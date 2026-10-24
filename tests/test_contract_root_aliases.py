"""Equivalent filesystem roots must freeze the same real shared contracts."""
import pytest

from test_ios_harness import fixture


@pytest.mark.parametrize('consumer', ['dependency', 'baseline', 'quality'])
def test_project_root_alias_keeps_transitive_contract_closure(tmp_path, consumer):
    _, project, _ = fixture(tmp_path)
    alias = tmp_path / 'project-alias'
    try:
        alias.symlink_to(project, target_is_directory=True)
    except OSError as exc:
        pytest.skip('Filesystem cannot create a directory alias: ' + str(exc))
    from hmigbot_ios.spec_contract import dependency_inputs
    from hmigbot_ios.ios_scheduler import baseline_inputs
    from hmigbot_ios.quality_views import spec_inputs
    consume = {'dependency': dependency_inputs, 'baseline': lambda p: baseline_inputs(p, 'domains'),
               'quality': spec_inputs}[consumer]
    expected = consume(project)
    assert 'spec/baseline/feature-base.md' in expected
    assert consume(alias) == expected


@pytest.mark.parametrize('consumer', ['validate', 'units', 'task', 'indexed'])
def test_plan_consumers_accept_the_same_project_directory_alias(consumer):
    from test_plan_contract import PlanContractTests
    from hmigbot_ios.plan_contract import validate_plan, plan_units, task_inputs, indexed_contract_inputs
    case = PlanContractTests()
    case.setUp()
    try:
        index = case.base / 'feature-index.md'
        index.write_text(index.read_text().replace('| 无 |', '| ["spec/ref/shared.md#Public"] |'))
        alias = case.project.parent / (case.project.name + '-alias')
        try:
            alias.symlink_to(case.project.resolve(), target_is_directory=True)
        except OSError as exc:
            pytest.skip('Filesystem cannot create a directory alias: ' + str(exc))
        try:
            consume = {
                'validate': lambda p: validate_plan(p, case.request),
                'units': plan_units,
                'task': lambda p: task_inputs(p, case.request['tasks'][1]),
                'indexed': indexed_contract_inputs,
            }[consumer]
            expected = consume(case.project.resolve())
            assert expected
            assert consume(alias) == expected
        finally:
            alias.unlink()
    finally:
        case.tearDown()


def test_tool_revision_freezes_code_imported_through_directory_alias(tmp_path):
    from unittest.mock import patch
    from hmigbot_ios import plan_contract
    _, project, _ = fixture(tmp_path)
    runtime = tmp_path / 'runtime'
    module = runtime / 'src/hmigbot_ios/plan_contract.py'
    module.parent.mkdir(parents=True)
    module.write_text('fixture plan rules')
    helper = module.with_name('objc_state.py')
    helper.write_text('original extractor')
    alias = tmp_path / 'runtime-alias'
    try:
        alias.symlink_to(runtime, target_is_directory=True)
    except OSError as exc:
        pytest.skip('Filesystem cannot create a directory alias: ' + str(exc))
    with patch('hmigbot_ios.artifact_contract.revision', return_value='same-catalog'), \
            patch('hmigbot_ios.source_responsibility.parser_fingerprints', return_value={}):
        with patch.object(plan_contract, '__file__', str(module)):
            expected = plan_contract.contract_revision(project)
        with patch.object(plan_contract, '__file__', str(alias / 'src/hmigbot_ios/plan_contract.py')):
            assert plan_contract.contract_revision(project) == expected
            helper.write_text('changed extractor')
            assert plan_contract.contract_revision(project) != expected
