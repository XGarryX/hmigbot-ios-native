"""Bind a verified workspace restart to one real host invocation.

This never edits a rollout or marks an earlier task completed. Historical failures
remain in a separate full-history audit. Only an empty, verified restored project
can enroll; an enrolled attempt cannot move its boundary.
"""
from pathlib import Path, PurePosixPath
import argparse,contextlib,hashlib,io,json,os,re,shlex,sys,time,unicodedata
from hmigbot_ios import __version__

STATE='.migbot/join-attempt.json'
SCHEMA='hmigbot-ios-join-attempt/v1'
RECEIPT='hmigbot-ios-recovery/v1'

def require(value,message):
    if not value: raise ValueError(message)

def sha(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value): return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
def load(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def files(root):
    root=Path(root)
    require(not root.is_symlink() and not getattr(root,'is_junction',lambda:False)(),'Recovery root is a link')
    root=root.resolve(strict=True); result={}
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink() and not getattr(path,'is_junction',lambda:False)(),'Recovery evidence contains a link: '+str(path))
        if path.is_file(): result[path.relative_to(root).as_posix()]=digest(path)
    return result

def rows(raw):
    offset=0
    for number,line in enumerate(raw.splitlines(keepends=True),1):
        offset+=len(line)
        if line.strip():
            try: row=json.loads(line.decode('utf-8-sig' if number==1 else 'utf-8'))
            except (ValueError,UnicodeError) as exc:raise ValueError(f'Invalid complete native log at line {number}: {exc}') from exc
            yield row,offset,line.endswith(b'\n')

def tool_text(payload):
    if payload.get('type') not in {'function_call','custom_tool_call'}:return ''
    if str(payload.get('name','')).rsplit('.',1)[-1] not in {'exec','exec_command'}:return ''
    if isinstance(payload.get('input'),str):return payload['input']
    value=payload.get('arguments','')
    try: args=json.loads(value) if isinstance(value,str) else value
    except ValueError:return ''
    return str(args.get('cmd',args.get('code',''))) if isinstance(args,dict) else ''

def flag(text,name,value):
    return re.search(r'--'+re.escape(name)+r'(?:=|\s+)'+re.escape(value)+r"(?=$|[\s'\"\\])",text) is not None

def process_arguments(payload,operation='exec_command'):
    """Read only a direct process call or its literal native JS wrapper."""
    name=str(payload.get('name','')).rsplit('.',1)[-1]
    if name==operation:
        value=payload.get('arguments')
        args=json.loads(value) if isinstance(value,str) else value
    else:
        text=tool_text(payload)
        if operation=='exec_command':require(text.startswith('// @exec:'),'Enrollment exec wrapper requires explicit complete-result metadata')
        if text.startswith('// @exec:'):
            first,separator,text=text.partition('\n')
            meta=re.fullmatch(r'// @exec: \{"yield_time_ms":([1-9][0-9]*),"max_output_tokens":([1-9][0-9]*)\}',first)
            require(separator and meta is not None and int(meta[1])>=60000 and int(meta[2])>=4096,
                    'Enrollment exec directive must allow a complete process result')
        match=re.fullmatch(r'\s*text\(\s*await\s+tools\.'+re.escape(operation)+r'\((\{[\s\S]*\})\)\s*\)\s*;?\s*',text)
        require(name=='exec' and match is not None,'Host call must be text(await tools.'+operation+'(<literal JSON>));')
        args=json.loads(match.group(1))
    return args

def enrollment_command(payload,*,script=None,live=True):
    """Accept one literal Python invocation, never a shell or JavaScript program."""
    args=process_arguments(payload)
    require(isinstance(args,dict) and not (set(args)-{'cmd','workdir','login','max_output_tokens','yield_time_ms','tty'}),'Enrollment exec parameters must be literal standard process options')
    require(args.get('tty',False) is False,'Enrollment cannot use a PTY')
    require(type(args.get('yield_time_ms')) is int and args['yield_time_ms']==30000,'Enrollment needs exactly 30000 ms of initial process waiting')
    require(type(args.get('max_output_tokens',10000)) is int and args.get('max_output_tokens',10000)>=4096,'Enrollment stdout budget must be at least 4096 tokens')
    cmd=args.get('cmd')
    require(isinstance(cmd,str) and '\n' not in cmd and '\r' not in cmd,'Enrollment must be one command line')
    argv=shlex.split(cmd,posix=True)
    require(cmd==shlex.join(argv),'Enrollment must use the canonical shell-quoted argv')
    require(len(argv)==12 and argv[:2] in (['python','-B'],['python3','-B']) and argv[3]=='begin','Enrollment must be a standalone python[3] -B join_attempt.py begin invocation')
    expected=Path(script) if script is not None else Path(__file__).resolve().parents[2]/'scripts/join_attempt.py'
    actual=Path(argv[2])
    require(actual.is_absolute() and argv[2]==str(expected),'Enrollment script must be the literal canonical absolute installed path')
    if live:
        for path in (actual,*actual.parents):
            require(not path.is_symlink() and not getattr(path,'is_junction',lambda:False)(),'Enrollment script path cannot traverse links')
        require(actual.is_file(),'Installed enrollment script is missing')
    options=dict(zip(argv[4::2],argv[5::2]))
    require(set(options)=={'--project','--receipt','--receipt-sha256','--enrollment'} and len(options)==4,'Enrollment must contain each required flag exactly once, with no extra arguments')
    require(Path(options['--project']).is_absolute() and Path(options['--receipt']).is_absolute(),'Enrollment project and receipt must be absolute paths')
    require(re.fullmatch('[0-9a-f]{32}',options['--enrollment']) and re.fullmatch('[0-9a-f]{64}',options['--receipt-sha256']),'Invalid canonical enrollment token or receipt digest')
    return cmd,options

