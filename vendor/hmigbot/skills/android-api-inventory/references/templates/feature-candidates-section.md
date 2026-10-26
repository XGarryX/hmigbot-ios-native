# Phase 4 分支 C：Feature 候选建议 模板

> SKILL.md Phase 4 分支 C（输入源模式）的输出示例。聚类规则在主文件，**具体写什么样的 markdown 与 JSON** 在本文件。
>
> 触发条件：spec 尚未生成（`feature-index.md` 与 `features/F*.md` 都不存在）—— `a2h-spec` Phase B 并行轨调用本 skill 的标准分支。

---

## markdown 输出（追加到 `api-inventory.md` 的「Feature 候选 / 覆盖度分析」段）

```markdown
## Feature 候选建议（供 spec 生成参考）

> 本项目 spec 尚未生成，以下候选基于扫描结果聚类推断，供 a2h-spec 后续决定 F0xx 划分时参考。
> **这些是候选**，spec 作者可采纳 / 调整 / 重划，不要写得像定论。

### 候选 F-user: 用户认证与账号
- 路径前缀：`/user/*`、`/app/sendSmsCode`
- 端点数：12
- 第三方依赖：微信 OAuth
- 迁移关注点：多种三方账号绑定（支付宝 / 微信 / 华为 / 荣耀）认证流程不同

### 候选 F-pay: 支付与 VIP
- 路径前缀：`/pay/*`、`/product/*`
- 端点数：13
- 迁移关注点：订单轮询、自动续费签约

### 候选 F-asset: 资产 / 配额经济
- 路径前缀：`/asset/*`、`/productComm/*`
- 端点数：10
- 迁移关注点：免费配额 / 金币消耗 / 礼包发放业务流

### 候选 F-aiimage: AI 图像生成
- 第三方依赖：火山引擎 CV
- 端点数：6（自有路由）+ N（火山 CV Action）
- 迁移关注点：SSE 异步任务 + AWS-style 签名，签名算法需 HMOS 重写

*（其余候选按相同格式列出）*
```

## JSON 输出（`coverage.feature_candidates` 字段）

```json
"coverage": {
  "_mode": "candidate",
  "spec_documented": 0,
  "inventory_found": 97,
  "gaps": [],
  "feature_candidates": [
    {
      "suggested_id": "F-user",
      "suggested_name": "用户认证与账号",
      "path_prefixes": ["/user/", "/app/sendSmsCode"],
      "endpoint_count": 12,
      "third_party_deps": ["WeChat OAuth"],
      "migration_concerns": ["多家三方账号绑定认证流程各异"]
    },
    {
      "suggested_id": "F-pay",
      "suggested_name": "支付与 VIP",
      "path_prefixes": ["/pay/", "/product/"],
      "endpoint_count": 13,
      "third_party_deps": [],
      "migration_concerns": ["订单轮询", "自动续费签约"]
    },
    {
      "suggested_id": "F-aiimage",
      "suggested_name": "AI 图像生成",
      "path_prefixes": ["/aiimage/"],
      "endpoint_count": 6,
      "third_party_deps": ["Volcano Engine CV"],
      "migration_concerns": ["SSE 异步任务", "AWS-style 签名移植"]
    }
  ]
}
```

---

## 聚类规则速查

1. **按路径前缀聚类** —— `/user/*` / `/pay/*` / `/asset/*` 等通常各对应一个 feature
2. **按第三方 provider 提议** —— 每个重要 provider 通常对应一个 AI 能力 feature（火山 CV → "AI Image Generation"）
3. **迁移关注点标签** —— 扫描结果对迁移难度高的接口打标签：
   - SSE / WebSocket（HMOS 支持有限）
   - 自定义签名（AWS-style / XXTEA / HMAC，需移植算法）
   - Multipart 上传
   - 异步任务模式（submit → poll → result）
   - 跨 Service 重复的端点

---

## 输出目标提醒

分支 C 的输出**喂给 a2h-spec**，不是终版交付。措辞上：

- ✅ "以下候选基于扫描结果聚类推断，供 a2h-spec 后续决定 F0xx 划分时参考"
- ✅ "候选 F-user"（用 `F-<name>` 而非 `F001` —— spec 作者可能重排）
- ❌ "Feature F001: 用户登录"（写得像定论）
