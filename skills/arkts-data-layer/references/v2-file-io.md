# ArkTS 文件读写（fileIo / @ohos.file.fs）

> 覆盖 SKILL.md description 声明的「文件读写」能力。**经 harmony-docs（快照 2026-05-24）核验**。
> 导入：`import { fileIo } from '@kit.CoreFileKit'`。⚠️ 不要用已废弃的小写 `@ohos.fileio`。
> 路径：**只能用应用沙箱路径**（`context.filesDir` / `cacheDir` / `tempDir`），不能用绝对路径。`fileIo.openSync(path, mode): File`、`closeSync` 必须配对。

## 1. 沙箱目录

```typescript
const ctx = this.getUIContext().getHostContext() as common.UIAbilityContext
const filesDir = ctx.filesDir   // 持久文件
const cacheDir = ctx.cacheDir   // 可被系统清理的缓存
const tempDir  = ctx.tempDir    // 临时文件
```

## 2. 整文件文本读写

```typescript
import { fileIo } from '@kit.CoreFileKit'

function writeText(path: string, content: string): void {
  const file = fileIo.openSync(path, fileIo.OpenMode.CREATE | fileIo.OpenMode.READ_WRITE | fileIo.OpenMode.TRUNC)
  try {
    fileIo.writeSync(file.fd, content)
  } finally {
    fileIo.closeSync(file)        // 必须关闭，放 finally
  }
}

// 读整文件文本（同步 / 异步均可）
const text: string = fileIo.readTextSync(path)         // 同步
const text2: string = await fileIo.readText(path)      // 异步 Promise
```

## 3. JSON 持久化到文件（常见模式）

```typescript
function saveJson<T>(path: string, data: T): void {
  writeText(path, JSON.stringify(data))
}
function loadJson<T>(path: string, fallback: T): T {
  if (!fileIo.accessSync(path)) return fallback        // 文件不存在
  try { return JSON.parse(fileIo.readTextSync(path)) as T } catch { return fallback }
}
```
> 小型结构化数据优先用 `preferences`（见 v2-network-service.md）/ `RdbStore`；fileIo 适合大文本 / 二进制 / 缓存文件 / 导入导出。

## 4. 二进制 / 大文件（按块读写，避免整文件入内存）

```typescript
// 写入 ArrayBuffer
const file = fileIo.openSync(path, fileIo.OpenMode.CREATE | fileIo.OpenMode.READ_WRITE)
try { fileIo.writeSync(file.fd, buffer) } finally { fileIo.closeSync(file) }

// 分块读
const f = fileIo.openSync(path, fileIo.OpenMode.READ_ONLY)
try {
  const buf = new ArrayBuffer(4096)
  let off = 0, len = 0
  while ((len = fileIo.readSync(f.fd, buf, { offset: off })) > 0) {
    // 处理 buf 前 len 字节
    off += len
  }
} finally { fileIo.closeSync(f) }
```

## 5. 目录与文件管理

```typescript
fileIo.accessSync(path)                 // 是否存在 → boolean
fileIo.mkdirSync(dirPath)               // 建目录（递归用 mkdirSync(path, true)）
const st = fileIo.statSync(path)        // st.size / st.isDirectory() / st.isFile()
fileIo.listFileSync(dirPath)            // 列目录 → string[]
fileIo.copyFileSync(src, dst)           // 复制
fileIo.moveFileSync(src, dst)           // 移动 / 重命名
fileIo.unlinkSync(path)                 // 删文件（删目录用 rmdirSync）
```

## 关键规则

- **沙箱路径**：所有路径基于 `context.filesDir/cacheDir/tempDir`，禁用绝对路径。
- **`closeSync` 配对**：`openSync` 拿到的 `File` 必须在 `finally` 里 `closeSync`，否则句柄泄漏。
- **OpenMode 组合**：写新文件用 `CREATE | READ_WRITE | TRUNC`；追加用 `CREATE | READ_WRITE | APPEND`；只读用 `READ_ONLY`。
- **选型**：键值/偏好 → `preferences`；结构化关系数据 → `RdbStore`；大文本/二进制/缓存/导入导出 → `fileIo`。
- **大文件下载落盘**：走 `request.agent`（见 `arkts-download-manager`），不要手撸 HTTP + fileIo。
