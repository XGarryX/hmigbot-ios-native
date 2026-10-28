"""Argument and diagnostic contracts; synthetic fixtures are not device evidence."""
from contextlib import contextmanager, redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'evaluations'))
from hmigbot_ios152 import native_canonical as C
from test_native_canonical import Fixture


@contextmanager
def cwd(path):
    previous=Path.cwd()
    os.chdir(path)
    try:yield
    finally:os.chdir(previous)


class DataArgumentTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='native-arguments44-')
        self.root=Path(self.temp.name).resolve()

    def tearDown(self):self.temp.cleanup()

    def test_all_seven_dispatch_shapes_keep_scalars_and_only_project_paths(self):
        (self.root/'spec').mkdir()
        with C.ProjectMirror(self.root) as m,cwd(self.root):
            cases={
                'phase2_needs':(['--trip','trip_2_logged_in_vip','--page','HomeView','spec/tree.json'],
                    ['--trip','trip_2_logged_in_vip','--page','HomeView',str(m.root/'spec/tree.json')]),
                'build_batches':(['--fact-tree','spec/tree.json','--batch-size','8'],
                    ['--fact-tree',str(m.root/'spec/tree.json'),'--batch-size','8']),
                'build_judge_input':(['--root',str(self.root),'--round','1','--trip','trip_2_logged_in_vip',
                                     '--prev-round','0','--skip-pages','HomeView,Other'],
                    ['--root',str(m.root),'--round','1','--trip','trip_2_logged_in_vip',
                     '--prev-round','0','--skip-pages','HomeView,Other']),
                'replay_place_artifacts':(['--capture-dir','spec/capture','--round','1','--trip','trip_2_logged_in_vip',
                                          '--only-pages','HomeView','--no-resize'],
                    ['--capture-dir',str(m.root/'spec/capture'),'--round','1','--trip','trip_2_logged_in_vip',
                     '--only-pages','HomeView','--no-resize']),
                'check_functional_dimension':(['x'],['x']),
                'check_android_screenshot':(['x'],['x']),
                'check_blackbox_evidence':(['x'],['x'])}
            for command,(before,after) in cases.items():
                with self.subTest(command=command):
                    self.assertEqual(C._data_arguments(command,before,self.root,m),(after,[]))
            # A real file with the enum's spelling never changes its meaning.
            (self.root/'trip_2_logged_in_vip').write_text('synthetic scalar collision')
            actual,_=C._data_arguments('phase2_needs',cases['phase2_needs'][0],self.root,m)
            self.assertEqual(actual[1],'trip_2_logged_in_vip')
            (self.root/'trip_2_logged_in_vip').unlink()

    def test_equals_paths_out_and_scalar_options_retain_contract(self):
        with C.ProjectMirror(self.root) as m,cwd(self.root):
            actual,outputs=C._data_arguments('build_batches',
                ['--fact-tree=spec/tree.json','--out=spec/batches.json','--batch-size=8'],self.root,m)
            self.assertEqual(actual,['--fact-tree',str(m.root/'spec/tree.json'),
                                     '--out',str(m.work/'requested-output.json'),'--batch-size=8'])
            self.assertEqual(outputs,[(m.work/'requested-output.json',self.root/'spec/batches.json')])
            actual,_=C._data_arguments('phase2_needs',['--trip=trip_2_logged_in_vip','--','spec/tree.json'],self.root,m)
            self.assertEqual(actual,['--trip=trip_2_logged_in_vip','--',str(m.root/'spec/tree.json')])

    def test_registered_escaped_paths_restore_and_unknown_temporary_paths_still_reject(self):
        with C.ProjectMirror(self.root) as m:
            target=str(m.root/'spec/tree.json')
            self.assertEqual(m.normalize(repr(target)),repr(str(self.root/'spec/tree.json')))
            self.assertEqual(json.loads(m.normalize(json.dumps({'path':target}))),
                             {'path':str(self.root/'spec/tree.json')})
            with self.assertRaisesRegex(C.MigrationError,'escaped native alias'):
                m.normalize(str(m.work/'unregistered'))

    def test_normalization_failure_keeps_backend_failure_and_marks_raw_output(self):
        def failed(value):raise C.MigrationError('synthetic display failure')
        output=io.StringIO();error=io.StringIO()
        with redirect_stdout(output),redirect_stderr(error):
            code=C._emit(SimpleNamespace(returncode=2,stdout='original stdout',stderr='original error'),failed)
        self.assertEqual(code,2)
        self.assertEqual(output.getvalue(),'original stdout')
        self.assertIn('original error',error.getvalue())
        self.assertIn('raw backend output follows',error.getvalue())
        with self.assertRaises(C.MigrationError):
            C._emit(SimpleNamespace(returncode=0,stdout='not publishable',stderr=''),failed)

    @unittest.skipUnless(os.environ.get('HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE'),'isolated original core required')
    def test_public_phase2_inside_project_matches_real_original_success_and_argparse_failure(self):
        fixture=Fixture(self.root/'project',names=('HomeView',))
        engine=Path(os.environ['HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE']).resolve()
        def execute(command,args,scripts,**kwargs):
            return subprocess.run([str(engine),command,*map(str,args)],capture_output=True,text=True,
                timeout=60,cwd=kwargs.get('cwd'),env={**os.environ,'ARKTS_SKILL_DIR':str(engine.parents[3])})
        for trip in [fixture.trip,'invalid_trip']:
            with self.subTest(trip=trip):
                with C.ProjectMirror(fixture.root) as mirror:
                    direct=execute('phase2_needs',[str(mirror.root/'spec/toolkit-fact-tree.json'),'--trip',trip],
                                   None,cwd=mirror.root)
                    expected_out=mirror.normalize(direct.stdout);expected_err=mirror.normalize(direct.stderr)
                out=io.StringIO();err=io.StringIO()
                with cwd(fixture.root),patch.object(C,'_core',side_effect=execute),redirect_stdout(out),redirect_stderr(err):
                    code=C.data_cli('phase2_needs',['spec/toolkit-fact-tree.json','--trip',trip],
                                    ROOT/'skills/arkts-visual-verify/scripts',project_override=fixture.root)
                self.assertEqual(code,direct.returncode)
                self.assertEqual(out.getvalue(),expected_out)
                self.assertEqual(err.getvalue(),expected_err)
                if trip=='invalid_trip':self.assertEqual(code,2)


if __name__=='__main__':unittest.main()
