"""Cross-capability regressions for the single native pipeline."""
import json
from pathlib import Path
from unittest.mock import patch
import pytest
from hmigbot_ios.core import MigrationError, read_json, snapshot, write_json
from hmigbot_ios.native_pipeline import configure, index_source


def project(tmp_path):
    source, target = tmp_path/'source', tmp_path/'target'
    source.mkdir(); target.mkdir()
    configure(source, target)
    return source, target


def test_objc_line_continuation_and_swift_bounds_share_facts_and_literals(tmp_path):
    from hmigbot_ios.analyze import analyze
    from hmigbot_ios.ios_facts import extract
    from hmigbot_ios.ios_literals import extract as literals
    from hmigbot_ios.swiftui import tokenize
    source, target = project(tmp_path)
    (source/'Model.m').write_text('#pragma mark "unclosed heading\n@interface Model : NSObject\n@property int count;\n@end\n@implementation Model\n- (void)run { NSString *s = @"hello\\\nworld"; self.count = 1; }\n@end\n')
    (source/'View.swift').write_text('struct View { var count: Int { 1 } var id: Int { self.count } }')
    graph = extract(source)
    assert any(f['kind']=='state' and f['symbol']=='count' and f['anchor']['path']=='Model.m' for f in graph['facts'])
    assert any(f['kind']=='state' and f['value'].get('storage')=='computed_property' for f in graph['facts'])
    analyze(source); assert literals(source)['files_scanned'] == 2
    with pytest.raises(MigrationError):
        tokenize('let s = "hello\\\nworld"')


def test_provider_config_precedence_ignores_unconsumed_invalid_input(tmp_path):
    from hmigbot_ios.provider_plan import preflight
    from hmigbot_ios.provider_runs import ProviderRun
    from hmigbot_ios.ios_facts import refresh, validate_graph
    source, target = project(tmp_path)
    (source/'Model.swift').write_text('struct Model {}')
    config=tmp_path/'xcode.json'; write_json(config, {'project':'Example.xcodeproj'})
    plan=tmp_path/'providers.json'; write_json(plan, {'schema_version':2,'providers':[
        {'operation':'build-settings','config':str(config),'input':str(tmp_path/'absent')}]})
    assert 'input' not in preflight(plan)[0]
    with patch('hmigbot_ios.atoms.xcodebuild_settings', return_value={'targets':[], 'evidence':'fixture'}) as execute:
        first=refresh(target,source,provider_plan=plan)
    assert execute.call_count == 1
    artifact=target/first['provider_artifacts'][0]['path']
    assert read_json(artifact)['input_mode'] == 'direct_xcodebuild'
    assert read_json(artifact.parent/'run.json')['input_sha256'] is None
    validate_graph(source,target)
    run=ProviderRun(target,'build-settings',snapshot(source)['sha256'],config=config,input_path=tmp_path/'absent')
    with pytest.raises(MigrationError):
        # fixed_inputs cannot run before an exclusive reservation.
        with run.fixed_inputs():
            pass


def test_preview_is_pure_and_same_renderer_as_facts(tmp_path):
    from hmigbot_ios.ios_facts import refresh
    from hmigbot_ios.native_scaffold import scaffold, apply_scaffold
    from hmigbot_ios.gate_artifacts import render_spec_inputs, generate_spec_gates
    source, target=project(tmp_path)
    (source/'View.swift').write_text('import SwiftUI\nstruct MainScreen: View { var body: some View { Text("hello") } }')
    index_source(target); refresh(target,source)
    before={str(p.relative_to(target)):p.read_bytes() for p in target.rglob('*') if p.is_file()}
    candidate=scaffold(target)
    after={str(p.relative_to(target)):p.read_bytes() for p in target.rglob('*') if p.is_file()}
    assert before == after
    rendered=render_spec_inputs(target)
    assert all(rendered['files'][path]==text for path,text in candidate['file_contents'].items())
    old=dict(candidate,schema_version=1)
    with pytest.raises(MigrationError,match='regenerate'):
        apply_scaffold(target,old)
    apply_scaffold(target,candidate); generate_spec_gates(target)
    assert all((target/path).read_text()==text for path,text in candidate['file_contents'].items())
    assert (target/'spec/baseline/ios-semantics.json').is_file()


