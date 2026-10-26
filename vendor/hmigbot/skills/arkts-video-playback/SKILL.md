---
name: arkts-video-playback
description: 生成 ArkTS/HarmonyOS 视频播放代码（AVPlayer 视频路径 + XComponent Surface 集成）。当用户需要实现 AVPlayer 视频播放、XComponent Surface 集成、横屏全屏播放器、视频 letterbox（保留原始宽高比）、控件 3.5s 自动隐藏、点击唤出控件、播放器返回挽留 Dialog、视频画中画 PiP 时触发。**前置依赖**：AVPlayer 状态机基础、音频播放、fd:// 协议、后台播放在 arkts-media-playback。
metadata:
  type: domain
  domain: media
  tags:
  - domain
  - media
  - video
  - xcomponent
  - surface
  - letterbox
  - fullscreen
  - pip
  - webp
---
# ArkTS Video Playback — 视频播放生成器

## 0. 与其他 skill 的关系（边界）

### 0.1 与 arkts-media-playback（音频通用基础 — 父子关系）

**音视频通用基础在 `arkts-media-playback`**：

- AVPlayer 状态机（Idle → Initialized → Prepared → Playing/Paused → Stopped → Released）
- fd:// 本地文件协议（视频本地文件同样适用）
- PlaybackSpeed 6 档枚举（视频倍速控件复用同一逻辑）

**本 skill 是"视频特化层"**——只描述视频场景独有的工程问题：

| 维度 | 本 skill 处理 |
|---|---|
| Surface 协调 | XComponent(SURFACE) + surfaceId 时序 |
| 启播链路 | 调用方透传 videoUrl + Player 三路兜底 |
| UI 基线 | 视频播放页对齐 Android 原生（横屏 / safeArea / 沉浸全屏）|
| Letterbox | 保留视频原始宽高比 + 顶/底栏钉视频帧 |
| 自动隐藏 | 控件 3.5s 三态定时器 |
| 按钮资源 | Android webp 直拷，禁用 Unicode 字符 |
| 视频专属错误 | linearGradient alpha / AUDIO_PLAYBACK 误用 / 横屏方向 / 透明点击层 |

视频场景**不要**无脑加 `BackgroundMode.AUDIO_PLAYBACK`（被系统策略限制）；视频后台走画中画 PiP，不是 AVPlayer 后台续播。

### 0.2 与 arkts-immersive-safearea（边界精确化）

| 场景 | 走哪个 | 关键细节 |
|---|---|---|
| 通用沉浸式（statusBar / navBar / cutout 透明 + 全屏背景延伸）| **arkts-immersive-safearea** | 四层架构 + WindowModel 响应式 padding |
| 视频横屏特化：防进度条最右段被系统手势横条遮挡 | **本 skill**（见 `references/video-playback-page.md`） | `setSpecificSystemBarEnabled('navigationIndicator', false)` |
| 视频横屏 letterbox 模式下顶/底栏定位 | **本 skill**（见 `references/letterbox-math.md`） | 钉**视频帧**（`videoOffsetXVp/Y`），**不用** windowModel padding（不钉屏幕边）|

⚠️ 视频特化的进度条防遮 + letterbox 钉视频帧（见 `references/video-playback-page.md` / `letterbox-math.md`）**是 immersive-safearea 不覆盖的视频独有问题**，不要把"沉浸式"统一交给 safearea。

### 0.3 混合应用模式

| 应用类型 | 主用 skill | 辅助 |
|---|---|---|
| 纯音频 app（播客 / 听书） | arkts-media-playback | — |
| 音频为主 + 偶尔 MV（音乐 app） | arkts-media-playback | 本 skill（视频补丁） |
| 纯视频 app（短视频 / 课程 / 直播） | **本 skill**（主用） | arkts-media-playback（提供 AVPlayer 状态机基础） |

---

## 1. 触发场景

用户提到下列任一时触发：

- 视频播放、全屏播放器、横屏视频
- AVPlayer + XComponent / surfaceId / 视频 Surface 集成
- 视频控件自动隐藏 / 点击唤出控件
- 视频 letterbox / 视频纵横比保留 / 黑边
- 横屏强制 / 沉浸全屏 / 状态栏隐藏
- 播放器返回挽留 Dialog
- 视频按钮图标 / webp / Unicode 字形不一致
- 画中画 PiP

混合应用（如带 MiniPlayer 的音乐 app + 偶尔放 MV）走音频主干（`arkts-media-playback`）+ 本 skill 视频补丁。

---

## 实现要点 + 模板（详见 references）

> **MUST**：实现前按场景先读对应 reference——

> - 启播链路（透传 videoUrl 三路兜底 / fromJson 反序列化 / @Param 不注入处理） → `references/launch-pipeline.md`
> - 完整播放页模板（Stack 布局 / 横屏强制 / safeArea / 沉浸全屏 / dp→vp / 挽留 Dialog） → `references/video-playback-page.md`
> - Letterbox 尺寸计算 + 顶/底栏钉视频帧 → `references/letterbox-math.md`
> - 控件自动隐藏 + 透明点击层 + webp 资源 → `references/auto-hide-controls.md`

### Surface 时序 & 启播补充铁律（§10 覆盖矩阵之外）

