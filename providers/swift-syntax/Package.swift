// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "HMigBotSwiftSyntax",
    platforms: [.macOS(.v13)],
    products: [.executable(name: "hmigbot-swift-syntax", targets: ["HMigBotSwiftSyntax"])],
    dependencies: [.package(url: "https://github.com/swiftlang/swift-syntax.git", exact: "600.0.1")],
    targets: [.executableTarget(name: "HMigBotSwiftSyntax", dependencies: [
        .product(name: "SwiftSyntax", package: "swift-syntax"),
        .product(name: "SwiftParser", package: "swift-syntax"),
        .product(name: "SwiftParserDiagnostics", package: "swift-syntax")
    ], path: ".", exclude: ["README.md", "provider.example.json"], sources: ["main.swift", "VisibilityFacts.swift"])]
)
