// Parses input data only. It never imports, builds or executes the supplied app.
import Foundation
import SwiftSyntax
import SwiftParser
import SwiftParserDiagnostics

struct SourceInput: Decodable { let path: String; let sha256: String; let source: String }
struct Request: Decodable { let files: [SourceInput] }

final class Collector: SyntaxVisitor {
    let converter: SourceLocationConverter
    var nodes: [[String: Any]] = []
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
    func fileLevel(_ node: some SyntaxProtocol) -> Bool {
        var parent = node.parent
        while let ancestor = parent {
            if ancestor.is(StructDeclSyntax.self) || ancestor.is(ClassDeclSyntax.self)
                || ancestor.is(EnumDeclSyntax.self) || ancestor.is(ActorDeclSyntax.self)
                || ancestor.is(ExtensionDeclSyntax.self) || ancestor.is(ProtocolDeclSyntax.self)
                || ancestor.is(CodeBlockSyntax.self) || ancestor.is(ClosureExprSyntax.self) { return false }
            parent = ancestor.parent
        }
        return true
    }
    override func visit(_ node: ImportDeclSyntax) -> SyntaxVisitorContinueKind {
        add("import", node, ["module": node.path.trimmedDescription]); return .visitChildren
    }
    override func visit(_ node: StructDeclSyntax) -> SyntaxVisitorContinueKind {
        add("type", node, ["kind": "struct", "name": node.name.text,
            "inherits": node.inheritanceClause?.inheritedTypes.map { $0.type.trimmedDescription } ?? [],
            "top_level": fileLevel(node)]); return .visitChildren
    }
    override func visit(_ node: ClassDeclSyntax) -> SyntaxVisitorContinueKind {
        add("type", node, ["kind": "class", "name": node.name.text,
            "inherits": node.inheritanceClause?.inheritedTypes.map { $0.type.trimmedDescription } ?? [],
            "top_level": fileLevel(node)]); return .visitChildren
    }
    override func visit(_ node: EnumDeclSyntax) -> SyntaxVisitorContinueKind {
        add("type", node, ["kind": "enum", "name": node.name.text, "top_level": fileLevel(node),
            "inherits": node.inheritanceClause?.inheritedTypes.map { $0.type.trimmedDescription } ?? []]); return .visitChildren
    }
    override func visit(_ node: ActorDeclSyntax) -> SyntaxVisitorContinueKind {
        add("type", node, ["kind": "actor", "name": node.name.text, "top_level": fileLevel(node),
            "inherits": node.inheritanceClause?.inheritedTypes.map { $0.type.trimmedDescription } ?? []]); return .visitChildren
    }
    override func visit(_ node: ProtocolDeclSyntax) -> SyntaxVisitorContinueKind {
        add("type", node, ["kind": "protocol", "name": node.name.text]); return .visitChildren
    }
    override func visit(_ node: ExtensionDeclSyntax) -> SyntaxVisitorContinueKind {
        add("extension", node, ["type": node.extendedType.trimmedDescription, "top_level": fileLevel(node)]); return .visitChildren
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

// SwiftSyntax owns lexical boundaries too. Treat complete strings/regexes as
// opaque expressions so their contents cannot activate migration signal rules.
func lexicalItems(_ root: Syntax, converter: SourceLocationConverter) -> [[String: Any]] {
    var result: [[String: Any]] = []
    func collect(_ syntax: Syntax) {
        let string = syntax.as(StringLiteralExprSyntax.self)
        let regex = syntax.is(RegexLiteralExprSyntax.self)
        let integer = syntax.as(IntegerLiteralExprSyntax.self)
        let floating = syntax.as(FloatLiteralExprSyntax.self)
        if string != nil || regex || integer != nil || floating != nil || syntax.is(TokenSyntax.self) {
            if let token = syntax.as(TokenSyntax.self),
               token.presence == .missing || token.tokenKind == .endOfFile { return }
            let start = syntax.positionAfterSkippingLeadingTrivia
            let end = syntax.endPositionBeforeTrailingTrivia
            let location = converter.location(for: start)
            var item: [String: Any] = ["text": syntax.trimmedDescription,
                "start_utf8": start.utf8Offset, "end_utf8": end.utf8Offset,
                "line": location.line, "kind": string != nil ? "string" : regex ? "regex" :
                    integer != nil || floating != nil ? "number" : "token"]
            if let token = syntax.as(TokenSyntax.self) {
                switch token.tokenKind {
                case .identifier, .keyword: item["migration_kind"] = "identifier"
                default: item["migration_kind"] = "symbol"
                }
            }
            if let string {
                item["hash_count"] = string.openingPounds?.text.count ?? 0
                item["quote_count"] = string.openingQuote.text.count
                item["decoded_value"] = string.representedLiteralValue ?? NSNull()
            }
            if let integer { item["decoded_number"] = integer.representedLiteralValue ?? NSNull() }
            if let floating {
                let value = floating.representedLiteralValue
                item["decoded_number"] = value?.isFinite == true ? value! : NSNull()
            }
            result.append(item)
        } else {
            for child in syntax.children(viewMode: .sourceAccurate) { collect(child) }
        }
    }
    collect(root)
    return result
}

// Tool-owned SwiftUI -> ArkUI rule. SwiftParser owns all Swift parsing; this
// mapping deliberately refuses every AST shape that has no target rule.
struct LoweringFailure: Error, CustomStringConvertible {
    let description: String
    init(_ message: String) { description = message }
}
final class ArkUIRule {
    var states: [String: Int] = [:]
    let converter: SourceLocationConverter
    init(_ converter: SourceLocationConverter) { self.converter = converter }
    func require(_ ok: Bool, _ message: String) throws {
        if !ok { throw LoweringFailure(message) }
    }
    func identifier(_ name: String) throws -> String {
        let reserved: Set<String> = ["build", "constructor", "aboutToAppear", "aboutToDisappear", "Index",
            "Text", "Button", "VStack", "HStack", "ZStack", "Spacer", "Divider", "class", "struct",
            "interface", "function", "private", "public", "this", "var", "let"]
        try require(!reserved.contains(name) && name.range(of: "^[A-Za-z_][A-Za-z_0-9]*$", options: .regularExpression) != nil,
                    "identifier collides with target component lifecycle or requires target naming mapping")
        return name
    }
    func number(_ expression: ExprSyntax, integer: Bool = false) throws -> Double {
        var expression = expression
        var sign = 1.0
        if let prefix = expression.as(PrefixOperatorExprSyntax.self) {
            try require(prefix.operator.text == "-", "only negative numeric prefix is mapped")
            sign = -1; expression = prefix.expression
        }
        let value: Double?
        if let literal = expression.as(IntegerLiteralExprSyntax.self), let represented = literal.representedLiteralValue {
            value = Double(represented)
        } else if !integer, let literal = expression.as(FloatLiteralExprSyntax.self) {
            value = literal.representedLiteralValue
        } else { value = nil }
        guard let value, value.isFinite, abs(value) <= 9_007_199_254_740_991 else {
            throw LoweringFailure("expected numeric literal within exact ArkTS integer range")
        }
        return sign * value
    }
    func text(_ expression: ExprSyntax, interpolate: Bool = false) throws -> [[String: String]] {
        guard let literal = expression.as(StringLiteralExprSyntax.self) else {
            throw LoweringFailure("only string literals are mapped")
        }
        try require(literal.openingPounds == nil, "extended-delimiter strings require an explicit target localization rule")
        try require(literal.openingQuote.text == "\"", "only single-line string literals are supported")
        if let value = literal.representedLiteralValue { return [["literal": value]] }
        var result: [[String: String]] = []
        for segment in literal.segments {
            if let string = segment.as(StringSegmentSyntax.self) {
                let isolated = literal.with(\.segments, StringLiteralSegmentListSyntax([.stringSegment(string)]))
                guard let decoded = isolated.representedLiteralValue else { throw LoweringFailure("unsupported Swift string escape") }
                if let previous = result.last?["literal"] {
                    result[result.count - 1] = ["literal": previous + decoded]
                } else { result.append(["literal": decoded]) }
            } else if let interpolation = segment.as(ExpressionSegmentSyntax.self) {
                try require(interpolate && interpolation.expressions.count == 1, "only declared integer-state interpolation is supported")
                guard let argument = interpolation.expressions.first, argument.label == nil,
                      let reference = argument.expression.as(DeclReferenceExprSyntax.self),
                      states[reference.baseName.text] != nil, reference.argumentNames == nil else {
                    throw LoweringFailure("only declared integer-state interpolation is supported")
                }
                result.append(["state": reference.baseName.text])
            } else { throw LoweringFailure("unmapped string segment") }
        }
        if result.last?["state"] != nil { result.append(["literal": ""]) }
        return result
    }
    func expressions(_ block: CodeBlockItemListSyntax) throws -> [ExprSyntax] {
        try block.map { item in
            guard item.semicolon == nil, let expression = item.item.as(ExprSyntax.self) else {
                throw LoweringFailure("statements/declarations require a behavioral lowering rule")
            }
            return expression
        }
    }
    func closure(_ value: ClosureExprSyntax?) throws -> [ExprSyntax] {
        guard let value, value.signature == nil else { throw LoweringFailure("expected a parameter-free view/action closure") }
        return try expressions(value.statements)
    }
    func node(_ expression: ExprSyntax) throws -> [String: Any] {
        guard let call = expression.as(FunctionCallExprSyntax.self), call.additionalTrailingClosures.isEmpty else {
            throw LoweringFailure("unsupported view expression")
        }
        let arguments = Array(call.arguments)
        if let member = call.calledExpression.as(MemberAccessExprSyntax.self), let base = member.base {
            var result = try node(base)
            let modifier = member.declName.baseName.text
            try require(call.trailingClosure == nil, "modifier closure has no target rule")
            var modifiers = result["modifiers"] as! [[String: Any]]
            if modifier == "padding" {
                try require(arguments.count == 1 && arguments[0].label == nil, "padding accepts one numeric literal")
                let value = try number(arguments[0].expression)
                try require(value >= 0, "negative padding needs a layout rule")
                modifiers.append(["name": "padding", "value": value])
            } else if modifier == "frame" {
                try require(!arguments.isEmpty, "frame requires explicit width/height")
                for argument in arguments {
                    let axis = argument.label?.text ?? ""
                    try require(["width", "height"].contains(axis), "frame accepts width/height literals only")
                    let value = try number(argument.expression)
                    try require(value >= 0, "negative dimensions are not supported")
                    modifiers.append(["name": axis, "value": value])
                }
            } else { throw LoweringFailure("unsupported modifier \(modifier)") }
            let names = modifiers.map { $0["name"] as! String }
            try require(Set(names).count == names.count, "repeated layout modifiers need composition-aware lowering")
            result["modifiers"] = modifiers; return result
        }
        guard let reference = call.calledExpression.as(DeclReferenceExprSyntax.self), reference.argumentNames == nil else {
            throw LoweringFailure("unsupported view callee")
        }
        let kind = reference.baseName.text
        var result: [String: Any] = ["kind": kind, "line": converter.location(for: call.positionAfterSkippingLeadingTrivia).line,
                                    "modifiers": [[String: Any]](), "children": [[String: Any]]()]
        if ["VStack", "HStack", "ZStack"].contains(kind) {
            try require(arguments.isEmpty || kind != "ZStack" && arguments.count == 1 && arguments[0].label?.text == "spacing",
                        "stack arguments require a layout rule")
            if let argument = arguments.first { result["spacing"] = try number(argument.expression) }
            result["children"] = try closure(call.trailingClosure).map { try node($0) }
        } else if kind == "Text" || kind == "Image" || kind == "Button" {
            try require(arguments.count == 1, "only a single literal title/asset is mapped")
            let argument = arguments[0]
            try require(argument.label == nil || kind == "Text" && argument.label?.text == "verbatim", "unmapped argument label")
            let pieces = try text(argument.expression, interpolate: kind == "Text")
            if kind == "Image" { result["asset_name"] = pieces.compactMap { $0["literal"] }.joined() }
            else { result["text"] = pieces }
            if argument.label?.text == "verbatim" { result["verbatim"] = true }
            if kind == "Button" {
                let actions = try closure(call.trailingClosure)
                guard actions.count == 1, let sequence = actions[0].as(SequenceExprSyntax.self) else {
                    throw LoweringFailure("button requires one integer-state assignment")
                }
                let elements = Array(sequence.elements)
                guard elements.count == 3, let state = elements[0].as(DeclReferenceExprSyntax.self), states[state.baseName.text] != nil else {
                    throw LoweringFailure("button can only modify a declared integer state")
                }
                let operation = elements[1].trimmedDescription
                try require(["+=", "-=", "="].contains(operation), "only integer assignment/add/subtract actions are supported")
                result["action"] = ["state": state.baseName.text, "operator": operation, "value": Int(try number(elements[2], integer: true))]
            } else { try require(call.trailingClosure == nil, "unexpected title/asset closure") }
        } else if kind == "Spacer" || kind == "Divider" {
            try require(arguments.isEmpty && call.trailingClosure == nil, "unexpected spacer/divider arguments")
        } else { throw LoweringFailure("unsupported view \(kind)") }
        return result
    }
    func lower(_ tree: SourceFileSyntax) throws -> [String: Any] {
        try require(!tree.hasError, "SwiftParser rejected source syntax")
        let items = Array(tree.statements)
        let declarations = items.compactMap { $0.item.as(StructDeclSyntax.self) }
        try require(declarations.count == 1 && items.allSatisfy { item in
            if item.item.is(StructDeclSyntax.self) { return true }
            guard let imported = item.item.as(ImportDeclSyntax.self) else { return false }
            return imported.path.trimmedDescription == "SwiftUI" && imported.attributes.isEmpty
                && imported.modifiers.isEmpty && imported.importKindSpecifier == nil
        }, "additional declarations/imports require a semantic adapter")
        let declaration = declarations[0]
        let name = try identifier(declaration.name.text)
        try require(declaration.attributes.isEmpty && declaration.modifiers.isEmpty && declaration.genericParameterClause == nil
            && declaration.genericWhereClause == nil && declaration.inheritanceClause?.inheritedTypes.map { $0.type.trimmedDescription } == ["View"],
            "only an unmodified non-generic View struct is mapped")
        var root: [String: Any]?
        for member in declaration.memberBlock.members {
            guard let variable = member.decl.as(VariableDeclSyntax.self), variable.bindingSpecifier.text == "var", variable.bindings.count == 1,
                  let binding = variable.bindings.first, let pattern = binding.pattern.as(IdentifierPatternSyntax.self) else {
                throw LoweringFailure("unsupported view member")
            }
            if pattern.identifier.text == "body" {
                try require(root == nil && variable.attributes.isEmpty && variable.modifiers.isEmpty && binding.initializer == nil
                    && binding.typeAnnotation?.type.trimmedDescription == "some View", "unsupported body declaration")
                guard let accessors = binding.accessorBlock, case .getter(let statements) = accessors.accessors else {
                    throw LoweringFailure("body requires a single view expression")
                }
                let body = try expressions(statements)
                try require(body.count == 1, "body requires a single root view")
                root = try node(body[0])
            } else {
                try require(root == nil && variable.attributes.count == 1 && variable.attributes.trimmedDescription == "@State"
                    && variable.modifiers.allSatisfy { $0.name.text == "private" }
                    && (binding.typeAnnotation == nil || binding.typeAnnotation?.type.trimmedDescription == "Int") && binding.accessorBlock == nil,
                    "only initialized integer State before body is mapped")
                let state = try identifier(pattern.identifier.text)
                guard states[state] == nil, let initializer = binding.initializer else { throw LoweringFailure("missing/duplicate state initializer") }
                states[state] = Int(try number(initializer.value, integer: true))
            }
        }
        guard let root else { throw LoweringFailure("missing View body") }
        return ["name": name, "states": states, "root": root, "rule": "swiftui-literal-and-int-state/1",
            "limitations": ["Layout units, typography and default spacing need visual validation",
                "String localization requires a separate localization mapping", "Swift Int overflow and large integer behavior are not equivalent",
                "Navigation, lifecycle and app entry are outside this page rule"]]
    }
}

do {
    let request = try JSONDecoder().decode(Request.self, from: FileHandle.standardInput.readDataToEndOfFile())
    var files: [[String: Any]] = []
    for file in request.files {
        let tree = Parser.parse(source: file.source)
        let collector = Collector(tree, file.path)
        collector.walk(tree)
        VisibilityCollector(collector).walk(tree)
        let diagnostics = ParseDiagnosticsGenerator.diagnostics(for: tree).map {
            ["message": $0.message, "offset_utf8": $0.position.utf8Offset] as [String: Any]
        }
        let lowering: [String: Any]
        do { lowering = ["status": "mapped", "view": try ArkUIRule(collector.converter).lower(tree)] }
        catch { lowering = ["status": "unsupported", "reason": String(describing: error)] }
        files.append(["path": file.path, "sha256": file.sha256, "nodes": collector.nodes,
                      "visibility_protocol_version": 1,
                      "arkui_rule": lowering,
                      "lexical_items": lexicalItems(Syntax(tree), converter: collector.converter),
                      "parse_has_error": tree.hasError, "diagnostics": diagnostics])
    }
    let output: [String: Any] = ["protocol_version": 1, "lexical_protocol_version": 1,
        "visibility_protocol_version": 1,
        "provider": "SwiftSyntax", "semantic_resolution": false, "files": files]
    let data = try JSONSerialization.data(withJSONObject: output, options: [.sortedKeys])
    FileHandle.standardOutput.write(data)
} catch {
    FileHandle.standardError.write(Data("SwiftSyntax provider error: \(error)\n".utf8))
    exit(2)
}
