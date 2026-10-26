# 动态语言切换实现（V2）

> 完整的运行时语言切换代码模板，包括状态管理和 UI 刷新。**本项目锁 V2**：组件用 `@ComponentV2`，本地状态用 `@Local`，全局 locale / refreshKey 用 `@ObservedV2 LocaleModel + AppStorageV2.connect`。i18n API 与装饰器版本无关。
>
> V1 老项目（`@Component / @State / @StorageLink`）查阅请见 [`v1-compat.md`](./v1-compat.md)。

---

## ⚠️ API 验证状态

| API | 状态 | 说明 |
|-----|------|------|
| `resourceManager.setPreferredLanguage()` | ⚠️ 未验证 | 需查官方文档确认 API 存在性 |
| `resourceManager.getPreferredLanguage()` | ⚠️ 未验证 | 需查官方文档确认 API 存在性 |
| V2 `@Local` / `AppStorageV2.connect` 触发 UI 刷新 | ✅ 已验证 | ArkTS V2 标准机制（API 12+） |
| `onLanguageConfigurationUpdate()` | ⚠️ 未验证 | 需确认生命周期回调是否正确 |

> **建议**：使用前请查阅官方文档
> - resourceManager API：https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/js-apis-resource-manager-V5
> - 如 API 不存在，可使用应用内状态管理替代

---

## 基本实现模式

### 简单实现（单页面，V2）

```typescript
import { resourceManager } from '@kit.LocalizationKit'
import { common } from '@kit.AbilityKit'
import { hilog } from '@kit.PerformanceAnalysisKit'

const DOMAIN = 0x0001
const TAG = 'I18nDemo'

@Entry
@ComponentV2
struct LanguageSwitchDemo {
  private context = getContext(this) as common.UIAbilityContext
  @Local private currentLanguage: string = 'zh'
  @Local private refreshKey: number = 0

  aboutToAppear(): void {
    this.loadCurrentLanguage()
  }

  async loadCurrentLanguage(): Promise<void> {
    try {
      const resMgr = this.context.resourceManager
      const langs = await resMgr.getPreferredLanguage()
      this.currentLanguage = langs[0] || 'zh'
      hilog.info(DOMAIN, TAG, `Current language: ${this.currentLanguage}`)
    } catch (e) {
      hilog.error(DOMAIN, TAG, `Failed to get language: ${e.message}`)
    }
  }

  async switchLanguage(lang: string): Promise<void> {
    try {
      hilog.info(DOMAIN, TAG, `Switching to: ${lang}`)

      const resMgr = this.context.resourceManager
      await resMgr.setPreferredLanguage([lang])

      this.currentLanguage = lang
      this.refreshKey++

      hilog.info(DOMAIN, TAG, `Language switched to: ${lang}`)
    } catch (e) {
      hilog.error(DOMAIN, TAG, `Failed to switch language: ${e.message}`)
    }
  }

  build() {
    Column({ space: 20 }) {
      Text($r('app.string.app_name'))
        .fontSize(24)
        .fontWeight(FontWeight.Bold)

      Text($r('app.string.welcome'))
        .fontSize(16)

      Text($r('app.string.settings_language'))
        .fontSize(14)
        .fontColor('#666666')

      Row({ space: 12 }) {
        Button('中文')
          .onClick(() => this.switchLanguage('zh'))
          .backgroundColor(this.currentLanguage === 'zh' ? '#007AFF' : '#CCCCCC')

        Button('English')
          .onClick(() => this.switchLanguage('en'))
          .backgroundColor(this.currentLanguage === 'en' ? '#007AFF' : '#CCCCCC')

        Button('日本語')
          .onClick(() => this.switchLanguage('ja'))
          .backgroundColor(this.currentLanguage === 'ja' ? '#007AFF' : '#CCCCCC')
      }

      Text(`Current: ${this.currentLanguage}`)
        .fontSize(12)
        .fontColor('#999999')
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .id('lang_container_' + this.refreshKey)
  }
}
```

---

## 完整实现（设置页面 + 全局状态，V2）

### 1. 全局 LocaleModel（@ObservedV2 + AppStorageV2）

V2 推荐**单一 `@ObservedV2` 类封装所有 locale 相关全局状态**，避免 V1 散落的 `@StorageLink('currentLanguage')` / `@StorageLink('languageRefreshKey')` 多 key 写法（拼写易错、无类型保护）。

