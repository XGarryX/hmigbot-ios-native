"""Objective-C state declarations must survive the real authoring/checker contract."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))

from hmigbot_ios.ios_facts import RULES, refresh
from hmigbot_ios.ios_harness import initialize, validate_native_claims
from hmigbot_ios.native_authoring import prepare, render
from hmigbot_ios.native_pipeline import configure, index_source
from hmigbot_ios.native_semantics import required_facts


class ObjCStateContractTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='objc-state-contract-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.source, self.project = self.root / 'source', self.root / 'target'
        self.source.mkdir(); self.project.mkdir()
        (self.source / 'Counter.m').write_text('''@interface Counter : NSObject {
    int _count;
}
@property (nonatomic, copy) NSString *title;
@end
@implementation Counter
- (void)viewDidLoad { _count = 7; }
@end
''', encoding='utf-8')
        configure(self.source, self.project)
        initialize(self.project)
        index_source(self.project)
        base = self.project / 'spec/baseline'
        for folder, name, ident in [('features', 'F001-counter.md', 'F001'),
                                    ('ui', 'page_0001_Counter.md', 'page_0001')]:
            (base / folder).mkdir(parents=True, exist_ok=True)
            text = '---\nsource_platform: ios\nsource_anchors:\n  - path: Counter.m\n---\n# ' + ident + '\n'
            if folder == 'features':
                text += '- [ ] F001-AC01 Creation preserves declared owner and initialization; lifecycle sets count to 7. `判:unit | 真:src:Counter.m:2`\n'
            (base / folder / name).write_text(text, encoding='utf-8')
        self.graph = refresh(self.project, self.source)

    def documents(self):
        result = []
        for ident, kind in [('F001', 'feature'), ('page_0001', 'page')]:
            frameworks = ['uikit'] if kind == 'page' else ['nonvisual']
            claims = {}
            for dimension in required_facts(kind, {'objc'}, set(frameworks)):
                signals = [f for f in self.graph['facts'] if dimension in RULES[f['kind']]['dimensions']]
                if signals:
                    value = {'summary': 'Counter declares count and copied title; viewDidLoad assigns count to 7.'}
                    if dimension == 'state_ownership':
                        value = {'states': [{'fact_id': f['id'], 'owner': f['owner'], **f['value']}
                                            for f in signals if f['kind'] == 'state']}
                    claims[dimension] = {'status': 'known', 'value': value,
                        'fact_ids': [f['id'] for f in signals],
                        'evidence': [{'path': f['anchor']['path'], 'line': f['anchor']['line']} for f in signals]}
                else:
                    claims[dimension] = {'status': 'not_applicable', 'reason': 'The complete eight-line fixture has no operation in this dimension.'}
            result.append({'id': ident, 'kind': kind, 'languages': ['objc'], 'frameworks': frameworks, 'facts': claims})
        return result

    def test_actual_objc_states_render_without_handwritten_machine_ids(self):
        states = [f for f in self.graph['facts'] if f['kind'] == 'state']
        self.assertEqual({f['symbol'] for f in states}, {'_count', 'title'})
        request = {**prepare(self.project)['input_template'], 'documents': self.documents(),
                   'dispositions': [], 'truth_anchors': [{'ac_id': 'F001-AC01', 'path': 'Counter.m', 'line': 2}]}
        candidate = render(self.project, request)
        actual = candidate['files']['spec/baseline/ios-semantics.json']['documents']
        self.assertEqual(actual, request['documents'])
        self.assertFalse(candidate['spec_complete'])
        self.assertFalse(candidate['behavior_verified'])

    def test_forged_initializer_still_fails_the_unchanged_claim_checker(self):
        self.assertTrue(any(f['kind'] == 'state' for f in self.graph['facts']))
        docs = self.documents()
        page = next(d for d in docs if d['kind'] == 'page')
        page['facts']['state_ownership']['value']['states'][0]['initializer'] = '999'
        failures = []
        validate_native_claims(self.project, self.graph, {'documents': docs},
                               lambda rule, subject, detail: failures.append(rule))
        self.assertIn('IOS.STATE_VALUE_CONTRADICTION', failures)

    def test_omitting_one_real_objc_state_still_fails(self):
        self.assertGreaterEqual(sum(f['kind'] == 'state' for f in self.graph['facts']), 2)
        docs = self.documents()
        claim = next(d for d in docs if d['kind'] == 'page')['facts']['state_ownership']
        claim['fact_ids'].pop()
        failures = []
        validate_native_claims(self.project, self.graph, {'documents': docs},
                               lambda rule, subject, detail: failures.append(rule))
        self.assertIn('IOS.CLAIM_SIGNAL_MISSING', failures)

    def test_state_extractor_rules_are_part_of_frozen_tool_revision(self):
        from hmigbot_ios import plan_contract
        runtime = self.root / 'runtime'
        module = runtime / 'src/hmigbot_ios/plan_contract.py'
        module.parent.mkdir(parents=True)
        module.write_text('fixture plan rules\n', encoding='utf-8')
        for name in ('ios_facts.py', 'objc_state.py'):
            helper = module.with_name(name)
            helper.write_text('original extraction rules\n', encoding='utf-8')
        with patch.object(plan_contract, '__file__', str(module)), \
                patch('hmigbot_ios.artifact_contract.revision', return_value='same-artifact-contract'):
            for name in ('ios_facts.py', 'objc_state.py'):
                before = plan_contract.contract_revision(self.project)
                helper = module.with_name(name)
                helper.write_text('changed extraction rules\n', encoding='utf-8')
                self.assertNotEqual(before, plan_contract.contract_revision(self.project), name)


if __name__ == '__main__':
    unittest.main()
