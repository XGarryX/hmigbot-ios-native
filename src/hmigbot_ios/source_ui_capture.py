"""Spec consumption of scoped native iOS UI evidence, separate from source builds.

The caller chooses application/device/scenario and page correspondence. Native
capture is delegated to the existing official XCTest adapter. No desktop, new
page scope, business state or source-to-control identity is inferred here.
"""
from pathlib import Path
import os
import re
import shutil
import time

from .core import MigrationError, digest, json_bytes, read_json, safe_child, source_snapshot, write_json

INDEX = 'spec/ref/ios-source-ui-observations.json'
MODES = {'ask', 'capture', 'replay', 'skip'}
SCHEMA = 'hmigbot-spec-source-ui/1'
START, END = '<!-- hmigbot-source-ui:start -->', '<!-- hmigbot-source-ui:end -->'


def settings(project, cfg=None, selected=None):
    project = Path(project)
    if cfg is None:
        path = project / 'spec/ref/ios-analysis-config.json'
        cfg = read_json(path) if path.is_file() else {}
    value = cfg.get('ui_capture', {})
    if (not isinstance(value, dict) or set(value)-{'mode','request','manifest','bindings','required'}
            or value.get('mode','ask') not in MODES or type(value.get('required',False)) is not bool):
        raise MigrationError('Invalid ui_capture; use mode/request/manifest/bindings/required')
    result = {**value, 'mode': value.get('mode','ask'), 'required':value.get('required',False)}
    if selected is not None:
        if selected not in MODES:
            raise MigrationError('Source UI choice must be ask, capture, replay or skip')
        result['mode'] = selected
    if result['mode'] == 'ask' and cfg.get('mode')!='static':
        path = project / 'spec/reports/init-environment.json'
        if path.is_file():
            saved = read_json(path).get('capabilities',{}).get('source_ui_capture',{}).get('selected')
            if saved in {'capture','replay','skip'}:
                result['mode'] = saved
    return result


def choice_card(project, source, cfg=None, selected=None):
    if cfg is None:
        path=Path(project)/'spec/ref/ios-analysis-config.json'
        cfg=read_json(path) if path.is_file() else {}
    value = settings(project,cfg,selected)
    # No extra question for a source with no UI/product hint, unless requested.
    possible=value['mode']!='ask'
    if not possible:
        from .core import EXCLUDED
        for parent,dirs,names in os.walk(source):
            dirs[:]=[d for d in dirs if d not in EXCLUDED]
            if any(Path(name).suffix in {'.swift','.storyboard','.xib','.pbxproj'} for name in names):
                possible=True;break
    if cfg.get('mode')=='static' and value['mode']=='ask':possible=False
    return {'id':'source_ui_capture','title':'源端 UI 采集策略',
            'state':'pending' if possible and value['mode']=='ask' else 'selected' if possible else 'not_applicable',
            'selected':None if value['mode']=='ask' else value['mode'],
            'requires_user_choice':possible and value['mode']=='ask','blocks_independent_cli':False,
            'required':value['required'], 'required_scope':['bundle_id','simulator_udid','simulator_app_build','scenario_checkpoints','source_to_page_bindings'],
            'source_analysis_mode':(cfg or {}).get('mode','auto'),
            'static_combination_note':'仅选择 static 不会继承旧的应用运行策略；static 与明确 capture 同时指定时，前者仅限制源编译，后者单独授权所选 App 的原生采集。',
            'options':[{'id':'capture','label':'原生采集并复用有效证据',
                        'difference':'指定应用/模拟器，用 Apple XCTest 采集截图和控件；需要模拟器构建与固定场景，会安装启动测试应用。'},
                       {'id':'replay','label':'使用已有当前证据',
                        'difference':'不运行应用；核对当前源码、构建、设备、场景与附件摘要，不将旧截图记作本轮执行。'},
                       {'id':'skip','label':'本轮仅静态分析',
                        'difference':'继续规格生成，运行外观和状态保持未观测；不授予 UI 验收通过。'}]}


