"""Attested tool installation changes without moving an original join attempt.

An upgrade is a host-observed installation transaction, never an enrollment.
Original attempt bytes, recovery receipts, history and join semantics stay intact.
"""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,os,re,shlex,shutil,subprocess,sys,time

SCHEMA='hmigbot-ios-join-tool-upgrade/v1'
POINTER='.migbot/join-tool-upgrade.json'
PACKAGE='hmigbot-ios-package/v1'
MEMBERS=('src/hmigbot_ios152/join_attempt.py','src/hmigbot_ios152/join_scope.py',
         'scripts/join_attempt.py','skills/a2h-join/scripts/join_gate.py',
         'skills/a2h-join/scripts/audit_join_coverage.py')
DEFAULT_CONFIG=b'[features]\nmulti_agent = true\n\n[agents]\nmax_threads = 4\nmax_depth = 2\n'

def api():
    from . import join_attempt as j
    return j

def require(value,message):
    if not value:raise ValueError(message)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def load(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def plain(path,*,exists=True):
    path=Path(path)
    require(path.is_absolute(),'Upgrade paths must be absolute')
    for item in (path,*path.parents):
        require(not item.is_symlink() and not getattr(item,'is_junction',lambda:False)(),'Upgrade path traverses a link: '+str(item))
    resolved=path.resolve(strict=exists)
    require(str(resolved)==str(path),'Upgrade path must be canonical: '+str(path))
    return resolved

def external(path,project,*protected):
    path=plain(path,exists=False)
    for root in (Path(project),*map(Path,protected)):
        root=root.resolve(strict=True)
        require(not path.is_relative_to(root) and not root.is_relative_to(path),'Upgrade evidence must be independent of project/package/recovery trees')
    return path

def installer(root):
    root=plain(root);path=plain(root/'scripts/manage_install.py')
    spec=importlib.util.spec_from_file_location('_hmigbot_upgrade_installer_'+sha(str(root).encode())[:12],path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def package_inventory(root):
    """Hash the actual normal installer payload, including generated members."""
    root=plain(root);module=installer(root);payload=module.payload();sources={};owned={};cache={}
    for name,data in payload.items():
        if isinstance(data,Path):
            path=plain(data);require(path.is_relative_to(root),'Package payload escapes root')
            key=str(path)
            if key not in cache:cache[key]=digest(path)
            value=cache[key];sources[path.relative_to(root).as_posix()]=value
        else:value=sha(data)
        owned[name]=value
    # This is the normal installer's initial config, not a user-config guess.
    owned['.codex/config.toml']=sha(DEFAULT_CONFIG)
    version=load(root/'.codex-plugin/plugin.json')['version']
    match=re.fullmatch(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]\s*',(root/'src/hmigbot_ios/__init__.py').read_text())
    require(match is not None,'Package Python version identity is not canonical')
    source_version=match.group(1)
    require(source_version==version,'Package version and Python implementation disagree')
    return {'schema':PACKAGE,'root':str(root),'version':version,'files':sources,'owned_files':owned,
            'tool_sha256':sha(b''.join((root/n).read_bytes() for n in MEMBERS))}

def verify_package(root,manifest_path,expected_sha):
    manifest_path=plain(manifest_path)
    require(re.fullmatch('[0-9a-f]{64}',expected_sha or '') and digest(manifest_path)==expected_sha,'Candidate package manifest SHA mismatch')
    expected=load(manifest_path);require(expected.get('schema')==PACKAGE,'Invalid candidate package manifest')
    actual=package_inventory(root)
    require(expected==actual,'Candidate package actual payload differs from frozen package manifest')
    return actual

def owned_path(project,name):
    require(isinstance(name,str) and not Path(name).is_absolute() and '..' not in Path(name).parts and '\\' not in name,'Invalid installed ownership path')
    require(name=='.codex/config.toml' or name.startswith(('.hmigbot-ios/','.agents/hmigbot-runtime/','.agents/skills/','.codex/agents/','.migbot/bin/','.migbot/policies/')),'Upgrade cannot own application/spec files')
    path=plain(Path(project)/name);require(path.is_file(),'Installed owned file missing: '+name)
    return path

def installed(project,expected=None):
    project=plain(project);path=plain(project/'.hmigbot-ios/install.json');value=load(path)
    require(value.get('owner')=='hmigbot-ios' and value.get('schema_version')==1,'Unknown install owner/schema')
    if expected is not None:require(value==expected,'Installed manifest differs from upgrade receipt')
    for name,expected_sha in value['files'].items():
        require(digest(owned_path(project,name))==expected_sha,'Installed owned bytes changed: '+name)
    require(digest(plain(project/'AGENTS.md'))==value['agent_installed_sha256'],'Installed AGENTS bytes changed')
    return {'manifest':value,'manifest_sha256':digest(path),'tool_sha256':sha(b''.join(
        owned_path(project,'.agents/hmigbot-runtime/'+n).read_bytes() for n in MEMBERS))}

def freeze_before(project,root,value):
    root=plain(root,exists=False);root.mkdir()
    for name,expected in value['manifest']['files'].items():
        path=root/'files'/name;path.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(owned_path(project,name),path);require(digest(path)==expected,'Before-install archive changed while copying')
    for name in ('AGENTS.md','.hmigbot-ios/install.json'):
        path=root/'metadata'/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(Path(project)/name,path)
    require(digest(root/'metadata/.hmigbot-ios/install.json')==value['manifest_sha256'],'Before-install manifest copy changed')
    return {**value,'archive':str(root),'files':api().files(root)}

def verify_archive(record):
    root=plain(record['archive']);require(api().files(root)==record['files'],'Frozen installed archive changed')
    require(digest(root/'metadata/.hmigbot-ios/install.json')==record['manifest_sha256'],'Frozen install manifest changed')
    require(load(root/'metadata/.hmigbot-ios/install.json')==record['manifest'],'Frozen install manifest identity mismatch')
    for name,value in record['manifest']['files'].items():require(digest(root/'files'/name)==value,'Frozen owned byte mismatch: '+name)
    return root

def freeze_origin(origin,receipt,state,root):
    origin=plain(origin);inventory=package_inventory(origin)
    require(inventory['version']==state['tool_version']==receipt['tool_version'],'Original package version mismatch')
    require(inventory['owned_files']==receipt['installed_manifest']['files'],'Original package does not reproduce complete original installed manifest')
    require(inventory['tool_sha256']==state['tool_sha256']==receipt['tool_sha256'],'Original five-file implementation fingerprint mismatch')
    root.mkdir();members=list(MEMBERS)+['src/hmigbot_ios/__init__.py','src/hmigbot_ios152/__init__.py']
    for name in members:
        src=plain(origin/name);dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
    return {'package':inventory,'frozen_root':str(root),'frozen_files':api().files(root)}

def origin_script(project,receipt):
    j=api();members=[m for m in j._SCRIPT_MEMBERS if m in receipt['installed_manifest']['files']]
    require(len(members)==1,'Origin receipt must identify one canonical enrollment script')
    return Path(project)/members[0],members[0]

def frozen_epochs(project,raw,receipt,origin):
    """Replay original receipt epochs as historical using attested old bytes."""
    j=api();root=plain(origin['frozen_root']);require(j.files(root)==origin['frozen_files'],'Frozen original implementation changed')
    require(sha(b''.join((root/n).read_bytes() for n in MEMBERS))==receipt['tool_sha256'],'Frozen original aggregate SHA mismatch')
    epochs=[];seen=set()
    def collect(rc,successor=None):
        require(rc.get('schema')==j.RECEIPT and Path(rc['project']).resolve()==Path(project),'Origin epoch identity mismatch')
        install=rc['installed_manifest'];require(install.get('owner')=='hmigbot-ios' and install['version']==rc['tool_version'],'Origin epoch installed identity mismatch')
        script,member=origin_script(project,rc);history=rc['history'];boundary=history['bytes']
        require(type(boundary) is int and 0<=boundary<=len(raw) and (boundary==0 or raw[boundary-1:boundary]==b'\n'),'Invalid original epoch boundary')
        snapshot=Path(history['snapshot']).read_bytes()
        require(len(snapshot)==boundary and sha(snapshot)==history['sha256'] and raw.startswith(snapshot),'Original epoch history prefix changed')
        previous=rc.get('previous_attempt')
        if previous:
            path=plain(previous['receipt']);key=str(path)
            require(key not in seen,'Cyclic original receipt chain');seen.add(key)
            require(digest(path)==previous['receipt_sha256'],'Original historical receipt changed')
            prior=load(path);require(prior['tool_version']==previous['tool_version'] and prior['tool_sha256']==previous['tool_sha256'],'Original historical identity mismatch')
            collect(prior,rc)
        if successor:
            p=plain(successor['archive_manifest']);require(digest(p)==successor['archive_manifest_sha256'],'Origin archive manifest changed')
            archive=load(p);require(Path(archive['workspace']).resolve()==Path(project),'Origin archive project mismatch')
            path=plain(Path(archive['archive'])/member)
            require(archive['files'].get(member)==install['files'][member] and digest(path)==install['files'][member],'Origin archived canonical script changed')
        else:require(digest(root/'scripts/join_attempt.py')==install['files'][member],'Frozen origin canonical script differs from receipt')
        require(not epochs or epochs[-1][0]<boundary,'Original epoch boundaries not increasing')
        epochs.append((boundary,script,False))
    collect(receipt)
    return tuple(epochs)

def audit_summary(scope,native,raw,start,epochs):
    j=api()
    with contextlib.redirect_stdout(io.StringIO()):
        trace=scope.read_trace(native,raw=raw,start_after=start,enrollment_epochs=epochs);result,code=scope.audit([trace])
    active,failed=j.enrollment_status(raw,epochs=epochs)
    return {'handles':result['handles'],'totals':result['totals'],'exit_code':code,
            'failed_spawns':trace.failed_spawns,'unrecovered_spawns':scope.unrecovered_spawns(trace),
            'failed_enrollments':failed,'foreign_enrollments':j.foreign_enrollments(raw,epochs=epochs),
            'issues':trace.issues,'invalid_lists':trace.invalid_lists,
            'last_invalid_list_output':trace.last_invalid_list_output,'last_full_list_call':trace.last_full_list_call,
            'ledger_fake':result.get('ledger_fake',[]),'ledger_checked':False,
            'thread_id':trace.meta.get('id'),'source_sha256':sha(raw),
            'interval_sha256':sha(raw[start:]),'start_bytes':start,'end_bytes':len(raw)}

def compare_audits(old,new):
    require(old['thread_id']==new['thread_id'] and old['source_sha256']==new['source_sha256'] and old['interval_sha256']==new['interval_sha256'] and old['start_bytes']==new['start_bytes'] and old['end_bytes']==new['end_bytes'],'Audit intervals/identities differ')
    require(not old.get('exit_code',0) or new.get('exit_code',0)!=0,'New implementation lost original nonzero audit verdict')
    require(set(old['handles'])<=set(new['handles']),'New implementation lost original handles')
    require(all(new['handles'].get(h)=='UNJOINED' for h,v in old['handles'].items() if v=='UNJOINED'),'New implementation lost an original unjoined observation')
    for field in ('failed_spawns','unrecovered_spawns','failed_enrollments','foreign_enrollments','invalid_lists'):
        old_ids={v.get('call_id') for v in old.get(field,[])};new_ids={v.get('call_id') for v in new.get(field,[])}
        require(old_ids<=new_ids,'New implementation lost original '+field)
    require(set(old['issues'])<=set(new['issues']),'New implementation lost original audit issues')
    old_invalid=old.get('last_invalid_list_output',-1)
    if old_invalid>=0 and old.get('last_full_list_call',-1)<=old_invalid:
        require(new.get('last_invalid_list_output',-1)>=0 and new.get('last_full_list_call',-1)<=new['last_invalid_list_output'],'New implementation lost invalid/full-list ordering failure')
    require({sha(encoded(v)) for v in old.get('ledger_fake',[])}<={sha(encoded(v)) for v in new.get('ledger_fake',[])},'New implementation lost original ledger_fake observations')
    return {'no_original_handle_or_failure_lost':True,'original_unjoined':sum(v=='UNJOINED' for v in old['handles'].values()),'new_unjoined':sum(v=='UNJOINED' for v in new['handles'].values())}

# The original bytes are imported only in an isolated interpreter. The logical
# module path is derived from the original receipt, never caller-selected.
_ORACLE=r'''
from pathlib import Path
import contextlib,hashlib,io,json,os,sys
request=json.loads(sys.stdin.read());root=Path(request['frozen_root']);project=Path(request['project']);physical=root/'src/hmigbot_ios152/join_attempt.py'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name,value in request['frozen_files'].items():
 if digest(root/name)!=value:raise ValueError('Original oracle byte changed: '+name)
sys.path.insert(0,str(root/'src'))
from hmigbot_ios152 import join_attempt as j,join_scope as scope
source_modules={name:{'physical':str(Path(module.__file__).resolve()),'sha256':digest(module.__file__)} for name,module in sys.modules.items() if name in {'hmigbot_ios','hmigbot_ios152','hmigbot_ios152.join_attempt','hmigbot_ios152.join_scope'}}
for value in source_modules.values():
 if not Path(value['physical']).is_relative_to(root):raise ValueError('Current modules contaminated historical oracle')
receipt=request['receipt'];members=[x for x in j._SCRIPT_MEMBERS if x in receipt['installed_manifest']['files']]
if len(members)!=1:raise ValueError('Invalid historical canonical script')
script=project/members[0];logical=script.parents[1]/'src/hmigbot_ios152/join_attempt.py';j.__file__=str(logical)
raw=Path(request['snapshot']).read_bytes();epochs=tuple((b,Path(p),False) for b,p in request['epochs'])
if hashlib.sha256(raw).hexdigest()!=request['source_sha256']:raise ValueError('Oracle log snapshot changed')
args=j.enrollment_command(request['enrollment_payload'],script=script,live=False)[1]
if args['--project']!=str(project):raise ValueError('Logical projection differs from original begin argv')
access=[];allowed={str(p) for end in [script,logical] for p in [end,*end.parents]}
def check(operation,path):
 if isinstance(path,int):return
 try:value=os.path.abspath(os.fsdecode(path))
 except (ValueError,TypeError):return
 access.append({'operation':operation,'path':value,'project':value==str(project) or value.startswith(str(project)+os.sep)})
 if value==str(project) or value.startswith(str(project)+os.sep):
  if operation=='open' or value not in allowed:raise ValueError('Forbidden project access in historical oracle: '+operation+' '+value)
def wrap(fn,operation):
 def inner(path,*args,**kwargs):check(operation,path);return fn(path,*args,**kwargs)
 return inner
for name in ('stat','lstat','readlink'):
 setattr(os,name,wrap(getattr(os,name),name))
if hasattr(os.path,'isjunction'):os.path.isjunction=wrap(os.path.isjunction,'isjunction')
def hook(event,args):
 if event=='open':check('open',args[0])
sys.addaudithook(hook)
with contextlib.redirect_stdout(io.StringIO()):
 trace=scope.read_trace(request['native'],raw=raw,start_after=request['start_bytes']);result,code=scope.audit([trace])
active,failed=j.enrollment_status(raw,epochs=epochs);foreign=j.foreign_enrollments(raw,epochs=epochs)
summary={'handles':result['handles'],'totals':result['totals'],'exit_code':code,'failed_spawns':trace.failed_spawns,'unrecovered_spawns':scope.unrecovered_spawns(trace),'failed_enrollments':failed,'foreign_enrollments':foreign,'issues':trace.issues,'invalid_lists':trace.invalid_lists,'last_invalid_list_output':trace.last_invalid_list_output,'last_full_list_call':trace.last_full_list_call,'ledger_fake':result.get('ledger_fake',[]),'ledger_checked':False,'thread_id':trace.meta.get('id'),'source_sha256':hashlib.sha256(raw).hexdigest(),'interval_sha256':hashlib.sha256(raw[request['start_bytes']:]).hexdigest(),'start_bytes':request['start_bytes'],'end_bytes':len(raw)}
# __file__ is metadata-only projection. All executed bytes remain frozen old code.
for name,value in source_modules.items():
 if digest(value['physical'])!=value['sha256']:raise ValueError('Original source changed during oracle')
 if name!='hmigbot_ios152.join_attempt' and str(Path(sys.modules[name].__file__).resolve())!=value['physical']:raise ValueError('Historical module origin changed')
print(json.dumps({'summary':summary,'provenance':{'modules':source_modules,'logical_module':str(logical),'derived_member':members[0],'project_accesses':access,'instrumentation':'CPython open audit hook plus forwarding os.stat/lstat/readlink/isjunction wrappers; not all stat calls are CPython audit events','actual_thread':os.environ.get('CODEX_THREAD_ID'),'native':request['native'],'old_version':j.__version__}},ensure_ascii=False))
'''

def original_audit(project,native,raw,state,receipt,origin,snapshot,epochs):
    j=api();entries=[p for p,_,end,_ in j.enrollment_rows(raw,epochs=epochs) if end==state['start_bytes'] and p.get('call_id')==state['enrollment_call_id']]
    require(len(entries)==1,'Original enrollment payload not unique for oracle')
    request={'frozen_root':origin['frozen_root'],'frozen_files':origin['frozen_files'],'project':str(project),
             'receipt':receipt,'snapshot':str(snapshot),'source_sha256':sha(raw),'native':str(native),
             'epochs':[(b,str(p)) for b,p,_ in epochs],'start_bytes':state['start_bytes'],'enrollment_payload':entries[0]}
    try:r=subprocess.run([sys.executable,'-I','-B','-c',_ORACLE],input=json.dumps(request),text=True,capture_output=True,timeout=300)
    except subprocess.TimeoutExpired as error:raise ValueError('Pinned original audit did not finish; preserve evidence and do not infer success') from error
    require(r.returncode==0,'Pinned original audit failed: '+r.stderr[-3000:])
    try:result=json.loads(r.stdout)
    except (ValueError,TypeError) as exc:raise ValueError('Original oracle returned no unambiguous JSON result') from exc
    require(result['summary']['thread_id']==state['thread_id'],'Original oracle thread mismatch')
    return result

def command(payload,script):
    j=api();args=j.process_arguments(payload)
    require(isinstance(args,dict) and not(set(args)-{'cmd','workdir','login','max_output_tokens','yield_time_ms','tty'}),'Upgrade requires literal standard process options')
    require(args.get('tty',False) is False and args.get('yield_time_ms')==30000 and args.get('max_output_tokens',10000)>=4096,'Upgrade requires one complete non-PTY process result')
    cmd=args.get('cmd');require(isinstance(cmd,str) and '\n' not in cmd and '\r' not in cmd,'Upgrade must be one canonical command line')
    argv=shlex.split(cmd);require(cmd==shlex.join(argv),'Upgrade argv must use canonical shell quoting')
    require(len(argv)==16 and argv[:2] in (['python','-B'],['python3','-B']) and argv[2]==str(script) and argv[3]=='upgrade','Upgrade must be a standalone canonical Python invocation')
    opts=dict(zip(argv[4::2],argv[5::2]));required={'--project','--origin-package','--package-manifest','--package-sha256','--evidence-root','--upgrade'}
    require(set(opts)==required and len(opts)==6,'Upgrade requires every option exactly once')
    require(re.fullmatch('[0-9a-f]{32}',opts['--upgrade']) and re.fullmatch('[0-9a-f]{64}',opts['--package-sha256']),'Upgrade nonce/package SHA invalid')
    for key in required-{'--upgrade','--package-sha256'}:require(Path(opts[key]).is_absolute(),'Upgrade paths must be absolute')
    return cmd,opts

def upgrade_marker(raw,script,nonce):
    j=api();found=[]
    for row,end,complete in j.rows(raw):
        if row.get('type')!='response_item':continue
        p=row.get('payload',{})
        try:cmd,opts=command(p,script)
        except (ValueError,TypeError,OSError,KeyError):continue
        if opts['--upgrade']==nonce:found.append((p,cmd,opts,end,complete))
    require(len(found)==1,'Upgrade must identify exactly one original host call; do not retry its nonce')
    require(found[0][4] and found[0][0].get('call_id'),'Upgrade call is not a complete native row')
    return found[0]

def output_proof(raw,receipt,receipt_sha,pointer_sha):
    j=api();values,finished=j.host_results(raw,receipt['host_call']['call_id'],_with_end=True)
    require(len(values)==1 and values[0].get('exit_code')==0,'Upgrade needs its actual successful original host process output')
    matches=[o for o in j.stdout_objects(values[0]['output']) if o.get('status')=='upgraded' and o.get('upgrade_id')==receipt['upgrade_id'] and o.get('receipt_sha256')==receipt_sha and o.get('pointer_sha256')==pointer_sha and o.get('attempt_id')==receipt['attempt_id'] and o.get('start_bytes')==receipt['start_bytes']]
    require(len(matches)==1,'Upgrade output must bind one exact receipt, pointer and original attempt')
    from .join_scope import AGENT_OPERATIONS
    for row,end,_ in j.rows(raw):
        if receipt['host_call']['end_bytes']<end<finished and row.get('type')=='response_item':
            p=row.get('payload',{})
            if p.get('type') in {'function_call','custom_tool_call'} and str(p.get('name','')).rsplit('.',1)[-1] in AGENT_OPERATIONS-{'list_agents'}:
                raise ValueError('Agent work occurred while the tool upgrade process was running')

def version_key(value):
    require(isinstance(value,str) and re.fullmatch(r'\d+\.\d+\.\d+-ios\.\d+',value),'Unsupported upgrade version identity')
    return tuple(map(int,re.findall(r'\d+',value)))

def pointer_bytes(path,receipt_sha,attempt):
    base={'schema':SCHEMA,'receipt':str(path),'receipt_sha256':receipt_sha,'attempt_id':attempt}
    return encoded({**base,'pointer_content_sha256':sha(encoded(base))})

def verify_pointer(raw):
    value=json.loads(raw);base={k:value[k] for k in ('schema','receipt','receipt_sha256','attempt_id')}
    require(value.get('schema')==SCHEMA and value.get('pointer_content_sha256')==sha(encoded(base)) and raw==encoded(value),'Upgrade pointer identity changed')
    return value


def prohibit_enrollments(raw,boundary):
    j=api()
    for row,end,_ in j.rows(raw):
        if end<=boundary or row.get('type')!='response_item':continue
        p=row.get('payload',{})
        try:args=j.process_arguments(p);argv=shlex.split(args.get('cmd',''))
        except (ValueError,TypeError,OSError,KeyError,AttributeError):continue
        if len(argv)>=4 and Path(argv[2]).name=='join_attempt.py' and argv[3] in {'seal','begin'}:
            raise ValueError('New enrollment/recovery commands cannot follow a same-attempt tool upgrade')


def _receipt(project,native,raw,state,path,expected_sha,pointer_sha,seen):
    j=api();path=plain(path);require(path.name==expected_sha+'.json' and digest(path)==expected_sha,'Content-addressed upgrade receipt changed')
    require(str(path) not in seen,'Cyclic upgrade receipt chain');seen.add(str(path));r=load(path)
    require(r.get('schema')==SCHEMA and r['project']==str(project) and r['thread_id']==state['thread_id'] and r['rollout']==str(native),'Upgrade receipt project/thread/native mismatch')
    require(r['attempt_id']==state['attempt_id'] and r['start_bytes']==state['start_bytes'] and r['prefix_sha256']==state['prefix_sha256'] and r['origin_state_sha256']==digest(Path(project)/j.STATE),'Upgrade moved or changed the original attempt')
    require(r['origin_receipt_sha256']==state['receipt_sha256'] and r['origin_tool_sha256']==state['tool_sha256'],'Upgrade origin differs from original enrollment')
    candidate=r['candidate'];frozen_manifest=plain(r['package_manifest_snapshot'])
    require(digest(frozen_manifest)==r['package_manifest_sha256'] and candidate==load(frozen_manifest),'Frozen upgrade candidate identity changed')
    script=Path(candidate['root'])/'scripts/join_attempt.py';p,cmd,opts,end,_=upgrade_marker(raw,script,r['upgrade_id'])
    require(cmd==r['host_call']['command'] and p['call_id']==r['host_call']['call_id'] and end==r['host_call']['end_bytes'],'Upgrade host call identity changed')
    require(opts==r['options'],'Upgrade argv/evidence binding changed')
    snapshot=plain(r['log']['snapshot']).read_bytes()
    require(len(snapshot)==end and r['log']['bytes']==end and sha(snapshot)==r['log']['sha256'] and raw.startswith(snapshot),'Upgrade complete log prefix changed')
    require(sha(snapshot[state['start_bytes']:])==r['log']['interval_sha256'],'Upgrade original-attempt interval changed')
    require(digest(r['original_audit_file'])==r['original_audit_sha256'] and digest(r['new_audit_file'])==r['new_audit_sha256'],'Upgrade differential audit evidence changed')
    old=load(r['original_audit_file'])['summary'];new=load(r['new_audit_file']);compare_audits(old,new)
    require(old['source_sha256']==sha(snapshot) and old['start_bytes']==state['start_bytes'] and old['end_bytes']==end,'Upgrade audit evidence has a different interval')
    verify_archive(r['before']);require(version_key(r['after']['manifest']['version'])>=version_key(r['before']['manifest']['version'])>=version_key(state['tool_version']),'Tool downgrade is forbidden')
    expected=dict(candidate['owned_files']);expected['.codex/config.toml']=r['before']['manifest']['files'].get('.codex/config.toml',sha(DEFAULT_CONFIG))
    require(r['after']['manifest']['files']==expected and r['after']['tool_sha256']==candidate['tool_sha256'] and r['after']['manifest']['version']==candidate['version'],'Installed payload does not match candidate source')
    previous=r.get('previous_pointer')
    if previous:
        prev_raw=encoded(previous);prev=verify_pointer(prev_raw)
        prior=_receipt(project,native,raw,state,prev['receipt'],prev['receipt_sha256'],sha(prev_raw),seen)
        require(prior['after']=={k:r['before'][k] for k in ('manifest','manifest_sha256','tool_sha256')},'Upgrade chain does not join actual before/after install identities')
        require(prior['host_call']['end_bytes']<end,'Upgrade chain is not chronological')
    else:require(r['past_intermediate_installation']=='unobserved; current installation bytes revalidated, no historical upgrade event inferred','First upgrade must disclose unrecorded past installation')
    output_proof(raw,r,expected_sha,pointer_sha);prohibit_enrollments(raw,end)
    return r


def latest_upgrade(raw,project,state,terminal,receipt_sha,pointer_sha,pending_allowed=None):
    """Host chronology, not a pointer mtime, determines the terminal binding."""
    j=api();successful=[];pending=[];failed=[]
    for row,end,_ in j.rows(raw):
        if end<=state['start_bytes'] or row.get('type')!='response_item':continue
        p=row.get('payload',{})
        try:
            args=j.process_arguments(p);argv=shlex.split(args.get('cmd',''))
            if len(argv)<4 or Path(argv[2]).name!='join_attempt.py' or argv[3]!='upgrade':continue
            _,opts=command(p,Path(argv[2]))
        except (ValueError,TypeError,OSError,KeyError,AttributeError):continue
        if opts['--project']!=str(project):continue
        values=j.host_results(raw,p.get('call_id'));objects=[obj for value in values for obj in j.stdout_objects(value.get('output',''))]
        created=[obj for obj in objects if obj.get('status')=='upgraded' and obj.get('upgrade_id')==opts['--upgrade']]
        if len(values)==1 and values[0].get('exit_code')!=0 and not created:
            failed.append(p.get('call_id'));continue
        if len(values)==1 and values[0].get('exit_code')==0 and len(created)==1:
            successful.append((end,p['call_id'],created[0]));continue
        if p.get('call_id')!=pending_allowed:pending.append(p.get('call_id'))
    require(not pending,'An upgrade has no unambiguous original successful/failed process result: '+str(pending))
    require(successful,'Upgrade pointer has no successful original upgrade')
    latest=max(successful,key=lambda item:item[0]);require(latest[1]==terminal['host_call']['call_id'] and latest[2].get('receipt_sha256')==receipt_sha and latest[2].get('pointer_sha256')==pointer_sha,'Upgrade pointer rolled back before latest successful original upgrade')
    linked=set();current=terminal
    while current:
        linked.add(current['host_call']['call_id']);previous=current.get('previous_pointer')
        current=load(previous['receipt']) if previous else None
    require(linked=={item[1] for item in successful},'Upgrade chain omitted or forked an actual successful upgrade')
    return failed


def validate_binding(project,native,raw,state,*,_preparing=False,_pending_call_id=None):
    from . import join_scope as scope
    j=api();project=plain(project);native=plain(native);path=plain(project/POINTER);pointer_raw=path.read_bytes();pointer=verify_pointer(pointer_raw)
    require(pointer['attempt_id']==state['attempt_id'],'Upgrade pointer belongs to another attempt')
    r=_receipt(project,native,raw,state,pointer['receipt'],pointer['receipt_sha256'],sha(pointer_raw),set())
    actual=installed(project,r['after']['manifest']);require(actual==r['after'],'Actual installed manifest/tool bytes differ from upgrade terminal identity')
    if not _preparing:require(actual['manifest']['version']==j.__version__ and actual['tool_sha256']==j.tool_sha(),'Current implementation is not the upgrade chain terminal tool')
    receipt=load(state['receipt']);epochs=frozen_epochs(project,raw,receipt,r['origin'])
    # Re-read pinned old bytes and both actual observations of the same interval.
    snapshot=Path(r['log']['snapshot']).read_bytes();old=original_audit(project,native,snapshot,state,receipt,r['origin'],r['log']['snapshot'],epochs)
    new=audit_summary(scope,native,snapshot,state['start_bytes'],epochs);compare_audits(old['summary'],new)
    require(old==load(r['original_audit_file']),'Upgrade original differential audit does not reproduce')
    if _preparing:compare_audits(load(r['new_audit_file']),new)
    else:require(new==load(r['new_audit_file']),'Upgrade terminal differential audit does not reproduce')
    latest_upgrade(raw,project,state,r,pointer['receipt_sha256'],sha(pointer_raw),_pending_call_id if _preparing else None)
    return {'receipt':str(pointer['receipt']),'receipt_sha256':pointer['receipt_sha256'],'epochs':epochs,'origin':r['origin']}


def restore_before(project,before,after=None):
    root=verify_archive(before);old=before['manifest'];current=load(Path(project)/'.hmigbot-ios/install.json')
    for name in set(current['files'])-set(old['files']):
        path=owned_path(project,name);require(digest(path)==current['files'][name],'Rollback refuses edited new owned file: '+name);path.unlink()
    for name,value in old['files'].items():
        target=Path(project)/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/'files'/name,target)
    for name in ('AGENTS.md','.hmigbot-ios/install.json'):
        target=Path(project)/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/'metadata'/name,target)
    require(installed(project)=={k:before[k] for k in ('manifest','manifest_sha256','tool_sha256')},'Upgrade rollback did not restore prior install identity')


