"""Scoped official DevEco emulator UI operations without an added test HAP.

Only an explicitly selected, already-running instance is used. This adapter
does not start an emulator, operate the computer desktop, or accept shell code.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import subprocess
import time
import uuid

from .core import MigrationError, digest, json_bytes, read_json, write_json
from .ui_validation_evidence import build_identity, source_identity, identity, _png_dimensions
from .harmony_ui_automation import _require, _call, _output, _hap_metadata, _installation_confirmed, _launch_confirmed


def api_level(value):
    """Decode HAP API metadata using Hvigor sdk-util.apiTransform's suffix.

    The installed official encoder appends the API level padded to three digits
    after version components; old low API levels remain plain integers.
    """
    if type(value)is int and value>0:
        return value if value<1000 else value%1000 or None
    if isinstance(value,str) and value.isdigit():
        return api_level(int(value))
    return None


def emulator_compatibility(hap, bundle, instance):
    metadata=_hap_metadata(Path(hap).resolve(),bundle)
    app=metadata.get('app',{})
    minimum=api_level(app.get('minAPIVersion'))
    available=api_level(instance.get('os.apiVersion'))
    status=('needs_compatible_emulator' if minimum is not None and available is not None and available<minimum
            else 'compatible_api_level' if minimum is not None and available is not None else 'api_compatibility_unknown')
    return {'status':status,'hap_min_api_raw':app.get('minAPIVersion'),'hap_target_api_raw':app.get('targetAPIVersion'),
        'hap_min_api_level':minimum,'emulator_api_raw':instance.get('os.apiVersion'),'emulator_api_level':available,
        'emulator_name':instance.get('name'),'emulator_uuid':instance.get('uuid'),
        'scope':'API-level prerequisite only; actual installation still checks signing, ABI and platform constraints',
        'recovery':'Select or install an explicitly authorized emulator image at the required API or newer; do not lower the project SDK or rewrite product code'
                   if status=='needs_compatible_emulator' else None}


def inspect_emulator(hap,bundle,name,instance_uuid,*,emulator=None):
    """Read native HAP/instance metadata without starting or touching a device."""
    executable=Path(emulator).resolve() if emulator else Path('/Applications/DevEco-Studio.app/Contents/tools/emulator/Emulator')
    _require(executable.is_file(),'Official emulator launcher is unavailable')
    started=time.monotonic()
    try:
        completed=subprocess.run([str(executable),'-list','-details'],capture_output=True,timeout=30,shell=False)
    except (OSError,subprocess.TimeoutExpired) as exc:
        return {'status':'emulator_metadata_unavailable','error':str(exc),'actual_calls':[{
            'argv':[str(executable),'-list','-details'],'exit_code':None,'elapsed_seconds':time.monotonic()-started,
            'timed_out':isinstance(exc,subprocess.TimeoutExpired),'actual_call_now':True}],
            'device_invoked':False,'capture_invoked':False,'product_failure':False}
    stdout=completed.stdout.decode('utf-8',errors='replace');stderr=completed.stderr.decode('utf-8',errors='replace')
    call={'argv':[str(executable),'-list','-details'],'exit_code':completed.returncode,'elapsed_seconds':time.monotonic()-started,
          'stdout':stdout,'stderr':stderr,'actual_call_now':True,'scope':'read-only host emulator instance metadata'}
    if completed.returncode!=0:
        return {'status':'emulator_metadata_unavailable','error':stderr[:1000],'actual_calls':[call],
            'device_invoked':False,'capture_invoked':False,'product_failure':False}
    rows=json.loads(stdout)
    matches=[row for row in rows if row.get('name')==name and row.get('uuid')==instance_uuid]
    _require(len(matches)==1,'Exact selected emulator instance was not found')
    compatibility=emulator_compatibility(hap,bundle,matches[0])
    status=compatibility['status']
    if status=='compatible_api_level' and str(matches[0].get('isRunning')).lower()!='true':status='needs_running_emulator'
    return {'status':status,'api_compatibility':compatibility,'selected_instance':matches[0],
            'actual_calls':[call],'device_invoked':False,'capture_invoked':False,'product_failure':False}


def foreground_bundle(text):
    """Read explicit lifecycle records, never assume the first mission is top."""
    blocks=re.split(r'(?m)^\s*(?:UI)?AbilityRecord ID\s*#',text)[1:]
    foreground=[]
    for block in blocks:
        bundle=re.search(r'(?m)^\s*bundle name\s*\[([^\]]+)\]',block)
        state=re.search(r'(?m)^\s*state\s*[#:]\s*([A-Z_]+)\b',block)
        if bundle and state and state[1]=='FOREGROUND':
            foreground.append(bundle[1])
    values=set(foreground)
    _require(len(values)==1,'Official ability dump did not establish one foreground application; retain dump and use a supported app-scoped provider')
    return next(iter(values))


def _cell(value):
    return value.strip().strip('`').replace('\\|','|')


def _observed_bool(value):
    if type(value)is bool:return value
    if isinstance(value,str) and value.casefold() in {'true','false'}:return value.casefold()=='true'
    return None


def layout_nodes(text, bundle):
    """Decode exposed widget fields, including native Widget Tree Markdown.

    Native ``[id:N]`` values are runtime widget IDs, never accessibility IDs.
    Unexposed enabled/identifier fields remain unknown rather than inferred.
    """
    nodes=[]
    for code in re.findall(r'```(?:json)?\s*\n(.*?)```',text,re.S):
        try:
            raw=json.loads(code)
        except ValueError:
            continue
        candidates=raw.get('nodes',[]) if isinstance(raw,dict) else raw if isinstance(raw,list) else []
        for entry in candidates:
            if not isinstance(entry,dict):continue
            widget=entry.get('widgetId',entry.get('widget_id'))
            if widget is None or not str(widget).isdigit():continue
            owner=entry.get('bundleName',entry.get('bundle_id'))
            if owner and owner!=bundle:continue
            nodes.append({'widget_id':str(widget),'identifier':str(entry.get('identifier',entry.get('resourceId',''))),
                'type':str(entry.get('type','')),'label':str(entry.get('text',entry.get('label',''))),
                'value':str(entry.get('value',entry.get('text',''))),'enabled':_observed_bool(entry.get('enabled')),
                'frame':entry.get('bounds',entry.get('frame'))})
    headers=None
    for line in text.splitlines():
        if not line.lstrip().startswith('|'):headers=None;continue
        cells=[_cell(v) for v in re.split(r'(?<!\\)\|',line.strip().strip('|'))]
        if all(re.fullmatch(r':?-+:?',c.replace(' ','')) for c in cells):continue
        normalized=[re.sub(r'[\s_-]','',c).casefold() for c in cells]
        if any(c in {'widgetid','控件id'} for c in normalized):headers=normalized;continue
        if headers is None or len(cells)!=len(headers):continue
        row=dict(zip(headers,cells))
        widget=row.get('widgetid',row.get('控件id'))
        if not widget or not widget.isdigit():continue
        owner=row.get('bundlename',row.get('bundleid'))
        if owner and owner!=bundle:continue
        nodes.append({'widget_id':widget,'identifier':row.get('resourceid',row.get('identifier',row.get('accessibilityid',''))),
            'type':row.get('type',row.get('控件类型','')),'label':row.get('text',row.get('label',row.get('文本',''))),
            'value':row.get('value',row.get('text','')),'enabled':_observed_bool(row.get('enabled')),
            'frame':row.get('bounds',row.get('frame'))})
    if not nodes:
        tree=re.search(r'(?m)^## Widget Tree\s*$',text)
        if tree:
            body=re.split(r'(?m)^#{1,2}\s+',text[tree.end():],maxsplit=1)[0]
            records=[]
            for line in body.splitlines():
                start=re.match(r'^(\s*)- (.*)$',line)
                if start:
                    records.append([len(start[1].expandtabs(2)),start[2]])
                elif records and line.strip():
                    records[-1][1]+='\n'+line
            ancestors=[]
            number=r'-?\d+(?:\.\d+)?'
            geometry=re.compile(r'\[top:\s*('+number+r'),\s*left:\s*('+number+r'),\s*width:\s*('+number+r'),\s*height:\s*('+number+r')\]')
            for depth,raw in records:
                frame=geometry.search(raw)
                if not frame:continue
                prefix=raw[:frame.start()].rstrip()
                widget=re.search(r'\s+\[id:(\d+)\]\s*$',prefix)
                if widget:prefix=prefix[:widget.start()].rstrip()
                fields=prefix.split(' ',1)
                while ancestors and ancestors[-1][0]>=depth:ancestors.pop()
                label=fields[1] if len(fields)==2 else ''
                nodes.append({'widget_id':widget[1] if widget else None,'identifier':'',
                    'type':fields[0],'label':label,'value':label,'enabled':None,
                    'frame':dict(zip(('top','left','width','height'),map(float,frame.groups()))),
                    'parent_index':ancestors[-1][1] if ancestors else None,'depth':depth,
                    'native_metadata':raw[frame.end():].strip()})
                ancestors.append((depth,len(nodes)-1))
    _require(nodes,'Official emulator layout format is not recognized; keep raw Markdown and adapt its actual schema, or use Hypium')
    widgets=[n['widget_id'] for n in nodes if n['widget_id'] is not None]
    _require(len(widgets)==len(set(widgets)),'Ambiguous emulator widget ids; no action was selected')
    return nodes


def _collect_screenshot(directory, destination, *, timeout=10):
    """Await async SDK output only in its fresh directory, never Pictures."""
    _require(isinstance(timeout,(int,float)) and 0<timeout<=10,'Screenshot artifact wait must be within 10 seconds')
    deadline=time.monotonic()+timeout
    while True:
        _require(directory.is_dir() and not directory.is_symlink(),'Screenshot output directory changed')
        entries=list(directory.iterdir())
        _require(not any(p.is_symlink() for p in entries),'Screenshot output cannot follow a symlink')
        images=[p for p in entries if p.is_file() and p.suffix.casefold()=='.png']
        _require(len(images)<=1,'Official screenshot directory produced multiple PNGs; raw errors retained')
        # Emulator returns before its asynchronous writer creates/completes PNG.
        # The PNG IEND trailer marks complete output; a partial header does not.
        if images:
            with images[0].open('rb') as stream:
                stream.seek(0,os.SEEK_END)
                size=stream.tell()
                if size>=12:
                    stream.seek(-12,os.SEEK_END)
                    complete=stream.read()==b'\x00\x00\x00\x00IEND\xaeB`\x82'
                else:complete=False
            if complete:
                _png_dimensions(images[0])
                break
        remaining=deadline-time.monotonic()
        _require(remaining>0,'Official screenshot did not produce one complete PNG before the bounded artifact wait expired; raw errors retained')
        time.sleep(min(0.05,remaining))
    _require(not destination.exists(),'Canonical screenshot output unexpectedly exists')
    os.replace(images[0],destination)
    return destination


def resolve_widget(nodes, step):
    candidates=nodes
    if 'widget_id' in step:
        candidates=[node for node in candidates if node['widget_id']==str(step['widget_id'])]
    if step.get('identifier'):
        candidates=[node for node in candidates if node['identifier']==step['identifier']]
    if 'expected_label' in step:
        candidates=[node for node in candidates if node['label']==step['expected_label']]
    if 'expected_type' in step:
        candidates=[node for node in candidates if node['type']==step['expected_type']]
    _require(len(candidates)==1,'Fixed scenario selector is absent or ambiguous in the freshly observed app layout')
    return candidates[0]


def _selected_instance(rows, binding):
    selected=binding['emulator']
    matches=[row for row in rows if row.get('name')==selected['name'] and row.get('uuid')==selected['uuid']]
    _require(len(matches)==1,'Selected emulator name/uuid does not match current official instance metadata')
    row=matches[0]
    _require(str(row.get('isRunning')).lower()=='true','Selected emulator is not running; start this exact instance within its authorized scope')
    port=str(row.get('hw.hdc.port',''))
    declared=binding['device']['id']
    direct=declared in {str(row.get(key,'')) for key in ('uuid','hdcDeviceId','deviceId','serial')}
    port_bound=port.isdigit() and declared in {'127.0.0.1:'+port,'localhost:'+port}
    receipt=selected.get('binding_receipt')
    observed=False
    if isinstance(receipt,dict) and isinstance(receipt.get('path'),str):
        path=Path(receipt['path']).resolve()
        _require(path.is_file() and digest(path.read_bytes())==receipt.get('sha256'),'Emulator/device mapping observation changed')
        value=read_json(path)
        observed=(value.get('schema_version')=='hmigbot-emulator-scope/1' and value.get('observations_actual') is True
            and value.get('instance_uuid')==row['uuid'] and value.get('instance_name')==row['name']
            and value.get('device_id')==declared)
    _require(direct or port_bound or observed,'Current official metadata does not bind the selected emulator to this HDC id; provide the actual startup/device mapping observation')
    return row


def run_emulator(project, record, output, *, install=False, hdc=None, emulator=None, timeout=180):
    project=Path(project).resolve();binding=record['binding']
    _require(install,'Emulator capture needs explicit --install to bind the selected current app HAP bytes; no test HAP is required')
    _require(type(timeout)is int and 1<=timeout<=1800,'UI timeout must be 1..1800 seconds')
    hdc=Path(hdc).resolve() if hdc else Path('/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains/hdc')
    emulator=Path(emulator).resolve() if emulator else Path('/Applications/DevEco-Studio.app/Contents/tools/emulator/Emulator')
    _require(hdc.is_file() and emulator.is_file(),'Official emulator/HDC launcher unavailable; choose a supported configured provider or the Hypium fallback')
    output=_output(project,output,'emulator capture');output.mkdir(parents=True)
    calls=[];sequence=0;checkpoints=[];warnings=[]
    run_id='HE-'+uuid.uuid4().hex
    initial_source=source_identity('harmonyos',project)
    expected=[s['checkpoint_id'] for s in binding['steps'] if s['action']=='checkpoint']

    def call(command,label,limit=None):
        nonlocal sequence
        sequence+=1
        value=_call([str(p) for p in command],output,f'{sequence:04d}-{label}',limit or min(timeout,30))
        calls.append(value)
        _require(value['exit_code']==0 and not value['timed_out'],f'Official {label} call failed; raw stdout/stderr retained')
        return (output/value['stdout']).read_text(encoding='utf-8',errors='replace')

    def foreground():
        # Official replacement for deprecated aa dump. If the supported service
        # formatter is absent, use the documented legacy read-only dump.
        text=''
        try:
            text=call([hdc,'-t',binding['device']['id'],'shell','hidumper','-s','AbilityManagerService','-a','-a'],'foreground')
            observed=foreground_bundle(text)
        except MigrationError:
            if re.search(r'(?m)^\s*(?:UI)?AbilityRecord ID\s*#',text):
                raise  # An explicitly ambiguous lifecycle dump is not a missing formatter.
            text=call([hdc,'-t',binding['device']['id'],'shell','aa','dump','-a'],'foreground-legacy')
            observed=foreground_bundle(text)
        _require(observed==binding['bundle_id'],'Foreground application differs from the selected bundle; no layout/action/capture is allowed')
        return observed

    def layout(row, *, controls_required=True):
        foreground()
        instance=Path(row['instancePath']).resolve()
        fixed=instance/'uiLayout/analysis.md'
        _require(not fixed.is_symlink() and not fixed.parent.is_symlink(),'Official layout output cannot follow a symlink')
        backup=fixed.with_name('.hmigbot-layout-backup-'+uuid.uuid4().hex)
        existing=fixed.exists()
        if existing:fixed.rename(backup)
        owned_stamp=None
        try:
            call([emulator,'-instance',row['name'],'-uiLayout','-a'],'layout')
            _require(fixed.is_file(),'Official layout call did not produce its documented instance uiLayout/analysis.md')
            info=fixed.stat();owned_stamp=(info.st_ino,info.st_mtime_ns,info.st_size)
            foreground()
            raw=fixed.read_bytes()
            destination=output/'layouts'/f'{sequence:04d}-analysis.md'
            destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
            try:
                nodes=layout_nodes(raw.decode('utf-8'),binding['bundle_id'])
            except MigrationError as exc:
                if controls_required:raise
                warnings.append({'kind':'layout_schema_unrecognized_raw_retained','detail':str(exc),
                                 'raw_layout':destination.relative_to(output).as_posix()})
                nodes=[]
            return nodes,destination
        finally:
            if fixed.exists() and owned_stamp:
                info=fixed.stat()
                if (info.st_ino,info.st_mtime_ns,info.st_size)==owned_stamp:fixed.unlink()
                else:warnings.append({'kind':'concurrent_layout_update_retained','path':str(fixed),'previous_backup':str(backup)})
            if existing and backup.exists():
                if not fixed.exists():os.replace(backup,fixed)
                else:warnings.append({'kind':'previous_layout_retained_in_backup','path':str(backup)})

    error=None;row=None
    try:
        help_text=call([emulator,'-help'],'emulator-help')
        _require(all(flag in help_text for flag in ('-screenshotPath','-uiLayout','-click','-fill')),
                 'Selected official emulator CLI lacks required operations; use the scoped Hypium fallback')
        rows=json.loads(call([emulator,'-list','-details'],'emulator-instances'))
        _require(isinstance(rows,list),'Official emulator instance metadata is not a list')
        selected=[item for item in rows if item.get('name')==binding['emulator']['name'] and item.get('uuid')==binding['emulator']['uuid']]
        _require(len(selected)==1,'Selected emulator name/uuid does not match current official instance metadata')
        compatibility=emulator_compatibility(binding['hap'],binding['bundle_id'],selected[0])
        write_json(output/'preflight.json',compatibility)
        if compatibility['status']=='needs_compatible_emulator':
            result={'status':'needs_compatible_emulator','backend':'official_emulator_cli','api_compatibility':compatibility,
                'calls':calls,'capture_invoked':False,'device_invoked':False,'product_failure':False,'behavior_verified':False}
            write_json(output/'run.json',result)
            return result
        if str(selected[0].get('isRunning')).lower()!='true':
            result={'status':'needs_running_emulator','backend':'official_emulator_cli','selected_instance':selected[0],
                'calls':calls,'capture_invoked':False,'device_invoked':False,'product_failure':False,
                'recovery':'Start only this selected compatible instance; preserve its actual startup/image errors for recovery',
                'behavior_verified':False}
            write_json(output/'run.json',result)
            return result
        row=_selected_instance(rows,binding)
        hap=Path(binding['hap']);_hap_metadata(hap,binding['bundle_id'])
        _require(build_identity(hap)==binding['build_sha256'],'Current app HAP changed')
        installed=call([hdc,'-t',binding['device']['id'],'install','-r',hap],'install-app',min(timeout,180))
        if not _installation_confirmed(installed,hap):
            result={'status':'installation_unconfirmed','backend':'official_emulator_cli','calls':calls,
                'device':binding['device'],'behavior_verified':False,'capture_invoked':False,'product_failure':False,
                'recovery':'Official install output did not confirm this selected HAP; preserve raw output and resolve installation before capture'}
            write_json(output/'run.json',result)
            return result
        launched=call([hdc,'-t',binding['device']['id'],'shell','aa','start','-a',binding['ability_name'],
              '-b',binding['bundle_id'],'-W'],'launch-app')
        if not _launch_confirmed(launched,binding['bundle_id'],binding['ability_name']):
            result={'status':'launch_unconfirmed','backend':'official_emulator_cli','calls':calls,
                'device':binding['device'],'behavior_verified':False,'capture_invoked':False,'product_failure':False,
                'recovery':'Official aa start -W output did not confirm the selected bundle/ability; preserve raw output and resolve launch before capture'}
            write_json(output/'run.json',result)
            return result
        # aa -W returns after first-frame/foreground completion, not a fixed sleep.
        foreground()
        for step in binding['steps']:
            action=step['action']
            deadline=time.monotonic()+step.get('timeout_ms',5000)/1000
            while True:
                nodes,raw_layout=layout(row,controls_required=action!='checkpoint')
                if action=='checkpoint':break
                try:
                    node=resolve_widget(nodes,step)
                    break
                except MigrationError:
                    if time.monotonic()>=deadline:raise
                    time.sleep(min(0.2,max(0,deadline-time.monotonic())))
            if action=='checkpoint':
                key=step['checkpoint_id'];shot=output/'shots'/(key+'.png');shot.parent.mkdir(parents=True,exist_ok=True)
                _require(not shot.exists(),'New screenshot output unexpectedly exists')
                # The official SDK requires an existing directory. A missing
                # filename silently redirects captures into the user's Pictures.
                capture_directory=output/'screenshot-output'/key
                capture_directory.mkdir(parents=True,exist_ok=False)
                foreground()
                call([emulator,'-instance',row['name'],'-screenshot','-screenshotPath',capture_directory],'screenshot')
                _collect_screenshot(capture_directory,shot)
                try:
                    foreground()
                except MigrationError:
                    if shot.is_file() and shot.resolve().is_relative_to(output):shot.unlink()
                    raise
                hierarchy=output/'hierarchy'/(key+'.json');hierarchy.parent.mkdir(parents=True,exist_ok=True)
                write_json(hierarchy,{'nodes':nodes,'scope':'official emulator exposed widget layout of foreground application display',
                    'raw_layout':raw_layout.relative_to(output).as_posix(),'window_bundle_id':binding['bundle_id'],
                    'parse_status':'decoded_named_fields' if nodes else 'raw_only_unknown_schema','complete_internal_tree':False})
                checkpoints.append({'id':key,'status':'passed','captured_at':datetime.now(timezone.utc).isoformat(),
                    'capture_scope':'emulator_display_bound_to_verified_foreground_app',
                    'screenshot':{'path':shot.relative_to(output).as_posix(),'sha256':digest(shot.read_bytes())},
                    'hierarchy':{'path':hierarchy.relative_to(output).as_posix(),'sha256':digest(hierarchy.read_bytes())}})
            else:
                if action=='assert_text':_require(node['label']==step.get('text',''),'Fixed scenario text assertion failed')
                elif action in {'tap','back'}:
                    foreground();call([emulator,'-instance',row['name'],'-click',node['widget_id']],'click');foreground()
                elif action=='input':
                    foreground();call([emulator,'-instance',row['name'],'-fill',node['widget_id']+' '+step.get('text','')],'fill');foreground()
        _require(source_identity('harmonyos',project)==initial_source,'Product source changed while capturing emulator evidence')
        _require(build_identity(Path(binding['hap']))==binding['build_sha256'],'Selected HAP changed while capturing emulator evidence')
    except (MigrationError,OSError,ValueError,KeyError,TypeError) as exc:
        error=str(exc)
    by_id={c['id']:c for c in checkpoints}
    checkpoints=[by_id.get(key,{'id':key,'status':'not_run'}) for key in expected]
    # The emulator CLI exposes controls/screenshots, not complete per-app locale,
    # theme/font policy. Never substitute the requested configuration as observed.
    configuration={'schema_version':'hmigbot-ui-current/1','platform':'harmonyos','bundle_id':binding['bundle_id'],
        'device':binding['device'],'build_sha256':binding['build_sha256'],'observed_configuration':{},
        'observations_actual':False,'calls':calls,'reason':'Official emulator UI operations do not establish all app configuration fields; supply actual application observations or use Hypium'}
    write_json(output/'current-configuration.json',configuration)
    manifest={'schema_version':'hmigbot-ui-evidence/1','platform':'harmonyos','run_id':run_id,'bundle_id':binding['bundle_id'],
        'device':binding['device'],'build':{'sha256':binding['build_sha256']},'source_sha256':initial_source,
        'scenario':binding['scenario'],'platform_script_sha256':digest(json_bytes(binding['steps'])),
        'configuration':binding['configuration'],'captured_at':datetime.now(timezone.utc).isoformat(),
        'checkpoints':checkpoints,'backend':'official_emulator_cli','capture_scope':'emulator_display_bound_to_verified_foreground_app',
        'configuration_observed':False,'actual_calls':calls,'warnings':warnings,'behavior_verified':False,
        'observations_only':binding.get('observations_only',False),
        'status':'failed' if error else 'passed','error':error,'emulator_identity':row}
    manifest['artifacts']={p.relative_to(output).as_posix():digest(p.read_bytes()) for p in output.rglob('*') if p.is_file()}
    write_json(output/'manifest.json',manifest)
    current=identity(manifest)
    current['verification']={'build_path':binding['hap'],'source_root':str(project),
        'configuration_receipt':{'path':str(output/'current-configuration.json'),'sha256':manifest['artifacts']['current-configuration.json']}}
    write_json(output/'current.json',current)
    result={'status':manifest['status'],'backend':'official_emulator_cli','manifest':str(output/'manifest.json'),
        'current':str(output/'current.json'),'calls':calls,'behavior_verified':False,
        'configuration_observed':False,'error':error,'warnings':warnings,
        'recovery':'Resolve the exact reported app/device/layout/configuration gap; Hypium remains optional for unsupported operations'}
    write_json(output/'run.json',result)
    return result