def render_choice(card):
    if card.get('id')!='source_ui_capture' or card.get('state')=='not_applicable':
        return ''
    if not card['requires_user_choice']:
        message='【源端 UI 采集策略】沿用 '+str(card['selected'])+'；不扩大已确认应用、模拟器和场景。'
        if card.get('source_analysis_mode')=='static' and card['selected']=='capture':
            message+=' 源分析为 static，但本次另外明确选择了原生 UI 采集，将安装启动所选测试 App。'
        return message
    return '【需要开发者选择：源端 UI 采集】\n'+'\n'.join(
        f"{n}. {item['label']}：{item['difference']}" for n,item in enumerate(card['options'],1)
    )+'\n已有明确范围与授权直接沿用；缺设备/场景仅暂缓对应采集，不增加基础转换总门禁。'


def _input(project, spelling):
    if not isinstance(spelling,str) or not spelling.startswith('spec/ref/'):
        raise MigrationError('Source UI input must be an explicit project spec/ref path')
    path = safe_child(project,spelling)
    if not path.is_file() or path.is_symlink():
        raise MigrationError('Source UI input missing or linked: '+spelling)
    return path


def _bindings(source, value, checkpoints):
    if not isinstance(value,list) or not value:
        raise MigrationError('Source UI needs explicit checkpoint/page/source bindings')
    bound, seen = [], set()
    known={f['path']:f for f in source_snapshot(source)['files']}
    for row in value:
        if (not isinstance(row,dict) or set(row)-{'page_id','checkpoint_id','source_anchors'}
                or not isinstance(row.get('page_id'),str) or not re.fullmatch(r'page_\d+',row['page_id'])
                or row.get('checkpoint_id') not in checkpoints or not isinstance(row.get('source_anchors'),list)
                or not row['source_anchors']):
            raise MigrationError('Source UI binding needs stable page/checkpoint and source anchors')
        key=(row['page_id'],row['checkpoint_id'])
        if key in seen:
            raise MigrationError('Duplicate source UI page/checkpoint binding')
        seen.add(key); anchors=[]
        for anchor in row['source_anchors']:
            if not isinstance(anchor,dict) or anchor.get('path') not in known:
                raise MigrationError('Source UI anchor outside current migration source')
            path=safe_child(source,anchor['path']); lines=path.read_text(encoding='utf-8').splitlines()
            line=anchor.get('line')
            if type(line)is not int or not 1<=line<=len(lines) or not isinstance(anchor.get('symbol'),str) or not anchor['symbol']:
                raise MigrationError('Source UI anchor needs a current line and explicit symbol')
            anchors.append({'path':anchor['path'],'line':line,'symbol':anchor['symbol'],
                            'quote':lines[line-1],'sha256':digest(path.read_bytes())})
        bound.append({**row,'source_anchors':anchors,'mapping_authority':'caller_supplied_page_correspondence; not inferred compiler identity'})
    return bound


def _verify(project, source, manifest_path, request):
    from .ios_ui_automation import validate_request, scenario_identity, PROVIDER
    from .ui_validation_evidence import validate_bundle, build_identity, source_identity
    app, checkpoints=validate_request(request)
    request={**request,'source_root':str(Path(request['source_root']).resolve()),'app_path':str(app)}
    if Path(request['source_root']).resolve()!=Path(source).resolve():
        raise MigrationError('Source UI request belongs to a different iOS source')
    expected={'platform':'ios','bundle_id':request['bundle_id'],
              'device':{'id':request['device_id'],'kind':'simulator'},
              'build':{'sha256':build_identity(app)},'source_sha256':source_identity('ios',source),
              'scenario':scenario_identity(request),'configuration':request['configuration'],
              'verification':{'source_root':str(source),'build_path':str(app)}}
    manifest=read_json(manifest_path)
    ref=manifest.get('verification',{}).get('configuration_receipt')
    if ref:
        relative='configuration-observation.json'
        expected['verification']['configuration_receipt']={'path':str(manifest_path.parent/relative),'sha256':ref['sha256']}
    checked=validate_bundle(manifest_path,expected)
    # App environment gaps limit configuration equivalence, not screenshot use.
    gaps=[i for i in checked['issues'] if i['rule'].startswith('current_configuration_')]
    failures=[i for i in checked['issues'] if i not in gaps]
    if failures or manifest.get('status')!='passed' or manifest.get('platform_script_sha256')!=digest(json_bytes(request['scenario']['steps'])):
        raise MigrationError('Source UI evidence is stale/failed or belongs to a different script: '+str(failures))
    prepared=read_json(manifest_path.parent/'prepared.json')
    if prepared.get('provider_sha256')!=digest(PROVIDER.read_bytes()) or prepared.get('request_sha256')!=digest(json_bytes(request)):
        raise MigrationError('Source UI request/provider changed; capture a fresh attempt')
    actual=manifest.get('calls',[])
    if not any(c.get('kind')=='app_ui_test' and c.get('actual_call_now')is True and c.get('exit_code')==0 and not c.get('timed_out')
               and 'test-without-building' in c.get('argv',[]) for c in actual if isinstance(c,dict)):
        raise MigrationError('Source UI manifest has no successful original XCTest call')
    if set(checkpoints)!={c['id'] for c in manifest['checkpoints']}:
        raise MigrationError('Source UI checkpoint scope differs')
    return manifest,gaps


