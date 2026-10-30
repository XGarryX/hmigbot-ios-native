# 三方库完整对照表

> 按功能分类保留原 L1–L5 选择层次和目标候选。源列是实际依赖/能力类别，不断言项目一定使用该库。目标包当前版本、许可、可用性和调用差异仍须按原选型步骤核验；表中命中不是自动接受或已经安装。

---

## 图片加载与显示

| iOS 库 | ArkTS 替代 | Level | 安装方式 | 备注 |
|-----------|-----------|-------|---------|------|
| 实际原生图片下载/缓存库 | `@ohos/imageknife` | L1 | `ohpm install @ohos/imageknife` | 内存+磁盘二级缓存 |
| 实际第二套图片缓存依赖（若有） | `@ohos/imageknife` | L1 | 同上 | 功能覆盖 |
| SwiftUI Image / UIImage 的简单显示链 | `Image` 组件 + `photoAccessHelper` | L2 | 原生 | 简单场景直接用原生 Image |
| 实际大图分块/缩放依赖 | `@ohos/largeimage` | L1 | `ohpm install @ohos/largeimage` | 支持缩放/拖拽/旋转 |
| UIScrollView 缩放 / 实际图片浏览组件 | `Image` + `PinchGesture` | L2 | 原生 | 手动实现手势缩放 |
| Image/UIImageView 的圆形裁剪 | `Image` + `.borderRadius('50%')` | L2 | 原生 | 原生属性即可 |
| 实际原生裁剪库 | `Canvas` + 手势 API | L5 | 自研 | 需自绘可拖拽裁剪框 |
| 实际原生 SVG 解析依赖 | ohos-svg | L1 | 需确认最新地址 | SVG 解析渲染 |
| 实际 GIF 解码/动画依赖 | ohos_gif-drawable | L1 | 需确认最新地址 | 基于 Canvas 渲染 GIF |
| APNG 动画库 | `ImageAnimator` 组件 | L2 | 原生 | 基础动画格式支持 |
| WebP 解码 | `Image` 组件 | L2 | 原生 | HarmonyOS 原生支持 WebP |

## 图片编辑与滤镜

| iOS 库 | ArkTS 替代 | Level | 安装方式 | 备注 |
|-----------|-----------|-------|---------|------|
| ImgLy PESDK | `Canvas` + `@kit.ImageKit` PixelMap | L5 | 自研 | 商业库无鸿蒙版 |
| GPUImage | `@kit.ImageKit` + `effectKit` | L2 | 原生 | 基础滤镜可用 |
| 实际原生像素滤镜依赖 | PixelMap 像素操作 | L2 | 原生 | 灰度/复古/反转可自研 |
| Lottie | `@ohos/lottie` | L1 | `ohpm install @ohos/lottie` | Lottie 动画支持 |

## 视频播放与编辑

| iOS 库 | ArkTS 替代 | Level | 安装方式 | 备注 |
|-----------|-----------|-------|---------|------|
| AVFoundation / AVPlayer | `Video` 组件 / `AVPlayer` | L2 | 原生 | 状态机有差异（见踩坑 P13） |
| IJKPlayer | `Video` 组件 / `AVPlayer` | L2 | 原生 | 同上 |
| ImgLy VESDK | FFmpeg + 自研 UI | L3+L5 | NAPI | 商业库无鸿蒙版 |
| FFmpeg | `HarmonyOS-tpc/FFmpeg` | L3 | HAR/NAPI | 完整 7 大核心库 |
| 实际三方视频播放器 | 已核验的鸿蒙播放器 / AVPlayer | L1/L2 | 按实际版本核验 | 保留协议、状态机与生命周期 |
| 实际原生全景/VR 渲染依赖 | Three.js + Pannellum | L4 | ArkWeb + JS | 全景/360度视频 |

## 网络与数据

| iOS 库 | ArkTS 替代 | Level | 安装方式 | 备注 |
|-----------|-----------|-------|---------|------|
| URLSession / URLRequest | `@kit.NetworkKit` http | L2 | 原生 | 实例需 `destroy()` |
| 实际原生网络封装库 | `@ohos/axios` 或原生 http | L1/L2 | `ohpm install @ohos/axios` | axios 提供更友好的 API |
| Codable/CodingKeys / 实际解码映射库 | `JSON.parse` / `JSON.stringify` | L2 | 原生 | ArkTS 原生支持 |
| Core Data / 实际 SQLite ORM / Realm | `@kit.ArkData` relationalStore | L2 | 原生 | 手写 SQL |
| UserDefaults / 实际偏好存储 | `@kit.ArkData` preferences | L2 | 原生 | 异步 API |

