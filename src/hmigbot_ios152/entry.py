"""Same command-line surface as 1.5.2; dispatch only source-input operations."""
from pathlib import Path
import argparse, json, os, subprocess, sys
from hmigbot_ios.core import MigrationError
from .source import Source, ios_source

def dispatch(name,scripts,argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    parser=argparse.ArgumentParser(description='HMigBot 1.5.2 iOS input adapter: '+name)
    parser.add_argument('--src',required=True)
    if name=='profile_feature':
        parser.add_argument('--features-dir',required=True); parser.add_argument('--out'); parser.add_argument('--rules')
    elif name=='lint_coverage':
        parser.add_argument('--project-root',required=True); parser.add_argument('--features-dir'); parser.add_argument('--profiles')
        parser.add_argument('--rules'); parser.add_argument('--skip-breadth',action='store_true')
        parser.add_argument('--after-repair',action='store_true'); parser.add_argument('--clear-halt')
        parser.add_argument('--only-feature'); parser.add_argument('--report-only',action='store_true')
    elif name=='extract_module_deps':
        parser.add_argument('--out',required=True); parser.add_argument('--modules')
    elif name=='extract_literals':
        parser.add_argument('--out',required=True)
    args=parser.parse_args(argv)
    project=getattr(args,'project_root',None)
    if not project and getattr(args,'features_dir',None): project=Path(args.features_dir).resolve().parents[2]
    if not ios_source(args.src,project):
        print('This independent distribution requires a native iOS source root',file=sys.stderr); return 3
    try:
        if name=='lint_coverage':
            from .coverage import run
            return run(args,scripts)
        source=Source(args.src,project)
        if name=='profile_feature':
            from .profile import build
            rules=json.loads(Path(args.rules or Path(scripts)/'coverage-rules.json').read_text(encoding='utf-8-sig'))
            value=build(source,args.features_dir,rules)
            output=Path(args.out or Path(args.features_dir).parent/'feature-profiles.json')
        elif name=='extract_module_deps':
            from .inventory import modules
            value=modules(source,args.modules); output=Path(args.out)
        elif name=='extract_literals':
            from hmigbot_ios.ios_literals import extract
            value=extract(source.root,source_view=source.view); output=Path(args.out)
        else: raise MigrationError('Unsupported input operation: '+name)
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'output':str(output),'source_platform':'ios'},ensure_ascii=False)); return 0
    except (MigrationError,OSError,ValueError,KeyError) as exc:
        print(json.dumps({'error':str(exc),'source_platform':'ios'},ensure_ascii=False),file=sys.stderr); return 3
