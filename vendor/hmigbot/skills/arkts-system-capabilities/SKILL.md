---
name: arkts-system-capabilities
description: HarmonyOS 系统 API 使用指南。当用户需要使用 photoAccessHelper 媒体查询、abilityAccessCtrl 权限申请、fileIo 文件操作、后台任务（workScheduler/ContinuousTask）、沙箱路径、相册访问、文件读写、权限检查、前台服务等系统能力时，务必触发此 skill。即使只说"怎么获取相册图片""怎么申请权限"也应触发。不含 AVPlayer 完整生命周期（用 arkts-media-playback）和文件下载队列（用 arkts-download-manager）。
metadata:
  type: domain
  domain: system
  tags:
  - system
  - permissions
  - file-io
  - background-task
---
# ArkTS System Capabilities — 系统能力指南

## API 版本

本 skill 基于 **API 12+**（HarmonyOS 5.0.0+）。系统 API 导入使用 `@kit.*` 格式：

- 媒体库：`import { photoAccessHelper } from '@kit.MediaLibraryKit'`
- 权限：`import { abilityAccessCtrl, Permissions } from '@kit.AbilityKit'`
- 文件：`import { fileIo } from '@kit.CoreFileKit'`
- 后台任务：`import { backgroundTaskManager } from '@kit.BackgroundTasksKit'`

遇到版本兼容性或其他不确定的 ArkTS 知识点，参阅 arkts-knowledge-verifier skill。

---

## 生成约定：本项目锁 ArkUI V2

**把系统能力调用包成页面时，组件壳一律用 V2 装饰器，绝不用 V1。**

- 页面：`@Entry @ComponentV2 struct`；状态用 `@Local`；入参用 `@Param`（可配 `@Once`）；事件回调用 `@Event`；派生监听用 `@Monitor`。
- **禁用 V1**：`@Component` / `@State` / `@Prop` / `@Link` / `@Watch`。
- 系统能力 API（`startBackgroundRunning` / `picker.*` / `call.makeCall` / `systemShare` 等）**用法本身不变**——照常写在 V2 组件的 `onClick` / `aboutToAppear` 里，只是承载它的组件壳换成 V2。references 里的 API 片段直接放进下面的壳即可。

极简 V2 壳（把任意系统能力片段放进 `onClick` 即可）：

```typescript
@Entry
@ComponentV2
struct Index {
  @Local status: string = '';

  build() {
    Column() {
      Button('调用系统能力')
        .onClick(async () => {
          // 这里放系统能力调用，如 picker.select() / call.makeCall(...) / startBackgroundRunning(...)
          this.status = 'done';
        })
      Text(this.status)
    }
  }
}
```

---

## 系统 API 分类索引

```
用户要做什么？
│
├─ 访问相册/媒体库（图片、视频）
│   └─ photoAccessHelper（见 references/photo-access-helper.md）
│       · 查询媒体资源
│       · 获取文件 URI
│       · FetchResult 游标遍历
│
├─ 申请/检查权限
│   └─ abilityAccessCtrl（见 references/permission-helper.md）
│       · 运行时权限请求
│       · 权限状态检查
│       · 权限拒绝处理
│
├─ 文件读写
│   └─ fileIo from @kit.CoreFileKit（见 references/file-utils.md）
│       · 沙箱路径（context.filesDir / context.cacheDir）
│       · 文件读写操作
│       · 目录创建
│
├─ 后台任务
│   └─ 见 references/background-tasks.md
│       · workScheduler（延迟任务）
│       · ContinuousTask（长时任务，如后台播放）
│       · AVSession（媒体会话，通知栏控制）
│
├─ 媒体播放（AVPlayer/本地播放/后台播放）
│   └─ 参阅 arkts-media-playback/SKILL.md（专项 Skill）
│       · AVPlayer 状态机
│       · fd:// 本地文件播放
│       · 后台播放三要素
│
├─ 文件下载（大文件/进度/队列）
│    └─ 参阅 arkts-download-manager/SKILL.md（专项 Skill）
│        · request.agent API
│        · 下载进度追踪
│        · 文件移动管线
│
└─ 拉起系统应用
    ├─ 分享面板（隐式启动）→ references/share-panel.md
    │   · @kit.ShareKit（ShareController / SharedData）
    │   · UTD 类型转换、MIME 判断
    │   · SharePreviewMode / SelectionMode 配置
    │
    ├─ 系统相机（隐式启动）→ references/camera-picker.md
    │   · @kit.CameraKit（cameraPicker.pick）
    │   · PickerMediaType（PHOTO / VIDEO）
    │   · PickerResult 处理
    │
    ├─ 文件管理器（隐式启动）→ references/document-picker.md
    │   · @kit.CoreFileKit（DocumentViewPicker）
    │   · .select() 选择文件（对应 ACTION_OPEN_DOCUMENT）
    │   · .save() 保存文件（对应 ACTION_CREATE_DOCUMENT）
    │   · DocumentSelectOptions / DocumentSaveOptions 配置
    │
    ├─ 系统打印管理 → references/print-management.md
    │   · @kit.BasicServicesKit（print.print）
    │   · WebPrintDocumentAdapter（网页打印）
    │   · PrintDocumentAdapter（自定义内容打印）
    │
    ├─ 浏览器/URL 跳转（隐式启动）→ references/browser-intent.md
    │   · Want + startAbility
    │   · action.viewData、mailto: 协议
    │
    ├─ 电话拨号 → references/telephony-dial.md
    │   · @kit.TelephonyKit（call.makeCall）
    │   · 拉起系统拨号界面，不走 Want/tel:
    │
    └─ 系统设置跳转（显式启动）→ references/system-settings.md
        · Want + startAbility（显式指定 bundleName/abilityName）
        · 华为系统设置页面跳转（com.huawei.settings）
        · 权限设置、应用信息页面
```