def test_init_prepares_only_known_entries_and_rechecks_live_state(tmp_path):
    from hmigbot_ios.init_environment import run, check_runtime_ready, REPORT
    source,target=project(tmp_path)
    runtime=target/'.hmigbot-ios/plugin'; runtime.mkdir(parents=True)
    binary=runtime/'known'; binary.write_text('#!/bin/sh\nexit 0\n'); binary.chmod(0o644)
    other=runtime/'unlisted'; other.write_text('source data'); other.chmod(0o644)
    write_json(runtime/'runtime-entrypoints.json',{'schema_version':1,'entries':['known']})
    assert run(target,runtime)['status']=='preparation_required'
    assert not (target/REPORT).exists()
    first=run(target,runtime,prepare=True)
    assert first['status']=='ready' and len(first['actions'])==1
    assert other.stat().st_mode & 0o111 == 0
    assert run(target,runtime,prepare=True)['actions']==[]
    check_runtime_ready(target,binary)
    binary.chmod(0o644)
    with patch('hmigbot_ios.init_environment.platform.system',return_value='Darwin'):
        with pytest.raises(MigrationError,match='init-environment'):
            check_runtime_ready(target,binary)
    assert binary.stat().st_mode & 0o111 == 0


def test_budget_lock_fence_is_precise(tmp_path):
    from hmigbot_ios.ios_scheduler import execution_files
    write_json(tmp_path/'.migbot/config.json', {'source_platform':'ios'})
    for path in ['spec/reports/derived/usage-budget.json.lock','spec/baseline/usage-budget.json.lock','entry/usage-budget.json.lock','spec/reports/derived/unrelated.json']:
        dest=tmp_path/path; dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text('locked')
    files=execution_files(tmp_path)
    assert 'spec/reports/derived/usage-budget.json.lock' not in files
    assert 'spec/baseline/usage-budget.json.lock' in files
    assert 'entry/usage-budget.json.lock' in files
    assert 'spec/reports/derived/unrelated.json' in files


def test_upgrade_refuses_inflight_before_cleaning_and_preserves_budget(tmp_path):
    from hmigbot_ios.upgrade_cleanup import prepare_upgrade_cleanup
    write_json(tmp_path/'spec/state/dispatch.json', {'waves': {'domains': {'dispatched': {'task': {'attempts':1}}}}})
    ledger=tmp_path/'spec/reports/derived/usage-budget.json'; ledger.parent.mkdir(parents=True);ledger.write_text('budget audit bytes')
    with pytest.raises(MigrationError,match='In-flight'):
        prepare_upgrade_cleanup(tmp_path,'0.11.0','0.12.0',tool_changed=True)
    assert ledger.read_text()=='budget audit bytes'


def test_verification_scope_maps_alias_and_does_not_guess_behavior():
    from hmigbot_ios.verification_scope import resolve
    assert resolve({'checks':['CHECK-4']})['behavior']=='pending'
    selected=resolve({'checks':['CHECK-3','CHECK-5'],'authorized_cases':True,'run_behavior':True})
    assert selected['execution_order']==['CHECK-1','CHECK-2','CHECK-3','behavior-check']
    assert selected==resolve({'checks':['CHECK-3'],'behavior':'selected','authorized_cases':True,'run_behavior':True})
    assert selected['overall_checks']==['CHECK-1','CHECK-2','CHECK-3']
    with pytest.raises(MigrationError):
        resolve({'run_behavior':True,'authorized_cases':True})


def test_unselected_behavior_report_never_reads_old_behavior_evidence(tmp_path):
    from test_ios_harness import fixture
    from hmigbot_ios.gate_artifacts import generate_verify_report
    source,target,graph=fixture(tmp_path)
    old=target/'spec/reports/ios-behavior-check.json';old.parent.mkdir(parents=True,exist_ok=True);old.write_text('invalid old report must never be read')
    cases=target/'spec/verification/ios-behavior.json';cases.parent.mkdir(parents=True,exist_ok=True);cases.write_text('invalid unselected cases')
    result=generate_verify_report(target,write=False,scope={'behavior':'not_selected'})
    assert '用户未选择' in result['markdown']
    assert old.read_text()=='invalid old report must never be read'


