// Parses input data only. It never imports, builds or executes the supplied app.
import Foundation
import SwiftSyntax
import SwiftParser
import SwiftParserDiagnostics

struct SourceInput: Decodable { let path: String; let sha256: String; let source: String }
struct SyntaxRequest: Decodable { let files: [SourceInput] }

final class Collector: SyntaxVisitor {
    let converter: SourceLocationConverter
    var nodes: [[String: Any]] = []
    var enums: [String] = []
    init(_ tree: SourceFileSyntax, _ path: String) {
        converter = SourceLocationConverter(fileName: path, tree: tree)
        super.init(viewMode: .sourceAccurate)
    }
    func add(_ kind: String, _ node: some SyntaxProtocol, _ value: [String: Any]) {
        let start = node.positionAfterSkippingLeadingTrivia
        let end = node.endPositionBeforeTrailingTrivia
        let location = converter.location(for: start)
        nodes.append(["kind": kind, "start_utf8": start.utf8Offset, "end_utf8": end.utf8Offset,
                      "line": location.line, "column": location.column, "value": value])
    }
    override func visit(_ node: ImportDeclSyntax) -> SyntaxVisitorContinueKind {
        add("import", node, ["module": node.path.trimmedDescription]); return .visitChildren
    }
    override func visit(_ node: StructDeclSyntax) -> SyntaxVisitorContinueKind {
        add("type", node, ["kind": "struct", "name": node.name.text,
            "attributes": node.attributes.trimmedDescription,
            "inherits": node.inheritanceClause?.inheritedTypes.map { $0.type.trimmedDescription } ?? []]); return .visitChildren
    }
    override func visit(_ node: ClassDeclSyntax) -> SyntaxVisitorContinueKind {
        add("type", node, ["kind": "class", "name": node.name.text,
            "attributes": node.attributes.trimmedDescription,
            "inherits": node.inheritanceClause?.inheritedTypes.map { $0.type.trimmedDescription } ?? []]); return .visitChildren
    }
    override func visit(_ node: EnumDeclSyntax) -> SyntaxVisitorContinueKind {
        add("type", node, ["kind": "enum", "name": node.name.text,
            "inherits": node.inheritanceClause?.inheritedTypes.map { $0.type.trimmedDescription } ?? []])
        enums.append(node.name.text)
        return .visitChildren
    }
    override func visitPost(_ node: EnumDeclSyntax) { enums.removeLast() }
    override func visit(_ node: EnumCaseDeclSyntax) -> SyntaxVisitorContinueKind {
        guard let owner = enums.last else { return .visitChildren }
        for element in node.elements {
            let start = node.caseKeyword.positionAfterSkippingLeadingTrivia
            let location = converter.location(for: start)
            nodes.append(["kind": "enum_case", "start_utf8": start.utf8Offset,
                "end_utf8": element.endPositionBeforeTrailingTrivia.utf8Offset,
                "line": location.line, "column": location.column,
                "value": ["enum_name": owner, "qualified_enum": enums.joined(separator: "."),
                    "name": element.name.text,
                    "associated_values": element.parameterClause?.trimmedDescription ?? "",
                    "raw_value": element.rawValue?.value.trimmedDescription ?? ""]])
        }
        return .visitChildren
    }
    override func visit(_ node: ProtocolDeclSyntax) -> SyntaxVisitorContinueKind {
        add("type", node, ["kind": "protocol", "name": node.name.text,
            "inherits": node.inheritanceClause?.inheritedTypes.map { $0.type.trimmedDescription } ?? []]); return .visitChildren
    }
    override func visit(_ node: ActorDeclSyntax) -> SyntaxVisitorContinueKind {
        add("actor", node, ["name": node.name.text,
            "inherits": node.inheritanceClause?.inheritedTypes.map { $0.type.trimmedDescription } ?? []])
        return .visitChildren
    }
    override func visit(_ node: ExtensionDeclSyntax) -> SyntaxVisitorContinueKind {
        add("extension", node, ["type": node.extendedType.trimmedDescription]); return .visitChildren
    }
    override func visit(_ node: FunctionDeclSyntax) -> SyntaxVisitorContinueKind {
        add("function", node, ["name": node.name.text, "signature": node.signature.trimmedDescription]); return .visitChildren
    }
    override func visit(_ node: VariableDeclSyntax) -> SyntaxVisitorContinueKind {
        let bindings = node.bindings.map { binding -> [String: Any] in
            ["pattern": binding.pattern.trimmedDescription,
             "type": binding.typeAnnotation?.type.trimmedDescription ?? "",
             "initializer": binding.initializer?.value.trimmedDescription ?? ""]
        }
        add("variable", node, ["specifier": node.bindingSpecifier.text, "bindings": bindings,
                              "attributes": node.attributes.trimmedDescription]); return .visitChildren
    }
    override func visit(_ node: FunctionCallExprSyntax) -> SyntaxVisitorContinueKind {
        let arguments = node.arguments.map { ["label": $0.label?.text ?? "", "expression": $0.expression.trimmedDescription] }
        add("call", node, ["callee": node.calledExpression.trimmedDescription, "arguments": arguments,
                           "has_trailing_closure": node.trailingClosure != nil]); return .visitChildren
    }
    override func visit(_ node: AttributeSyntax) -> SyntaxVisitorContinueKind {
        add("attribute", node, ["name": node.attributeName.trimmedDescription]); return .visitChildren
    }
    override func visit(_ node: IfConfigDeclSyntax) -> SyntaxVisitorContinueKind {
        add("conditional_compilation", node, ["conditions": node.clauses.map { $0.condition?.trimmedDescription ?? "else" }]); return .visitChildren
    }
}

