<!-- when: Phase C Step C2 生成 feature-index.md 时加载 -->
<!-- topics: feature-index, 领域模型, 功能清单, 依赖图, 拓扑排序 -->

# feature-index.md 模板

必填字段：领域模型概览（核心实体 + 关系）、功能清单表（ID / 功能 / 优先级 / 依赖 / 涉及页面 / 状态）、依赖图、执行顺序（拓扑排序）。

> **状态列生命周期**（feature 级产物状态的**唯一账本**，活过 plan 重排）：`pending → implemented → verified`。写者 = a2h-execute（group-closer 在组 brief 对应 slice 小节 PASS 时经 writeback manifest 翻 `implemented`，与 ui-manifest 页面回写同处；FV 通过后翻 `verified`）；读者 = execute resume / 部分执行、gate 摘要、a2h-verify 范围选择。spec 侧只初始化为 `pending`，此后不改写本列。

```markdown
# Feature Index

## 领域模型概览
核心实体: Feed, FeedItem, FeedMedia, Queue, DownloadTask, PlaybackState
关系: Feed 1:N FeedItem 1:1 FeedMedia, Queue 1:N FeedItem

## 功能清单
| ID | 功能 | 优先级 | 依赖 | 涉及页面 | 状态 |
|----|------|--------|------|---------|------|
| F001 | 音频播放 | P0 | base | AudioPlayerPage, MainPage(MiniBar) | pending |
| F002 | 订阅管理 | P0 | base | SubscriptionPage, FeedDetailPage | pending |
| F003 | 下载管理 | P1 | F001 | DownloadsPage | pending |
| ... |

## 依赖图
base → F001(播放) → F003(下载)
base → F002(订阅) → F005(搜索)
base → F004(队列) → F001(播放)
F001 + F002 → F007(统计)

## 执行顺序（拓扑排序）
1. feature-base (水平)
2. F001, F002 (可并行)
3. F004 (依赖 F001)
4. F003, F005 (可并行)
5. F006, F007 (可并行)
```

功能拆分原则：
- 一个功能 = 一个用户可感知的完整能力（如"播放"、"订阅"、"下载"）
- 功能之间通过明确接口（Service 方法、Event）解耦
- 每个功能关联到它涉及的页面（来自 Phase B 的页面清单）
- 优先级与页面优先级对齐：P0 页面的核心功能 = P0 功能
- 后端向功能优先对照 `api-inventory.json` 的 `feature_candidates` 聚类结果（见 C2-pre），确保按 API 路径前缀划分的功能边界不被遗漏
