"""Run reproducible release checks and retain logs. External validators are optional paths."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def unit_timeout_seconds(value):
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError('Unit timeout must be an integer from 1 to 7200 seconds')
    if not 1 <= seconds <= 7200:
        raise argparse.ArgumentTypeError('Unit timeout must be an integer from 1 to 7200 seconds')
    return seconds


def fresh_test_temp(output, selected=None):
    """Pytest purges basetemp: accept only a fresh, dedicated, non-evidence path."""
    selected = selected if selected is not None else output / 'test-temp'
    if selected.exists() or selected.is_symlink():
        raise ValueError('Use a new, nonexistent dedicated --test-temp directory, never an existing path or drive root')
    path = selected.resolve()
    if path == Path(path.anchor) or path.exists():
        raise ValueError('Use a new, nonexistent dedicated --test-temp directory, never an existing path or drive root')
    if path == output or path in output.parents:
        raise ValueError('--test-temp must not contain the evidence directory')
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--plugin-validator', type=Path)
    parser.add_argument('--skill-validator', type=Path)
    parser.add_argument('--unit-timeout-seconds', type=unit_timeout_seconds, default=1800,
                        help='Full pytest-suite timeout in seconds (1..7200; default: 1800)')
    parser.add_argument('--test-temp', type=Path,
                        help='New nonexistent dedicated pytest basetemp; use a short path on Windows')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit('Use a new evidence directory')
    try:
        test_temp = fresh_test_temp(output, args.test_temp)
    except ValueError as exc:
        parser.error(str(exc))
    output.mkdir(parents=True)
    # Reserve exclusively before starting pytest. An intervening directory must
    # fail here rather than authorizing pytest to remove someone else's files.
    test_temp.mkdir(parents=True, exist_ok=False)
    checks = []
    def command(name, arguments, *, timeout_seconds=600):
        env = {**os.environ, 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1',
               'HMIGBOT_TEST_RUNTIME': str(ROOT),
               'PYTHONPATH': str(ROOT / 'src') + os.pathsep + str(ROOT / 'tests') + os.pathsep + os.environ.get('PYTHONPATH', '')}
        timed_out = False
        if sys.platform == 'darwin':
            env['TMPDIR'] = str(Path('/tmp').resolve())
        try:
            result = subprocess.run(arguments, cwd=ROOT, env=env, capture_output=True, timeout=timeout_seconds, shell=False)
            stdout, stderr, code = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, code = exc.stdout or b'', exc.stderr or b'', None
            timed_out = True
        except OSError as exc:
            stdout, stderr, code = b'', str(exc).encode('utf-8'), None
        (output / (name + '.stdout.log')).write_bytes(stdout)
        (output / (name + '.stderr.log')).write_bytes(stderr)
        checks.append({'name': name, 'passed': code == 0, 'exit_code': code,
                       'timeout_seconds': timeout_seconds, 'timed_out': timed_out})
    # Collect both unittest classes and function-style pytest tests (doctor,
    # Swift boundaries). unittest discovery only imports the latter silently.
    command('unit-tests', [sys.executable, '-X', 'utf8', '-m', 'pytest', 'tests',
                          '-q', '-p', 'no:cacheprovider', '--basetemp', str(test_temp),
                          '--ignore=tests/fixtures', '--ignore=tests/evaluations'],
            timeout_seconds=args.unit_timeout_seconds)
    command('upstream-resource-audit', [sys.executable, '-X', 'utf8', 'scripts/audit_upstream.py'])
    command('scheduler-resource-audit', [sys.executable, '-X', 'utf8', 'scripts/audit_scheduler.py'])
    command('external-expertise-audit', [sys.executable, '-X', 'utf8', 'scripts/a2h_ios.py', 'expertise-audit'])
    command('native-instruction-surface', [sys.executable, '-X', 'utf8', 'scripts/audit_native_surface.py'])
    command('original-pipeline-compatibility', [sys.executable, '-X', 'utf8', 'scripts/validate_native_pipeline.py', '--output', str(output / 'native-pipeline')])
    manifest = json.loads((ROOT / '.codex-plugin/plugin.json').read_text(encoding='utf-8-sig'))
    catalog = json.loads((ROOT / 'src/hmigbot_ios/capabilities.json').read_text(encoding='utf-8'))
    version = re.search(r'__version__ = "([^"]+)"', (ROOT / 'src/hmigbot_ios/__init__.py').read_text()).group(1)
    pyproject_version = re.search(r'version = "([^"]+)"', (ROOT / 'pyproject.toml').read_text()).group(1)
    checks.append({'name': 'version-consistency', 'passed': len({manifest['version'], catalog['tool_version'], version, pyproject_version}) == 1, 'version': version})
    skills = sorted(p.parent for p in (ROOT / 'skills').glob('*/SKILL.md'))
    checks.append({'name': 'skill-catalog-coverage', 'passed': {s.name for s in skills} == set(catalog['public_skills']) and len(skills) == 96 and len(catalog['atoms']) == 62 and
        all(a['status'] == 'checklist_reference' and (ROOT / 'skills' / a['skill'] / 'SKILL.md').is_file() for a in catalog['atoms']),
        'skill_count': len(skills), 'atom_count': len(catalog['atoms'])})
    wrappers_equal = all((ROOT / 'skills' / name / 'scripts/run.py').read_bytes() == (ROOT / 'scripts/skill_entry.py').read_bytes()
                         for name in ('ios-source-analysis', 'ios-project-inspector', 'ios-ui-analyzer', 'ios-feature-analyzer', 'ios-api-inventory', 'ios-resources-convert', 'ios-ui-to-arkui'))
    checks.append({'name': 'portable-skill-wrappers', 'passed': wrappers_equal})
    missing = []
    # Upstream vendor snapshots and project-output templates contain remote-relative,
    # example, and historical links; scope this gate to maintained delivery instructions.
    docs = [ROOT / 'README.md', *(ROOT / 'docs').glob('*.md')]
    docs += [p for p in (ROOT / 'skills').rglob('ios-*.md') if '/bin/' not in p.as_posix()]
    docs += [p for name in ('ios-source-analysis', 'ios-project-inspector', 'ios-ui-analyzer', 'ios-feature-analyzer', 'ios-api-inventory', 'ios-resources-convert', 'ios-ui-to-arkui')
             for p in (ROOT / 'skills' / name).rglob('*.md')]
    for path in docs:
        if path.read_text(encoding='utf-8-sig').startswith('> 历史记录'):
            continue
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8-sig')):
            if '://' in target or target.startswith('#'):
                continue
            local = target.split('#')[0]
            if not (path.parent / local).exists():
                missing.append({'document': path.relative_to(ROOT).as_posix(), 'target': target})
    checks.append({'name': 'local-document-links', 'passed': not missing, 'missing': missing})
    invalid_roles = []
    roles = sorted((ROOT / 'agents-codex').glob('*.toml'))
    for role in roles:
        try:
            data = tomllib.loads(role.read_text(encoding='utf-8-sig'))
            if not data.get('developer_instructions'): invalid_roles.append(role.name)
        except (ValueError, OSError): invalid_roles.append(role.name)
    checks.append({'name': 'agent-role-contracts', 'passed': len(roles) == 29 and not invalid_roles,
                   'count': len(roles), 'invalid': invalid_roles})
    if args.plugin_validator:
        command('plugin-validator', [sys.executable, '-X', 'utf8', str(args.plugin_validator.resolve()), str(ROOT)])
    if args.skill_validator:
        failures = []
        for skill in skills:
            result = subprocess.run([sys.executable, '-X', 'utf8', str(args.skill_validator.resolve()), str(skill)], cwd=ROOT, capture_output=True, timeout=30)
            if result.returncode:
                failures.append({'skill': skill.name, 'stdout': result.stdout.decode('utf-8', errors='replace'), 'stderr': result.stderr.decode('utf-8', errors='replace')})
        checks.append({'name': 'official-skill-validator', 'passed': not failures, 'checked': len(skills), 'failures': failures})
    report = {'version': version, 'status': 'passed' if all(c['passed'] for c in checks) else 'failed', 'checks': checks,
              'runner_options': {'unit_timeout_seconds': args.unit_timeout_seconds,
                                 'test_temp': str(test_temp),
                                 'test_temp_ownership': 'new dedicated directory reserved exclusively before pytest'},
              'scope': 'Tool/contract/packaging checks; excludes application device and equivalence acceptance'}
    (output / 'release-checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
