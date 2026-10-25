---
name: arkts-i18n
description: 'ArkTS/HarmonyOS 国际化（i18n）技能（V2 优先，API 12+）。当用户需要添加多语言支持、实现动态语言切换、配置资源文件、处理国际化资源目录结构、扫描硬编码字符串，或任何与"国际化"、"多语言"、"切换语言"相关的问题时，务必触发此 skill。 即使用户只是说"怎么添加英文"或"怎么做中英文切换"，也应触发。

  '
metadata:
  type: domain
  domain: engineering
  tags:
  - i18n
  - localization
  - multi-language
  - resource-manager
---
# ArkTS I18N — 国际化指南（V2 优先）

## API 版本与项目策略

本 skill 的代码示例基于 **API 12+（HarmonyOS 5.0.0+）和 ArkTS V2 装饰器体系**。

> **项目锁 V2**：所有新生成的"语言切换 / locale 状态 / refreshKey"代码使用 V2 装饰器（`@ComponentV2 / @Local / @Param / @Once / @ObservedV2 / @Trace / AppStorageV2.connect / PersistenceV2.globalConnect`）。i18n 相关 API（`resourceManager` / `intl` / `$r('app.string.xxx')` / `setPreferredLanguage` / `getPreferredLanguage` / `onLanguageConfigurationUpdate`）在 V1/V2 之间**完全不变**。
>
> 仅当需要查阅老项目 V1 写法（`@Component / @State / @StorageLink('currentLanguage')` 等）时，参阅 [`references/v1-compat.md`](./references/v1-compat.md) 与现有 legacy 文档（已加历史标识）。

V1 → V2 关键差异（仅与本 skill 相关的 state 部分）：

| V1 | V2 |
|---|---|
| `@Component` | `@ComponentV2` |
| `@State refreshKey: number = 0` | `@Local refreshKey: number = 0` |
| `@StorageLink('currentLanguage') lang: string = 'zh'` | `@Local locale: LocaleModel = AppStorageV2.connect(LocaleModel, 'locale', () => new LocaleModel())!`（需先定义 `@ObservedV2 LocaleModel`） |
| `@Prop currentColumns: number = 3` | `@Param @Once currentColumns: number = 3`（只读） |
| `@Watch('lang') onLangChange()` | `@Monitor('lang') onLangChange(m: IMonitor)` |
| `AppStorage.setOrCreate('refreshKey', n)` | `localeModel.refreshKey = n`（直接改 @Trace 字段，自动同步） |
| `PersistentStorage.persistProp('currentLanguage', 'zh')` | `PersistenceV2.globalConnect({ type: LocaleModel, key: 'locale', defaultCreator: () => new LocaleModel() })` |

> **重要**：i18n 业务 API（`resourceManager.setPreferredLanguage()` / `$r()` / `onLanguageConfigurationUpdate()` 等）**与装饰器版本无关**。本次升级仅替换状态装饰器，API 调用方式不变。

---

## 触发场景

- "怎么做国际化"、"添加多语言支持"
- "实现中英文切换"
- "资源文件怎么组织"
- "动态切换语言不生效"
- "怎么添加日语/韩语/其他语言"
- "扫描硬编码字符串"、"找出没有国际化的文本"
- **被 a2h-execute 主线程自动调用**（task=translate-pending-todos，详见下方"自动翻译模式"）

---

## 自动翻译模式（被 a2h-execute 调用时）

a2h-execute 在 Stage 0 完成后若检测到 `spec/placeholder-registry.md` 含 `kind=resource-pending-translation` 条目，会**自动调用本 skill**：

调用 `$arkts-i18n` skill（读取 `.agents/skills/arkts-i18n/SKILL.md` 并按其执行），参数：`task=translate-pending-todos source_locale=base target_locales=<auto-detect> registry=spec/placeholder-registry.md`

收到 `task=translate-pending-todos` 时，按以下流程执行（不需要用户介入）：

### 自动流程

