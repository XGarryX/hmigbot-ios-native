# 国际化避坑指南（V2）

> 常见国际化错误与正确做法对照表。**本项目锁 V2**：所有代码示例使用 `@ComponentV2 / @Local / @ObservedV2 / @Trace / AppStorageV2`。i18n API（`resourceManager` / `$r()` 等）与装饰器版本无关。
>
> V1 老项目兼容写法见 [`v1-compat.md`](./v1-compat.md)。

---

## ⚠️ 文档说明

- ✅ **已验证项**：基于代码仓实际使用或官方文档
- ⚠️ **未验证项**：需要查证官方文档确认
- 💡 **建议**：使用前查阅 https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/i18n-overview-V5

---

## 目录命名错误

### 错误 vs 正确

| 错误写法 | 正确写法 | 说明 |
|---------|---------|------|
| `chinese` | `zh` | 使用 ISO 639-1 |
| `china` | `zh_CN` | 使用 ISO 639-1 + ISO 3166-1 |
| `Chinese` | `zh-Hans` | 小写，或带区域码 |
| `zh-CN` | `zh_CN` | 下划线而非连字符（部分版本接受连字符） |
| `en-uk` | `en_GB` | 英国英文用 `en_GB` |

### 完整语言代码参考

| 语言 | 代码 | 区域变体 |
|------|------|---------|
| 中文 | `zh` | `zh_CN`, `zh_HK`, `zh_TW`, `zh_Hans`, `zh_Hant` |
| 英文 | `en` | `en_US`, `en_GB`, `en_AU`, `en_CA` |
| 日文 | `ja` | - |
| 韩文 | `ko` | - |
| 德文 | `de` | `de_DE`, `de_AT`, `de_CH` |
| 法文 | `fr` | `fr_FR`, `fr_CA`, `fr_CH` |
| 西班牙文 | `es` | `es_ES`, `es_MX`, `es_AR` |
| 葡萄牙文 | `pt` | `pt_BR`, `pt_PT` |
| 俄文 | `ru` | - |
| 阿拉伯文 | `ar` | - |

---

## string.json 格式错误

### 错误 1：value 使用错误引号

```json
// 错误 — value 被双引号包裹
{
  "string": [
    { "name": "app_name", "value": "\"图库\"" }
  ]
}

// 正确 — value 直接是字符串
{
  "string": [
    { "name": "app_name", "value": "图库" }
  ]
}
```

### 错误 2：缺少必要字段

```json
// 错误 — 缺少 name 或 value
{
  "string": [
    { "value": "图库" },
    { "name": "app_name" }
  ]
}

// 正确
{
  "string": [
    { "name": "app_name", "value": "图库" }
  ]
}
```

### 错误 3：JSON 语法错误

```json
// 错误 — 尾随逗号
{
  "string": [
    { "name": "a", "value": "A" },
    { "name": "b", "value": "B" },  // ← 尾随逗号
  ]
}

// 正确
{
  "string": [
    { "name": "a", "value": "A" },
    { "name": "b", "value": "B" }
  ]
}
```

---

## 硬编码字符串

### 错误 vs 正确

| 错误写法 | 正确写法 |
|---------|---------|
| `Text('确认')` | `Text($r('app.string.confirm'))` |
| `Button('取消')` | `Button($r('app.string.cancel'))` |
| `'共 ' + count + ' 个文件'` | `$r('app.string.file_count', count)` |
| `promptAction.showToast('操作成功')` | `promptAction.showToast($r('app.string.success'))` |

### 容易硬编码的地方

1. **Button 文字**
2. **Dialog 标题和内容**
3. **Toast 消息**
4. **Placeholder 文案**
5. **Error 消息**
6. **Menu 项**
7. **Tab 标签**

---

## 动态切换不生效

### 原因 1：未声明 supportedLanguages

```json5
// module.json5
{
  "module": {
    "supportedLanguages": ["zh", "en", "ja"]  // ← 必须声明
  }
}
```

### 原因 2：UI 未触发重建

```typescript
// 错误 — 切换后 UI 不更新
async switchLanguage(lang: string) {
  await resMgr.setPreferredLanguage([lang])
  // 直接返回，UI 不会更新
}

// 正确 — 触发状态更新
async switchLanguage(lang: string) {
  await resMgr.setPreferredLanguage([lang])
  this.refreshKey++  // 触发重建
  this.currentLang = lang
}
```

### 原因 3：组件未持有响应式 locale 状态

```typescript
// 错误 — 组件不响应状态变化
@Entry
@ComponentV2
struct Page {
  build() {
    Column() {
      Text($r('app.string.hello'))  // 不会自动更新
    }
  }
}

// 正确 — 使用 @Local + LocaleModel 包装
@ObservedV2
class LocaleModel {
  @Trace currentLanguage: string = 'zh'
  @Trace refreshKey: number = 0
}

@Entry
@ComponentV2
struct Page {
  @Local locale: LocaleModel = AppStorageV2.connect(
    LocaleModel, 'locale', () => new LocaleModel()
  )!

  build() {
    Column() {
      Text($r('app.string.hello'))
        .id('page_' + this.locale.refreshKey)  // refreshKey 改即重建
    }
  }
}
```

