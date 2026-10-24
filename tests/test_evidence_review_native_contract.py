"""Independent adversarial checks for derived runtime and landing claims."""
import copy
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.core import digest, json_bytes, read_json, write_json
from hmigbot_ios.behavior import verify
from hmigbot_ios.ios_scheduler import generate, step
from hmigbot_ios.quality_views import summary
from test_ios_harness import fixture


class EvidenceReviewTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='evidence-review-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source, self.project, self.graph = fixture(self.root)

    def land_counter(self):
        output = 'entry/Counter.ets'
        request = self.root / 'request.json'
        write_json(request, {'schema_version': 2, 'wave': 'domains',
            'graph_sha256': digest(json_bytes(self.graph)), 'tasks': [{
                'id': 'counter', 'role': 'a2h-ios-converter', 'goal': 'Implement counter',
                'ownership': [output], 'ac_ids': ['F001-AC01'],
                'fact_ids': [fact['id'] for fact in self.graph['facts']], 'parents': []}]})
        generate(self.project, request)
        action, code = step(self.project, 'domains')
        self.assertEqual(code, 0)
        task = action['batch'][0]
        target = self.project / output
        target.parent.mkdir(parents=True)
        target.write_text('export class Counter { count:number=0; add():void { this.count+=1; } }', encoding='utf-8')
        write_json(self.project / task['result_path'], {
            'ios_receipt_version': 2, 'source_sha256': self.graph['source_sha256'],
            'plan_sha256': digest((self.project / 'spec/waves/plan-domains.json').read_bytes()),
            'task_id': 'counter', 'status': 'generated', 'behavior_verified': False,
            'file_hashes': {output: digest(target.read_bytes())}, 'ac_ids': ['F001-AC01'],
            'findings': [], 'final_state': 'PASS', 'task': 'counter', 'files_touched': [output],
            'files': [output], 'fixed': [], 'unresolved': [], 'domain': 'counter', 'skipped': []})
        self.assertEqual(step(self.project, 'domains', landing=True)[1], 0)
        self.assertEqual(summary(self.project)['axes']['generation']['status'], 'generated')

    def test_behavior_report_cannot_override_failed_stdout(self):
        feature = self.project / 'spec/baseline/features/F001-counter.md'
        feature.write_text(feature.read_text(encoding='utf-8').replace('判:ui', '判:unit'), encoding='utf-8')
        target = self.project / 'counter.py'
        target.write_text('def add():\n    return 0\nprint(add())\n', encoding='utf-8')
        node = {'path': 'counter.py', 'line': 1, 'symbol': 'add', 'sha256': digest(target.read_bytes())}
        events = [fact for fact in self.graph['facts'] if fact['kind'] == 'event']
        spec = {'schema_version': 2, 'source_sha256': self.graph['source_sha256'],
            'chains': [{'source_fact': fact['id'], **{key: node for key in ('input', 'processing', 'feedback')},
                        'review': {'status': 'reviewed', 'reviewer': 'source-reader'}} for fact in events],
            'cases': [{'id': 'add', 'ac_ids': ['F001-AC01'], 'runner': 'unit',
                'oracle': {'source_fact': events[0]['id'], 'expected': 1, 'reviewer': 'source-reader'},
                'target_hashes': {'counter.py': digest(target.read_bytes())},
                'command': [sys.executable, 'counter.py']}]}
        write_json(self.project / 'spec/verification/ios-behavior.json', spec)
        report, code = verify(self.project, self.source, self.graph, {'F001-AC01': {'judgment': 'unit'}}, run=True)
        self.assertEqual(code, 2, report)
        self.assertEqual(report['observations'][0]['actual'], 0)
        self.assertEqual((self.project / 'spec/reports/behavior/add/stdout.log').read_text().strip(), '0')
        # A stage summary author must not be able to turn the failed evidence
        # into a PASS by editing only derived report fields.
        report.update(status='PASS', behavior_verified=True, failures=[], unverified_ac_ids=[])
        report['observations'][0].update(status='observed_pass', actual=1)
        write_json(self.project / 'spec/reports/ios-behavior-check.json', report)
        result = summary(self.project)
        self.assertNotEqual(result['axes']['behavior']['status'], 'passed')
        self.assertFalse(result['behavior_verified'])

    def test_generation_requires_current_original_run_and_dispatch_identity(self):
        self.land_counter()
        journal_path = self.project / 'spec/state/journal.json'
        dispatch_path = self.project / 'spec/state/dispatch.json'
        journal, dispatch = read_json(journal_path), read_json(dispatch_path)
        if os.name == 'nt':
            # The real original binary now records an extended Windows plan
            # address. Its ordinary spelling must identify that same run.
            original_path = dispatch['waves']['domains']['plan_path'].replace('\\', '/')
            self.assertTrue(original_path.startswith('//?/'), original_path)
            ordinary = str((self.project / 'spec/waves/plan-domains.json').resolve())
            plain_journal, plain_dispatch = copy.deepcopy(journal), copy.deepcopy(dispatch)
            plain_journal['workflow_status'][0]['plan_path'] = ordinary
            plain_dispatch['waves']['domains']['plan_path'] = ordinary
            def read_plain(path):
                if Path(path).resolve() == journal_path.resolve(): return plain_journal
                if Path(path).resolve() == dispatch_path.resolve(): return plain_dispatch
                return read_json(path)
            with patch('hmigbot_ios.page_evidence.read_json', side_effect=read_plain):
                self.assertEqual(summary(self.project)['axes']['generation']['status'], 'generated')
        mutations = [
            ('missing workflow identity', lambda j, d: j.update(workflow_status=[])),
            ('wrong journal contract', lambda j, d: j['workflow_status'][0].update(contract_hash='sha256:' + '0' * 64)),
            ('wrong journal plan', lambda j, d: j['workflow_status'][0].update(plan_path='elsewhere/plan-domains.json')),
            ('missing dispatch identity', lambda j, d: d.update(waves={})),
            ('wrong dispatch contract', lambda j, d: d['waves']['domains'].update(contract_hash='sha256:' + '0' * 64)),
            ('wrong dispatch plan', lambda j, d: d['waves']['domains'].update(plan_path='elsewhere/plan-domains.json')),
            ('wrong extended journal plan', lambda j, d: j['workflow_status'][0].update(
                plan_path='\\\\?\\' + str(self.root / 'elsewhere/plan-domains.json'))),
            ('wrong extended dispatch plan', lambda j, d: d['waves']['domains'].update(
                plan_path='\\\\?\\' + str(self.root / 'elsewhere/plan-domains.json'))),
            ('unlanded new attempt', lambda j, d: d['waves']['domains']['dispatched']['counter'].update(attempts=2)),
            ('wrong resume key', lambda j, d: d['waves']['domains']['dispatched']['counter'].update(resume_key='domains:other')),
        ]
        for label, mutate in mutations:
            with self.subTest(label=label):
                changed_journal, changed_dispatch = copy.deepcopy(journal), copy.deepcopy(dispatch)
                mutate(changed_journal, changed_dispatch)
                def read_evidence(path):
                    if Path(path).resolve() == journal_path.resolve(): return changed_journal
                    if Path(path).resolve() == dispatch_path.resolve(): return changed_dispatch
                    return read_json(path)
                # Pure reader injection; no test writes the original state
                # ledgers or substitutes a new landing algorithm.
                with patch('hmigbot_ios.page_evidence.read_json', side_effect=read_evidence):
                    self.assertNotEqual(summary(self.project)['axes']['generation']['status'], 'generated')

    def test_slice_page_associations_do_not_distribute_all_ac_to_every_page(self):
        import test_plan_contract as plan_fixtures
        from hmigbot_ios.page_evidence import pages
        planned = plan_fixtures.PlanContractTests('test_valid_explicit_merge_and_transitive_consumer')
        planned.setUp()
        self.addCleanup(planned.tearDown)
        (planned.base / 'ui/page_0002_Other.md').write_text('# page_0002\n## Acceptance\nF001-AC02\n', encoding='utf-8')
        planned.items[2]['page_ids'] = ['page_0001', 'page_0002']
        planned.items[2]['ac_ids'] = ['F001-AC01', 'F001-AC02']
        planned.items.append({'item_id': 'UI:PAGE-0002', 'ac_ids': ['F001-AC02'],
            'ownership': ['entry/Other.ets'], 'parents': ['BASE:Base-0'], 'page_ids': ['page_0002'],
            'scope': 'product', 'verification': 'generated'})
        planned.write_plans()
        axes = {'generation': {'status': 'not_run'}, 'compilation': {'status': 'not_run'},
                'behavior': {'status': 'failed', 'ac_statuses': {'F001-AC01': 'passed', 'F001-AC02': 'failed'}}}
        report = pages(planned.project, {'F001-AC01': {}, 'F001-AC02': {}}, axes, [], {})
        by_page = {page['page_id']: page for page in report}
        self.assertEqual(by_page['page_0001']['ac_ids'], ['F001-AC01'])
        self.assertEqual(by_page['page_0001']['axes']['behavior']['status'], 'passed')
        self.assertEqual(by_page['page_0002']['ac_ids'], ['F001-AC02'])
        self.assertEqual(by_page['page_0002']['axes']['behavior']['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
