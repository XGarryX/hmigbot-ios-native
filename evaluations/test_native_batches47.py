"""Neutral mirror contracts; synthetic captures are never device evidence.

The opaque original core is exercised on these inputs, not claimed exhaustively
enumerated. Set HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE for real-core cases.
"""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios.core import read_json,write_json
from hmigbot_ios152 import native_canonical as C
from hmigbot_ios152 import native_file_mapping as M
from evaluations.test_native_canonical import Fixture,capture

SCRIPTS=ROOT/'skills/arkts-visual-verify/scripts'


def fixture(root):
    f=Fixture(root,names=('HomeView','LibraryView','DetailView','UnavailableView'))
    tree=read_json(f.tree)
    for node in tree['pages']:node['functional_checks']=[]
    tree['pages'][0]['functional_checks']=[{'name':'Toggle favorite','feature_path':'Neutral>favorite',
        'expected_ios':None,'ios_trusted':None,'ios_anchor':{'raw_identifier':'favorite'}}]
    write_json(f.tree,tree)
    ledger=read_json(f.ew/'ledger.json');ledger['settled'].pop('UnavailableView');write_json(f.ew/'ledger.json',ledger)
    f.place()
    first='trip_1_logged_out'
    plan=read_json(f.ew/'walk_plan.json');walk=copy.deepcopy(plan['walks'][0])
    walk.update(walk_id='synthetic_first',trip_id=first);plan['walks'].append(walk)
    write_json(f.ew/'walk_plan.json',plan)
    for name,row in ledger['settled'].items():
        row['trip']=first;row['capture_meta']=capture(f.ew/'shots/_bytrip'/first,name,trip=first)
    write_json(f.ew/'ledger.json',ledger)
    C.place_baselines(f.tree,f.ew,f.root,first)
    write_json(f.root/'spec/visual-verify/_trip_assignment.json',
        {'pages':{name:{'trips':[first,f.trip]} for name in f.names}})
    write_json(f.root/'spec/a2h/functional_registry.json',{'entries':[{'name':'Toggle favorite',
        'feature_path':'Neutral>favorite','raw_identifier':'favorite','depth':1,
        'source_file':'Neutral.swift','source_section':'click_handlers'}]})
    debt=f.root/'spec/visual-verify/_baseline_debt.json'
    write_json(debt,{'old':'must be recomputed'})
    return f,debt


def batch_args(f):
    return ['--fact-tree',str(f.tree),'--out',str(f.root/'batches.json'),
            '--batch-size','8','--hmos-project',str(f.root)]


@unittest.skipUnless(os.environ.get('HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE'),'isolated original core required')
class NestedOriginal47(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='native-batches47-test-');self.addCleanup(temp.cleanup)
        self.root=Path(temp.name).resolve();self.f,self.debt=fixture(self.root)
        self.engine=Path(os.environ['HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE']).resolve()
        def execute(command,args,scripts,*,cwd=None,env=None):
            environment={**os.environ,**(env or {}),'ARKTS_SKILL_DIR':str(scripts),
                'HMIGBOT_SCRIPT_DIR':str(scripts),'HMIGBOT_HOST_PYTHON':sys.executable,
                'PYTHONDONTWRITEBYTECODE':'1'}
            return subprocess.run([str(self.engine),command,*map(str,args)],cwd=cwd,
                capture_output=True,text=True,timeout=120,env=environment)
        self.execute=execute
        self.addCleanup(patch.stopall)
        patch.object(C,'_core',side_effect=execute).start()
    def run_data(self,command,args):
        out=io.StringIO();err=io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            code=C.data_cli(command,args,SCRIPTS,project_override=self.root)
        return code,out.getvalue()+err.getvalue()
    def test_nested_writer_recomputes_identical_original_debt(self):
        before_tree=self.f.tree.read_bytes();before_mode=self.debt.stat().st_mode
        code,log=self.run_data('build_batches',batch_args(self.f))
        self.assertEqual(0,code,log);self.assertTrue((self.root/'batches.json').is_file())
        actual=read_json(self.debt);self.assertNotIn('old',actual)
        self.assertEqual(before_tree,self.f.tree.read_bytes())
        self.assertEqual(before_mode,self.debt.stat().st_mode)
        code,log=self.run_data('check_android_screenshot',[])
        self.assertEqual(0,code,log);self.assertEqual(actual,read_json(self.debt))
    def test_readonly_control_reproduces_original_nested_permission_failure(self):
        before=self.debt.read_bytes()
        with C.ProjectMirror(self.root) as mirror:
            copied=mirror.root/'spec/visual-verify/_baseline_debt.json'
            self.assertEqual(0o444,copied.stat().st_mode & 0o777)
            args,_=C._data_arguments('build_batches',batch_args(self.f),self.root,mirror)
            process=self.execute('build_batches',args,SCRIPTS,cwd=mirror.root,
                env={'HMIGBOT_NATIVE_MIRROR':str(mirror.root),'HMIGBOT_NATIVE_CANONICAL_PROJECT':str(self.root)})
            self.assertEqual(40,process.returncode,process.stderr)
            self.assertIn('PermissionError',process.stderr);mirror.verify()
        self.assertEqual(before,self.debt.read_bytes())
    def test_blackbox_consumer_keeps_existing_debt_and_original_gate(self):
        before=self.debt.read_bytes()
        code,log=self.run_data('check_blackbox_evidence',[])
        self.assertEqual(0,code,log);self.assertEqual(before,self.debt.read_bytes())
    def test_missing_ui_still_blocks_original_gate_and_never_publishes_batches(self):
        shutil.rmtree(self.root/'spec/visual-verify/screenshots/ios')
        code,log=self.run_data('build_batches',batch_args(self.f))
        self.assertEqual(40,code,log);self.assertNotIn('PermissionError',log)
        self.assertFalse((self.root/'batches.json').exists())


