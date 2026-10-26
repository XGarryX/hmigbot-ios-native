"""Real SwiftSyntax / original compiled coverage regressions on neutral sources."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/a2h-spec/scripts'


class SharedInstances(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='shared-instance-check-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'source'
        self.source.mkdir()
        (self.source / 'Shared.swift').write_text('enum Status { case ready, closed }\nstruct Limit {\n func check(_ value: Int) -> Bool {\n  return value < 180\n }\n}\n')
        self.project = self.base / 'workspace'
        self.features = self.project / 'spec/baseline/features'
        self.features.mkdir(parents=True)
        self.owner = self.features / 'F101-state.md'
        self.consumer = self.features / 'F102-screen.md'
        self.header = '---\ncomplexity: simple\nsource_anchors:\n  - role: util\n    path: Shared.swift\n---\n'
        self.owner_text = self.header + '\n## 验收标准\n' + (
            '- [ ] F101-AC01 ready和closed分别保留。 `源:Status → 标:Status` `判:unit | 两值保留` `真:src:Shared.swift:1` `组:{enum:Status.ready, enum:Status.closed}`\n'
            '- [ ] F101-AC02 小于180时通过。 `源:Limit.check → 标:Limit.check` `判:unit | 179通过180拒绝` `真:src:Shared.swift:4` `组:{threshold:180}`\n')
        self.consumer_text = self.header + '\n## 验收标准\n- [ ] F102-AC01 使用领域服务的结果。 `源:Limit.check → 标:ScreenModel` `判:unit | 显示返回结果` `真:src:Shared.swift:3`\n'
        self.rows = [('enum:Status.ready', 'Shared.swift:1', 'F101-AC01'),
                     ('enum:Status.closed', 'Shared.swift:1', 'F101-AC01'),
                     ('threshold:180', 'Shared.swift:4', 'F101-AC02')]
        self.owner.write_text(self.owner_text)
        self.write_consumer(self.rows)
        self.profile()

    def command(self, script, *args):
        result = subprocess.run([sys.executable, '-B', str(SCRIPTS / script), '--src', str(self.source), *map(str, args)],
                                cwd=self.project, capture_output=True, text=True, timeout=120,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        self.assertIn(result.returncode, (0, 2), result.stdout + result.stderr)
        return result

    def profile(self):
        self.command('profile_feature.py', '--features-dir', self.features)

    def write_consumer(self, rows):
        table = '\n## 共享实例引用\n\n| 实例ID | 源位置 | owner AC |\n|---|---|---|\n'
        self.consumer.write_text(self.consumer_text + table + ''.join('| `' + '` | `'.join(row) + '` |\n' for row in rows))

    def lint(self, *args):
        return self.command('lint_coverage.py', '--project-root', self.project, *args)

    def section(self):
        return json.loads((self.project / 'spec/.a2h/open-findings.json').read_text())['sections']['spec/lint_coverage']

    def test_valid_reference_preserves_denominator_and_warnings(self):
        self.write_consumer([])
        self.assertEqual(self.lint().returncode, 2)
        before = self.section()
        profile = (self.project / 'spec/baseline/feature-profiles.json').read_bytes()
        self.write_consumer(self.rows)
        self.assertEqual(self.lint('--after-repair').returncode, 0)
        after = self.section()
        self.assertEqual(profile, (self.project / 'spec/baseline/feature-profiles.json').read_bytes())
        warning = lambda x: (x['rule'], x['subject'], x['detail'], x['severity'])
        old_warnings = [warning(x) for x in before['findings'] if x['severity'] == 'warn']
        self.assertEqual(old_warnings, [warning(x) for x in after['findings'] if x['severity'] == 'warn'])
        for feature, kinds in before['context']['instance_stats'].items():
            for kind, counts in kinds.items():
                self.assertEqual(counts['total'], after['context']['instance_stats'][feature][kind]['total'])
        self.assertEqual(after['context']['instance_stats']['F102-screen.md']['enum_case']['shared'], 2)

    def test_missing_owner_ac_does_not_exempt(self):
        self.write_consumer([(i, s, 'F101-AC99') for i, s, a in self.rows])
        self.assertEqual(self.lint().returncode, 2)

    def test_superseded_owner_does_not_exempt(self):
        self.owner.write_text(self.owner_text.replace('F101-AC01', 'F101-AC01 〔superseded by PD-OLD〕'))
        self.assertEqual(self.lint().returncode, 2)

    def test_nonexistent_truth_location_does_not_exempt(self):
        self.owner.write_text(self.owner_text.replace('真:src:Shared.swift:1', '真:src:Shared.swift:999'))
        self.assertEqual(self.lint().returncode, 2)

    def test_owner_proof_must_actually_cover_item(self):
        self.owner.write_text(self.owner_text.replace('ready和closed分别保留', '其他状态保留').replace(' `组:{enum:Status.ready, enum:Status.closed}`', ''))
        self.assertEqual(self.lint().returncode, 2)

    def test_same_number_different_source_does_not_exempt(self):
        (self.source / 'Other.swift').write_text('struct Other { func check(_ value: Int) -> Bool { value < 180 } }\n')
        self.owner.write_text(self.owner_text.replace('path: Shared.swift', 'path: Shared.swift\n  - role: util\n    path: Other.swift').replace('真:src:Shared.swift:4', '真:src:Other.swift:1'))
        self.profile()
        self.assertEqual(self.lint().returncode, 2)

    def test_stale_declaration_line_does_not_exempt(self):
        self.write_consumer([(i, 'Shared.swift:99', a) for i, s, a in self.rows])
        self.assertEqual(self.lint().returncode, 2)

    def test_plain_owner_names_do_not_exempt(self):
        self.consumer.write_text(self.consumer_text + '\n其他行为由F101负责。\n')
        self.assertEqual(self.lint().returncode, 2)

    def test_unreferenced_missing_item_remains_blocking(self):
        self.write_consumer([self.rows[0]])
        self.assertEqual(self.lint().returncode, 2)
        self.assertTrue(any(x['rule'] == 'SPEC.INSTANCE_UNACCOUNTED' for x in self.section()['findings']))

    def test_cycle_cannot_replace_direct_owner(self):
        self.owner.write_text(self.owner_text + '\n## 共享实例引用\n| 实例ID | 源位置 | owner AC |\n|---|---|---|\n| enum:Status.ready | Shared.swift:1 | F102-AC01 |\n')
        self.assertEqual(self.lint().returncode, 2)

    def test_duplicate_ac_id_does_not_exempt(self):
        self.owner.write_text(self.owner_text + self.owner_text.split('## 验收标准\n')[1])
        self.assertEqual(self.lint().returncode, 2)

    def test_owner_not_in_global_profiles_does_not_exempt(self):
        p=self.project/'spec/baseline/feature-profiles.json'
        data=json.loads(p.read_text());del data['features'][self.owner.name]
        p.write_text(json.dumps(data))
        self.assertEqual(self.lint().returncode, 2)

    def test_retired_owner_does_not_exempt(self):
        self.owner.write_text(self.owner_text.replace('complexity: simple','complexity: simple\nstatus: skipped'))
        self.assertEqual(self.lint().returncode, 2)

    def test_owner_instance_obligation_cannot_be_removed(self):
        p=self.project/'spec/baseline/feature-profiles.json'
        data=json.loads(p.read_text());data['features'][self.owner.name]['enumerable_instances']['enum_case']=[]
        p.write_text(json.dumps(data))
        self.assertEqual(self.lint().returncode, 2)

    def test_only_feature_and_report_only_leave_outputs_unchanged(self):
        before = {p: p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        self.assertEqual(self.lint('--only-feature', self.consumer.name).returncode, 0)
        self.assertEqual(before, {p: p.read_bytes() for p in self.project.rglob('*') if p.is_file()})
        self.assertEqual(self.lint('--report-only').returncode, 0)
        self.assertEqual(before, {p: p.read_bytes() for p in self.project.rglob('*') if p.is_file()})


if __name__ == '__main__':
    unittest.main()
