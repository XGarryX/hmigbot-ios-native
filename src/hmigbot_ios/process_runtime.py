"""Mac ARM64 process adapter using CPython subprocess semantics.

No Windows Job Object or interpreter bootstrap is imported on this path.
TimeoutExpired retains CPython's stdout/stderr and caller recovery policy;
this adapter does not claim descendant-tree termination beyond that contract.
"""
import subprocess

from .host import require_supported_host


def run(command, *, cwd, env, timeout):
    require_supported_host()
    return subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                          timeout=timeout, shell=False)
