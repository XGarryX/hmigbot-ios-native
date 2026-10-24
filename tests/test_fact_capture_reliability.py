"""Provider captures must be retryable after failure without losing or inventing evidence."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.atoms import run_atom
from hmigbot_ios.core import MigrationError, digest, read_json, snapshot, write_json
from hmigbot_ios.ios_facts import extract, obligations, refresh, validate_graph
from hmigbot_ios.provider_runs import ProviderRun, capture_root, retained_failures

STORYBOARD = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB">\n'
              '  <connections>\n'
              '    <action selector="tap:" id="xYz-01-abc"/>\n'
              '    <segue id="pQr-02-def" kind="show"/>\n'
              '  </connections>\n'
              '</document>\n')


class ProviderRunTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        (self.source / 'App.swift').write_text('import SwiftUI\nstruct App { @State var count = 0 }\n', encoding='utf-8')
        (self.source / 'Main.storyboard').write_text(STORYBOARD, encoding='utf-8')
        self.project = self.root / 'project'
        self.project.mkdir()

    def plan(self, providers):
        path = self.root / ('plan-%d.json' % len(list(self.root.glob('plan-*.json'))))
        write_json(path, {'schema_version': 2, 'providers': providers})
        return path

    def attempts(self, operation='interface-builder'):
        root = capture_root(self.project) / operation
        found = []
        for record in sorted(root.rglob('run.json')) if root.is_dir() else []:
            attempt = record.parent
            found.append((attempt.parent.name, attempt.name, attempt))
        return found

    def test_failure_then_retry_gets_a_new_attempt_and_keeps_the_original(self):
        config = self.root / 'invalid-syntax-config.json'
        write_json(config, {})  # structurally valid plan; real provider rejects incomplete config
        plan = self.plan([{'operation': 'swift-syntax', 'config': str(config)}])
        with self.assertRaises(MigrationError) as first:
            refresh(self.project, self.source, provider_plan=plan)
        with self.assertRaises(MigrationError) as second:
            refresh(self.project, self.source, provider_plan=plan)
        self.assertNotIn('immutable', str(first.exception))
        self.assertNotEqual(str(first.exception), str(second.exception), 'retry must not point at the same directory')
        failures = sorted((capture_root(self.project) / 'swift-syntax').rglob('failure.json'))
        self.assertEqual(len(failures), 2, 'a retained failure must never block a retry, and must not be deleted')
        records = [read_json(path) for path in failures]
        self.assertEqual([r['attempt'] for r in records], [1, 2])
        self.assertNotEqual(records[0]['run_id'], records[1]['run_id'], 'each try needs its own run id')
        self.assertEqual(len({r['run_id'] for r in records}), 2)
        for record, path in zip(records, failures):
            self.assertEqual(record['status'], 'failed')
            self.assertEqual(record['source_sha256'], snapshot(self.source)['sha256'])
            self.assertEqual(record['identity'], path.parent.parent.name)
            self.assertIn('error', record)
        self.assertFalse(list(capture_root(self.project).rglob('artifact.json')), 'a failure cannot publish evidence')
        self.assertFalse((self.project / 'spec/baseline/ios-facts.json').exists())

    def test_success_is_immutable_and_fresh_attempts_do_not_reuse_unpinned_tool_identity(self):
        plan = self.plan([{'operation': 'interface-builder'}])
        graph = refresh(self.project, self.source, provider_plan=plan)
        self.assertEqual(len(graph['provider_artifacts']), 1)
        artifact = graph['provider_artifacts'][0]
        self.assertEqual(artifact['run']['attempt'], 1)
        self.assertTrue(artifact['path'].endswith('/artifact.json'))
        self.assertEqual(read_json(self.project / artifact['path'])['source_sha256'], graph['source_sha256'])
        first_bytes = (self.project / artifact['path']).read_bytes()
        again = refresh(self.project, self.source, provider_plan=plan)
        self.assertNotEqual(again['provider_artifacts'], [artifact], 'tool identity is not pinned, so capture must run again')
        self.assertEqual(again['provider_artifacts'][0]['run']['attempt'], 2)
        self.assertEqual((self.project / artifact['path']).read_bytes(), first_bytes)
        self.assertEqual(len(self.attempts()), 2, 'fresh captures keep the old successful evidence')
        validate_graph(self.source, self.project)  # round trip still verifies
        # A different configuration fingerprint is a different request, so it cannot reuse attempt 1.
        config = self.root / 'provider.json'
        write_json(config, {'executable': ['fixture']})
        other = refresh(self.project, self.source, provider_plan=self.plan([{'operation': 'interface-builder', 'config': str(config)}]))
        self.assertEqual(other['provider_artifacts'][0]['run']['identity'], artifact['run']['identity'], 'unconsumed config cannot change identity')
        self.assertEqual(len(self.attempts()), 3, 'each fingerprint keeps its own attempt history')
        self.assertEqual(other['provider_artifacts'][0]['run']['attempt'], 3, 'same consumed inputs retain their attempt history')

    def test_graph_only_references_successes_and_failure_keeps_previous_baseline(self):
        good = self.plan([{'operation': 'interface-builder'}])
        published = refresh(self.project, self.source, provider_plan=good)
        baseline = self.project / 'spec/baseline/ios-facts.json'
        before = baseline.read_bytes()
        config = self.root / 'invalid-clang-config.json'
        write_json(config, {})  # execution failure, rather than whole-plan preflight failure
        mixed = self.plan([{'operation': 'interface-builder'}, {'operation': 'clang-ast', 'config': str(config)}])
        with self.assertRaises(MigrationError):
            refresh(self.project, self.source, provider_plan=mixed)
        self.assertEqual(baseline.read_bytes(), before, 'a partially failed plan must not publish a new graph')
        self.assertEqual(read_json(baseline), published)
        validate_graph(self.source, self.project)
        text = baseline.read_bytes().decode('utf-8')
        self.assertNotIn('clang-ast', text, 'the graph must not reference the capture that failed')
        self.assertTrue(list((capture_root(self.project) / 'clang-ast').rglob('failure.json')))
        self.assertFalse(list((capture_root(self.project) / 'clang-ast').rglob('artifact.json')))

    def test_retry_after_failure_keeps_the_original_problem_visible(self):
        config = self.root / 'syntax-provider.json'
        write_json(config, {'executable': ['fixture-interface-builder']})
        plan = self.plan([{'operation': 'interface-builder', 'config': str(config)}])
        with mock.patch('hmigbot_ios.atoms.run_atom',
                        side_effect=MigrationError('fixture: provider executable missing')):
            with self.assertRaises(MigrationError):
                refresh(self.project, self.source, provider_plan=plan)
        graph = refresh(self.project, self.source, provider_plan=plan)  # the real atom now runs
        self.assertEqual(graph['provider_artifacts'][0]['run']['attempt'], 2)
        retries = [i for i in graph['issues'] if i['rule'] == 'IOS.PROVIDER_RETRY']
        self.assertEqual(len(retries), 1)
        self.assertEqual(retries[0]['detail']['attempt'], 1)
        self.assertIn('provider executable missing', retries[0]['detail']['error'])
        validated, _ = validate_graph(self.source, self.project)
        self.assertEqual(validated, graph)
        # Deleting the retry finding from the published graph is detected, not quietly accepted.
        stale = dict(graph)
        stale['issues'] = [i for i in graph['issues'] if i['rule'] != 'IOS.PROVIDER_RETRY']
        write_json(self.project / 'spec/baseline/ios-facts.json', stale)
        with self.assertRaises(MigrationError):
            validate_graph(self.source, self.project)

    def test_source_change_during_capture_is_not_published(self):
        plan = self.plan([{'operation': 'interface-builder'}])
        graph = refresh(self.project, self.source, provider_plan=plan)
        # A fresh fingerprint is required here: a reused success never re-runs the provider.
        config = self.root / 'drift-provider.json'
        write_json(config, {'executable': ['fixture']})
        drifting_plan = self.plan([{'operation': 'interface-builder', 'config': str(config)}])
        baseline = self.project / 'spec/baseline/ios-facts.json'
        obligations_path = self.project / 'spec/baseline/ios-obligations.json'
        before, before_obligations = baseline.read_bytes(), obligations_path.read_bytes()
        real = run_atom

        def drifting(operation, root, output, **kwargs):
            (root / 'Late.swift').write_text('struct Late { var added = 1 }\n', encoding='utf-8')
            return real(operation, root, output, **kwargs)

        with mock.patch('hmigbot_ios.atoms.run_atom', side_effect=drifting):
            with self.assertRaises(MigrationError) as raised:
                refresh(self.project, self.source, provider_plan=drifting_plan)
        self.assertIn('Source changed while extracting', str(raised.exception))
        self.assertEqual(baseline.read_bytes(), before, 'an invalid graph must not replace the baseline')
        self.assertEqual(obligations_path.read_bytes(), before_obligations)
        self.assertIn('Late.swift', [f['path'] for f in snapshot(self.source)['files']])
        with self.assertRaises(MigrationError):
            validate_graph(self.source, self.project)  # the kept graph is honestly stale, not silently trusted
        drifted = refresh(self.project, self.source, provider_plan=drifting_plan)
        self.assertNotEqual(drifted['source_sha256'], graph['source_sha256'], 'the drift must change the snapshot')
        self.assertEqual(read_json(baseline), drifted, 'a stable re-extract publishes and then validates')
        self.assertEqual(drifted['provider_artifacts'][0]['run']['attempt'], 1)
        captured = self.attempts()
        self.assertEqual(len({identity for identity, _, _ in captured}), 2,
                         'source state and actually consumed inputs define identity; ignored config does not')
        self.assertEqual({read_json(path / 'run.json')['source_sha256'] for _, _, path in captured},
                         {graph['source_sha256'], drifted['source_sha256']},
                         'a stale source state stays in its own directory instead of being reused')
        referenced = self.project / drifted['provider_artifacts'][0]['path']
        self.assertEqual(read_json(referenced.parent / 'run.json')['source_sha256'], drifted['source_sha256'])
        validate_graph(self.source, self.project)

    def test_attempt_records_carry_provenance_and_no_invented_usage(self):
        plan = self.plan([{'operation': 'interface-builder'}])
        graph = refresh(self.project, self.source, provider_plan=plan)
        attempt = self.attempts()[0][2]
        record = read_json(attempt / 'run.json')
        allowed = {'schema_version', 'status', 'operation', 'source_sha256', 'identity', 'attempt', 'run_id',
                   'config_sha256', 'input_sha256', 'artifact', 'artifact_sha256', 'artifact_status', 'atom_issue_count', 'prior_failures'}
        self.assertTrue(set(record) <= allowed, f'unknown provenance fields: {set(record) - allowed}')
        for forbidden in ('model', 'tokens', 'usage', 'cost', 'duration_ms'):
            self.assertNotIn(forbidden, record)
        self.assertEqual(record['artifact_sha256'], graph['provider_artifacts'][0]['sha256'])
        self.assertEqual(record['config_sha256'], None, 'an absent config must not be fingerprinted as a value')
        report = read_json(attempt / 'artifact.json')
        self.assertEqual(digest((attempt / 'artifact.json').read_bytes()), record['artifact_sha256'])
        self.assertEqual(report['source_sha256'], graph['source_sha256'])

    def test_legacy_flat_capture_still_validates(self):
        """Graphs published before the attempt layout keep re-verifying, with failures beside them."""
        graph = extract(self.source)
        legacy = capture_root(self.project) / 'interface-builder' / graph['source_sha256']
        report = run_atom('interface-builder', self.source, legacy)
        data = (legacy / 'artifact.json').read_bytes()
        graph['provider_artifacts'] = [{'path': (legacy / 'artifact.json').relative_to(self.project).as_posix(),
                                        'sha256': digest(data), 'operation': 'interface-builder'}]
        write_json(legacy / 'failure.json', {'operation': 'interface-builder', 'status': 'failed',
                                             'source_sha256': graph['source_sha256'], 'error': 'legacy fixture'})
        write_json(self.project / 'spec/baseline/ios-facts.json', graph)
        write_json(self.project / 'spec/baseline/ios-obligations.json', obligations(graph))
        self.assertEqual(retained_failures(legacy / 'artifact.json'), [],
                         'a legacy flat path has no attempt siblings to promote into issues')
        validated, expected = validate_graph(self.source, self.project)
        self.assertEqual(validated, graph)
        self.assertEqual(read_json(self.project / 'spec/baseline/ios-obligations.json'), expected)
        tampered = dict(graph)
        tampered['provider_artifacts'] = [dict(graph['provider_artifacts'][0], sha256='0' * 64)]
        write_json(self.project / 'spec/baseline/ios-facts.json', tampered)
        with self.assertRaises(MigrationError):
            validate_graph(self.source, self.project)

    def test_run_identity_follows_input_and_config_fingerprints(self):
        config = self.root / 'cfg-a.json'
        write_json(config, {'executable': ['a']})
        other = self.root / 'cfg-b.json'
        write_json(other, {'executable': ['b']})
        source_sha = snapshot(self.source)['sha256']
        base = ProviderRun(self.project, 'swift-syntax', source_sha)
        with_a = ProviderRun(self.project, 'swift-syntax', source_sha, config=config)
        with_b = ProviderRun(self.project, 'swift-syntax', source_sha, config=other)
        self.assertNotEqual(with_a.identity, with_b.identity)
        self.assertNotEqual(with_a.identity, base.identity)
        missing = self.root / 'absent.json'
        self.assertEqual(ProviderRun(self.project, 'swift-syntax', source_sha, config=missing).identity, base.identity,
                         'an unreadable config has no content to fingerprint; the atom must still fail explicitly')
        self.assertIsNone(ProviderRun(self.project, 'swift-syntax', source_sha, config=missing).config_sha256)
        self.assertEqual(base.attempt, 1)
        self.assertEqual(len(base.run_id), 12)


if __name__ == '__main__':
    unittest.main()
