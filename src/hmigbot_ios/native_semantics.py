"""Validate native source facts without pretending to infer program semantics."""
from pathlib import Path
import re

from .core import MigrationError, read_json, safe_child
from .source_scope import source_anchor_info

LANGUAGES = {'swift', 'objc', 'objcxx', 'c', 'cpp'}
FRAMEWORKS = {'swiftui', 'uikit', 'ib', 'other', 'nonvisual'}
COMMON = {'entrypoints', 'data_flow', 'error_behavior'}
PAGE = {'identity', 'composition', 'layout', 'state_ownership', 'events', 'navigation', 'accessibility'}
FEATURE = {'state_transitions', 'concurrency', 'lifetime', 'persistence', 'platform_capabilities'}
SWIFTUI = {'modifier_order', 'binding_flow', 'environment', 'task_lifetime'}
UIKIT = {'controller_lifecycle', 'layout_constraints', 'event_connections', 'delegates'}
SWIFT = {'optionality', 'value_reference_semantics', 'concurrency_model'}
OBJC = {'nullability', 'ownership', 'dynamic_dispatch'}


def required_facts(kind, languages, frameworks):
    fields = COMMON | (PAGE if kind == 'page' else FEATURE)
    if kind == 'page' and 'swiftui' in frameworks:
        fields |= SWIFTUI
    if kind == 'page' and frameworks & {'uikit', 'ib'}:
        fields |= UIKIT
    if 'swift' in languages:
        fields |= SWIFT
    if languages & {'objc', 'objcxx'}:
        fields |= OBJC
    return fields


def validate_native_facts(source, project, documents, known, fail, *, projection=None):
    """Emit findings for missing native dimensions, stale claims or invalid evidence.

    documents is the exact {stable_id: (kind, source_paths)} spec inventory. Evidence
    must stay within each spec's declared anchors; unrelated real files cannot justify it.
    This checks the contract and provenance, not the truth of a natural-language claim.
    """
    path = project / 'spec/baseline/ios-semantics.json'
    if not path.is_file():
        fail('IOS.NATIVE_FACTS_MISSING', path.name, 'Read native-facts.md and retain framework/language semantics')
        return
    data = read_json(path)
    validate_native_payload(source, project, documents, known, fail, data, projection=projection)