def execute(project, source, directory, cfg, selected=None):
    """Run once or reuse exact current evidence; never mutate a planned project."""
    from .ios_ui_automation import prepare, run, validate_request
    project,source,directory=Path(project),Path(source),Path(directory)
    value=settings(project,cfg,selected); started=time.monotonic()
    result={'schema_version':SCHEMA,'source_sha256':source_snapshot(source)['sha256'],
            'selected':value['mode'],'required':value['required'],'status':'not_run',
            'actual_native_ui_run':False,'reused':False,'observations':[], 'gaps':[],
            'behavior_verified':False,'application_acceptance':'not_established'}
    if (project/'spec/state/state.json').exists() or any((project/'spec/waves').glob('plan-*.json')):
        raise MigrationError('Source UI evidence cannot change under a frozen plan; use reviewed source-refresh/replan')
    phase='scope'
    try:
        if value['mode'] in {'ask','skip'}:
            static_only=cfg.get('mode')=='static' and value['mode']=='ask'
            result.update(status='needs_choice' if value['mode']=='ask' and not static_only else 'not_selected')
            result['gaps']=[{'reason':'static_source_scope_without_explicit_live_ui' if static_only
                            else 'source_ui_strategy_not_selected' if value['mode']=='ask' else 'developer_selected_static_only'}]
            return result
        request_path=_input(project,value.get('request')); request=read_json(request_path)
        app,checkpoint_ids=validate_request(request)
        request={**request,'source_root':str(Path(request['source_root']).resolve()),'app_path':str(app)}
        if Path(request['source_root']).resolve()!=source.resolve():
            raise MigrationError('Source UI request source differs from configured iOS source')
        bindings=_bindings(source,value.get('bindings'),checkpoint_ids)
        previous=read_json(project/INDEX) if (project/INDEX).is_file() else {}
        candidate=value.get('manifest') or (previous.get('manifest') if value['mode']=='capture' else None)
        manifest_path=None; manifest=None; gaps=[]
        if candidate:
            phase='replay'
            try:
                path=_input(project,candidate)
                manifest,gaps=_verify(project,source,path,request); manifest_path=path
                result['reused']=True
            except (MigrationError,OSError,ValueError,KeyError,TypeError) as exc:
                if value['mode']=='replay':raise
                result['rejected_previous_evidence']=str(exc)
        if manifest_path is None:
            if value['mode']=='replay':
                raise MigrationError('Replay requires a current explicitly bound manifest')
            # Compiler/test caches can contain generated links. Keep them out of
            # Spec evidence/contract enumeration; publish only original receipts.
            native=project/'.build/hmigbot-source-ui'/directory.name
            result['native_directory']=str(native)
            phase='prepare'
            tick=time.monotonic(); prepare(request,native)
            result['prepare_seconds']=time.monotonic()-tick
            phase='native'
            tick=time.monotonic(); execution=run(native)
            result['native_seconds']=time.monotonic()-tick
            result['actual_native_ui_run']=bool(execution.get('ui_test_executed_now'))
            result['native_result']=execution
            if execution.get('status')!='passed':
                raise MigrationError('Native source UI capture failed; original logs retained at '+str(native))
            original=read_json(native/'manifest.json')
            published=directory/'source-ui'; published.mkdir(parents=True)
            for relative in [*original['artifacts'], 'manifest.json','request.json','prepared.json']:
                src=safe_child(native,relative); dst=safe_child(published,relative)
                dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
            result['native_directory']=str(native)
            manifest_path=published/'manifest.json'
            manifest,gaps=_verify(project,source,manifest_path,request)
        from .ui_cross_platform import nodes
        result.update(status='captured',manifest=manifest_path.relative_to(project).as_posix(),
            manifest_sha256=digest(manifest_path.read_bytes()),request= request_path.relative_to(project).as_posix(),
            request_sha256=digest(request_path.read_bytes()),provider_sha256=read_json(manifest_path.parent/'prepared.json')['provider_sha256'],
            captured_identity={k:manifest[k] for k in ('bundle_id','device','build','source_sha256','scenario','configuration')},
            observed_context='iOS Simulator UI; independent from a device SDK source compiler view',gaps=gaps)
        for row in bindings:
            checkpoint=next(c for c in manifest['checkpoints'] if c['id']==row['checkpoint_id'])
            refs={k:{'path':(manifest_path.parent/checkpoint[k]['path']).relative_to(project).as_posix(),
                      'sha256':checkpoint[k]['sha256']} for k in ('screenshot','hierarchy')}
            hierarchy=nodes(read_json(project/refs['hierarchy']['path']))
            result['observations'].append({**row,**refs,'runtime':'captured',
                'native_nodes':len(hierarchy),'text_nodes':sum(n['role']=='text' for n in hierarchy),
                'truncated_nodes':sum(n.get('children_truncated')is True for n in hierarchy),
                'scope':'Only this explicitly bound page/checkpoint state; no default-state or all-branch inference'})
        return result
    except (MigrationError,OSError,ValueError,KeyError,TypeError) as exc:
        if result.get('native_directory'):
            call=Path(result['native_directory'])/'calls/test.json'
            if call.is_file():
                actual=read_json(call)
                result['actual_native_ui_run']=actual.get('actual_call_now')is True
        result.update(status='capture_failed' if phase=='native' else 'stale_evidence' if phase=='replay'
                      else 'preparation_failed' if phase=='prepare' else 'needs_scope',error=str(exc))
        result['gaps'].append({'reason':'native_ui_capture_or_binding_unavailable','detail':str(exc),
                               'recovery':'Resolve the exact app build/device/scenario or evidence error and rerun this scope; do not change source or frozen hashes'})
        return result
    finally:
        result['elapsed_seconds']=time.monotonic()-started
        write_json(project/INDEX,result)


