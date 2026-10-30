# AVPlayer 生命周期参考

> AVPlayer 完整状态机、stateChange 回调模板、fd:// 协议、Speed 枚举映射。

---

## 状态机完整图

```
                        ┌─────────┐
                        │  Idle   │  ← media.createAVPlayer() 创建后
                        └────┬────┘
                             │ avPlayer.url = sourceUrl
                        ┌────▼────┐
                        │Initialized│
                        └────┬────┘
                             │ avPlayer.prepare()
                        ┌────▼────┐
                        │Prepared │  ← 可以 seek/setSpeed/play
                        └────┬────┘
                             │ avPlayer.play()
                   ┌─────────▼─────────┐
                   │     Playing       │
                   └─────────┬─────────┘
                    pause()  │  │ 播放完成
                   ┌─────────▼──▼──────┐
                   │  Paused / Completed│
                   └─────────┬─────────┘
                             │ stop() / reset()
                        ┌────▼────┐
                        │Stopped  │
                        └────┬────┘
                             │ release()
                        ┌────▼────┐
                        │Released │  ← 资源已释放
                        └─────────┘

  Error 处理：
  任何状态 → error → reset() → release()
```

---

## stateChange 回调完整模板

来自 AntennaPod PlaybackController.ets 的实战代码：

```typescript
import { media } from '@kit.MediaKit';

private setupAVPlayerCallbacks(): void {
  if (this.avPlayer === undefined) {
    return;
  }
  const player = this.avPlayer;

  // 状态变化回调 — 核心状态机驱动
  player.on('stateChange', (state: string) => {
    this.onStateChange(state);
  });

  // 播放进度更新（毫秒）
  player.on('timeUpdate', (time: number) => {
    AppStorage.setOrCreate<number>('playbackPosition', time);
    // 通过 EventBus 广播位置更新
  });

  // Seek 完成回调
  player.on('seekDone', (seekPos: number) => {
    AppStorage.setOrCreate<number>('playbackPosition', seekPos);
  });

  // 错误处理
  player.on('error', () => {
    // 重置播放器并更新状态
    this.resetPlayer();
    this.setStatus(PLAYER_STATUS_STOPPED);
  });
}

private onStateChange(state: string): void {
  if (state === 'initialized') {
    // URL 设置后触发 → 调用 prepare
    if (this.avPlayer !== undefined) {
      this.avPlayer.prepare();
    }

  } else if (state === 'prepared') {
    // prepare 完成 → 可以设置倍速、seek、开始播放
    this.onPrepared();

  } else if (state === 'playing') {
    // 播放中
    this.onPlaying();

  } else if (state === 'paused') {
    // 暂停
    this.onPaused();

  } else if (state === 'completed') {
    // 播放完成 → 自动切歌或停止
    this.onCompleted();

  } else if (state === 'stopped') {
    // 已停止

  } else if (state === 'released') {
    // 已释放

  } else if (state === 'error') {
    // 错误状态 → reset 并停止
    this.resetPlayer();
    this.setStatus(PLAYER_STATUS_STOPPED);
  }
}
```

---

## onPrepared 处理模板

Prepared 状态是设置播放参数的关键时机：

```typescript
private onPrepared(): void {
  if (this.avPlayer === undefined || this.currentMedia === undefined) {
    return;
  }

  // 1. 获取并更新时长
  const duration = this.avPlayer.duration;
  if (duration > 0) {
    AppStorage.setOrCreate<number>('playbackDuration', duration);
    this.currentMedia.duration = duration;
    this.feedMediaDao.setDuration(this.currentMedia.id, duration);
  }

  // 2. 设置播放倍速（必须在 Prepared 后）
  this.avPlayer.setSpeed(this.mapToPlaybackSpeed(this.currentSpeed));

  // 3. 恢复上次播放位置
  let startPos = this.currentMedia.position;
  if (startPos > 0) {
    this.avPlayer.seek(startPos);
  }

  // 4. 开始播放
  this.avPlayer.play();

  // 5. 启动后台播放
  this.backgroundManager.start(callbacks);
}
```

---

## fd:// 协议完整代码

