# 字符串路由框架解析 Pass — 设计方案

> 目标：让 toolkit 识别 ARouter / TheRouter / WMRouter 这类**注解 + 字符串路由**框架的页面跳转，补上 `navigation_graph.json` 里缺失的 Activity→Activity / Activity→Fragment 边。

---

## 1. 问题背景

### 现象
在重度使用 TheRouter 的项目（如 Fitness）上，`navigation_graph.json` 几乎全是 dialog 自环边，Activity 间跳转边约等于零。下游 `compute_reach_paths` 的 BFS 无边可走，77% 屏幕被判 `truly_isolated`，`phase2_scope` 判死大量真实页面。

### 根因
toolkit 现有导航抽取只认 4 种**直接模式**：
- `startActivity(Intent(this, X::class.java))`
- 间接 Intent（`createIntent` 工厂 / 局部 Intent 变量）
- `FragmentTransaction.replace/add`
- `dialog.show()` / `Dialog()` 构造

而字符串路由是**三层间接**，一条都不匹配：

```kotlin
// 第1层 目标侧：注解声明路由串（常量拼接）
@Route(path = GyRouterConstant.ACTIVITY_MAIN)
class GyMainActivity : ...

// 常量定义（编译期可求值）
object GyRouterConstant {
    private const val GY_GROUP = "/gym/"
    const val ACTIVITY_MAIN = GY_GROUP + "activity/GyMainActivity"   // = "/gym/activity/GyMainActivity"
}

// 第2层 发起侧：走封装扩展函数
theRouter(RingARouteConstant.ACTIVITY_RING) { ... }   // wrapper
// wrapper 内部： TheRouter.build(path).apply{...}.navigation()

// 第3层 运行时：路由串来自服务定位器（静态解不了）
TheRouter.build(getServiceCenter()!!.getVipActivityRoutePath())
```

### Fitness 实测数据（3296 源文件）
| 信号 | 数量 |
|---|---|
| `@Route(path=)` 声明 | 102 |
| TheRouter/ARouter 引用 | 762 |
| `startActivity` 直接跳转 | 62 |
| toolkit grep `TheRouter/ARouter` | **0 命中** |
| `theRouter(常量)` 真实发起点 | 14 |
| `TheRouter.build(常量)` 直接调用 | **0** ← 注意：没有裸的 build(常量) |
| `build(运行时表达式)` 解不了的 | 少数（服务定位器） |

**关键教训**：不能只 grep `build(常量)`——真实发起点全被 wrapper 包了一层，必须做**封装函数穿透 + 跨函数常量传播**。

---

## 2. 方案总览

新增一个提取器 `router_table_extractor.py`，在 `navigation_extractor.run()` 的 `all_edges` 累加流水线中插入一步，产出 `via = "router:therouter"` 的导航边。四步：

```
Step 1  建路由表     @Route(path=X) + 常量求值   →  { 路由串: 目标类 }
Step 2  建 wrapper 白名单   识别 theRouter(path) 这类封装  →  { wrapper函数: 路由串形参位置 }
Step 3  连边         扫调用点，常量实参 → 路由表查 to  →  nav 边
Step 4  兜底标记     解不出常量的 build(表达式)  →  confidence=uncertain
```

全部确定性静态分析，复用现有 tree-sitter AST 基础设施，无新依赖，无 LLM。

---

## 3. 详细设计

### Step 1 — 建路由表 `{ route_string: target_class }`

**输入**：所有 `.kt` / `.java` 源文件。

**1a. 收集常量定义**
扫所有 `object` / `companion object` 里的 `const val`（以及 Java `static final String`）：
```kotlin
const val GY_GROUP = "/gym/"
const val ACTIVITY_MAIN = GY_GROUP + "activity/GyMainActivity"
```
建常量表 `{ 全限定常量名: AST表达式 }`，例如 `GyRouterConstant.ACTIVITY_MAIN → (GY_GROUP + "activity/GyMainActivity")`。

**1b. 常量求值（编译期折叠）**
对每个常量表达式做 AST 遍历求值，只支持编译期可求值的形式：
- 字符串字面量 `"foo"`
- 字符串拼接 `A + B`（两侧递归求值）
- 引用另一个已知常量（`GY_GROUP` → `"/gym/"`），支持同 object 内 `private const` 和跨 object 的 `Xxx.CONST`
- 求值失败（含函数调用、变量）→ 该常量标记 unresolved，不进表

