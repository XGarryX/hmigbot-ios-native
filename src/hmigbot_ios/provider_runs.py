"""Attempt-scoped provider captures.

A capture is identified by what was asked for (operation + source snapshot + config/input
fingerprint) and each try gets its own attempt directory and run id. A failure therefore never
occupies the place a retry would need, and a published success is never rewritten in place.
Nothing here invents evidence: only an artifact.json written by the atom is treated as success.
"""
from __future__ import annotations

import re
import json
from pathlib import Path
import tempfile
from contextlib import contextmanager

from .core import MigrationError, digest, io_path, json_bytes, read_json, safe_child, write_json

RUNS_FOLDER = 'runs'
ARTIFACT_NAME = 'artifact.json'
RUN_RECORD_NAME = 'run.json'
FAILURE_NAME = 'failure.json'
ATTEMPT_PATTERN = re.compile(r'^attempt-(\d{6})-([0-9a-f]{12})$')
SUCCESS_STATUSES = {'operation_completed', 'partial'}


def _fingerprint(path) -> str | None:
    """Content digest of the exact input the provider consumes; None when there is nothing to read.

    Absent or unreadable inputs stay None instead of guessing a value: the atom will fail on its
    own, and the failure record then shows a fingerprint that cannot be mistaken for real input.
    """
    if not path:
        return None
    target = io_path(path)
    if target.is_dir():
        target = target / 'manifest.json'
    try:
        return digest(target.read_bytes())
    except OSError:
        return None


def capture_root(project) -> Path:
    return io_path(project) / 'spec/ref/provider-runs'


def identity_of(operation, source_sha256, config_sha256, input_sha256) -> str:
    return digest(json_bytes([operation, source_sha256, config_sha256, input_sha256]))[:16]


def _attempt_dirs(directory: Path):
    if not directory.is_dir():
        return []
    return sorted((p for p in directory.iterdir() if p.is_dir() and ATTEMPT_PATTERN.match(p.name)),
                  key=lambda p: p.name)


def _attempt_number(directory: Path) -> int:
    match = ATTEMPT_PATTERN.match(directory.name)
    return int(match.group(1)) if match else 0


def _run_id(directory: Path) -> str:
    match = ATTEMPT_PATTERN.match(directory.name)
    return match.group(2) if match else 'unrecorded'


