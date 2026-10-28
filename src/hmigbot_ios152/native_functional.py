"""Native source boundaries around the original functional projection/merge.

Analysis keys and original enumeration/folding stay in the bundled engine.
Synthetic labels never become UI text, and static seeds never become observed
iOS truth. All original operations run against checked disposable inputs.
"""
from __future__ import annotations
import argparse
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

from hmigbot_ios.core import MigrationError, read_json, write_json, atomic_write
from . import native_canonical as C

FILES = ('functional_registry.json', 'test_intents.json', 'compose_host_map.json')
GT = {'expected_ios','ios_trusted','ios_anchor','precondition','grounding',
      'grounding_evidence','runtime','evidence','observed_outcome'}
LOCATOR = ('native_analysis_label','source_native_selector','native_locator_status',
           'native_locator_debt','native_locator_scope')


def has_grounding(check):
    anchor=check.get('ios_anchor')
    runtime_anchor=(isinstance(anchor,dict) and any(value is not None for key,value in anchor.items()
        if key not in {'decl_file','impl_file','raw_identifier'}))
    return (check.get('expected_ios') is not None or check.get('ios_trusted') is not None or runtime_anchor or
            any(check.get(k) is not None for k in GT-set(C.FIELDS)-{'precondition'}))


def publish(outputs, guard):
    """Stage the complete JSON set first; restore prior bytes on publish error."""
    parent=next(iter(outputs)).parent;parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.native-functional-publish-',dir=parent) as directory:
        staged={}
        for index,(path,value) in enumerate(outputs.items()):
            temporary=Path(directory)/str(index);write_json(temporary,value);staged[path]=temporary
        guard.verify()
        backup={path:path.read_bytes() if path.is_file() else None for path in outputs}
        written=[]
        try:
            for path,temporary in staged.items():
                path.parent.mkdir(parents=True,exist_ok=True);os.replace(temporary,path);written.append(path)
        except BaseException:
            for path in reversed(written):
                if backup[path] is None:path.unlink(missing_ok=True)
                else:atomic_write(path,backup[path])
            raise


def check_key(check):
    if check.get('feature_path'):return ('feature_path',check['feature_path'])
    if check.get('fp_id'):return ('fp_id',check['fp_id'])
    raise MigrationError('Functional check has no stable original key')


def scoped_key(page, check):
    return (page,*check_key(check))


def checks(tree):
    result = {}
    for page in C.page_records(tree):
        for check in page.get('functional_checks',[]):
            key = scoped_key(page['id'],check)
            if key in result:raise MigrationError('Duplicate original functional key: '+str(key))
            result[key] = check
    return result


def match_checks(old,new):
    """Use the original registry's feature_path identity, with explicit legacy fallback."""
    matches={}
    for key,prior in old.items():
        target=key if key in new else None
        if target is None and not prior.get('feature_path') and prior.get('fp_id'):
            candidates=[k for k,v in new.items() if k[0]==key[0] and v.get('fp_id')==prior['fp_id']]
            old_candidates=[k for k,v in old.items() if k[0]==key[0] and v.get('fp_id')==prior['fp_id']]
            if len(candidates)>1 or candidates and len(old_candidates)!=1:
                raise MigrationError('Ambiguous legacy functional fp_id fallback: '+str(key))
            if candidates:target=candidates[0]
        # Ordinary checks predate the explicit "functional" discriminator.
        # A folded presence/behavior record is a different oracle, even when
        # its prefix happens to reuse an old ordinary feature_path.
        if target is not None and (prior.get('check_kind') or 'functional')!=(new[target].get('check_kind') or 'functional'):
            target=None
        if target is not None:
            if target in matches:raise MigrationError('Two old functional checks match one new check: '+str(target))
            matches[target]=(key,prior)
    removed=set(old)-{key for key,_ in matches.values()}
    return matches,removed


