// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "HMigBotSwiftSyntax",
    platforms: [.macOS(.v13)],
    products: [.executable(name: "hmigbot-swift-syntax", targets: ["HMigBotSwiftSyntax"])],
    dependencies: [.package(url: "https://github.com/swiftlang/swift-syntax.git", exact: "604.0.0")],
    targets: [.executableTarget(name: "HMigBotSwiftSyntax", dependencies: [
        .product(name: "SwiftSyntax", package: "swift-syntax"),
        .product(name: "SwiftParser", package: "swift-syntax"),
        .product(name: "SwiftParserDiagnostics", package: "swift-syntax"),
        .product(name: "SwiftDiagnostics", package: "swift-syntax"),
        .product(name: "SwiftIfConfig", package: "swift-syntax")
    ], path: ".", exclude: ["README.md", "provider.example.json"], sources: ["main.swift", "ConditionalSource.swift", "CompilerConfiguration.swift"])]
)
