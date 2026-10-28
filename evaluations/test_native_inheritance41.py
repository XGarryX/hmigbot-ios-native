"""Indexed producer -> actual retained inheritance -> native writer contracts.

Fixtures are synthetic, never device evidence. The optional engine is the
byte-verified original core with only the established Mac runtime adaptation.
"""
from contextlib import redirect_stdout
import copy
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.core import MigrationError, read_json, write_json
from hmigbot_ios152 import native_canonical as C
from hmigbot_ios152.native_visual import functional_snapshot
from evaluations.test_native_canonical import Fixture


@unittest.skipUnless(os.environ.get('HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE'), 'Needs retained original core')
class IndexedInheritance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='native41-inherit-')
        self.root = Path(self.temp.name)
        self.scripts = ROOT / 'skills/arkts-visual-verify/scripts'
        engine = Path(os.environ['HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE'])
        def execute(command, args, scripts, *, cwd=None, env=None):
            return subprocess.run([str(engine), command, *map(str, args)], cwd=cwd,
                capture_output=True, text=True, timeout=60,
                env={**os.environ, **(env or {}), 'ARKTS_SKILL_DIR': str(engine.parents[3])})
        self.original = patch.object(C, '_core', side_effect=execute)
        self.original.start()

    def tearDown(self):
        self.original.stop()
        self.temp.cleanup()

    def fixture(self, name='case', *, trip='trip_2_logged_in_vip', trigger='Open library'):
        f = Fixture(self.root / name, names=('HomeView', 'LibraryView'))
        tree = read_json(f.tree)
        tree['pages'][0]['functional_checks'] = [
            {'name': 'Open library', 'feature_path': 'Home>open', 'expected_ios': None, 'ios_trusted': None}]
        write_json(f.tree, tree)
        fingerprint = functional_snapshot(tree['pages'][0])
        plan = read_json(f.ew / 'walk_plan.json')
        plan['walks'][0]['steps'][1]['settles_grounding'] = ['Open library']
        write_json(f.ew / 'walk_plan.json', plan)
        row = {'idx': 0, 'name': 'Open library', 'check_idx': 0, 'check_name': 'Open library',
               'feature_path': 'Home>open', 'functional_checks_sha256': fingerprint,
               'status': 'deferred_to_walk', 'walk_evidence': {'walk_id': 'neutral_walk', 'step': 2}}
        meta = f.ew / 'grounding/HomeView/run_meta.json'
        write_json(meta, {'node': 'HomeView', 'functional_checks_sha256': fingerprint, 'checks': [row]})
        edge = {'from': 'HomeView', 'to': 'LibraryView', 'status': 'confirmed', 'device_state': trip,
                'control': {'rid': '', 'text': trigger}, 'landed': 'LibraryView',
                'back_returns_to_parent': True, 'evidence': 'SYNTHETIC fixture, not a device observation'}
        write_json(f.ew / 'edge_results.json', [edge])
        return f, meta, fingerprint

    def inherit(self, f):
        with redirect_stdout(io.StringIO()):
            return C.inherit_cli(['--dir', str(f.ew), '--device-state', f.trip], self.scripts)

    def test_indexed_current_trip_closes_through_original_core_and_native_writer(self):
        f, meta, fingerprint = self.fixture()
        original_meta = meta.read_bytes()
        self.assertEqual(self.inherit(f), 0)
        rows = read_json(f.ew / 'grounding_results.json')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['feature_path'], 'Home>open')
        self.assertEqual(rows[0]['functional_checks_sha256'], fingerprint)
        self.assertIs(rows[0]['ios_trusted'], True)
        self.assertEqual(meta.read_bytes(), original_meta)
        with redirect_stdout(io.StringIO()):
            code = C.tree_write_cli('writeback_walk', ['--tree', str(f.tree),
                '--grounding', str(f.ew / 'grounding_results.json'),
                '--edges', str(f.ew / 'edge_results.json')], self.scripts)
        self.assertEqual(code, 0)
        self.assertIs(read_json(f.tree)['pages'][0]['functional_checks'][0]['ios_trusted'], True)

    def test_foreign_and_unmarked_edges_cannot_be_labelled_current_trip(self):
        for idx, trip in enumerate(['trip_1_logged_out', None]):
            f, meta, _ = self.fixture(str(idx), trip=trip)
            before = (f.ew / 'edge_results.json').read_bytes()
            self.assertEqual(self.inherit(f), 0)
            self.assertEqual(read_json(f.ew / 'grounding_results.json'), [])
            self.assertEqual(len(read_json(f.ew / 'needs_retap.json')), 1)
            self.assertEqual((f.ew / 'edge_results.json').read_bytes(), before)
            self.assertEqual(len(read_json(f.ew / 'inherit.native-input.json')['excluded_edges']), 1)

    def test_original_trigger_forms_and_repeat_are_preserved(self):
        for idx, trigger in enumerate([None, '', 'Actual observed label']):
            f, meta, _ = self.fixture(str(idx), trigger=trigger)
            m = read_json(meta)
            m['checks'][0].update(status='deferred_same_destination',
                inherit_from_edge={'from': 'HomeView', 'to': 'LibraryView', 'trigger': trigger})
            write_json(meta, m)
            self.assertEqual(self.inherit(f), 0)
            first = read_json(f.ew / 'grounding_results.json')
            self.assertEqual(len(first), 1)
            self.assertEqual(self.inherit(f), 0)
            self.assertEqual(read_json(f.ew / 'grounding_results.json'), first)

    def test_unbound_navigation_stays_debt_without_invented_same_destination(self):
        for idx, evidence in enumerate([{}, {'walk_id': 'neutral_walk', 'step': 999},
                                        {'walk_id': 'other_walk', 'step': 2}]):
            f, meta, _ = self.fixture(str(idx))
            m = read_json(meta); m['checks'][0]['walk_evidence'] = evidence; write_json(meta, m)
            self.assertEqual(self.inherit(f), 0)
            self.assertEqual(read_json(f.ew / 'grounding_results.json'), [])
            receipt = read_json(f.ew / 'inherit.native-input.json')
            self.assertEqual(len(receipt['unresolved']), 1)
            self.assertIsNone(read_json(f.tree)['pages'][0]['functional_checks'][0]['ios_trusted'])

    def test_stale_and_misaligned_indexed_identity_fail_before_publication(self):
        for idx, change in enumerate([{'functional_checks_sha256': 'stale'}, {'feature_path': 'Other>open'},
                                      {'idx': 1, 'check_idx': 1}, {'check_name': 'Other'}]):
            f, meta, _ = self.fixture(str(idx))
            m = read_json(meta); m['checks'][0].update(change); write_json(meta, m)
            with self.assertRaises(MigrationError): self.inherit(f)
            self.assertFalse((f.ew / 'grounding_results.json').exists())

    def test_unbound_explicit_same_destination_cannot_bypass_plan_binding(self):
        f, meta, _ = self.fixture()
        m = read_json(meta)
        m['checks'][0].update(status='deferred_same_destination',
            inherit_from_edge={'from': 'OtherView', 'to': 'LibraryView', 'trigger': None})
        write_json(meta, m)
        self.assertEqual(self.inherit(f), 0)
        self.assertEqual(read_json(f.ew / 'grounding_results.json'), [])
        self.assertEqual(len(read_json(f.ew / 'inherit.native-input.json')['unresolved']), 1)

    def test_settled_by_walk_is_not_reinterpreted_or_downgraded(self):
        f, meta, _ = self.fixture()
        m = read_json(meta); m['checks'][0].update(status='settled_by_walk', walk_evidence={}); write_json(meta, m)
        original = C._core; observed = []
        def record(command, args, scripts, **kwargs):
            directory = Path(args[args.index('--dir') + 1])
            observed.append(read_json(directory / 'grounding/HomeView/run_meta.json')['checks'][0])
            return original(command, args, scripts, **kwargs)
        with patch.object(C, '_core', side_effect=record): self.assertEqual(self.inherit(f), 0)
        self.assertEqual(observed[0], C.legacy_wire(m)['checks'][0])

    def test_empty_explicit_declaration_does_not_gain_plan_derived_ends(self):
        f, meta, _ = self.fixture()
        m = read_json(meta); m['checks'][0].update(status='deferred_same_destination', inherit_from_edge={}); write_json(meta, m)
        before = meta.read_bytes()
        self.assertEqual(self.inherit(f), 0)
        self.assertEqual(read_json(f.ew / 'grounding_results.json'), [])
        self.assertEqual(len(read_json(f.ew / 'inherit.native-input.json')['unresolved']), 1)
        self.assertEqual(meta.read_bytes(), before)

    def test_mixed_directory_trip_projection_is_disclosed_and_retap_is_bound(self):
        f, meta, fingerprint = self.fixture()
        write_json(f.ew / 'grounding/LibraryView/run_meta.json', {'node': 'LibraryView', 'checks': [
            {'idx': 0, 'name': 'Return home', 'status': 'deferred_same_destination',
             'inherit_from_edge': {'from': 'LibraryView', 'to': 'HomeView', 'trigger': 'Return home'}}]})
        edges = read_json(f.ew / 'edge_results.json')
        edges.append({'from': 'LibraryView', 'to': 'HomeView', 'status': 'confirmed',
                      'device_state': 'trip_1_logged_out', 'control': {'text': 'Return home'},
                      'landed': 'HomeView', 'evidence': 'Synthetic legacy fixture'})
        write_json(f.ew / 'edge_results.json', edges)
        self.assertEqual(self.inherit(f), 0)
        receipt = read_json(f.ew / 'inherit.native-input.json')
        self.assertEqual(receipt['legacy_nodes'], ['LibraryView'])
        self.assertEqual(receipt['trip_scope'], 'whole directory, including legacy nodes')
        self.assertEqual(len(receipt['excluded_edges']), 1)
        self.assertEqual(read_json(f.ew / 'needs_retap.json')[0]['node'], 'LibraryView')
        # Indexed retap also carries its unambiguous original identity.
        f2, _, fp2 = self.fixture('retap', trip='trip_1_logged_out')
        self.assertEqual(self.inherit(f2), 0)
        retap = read_json(f2.ew / 'needs_retap.json')[0]
        self.assertEqual((retap['check_idx'], retap['feature_path'], retap['functional_checks_sha256']),
                         (0, 'Home>open', fp2))

    def test_ambiguous_or_malformed_trip_input_cannot_reach_core(self):
        cases = ['mixed', 'unknown', 'not_list', 'not_object', 'invalid_trip_type']
        for case in cases:
            f, _, _ = self.fixture(case)
            edges = read_json(f.ew / 'edge_results.json')
            if case == 'mixed': edges.append({**edges[0], 'device_state': 'trip_1_logged_out'})
            if case == 'unknown': edges[0].pop('device_state')
            if case == 'not_list': edges = {'edges': edges}
            if case == 'not_object': edges = [False]
            if case == 'invalid_trip_type': edges[0]['device_state'] = {}
            write_json(f.ew / 'edge_results.json', edges)
            with self.assertRaises(MigrationError):
                C.inherit_cli(['--dir', str(f.ew)], self.scripts)
            self.assertFalse((f.ew / 'grounding_results.json').exists())

    def test_duplicate_check_names_and_multiple_plan_candidates_remain_debt(self):
        f, meta, _ = self.fixture('duplicate')
        tree = read_json(f.tree); second = copy.deepcopy(tree['pages'][0]['functional_checks'][0])
        second['feature_path'] = 'Home>second'; tree['pages'][0]['functional_checks'].append(second); write_json(f.tree, tree)
        fp = functional_snapshot(tree['pages'][0]); m = read_json(meta); m['functional_checks_sha256'] = fp
        m['checks'][0]['functional_checks_sha256'] = fp
        m['checks'].append({**m['checks'][0], 'idx': 1, 'check_idx': 1, 'feature_path': 'Home>second'})
        write_json(meta, m); self.assertEqual(self.inherit(f), 0)
        self.assertEqual(read_json(f.ew / 'grounding_results.json'), [])
        self.assertEqual(len(read_json(f.ew / 'inherit.native-input.json')['unresolved']), 2)
        f2, meta2, _ = self.fixture('plans')
        plan = read_json(f2.ew / 'walk_plan.json'); step = copy.deepcopy(plan['walks'][0]['steps'][1]); step['step'] = 3
        plan['walks'][0]['steps'].append(step); write_json(f2.ew / 'walk_plan.json', plan)
        m = read_json(meta2); m['checks'][0].update(status='deferred_same_destination', walk_evidence={},
            inherit_from_edge={'from': 'HomeView', 'to': 'LibraryView', 'trigger': None}); write_json(meta2, m)
        self.assertEqual(self.inherit(f2), 0)
        self.assertEqual(read_json(f2.ew / 'grounding_results.json'), [])

    def test_collector_directory_source_plan_and_trigger_identity_are_checked(self):
        for case in ['directory', 'trigger', 'observation_source']:
            f, meta, _ = self.fixture(case); m = read_json(meta)
            if case == 'directory': m['node'] = 'LibraryView'
            if case == 'trigger': m['checks'][0].update(status='deferred_same_destination',
                inherit_from_edge={'from': 'HomeView', 'to': 'LibraryView', 'trigger': 42})
            if case == 'observation_source': m['source_sha256'] = 'unbound source'
            write_json(meta, m)
            with self.assertRaises(MigrationError): self.inherit(f)

    def test_unmapped_inherited_backend_output_is_rejected_before_publication(self):
        f, meta, _ = self.fixture(); m = read_json(meta); m['checks'][0]['status'] = 'not_found'; write_json(meta, m)
        def corrupt(command, args, scripts, **kwargs):
            directory = Path(args[args.index('--dir') + 1])
            write_json(directory / 'grounding_results.json', [{'node': 'HomeView', 'check_idx': 0,
                'check_name': 'Open library', 'evidence_source': 'inherited_from_edge',
                'expected_android': 'CORRUPT TEST OUTPUT', 'android_trusted': True}])
            write_json(directory / 'needs_retap.json', [])
            return subprocess.CompletedProcess([], 0, '', '')
        with patch.object(C, '_core', side_effect=corrupt), self.assertRaises(MigrationError): self.inherit(f)
        self.assertFalse((f.ew / 'grounding_results.json').exists())

    def test_repeat_preserves_existing_gt_without_rebinding_settled_observation(self):
        f, meta, _ = self.fixture()
        self.assertEqual(self.inherit(f), 0)
        prior = read_json(f.ew / 'grounding_results.json')
        m = read_json(meta); m['checks'][0].update(status='settled_by_walk', walk_evidence={}); write_json(meta, m)
        self.assertEqual(self.inherit(f), 0)
        self.assertEqual(read_json(f.ew / 'grounding_results.json'), prior)
        retained = read_json(f.ew / 'inherit.native-input.json')['prior_retained'][0]
        self.assertEqual(retained['state'], 'prior_valid')
        self.assertTrue(retained['prior_retained_without_current_mapping'])

    def test_prior_stale_and_legacy_gt_remain_debt_rejected_by_native_writeback(self):
        for case in ['stale', 'legacy']:
            f, meta, _ = self.fixture(case); self.assertEqual(self.inherit(f), 0)
            path = f.ew / 'grounding_results.json'; prior = read_json(path)
            if case == 'stale':
                tree = read_json(f.tree)
                tree['pages'][0]['functional_checks'][0]['feature_path'] = 'Home>revised'
                write_json(f.tree, tree); fp = functional_snapshot(tree['pages'][0])
                m = read_json(meta); m['functional_checks_sha256'] = fp
                m['checks'][0].update(feature_path='Home>revised', functional_checks_sha256=fp)
            else:
                prior[0].pop('feature_path'); prior[0].pop('functional_checks_sha256'); write_json(path, prior)
                m = read_json(meta)
            m['checks'][0].update(status='settled_by_walk', walk_evidence={}); write_json(meta, m)
            self.assertEqual(self.inherit(f), 0)
            self.assertEqual(read_json(path), prior)
            retained = read_json(f.ew / 'inherit.native-input.json')['prior_retained'][0]
            self.assertEqual(retained['state'], 'prior_stale' if case == 'stale' else 'prior_unbound')
            before = f.tree.read_bytes()
            with self.assertRaises(MigrationError):
                C.tree_write_cli('writeback_walk', ['--tree', str(f.tree), '--grounding', str(path),
                    '--edges', str(f.ew / 'edge_results.json')], self.scripts)
            self.assertEqual(f.tree.read_bytes(), before)

    def test_modified_or_duplicated_prior_unmapped_backend_rows_are_rejected(self):
        for case in ['changed', 'duplicated']:
            f, meta, _ = self.fixture(case); self.assertEqual(self.inherit(f), 0)
            before = (f.ew / 'grounding_results.json').read_bytes()
            m = read_json(meta); m['checks'][0].update(status='settled_by_walk', walk_evidence={}); write_json(meta, m)
            original = C._core
            def corrupt(command, args, scripts, **kwargs):
                result = original(command, args, scripts, **kwargs)
                directory = Path(args[args.index('--dir') + 1]); path = directory / 'grounding_results.json'
                rows = read_json(path)
                if case == 'changed': rows[0]['expected_android'] = 'CORRUPT SYNTHETIC BACKEND OUTPUT'
                else: rows.append(copy.deepcopy(rows[0]))
                write_json(path, rows); return result
            with patch.object(C, '_core', side_effect=corrupt), self.assertRaises(MigrationError): self.inherit(f)
            self.assertEqual((f.ew / 'grounding_results.json').read_bytes(), before)

    def test_retap_fallback_binds_unique_debt_and_retains_ambiguous_conflicting_debt(self):
        from hmigbot_ios152.native_inheritance import bind_retap
        bindings = {('HomeView', 0, 'Open'): {'feature_path': 'Home>open', 'functional_checks_sha256': 'FP'}}
        receipt = {'mapped': [], 'indexed_nodes': ['HomeView']}
        rows = bind_retap([{'node': 'HomeView', 'check_name': 'Open'}], bindings, receipt)
        self.assertEqual(rows[0]['feature_path'], 'Home>open')
        for case in ['unknown', 'ambiguous', 'conflict']:
            current = copy.deepcopy(bindings); row = {'node': 'HomeView', 'check_name': 'Open'}
            if case == 'unknown': row['check_name'] = 'Other'
            if case == 'ambiguous': current[('HomeView', 1, 'Open')] = bindings[('HomeView', 0, 'Open')]
            if case == 'conflict': row['functional_checks_sha256'] = 'OLD'
            before = copy.deepcopy(row); r = {'mapped': [], 'indexed_nodes': ['HomeView']}
            self.assertEqual(bind_retap([row], current, r), [before])
            self.assertEqual(r['unbound_retap'][0]['row'], before)

    def test_plan_optional_hashes_do_not_block_writeback_retap_and_reinherit(self):
        f, meta, _ = self.fixture(); p = f.ew / 'walk_plan.json'; plan = read_json(p)
        tree = read_json(f.tree)
        tree['pages'][0]['functional_checks'].append({'name': 'Open library again',
            'feature_path': 'Home>second', 'expected_ios': None, 'ios_trusted': None})
        write_json(f.tree, tree); fp = functional_snapshot(tree['pages'][0])
        m = read_json(meta); m['functional_checks_sha256'] = fp
        m['checks'][0]['functional_checks_sha256'] = fp
        m['checks'].append({**m['checks'][0], 'idx': 1, 'check_idx': 1,
            'name': 'Open library again', 'check_name': 'Open library again', 'feature_path': 'Home>second',
            'status': 'not_found', 'walk_evidence': {'walk_id': 'neutral_walk', 'step': 3}})
        write_json(meta, m)
        second = copy.deepcopy(plan['walks'][0]['steps'][1]); second.update(step=3, settles_grounding=['Open library again'])
        plan['walks'][0]['steps'].append(second)
        plan.update(tree_sha256=C.sha(f.tree), source_sha256='UNKNOWN ORIGINAL FIELD SEMANTICS')
        write_json(p, plan); self.assertEqual(self.inherit(f), 0)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(C.tree_write_cli('writeback_walk', ['--tree', str(f.tree),
                '--grounding', str(f.ew / 'grounding_results.json'), '--edges', str(f.ew / 'edge_results.json')], self.scripts), 0)
        self.assertNotEqual(C.sha(f.tree), plan['tree_sha256'])
        m['checks'][1]['status'] = 'deferred_to_walk'; write_json(meta, m)
        edges = read_json(f.ew / 'edge_results.json')
        write_json(f.ew / 'edge_results.json', [])
        self.assertEqual(self.inherit(f), 0)
        self.assertEqual(len(read_json(f.ew / 'needs_retap.json')), 1)
        write_json(f.ew / 'edge_results.json', edges)
        self.assertEqual(self.inherit(f), 0)
        self.assertEqual(read_json(f.ew / 'needs_retap.json'), [])
        receipt = read_json(f.ew / 'inherit.native-input.json')
        self.assertEqual(receipt['plan_identity']['declared_fingerprints']['tree_sha256'], plan['tree_sha256'])

    def test_invalid_tree_source_raises_migration_error(self):
        f, _, _ = self.fixture(); tree = read_json(f.tree); tree['source'] = False; write_json(f.tree, tree)
        with self.assertRaises(MigrationError): self.inherit(f)

    def test_all_legacy_directory_core_input_bytes_remain_identical(self):
        f, meta, _ = self.fixture(); m = read_json(meta); m.pop('functional_checks_sha256')
        m['checks'][0].pop('functional_checks_sha256'); m['checks'][0].update(status='deferred_same_destination',
            inherit_from_edge={'from': 'HomeView', 'to': 'LibraryView', 'trigger': None}); write_json(meta, m)
        expected = self.root / 'expected-wire'
        for path in f.ew.rglob('*.json'):
            write_json(expected / path.relative_to(f.ew), C.legacy_wire(read_json(path)))
        original = C._core; inputs = []
        def record(command, args, scripts, **kwargs):
            directory = Path(args[args.index('--dir') + 1])
            inputs.append({str(p.relative_to(directory)): p.read_bytes() for p in directory.rglob('*.json')})
            return original(command, args, scripts, **kwargs)
        with patch.object(C, '_core', side_effect=record): self.assertEqual(self.inherit(f), 0)
        self.assertEqual(inputs[0], {str(p.relative_to(expected)): p.read_bytes() for p in expected.rglob('*.json')})
        self.assertFalse((f.ew / 'inherit.native-input.json').exists())


