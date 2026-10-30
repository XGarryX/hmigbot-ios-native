# 播放模式参考

> 队列自动切歌、位置保存、SleepTimer、PlaybackCallbacks 接口。

---

## 队列自动切歌

播放完成后自动播放队列中的下一首：

```typescript
private async onCompleted(): Promise<void> {
  // 1. 标记当前剧集为已播放
  if (this.currentItem !== undefined) {
    await this.feedItemDao.markItemPlayed(this.currentItem.id, PLAY_STATE_PLAYED);
    EventBus.getInstance().publish(EVENT_EPISODE_PLAY_STATE_CHANGED,
      new EpisodePlayStateData(this.currentItem.id, PLAY_STATE_PLAYED));
  }

  // 2. 设置完成日期并重置位置
  if (this.currentMedia !== undefined) {
    await this.feedMediaDao.setPlaybackCompletionDate(this.currentMedia.id, Date.now());
    await this.feedMediaDao.setPosition(this.currentMedia.id, 0);
    EventBus.getInstance().publish(EVENT_PLAYBACK_HISTORY_CHANGED, new Object());
  }

  // 3. 从队列中移除
  if (this.currentItem !== undefined) {
    await this.queueDao.removeFromQueue(this.currentItem.id);
    EventBus.getInstance().publish(EVENT_QUEUE_CHANGED, new Object());
  }

  // 4. 尝试播放下一首
  const nextItem = await this.getNextQueueItem();
  if (nextItem !== null) {
    await this.playEpisode(nextItem.id);
  } else {
    await this.stopInternal(true);
  }
}

// 获取队列中的下一个条目
private async getNextQueueItem(): Promise<FeedItem | null> {
  const queue = await this.queueDao.getQueue();
  if (queue.length === 0) {
    return null;
  }
  // 如果正在播放，找到当前条目之后的下一个
  if (this.currentItem !== undefined) {
    for (let i = 0; i < queue.length; i++) {
      if (queue[i].id === this.currentItem.id && i + 1 < queue.length) {
        return queue[i + 1];
      }
    }
  }
  // 默认返回队列第一个
  return queue[0];
}
```

---

## 位置保存模式

每 5 秒自动保存播放位置到数据库，恢复时可续播：

```typescript
const POSITION_SAVE_INTERVAL_MS: number = 5000;

private positionSaveTimerId: number = -1;

// 开始播放时启动定时器
private startPositionSaveTimer(): void {
  this.stopPositionSaveTimer();
  this.positionSaveTimerId = setInterval((): void => {
    this.savePosition();
  }, POSITION_SAVE_INTERVAL_MS);
}

// 暂停/停止时关闭定时器
private stopPositionSaveTimer(): void {
  if (this.positionSaveTimerId !== -1) {
    clearInterval(this.positionSaveTimerId);
    this.positionSaveTimerId = -1;
  }
}

// 保存当前位置到数据库
private savePosition(): void {
  if (this.currentMedia === undefined) {
    return;
  }
  const pos = AppStorage.get<number>('playbackPosition');
  if (pos !== undefined && pos > 0) {
    this.currentMedia.position = pos;
    this.feedMediaDao.setPosition(this.currentMedia.id, pos);
  }
}

// 调用时机：
// onPlaying() → startPositionSaveTimer()
// onPaused()  → stopPositionSaveTimer() + savePosition()
// stopInternal() → stopPositionSaveTimer() + savePosition()
```

---

## 恢复上次播放

应用启动时恢复上次播放的剧集信息（不自动播放）：

```typescript
async restoreLastPlayedEpisode(): Promise<void> {
  const prefs = PlaybackPreferences.getInstance();
  const mediaId = prefs.getCurrentlyPlayingFeedMediaId();
  if (mediaId <= 0) {
    return;
  }

  const feedMedia = await this.feedMediaDao.getFeedMedia(mediaId);
  if (feedMedia === null) {
    return;
  }

  const item = await this.feedItemDao.getFeedItem(feedMedia.itemId);
  if (item === null) {
    return;
  }

  const feed = await this.feedDao.getFeed(item.feedId);
  const feedTitle = feed !== null ? feed.getDisplayTitle() : '';

  // 填充 AppStorage 供 UI 显示 — 不自动播放
  AppStorage.setOrCreate<string>('currentEpisodeTitle', item.title);
  AppStorage.setOrCreate<string>('currentFeedTitle', feedTitle);
  AppStorage.setOrCreate<number>('currentEpisodeId', item.id);
  AppStorage.setOrCreate<string>('currentCoverUrl', item.getImageLocation());
  AppStorage.setOrCreate<number>('playbackPosition', feedMedia.position);
  AppStorage.setOrCreate<number>('playbackDuration', feedMedia.duration);
  AppStorage.setOrCreate<boolean>('isPlayerVisible', true);
  AppStorage.setOrCreate<number>('playbackSpeed', prefs.getCurrentPlaybackSpeed());
}
```

---

## SleepTimer 完整实现

定时暂停播放，支持设置分钟数、延长、取消：

