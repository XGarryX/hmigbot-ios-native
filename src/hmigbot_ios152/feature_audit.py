"""Native input port of the public 1.5.2 feature-auditor CLI.

The original implementation is compiled, not importable. This module implements
its observable contract, checked against the bundled original CLI in paired
tests. It reuses Source, including target membership and the Release view. No
foreign-language source projection or source-to-AC obligation ledger is created.
"""
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import argparse
import json
import re
import sys

from hmigbot_ios.core import MigrationError
from .source import Source, entrypoints

DOMAIN_BLACKLIST = set('di infra debug rteditor_api util utils test libs core common base xpopup lib config constants helpers views rteditor adapters kit widgets infrastructure configs beans bean extension const adapter tests ext internal widget view helper'.split())
MODULE_BLACKLIST_PREFIX = ('lib_', 'third_', 'external_', 'vendor_', 'XPopup', 'xpopup')
STRONG = re.compile(r'\w+(?:Presenter|ViewModel|Manager|Repository|UseCase|Service|Controller)$')
MEDIUM = re.compile(r'\w+(?:ViewDelegate|ItemTouchCallback|DragHelper)$')
CLASS_REF = re.compile(r'\b([A-Z][a-zA-Z0-9]{3,})\b')
NON_BIZ = set('Integer VALID API Plus NULL URL String JSON MMKV Intent Free View Page URI Service HTTP Component Bean Phase ArkTS Bundle Long RecyclerView ets DAOImpl MutableLiveData Room Float Helper TextView ArkUI Util Boolean Model TODO HTTPS REST Set Database Step Context FIXME ListView Dialog ActivityResult Feature HarmonyOS Lite SDK ImageView Application Manager Button Android EditText Double DAO ViewModel Utils Adapter Activity Item DialogFragment List DSL Map Fragment Repository'.split())
TIERS = {'strict': {'L1': .90, 'L4_main': .95, 'L4_aux': 0, 'L5_under_max': .20},
         'lenient': {'L1': .85, 'L4_main': .90, 'L4_aux': 0, 'L5_under_max': .30}}
PAGE_ID = re.compile(r'page_(\d+)_(\w+)')
DIALOG = re.compile(r'(Dialog|Popup|Window|Sheet|BottomDialog)$')

# The original title matcher has a fixed fallback dictionary in addition to the
# project-specific Chinese/English mapping derived from feature-index rows.
CN_EN = json.loads(Path(__file__).with_name('feature-audit-title-map.json').read_text(encoding='utf-8'))


def read(path):
    return path.read_text(encoding='utf-8-sig') if path.is_file() else ''


def word_match(name, text):
    # Original CLI: short names use case-insensitive word boundaries; long
    # names use case-sensitive substring matching. Do not silently strengthen it.
    return bool(re.search(r'\b' + re.escape(name) + r'\b', text, re.I)) if len(name) <= 3 else name in text


def feature_texts(project):
    return {p.stem: read(p) for p in sorted((project/'spec/baseline/features').glob('F*.md'))}


