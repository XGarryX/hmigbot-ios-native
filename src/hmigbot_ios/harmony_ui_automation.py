"""Explicit-device HarmonyOS official emulator/Hypium UI validation adapter.

The official emulator CLI is preferred for an explicitly selected emulator when
it provides the requested UI operations. Hypium remains the test-HAP fallback.
Never selects a device, runs desktop automation,
uploads recordings, or accepts shell commands from recipes.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
import time
import uuid
import zipfile

from .core import MigrationError, digest, json_bytes, read_json, write_json, write_new_tree
from .cli_output import emit_json
from .ui_validation_evidence import build_identity, source_identity, identity, CONFIG_KEYS

NAME = re.compile(r'[A-Za-z][A-Za-z0-9_.]*')
CHECKPOINT = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,100}')
DEVICE = re.compile(r'[A-Za-z0-9_.:-]{1,200}')
MARKER = 'HMIGBOT_UI_V1 '


def _require(condition, message):
    if not condition:
        raise MigrationError(message)


def _path(project, value):
    path = Path(value)
    return (path if path.is_absolute() else project / path).resolve()


def _output(project, value, prefix):
    project = Path(project).resolve()
    path = _path(project, value)
    runtime = Path(__file__).resolve().parents[2]
    _require(project.is_dir() and project not in {Path('/'),Path.home(),runtime}
             and not project.is_relative_to(runtime), 'Choose the explicit HarmonyOS application project')
    _require((project/'oh-package.json5').is_file(), 'Selected target must expose its HarmonyOS oh-package.json5')
    _require(path.is_relative_to(project / 'spec') and not path.is_relative_to(runtime),
             'UI preparation/evidence belongs inside the selected target project spec directory')
    _require(not path.exists(), 'Use a new ' + prefix + ' output directory; existing evidence is retained')
    return path


def _hap_metadata(path, bundle, module=None):
    _require(path.is_file() and path.suffix=='.hap', 'An explicitly built HAP is required')
    with zipfile.ZipFile(path) as archive:
        names=[name for name in archive.namelist() if name=='module.json']
        _require(len(names)==1, 'HAP must expose exactly one root module.json for scoped installation')
        import json
        data=json.loads(archive.read(names[0]))
    _require(data.get('app',{}).get('bundleName')==bundle, 'HAP bundle identity differs from selected application')
    if module is not None:
        _require(data.get('module',{}).get('name')==module, 'Test HAP module differs from selected test module')
    return data


def _request(project, request):
    _require(isinstance(request,dict), 'Harmony UI request must be an object')
    for key in ('bundle_id','ability_name'):
        _require(isinstance(request.get(key),str) and NAME.fullmatch(request[key]), 'Explicit identifier required: '+key)
    device=request.get('device',{})
    _require(isinstance(device,dict) and isinstance(device.get('id'),str) and DEVICE.fullmatch(device['id'])
             and device.get('kind') in {'emulator','physical'}, 'Explicit device id and emulator/physical kind are required')
    backend=request.get('backend','auto')
    _require(backend in {'auto','emulator','hypium'},'Unknown Harmony UI backend')
    emulator=request.get('emulator')
    launcher=Path('/Applications/DevEco-Studio.app/Contents/tools/emulator/Emulator')
    selected=('emulator' if device['kind']=='emulator' and launcher.is_file() else 'hypium') if backend=='auto' else backend
    if selected=='emulator':
        _require(device['kind']=='emulator' and isinstance(emulator,dict),'Official emulator route needs explicit emulator instance metadata')
        _require(all(isinstance(emulator.get(k),str) and emulator[k] for k in ('name','uuid')),
                 'Official emulator route needs exact instance name and uuid')
    else:
        for key in ('test_module','test_runner'):
            _require(isinstance(request.get(key),str) and NAME.fullmatch(request[key]),'Explicit identifier required: '+key)
    observations_only=request.get('observations_only',False)
    _require(type(observations_only)is bool,'observations_only must be explicitly boolean')
    configuration=request.get('configuration') or {}
    _require(isinstance(configuration,dict),'UI configuration must be an object')
    if observations_only:
        _require(all(configuration.get(k) is None or isinstance(configuration[k],str) for k in CONFIG_KEYS),
                 'Observed/requested UI configuration fields must be strings or unknown')
        configuration={k:configuration.get(k) or 'unknown' for k in CONFIG_KEYS}
    else:
        _require(all(isinstance(configuration.get(k),str) and configuration[k] and configuration[k]!='unknown' for k in CONFIG_KEYS),
                 'Explicit UI configuration is required for strict verification; observations_only permits honest unknowns')
    recipe_path=_path(project,request['business_recipe'])
    recipe=read_json(recipe_path)
    _require(isinstance(recipe,dict) and isinstance(recipe.get('id'),str) and recipe['id'], 'Business recipe id is required')
    checkpoints=recipe.get('checkpoints')
    _require(isinstance(checkpoints,list) and checkpoints and all(isinstance(c,str) and CHECKPOINT.fullmatch(c) for c in checkpoints)
             and len(set(checkpoints))==len(checkpoints), 'Business recipe needs unique checkpoint ids')
    steps=request.get('steps')
    _require(isinstance(steps,list) and steps, 'Explicit fixed test steps are required')
    observed=[]
    for step in steps:
        _require(isinstance(step,dict) and not(set(step)-{'action','identifier','text','checkpoint_id','timeout_ms',
            'widget_id','expected_label','expected_type'}), 'Unknown fixed-scenario fields')
        action=step.get('action')
        _require(action in {'wait','tap','input','assert_exists','assert_text','back','checkpoint'}, 'Unsupported fixed test action')
        if observations_only:
            _require(action in {'wait','assert_exists','assert_text','checkpoint'},'Pure observations_only does not authorize control mutation or navigation')
        if action=='checkpoint':
            _require(step.get('checkpoint_id') in checkpoints, 'Checkpoint is absent from shared business recipe')
            observed.append(step['checkpoint_id'])
        elif action!='back' or selected=='emulator':
            stable=isinstance(step.get('identifier'),str) and bool(step['identifier'])
            mapped=(selected=='emulator' and isinstance(step.get('widget_id'),(str,int))
                    and str(step['widget_id']).isdigit() and isinstance(step.get('expected_label'),str))
            _require(stable or mapped, 'Stable control id or current widget id with expected_label is required')
        if selected=='hypium':
            _require(not(set(step)&{'widget_id','expected_label','expected_type'}),'Widget-id selectors belong to the emulator backend')
        if 'text' in step:
            _require(isinstance(step['text'],str), 'Test text must be a string')
        if 'timeout_ms' in step:
            _require(type(step['timeout_ms']) is int and 1<=step['timeout_ms']<=30000, 'Per-step timeout must be 1..30000ms')
    _require(observed==checkpoints, 'Fixed steps must visit every recipe checkpoint exactly once in recipe order')
    hap=_path(project,request['hap'])
    _hap_metadata(hap,request['bundle_id'])
    fields=('bundle_id','ability_name','device','steps')
    binding={key:request[key] for key in fields}
    binding['configuration']=configuration
    binding['observations_only']=observations_only
    binding['backend']=selected
    if selected=='hypium':
        binding.update({key:request[key] for key in ('test_module','test_runner')})
    else:
        binding['emulator']=emulator
    binding['scenario']={'id':recipe['id'],'sha256':digest(json_bytes(recipe))}
    binding['hap']=str(hap)
    binding['build_sha256']=build_identity(hap)
    binding['business_recipe']=str(recipe_path)
    return binding


def prepare(project, request, output):
    project=Path(project).resolve()
    binding=_request(project,request)
    output=_output(project,output,'preparation')
    if binding['backend']=='emulator':
        record={'schema_version':1,'status':'emulator_scope_prepared','binding':binding,
            'binding_sha256':digest(json_bytes(binding)),'device_invoked':False,'capture_invoked':False,
            'backend_reason':'Official emulator screenshot/layout/widget operations; no test HAP required'}
        write_new_tree(output,{'prepared.json':json_bytes(record)})
        return {**record,'prepared':str(output/'prepared.json')}
    template=Path(__file__).resolve().parents[2]/'providers/ui-testing/harmony/HMigbotScenario.test.ets'
    recipe={key:binding[key] for key in ('bundle_id','ability_name','configuration','steps','observations_only')}
    recipe['binding_sha256']=digest(json_bytes(binding))
    script=template.read_text().replace('__HMIGBOT_REQUEST__',json_bytes(recipe).decode().strip())
    record={'schema_version':1,'status':'prepared_test_source_not_built','binding':binding,
            'binding_sha256':recipe['binding_sha256'],'generated_test_sha256':digest(script.encode()),
            'required_registration':'Import and call hmigbotUiValidationTest in the selected ohosTest List.test.ets, then build its test HAP.',
            'device_invoked':False,'capture_invoked':False}
    write_new_tree(output,{'HMigbotScenario.test.ets':script.encode(),'prepared.json':json_bytes(record)})
    return {**record,'prepared':str(output/'prepared.json'),'test_source':str(output/'HMigbotScenario.test.ets')}


def _call(command, output, name, timeout):
    started=time.monotonic()
    stdout,stderr=output/(name+'.stdout.log'),output/(name+'.stderr.log')
    timed_out=False
    try:
        with stdout.open('wb') as out,stderr.open('wb') as err:
            result=subprocess.run(command,stdout=out,stderr=err,timeout=timeout,shell=False)
        code=result.returncode
    except subprocess.TimeoutExpired:
        timed_out=True;code=None
    except OSError as exc:
        code=None
        stderr.write_text(str(exc),encoding='utf-8')
    return {'argv':[str(x) for x in command],'actual_call_now':True,'exit_code':code,'timed_out':timed_out,
            'elapsed_seconds':time.monotonic()-started,'stdout':stdout.name,'stderr':stderr.name}


def _native_lines(text):
    # The native HDC build may emit literal escaped newlines on macOS.
    return text.replace('\\r\\n','\n').replace('\\n','\n').replace('\r\n','\n')


def _installation_confirmed(text, hap):
    """Confirm the actual selected HAP, not only a zero HDC process exit."""
    text=_native_lines(text)
    markers=re.findall(r'(?m)^\[Info\]App install path:(.+?) msg:install bundle successfully\.\s*$',text)
    return (len(markers)==1 and Path(markers[0]).is_absolute() and Path(markers[0]).resolve()==Path(hap).resolve()
            and re.search(r'(?m)^AppMod finish\s*$',text) is not None)


def _launch_confirmed(text, bundle, ability):
    text=_native_lines(text)
    return (re.findall(r'(?m)^BundleName:\s*(\S+)\s*$',text)==[bundle]
            and re.findall(r'(?m)^AbilityName:\s*(\S+)\s*$',text)==[ability]
            and re.search(r'(?m)^start ability successfully\.\s*$',text) is not None)


def _decode_events(raw, run_id, binding):
    import json
    groups={}
    for line in raw.splitlines():
        if MARKER not in line:
            continue
        event=json.loads(line.split(MARKER,1)[1])
        _require(event.get('run_id')==run_id and event.get('binding_sha256')==binding,
                 'Test HAP protocol output belongs to another run or prepared scenario')
        kind,name=event.get('kind'),event.get('name')
        _require(kind in {'artifact','configuration','checkpoint','complete','error'} and isinstance(name,str), 'Unknown test output event')
        _require(type(event.get('parts')) is int and 1<=event['parts']<=10000
                 and type(event.get('sequence')) is int and 0<=event['sequence']<event['parts'], 'Malformed output chunk numbering')
        key=(kind,name)
        group=groups.setdefault(key,{'parts':event['parts'],'chunks':{}})
        _require(group['parts']==event['parts'] and event['sequence'] not in group['chunks'], 'Duplicate or conflicting output chunk')
        _require(isinstance(event.get('data'),str) and len(event['data'])<=6000, 'Oversized test output chunk')
        group['chunks'][event['sequence']]=event['data']
    decoded={}
    for key,group in groups.items():
        _require(len(group['chunks'])==group['parts'], 'Incomplete test output artifact')
        value=base64.b64decode(''.join(group['chunks'][i] for i in range(group['parts'])),validate=True)
        _require(len(value)<=25*1024*1024,'Test output artifact exceeds byte budget')
        decoded[key]=value
    return decoded


def run(project, prepared, test_hap, output, *, install=False, hdc=None, emulator=None, timeout=180):
    import json
    project=Path(project).resolve()
    prepared=Path(prepared).resolve()
    record=read_json(prepared)
    _require(record.get('schema_version')==1 and isinstance(record.get('binding'),dict), 'Unsupported prepared UI request')
    binding=record['binding']
    _require(record.get('binding_sha256')==digest(json_bytes(binding)), 'Prepared UI binding changed')
    input_keys=('bundle_id','ability_name','test_module','test_runner','device','configuration','steps','hap','business_recipe','backend','emulator','observations_only')
    checked=_request(project,{key:binding[key] for key in input_keys if key in binding})
    _require(checked==binding, 'Prepared UI request no longer matches its current typed inputs')
    if binding['backend']=='emulator':
        from .harmony_emulator import run_emulator
        return run_emulator(project,record,output,install=install,hdc=hdc,emulator=emulator,timeout=timeout)
    script=prepared.parent/'HMigbotScenario.test.ets'
    _require(script.is_file() and digest(script.read_bytes())==record['generated_test_sha256'], 'Generated Hypium test source changed')
    _require(install,'Run requires explicit --install so current app/test HAP bytes are bound to this selected device')
    _require(type(timeout)is int and 1<=timeout<=1800,'UI timeout must be 1..1800 seconds')
    hap=Path(binding['hap'])
    _require(build_identity(hap)==binding['build_sha256'],'Selected app HAP changed; prepare against current build')
    _require(digest(json_bytes(read_json(Path(binding['business_recipe']))))==binding['scenario']['sha256'],'Business recipe changed')
    _hap_metadata(hap,binding['bundle_id'])
    _require(test_hap is not None,'Hypium fallback needs the explicit registered test HAP')
    test_hap=Path(test_hap).resolve()
    _hap_metadata(test_hap,binding['bundle_id'],binding['test_module'])
    hdc=Path(hdc).resolve() if hdc else Path('/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains/hdc')
    _require(hdc.is_file(),'Select the installed official hdc executable')
    output=_output(project,output,'capture')
    output.mkdir(parents=True)
    run_id='HU-'+uuid.uuid4().hex
    before_source=source_identity('harmonyos',project)
    calls=[]
    device=binding['device']
    for name,file in (('install-app',hap),('install-test',test_hap)):
        call=_call([str(hdc),'-t',device['id'],'install','-r',str(file)],output,name,min(timeout,180))
        calls.append(call)
        if call['exit_code']!=0:
            result={'status':'installation_failed','calls':calls,'device':device,'behavior_verified':False}
            write_json(output/'run.json',result)
            return result
        if not _installation_confirmed((output/call['stdout']).read_text(encoding='utf-8',errors='replace'),file):
            result={'status':'installation_unconfirmed','calls':calls,'device':device,'behavior_verified':False,
                'capture_invoked':False,'product_failure':False,'installation_step':name,
                'recovery':'The official install output did not confirm these selected HAP bytes; preserve raw output and resolve installation before running UI tests'}
            write_json(output/'run.json',result)
            return result
    call=_call([str(hdc),'-t',device['id'],'shell','aa','test','-b',binding['bundle_id'],
                '-m',binding['test_module'],'-s','unittest',binding['test_runner'],
                '-s','class','HMigbotUiValidation','-s','hmigbot_run',run_id,
                '-s','hmigbot_binding',record['binding_sha256'],'-s','timeout',str(timeout*1000)],output,'aa-test',timeout)
    call['kind']='app_ui_test';calls.append(call)
    events=_decode_events((output/call['stdout']).read_text(encoding='utf-8',errors='replace'),run_id,record['binding_sha256'])
    checkpoints=[]
    expected=[step['checkpoint_id'] for step in binding['steps'] if step['action']=='checkpoint']
    allowed={'shots/'+key+'.png' for key in expected}|{'hierarchy/'+key+'.json' for key in expected}
    for (kind,name),body in events.items():
        if kind=='artifact':
            _require(name in allowed,'Test output names an artifact outside selected checkpoints')
            path=output/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    for key in expected:
        checkpoint={'id':key,'status':'not_run'}
        body=events.get(('checkpoint',key))
        if body is not None:
            checkpoint=json.loads(body)
            _require(checkpoint.get('id')==key and checkpoint.get('status')=='passed'
                     and checkpoint.get('window_bundle_id')==binding['bundle_id'], 'Checkpoint app identity mismatch')
            for field,name in (('screenshot','shots/'+key+'.png'),('hierarchy','hierarchy/'+key+'.json')):
                path=output/name
                _require(path.is_file(),'Checkpoint output artifact is missing')
                checkpoint[field]={'path':name,'sha256':digest(path.read_bytes())}
        checkpoints.append(checkpoint)
    complete=json.loads(events.get(('complete','complete.json'),b'{}'))
    source_unchanged=source_identity('harmonyos',project)==before_source
    passed=(call['exit_code']==0 and complete.get('status')=='passed' and complete.get('checkpoints')==expected
            and source_unchanged and all(c['status']=='passed' for c in checkpoints))
    observed=json.loads(events.get(('configuration','configuration.json'),b'{}'))
    observed_actual=observed==binding['configuration'] and all(observed.get(k) not in {'unknown',None,''} for k in CONFIG_KEYS)
    current_receipt={'schema_version':'hmigbot-ui-current/1','platform':'harmonyos','bundle_id':binding['bundle_id'],
        'device':device,'build_sha256':binding['build_sha256'],'observed_configuration':observed,
        'observations_actual':observed_actual,'observed_at':datetime.now(timezone.utc).isoformat(),
        'calls':calls,'scope':'configuration read from selected current top UIAbility context; not request echo'}
    write_json(output/'current-configuration.json',current_receipt)
    manifest={'schema_version':'hmigbot-ui-evidence/1','platform':'harmonyos','run_id':run_id,
        'bundle_id':binding['bundle_id'],'device':device,'build':{'sha256':binding['build_sha256']},
        'test_hap_sha256':build_identity(test_hap),'source_sha256':before_source,'scenario':binding['scenario'],
        'configuration':binding['configuration'],'captured_at':datetime.now(timezone.utc).isoformat(),
        'checkpoints':checkpoints,'capture_scope':'device_region_bound_to_active_app_window',
        'actual_calls':calls,'status':'passed' if passed else 'failed','behavior_verified':False,
        'configuration_observed':observed_actual,'source_unchanged':source_unchanged}
    if ('error','error.json') in events:
        manifest['test_error']=json.loads(events[('error','error.json')])
    manifest['artifacts']={p.relative_to(output).as_posix():digest(p.read_bytes()) for p in output.rglob('*') if p.is_file()}
    write_json(output/'manifest.json',manifest)
    current=identity(manifest)
    current['verification']={'build_path':str(hap),'source_root':str(project),
        'configuration_receipt':{'path':str(output/'current-configuration.json'),
                                 'sha256':manifest['artifacts']['current-configuration.json']}}
    write_json(output/'current.json',current)
    result={'status':'passed' if passed else 'failed','manifest':str(output/'manifest.json'),
            'current':str(output/'current.json'),'calls':calls,'behavior_verified':False,
            'capture_scope':manifest['capture_scope'],'source_unchanged':source_unchanged}
    write_json(output/'run.json',result)
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    preflight=commands.add_parser('preflight',help='Read HAP API requirement and exact emulator metadata; never starts a device')
    preflight.add_argument('--hap',type=Path,required=True)
    preflight.add_argument('--bundle-id',required=True)
    preflight.add_argument('--emulator-name',required=True)
    preflight.add_argument('--emulator-uuid',required=True)
    preflight.add_argument('--emulator',type=Path)
    preflight.add_argument('--output',type=Path)
    prepare_cmd=commands.add_parser('prepare')
    prepare_cmd.add_argument('--request',type=Path,required=True)
    run_cmd=commands.add_parser('run')
    run_cmd.add_argument('--prepared',type=Path,required=True)
    run_cmd.add_argument('--test-hap',type=Path,help='Required only by the Hypium fallback')
    run_cmd.add_argument('--install',action='store_true')
    run_cmd.add_argument('--hdc',type=Path)
    run_cmd.add_argument('--emulator',type=Path,help='Selected installed official emulator launcher')
    run_cmd.add_argument('--timeout',type=int,default=180)
    for command in (prepare_cmd,run_cmd):
        command.add_argument('--project',type=Path,required=True)
        command.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    from .project_progress import ProjectProgress
    from argparse import Namespace
    progress=ProjectProgress(Namespace(command='ui-harmony-run' if args.command=='run' else 'ui-harmony-prepare',project=getattr(args,'project',None)))
    progress.record('running')
    try:
        if args.command=='preflight':
            from .harmony_emulator import inspect_emulator
            result=inspect_emulator(args.hap,args.bundle_id,args.emulator_name,args.emulator_uuid,emulator=args.emulator)
            if args.output:
                runtime=Path(__file__).resolve().parents[2]
                _require(not args.output.resolve().is_relative_to(runtime),'Preflight output must be outside the tool runtime')
                write_json(args.output,result)
        elif args.command=='prepare':
            result=prepare(args.project,read_json(args.request),args.output)
        else:
            result=run(args.project,args.prepared,args.test_hap,args.output,install=args.install,hdc=args.hdc,emulator=args.emulator,timeout=args.timeout)
        code=0 if args.command=='preflight' or result['status'] in {'prepared_test_source_not_built','emulator_scope_prepared','passed'} else 3
        progress.record(result['status'],result,exit_code=code)
        emit_json(result)
        return code
    except (MigrationError,OSError,ValueError,TypeError,KeyError,zipfile.BadZipFile) as exc:
        result={'status':'error','error':str(exc),'behavior_verified':False}
        progress.record('error',result,exit_code=2)
        emit_json(result)
        return 2
