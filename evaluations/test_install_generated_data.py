"""Packaging must not claim working data produced by the original wrappers."""
import ast
import importlib.util
from pathlib import Path
import platform
import re
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('managed_install_qa', ROOT / 'scripts/manage_install.py')
install = importlib.util.module_from_spec(spec)
spec.loader.exec_module(install)


class GeneratedData(unittest.TestCase):
    def test_dirty_package_keeps_canonical_data_but_excludes_only_known_stage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / 'bin').mkdir()
            operating_system = {'Darwin': 'darwin', 'Linux': 'linux', 'Windows': 'windows'}[platform.system()]
            architecture = 'arm64' if platform.machine().lower() in {'arm64', 'aarch64'} else 'amd64'
            suffix = '.exe' if operating_system == 'windows' else ''
            (root / 'bin' / f'a2h-{operating_system}-{architecture}{suffix}').write_bytes(b'fixture asset; never executed')
            scripts = root / 'skills/a2h-spec/scripts'
            scripts.mkdir(parents=True)
            (scripts.parent / 'SKILL.md').write_text('fixture')
            canonical = scripts / 'coverage-rules.json'
            canonical.write_text('{"source":"canonical"}')
            stage = scripts / 'bin/macos-arm64/_entry.dist/coverage-rules.json'
            stage.parent.mkdir(parents=True)
            stage.write_text('{"source":"stale working copy"}')
            other = stage.with_name('other-resource.json')
            other.write_text('{"must":"remain in payload"}')
            metadata = [root / 'docs/.DS_Store', scripts / '.DS_Store',
                        stage.parent / '.DS_Store', root / 'bin/.DS_Store', root / 'policies/.DS_Store']
            for path in metadata:
                path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(b'Finder cache')
            hidden = scripts / '.gitkeep'; hidden.write_bytes(b'keep legitimate hidden file')
            named = scripts / '._ordinary'; named.write_bytes(b'ordinary file, not part of this repair')
            with patch.object(install, 'ROOT', root):
                payload = install.payload()
                for path in metadata: path.write_bytes(b'changed Finder cache')
                self.assertEqual(install.payload(), payload)
            self.assertFalse(any(isinstance(path, Path) and path.name == '.DS_Store' for path in payload.values()))
            for prefix in ('.agents/hmigbot-runtime/skills/a2h-spec/scripts/',
                           '.agents/skills/a2h-spec/scripts/'):
                self.assertEqual(payload[prefix + 'coverage-rules.json'], canonical)
                self.assertNotIn(prefix + 'bin/macos-arm64/_entry.dist/coverage-rules.json', payload)
                self.assertIn(prefix + 'bin/macos-arm64/_entry.dist/other-resource.json', payload)
                self.assertEqual(payload[prefix + '.gitkeep'], hidden)
                self.assertEqual(payload[prefix + '._ordinary'], named)
            self.assertEqual(stage.read_text(), '{"source":"stale working copy"}')

    def test_visible_wrapper_dist_writes_have_an_excluded_stage_and_canonical_source(self):
        # Static coverage of readable wrapper writes; this does not claim to
        # enumerate writes hidden inside the preserved compiled engines.
        found = []
        for script in (ROOT / 'skills').glob('*/scripts/*.py'):
            text = script.read_text(encoding='utf-8-sig')
            if not re.search(r'^_DIST\s*=', text[:1600], re.MULTILINE):
                continue
            tree = ast.parse(text, filename=str(script))
            assignments = {target.id: node.value for node in ast.walk(tree)
                           if isinstance(node, ast.Assign)
                           for target in node.targets if isinstance(target, ast.Name)}

            def relative(node, base, seen=()):
                if isinstance(node, ast.Name):
                    if node.id == base:
                        return ()
                    if node.id in assignments and node.id not in seen:
                        return relative(assignments[node.id], base, (*seen, node.id))
                if isinstance(node, ast.Call):
                    name = ast.unparse(node.func)
                    if name == 'os.path.join' and node.args:
                        head = relative(node.args[0], base, seen)
                        tail = node.args[1:]
                        if head is not None and all(isinstance(x, ast.Constant) and isinstance(x.value, str) for x in tail):
                            return (*head, *(x.value for x in tail))
                    if name in {'Path', 'pathlib.Path'} and len(node.args) == 1:
                        return relative(node.args[0], base, seen)
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div) and isinstance(node.right, ast.Constant) and isinstance(node.right.value, str):
                    head = relative(node.left, base, seen)
                    if head is not None:
                        return (*head, node.right.value)
                return None

            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = ast.unparse(node.func)
                destination = source = None
                if name.rsplit('.', 1)[-1] in {'copy', 'copy2', 'copyfile', 'replace', 'rename'} and len(node.args) >= 2:
                    source, destination = node.args[:2]
                elif name in {'open', 'io.open'} and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str) and any(x in node.args[1].value for x in 'wax'):
                    destination = node.args[0]
                elif isinstance(node.func, ast.Attribute) and node.func.attr in {'write_text', 'write_bytes'}:
                    destination = node.func.value
                if destination is None:
                    continue
                target = relative(destination, '_DIST')
                if target is None:
                    continue
                canonical_name = relative(source, '_HERE') if source is not None else None
                self.assertIsNotNone(canonical_name, str(script))
                canonical = script.parent.joinpath(*canonical_name)
                self.assertTrue(canonical.is_file(), str(canonical))
                staged = script.parent / 'bin/macos-arm64/_entry.dist'
                staged = staged.joinpath(*target)
                self.assertTrue(install.generated_runtime_stage(staged), str(staged))
                payload = install.payload()
                self.assertIn('.agents/skills/' + canonical.relative_to(ROOT / 'skills').as_posix(), payload)
                found.append((script.relative_to(ROOT).as_posix(), target))
        self.assertTrue(found, 'No visible original wrapper data producer was checked')


if __name__ == '__main__':
    unittest.main()
