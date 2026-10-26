# Audit 阶段的 grep/glob 模式手册

执行 audit 时按 rule_id 顺序扫，命中规则严格度（MUST/SHOULD）决定写入 P0/P1/P2 哪一节。`<root>` 指工程根目录。

> ⚠️ **核心原则**：**判违规要看规则原意，不看字面**。grep 命中后，必要时再读上下文确认。

---

## R1 工程结构（MUST）

```bash
test -d <root>/products       || echo "P0: 缺 products/"
test -d <root>/features       || echo "P0: 缺 features/"
test -d <root>/components     || echo "P0: 缺 components/"
ls <root>/features/ 2>/dev/null | grep -E '^business_' | wc -l   # business 模块数
```

如果发现 entry 单模块且其 ets 下含明显多业务（pages/ 里同时有 home/mine/login 等）→ P0 拆分。

## R2 私仓（MUST）

```bash
grep -q dadoubk <root>/.ohpmrc 2>/dev/null || echo "P0: .ohpmrc 缺私仓 registry"
grep -q '"lib_common"' <root>/oh-package.json5 || echo "P0: 未引入 lib_common（提供 BaseViewModel/RouterUtils 等核心）"
grep -q '"lib_widget"' <root>/oh-package.json5 || echo "P1: 建议引入 lib_widget（公共 ArkUI 组件）"
# lib_network 仅当工程有网络调用时必需：
if grep -rq -E 'RequestUtil|ExternalReqUtil|http\.createHttp|@ohos/axios' --include='*.ets' <root>; then
  grep -q '"lib_network"' <root>/oh-package.json5 || echo "P0: 工程使用网络请求但未引入 lib_network"
fi
# overrides
grep -A20 '"overrides"' <root>/oh-package.json5 2>/dev/null | grep -q lib_ \
  || echo "P1: 缺 overrides 锁版本（多模块版本可能不一致）"
# 鸿蒙联运版本规则
if grep -q '"lib_hmiap"' <root>/oh-package.json5; then
  grep -E '"lib_hmiap":\s*"1\.0\.0"' <root>/oh-package.json5 \
    || echo "提示: lib_hmiap 非 1.0.0，确认是否启用了鸿蒙联运（未启用应锁 1.0.0）"
fi
```

## R3 代码分层（SHOULD）

**不**按目录名拼写判违规。检测：

```bash
# 单 .ets 超大 → 职责单一性 warning
find <root>/features <root>/components <root>/products -name '*.ets' \
  -exec wc -l {} \; 2>/dev/null | awk '$1>500 {print "P2: "$2" "$1" 行，建议拆分"}'

# 业务混杂判定（启发式）：检查每个 features/business_* 的 pages/ 下是否同时含
# 明显跨业务关键字（home/mine/login/setting/video）。如出现至少 2 个，说明业务未拆开。
```

## R4 资源（**MUST**——客户已升级严格度）

> 客户校准（2026-04）：R4.1/R4.2/R4.3/R4.4 全部 MUST。新增资源**禁止** png/jpg/gif；存量 png 列入 P1 资源迁移待办；多色版图标**必须**改单色 webp + ColorUtils.hexToColorMatrix（私仓 lib_common）+ colorFilter。

```bash
# R4.1: 新增图片 → 必须 webp/svg。存量 png 标 P1 迁移
PNG_COUNT=$(find <root> -name '*.png' -path '*/resources/*' 2>/dev/null | wc -l)
[ "$PNG_COUNT" -gt 0 ] && echo "P1: $PNG_COUNT 个 png（应批量转 webp 3x，并禁止新增 png）"

# R4.3: gif 必改
GIF_COUNT=$(find <root> -name '*.gif' 2>/dev/null | wc -l)
[ "$GIF_COUNT" -gt 0 ] && echo "P1: $GIF_COUNT 个 gif（必改 webp，对齐 Android）"

# R4.4: 多色版同名图标（典型反模式）—— 命中 → P1 改单色 webp + colorFilter
find <root> -name '*_blue.*' -o -name '*_red.*' -o -name '*_dark.*' -o -name '*_light.*' \
  -path '*/resources/*' 2>/dev/null | head -10
```

## R5.1 颜色（MUST + MAY）

```python
# 检查 business_common/color.json 是否包含规范定义的所有通用 token
required = {'color_main','color_page_bg','color_text','color_text_hint','color_text_low',
            'color_main_btn_bg_start','color_main_btn_bg_end','color_main_btn_bg_disabled',
            'color_title','color_title_right',
            'color_dialog_bg','color_dialog_title','color_dialog_content',
            'color_dialog_sure_bg_start','color_dialog_sure_bg_end','color_dialog_sure_text',
            'color_dialog_cancel_bg','color_dialog_cancel_text','color_dialog_disable_bg'}
# missing = required - business_common_names → P1: 缺通用 token

# 检查"通用色被乱命名"：如 products/phone 或 entry 的 color.json 里出现明显是主色/主文字色
# 但命名为 app_theme/main_color/text_color 等 → P1: 通用色应统一到 business_common 用规范名
non_canonical_general_hints = {'app_theme','app_text_color','main_color','theme_color',
                               'text_color','page_color','main_bg_color'}
# 命中即提示替换
```

**业务自有色**（如 `slide_default_track_color / video_duration_bg / digital_xxx`）允许业务模块自己定义，**不视违规**。

## R5.2 字体 weight（SHOULD）

```bash
COUNT=$(grep -rn 'FontWeight\.Bold' --include='*.ets' <root> 2>/dev/null | wc -l)
[ "$COUNT" -gt 0 ] && echo "P2: 共 $COUNT 处 FontWeight.Bold（如系 Android 迁移代码，建议改 UI 给定 weight 数值）"
```

## R5.3 页面左右间距（SHOULD）

只看页面最外层 padding。简单启发：扫 `pages/*.ets`，看 build() 第一层 Column/Row 是否含硬编码 left/right padding：

```bash
# 简化版：grep page 下 ets 文件中包含 padding({...left:数字 或 right:数字
grep -rn 'padding.*\(left\|right\):\s*[0-9]' --include='*.ets' <root>/features/*/src/main/ets/pages \
  2>/dev/null | head -20
# 命中作 P2 提示：建议改 BreakpointModel.pagePadding
```

## R6.1a 状态管理 v1 残留（MUST）

```bash
grep -rnE '@(State|Prop|Link|Provide|Consume|ObjectLink|Observed|StorageLink|StorageProp)\b' \
     --include='*.ets' <root> | grep -v 'ObservedV2\|StorageLinkV2\|StoragePropV2' | head -50
grep -rn '^@Component\b' --include='*.ets' <root>   # 应是 @ComponentV2
```

## R6.1b LazyForEach（**MUST**——客户已升级严格度）

```bash
# 客户校准（2026-04）：从 SHOULD 升 MUST，命中即 P1 改 Repeat
grep -rn 'LazyForEach' --include='*.ets' <root>
# 仅在 SDK 内置组件强制 LazyForEach 等极端场景豁免，需在报告记录
```

## R6.1b''' Repeat + LazyDataSource / virtualScroll 传参（**MUST** — 2026-05 客户校准）

```bash
# 客户校准：Repeat 数据源应是 T[]，不是 LazyDataSource；virtualScroll() 不传参
grep -rnE 'Repeat<[^>]+>\([^)]*\.getDataList\(\)' --include='*.ets' <root>     # ❌ 命中即 P1
grep -rnE '\.virtualScroll\(\s*\{' --include='*.ets' <root>                     # ❌ 命中即 P1
grep -rn 'LazyDataSource' --include='*.ets' <root>                              # 配套清理
grep -rnE 'private\s+\w+\s*:\s*LazyDataSource' --include='*.ets' <root>        # 待删字段
```

修复方法：
1. `private dataSource: LazyDataSource<T> = new LazyDataSource<T>()` → `@Trace list: T[] = []`
2. `dataSource.setData(arr); dataSource.reloadData()` → `this.list = arr`
3. `Repeat<T>(this.dataSource.getDataList())` → `Repeat<T>(this.list)`
4. `.virtualScroll({ totalCount: ... })` → `.virtualScroll()` 空参

## R5.4 NavHeaderBar 强制使用（**MUST** — 2026-05 客户校准）

```bash
# 私仓 lib_widget@1.0.8+ 已提供 NavHeaderBar — 业务侧禁止再写自定义标题栏
grep -rln "ic_title_white_back\|app\.media\.back\|app\.media\.ic_back" features/*/src/main/ets/pages products/phone/src/main/ets/pages --include='*.ets'
# 期望 0 命中（除显式 ADR 豁免的特殊标题外）
```

替换模板：
```ts
// 反例（手写）
Row() {
  Image($r('app.media.ic_title_white_back'))
    .width(24).height(24).margin({ left: 15 })
    .onClick(() => RouterUtils.getStack().pop())
  Text('画面调整').fontSize(18).fontWeight(FontWeight.Bold).layoutWeight(1).textAlign(TextAlign.Center)
}.height(56)

// 正例
import { NavHeaderBar } from 'lib_widget'
NavHeaderBar({ title: '画面调整' })
// 需要右侧按钮：NavHeaderBar({ title: 'xxx', rightPartBuilder: this.RightArea })
// 需要自定义返回：NavHeaderBar({ title: 'xxx', onBack: () => this.vm.onCustomBack() })
```

豁免：① 特殊定制（搜索框 / Tab 切换 / 重度视觉）写 ADR 记录；② 全屏沉浸页（无标题）不适用。

## R6.1e-2 Page 业务逻辑下沉 VM（**MUST** — 2026-05 客户实证强化）

