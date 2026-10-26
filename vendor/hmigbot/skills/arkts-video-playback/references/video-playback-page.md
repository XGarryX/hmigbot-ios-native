# 视频播放页完整模板（XComponent + AVPlayer + 全屏控件）

> 从某实战项目 `VideoPlayerPage.ets` + `PlayerCore.ets` 提炼的可复用骨架。
>
> 如果任务是"音频/Podcast"，请改读 `playback-patterns.md`；这里是**全屏视频播放页**专用。

---

## 前置步骤：资源先拷 4 张 webp

模板里的控件层引用了 Android 原生 SuperPlayer 的 4 张图标资源；如果 Android 源码工程在手，**先拷到 `entry/src/main/resources/base/media/` 再写代码**，否则 `$r('app.media.player_ic_*')` 会 resolve 失败。

```bash
# 原路径：<Android 工程>/<player 模块>/src/main/res/drawable-xxhdpi/
cp player_ic_backward.webp           entry/src/main/resources/base/media/
cp player_ic_forward.webp            entry/src/main/resources/base/media/
cp player_ic_vod_pause_normal.webp   entry/src/main/resources/base/media/
cp player_ic_vod_play_normal.webp    entry/src/main/resources/base/media/
```

**用途**：
- `player_ic_backward / forward` — 左右 -15s/+15s（灰半透明圆 + 弧箭头 + "15"）
- `player_ic_vod_pause_normal / play_normal` — 中心播放/暂停（灰半透明圆 + 白图形）

**不要**用 Unicode `▶` / `❙❙` 字符当图标——跨设备字形不一致、缺弧箭头数字、手搓黑圆会和原图灰圆叠加。

如果没有 Android 源码可拷（全新项目），退而求其次用 `SymbolGlyph($r('sys.symbol.play_fill / pause'))` + `backward_15` / `forward_15` 两个系统符号，但视觉上会和 Android 版不完全一致（系统符号是线框，非灰圆填充）。

---

## 整体架构

```
VideoPlayerPage (@Entry)              ← 页面：路由参数接收 / 横屏 / safeArea / UI 控件层
│
├── PlayerCore                         ← 播放器封装：AVPlayer 状态机 + surfaceId 桥接
│   ├── on('stateChange')
│   ├── on('timeUpdate') → onProgress
│   ├── on('durationUpdate') → onDuration
│   ├── on('error')       → onError
│   └── prepare / play / pause / seekTo / release
│
└── build()                            ← Stack 叠层：XComponent + Loading/Error + 顶栏 + 两侧 + 中心 + 底栏 + Dialog
```

---

## PlayerCore — 可复用的 AVPlayer + XComponent 桥接

