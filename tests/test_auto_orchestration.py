"""Routing tests consume real graph artifacts; fake boundaries are not native acceptance."""
import json
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

from hmigbot_ios.core import MigrationError, digest, read_json, snapshot, write_json
from hmigbot_ios.host import detect_host_profile
from hmigbot_ios.native_pipeline import configure
from hmigbot_ios.source_analysis import run, frozen_inputs
from hmigbot_ios.analysis_strategy import plan


def host(native=False):
    return detect_host_profile(host_os='Darwin' if native else 'Windows', machine='test',
        lookup=lambda name: '/tools/' + name if native and name in {'xcodebuild', 'xcrun'} else None,
        environ={})


def project(tmp_path, xcode=False):
    source, target = tmp_path / 'source', tmp_path / 'target'
    source.mkdir(); target.mkdir()
    (source / 'View.swift').write_text('import SwiftUI\nstruct Screen: View { var body: some View { Text("Hello") } }')
    if xcode:
        from test_project_scope import openstep
        folder = source / 'App.xcodeproj'; folder.mkdir()
        objects = {
            'P': {'isa': 'PBXProject', 'targets': ['A'], 'mainGroup': 'G', 'buildConfigurationList': 'C'},
            'G': {'isa': 'PBXGroup', 'children': ['F'], 'sourceTree': '<group>'},
            'F': {'isa': 'PBXFileReference', 'path': 'View.swift', 'sourceTree': '<group>'},
            'B': {'isa': 'PBXBuildFile', 'fileRef': 'F'},
            'S': {'isa': 'PBXSourcesBuildPhase', 'files': ['B']},
            'A': {'isa': 'PBXNativeTarget', 'name': 'App', 'productType': 'com.apple.product-type.application',
                  'buildPhases': ['S'], 'buildConfigurationList': 'C', 'dependencies': []},
            'C': {'isa': 'XCConfigurationList', 'buildConfigurations': ['D']},
            'D': {'isa': 'XCBuildConfiguration', 'name': 'Debug', 'buildSettings': {}},
        }
        (folder / 'project.pbxproj').write_text(openstep({'rootObject': 'P', 'objects': objects}))
    configure(source, target)
    return source, target


def build_evidence(source, target):
    from hmigbot_ios.evidence import pack
    from hmigbot_ios.source_build_membership import collect
    root = target / 'spec/ref/ios-build-evidence/test'
    capture, derived = root / 'capture', root / 'DerivedData'
    capture.mkdir(parents=True)
    filelist = derived / 'Build/Intermediates.noindex/App.build/Debug-iphoneos/App.build/Objects-normal/arm64/App.SwiftFileList'
    filelist.parent.mkdir(parents=True)
    filelist.write_text(str(source / 'View.swift') + '\n')
    log = capture / 'build.log'; log.write_text('** BUILD SUCCEEDED **\n')
    selection = {'scheme': 'App', 'configuration': 'Debug', 'sdk': 'iphoneos',
                 'targets': ['App'], 'architectures': ['arm64'], 'xcode_version': 'test fixture'}
    collect(source, derived, capture, selection, build_log=log)
    write_json(capture / 'build-settings.json', [{'target': 'App', 'buildSettings': {
        'TARGET_NAME': 'App', 'CONFIGURATION': 'Debug', 'SDKROOT': '/sdk',
        'PROJECT_FILE_PATH': str(source / 'App.xcodeproj'),
        'SDK_NAME': 'iphoneos27.1', 'ARCHS': 'arm64', 'SWIFT_VERSION': '5.0'}}])
    output = root / 'evidence'
    pack(source, capture, output, 'source_build', 'test fixture')
    return output


def offline(monkeypatch, native=False):
    monkeypatch.setattr('hmigbot_ios.host.detect_host_profile', lambda: host(native))
    monkeypatch.setattr('hmigbot_ios.apple_capabilities.export_skills',
        lambda *a, **kw: {'status': 'unavailable', 'loaded': [], 'used': False, 'reason': 'test boundary'})
    monkeypatch.setattr('hmigbot_ios.apple_capabilities.discover_mcp',
        lambda *a, **kw: {'status': 'unavailable', 'tool_calls_performed': False, 'reason': 'test boundary'})


def test_plan_only_is_read_only_and_identifies_native_selection(tmp_path, monkeypatch):
    source, target = project(tmp_path, xcode=True)
    offline(monkeypatch, native=True)
    before = snapshot(target)
    result = run(target, plan_only=True)
    assert result['backend'] == 'native'
    assert result['selection']['target'] == 'App'
    assert result['selection']['project'] == 'App.xcodeproj'
    assert snapshot(target) == before


