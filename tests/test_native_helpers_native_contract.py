"""Exercise real bundled consumers at the boundaries that formerly guessed source semantics."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.native_helpers import feature_inputs, icon_audit, structural_loop


class NativeHelperTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='native helper 测试 ')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / 'build-profile.json5').write_text(json.dumps({
            'modules': [{'name': 'entry', 'srcPath': './entry'}]}), encoding='utf-8')
        main = self.root / 'entry/src/main'
        main.mkdir(parents=True)
        (main / 'module.json5').write_text(json.dumps({
            'module': {'name': 'entry', 'type': 'entry'}}), encoding='utf-8')

    def test_missing_image_dimensions_blocks_before_any_mutation(self):
        page = self.root / 'entry/src/main/ets/pages/Main.ets'
        page.parent.mkdir(parents=True)
        page.write_text("@Entry\n@ComponentV2\nstruct Main {\n build() {\n Column() {\n Image($r('app.media.icon')).objectFit(ImageFit.Contain)\n }\n }\n}\n")
        before = page.read_bytes()
        result = icon_audit(self.root, self.root / 'evidence/images.json')
        self.assertEqual(result['status'], 'needs_source_dimensions')
        output = self.root / 'evidence/closure.json'
        with contextlib.redirect_stdout(io.StringIO()):
            code = structural_loop(['iterate', '--project-root', str(self.root), '--mode', 'pipeline',
                '--target', 'all', '--state-file', str(self.root / 'evidence/state.json'), '--output-json', str(output)])
        self.assertEqual(code, 3)
        self.assertEqual(json.loads(output.read_text())['verdict'], 'NATIVE_INPUT_REQUIRED')
        self.assertEqual(page.read_bytes(), before)
        self.assertFalse((self.root / 'evidence/state.json').exists())
        # The upstream detector is line-oriented; compact chains can be false
        # positives. Reformat to the documented multiline style and rerun.
        page.write_text(page.read_text().replace('.objectFit', '\n      .width(24)\n      .height(24)\n      .objectFit'))
        self.assertEqual(icon_audit(self.root, self.root / 'evidence/images.json')['status'], 'passed')

    def test_source_oracle_uses_native_output_namespace(self):
        project = self.root / 'project'
        shutil.copytree(ROOT / 'tests/fixtures/a2h-native-spec', project)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(feature_inputs(['--project-root', str(project)]), 0)
        features = json.loads(buffer.getvalue())['features']
        self.assertTrue(features)
        for feature in features:
            self.assertEqual(Path(feature['oracle_file']).parent, (project / 'spec/verify/ut/source-oracle').resolve())


if __name__ == '__main__':
    unittest.main()