```bash
# Page 内禁止业务调用 / 定时器 / AbortController / 长 async 方法
grep -rnE 'await\s+(\w+Service|\w+Api|\w+Repository\.getInstance\(\)|MembershipRefresher|UseCountManager|IonBusiness|new\s+\w+(Service|Api))\b' features/*/src/main/ets/pages products/phone/src/main/ets/pages --include='*.ets'
grep -rnE 'setInterval|setTimeout|new\s+AbortController' features/*/src/main/ets/pages products/phone/src/main/ets/pages --include='*.ets'
grep -rnE 'private\s+async\s+\w+(submit|fetch|load|create|generate|process|upload|download)' features/*/src/main/ets/pages products/phone/src/main/ets/pages --include='*.ets'

# Page 文件总行数（>300 通常意味业务在 page 没下沉）
for f in $(find features/*/src/main/ets/pages products/phone/src/main/ets/pages -name '*Page.ets'); do
  n=$(wc -l < "$f"); [ "$n" -gt 300 ] && echo "$n: $f"
done | sort -rn
```

整改模板：
```ts
// ❌ Page 反例
struct VFXCreatePage {
  @Local sourceImageUri: string = ''
  private aiPaintingForm: AIPaintingForm | null = null
  private async submitTask(): Promise<void> {
    await VFXRepository.getInstance().getAiConfig()
    const result = await VFXRepository.getInstance().humanSegment(...)
    // ... 50+ 行业务逻辑
  }
}

// ✅ Page 正例
struct VFXCreatePage {
  private vm: VFXCreateViewModel = new VFXCreateViewModel()
  aboutToAppear(): void { this.vm.applyRouterContext(...) }
  aboutToDisappear(): void { this.vm.dispose() }
  build() {
    NavDestination() {
      Column() {
        NavHeaderBar({ title: '画面调整' })
        if (this.vm.isGenerating) { Text(this.vm.generatingText) }
        Button('开始').onClick(() => this.vm.startGeneration())
      }
    }
  }
}

// VM 接管所有业务
@ObservedV2
class VFXCreateViewModel extends BaseViewModel {
  @Trace sourceImageUri: string = ''
  @Trace generatingText: string = '作品正在生成中'
  @Trace errorType: number = 0
  @Trace isGenerating: boolean = false
  private aiPaintingForm: AIPaintingForm | null = null
  private abortController: AbortController = new AbortController()

  async startGeneration(): Promise<void> {
    this.isGenerating = true
    try {
      await VFXRepository.getInstance().getAiConfig()
      // ... 业务编排全部在 vm
    } finally {
      this.isGenerating = false
    }
  }
  dispose(): void { this.abortController.abort() }
}
```

## R6.1c-2 ViewModel 单例反模式（**MUST** — 2026-05 客户校准）

```bash
# Page/Fragment-scope VM 不能写单例三件套
grep -rnE 'private\s+static\s+instance.*(Page|Fragment)?ViewModel' --include='*.ets' <root>
grep -rnE 'static\s+getInstance\(\)\s*:\s*\w+(Page|Fragment)?ViewModel' --include='*.ets' <root>
grep -rnE 'static\s+clearInstance\(\)' --include='*.ets' <root> | grep -i ViewModel
```

合法豁免清单（service/manager/global 层，单例可接受）：
- `*Manager` (UseCountManager, AggregatedPaymentVM 等)
- `*Service` (CoinService 这种封装 API 不算 VM 的不计入)
- `*Repository` (StarBurstRepository, AIPaintRepository 等)
- `*Refresher` / `*Business` (MembershipRefresher, IonBusiness 等)

整改：删除三件套 → 调用方 `new XxxViewModel()` + page `@Local` 持有 → 跨页共享场景改 `AppStorageV2.connect(VM, () => new VM())`

## R6.1c ViewModel 链顶层未继承 BaseViewModel（SHOULD）

```python
# 解析所有 *ViewModel.ets，构建继承图
# 对每个根（无 extends 或 extends 的目标不在工程内）的 ViewModel：
#   - 如果它是"复杂页面"的状态容器（关联了多个 @Trace 字段或多个方法）→ P1: 应继承 BaseViewModel
#   - 否则 P2 warning
# 如 class A extends B、B extends BaseViewModel → A 合规
```

简化的 grep 起点：

```bash
grep -rnE 'class\s+(\w+ViewModel)\b\s*\{' --include='*.ets' <root>
# 上面命中"无 extends"的 *ViewModel；再读上下文判断是否复杂页面状态容器
```

## R6.2 旧路由 API（MUST）

```bash
grep -rnE '\brouter\.(pushUrl|replaceUrl|back|clear)\b' --include='*.ets' <root>
grep -rn 'RouterUtils' --include='*.ets' <root> | head -3   # 是否已采用
```

## R6.3a HTTP 网络请求绕开私仓（MUST）

```bash
# HTTP 客户端
grep -rnE '@ohos/axios|http\.createHttp\b' --include='*.ets' <root>
# 注意：webSocket、@kit.NetworkKit 的 socket/connection API 不属于"网络请求"，不要标违规
```

## R6.3b DTO 用 class（MUST/SHOULD 分级）

```bash
# 命中所有 *Dto/Bean/Resp/Vo class
grep -rnE 'class\s+\w+(Dto|Bean|Data|Resp|Response|Vo|Model)\b' --include='*.ets' <root>
```

**分级判定**（必须读源码上下文，不能仅凭命名）：

- **P1（裸 class）**：`class XxxBean { field: T = default; ... }`，无 extends、无业务方法 → 必须改 interface
- **P2（项目基类继承）**：`class XxxBean extends BaseBean`、`extends HSData` 等
  - 如果项目基类提供反序列化/校验/快照等真实能力 → 视为合理设计，**仅作 P2 提示**
  - 如果基类是空壳 → 仍建议改 interface
- **MAY（实现 UI 契约）**：`class XxxBean implements VideoPlayerData`（被 ArkUI 组件签名约束必须 class）→ 不视为违规

> 不能一刀切——AI 工程里所有 DTO 都 `extends BaseBean`，是项目级历史决策，audit 应交给用户判定。

## R6.3c / R6.3d / R6.3e AbortController（按请求范围拆三条规则）

规范原文："**发起网络请求时**...在页面退出时 abort" — 但客户校准为 **按请求范围分流**：

| 规则 | 类别 | 严格度 | audit 行为 |
|---|---|---|---|
| **R6.3c** | 全局请求（App 级 init / 跨页轮询 / 用户态预加载）| MAY | **不报，禁止 abort** |
| **R6.3d** | 非全局请求（页面专属业务接口） | SHOULD | **必报 P1**——分两层检测（见下） |
| **R6.3e** | 第三方请求（ExternalReqUtil / 外部 SDK） | SHOULD（重点关注）| 默认报，业务理由可豁免 |

**R6.3c 全局请求识别（先排除，再扫剩余）**：
```bash
# 全局请求白名单：调用方在 EntryAbility / AppRepository / 私仓 BootService 等
GLOBAL_CALLERS='EntryAbility|AppRepository|IonBusiness|UseCountManager|App[A-Z]\w*Service'
# 跑 audit 前先列出所有全局请求点，execution-log 记录
grep -rEln "$GLOBAL_CALLERS" --include='*.ets' <root>/features <root>/products
```

**R6.3d 非全局请求两层检测**（命中即报 P1）：
```bash
# 第一层：API 层（*Api / *Service.ets）函数签名应含 signal? 参数（全局/非全局共用 API 层都应支持）
for f in $(grep -rlE 'RequestUtil|ExternalReqUtil' --include='*.ets' <root>); do
  if [[ "$f" == *Api.ets || "$f" == *Service.ets ]]; then
    grep -qE 'signal\??:\s*AbortSignal' "$f" \
      || echo "P1: $f 是 API 层但函数签名未接受 signal 参数"
  fi
done

# 第二层：调用层（页面 + 页面 VM）— 排除全局调用方后必须 new AbortController + abort
for f in $(grep -rlE '\.\w+Api\.\w+\(|\.\w+Service\.\w+\(' --include='*.ets' <root>/features); do
  case "$f" in
    *Page.ets|*PageVM.ets|*PageViewModel.ets)
      grep -q 'new AbortController' "$f" \
        || echo "P1 (R6.3d): $f 是页面级调用层但未创建 AbortController"
      ;;
  esac
done
```

**R6.3e 第三方请求**：grep `ExternalReqUtil`、`@ohos/axios` 直调、外部 SDK 网络（Web SDK、广告 SDK 推送 SDK 等）；命中后 audit 报为"待 review"，由 execution-log 给出业务豁免理由。

**例外**：纯工具类（如 `OssUploadFile.ets` 上传工具，调用方应自己管 abort）—— 若该工具被同一 module 内其他 API/服务调用，由调用方传 signal 即可，工具本身不必 new AbortController。

## R6.4a 持久化绕开 PreferenceUtil（MUST）

```bash
grep -rnE '@ohos\.data\.preferences\b|getPreferences\(' --include='*.ets' <root> \
  | grep -v 'PreferenceUtil'   # 排除 lib_common 自身实现
```

## R6.4b 复杂数据未用 dataorm（MUST，仅当复杂场景）

```bash
grep -rnE 'rdbStore\.|@ohos\.data\.relationalStore\b' --include='*.ets' <root> \
  | grep -v '@ohos/dataorm'
```

## R6.5a 沉浸式安全距（**MUST**——客户已升级严格度）

```bash
# 客户校准（2026-04）：从 SHOULD 升 MUST。鸿蒙工程必须预留顶/底安全距
# 即使工程没显式开 expandSafeArea，每个页面也应使用 WindowModel.windowTopPadding/BottomPadding
grep -rq 'WindowModel\|windowTopPadding\|windowBottomPadding' --include='*.ets' <root> \
  || echo "P1: 工程未使用 WindowModel（私仓 lib_common）的顶/底安全距属性"

# 写死 padding 顶/底大概率违规（可能写死安全距）
grep -rnE 'padding\s*\(\s*\{\s*top\s*:\s*[0-9]+\s*\}' --include='*.ets' <root> | head -10
grep -rnE 'padding\s*\(\s*\{\s*bottom\s*:\s*[0-9]+\s*\}' --include='*.ets' <root> | head -10
```