def test_automatic_native_call_feeds_real_membership_and_build_settings_graph(tmp_path, monkeypatch):
    source, target = project(tmp_path, xcode=True)
    offline(monkeypatch, native=True)
    calls = []
    def capture(src, project, selection, output, **kwargs):
        calls.append(selection)
        evidence = build_evidence(src, project)
        return {'status': 'captured', 'variant': {'scope': 'selected-build',
                'source_files': ['View.swift'], 'evidence_path': str(evidence)},
                'compilation': str(evidence), 'clang_config': None}
    monkeypatch.setattr('hmigbot_ios.native_source_capture.selection', lambda s, c, o: {**c, 'scheme': 'App'})
    monkeypatch.setattr('hmigbot_ios.native_source_capture.capture', capture)
    events = []
    result = run(target, progress=events.append)
    graph = read_json(target / 'spec/baseline/ios-facts.json')
    assert len(calls) == 1 and result['build'] == 'source_build_captured'
    assert graph['variant']['source_files'] == ['View.swift']
    assert any(p['operation'] == 'build-settings' for p in graph['provider_artifacts'])
    assert result['progress']['completed'] == result['progress']['total']
    assert [e['current'] for e in events].count('native-source-capture') >= 2
    assert result['status'] == 'needs_review' and not result['behavior_verified']


@pytest.mark.parametrize('native', [False, True])
def test_current_compiler_evidence_is_automatically_replayed_without_build(tmp_path, monkeypatch, native):
    source, target = project(tmp_path, xcode=True)
    bundle = build_evidence(source, target)
    offline(monkeypatch, native=native)
    with patch('hmigbot_ios.native_source_capture.capture') as capture:
        result = run(target)
    capture.assert_not_called()
    assert result['source_provider_selection']['selected_backend'] == 'replay'
    assert result['build'] == 'source_build_evidence_replayed'
    graph = read_json(target / 'spec/baseline/ios-facts.json')
    assert graph['variant']['evidence_path'] == str(bundle)
    assert len(graph['provider_artifacts']) == 1
    assert result['source_provider_selection']['compiler_binding'] == 'unresolved'


def test_missing_conditional_context_selects_native_recapture(tmp_path):
    source, target = project(tmp_path, xcode=True)
    (source / 'Unused.h').write_text('#if FLAG\nint x;\n#endif\n')
    build_evidence(source, target)
    value = plan(source, target, {'mode': 'auto'}, host(True))
    assert value['backend'] == 'native'
    assert any(d['backend'] == 'native_recapture' for d in value['decisions'])
    assert plan(source, target, {'mode': 'replay'}, host(True))['backend'] == 'replay'


def test_same_named_target_in_different_project_does_not_replay_wrong_context(tmp_path):
    source, target = project(tmp_path, xcode=True)
    other = source / 'Other.xcodeproj'; other.mkdir()
    (other / 'project.pbxproj').write_bytes((source / 'App.xcodeproj/project.pbxproj').read_bytes())
    bundle = build_evidence(source, target)
    with pytest.raises(MigrationError, match='selected project'):
        plan(source, target, {'mode': 'auto', 'selection': {'project': 'Other.xcodeproj'},
             'evidence': {'build': str(bundle)}}, host(True))


def test_same_labels_from_different_builds_cannot_join_conditional_and_compiler_views(tmp_path):
    from hmigbot_ios.source_analysis import _replay_variant
    source, target = project(tmp_path, xcode=True)
    bundle = build_evidence(source, target)
    evidence = plan(source, target, {'mode': 'auto'}, host(True))['evidence']
    condition = target / 'spec/ref/condition'; condition.mkdir()
    raw = target / 'spec/ref/other-build/artifacts'; raw.mkdir(parents=True)
    (raw / 'device-build.stdout.log').write_text('different captured build with the same labels')
    write_json(condition / 'manifest.json', {'build_evidence': str(raw.parent)})
    expected = {'project': 'App.xcodeproj', 'scheme': 'App', 'configuration': 'Debug',
                'sdk': 'iphoneos', 'target': 'App', 'architecture': 'arm64'}
    with patch('hmigbot_ios.conditional_evidence.validate', return_value={'expected_build': expected, 'members': ['View.swift']}):
        with pytest.raises(MigrationError, match='same captured build'):
            _replay_variant(target, source, {'evidence': evidence}, {'evidence': {'conditional': str(condition)}})


def test_explicit_static_scope_never_invokes_official_processes(tmp_path, monkeypatch):
    source, target = project(tmp_path, xcode=True)
    monkeypatch.setattr('hmigbot_ios.host.detect_host_profile', lambda: host(True))
    write_json(target / 'spec/ref/ios-analysis-config.json', {'schema_version': 1, 'mode': 'static'})
    with patch('hmigbot_ios.apple_capabilities.command') as command, patch('hmigbot_ios.source_mcp.discover') as mcp:
        result = run(target)
    command.assert_not_called(); mcp.assert_not_called()
    assert result['source_provider_selection']['selected_backend'] == 'static'
    assert result['official_capabilities']['primary_guidance'] == 'declared_third_party_or_static_fallback'


