import Foundation
import XCTest
import UIKit

private struct DriverError: Error {
    let code: String
    let message: String
}

@MainActor
final class DriverTests: XCTestCase {
    private var app: XCUIApplication!
    private var root: URL!
    private var session = ""
    private var bundleID = ""

    func testServe() throws {
        continueAfterFailure = false
        let environment = ProcessInfo.processInfo.environment
        session = try required(environment["HMIGBOT_SESSION"], "session")
        guard session.range(of: "^[a-f0-9]{32}$", options: .regularExpression) != nil else {
            throw DriverError(code: "invalid_session", message: "Invalid queue nonce")
        }
        let bundle = try required(environment["HMIGBOT_AUT_BUNDLE_ID"], "bundle ID")
        bundleID = bundle
        app = XCUIApplication(bundleIdentifier: bundle)
        root = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("hmigbot").appendingPathComponent(session)
        for subdirectory in ["commands", "results", "artifacts"] {
            try FileManager.default.createDirectory(at: root.appendingPathComponent(subdirectory), withIntermediateDirectories: true)
        }
        try write(["schema_version": 1, "session": session, "bundle_id": bundle,
                   "ready_at": Date().timeIntervalSince1970], to: root.appendingPathComponent("ready.json"))
        let duration = min(max(Double(environment["HMIGBOT_MAX_SECONDS"] ?? "3600") ?? 3600, 30), 28800)
        let deadline = Date().addingTimeInterval(duration)
        while Date() < deadline {
            let paths = try FileManager.default.contentsOfDirectory(at: root.appendingPathComponent("commands"), includingPropertiesForKeys: nil)
                .filter { $0.pathExtension == "json" }.sorted { $0.lastPathComponent < $1.lastPathComponent }
            if let path = paths.first {
                let shouldStop = process(path)
                if shouldStop { return }
            } else {
                RunLoop.current.run(until: Date().addingTimeInterval(0.1))
            }
        }
        throw DriverError(code: "session_expired", message: "Observer maximum session duration reached")
    }

    private func required(_ value: String?, _ field: String) throws -> String {
        guard let value, !value.isEmpty else { throw DriverError(code: "invalid_request", message: "Missing \(field)") }
        return value
    }

    private func write(_ object: Any, to path: URL) throws {
        try JSONSerialization.data(withJSONObject: object, options: [.sortedKeys, .prettyPrinted]).write(to: path, options: .atomic)
    }

    private func process(_ path: URL) -> Bool {
        var id = path.deletingPathExtension().lastPathComponent
        var operation = ""
        var requestScope = "app"
        var requestQuery: Any = NSNull()
        let started = Date().timeIntervalSince1970
        var response: [String: Any] = ["schema_version": 1, "session": session, "started_at": started]
        defer { try? FileManager.default.removeItem(at: path) }
        do {
            guard let command = try JSONSerialization.jsonObject(with: Data(contentsOf: path)) as? [String: Any],
                  let requestID = command["id"] as? String,
                  requestID == id,
                  requestID.range(of: "^[a-f0-9]{32}$", options: .regularExpression) != nil,
                  command["session"] as? String == session else {
                throw DriverError(code: "invalid_request", message: "Bad session or request ID")
            }
            id = requestID
            operation = try required(command["operation"] as? String, "operation")
            let arguments = command["arguments"] as? [String: Any] ?? [:]
            requestScope = arguments["scope"] as? String ?? "app"
            requestQuery = arguments["selector"] ?? NSNull()
            let value = try execute(operation, arguments: arguments, id: id)
            response["ok"] = true
            response["result"] = value
        } catch let error as DriverError {
            response["ok"] = false
            response["error"] = ["code": error.code, "message": error.message]
        } catch {
            response["ok"] = false
            response["error"] = ["code": "operation_failed", "message": String(describing: error)]
        }
        response["id"] = id
        response["operation"] = operation
        response["finished_at"] = Date().timeIntervalSince1970
        response["request_scope"] = requestScope
        response["query"] = requestQuery
        if response["ok"] as? Bool == false {
            // Publish the original error before any synchronous AX evidence work.
            // Host owns a separate bounded wait; this does not cancel AX calls.
            response["error_at"] = Date().timeIntervalSince1970
            response["evidence_status"] = "pending"
            try? write(response, to: root.appendingPathComponent("results/\(id).json"))
            let evidenceScope = requestScope == "springboard" || app.state != .runningForeground ? "springboard" : "app"
            do {
                response["evidence"] = try capture(id: id, includeScreenshot: true,
                                                    scope: evidenceScope, requestedScope: requestScope)
                response["evidence_status"] = "complete"
            } catch {
                response["evidence_status"] = "failed"
                response["evidence_error"] = String(describing: error)
            }
            response["evidence_finished_at"] = Date().timeIntervalSince1970
        }
        try? write(response, to: root.appendingPathComponent("results/\(id).json"))
        return operation == "stop"
    }

