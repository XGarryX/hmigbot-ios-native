"""Native blocked outcomes and dotfiles must survive the original kernel bridge."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from contextlib import redirect_stderr
import io
import shutil
import subprocess

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))

from hmigbot_ios.core import MigrationError, atomic_write, digest, json_bytes, read_json, write_json
from hmigbot_ios.ios_scheduler import generate, step, _land_native_receipts
import hmigbot_ios.ios_scheduler as scheduler
from hmigbot_ios.page_evidence import generation
import test_ios_harness as harness_fixture


class FailureReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='native-receipt-outcome-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        _, self.project, self.graph = harness_fixture.fixture(self.root)

    def plan(self, ownership, child=False):
        tasks = [{'id': 'counter', 'role': 'a2h-ios-converter', 'goal': 'Implement source counter',
            'ownership': ownership, 'ac_ids': ['F001-AC01'],
            'fact_ids': [f['id'] for f in self.graph['facts']], 'parents': []}]
        if child:
            tasks.append({**tasks[0], 'id': 'final', 'ownership': ['entry/Final.ets'], 'parents': ['counter']})
        request = self.root / 'request.json'
        write_json(request, {'schema_version': 2, 'wave': 'domains',
            'graph_sha256': digest(json_bytes(self.graph)), 'tasks': tasks})
        return generate(self.project, request)

    def receipt(self, action, paths, blocked=False):
        ident = action['batch'][0]['id']
        hashes = {}
        for path in paths:
            file = self.project / path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text('build/\n' if path == '.gitignore' else 'fixture\n', encoding='utf-8')
            hashes[path] = digest(file.read_bytes())
        result = self.project / action['batch'][0]['result_path']
        write_json(result, {'ios_receipt_version': 2, 'source_sha256': self.graph['source_sha256'],
            'plan_sha256': digest((self.project / 'spec/waves/plan-domains.json').read_bytes()),
            'task_id': ident, 'task': ident, 'domain': ident,
            'status': 'blocked' if blocked else 'generated', 'final_state': 'BLOCKED' if blocked else 'PASS',
            'behavior_verified': False, 'file_hashes': hashes, 'ac_ids': ['F001-AC01'],
            'files_touched': list(paths), 'files': list(paths), 'fixed': [], 'skipped': [],
            'findings': [{'id': 'SPEC.CONFLICT', 'message': 'Source contract needs correction'}] if blocked else []})
        return result

    def task_state(self):
        tasks = read_json(self.project / 'spec/state/state.json')['waves']['domains']['tasks']
        return next(row for row in tasks if row['id'] == 'counter')

    def test_partial_blocked_receipt_lands_as_failure_and_never_releases_its_child(self):
        self.plan(['.gitignore', 'entry/Counter.ets'], child=True)
        for attempt in (1, 2):
            action, _ = step(self.project, 'domains')
            self.assertEqual([row['id'] for row in action['batch']], ['counter'])
            result = self.receipt(action, ['.gitignore'], blocked=True)
            original = result.read_bytes()
            landed, code = step(self.project, 'domains', landing=True)
            self.assertEqual(code, 2, landed)
            self.assertNotEqual(landed['landed'][0]['status'], 'OK', landed)
            self.assertNotEqual(self.task_state()['status'], 'done')
            self.assertEqual(result.read_bytes(), original)
            archived = self.project / landed['ios_blocked_receipts'][0]['archive']
            self.assertEqual(archived.read_bytes(), original)
            self.assertEqual(generation(self.project, self.graph['source_sha256'])[0]['status'], 'blocked')
        with self.assertRaisesRegex(MigrationError, 'failed|blocked'):
            step(self.project, 'domains')
        state = read_json(self.project / 'spec/state/state.json')
        final = [row for row in state['waves']['domains']['tasks'] if row['id'] == 'final']
        self.assertFalse(final and final[0]['status'] == 'done')

    def test_generated_dotfiles_have_no_false_fence_but_a_real_shadow_file_is_unowned(self):
        paths = ['.gitignore', '.github/CODEOWNERS', '...hidden/config.json']
        self.plan(paths)
        self.assertEqual(read_json(self.project / 'spec/blueprint/contracts.json')['ios_tasks'][0]['ownership'], paths)
        action, _ = step(self.project, 'domains')
        self.receipt(action, paths)
        shadow = self.project / 'gitignore'
        shadow.write_text('unauthorized actual file', encoding='utf-8')
        with self.assertRaisesRegex(MigrationError, 'outside ownership'):
            step(self.project, 'domains', landing=True)
        shadow.unlink()
        landed, code = step(self.project, 'domains', landing=True)
        self.assertEqual(code, 0, landed)
        self.assertFalse(landed.get('fence_breach'), landed)
        self.assertEqual(set(self.task_state()['files_touched']), set(paths))

    def test_two_native_owners_cannot_collide_in_the_original_dotpath_projection(self):
        request = self.root / 'ambiguous.json'
        task = {'role': 'a2h-ios-converter', 'goal': 'Own a distinct native filename',
            'ac_ids': ['F001-AC01'], 'fact_ids': [f['id'] for f in self.graph['facts']], 'parents': []}
        write_json(request, {'schema_version': 2, 'wave': 'domains', 'graph_sha256': digest(json_bytes(self.graph)),
            'tasks': [{**task, 'id': 'hidden', 'ownership': ['.gitignore']},
                      {**task, 'id': 'visible', 'ownership': ['gitignore']}]})
        with self.assertRaisesRegex(MigrationError, 'original.*ownership|ownership.*original'):
            generate(self.project, request)

    def test_multiple_blocked_receipts_use_the_original_csv_failure_channel(self):
        task = {'role': 'a2h-ios-converter', 'goal': 'Report a real blocked native contract',
            'ac_ids': ['F001-AC01'], 'fact_ids': [f['id'] for f in self.graph['facts']], 'parents': []}
        request = self.root / 'multiple.json'
        write_json(request, {'schema_version': 2, 'wave': 'domains', 'max_parallel': 2,
            'graph_sha256': digest(json_bytes(self.graph)), 'tasks': [
                {**task, 'id': 'counter', 'ownership': ['entry/Counter.ets']},
                {**task, 'id': 'second', 'ownership': ['entry/Second.ets']}]})
        generate(self.project, request)
        action, _ = step(self.project, 'domains')
        self.assertEqual({row['id'] for row in action['batch']}, {'counter', 'second'})
        original = {}
        for row in action['batch']:
            path = self.receipt({'batch': [row]}, [], blocked=True)
            original[path] = path.read_bytes()
        landed, code = step(self.project, 'domains', landing=True)
        self.assertEqual(code, 2, landed)
        self.assertEqual({row['id']: row['status'] for row in landed['landed']},
                         {'counter': 'RETRY_NEEDED', 'second': 'RETRY_NEEDED'})
        self.assertEqual({row['id'] for row in landed['ios_blocked_receipts']}, {'counter', 'second'})
        for path, raw in original.items():
            self.assertEqual(path.read_bytes(), raw)
        self.assertFalse(any(row['status'] == 'done' for row in read_json(self.project / 'spec/state/state.json')['waves']['domains']['tasks']))


class BlockedReceiptRestoreTests(unittest.TestCase):
    def assert_other_receipts_restored(self, mode):
        with tempfile.TemporaryDirectory(prefix='blocked-restore-') as directory:
            project = Path(directory)
            first = project / 'spec/waves/results/domains/first.json'
            second = first.with_name('second.json')
            first.parent.mkdir(parents=True)
            first.write_bytes(b'{"status":"blocked","id":"first"}')
            second.write_bytes(b'{"status":"blocked","id":"second"}')
            raw_first, raw_second = first.read_bytes(), second.read_bytes()
            dispatch = {'waves': {'domains': {'dispatched': {'first': {'attempts': 1}, 'second': {'attempts': 1}}}}}

            def original_writer(*args):
                self.assertFalse(first.exists())
                self.assertFalse(second.exists())
                if mode == 'conflict':
                    first.write_bytes(b'new concurrent result')
                return {'landed': [{'id': 'first', 'status': 'RETRY_NEEDED'}, {'id': 'second', 'status': 'RETRY_NEEDED'}]}

            def restore(path, raw):
                if mode == 'restore_error' and path == first:
                    raise PermissionError('injected first restore lock')
                return atomic_write(path, raw)

            with patch('hmigbot_ios.ios_scheduler.read_json', return_value=dispatch), \
                 patch('hmigbot_ios.ios_scheduler.kernel', return_value=SimpleNamespace(journal_indexes=lambda *_: ({}, {}))), \
                 patch('hmigbot_ios.ios_scheduler.invoke', side_effect=original_writer), \
                 patch('hmigbot_ios.ios_scheduler.atomic_write', side_effect=restore):
                with self.assertRaisesRegex(MigrationError, 'restore all native receipts'):
                    _land_native_receipts(project, 'domains', project / 'plan.json', [('first', first), ('second', second)])
            self.assertEqual(second.read_bytes(), raw_second)
            self.assertEqual((project / f'spec/reports/ios-blocked-receipts/domains/first/{digest(raw_first)}.json').read_bytes(), raw_first)
            if mode == 'conflict':
                self.assertEqual(first.read_bytes(), b'new concurrent result')
            else:
                self.assertFalse(first.exists())

    def test_conflicting_first_result_does_not_prevent_restoring_later_receipts(self):
        self.assert_other_receipts_restored('conflict')

    def test_first_restore_permission_error_does_not_prevent_restoring_later_receipts(self):
        self.assert_other_receipts_restored('restore_error')


class SchedulerRuntimeCleanupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='runtime-cleanup-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'
        self.project.mkdir()
        self.runtime_parent = self.root / 'runtime-parent'
        self.runtime_parent.mkdir()

    def lock(self, code=32):
        error = PermissionError('injected staged executable lock')
        error.winerror = code
        return error

    def run_original(self, errors, outcome=None, diagnostic_failure=False):
        if os.name != 'nt':
            self.skipTest('Fault injection for Windows staged runtime cleanup')
        self.cleanup_paths = []
        self.stderr = io.StringIO()
        original_rmtree, original_write = shutil.rmtree, scheduler.write_json

        def stage(source, directory):
            directory.mkdir(parents=True)
            (directory / '_entry.exe').write_bytes(b'not executed: subprocess is mocked')

        def cleanup(path, *args, **kwargs):
            if Path(path).name.startswith('ios-scheduler-python-'):
                self.cleanup_paths.append(Path(path))
                if len(self.cleanup_paths) <= len(errors):
                    raise errors[len(self.cleanup_paths) - 1]
            return original_rmtree(path, *args, **kwargs)

        def write(path, value):
            if diagnostic_failure and '.cleanup-' in path.name:
                raise OSError('injected audit write failure')
            return original_write(path, value)

        run = ({'side_effect': outcome} if isinstance(outcome, BaseException) else
               {'return_value': outcome or SimpleNamespace(returncode=0, stdout=b'{"action":"dispatch"}', stderr=b'')})
        with patch('hmigbot_ios.ios_scheduler.tempfile.gettempdir', return_value=str(self.runtime_parent)), \
             patch('hmigbot_ios.ios_scheduler.platform.machine', return_value='AMD64'), \
             patch('hmigbot_ios.ios_scheduler.shutil.copytree', side_effect=stage), \
             patch('hmigbot_ios.ios_scheduler.shutil.copy2'), \
             patch('hmigbot_ios.ios_scheduler.shutil.rmtree', side_effect=cleanup), \
             patch('hmigbot_ios.ios_scheduler.subprocess.run', **run), \
             patch('hmigbot_ios.scheduler_windows_runtime.run', **run), \
             patch('hmigbot_ios.ios_scheduler.write_json', side_effect=write), redirect_stderr(self.stderr):
            return scheduler.invoke(self.project, 'next_batch', [])

    def diagnostics(self):
        return [read_json(path) for path in (self.project / 'spec/reports/scheduler').glob('next_batch.cleanup-*.json')]

    def test_transient_windows_lock_does_not_change_successful_command_result(self):
        self.assertEqual(self.run_original([self.lock()]), {'action': 'dispatch'})
        self.assertEqual(len(self.cleanup_paths), 2)
        self.assertFalse(self.cleanup_paths[-1].exists())
        self.assertEqual(self.diagnostics()[0]['status'], 'removed_after_retry')

    def test_persistent_windows_lock_retains_runtime_and_reports_cleanup_separately(self):
        self.assertEqual(self.run_original([self.lock(5)] * 20), {'action': 'dispatch'})
        self.assertGreater(len(self.cleanup_paths), 1)
        self.assertLess(len(self.cleanup_paths), 20)
        diagnostic = self.diagnostics()[0]
        self.assertEqual(diagnostic['status'], 'retained')
        self.assertTrue(Path(diagnostic['runtime_path']).exists())
        self.assertEqual(diagnostic['attempts'], len(self.cleanup_paths))
        self.assertFalse((self.project / 'spec/reports/scheduler/next_batch.failure.json').exists())

    def test_non_lock_cleanup_error_is_not_retried_or_confused_with_command_failure(self):
        self.assertEqual(self.run_original([self.lock(123)] * 20), {'action': 'dispatch'})
        self.assertEqual(len(self.cleanup_paths), 1)
        self.assertEqual(self.diagnostics()[0]['winerror'], 123)

    def test_actual_command_failure_has_priority_over_persistent_cleanup_lock(self):
        timeout = subprocess.TimeoutExpired(['original-tool'], 60)
        missing = FileNotFoundError('actual original executable missing')
        rejected = SimpleNamespace(returncode=7, stdout=b'', stderr=b'actual original rejection')
        malformed = SimpleNamespace(returncode=0, stdout=b'not JSON', stderr=b'')
        for outcome, message in ((timeout, 'Original scheduler failed'), (missing, 'Original scheduler failed'),
                                 (rejected, 'actual original rejection'), (malformed, 'did not return a JSON action')):
            with self.subTest(outcome=outcome):
                with self.assertRaisesRegex(MigrationError, message) as raised:
                    self.run_original([self.lock()] * 20, outcome)
                if isinstance(outcome, BaseException):
                    self.assertIs(raised.exception.__cause__, outcome)

    def test_cleanup_audit_write_failure_is_reported_without_hiding_success(self):
        self.assertEqual(self.run_original([self.lock()] * 20, diagnostic_failure=True), {'action': 'dispatch'})
        self.assertIn('injected audit write failure', self.stderr.getvalue())
        self.assertIn(str(self.cleanup_paths[-1]), self.stderr.getvalue())

    def test_same_parent_runtime_redirection_is_retained_without_deletion(self):
        directory = self.runtime_parent / 'ios-scheduler-python-owned'
        directory.mkdir()
        redirected = self.runtime_parent / 'other-runtime'
        original_resolve = Path.resolve

        def resolve(path, *args, **kwargs):
            return redirected if path == directory else original_resolve(path, *args, **kwargs)

        with patch.object(Path, 'resolve', autospec=True, side_effect=resolve), \
             patch('hmigbot_ios.ios_scheduler.shutil.rmtree') as remove:
            report = scheduler._cleanup_windows_runtime(self.project, 'next_batch', directory, self.runtime_parent)
        remove.assert_not_called()
        self.assertEqual(report['status'], 'retained')
        self.assertIn('Refusing cleanup', report['error'])
        self.assertTrue(directory.exists())

    def test_other_platforms_keep_the_original_temporary_directory_context(self):
        context = MagicMock()
        context.__enter__.return_value = 'original-posix-temp'
        failure = PermissionError('original non-Windows cleanup behavior')
        context.__exit__.side_effect = failure
        with patch('hmigbot_ios.ios_scheduler.tempfile.TemporaryDirectory', return_value=context) as constructor, \
             patch('hmigbot_ios.ios_scheduler._cleanup_windows_runtime') as windows_cleanup:
            with self.assertRaises(PermissionError) as raised:
                with scheduler._runtime_directory(self.project, 'next_batch', windows=False) as name:
                    self.assertEqual(name, 'original-posix-temp')
            self.assertIs(raised.exception, failure)
            constructor.assert_called_once_with(prefix='ios-scheduler-python-', dir='/private/tmp' if scheduler.platform.system() == 'Darwin' else None)
            windows_cleanup.assert_not_called()


if __name__ == '__main__':
    unittest.main()