def enrollment_candidates(raw):
    for row,end,complete in rows(raw):
        if row.get('type')!='response_item':continue
        payload=row.get('payload',{}); text=tool_text(payload)
        try:
            args=process_arguments(payload)
            if isinstance(args,dict) and isinstance(args.get('cmd'),str):text=args['cmd']
        except (ValueError,OSError,TypeError):pass
        if 'join_attempt.py' in text and re.search(r'\bbegin\b',text) and re.search(r'--enrollment(?:=|\s+)[\'\"]?[0-9a-f]{32}(?=$|[^0-9a-fA-F])',text) and re.search(r'--receipt-sha256(?:=|\s+)[\'\"]?[0-9a-f]{64}(?=$|[^0-9a-fA-F])',text):
            yield payload,text,end,complete

_SCRIPT_MEMBERS=('.hmigbot-ios/plugin/scripts/join_attempt.py',
                 '.agents/hmigbot-runtime/scripts/join_attempt.py')

def enrollment_epochs(project,raw,receipt,*,sealing=False):
    """One receipt-bound canonical script per immutable history interval."""
    project=Path(project).resolve(strict=True);epochs=[];seen=set()
    current=Path(__file__).resolve().parents[2]/'scripts/join_attempt.py'
    def collect(value,live,successor=None):
        require(value.get('schema')==RECEIPT,'Invalid epoch recovery receipt')
        require(Path(value['project']).resolve()==project,'Epoch receipt project mismatch')
        installed=value['installed_manifest']
        require(installed.get('owner')=='hmigbot-ios' and installed.get('version')==value['tool_version'],'Epoch installed identity mismatch')
        members=[name for name in _SCRIPT_MEMBERS if name in installed.get('files',{})]
        require(len(members)==1,'Receipt needs one owned canonical enrollment script')
        member=members[0];script=project/member
        require(re.fullmatch('[0-9a-f]{64}',installed['files'][member]) is not None,'Invalid epoch script digest')
        if live:
            require(script==current and value['tool_version']==__version__,'Current manifest canonical enrollment path mismatch')
        history=value['history'];boundary=history['bytes']
        require(type(boundary) is int and 0<=boundary<=len(raw),'Invalid enrollment epoch boundary')
        require(boundary==0 or raw[boundary-1:boundary]==b'\n','Enrollment epoch cuts a native log row')
        if live and sealing:
            require(boundary==len(raw),'Pending seal must cover the complete native history')
            snapshot=raw
        else:snapshot=Path(history['snapshot']).read_bytes()
        require(len(snapshot)==boundary and sha(snapshot)==history['sha256'] and raw.startswith(snapshot),'Epoch historical snapshot changed')
        previous=value.get('previous_attempt')
        if previous:
            path=Path(previous['receipt']).resolve(strict=True)
            key=(str(path),previous['receipt_sha256'])
            require(key not in seen,'Cyclic historical receipt chain');seen.add(key)
            require(digest(path)==previous['receipt_sha256'],'Historical receipt digest changed')
            prior=load(path)
            require(prior.get('tool_version')==previous['tool_version'] and prior.get('tool_sha256')==previous['tool_sha256'],'Historical receipt tool identity mismatch')
            collect(prior,False,value)
        if successor is not None:
            manifest=Path(successor['archive_manifest'])
            require(digest(manifest)==successor['archive_manifest_sha256'],'Epoch archive manifest changed')
            archived=load(manifest);root=Path(archived['archive']).resolve(strict=True)
            require(Path(archived['workspace']).resolve()==project,'Epoch archive project mismatch')
            source=root/member;expected=installed['files'][member]
            require(archived['files'].get(member)==expected and source.is_file() and not source.is_symlink() and digest(source)==expected,'Archived historical enrollment script changed')
        require(not epochs or epochs[-1][0]<boundary,'Enrollment epochs are not strictly increasing')
        epochs.append((boundary,script,live))
    collect(receipt,True)
    return tuple(epochs)

