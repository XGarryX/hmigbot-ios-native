"""Native host scope reader bound to the actual dispatcher thread.

Reads the complete original JSONL in memory. Never translates paths in evidence,
creates a derived rollout, or accepts a caller-supplied dispatcher override.
Completion uses native list observations or authenticated host agent messages;
neither ordinary message text nor file existence proves a task has finished.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import time


class ScopeError(ValueError):
    pass


AGENT_CONTROLS = frozenset({'spawn_agent','followup_task','send_message','send_input','resume_agent','interrupt_agent','close_agent','wait_agent'})
AGENT_OPERATIONS = AGENT_CONTROLS | {'list_agents'}
RESTART_CONTROLS = frozenset({'followup_task', 'send_input', 'resume_agent'})
TERMINATING_CONTROLS = frozenset({'interrupt_agent', 'close_agent'})


def native_agent_message(payload, scope, kind):
    """Recognize the observed host channel, never an arbitrary prose marker.

    The collaboration transport records an agent_message with tool provenance
    and a routing envelope. User/developer message copies are deliberately not
    considered. The transport currently has no verified child-turn identifier;
    callers therefore cannot use this signal after reusing a task handle.
    """
    if not isinstance(payload, dict) or payload.get('type') != 'agent_message':
        return None
    content = payload.get('content')
    metadata = payload.get('internal_chat_message_metadata_passthrough', {})
    if not isinstance(content, list) or not isinstance(metadata, dict):
        return None
    parts = metadata.get('content_item_metadata')
    if not isinstance(parts, list) or len(parts) != len(content):
        return None
    texts = []
    encrypted_body = False
    for item, evidence in zip(content, parts):
        if not isinstance(item, dict) or not isinstance(evidence, dict):
            return None
        if evidence.get('provenance') != {'type': 'tool', 'namespace': 'collaboration'}:
            return None
        if item.get('type') == 'input_text':
            if not isinstance(item.get('text'), str):
                return None
            texts.append(item['text'])
        elif item.get('type') == 'encrypted_content':
            body = item.get('encrypted_content')
            if not isinstance(body, str) or not body:
                return None
            encrypted_body = True
        else:
            return None
    author, recipient, ident = payload.get('author'), payload.get('recipient'), payload.get('id')
    if (not isinstance(author, str) or recipient != scope or not isinstance(ident, str)
            or not ident or len(texts) != 1):
        return None
    prefix = 'Message Type: ' + kind + '\nTask name: ' + scope + '\nSender: ' + author + '\nPayload:\n'
    if not texts[0].startswith(prefix) or not (texts[0][len(prefix):].strip() or encrypted_body):
        return None
    return {'author': author, 'message_id': ident,
            'envelope_sha256': hashlib.sha256(json.dumps(payload, sort_keys=True,
                ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()}


def native_final_message(payload, scope):
    return native_agent_message(payload, scope, 'FINAL_ANSWER')


def thread_spawn(meta):
    if not isinstance(meta, dict):
        raise ScopeError('session_meta 必须是对象')
    source = meta.get('source')
    if not isinstance(source, dict) or 'subagent' not in source:
        return {}
    subagent = source['subagent']
    if not isinstance(subagent, dict) or not isinstance(subagent.get('thread_spawn'), dict):
        raise ScopeError('session_meta 子任务来源格式不可核验')
    return subagent['thread_spawn']


def inherited_history_boundary(lines, meta, scope):
    """Exclude copied ancestor calls only at the observed native NEW_TASK edge.

    Full-history forks include their parent's session_meta and unfinished spawn
    call before their own authenticated task delivery. All bytes are decoded and
    parsed here as well as fingerprinted; no caller-controlled cursor is used.
    """
    rows = []
    offset = 0
    for number, line in enumerate(lines, 1):
        offset += len(line)
        if not line.strip():
            continue
        try:
            value = json.loads(line.decode('utf-8-sig' if number == 1 else 'utf-8'))
        except (ValueError, UnicodeError) as exc:
            raise ScopeError(f'原生日志第 {number} 行不完整或损坏：{exc}') from exc
        if not isinstance(value, dict):
            raise ScopeError('原生日志行必须是对象')
        rows.append((value, offset))
    sessions = [(row.get('payload'), end) for row, end in rows if row.get('type') == 'session_meta']
    if any(not isinstance(value, dict) or not isinstance(value.get('id'), str) or not value['id']
           for value, _ in sessions):
        raise ScopeError('原生日志会话元数据身份无效')
    foreign = [(value, end) for value, end in sessions if value['id'] != meta.get('id')]
    if not foreign:
        return 0
    spawn = thread_spawn(meta)
    parent = spawn.get('parent_thread_id')
    if scope == '/root' or not isinstance(parent, str) or not parent:
        raise ScopeError('原生日志含其他会话元数据，但缺少明确的当前子任务父身份')
    parent_scope = scope.rsplit('/', 1)[0]
    if not any(value['id'] == parent and caller(value) == parent_scope for value, _ in foreign):
        raise ScopeError('继承历史的父线程元数据与当前子任务不匹配')
    for row, end in rows:
        if row.get('type') != 'response_item':
            continue
        message = native_agent_message(row.get('payload'), scope, 'NEW_TASK')
        if message is not None and message['author'] == parent_scope:
            if any(foreign_end >= end for _, foreign_end in foreign):
                raise ScopeError('自身任务边界后出现外部会话元数据，不能隔离继承历史')
            return end
    raise ScopeError('继承历史缺少与真实父子身份一致的原生NEW_TASK边界')


def control_error(value):
    parsed = _object(value)
    if isinstance(parsed, dict) and parsed.get('error'):
        return str(parsed['error'])
    return None

def native_bytes(path):
    """Wait briefly for an in-progress final record; never discard its bytes."""
    for _ in range(11):
        raw=Path(path).read_bytes()
        if not raw or raw.endswith(b'\n'):return raw
        time.sleep(.2)
    raise ScopeError('原生日志末行尚未完整落盘，稍后重跑；禁止裁剪该行')


def _object(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return None
    return value if isinstance(value, dict) else None


def _name(payload):
    return str(payload.get('name', '')).rsplit('.', 1)[-1]


def full_list_args(args, scope):
    """Only a complete listing of this dispatcher's subtree proves absence."""
    return isinstance(args, dict) and not (set(args) - {'path_prefix'}) and args.get('path_prefix') in (None, '', scope)


