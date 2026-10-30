# request.agent 下载模式参考

> request.agent.Config 完整字段、下载流程、进度回调、取消删除、API 对比。

---

## http.request vs requestInStream vs request.agent 对比

| 特性 | http.request | requestInStream | request.agent |
|------|-------------|-----------------|---------------|
| 文件大小限制 | ~5MB | 理论无限 | 无限制 |
| 进度回调 | ❌ 无 | ⚠️ 不可靠 | ✓ 稳定 |
| 后台下载 | ❌ | ❌ | ✓ Mode.BACKGROUND |
| 断点续传 | ❌ | ❌ | ✓ 系统管理 |
| 稳定性 | ✓ | ❌ dataEnd 不触发 | ✓ |
| 适用场景 | 小文件/JSON/API | 不推荐使用 | **所有文件下载** |

**结论**：文件下载统一使用 `request.agent`。

---

## request.agent.Config 字段详解

```typescript
const config: request.agent.Config = {
  // 必填字段
  action: request.agent.Action.DOWNLOAD,  // DOWNLOAD 或 UPLOAD
  url: 'https://example.com/file.mp3',    // 下载 URL

  // 推荐字段
  overwrite: true,                        // 覆盖已存在的同名文件
  saveas: './episode_123.mp3',            // 保存路径（相对于 cacheDir）
  mode: request.agent.Mode.FOREGROUND,    // FOREGROUND 或 BACKGROUND
  gauge: true,                            // true=启用进度回调

  // 可选字段
  method: 'GET',                          // HTTP 方法（默认 GET）
  headers: new Map(),                     // 自定义请求头
  retry: true,                            // 是否自动重试
  redirect: true,                         // 是否跟随重定向
};
```

### mode 选项

| Mode | 说明 | 适用场景 |
|------|------|---------|
| `FOREGROUND` | 前台下载，应用退到后台可能中断 | 用户主动触发的下载 |
| `BACKGROUND` | 后台下载，应用退出也继续 | 大文件、批量下载 |

### gauge 选项

- `true`：启用 progress 回调，可获取下载进度
- `false`：不回调进度，减少开销

---

## 完整下载流程代码

```typescript
import { request } from '@kit.BasicServicesKit';
import { fileIo } from '@kit.CoreFileKit';

export class DownloadManager {
  private activeDownloads: Set<number> = new Set();
  private activeTasks: Map<number, request.agent.Task> = new Map();

  async downloadFile(
    itemId: number, downloadUrl: string, mimeType: string
  ): Promise<void> {
    // 去重检查
    if (this.activeDownloads.has(itemId)) {
      return;
    }

    // URL 清洗：&amp; → &
    const cleanUrl = downloadUrl.replace(/&amp;/g, '&');

    // 确定文件名
    const ext = this.getExtension(mimeType, downloadUrl);
    const fileName = 'episode_' + itemId.toString() + '.' + ext;

    this.activeDownloads.add(itemId);

    try {
      const context = GlobalState.getContext();

      // 配置下载任务
      const agentConfig: request.agent.Config = {
        action: request.agent.Action.DOWNLOAD,
        url: cleanUrl,
        overwrite: true,
        method: 'GET',
        saveas: './' + fileName,
        mode: request.agent.Mode.FOREGROUND,
        gauge: true
      };

      // 创建任务
      const task = await request.agent.create(context, agentConfig);
      this.activeTasks.set(itemId, task);

      // 进度回调
      task.on('progress', (progress: request.agent.Progress) => {
        if (progress.sizes.length >= 2) {
          const received = progress.sizes[0];
          const total = progress.sizes[1];
          if (total > 0) {
            const percent = Math.floor(received * 100 / total);
            // 发布进度事件
          }
        }
      });

      // 完成回调
      task.on('completed', (progress: request.agent.Progress) => {
        this.activeTasks.delete(itemId);
        this.finalizeDownload(itemId, fileName);
      });

      // 失败回调
      task.on('failed', (progress: request.agent.Progress) => {
        this.activeTasks.delete(itemId);
        this.failDownload(itemId, 'Download failed');
      });

      // 启动下载
      await task.start();

    } catch (e) {
      this.activeTasks.delete(itemId);
      this.activeDownloads.delete(itemId);
    }
  }

  // 取消下载
  cancelDownload(itemId: number): void {
    const task = this.activeTasks.get(itemId);
    if (task !== undefined) {
      task.stop().catch(() => {});
      this.activeTasks.delete(itemId);
    }
    this.activeDownloads.delete(itemId);
  }

  // 删除已下载文件
  async deleteDownload(itemId: number, filePath: string): Promise<void> {
    try {
      fileIo.unlinkSync(filePath);
    } catch (e) { /* 文件可能不存在 */ }
    // 更新数据库...
  }

  // 检查是否正在下载
  isDownloading(itemId: number): boolean {
    return this.activeDownloads.has(itemId);
  }
}
```

---

## 错误码参考

| 错误码 | 含义 | 解决方案 |
|-------|------|---------|
| 2300023 | 文件大小超限（http.request） | 改用 request.agent |
| 13900002 | ENOENT 路径不存在 | mkdirSync(dir, true) |
| 401/403 | 未授权 | 检查 URL 权限 |
| 网络错误 | 连接失败 | 检查网络 + 重试 |

---

## 下载状态管理

```typescript
// 下载状态枚举
const DOWNLOAD_STATUS_IDLE: number = 0;
const DOWNLOAD_STATUS_DOWNLOADING: number = 1;
const DOWNLOAD_STATUS_COMPLETED: number = 2;
const DOWNLOAD_STATUS_FAILED: number = 3;

// 事件数据类
class DownloadProgressData {
  itemId: number = 0;
  percent: number = 0;
  constructor(itemId: number, percent: number) {
    this.itemId = itemId;
    this.percent = percent;
  }
}

class DownloadFailedData {
  itemId: number = 0;
  errorCode: number = 0;
  constructor(itemId: number, errorCode: number) {
    this.itemId = itemId;
    this.errorCode = errorCode;
  }
}
```
