"""Verify host-marked inherited context without treating it as actor work."""
import hashlib
import json
import re
from pathlib import Path

def inherited_context(path, lines, meta):
    from .join_scope import ScopeError, caller, native_bytes, _name, _object
    def need(value, message):
        if not value: raise ScopeError(message)
    def fingerprint(payload):
        raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        return hashlib.sha256(raw).hexdigest()
    parsed=[json.loads(line) for line in lines if line.strip()]
    need(len(parsed)==len(lines),'Fork context cannot contain blank native rows')
    own=parsed[0]
    need(own.get('type')=='session_meta' and own.get('payload')==meta,'Fork needs its own first metadata row')
    parent_id=meta.get('forked_from_id');scope=caller(meta)
    source=meta.get('source',{})
    need(isinstance(source,dict) and isinstance(source.get('subagent'),dict),'Invalid fork source metadata')
    spawn=source['subagent'].get('thread_spawn')
    need(isinstance(spawn,dict),'Missing fork spawn metadata')
    need(isinstance(parent_id,str) and re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',parent_id),'Invalid fork parent identity')
    need(parent_id==meta.get('parent_thread_id')==spawn.get('parent_thread_id') and parent_id!=meta.get('id'),'Fork parent identities disagree')
    # Only the observed direct-child host format is supported here.
    need(type(spawn.get('depth')) is int and spawn['depth']==1 and scope.count('/')==2
         and scope==meta.get('agent_path')==spawn.get('agent_path'),'Unsupported nested or conflicting fork scope')
    marked=lambda r:isinstance(r.get('metadata'),dict) and r['metadata'].get('inherited_user_message') is True
    if len(parsed)<2 or parsed[1].get('type')!='session_meta':
        need(not any(marked(r) for r in parsed),'Inherited context is missing its parent metadata')
        return None  # A no-history child has no inherited header or operations.
    parent_meta=parsed[1].get('payload',{})
    need(parent_meta.get('id')==parent_id and caller(parent_meta)=='/root' and not parent_meta.get('forked_from_id'),'Inherited metadata is not the actual root parent')
    need('metadata' not in parsed[1],'Unsupported marked parent metadata')
    preamble={'compacted','world_state','turn_context'}
    inherited=[];last=1;started=False;ended=False
    for index,row in enumerate(parsed[2:],2):
        md=row.get('metadata',{})
        if isinstance(md,dict) and 'inherited_user_message' in md:
            need(type(md['inherited_user_message']) is bool,'Inherited marker must be a host boolean')
        if row.get('type')=='response_item':
            if marked(row):
                need(not ended and type(md.get('client_authored')) is bool and md['client_authored'] is False,'Inherited responses must form one host-authored prefix')
                need(isinstance(row.get('payload'),dict),'Inherited response payload must be an object')
                inherited.append(row['payload']);started=True;last=index
            else:
                need(started,'Inherited header has no marked response prefix')
                ended=True
        elif not ended:
            need(not marked(row) and row.get('type') in preamble,'Unsupported row in inherited context preamble')
            last=index
        else:need(not marked(row),'Inherited context cannot resume after actor work')
    need(started and ended,'Fork context lacks its actor boundary')
    compared=[p for p in inherited if p.get('type')!='reasoning']
    need(compared,'Inherited context has no verifiable parent records')
    anchor=compared[-1];cid=anchor.get('call_id')
    args=_object(anchor.get('arguments'))
    need(anchor.get('type')=='function_call' and _name(anchor)=='spawn_agent' and isinstance(cid,str) and cid
         and isinstance(args,dict) and args.get('task_name')==scope.rsplit('/',1)[1],'Inherited prefix must end at this child spawn request')
    sessions=next((p for p in Path(path).resolve(strict=True).parents if p.name=='sessions'),None)
    need(sessions is not None,'Native sessions directory is unavailable')
    matches=list(sessions.rglob('*'+parent_id+'.jsonl'))
    need(len(matches)==1,'Fork parent native file is not unique')
    parent=matches[0].resolve(strict=True)
    need(parent!=Path(path).resolve(strict=True),'Fork parent cannot be its own file')
    raw=native_bytes(parent);signatures=[];requests=[];outputs=[];first=None;cut=False
    for line in raw.splitlines():
        if not line.strip():continue
        row=json.loads(line)
        if first is None and row.get('type')=='session_meta':first=row.get('payload',{})
        if row.get('type')!='response_item':continue
        payload=row.get('payload',{})
        if not cut and payload.get('type')!='reasoning':signatures.append(fingerprint(payload))
        if payload.get('call_id')!=cid:continue
        if payload.get('type')=='function_call':
            requests.append(payload);cut=True
        elif payload.get('type')=='function_call_output':outputs.append(_object(payload.get('output')))
    need(first is not None and first.get('id')==parent_id and caller(first)=='/root' and not first.get('forked_from_id'),'Fork parent native metadata mismatch')
    need(len(requests)==1 and requests[0]==anchor,'Fork spawn request does not match its parent')
    # task_name is the existing native host's canonical returned agent path.
    need(len(outputs)==1 and isinstance(outputs[0],dict) and outputs[0].get('task_name')==scope,'Fork spawn output does not identify this child')
    sequence=iter(signatures)
    for payload in compared:
        wanted=fingerprint(payload)
        need(any(value==wanted for value in sequence),'Inherited parent payload changed or reordered')
    return {'line_numbers':set(range(2,last+2)),
            'evidence':{'parent_path':str(parent),'parent_thread_id':parent_id,'parent_sha256':hashlib.sha256(raw).hexdigest(),
                        'parent_read_bytes':len(raw),'spawn_call_id':cid,'inherited_response_items':len(inherited),
                        'parent_matched_nonreasoning_items':len(compared),'transformed_reasoning_items':len(inherited)-len(compared)}}
