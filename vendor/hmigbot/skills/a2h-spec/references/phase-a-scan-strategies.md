<!-- when: Phase A Step A2b LLM 语义分析、做扩展分析项时加载 -->
<!-- topics: 动态菜单, BottomSheet, RecyclerView item layout, Fragment TAG, 导航模式, meta.json 字段 -->

# Phase A 扩展分析项（增强 UI 还原精度）

对每个 Activity/Fragment 额外执行以下分析（结果写入 meta.json 对应字段）：

```
├─ 动态菜单分析:
│   ├─ BottomNavigationView.getMenu().add() → 运行时动态添加的菜单项
│   ├─ menu.clear() + 循环 add → 可配置菜单（记录 max items、overflow 逻辑）
│   ├─ setOnItemSelectedListener → 菜单点击事件处理
│   ├─ ListPopupWindow / PopupMenu → overflow "More" 弹窗（记录宽度、Gravity、内容项）
│   └─ onCreateOptionsMenu() → inflates res/menu/*.xml（记录到 menu_sources）
│
├─ BottomSheet 行为分析:
│   ├─ BottomSheetBehavior 子类 → 自定义行为类名（如 LockableBottomSheetBehavior）
│   ├─ setPeekHeight() / @dimen/ 引用 → peek 高度
│   ├─ setState() 调用点 → 状态切换逻辑（COLLAPSED/EXPANDED/HIDDEN）
│   ├─ setHideable() → 是否可隐藏
│   └─ addBottomSheetCallback() → 滑动回调（记录 onSlide 行为）
│
├─ RecyclerView Adapter item layout 追踪:
│   ├─ Adapter.onCreateViewHolder() → inflate(R.layout.xxx) → 记录 item layout 名
│   ├─ getItemViewType() → 多类型 item layout 映射
│   └─ 记录到 meta.json.recycler_item_layouts
│
├─ Fragment TAG 常量提取:
│   ├─ 扫描 public static final String TAG = "xxx"
│   ├─ 记录 Fragment 类名 → TAG 常量值的映射
│   └─ 后续所有导航引用必须使用 TAG 而非类名（如 InboxFragment.TAG = "NewEpisodesFragment"）
│
└─ 导航模式分析:
    ├─ DrawerLayout.setDrawerLockMode() → drawer 是否被锁定及条件
    ├─ BottomNavigationView.setVisibility(GONE/VISIBLE) → 底部导航显隐条件
    └─ 互斥判断：底部导航启用时 drawer 锁定，drawer 启用时底部导航隐藏
```

对每个页面记录：
- Activity/Fragment 类名
- layout XML 文件路径列表（`layout_sources`）
- 样式/主题文件路径列表（`style_sources`）：从 layout XML 的 `style="@style/xxx"` 和 Activity 的 `android:theme` 溯源
- Fragment 加载关系
- 导航关系（跳转目标 + 触发方式）
- 可交互元素（按钮、列表项、输入框等）
- menu 相关文件路径列表（`menu_sources`）：从 onCreateOptionsMenu 和 layout XML 的 app:menu 属性溯源
- Fragment TAG 常量映射（`fragment_tags`）：{类名: TAG值}
- 动态菜单配置（`dynamic_menus`）：底部导航的 buildMenu 逻辑、max items、overflow 弹窗类型
- BottomSheet 配置（`bottom_sheet_config`）：行为类、peek 高度、状态列表、是否可锁定
- RecyclerView item layouts（`recycler_item_layouts`）：adapter 类名 → item layout 列表映射
- 导航模式（`navigation_mode`）：底部导航和 drawer 的互斥/共存关系
