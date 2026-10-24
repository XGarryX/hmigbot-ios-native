"""Bounded Objective-C declaration inventory, never compiler-resolved storage.

Properties are declarations, not proof of an ivar. The closed grammar records
declared ivars and lexical synthesis candidates, preserves assignment locations,
and diagnoses unsupported declarators rather than inventing a field name. Default
values describe zero-initialized instance storage, not the result of an init or
lifecycle method. A lexical assignment is not evidence that its branch executed.
"""
from __future__ import annotations


OWNERSHIP = {'copy', 'strong', 'weak', 'assign', 'retain', 'unsafe_unretained',
             '__strong', '__weak', '__unsafe_unretained', '__autoreleasing'}
QUALIFIERS = OWNERSHIP | {'const', 'volatile', 'nullable', 'nonnull', '_Nullable',
                          '_Nonnull', '__kindof', '__block'}
SCALARS = {'char', 'short', 'int', 'long', 'signed', 'unsigned', 'float', 'double',
           'NSInteger', 'NSUInteger', 'CGFloat', 'NSTimeInterval', 'size_t', 'ssize_t'}
LIFECYCLE = {'viewDidLoad', 'loadView', 'viewWillAppear:', 'viewDidAppear:',
             'viewWillDisappear:', 'viewDidDisappear:', 'awakeFromNib', 'dealloc',
             'viewWillTransitionToSize:withTransitionCoordinator:'}
PROPERTY_ATTRIBUTES = {'atomic', 'nonatomic', 'readonly', 'readwrite', 'assign',
                       'retain', 'copy', 'strong', 'weak', 'unsafe_unretained',
                       'class', 'nullable', 'nonnull', 'null_unspecified',
                       'null_resettable', 'direct'}


def _match(tokens, start, opening='(', closing=')'):
    depth = 0
    for i in range(start, len(tokens)):
        if tokens[i].value == opening:
            depth += 1
        elif tokens[i].value == closing:
            depth -= 1
            if not depth:
                return i
    return None


def _words(tokens):
    return ' '.join(t.value for t in tokens)


def _split(tokens, delimiter=','):
    parts, start, depth = [], 0, 0
    for i, token in enumerate(tokens):
        if token.value in {'(', '[', '{', '<'}:
            depth += 1
        elif token.value in {')', ']', '}', '>'}:
            depth -= 1
        elif token.value == delimiter and not depth:
            parts.append(tokens[start:i]); start = i + 1
    return parts + [tokens[start:]]


def _declarations(tokens):
    """Closed object/scalar/pointer/block grammar; reject arrays and bitfields."""
    # A simple block declarator has a single named ^ slot. Return and parameter
    # tokens are retained verbatim; block parameter names are never declarations
    # of the containing Objective-C instance.
    values = [t.value for t in tokens]
    if '^' in values:
        caret = values.index('^')
        if (caret < 2 or caret + 3 >= len(tokens) or values[caret - 1] != '(' or
                tokens[caret + 1].kind != 'identifier' or values[caret + 2:caret + 4] != [')', '(']):
            return None
        end = _match(tokens, caret + 3)
        if end != len(tokens) - 1 or not _valid_type(tokens[:caret - 1]):
            return None
        name = values[caret + 1]
        return [(name, _words(tokens[:caret + 1] + tokens[caret + 2:]))]
    if not tokens or any(t.kind != 'identifier' and t.value not in {'*', '<', '>', ','} for t in tokens):
        return None
    pieces = _split(tokens)
    result, base = [], None
    for piece in pieces:
        # UI_APPEARANCE_SELECTOR is a trailing annotation, not the property's name.
        if piece and piece[-1].value == 'UI_APPEARANCE_SELECTOR':
            piece = piece[:-1]
        if len(piece) < (2 if base is None else 1) or piece[-1].kind != 'identifier':
            return None
        name = piece[-1].value
        type_tokens = piece[:-1]
        if base is None:
            if not type_tokens:
                return None
            if not _valid_type(type_tokens):
                return None
            base = list(type_tokens)
            while base and base[-1].value == '*':
                base.pop()
        else:
            if any(t.value not in {'*', *QUALIFIERS} for t in type_tokens):
                return None
            type_tokens = base + list(type_tokens)
        result.append((name, _words(type_tokens)))
    return result


