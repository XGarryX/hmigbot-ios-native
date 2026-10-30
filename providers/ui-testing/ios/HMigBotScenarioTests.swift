import Foundation
import XCTest

// This XCTest bundle queries only the explicitly selected XCUIApplication.
// It never uses XCUIScreen, a desktop API, arbitrary predicates or shell code.
@MainActor
final class HMigBotScenarioTests: XCTestCase {
    enum Failure: Error { case script(String), assertion(String) }
    var checkpoints: [[String: Any]] = []
    var completed: [[String: Any]] = []
    var nonce = ""

    func attachment(_ name: String, _ value: Any) throws {
        let data = try JSONSerialization.data(withJSONObject: value, options: [.sortedKeys])
        let item = XCTAttachment(data: data, uniformTypeIdentifier: "public.json")
        item.name = name
        item.lifetime = .keepAlways
        add(item)
    }

    func element(_ app: XCUIApplication, _ step: [String: Any]) throws -> XCUIElement {
        guard let identifier = step["identifier"] as? String, !identifier.isEmpty else {
            throw Failure.script("A stable accessibility identifier is required")
        }
        let query = app.descendants(matching: .any).matching(identifier: identifier)
        let result = query.firstMatch
        let timeout = step["timeout"] as? Double ?? 10
        var ready = false
        for _ in 0...(step["retries"] as? Int ?? 0) {
            if result.waitForExistence(timeout: timeout) { ready = true; break }
        }
        guard ready else {
            throw Failure.assertion("Element did not become available: " + identifier)
        }
        guard query.count == 1 else { throw Failure.script("Ambiguous accessibility identifier: " + identifier) }
        return result
    }

    func node(_ snapshot: XCUIElementSnapshot, _ depth: Int, _ remaining: inout Int) -> [String: Any] {
        remaining -= 1
        let f = snapshot.frame
        let frame: [String: Any] = ["x": f.origin.x, "y": f.origin.y, "width": f.width, "height": f.height]
        var value: [String: Any] = ["identifier": snapshot.identifier, "type": String(describing: snapshot.elementType),
            "label": snapshot.label, "enabled": snapshot.isEnabled, "selected": snapshot.isSelected, "frame": frame]
        if let raw = snapshot.value, snapshot.elementType != .secureTextField { value["value"] = String(describing: raw) }
        // SwiftUI hosting/container chains can exceed 16 before exposing the
        // actual labels. Keep a global node budget and report every truncation.
        if depth < 64 && remaining > 0 {
            var children: [[String: Any]] = []
            for child in snapshot.children {
                if remaining <= 0 { value["children_truncated"] = true; break }
                children.append(node(child, depth + 1, &remaining))
            }
            value["children"] = children
        } else if !snapshot.children.isEmpty { value["children_truncated"] = true }
        return value
    }

    func checkpoint(_ app: XCUIApplication, _ step: [String: Any]) throws {
        guard let id = step["id"] as? String else { throw Failure.script("Checkpoint id missing") }
        guard app.state == .runningForeground else { throw Failure.assertion("Selected app is not foreground") }
        let scope = step["scope"] as? String ?? "application"
        let target: XCUIElement = scope == "application" ? app : try element(app, step)
        if scope == "window" && target.elementType != .window { throw Failure.script("Window checkpoint did not identify an application window") }
        let image = XCTAttachment(screenshot: target.screenshot())
        image.name = "hmigbot." + nonce + "." + id + ".png"
        image.lifetime = .keepAlways
        add(image)
        var remaining = 1000
        let snapshot = try app.snapshot()
        let tree = node(snapshot, 0, &remaining)
        try attachment("hmigbot." + nonce + "." + id + ".hierarchy.json", [
            "schema_version": "hmigbot-xcui-hierarchy/1", "scope": "application_accessibility_snapshot",
            "captured_at": ISO8601DateFormatter().string(from: Date()), "node_limit": 1000, "depth_limit": 64,
            "nodes": [tree], "limitations": ["Not the full SwiftUI/UIKit internal view tree", "Custom-drawn content may be absent"]])
        checkpoints.append(["id": id, "status": "passed", "captured_at": ISO8601DateFormatter().string(from: Date())])
    }