## R6.5b-1 List/Grid 列数动态化（**MUST**——客户已升级严格度）

```bash
# 客户校准：List 的 lanes / Grid 的 columnsTemplate 必须动态化
# 反例：lanes(2) / columnsTemplate('1fr 1fr')
grep -rnE '\.lanes\s*\(\s*[0-9]+\s*\)' --include='*.ets' <root>   # 写死数字 → P1
grep -rnE 'columnsTemplate\s*\(\s*[\047"][^\047"{]+[\047"]\s*\)' --include='*.ets' <root>  # 写死字符串 → P1

# 正例：用 BreakpointModel 的 .lanes(this.breakpoint.gridColumns)
grep -rn 'breakpoint\.\(gridColumns\|columns\)' --include='*.ets' <root> | head -3
```

## R6.6 buildProfileFields（**MUST**——客户已升级严格度）

```bash
# 客户校准：壳工程 build-profile.json5 必须配置
# 即使无三方 key，appName/appBaseType/ChanelId 也必须填
grep -A30 buildProfileFields <root>/build-profile.json5 2>/dev/null \
  | grep -qE '"(appName|appBaseType|ChanelId)"' \
  || echo "P1: build-profile.json5 缺 buildProfileFields 或缺 appName/appBaseType/ChanelId 基础字段"
```

## R6.5d List/Scroll 内嵌 RelativeContainer（MUST，会导致 bug）

```bash
# 启发式：扫 List() / Scroll() 块内子节点
python3 - <<'PY'
import os, re
for root,_,files in os.walk('<root>'):
    for f in files:
        if not f.endswith('.ets'): continue
        p=os.path.join(root,f); src=open(p,encoding='utf-8',errors='ignore').read()
        # 简化：找 List(){...RelativeContainer
        if re.search(r'(List|Scroll)\s*\([^)]*\)\s*\{[^{}]{0,2000}RelativeContainer\s*\(', src, re.S):
            print(f'P0: {p} 内 List/Scroll 套了 RelativeContainer')
PY
```

## R1.1 / R1.2 / R1.3 三段式 + business 粒度（MUST 硬检查）

> **来自 AIPPT_ArkTS_rebuild 实战教训**：第一轮重构试图用单 `business_main` 当过渡形态偷懒，被客户当场识破（"为什么 AI/Scan 的 features/ 颗粒度比这细那么多"）。本检查是**反作弊**硬关卡。

```bash
ROOT=<project-root>

# R1.1 三段式齐备
test -d "$ROOT/products" || echo "P0 R1.1: 缺 products/ 目录"
test -d "$ROOT/features" || echo "P0 R1.1: 缺 features/ 目录"
test -d "$ROOT/components" || echo "P0 R1.3: 缺 components/ 目录（components/ 不能省）"

# R1.2 features/ 业务粒度：非 common business >= 2
NON_COMMON=$(ls -d "$ROOT/features"/business_*/ 2>/dev/null | grep -v 'business_common/' | wc -l | tr -d ' ')
if [ "$NON_COMMON" -lt 2 ]; then
  echo "P0 R1.2 FAIL: features/ 下非 common business 仅 $NON_COMMON 个 (要求 >=2)"
  echo "       双 baseline: AI 6 个 / Scan 4 个"
  echo "       禁止用单 business_main 当合规'过渡形态'"
fi

# R1.3 components/module_* 至少 1 个
MOD_COUNT=$(ls -d "$ROOT/components"/module_*/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$MOD_COUNT" -lt 1 ]; then
  echo "P1 R1.3 FAIL: components/ 缺 module_* (双 baseline 各有 6 个，最低 1 个)"
fi

# R1.3' components/ 颗粒度抽取漏报检查（按复用证据，不按数量配额）
# 触发器 1: ≥2 个 page 用 Web({}) 但没 module_webview → 漏抽
WEB_PAGES=$(grep -rln "Web({" "$ROOT/features" --include='*.ets' 2>/dev/null | wc -l | tr -d ' ')
if [ "$WEB_PAGES" -ge 2 ] && ! ls -d "$ROOT/components/module_webview" >/dev/null 2>&1; then
  echo "P1 R1.3' FAIL: $WEB_PAGES 处 Web({}) 但缺 components/module_webview/"
fi

# 触发器 2: business_common/components 下任意"业务无关"类被 ≥2 个 business 引用 → 应下沉
# 注意：business-coupled UI（如 PptTemplateItem 依赖 PptTemplateBean）不在此列，留在 business_common 是对的
# 自包含原则：components/module_* 是"包含 Bean/VM/Controller/UI 的子系统"，不是单独 UI 容器
# baseline 实证：AI 的 VideoCard 在 module_swipeplayer 里，其 VideoCardModel/AVPlayerManager 也都在 module 内
if [ -d "$ROOT/features/business_common/src/main/ets/components" ]; then
  for f in $(find "$ROOT/features/business_common/src/main/ets/components" -name "*.ets" 2>/dev/null); do
    name=$(basename "$f" .ets)
    # 排除依赖 business 类型的（业务耦合）
    has_biz_dep=$(grep -lE "from '(\.\./)+models/|from '(\.\./)+services/|from '(\.\./)+viewmodels/" "$f" 2>/dev/null | wc -l | tr -d ' ')
    [ "$has_biz_dep" -gt 0 ] && continue
    refs=$(grep -rln "\\b$name\\b" "$ROOT/features/business_"*"/src/main/ets/pages/" --include='*.ets' 2>/dev/null | grep -v business_common | wc -l | tr -d ' ')
    if [ "$refs" -ge 2 ]; then
      echo "P2 R1.3' WARN: $name 业务无关 + 被 $refs 个 business 引用，应下沉 components/module_*/"
    fi
  done
fi

# 触发器 3: 自定义转场 → 应有 module_transition
if grep -rln "PageTransition\|customTransition\|transitionEffect" "$ROOT/features" --include='*.ets' >/dev/null 2>&1; then
  ls -d "$ROOT/components/module_transition" >/dev/null 2>&1 || \
    echo "P2 R1.3' WARN: 检测到自定义转场代码但无 components/module_transition/"
fi

# 触发器 4: 广告 SDK → 必须 module_advertisement（非工具型工程）
if grep -rln "GroMore\|csj\|穿山甲\|RewardVideo\|interstitial" "$ROOT/features" --include='*.ets' >/dev/null 2>&1; then
  ls -d "$ROOT/components/module_advertisement" >/dev/null 2>&1 || \
    echo "P1 R1.3' FAIL: 检测到广告 SDK 调用但无 components/module_advertisement/"
fi

# 注意：不要因为"AI/Scan 都有 6 个 module"就强求当前工程也凑 6 个。
# 工具型工程（PPT/计算器/记事本）功能面窄，少几个 module 是合理的。
# 关键看 grep 触发证据，不看数量。

# business_common 必须存在
test -d "$ROOT/features/business_common" || echo "P0 R1.2: 缺 features/business_common/"
```

---

## R2.0 自建轮子检测（"依赖装了但 0 处 import"）

> 严格度以本 skill 主文档与 customer-checklist 为准；本节仅给检测脚本与可移植的双向判定套路。

最隐蔽的 R2.0 违规：`oh-package.json5` 引入了 `lib_xxx` 私仓，**但业务代码完全没 import**——同时存在自建副本（HttpClient / PreferenceHelper / SafeAreaModel / 自建 AbortController polyfill 等）在用。仅看"装了哪些 lib"或仅看"业务里有没有自建文件"都会漏掉，必须**双向交叉**：

### 双向判定模板（依赖装了 + 业务 import 数 = 0 → 必有副本）

```bash
ROOT=<project_root>

# 通用：所有私仓 lib_* 装了但 0 处 import → 强信号
for lib in lib_common lib_network lib_widget lib_payment lib_starburst lib_umeng lib_hmiap; do
  if grep -q "\"$lib\"" "$ROOT/oh-package.json5" 2>/dev/null; then
    USE=$(grep -rE "from '$lib'" --include='*.ets' \
              "$ROOT/features" "$ROOT/products" 2>/dev/null \
          | wc -l | tr -d ' ')
    [ "$USE" = "0" ] && echo "P1 R2.0: $lib 已装但 0 处 import，必有自建副本未删"
  fi
done
```

### 已知自建副本路径黑名单（命中即必删）

```bash
for f in \
  features/business_common/src/main/ets/network/HttpClient.ets \
  features/business_common/src/main/ets/network/NetworkUtil.ets \
  features/business_common/src/main/ets/network/HttpManager.ets \
  features/business_common/src/main/ets/preferences/PreferenceHelper.ets \
  features/business_common/src/main/ets/preferences/PrefStore.ets \
  features/business_common/src/main/ets/util/AbortController.ets \
  features/business_common/src/main/ets/utils/RouterUtils.ets \
  features/business_common/src/main/ets/models/SafeAreaModel.ets ; do
  test -f "$ROOT/$f" && echo "P1 R2.0: 发现自建副本 $f（必删，迁移到对应私仓 lib_*）"
done

# SafeAreaModel 在 GlobalStateModels.ets 里以 @ObservedV2 class 形式存在的情况
grep -rn '@ObservedV2[[:space:]]*\(class\|export class\)\s*SafeAreaModel\|GlobalState\.safeArea' \
     --include='*.ets' "$ROOT/features" 2>/dev/null \
  && echo "P1 R6.5a: 自建 SafeAreaModel 与私仓 WindowModel 重复，应改走 lib_common WindowModel"
```

具体迁移配方见 [05-network-persistence.md § 自建 wrapper → 私仓迁移配方](./05-network-persistence.md)。

---

## AbortController 三层 grep 判定（反假阳性）

> 仅 grep 到 `AbortController` 不算 PASSED——自建 polyfill 也会命中但根本没 `.signal`，等于规则没遵守。R6.3 系列规则的 audit 必须三层都过：