final class LiteralCollector: SyntaxVisitor {
    var literals: [[String: Any]] = []
    func add(_ node: some SyntaxProtocol, _ kind: String, hashes: Int = 0, quotes: Int = 0) {
        literals.append(["kind": kind, "start_utf8": node.positionAfterSkippingLeadingTrivia.utf8Offset,
                         "end_utf8": node.endPositionBeforeTrailingTrivia.utf8Offset,
                         "hash_count": hashes, "quote_count": quotes])
    }
    override func visit(_ node: StringLiteralExprSyntax) -> SyntaxVisitorContinueKind {
        add(node, "string", hashes: node.openingPounds?.text.count ?? 0, quotes: node.openingQuote.text.count)
        literals[literals.count - 1]["literal_value"] = node.representedLiteralValue ?? NSNull()
        literals[literals.count - 1]["literal_is_static"] = node.representedLiteralValue != nil
        return .skipChildren
    }
    override func visit(_ node: RegexLiteralExprSyntax) -> SyntaxVisitorContinueKind {
        add(node, "regex")
        return .skipChildren
    }
}

func tokens(_ tree: SourceFileSyntax, _ source: String, _ converter: SourceLocationConverter) throws -> [[String: Any]] {
    let literals = LiteralCollector(viewMode: .sourceAccurate)
    literals.walk(tree)
    let ranges = literals.literals.sorted { ($0["start_utf8"] as! Int) < ($1["start_utf8"] as! Int) }
    var result: [[String: Any]] = []
    var literalIndex = 0
    var skippedUntil = -1
    let bytes = Array(source.utf8)
    for token in tree.tokens(viewMode: .sourceAccurate) {
        let start = token.positionAfterSkippingLeadingTrivia.utf8Offset
        let end = token.endPositionBeforeTrailingTrivia.utf8Offset
        if start < skippedUntil || end <= start { continue }
        let location = converter.location(for: token.positionAfterSkippingLeadingTrivia)
        if literalIndex < ranges.count, ranges[literalIndex]["start_utf8"] as! Int == start {
            var literal = ranges[literalIndex]
            let last = literal["end_utf8"] as! Int
            literal["value"] = String(decoding: bytes[start..<last], as: UTF8.self)
            literal["line"] = location.line
            literal["end_line"] = converter.location(for: AbsolutePosition(utf8Offset: last)).line
            result.append(literal)
            skippedUntil = last
            literalIndex += 1
        } else {
            let kind: String
            switch token.tokenKind {
            case .identifier(_), .keyword(_): kind = "identifier"
            default: kind = "symbol"
            }
            var item: [String: Any] = ["kind": kind, "value": token.text, "start_utf8": start, "end_utf8": end,
                                      "line": location.line, "end_line": location.line]
            switch token.tokenKind {
            case .integerLiteral(_): item["number_literal"] = "integer"
            case .floatLiteral(_): item["number_literal"] = "float"
            default: break
            }
            result.append(item)
        }
    }
    guard literalIndex == ranges.count else {
        throw NSError(domain: "HMigBotSwiftSyntax", code: 2,
                      userInfo: [NSLocalizedDescriptionKey: "Literal ranges did not align with official tokens"])
    }
    return result
}

do {
    if CommandLine.arguments.contains("--conditional-source") {
        try runConditionalSource()
        exit(0)
    }
    let request = try JSONDecoder().decode(SyntaxRequest.self, from: FileHandle.standardInput.readDataToEndOfFile())
    var files: [[String: Any]] = []
    for file in request.files {
        let tree = Parser.parse(source: file.source)
        let collector = Collector(tree, file.path)
        collector.walk(tree)
        VisibilityCollector(collector).walk(tree)
        let diagnostics = ParseDiagnosticsGenerator.diagnostics(for: tree).map {
            ["message": $0.message, "offset_utf8": $0.position.utf8Offset] as [String: Any]
        }
        files.append(["path": file.path, "sha256": file.sha256, "nodes": collector.nodes,
                      "tokens": try tokens(tree, file.source, collector.converter),
                      "parse_has_error": tree.hasError, "diagnostics": diagnostics])
    }
    let output: [String: Any] = ["protocol_version": 1, "schema_version": 2,
                               "provider": "SwiftSyntax", "semantic_resolution": false, "files": files]
    let data = try JSONSerialization.data(withJSONObject: output, options: [.sortedKeys])
    FileHandle.standardOutput.write(data)
} catch {
    FileHandle.standardError.write(Data("SwiftSyntax provider error: \(error)\n".utf8))
    exit(2)
}
