"""Deterministic source signals. Token evidence is never compiler or runtime proof."""
from __future__ import annotations

import re
from pathlib import Path
import xml.etree.ElementTree as ET

from .core import source_snapshot
from .core import MigrationError, digest, json_bytes, read_json, snapshot, write_json
from .swiftui import tokenize
from .source_scope import import_token_lines, source_anchor_info, PLIST_SUFFIXES
from .computed_properties import computed_property
from .xcode import project_inventory, dependency_inventory
from .resources import asset_inventory

RULESET = read_json(Path(__file__).with_name('ios_rules.json'))
RULES = RULESET['rules']
SOURCE_KINDS = {'.swift', '.m', '.mm', '.h', '.c', '.cpp'}


def _identity_borrowed(values, index):
    """Walk a lexical member/subscript receiver to a possible ownership prefix."""
    scan = index - 2
    while scan >= 0:
        while scan >= 0 and values[scan] in {'?', '!'}:
            scan -= 1
        if scan >= 0 and values[scan] in {']', ')'}:
            closing = values[scan]
            opening = '[' if closing == ']' else '('
            depth = 1
            scan -= 1
            while scan >= 0 and depth:
                if values[scan] == closing:
                    depth += 1
                elif values[scan] == opening:
                    depth -= 1
                scan -= 1
            if depth:
                return True  # Incomplete receiver cannot establish an ordinary read.
            if closing == ']':
                continue  # Include the subscript's receiver in the walk.
        elif scan >= 0 and ('_' + values[scan]).isidentifier():
            scan -= 1
            # This lexer splits Unicode names into fragments. Treat adjacent
            # identifier fragments conservatively as one receiver; never swallow
            # an ownership prefix. This is lexical evidence, not Swift binding.
            while (scan >= 0 and ('_' + values[scan]).isidentifier()
                   and values[scan] not in RULESET['identity_usage']['ownership_prefixes']):
                scan -= 1
            if scan >= 0 and values[scan] == '$':
                scan -= 1  # Closure shorthand $0 and projected-property $value.
        elif scan >= 0 and values[scan] == '`':
            scan -= 1
            while scan >= 0 and values[scan] != '`':
                scan -= 1
            if scan < 0:
                return True
            scan -= 1
        else:
            return scan < 0 or values[scan] != '\\'  # Untyped key path is a read; unknown receivers are not proven reads.
        if scan >= 0 and values[scan] == '.':
            scan -= 1
            continue
        break
    if scan < 0 or values[scan] not in RULESET['identity_usage']['ownership_prefixes']:
        return False
    # A binary bitwise '&' does not borrow the receiver. Ambiguous unary positions
    # remain conservative; no declaration/type binding is claimed.
    return values[scan] != '&' or scan == 0 or values[scan - 1] in {'(', ',', ':', '='}


def _identity_usage(values, index):
    """Describe lexical use, without binding a receiver or inferring its framework.

    Invocations and ambiguous generic/operator uses keep the UI default.
    A bare member access may instead be tested as a value read;
    ForEach has its own independent UI obligation even when its key path is read.
    """
    if values[index] == 'ForEach':
        return 'for_each'
    following = index + 1
    while (following < len(values) and values[following] in {'?', '!'}
           and values[following:following + 2] != ['!', '=']):
        following += 1
    if following < len(values) and values[following] in {'(', '{'}:
        return 'member_call'
    if _identity_borrowed(values, index):
        return 'unknown'
    # The bounded lexer emits +=/-= whole but splits >>= and &*=. Match the
    # operator's actual token spelling, retaining the same boundary for either form.
    operators = {''.join(values[following:following + length]) for length in (1, 2, 3)}
    if operators.intersection(RULESET['identity_usage']['compound_writes']):
        return 'unknown'
    if operators.intersection(RULESET['identity_usage']['comparisons']):
        return 'member_read'
    if following < len(values) and values[following] in {'<', '='}:
        return 'unknown'
    return 'member_read'


def _fact_rule(fact):
    for context in RULESET.get('context_rules', []):
        selector = context['selector']
        if (fact.get('kind') == selector['kind'] and fact.get('symbol') == selector['symbol']
                and all(fact.get('value', {}).get(key) == value
                        for key, value in selector['value'].items())):
            return context['rule']
    return RULES[fact['kind']]


