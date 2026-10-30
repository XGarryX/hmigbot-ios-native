# AVPlayer 完整指南

> AVPlayer 生命周期、stateChange 回调、fd:// 协议、Speed 枚举、后台播放三要素。

---

## AVPlayer 状态机

```
Idle →(url=)→ Initialized →(prepare)→ Prepared →(play)→ Playing ↔(pause/play)↔ Paused
                                                                    ↓ completed
                                                                  Stopped →(release)→ Released
Error: 任何状态出错 → reset() → release()
```

### 状态转换规则

| 当前状态 | 可执行操作 | 目标状态 |
|---------|----------|---------|
| Idle | 设置 `url` | Initialized |
| Initialized | `prepare()` | Prepared |
| Prepared | `play()`, `seek()`, `setSpeed()` | Playing |
| Playing | `pause()`, `seek()`, `stop()` | Paused/Stopped |
| Paused | `play()`, `seek()`, `stop()` | Playing/Stopped |
| Stopped | `release()` | Released |

---

## stateChange 回调模板

```typescript
import { media } from '@kit.MediaKit';

player.on('stateChange', (state: string) => {
  if (state === 'initialized') {
    // URL 设置后触发 → 必须调用 prepare
    player.prepare();
  } else if (state === 'prepared') {
    // prepare 完成 → 设置倍速/seek/play
    player.setSpeed(media.PlaybackSpeed.SPEED_FORWARD_1_00_X);
    if (savedPosition > 0) {
      player.seek(savedPosition);
    }
    player.play();
  } else if (state === 'playing') {
    // 播放中 → 更新 UI 状态
    AppStorage.setOrCreate<boolean>('isPlaying', true);
  } else if (state === 'paused') {
    AppStorage.setOrCreate<boolean>('isPlaying', false);
  } else if (state === 'completed') {
    // 播放完成 → 自动切歌或停止
  } else if (state === 'error') {
    player.reset();
    player.release();
  }
});

player.on('timeUpdate', (time: number) => {
  AppStorage.setOrCreate<number>('playbackPosition', time);
});

player.on('seekDone', (seekPos: number) => {
  AppStorage.setOrCreate<number>('playbackPosition', seekPos);
});

player.on('error', () => {
  // 错误处理
});
```

---

## fd:// 本地文件播放

```typescript
import { fileIo } from '@kit.CoreFileKit';

// 打开文件
const file = fileIo.openSync(localPath, fileIo.OpenMode.READ_ONLY);
const fd = file.fd;
avPlayer.url = 'fd://' + fd.toString();

// 停止时关闭
if (this.localFileFd >= 0) {
  try { fileIo.closeSync(this.localFileFd); } catch (e) {}
  this.localFileFd = -1;
}
```

---

## Speed 枚举映射

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

private mapToPlaybackSpeed(speed: number): media.PlaybackSpeed {
  if (speed <= 0.75) return media.PlaybackSpeed.SPEED_FORWARD_0_75_X;
  else if (speed <= 1.0) return media.PlaybackSpeed.SPEED_FORWARD_1_00_X;
  else if (speed <= 1.25) return media.PlaybackSpeed.SPEED_FORWARD_1_25_X;
  else if (speed <= 1.5) return media.PlaybackSpeed.SPEED_FORWARD_1_50_X;
  else if (speed <= 1.75) return media.PlaybackSpeed.SPEED_FORWARD_1_75_X;
  return media.PlaybackSpeed.SPEED_FORWARD_2_00_X;
}
```

---

## 后台播放三要素

```typescript
import { backgroundTaskManager } from '@kit.BackgroundTasksKit';
import { wantAgent } from '@kit.AbilityKit';
import { avSession } from '@kit.AVSessionKit';

// 1. WantAgent
const info: wantAgent.WantAgentInfo = {
  wants: [{ bundleName: 'com.example.app', abilityName: 'EntryAbility' }],
  actionType: wantAgent.OperationType.START_ABILITY,
  requestCode: 0,
  actionFlags: [wantAgent.WantAgentFlags.UPDATE_PRESENT_FLAG]
};
const agent = await wantAgent.getWantAgent(info);

// 2. 长时任务
await backgroundTaskManager.startBackgroundRunning(
  context, backgroundTaskManager.BackgroundMode.AUDIO_PLAYBACK, agent);

// 3. AVSession
const session = await avSession.createAVSession(context, 'AppName', 'audio');
await session.activate();
session.on('play', () => { /* play */ });
session.on('pause', () => { /* pause */ });
session.on('seek', (time: number) => { /* seek */ });
session.on('playNext', () => { /* next */ });
session.on('playPrevious', () => { /* prev */ });

// 更新元数据
await session.setAVMetadata({ assetId: '0', title: 'Title', artist: 'Artist', duration: 300000 });

// 更新播放状态
await session.setAVPlaybackState({
  state: avSession.PlaybackState.PLAYBACK_STATE_PLAY,
  position: { elapsedTime: posMs, updateTime: Date.now() }
});

// 停止
session.off('play'); session.off('pause');
await session.deactivate();
await session.destroy();
await backgroundTaskManager.stopBackgroundRunning(context);
```
