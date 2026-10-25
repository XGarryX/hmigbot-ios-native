# 媒体应用动效模式（V2）

> 本文档基于 ArkTS V2（API 12+ 推荐）。**本项目锁 V2**，本文档为主参考。
> 动画 API（`Progress / SymbolGlyph / Canvas / TransitionEffect`）在 V1/V2 完全相同；状态装饰器从 V1 升级到 V2：`@Component` → `@ComponentV2`、`@State` → `@Local`、`@Prop` → `@Param + @Once`、`@StorageLink('isPlaying')` → `AppStorageV2.connect(PlaybackModel, 'playback', () => new PlaybackModel())!`（配合 `@ObservedV2` 类）。
> V1 版本查阅请见 [`media-app-animations.md`](./media-app-animations.md)。
>
> **必要 import**：用到 `AppStorageV2.connect(...)` 的文件顶部须有 `import { AppStorageV2 } from '@kit.ArkUI';`（真实模块导出，非 ambient；漏则 `Cannot find name 'AppStorageV2'`）。用到 `curves.*` 同理 `import { curves } from '@kit.ArkUI';`。

> 基于 AntennaPod ArkTS 播客应用实战总结的 4 种动效模式：下载进度环、播放按钮切换、MiniPlayer 显隐、半圆统计图。
> 源码参考：`entry/src/main/ets/pages/Index.ets`、`entry/src/main/ets/components/statistics/HalfCircleChart.ets`

---

## 0. 全局播放状态 — @ObservedV2 + AppStorageV2

V2 用 `@ObservedV2` 类聚合所有播放相关字段，再通过 `AppStorageV2.connect()` 全局共享，替代 V1 分散的 `@StorageLink('xxx')`：

```typescript
// entry/src/main/ets/model/PlaybackModel.ets
import { AppStorageV2 } from '@kit.ArkUI';   // AppStorageV2 是真实模块导出，必须 import

@ObservedV2
export class PlaybackModel {
  @Trace isPlaying: boolean = false
  @Trace currentEpisodeId: string = ''
  @Trace progressMs: number = 0
  @Trace durationMs: number = 0
  @Trace isPlayerVisible: boolean = false
  @Trace isFullPlayerVisible: boolean = false
}

// 全局 connect 助手
export function getPlaybackModel(): PlaybackModel {
  return AppStorageV2.connect(
    PlaybackModel,
    'playback',
    () => new PlaybackModel()
  )!
}
```

业务侧（PlaybackController 单例）改为直接修改类属性：

```typescript
// V1: AppStorage.setOrCreate<boolean>('isPlaying', true)
// V2:
private model: PlaybackModel = getPlaybackModel()

private onPlaying(): void {
  this.model.isPlaying = true   // @Trace 触发所有 connect 同 key 的组件刷新
}

private onPaused(): void {
  this.model.isPlaying = false
}
```

---

## 1. 下载进度环 — Progress Ring

使用 `Progress` 组件的 `Ring` 类型，value 动态绑定下载百分比。Progress / SymbolGlyph 等组件 API 在 V1/V2 完全相同。

### 基本用法

```typescript
Progress({ value: this.downloadProgress, total: 100, type: ProgressType.Ring })
  .width(32)
  .height(32)
  .color('#007DFF')
  .style({ strokeWidth: 3 })
```

### 带百分比文字的进度环

```typescript
Stack() {
  Progress({ value: this.downloadProgress, total: 100, type: ProgressType.Ring })
    .width(36).height(36)
    .color('#007DFF').backgroundColor('#E0E0E0')
    .style({ strokeWidth: 3 })

  Text(this.downloadProgress.toString() + '%')
    .fontSize(9).fontColor('#007DFF')
}
```

### 三态下载按钮（完整模式 — V2）