def _enrollment_epoch(raw,end,epochs):
    if not epochs:return None,True
    start=raw.rfind(b'\n',0,end-1)+1
    require(not any(start<boundary<end for boundary,_,_ in epochs),'Enrollment row crosses an epoch boundary')
    selected=epochs[0]
    for epoch in epochs:
        if epoch[0]<=start:selected=epoch
        else:break
    return selected[1:]

def enrollment_rows(raw,*,epochs=()):
    for payload,_,end,complete in enrollment_candidates(raw):
        try:
            script,live=_enrollment_epoch(raw,end,epochs)
            text,_=enrollment_command(payload,script=script,live=live)
        except (ValueError,OSError,TypeError):continue
        yield payload,text,end,complete

def foreign_enrollments(raw,*,epochs=()):
    result=[]
    for payload,_,end,_ in enrollment_candidates(raw):
        try:
            script,live=_enrollment_epoch(raw,end,epochs)
            enrollment_command(payload,script=script,live=live)
        except (ValueError,OSError,TypeError) as exc:
            result.append({'call_id':payload.get('call_id'),'end_bytes':end,'reason':str(exc)})
    return result

def tool_sha():
    """Bind the actual gate and enrollment implementation, not just a label."""
    root=Path(__file__).resolve().parents[2]
    names=['src/hmigbot_ios152/join_attempt.py','src/hmigbot_ios152/join_scope.py','scripts/join_attempt.py',
           'skills/a2h-join/scripts/join_gate.py','skills/a2h-join/scripts/audit_join_coverage.py']
    return sha(b''.join((root/name).read_bytes() for name in names))

def load_ledger(path):return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]

def host_results(raw,call_id,*,_with_end=False):
    def objects(value):
        if isinstance(value,str):
            try:yield from objects(json.loads(value))
            except (ValueError,TypeError):return
        elif isinstance(value,list):
            for part in value:yield from objects(part)
        elif isinstance(value,dict):
            if isinstance(value.get('output'),str) and (type(value.get('exit_code')) is int or type(value.get('session_id')) is int):
                yield value
                return  # stdout is application data, never another host envelope.
            if value.get('type') in ('text','input_text') and isinstance(value.get('text'),str):
                yield from objects(value['text'])
            elif isinstance(value.get('content'),list):
                yield from objects(value['content'])
    source=[(row.get('payload',{}),end) for row,end,_ in rows(raw) if row.get('type')=='response_item']
    results=[(p,end) for p,end in source if p.get('type') in ('function_call_output','custom_tool_call_output') and p.get('call_id')==call_id]
    require(len(results)<=1,'Enrollment has multiple original outputs')
    if not results:return ([],None) if _with_end else []
    original,original_end=results[0]; values=list(objects(original.get('output')))
    if len(values)!=1 or type(values[0].get('exit_code')) is int:return (values,original_end) if _with_end else values
    # Follow only the original process session, through literal empty-stdin polls.
    # Neither stdout nor an unrelated session can supply an exit code.
    session=values[0]['session_id'];chunks=[values[0]['output']];pending=None;last_end=original_end
    for p,end in source:
        if end<=last_end:continue
        if p.get('type') in ('function_call_output','custom_tool_call_output') and p.get('call_id')!=pending:
            require(not any(type(v.get('session_id')) is int and v['session_id']==session for v in objects(p.get('output'))),
                    'Another host output claimed the enrollment process session')
        if p.get('type') in ('function_call','custom_tool_call'):
            try:args=process_arguments(p,'write_stdin')
            except (ValueError,TypeError,OSError):continue
            if not isinstance(args,dict) or type(args.get('session_id')) is not int or args['session_id']!=session:continue
            require(not (set(args)-{'session_id','chars','yield_time_ms','max_output_tokens'}) and args.get('chars','')=='',
                    'Enrollment process continuation must only poll its original session')
            require(type(args.get('max_output_tokens',10000)) is int and args.get('max_output_tokens',10000)>=4096,
                    'Enrollment continuation stdout budget must be at least 4096 tokens')
            require(pending is None and p.get('call_id'),'Enrollment process polls must be sequential original calls')
            pending=p['call_id']
        elif p.get('type') in ('function_call_output','custom_tool_call_output') and pending and p.get('call_id')==pending:
            values=list(objects(p.get('output')))
            require(len(values)==1,'Enrollment continuation needs one original process envelope')
            value=values[0]
            require(value.get('session_id',session)==session,'Enrollment process session changed')
            chunks.append(value['output']);pending=None;last_end=end
            if type(value.get('exit_code')) is int:
                result=[{'exit_code':value['exit_code'],'output':''.join(chunks)}]
                return (result,end) if _with_end else result
    return ([],None) if _with_end else []