def _valid_type(tokens):
    """Reject trailing macro identifiers and syntax outside the bounded type grammar."""
    names, depth, pointer = [], 0, False
    for token in tokens:
        v = token.value
        if v == '<':
            depth += 1
        elif v == '>':
            depth -= 1
            if depth < 0:
                return False
        elif v == '*' and not depth:
            pointer = True
        elif token.kind == 'identifier':
            if not depth and v not in QUALIFIERS:
                if pointer:
                    return False
                names.append(v)
        elif v != ',' or not depth:
            if v != '*':
                return False
    return (depth == 0 and bool(names) and
            (len(names) == 1 or set(names) <= SCALARS or
             len(names) == 2 and names[0] in {'struct', 'enum', 'union'}))


def _annotations(tokens):
    """Strip only known trailing annotations, preserving their complete tokens."""
    known = {'UI_APPEARANCE_SELECTOR', 'API_AVAILABLE'}
    start = next((i for i, t in enumerate(tokens) if t.value in known), len(tokens))
    head, annotations, i = tokens[:start], [], start
    while i < len(tokens):
        if tokens[i].value == 'UI_APPEARANCE_SELECTOR':
            annotations.append(tokens[i].value); i += 1
        elif tokens[i].value == 'API_AVAILABLE' and i + 1 < len(tokens) and tokens[i + 1].value == '(':
            end = _match(tokens, i + 1)
            if end is None:
                return tokens, []
            annotations.append(_words(tokens[i:end + 1])); i = end + 1
        else:
            return tokens, []
    return head, annotations


def _property_attributes(tokens):
    """Unexpanded attribute macros may change storage/class semantics; fail closed."""
    attributes, accessors = [], {}
    for part in _split(tokens):
        values = [t.value for t in part]
        if len(part) == 1 and values[0] in PROPERTY_ATTRIBUTES:
            pass
        elif (len(part) == 3 and values[:2] == ['getter', '='] and
              part[2].kind == 'identifier'):
            accessors['getter'] = values[2]
        elif (len(part) == 4 and values[:2] == ['setter', '='] and
              part[2].kind == 'identifier' and values[3] == ':'):
            accessors['setter'] = values[2] + ':'
        else:
            return None
        attributes.append(_words(part))
    return attributes, accessors


def _zero(type_):
    if '^' in type_.split():
        return 'nil'
    values, depth = [], 0
    for v in type_.split():
        if v == '<':
            depth += 1
        elif v == '>':
            depth -= 1
        elif not depth and v not in QUALIFIERS:
            values.append(v)
    if not values:
        return None
    if values == ['BOOL']:
        return 'NO'
    if values == ['bool'] or values == ['_Bool']:
        return 'false' if values == ['bool'] else '0'
    if values[0] == 'Class':
        return 'Nil'
    if values[0] == 'id':
        return 'nil'
    if '*' in values:
        # C/opaque pointers are null pointers, not Objective-C object references.
        return 'NULL' if values[0] in SCALARS | {'void', 'struct', 'union', 'SEL'} or values.count('*') != 1 else 'nil'
    if set(values) <= SCALARS:
        return '0'
    return None  # Unknown typedef/aggregate: do not guess its representation.


def _issue(file, token, message):
    return {'rule': 'IOS.OBJC_STATE_UNRESOLVED', 'path': file['path'],
            'line': token.line, 'message': message}


