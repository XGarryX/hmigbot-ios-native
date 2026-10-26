# 为什么能力层级（feature_tree）≠ fact-tree 的导航边/组件父子

A2H 的 `android-source-analysis` 产 **feature_tree**（L1-L6 能力层级树）。本 skill 借它的方法论，但**绝不能直接套 L1-L6 当 fact-tree 的导航/组件**。三者是不同「形状 + 高度」的关系：

| | 能力层级（L1-L6） | 导航边（page→page） | 组件父子 |
|---|---|---|---|
| 图形 | 树（单父） | **有向图**（扇入/回边/环） | 树（布局嵌套） |
| 嵌套基准 | 能力/语义 | 页面运行时可达 | UI 渲染层 |
| 边的含义 | "是子能力" | "点击跳转到" | "渲染包含" |
| 带 type/trigger/target | ❌ | ✅ | ✅ |

## 实测反例（Jetsnack）
1. **扇入丢失**：详情页真实被 Feed/Search/Cart **3 个入口**跳入。feature_tree 是单父树，只能把"零食详情"挂在"首页"下一次；其 `cross_reference_map` 实测只记 1 条且**主动声明放弃**购物车→详情（"一个注册表条目只属一个原始域"）。→ fact-tree 必须建全 3 条 inbound（SKILL Phase2 铁律 A）。
2. **大量层级父子不是导航**：`排序 > 按评分排序`=选项；`购物车 > 增减数量`=动作；`首页 > 筛选`在 Compose 里是 overlay 不是页面。→ 只有"子节点是独立屏"的层级边才可能对应导航边，且要重新判定。
3. **能力叶子没有组件信息**：feature_tree 叶子字段只有 `name/level/source_file`，**没有 type/triggers/navigation.to_page**。→ 组件必须从源码控件（Button/clickable/Slider…）单独抽，带全 schema §七 字段。

## 正确做法
- **不要**从 feature_tree 反推导航边或组件树。
- feature_tree 的价值是**语义层**（purpose / 功能聚类），正好是 fact-tree 里留 `null` 给 `app-relationship-tree` 补的部分。
- 若同目录恰有 A2H 的 `feature_tree.json`，**仅可**借它给 `features[]` 做聚类种子（Phase 4），不可借它当 `flow_graph` 或 `components`。
