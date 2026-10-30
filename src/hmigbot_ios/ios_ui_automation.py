"""Scoped Apple XCUITest capture/replay. No Mac desktop or device auto-selection."""
from __future__ import annotations

import argparse
from argparse import Namespace
import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid

from .core import MigrationError, digest, json_bytes, read_json, write_json
from .ui_validation_evidence import build_identity, source_identity, validate_bundle
from .cli_output import emit_json

ROOT = Path(__file__).resolve().parents[2]
PROVIDER = ROOT / 'providers/ui-testing/ios/HMigBotScenarioTests.swift'
HASH = re.compile(r'[0-9a-f]{64}')
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}')
ACTIONS = {'wait', 'tap', 'type_text', 'assert', 'swipe_up', 'swipe_down', 'checkpoint'}


def _require(value, message):
    if not value:
        raise MigrationError(message)


def validate_request(request):
    _require(isinstance(request, dict) and request.get('schema_version') == 'hmigbot-ios-ui-request/1', 'Unsupported iOS UI request')
    for key in ('bundle_id', 'device_id', 'source_root', 'app_path'):
        _require(isinstance(request.get(key), str) and request[key], 'Missing explicit ' + key)
    _require(re.fullmatch(r'[0-9A-Fa-f-]{36}', request['device_id']), 'Use an exact simulator UDID, never booted/automatic')
    app = Path(request['app_path']).resolve()
    _require(app.is_dir() and app.suffix == '.app' and not Path(request['app_path']).is_symlink(), 'Use an actual simulator .app build')
    info = plistlib.loads((app / 'Info.plist').read_bytes())
    _require(info.get('CFBundleIdentifier') == request['bundle_id'], 'App build bundle ID differs from request')
    _require('iPhoneSimulator' in info.get('CFBundleSupportedPlatforms', []), 'Only iOS Simulator app builds are accepted')
    for key in ('language', 'locale', 'theme', 'content_size'):
        _require(isinstance(request.get('configuration', {}).get(key), str) and request['configuration'][key], 'Explicit configuration missing: ' + key)
    _require(request['configuration']['theme'] in ('light', 'dark'), 'Theme must be light or dark')
    _require(type(request.get('test_timeout_seconds', 120)) is int and 10 <= request.get('test_timeout_seconds', 120) <= 240,
             'test_timeout_seconds must be 10–240')
    scenario = request.get('scenario')
    _require(isinstance(scenario, dict) and ID.fullmatch(scenario.get('id', '')), 'Stable scenario ID required')
    _require(isinstance(scenario.get('steps'), list) and 0 < len(scenario['steps']) <= 100, 'Scenario needs 1–100 deterministic steps')
    checkpoint_ids = []
    for step in scenario['steps']:
        _require(isinstance(step, dict) and step.get('action') in ACTIONS, 'Unsupported action; no arbitrary shell/predicate is allowed')
        timeout = step.get('timeout', 10)
        _require(type(timeout) in (int, float) and 0 < timeout <= 60, 'Each wait must be bounded to 60 seconds')
        _require(type(step.get('retries', 0)) is int and 0 <= step.get('retries', 0) <= 2, 'Readiness retries must be 0–2; actions are never blindly repeated')
        if step['action'] != 'checkpoint' or step.get('scope', 'application') != 'application':
            _require(isinstance(step.get('identifier'), str) and step['identifier'], 'Stable accessibility identifier required')
        if step['action'] == 'type_text':
            _require(isinstance(step.get('text'), str) and len(step['text']) <= 4096, 'Text input is missing or too large')
        if step['action'] == 'checkpoint':
            _require(ID.fullmatch(step.get('id', '')) and step.get('scope', 'application') in ('application', 'element', 'window'), 'Invalid checkpoint/screenshot scope')
            checkpoint_ids.append(step['id'])
    _require(checkpoint_ids and len(checkpoint_ids) == len(set(checkpoint_ids)), 'Unique explicit checkpoints required')
    _require(isinstance(request.get('launch_arguments', []), list) and all(isinstance(v, str) for v in request.get('launch_arguments', [])), 'launch_arguments must be strings')
    _require(isinstance(request.get('launch_environment', {}), dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in request.get('launch_environment', {}).items()), 'launch_environment must contain string keys and values')
    return app, checkpoint_ids