def authoring_observations(project, source, documents):
    """Expose actual captures to the page author and freeze their dependencies."""
    project,source=Path(project),Path(source); path=project/INDEX
    if not path.is_file():return {},{},[]
    report=read_json(path); inputs={INDEX:digest(path.read_bytes())}
    if report.get('status')!='captured':
        if report.get('required')is True:
            raise MigrationError('Explicitly required source UI capture remains unavailable; retain scope and resolve its original error')
        # Unselected/diagnostic UI progress is not a business contract input.
        return {},{},[]
    if report.get('source_sha256')!=source_snapshot(source)['sha256']:
        raise MigrationError('Spec source UI observations are stale; refresh selected evidence')
    request_path=_input(project,report['request'])
    if digest(request_path.read_bytes())!=report['request_sha256']:
        raise MigrationError('Source UI request changed after capture')
    manifest_path=_input(project,report['manifest'])
    if digest(manifest_path.read_bytes())!=report['manifest_sha256']:
        raise MigrationError('Source UI manifest changed after capture')
    manifest,gaps=_verify(project,source,manifest_path,read_json(request_path))
    inputs[report['request']]=report['request_sha256']; inputs[report['manifest']]=report['manifest_sha256']
    prepared=manifest_path.parent/'prepared.json'; inputs[prepared.relative_to(project).as_posix()]=digest(prepared.read_bytes())
    for relative,sha in manifest['artifacts'].items():
        inputs[(manifest_path.parent/relative).relative_to(project).as_posix()]=sha
    by_id={d['id']:d for d in documents}; observations={}
    for row in report['observations']:
        checkpoint=next((c for c in manifest['checkpoints'] if c['id']==row.get('checkpoint_id')),None)
        if checkpoint is None:
            raise MigrationError('Source UI observation points to a different checkpoint')
        for field in ('screenshot','hierarchy'):
            expected={'path':(manifest_path.parent/checkpoint[field]['path']).relative_to(project).as_posix(),
                      'sha256':checkpoint[field]['sha256']}
            if row.get(field)!=expected:
                raise MigrationError('Source UI observation is not bound to the original '+field)
        from .ui_cross_platform import nodes
        actual_nodes=nodes(read_json(project/row['hierarchy']['path']))
        if (row.get('native_nodes')!=len(actual_nodes) or row.get('text_nodes')!=sum(n['role']=='text' for n in actual_nodes)
                or row.get('truncated_nodes')!=sum(n.get('children_truncated')is True for n in actual_nodes)):
            raise MigrationError('Source UI node summary differs from the original hierarchy')
        doc=by_id.get(row['page_id'])
        if doc is None:
            gaps.append({'reason':'captured_page_not_in_authored_inventory','page_id':row['page_id']});continue
        allowed={a['path'] for a in doc['source_anchors']}
        if doc['kind']!='page' or not {a['path'] for a in row['source_anchors']}<=allowed:
            raise MigrationError('Source UI capture does not belong to this page source: '+row['page_id'])
        for anchor in row['source_anchors']:
            f=safe_child(source,anchor['path'])
            if digest(f.read_bytes())!=anchor['sha256'] or f.read_text().splitlines()[anchor['line']-1]!=anchor['quote']:
                raise MigrationError('Source UI page anchor changed')
        observations.setdefault(row['page_id'],[]).append({**row,'configuration_gaps':gaps,
            'captured_identity':report['captured_identity'],'review_status':'requires_original_image_and_hierarchy_review'})
    return observations,inputs,gaps


