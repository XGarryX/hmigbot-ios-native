import Foundation
import SwiftDiagnostics
import SwiftIfConfig
import SwiftParser
import SwiftParserDiagnostics
import SwiftSyntax

struct InputFile: Codable { let path: String; let source: String }
struct ConditionalRequest: Decodable {
    let schema_version: Int
    let custom_conditions: [String]
    let conditions_complete: Bool
    let files: [InputFile]
    let compiler_context: CompilerContext?
}
struct Region: Encodable {
    let directive: String
    let expression: String
    let selected: Bool
    let line: Int
    let start_utf8: Int
    let end_utf8: Int
}
struct SourceMap: Encodable {
    let kind: String
    let input_utf8_bytes: Int
    let output_utf8_bytes: Int
}
struct FileResult: Encodable {
    let path: String
    let status: String
    let filtered_source: String?
    let rewritten_source: String?
    let source_map: SourceMap?
    let regions: [Region]
    let diagnostics: [String]

    enum CodingKeys: String, CodingKey {
        case path, status, filtered_source, rewritten_source, source_map, regions, diagnostics
    }
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(path, forKey: .path)
        try container.encode(status, forKey: .status)
        if let filtered_source {
            try container.encode(filtered_source, forKey: .filtered_source)
        } else {
            try container.encodeNil(forKey: .filtered_source)
        }
        try container.encodeIfPresent(rewritten_source, forKey: .rewritten_source)
        try container.encodeIfPresent(source_map, forKey: .source_map)
        try container.encode(regions, forKey: .regions)
        try container.encode(diagnostics, forKey: .diagnostics)
    }
}
struct Response: Encodable {
    let stage = "official-swift-if-config"
    let schema_version = 2
    let evidence: String
    let provider_build = "xcode-toolchain"
    let files: [FileResult]
    let compiler_queries: [CompilerProbeRecord]
}

final class IfCollector: SyntaxVisitor {
    var declarations: [IfConfigDeclSyntax] = []
    override func visit(_ node: IfConfigDeclSyntax) -> SyntaxVisitorContinueKind {
        declarations.append(node)
        return .visitChildren
    }
}
final class ConditionCallCollector: SyntaxVisitor {
    var calls: [String] = []
    override func visit(_ node: FunctionCallExprSyntax) -> SyntaxVisitorContinueKind {
        calls.append(node.calledExpression.description.trimmingCharacters(in: .whitespacesAndNewlines))
        return .skipChildren
    }
}

func unknown(_ file: InputFile, _ diagnostics: [String]) -> FileResult {
    FileResult(path: file.path, status: "unknown", filtered_source: nil,
               rewritten_source: nil, source_map: nil, regions: [], diagnostics: diagnostics)
}