Fitness 的常量全是 `GROUP + "字面量"` 两层拼接，100% 可解。

**1c. 关联注解 → 目标类**
扫 `@Route(path = <常量引用或字面量>)` 注解，取其**紧邻的类声明**作为目标类：
```kotlin
@Route(path = GyRouterConstant.ACTIVITY_MAIN)   // path 常量求值 = "/gym/activity/GyMainActivity"
class GyMainActivity                             // 目标类
```
写入路由表：`{ "/gym/activity/GyMainActivity": "GyMainActivity" }`。

**注解形式兼容**（做成配置，覆盖三框架）：
- TheRouter/ARouter：`@Route(path = X)`
- 多参数：`@Route(path = X, group = Y)` — 只取 path
- path 直接字面量：`@Route(path = "/gym/xxx")`

**产出**：`route_table = { route_string: {class, path_const_name, decl_file, decl_line} }`

---

### Step 2 — 建 wrapper 白名单

**动机**：真实发起点是 `theRouter(常量)`，不是 `build(常量)`。必须先识别这些封装函数，才能把常量实参映射到路由。

**识别规则**：一个函数是路由 wrapper，当且仅当：
1. 有一个 `String` 类型形参（记其位置/名字，如 `path`）
2. 函数体内出现 `TheRouter.build(<该形参>)` 或 `<Router>.getInstance().build(<该形参>)`
3. 且后接 `.navigation()` / `.createFragment()` / `.navigationForResult()` 等发起终结符

```kotlin
inline fun theRouter(path: String, block: Navigator.() -> Unit) =
    TheRouter.build(path).apply { block(this) }.navigation()   // ← path 形参流入 build
```
→ 记录 `{ "theRouter": {path_param_index: 0} }`

**递归穿透**（一层足够覆盖 Fitness）：`theRouter(path) = theRouter(path) {}` 这种转调另一个 wrapper 的，把 path 位置继承过去。

**产出**：`wrappers = { func_name: {path_param_index, kind: activity|fragment} }`

内置默认白名单（`TheRouter.build`、`ARouter.getInstance().build`、`Router.build`）作为直接入口，wrapper 是项目自定义的补充。

---

### Step 3 — 连边

扫所有调用点，三种情况：

**3a. 直接入口**：`TheRouter.build(<常量>).navigation()`
- 常量实参 → 常量表求值 → 路由表查 `to`
- `from` = 调用点所在类（`_extract_class_name`）
- 直接连边

**3b. Wrapper 调用**：`theRouter(<常量>)` / `theRouter(<常量>) {...}`
- 函数名命中 wrapper 白名单
- 取 `path_param_index` 位置的实参 → 常量求值 → 路由表查 `to`
- `from` = 调用点所在类
- 连边

**3c. 边构造**（对齐现有边 schema）：
```python
{
    "from": <调用点类>,
    "to": <路由表目标类>,
    "to_layout": _find_layout_for_class(<目标类>),
    "type": "activity" | "fragment",        # 由目标类注解/继承判定
    "via": "router:therouter",              # 新 via 值，下游可区分
    "trigger": f"route: {route_string}",    # 保留路由串做证据
    "confidence": "static",
    "evidence": {"call_file": ..., "call_line": ..., "route_string": ...,
                 "decl_file": ..., "decl_line": ...}
}
```

**去重**：交给现有 `nav_pipeline.dedupe_edges()`，无需自己做。

---

### Step 4 — 兜底标记

解不出常量的调用点（`build(getServiceCenter()!!.getVipActivityRoutePath())`）：
- 不丢弃，产一条 `confidence = "uncertain"` 的记录，`to = ""`，`trigger = "route: <unresolved-expr>"`
- 写入独立文件 `router_unresolved.json`（不进 nav_graph 主边集，避免假边），供下游/人工审计

---

## 4. 集成点

### 4.1 代码位置
新文件：`bundled_spec_tools/extractors/router_table_extractor.py`
主函数：`run(project_root, dep_roots, layout_resolver) -> {"edges": [...], "route_table": {...}, "unresolved": [...], "stats": {...}}`

### 4.2 挂载到 navigation_extractor.run()
在 `navigation_extractor.run()` 的 `all_edges` 累加链里插入（L2 之后、manifest 隐式 Intent 之前）：

