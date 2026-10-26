# 下载 API 选型参考

> http.request vs requestInStream vs request.agent 详细对比。

---

## 对比表

| 特性 | http.request | requestInStream | request.agent |
|------|-------------|-----------------|---------------|
| 文件大小限制 | ~5MB | 理论无限 | 无限制 |
| 进度回调 | ❌ | ⚠️ 不可靠 | ✓ 稳定 |
| 后台下载 | ❌ | ❌ | ✓ |
| 断点续传 | ❌ | ❌ | ✓ |
| 稳定性 | ✓ | ❌ | ✓ |
| 适用场景 | 小文件/API | 不推荐 | **所有文件下载** |

---

## 错误码

| 错误码 | 含义 | 解决方案 |
|-------|------|---------|
| 2300023 | 文件大小超限（http.request ARRAY_BUFFER） | 改用 request.agent |
| 13900002 | ENOENT 路径不存在 | mkdirSync(dir, true) |
| 401/403 | 未授权/禁止 | 检查 URL 权限 |

---

## request.agent.Config 速查

```typescript
import { request } from '@kit.BasicServicesKit';

const config: request.agent.Config = {
  action: request.agent.Action.DOWNLOAD,
  url: cleanUrl,
  overwrite: true,
  saveas: './' + fileName,  // 相对于 cacheDir
  mode: request.agent.Mode.FOREGROUND,
  gauge: true
};
const task = await request.agent.create(context, config);
task.on('progress', (p: request.agent.Progress) => {
  const percent = Math.floor(p.sizes[0] * 100 / p.sizes[1]);
});
task.on('completed', () => { /* 完成 */ });
task.on('failed', () => { /* 失败 */ });
await task.start();
```

---

## 从 http.request 迁移到 request.agent

```typescript
// 旧方案（有 5MB 限制）
const httpReq = http.createHttp();
try {
  const resp = await httpReq.request(url, {
    method: http.RequestMethod.GET,
    expectDataType: http.HttpDataType.ARRAY_BUFFER
  });
  // 写入文件...
} finally {
  httpReq.destroy();
}

// 新方案（无限制）
const config: request.agent.Config = {
  action: request.agent.Action.DOWNLOAD,
  url: url,
  saveas: './' + fileName,
  mode: request.agent.Mode.FOREGROUND,
  gauge: true
};
const task = await request.agent.create(context, config);
task.on('completed', () => { /* 文件已在 cacheDir */ });
await task.start();
```
