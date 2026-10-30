"""Audited scope projection for the original depth-two-only join consumer.

Only real spawn results and tool status observations are projected. The original
gate owns normal joins and its ledger; verified exemptions additionally need the
dispatcher's actual artifacts. Agent prose is never a completion observation.
"""
from __future__ import annotations

import argparse
import copy
import fnmatch
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

from .core import MigrationError, atomic_write, digest, json_bytes, read_json, safe_child, write_json

TOOLS = {'spawn_agent', 'list_agents', 'followup_task', 'interrupt_agent'}
TASK = re.compile(r'[A-Za-z0-9_-]+')
AGENT = re.compile(r'/root(?:/[A-Za-z0-9_-]+)*')


def _record_bytes(row):
    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def _object(value, label):
    try:
        result = json.loads(value) if isinstance(value, str) else value
    except (ValueError, TypeError) as exc:
        raise MigrationError('Invalid structured ' + label) from exc
    if not isinstance(result, dict):
        raise MigrationError('Expected structured object for ' + label)
    return result


def _status(value):
    if isinstance(value, dict):
        value = next(iter(value)) if len(value) == 1 else 'unknown'
    known = {'completed', 'running', 'pending', 'failed', 'dead', 'stopped',
             'terminated', 'error', 'cancelled', 'interrupted'}
    return value if isinstance(value, str) and value in known else 'unknown'


