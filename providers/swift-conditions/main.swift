// SwiftIfConfig selects clauses. Apple Swift answers configuration queries using
// the captured compiler arguments; probes contain no application implementation.
import Foundation
import Darwin
import SwiftSyntax
import SwiftParser
import SwiftParserDiagnostics
import SwiftIfConfig

struct Context: Decodable {
    let swiftc: String
    let arguments: [String]
    let compiler_version: [Int]
    let declared_modules: [String]
}
struct Input: Decodable { let path: String; let source: String; let sha256: String }
struct Request: Decodable { let context: Context; let files: [Input] }
struct Unknown: Error, CustomStringConvertible {
    let description: String
    init(_ message: String) { description = message }
}
final class Configuration: BuildConfiguration {
    let context: Context
    var records: [[String: Any]] = []
    var answers: [String: Bool] = [:]
    var languageVersion = VersionTuple(0)
    let compilerVersion: VersionTuple
    // The private pointer/atomic/endian queries are rejected before evaluation;
    // placeholder properties never supply a claimed target condition result.
    var targetPointerBitWidth: Int { 0 }
    var targetAtomicBitWidths: [Int] { [] }
    var endianness: Endianness { .little }
    init(_ context: Context) throws {
        self.context = context
        compilerVersion = VersionTuple(components: context.compiler_version)
        guard context.compiler_version.count >= 2, context.arguments.filter({ $0 == "-target" }).count == 1,
              context.arguments.filter({ $0 == "-sdk" }).count == 1,
              context.arguments.filter({ $0 == "-swift-version" }).count <= 1 else {
            throw Unknown("Incomplete captured Swift compiler context")
        }
        var major = 0
        for candidate in 1...(context.compiler_version[0] + 1) {
            if try query("swift(>=\(candidate).0)") { major = candidate } else { break }
        }
        guard major > 0, try !query("swift(>=\(major).1024)") else { throw Unknown("Unbounded Swift language version") }
        var lower = 0, upper = 1024
        while lower + 1 < upper {
            let middle = (lower + upper) / 2
            if try query("swift(>=\(major).\(middle))") { lower = middle } else { upper = middle }
        }
        languageVersion = VersionTuple(major, lower)
    }
    func query(_ expression: String) throws -> Bool {
        if let value = answers[expression] { return value }
        let folder = FileManager.default.temporaryDirectory.appendingPathComponent("hmigbot-swift-condition-" + UUID().uuidString)
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: folder) }
        let file = folder.appendingPathComponent("Condition.swift")
        let source = "#if \(expression)\nenum HMIGBOT_CONDITION_TRUE {}\n#else\nenum HMIGBOT_CONDITION_FALSE {}\n#endif\n"
        try source.write(to: file, atomically: true, encoding: .utf8)
        // Xcode's bridging-header PCH invocation does not accept JSON AST
        // formatting. The compiler's text AST preserves the exact enum name
        // and works with the original mixed Swift/Objective-C arguments.
        let argv = ["-dump-ast"] + context.arguments + [file.path]
        let outURL = folder.appendingPathComponent("stdout.ast"), errURL = folder.appendingPathComponent("stderr.log")
        FileManager.default.createFile(atPath: outURL.path, contents: nil)
        FileManager.default.createFile(atPath: errURL.path, contents: nil)
        let out = try FileHandle(forWritingTo: outURL), err = try FileHandle(forWritingTo: errURL)
        defer { try? out.close(); try? err.close() }
        let process = Process(); process.executableURL = URL(fileURLWithPath: context.swiftc)
        process.arguments = argv; process.standardOutput = out; process.standardError = err
        try process.run()
        let deadline = Date().addingTimeInterval(30)
        while process.isRunning && Date() < deadline { Thread.sleep(forTimeInterval: 0.01) }
        if process.isRunning { kill(process.processIdentifier, SIGKILL) }
        process.waitUntilExit()
        let stdout = try Data(contentsOf: outURL), stderr = try Data(contentsOf: errURL)
        // SwiftDriver writes the text AST to stdout for plain Swift and to
        // stderr when a bridging-header PCH participates. Examine both actual
        // compiler streams; success plus one exact marker is required.
        let lines = (String(decoding: stdout, as: UTF8.self) + "\n" +
                     String(decoding: stderr, as: UTF8.self)).split(separator: "\n")
        let names = lines.compactMap { line -> String? in
            guard line.contains("(enum_decl ") else { return nil }
            if line.contains("\"HMIGBOT_CONDITION_TRUE\"") { return "HMIGBOT_CONDITION_TRUE" }
            if line.contains("\"HMIGBOT_CONDITION_FALSE\"") { return "HMIGBOT_CONDITION_FALSE" }
            return nil
        }
        let answer: Bool? = process.terminationStatus == 0 && names.count == 1 ? names[0] == "HMIGBOT_CONDITION_TRUE" : nil
        records.append(["expression": expression, "argv": [context.swiftc] + argv, "ast_format": "text", "input_source": source,
                        "exit_code": process.terminationStatus, "stdout": String(decoding: stdout, as: UTF8.self),
                        "stderr": String(decoding: stderr, as: UTF8.self), "result": answer as Any? ?? NSNull()])
        guard let answer else { throw Unknown("Compiler query failed: \(expression): " + String(decoding: stderr, as: UTF8.self)) }
        answers[expression] = answer; return answer
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
        case .version(let value): suffix = ", _version: \(value)"
        case .underlyingVersion(let value): suffix = ", _underlyingVersion: \(value)"
        @unknown default: throw Unknown("Unsupported canImport version query")
        }
        let value = try query("canImport(\(module)\(suffix))")
        if !value && context.declared_modules.contains(importPath.first?.1 ?? "") {
            throw Unknown("Declared build module is unavailable in captured search paths: " + module)
        }
        return value
    }
}
final class ConditionVisitor: SyntaxVisitor {
    var declarations: [IfConfigDeclSyntax] = []
    override func visit(_ node: IfConfigDeclSyntax) -> SyntaxVisitorContinueKind {
        declarations.append(node); return .visitChildren
    }
}
func analyze(_ input: Input, _ configuration: Configuration) -> [String: Any] {
    func unknown(_ messages: [String]) -> [String: Any] {
        ["path": input.path, "sha256": input.sha256, "status": "unknown", "diagnostics": messages]
    }
    let tree = Parser.parse(source: input.source)
    let syntaxErrors = ParseDiagnosticsGenerator.diagnostics(for: tree)
    if !syntaxErrors.isEmpty { return unknown(syntaxErrors.map { $0.diagMessage.message }) }
    let visitor = ConditionVisitor(viewMode: .sourceAccurate); visitor.walk(tree)
    for declaration in visitor.declarations {
        for clause in declaration.clauses {
            if let condition = clause.condition, condition.tokens(viewMode: .sourceAccurate).contains(where: {
                ["_pointerBitWidth", "_hasAtomicBitWidth", "_endian"].contains($0.text)
            }) { return unknown(["Private pointer/atomic/endian condition needs an additional official context adapter"]) }
        }
    }
    let regions = tree.configuredRegions(in: configuration)
    if !regions.diagnostics.isEmpty { return unknown(regions.diagnostics.map { $0.diagMessage.message }) }
    let original = Array(input.source.utf8); var masked = original
    var spans: [[String: Any]] = []
    func blank(_ start: Int, _ end: Int) {
        if start >= 0 && end >= start && end <= masked.count {
            for index in start..<end where masked[index] != 10 && masked[index] != 13 { masked[index] = 32 }
        }
    }
    do {
        for declaration in visitor.declarations {
            let active = regions.activeClause(for: declaration)
            var evaluate = regions.isActive(declaration) == .active
            for clause in declaration.clauses {
                let selected = clause.id == active?.id
                let start = clause.poundKeyword.positionAfterSkippingLeadingTrivia.utf8Offset
                let end = clause.endPosition.utf8Offset
                let header = (clause.condition?.endPositionBeforeTrailingTrivia ?? clause.poundKeyword.endPositionBeforeTrailingTrivia).utf8Offset
                if evaluate, let expression = clause.condition {
                    let result = IfConfigRegionState.evaluating(expression, in: configuration)
                    if !result.diagnostics.isEmpty { return unknown(result.diagnostics.map { $0.diagMessage.message }) }
                    let actual = try configuration.query(expression.trimmedDescription)
                    if actual != (result.state == .active) { return unknown(["SwiftIfConfig and selected compiler disagree"]) }
                }
                blank(start, selected ? header : end)
                if selected { evaluate = false }
                spans.append(["start_utf8": start, "end_utf8": end, "selected": selected])
                // Short-circuited clauses need no forced compiler query; mask
                // selection still comes from the official configured regions.
            }
            blank(declaration.poundEndif.positionAfterSkippingLeadingTrivia.utf8Offset,
                  declaration.poundEndif.endPositionBeforeTrailingTrivia.utf8Offset)
        }
    } catch { return unknown([String(describing: error)]) }
    return ["path": input.path, "sha256": input.sha256, "status": "resolved", "regions": spans,
            "filtered_source": String(decoding: masked, as: UTF8.self),
            "source_map": "utf8-offset-and-newline-preserving-mask", "diagnostics": []]
}
do {
    let request = try JSONDecoder().decode(Request.self, from: FileHandle.standardInput.readDataToEndOfFile())
    let configuration = try Configuration(request.context)
    let files = request.files.map { analyze($0, configuration) }
    let result: [String: Any] = ["schema_version": 1, "provider": "SwiftIfConfig+AppleSwiftCompiler",
                                "files": files, "compiler_queries": configuration.records,
                                "effective_language_version": "\(configuration.languageVersion)"]
    FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys]))
} catch {
    let result: [String: Any] = ["schema_version": 1, "status": "unknown", "error": String(describing: error)]
    FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys]))
}
