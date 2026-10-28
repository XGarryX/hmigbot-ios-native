"""The same HarmonyOS graph is measured for either source language."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/arkts-router-verify/scripts'


class SharedTargetRoutes(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='shared-target-route-')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'project'
        (self.project / '.agents').mkdir(parents=True)
        (self.project / '.migbot').mkdir()
        self.out = self.project / 'spec/verify/route'
        self.pages = self.project / 'entry/src/main/ets/pages'
        self.pages.mkdir(parents=True)
        self.host = self.pages / 'Root.ets'
        self.host.write_text("import { DetailPage } from './DetailPage'\n"
            "@Entry @Component struct Root {\n"
            " @State shown:boolean=false;\n"
            " @Builder sheet(){DetailPage()}\n"
            " build(){Column(){Button('Open').onClick(()=>{this.shown=true})}.bindSheet(this.shown,this.sheet())}\n"
            "}\n")
        (self.pages / 'DetailPage.ets').write_text("@Component export struct DetailPage{build(){Text('Detail')}}\n")
        self.config('ios')

    def config(self, platform):
        (self.project / '.migbot/config.json').write_text(json.dumps({'source_platform': platform,
            'ios': {'source_root': str(self.project / 'unavailable-source')},
            'android': str(self.project / 'unavailable-android')}))

    def runstage(self, stage):
        return subprocess.run([sys.executable, '-B', str(SCRIPTS / (stage + '.py'))], cwd=self.project,
            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'ROUTE_VERIFY_ROOT': str(self.project),
                 'ROUTE_VERIFY_OUT': str(self.out)}, capture_output=True, text=True, timeout=120)

    def extract(self):
        result = self.runstage('hmos_extract')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return (self.out / 'actual_nav.json').read_bytes()

    def test_target_producer_needs_no_source_facts_and_both_sources_get_same_graph(self):
        ios = self.extract()
        self.assertFalse((self.out / 'expected_nav.json').exists())
        self.assertEqual(json.loads(ios)['edges'][0]['target'], 'DetailPage')
        receipt = json.loads((self.out / 'hmos_extract.native-input.json').read_text())
        self.assertEqual(receipt['scope'], 'harmonyos-target')
        self.config('android')
        self.assertEqual(self.extract(), ios)
        self.assertEqual(json.loads((self.out / 'hmos_extract.native-input.json').read_text())['target_identity'],
                         receipt['target_identity'])

    def test_android_target_mutation_refuses_existing_evidence(self):
        self.config('android')
        self.extract()
        self.host.write_text(self.host.read_text() + '// changed target input\n')
        result = self.runstage('build_page_mapping')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('rerun hmos_extract', result.stderr)

    def test_android_output_tampering_refuses_before_original_consumer(self):
        self.config('android')
        self.extract()
        path = self.out / 'actual_nav.json'
        path.write_bytes(path.read_bytes() + b'\n')
        result = self.runstage('build_report')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('target output changed', result.stderr)

    def test_missing_target_sdk_is_an_error_for_both_sources(self):
        for platform in ('ios', 'android'):
            self.config(platform)
            env = {**os.environ, 'HMIGBOT_ETS_PARSER': str(self.project / 'missing-parser'),
                   'PYTHONDONTWRITEBYTECODE': '1', 'ROUTE_VERIFY_ROOT': str(self.project),
                   'ROUTE_VERIFY_OUT': str(self.out)}
            result = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'hmos_extract.py')],
                cwd=self.project, env=env, capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(json.loads((self.out / 'hmos_extract.native-input.json').read_text())['status'], 'incomplete')


if __name__ == '__main__':
    unittest.main()