def _is_task_priority_argument(values, index):
    """True only when a 'priority' token is the keyword argument of a Task constructor.

    Task.detached/Task/Task.init schedule work by priority; that is concurrency, not
    layout, so the enclosing 'Task' token already emits the task/concurrency obligation
    and its token window carries the priority literal. Every other 'priority' (property
    access, unknown callee, non-call) keeps its original constraint signal: lexical context
    alone cannot prove a scheduling meaning, so we do not exempt it.
    """
    if values[index] != 'priority' or index == 0 or index + 1 >= len(values):
        return False
    if values[index - 1] not in {'(', ','} or values[index + 1] != ':':
        return False
    open_index = index - 1
    if values[open_index] == ',':  # Later argument: walk back past balanced groups to the call's '('.
        depth, scan = 0, open_index - 1
        while scan >= 0:
            if values[scan] in {')', ']', '}'}:
                depth += 1
            elif values[scan] in {'(', '[', '{'}:
                if depth == 0:
                    break
                depth -= 1
            scan -= 1
        else:
            return False
        open_index = scan
    if values[open_index] != '(':
        return False
    if open_index >= 1 and values[open_index - 1] == 'Task':
        head = open_index - 1  # Task(priority: ...) initializer
    elif (open_index >= 3 and values[open_index - 1] in {'detached', 'init'}
          and values[open_index - 2] == '.' and values[open_index - 3] == 'Task'):
        head = open_index - 3  # Task.detached / Task.init
    else:
        return False
    return head == 0 or values[head - 1] != '.'  # An unknown qualified callee keeps protection.


def _is_button_cancel_role(values, index):
    """Recognize only the exact .cancel value of a bare Button's role argument.

    Calls, unknown member references and handler tokens keep their task signals.
    The Button event still carries the role value in its evidence window.
    """
    if (index < 4 or values[index - 3:index + 1] != ['role', ':', '.', 'cancel']
            or index + 1 >= len(values) or values[index + 1] not in {',', ')'}):
        return False
    open_index = index - 4
    if values[open_index] == ',':
        depth, scan = 0, open_index - 1
        while scan >= 0:
            if values[scan] in {')', ']', '}'}:
                depth += 1
            elif values[scan] in {'(', '[', '{'}:
                if depth == 0:
                    break
                depth -= 1
            scan -= 1
        else:
            return False
        open_index = scan
    return (open_index >= 1 and values[open_index] == '(' and values[open_index - 1] == 'Button'
            and (open_index == 1 or values[open_index - 2] != '.'))


class _FileViews:
    """Bytes, text and lines for the file currently being scanned, read at most once each.

    A fact anchor needs a line window, so add() used to re-read and re-decode the whole file
    per fact. The cache binds its one byte read to the snapshot's expected content hash,
    and is dropped as soon as another file or expected hash is requested. Token text and
    snippets share those verified bytes; a transient A -> B -> A edit cannot bind B to A.
    """
    __slots__ = ('_key', '_path', '_expected_sha256', '_raw', '_text', '_lines', '_decode_error')

    def __init__(self):
        self._key = self._path = self._raw = self._text = self._lines = self._decode_error = None
        self._expected_sha256 = None

    def _select(self, key, path, expected_sha256):
        if (key, path, expected_sha256) != (self._key, self._path, self._expected_sha256):
            self._key, self._path, self._expected_sha256 = key, path, expected_sha256
            self._raw = self._text = self._lines = self._decode_error = None

    def _read(self):
        if self._raw is None:
            raw = self._path.read_bytes()
            if digest(raw) != self._expected_sha256:
                raise MigrationError('Source content changed while reading snapshot file: ' + str(self._key))
            self._raw = raw
        return self._raw

    def raw(self, key, path, expected_sha256):
        self._select(key, path, expected_sha256)
        return self._read()

    def text(self, key, path, expected_sha256):
        self._select(key, path, expected_sha256)
        if self._text is None and self._decode_error is None:
            try:
                raw = self._read().decode('utf-8-sig')
            except UnicodeError as exc:
                self._decode_error = exc
                raise
            # Path.read_text applies universal newlines, so reproduce it rather than re-read.
            self._text = raw.replace('\r\n', '\n').replace('\r', '\n')
        if self._decode_error is not None:
            raise self._decode_error
        return self._text

    def lines(self, key, path, expected_sha256):
        self._select(key, path, expected_sha256)
        text = self.text(key, path, expected_sha256)
        if self._lines is None:
            self._lines = text.splitlines()
        return self._lines


