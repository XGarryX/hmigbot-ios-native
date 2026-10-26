# 后台任务指南

> workScheduler（延迟任务）、ContinuousTask（长时任务）、AVSession（媒体会话）的使用指南。

---

## 后台任务类型选择

```
需要什么后台能力？
│
├─ 定时/延迟执行任务（如定时更新数据）
│   └─ workScheduler（见下方）
│       ⚠️ 最短间隔比 Android WorkManager 更保守
│
├─ 持续运行（如后台播放音乐）
│   └─ ContinuousTask（长时任务）
│       需要 module.json5 声明 backgroundModes
│
└─ 媒体播放控制（通知栏/锁屏控制）
    └─ AVSession（媒体会话）
        配合 ContinuousTask 使用
```

---

## workScheduler（延迟任务）

```typescript
import { workScheduler } from '@kit.BackgroundTasksKit'

// 注册延迟任务
const workInfo: workScheduler.WorkInfo = {
  workId: 1,
  bundleName: 'com.example.myapp',
  abilityName: 'UpdateWorker',
  isPersisted: true,
  repeatCycleTime: 7200000,  // 2 小时（官方循环任务最短间隔，不是 30 分钟）
  isRepeat: true,
  networkType: workScheduler.NetworkType.NETWORK_TYPE_ANY
}

workScheduler.startWork(workInfo)
```

**注意**：
- ⚠️ HarmonyOS `workScheduler` 最短重复间隔比 Android `WorkManager` 更保守
- 不要依赖精确间隔，系统会根据电量和资源情况调整
- 如需频繁更新，改为用户手动触发 + 后台半定时

---

## ContinuousTask（长时任务）

后台播放音乐等场景必须使用长时任务：

### 前提条件（三个条件缺一不可）

1. **module.json5 声明 backgroundModes**：

```json5
{
  "module": {
    "abilities": [{
      "name": "EntryAbility",
      "backgroundModes": ["audioPlayback"]
    }]
  }
}
```

2. **代码申请长时任务**：

```typescript
import { backgroundTaskManager } from '@kit.BackgroundTasksKit'
import { wantAgent, WantAgent } from '@kit.AbilityKit'
import { common } from '@kit.AbilityKit'

async function startBackgroundPlay(context: common.UIAbilityContext): Promise<void> {
  // 创建 WantAgent（点击通知时的跳转意图）
  const wantAgentInfo: wantAgent.WantAgentInfo = {
    wants: [{
      bundleName: 'com.example.myapp',
      abilityName: 'EntryAbility'
    }],
    actionType: wantAgent.OperationType.START_ABILITY,
    requestCode: 0
  }
  const wantAgentObj = await wantAgent.getWantAgent(wantAgentInfo)

  // 申请长时任务
  await backgroundTaskManager.startBackgroundRunning(
    context,
    backgroundTaskManager.BackgroundMode.AUDIO_PLAYBACK,
    wantAgentObj
  )
}

// 停止长时任务
async function stopBackgroundPlay(context: common.UIAbilityContext): Promise<void> {
  await backgroundTaskManager.stopBackgroundRunning(context)
}
```

3. **注册 AVSession**（见下方）

---

## AVSession（媒体会话）

```typescript
import { avSession } from '@kit.MediaKit'

// 创建会话
const session = await avSession.createAVSession(context, 'musicPlayer', 'audio')

// 设置元数据
session.setAVMetadata({
  assetId: 'song_001',
  title: '歌曲名',
  artist: '歌手',
  duration: 300000  // 毫秒
})

// 设置播放状态
session.setAVPlaybackState({
  state: avSession.PlaybackState.PLAYBACK_STATE_PLAY,
  position: { elapsedTime: 50000, updateTime: Date.now() }
})

// 监听控制命令（来自通知栏/锁屏）
session.on('play', () => { avPlayer.play() })
session.on('pause', () => { avPlayer.pause() })
session.on('playNext', () => { playNext() })
session.on('playPrevious', () => { playPrevious() })

// 激活会话
await session.activate()

// 释放会话（退出时）
await session.destroy()
```

---

## backgroundModes 类型

| 模式 | 用途 | module.json5 值 |
|------|------|----------------|
| 音频播放 | 后台播放音乐/播客 | `"audioPlayback"` |
| 定位 | 后台持续定位 | `"location"` |
| 蓝牙交互 | 后台蓝牙通信 | `"bluetoothInteraction"` |
| 数据传输 | 后台大文件下载/上传 | `"dataTransfer"` |

---

## 后台播放三要素实战模式

> 基于 AntennaPod ArkTS 播客应用 `BackgroundPlaybackManager.ets` 提取的完整实战代码。

