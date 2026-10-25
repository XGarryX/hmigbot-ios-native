"""Source C2/C3 checks, retaining the original C1/C4 implementation.

The original engine's complete output is preserved separately.
No decision is derived by filtering an original FAIL.
"""
from pathlib import Path
import argparse, hashlib, json, os, platform, re, subprocess, sys, tempfile, uuid, shutil
from datetime import datetime, timezone
from collections.abc import Mapping

NODE=Path('/Applications/DevEco-Studio.app/Contents/tools/node/bin/node')
PARSER=Path('/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/ets/build-tools/ets-loader/node_modules/typescript')

def source_files(project):
    # Original ref_graph_lib.EtsRefGraph skip_parts, by directory name at every
    # depth. Keep legal application directories named "spec" discoverable.
    excluded={'oh_modules','node_modules','build','.cxx','.preview','.claude',
              '.agents','.codex','.git','.hvigor','__pycache__'}
    found=[]
    for directory,dirs,names in os.walk(project):
        dirs[:]=[d for d in dirs if d not in excluded and not
                 (Path(directory)==project and d in {'.hmigbot-ios','.migbot'})]
        parts=Path(directory).relative_to(project).parts
        if not any(parts[i:i+3]==('src','main','ets') for i in range(len(parts)-2)):continue
        found.extend(Path(directory)/name for name in names if name.endswith('.ets'))
    return sorted(found)

def preserve_previous(path):
    if path.exists() or path.is_symlink():
        archive=path.parent/'previous-results';archive.mkdir(exist_ok=True)
        path.rename(archive/(path.name+'.'+uuid.uuid4().hex))

class EvidenceIOError(OSError):
    """Failure writing the source adapter's additional evidence, not a detector."""

class SourceInputChangedError(RuntimeError):
    """A measurement cannot be published after its inputs changed."""

