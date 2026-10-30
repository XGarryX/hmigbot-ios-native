"""Garry downstream adapters on the shared portable runtime service."""
import os
from pathlib import Path
import platform

from .portable_helper import command, run


def signing(helper, arguments):
    arguments = list(arguments)
    cwd = None
    if platform.system() == 'Darwin' and len(arguments) == 1:
        project = Path(arguments[0]).expanduser().resolve()
        if project.is_dir():
            cwd, arguments = project, ['.']
    env = dict(os.environ)
    if cwd is not None:
        env['PWD'] = str(cwd)
    return run(helper, arguments, cwd=cwd, env=env).returncode


def structural_loop(helper, arguments):
    from .indexed_compile_gate import preflight
    from .core import MigrationError
    import sys
    try:
        preflight(arguments)
    except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
        print('Indexed final compilation guard: '+str(exc),file=sys.stderr)
        return 3
    from .native_image_guard import maybe_run
    import argparse
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--project-root',type=Path)
    args,_=parser.parse_known_args(arguments)
    if args.project_root and (args.project_root/'spec/execution/execution-contract.json').exists():
        with command(helper, arguments) as (argv, env):
            if Path(argv[0]).name in {'_entry.bin', '_entry.exe'}:
                result = maybe_run(argv[0], arguments, Path(helper).parent, invoke=False)
                if result not in (None,0):
                    return result
    # Input/sibling-layout adaptation is shared with the Git source contract;
    # all actual detectors and the loop runner use the selected Garry payload.
    from .native_helpers import structural_loop as native_loop
    return native_loop(arguments)