def legacy_static_seeds(tree, contracts, source):
    """Recover only proved declarations from the pre-native iOS wire schema."""
    result=copy.deepcopy(tree);count=0
    registry=contracts.get('functional_registry.json',{})
    entries=registry if isinstance(registry,list) else registry.get('entries',[])
    hostmap=contracts.get('compose_host_map.json',{})
    for page in C.page_records(result):
        for check in page.get('functional_checks',[]):
            check.pop('native_unproved_original_oracle',None)
            if 'ios_anchor' in check or 'android_anchor' not in check:continue
            anchor=check['android_anchor']
            if not isinstance(anchor,dict) or source is None:
                raise MigrationError('Legacy iOS declaration anchor needs the selected native source')
            feature=check.get('feature_path');matches=[e for e in entries if e.get('feature_path')==feature]
            host=hostmap.get(feature,{})
            components=[c for c in page.get('components',[]) if c.get('id')==host.get('component_id')]
            if len(matches)!=1 or host.get('host_id')!=page['id'] or len(components)!=1:
                raise MigrationError('Legacy declaration has no exact current registry/host component: '+str(feature))
            entry=matches[0];component=components[0];span=component.get('source_anchor') or {}
            decl=anchor.get('decl_file');impl=anchor.get('impl_file')
            expected=str(span.get('file'))+':'+str(span.get('line'))
            if (not decl or decl not in source.files or impl is not None and impl not in source.files
                    or decl!=entry.get('source_file') or decl!=span.get('file')
                    or anchor.get('raw_identifier')!=entry.get('raw_identifier')
                    or host.get('code_anchor')!=expected or check.get('code_anchor')!=expected):
                raise MigrationError('Legacy declaration differs from its current source component: '+str(feature))
            if span.get('sha256') and span['sha256']!=source.records[decl]['sha256']:
                raise MigrationError('Legacy component source hash is stale: '+str(feature))
            check['ios_anchor']={k:copy.deepcopy(anchor[k]) for k in ('decl_file','impl_file','raw_identifier') if k in anchor}
            check['native_ios_anchor_provenance']={'kind':'legacy_android_alias_static_seed',
                'feature_path':feature,'component_id':host['component_id'],
                'source_file_sha256':source.records[decl]['sha256']}
            unproved={k:copy.deepcopy(check[k]) for k in ('expected_android','android_trusted') if check.get(k) is not None}
            extra={k:v for k,v in anchor.items() if k not in {'decl_file','impl_file','raw_identifier'} and v is not None}
            if extra:unproved['android_anchor_runtime_fields']=copy.deepcopy(extra)
            if unproved:check['native_unproved_original_oracle']=unproved
            if 'expected_ios' not in check:check['expected_ios']=None
            if 'ios_trusted' not in check:check['ios_trusted']=None
            count+=1
    return result,count