```typescript
import { media } from '@kit.MediaKit';
import { BusinessError } from '@kit.BasicServicesKit';

export enum PlayerState {
  IDLE = 'idle',
  INITIALIZED = 'initialized',
  PREPARED = 'prepared',
  PLAYING = 'playing',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  STOPPED = 'stopped',
  RELEASED = 'released',
  ERROR = 'error',
}

export interface PlayerCallbacks {
  onStateChange?: (state: PlayerState) => void;
  onProgress?: (positionMs: number) => void;
  onDuration?: (durationMs: number) => void;
  onComplete?: () => void;
  onError?: (code: number, message: string) => void;
}

export class PlayerCore {
  private player: media.AVPlayer | undefined = undefined;
  private surfaceId: string = '';
  private pendingUrl: string = '';
  private callbacks: PlayerCallbacks = {};
  private state: PlayerState = PlayerState.IDLE;
  /** Prepared 之前的 seek 请求暂存 */
  private pendingSeekMs: number = -1;

  setCallbacks(cbs: PlayerCallbacks): void {
    this.callbacks = cbs;
  }

  /**
   * 注入 XComponent.onLoad 拿到的 surfaceId。
   * 如 AVPlayer 已进 Initialized 在等 surface，立即 prepare；否则等 stateChange('initialized') 再触发。
   */
  setSurfaceId(id: string): void {
    this.surfaceId = id;
    if (this.player !== undefined
        && this.state === PlayerState.INITIALIZED
        && this.surfaceId.length > 0) {
      this.player.surfaceId = this.surfaceId;
      this.player.prepare().catch((err: BusinessError): void => {
        this.emitError(err.code, 'prepare failed: ' + JSON.stringify(err));
      });
    }
  }

  /**
   * 加载并播放一个 URL（http/https/fd:// 都支持）。
   * 幂等：多次调用先 reset 再设置新 URL。
   */
  async prepare(url: string): Promise<void> {
    if (url.length === 0) { this.emitError(-1, 'empty url'); return; }
    this.pendingUrl = url;

    if (this.player === undefined) {
      try {
        this.player = await media.createAVPlayer();
      } catch (err) {
        const be = err as BusinessError;
        this.emitError(be.code, 'createAVPlayer failed: ' + JSON.stringify(be));
        return;
      }
      this.attachListeners(this.player);
    } else {
      try { await this.player.reset(); }
      catch (e) {
        try { await this.player.release(); } catch (e2) { /* ignore */ }
        this.player = await media.createAVPlayer();
        this.attachListeners(this.player);
      }
    }
    this.player.url = this.pendingUrl;  // 触发 stateChange('initialized')
  }

  play(): void {
    if (this.player === undefined) return;
    if (this.state === PlayerState.PREPARED || this.state === PlayerState.PAUSED
        || this.state === PlayerState.COMPLETED) {
      this.player.play().catch((err: BusinessError): void => {
        this.emitError(err.code, 'play failed: ' + JSON.stringify(err));
      });
    }
  }

  pause(): void {
    if (this.player === undefined) return;
    if (this.state === PlayerState.PLAYING) {
      this.player.pause().catch((err: BusinessError): void => {
        this.emitError(err.code, 'pause failed: ' + JSON.stringify(err));
      });
    }
  }

  seekTo(positionMs: number): void {
    if (this.player === undefined) { this.pendingSeekMs = positionMs; return; }
    if (this.state === PlayerState.PREPARED || this.state === PlayerState.PLAYING
        || this.state === PlayerState.PAUSED || this.state === PlayerState.COMPLETED) {
      this.player.seek(positionMs, media.SeekMode.SEEK_PREV_SYNC);
    } else {
      this.pendingSeekMs = positionMs;
    }
  }

  async release(): Promise<void> {
    if (this.player === undefined) return;
    try { await this.player.release(); } catch (e) { /* ignore */ }
    this.player = undefined;
    this.setState(PlayerState.RELEASED);
  }

  getState(): PlayerState { return this.state; }

  private attachListeners(p: media.AVPlayer): void {
    p.on('stateChange', (state: string, _reason: media.StateChangeReason): void => {
      switch (state) {
        case 'idle':        this.setState(PlayerState.IDLE); break;
        case 'initialized':
          this.setState(PlayerState.INITIALIZED);
          // surface 已就位 → 立即 prepare
          if (this.surfaceId.length > 0 && this.player !== undefined) {
            this.player.surfaceId = this.surfaceId;
            this.player.prepare().catch((err: BusinessError): void => {
              this.emitError(err.code, 'prepare failed: ' + JSON.stringify(err));
            });
          }
          break;
        case 'prepared':
          this.setState(PlayerState.PREPARED);
          if (this.pendingSeekMs >= 0 && this.player !== undefined) {
            this.player.seek(this.pendingSeekMs, media.SeekMode.SEEK_PREV_SYNC);
            this.pendingSeekMs = -1;
          }
          // 首次 prepared 自动起播
          this.player?.play().catch((err: BusinessError): void => {
            this.emitError(err.code, 'autoplay failed: ' + JSON.stringify(err));
          });
          break;
        case 'playing':     this.setState(PlayerState.PLAYING); break;
        case 'paused':      this.setState(PlayerState.PAUSED); break;
        case 'completed':
          this.setState(PlayerState.COMPLETED);
          this.callbacks.onComplete?.();
          break;
        case 'stopped':     this.setState(PlayerState.STOPPED); break;
        case 'released':    this.setState(PlayerState.RELEASED); break;
        case 'error':       this.setState(PlayerState.ERROR); break;
      }
    });

    p.on('timeUpdate', (time: number): void => { this.callbacks.onProgress?.(time); });
    p.on('durationUpdate', (d: number): void => { this.callbacks.onDuration?.(d); });
    p.on('error', (err: BusinessError): void => { this.emitError(err.code, err.message); });
  }

  private setState(s: PlayerState): void {
    this.state = s;
    this.callbacks.onStateChange?.(s);
  }

  private emitError(code: number, msg: string): void {
    this.setState(PlayerState.ERROR);
    this.callbacks.onError?.(code, msg);
  }
}
```