def stdout_objects(text):
    result=[]
    for line in text.splitlines():
        try:value=json.loads(line)
        except ValueError:continue
        if isinstance(value,dict):result.append(value)
    return result

def successful_output(raw,call_id,state):
    envelopes=host_results(raw,call_id)
    require(len(envelopes)==1,'Enrollment must run as one standalone host process')
    matches=[v for v in envelopes if v['exit_code']==0 and any(
        obj.get('status')=='created' and obj.get('attempt_id')==state['attempt_id'] and obj.get('prefix_sha256')==state['prefix_sha256']
        for obj in stdout_objects(v['output']))]
    require(len(matches)==1,'Enrollment needs one original successful process envelope and its matching stdout JSON')

def enrollment_status(raw,*,epochs=()):
    active=[];failed=[]
    for payload,text,end,complete in enrollment_rows(raw,epochs=epochs):
        values=host_results(raw,payload.get('call_id'))
        token=re.search(r'--enrollment(?:=|\s+)([0-9a-f]{32})',text).group(1)
        created=any(obj.get('status')=='created' and obj.get('attempt_id')==token
                    for value in values for obj in stdout_objects(value['output']))
        if len(values)==1 and values[0]['exit_code']!=0 and not created:
            failed.append({'call_id':payload.get('call_id'),'exit_code':values[0]['exit_code']})
        else:active.append((payload,text,end,complete))
    return active,failed

def legacy_active(project,raw):
    """Blocking only; never authorize a historical alias or create a scope."""
    project=Path(project).resolve(strict=True)
    current=Path(__file__).resolve().parents[2]/'scripts/join_attempt.py'
    for member in _SCRIPT_MEMBERS:
        script=project/member
        if script==current:continue
        active,_=enrollment_status(raw,epochs=((0,script,False),))
        if any(Path(enrollment_command(payload,script=script,live=False)[1]['--project']).resolve()==project
               for payload,_,_,_ in active):return True
    return False

def verify_pristine(pristine):
    """Reject a migration output tree relabeled as an original empty shell."""
    mapping=pristine.get('files')
    require(isinstance(mapping,dict) and mapping,'Pristine manifest must contain the approved empty shell files')
    for name,value in mapping.items():
        require(isinstance(name,str) and name and '\\' not in name,'Invalid pristine relative path')
        path=PurePosixPath(name)
        require(path.parts and not path.is_absolute() and '..' not in path.parts and ':' not in name,'Invalid pristine relative path')
        require(unicodedata.normalize('NFC',path.parts[0]).casefold() not in {'spec','.migbot','.hmigbot-ios','.agents','.codex','work'},'Pristine backup contains migration or installed-tool artifacts: '+name)
        require(isinstance(value,str) and re.fullmatch('[0-9a-fA-F]{64}',value),'Invalid pristine file digest')

def expected_tree(project,pristine,installed,handoff_hash=None):
    require(installed.get('owner')=='hmigbot-ios','Wrong install owner')
    for name in installed['files']:
        require(not Path(name).is_absolute() and '..' not in Path(name).parts and (name=='.codex/config.toml' or name.startswith(('.hmigbot-ios/','.agents/hmigbot-runtime/','.agents/skills/','.codex/agents/','.migbot/bin/','.migbot/policies/'))),'Install ownership cannot claim application or spec artifacts')
    expected={**pristine['files'],**installed['files']}
    expected['AGENTS.md']=installed['agent_installed_sha256']
    expected['.hmigbot-ios/install.json']=digest(project/'.hmigbot-ios/install.json')
    if handoff_hash:expected['MIGRATION-HANDOFF.md']=handoff_hash
    return expected

