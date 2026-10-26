# RdbStore 与 DAO 完整模式

> 本文件覆盖 HarmonyOS 关系型数据库（relationalStore）的完整使用模式，从初始化到 CRUD，替代 Android Room 的全部功能。

---

## RdbStore 单例初始化

```typescript
import { relationalStore } from '@kit.ArkData'

export class AppDatabase {
  private static instance: AppDatabase | null = null
  private rdbStore: relationalStore.RdbStore | null = null

  static getInstance(): AppDatabase {
    if (!AppDatabase.instance) {
      AppDatabase.instance = new AppDatabase()
    }
    return AppDatabase.instance
  }

  async init(context: Context): Promise<void> {
    this.rdbStore = await relationalStore.getRdbStore(context, {
      name: 'app.db',
      securityLevel: relationalStore.SecurityLevel.S1  // S1=低安全，S2=中，S3=高，S4=极高
    })
    await this.createTables()
  }

  private async createTables(): Promise<void> {
    const store = this.getStore()
    await store.executeSql(CREATE_MEDIA_TABLE)
    await store.executeSql(CREATE_MEDIA_INDEX)
    // 添加更多建表语句...
  }

  getStore(): relationalStore.RdbStore {
    if (!this.rdbStore) throw new Error('Database not initialized. Call init() first.')
    return this.rdbStore
  }
}
```

**SecurityLevel 选择指南**：

| 级别 | 适用数据 | 示例 |
|------|---------|------|
| S1 | 公开数据 | 新闻缓存、配置 |
| S2 | 内部数据 | 用户偏好、搜索历史 |
| S3 | 敏感数据 | 聊天记录、个人信息 |
| S4 | 关键数据 | 密钥、认证凭据 |

---

## 建表 SQL 模板

```typescript
// 完整建表（含 NOT NULL、DEFAULT、自增主键）
const CREATE_MEDIA_TABLE = `CREATE TABLE IF NOT EXISTS media (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT NOT NULL,
  full_path TEXT NOT NULL,
  parent_path TEXT NOT NULL,
  last_modified INTEGER NOT NULL DEFAULT 0,
  date_taken INTEGER NOT NULL DEFAULT 0,
  size INTEGER NOT NULL DEFAULT 0,
  type INTEGER NOT NULL DEFAULT 0,
  video_duration INTEGER NOT NULL DEFAULT 0,
  is_favorite INTEGER NOT NULL DEFAULT 0,
  deleted_ts INTEGER NOT NULL DEFAULT 0,
  media_store_id INTEGER NOT NULL DEFAULT 0
)`

// 唯一索引（替代 Room @Entity(indices)）
const CREATE_MEDIA_INDEX =
  'CREATE UNIQUE INDEX IF NOT EXISTS idx_media_full_path ON media(full_path)'

// 普通索引（加速查询）
const CREATE_PARENT_INDEX =
  'CREATE INDEX IF NOT EXISTS idx_media_parent ON media(parent_path)'
```

**从 Room @Entity 转换规则**：

| Room 注解 | SQL 写法 |
|----------|---------|
| `@PrimaryKey(autoGenerate = true)` | `INTEGER PRIMARY KEY AUTOINCREMENT` |
| `@ColumnInfo(name = "xxx")` | 直接用字段名 |
| `@Entity(indices = [@Index(value = ["path"], unique = true)])` | `CREATE UNIQUE INDEX ...` |
| `@TypeConverter` | 手动在 DAO 中转换 |

---

## ResultSet 解析

**标准解析模式**：