    private func scopedApplication(_ arguments: [String: Any]) throws -> XCUIApplication {
        switch arguments["scope"] as? String ?? "app" {
        case "app": return app
        case "springboard": return XCUIApplication(bundleIdentifier: "com.apple.springboard")
        default: throw DriverError(code: "invalid_scope", message: "Scope must be app or springboard")
        }
    }

    private func selected(_ arguments: [String: Any]) throws -> XCUIElement {
        let target = try scopedApplication(arguments)
        guard let selector = arguments["selector"] as? [String: Any], !selector.isEmpty else {
            throw DriverError(code: "invalid_request", message: "A native element selector is required")
        }
        var query = target.descendants(matching: .any)
        var constrained = false
        if let type = selector["element_type"] as? UInt, let elementType = XCUIElement.ElementType(rawValue: type) {
            query = target.descendants(matching: elementType)
            constrained = true
        }
        if let identifier = selector["identifier"] as? String, !identifier.isEmpty {
            query = query.matching(identifier: identifier)
            constrained = true
        }
        if let label = selector["label"] as? String {
            query = query.matching(NSPredicate(format: "label == %@", label))
            constrained = true
        }
        guard constrained else { throw DriverError(code: "invalid_selector", message: "No supported native selector field") }
        let count = query.count
        guard count > 0 else { throw DriverError(code: "not_found", message: "Native selector matched zero elements") }
        guard count == 1 else { throw DriverError(code: "ambiguous", message: "Native selector matched \(count) elements") }
        let element = query.element(boundBy: 0)
        guard element.exists else { throw DriverError(code: "not_found", message: "Selected element disappeared") }
        return element
    }

    private func observed(_ element: XCUIElement) -> [String: Any] {
        var object = attributes(element)
        object["exists"] = element.exists
        object["hittable"] = element.isHittable
        return object
    }

    private func requireForeground() throws {
        guard app.state == .runningForeground else {
            throw DriverError(code: "not_foreground", message: "The requested application is not in the foreground")
        }
    }