```python
# --- Router framework pass (TheRouter/ARouter/WMRouter) ---
try:
    from extractors import router_table_extractor
    router_result = router_table_extractor.run(
        project_root, dep_roots, layout_resolver=_find_layout_for_class
    )
    all_edges.extend(router_result["edges"])
    _ROUTER_TABLE = router_result["route_table"]   # 供 main.py 落盘
except Exception:
    pass
```

因为 `run()` 已是"多来源 edge 累加 + 末尾统一 dedupe"的结构，插入零副作用：不改任何现有模式，只追加边。

### 4.3 产物落盘（main.py）
- 主边并入 `navigation_graph.json`（`via` 带 `router:` 前缀，下游可筛）
- 新增 `route_table.json`：`{ 路由串: 目标类 }` 全表（诊断 + 下游复用）
- 新增 `router_unresolved.json`：Step 4 的 uncertain 记录

### 4.4 终端输出（对齐现有中文风格）
```
[4b/9] 解析字符串路由框架 (router framework)…
  路由声明(@Route)：102 → 已解析路由表：102
  发起调用点(build/wrapper)：29 → 连边：24，运行时未定：5
  封装函数(wrapper)识别：3（theRouter / theRouterFragment / theRouterIntent）
```

---

## 5. 配置化（覆盖三框架）

抽一个 `data/router_frameworks.yaml`，让三家框架共用一个 pass：

```yaml
frameworks:
  therouter:
    annotation: "Route"           # @Route(path=...)
    path_arg: "path"
    build_entries:                # 直接入口
      - "TheRouter.build"
    dispatch_terminals:           # 发起终结符
      - "navigation"
      - "createFragment"
      - "navigationForResult"
  arouter:
    annotation: "Route"
    path_arg: "path"
    build_entries:
      - "ARouter.getInstance().build"
    dispatch_terminals:
      - "navigation"
  wmrouter:
    annotation: "RouterUri"
    path_arg: "path"
    build_entries:
      - "Router.startUri"
    dispatch_terminals:
      - "startUri"
```

wrapper 白名单是项目扫出来的，不写死。

---

## 6. 影响面评估

| 方面 | 影响 |
|---|---|
| 现有直接模式抽取 | **零改动**，纯追加边 |
| 无路由框架的项目（AIPPT） | **零触发**，没有 `@Route` 就不产边 |
| 依赖 | 无新增，复用 tree-sitter AST |
| 性能 | +1 遍源码扫描（可与现有扫描合并，摊薄）；Fitness 3296 文件量级可接受 |
| 假边风险 | 低——`@Route` 注解是强信号，路由串→类是精确映射；解不出的走 uncertain 不进主边集 |
| 下游 | `via="router:*"` 是新值，向后兼容；老下游当普通边用，新下游可按 confidence 筛 |

---

## 7. 覆盖边界（诚实声明）

**能解**：
- `@Route(path=常量)` + 常量为字面量/拼接/常量引用 → 100%（Fitness 102/102）
- `TheRouter.build(常量)` 直接调用
- `theRouter(常量)` 经 wrapper 白名单（一层穿透）

**解不了（标 uncertain）**：
- 路由串来自运行时（服务定位器 `getVipActivityRoutePath()`、网络下发、`when` 分支拼接）
- wrapper 嵌套超过一层的极端情况
- 路由串用非 `const`（普通 `val` / 函数返回）拼接

Fitness 上预期：102 声明全解，~24/29 发起点连边，~5 运行时留 uncertain。

---

## 8. 工作量与分期

| 阶段 | 内容 | 量级 |
|---|---|---|
| P1 | Step 1 路由表（注解 + 常量求值）+ 落盘 `route_table.json` | 核心，~1 个提取器模块 |
| P2 | Step 2/3 wrapper 白名单 + 连边 | 中等，难点在常量传播 |
| P3 | Step 4 uncertain + 配置化 YAML + 三框架适配 | 收尾 |

P1+P2 做完即可让 Fitness 的 nav 边从"几乎全 dialog 自环"恢复到接近真实规模，是收益主体。P3 让能力普适到 ARouter/WMRouter。

三步全是确定性静态分析，与现有 tree-sitter AST 基础设施完全兼容，不需要 LLM。
