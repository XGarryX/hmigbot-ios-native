---
name: arkts-app-identity
description: Android App 身份信息迁移到 HarmonyOS：App 名称（label）、图标（含 layered_image.json 分层自适应图标）、版本号（versionName/versionCode）、包名/厂商（app.json5 的 bundleName/vendor）。当用户需要迁移这些身份字段、或发现 app.json5 中 bundleName/vendor/versionName 仍是模板默认值时触发，从 AndroidManifest.xml / build.gradle 提取原值。即使只说"app 名字不对""图标没迁移""包名还是默认的"也应触发。不处理全量资源迁移（用 android2hmos-resources-convert）、运行时权限或深度链接。
metadata:
  type: domain
  domain: system
  tags:
  - migration
  - app-config
  - bundle-name
  - icon
---
# ArkTS App Identity — 应用身份迁移

## 定位

从 Android 项目提取 App 身份信息（名称、图标、版本号、包名），生成 HarmonyOS 对应配置文件。

本 skill 在迁移管线中的位置：Plan 1 的第一个 task（Task 1.0），在所有其他任务之前执行。

```
Android 项目 → [本 skill] → app.json5 + string.json + 图标资源
```

---

## 输入

| 项 | 内容 |
|----|------|
| **必须** | Android 项目根路径 |
| **可选** | `spec/baseline/feature-base.md` App 身份段（如果 spec 阶段已提取） |
| **可选** | `scope`：`full`（默认，写全部身份字段）/ `dev-identity`（仅 dev 安全字段 app_name / versionName / versionCode / 图标，**跳过 bundleName / vendor**——见 Step 3 说明） |

自动定位以下文件：
- `app/src/main/AndroidManifest.xml`（或扫描 `**/AndroidManifest.xml`）
- `app/build.gradle` 或 `app/build.gradle.kts`
- `**/res/values/strings.xml`（或 `common.gradle` 中的 `resValue`）
- `**/res/mipmap-xxxhdpi/ic_launcher*.png`
- `**/res/mipmap-anydpi-v26/ic_launcher.xml`（自适应图标定义）

---

## 输出

| 文件 | 内容 | 说明 |
|------|------|------|
| `AppScope/app.json5` | bundleName, vendor, versionCode, versionName, icon, label | 更新已有文件，不覆盖无关字段 |
| `AppScope/resources/base/element/string.json` | app_name 字段 | 更新 app_name 值 |
| `AppScope/resources/base/media/foreground.png` | 前景图标 | 从 Android xxxhdpi 提取 |
| `AppScope/resources/base/media/background.png` | 背景图标 | 从 Android xxxhdpi 提取 |
| `AppScope/resources/base/media/layered_image.json` | 自适应图标配置 | 生成或验证 |
| `entry/src/main/resources/base/media/startIcon.png` | 启动图标 | 复制 foreground 或 ic_launcher |
| `entry/src/main/resources/base/element/string.json` | EntryAbility_label | 更新为 app_name |
| 映射报告（输出到控制台） | Android 原值 → HarmonyOS 填充值 | 供用户确认 |

---

## 核心映射规则

```
Android                            →  HarmonyOS
──────────────────────────────────────────────────────
applicationId                      →  bundleName
  规则: 保持原值，或用户自定义
  示例: de.danoeh.antennapod → com.danoeh.antennapod

android:label / app_name (string)  →  app.json5 label ($string:app_name)
  规则: 从 strings.xml 或 build.gradle resValue 解析真实值

versionName                        →  versionName
  规则: 保持一致

versionCode                        →  versionCode
  规则: 保持一致

namespace / applicationId 的组织名   →  vendor
  规则: 提取第二段 (com.example.app → example)

mipmap-xxxhdpi/ic_launcher.png     →  foreground.png
  规则: 优先 xxxhdpi，降级到 xxhdpi/xhdpi

ic_launcher_background.png         →  background.png
  规则: 优先 xxxhdpi，如不存在生成纯色 PNG

adaptive-icon XML (ic_launcher.xml) →  layered_image.json
  格式: { "layered-image": { "background": "$media:background", "foreground": "$media:foreground" } }
```

---

## 工作流程

### Step 1: 提取 Android 身份信息

```
1. Read AndroidManifest.xml
   → 提取 android:label (通常是 @string/app_name)
   → 提取 android:icon (通常是 @mipmap/ic_launcher)

2. Read build.gradle / build.gradle.kts
   → 提取 applicationId / namespace
   → 提取 versionName, versionCode
   → 检查 buildTypes 中的 resValue (动态 app_name)

3. Read strings.xml (如果 label 是 @string 引用)
   → 解析 app_name 的实际文本值
   → 如果 build.gradle 有 resValue 覆盖，使用 release buildType 的值
```

