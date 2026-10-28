"""Read-only iOS/HMOS prerequisites for the existing VERIFY device check.

ALL_READY means prerequisites allow Phase 1 preparation. It never establishes
baseline, arrival or app behavior. No Simulator is created/booted and no app is
installed by this probe. Android input retains the original public launcher.
"""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

from hmigbot_ios.core import MigrationError, read_json
from .source import config


def command(argv, timeout, env=None):
    try:
        r=subprocess.run(list(map(str,argv)),env=env,capture_output=True,text=True,timeout=timeout)
        return {'argv':list(map(str,argv)),'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'timed_out':False}
    except subprocess.TimeoutExpired:
        return {'argv':list(map(str,argv)),'exit_code':None,'stdout':'','stderr':'timeout','timed_out':True}


def ios_prerequisites(project, cfg, timeout, session=None):
    ios=cfg.get('ios',{});configured=ios.get('developer_dir') if isinstance(ios,dict) else None
    selected=command(['/usr/bin/xcode-select','-p'],timeout)
    paths=[Path(configured)] if configured else []
    if os.environ.get('DEVELOPER_DIR'):paths.append(Path(os.environ['DEVELOPER_DIR']))
    if selected['exit_code']==0:paths.append(Path(selected['stdout'].strip()))
    paths += [Path('/Applications/Xcode.app/Contents/Developer')]
    paths += sorted(Path('/Applications').glob('Xcode*.app/Contents/Developer'))
    full=[p.resolve() for p in paths if (p/'usr/bin/xcodebuild').is_file()]
    if configured and not (Path(configured)/'usr/bin/xcodebuild').is_file():
        raise MigrationError('Configured ios.developer_dir is not full Xcode')
    if not full:
        return {'available':False,'source_setup':'unavailable','reason':'Full Xcode is not installed','commands':[selected]}
    developer=full[0]; env={**os.environ,'DEVELOPER_DIR':str(developer)}
    first=command(['/usr/bin/xcodebuild','-checkFirstLaunchStatus'],timeout,env)
    version=command(['/usr/bin/xcodebuild','-version'],timeout,env)
    if first['exit_code'] != 0 or version['exit_code'] != 0:
        raise MigrationError('Xcode needs environment setup/license/first launch; inspect xcodebuild -checkFirstLaunchStatus and -version; probe does not change it')
    runtime=command(['/usr/bin/xcrun','simctl','list','runtimes','-j'],timeout,env)
    if runtime['exit_code'] != 0:
        raise MigrationError('Official simctl runtime inventory failed: '+runtime['stderr'].strip())
    try:
        available=[r for r in json.loads(runtime['stdout'])['runtimes']
                   if r.get('isAvailable') and '.iOS-' in r.get('identifier','')]
    except (ValueError,KeyError,TypeError) as exc:raise MigrationError('Invalid simctl runtime inventory') from exc
    result={'available':bool(available),'developer_dir':str(developer),'xcode_version':version['stdout'].strip(),
            'runtimes':[{'identifier':r['identifier'],'version':r.get('version')} for r in available],
            'source_setup':'pending' if available else 'unavailable','source_observation_verified':False,
            'reason':'Owned source build/create/start and live identity remain required' if available else 'No available iOS Simulator runtime',
            'commands':[selected,first,version,runtime]}
    if session:
        from .xcode_ui import XcodeUISession
        observer=XcodeUISession.open(session)
        devices=command(['/usr/bin/xcrun','simctl','list','devices','-j'],timeout,env)
        if devices['exit_code'] != 0:raise MigrationError('Owned Simulator inventory failed')
        rows=[r for group in json.loads(devices['stdout'])['devices'].values() for r in group]
        matches=[r for r in rows if r.get('udid')==observer.state['udid']]
        if len(matches)!=1:raise MigrationError('Owned observer UDID does not exist in Simulator inventory')
        tree=project/'spec/toolkit-fact-tree.json'
        expected=read_json(tree).get('app',{}).get('package') if tree.is_file() else None
        if expected and expected!=observer.state['bundle_id']:raise MigrationError('Owned source observer bundle conflicts with source tree')
        result.update(source_setup='live_identity_pending',owned_session=str(Path(session).resolve()),
                      owned_udid=observer.state['udid'],owned_bundle_id=observer.state['bundle_id'],
                      owned_device_state=matches[0].get('state'),live_identity_verified=False)
        result['commands'].append(devices)
    return result


def disabled_checks(project):
    values=[]
    text=os.environ.get('A2H_VERIFY_DISABLE','')
    path=project/'spec/verify/disabled_checks.txt'
    if path.is_file():text+='\n'+path.read_text(encoding='utf-8-sig')
    for line in text.replace(',',' ').splitlines():
        if line.lstrip().startswith('#'):continue
        for value in line.split():
            value=value.upper()
            if value.isdigit():value='CHECK-'+value
            if value not in values:values.append(value)
    return values


def inspect(project, *, timeout=10, serial=None, session=None):
    project=Path(project).resolve();cfg=config(project)
    if not math.isfinite(timeout) or timeout<=0 or timeout>120:raise MigrationError('Probe timeout must be finite, >0 and <=120')
    source=ios_prerequisites(project,cfg,timeout,session)
    ios=cfg.get('ios',{});root=ios.get('source_root') if isinstance(ios,dict) else ios
    root=root or cfg.get('android')
    if not root or not (project/root).resolve().is_dir():
        raise MigrationError('Configured iOS source root is missing; prepare this project source input before VERIFY')
    source['source_root']=str((project/root).resolve())
    from .env_doctor import installation
    tools,_=installation(project,cfg)
    configured=os.environ.get('HDC') or cfg.get('hdc')
    hdc=(project/configured).resolve() if configured else (tools or {}).get('hdc')
    if not hdc:hdc=shutil.which('hdc')
    probe=command([str(hdc),'list','targets'],timeout) if hdc and Path(hdc).is_file() else None
    targets=[]
    if probe and probe['exit_code']==0:
        targets=[s.strip() for s in probe['stdout'].splitlines() if s.strip() and 'Empty' not in s]
    if serial:
        selected=serial if serial in targets else None
    elif len(targets)==1:selected=targets[0]
    elif len(targets)>1:raise MigrationError('Several HDC targets are online; pass --serial for this project')
    else:selected=None
    installed=(project/'.agents/skills/arkts-visual-verify/SKILL.md').is_file()
    disabled=disabled_checks(project)
    if not selected:code,verdict=20,'HMOS_UNAVAILABLE'
    elif not source['available']:code,verdict=10,'HMOS_ONLY'
    else:code,verdict=0,'ALL_READY'
    if not installed:check='DEFERRED（verifier skill 未安装：arkts-visual-verify；不阻塞门控）'
    elif 'CHECK-7' in disabled or 'CHECK-8' in disabled:
        check='DEFERRED（A2H_VERIFY_DISABLE / spec/verify/disabled_checks.txt 显式禁用）'
    elif code==20:check='DEFERRED（目标 HDC 无可用设备或指定 serial 未上线）'
    elif code==10:check='DEFERRED（iOS 源不可用：'+source['reason']+'）'
    else:check='RUN'
    return {'hdc':str(hdc) if hdc else None,'hdc_resolved':bool(hdc and Path(hdc).is_file()),
            'hmos_targets':targets,'hmos_online':bool(selected),'selected_serial':selected,
            'hdc_timed_out':bool(probe and probe['timed_out']),'hdc_probe':probe,
            'source_platform':'ios','ios':source,'ios_online':False,
            'readiness_scope':'prerequisites-only; Phase 1 source setup and live identity still required',
            'verifier_skills':{'arkts-visual-verify':str(project/'.agents/skills/arkts-visual-verify') if installed else None},
            'disabled_checks':disabled,'verdict':verdict,'exit_code':code,'checks':{'CHECK-7':check},
            'legacy_check_mapping':{'CHECK-8':'CHECK-7 visual in the current iOS VERIFY contract'},'platform':'darwin'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',default='.');p.add_argument('--timeout',type=float,default=10)
    p.add_argument('--serial');p.add_argument('--native-session',default=os.environ.get('HMIGBOT_IOS_SESSION'));p.add_argument('--json',action='store_true')
    a=p.parse_args(argv)
    try:
        result=inspect(a.project_root,timeout=a.timeout,serial=a.serial,session=a.native_session)
        print(json.dumps(result,ensure_ascii=False));return result['exit_code']
    except (MigrationError,OSError,ValueError,RuntimeError) as exc:
        print(json.dumps({'source_platform':'ios','status':'error','error':str(exc),'exit_code':2,
                          'checks':{'CHECK-7':'FAIL（原生设备预检工具错误；不是设备 DEFERRED）'}},ensure_ascii=False));return 2


if __name__=='__main__':raise SystemExit(main())