def extract(source: Path, variant: dict | None = None, *, manifest_evidence: Path | None = None, swift_syntax=None):
    """Repository scope is explicit; effective configuration remains unresolved without tools."""
    snap = source_snapshot(source)
    variant = variant or {'scope': 'repository', 'effective_build': 'unresolved'}
    if not isinstance(variant, dict) or variant.get('scope') not in {'repository', 'selected-build', 'project-targets'}:
        raise MigrationError('Variant must declare repository, selected-build or project-targets scope')
    project_context = None
    conditional = None
    additional_compiled_files = set()
    if variant['scope'] == 'project-targets':
        from .project_scope import resolve
        variant, project_context = resolve(source, variant, _context=True)
    if variant['scope'] == 'selected-build':
        # Membership needs an explicit path set; caller cannot promote guessed settings.
        if not isinstance(variant.get('source_files'), list) or not variant.get('evidence_path'):
            raise MigrationError('Selected build requires source_files and captured evidence_path')
        if not set(variant['source_files']) <= {f['path'] for f in snap['files']}:
            raise MigrationError('Variant contains unknown source files')
        from .evidence import validate
        bundle = Path(variant['evidence_path'])
        captured = validate(source, bundle)
        membership = read_json(bundle / 'artifacts/source-files.json')
        manifest = read_json(bundle / 'manifest.json')
        if captured['kind'] != 'source_build' or 'artifacts/source-files.json' not in manifest['artifacts'] or membership.get('source_files') != variant['source_files']:
            raise MigrationError('Selected membership must match hashed source-build evidence')
        if membership.get('kind') == 'source_build_membership':
            from .source_build_membership import validate as validate_membership
            checked = validate_membership(source, membership, capture=bundle / 'artifacts')
            if checked['membership_status'] != 'complete':
                raise MigrationError('Selected build requires complete captured compiler membership')
            selection = membership['selection']
            if 'selection' in variant and variant['selection'] != selection:
                raise MigrationError('Selected build identity differs from captured membership')
            for key in ('scheme', 'configuration', 'sdk', 'product', 'xcode_version', 'toolchain', 'targets', 'architectures'):
                if key in variant and variant[key] != selection.get(key):
                    raise MigrationError('Selected build identity differs from capture: ' + key)
            if 'target' in variant and selection['targets'] != [variant['target']]:
                raise MigrationError('Single target identity does not match the captured target set')
            pinned = {'selection': selection, 'source_membership': 'captured_compiler_inputs',
                      'membership_status': 'complete', 'effective_build': 'unresolved',
                      'evidence_manifest_sha256': digest((bundle / 'manifest.json').read_bytes()),
                      'membership_sha256': digest((bundle / 'artifacts/source-files.json').read_bytes())}
            for key, expected in pinned.items():
                if key in variant and variant[key] != expected:
                    raise MigrationError('Selected build evidence reference changed: ' + key)
            variant = {**variant, **pinned}
        elif set(membership) != {'source_files'}:
            # The previous unversioned source_files-only shape remains readable;
            # malformed modern evidence cannot bypass validation as legacy data.
            raise MigrationError('Unsupported source build membership contract')
        elif (set(variant) & {'selection', 'source_membership', 'membership_status',
                              'evidence_manifest_sha256', 'membership_sha256'}
              or variant.get('effective_build', 'unresolved') != 'unresolved'):
            raise MigrationError('Legacy membership cannot claim captured compiler identity or verified build')
        if variant.get('conditional_evidence'):
            from .conditional_evidence import validate as validate_conditionals
            conditional = validate_conditionals(source, Path(variant['conditional_evidence']))
            if (conditional['members'] != variant['source_files'] or
                    conditional['expected_build'] != variant.get('expected_build') or
                    Path(read_json(Path(variant['conditional_evidence']) / 'manifest.json')['build_evidence']).resolve() != bundle.resolve()):
                raise MigrationError('Conditional evidence does not match selected build')
            # Textually included headers are product inputs only when a
            # validated compiler view names them. Keep their per-unit regions.
            additional_compiled_files.update(set(conditional.get('analysis_files', [])) - set(variant['source_files']))
        if variant.get('compilation_evidence_path'):
            if conditional is None:
                raise MigrationError('Separate compilation evidence requires validated conditional context')
            compiled_bundle = Path(variant['compilation_evidence_path'])
            compiled_capture = validate(source, compiled_bundle)
            from .source_build_membership import validate as validate_membership
            compiled_document = read_json(compiled_bundle / 'artifacts/source-files.json')
            if compiled_capture['kind'] != 'source_build' or compiled_document.get('kind') != 'source_build_membership':
                raise MigrationError('Separate compilation evidence needs versioned source build membership')
            checked = validate_membership(source, compiled_document, capture=compiled_bundle / 'artifacts')
            selection, expected = compiled_document['selection'], conditional['expected_build']
            if (checked['membership_status'] != 'complete'
                    or any(selection.get(key) != expected.get(key) for key in ('scheme', 'configuration', 'sdk'))
                    or expected.get('target') not in selection['targets']
                    or expected.get('architecture') not in selection['architectures']):
                raise MigrationError('Compilation units and preprocessing dependencies use different build contexts')
            additional_compiled_files = set(compiled_document['source_files'])
            pinned_view = {'compiled_source_files': sorted(additional_compiled_files),
                           'preprocessor_dependency_files': conditional['members'],
                           'compilation_manifest_sha256': digest((compiled_bundle / 'manifest.json').read_bytes())}
            for key, value in pinned_view.items():
                if key in variant and variant[key] != value:
                    raise MigrationError('Separate membership view changed: ' + key)
            variant = {**variant, **pinned_view}

    evaluated_manifests, evidence_ref = None, None
    if manifest_evidence is not None:
        from .manifest_evidence import validate
        bundle = Path(manifest_evidence).resolve()
        report_path = bundle / 'manifest.json' if bundle.is_dir() else bundle
        evaluation = validate(source, bundle)
        evaluated_manifests = evaluation['manifests']
        evidence_ref = {'path': str(report_path), 'report_sha256': digest(report_path.read_bytes())}
    facts, issues = [], []
    occurrence = {}
    file_views = _FileViews()

    def add(file, kind, line, end, symbol, value, owner='unresolved', evidence='token_signal'):
        key = (file['path'], kind, owner, symbol)
        occurrence[key] = occurrence.get(key, 0) + 1
        ident = 'IF-' + digest(json_bytes([*key, occurrence[key]]))[:16]
        raw = file_views.raw(file['path'], source / file['path'], file['sha256'])
        resource_info = source_anchor_info(source / file['path'], raw=raw) if kind == 'resource' and Path(file['path']).suffix.lower() in PLIST_SUFFIXES else None
        try:
            if resource_info and resource_info['coordinate_kind'] == 'resource_document':
                raise UnicodeError('Resource-document coordinate')
            text = file_views.text(file['path'], source / file['path'], file['sha256'])
            snippet = '\n'.join(file_views.lines(file['path'], source / file['path'], file['sha256'])[line - 1:end])
        except UnicodeError:
            if kind != 'resource':
                raise MigrationError('Non-text source needs an explicit parser: ' + file['path'])
            snippet = 'binary resource sha256:' + file['sha256']
            value = {**value, 'encoding': 'binary', 'content_validation': 'unresolved'}
        if resource_info:
            value = {**value, **{k: v for k, v in resource_info.items() if k != 'line_count'}}
        facts.append({'id': ident, 'kind': kind, 'symbol': symbol, 'owner': owner,
                      'value': value, 'resolution': evidence, 'variant': variant['scope'],
                      'anchor': {'path': file['path'], 'line': line, 'end_line': end,
                                 'file_sha256': file['sha256'], 'snippet_sha256': digest(snippet.encode()),
                                 'snippet': snippet}})
        if build_contexts is not None:
            facts[-1]['build_contexts'] = build_contexts

    inputs = []
    objc_inputs = []
    unresolved_conditions = {item['path'] for item in conditional.get('unknowns', [])} if conditional else set()
    for file in snap['files']:
        if file['path'] in unresolved_conditions:
            issues.append({'kind': 'conditional_compilation_unresolved', 'path': file['path'],
                           'reason': 'Selected compiler context could not resolve this source view'})
            continue
        views = conditional['observed'].get(file['path']) if conditional else None
        if views:
            groups = {}
            for view in views:
                key = tuple(view['active_lines'])
                groups.setdefault(key, []).append({'unit': view['unit'], 'instance': view['instance']})
            for lines, contexts in sorted(groups.items()):
                inputs.append((file, set(lines), contexts))
        else:
            inputs.append((file, None, None))
    for file, active_lines, build_contexts in inputs:
        path = source / file['path']
        if variant['scope'] == 'selected-build' and path.suffix in SOURCE_KINDS and file['path'] not in set(variant['source_files']) | additional_compiled_files:
            continue
        if (variant['scope'] == 'project-targets' and path.suffix in SOURCE_KINDS - {'.h'}
                and file['path'] not in variant['source_files']):
            continue  # Declared product membership; implicit headers remain conservatively included.
        if path.suffix in SOURCE_KINDS:
            text = file_views.text(file['path'], path, file['sha256'])
            native_swift = path.suffix == '.swift' and swift_syntax is not None
            if native_swift:
                from .swift_native import tokens_for
                if file['path'] not in swift_syntax:
                    raise MigrationError('SwiftSyntax lexical evidence omitted source: ' + file['path'])
                # SwiftSyntax coordinates bind raw UTF-8, before newline/BOM adaptation.
                tokens = tokens_for(swift_syntax[file['path']], file_views.raw(file['path'], path, file['sha256']).decode('utf-8'))
            else:
                tokens = tokenize(text, skip_pragma_marks=path.suffix in {'.m', '.mm', '.h', '.c', '.cpp'})
            if active_lines is not None:
                tokens = [t for t in tokens if t.line in active_lines]
            if path.suffix in {'.m', '.mm', '.h'}:
                objc_inputs.append((file, tokens, build_contexts))
            import_lines = import_token_lines(tokens)
            values = [t.value for t in tokens]
            owner, pending_owner, depth, stack, wrapper_vars = 'file', None, 0, [], set()
            computed_scopes, pending_computed_scope, computed_members = [], None, []
            storage = {'State', 'StateObject', 'ObservedObject', 'EnvironmentObject', 'Environment', 'Binding', 'AppStorage', 'SceneStorage'}
            for i, token in enumerate(tokens):
                v = token.value
                if v in {'class', 'struct', 'enum', 'extension'} and i + 1 < len(tokens):
                    pending_owner = values[i + 1]
                # Separate lexical membership tracking avoids treating `class func`
                # or `class var` modifiers as type declarations. Legacy owners/IDs
                # remain unchanged; protocols are tracked only to exclude requirements.
                if (token.kind != 'string' and v in {'class', 'struct', 'enum', 'extension', 'protocol'}
                        and i + 1 < len(tokens) and tokens[i + 1].kind == 'identifier'
                        and values[i + 1] not in {'func', 'var', 'let', 'subscript'}):
                    pending_computed_scope = v
                if v == '{':
                    depth += 1
                    if pending_computed_scope:
                        computed_scopes.append((depth, pending_computed_scope))
                        pending_computed_scope = None
                    if pending_owner:
                        stack.append((depth, owner)); owner = pending_owner; pending_owner = None
                if v == '}':
                    if computed_scopes and computed_scopes[-1][0] == depth:
                        computed_scopes.pop()
                    if stack and stack[-1][0] == depth:
                        _, owner = stack.pop()
                    depth -= 1
                # No comment/string scans: only syntax tokens can activate a rule.
                if token.kind == 'string':
                    continue
                if token.line in import_lines:
                    if v == ';':
                        import_lines.remove(token.line)
                    continue  # A dependency import is not an executable persistence/event operation.
                after = values[i + 1:i + 24]
                window = ' '.join(after)
                if v == '@' and after and after[0] in storage:
                    start = i + 2
                    while start < len(tokens) and start < i + 16 and values[start] not in {'var', '{', '}'}:
                        start += 1
                    if start >= len(tokens) or values[start] != 'var':
                        issues.append({'rule': 'IOS.STATE_UNRESOLVED', 'path': file['path'], 'line': token.line})
                        continue
                    wrapper_vars.add(start)
                    end = start + 1
                    while end < len(tokens) and tokens[end].line == tokens[start].line and values[end] not in {'{', '}', ';'}:
                        end += 1
                    declaration = values[i + 1:end]
                    if 'var' not in declaration:
                        issues.append({'rule': 'IOS.STATE_UNRESOLVED', 'path': file['path'], 'line': token.line})
                    else:
                        k = declaration.index('var')
                        name = declaration[k + 1] if k + 1 < len(declaration) else 'unresolved'
                        init = ' '.join(declaration[declaration.index('=') + 1:]) if '=' in declaration else None
                        type_ = ' '.join(declaration[declaration.index(':') + 1:declaration.index('=') if '=' in declaration else len(declaration)]) if ':' in declaration else None
                        add(file, 'binding' if after[0] == 'Binding' else 'state', token.line, tokens[end - 1].line,
                            name, {'storage': after[0], 'type': type_, 'initializer': init}, owner)
                if v == 'var' and i not in wrapper_vars and stack and depth == stack[-1][0]:
                    end = i + 1
                    while end < len(tokens) and tokens[end].line == token.line and values[end] not in {'{', '}', ';'}:
                        end += 1
                    decl = values[i + 1:end]
                    if '=' in decl and decl:
                        k = decl.index('=')
                        type_ = ' '.join(decl[decl.index(':') + 1:k]) if ':' in decl else None
                        add(file, 'state', token.line, token.line, decl[0], {'storage': 'stored_property', 'type': type_, 'initializer': ' '.join(decl[k + 1:])}, owner)
                    elif (path.suffix == '.swift' and computed_scopes
                          and depth == computed_scopes[-1][0] and computed_scopes[-1][1] != 'protocol'):
                        derived = computed_property(tokens, i)
                        if derived is not None:
                            computed_members.append((derived, owner))
                if v in {'Button', 'onTapGesture', 'addTarget', 'IBAction'}:
                    add(file, 'event', token.line, min(tokens[min(i + 12, len(tokens) - 1)].line, token.line + 3), v,
                        {'trigger': v, 'tokens': window, 'handler_resolution': 'unresolved'}, owner)
                if v in {'=', '+=', '-='} and i > 0:
                    if values[i - 1] not in {'=', '<', '>', '!', '+', '-'}:
                        add(file, 'write', token.line, token.line, values[i - 1], {'operator': v, 'tokens': window}, owner)
                if v in {'if', 'guard', 'switch', 'catch', 'throw'}:
                    add(file, 'branch', token.line, token.line, v, {'condition_tokens': window}, owner)
                if v in {'task', 'Task', 'async', 'await', 'MainActor', 'cancel'}:
                    if not (v == 'cancel' and _is_button_cancel_role(values, i)):
                        add(file, 'task', token.line, token.line, v, {'tokens': window, 'binding': 'unresolved'}, owner)
                if v in {'NavigationLink', 'navigationDestination', 'sheet', 'fullScreenCover', 'pushViewController', 'present', 'performSegue'}:
                    add(file, 'navigation', token.line, token.line, v, {'tokens': window, 'destination': 'unresolved'}, owner)
                if v in {'UserDefaults', 'AppStorage', 'SceneStorage', 'CoreData', 'SwiftData', 'Keychain', 'SecItemAdd', 'SecItemCopyMatching'}:
                    add(file, 'persistence', token.line, token.line, v, {'tokens': window}, owner)
                if v in {'URLSession', 'Alamofire', 'AVPlayer', 'CLLocationManager', 'StoreKit', 'WKWebView', 'requestAuthorization'}:
                    add(file, 'service', token.line, token.line, v, {'tokens': window, 'contract': 'unresolved'}, owner)
                if v in {'viewDidLoad', 'viewWillAppear', 'viewDidAppear', 'viewWillDisappear', 'viewDidDisappear', 'deinit', 'onAppear', 'onDisappear'}:
                    add(file, 'lifecycle', token.line, token.line, v, {'tokens': window}, owner)
                if v in {'constraint', 'NSLayoutConstraint', 'priority'}:
                    if not (v == 'priority' and _is_task_priority_argument(values, i)):
                        add(file, 'constraint', token.line, token.line, v, {'tokens': window, 'relation': 'unresolved'}, owner)
                if v == 'ForEach' or v == 'id' and i and values[i - 1] == '.':
                    add(file, 'identity', token.line, token.line, v,
                        {'tokens': window, 'token_index': i, 'identity_usage': _identity_usage(values, i)}, owner)
                if v in {'VStack', 'HStack', 'ZStack', 'List', 'ScrollView', 'Text', 'Image', 'UIView', 'UILabel', 'UIButton', 'UIStackView'}:
                    add(file, 'composition', token.line, token.line, v, {'tokens': window}, owner)
                if v in {'frame', 'padding', 'background', 'overlay', 'clipShape', 'offset', 'position', 'opacity', 'transition', 'animation'} and i and values[i - 1] == '.':
                    add(file, 'modifier', token.line, token.line, v, {'token_index': i, 'tokens': window, 'order': 'lexical_only'}, owner)
                if v in {'Environment', 'EnvironmentObject', 'environment', 'environmentObject'}:
                    add(file, 'environment', token.line, token.line, v, {'tokens': window}, owner)
                if v in {'nil', 'nullable', 'nonnull', '_Nullable', '_Nonnull'} or v == '?' and i and tokens[i - 1].kind == 'identifier':
                    add(file, 'language', token.line, token.line, v, {'tokens': window}, owner)
                if v in {'weak', 'unowned', 'copy', 'assign', 'strong'}:
                    add(file, 'ownership', token.line, token.line, v, {'tokens': window}, owner)
                if v in {'delegate', 'dataSource', 'performSelector', 'valueForKey', 'setValue'}:
                    add(file, 'delegate', token.line, token.line, v, {'tokens': window, 'receiver': 'unresolved'}, owner)
            # Append after legacy facts so a conditional declaration with the same
            # owner/name cannot change an existing fact's occurrence-based ID.
            for derived, derived_owner in computed_members:
                value = {key: val for key, val in derived.items()
                         if key not in {'symbol', 'line', 'end_line', 'resolution'}}
                add(file, 'state', derived['line'], derived['end_line'], derived['symbol'], value,
                    derived_owner, evidence='token_signal')
            if depth != 0:
                issues.append({'rule': 'IOS.TOKEN_BALANCE', 'path': file['path'], 'message': 'Use a syntax provider; token scope is incomplete'})
            if not native_swift and any(ord(t.value[0]) > 127 and t.kind != 'string' for t in tokens if t.value):
                issues.append({'rule': 'IOS.TOKEN_IDENTIFIER_UNRESOLVED', 'path': file['path'], 'message': 'Unicode identifiers require a syntax provider and explicit review'})
            if active_lines is None:
                if path.suffix == '.swift':
                    if native_swift:
                        parsed = swift_syntax[file['path']]
                    else:
                        from .swift_native import parse_sources
                        parsed = parse_sources({file['path']: text})[file['path']]
                    has_conditional = any(node['kind'] == 'conditional_compilation' for node in parsed['nodes'])
                else:
                    has_conditional = bool(re.search(r'^\s*#\s*(if|ifdef|ifndef)', text, re.M))
                if has_conditional:
                    issues.append({'rule': 'IOS.CONDITIONAL_BUILD', 'path': file['path'],
                                   'message': 'Resolve active branches using selected compiler configuration'})
        elif path.suffix in {'.storyboard', '.xib'}:
            text = file_views.text(file['path'], path, file['sha256'])
            if '<!DOCTYPE' in text or '<!ENTITY' in text:
                raise MigrationError('Interface Builder DTD/entities are not supported')
            try:
                tree = ET.fromstring(text)
                lines = file_views.lines(file['path'], path, file['sha256'])
                for element in tree.iter():
                    kind = {'action': 'event', 'segue': 'navigation', 'constraint': 'constraint'}.get(element.tag)
                    if kind:
                        # XML parser verifies structure; textual location is a locator only.
                        ident = element.get('id', element.get('selector', element.tag))
                        line = next((n for n, s in enumerate(lines, 1) if ident in s), 1)
                        add(file, kind, line, line, ident, dict(element.attrib), evidence='structured_xml')
            except ET.ParseError as exc:
                issues.append({'rule': 'IOS.IB_PARSE', 'path': file['path'], 'message': str(exc)})
        elif path.name == 'Contents.json' or path.suffix in {'.xcstrings', '.stringsdict', '.xcprivacy', '.entitlements', '.plist'}:
            try:
                add(file, 'resource', 1, 1, path.name, {'resource_type': path.suffix or path.name}, evidence='resource_locator')
            except MigrationError as exc:
                if str(exc).startswith('Source content changed'):
                    raise
                issues.append({'rule': 'IOS.RESOURCE_PARSE', 'path': file['path'], 'message': str(exc)})
    from .objc_state import extract_states
    objc_states, objc_issues = extract_states(objc_inputs)
    issues.extend(objc_issues)
    for state in objc_states:
        # Keep declarations and their cross-file assignment evidence together;
        # conditional views retain the declaration's original build contexts.
        build_contexts = state['contexts']
        add(state['file'], 'state', state['line'], state['end_line'],
            state['symbol'], state['value'], state['owner'])
    project, pi = project_inventory(source, snap['files'])
    dependencies, di = dependency_inventory(source, snap['files'], manifest_evaluations=evaluated_manifests)
    assets, ai = asset_inventory(source, snap['files'])
    graph = {'schema_version': 2, 'source_platform': 'ios', 'source_sha256': snap['sha256'],
            'variant': variant, 'facts': facts, 'issues': issues + pi + di + ai,
            'project': project, 'dependencies': dependencies, 'assets': assets,
            'capabilities': {'syntax': 'token_signal', 'symbol_binding': 'unresolved',
                             'effective_build': 'unresolved', 'runtime': 'unavailable'}}
    if project_context is not None:
        from .manifest_scope import classify
        graph['dependency_scope'] = classify(source, snap, variant, project_context, swift_syntax=swift_syntax)
    if evidence_ref is not None:
        graph['manifest_evidence'] = evidence_ref
    if swift_syntax is not None:
        graph['capabilities']['syntax'] = 'SwiftSyntax_input_with_migration_signals'
        graph['capabilities']['swift_syntax'] = 'SwiftParser/SwiftSyntax lexical input; migration signals remain unresolved'
        graph['syntax_consumption'] = {'swift': 'SwiftSyntax', 'python_swift_lexer': False,
            'files': sorted(swift_syntax), 'symbol_binding': 'unresolved'}
    if conditional is not None:
        graph['conditional_evidence'] = conditional['reference']
        graph['capabilities']['conditional_compilation'] = 'compiler_source_views' if conditional.get('analysis_files') else 'clang_textual_observations'
        # Module/PCH-only files and non-C inputs are NOT promoted by this capture.
    return graph


