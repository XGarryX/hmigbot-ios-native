"""Conservative Package relevance for replayed, declared Xcode product membership.

This is neither manifest execution nor an effective-build/dependency graph.
"""
from pathlib import Path, PurePosixPath
import re

from .core import MigrationError, digest, json_bytes
from .swiftui import tokenize

SDK_IMPORTS = frozenset("Swift SwiftData Observation PhotosUI Charts Foundation SwiftUI UIKit Combine WidgetKit AppIntents ActivityKit AVFoundation CoreMedia CoreImage CoreGraphics Vision VisionKit UserNotifications UniformTypeIdentifiers OSLog os Darwin".split())
BOOL_SETTINGS = frozenset("GENERATE_INFOPLIST_FILE APPLICATION_EXTENSION_API_ONLY SKIP_INSTALL CLANG_ENABLE_MODULES CLANG_ENABLE_OBJC_ARC ENABLE_USER_SCRIPT_SANDBOXING ENABLE_TESTABILITY SUPPORTS_MACCATALYST SWIFT_EMIT_LOC_STRINGS".split())
METADATA_SETTINGS = frozenset("PRODUCT_NAME PRODUCT_BUNDLE_IDENTIFIER CODE_SIGN_STYLE DEVELOPMENT_TEAM ASSETCATALOG_COMPILER_APPICON_NAME ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME MARKETING_VERSION CURRENT_PROJECT_VERSION TARGETED_DEVICE_FAMILY".split())
PATH_SETTINGS = {'INFOPLIST_FILE', 'CODE_SIGN_ENTITLEMENTS'}
FIXED_SETTINGS = {
    'SDKROOT': {'iphoneos', 'iphonesimulator'},
    'SUPPORTED_PLATFORMS': {'iphoneos iphonesimulator', 'iphoneos', 'iphonesimulator'},
    'SWIFT_VERSION': {'5.0', '5', '6.0', '6'},
    'SWIFT_OPTIMIZATION_LEVEL': {'-Onone', '-O', '-Osize'},
    'DEBUG_INFORMATION_FORMAT': {'dwarf', 'dwarf-with-dsym'},
}


def require(ok, message):
    if not ok: raise MigrationError(message)


