"""Capture and replay SwiftPM manifest evaluation, without claiming a resolved graph.

Checksums bind these portable records to source and artifacts. They do not certify
the identity of the executable or authenticate an evidence bundle's author.
"""
from __future__ import annotations

import json
from pathlib import Path
import platform
import re
import subprocess

from .contracts import require, validate_file_map
from .core import source_snapshot
from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot, write_new_tree


KIND = 'swiftpm_manifest_evaluation'
SCOPE = 'current_host_manifest_evaluation'


def _argv(value, field):
    require(isinstance(value, list) and bool(value)
            and all(isinstance(arg, str) and arg and '\0' not in arg for arg in value),
            f'{field} must be an explicit nonempty executable argument array')
    return value


def _commands(item):
    command = _argv(item.get('command'), 'command')
    version = _argv(item.get('version_command'), 'version_command')
    require('package' in command and 'dump-package' in command
            and command.index('package') < command.index('dump-package'),
            'Manifest command must invoke SwiftPM package dump-package')
    require('--version' in version, 'version_command must request the Swift tool version')
    timeout = item.get('timeout_seconds', 120)
    require(type(timeout) is int and 1 <= timeout <= 3600, 'timeout_seconds must be 1..3600')
    return command, version, timeout


def _package_directory(value, source, command):
    """Resolve only native paths or the documented WSL Windows-drive mount."""
    require(isinstance(value, str) and bool(value) and value == value.strip(),
            'SwiftPM package directory must be an explicit path')
    launcher = command[0].replace('\\', '/').rsplit('/', 1)[-1].lower()
    if launcher in {'wsl', 'wsl.exe'}:
        match = re.fullmatch(r'/mnt/([A-Za-z])(?:/(.*))?', value)
        require(match is not None and source.drive.endswith(':'),
                'Unsupported WSL package directory; use /mnt/<drive>/... for the source directory')
        remainder = match.group(2) or ''
        require(not {'..', '.'} & set(remainder.split('/')) and '\\' not in remainder,
                'WSL package directory must use an unambiguous drive path')
        return Path(match.group(1).upper() + ':/' + remainder).resolve()
    require(not value.startswith(('\\\\', '//')) and '://' not in value,
            'Remote package directories are not supported')
    directory = Path(value)
    return (directory if directory.is_absolute() else source / directory).resolve()


def _bind_package_path(command, source, package_dir):
    values = []
    for index, argument in enumerate(command):
        if argument == '--package-path':
            require(index + 1 < len(command), 'SwiftPM --package-path requires a directory')
            values.append(command[index + 1])
        elif argument.startswith('--package-path='):
            values.append(argument[len('--package-path='):])
    require(len(values) == 1, 'SwiftPM command requires exactly one explicit --package-path')
    require(_package_directory(values[0], source, command) == package_dir,
            'SwiftPM --package-path does not identify the configured Package.swift directory')


def _swift_version(output):
    require(bool(re.search(r'(?<![A-Za-z])(?:Apple )?Swift version [0-9]+\.[0-9]+(?:\.[0-9]+)?(?=\s|$)', output)),
            'Version probe output does not identify a Swift tool version')
    return output


def _configuration(source, value):
    require(isinstance(value, dict) and type(value.get('schema_version')) is int
            and value['schema_version'] == 1, 'Unsupported manifest evaluation configuration')
    require(not set(value) - {'schema_version', 'manifests'}, 'Unknown manifest evaluation configuration fields')
    items = value.get('manifests')
    require(isinstance(items, list) and bool(items), 'manifests must be a nonempty array')
    seen, result = set(), []
    for item in items:
        require(isinstance(item, dict), 'Manifest configuration must be an object')
        require(not set(item) - {'path', 'command', 'version_command', 'timeout_seconds', 'conditions'},
                'Unknown manifest configuration fields')
        name = item.get('path')
        require(isinstance(name, str), 'Manifest path must be relative to source')
        path = safe_child(source, name)
        require(path.name == 'Package.swift' and path.is_file(),
                f'Manifest must identify an existing Package.swift: {name}')
        key = path.relative_to(source).as_posix().casefold()
        require(key not in seen, f'Duplicate manifest: {name}')
        seen.add(key)
        command, version, timeout = _commands(item)
        conditions = item.get('conditions', '')
        require(isinstance(conditions, str), 'conditions must be an explanatory string')
        expand = lambda args: [arg.replace('{source}', str(source)).replace('{package_dir}', str(path.parent)) for arg in args]
        command = expand(command)
        _bind_package_path(command, source, path.parent)
        result.append({'path': name, 'command': command, 'version_command': expand(version),
                       'timeout_seconds': timeout, 'conditions': conditions})
    return result


