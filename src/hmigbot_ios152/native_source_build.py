"""Build the selected source app with Xcode for a separate source observer."""
from datetime import datetime, timezone
import json
from pathlib import Path
import plistlib
import subprocess

from hmigbot_ios.apple_tools import environment
from hmigbot_ios.core import MigrationError, snapshot, write_json, digest
from .simulator_entitlements import SIGNING


def app_build_identity(app_path):
    """Bind an observer's installation to the actual product and saved build.

    Explicitly supplied apps without this tool's build record remain usable for
    observer QA, with unrecorded provenance rather than an invented build PASS.
    """
    app=Path(app_path).resolve();info=plistlib.loads((app/'Info.plist').read_bytes())
    binary=(app/info['CFBundleExecutable']).resolve()
    if not binary.is_relative_to(app):raise MigrationError('Source executable escapes its app bundle')
    result={'app':str(app),'bundle_id':info['CFBundleIdentifier'],'app_binary_sha256':digest(binary.read_bytes()),
            'signing_mode':'unrecorded','build_record_binding':False}
    for parent in app.parents:
        path=parent/'build.json'
        if not path.is_file():continue
        try:record=json.loads(path.read_text())
        except (ValueError,UnicodeError):continue
        if record.get('app')!=str(app):continue
        result.update(build_record=str(path),build_record_sha256=digest(path.read_bytes()))
        if record.get('app_binary_sha256'):
            if record.get('exit_code')!=0 or record.get('simulator_entitlements',{}).get('validation')!='passed':
                raise MigrationError('Recorded source build failed validation; cannot bind observer to '+str(path))
            if record['app_binary_sha256']!=result['app_binary_sha256']:
                raise MigrationError('Source app differs from its recorded build; rebuild the source observer product')
            result.update(build_record_binding=True,signing_mode=record.get('signing_mode','unrecorded'),
                          source_sha256=record.get('source_sha256'))
        break
    return result