    private func execute(_ operation: String, arguments: [String: Any], id: String) throws -> [String: Any] {
        let target = try scopedApplication(arguments)
        let systemScope = arguments["scope"] as? String == "springboard"
        if systemScope && ["launch", "activate", "terminate", "openurl"].contains(operation) {
            throw DriverError(code: "unsupported", message: "SpringBoard scope supports observation and explicit UI actions only")
        }
        switch operation {
        case "ping": return ["bundle_id": bundleID, "app_state": app.state.rawValue]
        case "launch":
            app.launchArguments = arguments["launch_arguments"] as? [String] ?? []
            app.launchEnvironment = arguments["launch_environment"] as? [String: String] ?? [:]
            app.launch()
            guard app.wait(for: .runningForeground, timeout: 15) else {
                throw DriverError(code: "launch_failed", message: "App did not enter foreground")
            }
            return ["bundle_id": bundleID, "app_state": app.state.rawValue]
        case "activate": app.activate(); return ["app_state": app.state.rawValue]
        case "terminate": app.terminate(); return ["app_state": app.state.rawValue]
        case "snapshot", "capture":
            if !systemScope { try requireForeground() }
            return try capture(id: id, includeScreenshot: operation == "capture", scope: systemScope ? "springboard" : "app")
        case "find":
            if !systemScope { try requireForeground() }
            return observed(try selected(arguments))
        case "tap":
            if !systemScope { try requireForeground() }
            if arguments["selector"] != nil {
                let element = try selected(arguments)
                guard element.isHittable else { throw DriverError(code: "not_hittable", message: "Selected element is not hittable") }
                let before = observed(element)
                element.tap()
                return ["element_before": before, "app_state": app.state.rawValue]
            }
            guard arguments["coordinate_space"] as? String == "screen_points",
                  let x = arguments["x"] as? Double, let y = arguments["y"] as? Double, x.isFinite, y.isFinite else {
                throw DriverError(code: "invalid_request", message: "Coordinate tap requires finite x/y in screen_points")
            }
            let frame = target.frame
            guard frame.contains(CGPoint(x: x, y: y)) else {
                throw DriverError(code: "out_of_bounds", message: "Coordinate lies outside observed application frame")
            }
            target.coordinate(withNormalizedOffset: .zero).withOffset(CGVector(dx: x - frame.minX, dy: y - frame.minY)).tap()
            return ["coordinate_space": "screen_points", "x": x, "y": y, "app_state": app.state.rawValue]
        case "press_home":
            XCUIDevice.shared.press(.home)
            return ["app_state": app.state.rawValue,
                    "springboard_state": XCUIApplication(bundleIdentifier: "com.apple.springboard").state.rawValue]
        case "long_press":
            if !systemScope { try requireForeground() }
            guard let duration = arguments["duration"] as? Double, duration.isFinite, duration >= 0.1, duration <= 30 else {
                throw DriverError(code: "invalid_request", message: "Long press requires finite duration between 0.1 and 30 seconds")
            }
            if arguments["selector"] != nil {
                let element = try selected(arguments)
                guard element.isHittable else { throw DriverError(code: "not_hittable", message: "Selected element is not hittable") }
                let before = observed(element)
                element.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.5)).press(forDuration: duration)
                return ["element_before": before, "duration": duration, "app_state": app.state.rawValue]
            }
            guard arguments["coordinate_space"] as? String == "screen_points",
                  let x = arguments["x"] as? Double, let y = arguments["y"] as? Double, x.isFinite, y.isFinite else {
                throw DriverError(code: "invalid_request", message: "Coordinate long press requires finite x/y in screen_points")
            }
            let frame = target.frame
            guard frame.contains(CGPoint(x: x, y: y)) else {
                throw DriverError(code: "out_of_bounds", message: "Coordinate lies outside observed application frame")
            }
            target.coordinate(withNormalizedOffset: .zero).withOffset(CGVector(dx: x - frame.minX, dy: y - frame.minY)).press(forDuration: duration)
            return ["coordinate_space": "screen_points", "x": x, "y": y, "duration": duration, "app_state": app.state.rawValue]
        case "type_text":
            if !systemScope { try requireForeground() }
            let element = try selected(arguments)
            guard element.isHittable else { throw DriverError(code: "not_hittable", message: "Selected input is not hittable") }
            guard let text = arguments["text"] as? String else { throw DriverError(code: "invalid_request", message: "Missing text") }
            element.tap()
            element.typeText(text)
            return observed(element)
        case "swipe":
            if !systemScope { try requireForeground() }
            let element = arguments["selector"] == nil ? target : try selected(arguments)
            switch arguments["direction"] as? String {
            case "up": element.swipeUp()
            case "down": element.swipeDown()
            case "left": element.swipeLeft()
            case "right": element.swipeRight()
            default: throw DriverError(code: "invalid_request", message: "Direction must be up/down/left/right")
            }
            return ["app_state": app.state.rawValue]
        case "openurl":
            guard let text = arguments["url"] as? String, let url = URL(string: text), url.scheme != nil else {
                throw DriverError(code: "invalid_request", message: "An absolute URL is required")
            }
            if #available(iOS 16.4, *) { app.open(url) }
            else { throw DriverError(code: "unsupported", message: "openurl requires iOS 16.4+") }
            return ["app_state": app.state.rawValue]
        case "stop": return ["stopped": true]
        default: throw DriverError(code: "unsupported", message: "Unsupported operation \(operation)")
        }
    }

    private func cleanValue(_ value: Any?) -> Any {
        guard let value else { return NSNull() }
        if value is String || value is NSNumber || value is NSNull { return value }
        return String(describing: value)
    }

    private func attributes(_ element: any XCUIElementAttributes) -> [String: Any] {
        let frame = element.frame
        return ["identifier": element.identifier, "element_type": element.elementType.rawValue,
                "label": element.label, "title": element.title, "value": cleanValue(element.value),
                "placeholder_value": cleanValue(element.placeholderValue), "enabled": element.isEnabled,
                "selected": element.isSelected, "frame": ["x": frame.minX, "y": frame.minY,
                "width": frame.width, "height": frame.height], "coordinate_space": "screen_points"]
    }

#if HMIGBOT_HAS_XCUI_SNAPSHOT
    private func snapshotNode(_ snapshot: any XCUIElementSnapshot, budget: inout Int) throws -> [String: Any] {
        guard budget > 0 else { throw DriverError(code: "tree_limit", message: "Native hierarchy exceeded 12000 nodes") }
        budget -= 1
        var node = attributes(snapshot)
        node["exists"] = true
        node["hittable"] = NSNull()
        node["hittable_observation"] = "not_available_in_snapshot"
        node["children"] = try snapshot.children.map { try snapshotNode($0, budget: &budget) }
        return node
    }