```typescript
import { fileIo } from '@kit.CoreFileKit';

// 播放本地文件
async playLocalFile(localPath: string): Promise<void> {
  let sourceUrl: string;
  try {
    // 打开文件获取文件描述符
    const file = fileIo.openSync(localPath, fileIo.OpenMode.READ_ONLY);
    this.localFileFd = file.fd;
    sourceUrl = 'fd://' + file.fd.toString();
  } catch (e) {
    // 本地文件打开失败，降级为流式播放
    this.isStream = true;
    sourceUrl = this.currentMedia.downloadUrl;
  }

  // 创建 AVPlayer 并设置 URL
  this.avPlayer = await media.createAVPlayer();
  this.setupAVPlayerCallbacks();
  this.avPlayer.url = sourceUrl;  // 触发 Idle → Initialized
}

// 停止播放时统一关闭 fd
private async stopInternal(clearUI: boolean): Promise<void> {
  // 释放 AVPlayer
  if (this.avPlayer !== undefined) {
    try {
      this.avPlayer.off('stateChange');
      this.avPlayer.off('timeUpdate');
      this.avPlayer.off('seekDone');
      this.avPlayer.off('error');
      await this.avPlayer.reset();
      await this.avPlayer.release();
    } catch (e) { /* 忽略释放错误 */ }
    this.avPlayer = undefined;
  }

  // 关闭本地文件描述符
  if (this.localFileFd >= 0) {
    try {
      fileIo.closeSync(this.localFileFd);
    } catch (e) { /* 忽略关闭错误 */ }
    this.localFileFd = -1;
  }
}
```

---

## Speed 枚举映射完整代码

```typescript
import { media } from '@kit.MediaKit';

// 映射用户倍速到最近的有效值
private snapToValidSpeed(speed: number): number {
  const validSpeeds: number[] = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0];
  let closest = validSpeeds[0];
  let minDiff = Math.abs(speed - closest);
  for (let i = 1; i < validSpeeds.length; i++) {
    const diff = Math.abs(speed - validSpeeds[i]);
    if (diff < minDiff) {
      minDiff = diff;
      closest = validSpeeds[i];
    }
  }
  return closest;
}

// 映射数值到 PlaybackSpeed 枚举
private mapToPlaybackSpeed(speed: number): media.PlaybackSpeed {
  if (speed <= 0.75) {
    return media.PlaybackSpeed.SPEED_FORWARD_0_75_X;
  } else if (speed <= 1.0) {
    return media.PlaybackSpeed.SPEED_FORWARD_1_00_X;
  } else if (speed <= 1.25) {
    return media.PlaybackSpeed.SPEED_FORWARD_1_25_X;
  } else if (speed <= 1.5) {
    return media.PlaybackSpeed.SPEED_FORWARD_1_50_X;
  } else if (speed <= 1.75) {
    return media.PlaybackSpeed.SPEED_FORWARD_1_75_X;
  }
  return media.PlaybackSpeed.SPEED_FORWARD_2_00_X;
}

// 使用：在 Prepared 状态后设置倍速
async setSpeed(speed: number): Promise<void> {
  const snapped = this.snapToValidSpeed(speed);
  this.currentSpeed = snapped;
  if (this.avPlayer !== undefined) {
    this.avPlayer.setSpeed(this.mapToPlaybackSpeed(snapped));
  }
  AppStorage.setOrCreate<number>('playbackSpeed', snapped);
}
```

---

## AVPlayer 创建与释放

```typescript
// 创建
const avPlayer = await media.createAVPlayer();

// 释放（退出页面/停止播放时必须调用）
async releasePlayer(): Promise<void> {
  if (this.avPlayer !== undefined) {
    // 先取消所有事件监听
    this.avPlayer.off('stateChange');
    this.avPlayer.off('timeUpdate');
    this.avPlayer.off('seekDone');
    this.avPlayer.off('error');
    // reset → release
    await this.avPlayer.reset();
    await this.avPlayer.release();
    this.avPlayer = undefined;
  }
}
```

**注意**：
- 释放前必须先取消事件监听（off），否则可能收到意外回调
- reset() 和 release() 都是异步操作
- 释放后将 avPlayer 置为 undefined 防止重复释放
