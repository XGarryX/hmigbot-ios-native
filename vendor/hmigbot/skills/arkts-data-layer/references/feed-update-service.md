# Feed 更新服务模式

> 基于 AntennaPod ArkTS 播客应用实战总结的 HTTP -> XML -> DB -> EventBus 刷新管线模式。
> 源码参考：`entry/src/main/ets/network/FeedUpdateService.ets`、`entry/src/main/ets/workers/FeedUpdateWorkAbility.ets`

---

## 整体流水线

```
HTTP GET RSS URL
    ↓
XmlPullParser 解析为 Feed + FeedItem[]
    ↓
DB 合并（检查重复 → 插入新 / 更新旧）
    ↓
EventBus 通知 UI 刷新
```

---

## 1. 订阅新 Feed — subscribeFeed

完整流程：网络检查 → 重复检查 → HTTP 获取 → 解析 → 存储 → 事件通知。

```typescript
// 文件: network/FeedUpdateService.ets
async subscribeFeed(url: string): Promise<number> {
  // 1. 网络检查
  const hasNetwork = await NetworkUtils.isNetworkAvailable();
  if (!hasNetwork) {
    throw new Error('No network connection');
  }

  // 2. 重复检查
  const existing = await this.feedDao.getFeedByUrl(url);
  if (existing !== null) {
    throw new Error('Already subscribed to this feed');
  }

  // 3. HTTP 获取
  const response = await HttpClient.get(url, new Map(), undefined);
  if (response.responseCode !== 200) {
    throw new Error('Failed to fetch feed: HTTP ' + response.responseCode.toString());
  }

  // 处理永久重定向
  let finalUrl = url;
  if (response.redirectUrl.length > 0) {
    finalUrl = response.redirectUrl;
  }

  // 4. XML 解析
  const feed = this.parser.parse(response.body);
  feed.downloadUrl = finalUrl;
  feed.state = FEED_STATE_SUBSCRIBED;

  // 保存条件请求头
  const lastModified = response.headers.get('last-modified');
  if (lastModified !== undefined) {
    feed.lastModified = lastModified;
  }

  // 5. 存储到数据库
  const feedId = await this.feedDao.setFeed(feed);
  await this.saveItems(feed.items, feedId);

  // 6. 事件通知
  EventBus.getInstance().publish(EVENT_SUBSCRIPTION_ADDED,
    new SubscriptionAddedData(feedId));

  return feedId;
}
```

---

## 2. 刷新已有 Feed — refreshFeed

使用条件请求（`If-Modified-Since` / `If-None-Match`）减少流量，合并新剧集。

```typescript
async refreshFeed(feedId: number): Promise<void> {
  const existingFeed = await this.feedDao.getFeed(feedId);
  if (existingFeed === null) { return; }

  // 条件请求 — 304 Not Modified 直接跳过
  const response = await HttpClient.getConditional(
    existingFeed.downloadUrl,
    existingFeed.lastModified,
    this.getEtag(existingFeed),
    credentials
  );

  if (response.responseCode === 304) {
    return;  // 未修改，无需处理
  }

  if (response.responseCode !== 200) {
    existingFeed.lastUpdateFailed = true;
    await this.feedDao.setFeed(existingFeed);
    throw new Error('Failed to refresh feed: HTTP ' + response.responseCode.toString());
  }

  // 处理永久重定向
  if (response.redirectUrl.length > 0) {
    existingFeed.downloadUrl = response.redirectUrl;
  }

  // 解析并更新 Feed 元数据
  const parsedFeed = this.parser.parse(response.body);
  existingFeed.feedTitle = parsedFeed.feedTitle;
  if (parsedFeed.imageUrl.length > 0) {
    existingFeed.imageUrl = parsedFeed.imageUrl;
  }
  // ... 更多字段更新
  existingFeed.lastUpdateFailed = false;
  existingFeed.lastRefreshAttempt = Date.now();
  await this.feedDao.setFeed(existingFeed);

  // 合并新剧集
  let newItemCount = 0;
  for (let i = 0; i < parsedFeed.items.length; i++) {
    const parsedItem = parsedFeed.items[i];
    const mediaUrl = parsedItem.media !== null ? parsedItem.media.downloadUrl : '';

    // 检查重复 — 先用 GUID，再用 media URL
    const existingItem = await this.feedItemDao.getFeedItemByGuidOrUrl(
      feedId, parsedItem.itemIdentifier, mediaUrl
    );

    if (existingItem === null) {
      // 新剧集 — 插入
      parsedItem.feedId = feedId;
      const itemId = await this.feedItemDao.setFeedItem(parsedItem);
      if (parsedItem.media !== null) {
        parsedItem.media.itemId = itemId;
        await this.feedMediaDao.setFeedMedia(parsedItem.media);
      }
      if (parsedItem.chapters.length > 0) {
        await this.chapterDao.setChapters(itemId, parsedItem.chapters);
      }
      newItemCount++;
    } else {
      // 已存在 — 仅更新缺失字段
      if (existingItem.imageUrl.length === 0 && parsedItem.imageUrl.length > 0) {
        existingItem.imageUrl = parsedItem.imageUrl;
        await this.feedItemDao.setFeedItem(existingItem);
      }
      // 修复缺失的 media downloadUrl
      if (parsedItem.media !== null && parsedItem.media.downloadUrl.length > 0) {
        const existingMedia = await this.feedMediaDao.getFeedMediaByItemId(existingItem.id);
        if (existingMedia !== null && existingMedia.downloadUrl.length === 0) {
          existingMedia.downloadUrl = parsedItem.media.downloadUrl;
          await this.feedMediaDao.setFeedMedia(existingMedia);
        }
      }
    }
  }

  EventBus.getInstance().publish(EVENT_FEED_UPDATED, new Object());
}
```