def verify_recovery(project,native,raw,receipt,*,current_tree=False,check_install=True,epochs=None):
    from .join_scope import read_trace,audit
    pristine=load(receipt['pristine_manifest']);archived=load(receipt['archive_manifest'])
    require(digest(receipt['pristine_manifest'])==receipt['pristine_manifest_sha256'],'Approved pristine manifest changed')
    verify_pristine(pristine)
    require(Path(pristine['workspace']).resolve()==project==Path(archived['workspace']).resolve(),'Recovery manifests belong to another project')
    backup=Path(pristine['backup']).resolve(strict=True);archive=Path(archived['archive']).resolve(strict=True)
    for path in [backup,archive]:require(not path.is_relative_to(project) and not project.is_relative_to(path),'Recovery tree must be external')
    require(files(backup)==pristine['files'] and files(archive)==archived['files'],'Recovery tree contents changed')
    if check_install:
        installed=load(project/'.hmigbot-ios/install.json')
        require(installed==receipt['installed_manifest'] and installed.get('version')==receipt['tool_version'],'Recovery installed tool manifest changed')
        expected=expected_tree(project,pristine,installed,receipt['post_install_files'].get('MIGRATION-HANDOFF.md'))
        require(expected==receipt['post_install_files'],'Receipt cannot add partial artifacts to the restored tree')
        for name,expected_hash in installed['files'].items():
            path=project/name
            require(path.resolve().is_relative_to(project) and path.is_file() and not path.is_symlink()
                    and not getattr(path,'is_junction',lambda:False)() and digest(path)==expected_hash,
                    'Installed owned file changed: '+name)
        if current_tree:
            require(not (project/'.migbot/config.json').exists(),'Enrollment requires a restored project before INIT')
            require(files(project)==expected,'Project is not the exact verified restored-and-installed tree')
    history=receipt['history'];snapshot=Path(history['snapshot']).read_bytes()
    with contextlib.redirect_stdout(io.StringIO()):result,code=audit([read_trace(native,raw=snapshot,history=True)])
    if epochs is None:epochs=enrollment_epochs(project,raw,receipt)
    foreign=foreign_enrollments(snapshot,epochs=epochs)
    if foreign:code=1
    recorded=load(history['audit'])
    require(recorded.get('foreign_enrollments',[])==foreign,'Historical foreign enrollment diagnostics changed')
    require(result['totals']==recorded['totals'] and result['handles']==recorded['handles'] and result['source_evidence']==recorded['source_evidence'] and code==history['exit_code'],'Historical audit does not match actual native observations')
    return recorded

def marker(raw,token,receipt_sha,call_id=None,*,epochs=()):
    matches=[(payload,end,complete) for payload,text,end,complete in enrollment_rows(raw,epochs=epochs)
             if flag(text,'enrollment',token) and flag(text,'receipt-sha256',receipt_sha)
             and (call_id is None or payload.get('call_id')==call_id)]
    require(len(matches)==1,'Enrollment must match exactly one original host tool call')
    payload,end,complete=matches[0]
    require(complete and payload.get('call_id'),'Enrollment call is not a complete native record')
    return payload['call_id'],end

def idle_trace(raw,trace):
    """A complete list must follow all agent controls; history stays failed."""
    pending={}; controls=set(); last_control_output=-1; last_list=-1; last_invalid=-1; latest=[]
    from .join_scope import _object,_name,full_list_args,stopped_status,valid_agents,AGENT_CONTROLS,AGENT_OPERATIONS
    for row,end,_ in rows(raw):
        payload=row.get('payload',{})
        require(not (payload.get('type')=='custom_tool_call' and _name(payload) in AGENT_OPERATIONS),'Unsupported custom agent control cannot prove recovery idle')
        if payload.get('type')=='function_call':
            name=_name(payload);pending[payload.get('call_id')]=(name,_object(payload.get('arguments')),end)
            if name in AGENT_CONTROLS:controls.add(payload.get('call_id'))
        elif payload.get('type')=='function_call_output' and payload.get('call_id') in controls:
            controls.remove(payload['call_id']);last_control_output=end
        elif payload.get('type')=='function_call_output' and pending.get(payload.get('call_id'),(None,))[0]=='list_agents':
            value=_object(payload.get('output'))
            _,args,requested_at=pending[payload['call_id']]
            if not isinstance(value,dict) or not valid_agents(value.get('agents')):
                last_invalid=end
            elif full_list_args(args,trace.scope):
                last_list=requested_at;latest=value['agents']
    require(not controls,'An earlier agent control has no original output; it may still be active')
    require(last_list>max(last_control_output,last_invalid),'A real complete list_agents call is required after all agent controls returned and any invalid listing')
    for agent in latest:
        require(isinstance(agent,dict),'Malformed agent in complete list_agents response')
        name=agent.get('agent_name','')
        if isinstance(name,str) and name.startswith(trace.scope+'/'):
            status=agent.get('agent_status')
            require(stopped_status(status),'A previous child is still active or unknown: '+name)