1. **读 registry** — 解析 `spec/placeholder-registry.md`，过滤 `kind=resource-pending-translation` 且 `status ∈ {registered, pending}` 的所有条目；每条 `location` 字段形如 `entry/src/main/resources/<locale>/element/<file>.json:<key>`
2. **按 locale 分组** — 每个目标 locale 单独处理
3. **逐 key 翻译** — 对每个 P-ID，读出 `[TODO: translate]` 前缀的英文原值，按目标 locale 生成真实翻译（LLM 按本 skill 既有"步骤 4：添加到 string.json"风格产出）。术语一致性参考 `references/code-examples.md` / `references/static-vs-dynamic.md`
4. **落盘** — 用 Edit/Write 把真实翻译写回对应 `resources/<locale>/element/<file>.json` 的 `value` 字段，**移除 `[TODO: translate]` 前缀**
5. **跨 locale 一致性验证** — 跑 `scripts/audit_i18n_completeness.sh --project-root <abs> --output-json docs/i18n-audit.json`；若 FAIL 则报告 missing keys 并停止
6. **更新 registry** — 把已处理的 P-ID 的 `status` 字段从 `registered` / `pending` 改为 `resolved`
7. **返回报告** — 输出 `{translated_count, locales, audit_pass, updated_registry_path}` 结构化结果给 a2h-execute 主线程

### 异常处理

- 任一 locale 的翻译产出无法通过审阅（含未翻译英文、术语不一致等）→ 保留 `[TODO: translate]` 前缀 + registry status 不更新 + 返回 `failed_translations[]` 让 a2h-execute 写迁移报告
- `audit_i18n_completeness.sh` 退出码 1（key_missing）→ 同上

> 此模式下 LLM 充当翻译引擎，但**仍可被独立审阅**——产出的翻译会留在 git working tree，用户跑完整 pipeline 后随时可 review / amend。

---

## 核心概念

HarmonyOS 国际化基于「**资源文件目录分级**」和「**系统语言检测**」：

```
resources/
├── base/           // Fallback 资源（无匹配时使用）
├── zh_CN/          // 简体中文
├── en_US/          // 美国英文
└── ja/             // 日文
```

- **静态引用**：`$r('app.string.xxx')` 由系统根据当前语言自动加载
- **动态切换**：通过 `resourceManager.setPreferredLanguage()` 手动指定语言

### ⚠️ base/ 目录的作用

**base/ 不是"中文目录"，而是 Fallback 目录！**

```
资源匹配规则：
1. 系统根据当前语言查找匹配目录（zh-CN → zh_CN、zh-Hans、zh）
2. 找到匹配目录？→ ✅ 使用该目录的资源
3. 未找到？→ 使用 base/ 目录的资源（Fallback）
```

---

## 资源文件结构

### 标准目录结构

```
src/main/resources/
├── base/                      # Fallback 资源
│   ├── element/
│   │   └── string.json        # 字符串资源
│   └── media/                  # 图片资源
├── zh_CN/                     # 简体中文
│   └── element/
│       └── string.json
├── en_US/                     # 美国英文
│   ├── element/
│   │   └── string.json
│   └── media/
│       └── logo.png           # 英文版 logo（可选）
└── ja/                        # 日文
    └── element/
        └── string.json
```

### 目录命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 语言 | ISO 639-1 | `en`, `ja`, `ko`, `zh` |
| 语言+区域 | ISO 639-1 + ISO 3166-1 | `zh_CN`, `en_US`, `zh_TW` |

> ⚠️ 目录名必须完全匹配，否则系统无法识别

---

## 字符串资源文件

### JSON 格式

**base/element/string.json**：
```json
{
  "string": [
    { "name": "app_name", "value": "App Name" },
    { "name": "confirm", "value": "Confirm" }
  ]
}
```

**zh_CN/element/string.json**：
```json
{
  "string": [
    { "name": "app_name", "value": "应用名称" },
    { "name": "confirm", "value": "确认" }
  ]
}
```

### 引用方式

```typescript
// 静态引用
Text($r('app.string.app_name'))
Button($r('app.string.confirm'))
Image($r('app.media.logo'))
```

### 插值参数（占位符）

```json
// string.json
{ "name": "file_count", "value": "共 %d 个文件" }
```

```typescript
// 代码中替换
const str = resourceManager.getStringByNameSync('file_count')
const message = str.replace('%d', count.toString())
```

---

## module.json5 配置

### 声明支持的语言

```json5
{
  "module": {
    "name": "entry",
    "type": "entry",
    "supportedLanguages": [
      "zh-Hans",  // 简体中文
      "en",       // 英文
      "ja"        // 日文
    ]
  }
}
```