---

## 3. 批量刷新 — refreshAllFeeds

遍历所有订阅的 Feed，逐个刷新，单个失败不影响其他。

```typescript
async refreshAllFeeds(): Promise<void> {
  // 通知 UI 开始刷新（显示加载指示器）
  EventBus.getInstance().publish(EVENT_FEED_UPDATE_RUNNING,
    new FeedUpdateRunningData(true));

  try {
    const feeds = await this.feedDao.getAllFeeds();
    for (let i = 0; i < feeds.length; i++) {
      const feed = feeds[i];
      if (feed.preferences.keepUpdated) {
        try {
          await this.refreshFeed(feed.id);
        } catch (e) {
          // 单个 Feed 失败不影响其他
          hilog.error(DOMAIN, TAG, 'Failed to refresh feed %{public}d', feed.id);
        }
      }
    }
  } finally {
    // 无论成功还是失败，通知 UI 刷新结束
    EventBus.getInstance().publish(EVENT_FEED_UPDATE_RUNNING,
      new FeedUpdateRunningData(false));
  }
}
```

---

## 4. workScheduler 定时触发

使用 HarmonyOS `workScheduler` 实现定时后台刷新。

### WorkSchedulerExtensionAbility 实现

```typescript
// 文件: workers/FeedUpdateWorkAbility.ets
import { WorkSchedulerExtensionAbility, workScheduler } from '@kit.BackgroundTasksKit';

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

### module.json5 注册

```json5
{
  "extensionAbilities": [
    {
      "name": "FeedUpdateWorkAbility",
      "srcEntry": "./ets/workers/FeedUpdateWorkAbility.ets",
      "type": "workScheduler",
      "exported": false
    }
  ]
}
```

### 注册定时任务

```typescript
import { workScheduler } from '@kit.BackgroundTasksKit';

function registerFeedUpdateWork(): void {
  const workInfo: workScheduler.WorkInfo = {
    workId: 1001,
    bundleName: 'com.example.antennapod_arkts',
    abilityName: 'FeedUpdateWorkAbility',
    isPersisted: true,
    repeatCycleTime: 1800000,  // 最短 30 分钟
    isRepeat: true,
    networkType: workScheduler.NetworkType.NETWORK_TYPE_ANY
  };
  workScheduler.startWork(workInfo);
}
```

---

## 重复检测策略

```
解析到的剧集 → getFeedItemByGuidOrUrl(feedId, guid, mediaUrl)
    ├─ guid 非空 → SELECT WHERE feed = ? AND item_identifier = ?
    │   ├─ 找到 → 已存在，跳过或更新缺失字段
    │   └─ 未找到 → 新剧集，插入
    └─ guid 为空 → SELECT WHERE feed = ? AND download_url = ?
        ├─ 找到 → 已存在
        └─ 未找到 → 新剧集
```

**为什么用两种匹配策略**：
- 大多数播客有 `<guid>` 标签，是最可靠的唯一标识
- 少数播客没有 `<guid>`，此时用媒体文件的 `download_url` 作为替代标识
- 这与 Android 版 AntennaPod 的 `FeedItemDuplicateGuesser` 逻辑一致
