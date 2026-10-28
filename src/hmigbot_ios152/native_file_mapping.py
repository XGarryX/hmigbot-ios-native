"""Native specification ownership at the original HMOS file resolver boundary.

Contracts name a destination; only the retained resolver decides whether it is
unique in the full target file set. No route or device verdict is produced.
"""
from __future__ import annotations
import argparse
import copy
import json
import os
from pathlib import Path
import re
import tempfile

from hmigbot_ios.core import MigrationError, read_json, write_json
from . import native_canonical as C
from .native_routes import analyze
from .native_visual_prepare import declared_paths
from .source import Source

LOCATORS=('file_resolved','parent_file_resolved','parent_used','file_candidates')
COPY_SUFFIXES={'.ets','.ts','.json','.json5','.yaml','.yml','.md'}


def resolution(entry):
    if entry.get('file_resolved'):return 'resolved'
    if entry.get('parent_file_resolved'):return 'via_parent'
    if len(entry.get('file_candidates') or [])>1:return 'ambiguous'
    return 'unfound'


def counts(entries):
    return {kind:sum(resolution(e)==kind for e in entries)
            for kind in ('resolved','via_parent','ambiguous','unfound')}


def declarations(source,facts):
    """Qualify actual SwiftParser types by selected target module membership."""
    members={r['path']:r['targets'] for r in source.selection.get('source_membership',[])} if source.selection else {}
    settings=source.view.artifact.get('settings_targets',{}) if source.view else {}
    result=[]
    for symbol in facts['symbols']:
        modules={settings[t].get('PRODUCT_MODULE_NAME',t) for t in members.get(symbol['file'],[]) if t in settings}
        names={m+'.'+symbol['name'] for m in modules} or {symbol['name']}
        result.extend({**symbol,'fq_class':name} for name in sorted(names))
    return result


def contracts(source,facts,directory,guard):
    symbols=declarations(source,facts);result={};issues=[]
    page_symbols={(r['file'],r['name']) for r in facts['pages']}
    for file in sorted(Path(directory).glob('page_*.md')):
        guard.add(file);text=file.read_text(encoding='utf-8-sig')
        outputs=re.findall(r'^- 输出文件:\s*(.+?)\s*$',text,re.M)
        if len(outputs)!=1:continue
        output=outputs[0]
        if output.startswith('`'):
            quoted=re.fullmatch(r'`([^`]+)`',output)
            if not quoted:continue
            output=quoted[1]
        destination=Path(output)
        if destination.is_absolute() or '..' in destination.parts or destination.suffix!='.ets':
            issues.append({'spec':str(file),'reason':'invalid declared output path'});continue
        try:anchors=declared_paths(text,source)
        except MigrationError as exc:
            issues.append({'spec':str(file),'reason':str(exc)});continue
        fields=re.findall(r'^- iOS (?:页面/系统表面|页面):\s*(.+)$',text,re.M)
        method='surface_field'
        if fields:
            tokens=re.split(r'[,，、]',re.split(r'[;；]',fields[0],maxsplit=1)[0].strip()) if len(fields)==1 else []
            tokens=[t.strip().strip('`') for t in tokens]
            if not tokens or any(not re.fullmatch(r'[^\W\d]\w*(?:\.[^\W\d]\w*)*',t) for t in tokens):
                issues.append({'spec':str(file),'reason':'ambiguous surface field'});continue
            owners=[]
            for token in tokens:
                exact=[s for s in symbols if (s['fq_class']==token if '.' in token else s['name']==token)]
                if len(exact)!=1 or str(source.root/exact[0]['file']) not in anchors:
                    owners=[];break
                owners.append(exact[0])
        else:
            method='file_only_unique_owner'
            owners=[s for s in symbols if (s['file'],s['name']) in page_symbols and str(source.root/s['file']) in anchors]
            if len(owners)!=1:owners=[]
        if not owners:
            issues.append({'spec':str(file),'reason':'no unique current Source owner declared by this contract'});continue
        for owner in owners:
            row={'owner':owner['fq_class'],'source_file':owner['file'],'source_line':owner['line'],
                 'source_file_sha256':C.sha(source.root/owner['file']),'spec':str(file),'spec_sha256':C.sha(file),
                 'output':destination.as_posix(),'method':method}
            result.setdefault(owner['fq_class'],[]).append(row)
    return result,issues