```typescript
// common/LocaleModel.ets
import { resourceManager } from '@kit.LocalizationKit'
import { common } from '@kit.AbilityKit'
import { AppStorageV2 } from '@kit.ArkUI'
import { hilog } from '@kit.PerformanceAnalysisKit'

const DOMAIN = 0x0000
const TAG = 'LocaleModel'

@ObservedV2
export class LocaleModel {
  @Trace currentLanguage: string = 'zh'
  @Trace refreshKey: number = 0

  async init(context: common.UIAbilityContext): Promise<void> {
    try {
      const resMgr = context.resourceManager
      const langs = await resMgr.getPreferredLanguage()
      this.currentLanguage = langs[0] || 'zh'
    } catch (e) {
      this.currentLanguage = 'zh'
    }
  }

  async setLanguage(context: common.UIAbilityContext, lang: string): Promise<void> {
    try {
      const resMgr = context.resourceManager
      await resMgr.setPreferredLanguage([lang])
      this.currentLanguage = lang
      this.refreshKey++  // @Trace 字段变化 → 所有 connect 同 key 的组件自动刷新
    } catch (e) {
      hilog.error(DOMAIN, TAG, `Failed to set language: ${e.message}`)
    }
  }
}

// 全局单例（推荐在 EntryAbility.onCreate 中预热一次；任何位置 connect 同 key 都返回同一实例）
export const localeStore = AppStorageV2.connect(
  LocaleModel,
  'locale',
  () => new LocaleModel()
)!
```

### 2. 设置页面（V2）

```typescript
// pages/SettingsPage.ets
import { LocaleModel, localeStore } from '../common/LocaleModel'
import { common } from '@kit.AbilityKit'

@Entry
@ComponentV2
struct SettingsPage {
  @Local locale: LocaleModel = AppStorageV2.connect(
    LocaleModel,
    'locale',
    () => new LocaleModel()
  )!

  @Builder
  LanguageItem(lang: string, label: string) {
    Row() {
      Text(label)
        .fontSize(16)

      if (this.locale.currentLanguage === lang) {
        Text('✓')
          .fontSize(16)
          .fontColor('#007AFF')
      }
    }
    .width('100%')
    .padding(16)
    .backgroundColor(this.locale.currentLanguage === lang ? '#F0F8FF' : '#FFFFFF')
    .onClick(() => {
      const context = getContext(this) as common.UIAbilityContext
      this.locale.setLanguage(context, lang)
    })
  }

  build() {
    Column() {
      Text($r('app.string.settings_title'))
        .fontSize(20)
        .fontWeight(FontWeight.Bold)
        .padding(16)

      List() {
        ListItem() {
          this.LanguageItem('zh', '简体中文')
        }

        ListItem() {
          this.LanguageItem('zh-Hans', '简体中文 (简体)')
        }

        ListItem() {
          this.LanguageItem('zh-Hant', '繁体中文 (繁体)')
        }

        ListItem() {
          this.LanguageItem('en', 'English')
        }

        ListItem() {
          this.LanguageItem('ja', '日本語')
        }
      }
    }
    .width('100%')
    .height('100%')
    .id('settings_' + this.locale.refreshKey)
  }
}
```

---

## 语言切换后刷新页面的方法（V2）

### 方法 1：@Local refreshKey + ID 变化

```typescript
@Local private refreshKey: number = 0

async switchLanguage(lang: string) {
  await resourceManager.setPreferredLanguage([lang])
  this.refreshKey++
}

build() {
  Column() {
    Text($r('app.string.hello'))
  }
  .id('page_' + this.refreshKey)  // ID 变化触发重建
}
```

### 方法 2：router.replaceUrl 重新加载

```typescript
import { router } from '@kit.ArkUI'

async switchLanguage(lang: string) {
  await resourceManager.setPreferredLanguage([lang])
  router.replaceUrl({ url: 'pages/SettingsPage' })
}
```

### 方法 3：Navigation 模式（V2）

```typescript
@Local private navPathStack: NavPathStack = new NavPathStack()
@Local private refreshKey: number = 0

build() {
  Navigation(this.navPathStack) {
    // 内容
  }
  .id('nav_' + this.refreshKey)
}
```

### 方法 4：@Monitor 触发副作用（V2 新增）

```typescript
@ComponentV2
struct PageWithMonitor {
  @Local locale: LocaleModel = AppStorageV2.connect(
    LocaleModel, 'locale', () => new LocaleModel()
  )!

  @Monitor('locale.currentLanguage')
  onLanguageChange(monitor: IMonitor): void {
    // currentLanguage 改变时执行副作用：埋点、缓存清理等
    console.info('Language changed to:', this.locale.currentLanguage)
  }

  build() {
    Text($r('app.string.hello'))
      .id('page_' + this.locale.refreshKey)
  }
}
```

---

## 获取支持的语言列表

