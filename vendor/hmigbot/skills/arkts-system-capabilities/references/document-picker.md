# 文件管理器 DocumentViewPicker

> 使用 `@kit.CoreFileKit` 的 `picker` 模块拉起系统文件管理器，替代 Android 的 `Intent.ACTION_OPEN_DOCUMENT` 和 `Intent.ACTION_CREATE_DOCUMENT`。

---

## 基本导入

```typescript
import { picker } from '@kit.CoreFileKit';
import { common } from '@kit.AbilityKit';
```

---

## 唤起文件管理器（选择文件）

> 对应 Android：`Intent.ACTION_OPEN_DOCUMENT`

### 基础用法

```typescript
function openFileManager(context: common.UIAbilityContext): void {
  const docPicker = new picker.DocumentViewPicker(context);
  const selectOptions = new picker.DocumentSelectOptions();

  docPicker.select(selectOptions)
    .then((uris: Array<string>) => {
      hilog.info(DOMAIN, TAG, `Selected files: ${uris.length}`);
      // uris 是用户选择的文件 URI 数组
      uris.forEach(uri => {
        hilog.info(DOMAIN, TAG, `Selected URI: ${uri}`);
      });
    })
    .catch((err: Error) => {
      hilog.error(DOMAIN, TAG, `Failed to open file manager: ${err.message}`);
    });
}
```

### 限定文件后缀

```typescript
function openFileManagerWithFilter(context: common.UIAbilityContext): void {
  const docPicker = new picker.DocumentViewPicker(context);
  const selectOptions = new picker.DocumentSelectOptions();

  // 仅允许选择特定后缀的文件
  selectOptions.fileSuffixFilters = ['.txt', '.pdf', '.epub', '.mht'];

  docPicker.select(selectOptions)
    .then((uris: Array<string>) => {
      if (uris.length > 0) {
        hilog.info(DOMAIN, TAG, `Selected: ${uris[0]}`);
      }
    })
    .catch((err: Error) => {
      hilog.error(DOMAIN, TAG, `Select error: ${err.message}`);
    });
}
```

---

## 唤起文件管理器（保存文件）

> 对应 Android：`Intent.ACTION_CREATE_DOCUMENT`

### 基础用法

```typescript
function saveFileToDownloads(context: common.UIAbilityContext, fileName: string, content: string): void {
  const docPicker = new picker.DocumentViewPicker(context);
  const saveOptions = new picker.DocumentSaveOptions();

  // 设置默认文件名
  saveOptions.newFileNames = [fileName];
  // 限定可保存的文件后缀
  saveOptions.fileSuffixChoices = ['.txt', '.mht', '.html'];

  docPicker.save(saveOptions)
    .then((uris: Array<string>) => {
      if (uris.length > 0) {
        hilog.info(DOMAIN, TAG, `File saved to: ${uris[0]}`);
        // 通过 URI 写入文件内容（需配合 fileIo）
      }
    })
    .catch((err: Error) => {
      hilog.error(DOMAIN, TAG, `Save cancelled or failed: ${err.message}`);
    });
}
```

### 完整示例：保存网页为 MHT

```typescript
import { picker } from '@kit.CoreFileKit';
import { fileIo } from '@kit.CoreFileKit';
import { common } from '@kit.AbilityKit';

function saveWebPage(context: common.UIAbilityContext, title: string, content: string): void {
  const docPicker = new picker.DocumentViewPicker(context);
  const saveOptions = new picker.DocumentSaveOptions();

  // 清理文件名中的非法字符
  let fileName = title || 'page';
  if (fileName.length > 50) {
    fileName = fileName.substring(0, 50);
  }
  fileName = fileName.replace(/[\\/:*?"<>|]/g, '_');

  saveOptions.newFileNames = [fileName + '.mht'];
  saveOptions.fileSuffixChoices = ['MHT|.mht'];

  docPicker.save(saveOptions)
    .then((uris: Array<string>) => {
      if (uris.length > 0) {
        hilog.info(DOMAIN, TAG, `Saved to: ${uris[0]}`);
        // 写入文件内容
        try {
          const file = fileIo.openSync(uris[0], fileIo.OpenMode.WRITE_ONLY | fileIo.OpenMode.CREATE);
          fileIo.writeSync(file.fd, content);
          fileIo.closeSync(file.fd);
          hilog.info(DOMAIN, TAG, 'File content written successfully');
        } catch (writeErr) {
          hilog.error(DOMAIN, TAG, `Write file error: ${writeErr.message}`);
        }
      }
    })
    .catch((err: Error) => {
      hilog.info(DOMAIN, TAG, `Save cancelled: ${err.message}`);
    });
}
```