def make_receipt(project,pristine_manifest,archive_manifest,out,*,pristine_sha256):
    from .join_scope import current_rollout,read_trace,audit,native_bytes
    project=Path(project).resolve(strict=True);out=Path(out).resolve()
    pristine_manifest=Path(pristine_manifest).resolve(strict=True)
    archive_manifest=Path(archive_manifest).resolve(strict=True)
    require(isinstance(pristine_sha256,str) and re.fullmatch('[0-9a-fA-F]{64}',pristine_sha256)
            and digest(pristine_manifest)==pristine_sha256.lower(),'Pristine manifest must match its previously approved SHA-256 anchor')
    pristine=load(pristine_manifest); archived=load(archive_manifest)
    verify_pristine(pristine)
    require(Path(pristine['workspace']).resolve()==project==Path(archived['workspace']).resolve(),'Recovery project identity mismatch')
    backup=Path(pristine['backup']).resolve(strict=True);archive=Path(archived['archive']).resolve(strict=True)
    for external in [backup,archive,out]:
        require(not external.is_relative_to(project) and not project.is_relative_to(external),'Recovery paths must be independent of the project')
    require(not out.is_relative_to(backup) and not out.is_relative_to(archive),'Evidence output must not change frozen backup or archive')
    require(out.parent.is_dir(),'Recovery output parent must already exist')
    require(files(backup)==pristine['files'],'Pristine backup changed')
    require(files(archive)==archived['files'],'Failed-attempt archive changed or incomplete')
    require(not (project/'.migbot/config.json').exists() and not (project/STATE).exists(),'Enrollment requires a restored project before INIT')
    installed=load(project/'.hmigbot-ios/install.json')
    require(installed.get('owner')=='hmigbot-ios' and installed.get('version')==__version__,'Installed tool identity mismatch')
    expected=expected_tree(project,pristine,installed,digest(project/'MIGRATION-HANDOFF.md') if (project/'MIGRATION-HANDOFF.md').is_file() else None)
    require(files(project)==expected,'Project is not the verified restored-and-installed tree')
    native=current_rollout();require(native is not None,'Actual CODEX_THREAD_ID is required')
    raw=native_bytes(native); trace=read_trace(native,raw=raw,history=True)
    require(trace.scope=='/root','Only the actual root dispatcher may enroll a restart')
    idle_trace(raw,trace)
    previous=load(archive/STATE) if (archive/STATE).is_file() else None
    if previous is None:
        require(not legacy_active(project,raw),'Earlier enrollment exists; its state must be preserved in the failed-attempt archive')
    history=out.with_suffix('.history.jsonl'); history_audit=out.with_suffix('.history-audit.json');history_log=out.with_suffix('.history-audit.log')
    require(not any(path.exists() for path in [out,history,history_audit,history_log]),'Recovery evidence already exists; do not overwrite')
    receipt={'schema':RECEIPT,'project':str(project),'tool_version':__version__,
             'tool_sha256':tool_sha(),'previous_attempt':previous,
             'installed_manifest':installed,
             'pristine_manifest':str(pristine_manifest),'pristine_manifest_sha256':digest(pristine_manifest),
             'archive_manifest':str(archive_manifest),'archive_manifest_sha256':digest(archive_manifest),
             'post_install_files':expected,'thread_id':trace.meta['id'],'rollout':str(native),
             'history':{'snapshot':str(history),'sha256':sha(raw),'bytes':len(raw),'audit':str(history_audit)}}
    epochs=enrollment_epochs(project,raw,receipt,sealing=True)
    prior_enrollments,_=enrollment_status(raw,epochs=epochs)
    if prior_enrollments:
        require(previous is not None,'Earlier enrollment exists; its state must be preserved in the failed-attempt archive')
        validate_state(project,native,raw,previous,check_tool=False,through=previous.get('start_bytes'),epochs=epochs)
    else:require(previous is None,'Archived attempt has no original enrollment')
    with history.open('xb') as stream:stream.write(raw)
    printed=io.StringIO()
    with contextlib.redirect_stdout(printed):result,code=audit([trace])
    foreign=foreign_enrollments(raw,epochs=epochs)
    if foreign:
        result['foreign_enrollments']=foreign;code=1
        printed.write(f'FOREIGN_ENROLLMENT: {len(foreign)} noncanonical historical candidates retained; no completion is inferred.\n')
    result.update(original_rollout=str(native),snapshot=str(history),snapshot_sha256=sha(raw),history_only=True)
    history_audit.write_bytes(encoded(result))
    with history_log.open('x',encoding='utf-8') as stream:stream.write(printed.getvalue())
    receipt['history'].update(audit_sha256=digest(history_audit),exit_code=code)
    with out.open('xb') as stream:stream.write(encoded(receipt))
    return {'receipt':str(out),'receipt_sha256':digest(out),'history_exit_code':code}