def test_responsibility_uses_unicode_adapter_around_original_inventory(tmp_path):
    from test_spec_helper_objects import account_doc
    from hmigbot_ios.source_responsibility import acceptance_inventory
    folder=tmp_path/'spec/baseline/features';folder.mkdir(parents=True)
    (folder/'F001-账号.md').write_text(account_doc(2))
    result=acceptance_inventory(tmp_path)
    assert set(result['all'])=={'F001-AC01','F001-AC02'}
    assert not (tmp_path/'spec/.a2h/requirements-index.json').exists()


def test_xcode_link_rpath_is_not_a_compiler_response_file(tmp_path):
    import subprocess
    from hmigbot_ios.providers import xcodebuild_compile_commands
    (tmp_path/'Project.xcodeproj').mkdir()
    response=tmp_path/'flags.resp';response.write_text('-DREAL=1')
    log=(f'/tool/clang -install_name @rpath/App.debug.dylib -o App\n'
         f'/tool/clang @{response} -c Model.m -o Model.o\n').encode()
    with patch('hmigbot_ios.providers.subprocess.run',return_value=subprocess.CompletedProcess([],0,log,b'')):
        capture=xcodebuild_compile_commands(tmp_path,{'project':'Project.xcodeproj'},derived_data=tmp_path/'Derived')
    assert capture['compiler_commands']==[['/tool/clang','-DREAL=1','-c','Model.m','-o','Model.o']]


def test_xcode_failure_retains_complete_stdout_in_provider_attempt(tmp_path):
    import subprocess
    from hmigbot_ios.ios_facts import refresh
    source,target=project(tmp_path)
    (source/'Model.m').write_text('@interface Model @end')
    config=tmp_path/'clang.json';write_json(config,{'xcodebuild':{'project':'Project.xcodeproj'}})
    plan=tmp_path/'plan.json';write_json(plan,{'schema_version':2,'providers':[{'operation':'clang-ast','config':str(config)}]})
    with patch('hmigbot_ios.providers.subprocess.run',return_value=subprocess.CompletedProcess([],65,b'actual full stdout error',b'build failed')):
        with pytest.raises(MigrationError,match='retained diagnostics'):
            refresh(target,source,provider_plan=plan)
    failure=next((target/'spec/ref/provider-runs').rglob('failure.json'))
    assert (failure.parent/'xcodebuild.stdout.log').read_bytes()==b'actual full stdout error'
    assert 'xcodebuild.stdout.log' in read_json(failure)['diagnostics']
    assert not (target/'spec/baseline/ios-facts.json').exists()


def test_membership_aliases_are_versioned_and_limited_to_darwin_system_paths(tmp_path):
    from hmigbot_ios.source_build_membership import _classify, _path_aliases
    aliases=_path_aliases({'schema_version':2,'path_aliases':[{'from':'/tmp','to':'/private/tmp'}]})
    assert _classify('/tmp/source/Model.swift','/private/tmp/source','/private/tmp/build',tmp_path,{'Model.swift':{}},aliases)[0:2]==('member','Model.swift')
    assert _classify('/tmp/source/../escape.swift','/private/tmp/source','',tmp_path,{},aliases)[0]=='escaping'
    with pytest.raises(MigrationError):
        _path_aliases({'schema_version':1,'path_aliases':[{'from':'/tmp','to':'/private/tmp'}]})
    with pytest.raises(MigrationError):
        _path_aliases({'schema_version':2,'path_aliases':[{'from':'/other','to':'/private/tmp'}]})