def scenario_identity(request):
    scenario = request['scenario']
    recipe = scenario.get('business_recipe')
    _require(isinstance(recipe, (dict, list)) and recipe, 'Shared business_recipe required for source/target scenario binding')
    return {'id': scenario['id'], 'sha256': digest(json_bytes(recipe))}


def _project(path):
    """A separate generated UI-test target, with no production source edits."""
    project = path / 'Harness.xcodeproj'
    project.mkdir()
    pbx = '''// !$*UTF8*$!
{archiveVersion=1;objectVersion=56;classes={};objects={
P={isa=PBXProject;attributes={LastUpgradeCheck=2710;};buildConfigurationList=PC;compatibilityVersion="Xcode 14.0";developmentRegion=en;mainGroup=G;productRefGroup=PR;projectDirPath="";targets=(T);};
G={isa=PBXGroup;children=(S,PR);sourceTree="<group>";};
PR={isa=PBXGroup;children=(PRODUCT);name=Products;sourceTree="<group>";};
S={isa=PBXFileReference;lastKnownFileType=sourcecode.swift;path=HMigBotScenarioTests.swift;sourceTree="<group>";};
B={isa=PBXBuildFile;fileRef=S;};
PRODUCT={isa=PBXFileReference;explicitFileType=wrapper.cfbundle;path=Harness.xctest;sourceTree=BUILT_PRODUCTS_DIR;};
SOURCES={isa=PBXSourcesBuildPhase;buildActionMask=2147483647;files=(B);runOnlyForDeploymentPostprocessing=0;};
FRAMEWORKS={isa=PBXFrameworksBuildPhase;buildActionMask=2147483647;files=();runOnlyForDeploymentPostprocessing=0;};
T={isa=PBXNativeTarget;buildConfigurationList=TC;buildPhases=(SOURCES,FRAMEWORKS);buildRules=();dependencies=();name=Harness;productName=Harness;productReference=PRODUCT;productType="com.apple.product-type.bundle.ui-testing";};
PC={isa=XCConfigurationList;buildConfigurations=(PD);defaultConfigurationIsVisible=0;defaultConfigurationName=Debug;};
TC={isa=XCConfigurationList;buildConfigurations=(TD);defaultConfigurationIsVisible=0;defaultConfigurationName=Debug;};
PD={isa=XCBuildConfiguration;name=Debug;buildSettings={SDKROOT=iphonesimulator;IPHONEOS_DEPLOYMENT_TARGET=16.0;};};
TD={isa=XCBuildConfiguration;name=Debug;buildSettings={PRODUCT_NAME=Harness;PRODUCT_BUNDLE_IDENTIFIER=org.hmigbot.scoped-ui-tests;GENERATE_INFOPLIST_FILE=YES;SWIFT_VERSION=5.0;CODE_SIGNING_ALLOWED=NO;SDKROOT=iphonesimulator;IPHONEOS_DEPLOYMENT_TARGET=16.0;TARGETED_DEVICE_FAMILY="1,2";};};
};rootObject=P;}
'''
    (project / 'project.pbxproj').write_text(pbx)
    schemes = project / 'xcshareddata/xcschemes'
    schemes.mkdir(parents=True)
    (schemes / 'Harness.xcscheme').write_text('''<?xml version="1.0" encoding="UTF-8"?><Scheme LastUpgradeVersion="2710" version="1.3"><BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES"><BuildActionEntries><BuildActionEntry buildForTesting="YES" buildForRunning="NO" buildForProfiling="NO" buildForArchiving="NO" buildForAnalyzing="YES"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="T" BuildableName="Harness.xctest" BlueprintName="Harness" ReferencedContainer="container:Harness.xcodeproj"/></BuildActionEntry></BuildActionEntries></BuildAction><TestAction buildConfiguration="Debug" shouldUseLaunchSchemeArgsEnv="NO"><Testables><TestableReference skipped="NO"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="T" BuildableName="Harness.xctest" BlueprintName="Harness" ReferencedContainer="container:Harness.xcodeproj"/></TestableReference></Testables></TestAction></Scheme>''')
    shutil.copy2(PROVIDER, path / PROVIDER.name)


