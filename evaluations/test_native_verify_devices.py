import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios.core import MigrationError
from hmigbot_ios152 import native_verify_devices as probe


class NativeDeviceProbe(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.project=Path(self.temp.name);(self.project/'.migbot').mkdir()
        (self.project/'source').mkdir();(self.project/'.agents/skills/arkts-visual-verify').mkdir(parents=True)
        (self.project/'.agents/skills/arkts-visual-verify/SKILL.md').write_text('fixture')
        (self.project/'.migbot/config.json').write_text(json.dumps({'source_platform':'ios','ios':{'source_root':'source'}}))

    def inspect(self,targets,source=True,serial=None):
        with patch.object(probe,'ios_prerequisites',return_value={'available':source,'source_setup':'pending','reason':'runtime unavailable' if not source else 'not started'}),\
             patch('hmigbot_ios152.env_doctor.installation',return_value=({'hdc':Path('/usr/bin/true')},{})),\
             patch.object(probe,'command',return_value={'exit_code':0,'stdout':targets,'stderr':'','timed_out':False}):
            return probe.inspect(self.project,serial=serial)

    def test_ready_means_preparation_not_observation(self):
        r=self.inspect('owned-device\n')
        self.assertEqual((0,'ALL_READY','RUN'),(r['exit_code'],r['verdict'],r['checks']['CHECK-7']))
        self.assertEqual('pending',r['ios']['source_setup']);self.assertFalse(r['ios_online'])
        self.assertNotIn('adb',r)

    def test_real_missing_target_or_source_retains_original_codes(self):
        self.assertEqual(20,self.inspect('[Empty]\n')['exit_code'])
        self.assertEqual(10,self.inspect('device\n',source=False)['exit_code'])

    def test_multiple_devices_cannot_be_guessed(self):
        with self.assertRaises(MigrationError):self.inspect('one\ntwo\n')
        self.assertEqual('two',self.inspect('one\ntwo\n',serial='two')['selected_serial'])

    def test_explicit_disable_is_preserved(self):
        with patch.dict(os.environ,{'A2H_VERIFY_DISABLE':'CHECK-7'}):
            self.assertIn('显式禁用',self.inspect('one')['checks']['CHECK-7'])

    def test_clt_selection_uses_full_xcode_without_changing_it(self):
        calls=[]
        def run(argv,timeout,env=None):
            calls.append((argv,env))
            if argv[-1]=='-p':text='/Library/Developer/CommandLineTools\n'
            elif argv[-1]=='-version':text='Xcode 27.1\n'
            elif 'runtimes' in argv:text=json.dumps({'runtimes':[{'identifier':'com.apple.CoreSimulator.SimRuntime.iOS-27-0','isAvailable':True,'version':'27.0'}]})
            else:text=''
            return {'exit_code':0,'stdout':text,'stderr':'','timed_out':False}
        with patch.object(probe,'command',side_effect=run):
            result=probe.ios_prerequisites(self.project,{},10)
        self.assertTrue(result['available']);self.assertEqual('pending',result['source_setup'])
        self.assertTrue(all(not any(a in argv for a in ('create','boot','shutdown','install','-switch')) for argv,env in calls))
        self.assertTrue(any(env and env['DEVELOPER_DIR'].endswith('Xcode.app/Contents/Developer') for argv,env in calls))

    def test_license_or_first_launch_error_is_not_deferred(self):
        def run(argv,timeout,env=None):
            return {'exit_code':1 if '-checkFirstLaunchStatus' in argv else 0,
                    'stdout':'/Applications/Xcode.app/Contents/Developer\n','stderr':'needs setup','timed_out':False}
        with patch.object(probe,'command',side_effect=run):
            with self.assertRaises(MigrationError):probe.ios_prerequisites(self.project,{},10)

    def test_android_public_launcher_outputs_unchanged(self):
        baseline=ROOT.parent/'hmigbot-ios-1.5.2-mac-20261026.32/skills/a2h-verify/scripts/probe_devices.py'
        if not baseline.is_file():self.skipTest('External baseline is needed for original binary differential')
        (self.project/'.migbot/config.json').write_text('{"source_platform":"android"}')
        outputs=[]
        for script in [baseline,ROOT/'skills/a2h-verify/scripts/probe_devices.py']:
            r=subprocess.run([sys.executable,'-B',str(script),''],cwd=self.project,capture_output=True,text=True,timeout=40)
            outputs.append((r.returncode,json.loads(r.stdout)))
        self.assertEqual(outputs[0],outputs[1])


if __name__=='__main__':unittest.main()