class ProviderRun:
    """One provider try: fresh directory, traceable run id, no overwrite of earlier evidence."""

    def __init__(self, project, operation, source_sha256, *, config=None, input_path=None):
        from .provider_plan import consumed_inputs
        config, input_path = consumed_inputs(operation, config, input_path)
        self.project = io_path(project)
        self.operation = operation
        self.source_sha256 = source_sha256
        self._config_path = io_path(config) if config else None
        self._input_path = io_path(input_path) if input_path else None
        self._config_bytes = self._read_initial(self._config_path)
        manifest = self._input_path / 'manifest.json' if self._input_path and self._input_path.is_dir() else self._input_path
        self._input_bytes = self._read_initial(manifest)
        self.config_sha256 = digest(self._config_bytes) if self._config_bytes is not None else None
        self.input_sha256 = digest(self._input_bytes) if self._input_bytes is not None else None
        self.identity = identity_of(operation, source_sha256, self.config_sha256, self.input_sha256)
        self.identity_directory = capture_root(project) / operation / source_sha256 / RUNS_FOLDER / self.identity
        existing = _attempt_dirs(self.identity_directory)
        reservations = self.identity_directory / '.reservations'
        if reservations.is_dir():
            existing += [p for p in reservations.iterdir() if ATTEMPT_PATTERN.match(p.name)]
        existing.sort(key=lambda p: p.name)
        self.attempt = _attempt_number(existing[-1]) + 1 if existing else 1
        self.reserved = False
        self.finished = False
        self._fixed_inputs = None
        self._input_artifacts = {}
        self._paths()

    @staticmethod
    def _read_initial(path):
        if path is None:
            return None
        try:
            return path.read_bytes()
        except OSError:
            return None

    def _paths(self):
        self.run_id = digest(json_bytes([self.identity, self.attempt]))[:12]
        self.directory = self.identity_directory / ('attempt-%06d-%s' % (self.attempt, self.run_id))
        self.artifact_path = self.directory / ARTIFACT_NAME
        self.failure_path = self.directory / FAILURE_NAME

    def reserve(self):
        """Claim an ordinal atomically, outside the atom's replaceable empty output."""
        if self.reserved:
            return
        reservations = self.identity_directory / '.reservations'
        reservations.mkdir(parents=True, exist_ok=True)
        while True:
            self._paths()
            marker = reservations / self.directory.name
            try:
                # Never delete the marker: a crashed run or the atom's rmdir/rename
                # publication window must not make this ordinal available again.
                with marker.open('xb'):
                    pass
            except FileExistsError:
                self.attempt += 1
                continue
            try:
                self.directory.mkdir(exist_ok=False)
            except FileExistsError:
                self.attempt += 1
                continue
            self.reserved = True
            return

    @contextmanager
    def fixed_inputs(self):
        """Consume captured bytes, with sensitive config kept out of project artifacts.

        Providers execute unchanged argv with their existing cwd; they never resolve
        argv relative to the configuration file. Moving this private copy therefore
        does not rebase relative provider commands or arguments.
        """
        if not self.reserved:
            raise MigrationError('Provider attempt must be reserved before fixing inputs')
        temporary_root = io_path(tempfile.gettempdir())
        with tempfile.TemporaryDirectory(prefix='hmigbot-provider-inputs-', dir=temporary_root) as directory:
            private = io_path(directory)
            config, bundle = None, None
            if self._config_path is not None:
                if self._config_bytes is None:
                    raise MigrationError('Cannot read the requested provider configuration')
                config = private / 'config.json'
                config.write_bytes(self._config_bytes)
            if self._input_path is not None:
                if self._input_bytes is None or not self._input_path.is_dir():
                    raise MigrationError('Provider input must be a readable evidence bundle')
                try:
                    manifest = json.loads(self._input_bytes.decode('utf-8-sig'))
                    artifacts = manifest['artifacts']
                    if not isinstance(artifacts, dict) or not artifacts:
                        raise ValueError()
                except (ValueError, UnicodeError, KeyError, TypeError):
                    raise MigrationError('Cannot freeze an invalid provider evidence manifest') from None
                bundle = private / 'input'
                bundle.mkdir()
                (bundle / 'manifest.json').write_bytes(self._input_bytes)
                for name, expected in artifacts.items():
                    if not isinstance(name, str) or not name.startswith('artifacts/'):
                        raise MigrationError('Provider evidence paths must be under artifacts/')
                    raw = safe_child(self._input_path, name).read_bytes()
                    if digest(raw) != expected:
                        raise MigrationError('Provider evidence differs from its captured manifest')
                    destination = safe_child(bundle, name)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(raw)
                self._input_artifacts = artifacts
            self._fixed_inputs = (config, bundle)
            try:
                yield config, bundle
            finally:
                self._fixed_inputs = None

    def _verify_inputs(self):
        if self._fixed_inputs is None:
            raise MigrationError('Provider success requires the fixed input context')
        config, bundle = self._fixed_inputs
        for original, fixed, expected in ((self._config_path, config, self.config_sha256),
                                           (self._input_path / 'manifest.json' if self._input_path else None,
                                            bundle / 'manifest.json' if bundle else None, self.input_sha256)):
            if original is not None and (_fingerprint(original) != expected or _fingerprint(fixed) != expected):
                raise MigrationError('Provider inputs changed during capture; success is not published')
        for name, expected in self._input_artifacts.items():
            if (digest(safe_child(self._input_path, name).read_bytes()) != expected
                    or digest(safe_child(bundle, name).read_bytes()) != expected):
                raise MigrationError('Provider evidence changed during capture; success is not published')

    def relative(self, path: Path) -> str:
        return path.relative_to(self.project).as_posix()

    def _base_record(self, status):
        return {'schema_version': 1, 'status': status, 'operation': self.operation,
                'source_sha256': self.source_sha256, 'identity': self.identity,
                'attempt': self.attempt, 'run_id': self.run_id,
                'config_sha256': self.config_sha256, 'input_sha256': self.input_sha256}

    def publish(self, report):
        """Record success next to the artifact the atom just wrote; the artifact stays untouched."""
        if not self.reserved:
            raise MigrationError('Provider attempt has no exclusive reservation')
        if self.finished:
            raise MigrationError('Provider attempt already has a terminal record')
        self._verify_inputs()
        if not self.artifact_path.is_file():
            raise MigrationError('Provider atom reported success without publishing ' + self.relative(self.artifact_path))
        data = self.artifact_path.read_bytes()
        captured = read_json(self.artifact_path)
        if captured != report or report.get('operation') != self.operation or report.get('status') not in SUCCESS_STATUSES:
            raise MigrationError('Provider artifact does not match the completed operation')
        if report.get('source_sha256') != self.source_sha256:
            raise MigrationError('Source changed while extracting; provider success is not published')
        prior_failures = []
        for attempt in _attempt_dirs(self.identity_directory):
            failure = attempt / FAILURE_NAME
            if attempt != self.directory and failure.is_file():
                prior_failures.append({'path': failure.relative_to(self.identity_directory).as_posix(),
                                       'sha256': digest(failure.read_bytes())})
        record = {**self._base_record('succeeded'), 'artifact': ARTIFACT_NAME,
                  'artifact_sha256': digest(data), 'artifact_status': report.get('status'),
                  'atom_issue_count': len(report.get('issues') or []), 'prior_failures': prior_failures}
        write_json(self.directory / RUN_RECORD_NAME, record)
        self.finished = True
        return {'path': self.relative(self.artifact_path), 'sha256': digest(data), 'operation': self.operation,
                'run': {'identity': self.identity, 'attempt': self.attempt, 'run_id': self.run_id}}

    def fail(self, error):
        """Keep the failed try on disk so a later run can see what was already attempted."""
        if not self.reserved:
            raise MigrationError('Provider attempt has no exclusive reservation')
        if self.finished:
            raise MigrationError('Provider attempt already has a terminal record')
        record = {**self._base_record('failed'), 'error': str(error),
                  'retry': 'a new attempt is allowed; this record is retained for review'}
        diagnostics = getattr(error, 'provider_diagnostics', {})
        if isinstance(diagnostics, dict) and diagnostics:
            from .core import atomic_write
            saved = {}
            for name, raw in diagnostics.items():
                if name not in {'xcodebuild.stdout.log', 'xcodebuild.stderr.log'} or not isinstance(raw, bytes):
                    raise MigrationError('Invalid provider failure diagnostics contract')
                atomic_write(self.directory / name, raw)
                saved[name] = digest(raw)
            record['diagnostics'] = saved
        write_json(self.failure_path, record)
        write_json(self.directory / RUN_RECORD_NAME, record)
        self.finished = True
        return self.relative(self.failure_path)

    def reusable(self):
        """No automatic reuse until effective tool/implementation identity is provable.

        Source/config equality cannot establish current executable, script, SDK or
        internal implementation identity. Old successes remain immutable evidence.
        """
        return None