class Proof:
    def __init__(self, source, project_directory):
        self.source=Path(source).resolve(); self.project_directory=project_directory
        self.files={}; self.edges=[]; self.settings=[]; self.pending=[]

    def path(self, base, spelling):
        require(isinstance(spelling,str) and spelling and not any(c in spelling for c in ('$', '\\', ':')),
                'unknown or macro configuration path')
        require(not Path(spelling).is_absolute() and not PurePosixPath(spelling).is_absolute(), 'absolute configuration path')
        actual=(base/spelling).resolve()
        require(actual.is_relative_to(self.source), 'configuration include/path escapes source or external symlink')
        return actual

    def evidence(self, actual, required):
        relative=actual.relative_to(self.source).as_posix()
        require(not actual.exists() or actual.is_file(), 'configuration path is not a regular file')
        exists=actual.is_file()
        require(exists or not required, 'required configuration file missing: '+relative)
        value={'path':relative,'exists':exists,'sha256':digest(actual.read_bytes()) if exists else None}
        self.files[relative]=value
        return value

    def setting(self, key, value, origin):
        self.pending.append((key,value,origin))

    def finish(self):
        # Custom scalar variables are accepted only through actual metadata
        # references. No project-name whitelist, and no unknown compiler flags
        # or search paths are promoted to harmless metadata.
        definitions={}
        for key,value,_ in self.pending:
            if isinstance(value,str): definitions.setdefault(key,[]).append(value)
        metadata=set(); pending=[value for key,value,_ in self.pending if key in METADATA_SETTINGS and isinstance(value,str)]
        while pending:
            for name in re.findall(r'\$\(([^)]+)\)',pending.pop()):
                if name in {'TARGET_NAME','inherited'} or name in metadata: continue
                require(re.fullmatch(r'[A-Z][A-Z0-9_]*',name) is not None and name in definitions,
                        'undefined metadata variable: '+name)
                require(not re.search(r'(?:FLAGS|SEARCH_PATHS|HEADER|MODULE|SDK|TOOLCHAIN|SWIFT|CLANG|GCC)',name),
                        'compiler/dependency variable is not scalar metadata: '+name)
                metadata.add(name); pending.extend(definitions[name])
        for key,value,origin in self.pending:
            self._check_setting(key,value,origin,metadata)

    def _check_setting(self, key, value, origin, metadata):
        require(isinstance(key,str) and re.fullmatch(r'[A-Z][A-Z0-9_]*',key), 'conditional/unknown configuration key')
        require(isinstance(value,str), 'non-string configuration value: '+key)
        require(not any(c in value for c in ('\n','\r','\\',';')) and '//' not in value, 'unsupported configuration value: '+key)
        macros=re.findall(r'\$\(([^)]+)\)',value)
        require(set(macros)<={'TARGET_NAME','inherited'}|metadata, 'unknown metadata macro: '+key)
        require('$' not in re.sub(r'\$\([^)]+\)','',value), 'unsupported metadata expansion: '+key)
        if key in BOOL_SETTINGS: require(value in {'YES','NO'}, 'unknown boolean setting: '+key)
        elif key in PATH_SETTINGS:
            actual=self.path(self.project_directory,value); self.evidence(actual,True)
        elif key in FIXED_SETTINGS: require(value in FIXED_SETTINGS[key], 'unsupported setting value: '+key)
        elif key=='IPHONEOS_DEPLOYMENT_TARGET':
            require(re.fullmatch(r'\d+(?:\.\d+)*',value) is not None, 'unknown deployment version')
        elif key=='SWIFT_ACTIVE_COMPILATION_CONDITIONS':
            require(re.fullmatch(r'[A-Za-z0-9_ ]*',value) is not None, 'unknown compilation condition syntax')
        elif key=='LD_RUNPATH_SEARCH_PATHS':
            parts=value.split()
            require(parts and set(parts)<={'$(inherited)','@executable_path/Frameworks','@executable_path/../../Frameworks'}, 'unknown runpath bridge')
        elif key in METADATA_SETTINGS or key in metadata:
            require(bool(value) and re.fullmatch(r'[A-Za-z0-9_.$(), -]+',value) is not None, 'unsupported metadata value: '+key)
        else: raise MigrationError('unknown/dependency-affecting configuration setting: '+key)
        self.settings.append({'origin':origin,'key':key,'value':value})

    def config(self, actual, stack=()):
        relative=actual.relative_to(self.source).as_posix()
        require(relative not in stack,'configuration include cycle')
        self.evidence(actual,True)
        for line_number,line in enumerate(actual.read_text(encoding='utf-8-sig').splitlines(),1):
            line=line.strip()
            if not line or line.startswith('//'): continue
            require(not line.endswith('\\'), 'configuration continuation unsupported')
            if line.startswith('#'):
                match=re.fullmatch(r'#include(\?)?\s+"([^"\n]+)"(?:\s*//.*)?',line)
                require(match is not None,'unknown/conditional configuration directive')
                included=self.path(actual.parent,match[2]); required=not bool(match[1])
                state=self.evidence(included,required)
                self.edges.append({'from':relative,'line':line_number,'to':state['path'],'required':required,**state})
                if state['exists']: self.config(included,stack+(relative,))
            else:
                key,separator,value=line.partition('=')
                require(bool(separator),'unknown configuration statement')
                self.setting(key.strip(),value.strip(),relative+':'+str(line_number))