## UI 框架与组件

| iOS 库 | ArkTS 替代 | Level | 安装方式 | 备注 |
|-----------|-----------|-------|---------|------|
| NSLayoutConstraint / UIStackView / SwiftUI 组合 | `Flex`/`Stack`/`Row`/`Column` | L2 | 原生 | 声明式布局 |
| UITableView / UICollectionView / SwiftUI 列表 | `List`/`Grid`/`WaterFlow` | L2 | 原生 | 配合 `ForEach`/`LazyForEach` |
| UIPageViewController / 分页 TabView | `Swiper` | L2 | 原生 | 支持水平/垂直翻页 |
| UIRefreshControl / refreshable | `Refresh` 组件 / `@ohos/pulltorefresh` | L1/L2 | 原生或 ohpm | 下拉刷新 |
| 实际 UIKit / SwiftUI 控件 | ArkUI 原生组件 | L2 | 原生 | Tabs/Dialog/Toast 等 |
| UINavigationController / NavigationStack | `Navigation` + `NavPathStack` | L2 | 原生 | 路由栈管理 |

## 工具与基础设施

| iOS 库 | ArkTS 替代 | Level | 安装方式 | 备注 |
|-----------|-----------|-------|---------|------|
| 实际 Combine/RxSwift / Swift Task | `async/await` + `Promise` | L2 | 原生 | 原生异步 |
| NotificationCenter / 实际事件发布器 | 自建 `Map<string, Function[]>` | L5 | 自研 | 简单发布订阅 |
| BGTaskScheduler / 实际后台任务 | `@kit.BackgroundTasksKit` | L2 | 原生 | 间隔约束不同 |
| 实际 os.Logger / 业务日志封装 | `hilog` (`@kit.PerformanceAnalysisKit`) | L2 | 原生 | 系统级日志 |
| 实际 Xcode/Instruments 内存诊断 | DevEco Profiler | — | IDE 工具 | 内存分析 |
| ImageIO / 实际 EXIF 读取库 | `@kit.ImageKit` image.ImageSource | L2 | 原生 | EXIF 读取 |
| 实际原生 HTML 解析库 | `@ohos/htmlparser2` 或自研 | L1 | ohpm | HTML 解析 |
| XMLParser / 实际 XML 解析器 | `XmlPullParser` (`@ohos.xml`) | L2 | 原生 | push→pull 需重写（见踩坑 P11） |

## 商业 SDK（推送/支付/地图等）

| iOS 库 | ArkTS 替代 | Level | 处理方式 |
|-----------|-----------|-------|---------|
| Firebase | AppGallery Connect | L2 | 华为对标服务 |
| Google Maps | 华为 Map Kit | L2 | 华为对标服务 |
| 极光推送 | 极光推送鸿蒙版 | L1 | 厂商已适配 |
| 友盟+ | 友盟+鸿蒙版 | L1 | 厂商已适配 |
| 个推 | 个推鸿蒙版 | L1 | 厂商已适配 |
| 微信 SDK | 联系厂商获取鸿蒙版 | — | 类型 C：联系厂商 |
| 支付宝 SDK | 支付宝鸿蒙版 | L1 | 已适配 |
| LocalAuthentication | `@ohos.userIAM.userAuth` | L2 | 原生 API |

---

## 按 Level 汇总（仅原候选层次，不是本项目依赖数量）

| Level | 数量 | 代表库 |
|-------|------|-------|
| **L1 ohpm** | 按实际命中 | imageknife, largeimage, lottie, axios, pulltorefresh, 极光, 友盟, 个推, 支付宝 |
| **L2 原生 API** | 按实际命中 | Image, Video/AVPlayer, relationalStore, preferences, http, Canvas, Navigation, hilog... |
| **L3 NAPI** | 按实际命中 | FFmpeg, OpenCV, OpenSSL |
| **L4 WebView+JS** | 按实际命中 | Three.js(全景), Fabric.js(编辑) |
| **L5 自研** | 按实际命中 | EventBus, 图片裁剪框, PESDK 简化版 |