```typescript
@ComponentV2
struct EpisodeDownloadButton {
  @Param @Once episodeId: string = ''
  @Local downloadProgress: number = -1   // -1=非下载中
  @Local isDownloaded: boolean = false

  build() {
    Stack() {
      if (this.downloadProgress >= 0) {
        // 下载中 — 进度环 + 取消手势
        Stack() {
          Progress({ value: this.downloadProgress, total: 100, type: ProgressType.Ring })
            .width(36).height(36).color('#007DFF').style({ strokeWidth: 3 })
          SymbolGlyph($r('sys.symbol.xmark'))
            .fontSize(12).fontColor(['#007DFF'])
        }
        .onClick(() => {
          DownloadManager.getInstance().cancelDownload(this.episodeId)
          this.downloadProgress = -1
        })
      } else if (this.isDownloaded) {
        // 已下载 — 完成图标
        SymbolGlyph($r('sys.symbol.checkmark_circle_fill'))
          .fontSize(24).fontColor(['#4CAF50'])
      } else {
        // 未下载 — 下载图标
        SymbolGlyph($r('sys.symbol.arrow_down_circle'))
          .fontSize(24).fontColor(['#666666'])
          .onClick(() => { /* 开始下载 */ })
      }
    }
  }
}
```

### 数据驱动（V2 — EventBus 推送 → @Local）

```typescript
aboutToAppear(): void {
  bus.subscribe(EVENT_DOWNLOAD_PROGRESS, (data: Object) => {
    if (data instanceof DownloadProgressData) {
      if (data.episodeId === this.episodeId) {
        this.downloadProgress = data.percent  // @Local 变化触发 UI 重绘
      }
    }
  })
}
```

如果同一进度需要被多个组件同步，把 `downloadProgress` 提升到 `@ObservedV2` 类，组件用 `@Param` 持有该类实例（见 §2 PlaybackModel 模式）。

---

## 2. 播放按钮切换 — SymbolGlyph 动态图标 + AppStorageV2

使用三元表达式切换 `play_fill` 和 `pause_fill` 图标。V2 用 `AppStorageV2 + @ObservedV2 PlaybackModel` 替代 V1 的 `@StorageLink('isPlaying')`。

### MiniPlayer 播放按钮（V2）

```typescript
@ComponentV2
struct MiniPlayerPlayButton {
  @Local model: PlaybackModel = getPlaybackModel()  // 来自 §0 的全局助手

  build() {
    Column() {
      SymbolGlyph(this.model.isPlaying ? $r('sys.symbol.pause_fill') : $r('sys.symbol.play_fill'))
        .fontSize(20).fontColor(['#333333'])
    }
    .width(36).height(36).borderRadius(18)
    .backgroundColor('#E8E8E8')
    .justifyContent(FlexAlign.Center).alignItems(HorizontalAlign.Center)
    .onClick(() => {
      PlaybackController.getInstance().playPause()
    })
  }
}
```

### FullPlayer 大播放按钮（V2）

```typescript
@ComponentV2
struct FullPlayerPlayButton {
  @Param model: PlaybackModel = new PlaybackModel()  // 父组件 connect 后传入

  build() {
    Column() {
      SymbolGlyph(this.model.isPlaying ? $r('sys.symbol.pause_circle_fill') : $r('sys.symbol.play_circle_fill'))
        .fontSize(56).fontColor(['#333333'])
    }
    .onClick(() => {
      PlaybackController.getInstance().playPause()
    })
  }
}
```

### 状态驱动（V2 — 直接改 @Trace 属性）

```typescript
// PlaybackController 在状态变化时更新 PlaybackModel 的 @Trace 属性
private model: PlaybackModel = getPlaybackModel()

private onPlaying(): void {
  this.model.isPlaying = true   // → SymbolGlyph 自动切换到 pause_fill
}

private onPaused(): void {
  this.model.isPlaying = false  // → SymbolGlyph 自动切换到 play_fill
}
```

### 常用媒体图标对照（V1/V2 通用）