def retained_failures(artifact_path):
    """Failures kept for the identity that produced this artifact, oldest attempt first.

    Only the attempt-scoped layout is scanned. A legacy flat capture has no attempt siblings, so
    previously saved graphs keep validating exactly as before instead of gaining new issues.
    """
    artifact = io_path(artifact_path)
    attempt, identity_dir = artifact.parent, artifact.parent.parent
    if identity_dir.parent.name != RUNS_FOLDER or not ATTEMPT_PATTERN.match(attempt.name):
        return []
    failures = []
    record = attempt / RUN_RECORD_NAME
    saved_run = read_json(record) if record.is_file() else {}
    if 'prior_failures' in saved_run:
        # A later concurrent failure stays on disk, but must not retroactively
        # change the evidence set of an already published successful baseline.
        attempts = []
        for pinned in saved_run['prior_failures']:
            failure = safe_child(identity_dir, pinned['path'])
            if digest(failure.read_bytes()) != pinned['sha256']:
                raise MigrationError('Provider retry evidence changed after publication')
            attempts.append(failure.parent)
    else:
        attempts = _attempt_dirs(identity_dir)  # Previous attempt layouts remain readable.
    for attempt_dir in attempts:
        record = attempt_dir / FAILURE_NAME
        if not record.is_file():
            continue
        try:
            saved = read_json(record)
        except (MigrationError, OSError) as exc:
            failures.append({'attempt': _attempt_number(attempt_dir), 'run_id': _run_id(attempt_dir),
                             'error': 'unreadable failure record: ' + str(exc)})
            continue
        failures.append({'attempt': saved.get('attempt', _attempt_number(attempt_dir)),
                         'run_id': saved.get('run_id', _run_id(attempt_dir)), 'error': saved.get('error')})
    return failures
