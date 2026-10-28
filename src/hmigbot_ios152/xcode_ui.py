"""Official XCUITest observer on a newly created, session-owned Simulator.

No adb, private XCTest APIs, network server, or existing-device selection is used.
The JSON command queue is in the generated XCTest runner's actual data container.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import plistlib
import shutil
import signal
import subprocess
import time
import uuid


class XcodeUIError(RuntimeError):
    pass


def _atomic_json(path: Path, data: dict) -> None:
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def _targets(document: dict) -> list[dict]:
    if "TestConfigurations" in document:
        return [target for config in document["TestConfigurations"]
                for target in config.get("TestTargets", [])]
    return [value for key, value in document.items()
            if not key.startswith("__") and isinstance(value, dict)
            and "TestBundlePath" in value]


def _safe_artifact(queue: Path, relative: str) -> Path:
    candidate = (queue / relative).resolve()
    artifacts = (queue / "artifacts").resolve()
    if not candidate.is_relative_to(artifacts):
        raise XcodeUIError("Runner returned a path outside its artifact directory")
    return candidate


class XcodeUISession:
    """Create/start/observe/close one tool-owned Simulator.

    ``create_owned(workspace, app_path).start()`` creates a new device; it never
    attaches to booted or user-supplied device IDs. ``open(workspace)`` resumes
    only a session whose ownership marker and persisted UDID agree.
    """
    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()
        self.state_path = self.workspace / "session.json"
        self.state = json.loads(self.state_path.read_text())
        marker = json.loads((self.workspace / "ownership.json").read_text())
        if marker != {"session": self.state["session"], "udid": self.state["udid"]}:
            raise XcodeUIError("Simulator session ownership marker mismatch")
        self.env = {**os.environ, "DEVELOPER_DIR": self.state["developer_dir"]}
        self._process = None

    @classmethod
    def open(cls, workspace: str | Path) -> "XcodeUISession":
        return cls(workspace)

    @classmethod
    def create_owned(cls, workspace: str | Path, app_path: str | Path, *,
                     developer_dir: str = "/Applications/Xcode.app/Contents/Developer",
                     runtime: str | None = None, device_type: str | None = None,
                     max_seconds: int = 3600) -> "XcodeUISession":
        workspace = Path(workspace).resolve()
        app_path = Path(app_path).resolve()
        info = plistlib.loads((app_path / "Info.plist").read_bytes())
        bundle = info.get("CFBundleIdentifier")
        if not bundle or "iPhoneSimulator" not in info.get("CFBundleSupportedPlatforms", []):
            raise XcodeUIError("A built iPhoneSimulator .app with CFBundleIdentifier is required")
        workspace.mkdir(parents=True, exist_ok=True)
        if any(workspace.iterdir()):
            raise XcodeUIError("Create requires a new empty session workspace")
        nonce = uuid.uuid4().hex
        env = {**os.environ, "DEVELOPER_DIR": developer_dir}
        # Inventory is read-only; creation is the first device mutation.
        runtime_data = json.loads(subprocess.check_output(
            ["xcrun", "simctl", "list", "runtimes", "-j"], env=env))
        available = [item for item in runtime_data["runtimes"]
                     if item.get("isAvailable") and ".iOS-" in item["identifier"]]
        if runtime:
            available = [item for item in available if item["identifier"] == runtime]
        if not available:
            raise XcodeUIError("No matching available iOS Simulator runtime")
        selected = max(available, key=lambda item: tuple(int(n) for n in item["version"].split(".")))
        supported = selected.get("supportedDeviceTypes", [])
        if device_type:
            supported = [item for item in supported if item["identifier"] == device_type]
        else:
            supported = [item for item in supported if item.get("productFamily") == "iPhone"]
        if not supported:
            # Older simctl versions omit supportedDeviceTypes; require an explicit type.
            if not device_type:
                raise XcodeUIError("Runtime does not expose a supported iPhone device type; provide device_type")
            supported = [{"identifier": device_type}]
        argv = ["xcrun", "simctl", "create", "HMigBot-UI-" + nonce[:12],
                supported[0]["identifier"], selected["identifier"]]
        started = time.time()
        created = subprocess.run(argv, env=env, capture_output=True, text=True)
        (workspace / "create.stdout").write_text(created.stdout)
        (workspace / "create.stderr").write_text(created.stderr)
        _atomic_json(workspace / "create.command.json", {"argv": argv, "exit_code": created.returncode,
                                                        "started_at": started, "finished_at": time.time()})
        if created.returncode:
            raise XcodeUIError("simctl create failed: " + created.stderr.strip())
        udid = created.stdout.strip()
        try:
            uuid.UUID(udid)
        except ValueError as error:
            raise XcodeUIError("simctl create returned an invalid UDID") from error
        state = {"schema_version": 1, "session": nonce, "udid": udid,
                 "runtime": selected["identifier"], "device_type": supported[0]["identifier"],
                 "developer_dir": developer_dir, "app_path": str(app_path), "bundle_id": bundle,
                 "max_seconds": max(30, min(int(max_seconds), 28800)), "status": "created"}
        _atomic_json(workspace / "ownership.json", {"session": nonce, "udid": udid})
        _atomic_json(workspace / "session.json", state)
        return cls(workspace)

    def _save(self) -> None:
        _atomic_json(self.state_path, self.state)

    def _run(self, argv: list[str], *, timeout: float = 240, check: bool = True) -> subprocess.CompletedProcess:
        number = len(list((self.workspace / "logs").glob("*.command.json"))) if (self.workspace / "logs").exists() else 0
        logs = self.workspace / "logs"
        logs.mkdir(exist_ok=True)
        stem = logs / f"{number:04d}"
        started = time.time()
        try:
            result = subprocess.run(argv, env=self.env, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            for extension, content in [(".stdout", error.stdout), (".stderr", error.stderr)]:
                stem.with_suffix(extension).write_text(content.decode(errors="replace") if isinstance(content, bytes) else (content or ""))
            _atomic_json(stem.with_suffix(".command.json"), {"argv": argv, "exit_code": None,
                         "timeout": timeout, "started_at": started, "finished_at": time.time()})
            raise XcodeUIError("Official tool timed out: " + " ".join(argv[:3])) from error
        stem.with_suffix(".stdout").write_text(result.stdout)
        stem.with_suffix(".stderr").write_text(result.stderr)
        _atomic_json(stem.with_suffix(".command.json"), {"argv": argv, "exit_code": result.returncode,
                     "started_at": started, "finished_at": time.time()})
        if check and result.returncode:
            raise XcodeUIError(f"Official tool failed ({result.returncode}); see {stem}.stderr and .stdout")
        return result

    def _simctl(self, action: str, *arguments: str, **kwargs) -> subprocess.CompletedProcess:
        if self.state.get("status") == "closed":
            raise XcodeUIError("Simulator session is closed")
        # There is deliberately no booted alias, device argument, or global shutdown.
        return self._run(["xcrun", "simctl", action, self.state["udid"], *arguments], **kwargs)

    def _probe_snapshot(self) -> bool:
        probe = self.workspace / "SnapshotProbe.swift"
        probe.write_text("import XCTest\n@MainActor func probe(_ a: XCUIApplication) throws {\n"
                         "let s = try a.snapshot(); _ = s.dictionaryRepresentation; _ = s.children\n}\n")
        sdk = self._run(["xcrun", "--sdk", "iphonesimulator", "--show-sdk-path"]).stdout.strip()
        framework = str(Path(self.state["developer_dir"]) / "Platforms/iPhoneSimulator.platform/Developer/Library/Frameworks")
        arch = "arm64" if os.uname().machine == "arm64" else "x86_64"
        result = self._run(["xcrun", "swiftc", "-typecheck", "-target", arch + "-apple-ios17.0-simulator",
                            "-sdk", sdk, "-F", framework, "-module-cache-path", str(self.workspace / "module-cache"),
                            str(probe)], check=False)
        return result.returncode == 0

    def start(self, *, timeout: float = 180) -> "XcodeUISession":
        if self.state["status"] != "created":
            raise XcodeUIError("Only a freshly created session can start")
        provider = Path(__file__).resolve().parents[2] / "providers/xcode-ui"
        project = self.workspace / "provider"
        shutil.copytree(provider, project)
        has_snapshot = self._probe_snapshot()
        self.state["snapshot_public_api"] = has_snapshot
        self._save()
        derived = self.workspace / "DerivedData"
        build = ["xcrun", "xcodebuild", "build-for-testing", "-project", str(project / "HMigBotUI.xcodeproj"),
                 "-scheme", "HMigBotUI", "-destination", "generic/platform=iOS Simulator",
                 "-derivedDataPath", str(derived), "CODE_SIGNING_ALLOWED=NO"]
        if has_snapshot:
            build.append("SWIFT_ACTIVE_COMPILATION_CONDITIONS=$(inherited) HMIGBOT_HAS_XCUI_SNAPSHOT")
        self._run(build, timeout=600)
        runs = list((derived / "Build/Products").glob("*.xctestrun"))
        if len(runs) != 1:
            raise XcodeUIError("Expected exactly one generated xctestrun")
        document = plistlib.loads(runs[0].read_bytes())
        targets = _targets(document)
        if len(targets) != 1:
            raise XcodeUIError("Expected one UI test target")
        target = targets[0]
        target["UITargetAppPath"] = self.state["app_path"]
        target["UITargetAppBundleIdentifier"] = self.state["bundle_id"]
        target["ParallelizationEnabled"] = False
        environment = target.setdefault("EnvironmentVariables", {})
        environment.update({"HMIGBOT_SESSION": self.state["session"],
                            "HMIGBOT_AUT_BUNDLE_ID": self.state["bundle_id"],
                            "HMIGBOT_MAX_SECONDS": str(self.state["max_seconds"])})
        self.state["runner_bundle_id"] = target.get("TestHostBundleIdentifier", "org.hmigbot.observer.tests.xctrunner")
        self.state["runner_target"] = target.get("BlueprintName", "HMigBotUITests")
        # Keep __TESTROOT__ expansion relative to the original generated file directory.
        patched = runs[0].with_name("HMigBotSession.xctestrun")
        patched.write_bytes(plistlib.dumps(document))
        self.state["xctestrun"] = str(patched)
        self._save()
        self._simctl("boot")
        self._simctl("bootstatus", "-b", timeout=300)
        from .native_source_build import app_build_identity
        self.state["source_app_build"] = app_build_identity(self.state["app_path"])
        self._save()
        self._simctl("install", self.state["app_path"])
        argv = ["xcrun", "xcodebuild", "test-without-building", "-xctestrun", str(patched),
                "-destination", "platform=iOS Simulator,id=" + self.state["udid"],
                "-parallel-testing-enabled", "NO", "-maximum-concurrent-test-simulator-destinations", "1",
                "-only-testing:HMigBotUITests/DriverTests/testServe", "-resultBundlePath", str(self.workspace / "Runner.xcresult")]
        stdout = (self.workspace / "runner.stdout").open("w")
        stderr = (self.workspace / "runner.stderr").open("w")
        try:
            self._process = subprocess.Popen(argv, env=self.env, stdout=stdout, stderr=stderr, start_new_session=True)
        finally:
            stdout.close()
            stderr.close()
        self.state.update({"runner_pid": self._process.pid, "runner_argv": argv,
                           "runner_started_at": time.time(), "status": "starting"})
        self._save()
        _atomic_json(self.workspace / "runner.command.json", {"argv": argv, "pid": self._process.pid,
                     "started_at": self.state["runner_started_at"], "exit_code": None})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._process.poll() is not None:
                raise XcodeUIError("XCTest runner exited before ready; inspect runner.stdout/stderr")
            result = self._simctl("get_app_container", self.state["runner_bundle_id"], "data", check=False)
            if result.returncode == 0:
                queue = Path(result.stdout.strip()) / "Documents/hmigbot" / self.state["session"]
                ready = queue / "ready.json"
                if ready.is_file():
                    message = json.loads(ready.read_text())
                    if message.get("session") != self.state["session"]:
                        raise XcodeUIError("Runner ready nonce mismatch")
                    self.state.update({"queue": str(queue), "status": "ready", "ready_at": time.time()})
                    self._save()
                    return self
            time.sleep(0.5)
        raise XcodeUIError("Timed out waiting for actual XCTest queue; inspect runner.stdout/stderr")

    def _record_response(self, response: dict, queue: Path, evidence: Path, request_id: str) -> dict:
        copies = {}
        try:
            for group in [response.get("result"), response.get("evidence")]:
                if not isinstance(group, dict):
                    continue
                for name in ["hierarchy", "screenshot"]:
                    if not isinstance(group.get(name), str):
                        continue
                    original = _safe_artifact(queue, group[name])
                    destination = self.workspace / "artifacts" / original.name
                    destination.parent.mkdir(exist_ok=True)
                    shutil.copy2(original, destination)
                    copies[group[name]] = str(destination)
        except (OSError, XcodeUIError) as error:
            if response.get("ok"):
                raise XcodeUIError("Successful response has unavailable native artifacts") from error
            # An evidence failure must never replace the already observed UI error.
            response["evidence_status"] = "failed"
            response["evidence_error"] = {"code": "evidence_copy_failed", "message": str(error)}
        if copies:
            response["artifact_copies"] = copies
        _atomic_json(evidence / (request_id + ".response.json"), response)
        return response

    def command(self, operation: str, arguments: dict | None = None, *,
                timeout: float | None = None, evidence_timeout: float = 5) -> dict:
        # XCTest can spend about 60 seconds waiting for idle before continuing.
        # Leave room for the real completion response without private idle APIs.
        if timeout is None:
            timeout = (180 if operation == "launch" or
                       operation == "tap" and (arguments or {}).get("scope") == "springboard"
                       else 120 if operation == "long_press" else 60)
        for name, value in [("Command timeout", timeout), ("Evidence timeout", evidence_timeout)]:
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise XcodeUIError(name + " must be positive and finite")
        if self.state["status"] != "ready":
            raise XcodeUIError("XCTest observer is not ready")
        queue = Path(self.state["queue"])
        request_id = uuid.uuid4().hex
        command = {"id": request_id, "session": self.state["session"],
                   "operation": operation, "arguments": arguments or {}, "issued_at": time.time(),
                   "timeout_seconds": timeout, "evidence_timeout_seconds": evidence_timeout}
        lock = self.workspace / "command.lock"
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as error:
            raise XcodeUIError("Another command is in flight for this observer") from error
        os.close(descriptor)
        try:
            evidence = self.workspace / "requests"
            evidence.mkdir(exist_ok=True)
            _atomic_json(evidence / (request_id + ".request.json"), command)
            _atomic_json(queue / "commands" / (request_id + ".json"), command)
            result_path = queue / "results" / (request_id + ".json")
            deadline = time.monotonic() + timeout
            evidence_deadline = None
            original_error = None
            last_raw = None
            while True:
                if result_path.is_file():
                    raw = result_path.read_text()
                    response = json.loads(raw)
                    if raw != last_raw:
                        _atomic_json(evidence / (request_id + ".raw-response.json"), response)
                        last_raw = raw
                    if response.get("session") != self.state["session"] or response.get("id") != request_id:
                        self.state["status"] = "protocol_error"
                        self._save()
                        raise XcodeUIError("Observer response identity mismatch")
                    if original_error is not None and (response.get("ok") is not False or response.get("error") != original_error.get("error")):
                        response = dict(original_error)
                        response.update(evidence_status="failed", session_invalidated=True,
                            evidence_error={"code": "original_error_changed", "message": "Observer changed the published original error"})
                        self.state["status"] = "protocol_error"
                        self._save()
                        return self._record_response(response, queue, evidence, request_id)
                    if response.get("ok") is False and response.get("evidence_status") == "pending":
                        if original_error is None:
                            original_error = dict(response)
                            evidence_deadline = min(deadline, time.monotonic() + evidence_timeout)
                        if self._process is not None and self._process.poll() is not None:
                            response = dict(original_error)
                            response.update(evidence_status="failed", session_invalidated=True,
                                evidence_error={"code": "runner_exited", "message": "Observer exited during error evidence collection"})
                            self.state["status"] = "runner_exited"
                            self._save()
                            return self._record_response(response, queue, evidence, request_id)
                        if time.monotonic() >= evidence_deadline:
                            response = dict(original_error)
                            response.update(evidence_status="timeout", session_invalidated=True,
                                evidence_error={"code": "evidence_timeout", "message": "Synchronous evidence may still be running; close this observer before reuse"})
                            self.state["status"] = "evidence_timeout"
                            self.state["last_error_request_id"] = request_id
                            self._save()
                            return self._record_response(response, queue, evidence, request_id)
                    else:
                        return self._record_response(response, queue, evidence, request_id)
                elif self._process is not None and self._process.poll() is not None:
                    self.state["status"] = "runner_exited"
                    self.state["last_error_request_id"] = request_id
                    self.state["runner_exit_code"] = self._process.returncode
                    self._save()
                    raise XcodeUIError("XCTest runner died while executing command")
                if time.monotonic() >= deadline and original_error is None:
                    self.state["status"] = "command_timeout"
                    self._save()
                    raise XcodeUIError("Observer command timed out; session must close before reuse")
                next_deadline = evidence_deadline if original_error is not None else deadline
                interval = 0.05 if original_error is not None else 0.1
                time.sleep(min(interval, max(0, next_deadline - time.monotonic())))
        finally:
            lock.unlink(missing_ok=True)

    def capture(self, output_dir: str | Path, *, timeout: float = 60, scope: str = "app") -> dict:
        """Return {png, native_json, observation, response}; originals remain in queue.

        This is raw source observation only. Arrival/baseline/canonical placement
        are responsibilities of the visual pipeline's existing consumer gates.
        """
        if scope not in {"app", "springboard"}:
            raise XcodeUIError("Capture scope must be app or springboard")
        response = self.command("capture", {"scope": scope}, timeout=timeout)
        if not response.get("ok"):
            raise XcodeUIError("Capture failed: " + json.dumps(response.get("error")))
        result = response["result"]
        queue = Path(self.state["queue"])
        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        native_source = _safe_artifact(queue, result["hierarchy"])
        png_source = _safe_artifact(queue, result["screenshot"])
        native = output / (response["id"] + ".native.json")
        png = output / (response["id"] + ".png")
        shutil.copy2(native_source, native)
        shutil.copy2(png_source, png)
        observation = json.loads(native.read_text())
        if scope == "app" and (observation["app_state_before"] != 4 or observation["app_state_after"] != 4):
            raise XcodeUIError("Capture drifted away from source foreground")
        if scope == "springboard" and (observation.get("bundle_id") != "com.apple.springboard"
                                      or observation.get("scope") != "springboard"):
            raise XcodeUIError("System capture did not observe the requested SpringBoard scope")
        return {"png": str(png), "native_json": str(native), "observation": observation,
                "sha256": {"png": hashlib.sha256(png.read_bytes()).hexdigest(),
                           "native_json": hashlib.sha256(native.read_bytes()).hexdigest()},
                "response": response}

    def close(self) -> dict:
        if self.state["status"] == "closed":
            return self.state
        if self.state["status"] == "ready":
            try:
                self.command("stop", timeout=10)
            except XcodeUIError:
                pass
        if self._process is not None:
            try:
                code = self._process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                os.killpg(self._process.pid, signal.SIGTERM)
                try:
                    code = self._process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(self._process.pid, signal.SIGKILL)
                    code = self._process.wait(timeout=10)
            self.state["runner_exit_code"] = code
            _atomic_json(self.workspace / "runner.command.json", {"argv": self.state["runner_argv"],
                         "pid": self.state["runner_pid"], "started_at": self.state["runner_started_at"],
                         "finished_at": time.time(), "exit_code": code})
        elif self.state.get("runner_pid"):
            # A resumed CLI session verifies the persisted child command before signalling it.
            pid = self.state["runner_pid"]
            # Give testServe() time to return and xcodebuild time to finish its result bundle.
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                actual = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True).stdout
                if not actual or "<defunct>" in actual:
                    break
                if self.state.get("xctestrun", "\0") not in actual or "xcodebuild" not in actual:
                    break
                time.sleep(0.2)
            else:
                try:
                    os.killpg(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            self.state["runner_exit_observation"] = "resumed_process_not_waitable"
        self._simctl("shutdown", check=False)
        deleted = self._simctl("delete", check=False)
        self.state.update({"status": "closed" if deleted.returncode == 0 else "cleanup_failed", "closed_at": time.time()})
        self._save()
        return self.state

    def __enter__(self) -> "XcodeUISession":
        return self.start()

    def __exit__(self, *unused) -> None:
        self.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    start = sub.add_parser("start")
    start.add_argument("--workspace", required=True)
    start.add_argument("--app", required=True)
    start.add_argument("--runtime")
    start.add_argument("--device-type")
    start.add_argument("--developer-dir", default="/Applications/Xcode.app/Contents/Developer")
    start.add_argument("--max-seconds", type=int, default=3600)
    command = sub.add_parser("command")
    command.add_argument("--workspace", required=True)
    command.add_argument("--operation", required=True)
    command.add_argument("--arguments", default="{}", help="JSON object of operation arguments")
    command.add_argument("--timeout", type=float, help="Override bounded operation timeout (launch/system tap 180s, long_press 120s, others 60s)")
    capture = sub.add_parser("capture")
    capture.add_argument("--workspace", required=True)
    capture.add_argument("--output", required=True)
    capture.add_argument("--scope", choices=["app", "springboard"], default="app")
    close = sub.add_parser("close")
    close.add_argument("--workspace", required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "start":
            session = XcodeUISession.create_owned(args.workspace, args.app, developer_dir=args.developer_dir,
                         runtime=args.runtime, device_type=args.device_type, max_seconds=args.max_seconds)
            try:
                session.start()
            except BaseException:
                session.close()
                raise
            result = session.state
        else:
            session = XcodeUISession.open(args.workspace)
            if args.action == "command":
                result = session.command(args.operation, json.loads(args.arguments), timeout=args.timeout)
            elif args.action == "capture":
                result = session.capture(args.output, scope=args.scope)
            else:
                result = session.close()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (XcodeUIError, OSError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