| 功能 | 图标资源 |
|------|---------|
| 播放 | `$r('sys.symbol.play_fill')` |
| 暂停 | `$r('sys.symbol.pause_fill')` |
| 播放（圆形） | `$r('sys.symbol.play_circle_fill')` |
| 暂停（圆形） | `$r('sys.symbol.pause_circle_fill')` |
| 后退 10 秒 | `$r('sys.symbol.gobackward_10')` |
| 快进 30 秒 | `$r('sys.symbol.goforward_30')` |
| 上一曲 | `$r('sys.symbol.backward_end_fill')` |
| 下一曲 | `$r('sys.symbol.forward_end_fill')` |
| 收藏 | `$r('sys.symbol.heart')` / `$r('sys.symbol.heart_fill')` |
| 下载 | `$r('sys.symbol.arrow_down_circle')` |
| 已完成 | `$r('sys.symbol.checkmark_circle_fill')` |

---

## 3. MiniPlayer 显隐 — if 条件渲染

MiniPlayer 使用 `if` 条件控制显隐。当条件从 false 变为 true 时，组件被创建并渲染；反之被销毁。

### 基本模式（V2）

```typescript
@ComponentV2
struct AppRoot {
  @Local model: PlaybackModel = getPlaybackModel()

  build() {
    Stack() {
      // 主内容
      MainContent()

      // 条件：有播放内容 且 不在全屏模式
      if (this.model.isPlayerVisible && !this.model.isFullPlayerVisible) {
        Column() {
          MiniPlayerPlayButton()
          // ... 其他 MiniPlayer 内容
        }
        .width('100%')
        .backgroundColor('#FAFAFA')
        .shadow({ radius: 4, color: '#1A000000', offsetY: -2 })
      }
    }
  }
}
```

### 添加过渡动画（可选增强）

```typescript
if (this.model.isPlayerVisible && !this.model.isFullPlayerVisible) {
  Column() { /* MiniPlayer */ }
    .transition(TransitionEffect.OPACITY.animation({ duration: 200 }))
    .transition(TransitionEffect.translate({ y: 60 }).animation({ duration: 250 }))
}
```

### Tab 栏联动隐藏（V2）

```typescript
// FullPlayer 打开时 Tab 栏也隐藏
if (!this.model.isFullPlayerVisible) {
  Row() {
    // Tab 按钮...
  }
  .height(56)
}
```

### 状态流转（V2）

```
初始: model.isPlayerVisible=false, model.isFullPlayerVisible=false
  → MiniPlayer 隐藏, Tab 栏可见

播放开始: PlaybackController 设置 model.isPlayerVisible = true（@Trace）
  → MiniPlayer 出现, Tab 栏可见

点击 MiniPlayer: NavPathStack.pushPath('FullPlayer')
  → FullPlayer.onReady 设置 model.isFullPlayerVisible = true
  → MiniPlayer 消失, Tab 栏消失

FullPlayer 返回: NavPathStack.pop()
  → FullPlayer.onDisAppear 设置 model.isFullPlayerVisible = false
  → MiniPlayer 恢复, Tab 栏恢复

播放停止: PlaybackController 设置 model.isPlayerVisible = false
  → MiniPlayer 消失
```

---

## 4. 半圆统计图 — Canvas 自定义绘制

使用 `Canvas` + `CanvasRenderingContext2D` 绘制半圆弧形统计图，用于播放时长统计。Canvas API 在 V1/V2 完全相同。

### 基本结构（V2）— @ObservedV2 段数据 + @Param 传入