def obligations(graph):
    return {'schema_version': 2, 'source_sha256': graph['source_sha256'],
            'graph_sha256': digest(json_bytes(graph)), 'rules_sha256': digest(json_bytes(RULESET)),
            'obligations': [{'id': 'IO-' + fact['id'][3:], 'fact_id': fact['id'], 'kind': fact['kind'],
                             **_fact_rule(fact)} for fact in graph['facts']]}


def _capture_providers(project, source, graph, providers):
    """Run each planned provider into its own attempt directory; return saved references and issues.

    Only a published artifact becomes a graph reference. A failed try keeps its diagnostics under
    a fresh attempt path, so the same source and configuration can be retried without deleting
    evidence and without reusing an unverified capture.
    """
    from .atoms import run_atom
    from .provider_runs import ProviderRun, retained_failures
    artifacts, issues = [], []
    for provider in providers:
        name = provider['operation']
        config = Path(provider['config']) if provider.get('config') else None
        input_path = Path(provider['input']) if provider.get('input') else None
        run = ProviderRun(project, name, graph['source_sha256'], config=config, input_path=input_path)
        reused = run.reusable()
        if reused is not None:
            report = reused['report']
            artifacts.append({key: reused[key] for key in ('path', 'sha256', 'operation', 'run')})
        else:
            try:
                run.reserve()
                with run.fixed_inputs() as (fixed_config, fixed_input):
                    report = run_atom(name, source, run.directory, provider_config=fixed_config, input_path=fixed_input)
                    artifact = run.publish(report)
            except (MigrationError, OSError, ValueError) as exc:
                if run.reserved and not run.finished:
                    run.fail(exc)
                if str(exc).startswith('Source changed while extracting;'):
                    raise MigrationError('Source changed while extracting; retained diagnostics: ' + str(run.directory)) from exc
                raise MigrationError('Provider failed; retained diagnostics: ' + str(run.directory)) from exc
            artifacts.append(artifact)
        issues.extend({'rule': 'IOS.PROVIDER_UNRESOLVED', 'operation': name, 'detail': issue} for issue in report.get('issues', []))
        issues.extend({'rule': 'IOS.PROVIDER_RETRY', 'operation': name, 'detail': failure}
                      for failure in retained_failures(project / artifacts[-1]['path']))
    return artifacts, issues