### Step 2: 提取图标资源

```
4. 定位图标文件
   优先级: mipmap-xxxhdpi > mipmap-xxhdpi > mipmap-xhdpi > mipmap-hdpi
   文件: ic_launcher.png, ic_launcher_foreground.png, ic_launcher_background.png

5. 检查自适应图标
   文件: mipmap-anydpi-v26/ic_launcher.xml
   如果存在:
     → 解析 <foreground android:drawable="@xxx"/>
     → 解析 <background android:drawable="@xxx"/>
     → 定位对应的 PNG 文件
```

### Step 3: 生成 HarmonyOS 配置

```
6. 更新 AppScope/app.json5
   仅更新以下字段（保留其他字段不变）:
   - versionCode: 保持
   - versionName: 保持
   - icon: "$media:layered_image" (不变)
   - label: "$string:app_name" (不变)
   - bundleName: 从 applicationId 映射   ⚠️ 仅 scope=full
   - vendor: 从 namespace 提取组织名     ⚠️ 仅 scope=full

   > **scope=dev-identity（a2h-execute Stage 0 调用）**：**跳过 bundleName / vendor**——
   > 二者与签名证书 / AGC 应用上架强绑定，属部署期决策（迁移 ledger C-类目，对应 D-009）。
   > dev 阶段写入真实 bundleName 会与脚手架签名配置 / 后续 AGC 注册不一致，反致装机失败；
   > 保留脚手架占位值，待部署期由 `scope=full`（或人工）统一落地。dev 阶段只消除
   > app_name / versionName 的脚手架默认值（这些无签名影响、却卡真机识别与 a2h-verify）。

7. 更新 AppScope/resources/base/element/string.json
   更新 app_name 的 value 字段

8. 复制图标文件
   - foreground.png → AppScope/resources/base/media/foreground.png
   - background.png → AppScope/resources/base/media/background.png
   - ic_launcher.png → entry/src/main/resources/base/media/startIcon.png
   - ic_launcher.png → entry/src/main/resources/base/media/ic_launcher.png (如存在)

9. 生成/验证 layered_image.json
   确保内容为:
   {
     "layered-image": {
       "background": "$media:background",
       "foreground": "$media:foreground"
     }
   }

10. 更新 entry/src/main/resources/base/element/string.json
    更新 EntryAbility_label 的 value 与 app_name 一致
```

### Step 4: 输出映射报告

```
11. 输出对照表:
    | 字段 | Android 原值 | HarmonyOS 填充值 |
    |------|-------------|-----------------|
    | 应用名称 | AntennaPod | AntennaPod |
    | 包名 | de.danoeh.antennapod | com.danoeh.antennapod |
    | 版本号 | 3.11.0 | 3.11.0 |
    | 版本码 | 3110095 | 3110095 |
    | 厂商 | danoeh | danoeh |
    | 图标 | mipmap-xxxhdpi/ic_launcher.png | foreground.png (XXkb) |

    提示用户确认 bundleName 映射（可能需要调整前缀）。
```

---

## 边界情况处理

| 场景 | 处理方式 |
|------|---------|
| 多模块项目，icon 在子模块 | 从 AndroidManifest.xml 追踪 icon 引用，跨模块定位 |
| build.gradle.kts (Kotlin DSL) | 同时支持 Groovy 和 KTS 语法解析 |
| 无 adaptive-icon (API < 26) | 只有单个 ic_launcher.png → 复制为 foreground.png，生成纯白 background.png |
| app_name 在 build.gradle resValue 中动态定义 | 优先使用 release buildType 的 resValue |
| 多 flavor 的 applicationId | 使用默认 applicationId（无 flavor 后缀） |
| feature-base.md App 身份段已存在 | 直接从 feature-base.md 读取映射值，跳过 Android 项目扫描 |

---

## 跨 Skill 协作

| 协作对象 | 关系 |
|---------|------|
| `a2h-spec` | feature-base.md 的 App 身份段提供映射数据，本 skill 消费 |
| `android2hmos-resources-convert` | 它处理全量资源，本 skill 只处理 app 级身份资源 |
| `arkts-project-scaffolder` | scaffolder 生成模板，本 skill 填充真实值 |
| `a2h-verify` | verify 的 App 身份校验项验证本 skill 的产出 |

---

## 触发 Prompt 示例

```
迁移 app 图标
```

```
app 名字不对
```

```
配置应用信息
```

```
bundleName 还是默认的
```
