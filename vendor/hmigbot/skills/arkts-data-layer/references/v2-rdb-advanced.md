# RDB 进阶：事务 / 批量 / 谓词 / 版本升级 / 加密

> 补 `rdbstore-dao-patterns.md`（基础 CRUD）之外的关键 RDB 能力。**经 harmony-docs（快照 2026-05-24）核验**，全部用当前 `@ohos.data.relationalStore`（**不用**已废弃的 `@ohos.data.rdb`）。
> 导入：`import { relationalStore } from '@kit.ArkData'`。

## 1. 事务（多行写入必用 —— 原子 + 快）

逐行 `insert`/`executeSql` 在多行写入时**慢（每行 fsync）且非原子**（中途失败留脏数据）。用事务包裹：

```typescript
store.beginTransaction()
try {
  store.batchInsert('feed_item', rows)
  store.executeSql('UPDATE feed SET unread = unread + ?', [rows.length])
  store.commit()
} catch (e) {
  store.rollBack()        // 失败回滚，保持一致
  throw e
}
```
> API 14+ 另有对象式 `store.createTransaction()` 返回 `Transaction`（带 insert/update/delete/commit/rollback），适合异步细粒度控制——详见官方 `Interface (Transaction)`。

## 2. batchInsert（批量插入，一次原生调用）

```typescript
const rows: relationalStore.ValuesBucket[] = items.map(i => ({ id: i.id, title: i.title, read: 0 }))
const n: number = await store.batchInsert('feed_item', rows)   // 远快于循环 insert
```
签名：`batchInsert(table: string, values: Array<ValuesBucket>): Promise<number>`。

## 3. RdbPredicates 全算子（替代手写 WHERE，防注入）

```typescript
const p = new relationalStore.RdbPredicates('feed_item')
p.equalTo('read', 0).and().like('title', '%news%')
  .orderByDesc('pubdate').limitAs(20).offsetAs(0)
const rs = await store.query(p, ['id', 'title', 'pubdate'])
```
常用算子：`equalTo / notEqualTo`、`greaterThan(OrEqualTo) / lessThan(OrEqualTo)`、`like / glob`、`between / notBetween`、`in / notIn`、`isNull / isNotNull`、`beginsWith / endsWith / contains`、逻辑 `and / or / beginWrap / endWrap`、`orderByAsc / orderByDesc`、`groupBy / having / distinct`、`limitAs / offsetAs`。**优先用谓词，不要拼 SQL 字符串**（注入风险 + 无类型）。

## 4. 版本升级 / 表结构迁移

`store.version` 是可读写的 schema 版本号。打开后比对版本，按需建表 / `ALTER`：

```typescript
const store = await relationalStore.getRdbStore(ctx, {
  name: 'app.db', securityLevel: relationalStore.SecurityLevel.S1
})
if (store.version === 0) {                                  // 全新库
  store.executeSql('CREATE TABLE IF NOT EXISTS feed_item(id TEXT PRIMARY KEY, title TEXT, read INTEGER)')
  store.version = 1
}
if (store.version < 2) {                                    // v1 → v2：加列
  store.executeSql('ALTER TABLE feed_item ADD COLUMN author TEXT')
  store.version = 2
}
```
> 这是 Room `Migration` 的等价物。漏写迁移 = 老用户升级后查询崩溃，务必每次改表都升 version + 写迁移分支。

## 5. 加密（敏感库）

```typescript
const store = await relationalStore.getRdbStore(ctx, {
  name: 'secure.db',
  securityLevel: relationalStore.SecurityLevel.S3,
  encrypt: true                 // 数据库文件加密；与 securityLevel 是两回事，敏感数据两者都设
})
```

## 关键规则

- **多行写入 = 事务**（beginTransaction/commit/rollBack）+ `batchInsert`，不要循环单插。
- **查询用 RdbPredicates**，不拼 SQL 字符串（防注入）。
- **改表必升 `store.version` + 写迁移分支**，否则老用户升级崩溃。
- **`securityLevel` ≠ 加密**：敏感库要显式 `encrypt: true`。
- 同步打开（API 24+）：`relationalStore.getRdbStoreSync(ctx, config)`。
- 备份/恢复：`store.backup(path)` / `store.restore(path)`。