def _parse_dump(data, source, package_dir, command):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, f'Duplicate SwiftPM JSON key: {key}')
            value[key] = item
        return value

    def nonfinite(value):
        raise MigrationError(f'Non-finite SwiftPM JSON value: {value}')

    try:
        value = json.loads(data.decode('utf-8'), object_pairs_hook=unique, parse_constant=nonfinite)
    except (UnicodeError, ValueError) as exc:
        raise MigrationError(f'SwiftPM dump-package did not produce valid UTF-8 JSON: {exc}') from exc
    require(isinstance(value, dict), 'SwiftPM dump-package must produce an object')
    if 'packageKind' in value:
        kind = value['packageKind']
        require(isinstance(kind, dict) and set(kind) == {'root'} and isinstance(kind['root'], list)
                and len(kind['root']) == 1, 'SwiftPM packageKind must identify one root package')
        require(_package_directory(kind['root'][0], source, command) == package_dir,
                'SwiftPM dump-package root does not identify the configured Package.swift directory')
    require(isinstance(value.get('name'), str) and bool(value['name'].strip()), 'SwiftPM manifest name is missing')
    targets, dependencies = value.get('targets'), value.get('dependencies')
    require(isinstance(targets, list), 'SwiftPM targets must be an array (possibly empty)')
    require(isinstance(dependencies, list), 'SwiftPM dependencies must be an array (possibly empty)')
    seen = set()
    for target in targets:
        require(isinstance(target, dict) and isinstance(target.get('name'), str)
                and bool(target['name'].strip()), 'SwiftPM target must have a name')
        require(target['name'] not in seen, 'Duplicate SwiftPM target name')
        seen.add(target['name'])
    require(all(isinstance(dep, dict) and bool(dep) for dep in dependencies),
            'SwiftPM dependencies must retain their structured manifest declarations')
    return {key: value[key] for key in ('name', 'targets', 'dependencies')}


def _bytes(value):
    return value.encode('utf-8') if isinstance(value, str) else value or b''


def _run(command, source, timeout, prefix, files):
    record = {'command': command, 'cwd': str(source), 'timeout_seconds': timeout,
              'exit_code': None, 'timed_out': False, 'error': None,
              'stdout': prefix + '.stdout.log', 'stderr': prefix + '.stderr.log'}
    stdout, stderr = b'', b''
    try:
        process = subprocess.run(command, cwd=source, capture_output=True, timeout=timeout, shell=False)
        record['exit_code'], stdout, stderr = process.returncode, _bytes(process.stdout), _bytes(process.stderr)
    except subprocess.TimeoutExpired as exc:
        record.update(timed_out=True, error=f'Command timed out after {timeout} seconds')
        stdout, stderr = _bytes(exc.stdout), _bytes(exc.stderr)
    except OSError as exc:
        record['error'] = str(exc)
    files[record['stdout']], files[record['stderr']] = stdout, stderr
    files[prefix + '.command.json'] = json_bytes(record)
    return record


def _successful(record):
    return type(record.get('exit_code')) is int and record['exit_code'] == 0 and record.get('timed_out') is False and record.get('error') is None


