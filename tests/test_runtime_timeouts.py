"""Short execution guards: no application conversion, scale probe or 60-second waits."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from hmigbot_ios import ios_scheduler, native_helpers, native_literal_scope
from hmigbot_ios import native_pipeline_runtime, native_pipeline_semantics, windows_scheduler_runtime
from hmigbot_ios.core import MigrationError, read_json
from hmigbot_ios.runtime_timeouts import DEFAULTS, DEADLINE, VARIABLES, timeout_for
from hmigbot_ios.scheduler_windows_runtime import run as owned_run


@pytest.fixture(autouse=True)
def clean_policy(monkeypatch):
    for name in [*VARIABLES.values(), DEADLINE]:
        monkeypatch.delenv(name, raising=False)


def test_defaults_and_explicit_stage_caps():
    assert {stage: timeout_for(stage, env={}) for stage in DEFAULTS} == DEFAULTS
    assert timeout_for('scheduler', env={VARIABLES['scheduler']: '900'}) == 900
    assert timeout_for('literal', env={VARIABLES['literal']: '0.125'}) == 0.125
    assert timeout_for('structural', env={}, default=None) is None


@pytest.mark.parametrize('value', ['', '0', '-1', 'nan', 'inf', '-inf', 'true', 'oops', '604801'])
def test_invalid_stage_values_are_explicitly_rejected(value):
    with pytest.raises(MigrationError, match='HMIGBOT_SCHEDULER_TIMEOUT_SECONDS'):
        timeout_for('scheduler', env={VARIABLES['scheduler']: value})


@pytest.mark.parametrize('value', ['', '0', '-1', 'nan', 'inf', 'oops', '1e300'])
def test_invalid_deadlines_are_explicitly_rejected(value):
    with pytest.raises(MigrationError, match=DEADLINE):
        timeout_for('scheduler', env={DEADLINE: value})


def test_absolute_deadline_is_shared_and_never_reset_per_stage():
    env = {DEADLINE: '1010', VARIABLES['scheduler']: '900', VARIABLES['structural']: '1800'}
    assert timeout_for('scheduler', env=env, now=1000) == 10
    assert timeout_for('structural', env=env, now=1007) == 3
    assert timeout_for('helper', env=env, now=1009) == 1
    with pytest.raises(subprocess.TimeoutExpired) as raised:
        timeout_for('literal', env=env, now=1010)
    assert raised.value.ios_timeout_policy['process_started'] is False


def fake_staging(monkeypatch, module, tmp_path):
    @contextmanager
    def directory(*args, **kwargs):
        yield str(tmp_path)
    monkeypatch.setattr(ios_scheduler, '_runtime_directory', directory)
    def copy(source, destination, *args, **kwargs):
        Path(destination).mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(module.shutil, 'copytree', copy)
    if module is windows_scheduler_runtime:
        monkeypatch.setattr(module, 'stage_base_python', lambda *args: None)
    else:
        monkeypatch.setattr('hmigbot_ios.windows_python_runtime.stage_base_python', lambda *args: None)


@pytest.mark.skipif(os.name != 'nt', reason='Windows owned scheduler bridge')
@pytest.mark.parametrize('adapter', [False, True])
def test_both_scheduler_entrypoints_consume_override(tmp_path, monkeypatch, adapter):
    module = windows_scheduler_runtime if adapter else ios_scheduler
    fake_staging(monkeypatch, module, tmp_path / 'runtime')
    monkeypatch.setenv(VARIABLES['scheduler'], '901')
    calls = []
    def execute(command, **kwargs):
        calls.append(kwargs)
        return subprocess.CompletedProcess(command, 0, b'{"action":"wait"}', b'')
    if adapter:
        monkeypatch.setattr(module, 'run_owned_process', execute)
    else:
        monkeypatch.setattr('hmigbot_ios.scheduler_windows_runtime.run', execute)
    result = module.invoke(tmp_path, 'next_batch', [])
    assert result['action'] == 'wait'
    assert calls[0]['timeout'] == 901


def test_pipeline_override_and_deadline_reach_nested_environment(tmp_path, monkeypatch):
    monkeypatch.setenv(VARIABLES['structural'], '1801')
    monkeypatch.setenv(DEADLINE, '1010')
    monkeypatch.setattr('hmigbot_ios.runtime_timeouts.time.time', lambda: 1000)
    @contextmanager
    def layout(**kwargs):
        yield tmp_path / 'engine', os.environ.copy()
    monkeypatch.setattr(native_pipeline_runtime, 'runtime_layout', layout)
    calls = []
    def execute(command, **kwargs):
        calls.append(kwargs)
        assert timeout_for('literal', env=kwargs['env'], now=1007) == 3
        return subprocess.CompletedProcess(command, 0, b'output', b'')
    if os.name == 'nt':
        monkeypatch.setattr(native_pipeline_runtime, 'run_owned_process', execute)
    else:
        monkeypatch.setattr(native_pipeline_runtime.subprocess, 'run', execute)
    result = native_pipeline_runtime._invoke_raw(['finalize', '--project-root', str(tmp_path)])
    assert result.returncode == 0
    assert calls[0]['timeout'] == 10
    assert calls[0]['env'][DEADLINE] == '1010'


@pytest.mark.skipif(os.name != 'nt', reason='Windows direct literal/helper consumers')
def test_literal_and_helper_consume_distinct_phase_values(tmp_path, monkeypatch):
    monkeypatch.setenv(VARIABLES['literal'], '601')
    monkeypatch.setenv(VARIABLES['helper'], '602')
    calls = []
    def execute(command, **kwargs):
        calls.append(kwargs['timeout'])
        return subprocess.CompletedProcess(command, 0, b'{}', b'')
    monkeypatch.setattr(native_literal_scope, 'run_owned_process', execute)
    native_literal_scope._original(tmp_path, tmp_path / 'literal.json')
    monkeypatch.setattr(native_helpers, 'run_owned_process', execute)
    native_helpers.original('arkts-structural-closure', 'loop_runner.py', [])
    assert calls == [601, 602]


def test_literal_timeout_replaces_stale_success_and_preserves_partial_output(tmp_path, monkeypatch, capsys):
    output = tmp_path / 'literal.json'
    output.write_text('{"passed":true}')
    error = subprocess.TimeoutExpired(['fixture'], 0.01, output=b'new stdout', stderr=b'new stderr')
    error.ios_process_tree = {'job_terminated': True}
    def fail(*args):
        raise error
    monkeypatch.setattr(native_literal_scope, 'audit', fail)
    assert native_literal_scope.main(['--project', str(tmp_path), '--output-json', str(output)]) == 1
    result = read_json(output)
    assert result['passed'] is False
    assert result['process_output']['stdout'] == 'new stdout'
    assert result['process_output']['stderr'] == 'new stderr'
    assert result['process_output']['process_tree']['job_terminated'] is True
    capsys.readouterr()


@pytest.mark.skipif(os.name != 'nt', reason='Windows assembly subprocess')
def test_assembly_override_and_timeout_do_not_adapt_stale_success(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv(VARIABLES['assembly'], '603')
    output = tmp_path / 'assembly.json'
    output.write_text('{"passed":true}')
    calls = []
    def fail(command, **kwargs):
        calls.append(kwargs['timeout'])
        raise subprocess.TimeoutExpired(command, kwargs['timeout'], output=b'partial assembly')
    monkeypatch.setattr('hmigbot_ios.scheduler_windows_runtime.run', fail)
    assert native_pipeline_semantics.assembly_main(['--project-root', str(tmp_path), '--output-json', str(output)]) == 124
    assert calls == [603]
    assert read_json(output)['passed'] is False
    assert read_json(output)['process_output']['stdout'] == 'partial assembly'
    capsys.readouterr()


@pytest.mark.skipif(os.name != 'nt', reason='Windows original join consumer')
def test_join_gate_entrypoint_consumes_join_override(tmp_path, monkeypatch, capsys):
    from hmigbot_ios import join_rollout
    monkeypatch.setenv(VARIABLES['join'], '604')
    expected = tmp_path / 'spec/a2h/_work/expected_probe.json'
    expected.parent.mkdir(parents=True)
    expected.write_text(json.dumps({'join_point': 'probe', 'task_names': ['worker'],
        'artifacts': [{'path': 'artifact.txt', 'min_count': 1, 'min_bytes': 10}]}))
    (tmp_path / 'artifact.txt').write_text('complete synthetic artifact')
    rows = [{'type': 'session_meta', 'payload': {'id': 'synthetic-timeout-test',
        'cwd': str(tmp_path), 'agent_path': '/root/parent',
        'source': {'subagent': {'thread_spawn': {'agent_path': '/root/parent', 'depth': 1}}}}}]
    for name, call, arguments, result in [
        ('spawn_agent', 'spawn-1', {'task_name': 'worker'}, {'task_name': '/root/parent/worker'}),
        ('list_agents', 'list-1', {}, {'agents': [{'agent_name': '/root/parent/worker',
            'agent_status': {'completed': 'fixture completion'}}]})]:
        rows.extend([{'type': 'response_item', 'payload': {'type': 'function_call', 'name': name,
            'call_id': call, 'arguments': json.dumps(arguments)}},
            {'type': 'response_item', 'payload': {'type': 'function_call_output', 'call_id': call,
                'output': json.dumps(result)}}])
    start = datetime.now(timezone.utc)
    for index, row in enumerate(rows):
        row['timestamp'] = (start + timedelta(milliseconds=index)).isoformat()
    rollout = tmp_path / 'fixture.jsonl'
    rollout.write_text(''.join(json.dumps(row) + '\n' for row in rows))
    calls = []
    def execute(command, **kwargs):
        calls.append(kwargs['timeout'])
        return subprocess.CompletedProcess(command, 0, '句柄 1\njoined worker\n'.encode(), b'')
    monkeypatch.setattr('hmigbot_ios.scheduler_windows_runtime.run', execute)
    assert join_rollout.main(['--project', str(tmp_path), '--join-point', 'probe',
                              '--rollout', str(rollout), '--no-ledger']) == 0
    assert calls == [604]
    capsys.readouterr()


@pytest.mark.skipif(os.name != 'nt', reason='Windows owned process tree')
def test_real_short_timeout_kills_owned_descendant_and_replaces_stale_logs(tmp_path, monkeypatch):
    fake_staging(monkeypatch, windows_scheduler_runtime, tmp_path / 'runtime')
    monkeypatch.setenv(VARIABLES['scheduler'], '0.6')
    logs = tmp_path / 'spec/reports/scheduler'
    logs.mkdir(parents=True)
    (logs / 'land_results.stdout.log').write_bytes(b'OLD success')
    code = ('import subprocess,sys,time; '
            'child=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); '
            'print("owned-child="+str(child.pid),flush=True); '
            'print("NEW stderr",file=sys.stderr,flush=True); time.sleep(30)')
    def execute(command, **kwargs):
        assert kwargs['timeout'] == 0.6
        return owned_run([sys.executable, '-B', '-c', code], **kwargs)
    monkeypatch.setattr(windows_scheduler_runtime, 'run_owned_process', execute)
    with pytest.raises(MigrationError, match='Original scheduler failed'):
        windows_scheduler_runtime.invoke(tmp_path, 'land_results', [])
    partial = (logs / 'land_results.stdout.log').read_bytes()
    assert b'owned-child=' in partial and b'OLD success' not in partial
    assert (logs / 'land_results.stderr.log').read_bytes() == b'NEW stderr\r\n'
    assert read_json(logs / 'land_results.failure.json')['process_tree']['job_terminated'] is True
    child = int(partial.split(b'owned-child=')[1].splitlines()[0])
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    handle = kernel.OpenProcess(0x00100000, False, child)
    if handle:
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        try:
            assert kernel.WaitForSingleObject(handle, 3000) == 0
        finally:
            kernel.CloseHandle(handle)


@pytest.mark.skipif(os.name != 'nt', reason='Windows installed scheduler adapter')
def test_expired_deadline_launches_nothing_and_clears_stale_output(tmp_path, monkeypatch):
    monkeypatch.setenv(DEADLINE, '1')
    def must_not_run(*args, **kwargs):
        pytest.fail('expired deadline launched a subprocess')
    monkeypatch.setattr(windows_scheduler_runtime, 'run_owned_process', must_not_run)
    logs = tmp_path / 'spec/reports/scheduler'
    logs.mkdir(parents=True)
    (logs / 'next_batch.stdout.log').write_bytes(b'OLD success')
    with pytest.raises(MigrationError, match='Original scheduler failed'):
        windows_scheduler_runtime.invoke(tmp_path, 'next_batch', [])
    assert (logs / 'next_batch.stdout.log').read_bytes() == b''
    assert read_json(logs / 'next_batch.failure.json')['timeout_policy']['process_started'] is False
