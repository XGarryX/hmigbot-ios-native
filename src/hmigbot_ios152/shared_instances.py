"""Resolve optional, direct shared-instance references without changing profiles.

Only temporary inputs are expanded. The original compiled gate measures both
the cited atomic AC and the final consumer; its normal findings writer remains
the sole writer. This module does not infer ownership from feature names.
"""
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
import re

from .profile import instances

FEATURE = re.compile(r'([A-Z]{1,4}\d+)-[a-z0-9-]+\.md\Z')
AC = re.compile(r'^\s*-\s*\[[ xX]\]\s*([A-Z]{1,4}\d+-AC\d+)(?!\d)(.*)$')
SITE = re.compile(r'([^\s|`]+\.(?:swift|mm|m|h|c|cpp)):(\d+)\Z')


def visible_lines(text):
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield number, line


def references(text):
    """A small optional table in a consumer main spec; no free-text inference."""
    active = False
    for number, line in visible_lines(text):
        heading = re.match(r'^(#{1,6})\s+(.+?)\s*#*\s*$', line)
        if heading:
            active = heading[2] == '共享实例引用'
            continue
        if not active or not line.strip().startswith('|'):
            continue
        cells = [x.strip().strip('`') for x in line.strip().strip('|').split('|')]
        if len(cells) != 3 or cells[0] == '实例ID' or all(re.fullmatch(r'[: -]+', x) for x in cells):
            continue
        yield {'line': number, 'instance': cells[0], 'site': cells[1], 'owner_ac': cells[2]}


def _sites(item):
    return {(s.get('file'), s.get('line')) for s in item.get('sites', [])}


def _truths(line):
    return [(m[1], int(m[2])) for m in re.finditer(r'真:src:([^\s`|]+?):(\d+)(?!\d)', line)]


def _same_source(source, item, site, assertion):
    """Qualified enum identity, or an exact/closest-function truth location.

    A number elsewhere in the same file is insufficient. Enum declarations can
    legitimately be tested by a switch elsewhere in their declaring file.
    """
    path, number = site
    line_count = len(source.text(path).splitlines())
    truths = [n for p, n in _truths(assertion) if p == path and 1 <= n <= line_count]
    if not truths:
        return False
    if item['id'].startswith('enum:'):
        qualified = item['id'][5:]
        owner, _, member = qualified.rpartition('.')
        if path.endswith('.swift'):
            cases = [n for n in source.syntax(path)['nodes'] if n['kind'] == 'enum_case'
                     and n['value']['enum_name'].strip('`') + '.' + n['value']['name'].strip('`') == qualified]
            if len(cases) != 1 or cases[0]['line'] != number:
                return False
        source_fields = ' '.join(re.findall(r'源:([^`→]+)', assertion))
        groups = {v.strip() for g in re.findall(r'组:\{([^}]+)\}', assertion) for v in g.split(',')}
        return (item['id'] in groups or
                re.search(r'(?<!\w)' + re.escape(qualified) + r'(?!\w)', assertion) is not None or
                (re.search(r'(?<!\w)' + re.escape(owner) + r'(?!\w)', source_fields) is not None
                 and re.search(r'(?<!\w)' + re.escape(member) + r'(?!\w)', assertion) is not None))
    if number in truths:
        return True
    if not path.endswith('.swift'):
        return False
    text = source.text(path)
    functions = []
    for node in source.syntax(path)['nodes']:
        if node['kind'] != 'function':
            continue
        start = text.count('\n', 0, node['start']) + 1
        end = text.count('\n', 0, node['end']) + 1
        if start <= number <= end:
            functions.append((end - start, start, end, node['value']['name'].strip('`')))
    if not functions:
        return False
    _, start, end, name = min(functions)
    source_fields = ' '.join(re.findall(r'源:([^`→]+)', assertion))
    return any(start <= n <= end for n in truths) and re.search(r'(?<!\w)' + re.escape(name) + r'(?!\w)', source_fields) is not None


