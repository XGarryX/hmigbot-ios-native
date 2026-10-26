# 高级 DAO 模式

> 基于 AntennaPod ArkTS 播客应用实战总结的 4 种 DAO 高级模式：多表 JOIN、ResultSet 安全、批量操作、INSERT ON CONFLICT。
> 源码参考：`entry/src/main/ets/database/FeedItemDao.ets`

---

## 1. 多表 JOIN DAO

播客应用中，`FeedItem`（剧集）需要关联 `FeedMedia`（媒体信息）和 `Feed`（播客源）。
使用 LEFT JOIN 一次查询获取完整数据，避免 N+1 查询。

### SQL 设计 — 列别名区分同名字段

```sql
-- fi.* 取 FeedItem 所有列
-- fm.id AS media_id 避免与 fi.id 冲突
-- f.title AS feed_title 避免与 fi.title 冲突
SELECT fi.*,
  fm.id AS media_id, fm.duration, fm.file_url AS media_file_url,
  fm.download_url AS media_download_url, fm.downloaded AS media_downloaded,
  fm.position, fm.filesize, fm.mime_type, fm.playback_completion_date,
  fm.played_duration, fm.has_embedded_picture, fm.last_played_time,
  f.title AS feed_title, f.custom_title AS feed_custom_title,
  f.image_url AS feed_image_url, f.author AS feed_author
FROM feed_items fi
LEFT JOIN feed_media fm ON fm.feeditem = fi.id
INNER JOIN feeds f ON f.id = fi.feed
WHERE fi.feed = ? ORDER BY fi.pubDate DESC
```

### ArkTS 实现

```typescript
// 文件: database/FeedItemDao.ets (行 13-32, 60-85)
async getFeedItem(itemId: number): Promise<FeedItem | null> {
  const store = this.getStore();
  const resultSet = await store.querySql(
    'SELECT fi.*, fm.id AS media_id, fm.duration, fm.file_url AS media_file_url, ' +
    'fm.download_url AS media_download_url, fm.downloaded AS media_downloaded, ' +
    'fm.position, fm.filesize, fm.mime_type, fm.playback_completion_date, ' +
    'fm.played_duration, fm.has_embedded_picture, fm.last_played_time ' +
    'FROM ' + TABLE_FEED_ITEMS + ' fi ' +
    'LEFT JOIN ' + TABLE_FEED_MEDIA + ' fm ON fm.feeditem = fi.id ' +
    'WHERE fi.id = ?', [itemId]
  );
  try {
    if (resultSet.goToFirstRow()) {
      return this.parseItemWithMedia(resultSet);
    }
    return null;
  } finally {
    resultSet.close();
  }
}

async getFeedItems(feedId: number): Promise<FeedItem[]> {
  const store = this.getStore();
  const resultSet = await store.querySql(
    'SELECT fi.*, fm.id AS media_id, fm.duration, fm.file_url AS media_file_url, ' +
    'fm.download_url AS media_download_url, fm.downloaded AS media_downloaded, ' +
    'fm.position, fm.filesize, fm.mime_type, fm.playback_completion_date, ' +
    'fm.played_duration, fm.has_embedded_picture, fm.last_played_time, ' +
    'f.title AS feed_title, f.custom_title AS feed_custom_title, ' +
    'f.image_url AS feed_image_url, f.author AS feed_author ' +
    'FROM ' + TABLE_FEED_ITEMS + ' fi ' +
    'LEFT JOIN ' + TABLE_FEED_MEDIA + ' fm ON fm.feeditem = fi.id ' +
    'INNER JOIN ' + TABLE_FEEDS + ' f ON f.id = fi.feed ' +
    'WHERE fi.feed = ? ORDER BY fi.pubDate DESC', [feedId]
  );
  try {
    const items: FeedItem[] = [];
    while (resultSet.goToNextRow()) {
      const item = this.parseItemWithMedia(resultSet);
      this.parseFeedFromJoin(resultSet, item);
      items.push(item);
    }
    return items;
  } finally {
    resultSet.close();
  }
}
```

### 分表解析函数

将 ResultSet 解析拆分为三个函数：`parseItemResultSet`（基本字段）、`parseItemWithMedia`（含媒体）、`parseFeedFromJoin`（含 Feed）。

