import copy
import json
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hmigbot_ios.analyze import analyze
from hmigbot_ios.build import build_target
from hmigbot_ios.contracts import validate_facts, validate_generation
from hmigbot_ios.core import MigrationError, digest, read_json, write_json
from hmigbot_ios.generate import sdk_api
from hmigbot_ios.swiftui import parse_view


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hmigbot test ")
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def test_fact_contract_rejects_tampered_anchor_and_duplicate_ids(self):
        report = analyze(ROOT / "tests/fixtures/swiftui_counter")
        validate_facts(report)
        invalid = copy.deepcopy(report)
        invalid["facts"][0]["source_anchors_ref"][0]["sha256"] = "0" * 64
        with self.assertRaises(MigrationError):
            validate_facts(invalid)
        invalid = copy.deepcopy(report)
        invalid["facts"].append(invalid["facts"][0])
        with self.assertRaises(MigrationError):
            validate_facts(invalid)

    def test_binary_plist_assets_localization_and_dependencies(self):
        self.root.joinpath("Model.swift").write_text("struct Model {}")
        self.root.joinpath("Info.plist").write_bytes(plistlib.dumps({"CFBundleIdentifier": "com.example.test",
            "NSCameraUsageDescription": "Scan a document"}, fmt=plistlib.FMT_BINARY))
        write_json(self.root / "Localizable.xcstrings", {"sourceLanguage": "en", "strings": {"greeting": {
            "localizations": {"zh-Hans": {"stringUnit": {"state": "translated", "value": "你好"}}}}}})
        write_json(self.root / "Assets.xcassets/Icon.imageset/Contents.json", {"images": [{"filename": "icon.png", "scale": "2x"}]})
        write_json(self.root / "Package.resolved", {"version": 2, "pins": [{"identity": "library", "state": {"version": "1.2.3"}}]})
        report = analyze(self.root)
        kinds = {f["kind"] for f in report["facts"]}
        self.assertTrue({"declaration_config", "localization", "asset_catalog", "dependency"}.issubset(kinds))
        validate_facts(report)

    def test_malformed_input_is_a_gap_and_dtd_is_rejected(self):
        self.root.joinpath("Model.swift").write_text("struct Model {}")
        self.root.joinpath("Bad.plist").write_text("not a plist")
        self.root.joinpath("Bad.storyboard").write_text('<!DOCTYPE x [<!ENTITY e "x">]><document>&e;</document>')
        report = analyze(self.root)
        self.assertEqual(sum(i["code"] == "unreadable_source" for i in report["issues"]), 2)

    def test_case_collision_and_bad_manifests(self):
        for manifest in [[], {}, {"schema_version": "hmigbot-ios/1", "source_sha256": "0" * 64,
                         "files": {"A.ets": "1" * 64, "a.ets": "2" * 64}}]:
            with self.subTest(value=manifest), self.assertRaises(MigrationError):
                validate_generation(manifest)

    def test_sdk_format_tracks_actual_toolchain_rules(self):
        self.assertEqual(sdk_api("26.0.0"), 26)
        self.assertEqual(sdk_api("6.0.2(22)"), 22)
        for invalid in ("latest", "22", "6.0.2", "26.0.0; command"):
            with self.subTest(value=invalid), self.assertRaises(MigrationError):
                sdk_api(invalid)

    def test_repeated_padding_not_silently_collapsed(self):
        with self.assertRaises(MigrationError):
            parse_view('import SwiftUI\nstruct Sample: View { var body: some View { Text("A").padding(8).padding(16) } }')

    def build_config(self):
        source, target = self.root / "ios", self.root / "harmony"
        source.mkdir()
        target.mkdir()
        source.joinpath("Main.swift").write_text("struct Model {}")
        write_json(target / "build-profile.json5", {})
        wrapper = self.root / "hvigorw.js"
        wrapper.write_text("// fake provider for process-boundary test")
        return {"source": {"platform": "ios", "root": str(source)},
                "target": {"platform": "harmonyos", "root": str(target)},
                "tools": {"hvigorw": str(wrapper), "node": sys.executable}}

    def test_build_failure_retains_evidence(self):
        config = self.build_config()
        with patch("hmigbot_ios.build.subprocess.run", return_value=subprocess.CompletedProcess([], 7, b"compile error", b"detail")) as run:
            result = build_target(config, self.root / "evidence")
        self.assertEqual(result["status"], "build_failed")
        self.assertEqual(result["exit_code"], 7)
        self.assertFalse(run.call_args.kwargs["shell"])
        self.assertEqual((self.root / "evidence/stdout.log").read_bytes(), b"compile error")
        self.assertEqual(result['target_project'], str(Path(config['target']['root']).resolve()))
        self.assertEqual(result['target_input_hashes']['build-profile.json5'],
                         digest((Path(config['target']['root']) / 'build-profile.json5').read_bytes()))
        self.assertEqual(result['spec_input_hashes'], {})

    def test_zero_exit_without_hap_is_not_success(self):
        with patch("hmigbot_ios.build.subprocess.run", return_value=subprocess.CompletedProcess([], 0, b"", b"")):
            result = build_target(self.build_config(), self.root / "evidence")
        self.assertEqual(result["status"], "build_failed")

    def test_old_hap_and_zero_exit_without_hvigor_success_are_not_passed(self):
        config = self.build_config()
        artifact = Path(config['target']['root']) / 'entry/build/default/old.hap'
        artifact.parent.mkdir(parents=True)
        artifact.write_bytes(b'old product')
        with patch('hmigbot_ios.build.subprocess.run', return_value=subprocess.CompletedProcess([], 0, b'', b'')):
            result = build_target(config, self.root / 'evidence')
        self.assertFalse(result['hvigor_success_marker'])
        self.assertEqual(result['status'], 'build_failed')

    def test_build_timeout_is_not_success(self):
        with patch("hmigbot_ios.build.subprocess.run", side_effect=subprocess.TimeoutExpired("hvigor", 1, output=b"partial")):
            result = build_target(self.build_config(), self.root / "evidence", timeout=1)
        self.assertTrue(result["timeout"])
        self.assertEqual(result["status"], "build_failed")

    def test_cli_error_is_structured_and_no_output_created(self):
        output = self.root / "rejected"
        result = subprocess.run([sys.executable, str(ROOT / "scripts/ios2harmony.py"), "generate",
            "--source", str(ROOT / "tests/fixtures/unsupported"), "--output", str(output),
            "--sdk", "26.0.0", "--min-sdk", "6.0.2(22)", "--model-version", "6.0.2", "--bundle-name", "com.example.test"],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["status"], "error")
        self.assertFalse(output.exists())

    def test_portable_entry_works_away_from_development_directory(self):
        # Full ZIP/CRC/install/upgrade testing belongs to smoke_package.py. This
        # unit regression isolates relocatable imports without recompressing 1GB.
        copied = self.root / "copied/hmigbot-ios"
        for folder in ('src', 'scripts', 'tests/fixtures/swiftui_counter'):
            shutil.copytree(ROOT / folder, copied / folder,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        entry = self.root / "copied/hmigbot-ios/scripts/ios2harmony.py"
        result = subprocess.run([sys.executable, str(entry), "capabilities"], cwd=self.root, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        atoms = json.loads(result.stdout)["atoms"]
        self.assertEqual(len(atoms), 62)
        self.assertEqual(len({a["id"] for a in atoms}), 62)
        scan = subprocess.run([sys.executable, str(entry), "scan", "--source", str(entry.parents[1] / "tests/fixtures/swiftui_counter"),
                               "--output", str(self.root / "report")], cwd=self.root, capture_output=True, encoding="utf-8")
        self.assertEqual(scan.returncode, 0, scan.stderr)
        self.assertTrue((self.root / "report/facts.json").is_file())


if __name__ == "__main__":
    unittest.main()