def refresh(project, source, variant=None, provider_plan=None, manifest_evidence=None):
    if variant and variant.get('conditional_evidence'):
        from .conditional_evidence import validate as validate_conditionals
        validate_conditionals(source, Path(variant['conditional_evidence']), project=project)
    from .provider_plan import preflight
    providers = preflight(provider_plan) if provider_plan is not None else None
    if manifest_evidence is not None:
        manifest_evidence = Path(manifest_evidence).resolve()
        if not manifest_evidence.is_relative_to((project / 'spec/ref/ios-manifest-evidence').resolve()):
            raise MigrationError('Manifest evidence must be under project/spec/ref/ios-manifest-evidence for pinned consumption')
    # Official parser artifacts must exist BEFORE fact extraction, rather than
    # being attached after Python has already parsed the source.
    artifacts, provider_issues = [], []
    syntax = None
    if providers:
        source_sha256 = source_snapshot(source)['sha256']
        artifacts, provider_issues = _capture_providers(project, source, {'source_sha256': source_sha256}, providers)
        from .swift_native import syntax_from_artifacts
        syntax = syntax_from_artifacts(project, source, source_sha256, artifacts)
    graph = extract(source, variant, manifest_evidence=manifest_evidence, swift_syntax=syntax)
    if providers:
        graph['provider_artifacts'] = artifacts
        graph['issues'].extend(provider_issues)
    if source_snapshot(source)['sha256'] != graph['source_sha256']:
        raise MigrationError('Source changed while extracting; the previous baseline stays published and nothing new is written')
    base = project / 'spec/baseline'
    if (base / 'ios-facts.json').exists():
        previous = read_json(base / 'ios-facts.json')
        if previous != graph:
            archive = project / 'spec/.a2h/history' / digest(json_bytes(previous))
            write_json(archive / 'ios-facts.json', previous)
    write_json(base / 'ios-facts.json', graph)
    write_json(base / 'ios-obligations.json', obligations(graph))
    if source_snapshot(source)['sha256'] != graph['source_sha256']:
        raise MigrationError('Source changed while extracting; retained graph is invalid until refreshed')
    return graph


