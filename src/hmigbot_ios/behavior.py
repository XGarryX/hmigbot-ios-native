"""Behavior-chain gate and explicit process observations; no generated done markers."""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .core import source_snapshot
from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot, write_json


@dataclass(frozen=True)
class _TargetToken:
    value: str
    line: int
    literal: bool = False
    start: int = field(default=-1, compare=False, repr=False)
    end: int = field(default=-1, compare=False, repr=False)


def _target_tokens(text):
    """Small JS/ArkTS boundary lexer, not a compiler or a behavior oracle.

    Comments disappear; literals remain opaque, nonempty tokens. In particular,
    braces/arrows inside a string, template or regexp cannot name a handler.
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
                # The interpolation is already opaque. A possible division is
                # skipped only up to its slash; no token inside can be selected.
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
    while pos < len(text):
        start, start_line = pos, line
        char = text[pos]
        if char.isspace():
            line += char == '\n'
            pos += 1
            continue
        if text.startswith(('//', '/*'), pos):
            pos = comment_end(pos)
        elif char in '\'"`':
            pos = quoted_end(pos)
            result.append(_TargetToken('<literal>', start_line, True, start, pos))
        elif (char == '/' and (not result or result[-1].value in expression_prefix)
              and (end := regexp_end(pos)) is not None):
            pos = end
            result.append(_TargetToken('<literal>', start_line, True, start, pos))
        else:
            match = re.match(r'[$\w]+|=>', text[pos:])
            value = match.group() if match else char
            result.append(_TargetToken(value, start_line, False, start, start + len(value)))
            pos += len(value)
        line += text[start:pos].count('\n')
    return result


def _target_pairs(tokens):
    stack, pairs = [], {}
    for index, token in enumerate(tokens):
        if token.literal:
            continue
        if token.value in {'(', '[', '{'}:
            stack.append(index)
        elif token.value in {')', ']', '}'}:
            if not stack or tokens[stack[-1]].value != {')': '(', ']': '[', '}': '{'}[token.value]:
                # An incomplete lexical scope is not evidence of an empty body.
                return {}
            opening = stack.pop()
            pairs[opening] = index
    return pairs


def _callable_body(tokens, start, end, pairs):
    """Locate an inline arrow/function body without entering its parameters."""
    if start < end and tokens[start].value == 'async':
        start += 1
    while start < end and tokens[start].value == '(' and pairs.get(start) == end - 1:
        start, end = start + 1, end - 1
    function = start < end and tokens[start].value == 'function'
    index = start + 1 if function else start
    while index < end:
        value = tokens[index].value
        if value == '=>' or function and value == '{':
            body = index + 1 if value == '=>' else index
            if body < end and tokens[body].value == '{' and pairs.get(body, end) < end:
                return body
            return None  # An expression body performs work, including literals.
        if value in {'(', '['} and index in pairs:
            index = pairs[index] + 1
        elif value in {',', ';', '{', '}'}:
            return None
        else:
            index += 1
    return None


def _selected_handler_bodies(tokens, symbol_end, pairs):
    """Resolve only the declaration or direct callback attached to this symbol."""
    start, limit = symbol_end + 1, len(tokens)
    if start >= limit:
        return []
    if tokens[start].value == '(' and start in pairs:
        close = pairs[start]
        after = close + 1
        # Declaration body, optionally after a return type. Do not interpret a
        # Python suite, a subsequent statement or a chained call as a method.
        if after < limit and tokens[after].value == ':':
            after += 1
            while after < limit:
                value = tokens[after].value
                if value in {';', '=', 'return', 'this', 'const', 'let', 'def', 'class'}:
                    break
                if value == '{':
                    # A structural return type can itself have braces.
                    following = pairs.get(after, limit) + 1
                    if following < limit and tokens[following].value == '{':
                        after = following
                    break
                if value in {'(', '['} and after in pairs:
                    after = pairs[after] + 1
                else:
                    after += 1
        if after < limit and tokens[after].value == '{' and after in pairs:
            return [after]
        # A call can own one inline callback. With multiple direct arguments the
        # metadata cannot identify which callback is the behavior node.
        index = start + 1
        while index < close:
            if tokens[index].value == ',':
                return []
            index = pairs[index] + 1 if index in pairs else index + 1
        body = _callable_body(tokens, start + 1, close, pairs)
        return [body] if body is not None else []
    # Named arrow/function field or variable: skip type syntax up to its actual
    # assignment, rather than mistaking an @Event function type for its value.
    index = start
    while index < limit:
        value = tokens[index].value
        if value == '=':
            end = index + 1
            while end < limit and tokens[end].value not in {';', '}'}:
                end = pairs[end] + 1 if end in pairs else end + 1
            body = _callable_body(tokens, index + 1, end, pairs)
            return [body] if body is not None else []
        if value in {';', '}'}:
            break
        index = pairs[index] + 1 if index in pairs else index + 1
    return []


def _empty_target_handler(text, symbol, line):
    tokens, selected = _target_tokens(text), []
    symbol_tokens = _target_tokens(symbol)
    name = [token.value for token in symbol_tokens]
    if not name or any(token.literal for token in symbol_tokens):
        return False
    pairs = _target_pairs(tokens)
    for index, token in enumerate(tokens):
        if token.line != line or token.literal:
            continue
        matched = tokens[index:index + len(name)]
        if ([item.value for item in matched] == name
                and all(not item.literal and item.line == line for item in matched)):
            selected.extend(_selected_handler_bodies(tokens, index + len(name) - 1, pairs))
    # Do not guess between same-line occurrences, or silently accept an empty
    # one because another happens to perform work. Put them on separate lines.
    if len(selected) > 1:
        raise MigrationError('Target handler anchor is ambiguous on this line')
    return bool(selected) and pairs[selected[0]] == selected[0] + 1


def verify(project, source, graph, acs, *, run=False):
    from .quality_views import spec_inputs, target_inputs
    contract_hashes, product_hashes = spec_inputs(project), target_inputs(project)
    failures, observations = [], []
    verification_path = project / 'spec/verification/ios-behavior.json'
    verification_sha = digest(verification_path.read_bytes())
    spec = read_json(verification_path)
    if spec.get('schema_version') != 2 or spec.get('source_sha256') != graph['source_sha256']:
        raise MigrationError('Behavior cases must pin the current independent source snapshot')
    facts = {f['id']: f for f in graph['facts']}
    required = {f['id'] for f in graph['facts'] if f['kind'] in {'event', 'persistence'}}
    linked, covered = set(), set()
    for chain in spec.get('chains', []):
        ident = chain.get('source_fact')
        if ident not in required or ident in linked:
            failures.append({'rule': 'IOS.BEHAVIOR_CHAIN_ID', 'subject': ident}); continue
        linked.add(ident)
        keys = ['input', 'processing', 'feedback'] if facts[ident]['kind'] == 'event' else ['save', 'reload', 'business_effect']
        for key in keys:
            node = chain.get(key)
            try:
                if not isinstance(node, dict) or not isinstance(node.get('symbol'), str) or not node['symbol']:
                    raise MigrationError('Chain node requires a concrete target symbol')
                path = safe_child(project, node['path'])
                data = path.read_bytes()
                if node.get('sha256') != digest(data):
                    raise MigrationError('Target chain node hash is stale')
                text = data.decode('utf-8-sig')
                line = node.get('line')
                if type(line) is not int or not 1 <= line <= len(text.splitlines()) or node['symbol'] not in text.splitlines()[line - 1]:
                    raise MigrationError('Target symbol/line is not present')
                # A lexical empty-body check for this exact anchor only. It is
                # deliberately not exhaustive behavior or call-graph analysis.
                if _empty_target_handler(text, node['symbol'], line):
                    raise MigrationError('Empty target handler cannot implement a behavior chain')
            except (MigrationError, OSError, UnicodeError, KeyError, TypeError) as exc:
                failures.append({'rule': 'IOS.BEHAVIOR_NODE', 'subject': str(ident) + ':' + key, 'detail': str(exc)})
        if chain.get('review', {}).get('status') != 'reviewed' or not chain.get('review', {}).get('reviewer'):
            failures.append({'rule': 'IOS.BEHAVIOR_REVIEW', 'subject': ident})
    for ident in sorted(required - linked):
        failures.append({'rule': 'IOS.BEHAVIOR_CHAIN_MISSING', 'subject': ident})
    seen = set()
    target_before = snapshot(project)['sha256']
    for case in spec.get('cases', []):
        ident = case.get('id')
        if not isinstance(ident, str) or not re.fullmatch(r'[a-zA-Z0-9_-]+', ident) or ident in seen:
            failures.append({'rule': 'IOS.BEHAVIOR_CASE_ID', 'subject': str(ident)}); continue
        seen.add(ident)
        ids = case.get('ac_ids')
        if not isinstance(ids, list) or not ids or any(a not in acs for a in ids):
            failures.append({'rule': 'IOS.BEHAVIOR_CASE_AC', 'subject': ident}); continue
        if not all(acs[a]['judgment'] == case.get('runner') for a in ids):
            failures.append({'rule': 'IOS.BEHAVIOR_RUNNER', 'subject': ident}); continue
        if case.get('oracle', {}).get('source_fact') not in facts or 'expected' not in case.get('oracle', {}) or not case.get('oracle', {}).get('reviewer'):
            failures.append({'rule': 'IOS.INDEPENDENT_ORACLE_MISSING', 'subject': ident}); continue
        targets = case.get('target_hashes')
        if not isinstance(targets, dict) or not targets:
            failures.append({'rule': 'IOS.BEHAVIOR_TARGET_UNBOUND', 'subject': ident}); continue
        try:
            if any(digest(safe_child(project, path).read_bytes()) != expected for path, expected in targets.items()):
                raise MigrationError('Observed target inputs changed')
        except (MigrationError, OSError, TypeError) as exc:
            failures.append({'rule': 'IOS.BEHAVIOR_TARGET_STALE', 'subject': ident, 'detail': str(exc)}); continue
        command = case.get('command')
        timeout = case.get('timeout_seconds', 60)
        if not isinstance(command, list) or not command or any(not isinstance(v, str) or not v for v in command) or type(timeout) is not int or not 1 <= timeout <= 600:
            failures.append({'rule': 'IOS.BEHAVIOR_COMMAND', 'subject': ident}); continue
        observed = {'id': ident, 'ac_ids': ids, 'runner': case['runner'], 'status': 'not_run', 'command': command}
        if run:
            output = project / 'spec/reports/behavior' / ident
            output.mkdir(parents=True, exist_ok=True)
            try:
                proc = subprocess.run(command, cwd=project, input=json_bytes(case.get('input')), capture_output=True, timeout=timeout, shell=False)
                stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
            except subprocess.TimeoutExpired as exc:
                stdout, stderr, code = exc.stdout or b'', exc.stderr or b'', None
            except OSError as exc:
                stdout, stderr, code = b'', str(exc).encode(), None
            (output / 'stdout.log').write_bytes(stdout)
            (output / 'stderr.log').write_bytes(stderr)
            observed['exit_code'] = code
            try:
                import json
                actual = json.loads(stdout)
            except (ValueError, UnicodeError):
                actual = None
            passed = code == 0 and actual == case['oracle']['expected']
            observed.update(status='observed_pass' if passed else 'observed_fail', actual=actual,
                            stdout_sha256=digest(stdout), stderr_sha256=digest(stderr))
            if passed:
                covered.update(ids)
            else:
                failures.append({'rule': 'IOS.BEHAVIOR_OBSERVATION', 'subject': ident})
        observations.append(observed)
        if run:
            try:
                if any(digest(safe_child(project, path).read_bytes()) != expected for path, expected in targets.items()):
                    raise MigrationError('Observed target inputs changed during execution')
            except (MigrationError, OSError, TypeError) as exc:
                failures.append({'rule': 'IOS.BEHAVIOR_TARGET_CHANGED', 'subject': ident, 'detail': str(exc)})
    # Report whether invoked processes changed source/target rather than silently accepting side effects.
    if source_snapshot(source)['sha256'] != graph['source_sha256']:
        failures.append({'rule': 'IOS.BEHAVIOR_SOURCE_CHANGED', 'subject': 'source'})
    if (digest(verification_path.read_bytes()) != verification_sha
            or spec_inputs(project) != contract_hashes or target_inputs(project) != product_hashes):
        failures.append({'rule': 'IOS.BEHAVIOR_INPUT_CHANGED', 'subject': 'verification/spec/target'})
    pending = sorted(set(acs) - covered)
    report = {'schema_version': 2, 'status': 'FAIL' if failures else 'UNVERIFIED' if pending else 'PASS',
              'verification_sha256': verification_sha,
              'spec_input_hashes': contract_hashes, 'target_input_hashes': product_hashes,
              'source_sha256': graph['source_sha256'], 'target_before_sha256': target_before,
              'failures': failures, 'observations': observations, 'unverified_ac_ids': pending,
              'behavior_verified': not failures and not pending,
              'scope': 'declared cases and process observations; source oracle and device authenticity need independent review'}
    write_json(project / 'spec/reports/ios-behavior-check.json', report)
    return report, 2 if failures else 3 if pending else 0
