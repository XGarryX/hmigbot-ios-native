"""Recover two original 1.5.2 data gates without changing their algorithms.

The bundled dispatch passes one argv string to these list-taking mains. Private
one-character paths recover that interface. The original exit and diagnostics
remain authoritative; no tree content or quality threshold is fabricated.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
import shutil
import sys
import tempfile

from hmigbot_ios.core import read_json, write_json, MigrationError
from . import native_canonical as canonical


def dimensions(argv, scripts):
    """Readable member probe from original Phase 1.1.f (not a core verdict)."""
    parser=argparse.ArgumentParser(description=dimensions.__doc__)
    parser.add_argument('--project-root',required=True)
    parser.add_argument('--skills-root')
    args=parser.parse_args(argv)
    project=Path(args.project_root).resolve()
    skills=Path(args.skills_root).resolve() if args.skills_root else Path(scripts).resolve().parents[1]
    members={'scenario_run':skills/'arkts-scenario-runner/scripts/scenario_run.py',
        'visual-fixer':project/'.codex/agents/visual-fixer.toml',
        'visual-fixer-reviewer':project/'.codex/agents/visual-fixer-reviewer.toml'}
    missing={key:str(path) for key,path in members.items() if not path.is_file() or path.stat().st_size==0}
    pages=list((project/'spec/baseline/ui').glob('page_*.md'))
    features=list((project/'spec/baseline/features').glob('F*.md'))
    code=2 if missing else 3 if not pages and not features else 0
    print(json.dumps({'implementation':'readable-original-phase1.1.f-member-contract',
        'original_core_compared':False,'exit_code':code,'missing_unit_members':missing,
        'dimensions':{'visual':'enabled' if pages else 'degraded: page specs absent',
                      'functional':'enabled' if features else 'degraded: feature specs absent'},
        'upstream_spec_wholly_absent':not pages and not features,
        'note':'Member availability only; no device, functional or visual acceptance implied'},ensure_ascii=False,indent=2))
    return code


def run(command, argv, scripts):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tree')
    if command == 'check_functional_dimension':
        parser.add_argument('project', nargs='?', default='.')
    else:
        parser.add_argument('--source')
        parser.add_argument('--arch', choices=('pure_traditional', 'pure_compose', 'hybrid'))
    parser.add_argument('--receipt', help='Optional copy of the actual core invocation receipt')
    args = parser.parse_args(argv)
    tree = Path(args.tree).resolve()
    project = (Path(args.project).resolve() if command == 'check_functional_dimension'
               else tree.parent.parent)
    guard = canonical.InputGuard()
    inputs = {}
    value = None
    if tree.is_file():
        inputs[str(tree)] = guard.add(tree)
        value = read_json(tree)
        if canonical.ios_tree(value):
            canonical._source_current(value, project)
    requested = getattr(args, 'arch', None)
    if getattr(args, 'source', None):
        from .native_context import describe
        from .source import Source
        detected = describe(Source(args.source, project if (project/'.migbot/config.json').is_file() else None))['arch']
        if requested and requested != detected:
            raise MigrationError('Explicit architecture differs from the selected native source')
        requested = detected
    requested = requested or 'pure_traditional'
    registry = project/'spec/a2h/functional_registry.json'
    registry_present = registry.is_file()
    if command == 'check_functional_dimension' and registry_present:
        inputs[str(registry)] = guard.add(registry)
    from .compiled_runtime import prepare, execute
    engine = prepare(scripts)
    with tempfile.TemporaryDirectory(prefix='hmigbot-original-gate-') as temporary:
        root = Path(temporary)
        if tree.is_file():
            shutil.copy2(tree, root/'t')
            if canonical.sha(root/'t') != inputs[str(tree)]:
                raise MigrationError('Gate tree copy differs from its canonical input')
        vector = 'xt'
        if command == 'check_functional_dimension':
            (root/'p/spec/a2h').mkdir(parents=True)
            if registry_present:
                shutil.copy2(registry, root/'p/spec/a2h/functional_registry.json')
                if canonical.sha(root/'p/spec/a2h/functional_registry.json') != inputs[str(registry)]:
                    raise MigrationError('Gate registry copy differs from its canonical input')
            vector = 'xtp'
        expected_members={str(p.relative_to(root)) for p in root.rglob('*')}
        guard.verify()
        process = execute(command, [vector], scripts, cwd=root, capture_output=True)
        guard.verify()
        actual_members={str(p.relative_to(root)) for p in root.rglob('*')}
        if actual_members!=expected_members or any(p.is_symlink() for p in root.rglob('*')):
            raise MigrationError('Original data gate produced unexpected private members: '+str(sorted(actual_members^expected_members)))
        if value is not None and canonical.ios_tree(value):canonical._source_current(value,project)
        if tree.exists() != (value is not None) or (command == 'check_functional_dimension' and registry.is_file() != registry_present):
            raise MigrationError('Gate input existence changed during the original invocation')
        for original, digest in inputs.items():
            alias = root/'t' if original == str(tree) else root/'p/spec/a2h/functional_registry.json'
            if canonical.sha(alias) != digest:
                raise MigrationError('Original data gate unexpectedly changed its private input')
        receipt = {'command':command, 'implementation':'original-1.5.2-core-private-argv-alias',
            'inputs_sha256':inputs, 'argv':[str(engine),command,vector], 'cwd':str(root),
            'engine_sha256':canonical.sha(engine), 'exit_code':process.returncode,
            'stdout':process.stdout, 'stderr':process.stderr,
            'canonical_inputs_changed':False}
        if command == 'check_prereq_freshness':
            match=re.search(r'(?:^|\s)arch=(\w+)',process.stderr)
            effective=match.group(1) if match else 'unknown'
            receipt.update(requested_arch=requested, effective_arch=effective,
                arch_rules_applied='original_default', hybrid_specific_rules_executed=False,
                relation_to_hybrid='documented_relaxation_only_unverified')
            if requested != 'pure_traditional':
                print('Native gate: requested_arch='+requested+
                    '; effective_arch='+effective+'; original_default rules; '
                    'hybrid/compose-specific rules were not executed. Original exit is preserved.',file=sys.stderr)
        if args.receipt:
            output = Path(args.receipt).resolve()
            if output in guard.files:
                raise MigrationError('Gate receipt cannot overwrite its input')
            write_json(output, receipt)
        if process.stdout:print(process.stdout,end='')
        if process.stderr:print(process.stderr,end='',file=sys.stderr)
        return process.returncode
