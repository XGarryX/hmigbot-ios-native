"""Native indexed structural consumers backed by the bundled real detectors.

The original compiled loop cannot accept profile-2 ownership or provider calls.
This adapter runs the actual original audit and C1/C3/C4 detector, applies a
bounded native C2 proof, then asks the original loop_runner for its verdict.
No reviewed plan, product, scheduler or scheduler ledger is rewritten.
"""
from __future__ import annotations

import importlib.util
from dataclasses import asdict
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from .core import MigrationError, digest, read_json, safe_child, write_json
from .native_structural_evidence import EvidenceIndex, SKIP
from .plan_contract import _projection

ROOT = Path(__file__).resolve().parents[2]
CATEGORIES = ('C1_orphan_check','C2_integration_point','C3_cross_slice','C4_parent_replacement')
HEADER = re.compile(r'^##\s+Slice\s+(\d+)\s*[:：]\s*(.+?)\s+\((F\d+)\)\s*$', re.M)
ITEM = re.compile(r'^(?:BASE:Base-\d+(?:\.\d+)?|UI:PAGE-\d{4}|SLICE:F\d+:3[a-d])$')


def enabled(project):
    path = Path(project) / '.migbot/config.json'
    if not path.is_file(): return False
    config = read_json(path)
    return config.get('source_platform') == 'ios' and config.get('ios_harness',{}).get('spec_contract_version',1) == 2


