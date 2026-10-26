"""The built-in C4.6b ownership fallback already specified by HMigBot 1.5.2."""
from collections import defaultdict
from pathlib import Path
import argparse,json,re
from .execution_source import Source,anchors

DEDICATED=re.compile(r'\w+(?:View|Renderer|Controller|Manager|Session)$')
GLUE_DIRS={'diagnostic','adhoc','widget','expand'}

def evaluate(source,features,skip_text=''):
    owned=set(); full_owned=set()
    for md in Path(features).glob('F*.md'):
        if re.fullmatch(r'F\d+-[^.]+\.md',md.name):
            files=anchors(md,source); owned.update(files)
            if not re.search(r'^\s*tier:\s*peripheral\b',md.read_text(encoding='utf-8-sig'),re.M): full_owned.update(files)
    groups=defaultdict(list)
    for name in sorted(source.files):
        if Path(name).suffix!='.h': groups[Path(name).parent.as_posix()].append(name)
    rows=[]
    for folder,files in sorted(groups.items()):
        loc=sum(len(source.text(p).splitlines()) for p in files)
        covered=[p for p in files if p in owned]
        glue=Path(folder).name in GLUE_DIRS or all(re.search(r'(?:Util|Helper|ShadowBuilder|ViewPager)$',Path(p).stem) for p in files)
        skipped=bool(re.search(r'(?<![\w/])'+re.escape(folder)+r'(?![\w/])',skip_text)) if folder!='.' else False
        significant=len(files)>=3 or loc>=500
        def dedicated(p):
            # The original rule is per source file. Extensions remain individual
            # partial_class files, not a new cross-file LOC aggregation rule.
            if p.endswith('.swift'):
                names=[Path(p).stem,*[n['value'].get('name',n['value'].get('type','')).split('.')[0].strip('`')
                    for n in source.syntax(p)['nodes'] if n['kind'] in {'type','actor','extension'}
                    and n['value'].get('kind')!='protocol']]
            else:
                names=[Path(p).stem,*re.findall(r'\b(?:class|struct|enum|actor|extension|interface|implementation)\s+(\w+)',source.code(p))]
            return any(DEDICATED.fullmatch(n) for n in names)
        missing_dedicated=[p for p in files if p not in owned and dedicated(p)
                           and len(source.text(p).splitlines())>=150]
        if glue or skipped: status='SKIP'
        elif significant and not covered or missing_dedicated: status='FAIL'
        elif significant and set(files)&full_owned and len(set(files)&full_owned)/len(files)<.3: status='WARN'
        else: status='PASS'
        rows.append({'package':folder,'file_count':len(files),'loc':loc,'anchored_files':covered,
                     'anchored_percent':round(len(covered)/len(files)*100,2),'status':status,
                     'skip_reason':'platform-glue' if glue else 'registered' if skipped else None,
                     'unowned_dedicated_files':missing_dedicated,'files':files})
    return rows

def main(argv=None):
    p=argparse.ArgumentParser(description='Original 1.5.2 C4.6b built-in ownership fallback on iOS inputs')
    p.add_argument('--src',required=True); p.add_argument('--project-root',required=True)
    a=p.parse_args(argv); project=Path(a.project_root).resolve(); base=project/'spec/baseline'
    skip=base/'feature-coverage-skiplist.md'
    text=skip.read_text(encoding='utf-8-sig') if skip.exists() else ''
    rows=evaluate(Source(a.src,project),base/'features',text)
    # Original fallback records mechanically recognizable glue for Gate C disclosure.
    new=[r for r in rows if r['skip_reason']=='platform-glue' and r['package'] not in text]
    if new:
        skip.parent.mkdir(parents=True,exist_ok=True)
        with skip.open('a',encoding='utf-8') as stream:
            if not text: stream.write('| package | reason |\n|---|---|\n')
            for r in new: stream.write('| `'+r['package']+'` | platform-glue |\n')
    report=['# 源码 ownership 覆盖审计','',
            '执行路径：HMigBot 1.5.2 C4.6b 内置 ownership 兜底。iOS 源输入使用同一选定 Release 上下文。',
            '这是显式选择的 ownership 兜底；正常四层审计使用独立入口，不因 FAIL 自动切换到此路径。',
            '', '| package | file_count | loc | anchored% | status | reason |','|---|---|---|---|---|---|']
    for r in rows: report.append('| '+r['package']+' | '+str(r['file_count'])+' | '+str(r['loc'])+' | '+str(r['anchored_percent'])+' | '+r['status']+' | '+str(r['skip_reason'] or '')+' |')
    failed=any(r['status']=='FAIL' for r in rows)
    report+=['','结果：'+('FAIL' if failed else 'PASS')+'（仅原 ownership 兜底范围）','']
    base.mkdir(parents=True,exist_ok=True)
    (base/'source-coverage-report.md').write_text('\n'.join(report),encoding='utf-8')
    (base/'source-coverage-inputs.json').write_text(json.dumps({'path':'original-C4.6b-ownership-fallback','packages':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(report[-2]); return 1 if failed else 0