def contract_for(page,contracts,symbols):
    identity=page.get('fq_class') or page['id']
    if '.' not in identity:
        owners={(s['fq_class'],s['file'],s['line']) for s in symbols if s['name']==identity}
        if len(owners)!=1:return None
    rows=contracts.get(identity,[])
    # Unqualified records are accepted only when they identify one real owner.
    if not rows and '.' not in (page.get('fq_class') or page['id']):
        rows=[r for owner,values in contracts.items() if owner.split('.')[-1]==(page.get('fq_class') or page['id']) for r in values]
    return rows[0] if len(rows)==1 else None


def _project_files(project):
    # Keep every ETS, including conflicts in any module; do not invent the
    # opaque resolver's directory-exclusion algorithm in this adapter.
    result={}
    for directory,dirs,names in os.walk(project):
        dirs[:]=[d for d in dirs if not (Path(directory)/d).is_symlink()]
        for name in names:
            file=Path(directory)/name
            if file.is_symlink() or file.suffix not in COPY_SUFFIXES:continue
            result[file.relative_to(project).as_posix()]=C.sha(file)
    return result


class OriginalQueueFailure(Exception):
    def __init__(self,process):self.process=process


def mapped_queue(tree_path,project,scripts,*,source=None):
    project=Path(project).resolve();tree_path=Path(tree_path).resolve()
    tree=read_json(tree_path);C._source_current(tree,project)
    guard=C.InputGuard();guard.add(tree_path)
    source=source or C._blackbox_source(tree,project)
    facts=analyze(source)
    symbols=declarations(source,facts)
    for name in source.files:guard.add(source.root/name)
    declared,issues=contracts(source,facts,project/'spec/baseline/ui',guard)
    inventory=_project_files(project)
    for name in inventory:guard.add(project/name)
    records={p['id']:p for p in C.page_records(tree)};proof=[];used={};runs=[]
    with tempfile.TemporaryDirectory(prefix='native-queue-contract-') as directory:
        root=Path(directory)/'project';root.mkdir()
        for name in inventory:
            dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((project/name).read_bytes())
        input_path=root/'spec/.native-file-map-input.json';output=Path(directory)/'queue.json'
        def run(value):
            write_json(input_path,value)
            guard.verify()
            process=C._core('build_page_queue',['--tree',str(input_path),'--out',str(output)],scripts,cwd=root)
            runs.append({'command':'build_page_queue','tree_sha256':C.sha(input_path),
                         'exit_code':process.returncode,'stdout':process.stdout.replace(str(root),str(project)),
                         'stderr':process.stderr.replace(str(root),str(project))})
            guard.verify()
            if process.returncode:raise OriginalQueueFailure(process)
            if not output.is_file():raise MigrationError('Original queue core produced no output')
            result=read_json(output);result['generated_from']=str(tree_path)
            if counts(result['entries'])!={k:result['path_resolution'][k] for k in counts(result['entries'])}:
                raise MigrationError('Original queue resolution statistics could not be reproduced')
            return result
        base=run(tree);result=copy.deepcopy(base);by_name={r['name']:r for r in result['entries']}
        def probe(page,contract,parent=None):
            alias=Path(contract['output']).stem;owner=parent or page
            if alias in records and alias!=owner['id']:
                proof.append({'node':page['id'],'reason':'projected output stem collides with a current node'});return None
            value=copy.deepcopy(tree)
            keep={page['id'],owner['id']}
            for family in ('pages','fragments','dialogs'):
                value[family]=[r for r in value.get(family,[]) if r['id'] in keep]
            before=run(value)
            old=next(e for e in before['entries'] if e['name']==page['id'])
            if old!=next(e for e in base['entries'] if e['name']==page['id']):
                proof.append({'node':page['id'],'reason':'minimal input slice changes original entry semantics'});return None
            if parent:
                parent_before=next(e for e in before['entries'] if e['name']==parent['id'])
                if parent_before!=next(e for e in base['entries'] if e['name']==parent['id']):
                    proof.append({'node':page['id'],'reason':'minimal parent slice changes original entry semantics'});return None
            for key in ('launcher_short','launcher_activity'):
                if value.get('app',{}).get(key)==owner['id']:value['app'][key]=alias
            for record in C.page_records(value):
                if record['id']==owner['id']:record['id']=alias
                for edge in record.get('navigation',{}).get('inbound',[]):
                    if edge.get('from')==owner['id']:edge['from']=alias
            after=run(value)
            row=next(e for e in after['entries'] if e['name']==(page['id'] if parent else alias))
            row=copy.deepcopy(row);row['name']=page['id']
            for field in ('host_page','parent_used'):
                if row.get(field)==alias:row[field]=owner['id']
            row['triggered_by']=[owner['id'] if v==alias else v for v in row.get('triggered_by',[])]
            fixed=copy.deepcopy(row)
            for field in LOCATORS:
                if field in old:fixed[field]=old[field]
                else:fixed.pop(field,None)
            if fixed!=old:
                proof.append({'node':page['id'],'reason':'probe changes fields beyond file location'});return None
            state=resolution(row);expected=contract['output']
            accepted=(state=='via_parent' and row.get('parent_used')==owner['id'] and row.get('parent_file_resolved')==expected) if parent else (state=='resolved' and row.get('file_resolved')==expected)
            if not parent and state=='ambiguous' and expected in (row.get('file_candidates') or []):
                accepted=True
            proof.append({'node':page['id'],'parent':owner['id'] if parent else None,'kind':'contract_probe',
                          'contract':contract,'state':state,'accepted':accepted,'before':old,'after':row})
            return row if accepted else None
        for row in result['entries']:
            if resolution(row)!='unfound':continue
            page=records[row['name']]
            if (page.get('native_declared_type') is False or
                    page['id'] in facts['modals'] and page['id'] not in {s['name'] for s in facts['symbols']}):
                continue  # An inline presentation's fq_class is its owner, not a new type.
            contract=contract_for(page,declared,symbols)
            if not contract:continue
            resolved=probe(page,contract)
            if resolved:
                for field in LOCATORS:
                    if field in resolved:row[field]=resolved[field]
                if resolution(row)=='resolved':used[page['id']]=contract
        for row in result['entries']:
            if resolution(row)!='unfound':continue
            page=records[row['name']]
            for edge in page.get('navigation',{}).get('inbound',[]):
                parent=edge.get('from')
                if parent not in used:continue
                resolved=probe(page,used[parent],records[parent])
                if resolved:
                    for field in LOCATORS:
                        if field in resolved:row[field]=resolved[field]
                    break
        result['path_resolution'].update(counts(result['entries']))
        for before,after in zip(base['entries'],result['entries'],strict=True):
            conserved=copy.deepcopy(after)
            for field in LOCATORS:
                if field in before:conserved[field]=before[field]
                else:conserved.pop(field,None)
            if conserved!=before:raise MigrationError('Native file mapping changed queue identity or non-location fields')
        other=copy.deepcopy(result);other['entries']=base['entries'];other['path_resolution']=base['path_resolution']
        if other!=base:raise MigrationError('Native file mapping changed original queue accounting')
    guard.verify()
    if inventory!=_project_files(project):raise MigrationError('Target project file inventory changed during queue mapping')
    receipt={'schema':'native-file-mapping.v1','source_sha256':facts['source_sha'],
             'tree_sha256':C.sha(tree_path),'target_ets':{n:s for n,s in inventory.items() if n.endswith('.ets')},
             'projection_inventory_sha256':C._json_digest(inventory),
             'source_files':{n:C.sha(source.root/n) for n in source.files},
             'classifier_sha256':C.sha(Path(__file__)),'core_runs':runs,
             'native_path_resolution':base['path_resolution'],'final_path_resolution':result['path_resolution'],
             'contracts':proof,'unresolved_contracts':issues,
             'note':'Contract-declared mapping with original resolver uniqueness check; no route/device verdict'}
    return result,receipt


