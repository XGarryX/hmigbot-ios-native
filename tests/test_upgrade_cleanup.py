"""Recognized old derived outputs are cleaned, authored contracts are retained."""
import json
from unittest.mock import patch
import pytest
from hmigbot_ios.core import MigrationError


def prepare(*args, **kwargs):
    from hmigbot_ios.upgrade_cleanup import prepare_upgrade_cleanup
    return prepare_upgrade_cleanup(*args, **kwargs)


def write(root, relative, value):
    path=root/relative; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(value if isinstance(value,str) else json.dumps(value))
    return path


@pytest.fixture
def case(tmp_path):
    root=tmp_path/'project'; root.mkdir()
    write(root,'spec/baseline/ios-facts.json',{'schema_version':2,'source_platform':'ios',
        'source_sha256':'a'*64,'facts':[],'issues':[],'variant':{'scope':'repository'}})
    write(root,'spec/migration-report.md','# Derived\n<!-- hmigbot-derived-report:2 -->\nnot_run\n')
    for r in ['spec/baseline/ios-source-index.json','spec/baseline/ios-semantics.json',
              'spec/baseline/ios-coverage.json','spec/baseline/ios-responsibility.json',
              'spec/baseline/features/F001-app.md','spec/decision-ledger.md','spec/ref/raw.json',
              'spec/state/state.json','spec/state/dispatch.json','spec/state/journal.json',
              'spec/blueprint/contracts.json','entry/App.ets']:
        write(root,r,'User reviewed content\n')
    write(root, 'spec/state/dispatch.json', {'waves': {}})
    write(root, 'spec/state/journal.json', {'workflow_status': []})
    return root


def snapshot(root):
    return {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}


def test_prepare_readonly_and_filename_alone_never_authorizes_cleanup(case):
    write(case,'spec/reports/spec-summary.json',{'user_notes':'preserve'})
    before=snapshot(case); tx=prepare(case,'old','new')
    assert snapshot(case)==before
    assert not (case/'.hmigbot-ios').exists()
    assert len(tx.receipt['files'])==2
    assert tx.receipt['preserved'][0]['path']=='spec/reports/spec-summary.json'


def test_archive_cleanup_commit_preserves_authored_and_control_bytes(case):
    before=snapshot(case); tx=prepare(case,'old','new'); tx.apply()
    for row in tx.receipt['files']:
        assert not (case/row['path']).exists()
        assert (case/tx.receipt['archive']/'generated'/row['path']).read_bytes()==before[row['path']]
    tx.commit(); assert tx.receipt['status']=='committed'
    removed={r['path'] for r in tx.receipt['files']}
    assert all((case/r).read_bytes()==data for r,data in before.items() if r not in removed)
    assert json.loads((case/tx.receipt['archive']/'cleanup.json').read_text())['status']=='committed'


def test_failed_install_rollback_restores_bytes_and_permissions(case):
    path=case/'spec/baseline/ios-facts.json'; path.chmod(0o640)
    before=snapshot(case); tx=prepare(case,'old','new'); tx.apply(); tx.rollback()
    assert all((case/r).read_bytes()==body for r,body in before.items())
    assert path.stat().st_mode & 0o777 == 0o640
    assert tx.receipt['status']=='rolled_back'
    tx.rollback()


def test_drift_after_preview_refuses_all_cleanup(case):
    tx=prepare(case,'old','new'); p=case/'spec/baseline/ios-facts.json'; p.write_bytes(p.read_bytes()+b' ')
    before=snapshot(case)
    with pytest.raises(MigrationError,match='input changed'): tx.apply()
    assert snapshot(case)==before


def test_partial_cleanup_failure_restores_removed_files(case):
    tx=prepare(case,'old','new'); before=snapshot(case); original=tx._check; calls=0
    def check(row):
        nonlocal calls
        calls+=1
        if calls==6: raise OSError('simulated removal failure')
        return original(row)
    with patch.object(tx,'_check',side_effect=check):
        with pytest.raises(OSError,match='simulated removal failure'): tx.apply()
    assert all((case/r).read_bytes()==body for r,body in before.items())
    assert tx.receipt['status']=='rolled_back'


@pytest.mark.parametrize('location',['spec','leaf','archive'])
def test_symlink_candidate_or_archive_refused(case,tmp_path,location):
    outside=tmp_path/'outside'; outside.mkdir(); (outside/'sentinel').write_text('outside')
    try:
        if location=='spec':
            (case/'spec').rename(case/'saved-spec'); (case/'spec').symlink_to(outside,target_is_directory=True)
        elif location=='leaf':
            p=case/'spec/baseline/ios-facts.json'; p.unlink(); p.symlink_to(outside/'sentinel')
        else:
            (case/'.hmigbot-ios').mkdir(); (case/'.hmigbot-ios/upgrade-history').symlink_to(outside,target_is_directory=True)
    except OSError as exc: pytest.skip('Filesystem cannot create links: '+str(exc))
    with pytest.raises(MigrationError,match='linked'): prepare(case,'old','new')
    assert list(outside.iterdir())==[outside/'sentinel']
    assert (outside/'sentinel').read_text()=='outside'


@pytest.mark.parametrize('old,changed',[(None,True),('same',False)])
def test_initial_or_unchanged_install_does_not_clean(case,old,changed):
    before=snapshot(case); tx=prepare(case,old,'same',tool_changed=changed)
    tx.apply(); tx.commit(); tx.rollback()
    assert tx.receipt['status']=='not_needed' and snapshot(case)==before


def test_same_version_changed_tool_still_cleans(case):
    tx=prepare(case,'same','same',tool_changed=True); tx.apply(); tx.commit()
    assert tx.receipt['status']=='committed'


def test_rollback_preserves_concurrent_new_output(case):
    tx=prepare(case,'old','new'); tx.apply(); p=case/'spec/migration-report.md'; p.write_text('new output')
    with pytest.raises(MigrationError,match='concurrent edit'): tx.rollback()
    assert p.read_text()=='new output'
    assert (case/'spec/baseline/ios-facts.json').is_file()