#endif
    private func queryNode(_ element: XCUIElement, depth: Int, budget: inout Int) throws -> [String: Any] {
        guard depth < 80, budget > 0 else { throw DriverError(code: "tree_limit", message: "Public query hierarchy exceeded its limit") }
        budget -= 1
        var node = observed(element)
        node["children"] = try element.children(matching: .any).allElementsBoundByIndex.map { try queryNode($0, depth: depth + 1, budget: &budget) }
        return node
    }

    private func capture(id: String, includeScreenshot: Bool, scope: String = "app", requestedScope: String? = nil) throws -> [String: Any] {
        let started = Date().timeIntervalSince1970
        let target = scope == "springboard" ? XCUIApplication(bundleIdentifier: "com.apple.springboard") : app!
        let stateBefore = target.state.rawValue
        var budget = 12000
        let tree: [String: Any]
        let method: String
#if HMIGBOT_HAS_XCUI_SNAPSHOT
        tree = try snapshotNode(target.snapshot(), budget: &budget)
        method = "public_snapshot"
#else
        tree = try queryNode(target, depth: 0, budget: &budget)
        method = "public_query_tree"
#endif
        var envelope: [String: Any] = ["schema_version": 1, "platform": "ios", "session": session,
            "request_id": id, "bundle_id": scope == "springboard" ? "com.apple.springboard" : bundleID,
            "aut_bundle_id": bundleID, "scope": scope, "collection_method": method,
            "started_at": started, "app_state_before": stateBefore, "tree": tree,
            "orientation": XCUIDevice.shared.orientation.rawValue]
        envelope["requested_scope"] = requestedScope ?? scope
        envelope["aut_state"] = app.state.rawValue
        envelope["aut_tree_status"] = scope == "app" ? "observed" : (requestedScope == "app" ? "unavailable" : "not_requested")
        if scope == "springboard" && requestedScope == "app" {
            envelope["aut_tree_unavailable_reason"] = "application_not_foreground"
            envelope["reason"] = "application_not_foreground"
        }
        let system = XCUIApplication(bundleIdentifier: "com.apple.springboard")
        envelope["system_overlay"] = ["springboard_exists": system.exists,
                                      "alert_count": system.alerts.count,
                                      "alerts": system.alerts.allElementsBoundByIndex.map { observed($0) }]
        if scope == "springboard" {
            envelope["system_tree"] = tree
            envelope["system_tree_status"] = "observed"
        } else if system.exists {
            do {
                var systemBudget = 12000
#if HMIGBOT_HAS_XCUI_SNAPSHOT
                envelope["system_tree"] = try snapshotNode(system.snapshot(), budget: &systemBudget)
#else
                envelope["system_tree"] = try queryNode(system, depth: 0, budget: &systemBudget)
#endif
                envelope["system_tree_status"] = "observed"
            } catch {
                envelope["system_tree_status"] = "unavailable"
                envelope["system_tree_error"] = String(describing: error)
            }
        } else {
            envelope["system_tree_status"] = "not_observable"
        }
        var result: [String: Any] = [:]
        if includeScreenshot {
            let shot = XCUIScreen.main.screenshot()
            let pngName = "artifacts/\(id).png"
            try shot.pngRepresentation.write(to: root.appendingPathComponent(pngName), options: .atomic)
            let image = shot.image
            guard let cgImage = image.cgImage else { throw DriverError(code: "screenshot_failed", message: "Screenshot has no CGImage") }
            let pixels = ["width": cgImage.width, "height": cgImage.height]
            let points = ["width": image.size.width, "height": image.size.height]
            envelope["screenshot"] = ["file": pngName, "pixel_size": pixels, "point_size": points,
                "image_scale": image.scale, "pixel_per_point_x": CGFloat(cgImage.width) / image.size.width,
                "pixel_per_point_y": CGFloat(cgImage.height) / image.size.height, "origin_screen_points": ["x": 0, "y": 0]]
            result["screenshot"] = pngName
        }
        envelope["app_state_after"] = target.state.rawValue
        envelope["finished_at"] = Date().timeIntervalSince1970
        let jsonName = "artifacts/\(id).native.json"
        try write(envelope, to: root.appendingPathComponent(jsonName))
        result["hierarchy"] = jsonName
        result["collection_method"] = method
        result["app_state_before"] = stateBefore
        result["app_state_after"] = target.state.rawValue
        return result
    }
}