def valid_agents(agents):
    return isinstance(agents,list) and all(isinstance(agent,dict) and isinstance(agent.get('agent_name'),str) and agent['agent_name'] for agent in agents)


def stopped_status(value):
    return isinstance(value, dict) and 'completed' in value or isinstance(value, str) and value in ('interrupted', 'errored', 'idle')


def string_values(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for part in value.values():
            yield from string_values(part)
    elif isinstance(value, list):
        for part in value:
            yield from string_values(part)


def _meta(path):
    with path.open(encoding='utf-8-sig') as stream:
        for line in stream:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get('type') == 'session_meta':
                return row.get('payload', {})
    raise ScopeError('原生日志缺少 session_meta，无法确认派发者身份')


def caller(meta):
    spawn = thread_spawn(meta)
    direct = meta.get('agent_path')
    nested = spawn.get('agent_path')
    if direct and nested and direct != nested:
        raise ScopeError('session_meta 中 agent_path 相互矛盾')
    result = direct or nested or '/root'
    if not isinstance(result, str) or not result.startswith('/root') or any(x in ('.', '..', '') for x in result.split('/')[1:]):
        raise ScopeError('session_meta 中 agent_path 无效')
    return result.rstrip('/')


def is_nested(path):
    return caller(_meta(Path(path))) != '/root'


def current_rollout():
    """Locate the actual host thread, never aggregate sessions sharing a cwd."""
    thread_id = os.environ.get('CODEX_THREAD_ID')
    if not thread_id:
        return None
    sessions = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'sessions'
    matches = list(sessions.rglob('*' + thread_id + '.jsonl')) if sessions.is_dir() else []
    if len(matches) != 1:
        raise ScopeError('无法唯一定位实际 CODEX_THREAD_ID 的原生日志；禁止选择或拼接其他记录')
    meta = _meta(matches[0])
    if meta.get('id') != thread_id:
        raise ScopeError('宿主原生日志 meta.id 与实际 CODEX_THREAD_ID 不一致')
    return matches[0].resolve(strict=True)


def current_scope():
    """The running process identity comes from host storage, never the input log."""
    path=current_rollout()
    return caller(_meta(path)) if path is not None else None


@dataclass
class Trace:
    path: Path
    meta: dict
    scope: str
    handles: dict = field(default_factory=dict)
    status: dict = field(default_factory=dict)
    completed: set = field(default_factory=set)
    waits: int = 0
    lists: int = 0
    spawns: int = 0
    gates: int = 0
    status_ts: str = ''
    last_ts: str = ''
    source_sha256: str = ''
    source_bytes: int = 0
    attempt: dict | None = None
    source_data: bytes = field(default=b'',repr=False)
    failed_spawns: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    last_spawn_call: int = -1
    last_spawn_output: int = -1
    last_full_list_call: int = -1
    last_invalid_list_output: int = -1
    invalid_lists: list = field(default_factory=list)
    completion_evidence: dict = field(default_factory=dict)
    failed_controls: list = field(default_factory=list)
    unverified_controls: list = field(default_factory=list)
    pending_controls: dict = field(default_factory=dict)
    successful_controls: dict = field(default_factory=dict)
    rejected_final_messages: list = field(default_factory=list)
    terminal_observations: dict = field(default_factory=dict)
    inherited_history_bytes: int = 0


def read_trace(path, *, raw=None, start_after=0, history=False):
    path = Path(path).resolve(strict=True)
    raw = path.read_bytes() if raw is None else raw
    if type(start_after) is not int or not 0 <= start_after <= len(raw) or start_after and raw[start_after-1:start_after] != b'\n':
        raise ScopeError('尝试边界必须是完整原始记录的字节行尾')
    physical_lines=raw.splitlines(keepends=True)
    lines=[line.decode('utf-8-sig' if i==0 else 'utf-8') for i,line in enumerate(physical_lines)]
    meta = None
    for line in lines:
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get('type') == 'session_meta':
            meta = row.get('payload', {})
            break
    if meta is None:
        raise ScopeError('原生日志缺少 session_meta')
    scope = caller(meta)
    trace = Trace(path, meta, scope, source_sha256=hashlib.sha256(raw).hexdigest(), source_bytes=len(raw),source_data=raw)
    trace.inherited_history_bytes = inherited_history_boundary(physical_lines, meta, scope)
    pending = {}
    pending_args = {}
    pending_offsets = {}
    returned = set()
    unresolved = set()
    offset = 0
    prior_calls = set()
    prior_tasks = set()
    prior_names = set()
    prior_aliases = set()
    prior_pending = {}
    prior_args = {}
    prior_statuses = {}
    bound_at = {}
    aliases = {}
    control_at = {}
    reused = set()
    control_snapshots = {}
    final_messages = {}

    def complete(full, kind, **details):
        trace.completed.add(full)
        trace.completion_evidence[full] = {'kind': kind, 'observed_bytes': offset, **details}

    def reset(full):
        trace.completed.discard(full)
        trace.completion_evidence.pop(full, None)

    def controlled_target(args):
        if not isinstance(args, dict):
            return None
        target = args.get('target', args.get('id', args.get('agent_id')))
        if not isinstance(target, str):
            return None
        return aliases.get(target, target if target.startswith('/') else scope + '/' + target)
    def problem(message):
        if not history:raise ScopeError(message)
        trace.issues.append(message)
    for number, line in enumerate(lines, 1):
        offset += len(physical_lines[number-1])
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as exc:
            raise ScopeError(f'原生日志第 {number} 行不完整或损坏：{exc}') from exc
        # Parse every original byte, including archived history. No sliced log.
        trace.last_ts = row.get('timestamp', trace.last_ts)
        if offset <= trace.inherited_history_bytes:
            # Ancestor calls are not this dispatcher's direct children. Their
            # original bytes and metadata stay in source_data and its digest.
            continue
        if row.get('type') != 'response_item':
            continue
        payload = row.get('payload', {})
        cid=payload.get('call_id')
        if offset <= start_after:
            if payload.get('type') in ('function_call','custom_tool_call'):
                prior_calls.add(cid)
                prior_pending[cid] = _name(payload)
                prior_args[cid] = _object(payload.get('arguments'))
            if payload.get('type') == 'function_call_output':
                value=_object(payload.get('output'))
                if prior_pending.get(cid) == 'spawn_agent' and isinstance(value,dict) and isinstance(value.get('task_name'),str):
                    prior_tasks.add(value['task_name'])
                    for key in ('task_name', 'agent_id', 'agent_name', 'id', 'nickname'):
                        alias = value.get(key)
                        if isinstance(alias, str) and alias:
                            prior_aliases.add(alias)
                    if value['task_name'].startswith(scope + '/'):
                        prior_aliases.add(value['task_name'][len(scope) + 1:])
                if prior_pending.get(cid) == 'list_agents' and isinstance(value,dict) and isinstance(value.get('agents'),list):
                    for agent in value['agents']:
                        if isinstance(agent,dict) and isinstance(agent.get('agent_name'),str) and agent['agent_name'].startswith(scope + '/'):
                            prior_names.add(agent['agent_name'])
                            prior_aliases.add(agent['agent_name'][len(scope)+1:])
                            for key in ('agent_name','agent_id','id','nickname'):
                                alias=agent.get(key)
                                if isinstance(alias,str) and alias:prior_aliases.add(alias)
                if prior_pending.get(cid) == 'list_agents' and isinstance(value,dict) and valid_agents(value.get('agents')) and full_list_args(prior_args.get(cid), scope):
                    prior_statuses = {}
                    for agent in value['agents']:
                        if isinstance(agent,dict) and isinstance(agent.get('agent_name'), str) and agent['agent_name'].startswith(scope + '/'):
                            prior_statuses[agent['agent_name']]=agent.get('agent_status')
            continue
        final = native_final_message(payload, scope)
        if final is not None:
            full = final['author']
            if full not in trace.handles or offset <= bound_at.get(full, offset):
                continue
            previous = final_messages.get(final['message_id'])
            if previous is not None:
                if previous != final:
                    problem('同一原生最终消息ID对应不同信封')
                continue
            final_messages[final['message_id']] = final
            if full in reused or full in trace.pending_controls.values():
                trace.rejected_final_messages.append({'task': full, 'message_id': final['message_id'],
                    'reason': '无法绑定到同句柄当前续作；需本次控制后新发起的completed状态观察'})
                continue
            value = trace.status.get(full)
            if full in trace.terminal_observations or value in ('interrupted', 'errored', 'idle', 'killed'):
                trace.rejected_final_messages.append({'task': full, 'message_id': final['message_id'],
                    'reason': '当前任务已有失败或终止状态，最终正文不能将其升级为成功'})
                continue
            complete(full, 'native_final_answer', **{k:v for k,v in final.items() if k != 'author'})
            continue
        if start_after and payload.get('type') in ('function_call_output','custom_tool_call_output') and cid in prior_calls:
            # The enrolling command is expected to finish just after its boundary.
            # Other historical tool calls cannot deliver late results into this run.
            from .join_attempt import enrollment_rows
            enrollments={p.get('call_id') for p,_,end,_ in enrollment_rows(raw) if end==start_after}
            if cid not in enrollments:raise ScopeError('历史调用在新尝试后才返回，必须先回收旧任务')
        if payload.get('type') == 'custom_tool_call' and _name(payload) == 'exec' and 'join_gate.py' in str(payload.get('input', '')):
            trace.gates += 1
        if payload.get('type')=='custom_tool_call' and _name(payload) in AGENT_OPERATIONS:
            problem('不支持此宿主代理控制/列举记录格式，禁止漏计句柄')
        if payload.get('type') == 'function_call':
            name = _name(payload)
            call_id = payload.get('call_id')
            if name in AGENT_OPERATIONS and (not isinstance(call_id,str) or not call_id or call_id in pending):
                problem('代理调用 ID 缺失或重复')
            pending[call_id] = name
            args=_object(payload.get('arguments'))
            pending_args[call_id]=args
            pending_offsets[call_id] = offset
            if start_after and name in AGENT_CONTROLS - {'spawn_agent'}:
                if not isinstance(args,dict):problem('代理控制参数无效，不能确认目标身份')
                if any(value in prior_aliases or any(
                        candidate == old or candidate.startswith(old + '/')
                        for candidate in (value, scope + '/' + value) for old in prior_tasks | prior_names)
                       for value in string_values(args)):
                    problem('当前尝试不能重新操作历史子任务')
            if name == 'spawn_agent':
                trace.spawns += 1
                trace.last_spawn_call = offset
                unresolved.add(call_id)
            elif name == 'wait_agent':
                trace.waits += 1
            elif name == 'list_agents':
                trace.lists += 1
            elif name in RESTART_CONTROLS | TERMINATING_CONTROLS:
                full = controlled_target(args)
                if full in trace.handles:
                    if full in trace.pending_controls.values():
                        problem('同一子任务存在尚未返回的控制调用，不能重叠续作或终止')
                    control_snapshots[call_id] = (full, full in trace.completed,
                        trace.completion_evidence.get(full), trace.status.get(full), control_at.get(full), full in reused)
                    trace.pending_controls[call_id] = full
                    control_at[full] = offset
                    if name in RESTART_CONTROLS:
                        reused.add(full)
                    reset(full)
                    trace.status[full] = 'control_pending'
            continue
        if payload.get('type') != 'function_call_output':
            continue
        call_id = payload.get('call_id')
        name = pending.get(call_id)
        if name in AGENT_OPERATIONS:
            if call_id in returned:
                problem('代理调用返回 ID 重复')
            returned.add(call_id)
        output = _object(payload.get('output'))
        if name == 'spawn_agent':
            trace.last_spawn_output = offset
            # The host rejects invalid names before creating an agent and returns
            # this exact plain-text message, rather than a JSON error envelope.
            # Preserve it as a failed request; do not invent a handle or rename
            # the request to match a differently named retry. Unknown text stays
            # unbound and is rejected by the existing path below.
            if payload.get('output') == 'agent_name must use only lowercase letters, digits, and underscores':
                output = {'error': payload['output']}
            if payload.get('output') in {'collab spawn failed: agent thread limit reached',
                                         'collab tool failed: agent thread limit reached'}:
                output={'error':payload['output']}
            task = output.get('task_name') if isinstance(output, dict) else None
            # Error responses are not successful handles. Ambiguous/missing output
            # is rejected rather than manufacturing a zero-handle success.
            if not isinstance(task, str):
                if isinstance(output,dict) and isinstance(output.get('error'),str) and output['error']:
                    requested = (pending_args.get(call_id) or {}).get('task_name')
                    if isinstance(requested, str) and not requested.startswith('/'):
                        requested = scope + '/' + requested
                    trace.failed_spawns.append({'call_id':call_id,'error':output['error'],'requested_task':requested});unresolved.discard(call_id)
                    continue
                problem('spawn_agent 没有可核验的真实 task_name 返回值')
                continue
            if task in prior_tasks | prior_names or task in trace.handles:
                problem('task_name 已在此前调用使用；须以尝试/轮次唯一化，禁止借用旧 completed')
            unresolved.discard(call_id)
            prefix = scope + '/'
            if task.startswith(prefix) and '/' not in task[len(prefix):] and task[len(prefix):]:
                trace.handles[task] = task[len(prefix):]
                bound_at[task] = offset
                aliases[task] = task
                aliases[task[len(prefix):]] = task
                for key in ('agent_id', 'id', 'nickname', 'agent_name'):
                    alias = output.get(key)
                    if isinstance(alias, str) and alias:
                        if alias in aliases and aliases[alias] != task:
                            problem('真实派发返回的代理别名冲突')
                        aliases[alias] = task
            else:problem('成功 spawn 返回的 task_name 不属于实际派发者，禁止以零句柄放行')
        elif name in RESTART_CONTROLS | TERMINATING_CONTROLS and call_id in control_snapshots:
            full, was_complete, proof, status, previous_control, was_reused = control_snapshots[call_id]
            trace.pending_controls.pop(call_id, None)
            failure = control_error(payload.get('output'))
            if failure:
                trace.failed_controls.append({'call_id': call_id, 'operation': name, 'task': full,
                                              'error': failure, 'requested_bytes': pending_offsets[call_id]})
                if was_complete:
                    trace.completed.add(full)
                    if proof is not None:
                        trace.completion_evidence[full] = proof
                if status is None:
                    trace.status.pop(full, None)
                else:
                    trace.status[full] = status
                if previous_control is None:
                    control_at.pop(full, None)
                else:
                    control_at[full] = previous_control
                if not was_reused:
                    reused.discard(full)
                continue
            control_at[full] = offset
            previous = output.get('previous_status') if isinstance(output, dict) else None
            verified_previous = (isinstance(previous, str) and previous in
                {'completed', 'running', 'interrupted', 'errored', 'idle', 'pending'} or
                isinstance(previous, dict) and set(previous) == {'completed'})
            if name in TERMINATING_CONTROLS and verified_previous:
                trace.successful_controls[(full, name)] = offset
                if previous == 'completed' or isinstance(previous, dict) and set(previous) == {'completed'}:
                    complete(full, 'control_previous_completed', call_id=call_id, operation=name)
                    trace.status[full] = {'completed': True}
                else:
                    trace.status[full] = 'killed' if name == 'close_agent' else 'interrupted'
                    trace.terminal_observations[full] = {'status': trace.status[full],
                        'call_id': call_id, 'operation': name, 'observed_bytes': offset}
            else:
                # No verified success response schema for restart operations is
                # currently available. Preserve this uncertainty instead of
                # treating an arbitrary non-error dictionary as a failed call
                # (which would restore stale completion) or a successful run.
                trace.unverified_controls.append({'call_id': call_id, 'operation': name, 'task': full,
                    'requested_bytes': pending_offsets[call_id], 'returned_bytes': offset,
                    'output_shape': sorted(output) if isinstance(output, dict) else type(output).__name__})
                reused.add(full)
                trace.status[full] = 'control_unverified'
        elif name == 'list_agents':
            agents = output.get('agents') if isinstance(output,dict) else None
            if not valid_agents(agents):
                trace.invalid_lists.append({'call_id':call_id,'reason':'list_agents 返回无效或损坏的 agents 列表','output_bytes':offset})
                trace.last_invalid_list_output = offset
                continue
            # Latest membership replaces stale running/interrupted observations.
            # Earlier completed observations remain separately authoritative.
            if full_list_args(pending_args.get(call_id,{}), scope):
                trace.status = {}
                trace.last_full_list_call = pending_offsets[call_id]
            had_status = False
            for agent in agents:
                full = agent['agent_name']
                value = agent.get('agent_status')
                if start_after and any(full==old or full.startswith(old+'/') for old in prior_tasks | prior_names):
                    if not stopped_status(value):raise ScopeError('历史子任务在当前尝试仍活跃，禁止混入新运行')
                    if full not in prior_statuses or value!=prior_statuses[full]:raise ScopeError('历史子任务的状态在新尝试发生变化，必须排查旧任务恢复')
                    continue
                if start_after and not unresolved and full.startswith(scope+'/') and '/' not in full[len(scope)+1:] and full not in trace.handles:
                    if not stopped_status(value):raise ScopeError('发现未绑定当前 spawn 的活跃直接子任务')
                if (full in trace.handles and (pending_offsets[call_id] <= control_at.get(full, -1)
                        or full in trace.pending_controls.values())):
                    continue
                trace.status[full] = value
                had_status = True
                if value in ('interrupted', 'errored', 'idle', 'killed'):
                    trace.terminal_observations[full] = {'status': value,
                        'call_id': call_id, 'operation': 'list_agents', 'observed_bytes': offset}
                if isinstance(value, dict) and 'completed' in value and set(value)!={'completed'}:
                    problem('completed 观测同时携带其他状态，身份不明确')
                if isinstance(value, dict) and set(value)=={'completed'}:
                    # A reused handle needs a fresh complete subtree listing;
                    # an older in-flight result cannot finish its new work.
                    if full not in reused or full_list_args(pending_args.get(call_id), scope):
                        complete(full, 'list_agents_completed', call_id=call_id)
                    else:
                        trace.status[full] = 'completion_requires_full_list'
                elif full in trace.completed:
                    reset(full)
            if had_status:
                trace.status_ts = row.get('timestamp', '')
    if unresolved:
        problem('原生日志含未绑定返回值的 spawn_agent，禁止以零句柄放行')
    if start_after:
        for full, value in trace.status.items():
            if full.startswith(scope+'/') and '/' not in full[len(scope)+1:] and full not in trace.handles and not stopped_status(value):
                problem('发现未绑定当前 spawn 的活跃直接子任务')
    return trace


def exempt(name):
    # Confirmed against the unchanged original CLI; not a configurable allowlist.
    return 'env-prewarm' in name or 'env_prewarm' in name


def unrecovered_spawns(trace):
    return [failure for failure in trace.failed_spawns if not (
        isinstance(failure.get('requested_task'), str) and failure['requested_task'] in trace.handles
        and failure['requested_task'] in trace.completed)]


def unrecovered_controls(trace):
    """A failed continuation is unfinished work, not a successful restart."""
    unresolved = unresolved_controls(trace)
    failures = []
    for failure in trace.failed_controls:
        task, operation = failure['task'], failure['operation']
        completions = [trace.successful_controls.get((task, operation), -1)] + [
            control['returned_bytes'] for control in trace.unverified_controls
            if control['task'] == task and control['operation'] == operation
            and control['requested_bytes'] > failure['requested_bytes'] and control not in unresolved]
        observed = trace.completion_evidence.get(task, {}).get('observed_bytes', -1)
        if task not in trace.completed or not any(
                failure['requested_bytes'] < returned <= observed for returned in completions):
            failures.append(failure)
    return failures


def unresolved_controls(trace):
    return [control for control in trace.unverified_controls if not (
        control['task'] in trace.completed
        and trace.completion_evidence.get(control['task'], {}).get('kind') == 'list_agents_completed'
        and trace.completion_evidence[control['task']]['observed_bytes'] > control['returned_bytes'])]


def contracts(project, point):
    result = []
    errors = []
    for path in sorted((project / 'spec/a2h/_work').glob('expected_*.json')):
        try:
            value = json.loads(path.read_text(encoding='utf-8'))
            if value.get('join_point') == point:
                if (not isinstance(value.get('task_names'),list) or
                        any(not isinstance(n,str) or not n for n in value['task_names']) or
                        not isinstance(value.get('artifacts',[]),list)):
                    raise ValueError('expected task_names/artifacts have invalid shape')
                result.append(value)
        except (ValueError, AttributeError) as exc:
            errors.append(f'契约文件损坏: {path}: {exc}')
    return result, errors


def artifact_gaps(project, name, expected, *, require_declaration=False):
    gaps = []
    declared = False
    for contract in expected:
        if not any(fnmatch.fnmatchcase(name, pattern) for pattern in contract.get('task_names', [])):
            continue
        for artifact in contract.get('artifacts', []):
            pattern = artifact['path']
            count = artifact.get('min_count', 1)
            size = artifact.get('min_bytes', 0)
            if (not isinstance(pattern,str) or not pattern or PurePosixPath(pattern).is_absolute()
                    or '..' in PurePosixPath(pattern).parts or '\\' in pattern or ':' in pattern
                    or type(count) is not int or count < 1 or type(size) is not int or size < 0):
                raise ScopeError('Invalid artifact path/count/size in expected contract')
            from .core import safe_child, MigrationError
            matches=[]
            for path in project.glob(pattern):
                try:
                    safe_child(project,path.relative_to(project).as_posix())
                except MigrationError as exc:
                    raise ScopeError(str(exc)) from exc
                if path.is_file() and path.stat().st_size >= size:
                    matches.append(path)
            declared = declared or any(not path.name.endswith('.done') for path in matches)
            prefix = f"[{contract['join_point']}] {pattern}"
            if len(matches) < count:
                gaps.append(f'{prefix}: 需≥{count} 个(≥{size}B)，实得 {len(matches)}')
            elif artifact.get('json'):
                for path in matches:
                    try:
                        json.loads(path.read_text(encoding='utf-8'))
                    except (ValueError, UnicodeError) as exc:
                        gaps.append(f'{prefix}: JSON 不可解析（{exc}）——可能读到半截，稍后重跑本闸')
    if require_declaration and not declared:
        gaps.append('原生最终消息/控制终态路径须有匹配且非空的expected-set产物声明；正文或.done文件不能单独证明完整交付')
    return gaps


def gate(trace, project, point, no_ledger=False, check_identity=True):
    project = Path(project)
    if check_identity:
        if not project.is_absolute() or not project.is_dir():
            raise ScopeError('--project 必须是有效的真实绝对项目路径')
        if not os.environ.get('CODEX_THREAD_ID') or trace.meta.get('id') != os.environ['CODEX_THREAD_ID']:
            raise ScopeError('原生日志 meta.id 与实际 CODEX_THREAD_ID 不一致')
    project = project.resolve(strict=True)
    if trace.attempt:
        history=trace.attempt['history_summary']
        print(f"attempt {trace.attempt['attempt_id']} | 历史审计 exit {history['exit_code']} / 未收口 {history['unjoined']}；历史失败保留")
    failures = unrecovered_spawns(trace)
    if failures:
        for failure in failures:
            print(f"⛔ 派发失败尚未补派完成：{failure.get('requested_task') or failure['call_id']} — {failure['error']}")
        return 1
    controls = unrecovered_controls(trace)
    if controls:
        for failure in controls:
            print(f"⛔ 代理控制失败尚未恢复：{failure['operation']} {failure['task']} — {failure['error']}")
        return 1
    if trace.pending_controls:
        print('⛔ 代理控制调用尚无真实返回，不能认定当前任务已停止或完成。')
        return 3
    if unresolved_controls(trace):
        print('⛔ 代理控制返回结构不可核验；需返回之后新发起的完整列表completed观察。')
        return 3
    if trace.last_invalid_list_output >= 0 and trace.last_full_list_call <= trace.last_invalid_list_output:
        print('⛔ 无法判定：列表调用失败或记录损坏，须重新调用完整 list_agents。')
        return 3
    if trace.attempt and trace.handles and trace.last_full_list_call <= trace.last_spawn_output:
        print('⛔ 无法判定：最后一次派发返回后缺少当前派发者子树的完整 list_agents 调用。')
        return 3
    expected, errors = contracts(project, point)
    requested=[name for contract in expected for name in contract['task_names']]
    if not trace.handles and requested:
        print('⛔ 预期任务没有真实 spawn 返回，禁止零句柄放行。')
        return 3
    if not trace.handles and errors:
        print('⛔ 预期产物合同损坏。')
        return 3
    if not trace.handles:
        print('✅ 本会话未派发任何子代理（直接子句柄=0），无需收口。')
        return 0
    if not trace.status and not trace.completed:
        print('⛔ 无法判定：没有可信completed或原生最终消息；先取得当前任务完成观察再重跑本闸。')
        return 3
    print(f'join_gate @ {point} | 句柄 {len(trace.handles)} | wait_agent 累计 {trace.waits} | 状态时点 {trace.status_ts}')
    joined, exemptions = [], []
    bad = False
    for full, name in trace.handles.items():
        if exempt(name):
            print(f'  ⏭  fire-and-forget   {name}（静态 allowlist）')
            exemptions.append(name)
        elif full in trace.completed:
            proof = trace.completion_evidence.get(full, {})
            gaps = artifact_gaps(project, name, expected,
                require_declaration=proof.get('kind') in {'native_final_answer', 'control_previous_completed'})
            if gaps:
                bad = True
                print(f'  ❌ COMPLETED-BUT-INCOMPLETE {name}（completed ≠ 验收，按条款②断点重派）')
                for gap in gaps:
                    print(f'       缺口: {gap}')
            else:
                print(f'  ✅ joined            {name}')
                joined.append(name)
        elif full not in trace.status:
            gaps = artifact_gaps(project, name, expected)
            bad = True
            if full in trace.terminal_observations:
                print(f"  ❌ OUTSTANDING       {name} — 已观察到 {trace.terminal_observations[full]['status']}，没有后续可信completed")
            else:
                print(f'  ❓ UNOBSERVED         {name} — 未观测到当前任务可信完成；文件存在不能代替完成信号')
            for gap in gaps:
                print(f'       契约缺口: {gap}')
        else:
            bad = True
            value = trace.status.get(full, 'UNOBSERVED')
            print(f'  ⏳ OUTSTANDING       {name} — 仍在 {value}')
    for error in errors:
        print(f'  ⚠️ {error}')
    if bad or errors:
        print('⛔ 收口未完成：OUTSTANDING → 继续 wait_agent 循环；INCOMPLETE → 条款②断点重派。禁止发完成报告/进下一阶段。')
        return 1
    if not no_ledger:
        ledger = project / 'spec/a2h/_work/join-ledger.jsonl'
        ledger.parent.mkdir(parents=True, exist_ok=True)
        row = {'ts': time.time(), 'join_point': point, 'joined': joined, 'exempt': exemptions,
               'rollouts': [trace.path.name], 'status_ts': trace.status_ts,
               'thread_id':trace.meta.get('id'),'agent_path':trace.scope,
               'source_sha256':trace.source_sha256,'source_bytes':trace.source_bytes,
               'completion_evidence':{name:trace.completion_evidence.get(trace.scope+'/'+name)
                                      for name in joined}}
        if trace.attempt:
            row.update(attempt_id=trace.attempt['attempt_id'],thread_id=trace.meta['id'],
                       start_bytes=trace.attempt['start_bytes'],prefix_sha256=trace.attempt['prefix_sha256'],
                       source_sha256=trace.source_sha256,source_bytes=trace.source_bytes)
        with ledger.open('a', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
        print('→ join-ledger 已记账。')
    return 0


def audit(traces, ledger=None):
    rows, handles = [], {}
    observed = set().union(*(trace.completed for trace in traces))
    for trace in traces:
        rows.append({'file': trace.path.name, 'cwd': trace.meta.get('cwd', ''),
                     'spawns': len(trace.handles), 'wait_agent': trace.waits,
                     'list_agents': trace.lists, 'spawn_agent': trace.spawns,
                     'join_gate': trace.gates, 'last_ts': trace.last_ts})
        print(f"— {trace.path.name}  cwd={trace.meta.get('cwd', '')}")
        print(f'    spawn={trace.spawns}(直接子句柄 {len(trace.handles)}) wait={trace.waits} list={trace.lists} join_gate={trace.gates}')
        for full, name in trace.handles.items():
            state = 'joined' if full in observed else 'fire-and-forget' if exempt(name) else 'UNJOINED'
            handles[full] = state
            print(f"  {'✅' if state == 'joined' else '⏭ ' if state == 'fire-and-forget' else '❌'} {state:16} {name}")
    joined = sum(state == 'joined' for state in handles.values())
    exemptions = sum(state == 'fire-and-forget' for state in handles.values())
    unjoined = len(handles) - joined - exemptions
    denom = len(handles) - exemptions
    rate = round(100 * joined / denom, 1) if denom else 0.0
    result = {'files': rows, 'handles': handles,
              'totals': {'spawns': len(handles), 'joined': joined, 'unjoined': unjoined,
                         'exempt': exemptions, 'recovery_rate_pct': rate}}
    print(f'\n条款①依从率(可信完成观察): {joined}/{denom} = {rate:.1f}%  (unjoined={unjoined}, exempt={exemptions})')
    fake = []
    if ledger:
        for line in Path(ledger).read_text(encoding='utf-8').splitlines():
            row = json.loads(line)
            attempted=[trace for trace in traces if trace.attempt]
            if attempted and not any(row.get('attempt_id')==t.attempt['attempt_id'] and row.get('thread_id')==t.meta['id']
                                     and row.get('start_bytes')==t.attempt['start_bytes'] and row.get('prefix_sha256')==t.attempt['prefix_sha256']
                                     for t in attempted):
                fake.append([row.get('join_point',''),'ATTEMPT_IDENTITY_MISMATCH'])
                continue
            snapshots={}
            bound_snapshot = attempted or any(key in row for key in ('source_bytes', 'source_sha256', 'completion_evidence'))
            if bound_snapshot:
                for trace in traces:
                    count=row.get('source_bytes')
                    start=trace.attempt['start_bytes'] if trace.attempt else 0
                    if type(count) is int and start <= count <= trace.source_bytes and hashlib.sha256(trace.source_data[:count]).hexdigest()==row.get('source_sha256'):
                        snapshots[trace.path]=read_trace(trace.path,raw=trace.source_data[:count],start_after=start)
                if not snapshots:
                    fake.append([row.get('join_point',''),'SOURCE_SNAPSHOT_MISMATCH'])
                    continue
            for name in row.get('joined', []):
                candidates = [trace for trace in traces if trace.path.name in row.get('rollouts', [])]
                if bound_snapshot:candidates=[snapshots[t.path] for t in candidates if t.path in snapshots]
                if not any(trace.scope + '/' + name in trace.completed for trace in candidates):
                    fake.append([row.get('join_point', ''), name])
                elif 'completion_evidence' in row and not any(
                        row.get('completion_evidence',{}).get(name) == trace.completion_evidence.get(trace.scope+'/'+name)
                        for trace in candidates):
                    fake.append([row.get('join_point', ''), name + ':COMPLETION_EVIDENCE_MISMATCH'])
        if fake:
            result['ledger_fake'] = fake
            print('⛔ ledger 防伪失败（当前原始字节快照没有对应可信完成观察）：')
            for point, name in fake:
                print(f'    [{point}] {name}')
    # Added evidence identity is audit-only; never a substitute for join observations.
    result['source_evidence'] = [{'path': str(trace.path), 'thread_id': trace.meta.get('id'),
                                  'agent_path': trace.scope, 'metadata_cwd': trace.meta.get('cwd'),
                                  'sha256': trace.source_sha256, 'read_bytes': trace.source_bytes} for trace in traces]
    for evidence,trace in zip(result['source_evidence'],traces):
        if trace.attempt:evidence['attempt']=trace.attempt
        if trace.failed_spawns:evidence['failed_spawns']=trace.failed_spawns
        if trace.invalid_lists:evidence['invalid_lists']=trace.invalid_lists
        if trace.issues:evidence['historical_issues']=trace.issues
        if trace.completion_evidence:evidence['completion_evidence']=trace.completion_evidence
        if trace.failed_controls:evidence['failed_controls']=trace.failed_controls
        if trace.unverified_controls:evidence['unverified_controls']=trace.unverified_controls
        if trace.pending_controls:evidence['pending_controls']=trace.pending_controls
        if trace.rejected_final_messages:evidence['rejected_final_messages']=trace.rejected_final_messages
        if trace.terminal_observations:evidence['terminal_observations']=trace.terminal_observations
        if trace.inherited_history_bytes:evidence['inherited_history_bytes']=trace.inherited_history_bytes
    return result, 1 if unjoined or fake or any(t.issues or unrecovered_spawns(t) or unrecovered_controls(t) or unresolved_controls(t) or t.pending_controls or
        t.last_invalid_list_output >= 0 and t.last_full_list_call <= t.last_invalid_list_output for t in traces) else 0


def maybe_main(command, argv):
    """Bind live callers to their own log; keep offline root oracle delegation."""
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'): stream.reconfigure(encoding='utf-8')
    if command == 'join_gate':
        parser = argparse.ArgumentParser()
        parser.add_argument('--project', default='.')
        parser.add_argument('--join-point', default='FINAL')
        parser.add_argument('--rollout')
        parser.add_argument('--window-hours', type=float, default=24)
        parser.add_argument('--no-ledger', action='store_true')
        if '--help' in argv or '-h' in argv:
            return None
        args = parser.parse_args(argv)
        try:
            native = current_rollout()
            if native is None and (Path(args.project)/'.migbot/join-attempt.json').exists():
                raise ScopeError('已有实际宿主尝试但 CODEX_THREAD_ID 缺失，禁止退回目录混计')
            if native is not None:
                running_scope = caller(_meta(native))
                if running_scope != '/root' and not args.rollout:
                    raise ScopeError('内部子任务须显式传自身完整原生日志 --rollout')
                if args.rollout and Path(args.rollout).resolve(strict=True) != native:
                    raise ScopeError('传入的日志不属于实际 CODEX_THREAD_ID 的宿主原始文件，禁止复制或分流到其他会话')
                project=Path(args.project)
                if running_scope == '/root': project=project.resolve(strict=True)
                from .join_attempt import scoped_trace
                return gate(scoped_trace(project,native),project,args.join_point,args.no_ledger)
            if not args.rollout:
                return None
            if not is_nested(args.rollout):
                return None
            return gate(read_trace(args.rollout), Path(args.project), args.join_point, args.no_ledger)
        except (ScopeError, OSError, ValueError, TypeError, KeyError) as exc:
            print(f'⛔ 无法判定：{exc}')
            return 3
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+')
    parser.add_argument('--json', dest='json_out')
    parser.add_argument('--ledger')
    parser.add_argument('--project',default='.')
    if not argv or '--help' in argv or '-h' in argv:
        return None
    args = parser.parse_args(argv)
    try:
        native=current_rollout()
        if native is None and (Path(args.project)/'.migbot/join-attempt.json').exists():
            raise ScopeError('已有实际宿主尝试但 CODEX_THREAD_ID 缺失')
        if native is not None:
            if len(args.paths)!=1 or Path(args.paths[0]).resolve(strict=True)!=native:
                raise ScopeError('当前宿主审计只接受实际 CODEX_THREAD_ID 的完整原始文件；其他会话应单独审计')
            from .join_attempt import scoped_trace
            result,code=audit([scoped_trace(args.project,native)],args.ledger)
            if args.json_out:
                Path(args.json_out).write_text(json.dumps(result,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
            return code
        if not any(is_nested(path) for path in args.paths):
            return None
        traces = [read_trace(path) for path in args.paths]
        result, code = audit(traces, args.ledger)
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
            print(f'→ {args.json_out}')
        return code
    except (ScopeError, OSError, ValueError, TypeError, KeyError) as exc:
        print(f'⛔ 无法判定：{exc}')
        return 3