> ⚠️ `supportedLanguages` 声明后，`setPreferredLanguage()` 才能正确工作
> 当前代码仓未配置此字段，如需动态语言切换，建议添加

---

## 动态语言切换（V2）

### 基本实现

V2 项目用 `@Local` 持有 refreshKey；i18n API 不变：

```typescript
import { resourceManager } from '@kit.LocalizationKit'
import { common } from '@kit.AbilityKit'

@Entry
@ComponentV2
struct LanguageSettings {
  private context = getContext(this) as common.UIAbilityContext
  @Local private refreshKey: number = 0

  async switchLanguage(lang: string): Promise<void> {
    const resMgr = this.context.resourceManager
    await resMgr.setPreferredLanguage([lang])
    this.refreshKey++  // 触发 UI 重建
  }

  build() {
    Column() {
      Text($r('app.string.welcome'))
        .fontSize(20)
    }
    .id('lang_' + this.refreshKey)
  }
}
```

### 全局共享 locale 状态（V2 推荐）

把 `currentLanguage` / `refreshKey` 封装到一个 `@ObservedV2 LocaleModel`，用 `AppStorageV2.connect` 在所有页面共享单例：

```typescript
// common/LocaleModel.ets
@ObservedV2
export class LocaleModel {
  @Trace currentLanguage: string = 'zh'
  @Trace refreshKey: number = 0
}

// 任意 V2 组件
@ComponentV2
struct AnyPage {
  @Local locale: LocaleModel = AppStorageV2.connect(
    LocaleModel,
    'locale',
    () => new LocaleModel()
  )!

  build() {
    Column() {
      Text($r('app.string.hello'))
        .id('page_' + this.locale.refreshKey)  // refreshKey 改 → 自动重建
    }
  }
}
```

> 修改 `this.locale.refreshKey++` 即可同步刷新所有 `connect` 同一 key 的组件，无需 V1 `@StorageLink` 散字段。

### 获取当前系统语言

```typescript
async getCurrentLanguage(): Promise<string> {
  const resMgr = this.context.resourceManager
  const languages = await resMgr.getPreferredLanguage()
  return languages[0] || 'zh'
}
```

### 监听语言变化

```typescript
// 在 EntryAbility 中
onLanguageConfigurationUpdate(): void {
  hilog.info(0x0000, 'I18N', 'Language changed')
}
```

---

## 图片国际化

```
resources/
├── base/media/logo.png         # 默认 logo
├── en/media/logo.png           # 英文版 logo（同名）
└── zh_CN/media/logo.png        # 中文版 logo（同名）
```

```typescript
// 同一引用路径，不同语言加载不同文件
Image($r('app.media.logo'))
```

> ⚠️ 不同语言目录下的图片**文件名必须一致**

---

## 常见错误

### 错误 1：硬编码字符串

```typescript
// ❌ 错误
Text('确认')
Button('登录')

// ✅ 正确
Text($r('app.string.confirm'))
Button($r('app.string.login'))
```

### 错误 2：目录命名错误

```typescript
// ❌ 错误
resources/chinese/element/string.json

// ✅ 正确
resources/zh_CN/element/string.json
```

### 错误 3：未声明 supportedLanguages

导致 `setPreferredLanguage()` 不生效。

### 错误 4：动态切换后 UI 不更新

```typescript
// ❌ 错误 — 直接返回
await resMgr.setPreferredLanguage([lang])

// ✅ 正确 — 触发重建
await resMgr.setPreferredLanguage([lang])
this.refreshKey++
```

### 错误 5：string.json 格式错误

```json
// ❌ 错误 — value 被双引号包裹
{ "name": "app_name", "value": "\"图库\"" }

// ✅ 正确
{ "name": "app_name", "value": "图库" }
```

---

## 硬编码字符串扫描与迁移

当用户需要**扫描项目中的硬编码字符串并迁移到 resources**时，执行以下流程：

### 步骤 1：扫描硬编码

```bash
rg "Text\(['\"]" --type ets -n
rg "Button\(['\"]" --type ets -n
rg "showToast\(['\"]" --type ets -n
```

### 步骤 2：识别需要迁移的字符串

**排除**：已使用 `$r()` 引用、URL、代码变量、正则、单字符

