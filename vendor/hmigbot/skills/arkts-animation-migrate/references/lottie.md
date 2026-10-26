# Lottie 迁移参考（@ohos/lottie）

**适用判定**：Android 端命中以下任意一项：
- `app:lottie_fileName="..."` / `app:lottie_imageAssetsFolder="..."` 在 XML
- `LottieAnimationView` / `LottieDrawable` 在 Kotlin/Java
- `assets/` 下有 `.json` 文件（头部含 `"v":"x.x.x"`, `"fr":24`, `"layers":[...]`，bodymovin 导出特征）+ 配套 PNG 图集子目录

这是 90% 复杂动画的来源，HarmonyOS 走 `@ohos/lottie` 几乎能 1:1 还原。

---

## 1. 安装

```bash
# 工程根目录
ohpm install @ohos/lottie@2.0.30   # 或 ohpm 仓库最新稳定版
```

执行后 `oh-package.json5` 自动追加：

```json5
"dependencies": {
  "@ohos/lottie": "2.0.30"
}
```

---

## 2. 资源迁移

### 路径映射

| Android 路径 | HarmonyOS 路径 |
|---|---|
| `lib-xxx/src/main/assets/fit_part_1.json` | `entry/src/main/resources/rawfile/fit_part_1.json` |
| `lib-xxx/src/main/assets/part_one_pre/img_0.png` | `entry/src/main/resources/rawfile/part_one_pre/img_0.png` |

**关键约束**：图集子目录名**必须与 Android `lottie_imageAssetsFolder` 完全一致**——`part_one_pre` ≠ `part1_pre` ≠ `partOnePre`。Lottie JSON 内部 `assets[].p` 是按这个目录名拼路径的。

### 拷贝命令模板

```bash
SRC=/path/to/android/project/lib-xxx/src/main/assets
DST=$(pwd)/entry/src/main/resources/rawfile

cp $SRC/fit_part_1.json $DST/
cp -r $SRC/part_one_pre $DST/   # 整子目录搬，保留所有 img_*.png
```

### 易漏检查项（按优先级）

1. **JSON `assets[]` 列出的每张图都能在子目录里找到**——缺一张就部分空白
2. **子目录名拼写、大小写**——macOS HFS+ 大小写不敏感，但设备文件系统大小写敏感
3. **PNG 命名**：`img_0.png` `img_1.png` ... 连续，中间不能跳号
4. **JSON 不要被 IDE 自动格式化**——某些工具会改 number precision，导致动画播放异常

---

## 3. LottieView 通用组件（**复用，不要每页重写**）

新建一次，全工程复用。本工程模板（[components/common/LottieView.ets](entry/src/main/ets/components/common/LottieView.ets)）：

```typescript
import lottie, { AnimationItem } from '@ohos/lottie';

@ComponentV2
export struct LottieView {
  /** JSON 文件名（相对 rawfile/） */
  @Param path: string = '';
  /** 图集子目录名（相对 rawfile/） */
  @Param assetsFolder: string = '';
  /** 唯一名（多个 Lottie 同时存在时必填且互不相同；destroy 按 name 释放） */
  @Param name: string = 'lottieAnim';
  /** 是否循环播放 — 对齐 Android lottie_loop */
  @Param loop: boolean = true;
  /** 是否进入即播放 — 对齐 Android lottie_autoPlay */
  @Param autoPlay: boolean = true;
  /**
   * 播放开关（可见性驱动的控制口）。默认 true = 保持原行为不变（单个 Lottie / 全屏场景无需传）。
   * 多页 / 列表场景传入「本项是否可见」→ 仅可见项播放、不可见项 pause。见 §6.1。
   */
  @Param playing: boolean = true;

  private settings: RenderingContextSettings = new RenderingContextSettings(true);
  private context: CanvasRenderingContext2D = new CanvasRenderingContext2D(this.settings);
  private anim: AnimationItem | undefined = undefined;

  aboutToDisappear(): void {
    try { lottie.destroy(this.name); } catch (_) { /* ignore */ }
    this.anim = undefined;
  }

  // playing 变 true → play()，变 false → pause()。@Monitor 属 @ComponentV2 体系，监听 @Param。
  @Monitor('playing')
  onPlayingChange(): void {
    if (this.anim === undefined) {
      return;
    }
    if (this.playing) {
      this.anim.play();
    } else {
      this.anim.pause();
    }
  }

  build() {
    Canvas(this.context)
      .width('100%')
      .height('100%')
      .backgroundColor(Color.Transparent)
      .onReady((): void => {
        // 页面 reuse 场景：同名动画若已存在先 destroy 再 load，避免重复绘制
        try { lottie.destroy(this.name); } catch (_) { /* ignore */ }

        this.anim = lottie.loadAnimation({
          container: this.context,
          renderer: 'canvas',
          loop: this.loop,
          autoplay: this.autoPlay && this.playing,   // 初始就不可见的项别自动播
          name: this.name,
          path: this.path,
          imagePath: this.assetsFolder.length > 0 ? this.assetsFolder + '/' : undefined,
        });
        // onReady 晚于首次 @Monitor 触发的情况下，用当前 playing 对齐一次状态
        if (!this.playing) {
          this.anim.pause();
        }
      });
  }
}
```