def _methods(tokens, start):
    """Return a method's selector, parameters, body and following token position."""
    close = _match(tokens, start + 1)
    if close is None or close + 1 >= len(tokens):
        return None
    i, signature = close + 1, []
    while i < len(tokens) and tokens[i].value not in {'{', ';'}:
        signature.append(tokens[i]); i += 1
    if i == len(tokens):
        return None
    selector = ''.join(signature[n].value + ':' for n in range(len(signature) - 1)
                       if signature[n].kind == 'identifier' and signature[n + 1].value == ':')
    if not selector:
        selector = signature[0].value if signature else 'unresolved'
    parameters = set()
    for n in range(len(signature) - 1):
        if signature[n].value == ':' and signature[n + 1].value == '(':
            end = _match(signature, n + 1)
            if end is not None and end + 1 < len(signature) and signature[end + 1].kind == 'identifier':
                parameters.add(signature[end + 1].value)
        elif signature[n].value == ':' and signature[n + 1].kind == 'identifier':
            parameters.add(signature[n + 1].value)  # Objective-C permits omitted id parameter types.
    if tokens[i].value == ';':
        return selector, parameters, None, i + 1
    end = _match(tokens, i, '{', '}')
    if end is None:
        return None
    return selector, parameters, tokens[i + 1:end], end + 1


def _parse(file, tokens, contexts):
    declarations, methods, syntheses, dynamics, implemented, issues = [], [], [], [], [], []
    # The shared Swift lexer does not delimit C character constants. Reject this
    # file's state inference instead of letting '{' / '}' join separate writes.
    # Comments and string tokens are already isolated by the lexer.
    character = next((t for t in tokens if t.value == "'" and t.kind != 'string'), None)
    if character is not None:
        return declarations, methods, syntheses, dynamics, implemented, [
            _issue(file, character, 'C/Objective-C character literal needs a character-aware provider; state inference withheld')]
    owner, container, category, i = None, None, None, 0
    while i < len(tokens):
        v = tokens[i].value
        if v == '@' and i + 1 < len(tokens):
            directive = tokens[i + 1].value
            if directive in {'interface', 'implementation', 'protocol'}:
                if i + 2 >= len(tokens) or tokens[i + 2].kind != 'identifier':
                    i += 2; continue
                # @protocol(Name) is an expression; @protocol A, B; is forward-only.
                if directive == 'protocol' and (i + 3 == len(tokens) or tokens[i + 3].value in {',', ';'}):
                    i += 3; continue
                owner, container, category, i = tokens[i + 2].value, directive, None, i + 3
                if i < len(tokens) and tokens[i].value == '(':
                    end = _match(tokens, i)
                    if end is None:
                        issues.append(_issue(file, tokens[i], 'Unbalanced Objective-C category declaration'))
                        break
                    category = _words(tokens[i + 1:end])
                    i = end + 1
                if container == 'implementation' and category in {None, ''}:
                    implemented.append((owner, contexts))
                # The class header can contain a superclass and protocol/generic list.
                while i < len(tokens) and tokens[i].value not in {'{', '@', '-', '+'}:
                    i += 1
                if i < len(tokens) and tokens[i].value == '{':
                    end = _match(tokens, i, '{', '}')
                    if end is None:
                        issues.append(_issue(file, tokens[i], 'Unbalanced Objective-C ivar declaration block'))
                        break
                    ivar_tokens = tokens[i + 1:end]
                    cleaned, n = [], 0
                    while n < len(ivar_tokens):
                        if (ivar_tokens[n].value == '@' and n + 1 < len(ivar_tokens) and
                                ivar_tokens[n + 1].value in {'private', 'public', 'protected', 'package'}):
                            n += 2
                        else:
                            cleaned.append(ivar_tokens[n]); n += 1
                    if container != 'protocol':
                        for part in _split(cleaned, ';'):
                            if not part:
                                continue
                            parsed = _declarations(part)
                            if parsed is None:
                                issues.append(_issue(file, part[0], 'Unsupported Objective-C ivar declarator; explicit review required'))
                            else:
                                for name, type_ in parsed:
                                    declarations.append({'file': file, 'contexts': contexts, 'owner': owner,
                                        'symbol': name, 'line': part[0].line, 'end_line': part[-1].line,
                                        'category': category, 'value': {'storage': 'objc_ivar', 'type': type_,
                                            'attributes': [], 'ownership': next((w for w in type_.split() if w in OWNERSHIP), 'unspecified')}})
                    i = end + 1
                continue
            if directive == 'end':
                owner, container, category = None, None, None
                i += 2; continue
            if owner and directive in {'property', 'synthesize', 'dynamic'}:
                start, end = i, i + 2
                while end < len(tokens) and tokens[end].value != ';':
                    end += 1
                if end == len(tokens):
                    issues.append(_issue(file, tokens[start], 'Unterminated Objective-C state declaration'))
                    break
                declaration = tokens[i + 2:end]
                if directive == 'property' and container != 'protocol':
                    attributes = []
                    accessors = {}
                    if declaration and declaration[0].value == '(':
                        attr_end = _match(declaration, 0)
                        if attr_end is None:
                            issues.append(_issue(file, tokens[start], 'Unbalanced Objective-C property attributes'))
                            i = end + 1; continue
                        parsed_attributes = _property_attributes(declaration[1:attr_end])
                        if parsed_attributes is None:
                            issues.append(_issue(file, tokens[start], 'Unknown/malformed Objective-C property attributes; consume provider expansion or review explicitly'))
                            i = end + 1; continue
                        attributes, accessors = parsed_attributes
                        declaration = declaration[attr_end + 1:]
                    declaration, annotations = _annotations(declaration)
                    parsed = _declarations(declaration)
                    if parsed is None or len(parsed) != 1:
                        issues.append(_issue(file, tokens[start], 'Unsupported Objective-C property declarator; explicit review required'))
                    else:
                        name, type_ = parsed[0]
                        declarations.append({'file': file, 'contexts': contexts, 'owner': owner, 'symbol': name,
                            'line': tokens[start].line, 'end_line': tokens[end].line, 'category': category, 'accessors': accessors,
                            'value': {'storage': 'objc_property', 'type': type_, 'attributes': attributes, 'annotations': annotations,
                                      'ownership': next((a for a in attributes if a in OWNERSHIP), 'unspecified')}})
                elif container == 'implementation':
                    for part in _split(declaration):
                        if directive == 'dynamic' and len(part) == 1:
                            dynamics.append((owner, part[0].value, contexts))
                        elif directive == 'synthesize' and len(part) in {1, 3}:
                            if len(part) == 1 or part[1].value == '=':
                                syntheses.append((owner, part[0].value, part[-1].value, contexts))
                i = end + 1; continue
        if owner and v in {'-', '+'} and i + 1 < len(tokens) and tokens[i + 1].value == '(':
            parsed = _methods(tokens, i)
            if parsed is None:
                issues.append(_issue(file, tokens[i], 'Unbalanced Objective-C method while locating state assignments'))
                break
            selector, params, body, end = parsed
            if body is not None and container == 'implementation':
                methods.append({'file': file, 'contexts': contexts, 'owner': owner, 'selector': selector,
                                'instance': v == '-', 'parameters': params, 'body': body, 'category': category})
            i = end; continue
        i += 1
    return declarations, methods, syntheses, dynamics, implemented, issues