```typescript
private parseResultSet(rs: relationalStore.ResultSet): Medium {
  const medium = new Medium()
  medium.id = rs.getLong(rs.getColumnIndex('id'))
  medium.filename = rs.getString(rs.getColumnIndex('filename'))
  medium.fullPath = rs.getString(rs.getColumnIndex('full_path'))
  medium.parentPath = rs.getString(rs.getColumnIndex('parent_path'))
  medium.lastModified = rs.getLong(rs.getColumnIndex('last_modified'))
  medium.dateTaken = rs.getLong(rs.getColumnIndex('date_taken'))
  medium.size = rs.getLong(rs.getColumnIndex('size'))
  medium.type = rs.getLong(rs.getColumnIndex('type'))
  medium.videoDuration = rs.getLong(rs.getColumnIndex('video_duration'))
  medium.isFavorite = rs.getLong(rs.getColumnIndex('is_favorite')) !== 0
  medium.deletedTs = rs.getLong(rs.getColumnIndex('deleted_ts'))
  return medium
}
```

**遍历 ResultSet**：

```typescript
async queryAll(): Promise<Medium[]> {
  const store = this.getStore()
  const resultSet = await store.querySql('SELECT * FROM media WHERE deleted_ts = 0')
  const results: Medium[] = []
  while (resultSet.goToNextRow()) {
    results.push(this.parseResultSet(resultSet))
  }
  resultSet.close()  // 必须关闭！否则资源泄漏
  return results
}
```

**关键规则**：
- ✅ `resultSet.close()` 必须在每个查询方法中调用
- ✅ 使用 `goToNextRow()` 遍历（不是 `goToFirstRow` + `goToNextRow` 组合）
- ✅ `getColumnIndex()` 获取列索引，不要硬编码数字
- ❌ 不要在 try 块外使用 resultSet（可能已关闭）

---

## DAO 标准 CRUD 方法

```typescript
export class MediumDao {
  private getStore(): relationalStore.RdbStore {
    return AppDatabase.getInstance().getStore()
  }

  // === 查询 ===
  async getByPath(path: string): Promise<Medium[]> {
    const store = this.getStore()
    const resultSet = await store.querySql(
      'SELECT * FROM media WHERE deleted_ts = 0 AND parent_path = ? ORDER BY last_modified DESC',
      [path]
    )
    const results: Medium[] = []
    while (resultSet.goToNextRow()) {
      results.push(this.parseResultSet(resultSet))
    }
    resultSet.close()
    return results
  }

  async getById(id: number): Promise<Medium | null> {
    const store = this.getStore()
    const resultSet = await store.querySql(
      'SELECT * FROM media WHERE id = ?', [id]
    )
    let result: Medium | null = null
    if (resultSet.goToNextRow()) {
      result = this.parseResultSet(resultSet)
    }
    resultSet.close()
    return result
  }

  // === 插入 ===
  async insert(medium: Medium): Promise<number> {
    const store = this.getStore()
    const bucket: relationalStore.ValuesBucket = {
      'filename': medium.filename,
      'full_path': medium.fullPath,
      'parent_path': medium.parentPath,
      'last_modified': medium.lastModified,
      'date_taken': medium.dateTaken,
      'size': medium.size,
      'type': medium.type,
      'video_duration': medium.videoDuration,
      'is_favorite': medium.isFavorite ? 1 : 0,
      'deleted_ts': medium.deletedTs,
    }
    return await store.insert('media', bucket)
  }

  // === 更新 ===
  async updateFavorite(id: number, isFavorite: boolean): Promise<number> {
    const store = this.getStore()
    const bucket: relationalStore.ValuesBucket = {
      'is_favorite': isFavorite ? 1 : 0
    }
    const predicates = new relationalStore.RdbPredicates('media')
    predicates.equalTo('id', id)
    return await store.update(bucket, predicates)
  }

  // === 删除（软删除）===
  async softDelete(id: number): Promise<number> {
    const store = this.getStore()
    const bucket: relationalStore.ValuesBucket = {
      'deleted_ts': Date.now()
    }
    const predicates = new relationalStore.RdbPredicates('media')
    predicates.equalTo('id', id)
    return await store.update(bucket, predicates)
  }

  // === 删除（硬删除）===
  async hardDelete(id: number): Promise<number> {
    const store = this.getStore()
    const predicates = new relationalStore.RdbPredicates('media')
    predicates.equalTo('id', id)
    return await store.delete(predicates)
  }

  // === 批量插入/更新 ===
  async upsertBatch(items: Medium[]): Promise<void> {
    const store = this.getStore()
    for (const item of items) {
      await store.executeSql(
        `INSERT OR REPLACE INTO media
        (filename, full_path, parent_path, last_modified, date_taken, size, type, video_duration, is_favorite, deleted_ts)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [item.filename, item.fullPath, item.parentPath, item.lastModified,
         item.dateTaken, item.size, item.type, item.videoDuration,
         item.isFavorite ? 1 : 0, item.deletedTs]
      )
    }
  }

  private parseResultSet(rs: relationalStore.ResultSet): Medium {
    const medium = new Medium()
    medium.id = rs.getLong(rs.getColumnIndex('id'))
    medium.filename = rs.getString(rs.getColumnIndex('filename'))
    medium.fullPath = rs.getString(rs.getColumnIndex('full_path'))
    medium.parentPath = rs.getString(rs.getColumnIndex('parent_path'))
    medium.lastModified = rs.getLong(rs.getColumnIndex('last_modified'))
    medium.dateTaken = rs.getLong(rs.getColumnIndex('date_taken'))
    medium.size = rs.getLong(rs.getColumnIndex('size'))
    medium.type = rs.getLong(rs.getColumnIndex('type'))
    medium.videoDuration = rs.getLong(rs.getColumnIndex('video_duration'))
    medium.isFavorite = rs.getLong(rs.getColumnIndex('is_favorite')) !== 0
    medium.deletedTs = rs.getLong(rs.getColumnIndex('deleted_ts'))
    return medium
  }
}
```

---

## INSERT OR REPLACE vs ON CONFLICT DO UPDATE

**关键区别**：

| 方式 | 行为 | id 变化 | 适用场景 |
|------|------|--------|---------|
| `INSERT OR REPLACE` | 先删旧行再插新行 | ✅ 会变（新自增值） | id 不重要的缓存数据 |
| `INSERT ... ON CONFLICT DO UPDATE` | 原地更新 | ❌ 不变 | id 作为外键引用时 |

```typescript
// INSERT OR REPLACE — id 会变化！
await store.executeSql(
  'INSERT OR REPLACE INTO media (full_path, filename, last_modified) VALUES (?, ?, ?)',
  [path, name, modified]
)