```typescript
import { resourceManager } from '@kit.LocalizationKit'

interface LanguageInfo {
  language: string   // 如 'zh'
  region?: string    // 如 'CN'
  displayName: string // 如 '简体中文'
}

async function getSupportedLanguages(): Promise<LanguageInfo[]> {
  // 这是一个示例，实际 API 可能不同
  const supported = ['zh', 'zh-Hans', 'zh-Hant', 'en', 'ja', 'ko']
  const displayNames: Record<string, string> = {
    'zh': '中文',
    'zh-Hans': '简体中文',
    'zh-Hant': '繁体中文',
    'en': 'English',
    'ja': '日本語',
    'ko': '한국어'
  }

  return supported.map(lang => ({
    language: lang,
    displayName: displayNames[lang] || lang
  }))
}
```

---

## 监听系统语言变化（V2）

### 在 UIAbility 中处理（写入 AppStorageV2）

```typescript
// EntryAbility.ets
import { AbilityConstant, ConfigurationConstant, UIAbility, Want } from '@kit.AbilityKit'
import { hilog } from '@kit.PerformanceAnalysisKit'
import { AppStorageV2 } from '@kit.ArkUI'
import { LocaleModel } from '../common/LocaleModel'

export default class EntryAbility extends UIAbility {
  onLanguageConfigurationUpdate(): void {
    hilog.info(0x0000, 'EntryAbility', 'System language configuration updated')

    // 1. 拿到全局 LocaleModel（与组件 connect 同一实例）
    const locale = AppStorageV2.connect(
      LocaleModel,
      'locale',
      () => new LocaleModel()
    )!

    // 2. 重新获取当前语言
    this.context.resourceManager.getPreferredLanguage().then((langs: string[]) => {
      locale.currentLanguage = langs[0] || 'zh'
      locale.refreshKey++   // 通知所有页面刷新
    })
  }

  onConfigurationUpdate(configuration: AbilityConstant.Configuration): void {
    hilog.info(0x0000, 'EntryAbility', 'Configuration updated: %{public}s',
      JSON.stringify(configuration))

    if (configuration.language !== undefined) {
      hilog.info(0x0000, 'EntryAbility', `Language changed to: ${configuration.language}`)
    }
  }
}
```

---

## 完整页面刷新机制（V2）

```typescript
// 确保语言切换后所有页面都刷新的完整 V2 模式

// 1. 全局 LocaleModel
@ObservedV2
class LocaleModel {
  @Trace currentLanguage: string = 'zh'
  @Trace refreshKey: number = 0

  async switchLanguage(context: common.UIAbilityContext, lang: string): Promise<void> {
    // 1. 切换语言
    const resMgr = context.resourceManager
    await resMgr.setPreferredLanguage([lang])

    // 2. 更新状态：所有 connect 'locale' 的组件 @Trace 字段变化即刷新
    this.currentLanguage = lang
    this.refreshKey++
  }
}

// 2. 任意页面用 @Local + AppStorageV2.connect 引用单例
@Entry
@ComponentV2
struct AnyPage {
  @Local locale: LocaleModel = AppStorageV2.connect(
    LocaleModel, 'locale', () => new LocaleModel()
  )!

  build() {
    Column() {
      Text($r('app.string.any_string'))
        .fontSize(16)
    }
    .id('page_' + this.locale.refreshKey)
  }
}
```

---

## 注意事项

1. **语言代码大小写**：`zh-Hans` vs `zh-hans` — 必须完全匹配
2. **切换后需要时间生效**：异步操作，避免连续快速切换
3. **并非所有页面都需要重建**：只有持有 `LocaleModel`（`@Local locale = AppStorageV2.connect(LocaleModel, 'locale', ...)`）并在 `build()` 中读取 `locale.refreshKey` 的组件才会重建
4. **性能考虑**：避免高频调用，建议在语言切换按钮上做防抖
5. **V1/V2 不混用**：同一 struct 内不要混用 `@State` 和 `@Local`，会编译报错

---

## 持久化用户语言偏好（V2 推荐 PersistenceV2）

V1 用 `PersistentStorage.persistProp('currentLanguage', 'zh')` + `@StorageLink`；V2 一站式：

```typescript
// common/LocaleModel.ets
@ObservedV2
export class LocaleModel {
  @Trace currentLanguage: string = 'zh'
  @Trace refreshKey: number = 0
}

// 在任意位置 connect（自动持久化到磁盘 + UI 响应式）
@ComponentV2
struct App {
  @Local locale: LocaleModel = PersistenceV2.globalConnect({
    type: LocaleModel,
    key: 'app_locale',
    defaultCreator: () => new LocaleModel()
  })!

  build() {
    Column() {
      Text(`当前: ${this.locale.currentLanguage}`)
      Button('切换 EN').onClick(() => {
        this.locale.currentLanguage = 'en'   // 自动落盘 + 触发所有引用刷新
      })
    }
  }
}
```

