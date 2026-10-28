"""Inspect Xcode Simulator products through Apple's lipo/otool/codesign.

Simulator entitlements can be linked in __TEXT,__entitlements even when
codesign reports an empty dictionary. This is build evidence, not runtime or
physical-device capability acceptance.
"""
import json
from pathlib import Path
import plistlib
import re
import subprocess
import tempfile

from hmigbot_ios.core import MigrationError, digest

SIGNING = ['CODE_SIGNING_ALLOWED=YES','CODE_SIGNING_REQUIRED=YES','CODE_SIGN_IDENTITY=-']
SIGNING_KEYS = ('CODE_SIGN_STYLE','DEVELOPMENT_TEAM','PROVISIONING_PROFILE_SPECIFIER',
                'PROVISIONING_PROFILE','CODE_SIGN_ENTITLEMENTS','CODE_SIGN_IDENTITY',
                'CODE_SIGNING_ALLOWED','CODE_SIGNING_REQUIRED')
GROUPS = 'com.apple.security.application-groups'


def _run(argv, env, log):
    value=subprocess.run(list(map(str,argv)),env=env,capture_output=True,timeout=180)
    log.append({'argv':list(map(str,argv)),'exit_code':value.returncode,
                'stdout':value.stdout.decode(errors='replace'),'stderr':value.stderr.decode(errors='replace')})
    if value.returncode:raise MigrationError('Simulator product inspection failed: '+str(argv[0])+': '+value.stderr.decode(errors='replace').strip())
    return value


def linked(binary, env):
    """Use official section offsets; never reimplement Mach-O load commands."""
    binary=Path(binary).resolve();commands=[]
    architectures=_run(['/usr/bin/lipo','-archs',binary],env,commands).stdout.decode().split()
    description=_run(['/usr/bin/lipo','-info',binary],env,commands).stdout.decode()
    fat=description.startswith('Architectures in the fat file:')
    if not fat and not description.startswith('Non-fat file:'):
        raise MigrationError('Apple lipo returned an unknown product architecture description')
    observations=[]
    with tempfile.TemporaryDirectory(prefix='hmigbot-simulator-sections-') as temp:
        for arch in architectures:
            image=binary
            if fat:
                image=Path(temp)/arch
                _run(['/usr/bin/lipo',binary,'-thin',arch,'-output',image],env,commands)
            result=_run(['/usr/bin/otool','-l',image],env,commands)
            sections=[]
            for block in re.split(r'(?m)^\s*Section\s*$',result.stdout.decode())[1:]:
                fields={}
                for line in block.splitlines():
                    match=re.fullmatch(r'\s*(sectname|segname|size|offset)\s+(\S+)\s*',line)
                    if match:fields.setdefault(*match.groups())
                if fields.get('sectname')!='__entitlements' or fields.get('segname')!='__TEXT':continue
                offset,size=int(fields['offset'],0),int(fields['size'],0)
                with image.open('rb') as stream:
                    if offset<0 or size<0 or offset+size>image.stat().st_size:
                        raise MigrationError('Apple-reported entitlement section exceeds the product')
                    stream.seek(offset);raw=stream.read(size).rstrip(b'\0')
                value=plistlib.loads(raw)
                if not isinstance(value,dict):raise MigrationError('Simulator entitlement section is not a dictionary')
                sections.append({'segment':'__TEXT','section':'__entitlements','offset_in_slice':offset,
                                 'bytes':len(raw),'sha256':digest(raw),'plist':value})
            observations.append({'architecture':arch,'sections':sections})
    return {'binary':str(binary),'binary_sha256':digest(binary.read_bytes()),'architectures':observations,
            'commands':commands,'note':'Temporary lipo slices are deleted; original product remains unchanged'}