### 三要素缺一不可

```
1. module.json5 声明 backgroundModes: ["audioPlayback"]
2. backgroundTaskManager.startBackgroundRunning() 申请长时任务
3. avSession.createAVSession() + activate() 注册媒体会话
```

### 完整实现 — BackgroundPlaybackManager

```typescript
// 文件: playback/BackgroundPlaybackManager.ets
import { backgroundTaskManager } from '@kit.BackgroundTasksKit';
import { wantAgent } from '@kit.AbilityKit';
import { avSession } from '@kit.AVSessionKit';
import { GlobalState } from '../common/GlobalState';

export interface PlaybackCallbacks {
  onPlay: () => Promise<void>;
  onPause: () => Promise<void>;
  onSeek: (timeMs: number) => Promise<void>;
  onFastForward: () => Promise<void>;
  onRewind: () => Promise<void>;
  onNext: () => Promise<void>;
  onPrevious: () => Promise<void>;
}

export class BackgroundPlaybackManager {
  private static instance: BackgroundPlaybackManager | undefined = undefined;
  private session: avSession.AVSession | undefined = undefined;
  private isBackgroundRunning: boolean = false;

  static getInstance(): BackgroundPlaybackManager {
    if (BackgroundPlaybackManager.instance === undefined) {
      BackgroundPlaybackManager.instance = new BackgroundPlaybackManager();
    }
    return BackgroundPlaybackManager.instance;
  }

  async start(callbacks: PlaybackCallbacks): Promise<void> {
    if (this.isBackgroundRunning) { return; }
    const context = GlobalState.getContext();

    // 1. 创建 WantAgent（通知栏点击跳转）
    const wantAgentInfo: wantAgent.WantAgentInfo = {
      wants: [{
        bundleName: 'com.example.antennapod_arkts',
        abilityName: 'EntryAbility'
      }],
      actionType: wantAgent.OperationType.START_ABILITY,
      requestCode: 0,
      actionFlags: [wantAgent.WantAgentFlags.UPDATE_PRESENT_FLAG]
    };
    const agent = await wantAgent.getWantAgent(wantAgentInfo);

    // 2. 启动后台长时任务
    await backgroundTaskManager.startBackgroundRunning(context,
      backgroundTaskManager.BackgroundMode.AUDIO_PLAYBACK, agent);

    // 3. 创建并激活 AVSession
    this.session = await avSession.createAVSession(context, 'AntennaPod', 'audio');
    await this.session.activate();

    // 4. 注册 7 个控制命令
    this.session.on('play', () => { callbacks.onPlay(); });
    this.session.on('pause', () => { callbacks.onPause(); });
    this.session.on('seek', (time: number) => { callbacks.onSeek(time); });
    this.session.on('fastForward', () => { callbacks.onFastForward(); });
    this.session.on('rewind', () => { callbacks.onRewind(); });
    this.session.on('playNext', () => { callbacks.onNext(); });
    this.session.on('playPrevious', () => { callbacks.onPrevious(); });

    this.isBackgroundRunning = true;
  }

  async stop(): Promise<void> {
    if (!this.isBackgroundRunning) { return; }

    // 释放顺序：取消监听 → 停用会话 → 销毁会话 → 停止后台任务
    if (this.session !== undefined) {
      this.session.off('play');
      this.session.off('pause');
      this.session.off('seek');
      this.session.off('fastForward');
      this.session.off('rewind');
      this.session.off('playNext');
      this.session.off('playPrevious');
      await this.session.deactivate();
      await this.session.destroy();
      this.session = undefined;
    }

    const context = GlobalState.getContext();
    await backgroundTaskManager.stopBackgroundRunning(context);
    this.isBackgroundRunning = false;
  }

  async updateMetadata(title: string, artist: string, durationMs: number): Promise<void> {
    if (this.session === undefined) { return; }
    const metadata: avSession.AVMetadata = {
      assetId: '0',
      title: title,
      artist: artist,
      duration: durationMs
    };
    await this.session.setAVMetadata(metadata);
  }

  async updatePlaybackState(isPlaying: boolean, positionMs: number): Promise<void> {
    if (this.session === undefined) { return; }
    const pos: avSession.PlaybackPosition = {
      elapsedTime: positionMs,
      updateTime: Date.now()
    };
    const playbackState: avSession.AVPlaybackState = {
      state: isPlaying ? avSession.PlaybackState.PLAYBACK_STATE_PLAY :
        avSession.PlaybackState.PLAYBACK_STATE_PAUSE,
      position: pos
    };
    await this.session.setAVPlaybackState(playbackState);
  }
}
```

### 调用时机

