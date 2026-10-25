"""Compatibility traversal reconstructed from native observable behavior.

This is not represented as recovered upstream source; native oracle tests cover its contract.
"""
import os
from pathlib import Path


def walk_files(root, suffix, skip_parts=None):
    skip = {'.git', '.hvigor', '.idea'}
    skip.update(skip_parts or ())
    files = []
    for directory, names, entries in os.walk(root):
        names[:] = [name for name in names if name not in skip]
        for name in entries:
            if name.endswith(suffix):
                files.append(Path(directory) / name)
    return files