---

## 如果 setPreferredLanguage API 不存在的替代方案

> ⚠️ 如果官方 API 确认不存在 `setPreferredLanguage()`，可以使用以下替代方案

### 方案 1：应用内状态管理（V2 推荐）

```typescript
// common/LocaleModel.ets — V2 写法（同上）
@ObservedV2
export class LocaleModel {
  @Trace currentLanguage: string = 'zh'
  @Trace refreshKey: number = 0

  setLanguage(lang: string): void {
    this.currentLanguage = lang
    this.refreshKey++
  }
}
```

**使用方式**：

```typescript
// 页面中使用
@Entry
@ComponentV2
struct SettingsPage {
  @Local locale: LocaleModel = AppStorageV2.connect(
    LocaleModel, 'locale', () => new LocaleModel()
  )!

  build() {
    Column() {
      Button('中文')
        .onClick(() => {
          this.locale.setLanguage('zh')
          // UI 会自动刷新，因为 @Local 持有 @ObservedV2 实例的 @Trace 属性
        })

      Button('English')
        .onClick(() => {
          this.locale.setLanguage('en')
        })

      Text($r('app.string.welcome'))
    }
    .id('page_' + this.locale.refreshKey)
  }
}
```

**优点**：
- ✅ 不依赖未知 API
- ✅ 完全可控
- ✅ 即时生效
- ✅ V2 类型安全（@Trace 属性强类型，不再有 string key 拼写错误）

**缺点**：
- ⚠️ 仅应用内生效，不影响系统语言
- ⚠️ 需要手动维护语言状态

---

### 方案 2：引导用户到系统设置

```typescript
import { common, Want } from '@kit.AbilityKit'
import { promptAction } from '@kit.ArkUI'

async function openSystemLanguageSettings(): Promise<void> {
  try {
    const context = getContext(this) as common.UIAbilityContext
    const want: Want = {
      action: 'action.settings.language',
    }

    context.startAbility(want)
      .then(() => {
        hilog.info(DOMAIN, TAG, 'Opened language settings')
      })
      .catch((err: Error) => {
        promptAction.showToast({ message: '无法打开设置' })
      })
  } catch (err) {
    promptAction.showToast({ message: '打开设置失败' })
  }
}
```

**使用场景**：
- 当无法动态切换时
- 用户需要永久修改系统语言

---

### 方案 3：重启应用应用语言

```typescript
import { common } from '@kit.AbilityKit'
import { process } from '@kit.BasicServicesKit'

function restartApp(): void {
  const context = getContext(this) as common.UIAbilityContext
  // ⚠️ 需要查证：HarmonyOS 是否支持应用重启
  // Android: Process.killProcess(Process.myPid())
  // HarmonyOS: 可能需要使用 context.terminateSelf() 然后重新启动
  context.terminateSelf()
}
```

> ⚠️ **注意**：此方案需要查证 HarmonyOS 是否支持应用自重启

---

### 最佳实践推荐

1. **优先尝试官方 API**：查证 `setPreferredLanguage()` 是否存在
2. **方案 1 作为备选**：V2 LocaleModel + AppStorageV2 / PersistenceV2 是通用解决方案
3. **方案 2 作为兜底**：引导用户到系统设置
4. **避免方案 3**：重启应用体验较差

---

## V1 → V2 迁移速查（仅本文涉及部分）

| V1 | V2 | 备注 |
|---|---|---|
| `@Component` | `@ComponentV2` | struct 装饰器 |
| `@State refreshKey: number = 0` | `@Local refreshKey: number = 0` | 必须初始化 |
| `@StorageLink('currentLanguage') lang: string = 'zh'` | `@Local locale: LocaleModel = AppStorageV2.connect(LocaleModel, 'locale', () => new LocaleModel())!` 然后 `this.locale.currentLanguage` | 先抽 @ObservedV2 类 |
| `AppStorage.setOrCreate('refreshKey', n+1)` | `localeStore.refreshKey++` | 直接改 @Trace 字段 |
| `PersistentStorage.persistProp('lang', 'zh')` | `PersistenceV2.globalConnect({ type: LocaleModel, key, defaultCreator })` | V2 一站式 |
| `@Watch('lang') onLangChange()` | `@Monitor('lang') onLangChange(m: IMonitor)` | 方法装饰器 + IMonitor |

> V1 老项目兼容写法见 [`v1-compat.md`](./v1-compat.md)。
