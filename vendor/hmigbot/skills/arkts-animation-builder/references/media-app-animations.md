# 媒体应用动效模式（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（含 `@Component / @State / @Prop / @StorageLink('isPlaying')` 等 V1 模式），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-media-app-animations.md`](./v2-media-app-animations.md)（V2 主参考）和 [`SKILL.md`](../SKILL.md)。
>
> 注意：动画 API（`Progress / SymbolGlyph / Canvas / TransitionEffect`）在 V1/V2 中完全相同；状态装饰器从 V1 升级到 V2：`@Component` → `@ComponentV2`、`@State` → `@Local`、`@Prop` → `@Param + @Once`、`@StorageLink('isPlaying')` → `AppStorageV2.connect(PlaybackModel, 'playback', () => new PlaybackModel())!`（配合 `@ObservedV2` 类）。

> 基于 AntennaPod ArkTS 播客应用实战总结的 4 种动效模式：下载进度环、播放按钮切换、MiniPlayer 显隐、半圆统计图。
> 源码参考：`entry/src/main/ets/pages/Index.ets`、`entry/src/main/ets/components/statistics/HalfCircleChart.ets`

---

## 1. 下载进度环 — Progress Ring

使用 `Progress` 组件的 `Ring` 类型，value 动态绑定下载百分比。

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
    .width(36)
    .height(36)
    .color('#007DFF')
    .backgroundColor('#E0E0E0')
    .style({ strokeWidth: 3 })

  Text(this.downloadProgress.toString() + '%')
    .fontSize(9)
    .fontColor('#007DFF')
}
```

### 三态下载按钮（完整模式）

```typescript
@State downloadProgress: number = -1;  // -1=非下载中
@State isDownloaded: boolean = false;

