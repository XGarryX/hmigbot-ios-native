"""Source observation provenance contracts; fixtures do not execute an app."""
import hashlib
import json
from pathlib import Path
import plistlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hmigbot_ios.core import MigrationError
from hmigbot_ios152.native_source_build import app_build_identity


class SourceBuildIdentityTests(unittest.TestCase):
    def fixture(self,root,validation='passed'):
        root=root.resolve()
        app=root/'DerivedData/Build/Products/Release-iphonesimulator/Neutral.app'
        app.mkdir(parents=True);(app/'Neutral').write_bytes(b'owned provenance fixture, not executable')
        (app/'Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier':'org.neutral.source','CFBundleExecutable':'Neutral'}))
        record={'app':str(app),'app_binary_sha256':hashlib.sha256((app/'Neutral').read_bytes()).hexdigest(),
                'exit_code':0,'signing_mode':'simulator-adhoc','source_sha256':'source-snapshot',
                'simulator_entitlements':{'validation':validation}}
        (root/'build.json').write_text(json.dumps(record));return app

    def test_failed_capability_validation_is_never_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=self.fixture(Path(tmp),'failed')
            with self.assertRaisesRegex(MigrationError,'failed validation'):app_build_identity(app)

    def test_successful_record_binds_exact_product_and_source_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=self.fixture(Path(tmp));value=app_build_identity(app)
            self.assertTrue(value['build_record_binding'])
            self.assertEqual('source-snapshot',value['source_sha256'])
            self.assertEqual('simulator-adhoc',value['signing_mode'])
            self.assertEqual(hashlib.sha256((Path(tmp)/'build.json').read_bytes()).hexdigest(),value['build_record_sha256'])

    def test_changed_product_is_rejected_and_unrecorded_qa_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=self.fixture(Path(tmp));(app/'Neutral').write_bytes(b'changed product')
            with self.assertRaisesRegex(MigrationError,'differs from its recorded build'):app_build_identity(app)
            (Path(tmp)/'build.json').unlink()
            value=app_build_identity(app);self.assertFalse(value['build_record_binding'])
            self.assertEqual('unrecorded',value['signing_mode'])


if __name__=='__main__':unittest.main()
