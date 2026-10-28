"""Host protocol and optional real XCUITest smoke.

Set HMIGBOT_XCODE_UI_SMOKE_APP to a built neutral iPhoneSimulator .app to run
integration. Every integration run creates and deletes its own Simulator.
"""
import json
import os
import shutil
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from hmigbot_ios152.xcode_ui import XcodeUISession, XcodeUIError, _safe_artifact, _targets, _atomic_json


class ObserverProtocolTests(unittest.TestCase):
    def session(self, root):
        queue = root / "container/Documents/hmigbot/nonce"
        (queue / "commands").mkdir(parents=True)
        (queue / "results").mkdir()
        (queue / "artifacts").mkdir()
        identity = {"session": "a" * 32, "udid": "11223344-5566-7788-9900-AABBCCDDEEFF"}
        (root / "ownership.json").write_text(json.dumps(identity))
        (root / "session.json").write_text(json.dumps({**identity, "status": "ready",
            "queue": str(queue), "developer_dir": "/Applications/Xcode.app/Contents/Developer"}))
        return XcodeUISession.open(root), queue

    def test_ownership_mismatch_blocks_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session, _ = self.session(root)
            (root / "ownership.json").write_text(json.dumps({"session": "other", "udid": session.state["udid"]}))
            with self.assertRaisesRegex(XcodeUIError, "ownership"):
                XcodeUISession.open(root)

    def test_queue_request_response_and_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session, queue = self.session(root)
            errors = []
            def responder():
                try:
                    deadline = time.monotonic() + 3
                    while time.monotonic() < deadline:
                        files = list((queue / "commands").glob("*.json"))
                        if files:
                            request = json.loads(files[0].read_text())
                            (queue / "artifacts/native.json").write_text('{"platform":"ios"}')
                            (queue / "artifacts/source.png").write_bytes(b"source evidence bytes")
                            response = {"session": request["session"], "id": request["id"],
                                        "ok": False, "error": {"code": "not_found"},
                                        "evidence": {"hierarchy": "artifacts/native.json", "screenshot": "artifacts/source.png"}}
                            (queue / "results" / files[0].name).write_text(json.dumps(response))
                            return
                        time.sleep(0.01)
                    raise AssertionError("No queue request")
                except BaseException as error:
                    errors.append(error)
            worker = threading.Thread(target=responder)
            worker.start()
            response = session.command("find", {"selector": {"identifier": "missing"}}, timeout=3)
            worker.join(3)
            self.assertEqual(errors, [])
            self.assertFalse(response["ok"])
            self.assertEqual(response["error"]["code"], "not_found")
            evidence = root / "requests" / (response["id"] + ".request.json")
            self.assertEqual(json.loads(evidence.read_text())["arguments"]["selector"]["identifier"], "missing")
            self.assertFalse((root / "command.lock").exists())
            shutil.rmtree(queue)
            self.assertEqual(Path(response["artifact_copies"]["artifacts/source.png"]).read_bytes(), b"source evidence bytes")
            self.assertEqual(json.loads(Path(response["artifact_copies"]["artifacts/native.json"]).read_text())["platform"], "ios")

    def test_inflight_command_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session, queue = self.session(root)
            (root / "command.lock").write_text("another owner")
            with self.assertRaisesRegex(XcodeUIError, "in flight"):
                session.command("tap", {"selector": {"identifier": "button"}})
            self.assertEqual(list((queue / "commands").glob("*.json")), [])
            self.assertEqual((root / "command.lock").read_text(), "another owner")

    def test_invalid_timeout_never_enqueues_an_action(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session, queue = self.session(root)
            for timeout in [0, -1, float("inf"), float("nan")]:
                with self.assertRaisesRegex(XcodeUIError, "positive and finite"):
                    session.command("tap", {"selector": {"identifier": "button"}}, timeout=timeout)
            self.assertEqual(list((queue / "commands").glob("*.json")), [])
            self.assertFalse((root / "command.lock").exists())

    def test_timeout_invalidates_session_and_releases_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session, _ = self.session(root)
            with self.assertRaisesRegex(XcodeUIError, "timed out"):
                session.command("capture", timeout=0.01)
            self.assertEqual(session.state["status"], "command_timeout")
            self.assertFalse((root / "command.lock").exists())
            with self.assertRaisesRegex(XcodeUIError, "not ready"):
                session.command("ping")

    def test_artifact_traversal_and_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, queue = self.session(root)
            for relative in ["../../secret", "/etc/passwd"]:
                with self.assertRaises(XcodeUIError):
                    _safe_artifact(queue, relative)
            (queue / "artifacts/escape").symlink_to(root)
            with self.assertRaises(XcodeUIError):
                _safe_artifact(queue, "artifacts/escape/session.json")
            self.assertEqual(_safe_artifact(queue, "artifacts/tree.json"), (queue / "artifacts/tree.json").resolve())

    def pending_responder(self, root, queue, finish=None):
        """Fake queue publication only; does not model or claim AX cancellation."""
        errors = []
        def respond():
            try:
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    files = list((queue / "commands").glob("*.json"))
                    if files:
                        request = json.loads(files[0].read_text())
                        response = {"id": request["id"], "session": request["session"],
                            "ok": False, "error": {"code": "ambiguous", "message": "Two native elements"},
                            "query": request["arguments"].get("selector"), "request_scope": "springboard",
                            "evidence_status": "pending"}
                        path = queue / "results" / files[0].name
                        _atomic_json(path, response)
                        if finish:
                            seen = root / "requests" / (request["id"] + ".raw-response.json")
                            while time.monotonic() < deadline and not seen.exists():
                                time.sleep(0.005)
                            if not seen.exists(): raise AssertionError("Host did not read original error")
                            finish(response, path)
                        return
                    time.sleep(0.005)
                raise AssertionError("No observer request")
            except BaseException as error:
                errors.append(error)
        worker = threading.Thread(target=respond, daemon=True)
        worker.start()
        return worker, errors

    def test_pending_error_timeout_preserves_error_and_invalidates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); session, queue = self.session(root)
            worker, errors = self.pending_responder(root, queue)
            started = time.monotonic()
            result = session.command("find", {"scope": "springboard", "selector": {"label": "duplicate"}},
                                     timeout=1, evidence_timeout=0.02)
            elapsed = time.monotonic() - started
            worker.join(3)
            self.assertEqual(errors, [])
            self.assertLess(elapsed, 0.5)
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"]["code"], "ambiguous")
            self.assertEqual(result["query"], {"label": "duplicate"})
            self.assertEqual(result["evidence_status"], "timeout")
            self.assertEqual(session.state["status"], "evidence_timeout")
            with self.assertRaisesRegex(XcodeUIError, "not ready"):
                session.command("ping")
            raw = json.loads((root / "requests" / (result["id"] + ".raw-response.json")).read_text())
            self.assertEqual(raw["evidence_status"], "pending")
            self.assertFalse((root / "command.lock").exists())

    def test_evidence_budget_does_not_extend_command_deadline(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); session, queue = self.session(root)
            worker, errors = self.pending_responder(root, queue)
            started = time.monotonic()
            result = session.command("find", {}, timeout=0.12, evidence_timeout=5)
            elapsed = time.monotonic() - started
            worker.join(3)
            self.assertEqual(errors, [])
            self.assertLess(elapsed, 0.4)
            self.assertEqual(result["evidence_status"], "timeout")
            self.assertEqual(result["error"]["code"], "ambiguous")

    def test_completed_pending_evidence_preserves_original_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); session, queue = self.session(root)
            def finish(response, path):
                (queue / "artifacts/scene.json").write_text('{"scope":"springboard"}')
                response.update(evidence_status="complete", evidence={"hierarchy": "artifacts/scene.json"})
                _atomic_json(path, response)
            worker, errors = self.pending_responder(root, queue, finish)
            result = session.command("find", {}, timeout=1, evidence_timeout=0.5)
            worker.join(3)
            self.assertEqual(errors, [])
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"]["code"], "ambiguous")
            self.assertEqual(result["evidence_status"], "complete")
            self.assertTrue(Path(result["artifact_copies"]["artifacts/scene.json"]).is_file())
            self.assertEqual(session.state["status"], "ready")

    def test_failed_evidence_still_returns_original_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); session, queue = self.session(root)
            def finish(response, path):
                response.update(evidence_status="failed", evidence_error="Native snapshot unavailable")
                _atomic_json(path, response)
            worker, errors = self.pending_responder(root, queue, finish)
            result = session.command("find", {}, timeout=1, evidence_timeout=0.5)
            worker.join(3)
            self.assertEqual(errors, [])
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"]["code"], "ambiguous")
            self.assertEqual(result["evidence_status"], "failed")
            self.assertEqual(session.state["status"], "ready")

    def test_published_error_cannot_be_replaced_with_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); session, queue = self.session(root)
            def finish(response, path):
                changed = {"id":response["id"],"session":response["session"],"ok":True,"result":{}}
                _atomic_json(path, changed)
            worker, errors = self.pending_responder(root, queue, finish)
            result = session.command("find", {}, timeout=1, evidence_timeout=0.5)
            worker.join(3)
            self.assertEqual(errors, [])
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"]["code"], "ambiguous")
            self.assertEqual(result["evidence_error"]["code"], "original_error_changed")
            self.assertEqual(session.state["status"], "protocol_error")

    def test_dead_owned_popen_invalidates_before_raising(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); session, queue = self.session(root)
            class DeadProcess:
                returncode = 65
                def poll(self): return self.returncode
            session._process = DeadProcess()
            with self.assertRaisesRegex(XcodeUIError, "runner died while executing command"):
                session.command("type_text", {"selector":{"identifier":"input"},"text":"x"}, timeout=0.2)
            self.assertEqual(session.state["status"], "runner_exited")
            saved = json.loads((root / "session.json").read_text())
            self.assertEqual(saved["status"], "runner_exited")
            self.assertEqual(saved["runner_exit_code"], 65)
            self.assertTrue(saved["last_error_request_id"])
            count = len(list((queue / "commands").glob("*.json")))
            with self.assertRaisesRegex(XcodeUIError, "not ready"):
                session.command("ping")
            self.assertEqual(len(list((queue / "commands").glob("*.json"))), count)

    def test_resumed_unknown_worker_uses_honest_deadline(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); session, queue = self.session(root)
            session.state["runner_pid"] = 2147483000
            session._save()
            resumed = XcodeUISession.open(root)
            self.assertIsNone(resumed._process)
            with self.assertRaisesRegex(XcodeUIError, "command timed out"):
                resumed.command("ping", timeout=0.02)
            self.assertEqual(resumed.state["status"], "command_timeout")
            self.assertEqual(json.loads((root / "session.json").read_text())["status"], "command_timeout")
            count = len(list((queue / "commands").glob("*.json")))
            with self.assertRaisesRegex(XcodeUIError, "not ready"):
                resumed.command("ping")
            self.assertEqual(len(list((queue / "commands").glob("*.json"))), count)

    def test_generated_xctestrun_formats(self):
        target = {"TestBundlePath": "__TESTROOT__/tests.xctest", "BlueprintName": "tests"}
        self.assertEqual(_targets({"TestConfigurations": [{"TestTargets": [target]}]}), [target])
        self.assertEqual(_targets({"tests": target, "__xctestrun_metadata__": {"FormatVersion": 1}}), [target])


@unittest.skipUnless(os.environ.get("HMIGBOT_XCODE_UI_SMOKE_APP"), "Set neutral Simulator app for real XCUITest smoke")
class RealObserverSmoke(unittest.TestCase):
    def test_real_owned_simulator_capture(self):
        with tempfile.TemporaryDirectory(prefix="hmigbot-ui-smoke-") as directory:
            session = XcodeUISession.create_owned(Path(directory) / "session", os.environ["HMIGBOT_XCODE_UI_SMOKE_APP"])
            try:
                session.start()
                self.assertTrue(session.command("ping")["ok"])
                self.assertTrue(session.command("launch")["ok"])
                capture = session.capture(Path(directory) / "capture")
                self.assertGreater(Path(capture["png"]).stat().st_size, 1000)
                self.assertEqual(capture["observation"]["platform"], "ios")
                self.assertTrue(capture["observation"]["tree"]["exists"])
                self.assertGreater(capture["observation"]["screenshot"]["pixel_size"]["width"], 0)
            finally:
                self.assertEqual(session.close()["status"], "closed")


if __name__ == "__main__":
    unittest.main()
