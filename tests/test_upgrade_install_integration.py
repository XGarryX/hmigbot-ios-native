"""Upgrade cleanup is ordered, reversible and separate from authored progress."""
import importlib.util
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()


def installer():
    spec = importlib.util.spec_from_file_location('cleanup_install_test', ROOT / 'scripts/manage_install.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else json.dumps(data))


def setup(tmp_path):
    module = installer()
    project = tmp_path / 'project'
    project.mkdir()
    payload = {'.hmigbot-ios/plugin/.codex-plugin/plugin.json': b'{"version":"fixture"}',
               '.hmigbot-ios/plugin/fixture.txt': b'new tool'}
    with patch.object(module, 'payload', return_value=payload):
        module.manage(project, 'install')
    manifest = project / '.hmigbot-ios/install.json'
    metadata = json.loads(manifest.read_text())
    metadata['version'] = '0.1.0'
    write(manifest, metadata)
    write(project / 'spec/reports/spec-summary.json', {'schema_version': 2, 'source_sha256': 'a'*64,
        'axes': {k:{'status':'not_run'} for k in ('generation','compilation','behavior','visual')}, 'counts': {'acceptance':0,'features':0,'pages':0}, 'behavior_verified': False, 'inputs':{}, 'pages':[], 'legacy_progress':{}, 'placeholders':{}, 'scope':'Derived machine report'})
    authored = {'spec/baseline/ios-semantics.json': {'documents': [{'facts': {'status': 'unknown'}}]},
        'spec/baseline/ios-coverage.json': {'mappings': ['reviewed by user']},
        'spec/baseline/ios-responsibility.json': {'review': 'reviewed by user'},
        'spec/baseline/ios-source-index.json': {'source_sha256': 'b'*64},
        'spec/decision-ledger.md': '# User decisions\n',
        'spec/baseline/features/F001-user.md': '# User AC\n',
        'spec/state/state.json': {'tasks': []}, 'spec/state/dispatch.json': {},
        'spec/state/journal.json': {}, 'entry/User.ets': 'class User {}'}
    for path, data in authored.items():
        write(project / path, data)
    return module, project, payload, {r: (project/r).read_bytes() for r in authored}


def test_upgrade_archives_generated_before_tool_write_and_preserves_user_contracts(tmp_path):
    module, project, payload, authored = setup(tmp_path)
    generated = project/'spec/reports/spec-summary.json'
    before = generated.read_bytes()
    original_put = module.put
    seen = []
    def checked_put(path, data):
        if Path(path).is_relative_to(project) and '.hmigbot-ios/plugin' in str(path):
            seen.append(not generated.exists())
        return original_put(path, data)
    # Change actual tool bytes so this also tests the same-version patch path.
    payload['.hmigbot-ios/plugin/fixture.txt'] = b'updated tool'
    with patch.object(module, 'payload', return_value=payload), patch.object(module, 'put', side_effect=checked_put):
        result = module.manage(project, 'install')
    assert seen and all(seen)
    assert not generated.exists()
    archived = list((project/'.hmigbot-ios/upgrade-history').rglob('spec-summary.json'))
    assert len(archived) == 1 and archived[0].read_bytes() == before
    assert result['upgrade_cleanup']['status'] == 'committed'
    assert all((project/r).read_bytes() == body for r, body in authored.items())


def test_failed_upgrade_restores_generated_and_prior_tool_manifest(tmp_path):
    module, project, payload, authored = setup(tmp_path)
    generated = project/'spec/reports/spec-summary.json'
    before = generated.read_bytes()
    manifest = (project/'.hmigbot-ios/install.json').read_bytes()
    payload['.hmigbot-ios/plugin/fixture.txt'] = b'updated tool'
    original_put = module.put
    tripped = False
    def fail_once(path, data):
        nonlocal tripped
        if Path(path).is_relative_to(project) and not tripped:
            tripped = True
            assert not generated.exists()
            raise OSError('simulated install failure after cleanup')
        return original_put(path, data)
    with patch.object(module, 'payload', return_value=payload), patch.object(module, 'put', side_effect=fail_once):
        with pytest.raises(OSError, match='simulated install failure'):
            module.manage(project, 'install')
    assert generated.read_bytes() == before
    assert (project/'.hmigbot-ios/install.json').read_bytes() == manifest
    assert (project/'.hmigbot-ios/plugin/fixture.txt').read_bytes() == b'new tool'
    assert all((project/r).read_bytes() == body for r, body in authored.items())


def test_edited_managed_file_blocks_before_cleanup(tmp_path):
    module, project, payload, _ = setup(tmp_path)
    generated = project/'spec/reports/spec-summary.json'
    body = generated.read_bytes()
    (project/'.hmigbot-ios/plugin/fixture.txt').write_bytes(b'user edit')
    with patch.object(module, 'payload', return_value=payload):
        with pytest.raises(ValueError, match='user-edited'):
            module.manage(project, 'install')
    assert generated.read_bytes() == body
    assert not (project/'.hmigbot-ios/upgrade-history').exists()