def project_locators(tree, hostmap, intents, proven_controls):
    pages = {p['id']:p for p in C.page_records(tree)}
    modified = {}
    for feature, host in hostmap.items():
        page = pages.get(host.get('host_id'),{})
        components = [c for c in page.get('components',[]) if c.get('id')==host.get('component_id')]
        if not page:raise MigrationError('Original host map has no source page: '+feature)
        if len(components)!=1:raise MigrationError('Original host map lacks a unique source component: '+feature)
        component = components[0]
        if isinstance(component.get('text'),str) and component['text'].strip():
            if host.get('native_locator_scope'):raise MigrationError('Original static-text host retained stale native locator metadata: '+feature)
            continue
        old = host.get('native_analysis_label') if host.get('native_locator_scope') else host.get('tap_text')
        host.pop('source_native_selector',None);host.pop('native_locator_debt',None)
        host['native_analysis_label'] = old
        host['native_locator_scope'] = 'ios_source_only'
        host['tap_text'] = None
        # Shared historical tap fields must not carry an iOS-only identifier to
        # the target driver. The target needs its own observed locator.
        host['tap_by'] = 'native_observation_required'
        proof = proven_controls.get(component.get('id'))
        anchor = component.get('source_anchor') or {}
        span = component.get('native_source_span') or {}
        identifier = component.get('native_identifier')
        if (proof and identifier and proof.get('accessibility_identifier')==identifier
                and proof.get('file')==anchor.get('file')
                and proof.get('start')==span.get('start') and proof.get('end')==span.get('end')):
            host['source_native_selector'] = {'by':'identifier','value':identifier,
                'proof':{'kind':'SwiftParser-accessibilityIdentifier','file':proof['file'],
                         'line':proof['line'],'start':proof['start'],'end':proof['end']}}
            host['native_locator_status'] = 'requires_live_uniqueness'
        else:
            host['native_locator_status'] = 'requires_native_observation'
            host['native_locator_debt'] = {'reason':'No proved static native locator',
                'source_anchor':anchor,'native_text_expression':component.get('native_text_expression')}
        modified[feature] = host
    for group in intents.get('groups',{}).values():
        for item in group:
            host = modified.get(item.get('feature_path'))
            if not host:
                if item.get('native_locator_scope'):raise MigrationError('Original intent retained stale native locator metadata')
                continue
            old = host['native_analysis_label']
            description = '源控件（分析键 '+str(old)+'；须先在当前原生层级确认定位）'
            item['steps'] = [step.replace('「'+old+'」',description) if isinstance(step,str) and isinstance(old,str) else step
                             for step in item.get('steps',[])]
            for key in LOCATOR:
                item.pop(key,None)
                if key in host:item[key] = copy.deepcopy(host[key])
    return len(modified)


def restore_checks(before, wire, hostmap):
    old = checks(before)
    native = C.native_writeback(before,wire)
    new = checks(native)
    matches,removed=match_checks(old,new)
    for key in removed:
        if has_grounding(old[key]):
            raise MigrationError('Original fold/merge removed an iOS grounding block without proved lineage: '+str(key))
    for key, item in new.items():
        prior = matches[key][1] if key in matches else {}
        if has_grounding(prior):
            block=GT
            for field in block:
                item.pop(field,None)
            for field in block:
                if field in prior:item[field] = copy.deepcopy(prior[field])
        else:
            # The original merge's null placeholders and declaration anchor are
            # static seeds. Any non-null runtime result needs iOS provenance.
            unexpected={k:copy.deepcopy(item[k]) for k in GT-{'ios_anchor','precondition'} if item.get(k) is not None}
            anchor=item.get('ios_anchor')
            if isinstance(anchor,dict):
                extra={k:v for k,v in anchor.items() if k not in {'decl_file','impl_file','raw_identifier'} and v is not None}
                if extra:unexpected['ios_anchor_unproved_fields']=copy.deepcopy(extra)
                item['ios_anchor']={k:v for k,v in anchor.items() if k in {'decl_file','impl_file','raw_identifier'}}
            if unexpected:item['native_unproved_original_oracle']=unexpected
            for field in unexpected:
                if field!='ios_anchor_unproved_fields':item.pop(field,None)
            item['expected_ios'] = None;item['ios_trusted'] = None
        for field,value in prior.items():
            if field not in item and field!='native_unproved_original_oracle' and (field.startswith('native_') or field in LOCATOR):item[field] = copy.deepcopy(value)
        host = hostmap.get(item.get('feature_path'))
        if host and host.get('host_id')==key[0] and host.get('native_locator_scope'):
            item['tap_by'] = host['tap_by'];item['tap_text'] = host['tap_text']
            for field in LOCATOR:
                if field in host:item[field] = copy.deepcopy(host[field])
    return native