def prepare(request, output):
    app, checkpoints = validate_request(request)
    output = Path(output).resolve()
    source = Path(request['source_root']).resolve()
    request = {**request, 'app_path': str(app), 'source_root': str(source)}
    _require(not output.exists(), 'Choose a fresh evidence directory; old evidence is never overwritten')
    _require(not output.is_relative_to(source) and not output.is_relative_to(app), 'UI outputs cannot modify source/app build')
    _require(not output.is_relative_to(ROOT), 'UI execution artifacts must stay outside the tool release')
    bound = {'schema_version': 'hmigbot-ui-evidence/1', 'platform': 'ios', 'run_id': 'UI-' + uuid.uuid4().hex,
        'bundle_id': request['bundle_id'], 'device': {'id': request['device_id'], 'kind': 'simulator'},
        'build': {'sha256': build_identity(app)}, 'source_sha256': source_identity('ios', source),
        'scenario': scenario_identity(request), 'configuration': request['configuration'],
        'platform_script_sha256': digest(json_bytes(request['scenario']['steps']))}
    output.mkdir(parents=True)
    harness = output / 'harness'
    harness.mkdir()
    _project(harness)
    write_json(output / 'request.json', request)
    write_json(output / 'prepared.json', {'identity': bound, 'expected_checkpoints': checkpoints,
        'request_sha256': digest(json_bytes(request)),
        'harness_inputs': {p.relative_to(output).as_posix(): digest(p.read_bytes()) for p in harness.rglob('*') if p.is_file()},
        'provider_sha256': digest(PROVIDER.read_bytes()), 'status': 'prepared', 'actually_executed': False})
    return {'status': 'prepared', 'directory': str(output), 'run_id': bound['run_id'], 'actually_executed': False}