---

## 播放页整体骨架

### 路由参数接收（支持多种上游）

```typescript
/** 至少覆盖三种形状：courseId / sectionId+courseId+sectionType / id（== sectionId） */
interface PlayerRouteParams {
  courseId?: string;
  sectionId?: string;
  sectionType?: string;
  id?: string;
  videoUrl?: string;   // 直接给 URL 时跳过详情接口
  name?: string;
  coverImage?: string;
  dura?: number;
  consume?: number;
}

aboutToAppear(): void {
  const raw: Object | undefined = router.getParams() as Object | undefined;
  const params: PlayerRouteParams = raw !== undefined
    ? (raw as PlayerRouteParams)
    : { courseId: '' };

  this.core.setCallbacks({
    onStateChange: (s: PlayerState): void => { this.playerState = s; },
    onProgress:    (ms: number): void => { this.positionMs = ms; },
    onDuration:    (ms: number): void => { this.durationMs = ms; },
    onComplete:    (): void => { this.onPlayComplete(); },
    onError:       (code: number, msg: string): void => {
      this.errorMsg = `播放失败 (${code}): ${msg}`;
      this.loading = false;
    },
  });

  this.querySafeAreaInset();   // 顶部状态栏避让
  this.setLandscape();         // 强制横屏
  this.loadAndStart(params);   // 拉详情 → core.prepare(url)
}

aboutToDisappear(): void {
  this.core.release();
  this.restoreOrientation();   // 恢复竖屏
}
```

### loadAndStart：详情接口失败时透传业务错误

```typescript
import { ApiError } from '../network/ResultHandler';  // 或等价的业务异常类

private async loadAndStart(params: PlayerRouteParams): Promise<void> {
  this.loading = true; this.errorMsg = '';

  // 1) 调用方直接带 videoUrl → 跳过接口
  if (params.videoUrl !== undefined && params.videoUrl.length > 0) {
    this.card = this.makeCardFromDirectParams(params);
    this.loading = false;
    await this.core.prepare(params.videoUrl);
    return;
  }

  // 2) 有 sectionId → loadDetailSingle；只有 courseId → loadDetailMulti
  const sectionId: string = params.sectionId ?? params.id ?? '';
  const courseId: string = params.courseId ?? '';
  if (sectionId.length === 0 && courseId.length === 0) {
    this.errorMsg = '缺少必要参数'; this.loading = false; return;
  }

  try {
    const detail = sectionId.length > 0
      ? await DetailService.loadDetailSingle(sectionId, params.sectionType ?? 'normal')
      : await this.pickFirstSection(courseId, params.sectionType);
    // ... 组装 this.card
    this.loading = false;
    const url = this.card.videoUrl;
    if (url.length === 0) { this.errorMsg = '该项暂无可播放视频'; return; }
    await this.core.prepare(url);
  } catch (e) {
    // 分层错误透传：业务 500（"内容已下架"）vs 网络错
    if (e instanceof ApiError && e.businessMessage.length > 0) {
      this.errorMsg = e.businessMessage;
    } else if (e instanceof Error && e.message.length > 0) {
      this.errorMsg = e.message;
    } else {
      this.errorMsg = '加载详情失败，请稍后重试';
    }
    this.loading = false;
  }
}
```

### 横屏 + safeArea

```typescript
import { window } from '@kit.ArkUI';

@Local safeTopVp: number = 44;

private setLandscape(): void {
  try {
    window.getLastWindow(getContext(this)).then((win: window.Window): void => {
      win.setPreferredOrientation(window.Orientation.LANDSCAPE).catch(() => { /* ignore */ });
    });
  } catch (e) { /* ignore */ }
}

private restoreOrientation(): void {
  try {
    window.getLastWindow(getContext(this)).then((win: window.Window): void => {
      win.setPreferredOrientation(window.Orientation.UNSPECIFIED).catch(() => { /* ignore */ });
    });
  } catch (e) { /* ignore */ }
}

private querySafeAreaInset(): void {
  try {
    window.getLastWindow(getContext(this)).then((win: window.Window): void => {
      const avoid = win.getWindowAvoidArea(window.AvoidAreaType.TYPE_SYSTEM);
      const vp = px2vp(avoid.topRect.height);
      if (vp > 0) this.safeTopVp = vp;
    });
  } catch (e) { /* ignore */ }
}
```