```typescript
@ObservedV2
export class ChartSegment {
  @Trace value: number = 0
  @Trace color: string = '#007DFF'
  @Trace label: string = ''
}

@ComponentV2
export struct HalfCircleChart {
  @Param @Once segments: ChartSegment[] = []
  @Param @Once totalValue: number = 0
  private settings: RenderingContextSettings = new RenderingContextSettings(true)
  private context: CanvasRenderingContext2D = new CanvasRenderingContext2D(this.settings)

  build() {
    Column() {
      Canvas(this.context)
        .width('100%').height(160)
        .onReady(() => { this.drawChart() })
    }
  }

  // 当 segments 变化时重新绘制
  @Monitor('segments', 'totalValue')
  onSegmentsChange(monitor: IMonitor): void {
    this.drawChart()
  }

  private drawChart(): void {
    const ctx = this.context
    const width = ctx.width
    const height = ctx.height
    const centerX = width / 2
    const centerY = height   // 圆心在底部
    const radius = Math.min(width / 2, height) - 10

    // 背景弧
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, Math.PI, 0)
    ctx.strokeStyle = '#E0E0E0'
    ctx.lineWidth = 24
    ctx.lineCap = 'round'
    ctx.stroke()

    // 各段数据
    let startAngle = Math.PI
    for (let i = 0; i < this.segments.length; i++) {
      const segment = this.segments[i]
      const sweepAngle = (segment.value / this.totalValue) * Math.PI
      ctx.beginPath()
      ctx.arc(centerX, centerY, radius, startAngle, startAngle + sweepAngle)
      ctx.strokeStyle = segment.color
      ctx.lineWidth = 24
      ctx.lineCap = 'butt'
      ctx.stroke()
      startAngle += sweepAngle
    }

    // 中心文字
    ctx.font = '24px sans-serif'
    ctx.fillStyle = '#333333'
    ctx.textAlign = 'center'
    ctx.fillText(this.formatDuration(this.totalValue), centerX, centerY - 20)
  }

  private formatDuration(ms: number): string {
    const hours = Math.floor(ms / 3600000)
    const minutes = Math.floor((ms % 3600000) / 60000)
    return hours.toString() + 'h ' + minutes.toString() + 'm'
  }
}
```

### 使用示例

```typescript
@ComponentV2
struct StatisticsPage {
  @Local segments: ChartSegment[] = []
  @Local totalValue: number = 12600000

  aboutToAppear(): void {
    const a = new ChartSegment(); a.value = 3600000; a.color = '#007DFF'; a.label = 'Feed A'
    const b = new ChartSegment(); b.value = 7200000; b.color = '#4CAF50'; b.label = 'Feed B'
    const c = new ChartSegment(); c.value = 1800000; c.color = '#FF9800'; c.label = 'Feed C'
    this.segments = [a, b, c]
  }

  build() {
    HalfCircleChart({
      segments: this.segments,
      totalValue: this.totalValue
    })
  }
}
```

### Canvas 绘制要点（V1/V2 通用）

- `onReady` 回调中绘制（此时 Canvas 尺寸已确定）
- 使用 `ctx.width` / `ctx.height` 获取实际尺寸
- 半圆弧：`arc(cx, cy, r, Math.PI, 0)` — 从 180 度到 0 度
- 多段弧线：累加 `startAngle`
- `lineCap: 'round'` 让弧线端点圆滑
- V2 推荐：用 `@Monitor('segments', 'totalValue')` 在数据变化时触发 `drawChart()`，替代 V1 的 `@Watch`

---

## V1 → V2 升级速查（本文档涉及的关键点）

| V1 | V2 | 备注 |
|---|---|---|
| `@Component` | `@ComponentV2` | 所有 struct |
| `@State downloadProgress: number = -1` | `@Local downloadProgress: number = -1` | 内部状态 |
| `@StorageLink('isPlaying') isPlaying: boolean = false` | `@Local model: PlaybackModel = AppStorageV2.connect(PlaybackModel, 'playback', () => new PlaybackModel())!` | 全局共享 |
| `AppStorage.setOrCreate<boolean>('isPlaying', true)` | `this.model.isPlaying = true`（@Trace 自动触发） | 状态写入 |
| `@Prop segments: ChartSegment[] = []` | `@Param @Once segments: ChartSegment[] = []` | 父传子只读 |
| `@Watch('onSegmentsChange')` | `@Monitor('segments') onSegmentsChange(m: IMonitor)` | 监听变化 |
| `@Observed class ChartSegment {...}` | `@ObservedV2 class ChartSegment { @Trace value... }` | 可观察类 |