def _call(output, label, argv, timeout=300):
    started = time.monotonic()
    timed_out = False
    logs = output / 'calls'
    logs.mkdir(exist_ok=True)
    receipt = {'actual_call_now': True, 'argv': argv, 'exit_code': None,
               'status': 'running', 'timed_out': False,
               'kind': 'app_ui_test' if label == 'test' else 'configuration_observation'}
    write_json(logs / (label + '.json'), receipt)
    emit_json({'stage': 'ui-ios/' + label, 'status': 'running'}, stream=sys.stderr, indent=None)
    with (logs / (label + '.stdout')).open('wb') as stdout, (logs / (label + '.stderr')).open('wb') as stderr:
        process = subprocess.Popen(argv, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            # This group contains only this adapter's own spawned CLI process
            # and its descendants. CoreSimulator-owned processes are not claimed
            # to belong to the group and are not controlled by this cleanup.
            try: os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError: pass
            try: process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try: os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                process.wait(timeout=3)
    code = process.returncode
    stdout = (logs / (label + '.stdout')).read_bytes()
    receipt = {'actual_call_now': True, 'argv': argv, 'exit_code': code, 'timed_out': timed_out,
        'status': 'timed_out' if timed_out else 'returned',
        'elapsed_seconds': time.monotonic() - started, 'kind': 'app_ui_test' if label == 'test' else 'configuration_observation'}
    write_json(logs / (label + '.json'), receipt)
    emit_json({'stage': 'ui-ios/' + label, 'status': receipt['status'], 'exit_code': code}, stream=sys.stderr, indent=None)
    _require(not timed_out and code == 0, 'Apple CLI ' + label + (' timed out' if timed_out else ' failed: exit ' + str(code)) + '; retained calls/' + label + '.stderr')
    return stdout, receipt


def run(directory):
    output = Path(directory).resolve()
    request = read_json(output / 'request.json')
    app, expected = validate_request(request)
    prepared = read_json(output / 'prepared.json')
    bound = prepared['identity']
    _require(digest(json_bytes(request)) == prepared.get('request_sha256'), 'Scoped request changed after prepare; prepare a fresh attempt')
    _require(digest(PROVIDER.read_bytes()) == prepared.get('provider_sha256'), 'XCTest provider changed after prepare')
    for name, sha in prepared.get('harness_inputs', {}).items():
        item = output / name
        _require(not item.is_symlink() and item.is_file() and digest(item.read_bytes()) == sha,
                 'Generated XCTest input changed after prepare: ' + name)
    _require(not (output / 'manifest.json').exists(), 'Evidence already finalized; use prepare for a new attempt')
    _require(build_identity(app) == bound['build']['sha256'] and source_identity('ios', request['source_root']) == bound['source_sha256'], 'Source/app build changed after prepare')
    _require(scenario_identity(request) == bound['scenario'] and digest(json_bytes(request['scenario']['steps'])) == bound['platform_script_sha256'], 'Scenario changed after prepare')
    calls = []
    devices, call = _call(output, 'devices', ['xcrun', 'simctl', 'list', 'devices', 'available', '-j'], 30); calls.append(call)
    selected = [d for group in json.loads(devices)['devices'].values() for d in group if d['udid'] == request['device_id']]
    _require(len(selected) == 1 and selected[0].get('isAvailable'), 'Exact selected simulator is unavailable')
    if selected[0]['state'] != 'Booted':
        _require(selected[0]['state'] == 'Shutdown', 'Selected simulator is not ready; inspect this exact simulator state')
        _, call = _call(output, 'boot', ['xcrun', 'simctl', 'boot', request['device_id']], 30); calls.append(call)
        _, call = _call(output, 'boot-ready', ['xcrun', 'simctl', 'bootstatus', request['device_id'], '-b'], 180); calls.append(call)
    _, call = _call(output, 'install', ['xcrun', 'simctl', 'install', request['device_id'], str(app)], 60); calls.append(call)
    for key, value in [('appearance', request['configuration']['theme']), ('content_size', request['configuration']['content_size'])]:
        _, call = _call(output, 'set-' + key, ['xcrun', 'simctl', 'ui', request['device_id'], key, value], 20); calls.append(call)
    from .ui_configuration import collect_simulator_context
    # Supplementary native device settings; an app may override these. Unknown
    # fields do not fail a screenshot or become fabricated app observations.
    collect_simulator_context(request['device_id'],request['bundle_id'],output/'device-configuration')
    _, call = _call(output, 'build', ['xcodebuild', 'build-for-testing', '-project', str(output / 'harness/Harness.xcodeproj'), '-scheme', 'Harness', '-destination', 'platform=iOS Simulator,id=' + request['device_id'], '-derivedDataPath', str(output / 'DerivedData'), 'CODE_SIGNING_ALLOWED=NO'], 300); calls.append(call)
    xctestruns = list((output / 'DerivedData/Build/Products').glob('*.xctestrun'))
    _require(len(xctestruns) == 1, 'Expected one generated .xctestrun')
    testconfig = plistlib.loads(xctestruns[0].read_bytes())
    payload = {**request, 'run_id': bound['run_id']}
    encoded = base64.b64encode(json_bytes(payload)).decode()
    test_timeout = request.get('test_timeout_seconds', 120)
    def configure(value):
        if isinstance(value, dict):
            if 'TestBundlePath' in value:
                value.setdefault('EnvironmentVariables', {})['HMIGBOT_SCENARIO_BASE64'] = encoded
                value['PreferredScreenCaptureFormat'] = 'screenshot'
                value['TestTimeoutsEnabled'] = True
                value['MaximumTestExecutionTimeAllowance'] = test_timeout
                value['DefaultTestExecutionTimeAllowance'] = test_timeout
            for key, child in list(value.items()):
                if isinstance(child, str):
                    value[key] = child.replace('__TESTROOT__', str(xctestruns[0].parent))
                else: configure(child)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                if isinstance(child, str): value[index] = child.replace('__TESTROOT__', str(xctestruns[0].parent))
                else: configure(child)
    configure(testconfig)
    scoped = output / 'scoped.xctestrun'
    scoped.write_bytes(plistlib.dumps(testconfig))
    # A failed product assertion still exports its actual captured evidence.
    test_error = None
    try:
        _, call = _call(output, 'test', ['xcodebuild', 'test-without-building', '-xctestrun', str(scoped), '-destination', 'platform=iOS Simulator,id=' + request['device_id'], '-resultBundlePath', str(output / 'result.xcresult'), '-parallel-testing-enabled', 'NO', '-maximum-test-execution-time-allowance', str(test_timeout), '-collect-test-diagnostics', 'never'], test_timeout + 90); calls.append(call)
    except MigrationError as exc:
        test_error = str(exc)
        calls.append(read_json(output / 'calls/test.json'))
    _require((output / 'result.xcresult').is_dir(), test_error or 'No Xcode test result bundle produced')
    if not (output / 'result.xcresult/Info.plist').is_file():
        error = MigrationError((test_error or 'Xcode test result is incomplete') + '; xcresult is incomplete; attachment export not attempted; retained calls/test.stdout and calls/test.stderr')
        error.receipt = {'failure_kind': 'test_timeout' if calls[-1].get('timed_out') else 'test_infrastructure',
                         'test': calls[-1], 'attachments': 'not_attempted_incomplete_result'}
        raise error
    try:
        _, call = _call(output, 'attachments', ['xcrun', 'xcresulttool', 'export', 'attachments', '--path', str(output / 'result.xcresult'), '--output-path', str(output / 'attachments')], 60); calls.append(call)
    except MigrationError as exc:
        if test_error:
            raise MigrationError(test_error + '; secondary attachment export failure: ' + str(exc)) from exc
        raise
    return finalize_existing(output, _ui_executed_now=True)


def finalize_existing(directory, *, _ui_executed_now=False):
    """Recover postprocessing of an actual complete test; never rerun app UI."""
    output = Path(directory).resolve()
    request = read_json(output / 'request.json')
    app, expected = validate_request(request)
    prepared = read_json(output / 'prepared.json')
    bound = prepared['identity']
    _require(digest(json_bytes(request)) == prepared.get('request_sha256'), 'Scoped request changed after the actual test')
    _require(build_identity(app) == bound['build']['sha256'] and source_identity('ios', request['source_root']) == bound['source_sha256'], 'Source/app changed since the captured test; retained evidence is stale')
    if (output / 'manifest.json').is_file():
        existing = read_json(output / 'manifest.json')
        _require(all(existing.get(key) == value for key, value in bound.items()), 'Finalized evidence differs from the prepared identity')
        validate_bundle(output / 'manifest.json')
        return {'status': existing['status'], 'failure_kind': existing.get('failure_kind'),
                'manifest': str(output / 'manifest.json'),
                'captured_checkpoints': sum(c['status'] == 'passed' for c in existing['checkpoints']),
                'actual_execution': True, 'actual_call_now': False, 'ui_test_executed_now': False,
                'resumed_from_existing_test': True, 'postprocessing_reused': True,
                'configuration_observation': existing['configuration_observation'], 'behavior_verified': False}
    _require((output / 'result.xcresult/Info.plist').is_file(), 'Actual xcresult is incomplete; retain the original test error')
    calls = [read_json(output / ('calls/' + label + '.json')) for label in
             ('devices', 'boot', 'boot-ready', 'install', 'set-appearance', 'set-content_size', 'build', 'test', 'attachments')
             if (output / ('calls/' + label + '.json')).is_file()]
    test_call = read_json(output / 'calls/test.json')
    _require(test_call.get('actual_call_now') is True and not test_call.get('timed_out'), 'No completed actual test call to finalize')
    argv = test_call.get('argv', [])
    _require('-resultBundlePath' in argv and argv[argv.index('-resultBundlePath') + 1] == str(output / 'result.xcresult'), 'Test receipt points to a different result bundle')
    _require('-destination' in argv and argv[argv.index('-destination') + 1] == 'platform=iOS Simulator,id=' + request['device_id'], 'Test receipt points to a different simulator')
    raw_summary, summary_call = _call(output, 'summary', ['xcrun', 'xcresulttool', 'get', 'test-results', 'summary', '--path', str(output / 'result.xcresult'), '--compact'], 30)
    summary = json.loads(raw_summary)
    _require(summary.get('totalTestCount') == 1, 'Expected the single scoped UI test result')
    devices = [d.get('device', {}).get('deviceId') for d in summary.get('devicesAndConfigurations', [])]
    _require(devices == [request['device_id']], 'Actual Xcode result reports a different device/configuration')
    test_error = None if test_call.get('exit_code') == 0 else 'Actual Xcode test returned exit ' + str(test_call.get('exit_code'))
    attachments = read_json(output / 'attachments/manifest.json')
    names = {}
    for test in attachments:
        for record in test['attachments']:
            _require(record.get('deviceId') == request['device_id'], 'Xcode attachment device differs from selected simulator')
            name = record['suggestedHumanReadableName']
            # xcresulttool 27 exports the original attachment stem followed by
            # repetition index and attachment UUID, before the actual suffix.
            # Normalize only that exact documented-by-output shape; preserve
            # the raw Apple manifest and reject duplicate logical attachments.
            match = re.fullmatch(r'(.+)_([0-9]+)_([0-9A-Fa-f-]{36})(\.[A-Za-z0-9]+)', name)
            if match:
                name = match[1] + match[4]
            _require(name not in names, 'Ambiguous duplicated test attachment: ' + name)
            path = Path(record['exportedFileName'])
            _require(path.name == str(path), 'Unsafe exported attachment path')
            names[name] = output / 'attachments' / path
    prefix = 'hmigbot.' + bound['run_id'] + '.'
    report_path = names.get(prefix + 'run.json')
    _require(report_path is not None, test_error or 'Scoped run receipt missing from Xcode attachments')
    report = read_json(report_path)
    _require(report.get('run_id') == bound['run_id'] and report.get('bundle_id') == bound['bundle_id'], 'Foreign or stale Xcode run receipt')
    reported = report.get('checkpoints', [])
    _require(isinstance(reported, list) and len({c['id'] for c in reported}) == len(reported), 'Duplicate or malformed captured checkpoint records')
    _require(all(c['id'] in expected for c in reported), 'XCTest reported a checkpoint outside the declared scenario')
    if report.get('status') == 'passed':
        _require(test_call.get('exit_code') == 0 and summary.get('result') == 'Passed' and summary.get('failedTests') == 0,
                 'Attachment status conflicts with actual Xcode test result')
        _require({c['id'] for c in reported} == set(expected), 'Successful test is missing a declared checkpoint capture')
    checkpoints = []
    captured = {c['id']: c for c in reported}
    def ref(path):
        return {'path': path.relative_to(output).as_posix(), 'sha256': digest(path.read_bytes())}
    for checkpoint in expected:
        value = {'id': checkpoint, 'status': captured.get(checkpoint, {}).get('status', 'not_run')}
        if checkpoint in captured:
            value['captured_at'] = captured[checkpoint]['captured_at']
            for field, suffix in [('screenshot', '.png'), ('hierarchy', '.hierarchy.json')]:
                path = names.get(prefix + checkpoint + suffix)
                _require(path is not None, 'Captured checkpoint missing ' + field + ': ' + checkpoint)
                value[field] = ref(path)
        checkpoints.append(value)
    observed = report.get('observed_configuration', {})
    actual = (isinstance(observed,dict) and all(isinstance(observed.get(k),str)
              and observed[k].casefold() not in {'','unknown','unsupported'}
              for k in ('language','locale','theme','content_size')))
    current = {'schema_version': 'hmigbot-ui-current/1', 'platform': 'ios', 'bundle_id': bound['bundle_id'],
        'device': bound['device'], 'build_sha256': bound['build']['sha256'], 'observed_configuration': observed,
        'observations_actual': actual, 'calls': calls,
        'scope': 'Configuration read from explicitly selected app accessibility probe, not copied from request',
        'missing': [] if actual else ['App configuration probe missing or does not confirm the selected configuration']}
    device_context = output / 'device-configuration/context.json'
    if device_context.is_file():
        current['device_context'] = read_json(device_context)
    write_json(output / 'configuration-observation.json', current)
    artifacts = {p.relative_to(output).as_posix(): digest(p.read_bytes()) for p in (output / 'attachments').iterdir() if p.is_file()}
    artifacts['configuration-observation.json'] = digest((output / 'configuration-observation.json').read_bytes())
    if device_context.is_file():
        artifacts.update({p.relative_to(output).as_posix():digest(p.read_bytes())
                          for p in device_context.parent.iterdir() if p.is_file()})
    manifest = {**bound, 'status': report['status'], 'failure_kind': report.get('failure_kind'),
        'error': report.get('error', test_error), 'captured_at': report['captured_at'], 'checkpoints': checkpoints,
        'artifacts': artifacts, 'calls': calls, 'configuration_observation': 'confirmed' if actual else 'unknown',
        'postprocessing': {'ui_test_executed_now': _ui_executed_now, 'actual_call_now': _ui_executed_now,
                           'resumed_from_existing_test': not _ui_executed_now,
                           'original_test_receipt': 'calls/test.json', 'summary_read': summary_call},
        'behavior_verified': False, 'verification': {'build_path': str(app), 'source_root': str(Path(request['source_root']).resolve()),
            'configuration_receipt': {'path': str(output / 'configuration-observation.json'), 'sha256': artifacts['configuration-observation.json']}}}
    write_json(output / 'manifest.json', manifest)
    _require(build_identity(app) == bound['build']['sha256'] and source_identity('ios', request['source_root']) == bound['source_sha256'], 'Source/app changed during test execution; evidence is stale')
    return {'status': manifest['status'], 'failure_kind': manifest['failure_kind'], 'manifest': str(output / 'manifest.json'),
        'captured_checkpoints': len(captured), 'actual_execution': True,
        'actual_call_now': _ui_executed_now, 'ui_test_executed_now': _ui_executed_now,
        'resumed_from_existing_test': not _ui_executed_now,
        'configuration_observation': manifest['configuration_observation'], 'behavior_verified': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare_cmd = commands.add_parser('prepare', help='Generate an isolated XCTest harness without executing UI')
    prepare_cmd.add_argument('--request', type=Path, required=True)
    prepare_cmd.add_argument('--output', type=Path, required=True)
    run_cmd = commands.add_parser('run', help='Execute against the exact selected simulator and app')
    run_cmd.add_argument('--prepared', type=Path, required=True)
    run_cmd.add_argument('--project', type=Path)
    collect = commands.add_parser('collect', help='Finalize an existing actual XCTest result without running UI again')
    collect.add_argument('--prepared', type=Path, required=True)
    collect.add_argument('--project', type=Path)
    check = commands.add_parser('validate', help='Verify captured artifacts without operating a device')
    check.add_argument('--manifest', type=Path, required=True)
    check.add_argument('--current', type=Path)
    args = parser.parse_args(argv)
    progress = None
    if args.command in {'run', 'collect'} and args.project:
        from .project_progress import ProjectProgress
        progress = ProjectProgress(Namespace(command='ui-ios-run', project=args.project))
        progress.record('running')
    try:
        if args.command == 'prepare': result = prepare(read_json(args.request), args.output)
        elif args.command == 'run': result = run(args.prepared)
        elif args.command == 'collect': result = finalize_existing(args.prepared)
        else: result = validate_bundle(args.manifest, read_json(args.current) if args.current else None)
        code = 2 if result.get('status') in ('failed', 'stale_evidence', 'needs_current_binding') else 0
    except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
        result, code = {'status': 'failed', 'error': str(exc), 'actual_execution': 'consult retained call receipts',
                        'recovery': 'Inspect retained calls; prepare a fresh exact simulator/app scenario or import existing scoped evidence. Static conversion remains available.'}, 2
        if isinstance(getattr(exc, 'receipt', None), dict): result['failure_receipt'] = exc.receipt
    if progress: progress.record(result['status'], result, exit_code=code)
    emit_json(result)
    return code
