// Conditions are answered by the selected Apple compiler for the captured iOS target.
// The generated probes contain no application code and are never executed.
import Foundation
import Darwin
import SwiftIfConfig
import SwiftSyntax

struct CompilerContext: Decodable {
    let swiftc: String
    let arguments: [String]
    let compiler_version: [Int]
    let pointer_bit_width: Int
    let declared_modules: [String]
}

struct CompilerProbeRecord: Encodable {
    let expression: String
    let argv: [String]
    let input_source: String
    let exit_code: Int32
    let stdout: String
    let stderr: String
    let result: Bool?
}

enum CompilerQueryError: Error, CustomStringConvertible {
    case unknown(String)
    var description: String { switch self { case .unknown(let message): return message } }
}

final class CompilerConfiguration: BuildConfiguration {
    let context: CompilerContext
    var records: [CompilerProbeRecord] = []
    var cache: [String: Bool] = [:]
    var languageVersion = VersionTuple(0)
    let compilerVersion: VersionTuple
    var targetPointerBitWidth: Int { context.pointer_bit_width }
    // These properties are never used: their query forms are rejected below.
    var targetAtomicBitWidths: [Int] { [] }
    var endianness: Endianness { .little }

    init(_ context: CompilerContext) throws {
        self.context = context
        self.compilerVersion = VersionTuple(components: context.compiler_version)
        guard context.compiler_version.count >= 2,
              context.arguments.filter({ $0 == "-target" }).count == 1,
              context.arguments.filter({ $0 == "-sdk" }).count == 1,
              context.arguments.filter({ $0 == "-swift-version" }).count == 1 else {
            throw CompilerQueryError.unknown("Incomplete captured compiler context")
        }
        // -swift-version 5 can mean effective Swift 5.10. Ask the compiler;
        // neither the setting's spelling nor the host OS supplies that answer.
        var major = 0
        for candidate in 1...(context.compiler_version[0] + 1) {
            if try query("swift(>=\(candidate).0)") { major = candidate } else { break }
        }
        guard major > 0, try !query("swift(>=\(major).1024)") else {
            throw CompilerQueryError.unknown("Cannot bound the compiler's effective language version")
        }
        var lower = 0, upper = 1024
        while lower + 1 < upper {
            let candidate = (lower + upper) / 2
            if try query("swift(>=\(major).\(candidate))") { lower = candidate } else { upper = candidate }
        }
        languageVersion = VersionTuple(major, lower)
    }

    func query(_ expression: String) throws -> Bool {
        if let value = cache[expression] { return value }
        let folder = FileManager.default.temporaryDirectory.appendingPathComponent("hmigbot-compiler-" + UUID().uuidString)
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: folder) }
        let file = folder.appendingPathComponent("Condition.swift")
        let source = "#if \(expression)\nenum HMIGBOT_CONDITION_TRUE {}\n#else\nenum HMIGBOT_CONDITION_FALSE {}\n#endif\n"
        try source.write(to: file, atomically: true, encoding: .utf8)
        let process = Process()
        process.executableURL = URL(fileURLWithPath: context.swiftc)
        process.arguments = ["-frontend", "-dump-ast", "-dump-ast-format", "json"] + context.arguments + [file.path]
        let outputURL = folder.appendingPathComponent("stdout.json")
        let errorURL = folder.appendingPathComponent("stderr.log")
        FileManager.default.createFile(atPath: outputURL.path, contents: nil)
        FileManager.default.createFile(atPath: errorURL.path, contents: nil)
        let output = try FileHandle(forWritingTo: outputURL), error = try FileHandle(forWritingTo: errorURL)
        defer { try? output.close(); try? error.close() }
        process.standardOutput = output; process.standardError = error
        try process.run()
        let deadline = Date().addingTimeInterval(30)
        while process.isRunning && Date() < deadline { Thread.sleep(forTimeInterval: 0.02) }
        if process.isRunning { kill(process.processIdentifier, SIGKILL) }
        process.waitUntilExit()
        let stdout = try Data(contentsOf: outputURL), stderr = try Data(contentsOf: errorURL)
        let json = try? JSONSerialization.jsonObject(with: stdout) as? [String: Any]
        let items = json?["items"] as? [[String: Any]] ?? []
        let names = items.compactMap { item -> String? in
            guard item["_kind"] as? String == "enum_decl",
                  let name = item["name"] as? [String: Any],
                  let base = name["base_name"] as? [String: Any] else { return nil }
            return base["name"] as? String
        }
        let matching = names.filter { $0 == "HMIGBOT_CONDITION_TRUE" || $0 == "HMIGBOT_CONDITION_FALSE" }
        let result: Bool? = process.terminationStatus == 0 && matching.count == 1
            ? matching[0] == "HMIGBOT_CONDITION_TRUE" : nil
        records.append(CompilerProbeRecord(expression: expression,
            argv: [context.swiftc] + (process.arguments ?? []), input_source: source,
            exit_code: process.terminationStatus, stdout: String(decoding: stdout, as: UTF8.self),
            stderr: String(decoding: stderr, as: UTF8.self), result: result))
        guard let result else {
            throw CompilerQueryError.unknown("Compiler could not resolve '\(expression)': " + String(decoding: stderr, as: UTF8.self))
        }
        cache[expression] = result
        return result
    }

    func isCustomConditionSet(name: String) throws -> Bool { try query(name) }
    func hasFeature(name: String) throws -> Bool { try query("hasFeature(\(name))") }
    func hasAttribute(name: String) throws -> Bool { try query("hasAttribute(\(name))") }
    func isActiveTargetOS(name: String) throws -> Bool { try query("os(\(name))") }
    func isActiveTargetArchitecture(name: String) throws -> Bool { try query("arch(\(name))") }
    func isActiveTargetEnvironment(name: String) throws -> Bool { try query("targetEnvironment(\(name))") }
    func isActiveTargetRuntime(name: String) throws -> Bool { try query("_runtime(\(name))") }
    func isActiveTargetPointerAuthentication(name: String) throws -> Bool { try query("_ptrauth(\(name))") }
    func isActiveTargetObjectFormat(name: String) throws -> Bool { try query("_objectFileFormat(\(name))") }
    func canImport(importPath: [(TokenSyntax, String)], version: CanImportVersion) throws -> Bool {
        let module = importPath.map { $0.1 }.joined(separator: ".")
        let suffix: String
        switch version {
        case .unversioned: suffix = ""
        case .version(let version): suffix = ", _version: \(version)"
        case .underlyingVersion(let version): suffix = ", _underlyingVersion: \(version)"
        @unknown default: throw CompilerQueryError.unknown("Unknown canImport version query")
        }
        let value = try query("canImport(\(module)\(suffix))")
        if !value && context.declared_modules.contains(importPath.first?.1 ?? "") {
            throw CompilerQueryError.unknown("Declared project module '\(module)' is not available in the captured compiler search paths")
        }
        return value
    }
}
