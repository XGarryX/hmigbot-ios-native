# 后台播放参考

> WantAgent + startBackgroundRunning + AVSession 三要素完整代码模板。

---

## 三要素架构

```
后台播放三要素：
┌─────────────────────┐
│ 1. WantAgent        │ ← 通知栏点击返回应用
├─────────────────────┤
│ 2. ContinuousTask   │ ← 申请后台长时任务（不被系统杀）
├─────────────────────┤
│ 3. AVSession        │ ← 媒体会话（通知栏/锁屏控制）
└─────────────────────┘
三者缺一不可！
```

---

## module.json5 配置（必须）

```json5
{
  "module": {
    "abilities": [{
      "name": "EntryAbility",
      "backgroundModes": ["audioPlayback"]  // 声明后台音频播放能力
    }],
    "requestPermissions": [
      { "name": "ohos.permission.INTERNET" },
      { "name": "ohos.permission.KEEP_BACKGROUND_RUNNING" }  // 后台长时任务权限
    ]
  }
}
```

---

## BackgroundPlaybackManager 完整实现

来自 AntennaPod 实战代码：

```typescript
import { backgroundTaskManager } from '@kit.BackgroundTasksKit';
import { wantAgent } from '@kit.AbilityKit';
import { avSession } from '@kit.AVSessionKit';

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
    if (this.isBackgroundRunning) {
      return;
    }
    const context = GlobalState.getContext();

    try {
      // ===== 要素 1：创建 WantAgent =====
      const wantAgentInfo: wantAgent.WantAgentInfo = {
        wants: [
          {
            bundleName: 'com.example.myapp',
            abilityName: 'EntryAbility'
          }
        ],
        actionType: wantAgent.OperationType.START_ABILITY,
        requestCode: 0,
        actionFlags: [wantAgent.WantAgentFlags.UPDATE_PRESENT_FLAG]
      };
      const agent = await wantAgent.getWantAgent(wantAgentInfo);

      // ===== 要素 2：申请后台长时任务 =====
      await backgroundTaskManager.startBackgroundRunning(
        context,
        backgroundTaskManager.BackgroundMode.AUDIO_PLAYBACK,
        agent
      );

      // ===== 要素 3：创建媒体会话 =====
      this.session = await avSession.createAVSession(
        context, 'MyApp', 'audio'
      );

      // 激活会话
      await this.session.activate();

      // 注册控制命令
      this.session.on('play', () => {
        callbacks.onPlay();
      });
      this.session.on('pause', () => {
        callbacks.onPause();
      });
      this.session.on('seek', (time: number) => {
        callbacks.onSeek(time);
      });
      this.session.on('fastForward', () => {
        callbacks.onFastForward();
      });
      this.session.on('rewind', () => {
        callbacks.onRewind();
      });
      this.session.on('playNext', () => {
        callbacks.onNext();
      });
      this.session.on('playPrevious', () => {
        callbacks.onPrevious();
      });

      this.isBackgroundRunning = true;
    } catch (e) {
      // 后台播放启动失败
    }
  }

  async stop(): Promise<void> {
    if (!this.isBackgroundRunning) {
      return;
    }
    try {
      // 清理媒体会话
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
      // 停止后台任务
      const context = GlobalState.getContext();
      await backgroundTaskManager.stopBackgroundRunning(context);
      this.isBackgroundRunning = false;
    } catch (e) {
      // 停止失败
    }
  }

  // 更新通知栏显示的元数据
  async updateMetadata(
    title: string, artist: string, durationMs: number
  ): Promise<void> {
    if (this.session === undefined) {
      return;
    }
    try {
      const metadata: avSession.AVMetadata = {
        assetId: '0',
        title: title,
        artist: artist,
        duration: durationMs
      };
      await this.session.setAVMetadata(metadata);
    } catch (e) { /* 更新失败 */ }
  }

  // 更新播放状态（通知栏显示播放/暂停）
  async updatePlaybackState(
    isPlaying: boolean, positionMs: number
  ): Promise<void> {
    if (this.session === undefined) {
      return;
    }
    try {
      const pos: avSession.PlaybackPosition = {
        elapsedTime: positionMs,
        updateTime: Date.now()
      };
      const playbackState: avSession.AVPlaybackState = {
        state: isPlaying
          ? avSession.PlaybackState.PLAYBACK_STATE_PLAY
          : avSession.PlaybackState.PLAYBACK_STATE_PAUSE,
        position: pos
      };
      await this.session.setAVPlaybackState(playbackState);
    } catch (e) { /* 更新失败 */ }
  }
}
```

---

## 调用时机

### 启动后台播放

在 PlaybackController 的 `onPrepared()` 中调用：

```typescript
private onPrepared(): void {
  // ... 设置倍速、seek 等
  this.avPlayer.play();

  // 启动后台播放
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
```

### 更新元数据

在 `onPrepared()` 中更新歌曲信息：

```typescript
this.backgroundManager.updateMetadata(
  item.title,
  feed.getDisplayTitle(),
  duration
);
```

### 更新播放状态

在 `onPlaying()` 和 `onPaused()` 中更新：

```typescript
this.backgroundManager.updatePlaybackState(true, currentPosition);   // Playing
this.backgroundManager.updatePlaybackState(false, currentPosition);  // Paused
```

### 停止后台播放

在 `stopInternal()` 中调用：

```typescript
await this.backgroundManager.stop();
```
