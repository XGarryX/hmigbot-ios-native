"""Source-backed literals, with dynamic text and symbolic colors kept distinct."""
import json
import math
import re
from pathlib import Path
from .core import snapshot, digest, write_json
from .swiftui import tokenize as objc_tokenize
from .apple_tools import tokenize


def extract(source, source_view=None):
    snap = snapshot(source)
    ledger = {'schema_version': 2, 'source_platform': 'ios', 'source_sha256': snap['sha256'],
              'texts': [], 'colors': [], 'dims': [], 'durations_ms': [], 'dynamic_texts': [],
              'numeric_constants': [], 'symbolic_colors': [], 'files_scanned': 0,
              'scope': 'source token literals; not runtime values, layout conversion or complete localization'}
    for file in snap['files']:
        if Path(file['path']).suffix not in {'.swift', '.m', '.mm', '.h'}:
            continue
        if source_view and not source_view.includes(file['path']):
            continue
        ledger['files_scanned'] += 1
        text = source_view.text(file['path']) if source_view else (source / file['path']).read_text(encoding='utf-8-sig')
        tokens = tokenize(text, file['path']) if file['path'].endswith('.swift') else objc_tokenize(text)
        for i, token in enumerate(tokens):
            anchor = {'sources': [file['path'] + ':' + str(token.line)], 'file_sha256': file['sha256']}
            if token.kind == 'string':
                raw = token.value
                if file['path'].endswith('.swift') and token.literal_is_static:
                    value = token.literal_value
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
            elif getattr(token, 'number_literal', None) or re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', token.value):
                spelling = token.value
                normalized = spelling.replace('_', '') if getattr(token, 'number_literal', None) else spelling
                reason = 'non_decimal_literal' if normalized.lower().startswith(('0x','0o','0b')) else None
                try:
                    value = float(normalized) if getattr(token, 'number_literal', None)=='float' or '.' in normalized else int(normalized)
                    if isinstance(value,float) and not math.isfinite(value): reason = 'non_finite_numeric_literal'
                except (ValueError, OverflowError):
                    reason = reason or 'numeric_literal_not_representable'
                if reason:
                    ledger.setdefault('unresolved_numeric_constants', []).append({'source_expression':spelling,
                        'decoding_status':'unresolved','reason':reason, **anchor})
                    continue
                item = {'value': value, **anchor}
                if '_' in spelling or 'e' in spelling.lower(): item['source_expression'] = spelling
                ledger['numeric_constants'].append(item)
                context = {t.value for t in tokens[max(0, i - 8):i] if token.line - t.line <= 1}
                if context & {'spacing', 'systemFont', 'fontSize', 'constant', 'padding', 'width', 'height'}:
                    ledger['dims'].append({'value': value, 'unit': 'source_point_or_context_unresolved', **anchor})
            elif token.value in {'white', 'black', 'red', 'blue', 'clear', 'systemBackground', 'label', 'secondaryLabel'} and i and tokens[i - 1].value == '.':
                ledger['symbolic_colors'].append({'value': token.value, 'resolved_rgba': None, **anchor})
    if source_view:
        ledger['source_view'] = source_view.reference
    return ledger


def run(project, output=None):
    from .native_pipeline import context
    source, project = context(project)
    from .conditional_source import for_project
    ledger = extract(source, for_project(project, source))
    write_json(output or project / 'spec/baseline/literal-ledger.json', ledger)
    return ledger