def _parser():
    name = '_hmigbot_original_structural_plan'
    if name not in sys.modules:
        path = ROOT / 'vendor/hmigbot/skills/arkts-structural-closure/scripts/plan_lib/feature_plan_parser.py'
        spec = importlib.util.spec_from_file_location(name,path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _files(project, paths, *, product_ownership=False):
    result=[]
    for relative in paths:
        path=safe_child(project,relative)
        parts=Path(relative).parts
        if (any(part in SKIP or part.startswith('.') for part in parts)
                or parts[0] in {'spec','work'}):
            raise MigrationError('Structural scope requires an actual product file: '+relative)
        if path.suffix != '.ets' and not product_ownership:
            raise MigrationError('Structural code scope requires a product ETS file: '+relative)
        if not path.is_file(): raise MigrationError('Structural scope file is missing: '+relative)
        result.append(relative)
    return sorted(set(result))


def _declarative_contracts(project, detail, content, label, keys, optional=()):
    """Read one explicit native binding list without inventing missing entries."""
    from .spec_contract import references
    starts=list(re.finditer(r'^'+re.escape(label)+r'[ \t]*:',content,re.M))
    if not starts: return []
    if len(starts)!=1: raise MigrationError('Duplicate '+label+' block')
    block=re.match(re.escape(label)+r'[ \t]*:[ \t]*([^\n]*)\n((?:[ \t]+[^\n]*(?:\n|$))*)',content[starts[0].start():])
    if block is None or block[1].strip(): raise MigrationError('Unsupported '+label+' syntax')
    entries=[]; current=None
    for line in block[2].splitlines():
        if not line.strip(): continue
        match=re.fullmatch(r'(  - |    )([a-z_]+):[ \t]*(.+)',line)
        if not match: raise MigrationError('Unsupported '+label+' field syntax')
        prefix,key,value=match.groups()
        if prefix=='  - ':
            if key!='owner': raise MigrationError(label+' item must start with owner')
            current={}; entries.append(current)
        if current is None or key not in set(keys)|set(optional) or key in current:
            raise MigrationError('Unknown or duplicate '+label+' field: '+key)
        if value.startswith('"'): value=json.loads(value)
        if not isinstance(value,str) or not value or value.startswith("'"):
            raise MigrationError(label+' fields require unambiguous nonempty strings')
        current[key]=value
    if not entries or any(not set(keys)<=set(entry) for entry in entries):
        raise MigrationError('Incomplete '+label+' responsibility')
    owners={item['item_id'] for item in _projection(project,detail)}
    seen=set()
    for entry in entries:
        identity=json.dumps(entry,sort_keys=True)
        if identity in seen or entry['owner'] not in owners:
            raise MigrationError('Duplicate or foreign '+label+' responsibility')
        seen.add(identity)
        references(project,detail,'contract_refs: '+json.dumps([entry['input']],ensure_ascii=False))
    return entries


def _component_definition(definition):
    if definition.kind!='struct': return False
    values=definition.source.values
    for index in range(definition.start-1,-1,-1):
        if values[index]=='struct':
            prefix=values[max(0,index-5):index]
            return any(prefix[position:position+2] in [['@','Component'],['@','ComponentV2']]
                       for position in range(len(prefix)-1))
        if values[index] in {';','}'}: break
    return False


def _adapt_direct_build_embeds(selection, evidence, category):
    """Only the original missing-@Builder/build case has a native alternative."""
    contracts=selection['embed_bindings']; details=[]
    for contract in contracts:
        parent=re.fullmatch(r'([A-Za-z_$][\w$]*)\.build',contract['parent'])
        if parent is None or contract['kind']!='direct_declarative_child':
            raise MigrationError('Unsupported direct declarative embed contract')
        matches=[]
        for original in category['details']:
            if original.get('builder_name')!='build' or original.get('replace_with')!=contract['child']+'()': continue
            relative=original.get('parent_file','').replace('\\','/')
            definitions=[definition for definition in evidence.definitions if definition.name==parent[1]
                         and definition.source.relative==relative]
            resolve=re.fullmatch(r'Slice '+str(selection['slice_id'])+r' Step (3[a-d])',original.get('resolve_by',''))
            if len(definitions)==1 and resolve and contract['owner']=='SLICE:'+selection['feature_id']+':'+resolve[1]:
                matches.append(original)
        if len(matches)!=1:
            raise MigrationError('Direct embed contract must match exactly one original authored wire')
    for original in category['details']:
        detail={**original,'original_evidence':original}
        if original.get('status')!='FAIL' or original.get('failed_check')!='C4_BUILDER_NOT_FOUND' or original.get('builder_name')!='build':
            details.append(detail); continue
        child_match=re.fullmatch(r'([A-Za-z_$][\w$]*)\(\)',original.get('replace_with',''))
        relative=original.get('parent_file','').replace('\\','/')
        parents=[definition for definition in evidence.definitions if definition.source.relative==relative
                 and _component_definition(definition)]
        if len(parents)!=1 or child_match is None:
            details.append(detail); continue
        parent=parents[0]; source=parent.source; values=source.values
        declarations=[entry for entry in contracts if entry['parent']==parent.name+'.build'
                      and entry['child']==child_match[1] and entry['kind']=='direct_declarative_child']
        resolve=re.fullmatch(r'Slice '+str(selection['slice_id'])+r' Step (3[a-d])',original.get('resolve_by',''))
        expected_owner='SLICE:'+selection['feature_id']+':'+resolve[1] if resolve else None
        if len(declarations)!=1 or declarations[0]['owner']!=expected_owner:
            details.append(detail); continue
        build=parent.members.get('build',[])
        if len(build)!=1 or build[0].kind!='method' or build[0].static or not build[0].body:
            details.append(detail); continue
        child=evidence.definition(child_match[1],source)
        if (child is None or not _component_definition(child)
                or relative not in selection['allowed_target_files']
                or child.source.relative not in selection['allowed_target_files']):
            details.append(detail); continue
        begin,end=build[0].body; calls=[]
        for index in range(begin+1,end-1):
            if values[index:index+2]!=[child_match[1],'(']: continue
            if values[index-1] in {'.','new','function','return','='}: continue
            if evidence._flow_idle_local_contains(source,begin,end,index): continue
            if evidence._flow_arrow_contains(source,begin,end,index): continue
            if evidence._shadowed_parameter(source,child_match[1],begin,end): continue
            if source.pairs.get(index+1) is None: continue
            calls.append(index)
        if len(calls)!=1:
            details.append(detail); continue
        detail={key:value for key,value in detail.items() if key not in {'failed_check','reason','repair_action'}}
        detail.update(status='PASS',evidence=[{'role':'native-build-entry','file':relative,
            'line':source.tokens[build[0].index].line,'class':parent.name,'member':'build'},
            {'role':'direct-declarative-child','file':relative,'line':source.tokens[calls[0]].line,
             'child':child.name,'definition_file':child.source.relative,
             'definition_line':child.source.tokens[child.start].line},
            {'role':'explicit-embed-contract',**declarations[0]}])
        details.append(detail)
    return {'pass':sum(detail['status']=='PASS' for detail in details),
            'fail':sum(detail['status']=='FAIL' for detail in details),'details':details}


def _top_cross(content):
    starts=list(re.finditer(r'^cross_slice_edits[ \t]*[:：]',content,re.M))
    if len(starts)>1: raise MigrationError('Duplicate top-level cross_slice_edits block')
    if not starts: return [],None
    block=re.match(r'cross_slice_edits[ \t]*[:：][ \t]*([^\n]*)\n((?:[ \t]+[^\n]*(?:\n|$))*)',content[starts[0].start():])
    if block is None: raise MigrationError('Malformed top-level cross_slice_edits block')
    if block[1].strip()=='[]' and not block[2].strip(): return [],None
    if block[1].strip(): raise MigrationError('Unsupported inline cross_slice_edits value')
    entries=[]; current=None
    for line in block[2].splitlines():
        if not line.strip(): continue
        field=re.fullmatch(r'(  - |    )([a-z_]+):[ \t]*(.+)',line)
        if not field: raise MigrationError('Unsupported cross_slice_edits field syntax')
        prefix,key,value=field.groups()
        if prefix=='  - ':
            if key!='file': raise MigrationError('Cross edit must start with file')
            current={}; entries.append(current)
        if current is None or key not in {'file','handler','resolve_by','slot'} or key in current:
            raise MigrationError('Unknown or duplicate cross edit field: '+key)
        if value.startswith('"'):
            value=json.loads(value)
        if not isinstance(value,str) or not value or value.startswith("'"):
            raise MigrationError('Cross edit fields require unambiguous nonempty strings')
        current[key]=value
    if not entries: raise MigrationError('Empty top-level cross edit block must explicitly use []')
    for entry in entries:
        if not {'file','handler','resolve_by'}<=entry.keys() or not re.fullmatch(r'[A-Za-z_$][\w$]*',entry['handler']):
            raise MigrationError('Cross edit requires exact file, handler and resolve_by')
    identities=[(entry['file'],entry['handler'],entry.get('slot',''),entry['resolve_by']) for entry in entries]
    if len(set(identities))!=len(identities): raise MigrationError('Duplicate cross edit responsibility')
    return entries,(starts[0].start(),starts[0].start()+block.end())


def _normalize_cross(content, entries, span):
    """Move exactly one authored block; other plan text remains byte-identical."""
    removed=content[:span[0]]+content[span[1]:]
    modifies=list(re.finditer(r'^modifies_files[ \t]*[:：]',removed,re.M))
    if len(modifies)!=1: raise MigrationError('Top-level cross needs one original modifies_files block')
    original=re.match(r'modifies_files[ \t]*[:：][ \t]*([^\n]*)\n((?:[ \t]+[^\n]*(?:\n|$))*)',removed[modifies[0].start():])
    if original is None or original[1].strip() not in {'','[]'}:
        raise MigrationError('Unsupported modifies_files shape for cross normalization')
    insertion=modifies[0].start()+original.end()
    nested='  cross_slice_edits:\n'+''.join('  '+line+'\n' for line in content[span[0]:span[1]].splitlines()[1:] if line.strip())
    normalized=removed[:insertion]+nested+removed[insertion:]
    if normalized.count(nested)!=1 or normalized.replace(nested,'',1)!=removed:
        raise MigrationError('Cross normalization changed non-cross bytes')
    expected=[asdict(edit) for spec in _parser().FeaturePlan.parse(content).slices.values() for edit in spec.cross_slice_edits]
    if expected: raise MigrationError('Cannot combine top-level and nested cross edit blocks implicitly')
    wanted=[dict(file=e['file'],handler=e['handler'],resolve_by=e['resolve_by'],slot=e.get('slot','')) for e in entries]
    parsed=_parser().FeaturePlan.parse(normalized)
    actual=[asdict(edit) for spec in parsed.slices.values() for edit in spec.cross_slice_edits]
    if actual!=wanted: raise MigrationError('Cross normalization changed item count, order or fields')
    before=_parser().FeaturePlan.parse(content)
    for number,spec in before.slices.items():
        prior,after=asdict(spec),asdict(parsed.get(number))
        prior['cross_slice_edits']=[];after['cross_slice_edits']=[]
        if prior!=after: raise MigrationError('Cross normalization changed another original plan field')
    return normalized,wanted


def _authority_plans(project, index):
    """Route stable parent IDs through exact indexed files, without glob authority."""
    text=index.read_text(encoding='utf-8-sig')
    paths={}; slices={}; numbers=set()
    headers=list(HEADER.finditer(text))
    for offset,header in enumerate(headers):
        number,fid=int(header[1]),header[3]
        if number in numbers or fid in slices:
            raise MigrationError('Duplicate indexed slice identity in target authority')
        numbers.add(number)
        section=text[header.end():headers[offset+1].start() if offset+1<len(headers) else len(text)]
        links=re.findall(r'^detail:\s*(\S+)\s*$',section,re.M)
        if len(links)!=1: raise MigrationError('Indexed slice needs one target authority detail')
        relative=links[0][6:] if links[0].startswith('plans/') else links[0]
        target=safe_child(project,index.parent.relative_to(project).as_posix()+'/'+relative)
        filename=re.fullmatch(r'slice-(\d+)-(F\d+)\.md',target.name)
        if (not filename or int(filename[1])!=number or filename[2]!=fid
                or target.parent!=index.parent/'slices'):
            raise MigrationError('Indexed target authority slice filename identity differs')
        paths['SLICE:'+fid+':']=target; slices[fid]=target
    all_links=re.findall(r'^detail:\s*(\S+)\s*$',text,re.M)
    consulted=[]
    for link in all_links:
        relative=link[6:] if link.startswith('plans/') else link
        target=safe_child(project,index.parent.relative_to(project).as_posix()+'/'+relative)
        if not target.is_file(): raise MigrationError('Indexed target authority detail is missing: '+link)
        if target in consulted: raise MigrationError('Duplicate indexed target authority detail path')
        consulted.append(target)
        if target==index.parent/'base-plan.md': paths['BASE:']=target
        elif target not in slices.values(): raise MigrationError('Unknown indexed target authority detail identity: '+link)
    if len(consulted)!=len(paths): raise MigrationError('Indexed target authority details are inconsistent')
    ui=index.parent/'ui-plan.md'
    if ui.is_file(): paths['UI:']=ui
    return paths


def _target_authority(project, index, detail, current, fid):
    """Grant targets only from exact reviewed ownership, parents or contracts.

    Candidate routing is not proof: every granted item is read again through
    _projection, which checks each responsibility table against its JSON row.
    Unrelated plan files are not required to be valid ancestors.
    """
    from .artifact_contract import markdown_tables
    from .spec_contract import references
    paths=_authority_plans(project,index)
    loaded={detail:{item['item_id']:item for item in current}}
    if len(loaded[detail])!=len(current): raise MigrationError('Duplicate current target authority item')
    items=dict(loaded[detail]); authority=[]; visited=set()

    def plan_for(ident):
        if not isinstance(ident,str) or not ITEM.fullmatch(ident):
            raise MigrationError('Target authority parent needs a stable Base/UI/Slice ID: '+str(ident))
        prefix='SLICE:'+ident.split(':')[1]+':' if ident.startswith('SLICE:') else ident.split(':',1)[0]+':'
        if prefix not in paths: raise MigrationError('Target authority parent plan is missing: '+ident)
        return paths[prefix],prefix

    def load(ident):
        path,prefix=plan_for(ident)
        if path not in loaded:
            projected=_projection(project,path)
            by_id={item['item_id']:item for item in projected}
            if len(by_id)!=len(projected) or any(not key.startswith(prefix) for key in by_id):
                raise MigrationError('Duplicate or foreign target authority item in '+path.relative_to(project).as_posix())
            if prefix.startswith('SLICE:'):
                headers=list(HEADER.finditer(path.read_text(encoding='utf-8-sig')))
                indexed=[header for header in HEADER.finditer(index.read_text(encoding='utf-8-sig'))
                         if header[3]==prefix.split(':')[1]]
                if (len(headers)!=1 or len(indexed)!=1 or headers[0][1]!=indexed[0][1]
                        or headers[0][3]!=indexed[0][3]):
                    raise MigrationError('Target authority slice header differs from indexed identity')
                index_text=index.read_text(encoding='utf-8-sig')
                tail=index_text[indexed[0].end():]
                following=HEADER.search(tail)
                section=tail[:following.start()] if following else tail
                groups=re.findall(r'^parallel_group:\s*(\d+)\b',section,re.M)
                parsed=_parser().FeaturePlan.parse(path.read_text(encoding='utf-8-sig')).get(int(headers[0][1]))
                if len(groups)!=1 or parsed is None or parsed.parallel_group!=int(groups[0]):
                    raise MigrationError('Target authority slice indexed/detail group differs')
            for key,item in by_id.items():
                if key in items: raise MigrationError('Duplicate target authority stable item: '+key)
                items[key]=item
            loaded[path]=by_id
        item=loaded[path].get(ident)
        if item is None or item['scope']!='product':
            raise MigrationError('Target authority parent is missing or excluded: '+ident)
        return item

    def visit(ident, chain, kind='parent', contract=None):
        if ident in chain: raise MigrationError('Target authority parent cycle: '+' -> '.join([*chain,ident]))
        item=load(ident); chain=[*chain,ident]
        key=(chain[0],ident,kind,json.dumps(contract,sort_keys=True))
        if key in visited: return
        visited.add(key)
        owners=_files(project,[path for path in item['ownership'] if Path(path).suffix=='.ets'])
        for relative in owners:
            proof={'file':relative,'kind':kind,'item_id':ident,'plan_path':item['path'],
                   'heading':item['heading'],'sha256':item['sha256'],'parent_chain':chain}
            if contract is not None: proof['contract']=contract
            authority.append(proof)
        for parent in item['parents']: visit(parent,chain,'parent',contract)

    for item in current: visit(item['item_id'],[],'current-slice')

    def owner_candidates(relative):
        candidates=set()
        # The aggregate blocks only route a precise path to a candidate item;
        # load()/visit() still require full table/JSON and parent validation.
        for path in paths.values():
            if path in loaded:
                candidates.update(item['item_id'] for item in loaded[path].values()
                    if item['scope']=='product' and relative in item['ownership'])
                continue
            text=path.read_text(encoding='utf-8-sig')
            for block in re.findall(r'^\s*```json\s*\n(.*?)^\s*```\s*$',text,re.M|re.S):
                try: value=json.loads(block)
                except ValueError:
                    if 'plan_items_version' in block and json.dumps(relative) in block:
                        raise MigrationError('Malformed candidate target authority projection')
                    continue
                if isinstance(value,dict) and value.get('plan_items_version')==2:
                    for item in value.get('items',[]):
                        if isinstance(item,dict) and relative in item.get('ownership',[]) and item.get('scope')=='product':
                            candidates.add(item.get('item_id'))
        return candidates

    def exact_paths(value):
        value=value.strip('` ')
        if value.startswith('[') or value.startswith('"'):
            try: value=json.loads(value)
            except ValueError as exc: raise MigrationError('Public target contract requires exact JSON paths') from exc
        values=value if isinstance(value,list) else [value]
        if (not values or any(not isinstance(path,str) or not path.endswith('.ets') for path in values)
                or len(set(values))!=len(values)):
            raise MigrationError('Public target contract requires exact ETS paths')
        return _files(project,values)

    seeds=[detail]
    features=[path for path in (project/'spec/baseline/features').glob('*.md')
              if re.fullmatch(re.escape(fid)+r'(?:[_.-].*)?\.md',path.name)]
    if len(features)>1: raise MigrationError('Ambiguous current feature contract source: '+fid)
    seeds+=features
    pending=[(source,target,heading,body) for source in seeds
             for target,heading,body in references(project,source,source.read_text(encoding='utf-8-sig'))]
    seen=set()
    while pending:
        source,target,heading,body=pending.pop()
        anchor=(target,heading)
        if anchor in seen: continue
        seen.add(anchor)
        declarations=[]
        for table in markdown_tables(body):
            headers=[header.strip('` ') for header in table['headers']]
            target_columns=[i for i,name in enumerate(headers) if name in {'目标文件','ownership'}]
            if not target_columns: continue
            if len(target_columns)!=1: raise MigrationError('Ambiguous public target contract path columns')
            owner_columns=[i for i,name in enumerate(headers) if name in {'item_id','owner','owner_item_id'}]
            if len(owner_columns)>1: raise MigrationError('Ambiguous public target contract owner columns')
            for row in table['rows']:
                if len(row)!=len(headers): raise MigrationError('Malformed public target contract row')
                owner=row[owner_columns[0]].strip('` "') if owner_columns else None
                declarations.extend((relative,owner) for relative in exact_paths(row[target_columns[0]]))
        for line in body.splitlines():
            match=re.fullmatch(r'唯一目标文件[：:][ \t]*`([^`]+\.ets)`[。.]?[ \t]*(?:这些.*)?',line)
            if match: declarations.extend((relative,None) for relative in exact_paths(match[1]))
        for relative,owner in declarations:
            candidates={owner} if owner else owner_candidates(relative)
            if len(candidates)!=1: raise MigrationError('Public target contract owner is missing or ambiguous: '+relative)
            ident=next(iter(candidates)); item=load(ident)
            if relative not in item['ownership']:
                raise MigrationError('Public target contract path differs from exact owner: '+relative)
            contract={'source':source.relative_to(project).as_posix(),'path':target.relative_to(project).as_posix(),
                      'heading':heading,'sha256':digest(target.read_bytes()),'target_file':relative}
            # A public contract grants exactly its declared target file. Its
            # owner's ancestry is checked, but sibling ownership is not granted.
            start=len(authority); visit(ident,[],'public-contract',contract)
            authority[start:]=[proof for proof in authority[start:] if proof['file']==relative]
        pending.extend((target,next_target,next_heading,next_body)
            for next_target,next_heading,next_body in references(project,target,body))
    unique={json.dumps(proof,sort_keys=True):proof for proof in authority}
    authority=[unique[key] for key in sorted(unique)]
    return sorted({proof['file'] for proof in authority}),authority


def load_slice(project, number, feature_plan=None, group=None):
    project=Path(project).resolve()
    index=Path(feature_plan).resolve() if feature_plan else project/'spec/baseline/plans/feature-plan.md'
    if not index.is_relative_to(project): raise MigrationError('Feature plan is outside the project')
    text=index.read_text(encoding='utf-8-sig')
    if not re.search(r'^\s*(?:-\s+)?plan_format:\s*indexed-v1\s*$',text,re.M):
        raise MigrationError('Native profile 2 requires an indexed-v1 feature plan')
    headers=list(HEADER.finditer(text))
    selected=[(i,h) for i,h in enumerate(headers) if int(h[1]) == number]
    if len(selected)!=1: raise MigrationError('Missing or duplicate indexed slice: '+str(number))
    i,header=selected[0]
    section=text[header.end():headers[i+1].start() if i+1<len(headers) else len(text)]
    detail=re.findall(r'^detail:\s*(\S+)\s*$',section,re.M)
    index_groups=re.findall(r'^parallel_group:\s*(\d+)\b',section,re.M)
    if len(detail)!=1 or len(index_groups)!=1: raise MigrationError('Indexed slice needs one detail and parallel_group')
    relative=detail[0][len('plans/'):] if detail[0].startswith('plans/') else detail[0]
    path=safe_child(project,index.parent.relative_to(project).as_posix()+'/'+relative)
    content=path.read_text(encoding='utf-8-sig')
    actual=list(HEADER.finditer(content))
    if len(actual)!=1 or actual[0][1] != header[1] or actual[0][3] != header[3]:
        raise MigrationError('Slice filename/header/index identity differs')
    file_fid=re.fullmatch(r'slice-(\d+)-(F\d+)\.md',path.name)
    if not file_fid or int(file_fid[1])!=number or file_fid[2]!=header[3]:
        raise MigrationError('Slice indexed filename identity differs')
    parsed=_parser().FeaturePlan.parse(content).get(number)
    if parsed is None or parsed.parallel_group!=int(index_groups[0]):
        raise MigrationError('Slice indexed/detail group differs')
    if group is not None and parsed.parallel_group!=int(group):
        raise MigrationError('Requested group differs from indexed slice group')
    items=_projection(project,path)
    fid=header[3]
    if not items or any(not item['item_id'].startswith('SLICE:'+fid+':') or item['scope']!='product' for item in items):
        raise MigrationError('Native slice projection is empty or has a foreign identity/scope')
    owned=_files(project,[f for item in items for f in item['ownership']],product_ownership=True)
    if not owned: raise MigrationError('Native structural scope cannot be empty')
    allowed,authority=_target_authority(project,index,path,items,fid)
    modifies=_files(project,parsed.modifies_files)
    top,span=_top_cross(content)
    embeds=_declarative_contracts(project,path,content,'embed_bindings',
        {'owner','parent','child','kind','input'})
    callbacks=_declarative_contracts(project,path,content,'callback_bindings',
        {'owner','kind','producer','event','binding','consumer','input'},optional={'continuation'})
    cross=_files(project,[edit.file for edit in parsed.cross_slice_edits]+[edit['file'] for edit in top])
    # Wires/embeds are not added to modifies; their source contracts and the
    # original detector retain their own semantics and repair categories.
    for wire in parsed.wires:
        _files(project,[wire.page,wire.viewmodel])
    for embed in parsed.parent_placeholder_replacement:
        _files(project,[embed.parent_file])
    return {'slice_id':number,'feature_id':fid,'index':index,'detail':path,'parsed':parsed,
            'top_cross':top,'top_cross_span':span,
            'embed_bindings':embeds,'callback_bindings':callbacks,
            'owned_files':owned,'modifies_files':modifies,'cross_slice_edits_files':cross,
            'allowed_target_files':allowed,'target_authority':authority,
            'audit_scope':sorted({path for path in owned+modifies+cross if Path(path).suffix=='.ets'})}


def _run_report(original, helper, arguments, destination):
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='native-structural-detector-') as directory:
        fresh=Path(directory)/'report.json'
        result=original('arkts-structural-closure',helper,[*arguments,'--output-json',fresh])
        accepted=(0,1,2) if helper=='loop_runner.py' else (0,1)
        if result.returncode not in accepted or not fresh.is_file():
            raise MigrationError(helper+' failed: '+(result.stderr or result.stdout)[-2000:])
        report=read_json(fresh)
    write_json(destination,report)
    return report,result


