"""One explicit release boundary for packaging, installation and provenance audits.

This is tool-owned distribution policy, not an application conversion gate.
The current release supports macOS Apple Silicon. Source-only Windows adapters
are not evidence that an omitted Windows engine is available.
"""
from pathlib import PurePosixPath
import re

RELEASE_PROFILE = 'macos-arm64'
ROOT_DIRECTORIES = {'.codex-plugin', 'skills', 'scripts', 'src', 'rules', 'schemas',
                    'providers', 'docs', 'agents-codex', 'bin', 'policies', 'vendor'}
ROOT_FILES = {'.gitattributes', '.gitignore', 'README.md', 'CHANGELOG.md',
              'pyproject.toml', 'install.sh', 'uninstall.sh', 'runtime-entrypoints.json',
              'LICENSE', 'LICENSE.md', 'NOTICE', 'THIRD-PARTY-NOTICES.md', 'PLATFORM-ROADMAP.md'}
LOCAL_DIRECTORIES = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
                     '.cache', '.venv', 'node_modules', '.build', '.swiftpm', 'build',
                     'dist', 'work', '.hmigbot-ios', '.migbot', '.agents', '.codex',
                     'deriveddata', '.xcresult', '.xcarchive', '.hvigor', 'oh_modules', '.idea'}
MAINTENANCE_ROOTS = {'reports', 'evidence', 'project-cases', 'evaluations', 'spec', 'migration'}
TEST_DIRECTORIES = {'tests', 'test', '_tests', '__tests__', 'fixtures', '__fixtures__',
                    'testdata', 'test-data', 'evaluations', 'test-results'}
DEVELOPMENT_FILES = {
    'scripts/audit_native_surface.py', 'scripts/benchmark_fact_capture.py',
    'scripts/create_cloud_fixture.py', 'scripts/generate_skills.py',
    'scripts/release_purity.py', 'scripts/smoke_package.py', 'scripts/smoke_upgrade.py',
    'scripts/sync_skill_catalog.py', 'scripts/validate_native_pipeline.py',
    'scripts/validate_release.py', 'scripts/vendor_ios_expertise.py',
    'policies/native-surface-contexts.json',
    'src/hmigbot_ios/scheduler_windows_runtime.py',
    'src/hmigbot_ios/windows_scheduler_runtime.py',
    'src/hmigbot_ios/windows_python_runtime.py',
}
OTHER_PLATFORM_DIRECTORIES = {'windows-x64', 'windows-arm64', 'macos-x64',
                              'linux-x64', 'linux-arm64', 'darwin-amd64',
                              'windows-amd64', 'linux-amd64'}
ARCHIVE_SUFFIXES = {'.zip', '.tar', '.tgz', '.gz', '.bz2', '.xz', '.7z', '.rar'}
DEFERRED_SKILLS = {'arkts-scenario-runner', 'arkts-visual-verify',
                   'arkts-ui-verifier', 'ios-screenshot-analyzer'}
DEFERRED_ROLES = {'scenario-builder', 'visual-fixer', 'visual-fixer-reviewer'}
DEFERRED_SOURCE_ALIASES = {'android-screenshot-analyzer'}


def release_profile():
    return {'id': RELEASE_PROFILE, 'host': {'system': 'Darwin', 'architectures': ['arm64', 'aarch64']},
            'scope': 'Conversion runtime, generic templates, schemas, provenance and licenses',
            'excluded_scope': ['development tests/fixtures/results', 'project evidence and local caches',
                               'other-platform binaries', 'maintainer evaluation and release QA',
                               'deferred device/visual execution skills and roles'],
            'deferred_skills': sorted(DEFERRED_SKILLS), 'deferred_roles': sorted(DEFERRED_ROLES),
            'deferred_source_aliases': sorted(DEFERRED_SOURCE_ALIASES),
            'authority': 'Tool distribution policy; no Apple semantic analysis claim'}


def exclusion(relative, *, directory=False):
    path = PurePosixPath(relative)
    parts = path.parts
    if not parts:
        return None
    if path.is_absolute() or '..' in parts or '\\' in str(relative) or ':' in str(relative):
        return 'unsafe release path'
    lower = tuple(part.casefold() for part in parts)
    folders = lower if directory else lower[:-1]
    if parts[0] in MAINTENANCE_ROOTS or parts[:3] == ('docs', 'integration', 'evidence'):
        return 'project/maintenance evidence (outside portable tool payload)'
    if LOCAL_DIRECTORIES.intersection(folders) or any(p.endswith(('.xcresult', '.xcarchive')) for p in folders):
        return 'local state/build/cache directory'
    if path.name == '.DS_Store' or path.name.startswith('._') or path.suffix in {'.pyc', '.pyo'}:
        return 'system/cache file'
    if (parts[0] not in ROOT_DIRECTORIES and
            (directory or len(parts) != 1 or parts[0] not in ROOT_FILES)):
        return 'outside declared conversion-tool release roots'
    if any(lower[i] == 'skills' and lower[i + 1] in DEFERRED_SKILLS | DEFERRED_SOURCE_ALIASES
           for i in range(len(lower) - 1)):
        return 'deferred optional device/visual skill; see docs/DEFERRED-CAPABILITIES.md'
    if ('agents-codex' in lower and path.stem in DEFERRED_ROLES):
        return 'deferred optional device/visual role; see docs/DEFERRED-CAPABILITIES.md'
    if OTHER_PLATFORM_DIRECTORIES.intersection(folders):
        return 'outside macos-arm64 release platform'
    if path.suffix.lower() in {'.exe', '.dll', '.pyd', '.ps1', '.bat', '.cmd'}:
        return 'outside macos-arm64 release platform'
    if path.name.casefold().endswith(('.windows.toml', '.windows.json')):
        return 'outside macos-arm64 release platform'
    asset = re.fullmatch(r'a2h-(darwin|windows|linux)-(amd64|arm64)(?:\.exe)?', path.name)
    if asset and asset.groups() != ('darwin', 'arm64'):
        return 'outside macos-arm64 release platform'
    # Target-project test stubs are part of a generic scaffold, unlike the
    # tool developer's tests and fixtures. Preserve their complete layout.
    template_at = next((i for i, part in enumerate(folders) if part in {'template', 'templates'}), None)
    test_at = next((i for i, part in enumerate(folders) if part in TEST_DIRECTORIES or
                    part.startswith(('test_', 'fixtures_', 'fixtures-'))), None)
    template = template_at is not None and (test_at is None or template_at < test_at)
    if not template:
        if (TEST_DIRECTORIES.intersection(folders) or
                any(p.startswith(('fixtures_', 'fixtures-')) for p in folders) or
                any(p.startswith('test_') for p in folders) or
                path.name.startswith('test_') or path.name.endswith(('_test.py', '.test.ts', '.spec.ts'))):
            return 'development tests/fixtures/results (outside conversion runtime)'
        if ('assets', 'examples') in tuple(zip(lower, lower[1:])) or path.name == 'default_test_image.jpg':
            return 'sample project scenarios/data (developer-owned inputs required)'
        if path.suffix.lower() in ARCHIVE_SUFFIXES | {'.log', '.har', '.trace', '.dormant', '.bak', '.orig'}:
            return 'archive/log/retired material (outside conversion runtime)'
    if path.as_posix() in DEVELOPMENT_FILES:
        return 'maintainer QA/evaluation resource (outside conversion runtime)'
    return None
