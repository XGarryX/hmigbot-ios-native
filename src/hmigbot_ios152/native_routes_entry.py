"""Native input wrappers around the original compiled route comparators."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

from hmigbot_ios.core import MigrationError, atomic_write, json_bytes, read_json, write_json
from .source import Source, config, ios_source
from .native_routes import analyze, expected_nav, worklist, apply_verdicts, sha, canonical_json


from .route_engine import roots, compiled
from .route_target_entry import TARGET_CONSUMERS, target_current, target_extract, target_consumer


def _source(root,value):
    if not value:
        cfg=config(root);ios=cfg.get('ios',{});value=(ios.get('source_root') if isinstance(ios,dict) else ios) or cfg.get('android')
    if not value:raise MigrationError('Native source root missing; pass --ios-root or configure ios.source_root')
    path=(root/value).resolve()
    if not path.is_dir():raise MigrationError('Native source directory does not exist: '+str(path))
    return Source(path,root)


def _facts(root,expected,args):
    value=args.ios_root or args.src or args.android_root or expected.get('ios_root') or expected.get('android_root')
    facts=analyze(_source(root,value))
    if expected and expected.get('input_identity')!=facts['input_identity']:
        raise MigrationError('Native source identity changed; rerun extract_nav_graph before downstream source consumers')
    if expected and expected!=expected_nav(facts):
        raise MigrationError('Expected native graph differs from current source facts; rerun extract_nav_graph')
    return facts


def current_nav(facts,expected,out):
    nav=read_json(out/'nav_edges.json')
    if nav.get('input_identity')!=facts['input_identity'] or nav.get('expected_sha')!=sha(canonical_json(expected)):
        raise MigrationError('Native nav_edges belongs to an older extraction; rerun llm_worklist/apply_llm')
    vp=out/'llm_verdicts.json'
    verdicts=read_json(vp) if vp.is_file() else {'target_rules':{},'method_verdicts':{}}
    if nav.get('verdicts_sha')!=sha(canonical_json(verdicts)):
        raise MigrationError('Native verdicts changed after apply_llm; rerun apply_llm')
    return nav


def modal_specs(facts,nav):
    relevant={e['target'] for e in nav['edges'] if e['target_type']=='dialog' and e.get('target')}
    unknown_targets=[]
    dialogs={k:{**v,'route_relevant':k in relevant} for k,v in facts['modals'].items()}
    for target in relevant-set(dialogs):
        symbols=[s for s in facts['symbols'] if s['name']==target]
        if len(symbols)!=1:
            unknown_targets.append({'target':target,'reason':'modal target has no unique selected native source declaration'});continue
        symbol=symbols[0]
        params=[{'name':p['name'],'type':p['type'],'default':p['initializer'] or None,'is_callback':'->' in p['type']}
                for p in symbol.get('properties',[]) if p['name']!='body' and '@State' not in p.get('attributes','')]
        dialogs[target]={'name':target,'file':symbol['file'],'route_relevant':True,'ctor_params':params,
          'callbacks':[p for p in params if p['is_callback']],'layout':None,'native_content_span':symbol,
          'controls':[{'tag':c['type'],'id':c['id'],'text':c.get('text'),'interactive':c['interactive'],'file':c['file'],'line':c['line']}
                      for c in facts['controls'] if c['owner']==target]}
    return dialogs,unknown_targets


def _metadata(out,stage,identity,inputs,outputs,extra=None):
    write_json(out/(stage+'.native-input.json'),{'stage':stage,'source_platform':'ios','status':'complete','input_identity':identity,
       'inputs':{str(p):sha(p.read_bytes()) for p in inputs if p.is_file()},
       'outputs':{str(p):sha(p.read_bytes()) for p in outputs if p.is_file()},**(extra or {})})
    previous=out/(stage+'.native-failure.json')
    if previous.is_file():previous.rename(out/(stage+'.native-failure.'+sha(previous.read_bytes())[:12]+'.json'))



def manifest_source_identity(value,facts):
    """Decode a display caption only against uniquely evidenced native owners."""
    original=value.strip();text=original;declarations={}
    while len(text)>1 and text.startswith('`') and text.endswith('`'):
        text=text[1:-1]
    symbols=[s for s in (facts or {}).get('symbols',[]) if s.get('kind')!='extension']
    names={s['name'] for s in symbols}
    symbols.extend(s for s in (facts or {}).get('pages',[]) if s['name'] not in names)
    for symbol in symbols:
        key=(symbol.get('file'),symbol.get('start'),symbol.get('line'))
        declarations.setdefault(symbol['name'],{})[key]=symbol
    info={'original':original,'normalized':text,'label':None,'status':'unknown','match_basis':None}
    token=text
    if text not in declarations:
        match=re.fullmatch(r'(?:`([^`]+)`|([^\s`（）()]+))\s*(?:（([^（）()]+)）|\(([^（）()]+)\))',text)
        if not match:
            if re.search(r'[/,，;；→]',text) and len(re.findall(r'[^\W\d]\w*',text))>1:
                info['status']='multi_type'
            return text,info
        token=match[1] or match[2];info['label']=match[3] or match[4]
        if not re.fullmatch(r'[^\W\d]\w*(?:\.[^\W\d]\w*)*',token):
            info['status']='multi_type' if re.search(r'[/,，;；→]',token) else 'unknown'
            return text,info
    exact=token in declarations
    candidates=[token] if exact else [name for name in declarations if '.' not in token and name.rsplit('.',1)[-1]==token]
    matches=[(name,s) for name in candidates for s in declarations[name].values()]
    if len(matches)!=1:
        info['status']='ambiguous' if matches else 'unknown'
        if matches:info['candidates']=[{'name':name,'file':s.get('file'),'line':s.get('line')} for name,s in matches]
        return text,info
    name,symbol=matches[0]
    # A bare short name is already part of the old wire; only caption decoding
    # may resolve it to the qualified owner used by native routes.
    if info['label'] is None:
        info['status']='unchanged_exact';info['match_basis']='qualified_exact'
        info['declaration']={'name':name,'file':symbol.get('file'),'line':symbol.get('line')}
        return text,info
    info.update(normalized=name,status='decoded',match_basis='qualified_exact' if exact else 'unique_short',
                declaration={'name':name,'file':symbol.get('file'),'line':symbol.get('line')})
    return name,info


def normalize_manifest(text,facts=None):
    """Normalize only source/target cells; row order, intent and statuses survive."""
    lines=[];normalized=[]
    for line in text.splitlines():
        cells=line.split('|')
        if len(cells)>=8 and re.fullmatch(r'\s*\d{4}\s*',cells[1]):
            original=cells[3].strip()
            source,source_identity=manifest_source_identity(cells[2],facts)
            record={'seq':cells[1].strip(),'source':cells[2].strip(),'original':original,
                    'normalized':None,'source_identity':source_identity}
            # Markdown code/link, path and arrow are wrappers around an actual ETS path.
            matches=re.findall(r'(?<![\w])(?:[\w.\-/]+/)?([A-Za-z_]\w*)\.ets\b',original)
            if len(set(matches))>1:
                record['reason']='multiple_static_ets_targets_preserved_for_original_parser'
            elif matches:
                cells[3]=' '+matches[0]+'.ets '
                record['normalized']=cells[3].strip()
            normalized.append(record)
            cells[2]=' '+source+' '
            line='|'.join(cells)
        lines.append(line)
    return '\n'.join(lines)+'\n',normalized


def manifest_consumer(stage,scripts,root,out,facts):
    target_current(root,out)
    manifest=root/'spec/baseline/ui-manifest.md'
    present=manifest.is_file()
    text=manifest.read_text(encoding='utf-8-sig') if present else ''
    normalized,rows=normalize_manifest(text,facts) if present else ('',[])
    notes=[]
    if not present:notes.append({'reason':'manifest_absent','handling':'original compiled consumer fallback unchanged'})
    elif not any(r['normalized'] for r in rows):notes.append({'reason':'no_static_ets_mapping_cells','handling':'original parser/status and naming fallback unchanged'})
    for line in text.splitlines():
        cells=line.split('|')
        if len(cells)>=8 and re.fullmatch(r'\s*\d{4}\s*',cells[1]) and not any(r['seq']==cells[1].strip() and r['normalized'] for r in rows):
            notes.append({'seq':cells[1].strip(),'source':cells[2].strip(),'cell':cells[3].strip(),'status':cells[6].strip(),'reason':'no_static_ets_target_in_cell'})
    tracked={};input_paths=[p for p in out.glob('*.json') if not p.name.endswith('.native-input.json')]
    dependency_names={'build_page_mapping':['nav_edges.json','actual_nav.json'],
      'diff_routes':['expected_nav.json','llm_verdicts.json','nav_edges.json','nav_edges_full.json','actual_nav.json']}[stage]
    dependencies=[out/n for n in dependency_names if (out/n).is_file()]
    excludes={'.git','.agents','.codex','.hmigbot-ios','.migbot','.build','node_modules','oh_modules','build','.hvigor','.preview','__pycache__'}
    with tempfile.TemporaryDirectory(prefix='native-route-input-') as temp:
        shadow=Path(temp)/'project';shadow.mkdir();(shadow/'.agents').mkdir();shadow_out=Path(temp)/'out';shadow_out.mkdir()
        # Real, read-only copies ensure pathlib glob semantics equal the original engine.
        # No Android source surrogate and no project/spec mutation is involved.
        for parent,dirs,names in os.walk(root):
            dirs[:]=[d for d in dirs if d not in excludes]
            for name in names:
                path=Path(parent)/name
                if path.suffix not in {'.ets','.json','.json5'} or out==path or out in path.parents:continue
                rel=path.relative_to(root);dest=shadow/rel;dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(path.read_bytes());tracked[str(path)]=sha(path.read_bytes())
        if present:
            dest=shadow/'spec/baseline/ui-manifest.md';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(normalized)
        for p in input_paths:shutil.copy2(p,shadow_out/p.name)
        r=compiled(scripts,stage,env={'ROUTE_VERIFY_ROOT':str(shadow),'ROUTE_VERIFY_OUT':str(shadow_out)})
        # Present real input paths in diagnostics, not ephemeral implementation details.
        print(r.stdout.replace(str(shadow_out),str(out)).replace(str(shadow),str(root)),end='')
        if r.stderr:print(r.stderr.replace(str(shadow_out),str(out)).replace(str(shadow),str(root)),file=sys.stderr,end='')
        if r.returncode:
            write_json(out/(stage+'.native-input.json'),{'stage':stage,'status':'incomplete','input_identity':facts['input_identity'],'outputs_usable':False,'exit_code':r.returncode})
            return r.returncode
        names={'build_page_mapping':['page_mapping.json'],'diff_routes':['diff_routes_report.json','diff_routes_report.md']}[stage]
        payloads=[]
        for name in names:
            p=shadow_out/name
            if not p.is_file():raise MigrationError('Original route engine did not produce '+name)
            payloads.append((out/name,p.read_bytes()))
        # Verify originals still equal the snapshot before publishing this round.
        if manifest.is_file()!=present:raise MigrationError('Manifest availability changed during comparison; rerun')
        if present and sha(manifest.read_bytes())!=sha(text.encode('utf-8')):
            # UTF8 BOM is permitted; compare decoded text as well.
            if manifest.read_text(encoding='utf-8-sig')!=text:raise MigrationError('Manifest changed during route input preparation')
        if any(not Path(p).is_file() or sha(Path(p).read_bytes())!=h for p,h in tracked.items()):raise MigrationError('Target input changed during route comparison; rerun')
        target_current(root,out)
        for p,data in payloads:atomic_write(p,data)
    _metadata(out,stage,facts['input_identity'],[manifest,*dependencies],[p for p,_ in payloads],
      {'manifest_original_sha':sha(manifest.read_bytes()) if present else None,'manifest_normalized_sha':sha(normalized) if present else None,
       'manifest_notes':notes,'manifest_rows':rows,'target_files':tracked,'input_mode':'read-only normalized manifest mirror; original compiled comparator'})
    return 0


# Tokens are deliberately the same inventory used by the original thin probe.
HMOS_INTERACTIVE=['Button(','TextInput(','TextArea(','Slider(','Toggle(','Checkbox(','Radio(','Select(','Search(','Swiper(','Tabs(','.onClick(','bindMenu','bindSheet','bindPopup']
WIDGETS={'TextField':['TextInput(','TextArea(','Search('], 'SecureField':['TextInput('], 'TextEditor':['TextArea('],
         'UITextField':['TextInput(','Search('], 'UITextView':['TextArea('], 'Slider':['Slider('], 'UISlider':['Slider('],
         'Toggle':['Checkbox(','Toggle('], 'UISwitch':['Checkbox(','Toggle('], 'Picker':['Select(','bindMenu'],
         'UISegmentedControl':['Radio(','Tabs(','TabContent('], 'List':['List(','Grid(','ForEach(','WaterFlow('],
         'UITableView':['List(','ForEach('], 'UICollectionView':['Grid(','ForEach(','WaterFlow(']}


MANAGED_TARGET_DIRS={'.agents','.codex','.hmigbot-ios','.migbot'}


def _managed_target_file(root,path,audit=None):
    # Managed ancestors of the checkout are not application directories: inspect
    # only descendants relative to this target (e.g. a .codex worktree is valid).
    try:relative=path.relative_to(root)
    except ValueError:
        try:relative=path.relative_to(root.resolve())
        except ValueError:return False
    for i,part in enumerate(relative.parts[:-1]):
        if part not in MANAGED_TARGET_DIRS:continue
        if audit is not None:
            value=str(path);excluded=audit.setdefault('excluded_paths',[])
            if value not in excluded:
                excluded.append(value);audit['excluded_file_count']=len(excluded)
                managed=str(root.joinpath(*relative.parts[:i+1]))
                roots=audit.setdefault('managed_roots',{});roots[managed]=roots.get(managed,0)+1
        return True
    return False


def _file_products(facts,path):
    owners=facts.get('source_product_owners',{}).get(path)
    if owners is not None:return set(owners)
    return set(facts.get('resource_scope',{}).get('owners',{}).get(path,[]))&set(facts.get('selected_products',[]))


def _localized_values(facts,key,page_products,source_files):
    records=[r for r in facts.get('localization_records',[]) if r['key']==key]
    if not records:return set(),[]
    notes=[];effective=set()
    for path in sorted(source_files):
        products=_file_products(facts,path)&page_products
        if not products:
            notes.append({'key':key,'file':path,'reason':'source_product_ownership_unknown','candidate_resources':[r['file'] for r in records]})
        effective|=products
    if notes or not effective:return set(),notes
    matched=[r for r in records if set(r.get('product_owners',[]))&effective]
    if not matched:
        return set(),[{'key':key,'product_owners':sorted(effective),'reason':'localization_not_declared_for_source_product','candidate_resources':[r['file'] for r in records]}]
    by_product={product:{} for product in sorted(effective)}
    for product,locales in by_product.items():
        for row in matched:
            if product not in row.get('product_owners',[]):continue
            language=row.get('locale')
            locales.setdefault(language,set()).update(row.get('values',[]))
    signatures={product:tuple(sorted((str(locale),tuple(sorted(values))) for locale,values in locales.items())) for product,locales in by_product.items()}
    conflicting=any(len(values)>1 for locales in by_product.values() for values in locales.values())
    if conflicting or len(set(signatures.values()))>1:
        return set(),[{'key':key,'product_owners':sorted(effective),'reason':'conflicting_or_non_equivalent_product_localizations',
            'records':matched,'locale_basis':'per-declared-locale; no runtime language assumed'}]
    missing=[r for r in matched if not r.get('values')]
    if missing:notes.append({'key':key,'reason':'localized_value_not_statically_available','records':missing})
    return {v for r in matched for v in r.get('values',[])},notes


def target_blob(root,page,audit=None):
    candidates=[]
    for p in root.rglob('*.ets'):
        if _managed_target_file(root,p,audit):continue
        if any(x in p.parts for x in {'.git','node_modules','oh_modules','build','.hvigor','.preview'}):continue
        text=p.read_text(encoding='utf-8-sig')
        if re.search(r'\bstruct\s+'+re.escape(page)+r'\b',text):candidates.append(p)
    if audit is not None:audit['matched_declarations']=[str(p) for p in candidates]
    if len(candidates)!=1:
        return None,[],('hmos_file_not_found' if not candidates else 'ambiguous_hmos_declaration')
    primary=candidates[0];paths=[primary];text=primary.read_text(encoding='utf-8-sig')
    for relative in re.findall(r"(?:import|export)\s*\{[^}]*\}\s*from\s*'(\.{1,2}/[^']+)'",text):
        p=(primary.parent/relative).with_suffix('.ets').resolve()
        try:p.relative_to(root.resolve())
        except ValueError:continue
        if p.is_file() and not _managed_target_file(root,p,audit) and p not in paths:paths.append(p)
    return '\n'.join(p.read_text(encoding='utf-8-sig') for p in paths),paths,None


def thin_shell(facts,root,out):
    mapping=read_json(out/'page_mapping.json');reach=read_json(out/'reachability_robust.json')
    controls=[c for c in facts['controls'] if c.get('render_context','host_content')=='host_content'];symbols=facts['symbols'];findings=[];skipped=[];ineligible=[];examined=0
    target_strings={};string_audit={};ets_audits={};localization_unknowns=[]
    for p in root.rglob('string.json'):
        if _managed_target_file(root,p,string_audit):continue
        if any(x in p.parts for x in {'node_modules','oh_modules','build','.git'}):continue
        try:
            for row in read_json(p).get('string',[]):
                if isinstance(row.get('value'),str):target_strings.setdefault(row['name'],set()).add(row['value'])
        except (MigrationError,KeyError):continue
    for row in mapping.get('page_mapping',[]):
        src,dst=row.get('android_page'),row.get('hmos_page')
        if not dst or row.get('spec_status')=='skipped':ineligible.append([src,'mapping_not_planned']);continue
        rr=next((r for r in reach.get('pages',[]) if r.get('android_page')==src),{})
        if rr.get('struct_exists') is False:
            ineligible.append([src,'target_structure_absent_accounted_by_reachability']);continue
        owner_rows=[c for c in controls if c['owner']==src]
        if not owner_rows and not any(s['name']==src for s in symbols) and not any(s['name']==src for s in facts['pages']):skipped.append([src,'native_symbol_not_found']);continue
        # Native reusable View components belong to their host census when instantiated.
        owners={src};changed=True
        while changed:
            changed=False
            for symbol in symbols:
                if symbol['name'] in owners:continue
                for owner in list(owners):
                    # A known source view constructor in the owner's real declaration span.
                    owner_decl=[s for s in symbols if s['name']==owner]
                    if not owner_decl:continue
                    decl=owner_decl[0]
                    # Source facts expose containing control ownership, not runtime item counts.
                    if any(c['owner']==owner and c['type']==symbol['name'] for c in controls):owners.add(symbol['name']);changed=True
        owner_rows=[c for c in controls if c['owner'] in owners]
        count=sum(c['interactive'] for c in owner_rows)
        if count<6:ineligible.append([src,'below_min_ctrls',count]);continue
        examined+=1;target_audit={};ets_audits[src]=target_audit
        blob,paths,reason=target_blob(root,dst,target_audit)
        if reason:skipped.append([src,reason]);continue
        hcount=sum(blob.count(t) for t in HMOS_INTERACTIVE)
        keys={c['text'] for c in owner_rows if c.get('text')}
        hkeys=set(re.findall(r"\$r\('app\.string\.(\w+)'\)",blob))
        shared=set();localization_notes=[]
        page_files={s['file'] for s in [*symbols,*facts['pages']] if s['name']==src}
        page_products=set().union(*(_file_products(facts,path) for path in page_files)) if page_files else set()
        for key in keys:
            translated,notes=_localized_values(facts,key,page_products,{c['file'] for c in owner_rows if c.get('text')==key})
            localization_notes.extend(notes)
            values={key,*translated}
            if key in hkeys or any(values&target_strings.get(hkey,set()) for hkey in hkeys):shared.add(key);continue
            # Literal target labels are legitimate native text counterparts.
            if any(('\''+v+'\'') in blob or ('"'+v+'"') in blob for v in values):shared.add(key)
        if not keys:skipped.append([src,'no_comparable_native_text_facts']);continue
        localization_unknowns.extend({'source_page':src,**note} for note in localization_notes)
        overlap=len(shared)/len(keys);ratio=hcount/count
        types={c['type'] for c in owner_rows}
        gaps=[t for t in sorted(types&WIDGETS.keys()) if not any(token in blob for token in WIDGETS[t])]
        thin=overlap<0.4 and (bool(gaps) or ratio<0.5)
        findings.append({'android_page':src,'hmos_page':dst,'reach_layer':rr.get('layer'),
          'layouts':sorted({c['file'] for c in owner_rows}),'android_ids':len(owner_rows),'android_interactive':count,
          'hmos_interactive':hcount,'string_keys_android':len(keys),'string_keys_shared':len(shared),
          'string_overlap':round(overlap,2),'interactive_ratio':round(ratio,2),'widget_gaps':gaps,
          'severity':round(count*(1-overlap),2),'thin_shell':thin,
          'source_platform':'ios','source_text_basis':'literal/localized text values, not fabricated Android resource keys',
          'source_product_owners':sorted(page_products),'localization_notes':localization_notes,
          'localization_evidence_status':'partial_unknowns' if localization_notes else 'literal-or-product-scoped',
          'source_controls':owner_rows,'target_files':{str(p):sha(p.read_bytes()) for p in paths}})
    report={'thresholds':{'overlap':0.4,'ratio':0.5,'min_ctrls':6},'pairs_checked':len(findings),
        'thin_shells':sum(f['thin_shell'] for f in findings),'skipped':len(skipped),'skipped_detail':skipped,
        'ineligible_detail':ineligible,'eligible_source_pairs':examined,'findings':findings,
        'input_identity':facts['input_identity'],'status':'incomplete' if skipped else 'complete',
        'target_scope':{'managed_directory_names':sorted(MANAGED_TARGET_DIRS),'ets_by_page':ets_audits,'strings':string_audit},
        'localization_unknowns':localization_unknowns,
        'inputs':{n:sha((out/n).read_bytes()) for n in ['page_mapping.json','reachability_robust.json']}}
    # Unresolved applicable pairs are a visible incomplete producer, never empty success.
    code=2 if skipped else 0
    return report,code


def dispatch_if_native(stage,scripts,argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    try:
        hints,root,out=roots(scripts,argv)
        # HarmonyOS extraction is independent of the source language and its facts.
        if stage=='hmos_extract':
            return target_extract(scripts,root,out,argv)
        old=read_json(out/'expected_nav.json') if (out/'expected_nav.json').is_file() else {}
        explicit=hints.platform=='ios' or bool(hints.ios_root)
        native=explicit or old.get('platform')=='ios'
        if stage=='extract_nav_graph' and hints.platform=='android':return None
        if not native:
            cfg=config(root)
            value=hints.src or hints.android_root
            native=cfg.get('source_platform')=='ios' or bool(value and ios_source(root/value))
        if not native:
            if stage in TARGET_CONSUMERS:
                return target_consumer(stage,scripts,root,out,argv)
            return None
        p=argparse.ArgumentParser(description='Native source adapter to original route verification: '+stage)
        p.add_argument('--platform',choices=['ios','android','harmony']);p.add_argument('--ios-root');p.add_argument('--android-root');p.add_argument('--src')
        p.add_argument('--out-dir');p.add_argument('--hmos-root');p.add_argument('--first-party-pkgs')
        p.add_argument('--allow-stale-verdicts',action='store_true')
        args,_=p.parse_known_args(argv) if stage in {'hmos_extract','build_report','hmos_reachability','build_fix_plan'} else (p.parse_args(argv),[])
        facts=_facts(root,{} if stage=='extract_nav_graph' else old,args)
        out.mkdir(parents=True,exist_ok=True)
        if stage=='extract_nav_graph':
            expected=expected_nav(facts)
            write_json(out/'native_source_facts.json',facts);write_json(out/'expected_nav.json',expected)
            print('Native expected navigation: %d edges; %d source unknowns'%(len(expected['edges']),len(facts['unknowns'])))
            _metadata(out,stage,facts['input_identity'],[],[out/'native_source_facts.json',out/'expected_nav.json'])
        elif stage=='llm_worklist':
            value=worklist(facts,old);write_json(out/'llm_worklist.json',value)
            print('Native LLM worklist: %d flag sites / %d unique methods'%(value['count'],value['unique_methods']))
        elif stage=='apply_llm':
            wl=read_json(out/'llm_worklist.json');vp=out/'llm_verdicts.json'
            verdicts=read_json(vp) if vp.is_file() else {'target_rules':{},'method_verdicts':{}}
            nav,full=apply_verdicts(facts,old,wl,verdicts,args.allow_stale_verdicts)
            write_json(out/'nav_edges.json',nav);write_json(out/'nav_edges_full.json',full)
            print('Native verdict coverage: '+str(nav['coverage'])+'; routes='+str(nav['count']))
        elif stage in {'android_dialog_probe','ios_dialog_probe'}:
            worklist(facts,old)  # same source identity and real method spans
            nav=current_nav(facts,old,out)
            dialogs,unknown_targets=modal_specs(facts,nav);value={'android_root':facts['source_root'],'ios_root':facts['source_root'],
                'count':len(dialogs),'route_relevant_count':sum(d['route_relevant'] for d in dialogs.values()),
                'input_identity':facts['input_identity'],'dialogs':dialogs,'unresolved_modal_specs':unknown_targets,
                'unresolved_modal_routes':[e for e in nav['edges'] if e['target_type']=='dialog' and not e['target']]}
            value['status']='partial_unknowns' if value['unresolved_modal_routes'] or unknown_targets or any(d.get('unsupported_content') for d in dialogs.values()) else 'complete'
            write_json(out/'dialog_specs.json',value)
            print('Native dialogs: '+str(value['count']))
        elif stage in {'build_report','hmos_reachability','build_fix_plan'}:
            current_nav(facts,old,out)
            return target_consumer(stage,scripts,root,out,argv)
        elif stage in {'build_page_mapping','diff_routes'}:
            current_nav(facts,old,out)
            return manifest_consumer(stage,scripts,root,out,facts)
        elif stage=='thin_shell_probe':
            current_nav(facts,old,out)
            target_current(root,out)
            receipt=read_json(out/'build_page_mapping.native-input.json')
            if receipt.get('status')!='complete' or receipt.get('input_identity')!=facts['input_identity'] or receipt.get('outputs',{}).get(str(out/'page_mapping.json'))!=sha((out/'page_mapping.json').read_bytes()):
                raise MigrationError('Native page mapping receipt is missing/stale; rerun build_page_mapping')
            if (out/'reachability_robust.json').stat().st_mtime_ns < (out/'page_mapping.json').stat().st_mtime_ns:
                raise MigrationError('Reachability predates current page mapping; rerun hmos_reachability')
            report,code=thin_shell(facts,root,out)
            if code:
                write_json(out/'thin_shell_incomplete.json',report)
                write_json(out/(stage+'.native-input.json'),{'stage':stage,'status':'incomplete','input_identity':facts['input_identity'],'outputs_usable':False})
                print('Native thin-shell incomplete: '+json.dumps(report['skipped_detail'],ensure_ascii=False),file=sys.stderr)
                return code
            write_json(out/'thin_shell_report.json',report)
            md='# Native thin-shell source census\n\nStatus: '+report['status']+'; compared '+str(report['pairs_checked'])+'; THIN '+str(report['thin_shells'])+'\n\n'+json.dumps({'skipped':report['skipped_detail'],'ineligible':report['ineligible_detail']},ensure_ascii=False,indent=2)+'\n'
            atomic_write(out/'thin_shell_report.md',md.encode('utf-8'))
            print('Native thin-shell: compared %d, THIN %d, unresolved skips %d'%(report['pairs_checked'],report['thin_shells'],report['skipped']))
            _metadata(out,stage,facts['input_identity'],[out/n for n in ['expected_nav.json','nav_edges.json','page_mapping.json','reachability_robust.json']],[out/'thin_shell_report.json',out/'thin_shell_report.md'])
            return code
        else:raise MigrationError('Unsupported native route stage: '+stage)
        produced={'extract_nav_graph':['expected_nav.json','native_source_facts.json'],'llm_worklist':['llm_worklist.json'],
          'apply_llm':['nav_edges.json','nav_edges_full.json'],'android_dialog_probe':['dialog_specs.json'],'ios_dialog_probe':['dialog_specs.json']}[stage]
        dependencies={'extract_nav_graph':[],'llm_worklist':['expected_nav.json'],'apply_llm':['expected_nav.json','llm_worklist.json','llm_verdicts.json'],
          'android_dialog_probe':['expected_nav.json','nav_edges.json'],'ios_dialog_probe':['expected_nav.json','nav_edges.json']}[stage]
        _metadata(out,stage,facts['input_identity'],[out/n for n in dependencies],[out/n for n in produced])
        return 0
    except (MigrationError,OSError,ValueError,KeyError,TypeError,RuntimeError) as exc:
        failure={'stage':stage,'source_platform':'harmonyos' if stage=='hmos_extract' or not locals().get('native',False) else 'ios','error':str(exc),'status':'incomplete'}
        if 'out' in locals() and out.is_dir():
            write_json(out/(stage+'.native-failure.json'),failure)
            write_json(out/(stage+'.native-input.json'),{**failure,'outputs_usable':False})
            if stage=='thin_shell_probe':
                write_json(out/'thin_shell_incomplete.json',{**failure,'outputs_usable':False})
        print(json.dumps(failure,ensure_ascii=False),file=sys.stderr)
        return 2