def collect(source, project, app, output, settings, env):
    """Keep declaration, Xcode-generated and linked evidence separate."""
    from hmigbot_ios.xcode import OpenStep
    objects=OpenStep((project/'project.pbxproj').read_text(encoding='utf-8-sig')).parse()['objects']
    products={}
    for value in objects.values():
        ref=objects.get(value.get('productReference'),{})
        if value.get('isa')=='PBXNativeTarget' and ref.get('path'):
            products.setdefault(Path(ref['path']).name,[]).append(value['name'])
    records=[];errors=[]
    for bundle in [app,*app.rglob('*.appex')]:
        info=plistlib.loads((bundle/'Info.plist').read_bytes());commands=[]
        rows=[r for r in settings if r.get('buildSettings',{}).get('PRODUCT_BUNDLE_IDENTIFIER')==info['CFBundleIdentifier']]
        if not rows and len(products.get(bundle.name,[]))==1:
            target=products[bundle.name][0]
            query=['/usr/bin/xcodebuild','-project',str(project),'-target',target,'-configuration','Release',
                   '-sdk','iphonesimulator','-showBuildSettings','-json',*SIGNING]
            rows=json.loads(_run(query,env,commands).stdout)
            rows=[r for r in rows if r.get('target')==target]
        row=rows[0] if len(rows)==1 else None
        values=row['buildSettings'] if row else {};target=row.get('target') if row else None
        declared=None;raw_declared=None;declared_path=None
        value=values.get('CODE_SIGN_ENTITLEMENTS')
        def expand(item):
            if isinstance(item,str):
                return re.sub(r'\$\(([^)]+)\)|\$\{([^}]+)\}',lambda m:str(values.get(m[1] or m[2],m[0])),item)
            if isinstance(item,list):return [expand(x) for x in item]
            if isinstance(item,dict):return {expand(k):expand(v) for k,v in item.items()}
            return item
        if value:
            declared_path=Path(expand(value))
            if not declared_path.is_absolute():declared_path=Path(values.get('PROJECT_DIR',source.root))/declared_path
            raw_declared=plistlib.loads(declared_path.read_bytes());declared=expand(raw_declared)
        generated=[]
        for path in sorted((output/'DerivedData/Build/Intermediates.noindex').rglob(bundle.name+'-Simulated.xcent')):
            if target and target+'.build' not in path.parts:continue
            generated.append({'path':str(path),'sha256':digest(path.read_bytes()),'plist':plistlib.loads(path.read_bytes())})
        binary=(bundle/info['CFBundleExecutable']).resolve()
        if not binary.is_relative_to(bundle.resolve()):raise MigrationError('Product executable escapes its bundle')
        evidence=linked(binary,env)
        expected=set(x for item in generated for x in item['plist'].get(GROUPS,[]))
        literal={x for x in (declared or {}).get(GROUPS,[]) if '$' not in x}
        expected.update(literal)
        if (raw_declared or {}).get(GROUPS) and not expected:
            errors.append({'product':str(bundle),'reason':'Declared AppGroup has no resolved generated entitlement'})
        for arch in evidence['architectures']:
            actual={x for section in arch['sections'] for x in section['plist'].get(GROUPS,[])}
            if not expected<=actual:errors.append({'product':str(bundle),'architecture':arch['architecture'],
                                                'missing_app_groups':sorted(expected-actual)})
        code=subprocess.run(['/usr/bin/codesign','-d','--entitlements','-',str(bundle)],env=env,capture_output=True,timeout=30)
        try:signed=plistlib.loads(code.stdout) if code.stdout else None
        except plistlib.InvalidFileException:signed=None
        records.append({'product':str(bundle),'target':target,'settings_status':'resolved' if row else 'unresolved_product_target',
            'effective_signing_settings':{k:values.get(k) for k in SIGNING_KEYS},'declaration_path':str(declared_path) if declared_path else None,
            'declaration_raw':raw_declared,'declaration_expanded_known_settings':declared,
            'generated_simulated_entitlements':generated,'linked':evidence,'settings_commands':commands,
            'codesign':{'argv':['/usr/bin/codesign','-d','--entitlements','-',str(bundle)],'exit_code':code.returncode,
                        'entitlements':signed,'stdout':code.stdout.decode(errors='replace'),'stderr':code.stderr.decode(errors='replace')},
            'expected_app_groups':sorted(expected)})
    return {'products':records,'errors':errors,'validation':'passed' if not errors else 'failed',
            'scope':'Simulator linked AppGroup inputs only; other capabilities and physical behavior unverified'}