def project_rollout(raw, source_path, expected):
    """Return a derived JSONL view plus private-body-free provenance metadata."""
    patterns = expected.get('task_names')
    if (not isinstance(patterns, list) or not patterns
            or any(not isinstance(p, str) or not re.fullmatch(r'[A-Za-z0-9_*?\[\]-]+', p) for p in patterns)):
        raise MigrationError('Verified join projection requires nonempty expected task-name patterns')
    rows = []
    for line, data in enumerate(raw.splitlines(), 1):
        if not data.strip():
            continue
        try:
            row = json.loads(data)
        except (ValueError, UnicodeError) as exc:
            raise MigrationError('Invalid rollout JSON at line ' + str(line)) from exc
        if not isinstance(row, dict) or row.get('type') == 'hmigbot_join_projection':
            raise MigrationError('A derived projection cannot be reused as the source rollout')
        rows.append((line, row, digest(data)))
    metadata = next(((n, r.get('payload', {}), sha) for n, r, sha in rows if r.get('type') == 'session_meta'), None)
    if not metadata or not isinstance(metadata[1], dict):
        raise MigrationError('Rollout needs its original writer session metadata')
    writer_line, meta, writer_sha = metadata
    source = meta.get('source', {})
    subagent = source.get('subagent', {}) if isinstance(source, dict) else {}
    spawned = subagent.get('thread_spawn', {}) if isinstance(subagent, dict) else {}
    if not isinstance(spawned, dict):
        raise MigrationError('Invalid rollout writer spawn metadata')
    if isinstance(source, dict) and 'subagent' in source and not (meta.get('agent_path') or spawned.get('agent_path')):
        raise MigrationError('Subagent rollout has no verifiable writer agent path')
    writer = meta.get('agent_path') or spawned.get('agent_path') or '/root'
    if (not isinstance(writer, str) or not AGENT.fullmatch(writer)
            or meta.get('agent_path') and spawned.get('agent_path') and meta['agent_path'] != spawned['agent_path']):
        raise MigrationError('Ambiguous rollout writer agent path')
    source_sha = digest(raw)
    calls, handles, projected, record_refs = {}, {}, {}, {}
    ignored_failed_spawns = []

    def include(call, output_entry, output):
        output_line, output_row, output_sha = output_entry
        for line, row, sha, replacement in (
                (*call['entry'], None), (output_line, output_row, output_sha, output)):
            result = copy.deepcopy(row)
            if replacement is not None:
                result['payload']['output'] = json.dumps(replacement, ensure_ascii=False, separators=(',', ':'))
            result['hmigbot_join_source'] = {'source_sha256': source_sha, 'line': line, 'line_sha256': sha}
            projected[line] = result
            record_refs[line] = {'source_line': line, 'source_line_sha256': sha,
                                 'call_id': call['id'], 'tool': call['tool'],
                                 'projected_record_sha256': digest(_record_bytes(result))}

    def observe(handle, kind, value, call, line):
        status = _status(value)
        item = {'kind': kind, 'status': status, 'call_id': call['id'], 'source_line': line,
                'status_origin': 'tool-status' if kind == 'list_agents' else 'work-reopened-by-tool-call',
                'original_status_sha256': digest(json_bytes(value)) if kind == 'list_agents' else None}
        handle['observations'].append(item)
        handle.update(status=status, observation_call_id=call['id'], observation_source_line=line,
                      original_status_sha256=item['original_status_sha256'])

    for entry in rows:
        line, row, _ = entry
        payload = row.get('payload', {})
        if row.get('type') != 'response_item' or not isinstance(payload, dict):
            continue
        kind = payload.get('type')
        if kind in {'function_call', 'custom_tool_call'}:
            tool = str(payload.get('name', '')).split('.')[-1]
            if tool not in TOOLS:
                continue
            ident = payload.get('call_id')
            if not isinstance(ident, str) or not ident or ident in calls:
                raise MigrationError('Missing or duplicate join tool call ID')
            calls[ident] = {'id': ident, 'tool': tool, 'entry': entry,
                            'arguments': _object(payload.get('arguments', payload.get('input', '{}')), tool + ' arguments')}
            if tool in {'followup_task', 'interrupt_agent'}:
                target = calls[ident]['arguments'].get('target')
                name = target if isinstance(target, str) and target.startswith('/') else writer + '/' + str(target)
                if name in handles:
                    # The call itself reopens certainty even while its output
                    # is pending. A later actual observation must close it.
                    observe(handles[name], tool, 'running' if tool == 'followup_task' else 'unknown', calls[ident], line)
                    result = copy.deepcopy(row)
                    result['hmigbot_join_source'] = {'source_sha256': source_sha, 'line': line, 'line_sha256': entry[2]}
                    projected[line] = result
                    record_refs[line] = {'source_line': line, 'source_line_sha256': entry[2], 'call_id': ident,
                                         'tool': tool, 'projected_record_sha256': digest(_record_bytes(result))}
            continue
        if kind not in {'function_call_output', 'custom_tool_call_output'}:
            continue
        call = calls.get(payload.get('call_id'))
        if not call:
            continue
        if call.get('output_line'):
            raise MigrationError('Duplicate join tool output for ' + call['id'])
        call['output_line'] = line
        args, tool = call['arguments'], call['tool']
        if tool == 'spawn_agent':
            task = args.get('task_name')
            if not isinstance(task, str) or not any(fnmatch.fnmatchcase(task, p) for p in patterns):
                continue
            spawn_output = payload.get('output', payload.get('content'))
            # These exact host-tool failures contain no agent handle. A real
            # retry still needs its own structured spawn and tool completion;
            # every other malformed output remains a hard parse failure.
            if spawn_output in ('collab spawn failed: agent thread limit reached',
                                'collab tool failed: agent thread limit reached'):
                ignored_failed_spawns.append({'task_name': task, 'call_id': call['id'],
                    'error_kind': 'agent_thread_limit_reached',
                    'spawn_source_line': call['entry'][0], 'spawn_source_line_sha256': call['entry'][2],
                    'output_source_line': line, 'output_source_line_sha256': entry[2],
                    'output_sha256': digest(spawn_output.encode('utf-8'))})
                continue
            output = _object(spawn_output, 'spawn result')
            name = output.get('task_name')
            if not TASK.fullmatch(task) or name != writer + '/' + task:
                continue  # An inherited/other writer's spawn cannot satisfy this expected set.
            if name in handles:
                raise MigrationError('Multiple real spawns share an expected agent identity: ' + task)
            alias = '/root/' + task
            handles[name] = {'task_name': task, 'role': args.get('agent_type'), 'source_name': name,
                'projected_name': alias, 'spawn_call_id': call['id'], 'spawn_source_line': call['entry'][0],
                'spawn_output_source_line': line, 'status': 'unknown', 'observations': []}
            projected_output = {**output, 'task_name': alias}
            include(call, entry, projected_output)
        elif tool == 'list_agents' and handles:
            output = _object(payload.get('output', payload.get('content')), 'agent observation')
            agents = output.get('agents')
            if not isinstance(agents, list):
                raise MigrationError('Agent observation has no structured agents array')
            selected, seen = [], set()
            for agent in agents:
                if not isinstance(agent, dict) or agent.get('agent_name') not in handles:
                    continue
                name = agent['agent_name']
                if name in seen:
                    raise MigrationError('Duplicate agent identity in a status observation')
                seen.add(name)
                observe(handles[name], 'list_agents', agent.get('agent_status'), call, line)
                selected.append({**agent, 'agent_name': handles[name]['projected_name']})
            if selected:
                include(call, entry, {**output, 'agents': selected})
        elif tool in {'followup_task', 'interrupt_agent'} and handles:
            target = args.get('target')
            name = target if isinstance(target, str) and target.startswith('/') else writer + '/' + str(target)
            if name in handles:
                include(call, entry, None)
    missing = [p for p in patterns if not any(fnmatch.fnmatchcase(h['task_name'], p) for h in handles.values())]
    unknown = any(h['status'] not in {'completed', 'running', 'pending', 'failed', 'dead', 'stopped',
                                    'terminated', 'error', 'cancelled', 'interrupted'} for h in handles.values())
    code = 3 if missing or not handles or unknown else 1 if any(h['status'] != 'completed' for h in handles.values()) else 0
    header = {'type': 'hmigbot_join_projection', 'schema_version': 1, 'derived': True,
              'source_path': str(source_path), 'source_sha256': source_sha, 'source_bytes': len(raw),
              'mapping': 'expected direct children rebased to the original depth-two consumer'}
    projection = b''.join(_record_bytes(r) + b'\n'
                          for r in [header, *(projected[n] for n in sorted(projected))])
    manifest = {**header, 'writer': {'session_id': meta.get('id'), 'agent_path': writer,
                'source_line': writer_line, 'source_line_sha256': writer_sha},
                'expected_task_patterns': patterns, 'unmatched_patterns': missing,
                'ignored_failed_spawns': ignored_failed_spawns,
                'handles': list(handles.values()), 'records': [record_refs[n] for n in sorted(record_refs)],
                'preflight_exit_code': code, 'projection_sha256': digest(projection)}
    return projection, manifest, code