def native_index(source, page_text=''):
    """Real type names and target membership, never synthesized .kt files."""
    memberships = defaultdict(set)
    if source.selection:
        from .inventory import modules as module_inventory
        allowed = set(module_inventory(source)['modules'])
        for item in source.selection['source_membership']:
            if item['path'] in source.files:
                memberships[item['path']].update(set(item['targets']) & allowed)
    default_module = source.root.name
    screens = {e['short'] for e in entrypoints(source)}
    screens.update(m[2] for m in PAGE_ID.finditer(page_text))
    # UIKit page names commonly end in Controller. Establish actual inheritance
    # before suffix classification so UI controllers map to page signals rather
    # than accidentally inheriting the business-controller priority.
    parents = {}
    for name in sorted(source.files):
        if name.endswith('.swift'):
            for node in source.syntax(name)['nodes']:
                if node['kind']=='type' and node['value']['kind'] in {'class','struct','protocol'}:
                    value=node['value']
                    parents.setdefault(value['name'].strip('`'),set()).update(
                        word for base in value.get('inherits',[]) for word in re.findall(r'\b\w+\b',base))
            continue
        for match in re.finditer(r'\b(?:class|struct|interface|protocol)\s+(\w+)(?:<[^>]*>)?\s*:\s*([^\n{]+)', source.code(name)):
            parents.setdefault(match[1], set()).update(re.findall(r'\b\w+\b', match[2]))
    controllers = {'UIViewController', 'UINavigationController', 'UITabBarController', 'UITableViewController',
                   'UICollectionViewController', 'UIPageViewController', 'UISplitViewController', 'UIHostingController'}
    views = {'UIView', 'UIControl', 'UILabel', 'UIButton', 'UIScrollView', 'UITableView', 'UICollectionView', 'View'}
    for _ in range(len(parents)+1):
        old = (len(controllers), len(views))
        controllers.update(n for n, bases in parents.items() if bases & controllers)
        views.update(n for n, bases in parents.items() if bases & views)
        if old == (len(controllers), len(views)):
            break
    classes = set()
    modules = defaultdict(set)
    groups = defaultdict(list)
    for name in sorted(source.files):
        code = source.code(name)  # forces stale/unknown Release evidence to surface
        if not code.strip() or 'generated' in Path(name).parts:
            continue
        if name.endswith('.swift'):
            nodes=source.syntax(name)['nodes']
            declarations=[n['value']['name'].strip('`') for n in nodes if n['kind'] in {'type','actor'}]
            extensions=[n['value']['type'].split('.')[0].strip('`') for n in nodes if n['kind']=='extension']
        else:
            declarations = re.findall(r'\b(?:class|struct|enum|actor|protocol|interface|implementation)\s+(\w+)', code)
            extensions = re.findall(r'\bextension\s+(\w+)', code)
        # Keep the original file-level signal unit. A same-named primary type
        # owns that file's signal; only container files with no primary type use
        # their real declarations together. Secondary helpers do not promote a
        # UI-controller file into a business domain by naming alone.
        primary = Path(name).stem
        signal_types = [primary] if primary in declarations else declarations
        names = set(declarations + extensions)
        classes.update(names)
        targets = memberships[name] or {default_module}
        for target in targets:
            modules[target].update(names)
        if Path(name).suffix == '.h':
            continue  # headers do not duplicate implementation-file counts
        if any(STRONG.fullmatch(n) and n not in controllers | views for n in signal_types):
            signal = 'strong'
        elif any(MEDIUM.fullmatch(n) or n in screens or n in controllers for n in signal_types):
            signal = 'medium'
        else:
            signal = 'weak'
        for target in targets:
            groups[(target, Path(name).parent.as_posix())].append({'path': name, 'signal': signal})
    return classes, dict(modules), groups


def scan_domains(groups, texts, index_text, whitelist):
    rows = []
    for (module, folder), files in sorted(groups.items()):
        name = Path(folder).name if folder != '.' else module
        if len(files) < 3 or (name.lower() in DOMAIN_BLACKLIST and name not in whitelist):
            continue
        if module.startswith(MODULE_BLACKLIST_PREFIX):
            continue
        strength = next((s for s in ('strong', 'medium') if any(f['signal'] == s for f in files)), 'weak')
        hits = [f for f, text in texts.items() if word_match(name, text)]
        status = 'covered' if hits else 'missing'
        if strength == 'weak':
            status = 'weak_excluded' if not hits else 'covered'
        rows.append({'name': name, 'pkg_path': folder, 'module': module,
                     'file_count': len(files), 'signal_strength': strength,
                     'signal_examples': [Path(f['path']).name for f in files if f['signal'] == strength][:2],
                     'sample_files': [Path(f['path']).name for f in files][:3],
                     'coverage_status': status, 'hit_features': hits})
    return rows