def test_missing_requested_replay_blocks_without_baseline_mutation(tmp_path, monkeypatch):
    source, target = project(tmp_path)
    offline(monkeypatch)
    write_json(target / 'spec/ref/ios-analysis-config.json', {'schema_version': 1, 'mode': 'replay'})
    result = run(target)
    assert result['status'] == 'needs_input'
    assert result['progress']['blocked'] == result['progress']['total']
    assert not (target / 'spec/baseline/ios-facts.json').exists()


def test_stale_explicit_evidence_is_rejected_and_never_replaced(tmp_path, monkeypatch):
    source, target = project(tmp_path)
    bundle = build_evidence(source, target)
    (source / 'View.swift').write_text('struct Different {}')
    offline(monkeypatch, native=True)
    write_json(target / 'spec/ref/ios-analysis-config.json', {'schema_version': 1, 'evidence': {'build': str(bundle)}})
    with patch('hmigbot_ios.native_source_capture.capture') as capture:
        with pytest.raises(MigrationError, match='Requested replay evidence rejected'):
            run(target)
    capture.assert_not_called()
    assert not (target / 'spec/baseline/ios-facts.json').exists()


def test_failure_progress_retains_cause_and_remaining_dependencies(tmp_path, monkeypatch):
    source, target = project(tmp_path, xcode=True)
    offline(monkeypatch, native=True)
    monkeypatch.setattr('hmigbot_ios.native_source_capture.selection', lambda *a: (_ for _ in ()).throw(MigrationError('scheme ambiguous')))
    with pytest.raises(MigrationError, match='scheme ambiguous'):
        run(target)
    report = read_json(target / 'spec/reports/derived/source-analysis.json')
    assert report['progress']['failed'] == 1
    assert report['progress']['completed'] + report['progress']['failed'] + report['progress']['blocked'] == report['progress']['total']
    assert report['stages'][-1]['name'] == 'native-selection'
    assert not (target / 'spec/baseline/ios-facts.json').exists()


def test_execution_evidence_is_frozen_and_tampering_blocks_consumers(tmp_path, monkeypatch):
    source, target = project(tmp_path)
    offline(monkeypatch)
    run(target)
    files = frozen_inputs(target)
    plan_file = next(p for p in files if p.endswith('/plan.json'))
    (target / plan_file).write_text('{}')
    with pytest.raises(MigrationError, match='Source analysis input changed'):
        frozen_inputs(target)


def test_official_resources_replace_only_applicable_review_and_are_pinned(tmp_path):
    from hmigbot_ios.ios_facts import extract
    from hmigbot_ios.apple_capabilities import publish_guidance
    from hmigbot_ios.expertise import make_plan
    source, target = project(tmp_path)
    graph = extract(source)
    resource = target / 'spec/ref/apple/SKILL.md'; resource.parent.mkdir(parents=True)
    resource.write_text('test-only exported guidance boundary')
    skills = {'status': 'loaded', 'loaded': [{'topic': 'swiftui', 'resources': [{
        'path': resource.relative_to(target).as_posix(), 'sha256': digest(resource.read_bytes())}]}]}
    publish_guidance(target, graph, skills, {'status': 'unavailable'})
    review = make_plan(source, graph, project=target)['reviews'][0]
    assert review['resource_origin'] == 'Apple'
    assert review['resources'][0]['path'] == str(resource)
    resource.write_text('changed')
    with pytest.raises(MigrationError, match='resource changed'):
        make_plan(source, graph, project=target)


def test_app_intents_official_resource_enters_required_downstream_review(tmp_path):
    from hmigbot_ios.ios_facts import extract
    from hmigbot_ios.apple_capabilities import publish_guidance
    from hmigbot_ios.expertise import make_plan
    source, target = project(tmp_path)
    (source / 'Intent.swift').write_text('import AppIntents\nstruct OpenIntent: AppIntent { func perform() async {} }')
    graph = extract(source)
    resource = target / 'spec/ref/apple/intent.md'; resource.parent.mkdir(parents=True)
    resource.write_text('test-only App Intents guidance')
    publish_guidance(target, graph, {'status': 'loaded', 'loaded': [{'topic': 'app_intents', 'resources': [{
        'path': resource.relative_to(target).as_posix(), 'sha256': digest(resource.read_bytes())}]}]}, {'status': 'unavailable'})
    reviews = make_plan(source, graph, project=target)['reviews']
    intent = next(r for r in reviews if r['pack'] == 'app_intents')
    assert intent['source_paths'] == ['Intent.swift'] and intent['resource_origin'] == 'Apple'
    assert intent['resources'][0]['path'] == str(resource)


