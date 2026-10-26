"""Execute an explicit evidence provider with recorded arguments and source freshness."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess

from .core import MigrationError, json_bytes, read_json, snapshot, write_new_tree
from .evidence import pack, KINDS


def capture(source, config_path, output, kind):
    source, output = source.resolve(), output.resolve()
    if kind not in KINDS:
        raise MigrationError('Unknown source evidence kind')
    if output.is_relative_to(source) or source.is_relative_to(output):
        raise MigrationError('Capture output must not overlap source')
    config = read_json(config_path)
    for field in ('command', 'version_command'):
        if not isinstance(config.get(field), list) or not config[field] or not all(isinstance(a, str) and a for a in config[field]):
            raise MigrationError('Capture provider requires ' + field + ' argument array')
    timeout = config.get('timeout_seconds', 300)
    if type(timeout) is not int or not 1 <= timeout <= 3600:
        raise MigrationError('Capture timeout must be 1..3600 seconds')
    before = snapshot(source)['sha256']
    # Output remains present on failure so the actual diagnostics are retained.
    write_new_tree(output, {'capture-start.json': json_bytes({'source_sha256': before, 'started_at': datetime.now(timezone.utc).isoformat()})})
    artifacts = output / 'artifacts'
    artifacts.mkdir()
    command = [arg.replace('{source}', str(source)).replace('{artifacts}', str(artifacts)) for arg in config['command']]
    report = {'source_sha256': before, 'kind': kind, 'command': command, 'status': 'capture_failed', 'claims': 'not_validated'}
    try:
        version = subprocess.run(config['version_command'], capture_output=True, timeout=30, shell=False)
        (artifacts / 'provider-version.stdout.log').write_bytes(version.stdout)
        (artifacts / 'provider-version.stderr.log').write_bytes(version.stderr)
        if version.returncode or not version.stdout.strip():
            raise MigrationError('Provider version command did not succeed with a version string')
        result = subprocess.run(command, cwd=source, capture_output=True, timeout=timeout, shell=False)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
        report['provider_version'] = version.stdout.decode('utf-8', errors='replace').strip()
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code = exc.stdout or b'', exc.stderr or b'', None
        report['error'] = 'Provider timeout'
    except (OSError, MigrationError) as exc:
        stdout, stderr, code = b'', str(exc).encode('utf-8'), None
        report['error'] = str(exc)
    (artifacts / 'provider.stdout.log').write_bytes(stdout)
    (artifacts / 'provider.stderr.log').write_bytes(stderr)
    report['exit_code'] = code
    report['source_changed'] = snapshot(source)['sha256'] != before
    if code == 0 and not report['source_changed']:
        pack(source, artifacts, output / 'evidence', kind, report['provider_version'])
        report['status'] = 'captured'
    (output / 'capture.json').write_bytes(json_bytes(report))
    return report
