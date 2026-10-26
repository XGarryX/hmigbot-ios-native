"""Project-contained macOS quarantine repair, without changing system policy.

The explicit current conversion project is the mutation boundary. An external
tool checkout or a temporary runtime is never an alternative repair boundary.
Returned receipts describe tool preparation only, never product verification.
"""
from __future__ import annotations

import os
import ctypes
import errno
from pathlib import Path
import platform
import stat
import subprocess

from .core import MigrationError, read_json

ATTRIBUTE = 'com.apple.quarantine'


class PermissionRepairError(MigrationError):
    """A failed attempt retains its actual subprocess evidence for the caller."""
    def __init__(self, message, receipt):
        super().__init__(message)
        self.receipt = receipt


def _root(project_root):
    if project_root is None:
        raise MigrationError('Quarantine repair requires the explicit current conversion project root')
    root = Path(project_root).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise MigrationError('Quarantine repair project root must be a directory')
    if root == Path(root.anchor) or root == Path.home().resolve():
        raise MigrationError('Filesystem root and the user home cannot be quarantine repair project roots')
    return root


def _inside(root, path):
    if not path.is_relative_to(root):
        raise MigrationError('Refusing quarantine repair outside the current conversion project: ' + str(path))


def _target(root, target):
    path = Path(target).expanduser()
    path = path if path.is_absolute() else root / path
    resolved = path.resolve(strict=True)
    _inside(root, resolved)
    return resolved


def _tree(root, target):
    """Check every descendant and all followed in-project symlink destinations.

    Internal links are allowed. Every link destination must stay in the project;
    directory identities prevent cycles from making the preflight unbounded.
    """
    pending, visited, entries = [target], set(), {}
    while pending:
        path = pending.pop()
        _inside(root, path)
        info = path.lstat()
        identity = (info.st_dev, info.st_ino, info.st_mode, info.st_ctime_ns)
        entries[path] = identity
        if stat.S_ISLNK(info.st_mode):
            destination = path.resolve(strict=True)
            _inside(root, destination)
            pending.append(destination)
        elif stat.S_ISDIR(info.st_mode):
            directory = (info.st_dev, info.st_ino)
            if directory not in visited:
                visited.add(directory)
                pending.extend(path.iterdir())
        elif not stat.S_ISREG(info.st_mode):
            raise MigrationError('Unsupported special file in quarantine repair tree: ' + str(path))
        elif info.st_nlink > 1:
            raise MigrationError('Hard-linked files cannot authorize project-contained quarantine repair: ' + str(path))
    return entries


def _quarantined(entries):
    return sorted(str(path) for path in entries
                  if ATTRIBUTE in _list_attributes(path))


def _list_attributes(path):
    """Darwin Python may omit os.listxattr; read names through libSystem then.

    This is a read-only probe with XATTR_NOFOLLOW. Removal still uses the one
    audited xattr subprocess below, never a silent native mutation fallback.
    """
    if hasattr(os, 'listxattr'):
        return os.listxattr(path, follow_symlinks=False)
    libc = ctypes.CDLL(None, use_errno=True)
    function = libc.listxattr
    function.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
    function.restype = ctypes.c_ssize_t
    encoded = os.fsencode(path)
    for _ in range(3):
        size = function(encoded, None, 0, 0x0001)  # Darwin XATTR_NOFOLLOW
        if size < 0:
            code = ctypes.get_errno()
            raise OSError(code, os.strerror(code), str(path))
        if not size:
            return []
        buffer = ctypes.create_string_buffer(size)
        count = function(encoded, buffer, size, 0x0001)
        if count >= 0:
            return [v.decode('utf-8', errors='replace') for v in buffer.raw[:count].split(b'\0') if v]
        code = ctypes.get_errno()
        if code != errno.ERANGE:
            raise OSError(code, os.strerror(code), str(path))
    raise MigrationError('Attribute names changed repeatedly during read-only quarantine probe')


def discover_project_root(arguments=(), *, cwd=None):
    """Use only an explicit project argument or a marked current directory."""
    values = list(map(str, arguments))
    chosen = None
    for index, value in enumerate(values):
        if value == '--project-root' and index + 1 < len(values):
            chosen = Path(values[index + 1]); break
        if value.startswith('--project-root='):
            chosen = Path(value.partition('=')[2]); break
    try:
        working = (Path(cwd) if cwd is not None else Path.cwd()).expanduser().resolve(strict=True)
        candidate = chosen if chosen is not None else working
        candidate = candidate if candidate.is_absolute() else working / candidate
        root = _root(candidate)
        for relative, kind in [('.migbot/config.json', 'config'), ('.hmigbot-ios/install.json', 'install')]:
            path = root / relative
            if not path.is_file() or not path.resolve().is_relative_to(root):
                continue
            try:
                data = read_json(path)
            except MigrationError:
                continue
            if not isinstance(data, dict):
                continue
            if (kind == 'config' and data.get('source_platform') == 'ios'
                    and isinstance(data.get('ios'), str) and data['ios'].strip()):
                return root
            if (kind == 'install' and data.get('owner') == 'hmigbot-ios'
                    and data.get('schema_version') == 1 and isinstance(data.get('files'), dict)):
                return root
    except (OSError, RuntimeError, MigrationError):
        pass
    return None


