# 升级清理、归档与隔离属性修复

仅当前转换项目是写入边界。工具升级不等于项目转换、编译或行为通过。

## 执行顺序

1. 检查旧安装所有权、用户编辑和所有目标路径；失败时不清理。
2. 只读识别已知生成文件，核对内容形状或完整生成marker。文件名相同但内容不认识时保留并记录。
3. 项目内 `.hmigbot-ios/upgrade-history/<id>/generated/` 归档全部候选，记录原路径、摘要、权限；全部归档核对后再移走原文件。
4. 替换工具，按需修复项目内工具运行时的下载隔离属性，写安装回执与清理收据。任何后续失败恢复原文件及安装；并发新内容不覆盖，记录具体回滚阻断并继续恢复其他文件。
5. 项目owner用原已审variant/provider重新运行facts、literals、facts-view和派生报告，重审新图绑定与门禁；不能手改机器义务或继承旧PASS。

同版本工具内容变更也触发清理；首次安装、工具无变化的重装不清理。

## 可清理的精确产物

- baseline：`ios-facts.json`、`ios-obligations.json`、`literal-ledger.json`、`ios-source-check.json`。
- reports：`ios-harness-check.json`、`spec-check.json`、`spec-summary.json`、`product-literals.json`。
- 具有原生成marker的 `spec/ui-coverage-report.md`、`migration-report.md`、`verify-report.md`，以及 `spec/reports/derived/ui-plan.md`、`feature-plan.md`。
- ref：原工具生成的 `ios-{project,ui,feature,api}-signals.json`；原始build/provider/条件捕获及审阅证据保留。

每个JSON还需符合相应机器输出的字段形状，不以目录名或文件存在授权清空。

保留：作者Spec/AC/正式计划、决策、source-index源变更审批边界、ios-semantics、ios-coverage、ios-responsibility、verification/impl-claims、原始证据、应用源码/产物、state/dispatch/journal及blueprint/waves。归档是恢复证据，不另立转换账本。

## 项目内隔离属性修复

在已配置或已安装的转换项目内运行：

```sh
.migbot/bin/a2h-tool repair-permissions --path .hmigbot-ios/plugin/vendor/hmigbot/skills/a2h-spec/scripts/bin/macos-arm64/_entry.dist
.migbot/bin/a2h-tool repair-permissions
```

第一条只检查指定运行时；第二条显式检查当前项目根。实际移除命令为 `xattr -dr com.apple.quarantine <通过边界检查的路径>`，仅检测到该属性后调用，并核验返回与剩余属性。

安装器和helper/调度/结构运行层在需要调用本地二进制的位置使用同一检查。项目外源工具或临时runtime不会成为另一个修复根；越界链接、硬链接、HOME、系统根被拒绝。权限失败返回真实receipt，退出0但属性仍在也失败。该功能不修改系统安全策略或给产品行为记PASS。
