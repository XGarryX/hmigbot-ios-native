"""Run the original lint rules with a linear equivalent declaration matcher.

The frozen scheduler remains the only state writer. Its Windows helper calls
this CLI in a disposable skill directory; neither vendor sources nor products
are rewritten to accommodate the original regular expression's backtracking.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

_DECL_HEAD = re.compile(r'^\s*(?:export\s+)?(?:const|let|var)\s+([\w$]+)')


class _DeclarationMatch:
    def __init__(self, text, prefix, rhs):
        self.text, self.prefix, self.rhs = text, prefix, rhs

    def group(self, *indices):
        indices = indices or (0,)
        values = (self.text, self.prefix.group(1), self.rhs)
        result = tuple(values[index] for index in indices)
        return result[0] if len(result) == 1 else result

    def groups(self, default=None):
        return self.group(1, 2)


class LinearTopDeclaration:
    """Preserve the original two captures without rescanning a whitespace tail.

The original matcher is applied to code.split('\\n') lines. A quote containing
16 KiB of spaces (string contents erased by strip_code) makes its adjacent
lazy RHS and whitespace repetitions effectively cubic. Prefix matching is
unchanged; slicing its tail preserves the original minimal nonempty RHS.
"""
    def match(self, text):
        equals = text.find('=')
        if equals < 0:
            return None
        left = text[:equals]
        prefix = _DECL_HEAD.match(left)
        if prefix is None:
            return None
        suffix = left[prefix.end():].lstrip()
        if suffix and (not suffix.startswith(':') or len(suffix) < 2):
            return None
        rest = text[equals + 1:].lstrip()
        if not rest:
            # Original '=\\s*(.+?)...' backtracks to the last whitespace
            # character that '.' can consume; '\\n' itself is excluded.
            tail = text[equals + 1:]
            rest = next((char for char in reversed(tail) if char != '\n'), '')
            if not rest:
                return None
        rhs = rest.rstrip()
        if '\n' in rhs:
            return None
        if rhs.endswith(';'):
            without_semicolon = rhs[:-1].rstrip()
            if without_semicolon:
                rhs = without_semicolon
        if not rhs:
            rhs = rest[:1]
        return _DeclarationMatch(text, prefix, rhs)


def original_runtime(scripts):
    path = Path(scripts) / '_static_runtime.py'
    spec = importlib.util.spec_from_file_location('hmigbot_original_static_runtime', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module._TOP_DECL_RE = LinearTopDeclaration()
    return module


def main(scripts, argv=None):
    parser = argparse.ArgumentParser(description='Original runtime lint with bounded declaration matching')
    parser.add_argument('--project', required=True)
    parser.add_argument('--module', default='entry')
    parser.add_argument('--files')
    parser.add_argument('--out')
    parser.add_argument('--fix', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    runtime = original_runtime(scripts)
    result = runtime.run_lint(args.project, module=args.module,
                              files=args.files.split(',') if args.files is not None else None, fix=args.fix)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        output = Path(args.out)
        if not output.is_absolute():
            output = Path(args.project) / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding='utf-8')
    if args.json:
        sys.stdout.write(rendered)
    else:
        print(f'Runtime lint: {result["scanned"]} files, {len(result["findings"])} findings')
    return 0 if result['ok'] else 1
