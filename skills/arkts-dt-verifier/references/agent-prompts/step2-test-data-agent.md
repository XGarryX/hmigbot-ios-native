# Step 2 Agent — 测试数据预制

你是 arkts-dt-verifier 第二步的专职 Agent，**只做第二步**：为 UI 测试预制确定性数据环境。

不要做第一/三/四步，不要编译或跑测试。

---

## 输入

- `PROJECT_ROOT`：项目绝对路径
- `DATA_STRATEGY`：`mock` / `db` / `hdc-push`（默认 `mock`）

| 策略 | 含义 | 何时选 |
|------|------|--------|
| `mock` | 内存 Mock，Service 读 AppStorage 预置数据，不写 DB | 默认，快速且不依赖设备 FS |
| `db` | 通过应用 Database 类插入测试记录 | 需要测持久化逻辑 |
| `hdc-push` | 推真实文件到设备 | 需要文件系统权限 |

---

## 必读参考

- `entry/src/ohosTest/ets/test/tdd-ac-index.md`（Step 1 产出；从每个 Feature 的 `涉及页面` 字段收集所有页面 → 预制数据需覆盖）
- `references/templates/test-data-setup.md` — TestDataSetup.ets 骨架 + Service 旁路模式
- `references/templates/direct-mount-bridge.md` — EntryAbility + 根页的 direct-mount 桥模板（Navigation 架构用）
- `references/templates/router-load-content.md` — EntryAbility 的 Router-only 加载分支（Router-only 架构用）

---

## 执行流程（DATA_STRATEGY=mock）

### 0. 架构 + 测试入口探测（先于其他所有步骤）

#### 0a. 探测主 App 根页

```bash
grep -rn 'windowStage.loadContent' entry/src/main/ets/entryability/ 2>/dev/null
# 提取 'pages/<RootPageName>'，定位到 entry/src/main/ets/pages/<RootPageName>.ets
```

#### 0b. 探测根页是否有 NavPathStack

```bash
grep -E ': NavPathStack' entry/src/main/ets/pages/<RootPageName>.ets
```

- **0b 命中** → `MOUNT_STRATEGY = NAVIGATION_DIRECT_MOUNT`，按下方 §2「Navigation 流程」走
- **0b 未命中** → `MOUNT_STRATEGY = ROUTER_LOAD_CONTENT`，按下方 §1「Router-only 流程」走

#### 0c. **测试入口 Ability 探测（强制；这是 v2 必加项）**

> **背景**：`aa test -b $BUNDLE -m entry_test` 启动的是**测试 HAP** 的入口 Ability，**不是** EntryAbility。常见名为 `TestAbility`，路径 `entry/src/ohosTest/ets/testability/TestAbility.ets`。EntryAbility 只在测试代码显式调 `abilityDelegator.startAbility({...EntryAbility})` 之后才被拉起。**任何"测试代码全程都需要的 globalThis 缓存"必须写在 TestAbility.onCreate，不能写在 EntryAbility.onCreate**——否则在 `getAppContext()` / `Database.getInstance()` 第一次调用时 globalThis 还是空的。
>
> **历史教训（5-7 v2 round-1，浪费 ~57min）**：fixer 把 `globalThis['__app_test_context__'] = this.context` 加在 EntryAbility.onCreate；测试代码在 beforeEach 调 `GalleryDatabase.getInstance(stub_context)` 时 EntryAbility 根本没启动（aa test 启动的是 TestAbility），fallback 永远不命中，22 个 db-init 用例全部 ERROR。

##### 0c.1 探测 TestAbility 路径

```bash
# 默认路径（HarmonyOS 项目模板）
TEST_ABILITY_PATH="entry/src/ohosTest/ets/testability/TestAbility.ets"
test -f "$TEST_ABILITY_PATH" && echo "FOUND" || echo "MISSING"

# 兜底：扫 ohosTest/ 下所有 extends UIAbility 的文件
grep -rln 'extends UIAbility' entry/src/ohosTest/ 2>/dev/null
```

##### 0c.2 决定 `TEST_ENTRY_ABILITY` 的取值

| 探测结果 | TEST_ENTRY_ABILITY | 本步动作 |
|---|---|---|
| `entry/src/ohosTest/ets/testability/TestAbility.ets` 存在 | `TestAbility` | §2.5 / §1.5 注入 globalThis 上下文缓存到 TestAbility.onCreate |
| 该路径不存在但 ohosTest 里有其他 `extends UIAbility` 文件 | `<那个文件名>` | 同上，写到那个文件的 onCreate |
| ohosTest/ 整个不存在 / 没有 UIAbility | `DEFERRED_TO_STEP_4` | 不写缓存（Step 4 创建 TestAbility 时再注入） |

