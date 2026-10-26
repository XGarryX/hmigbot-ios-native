# HarmonyOS ArkTS 需求领域分类体系

> 用于 rq-parse 步骤 2（领域映射）的参考文档。将用户需求映射到技术领域时查阅。

## 领域分类树

```
HarmonyOS ArkTS 应用
├── UI 展示层
│   ├── 页面布局（Column, Row, Stack, Grid, Flex, List）
│   ├── 组件交互（Button, TextInput, Slider, Toggle, Dialog）
│   ├── 动画效果（animateTo, transition, Spring, 手势跟随）
│   ├── 自定义绘制（Canvas, Shape）
│   └── 响应式适配（断点, 折叠屏）
│
├── 导航路由
│   ├── 页面跳转（Navigation, NavPathStack, NavDestination）
│   ├── Tab 导航（Tabs, 底部导航栏）
│   ├── 侧边栏（SideBarContainer）
│   └── 路由参数传递
│
├── 状态管理
│   ├── 组件内状态（@State）
│   ├── 父子传递（@Prop, @Link）
│   ├── 跨组件（@Provide/@Consume）
│   ├── 全局状态（AppStorage, @StorageLink）
│   └── 持久化（PersistentStorage, Preferences）
│
├── 数据管理
│   ├── 数据模型定义
│   ├── 关系型数据库（RelationalStore, DAO）
│   ├── 键值存储（Preferences）
│   ├── 文件存储（fileIo, 沙箱路径）
│   └── 数据源（IDataSource, LazyForEach）
│
├── 网络通信
│   ├── HTTP 请求（@kit.NetworkKit）
│   ├── 文件下载（request.agent）
│   ├── 数据解析（JSON, XML/RSS）
│   └── 网络状态监听
│
├── 媒体处理
│   ├── 音频播放（AVPlayer）
│   ├── 视频播放（AVPlayer）
│   ├── 后台播放（ContinuousTask + AVSession）
│   ├── 媒体会话（AVSession 元数据）
│   └── 播放控制（速度, 进度, 队列）
│
├── 系统能力
│   ├── 权限管理（abilityAccessCtrl）
│   ├── 文件访问（photoAccessHelper）
│   ├── 后台任务（workScheduler, ContinuousTask）
│   ├── 通知（Notification）
│   └── 设备能力（屏幕信息, 网络类型）
│
├── 国际化
│   ├── 多语言资源
│   ├── 动态语言切换
│   └── 本地化格式（日期, 数字）
│
└── WebView
    ├── 网页加载
    ├── JS/CSS 注入
    └── 原生交互
```

## 领域 → Skill 映射表

| 领域 | 主 Skill | 辅助 Skill |
|------|---------|-----------|
| 页面布局 | `arkts-component-builder` | `arkts-pattern-library` |
| 组件交互 | `arkts-component-builder` | `arkts-state-manager` |
| 动画效果 | `arkts-animation-builder` | `arkts-component-builder` |
| 页面跳转 | `arkts-navigation-builder` | — |
| Tab 导航 | `arkts-navigation-builder` | `arkts-component-builder` |
| 组件内状态 | `arkts-state-manager` | — |
| 全局状态 | `arkts-state-manager` | — |
| 关系型数据库 | `arkts-data-layer` | — |
| 键值存储 | `arkts-data-layer` | `arkts-system-capabilities` |
| 文件存储 | `arkts-system-capabilities` | `arkts-data-layer` |
| HTTP 请求 | `arkts-data-layer` | — |
| 文件下载 | `arkts-download-manager` | `arkts-system-capabilities` |
| 数据解析 | `arkts-data-layer` | — |
| 音频播放 | `arkts-media-playback` | — |
| 后台播放 | `arkts-media-playback` | `arkts-system-capabilities` |
| 权限管理 | `arkts-system-capabilities` | — |
| 后台任务 | `arkts-system-capabilities` | — |
| 多语言 | `arkts-i18n` | — |
| WebView | `arkts-webview-manager` | — |

## 关键词信号库

用于从用户自然语言中识别领域的关键词（包括同义词和口语表达）：

### UI/交互
页面, 界面, 按钮, 列表, 弹窗, 对话框, 输入框, 图片, 图标, 卡片, 布局, 排版, 样式, 颜色, 字体, 间距, 圆角, 阴影, 滑动, 滚动, 下拉, 上拉, 刷新, 加载更多, 骨架屏, 空状态, loading, toast, 提示

### 导航
跳转, 返回, 切换页面, tab, 标签, 底部栏, 侧边栏, 抽屉, 路由, 导航, 首页, 详情页, 设置页

### 数据
保存, 存储, 数据库, 缓存, 持久化, 记录, 历史, 收藏, 书签, 配置, 设置项, 偏好, 同步

### 网络
请求, 接口, API, 服务器, 云端, 下载, 上传, 联网, 离线, 加载, 拉取, 推送, RSS, 订阅, 源

### 媒体
播放, 暂停, 停止, 音频, 视频, 音乐, 播客, 语音, 录音, 音量, 速度, 进度, 快进, 后台播放, 锁屏, 定时, 队列, 播放列表

### 系统
权限, 通知, 文件, 相册, 照片, 摄像头, 麦克风, 后台, 分享, 剪贴板, 震动
