---
name: arkts-app-identity
description: iOS App 身份信息迁移到 HarmonyOS：App 名称（label）、图标（含 layered_image.json 分层自适应图标）、版本号（versionName/versionCode）、包名/厂商（app.json5 的 bundleName/vendor）。当用户需要迁移这些身份字段、或发现 app.json5 中 bundleName/vendor/versionName 仍是模板默认值时触发，从选中 Xcode target 的 Release 配置、Info.plist/InfoPlist.strings 和 Asset Catalog 提取原值。即使只说"app 名字不对""图标没迁移""包名还是默认的"也应触发。不处理全量资源迁移（用 ios-resources-convert）、运行时权限或深度链接。
metadata:
  type: domain
  domain: system
  tags:
  - migration
  - app-config
  - bundle-name
  - icon
---

> **0.13.4 统一合同（优先于历史示例）**：先读 [执行交界合同](../a2h-run/references/execution-boundary.md)。源读取、选定构建配置、SwiftSyntax/facts、源 AC 和 indexed 计划由当前 git 上游唯一生产；从 execute 起使用本技能的 Garry 实施/收口方法。只使用宿主实际支持的派发字段，不照抄 `agent_type`。已有授权直接沿用；依赖失败输入的任务保持 blocked，不降低静态门禁。当前范围禁止屏幕读取/截图/录屏及设备远控；依赖这些观察的检查记 not_run。未经授权不运行遥测上传。工具修复、工具验证、项目转换、HAP 构建和完整迁移验收分别报告，不能用局部 100% 代表全部完成。



# ArkTS App Identity — 应用身份迁移

读取 [原生输入协议](../ios-source-analysis/SKILL.md)。本技能保持原身份阶段与输出格式，只替换源侧取证方式。

## 输入与范围

输入为选定源项目/target/Release、已批准的 feature-base 身份段和目标项目。`scope=full` 写经批准的全部身份字段；`scope=dev-identity` 是原 Stage 0 路径，只更新 app_name、versionName、可确定的 versionCode 和图标，**跳过 bundleName / vendor**，保留现有签名配置。

## Step 1: 提取源身份

从有效构建设置和 Info.plist 读取 PRODUCT_BUNDLE_IDENTIFIER、MARKETING_VERSION、CURRENT_PROJECT_VERSION、CFBundleDisplayName/CFBundleName、CFBundleShortVersionString、CFBundleVersion；读取实际 InfoPlist.strings 本地化覆盖。优先使用绑定当前源码的 Release 导出，不猜未展开的变量；生成 plist 时读取对应有效设置。源码导出设置不代表真实编译、签名或运行通过。

已审批 feature-base 有可追溯映射时直接复用，源值变化则回到原决策流程。目标 vendor 需要批准值，不能从域名的第二段自动猜出。

## Step 2: 提取图标

沿 ASSETCATALOG_COMPILER_APPICON_NAME、CFBundleIcons 与实际 AppIcon.appiconset/Contents.json 定位文件。保留尺寸、scale、appearance 和透明背景证据。iOS 单张图标没有自动对应的前景/背景分层；根据已批准视觉方案复用原图或生成明确的目标分层资源，不伪造源分层。无法解析的编译资源、PDF 或符号记录待替换项，按原资源占位/决策流程处理。

## Step 3: 更新目标配置

只改相关字段，保留无关配置与用户文件：

| 输出 | 操作 |
|---|---|
| AppScope/app.json5 | label/icon 引用、versionName/versionCode；full 才按已批准值改 bundleName/vendor |
| AppScope/resources/base/element/string.json | app_name |
| AppScope/resources/base/media | 实际转换的图标、必要的 foreground/background 与 layered_image.json |
| entry/src/main/resources/base/media | 启动页实际引用的图标资源 |
| entry/src/main/resources/base/element/string.json | EntryAbility_label 与 app_name 一致 |

保留原 `$string:app_name` / `$media:layered_image` 引用约定。使用 layered_image 时核验 background/foreground 引用均真实存在。源 CFBundleVersion 可能不符合目标整数规则，必须记录映射及批准依据，不能直接截断或乱填。dev-identity 不改 bundleName/vendor，也不承诺云服务或签名已开通。

## Step 4: 报告与原门禁

输出字段、源值与锚点、目标值、保留值、未决项的对照。运行原资源引用/身份检查和 Stage 0 编译，不把转换成功当成运行或视觉通过。跨 target、AppIcon 变体、动态本地化、生成 plist 的缺口明确记录，不套用默认源资源路径。