---

## DocumentSelectOptions 配置项

| 属性 | 类型 | 说明 |
|------|------|------|
| `fileSuffixFilters` | `string[]` | 限定可选择的文件后缀，如 `['.txt', '.pdf']` |
| `subFuzzingNumber` | `number` | 子目录搜索深度，默认 0（仅当前目录） |

---

## DocumentSaveOptions 配置项

| 属性 | 类型 | 说明 |
|------|------|------|
| `newFileNames` | `string[]` | 默认文件名数组（第一个为默认名） |
| `fileSuffixChoices` | `string[]` | 允许保存的文件后缀列表，格式如 `'MHT|.mht'` 或 `'.mht'` |

---

## DocumentViewPicker 其他方法

| 方法 | 用途 | 对应 Android |
|------|------|-------------|
| `.select(options)` | 选择文件（可多选） | `ACTION_OPEN_DOCUMENT` |
| `.save(options)` | 保存文件 | `ACTION_CREATE_DOCUMENT` |

---

## module.json5 配置

> ⚠️ **重要**：`DocumentViewPicker` 是系统内置 picker，通常**不需要**额外配置 module.json5。

以下情况可能需要配置：
- 应用需要作为文件提供者响应其他应用的文件请求
- 需要声明特定的 file 类型支持

```json5
{
  "skills": [{
    "entities": ["entity.system.home"],
    "actions": [
      "ohos.want.action.home"
    ]
  }]
}
```

---

## 常见错误

### 错误 1：选择文件后未正确处理 URI

```typescript
// 错误 — 直接使用 URI 访问文件
const data = fileIo.readFileSync(uri);  // ❌ 不支持直接路径

// 正确 — 使用 fileIo.openSync 获取 fd
const file = fileIo.openSync(uri, fileIo.OpenMode.READ_ONLY);
const data = fileIo.readSync(file.fd);
fileIo.closeSync(file.fd);
```

### 错误 2：保存文件时文件名包含非法字符

```typescript
// 错误 — Windows 文件名不允许以下字符
saveOptions.newFileNames = ['file:name?.mht'];

// 正确 — 替换非法字符
let safeName = fileName.replace(/[\\/:*?"<>|]/g, '_');
saveOptions.newFileNames = [safeName + '.mht'];
```

### 错误 3：save() 的 Promise 被静默取消

```typescript
// 错误 — 用户取消时可能静默失败
docPicker.save(saveOptions)
  .then((uris) => {
    if (uris.length > 0) { /* 保存成功 */ }
    // ⚠️ 用户取消时 uris 为空数组，但没有提示
  });

// 正确 — 用 finally 或区分处理
docPicker.save(saveOptions)
  .then((uris) => {
    if (uris.length > 0) {
      hilog.info(DOMAIN, TAG, 'Save success');
    }
  })
  .catch((err) => {
    hilog.error(DOMAIN, TAG, 'Save failed');
  })
  .finally(() => {
    // 用户取消也会走到这里
    hilog.info(DOMAIN, TAG, 'Save dialog closed');
  });
```

---

## 与 cameraPicker 的对比

| 维度 | DocumentViewPicker（本节） | cameraPicker |
|------|--------------------------|--------------|
| 所属 Kit | `@kit.CoreFileKit` | `@kit.CameraKit` |
| 功能 | 选择/保存文件 | 拍照/录像 |
| 返回 | `Promise<Array<string>>`（URI 数组） | `Promise<PickerResult>` |
| module.json5 配置 | 通常不需要 | 需要 `entity.system.camera` |
