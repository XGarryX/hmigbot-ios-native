# Clang AST provider

复制 provider.example.json，填入真实 Clang 和当前构建变体的参数。每个 translation_units 项指定源文件与参数数组，必须包含 -fsyntax-only 以及 -Xclang -ast-dump=json。`{file}`/`{source}` 替换为文件/根目录，进程工作目录为 source。

调用 `atom clang-ast --source <source> --provider-config <config> --output <new-dir>`。保留原始编译器 AST、诊断、命令、版本、退出码和源摘要；不把编译失败时的部分 AST 当完整成功。不自行重写或猜测编译器的 location/引用信息。

本机随 DevEco 的 Clang 可解析不依赖 Apple SDK 的 Objective-C 语法夹具；这不意味着 Windows 拥有 UIKit/Foundation。实际 iOS 变体需在 Mac/云端使用 Xcode 的 sysroot、target triple、framework/header/module 搜索路径、宏、ARC 与 ObjC++ 参数。调用记录必须与 A02 变体对应。

参考：[LLVM Clang AST 文档](https://clang.llvm.org/docs/IntroductionToTheClangAST.html)。本包没有复制 Clang 二进制。