```typescript
// PlaybackController.onPrepared() 中调用 start
private onPrepared(): void {
  // AVPlayer prepare 完成后，启动后台播放
  const callbacks: PlaybackCallbacks = {
    onPlay: async (): Promise<void> => { await this.play(); },
    onPause: async (): Promise<void> => { await this.pause(); },
    onSeek: async (timeMs: number): Promise<void> => { await this.seekTo(timeMs); },
    onFastForward: async (): Promise<void> => { await this.fastForward(); },
    onRewind: async (): Promise<void> => { await this.rewind(); },
    onNext: async (): Promise<void> => { await this.skipToNext(); },
    onPrevious: async (): Promise<void> => { await this.skipToPrevious(); }
  };
  this.backgroundManager.start(callbacks);
}

// PlaybackController.stopInternal() 中调用 stop
private async stopInternal(clearUI: boolean): Promise<void> {
  await this.backgroundManager.stop();
}
```

---

## workScheduler module.json5 配置模板

### extensionAbilities 注册

```json5
{
  "module": {
    "extensionAbilities": [
      {
        "name": "FeedUpdateWorkAbility",
        "srcEntry": "./ets/workers/FeedUpdateWorkAbility.ets",
        "type": "workScheduler",
        "exported": false
      }
    ]
  }
}
```

### WorkSchedulerExtensionAbility 实现

```typescript
// 文件: workers/FeedUpdateWorkAbility.ets
import { WorkSchedulerExtensionAbility, workScheduler } from '@kit.BackgroundTasksKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { FeedUpdateService } from '../network/FeedUpdateService';

const DOMAIN: number = 0x0000;
const TAG: string = 'FeedUpdateWorkAbility';

export default class FeedUpdateWorkAbility extends WorkSchedulerExtensionAbility {
  onWorkStart(work: workScheduler.WorkInfo): void {
    hilog.info(DOMAIN, TAG, 'Feed update work started, workId=%{public}d', work.workId);
    const service = new FeedUpdateService();
    service.refreshAllFeeds().then(() => {
      hilog.info(DOMAIN, TAG, 'Feed update work completed');
    }).catch((e: Error) => {
      hilog.error(DOMAIN, TAG, 'Feed update work failed: %{public}s', e.message);
    });
  }

  onWorkStop(work: workScheduler.WorkInfo): void {
    hilog.info(DOMAIN, TAG, 'Feed update work stopped, workId=%{public}d', work.workId);
  }
}
```

### 注册定时工作

```typescript
import { workScheduler } from '@kit.BackgroundTasksKit';

function registerFeedUpdateWork(): void {
  const workInfo: workScheduler.WorkInfo = {
    workId: 1001,
    bundleName: 'com.example.antennapod_arkts',
    abilityName: 'FeedUpdateWorkAbility',
    isPersisted: true,          // 重启后保留
    repeatCycleTime: 7200000,   // 2 小时（官方循环任务最短间隔；设了循环间隔须同时设 isRepeat 或 repeatCount 之一）
    isRepeat: true,             // 重复执行
    networkType: workScheduler.NetworkType.NETWORK_TYPE_ANY  // 需要网络
  };
  workScheduler.startWork(workInfo);
}

// 取消定时工作
// ⚠️ stopWork(work: WorkInfo, needCancel?: boolean): void —— 首参是【完整 WorkInfo】，
//    与 startWork 同形，须含 workId + bundleName + abilityName（缺则编译报错 10505001：
//    Type '{ workId: number; }' is missing the following properties from type 'WorkInfo': bundleName, abilityName）。
//    不要传 { workId } 裸对象。复用注册时那份 workInfo（或重建含三个必填项的完整对象）。
function cancelFeedUpdateWork(): void {
  const workInfo: workScheduler.WorkInfo = {
    workId: 1001,
    bundleName: 'com.example.antennapod_arkts',
    abilityName: 'FeedUpdateWorkAbility'
  };
  workScheduler.stopWork(workInfo);
}
```

### workScheduler vs Android WorkManager 对比

| 特性 | Android WorkManager | HarmonyOS workScheduler |
|------|-------------------|----------------------|
| 最短间隔 | 15 分钟 | 2 小时（循环任务，官方下限） |
| 约束条件 | 网络、充电、空闲 | 网络、充电、存储 |
| 持久化 | 自动 | `isPersisted: true` |
| 链式任务 | 支持 (WorkContinuation) | 不支持 |
| 精确执行 | 不保证 | 不保证 |
| 注册方式 | `WorkManager.enqueue()` | `workScheduler.startWork()` |
| 实现方式 | `Worker` 类 | `WorkSchedulerExtensionAbility` |