def validate_state(project,native,raw,state,*,finalized=True,check_tool=True,through=None,epochs=None,_return_binding=False):
    from .join_scope import _meta,read_trace,AGENT_OPERATIONS
    project=Path(project).resolve(strict=True);native=Path(native).resolve(strict=True)
    require(state.get('schema')==SCHEMA,'Invalid join-attempt schema')
    require(Path(state['project']).resolve()==project,'Attempt project mismatch')
    require(state['thread_id']==os.environ.get('CODEX_THREAD_ID')==_meta(native).get('id'),'Attempt thread mismatch')
    require(Path(state['rollout']).resolve(strict=True)==native,'Attempt native file changed')
    binding=None
    if check_tool:
        from .join_upgrade import POINTER,validate_binding
        if (project/POINTER).exists():binding=validate_binding(project,native,raw,state)
        else:require(state.get('tool_version')==__version__ and state.get('tool_sha256')==tool_sha(),'Join attempt tool changed')
    receipt_path=Path(state['receipt']).resolve(strict=True)
    require(digest(receipt_path)==state['receipt_sha256'],'Recovery receipt changed')
    receipt=load(receipt_path)
    require(receipt.get('schema')==RECEIPT and receipt.get('tool_version')==state['tool_version'] and receipt.get('tool_sha256')==state['tool_sha256'],'Invalid recovery receipt')
    require(Path(receipt['project']).resolve()==project and receipt['thread_id']==state['thread_id'],'Recovery receipt belongs to another project or thread')
    require(Path(receipt['rollout']).resolve(strict=True)==native,'Recovery receipt log mismatch')
    if epochs is None:epochs=binding['epochs'] if binding else enrollment_epochs(project,raw,receipt)
    for name in ['pristine_manifest','archive_manifest']:
        require(digest(receipt[name])==receipt[name+'_sha256'],'Recovery manifest changed: '+name)
    history=receipt['history']; snapshot=Path(history['snapshot']).read_bytes()
    require(len(snapshot)==history['bytes'] and sha(snapshot)==history['sha256'] and raw.startswith(snapshot),'Prior complete history changed')
    require(digest(history['audit'])==history['audit_sha256'],'Historical audit changed')
    require(not any(v['end_bytes']>history['bytes'] and (through is None or v['end_bytes']<=through) for v in foreign_enrollments(raw,epochs=epochs)),
            'Noncanonical enrollment after this recovery seal; preserve the failure and perform authorized recovery')
    historical=verify_recovery(project,native,raw,receipt,check_install=check_tool and binding is None,epochs=epochs)
    require(state['history_summary']=={'exit_code':history['exit_code'],'unjoined':historical['totals']['unjoined'],'audit':history['audit'],'audit_sha256':history['audit_sha256']},'Historical failure summary changed')
    previous=receipt.get('previous_attempt')
    older_end=0
    if previous:
        validate_state(project,native,raw,previous,check_tool=False,through=previous.get('start_bytes'),epochs=epochs)
        older_end=previous['start_bytes']
        require(history['bytes']>older_end,'Recovery does not preserve the previous attempt')
    active,failed=enrollment_status(raw,epochs=epochs)
    current=[p for p,text,end,_ in active if end>older_end and (through is None or end<=through)]
    require(len(current)==1 and current[0].get('call_id')==state['enrollment_call_id'],'Additional begin calls cannot move or mask an attempt')
    call_id,end=marker(raw,state['attempt_id'],state['receipt_sha256'],state['enrollment_call_id'],epochs=epochs)
    call_start=raw.rfind(b'\n',0,end-1)+1
    require(history['bytes']<=call_start,'Recovery snapshot overlaps the enrollment request')
    prefix=raw[:call_start]
    idle_trace(prefix,read_trace(native,raw=prefix,history=True))
    entry=next(p for p,_,rowend,_ in enrollment_rows(raw,epochs=epochs) if rowend==end and p.get('call_id')==call_id)
    script,live=_enrollment_epoch(raw,end,epochs)
    if check_tool and binding is None:require(live,'Current enrollment is outside the current recovery epoch')
    _,options=enrollment_command(entry,script=script,live=live)
    require(Path(options['--project']).resolve()==project and Path(options['--receipt']).resolve()==receipt_path,'Enrollment argv does not match its project and recovery receipt')
    require(options['--enrollment']==state['attempt_id'] and options['--receipt-sha256']==state['receipt_sha256'],'Enrollment argv identity mismatch')
    require(type(state['start_bytes']) is int and end==state['start_bytes'],'Attempt cursor is not the real enrollment call boundary')
    require(sha(raw[:end])==state['prefix_sha256'],'Original log prefix changed')
    require(state['failed_enrollments']==[v for v in failed if any(p.get('call_id')==v['call_id'] and oldend<=end for p,_,oldend,_ in enrollment_rows(raw,epochs=epochs))],'Failed enrollment audit changed')
    for row,rowend,_ in rows(raw):
        p=row.get('payload',{})
        if history['bytes']<rowend<end and p.get('type') in ('function_call','custom_tool_call') and str(p.get('name','')).rsplit('.',1)[-1] in AGENT_OPERATIONS - {'list_agents'}:
            raise ValueError('Agent work occurred between recovery seal and enrollment; seal again after authorized recovery')
    if finalized:successful_output(raw,call_id,state)
    return (state,binding) if _return_binding else state

