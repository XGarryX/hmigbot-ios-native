"""Archive only recognized machine outputs before replacing an owned tool install.

Authored contracts, source provenance, raw evidence and migration control ledgers
are never cleanup candidates. This is an installation transaction, not progress.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import shutil
import stat
import time
import uuid

from .core import MigrationError, digest, io_path, json_bytes, read_json

MD_OUTPUTS = {
    'spec/ui-coverage-report.md', 'spec/migration-report.md', 'spec/verify-report.md',
    'spec/reports/derived/ui-plan.md', 'spec/reports/derived/feature-plan.md'}
JSON_OUTPUTS = {
    'spec/baseline/ios-facts.json', 'spec/baseline/ios-obligations.json',
    'spec/baseline/literal-ledger.json', 'spec/baseline/ios-source-check.json',
    'spec/reports/ios-harness-check.json', 'spec/reports/spec-check.json',
    'spec/reports/spec-summary.json', 'spec/reports/product-literals.json',
    *('spec/ref/ios-' + scope + '-signals.json' for scope in ('project','ui','feature','api'))}
MARKERS = ('<!-- hmigbot-derived-gate:1 -->', '<!-- hmigbot-derived-report:2 -->')
PROTECTED = ('spec/baseline/ios-source-index.json', 'spec/baseline/ios-semantics.json',
             'spec/baseline/ios-coverage.json', 'spec/baseline/ios-responsibility.json',
             'spec/baseline/verification.json', 'spec/baseline/impl-claims.json',
             'spec/decision-ledger.md', 'spec/.a2h/', 'spec/state/', 'spec/blueprint/',
             'spec/waves/', 'authored Spec/AC/plans', 'raw evidence', 'application/source files')


def _safe(project, relative):
    parts = Path(relative)
    if parts.is_absolute() or '..' in parts.parts or not parts.parts or ':' in str(relative) or chr(92) in str(relative):
        raise MigrationError('Invalid upgrade cleanup path')
    cursor = project
    for part in parts.parts:
        cursor = cursor / part
        if cursor.is_symlink() or (hasattr(cursor, 'is_junction') and cursor.is_junction()):
            raise MigrationError('Upgrade cleanup refuses linked paths: ' + str(relative))
    path = io_path(project / parts)
    if not path.resolve().is_relative_to(project) or path == project:
        raise MigrationError('Upgrade cleanup escapes the current project')
    return path


def _recognized(relative, raw):
    if relative in MD_OUTPUTS:
        try:
            return any(marker in raw.decode('utf-8-sig').splitlines()[:8] for marker in MARKERS)
        except UnicodeError:
            return False
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeError):
        return False
    if not isinstance(data, dict):
        return False
    sha = isinstance(data.get('source_sha256'), str) and bool(re.fullmatch('[0-9a-f]{64}', data['source_sha256']))
    name = Path(relative).name
    if name == 'ios-facts.json':
        return data.get('schema_version') == 2 and sha and data.get('source_platform') == 'ios' and isinstance(data.get('facts'), list) and isinstance(data.get('variant'), dict)
    if name == 'ios-obligations.json':
        return data.get('schema_version') == 2 and sha and isinstance(data.get('obligations'), list)
    if name == 'literal-ledger.json':
        return data.get('schema_version') == 2 and sha and data.get('source_platform') == 'ios' and all(isinstance(data.get(k), list) for k in ('texts','colors','dims','durations_ms','dynamic_texts','numeric_constants','symbolic_colors'))
    if name == 'ios-source-check.json':
        return data.get('source_platform') == 'ios' and data.get('status') in ('PASS','FAIL') and isinstance(data.get('findings'), list) and isinstance(data.get('checks'), str) and data.get('behavior_verified') is False
    if name == 'ios-harness-check.json':
        return data.get('schema_version') == 2 and data.get('status') in ('PASS','FAIL') and isinstance(data.get('findings'), list) and isinstance(data.get('checks'), dict) and data.get('behavior_verified') is False
    if name == 'spec-check.json':
        return data.get('schema_version') == 1 and data.get('status') in ('PASS','FAIL') and isinstance(data.get('findings'), list) and isinstance(data.get('inputs'), dict) and data.get('behavior_verified') is False
    if name == 'spec-summary.json':
        return data.get('schema_version') == 2 and sha and isinstance(data.get('axes'), dict) and isinstance(data.get('counts'), dict) and type(data.get('behavior_verified')) is bool
    if name == 'product-literals.json':
        return data.get('schema_version') == 1 and sha and isinstance(data.get('entries'), list) and data.get('behavior_verified') is False
    if name.endswith('-signals.json'):
        return data.get('schema_version') == 2 and sha and data.get('scope') in ('project','ui','feature','api') and isinstance(data.get('facts'), list) and isinstance(data.get('obligations'), list)
    return False


def frozen_plan_inputs(project):
    """Preserve exact machine inputs still referenced by the original frozen run.

    Keeping bytes available does not revalidate their semantics or grant a PASS.
    The original kernel computes contract identity; no second state writer exists.
    """
    plans = [_safe(project, p.relative_to(project).as_posix())
             for p in (project / 'spec/waves').glob('plan-*.json')]
    typed = []
    for path in plans:
        value = read_json(path)
        if isinstance(value, dict) and value.get('ios_adapter_version') == 2:
            typed.append(value)
    if not typed:
        return {}
    contract = read_json(_safe(project, 'spec/blueprint/contracts.json'))
    from .ios_scheduler import kernel
    expected = kernel().compute_contract_hash(project / 'spec/blueprint', [])
    matching = [p for p in typed if p.get('contract_hash') == expected]
    if (not matching or any(digest(json_bytes({k: v for k, v in p.items() if k != 'contract_hash'}))
                           != contract.get('plan_identity_sha256') for p in matching)
            or not isinstance(contract.get('input_hashes'), dict)):
        raise MigrationError('Frozen plan identity is inconsistent; preserve it before upgrading')
    return contract['input_hashes']


class UpgradeCleanup:
    def __init__(self, project, old, new, tool_changed):
        self.project = io_path(Path(project).resolve(strict=True))
        if not self.project.is_dir() or self.project == Path(self.project.anchor) or self.project == Path.home().resolve():
            raise MigrationError('Upgrade cleanup requires one explicit project directory')
        self._removed = []
        self._archived = []
        self._receipt = {'schema_version': 1, 'kind': 'tool_upgrade_cleanup', 'status': 'prepared',
            'project': str(self.project), 'from_version': old, 'to_version': new,
            'enabled': bool(old and tool_changed), 'files': [], 'preserved': [],
            'protected': list(PROTECTED), 'archive': None, 'product_verified': False,
            'rebuild_required': ['facts (with original reviewed variant/providers)', 'literals',
                                 'facts-view', 'gate-artifacts', 'spec-check', 'source-check --harness']}
        if not self._receipt['enabled']:
            self._receipt['status'] = 'not_needed'
            return
        dispatch_path = self.project / 'spec/state/dispatch.json'
        if dispatch_path.is_file():
            from .core import read_json
            from .ios_scheduler import kernel
            dispatch = read_json(dispatch_path)
            journal_path = self.project / 'spec/state/journal.json'
            journal = read_json(journal_path) if journal_path.is_file() else {}
            for wave, row in dispatch.get('waves', {}).items():
                landed, _ = kernel().journal_indexes(journal, wave)
                if any(record.get('attempts', 0) > landed.get(ident, 0)
                       for ident, record in row.get('dispatched', {}).items()):
                    raise MigrationError('In-flight tasks must land or be explicitly terminated before tool upgrade')
        pinned = frozen_plan_inputs(self.project)
        for relative in sorted(MD_OUTPUTS | JSON_OUTPUTS):
            path = _safe(self.project, relative)
            if not path.exists():
                continue
            if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
                raise MigrationError('Upgrade cleanup candidate must be a regular file: ' + relative)
            raw = path.read_bytes()
            if relative in pinned:
                self._receipt['preserved'].append({'path': relative,
                    'reason': 'Frozen plan input retained; current consumers must revalidate it',
                    'expected_sha256': pinned[relative], 'current_sha256': digest(raw)})
                continue
            if not _recognized(relative, raw):
                self._receipt['preserved'].append({'path': relative, 'reason': 'Unrecognized content; filename alone cannot authorize cleanup'})
                continue
            self._receipt['files'].append({'path': relative, 'sha256': digest(raw), 'size':len(raw),
                                          'mode': stat.S_IMODE(path.stat().st_mode)})
        # Validate the archive parent now, before any mutation.
        _safe(self.project, '.hmigbot-ios/upgrade-history')

    @property
    def receipt(self):
        return copy.deepcopy(self._receipt)

    def _record(self):
        if self._receipt['archive']:
            path = _safe(self.project, self._receipt['archive'] + '/cleanup.json')
            path.write_text(json.dumps(self._receipt, ensure_ascii=False, indent=2) + chr(10), encoding='utf-8')

    def _check(self, row):
        path = _safe(self.project, row['path'])
        if not path.is_file() or digest(path.read_bytes()) != row['sha256'] or stat.S_IMODE(path.stat().st_mode) != row['mode']:
            raise MigrationError('Upgrade cleanup input changed: ' + row['path'])
        return path

    def apply(self):
        if not self._receipt['enabled']:
            return self.receipt
        if self._receipt['status'] != 'prepared':
            raise MigrationError('Upgrade cleanup transaction already applied')
        for row in self._receipt['files']:
            self._check(row)
        relative = '.hmigbot-ios/upgrade-history/' + time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:12]
        archive = _safe(self.project, relative)
        archive.mkdir(parents=True, exist_ok=False)
        self._receipt['archive'] = relative
        self._receipt['status'] = 'archiving'
        try:
            # Archive every candidate before removing any original.
            for row in self._receipt['files']:
                source = self._check(row)
                backup = _safe(self.project, relative + '/generated/' + row['path'])
                backup.parent.mkdir(parents=True, exist_ok=True)
                _safe(self.project, relative + '/generated/' + row['path'])
                shutil.copy2(source, backup)
                if digest(backup.read_bytes()) != row['sha256']:
                    raise MigrationError('Upgrade cleanup archive verification failed')
                self._archived.append(row['path'])
            self._record()
            for row in self._receipt['files']:
                source = self._check(row)
                source.unlink()
                self._removed.append(row['path'])
            self._receipt['status'] = 'applied'
            self._record()
        except Exception:
            self.rollback()
            raise
        return self.receipt

    def commit(self):
        if not self._receipt['enabled']:
            return self.receipt
        if self._receipt['status'] != 'applied':
            raise MigrationError('Upgrade cleanup cannot commit before apply')
        if any(_safe(self.project, p).exists() for p in self._removed):
            raise MigrationError('Upgrade cleanup output changed during install')
        self._receipt['status'] = 'committed'
        self._record()
        return self.receipt

    def rollback(self):
        if not self._receipt['enabled'] or not self._receipt['archive']:
            return self.receipt
        rows = {r['path']:r for r in self._receipt['files']}
        failures = []
        for relative in reversed(self._removed):
            row = rows[relative]
            try:
                target = _safe(self.project, relative)
                if target.exists():
                    if digest(target.read_bytes()) == row['sha256']:
                        continue
                    raise MigrationError('Cleanup rollback refuses a concurrent edit: ' + relative)
                backup = _safe(self.project, self._receipt['archive'] + '/generated/' + relative)
                if digest(backup.read_bytes()) != row['sha256']:
                    raise MigrationError('Cleanup rollback archive is stale: ' + relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup, target)
            except (MigrationError, OSError) as exc:
                failures.append({'path': relative, 'error': str(exc)})
        self._receipt['status'] = 'rollback_blocked' if failures else 'rolled_back'
        if failures:
            self._receipt['rollback_failures'] = failures
        self._record()
        if failures:
            raise MigrationError('; '.join(f['error'] for f in failures))
        return self.receipt


def prepare_upgrade_cleanup(project, from_version, to_version, *, tool_changed=True):
    return UpgradeCleanup(project, from_version, to_version, tool_changed)