def validate_fold_lineage(before, result, report):
    originals=checks(C.legacy_wire(before));pages={p['id']:p for p in C.page_records(result)}
    reported=set()
    for group in report.get('folded_groups',[]):
        page=group.get('page');members=group.get('original_members',[])
        if not members or group.get('member_count')!=len(members):raise MigrationError('Original fold report has inconsistent members')
        for member in members:
            key=scoped_key(page,member)
            if originals.get(key)!=member:raise MigrationError('Original fold report member differs from its actual input')
            reported.add(key)
        candidates=[x for x in pages.get(page,{}).get('functional_checks',[])
                    if x.get('check_kind')=='enum_group_presence' and x.get('feature_path')==group.get('prefix')]
        if len(candidates)!=1:raise MigrationError('Original fold group has no unique presence representative')
        presence=candidates[0]
        expected=[m.get('fp_id') for m in members]
        actual=[m.get('fp_id') for m in presence.get('members',[])]
        if actual!=expected:raise MigrationError('Original fold presence members differ from its reversible report')
        behaviors=[x for x in pages[page].get('functional_checks',[])
                   if x.get('check_kind')=='enum_group_behavior' and x.get('members_ref')==presence.get('fp_id')]
        if len(behaviors)!=1 or behaviors[0].get('representative')!=group.get('representative'):
            raise MigrationError('Original fold behavior representative differs from its lineage')
    dropped=list(report.get('dropped_titles',[]))
    _,removed=match_checks(originals,checks(result))
    for key in removed:
        if key in reported:continue
        member=originals[key]
        if member not in dropped:raise MigrationError('Removed functional check is absent from the original reversible report: '+str(key))
        dropped.remove(member)