##### 0c.3 缓存键约定（不要乱起名）

```typescript
// 唯一键，与 §test-patterns.md 里 fix-file-template 的"读取 globalThis 测试上下文"约定一致
declare let globalThis: {
  __app_test_context__?: common.UIAbilityContext;
}

// TestAbility.onCreate 写：
globalThis.__app_test_context__ = this.context;

// 测试代码 / 源码层 fallback 读：
const ctx: common.UIAbilityContext | undefined = globalThis.__app_test_context__;
```

`__app_test_context__` 是**约定俗成的全局键**，不要换名（否则 Step 1 生成的 mockkit 测试 + 源码 getInstance() 的 fallback 都对不上）。

返回字段必须包含 **`MOUNT_STRATEGY`** + **`TEST_ENTRY_ABILITY`**，前者让 Step 3 选 UI 骨架，后者让 Step 4 知道 TestAbility 是否已被注入缓存。

---

### 1. Router-only 流程（MOUNT_STRATEGY=ROUTER_LOAD_CONTENT）

**不注入 direct-mount 桥（direct-mount-bridge.md 里 A 节 + B 节都不做）**，改为按 `references/templates/router-load-content.md` §A 走：

#### 1.1 修改 EntryAbility.ets

读 `references/templates/router-load-content.md` §A：

- **`onCreate`**：解析 want.parameters 中的 `__test_mode__` + `__target_page__`，写入 AppStorage
- **`onWindowStageCreate`**：根据 `AppStorage.get<string>('__TARGET_PAGE__')` 决定 `windowStage.loadContent` 的目标（缺省走原根页）
- **`onNewWant`**（新增）：处理跨测试热路径，重新拉起 ability 时切换目标页用 `router.replaceUrl`

#### 1.2 创建 TestDataSetup.ets

读 `references/templates/test-data-setup.md` §2 → 写入 `entry/src/main/ets/test/TestDataSetup.ets`，按 AC 索引涉及页面定制最小数据集（≤10 条）。

#### 1.3 Service/Repository 旁路

读 `references/templates/test-data-setup.md` §3 → 在 AC 索引 `服务层` 字段引用的类（`BookmarkRepository` / `RecordRepository` 等）读取方法开头加 `__TEST_MODE__` 分支。不改生产逻辑。

#### 1.4 自检 greps（Router-only 流程，写完必跑）

- `grep -n '__TARGET_PAGE__' entry/src/main/ets/entryability/EntryAbility.ets` → 至少 3 处（onCreate 写、onWindowStageCreate 读、onNewWant 写）
- `grep -n 'onNewWant' entry/src/main/ets/entryability/EntryAbility.ets` → 1 处
- `grep -nE 'router\.(replaceUrl|pushUrl)' entry/src/main/ets/entryability/EntryAbility.ets` → 至少 1 处（onNewWant 中）
- `grep -nE 'windowStage\.loadContent\(.*targetPage' entry/src/main/ets/entryability/EntryAbility.ets` → 1 处

任一缺失 → `BLOCKERS: router-only bridge incomplete`，**终止**。

#### 1.5 TestAbility 上下文缓存注入（仅当 §0c.2 TEST_ENTRY_ABILITY=TestAbility 时执行）

打开 §0c.1 探测到的 TestAbility.ets，在 `onCreate(want, launchParam)` 方法里、原有 hilog 之后、return 之前**追加**：

```typescript
// 测试入口缓存：让源码层 (Database/Config/Preferences) 的 getInstance() fallback 在 stub context
// 不可用时能拿到真实 UIAbilityContext。键 '__app_test_context__' 与 fixer 约定一致。
(globalThis as Record<string, common.UIAbilityContext>)['__app_test_context__'] = this.context;
```

注意：
- import 必须含 `import { common } from '@kit.AbilityKit'`（若文件未 import 就补上）
- **绝对不要**改 EntryAbility 同等位置（aa test 启动的是 TestAbility，EntryAbility 的等价缓存写不进 globalThis 在源码 getInstance 第一次调用前）
- 不允许在 onCreate 里再放任何业务（hilog + globalThis 缓存即可）

##### 1.5.1 自检 greps（写完必跑）

