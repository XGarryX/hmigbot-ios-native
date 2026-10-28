"""Native source data for original visual preparation; no device actions."""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import re
import tempfile
import uuid
import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError

from hmigbot_ios.core import MigrationError, read_json, write_json
from . import native_canonical as C
from .native_routes import analyze, SwiftFile, _xml_spans
from .source import Source


def original_enrich(argv,scripts,work):
    from .compiled_runtime import execute
    process=execute('enrich_factree_anchors',list(map(str,argv)),scripts,cwd=work,capture_output=True,text=False,
                    env={'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'})
    process.stdout=process.stdout.decode('utf-8');process.stderr=process.stderr.decode('utf-8')
    return process


def failed_original(process):
    print(json.dumps({'status':'original_anchor_failure','exit_code':process.returncode,
                      'argv':process.args,'stdout':process.stdout,'stderr':process.stderr}))
    return process.returncode


def checked_source(root, project):
    source=Source(root,project)
    for name in sorted(source.files):
        if name.endswith('.swift') and source.syntax(name).get('diagnostics'):
            raise MigrationError('SwiftParser diagnostics prevent native preparation: '+name)
    return source,analyze(source)


def same_source(source, facts):
    _,current=checked_source(source.root,source.project)
    if current['source_sha']!=facts['source_sha']:
        raise MigrationError('Selected native source changed during visual preparation')


def native_catalog(source, facts, package):
    resource_scope=facts.get('resource_scope')
    if (not isinstance(resource_scope,dict) or not isinstance(resource_scope.get('files'),list) or
            resource_scope.get('scope') not in {'selected-product-targets','explicit-source-root-no-product-selection'}):
        raise MigrationError('Native modal catalog requires a computed resource scope')
    controls={c['id']:c for c in facts['controls']};roles={};unsupported=[]
    modal_apis={'sheet','fullScreenCover','alert','confirmationDialog','popover',
                'UIAlertController','present','presentViewController'}
    known={(r['source_file'],r['evidence_line'],r['via']) for r in facts['routes']
           if r.get('target') in facts['modals'] and r.get('target_type')=='dialog'}
    for name in sorted(source.files):
        if name.endswith(('.m','.mm')):
            unsupported.append({'file':name,'line':1,'reason':'Objective-C modal analysis is not implemented'})
        if not name.endswith('.swift'):continue
        file=SwiftFile(source,name)
        for node in file.nodes:
            if node['kind']!='call':continue
            value=node['value'];api=value.get('callee_name')
            if api=='Button':
                expression=next((a['expression'] for a in value['arguments'] if a['label']=='role'),None)
                roles[(name,node['start'],node['end'])]=expression
            if api in modal_apis:
                span=file.span(value['callee_name_span']) if value.get('callee_name_span') else file.span(node)
                if (name,span['line'],api) not in known:
                    unsupported.append({'file':name,'line':span['line'],'api':api,
                                        'reason':'Presentation call has no modeled native modal'})
    for route in facts['routes']:
        if route.get('target_type')=='dialog' and route.get('target') not in facts['modals']:
            unsupported.append({'file':route['source_file'],'line':route['evidence_line'],
                                'api':route['via'],'reason':route.get('unknown_reason','Unmodeled modal destination')})
    for name in resource_scope['files']:
        if Path(name).suffix not in {'.storyboard','.xib'} or (source.view and not source.view.includes(name)):continue
        raw=(source.root/name).read_bytes()
        try:
            spans,_=_xml_spans(raw,name);document=ET.fromstring(raw)
        except (ET.ParseError,ExpatError,UnicodeError) as exc:
            raise MigrationError('Invalid Interface Builder document '+name) from exc
        for element in document.iter('segue'):
            kind=element.get('kind');span=spans.get(element.get('id'))
            if kind not in {'presentation','popoverPresentation','custom'}:continue
            modeled=span and any(r.get('via')=='storyboard.segue' and r.get('source_file')==name and
                r.get('start')==span['start'] and r.get('target') in facts['modals'] for r in facts['routes'])
            if kind=='custom' or not modeled:
                unsupported.append({'file':name,'line':span['line'] if span else 1,'line_is_file_scope':not bool(span),
                                    'api':'storyboard.segue','kind':kind,'reason':'IB modal/custom segue requires source adjudication'})
    dialogs={}
    for name,modal in facts['modals'].items():
        rows=[]
        if modal.get('unsupported_content'):
            unsupported.append({'file':modal['file'],'line':modal['native_content_span']['line'],
                                'reason':modal['unsupported_content']})
        for item in modal['controls']:
            full=controls.get(item['id'],{})
            expression=roles.get((full.get('file'),full.get('start'),full.get('end')))
            role=('cancel' if expression in {'.cancel','ButtonRole.cancel','SwiftUI.ButtonRole.cancel'} else
                  'destructive' if expression in {'.destructive','ButtonRole.destructive','SwiftUI.ButtonRole.destructive'} else None)
            identifier=full.get('accessibility_identifier')
            rows.append({'analysis_key':item['id'],'type':item['tag'],
                         'declared_text_literal_or_key':item.get('text'),
                         'declared_accessibility_label':full.get('accessibility_label'),
                         'source_role':role,'source_role_expression':expression,
                         'selector_candidate':({'identifier':identifier} if isinstance(identifier,str) and identifier else None),
                         'requires_live_uniqueness':True,'runtime_verified':False,
                         'source_anchor':{k:full.get(k,item.get(k)) for k in ('file','line','start','end')}})
        dialogs[name]={'api':modal.get('api','storyboard.segue'),'source_file':modal['file'],
                       'source_span':modal['native_content_span'] if modal.get('api') else None,'controls':rows,
                       'presentation_sites':[{k:r.get(k) for k in ('via','source_file','evidence_line','api_span','state_binding')}
                                             for r in facts['routes'] if r.get('target')==name and r.get('target_type')=='dialog'],
                       'automatic_dismiss_allowed':False}
    # Multiple routes may diagnose the same unresolved call; preserve distinct facts.
    unsupported=list({json.dumps(x,sort_keys=True):x for x in unsupported}.values())
    return {'schema_version':'native-dialog-catalog/1','source_platform':'ios',
            'ios_root':str(source.root),'package':package,'source_sha256':facts['source_sha'],
            'source_context':facts['context'],'selected_products':facts.get('selected_products',[]),
            'source_input_identity':facts.get('input_identity'),
            'static_only':True,'runtime_verified':False,'automatic_dismiss_allowed':False,
            'status':'partial_unknowns' if unsupported else 'complete',
            'matched_dialogs':len(dialogs),'dialogs':dialogs,'unsupported_constructs':unsupported}