**配套注意**：上一页（返回目标页）需要在 `onPageShow` 重查 safeArea，否则横屏切回竖屏时上一页 padding 仍是旧值 → 顶部顶破状态栏。

### build() 布局 Stack 叠层

```typescript
@Local loading: boolean = true;
@Local errorMsg: string = '';
@Local showBackDialog: boolean = false;
@Local positionMs: number = 0;
@Local durationMs: number = 0;
@Local playerState: PlayerState = PlayerState.IDLE;

private xcCtrl: XComponentController = new XComponentController();
private core: PlayerCore = new PlayerCore();
private backPressedOnce: boolean = false;

onBackPress(): boolean {
  if (this.backPressedOnce) return false;
  this.core.pause();
  this.showBackDialog = true;
  return true;  // 消费事件
}

build() {
  NavDestination() {
    Stack({ alignContent: Alignment.TopStart }) {
      // 1) 视频 Surface
      XComponent({
        id: 'playerSurface',
        type: XComponentType.SURFACE,
        controller: this.xcCtrl,
      })
        .width('100%').height('100%').backgroundColor(Color.Black)
        .onLoad((): void => {
          const id: string = this.xcCtrl.getXComponentSurfaceId();
          this.core.setSurfaceId(id);
        })
        .onDestroy((): void => { this.core.release(); })

      // 2) Loading 遮罩
      if (this.loading) {
        Column() {
          LoadingProgress().width(48).height(48).color(Color.White)
          Text('加载中…').fontColor(Color.White).margin({ top: 8 })
        }
        .width('100%').height('100%')
        .justifyContent(FlexAlign.Center).alignItems(HorizontalAlign.Center)
        .backgroundColor('rgba(0,0,0,0.6)')
      }

      // 3) Error 遮罩（全屏；横屏不能用 Toast）
      if (this.errorMsg.length > 0 && !this.loading) {
        Column({ space: 12 }) {
          SymbolGlyph($r('sys.symbol.exclamationmark_circle'))
            .fontSize(56).fontColor([Color.White])
          Text(this.errorMsg)                // ← 透传业务错误原文
            .fontColor(Color.White).maxLines(3)
            .textAlign(TextAlign.Center).width('80%')
          Button('返回').onClick((): void => { router.back(); })
        }
        .width('100%').height('100%')
        .justifyContent(FlexAlign.Center).alignItems(HorizontalAlign.Center)
        .backgroundColor('rgba(0,0,0,0.85)')
      }

      // 4) 顶栏：左返回+标题，右倍速
      Row() {
        Image($r('app.media.ic_back_white')).width(24).height(24)
          .onClick((): void => { this.onBackPress(); })
        Text(this.card.name.length > 0 ? this.card.name : '正在播放')
          .fontSize(16).fontColor(Color.White).fontWeight(FontWeight.Medium)
          .margin({ left: 8 }).maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis }).layoutWeight(1)
        Text('倍速')   // 占位；接真实 setSpeed 后从此处弹选择器
          .fontSize(14).fontColor(Color.White)
          .padding({ left: 10, right: 10, top: 4, bottom: 4 })
          .borderRadius(4).backgroundColor('rgba(255,255,255,0.15)')
      }
      .width('100%')
      .padding({ left: 12, right: 12, top: this.safeTopVp + 8, bottom: 12 })
      .linearGradient({
        direction: GradientDirection.Bottom,
        colors: [['rgba(0,0,0,0.55)', 0.0], ['rgba(0,0,0,0)', 1.0]],
      })

      // 5) 左右两侧 -15s / +15s（对齐 Android player_vod_player_fullscreen.xml）
      //    资源：从 Android <player 模块>/res/drawable-xxhdpi 拷 player_ic_backward.webp / player_ic_forward.webp
      //    到 entry/src/main/resources/base/media/。webp 自带灰半透明圆底 + 弧箭头 + "15" 数字，
      //    不要再套 rgba 黑圆或加 Text("15")——会双圆叠加且中心偏。
      //    尺寸：36×36vp（对齐 Android 36dp），距屏边 95vp（对齐 marginLeft="dp_95"）。
      //    竖直正中：top:'50%' + translate(y:-18) = layout_centerVertical。**不要写 top:'42%'**。
      Row() {
        Image($r('app.media.player_ic_backward'))
          .width(36).height(36)
          .onClick((): void => { this.onSeekBy(-15000); })
        Image($r('app.media.player_ic_forward'))
          .width(36).height(36)
          .onClick((): void => { this.onSeekBy(15000); })
      }
      .width('100%').padding({ left: 95, right: 95 })
      .justifyContent(FlexAlign.SpaceBetween)
      .position({ top: '50%', left: 0 })
      .translate({ y: -18 })

      // 6) 中心播放/暂停（对齐 Android FullScreenPlayer.updatePlayState）
      //    资源：player_ic_vod_pause_normal.webp（灰圆+❙❙）/ player_ic_vod_play_normal.webp（灰圆+▶）
      //    切换规则："按 action 展示"：PLAYING → pause（点=暂停）；其他 → play（点=播放）。
      //    尺寸：50×50vp（对齐 Android 50dp），layout_centerInParent=true。
      //    **不要**用 Unicode `▶`/`❙❙` 字符——跨设备字形不一致；也不要外层 Column + 手搓黑圆。
      Image(this.playerState === PlayerState.PLAYING
        ? $r('app.media.player_ic_vod_pause_normal')
        : $r('app.media.player_ic_vod_play_normal'))
        .width(50).height(50)
        .position({ top: '50%', left: '50%' })
        .translate({ x: -25, y: -25 })        // 双轴各减半个自身尺寸，精确居中
        .onClick((): void => { this.onTapPlayPause(); })

      // 7) 底部进度条（贴底 + 避让 home indicator 28vp）
      Row({ space: 8 }) {
        Text(this.formatMs(this.positionMs))
          .fontSize(12).fontColor(Color.White).width(44).textAlign(TextAlign.Center)
        Slider({
          value: this.progressPercent() * 100,
          min: 0, max: 100, step: 1,
          style: SliderStyle.OutSet,
        })
          .trackColor('rgba(255,255,255,0.4)')
          .selectedColor('#FF5A5F')        // 主色
          .blockColor(Color.White)
          .layoutWeight(1)
          .onChange((value: number, mode: SliderChangeMode): void => {
            if (mode === SliderChangeMode.End || mode === SliderChangeMode.Click) {
              this.onSeek(value / 100);
            }
          })
        Text(this.formatMs(this.durationMs))
          .fontSize(12).fontColor(Color.White).width(44).textAlign(TextAlign.Center)
      }
      .width('100%').padding({ left: 16, right: 16, top: 10, bottom: 10 })
      .linearGradient({
        direction: GradientDirection.Top,
        colors: [['rgba(0,0,0,0.55)', 0.0], ['rgba(0,0,0,0)', 1.0]],
      })
      .position({ left: 0, right: 0, bottom: 28 })  // ~横屏 home indicator

      // 8) 挽留 Dialog
      if (this.showBackDialog) {
        this.RetentionDialog()
      }
    }
    .width('100%').height('100%').backgroundColor(Color.Black)
  }
  .hideTitleBar(true)
}
```