> `AnimationItem.play()` / `.pause()` 来自 `@ohos/lottie`（lottie-web 兼容层）实例方法，与模板返回的 `this.anim`（`loadAnimation` 的返回值）配套。

需要在 `@ComponentV2` 组件里用 `@Monitor` 才能监听 `@Param playing` 的变化——这是 V2 体系里驱动「按可见性播放/暂停」的标准接线。

---

## 4. 调用方 — 对齐 Android XML

| Android XML | LottieView Param | 备注 |
|---|---|---|
| `app:lottie_fileName="fit_part_1.json"` | `path: 'fit_part_1.json'` | 相对 rawfile/，**不带前缀** |
| `app:lottie_imageAssetsFolder="part_one_pre"` | `assetsFolder: 'part_one_pre'` | **不带 `/` 前缀** |
| `app:lottie_loop="true"` | `loop: true` | |
| `app:lottie_autoPlay="true"` | `autoPlay: true` | |

> `loop` / `autoPlay` 等标志位**必须逐控件显式落地**（`loadAnimation` 的 `loop`/`autoplay` 显式为 true），不要静默依赖鸿蒙默认值——Android 与鸿蒙的默认取值不保证一致。

调用示例：

```typescript
LottieView({
  path: 'fit_part_1.json',
  assetsFolder: 'part_one_pre',
  name: 'partOnePreLottie',  // 唯一
})
  .width('100%')
  .height(300)
```

---

## 5. 容器尺寸与坐标对齐

Android 端 `LottieAnimationView` 通常配 `android:layout_marginStart=Xdp` `android:layout_marginEnd=Xdp` `app:layout_constraintHorizontal_creator=parent`（水平居中）+ `app:layout_constraintVertical_bias=0.359`（垂直偏移）。

ArkTS 端用 `position()` 时要把 margin 翻译成 x：

```typescript
// 错：只设 y，x 默认 0 → 容器贴左边，看上去歪
LottieView({...})
  .position({ y: '35.889%' })

// 对：x 也要算（67vp 来自 Android marginStart=67dp）
LottieView({...})
  .position({ x: 67, y: '35.889%' })
  .width('100%')   // 或 .width(`calc(100% - ${67 * 2}vp)`)
```

**翻译公式**：
- `position.x = marginStart` (Android dp ≈ ArkTS vp)
- `position.y = constraintVertical_bias × parentHeight` （或直接写 `'35.889%'`）
- `width = parentWidth - marginStart - marginEnd`

---

## 6. 多 Lottie 同屏 / 列表场景

`name` **必须唯一**。`lottie.destroy(name)` 是按 name 释放——两个组件同 name，destroy 一个会把另一个也销毁。