def prepare(source, features, profiles, rules, local=False):
    """Return structurally valid references; compiled direct coverage comes next."""
    paths = {p.name: p for p in Path(features).glob('*.md') if FEATURE.fullmatch(p.name)}
    texts = {name: paths[name].read_text(encoding='utf-8-sig') for name in profiles['features'] if name in paths}
    needed = {row['owner_ac'].split('-AC')[0] for text in texts.values() for row in references(text)}
    for name, path in paths.items():
        if FEATURE.fullmatch(name)[1] in needed and name not in texts:
            texts[name] = path.read_text(encoding='utf-8-sig')
    acs = defaultdict(list)
    refs = {name: list(references(text)) for name, text in texts.items()}
    for name, text in texts.items():
        fid = FEATURE.fullmatch(name)[1]
        retired = bool(re.search(r'^\s*(?:status|state):\s*(?:skip|skipped|superseded)\s*$', text, re.M))
        for number, line in visible_lines(text):
            match = AC.match(line)
            if match:
                acs[match[1]].append({'file': name, 'line': number, 'text': line, 'fid': fid, 'retired': retired})
    records, rejected = [], []
    current = {}
    for consumer, profile in profiles['features'].items():
        for row in refs.get(consumer, []):
            record = {'consumer': consumer, **row}
            reason = None
            site_match = SITE.fullmatch(row['site'])
            candidates = [(kind, item) for kind, items in profile.get('enumerable_instances', {}).items()
                          for item in items if item['id'] == row['instance']]
            targets = acs.get(row['owner_ac'], [])
            if not site_match or len(candidates) != 1:
                reason = '实例ID或源位置无效/不唯一'
            else:
                path, number = site_match[1], int(site_match[2]); site = (path, number)
                kind, item = candidates[0]
                record.update(kind=kind, item=item, source_site=site)
                if site not in _sites(item) or path not in source.files:
                    reason = '声明位置与当前消费者画像不符'
                else:
                    if path not in current:
                        current[path] = instances(source, path, rules)
                    actual = [v for v in current[path].get(kind, []) if v['id'] == item['id'] and site in _sites(v)]
                    if len(actual) != 1:
                        reason = '实例已陈旧或不在当前源视图中'
                if reason is None and len(targets) != 1:
                    reason = 'owner AC不存在或ID重复'
                if reason is None:
                    target = targets[0]; assertion = target['text']
                    owner = Path(features) / target['file']
                    if target['fid'] == FEATURE.fullmatch(consumer)[1] or not row['owner_ac'].startswith(target['fid'] + '-AC'):
                        reason = '自转引或owner AC前缀不符'
                    elif not local and target['file'] not in profiles['features']:
                        reason = 'owner主规格不在本轮画像检查范围内'
                    elif not local and not any(v['id']==item['id'] and site in _sites(v)
                                               for v in profiles['features'][target['file']].get('enumerable_instances',{}).get(kind,[])):
                        reason = 'owner画像没有保留该源实例义务'
                    elif target['retired'] or re.search(r'superseded|〔\s*被替代', assertion, re.I):
                        reason = 'owner AC已失效'
                    elif not all(re.search(field, assertion) for field in [r'源:', r'判:', r'真:src:']):
                        reason = 'owner AC缺少源/判/真字段'
                    elif any(r['instance'] == item['id'] and r['site'] == row['site'] for r in refs[target['file']]):
                        reason = 'owner又转引同一实例，拒绝链式转引'
                    else:
                        from .source import anchors
                        if path not in anchors(owner, source) or not _same_source(source, item, site, assertion):
                            reason = 'owner AC未指向同一源实例'
                        else:
                            record.update(owner=target)
            if reason:
                rejected.append({**{k: v for k, v in record.items() if k not in {'item', 'owner'}}, 'reason': reason})
            else:
                records.append(record)
    return records, rejected


def probe_inputs(records, profiles, texts):
    """Each probe sees one instance and either the consumer or one cited AC."""
    result = {'features': {}}
    documents, lookups = {}, []
    counter = 0
    for record in records:
        for role, text in [('consumer', texts[record['consumer']]), ('owner', record['owner']['text'])]:
            name = f'F{900000 + counter}-shared-probe.md'; counter += 1
            profile = deepcopy(profiles['features'][record['consumer']])
            profile.update(feature_file=name, required_obligation_kinds={}, required_addenda={}, signal_counts={},
                           enumerable_instances={record['kind']: [record['item']]})
            result['features'][name] = profile
            documents[name] = text
            lookups.append((name, role, record))
    return result, documents, lookups


def approved_records(records, lookups, context):
    measurements = {}
    for name, role, record in lookups:
        stats = context.get('instance_stats', {}).get(name, {}).get(record['kind'], {})
        measurements[(id(record), role)] = stats
    approved, refused = [], []
    for record in records:
        stats = measurements.get((id(record), 'owner'), {})
        if stats.get('total') == 1 and stats.get('unaccounted') == 0 and stats.get('skip', 0) == 0 and stats.get('ac', 0) + stats.get('group', 0) == 1:
            approved.append({**record, 'consumer_measurement': measurements.get((id(record), 'consumer'), {})})
        else:
            refused.append({'consumer': record['consumer'], 'instance': record['instance'], 'site': record['site'],
                            'owner_ac': record['owner_ac'], 'reason': '原检查器未确认所引AC直接覆盖该实例'})
    return approved, refused