def test_mcp_discovery_is_real_protocol_and_preserves_null_id_error(tmp_path):
    from hmigbot_ios.source_mcp import discover
    server = tmp_path / 'server.py'
    server.write_text('import json,sys\nfor line in sys.stdin:\n m=json.loads(line)\n if "id" in m:\n  print(json.dumps({"jsonrpc":"2.0","id":None,"error":{"code":-32603,"message":"access is disabled"}}),flush=True)\n')
    value = discover({'command': [sys.executable, str(server)]}, tmp_path, tmp_path / 'logs')
    assert value['status'] == 'unavailable' and 'access is disabled' in value['error']
    assert not value['tool_calls_performed']
    assert read_json(tmp_path / 'logs/transcript.json')[-1]['message']['id'] is None


def test_official_command_timeout_keeps_partial_output(tmp_path):
    from hmigbot_ios.apple_capabilities import command
    with pytest.raises(MigrationError, match='raw diagnostics'):
        command(tmp_path / 'logs', 'bounded', [sys.executable, '-c',
            'import time; print("partial", flush=True); time.sleep(3)'], cwd=tmp_path, timeout=.05)
    assert (tmp_path / 'logs/bounded.stdout.log').read_bytes() == b'partial\n'
    assert read_json(tmp_path / 'logs/bounded.command.json')['error'] == 'timeout'


def test_auto_mcp_query_consumes_real_protocol_and_does_not_relabel_custom_server(tmp_path, monkeypatch):
    source, target = project(tmp_path)
    monkeypatch.setattr('hmigbot_ios.host.detect_host_profile', lambda: host(False))
    monkeypatch.setattr('hmigbot_ios.apple_capabilities.export_skills', lambda *a, **kw:
        {'status': 'unavailable', 'loaded': [], 'used': False})
    server = tmp_path / 'server.py'
    server.write_text('''import json,sys
for line in sys.stdin:
 m=json.loads(line)
 if 'id' not in m: continue
 if m['method']=='initialize':
  r={'protocolVersion':'2025-11-25','capabilities':{'tools':{}},'serverInfo':{'name':'test-only','version':'1'}}
 elif m['method']=='tools/list':
  r={'tools':[{'name':'DocumentationSearch','inputSchema':{'required':['query']},'annotations':{'readOnlyHint':True}}]}
 else: r={'content':[{'type':'text','text':'test-only documentation response'}]}
 print(json.dumps({'jsonrpc':'2.0','id':m['id'],'result':r}),flush=True)
''')
    config = target / 'spec/ref/test-server.json'
    write_json(config, {'provider': 'xcode', 'transport': 'stdio', 'command': [sys.executable, str(server)]})
    write_json(target / 'spec/ref/ios-analysis-config.json', {'schema_version': 1, 'mcp_server': str(config)})
    run(target)
    guidance = read_json(target / 'spec/ref/ios-official-analysis.json')
    mcp = guidance['xcode_mcp']
    assert mcp['status'] == 'captured' and mcp['publisher'] == 'user_configured'
    assert guidance['official_resources'] == {}
    artifact = read_json(Path(mcp['captures'][0]['path']) / 'artifact.json')
    assert artifact['fact_ids'] and artifact['source_sha256'] == snapshot(source)['sha256']
    assert artifact['resolution'] == 'tool_response' and not artifact['behavior_verified']


def test_official_review_can_be_recorded_without_losing_project_resource_context(tmp_path):
    from test_ios_harness import fixture
    from hmigbot_ios.apple_capabilities import publish_guidance
    from hmigbot_ios.expertise import prepare, record, validate_reviews
    from hmigbot_ios.core import json_bytes
    source, target, graph = fixture(tmp_path)
    resource = target / 'spec/ref/apple/SKILL.md'; resource.parent.mkdir(parents=True)
    resource.write_text('test-only guidance resource')
    publish_guidance(target, graph, {'status': 'loaded', 'loaded': [{'topic': 'swiftui',
        'resources': [{'path': resource.relative_to(target).as_posix(), 'sha256': digest(resource.read_bytes())}]}]},
        {'status': 'unavailable'})
    expected = prepare(target)
    from hmigbot_ios.expertise import PLAN
    current = read_json(target / PLAN)
    entry = current['reviews'][0]
    receipt = {'schema_version': 1, 'plan_sha256': digest(json_bytes(current)), 'reviews': [{
        'id': entry['id'], 'status': 'reviewed', 'reviewer': 'test-only-reviewer',
        'resources': entry['resources'], 'observations': [{'source': {'path': p, 'line': 1},
            'interpretation': 'test observation for receipt contract', 'unknowns': []} for p in entry['source_paths']]}]}
    path = tmp_path / 'review.json'; write_json(path, receipt)
    assert record(target, path)['status'] == 'recorded'
    assert validate_reviews(source, target, graph)['status'] == 'reviewed'
