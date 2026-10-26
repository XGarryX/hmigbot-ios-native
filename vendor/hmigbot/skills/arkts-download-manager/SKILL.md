---
name: arkts-download-manager
description: 生成 ArkTS/HarmonyOS 文件下载代码。当用户需要实现大文件下载（request.agent）、下载进度追踪、下载队列管理、暂停/取消/删除下载、断点续传、下载文件的存储与移动（cacheDir→沙箱目录）时触发。即使只说"下载个文件""怎么显示下载进度"也应触发。不适用于流媒体边下边播（用 arkts-media-playback / arkts-video-playback）。
metadata:
  type: domain
  domain: media
  tags:
  - download
  - request-agent
  - file-storage
---
# ArkTS Download Manager — 文件下载生成器

## API 版本

本 skill 基于 **API 12+**（HarmonyOS 5.0.0+）。相关导入：

- 下载：`import { request } from '@kit.BasicServicesKit'`
- 文件：`import { fileIo } from '@kit.CoreFileKit'`
- 小文件 HTTP：`import { http } from '@kit.NetworkKit'`

遇到版本兼容性或其他不确定的 ArkTS 知识点，参阅 arkts-knowledge-verifier skill。

---

## API 选型决策树

```
文件下载用哪个 API？
│
├─ 文件 ≤ 5MB 且不需要进度回调
│   └─ http.request() + expectDataType: ARRAY_BUFFER
│       ✓ 简单快速
│       ⚠️ 约 5MB 限制（错误码 2300023）
│
├─ 文件 > 5MB
│   └─ 必须用 request.agent ✓
│
├─ 需要进度回调
│   └─ request.agent (gauge: true) ✓
│
├─ 需要后台下载
│   └─ request.agent + Mode.BACKGROUND ✓
│
└─ http.requestInStream()
    ❌ 不推荐 — dataEnd 事件在实际设备上不触发
    ❌ Promise 在收到响应头后即 resolve，不等数据完成
    ❌ 不要用于文件下载
```

> 详细对比见 `references/request-agent-patterns.md`

---

## request.agent.Config 速查

5 个必填字段：

```typescript
import { request } from '@kit.BasicServicesKit';

const config: request.agent.Config = {
  action: request.agent.Action.DOWNLOAD,  // 下载动作
  url: cleanUrl,                          // 下载 URL
  overwrite: true,                        // 覆盖已存在文件
  saveas: './' + fileName,                // 相对于 cacheDir 的保存路径
  mode: request.agent.Mode.FOREGROUND,    // 前台模式
  gauge: true                             // 启用进度回调
};

const task = await request.agent.create(context, config);
```

**注意**：`saveas` 路径是相对于应用 `cacheDir` 的相对路径，不是绝对路径。

---

## Progress 回调模式

```typescript
task.on('progress', (progress: request.agent.Progress) => {
  if (progress.sizes.length >= 2) {
    const received = progress.sizes[0];  // 已接收字节数
    const total = progress.sizes[1];     // 总字节数
    if (total > 0) {
      const percent = Math.floor(received * 100 / total);
      // 发布进度事件
      EventBus.getInstance().publish(EVENT_DOWNLOAD_PROGRESS,
        new DownloadProgressData(itemId, percent));
    }
  }
});

task.on('completed', (progress: request.agent.Progress) => {
  // 下载完成 → 执行文件移动管线
  this.finalizeDownload(itemId, fileName);
});

task.on('failed', (progress: request.agent.Progress) => {
  // 下载失败 → 清理 + 通知
  this.failDownload(itemId, errorCode, 'Download failed');
});

await task.start();  // 启动下载
```

---

## 文件移动管线

`request.agent` 下载到 `cacheDir`，通常需要移到目标目录：

```
cacheDir/file.mp3
    ↓ (1) statSync 验证文件存在且 > 0 字节
    ↓ (2) mkdirSync(targetDir, true) 递归创建目标目录
    ↓ (3) moveFileSync(cachePath, destPath) 移动文件
    ↓ (4) 更新数据库记录
    ↓ (5) EventBus.publish 通知 UI
```

```typescript
private async finalizeDownload(itemId: number, fileName: string): Promise<void> {
  const filePath = GlobalState.cacheDir + '/' + fileName;

  // 1. 验证文件
  let finalSize: number = 0;
  try {
    const stat = fileIo.statSync(filePath);
    finalSize = stat.size;
  } catch (e) {
    await this.failDownload(itemId, ERROR_NOT_FOUND, 'File not found');
    return;
  }
  if (finalSize === 0) {
    await this.failDownload(itemId, ERROR_EMPTY, 'Empty file');
    return;
  }

  // 2-3. 移动文件
  let finalPath = filePath;
  try {
    const dir = GlobalState.downloadDir;
    fileIo.mkdirSync(dir, true);  // 递归创建
    const destPath = dir + '/' + fileName;
    fileIo.moveFileSync(filePath, destPath);
    finalPath = destPath;
  } catch (moveErr) {
    // 移动失败则就地使用 cache 路径
  }

  // 4. 更新数据库
  const media = await this.mediaDao.getFeedMediaByItemId(itemId);
  if (media !== null) {
    media.localFileUrl = finalPath;
    media.downloadDate = Date.now();
    media.size = finalSize;
    await this.mediaDao.setFeedMedia(media);
  }

  // 5. 通知
  EventBus.getInstance().publish(EVENT_EPISODE_DOWNLOADED, logData);
}
```