def catalog_cli(argv):
    p=argparse.ArgumentParser(description='Static native modal declarations for live Xcode orchestration')
    p.add_argument('--ios-root',required=True);p.add_argument('--package',required=True);p.add_argument('--out',required=True)
    p.add_argument('--project-root');p.add_argument('--layout-pattern')
    args=p.parse_args(argv)
    if args.layout_pattern is not None:raise MigrationError('--layout-pattern is Android XML only')
    output=Path(args.out).resolve()
    if output.name=='dialog_id_catalog.json':
        raise MigrationError('Native catalog requires native_dialog_catalog.json; the legacy filename belongs to Android consumers')
    source,facts=checked_source(args.ios_root,C._project_for(argv))
    result=native_catalog(source,facts,args.package)
    legacy=output.parent/'dialog_id_catalog.json'
    result['ignored_legacy_catalog']=({'path':str(legacy),'sha256':C.sha(legacy)} if legacy.is_file() else None)
    same_source(source,facts);write_json(output,result)
    print(json.dumps({'out':str(output),'status':result['status'],'matched_dialogs':result['matched_dialogs'],
                      'unsupported_constructs':len(result['unsupported_constructs']),'runtime_verified':False}))
    return 0


def refs_result(before,wire,source,declared=None):
    """Accept only the measured original producer's file-reference changes."""
    original=copy.deepcopy(before);expected=copy.deepcopy(wire);result=copy.deepcopy(before);unmatched=[]
    for key in ('pages','fragments','dialogs'):
        if len(original.get(key,[]))!=len(expected.get(key,[])):
            raise MigrationError('Original anchor producer changed the node set')
        for old,new,out in zip(original.get(key,[]),expected.get(key,[]),result.get(key,[])):
            refs=new.pop('android_source_refs',None);old.pop('android_source_refs',None)
            out.pop('android_source_refs',None)
            out.pop('ios_source_refs',None)
            if refs is None:
                unmatched.append(out['id']);continue
            if not isinstance(refs,list):raise MigrationError('Unexpected original reference shape')
            for ref in refs:
                if not isinstance(ref,str):raise MigrationError('Original references must be plain file paths, without unverified lines')
                path=Path(ref).resolve()
                if not path.is_relative_to(source.root) or path.relative_to(source.root).as_posix() not in source.files:
                    raise MigrationError('Original source reference is outside selected native code: '+ref)
                if declared is not None and str(path) not in declared.get((key,out['id']),set()):
                    raise MigrationError('Original reference is not declared by a matching page specification: '+ref)
            out['ios_source_refs']=refs
            if not refs:unmatched.append(out['id'])
    if original!=expected:raise MigrationError('Original anchor producer changed fields other than source references')
    return result,unmatched