```typescript
// name 用 idx / 业务 id 区分，全工程唯一
ForEach(this.items, (item: Item, idx: number) => {
  LottieView({
    path: item.lottiePath,
    assetsFolder: item.lottieAssets,
    name: `item_${idx}`,    // ← 用 idx 区分
  })
})
```

> **上面这段只解决 name 唯一，不解决「同时播放」。** 把它直接套进 Swiper / ViewPager / 多页表情面板 = 所有格子无条件 `autoPlay` 同播（几十个 Canvas 同时跑动画，功耗炸裂，且与 Android「回收→只播可见项」的原行为不符）。**多页 / 可滚动列表场景必须加可见性驱动，见 §6.1。**

---

## 6.1 列表 / 多页：只播可见项（Swiper / ViewPager 表情面板等）

**场景**：Android 端 `ViewPager2 + RecyclerView` / 多页表情面板，靠 ViewHolder 回收，天然只有可见页在播。迁到 ArkTS 的 `Swiper + ForEach + LottieView`，若每格 `autoPlay: true` 就变成**全量同播**——这不是 Android 原行为的还原。

**症状**：翻页流畅度差 / 发热 / 后台页动画照跑。

**修复**：给每个 `LottieView` 传 §3 模板的 `playing` 开关，只让当前可见页为 `true`。

### 方案 A — Swiper.onChange 驱动（多页容器首选）

`Swiper.onChange(event: Callback<number>)` 回调返回当前显示页索引；用一个 `@Local currentPage` 记录，每格按「所在页 === currentPage」决定 `playing`。

```typescript
@Entry
@ComponentV2
struct EmojiPanel {
  @Local pages: EmojiPage[] = /* ... chunked 分页 ... */ [];
  @Local currentPage: number = 0;   // 当前可见页

  build() {
    Swiper() {
      ForEach(this.pages, (page: EmojiPage) => {
        Grid() {
          ForEach(page.ids, (id: number) => {
            GridItem() {
              LottieView({
                path: `emoji/emoji_${id}.json`,
                name: `emoji_${id}`,
                loop: true,
                autoPlay: true,
                playing: page.pageIndex === this.currentPage,  // 只有当前页在播
              })
                .width(50)
                .height(50)
            }
          }, (id: number) => id.toString())
        }
        .columnsTemplate('1fr 1fr 1fr 1fr')
      }, (page: EmojiPage) => page.pageIndex.toString())
    }
    .onChange((index: number) => {   // 翻页 → 切换哪一页在播
      this.currentPage = index
    })
    .indicator(Indicator.dot())      // 指示器高亮是 onChange 的「顺带」用途，不能只做这个
  }
}
```

> **只把 onChange 用于指示器高亮 = 没做可见性控制。** onChange 的首要职责是切换「哪一页在播」，指示器是附带。

### 方案 B — 可见性回调驱动（垂直长列表 / 单个组件自管）

组件自己监听可见比例，不依赖外层维护索引。用通用事件 `onVisibleAreaApproximateChange`（API 17+，自定义组件内 API 18+，比 `onVisibleAreaChange` 省功耗，有执行间隔限制）：

```typescript
// 回调类型 VisibleAreaChangeCallback = (isExpanding: boolean, currentRatio: number) => void
LottieView({ path: 'x.json', name: 'x', playing: this.visible })
  .width(50)
  .height(50)
  .onVisibleAreaApproximateChange(
    { ratios: [0.0, 0.5], expectedUpdateInterval: 500 },
    (isExpanding: boolean, currentRatio: number) => {
      this.visible = currentRatio > 0    // 露出即播，划走即停
    }
  )
```

API < 17 用 `onVisibleAreaChange(ratios: Array<number>, callback)`（API 9+）同理，只是无间隔限制、每帧计算、注册多了有功耗代价。

### 帧动画（ImageAnimator）同类场景

若这一类是 `ImageAnimator` 序列帧而非 Lottie（见 frame-and-svga.md §1），API 17+ 直接用单属性 `.monitorInvisibleArea(true)`——系统按 `onVisibleAreaChange` 判定自动暂停/播放，无需手写可见性回调。

