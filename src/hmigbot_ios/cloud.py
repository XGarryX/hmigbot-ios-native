"""Portable macOS cloud builds. Preparation never publishes source or credentials."""
from pathlib import Path
import json
import re
import subprocess

from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot, source_snapshot, write_new_tree


def validate_config(config):
    for key in ('project', 'scheme', 'configuration', 'runner'):
        if not isinstance(config.get(key), str) or not config[key].strip() or '\n' in config[key]:
            raise MigrationError('Cloud configuration needs ' + key)
    if not config['project'].endswith(('.xcodeproj', '.xcworkspace')):
        raise MigrationError('project must identify an .xcodeproj or .xcworkspace')
    if config.get('test_destination') is not None and not isinstance(config['test_destination'], str):
        raise MigrationError('test_destination must be a destination string')
    setups = config.get('setup_commands', [])
    if not isinstance(setups, list) or any(not isinstance(command, list) or not command or
        not all(isinstance(arg, str) and arg for arg in command) for command in setups):
        raise MigrationError('setup_commands must contain executable argument arrays')
    return config


def prepare(source, config_path, output):
    source, output = source.resolve(), output.resolve()
    if output.is_relative_to(source) or source.is_relative_to(output):
        raise MigrationError('Cloud output must not overlap source')
    config = validate_config(read_json(config_path))
    if not safe_child(source, config['project']).is_dir():
        raise MigrationError('Selected Xcode project/workspace does not exist under source')
    before = snapshot(source)
    migration = source_snapshot(source)
    files = {}
    for entry in before['files']:
        path = Path(entry['path'])
        if path.suffix.lower() in {'.p12', '.pfx', '.mobileprovision', '.key', '.pem'} or path.name.startswith('.env'):
            raise MigrationError('Remove credential material from the export source: ' + entry['path'])
        files['source/' + entry['path']] = (source / entry['path']).read_bytes()
    config = {**config, 'source_sha256': migration['sha256']}
    root = Path(__file__).resolve().parents[2]
    for folder in ('src',):
        for path in (root / folder).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                files['tool/' + path.relative_to(root).as_posix()] = path.read_bytes()
    files['tool/scripts/ios2harmony.py'] = (root / 'scripts/ios2harmony.py').read_bytes()
    files['build_source.py'] = (root / 'providers/xcode/build_source.py').read_bytes()
    files['cloud-config.json'] = json_bytes(config)
    # All user/project strings are data files or environment values, never interpolated into shell code.
    runner = json.dumps(config['runner'])
    workflow = f'''name: HMigBot iOS source verification
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  source:
    runs-on: {runner}
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - name: Build device app and retain source evidence
        run: python3 build_source.py --source source --config cloud-config.json --output build
      - name: Upload evidence and unsigned IPA
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: hmigbot-ios-source
          path: build/
          if-no-files-found: error
          retention-days: 7
'''
    files['.github/workflows/hmigbot-ios.yml'] = workflow.encode()
    files['.gitattributes'] = b'* -text\n'
    files['.gitignore'] = b'build/\n__pycache__/\n.DS_Store\n'
    files['README.md'] = ('# iOS source verification\n\nPrepared locally by HMigBot iOS. '
        'Contains project source; use a private repository. Run the manual workflow. '
        'The unsigned IPA requires legitimate local Apple signing before installation. '
        'No Apple account credentials are needed by this unsigned workflow.\n').encode()
    if snapshot(source)['sha256'] != before['sha256']:
        raise MigrationError('Source changed during cloud preparation')
    write_new_tree(output, files)
    return {'status': 'prepared', 'output': str(output), 'source_sha256': migration['sha256'],
            'repository_sha256': before['sha256'],
            'files': len(files), 'upload_performed': False, 'signing': 'unsigned_for_local_signing'}


def gh_command(gh, args, timeout=60):
    try:
        result = subprocess.run([str(gh), *args], capture_output=True, timeout=timeout, shell=False)
    except subprocess.TimeoutExpired as exc:
        raise MigrationError('GitHub operation timed out; inspect its run before retrying mutations') from exc
    if result.returncode:
        raise MigrationError('GitHub operation failed: ' + result.stderr.decode('utf-8', errors='replace')[-1500:])
    return result.stdout


def repository_name(value):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', value):
        raise MigrationError('Use an explicit owner/repository name')
    return value


def dispatch(gh, repository, ref, workflow='hmigbot-ios.yml'):
    repository_name(repository)
    repo = json.loads(gh_command(gh, ['repo', 'view', repository, '--json', 'isPrivate,nameWithOwner']))
    if not repo.get('isPrivate'):
        raise MigrationError('Cloud dispatch requires a private repository for source confidentiality')
    if not ref or ref.startswith('-') or not re.fullmatch(r'[A-Za-z0-9_./-]+', ref):
        raise MigrationError('Invalid Git ref')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+\.ya?ml', workflow):
        raise MigrationError('Expected a workflow filename')
    gh_command(gh, ['workflow', 'run', workflow, '--repo', repository, '--ref', ref])
    return {'status': 'dispatched', 'repository': repository, 'ref': ref,
            'next': 'Use gh run list to select the new run ID; cloud-fetch never chooses a run implicitly'}


def fetch(gh, repository, run_id, source, output):
    repository_name(repository)
    if not re.fullmatch('[0-9]+', str(run_id)):
        raise MigrationError('Run ID must be numeric')
    output, source = output.resolve(), source.resolve()
    if output.exists() or output.is_relative_to(source) or source.is_relative_to(output):
        raise MigrationError('Cloud download needs a new directory separate from source')
    run = json.loads(gh_command(gh, ['run', 'view', str(run_id), '--repo', repository, '--json',
        'databaseId,headSha,status,conclusion,url,workflowName,event']))
    if run.get('status') != 'completed':
        return {'status': 'pending', 'run': run}
    gh_command(gh, ['run', 'download', str(run_id), '--repo', repository, '--name', 'hmigbot-ios-source', '--dir', str(output)], timeout=180)
    (output / 'github-run.json').write_bytes(json_bytes(run))
    report = read_json(output / 'cloud-result.json')
    if report.get('source_sha256') != source_snapshot(source)['sha256']:
        raise MigrationError('Downloaded evidence belongs to another source snapshot')
    artifacts = report.get('artifacts')
    if not isinstance(artifacts, dict) or not artifacts:
        raise MigrationError('Cloud result has no hashed artifacts')
    for path, sha in artifacts.items():
        file = safe_child(output, path)
        if not file.is_file() or digest(file.read_bytes()) != sha:
            raise MigrationError('Cloud artifact hash mismatch: ' + path)
    passed = run.get('conclusion') == 'success' and report.get('status') == 'build_passed'
    if passed:
        from .evidence import validate
        from .iphone import inspect_ipa
        if not {'application-unsigned.ipa', 'evidence/manifest.json'}.issubset(artifacts):
            raise MigrationError('Successful cloud build lacks IPA or evidence manifest')
        validate(source, output / 'evidence')
        inspect_ipa(output / 'application-unsigned.ipa')
    return {'status': 'build_passed' if passed else 'build_failed', 'run': run, 'output': str(output),
            'signing': report.get('signing'), 'installation': 'not_performed', 'source_sha256': report['source_sha256']}