def validate_graph(source, project):
    graph = read_json(project / 'spec/baseline/ios-facts.json')
    if graph.get('conditional_evidence') is not None:
        from .conditional_evidence import validate as validate_conditionals
        ref = graph['conditional_evidence']
        if validate_conditionals(source, Path(ref['path']), project=project)['reference'] != ref:
            raise MigrationError('Conditional evidence changed; re-extract and review')
    manifest = graph.get('manifest_evidence')
    evidence_path = None
    if manifest is not None:
        if (not isinstance(manifest, dict) or set(manifest) != {'path', 'report_sha256'}
                or not isinstance(manifest['path'], str)):
            raise MigrationError('Invalid manifest evaluation evidence reference')
        evidence_path = Path(manifest['path']).resolve()
        if not evidence_path.is_relative_to((project / 'spec/ref/ios-manifest-evidence').resolve()):
            raise MigrationError('Manifest evidence reference escapes the pinned project evidence directory')
        if digest(evidence_path.read_bytes()) != manifest['report_sha256']:
            raise MigrationError('Manifest evaluation evidence changed')
    from .swift_native import syntax_from_artifacts
    syntax = syntax_from_artifacts(project, source, graph['source_sha256'], graph.get('provider_artifacts', []))
    current = extract(source, graph.get('variant'), manifest_evidence=evidence_path, swift_syntax=syntax)
    if graph.get('provider_artifacts'):
        from .core import safe_child
        from .provider_runs import retained_failures
        current['provider_artifacts'] = graph['provider_artifacts']
        for item in graph['provider_artifacts']:
            path = safe_child(project, item['path'])
            if digest(path.read_bytes()) != item['sha256']:
                raise MigrationError('Provider evidence changed')
            report = read_json(path)
            if report.get('source_sha256') != current['source_sha256']:
                raise MigrationError('Provider evidence source is stale')
            current['issues'].extend({'rule': 'IOS.PROVIDER_UNRESOLVED', 'operation': item['operation'], 'detail': issue} for issue in report.get('issues', []))
            current['issues'].extend({'rule': 'IOS.PROVIDER_RETRY', 'operation': item['operation'], 'detail': failure}
                                     for failure in retained_failures(path))
    if graph != current:
        raise MigrationError('Source facts are stale or edited; re-extract and re-review affected coverage')
    expected = obligations(graph)
    if read_json(project / 'spec/baseline/ios-obligations.json') != expected:
        raise MigrationError('Obligations must be machine-derived from current facts and rules')
    return graph, expected