def validate_native_payload(source, project, documents, known, fail, data, *, projection=None):
    """Validate an authored candidate with the same rules as the on-disk gate."""
    if projection is not None:
        projection.validate_frozen_inputs(project)
    path = project / 'spec/baseline/ios-semantics.json'
    if not isinstance(data, dict) or data.get('schema_version') not in {1, 2} or data.get('source_platform') != 'ios' or not isinstance(data.get('documents'), list):
        fail('IOS.NATIVE_FACTS_SCHEMA', path.name, 'Expected native facts v1/v2 with source_platform=ios and documents list')
        return
    seen = set()
    for item in data['documents']:
        if not isinstance(item, dict):
            fail('IOS.NATIVE_FACTS_SCHEMA', path.name, 'Document must be an object')
            continue
        ident = item.get('id')
        if not isinstance(ident, str) or ident not in documents or ident in seen:
            fail('IOS.NATIVE_FACTS_ID', str(ident), 'Unknown, missing or duplicate page/feature ID')
            continue
        seen.add(ident)
        kind, anchors = documents[ident]
        if item.get('kind') != kind:
            fail('IOS.NATIVE_FACTS_KIND', ident, 'Kind differs from the owning spec')
            continue
        languages, frameworks = item.get('languages'), item.get('frameworks')
        if not isinstance(languages, list) or not languages or any(not isinstance(v, str) or v not in LANGUAGES for v in languages):
            fail('IOS.NATIVE_FACTS_LANGUAGE', ident, 'Declare actual source languages')
            continue
        if not isinstance(frameworks, list) or not frameworks or any(not isinstance(v, str) or v not in FRAMEWORKS for v in frameworks) or (kind == 'page' and 'nonvisual' in frameworks):
            fail('IOS.NATIVE_FACTS_FRAMEWORK', ident, 'Declare actual UI framework(s); a page cannot be nonvisual')
            continue
        # This is a conservative contradiction detector, not framework inference.
        content_parts = []
        for relative in anchors:
            try:
                file = safe_child(source, relative)
                if (relative in known and file.is_file()
                        and file.suffix.lower() in {'.swift', '.m', '.mm', '.h', '.c', '.cc', '.cpp', '.storyboard', '.xib'}):
                    info = source_anchor_info(file)
                    if info['coordinate_kind'] == 'text_line':
                        content_parts.append(file.read_text(encoding='utf-8-sig'))
            except (MigrationError, OSError, UnicodeError) as exc:
                fail('IOS.NATIVE_FACT_EVIDENCE', ident + ':' + relative, str(exc))
        content = '\n'.join(content_parts)
        if any(Path(a).suffix == '.swift' for a in anchors) and 'swift' not in languages:
            fail('IOS.NATIVE_FACTS_LANGUAGE', ident, 'Swift anchor omitted from declared languages')
        if any(Path(a).suffix == '.m' for a in anchors) and 'objc' not in languages:
            fail('IOS.NATIVE_FACTS_LANGUAGE', ident, 'Objective-C anchor omitted from declared languages')
        if any(Path(a).suffix == '.mm' for a in anchors) and 'objcxx' not in languages:
            fail('IOS.NATIVE_FACTS_LANGUAGE', ident, 'Objective-C++ anchor omitted from declared languages')
        if kind == 'page':
            if re.search(r'^\s*import\s+SwiftUI\b', content, re.M) and 'swiftui' not in frameworks:
                fail('IOS.NATIVE_FACTS_FRAMEWORK', ident, 'SwiftUI import requires explicit treatment, including bridges')
            if re.search(r'UIViewController|UIViewRepresentable|UIViewControllerRepresentable|UIHostingController', content) and not set(frameworks) & {'uikit', 'ib'}:
                fail('IOS.NATIVE_FACTS_FRAMEWORK', ident, 'Controller/bridge evidence requires UIKit treatment')
        facts = item.get('facts')
        if not isinstance(facts, dict):
            fail('IOS.NATIVE_FACTS_SCHEMA', ident, 'facts must be an object')
            continue
        required = required_facts(kind, set(languages), set(frameworks))
        for field in sorted(required - facts.keys()):
            fail('IOS.NATIVE_DIMENSION_MISSING', ident + ':' + field, 'Retain this native semantic dimension')
        for field, fact in facts.items():
            subject = ident + ':' + field
            if not isinstance(fact, dict) or fact.get('status') not in {'known', 'unknown', 'not_applicable'}:
                fail('IOS.NATIVE_FACT_STATUS', subject, 'Expected known, unknown or not_applicable')
                continue
            status = fact['status']
            if status != 'known':
                if not isinstance(fact.get('reason'), str) or not fact['reason'].strip():
                    fail('IOS.NATIVE_FACT_REASON', subject, 'Unknown/not-applicable facts need a concrete reason')
                if status == 'unknown':
                    treatment = projection.semantic_requirement(ident, field, fact) if projection is not None else {'target_required': True}
                    if treatment['target_required']:
                        fail('IOS.NATIVE_FACT_UNKNOWN', subject, fact.get('reason') or 'Native source semantics unresolved')
                    else:
                        for part in treatment['retained_parts']:
                            _known_fact(source, known, anchors, subject + ':' + part['id'], part, fail)
                continue
            _known_fact(source, known, anchors, subject, fact, fail)
    for ident in sorted(documents.keys() - seen):
        fail('IOS.NATIVE_DOCUMENT_MISSING', ident, 'Native facts must cover each page and feature spec')


def _known_fact(source, known, anchors, subject, fact, fail):
    # 0 and False are valid initial values; empty strings/containers are not claims.
    value = fact.get('value')
    if value is None or isinstance(value, (str, list, dict)) and not value:
        fail('IOS.NATIVE_FACT_VALUE', subject, 'Known fact requires a non-empty semantic value')
    evidence = fact.get('evidence')
    if not isinstance(evidence, list) or not evidence:
        fail('IOS.NATIVE_FACT_EVIDENCE', subject, 'Known fact requires source evidence')
        return
    for anchor in evidence:
        try:
            if not isinstance(anchor, dict) or not isinstance(anchor.get('path'), str):
                raise MigrationError('Evidence must declare path and line')
            relative, line = anchor['path'], anchor.get('line')
            file = safe_child(source, relative)
            if relative not in known or relative not in anchors or not file.is_file():
                raise MigrationError('Evidence is outside the owning spec anchors')
            info = source_anchor_info(file)
            if type(line) is not int or not 1 <= line <= info['line_count']:
                raise MigrationError('Evidence line is outside the source file')
            coordinate = info['coordinate_kind']
            if coordinate == 'resource_document':
                if (anchor.get('coordinate_kind') != coordinate
                        or anchor.get('source_sha256') != info['source_sha256']):
                    raise MigrationError('Binary resource evidence requires resource_document coordinates and the current byte hash')
            elif anchor.get('coordinate_kind', 'text_line') != 'text_line':
                raise MigrationError('Text evidence requires real text_line coordinates')
        except (MigrationError, OSError, UnicodeError) as exc:
            fail('IOS.NATIVE_FACT_EVIDENCE', subject, str(exc))
