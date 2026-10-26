// Adapted from Garry ios.32's additive SwiftSyntax facts. Overload resolution,
// source/target equivalence and runtime visibility remain separate review work.
import Foundation
import SwiftSyntax

private final class VisibilityReferences: SyntaxVisitor {
    var names: [String] = []
    func append(_ name: String) {
        let value = name.replacingOccurrences(of: "`", with: "")
        if !["self", "Self", "super", "true", "false", "nil"].contains(value), !names.contains(value) {
            names.append(value)
        }
    }
    override func visit(_ node: DeclReferenceExprSyntax) -> SyntaxVisitorContinueKind {
        if case .identifier = node.baseName.tokenKind { append(node.baseName.text) }
        return .skipChildren
    }
    override func visit(_ node: MemberAccessExprSyntax) -> SyntaxVisitorContinueKind {
        // A contextual enum case (.visible) is not a source data field.
        if let base = node.base { walk(base); append(node.declName.baseName.text) }
        return .skipChildren
    }
    override func visit(_ node: FunctionCallExprSyntax) -> SyntaxVisitorContinueKind {
        // Keep data used to compute a value, excluding constructor/callee names and labels.
        if let member = node.calledExpression.as(MemberAccessExprSyntax.self), let base = member.base { walk(base) }
        for argument in node.arguments { walk(argument.expression) }
        return .skipChildren
    }
    override func visit(_ node: StringLiteralExprSyntax) -> SyntaxVisitorContinueKind { .skipChildren }
    override func visit(_ node: RegexLiteralExprSyntax) -> SyntaxVisitorContinueKind { .skipChildren }
}

final class VisibilityCollector: SyntaxVisitor {
    let collector: Collector
    init(_ collector: Collector) { self.collector = collector; super.init(viewMode: .sourceAccurate) }

