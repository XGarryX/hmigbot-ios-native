# TestDataSetup 模板

为 UI 测试预制确定性数据环境。默认策略 `mock`：内存 Mock，Service 读 AppStorage 中预置数据，不写 DB。

---

## 1. 应用入口检测测试模式

在 `entry/src/main/ets/entryability/EntryAbility.ets` 的 `onCreate` 或 `onWindowStageCreate` 中注入（已存在则跳过）：

```typescript
const isTestMode = want?.parameters?.['__test_mode__'] as boolean ?? false
if (isTestMode) {
  AppStorage.setOrCreate('__TEST_MODE__', true)
  const { TestDataSetup } = await import('../test/TestDataSetup')
  await TestDataSetup.injectMockData()
}
```

若入口文件结构差异较大，**不乱改**；返回 `BLOCKERS` 让主线程处理。

---

## 2. TestDataSetup.ets

路径：`entry/src/main/ets/test/TestDataSetup.ets`

```typescript
export class TestDataSetup {
  static async injectMockData(): Promise<void> {
    // 覆盖 AC 索引中所有涉及页面的最小数据集
    const directories = [
      { path: 'DCIM/Camera',   name: 'Camera' },
      { path: 'Pictures/Test', name: 'Test' },
    ]
    const media = [
      { path: 'DCIM/Camera/test_img1.jpg', isFavorite: true,  deletedTimestamp: 0 },
      { path: 'DCIM/Camera/test_img2.jpg', isFavorite: false, deletedTimestamp: 0 },
      { path: 'DCIM/Camera/test_vid1.mp4', isFavorite: false, deletedTimestamp: 0 },
      { path: 'Trash/test_old.jpg',        isFavorite: false, deletedTimestamp: Date.now() / 1000 - 31 * 86400 },
    ]
    AppStorage.setOrCreate('__MOCK_DIRECTORIES__', directories)
    AppStorage.setOrCreate('__MOCK_MEDIA__', media)
    AppStorage.setOrCreate('__MOCK_FAVORITES__', media.filter(m => m.isFavorite))
  }
}
```

**原则**：
- 数量**固定且小**（≤10 条）
- 覆盖各种边界：收藏 / 未收藏 / 已删除 / 普通 / 超期
- 文件名以 `test_` 前缀，避免混淆真实数据
- 通过 `AppStorage.setOrCreate(...)` 注入

---

## 3. Service/Repository 测试模式旁路

找到 AC 索引中 `服务层` 字段引用的类（`MediaRepository` / `FavoritesRepository` / ...），在读取方法开头加：

```typescript
if (AppStorage.get<boolean>('__TEST_MODE__')) {
  const mock = AppStorage.get<XxxModel[]>('__MOCK_XXX__')
  if (mock) return mock
}
```

**不修改生产逻辑**，只在测试模式下旁路。

---

## 输出

- 新增：`entry/src/main/ets/test/TestDataSetup.ets`
- 修改：`EntryAbility.ets`（+ direct-mount 桥，见 `direct-mount-bridge.md`）
- 修改：相关 Service/Repository（条件分支注入）

不写 UI 测试（Step 3 的事）。
