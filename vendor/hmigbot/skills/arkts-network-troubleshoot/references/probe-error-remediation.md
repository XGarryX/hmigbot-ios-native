# probe 错误 → 修法 知识库（可增长）

> auth-chain 活性探针（[probe-runbook.md](probe-runbook.md)）循环时，按后端回包的**业务错误码/文案**查此表：判"归类"决定循环还是停，取"修法/候选来源"调字段。
> **如何增长**：probe 撞到**新的**错误→修法模式（KB 无匹配）→ 冒泡的同时**追加一条**到本表。novel 门只发现一次，下个项目自动受益——这是把"单点补丁"沉淀成系统资产的地方。
> **归类三分类**（见 runbook）：`客户端可调`=循环调；`后端侧`=立即停+冒泡(需后端配合)；`人输/MISSING-TRUTH`=立即停+冒泡(值在源码/需用户)。
> 匹配用**模式**（错误码 + 文案关键词），不同项目文案会变，抓语义。

| 症状（错误码 / 文案模式） | 归类 | 诊断 | 修法 / 候选来源 |
|---|---|---|---|
| `-401` 类 / "权限校验未通过" / "请下载安装新包" / "版本" | 客户端可调 | 公参身份/版本门：请求缺正确身份值，或用了占位版本 | 填公参对象真实身份值——`versionCode`/`versionName`/`baseType`/`packageName` 从 **flavor 配置**（`product.xml` 等被 build.gradle 解析的 XML）取；**禁 gradle 默认占位**（如 `versionName "1.0"`/code 1）。这些值同时进签名串。 |
| `-500` 类 + "mediaNo" / "媒体号" / 某枚举 `.ordinal()` NPE / 某映射 null | 客户端可调 | 渠道→媒体号(或类似)映射查空：用的渠道后端表里没有 | 换**真实分发渠道**——从 walle **渠道清单** `channel/*.txt` 取真实值；**禁 fallback 默认渠道**（源码 getChannel 的兜底常量，后端不认）。 |
| `-500` 类 + "Column 'XXX' cannot be null" / DB 约束 / NOT NULL | 客户端可调 | 后端建记录时某字段 DB 非空约束，请求送了空 | 该字段填**非空**。设备标识类：OAID 非全 0 才用、否则退持久化 UUID；androidId 用 16 hex；**禁送空串/全 0**（见 framework-kit-mapping §5）。 |
| `code:"000"` / "请登录" / "token 无效" / "access_token 非法" | 视端点而定 | token 门。**先判端点是否本该免 token** | (a) 若靶点确需 token（业务鉴权，非签名问题）→ 换更浅的**真免 token** 端点（config/system/version/游客换发）；(b) 若在**真公共端点**上：正确签名过、错签名/nonce 不匹配同样"请登录"= **签名被真校验**，用"正确 vs 错误签名"对照即可证签名字节正确。 |
| "解密失败" / "参数解析异常" / 协议层拒绝 / body 解不开 | 人输 / MISSING-TRUTH | body 加密层字节不对（AES 等） | AES 密钥/IV/模式须**字节真值**。若密钥被掩码或封在不可读 AAR → **停 + 冒泡** `MISSING-TRUTH`（循环修不了，值得从源码/厂商/后端要）。用"垃圾凭证"打时：得到**业务拒绝**=加密对；**协议拒绝**=加密错。 |
| 防重打包指纹被拒 / "safe-env" 类 / 签名指纹校验失败 | 客户端可调（有 keystore）/ 否则后端 | 请求头含 APK/HAP 签名指纹（如 `safe-env-token = ts.md5(deviceId-ts-签名MD5)`），后端校验它 | 从项目 **keystore**（`app/sign/*.jks`/`debug.keystore`）用 `keytool -exportcert` 导出证书 DER → MD5(大写) = 签名指纹（Android `signatures[0].toByteArray()` 就是该 DER）。若后端认的是**另一套签名**（release/线上）→ 归**后端侧**，需后端把 HMOS 签名加白名单。 |
| 所有端点（含启动/公共）都要 token / 最外层全局 token 门 | 后端侧 / 联调 | 该环境有最外层全局 token 过滤，token 校验先于签名/业务短路 | **停 + 冒泡**："新客户端在该环境如何 bootstrap 第一个 token？" 须问后端（dev 环境的公共端点白名单常与生产不一致，bootstrap 端点如 vistorToken 可能被误挡）。 |
| 明确 "sign invalid" / "签名错误"（非 token、非业务层） | 客户端可调 | 签名字节不对 | 逐项查：参数**键序**（字典序、大小写敏感 `CASE_INSENSITIVE`？）、hex **大小写**、**时间窗**（毫秒 vs 秒、分钟窗算法）、盐/key 值、**公参对象是否进签名串 + 注入顺序**（先注公参后算签名 vs 反之，键序会变）。拿一次真包/golden 逐字节对。 |

## 条目来源（provenance，便于复核）

- `-401` / `mediaNo` / `ANDROID_ID NOT NULL`：AIPPT initUser 探针实测（渠道须真实 walle 值、androidId 是后端 DB 约束）。
- `code:000 请登录` 对照法：xiaoyibang `common/system` 公共端点（正确签名 200、错签名被拒）+ motu vistorToken（token 先短路）。
- `解密失败` / MISSING-TRUTH：xiaoyibang 登录体 AES（密钥须字节真值）。
- 防重打包指纹 keystore 算法：motu safe-env-token（从 `app/sign/debug/debug.keystore` keytool 导出算 MD5）。
- 全局 token 门：motu dev 后端（vistorToken/checkVersion 全 token 短路）。