def _compatible(a, b):
    # A header include has a different instance number from its translation unit.
    # Unit identity is sufficient to keep separately observed branch views apart.
    return a is None or b is None or bool({c['unit'] for c in a} & {c['unit'] for c in b})


def _assignments(declaration, methods, backing):
    found = []
    name, owner = declaration['symbol'], declaration['owner']
    for method in methods:
        if not method['instance'] or method['owner'] != owner or not _compatible(declaration['contexts'], method['contexts']):
            continue
        body, shadowed = method['body'], set(method['parameters'])
        # Conservatively treat a declaration anywhere in this method as shadowing
        # a bare name. A shadowed self also prevents receiver/implicit-ivar binding.
        for n, t in enumerate(body):
            if t.value not in {backing, 'self'} or n == 0:
                continue
            previous = body[n - 1]
            typeof_declaration = False
            if previous.value == ')':
                depth, p = 1, n - 2
                while p >= 0:
                    depth += body[p].value == ')'
                    depth -= body[p].value == '('
                    if depth == 0:
                        typeof_declaration = p > 0 and body[p - 1].value in {'typeof', '__typeof', '__typeof__', 'decltype'}
                        break
                    p -= 1
            if ((previous.kind == 'identifier' and previous.value not in {'return', 'throw', 'case'}) or
                    previous.value == '*' and n >= 2 and body[n - 2].kind == 'identifier' or typeof_declaration):
                shadowed.add(t.value)
        if 'self' in shadowed:
            continue
        values = [t.value for t in body]
        for i, token in enumerate(body):
            if token.value != '=' or i == 0:
                continue
            lhs = i - 1
            receiver = None
            if lhs >= 2 and values[lhs - 2] == 'self' and values[lhs - 1] in {'.', '->'}:
                if lhs < 3 or values[lhs - 3] not in {'.', '->'}:
                    if values[lhs - 1] == '.' and values[lhs] == name and declaration['value']['storage'] == 'objc_property':
                        receiver = 'self.' + name
                    elif values[lhs - 1] == '->' and values[lhs] == backing:
                        receiver = 'self->' + backing
            elif (backing and values[lhs] == backing and backing not in shadowed and
                  (lhs == 0 or values[lhs - 1] not in {'.', '->', '*', '&'})):
                receiver = backing
            if receiver is None:
                continue
            end, depth = i + 1, 0
            while end < len(body):
                v = values[end]
                if v in {')', ']', '}'}:
                    if depth == 0:
                        break
                    depth -= 1
                elif v in {'(', '[', '{'}:
                    depth += 1
                elif v == ';' and depth == 0:
                    break
                end += 1
            if end == i + 1:
                continue
            selector = method['selector']
            phase = ('initializer' if selector == 'init' or selector.startswith('init') and len(selector) > 4 and selector[4].isupper()
                     else 'lifecycle' if selector in LIFECYCLE else 'method')
            item = {'path': method['file']['path'], 'line': token.line, 'end_line': body[end - 1].line,
                    'method': selector, 'phase': phase, 'receiver': receiver,
                    'expression': _words(body[i + 1:end]), 'control_flow': 'lexical_only'}
            if item not in found:
                found.append(item)
    return found


