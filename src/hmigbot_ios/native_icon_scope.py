"""Read-only original image detection over configured production ArkTS sources.

The bundled detector rewrites backslashes before opening files, so even an
extended Windows root cannot address a long child safely. A short temporary
input view keeps source bytes separately hashed and applies whitespace-only
Image-chain formatting; every detector location maps to its production line.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from dataclasses import dataclass

from .core import io_path, write_json
from .native_structural_evidence import product_source_roots, SKIP, TEST_PARTS
from .behavior import _target_tokens, _target_pairs


@dataclass(frozen=True)
class _OffsetToken:
    value: str
    line: int
    literal: bool
    start: int
    end: int


def _offset_tokens(text):
    """The shared ArkTS boundary lexer's rules, retaining source offsets.

    Every result is checked against the existing lexer before any formatting;
    opaque literals/comments and balanced scopes keep their original meaning.
    """
    def comment_end(pos):
        if text.startswith('//', pos):
            end = text.find('\n', pos + 2)
            return len(text) if end < 0 else end
        end = text.find('*/', pos + 2)
        return len(text) if end < 0 else end + 2

    def quoted_end(pos):
        quote, pos = text[pos], pos + 1
        while pos < len(text):
            if text[pos] == '\\':
                pos += 2
            elif text[pos] == quote:
                return pos + 1
            elif quote == '`' and text.startswith('${', pos):
                pos = interpolation_end(pos + 2)
            else:
                pos += 1
        return pos

    def regexp_end(pos):
        pos, in_class = pos + 1, False
        while pos < len(text) and text[pos] not in '\r\n':
            char = text[pos]
            if char == '\\':
                pos += 2
                continue
            if char == '[':
                in_class = True
            elif char == ']':
                in_class = False
            elif char == '/' and not in_class:
                pos += 1
                while pos < len(text) and text[pos].isalpha():
                    pos += 1
                return pos
            pos += 1
        return None

    def interpolation_end(pos):
        depth = 1
        while pos < len(text):
            if text.startswith(('//', '/*'), pos):
                pos = comment_end(pos)
            elif text[pos] in '\'"`':
                pos = quoted_end(pos)
            elif text[pos] == '/' and (end := regexp_end(pos)) is not None:
                pos = end
            else:
                depth += text[pos] == '{'
                depth -= text[pos] == '}'
                pos += 1
                if not depth:
                    return pos
        return pos

    result, pos, line = [], 0, 1
    expression_prefix = {'=', '(', '[', '{', ',', ':', ';', '=>', 'return', 'throw',
                         'case', '?', '!', '&', '|', '+', '-', '*', '%', '~'}
    word = re.compile(r'[$\w]+|=>')
    while pos < len(text):
        start, start_line = pos, line
        char = text[pos]
        if char.isspace():
            line += char == '\n'
            pos += 1
            continue
        literal = False
        if text.startswith(('//', '/*'), pos):
            pos = comment_end(pos)
            line += text[start:pos].count('\n')
            continue
        if char in '\'"`':
            pos, value, literal = quoted_end(pos), '<literal>', True
        elif char == '/' and (not result or result[-1].value in expression_prefix) and (end := regexp_end(pos)) is not None:
            pos, value, literal = end, '<literal>', True
        else:
            match = word.match(text, pos)
            value = match.group() if match else char
            pos += len(value)
        result.append(_OffsetToken(value, start_line, literal, start, pos))
        line += text[start:pos].count('\n')
    shared = _target_tokens(text)
    if [(t.value, t.line, t.literal) for t in result] != [(t.value, t.line, t.literal) for t in shared]:
        raise ValueError('Image projection lexical boundaries differ from the shared ArkTS lexer')
    return result


def projection_text(raw):
    """Insert whitespace only at actual Image fluent-chain token boundaries."""
    text = raw.decode('utf-8')
    if 'Image' not in text:
        return raw, list(range(1, text.count('\n') + 2)), 0
    tokens = _offset_tokens(text)
    pairs = _target_pairs(tokens)
    insertions = {}
    def linebreak(position, indentation):
        prefix = text[text.rfind('\n', 0, position) + 1:position]
        if prefix.strip():
            insertions[position] = '\n' + indentation
        elif len(prefix) < len(indentation):
            insertions[position] = ' ' * (len(indentation) - len(prefix))
    for index, token in enumerate(tokens[:-1]):
        if token.literal or token.value != 'Image':
            continue
        if index and tokens[index - 1].value in {'.', '?'}:
            continue
        if tokens[index + 1].value == '?':
            raise ValueError('Optional Image constructor cannot be normalized safely')
        if tokens[index + 1].value != '(':
            continue
        if index + 1 not in pairs:
            raise ValueError('Image constructor has unbalanced lexical scope')
        original_prefix = text[text.rfind('\n', 0, token.start) + 1:token.start]
        indentation = re.match(r'[ \t]*', original_prefix).group()
        if not index or tokens[index - 1].value not in {'return', 'throw', 'yield'}:
            linebreak(token.start, indentation)
        close = pairs[index + 1]
        cursor = close + 1
        while (cursor + 2 < len(tokens) and tokens[cursor].value == '.'
               and re.fullmatch(r'[$\w]+', tokens[cursor + 1].value)
               and tokens[cursor + 2].value == '(' and cursor + 2 in pairs):
            linebreak(tokens[cursor].start, indentation + '  ')
            end = pairs[cursor + 2]
            # A callback's component widths belong to that callback, not to
            # the Image receiving onClick/etc. Put its body on a separate line.
            for inner in range(cursor + 3, end):
                if tokens[inner].value == '=>':
                    body = inner + 1
                    if body < end:
                        linebreak(tokens[body].end if tokens[body].value == '{' else tokens[body].start,
                                  indentation + '    ')
            close, cursor = end, end + 1
        if close + 1 < len(tokens):
            linebreak(tokens[close].end, indentation)
    pieces, line_map, original_line, added = [], [1], 1, 0
    for position, char in enumerate(text):
        if position in insertions:
            whitespace = insertions[position]
            pieces.append(whitespace)
            line_map.extend([original_line] * whitespace.count('\n'))
            added += whitespace.count('\n')
        pieces.append(char)
        if char == '\n':
            original_line += 1
            line_map.append(original_line)
    projected = ''.join(pieces)
    # Token values and full literal contents stay identical; only newlines
    # were inserted, and each detector line has an explicit original mapping.
    after_tokens = _offset_tokens(projected)
    signature = lambda source, items: [(t.value, source[t.start:t.end] if t.literal else None) for t in items]
    if signature(text, tokens) != signature(projected, after_tokens):
        raise ValueError('Image projection changed source tokens or literal contents')
    return projected.encode('utf-8'), line_map, added


def product_sources(project):
    project = io_path(project).resolve()
    roots = product_source_roots(project)
    sources = {}
    for root in roots:
        for parent, directories, names in os.walk(io_path(root)):
            directories[:] = sorted(name for name in directories
                if name not in SKIP | TEST_PARTS and not name.startswith('.'))
            for name in sorted(names):
                if not name.endswith('.ets'):
                    continue
                path = io_path(Path(parent) / name).resolve()
                if not path.is_relative_to(root):
                    raise ValueError('Product source escapes configured root: ' + str(path))
                relative = path.relative_to(project).as_posix()
                if relative in sources:
                    raise ValueError('Configured source roots overlap: ' + relative)
                sources[relative] = path
    return project, roots, sources


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _check_direct_image_constraints(text, flagged_lines, relative, line_map):
    """A regex must not borrow callback, string, or another component's size.

    This only rejects an inconsistent passing detector result. It never clears
    a finding, invents dimensions, or promotes an unsupported construct to PASS.
    """
    tokens = _offset_tokens(text)
    pairs = _target_pairs(tokens)
    for index, token in enumerate(tokens[:-1]):
        if token.literal or token.value != 'Image' or tokens[index + 1].value != '(':
            continue
        if index and tokens[index - 1].value in {'.', '?'}:
            continue
        if index + 1 not in pairs:
            raise ValueError('Unbalanced Image in projected constraints')
        cursor = pairs[index + 1] + 1
        modifiers = set()
        while (cursor + 2 < len(tokens) and tokens[cursor].value == '.'
               and re.fullmatch(r'[$\w]+', tokens[cursor + 1].value)
               and tokens[cursor + 2].value == '(' and cursor + 2 in pairs):
            modifiers.add(tokens[cursor + 1].value)
            cursor = pairs[cursor + 2] + 1
        dimensions = {'width', 'height'} & modifiers
        incomplete = ('size' not in modifiers and len(dimensions) < 2
                      and not (dimensions and 'aspectRatio' in modifiers))
        if incomplete and token.line not in flagged_lines:
            original_line = line_map[token.line - 1]
            raise ValueError('Original image detector borrowed dimensions outside the Image direct chain: '
                             + relative + ':' + str(original_line))


def audit(project, output, original):
    project, roots, sources = product_sources(project)
    contents = {name: path.read_bytes() for name, path in sorted(sources.items())}
    hashes = {name: _sha(raw) for name, raw in contents.items()}
    with tempfile.TemporaryDirectory(prefix='native-icon-') as temporary:
        directory = Path(temporary)
        inputs = directory / 'inputs'
        inputs.mkdir()
        mapping, projected_bytes, projection_hashes, projection_lines = {}, {}, {}, {}
        for index, (relative, raw) in enumerate(contents.items()):
            projected = inputs / f'{index:08d}.ets'
            body, line_map, added = projection_text(raw)
            projected.write_bytes(body)
            mapping[projected.as_posix().casefold()] = (relative, line_map)
            projected_bytes[index] = body
            projection_hashes[relative] = _sha(body)
            if added:
                projection_lines[relative] = {'newlines_added': added, 'original_line_by_projected_line': line_map}
        current = directory / 'report.json'
        result = original('arkts-icon-sizing', 'icon_audit.py',
                          ['--roots', inputs, '--json', current], cwd=project)
        if result.returncode or not current.is_file():
            raise ValueError('Image constraint detector failed: ' + result.stderr[-1000:])
        data = json.loads(current.read_text(encoding='utf-8-sig'))
        if not isinstance(data, dict) or not isinstance(data.get('flagged'), list):
            raise ValueError('Unexpected image constraint report')
        # Upstream 'scanned' counts Image expressions, not ETS files. Keep
        # that field's original meaning and expose file coverage separately.
        if type(data.get('scanned')) is not int or data['scanned'] < 0:
            raise ValueError('Unexpected original Image-expression count')
        for index, body in projected_bytes.items():
            if (inputs / f'{index:08d}.ets').read_bytes() != body:
                raise ValueError('Original image detector mutated a projected source')
            projected = inputs / f'{index:08d}.ets'
            relative, line_map = mapping[projected.as_posix().casefold()]
            flagged_lines = {row.get('line') for row in data['flagged']
                             if isinstance(row, dict) and isinstance(row.get('file'), str)
                             and row['file'].replace('\\', '/').casefold() == projected.as_posix().casefold()}
            _check_direct_image_constraints(body.decode('utf-8'), flagged_lines, relative, line_map)

        def remap(value):
            if isinstance(value, list):
                return [remap(item) for item in value]
            if not isinstance(value, dict):
                return value
            binding = mapping.get(value.get('file', '').replace('\\', '/').casefold()) if isinstance(value.get('file'), str) else None
            result = {}
            for key, item in value.items():
                if key == 'file':
                    if not isinstance(item, str) or item.replace('\\', '/').casefold() not in mapping:
                        raise ValueError('Original image detector reported an unbound input path')
                    result[key] = binding[0]
                elif key == 'line' and binding:
                    if type(item) is not int or not 1 <= item <= len(binding[1]):
                        raise ValueError('Original image detector reported an unbound source line')
                    result[key] = binding[1][item - 1]
                else:
                    result[key] = remap(item)
            return result
        data = remap(data)
    # The original detector recognizes width/height/aspectRatio, whereas a
    # source-backed dynamic image may intentionally have a maximum height.
    # Retain its original finding and require the exact typed/source contract;
    # this is a read-only layout proof, never density inference or visual PASS.
    from .native_pipeline_semantics import source_bounded_image
    original_report = copy.deepcopy(data)
    remaining, dispositions = [], []
    for finding in data['flagged']:
        proof = None
        if (isinstance(finding, dict) and finding.get('kind') == 'ONE-DIM-NO-ASPECT'
                and isinstance(finding.get('file'), str) and type(finding.get('line')) is int):
            try:
                proof = source_bounded_image(project, finding['file'], finding['line'])
            except (ValueError, OSError, KeyError):
                # Unsupported/missing provenance remains an original finding.
                proof = None
        if proof is None:
            remaining.append(finding)
        else:
            dispositions.append({'original_finding': finding, **proof})
    data.update(flagged=remaining, original_report=original_report, native_dispositions=dispositions)
    after = {name: _sha(path.read_bytes()) for name, path in sources.items()}
    if hashes != after:
        raise ValueError('Production ArkTS changed during the read-only image audit')
    native = {'source_platform': 'ios', 'status': 'needs_source_dimensions' if data['flagged'] else 'passed',
        'mutated': False, 'report': data,
        'source_roots': [root.relative_to(project).as_posix() for root in roots],
        'source_file_hashes': hashes, 'source_file_count': len(contents),
        'projected_file_hashes': projection_hashes, 'projection_line_maps': projection_lines,
        'direct_chain_consistency': 'passed; an inconsistent original passing result is blocked',
        'input_projection': 'short-path files; whitespace-only Image chain formatting; original tokens/literals and source lines verified',
        'scope': 'Image constraints only; not visual equivalence or inferred point-to-vp scale'}
    write_json(io_path(output).resolve(), native)
    return native


def autofix_main(arguments=None):
    """Original pipeline icon interface, with actual native audit and zero edits.

    This shim replaces only the Android density-based mutation step for native
    iOS inputs. It cannot turn an under-constrained Image into a passing result.
    """
    from .native_helpers import icon_audit
    parser = argparse.ArgumentParser(description='Read-only native image constraints for the original pipeline')
    parser.add_argument('--project-root', type=Path, default=Path.cwd())
    parser.add_argument('--android-res', nargs='*')
    parser.add_argument('--density', type=float)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--output-json', type=Path, required=True)
    args = parser.parse_args(arguments)
    with tempfile.TemporaryDirectory(prefix='native-icon-result-') as temporary:
        native = icon_audit(args.project_root, Path(temporary) / 'audit.json')
    report = {'passed': native['status'] == 'passed', 'warnings': [],
        'scanned': native['report']['scanned'],
        'flagged_before': len(native['report']['original_report']['flagged']),
        'flagged_after': len(native['report']['flagged']), 'fixed_count': 0, 'fixed': [],
        'mutated': False, 'source_platform': 'ios', 'native_image_constraints': native,
        'dynamic_unresolved': [row for row in native['report']['flagged'] if row.get('dynamic')],
        'residual_static': [row for row in native['report']['flagged'] if not row.get('dynamic')],
        'no_raster_unresolved': [], 'fill_for_review': native['report'].get('fill', []),
        'density_source': 'not used for native iOS; source dimensions required'}
    output = args.output_json if args.output_json.is_absolute() else args.project_root / args.output_json
    write_json(output, report)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report['passed'] else 1