### 挽留 Dialog（文字链次按钮样式）

```typescript
@Builder
RetentionDialog() {
  Column() {
    Column({ space: 14 }) {
      Text('等等！才开始就不练了？')
        .fontSize(20).fontWeight(FontWeight.Bold).fontColor(Color.White)
      Text('练什么不重要，动起来都算数哦!')
        .fontSize(13).fontColor('rgba(255,255,255,0.75)')
        .textAlign(TextAlign.Center).maxLines(2)
      Button('继续练习')
        .width(220).height(44)
        .backgroundColor('#C6EE4A')      // 主按钮：品牌绿
        .fontColor(0xFF2D2D2D).fontWeight(FontWeight.Bold)
        .borderRadius(22)
        .onClick((): void => {
          this.showBackDialog = false;
          this.core.play();
        })
      Row() {
        Text('我要放弃').fontSize(13).fontColor('rgba(255,255,255,0.75)')
        Text(' >').fontSize(13).fontColor('rgba(255,255,255,0.75)')
      }
        .margin({ top: 2 })
        .onClick((): void => { this.onAbandon(); })
    }
    .alignItems(HorizontalAlign.Center)
    .padding({ left: 24, right: 24, top: 20, bottom: 20 })
  }
  .width('100%').height('100%')
  .justifyContent(FlexAlign.Center).alignItems(HorizontalAlign.Center)
  .backgroundColor('rgba(0,0,0,0.55)')
}

private async onAbandon(): Promise<void> {
  this.showBackDialog = false;
  // 可选：上报半程进度（业务侧自定义）
  // await this.uploadPartialProgress(this.positionMs);
  this.backPressedOnce = true;
  router.back();
}
```

