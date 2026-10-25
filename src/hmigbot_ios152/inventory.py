"""Native declarations feeding the existing Phase A / B input documents."""
from collections import defaultdict
from pathlib import Path
import json, os, re
from hmigbot_ios.core import safe_child
from hmigbot_ios.xcode import OpenStep, project_inventory, dependency_inventory

def modules(source,explicit=None):
    result={}; memberships=defaultdict(set); imports={}; symbols={}
    for p in sorted(source.records):
        if not p.endswith('.xcodeproj/project.pbxproj'): continue
        document=OpenStep(safe_child(source.root,p).read_text(encoding='utf-8-sig')).parse()
        objects=document.get('objects',{})
        for key,obj in objects.items():
            if obj.get('isa')!='PBXNativeTarget': continue
            name=obj.get('name',key)
            deps=[objects.get(objects.get(d,{}).get('target'),{}).get('name') for d in obj.get('dependencies',[])]
            result[name]={'root':str(Path(p).parent.parent).replace('\\','/'),'gradle_deps':[n for n in deps if n],
                          'source_project':p,'source_target':key,'product_type':obj.get('productType')}
    if explicit:
        result={Path(p).name:{'root':p,'gradle_deps':[]} for p in explicit.split(',')}
    if not result: result={source.root.name:{'root':'.','gradle_deps':[]}}
    if source.selection:
        products={n for n,v in result.items() if v.get('product_type') in {
                  'com.apple.product-type.application','com.apple.product-type.app-extension'}}
        allowed=(set(source.selection['target_closure'])-products)|set(source.selection['targets'])
        result={n:v for n,v in result.items() if n in allowed}
        for info in result.values(): info['gradle_deps']=[n for n in info['gradle_deps'] if n in result]
        for f in source.selection['source_membership']:
            for target in set(f['targets'])&set(result): memberships[f['path']].add(target)
    for p in sorted(source.files):
        if not memberships[p]:
            candidates=[n for n,v in result.items() if v['root']=='.' or p.startswith(v['root'].rstrip('/')+'/')]
            # Ambiguous target membership remains visible, not a guessed module edge.
            if len(candidates)==1: memberships[p].add(candidates[0])
        code=source.code(p)
        if p.endswith('.swift'):
            nodes=source.syntax(p)['nodes']
            imports[p]=[n['value']['module'].split('.')[0] for n in nodes if n['kind']=='import']
            for node in nodes:
                if node['kind']=='type':
                    value=node['value']; signature=value['kind']+' '+value['name']
                    if value.get('inherits'): signature+=': '+', '.join(value['inherits'])
                    symbols.setdefault(value['name'].strip('`'),[]).append({'file':p,'signature':signature,'modules':sorted(memberships[p])})
        else:
            imports[p]=re.findall(r'\bimport\s+(\w+)',code)
            for match in re.finditer(r'\b(?:public\s+|open\s+)?(?:class|struct|enum|protocol)\s+(\w+)[^{]*',code):
                symbols.setdefault(match[1],[]).append({'file':p,'signature':match[0].strip(),'modules':sorted(memberships[p])})
    edges=[]; signatures={}
    for p,targets in imports.items():
        for callee in targets:
            if callee not in result: continue
            for caller in sorted(memberships[p]-{callee}):
                edges.append({'caller_module':caller,'callee_module':callee,'file':p,'symbol':callee})
    for symbol,decls in symbols.items():
        for decl in decls:
            if any(d['callee_module'] in decl['modules'] for d in edges): signatures[symbol]=decl
    pending={name:set(info['gradle_deps'])&set(result) for name,info in result.items()}; order=[]
    while pending:
        ready=sorted(n for n,deps in pending.items() if not deps)
        if not ready: order.extend(sorted(pending)); break
        for n in ready: order.append(n); pending.pop(n)
        for deps in pending.values(): deps.difference_update(ready)
    return {'src':source.root.name,'stats':{'modules':len(result),'files':len(source.files),
            'cross_module_edges':len(edges),'shared_models':0},'modules':result,'module_topo_order':order,
            'cross_module_edges':edges,'edges_by_module':{n:[e for e in edges if n in (e['caller_module'],e['callee_module'])] for n in result},
            'shared_models':[],'seam_signatures':signatures,
            'input_limitations':['Dynamic DI/event/reflection seams require the original Phase 0 semantic supplement',
                                'Target membership must be selected before ambiguous shared sources can be attributed']}

def api(source):
    services=[]; urls=[]; constants=[]; interceptors=[]; bodies=[]; models=[]
    for p in sorted(source.files):
        text=source.code(p,strings=True); code=source.code(p); endpoints=[]
        for m in re.finditer(r'@?"(https?://[^"\n]+)"',text):
            urls.append({'url':m[1],'file':p,'line':text.count('\n',0,m.start())+1})
        for m in re.finditer(r'\b(?:dataTask|downloadTask|uploadTask|data|request)\s*\(',code):
            line=code.count('\n',0,m.start())+1
            endpoints.append({'method':'unknown','path':'dynamic','path_is_dynamic':True,
                              'file':p,'line':line,'source_symbol':m[0][:-1].strip(),'callers':[],
                              'static_headers':[],'parameters':[],'evidence':'source_call_requires_dataflow_review'})
        if endpoints: services.append({'name':Path(p).stem,'file':p,'endpoints':endpoints})
        if re.search(r'\b(?:RequestAdapter|RequestInterceptor|URLProtocol)\b',code):
            interceptors.append({'file':p,'name':Path(p).stem,'evidence':['native_interceptor_declaration']})
        if re.search(r'\b(?:Codable|Decodable|Encodable)\b',code): models.append({'file':p,'name':Path(p).stem,'fields':[],
            'evidence':'Read CodingKeys, custom init(from:), defaults and failure ordering in Phase 2'})
        for m in re.finditer(r'\b(?:let|var)\s+(\w+)\s*(?::[^=\n]+)?=\s*@?"([^"\n]*)"',text):
            constants.append({'name':m[1],'value':m[2],'file':p,'line':text.count('\n',0,m.start())+1})
        for line,body in enumerate(source.text(p).splitlines(),1):
            if re.search(r'\b(?:httpBody|httpMethod|setValue|addValue|JSONEncoder)\b',code.splitlines()[line-1]):
                bodies.append({'file':p,'line':line,'excerpt':body.strip()})
    return {'platform':'ios','services':services,'base_urls':[],'url_constants':constants,
            'api_related_constants':[],'hardcoded_urls':urls,'third_party_domains':[],
            'interceptors':interceptors,'body_assembly_sites':bodies,'gradle_config':[],
            'bean_classes':models,'scan_limitations':['Lexical call sites; Phase 1b/2 must resolve dynamic paths, parameters, signing and response behavior']}

def overview(source):
    files=list(source.records.values())
    projects,issues=project_inventory(source.root,files)
    dependencies,dependency_issues=dependency_inventory(source.root,files)
    from .source import entrypoints
    try: entries=entrypoints(source)
    except Exception as exc:
        from hmigbot_ios.core import MigrationError
        if not isinstance(exc,MigrationError): raise
        entries=[]; issues.append({'code':'source_context_unresolved','message':str(exc)})
    return {'source_platform':'ios','source_sha256':source.fingerprint,'source_files':sorted(source.files),
            'discovery_only':source.selection is None,'projects':projects,'dependencies':dependencies,'entrypoints':entries,
            'issues':issues+dependency_issues,'source_view':source.view.reference if source.view else None,
            'evidence':'source declarations; not a successful build or runtime observation'}