def title_keywords(title, index_text):
    mapping = dict(CN_EN)
    for cell in re.findall(r'^\|\s*F\d+\s*\|\s*([^|]+?)\s*\|', index_text, re.M):
        english = re.findall(r'\b([a-z][a-z0-9\-]*[a-z0-9])\b', cell)
        chinese = re.findall(r'[\u4e00-\u9fff]{2,}', cell)
        if english:
            for cn in chinese:
                mapping[cn] = english[0]
    pieces = [p for p in re.split(r'[\s/与和及、，,：:（）()\[\]|]+', title) if len(p) >= 2]
    result = list(dict.fromkeys(pieces))
    plain = re.sub(r'[\s/、，,：:（）()\[\]|]+', '', title)
    if len(plain) >= 3:
        width = 2 if len(plain) == 3 else 3
        result.extend(plain[i:i+width] for i in range(len(plain)-width+1))
    result.extend(value for key, value in mapping.items() if key in title)
    return list(dict.fromkeys(result))


def document_layers(project, texts):
    baseline = project/'spec/baseline'
    index_text = read(baseline/'feature-index.md')
    all_text = '\n'.join([index_text, *texts.values()])
    lower = all_text.lower()
    refs = sorted((project/'spec/ref').glob('*_spec.md'))
    if not refs:
        refs = sorted((project/'spec/ref').glob('*spec*.md'))
    caps = []
    for ref in refs:
        for m in re.finditer(r'^###\s+(?:§)?5\.(\d+)\s+(.+?)$', read(ref), re.M):
            keywords = title_keywords(m[2].strip(), index_text)
            caps.append({'section': '5.'+m[1], 'title': m[2].strip(), 'keywords': keywords,
                         'covered': any(k.lower() in lower for k in keywords)})
    api_path = baseline/'api-inventory/api-inventory.json'
    try:
        api = json.loads(read(api_path)) if api_path.is_file() else {}
    except json.JSONDecodeError:
        api = {}  # original CLI treats malformed optional inventory as absent
    candidates = []
    for c in api.get('coverage', {}).get('feature_candidates', []):
        candidates.append({**c, 'covered': bool(c.get('suggested_id') and c['suggested_id'].lower() in lower)
                           or any(p and p.lower() in lower for p in c.get('path_prefixes', []))})
    manifest = read(baseline/'ui-manifest.md')
    ids = {m[0] for m in PAGE_ID.finditer(manifest)}
    if not ids:
        ids = {p.stem for p in (baseline/'ui').glob('page_*.md') if PAGE_ID.fullmatch(p.stem)}
    pages = []
    for page in sorted(ids):
        match = PAGE_ID.fullmatch(page)
        number, short = match.groups()
        covered = page in all_text or bool(re.search(r'\bpage_'+number+r'\b', all_text))
        pages.append({'page_id': page, 'short_name': short, 'page_class': 'aux' if DIALOG.search(short) else 'main', 'covered': covered})
    return caps, candidates, pages, index_text, manifest


def feature_depth(texts, classes, modules):
    rows = []
    for feature, text in texts.items():
        refs = (set(CLASS_REF.findall(text)) - NON_BIZ) & classes
        lines = text.count('\n') + 1
        ratio = round(lines / len(refs), 2) if refs else 0
        sparse = []
        for module, names in modules.items():
            if len(names) >= 20 and re.search(r'\b'+re.escape(module)+r'\b', text) and len(refs & names)/len(names) < .1:
                sparse.append({'module': module, 'referenced_count': len(refs & names),
                               'module_class_count': len(names), 'breadth_pct': round(len(refs & names)/len(names)*100, 1)})
        under = (len(refs) >= 5 and lines/len(refs) < 3) or bool(sparse)
        rows.append({'feature': feature, 'lines': lines, 'referenced_source_count': len(refs),
                     'referenced_paths_sample': sorted(refs)[:8], 'depth_ratio': ratio,
                     'sparse_modules': sparse, 'depth_status': 'under_depth' if under else 'ok' if len(refs) >= 5 else 'not_assessed'})
    return rows