```typescript
ImageAnimator()
  .images(frames)
  .iterations(-1)              // -1 = 无限循环
  .monitorInvisibleArea(true)  // 不可见时自动暂停（API 17+）
```

**自检**：多页 / 列表 Lottie 迁移后，翻到第 2 页时第 1 页动画应停；后台 / 划出屏幕的项不应继续跑。

---

## 7. 常见坑

### 7.1 Canvas 没 `onReady` 就 loadAnimation

```typescript
// 错：context 还没绑 Canvas，loadAnimation 静默失败
build() {
  Canvas(this.context)
  // 此时若外部代码已调 lottie.loadAnimation(this.context, ...) → 不渲染
}

// 对
build() {
  Canvas(this.context).onReady(() => {
    this.anim = lottie.loadAnimation({ container: this.context, ... })
  })
}
```

### 7.2 多 Lottie 同 name → `destroy` 互相影响

详见 §6。规则：`name` 全工程内唯一（含列表场景）。

### 7.3 rawfile 子目录名带 `/` 前缀

```typescript
// 错
imagePath: '/part_one_pre/'

// 对
imagePath: 'part_one_pre/'
```

### 7.4 JSON 路径写错

```typescript
// 错（path 是相对 rawfile/，不要加任何前缀）
path: './fit_part_1.json'
path: 'rawfile/fit_part_1.json'

// 对
path: 'fit_part_1.json'
```

### 7.5 容器没显式宽高 / 宽高为 0

Lottie Canvas 渲染区域 0×0 → 看上去什么都没有。**LottieView 外层调用必须给 width/height**：

```typescript
// 错（外层没尺寸，Canvas 0×0）
Column() {
  LottieView({...})
}

// 对
Column() {
  LottieView({...})
    .width('100%')
    .height(200)
}
```

### 7.6 aboutToDisappear 不 destroy

内存泄漏。列表里上下滑几次内存涨几倍。模板里已含 `aboutToDisappear() { lottie.destroy(this.name) }`，**别删**。

### 7.7 资源缺 `img_X.png`（最隐蔽）

Lottie 静默 fallback 到空。**截图特征**：部分图层在动 + 部分位置空白方框。

排查方法：

```bash
# 1. 看 JSON 列出的所有图
cat entry/src/main/resources/rawfile/fit_part_1.json \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('\n'.join(a['p'] for a in d.get('assets',[]) if 'p' in a))"

# 2. 对照磁盘
ls entry/src/main/resources/rawfile/part_one_pre/

# 3. 缺哪张补哪张（从 Android assets 目录补）
```

历史范例：本工程 [`5d3ed1f`](#) 就是补这种缺漏（PartFive NICE Lottie `gy_complete_data.json` 缺 `imagesComplete*/img_0..7.png`）。

### 7.8 多页 / 列表 Lottie 全量同播（不还原 Android 回收行为）

Swiper / ViewPager / 多页面板里每格 `autoPlay: true` = 几十个动画同时跑，且后台页照播。Android 端靠 ViewHolder 回收只播可见项。**修复见 §6.1**（Swiper.onChange 或 onVisibleAreaApproximateChange 驱动 `playing`）。

---

## 8. 历史 commit 范例（按演进顺序）

| Commit | 场景 | 学习点 |
|---|---|---|
| [`fc2a348`](#) `接入 @ohos/lottie + 4 个 PrePage Lottie 还原` | 首次接入 | LottieView 组件诞生 + 4 套 fit_part_*.json + 4 套图集迁移 |
| [`bd6ee25`](#) `PartFour SPORTS 步补齐机器人 Lottie` | 二次复用 | 复用 LottieView + 新增 gy_jqr_eye_up_down.json + jqr_eye/img_0..3.png |
| [`5d3ed1f`](#) `PartFive NICE Lottie 缺失资源` | 资源补漏 | 典型"动画在播但部分空白"症状 → 查 JSON `assets[]` |

读这 3 个 commit 的 diff 是最快理解 Lottie 迁移实战的方式。