def capture(source: Path, config_path: Path, output: Path) -> dict:
    """Run explicit SwiftPM commands and save successful or failed evidence.

    Invalid commands, JSON, versions or source changes produce capture_failed
    records; unsafe output locations and existing nonempty output are refused.
    """
    source, config_path, output = Path(source).resolve(), Path(config_path).resolve(), Path(output).resolve()
    require(not output.is_relative_to(source) and not source.is_relative_to(output),
            'Manifest evidence output must not overlap source')
    require(not output.exists() or (output.is_dir() and not any(output.iterdir())),
            f'Output must be absent or empty: {output}')
    before = source_snapshot(source)
    host = {'system': platform.system(), 'release': platform.release(), 'machine': platform.machine()}
    files = {'artifacts/source.before.json': json_bytes(before)}
    report = {'schema_version': 1, 'kind': KIND, 'status': 'capture_failed',
              'source_sha256': before['sha256'], 'source_after_sha256': None, 'source_changed': False,
              'source_before_artifact': 'artifacts/source.before.json',
              'source_after_artifact': 'artifacts/source.after.json',
              'config_artifact': 'artifacts/config.json', 'host': host,
              'scope': SCOPE, 'capture_authenticity': 'not_verified',
              'dependency_resolution': 'not_verified', 'behavior_equivalence': 'not_verified',
              'manifests': [], 'failures': []}
    try:
        files['artifacts/config.json'] = config_path.read_bytes()
        settings = _configuration(source, read_json(config_path))
        for index, setting in enumerate(settings):
            prefix = f'artifacts/manifest-{index:04d}'
            item = {**setting, 'source_sha256': before['sha256'],
                    'manifest_sha256': digest(safe_child(source, setting['path']).read_bytes()),
                    'status': 'capture_failed', 'host': host, 'scope': SCOPE,
                    'version_record': prefix + '/version.command.json',
                    'evaluation_record': prefix + '/evaluation.command.json',
                    'evaluation_artifact': prefix + '/evaluation.stdout.log'}
            report['manifests'].append(item)
            try:
                version = _run(setting['version_command'], source, min(setting['timeout_seconds'], 30), prefix + '/version', files)
                require(_successful(version), f'Swift version probe failed for {setting["path"]}')
                version_output = files[version['stdout']].decode('utf-8').strip()
                require(bool(version_output), f'Swift version probe was empty for {setting["path"]}')
                item['version_output'] = _swift_version(version_output)
                process = _run(setting['command'], source, setting['timeout_seconds'], prefix + '/evaluation', files)
                require(_successful(process), f'SwiftPM dump-package failed for {setting["path"]}')
                item.update(_parse_dump(files[process['stdout']], source,
                    safe_child(source, setting['path']).parent, setting['command']))
                item['status'] = 'manifest_evaluated'
            except (MigrationError, UnicodeError) as exc:
                item['failure'] = str(exc)
                report['failures'].append(str(exc))
    except (MigrationError, OSError) as exc:
        report['failures'].append(str(exc))
    try:
        after = source_snapshot(source)
        files['artifacts/source.after.json'] = json_bytes(after)
        report['source_after_sha256'] = after['sha256']
        report['source_changed'] = before != after
        if report['source_changed']:
            report['failures'].append('Source changed during SwiftPM manifest capture')
    except (MigrationError, OSError) as exc:
        report['source_changed'] = True
        report['failures'].append(f'Cannot fingerprint source after capture: {exc}')
    if not report['failures'] and report['manifests']:
        report['status'] = 'captured'
    report['artifacts'] = {name: digest(data) for name, data in files.items()}
    files['manifest.json'] = json_bytes(report)
    write_new_tree(output, files)
    return report