    private func callee(_ call: FunctionCallExprSyntax) -> String {
        if let member = call.calledExpression.as(MemberAccessExprSyntax.self) { return member.declName.baseName.text }
        if let ref = call.calledExpression.as(DeclReferenceExprSyntax.self) { return ref.baseName.text }
        return ""
    }
    private func owner(_ node: some SyntaxProtocol) -> String {
        var current = Syntax(node).parent
        while let syntax = current {
            if let value = syntax.as(StructDeclSyntax.self) { return value.name.text }
            if let value = syntax.as(ClassDeclSyntax.self) { return value.name.text }
            if let value = syntax.as(EnumDeclSyntax.self) { return value.name.text }
            if let value = syntax.as(ActorDeclSyntax.self) { return value.name.text }
            if let value = syntax.as(ExtensionDeclSyntax.self) { return value.extendedType.trimmedDescription }
            current = syntax.parent
        }
        return ""
    }
    private enum Context { case render, action, unresolved }
    private struct WidgetBuilderSignature {
        let labels: [String]
        let contentClosures: Set<Int>
    }
    // Derived from public WidgetKit init signatures (see README.md for scope).
    // Indices refer to declaration parameters, so
    // explicit and forward-scanned trailing closures use the same slot.
    // ActivityConfiguration.dynamicIsland is a DynamicIsland-returning UI
    // configuration closure, not a ViewBuilder parameter.
    private static let widgetBuilders: [String: WidgetBuilderSignature] = [
        "AppIntentConfiguration": .init(labels: ["kind", "intent", "provider", "content"], contentClosures: [3]),
        "StaticConfiguration": .init(labels: ["kind", "provider", "content"], contentClosures: [2]),
        "IntentConfiguration": .init(labels: ["kind", "intent", "provider", "content"], contentClosures: [3]),
        "ActivityConfiguration": .init(labels: ["for", "content", "dynamicIsland"], contentClosures: [1, 2]),
        "DynamicIsland": .init(labels: ["expanded", "compactLeading", "compactTrailing", "minimal"], contentClosures: [0, 1, 2, 3]),
        "DynamicIslandExpandedRegion": .init(labels: ["", "priority", "content"], contentClosures: [2])
    ]
    private func widgetClosureContext(_ closure: ClosureExprSyntax, _ call: FunctionCallExprSyntax) -> Context? {
        guard let signature = Self.widgetBuilders[callee(call)] else { return nil }
        var cursor = 0
        var slots: [SyntaxIdentifier: Int] = [:]
        for argument in call.arguments {
            let label = argument.label?.text ?? ""
            guard let index = signature.labels.indices.first(where: { $0 >= cursor && signature.labels[$0] == label }) else {
                return .unresolved
            }
            if let value = argument.expression.as(ClosureExprSyntax.self) { slots[value.id] = index }
            cursor = index + 1
        }
        if let trailing = call.trailingClosure {
            // Swift scans forward from the explicit arguments to the first
            // remaining closure parameter; later trailing closures are labeled.
            guard let index = signature.labels.indices.first(where: { $0 >= cursor && signature.contentClosures.contains($0) }) else {
                return .unresolved
            }
            slots[trailing.id] = index
            cursor = index + 1
        }
        for trailing in call.additionalTrailingClosures {
            guard let index = signature.labels.indices.first(where: {
                $0 >= cursor && signature.labels[$0] == trailing.label.text && signature.contentClosures.contains($0)
            }) else { return .unresolved }
            slots[trailing.closure.id] = index
            cursor = index + 1
        }
        guard let index = slots[closure.id], signature.contentClosures.contains(index) else { return .unresolved }
        return .render
    }
    private func renderType(_ type: TypeSyntax?) -> Bool {
        type?.tokens(viewMode: .sourceAccurate).contains {
            ["View", "Scene", "Widget", "WidgetConfiguration", "ToolbarContent", "Commands"].contains($0.text)
        } == true
    }
    private func closureContext(_ closure: ClosureExprSyntax) -> Context {
        var call: FunctionCallExprSyntax?
        var label = ""
        if let argument = closure.parent?.as(LabeledExprSyntax.self) {
            label = argument.label?.text ?? ""
            call = argument.parent?.parent?.as(FunctionCallExprSyntax.self)
        } else if let extra = closure.parent?.as(MultipleTrailingClosureElementSyntax.self) {
            label = extra.label.text
            call = extra.parent?.parent?.as(FunctionCallExprSyntax.self)
        } else { call = closure.parent?.as(FunctionCallExprSyntax.self) }
        guard let call else { return .unresolved }
        let name = callee(call)
        if let context = widgetClosureContext(closure, call) { return context }
        // These slots follow SwiftUI SDK builder/action signatures, not app identifiers.
        let builders: Set<String> = ["VStack", "HStack", "ZStack", "LazyVStack", "LazyHStack", "LazyVGrid", "LazyHGrid",
            "Group", "GroupBox", "List", "ForEach", "ScrollView", "ScrollViewReader", "GeometryReader", "Section",
            "Form", "NavigationStack", "NavigationView", "NavigationSplitView", "TabView", "ToolbarItem", "ToolbarItemGroup",
            "WindowGroup", "TimelineView", "ViewThatFits", "Grid", "GridRow", "AnyView"]
        let actions: Set<String> = ["onAppear", "onDisappear", "onChange", "onReceive", "onSubmit", "onTapGesture",
            "onLongPressGesture", "task", "refreshable", "onOpenURL", "onContinueUserActivity"]
        if actions.contains(name) { return .action }
        let renderLabels: Set<String> = ["content", "label", "destination", "header", "footer", "placeholder", "rowContent", "message"]
        let mixed: Set<String> = ["Button", "Menu", "NavigationLink", "Picker", "Toggle", "DisclosureGroup", "Label",
            "sheet", "fullScreenCover", "popover", "alert", "confirmationDialog", "contextMenu", "overlay", "background",
            "safeAreaInset", "toolbar", "navigationDestination", "AsyncImage"]
        if builders.contains(name) { return .render }
        if mixed.contains(name) {
            if renderLabels.contains(label) { return .render }
            if label == "action" || label == "onDismiss" || label == "onCompletion" { return .action }
            if name == "Button" {
                return call.arguments.contains(where: { $0.label?.text == "action" }) ? .render : .action
            }
            if name == "alert" || name == "confirmationDialog" { return .action }
            if label.isEmpty { return .render }
        }
        return .unresolved
    }
    private func context(_ node: some SyntaxProtocol) -> Context {
        var current = Syntax(node).parent
        var unresolved = false
        while let syntax = current {
            if let closure = syntax.as(ClosureExprSyntax.self) {
                switch closureContext(closure) {
                case .action: return .action
                case .unresolved: unresolved = true
                case .render: break
                }
            }
            if let binding = syntax.as(PatternBindingSyntax.self), binding.initializer != nil { return .action }
            if let variable = syntax.as(VariableDeclSyntax.self) {
                let isView = variable.bindings.contains { renderType($0.typeAnnotation?.type) }
                    || variable.attributes.trimmedDescription.contains("ViewBuilder")
                return isView ? (unresolved ? .unresolved : .render) : .action
            }
            if let function = syntax.as(FunctionDeclSyntax.self) {
                let isView = function.attributes.trimmedDescription.contains("ViewBuilder")
                    || renderType(function.signature.returnClause?.type)
                return isView ? (unresolved ? .unresolved : .render) : .action
            }
            current = syntax.parent
        }
        return .action
    }
    private func controllingConditions(_ node: some SyntaxProtocol) -> [Syntax] {
        var result: [Syntax] = []
        var current = Syntax(node).parent
        while let syntax = current {
            if syntax.is(FunctionDeclSyntax.self) || syntax.is(AccessorDeclSyntax.self) { break }
            if let branch = syntax.as(IfExprSyntax.self) { result.append(Syntax(branch.conditions)) }
            if let branch = syntax.as(SwitchExprSyntax.self) { result.append(Syntax(branch.subject)) }
            if let branch = syntax.as(GuardStmtSyntax.self) { result.append(Syntax(branch.conditions)) }
            if let items = syntax.as(CodeBlockItemListSyntax.self) {
                for item in items where item.positionAfterSkippingLeadingTrivia < node.positionAfterSkippingLeadingTrivia {
                    if let guardNode = item.item.as(GuardStmtSyntax.self) { result.append(Syntax(guardNode.conditions)) }
                }
            }
            current = syntax.parent
        }
        return result
    }
    private func add(_ node: some SyntaxProtocol, expression: String, references: [Syntax], form: String,
                     render: Context? = nil, keepUnresolvedConstant: Bool = false) {
        let refs = VisibilityReferences(viewMode: .sourceAccurate)
        references.forEach { refs.walk($0) }
        guard !refs.names.isEmpty || keepUnresolvedConstant else { return }
        let state = refs.names.isEmpty ? Context.unresolved : (render ?? context(node))
        if state == .action { return }
        collector.add(state == .render ? "visibility" : "visibility_unresolved", node,
            ["owner": owner(node), "expression": expression, "drivers": refs.names, "form": form,
             "context": state == .render ? "render-syntax" : "unresolved-syntax"])
    }
    override func visit(_ node: IfExprSyntax) -> SyntaxVisitorContinueKind {
        var references: [Syntax] = []
        for condition in node.conditions {
            if let binding = condition.condition.as(OptionalBindingConditionSyntax.self) {
                if let initializer = binding.initializer { references.append(Syntax(initializer.value)) }
                else if let pattern = binding.pattern.as(IdentifierPatternSyntax.self) {
                    // Swift shorthand `if let value` reads the existing optional value.
                    let expr = DeclReferenceExprSyntax(baseName: pattern.identifier)
                    references.append(Syntax(expr))
                }
            } else { references.append(Syntax(condition.condition)) }
        }
        add(node, expression: node.conditions.trimmedDescription, references: references, form: "if")
        return .visitChildren
    }
    override func visit(_ node: SwitchExprSyntax) -> SyntaxVisitorContinueKind {
        add(node, expression: node.subject.trimmedDescription, references: [Syntax(node.subject)], form: "switch")
        return .visitChildren
    }
    override func visit(_ node: TernaryExprSyntax) -> SyntaxVisitorContinueKind {
        if node.parent?.is(CodeBlockItemSyntax.self) == true || node.parent?.is(ReturnStmtSyntax.self) == true {
            add(node, expression: node.condition.trimmedDescription, references: [Syntax(node.condition)], form: "ternary")
        }
        return .visitChildren
    }
    override func visit(_ node: SequenceExprSyntax) -> SyntaxVisitorContinueKind {
        let elements = Array(node.elements)
        let property = elements.first?.as(MemberAccessExprSyntax.self)?.declName.baseName.text
            ?? elements.first?.as(DeclReferenceExprSyntax.self)?.baseName.text ?? ""
        if elements.count > 2, elements[1].is(AssignmentExprSyntax.self), ["isHidden", "alpha"].contains(property) {
            let rhs = elements.dropFirst(2)
            // UIKit assignments are imperative; their source data still drives visibility.
            add(node, expression: rhs.map { $0.trimmedDescription }.joined(separator: " "),
                references: rhs.map { Syntax($0) } + controllingConditions(node),
                form: "assignment-" + property, render: .render, keepUnresolvedConstant: true)
        } else if let index = elements.firstIndex(where: { $0.is(UnresolvedTernaryExprSyntax.self) }), index > 0,
                  node.parent?.is(CodeBlockItemSyntax.self) == true || node.parent?.is(ReturnStmtSyntax.self) == true {
            let condition = elements.prefix(index)
            add(node, expression: condition.map { $0.trimmedDescription }.joined(separator: " "),
                references: condition.map { Syntax($0) }, form: "ternary")
        }
        return .visitChildren
    }
    override func visit(_ node: FunctionCallExprSyntax) -> SyntaxVisitorContinueKind {
        if callee(node) == "opacity", node.calledExpression.is(MemberAccessExprSyntax.self), let first = node.arguments.first {
            add(node, expression: first.expression.trimmedDescription, references: [Syntax(first.expression)], form: "opacity")
        }
        return .visitChildren
    }
}
