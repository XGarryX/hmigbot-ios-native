<!-- when: 离线库 l0-index.md 未覆盖该 SDK、文档厚度=薄、或怀疑版本漂移(离线版本较旧)时读本文件 -->
<!-- topics: 在线查询, ohpm, 版本漂移, 厂商文档, 域名白名单, 信任分级 -->

# 在线补齐协议 — 离线库查不到/不够用时走这里

离线快照优先。走线上的触发条件（满足其一）：
1. l0-index.md 索引中无该 SDK / 无对应能力分类
2. 索引"示例代码"列 = **纯文字或仅安装**，且该 SDK 目录下没有 `readme-ohpm.md`（有则先用它，那就是 ohpm README 的本地副本）
3. 索引标记文档厚度=薄（离线内容仅简介，撑不起编码）
4. 需要确认最新版本（离线版本是市场快照，常滞后于 ohpm 最新版）

在线结果必须标注：`[来源级别 T0-T4] [版本] [抓取日期]`。与离线内容冲突时以更新者为准，并提示刷新快照（`scripts/sdk_kb/README.md`）。

**先查捷径清单**：`Grep ohpm-misses.md` —— 该 SDK 在列 = 补采时已确认 ohpm 中央仓无此包，**跳过第一步**直接走第三步厂商站；全部信源穷尽仍无实质文档时，如实告知"该 SDK 无公开集成文档"，并给出 overview.md 里的厂商联系邮箱与市场详情页链接，不要凭训练记忆编造 API。

## 第一步：ohpm 中央仓（T1，主力信源，先走这条）

一次 HTTP 拿到最新版本 + 原生 Markdown README（多数厂商的 README 就是完整集成文档）：

```
搜索: GET https://ohpm.openharmony.cn/ohpmweb/registry/oh-package/openapi/v1/search
      ?condition=<关键词>&pageNum=1&pageSize=10&sortedType=relevancy&isHomePage=false
详情: GET https://ohpm.openharmony.cn/ohpmweb/registry/oh-package/openapi/v1/detail/<URL编码包名>
      如: .../detail/%40umeng%2Fpush
```

detail 返回关键字段：
- `readmeCnUrl` / `changelogUrl` — **原生 .md 直链**，curl 即得，无需任何解析
- `versions` — 全部历史版本+发布时间（与 l0-index 的快照版本对比即知漂移）
- `org` / `publisherName` — 官方性交叉验证（org 与厂商一致 = 官方包）

包名优先取 l0-index.md 的 `ohpm 包名` 列；没有则用 search 搜 SDK 名/能力词。
ohpm 覆盖面大于市场快照（部分厂商只发 ohpm 不上市场），离线库查不到的 SDK 先搜这里。

## 第二步：市场接口（T0，要官方审核口径/最新 PDF 时）

```
详情: POST https://svc-drcn.developer.huawei.com/partnerVectorServlet/market/buyerQueryProductDetail
      body: {"productId": "<id>"}     # id 在 sdks/<slug>/ 目录名前 8 位可反查,或经列表接口搜
列表: POST https://svc-drcn.developer.huawei.com/partnerVectorServlet/market/product/list
      body: {"lang": "zh_CN", "pageNum": 1, "pageSize": 50,
             "categoryIdL1": "a97c5f2de7df49f49c139a32125fa4c8"}   # lang 必须 zh_CN
```

- 返回中 `manualUrl`（使用指南）与 `productApiSdkList[].interfaceFileUrl`（接口文档）是**带签名的临时 PDF 链接（约 24h 过期）**——现取现用，不要缓存 URL
- `productApiSdkList[].version` / `packageName` 是市场审核过的版本与包名（T0 口径）
- 私有未公开接口，字段可能随改版变动；失败时降级回 ohpm + 搜索

## 第三步：厂商官方文档站（T2，需要深度 API 细节时）

官方性靠域名白名单判定，不靠搜索排名：

1. 读 `references/vendor-domains.json` 取该 SDK 的 `email_domain` + `link_domains`（白名单从华为审核过的市场元数据推导，可信）
2. WebSearch 限定 `site:<白名单域名> 鸿蒙|HarmonyOS|ArkTS <API名/能力词>`
3. 白名单外的命中（CSDN/掘金/博客园等转载站）只作线索，结果标注"非官方"

解析优先级（能拿 Markdown 绝不解析 HTML，能解析 HTML 绝不碰 PDF）：
GitHub/Gitee raw md → 文档站 sitemap.xml / llms.txt → 文档框架主内容区抽取 → 浏览器渲染 SPA → PDF 转换

## 信任分级速查

| 级别 | 信源 | 用途 |
|---|---|---|
| T0 | 华为生态市场接口 | SDK 是否存在/审核版本/官方 PDF |
| T1 | ohpm 中央仓 API | 最新版本 + README 集成文档（主力） |
| T2 | 白名单厂商域名 | 深度 API 参考 |
| T3 | 华为全站搜索（celia/search，参数名 keyWord） | 华为域内文档/论坛线索 |
| T4 | 开放网络搜索 | 最后手段，必须标"非官方" |