---

## 核心踩坑警示

### 1. photoAccessHelper URI 不能给 Image 组件渲染视频

视频类型的 URI 传给 `Image` 组件会显示灰色空白。视频项需用占位图。

### 2. FetchResult 不是数组

`FetchResult` 是游标式迭代器，必须用 `getFirstObject()` + `getNextObject()` 遍历，最后 `close()`。

### 3. 文件只能写沙箱路径

HarmonyOS 应用只能访问沙箱目录（`context.filesDir`、`context.cacheDir`），写入其他路径会 Permission denied。

### 4. 后台播放需要三个条件

module.json5 声明 `backgroundModes` + 代码申请 `ContinuousTask` + `AVSession` 注册媒体会话。缺一不可。

### 5. 权限请求是异步的

`requestPermissionsFromUser` 返回 Promise，必须 await。

### 6. 分享面板 ShareController.show() 是异步的

`show()` 不会阻塞 UI，通过 `.then()`/.catch() 处理结果，不能 await。

### 7. 拉起其他应用需要 module.json5 配置

**需要配置的场景**：
- 相机跳转：必须配置 `entity.system.camera` + `ohos.want.action.camera`
- 响应外部查看请求：需要配置 `ohos.want.action.view`（如相册响应其他应用查看图片）

**通常不需要配置的场景**：
- 浏览器跳转（`ohos.want.action.viewData`）：系统内置支持
- 图片/视频分享：通常系统已内置支持（某些设备可能需要）
- 系统设置跳转（显式 Want）：直接指定目标应用，无需声明

> 详细配置规则见各 references 文件中的 module.json5 配置章节。
> 系统设置跳转参考 `references/system-settings.md`

---

## AVPlayer 速查

AVPlayer 是 HarmonyOS 的核心媒体播放 API。状态机必须严格按顺序：

```
Idle →(url=)→ Initialized →(prepare)→ Prepared →(play)→ Playing ↔ Paused
```

**关键导入**：`import { media } from '@kit.MediaKit'`

**本地文件必须用 fd:// 协议**：
```typescript
const file = fileIo.openSync(path, fileIo.OpenMode.READ_ONLY);
avPlayer.url = 'fd://' + file.fd.toString();
```

> 完整生命周期、后台播放、倍速控制等详见 **arkts-media-playback** skill 和 `references/avplayer-guide.md`。

---

## 后台播放三要素检查清单

后台持续播放需要三个条件同时满足，缺一不可：

- [ ] **module.json5**：abilities 中声明 `"backgroundModes": ["audioPlayback"]`
- [ ] **module.json5**：requestPermissions 中声明 `"ohos.permission.KEEP_BACKGROUND_RUNNING"`
- [ ] **代码**：调用 `backgroundTaskManager.startBackgroundRunning(context, BackgroundMode.AUDIO_PLAYBACK, wantAgent)`
- [ ] **代码**：创建 `avSession.createAVSession()` 并 `activate()`
- [ ] **代码**：创建 `wantAgent` 用于通知栏点击返回应用

---

## 权限配置三件套

音频/网络应用常用权限组合（均为 system_grant，无需弹窗）：

```json5
"requestPermissions": [
  { "name": "ohos.permission.INTERNET" },
  { "name": "ohos.permission.GET_NETWORK_INFO" },
  { "name": "ohos.permission.KEEP_BACKGROUND_RUNNING" }
]
```

---

## workScheduler 配置

后台定时任务需要在 module.json5 中声明 extensionAbilities：