```typescript
// 基本 FeedItem 解析
private parseItemResultSet(resultSet: relationalStore.ResultSet): FeedItem {
  const item = new FeedItem();
  item.id = resultSet.getLong(resultSet.getColumnIndex('id'));
  item.title = this.getStringCol(resultSet, 'title');
  item.pubDate = resultSet.getLong(resultSet.getColumnIndex('pubDate'));
  item.state = resultSet.getLong(resultSet.getColumnIndex('read'));
  item.link = this.getStringCol(resultSet, 'link');
  item.description = this.getStringCol(resultSet, 'description');
  item.feedId = resultSet.getLong(resultSet.getColumnIndex('feed'));
  item.itemIdentifier = this.getStringCol(resultSet, 'item_identifier');
  item.imageUrl = this.getStringCol(resultSet, 'image_url');
  // ... 其余字段
  return item;
}

// FeedItem + FeedMedia（LEFT JOIN）
private parseItemWithMedia(resultSet: relationalStore.ResultSet): FeedItem {
  const item = this.parseItemResultSet(resultSet);

  // 使用别名列 media_id 检测是否有关联的 media
  const mediaIdIdx = resultSet.getColumnIndex('media_id');
  if (!resultSet.isColumnNull(mediaIdIdx)) {
    const media = new FeedMedia();
    media.id = resultSet.getLong(mediaIdIdx);
    media.duration = resultSet.getLong(resultSet.getColumnIndex('duration'));
    media.localFileUrl = this.getStringCol(resultSet, 'media_file_url');
    media.downloadUrl = this.getStringCol(resultSet, 'media_download_url');
    media.downloadDate = resultSet.getLong(resultSet.getColumnIndex('media_downloaded'));
    media.position = resultSet.getLong(resultSet.getColumnIndex('position'));
    media.size = resultSet.getLong(resultSet.getColumnIndex('filesize'));
    media.mimeType = this.getStringCol(resultSet, 'mime_type');
    media.playedDuration = resultSet.getLong(resultSet.getColumnIndex('played_duration'));
    media.hasEmbeddedPicture = resultSet.getLong(resultSet.getColumnIndex('has_embedded_picture')) === 1;
    media.itemId = item.id;
    media.item = item;
    item.media = media;
  }

  return item;
}

// Feed 信息（INNER JOIN feeds）
private parseFeedFromJoin(resultSet: relationalStore.ResultSet, item: FeedItem): void {
  const titleIdx = resultSet.getColumnIndex('feed_title');
  if (titleIdx < 0) {
    return;  // 查询中没有 JOIN feeds 表
  }
  const feed = new Feed();
  feed.id = item.feedId;
  feed.feedTitle = this.getStringCol(resultSet, 'feed_title');
  feed.customTitle = this.getStringCol(resultSet, 'feed_custom_title');
  feed.imageUrl = this.getStringCol(resultSet, 'feed_image_url');
  feed.author = this.getStringCol(resultSet, 'feed_author');
  item.feed = feed;
}
```

### 空值安全的字符串读取

```typescript
private getStringCol(resultSet: relationalStore.ResultSet, colName: string): string {
  const idx = resultSet.getColumnIndex(colName);
  if (resultSet.isColumnNull(idx)) {
    return '';
  }
  return resultSet.getString(idx);
}
```

---

## 2. ResultSet 安全模式

**核心原则**：`ResultSet` 使用后必须 `close()`，使用 `try/finally` 保证即使出错也会关闭。

```typescript
// 正确模式 — try/finally
async getPlayedEpisodeCount(): Promise<number> {
  const store = this.getStore();
  const resultSet = await store.querySql(
    'SELECT COUNT(*) AS cnt FROM ' + TABLE_FEED_ITEMS + ' WHERE read = 1'
  );
  try {
    if (resultSet.goToFirstRow()) {
      return resultSet.getLong(resultSet.getColumnIndex('cnt'));
    }
    return 0;
  } finally {
    resultSet.close();  // 即使 goToFirstRow 或 getLong 抛异常也会执行
  }
}
```

**迭代多行的标准模式**：

```typescript
async getDownloadedItems(): Promise<FeedItem[]> {
  const store = this.getStore();
  const resultSet = await store.querySql(/* SQL */, [/* params */]);
  try {
    const items: FeedItem[] = [];
    while (resultSet.goToNextRow()) {
      const item = this.parseItemWithMedia(resultSet);
      this.parseFeedFromJoin(resultSet, item);
      items.push(item);
    }
    return items;
  } finally {
    resultSet.close();
  }
}
```

**错误示例**（不关闭 ResultSet）：

```typescript
// 错误 — ResultSet 泄漏
async getBadExample(): Promise<number> {
  const resultSet = await store.querySql('SELECT COUNT(*) as cnt FROM items');
  if (resultSet.goToFirstRow()) {
    return resultSet.getLong(0);  // 如果这里抛异常，ResultSet 永不关闭
  }
  resultSet.close();
  return 0;
}
```