def test_membership_captures_external_build_log_for_replay(tmp_path):
    from hmigbot_ios.source_build_membership import collect, validate
    source=tmp_path/'source';source.mkdir();(source/'App.swift').write_text('struct App {}')
    derived=tmp_path/'Derived';filelist=derived/'Build/Intermediates.noindex/App.build/Debug-iphoneos/App.build/Objects-normal/arm64/App.SwiftFileList'
    filelist.parent.mkdir(parents=True);filelist.write_text(str(source/'App.swift')+'\n')
    capture=tmp_path/'capture';capture.mkdir();log=tmp_path/'external.log';log.write_text('** BUILD SUCCEEDED **\n')
    selection={'scheme':'App','configuration':'Debug','sdk':'iphoneos','xcode_version':'fixture','targets':['App']}
    document=collect(source,derived,capture,selection,build_log=log)
    assert document['membership_status']=='complete'
    assert document['evidence']['captured_build_log']['artifact']=='build-logs/compile.log'
    assert (capture/'build-logs/compile.log').read_bytes()==log.read_bytes()
    validate(source,document,capture=capture)


def test_compilation_units_and_preprocessor_dependencies_keep_distinct_views(tmp_path):
    from hmigbot_ios.evidence import pack
    from hmigbot_ios.source_build_membership import collect
    from hmigbot_ios.ios_facts import extract
    source,target=project(tmp_path)
    (source/'App.swift').write_text('struct App { var count: Int { 1 } }')
    (source/'main.c').write_text('#include "dependency.h"\nint main(void) { return VALUE; }\n')
    (source/'dependency.h').write_text('#define VALUE 1\n')
    legacy=tmp_path/'legacy';legacy.mkdir();write_json(legacy/'source-files.json',{'source_files':['dependency.h','main.c']})
    legacy_bundle=tmp_path/'legacy-bundle';pack(source,legacy,legacy_bundle,'source_build','fixture dependency capture')
    derived=tmp_path/'Derived';filelist=derived/'Build/Intermediates.noindex/App.build/Debug-iphoneos/App.build/Objects-normal/arm64/App.SwiftFileList'
    filelist.parent.mkdir(parents=True);filelist.write_text(str(source/'App.swift')+'\n')
    capture=tmp_path/'compile';capture.mkdir();log=capture/'build.log';log.write_text(f'CompileC obj {source}/main.c normal arm64 c com.apple.compilers.llvm.clang.1_0.compiler (in target \'App\' from project \'App\')\n')
    selection={'scheme':'App','configuration':'Debug','sdk':'iphoneos','xcode_version':'fixture','targets':['App'],'architectures':['arm64']}
    doc=collect(source,derived,capture,selection,build_log=log)
    assert doc['source_files']==['App.swift','main.c']
    compiled=tmp_path/'compiled-bundle';pack(source,capture,compiled,'source_build','fixture compiler capture')
    condition=tmp_path/'conditional';condition.mkdir();write_json(condition/'manifest.json',{'build_evidence':str(legacy_bundle)})
    expected={'project':'App.xcodeproj','scheme':'App','target':'App','configuration':'Debug','sdk':'iphoneos','architecture':'arm64'}
    variant={'scope':'selected-build','source_files':['dependency.h','main.c'],'evidence_path':str(legacy_bundle),'conditional_evidence':str(condition),'expected_build':expected,'compilation_evidence_path':str(compiled)}
    conditional={'members':['dependency.h','main.c'],'expected_build':expected,'observed':{},'reference':{'fixture':True}}
    with patch('hmigbot_ios.conditional_evidence.validate',return_value=conditional):
        graph=extract(source,variant)
        assert graph['variant']['compiled_source_files']==['App.swift','main.c']
        assert graph['variant']['preprocessor_dependency_files']==['dependency.h','main.c']
        assert any(f['anchor']['path']=='App.swift' and f['value'].get('storage')=='computed_property' for f in graph['facts'])
        with pytest.raises(MigrationError,match='view changed'):
            extract(source,{**graph['variant'],'compiled_source_files':['main.c']})


def test_cli_uses_one_authoritative_semantic_catalog():
    from hmigbot_ios.cli import dispatch, parser
    result=dispatch(parser().parse_args(['capabilities']))
    assert result['independent_capability_count']==93
    assert len({row['id'] for row in result['canonical_capabilities']})==93
    assert len(result['atoms'])==62  # Non-counting internal checklist, retained.
    assert result['canonical_catalog']=='semantic_capabilities.json'
