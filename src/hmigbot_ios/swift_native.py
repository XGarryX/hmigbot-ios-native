"""Consume SwiftSyntax output, without re-parsing Swift in Python.

The adapter checks hashes/UTF-8 coordinates and maps tokens into the migration
contract. SwiftParser owns syntax, string/regex boundaries and string decoding.
"""
from dataclasses import dataclass
from bisect import bisect_right
import math
import re

from .core import MigrationError, digest, read_json, safe_child
from .swiftui import Token

_live_config = None


class SwiftEvidenceError(MigrationError):
    """A source/provider identity failure must never enable weak parsing."""


def parse_sources(files):
    """Real SwiftParser for standalone consumers without a published graph.

    Compilation and command receipts live outside the tool/project. A process
    reuses only its compiled adapter, never cached source answers. Unavailable
    toolchains raise; they do not silently select the Python Swift lexer.
    """
    import json
    from pathlib import Path
    import tempfile
    from .native_source_capture import swift_provider
    from .apple_capabilities import command
    global _live_config
    if _live_config is None:
        folder = Path(tempfile.mkdtemp(prefix='hmigbot-swift-parser-'))
        _live_config = swift_provider(folder, folder / 'provider')
    config = read_json(_live_config)
    executable = safe_child(_live_config.parent, 'swift-syntax-provider')
    if digest(executable.read_bytes()) != config['provider_binary_sha256']:
        raise SwiftEvidenceError('Live SwiftSyntax adapter changed')
    request = {'files': [{'path': path, 'sha256': digest(text.encode('utf-8')), 'source': text}
                         for path, text in files.items()]}
    # Unique evidence directory prevents concurrent/repeated invocations from
    # overwriting the actual command and original diagnostics.
    output = Path(tempfile.mkdtemp(prefix='hmigbot-swift-parse-'))
    raw = command(output, 'parse', config['command'], cwd=output,
                  input_data=json.dumps(request, ensure_ascii=False).encode('utf-8'), timeout=120)
    data = json.loads(raw)
    result = {file['path']: file for file in data['files']}
    if set(result) != set(files) or len(result) != len(data['files']):
        raise SwiftEvidenceError('SwiftSyntax live source set mismatch')
    for path, file in result.items():
        if file.get('sha256') != digest(files[path].encode('utf-8')):
            raise SwiftEvidenceError('SwiftSyntax live source hash mismatch')
        if file.get('parse_has_error') is False:
            tokens_for(file, files[path])
    return result


@dataclass(frozen=True)
class NativeToken(Token):
    decoded_value: str | None = None
    native_literal: bool = False
    decoded_number: int | float | None = None
    native_number: bool = False


def tokens_for(file, text):
    if file.get('parse_has_error') is not False:
        raise MigrationError('SwiftParser rejected source: ' + str(file.get('path')))
    items = file.get('lexical_items')
    if not isinstance(items, list):
        raise SwiftEvidenceError('SwiftSyntax lexical items are missing')
    raw = text.encode('utf-8')
    if digest(raw) != file.get('sha256'):
        raise SwiftEvidenceError('SwiftSyntax file changed')
    # Byte-to-character translation is an evidence coordinate operation, not a lexer.
    boundaries, offset = {0: 0}, 0
    for index, char in enumerate(text, 1):
        offset += len(char.encode('utf-8'))
        boundaries[offset] = index
    newlines = [m.end() for m in re.finditer(r'\r\n|\r|\n', text)]
    result, previous = [], 0
    for item in items:
        if not isinstance(item, dict):
            raise SwiftEvidenceError('Invalid SwiftSyntax lexical item')
        start, end = item.get('start_utf8'), item.get('end_utf8')
        if (type(start) is not int or type(end) is not int or start < previous or start >= end
                or start not in boundaries or end not in boundaries):
            raise SwiftEvidenceError('Invalid SwiftSyntax lexical span')
        value = raw[start:end].decode('utf-8')
        line = bisect_right(newlines, boundaries[start]) + 1
        if item.get('text') != value or type(item.get('line')) is not int or item['line'] != line:
            raise SwiftEvidenceError('SwiftSyntax lexical source/line mismatch')
        kind = item.get('kind')
        if kind not in {'string', 'regex', 'number', 'token'}:
            raise SwiftEvidenceError('Invalid SwiftSyntax lexical kind')
        decoded = item.get('decoded_value')
        if kind == 'string':
            if ('decoded_value' not in item or decoded is not None and not isinstance(decoded, str)
                    or type(item.get('hash_count')) is not int or item['hash_count'] < 0
                    or type(item.get('quote_count')) is not int or item['quote_count'] not in {1, 3}):
                raise SwiftEvidenceError('Invalid SwiftSyntax decoded literal')
        number = item.get('decoded_number')
        if kind == 'number' and ('decoded_number' not in item or number is not None
                and (type(number) not in {int, float} or type(number) is float and not math.isfinite(number))):
            raise SwiftEvidenceError('Invalid SwiftSyntax decoded number')
        # Regex contents are opaque to source-signal rules, just as string contents.
        adapted_kind = ('string' if kind in {'string', 'regex'} else item['migration_kind']
                        if 'migration_kind' in item else
                        'identifier' if re.fullmatch(r'[^\W\d]\w*|`[^`]+`', value) else 'symbol')
        if adapted_kind not in {'string', 'identifier', 'symbol'}:
            raise SwiftEvidenceError('Invalid SwiftSyntax migration token class')
        result.append(NativeToken(value, line, adapted_kind, item.get('hash_count', 0),
            item.get('quote_count', 0), bisect_right(newlines, boundaries[end]) + 1, boundaries[start], boundaries[end],
            decoded, kind == 'string', number, kind == 'number'))
        previous = end
    return result