func analyze(_ file: InputFile, request: ConditionalRequest, compiler: CompilerConfiguration?) -> FileResult {
    guard request.conditions_complete else {
        return unknown(file, ["Custom condition inputs are incomplete within the declared analysis profile"])
    }
    let tree = Parser.parse(source: file.source)
    let syntaxDiagnostics = ParseDiagnosticsGenerator.diagnostics(for: tree)
    guard syntaxDiagnostics.isEmpty else {
        return unknown(file, syntaxDiagnostics.map { $0.diagMessage.message })
    }
    let collector = IfCollector(viewMode: .sourceAccurate)
    collector.walk(tree)
    var unsupported: [String] = []
    for declaration in collector.declarations {
        for clause in declaration.clauses {
            guard let condition = clause.condition else { continue }
            let calls = ConditionCallCollector(viewMode: .sourceAccurate)
            calls.walk(condition)
            unsupported.append(contentsOf: calls.calls.filter { compiler == nil || ["_pointerBitWidth", "_hasAtomicBitWidth", "_endian"].contains($0) }.map {
                "Condition query '\($0)' requires context outside this custom-boolean-only provider profile"
            })
            if compiler == nil && condition.tokens(viewMode: .sourceAccurate).contains(where: { $0.text.hasPrefix("$") }) {
                unsupported.append("Compiler feature queries are outside the supplied custom condition set")
            }
        }
    }
    guard unsupported.isEmpty else { return unknown(file, unsupported) }

    // These placeholder versions are never queried: all function-shaped
    // conditions, including compiler()/swift(), are explicitly rejected above.
    // Neither the host OS nor its compiler/SDK availability is used as an iOS fact.
    let configuration: any BuildConfiguration = compiler ?? StaticBuildConfiguration(
        customConditions: Set(request.custom_conditions),
        languageVersion: VersionTuple(5), compilerVersion: VersionTuple(0)
    )
    let configured = tree.configuredRegions(in: configuration)
    guard configured.diagnostics.isEmpty else {
        // The library may consider an errored condition false. Never accept that
        // fallback as a proven inactive branch in the migration provider profile.
        return unknown(file, configured.diagnostics.map { $0.diagMessage.message })
    }

    // Compare each evaluated complete expression against the compiler as well.
    // Selection itself remains SwiftIfConfig's job on the original syntax tree.
    if let compiler {
        do {
            for declaration in collector.declarations where configured.isActive(declaration) == .active {
                let selected = configured.activeClause(for: declaration)
                for clause in declaration.clauses {
                    if let condition = clause.condition {
                        let evaluated = IfConfigRegionState.evaluating(condition, in: compiler)
                        guard evaluated.diagnostics.isEmpty else { return unknown(file, evaluated.diagnostics.map { $0.diagMessage.message }) }
                        let actual = try compiler.query(condition.trimmedDescription)
                        guard actual == (evaluated.state == .active) else {
                            return unknown(file, ["SwiftIfConfig and the compiler disagree on " + condition.trimmedDescription])
                        }
                    }
                    if clause.id == selected?.id { break }
                }
            }
        } catch { return unknown(file, [String(describing: error)]) }
    }

    let converter = SourceLocationConverter(fileName: file.path, tree: tree)
    let originalBytes = Array(file.source.utf8)
    var masked = originalBytes
    var invalidSpan = false
    func blank(_ start: Int, _ end: Int) {
        guard start >= 0, end >= start, end <= masked.count else {
            invalidSpan = true
            return
        }
        for index in start..<end where masked[index] != 10 && masked[index] != 13 {
            masked[index] = 32
        }
    }
    var regionResults: [Region] = []
    for declaration in collector.declarations {
        let active = configured.activeClause(for: declaration)
        for clause in declaration.clauses {
            let selected = active?.id == clause.id
            let start = clause.poundKeyword.positionAfterSkippingLeadingTrivia.utf8Offset
            let headerEnd = (clause.condition?.endPositionBeforeTrailingTrivia
                             ?? clause.poundKeyword.endPositionBeforeTrailingTrivia).utf8Offset
            let end = clause.endPosition.utf8Offset
            blank(start, selected ? headerEnd : end)
            regionResults.append(Region(
                directive: clause.poundKeyword.text,
                expression: clause.condition?.description.trimmingCharacters(in: .whitespacesAndNewlines) ?? "",
                selected: selected, line: converter.location(for: clause.poundKeyword.positionAfterSkippingLeadingTrivia).line,
                start_utf8: start, end_utf8: end
            ))
        }
        blank(declaration.poundEndif.positionAfterSkippingLeadingTrivia.utf8Offset,
              declaration.poundEndif.endPositionBeforeTrailingTrivia.utf8Offset)
    }
    guard !invalidSpan else { return unknown(file, ["Official syntax source span is outside original UTF-8 input"]) }
    let filtered = String(decoding: masked, as: UTF8.self)
    let rewritten = configured.removingInactive(from: tree).description
    return FileResult(path: file.path, status: "resolved", filtered_source: filtered,
                      rewritten_source: rewritten,
                      source_map: SourceMap(kind: "utf8-offset-and-newline-preserving-mask",
                                            input_utf8_bytes: originalBytes.count,
                                            output_utf8_bytes: masked.count),
                      regions: regionResults, diagnostics: [])
}

func runConditionalSource() throws {
    let request = try JSONDecoder().decode(ConditionalRequest.self, from: FileHandle.standardInput.readDataToEndOfFile())
    guard request.schema_version == 1 || request.schema_version == 2 else { throw CocoaError(.coderReadCorrupt) }
    guard request.schema_version != 2 || request.compiler_context != nil else { throw CocoaError(.coderReadCorrupt) }
    let compiler = try request.compiler_context.map { try CompilerConfiguration($0) }
    let files = request.files.map { analyze($0, request: request, compiler: compiler) }
    let response = Response(evidence: compiler == nil ? "declared-custom-boolean-conditions-only" : "compiler-backed-conditions",
                            files: files, compiler_queries: compiler?.records ?? [])
    FileHandle.standardOutput.write(try JSONEncoder().encode(response))
}
