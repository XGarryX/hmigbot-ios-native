"""Reuse 1.5.2's compiled feature rules and its original findings writer.

Only native production-file discovery and native entry declarations differ.
No generated Kotlin, fake Manifest, or source/AC obligation registry is used.
"""
from pathlib import Path
import importlib.util, json, os, re, shutil, subprocess, sys, tempfile
from .source import Source, anchors, declarations, entrypoints
from .profile import build, one

def writer(scripts):
    spec=importlib.util.spec_from_file_location('_ios152_original_findings',Path(scripts)/'_a2h_findings.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def native_anchor_coverage(source,features,profiles,fw):
    """The compiled gate's source-extension scan excludes Swift/ObjC.

    Preserve its file accounting level and permissive symbol-root matching;
    this is not compiler symbol or truth-range validation.
    """
    out=[]
    for name,profile in profiles.items():
        md=Path(features)/name
        if not md.is_file(): continue
        acs=re.findall(r'^\s*-\s*\[[ xX]\]\s*[A-Z]{1,4}\d+-AC\d+[^\n]*',md.read_text(encoding='utf-8-sig'),re.M)
        if not acs: continue
        signaled={e['file'] for k in profile.get('required_obligation_kinds',{}).values() for e in k.get('evidence',[])}
        for path in sorted(signaled):
            symbols=declarations(source,path) if path.endswith('.swift') else set(re.findall(r'^\s*(?:(?:public|private|internal|fileprivate|open|final|static|override|mutating|nonisolated|@objc)\s+)*(?:class|struct|enum|protocol|extension|func|@interface|@implementation)\s+(\w+)',source.code(path),re.M))
            covered=False
            for ac in acs:
                sources=re.findall(r'源:([^`→]+)',ac)
                roots={x for value in sources for x in re.findall(r'\b\w+\b',value)}
                if symbols&roots: covered=True; break
            if not covered:
                out.append(fw.make('SPEC.UNCOVERED_ANCHOR_FILE','spec',path,
                    '带原规则信号的源文件没有被任何 AC 的源符号指向承接。',
                    subject_ref=name,fix_hint='在现有或新增行为 AC 中补源码对应；允许合并行为，不按赋值拆 AC'))
    return out

def supplementary(source,project,profiles,findings,skip_breadth=False):
    baseline=Path(project)/'spec/baseline'
    def read(name):
        path=baseline/name
        return path.read_text(encoding='utf-8-sig') if path.is_file() else ''
    skip=read('skip-list.md'); pages=read('ui-manifest.md')
    # Entry coverage is file/screen based, as in the original Manifest rule.
    owned={p.replace('\\','/') for feature in profiles.values() for p in feature.get('anchored_files',[])}
    known=set()
    for p in owned:
        if p in source.files: known.update(declarations(source,p))
    out=[]; summary={'unaccounted':[],'skip_registered':[],'sdk_shells':[]}
    decision=r'\b(?:D-\d+|PD-[\w-]+)\b'
    for entry in entrypoints(source):
        name=entry['short']
        skip_lines=[line for line in skip.splitlines() if re.search(r'`'+re.escape(name)+r'`',line)]
        if skip_lines:
            ref=re.search(decision,'\n'.join(skip_lines))
            summary['skip_registered'].append({**entry,'decision_ref':ref[0] if ref else None})
            if not ref:
                out.append(findings.make('SPEC.MANIFEST_SKIP_NO_DECISION','spec',name,
                    'iOS 入口已登记 skip，但没有决策引用；Gate C 复核理由。',severity='warn'))
        elif name in known or re.search(r'(?<!\w)'+re.escape(name)+r'(?!\w)',pages): pass
        else:
            summary['unaccounted'].append(name)
            out.append(findings.make('SPEC.MANIFEST_ACTIVITY_UNACCOUNTED','spec',name,
                '声明的 iOS App/Scene/导航或 Storyboard 入口未被页面清单、feature anchors 或 skip-list 承接。',
                subject_ref=entry['file'],fix_hint='补页面/功能锚点，或在 skip-list 登记入口与决策引用'))
    unowned=[]
    if not skip_breadth:
        for p in sorted(source.files):
            if Path(p).suffix=='.h': continue
            if p not in owned and p not in skip: unowned.append(p)
        if unowned:
            out.append(findings.make('SPEC.UNOWNED_FILE','spec',str(len(unowned))+' files',
                '生产源码既未被 feature 锚定，也不在 skip-list；完整清单见 context.unowned_files。',
                severity='warn',fix_hint='按模块核对文件归属；不要求一文件一 AC'))
    return out,{'unowned_files':unowned,'manifest_components':summary}

def original_measurement(scripts,source,project,profiles,rules_path,fw):
    profile_path=project/'profiles.json'
    profile_path.write_text(json.dumps(profiles,ensure_ascii=False),encoding='utf-8')
    cmd=[sys.executable,'-B',str(Path(scripts)/'_upstream_lint_coverage.py'),
         '--src',str(source.root),'--project-root',str(project),'--profiles',str(profile_path),
         '--rules',str(rules_path),'--skip-breadth']
    result=subprocess.run(cmd,capture_output=True,env={**os.environ,'PYTHONUTF8':'1','ARKTS_SKILL_DIR':str(scripts)},timeout=120)
    if result.returncode not in (0,2):
        from hmigbot_ios.core import MigrationError
        raise MigrationError('Original coverage engine failed: '+str(result.returncode)+' '+result.stderr.decode('utf-8','replace')[-2000:])
    section=fw.load(str(project)).get('sections',{}).get('spec/lint_coverage')
    if section is None:
        from hmigbot_ios.core import MigrationError
        raise MigrationError('Original coverage engine produced no findings section')
    return section

def shared_measurement(source,features,profiles,rules,scripts,rules_path,fw,scratch,original,local=False):
    from .shared_instances import prepare,probe_inputs,approved_records,expansion,merge,collection_inputs,collection_results
    records,rejected=prepare(source,features,profiles,rules,local=local)
    if not records:
        if rejected:
            original.setdefault('context',{})['shared_instance_references']={'accepted':[],'rejected':rejected}
        return original['findings'],original.get('context',{})
    texts={name:(Path(features)/name).read_text(encoding='utf-8-sig') for name in profiles['features']}
    probe_profiles,documents,lookups=probe_inputs(records,profiles,texts)
    probe=scratch/'direct-probes'; probe_features=probe/'spec/baseline/features';probe_features.mkdir(parents=True)
    # Match the original consumer's skip behavior; an owner proof may never rely on skip.
    skip=scratch/'spec/baseline/skip-list.md'
    if skip.is_file():shutil.copy2(skip,probe_features.parent/'skip-list.md')
    for name,text in documents.items():(probe_features/name).write_text(text,encoding='utf-8')
    measured=original_measurement(scripts,source,probe,probe_profiles,rules_path,fw)
    approved,refused=approved_records(records,lookups,measured.get('context',{}));rejected+=refused
    additions,accepted=expansion(approved,profiles,rejected)
    projected=original
    collections={}
    if accepted:
        for name,assertions in additions.items():
            path=scratch/'spec/baseline/features'/name
            with path.open('a',encoding='utf-8') as handle:
                handle.write('\n\n## Temporary expansion of verified shared AC references\n'+ '\n'.join(assertions.values())+'\n')
        projected=original_measurement(scripts,source,scratch,profiles,rules_path,fw)
        collection_profiles,collection_docs,collection_lookups=collection_inputs(profiles,texts,additions,accepted)
        collection_root=scratch/'collection-probes';collection_features=collection_root/'spec/baseline/features';collection_features.mkdir(parents=True)
        if skip.is_file():shutil.copy2(skip,collection_features.parent/'skip-list.md')
        for name,text in collection_docs.items():(collection_features/name).write_text(text,encoding='utf-8')
        collection=original_measurement(scripts,source,collection_root,collection_profiles,rules_path,fw)
        collections=collection_results(collection_lookups,collection.get('context',{}))
    items,context=merge(original,projected,accepted,rejected,collections=collections)
    from hashlib import sha256
    context['shared_instance_references'].update(source_fingerprint=source.fingerprint,
        original_engine_probes=len(lookups),probe_other_findings=[i for i in measured['findings'] if i['rule']!='SPEC.INSTANCE_UNACCOUNTED'],
        verified_direct_references=[{'consumer':r['consumer'],'instance':r['instance'],'site':r['site'],'owner_ac':r['owner_ac'],
            'owner_file':r['owner']['file'],'owner_line':r['owner']['line'],
            'owner_assertion_sha256':sha256(r['owner']['text'].encode('utf-8')).hexdigest()} for r in approved])
    return items,context

def run(args,scripts):
    fw=writer(scripts); project=Path(args.project_root).resolve()
    features=Path(args.features_dir).resolve() if args.features_dir else project/'spec/baseline/features'
    source=Source(args.src,project)
    rules_path=Path(args.rules) if args.rules else Path(scripts)/'coverage-rules.json'
    rules=json.loads(rules_path.read_text(encoding='utf-8-sig'))
    local=bool(args.only_feature)
    if local:
        md=features/args.only_feature
        if not md.is_file(): print('[lint_coverage] feature missing: '+str(md)); return 3
        profiles={'features':{md.name:one(source,md,rules)}}
    elif args.profiles:
        profiles=json.loads(Path(args.profiles).read_text(encoding='utf-8-sig'))
    else:
        profile_path=project/'spec/baseline/feature-profiles.json'
        if not profile_path.exists():
            print('[lint_coverage] 缺少 feature-profiles.json —— 先运行 profile_feature.py'); return 3
        profiles=json.loads(profile_path.read_text(encoding='utf-8-sig'))
    with tempfile.TemporaryDirectory(prefix='hmigbot-ios152-lint-') as temp:
        scratch=Path(temp); base=scratch/'spec/baseline'; base.mkdir(parents=True)
        for p in (project/'spec/baseline').glob('*.md'):
            shutil.copy2(p,base/p.name)
        scratch_features=base/'features'; scratch_features.mkdir()
        if local:
            # Preserve sibling addenda for this feature's self-check.
            stem=Path(args.only_feature).stem
            for p in features.glob(stem+'*.md'): shutil.copy2(p,scratch_features/p.name)
        else:
            for p in features.glob('*.md'): shutil.copy2(p,scratch_features/p.name)
        section=original_measurement(scripts,source,scratch,profiles,rules_path,fw)
        items,context=shared_measurement(source,features,profiles,rules,scripts,rules_path,fw,scratch,section,local=local)
    existing={(v['rule'],v['subject']) for v in items}
    for item in native_anchor_coverage(source,features,profiles['features'],fw):
        if (item['rule'],item['subject']) not in existing:
            items.append(item); existing.add((item['rule'],item['subject']))
    if not local:
        extra,native_context=supplementary(source,project,profiles['features'],fw,args.skip_breadth)
        items+=extra; context.update(native_context)
    readonly=local or args.report_only
    if readonly:
        print('iOS → 原 1.5.2 coverage（只读不写）')
        print(fw.render(items,'检查结果')); return fw.exit_code(items)
    if args.clear_halt: fw.clear_halt(str(project),'spec/lint_coverage',args.clear_halt)
    stored=fw.replace_section(str(project),'spec/lint_coverage',items,context=context,after_repair=args.after_repair)
    current=stored['sections']['spec/lint_coverage']['findings']
    print(fw.render(current,'检查结果'))
    return fw.section_exit_code(str(project),'spec/lint_coverage',current)
