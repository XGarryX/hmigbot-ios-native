"""Run unchanged macOS Nuitka payloads from an ASCII executable location.

Some shipped standalone binaries abort during Python initialization when their
own path contains non-ASCII text. Arguments and user project paths stay intact.
"""
from contextlib import contextmanager
import ast
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

from .core import MigrationError
from .macos_permissions import discover_project_root
from .init_environment import check_runtime_ready


def quarantine_free_launcher(text):
    """Remove only the shipped launcher's implicit, unbounded xattr block.

    Temporary copies keep the original command, program name and environment.
    The unchanged installed launcher and compiled engine bytes are not edited.
    Unexpected mutation code is refused rather than guessed away.
    """
    if not text.startswith('# AUTO-GENERATED launcher'):
        return text
    tree = ast.parse(text)
    matches = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if not (isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess'
                and node.func.attr == 'run' and node.args and isinstance(node.args[0], ast.List)):
            continue
        values = node.args[0].elts
        if not values or not isinstance(values[0], ast.Constant) or values[0].value != 'xattr':
            continue
        valid = (len(values) == 4 and
                 [v.value for v in values[:3] if isinstance(v, ast.Constant)] ==
                 ['xattr', '-dr', 'com.apple.quarantine'] and
                 isinstance(values[3], ast.Name) and values[3].id == '_DIST')
        def owns_call(item):
            if not isinstance(item, ast.If) or len(item.body) != 1:
                return False
            statement = item.body[0]
            if isinstance(statement, ast.Expr):
                return statement.value is node
            if not isinstance(statement, ast.Try):
                return False
            # The pinned 1.7 scheduler launcher catches OSError around this
            # same one xattr call. Remove that exact block, never other work.
            return (len(statement.body) == 1 and isinstance(statement.body[0], ast.Expr)
                    and statement.body[0].value is node and not statement.orelse
                    and not statement.finalbody and len(statement.handlers) == 1
                    and isinstance(statement.handlers[0].type, ast.Name)
                    and statement.handlers[0].type.id == 'OSError'
                    and statement.handlers[0].name is None
                    and len(statement.handlers[0].body) == 1
                    and isinstance(statement.handlers[0].body[0], ast.Pass))
        owner = next((item for item in tree.body if owns_call(item)), None)
        expected = ast.dump(ast.parse('_OS == "macos"', mode='eval').body)
        if not valid or owner is None or owner.orelse or ast.dump(owner.test) != expected:
            raise MigrationError('Unexpected quarantine operation in original launcher; refusing runtime staging')
        matches.append(owner)
    if not matches:
        return text
    if len(matches) != 1:
        raise MigrationError('Multiple quarantine operations in original launcher; refusing runtime staging')
    lines = text.splitlines(keepends=True)
    node = matches[0]
    lines[node.lineno - 1:node.end_lineno] = ['# Quarantine preparation is owned by the explicit project boundary.\n']
    return ''.join(lines)


@contextmanager
def command(helper, arguments, env=None, *, project_root=None, permission_receipts=None):
    from .host import require_supported_host
    require_supported_host()
    arguments = list(arguments)
    original_helper = Path(helper).expanduser().absolute()
    helper = original_helper.resolve()
    environment = dict(os.environ if env is None else env)
    architecture = 'arm64'
    payload = helper.parent / 'bin' / ('macos-' + architecture) / '_entry.dist'
    if not (payload / '_entry.bin').is_file():
        # Preserve the original script's actual missing-platform/error protocol.
        yield [sys.executable, str(helper), *map(str, arguments)], environment
        return
    if project_root is None:
        project_root = discover_project_root(arguments)
    if permission_receipts is not None:
        permission_receipts.append(check_runtime_ready(project_root, payload, source_path=original_helper))
    else:
        check_runtime_ready(project_root, payload, source_path=original_helper)
    environment.setdefault('ARKTS_SKILL_DIR', str(helper.parent))
    if str(helper).isascii():
        # The vendor Python launcher runs unbounded xattr before exec. Delegate
        # directly with the same original engine/program, without that side effect.
        yield [str(payload / '_entry.bin'), helper.stem, *map(str, arguments)], environment
        return
    with tempfile.TemporaryDirectory(prefix='hmigbot-helper-', dir='/private/tmp') as temporary:
        staged = Path(temporary) / '_entry.dist'
        shutil.copytree(payload, staged)
        executable = staged / '_entry.bin'
        executable.chmod(executable.stat().st_mode | 0o111)
        yield [str(executable), helper.stem, *map(str, arguments)], environment


def run(helper, arguments, **kwargs):
    arguments = list(arguments)
    environment = kwargs.pop('env', None)
    project = kwargs.pop('project_root', None)
    if project is None:
        project = discover_project_root(arguments, cwd=kwargs.get('cwd'))
    receipts = kwargs.pop('permission_receipts', [])
    with command(helper, arguments, environment, project_root=project,
                 permission_receipts=receipts) as (argv, env):
        result = subprocess.run(argv, env=env, shell=False, **kwargs)
        result.macos_permission_receipts = receipts
        return result