def classify(source, snap, variant, context, *, swift_syntax=None):
    """Only a context produced by project_scope.resolve can establish this proof."""
    manifests=[{'path':f['path'],'sha256':f['sha256']} for f in snap['files'] if Path(f['path']).name=='Package.swift']
    proof=Proof(source,context.path.parent.parent); imports=[]; error=None
    try:
        require(context.project.get('packageReferences',[])==[], 'project package references remain unresolved')
        require(context.project.get('projectReferences',[])==[], 'external project references remain unresolved')
        for key in sorted(context.selected_closure):
            target=context.targets[key]
            for phase_id,phase in context.phases(target):
                for bid,item in context.build_files(phase,phase_id):
                    ref=item.get('fileRef')
                    settings=item.get('settings',{})
                    require(isinstance(settings,dict) and set(settings)<={'ATTRIBUTES'}, 'per-file compiler/dependency settings remain unresolved: '+bid)
                    attributes=settings.get('ATTRIBUTES',[])
                    require(isinstance(attributes,list) and set(attributes)<={'CodeSignOnCopy','RemoveHeadersOnCopy'}, 'unknown per-file attributes: '+bid)
                    if phase.get('isa') in {'PBXFrameworksBuildPhase','PBXCopyFilesBuildPhase','PBXHeadersBuildPhase'}:
                        require(ref in context.products,'external framework/copy/header bridge: '+bid)
        for config in context.selected_configs:
            if config['base_path']: proof.config(proof.path(proof.source,config['base_path']))
            for key,value in config['settings'].items(): proof.setting(key,value,config['owner']+':'+config['name'])
        proof.finish()
        require(not any(Path(f['path']).suffix.lower() in {'.h','.modulemap'} for f in snap['files']), 'implicit headers/module maps remain unresolved')
        for relative in variant['source_files']:
            require(Path(relative).suffix=='.swift','non-Swift dependency/include bridges remain unresolved')
            from .swift_native import source_tokens
            parsed=source_tokens(proof.source, relative, swift_syntax)
            for at,token in enumerate(parsed):
                if token.kind=='string' or token.value!='import': continue
                following=at+1
                if following<len(parsed) and parsed[following].value in {'struct','class','enum','protocol','func','var','let','typealias'}: following+=1
                require(following<len(parsed),'unsupported import syntax')
                module=parsed[following].value
                require(module in SDK_IMPORTS,'unknown/non-SDK source import: '+relative+':'+module)
                imports.append({'path':relative,'line':token.line,'module':module,'resolution':'known_sdk_import_name_only'})
    except (MigrationError, OSError, UnicodeError, ValueError) as exc:
        error=str(exc)
    basis={'source_sha256':snap['sha256'],'project_path':variant['project_path'],'project_sha256':variant['project_sha256'],
           'variant_sha256':digest(json_bytes(variant)), 'target_closure':variant['target_closure'],
           'membership_sha256':digest(json_bytes(variant['source_membership'])),
           'selected_configurations':context.selected_configs,'configuration_files':sorted(proof.files.values(),key=lambda x:x['path']),
           'include_edges':proof.edges,'checked_settings':proof.settings,'imports':imports,'manifests':manifests}
    return {'schema_version':1,'policy':'declared-project-targets-package-relevance-v1',
            'scope':'project-targets','complete_graph':False,'effective_build':'unresolved',
            'basis':basis,'basis_sha256':digest(json_bytes(basis)),
            'manifests':[{**m,'status':'unresolved' if error else 'independent_of_declared_product',
                          'blocking':bool(error),'reason':error or 'No declared package product, script, external product, dependency configuration or unknown source import bridge in supported product closure'} for m in manifests],
            'limitations':['not_manifest_execution','dependency_resolution_not_verified','headers_implicit_includes_unresolved','conditional_build_settings_not_evaluated']}


def issue_dispositions(graph):
    """Consume only after validate_graph has replayed and compared the full graph."""
    scope=graph.get('dependency_scope',{})
    classifications={m['path']:m for m in scope.get('manifests',[])} if graph.get('variant',{}).get('scope')=='project-targets' else {}
    result=[]
    for issue in graph['issues']:
        claim=classifications.get(issue.get('path')) if issue.get('code')=='executable_manifest_not_evaluated' else None
        independent=bool(claim and claim.get('status')=='independent_of_declared_product' and claim.get('blocking') is False)
        result.append({'issue':issue,'blocking':not independent,
                       'scope_reason':claim['reason'] if claim else 'original extraction issue remains blocking',
                       'scope_basis_sha256':scope.get('basis_sha256') if claim else None})
    return result