// ON CONFLICT DO UPDATE — id 不变（推荐）
await store.executeSql(
  `INSERT INTO media (full_path, filename, last_modified)
   VALUES (?, ?, ?)
   ON CONFLICT(full_path) DO UPDATE SET
   filename = excluded.filename,
   last_modified = excluded.last_modified`,
  [path, name, modified]
)
```

**选择指南**：
- 缓存数据（如媒体列表）→ `INSERT OR REPLACE` 简单直接
- 需要 id 稳定（如外键关联、收藏记录）→ `ON CONFLICT DO UPDATE`
- 不确定时 → 用 `ON CONFLICT DO UPDATE` 更安全

---

## Preferences 值类型限制

Preferences 只支持以下值类型：

| 类型 | 示例 |
|------|------|
| `number` | `42`, `3.14` |
| `string` | `'hello'` |
| `boolean` | `true`, `false` |
| `number[]` | `[1, 2, 3]` |
| `string[]` | `['a', 'b']` |
| `boolean[]` | `[true, false]` |

**不支持**：对象、Set、Map、嵌套数组

**存储复杂类型的解决方案**：

```typescript
// Set<string> → JSON 序列化
get pinnedFolders(): Set<string> {
  const json = this.getString(PINNED_FOLDERS, '[]')
  try {
    return new Set(JSON.parse(json) as string[])
  } catch {
    return new Set()
  }
}

async setPinnedFolders(v: Set<string>): Promise<void> {
  await this.putString(PINNED_FOLDERS, JSON.stringify(Array.from(v)))
}

// 对象 → JSON 序列化
async saveUserProfile(profile: UserProfile): Promise<void> {
  await this.putString('user_profile', JSON.stringify(profile))
}
```
