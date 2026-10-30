# 文件管线参考

> 文件移动管线、MIME 映射、URL 清洗、沙箱路径、fileIo 操作速查。

---

## 文件移动管线

request.agent 下载文件到 `cacheDir`，需要移到目标目录：

```typescript
import { fileIo } from '@kit.CoreFileKit';

private async finalizeDownload(
  itemId: number, fileName: string
): Promise<void> {
  // agent 下载到 cacheDir
  const filePath = GlobalState.cacheDir + '/' + fileName;

  try {
    // Step 1: 验证文件存在且有内容
    let finalSize: number = 0;
    try {
      const stat = fileIo.statSync(filePath);
      finalSize = stat.size;
    } catch (e) {
      await this.failDownload(itemId, 'File not found after download');
      return;
    }

    if (finalSize === 0) {
      await this.failDownload(itemId, 'Downloaded file is empty');
      return;
    }

    // Step 2-3: 移动到目标目录
    let finalPath = filePath;
    try {
      const dir = GlobalState.downloadDir;
      fileIo.mkdirSync(dir, true);  // 递归创建目标目录
      const destPath = dir + '/' + fileName;
      fileIo.moveFileSync(filePath, destPath);
      finalPath = destPath;
    } catch (moveErr) {
      // 移动失败则就地使用 cache 路径
      // 不中断流程 — 文件仍然可用
    }

    // Step 4: 更新数据库
    const media = await this.mediaDao.getFeedMediaByItemId(itemId);
    if (media !== null) {
      media.localFileUrl = finalPath;
      media.downloadDate = Date.now();
      media.size = finalSize;
      await this.mediaDao.setFeedMedia(media);
    }

    // Step 5: 通知 UI
    this.activeDownloads.delete(itemId);
    EventBus.getInstance().publish(EVENT_EPISODE_DOWNLOADED, logData);

  } catch (e) {
    await this.failDownload(itemId, JSON.stringify(e));
  }
}
```

---

## MIME 类型→扩展名映射

```typescript
private static getExtension(mimeType: string, url: string): string {
  const lower = mimeType.toLowerCase();

  // 按 MIME 类型匹配
  if (lower.indexOf('mp3') >= 0 || lower.indexOf('mpeg') >= 0) {
    return 'mp3';
  }
  if (lower.indexOf('video/mp4') >= 0) {
    return 'mp4';
  }
  if (lower.indexOf('mp4') >= 0 || lower.indexOf('m4a') >= 0) {
    return 'm4a';
  }
  if (lower.indexOf('ogg') >= 0) {
    return 'ogg';
  }
  if (lower.indexOf('opus') >= 0) {
    return 'opus';
  }
  if (lower.indexOf('aac') >= 0) {
    return 'aac';
  }

  // 从 URL 提取扩展名（去掉查询参数）
  const urlPath = url.split('?')[0];
  const lastDot = urlPath.lastIndexOf('.');
  if (lastDot >= 0) {
    const ext = urlPath.substring(lastDot + 1).toLowerCase();
    if (ext.length > 0 && ext.length <= 5) {
      return ext;
    }
  }

  // 默认 mp3
  return 'mp3';
}
```

---

## URL 清洗

RSS/XML 解析出的 URL 可能包含 HTML 实体编码：

```typescript
// RSS XML 中: <enclosure url="https://example.com/file?a=1&amp;b=2"/>
// 解析后得到: "https://example.com/file?a=1&amp;b=2"
// 实际需要:   "https://example.com/file?a=1&b=2"

const cleanUrl = downloadUrl.replace(/&amp;/g, '&');
```

**何时清洗**：在创建下载任务之前，对所有从 XML/RSS 解析出的 URL 执行清洗。

---

## 沙箱路径说明

HarmonyOS 应用只能访问沙箱目录：

| 路径 | 获取方式 | 用途 | 持久性 |
|------|---------|------|--------|
| `filesDir` | `context.filesDir` | 应用持久数据 | 卸载时删除 |
| `cacheDir` | `context.cacheDir` | 临时缓存 | 系统可清理 |
| `tempDir` | `context.tempDir` | 临时文件 | 随时清理 |

**request.agent 下载位置**：`cacheDir`（saveas 相对路径基于此）

**推荐下载文件最终位置**：`filesDir + '/downloads/'`

```typescript
// GlobalState 中初始化路径
static downloadDir: string = '';
static cacheDir: string = '';

static async init(context: Context): Promise<void> {
  GlobalState.downloadDir = context.filesDir + '/downloads';
  GlobalState.cacheDir = context.cacheDir;
}
```

---

## fileIo 常用操作速查

```typescript
import { fileIo } from '@kit.CoreFileKit';

// 检查文件是否存在
function fileExists(path: string): boolean {
  try {
    fileIo.statSync(path);
    return true;
  } catch (e) {
    return false;
  }
}

// 获取文件大小
function getFileSize(path: string): number {
  try {
    const stat = fileIo.statSync(path);
    return stat.size;
  } catch (e) {
    return 0;
  }
}

// 递归创建目录
fileIo.mkdirSync(dirPath, true);

// 移动文件
fileIo.moveFileSync(srcPath, destPath);

// 删除文件
fileIo.unlinkSync(filePath);

// 打开文件（用于 AVPlayer fd://）
const file = fileIo.openSync(filePath, fileIo.OpenMode.READ_ONLY);
const fd = file.fd;

// 关闭文件描述符
fileIo.closeSync(fd);

// 读取文本文件
const content = fileIo.readTextSync(filePath);

// 写入文本文件
const file = fileIo.openSync(filePath,
  fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY | fileIo.OpenMode.TRUNC);
fileIo.writeSync(file.fd, content);
fileIo.closeSync(file.fd);
```

---

## 删除不完整文件

下载失败时清理不完整的文件：

```typescript
private async removeIncompleteFile(destPath: string): Promise<void> {
  try {
    fileIo.statSync(destPath);  // 检查是否存在
    fileIo.unlinkSync(destPath);  // 删除
  } catch (e) {
    // 文件不存在，无需删除
  }
}
```
