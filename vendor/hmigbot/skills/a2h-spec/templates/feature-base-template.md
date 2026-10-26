<!-- when: Phase C Step C3 生成 feature-base.md 时加载 -->
<!-- topics: feature-base, 数据模型, 数据库, 网络层, 事件系统, 偏好设置, 公共组件库 -->

# feature-base.md 模板（共享基础设施 Spec）

七节基础设施（数据模型 / 数据库 / 网络层 / 事件系统 / 偏好设置 / 权限声明 / 公共组件库）+ **跨栈映射基线**（项目级 Source→ArkTS 硬映射，供各 feature「实现映射」段引用）。网络层在 `api_inventory_status = ready` 时基于 `spec/baseline/api-inventory/api-inventory.json` 生成。

```markdown
# Feature Base: 共享基础设施

## 数据模型
所有实体定义 (Feed, FeedItem, FeedMedia, ...)
- 字段清单、类型、默认值
- 实体间关系（1:1, 1:N, M:N）

## 数据库
- 建表 SQL / RDB schema
- 索引定义
- 初始数据 / 迁移策略
- DAO 接口定义

## 网络层
（`api_inventory_status = ready` 时，本节基于 `spec/baseline/api-inventory/api-inventory.json` 生成；endpoint 三段式 contract 字段路径见下。**详尽公共约定（信封 / 签名头 / 公参 / 状态码 / 共享 Bean）参考** `spec/baseline/api-inventory/common.md`，本节只摘核心字段不重复展开）
- HttpClient 封装（基于 @ohos.net.http 或三方库）
- Base URL 配置 ← `api-inventory.json` 的 `base_urls`（含环境、来源文件）
- API endpoint 定义 ← `api-inventory.json` 的 `services[].endpoints[].static.*`（每条取 `http_method` + `path` + `protocol` + `request.params` + `response.{model_class, fields}`；**不读** `endpoints[].runtime` / `endpoints[].reconciled` —— 这两段在 spec 阶段恒为 `null`，由后续 `arkts-network-troubleshoot` 抓包回填）
- 请求拦截器 / 认证 ← `api-inventory.json` 的 `services[].auth_type/auth_detail`（service 层散文摘要）与 `third_party_apis[].auth_detail`（含自定义签名算法）；**结构化 header 名 / App 凭证名表** ← `raw_apis.json` 的 `api_related_constants[header]+[app_secret]`（v1.2 新增；详尽人类可读视图见 `common.md` §签名头 · §App 凭证；含 `secret` 字样的桶项**仅落名不落值**，避免凭证进 spec 仓）
- 公共请求参数（多端点复用，如 platformInfo） ← `raw_apis.json` 的 `api_related_constants[param]`（v1.2，多端点复用部分；单端点专属字段留在各 endpoint 请求表；详见 `common.md` §公共请求参数）
- 业务状态码 ← `raw_apis.json` 的 `api_related_constants[code]`（v1.2；详见 `common.md` §业务状态码），作为下方「错误处理策略」的结构化底座
- 项目画像参考 ← `api-inventory.json` 的 `project_profile.{http_stack, architecture, primary_auth}`（v1.2 新增），用于确定 HMOS HttpClient 封装风格（多 base_url / 多套签名并存等）
- 错误处理策略（基于上方业务状态码表 + 各 endpoint 的 `static.response`）

## 事件系统
- EventHub 事件名常量
- 发布/订阅模式封装
- 典型事件流

## 偏好设置
- SharedPreferences → @ohos.data.preferences 键值映射
- 类型定义
- 默认值

## 权限声明
- module.json5 权限配置
- 运行时权限请求逻辑

## 公共组件库
- Toolbar / ActionBar 通用组件
- TabBar 通用组件
- Card / ListItem 通用组件
- 作为 Agent UI 还原的样式锚点，确保跨页面风格一致

## 跨栈映射基线（Source→ArkTS）
项目级复用的硬映射；各 feature 的「实现映射」段引用本表，不各自重复决策：
- 平台专有 UI / 图形类型 → ArkUI/ArkTS 等价（统一选型）
- 自定义序列化 / 编解码框架 → ArkTS 实现策略 + 字段号/tag 来源
- 原生 / GPU / 桥接原语 → NAPI 方案或占位归属
- 平台文件、并发、弱引用/缓存原语 → ArkTS 等价或降级策略
> 目的：HARD 映射只决策一次，避免每个 slice 的 worker 各自重新发明或就地留桩。
```
