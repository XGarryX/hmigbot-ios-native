"""Read-only Stage 3 compilation consumer before the unchanged final loop."""
import argparse
import json
from pathlib import Path
import re

from .core import MigrationError, digest
from .resource_merge import _project, _path, _raw
from .indexed_dispatch import ROOT, load, require, current_outputs


def current_stage3(project):
    """Verify the actual concentrated build, without promoting old group briefs."""
    project=_project(project);state,contract=load(project)
    if state['compile_policy']!='stage3-pilot':return None
    slices=[j for j in state['jobs'].values() if j['phase']=='slice']
    require(slices and all(j['status']=='closed' for j in slices),'Stage 3 generation/closer checkpoints are unfinished')
    require(not any(j['status'] in {'active','stopped'} for j in state['jobs'].values()),'A writer is still active or cessation is unverified')
    require(all(current_outputs(project,j)==j['outputs'] for j in slices),'Stage 3 outputs changed after their closer')
    proof=state['builds'].get('stage3');require(proof,'Stage 3 compilation is pending; do not read old FV PASS')
    report_path=Path(proof['evidence'])
    raw=report_path.read_bytes();report=json.loads(raw)
    require(digest(raw)==proof['sha256'],'Stage 3 build receipt changed')
    from .quality_views import target_inputs
    require(report.get('target_project')==str(project) and report.get('source_sha256')==contract['source_sha256'] and
            report.get('status')=='build_passed' and type(report.get('exit_code')) is int and report['exit_code']==0 and
            report.get('source_changed') is False and report.get('target_input_hashes')==target_inputs(project),
            'Stage 3 build failed or its source/target/resource inputs are stale')
    details=report_path.parent/report['diagnostics']['path']
    require(details.parent==report_path.parent and digest(details.read_bytes())==report['diagnostics']['sha256'] and
            json.loads(details.read_bytes()).get('build_command_passed') is True,'Stage 3 diagnostics changed or failed')
    require(report.get('hvigor_success_marker') is True and b'BUILD SUCCESSFUL' in
            (report_path.parent/'stdout.log').read_bytes()+(report_path.parent/'stderr.log').read_bytes(),
            'Stage 3 success log is missing')
    require(report.get('artifacts'),'Stage 3 build has no current HAP')
    for artifact in report['artifacts']:
        content=_raw(project,artifact['path'])
        require(content and digest(content)==artifact['sha256'],'Stage 3 HAP is missing or changed')
    # New briefs honestly remain pending-compile. At final generation closure,
    # in-app obligations cannot be exempted merely because the old brief parser
    # knows only PASS/ESCALATED/ROLLED_BACK as terminal states.
    registry='spec/placeholder-registry.md'
    if _path(project,registry).exists():
        from .native_writeback import _registry
        _,rows=_registry(project,allow_groups=True)
        debts=[pid for pid,row in rows.items() if row['kind'] in {'forward-ref','forward-ref-uncertain'}
               and row['status']!='resolved' and re.search(r'\bSlice\s+0*\d+\b',row['resolve_by'],re.I)]
        require(not debts,'Generated slices retain unresolved in-app wiring obligations: '+', '.join(debts))
    return {'status':'current_compilation','receipt_sha256':proof['sha256'],
            'group_briefs_unchanged':True,'original_final_structural_and_build_still_required':True}


def preflight(arguments):
    """No writes, including failures; caller preserves original loop exit code 3."""
    args=list(map(str,arguments))
    if not args or args[0] not in {'iterate','finalize'}:return None
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--mode');parser.add_argument('--project-root',type=Path);parser.add_argument('--state-file',type=Path)
    probe,_=parser.parse_known_args(args[1:])
    if args[0]=='iterate' and probe.mode!='pipeline':return None
    project=probe.project_root
    if args[0]=='finalize':
        if not probe.state_file or not probe.state_file.is_file():return None
        state=json.loads(probe.state_file.read_bytes())
        if state.get('mode')!='pipeline':return None
        candidates=[p for p in probe.state_file.resolve().parents if (p/'.migbot/config.json').is_file()
                    and (p/ROOT/'state.json').is_file()]
        if not candidates:return None
        require(len(candidates)==1,'Final structural state has ambiguous project ownership')
        project=candidates[0]
    if project is None:return None
    project=_project(project)
    if not _path(project,ROOT+'/state.json').exists():return None
    return current_stage3(project)
