from pathlib import Path
import argparse, json, sys
from hmigbot_ios.core import MigrationError
from .source import Source

def main(argv=None):
    p=argparse.ArgumentParser(description='Native inputs for HMigBot 1.5.2 (no additional stage gates)')
    sub=p.add_subparsers(dest='command',required=True)
    for name in ['inventory','api','visibility']:
        q=sub.add_parser(name); q.add_argument('--src',required=True); q.add_argument('--project-root'); q.add_argument('--out',required=True)
    q=sub.add_parser('environment'); q.add_argument('--swift'); q.add_argument('--xcode-settings'); q.add_argument('--out')
    q=sub.add_parser('capture-release'); q.add_argument('--src',required=True); q.add_argument('--project',required=True)
    q.add_argument('--scheme',required=True); q.add_argument('--out',required=True)
    q.add_argument('--build',action='store_true')
    q=sub.add_parser('prepare-source'); q.add_argument('--src',required=True); q.add_argument('--project-root',required=True)
    q.add_argument('--bundle',required=True); q.add_argument('--provider'); q.add_argument('--variant',required=True); q.add_argument('--out',required=True)
    q=sub.add_parser('meta'); q.add_argument('src'); q.add_argument('--activity',required=True); q.add_argument('--page-id',required=True)
    q.add_argument('--output',required=True); q.add_argument('--package',default=''); q.add_argument('--mode',choices=['scaffold','enrich'],default='scaffold')
    q.add_argument('--existing'); q.add_argument('--view-xml'); q.add_argument('--project-root')
    q=sub.add_parser('view'); q.add_argument('src'); q.add_argument('--layouts',required=True); q.add_argument('--output',required=True)
    q.add_argument('--menus'); q.add_argument('--package'); q.add_argument('--project-root')
    q.add_argument('--resolve-strings',action='store_true'); q.add_argument('--resolve-styles',action='store_true')
    a=p.parse_args(argv)
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'): stream.reconfigure(encoding='utf-8')
    try:
        output=getattr(a,'out',None) or getattr(a,'output',None)
        if a.command=='capture-release':
            from hmigbot_ios.mac_capture import capture_release
            value=capture_release(a.src,a.project,a.scheme,a.out,build=a.build)
            print(json.dumps(value,ensure_ascii=False,indent=2)); return 0
        elif a.command=='environment':
            from hmigbot_ios.init_environment import inspect_environment
            value=inspect_environment(swift=a.swift,build_settings=a.xcode_settings)
        elif a.command=='prepare-source':
            from hmigbot_ios.conditional_source import prepare
            value=prepare(Path(a.project_root),Path(a.src),Path(a.bundle),Path(a.provider) if a.provider else None,
                          json.loads(Path(a.variant).read_text(encoding='utf-8-sig')),Path(a.out),migration_scope=True)
            print(json.dumps(value,ensure_ascii=False,indent=2)); return 0
        else:
            source=Source(a.src,getattr(a,'project_root',None))
            if a.command in {'inventory','api'}:
                from .inventory import overview,api
                value=(overview if a.command=='inventory' else api)(source)
            elif a.command=='visibility':
                from .ui import visibility,visibility_warnings
                value=visibility(source)
                for warning in visibility_warnings(value): print(warning,file=sys.stderr)
            elif a.command=='meta':
                from .ui import meta
                existing=json.loads(Path(a.existing).read_text(encoding='utf-8-sig')) if a.existing else None
                value=meta(source,a.activity,a.page_id,a.package,existing)
            elif a.command=='view':
                from .ui import view
                value=view(source,[n for n in a.layouts.split(',') if n])
        if output:
            path=Path(output); path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(json.dumps({'output':str(path)},ensure_ascii=False))
        else: print(json.dumps(value,ensure_ascii=False,indent=2))
        return 0
    except (MigrationError,OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr); return 3

if __name__=='__main__': raise SystemExit(main())