---

## 3. 批量操作

使用 `executeSql` 执行不返回结果集的 SQL（UPDATE/DELETE/INSERT），搭配 `?` 占位符防 SQL 注入。

```typescript
// 批量更新 — executeSql
async markAllNewAsUnplayed(): Promise<void> {
  const store = this.getStore();
  await store.executeSql(
    'UPDATE ' + TABLE_FEED_ITEMS + ' SET read = 0 WHERE read = -1'
  );
}
```

**单行更新 — RdbPredicates + ValuesBucket**：

```typescript
async markItemPlayed(itemId: number, played: number): Promise<void> {
  const store = this.getStore();
  const bucket: relationalStore.ValuesBucket = {
    'read': played
  };
  const predicates = new relationalStore.RdbPredicates(TABLE_FEED_ITEMS);
  predicates.equalTo('id', itemId);
  await store.update(bucket, predicates);
}
```

**插入或更新 — 根据 id 判断**：

```typescript
async setFeedItem(item: FeedItem): Promise<number> {
  const store = this.getStore();
  const bucket: relationalStore.ValuesBucket = {
    'title': item.title,
    'pubDate': item.pubDate,
    'read': item.state,
    'link': item.link,
    'description': item.description,
    'feed': item.feedId,
    'item_identifier': item.itemIdentifier,
    'image_url': item.imageUrl,
    // ... 其余字段
  };

  if (item.id > 0) {
    // 已有 id → UPDATE
    const predicates = new relationalStore.RdbPredicates(TABLE_FEED_ITEMS);
    predicates.equalTo('id', item.id);
    await store.update(bucket, predicates);
    return item.id;
  }

  // 无 id → INSERT
  const rowId = await store.insert(TABLE_FEED_ITEMS, bucket);
  item.id = rowId;
  return rowId;
}
```

---

## 4. INSERT ON CONFLICT DO UPDATE

**问题**：`INSERT OR REPLACE` 会删除再插入，导致自增 id 改变。如果其他表有外键引用该 id，关联会断裂。

**解决**：使用 `ON CONFLICT DO UPDATE` 保持 id 稳定。

```typescript
// 方式 1：先查后判断（AntennaPod 实际采用方式）
async setFeedItem(item: FeedItem): Promise<number> {
  if (item.id > 0) {
    // 已有 id → 用 RdbPredicates UPDATE，id 不变
    const predicates = new relationalStore.RdbPredicates(TABLE_FEED_ITEMS);
    predicates.equalTo('id', item.id);
    await store.update(bucket, predicates);
    return item.id;
  }
  // 无 id → INSERT 新行
  return await store.insert(TABLE_FEED_ITEMS, bucket);
}
```

```sql
-- 方式 2：SQL 层 ON CONFLICT（需要唯一约束）
INSERT INTO feeds (download_url, title, image_url, description)
VALUES (?, ?, ?, ?)
ON CONFLICT(download_url) DO UPDATE SET
  title = excluded.title,
  image_url = excluded.image_url,
  description = excluded.description
```

**重复检测 — getFeedItemByGuidOrUrl**：

```typescript
// 通过 GUID 或 media URL 检测重复
async getFeedItemByGuidOrUrl(feedId: number, guid: string, url: string): Promise<FeedItem | null> {
  const store = this.getStore();
  let resultSet: relationalStore.ResultSet;
  if (guid.length > 0) {
    // 优先用 GUID 匹配
    resultSet = await store.querySql(
      'SELECT * FROM ' + TABLE_FEED_ITEMS + ' WHERE feed = ? AND item_identifier = ?',
      [feedId, guid]
    );
  } else {
    // 无 GUID 时用 media URL 匹配
    resultSet = await store.querySql(
      'SELECT fi.* FROM ' + TABLE_FEED_ITEMS + ' fi ' +
      'INNER JOIN ' + TABLE_FEED_MEDIA + ' fm ON fm.feeditem = fi.id ' +
      'WHERE fi.feed = ? AND fm.download_url = ?',
      [feedId, url]
    );
  }
  try {
    if (resultSet.goToFirstRow()) {
      return this.parseItemResultSet(resultSet);
    }
    return null;
  } finally {
    resultSet.close();
  }
}
```

**id 稳定性关系图**：

```
feeds.id ← feed_items.feed (外键)
feed_items.id ← feed_media.feeditem (外键)
feed_items.id ← queue.feeditem (外键)
feed_items.id ← favorites.feeditem (外键)
feed_items.id ← chapters.feeditem (外键)
```

如果 feeds.id 因 INSERT OR REPLACE 变化，feed_items 中所有关联行都会失效。