def begin_attempt(project,receipt_path,receipt_sha,enrollment):
    from .join_scope import current_rollout,read_trace,native_bytes
    require(re.fullmatch('[0-9a-f]{32}',enrollment) is not None,'Enrollment must be a unique 32-hex nonce')
    project=Path(project).resolve(strict=True);receipt_path=Path(receipt_path).resolve(strict=True)
    native=current_rollout();require(native is not None,'Actual CODEX_THREAD_ID is required')
    raw=native_bytes(native);state_path=project/STATE
    if state_path.exists():
        state=validate_state(project,native,raw,load(state_path))
        require(state['attempt_id']==enrollment and state['receipt_sha256']==receipt_sha and Path(state['receipt']).resolve()==receipt_path,'Active attempt cannot be replaced or moved')
        return {**state,'status':'exists'}
    require(digest(receipt_path)==receipt_sha,'Receipt SHA does not match actual recovery evidence')
    receipt=load(receipt_path)
    require(receipt.get('schema')==RECEIPT and receipt.get('tool_version')==__version__,'Recovery receipt identity mismatch')
    require(Path(receipt['project']).resolve()==project and receipt['thread_id']==os.environ.get('CODEX_THREAD_ID'),'Recovery receipt project/thread mismatch')
    epochs=enrollment_epochs(project,raw,receipt)
    for retry in range(11):
        try:marker(raw,enrollment,receipt_sha,epochs=epochs);break
        except ValueError:
            if retry==10:raise
            time.sleep(.2);raw=native_bytes(native)
    verify_recovery(project,native,raw,receipt,current_tree=True,epochs=epochs)
    trace=read_trace(native,raw=raw,history=True);require(trace.scope=='/root','Only the actual root dispatcher can enroll')
    idle_trace(raw,trace)
    call_id,end=marker(raw,enrollment,receipt_sha,epochs=epochs)
    state={'schema':SCHEMA,'tool_version':__version__,'attempt_id':enrollment,'project':str(project),
           'tool_sha256':tool_sha(),
           'thread_id':trace.meta['id'],'rollout':str(native),'enrollment_call_id':call_id,
           'start_bytes':end,'prefix_sha256':sha(raw[:end]),'receipt':str(receipt_path),'receipt_sha256':receipt_sha}
    _,failed=enrollment_status(raw,epochs=epochs);state['failed_enrollments']=failed
    history=receipt['history'];historical=load(history['audit'])
    state['history_summary']={'exit_code':history['exit_code'],'unjoined':historical['totals']['unjoined'],'audit':history['audit'],'audit_sha256':history['audit_sha256']}
    validate_state(project,native,raw,state,finalized=False,epochs=epochs)
    state_path.parent.mkdir(parents=True,exist_ok=True)
    with state_path.open('xb') as stream:stream.write(encoded(state))
    return {**state,'status':'created'}

def scoped_trace(project,native):
    from .join_scope import read_trace,caller,_meta,native_bytes
    native=Path(native).resolve(strict=True);raw=native_bytes(native)
    if caller(_meta(native))!='/root':return read_trace(native,raw=raw)
    path=Path(project).resolve(strict=True)/STATE
    if not path.exists():
        active,_=enrollment_status(raw)
        require(not active,'A recorded attempt lost its state; authorized recovery is required')
        require(not legacy_active(path.parent.parent,raw),
                'A recorded attempt lost its state; authorized recovery is required')
        return read_trace(native,raw=raw)
    state,binding=validate_state(project,native,raw,load(path),_return_binding=True)
    trace=read_trace(native,raw=raw,start_after=state['start_bytes'],enrollment_epochs=binding['epochs'] if binding else None)
    if binding:trace.tool_upgrade={'receipt':binding['receipt'],'receipt_sha256':binding['receipt_sha256']}
    trace.attempt=state
    return trace

def main(argv=None):
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    seal=sub.add_parser('seal');seal.add_argument('--project',required=True);seal.add_argument('--pristine-manifest',required=True);seal.add_argument('--pristine-sha256',required=True);seal.add_argument('--archive-manifest',required=True);seal.add_argument('--out',required=True)
    begin=sub.add_parser('begin');begin.add_argument('--project',required=True);begin.add_argument('--receipt',required=True);begin.add_argument('--receipt-sha256',required=True);begin.add_argument('--enrollment',required=True)
    upgrade=sub.add_parser('upgrade')
    for name in ('project','origin-package','package-manifest','package-sha256','evidence-root','upgrade'):upgrade.add_argument('--'+name,required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=='upgrade':
            from .join_upgrade import upgrade as perform_upgrade
            result=perform_upgrade(args.project,args.origin_package,args.package_manifest,args.package_sha256,args.evidence_root,args.upgrade)
        elif args.command=='seal':result=make_receipt(args.project,args.pristine_manifest,args.archive_manifest,args.out,pristine_sha256=args.pristine_sha256)
        else:result=begin_attempt(args.project,args.receipt,args.receipt_sha256,args.enrollment)
        print(json.dumps(result,ensure_ascii=False));return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr);return 3

if __name__=='__main__':raise SystemExit(main())