def syntax_from_artifacts(project, source, source_sha256, artifacts):
    """Only the pinned, published provider artifact can drive facts/literals."""
    selected = None
    for ref in artifacts:
        if ref.get('operation') != 'swift-syntax':
            continue
        path = safe_child(project, ref['path'])
        if digest(path.read_bytes()) != ref['sha256']:
            raise MigrationError('Provider evidence changed')
        report = read_json(path)
        if report.get('source_sha256') != source_sha256 or report.get('operation') != 'swift-syntax':
            raise MigrationError('SwiftSyntax evidence source is stale')
        data = report.get('data', {})
        # Old explicit providers remain readable; they cannot claim replacement.
        if data.get('lexical_protocol_version') != 1:
            continue
        if selected is not None:
            raise MigrationError('Ambiguous SwiftSyntax lexical providers')
        if data.get('provider') != 'SwiftSyntax' or data.get('semantic_resolution') is not False:
            raise MigrationError('Invalid SwiftSyntax evidence class')
        selected = {}
        for file in data.get('files', []):
            relative = file.get('path')
            if not isinstance(relative, str) or not relative.endswith('.swift') or relative in selected:
                raise MigrationError('Invalid/duplicate SwiftSyntax lexical file')
            raw = safe_child(source, relative).read_bytes()
            if digest(raw) != file.get('sha256'):
                raise MigrationError('SwiftSyntax file changed')
            tokens_for(file, raw.decode('utf-8'))
            selected[relative] = file
    return selected


def project_syntax(project, source, graph=None):
    path = project / 'spec/baseline/ios-facts.json'
    if graph is None:
        if not path.is_file():
            return None
        graph = read_json(path)
    syntax = syntax_from_artifacts(project, source, graph['source_sha256'], graph.get('provider_artifacts', []))
    if syntax is None or not graph.get('conditional_evidence'):
        return syntax
    from pathlib import Path
    from .conditional_evidence import validate as validate_conditionals
    ref = graph['conditional_evidence']
    condition = validate_conditionals(source, Path(ref['path']), project=project)
    if condition['reference'] != ref:
        raise SwiftEvidenceError('Conditional source view changed')
    selected = set(condition['members'])
    unresolved = {item['path'] for item in condition.get('unknowns', [])}
    for name, file in list(syntax.items()):
        lines = set()
        for view in condition['observed'].get(name, []):
            lines.update(view['active_lines'])
        syntax[name] = {**file, 'selected_for_build': name in selected,
                        'conditional_unresolved': name in unresolved,
                        'active_lines': sorted(lines)}
        if name in selected and name not in unresolved and not condition['observed'].get(name):
            raise SwiftEvidenceError('Selected Swift file has no compiler source view: ' + name)
    return syntax


def project_conditions(project, source):
    from pathlib import Path
    from .conditional_evidence import validate as validate_conditionals
    path = project / 'spec/baseline/ios-facts.json'
    if not path.is_file():
        return None
    ref = read_json(path).get('conditional_evidence')
    if not ref:
        return None
    checked = validate_conditionals(source, Path(ref['path']), project=project)
    if checked['reference'] != ref:
        raise SwiftEvidenceError('Conditional source view changed')
    return checked


def source_tokens(source, relative, syntax=None):
    """Explicit static compatibility for hosts/evidence without SwiftSyntax."""
    from .swiftui import tokenize
    path = safe_child(source, relative)
    if path.suffix == '.swift' and syntax is not None:
        if relative not in syntax:
            raise MigrationError('SwiftSyntax lexical evidence omitted source: ' + relative)
        file = syntax[relative]
        if file.get('conditional_unresolved'):
            raise SwiftEvidenceError('Swift conditional context unresolved: ' + relative)
        if file.get('selected_for_build') is False:
            return []
        tokens = tokens_for(file, path.read_bytes().decode('utf-8'))
        if 'active_lines' in file:
            active = set(file['active_lines'])
            tokens = [token for token in tokens if token.line in active]
        return tokens
    return tokenize(path.read_text(encoding='utf-8-sig'), skip_pragma_marks=path.suffix != '.swift')
