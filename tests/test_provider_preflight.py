"""Reject a malformed whole plan before running providers or replacing facts."""
from pathlib import Path
import tempfile
from unittest.mock import patch

import pytest

from hmigbot_ios.core import MigrationError, write_json
from hmigbot_ios.ios_facts import extract, refresh
from hmigbot_ios.atoms import run_atom


@pytest.fixture
def tmp_path():
    # Keep real provider attempt paths below legacy Windows path limits.
    with tempfile.TemporaryDirectory(prefix='pf-') as directory:
        yield Path(directory)


@pytest.mark.parametrize('entries', [
    [None], ['swift-syntax'], [{'operation': 'not-a-provider'}],
    [{'operation': 'swift-syntax'}], [{'operation': 'clang-ast'}],
    [{'operation': 'build-settings'}],
    [{'operation': 'asset-inventory', 'config': []}],
    [{'operation': 'asset-inventory', 'input': ''}],
    [{'operation': 'interface-builder'}, {'operation': 'interface-builder'}],
])
def test_whole_plan_is_checked_before_source_capture_or_provider_execution(tmp_path, entries):
    source, project = tmp_path / 'source', tmp_path / 'target'
    source.mkdir(); project.mkdir()
    plan = tmp_path / 'providers.json'
    write_json(plan, {'schema_version': 2, 'providers': [{'operation': 'asset-inventory'}, *entries]})
    baseline = project / 'spec/baseline/ios-facts.json'
    write_json(baseline, {'preserved': True})
    before = baseline.read_bytes()
    with patch('hmigbot_ios.ios_facts.extract', wraps=extract) as capture, patch('hmigbot_ios.atoms.run_atom', wraps=run_atom) as atom:
        with pytest.raises(MigrationError, match='Provider plan'):
            refresh(project, source, provider_plan=plan)
        capture.assert_not_called()
        atom.assert_not_called()
    assert baseline.read_bytes() == before
    assert not (project / 'spec/ref/provider-runs').exists()


def test_missing_referenced_configuration_is_preflight_failure(tmp_path):
    source, project = tmp_path / 'source', tmp_path / 'target'
    source.mkdir(); project.mkdir()
    plan = tmp_path / 'providers.json'
    write_json(plan, {'schema_version': 2, 'providers': [
        {'operation': 'interface-builder'},
        {'operation': 'swift-syntax', 'config': str(tmp_path / 'absent.json')},
    ]})
    with patch('hmigbot_ios.atoms.run_atom', wraps=run_atom) as atom:
        with pytest.raises(MigrationError, match='Provider plan'):
            refresh(project, source, provider_plan=plan)
        atom.assert_not_called()
    assert not (project / 'spec/baseline/ios-facts.json').exists()


@pytest.mark.parametrize('input_kind', ['file', 'directory_without_manifest'])
def test_any_explicit_input_must_be_a_bundle_before_earlier_provider_runs(tmp_path, input_kind):
    source, project = tmp_path / 'source', tmp_path / 'target'
    source.mkdir(); project.mkdir()
    input_path = tmp_path / 'input'
    if input_kind == 'file':
        write_json(input_path, {})
    else:
        input_path.mkdir()
    baseline = project / 'spec/baseline/ios-facts.json'
    write_json(baseline, {'preserved': True})
    before = baseline.read_bytes()
    plan = tmp_path / 'providers.json'
    write_json(plan, {'schema_version': 2, 'providers': [
        {'operation': 'interface-builder'},
        {'operation': 'build-settings', 'input': str(input_path)},
    ]})
    with patch('hmigbot_ios.atoms.run_atom', wraps=run_atom) as atom:
        with pytest.raises(MigrationError, match='Provider plan'):
            refresh(project, source, provider_plan=plan)
        atom.assert_not_called()
    assert baseline.read_bytes() == before


def test_valid_builtin_plan_still_captures_and_validates(tmp_path):
    from hmigbot_ios.ios_facts import validate_graph
    source, project = tmp_path / 'source', tmp_path / 'target'
    source.mkdir(); project.mkdir()
    (source / 'App.swift').write_text('struct App {}\n', encoding='utf-8')
    plan = tmp_path / 'providers.json'
    write_json(plan, {'schema_version': 2, 'providers': [
        {'operation': 'interface-builder'}, {'operation': 'asset-inventory'},
        {'operation': 'localization-inventory'},
    ]})
    graph = refresh(project, source, provider_plan=plan)
    assert len(graph['provider_artifacts']) == 3
    assert validate_graph(source, project)[0] == graph


def test_empty_plan_is_equivalent_to_no_provider_and_round_trips(tmp_path):
    from hmigbot_ios.ios_facts import validate_graph
    source, project = tmp_path / 'source', tmp_path / 'target'
    source.mkdir(); project.mkdir()
    (source / 'App.swift').write_text('struct App {}\n', encoding='utf-8')
    plan = tmp_path / 'providers.json'
    write_json(plan, {'schema_version': 2, 'providers': []})
    graph = refresh(project, source, provider_plan=plan)
    assert validate_graph(source, project)[0] == graph


def test_duplicate_alias_is_rejected_but_distinct_configurations_remain_valid(tmp_path):
    from hmigbot_ios.provider_plan import preflight
    config, other = tmp_path / 'config.json', tmp_path / 'other.json'
    write_json(config, {}); write_json(other, {})
    plan = tmp_path / 'providers.json'
    first = {'operation': 'swift-syntax', 'config': str(config)}
    write_json(plan, {'schema_version': 2, 'providers': [
        first, {'operation': 'swift-syntax', 'config': str(other)}]})
    assert len(preflight(plan)) == 2
    write_json(plan, {'schema_version': 2, 'providers': [
        first, {'operation': 'swift-syntax', 'config': str(tmp_path / '.' / 'config.json')}]})
    with pytest.raises(MigrationError, match='duplicates'):
        preflight(plan)