def _exempt_verdicts(before, after, manifest, join_point, projection_path):
    """Consume only this call's single append-only upstream ledger decision."""
    if (not after.startswith(before) or len(after) == len(before)
            or before and not before.endswith(b'\n')):
        raise MigrationError('Exemption needs a new append-only original ledger record')
    lines = [line for line in after[len(before):].splitlines() if line.strip()]
    if len(lines) != 1:
        raise MigrationError('Exemption needs one unambiguous new original ledger decision')
    record = _object(lines[0].decode('utf-8'), 'original ledger record')
    rollout = f"join-{join_point}-{manifest['source_sha256']}.log"
    if (record.get('join_point') != join_point or projection_path.name != rollout
            or record.get('rollouts') != [rollout]):
        raise MigrationError('Original exemption ledger has a different join point or source projection')
    verdicts = {}
    for verdict in ('joined', 'exempt'):
        names = record.get(verdict)
        if not isinstance(names, list) or any(not isinstance(name, str) or not TASK.fullmatch(name) for name in names):
            raise MigrationError('Original ledger verdict must list exact task identities')
        for name in names:
            if name in verdicts:
                raise MigrationError('Duplicate original ledger task verdict: ' + name)
            verdicts[name] = verdict
    if set(verdicts) != {h['task_name'] for h in manifest['handles']} or 'exempt' not in verdicts.values():
        raise MigrationError('Original exemption ledger does not exactly cover the expected handles')
    return [{'task_name': h['task_name'], 'verdict': verdicts[h['task_name']],
             'authority': 'new-original-ledger'} for h in manifest['handles']]