**需要迁移**：
```typescript
Text('确认')
Button('取消')
.title('设置页面')
promptAction.showToast('操作成功')
```

### 步骤 3：生成资源 key

| 场景 | key 格式 | 示例 |
|------|---------|------|
| 按钮 | `btn_xxx` | `btn_confirm`, `btn_cancel` |
| 标题 | `title_xxx` | `title_settings` |
| 消息 | `msg_xxx` | `msg_delete_confirm` |
| Toast | `toast_xxx` | `toast_save_success` |

### 步骤 4：添加到 string.json

**base/element/string.json**：
```json
{ "name": "confirm", "value": "确认" }
```

**en_US/element/string.json**：
```json
{ "name": "confirm", "value": "Confirm" }
```

### 步骤 5：替换代码

```typescript
// 替换前
Text('确认')

// 替换后
Text($r('app.string.confirm'))
```

### 步骤 6：验证

**1) 跨 locale key 一致性（自动）** — 跑本 skill 自带的完整性脚本：

```bash
bash <skill-root>/arkts-i18n/scripts/audit_i18n_completeness.sh \
    --project-root <abs> \
    --output-json docs/i18n-audit.json
```

职责：扫 `string.json` / `plural.json` / `strarray.json`，base 的全部 key 必须在每个 language locale（zh_CN / en_US / ...）出现；mode locale（dark / horizontal / vertical 等）按差异覆盖即可，豁免。

退出码：`0` 全 PASS / `1` 有 key_missing FAIL / `2` 脚本参数错误。

> 资源 value 内未注册的 `[TODO: translate]` / 裸 TODO 占位**不归本脚本管**——由 `arkts-structural-closure/scripts/audit_skeletons.py` 的 L5 patterns 在 pipeline 模式统一扫描。两者职责正交。
>
> 本脚本由 arkts-i18n 任务收尾**自行调用**，**不被其他 skill 跨引用**（减少跨 skill 耦合）。

**2) 手工 / 编译检查**：

- [ ] 所有用户可见字符串都已替换为 `$r()` 引用
- [ ] 替换后能正常编译

---

## 生成检查清单

- [ ] 资源目录使用标准语言代码
- [ ] string.json 格式正确
- [ ] 所有用户可见字符串使用 `$r()` 引用
- [ ] module.json5 中声明 `supportedLanguages`（如需动态切换）
- [ ] 不同语言目录下的图片文件名一致
- [ ] 已扫描硬编码字符串并迁移到 resources

---

## API 验证状态

| API | 状态 |
|-----|------|
| `resourceManager.getStringByNameSync()` | ✅ 已验证 |
| `resourceManager.getStringByName()` | ⚠️ 需查证 |
| `setPreferredLanguage()` | ⚠️ 需查证 |
| `getPreferredLanguage()` | ⚠️ 需查证 |
| `$r('app.string.xxx')` | ✅ 已验证 |

---

## References

详细文档和完整代码示例请参阅（**全部代码示例已升级 V2**）：

| 文件 | 内容 |
|------|------|
| `references/resource-file-structure.md` | 完整资源目录结构模板（与装饰器版本无关） |
| `references/dynamic-language-switch.md` | 动态语言切换完整代码（V2，含 LocaleModel） |
| `references/common-pitfalls.md` | 避坑指南与错误对照表（V2） |
| `references/hardcoded-string-scanner.md` | 硬编码扫描脚本和工具（与装饰器版本无关） |
| `references/language-codes.md` | 语言代码对照表（ISO 标准） |
| `references/code-examples.md` | ColumnsDialog 等代码示例（V2） |
| `references/static-vs-dynamic.md` | 纯静态 vs 动态切换方案对比 |
| `references/v1-compat.md` | **V1 兼容写法**（@Component / @State / @StorageLink），仅老项目查阅 |

---

## 跨 Skill 协作

| 需要什么 | 读取哪里 |
|---------|---------|
| 项目脚手架 | `arkts-project-scaffolder/SKILL.md` |
| 设置页面实现 | `arkts-pattern-library/references/v2-media-app-pattern.md` |
| V2 状态管理（@Local / @Param / @Event / AppStorageV2） | `arkts-state-manager/SKILL.md` + `arkts-state-manager/references/v2-decorators.md` |
| @Provider/@Consumer 跨页传 locale | `arkts-state-manager/references/v2-real-world.md` |

