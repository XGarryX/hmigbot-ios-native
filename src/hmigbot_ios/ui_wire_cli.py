"""Compatibility argv for native meta/outline views from the one Git source service."""
from pathlib import Path
import argparse
import json
import sys

from .core import MigrationError, atomic_write, json_bytes, read_json, safe_child
from .execution_source import Source


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    for name in ('meta','view','visibility'):
        p=commands.add_parser(name)
        p.add_argument('src',type=Path)
        p.add_argument('--project-root',type=Path,required=True)
        p.add_argument('--output',type=Path,required=True)
        p.add_argument('--package',default='')
        if name=='meta':
            p.add_argument('--activity',required=True);p.add_argument('--page-id',required=True)
            p.add_argument('--mode',choices=['scaffold','enrich'],default='scaffold')
            p.add_argument('--existing',type=Path);p.add_argument('--view-xml',type=Path)
        elif name=='view':
            p.add_argument('--layouts',required=True);p.add_argument('--menus')
            p.add_argument('--resolve-strings',action='store_true');p.add_argument('--resolve-styles',action='store_true')
    args=parser.parse_args(argv)
    try:
        project=args.project_root.resolve()
        output=args.output if args.output.is_absolute() else project/args.output
        output=safe_child(project,output.absolute().relative_to(project).as_posix())
        if not output.is_relative_to(project/'spec/execution/source-ui'):
            raise MigrationError('Derived UI writes belong to spec/execution/source-ui; frozen baseline is read-only')
        source=Source(args.src,project)
        from .source_ui_wire import meta,view,visibility
        if args.command=='meta':
            existing=read_json(args.existing) if args.existing else None
            value=meta(source,args.activity,args.page_id,args.package,existing)
            raw=json_bytes(value)
        elif args.command=='view':
            raw=view(source,[p for p in args.layouts.split(',') if p]).encode('utf-8')
        else:
            raw=json_bytes(visibility(source))
        atomic_write(output,raw)
        print(json.dumps({'output':str(output),'source_sha256':source.fingerprint,'runtime_observed':False},ensure_ascii=False))
        return 0
    except (MigrationError,OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'status':'blocked','error':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 3


if __name__=='__main__':
    raise SystemExit(main())
