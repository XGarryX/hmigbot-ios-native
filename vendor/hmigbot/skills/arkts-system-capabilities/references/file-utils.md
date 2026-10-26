# 文件操作指南

> @kit.CoreFileKit 文件读写的完整使用模式，替代 Android 的 java.io.File。

---

## 基本导入

```typescript
import { fileIo } from '@kit.CoreFileKit'
import { util } from '@kit.ArkTS'
```

---

## 沙箱路径

HarmonyOS 应用只能访问自己的沙箱目录：

```typescript
// 获取沙箱路径
const filesDir = context.filesDir       // 持久化存储目录
const cacheDir = context.cacheDir       // 缓存目录（系统可能自动清理）
const tempDir = context.tempDir         // 临时目录
```

**关键规则**：
- ✅ 只能使用 `context.filesDir`、`context.cacheDir`、`context.tempDir`
- ❌ 不能写入 `/storage/...` 等绝对路径（Permission denied）

---

## 文件读写

### 写入文件

```typescript
function writeFile(context: Context, fileName: string, content: string): void {
  const filePath = `${context.filesDir}/${fileName}`
  const file = fileIo.openSync(filePath, fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY)
  fileIo.writeSync(file.fd, content)
  fileIo.closeSync(file.fd)
}
```

### 读取文件

```typescript
function readFile(context: Context, fileName: string): string {
  const filePath = `${context.filesDir}/${fileName}`
  const file = fileIo.openSync(filePath, fileIo.OpenMode.READ_ONLY)
  const stat = fileIo.statSync(filePath)
  const buffer = new ArrayBuffer(stat.size)
  fileIo.readSync(file.fd, buffer)
  fileIo.closeSync(file.fd)

  const decoder = new util.TextDecoder('utf-8')
  return decoder.decodeWithStream(new Uint8Array(buffer))
}
```

### 检查文件是否存在

```typescript
function fileExists(path: string): boolean {
  try {
    fileIo.accessSync(path)
    return true
  } catch {
    return false
  }
}
```

### 创建目录

```typescript
function ensureDir(dirPath: string): void {
  try {
    fileIo.mkdirSync(dirPath, true)  // true = 递归创建
  } catch {
    // 目录已存在
  }
}
```

### 删除文件

```typescript
function deleteFile(path: string): void {
  try {
    fileIo.unlinkSync(path)
  } catch {
    // 文件不存在
  }
}
```

---

## 下载文件到沙箱

```typescript
import { http } from '@kit.NetworkKit'

async function downloadToSandbox(
  context: Context,
  url: string,
  fileName: string
): Promise<string> {
  const savePath = `${context.filesDir}/downloads`
  ensureDir(savePath)

  const filePath = `${savePath}/${fileName}`
  const httpRequest = http.createHttp()
  try {
    const response = await httpRequest.request(url, {
      method: http.RequestMethod.GET,
      expectDataType: http.HttpDataType.ARRAY_BUFFER
    })
    if (response.responseCode === 200) {
      const file = fileIo.openSync(filePath, fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY)
      fileIo.writeSync(file.fd, response.result as ArrayBuffer)
      fileIo.closeSync(file.fd)
    }
  } finally {
    httpRequest.destroy()
  }
  return filePath
}
```
