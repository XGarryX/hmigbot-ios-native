# 浏览器/URL 跳转

> 使用 `Want` + `startAbility` 拉起系统浏览器或其他应用，替代 Android 的 `Intent.ACTION_VIEW`。

---

## 基本导入

```typescript
import { common, Want } from '@kit.AbilityKit'
```

---

## 拉起浏览器打开 URL

> ✅ **验证状态**：已在 AboutPage.ets 中验证（网页和邮件跳转）

```typescript
function openBrowser(context: common.UIAbilityContext, url: string): void {
  const want: Want = {
    action: 'ohos.want.action.viewData',
    uri: url
  }

  context.startAbility(want)
    .then(() => {
      hilog.info(DOMAIN, TAG, `Opened browser to ${url}`)
    })
    .catch((err: Error) => {
      hilog.error(DOMAIN, TAG, `Failed to open browser: ${err.message}`)
    })
}
```

---

## 常见 URL 协议

| 协议 | 用途 | 示例 | 验证状态 |
|------|------|------|---------|
| `https://` | 网页 | `openBrowser(ctx, 'https://example.com')` | ✅ 已验证 |
| `http://` | 网页 | `openBrowser(ctx, 'http://example.com')` | ✅ 已验证 |
| `mailto:` | 邮件 | `openBrowser(ctx, 'mailto:hello@example.com')` | ✅ 已验证 |
| `tel:` | 电话 | **电话拨号不属 URL 跳转** → 见 `references/telephony-dial.md`（用 `call.makeCall`）；**不要**用 `openBrowser` / `viewData`+`tel:` | — |

---

## 发送邮件（带主题）

```typescript
function sendEmail(context: common.UIAbilityContext, to: string, subject: string): void {
  const want: Want = {
    action: 'ohos.want.action.viewData',
    uri: `mailto:${to}?subject=${encodeURIComponent(subject)}`
  }

  context.startAbility(want).catch((err: Error) => {
    hilog.error(DOMAIN, TAG, `Failed to send email: ${err.message}`)
  })
}
```

---

## 其他常见 Want Action

| Action | 用途 |
|--------|------|
| `ohos.want.action.viewData` | 浏览器/数据查看 |
| `ohos.want.action.send` | 发送数据 |
| `ohos.want.action.edit` | 编辑数据 |
| `ohos.want.action.pick` | 选择数据 |

---

## module.json5 配置

### Action 区别说明

| Action | 用途 | 是否需要配置 |
|--------|------|------------|
| `ohos.want.action.viewData` | 拉起浏览器查看数据 | 通常不需要（系统内置） |
| `ohos.want.action.view` | 响应外部应用的查看请求 | 需要配置（如相册响应外部查看图片） |

### 配置示例

```json5
{
  "skills": [{
    "entities": ["entity.system.home"],
    "actions": [
      "ohos.want.action.home",
      "ohos.want.action.view"   // 响应外部查看请求（如其他应用查看图片）
    ]
  }]
}
```

> ⚠️ **重要**：
> - 使用 `ohos.want.action.viewData` **主动拉起**浏览器时，通常无需配置
> - 配置 `ohos.want.action.view` 是为了**被动响应**其他应用的查看请求
> - 相册应用需要配置 `ohos.want.action.view` 以响应外部查看图片/视频的请求

---

## 常见错误

### 错误 1：URL 包含特殊字符未编码

```typescript
// 错误 — 主题包含空格和特殊字符
uri: 'mailto:hello@example.com?subject=Hello World'

// 正确 — URL 编码
uri: 'mailto:hello@example.com?subject=' + encodeURIComponent('Hello World')
```

### 错误 2：startAbility 返回的 Promise 未处理

`startAbility` 可能抛出异常（如应用不存在），必须 catch 处理。