def expansion(records, profiles, diagnostics):
    """Expand only when every site of a merged instance has an approved row."""
    by_item = defaultdict(list)
    for record in records:
        by_item[(record['consumer'], record['kind'], record['instance'])].append(record)
    additions = defaultdict(dict); accepted = defaultdict(list)
    for (consumer, kind, instance), rows in by_item.items():
        item = rows[0]['item']
        if {tuple(r['source_site']) for r in rows} != _sites(item):
            diagnostics.append({'consumer':consumer,'instance':instance,'reason':'合并实例的源位置未全部获得有效直接引用'})
            continue
        measure = rows[0]['consumer_measurement']
        if measure.get('total') != 1 or measure.get('unaccounted') != 1:
            diagnostics.append({'consumer':consumer,'instance':instance,'reason':'本地已覆盖或消费者单项测量不符，转引未用于清除缺项'})
            continue
        accepted[(consumer, kind)].append(instance)
        for row in rows:
            additions[consumer][row['owner_ac']] = row['owner']['text']
    return additions, accepted


def collection_inputs(profiles, texts, additions, accepted):
    """Measure named before/after sets, preventing equal-count substitutions."""
    result={'features':{}}; documents={};lookups=[];counter=0
    for consumer,kind in accepted:
        for item in profiles['features'][consumer]['enumerable_instances'][kind]:
            for role in ('before','after'):
                name=f'F{800000+counter}-collection-probe.md';counter+=1
                profile=deepcopy(profiles['features'][consumer])
                profile.update(feature_file=name,required_obligation_kinds={},required_addenda={},signal_counts={},
                               enumerable_instances={kind:[item]})
                result['features'][name]=profile
                text=texts[consumer]
                if role=='after':text+='\n\n'+'\n'.join(additions[consumer].values())+'\n'
                documents[name]=text
                lookups.append((name,role,consumer,kind,item['id']))
    return result,documents,lookups


def collection_results(lookups, context):
    sets=defaultdict(lambda:{'before':set(),'after':set(),'valid':True})
    for name,role,consumer,kind,instance in lookups:
        stats=context.get('instance_stats',{}).get(name,{}).get(kind,{})
        if stats.get('total')!=1 or stats.get('unaccounted') not in (0,1):
            sets[(consumer,kind)]['valid']=False
        elif stats['unaccounted']==1:sets[(consumer,kind)][role].add(instance)
    return sets


def merge(original, projected, accepted, diagnostics, collections=None):
    """Keep every unrelated first-pass finding, warning and original denominator."""
    items = list(original['findings']); context = deepcopy(original.get('context', {}))
    done = []
    for (consumer, kind), instances_ in accepted.items():
        before = context.get('instance_stats', {}).get(consumer, {}).get(kind, {})
        after = projected.get('context', {}).get('instance_stats', {}).get(consumer, {}).get(kind, {})
        measured=(collections or {}).get((consumer,kind),{})
        correct_set=(measured.get('valid') and set(instances_)<=measured['before'] and
                     measured['after']==measured['before']-set(instances_) and
                     len(measured['before'])==before.get('unaccounted') and len(measured['after'])==after.get('unaccounted'))
        if not correct_set or before.get('total') != after.get('total') or before.get('unaccounted', 0) - len(instances_) != after.get('unaccounted'):
            diagnostics.append({'consumer': consumer, 'kind': kind, 'reason': '展开产生额外覆盖或计数不符，保留原阻断'})
            continue
        subject = consumer + '::' + kind
        items = [i for i in items if not (i['rule'] == 'SPEC.INSTANCE_UNACCOUNTED' and i['subject'] == subject)]
        items.extend(i for i in projected['findings'] if i['rule'] == 'SPEC.INSTANCE_UNACCOUNTED' and i['subject'] == subject)
        context['instance_stats'][consumer][kind] = {**before, 'shared': len(instances_), 'unaccounted': after['unaccounted']}
        done.append({'consumer': consumer, 'kind': kind, 'instances': instances_,
                     'uncovered_before':sorted(measured['before']),'uncovered_after':sorted(measured['after'])})
    context['shared_instance_references'] = {'accepted': done, 'rejected': diagnostics,
        'projection_other_findings': [i for i in projected['findings'] if i['rule'] != 'SPEC.INSTANCE_UNACCOUNTED']}
    return items, context