def queue_cli(argv,scripts):
    parser=argparse.ArgumentParser(description='Original queue with native specification file contracts')
    parser.add_argument('--tree',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args(argv);tree=Path(args.tree).resolve();project=C._project_for(argv)
    try:result,receipt=mapped_queue(tree,project,scripts)
    except OriginalQueueFailure as exc:return C._emit(exc.process)
    out=Path(args.out).resolve()
    if out==tree:raise MigrationError('Queue output cannot replace its fact tree')
    write_json(out.with_name(out.name+'.native-mapping.json'),receipt);write_json(out,result)
    print(json.dumps({'queue':str(out),'native_path_resolution':receipt['native_path_resolution'],
                      'path_resolution':result['path_resolution'],'source_platform':'ios'},ensure_ascii=False));return 0


def batch_rows(value):
    """Read retained v4 trip groups or the legacy flat batch layout."""
    flat='batches' in value;nested='trips' in value
    if flat==nested or nested and value.get('schema_version')!='v4-batches/1':
        raise MigrationError('Unsupported or mixed native batch layout')
    groups=value['trips'] if nested else [{'trip_id':'legacy_flat','batches':value['batches']}]
    if not isinstance(groups,list):raise MigrationError('Native batch groups must be a list')
    for group in groups:
        if not isinstance(group,dict) or not isinstance(group.get('batches'),list):
            raise MigrationError('Malformed native trip batch group')
        trip=group.get('trip_id')
        if not isinstance(trip,str) or not trip:raise MigrationError('Native batch trip identity is missing')
        for batch in group['batches']:
            if not isinstance(batch,dict) or not isinstance(batch.get('pages'),list):
                raise MigrationError('Malformed native batch pages')
            for page in batch['pages']:
                if not isinstance(page,dict):raise MigrationError('Native batch page must be an object')
                if page.get('name') and page.get('page_id') and page['name']!=page['page_id']:
                    raise MigrationError('Conflicting native batch page identity')
                yield trip,page


def batches_cli(argv,scripts):
    """Keep original batch gates/grouping; only supply verified file locations."""
    if any(arg in {'-h','--help'} for arg in argv):
        return C._emit(C._core('build_batches',argv,scripts,cwd=Path.cwd()))
    code=C.data_cli('build_batches',argv,scripts)
    if code:return code
    path=Path(C._option(argv,'--out')).resolve()
    before=read_json(path);old_rows=list(batch_rows(before))
    tree=Path(C._option(argv,'--fact-tree')).resolve();project=C._project_for(argv)
    try:queue,receipt=mapped_queue(tree,project,scripts)
    except OriginalQueueFailure as exc:return C._emit(exc.process)
    after=copy.deepcopy(before);entries={e['name']:e for e in queue['entries']}
    changed=0;by_trip={};matched=0
    for trip,page in batch_rows(after):
        counts=by_trip.setdefault(trip,{'rows':0,'matched':0,'location_fields_changed':0,'unmatched':[]});counts['rows']+=1
        name=page.get('page_id') or page.get('name');entry=entries.get(name)
        if entry is None:counts['unmatched'].append(name);continue
        matched+=1;counts['matched']+=1
        if resolution(page)!='unfound':continue
        state=resolution(entry)
        fields=LOCATORS if state in {'resolved','via_parent'} else ('file_candidates',) if state=='ambiguous' else ()
        for field in fields:
            if field in entry and page.get(field)!=entry[field]:
                page[field]=copy.deepcopy(entry[field]);changed+=1;counts['location_fields_changed']+=1
    if old_rows and not matched:raise MigrationError('Native batch rows have no queue identity matches')
    restored=copy.deepcopy(after)
    for (trip,old),(other,new) in zip(old_rows,batch_rows(restored),strict=True):
        if trip!=other:raise MigrationError('Native batch trip order changed')
        for field in LOCATORS:
            if field in old:new[field]=old[field]
            else:new.pop(field,None)
    if restored!=before:raise MigrationError('Native file mapping changed batch membership, identity or gates')
    receipt.update(batch_input_sha256=C.sha(path),batch_location_fields_changed=changed,batch_rows_by_trip=by_trip)
    write_json(path.with_name(path.name+'.native-mapping.json'),receipt);write_json(path,after)
    print(json.dumps({'native_batch_file_mapping':str(path),'location_fields_changed':changed}));return 0
