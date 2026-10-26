# 帧动画 (AnimationDrawable) / SVGA 迁移参考

**适用判定**：
- `<animation-list>` + `<item drawable=... duration=.../>` 在 `res/drawable/*.xml` → **AnimationDrawable / 帧动画**
- 代码 `(view.background as AnimationDrawable).start()` → **AnimationDrawable**
- `SVGAImageView` / `SVGAParser` / `.svga` 文件在 assets → **SVGA**

二者本质都是"序列帧"——一个用 PNG 数组，一个用 zlib 压缩的私有格式。HarmonyOS 端：
- 帧动画 → 内置 `ImageAnimator` 直接对标
- SVGA → 没有官方等价，需要降级或重做

---

## 1. AnimationDrawable → `ImageAnimator`

### 对照示例

Android：
```xml
<!-- res/drawable/loading.xml -->
<animation-list xmlns:android="http://schemas.android.com/apk/res/android"
    android:oneshot="false">
  <item android:drawable="@drawable/img_0" android:duration="100"/>
  <item android:drawable="@drawable/img_1" android:duration="100"/>
  <item android:drawable="@drawable/img_2" android:duration="100"/>
  <!-- ... -->
</animation-list>
```

```kotlin
val anim = view.background as AnimationDrawable
anim.start()
```

ArkTS（V2 推荐）：

```typescript
@ComponentV2
struct LoadingAnim {
  @Local animState: AnimationStatus = AnimationStatus.Running;

  build() {
    ImageAnimator()
      .images([
        { src: $r('app.media.img_0'), duration: 100 },
        { src: $r('app.media.img_1'), duration: 100 },
        { src: $r('app.media.img_2'), duration: 100 },
        // ...
      ])
      .iterations(-1)              // -1 = 无限循环（对齐 oneshot=false）
      .state(this.animState)
      .width(100)
      .height(100)
      .onStart(() => { console.info('start'); })
      .onFinish(() => { console.info('finish'); })
  }
}
```

### Android `oneshot` 对照

| Android `android:oneshot` | ArkTS `iterations` |
|---|---|
| `"false"`（默认 / 循环） | `-1` |
| `"true"`（播一次） | `1` |
| 自定义次数（Android 没原生支持，需手动 stop） | `N`（任意正整数） |

### 控制 API 对照

| Android | ArkTS |
|---|---|
| `anim.start()` | `state(AnimationStatus.Running)` |
| `anim.stop()` | `state(AnimationStatus.Stopped)` |
| `anim.isRunning` | 自己用 `@Local` 跟踪（V1 项目用 `@State`） |
| `setOnFinishedListener` | `.onFinish(() => ...)` |

### 资源迁移

```bash
# 把 drawable 里的序列帧 PNG 拷到 media
SRC=/path/to/android/lib-xxx/src/main/res/drawable
DST=$(pwd)/entry/src/main/resources/base/media

cp $SRC/img_*.png $DST/   # 同名直接对齐
```

如果原工程 PNG 在 `drawable-xxhdpi/` 等密度目录里，**只取一份**（HarmonyOS 不区分密度，按 vp 自动缩放），优先 `xxhdpi` 或 `xxxhdpi` 高密度版本。

### 适用场景与边界

✅ **适合**：5~30 帧的简单循环（loading 圈、表情动效、按钮 hover）

❌ **不适合**：
- 帧数 > 30 → PNG 体积爆炸 + 解码内存高，**改 Lottie**
- 含复杂矢量变换（旋转/缩放/路径变化）→ ImageAnimator 只能切换图片，做不到，**改 Lottie**
- 帧间需要插值（中间状态平滑过渡）→ 必须用属性动画

---

## 2. SVGA → 没有官方鸿蒙等价

ohpm 公网仓搜不到 `@xxx/svga`。**3 种走法，按推荐度排序**：

### 2.1 首选：转 Lottie（重导）

拿 SVGA 源工程的 AE 工程文件（`.aep`），让设计师**重导一份 Lottie JSON + 图集**。