def anchor_header(text):
    prefix=re.split(r'(?m)^##\s',text,maxsplit=1)[0]
    matches=list(re.finditer(r'(?m)^(source_anchors|android_source_anchors)([ \t]*:)',prefix))
    if len(matches)>1:raise MigrationError('Ambiguous top source anchor maps')
    return prefix,matches[0] if matches else None


def declared_paths(text,source):
    """Read only the template's top file-level string map, without interpreting prose."""
    prefix,match=anchor_header(text)
    if match is None:return set()
    lines=prefix.splitlines();start=prefix[:match.start()].count('\n')
    suffix=lines[start].split(':',1)[1].strip()
    if suffix and not suffix.startswith('#') and suffix!='{}':raise MigrationError('Unsupported inline source anchor map')
    result=set()
    for line in lines[start+1:]:
        if not line.strip() or line.lstrip().startswith('#'):continue
        if not line[0].isspace():break
        match=re.match(r'^\s+[^:]+:\s*(.*?)\s*$',line)
        if not match:raise MigrationError('Unsupported source anchor mapping entry')
        value=match[1]
        if value.startswith('"'):
            literal=value
            try:value,end=json.JSONDecoder().raw_decode(literal)
            except ValueError as exc:raise MigrationError('Invalid quoted source anchor') from exc
            if literal[end:].strip() and not literal[end:].lstrip().startswith('#'):
                raise MigrationError('Unsupported source anchor suffix')
            if not isinstance(value,str):raise MigrationError('Source anchors must be file path strings')
        elif value.startswith("'"):
            quoted=re.match(r"^'((?:[^']|'')*)'(?:\s*#.*)?$",value)
            if not quoted:raise MigrationError('Invalid quoted source anchor')
            value=quoted[1].replace("''", "'")
        else:value=value.split(' #',1)[0].strip()
        if not value:raise MigrationError('Empty source anchor file path')
        path=(source.root/value).resolve()
        if not path.is_relative_to(source.root) or path.relative_to(source.root).as_posix() not in source.files:
            raise MigrationError('Declared anchor is outside selected native code: '+value)
        result.add(str(path))
    return result


