# 0.9.3 本地发布候选 · 2026-10-22

本版本整合 ios2harmonyTest 工程可追溯的工具优化，供后续人工上传服务器。未执行上传、线上部署、Git 推送或真实应用迁移。

## 交付

- 源安装包：本目录，版本元数据统一为 0.9.3。
- 可复用 ZIP、SHA256、逐文件摘要及独立验证日志位于本包外的同轮 release 输出目录，防止压缩包包含自身。
- 优化总表与证据（本地过程记录：`reports/optimization-rollup-2026-10-22.md`）。最终验证数据见 docs/reports/release-validation.json 和 release 输出中的原始日志。

## 安装与升级

Python 3.11+；macOS 使用 `PYTHON=python3 sh install.sh <workspace>`，Windows 按 [INSTALL](INSTALL.md) 指定 Python 和 Workspace。安装仅写明确工作区托管目录。

保持 96 个技能、29 个角色、原五阶段、稳定 page/F/AC 和原三账本写者。新增 conditional-capture、gate-artifacts、verify-report 与参数透传。无证据的语义/AC/构建/设备项保持 unknown/BLOCKED/DEFERRED。

工具合同 revision 会变化，已有冻结任务不能继续使用旧合同落账；先完成或明确终止在途任务，审阅差异，再走既有 replan。升级不会替用户改 Spec 或账本。安装器拒绝覆盖用户编辑的托管文件；先备份和选择性合并，不能删除 install.json 或手改摘要强装。

## 兼容与已知边界

本轮 macOS arm64 实测。原Nuitka载荷在其自身路径含中文时会在初始化阶段abort；source-neutral公共包装器现将原载荷临时复制到ASCII路径运行，用户工程参数保持原值，vendor字节不变。Windows/Linux 资产和兼容测试保留；平台专用跳过项不计通过，未完成本轮跨平台实机认证。Xcode/Clang/SDK/设备依赖仍按实际环境提供，包内不携带用户源 SDK、凭证或 Apple SDK。

Clang 条件证据仅支持规程列明的单 target、文本观察及严格 guard/枚举见证；完整性不是采集身份认证或行为等价。证据绑定绝对输入路径、编译器/SDK/PCM 摘要，换机器或依赖更新应重新采集。Swift 条件、多 target、复杂 module/PCH 情况仍保留阻断。

`conditional-capture` 消费满足新版合同的 source_build 包。现有云 build_source.py 不自动产生全部新版编译单元/工具链/模块前后证据；旧云包不能直接升级为有效条件证据。通用化的完整 source_build 生产入口仍是后续工作，项目专用 capture 脚本未混入发行包。

Xcode 自动 AST 路径现会在 DerivedData 存活时展开 response 并运行真实 Clang，拒绝失败构建。新增回归使用受控构建日志和真实 Clang；本轮没有对真实用户工程重新执行 Xcode 构建，不能据此宣布任意 Xcode 工程均已支持。

门禁文件自动补全只提供待审结构，不自动完成语义、平台决策或正式计划；current 表示报告与当前证据一致。结构静态证明不等于运行行为，宿主工具测试不等于鸿蒙 HAP/双端设备验收。

既有上游参考文档的一处摘要差异透明登记在 derivative-manifest.json；本轮没有更改其正文或原二进制字节。该历史文档的 ArkTS API 未在本轮重做官方文档认证。

## 复现验证

```sh
python3 -m venv /tmp/hmigbot-release-check
/tmp/hmigbot-release-check/bin/python -m pip install 'pytest>=8,<10'
/tmp/hmigbot-release-check/bin/python scripts/validate_release.py --output /tmp/hmigbot-release-evidence-new
python3 scripts/package_plugin.py --output /tmp/hmigbot-ios-0.9.3.zip
python3 scripts/smoke_package.py --package /tmp/hmigbot-ios-0.9.3.zip --output /tmp/hmigbot-ios-smoke-new.json
```

每次选择未存在的输出路径。验证命令的非零退出码、失败日志和跳过项须保留；不能通过改报告、旧 PASS 或排除失败用例发布。