    func testScenario() throws {
        continueAfterFailure = false
        guard let encoded = ProcessInfo.processInfo.environment["HMIGBOT_SCENARIO_BASE64"],
              let bytes = Data(base64Encoded: encoded),
              let config = try JSONSerialization.jsonObject(with: bytes) as? [String: Any],
              let bundle = config["bundle_id"] as? String,
              let run = config["run_id"] as? String,
              let scenario = config["scenario"] as? [String: Any],
              let steps = scenario["steps"] as? [[String: Any]],
              let settings = config["configuration"] as? [String: String] else {
            throw Failure.script("Missing or malformed scoped test request")
        }
        nonce = run
        let app = XCUIApplication(bundleIdentifier: bundle)
        app.launchArguments = ["-AppleLanguages", "(" + (settings["language"] ?? "en") + ")", "-AppleLocale", settings["locale"] ?? "en_US"]
        app.launchArguments += config["launch_arguments"] as? [String] ?? []
        app.launchEnvironment = config["launch_environment"] as? [String: String] ?? [:]
        app.terminate()
        app.launch()
        var result: [String: Any] = ["run_id": run, "bundle_id": bundle, "status": "running"]
        do {
            guard app.wait(for: .runningForeground, timeout: 20) else { throw Failure.assertion("Selected app did not launch") }
            for (index, step) in steps.enumerated() {
                guard let action = step["action"] as? String else { throw Failure.script("Missing action") }
                switch action {
                case "wait": _ = try element(app, step)
                case "tap":
                    let target = try element(app, step)
                    guard target.isHittable else { throw Failure.assertion("Element is not hittable") }
                    target.tap()
                case "type_text":
                    let target = try element(app, step)
                    guard let text = step["text"] as? String else { throw Failure.script("Missing text") }
                    target.tap(); target.typeText(text)
                case "assert":
                    let target = try element(app, step)
                    if let expected = step["label"] as? String, target.label != expected { throw Failure.assertion("Label mismatch: " + target.identifier) }
                    if let expected = step["value"] as? String, String(describing: target.value ?? "") != expected { throw Failure.assertion("Value mismatch: " + target.identifier) }
                    if let enabled = step["enabled"] as? Bool, target.isEnabled != enabled { throw Failure.assertion("Enabled mismatch") }
                case "swipe_up": try element(app, step).swipeUp()
                case "swipe_down": try element(app, step).swipeDown()
                case "checkpoint": try checkpoint(app, step)
                default: throw Failure.script("Unsupported action: " + action)
                }
                completed.append(["index": index, "action": action, "status": "passed"])
            }
            result["status"] = "passed"
            if let probe = scenario["configuration_probe"] as? String {
                if let element = try? self.element(app, ["identifier": probe, "timeout": 5.0]) {
                    let raw = (element.value as? String) ?? element.label
                    if let data = raw.data(using: .utf8), let observation = (try? JSONSerialization.jsonObject(with: data)) as? [String: String] {
                        result["observed_configuration"] = observation
                    }
                }
            }
        } catch {
            result["status"] = "failed"
            switch error {
            case Failure.assertion(let detail): result["failure_kind"] = "product_assertion"; result["error"] = detail
            case Failure.script(let detail): result["failure_kind"] = "scenario_script"; result["error"] = detail
            default: result["failure_kind"] = "test_infrastructure"; result["error"] = String(describing: error)
            }
        }
        result["checkpoints"] = checkpoints
        result["steps"] = completed
        result["captured_at"] = ISO8601DateFormatter().string(from: Date())
        try attachment("hmigbot." + nonce + ".run.json", result)
        app.terminate()
        if result["status"] as? String != "passed" { throw Failure.assertion(result["error"] as? String ?? "Scenario failed") }
    }
}
