# 三方库完整对照表

> 50+ Android 库到 ArkTS 的替代方案映射。按功能分类，每个条目标注 Level、安装方式和注意事项。

---

## 图片加载与显示

| Android 库 | ArkTS 替代 | Level | 安装方式 | 备注 |
|-----------|-----------|-------|---------|------|
| Glide | `@ohos/imageknife` | L1 | `ohpm install @ohos/imageknife` | 内存+磁盘二级缓存 |
| Picasso | `@ohos/imageknife` | L1 | 同上 | 功能覆盖 |
| Coil | `Image` 组件 + `photoAccessHelper` | L2 | 原生 | 简单场景直接用原生 Image |
| SubsamplingScaleImageView | `@ohos/largeimage` | L1 | `ohpm install @ohos/largeimage` | 支持缩放/拖拽/旋转 |
| PhotoView | `Image` + `PinchGesture` | L2 | 原生 | 手动实现手势缩放 |
| CircleImageView | `Image` + `.borderRadius('50%')` | L2 | 原生 | 原生属性即可 |
| Android Image Cropper | `Canvas` + 手势 API | L5 | 自研 | 需自绘可拖拽裁剪框 |
| AndroidSVG | ohos-svg | L1 | 需确认最新地址 | SVG 解析渲染 |
| GIF Drawable | ohos_gif-drawable | L1 | 需确认最新地址 | 基于 Canvas 渲染 GIF |
| APNG 动画库 | `ImageAnimator` 组件 | L2 | 原生 | 基础动画格式支持 |
| WebP 解码 | `Image` 组件 | L2 | 原生 | HarmonyOS 原生支持 WebP |

## 图片编辑与滤镜

| Android 库 | ArkTS 替代 | Level | 安装方式 | 备注 |
|-----------|-----------|-------|---------|------|
| ImgLy PESDK | `Canvas` + `@kit.ImageKit` PixelMap | L5 | 自研 | 商业库无鸿蒙版 |
| GPUImage | `@kit.ImageKit` + `effectKit` | L2 | 原生 | 基础滤镜可用 |
| zomato/androidphotofilters | PixelMap 像素操作 | L2 | 原生 | 灰度/复古/反转可自研 |
| Lottie | `@ohos/lottie` | L1 | `ohpm install @ohos/lottie` | Lottie 动画支持 |

## 视频播放与编辑

| Android 库 | ArkTS 替代 | Level | 安装方式 | 备注 |
|-----------|-----------|-------|---------|------|
| ExoPlayer / Media3 | `Video` 组件 / `AVPlayer` | L2 | 原生 | 状态机有差异（见踩坑 P13） |
| IJKPlayer | `Video` 组件 / `AVPlayer` | L2 | 原生 | 同上 |
| ImgLy VESDK | FFmpeg + 自研 UI | L3+L5 | NAPI | 商业库无鸿蒙版 |
| FFmpeg | `HarmonyOS-tpc/FFmpeg` | L3 | HAR/NAPI | 完整 7 大核心库 |
| GSYVideoPlayer | GSYVideoPlayer (鸿蒙版) | L1 | 需确认最新地址 | 支持多内核和滤镜 |
| Google VR SDK | Three.js + Pannellum | L4 | ArkWeb + JS | 全景/360度视频 |

## 网络与数据

| Android 库 | ArkTS 替代 | Level | 安装方式 | 备注 |
|-----------|-----------|-------|---------|------|
| OkHttp | `@kit.NetworkKit` http | L2 | 原生 | 实例需 `destroy()` |
| Retrofit | `@ohos/axios` 或原生 http | L1/L2 | `ohpm install @ohos/axios` | axios 提供更友好的 API |
| Gson / Moshi | `JSON.parse` / `JSON.stringify` | L2 | 原生 | ArkTS 原生支持 |
| Room / GreenDAO / Realm | `@kit.ArkData` relationalStore | L2 | 原生 | 手写 SQL |
| SharedPreferences / DataStore | `@kit.ArkData` preferences | L2 | 原生 | 异步 API |

## UI 框架与组件

| Android 库 | ArkTS 替代 | Level | 安装方式 | 备注 |
|-----------|-----------|-------|---------|------|
| ConstraintLayout | `Flex`/`Stack`/`Row`/`Column` | L2 | 原生 | 声明式布局 |
| RecyclerView | `List`/`Grid`/`WaterFlow` | L2 | 原生 | 配合 `ForEach`/`LazyForEach` |
| ViewPager2 | `Swiper` | L2 | 原生 | 支持水平/垂直翻页 |
| SwipeRefreshLayout | `Refresh` 组件 / `@ohos/pulltorefresh` | L1/L2 | 原生或 ohpm | 下拉刷新 |
| Material Components | ArkUI 原生组件 | L2 | 原生 | Tabs/Dialog/Toast 等 |
| Navigation Component | `Navigation` + `NavPathStack` | L2 | 原生 | 路由栈管理 |

## 工具与基础设施

| Android 库 | ArkTS 替代 | Level | 安装方式 | 备注 |
|-----------|-----------|-------|---------|------|
| RxJava / Coroutine | `async/await` + `Promise` | L2 | 原生 | 原生异步 |
| EventBus | 自建 `Map<string, Function[]>` | L5 | 自研 | 简单发布订阅 |
| WorkManager | `@kit.BackgroundTasksKit` | L2 | 原生 | 间隔约束不同 |
| Timber / Logger | `hilog` (`@kit.PerformanceAnalysisKit`) | L2 | 原生 | 系统级日志 |
| LeakCanary | DevEco Profiler | — | IDE 工具 | 内存分析 |
| Sanselan / ExifInterface | `@kit.ImageKit` image.ImageSource | L2 | 原生 | EXIF 读取 |
| JSOUP (HTML 解析) | `@ohos/htmlparser2` 或自研 | L1 | ohpm | HTML 解析 |
| SAX Parser | `XmlPullParser` (`@ohos.xml`) | L2 | 原生 | push→pull 需重写（见踩坑 P11） |

## 商业 SDK（推送/支付/地图等）

| Android 库 | ArkTS 替代 | Level | 处理方式 |
|-----------|-----------|-------|---------|
| Firebase | AppGallery Connect | L2 | 华为对标服务 |
| Google Maps | 华为 Map Kit | L2 | 华为对标服务 |
| 极光推送 | 极光推送鸿蒙版 | L1 | 厂商已适配 |
| 友盟+ | 友盟+鸿蒙版 | L1 | 厂商已适配 |
| 个推 | 个推鸿蒙版 | L1 | 厂商已适配 |
| 微信 SDK | 联系厂商获取鸿蒙版 | — | 类型 C：联系厂商 |
| 支付宝 SDK | 支付宝鸿蒙版 | L1 | 已适配 |
| BiometricPrompt | `@ohos.userIAM.userAuth` | L2 | 原生 API |

---

## 按 Level 汇总

| Level | 数量 | 代表库 |
|-------|------|-------|
| **L1 ohpm** | ~12 | imageknife, largeimage, lottie, axios, pulltorefresh, 极光, 友盟, 个推, 支付宝 |
| **L2 原生 API** | ~25 | Image, Video/AVPlayer, relationalStore, preferences, http, Canvas, Navigation, hilog... |
| **L3 NAPI** | ~3 | FFmpeg, OpenCV, OpenSSL |
| **L4 WebView+JS** | ~2 | Three.js(全景), Fabric.js(编辑) |
| **L5 自研** | ~5 | EventBus, 图片裁剪框, PESDK 简化版 |