def frozen_inputs(project, source=None):
    """Only selected capture dependencies; no whole cache/run-directory freeze."""
    project=Path(project)
    if not (project/INDEX).is_file():return {}
    if source is None:
        from .native_pipeline import context
        source,_=context(project)
    report=read_json(project/INDEX)
    if report.get('status')!='captured':
        if report.get('required')is True:
            raise MigrationError('Explicitly required source UI capture remains unavailable')
        return {}
    documents=[{'id':row['page_id'],'kind':'page','source_anchors':row['source_anchors']}
               for row in report['observations']]
    _,inputs,_=authoring_observations(project,source,documents)
    return inputs


def render_page(text, observations):
    lines=[START,'### 原生 UI 检查点观察（工具绑定，待内容复核）','',
           '以下是所选 iOS Simulator 构建的实际捕获，独立于 iphoneos 编译分支；不替代源码默认值、其他页面或全业务验收。','']
    for row in observations:
        lines += [f"- 检查点 `{row['checkpoint_id']}`，runtime=captured；原生节点 {row['native_nodes']}，文本 {row['text_nodes']}，截断 {row['truncated_nodes']}。",
                  f"- 原图：[{row['screenshot']['path']}](../../../{row['screenshot']['path']})；控件树：[{row['hierarchy']['path']}](../../../{row['hierarchy']['path']})。",
                  '- 源码对应：'+', '.join(a['path']+':'+str(a['line'])+' '+a['symbol'] for a in row['source_anchors'])+'。',
                  '- 应用配置缺口：'+('保留未知，见原始配置收据。' if row.get('configuration_gaps',[{}]) else '本次实际配置见绑定收据。'),'']
    block='\n'.join(lines+[END])
    if START in text:
        if text.count(START)!=1 or text.count(END)!=1:raise MigrationError('Ambiguous source UI managed evidence block')
        before,rest=text.split(START,1); _,after=rest.split(END,1)
        return before+block+after
    return text.rstrip()+'\n\n'+block+'\n'