class Help47(unittest.TestCase):
    def test_resolved_project_alias_restores_without_private_prefix(self):
        with tempfile.TemporaryDirectory(prefix='native-root47-test-') as temp:
            root=Path(temp).resolve()
            with C.ProjectMirror(root) as mirror:
                for origin in (mirror.root,mirror.root.resolve()):
                    self.assertEqual(str(root/'spec/tree.json'),mirror.normalize(str(origin/'spec/tree.json')))
    def test_declared_output_paths_restore_raw_json_repr_and_resolved_alias(self):
        with tempfile.TemporaryDirectory(prefix='native-output47-test-') as temp:
            root=Path(temp).resolve()
            with C.ProjectMirror(root) as mirror:
                actual=str(root/'with spaces'/'雪"quote.json')
                _,outputs=C._data_arguments('build_batches',['--out',actual],root,mirror)
                staged=outputs[0][0]
                for path in (str(staged),str(staged.resolve())):
                    self.assertEqual(actual,mirror.normalize(path))
                    self.assertEqual(actual,json.loads(mirror.normalize(json.dumps(path))))
                    self.assertEqual(repr(actual),mirror.normalize(repr(path)))
                for path in (str(staged)+'.tmp',str(mirror.work/'unregistered.json')):
                    with self.assertRaises(C.MigrationError):mirror.normalize(path)
    def test_original_argparse_failure_keeps_exit_and_restores_declared_out(self):
        with tempfile.TemporaryDirectory(prefix='native-output47-test-') as temp:
            root=Path(temp).resolve();f=Fixture(root,names=('HomeView',))
            def fail(command,args,scripts,**kw):
                return subprocess.CompletedProcess([],2,'','error: unrecognized arguments: --out '+C._option(args,'--out')+'\n')
            text=io.StringIO();error=io.StringIO()
            with patch.object(C,'_core',side_effect=fail),contextlib.redirect_stdout(text),contextlib.redirect_stderr(error):
                result=C.data_cli('phase2_needs',[str(f.tree),'--trip',f.trip,'--out',str(root/'missing.json')],SCRIPTS)
            self.assertEqual(2,result);self.assertIn(str(root/'missing.json'),error.getvalue())
            self.assertNotIn('adapter_normalization_error',error.getvalue());self.assertFalse((root/'missing.json').exists())
    def test_help_preserves_core_exit_and_never_runs_mirror_or_mapping(self):
        with tempfile.TemporaryDirectory(prefix='native-help47-test-') as temp:
            out=Path(temp)/'must-not-exist.json'
            for argv in (['--help'],['-h'],['--help','--out',str(out)]):
                with (self.subTest(argv=argv),patch.object(C,'data_cli',side_effect=AssertionError('mirror')),
                     patch.object(M,'mapped_queue',side_effect=AssertionError('overlay')),
                     patch.object(C,'_core',return_value=subprocess.CompletedProcess([],17,'original help\n','')) as core,
                     contextlib.redirect_stdout(io.StringIO()) as text):
                    self.assertEqual(17,M.batches_cli(argv,SCRIPTS))
                self.assertEqual('original help\n',text.getvalue())
                self.assertEqual(argv,core.call_args.args[1]);self.assertFalse(out.exists())


if __name__=='__main__':unittest.main()