// UI
if (this.downloadProgress >= 0) {
  // 下载中 — 进度环 + 取消手势
  Stack() {
    Progress({ value: this.downloadProgress, total: 100, type: ProgressType.Ring })
      .width(36).height(36).color('#007DFF').style({ strokeWidth: 3 })
    // 中心显示取消图标
    SymbolGlyph($r('sys.symbol.xmark'))
      .fontSize(12).fontColor(['#007DFF'])
  }
  .onClick(() => {
    DownloadManager.getInstance().cancelDownload(this.episodeId);
    this.downloadProgress = -1;
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
```

### 数据驱动

```typescript
// EventBus 订阅下载进度更新
bus.subscribe(EVENT_DOWNLOAD_PROGRESS, (data: Object) => {
  if (data instanceof DownloadProgressData) {
    if (data.episodeId === this.episodeId) {
      this.downloadProgress = data.percent;  // @State 变化触发 UI 重绘
    }
  }
});
```

---

## 2. 播放按钮切换 — SymbolGlyph 动态图标

使用三元表达式切换 `play_fill` 和 `pause_fill` 图标。

### MiniPlayer 播放按钮

```typescript
Column() {
  SymbolGlyph(this.isPlaying ? $r('sys.symbol.pause_fill') : $r('sys.symbol.play_fill'))
    .fontSize(20)
    .fontColor(['#333333'])
}
.width(36)
.height(36)
.borderRadius(18)  // 圆形按钮
.backgroundColor('#E8E8E8')
.justifyContent(FlexAlign.Center)
.alignItems(HorizontalAlign.Center)
.onClick(() => {
  PlaybackController.getInstance().playPause();
})
```

### FullPlayer 大播放按钮

```typescript
Column() {
  SymbolGlyph(this.isPlaying ? $r('sys.symbol.pause_circle_fill') : $r('sys.symbol.play_circle_fill'))
    .fontSize(56)
    .fontColor(['#333333'])
}
.onClick(() => {
  PlaybackController.getInstance().playPause();
})
```

### 状态驱动

```typescript
// @StorageLink 自动双向绑定
@StorageLink('isPlaying') isPlaying: boolean = false;

// PlaybackController 在状态变化时更新 AppStorage
private onPlaying(): void {
  AppStorage.setOrCreate<boolean>('isPlaying', true);   // → SymbolGlyph 切换到 pause_fill
}

private onPaused(): void {
  AppStorage.setOrCreate<boolean>('isPlaying', false);  // → SymbolGlyph 切换到 play_fill
}
```

### 常用媒体图标对照

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

### 基本模式

```typescript
// 条件：有播放内容 且 不在全屏模式
if (this.isPlayerVisible && !this.isFullPlayerVisible) {
  Column() {
    // MiniPlayer 内容...
  }
  .width('100%')
  .backgroundColor('#FAFAFA')
  .shadow({ radius: 4, color: '#1A000000', offsetY: -2 })
}
```

### 添加过渡动画（可选增强）

```typescript
if (this.isPlayerVisible && !this.isFullPlayerVisible) {
  Column() { /* MiniPlayer */ }
    .transition(TransitionEffect.OPACITY.animation({ duration: 200 }))
    .transition(TransitionEffect.translate({ y: 60 }).animation({ duration: 250 }))
}
```

### Tab 栏联动隐藏

```typescript
// FullPlayer 打开时 Tab 栏也隐藏
if (!this.isFullPlayerVisible) {
  Row() {
    // Tab 按钮...
  }
  .height(56)
}
```

### 状态流转

```
初始: isPlayerVisible=false, isFullPlayerVisible=false
  → MiniPlayer 隐藏, Tab 栏可见

播放开始: PlaybackController 设置 isPlayerVisible=true
  → MiniPlayer 出现, Tab 栏可见

点击 MiniPlayer: push FullPlayer
  → FullPlayer.onReady 设置 isFullPlayerVisible=true
  → MiniPlayer 消失, Tab 栏消失

FullPlayer 返回: NavPathStack.pop()
  → FullPlayer.onDisAppear 设置 isFullPlayerVisible=false
  → MiniPlayer 恢复, Tab 栏恢复

播放停止: PlaybackController 设置 isPlayerVisible=false
  → MiniPlayer 消失
```

---

## 4. 半圆统计图 — Canvas 自定义绘制

使用 `Canvas` + `CanvasRenderingContext2D` 绘制半圆弧形统计图，用于播放时长统计。

### 基本结构

```typescript
@Component
export struct HalfCircleChart {
  @Prop segments: ChartSegment[] = [];
  @Prop totalValue: number = 0;
  private settings: RenderingContextSettings = new RenderingContextSettings(true);
  private context: CanvasRenderingContext2D = new CanvasRenderingContext2D(this.settings);

  build() {
    Column() {
      Canvas(this.context)
        .width('100%')
        .height(160)
        .onReady(() => {
          this.drawChart();
        })
    }
  }

  private drawChart(): void {
    const ctx = this.context;
    const width = ctx.width;
    const height = ctx.height;
    const centerX = width / 2;
    const centerY = height;   // 圆心在底部
    const radius = Math.min(width / 2, height) - 10;

    // 绘制背景弧
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, Math.PI, 0);  // 半圆
    ctx.strokeStyle = '#E0E0E0';
    ctx.lineWidth = 24;
    ctx.lineCap = 'round';
    ctx.stroke();

    // 绘制各段数据
    let startAngle = Math.PI;  // 从左侧开始
    for (let i = 0; i < this.segments.length; i++) {
      const segment = this.segments[i];
      const sweepAngle = (segment.value / this.totalValue) * Math.PI;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, startAngle, startAngle + sweepAngle);
      ctx.strokeStyle = segment.color;
      ctx.lineWidth = 24;
      ctx.lineCap = 'butt';
      ctx.stroke();
      startAngle += sweepAngle;
    }

    // 中心文字
    ctx.font = '24px sans-serif';
    ctx.fillStyle = '#333333';
    ctx.textAlign = 'center';
    ctx.fillText(this.formatDuration(this.totalValue), centerX, centerY - 20);
  }

  private formatDuration(ms: number): string {
    const hours = Math.floor(ms / 3600000);
    const minutes = Math.floor((ms % 3600000) / 60000);
    return hours.toString() + 'h ' + minutes.toString() + 'm';
  }
}
```

### 使用示例

```typescript
HalfCircleChart({
  segments: [
    { value: 3600000, color: '#007DFF', label: 'Feed A' },
    { value: 7200000, color: '#4CAF50', label: 'Feed B' },
    { value: 1800000, color: '#FF9800', label: 'Feed C' }
  ],
  totalValue: 12600000
})
```

### Canvas 绘制要点

- `onReady` 回调中绘制（此时 Canvas 尺寸已确定）
- 使用 `ctx.width` / `ctx.height` 获取实际尺寸
- 半圆弧：`arc(cx, cy, r, Math.PI, 0)` — 从 180 度到 0 度
- 多段弧线：累加 `startAngle`
- `lineCap: 'round'` 让弧线端点圆滑
- 响应 `@Prop` 变化时需要清除并重绘
