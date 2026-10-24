"""The public repair command always supplies one identified project boundary."""
from pathlib import Path
from unittest.mock import patch

import pytest

from hmigbot_ios.core import write_json
from hmigbot_ios.native_pipeline import main


def test_permissions_cli_requires_identified_migration_project(tmp_path, capsys):
    with patch('hmigbot_ios.macos_permissions.ensure_runtime_permissions') as repair:
        assert main(['repair-permissions', '--project', str(tmp_path)]) == 2
        repair.assert_not_called()
    assert 'configured or installed migration project' in capsys.readouterr().out


def test_permissions_cli_resolves_relative_target_inside_project(tmp_path, capsys):
    write_json(tmp_path/'.hmigbot-ios/install.json', {'owner':'hmigbot-ios'})
    target = tmp_path/'payload/_entry.dist'
    target.mkdir(parents=True)
    with patch('hmigbot_ios.macos_permissions.ensure_runtime_permissions', return_value={'status':'not_needed'}) as repair:
        assert main(['repair-permissions','--project',str(tmp_path),'--path','payload/_entry.dist']) == 0
        repair.assert_called_once_with(tmp_path.resolve(), target)
    assert 'not_needed' in capsys.readouterr().out


def test_permissions_cli_rejects_external_target_without_xattr(tmp_path, capsys):
    from hmigbot_ios.macos_permissions import subprocess
    project = tmp_path/'project'
    outside = tmp_path/'outside'
    project.mkdir(); outside.mkdir()
    write_json(project/'.hmigbot-ios/install.json', {'owner':'hmigbot-ios'})
    with patch.object(subprocess, 'run') as run:
        assert main(['repair-permissions','--project',str(project),'--path',str(outside)]) == 2
        run.assert_not_called()
    assert capsys.readouterr().out
