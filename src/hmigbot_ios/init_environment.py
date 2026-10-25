"""INIT host/Swift probes and an untrusted Xcode settings input preview.

No source configuration, build, installation, or specification is inferred from
these probes. Full source/configuration binding remains prepare-source-view's job.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess


def _environment():
    env = os.environ.copy()
    if platform.system() == 'Darwin':
        from .apple_tools import environment
        return environment()[1]
    paths = [env.get('PATH', '')]
    if platform.system() == 'Windows':
        try:
            import winreg
            for hive, key in [(winreg.HKEY_CURRENT_USER, 'Environment'),
                              (winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment')]:
                try:
                    with winreg.OpenKey(hive, key) as item:
                        paths.append(os.path.expandvars(winreg.QueryValueEx(item, 'Path')[0]))
                except OSError:
                    pass
        except ImportError:
            pass
    env['PATH'] = os.pathsep.join(paths)
    return env


def _swift_candidate(explicit, env):
    if explicit is not None:
        path = Path(explicit).expanduser().resolve()
        return path, 'explicit'
    found = shutil.which('swift.exe', path=env['PATH'])
    if found:
        return Path(found).resolve(), 'path_or_registry'
    # Only known installer roots are inspected, never a recursive drive scan.
    roots = []
    if env.get('LOCALAPPDATA'):
        roots.append(Path(env['LOCALAPPDATA']) / 'Programs/Swift/Toolchains')
    if env.get('ProgramFiles'):
        roots.append(Path(env['ProgramFiles']) / 'Swift/Toolchains')
    for root in roots:
        try:
            candidates = sorted(root.glob('*/usr/bin/swift.exe'), key=lambda p: p.stat().st_mtime, reverse=True)
            if candidates:
                return candidates[0].resolve(), 'known_installer_root'
        except OSError:
            continue
    return None, 'not_found'


def windows_swift(explicit=None):
    env = _environment()
    path, discovery = _swift_candidate(explicit, env)
    result = {'status': 'missing', 'available': False, 'path': str(path) if path else None,
              'discovery': discovery, 'executed': False, 'version': None, 'target': None,
              'exit_code': None, 'ios_sdk_verified': False, 'adapter_compatibility': 'not_checked'}
    if path is None or not path.is_file():
        result['reason'] = 'Windows Swift executable was not found; an explicit missing path is never replaced silently.'
        return result
    try:
        run = subprocess.run([str(path), '--version'], env=env, shell=False,
                             capture_output=True, timeout=15)
    except subprocess.TimeoutExpired:
        result.update(status='timeout', executed=True, reason='swift --version timed out')
        return result
    except OSError as exc:
        result.update(status='not_executable', reason=str(exc))
        return result
    output = run.stdout.decode('utf-8', errors='replace')
    error = run.stderr.decode('utf-8', errors='replace')
    text = output + '\n' + error
    result.update(executed=True, exit_code=run.returncode,
                  version_output=output[:4096], version_stderr=error[:4096])
    if run.returncode:
        result.update(status='failed', reason='swift --version returned a nonzero exit code')
        return result
    version = re.search(r'(?:Apple )?Swift version\s+(\d+(?:\.\d+)+)', text)
    target = re.search(r'^Target:\s*(\S+)\s*$', text, re.MULTILINE)
    result['version'] = version[1] if version else None
    result['target'] = target[1] if target else None
    if not version or not target:
        result.update(status='unverified', reason='Version output did not identify both a Swift version and its target')
    elif 'windows' not in target[1].lower().split('-'):
        result.update(status='wrong_host_target', reason='This Swift reports a non-Windows target')
    else:
        result.update(status='available', available=True,
                      reason='Windows Swift starts successfully; iOS SDK and adapter runtime compatibility remain separate checks.')
    return result


def xcode_settings_input(value=None):
    result = {'status': 'not_provided', 'path': None, 'query_evidence': 'not_checked',
              'source_binding': 'not_checked', 'source_view_prepared': False,
              'ios_build_verified': False, 'ios_signing_verified': False, 'ios_runtime_verified': False}
    if value is None:
        return result
    supplied = Path(value).expanduser().resolve()
    path = supplied / 'release-build-settings.json' if supplied.is_dir() else supplied
    result['path'] = str(path)
    if not path.is_file():
        result.update(status='missing', reason='Provide the actual JSON file, or a capture directory containing release-build-settings.json')
        return result
    try:
        data = json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, UnicodeError, ValueError) as exc:
        result.update(status='invalid', reason=str(exc))
        return result
    if not isinstance(data, list) or not data:
        result.update(status='invalid', reason='Expected a nonempty xcodebuild -showBuildSettings -json array')
        return result
    targets = []
    for entry in data:
        if (not isinstance(entry, dict) or not isinstance(entry.get('target'), str) or not entry['target'].strip()
                or not isinstance(entry.get('buildSettings'), dict)):
            result.update(status='invalid', reason='Each entry requires a target and a buildSettings object')
            return result
        settings = entry['buildSettings']
        if settings.get('CONFIGURATION') != 'Release':
            result.update(status='wrong_configuration', reason='The current source-view profile requires Release settings for every captured target')
            return result
        if settings.get('PLATFORM_NAME') != 'iphoneos':
            result.update(status='wrong_platform', reason='The current source-view profile requires iphoneos settings, not simulator or host settings')
            return result
        targets.append({'target': entry['target'], 'configuration': 'Release', 'platform': 'iphoneos',
                        'swift_language_mode': settings.get('SWIFT_VERSION')})
    result.update(status='release_settings_json', targets=targets,
                  capture_attachments={name: (path.parent / name).is_file()
                    for name in ['source-files.json', 'command-execution-records.json', 'bundle-files.sha256']},
                  reason='JSON structure and Release/iphoneos values were checked only; provenance, hashes, current source and selected targets still require prepare-source-view.')
    return result


def inspect_environment(*, swift=None, build_settings=None):
    system = platform.system()
    host = {'system': system, 'release': platform.release(), 'machine': platform.machine()}
    report = {'schema_version': 1, 'host': host, 'tools_installed_by_probe': False, 'source_modified': False,
              'source_build_verified': False, 'source_runtime_verified': False,
              'windows_swift': {'status': 'not_applicable', 'available': None, 'executed': False}}
    if system == 'Windows':
        report['windows_swift'] = windows_swift(swift)
    elif system == 'Darwin':
        from .apple_tools import environment
        report['apple_toolchain'] = environment()[0]
    settings = xcode_settings_input(build_settings)
    report['xcode_build_settings'] = settings
    needs_question = system == 'Windows' and settings['status'] == 'not_provided'
    report['question_required'] = needs_question
    report['next_question'] = ('是否已有 Mac 上为当前 iOS 工程导出的 Release 配置结果（xcodebuild -showBuildSettings -json）？'
                               if needs_question else None)
    report['settings_input_needs_attention'] = settings['status'] not in {'not_provided', 'release_settings_json'}
    report['static_source_reading_can_continue'] = True
    report['release_source_view_ready'] = False
    report['status'] = 'environment_checked'
    return report
