# 功能点深度提取方法论（我们自有，源自并改进 A2H 开放方法论）

> 本文件是 S3「生成 functional_points.json」的**权威规则**。它是 LLM 主提取器的工作手册。
> 角色定位（对齐 A2H，纠正早期版本的颠倒）：
> - **LLM 读完整源码 = 主提取器**（决定有哪些功能点、叫什么、挂哪）。
> - **control_census.json = 确定性地板 + 省 token 素材**（XML 控件直接采用；代码交互给候选种子）。census **不是**上限——LLM 要在它之上展开 dialog 选项 / context_menu 各项 / 枚举值等。

---

## 0. 输入
- `control_census.json`：XML 控件（带真 resource-id）+ 代码交互候选（dialog/context_menu/bottom_sheet/code_click...，带 source_file + 锚点）。
- `strings_catalog.json`：`strings{key→value}` + `string_arrays{name→[items]}`。**所有 R.string / @string 必须查表成语义名**。
- `source_index.json`：preference/menu/enum/dialog/bottomsheet/programmatic 文件清单 → 定向读取，不盲扫。
- `spec_oracle.json`（可选）：features 验收标准 + page 导航关系 → 填 `expected`（见 SKILL S3）。
- Android 源码：按下方优先级**定向读取**。

## 1. source_section 全类目（必须产全，不止 XML 那 5 类）
`preference · enum_options · menu_xml · menu_programmatic · context_menu · spinner · seekbar · fab · toggle · dialog · bottom_sheet · drawer · tab_pager · custom_view · compose · search · navigation · intent_filter · broadcast_receiver`

> census 已把 XML 类(view→toggle/menu_item→menu_xml/menu_overflow/preference/enum_options)和代码类候选(dialog/context_menu/bottom_sheet/code_click/menu_programmatic/spinner/seekbar/custom_view)枚举出来。LLM 据此**逐项落地 + 展开子项**。

## 2. 提取映射表（源码内容 → 功能点）
| 源码内容 | source_section | 展开规则 |
|---------|---------------|---------|
| SwitchPreference | preference | 单节点（**禁止**拆"开/关"两节点） |
| ListPreference / MultiSelect | preference + **enum_options** | 标题=1 节点；`entries` 数组**每个值都展开**为独立子节点（查 arrays_catalog）|
| EditText/SeekBarPreference | preference | 单节点 |
| PreferenceCategory | （分组容器） | 不独立提取，只作 feature_path 分组 |
| PreferenceScreen 嵌套 | preference | 子设置页入口节点 |
| Menu item showAsAction=always/ifRoom | menu_xml | 可见操作，直接挂页面 |
| Menu item showAsAction=never | menu_xml | 溢出操作，**必经"更多"中间层** |
| onCreateOptionsMenu menu.add() | menu_programmatic | 编程式操作，逐项 |
| onCreateContextMenu / setOnLongClickListener | context_menu | 长按操作，**直接挂宿主页面**（禁止"列表项"伪容器）|
| AlertDialog/MaterialAlertDialogBuilder | dialog | 按钮组(确定/取消/重置) + `setSingleChoiceItems`/`setItems` **每个选项**都提取 |
| BottomSheet(Dialog/Behavior) | bottom_sheet | 容器 + **内部每个按钮/菜单项**逐项提取 |
| FloatingActionButton | fab | 强制扫描（layout + 代码 findViewById/ViewBinding）|
| Switch/ToggleButton/setOnCheckedChangeListener | toggle | 二态切换单节点 |
| Spinner | spinner | 控件 + adapter/entries **每个选项**子节点 |
| SeekBar(非 Preference) | seekbar | 数值调节节点（max/min/progress）|
| Enum 类 | enum_options | **每个枚举常量**独立节点（类名去后缀分词作分组）|
| SearchView/queryTextListener | search | 入口 + onQueryTextSubmit/Change/suggestion 各回调如有可见行为则提取 |
| Drawer/NavigationView | drawer | 每个导航项 |
| TabLayout/ViewPager | tab_pager | 每个 Tab |
| @Composable/NavHost/composable() | compose | 页面 + 导航目标 |
| SurfaceView/TextureView/onTouch 自定义绘制 | custom_view | 用户可见交互（标准控件不归此类）|
| 代码级参数键(SettingKeys/ParameterManager) | custom_view | 每个键；有离散值则每值一子节点 |

## 3. 读取优先级（高产出先读，定向不盲扫）
1. **Preference XML**（最高产；ListPreference 的 entries 必须全展开）
2. **strings_catalog**（查表，不重复读 strings.xml）
3. **Menu XML**（按域；showAsAction 决定可见/溢出）
4. **编程式菜单**（onCreateOptionsMenu/onCreateContextMenu 方法体）
5. **Enum 类**（每常量一节点）
6. **Dialog/BottomSheet**（按钮 + 选项 + 内部操作逐项）
7. **FAB / 独立按钮 / Spinner / 页面级 SeekBar**（强制 Grep，不依赖索引）
8. **导航组件**（Drawer/Tab/ViewPager/Compose）
9. **自定义控件**（SurfaceView/onTouch）
10. **Search 回调**（逐个回调检查）
11. **Fragment/Activity 导航流**（fragmentTransaction/startActivity → 完整链）
12. **★事件监听器全量兜底（必跑，不可跳过）**：见下。