> V2 关键点：`@Local` 持有 `@ObservedV2` 实例 → 实例的 `@Trace` 字段变化自动刷新该组件。无需 V1 的 `@StorageLink('refreshKey')` 单字段绑定。

---

## 图片国际化问题

### 错误：文件名不一致

```
base/media/
└── logo.png      ✓

en/media/
└── logo_en.png  ✗ 应该是 logo.png

ja/media/
└── logo_jp.png  ✗ 应该是 logo.png
```

### 正确做法

```
base/media/
└── logo.png      ✓

en/media/
└── logo.png      ✓（同名文件，内容不同）

ja/media/
└── logo.png      ✓（同名文件，内容不同）
```

---

## 插值参数使用错误

> ⚠️ **验证状态**：`IntlString.format()` API 需要查证官方文档
> 
> **推荐方案**：使用字符串模板 ` \`...${variable}...\` ` 或 `resourceManager.getStringByName()`

### 错误 1：参数顺序错误

```typescript
// string.json: { "name": "info", "value": "文件：%s，大小：%s" }

// ⚠️ 以下 API 需要查证 - IntlString.format 可能不存在
// 错误 — 参数顺序颠倒
// IntlString.format($r('app.string.info'), size, name)

// ✅ 推荐 — 使用字符串模板
const name = 'photo.jpg'
const size = '1.5MB'
const message = `文件：${name}，大小：${size}`

// ⚠️ 或者 — 如果 resourceManager 支持参数
// resourceManager.getStringByName('info', name, size)
```

### 错误 2：参数类型不匹配

```typescript
// string.json: { "name": "count", "value": "数量：%d" }

// ⚠️ 以下 API 需要查证
// 错误 — 传字符串
// IntlString.format($r('app.string.count'), '10')

// ✅ 推荐 — 使用字符串模板
const count = 10
const message = `数量：${count}`
```

### 错误 3：参数数量不匹配

```typescript
// string.json: { "name": "info", "value": "%s 大小：%s" }

// ⚠️ 以下 API 需要查证
// 错误 — 只传一个参数
// IntlString.format($r('app.string.info'), name)

// ✅ 推荐 — 使用字符串模板
const name = 'file.txt'
const size = '2KB'
const message = `${name} 大小：${size}`
```

---

## RTL 语言注意事项

阿拉伯文、希伯来文等 RTL（从右到左）语言需要额外处理：

### 1. 布局适配

```typescript
// 检测 RTL
import { i18n } from '@kit.LocalizationKit'

const isRTL = i18n.isRTL()
```

### 2. 布局方向

```typescript
Column() {
  // RTL 语言下自动反转
}
.layoutDirection(isRTL ? LayoutDirection.RTL : LayoutDirection.LTR)
```

### 3. 图片翻转

```typescript
Image($r('app.media.arrow'))
  .rotate({ angle: isRTL ? 180 : 0 })  // 箭头方向需反转
```

---

## module.json5 supportedLanguages 陷阱

### 问题：声明了但不生效

```json5
// module.json5
{
  "module": {
    "supportedLanguages": ["zh", "en"]
  }
}
```

可能原因：
1. **语言代码不匹配**：`"zh-Hans"` vs `"zh"`
2. **应用未重启**：切换语言后需要重启应用
3. **资源文件缺失**：声明了但对应目录不存在

### 正确声明

```json5
{
  "module": {
    "supportedLanguages": [
      "zh",        // 中文（默认）
      "zh-Hans",   // 简体中文（API 12+）
      "zh-Hant",   // 繁体中文（API 12+）
      "en",        // 英文
      "ja"         // 日文
    ]
  }
}
```

---

## 调试技巧

### 1. 打印当前语言

```typescript
import { resourceManager } from '@kit.LocalizationKit'

const langs = await context.resourceManager.getPreferredLanguage()
hilog.info(0x0000, 'I18N', 'Current language: %{public}s', langs[0])
```

### 2. 检查资源是否加载

```typescript
const resMgr = context.resourceManager
const str = await resMgr.getStringByName('app_name')
hilog.info(0x0000, 'I18N', 'String value: %{public}s', str)
```

### 3. 检查资源目录是否存在

```typescript
// 在 DevEco Studio 中
// File > Project Structure > Module > Resources
// 查看 supportedLanguages 是否与实际目录匹配
```

---

## 错误代码速查

| 错误现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 切换语言后 UI 不更新 | 未触发重建 | 增加 `@Local refreshKey` 或 `@ObservedV2 LocaleModel` 的 `@Trace refreshKey` 字段并改变 ID |
| `$r()` 引用报错 | string.json 中 key 不存在 | 检查 key 拼写 |
| setPreferredLanguage 不生效 | 未声明 supportedLanguages | 在 module.json5 中声明 |
| 英文资源不加载 | 目录名错误 | 使用 `en` 而非 `en_US` |
| 日文显示乱码 | 文件编码错误 | 确保文件是 UTF-8 编码 |
| 图片不切换 | 文件名不一致 | 不同语言目录图片文件名相同 |
