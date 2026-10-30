"""Source-backed literals, with dynamic text and symbolic colors kept distinct."""
import json
import re
from pathlib import Path
from .core import source_snapshot
from .core import MigrationError, snapshot, digest, write_json, read_json
from .swiftui import tokenize


def extract(source, *, swift_syntax=None, conditional=None):
    snap = source_snapshot(source)
    ledger = {'schema_version': 2, 'source_platform': 'ios', 'source_sha256': snap['sha256'],
              'texts': [], 'colors': [], 'dims': [], 'durations_ms': [], 'dynamic_texts': [],
              'numeric_constants': [], 'symbolic_colors': [], 'files_scanned': 0,
              'scope': 'source token literals; not runtime values, layout conversion or complete localization'}
    for file in snap['files']:
        if Path(file['path']).suffix not in {'.swift', '.m', '.mm', '.h'}:
            continue
        if conditional is not None:
            selected = set(conditional['members']) | set(conditional.get('analysis_files', []))
            if file['path'] not in selected:
                continue
            if file['path'] in {item['path'] for item in conditional.get('unknowns', [])}:
                continue
            if file['path'].endswith('.swift') and file['path'] not in conditional['observed']:
                raise MigrationError('Selected Swift literal source has no compiler view: ' + file['path'])
        ledger['files_scanned'] += 1
        native = file['path'].endswith('.swift') and swift_syntax is not None
        if native:
            from .swift_native import tokens_for
            if file['path'] not in swift_syntax:
                raise MigrationError('SwiftSyntax lexical evidence omitted literal source')
            from .swift_native import source_tokens
            tokens = source_tokens(source, file['path'], swift_syntax)
        else:
            tokens = tokenize((source / file['path']).read_text(encoding='utf-8-sig'), skip_pragma_marks=Path(file['path']).suffix != '.swift')
        if conditional is not None and file['path'] in conditional['observed']:
            active = {line for view in conditional['observed'][file['path']] for line in view['active_lines']}
            tokens = [token for token in tokens if token.line in active]
        for i, token in enumerate(tokens):
            anchor = {'sources': [file['path'] + ':' + str(token.line)], 'file_sha256': file['sha256']}
            if conditional is not None:
                anchor['build_contexts'] = [
                    {'unit': view['unit'], 'instance': view['instance']}
                    for view in conditional['observed'].get(file['path'], [])
                    if token.line in view['active_lines']]
            if token.kind == 'string':
                raw = token.value
                if native:
                    if not token.native_literal:
                        continue  # Regex is opaque, not a user-facing string.
                    if token.decoded_value is None:
                        ledger['dynamic_texts'].append({'source_expression': raw, 'decoding_status': 'unresolved',
                            'reason': 'SwiftParser_no_static_value', **anchor})
                        continue
                    value = token.decoded_value
                    if value:
                        group = 'colors' if re.fullmatch(r'#[0-9a-fA-F]{6,8}', value) else 'texts'
                        ledger[group].append({'value': value, 'page_level': True, **anchor})
                    continue
                reason = ('extended_delimiter_requires_swift_semantic_decode' if token.hash_count else
                          'multiline_requires_swift_semantic_decode' if token.quote_count == 3 else
                          'interpolation_requires_runtime_evaluation' if '\\(' in raw else None)
                if reason:
                    ledger['dynamic_texts'].append({'source_expression': raw, 'decoding_status': 'unresolved',
                                                   'reason': reason, **anchor})
                    continue
                try:
                    value = json.loads(raw)
                except ValueError:
                    ledger['dynamic_texts'].append({'source_expression': raw, 'decoding_status': 'unresolved',
                                                   'reason': 'unsupported_swift_string_escape', **anchor})
                    continue
                if not value:
                    continue
                group = 'colors' if re.fullmatch(r'#[0-9a-fA-F]{6,8}', value) else 'texts'
                ledger[group].append({'value': value, 'page_level': True, **anchor})
            elif (native and token.native_number) or re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', token.value):
                value = token.decoded_number if native and token.native_number else float(token.value) if '.' in token.value else int(token.value)
                if value is None:
                    continue  # Outside Swift's representable numeric range; no guessed value.
                ledger['numeric_constants'].append({'value': value, **anchor})
                context = {t.value for t in tokens[max(0, i - 8):i] if token.line - t.line <= 1}
                if context & {'spacing', 'systemFont', 'fontSize', 'constant', 'padding', 'width', 'height'}:
                    ledger['dims'].append({'value': value, 'unit': 'source_point_or_context_unresolved', **anchor})
            elif token.value in {'white', 'black', 'red', 'blue', 'clear', 'systemBackground', 'label', 'secondaryLabel'} and i and tokens[i - 1].value == '.':
                ledger['symbolic_colors'].append({'value': token.value, 'resolved_rgba': None, **anchor})
    if swift_syntax is not None:
        ledger['syntax_consumption'] = {'swift': 'SwiftSyntax', 'string_decoding': 'SwiftParser.representedLiteralValue',
                                      'python_swift_lexer': False}
    return ledger


def extract_for_project(source, project):
    """Replay the same official parser input used by the current fact graph."""
    syntax, conditional = None, None
    graph_path = project / 'spec/baseline/ios-facts.json'
    if graph_path.is_file():
        from .swift_native import project_syntax
        graph = read_json(graph_path)
        if graph.get('source_sha256') != source_snapshot(source)['sha256']:
            raise MigrationError('Source facts are stale; refresh before extracting literals')
        syntax = project_syntax(project, source, graph)
        if graph.get('conditional_evidence'):
            from .conditional_evidence import validate as validate_conditionals
            conditional = validate_conditionals(source, Path(graph['conditional_evidence']['path']), project=project)
            if conditional['reference'] != graph['conditional_evidence']:
                raise MigrationError('Conditional source view changed')
    return extract(source, swift_syntax=syntax, conditional=conditional)


def run(project, output=None):
    from .native_pipeline import context
    source, project = context(project)
    ledger = extract_for_project(source, project)
    write_json(output or project / 'spec/baseline/literal-ledger.json', ledger)
    return ledger