def extract_states(inputs):
    """inputs: (snapshot file, active lexical tokens, build contexts) tuples."""
    declarations, methods, syntheses, dynamics, implemented, issues = [], [], [], [], [], []
    for file, tokens, contexts in inputs:
        d, m, s, dy, im, errors = _parse(file, tokens, contexts)
        declarations.extend(d); methods.extend(m); syntheses.extend(s)
        dynamics.extend(dy); implemented.extend(im); issues.extend(errors)
    for declaration in declarations:
        value, owner, name = declaration['value'], declaration['owner'], declaration['symbol']
        backing = name if value['storage'] == 'objc_ivar' else None
        binding = 'declared_ivar' if backing else 'unresolved'
        contexts = declaration['contexts']
        dynamic = any(o == owner and n == name and _compatible(contexts, c) for o, n, c in dynamics)
        if value['storage'] == 'objc_property' and declaration['category'] in {None, ''} and 'class' not in value['attributes'] and not dynamic:
            aliases = {ivar for o, n, ivar, c in syntheses if o == owner and n == name and _compatible(contexts, c)}
            if len(aliases) == 1:
                backing, binding = next(iter(aliases)), 'explicit_synthesize'
            elif len(aliases) > 1:
                issues.append({'rule': 'IOS.OBJC_STATE_UNRESOLVED', 'path': declaration['file']['path'],
                               'line': declaration['line'], 'message': 'Conflicting lexical backing ivars across build contexts'})
            elif any(o == owner and _compatible(contexts, c) for o, c in implemented):
                getter = declaration['accessors'].get('getter', name)
                setter = declaration['accessors'].get('setter', 'set' + name[0].upper() + name[1:] + ':')
                selectors = {m['selector'] for m in methods if m['owner'] == owner and m['instance']
                             and m['category'] in {None, ''} and _compatible(contexts, m['contexts'])}
                if getter not in selectors or 'readonly' not in value['attributes'] and setter not in selectors:
                    backing, binding = '_' + name, 'lexical_auto_synthesis_candidate'
        initial = _zero(value['type']) if backing else None
        value.update(initializer=initial, initializer_basis='objc_instance_zero_initialization' if backing else 'unresolved_storage',
                     storage_binding=binding, backing_ivar=backing,
                     assignments=_assignments(declaration, methods, backing))
    return declarations, issues