def enrich_cli(argv,scripts):
    p=argparse.ArgumentParser(description='Original anchor matching with native source field projection')
    p.add_argument('--fact-tree',default='spec/toolkit-fact-tree.json')
    p.add_argument('--page-spec-dir',default='spec/baseline/ui')
    p.add_argument('--also-draft',default='spec/.cache/fact-tree/draft.json')
    p.add_argument('--project-root')
    p.add_argument('--receipt');args=p.parse_args(argv)
    project=C._project_for([*argv,'--tree',args.fact_tree]);tree_path=Path(args.fact_tree).resolve()
    tree=read_json(tree_path);C._source_current(tree,project)
    root=tree.get('native_source_root') or tree.get('source',{}).get('ios_root')
    if not root:raise MigrationError('Native anchor enrichment requires the selected iOS source root')
    source,facts=checked_source(root,project);guard=C.InputGuard();guard.add(tree_path)
    config=project/'.migbot/config.json'
    if config.is_file():guard.add(config)
    documents=Path(args.page_spec_dir).resolve();members=list(documents.glob('page_*.md'))
    for file in members:guard.add(file)
    paths=[tree_path];draft=Path(args.also_draft).resolve()
    if draft.is_file() and draft!=tree_path:guard.add(draft);paths.append(draft)
    if not members:print('WARN: no native page specifications; original empty-reference behavior retained',file=__import__('sys').stderr)
    outputs={};receipts=[];declarations={}
    with tempfile.TemporaryDirectory(prefix='hmigbot-native-anchors-') as temporary:
        work=Path(temporary);specs=work/'ui';specs.mkdir()
        for file in members:
            text=file.read_bytes().decode('utf-8-sig')
            declarations[file.name]=declared_paths(text,source)
            # Only the field line changes; values and prose remain original input.
            _,header=anchor_header(text)
            if header and header[1]=='source_anchors':
                text=text[:header.start(1)]+'android_source_anchors'+text[header.end(1):]
            (specs/file.name).write_bytes(text.encode('utf-8'))
        for index,path in enumerate(paths):
            before=read_json(path)
            if path==tree_path or 'source' in before:C._source_current(before,project)
            elif before.get('native_source_root') or before.get('native_source_sha256'):
                raise MigrationError('Draft contains incomplete native source provenance')
            mirror=copy.deepcopy(before);mirror.setdefault('source',{})['android_root']=str(source.root)
            for node in C.page_records(mirror):
                node.pop('android_source_refs',None)
                node.pop('ios_source_refs',None)
            target=work/(str(index)+'.json');write_json(target,mirror)
            declared={};matched_specs={};probes=[]
            # Ask the original matcher which nodes each spec belongs to. This
            # provides provenance without reimplementing its class/name rules.
            for number,file in enumerate(members):
                single=work/('single-'+str(index)+'-'+str(number));single.mkdir()
                (single/file.name).write_bytes((specs/file.name).read_bytes())
                probe=copy.deepcopy(mirror)
                for node in C.page_records(probe):node.pop('android_source_refs',None)
                probe_path=single/'tree.json';write_json(probe_path,probe)
                measured=original_enrich(['--fact-tree',str(probe_path),'--page-spec-dir',str(single),
                                         '--also-draft',str(work/'absent-draft.json')],scripts,work)
                if measured.returncode:return failed_original(measured)
                observed=read_json(probe_path)
                # Every per-spec probe is subject to the same complete diff guard.
                refs_result(probe,observed,source)
                claimed=[]
                for collection in ('pages','fragments','dialogs'):
                    for node in observed.get(collection,[]):
                        if node.get('android_source_refs'):
                            if any(str(Path(ref).resolve()) not in declarations[file.name] for ref in node['android_source_refs']):
                                raise MigrationError('Original per-spec reference was not declared in that specification')
                            identity=(collection,node['id'])
                            if identity in declared:raise MigrationError('Multiple page specifications claim the same native node: '+node['id'])
                            declared.setdefault(identity,set()).update(declarations[file.name])
                            matched_specs.setdefault(node['id'],[]).append(file.name)
                            claimed.append(node['id'])
                probes.append({'spec':str(file),'spec_sha256':C.sha(file),'argv':measured.args,
                               'exit_code':measured.returncode,'stdout':measured.stdout,'stderr':measured.stderr,
                               'matched_nodes':claimed,'refs_only_diff_verified':True})
            wire_before_sha256=C.sha(target)
            process=original_enrich(['--fact-tree',str(target),'--page-spec-dir',str(specs),
                                     '--also-draft',str(work/'absent-draft.json')],scripts,work)
            record={'canonical':str(path),'exit_code':process.returncode,'stdout':process.stdout,'stderr':process.stderr}
            record.update(argv=process.args,wire_before_sha256=wire_before_sha256,wire_after_sha256=C.sha(target),matching_probes=probes)
            receipts.append(record)
            if process.returncode:return failed_original(process)
            changed=read_json(target);result,unmatched=refs_result(mirror,changed,source,declared)
            # Restore the canonical source object; only source reference fields may change.
            if 'source' in before:result['source']=before['source']
            else:result.pop('source',None)
            outputs[path]=result
            record.update(enriched=sum(bool(n.get('ios_source_refs')) for n in C.page_records(result)),
                          unmatched=unmatched,matched_specs=matched_specs)
        same_source(source,facts);guard.verify()
        from .native_functional import publish
        publish(outputs,guard)
        receipt={'schema':'native-visual-anchors/1','source_sha256':facts['source_sha'],'inputs':guard.files,'runs':receipts,
                 'original_io_environment':{'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'},
                 'outputs':{str(path):C.sha(path) for path in outputs},'runtime_verified':False}
        destination=Path(args.receipt) if args.receipt else project/'.hmigbot-ios/cache/native-visual-prepare'/(uuid.uuid4().hex+'.json')
        receipt['inputs']={str(k):v for k,v in receipt['inputs'].items()};write_json(destination,receipt)
    print(json.dumps({'receipt':str(destination),'runs':[{k:r[k] for k in ('canonical','enriched','unmatched')} for r in receipts]}))
    return 0