def build(source, output, *, project_path=None, scheme=None):
    output = Path(output).resolve()
    if output.exists() or output.is_relative_to(source.root) or source.root.is_relative_to(output):
        raise MigrationError('Source build requires a new output directory outside the source tree')
    selection = source.selection
    if not project_path:
        if not selection: raise MigrationError('Select an Xcode project for source observation')
        project_path = selection['project_path']
    project = (source.root/project_path).resolve()
    if project.name == 'project.pbxproj': project = project.parent
    if not project.is_relative_to(source.root) or project.suffix != '.xcodeproj' or not project.is_dir():
        raise MigrationError('Source build project is outside the selected source or is not an .xcodeproj')
    if not scheme and selection:
        from hmigbot_ios.project_scope import resolve
        _,graph = resolve(source.root,source.config['ios']['variant'],_context=True)
        candidates = [n for n in selection['targets'] if graph.targets[graph.names[n]].get('productType') == 'com.apple.product-type.application']
        if len(candidates) == 1: scheme = candidates[0]
    if not scheme: raise MigrationError('Select the application scheme; no unique selected app scheme is available')
    info,env = environment()
    output.mkdir(parents=True)
    before = snapshot(source.root)
    configuration = selection['configuration'] if selection else 'Release'
    if configuration != 'Release': raise MigrationError('Source observation must use the selected Release configuration')
    query=['/usr/bin/xcodebuild','-project',str(project),'-scheme',scheme,'-configuration',configuration,
           '-sdk','iphonesimulator','-showBuildSettings','-json',*SIGNING]
    settings=subprocess.run(query,cwd=source.root,env=env,capture_output=True,timeout=180)
    (output/'scheme-settings.stdout').write_bytes(settings.stdout)
    (output/'scheme-settings.stderr').write_bytes(settings.stderr)
    write_json(output/'scheme-settings.command.json',{'argv':query,'exit_code':settings.returncode,
                'stdout_sha256':digest(settings.stdout),'stderr_sha256':digest(settings.stderr)})
    if settings.returncode:raise MigrationError('Xcode source scheme settings query failed')
    queried=json.loads(settings.stdout)
    if selection:
        from hmigbot_ios.project_scope import resolve
        _,graph=resolve(source.root,source.config['ios']['variant'],_context=True)
        expected={n for n in selection['targets'] if graph.targets[graph.names[n]].get('productType') == 'com.apple.product-type.application'}
        observed={r['target'] for r in queried if r.get('buildSettings',{}).get('PRODUCT_TYPE') == 'com.apple.product-type.application'}
        if not observed or not observed<=expected:
            raise MigrationError('Source scheme application targets differ from selected source products: '+str(sorted(observed)))
    argv = ['/usr/bin/xcodebuild','-project',str(project),'-scheme',scheme,'-configuration',configuration,
            '-sdk','iphonesimulator','-destination','generic/platform=iOS Simulator',
            '-derivedDataPath',str(output/'DerivedData'),'-resultBundlePath',str(output/'SourceBuild.xcresult'),
            *SIGNING,'build']
    started = datetime.now(timezone.utc).isoformat()
    with (output/'build.stdout').open('w') as stdout,(output/'build.stderr').open('w') as stderr:
        result = subprocess.run(argv,cwd=source.root,env=env,stdout=stdout,stderr=stderr)
    record = {'argv':argv,'cwd':str(source.root),'started_at':started,
              'finished_at':datetime.now(timezone.utc).isoformat(),'exit_code':result.returncode,
              'configuration':configuration,'platform':'iphonesimulator','source_sha256':before['sha256'],
              'signing_mode':'simulator-adhoc','source_root':str(source.root),
              'toolchain':info,'source_behavior_verified':False,
              'scheme_targets':[r.get('target') for r in queried],
              'limitation':'Simulator observation does not establish physical-device or extension behavior'}
    write_json(output/'build.json',record)
    if result.returncode: raise MigrationError('Source Xcode build failed; see '+str(output/'build.stdout'))
    if snapshot(source.root)['sha256'] != before['sha256']:
        raise MigrationError('Source changed during source observer build')
    products = output/'DerivedData/Build/Products'/('Release-iphonesimulator')
    apps = []
    for path in products.glob('*.app'):
        plist = plistlib.loads((path/'Info.plist').read_bytes())
        if plist.get('CFBundlePackageType') == 'APPL':
            apps.append({'path':str(path),'bundle_id':plist.get('CFBundleIdentifier')})
    if len(apps) != 1:
        raise MigrationError('Expected one built application product; choose an unambiguous application scheme')
    record.update({'app':apps[0]['path'],'bundle_id':apps[0]['bundle_id']})
    # Official final products cross-check declaration evidence without guessing
    # source ownership from compiled names or rewriting approved source facts.
    app = Path(apps[0]['path'])
    observed = []
    for bundle in [app,*app.rglob('*.appex')]:
        info_path = bundle/'Info.plist'; final = plistlib.loads(info_path.read_bytes())
        metadata_keys = ('CFBundleIdentifier','CFBundleExecutable','CFBundleName','CFBundleVersion',
                         'CFBundleShortVersionString','CFBundleDevelopmentRegion','CFBundleLocalizations',
                         'MinimumOSVersion','UIApplicationSceneManifest','UIMainStoryboardFile','CFBundleURLTypes','NSExtension')
        resources = [str(p.relative_to(bundle)) for p in bundle.rglob('*')
                     if (p.is_dir() and p.suffix == '.storyboardc') or
                        (p.is_file() and p.suffix in {'.strings','.stringsdict','.nib','.car'})]
        observed.append({'product':str(bundle),'info_plist_sha256':digest(info_path.read_bytes()),
                         'metadata':{k:final[k] for k in metadata_keys if k in final},
                         'compiled_resources':sorted(resources)})
    from .native_resources import selected
    record['declared_resource_scope'] = selected(source)
    record['observed_products'] = observed
    from .simulator_entitlements import collect
    record['simulator_entitlements']=collect(source,project,app,output,queried,env)
    record['app_binary_sha256']=record['simulator_entitlements']['products'][0]['linked']['binary_sha256']
    record['resource_comparison'] = 'Declaration ownership and final product inventories retained separately; unresolved name/product correspondence is not auto-filled or attributed to target defects'
    write_json(output/'build.json',record)
    if snapshot(source.root)['sha256'] != before['sha256']:
        raise MigrationError('Source changed during final Simulator product inspection')
    if record['simulator_entitlements']['errors']:
        raise MigrationError('Simulator AppGroup declarations were not preserved in the final product; see '+str(output/'build.json'))
    return record