**为什么**：
- 体积更小（SVGA zlib 压缩看着小，但解出来 + 渲染开销其实更大）
- 鸿蒙官方支持，未来稳定
- Lottie 兼容 iOS / Android / Web，多端统一
- 重导成本：设计师在 AE 里安装 bodymovin 插件，导出选 JSON+resources，5 分钟一个

走完 §1 之后，按 [`lottie.md`](./lottie.md) 流程接入即可。

### 2.2 兜底：拆帧走 ImageAnimator

如果拿不到源 AE 文件、又有强烈"必须现在上"的压力，**用 SVGA 工具拆出 PNG 序列**：

1. 找 [SVGA 在线预览器](https://svga.io/) 或本地 player 工具，把 `.svga` 解出每帧 PNG
2. 按 §1 路径放到 `entry/src/main/resources/base/media/`
3. 用 ImageAnimator 播

**代价**：
- 帧多体积爆炸（一个 60 帧的 SVGA 拆出来可能几 MB→几十 MB）
- 失去矢量优势，缩放糊
- 无法动态换肤

适合短期止血，不适合长期方案。

### 2.3 不推荐：自己写 SVGA 解码 / WebView 内嵌

- **自写解码器**：SVGA 是封闭格式（zlib + protobuf），解码 + Canvas 绘制全栈实现 ≥ 数千行，对接成本远高于重导 Lottie
- **`SVGAPlayer-Web` + WebView**：性能差，列表滚动场景明显卡，且 WebView 启动开销大；只适合首页大礼物动画且不在 list 里的极个别场景

---

## 3. 决策速查

```
有 SVGA 文件
  │
  ├─ 能拿到 AE 源文件？
  │   ├─ 能 → 重导 Lottie，走 lottie.md   ← 首选
  │   └─ 不能 → 下一步
  │
  ├─ 帧数 ≤ 30 且只是简单序列帧？
  │   └─ 拆帧走 ImageAnimator   ← 兜底
  │
  └─ 帧数 > 30 或含矢量变换？
      └─ 找设计师补 AE 源文件 → 重导 Lottie
         （拒绝拆帧，体积/性能不可接受）
```

---

## 4. 常见坑

### 4.1 帧动画 PNG 顺序错乱

ArkTS `images: [{ src, duration }]` 是**按数组顺序播**，不是按文件名排序。**显式按 `img_0..N` 顺序写数组**：

```typescript
// 错（顺序乱了画面就乱）
const frames = [
  { src: $r('app.media.img_3'), duration: 100 },
  { src: $r('app.media.img_1'), duration: 100 },
  // ...
];

// 对（按数字索引顺序）
const frames = Array.from({ length: 10 }, (_, i) => ({
  src: $r(`app.media.img_${i}`),
  duration: 100,
}));
```

### 4.2 ImageAnimator 不指定 `width/height`

不显示。和 Lottie Canvas 同问题——必须给容器尺寸。

### 4.3 `state(AnimationStatus.Running)` 写死，不响应外部控制

如果想根据条件 stop/resume，要用 `@Local`（V1 项目用 `@State`）包：

```typescript
// 错（写死 Running，没法 stop）
ImageAnimator().state(AnimationStatus.Running)

// 对（V2 推荐）
@ComponentV2
struct PausableAnim {
  @Local animState: AnimationStatus = AnimationStatus.Initial;

  build() {
    ImageAnimator().state(this.animState)
  }

  // 触发：
  start(): void { this.animState = AnimationStatus.Running; }   // 开始播
  pause(): void { this.animState = AnimationStatus.Paused; }    // 暂停
  stop(): void  { this.animState = AnimationStatus.Stopped; }   // 停止
}
```

### 4.4 拆帧 SVGA 后忘记测内存

序列帧 PNG 全部解码到内存。`hdc shell hidumper -s WindowManagerService` 看下进程内存，超 200MB 就不能上了——**必须改 Lottie**。
