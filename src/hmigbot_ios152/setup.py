"""Local-only init support; no telemetry enrolment or installation side effects."""
from pathlib import Path
import argparse, json, os, platform, shutil, sys

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['bootstrap','validate'])
    p.add_argument('--workspace',default='.'); p.add_argument('--lang',default='zh')
    a=p.parse_args(argv); root=Path(a.workspace).resolve(); path=root/'.migbot/config.json'
    cfg=json.loads(path.read_text(encoding='utf-8-sig')) if path.is_file() else {}
    if cfg and (cfg.get('source_platform') not in (None,'ios') or cfg.get('tool_package') not in (None,'hmigbot-ios152')
                or (not cfg.get('source_platform') and not cfg.get('ios'))):
        print(json.dumps({'ok':False,'error':'Project belongs to another migration package; use a separate workspace.'})); return 2
    if a.command=='bootstrap':
        if not path.exists():
            cfg={'tool_package':'hmigbot-ios152','source_platform':'ios','ios':{'source_root':''},'harmonyos':'.','hvigorw':'',
                 'deveco':'','hdc':'','language':a.lang,'confirmed':False,'telemetry_consent':'denied'}
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':'exists' if cfg.get('confirmed') else 'needs_path_confirmation',
                          'path':str(path),'config':cfg,'telemetry_hooks_installed':False},ensure_ascii=False)); return 0
    failures=[]
    ios=cfg.get('ios',{}); src=ios.get('source_root','') if isinstance(ios,dict) else ios
    src=src or cfg.get('android','')
    target=cfg.get('harmonyos','')
    if not src or not (root/src).is_dir(): failures.append('iOS source path missing')
    if cfg.get('source_platform')!='ios': failures.append('source_platform must be ios')
    if not target or not (root/target).is_dir(): failures.append('HarmonyOS target path missing')
    elif not cfg.get('hvigorw') and not any((root/target/name).is_file() for name in ['hvigorw','hvigorw.bat']):
        failures.append('hvigorw unresolved; complete the original DevEco resolution chain')
    elif cfg.get('hvigorw') and not (root/cfg['hvigorw']).is_file(): failures.append('Configured hvigorw missing')
    if src and cfg.get('android') and (root/src).resolve()!=(root/cfg['android']).resolve(): failures.append('Legacy source-path alias conflicts with ios.source_root')
    print(json.dumps({'ok':not failures,'failures':failures,'source_build_verified':False,
                      'source_device':'not required for static init'},ensure_ascii=False)); return 1 if failures else 0

if __name__=='__main__': raise SystemExit(main())