class SameDestinationCollector(unittest.TestCase):
    def test_original_disposition_and_edge_binding_survive_native_collection(self):
        from hmigbot_ios152 import native_visual as V
        from evaluations.test_native_verify38 import source_tree, FixtureObserver
        tree = source_tree(); page = tree['pages'][0]
        inherit = {'from': 'Neutral', 'to': 'Detail', 'trigger': None}
        plan = {'functional_checks_sha256': V.functional_snapshot(page), 'checks': [
            {'check_idx': 0, 'feature_path': 'Form>A', 'disposition': 'deferred_same_destination',
             'inherit_from_edge': inherit},
            {'check_idx': 1, 'feature_path': 'Form>B', 'disposition': 'input_field_no_tap'}]}
        with tempfile.TemporaryDirectory(prefix='native41-collector-') as directory:
            observer = FixtureObserver()
            V.sweep(observer, tree, 'Neutral', plan, Path(directory) / 'valid', project=directory)
            meta = read_json(Path(directory) / 'valid/run_meta.json')
            self.assertEqual(meta['checks'][0]['status'], 'deferred_same_destination')
            self.assertEqual(meta['checks'][0]['inherit_from_edge'], inherit)
            self.assertEqual(meta['checks'][0]['feature_path'], 'Form>A')
            self.assertEqual(observer.values, {'A': 0, 'B': 0})
            bad = copy.deepcopy(plan); bad['checks'][0]['inherit_from_edge']['from'] = 'Other'
            with self.assertRaises(MigrationError):
                V.sweep(FixtureObserver(), tree, 'Neutral', bad, Path(directory) / 'invalid', project=directory)


if __name__ == '__main__':
    unittest.main()