def view(project, source, scope):
    graph, obs = validate_graph(source, project)
    selections = {
        'project': set(),
        'ui': {'state', 'binding', 'event', 'navigation', 'lifecycle', 'constraint', 'identity', 'composition', 'modifier', 'environment', 'delegate'},
        'feature': {'state', 'write', 'branch', 'task', 'persistence', 'service', 'language', 'ownership', 'lifecycle'},
        'api': {'service', 'persistence', 'task', 'delegate', 'resource'}
    }
    if scope not in selections:
        raise MigrationError('Unknown source analysis scope')
    value = {'schema_version': 2, 'scope': scope, 'source_sha256': graph['source_sha256'],
             'graph_sha256': digest(json_bytes(graph)), 'issues': graph['issues'], 'capabilities': graph['capabilities'],
             'facts': [f for f in graph['facts'] if f['kind'] in selections[scope]]}
    if scope == 'project':
        value.update(project=graph['project'], dependencies=graph['dependencies'], assets=graph['assets'])
        if 'dependency_scope' in graph: value['dependency_scope'] = graph['dependency_scope']
    ids = {f['id'] for f in value['facts']}
    value['obligations'] = [o for o in obs['obligations'] if o['fact_id'] in ids]
    write_json(project / f'spec/ref/ios-{scope}-signals.json', value)
    return value