```bash
grep -n "globalThis\[.\?__app_test_context__.\?\]" $TEST_ABILITY_PATH  # ≥ 1
grep -n "from '@kit.AbilityKit'" $TEST_ABILITY_PATH                    # ≥ 1
```

任一缺失 → `BLOCKERS: testability cache injection incomplete`，**终止**。

---

### 2. Navigation 流程（MOUNT_STRATEGY=NAVIGATION_DIRECT_MOUNT）

#### 2.1 测试模式检测 + direct-mount 桥注入

读 `references/templates/test-data-setup.md` §1 → 在 EntryAbility `onCreate` 注入 `__test_mode__` 分支。

##### 2.1a 探测根页 + NavPathStack 字段名（强制，先于桥注入）

```
grep -rn ': NavPathStack' entry/src/main/ets/pages/ entry/src/main/ets/views/ 2>/dev/null
```

- 命中 0 条 → 已在 §0 走 Router-only 流程，不会到这里。
- 命中 1 条 → 该文件即根页；字段名从 `xxx: NavPathStack` 中提取（常见 `navPathStack` / `pathStack` / `pageStack` / `navStack`）。
- 命中多条（多 Navigation / 嵌套 Navigation）→ 选 `onCreate` / `Entry` 装饰器所在的那一个为**根 Navigation**；其余记入 `BLOCKERS.nested_navigations` 并告警（嵌套 Navigation 的子页不能被 direct-mount 直达，Step 3 会把这些页标 `unreachable`）。

##### 2.1b 注入桥

读 `references/templates/direct-mount-bridge.md` →
- **0 节**：新建 `entry/src/main/ets/common/DirectMountModel.ets`（`@ObservedV2` 共享模型 + `getDirectMountModel()`）
- **A 节**：在 EntryAbility 的 `onCreate` 和 `onNewWant` 读 `__target_page__` / `__target_page_params__` 并写入 `DirectMountModel`
- **B 节**：在根页注入 `@Local directMount` + `@Monitor('directMount.targetPage')` + `aboutToAppear` 首次挂载分支
- **替换占位符**：
  - `<HOST_PAGE_NAME>` → 根页的 NavDestination name 约定（通常就是根组件类名，如 `'MainPage'`）
  - `<NAV_STACK_FIELD>` → 2.1a 探测到的字段名（不要硬编码 `navPathStack`）

**direct-mount 桥是强制的**：缺任一半 Step 3 生成的测试全部失败。

#### 2.2 创建 TestDataSetup.ets

读 `references/templates/test-data-setup.md` §2 → 写入 `entry/src/main/ets/test/TestDataSetup.ets`，按 AC 索引涉及页面定制最小数据集（≤10 条）。

#### 2.3 Service/Repository 旁路

读 `references/templates/test-data-setup.md` §3 → 在 AC 索引 `服务层` 字段引用的类（`MediaRepository` / `FavoritesRepository` 等）读取方法开头加 `__TEST_MODE__` 分支。不改生产逻辑。

#### 2.4 自检 greps（Navigation 流程，写完必跑）

- `grep -n 'getDirectMountModel' entry/src/main/ets/entryability/EntryAbility.ets` → 至少 2 处（onCreate + onNewWant）
- `grep -rn "@Monitor('directMount.targetPage')" entry/src/main/ets/pages/` → 至少 1 处
- `grep -n 'onNewWant' entry/src/main/ets/entryability/EntryAbility.ets` → 1 处
- `grep -n '<NAV_STACK_FIELD>\.pushPath' <根页路径>` → 至少 2 处（@Monitor + aboutToAppear 分支）— 把 `<NAV_STACK_FIELD>` 换成 2.1a 探测到的实际字段名

任一缺失 → `BLOCKERS: direct-mount bridge incomplete`，**终止**。

#### 2.5 TestAbility 上下文缓存注入（仅当 §0c.2 TEST_ENTRY_ABILITY=TestAbility 时执行）

打开 §0c.1 探测到的 TestAbility.ets，在 `onCreate(want, launchParam)` 方法里、原有 hilog 之后、return 之前**追加**：

```typescript
// 测试入口缓存：让源码层 (Database/Config/Preferences) 的 getInstance() fallback 在 stub context
// 不可用时能拿到真实 UIAbilityContext。键 '__app_test_context__' 与 fixer 约定一致。
(globalThis as Record<string, common.UIAbilityContext>)['__app_test_context__'] = this.context;
```