## 4. ★事件监听器全量兜底（A2H 抓到代码级交互的关键，我们用 census.code_* 候选驱动）
census 的代码扫描已把这些监听器站点枚举为候选（source_section ∈ {code_click, context_menu, toggle, spinner, seekbar, custom_view, dialog, menu_programmatic, bottom_sheet}）。对**每个 code_* 候选**：
1. 读 `source_file` 的 `attrs.line` 附近代码，判断该监听器对应的用户可见控件/操作。
2. 已被前 11 步覆盖 → 跳过（避免重复）。
3. 未覆盖 → 落一条 functional_point，归入合适 source_section，`raw_identifier` = census 的代码锚点（如 `butPlay.setOnClickListener`）。
4. 真无用户可见行为（纯内部）→ 丢弃并在日志记原因。

> 监听器是 Android 交互的通用基础设施——任何可交互控件都要注册监听器。扫监听器 = 发现一切可交互控件的兜底。这条堵住了"XML 看不见的代码交互"。

## 5. 命名 / 路径 / 深度
- **name**：去 `Button/Item/Preference/Fragment/Activity` 后缀；`title_ref`/R.string → strings_catalog 查表；CamelCase 分词；描述"有什么"不描述"怎么做"；不重复父节点语义；禁加"页/操作/管理/区块"后缀；溢出统一叫"更多"。
- **feature_path**：`L1>L2>...`（`>` 分隔无类名）。层级参考已有 fact-tree / spec/baseline/ui 页面归属 / 源码包结构。`menu_overflow`/`showAsAction=never` 必经"更多"。
- **source_file**：源码根起的相对路径（必含 `/`，非空——它会成为 android_anchor.decl_file）。
- **raw_identifier**：XML 控件 = census 的真 resource-id（grounding 定位命门）；代码交互 = 代码锚点（同 A2H 哲学）。
- **depth**：= feature_path 段数 + 1。
- **enum 零缺失**：ListPreference entries / enum 常量 / Spinner 选项 / Dialog 选项**每个值都要独立节点**，缺一不可。

## 5.5 verify_by — 事务型 oracle 路由（Q2；**app 无关判据，禁写死"如果是登录"**）
每个 point 判一个 `verify_by`，决定下游 grounding / dual-oracle **用哪种方式判它对不对**：

- **`landing`（默认，绝大多数）**：单点该控件、看**当场落地**（跳 X 页 / 弹 X 窗 / toast / 停原地）即可判对错。导航、开关、清空、打开弹窗、切筛选——这类单点就露出正确性。
- **`outcome`**：**必须把事务用真输入走完、看最终状态变化**才判得出对错。判据（app 无关，读 handler 定）——三条**全中**才标 outcome：
  1. handler 要等一个**改持久态的后端往返**才算完成（写 auth/session/账号/订单/服务端记录）；
  2. "正确"表现为**结果态变化**（已登录 / 已下单 / 已提交），不是一次导航或 toast；
  3. 它的**校验门禁**（空输入拦截 / 勾选拦截 / 参数校验）单独看**区分不了好坏实现**——坏实现照样门禁正常。
  典型（任何 app 通用）：登录 / 注册 / 登出 / 注销 / 绑手机 / 支付 / 下单 / 会持久化的提交。
  - **`outcome_scenario`**：完成该事务的配方名（`spec/scenarios/<name>.yaml`），按事务语义取（登录→`login`、支付→`pay`…）。下游据此调 `verify_outcome.py` 走完事务。
  - **完不成的事务照标 landing**：三方 OAuth（微信/支付宝/Apple 登录）等**需外部授权、自动化走不完**的，保持 `landing` 并在 name/note 标"需外部授权"——下游退 low_confidence，不硬撑（这是自动化天花板，不是漏标）。

## 6. 排除（实现细节，跳过）
DBReader/DBWriter、Adapter、网络协议实现、Util 类、test/、build config、图片加载配置、Service stub、日志/崩溃上报、框架胶水、纯 layout（仅辅助理解）。判据：描述"代码如何实现"→ 跳；描述"用户能做/配/感知"→ 提。

## 7. 相对 A2H 的改进（我们超越的地方）
1. **每个功能点都配 expected**（S4 1:1 产 intent）——A2H 仅 75% registry 能 join 到 intent。
2. **expected 升级源**：features 验收标准 + page 导航关系 > test_intents 静态种子。
3. **raw_identifier 更稳**：XML 控件给真 resource-id（A2H 常给代码路径），grounding 定位更准；代码交互才退化为锚点。
4. **完备性兜底透明**：census(XML+代码) + validate_contract 全是开放 Python，可审计；A2H 的 verifier 是封装二进制。
5. **确定性地板可量化**：census 给出"应覆盖控件数"，C5 直接算覆盖率、列 uncovered，漏没漏一目了然。
6. **spec 双向交叉校验**：源码主推导 vs a2h-spec 独立第二来源对账（spec_crosscheck.py），两个独立推导互相挑错——**spec 当校验器不当脚手架**（避免继承 spec 盲区），源码始终是真值。A2H 单源生成、无此回路。