```bash
ROOT=<project_root>

# 第 1 层：来源正确（必须从 @ohos/axios 导入，禁止自建 polyfill）
LAYER1=$(grep -rE "from '@ohos/axios'" --include='*.ets' \
              "$ROOT/features" "$ROOT/products" 2>/dev/null \
         | grep AbortController | wc -l | tr -d ' ')

# 第 2 层：signal 真传给请求（不是孤立的 AbortController 对象）
LAYER2=$(grep -rnE '\.signal\b' --include='*.ets' \
              "$ROOT/features"/*/src/main/ets/viewmodels \
              "$ROOT/features"/*/src/main/ets/services 2>/dev/null \
         | wc -l | tr -d ' ')

# 第 3 层：abort() 位于页面清理函数（aboutToDisappear / onPageHide / cancelInflight）
LAYER3=$(grep -rnB2 '\.abort()' --include='*.ets' \
              "$ROOT/features" "$ROOT/products" 2>/dev/null \
         | grep -E 'aboutToDisappear|onPageHide|cancelInflight' \
         | wc -l | tr -d ' ')

echo "Layer1 (来源正确)=$LAYER1  Layer2 (signal 透传)=$LAYER2  Layer3 (退出 abort)=$LAYER3"

# 任一层 = 0 → 即使 AbortController 命中再多也判 R6.3 FAIL
[ "$LAYER1" = "0" ] && echo "FAIL R6.3: AbortController 来源不是 @ohos/axios（疑似自建 polyfill）"
[ "$LAYER2" = "0" ] && echo "FAIL R6.3: 没有任何 .signal 透传给请求"
[ "$LAYER3" = "0" ] && echo "FAIL R6.3: .abort() 不在页面清理函数中（aboutToDisappear/onPageHide）"
```

> **为什么需要三层**：自建 polyfill 没 `.signal` 属性 → 即使到处 `new AbortController()` 也是死代码；只有 Layer1+2+3 同时满足，才能证明 abort 链路真的连通。详见 [05-network-persistence.md § 反模式：自建 AbortController polyfill](./05-network-persistence.md)。

---

## R6.10 登录/VIP 判定必须用 LibUserData isBinding / isVip（MUST，2026-05-08 客户实证）

**现象**：业务代码用各种方式自己判登录态和 VIP 态：
```ts
const isLogin = await UserPreferences.isLogin()       // ❌ 读独立 KV
this.isLoggedIn = this.userInfoModel.isLogin           // ❌ 读 UserInfoModel 字段
if (vipLevel > 0) { ... }                             // ❌ 显式数值比较
this.isVip = this.vipLevel > 0;                        // ❌ 同款
if (vipLevel <= 0) { ... }                            // ❌ 反向比较
```

**为什么是 BUG**：
- 私仓 `LibUserData.isBinding()` 内部判定**双条件**：`token.length > 0 && userId > 0 && userState !== 4` 等，业务侧手写 `token > 0` 漏掉 userId / userState 的细节
- 私仓 `LibUserData.isVip()` 内部含 **5 分钟 VIP 保护窗口**（vipManualUpdateTime）—— 支付成功后服务端异步回调慢于客户端时不被覆盖。`vipLevel > 0` 直接读绕过这个保护
- 服务端语义演进（如新增 vipLevel=99 企业账号、userState=5 限制态）私仓自动跟，业务侧手写要全工程排查

**正确实现**：

```ts
import { UserData as LibUserData } from 'lib_common'

// 登录态
if (LibUserData.getInstance().isBinding()) { ... }   // 同步方法，不要 await

// VIP 态
if (LibUserData.getInstance().isVip()) { ... }
if (!LibUserData.getInstance().isVip()) { ... }      // 反向用 ! 而不是 vipLevel <= 0
```

**audit grep**：

```bash
# 1. 业务代码用 await UserPreferences.isLogin() 判登录
grep -rn "await\s\+UserPreferences\.isLogin\s*(" features products --include="*.ets" 2>/dev/null \
  | grep -v "preferences/UserPreferences\.ets" | grep -v build
# 期望 0 命中

# 2. userInfoModel.isLogin 字段读
grep -rn "userInfoModel\.isLogin\b" features products --include="*.ets" 2>/dev/null
# 期望 0 命中

# 3. vipLevel 显式数值比较
grep -rEn "vipLevel\s*(>|<=|<|>=|===|!==)\s*[0-9]" features products --include="*.ets" 2>/dev/null \
  | grep -v "lib_common\|MembershipRefresher\|build"
# 期望 0 命中（MembershipRefresher 5min 保护窗口业务可豁免）

# 4. 正面 grep — 应至少 5+ 处
grep -rn "LibUserData\.getInstance()\.\(isBinding\|isVip\)\(\)\|UserData\.getInstance()\.\(isBinding\|isVip\)\(\)" \
  features products --include="*.ets" 2>/dev/null | grep -v build | wc -l
```

**修复脚本**：

```python
import re
from pathlib import Path
ROOT = Path(".")
for p in ROOT.rglob('*.ets'):
    if '/build/' in str(p) or '/oh_modules/' in str(p): continue
    if 'preferences/UserPreferences.ets' in str(p): continue
    c = p.read_text(encoding='utf-8'); orig = c
    # 1. 登录态判定
    c = re.sub(r"await\s+UserPreferences\.isLogin\(\s*\)", "LibUserData.getInstance().isBinding()", c)
    c = re.sub(r"this\.userInfoModel\.isLogin", "LibUserData.getInstance().isBinding()", c)
    # 2. VIP — 注意先匹配 `this.vipLevel > 0` 再裸 `vipLevel > 0` 否则会出现 `this.LibUserData.getInstance()...` 错误格式
    c = re.sub(r"this\.vipLevel\s*>\s*0", "LibUserData.getInstance().isVip()", c)
    c = re.sub(r"\bvipLevel\s*>\s*0\b", "LibUserData.getInstance().isVip()", c)
    c = re.sub(r"\bvipLevel\s*<=\s*0\b", "!LibUserData.getInstance().isVip()", c)
    if c != orig:
        # 加 import
        if "UserData as LibUserData" not in c:
            m = re.search(r"import\s*\{\s*([^}]+?)\s*\}\s*from\s*['\"]lib_common['\"]", c)
            if m:
                c = c.replace(m.group(0), f"import {{ {m.group(1)}, UserData as LibUserData }} from 'lib_common'", 1)
        p.write_text(c, encoding='utf-8')
```

⚠️ **regex 顺序坑**：`this\.vipLevel > 0` 必须在 `\bvipLevel > 0\b` 之前，否则会把 `this.vipLevel > 0` 匹配为裸 `vipLevel > 0` → 替换出 `this.LibUserData.getInstance().isVip()` 错误形式。

---

## R6.9-A page 持 vm + 冗余 @Local windowModel/breakpointModel（MUST，2026-05-08 客户复审实证）

**现象**：page 顶部同时有：
```ts
private vm: XxxViewModel = new XxxViewModel()                // ← VM extends BaseViewModel，已含 windowModel
@Local windowModel: WindowModel = AppStorageV2.connect(WindowModel, () => new WindowModel())!  // ← 冗余，应删
@Local breakpointModel: BreakpointModel = AppStorageV2.connect(BreakpointModel, () => new BreakpointModel())!  // ← 冗余，应删
```

**为什么是 BUG**：
- 双源 truth — BaseViewModel 内部用一份 windowModel，page 自己又绑一份；视觉上等价但内存里是两个独立实例
- 客户原话："已经有 vm，但是还是单独定义了 WindowModel，应该直接从 vm 获取。这个逻辑是所有页面通用的"
- 这是 **batch VM 抽取后**最容易漏的反模式 — agent 把原本 page 上的 `@Local windowModel` 当作"基础设施 binding"保留，没意识到 vm 已经接手

**正确实现**：

```ts
@ComponentV2
struct XxxPage {
  private vm: XxxViewModel = new XxxViewModel()
  // 没有 @Local windowModel / breakpointModel — vm 已自带

  build() {
    Column() { ... }
      .padding({ top: this.vm.windowModel.windowTopPadding })  // 通过 vm 读
      .padding({ bottom: this.vm.windowModel.windowBottomPadding })
  }
}
```

⚠️ **大小写陷阱**：BaseViewModel 的字段名是 `breakPointModel`（大写 P），不是 `breakpointModel`。替换时：
- ❌ `this.breakpointModel` → `this.vm.breakpointModel` （编译报错：无此字段）
- ✅ `this.breakpointModel` → `this.vm.breakPointModel` （正确）

**audit grep**：

```bash
# 同时持 vm + 冗余 @Local windowModel/breakpointModel 的 page
for f in $(find features products -name '*Page.ets' -path '*/pages/*' 2>/dev/null | grep -v build); do
  has_vm=$(grep -cE "(private|@Local) vm:\s*\w+ViewModel" "$f")
  has_redundant=$(grep -cE "@Local (windowModel|breakpointModel):\s*(WindowModel|BreakpointModel)" "$f")
  [ "$has_vm" -gt 0 ] && [ "$has_redundant" -gt 0 ] && echo "VIOLATION: $f"
done
# 期望 0 命中
```

**修复脚本**（sed 批量）：

```python
import re
from pathlib import Path
ROOT = Path(".")
WINDOW_LINE = re.compile(
    r'^\s*@Local\s+windowModel:\s*WindowModel\s*=\s*AppStorageV2\.connect\(.*?\)!\s*\n', re.MULTILINE)
BP_LINE = re.compile(
    r'^\s*@Local\s+breakpointModel:\s*BreakpointModel\s*=\s*AppStorageV2\.connect\(.*?\)!\s*\n', re.MULTILINE)
for p in ROOT.rglob('*Page.ets'):
    if 'build' in str(p): continue
    c = p.read_text(encoding='utf-8')
    if not re.search(r'(?:private|@Local)\s+vm:\s*\w+ViewModel\s*=', c): continue
    c = WINDOW_LINE.sub('', c)
    c = BP_LINE.sub('', c)
    c = re.sub(r'\bthis\.windowModel\b', 'this.vm.windowModel', c)
    c = re.sub(r'\bthis\.breakpointModel\b', 'this.vm.breakPointModel', c)  # ← 注意 P 大写
    p.write_text(c, encoding='utf-8')
```