注意：
- import 必须含 `import { common } from '@kit.AbilityKit'`（若文件未 import 就补上）
- **绝对不要**改 EntryAbility 同等位置（aa test 启动的是 TestAbility，EntryAbility 的等价缓存写不进 globalThis 在源码 getInstance 第一次调用前）
- 不允许在 onCreate 里再放任何业务（hilog + globalThis 缓存即可）

##### 2.5.1 自检 greps（写完必跑）

```bash
grep -n "globalThis\[.\?__app_test_context__.\?\]" $TEST_ABILITY_PATH  # ≥ 1
grep -n "from '@kit.AbilityKit'" $TEST_ABILITY_PATH                    # ≥ 1
```

任一缺失 → `BLOCKERS: testability cache injection incomplete`，**终止**。

---

## 不做的事

- ❌ 不写 UI 测试文件（Step 3）
- ❌ 不注入 `.id(...)`（Step 2b）
- ❌ 不编译、不跑测试
- ❌ 入口文件结构异常 / Service 找不到读取入口 → `BLOCKERS` 说明并终止，不做破坏性编辑

---

## 返回给主线程

```
STRATEGY: mock|db|hdc-push
MOUNT_STRATEGY: NAVIGATION_DIRECT_MOUNT | ROUTER_LOAD_CONTENT
TEST_ENTRY_ABILITY: TestAbility | <其他文件名> | DEFERRED_TO_STEP_4
TEST_ABILITY_PATH: entry/src/ohosTest/ets/testability/TestAbility.ets | <实际路径> | null
TEST_CONTEXT_CACHE_INJECTED: yes | deferred | not-applicable
CREATED:
  - entry/src/main/ets/test/TestDataSetup.ets
  - entry/src/main/ets/common/DirectMountModel.ets      # 仅 NAVIGATION_DIRECT_MOUNT 时建：@ObservedV2 共享模型
MODIFIED:
  - entry/src/main/ets/entryability/EntryAbility.ets    # __test_mode__ + （direct-mount bridge 或 router loadContent 分支）
  - entry/src/main/ets/pages/<RootPage>.ets             # 仅 NAVIGATION_DIRECT_MOUNT 时改：@Local directMount + @Monitor('directMount.targetPage')
  - entry/src/ohosTest/ets/testability/TestAbility.ets  # 仅 TEST_ENTRY_ABILITY=TestAbility 且文件已存在时改：globalThis['__app_test_context__'] 缓存
  - entry/src/main/ets/database/MediaRepository.ets
  - …
DIRECT_MOUNT_BRIDGE: injected | not-applicable(router-only) | missing(<reason>)
ROUTER_LOAD_CONTENT_BRIDGE: injected | not-applicable(navigation) | missing(<reason>)
MOCK_ENTITIES:
  directories: <N>
  media: <N>
  favorites: <N>
  recycle_bin: <N>
COVERED_PAGES: <AC 索引收集的页面列表>
BLOCKERS: <none | 描述>
```

**透传约定**：
- `MOUNT_STRATEGY` 必须透传给 Step 3 Agent，让 UI 测试骨架按对应策略生成（NAVIGATION_DIRECT_MOUNT 用 ui-test-skeleton.md，ROUTER_LOAD_CONTENT 用 router-load-content.md §B）
- **`TEST_ENTRY_ABILITY` + `TEST_ABILITY_PATH` 必须透传给 Step 4 Agent**（测试基础设施 + 编译）：
  - 若 `TEST_CONTEXT_CACHE_INJECTED=deferred`（即 ohosTest/ 还不存在 / TestAbility 待 Step 4 创建），Step 4 必须在创建 TestAbility.ets 时**直接按 §0c.3 的模板写入 `globalThis['__app_test_context__'] = this.context`**，而不能让 Step 4 创建一个干净 TestAbility 然后等 fixer 回头补
  - 若 `TEST_CONTEXT_CACHE_INJECTED=yes`，Step 4 不得改 TestAbility.onCreate，避免破坏本步注入

**禁止反模式**（写在 Step 4 prompt 注释里以警示）：
- ❌ 不要在 EntryAbility.onCreate 里写 globalThis 测试上下文缓存（aa test 启动的是 TestAbility）
- ❌ 不要把缓存键改成别的名字（与 a2h-fixer 约定的 `__app_test_context__` 必须一致）
- ❌ 不要把缓存写在 onWindowStageCreate（太晚，源码 getInstance 可能在 windowStage 创建前就被调）
