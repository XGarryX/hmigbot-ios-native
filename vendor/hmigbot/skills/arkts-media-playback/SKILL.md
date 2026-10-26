---
name: arkts-media-playback
description: 生成 ArkTS/HarmonyOS **音频**播放代码。当用户需要实现 AVPlayer 音频播放、本地音频文件播放(fd://协议)、后台音频播放(ContinuousTask+AVSession)、播放速度控制、播放位置保存、队列自动切歌、睡眠定时器时触发。**视频播放（XComponent + Surface + letterbox + 横屏全屏 + 自动隐藏控件 + PiP）请走 [arkts-video-playback](../arkts-video-playback/SKILL.md)。**
metadata:
  type: domain
  domain: media
  tags:
  - media
  - audio
  - avplayer
  - avsession
---
# ArkTS Media Playback — 音频播放生成器

## §0 边界声明 — 本 skill 是音频专项

本 skill 仅覆盖**音频**通用基础与音频专属能力：

- AVPlayer 状态机（Idle → Initialized → Prepared → Playing/Paused → Stopped → Released）
- fd:// 本地文件协议
- PlaybackSpeed 6 档枚举映射
- 后台播放三要素（module.json5 + 权限 + 代码）
- AVSession 媒体控制
- 队列自动切歌 / 播放位置保存 / SleepTimer

**视频播放场景请走 [arkts-video-playback](../arkts-video-playback/SKILL.md)**：

- XComponent + Surface 集成（surfaceId 时序）
- 启播链路（调用方透传 videoUrl，避免 detail-single 反查）
- 视频 UI 基线（横屏 / 沉浸全屏 / letterbox / 顶底栏钉视频帧）
- 控件 3.5s 自动隐藏（PLAYING / PAUSED / PREPARED 三态）
- 视频按钮图标（webp 资源 / 禁用 Unicode）
- 画中画 PiP

> 视频场景**不要**无脑加 `BackgroundMode.AUDIO_PLAYBACK`（被系统策略限制）；视频后台走 PiP，不是 AVPlayer 后台续播。

---

## API 版本

本 skill 基于 **API 12+**（HarmonyOS 5.0.0+）。相关导入：

- 播放器：`import { media } from '@kit.MediaKit'`
- 文件：`import { fileIo } from '@kit.CoreFileKit'`
- 后台任务：`import { backgroundTaskManager } from '@kit.BackgroundTasksKit'`
- 媒体会话：`import { avSession } from '@kit.AVSessionKit'`
- 通知意图：`import { wantAgent } from '@kit.AbilityKit'`

遇到版本兼容性或其他不确定的 ArkTS 知识点，参阅 arkts-knowledge-verifier skill。

---

## AVPlayer 状态机

AVPlayer 是 HarmonyOS 的核心媒体播放 API，状态机**必须严格按顺序**，不能跳过：

```
                    ┌──────────────────────────────────┐
                    │           AVPlayer 状态机          │
                    └──────────────────────────────────┘

  创建 AVPlayer
       ↓
     Idle ──(设置 url)──→ Initialized ──(prepare)──→ Prepared
                                                       ↓
                                                    (play)
                                                       ↓
                                          Playing ←──→ Paused
                                           (pause)  (play)
                                              ↓
                                          completed
                                              ↓
                                          Stopped ──(release)──→ Released

  error 状态：任何阶段出错 → reset() → release()
```

### 状态转换规则

| 当前状态 | 可执行操作 | 转换到 |
|---------|----------|--------|
| Idle | 设置 `url` | Initialized |
| Initialized | `prepare()` | Prepared |
| Prepared | `play()`, `seek()`, `setSpeed()` | Playing |
| Playing | `pause()`, `seek()`, `stop()` | Paused / Stopped |
| Paused | `play()`, `seek()`, `stop()` | Playing / Stopped |
| Stopped | `release()` | Released |

**关键规则**：
- `seek()` 和 `setSpeed()` 必须在 Prepared 状态之后调用
- `play()` 必须在 Prepared 或 Paused 状态调用
- 所有状态转换通过 `on('stateChange')` 回调感知

---

## fd:// 本地文件协议

AVPlayer **不支持** `file://` 协议。本地文件必须使用 `fd://` + 文件描述符：

```typescript
import { fileIo } from '@kit.CoreFileKit';

// 打开文件获取 fd
const file = fileIo.openSync(localPath, fileIo.OpenMode.READ_ONLY);
const fd = file.fd;

// 设置 AVPlayer URL
avPlayer.url = 'fd://' + fd.toString();

// ⚠️ fd 生命周期管理：在 stopInternal() 中统一关闭
// 不要在播放过程中关闭，否则中断播放
```

**fd 关闭时机**：在停止播放时（stopInternal）统一关闭：
```typescript
if (this.localFileFd >= 0) {
  try {
    fileIo.closeSync(this.localFileFd);
  } catch (e) { /* 忽略关闭错误 */ }
  this.localFileFd = -1;
}
```

---

## PlaybackSpeed 枚举

`media.PlaybackSpeed` 只有 **6 个有效值**，不能设置任意倍速：

| 用户倍速 | 枚举值 |
|---------|-------|
| 0.75x | `media.PlaybackSpeed.SPEED_FORWARD_0_75_X` |
| 1.0x | `media.PlaybackSpeed.SPEED_FORWARD_1_00_X` |
| 1.25x | `media.PlaybackSpeed.SPEED_FORWARD_1_25_X` |
| 1.5x | `media.PlaybackSpeed.SPEED_FORWARD_1_50_X` |
| 1.75x | `media.PlaybackSpeed.SPEED_FORWARD_1_75_X` |
| 2.0x | `media.PlaybackSpeed.SPEED_FORWARD_2_00_X` |

用户传入任意值时，必须映射到最近的有效值：

```typescript
private snapToValidSpeed(speed: number): number {
  const validSpeeds: number[] = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0];
  let closest = validSpeeds[0];
  let minDiff = Math.abs(speed - closest);
  for (let i = 1; i < validSpeeds.length; i++) {
    const diff = Math.abs(speed - validSpeeds[i]);
    if (diff < minDiff) { minDiff = diff; closest = validSpeeds[i]; }
  }
  return closest;
}
```

---

## 后台播放三要素

后台持续播放需要三个条件**缺一不可**：

### 检查清单

- [ ] **module.json5**：abilities 中声明 `"backgroundModes": ["audioPlayback"]`
- [ ] **module.json5**：requestPermissions 中声明 `"ohos.permission.KEEP_BACKGROUND_RUNNING"`
- [ ] **代码**：`wantAgent.getWantAgent(info)` 创建通知栏返回意图
- [ ] **代码**：`backgroundTaskManager.startBackgroundRunning(context, AUDIO_PLAYBACK, agent)`
- [ ] **代码**：`avSession.createAVSession(context, 'appName', 'audio')` + `activate()`
- [ ] **代码**：注册媒体控制命令（play/pause/seek/next/previous）

### module.json5 配置

```json5
{
  "module": {
    "abilities": [{
      "name": "EntryAbility",
      "backgroundModes": ["audioPlayback"]
    }],
    "requestPermissions": [
      { "name": "ohos.permission.INTERNET" },
      { "name": "ohos.permission.KEEP_BACKGROUND_RUNNING" }
    ]
  }
}
```

### 启动后台播放代码概要

```typescript
// 1. 创建 WantAgent
const wantAgentInfo: wantAgent.WantAgentInfo = {
  wants: [{ bundleName: 'com.example.myapp', abilityName: 'EntryAbility' }],
  actionType: wantAgent.OperationType.START_ABILITY,
  requestCode: 0,
  actionFlags: [wantAgent.WantAgentFlags.UPDATE_PRESENT_FLAG]
};
const agent = await wantAgent.getWantAgent(wantAgentInfo);

// 2. 申请长时任务
await backgroundTaskManager.startBackgroundRunning(
  context, backgroundTaskManager.BackgroundMode.AUDIO_PLAYBACK, agent);

// 3. 创建并激活媒体会话
const session = await avSession.createAVSession(context, 'AppName', 'audio');
await session.activate();

// 4. 注册控制命令
session.on('play', () => { callbacks.onPlay(); });
session.on('pause', () => { callbacks.onPause(); });
session.on('seek', (time: number) => { callbacks.onSeek(time); });
session.on('playNext', () => { callbacks.onNext(); });
session.on('playPrevious', () => { callbacks.onPrevious(); });
```

> 完整代码模板见 `references/background-playback.md`

---

## 播放器架构（必须遵循）

```
PlaybackController (单例)
├── AVPlayer 管理（创建/释放/状态机）
├── 播放控制（play/pause/stop/seek/speed）
├── 队列管理（getNextQueueItem → 自动切歌）
├── 位置保存（5秒定时器 → DAO 持久化）
└── 事件广播（EventBus → UI 更新）

BackgroundPlaybackManager (单例)
├── WantAgent + startBackgroundRunning
├── AVSession（元数据 + 播放状态 + 命令监听）
└── 生命周期管理（start/stop）

SleepTimer (单例)
├── setInterval tick → 倒计时
├── EventBus 广播剩余时间
└── 到期回调 → pause()
```

---

## 常见错误

### 1. 使用 file:// 协议
```typescript
// ❌ AVPlayer 不支持 file:// 协议
avPlayer.url = 'file://' + localPath;

// ✓ 必须用 fd://
const file = fileIo.openSync(localPath, fileIo.OpenMode.READ_ONLY);
avPlayer.url = 'fd://' + file.fd.toString();
```

### 2. 跳过状态机步骤
```typescript
// ❌ Initialized 状态直接 play()
avPlayer.url = sourceUrl;
avPlayer.play();  // 无效！

// ✓ 在 stateChange 回调中按顺序操作
player.on('stateChange', (state: string) => {
  if (state === 'initialized') player.prepare();
  else if (state === 'prepared') player.play();
});
```

### 3. 设置任意倍速
```typescript
// ❌ 1.3x 不是有效值
avPlayer.setSpeed(1.3);

// ✓ 映射到最近的有效枚举
const snapped = snapToValidSpeed(1.3);  // → 1.25
avPlayer.setSpeed(mapToPlaybackSpeed(snapped));
```

### 4. 缺少后台播放配置
```typescript
// ❌ 只在代码中调用，忘记 module.json5 配置
await backgroundTaskManager.startBackgroundRunning(...);
// 切到后台后被系统杀死

// ✓ 三要素都要配齐（module.json5 + 权限 + 代码）
```

### 5. fd 泄漏
```typescript
// ❌ 打开文件后忘记关闭
const file = fileIo.openSync(path, fileIo.OpenMode.READ_ONLY);
avPlayer.url = 'fd://' + file.fd.toString();
// 文件描述符永远不关闭

// ✓ 在 stopInternal 中统一关闭
```

---

## 生成检查清单

- [ ] AVPlayer 通过 `media.createAVPlayer()` 创建
- [ ] 状态转换在 `on('stateChange')` 回调中处理
- [ ] 本地文件使用 `fd://` 协议（不是 `file://`）
- [ ] fd 在 stopInternal 中统一关闭
- [ ] 倍速只使用 6 个有效枚举值
- [ ] 后台播放满足三要素（module.json5 + 权限 + 代码）
- [ ] AVSession 注册了媒体控制命令
- [ ] 退出/切页面时调用 `avPlayer.release()` 释放资源
- [ ] 播放位置定时保存到数据库
- [ ] 没有使用 `any` 类型
- [ ] 导入使用 `@kit.*` 格式

---

## 跨 Skill 协作

| 需要什么 | 读取哪里 |
|---------|---------|
| 文件下载管理 | `arkts-download-manager/SKILL.md` |
| 数据库存储（DAO） | `arkts-data-layer/references/rdbstore-dao-patterns.md` |
| UI 组件（MiniPlayer） | `arkts-component-builder/references/media-app-components.md` |
| 状态管理（AppStorage） | `arkts-state-manager/SKILL.md` |
| 系统能力（权限/文件） | `arkts-system-capabilities/SKILL.md` |
| 验证 API 兼容性 | `arkts-knowledge-verifier/SKILL.md` |
| Android UI 对齐 | `arkts-ui-alignment/SKILL.md` |

> 完整路由矩阵见 `arkts-knowledge-verifier/references/skill-routing-guide.md`

---

## References

- `references/avplayer-lifecycle.md` — AVPlayer 完整生命周期 + stateChange 回调 + fd:// 协议 + Speed 枚举映射 — 生成 AVPlayer 初始化/状态机代码时读
- `references/background-playback.md` — 后台播放三要素完整代码 + AVSession + WantAgent + 清理 — 实现后台播放/AVSession 时读
- `references/playback-patterns.md` — 队列自动切歌 + 位置保存 + SleepTimer + PlaybackCallbacks — 实现队列切歌/位置保存/睡眠定时器时读
- 遇到版本兼容性或其他不确定的 ArkTS 知识点，参阅 **arkts-knowledge-verifier** skill


---

## See Also

- [arkts-video-playback](../arkts-video-playback/SKILL.md) — 视频特化层（XComponent + Surface + letterbox + 横屏全屏 + 自动隐藏控件 + PiP）；本 skill 仅覆盖音频通用基础与音频专属能力
