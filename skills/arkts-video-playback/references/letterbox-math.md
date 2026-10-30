# Letterbox 尺寸计算 + 顶底栏定位（复盘 v1 关键 fix）

> 锚点：SKILL.md §5

---

## 概念

**Letterbox**：视频原始宽高比与播放容器宽高比不一致时，保留视频原始比例 → 上下或左右出现黑边。

```
视频 16:9，容器 18:9（横屏满屏）
┌──────────────────────────┐
│ [黑边 80vp]              │
│  ┌────────────────────┐  │
│  │                    │  │
│  │     视频内容        │  │
│  │                    │  │
│  └────────────────────┘  │
│ [黑边 80vp]              │
└──────────────────────────┘
```

如果顶/底栏跨整屏（width: '100%'），按钮就会坐在黑边上。**正确做法是把控件钉到视频帧**。

---

## 完整公式

```typescript
@ComponentV2
struct VideoPlayerPage {
  @Local videoW: number = 0;       // 视频原始宽（像素）
  @Local videoH: number = 0;       // 视频原始高（像素）
  @Local containerW: number = 0;   // 容器宽（vp，通常等于屏幕宽）
  @Local containerH: number = 0;   // 容器高（vp）

  // PlayerCore 触发
  onVideoSize(w: number, h: number): void {
    this.videoW = w;
    this.videoH = h;
  }

  // letterbox 后视频实际渲染宽
  xcWidthVp(): number {
    if (!this.videoW || !this.videoH) return this.containerW;
    const videoRatio = this.videoW / this.videoH;
    const containerRatio = this.containerW / this.containerH;
    if (videoRatio > containerRatio) {
      // 视频比容器更宽 → 横向铺满，上下 letterbox 黑边
      return this.containerW;
    } else {
      // 视频比容器更高 → 纵向铺满，左右黑边
      return this.containerH * videoRatio;
    }
  }

  xcHeightVp(): number {
    if (!this.videoW || !this.videoH) return this.containerH;
    const videoRatio = this.videoW / this.videoH;
    const containerRatio = this.containerW / this.containerH;
    if (videoRatio > containerRatio) {
      return this.containerW / videoRatio;  // 视频更宽 → 高度按比例缩
    } else {
      return this.containerH;
    }
  }

  // 视频帧左上角偏移（让视频居中）
  videoOffsetXVp(): number {
    return (this.containerW - this.xcWidthVp()) / 2;
  }
  videoOffsetYVp(): number {
    return (this.containerH - this.xcHeightVp()) / 2;
  }
}
```

---

## 顶/底栏定位（钉到视频帧）

```typescript
// 顶栏
@Builder buildTopBar() {
  Row() {
    Image($r('app.media.player_ic_back')).onClick(() => router.back())
    Text(this.title).fontSize(18).fontColor(Color.White)
  }
  .width(this.xcWidthVp())                    // ← 视频帧宽，不是 '100%'
  .height(56)
  .position({
    left: this.videoOffsetXVp(),               // ← 钉到视频左边
    top: this.videoOffsetYVp() + this.statusBarHeight  // ← 视频顶 + 状态栏避让
  })
}

// 底栏（进度条）
@Builder buildBottomBar() {
  Column() {
    Slider({ value: this.currentMs, min: 0, max: this.durationMs })
      .blockColor('#FFFFFF').selectedColor('#FF6B35')
      .onChange((v) => this.onSeek(v))
    Row() {
      Text(this.fmtMs(this.currentMs)).fontColor(Color.White)
      Blank()
      Text(this.fmtMs(this.durationMs)).fontColor(Color.White)
    }
  }
  .width(this.xcWidthVp())
  .height(80)
  .position({
    left: this.videoOffsetXVp(),
    bottom: this.containerH - (this.videoOffsetYVp() + this.xcHeightVp()) + this.gestureBarHeight
  })
}
```

---

## 为什么 alignContent 不要用 Center

```typescript
// ❌ 错误
Stack({ alignContent: Alignment.Center }) {
  XComponent(...).width(this.xcWidthVp()).height(this.xcHeightVp())
  this.buildTopBar()    // ← 也被推到 Stack 中心
  this.buildBottomBar() // ← 也被推到 Stack 中心
}
```

`alignContent: Center` 会把所有没显式 position 的子元素推到中心。即使你给顶栏写了 `.position({ top: ... })`，alignContent 会和 position 互相干扰，行为不可预测。

```typescript
// ✓ 正确
Stack({ alignContent: Alignment.TopStart }) {
  XComponent(...).position({ left: this.videoOffsetXVp(), top: this.videoOffsetYVp() })
  this.buildTopBar().position({ left: ..., top: ... })
  this.buildBottomBar().position({ left: ..., bottom: ... })
}
```

`TopStart` 让所有子元素从 (0,0) 开始；位置全靠 `position` 显式控制。