def _exempt_artifacts(project, expected):
    """Check the existing path/count/bytes/JSON contract only for new exemptions."""
    artifacts = expected.get('artifacts')
    if not isinstance(artifacts, list) or not artifacts:
        raise MigrationError('Verified exemption requires a nonempty expected artifact contract')
    reports = []
    for artifact in artifacts:
        if not isinstance(artifact, dict) or set(artifact) - {'path', 'count', 'min_count', 'min_bytes', 'json'}:
            raise MigrationError('Unsupported expected artifact contract')
        pattern = artifact.get('path')
        if not isinstance(pattern, str) or not pattern:
            raise MigrationError('Expected artifact needs a project-relative path or glob')
        # Validate the portable path shape before globbing; validate every real
        # match again after resolution, including links and directory junctions.
        safe_child(project, re.sub(r'[*?\[\]]', '_', pattern))
        minimum = artifact.get('min_count', 1)
        size = artifact.get('min_bytes', 0)
        exact = artifact.get('count')
        if (type(minimum) is not int or minimum < 1 or type(size) is not int or size < 0
                or 'count' in artifact and (type(exact) is not int or exact < minimum)
                or type(artifact.get('json', False)) is not bool):
            raise MigrationError('Invalid expected artifact count, byte limit or JSON flag type')
        files = []
        for match in sorted(project.glob(pattern)):
            path = safe_child(project, match.relative_to(project).as_posix())
            if not path.is_file():
                continue
            raw = path.read_bytes()
            if len(raw) < size:
                raise MigrationError('Expected artifact is undersized: ' + match.relative_to(project).as_posix())
            if artifact.get('json', False):
                read_json(path)
            files.append({'path': match.relative_to(project).as_posix(), 'bytes': len(raw), 'sha256': digest(raw)})
        if len(files) < minimum or exact is not None and len(files) != exact:
            raise MigrationError('Expected artifact file count is not satisfied: ' + pattern)
        reports.append({'pattern': pattern, 'files': files})
    return reports


