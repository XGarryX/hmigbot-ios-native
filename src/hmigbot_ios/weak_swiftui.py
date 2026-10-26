"""Bounded, tool-owned weak parsing for standalone drafts after native failure.

This is neither Swift syntax validation nor a source-harness fallback. Unknown
page constructs are rejected rather than skipped; outputs retain native errors.
"""
import json
import re

from .swiftui import Unsupported, tokenize
from .core import MigrationError


def weak_tokens(text):
    try:
        tokens = tokenize(text.removeprefix('\ufeff').replace('\r\n', '\n').replace('\r', '\n'))
    except MigrationError as exc:
        raise Unsupported('weak parser: ' + str(exc)) from exc
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for token in tokens:
        if token.kind == 'string':
            continue
        if token.value in {'(', '[', '{'}:
            stack.append(token.value)
        elif token.value in pairs:
            if not stack or stack.pop() != pairs[token.value]:
                raise Unsupported(f'weak parser: mismatched delimiter at line {token.line}')
    if stack:
        raise Unsupported('weak parser: unclosed delimiter')
    return tokens


class _WeakViewParser:
    def __init__(self, tokens):
        self.tokens, self.pos, self.states = tokens, 0, {}

    def peek(self):
        return self.tokens[self.pos].value if self.pos < len(self.tokens) else '<eof>'

    def error(self, message):
        line = self.tokens[min(self.pos, len(self.tokens) - 1)].line if self.tokens else 1
        raise Unsupported(f'weak parser line {line}: {message}; found {self.peek()}')

    def take(self, expected=None):
        if self.pos == len(self.tokens) or expected is not None and self.peek() != expected:
            self.error(f'expected {expected}')
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def accept(self, value):
        if self.peek() == value:
            self.pos += 1
            return True
        return False

    def separator(self):
        previous = self.tokens[self.pos - 1]
        if not self.accept(';') and self.pos < len(self.tokens) and self.tokens[self.pos].line <= (previous.end_line or previous.line):
            self.error('expected a declaration separator')

    def identifier(self):
        token = self.take()
        if token.kind != 'identifier' or token.value in {
            'build', 'constructor', 'aboutToAppear', 'aboutToDisappear', 'Index',
            'Text', 'Button', 'VStack', 'HStack', 'ZStack', 'Spacer', 'Divider',
            'class', 'struct', 'interface', 'function', 'private', 'public', 'this', 'var', 'let',
        }:
            self.error('unsupported or target-colliding identifier')
        return token.value

    def number(self, integer=False):
        sign = -1 if self.accept('-') else 1
        raw = self.take().value
        if len(raw) > 32 or not re.fullmatch(r'\d+' if integer else r'\d+(?:\.\d+)?', raw):
            self.error('expected numeric literal')
        value = sign * (int(raw) if '.' not in raw else float(raw))
        if abs(value) > 2**53 - 1:
            self.error('number exceeds exact ArkTS integer range')
        return value

    def text_literal(self, interpolate=False):
        token = self.take()
        if token.kind != 'string' or token.hash_count or token.quote_count == 3:
            self.error('weak drafts support ordinary single-line strings only')
        raw, pieces, start = token.value[1:-1], [], 0
        for match in re.finditer(r'\\\(([^)]*)\)', raw):
            if not interpolate or match.group(1) not in self.states:
                self.error('only declared integer-state interpolation is supported')
            try:
                prefix = json.loads('"' + raw[start:match.start()] + '"')
            except json.JSONDecodeError:
                self.error('unsupported Swift string escape')
            pieces.extend([{'literal': prefix}, {'state': match.group(1)}])
            start = match.end()
        try:
            pieces.append({'literal': json.loads('"' + raw[start:] + '"')})
        except json.JSONDecodeError:
            self.error('unsupported Swift string escape')
        return pieces

    def parse(self):
        while self.accept('import'):
            self.take('SwiftUI')
            self.separator()
        self.take('struct')
        name = self.identifier()
        self.take(':'); self.take('View'); self.take('{')
        while self.accept('@'):
            self.take('State'); self.accept('private'); self.take('var')
            state = self.identifier()
            if self.accept(':'):
                self.take('Int')
            self.take('=')
            initial = self.number(integer=True)
            if state in self.states:
                self.error('duplicate state')
            self.states[state] = initial
            self.separator()
        for value in ('var', 'body', ':', 'some', 'View', '{'):
            self.take(value)
        root = self.node()
        self.take('}'); self.take('}')
        if self.peek() != '<eof>':
            self.error('additional declarations are outside the weak page rule')
        return {'name': name, 'states': self.states, 'root': root,
                'rule': 'weak-swiftui-literal-and-int-state/1',
                'limitations': ['Weak Python draft after official parsing failed; Swift syntax and semantics are unverified',
                                'Layout, localization, compilation and behavior require independent validation']}

    def node(self, depth=0):
        if depth >= 64:
            self.error('weak view nesting exceeds 64')
        start = self.take()
        kind = start.value
        node = {'kind': kind, 'line': start.line, 'modifiers': [], 'children': []}
        if kind in {'VStack', 'HStack', 'ZStack'}:
            if self.accept('(') and not self.accept(')'):
                self.take('spacing'); self.take(':')
                if kind == 'ZStack':
                    self.error('ZStack spacing is not supported')
                node['spacing'] = self.number()
                self.take(')')
            self.take('{')
            while self.peek() not in {'}', '<eof>'}:
                node['children'].append(self.node(depth + 1))
            self.take('}')
        elif kind in {'Text', 'Image', 'Button'}:
            self.take('(')
            if kind == 'Text' and self.accept('verbatim'):
                self.take(':'); node['verbatim'] = True
            pieces = self.text_literal(interpolate=kind == 'Text')
            if kind == 'Image':
                node['asset_name'] = ''.join(p['literal'] for p in pieces)
            else:
                node['text'] = pieces
            self.take(')')
            if kind == 'Button':
                self.take('{')
                state = self.identifier()
                if state not in self.states:
                    self.error('button needs declared integer state')
                operation = self.take().value
                if operation not in {'+=', '-=', '='}:
                    self.error('unsupported action')
                node['action'] = {'state': state, 'operator': operation, 'value': self.number(integer=True)}
                self.take('}')
        elif kind in {'Spacer', 'Divider'}:
            self.take('('); self.take(')')
        else:
            self.error(f'unsupported view {kind}')
        while self.accept('.'):
            modifier = self.take().value
            self.take('(')
            if modifier == 'padding':
                value = self.number()
                if value < 0:
                    self.error('negative padding is unsupported')
                node['modifiers'].append({'name': 'padding', 'value': value})
            elif modifier == 'frame':
                seen = set()
                while True:
                    axis = self.take().value
                    if axis not in {'width', 'height'} or axis in seen:
                        self.error('frame requires unique width/height literals')
                    seen.add(axis); self.take(':')
                    value = self.number()
                    if value < 0:
                        self.error('negative dimensions are unsupported')
                    node['modifiers'].append({'name': axis, 'value': value})
                    if not self.accept(','):
                        break
            else:
                self.error(f'unsupported modifier {modifier}')
            self.take(')')
        names = [m['name'] for m in node['modifiers']]
        if len(names) != len(set(names)):
            self.error('repeated layout modifiers need composition-aware lowering')
        return node


def parse_weak_view(tokens):
    return _WeakViewParser(tokens).parse()
