"""Fresh whole-orphan measurement with official same-file UI composition proof.

The original graph/parser/resolver are executed as visible source. Their missing
walker and pipeline caller are explicitly reconstructed compatibility code, not
claimed recovered upstream source. Native output is never an input to this
measurement; the pipeline adapter compares its same-run native archive separately.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hmigbot_ios152.binding_projection import (
    _Guard, _file, _json, _process, _write,
    ProjectionInputChanged, ProjectionEvidenceError,
)


class OrphanMeasurementError(RuntimeError):
    exit_code = 3


class OrphanInputChanged(OrphanMeasurementError):
    pass


class OrphanEvidenceError(OrphanMeasurementError):
    pass


_VM_HINTS = ('/viewmodels/', '/store/', '/stores/', '/repository/',
             '/repositories/', '/service/', '/services/', '/network/')
_COMPONENT_HINTS = ('/components/', '/views/', '/widgets/', '/dialogs/', '/dialog/')
_VM_HINTS += tuple(h.replace('/', '\\') for h in _VM_HINTS)
_COMPONENT_HINTS += tuple(h.replace('/', '\\') for h in _COMPONENT_HINTS)
_SKIP = {'.git', '.hvigor', '.idea', 'oh_modules', 'node_modules', 'build',
         '.cxx', '.preview', '.claude', '.agents', '.codex'}
_NETWORK_EVIDENCE = ['network-infra: ONLY_INSTANTIATED_BY_NON_UI 对基础设施层是正常架构（由非 UI 装配）']


def _inventory(project):
    files = []
    for directory, names, entries in os.walk(project):
        names[:] = [name for name in names if name not in _SKIP]
        files.extend(str((Path(directory) / name).relative_to(project))
                     for name in entries if name.endswith(('.ets', '.ts')))
    return sorted(files)


class _OrphanGuard:
    def __init__(self, project, snapshot=None):
        self.project = Path(project)
        self.guard = _Guard()
        if snapshot is None:
            self.inventory = _inventory(self.project)
            for name in self.inventory:
                self.guard.add(self.project / name)
        else:
            self.inventory = snapshot['source_inventory']
            self.guard.paths = snapshot['guard']['files']
            self.guard.trees = snapshot['guard']['inventories']

    def snapshot(self):
        return {'source_inventory': copy.deepcopy(self.inventory),
                'guard': self.guard.snapshot()}

    def verify(self):
        if _inventory(self.project) != self.inventory:
            raise OrphanInputChanged('Orphan source inventory changed')
        try:
            self.guard.verify()
        except ProjectionInputChanged as error:
            raise OrphanInputChanged(str(error)) from error


def _load_graph(project, scripts, guard):
    for name in ('__init__.py', 'graph.py', 'ets_parser.py', 'import_resolver.py'):
        path = scripts / 'ref_graph_lib' / name
        if not path.is_file():
            raise OrphanMeasurementError('Original visible orphan module missing: ' + str(path))
        guard.guard.add(path)
    walker = scripts / 'fswalk.py'
    if not walker.is_file():
        raise OrphanMeasurementError('Orphan traversal module missing: ' + str(walker))
    guard.guard.add(walker)
    sys.path.insert(0, str(scripts))
    from ref_graph_lib.graph import EtsRefGraph
    module = sys.modules[EtsRefGraph.__module__]
    if Path(module.__file__).resolve() != (scripts / 'ref_graph_lib/graph.py').resolve():
        raise OrphanMeasurementError('Orphan graph resolved outside selected package')
    return EtsRefGraph(project).build()


def _whole_result(graph, rescued=frozenset()):
    """Original caller contract, with a proven local inbound edge as one predicate.

    All rows and counts are remeasured from this graph. No native rows or native
    totals are read, filtered, or decremented.
    """
    vm_files = [p for p in graph.files if any(h in str(p) for h in _VM_HINTS)]
    component_files = [p for p in graph.files if any(h in str(p) for h in _COMPONENT_HINTS)]
    raw_vm = graph.find_orphans(vm_files)
    component_rows = graph.find_orphan_components(component_files)
    component_rows = [row for row in component_rows
                      if (row.file, row.class_name) not in rescued]
    unrendered = graph.find_unrendered_components(component_files)
    kept, exempted, remaining = [], [], []
    for finding in raw_vm:
        row = finding.to_dict()
        if any(h in '/' + row['file'] for h in ('/network/', '\\network\\')) and row['reason'] == 'ONLY_INSTANTIATED_BY_NON_UI':
            row['exempt_evidence'] = _NETWORK_EVIDENCE.copy()
            exempted.append(row)
        else:
            remaining.append(finding)
    for finding in remaining:
        row = finding.to_dict()
        evidence = graph.usage_evidence(row['class_name'], row['file'])
        if evidence:
            row['exempt_evidence'] = evidence
            exempted.append(row)
        else:
            kept.append(row)
    kept.extend(row.to_dict() for row in component_rows)
    return {'vm_candidates': len(vm_files), 'component_candidates': len(component_files),
            'component_orphan_count': len(component_rows),
            'component_unrendered_count': len(unrendered),
            'component_unrendered_warnings': [row.to_dict() for row in unrendered],
            'orphan_count': len(kept), 'orphans': kept,
            'exempted_count': len(exempted), 'exempted': exempted}


def _sdk(project, scripts, guard):
    helper_path = scripts / 'wiring_source.py'
    guard.guard.add(helper_path)
    spec = importlib.util.spec_from_file_location('_orphan_wiring_helpers', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    node, parser, selection = helper.sdk_runtime(project)
    loader = next(p for p in (parser, *parser.parents) if p.name == 'ets-loader')
    sdk = loader.parent.parent
    for path in (node, Path(selection['package']), loader / 'tsconfig.json'):
        guard.guard.add(path)
    if _file(Path(selection['package'])).get('sha256') != selection['packageSha256']:
        raise OrphanInputChanged('Selected SDK metadata changed during discovery')
    guard.guard.tree(parser if parser.is_dir() else parser.parent)
    for root in (sdk, sdk.parent.parent / 'hms/ets'):
        for name in ('api', 'kits', 'component'):
            if (root / name).is_dir():
                guard.guard.tree(root / name)
    for name in ('declarations', 'node_modules/json5'):
        guard.guard.tree(loader / name)
    return node, parser, selection


def _bytes(value):
    return json.dumps(value, ensure_ascii=False, indent=2).encode('utf-8')


def _worker(project, scripts, evidence):
    if evidence.is_relative_to(project):
        raise OrphanEvidenceError('Orphan measurement evidence must be outside project')
    guard = _OrphanGuard(project)
    for path in (Path(sys.executable), Path(__file__), Path(__file__).with_name('orphan_measurement_sdk.cjs'),
                 Path(__file__).with_name('binding_projection.py')):
        guard.guard.add(path)
    for name in ('.migbot/config.json', 'build-profile.json5', 'local.properties'):
        guard.guard.add(project / name)
    graph = _load_graph(project, scripts, guard)
    baseline = _whole_result(graph)
    component_files = [p for p in graph.files if any(h in str(p) for h in _COMPONENT_HINTS)]
    targets = [row for row in baseline['orphans']
               if graph.info.get((project / row['file']).resolve()) is not None and
               graph.info[(project / row['file']).resolve()].export_kinds.get(row['class_name']) == 'struct'
               and (project / row['file']).resolve() in component_files]
    rescued, sdk_record = [], None
    if targets:
        helper = Path(__file__).with_name('ets_components.cjs')
        if not helper.is_file():
            raise OrphanMeasurementError('Official ETS custom-component context helper missing')
        guard.guard.add(helper)
        node, parser, selection = _sdk(project, scripts, guard)
        original_orphans = {(row['file'], row['class_name']) for row in baseline['orphans']}
        seeds = [{'file': str(p.relative_to(project)), 'name': name}
                 for p in component_files for name in graph.info[p].exports
                 if graph.info[p].export_kinds.get(name) == 'struct'
                 and (str(p.relative_to(project)), name) not in original_orphans]
        request = {'runId': uuid.uuid4().hex, 'project': str(project),
                   'files': list(map(str, component_files)), 'parserModule': str(parser),
                   'sdkSelection': selection, 'seeds': seeds,
                   'targets': [{'file': row['file'], 'name': row['class_name']} for row in targets]}
        _json(evidence / 'sdk.request.json', request)
        process, stdout, _ = _process([node, Path(__file__).with_name('orphan_measurement_sdk.cjs')],
                                     evidence, 'sdk', env=dict(os.environ), cwd=project,
                                     data=(json.dumps(request, ensure_ascii=False) + '\n').encode())
        if process['exit_code'] != 0:
            raise OrphanMeasurementError('Official orphan SDK proof process failed')
        sdk_record = json.loads(stdout)
        if sdk_record.get('runId') != request['runId'] or sdk_record.get('valid') is not True:
            raise OrphanMeasurementError('Invalid official orphan SDK response')
        target_map = {(row['file'], row['class_name']): row for row in targets}
        seed_keys = {(row['file'], row['name']) for row in seeds}
        seen = set()
        for proof in sdk_record.get('proofs', []):
            target, seed, chain = proof.get('target', {}), proof.get('seed', {}), proof.get('chain', [])
            key = target.get('file'), target.get('name')
            if key not in target_map or key in seen or (seed.get('file'), seed.get('name')) not in seed_keys or not chain:
                raise OrphanMeasurementError('Unproven/duplicate orphan local-use response')
            if chain[0].get('from') != proof.get('seedKey') or chain[-1].get('to') != proof.get('targetKey'):
                raise OrphanMeasurementError('Orphan local-use chain endpoints do not match')
            if any(a.get('to') != b.get('from') for a, b in zip(chain, chain[1:])):
                raise OrphanMeasurementError('Disconnected orphan local-use chain')
            if any(edge.get('file') != target['file'] or not isinstance(edge.get('line'), int) or edge['line'] < 1 for edge in chain):
                raise OrphanMeasurementError('Orphan local-use evidence escapes defining file')
            seen.add(key)
            rescued.append({'record': target_map[key], 'seed': seed, 'chain': chain,
                            'seedKey': proof['seedKey'], 'targetKey': proof['targetKey']})
    result = _whole_result(graph, frozenset((item['record']['file'], item['record']['class_name']) for item in rescued))
    guard.verify()
    provenance = {'schema': 'fresh-orphans.v1', 'hashseed': os.environ.get('PYTHONHASHSEED'),
                  'python': sys.version, 'pythonExecutable': sys.executable,
                  'measurementFile': str(Path(__file__).resolve()), 'scriptsDir': str(scripts),
                  'graphFile': sys.modules[graph.__class__.__module__].__file__,
                  'rescued': rescued, 'sdk': sdk_record,
                  'sdkNotRequired': not bool(targets),
                  'baselineContract': 'original visible graph/parser/resolver with explicitly reconstructed native walker/caller',
                  'limitations': ['Static source/official SDK proof; no build, visual, or device validation.']}
    _write(evidence / 'baseline.json', _bytes(baseline))
    _write(evidence / 'result.json', _bytes(result))
    _json(evidence / 'measurement.json', {'baseline': baseline, 'result': result,
                                        'provenance': provenance, 'signature': guard.snapshot()})


@dataclass
class OrphanMeasurement:
    baseline: dict
    result: dict
    baseline_bytes: bytes
    result_bytes: bytes
    provenance: dict
    signature: dict
    _guard: object = field(repr=False)

    def verify(self):
        self._guard.verify()


def measure_orphans(*, project: Path, scripts_dir: Path, evidence: Path, env: dict) -> OrphanMeasurement:
    project, scripts_dir, evidence = map(lambda p: Path(p).resolve(), (project, scripts_dir, evidence))
    if evidence.is_relative_to(project):
        raise OrphanEvidenceError('Orphan measurement evidence must be outside project')
    child_env = dict(env, PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1')
    argv = [sys.executable, '-B', str(Path(__file__).resolve()), '_measure', str(project), str(scripts_dir), str(evidence)]
    try:
        process, _, stderr = _process(argv, evidence, 'fresh-source', env=child_env, cwd=project)
        if process['exit_code'] != 0:
            raise OrphanMeasurementError('Fresh orphan measurement failed: ' + stderr.decode('utf-8', errors='replace').strip())
        data = json.loads((evidence / 'measurement.json').read_bytes())
        baseline_bytes, result_bytes = (evidence / 'baseline.json').read_bytes(), (evidence / 'result.json').read_bytes()
        if baseline_bytes != _bytes(data['baseline']) or result_bytes != _bytes(data['result']):
            raise OrphanMeasurementError('Fresh orphan JSON bytes differ from measured records')
        guard = _OrphanGuard(project, data['signature'])
        guard.verify()
        provenance = dict(data['provenance'], freshSourceProcess=process)
        return OrphanMeasurement(data['baseline'], data['result'], baseline_bytes, result_bytes,
                                 provenance, data['signature'], guard)
    except ProjectionEvidenceError as error:
        raise OrphanEvidenceError(str(error)) from error
    except (OSError, ValueError, KeyError) as error:
        raise OrphanMeasurementError('Invalid fresh orphan measurement/evidence: ' + str(error)) from error


if __name__ == '__main__':
    try:
        if len(sys.argv) != 5 or sys.argv[1] != '_measure':
            raise OrphanMeasurementError('Expected internal fresh orphan measurement arguments')
        _worker(*map(lambda p: Path(p).resolve(), sys.argv[2:]))
    except Exception as error:
        sys.stderr.write(type(error).__name__ + ': ' + str(error) + '\n')
        raise SystemExit(3)