- XComponent `onLoad` 拿 surfaceId 与 AVPlayer `prepare` 需**双向等待**；`prepared` 前的 `seek` 请求先暂存、prepared 后重放。
- 时长用 `durationUpdate` 事件获取，不用 `getDuration`。
- `router.pushUrl` 跳转路径下 `@Param` 不注入 → 用 AppStorageV2 / 显式参数透传。

> 7 条核心增量经验（自动隐藏 / webp / dp→vp / 沉浸全屏 / letterbox 定位 / videoUrl / fromJson）见 §10 覆盖矩阵。

---

## 7. 视频专属错误速记

| # | 错误 | 正确做法 |
|---|---|---|
| 1 | linearGradient 用 0xAARRGGBB number 吞 alpha | 用 'rgba()' 字符串或带 alpha 的颜色 |
| 2 | 视频页加 BackgroundMode.AUDIO_PLAYBACK | 视频后台走 PiP，不加 AUDIO_PLAYBACK |
| 3 | 忘记成对管理横屏方向 | 进/退横屏成对 set/restore orientation |
| 4 | XComponent width/height='100%' 拉伸视频 | 按 letterbox 计算实际宽高（见 letterbox-math） |
| 5 | 外层 Stack alignContent:Center 顶栏漂移 | 顶/底栏钉视频帧偏移，不用 Center |
| 6 | 忘记在 XComponent 上放透明点击层 | 之上加透明层接收点击唤出控件 |

> **MUST**：完整「错误 vs 正确」代码见对应 reference。

---

## 8. 生成检查清单

- [ ] 启播链路 3 路兜底齐全（透传 / detail-multi / detail-single）
- [ ] 业务详情接口走 fromJson 反序列化
- [ ] @Param 路径用 router.getParams() 兜底
- [ ] surfaceId 在 Initialized 之后、prepare 之前设置
- [ ] 双向等待逻辑齐（surfaceId 已设 + isInitialized 都满足才 attach）
- [ ] 横屏 / safeArea / 沉浸全屏在 aboutToAppear/aboutToDisappear 配对
- [ ] Letterbox 尺寸计算齐（xcWidthVp / xcHeightVp / videoOffsetXVp/Y）
- [ ] 顶/底栏 position 钉到视频帧（不跨整屏）
- [ ] alignContent 用 TopStart，不要用 Center
- [ ] 控件自动隐藏覆盖 PLAYING / PAUSED / PREPARED 三态
- [ ] 透明点击层在 XComponent 上方接收点击
- [ ] 按钮图标用 Android 原 webp，不用 Unicode / 手搓黑圆
- [ ] dp→vp 1:1 直拷；layout_centerVertical = top:'50%' + translate(y:-halfH)
- [ ] 挽留 Dialog 拦截 onBackPress
- [ ] linearGradient.colors 用 rgba 字符串，不用 0xAARRGGBB number
- [ ] backgroundModes **不**配 audioPlayback（视频走 PiP）

---

## 9. 跨 Skill 协作

| 场景 | 委托给 |
|---|---|
| AVPlayer 状态机基础 / fd:// / PlaybackSpeed / 后台播放 | **`arkts-media-playback`**（前置依赖）|
| 视频文件下载到沙箱 | `arkts-download-manager` |
| 媒体库 / 相册视频选择 | `arkts-system-capabilities`（photoAccessHelper）|
| 三方视频 SDK（如保留腾讯 SuperPlayer HMOS 版） | `arkts-third-party-fix` 通用 SOP |
| 字幕渲染（独立绘制） | `arkts-component-builder` |

---

## 10. References

### 7 条增量经验（Round 22-23 复盘）↔ 4 references 覆盖矩阵

| # | 增量经验 | 对应 reference |
|---|---|---|
| ① | 控件 3.5s 自动隐藏覆盖 PLAYING / PAUSED / PREPARED 三态 | `auto-hide-controls.md` |
| ② | Android→HMOS 按钮图标必须拷原工程 webp，禁用 Unicode + 手搓黑圆 | `auto-hide-controls.md` |
| ③ | dp→vp 1:1，layout_centerVertical = `top:'50%'` + `translate(y:-halfH)` | `video-playback-page.md` |
| ④ | 沉浸全屏 → `setSpecificSystemBarEnabled('navigationIndicator', false)`（防进度条最右段被遮）| `video-playback-page.md` |
| ⑤ | 顶/底栏按 `videoOffsetXVp/Y` 钉到**视频帧**（不是屏幕，避免 letterbox 黑边上挂按钮）| `letterbox-math.md` |
| ⑥ | Player 必须由调用方透传 videoUrl，避免再调 detail-single 反查（部分子项返空 + ~700ms 延迟）| `launch-pipeline.md` |
| ⑦ | 业务详情接口走 `fromJson` 反序列化（否则 plain object 字段 setter 静默失败）| `launch-pipeline.md` |

### 文件清单

- `references/launch-pipeline.md` —— 启播 3 路兜底完整代码 + 复盘 v1（覆盖经验 ⑥⑦）
- `references/video-playback-page.md` —— 完整视频播放页模板（Stack 布局 / 横屏 / 沉浸全屏 / 挽留 Dialog，覆盖经验 ③④）
- `references/letterbox-math.md` —— Letterbox 尺寸计算 + 顶底栏定位公式（覆盖经验 ⑤）
- `references/auto-hide-controls.md` —— 控件自动隐藏 + 透明点击层模板 + webp 资源指南（覆盖经验 ①②）