def render(domains, caps, apis, pages, depth, tier):
    t = TIERS[tier]
    scored = [r for r in domains if r['signal_strength'] != 'weak']
    weak = [r for r in domains if r['signal_strength'] == 'weak']
    main = [r for r in pages if r['page_class'] == 'main']
    aux = [r for r in pages if r['page_class'] == 'aux']
    under = [r for r in depth if r['depth_status'] == 'under_depth']
    counts = [(len(scored), sum(r['coverage_status'] == 'covered' for r in scored)),
              (len(caps), sum(r['covered'] for r in caps)),
              (len(apis), sum(r['covered'] for r in apis)),
              (len(main), sum(r['covered'] for r in main)),
              (len(aux), sum(r['covered'] for r in aux)),
              (len(depth), len(depth)-len(under))]
    percentages = [100*c/n if n else 100 for n, c in counts]
    pass_flags = [percentages[0] >= t['L1']*100, percentages[1] >= 100, percentages[2] >= 100,
                  percentages[3] >= t['L4_main']*100, percentages[4] >= t['L4_aux']*100,
                  (len(under)/len(depth) if depth else 0) <= t['L5_under_max']]
    passed = all(pass_flags)
    report = ['# Feature 覆盖率审计', '', '- scan_time: '+datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
              '- features_count: '+str(len(depth)),
              f"- tier: **{tier}** (阈值: L1≥{t['L1']*100:.0f}% / L2=100% / L3=100% / L4_main≥{t['L4_main']*100:.0f}% / L4_aux≥{t['L4_aux']*100:.0f}%)",
              '- L1 weak 信号候选已剔除（不参与阈值，单列）：'+str(len(weak)), '', '## 四层对账总览', '',
              '| 维度 | 全量 | 已覆盖 | 缺失 | 覆盖率 | 阈值 | 状态 |', '|---|---|---|---|---|---|---|']
    names = ['L1 源码 domain (strong+medium)', 'L2 ref/spec §5 能力', 'L3 api 候选', 'L4 主页 (Activity/Fragment)', 'L4 附属页 (Dialog/Popup/Window)', 'L5 feature 深度（under_depth 占比）']
    thresholds = [f"≥{t['L1']*100:.0f}%", '100%', '100%', f"≥{t['L4_main']*100:.0f}%", f"≥{t['L4_aux']*100:.0f}%", f"≤{t['L5_under_max']*100:.0f}%"]
    for i, ((n, c), name) in enumerate(zip(counts, names)):
        value = f'under={100*(n-c)/n if n else 0:.0f}%' if i == 5 else f'{percentages[i]:.0f}%'
        spacing = '' if i == 5 else ' '
        report.append(f"| {name}{spacing}| {n} | {c} | {n-c} | {value} | {thresholds[i]} | {'✅' if pass_flags[i] else '❌'} |")
    report += ['', '**总判定：'+('✅ PASS' if passed else '❌ FAIL')+'**', '']
    missing_domains = [r for r in scored if r['coverage_status'] != 'covered']
    if missing_domains:
        report += ['## L1 缺失：源码 domain 没成 feature', '', '| 优先级 | domain dir | module | 文件数 | 信号 | 状态 | 样例文件 |', '|---|---|---|---|---|---|---|']
        for r in missing_domains:
            priority = 'P0' if r['signal_strength'] == 'strong' else 'P1'
            report.append(f"| **{priority}** | `{r['name']}` | {r['module']} | {r['file_count']} | {r['signal_strength']} ({', '.join(r['signal_examples'])}) | missing | {', '.join(r['sample_files'])} |")
        report.append('')
    if any(not r['covered'] for r in caps):
        report += ['## L2 缺失：ref/spec §5 能力没 feature', '', '| ref 节 | 标题 | 关键词 |', '|---|---|---|']
        for r in caps:
            if not r['covered']:
                report.append('| §'+r['section']+' | '+r['title']+' | '+', '.join(r['keywords'][:3])+' |')
        report.append('')
    if any(not r['covered'] for r in apis):
        report += ['## L3 缺失：api-inventory 候选没 feature', '', '| suggested_id | path_prefixes |', '|---|---|']
        for r in apis:
            if not r['covered']: report.append('| '+r.get('suggested_id', '')+' | '+', '.join(r.get('path_prefixes', []))+' |')
        report.append('')
    if under:
        report += ['## L5 缺失：feature 深度不足', '', '**L5a (ratio)**: 每业务类引用平均不到 3 行描述（概述层级，未展开）', '**L5b (sparse)**: feature 提及某 module 但实际引用其类 < 10%（「提了一句没展开」）', '', '| feature | 行数 | 业务类引用 | ratio | sparse modules | 引用类样例 |', '|---|---|---|---|---|---|']
        for r in under:
            sparse = ', '.join(f"{v['module']}({v['referenced_count']}/{v['module_class_count']} = {v['breadth_pct']}%)" for v in r['sparse_modules']) or '—'
            ratio = str(r['depth_ratio'])
            if r['referenced_source_count'] >= 5 and r['depth_ratio'] < 3: ratio = '**'+ratio+'**'
            report.append(f"| `{r['feature']}` | {r['lines']} | {r['referenced_source_count']} | {ratio} | {sparse} | {', '.join(r['referenced_paths_sample'])} |")
        report.append('')
    for kind, label in [('main', '主页 (Activity/Fragment)'), ('aux', '附属页 (Dialog/Popup/Window)')]:
        missing = [r for r in pages if r['page_class'] == kind and not r['covered']]
        if missing:
            noun = '主页' if kind == 'main' else '附属页（阈值更松，仅作提示）'
            report += [f'## L4 缺失：{label} 没归属 feature', '', f"共 {len(missing)} 个孤{noun}：", '', '| page_id | short_name |', '|---|---|']
            report += ['| '+r['page_id']+' | '+r['short_name']+' |' for r in missing[:80]]
            report.append('')
    tasks = ['# Feature Coverage Tasks', '', '## a2h-spec 增量任务', '']
    ids = [int(m[1]) for m in re.finditer(r'^F(\d+)', '\n'.join(r['feature'] for r in depth), re.M)]
    next_id = max(ids, default=0)+1
    for r in missing_domains:
        slug = re.sub(r'[/\s]+', '-', r['name'])
        tasks.append(f"- [ ] 新建 features/F{next_id:03d}-{slug}.md（来源: 源码 {r['module']}/{r['pkg_path']}，{r['file_count']} 文件，信号={r['signal_strength']}）")
        next_id += 1
    for r in caps:
        if not r['covered']: tasks.append('- [ ] 补 ref/spec §'+r['section']+' 能力：'+r['title'])
    for r in apis:
        if not r['covered']: tasks.append('- [ ] 补 api-inventory 候选 '+r.get('suggested_id', '')+' 到 feature-index')
    for r in pages:
        if not r['covered']: tasks.append('- [ ] 将 '+r['page_id']+' 归属到 feature')
    for r in under:
        tasks.append('- [ ] 展开 `features/'+r['feature']+'.md` 的源码行为描述 (ratio='+str(r['depth_ratio'])+')')
    if weak:
        tasks += ['', '## L1 weak 候选（不强制独立 feature）', '']
        tasks += ['- `'+r['name']+'` ('+str(r['file_count'])+' files)' for r in weak]
    tasks += ['', '## a2h-plan 增量任务', '', '- [ ] 跑完上述补漏后，feature-plan.md 重算依赖图 + 拓扑顺序', '']
    return passed, '\n'.join(report)+'\n', '\n'.join(tasks)+'\n', counts


