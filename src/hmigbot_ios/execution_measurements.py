"""Project-local measured call spans; observations never approve project gates."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from functools import lru_cache
import json
import os
from pathlib import Path
import platform
import re
import stat
import subprocess
import sys
import time
import uuid

from .core import MigrationError, digest, json_bytes, source_snapshot, write_json
from .receipt_outputs import regular_path

ROOT = 'spec/reports/derived/execution-measurements'
CATEGORIES = {'work', 'task', 'wait', 'build', 'rework', 'merge', 'writeback', 'input'}
FAILED = {'failed', 'FAIL', 'blocked', 'error', 'timed_out', 'unavailable', 'interrupted', 'UNVERIFIED', 'build_failed'}


def _require(value, message):
    if not value:
        raise MigrationError(message)


def read_json(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        _require(stat.S_ISREG(info.st_mode) and info.st_size <= 64*1024*1024, 'Expected bounded ordinary JSON record')
        def pairs(values):
            result = {}
            for key, value in values:
                _require(key not in result, 'Duplicate JSON key: ' + key)
                result[key] = value
            return result
        def invalid(value):
            raise MigrationError('Non-finite JSON value: ' + value)
        return json.loads(stream.read().decode('utf-8-sig'), object_pairs_hook=pairs, parse_constant=invalid)


def _project(project):
    project = Path(project).absolute()
    _require(project.is_dir() and not any(p.is_symlink() for p in (project, *project.parents)),
             'Measurements require an ordinary, explicit project directory')
    runtime = Path(__file__).resolve().parents[2]
    _require(not project.is_relative_to(runtime), 'Tool maintenance measurements belong outside the runtime')
    return project


def _path(project, relative):
    return regular_path(project, relative)


def _id(value):
    _require(isinstance(value, str) and re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,100}', value), 'Invalid measurement identity')
    return value


@lru_cache(maxsize=1)
def _boot():
    # Use ordinary process clocks. Kernel inspection can be denied by a host
    # sandbox and must not introduce a permission requirement for timing.
    return digest(json_bytes({'node': platform.node(), 'system': platform.system(),
                              'machine': platform.machine(), 'release': platform.release()}))


def _clock():
    wall, monotonic = time.time_ns(), time.monotonic_ns()
    return {'wall_ns': wall, 'monotonic_ns': monotonic, 'domain': _boot(), 'epoch_ns': wall-monotonic}


def _same_clock(before, after):
    return (before['domain'] == after['domain'] and after['monotonic_ns'] >= before['monotonic_ns']
            and abs(before['epoch_ns']-after['epoch_ns']) <= 2_000_000_000)


@contextmanager
def _lock(project, *, create=False):
    import fcntl
    directory = _path(project, ROOT)
    if create:
        directory.mkdir(parents=True, exist_ok=True)
    path = _path(project, ROOT + '/.lock')
    fd = os.open(path, (os.O_RDWR | os.O_CREAT if create else os.O_RDONLY) | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX if create else fcntl.LOCK_SH)
        yield
    finally:
        os.close(fd)


def _identity(project):
    config = read_json(_path(project, '.migbot/config.json'))
    _require(config.get('source_platform') == 'ios' and config.get('ios'), 'Configure the iOS source before starting measurements')
    source = Path(config['ios'])
    source = (source if source.is_absolute() else project/source).resolve(strict=True)
    _require(source.is_dir() and source != project and not source.is_relative_to(project)
             and not project.is_relative_to(source), 'Source and target must not contain each other')
    normalized = dict(config, ios='<source>', harmonyos='<target>')
    return {'source_sha256': source_snapshot(source)['sha256'],
            'configuration_sha256': digest(json_bytes(normalized)),
            'environment': {'system': platform.system(), 'machine': platform.machine(),
                            'release': platform.release(), 'python': platform.python_version()}}


def _run_path(run_id):
    return ROOT + '/' + _id(run_id)


def start(project, request):
    project = _project(project)
    _require(isinstance(request, dict) and set(request) <= {'run_id', 'scope', 'quality_protocol', 'cache'}, 'Invalid measurement request')
    for name in ('scope', 'quality_protocol'):
        _require(isinstance(request.get(name), dict) and request[name], name + ' must explicitly identify this run')
    _require(request.get('cache') in {'cold', 'warm', 'unknown'}, 'Declare cold/warm/unknown cache; it is not inferred')
    run_id = _id(request.get('run_id', uuid.uuid4().hex))
    value = {'schema_version': 1, 'run_id': run_id, 'identity': _identity(project),
             'scope': request['scope'], 'quality_protocol': request['quality_protocol'],
             'cache': request['cache'], 'start': _clock(), 'status': 'running',
             'tool_version': __import__('hmigbot_ios').__version__}
    with _lock(project, create=True):
        active = _path(project, ROOT + '/active.json')
        _require(not active.exists(), 'A measured run is active; finish/interruption must be recorded first')
        path = _path(project, _run_path(run_id) + '/run.json')
        _require(not path.exists(), 'Measurement run IDs are immutable')
        write_json(path, value)
        write_json(active, {'run_id': run_id})
    return {'status': 'started', 'run_id': run_id, 'record': _run_path(run_id) + '/run.json'}


def observe_start(project, stage, operation, category='work', metadata=None):
    """Record an actual invocation, or return None when no run was selected."""
    project = _project(project)
    if not _path(project, ROOT + '/active.json').is_file():
        return None
    _require(category in CATEGORIES and isinstance(stage, str) and isinstance(operation, str), 'Invalid span')
    with _lock(project, create=True):
        run_id = _id(read_json(_path(project, ROOT + '/active.json'))['run_id'])
        run = read_json(_path(project, _run_path(run_id) + '/run.json'))
        _require(run['status'] == 'running' and _same_clock(run['start'], _clock()), 'Run clock domain changed; preserve the run as unresolved')
        span_id = uuid.uuid4().hex
        value = {'schema_version': 1, 'run_id': run_id, 'span_id': span_id, 'stage': stage,
                 'operation': operation, 'category': category, 'metadata': metadata or {}, 'start': _clock()}
        write_json(_path(project, _run_path(run_id) + '/spans/' + span_id + '.json'), value)
    return {'run_id': run_id, 'span_id': span_id}


def observe_end(project, token, status, exit_code=None, metadata=None):
    if token is None:
        return None
    project = _project(project)
    with _lock(project, create=True):
        run = read_json(_path(project, _run_path(token['run_id']) + '/run.json'))
        _require(run['status'] == 'running', 'A closed run cannot receive late span results')
        relative = _run_path(token['run_id']) + '/spans/' + _id(token['span_id']) + '.json'
        path = _path(project, relative)
        span = read_json(path)
        _require('end' not in span, 'Span completion is immutable')
        end = _clock()
        _require(_same_clock(span['start'], end), 'Measurement clock changed')
        _require(isinstance(status, str) and status, 'A real result status is required')
        span.update(end=end, status=status, exit_code=exit_code)
        span['metadata'].update(metadata or {})
        write_json(path, span)
    return {'status': 'recorded', **token}


def _spans(project, run_id):
    directory = _path(project, _run_path(run_id) + '/spans')
    return [read_json(_path(project, p.relative_to(project).as_posix())) for p in sorted(directory.glob('*.json'))]


def _quality(project, paths, run_id):
    _require(isinstance(paths, list), 'quality_evidence must be a list of project-relative JSON reports')
    results, prepared = [], []
    for index, name in enumerate(paths):
        path = _path(project, name)
        data = read_json(path)
        raw = path.read_bytes()
        verdict = data.get('verdict', data.get('status')) if isinstance(data, dict) else None
        archived = _run_path(run_id) + '/quality/' + str(index) + '.json'
        destination = _path(project, archived)
        _require(not destination.exists() or destination.read_bytes() == json_bytes(data), 'Quality snapshots already exist; preserve original evidence')
        prepared.append((destination, data))
        results.append({'path': archived, 'source_path': name, 'source_sha256': digest(raw),
                        'sha256': digest(json_bytes(data)), 'passed': verdict in {'PASS', 'passed', 'pass', 'build_passed'}})
    for destination, data in prepared:
        if not destination.exists():
            write_json(destination, data)
    return results


def finish(project, run_id, request):
    project = _project(project)
    _require(request.get('status') in {'completed', 'failed', 'interrupted'}, 'Declare completed/failed/interrupted')
    with _lock(project, create=True):
        path = _path(project, _run_path(run_id) + '/run.json')
        run = read_json(path)
        _require(run['status'] == 'running' and read_json(_path(project, ROOT+'/active.json'))['run_id'] == run_id,
                 'Only the active run can be finished')
        spans = _spans(project, run_id)
        _require(request['status'] != 'completed' or all('end' in s for s in spans), 'Unfinished spans prevent a completed run')
        end = _clock()
        clock_valid = _same_clock(run['start'], end)
        _require(request['status'] != 'completed' or clock_valid, 'Clock domain changed; finish interrupted without a duration claim')
        try:
            final_identity = _identity(project)
        except (MigrationError, OSError, ValueError) as exc:
            _require(request['status'] != 'completed', 'Current source identity is unavailable')
            final_identity = {'unavailable': str(exc)}
        run.update(status=request['status'], end=end, clock_valid=clock_valid,
                   quality_evidence=_quality(project, request.get('quality_evidence', []), run_id), final_identity=final_identity)
        write_json(path, run)
        _path(project, ROOT+'/active.json').unlink()
    result = summary(project, run_id)
    report = ROOT + '/' + run_id + '/summary.md'
    rows = ['# 全流程实际计量', '', '- run：' + run_id, '- 结果：' + result['status'],
            '- 实际经过：' + str(result['wall_seconds']) + ' 秒',
            '- 实际调用：' + str(result['calls']), '- 未结束调用：' + str(result['unfinished_calls']),
            '- 最大已计量任务并发：' + str(result['maximum_measured_tasks']), '',
            '| 类别 | 次数 | 耗时之和（秒） | 实际覆盖时长（秒） |', '|---|---:|---:|---:|']
    for category, counters in result['categories'].items():
        rows.append('| ' + category + ' | ' + str(counters['calls']) + ' | ' + str(round(counters['sum_seconds'], 3))
                    + ' | ' + str(round(counters['elapsed_union_seconds'], 3)) + ' |')
    rows += ['', '嵌套调用之和包含重叠，不能当作用户等待时间；只统计已实际记录的调用。',
             '缓存状态由本轮声明；计量不授予生成、编译、行为或视觉验收。']
    path = _path(project, report)
    path.write_text('\n'.join(rows)+'\n', encoding='utf-8')
    return dict(result, report=report)


def _union(intervals):
    total = 0
    right = None
    for start_ns, end_ns in sorted(intervals):
        total += max(0, end_ns - max(start_ns, right if right is not None else start_ns))
        right = max(end_ns, right if right is not None else end_ns)
    return total / 1e9


def summary(project, run_id):
    project = _project(project)
    with _lock(project):
        run = read_json(_path(project, _run_path(run_id)+'/run.json'))
        spans = _spans(project, run_id)
        completed = [s for s in spans if 'end' in s]
        categories = {}
        for category in sorted(CATEGORIES):
            group = [s for s in completed if s['category'] == category]
            intervals = [(s['start']['monotonic_ns'], s['end']['monotonic_ns']) for s in group]
            categories[category] = {'calls': len(group), 'sum_seconds': sum(b-a for a,b in intervals)/1e9,
                                    'elapsed_union_seconds': _union(intervals)}
        points = sorted((t, delta) for s in completed if s['category'] == 'task'
                        for t, delta in [(s['start']['monotonic_ns'], 1), (s['end']['monotonic_ns'], -1)])
        current = maximum = 0
        for _, delta in points:
            current += delta
            maximum = max(maximum, current)
        evidence_current = all(digest(_path(project, e['path']).read_bytes()) == e['sha256'] for e in run.get('quality_evidence', []))
        end = run.get('end')
        return {'schema_version': 1, 'run_id': run_id, 'status': run['status'], 'identity': run['identity'],
                'scope': run['scope'], 'quality_protocol': run['quality_protocol'], 'cache': run['cache'],
                'wall_seconds': (end['monotonic_ns']-run['start']['monotonic_ns'])/1e9 if end and run.get('clock_valid') else None,
                'calls': len(spans), 'unfinished_calls': len(spans)-len(completed), 'categories': categories,
                'successful_operations': sorted({s['operation'] for s in completed if s.get('exit_code') == 0
                                                and s.get('status') not in FAILED}),
                'maximum_measured_tasks': maximum,
                'failed_calls': sum(s.get('exit_code') not in (None, 0) or s.get('status') in FAILED for s in completed),
                'input_bytes': sum(s.get('metadata', {}).get('input_bytes', 0) for s in completed),
                'identity_unchanged': run.get('final_identity') == run['identity'],
                'quality_evidence_current': evidence_current,
                'quality_passed': bool(run.get('quality_evidence')) and evidence_current and all(e['passed'] for e in run['quality_evidence']),
                'timing_scope': 'Measured intervals only; nested call sums include overlap; task concurrency excludes ordinary calls',
                'cache_scope': 'Caller-declared cache condition, not an automatic cache inspection'}


def compare(current, baseline):
    reasons = []
    for key in ('identity', 'scope', 'quality_protocol', 'cache'):
        if current.get(key) != baseline.get(key):
            reasons.append('Different ' + key)
    for label, result in [('current', current), ('baseline', baseline)]:
        if (result.get('status') != 'completed' or not result.get('identity_unchanged') or not result.get('quality_passed')
                or result.get('unfinished_calls') or not result.get('calls') or result.get('wall_seconds', 0) is None):
            reasons.append(label + ': complete measured scope and current passing quality evidence are required')
        required = result.get('quality_protocol', {}).get('required_commands')
        if not isinstance(required, list) or not required or not set(required) <= set(result.get('successful_operations', [])):
            reasons.append(label + ': required quality commands were not actually recorded successfully')
        if result.get('cache') == 'unknown':
            reasons.append(label + ': cache condition is unknown')
    if baseline.get('wall_seconds', 0) is None or baseline.get('wall_seconds', 0) <= 0:
        reasons.append('No positive baseline duration')
    result = {'status': 'not_comparable' if reasons else 'measured_comparison', 'comparison_available': not reasons,
              'current': current, 'baseline': baseline, 'reasons': reasons}
    if not reasons:
        result['wall_time_reduction_percent'] = 100*(baseline['wall_seconds']-current['wall_seconds'])/baseline['wall_seconds']
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest='action', required=True)
    for name in ('start', 'finish', 'summary', 'begin', 'end', 'compare'):
        command = actions.add_parser(name)
        command.add_argument('--project', required=True, type=Path)
        if name in {'start', 'finish', 'begin', 'end'}:
            command.add_argument('--input', required=True, type=Path)
        if name in {'finish', 'summary', 'compare'}:
            command.add_argument('--run', required=True)
        if name == 'compare':
            command.add_argument('--baseline', required=True)
    args = parser.parse_args(argv)
    try:
        request = read_json(args.input) if hasattr(args, 'input') else None
        if args.action == 'start': result = start(args.project, request)
        elif args.action == 'finish': result = finish(args.project, args.run, request)
        elif args.action == 'summary': result = summary(args.project, args.run)
        elif args.action == 'begin': result = observe_start(args.project, **request)
        elif args.action == 'end': result = observe_end(args.project, **request)
        else: result = compare(summary(args.project, args.run), summary(args.project, args.baseline))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (MigrationError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'blocked', 'error': str(exc), 'recovery': 'Preserve the measured run; repair explicit inputs, or finish interrupted without claiming speedup.'}, ensure_ascii=False))
        return 2
