# 控件自动隐藏 + 透明点击层模板

> 锚点：SKILL.md §6

---

## 状态机：3.5s 三态定时器

```typescript
@Entry @ComponentV2
struct VideoPlayerPage {
  @Local showControls: boolean = true;
  private hideTimerId: number = -1;
  private readonly HIDE_DELAY_MS = 3500;

  /**
   * 调度隐藏：清除现有定时器，重新计时
   * 任何用户交互或状态变化都应调用此方法
   */
  private scheduleHide(): void {
    if (this.hideTimerId !== -1) {
      clearTimeout(this.hideTimerId);
    }
    this.hideTimerId = setTimeout(() => {
      this.showControls = false;
      this.hideTimerId = -1;
    }, this.HIDE_DELAY_MS);
  }

  /**
   * 取消隐藏（控件本身被点击/拖动时）
   */
  private cancelHide(): void {
    if (this.hideTimerId !== -1) {
      clearTimeout(this.hideTimerId);
      this.hideTimerId = -1;
    }
  }

  /**
   * 用户交互：显示控件 + 重新计时
   */
  private onUserInteract(): void {
    this.showControls = true;
    this.scheduleHide();
  }

  /**
   * AVPlayer stateChange 回调
   * ⚠️ PLAYING / PAUSED / PREPARED 三态都触发，不要漏 PAUSED
   */
  private onPlayerStateChange(state: string): void {
    if (state === 'prepared' || state === 'playing' || state === 'paused') {
      this.scheduleHide();
    }
  }

  aboutToDisappear(): void {
    this.cancelHide();  // 释放定时器
  }
}
```

---

## 为什么 PAUSED 也要走定时器

错误模式："暂停时强制显示控件，不隐藏"——和 Android `FullPlayerView` 对照不一致。

Android 行为：暂停 3 秒后控件也会收起，用户再次点击屏幕才唤出。HMOS 实现要对齐。

如果只在 PLAYING 触发隐藏，暂停状态下控件永远占着上下两条 → 视频被裁。用户报障"控件收不起来"。

---

## 透明点击层（关键架构）

XComponent 的 SURFACE 是渲染层，**不响应** `onClick`。必须在它上方放一层透明 Stack 来接收点击。

### 层序（从底到顶）

```
Layer 1: XComponent (SURFACE)
Layer 2: 透明点击层（接收点击 → 唤出/收起控件）
Layer 3: 顶栏（仅 showControls=true 时渲染）
Layer 4: 底栏（仅 showControls=true 时渲染）
Layer 5: 中心 Play/Pause 按钮（仅 showControls=true 时渲染）
```

### 模板代码

```typescript
build() {
  Stack({ alignContent: Alignment.TopStart })
    .width('100%').height('100%')
  {
    // Layer 1: XComponent
    XComponent({ type: XComponentType.SURFACE, controller: this.xc })
      .width(this.xcWidthVp())
      .height(this.xcHeightVp())
      .position({ left: this.videoOffsetXVp(), top: this.videoOffsetYVp() })
      .onLoad((id) => this.playerCore.setSurface(id))

    // Layer 2: 透明点击层（关键）
    Stack()
      .width('100%').height('100%')
      .backgroundColor('#00000000')   // ⚠️ 必须设这个；省略会让 Stack 不接收点击
      .onClick(() => this.toggleControls())

    // Layer 3-5: 仅 showControls=true 时渲染
    if (this.showControls) {
      this.buildTopBar()
      this.buildBottomBar()
      this.buildCenterPlayButton()
    }
  }
}

private toggleControls(): void {
  if (this.showControls) {
    this.showControls = false;
    this.cancelHide();
  } else {
    this.showControls = true;
    this.scheduleHide();
  }
}
```

---

## 控件层自身要 cancelHide

进度条拖动时不要让控件自动隐藏：

```typescript
@Builder buildBottomBar() {
  Column() {
    Slider({ value: this.currentMs, min: 0, max: this.durationMs })
      .onChange((v) => {
        this.cancelHide();  // ← 拖动时取消隐藏
        this.onSeek(v);
      })
      .onTouch((event) => {
        if (event.type === TouchType.Up) {
          this.scheduleHide();  // ← 松手后重新计时
        }
      })
  }
  // ...
}
```

倍速选择器同理。

---

## 检查清单

- [ ] hideTimerId 在 aboutToDisappear 清理
- [ ] 三态都触发 scheduleHide（PLAYING / PAUSED / PREPARED）
- [ ] 透明点击层在 XComponent 上方、控件层下方
- [ ] 透明点击层 backgroundColor 显式设 `'#00000000'`
- [ ] 控件层自己的拖动 / 长按交互调 cancelHide
- [ ] 拖动结束（TouchType.Up）调 scheduleHide
