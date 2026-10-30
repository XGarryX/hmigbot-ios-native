# V1 兼容写法参考（仅老项目查阅）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Component / @State / @StorageLink / @Prop / @Watch` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`SKILL.md`](../SKILL.md)、[`dynamic-language-switch.md`](./dynamic-language-switch.md)、[`code-examples.md`](./code-examples.md)（已升级 V2）。
>
> i18n 相关 API（`resourceManager` / `intl` / `$r('app.string.xxx')` / `setPreferredLanguage` / `getPreferredLanguage` / `onLanguageConfigurationUpdate`）在 V1/V2 之间**完全不变**，本文仅记录"持有 locale / refreshKey 状态"的 V1 装饰器写法。

---

## V1 / V2 速查（仅 i18n 相关）

| V1 | V2 |
|---|---|
| `@Component` | `@ComponentV2` |
| `@State refreshKey: number = 0` | `@Local refreshKey: number = 0` |
| `@StorageLink('currentLanguage') lang: string = 'zh'` | 先定义 `@ObservedV2 LocaleModel`，然后 `@Local locale = AppStorageV2.connect(LocaleModel, 'locale', () => new LocaleModel())!`，访问 `this.locale.currentLanguage` |
| `@StorageLink('languageRefreshKey') key: number = 0` | 同上，访问 `this.locale.refreshKey` |
| `@Prop currentColumns: number = 3` | `@Param @Once currentColumns: number = 3`（只读） |
| `@Prop currentColumns: number = 3`（子可改本地副本） | `@Param currentColumns: number = 3`（不带 @Once） |
| `@Watch('lang') onLangChange()` | `@Monitor('lang') onLangChange(m: IMonitor)` |
| `AppStorage.setOrCreate('refreshKey', n)` | `localeStore.refreshKey = n`（直接改 @Trace 字段） |
| `PersistentStorage.persistProp('currentLanguage', 'zh')` | `PersistenceV2.globalConnect({ type: LocaleModel, key: 'locale', defaultCreator: () => new LocaleModel() })` |

---

## V1 简单实现（单页面语言切换）

```typescript
import { resourceManager } from '@kit.LocalizationKit'
import { common } from '@kit.AbilityKit'

@Entry
@Component
struct LanguageSwitchDemoV1 {
  private context = getContext(this) as common.UIAbilityContext
  @State private currentLanguage: string = 'zh'
  @State private refreshKey: number = 0

  async switchLanguage(lang: string): Promise<void> {
    const resMgr = this.context.resourceManager
    await resMgr.setPreferredLanguage([lang])
    this.currentLanguage = lang
    this.refreshKey++
  }

  build() {
    Column() {
      Text($r('app.string.welcome'))
      Button('English').onClick(() => this.switchLanguage('en'))
    }
    .id('lang_' + this.refreshKey)
  }
}
```

**升级到 V2**（参考 [`dynamic-language-switch.md`](./dynamic-language-switch.md) 的"基本实现"）：
- `@Component` → `@ComponentV2`
- `@State` → `@Local`
- 其他 API 调用不变

---

## V1 全局状态共享（@StorageLink 多 key 写法）

```typescript
// V1：散落的 key（拼写易错、无类型保护）
class LanguageStateV1 {
  @StorageLink('currentLanguage') currentLanguage: string = 'zh'
  @StorageLink('languageRefreshKey') refreshKey: number = 0

  async setLanguage(context: common.UIAbilityContext, lang: string): Promise<void> {
    const resMgr = context.resourceManager
    await resMgr.setPreferredLanguage([lang])
    this.currentLanguage = lang
    this.refreshKey++
  }
}

// V1 设置页面
@Entry
@Component
struct SettingsPageV1 {
  @StorageLink('currentLanguage') currentLanguage: string = 'zh'
  @StorageLink('languageRefreshKey') refreshKey: number = 0

  build() {
    Column() {
      Text(`Current: ${this.currentLanguage}`)
    }
    .id('settings_' + this.refreshKey)
  }
}

// V1 任意页面
@Entry
@Component
struct AnyPageV1 {
  @StorageLink('languageRefreshKey') refreshKey: number = 0

  build() {
    Column() {
      Text($r('app.string.any_string'))
    }
    .id('page_' + this.refreshKey)
  }
}
```

**问题**：
- key 拼写错误（如 `'lanugageRefreshKey'`）静默失效
- 无类型保护（值是 Object）
- 字段加减需改多处

