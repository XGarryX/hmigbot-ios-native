"""A fresh upstream exempt verdict still needs completed handles and real artifacts."""
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.core import MigrationError, digest, read_json, write_json
from hmigbot_ios.join_rollout import _exempt_artifacts, main


class JoinExemptionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='join-exempt-')
        self.addCleanup(temp.cleanup)
        self.project = Path(temp.name) / 'project'
        self.project.mkdir()
        self.rollout = self.project / 'source.jsonl'
        self.point = 'env_prewarm_r2'
        self.names = [self.point]
        self.expected_path = self.project / f'spec/a2h/_work/expected_{self.point}.json'
        self.ledger = self.project / 'spec/a2h/_work/join-ledger.jsonl'
        self.artifact = self.project / 'out/report.json'
        write_json(self.artifact, {'synthetic': 'complete artifact ' * 20})
        self.expected = {'join_point': self.point, 'task_names': self.names,
                         'artifacts': [{'path': 'out/*.json', 'min_count': 1, 'min_bytes': 100, 'json': True}]}
        self.rows = [{'type': 'session_meta', 'payload': {'id': 'synthetic-exempt-writer',
                      'agent_path': '/root/parent'}}]
        self.observation('completed')
        self.gate_calls = 0

    def observation(self, status, reopen=False, wrong_writer=False):
        self.rows = self.rows[:1]
        writer = '/root/wrong' if wrong_writer else '/root/parent'
        for index, name in enumerate(self.names):
            self.tool('spawn_agent', {'task_name': name, 'agent_type': 'hmos-builder'},
                      {'task_name': writer + '/' + name}, f'spawn-{index}')
        self.tool('list_agents', {}, {'agents': [{'agent_name': writer + '/' + name,
                   'agent_status': {status: 'synthetic tool observation'}} for name in self.names]}, 'status')
        if reopen:
            self.rows.append({'type': 'response_item', 'payload': {'type': 'function_call',
                'name': 'followup_task', 'call_id': 'reopen', 'arguments': json.dumps({'target': self.names[0]})}})

    def tool(self, name, args, output, ident):
        self.rows.extend([{'type': 'response_item', 'payload': {'type': 'function_call', 'name': name,
            'call_id': ident, 'arguments': json.dumps(args)}}, {'type': 'response_item', 'payload': {
            'type': 'function_call_output', 'call_id': ident, 'output': json.dumps(output)}}])

    def prepare(self):
        write_json(self.expected_path, self.expected)
        for row in self.rows:
            row.setdefault('timestamp', datetime.now(timezone.utc).isoformat())
        raw = b''.join((json.dumps(row) + '\n').encode() for row in self.rows)
        self.rollout.write_bytes(raw)
        self.sha = digest(raw)

    def record(self):
        return {'join_point': self.point, 'joined': [], 'exempt': list(self.names),
                'rollouts': [f'join-{self.point}-{self.sha}.log']}

    def run_mock(self, *, row_change=None, append=True, stale=False, tamper=False, no_ledger=False,
                 recognized=None, stdout=None, original_code=0, during=None, second_row=False):
        self.prepare()
        record = self.record()
        if row_change:
            row_change(record)
        if stale:
            self.ledger.write_bytes((json.dumps(record) + '\n').encode())

        def invoke(argv, **kwargs):
            if argv[0] == 'git':
                return SimpleNamespace(returncode=0, stdout=b'synthetic-fixed-sha\n' if 'rev-parse' in argv else b'', stderr=b'')
            self.gate_calls += 1
            if append:
                before = self.ledger.read_bytes() if self.ledger.exists() else b''
                added = (json.dumps(record) + '\n').encode()
                self.ledger.write_bytes((b'changed prefix\n' if tamper else before) + added * (2 if second_row else 1))
            if during:
                during(argv)
            output = stdout if stdout is not None else f'句柄 {len(self.names) if recognized is None else recognized}\nfire-and-forget'
            return SimpleNamespace(returncode=original_code, stdout=output.encode(), stderr=b'')

        buffer = StringIO()
        argv = ['--project', str(self.project), '--join-point', self.point, '--rollout', str(self.rollout)]
        if no_ledger:
            argv.append('--no-ledger')
        with patch('hmigbot_ios.join_rollout.subprocess.run', side_effect=invoke), redirect_stdout(buffer):
            code = main(argv, root=ROOT)
        result = json.loads(buffer.getvalue())
        audit = self.project / f'spec/reports/derived/a2h-join/{self.point}/{self.sha}.json'
        return code, result, read_json(audit) if audit.is_file() else None

    def test_actual_upstream_allowlisted_completed_case_is_truthfully_exempt(self):
        self.prepare()
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'skills/a2h-join/scripts/join_gate.py'),
            '--project', str(self.project), '--join-point', self.point, '--rollout', str(self.rollout)],
            capture_output=True, env={**os.environ, 'PYTHONUTF8': '1'}, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        response = json.loads(result.stdout)
        self.assertEqual(response['status'], 'exempt')
        audit = read_json(Path(response['audit_path']))
        self.assertEqual(audit['original_gate']['verdicts'][0]['verdict'], 'exempt')
        self.assertEqual(audit['writer']['agent_path'], '/root/parent')
        self.assertEqual(audit['source_sha256'], self.sha)
        self.assertEqual(audit['exempt_artifacts'][0]['files'][0]['bytes'], self.artifact.stat().st_size)
        evidence = os.environ.get('HMIGBOT_JOIN_VERIFY_OUTPUT')
        if evidence:
            output = Path(evidence)
            output.mkdir(parents=True, exist_ok=True)
            write_json(output / 'actual-positive.audit.json', audit)
            (output / 'actual-positive.stdout.log').write_bytes(result.stdout)
            (output / 'actual-positive.stderr.log').write_bytes(result.stderr)

    def test_missing_invalid_undersized_and_count_shortfalls_reject_upstream_zero(self):
        for value in (None, b'not valid json' * 20, b'{}'):
            with self.subTest(artifact=value):
                if value is None:
                    self.artifact.unlink(missing_ok=True)
                else:
                    self.artifact.write_bytes(value)
                code, _, audit = self.run_mock()
                self.assertEqual(code, 3)
                self.assertEqual(audit['original_gate']['exit_code'], 0)
                self.assertIn('verification_error', audit['original_gate'])
        write_json(self.artifact, {'padding': 'x' * 200})
        self.expected['artifacts'][0]['min_count'] = 2
        self.assertEqual(self.run_mock()[0], 3)

    def test_stdout_stale_wrong_scope_and_duplicate_ledger_are_not_authority(self):
        cases = [dict(append=False), dict(append=False, stale=True), dict(tamper=True, stale=True), dict(second_row=True),
            dict(row_change=lambda r: r.update(join_point='other')),
            dict(row_change=lambda r: r.update(rollouts=['join-env_prewarm_r2-' + '0' * 64 + '.log'])),
            dict(row_change=lambda r: r.update(exempt=['other'])),
            dict(row_change=lambda r: r.update(exempt=self.names * 2)),
            dict(row_change=lambda r: r.update(joined=list(self.names))),
            dict(row_change=lambda r: r.update(exempt=self.names + ['extra']))]
        for case in cases:
            with self.subTest(case=case):
                self.ledger.unlink(missing_ok=True)
                code, _, audit = self.run_mock(**case)
                self.assertEqual(code, 3)
                self.assertIn('verification_error', audit['original_gate'])

    def test_mixed_tasks_need_individual_verdicts_and_recognized_count(self):
        self.names.append('ordinary_worker')
        self.observation('completed')
        split = lambda r: r.update(joined=['ordinary_worker'], exempt=[self.point])
        code, result, audit = self.run_mock(row_change=split)
        self.assertEqual((code, result['status']), (0, 'joined-with-exempt'))
        self.assertEqual([v['verdict'] for v in audit['original_gate']['verdicts']], ['exempt', 'joined'])
        self.assertEqual(self.run_mock(row_change=lambda r: r.update(exempt=[self.point]))[0], 3)
        self.assertEqual(self.run_mock(row_change=split, recognized=1)[0], 3)

    def test_no_ledger_exemption_stays_rejected_and_ordinary_joined_stays_supported(self):
        self.assertEqual(self.run_mock(no_ledger=True)[0], 3)
        self.assertEqual(self.run_mock(no_ledger=True, append=False,
                         stdout=f'句柄 1\njoined {self.point}\n')[0], 0)
        self.assertEqual(self.run_mock(original_code=1)[0], 1)

    def test_noncompleted_reopened_wrong_writer_and_missing_expected_stop_before_original(self):
        for status, reopen, wrong in [('unknown', False, False), ('running', False, False),
                                     ('completed', True, False), ('completed', False, True)]:
            with self.subTest(status=status, reopen=reopen, wrong_writer=wrong):
                self.observation(status, reopen=reopen, wrong_writer=wrong)
                self.gate_calls = 0
                self.assertNotEqual(self.run_mock()[0], 0)
                self.assertEqual(self.gate_calls, 0)
        self.observation('completed')
        self.expected['task_names'] = ['missing_task']
        self.gate_calls = 0
        self.assertEqual(self.run_mock()[0], 3)
        self.assertEqual(self.gate_calls, 0)

    def test_contract_or_projection_changed_during_original_call_is_rejected(self):
        def expected_change(argv):
            write_json(self.expected_path, {**self.expected, 'task_names': ['other']})
        def projection_change(argv):
            Path(argv[argv.index('--rollout') + 1]).write_text('changed', encoding='utf-8')
        for change in (expected_change, projection_change):
            with self.subTest(change=change):
                self.assertEqual(self.run_mock(during=change)[0], 3)

    def test_strict_artifact_fields_paths_globs_and_exact_count(self):
        write_json(self.project / 'out/second.json', {'padding': 'x' * 200})
        contract = {'artifacts': [{'path': 'out/*.json', 'count': 2, 'min_count': 2, 'min_bytes': 100, 'json': True}]}
        self.assertEqual(len(_exempt_artifacts(self.project, contract)[0]['files']), 2)
        malformed = [[], [{}], [{'path': '../escape.json'}], [{'path': str(self.artifact)}],
                     [{'path': 'C:/escape.json'}], [{'path': r'out\*.json'}],
                     [{'path': 'out/*.json', 'unsupported': True}]]
        for field in ('min_count', 'count', 'min_bytes'):
            for value in (True, '1', 1.5, -1):
                malformed.append([{'path': 'out/*.json', field: value}])
        malformed += [[{'path': 'out/*.json', 'json': value}] for value in ('true', 1, None)]
        malformed += [[{'path': 'out/*.json', 'min_count': 0}], [{'path': 'out/*.json', 'count': 1}]]
        for artifacts in malformed:
            with self.subTest(artifacts=artifacts), self.assertRaises((MigrationError, OSError, ValueError)):
                _exempt_artifacts(self.project, {'artifacts': artifacts})
        with self.assertRaises(MigrationError):
            _exempt_artifacts(self.project, {'done_envelope': True})

    def test_artifact_glob_cannot_escape_through_directory_link(self):
        outside = self.project.parent / 'outside'
        outside.mkdir()
        write_json(outside / 'escape.json', {'padding': 'x' * 200})
        link = self.project / 'linked'
        if os.name == 'nt':
            result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(outside)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.addCleanup(os.rmdir, link)
        else:
            link.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(MigrationError):
            _exempt_artifacts(self.project, {'artifacts': [{'path': 'linked/*.json'}]})


if __name__ == '__main__':
    unittest.main()