def main(argv=None, *, helper=None, root=None):
    parser = argparse.ArgumentParser(description='Verified source-rollout scope adapter for the original join gate')
    parser.add_argument('--project', default='.')
    parser.add_argument('--join-point', required=True)
    parser.add_argument('--rollout')
    parser.add_argument('--window-hours', type=float, default=48)
    parser.add_argument('--no-ledger', action='store_true')
    args = parser.parse_args(argv)
    root = Path(root or Path(__file__).resolve().parents[2])
    helper = Path(helper or root / 'vendor/hmigbot/skills/a2h-join/scripts/join_gate.py')
    try:
        if not TASK.fullmatch(args.join_point):
            raise MigrationError('Unsafe join point name')
        if not args.rollout:
            raise MigrationError('Explicit current-writer --rollout is required; no other sessions will be scanned')
        project = Path(args.project).resolve()
        if (project / 'spec/execution/execution-contract.json').exists():
            raise MigrationError('Indexed execution uses the native host join; legacy projected rollout cannot gate this run')
        source = Path(args.rollout).resolve()
        expected_path = safe_child(project, f'spec/a2h/_work/expected_{args.join_point}.json')
        expected = read_json(expected_path)
        if not isinstance(expected, dict):
            raise MigrationError('Expected-set contract must be a structured object')
        if expected.get('join_point') != args.join_point:
            raise MigrationError('Expected-set join point differs from the requested join point')
        projection, manifest, code = project_rollout(source.read_bytes(), source, expected)
        sha = manifest['source_sha256']
        projection_path = safe_child(project, f'spec/reports/host-oracle/support/join-{args.join_point}-{sha}.log')
        audit_path = safe_child(project, f'spec/reports/derived/a2h-join/{args.join_point}/{sha}.json')
        atomic_write(projection_path, projection)
        system = {'Windows': 'windows', 'Darwin': 'macos', 'Linux': 'linux'}[platform.system()]
        arch = 'arm64' if platform.machine().lower() in {'arm64', 'aarch64'} else 'x64'
        binary = helper.parent / f'bin/{system}-{arch}/_entry.dist' / ('_entry.exe' if system == 'windows' else '_entry.bin')
        commit = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], capture_output=True, timeout=10)
        dirty = subprocess.run(['git', '-C', str(root), 'status', '--porcelain'], capture_output=True, timeout=10)
        manifest.update(projection_path=str(projection_path), expected_path=str(expected_path),
                        expected_sha256=digest(expected_path.read_bytes()),
                        tool_repo_commit=commit.stdout.decode().strip() if commit.returncode == 0 else None,
                        tool_repo_dirty=bool(dirty.stdout) if dirty.returncode == 0 else None,
                        adapter_sha256=digest(Path(__file__).read_bytes()),
                        wrapper_sha256=digest((root / 'skills/a2h-join/scripts/join_gate.py').read_bytes()),
                        original_helper_path=str(helper), original_helper_sha256=digest(helper.read_bytes()),
                        original_binary_path=str(binary), original_binary_sha256=digest(binary.read_bytes()))
        if not code:
            original_args = [sys.executable, str(helper), '--project', str(project), '--join-point', args.join_point,
                             '--rollout', str(projection_path), '--window-hours', str(args.window_hours)]
            if args.no_ledger:
                original_args.append('--no-ledger')
            ledger_path = None if args.no_ledger else safe_child(project, 'spec/a2h/_work/join-ledger.jsonl')
            ledger_before = ledger_path.read_bytes() if ledger_path and ledger_path.exists() else b''
            from .runtime_timeouts import timeout_for
            from .process_runtime import run as run_owned_process
            env = {**os.environ, 'PYTHONUTF8': '1'}
            limit = timeout_for('join', env=env)
            if os.name == 'nt':
                result = run_owned_process(original_args, cwd=project, env=env, timeout=limit)
            else:
                from .portable_helper import run
                result = run(helper, original_args[2:], cwd=project, capture_output=True, timeout=limit, env=env)
            stdout, stderr = result.stdout.decode('utf-8', 'replace'), result.stderr.decode('utf-8', 'replace')
            count = re.search(r'句柄\s+(\d+)', stdout)
            recognized = int(count.group(1)) if count else 0
            code = result.returncode
            manifest['original_gate'] = {'exit_code': result.returncode, 'recognized_handles': recognized,
                'stdout': stdout, 'stderr': stderr, 'argv': getattr(result, 'args', original_args), 'requested_argv': original_args}
            if code == 0:
                if recognized != len(manifest['handles']):
                    code = 3
                elif any(not re.search(r'joined\s+' + re.escape(h['task_name']) + r'(?:\s|$)', stdout)
                         for h in manifest['handles']):
                    try:
                        if ledger_path is None:
                            raise MigrationError('Exemption has no authoritative original ledger in --no-ledger mode')
                        after = ledger_path.read_bytes() if ledger_path.exists() else b''
                        manifest['original_gate']['ledger'] = {'path': str(ledger_path),
                            'before_sha256': digest(ledger_before), 'after_sha256': digest(after)}
                        verdicts = _exempt_verdicts(ledger_before, after, manifest, args.join_point, projection_path)
                        manifest['original_gate']['verdicts'] = verdicts
                        if (read_json(expected_path) != expected
                                or digest(expected_path.read_bytes()) != manifest['expected_sha256']
                                or digest(projection_path.read_bytes()) != manifest['projection_sha256']):
                            raise MigrationError('Expected contract or source projection changed during original join')
                        manifest['exempt_artifacts'] = _exempt_artifacts(project, expected)
                        manifest['join_status'] = ('exempt' if all(v['verdict'] == 'exempt' for v in verdicts)
                                                   else 'joined-with-exempt')
                    except (MigrationError, OSError, ValueError) as exc:
                        code = 3
                        manifest['original_gate']['verification_error'] = str(exc)
        else:
            manifest['original_gate'] = {'invoked': False}
        manifest['exit_code'] = code
        write_json(audit_path, manifest)
        print(json.dumps({'status': manifest.get('join_status', 'joined') if code == 0 else 'rejected', 'exit_code': code,
            'source_sha256': sha, 'handle_count': len(manifest['handles']),
            'handles': [{'task_name': h['task_name'], 'status': h['status']} for h in manifest['handles']],
            'audit_path': str(audit_path), 'projection_sha256': manifest['projection_sha256']}, ensure_ascii=False))
        return code
    except (MigrationError, OSError, ValueError, subprocess.SubprocessError) as exc:
        failure = {'status': 'unverified', 'exit_code': 3, 'error': str(exc)}
        if isinstance(exc, subprocess.TimeoutExpired):
            from .runtime_timeouts import timeout_evidence
            failure['process_output'] = timeout_evidence(exc)
        print(json.dumps(failure, ensure_ascii=False))
        return 3

