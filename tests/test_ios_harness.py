"""Adversarial contracts and real upstream four-beat scheduling in isolated projects."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.core import MigrationError, digest, json_bytes, read_json, write_json
from hmigbot_ios.native_pipeline import configure, index_source
from hmigbot_ios.native_semantics import required_facts
from hmigbot_ios.ios_facts import extract, refresh, validate_graph, RULES
from hmigbot_ios.ios_harness import initialize, check
from hmigbot_ios.ios_scheduler import generate, step, replan
from hmigbot_ios.native_pipeline import refresh_source_index
from hmigbot_ios.behavior import verify
from hmigbot_ios.ios_literals import run as literal_index


def fixture(root, source_suffix='', *, resources=None):
    source, project = root / 'source', root / 'target'
    source.mkdir(); project.mkdir()
    (source / 'Counter.swift').write_text('''import SwiftUI
struct Counter: View {
    @State private var count: Int = 0
    var body: some View {
        VStack {
            Text("Count: \\(count)")
            Button("Add") { count += 1 }
        }
    }
}
''' + source_suffix, encoding='utf-8')
    for relative, data in (resources or {}).items():
        resource = source / relative
        resource.parent.mkdir(parents=True, exist_ok=True)
        resource.write_bytes(data)
    configure(source, project); initialize(project); index_source(project)
    base = project / 'spec/baseline'
    for folder, name, ident in [('features', 'F001-counter.md', 'F001'), ('ui', 'page_0001_Counter.md', 'page_0001')]:
        (base / folder).mkdir(parents=True)
        text = f'---\nsource_platform: ios\nsource_anchors:\n  - path: Counter.swift\n---\n# {ident}\n'
        if folder == 'features':
            text += '- [ ] F001-AC01 从初值0点击递增后可见Count:1 `判:ui | 真:src:Counter.swift:7`\n'
        (base / folder / name).write_text(text, encoding='utf-8')
    from spec_contract_fixture import complete_contract
    complete_contract(project)
    graph = refresh(project, source)
    literal_index(project)
    docs = []
    for ident, kind in [('F001', 'feature'), ('page_0001', 'page')]:
        facts = {}
        for dimension in required_facts(kind, {'swift'}, {'swiftui'}):
            relevant = [f for f in graph['facts'] if dimension in RULES[f['kind']]['dimensions']]
            if relevant:
                value = {'summary': 'Counter source behavior reviewed'}
                if dimension == 'state_ownership':
                    value = {'states': [{'fact_id': f['id'], 'owner': f['owner'], **f['value']} for f in relevant if f['kind'] == 'state']}
                facts[dimension] = {'status': 'known', 'value': value, 'fact_ids': [f['id'] for f in relevant],
                                    'evidence': [{'path': f['anchor']['path'], 'line': f['anchor']['line']} for f in relevant]}
            else:
                facts[dimension] = {'status': 'not_applicable', 'reason': 'Counter fixture has no source operation in this dimension; full ten-line file reviewed'}
        docs.append({'id': ident, 'kind': kind, 'languages': ['swift'], 'frameworks': ['swiftui'], 'facts': facts})
    write_json(base / 'ios-semantics.json', {'schema_version': 2, 'source_platform': 'ios', 'documents': docs})
    obs = read_json(base / 'ios-obligations.json')
    write_json(base / 'ios-coverage.json', {'schema_version': 2, 'graph_sha256': digest(json_bytes(graph)),
        'mappings': [{'obligation_id': o['id'], 'ac_ids': ['F001-AC01'],
            'source_review': {'status': 'reviewed', 'input': 'Tap Add', 'processing': 'Increment count by one', 'observable': 'Count text changes', 'reviewer': 'fixture-source-reader'}} for o in obs['obligations']]})
    from hmigbot_ios.expertise import prepare, record
    prepare(project)
    plan = read_json(project / 'spec/ref/ios-expertise-plan.json')
    request = root / 'fixture-expertise.json'
    write_json(request, {'plan_sha256': digest(json_bytes(plan)), 'reviews': [
        {'id': r['id'], 'resources': r['resources'], 'status': 'reviewed', 'reviewer': 'fixture-source-reader',
         'observations': [{'source': {'path': p, 'line': 1}, 'interpretation': 'Fixture source owns counter state and updates visible text on button input.', 'unknowns': []} for p in r['source_paths']]}
        for r in plan['reviews']]})
    record(project, request)
    return source, project, graph


class HarnessTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='iOS harness 测试 ')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.source, self.project, self.graph = fixture(self.root)

    def mutate_semantics(self, update):
        path = self.project / 'spec/baseline/ios-semantics.json'
        data = read_json(path); update(data); write_json(path, data)

    def rules(self):
        return [f['rule'] for f in check(self.project)[0]['findings']]

    def test_report_only_harness_preserves_existing_findings_and_creates_no_report(self):
        from hmigbot_ios.native_pipeline import findings_module
        queue = findings_module()
        marker = queue.make('IOS.SENTINEL', 'spec', 'preserve', 'Pending prior evidence')
        queue.replace_section(str(self.project), 'spec.ios-harness', [marker])
        before = {p.relative_to(self.project).as_posix(): p.read_bytes()
                  for p in self.project.rglob('*') if p.is_file()}
        report, code = check(self.project, report_only=True)
        self.assertEqual(code, 0, report)
        after = {p.relative_to(self.project).as_posix(): p.read_bytes()
                 for p in self.project.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_reviewed_contract_is_not_behavior_pass(self):
        report, code = check(self.project)
        self.assertEqual(code, 0, report)
        self.assertFalse(report['behavior_verified'])

    def test_all_not_applicable_cannot_hide_source_signals(self):
        def update(data):
            for doc in data['documents']:
                for key in doc['facts']:
                    doc['facts'][key] = {'status': 'not_applicable', 'reason': 'Already handled'}
        self.mutate_semantics(update)
        self.assertIn('IOS.NA_CONTRADICTION', self.rules())

    def test_true_line_with_false_initializer_fails(self):
        def update(data):
            data['documents'][1]['facts']['state_ownership']['value']['states'][0]['initializer'] = '999'
        self.mutate_semantics(update)
        self.assertIn('IOS.STATE_VALUE_CONTRADICTION', self.rules())

    def test_stable_fact_id_survives_comment_insertion(self):
        initial = next(f['id'] for f in self.graph['facts'] if f['kind'] == 'state')
        path = self.source / 'Counter.swift'
        path.write_text('// leading comment\n' + path.read_text(encoding='utf-8'), encoding='utf-8')
        graph = extract(self.source)
        self.assertEqual(next(f['id'] for f in graph['facts'] if f['kind'] == 'state'), initial)
        self.assertNotEqual(graph['source_sha256'], self.graph['source_sha256'])

    def test_multiline_state_and_unicode_unknown_are_explicit(self):
        path = self.source / 'Counter.swift'
        path.write_text('import SwiftUI\nstruct Counter: View {\n @State\n private var count = 0\n}\n', encoding='utf-8')
        graph = extract(self.source)
        state = next(f for f in graph['facts'] if f['kind'] == 'state')
        self.assertEqual(state['value']['initializer'], '0')
        path.write_text('struct Counter { var 数量 = 0 }', encoding='utf-8')
        self.assertIn('IOS.TOKEN_IDENTIFIER_UNRESOLVED', [i['rule'] for i in extract(self.source)['issues']])

    def test_source_refresh_requires_explicit_review(self):
        path = self.source / 'Counter.swift'; path.write_text(path.read_text(encoding='utf-8') + '\n// reviewed change\n', encoding='utf-8')
        graph = refresh(self.project, self.source)
        review = self.root / 'refresh-review.json'; write_json(review, {'source_sha256': graph['source_sha256']})
        with self.assertRaises(MigrationError): refresh_source_index(self.project, review)
        write_json(review, {'source_sha256': graph['source_sha256'], 'previous_source_sha256': self.graph['source_sha256'], 'reviewer': 'fixture', 'reason': 'Only a trailing comment; still recheck all pinned contracts'})
        report = refresh_source_index(self.project, review)
        self.assertFalse(report['spec_complete'])
        self.assertTrue((Path(report['archive']) / 'ios-source-index.json').exists())

    def test_provider_failure_retains_diagnostics(self):
        plan = self.root / 'providers.json'
        config = self.root / 'invalid-syntax-config.json'
        write_json(config, {})  # valid plan; the real provider rejects incomplete config
        write_json(plan, {'schema_version': 2, 'providers': [{'operation': 'swift-syntax', 'config': str(config)}]})
        with self.assertRaises(MigrationError): refresh(self.project, self.source, provider_plan=plan)
        self.assertTrue(list((self.project / 'spec/ref/provider-runs').rglob('failure.json')))

    def test_generic_known_claim_import_line_fails(self):
        def update(data):
            for doc in data['documents']:
                for key in doc['facts']:
                    doc['facts'][key] = {'status': 'known', 'value': 'Already handled correctly.', 'evidence': [{'path': 'Counter.swift', 'line': 1}]}
        self.mutate_semantics(update)
        self.assertIn('IOS.CLAIM_FACT_LINK', self.rules())

    def test_missing_obligation_and_weak_oracle_fail(self):
        path = self.project / 'spec/baseline/ios-coverage.json'
        data = read_json(path); data['mappings'].pop(); write_json(path, data)
        self.assertIn('IOS.OBLIGATION_UNCOVERED', self.rules())
        feature = self.project / 'spec/baseline/features/F001-counter.md'
        feature.write_text(feature.read_text(encoding='utf-8').replace('判:ui', '判:static'), encoding='utf-8')
        self.assertIn('IOS.ORACLE_TOO_WEAK', self.rules())

    def test_literal_index_is_source_backed_and_preserves_dynamic_text(self):
        data = literal_index(self.project)
        self.assertEqual(data['files_scanned'], 1)
        self.assertIn('Add', [v['value'] for v in data['texts']])
        self.assertTrue(data['dynamic_texts'])
        self.assertIn(0, [v['value'] for v in data['numeric_constants']])
        path = self.project / 'spec/baseline/literal-ledger.json'; data['texts'] = []; write_json(path, data)
        self.assertIn('IOS.HARNESS_CONTRACT', self.rules())

    def test_stale_or_hand_edited_facts_fail(self):
        path = self.project / 'spec/baseline/ios-facts.json'
        data = read_json(path); data['facts'][0]['owner'] = 'Invented'; write_json(path, data)
        with self.assertRaises(MigrationError): validate_graph(self.source, self.project)
        refresh(self.project, self.source)
        (self.source / 'Counter.swift').write_text('struct Different {}')
        self.assertIn('IOS.HARNESS_CONTRACT', self.rules())

    def test_comments_and_strings_do_not_add_fake_signals(self):
        path = self.source / 'Counter.swift'
        before = len(extract(self.source)['facts'])
        path.write_text(path.read_text(encoding='utf-8') + '\n// Task cancel UserDefaults Button\nlet note = "Button Task UserDefaults"\n', encoding='utf-8')
        after = extract(self.source)['facts']
        self.assertFalse(any(f['kind'] in {'task', 'persistence'} for f in after))
        self.assertEqual(len(after), before + 1)  # only the real string assignment

    def test_legacy_import_preserves_ids_but_never_inherits_pass(self):
        path = self.project / 'spec/baseline/ios-semantics.json'
        data = read_json(path); data['schema_version'] = 1; write_json(path, data)
        with self.assertRaises(MigrationError): initialize(self.project)
        result = initialize(self.project, import_legacy=True)
        self.assertFalse(result['legacy_pass_inherited'])
        self.assertEqual(read_json(path)['documents'][0]['id'], 'F001')
        self.assertIn('IOS.NATIVE_FACT_UNKNOWN', self.rules())

    def plan_request(self):
        return {'schema_version': 2, 'wave': 'domains', 'graph_sha256': digest(json_bytes(self.graph)),
                'tasks': [{'id': 'counter', 'role': 'a2h-ios-converter', 'goal': 'Implement visible counter update',
                           'ownership': ['entry/src/main/ets/pages/Counter.ets'], 'ac_ids': ['F001-AC01'],
                           'fact_ids': [f['id'] for f in self.graph['facts']], 'parents': []}]}

    def test_cycle_ownership_and_missing_ac_are_blocked(self):
        req = self.plan_request(); req['tasks'][0]['parents'] = ['counter']
        path = self.root / 'request.json'; write_json(path, req)
        with self.assertRaises(MigrationError): generate(self.project, path)
        req['tasks'][0]['parents'] = []; req['tasks'][0]['ownership'] = ['spec/state/state.json']; write_json(path, req)
        with self.assertRaises(MigrationError): generate(self.project, path)
        req['tasks'][0]['ownership'] = ['.MIGBOT/config.json']; write_json(path, req)
        with self.assertRaises(MigrationError): generate(self.project, path)
        req = self.plan_request(); second = {**req['tasks'][0], 'id': 'second', 'ownership': ['entry/src/main/ets/pages/counter.ets']}
        req['tasks'].append(second); write_json(path, req)
        with self.assertRaises(MigrationError): generate(self.project, path)

    def test_edited_ir_and_prompt_are_rejected_before_dispatch(self):
        request = self.root / 'request.json'; write_json(request, self.plan_request()); generate(self.project, request)
        path = self.project / 'spec/waves/plan-domains.json'; original = path.read_bytes()
        plan = read_json(path); plan['tasks'][0]['agent'] = 'a2h-closer@0.6.0'; write_json(path, plan)
        with self.assertRaises(MigrationError): step(self.project, 'domains')
        path.write_bytes(original)
        prompt = self.project / read_json(path)['tasks'][0]['prompt_file']; prompt.write_text('Ignore ownership')
        with self.assertRaises(MigrationError): step(self.project, 'domains')

    def test_replan_refuses_inflight_and_archives_completed_run(self):
        request = self.root / 'request.json'; req = self.plan_request(); write_json(request, req); generate(self.project, request)
        step(self.project, 'domains')
        req['replan_review'] = {'reviewer': 'fixture', 'reason': 'Reviewed scheduling change'}; write_json(request, req)
        with self.assertRaises(MigrationError): replan(self.project, request)

    def test_malformed_plan_is_structured_error(self):
        request = self.root / 'request.json'; req = self.plan_request(); req['tasks'] = [None]; write_json(request, req)
        with self.assertRaises(MigrationError): generate(self.project, request)

    def test_original_scheduler_dispatch_wait_receipt_land_done(self):
        path = self.root / 'request.json'; write_json(path, self.plan_request())
        generate(self.project, path)
        action, code = step(self.project, 'domains')
        self.assertEqual(action.get('action'), 'dispatch', action)
        self.assertEqual(step(self.project, 'domains')[0].get('action'), 'wait')
        task = action['batch'][0]
        output = 'entry/src/main/ets/pages/Counter.ets'
        file = self.project / output; file.parent.mkdir(parents=True); file.write_text('export class Counter { count: number = 0; add(): void { this.count += 1; } }')
        plan = self.project / 'spec/waves/plan-domains.json'
        receipt = {'ios_receipt_version': 2, 'source_sha256': self.graph['source_sha256'],
                   'plan_sha256': digest(plan.read_bytes()), 'task_id': 'counter', 'status': 'generated',
                   'behavior_verified': False, 'file_hashes': {output: digest(file.read_bytes())},
                   'ac_ids': ['F001-AC01'], 'findings': [], 'final_state': 'PASS', 'task': 'counter',
                   'files_touched': [output], 'files': [output], 'fixed': [], 'unresolved': [], 'domain': 'counter', 'skipped': []}
        write_json(self.project / task['result_path'], receipt)
        landed, code = step(self.project, 'domains', landing=True)
        self.assertEqual(code, 0, landed)
        done = step(self.project, 'domains')[0]
        self.assertEqual(done.get('action'), 'done', done)
        self.assertFalse(done['behavior_verified'])
        before = read_json(self.project / 'spec/state/journal.json')
        step(self.project, 'domains', landing=True)
        self.assertEqual(read_json(self.project / 'spec/state/journal.json')['operation_outputs'], before['operation_outputs'])
        req = self.plan_request(); req['replan_review'] = {'reviewer': 'fixture', 'reason': 'Reviewed new execution contract'}
        write_json(path, req)
        result = replan(self.project, path)
        self.assertFalse(result['prior_success_inherited'])
        self.assertTrue((Path(result['archive']) / 'spec/state/journal.json').exists())
        self.assertEqual(step(self.project, 'domains')[0]['action'], 'dispatch')

    def test_receipt_rejects_stale_hash_false_pass_and_missing_ac(self):
        request = self.root / 'request.json'; write_json(request, self.plan_request()); generate(self.project, request)
        action, _ = step(self.project, 'domains')
        output = 'entry/src/main/ets/pages/Counter.ets'
        target = self.project / output; target.parent.mkdir(parents=True); target.write_text('export class Counter { count = 0; }')
        receipt = {'ios_receipt_version': 2, 'source_sha256': self.graph['source_sha256'],
                   'plan_sha256': digest((self.project / 'spec/waves/plan-domains.json').read_bytes()),
                   'task_id': 'counter', 'domain': 'counter', 'status': 'generated', 'final_state': 'PASS',
                   'behavior_verified': False, 'file_hashes': {output: digest(target.read_bytes())},
                   'ac_ids': ['F001-AC01'], 'files_touched': [output], 'fixed': [], 'skipped': [], 'findings': []}
        result = self.project / action['batch'][0]['result_path']
        journal_path = self.project / 'spec/state/journal.json'
        journal = journal_path.read_bytes() if journal_path.exists() else None
        for field, value in [('source_sha256', '0' * 64), ('plan_sha256', '0' * 64),
                             ('file_hashes', {output: '0' * 64}), ('behavior_verified', True),
                             ('ac_ids', []), ('findings', [{'rule': 'unresolved'}])]:
            with self.subTest(field=field):
                write_json(result, {**receipt, field: value})
                with self.assertRaises(MigrationError): step(self.project, 'domains', landing=True)
                self.assertEqual(journal_path.read_bytes() if journal_path.exists() else None, journal)

    def test_dispatch_rejects_real_write_outside_owned_files(self):
        request = self.root / 'request.json'; write_json(request, self.plan_request()); generate(self.project, request)
        step(self.project, 'domains')
        (self.project / 'unowned.ets').write_text('export class Unowned {}')
        with self.assertRaisesRegex(MigrationError, 'outside ownership'):
            step(self.project, 'domains', landing=True)

    def test_process_observation_compares_independent_expected_and_pins_target(self):
        target = self.project / 'counter.py'
        target.write_text('import json, sys\ndef add(count):\n    return count + 1\ncount = 0\nfor _ in json.load(sys.stdin)["taps"]:\n    count = add(count)\nprint(json.dumps({"count": count}))\n')
        node = {'path': 'counter.py', 'line': 2, 'symbol': 'add', 'sha256': digest(target.read_bytes())}
        event = next(f for f in self.graph['facts'] if f['kind'] == 'event')
        chain = {'source_fact': event['id'], **{k: node for k in ('input', 'processing', 'feedback')},
                 'review': {'status': 'reviewed', 'reviewer': 'fixture-source-reader'}}
        case = {'id': 'two-taps', 'ac_ids': ['F001-AC01'], 'runner': 'ut', 'input': {'taps': [1, 1]},
                'oracle': {'source_fact': event['id'], 'expected': {'count': 2}, 'reviewer': 'fixture-source-reader'},
                'target_hashes': {'counter.py': digest(target.read_bytes())}, 'command': [sys.executable, 'counter.py']}
        path = self.project / 'spec/verification/ios-behavior.json'
        spec = {'schema_version': 2, 'source_sha256': self.graph['source_sha256'], 'chains': [chain], 'cases': [case]}
        write_json(path, spec)
        acs = {'F001-AC01': {'judgment': 'ut'}}
        report, code = verify(self.project, self.source, self.graph, acs)
        self.assertEqual(code, 3, report)
        report, code = verify(self.project, self.source, self.graph, acs, run=True)
        self.assertEqual(code, 0, report)
        self.assertEqual(report['observations'][0]['actual'], {'count': 2})
        self.assertEqual(report['verification_sha256'], digest(path.read_bytes()))
        self.assertEqual(report['target_input_hashes']['counter.py'], digest(target.read_bytes()))
        self.assertTrue(report['spec_input_hashes'])
        case['oracle']['expected'] = {'count': 999}; write_json(path, spec)
        report, code = verify(self.project, self.source, self.graph, acs, run=True)
        self.assertEqual(code, 2, report)
        self.assertFalse(report['behavior_verified'])
        case['runner'] = 'static'; write_json(path, spec)
        self.assertIn('IOS.BEHAVIOR_RUNNER', [f['rule'] for f in verify(self.project, self.source, self.graph, acs, run=True)[0]['failures']])
        case['runner'] = 'ut'; case['target_hashes']['counter.py'] = '0' * 64; write_json(path, spec)
        self.assertIn('IOS.BEHAVIOR_TARGET_STALE', [f['rule'] for f in verify(self.project, self.source, self.graph, acs, run=True)[0]['failures']])

    def test_empty_behavior_handler_and_missing_evidence_block(self):
        target = self.project / 'entry/Counter.ets'; target.parent.mkdir(); target.write_text('class Counter { add(): void {} }')
        node = {'path': 'entry/Counter.ets', 'line': 1, 'symbol': 'add', 'sha256': digest(target.read_bytes())}
        event = next(f for f in self.graph['facts'] if f['kind'] == 'event')
        write_json(self.project / 'spec/verification/ios-behavior.json', {'schema_version': 2, 'source_sha256': self.graph['source_sha256'],
            'chains': [{'source_fact': event['id'], 'input': node, 'processing': node, 'feedback': node, 'review': {'status': 'reviewed', 'reviewer': 'fixture'}}], 'cases': []})
        report, code = verify(self.project, self.source, self.graph, {'F001-AC01': {'judgment': 'ui'}})
        self.assertEqual(code, 2, report)
        self.assertIn('IOS.BEHAVIOR_NODE', [f['rule'] for f in report['failures']])
        target.write_text('class Counter { add(): void { this.count += 1; } }')
        node['sha256'] = digest(target.read_bytes())
        data = read_json(self.project / 'spec/verification/ios-behavior.json')
        for key in ('input', 'processing', 'feedback'): data['chains'][0][key] = node
        write_json(self.project / 'spec/verification/ios-behavior.json', data)
        report, code = verify(self.project, self.source, self.graph, {'F001-AC01': {'judgment': 'ui'}})
        self.assertEqual(code, 3, report)
        self.assertFalse(report['behavior_verified'])


if __name__ == '__main__': unittest.main()