```typescript
import { EventBus, EVENT_SLEEP_TIMER } from '../common/EventBus';
import { SleepTimerData } from '../common/EventData';

const TICK_INTERVAL_MS: number = 1000;

export class SleepTimer {
  private static instance: SleepTimer | undefined = undefined;
  private timerId: number = -1;
  private endTimeMs: number = 0;
  private running: boolean = false;
  private onTimerExpired: (() => Promise<void>) | undefined = undefined;

  static getInstance(): SleepTimer {
    if (SleepTimer.instance === undefined) {
      SleepTimer.instance = new SleepTimer();
    }
    return SleepTimer.instance;
  }

  setOnTimerExpired(callback: () => Promise<void>): void {
    this.onTimerExpired = callback;
  }

  // 启动定时器
  start(minutes: number): void {
    this.cancel();
    this.endTimeMs = Date.now() + minutes * 60 * 1000;
    this.running = true;
    this.timerId = setInterval((): void => {
      this.tick();
    }, TICK_INTERVAL_MS);
    this.publishState();
  }

  // 延长定时器
  extend(minutes: number): void {
    if (!this.running) {
      this.start(minutes);
      return;
    }
    this.endTimeMs += minutes * 60 * 1000;
    this.publishState();
  }

  // 取消定时器
  cancel(): void {
    if (this.timerId !== -1) {
      clearInterval(this.timerId);
      this.timerId = -1;
    }
    this.running = false;
    this.endTimeMs = 0;
    this.publishState();
  }

  // 获取剩余时间（毫秒）
  getTimeLeft(): number {
    if (!this.running) {
      return 0;
    }
    const left = this.endTimeMs - Date.now();
    return left > 0 ? left : 0;
  }

  isRunning(): boolean {
    return this.running;
  }

  private tick(): void {
    const timeLeft = this.getTimeLeft();
    this.publishState();
    if (timeLeft <= 0) {
      this.cancel();
      if (this.onTimerExpired !== undefined) {
        this.onTimerExpired();
      }
    }
  }

  private publishState(): void {
    EventBus.getInstance().publish(
      EVENT_SLEEP_TIMER,
      new SleepTimerData(this.getTimeLeft(), this.running)
    );
  }
}
```

### 使用方式

在 PlaybackController 构造函数中注册到期回调：

```typescript
private constructor() {
  this.sleepTimer.setOnTimerExpired(async (): Promise<void> => {
    await this.pause();
  });
}
```

---

## PlaybackCallbacks 接口

定义后台播放控制命令的回调接口：

```typescript
export interface PlaybackCallbacks {
  onPlay: () => Promise<void>;
  onPause: () => Promise<void>;
  onSeek: (timeMs: number) => Promise<void>;
  onFastForward: () => Promise<void>;
  onRewind: () => Promise<void>;
  onNext: () => Promise<void>;
  onPrevious: () => Promise<void>;
}
```

---

## PlaybackPreferences 模式

使用 Preferences 存储播放偏好：

```typescript
import { preferences } from '@kit.ArkData';

export class PlaybackPreferences {
  private prefs: preferences.Preferences | undefined = undefined;

  async init(context: Context): Promise<void> {
    this.prefs = await preferences.getPreferences(context, 'playback_prefs');
  }

  getCurrentlyPlayingFeedMediaId(): number {
    return this.prefs?.getSync('currentlyPlayingFeedMediaId', 0) as number;
  }

  getCurrentPlaybackSpeed(): number {
    return this.prefs?.getSync('currentPlaybackSpeed', 1.0) as number;
  }

  async writeMediaPlaying(
    mediaId: number, feedId: number,
    isStream: boolean, isVideo: boolean, speed: number
  ): Promise<void> {
    if (this.prefs === undefined) return;
    this.prefs.putSync('currentlyPlayingFeedMediaId', mediaId);
    this.prefs.putSync('currentlyPlayingFeedId', feedId);
    this.prefs.putSync('currentlyPlayingIsStream', isStream);
    this.prefs.putSync('currentlyPlayingIsVideo', isVideo);
    this.prefs.putSync('currentPlaybackSpeed', speed);
    await this.prefs.flush();
  }

  async writeNoMediaPlaying(): Promise<void> {
    if (this.prefs === undefined) return;
    this.prefs.putSync('currentlyPlayingFeedMediaId', 0);
    await this.prefs.flush();
  }
}
```

---

## 倍速确定逻辑

优先使用 Feed 级别倍速，其次全局倍速：

```typescript
private determineSpeed(): number {
  // Feed 级别倍速优先
  if (this.currentFeed !== undefined) {
    const feedSpeed = this.currentFeed.preferences.feedPlaybackSpeed;
    if (feedSpeed > 0) {
      return this.snapToValidSpeed(feedSpeed);
    }
  }
  // 全局倍速
  const globalSpeed = AppStorage.get<number>('playbackSpeed');
  return this.snapToValidSpeed(globalSpeed !== undefined ? globalSpeed : 1.0);
}
```
