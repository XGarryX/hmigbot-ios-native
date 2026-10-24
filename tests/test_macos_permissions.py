"""Quarantine preparation never mutates outside the selected conversion project."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from unittest.mock import patch

import pytest

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.core import MigrationError
from hmigbot_ios import macos_permissions as permissions
from hmigbot_ios import portable_helper


@pytest.fixture
def project(tmp_path):
    root = tmp_path / 'project'
    root.mkdir()
    payload = root / '.hmigbot-ios/plugin/payload/_entry.dist'
    payload.mkdir(parents=True)
    (payload / '_entry.bin').write_bytes(b'original binary bytes')
    (payload / 'library.so').write_bytes(b'original library bytes')
    return root, payload


def original_bytes(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}


def test_on_demand_repair_preserves_bytes_and_records_the_actual_result(project):
    root, payload = project
    before = original_bytes(root)
    flagged = {payload / 'library.so'}
    def attributes(path, **kwargs):
        assert kwargs == {}
        return [permissions.ATTRIBUTE] if path in flagged else []
    def execute(command, **kwargs):
        assert command == ['xattr', '-dr', permissions.ATTRIBUTE, str(payload)]
        assert kwargs['shell'] is False and kwargs['capture_output'] is True
        flagged.clear()
        return subprocess.CompletedProcess(command, 0, 'actual stdout', 'actual stderr')
    with patch.object(permissions.platform, 'system', return_value='Darwin'), \
         patch.object(permissions, '_list_attributes', side_effect=attributes), \
         patch.object(permissions.subprocess, 'run', side_effect=execute) as run:
        receipt = permissions.ensure_runtime_permissions(root, payload)
        second = permissions.clear_quarantine(root, payload)
    assert receipt['status'] == 'cleared' and receipt['mutated'] is True
    assert receipt['stdout'] == 'actual stdout' and receipt['stderr'] == 'actual stderr'
    assert receipt['returncode'] == 0 and receipt['remaining_quarantined_paths'] == []
    assert receipt['product_verified'] is False and receipt['mutation_attempted'] is True
    assert second['status'] == 'not_needed' and second['command'] is None
    assert run.call_count == 1 and original_bytes(root) == before
    json.dumps(receipt)


@pytest.mark.skipif(platform.system() != 'Darwin' and not hasattr(os, 'listxattr'),
                    reason='Native read-only xattr probe requires Darwin or os.listxattr')
def test_native_read_only_attribute_probe_exists_on_supported_python(project):
    root, payload = project
    assert isinstance(permissions._list_attributes(payload / '_entry.bin'), list)


@pytest.mark.parametrize('marker', ['config', 'install'])
def test_discovery_requires_current_project_marker_and_honors_explicit_root(project, tmp_path, marker):
    root, _ = project
    path = root / ('.migbot/config.json' if marker == 'config' else '.hmigbot-ios/install.json')
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({'source_platform': 'ios', 'ios': '/fixture/source'} if marker == 'config'
                               else {'schema_version': 1, 'owner': 'hmigbot-ios', 'files': {}}))
    assert permissions.discover_project_root(cwd=root) == root
    assert permissions.discover_project_root(['--project-root', str(root)], cwd=tmp_path) == root
    assert permissions.discover_project_root(['--project-root=' + str(root)], cwd=tmp_path) == root
    assert permissions.discover_project_root(cwd=tmp_path) is None


def test_untrusted_or_external_marker_cannot_authorize_automatic_repair(project, tmp_path):
    root, _ = project
    cfg = root / '.migbot/config.json'; cfg.parent.mkdir()
    cfg.write_text('{invalid')
    assert permissions.discover_project_root(cwd=root) is None
    cfg.unlink()
    outside = tmp_path / 'external-config.json'
    outside.write_text(json.dumps({'source_platform': 'ios', 'ios': '/fixture/source'}))
    cfg.symlink_to(outside)
    assert permissions.discover_project_root(cwd=root) is None


@pytest.mark.parametrize('system', ['Linux', 'Windows'])
def test_other_platforms_never_inspect_or_remove_macos_attributes(project, system):
    root, payload = project
    with patch.object(permissions.platform, 'system', return_value=system), \
         patch.object(permissions, '_list_attributes') as attrs, \
         patch.object(permissions.subprocess, 'run') as run:
        receipt = permissions.ensure_runtime_permissions(root, payload)
    assert receipt['status'] == 'not_applicable'
    attrs.assert_not_called(); run.assert_not_called()


@pytest.mark.parametrize('root', [Path('/'), Path.home()])
def test_filesystem_and_home_roots_cannot_widen_the_mutation_boundary(root):
    with patch.object(permissions.platform, 'system', return_value='Darwin'), \
         patch.object(permissions, '_list_attributes') as attrs, \
         patch.object(permissions.subprocess, 'run') as run:
        with pytest.raises(permissions.PermissionRepairError, match='project roots'):
            permissions.ensure_runtime_permissions(root, root)
    attrs.assert_not_called(); run.assert_not_called()


@pytest.mark.parametrize('kind', ['absolute', 'traversal', 'sibling_prefix', 'tmp_staging'])
def test_external_targets_are_refused_before_any_attribute_operation(project, tmp_path, kind):
    root, payload = project
    outside = tmp_path / ('project-copy' if kind == 'sibling_prefix' else 'outside')
    outside.mkdir()
    if kind == 'traversal': target = Path('../outside')
    elif kind == 'tmp_staging': target = tmp_path
    else: target = outside
    with patch.object(permissions.platform, 'system', return_value='Darwin'), \
         patch.object(permissions, '_list_attributes') as attrs, \
         patch.object(permissions.subprocess, 'run') as run:
        with pytest.raises(permissions.PermissionRepairError, match='outside') as error:
            permissions.clear_quarantine(root, target)
    assert error.value.receipt['command'] is None
    assert error.value.receipt['mutation_attempted'] is False
    attrs.assert_not_called(); run.assert_not_called()


@pytest.mark.parametrize('kind', ['target', 'child_file', 'child_dir', 'ancestor'])
def test_escaping_symlinks_anywhere_in_the_complete_tree_are_refused(project, tmp_path, kind):
    root, payload = project
    outside = tmp_path / 'outside'; outside.mkdir()
    (outside / 'file').write_text('must not touch')
    target = payload
    if kind == 'target':
        target = root / 'linked'; target.symlink_to(outside, target_is_directory=True)
    elif kind == 'ancestor':
        alias = root / 'linked'; alias.symlink_to(outside, target_is_directory=True)
        target = alias / 'file'
    elif kind == 'child_file': (payload / 'linked').symlink_to(outside / 'file')
    else: (payload / 'linked').symlink_to(outside, target_is_directory=True)
    with patch.object(permissions.platform, 'system', return_value='Darwin'), \
         patch.object(permissions, '_list_attributes') as attrs, \
         patch.object(permissions.subprocess, 'run') as run:
        with pytest.raises(permissions.PermissionRepairError, match='outside'):
            permissions.ensure_runtime_permissions(root, target)
    attrs.assert_not_called(); run.assert_not_called()


def test_internal_symlinks_and_directory_cycle_remain_bounded(project):
    root, payload = project
    (payload / 'linked').symlink_to(payload / 'library.so')
    (payload / 'cycle').symlink_to(payload, target_is_directory=True)
    with patch.object(permissions.platform, 'system', return_value='Darwin'), \
         patch.object(permissions, '_list_attributes', return_value=[]), \
         patch.object(permissions.subprocess, 'run') as run:
        receipt = permissions.ensure_runtime_permissions(root, payload)
    assert receipt['status'] == 'not_needed' and receipt['scanned_paths'] == 5
    run.assert_not_called()


def test_external_hardlink_is_refused(project, tmp_path):
    root, payload = project
    outside = tmp_path / 'outside'; outside.write_text('linked bytes')
    (payload / 'hardlink').hardlink_to(outside)
    with patch.object(permissions.platform, 'system', return_value='Darwin'), \
         patch.object(permissions, '_list_attributes') as attrs, \
         patch.object(permissions.subprocess, 'run') as run:
        with pytest.raises(permissions.PermissionRepairError, match='Hard-linked'):
            permissions.ensure_runtime_permissions(root, payload)
    attrs.assert_not_called(); run.assert_not_called()


def test_symlink_added_after_attribute_probe_is_caught_before_xattr(project, tmp_path):
    root, payload = project
    outside = tmp_path / 'outside'; outside.mkdir()
    def probe(entries):
        (payload / 'late-link').symlink_to(outside, target_is_directory=True)
        return [str(payload / '_entry.bin')]
    with patch.object(permissions.platform, 'system', return_value='Darwin'), \
         patch.object(permissions, '_quarantined', side_effect=probe), \
         patch.object(permissions.subprocess, 'run') as run:
        with pytest.raises(permissions.PermissionRepairError, match='outside'):
            permissions.ensure_runtime_permissions(root, payload)
    run.assert_not_called()


@pytest.mark.parametrize('failure', ['exit', 'timeout', 'oserror', 'attributes_remain'])
def test_failure_never_becomes_success_and_retains_actual_evidence(project, failure):
    root, payload = project
    result = subprocess.CompletedProcess([], 13, 'partial stdout', 'permission denied')
    if failure == 'timeout': result = subprocess.TimeoutExpired([], 120, b'partial stdout', b'timeout stderr')
    elif failure == 'oserror': result = OSError('xattr unavailable')
    elif failure == 'attributes_remain': result.returncode = 0
    options = {'side_effect': result} if isinstance(result, BaseException) else {'return_value': result}
    with patch.object(permissions.platform, 'system', return_value='Darwin'), \
         patch.object(permissions, '_list_attributes', return_value=[permissions.ATTRIBUTE]), \
         patch.object(permissions.subprocess, 'run', **options):
        with pytest.raises(permissions.PermissionRepairError) as error:
            permissions.clear_quarantine(root, payload)
    receipt = error.value.receipt
    assert receipt['status'] == 'failed' and receipt['mutation_attempted'] is True
    assert receipt['mutated'] is None and receipt['product_verified'] is False
    if failure in {'exit', 'timeout'}: assert receipt['stdout'] == 'partial stdout'
    if failure == 'exit': assert receipt['returncode'] == 13 and receipt['stderr'] == 'permission denied'
    json.dumps(receipt)


def test_external_main_runtime_is_never_repaired_or_reclassified_via_copy(project, tmp_path):
    root, payload = project
    external = tmp_path / 'hmigbot-ios-main'; external.mkdir()
    with patch.object(permissions, '_list_attributes') as attrs, \
         patch.object(permissions.subprocess, 'run') as run:
        assert permissions.maybe_prepare_runtime(root, external)['status'] == 'external_runtime'
        assert permissions.maybe_prepare_runtime(None, external)['status'] == 'not_requested'
        alias = root / 'escape'; alias.symlink_to(external, target_is_directory=True)
        with pytest.raises(permissions.PermissionRepairError):
            permissions.maybe_prepare_runtime(root, alias)
    attrs.assert_not_called(); run.assert_not_called()


def test_original_launcher_only_loses_the_exact_implicit_xattr_block():
    helper = ROOT / 'vendor/hmigbot/skills/a2h-spec/scripts/lint_addenda_closure.py'
    original = helper.read_text(encoding='utf-8')
    removed = ('if _OS == "macos":  # idempotent; failure must not block execution\n'
               '    subprocess.run(["xattr", "-dr", "com.apple.quarantine", _DIST],\n'
               '                   check=False, capture_output=True)\n')
    safe = portable_helper.quarantine_free_launcher(original)
    assert safe == original.replace(removed, '# Quarantine preparation is owned by the explicit project boundary.\n')
    assert '"lint_addenda_closure"' in safe and 'os.execv(_EXE, _argv)' in safe
    assert 'os.environ.setdefault("ARKTS_SKILL_DIR", _HERE)' in safe
    assert 'subprocess.run(["xattr"' not in safe
    with pytest.raises(MigrationError):
        portable_helper.quarantine_free_launcher(original.replace('"-dr"', '"-cr"'))
    assert portable_helper.quarantine_free_launcher('print("ordinary helper")\n') == 'print("ordinary helper")\n'


@pytest.mark.parametrize('unicode_path', [False, True])
def test_portable_helper_delegates_directly_and_never_repairs_tmp_copy(project, tmp_path, unicode_path):
    root, _ = project
    scripts = tmp_path / ('外部 helper' if unicode_path else 'external-helper')
    scripts.mkdir()
    helper = scripts / 'original.py'; helper.write_text('# AUTO-GENERATED launcher\n')
    architecture = 'arm64' if platform.machine().lower() in {'arm64', 'aarch64'} else 'x64'
    payload = scripts / 'bin' / ('macos-' + architecture) / '_entry.dist'
    payload.mkdir(parents=True); (payload / '_entry.bin').write_bytes(b'original binary'); (payload / '_entry.bin').chmod(0o755)
    receipts = []
    with patch.object(portable_helper.platform, 'system', return_value='Darwin'), \
         patch.object(permissions, '_list_attributes', return_value=[]) as attrs, \
         patch.object(permissions.subprocess, 'run') as run:
        with portable_helper.command(helper, ['--help'], project_root=root, permission_receipts=receipts) as (command, env):
            assert command[1:] == ['original', '--help']
            assert Path(command[0]).read_bytes() == b'original binary'
            assert env['ARKTS_SKILL_DIR'] == str(scripts)
            assert not command[0].endswith('.py')
        assert receipts[0]['status'] == 'ready'
    assert attrs.call_count > 0; run.assert_not_called()


def test_project_helper_symlink_cannot_hide_an_escaping_runtime(project, tmp_path):
    root, _ = project
    external = tmp_path / 'outside'; external.mkdir()
    helper = external / 'original.py'; helper.write_text('# AUTO-GENERATED launcher\n')
    architecture = 'arm64' if platform.machine().lower() in {'arm64', 'aarch64'} else 'x64'
    payload = external / 'bin' / ('macos-' + architecture) / '_entry.dist'
    payload.mkdir(parents=True); (payload / '_entry.bin').write_bytes(b'original binary')
    alias = root / 'linked.py'; alias.symlink_to(helper)
    with patch.object(portable_helper.platform, 'system', return_value='Darwin'), \
         patch.object(permissions, '_list_attributes') as attrs, \
         patch.object(permissions.subprocess, 'run') as run:
        with pytest.raises(MigrationError, match='outside'):
            with portable_helper.command(alias, ['--help'], project_root=root):
                pytest.fail('Escaping project alias must not create an executable runtime')
    attrs.assert_not_called(); run.assert_not_called()


def test_project_payload_is_prepared_before_unicode_copy_and_stage_is_never_repaired(project):
    root, _ = project
    scripts = root / '项目工具/scripts'; scripts.mkdir(parents=True)
    helper = scripts / 'original.py'; helper.write_text('# AUTO-GENERATED launcher\n')
    architecture = 'arm64' if platform.machine().lower() in {'arm64', 'aarch64'} else 'x64'
    payload = scripts / 'bin' / ('macos-' + architecture) / '_entry.dist'
    payload.mkdir(parents=True); binary = payload / '_entry.bin'; binary.write_bytes(b'original binary')
    flagged = {binary}
    inspected = []
    def attributes(path):
        inspected.append(path)
        assert path.is_relative_to(root)
        return [permissions.ATTRIBUTE] if path in flagged else []
    def mutate(command, **kwargs):
        assert command == ['xattr', '-dr', permissions.ATTRIBUTE, str(payload)]
        flagged.clear()
        return subprocess.CompletedProcess(command, 0, '', '')
    receipts = []
    with patch.object(portable_helper.platform, 'system', return_value='Darwin'), \
         patch.object(permissions, '_list_attributes', side_effect=attributes), \
         patch.object(permissions.subprocess, 'run', side_effect=mutate) as run:
        with pytest.raises(MigrationError, match='init-environment'):
            with portable_helper.command(helper, [], project_root=root):
                pytest.fail('unprepared runtime cannot execute')
        assert run.call_count == 0
        permissions.ensure_runtime_permissions(root, payload)
        binary.chmod(0o755)
        with portable_helper.command(helper, [], project_root=root, permission_receipts=receipts) as (command, _):
            assert not flagged and receipts[0]['status'] == 'ready'
            assert not Path(command[0]).is_relative_to(root)  # Existing ASCII layout workaround only.
            assert Path(command[0]).read_bytes() == b'original binary'
    assert inspected and run.call_count == 1
    assert binary.read_bytes() == b'original binary'


def test_run_uses_only_a_marked_cwd_as_implicit_project_boundary(project):
    root, _ = project
    cfg = root / '.migbot/config.json'; cfg.parent.mkdir()
    cfg.write_text(json.dumps({'source_platform': 'ios', 'ios': '/fixture/source'}))
    scripts = root / 'scripts'; scripts.mkdir()
    helper = scripts / 'original.py'; helper.write_text('# AUTO-GENERATED launcher\n')
    architecture = 'arm64' if platform.machine().lower() in {'arm64', 'aarch64'} else 'x64'
    payload = scripts / 'bin' / ('macos-' + architecture) / '_entry.dist'
    payload.mkdir(parents=True); binary = payload / '_entry.bin'; binary.write_bytes(b'original binary')
    flagged = {binary}
    def attributes(path):
        return [permissions.ATTRIBUTE] if path in flagged else []
    def execute(command, **kwargs):
        if command[0] == 'xattr':
            assert command[-1] == str(payload); flagged.clear()
            return subprocess.CompletedProcess(command, 0, '', '')
        assert command == [str(binary), 'original', '--help']
        assert kwargs['cwd'] == root and kwargs['shell'] is False
        return subprocess.CompletedProcess(command, 0, 'helper stdout', 'helper stderr')
    with patch.object(portable_helper.platform, 'system', return_value='Darwin'), \
         patch.object(permissions, '_list_attributes', side_effect=attributes), \
         patch.object(permissions.subprocess, 'run', side_effect=execute):
        with pytest.raises(MigrationError, match='init-environment'):
            portable_helper.run(helper, ['--help'], cwd=root, capture_output=True, text=True)
        permissions.ensure_runtime_permissions(root, payload)
        binary.chmod(0o755)
        result = portable_helper.run(helper, ['--help'], cwd=root, capture_output=True, text=True)
    assert result.stdout == 'helper stdout' and result.stderr == 'helper stderr'
    assert result.macos_permission_receipts[0]['status'] == 'ready'


@pytest.mark.parametrize('program', ['state_update', 'next_batch', 'land_results'])
def test_actual_scheduler_launcher_quarantine_try_is_removed_without_changing_other_code(program):
    import ast
    source = ROOT/'vendor/hmigbot-1.7.0/skills/a2h-execute/scripts'/(program+'.py')
    text = source.read_text()
    tree = ast.parse(text)
    block = next(n for n in tree.body if isinstance(n,ast.If) and isinstance(n.body[0],ast.Try))
    safe = portable_helper.quarantine_free_launcher(text)
    lines = text.splitlines(keepends=True)
    expected = ''.join(lines[:block.lineno-1]+['# Quarantine preparation is owned by the explicit project boundary.\n']+lines[block.end_lineno:])
    assert safe == expected and '"xattr"' not in safe
    compile(safe, str(source), 'exec')


def test_scheduler_permission_evidence_is_separate_from_original_action(tmp_path):
    from contextlib import contextmanager
    from hmigbot_ios import ios_scheduler
    project=tmp_path/'project'; project.mkdir()
    stage=tmp_path/'stage'; stage.mkdir()
    @contextmanager
    def runtime(*args, **kwargs):
        yield str(stage)
    action={'ok':False,'landed':[{'id':'fixture','status':'failed'}]}
    receipt={'status':'external_runtime','mutated':False,'command':None,'product_verified':False}
    with patch.object(ios_scheduler.platform,'system',return_value='Darwin'), \
         patch.object(ios_scheduler,'_runtime_directory',side_effect=runtime), \
         patch('hmigbot_ios.macos_permissions.maybe_prepare_runtime',return_value=receipt), \
         patch.object(ios_scheduler.subprocess,'run',return_value=subprocess.CompletedProcess([],0,json.dumps(action).encode(),b'')):
        actual=ios_scheduler.invoke(project,'land_results',[])
    assert actual==action
    assert json.loads((project/'spec/reports/scheduler/land_results.stdout.log').read_text())==action
    evidence=json.loads((project/'spec/reports/scheduler/land_results.permissions.json').read_text())
    assert evidence['kind']=='tool_runtime_permissions' and not evidence['product_verified']
    assert ios_scheduler._execution_evidence('spec/reports/scheduler/land_results.permissions.json')
    assert not ios_scheduler._execution_evidence('entry/product.permissions.json')
