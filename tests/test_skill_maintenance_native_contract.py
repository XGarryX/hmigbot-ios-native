"""Regressions for maintained skill content and installed supporting resources."""
import hashlib
import importlib.util
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SkillMaintenanceTests(unittest.TestCase):
    def test_metadata_sync_preserves_manually_maintained_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('src', 'scripts'):
                shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns('__pycache__'))
            for source in (ROOT / 'skills').rglob('*.md'):
                target = root / source.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            (root / 'docs').mkdir()
            maintained = root / 'skills/a2h-run/SKILL.md'
            maintained.write_bytes(maintained.read_bytes() + b'\nLocal maintained correction must survive catalog sync.\n')
            before = {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (root / 'skills').rglob('*') if p.is_file()}
            for entry in ('sync_skill_catalog.py', 'generate_skills.py'):
                result = subprocess.run([sys.executable, str(root / 'scripts' / entry)], capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            after = {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (root / 'skills').rglob('*') if p.is_file()}
            self.assertEqual(before, after)

    def test_installed_skill_references_are_readable_without_development_checkout(self):
        spec = importlib.util.spec_from_file_location('maintenance_install', ROOT / 'scripts/manage_install.py')
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        from install_fixture import small_payload
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            with small_payload(installer):
                installer.manage(workspace, 'install')
            skills = workspace / '.agents/skills'
            references = []
            for entry in skills.glob('*/SKILL.md'):
                for target in re.findall(r'\]\(([^)]+)\)', entry.read_text(encoding='utf-8')):
                    if target.startswith('references/'):
                        path = entry.parent / target
                        self.assertTrue(path.is_file(), str(path))
                        original = ROOT / 'skills' / entry.parent.name / target
                        self.assertEqual(path.read_bytes(), original.read_bytes())
                        references.append(path)
            self.assertTrue(references)
            result = installer.manage(workspace, 'uninstall')
            self.assertEqual(result['status'], 'uninstalled')
            self.assertTrue(all(not p.exists() for p in references))


if __name__ == '__main__':
    unittest.main()