def upgrade(project,origin_package,package_manifest,package_sha256,evidence_root,nonce):
    from . import join_scope as scope
    j=api();project=plain(project);origin_package=plain(origin_package);package_manifest=plain(package_manifest)
    candidate=verify_package(Path(j.__file__).resolve().parents[2],package_manifest,package_sha256)
    require(candidate['version']==j.__version__ and candidate['tool_sha256']==j.tool_sha(),'Upgrade process differs from frozen candidate code')
    native=scope.current_rollout();require(native is not None,'Upgrade requires actual root CODEX_THREAD_ID')
    native=plain(native);raw=scope.native_bytes(native);require(scope.caller(scope._meta(native))=='/root','Only the actual root may upgrade its tool')
    state_path=plain(project/j.STATE);state_raw=state_path.read_bytes();state=json.loads(state_raw)
    require(state['thread_id']==os.environ.get('CODEX_THREAD_ID')==scope._meta(native).get('id'),'Upgrade thread differs from original attempt')
    receipt=load(plain(state['receipt']));require(digest(state['receipt'])==state['receipt_sha256'],'Original recovery receipt changed')
    script=Path(candidate['root'])/'scripts/join_attempt.py'
    for retry in range(11):
        try:p,cmd,opts,end,_=upgrade_marker(raw,script,nonce);break
        except ValueError:
            if retry==10:raise
            time.sleep(.2);raw=scope.native_bytes(native)
    expected={'--project':str(project),'--origin-package':str(origin_package),'--package-manifest':str(package_manifest),'--package-sha256':package_sha256,'--evidence-root':str(evidence_root),'--upgrade':nonce}
    require(opts==expected,'Upgrade actual argv differs from current invocation')
    call_start=raw.rfind(b'\n',0,end-1)+1;prefix=raw[:call_start]
    j.idle_trace(prefix,scope.read_trace(native,raw=prefix,history=True))
    pm=load(receipt['pristine_manifest']);am=load(receipt['archive_manifest'])
    root=external(evidence_root,project,origin_package,Path(candidate['root']),Path(pm['backup']),Path(am['archive']))
    require(not root.exists() and root.parent.is_dir(),'Upgrade evidence root must be new; do not retry a prior upgrade')
    before=installed(project);require(version_key(candidate['version'])>=version_key(before['manifest']['version'])>=version_key(state['tool_version']),'Tool downgrade is forbidden')
    root.mkdir();frozen_manifest=root/'package-manifest.json';shutil.copy2(package_manifest,frozen_manifest)
    require(digest(frozen_manifest)==package_sha256,'Candidate package manifest changed before freezing')
    origin=freeze_origin(origin_package,receipt,state,root/'origin');epochs=frozen_epochs(project,raw,receipt,origin)
    previous_path=project/POINTER;previous_raw=previous_path.read_bytes() if previous_path.exists() else None
    if previous_raw:validate_binding(project,native,raw,state,_preparing=True,_pending_call_id=p['call_id'])
    # Provenance validation is separate from the freshly checked live install;
    # this internal historical operation cannot authorize a stage gate on its own.
    j.validate_state(project,native,raw,state,check_tool=False,epochs=epochs)
    snapshot=root/'history.jsonl';snapshot.write_bytes(raw[:end]);interval=raw[:end]
    old=original_audit(project,native,interval,state,receipt,origin,snapshot,epochs);new=audit_summary(scope,native,interval,state['start_bytes'],epochs);comparison=compare_audits(old['summary'],new)
    old_path=root/'original-audit.json';new_path=root/'new-audit.json';old_path.write_bytes(encoded(old));new_path.write_bytes(encoded(new))
    before=freeze_before(project,root/'before',before);after=None;pointer_installed=False
    try:
        normal=installer(candidate['root']);result=normal.manage(project,'install')
        require(result['status'] in {'installed','upgraded'},'Normal installer did not finish')
        after=installed(project);require(state_path.read_bytes()==state_raw,'Upgrade changed original join attempt bytes')
        require(after['tool_sha256']==candidate['tool_sha256'] and after['manifest']['version']==candidate['version'],'Installed implementation differs from candidate')
        expected_owned=dict(candidate['owned_files']);expected_owned['.codex/config.toml']=before['manifest']['files'].get('.codex/config.toml',sha(DEFAULT_CONFIG))
        require(after['manifest']['files']==expected_owned,'Installed complete owned payload differs from candidate')
        record={'schema':SCHEMA,'upgrade_id':nonce,'project':str(project),'thread_id':state['thread_id'],'rollout':str(native),
                'attempt_id':state['attempt_id'],'start_bytes':state['start_bytes'],'prefix_sha256':state['prefix_sha256'],
                'origin_state_sha256':sha(state_raw),'origin_receipt_sha256':state['receipt_sha256'],'origin_tool_sha256':state['tool_sha256'],
                'origin':origin,'before':before,'candidate':candidate,'after':after,'normal_installer_result':result,
                'package_manifest':str(package_manifest),'package_manifest_snapshot':str(frozen_manifest),'package_manifest_sha256':package_sha256,'options':opts,
                'host_call':{'call_id':p['call_id'],'command':cmd,'end_bytes':end},
                'log':{'snapshot':str(snapshot),'sha256':sha(interval),'bytes':end,'interval_sha256':sha(interval[state['start_bytes']:])},
                'original_audit_file':str(old_path),'original_audit_sha256':digest(old_path),'new_audit_file':str(new_path),'new_audit_sha256':digest(new_path),'comparison':comparison,
                'previous_pointer':json.loads(previous_raw) if previous_raw else None,
                'past_intermediate_installation':'unobserved; current installation bytes revalidated, no historical upgrade event inferred'}
        data=encoded(record);receipt_sha=sha(data);dest=root/(receipt_sha+'.json')
        with dest.open('xb') as stream:stream.write(data)
        pointer_data=pointer_bytes(dest,receipt_sha,state['attempt_id']);previous_path.parent.mkdir(parents=True,exist_ok=True)
        if previous_path.exists():require(previous_path.read_bytes()==previous_raw,'Concurrent upgrade pointer changed')
        temporary=previous_path.with_name(previous_path.name+'.'+nonce+'.tmp')
        with temporary.open('xb') as stream:stream.write(pointer_data)
        os.replace(temporary,previous_path);pointer_installed=True
        require(state_path.read_bytes()==state_raw,'Upgrade modified original attempt state')
        return {'status':'upgraded','upgrade_id':nonce,'receipt':str(dest),'receipt_sha256':receipt_sha,'pointer_sha256':sha(pointer_data),'attempt_id':state['attempt_id'],'start_bytes':state['start_bytes'],'version':candidate['version']}
    except Exception as error:
        try:
            if pointer_installed:
                if previous_raw is None:previous_path.unlink()
                else:previous_path.write_bytes(previous_raw)
            restore_before(project,before,after)
            require(state_path.read_bytes()==state_raw,'Original state changed during failed upgrade; preserve evidence')
        except Exception as rollback:
            raise ValueError('Upgrade failed: '+str(error)+'; rollback failed: '+str(rollback)+'; preserve all evidence') from error
        raise