def _cross_declaration(evidence, relative, handler):
    source=next((source for source in evidence.sources if source.relative==relative),None)
    if source is None: return []
    declarations=[]
    for definition in source.definitions:
        for member in definition.members.get(handler,[]):
            declarations.append({'file':relative,'line':source.tokens[member.index].line,
                                 'class':definition.name,'member':handler,'kind':member.kind})
    # Top-level exported functions and shared capability bindings are native
    # cross-edit targets too. Nested local names cannot prove their existence.
    cursor=0
    while cursor<len(source.tokens)-1:
        if source.values[cursor] in {'function','const','let','var'} and source.values[cursor+1]==handler:
            declarations.append({'file':relative,'line':source.tokens[cursor+1].line,
                                 'member':handler,'kind':'top-level-'+source.values[cursor]})
        cursor=source.pairs[cursor]+1 if cursor in source.pairs else cursor+1
    return declarations


def _adapt_top_cross(selection, project, original, evidence):
    raw=selection['detail'].read_bytes()
    # Decode explicitly so CRLF and any original BOM outside the relocated
    # block remain byte-identical in the derived plan.
    content=raw.decode('utf-8-sig')
    entries,span=_top_cross(content)
    if entries!=selection['top_cross']: raise MigrationError('Cross plan changed during detection')
    normalized,wanted=_normalize_cross(content,entries,span)
    normalized_bytes=(b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+normalized.encode('utf-8')
    with tempfile.TemporaryDirectory(prefix='native-cross-plan-') as temporary:
        temporary=Path(temporary)
        index=selection['index']; index_text=index.read_text(encoding='utf-8-sig')
        headers=list(HEADER.finditer(index_text))
        for offset,header in enumerate(headers):
            section=index_text[header.end():headers[offset+1].start() if offset+1<len(headers) else len(index_text)]
            pointers=re.findall(r'^detail:\s*(\S+)\s*$',section,re.M)
            if len(pointers)!=1: raise MigrationError('Derived index requires every original detail pointer')
            relative=pointers[0][6:] if pointers[0].startswith('plans/') else pointers[0]
            source=safe_child(project,index.parent.relative_to(project).as_posix()+'/'+relative)
            target=safe_child(temporary,relative)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(normalized_bytes if source==selection['detail'] else source.read_bytes())
        derived_index=temporary/index.name
        derived_index.write_bytes(index.read_bytes())
        report,_=_run_report(original,'verify_slice_wiring.py',
            ['--project-root',project,'--slice',selection['slice_id'],'--feature-plan',derived_index],temporary/'result.json')
    category=report['categories']['C3_cross_slice']
    details=category.get('details',[])
    def fields(value):
        return {key:value.get(key,'') for key in ['file','handler','resolve_by','slot']}
    if len(details)!=len(wanted) or [fields(detail) for detail in details]!=wanted:
        raise MigrationError('Original C3 did not consume each normalized cross edit in order')
    checked=[]
    item_ids={item['item_id'] for item in _projection(project,selection['detail'])}
    for detail in details:
        declarations=_cross_declaration(evidence,detail['file'],detail['handler'])
        check={**detail,'normalized_original_evidence':detail,'evidence':declarations}
        resolve=re.fullmatch(r'Slice\s+(\d+)\s+Step\s+(3[a-d])',detail.get('resolve_by',''))
        correct_resolve=(resolve is not None and int(resolve[1])==selection['slice_id']
                         and 'SLICE:'+selection['feature_id']+':'+resolve[2] in item_ids)
        bindings=[]
        if (detail.get('status')=='FAIL' and detail.get('failed_check')=='C3_HANDLER_NOT_FOUND'
                and correct_resolve):
            bindings=evidence.top_binding_proof(detail['file'],detail['handler'])
        if bindings:
            check.update(status='PASS',evidence=bindings,native_binding_evidence={
                'bounded_exception':'C3_HANDLER_NOT_FOUND','file':detail['file'],
                'handler':detail['handler'],'resolve_item':'SLICE:'+selection['feature_id']+':'+resolve[2],
                'producer_consumer_proof':bindings})
            for field in ['failed_check','reason','repair_action']: check.pop(field,None)
        elif not declarations and detail.get('failed_check') in {None,'C3_HANDLER_NOT_FOUND'}:
            check.update(status='FAIL',failed_check='C3_NATIVE_DECLARATION_MISSING',
                reason='No real handler/binding declaration in the configured product file; comments, strings and historical copies are not evidence.',
                repair_action='Reconcile the authored cross edit with the actual product handler or binding; do not add a dummy declaration.')
        checked.append(check)
    adapted={'pass':sum(detail['status']=='PASS' for detail in checked),
             'fail':sum(detail['status']=='FAIL' for detail in checked),'details':checked}
    provenance={'original_detail':selection['detail'].relative_to(project).as_posix(),
        'original_sha256':digest(raw),'derived_sha256':digest(normalized_bytes),
        'original_index_sha256':digest(selection['index'].read_bytes()),
        'authored_count':len(wanted),'original_consumer_count':len(details),
        'field_mapping':[{'authored':entry,'derived_parser':entry,'derived_original_consumer':fields(detail)}
                         for entry,detail in zip(wanted,details)],
        'preserved':'All non-cross text unchanged; original modifies/ownership/wires/integration/Step table and JSON values retained',
        'temporary_plan_only':True}
    return adapted,category,provenance


def wiring(project, number, destination, original, *, feature_plan=None, index=None):
    selection=load_slice(project,number,feature_plan)
    args=['--project-root',project,'--slice',number,'--feature-plan',selection['index']]
    report,result=_run_report(original,'verify_slice_wiring.py',args,destination)
    categories=report.get('categories',{})
    if set(categories)!=set(CATEGORIES) or not all(isinstance(categories[key].get('details'),list) for key in CATEGORIES):
        raise MigrationError('Incomplete original wiring detector report')
    expected=selection['parsed'].integration_points
    details=categories['C2_integration_point']['details']
    if len(details)!=len(expected) or [d.get('description') for d in details]!=[p.description for p in expected]:
        raise MigrationError('Original wiring detector did not consume every integration point')
    report['original_C2_integration_point']=categories['C2_integration_point']
    evidence=index or EvidenceIndex(project)
    if selection['embed_bindings']:
        expected_embeds=[asdict(entry) for entry in selection['parsed'].parent_placeholder_replacement]
        original_embeds=categories['C4_parent_replacement']['details']
        fields=lambda entry: {key:entry.get(key,'') for key in ('parent_file','builder_name','replace_with','resolve_by')}
        if len(expected_embeds)!=len(original_embeds) or [fields(entry) for entry in expected_embeds]!=[fields(entry) for entry in original_embeds]:
            raise MigrationError('Original C4 detector did not consume every authored embed responsibility')
        report['original_C4_parent_replacement']=categories['C4_parent_replacement']
        categories['C4_parent_replacement']=_adapt_direct_build_embeds(selection,evidence,categories['C4_parent_replacement'])
    if selection['top_cross']:
        report['original_C3_cross_slice']=categories['C3_cross_slice']
        adapted,normalized,provenance=_adapt_top_cross(selection,Path(project).resolve(),original,evidence)
        report['normalized_original_C3_cross_slice']=normalized
        report['native_cross_projection']=provenance
        categories['C3_cross_slice']=adapted
    proved=[]
    for old,point in zip(details,expected):
        proof=evidence.prove(point.description,selection['allowed_target_files'])
        if proof['status']=='FAIL':
            declared=evidence.prove_declarative(point.description,selection['allowed_target_files'],selection['callback_bindings'])
            if declared['status']=='PASS': proof=declared
        if proof['status']=='FAIL':
            platform=evidence.prove_platform_route(point.description,selection['allowed_target_files'],selection['owned_files'])
            if platform['status']=='PASS': proof=platform
        targets={entry['file'] for entry in proof.get('evidence',[]) if entry.get('role')=='definition'}
        proof['target_authority']=[entry for entry in selection['target_authority'] if entry['file'] in targets]
        proved.append({'ip_id':old['ip_id'],'description':point.description,
                       'original_evidence':old,**proof})
    categories['C2_integration_point']={'pass':sum(d['status']=='PASS' for d in proved),
        'fail':sum(d['status']=='FAIL' for d in proved),'details':proved}
    replaced={'C2_integration_point'}|({'C3_cross_slice'} if selection['top_cross'] else set())|({'C4_parent_replacement'} if selection['embed_bindings'] else set())
    actions=[a for a in report.get('repair_actions',[]) if a.get('category') not in replaced]
    if selection['embed_bindings']:
        for detail in categories['C4_parent_replacement']['details']:
            if detail['status']=='FAIL':
                actions.append({'id':'C4_parent_replacement__'+detail['ppr_id'],'category':'C4_parent_replacement',
                    'failed_check':detail['failed_check'],'current_state':detail['reason'],
                    'suggested_action':detail['repair_action'],'file':detail['parent_file'],'fixer_layer':'ui'})
    if selection['top_cross']:
        for detail in categories['C3_cross_slice']['details']:
            if detail['status']=='FAIL':
                actions.append({'id':'C3_cross_slice__'+detail['cse_id'],'category':'C3_cross_slice',
                    'failed_check':detail['failed_check'],'current_state':detail['reason'],
                    'suggested_action':detail['repair_action'],'file':detail['file'],'fixer_layer':'ui'})
    for detail in proved:
        if detail['status']=='FAIL':
            actions.append({'id':'C2_integration_point__'+detail['ip_id'],'category':'C2_integration_point',
                'failed_check':detail['failed_check'],'current_state':detail['reason'],
                'suggested_action':detail['repair_action'],'file':detail.get('caller',''),'fixer_layer':'ui'})
    report.update(feature_id=selection['feature_id'],repair_actions=actions,
                  overall='BLOCKED' if any(c['fail'] for c in categories.values()) else 'PASS')
    report['scope']={key:selection[key] for key in ['owned_files','modifies_files','cross_slice_edits_files','audit_scope',
                                                 'allowed_target_files','target_authority']}
    report['native_adapter']={'version':1,'original_detector':'verify_slice_wiring.py',
                              'preserved_categories':['C1_orphan_check']+([] if selection['embed_bindings'] else ['C4_parent_replacement'])+
                                  ([] if selection['top_cross'] else ['C3_cross_slice']),
                              'source_roots':[path.relative_to(Path(project).resolve()).as_posix()
                                              for path in evidence.source_roots]}
    write_json(destination,report)
    return report


def _diff_scope(project, base):
    if not base: return []
    result=subprocess.run(['git','-C',str(project),'diff','--name-only','-z','--diff-filter=ACMRT',base,'--','*.ets'],
        capture_output=True,encoding='utf-8',errors='strict',shell=False)
    if result.returncode: raise MigrationError('Cannot resolve explicitly supplied diff base: '+result.stderr[-1000:])
    return _files(project,[p for p in result.stdout.split('\0') if p])


def _group_members(project, group):
    text=(project/'spec/baseline/plans/feature-plan.md').read_text(encoding='utf-8-sig')
    headers=list(HEADER.finditer(text))
    members=[]
    for index,header in enumerate(headers):
        section=text[header.end():headers[index+1].start() if index+1<len(headers) else len(text)]
        groups=re.findall(r'^parallel_group:\s*(\d+)\b',section,re.M)
        if len(groups)!=1: raise MigrationError('Each indexed slice requires one parallel_group')
        if int(groups[0])==int(group): members.append(int(header[1]))
    if not members or len(set(members))!=len(members):
        raise MigrationError('Requested indexed group is empty or duplicated')
    return set(members)


def iterate(args, original):
    project=args.project_root.resolve()
    maximum=8 if args.max_iter is None else args.max_iter
    if args.mode=='group':
        if not args.slices or not re.fullmatch(r'\d+(?:,\d+)*',args.slices):
            raise MigrationError('Native group mode requires explicit comma-separated slices')
        numbers=[int(n) for n in args.slices.split(',')]
        if len(set(numbers))!=len(numbers): raise MigrationError('Duplicate native group slice')
        if set(numbers)!=_group_members(project,args.target):
            raise MigrationError('Explicit slices do not match all indexed group members')
    else:
        try: numbers=[int(args.target)]
        except ValueError as exc: raise MigrationError('Slice target must be a number') from exc
    selected=[load_slice(project,n,group=args.target if args.mode=='group' else None) for n in numbers]
    changed_files=_diff_scope(project,args.diff_base)
    scope=sorted(set(changed_files+[f for s in selected for f in s['audit_scope']]))
    if not scope: raise MigrationError('Native structural audit requires nonempty scope')
    state_path=args.state_file.resolve()
    state=read_json(state_path) if state_path.exists() else {'history':[],'max_iter':maximum,'mode':args.mode,'target':args.target}
    if state.get('mode',args.mode)!=args.mode or str(state.get('target',args.target))!=args.target:
        raise MigrationError('Structural state mode/target differs')
    history=state['history']
    if not isinstance(history,list): raise MigrationError('Malformed structural history')
    iteration=len(history)
    directory=state_path.parent
    audit_path=directory/f'audit-{args.target}-iter{iteration}.json'
    audit_arguments=['--project-root',project,'--scope','slice','--scope-files',*scope]
    if args.handoffs: audit_arguments+=['--handoffs',*args.handoffs]
    audit,_=_run_report(original,'audit_skeletons.py',audit_arguments,audit_path)
    if {path.replace('\\','/') for path in audit.get('scope_files',[])}!=set(scope):
        raise MigrationError('Original audit did not scan the exact native scope')
    wiring_path=directory/f'wiring-{args.target}-iter{iteration}.json'
    index=EvidenceIndex(project)
    reports=[]
    for n in numbers:
        output=directory/f'wiring-{args.target}-s{n}-iter{iteration}.json' if args.mode=='group' else wiring_path
        reports.append(wiring(project,n,output,original,index=index))
    actions=[{**a,'slice_id':r['slice_id']} for r in reports for a in r['repair_actions']]
    combined={key:{'pass':sum(r['categories'][key]['pass'] for r in reports),
                   'fail':sum(r['categories'][key]['fail'] for r in reports),
                   'details':[detail for r in reports for detail in r['categories'][key]['details']]}
              for key in CATEGORIES}
    wiring_report=reports[0] if args.mode=='slice' else {'group_id':args.target,'slices':numbers,
        'group_slices':[str(number) for number in numbers],
        'scope':{key:sorted({file for report in reports for file in report['scope'][key]})
                 for key in ['owned_files','modifies_files','cross_slice_edits_files','audit_scope','allowed_target_files']},
        'slice_reports':reports,'categories':combined,'repair_actions':actions,'overall':'BLOCKED' if actions else 'PASS'}
    if args.mode=='group':
        authorities={json.dumps(proof,sort_keys=True):proof for report in reports for proof in report['scope']['target_authority']}
        wiring_report['scope']['target_authority']=[authorities[key] for key in sorted(authorities)]
    wiring_report['scope']['audit_scope']=scope
    write_json(wiring_path,wiring_report)
    failures=[f for f in audit['findings'] if f.get('severity_at_scope')=='FAIL']
    escapes=audit.get('handoff_escape_hatches',[])
    fingerprint=[[f.get('file',''),f.get('line',0),f.get('subtype','')] for f in failures]
    fingerprint += [[a.get('file',''),0,'wiring:'+a['category']+':'+a['failed_check']] for a in actions]
    fingerprint += [[f.get('file',''),f.get('line',0),'handoff-escape-hatch'] for f in escapes]
    fingerprint.sort(key=lambda row:(str(row[0]),row[1],row[2]))
    current={'iter':iteration,'audit_fail':len(failures),'audit_warn':audit['summary'].get('WARN',0),
        'wiring_blocked_categories':sum(c['fail']>0 for r in reports for c in r['categories'].values()),
        'wiring_repair_actions':len(actions),'handoff_escape_hatches':len(escapes),'fingerprint':fingerprint,
        'detectors_run':['audit','wiring'],'detectors_skipped':[],'detectors_effective':['audit','wiring']}
    runner={'history':history,'max_iter':maximum,'current':current}
    # The upstream public runner owns every verdict, constant and stall/regress
    # decision. Its input is ephemeral, not a second control ledger.
    with tempfile.TemporaryDirectory(prefix='native-structural-runner-') as temp:
        input_path=Path(temp)/'input.json'; write_json(input_path,runner)
        verdict,result=_run_report(original,'loop_runner.py',['--state-file',input_path],Path(temp)/'verdict.json')
    if verdict.get('verdict') not in {'CONVERGED','CONTINUE','STALLED','REGRESSED','EXHAUSTED'}:
        raise MigrationError('Unexpected original loop_runner verdict')
    state.update(history=[*history,current],max_iter=runner['max_iter'],last_verdict=verdict,mode=args.mode,target=args.target)
    write_json(state_path,state)
    prompt=''
    if verdict['verdict']=='CONTINUE':
        prompt='STRUCTURAL LOOP native indexed repair brief\nRepair only the following original detector findings and bounded native wiring failures, then rerun the same structural entry.\n'+json.dumps({'skeleton_findings':failures,'wiring_repair_actions':actions,'handoff_escape_hatches':escapes},ensure_ascii=False,indent=2)
    output={'mode':args.mode,'target':args.target,'iteration':iteration,**{key:verdict[key] for key in ['verdict','escalation','reason']},
        'current_state':{'audit_fail':len(failures),'wiring_repair_actions':len(actions),'handoff_escape_hatches':len(escapes),
                         'total_fail':len(failures)+len(actions)+len(escapes)},
        'dispatch_prompt':prompt,'detector_json_paths':{'audit':str(audit_path),'wiring':str(wiring_path)},
        'state_file':str(state_path),'native_scope':{'owned_files':sorted({f for s in selected for f in s['owned_files']}),
            'audit_scope':scope,'diff_base':args.diff_base,'diff_files':changed_files}}
    if args.output_json: write_json(args.output_json,output)
    print(json.dumps(output,ensure_ascii=False,indent=2))
    return 0 if verdict['verdict']=='CONVERGED' else 1 if verdict['verdict']=='CONTINUE' else 2
