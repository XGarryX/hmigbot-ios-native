# 分享面板 ShareKit

> 使用 `@kit.ShareKit` 拉起系统分享面板，替代 Android 的 `Intent.ACTION_SEND`。

---

## 基本导入

```typescript
import { systemShare } from '@kit.ShareKit'
import { uniformTypeDescriptor as utd } from '@kit.ArkData'
import { common } from '@kit.AbilityKit'
```

---

## 完整调用模板

```typescript
async function shareMedia(
  context: common.UIAbilityContext,
  uri: string,
  title: string,
  mimeType: string
): Promise<void> {
  // 1. 求该文件自己的 UTD 类型 ID（按后缀推断，不要硬塞 belongsTo）
  const ext = uri.substring(uri.lastIndexOf('.') + 1).toLowerCase()
  const utdTypeId = utd.getUniformDataTypeByFilenameExtension('.' + ext)

  // 2. 构建分享数据
  const shareData: systemShare.SharedData = new systemShare.SharedData({
    utd: utdTypeId,
    uri: uri,
    title: title,
    description: '分享 ' + title
  })

  // 3. 创建分享控制器
  const controller: systemShare.ShareController = new systemShare.ShareController(shareData)

  // 4. 展示分享面板
  controller.show(context, {
    selectionMode: systemShare.SelectionMode.SINGLE,
    previewMode: systemShare.SharePreviewMode.DETAIL
  }).then(() => {
    hilog.info(DOMAIN, TAG, 'ShareController show success')
  }).catch((error: BusinessError) => {
    hilog.error(DOMAIN, TAG, `ShareController show error: ${error.code}, ${error.message}`)
    promptAction.showToast({ message: '分享失败' })
  })
}
```

---

## MIME 类型判断

```typescript
private getMimeType(medium: Medium): string {
  if ((medium.type & TYPE_VIDEOS) !== 0) {
    return 'video/*'
  }
  if ((medium.type & TYPE_IMAGES) !== 0) {
    return 'image/*'
  }
  return '*/*'
}
```

---

## SharePreviewMode 配置

| 模式 | 效果 |
|------|------|
| `DETAIL` | 显示详情预览（推荐） |
| `NONE` | 不显示预览 |

## SelectionMode 配置

`SelectionMode` 只有两个成员（`@kit.ShareKit`，编译校验过）。**没有 `MULTIPLE`**——写 `SelectionMode.MULTIPLE` 会编译失败：`Property 'MULTIPLE' does not exist on type 'typeof SelectionMode'`。

| 模式 | 值 | 效果 |
|------|----|------|
| `SINGLE` | 0 | 单选模式：传入多条记录时，用户多选一进行分享（缺省值） |
| `BATCH` | 1 | 批量模式：分享全部数据记录 |

> 一次分享多条记录、想让目标应用收到全部记录时，用 `selectionMode: systemShare.SelectionMode.BATCH`。
> ⚠️ BATCH 批量模式只支持文件类型记录（每条 `SharedRecord` 走 `uri` 的 File 类型）；混入纯文本/链接等非文件记录会触发错误码 `1003702001`。

---

## module.json5 配置

### 配置规则

| 分享内容类型 | 是否需要配置 | 说明 |
|------------|------------|------|
| 图片/视频/文件 | 通常不需要 | 系统已内置支持 |
| 纯文本 | 需要配置 | 需声明 `ohos.want.action.send` |
| 自定义数据 | 需要配置 | 需声明 `ohos.want.action.send` |

### 配置示例（纯文本/自定义数据）

```json5
{
  "skills": [{
    "entities": ["entity.system.home"],
    "actions": [
      "ohos.want.action.home",
      "ohos.want.action.send"    // 发送数据
    ]
  }]
}
```

> ⚠️ **注意**：虽然图片/视频分享通常不需要额外声明，但某些设备可能需要。如遇分享失败，建议添加 `ohos.want.action.send` 配置。

---

## 常见错误

### 错误 1：不转换 UTD 直接传 MIME

```typescript
// 错误 — 部分设备不支持
const shareData = new systemShare.SharedData({
  mimeType: 'image/*',  // ❌
  uri: uri,
  title: title
})

// 正确 — 使用 UTD（按后缀推断，不传 belongsTo）
const utdTypeId = utd.getUniformDataTypeByFilenameExtension('.' + ext)
const shareData = new systemShare.SharedData({
  utd: utdTypeId,
  uri: uri,
  title: title
})
```

### 错误 2：show() 后不 await

`controller.show()` 是异步的，但不会阻塞 UI。不需要 await，但错误需要通过 catch 处理。

### 错误 3：给每个文件的 `getUniformDataTypeByFilenameExtension` 硬塞第二参 IMAGE

签名是 `getUniformDataTypeByFilenameExtension(filenameExtension: string, belongsTo?: string): string`——**第二参 `belongsTo` 可选**（归属类型 ID，无默认值）。按后缀推断类型时**只传后缀、不传第二参**；否则给 `.pdf` 也塞 `utd.UniformDataType.IMAGE` 会把它误标成图片。

```typescript
// 错误 — 所有扩展名都硬塞 IMAGE，.pdf / .txt 被误标
const t = utd.getUniformDataTypeByFilenameExtension('.' + ext, utd.UniformDataType.IMAGE)  // ❌

// 正确 A — 按后缀推断：只传一个后缀实参
const t = utd.getUniformDataTypeByFilenameExtension('.' + ext)

// 正确 B — 类型已知时直接用字面 UTD 枚举（更精准，无需查后缀）
const t = utd.UniformDataType.PNG        // 或 JPEG / PDF / IMAGE / TEXT / PLAIN_TEXT ...
```

> `SharedRecord` 用 `utd`（string）承载类型、`uri` 承载文件位置、文本/链接用 `content`；**没有 `mimeType` 字段**。`content` 与 `uri` 至少一个非空。

### 多条记录批量分享

一个 `SharedData` 至少含一条记录。多条时：用首条 `new systemShare.SharedData(firstRecord)`，其余用实例方法 `sharedData.addRecord(record)` 逐条追加——**构造器只收单条 `SharedRecord`，不能把数组塞进构造器，也不要为每个文件各建一个 `SharedData`/`ShareController`**。每条记录的 `utd` 按它自己的扩展名求得。

```typescript
const shareData = new systemShare.SharedData(records[0])
for (let i = 1; i < records.length; i++) {
  shareData.addRecord(records[i])
}
const controller = new systemShare.ShareController(shareData)
controller.show(context, {
  selectionMode: systemShare.SelectionMode.BATCH,   // 全部记录一起分享
  previewMode: systemShare.SharePreviewMode.DETAIL
}).then(() => {}).catch((e: BusinessError) => {})
```
