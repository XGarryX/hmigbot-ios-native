"""Read-only content/consumer contract checks over authoritative Markdown.

This gate detects structural and evidenced counterexamples, not full semantic
equivalence. It does not generate business assertions or mark model reviews PASS.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .core import MigrationError, digest, read_json, safe_child
from .source_scope import import_token_lines, preview_lines
from .swiftui import tokenize

FEATURE_SECTIONS = ('范围', '数据流', '服务层', '实现映射', '状态管理', '对接点', '验收标准')
PAGE_SECTIONS = ('页面', '结构', '状态接口', '导航', '映射', '资源', '验收')
COMMON = ('feature-base.md', 'feature-index.md', 'ui-manifest.md', 'skip-list.md', 'source-coverage-report.md')
AC = re.compile(r'^- \[[ xX]\]\s+(F\d+-AC\d+)\s+(.+)$', re.M)
SYMBOL = re.compile(r'\b[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+\b')
DEFERRED = re.compile(r'(?:^|[;；，])\s*(?:\b(?:TODO|TBD)\b(?:\s*[:：]|\s+|\s*$)|待(?:补充|完善|展开|定义|确定)|'
                      r'(?:后续|以后|稍后).{0,16}(?:补充|展开|定义|填写)|'
                      r'(?:其余|剩余|其他)\s*\d+\s*(?:处|项|条).{0,40}(?:见|另行|审阅)|'
                      r'\b(?:to be (?:defined|supplied|completed)|will be (?:defined|supplied|completed) later)\b)', re.I)
TARGET_HEADINGS = ('服务层', '公共服务与状态', '目标接口', '公开接口', '实现映射', '状态管理', '状态接口')
TARGET_HEADERS = frozenset(('目标接口', '目标实现', '目标状态', '目标状态与类型', '目标字段', '目标成员',
                            '目标Owner.state与类型', '目标Owner.symbol', '目标Owner.symbol与类型',
                            'ArkTS目标', 'ArkTS目标接口', 'ArkTS目标实现', 'ArkTS目标状态'))
STATE_HEADERS = frozenset(('目标状态', '目标状态与类型', '目标字段', '目标成员',
                           '目标Owner.state与类型', 'ArkTS目标状态'))


def sections(text):
    """Keep every body; core/reference consumers diagnose ambiguous headings.

    This compatibility mapping is not an exact reference resolver. Joining is
    deliberate: an old document must never silently lose the earlier section.
    The structured parser retains levels and positions for ambiguity checks.
    """
    from .artifact_contract import markdown_sections
    result = {}
    for section in markdown_sections(text):
        title = section['title']
        result[title] = result[title] + '\n' + section['body'] if title in result else section['body']
    return result


def acceptance(text):
    """Stable AC assertions from authored visible lines, never code examples."""
    from .artifact_contract import _visible_lines
    return [assertion for _, line in _visible_lines(text) for assertion in AC.findall(line)]


def contract_refs(text):
    lines, refs, active, declared = text.splitlines(), [], False, False
    for line in lines:
        field = re.match(r'^contract_refs:\s*(.*?)\s*$', line)
        if field:
            if declared:
                raise MigrationError('Duplicate contract_refs field')
            declared = True
            active = True
            if field[1]:
                try:
                    inline = json.loads(field[1])
                except ValueError as exc:
                    raise MigrationError('Inline contract_refs must be a JSON string list, or use the multiline YAML form') from exc
                if not isinstance(inline, list) or any(not isinstance(ref, str) for ref in inline):
                    raise MigrationError('contract_refs must contain strings')
                refs.extend(inline)
                active = False
            continue
        if active:
            match = re.match(r'^\s+-\s+[\'\"]?([^\'\"]+?)[\'\"]?\s*$', line)
            if match:
                refs.append(match[1])
            elif line.strip():
                active = False
    return refs


def references(project, document, text):
    resolved = []
    for ref in contract_refs(text):
        relative, _, heading = ref.partition('#')
        target = safe_child(project, relative)
        if (not relative.startswith(('spec/baseline/', 'spec/ref/'))
                or relative.startswith('spec/baseline/plans/')
                or relative in {'spec/baseline/ui-manifest.md', 'spec/baseline/feature-index.md'}
                or target.suffix != '.md' or not target.is_file()):
            raise MigrationError('Contract reference must be an existing baseline/ref Markdown file: ' + ref)
        contents = target.read_text(encoding='utf-8-sig')
        from .artifact_contract import markdown_sections
        if not heading or sum(s['title'] == heading for s in markdown_sections(contents)) != 1:
            raise MigrationError('Contract reference needs an exact existing heading: ' + ref)
        resolved.append((target, heading, sections(contents)[heading]))
    return resolved


def dependency_inputs(project):
    """Freeze explicit shared contracts transitively, including references under ref/."""
    project = Path(project).resolve()
    base = project / 'spec/baseline'
    pending = [base / name for name in COMMON]
    pending += list((base / 'features').glob('*.md')) + list((base / 'ui').glob('*.md'))
    pending.append(project / 'spec/decision-ledger.md')
    from .artifact_contract import external_contracts
    pending.extend(external_contracts(project))
    seen, hashes = set(), {}
    while pending:
        path = pending.pop()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        hashes[path.relative_to(project).as_posix()] = digest(path.read_bytes())
        for target, _, _ in references(project, path, path.read_text(encoding='utf-8-sig')):
            pending.append(target)
    from .artifact_contract import authored_inputs
    hashes.update(authored_inputs(project))
    return hashes


def _target_cells(body, *, state=False):
    """Return only cells selected by supported, real table headers."""
    from .artifact_contract import markdown_tables
    allowed, values = STATE_HEADERS if state else TARGET_HEADERS, []
    for table in markdown_tables(body):
        headers = [re.sub(r'\s+', '', header.strip('`*_ ')) for header in table['headers']]
        indexes = [index for index, header in enumerate(headers) if header in allowed]
        for row in table['rows']:
            values.extend(row[index] if index < len(row) else '' for index in indexes)
    return values


def _prose_declarations(body):
    """A target signature starts a line, optionally with an explicit label.

    Source prose, arbitrary mentions, malformed table rows and fenced examples
    cannot define an executable target contract.
    """
    from .artifact_contract import _visible_lines, markdown_tables
    table_lines = {number for table in markdown_tables(body)
                   for number in range(table['line'], table['end_line'] + 1)}
    symbols = set()
    for number, line in _visible_lines(body):
        if number in table_lines or '|' in line:
            continue
        line = re.sub(r'^\s*(?:(?:[-*+]\s+)|(?:\d+[.)]\s+))?', '', line)
        line = re.sub(r'^(?:目标接口|目标状态|目标字段|目标实现|公开接口|ArkTS\s*目标接口)\s*[:：]\s*', '', line)
        match = re.match(r'`?(' + SYMBOL.pattern + r')', line)
        if match:
            symbols.add(match[1])
    return symbols


def declared_symbols(parts):
    declared = set()
    for heading, body in parts.items():
        if not any(key in heading for key in TARGET_HEADINGS):
            continue
        for value in _target_cells(body):
            declared.update(SYMBOL.findall(value))
        if any(key in heading for key in ('状态管理', '接口', '服务层', '公共服务与状态')):
            declared.update(_prose_declarations(body))
    return declared


def check(project):
    from .native_pipeline import context, findings_module, source_paths
    source, project = context(Path(project))
    queue, findings, inputs, acceptance_count = findings_module(), [], {}, 0
    base = project / 'spec/baseline'
    graph_path = base / 'ios-facts.json'
    state_paths = {f['anchor']['path'] for f in read_json(graph_path).get('facts', []) if f.get('kind') == 'state'} if graph_path.is_file() else set()
    source_views = {}
    projection = None
    try:
        from .ios_harness import responsibility
        projection = responsibility(project, source=source)
        if projection is not None:
            inputs.update(projection.frozen_inputs())
    except (MigrationError, OSError, ValueError, TypeError, KeyError) as exc:
        # Keep inspecting independent source and Markdown contracts below.
        findings.append(queue.make('IOS.SPEC_RESPONSIBILITY_INVALID', 'spec', 'ios-responsibility.json', str(exc)))

    def fail(rule, subject, detail):
        full_rule = 'IOS.SPEC_' + rule
        if rule in ('DOCUMENT_MISSING', 'ARTIFACT_MISSING'):
            # Both profiles still run all checks. Only the same absent path is
            # coalesced; unrelated semantic findings retain their identities.
            subject = re.sub(r'/+', '/', subject.replace('\\', '/')).removeprefix('./')
            existing = next((row for row in findings if row['subject'] == subject
                             and row['rule'] in ('IOS.SPEC_DOCUMENT_MISSING', 'IOS.SPEC_ARTIFACT_MISSING')), None)
            if existing:
                existing['rules'] = sorted(set(existing.get('rules', [existing['rule']])) | {full_rule})
                return
        finding = queue.make(full_rule, 'spec', subject, detail)
        if rule in ('DOCUMENT_MISSING', 'ARTIFACT_MISSING'):
            finding['rules'] = [full_rule]
        findings.append(finding)

    def read(path):
        if not path.is_file():
            fail('DOCUMENT_MISSING', path.relative_to(project).as_posix(), 'Required migration contract is missing')
            return ''
        inputs[path.relative_to(project).as_posix()] = digest(path.read_bytes())
        return path.read_text(encoding='utf-8-sig')

    from .artifact_contract import catalog, check_artifacts, contract_version, markdown_sections, revision
    try:
        profile = contract_version(project)
        if profile == 2:
            check_artifacts(project, source, fail, inputs)
    except (MigrationError, OSError, UnicodeError) as exc:
        profile = None
        fail('ARTIFACT_PROFILE', 'ios_harness.spec_contract_version', str(exc))

    for name in COMMON:
        contents = read(base / name)
        if contents and not any(line.strip() and not line.startswith('#') for line in contents.splitlines()):
            fail('COMMON_EMPTY', name, 'State the applicable contract or an evidenced not-applicable assessment')
        if profile == 1:
            core = {rule['title'] for entry in catalog()['spec']
                    if entry.get('path') == 'spec/baseline/' + name for rule in entry.get('sections', [])}
            headings = [section['title'] for section in markdown_sections(contents)]
            for title in sorted(set(headings) & core):
                if headings.count(title) > 1:
                    fail('HEADING_AMBIGUOUS', 'spec/baseline/' + name + '#' + title,
                         'Required headings must resolve uniquely; preserve both bodies and review the ambiguity')
    read(project / 'spec/decision-ledger.md')
    documents = [(p, 'feature') for p in sorted((base / 'features').glob('F*.md')) if not re.match(r'F\d+[-_].+\..+\.md$', p.name)]
    documents += [(p, 'page') for p in sorted((base / 'ui').glob('page_*.md'))]
    if not documents:
        fail('DOCUMENT_MISSING', 'baseline', 'No page or feature contracts exist')
    seen = set()
    for path, kind in documents:
        text = read(path)
        parts = sections(text)
        required = FEATURE_SECTIONS if kind == 'feature' else PAGE_SECTIONS
        headings = [section['title'] for section in markdown_sections(text)]
        for heading in sorted(set(headings)):
            if headings.count(heading) > 1 and any(key in heading for key in required + TARGET_HEADINGS):
                fail('HEADING_AMBIGUOUS', path.relative_to(project).as_posix() + '#' + heading,
                     'Required/target headings must resolve uniquely; preserve both bodies and review the ambiguity')
        for key in required:
            if not any(key in name and body for name, body in parts.items()):
                fail('SECTION_MISSING', path.name + ':' + key, 'Supply the behavior/target contract, a precise shared reference, or an evidenced not-applicable statement')
        if kind == 'feature':
            for field, allowed in {'complexity': {'simple', 'complex'}, 'tier': {'core', 'standard', 'peripheral'}, 'depth': {'full', 'stub'}}.items():
                match = re.search(r'^' + field + r':\s*(\w+)\s*$', text, re.M)
                if not match or match[1] not in allowed:
                    fail('METADATA', path.name + ':' + field, 'Declare a supported scheduling value: ' + '/'.join(sorted(allowed)))
        for heading, body in parts.items():
            if any(key in heading for key in ('服务层', '实现映射', '状态接口', '对接点')) and re.search(r'(?im)^\s*(?:TBD|TODO|待确定|待计划阶段)\s*[:：]', body):
                fail('UNRESOLVED', path.name + ':' + heading, 'Resolve public target contracts before planning implementation; preserve unrelated unknowns separately')
        shared = {}
        pending, visited = [path], set()
        try:
            while pending:
                parent = pending.pop()
                if parent in visited:
                    continue
                visited.add(parent)
                for target, heading, body in references(project, parent, parent.read_text(encoding='utf-8-sig')):
                    inputs[target.relative_to(project).as_posix()] = digest(target.read_bytes())
                    shared[heading] = shared.get(heading, '') + '\n' + body
                    pending.append(target)
        except (MigrationError, OSError, UnicodeError) as exc:
            fail('REFERENCE_INVALID', path.name, str(exc))
        symbols = declared_symbols(parts) | declared_symbols(shared)
        if kind == 'page':
            state = next((body for name, body in parts.items() if '状态接口' in name), '')
            targets = _target_cells(state, state=True)
            if ((not targets and not _prose_declarations(state))
                    or any(not SYMBOL.search(value) for value in targets)):
                if set(source_paths(text)) & state_paths or not re.search(r'无状态|stateless', state, re.I):
                    fail('UI_TARGET_STATE', path.name, 'State table needs explicit target owner.symbol mapping, or a reviewed stateless contract')
            continue
        assertions = acceptance(text)
        if not assertions:
            fail('AC_MISSING', path.name, 'The main feature must retain stable independently judgeable acceptance criteria')
        for ident, body in assertions:
            acceptance_count += 1
            if ident in seen:
                fail('AC_DUPLICATE', ident, 'Stable AC IDs must be globally unique')
            seen.add(ident)
            target = re.search(r'标:\s*([^`\s]+)', body)
            symbol = target[1].split('(', 1)[0].rstrip(',;') if target else ''
            historical = projection is not None and ident in projection.acceptance['source_history']
            if not historical and (not symbol or symbol not in symbols):
                fail('TARGET_UNDEFINED', ident, 'Declare target owner.symbol in this feature or an explicitly referenced target contract: ' + symbol)
            expected = re.search(r'判:(?:static|unit|contract|route|ui|visual|device)\s*\|\s*([^`]+)', body)
            if not expected or not expected[1].strip() or re.match(r'真:', expected[1].strip()):
                fail('AC_EXPECTED', ident, 'Acceptance needs its own concrete expected result before the truth anchor')
            if expected and DEFERRED.search(expected[1].strip()):
                fail('AC_DEFERRED', ident, 'Expand concrete independently judgeable assertions; do not defer unspecified expressions')
            truth = re.search(r'真:src:([^`\s]+?):(\d+)(?:-\d+)?', body)
            if truth:
                try:
                    source_file = safe_child(source, truth[1])
                    if source_file not in source_views:
                        source_text = source_file.read_text(encoding='utf-8-sig')
                        from .swift_native import project_syntax, source_tokens
                        parsed = source_tokens(source, truth[1], project_syntax(project, source))
                        source_views[source_file] = (source_text.splitlines(), preview_lines(source_text, tokens=parsed), import_token_lines(parsed))
                    source_lines, preview, imports = source_views[source_file]
                    line = int(truth[2])
                    if not 1 <= line <= len(source_lines):
                        raise MigrationError('Source truth line outside file')
                    if line in imports:
                        fail('TRUTH_IMPORT', ident, 'An import is a dependency locator, not evidence of a business operation')
                    if line in preview:
                        fail('TRUTH_PREVIEW', ident, 'Preview-only code cannot establish production behavior')
                except (MigrationError, OSError, UnicodeError) as exc:
                    fail('TRUTH_INVALID', ident, str(exc))
    from .gate_policy import summary_status
    report = {'schema_version': 1, 'status': summary_status(findings, queue=queue),
              'scope': 'Markdown migration content and consumer contracts; not semantic or runtime equivalence',
              'behavior_verified': False, 'spec_contract_version': profile,
              'artifact_contract_revision': revision(project) if profile else None,
              'findings': findings, 'inputs': inputs,
              'counts': {'features': sum(k == 'feature' for _, k in documents),
                         'pages': sum(k == 'page' for _, k in documents), 'acceptance': acceptance_count}}
    return report, 2 if findings else 0