```json5
"extensionAbilities": [{
  "name": "FeedUpdateWorkAbility",
  "srcEntry": "./ets/workers/FeedUpdateWorkAbility.ets",
  "type": "workScheduler"
}]
```

---

## fd:// 本地文件协议

AVPlayer 播放本地文件不能用 `file://`，必须用 `fd://`：

```typescript
import { fileIo } from '@kit.CoreFileKit';
const file = fileIo.openSync(localPath, fileIo.OpenMode.READ_ONLY);
avPlayer.url = 'fd://' + file.fd.toString();
// 播放结束后统一关闭：fileIo.closeSync(file.fd);
```

---

## 常见错误 vs 正确写法

### 错误 1：直接用 for 循环遍历 FetchResult

```typescript
// 错误 — FetchResult 不支持 for...of
for (const asset of fetchResult) { ... }

// 正确 — 使用 getFirstObject + getNextObject
let asset = await fetchResult.getFirstObject()
let i = 0
while (i < count) {
  // 处理 asset
  i++
  if (i < count) asset = await fetchResult.getNextObject()
}
fetchResult.close()
```

### 错误 2：写文件到绝对路径

```typescript
// 错误 — Permission denied
const path = '/storage/emulated/0/Download/file.txt'

// 正确 — 使用沙箱路径
const path = `${context.filesDir}/downloads/file.txt`
```

### 错误 3：忘记关闭 FetchResult

```typescript
// 错误 — 资源泄漏
const result = await phAccessHelper.getAssets(options)
// 使用后没有 close

// 正确
const result = await phAccessHelper.getAssets(options)
try {
  // 遍历处理...
} finally {
  result.close()
}
```

---

## 生成检查清单

- [ ] 页面/产物页用 V2 装饰器（`@Entry @ComponentV2` + `@Local`/`@Param`/`@Event`），无 V1 `@Component`/`@State`/`@Prop`/`@Link`/`@Watch`
- [ ] photoAccessHelper 的 FetchResult 在使用后调用了 close()
- [ ] 文件路径使用沙箱路径（context.filesDir / context.cacheDir）
- [ ] 需要的权限在 module.json5 中声明
- [ ] 运行时权限用 abilityAccessCtrl 动态请求
- [ ] 后台任务同时满足 module.json5 声明 + 代码申请
- [ ] 异步 API 正确使用 async/await
- [ ] 隐式启动（相机/分享/浏览器）已在 module.json5 的 skills 中声明 entities/actions

---

## 跨 Skill 协作

| 需要什么 | 读取哪里 |
|---------|---------|
| 网络请求（HTTP 下载） | `arkts-data-layer/references/network-service.md` |
| 权限配置（module.json5） | `arkts-project-scaffolder/SKILL.md` 权限速查表 |
| 数据库存储 | `arkts-data-layer/references/rdbstore-dao-patterns.md` |
| 三方库替代方案 | `arkts-library-migration/SKILL.md` |
| 验证 API 兼容性 | `arkts-knowledge-verifier/SKILL.md` |
| 媒体播放（AVPlayer/后台） | `arkts-media-playback/SKILL.md` |
| 文件下载（request.agent） | `arkts-download-manager/SKILL.md` |
| Android UI 对齐 | `arkts-ui-alignment/SKILL.md` |

> 完整路由矩阵见 `arkts-knowledge-verifier/references/skill-routing-guide.md`

---

## References

- `references/share-panel.md` — @kit.ShareKit 分享面板完整模板
- `references/camera-picker.md` — @kit.CameraKit 系统相机调用模板
- `references/document-picker.md` — @kit.CoreFileKit 文件管理器调用模板（DocumentViewPicker.select / .save）
- `references/print-management.md` — @kit.BasicServicesKit 系统打印管理模板（print.print / WebPrintDocumentAdapter）
- `references/browser-intent.md` — Want + startAbility 浏览器/URL 跳转模板
- `references/telephony-dial.md` — @kit.TelephonyKit 电话拨号（call.makeCall 拉起系统拨号界面）
- `references/system-settings.md` — Want + startAbility 系统设置跳转模板（显式 Want）
- `references/photo-access-helper.md` — 媒体查询/URI 获取/FetchResult 遍历完整模板
- `references/permission-helper.md` — abilityAccessCtrl 权限请求与检查
- `references/file-utils.md` — @kit.CoreFileKit 文件读写/沙箱路径
- `references/background-tasks.md` — workScheduler/ContinuousTask/AVSession 后台任务
- `references/avplayer-guide.md` — AVPlayer 完整生命周期 + stateChange 回调 + fd:// + Speed 枚举
- 遇到版本兼容性或其他不确定的 ArkTS 知识点，参阅 **arkts-knowledge-verifier** skill