def validate(source: Path, evidence_path: Path) -> dict:
    """Replay raw outputs, validating fingerprints instead of trusting summaries."""
    source, evidence_path = Path(source).resolve(), Path(evidence_path).resolve()
    if evidence_path.is_dir():
        bundle, path = evidence_path, evidence_path / 'manifest.json'
    else:
        require(evidence_path.name == 'manifest.json', 'Manifest evidence must identify its bundle or manifest.json')
        bundle, path = evidence_path.parent, evidence_path
    require(not bundle.is_relative_to(source) and not source.is_relative_to(bundle),
            'Manifest evidence must not overlap source')
    report = read_json(path)
    require(isinstance(report, dict) and type(report.get('schema_version')) is int
            and report['schema_version'] == 1 and report.get('kind') == KIND,
            'Unsupported SwiftPM manifest evidence contract')
    require(report.get('status') == 'captured' and report.get('failures') == []
            and report.get('source_changed') is False, 'SwiftPM manifest capture failed')
    for key, expected in (('scope', SCOPE), ('capture_authenticity', 'not_verified'),
                          ('dependency_resolution', 'not_verified'), ('behavior_equivalence', 'not_verified')):
        require(report.get(key) == expected, f'Invalid manifest evidence claim: {key}')
    files = report.get('artifacts')
    validate_file_map(files)
    for name, expected in files.items():
        require(name.startswith('artifacts/'), 'Manifest evidence artifacts must be under artifacts/')
        artifact = safe_child(bundle, name)
        require(artifact.is_file() and digest(artifact.read_bytes()) == expected,
                f'Missing or modified manifest artifact: {name}')

    def artifact(name):
        require(isinstance(name, str) and name in files, 'Referenced manifest artifact is not fingerprinted')
        return safe_child(bundle, name)

    current = source_snapshot(source)
    require(report.get('source_sha256') == current['sha256']
            and report.get('source_after_sha256') == current['sha256'],
            'Manifest evidence source fingerprint does not match current source')
    for key in ('source_before_artifact', 'source_after_artifact'):
        require(read_json(artifact(report.get(key))) == current, 'Manifest capture source snapshot is stale or modified')
    settings = _configuration(source, read_json(artifact(report.get('config_artifact'))))
    items = report.get('manifests')
    require(isinstance(items, list) and len(items) == len(settings), 'Missing or duplicate manifest evaluation entries')
    host = report.get('host')
    require(isinstance(host, dict) and all(isinstance(host.get(key), str) and host[key]
            for key in ('system', 'release', 'machine')), 'Missing manifest capture host')
    validated, seen = [], set()
    for setting, item in zip(settings, items):
        require(isinstance(item, dict) and item.get('status') == 'manifest_evaluated', 'Manifest evaluation did not succeed')
        name = item.get('path')
        require(isinstance(name, str) and name.casefold() not in seen, 'Duplicate manifest evidence path')
        seen.add(name.casefold())
        require(all(item.get(key) == value for key, value in setting.items()),
                'Manifest capture metadata disagrees with configured invocation')
        require(item.get('source_sha256') == current['sha256']
                and item.get('manifest_sha256') == digest(safe_child(source, name).read_bytes()),
                'Manifest fingerprint is stale or modified')
        require(item.get('scope') == SCOPE and item.get('host') == host, 'Manifest evaluation host/scope is missing or inconsistent')
        outputs = {}
        for label, argv, timeout in (('version', setting['version_command'], min(setting['timeout_seconds'], 30)),
                                     ('evaluation', setting['command'], setting['timeout_seconds'])):
            record = read_json(artifact(item.get(label + '_record')))
            require(isinstance(record, dict) and _successful(record), f'Raw SwiftPM {label} invocation failed')
            require(record.get('command') == argv and record.get('cwd') == str(source)
                    and record.get('timeout_seconds') == timeout,
                    f'Raw SwiftPM {label} invocation differs from its metadata')
            outputs[label] = artifact(record.get('stdout')).read_bytes()
            artifact(record.get('stderr'))
            if label == 'evaluation':
                require(item.get('evaluation_artifact') == record['stdout'], 'Evaluation stdout reference was changed')
        try:
            version = outputs['version'].decode('utf-8').strip()
        except UnicodeError as exc:
            raise MigrationError('Swift version output must be UTF-8') from exc
        require(bool(version) and item.get('version_output') == version, 'Swift version output is empty or modified')
        _swift_version(version)
        normalized = _parse_dump(outputs['evaluation'], source,
            safe_child(source, name).parent, setting['command'])
        require(all(item.get(key) == value for key, value in normalized.items()),
                'Normalized SwiftPM manifest was modified; raw dump-package output disagrees')
        validated.append({'path': name, **normalized, 'source_sha256': current['sha256'],
                          'manifest_sha256': item['manifest_sha256'], 'status': 'manifest_evaluated',
                          'evaluation_artifact': item['evaluation_artifact'],
                          'version_output': version, 'command': setting['command'],
                          'version_command': setting['version_command'], 'host': host,
                          'conditions': setting['conditions'], 'scope': SCOPE})
    return {'schema_version': 1, 'integrity_passed': True, 'source_sha256': current['sha256'],
            'manifests': validated, 'claim_validation': 'manifest_evaluated',
            'dependency_resolution': 'not_verified', 'behavior_equivalence': 'not_verified',
            'capture_authenticity': 'not_verified'}