def main(argv=None):
    parser = argparse.ArgumentParser(prog='compute_feature_coverage.py')
    parser.add_argument('--ios-root', dest='source_root', help='iOS 源码根目录')
    parser.add_argument('--android-root', dest='source_root', help=argparse.SUPPRESS)
    parser.add_argument('--project-root', default='.')
    parser.add_argument('--tier', choices=['strict', 'lenient', 'auto'], default='auto')
    parser.add_argument('--whitelist', help='逗号分隔的 dir 名，覆盖黑名单')
    parser.add_argument('--incremental', action='store_true', help='[v1.1 TODO] 增量扫描，v1.0 未实现。')
    args = parser.parse_args(argv)
    if not args.source_root:
        parser.error('--ios-root is required')
    if args.incremental:
        print('ERROR: --incremental not yet implemented (planned for v1.1).\n       Run full scan without --incremental, or wait for v1.1.', file=sys.stderr)
        return 2
    root = Path(args.source_root).resolve()
    project = Path(args.project_root).resolve()
    if not root.is_dir():
        print('ERROR: iOS source root not found: '+str(root), file=sys.stderr)
        return 2
    if not (project/'spec/baseline/feature-index.md').is_file():
        print('ERROR: PHASE_C_INCOMPLETE feature-index.md not found, run a2h-spec Phase C first', file=sys.stderr)
        return 2
    try:
        texts = feature_texts(project)
        caps, apis, pages, index_text, manifest = document_layers(project, texts)
        source = Source(root, project)
        classes, modules, groups = native_index(source, manifest)
        domains = scan_domains(groups, texts, index_text, set((args.whitelist or '').split(',')))
        depth = feature_depth(texts, classes, modules)
        tier = ('strict' if len(texts) <= 30 else 'lenient') if args.tier == 'auto' else args.tier
        passed, report, tasks, counts = render(domains, caps, apis, pages, depth, tier)
        print('─── L1: 源码 domain 扫描 ───')
        print(f'  candidates(strong+medium)={counts[0][0]} covered={counts[0][1]} missing={counts[0][0]-counts[0][1]} weak_excluded={sum(r["signal_strength"] == "weak" for r in domains)}')
        print('─── L2: ref/spec §5 能力扫描 ───')
        print(f'  capabilities={counts[1][0]} covered={counts[1][1]} missing={counts[1][0]-counts[1][1]}')
        print('─── L3: api-inventory 候选扫描 ───')
        print(f'  candidates={counts[2][0]} covered={counts[2][1]} missing={counts[2][0]-counts[2][1]}')
        print('─── L4: page → feature 反向覆盖 ───')
        print(f'  main(Activity/Fragment)={counts[3][1]}/{counts[3][0]}  aux(Dialog/Popup)={counts[4][1]}/{counts[4][0]}  missing={sum(n-c for n,c in counts[3:5])}')
        print('─── L5: feature 深度（spec lines / source files ratio）───')
        print(f'    indexed classes: {len(classes)}; modules: {len(modules)}')
        print(f'  features={counts[5][0]} ok+no_ref={counts[5][1]} under_depth={counts[5][0]-counts[5][1]}')
        output = project/'spec'
        output.mkdir(parents=True, exist_ok=True)
        (output/'feature-coverage-report.md').write_text(report, encoding='utf-8')
        (output/'feature-coverage-tasks.md').write_text(tasks, encoding='utf-8')
        print('\nreport: '+str(output/'feature-coverage-report.md'))
        print('tasks:  '+str(output/'feature-coverage-tasks.md'))
        print('verdict: '+('✅ PASS' if passed else '❌ FAIL')+' (tier='+tier+')')
        return 0 if passed else 1
    except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
        print('ERROR: native source context: '+str(exc), file=sys.stderr)
        return 1