def ensure_runtime_permissions(project_root, target):
    """Remove this one attribute only when observed inside the explicit project.

    All paths are checked before any xattr mutation; the full tree is rechecked
    immediately before invocation. No signing, chmod, Gatekeeper or system-policy
    changes are attempted. Callers may persist the returned receipt themselves.
    """
    receipt = {'schema_version': 1, 'kind': 'tool_runtime_quarantine',
               'status': 'checking', 'platform': platform.system(),
               'project_root': str(project_root), 'target': str(target),
               'mutated': False, 'mutation_attempted': False,
               'product_verified': False, 'command': None}
    try:
        root = _root(project_root)
        path = _target(root, target)
        receipt.update(project_root=str(root), target=str(path))
        entries = _tree(root, path)
        receipt['scanned_paths'] = len(entries)
        if receipt['platform'] != 'Darwin':
            receipt['status'] = 'not_applicable'
            return receipt
        quarantined = _quarantined(entries)
        receipt['quarantined_paths'] = quarantined
        if not quarantined:
            receipt['status'] = 'not_needed'
            return receipt
        if _tree(root, path) != entries:
            raise MigrationError('Quarantine repair tree changed during preflight; retry with a stable project tree')
        command = ['xattr', '-dr', ATTRIBUTE, str(path)]
        receipt.update(command=command, mutation_attempted=True, mutated=None)
        result = subprocess.run(command, shell=False, capture_output=True, text=True,
                                check=False, timeout=120)
        receipt.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
        if result.returncode:
            raise MigrationError('xattr quarantine repair failed with exit ' + str(result.returncode))
        # Do not report success merely because xattr returned zero.
        remaining = _quarantined(_tree(root, path))
        receipt['remaining_quarantined_paths'] = remaining
        if remaining:
            raise MigrationError('xattr returned success but quarantine attributes remain')
        receipt.update(status='cleared', mutated=True)
        return receipt
    except (MigrationError, OSError, ValueError, RuntimeError, AttributeError, subprocess.SubprocessError) as exc:
        receipt.update(status='failed', error=str(exc))
        if isinstance(exc, subprocess.TimeoutExpired):
            output = lambda value: value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value
            receipt.update(stdout=output(exc.stdout), stderr=output(exc.stderr), timed_out=True)
        raise PermissionRepairError(str(exc), receipt) from exc


def clear_quarantine(project_root, target):
    """Explicit repair entry point with the same contained, on-demand contract."""
    return ensure_runtime_permissions(project_root, target)


def maybe_prepare_runtime(project_root, target, *, source_path=None):
    """A tool may execute an external runtime but must never repair it.

    A lexical in-project path that escapes through a symlink still goes through
    the strict validator and is refused; it cannot be relabeled external.
    """
    if project_root is None:
        return {'schema_version': 1, 'kind': 'tool_runtime_quarantine',
                'status': 'not_requested', 'target': str(target),
                'mutated': False, 'product_verified': False, 'command': None}
    root = _root(project_root)
    lexical_root = Path(os.path.abspath(Path(project_root).expanduser()))
    if source_path is not None:
        original = Path(source_path).expanduser()
        original = Path(os.path.abspath(original if original.is_absolute() else root / original))
        if original.is_relative_to(lexical_root):
            original = root / original.relative_to(lexical_root)
        if original.is_relative_to(root):
            # A symlinked helper inside the project cannot hide its escaping
            # origin by first resolving into an apparently external payload.
            _target(root, original)
    path = Path(target).expanduser()
    absolute = Path(os.path.abspath(path if path.is_absolute() else root / path))
    if absolute.is_relative_to(lexical_root):
        absolute = root / absolute.relative_to(lexical_root)
    if absolute.is_relative_to(root):
        return ensure_runtime_permissions(root, absolute)
    # Resolving an external alias must not turn the alias into a repair target.
    return {'schema_version': 1, 'kind': 'tool_runtime_quarantine',
            'status': 'external_runtime', 'project_root': str(root), 'target': str(absolute),
            'mutated': False, 'product_verified': False, 'command': None}