### seek 辅助

```typescript
private onTapPlayPause(): void {
  if (this.playerState === PlayerState.PLAYING) this.core.pause();
  else this.core.play();
}

private onSeek(percent: number): void {
  if (this.durationMs > 0) {
    this.core.seekTo(Math.floor(this.durationMs * percent));
  }
}

private onSeekBy(deltaMs: number): void {
  if (this.durationMs <= 0) return;
  const target = this.positionMs + deltaMs;
  const clamped = target < 0 ? 0 : (target > this.durationMs ? this.durationMs : target);
  this.core.seekTo(clamped);
}

private formatMs(ms: number): string {
  const total = Math.floor(ms / 1000);
  const m = Math.floor(total / 60);
  const s = total % 60;
  return (m < 10 ? '0' + m : String(m)) + ':' + (s < 10 ? '0' + s : String(s));
}

private progressPercent(): number {
  if (this.durationMs <= 0) return 0;
  const p = this.positionMs / this.durationMs;
  return p < 0 ? 0 : (p > 1 ? 1 : p);
}
```

---

## 返回目标页的配套修复

横屏播放器 pop 回来时，上一页必须**重查 safeArea inset**，否则顶部顶破状态栏：

```typescript
// MainPage.ets / 或任何可能成为 Player 返回目标的页面
onPageShow(): void {
  this.querySafeAreaInsets();   // 重新读 AvoidArea → 更新 @Local statusBarInsetVp
}
```

原因：Player 横屏切换触发了 display/window 配置更新，返回时竖屏尺寸变了但上一页的 `@Local` 是 `aboutToAppear` 时查的旧值。

---

## 视频播放 vs 音频播放：关键差异对照

| 对象 | 视频（本模板） | 音频（`playback-patterns.md`） |
|---|---|---|
| 渲染层 | `XComponent(SURFACE)` 全屏 | 无 |
| Surface 协调 | `setSurfaceId` + `stateChange('initialized')` 双向兜底 | 不涉及 |
| 控件层 | 顶/中/底 + 两侧 -15s +15s + 中心圆形 | MiniPlayer 单行 |
| 方向 | `setPreferredOrientation(LANDSCAPE)` 入出对称 | 不改 |
| safeArea | 页内主动查 + 上一页 onPageShow 重查 | 一般不需 |
| 后台 | **不加** AudioPlayback；要后台显示走 PiP | `startBackgroundRunning(AUDIO_PLAYBACK)` + AVSession |
| 错误 | 全屏错误遮罩 + "返回"按钮 | Toast / 状态栏图标 |
| 返回拦截 | 挽留 Dialog | 可选 |

---

## 常见错误（对 SKILL.md §"常见错误" 的补充放大）

### 视频首次播放无画面 / 黑屏
**根因**：`surfaceId` 还没注入就 `prepare()` 了。
**检查**：确认 `setSurfaceId` 和 `onStateChange('initialized')` 都做了"对方就位没"判断。

### 返回上一页顶部被状态栏盖
**根因**：Player 横屏 → pop 回竖屏时系统 AvoidArea 变了，上一页 `@Local inset` 未重查。
**修复**：上一页加 `onPageShow` 重调 `querySafeAreaInsets`。

### 顶部/底部控件栏变纯黑大色块遮住视频
**根因**：`linearGradient.colors` 用了 `[0xB3000000, ...]` number 型 ARGB，alpha 被吞。
**修复**：所有颜色必须用 rgba 字符串 `['rgba(0,0,0,0.55)', ...]`。

### XComponent onDestroy 后 AVPlayer 崩溃
**根因**：Surface 已销毁但 AVPlayer 还在写帧。
**修复**：`onDestroy` 里调 `core.release()` 兜底；页面 `aboutToDisappear` 也调一次（防 onDestroy 未触发）。

### `BackgroundMode.AUDIO_PLAYBACK` 被系统拒批
**根因**：视频页无声音流，申请音频后台任务被策略拒。
**修复**：删除；要后台显示画面走 PiP（`arkts-multi-window`）。