def plan_signature(plan_path):
    """The public parser reads only its index and explicit detail pointers."""
    from plan_lib.feature_plan_parser import _iter_slice_sections
    paths=set(plan_path.parent.rglob('*.md'));paths.add(plan_path)
    try:
        text=plan_path.read_text(encoding='utf-8',errors='replace').lstrip('\ufeff')
        for section,_ in _iter_slice_sections(text):
            match=re.search(r'^detail\s*[:：]\s*(\S+)',section,re.MULTILINE)
            if match:
                relative=match.group(1)
                if relative.startswith('plans/'):relative=relative[len('plans/'):]
                paths.add(plan_path.parent/relative)
    except OSError:
        pass  # Initial parser errors still belong to the original engine.
    # Normalize both sides before relpath: Python resolve() preserves APFS case
    # aliases, whereas the source adapter uses the kernel's physical root.
    try:base=Path(physical_file(plan_path.parent)['physical_path'])
    except (OSError,RuntimeError):base=plan_path.parent.resolve()
    signature={}
    for path in sorted(paths):
        try:physical=Path(physical_file(path)['physical_path'])
        except (OSError,RuntimeError):physical=path.resolve()
        name=os.path.relpath(physical,base)
        try:signature[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as error:signature[name]={'error':type(error).__name__,'errno':error.errno}
    return signature

def measurement_file(path):
    """Record initial unreadability without changing original detector policy."""
    result={}
    try:
        stat=path.stat();result.update(device=stat.st_dev,inode=stat.st_ino,resolved=str(path.resolve()))
        result['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as error:result.update(error=type(error).__name__,errno=error.errno)
    return result

class MeasurementGuard:
    def __init__(self,project,plan_path,scope,cse_files,handoffs,registry,expected_plan):
        self.project=project;self.plan_path=plan_path;self.registry=registry
        self.declared=[project/Path(name) for name in [*scope,*cse_files,*handoffs]]
        self.before=self.snapshot()
        if self.before['plan']!=expected_plan:raise SourceInputChangedError('Plan changed during input preparation')

    def snapshot(self):
        sources=list(dict.fromkeys([*source_files(self.project),*self.declared]))
        return {'plan':plan_signature(self.plan_path),
                'sources':{str(p):measurement_file(p) for p in sources},
                'registry':measurement_file(self.registry)}

    def verify(self):
        if self.snapshot()!=self.before:raise SourceInputChangedError('Shared plan/source/registry/handoff inputs changed during measurement')

def physical_file(path):
    """macOS kernel file identity and true on-disk spelling, through a read fd."""
    try:
        import fcntl
        command=fcntl.F_GETPATH
    except (ImportError,AttributeError) as error:
        raise RuntimeError('macOS F_GETPATH capability is unavailable') from error
    fd=os.open(path,os.O_RDONLY)
    try:
        stat=os.fstat(fd)
        try:raw=fcntl.fcntl(fd,command,b'\0'*1024)
        except OSError as error:raise RuntimeError('macOS F_GETPATH failed: '+str(error)) from error
        return {'device':stat.st_dev,'inode':stat.st_ino,
                'physical_path':raw.split(b'\0',1)[0].decode('utf-8')}
    finally:os.close(fd)

class SourceIndex:
    def __init__(self,project):
        self.root_info=physical_file(project)
        self.root=Path(self.root_info['physical_path'])
        self.records={}
        self.identities={}

    def observe(self,path):
        name=str(path)
        if name not in self.records:
            record=physical_file(path)
            identity=(record['device'],record['inode'])
            record['fact_key']=self.identities.setdefault(identity,record['physical_path'])
            self.records[name]=record
        return self.records[name]

    def key(self,path):return self.observe(path)['fact_key']

class FileFacts(Mapping):
    """Physical lookup, while C2 retains its original lexical file candidates."""
    def __init__(self,files,index):self.files=files;self.index=index
    def __getitem__(self,path):return self.files[self.index.key(Path(path))]
    def __iter__(self):return iter(self.files)
    def __len__(self):return len(self.files)
    def __contains__(self,path):
        try:return self.index.key(Path(path)) in self.files
        except OSError:return False

def source_snapshot(project,spec):
    index=SourceIndex(project)
    candidates=source_files(index.root)
    explicit=[index.root/row.file for row in spec.cross_slice_edits if (index.root/row.file).is_file()]
    inputs=list(dict.fromkeys([*candidates,*explicit]))
    digests={};records={};sdk_files=[]
    for path in inputs:
        record=dict(index.observe(path));key=record['fact_key']
        if key not in digests:
            sdk_files.append(Path(key));digests[key]=hashlib.sha256(Path(key).read_bytes()).hexdigest()
        record['sha256']=digests[key];records[str(path)]=record
    signature={'project':index.root_info,'c2_candidates':[str(p) for p in candidates],
               'sdk_inputs':records}
    return candidates,sdk_files,index,signature

def record_evidence(path,text):
    try:path.write_text(text,encoding='utf-8')
    except OSError as error:raise EvidenceIOError(str(error)) from error

def begin_evidence(output):
    run_id=uuid.uuid4().hex
    evidence=output.parent/'wiring-evidence'/output.stem
    try:
        output.parent.mkdir(parents=True,exist_ok=True)
        if evidence.exists() or evidence.is_symlink():
            archive=output.parent/'wiring-evidence-archive';archive.mkdir(exist_ok=True)
            evidence.rename(archive/(output.stem+'.'+uuid.uuid4().hex))
        evidence.mkdir(parents=True,exist_ok=False)
        record_evidence(evidence/'run.json',json.dumps({'run_id':run_id,
            'started_at':datetime.now(timezone.utc).isoformat()},ensure_ascii=False,indent=2))
        preserve_previous(output)
    except OSError as error:raise EvidenceIOError(str(error)) from error
    return evidence,run_id

def ets_component_helper():
    for parent in Path(__file__).resolve().parents:
        runtime=parent/'runtime.json'
        if runtime.is_file():
            root=(parent/json.loads(runtime.read_text(encoding='utf-8'))['runtime_relative']).resolve()
            helper=root/'src/hmigbot_ios152/ets_components.cjs'
            if helper.is_file():return helper
        helper=parent/'src/hmigbot_ios152/ets_components.cjs'
        if helper.is_file():return helper
    raise RuntimeError('Bundled ETS component context helper is unavailable')

def sdk_runtime(project):
    parser_override=os.environ.get('HMIGBOT_ETS_PARSER')
    node_override=os.environ.get('HMIGBOT_NODE')
    apps=[]
    for home in [Path('/Applications'),Path.home()/'Applications']:
        if home.is_dir():apps.extend(home.glob('*DevEco*.app'))
    nodes=[Path(node_override)] if node_override else [app/'Contents/tools/node/bin/node' for app in apps]
    nodes.append(NODE)
    node_path=next((p for p in nodes if p.is_file() and os.access(p,os.X_OK)),None)
    if node_override and node_path!=Path(node_override):raise RuntimeError('Configured Node runtime is unavailable')
    if node_path is None:raise RuntimeError('Official DevEco SDK Node runtime unavailable')
    sdk_roots=[]
    for key in ['DEVECO_SDK_HOME','OHOS_SDK_HOME','HOS_SDK_HOME']:
        if os.environ.get(key):sdk_roots.append(Path(os.environ[key]))
    properties=project/'local.properties'
    if properties.is_file():
        for line in properties.read_text(encoding='utf-8').splitlines():
            m=re.match(r'\s*(?:sdk\.dir|hwsdk\.dir|ohos\.sdk\.dir)\s*=\s*(.*?)\s*$',line)
            if m:sdk_roots.append(Path(m.group(1).replace('\\:',':').replace('\\ ',' ')))
    if not parser_override and not sdk_roots:
        raise RuntimeError('Project SDK is not configured in local.properties or SDK environment; set the selected official SDK parser explicitly')
    suffixes=['openharmony/ets/build-tools/ets-loader/node_modules/typescript','ets/build-tools/ets-loader/node_modules/typescript']
    parsers=[Path(parser_override)] if parser_override else []
    for root in sdk_roots if not parser_override else []:
        for base in [root,root/'default',*sorted(root.glob('*'))]:
            parsers.extend(base/s for s in suffixes)
    candidates=[]
    for parser in parsers:
        if not ((parser/'package.json').is_file() or parser.is_file()):continue
        parser=parser.resolve()
        loader=next((p for p in [parser,*parser.parents] if p.name=='ets-loader'),None)
        if loader is None:continue
        package=loader.parent.parent/'oh-uni-package.json'
        if not package.is_file():continue
        metadata=json.loads(package.read_text(encoding='utf-8'))
        if not any(p[0]==parser for p in candidates):candidates.append((parser,package,metadata))
    profile=project/'build-profile.json5'
    configured=[]
    if profile.is_file() and candidates:
        loader=next(p for p in [candidates[0][0],*candidates[0][0].parents] if p.name=='ets-loader')
        json5=loader/'node_modules/json5'
        program="const fs=require('fs'),parser=require(process.argv[1]);const data=parser.parse(fs.readFileSync(process.argv[2],'utf8'));const versions=[];function walk(o){if(!o||typeof o!=='object')return;for(const [k,v] of Object.entries(o)){if(k==='compileSdkVersion')versions.push(String(v));else walk(v);}}walk(data);process.stdout.write(JSON.stringify(versions));"
        parsed_profile=subprocess.run([str(node_path),'-e',program,str(json5),str(profile)],capture_output=True,text=True,encoding='utf-8')
        if parsed_profile.returncode:raise RuntimeError('Cannot parse project SDK selection with the official SDK JSON5 dependency')
        configured=json.loads(parsed_profile.stdout)
    def matches(metadata,version):
        api=re.search(r'\((\d+)\)\s*$',version)
        return (api.group(1) if api else version) in [str(metadata.get('apiVersion')),str(metadata.get('platformVersion'))]
    if configured:candidates=[row for row in candidates if all(matches(row[2],version) for version in configured)]
    if len(candidates)!=1:raise RuntimeError('Selected project SDK parser is missing or ambiguous; use the exact official SDK path')
    parser_path,package,metadata=candidates[0]
    return node_path,parser_path,{'package':str(package),'packageSha256':hashlib.sha256(package.read_bytes()).hexdigest(),'metadata':metadata,'configuredCompileSdk':configured,'configuredSdkRoots':[str(p) for p in sdk_roots],'explicitParser':bool(parser_override)}

def failure(row,code,reason,action):
    return dict(row,status='FAIL',failed_check=code,reason=reason,repair_action=action)

def category(rows):
    return {'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'details':rows}

def original_priority(path,project):
    # Keep original directory precedence among real exact-case candidates.
    priority=['viewmodels','models','pages','components','services','repositories','database']
    parts=path.relative_to(project).parts
    return (next((priority.index(x) for x in parts if x in priority),len(priority)),str(path.relative_to(project)))

def caller_file(name,files,facts,project):
    candidates=[p for p in files if p.name==name+'.ets']
    return sorted(candidates,key=lambda p:original_priority(p,project))[0] if candidates else None

def canonical_reference(caller,target,member,project,files,facts):
    """Prove a real reference to a constructed Root provider, never a name exemption.

    Original 1.5.2 _common.md requires capabilityTable consumption and forbids a
    consumer from constructing slot classes. This proves that same allocation
    through the imported Root, with a unique declared target type.
    """
    from ref_graph_lib.import_resolver import resolve_import_path
    roots=[p for p in files if p.name=='AppAssembly.ets' and p.parent.name=='ets']
    targets=[(p,d) for p in files for d in facts[str(p)]['declarations'] if d['name']==target]
    if len(roots)!=1 or len(targets)!=1 or not member:return False
    root=roots[0];target_id=(str(targets[0][0]),targets[0][1]['name'])
    def resolve_symbol(path,name,seen=None):
        seen=set() if seen is None else seen
        key=(str(path),name)
        if key in seen or str(path) not in facts:return None
        seen=seen|{key};info=facts[str(path)]
        declarations=[d for d in info['declarations'] if d['name']==name or name=='default' and d.get('default')]
        if len(declarations)==1:return (path,declarations[0])
        for imp in info['imports']:
            if '.' in name and imp.get('namespace')==name.split('.',1)[0]:
                dest=resolve_import_path(imp['source'],path,project)
                return resolve_symbol(dest,name.split('.',1)[1],seen) if dest is not None else None
            symbol=next((x for x in imp['names'] if x['local']==name),None)
            if symbol:
                dest=resolve_import_path(imp['source'],path,project)
                return resolve_symbol(dest,symbol['imported'],seen) if dest is not None else None
        found=[]
        for exp in info.get('reexports',[]):
            symbol=next((x for x in exp['names'] if x['exported']==name),None) if exp['names'] is not None else {'imported':name}
            if symbol:
                dest=resolve_import_path(exp['source'],path,project) if exp['source'] else path
                resolved=resolve_symbol(dest,symbol['imported'],seen) if dest is not None else None
                if resolved:found.append(resolved)
        return found[0] if len(found)==1 else None
    def compatible(resolved,seen=None):
        if resolved is None:return False
        path,decl=resolved;key=(str(path),decl['name']);seen=set() if seen is None else seen
        if key==target_id:return True
        if key in seen:return False
        return any(compatible(resolve_symbol(path,h),seen|{key}) for h in decl['heritage'])
    def has_member(resolved,seen=None):
        if resolved is None:return False
        path,decl=resolved;key=(str(path),decl['name']);seen=set() if seen is None else seen
        if key in seen:return False
        return any(p['name']==member for p in decl['properties']) or any(has_member(resolve_symbol(path,h),seen|{key}) for h in decl['heritage'])
    if not has_member(targets[0]):return False
    def origins(path,name,seen=None,local=False):
        key=(str(path),name,local);seen=set() if seen is None else seen
        if key in seen or str(path) not in facts:return set()
        seen=seen|{key};info=facts[str(path)];found=set()
        found.update((str(path),o['name']) for o in info['objects'] if o['name']==name and (local or o['exported']))
        if local:
            for imp in info['imports']:
                symbol=next((x for x in imp['names'] if x['local']==name),None)
                if symbol:
                    dest=resolve_import_path(imp['source'],path,project)
                    if dest is not None:found.update(origins(dest,symbol['imported'],seen))
        for binding in info.get('bindings',[]):
            if binding['name']==name and binding['const'] and binding['topLevel'] and binding.get('identifier') and (local or binding['exported']):
                found.update(origins(path,binding['identifier'],seen,True))
        for exp in info.get('reexports',[]):
            symbol=next((x for x in exp['names'] if x['exported']==name),None) if exp['names'] is not None else {'imported':name}
            if not symbol:continue
            dest=resolve_import_path(exp['source'],path,project) if exp['source'] else path
            if dest is not None:found.update(origins(dest,symbol['imported'],seen,not exp['source']))
        return found
    root_id={(str(root),'capabilityTable')}
    def imported_roots(path):
        prefixes=['capabilityTable'] if path==root else []
        for imp in facts[str(path)]['imports']:
            dest=resolve_import_path(imp['source'],path,project)
            if dest is None or str(dest) not in facts:continue
            prefixes.extend(x['local'] for x in imp['names'] if origins(dest,x['imported'])==root_id)
            if imp.get('namespace'):
                names={'capabilityTable'}
                names.update(x['exported'] for e in facts[str(dest)].get('reexports',[]) for x in (e['names'] or []))
                prefixes.extend(imp['namespace']+'.'+name for name in names if origins(dest,name)==root_id)
        return prefixes
    bindings=imported_roots(caller)
    tables=[o for o in facts[str(root)]['objects'] if o['name']=='capabilityTable' and o['exported'] and o.get('closedLiteral')]
    if len(tables)!=1:return False
    table=tables[0]
    if len(table['properties'])!=len({p['name'] for p in table['properties']}):return False
    table_type=resolve_symbol(root,table.get('type',''))
    def allocation(slot,seen=None):
        if slot.get('constructor'):return resolve_symbol(root,slot['constructor'])
        name=slot.get('identifier');seen=set() if seen is None else seen
        if not name or name in seen:return None
        aliases=[b for b in facts[str(root)]['bindings'] if b['name']==name and b['const'] and b['topLevel']]
        return allocation(aliases[0],seen|{name}) if len(aliases)==1 else None
    def stable_slot(slot):
        safe_reads={'Object.keys','Object.values','Object.entries','Object.freeze','Object.seal','Object.isFrozen','Object.isSealed','Object.getOwnPropertyDescriptor','Object.getOwnPropertyNames'}
        for path in files:
            aliases=set(imported_roots(path));info=facts[str(path)]
            if not aliases:continue
            # Local lexical shadows do not prove an imported Root binding.
            base_names={a.split('.')[0] for a in aliases}
            if any(b['name'] in base_names and not (path==root and b['name']=='capabilityTable' and b['topLevel']) for b in info['bindings']):return False
            changed=True
            while changed:
                changed=False
                for b in info['bindings']:
                    expression=(b.get('expression') or '').strip()
                    if expression in aliases and b['name'] not in aliases:aliases.add(b['name']);changed=True
            for write in info['writes']:
                normalized=write.replace('?.','.')
                if any(normalized==a or normalized==a+'.'+slot or normalized.startswith(a+'[') for a in aliases):return False
            for call in info['calls']:
                if call['callee'] in safe_reads:continue
                if any(arg in aliases for arg in call['args']):return False
        return True
    for slot in table['properties']:
        provider=allocation(slot)
        # No empty object, as-cast, unconstructed slot or decorative Root import.
        if provider is None or not stable_slot(slot['name']):continue
        public_type=None
        if table_type:
            type_path,type_decl=table_type
            prop=next((p for p in type_decl['properties'] if p['name']==slot['name']),None)
            if prop:public_type=resolve_symbol(type_path,prop['type'])
        if not compatible(provider) and not compatible(public_type):continue
        for binding in bindings:
            expected=binding+'.'+slot['name']+'.'+member
            if any(r['text'].replace('?.','.')==expected for r in facts[str(caller)]['references']):return True
    return False

def calculate_c2(spec,project,files,facts,parse_ets_file):
    rows=[]
    def instantiated(path,target):
        info=parse_ets_file(path)
        if info.has_instantiation(target) or info.has_typed_ref(target):return True
        return bool(re.search(r'\b'+re.escape(target)+r'\s*\(',path.read_bytes().decode('utf-8')))
    for i,ip in enumerate(spec.integration_points,1):
        row={'ip_id':f'ip_{i:03d}','description':ip.description}
        m=re.match(r'^([A-Z][A-Za-z0-9_]*)\.',ip.handler_text)
        name=m.group(1) if m else None
        if name is None:
            if ip.target_class and not any(instantiated(p,ip.target_class) for p in files):
                rows.append(failure(row,'C2_VM_NOT_INSTANTIATED',f'{ip.target_class} is not instantiated in project.',f'Instantiate {ip.target_class} in the calling page/component.'))
            else:rows.append(dict(row,status='PASS',note='pair without derivable page — target instantiation verified only'))
            continue
        caller=caller_file(name,files,facts,project)
        if caller is None:
            rows.append(failure(row,'C2_PAGE_NOT_FOUND',f'Caller page/component `{name}.ets` not found in project.',f'Create {name}.ets or fix the integration_points entry.'));continue
        relative=str(caller.relative_to(project));text=caller.read_bytes().decode('utf-8')
        if ip.handler_local and not re.search(r'\b'+re.escape(ip.handler_local)+r'\b',text):
            rows.append(failure(row,'C2_HANDLER_NOT_WIRED',f'`{ip.handler_local}` not found in {relative}.',f'Wire `{ip.handler_local}` in {relative} per the pair `{ip.description}`.'));continue
        member_match=re.search(r'\.([A-Za-z_][A-Za-z0-9_]*)\s*(?:\([^)]*\))?\s*$',ip.target_text)
        member=member_match.group(1) if member_match else None
        wired=not ip.target_class or instantiated(caller,ip.target_class) or canonical_reference(caller,ip.target_class,member,project,files,facts)
        if not wired:
            target=ip.target_class
            rows.append(failure(row,'C2_VM_NOT_INSTANTIATED',f'{relative} does not instantiate {target} (no `new {target}(`, `{target}.getInstance(`, typed field, or render call).',f'Add `private vm: {target} = new {target}()` inside the @ComponentV2 struct of {relative}.'));continue
        rows.append(dict(row,status='PASS',caller=relative))
    return category(rows)

def mask_spans(text,spans):
    chars=list(text)
    for span in spans:
        for i in range(span['start'],span['end']):
            if chars[i] not in '\r\n':chars[i]=' '
    return ''.join(chars)

def verified_body(method,text,fact):
    if not method.get('block',True):return method['body']
    masked=mask_spans(text,fact['literals']+fact['comments'])
    start=method['bodyStart'];depth=0;end=None
    if masked[start]!='{':raise ValueError('SDK method body does not start with a brace')
    for i in range(start,len(masked)):
        if masked[i]=='{':depth+=1
        elif masked[i]=='}':
            depth-=1
            if depth==0:end=i+1;break
    if end!=method['bodyEnd']:raise ValueError('SDK method body range cannot be verified lexically')
    without_comments=mask_spans(text,fact['comments'])
    return without_comments[start+1:end-1]

def registered_other_slot(marker, cse, registry, source_file=None):
    """Prove ownership of an outside-body marker; unknown ownership stays FAIL."""
    if registry is None:return False
    from skeleton_lib.patterns import FWD_REF_MARKER
    # Original audit must recognize the PID/resolve_by grammar too. Keep the
    # complete values (including spaces); key order after resolve_by may vary.
    parsed=FWD_REF_MARKER.match(marker)
    if parsed is None:return False
    keys=list(re.finditer(r'(?:^|\s)(resolve_by|kind|slot)=',marker))
    fields={}
    for i,key in enumerate(keys):
        if key.group(1) in fields:return False
        end=keys[i+1].start() if i+1<len(keys) else len(marker)
        fields[key.group(1)]=marker[key.end():end].strip()
    if set(fields)!={'resolve_by','kind','slot'} or fields['kind']!='forward-ref':return False
    target=fields['slot']
    if target in (cse.handler,cse.slot):return False
    entry=registry.get_entry(parsed.group('p_id'))
    return bool(entry and entry['kind']=='forward-ref' and entry['status'] in {'registered','pending','due','fired'}
                and entry['location']==(source_file or cse.file)+'#'+target
                and entry['resolve_by']==fields['resolve_by'])

def registry_snapshot(path):
    try:return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    except OSError as error:return {'path':str(path),'error':type(error).__name__+': '+str(error)}

def calculate_c3(spec,project,facts,registry=None):
    rows=[]
    for i,cse in enumerate(spec.cross_slice_edits,1):
        row={'cse_id':f'cse_{i:03d}','file':cse.file,'handler':cse.handler,'slot':cse.slot,'resolve_by':cse.resolve_by}
        path=project/cse.file
        if not path.is_file():
            rows.append(failure(row,'C3_FILE_NOT_FOUND',f'Target file does not exist: {cse.file}',f'Create or locate {cse.file}; the file must exist before cross_slice_edits can wire handlers in it.'));continue
        text=path.read_bytes().decode('utf-8');match=re.search(r'\b'+re.escape(cse.handler)+r'\b',text)
        if not match:
            rows.append(failure(row,'C3_HANDLER_NOT_FOUND',f'Handler `{cse.handler}` not found in {cse.file}.',f'Add handler `{cse.handler}` in {cse.file} per spec.'));continue
        fact=facts[str(path)];methods=fact['methods']
        # Ownership uses the physical path, not a case/symlink spelling alias.
        try:registry_file=str(Path(facts.index.key(path)).relative_to(facts.index.root))
        except ValueError:registry_file=None
        own=next((m for m in methods if m['name']==cse.handler),None)
        # Retain legacy +/- two lines. Exempt only a proven other method body,
        # or a registered future slot outside this method; never its own body.
        anchor=own['nameStart'] if own else match.start()
        finish=own['bodyEnd'] if own else match.end()
        line_at=lambda position:len(re.findall(r'\r\n|\r|\n',text[:position]))
        first=line_at(anchor);last=line_at(finish)
        marker_found=False
        markers=list(re.finditer(r'//\s*FWD-REF:',text))
        for marker_index,marker in enumerate(markers):
            # A containing outer method is never evidence against ownership.
            inside_own=own and own['bodyStart']<=marker.start()<own['bodyEnd']
            if inside_own:marker_found=True;break
            line=line_at(marker.start())
            if not max(0,first-2)<=line<=last+2:continue
            elsewhere=any(m is not own and m['bodyStart']<=marker.start()<m['bodyEnd'] and not
              (own and own['bodyStart']<=m['bodyStart'] and m['bodyEnd']<=own['bodyEnd']) for m in methods)
            if elsewhere:continue
            newline=re.search(r'\r\n|\r|\n',text[marker.start():])
            end=marker.start()+newline.start() if newline else len(text)
            if marker_index+1<len(markers):end=min(end,markers[marker_index+1].start())
            marker_line=text[marker.start():end].rstrip()
            if own and registry_file is not None and registered_other_slot(marker_line,cse,registry,registry_file):continue
            marker_found=True;break
        if marker_found:
            rows.append(failure(row,'C3_FWD_REF_NOT_REMOVED',f'`// FWD-REF:` marker still present near `{cse.handler}` in {cse.file}.','Remove the `// FWD-REF:` marker after wiring real implementation.'));continue
        body=verified_body(own,text,fact).strip() if own else None
        if body is not None and (not body or re.fullmatch(r'return\s*;?',body)):
            rows.append(failure(row,'C3_HANDLER_BODY_SKELETON',f'Handler `{cse.handler}` body is empty / skeleton.',f'Implement `{cse.handler}` real logic per the spec \'## 对接点\' description.'));continue
        rows.append(dict(row,status='PASS'))
    return category(rows)

def run(project,slice_id,scripts,output,feature_plan=None,registry_path=None,measurement_guard=None):
    if measurement_guard is not None:measurement_guard.verify()
    project=project.resolve();output=output.resolve()
    evidence,run_id=begin_evidence(output)
    project=Path(physical_file(project)['physical_path'])
    sys.path.insert(0,str(scripts))
    from plan_lib.feature_plan_parser import FeaturePlan
    from ref_graph_lib.ets_parser import parse_ets_file
    from skeleton_lib.registry_resolver import RegistryResolver
    registry_path=(registry_path or project/'spec/placeholder-registry.md').resolve()
    registry_input=registry_snapshot(registry_path)
    try:registry=RegistryResolver(registry_path=registry_path)
    except OSError:registry=None  # Cannot prove another owner; retain legacy FAIL.
    plan_path=(feature_plan or project/'spec/baseline/plans/feature-plan.md').resolve()
    plan_inputs=plan_signature(plan_path)
    if measurement_guard is not None and plan_inputs!=measurement_guard.before['plan']:raise SourceInputChangedError('Wiring plan differs from the shared measurement input')
    plan=FeaturePlan.parse_file(plan_path);spec=plan.slices[slice_id]
    files,sdk_files,index,source_input=source_snapshot(project,spec)
    sdk_context_inputs={}
    def assert_fresh():
        try:
            current=source_snapshot(project,spec)[3]
            current_plan=plan_signature(plan_path)
        except OSError as error:raise SourceInputChangedError('Source inputs became unreadable during measurement: '+str(error)) from error
        if current!=source_input:raise SourceInputChangedError('Source identity/path/bytes changed during detection')
        if plan_inputs!=current_plan:raise SourceInputChangedError('Plan inputs changed during detection')
        if registry_snapshot(registry_path)!=registry_input:raise SourceInputChangedError('Registry input changed during detection')
        for name,record in sdk_context_inputs.items():
            if measurement_file(Path(name))!=record:raise SourceInputChangedError('SDK component context input changed: '+name)
        if measurement_guard is not None:measurement_guard.verify()
    raw_path=evidence/'engine-original.json'
    preserve_previous(raw_path)
    if platform.system()!='Darwin':raise RuntimeError('This native tool supports macOS only')
    arch='arm64' if platform.machine().lower() in ('arm64','aarch64') else 'x64'
    dist=scripts/('bin/macos-'+arch+'/_entry.dist')
    # Preserve the original Mac launcher's quarantine handling; never change binaries.
    subprocess.run(['xattr','-dr','com.apple.quarantine',str(dist)],capture_output=True,check=False)
    argv=[str(dist/'_entry.bin'),'verify_slice_wiring','--slice',str(slice_id),'--project-root',str(project),'--feature-plan',str(plan_path),'--output-json',str(raw_path)]
    env=os.environ.copy();env['ARKTS_SKILL_DIR']=str(scripts)
    original=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',env=env)
    record_evidence(evidence/'engine.stdout.log',original.stdout);record_evidence(evidence/'engine.stderr.log',original.stderr)
    assert_fresh()
    if original.returncode not in (0,1) or not raw_path.is_file():raise RuntimeError('Original engine did not produce a usable current result')
    raw=json.loads(raw_path.read_text(encoding='utf-8'))
    node_path,parser_path,selection=sdk_runtime(project)
    helper_path=ets_component_helper()
    loader=next(p for p in (parser_path,*parser_path.parents) if p.name=='ets-loader')
    parser_entry=parser_path
    if parser_path.is_dir():
        parser_package=json.loads((parser_path/'package.json').read_text(encoding='utf-8'))
        parser_entry=parser_path/parser_package.get('main','index.js')
    for path in (helper_path,Path(__file__).with_name('sdk_ast.cjs'),node_path,parser_entry,loader/'tsconfig.json',Path(selection['package'])):
        sdk_context_inputs[str(path)]=measurement_file(path)
    request={'files':[str(p) for p in sdk_files],'parserModule':str(parser_path),'sdkSelection':selection,
             'componentHelper':str(helper_path),'runId':run_id}
    parsed=subprocess.run([str(node_path),str(Path(__file__).with_name('sdk_ast.cjs'))],input=json.dumps(request),capture_output=True,text=True,encoding='utf-8')
    record_evidence(evidence/'sdk.stdout.log',parsed.stdout);record_evidence(evidence/'sdk.stderr.log',parsed.stderr)
    if parsed.returncode:raise RuntimeError('SDK parser failed: '+parsed.stderr)
    facts=json.loads(parsed.stdout)
    if facts.get('runId')!=run_id:raise RuntimeError('SDK parser evidence run_id does not match this measurement')
    context=facts.get('componentContext',{})
    if context.get('helper',{}).get('file')!=str(helper_path) or context.get('helper',{}).get('sha256')!=sdk_context_inputs[str(helper_path)].get('sha256'):
        raise SourceInputChangedError('SDK component helper identity changed during measurement')
    for dependency in context.get('files',[]):
        path=Path(dependency['file']);record=measurement_file(path)
        if record.get('sha256')!=dependency.get('sha256'):raise SourceInputChangedError('SDK component dependency changed: '+str(path))
        if str(path) in sdk_context_inputs and sdk_context_inputs[str(path)]!=record:raise SourceInputChangedError('SDK component context input changed: '+str(path))
        sdk_context_inputs[str(path)]=record
    facts['componentContextInputs']=sdk_context_inputs
    facts['registryInput']=registry_input
    facts['sourceInputs']=source_input
    record_evidence(evidence/'sdk-evidence.json',json.dumps(facts,ensure_ascii=False))
    assert_fresh()
    for record in source_input['sdk_inputs'].values():
        if facts['files'][record['fact_key']]['sha256']!=record['sha256']:raise SourceInputChangedError('SDK/source bytes do not match the measured snapshot')
    diagnostics={name:item['diagnostics'] for name,item in facts['files'].items() if item['diagnostics']}
    if diagnostics:raise RuntimeError('SDK syntax parsing failed; see preserved sdk-evidence.json: '+json.dumps(diagnostics))
    view=FileFacts(facts['files'],index)
    # All C2/C3 rows are independently calculated from current source facts.
    c2=calculate_c2(spec,project,files,view,parse_ets_file)
    c3=calculate_c3(spec,project,view,registry)
    assert_fresh()
    categories={'C1_orphan_check':raw['categories']['C1_orphan_check'],'C2_integration_point':c2,'C3_cross_slice':c3,'C4_parent_replacement':raw['categories']['C4_parent_replacement']}
    repairs=[]
    for cat,contents in categories.items():
        if cat not in ('C2_integration_point','C3_cross_slice'):
            repairs.extend(a for a in raw['repair_actions'] if a['category']==cat)
            continue
        key='ip_id' if cat=='C2_integration_point' else 'cse_id'
        for row in categories[cat]['details']:
            if row['status']!='FAIL':continue
            repairs.append({'id':cat+'__'+row[key],'category':cat,'failed_check':row['failed_check'],'current_state':row['reason'],'suggested_action':row['repair_action'],'file':row.get('file',''),'fixer_layer':'ui'})
    result={k:raw[k] for k in ['slice_id','feature_id','scope']};result.update(categories=categories,overall='BLOCKED' if any(x['fail'] for x in categories.values()) else 'PASS',repair_actions=repairs)
    record_evidence(evidence/'sdk-evidence.json',json.dumps(facts,ensure_ascii=False))
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=output.parent,prefix=output.name+'.',suffix='.tmp',delete=False) as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2);temporary=Path(stream.name)
    temporary.replace(output)
    return result

def main(scripts=None):
    parser=argparse.ArgumentParser(description='Slice wiring closure check (C1-C4)');parser.add_argument('--slice',required=True,type=int,metavar='SLICE_N');parser.add_argument('--project-root',required=True,type=Path);parser.add_argument('--feature-plan',type=Path);parser.add_argument('--output-json',type=Path)
    args=parser.parse_args();scripts=Path(scripts) if scripts is not None else Path(__file__).parent
    output=args.output_json if args.output_json is not None else Path(tempfile.mkdtemp(prefix='hmigbot-wiring-'))/'result.json'
    try:
        result=run(args.project_root,args.slice,scripts,output,args.feature_plan)
        if args.output_json is None:print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result['overall']=='PASS' else 1
    except (EvidenceIOError,SourceInputChangedError) as error:
        print('wiring source measurement error: '+str(error),file=sys.stderr);return 3
    except Exception as error:
        print('wiring source detector error: '+str(error),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