**Phase 3 batch agent prompt 必须显式说明**：抽 VM 后**必须删** `@Local windowModel` 和 `@Local breakpointModel`，访问点全文替换 `this.windowModel` → `this.vm.windowModel`、`this.breakpointModel` → `this.vm.breakPointModel`（**P 大写**）。

---

## R6.4a dataorm entity 主键必须 nullable + DAO 用 dataorm 原生 API（MUST，2026-05-08 客户实证）

**现象**：DAO 实现里业务自己写 `relationalStore.ValuesBucket = { 'uid': form.uid, 'taskId': form.taskId, ...28 个字段... }`，然后调 `store.insert('VideoForm', bucket)` raw API。  
而 entity 主键定义为 `id: number = 0`。

**为什么是 BUG**：
- 字面值 `0` 不被 dataorm `bindValues` 跳过（`if (entity[name] !== null && !== undefined)`）
- INSERT 时 SQL 写入 id=0 字面值 → sqlite INTEGER PRIMARY KEY 不 autoincrement
- 用 `insertOrReplace`：第二条 INSERT id=0 → 替换第一条 → 列表只看到一条最近插入
- 用 `insert`：第二条 INSERT id=0 → UNIQUE 冲突 / SQL 报错

**正确实现**（详见 [05-network-persistence.md § R6.4a](./05-network-persistence.md#r64a-dataorm-主键字段必须-nullablemust2026-05-08-客户实证)）：

```ts
// Entity 主键 nullable
@Id()
@Columns({ columnName: 'id', types: ColumnType.num })
id: number | null = null

// DAO 一行原生调用
async insertVideo(form: VideoForm): Promise<number> {
  return await this.videoDao.insertOrReplace(form)
}

// 业务消费 — 非空断言（DB 加载的 entity 有 id）
const sceneId: number = scene.id!
```

**audit grep**：

```bash
# 1. entity 主键仍是 number = 0（应改 nullable）
grep -B1 "id:\s*number\s*=\s*0\b\|pid:\s*number\s*=\s*0\b" \
  features/business_common/src/main/ets/model/entities/*.ets 2>/dev/null
# 期望 0 命中

# 2. DAO 内业务自拼 ValuesBucket（应直接 dao.insertOrReplace(entity)）
grep -rn "ValuesBucket\s*=\s*{" features --include="*Dao.ets" 2>/dev/null
# 期望 0 命中

# 3. DAO 用 raw RdbStore.insert（应用 BaseDao）
grep -rn "getRawDatabase\|getRawStore\|store\.insert\(" features --include="*Dao.ets" 2>/dev/null
# 期望 0 命中

# 4. runtime 验证：
# hdc shell hilog | grep "saved.*dbId="
# 多次操作生成数据，dbId 应递增非 0
```

**修复步骤**：

1. 修改所有 entity 主键字段：`id: number = 0` → `id: number | null = null`（pid 同理）
2. 重写 DAO insert 方法：删除手动 ValuesBucket 拼装，改用 `dao.insertOrReplace(entity)` 一行
3. 删除 `private daoSession` / `getRawStore()` 桥接方法（不再需要）
4. 业务侧（Repository / VM）凡是消费 `entity.id` 传给 `number` 参数的地方，改为 `entity.id!`
5. 编译过 + 装机：生成多条数据，确认 hilog 里 dbId 递增非 0

**反辩白**：

- ❌ "我看 dataorm 把 id=0 写入 SQL 了，只能绕过" → bindValues 跳 null/undefined，**改字段类型为 nullable**才是对的
- ❌ "改 nullable 业务代码很多 entity.id 引用编译报错" → 用 `entity.id!` 非空断言
- ❌ "raw RdbStore.insert 也走 sqlite 啊" → 偏离 dataorm 设计：schema migration / type binding / identity scope 都失效

---

## R6.8-F 登录链路必须走 `lib_network.AccountApi`（MUST，2026-05-08 客户实证第 4 次）

**现象**：LoginViewModel 用业务自建 `userApiService.bindMobileBySmsCode(params)` / `userApiService.bindWx(code)` / `userApiService.bindAli(authCode)` / `userApiService.logout()`，登录成功后通过 `applyUserDataToLib(userData)` 私有方法把服务端返回的 13+ 个用户字段（token / userId / vipLevel / nickName / headUrl / userState / phoneAuth / vipDays / ...）手动 mirror 到 `LibUserData` 单例。

**为什么是 BUG**：
- 与 R6.7（initUser 走私仓）同款问题，只是路径换成"登录"
- 业务侧手写 `lib.X = userData.X` 就是双源 truth — 一旦私仓 `lib_network` 内部 init 流程没跟着跑（拦截器签名缓存 / SDK init flag / saveUserInfo 落盘），后续请求会断链
- 客户 2026-05-08 直接圈出 LoginViewModel 64-110 行代码并附 `LoginVM(1).ets` 标准实现 — 这是同款反模式第 4 次返工

**正确实现**（详见 [05-network-persistence.md § R6.8-F](./05-network-persistence.md)）：
```ts
private accountApi: AccountApi = new AccountApi();   // 私仓单例
async loginWithSms(): Promise<boolean> {
  const ok = await this.accountApi.bindPhone(this.phone, this.smsCode);  // 私仓自治
  if (ok) EventBusHelper.emit(EventId.LOGIN_OUT, { isLogin: true });
  return ok;
}
async loginByWechat(code: string) { return this.accountApi.wechatLogin(code); }
async loginWithHuawei(resp) { return this.accountApi.harmonyLogin(resp); }
async logout() { await this.accountApi.signOut(); /* 私仓自治清 LibUserData */ }
async sendSmsCode() { this.accountApi.sendSmsCode(this.phone); }
```

**audit grep**：
```bash
# 1. LoginVM 不应有 applyUserDataToLib / mirror / copy / save 等 mirror 方法
grep -rn "applyUserDataToLib\|mirrorUserData\|copyUserData\|saveUserToLib" \
  features --include="*ViewModel.ets" 2>/dev/null
# 期望 0

# 2. LoginVM 不应调业务自建 userApi 登录方法
grep -rn "userApi\.\(bindMobile\|bindWx\|bindAli\|logout\)\|userApiService\.\(bindMobile\|bindWx\|bindAli\|logout\)" \
  features --include="*ViewModel.ets" 2>/dev/null
# 期望 0 — 应全部走 AccountApi

# 3. LoginVM 范围内不应对 LibUserData 字段写
grep -rn "lib\.\(token\|userId\|vipLevel\|nickName\|headUrl\|avatar\|phoneAuth\|userState\|fromChannel\|vipDays\|vipContent\|vipTitle\|h5ProductPageUrl\|contactUsUrl\|showAd\)\s*=" \
  features/business_login --include="*.ets" 2>/dev/null
# 期望 0

# 4. business_login/oh-package.json5 必须有 lib_network 直接依赖
grep '"lib_network"' features/business_login/oh-package.json5 || echo "❌ R6.8-F: business_login 缺 lib_network 直接依赖"

# 5. AccountApi 实例字段（正面 grep — 应至少存在）
grep -rn "AccountApi\s*=\s*new\s\+AccountApi" features/business_login --include="*ViewModel.ets" 2>/dev/null
# 期望至少 1 处（LoginViewModel 持有）
```

**修复模板**：

| 替换原方法 | 新方法（lib_network.AccountApi） |
|---|---|
| `userApiService.bindMobileBySmsCode({mobile, smsCode})` | `accountApi.bindPhone(phone, smsCode): Promise<boolean>` |
| `userApiService.bindWx(code)` | `accountApi.wechatLogin(code): Promise<boolean>` |
| `userApiService.bindAli(authCode)` | （AccountApi 未提供 → 写 ADR 偏离登记）|
| 自建 huawei login + handler | `accountApi.harmonyLogin(response): Promise<boolean>` |
| `userApiService.logout()` | `accountApi.signOut(): Promise<boolean>` |
| `appApiService.sendSmsCode(phone)` | `accountApi.sendSmsCode(phone): void` |
| `userApiService.closeAccount()` | `accountApi.closeAccount(): Promise<boolean>` |
| `userApiService.getInfo()` | `accountApi.getInfo()` 或直接读 `LibUserData.getInstance()` |

**整改步骤**：
1. 删 `applyUserDataToLib` / 任何手动 lib.X 赋值方法
2. 删 `finalizeLoginSession` 内的 `UserPreferences.setUserId/setNickname/...` 字段写（仅保留 `LOGIN_OUT` 事件广播 + `setPhone` 等业务自有非用户态字段）
3. 替换所有自建登录调用为 AccountApi 对应方法
4. `business_login/oh-package.json5` 加 `"lib_network": "1.1.8"` 直接依赖
5. 编译过 + LoginPage 跑一遍：手机号登录 / 微信登录 / 退出登录

---

## 真实回归模式（2026-04 用户审核录入）

> 以下 5 条来自一次完整 refactor 后用户的审核反馈。它们的共同点：**编译期不报错，audit 不一定显式标红，但都违反"私仓优先 / 业务边界 / VM 化彻底 / 资源归属"四大原则**。Phase 1 audit 必须显式扫这 5 条；Phase 4 verify 也要再扫一次防回归。

### RR1（MUST）：壳工程 `commons/` 残留本地 `lib_common` / `lib_widget` 子模块

**现象**：refactor 已经在 oh-package.json5 引入了私仓 `lib_common@x.x.x`，但工程根 `commons/lib_common`、`commons/lib_widget` 子模块**仍然存在**（HAR/HSP 形态），entry/features 的 import 一半走私仓、一半走本地路径。

**为什么是 BUG**：违反"私仓优先原则（R2.0）"——只要本地副本存在，IDE 自动补全 / hvigor 解析就有 50% 概率拿本地，导致 RouterUtils / BaseViewModel 等单例被双份加载，运行时行为分裂。

**audit grep**：
```bash
# RR1 命中即 P0
[ -d commons/lib_common ] && echo "❌ RR1: commons/lib_common 本地副本未删（应只走私仓）"
[ -d commons/lib_widget ] && echo "❌ RR1: commons/lib_widget 本地副本未删（应只走私仓）"

# 同时反查 import：仍指向本地路径的视为残留 ref
grep -rE "from ['\"]\.\.?/.*commons/lib_(common|widget)" --include="*.ets" --include="*.ts" \
  | head && echo "❌ RR1: 仍存在指向本地 commons/lib_* 的 import"
```

**修复**：删除 `commons/lib_common`、`commons/lib_widget` 整个目录；改回根 `build-profile.json5` modules 列表；统一所有 import 为 `from 'lib_common'` / `from 'lib_widget'`。

---

### RR2（MUST）：冗余 `PageMap.ets` —— 已用 `Navigation(RouterUtils.getStack())` 就不应再写 PageMap

**现象**：Index.ets 已经 `Navigation(RouterUtils.getStack()) {}`（空 body，未 `.navDestination(...)`），同时工程里又**额外**写了一份 `pages/PageMap.ets`，里面用 `if (name === RouterMap.XXX) { XxxPage() }` 长 if-else 分发。两份并存，PageMap 实际是死代码。

**为什么是 BUG**：`lib_common` 的 `RouterUtils` 已经内置了基于 `@RouterMap` 注解的全局注册（即 [04-state-routing.md § R6.2-CRITICAL 表中的"方案 C"](./04-state-routing.md)）。手写 PageMap 等于在 RouterUtils 之上叠了一层手写分发，违反 R2.0 自建轮子原则；且 PageMap 没挂到 Navigation 的 `.navDestination()` 上，写了也不生效。

**audit grep**：
```bash
# RR2.a：Index.ets 用 RouterUtils.getStack() 但没挂 navDestination → PageMap 必然冗余
INDEX=$(find products -name Index.ets -path "*/pages/*" | head -1)
if grep -q 'Navigation(RouterUtils\.getStack()' "$INDEX" \
   && ! grep -q '\.navDestination(' "$INDEX"; then
  # 此时若工程内还存在 PageMap @Builder → 100% 死代码
  find . -name "PageMap.ets" -not -path "*/oh_modules/*" | grep -q . \
    && echo "❌ RR2: 检测到冗余 PageMap.ets（RouterUtils.getStack() 已自带注册分发）"
fi
```

**修复**：删除 `pages/PageMap.ets`；删除 `RouterMap` 中纯字符串常量（若仅供 PageMap 使用）；保持 Index.ets `Navigation(RouterUtils.getStack()) {}` 不变；各 page 通过 `@RouterMap({ name: ... })` 装饰器（lib_common 提供）声明自己。

---

### RR3（MUST）：ViewModel 放在错误的模块（不限于 business_common）

**现象（两种子模式）**：

- **RR3-a**（原 RR3）：业务专属 VM 堆在 `business_common/viewmodels/`——如 `PptCreateViewModel`、`VipViewModel` 放在 business_common 而非对应 feature。
- **RR3-b**（2026-04 新增）：VM 放在**错误的 business 模块**——如 `SplashViewModel` 放在 `business_login/viewmodel/` 而非 `business_home/viewmodel/`（SplashPage 所在模块）。判定标准：**VM 必须与其主调 Page 同模块**。

**为什么是 BUG**：违反 R1.2 业务粒度原则 + 职责单一。
- RR3-a：business_common 变垃圾桶 + 循环依赖 + 删 feature 时残留。
- RR3-b：VM 跨模块放置导致 ① 阅读困难（在 login 目录找不到 SplashVM）；② 模块依赖方向反转（home 依赖 login 才能用 SplashVM）；③ 违背「同一功能的 Page + VM + Service 同模块内聚」原则。

**audit grep**：
```bash
# RR3-a：扫 business_common/viewmodels/* 文件名前缀，匹配到 business_xxx 命名空间
COMMON_VM_DIR=$(find features -path "*/business_common/*" -type d -name "viewmodel*" | head -1)
[ -n "$COMMON_VM_DIR" ] && for f in "$COMMON_VM_DIR"/*.ets; do
  base=$(basename "$f" .ets)
  echo "$base" | grep -qE '^(Ppt|Template|Works|Vip|Auth|FileScan|Mine|Login|Home|Splash)' \
    && echo "❌ RR3-a: $base 是业务专用 VM，应迁回对应 features/business_*/viewmodel/"
done

# RR3-b：扫每个 VM 文件里的 class 名，检查其主调 Page 是否在同模块
for biz in features/business_*/; do
  biz_name=$(basename "$biz")
  vm_dir="$biz/src/main/ets/viewmodel"
  [ -d "$vm_dir" ] || continue
  for vm_file in "$vm_dir"/*.ets; do
    [ -f "$vm_file" ] || continue
    # 提取 VM class 名
    vm_classes=$(grep -oE 'export class (\w+ViewModel)\b' "$vm_file" | awk '{print $3}')
    for cls in $vm_classes; do
      # 从 class 名推断对应 Page：SplashViewModel → SplashPage, PptCreateViewModel → CreateOutlinePage 等
      # 更可靠方式：grep 哪些 pages 实际 import 或 new 这个 VM
      page_module=$(grep -rl "new $cls\b\|: $cls " features/business_*/src/main/ets/pages/*.ets 2>/dev/null | head -1)
      if [ -n "$page_module" ]; then
        page_biz=$(echo "$page_module" | sed 's|features/\(business_[^/]*\)/.*|\1|')
        if [ "$page_biz" != "$biz_name" ]; then
          echo "❌ RR3-b: $cls 定义在 $biz_name 但主调 Page 在 $page_biz → 应迁到 $page_biz/viewmodel/"
        fi
      fi
    done
  done
done

# 配套检查：features/business_*/viewmodel/ 是否空目录
for d in features/business_*/src/main/ets/viewmodel; do
  [ -d "$d" ] && [ -z "$(ls -A "$d" 2>/dev/null)" ] \
    && echo "⚠️ RR3: $d 是空目录（VM 可能被错放到其他模块）"
done
```

**修复**：
- RR3-a：按文件名前缀回迁——`PptXxxViewModel` → `business_ppt/viewmodel/`；`VipXxxViewModel` → `business_vip/viewmodel/` 等。
- RR3-b：按主调 Page 归属迁移——`SplashViewModel` 的主调是 `business_home/pages/SplashPage.ets` → 迁到 `business_home/viewmodel/`。同文件内多个不同模块的 class 必须拆文件再分别迁移。
- 回迁后 grep 更新所有 import 路径。

---

### RR4（SHOULD→MUST 当 VM 已存在）：页面残留 `@Local` / `@State` 而对应 VM 已建立

**现象**：refactor 已经为页面引入了 ViewModel（如 Index.ets 持有 `vm: IndexVM = new IndexVM()`），但页面 struct 内仍然保留 `@Local isEnabled: boolean = true` 这类**应当下沉到 VM 的状态**；副作用（aboutToAppear 调一堆 vm.xxxListener、windowStageEventListener）也散落在页面而非 VM 自己负责。

**为什么是 BUG**：违反 R6.1c "VM 化彻底"原则。判定标准：**只要状态会被 VM 内任意方法读 / 写，或会跨页面共享，就必须放 VM**。页面应只保留"纯 UI 局部状态"（如临时折叠 / 输入框编辑值）。否则后续 VM 的 `setInterception()` / 转场逻辑被迫到页面里 mutate `this.isEnabled`，破坏单向数据流。

**audit grep**：
```bash
# RR4：扫 page 文件中 @Local/@State 数量，配合 VM 存在判断
for page in $(find features/business_*/src/main/ets/pages -name "*.ets" 2>/dev/null) \
            $(find products -path "*/pages/*.ets" 2>/dev/null); do
  has_vm=$(grep -cE '\bvm\s*[:=].*ViewModel|=\s*new\s+\w+ViewModel' "$page")
  local_cnt=$(grep -cE '^\s*@(Local|State)\s+\w+' "$page")
  if [ "$has_vm" -gt 0 ] && [ "$local_cnt" -gt 0 ]; then
    echo "⚠️ RR4: $page 已有 VM 但仍有 $local_cnt 处 @Local/@State（核查能否下沉到 VM）"
  fi
done
```

**修复策略**：
1. 凡是被页面副作用回调 mutate 的状态 → 下沉到 VM，VM 用 `@Trace` 暴露
2. 仅在 page build() 渲染分支用、且不跨方法 → 保留 @Local
3. 转场 / 拦截 / 监听这类副作用本身（如 `customNavContentTransition` 里 `onTransitionStart`）→ 把闭包内的状态切换迁到 VM 方法（`vm.beginTransition()` / `vm.endTransition()`），page 只调用方法

**配套：VM 字段必须 @Trace**——@ObservedV2 类下的字段，**只有 @Trace 装饰的字段写入才触发 UI 重渲染**。如果 page 把 @Local 全删了改读 `vm.field`，但 VM 字段没 `@Trace`，编译期不报错，**运行时 UI 假死**（首次值显示后再无更新）。每次 RR4 整改完成后，必须 grep 一下确认 VM 文件里的反应字段都有 `@Trace`：
```bash
# 检查每个 VM 文件中的 class 字段是否带 @Trace（按缩进 2 空格 + 标识符 + : 类型 = 默认值识别）
for vm in $(find features -name "*ViewModel.ets" -not -path "*/oh_modules/*"); do
  total=$(grep -cE '^  [a-zA-Z_][a-zA-Z0-9_]*\s*:\s*[^=]+= ' "$vm")
  traced=$(grep -cE '^  @Trace ' "$vm")
  [ "$total" -gt 0 ] && echo "$vm: traced=$traced / fields=$total"
done
```
触发条件：refactor 后某 VM 中 `traced < fields` 且 page 用 `vm.field` 直接读 → P1 漏 @Trace。

---

### RR5（MUST）：资源全堆在壳工程，没按业务模块归属

**现象（两种子模式）**：

- **RR5-a**（原 RR5）：`products/phone/.../media/` 里堆了几十张图，但壳工程 ets 代码 0 处引用，所有引用来自 features。
- **RR5-b**（2026-04 新增）：`products/phone/.../element/color.json` 和 `string.json` 里堆了大量**业务专属**颜色和字符串（如 `color_login_subtitle`、`login_phone_hint`、`tab_create` 等），但这些资源只在对应 feature 模块中使用。**壳工程不被任何 feature 依赖**，因此 feature 布局文件中用 `$r('app.color.xxx')` / `$r('app.string.xxx')` 引用壳工程的资源，**在模块级编译时会报错**（找不到资源定义）。

**为什么是 BUG**：
- **RR5-b 尤其严重**：壳工程不在 features 的依赖链上。虽然最终打包时资源会合并，但 DevEco Studio 做模块级增量编译、或其他 HAR/HSP 被独立编译时，引用壳工程的颜色/字符串**直接编译报错**。这不是"建议"而是"必改"。
- 删除某 feature 时，对应资源残留成死资源
- 多业务复用资源若放在某个 feature 而不是 business_common，会触发跨 feature 引用反模式

**audit grep**：
```bash
# RR5-a：壳工程 media 数量 vs 壳工程 ets 引用数量
SHELL_MEDIA_DIR=$(find products/*/src/main/resources/base -type d -name media | head -1)
[ -n "$SHELL_MEDIA_DIR" ] && {
  shell_imgs=$(ls "$SHELL_MEDIA_DIR" 2>/dev/null | grep -cE '\.(webp|svg|png|jpg)$')
  shell_refs=$(grep -rohE 'app\.media\.[a-zA-Z_0-9]+' products/*/src/main/ets/ 2>/dev/null | sort -u | wc -l)
  feature_refs=$(grep -rohE 'app\.media\.[a-zA-Z_0-9]+' features/*/src/main/ets/ 2>/dev/null | sort -u | wc -l)
  echo "shell media: $shell_imgs files, shell ets refs: $shell_refs, feature ets refs: $feature_refs"
  if [ "$shell_imgs" -gt 5 ] && [ "$feature_refs" -gt $((shell_refs * 5)) ]; then
    echo "❌ RR5-a: 壳工程囤了 $shell_imgs 张图，但绝大部分实际引用来自 features ($feature_refs vs $shell_refs)，应按业务下沉"
  fi
}

# RR5-b：壳工程 color.json / string.json 中的业务专属资源
SHELL_ELEMENT_DIR=$(find products/*/src/main/resources/base -type d -name element | head -1)
[ -n "$SHELL_ELEMENT_DIR" ] && {
  # 扫 color.json 中 name 带业务前缀的条目
  if [ -f "$SHELL_ELEMENT_DIR/color.json" ]; then
    biz_colors=$(grep -oE '"name":\s*"[^"]*"' "$SHELL_ELEMENT_DIR/color.json" \
      | grep -iE 'login|home|tab|mine|ppt|template|vip|create|splash|feedback|upload' | wc -l)
    total_colors=$(grep -c '"name"' "$SHELL_ELEMENT_DIR/color.json")
    [ "$biz_colors" -gt 3 ] && echo "❌ RR5-b: 壳工程 color.json 有 $biz_colors/$total_colors 条业务专属颜色（如 login_*/tab_*/ppt_*），应下沉到对应 feature 或 business_common"
  fi
  # 扫 string.json 中 name 带业务前缀的条目
  if [ -f "$SHELL_ELEMENT_DIR/string.json" ]; then
    biz_strings=$(grep -oE '"name":\s*"[^"]*"' "$SHELL_ELEMENT_DIR/string.json" \
      | grep -iE 'login|home|tab|mine|ppt|template|vip|create|splash|feedback|upload' | wc -l)
    total_strings=$(grep -c '"name"' "$SHELL_ELEMENT_DIR/string.json")
    [ "$biz_strings" -gt 3 ] && echo "❌ RR5-b: 壳工程 string.json 有 $biz_strings/$total_strings 条业务专属字符串，应下沉到对应 feature 或 business_common"
  fi
}

# RR5-c：features 模块的 media 目录是否为空（应当不为空）
for f in features/business_*/src/main/resources/base/media; do
  if [ -d "$f" ]; then
    cnt=$(ls "$f" 2>/dev/null | wc -l)
    [ "$cnt" -eq 0 ] && echo "⚠️ RR5-c: $f 是空目录"
  fi
done
```

**RR5-b 归属判定规则**（element 资源 — color / string / float）：
1. 资源名带明确业务前缀（`login_*`、`tab_*`、`ppt_*`、`vip_*` 等）→ 迁到对应 feature 的 `element/color.json` 或 `string.json`
2. 资源名是通用色（`color_main`、`color_page_bg`、`color_text` 等规范 19 个 token）→ 迁到 `business_common`
3. 资源名是通用 UI 色但非规范命名（`color_title_color`、`white`、`translate` 等）→ 重命名为规范名后迁到 `business_common`
4. 壳工程仅保留：`start_window_background`（启动窗口色）、`module_desc`（模块描述）、`EntryAbility_*`（入口描述）等**壳工程自身配置**必需的条目
5. 多 feature 共用的字符串/颜色 → 迁 `business_common`
6. **迁移后代码中 `$r('app.color.xxx')` / `$r('app.string.xxx')` 不需要改**——HarmonyOS 资源合并机制保证引用名不变

**归属判定规则**（按引用方计算，不按文件名猜业务）：
1. 对 `products/*/src/main/resources/base/media/` 里每张图 X：
   - grep `app.media.X` 在所有 features 模块出现的次数
   - 出现 **0 个 feature** → 死资源（壳/系统图标除外，如 icon/foreground/background.png 用于 `module.json5` icon 字段，必须留壳）
   - 出现 **1 个 feature** → 迁到该 feature 的 `src/main/resources/base/media/`
   - 出现 **≥2 个 feature** → 迁到 `business_common/src/main/resources/base/media/`（多业务共享）
2. 例外保留在壳工程的资源（白名单）：
   - `module.json5` 的 `icon` 字段引用的（应用图标）
   - `app.json5` / launcher 配置引用的
   - splash/启动图（如果 phone shell 直接用，否则也应下沉）
   - 这些"系统级配置资源"留壳，**业务页面用的资源全部下沉**

**ArkTS 下资源跨模块自动可见**：把图片从 `products/phone/.../media/` 移到 `features/business_xxx/.../media/` 后，源代码里的 `$r('app.media.xxx')` **不需要改**——HarmonyOS 资源以 bundleName 为命名空间统一查找，feature 模块（HSP/HAR）资源在打包时合并到 hap 资源池，业务页面用 `app.media.xxx` 直接命中。这是 RR5 整改的最大利好：**只 git mv 文件，零代码改动**。

**audit 必带的副产物**：每次 RR5 整改前，先生成 `image-ownership.md` 清单——逐张图列出 [被哪些 features 引用 / 引用次数 / 建议归属]，用户拍板归属再动文件。

---

## RR3 / RR5 / RR6 的对称性原则（2026-04 反思补全）

> **客户反馈触发的反思**（2026-04）：客户指出 SplashViewModel 错放、color/string 还在壳、HttpClient 重复造轮子三个问题。这三个问题**根因相同**——「不在正确位置」/「在不该在的位置」/「自造私仓已有的能力」。原 RR3/RR5/RR6 只覆盖了三个最显眼的子场景，但同一根因的其他变体没覆盖，导致 audit 漏报。
>
> **统一三原则**（audit 阶段每条违规都按这三个角度过一遍）：
>
> | 原则 | 一句话 | 漏报后果 |
> |---|---|---|
> | **A. 错位放置** | "X 必须在使用它的最小作用域内" | 跨模块依赖 / 删 feature 时残留 |
> | **B. 壳工程瘦身** | "壳工程只保留 EntryAbility 启动逻辑 + module/app 配置必需，其他全部下沉" | feature 编译报错（壳不被依赖）/ 删 feature 时残留 |
> | **C. 私仓优先** | "私仓有等价能力时禁止造轮子，单点豁免仅限极窄一次性调用" | 偏离规范 / 后续维护两套 |

---

### RR3 扩展（2026-04）：错位放置不只 VM

**RR3-c**（MUST）：**Service 错位**——业务专属 service 错放在 `business_common/services/`（如 `PptService`、`VipService` 仅被某一个 feature 引用），或错放在另一个 business（如 `LoginService` 在 business_home）。

**RR3-d**（MUST）：**Bean / 数据模型错位**——业务专属 DTO（如 `PptDraft`、`VipPackageInfo`）错放在 `business_common/bean/`，仅被一个 feature 使用。

**RR3-e**（SHOULD）：**Component / Dialog 错位**——业务专属组件（如 `LoginPrivacyDialog`、`PptTemplateCard`）放在 `business_common/components/` 或 `lib_widget`（私仓），但仅被一个 feature 引用。

**audit grep 模板**（套用同一脚本，按目录类型循环）：
```bash
# RR3-c/d/e 通用：扫 business_common 下各类目录，检查文件名前缀是否带业务关键词
for sub in services service bean beans components dialog dialogs util utils; do
  COMMON_SUB=$(find features -path "*/business_common/*" -type d -name "$sub" | head -1)
  [ -z "$COMMON_SUB" ] && continue
  for f in "$COMMON_SUB"/*.ets; do
    [ -f "$f" ] || continue
    base=$(basename "$f" .ets)
    if echo "$base" | grep -qE '^(Ppt|Template|Works|Vip|Auth|FileScan|Mine|Login|Home|Splash|Feedback|Upload|AfterSale|Refund|Renew|MemberCenter|CustomerService|AboutUs|WebView|ChoiceTemplate|TemplatePreview|TemplateSelect|CreateOutline|FileUpload|PPTFile)'; then
      # 进一步检查是否真的只被一个 feature 引用
      ref_features=$(grep -rl "$base" features/business_*/src/main/ets/ 2>/dev/null \
        | grep -oE 'features/business_[^/]+' | sort -u | grep -v business_common | wc -l)
      [ "$ref_features" -le 1 ] && echo "❌ RR3 ($sub): $base 仅被 $ref_features 个非 common feature 引用，应下沉"
    fi
  done
done
```

**RR3-f**（MUST）：**多 class 一文件且跨模块**——同一 .ets 文件内 export 多个 class，且这些 class 按 RR3-b 归属应该在不同 business 模块（如 `AuthViewModel.ets` 同时含 `SplashViewModel` 和 `LoginViewModel`，前者主调 Page 在 business_home，后者在 business_login）。

```bash
# RR3-f：扫 ets 文件，提取 export class 列表，每个 class 按主调 Page 反查归属
for f in $(find features -name "*.ets" -path "*/viewmodel/*" -not -path "*/oh_modules/*"); do
  classes=$(grep -oE 'export class (\w+ViewModel)\b' "$f" | awk '{print $3}')
  modules=""
  for cls in $classes; do
    page_file=$(grep -rl "new $cls\b\|: $cls " features/business_*/src/main/ets/pages/ 2>/dev/null | head -1)
    [ -n "$page_file" ] && modules+=" $(echo "$page_file" | sed 's|features/\(business_[^/]*\)/.*|\1|')"
  done
  uniq_modules=$(echo "$modules" | tr ' ' '\n' | sort -u | grep -v '^$' | wc -l)
  if [ "$uniq_modules" -gt 1 ]; then
    echo "❌ RR3-f: $f 内多 class 跨模块（涉及：$(echo "$modules" | tr ' ' '\n' | sort -u)），必须拆文件"
  fi
done
```

---

### RR5 扩展（2026-04）：壳工程囤积不只资源

**RR5-d**（MUST）：**float.json / boolean.json 业务条目残留**——同 RR5-b 模式，扫壳工程 element 目录所有 json 文件中的业务前缀名。

**RR5-e**（MUST）：**Pages 残留壳工程**——`products/*/src/main/ets/pages/` 下含**业务页面**（除 `Index.ets` 入口外）。所有业务页面必须在 `features/business_*/src/main/ets/pages/`。

**RR5-f**（MUST）：**业务 Service / Util / Bean 残留壳工程**——`products/*/src/main/ets/{services,util,bean,viewmodel}/` 不应存在；这些类必须在对应 feature 内。壳工程 ets 仅保留 `EntryAbility.ets`、`Index.ets`（路由入口）、以及壳级别配置类（如 NetworkInit / SplashInit 等启动初始化）。

```bash
# RR5-d：壳工程 float.json / boolean.json
for f in products/*/src/main/resources/base/element/float.json \
         products/*/src/main/resources/base/element/boolean.json; do
  [ -f "$f" ] || continue
  biz_count=$(grep -oE '"name":\s*"[^"]*"' "$f" \
    | grep -iE 'login|home|tab|mine|ppt|template|vip|create|splash|feedback|upload' | wc -l)
  [ "$biz_count" -gt 0 ] && echo "❌ RR5-d: $f 有 $biz_count 条业务条目，应下沉"
done

# RR5-e：壳工程 pages 下是否含非入口页面
SHELL_PAGES_DIR=$(find products/*/src/main/ets -type d -name pages | head -1)
[ -n "$SHELL_PAGES_DIR" ] && {
  for p in "$SHELL_PAGES_DIR"/*.ets; do
    [ -f "$p" ] || continue
    base=$(basename "$p" .ets)
    case "$base" in
      Index|RouterBuilders|PageMap) ;;  # 允许的入口/路由文件
      *) echo "❌ RR5-e: 壳工程残留业务页面 $p，应迁到 features/business_*/pages/" ;;
    esac
  done
}

# RR5-f：壳工程 ets 下是否有 services/util/bean/viewmodel 目录
for d in products/*/src/main/ets/services products/*/src/main/ets/service \
         products/*/src/main/ets/util products/*/src/main/ets/utils \
         products/*/src/main/ets/bean products/*/src/main/ets/beans \
         products/*/src/main/ets/viewmodel products/*/src/main/ets/viewmodels; do
  [ -d "$d" ] && [ -n "$(ls -A "$d" 2>/dev/null)" ] \
    && echo "❌ RR5-f: 壳工程残留 $d（业务代码不应在壳）"
done
```

---

### RR6 扩展（2026-04）：私仓重复轮子的全谱清单

**RR6 已覆盖**：HttpClient 重复封装（R6.3-CRITICAL）。

**RR6-b 至 RR6-g**（全部 MUST）：以下私仓能力同样禁止造轮子。检测方式统一：grep 私仓符号 `import { X } from 'lib_*'` 是否存在；若同时存在自定义同名/同职责类，则违规。

| 编号 | 自造轮子模式 | 私仓等价 | grep 模式 |
|---|---|---|---|
| **RR6-b** | 自定义 Logger / LogUtil 类 | `Logger from 'lib_common'` | `class (Logger\|LogUtil\|MyLog\|HiLog)\b` |
| **RR6-c** | 自定义路由工具（router.pushUrl 包装层） | `RouterUtils from 'lib_common'` | `class (Router\|RouterHelper\|NavHelper\|PageRouter)\b` |
| **RR6-d** | 自定义 KV 存储工具（preferences 包装层） | `PreferenceUtil from 'lib_common'` | `class (PrefsUtil\|StorageHelper\|KvStore\|MyPreference)\b` |
| **RR6-e** | 自定义 Toast / Snackbar / Dialog 容器 | `lib_widget` 已有 | `class (Toast\|MyToast\|Snackbar\|CustomDialog)\b` 且非 lib_widget 内部 |
| **RR6-f** | 自定义 DateUtil / StringUtil / ScreenUtil / DeviceUtil | `lib_common` 已有 | `class (DateHelper\|StringHelper\|ScreenHelper\|DeviceInfo)` 且 lib_common 已 import |
| **RR6-g** | 自定义事件总线 / EventHub | `lib_common` 已有 EventHub | `class (EventBus\|MyEventHub\|EventEmitter)\b` 且非 RxJS/原生 emitter |

```bash
# RR6-b 至 RR6-g 通用扫描
declare -A WHEEL_PATTERNS=(
  ["RR6-b Logger"]="class (Logger|LogUtil|MyLog|HiLog)\b"
  ["RR6-c Router"]="class (Router|RouterHelper|NavHelper|PageRouter)\b"
  ["RR6-d Preference"]="class (PrefsUtil|StorageHelper|KvStore|MyPreference)\b"
  ["RR6-e Widget"]="class (Toast|MyToast|Snackbar|CustomDialog)\b"
  ["RR6-f Common Util"]="class (DateHelper|StringHelper|ScreenHelper|DeviceInfo)\b"
  ["RR6-g EventBus"]="class (EventBus|MyEventHub|EventEmitter)\b"
)
for label in "${!WHEEL_PATTERNS[@]}"; do
  pattern="${WHEEL_PATTERNS[$label]}"
  hits=$(grep -rlE "$pattern" features/ products/ --include='*.ets' 2>/dev/null \
    | grep -v oh_modules | head -5)
  [ -n "$hits" ] && echo "⚠️ $label 命中可疑自造类：$hits（核查私仓是否已有等价能力）"
done

# RR6 反自我安慰检查：扫文件内是否有「单点豁免」「lib_network 单点豁免」「MAY 例外」等自我说服式注释
grep -rln '单点豁免\|MAY 例外\|MAY 豁免\|sole exemption\|grandfathered' \
  features/ products/ --include='*.ets' 2>/dev/null | while read -r f; do
  # 只要文件 > 200 行 + 含完整 class（非单函数）→ 豁免不成立
  lines=$(wc -l < "$f")
  has_full_class=$(grep -cE 'static (async )?(get|post|put|delete)<' "$f")
  if [ "$lines" -gt 200 ] && [ "$has_full_class" -ge 2 ]; then
    echo "❌ RR6: $f 自称单点豁免但实际是完整封装（$lines 行，$has_full_class 个 HTTP 方法）→ 不接受豁免"
  fi
done
```

---

### audit 阶段反自我安慰原则（2026-04 新增）

> **背景**：上一轮 refactor 中 HttpClient.ets 在文件头写了 30 行注释自证「符合 AI baseline 单点 axios MAY 豁免」，agent 据此放行。但实际：① 不是单点（30+ 调用方）；② 不是 axios（混用 http.createHttp）；③ 不是窄场景（覆盖 GET/POST/upload/download/multipart 全谱）。**自证注释不能作为豁免证据**。

**Phase 1 audit / Phase 4 ② 重审 必须遵守**：

1. **代码内注释/ADR 中宣称的「MAY 豁免 / 单点例外 / 已评估保留」绝不直接信**——必须用 grep 重新核对实际边界（行数、调用方数、覆盖方法数）。
2. **execution-log 中「我评估后保留本地实现」要倒查**——查 ADR 的「不选择的方案」段是否真有「试过私仓 → 失败」的可复现证据，而非「我觉得」。
3. **MAY 豁免有上限**：单点 axios MAY 上限 = **1 个调用点 + ≤30 行 + 不形成可复用类**。命中三者任一上限即升级为 MUST 违规。

加进 Phase 4 ② 「重跑 audit 对比改造前后」步骤前，**先跑反自我安慰扫描**（上面 RR6 反自我安慰那段 grep），命中即列入 P0 待修。


