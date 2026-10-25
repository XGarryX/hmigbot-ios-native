#!/usr/bin/env python3
"""Run on macOS/Xcode. Source selection is data, and no Apple secrets are used."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import zipfile


def membership_selection(parsed, settings, *, scheme, configuration, sdk, xcode_version, product):
    """Scope actual membership by the selected build settings, not by directory names."""
    targets = sorted({entry.get('buildSettings', {}).get('TARGET_NAME') for entry in parsed
                      if entry.get('buildSettings', {}).get('WRAPPER_EXTENSION') in {'app', 'appex'}
                      and entry.get('buildSettings', {}).get('TARGET_NAME')})
    if settings.get('TARGET_NAME') and settings['TARGET_NAME'] not in targets:
        targets.append(settings['TARGET_NAME'])
    toolchain = {key: str(settings[key]) for key in
                 ('SWIFT_VERSION', 'GCC_VERSION', 'SDK_VERSION', 'TOOLCHAINS', 'SWIFT_OPTIMIZATION_LEVEL',
                  'IPHONEOS_DEPLOYMENT_TARGET', 'SWIFT_ACTIVE_COMPILATION_CONDITIONS')
                 if str(settings.get(key, '')).strip()}
    return {'scheme': scheme, 'configuration': configuration, 'sdk': sdk,
            'xcode_version': xcode_version, 'product': product, 'targets': targets,
            'architectures': str(settings.get('ARCHS', '')).split(), 'toolchain': toolchain}


def record_source_membership(*, source, derived_data, capture, build_log, selection):
    """Capture the actual compiled source membership of the device build just made."""
    from hmigbot_ios.source_build_membership import collect
    return collect(source, derived_data, capture, selection, build_log=build_log)


def membership_summary(document):
    """Small report entry; the full contract stays in capture/source-files.json."""
    return {'status': document['membership_status'],
            'artifact': 'artifacts/source-files.json',
            'source_files': len(document['source_files']),
            'non_member_inputs': document['counts']['non_member_inputs'],
            'unsupported_inputs': document['counts']['unsupported_inputs'],
            'unresolved': [{'reason': item['reason'], 'path': item['path'],
                            'detail': item['detail']} for item in document['unresolved']],
            'limitations': document['limitations']}


class MembershipIncomplete(RuntimeError):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    runtime = Path(__file__).resolve().parent / 'tool/src'
    if not runtime.is_dir():
        runtime = Path(__file__).resolve().parents[2] / 'src'
    sys.path.insert(0, str(runtime))
    from hmigbot_ios.core import snapshot, safe_child, json_bytes
    from hmigbot_ios.evidence import pack
    from hmigbot_ios.cloud import validate_config
    config = validate_config(json.loads(args.config.read_text(encoding='utf-8')))
    if sys.platform != 'darwin':
        raise SystemExit('This provider requires macOS with Xcode; use the cloud workflow from Windows.')
    if output.exists():
        raise SystemExit('Use a new output directory')
    output.mkdir(parents=True)
    capture = output / 'capture'
    capture.mkdir()
    before = snapshot(source)
    report = {'source_sha256': before['sha256'], 'status': 'build_failed', 'signing': 'unsigned',
              'installation': 'not_performed', 'tests': 'not_requested', 'artifacts': {}, 'commands': []}
    env = os.environ.copy()
    if config.get('developer_dir'):
        env['DEVELOPER_DIR'] = config['developer_dir']
    def run(name, command):
        result = subprocess.run(command, cwd=source, env=env, capture_output=True, timeout=1500, shell=False)
        (capture / (name + '.stdout.log')).write_bytes(result.stdout)
        (capture / (name + '.stderr.log')).write_bytes(result.stderr)
        report['commands'].append({'name': name, 'arguments': command, 'exit_code': result.returncode})
        if result.returncode:
            raise RuntimeError(name + ' failed; inspect capture logs')
        return result.stdout
    try:
        if config.get('source_sha256') and before['sha256'] != config['source_sha256']:
            raise RuntimeError('Source fingerprint differs from the prepared export')
        project = safe_child(source, config['project'])
        if not project.is_dir():
            raise RuntimeError('Missing project/workspace')
        report['xcode_version'] = run('xcode-version', ['xcodebuild', '-version']).decode().strip()
        for number, command in enumerate(config.get('setup_commands', [])):
            run('setup-' + str(number), command)
        selected = ['xcodebuild', '-workspace' if project.suffix == '.xcworkspace' else '-project',
                    str(project), '-scheme', config['scheme'], '-configuration', config['configuration']]
        unsigned = ['CODE_SIGNING_ALLOWED=NO', 'CODE_SIGNING_REQUIRED=NO', 'CODE_SIGN_IDENTITY=', 'DEVELOPMENT_TEAM=']
        device = selected + ['-sdk', 'iphoneos', '-destination', 'generic/platform=iOS',
                            '-derivedDataPath', str(output / 'DerivedData')] + unsigned
        settings = run('settings', device + ['-showBuildSettings', '-json'])
        # Ensure successful output is parseable before it enters the source_build evidence bundle.
        parsed = json.loads(settings)
        (capture / 'build-settings.json').write_bytes(json_bytes(parsed))
        run('device-build', device + ['build'])
        app_settings = [p['buildSettings'] for p in parsed if p.get('buildSettings', {}).get('WRAPPER_EXTENSION') == 'app']
        if len(app_settings) != 1:
            raise RuntimeError('Scheme must produce exactly one main application; select a narrower scheme')
        settings = app_settings[0]
        app = Path(settings['TARGET_BUILD_DIR']) / settings['FULL_PRODUCT_NAME']
        if not app.is_dir() or not app.resolve().is_relative_to(output):
            raise RuntimeError('Built application is missing or outside DerivedData')
        info = plistlib.loads((app / 'Info.plist').read_bytes())
        if info.get('CFBundleSupportedPlatforms') != ['iPhoneOS']:
            raise RuntimeError('Refusing to package a simulator product as a device IPA')
        report['bundle_id'] = info['CFBundleIdentifier']
        report['extensions'] = []
        for bundle in [app, *app.rglob('*.appex')]:
            bi = plistlib.loads((bundle / 'Info.plist').read_bytes())
            executable = bundle / bi['CFBundleExecutable']
            arches = run('arch-' + bundle.stem, ['lipo', '-archs', str(executable)]).decode().split()
            if 'arm64' not in arches or any(a.startswith('x86') for a in arches):
                raise RuntimeError('Unexpected device architecture')
            if bundle != app:
                report['extensions'].append(bi['CFBundleIdentifier'])
        # Capture actual compiled membership while the build tree still exists: the
        # cleanup below deletes the only record of which files really compiled.
        membership = record_source_membership(
            source=source, derived_data=output / 'DerivedData', capture=capture,
            build_log=capture / 'device-build.stdout.log',
            selection=membership_selection(parsed, settings, scheme=config['scheme'],
                configuration=config['configuration'], sdk='iphoneos',
                xcode_version=report.get('xcode_version') or 'xcodebuild',
                product=report['bundle_id']))
        report['source_membership'] = membership_summary(membership)
        if membership['membership_status'] != 'complete':
            raise MembershipIncomplete('Actual build source membership is '
                + membership['membership_status']
                + '; inspect capture/source-files.json before claiming a selected-build scope')
        stage = output / 'package/Payload'
        stage.mkdir(parents=True)
        shutil.copytree(app, stage / app.name, symlinks=True)
        run('package', ['ditto', '-c', '-k', '--keepParent', str(stage), str(output / 'application-unsigned.ipa')])
        with zipfile.ZipFile(output / 'application-unsigned.ipa') as archive:
            if archive.testzip():
                raise RuntimeError('IPA ZIP integrity failure')
        if config.get('test_destination'):
            report['tests'] = 'failed'
            run('source-tests', selected + ['-destination', config['test_destination'], '-derivedDataPath',
                str(output / 'TestDerivedData'), '-resultBundlePath', str(capture / 'source-tests.xcresult')] + unsigned + ['test'])
            report['tests'] = 'passed'
        if snapshot(source)['sha256'] != before['sha256']:
            raise RuntimeError('Source changed during build')
        pack(source, capture, output / 'evidence', 'source_build', report['xcode_version'])
        report['status'] = 'build_passed'
    except MembershipIncomplete as exc:
        # The build itself succeeded; the capture cannot serve a selected-build scope.
        # Keep the evidence that explains why, then fail closed instead of publishing
        # a bundle whose membership is not complete.
        report['status'] = 'membership_incomplete'
        report['error'] = str(exc)
        try:
            pack(source, capture, output / 'evidence', 'source_build',
                 report.get('xcode_version') or 'xcodebuild')
        except (OSError, ValueError) as error:
            report['error'] = str(exc) + '; evidence pack failed: ' + str(error)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        report['error'] = str(exc)
    finally:
        # Upload only useful evidence and IPA, not gigabytes of intermediate products.
        for name in ('DerivedData', 'TestDerivedData', 'package'):
            candidate = output / name
            if candidate.exists() and candidate.resolve().is_relative_to(output):
                shutil.rmtree(candidate)
        for file in sorted(output.rglob('*')):
            if file.is_file():
                report['artifacts'][file.relative_to(output).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
        (output / 'cloud-result.json').write_bytes(json_bytes(report))
    print(json.dumps({'status': report['status'], 'tests': report['tests'], 'error': report.get('error')}, indent=2))
    return 0 if report['status'] == 'build_passed' else 3


if __name__ == '__main__':
    raise SystemExit(main())