def run(command, argv, scripts):
    parser = argparse.ArgumentParser(description=__doc__,add_help=False)
    if command=='compose_registry_from_tree':parser.add_argument('tree',nargs='?',default='spec/toolkit-fact-tree.json')
    elif command=='fold_enum_groups':
        parser.add_argument('tree',nargs='?');parser.add_argument('--write',action='store_true')
        parser.add_argument('--min-group',type=int);parser.add_argument('--no-drop-titles',action='store_true')
    else:
        parser.add_argument('--write',action='store_true');parser.set_defaults(tree='spec/toolkit-fact-tree.json')
    args,unknown = parser.parse_known_args(argv)
    from .route_engine import compiled
    path = Path(args.tree).resolve() if args.tree else None
    before=read_json(path) if path and path.is_file() else None
    if before is None or not C.ios_tree(before):
        process=compiled(scripts,command,argv);return C._emit(process)
    if unknown:raise MigrationError('Unsupported native functional arguments cannot bypass the checked mirror: '+str(unknown))
    before_checks=checks(before)
    project=C._project_for([str(path)])
    C._source_current(before,project)
    guard=C.InputGuard();guard.add(path)
    originals={};absent=set()
    for name in FILES:
        source=project/'spec/a2h'/name
        if source.is_file():guard.add(source);originals[name]=read_json(source)
        else:absent.add(source)
    proven={};selected_source=None;seed_count=0;seeded=before
    root=before.get('native_source_root') or before.get('source',{}).get('ios_root')
    needs_legacy=command!='compose_registry_from_tree' and any('ios_anchor' not in c and 'android_anchor' in c for c in before_checks.values())
    if root and (command=='compose_registry_from_tree' or needs_legacy):
        from .source import Source
        selected_source=Source(root,project if (project/'.migbot/config.json').is_file() else None)
    if command!='compose_registry_from_tree':seeded,seed_count=legacy_static_seeds(before,originals,selected_source)
    if command=='compose_registry_from_tree' and selected_source:
        from .native_routes import analyze
        facts=analyze(selected_source)
        proven={c['id']:c for c in facts['controls']}
    with tempfile.TemporaryDirectory(prefix='hmigbot-native-functional-') as directory:
        work=Path(directory);target=work/'spec/toolkit-fact-tree.json'
        target.parent.mkdir();(work/'spec/a2h').mkdir()
        write_json(target,C.legacy_wire(seeded))
        for name,value in originals.items():write_json(work/'spec/a2h'/name,value)
        prior_contracts={name:(C.sha(work/'spec/a2h'/name),(work/'spec/a2h'/name).stat().st_mtime_ns)
                         for name in originals}
        if command=='compose_registry_from_tree':core_args=[str(target)]
        elif command=='fold_enum_groups':
            core_args=[str(target)]
            if args.write:core_args.append('--write')
            if args.min_group is not None:core_args.extend(['--min-group',str(args.min_group)])
            if args.no_drop_titles:core_args.append('--no-drop-titles')
        else:core_args=list(argv)
        # The original helpers resolve contract paths from cwd, independently
        # of the input tree filename. Keep that original contract in the mirror.
        import subprocess,platform
        arch='arm64' if platform.machine().lower() in {'arm64','aarch64'} else 'x64'
        engine=Path(scripts)/('bin/macos-'+arch+'/_entry.dist/_entry.bin')
        if platform.system()!='Darwin' or not engine.is_file():raise MigrationError('Native functional bridge needs the bundled macOS engine')
        engine_sha=C.sha(engine)
        process=subprocess.run([str(engine),command,*core_args],cwd=work,
            env={**os.environ,'ARKTS_SKILL_DIR':str(Path(scripts).resolve())},capture_output=True,text=True)
        guard.verify()
        if C.sha(engine)!=engine_sha:raise MigrationError('Original functional engine changed during invocation')
        if any(p.exists() for p in absent):raise MigrationError('Functional contract appeared during projection')
        C._source_current(before,project)
        if process.returncode:return C._emit(process)
        outputs={}
        if command=='compose_registry_from_tree':
            generated={}
            for name in FILES:
                file=work/'spec/a2h'/name
                if not file.is_file():raise MigrationError('Original projection did not produce its required contract: '+name)
                state=(C.sha(file),file.stat().st_mtime_ns)
                if name in prior_contracts and state==prior_contracts[name]:
                    raise MigrationError('Original projection did not refresh its prior contract: '+name)
                generated[name]=read_json(file)
            project_locators(before,generated['compose_host_map.json'],generated['test_intents.json'],proven)
            guard.verify()
            outputs={project/'spec/a2h'/name:value for name,value in generated.items()}
            publish(outputs,guard)
        elif args.write:
            result=restore_checks(before,read_json(target),originals.get('compose_host_map.json',{}))
            outputs={path:result}
            if command=='fold_enum_groups':
                report=work/'spec/a2h/_work/fold_enum_report.json'
                if report.is_file():
                    raw_report=read_json(report);validate_fold_lineage(before,result,raw_report)
                    outputs[project/'spec/a2h/_work/fold_enum_report.json']=C.native_writeback({},raw_report)
                elif set(checks(before))-set(checks(result)):
                    raise MigrationError('Original fold removed checks without its reversible report')
            guard.verify();publish(outputs,guard)
        after_checks=checks(read_json(path)) if getattr(args,'write',False) and command!='compose_registry_from_tree' else before_checks
        matching,removed=match_checks(before_checks,after_checks)
        receipt={'entry':command,'engine_sha256':engine_sha,'argv':[str(engine),command,*core_args],
            'cwd':str(work),'inputs_sha256':{str(p):h for p,h in guard.files.items()},
            'exit_code':process.returncode,'stdout':process.stdout,'stderr':process.stderr,
            'outputs_sha256':{str(p):C.sha(p) for p in outputs},
            'before_check_count':len(before_checks),'after_check_count':len(after_checks),
            'legacy_static_anchor_seeds':seed_count,
            'removed_check_keys':[list(k) for k in sorted(removed)],
            'fp_id_changes':[{'key':list(k),'before':prior.get('fp_id'),'after':after_checks[k].get('fp_id')}
                for k,(_,prior) in matching.items() if prior.get('fp_id')!=after_checks[k].get('fp_id')]}
        receipt_path=project/'.hmigbot-ios/cache/native-functional'/(uuid.uuid4().hex+'.json')
        write_json(receipt_path,receipt)
        print('Native functional receipt: '+str(receipt_path),file=sys.stderr)
        return C._emit(process)


def main(command, argv, scripts):
    try:return run(command,argv,scripts)
    except (MigrationError,OSError,ValueError,RuntimeError) as exc:
        print(json.dumps({'status':'error','entry':command,'error':str(exc)},ensure_ascii=False),file=sys.stderr)
        return getattr(exc,'code',2)
