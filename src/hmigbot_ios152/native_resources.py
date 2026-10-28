"""Declared resource scope for native VERIFY producers only.

Uses the existing Apple-plutil project graph and its conservative synchronized
group subset. This does not change the earlier Source/SPEC input contracts or
claim that project declarations are compiled resource membership evidence.
"""
from pathlib import Path
from hmigbot_ios.core import MigrationError

SUFFIXES = {'.storyboard','.xib','.strings','.xcstrings','.stringsdict','.plist','.entitlements'}
TEXT_SUFFIXES = SUFFIXES | {'.json','.txt','.html','.htm','.csv','.tsv','.svg','.xml','.yaml','.yml','.md','.properties'}


def selected(source, *, text_resources=False):
    cache_key='_native_text_resources' if text_resources else '_native_resources'
    cached = getattr(source,cache_key,None)
    if cached is not None: return cached
    suffixes=TEXT_SUFFIXES if text_resources else SUFFIXES
    candidates = {p for p in source.records if Path(p).suffix.lower() in suffixes}
    if not source.selection:
        if text_resources:
            from hmigbot_ios.core import EXCLUDED
            # No product selection is explicitly root-scoped. Do not mistake
            # managed tools/build output for first-party bundled resource text.
            candidates.update(p.relative_to(source.root).as_posix() for p in source.root.rglob('*')
                              if p.is_file() and not p.is_symlink() and p.suffix.lower() in suffixes
                              and not (EXCLUDED|{'.agents','.codex','.migbot'}).intersection(p.relative_to(source.root).parts))
        result = {'files':sorted(candidates),'scope':'explicit-source-root-no-product-selection',
                  'evidence':'source-snapshot','issues':[],'excluded':[]}
        if text_resources:result['evidence']='explicit-root-text-resources; product membership unselected'
        setattr(source,cache_key,result);return result
    from hmigbot_ios.project_scope import resolve, ROOT_PRODUCTS
    selection,graph = resolve(source.root,source.config['ios']['variant'],_context=True)
    roots = {graph.names[n] for n in selection['targets']}
    products = {key for key,t in graph.targets.items() if t.get('productType') in ROOT_PRODUCTS}
    allowed = (graph.selected_closure-products)|roots
    included, issues, ownership = set(),[],{}
    def include(path,owner):
        if not path.is_relative_to(source.root):
            raise MigrationError('Declared native resource escapes source root')
        if text_resources:
            discovered=[path] if path.is_file() else path.rglob('*')
            candidates.update(p.relative_to(source.root).as_posix() for p in discovered
                              if p.is_file() and not p.is_symlink() and p.suffix.lower() in suffixes)
        names = [path.relative_to(source.root).as_posix()] if path.is_file() else [p for p in candidates if (source.root/p).is_relative_to(path)]
        for name in names:
            if name in candidates:
                included.add(name);ownership.setdefault(name,set()).add(owner)
    def resource(ref,owner,seen=()):
        if ref in seen: raise MigrationError('Cyclic resource group')
        item = graph.object(ref)
        if item.get('isa') == 'PBXVariantGroup':
            for child in graph.list_value(item.get('children',[]),'resource variant children'):
                resource(child,owner,seen+(ref,))
            return
        if item.get('isa') != 'PBXFileReference':
            issues.append({'reason':'unsupported_resource_reference','reference':ref,'target':owner,'kind':item.get('isa')});return
        path = graph.file_path(ref)
        if not path.exists(): raise MigrationError('Declared native resource does not exist: '+str(path))
        include(path,owner)
    for key in sorted(allowed):
        target=graph.targets[key]
        for phase_id,phase in graph.phases(target):
            if phase.get('isa') != 'PBXResourcesBuildPhase': continue
            for _,entry in graph.build_files(phase,phase_id):
                resource(entry.get('fileRef'),target['name'])
    for group in graph.synchronized_declarations:
        owners = set(group['targets']) & allowed
        if not owners: continue
        directory = source.root/group['path']
        if text_resources:
            candidates.update(p.relative_to(source.root).as_posix() for p in directory.rglob('*')
                              if p.is_file() and not p.is_symlink() and p.suffix.lower() in suffixes)
        exceptions = {entry['target']:set(entry['paths']) for entry in group['membership_exceptions']}
        for name in candidates:
            path=source.root/name
            if not path.is_relative_to(directory):continue
            local=path.relative_to(directory).as_posix()
            eligible = [tid for tid in owners if local not in exceptions.get(tid,set())]
            for tid in eligible: include(path,graph.targets[tid]['name'])
        issues.append({'reason':'synchronized_resource_format_subset','group':group['id'],
                       'evidence':'project-declared-membership-not-compiled-resource-evidence'})
    # Info/entitlements files are build-setting inputs, not resource phase items.
    for config in graph.selected_configs:
        if config['owner'] not in {graph.targets[k]['name'] for k in allowed}: continue
        for key in ('INFOPLIST_FILE','CODE_SIGN_ENTITLEMENTS'):
            raw=config['settings'].get(key)
            if not raw:continue
            if not isinstance(raw,str):
                issues.append({'reason':'unresolved_resource_setting','target':config['owner'],'key':key});continue
            value=raw.replace('$(SRCROOT)/','').replace('${SRCROOT}/','')
            if '$' in value:
                issues.append({'reason':'unresolved_resource_setting','target':config['owner'],'key':key,'value':raw});continue
            include(graph.path.parent.parent/value,config['owner'])
    result={'files':sorted(included),'scope':'selected-product-targets',
            'evidence':'project-declared-resource-membership',
            'owners':{p:sorted(v) for p,v in ownership.items()},'issues':issues,
            'excluded':[{'file':p,'reason':'not-declared-for-selected-products'} for p in sorted(candidates-included)]}
    if text_resources:result['resource_text_scope']='selected-declared-text-resources-including-json-and-assets'
    setattr(source,cache_key,result);return result