> 完整代码见 `references/file-pipeline.md`

---

## 取消和删除

### 取消进行中的下载

```typescript
cancelDownload(itemId: number): void {
  const task = this.activeTasks.get(itemId);
  if (task !== undefined) {
    task.stop();  // 停止下载任务
    this.activeTasks.delete(itemId);
  }
  this.activeDownloads.delete(itemId);
}
```

### 删除已下载文件

```typescript
async deleteDownload(itemId: number): Promise<void> {
  const media = await this.mediaDao.getFeedMediaByItemId(itemId);
  if (media !== null && media.localFileUrl.length > 0) {
    try {
      fileIo.unlinkSync(media.localFileUrl);  // 删除文件
    } catch (e) { /* 文件不存在 */ }
    media.localFileUrl = '';
    media.downloadDate = 0;
    await this.mediaDao.setFeedMedia(media);
  }
}
```

---

## 下载去重

使用 `Set<number>` 防止同一文件重复下载：

```typescript
private activeDownloads: Set<number> = new Set();
private activeTasks: Map<number, request.agent.Task> = new Map();

async downloadFile(itemId: number, url: string): Promise<void> {
  if (this.activeDownloads.has(itemId)) {
    return;  // 已在下载中
  }
  this.activeDownloads.add(itemId);
  // ... 开始下载
}
```

---

## URL 清洗

RSS/XML 中的 URL 可能包含 HTML 实体编码：

```typescript
// RSS 中的 URL: https://example.com/file?a=1&amp;b=2
// 实际需要:     https://example.com/file?a=1&b=2
const cleanUrl = downloadUrl.replace(/&amp;/g, '&');
```

---

## 常见错误

### 1. 用 http.request() 下载大文件
```typescript
// ❌ 约 5MB 限制，报错 2300023
const resp = await httpRequest.request(url, {
  expectDataType: http.HttpDataType.ARRAY_BUFFER
});

// ✓ 使用 request.agent
const task = await request.agent.create(context, config);
```

### 2. 使用 requestInStream
```typescript
// ❌ dataEnd 事件不可靠，下载卡住
httpRequest.on('dataEnd', () => { /* 可能永远不触发 */ });
await httpRequest.requestInStream(url, options);

// ✓ 使用 request.agent
```

### 3. URL 中 &amp; 未解码
```typescript
// ❌ HTTP 400 错误
const url = 'https://example.com?a=1&amp;b=2';

// ✓ 先解码
const cleanUrl = url.replace(/&amp;/g, '&');
```

### 4. moveFileSync 前未创建目录
```typescript
// ❌ 报 13900002 ENOENT
fileIo.moveFileSync(src, '/path/to/new/dir/file.mp3');

// ✓ 先创建目录
fileIo.mkdirSync('/path/to/new/dir', true);
fileIo.moveFileSync(src, '/path/to/new/dir/file.mp3');
```

### 5. 下载完不验证文件
```typescript
// ❌ 可能是空文件或不完整
this.updateDB(itemId, filePath);

// ✓ 先验证
const stat = fileIo.statSync(filePath);
if (stat.size === 0) { /* 失败处理 */ }
```

---

## 生成检查清单

- [ ] 大文件使用 `request.agent`（不用 `http.request`）
- [ ] 没有使用 `requestInStream`
- [ ] URL 已做 `&amp;` → `&` 解码
- [ ] `saveas` 使用相对路径（相对于 cacheDir）
- [ ] `gauge: true` 启用进度回调
- [ ] 下载完成后验证文件大小
- [ ] 移动文件前创建目标目录 `mkdirSync(dir, true)`
- [ ] 使用 Set 去重防止重复下载
- [ ] 没有使用 `any` 类型
- [ ] 导入使用 `@kit.*` 格式

---

## 跨 Skill 协作

| 需要什么 | 读取哪里 |
|---------|---------|
| 媒体播放（下载后播放） | `arkts-media-playback/SKILL.md` |
| 数据库存储（下载记录） | `arkts-data-layer/references/rdbstore-dao-patterns.md` |
| 系统能力（文件/权限） | `arkts-system-capabilities/SKILL.md` |
| UI 组件（进度显示） | `arkts-component-builder/SKILL.md` |
| 验证 API 兼容性 | `arkts-knowledge-verifier/SKILL.md` |

> 完整路由矩阵见 `arkts-knowledge-verifier/references/skill-routing-guide.md`

---

## References

- `references/request-agent-patterns.md` — request.agent 完整代码模板 + http 对比 + 错误码 + 取消/删除 — 写下载 task 生命周期/取消删除时读
- `references/file-pipeline.md` — 文件移动管线 + MIME 映射 + URL 清洗 + 沙箱路径 — 需要文件移动/MIME 映射代码时读
- 遇到版本兼容性或其他不确定的 ArkTS 知识点，参阅 **arkts-knowledge-verifier** skill
