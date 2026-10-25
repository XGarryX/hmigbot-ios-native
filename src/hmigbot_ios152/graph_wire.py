"""Read-only native UI graph input adapter for the unchanged original engines.

Only the Component identity key crosses the historical wire boundary. No source,
canonical node ID, edge, attribute value, or formal graph is rewritten.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from uuid import uuid4

FILES = ('Screen.json', 'Component.json', 'Navigation_Edge.json', 'Containment_Edge.json')
ADAPTER = 'hmigbot_ios152.graph_wire.v1'


class GraphInputError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def wire_component_bytes(data):
    """Leave malformed JSON for the original validator, never repair its input."""
    try:
        nodes = json.loads(data)
    except (ValueError, UnicodeError):
        return data
    if not isinstance(nodes, list):
        return data
    changed = False
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if 'android_id' in node:
            raise GraphInputError('Component identity must use only ios_id; legacy or dual identity keys are not accepted')
        if 'ios_id' in node:
            node['android_id'] = node.pop('ios_id')
            changed = True
    return (json.dumps(nodes, ensure_ascii=False, indent=2) + '\n').encode('utf-8') if changed else data


def native_result(value):
    """Map result keys only. User strings/IDs/source text are never substituted."""
    if isinstance(value, list):
        return [native_result(item) for item in value]
    if isinstance(value, dict):
        component = isinstance(value.get('id'), str) and value['id'].startswith('comp:')
        return {('ios_id' if component and key == 'android_id' else key): native_result(item)
                for key, item in value.items()}
    return value


def display_bytes(data):
    try:
        result = json.loads(data)
    except (ValueError, UnicodeError):
        # Exact diagnostic vocabulary only, not arbitrary occurrence substitution.
        return data.replace(b'Android UI Graph \xe2\x80\x94 Validation Report',
                            b'iOS UI Graph \xe2\x80\x94 Validation Report').replace(
            b"Missing required field: 'android_id'", b"Missing required field: 'ios_id'")
    return (json.dumps(native_result(result), ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def _emit(stream, data):
    if hasattr(stream, 'buffer'):
        stream.buffer.write(data)
        stream.buffer.flush()
    else:
        stream.write(data.decode('utf-8', errors='replace'))


def run(engine, command, argv, scripts_dir):
    """Run the original binary against a disposable four-file wire view.

    Raw original output and native display are retained outside the formal graph.
    Empty/incomplete/malformed input keeps the original engine's own disposition.
    Only a non-native identity key is an adapter input error (exit 2).
    """
    if not argv:
        return subprocess.run([str(engine), command]).returncode
    graph = Path(argv[0]).resolve()
    evidence_root = Path(os.environ.get('HMIGBOT_GRAPH_EVIDENCE_ROOT',
                                        str(graph.parent / '_graph-adapter-evidence'))).resolve()
    if evidence_root == graph or graph in evidence_root.parents:
        _emit(sys.stderr, b'Graph adapter evidence must be outside the formal graph directory\n')
        return 2
    evidence = evidence_root / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid4().hex[:8])
    evidence.mkdir(parents=True, exist_ok=False)
    record = {'adapter': ADAPTER, 'command': command, 'arguments': list(argv),
              'graph': str(graph), 'engine': str(Path(engine).resolve()),
              'formal_files': {}, 'wire_files': {}, 'formal_graph_written': False}
    raw_stdout = raw_stderr = b''
    exit_code = 2
    try:
        with tempfile.TemporaryDirectory(prefix='hmigbot-ios-graph-wire-') as folder:
            wire = Path(folder)
            snapshots = {name: (graph / name).read_bytes() if (graph / name).is_file() else None
                         for name in FILES}
            record['formal_files'] = {name: digest(data) if data is not None else None
                                      for name, data in snapshots.items()}
            record['formal_graph_sha256'] = digest(json.dumps(record['formal_files'], sort_keys=True).encode())
            for name, data in snapshots.items():
                if data is None:
                    record['wire_files'][name] = None
                    continue
                adapted = wire_component_bytes(data) if name == 'Component.json' else data
                record['wire_files'][name] = digest(adapted)
                (wire / name).write_bytes(adapted)
            record['wire_graph_sha256'] = digest(json.dumps(record['wire_files'], sort_keys=True).encode())
            record['wire_view'] = str(wire)
            env = dict(os.environ, ARKTS_SKILL_DIR=str(scripts_dir), PYTHONIOENCODING='utf-8')
            result = subprocess.run([str(engine), command, str(wire), *argv[1:]],
                                    capture_output=True, env=env)
            raw_stdout, raw_stderr = result.stdout, result.stderr
            exit_code = result.returncode
            record['engine_called'] = True
    except GraphInputError as error:
        record['adapter_error'] = str(error)
        record['engine_called'] = False
    except OSError as error:
        record['adapter_error'] = str(error)
        record['engine_called'] = False
    native_stdout, native_stderr = display_bytes(raw_stdout), display_bytes(raw_stderr)
    if record.get('adapter_error'):
        native_stderr += ('UI graph input error: ' + record['adapter_error'] + '\n').encode('utf-8')
    for name, data in [('original-stdout.log', raw_stdout), ('original-stderr.log', raw_stderr),
                       ('native-stdout.log', native_stdout), ('native-stderr.log', native_stderr)]:
        (evidence / name).write_bytes(data)
    record['exit_code'] = exit_code
    record['wire_view_removed'] = not Path(record.get('wire_view', '')).exists() if record.get('wire_view') else True
    (evidence / 'invocation.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    _emit(sys.stdout, native_stdout)
    _emit(sys.stderr, native_stderr)
    return exit_code
