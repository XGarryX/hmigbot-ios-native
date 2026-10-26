"""Bounded native alternatives to declaration-shape structural heuristics.

These proofs concern source wiring and layout policy, never device rendering.
The upstream finding is retained. Unknown syntax and ambiguous bindings stay
findings; no project name, path whitelist, or reviewed hash grants an exemption.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid

from .behavior import _target_tokens, _target_pairs
from .core import read_json, safe_child, write_json, io_path
from .native_structural_evidence import EvidenceIndex, IDENT, _one, product_source_roots

SAFE_AREA_REFERENCE = ('https://raw.githubusercontent.com/openharmony/docs/'
    'OpenHarmony-6.0-Release/zh-cn/application-dev/reference/apis-arkui/'
    'arkui-ts/ts-universal-attributes-expand-safe-area.md')
IMAGE_REFERENCE = ('https://raw.githubusercontent.com/openharmony/arkui_ace_engine/'
    'OpenHarmony-6.0-Release/frameworks/core/components_ng/pattern/image/'
    'image_layout_algorithm.cpp')
SCROLL_CLIP_REFERENCE = ('https://raw.githubusercontent.com/openharmony/docs/'
    'OpenHarmony-6.0-Release/zh-cn/application-dev/reference/apis-arkui/'
    'arkui-ts/ts-container-scroll.md')


def _anchor(source, index, role):
    return {'role': role, 'file': source.relative, 'line': source.tokens[index].line,
            'sha256': hashlib.sha256(source.path.read_bytes()).hexdigest()}


def _modules(index):
    result = []
    for root in index.source_roots:
        main = root.parent
        config = main / 'module.json5'
        result.append((main, read_json(config)['module']))
    return result


def _main_sources(index):
    result = []
    for main, module in _modules(index):
        reference = module.get('pages', '')
        if not reference.startswith('$profile:'):
            continue
        path = main / 'resources/base/profile' / (reference.split(':', 1)[1] + '.json')
        pages = read_json(path).get('src', [])
        if not isinstance(pages, list):
            continue
        for page in pages:
            if isinstance(page, str):
                candidate = (main / 'ets' / (page + '.ets')).resolve()
                result.extend(s for s in index.sources if s.path == candidate)
    return result


def _regions(index, definition):
    """Real build plus bounded self calls and ArkUI builder arguments."""
    build = _one(definition.members.get('build', []))
    if build is None or not build.body:
        return []
    result, queue, seen = [], [build], set()
    values = definition.source.values
    while queue:
        member = queue.pop()
        if member.index in seen or not member.body:
            continue
        seen.add(member.index)
        begin, end = member.body
        result.append((begin, end))
        for cursor in range(begin + 1, end - 2):
            if values[cursor:cursor + 2] != ['this', '.']:
                continue
            target = _one(definition.members.get(values[cursor + 2], []))
            if target is None or not target.body:
                continue
            if values[cursor + 3:cursor + 4] == ['('] or 'Builder' in target.decorators:
                # An uncalled lambda stored in a method does not render.
                if not index._local_callable_contains(definition.source, begin, end, cursor):
                    queue.append(target)
    return result


def _entry_roots(index):
    roots = _main_sources(index)
    live = []
    for source in roots:
        candidates = []
        for definition in source.definitions:
            if definition.kind != 'struct':
                continue
            declaration = definition.start - 1
            while declaration >= 0 and source.values[declaration] != 'struct':
                declaration -= 1
            boundary = declaration - 1
            while boundary >= 0 and source.values[boundary] not in {';', '}'}:
                boundary -= 1
            prefix = source.values[boundary + 1:declaration]
            if any(prefix[i:i + 2] == ['@', 'Entry'] for i in range(len(prefix) - 1)):
                candidates.append(definition)
        # main_pages identifies a source file, not every struct in that file.
        # Ambiguous or missing entry decorators cannot seed reachability.
        if len(candidates) != 1:
            return []
        live.extend(candidates)
    return live


def _rendered(index):
    return {(owner.source.relative, owner.name) for owner, _ in _render_contexts(index)}


def static_resource_use(index, relative, name):
    """A same-file static Resource result must feed a rendered Image."""
    relative = relative.replace('\\', '/')
    definition = _one([d for d in index.definitions if d.source.relative == relative
                       and d.name == name and d.kind == 'class'])
    if definition is None:
        return None
    source, values = definition.source, definition.source.values
    live = _rendered(index)
    for owner in source.definitions:
        if (source.relative, owner.name) not in live or owner.kind != 'struct':
            continue
        for begin, end in _regions(index, owner):
            if index._shadowed_parameter(source, name, begin, end):
                continue
            for cursor in range(begin + 1, end - 6):
                if values[cursor:cursor + 4] != ['Image', '(', name, '.']:
                    continue
                method = _one(definition.members.get(values[cursor + 4], []))
                if (method is None or not method.static or method.kind != 'method'
                        or not method.body or [t.value for t in method.type_tokens] != ['Resource']):
                    continue
                call = cursor + 5
                finish = source.pairs.get(call)
                image_finish = source.pairs.get(cursor + 1)
                if values[call] != '(' or finish is None or image_finish != finish + 1:
                    continue
                if index._local_callable_contains(source, begin, end, cursor):
                    continue
                left, right = method.body
                returns = [i for i in range(left + 1, right) if values[i] == 'return']
                if not returns or any(values[i + 1:i + 3] != ['$r', '('] for i in returns):
                    continue
                return {'kind': 'same_file_static_resource_consumed_by_image',
                        'evidence': [_anchor(source, method.index, 'static-resource-definition'),
                                     _anchor(source, cursor, 'rendered-image-consumer')],
                        'source_visual_unverified': True}
    return None


def adapt_orphans(project, report):
    original = copy.deepcopy(report)
    result = copy.deepcopy(report)
    index, remaining, dispositions = EvidenceIndex(project), [], []
    for finding in report.get('orphans', []):
        proof = static_resource_use(index, finding.get('file', ''), finding.get('class_name', ''))
        if proof is None:
            remaining.append(finding)
        else:
            dispositions.append({'original_finding': finding, **proof})
    removed = len(report.get('orphans', [])) - len(remaining)
    result.update(orphans=remaining, original_report=original, native_dispositions=dispositions)
    for key in ('orphan_count', 'component_orphan_count'):
        if isinstance(result.get(key), int):
            result[key] = max(0, result[key] - removed)
    return result


def _new_value(index, source, start, end, expected):
    values = source.values
    if values[start:start + 1] != ['new'] or start + 2 >= end:
        return None
    if (index.definition(values[start + 1], source) != expected or values[start + 2] != '('
            or source.pairs.get(start + 2) != end - 1):
        return None
    if re.search(r'noop|unavailable|mock|stub', expected.name, re.I):
        return None
    return [_anchor(source, start, 'typed-constructor')]


def _singleton(index, source, start, end, expected):
    values = source.values
    if end - start != 3 or values[start + 1] != '.':
        return None
    if index.definition(values[start], source) != expected:
        return None
    getter = _one(expected.members.get(values[start + 2], []))
    if getter is None or getter.kind != 'getter' or not getter.static or not getter.body:
        return None
    if index.member_type(expected, getter) != expected:
        return None
    owner, vals = expected.source, expected.source.values
    begin, finish = getter.body
    returns = [i for i in range(begin + 1, finish) if vals[i] == 'return']
    if len(returns) != 1:
        return None
    position = returns[0]
    if vals[position + 1:position + 3] != [expected.name, '.']:
        return None
    field = _one(expected.members.get(vals[position + 3], []))
    if (field is None or not field.static or field.kind != 'field'
            or index.member_type(expected, field) != expected):
        return None
    writes = [i for i in range(len(vals) - 4)
              if vals[i:i + 4] == [expected.name, '.', field.name, '=']
              and vals[i + 4:i + 5] != ['=']]
    if len(writes) != 1 or not begin < writes[0] < finish:
        return None
    position = writes[0] + 4
    closing = owner.pairs.get(position + 2)
    if closing is None or _new_value(index, owner, position, closing + 1, expected) is None:
        return None
    return [_anchor(source, start, 'typed-singleton-use'),
            _anchor(owner, getter.index, 'singleton-getter'),
            _anchor(owner, writes[0], 'singleton-unique-initializer')]


def _slot_value(index, provider, start, end, expected, opening):
    direct = _new_value(index, provider, start, end, expected)
    if direct:
        return direct
    if end - start == 1 and IDENT.fullmatch(provider.values[start]):
        name, values = provider.values[start], provider.values
        candidates = [i for i in range(opening - 3) if values[i:i + 2] == ['const', name]
                      and values[i + 2:i + 3] == ['=']]
        if len(candidates) != 1:
            return None
        cursor = candidates[0] + 3
        finish = cursor
        while finish < opening and values[finish] != ';':
            finish = provider.pairs[finish] + 1 if finish in provider.pairs else finish + 1
        if finish >= opening:
            return None
        # Reject any additional declaration/assignment of the alias.
        object_keys = {left for left, _ in index._segments_object(provider, opening)}
        interface_fields = {member.index for definition in provider.definitions
                            if definition.kind == 'interface'
                            for members in definition.members.values() for member in members}
        for i in range(len(values) - 1):
            if values[i] == name and i != candidates[0] + 1:
                if (values[i + 1] in {'=', ':'} and values[i - 1] != '.'
                        and i not in object_keys | interface_fields):
                    return None
        proof = (_new_value(index, provider, cursor, finish, expected)
                 or _singleton(index, provider, cursor, finish, expected))
        if proof:
            return [_anchor(provider, candidates[0], 'unique-local-constructor-alias'), *proof]
        return None
    return _singleton(index, provider, start, end, expected)


def _top_level(source, body, position):
    begin, end = body
    return begin < position < end and not any(
        source.values[left] == '{' and begin < left < position < right <= end
        for left, right in source.pairs.items())


def _startup_before_ui(index, host, ability, factory):
    """A deliberately small lifecycle dominance proof, not token ordering.

    Accept the unconditional first onCreate assignment and either an immediate
    await or the exact nullable-startup guard used by that initialized field.
    Unknown branches/handlers/reassignments retain the assembly finding.
    """
    values = host.values
    oncreate = _one(ability.members.get('onCreate', []))
    onwindow = _one(ability.members.get('onWindowStageCreate', []))
    if oncreate is None or onwindow is None or not oncreate.body or not onwindow.body:
        return None
    first = oncreate.body[0] + 1
    if values[first:first + 2] != ['this', '.'] or values[first + 3:first + 6] != ['=', factory, '(']:
        return None
    closing = host.pairs.get(first + 5)
    if closing is None or values[closing + 1:closing + 2] != [';']:
        return None
    name = values[first + 2]
    field = _one(ability.members.get(name, []))
    if field is None or field.kind != 'field' or field.static or not field.type_tokens:
        return None
    if field.type_tokens[0].value != 'Promise':
        return None
    writes = [i for i in range(ability.start + 1, ability.end - 4)
              if values[i:i + 4] == ['this', '.', name, '=']
              and values[i + 4:i + 5] != ['=']]
    if writes != [first]:
        return None
    begin, end = onwindow.body
    cursor = begin + 1
    if values[cursor:cursor + 5] == ['await', 'this', '.', name, ';']:
        awaited, after = cursor, cursor + 5
    elif values[cursor:cursor + 2] == ['if', '(']:
        guard_end = host.pairs.get(cursor + 1)
        if guard_end is None or values[cursor + 2:guard_end] != ['this', '.', name, '!', '=', '=', 'undefined']:
            return None
        body = guard_end + 1
        body_end = host.pairs.get(body)
        if body_end is None or values[body] != '{' or values[body + 1:body_end] != ['await', 'this', '.', name, ';']:
            return None
        awaited, after = body + 1, body_end + 1
    else:
        return None
    loads = [i for i in range(begin + 1, end - 1) if values[i:i + 2] == ['loadContent', '(']]
    if not loads or any(i <= after or not _top_level(host, onwindow.body, i) for i in loads):
        return None
    if values[after:after + 1] == ['else']:
        return None
    return first, awaited


def assembly_binding(project, relative):
    index = EvidenceIndex(project)
    provider = _one([s for s in index.sources if s.relative == relative.replace('\\', '/')])
    if provider is None:
        return None
    binding = _one(provider.bindings.get('capabilityTable', []))
    if binding is None or not binding.exported or binding.kind not in {'const', 'let'}:
        return None
    types = [t.value for t in binding.type_tokens]
    interface = index.definition(types[0], provider) if len(types) == 1 else None
    if interface is None or interface.kind != 'interface' or not interface.members:
        return None
    values = provider.values
    producers = ([binding.initializer] if binding.initializer is not None else [])
    producers += [i + 2 for i in range(len(values) - 2)
                  if values[i:i + 2] == [binding.name, '=']
                  and (not i or values[i - 1] not in {'.', 'const', 'let', 'var'})]
    producers = sorted(set(producers))
    if len(producers) != 1 or values[producers[0]] != '{' or producers[0] not in provider.pairs:
        return None
    opening = producers[0]
    entry = index._producer_entry(provider, opening)
    if not entry:
        return None
    for i, value in enumerate(values):
        if value == binding.name and i != binding.index and i:
            if values[i - 1] in {'const', 'let', 'var'} or (
                    values[i + 1:i + 2] == [':'] and values[i - 1] in {'(', ','}):
                return None
    slots = {}
    for start, end in index._segments_object(provider, opening):
        if values[start + 1:start + 2] != [':'] or values[start] in slots:
            return None
        slots[values[start]] = (start + 2, end)
    if set(slots) != set(interface.members):
        return None
    proof = [_anchor(provider, binding.index, 'unique-exported-typed-binding'), *entry]
    for slot, members in interface.members.items():
        field = _one(members)
        expected = index.member_type(interface, field) if field else None
        if (expected is None or expected.kind != 'class' or not expected.members
                or re.search(r'noop|unavailable|mock|stub', expected.name, re.I)):
            return None
        # Use the existing binding proof for direct constructors.
        direct = index._binding_slot(provider, binding.name, slot)
        specific = direct[1] if direct else _slot_value(index, provider, *slots[slot], expected, opening)
        if not specific:
            return None
        proof.extend(specific)
    invocation = _one([e for e in entry if e.get('role') == 'producer-invocation'])
    factory = _one([e for e in entry if e.get('role') == 'producer-factory'])
    if invocation is None or factory is None or invocation.get('member') != 'onCreate':
        return None
    host = _one([s for s in index.sources if s.relative == invocation['file']])
    registered = []
    for main, module in _modules(index):
        for ability in module.get('abilities', []):
            if isinstance(ability, dict) and isinstance(ability.get('srcEntry'), str):
                registered.append((main / ability['srcEntry']).resolve())
    if host is None or host.path not in registered:
        return None
    ability = _one([d for d in host.definitions if d.name == invocation.get('class')])
    if ability is None or 'UIAbility' not in host.values[max(0, ability.start - 4):ability.start]:
        return None
    startup = _startup_before_ui(index, host, ability, factory['function'])
    if startup is None:
        return None
    consumers = []
    for source in index.sources:
        if source == provider:
            continue
        resolved = index._binding(source, binding.name)
        if resolved != (provider, binding):
            continue
        for i in range(len(source.values) - 2):
            if source.values[i:i + 2] == [binding.name, '.'] and source.values[i + 2] in slots:
                if index._shadowed_parameter(source, binding.name, 0, len(source.values) - 1):
                    continue
                consumers.append(_anchor(source, i, 'same-export-consumer'))
    if not consumers:
        return None
    return {'kind': 'typed_delayed_capability_object', 'slots': sorted(slots),
            'evidence': [*proof, _anchor(host, startup[0], 'unconditional-startup-installation'),
                         _anchor(host, startup[1], 'startup-awaited-before-ui'), *consumers],
            'source_visual_unverified': True}


def adapt_assembly(project, report):
    result = copy.deepcopy(report)
    remaining, dispositions = [], []
    for finding in report.get('findings', []):
        proof = assembly_binding(project, finding.get('file', '')) if finding.get('kind') == 'capability-table-missing' else None
        if proof:
            dispositions.append({'original_finding': finding, **proof})
        else:
            remaining.append(finding)
    result.update(original_report=copy.deepcopy(report), findings=remaining,
                  native_dispositions=dispositions)
    if dispositions:
        result['passed'] = not any(f.get('severity') == 'FAIL' for f in remaining)
    return result


def form_surfaces(index):
    surfaces = {}
    main_paths = {s.path for s in _main_sources(index)}
    for main, module in _modules(index):
        ui_paths = {(main / a['srcEntry']).resolve() for a in module.get('abilities', [])
                    if isinstance(a, dict) and isinstance(a.get('srcEntry'), str)}
        for extension in module.get('extensionAbilities', []):
            if not isinstance(extension, dict) or extension.get('type') != 'form':
                continue
            for metadata in extension.get('metadata', []):
                if not isinstance(metadata, dict) or metadata.get('name') != 'ohos.extension.form':
                    continue
                resource = metadata.get('resource', '')
                if not resource.startswith('$profile:'):
                    continue
                config = main / 'resources/base/profile' / (resource.split(':', 1)[1] + '.json')
                for form in read_json(config).get('forms', []):
                    if not isinstance(form, dict) or not isinstance(form.get('src'), str):
                        continue
                    path = (main / form['src']).resolve()
                    if not path.is_relative_to(main) or path in ui_paths | main_paths:
                        continue
                    source = _one([s for s in index.sources if s.path == path])
                    if source is None or source.imports:
                        continue
                    values = source.values
                    if ['@', 'Entry'] not in [values[i:i + 2] for i in range(len(values) - 1)]:
                        continue
                    if 'ComponentV2' in values or any(v in values for v in ('NavDestination', 'loadContent')):
                        continue
                    surfaces[source.relative] = {'kind': 'registered_form_surface',
                        'metadata_file': (main / 'module.json5').relative_to(index.project).as_posix(),
                        'form_profile': config.relative_to(index.project).as_posix(),
                        'evidence': [_anchor(source, 0, 'form-carrier')], 'source_visual_unverified': True}
    return surfaces


def _background_expansions(index):
    """Expansion is accepted only on a leaf Rect with no interactive modifiers."""
    live, proofs = _rendered(index), []
    for source in index.sources:
        values = source.values
        for cursor in range(len(values) - 2):
            if values[cursor:cursor + 3] != ['.', 'expandSafeArea', '(']:
                continue
            owner = _one([d for d in source.definitions if d.start < cursor < d.end])
            if owner is None or (source.relative, owner.name) not in live:
                return None
            candidates = []
            for i in range(owner.start + 1, cursor):
                if values[i:i + 3] != ['Rect', '(', ')']:
                    continue
                position, names = i + 3, []
                while position + 2 < len(values) and values[position] == '.' and values[position + 2] == '(':
                    if position + 2 not in source.pairs:
                        break
                    names.append(values[position + 1])
                    if position == cursor:
                        candidates.append((i, names.copy()))
                    position = source.pairs[position + 2] + 1
            if len(candidates) != 1:
                return None
            start, names = candidates[0]
            allowed = {'fill', 'width', 'height', 'expandSafeArea', 'hitTestBehavior', 'accessibilityLevel'}
            # Inspect the complete same-node chain, including modifiers after expansion.
            position = start + 3
            while position + 2 < len(values) and values[position] == '.' and values[position + 2] == '(':
                if values[position + 1] not in allowed or position + 2 not in source.pairs:
                    return None
                position = source.pairs[position + 2] + 1
            if values[position:position + 1] == ['{']:
                return None
            if not {'fill', 'width', 'height'} <= set(names):
                return None
            proofs.append(_anchor(source, start, 'reachable-background-only-expansion'))
    return proofs or None


TRANSFORMS = {'offset', 'position', 'translate'}


def _render_nodes(index, owner):
    source, values, nodes = owner.source, owner.source.values, []
    for begin, end in _regions(index, owner):
        for cursor in range(begin + 1, end - 1):
            if (not re.fullmatch(r'[A-Z][\w$]*', values[cursor]) or values[cursor + 1] != '('
                    or values[cursor - 1] in {'.', 'new', 'function'}):
                continue
            closing = source.pairs.get(cursor + 1)
            if closing is None:
                continue
            body, after = None, closing + 1
            if values[after:after + 1] == ['{'] and after in source.pairs:
                body, after = (after, source.pairs[after]), source.pairs[after] + 1
            modifiers = []
            while (after + 2 < len(values) and values[after] == '.'
                   and values[after + 2] == '(' and after + 2 in source.pairs):
                finish = source.pairs[after + 2]
                modifiers.append((after, values[after + 1], after + 3, finish))
                after = finish + 1
            nodes.append((cursor, body, modifiers))
    return nodes


def _sdk_scroll(index, owner):
    source, values = owner.source, owner.source.values
    if index.definition('Scroll', source) is not None or source.imports.get('Scroll') or source.bindings.get('Scroll'):
        return False
    if any(values[i:i + 2] == ['function', 'Scroll'] for i in range(len(values) - 1)):
        return False
    # Scroll is a global ArkUI constructor here. Any explicit import or local
    # binding makes that identity unknown, even if the spelling stays Scroll.
    for cursor in range(len(values) - 1):
        if values[cursor] == 'import' and values[cursor + 1] == '{':
            finish = source.pairs.get(cursor + 1)
            if finish is not None and 'Scroll' in values[cursor + 2:finish]:
                return False
    return not any(index._shadowed_parameter(source, 'Scroll', begin, end)
                   for begin, end in _regions(index, owner))


def _local_clip(index, owner, nodes, position):
    source, values = owner.source, owner.source.values
    for cursor, body, modifiers in nodes:
        if body is None or not body[0] < position < body[1]:
            continue
        if any(name in TRANSFORMS for _, name, _, _ in modifiers):
            continue
        clips = [(start, finish) for _, name, start, finish in modifiers if name == 'clip']
        explicit = bool(clips) and values[clips[-1][0]:clips[-1][1]] == ['true']
        default_scroll = not clips and values[cursor] == 'Scroll' and _sdk_scroll(index, owner)
        if not explicit and not default_scroll:
            continue
        if any(outer and outer[0] < body[0] < outer[1]
               and any(name in TRANSFORMS for _, name, _, _ in mods)
               for _, outer, mods in nodes):
            continue
        return {**_anchor(source, cursor, 'sdk-scroll-default-clip' if default_scroll else 'explicit-ancestor-clip'),
                'reference': SCROLL_CLIP_REFERENCE if default_scroll else SAFE_AREA_REFERENCE}
    return None


def _render_contexts(index):
    """Keep both bounded/unbounded occurrences of each actual rendered struct.

    A component rendered once inside Scroll and once outside it is not globally
    granted that Scroll's clip. Only real parent->child render calls propagate
    the clip, and every reachable unbounded occurrence remains represented.
    """
    queue, result, seen = [(root, None) for root in _entry_roots(index)], [], set()
    while queue:
        owner, inherited = queue.pop()
        identity = (owner.source.relative, owner.name, bool(inherited))
        if identity in seen:
            continue
        seen.add(identity)
        result.append((owner, inherited))
        source, values = owner.source, owner.source.values
        nodes = _render_nodes(index, owner)
        for begin, end in _regions(index, owner):
            for cursor in range(begin + 1, end - 1):
                if values[cursor + 1] != '(' or not IDENT.fullmatch(values[cursor]):
                    continue
                if values[cursor - 1] in {'.', 'new', 'function'}:
                    continue
                child = index.definition(values[cursor], source)
                if child is None or child.kind != 'struct' or index._local_callable_contains(source, begin, end, cursor):
                    continue
                clip = inherited or _local_clip(index, owner, nodes, cursor)
                proof = None if clip is None else {'clip': clip,
                    'render_call': _anchor(source, cursor, 'clipped-component-render-call'),
                    'parent': owner.name, 'child': child.name}
                queue.append((child, proof))
    return result


def _render_transform_analysis(index):
    findings, bounded = [], []
    for owner, inherited in _render_contexts(index):
        source, values = owner.source, owner.source.values
        regions, nodes = _regions(index, owner), _render_nodes(index, owner)
        positions = sorted({cursor for begin, end in regions for cursor in range(begin + 1, end - 2)
            if values[cursor] == '.' and values[cursor + 1] in TRANSFORMS and values[cursor + 2] == '('})
        for position in positions:
            clip = inherited or _local_clip(index, owner, nodes, position)
            evidence = {**_anchor(source, position, 'bounded-rendered-transform' if clip else 'unbounded-rendered-transform'),
                        'class': owner.name, 'modifier': values[position + 1]}
            if clip:
                bounded.append({**evidence, 'clip_chain': clip})
            else:
                findings.append({**evidence,
                    'reason': 'No unchanged real clipping ancestor proves this transformed content stays in host bounds.'})
    return findings, bounded


def safearea_report(project, original_report):
    index = EvidenceIndex(project)
    result = copy.deepcopy(original_report)
    result.update(original_report=copy.deepcopy(original_report), native_dispositions=[],
                  source_visual_unverified=True)
    # The official API10+ default applies only while no code overrides that policy.
    profile = read_json(index.project / 'build-profile.json5')
    versions = [p.get('compatibleSdkVersion') for p in profile.get('app', {}).get('products', [])]
    def api(value):
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.search(r'\((\d+)\)$', value)
            return int(match[1]) if match else int(value.split('.')[0]) if re.fullmatch(r'\d+(?:\.\d+)*', value) else 0
        return 0
    if not versions or any(api(v) < 10 for v in versions):
        return result
    overrides = {'setWindowLayoutFullScreen', 'setLayoutFullScreen', 'setWindowSystemBarEnable',
                 'ignoreLayoutSafeArea', 'setDecorVisible', 'setImmersiveModeEnabledState',
                 'createWindow', 'createSubWindow', 'createSubWindowWithOptions'}
    for source in index.sources:
        if any(v in overrides and source.values[i + 1:i + 2] == ['(']
               for i, v in enumerate(source.values)):
            return result
    backgrounds = _background_expansions(index)
    if backgrounds is None:
        return result
    registered = []
    for main, module in _modules(index):
        for ability in module.get('abilities', []):
            if isinstance(ability, dict) and isinstance(ability.get('srcEntry'), str):
                path = (main / ability['srcEntry']).resolve()
                registered.extend(s for s in index.sources if s.path == path)
    if not registered or not _main_sources(index):
        return result
    if any('loadContent' not in source.values or 'UIAbility' not in source.values for source in registered):
        return result
    mains, forms = {s.path for s in _main_sources(index)}, form_surfaces(index)
    for source in index.sources:
        is_entry = any(source.values[i:i + 2] == ['@', 'Entry'] for i in range(len(source.values) - 1))
        if is_entry and source.path not in mains and source.relative not in forms:
            return result
    transforms, bounded_transforms = _render_transform_analysis(index)
    if transforms:
        result['native_unresolved'] = transforms
        return result
    result['native_dispositions'] = [{'kind': 'api10_default_system_safe_area_with_leaf_background',
        'reference': SAFE_AREA_REFERENCE, 'api_versions': [api(v) for v in versions],
        'evidence': backgrounds, 'forms': list(form_surfaces(index).values()),
        'scope': 'static system status/navigation bar policy; visual and cutout geometry unverified',
        'bounded_rendered_transforms': bounded_transforms,
        'cutout_avoidance_configured': all(any(m.get('name') == 'avoid_cutout' and m.get('value') == 'true'
            for m in module.get('metadata', []) if isinstance(m, dict)) for _, module in _modules(index)),
        'source_visual_unverified': True}]
    # The recipe-only original fail is superseded only by the complete bounded policy proof.
    if (original_report.get('engine') == 'python-native' and original_report.get('returncode') == 1
            and not original_report.get('stderr_excerpt') and not original_report.get('error')
            and isinstance(original_report.get('stdout_excerpt'), str)):
        text = original_report['stdout_excerpt']
        failures = [line for line in text.splitlines() if line.startswith('❌ L')]
        full_report = '扫描结果' in text and '校验 FAIL' in text
        known_files = {s.path for s in index.sources}
        for line in failures:
            if line.startswith('❌ L3'):
                match = re.search(r'\[([^\]]+)\]', line)
                path = match[1].replace('\\', '/') if match else ''
                if not any((root / path).resolve() in known_files for root in index.source_roots):
                    full_report = False
        if full_report and failures and all('缺 setWindowLayoutFullScreen' in line or '未发现任何安全区响应' in line
                                            for line in failures):
            result.update(passed=True, returncode=0)
    return result


def source_bounded_image(project, relative, line):
    """One typed transient PixelMap and its frozen Swift max-height contract."""
    from .native_icon_scope import _offset_tokens
    relative = relative.replace('\\', '/')
    index = EvidenceIndex(project)
    source = _one([s for s in index.sources if s.relative == relative.replace('\\', '/')])
    if source is None:
        return None
    tokens = _offset_tokens(source.text)
    values, pairs = [t.value for t in tokens], _target_pairs(tokens)
    calls = [i for i, t in enumerate(tokens[:-1]) if t.value == 'Image' and t.line == line
             and values[i + 1] == '(' and (not i or values[i - 1] not in {'.', '?'})]
    if len(calls) != 1:
        return None
    position = calls[0]
    closing = pairs.get(position + 1)
    if closing != position + 5 or values[position + 2:position + 4] != ['this', '.']:
        return None
    name = values[position + 4]
    owner = _one([d for d in source.definitions if d.start < position < d.end and d.kind == 'struct'])
    field = _one(owner.members.get(name, [])) if owner else None
    if field is None or 'Param' not in field.decorators or [t.value for t in field.type_tokens] != ['image', '.', 'PixelMap', '|', 'undefined']:
        return None
    if not re.search(r"(?m)^import\s*\{\s*image\s*\}\s*from\s*['\"]@kit.ImageKit['\"]", source.text):
        return None
    modifiers, cursor = {}, closing + 1
    while cursor + 2 < len(tokens) and values[cursor] == '.' and values[cursor + 2] == '(':
        finish = pairs.get(cursor + 2)
        if finish is None or values[cursor + 1] in modifiers:
            return None
        modifiers[values[cursor + 1]] = (cursor + 3, finish)
        cursor = finish + 1
    if any(key in modifiers for key in ('height', 'size', 'aspectRatio', 'clip', 'onClick')):
        return None
    width, cap, fit = (modifiers.get(key) for key in ('width', 'constraintSize', 'objectFit'))
    if None in (width, cap, fit):
        return None
    if width[1] - width[0] != 1 or source.text[tokens[width[0]].start:tokens[width[0]].end] not in ("'100%'", '"100%"'):
        return None
    if values[fit[0]:fit[1]] != ['ImageFit', '.', 'Contain']:
        return None
    capvalues = values[cap[0]:cap[1]]
    if len(capvalues) != 5 or capvalues[:3] != ['{', 'maxHeight', ':'] or capvalues[-1] != '}':
        return None
    amount = capvalues[3]
    if not re.fullmatch(r'[1-9]\d*', amount):
        return None
    config = read_json(index.project / '.migbot/config.json')
    if config.get('source_platform') != 'ios' or not isinstance(config.get('ios'), str):
        return None
    contracts = []
    for path in (index.project / 'spec/baseline/ui').glob('*.md'):
        content = path.read_text(encoding='utf-8-sig')
        if relative not in content or 'maxHeight' + amount not in content:
            continue
        match = re.search(r'role: view\s+path: ([^\s]+)\s+symbol: ([\w$]+)', content)
        if match:
            contracts.append((path, match[1], match[2]))
    if len(contracts) != 1:
        return None
    contract, source_relative, symbol = contracts[0]
    swift = safe_child(Path(config['ios']).resolve(), source_relative)
    raw = swift.read_text(encoding='utf-8-sig')
    stokens, spairs = _target_tokens(raw), None
    svalues = [t.value for t in stokens]
    spairs = _target_pairs(stokens)
    definitions = [i for i in range(len(svalues) - 5) if svalues[i:i + 4] == ['struct', symbol, ':', 'View']]
    if len(definitions) != 1:
        return None
    begin = definitions[0] + 4
    if svalues[begin] != '{' or begin not in spairs:
        return None
    end = spairs[begin]
    if not any(svalues[i:i + 6] == ['var', name, ':', 'UIImage', '?', '='] for i in range(begin + 1, end - 5)):
        return None
    pattern = ['Image', '(', 'uiImage', ':', name, ')', '.', 'resizable', '(', ')', '.',
               'scaledToFit', '(', ')', '.', 'frame', '(', 'maxHeight', ':', amount, ')']
    matches = [i for i in range(begin + 1, end - len(pattern) + 1) if svalues[i:i + len(pattern)] == pattern]
    if len(matches) != 1:
        return None
    return {'kind': 'source_max_height_contain', 'max_height': int(amount), 'reference': IMAGE_REFERENCE,
            'evidence': [_anchor(source, position, 'same-image-bounded-chain'),
                {'role': 'frozen-ui-contract', 'file': contract.relative_to(index.project).as_posix(),
                 'sha256': hashlib.sha256(contract.read_bytes()).hexdigest()},
                {'role': 'swift-scaled-to-fit-max-height', 'file': source_relative,
                 'line': stokens[matches[0]].line, 'sha256': hashlib.sha256(swift.read_bytes()).hexdigest()}],
            'source_visual_unverified': True}


def assembly_main(arguments=None):
    from .runtime_timeouts import timeout_for, timeout_evidence
    from .process_runtime import run as run_owned_process
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--output-json', type=Path, required=True)
    args, unknown = parser.parse_known_args(sys.argv[1:] if arguments is None else arguments)
    root = Path(__file__).resolve().parents[2]
    original = root / 'vendor/hmigbot/skills/arkts-structural-closure/scripts/assembly_gate.py'
    command = [sys.executable, str(original), '--project-root', str(args.project_root),
               '--output-json', str(args.output_json), *unknown]
    try:
        limit = timeout_for('assembly')
        if os.name == 'nt':
            raw = run_owned_process(command, cwd=None, env=os.environ.copy(), timeout=limit)
            process = subprocess.CompletedProcess(raw.args, raw.returncode,
                raw.stdout.decode('utf-8', errors='replace'), raw.stderr.decode('utf-8', errors='replace'))
        else:
            from .portable_helper import run
            process = run(original, command[2:], capture_output=True, encoding='utf-8', errors='replace', timeout=limit)
    except subprocess.TimeoutExpired as exc:
        evidence = timeout_evidence(exc)
        sys.stdout.write(evidence['stdout'])
        sys.stderr.write(evidence['stderr'])
        write_json(args.output_json, {'detector': 'assembly', 'passed': False, 'skipped': False,
                                     'error': 'Original assembly detector timed out', 'process_output': evidence})
        return 124
    sys.stdout.write(process.stdout)
    sys.stderr.write(process.stderr)
    if args.output_json.is_file():
        result = adapt_assembly(args.project_root, read_json(args.output_json))
        write_json(args.output_json, result)
        return 0 if result.get('passed') else process.returncode or 1
    return process.returncode or 2


def stage_runtime(skills, root=None):
    """Install adapters only in a disposable original-engine scripts layout."""
    root = Path(root) if root else Path(__file__).resolve().parents[2]
    scripts = Path(skills) / 'arkts-structural-closure/scripts'
    for filename, kind in [('gen_capability_manifest.py', 'gen'), ('capability_ledger_gate.py', 'gate')]:
        legacy = root / 'vendor/hmigbot/skills/arkts-structural-closure/scripts' / filename
        (scripts / filename).write_text('import sys\n'
            f'sys.path.insert(0, {str(root / "src")!r})\n'
            'from hmigbot_ios.capability_manifest import main\n'
            f'raise SystemExit(main({kind!r}, {str(legacy)!r}))\n', encoding='utf-8')
    (scripts / 'assembly_gate.py').write_text('import sys\n'
        f'sys.path.insert(0, {str(root / "src")!r})\n'
        'from hmigbot_ios.native_pipeline_semantics import assembly_main\n'
        'raise SystemExit(assembly_main())\n', encoding='utf-8')


DETECTORS = frozenset({'assembly', 'audit', 'binding', 'carrier', 'deadshell', 'hittest',
    'icon', 'immersive', 'ledger', 'literal', 'orphans', 'resname', 'theme'})


def _outside_main_ets(project, roots, relative):
    """Prove an actual unaliased ETS is outside every configured main root."""
    if not isinstance(relative, str) or not relative or '\x00' in relative:
        raise ValueError('Scope finding has an unknown source path')
    spelling = relative.replace('\\', '/')
    parts = spelling.split('/')
    path = Path(spelling)
    if ('..' in parts or any(':' in part and not (
            position == 0 and path.is_absolute() and re.fullmatch(r'[A-Za-z]:', part))
            for position, part in enumerate(parts))):
        raise ValueError('Scope finding path contains traversal or an ambiguous stream')
    lexical = io_path(path if path.is_absolute() else project / path)
    if not lexical.is_absolute() or not lexical.is_relative_to(project):
        raise ValueError('Scope finding path escapes the project')
    resolved = lexical.resolve()
    # A source-root spelling cannot be scoped away through an alias, and an
    # outside alias resolving into the source root remains a real source item.
    if any(lexical.is_relative_to(root) or resolved.is_relative_to(root) for root in roots):
        return None
    if not resolved.is_relative_to(project) or not lexical.is_file():
        raise ValueError('Scope finding has no project-owned real source file')
    if lexical.suffix != '.ets':
        return None  # Resource/other detector domains retain their own findings.
    for part in (lexical, *lexical.parents):
        if part == project:
            break
        if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
            raise ValueError('Scope finding uses an ambiguous linked source path')
    if (os.path.normcase(str(lexical)) != os.path.normcase(str(resolved))
            or lexical.stat().st_nlink != 1):
        raise ValueError('Scope finding has an ambiguous aliased source identity')
    return {'kind': 'outside_configured_main_ets', 'file': relative,
            'resolved_relative': resolved.relative_to(project).as_posix(),
            'file_sha256': hashlib.sha256(resolved.read_bytes()).hexdigest(),
            'source_roots': [root.relative_to(project).as_posix() for root in roots],
            'reason': 'Both lexical and real source paths are outside every declared module main ETS root.'}


def source_scope_reports(project, audit, orphans):
    """Partition only proved outside-source audit/orphan rows; retain raw data."""
    project = Path(project).resolve()
    roots = product_source_roots(project)
    effective_audit, effective_orphans = copy.deepcopy(audit), copy.deepcopy(orphans)
    audit_rows, orphan_rows = audit.get('findings'), orphans.get('orphans')
    if not isinstance(audit_rows, list) or not isinstance(orphan_rows, list):
        raise ValueError('Malformed original source-scope report')
    if any(not isinstance(row, dict) for row in audit_rows + orphan_rows):
        raise ValueError('Malformed original source-scope finding')
    summary = audit.get('summary')
    if not isinstance(summary, dict) or type(orphans.get('orphan_count')) is not int:
        raise ValueError('Original source-scope counts are missing')
    if orphans['orphan_count'] != len(orphan_rows):
        raise ValueError('Original orphan count does not match its findings')
    for key in ('FAIL', 'WARN'):
        if type(summary.get(key)) is not int or summary[key] != sum(
                row.get('severity_at_scope') == key for row in audit_rows):
            raise ValueError('Original audit severity counts differ from its findings')
    for level in ('L1', 'L2', 'L3', 'L4', 'L5'):
        if level in summary and (type(summary[level]) is not int or summary[level] != sum(
                row.get('level') == level for row in audit_rows)):
            raise ValueError('Original audit level counts differ from its findings')
    def component(row):
        # Match the original graph's documented UI path hints. This is only
        # count reconciliation; no directory name grants a scope exemption.
        if not isinstance(row.get('file'), str):
            raise ValueError('Original orphan has an unknown source path')
        parts = row['file'].replace('\\', '/').split('/')[:-1]
        return any(part in {'components', 'views', 'widgets', 'dialogs', 'dialog'} for part in parts)
    if 'component_orphan_count' in orphans and (
            type(orphans['component_orphan_count']) is not int
            or orphans['component_orphan_count'] != sum(component(row) for row in orphan_rows)):
        raise ValueError('Original component orphan count differs from its findings')
    audit_keep, orphan_keep, audit_scope, orphan_scope = [], [], [], []
    for row in audit_rows:
        if not isinstance(row, dict):
            raise ValueError('Malformed original audit finding')
        proof = _outside_main_ets(project, roots, row.get('file'))
        if (proof and row.get('severity_at_scope') in {'FAIL', 'WARN'}
                and row.get('level') in {'L1', 'L2', 'L3', 'L4', 'L5'}
                and type(row.get('line')) is int and row['line'] > 0
                and isinstance(row.get('subtype'), str)):
            audit_scope.append({'original_finding': copy.deepcopy(row), **proof})
        else:
            audit_keep.append(row)
    for row in orphan_rows:
        if not isinstance(row, dict):
            raise ValueError('Malformed original orphan finding')
        proof = _outside_main_ets(project, roots, row.get('file'))
        if proof and isinstance(row.get('class_name'), str) and isinstance(row.get('reason'), str):
            orphan_scope.append({'original_finding': copy.deepcopy(row), **proof})
        else:
            orphan_keep.append(row)
    effective_audit.update(original_report=copy.deepcopy(audit), findings=audit_keep,
                           native_scope_dispositions=audit_scope)
    effective_audit['summary'] = {**summary,
        'FAIL': sum(row.get('severity_at_scope') == 'FAIL' for row in audit_keep),
        'WARN': sum(row.get('severity_at_scope') == 'WARN' for row in audit_keep)}
    for level in ('L1', 'L2', 'L3', 'L4', 'L5'):
        if level in summary:
            effective_audit['summary'][level] = sum(row.get('level') == level for row in audit_keep)
    effective_orphans.update(original_report=copy.deepcopy(orphans), orphans=orphan_keep,
        orphan_count=len(orphan_keep), native_scope_dispositions=orphan_scope)
    if 'component_orphan_count' in orphans:
        effective_orphans['component_orphan_count'] = sum(component(row) for row in orphan_keep)
    return effective_audit, effective_orphans


def _inputs_snapshot(project):
    """Bind proofs and all original detectors to one stable declared product."""
    index = EvidenceIndex(project)
    paths = {project / 'build-profile.json5', project / '.migbot/config.json'}
    app_scope=project/'AppScope'
    if app_scope.is_dir():paths.update(path for path in app_scope.rglob('*') if path.is_file())
    for root in index.source_roots:
        # Main source/resources are small application inputs, never build/cache.
        paths.update(p for p in root.parent.rglob('*') if p.is_file())
    from .consumed_inputs import baseline_inputs as consumed_inputs
    try:
        contracts=consumed_inputs(project,'domains')
    except (OSError,ValueError,KeyError,TypeError) as exc:
        # Static detectors remain runnable while the source baseline is being
        # authored. Capture only existing formal objects, not arbitrary notes.
        from .artifact_contract import catalog, _artifact_paths
        from .consumed_inputs import PRODUCT_RECORDS
        formal={project/'spec/baseline'/name for name in PRODUCT_RECORDS}
        for entry in catalog()['spec']:formal.update(_artifact_paths(project,entry))
        contracts={p.relative_to(project).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(formal) if p.is_file()}
        contracts['@partial-contract']=hashlib.sha256(str(exc).encode()).hexdigest()
    from .artifact_contract import catalog, _artifact_paths
    for entry in catalog()['plan']['artifacts']:
        for path in _artifact_paths(project,entry):
            if path.is_file():contracts[path.relative_to(project).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    return {**{p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(paths) if p.is_file()}, **contracts}


def _cache_inputs(project, arguments):
    """Conservative closed-engine read scope; it affects reuse, never admission."""
    from .quality_views import target_inputs
    inputs=target_inputs(project)
    # Requested result files are outputs, not product inputs. Do not allow this
    # exception inside a configured product source/resource directory.
    roots=product_source_roots(project)
    for flag in ('--state-file','--output-json'):
        if flag in arguments:
            path=Path(arguments[arguments.index(flag)+1]).resolve()
            if (path.is_relative_to(project) and not path.is_relative_to(project/'AppScope')
                    and not any(path.is_relative_to(root.parent) for root in roots)):
                inputs.pop(path.relative_to(project).as_posix(),None)
    for folder in ('spec/baseline','spec/ref'):
        base=project/folder
        for path in base.rglob('*') if base.is_dir() else []:
            if path.is_file():inputs[path.relative_to(project).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    for name in ('spec/placeholder-registry.md','spec/execution/base-contracts.md','spec/execution/capability-manifest.json'):
        path=project/name
        if path.is_file():inputs[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    return inputs


def _detector_rules():
    """Pin the actual host payload and adapters, not unrelated platform engines."""
    import platform
    root=Path(__file__).resolve().parents[2]
    paths={Path(__file__)}
    for name in ('native_structural_evidence.py','native_structural.py','native_helpers.py',
                 'native_pipeline_runtime.py','native_literal_scope.py','detector_cache.py'):
        paths.add(root/'src/hmigbot_ios'/name)
    system={'Darwin':'macos','Windows':'windows','Linux':'linux'}.get(platform.system())
    arch='arm64' if platform.machine().lower() in {'arm64','aarch64'} else 'x64'
    for folder in ('skills/arkts-structural-closure/scripts',
                   'vendor/hmigbot/skills/arkts-structural-closure/scripts'):
        scripts=root/folder
        paths.update(scripts.glob('*.py'))
        payload=scripts/'bin'/f'{system}-{arch}'/'_entry.dist'
        if payload.is_dir():paths.update(p for p in payload.rglob('*') if p.is_file())
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths) if p.is_file()}


def _replace_argument(arguments, name, value):
    result = list(map(str, arguments))
    positions = [i for i, item in enumerate(result) if item == name]
    if len(positions) != 1 or positions[0] + 1 >= len(result):
        raise ValueError('Native pipeline requires one explicit ' + name)
    result[positions[0] + 1] = str(value)
    return result


def pipeline_iterate(arguments, run_raw):
    """Original 13 raw detectors, bounded views, original public loop verdict.

    This follows the existing native slice/group consumer protocol. Raw output
    is immutable per invocation; the only persisted adaptation is a structural
    loop record with auditable exact dispositions. Scheduler ledgers are never
    read as writable state here. Finalize remains the original engine operation.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('operation', choices=['iterate'])
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--state-file', type=Path, required=True)
    parser.add_argument('--output-json', type=Path)
    parser.add_argument('--mode', choices=['pipeline'], required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--max-iter', type=int)
    args, extra_arguments = parser.parse_known_args(arguments)
    project, state_path = args.project_root.resolve(), args.state_file.resolve()
    before = _inputs_snapshot(project)
    state = read_json(state_path) if state_path.is_file() else {
        'history': [], 'max_iter': args.max_iter or 8, 'mode': 'pipeline', 'target': args.target}
    if state.get('mode') != 'pipeline' or state.get('target') != args.target or not isinstance(state.get('history'), list):
        raise ValueError('Native pipeline structural state identity differs')
    iteration = len(state['history'])
    from .detector_cache import identity as cache_identity, load as load_cache, save as save_cache
    cache_before=_cache_inputs(project,arguments)
    signature=cache_identity(cache_before,_detector_rules(),arguments)
    cache_path=state_path.parent/'native-detector-cache'/(signature+'.json')
    # Unknown engine parameters may reference inputs this adapter cannot bind.
    # Execute normally, but do not reuse a result for an unmodeled read scope.
    cache_eligible=state_path.is_relative_to(project/'spec') and not extra_arguments
    cached=load_cache(project,cache_path,signature) if cache_eligible else None
    reused=cached is not None
    if cached:
        raw_directory,process=cached
        raw_state,raw_output=raw_directory/'state.json',raw_directory/'result.json'
    else:
        raw_directory = state_path.parent / 'native-pipeline-raw' / (
            state_path.stem + '-iter' + str(iteration) + '-' + uuid.uuid4().hex)
        raw_directory.mkdir(parents=True)
        raw_state, raw_output = raw_directory / 'state.json', raw_directory / 'result.json'
        raw_arguments = _replace_argument(arguments, '--state-file', raw_state)
        if '--output-json' in raw_arguments:
            raw_arguments = _replace_argument(raw_arguments, '--output-json', raw_output)
        else:
            raw_arguments.extend(['--output-json', str(raw_output)])
        process = run_raw(raw_arguments)
    if process.returncode not in (0, 1, 2) or not raw_state.is_file() or not raw_output.is_file():
        return process
    raw = read_json(raw_state)
    raw_result = read_json(raw_output)
    if raw.get('mode') != 'pipeline' or len(raw.get('history', [])) != 1:
        raise ValueError('Original pipeline did not produce one complete raw iteration')
    current = copy.deepcopy(raw['history'][0])
    if (set(current.get('detectors_run', [])) != DETECTORS
            or set(current.get('detectors_effective', [])) != DETECTORS
            or current.get('detectors_skipped') != []):
        raise ValueError('Original pipeline did not execute all 13 detectors')
    reports = {}
    for detector in sorted(DETECTORS):
        path = raw_directory / (detector + '-pipeline-iter0.json')
        if not path.is_file():
            raise ValueError('Missing original pipeline detector report: ' + detector)
        reports[detector] = read_json(path)
        if reports[detector].get('skipped'):
            raise ValueError('Original pipeline detector was skipped: ' + detector)
    raw_files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in raw_directory.iterdir() if p.is_file()}
    effective = copy.deepcopy(reports)
    effective['audit'], scoped_orphans = source_scope_reports(project, reports['audit'], reports['orphans'])
    effective['orphans'] = adapt_orphans(project, scoped_orphans)
    effective['immersive'] = safearea_report(project, reports['immersive'])
    # Assembly may already be adapted by its real staged subprocess shim.
    if not reports['assembly'].get('native_dispositions'):
        effective['assembly'] = adapt_assembly(project, reports['assembly'])
    resolved, audit_resolved = [], []
    for disposition in effective['audit']['native_scope_dispositions']:
        item = disposition['original_finding']
        if item['severity_at_scope'] == 'FAIL':
            audit_resolved.append([item['file'], item['line'], item['subtype']])
    for disposition in (effective['orphans']['native_dispositions']
                        + effective['orphans']['native_scope_dispositions']):
        item = disposition['original_finding']
        resolved.append([item['file'], 0, 'pipeline-orphan:' + item['class_name'] + ':' + item['reason']])
    if not reports['immersive'].get('passed') and effective['immersive'].get('passed'):
        resolved.append(['__immersive__', 0, 'pipeline-immersive-fail'])
    if not reports['assembly'].get('passed') and effective['assembly'].get('passed'):
        for disposition in effective['assembly']['native_dispositions']:
            item = disposition['original_finding']
            resolved.append([item['file'], 0, 'assembly:' + item['kind'] + ':' + item.get('class', '-')])
    fingerprint = copy.deepcopy(current.get('fingerprint', []))
    for row in audit_resolved + resolved:
        if fingerprint.count(row) != 1:
            raise ValueError('Native disposition does not match exactly one original fingerprint: ' + str(row))
        fingerprint.remove(row)
    actions = current.get('wiring_repair_actions')
    if not isinstance(actions, int) or actions < len(resolved):
        raise ValueError('Original pipeline finding count differs from exact native dispositions')
    if (type(current.get('audit_fail')) is not int
            or current['audit_fail'] != reports['audit']['summary']['FAIL']
            or type(current.get('audit_warn')) is not int
            or current['audit_warn'] != reports['audit']['summary']['WARN']):
        raise ValueError('Original pipeline audit counts differ from original audit findings')
    current.update(iter=iteration, wiring_repair_actions=actions - len(resolved), fingerprint=fingerprint,
        audit_fail=effective['audit']['summary']['FAIL'], audit_warn=effective['audit']['summary']['WARN'])
    scope_dispositions = (effective['audit']['native_scope_dispositions']
                          + effective['orphans']['native_scope_dispositions'])
    scope_hashes = {row['resolved_relative']: row['file_sha256'] for row in scope_dispositions}
    if any(hashlib.sha256(io_path(project / path).read_bytes()).hexdigest() != digest
           for path, digest in scope_hashes.items()):
        raise ValueError('Scoped-out source bytes changed during native pipeline detection')
    after = _inputs_snapshot(project)
    if before != after:
        raise ValueError('Product or frozen source inputs changed during native pipeline detection')
    if raw_files != {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in raw_directory.iterdir() if p.is_file()}:
        raise ValueError('Original raw detector evidence changed during adaptation')
    if not reused and cache_eligible and cache_before==_cache_inputs(project,arguments):
        save_cache(project,cache_path,signature,raw_directory,process)
    # Use the unchanged original public runner for all verdict/stall constants.
    from .native_helpers import original
    from .native_structural import _run_report
    runner = {'history': state['history'], 'max_iter': args.max_iter or state.get('max_iter', 8),
              'current': current}
    with tempfile.TemporaryDirectory(prefix='native-pipeline-runner-') as directory:
        input_path = Path(directory) / 'input.json'
        write_json(input_path, runner)
        verdict, verdict_process = _run_report(original, 'loop_runner.py',
            ['--state-file', input_path], Path(directory) / 'verdict.json')
    if verdict.get('verdict') not in {'CONVERGED', 'CONTINUE', 'STALLED', 'REGRESSED', 'EXHAUSTED'}:
        raise ValueError('Original pipeline runner returned an unknown verdict')
    output_paths = {}
    for detector, report in effective.items():
        destination = state_path.parent / (detector + '-pipeline-iter' + str(iteration) + '.json')
        if destination.exists():
            from .core import json_bytes
            if destination.read_bytes()!=json_bytes(report):
                destination=state_path.parent/'native-pipeline-effective'/(state_path.stem+'-iter'+str(iteration)+'-'+signature[:12])/(detector+'.json')
                if destination.exists() and destination.read_bytes()!=json_bytes(report):
                    raise ValueError('Effective detector evidence identity collision: '+str(destination))
        if not destination.exists():write_json(destination, report)
        output_paths[detector] = str(destination)
    audit = {'schema_version': 'native-pipeline-dispositions/1', 'iteration': iteration,
        'raw_state': str(raw_state), 'raw_output': str(raw_output), 'raw_files_sha256': raw_files,
        'raw_verdict': raw_result.get('verdict'), 'resolved_fingerprints': audit_resolved + resolved,
        'scope_disposition_files_sha256': scope_hashes,
        'original_audit_fail': reports['audit']['summary']['FAIL'],
        'effective_audit_fail': current['audit_fail'],
        'original_finding_count': actions, 'effective_finding_count': current['wiring_repair_actions'],
        'source_inputs_sha256': after, 'original_runner_verdict': verdict,
        'source_visual_unverified': True, 'all_original_detectors_executed': sorted(DETECTORS),
        'detector_evidence_reused':reused,'detector_input_signature':signature,
        'executed_this_invocation':[] if reused else sorted(DETECTORS),
        'source_contract_readiness':'partial' if '@partial-contract' in before else 'existing-consumed-inputs',
        'scope':'Structural detector evidence only; source contract completeness and runtime observation remain independent'}
    audit_path = state_path.parent / ('native-pipeline-dispositions-iter' + str(iteration) + '.json')
    if audit_path.exists():
        audit_path=state_path.parent/'native-pipeline-dispositions'/(state_path.stem+'-iter'+str(iteration)+'-'+uuid.uuid4().hex+'.json')
    write_json(audit_path, audit)
    current['native_dispositions_report'] = str(audit_path)
    state.update(history=[*state['history'], current], max_iter=runner['max_iter'], last_verdict=verdict,
                 mode='pipeline', target=args.target)
    write_json(state_path, state)
    output = {'mode': 'pipeline', 'target': args.target, 'iteration': iteration,
        **{key: verdict[key] for key in ('verdict', 'escalation', 'reason')},
        'current_state': {'audit_fail': current.get('audit_fail', 0),
            'wiring_repair_actions': current['wiring_repair_actions'],
            'handoff_escape_hatches': current.get('handoff_escape_hatches', 0),
            'total_fail': current.get('audit_fail', 0) + current['wiring_repair_actions'] + current.get('handoff_escape_hatches', 0)},
        'dispatch_prompt': '' if verdict['verdict'] == 'CONVERGED' else (
            'Repair remaining original findings; source-backed native dispositions are recorded separately.\n'
            + json.dumps(fingerprint, ensure_ascii=False)),
        'detector_json_paths': output_paths, 'state_file': str(state_path),
        'native_dispositions_report': str(audit_path), 'source_visual_unverified': True,
        'detector_evidence_reused':reused,'detector_input_signature':signature}
    if args.output_json:
        write_json(args.output_json, output)
        stdout = process.stdout
    else:
        stdout = process.stdout + '\n' + json.dumps(output, ensure_ascii=False, indent=2) + '\n'
    return subprocess.CompletedProcess(process.args,
        0 if verdict['verdict'] == 'CONVERGED' else 1 if verdict['verdict'] == 'CONTINUE' else 2,
        stdout, process.stderr)