**V2 重构**（推荐，见 [`dynamic-language-switch.md`](./dynamic-language-switch.md) 的"全局 LocaleModel"段）：
- 单一 `@ObservedV2 LocaleModel` 封装所有 locale 状态
- 任意组件 `@Local locale = AppStorageV2.connect(LocaleModel, 'locale', () => new LocaleModel())!`
- 访问 `this.locale.currentLanguage` / `this.locale.refreshKey`
- 编译期类型检查 + IDE 重命名安全

---

## V1 子组件接收只读 Prop

```typescript
@Component
export struct ColumnsDialogV1 {
  @Prop currentColumns: number = 3        // V1：单向只读（API 12+ 必须初始化）

  build() {
    Text(`Columns: ${this.currentColumns}`)
  }
}
```

**V2 等价写法**（见 [`code-examples.md`](./code-examples.md) 的 V2 ColumnsDialog）：

```typescript
@ComponentV2
export struct ColumnsDialog {
  @Param @Once currentColumns: number = 3  // V2：单向只读（编译期检查）

  build() {
    Text(`Columns: ${this.currentColumns}`)
  }
}
```

---

## V1 监听语言变化（@Watch）

```typescript
@Component
struct PageV1 {
  @StorageLink('currentLanguage') @Watch('onLangChange') currentLanguage: string = 'zh'

  onLangChange(propName: string): void {
    console.info(`Language changed: ${this.currentLanguage}`)
    // 副作用：埋点、清缓存等
  }

  build() { Column() { Text($r('app.string.hello')) } }
}
```

**V2 等价**：

```typescript
@ComponentV2
struct Page {
  @Local locale: LocaleModel = AppStorageV2.connect(
    LocaleModel, 'locale', () => new LocaleModel()
  )!

  @Monitor('locale.currentLanguage')
  onLangChange(monitor: IMonitor): void {
    console.info(`Language changed: ${this.locale.currentLanguage}`)
    // 副作用
  }

  build() { Column() { Text($r('app.string.hello')) } }
}
```

---

## V1 持久化语言偏好（PersistentStorage.persistProp）

```typescript
// V1：双层模式（AppStorage + Preferences）
PersistentStorage.persistProp('currentLanguage', 'zh')

@Component
struct PageV1 {
  @StorageLink('currentLanguage') currentLanguage: string = 'zh'
  // 修改 currentLanguage 自动落盘 + UI 刷新
}
```

**V2 等价**（一站式）：

```typescript
@ObservedV2
class LocaleModel {
  @Trace currentLanguage: string = 'zh'
}

@ComponentV2
struct Page {
  @Local locale: LocaleModel = PersistenceV2.globalConnect({
    type: LocaleModel,
    key: 'app_locale',
    defaultCreator: () => new LocaleModel()
  })!
  // 修改 this.locale.currentLanguage 自动落盘 + UI 刷新（无需双层）
}
```

---

## V1 → V2 迁移建议

1. **先升级 SKILL.md / 主参考的代码模板**（已完成 — 见本目录其他文件）
2. **逐文件迁移老代码**：从最常用的 LanguageSettings / Settings 页面开始
3. **抽取 LocaleModel**：把所有 `@StorageLink('currentLanguage' | 'languageRefreshKey' | ...)` 整合到一个 `@ObservedV2 LocaleModel` 类
4. **替换装饰器**：
   - `@Component` → `@ComponentV2`
   - `@State` → `@Local`
   - `@StorageLink('xxx') xxx: T = default` → `@Local locale: LocaleModel = AppStorageV2.connect(LocaleModel, 'locale', () => new LocaleModel())!`，访问 `this.locale.xxx`
   - `@Prop` → `@Param @Once`（只读）/ `@Param`（可改本地副本）
   - `@Watch` → `@Monitor`
   - `PersistentStorage.persistProp` → `PersistenceV2.globalConnect`
5. **同 struct 内不混用 V1/V2 装饰器**（编译报错）

---

## 跨文档参考

- [`SKILL.md`](../SKILL.md) — V2 优先决策树与陷阱
- [`dynamic-language-switch.md`](./dynamic-language-switch.md) — V2 完整动态切换模板
- [`code-examples.md`](./code-examples.md) — V2 ColumnsDialog 实战示例
- [`common-pitfalls.md`](./common-pitfalls.md) — V2 i18n 避坑
- 跨 skill：[`arkts-state-manager/SKILL.md`](../../arkts-state-manager/SKILL.md) — V2 状态装饰器全集
- 跨 skill：[`arkts-state-manager/references/v2-decorators.md`](../../arkts-state-manager/references/v2-decorators.md) — @Local / @Param / @Event / @ObservedV2 / @Trace / @Monitor / @Computed / AppStorageV2 / PersistenceV2 完整语法（无 LocalStorageV2）
