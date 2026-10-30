# 私仓依赖规范（R2）

## 规则原文

各业务线必须接入公司自有私有化底层仓库（**私仓**）`http://repo.dadoubk.cn/harmony/repos/ohpm/`，可在根目录 `oh-package.json5` 中引用各子仓库。

## 🔑 私仓优先原则（R2.0，必读）

> **能用私仓就用私仓**——这是规范第二章的核心约束，也是客户验收的硬红线。

- ✅ 路由（公司业务）→ 用 `RouterUtils`（私仓 lib_common），**不要**手撸 NavPathStack 包装
- ✅ KV 存储 → 用 `PreferenceUtil`（私仓 lib_common），**不要**直调 `@ohos.data.preferences`
- ✅ 颜色 hex → ColorMatrix → 用 `ColorUtils.hexToColorMatrix`（私仓 lib_common）
- ✅ HTTP 请求 → 用 `RequestUtil`（私仓 lib_network，公司服务器）/ `ExternalReqUtil`（私仓 lib_network，第三方 API）
- ✅ ViewModel 基类 → 继承 `BaseViewModel`（私仓 lib_common，复杂主页面 VM）
- ✅ 断点适配 → 用 `BreakpointModel`（私仓 lib_common）连接 AppStorageV2
- ✅ 安全距 → 用 `WindowModel.windowTopPadding` / `windowBottomPadding`（私仓 lib_common）
- ✅ 通用 ArkUI 组件 → 优先 `lib_widget`（私仓）已有的，避免造重复轮子
- ✅ 支付 / 推送 / 应用内购 → 对应 `lib_payment / lib_umeng / lib_hmiap`（均私仓）
- ✅ **客户内容平台**（素材 / 运营位 / 推荐内容 / 灵感页等接口）→ **直接 `import` 复用 `lib_starburst`（私仓）暴露的 API**，禁止业务侧自写 HTTP 调用 / DTO 类型 / 响应解析。**lib_starburst 不是数据上报库，是客户的内容供给平台 SDK**

**反例**（违反 R2.0 → P1）：自己 wrap 一层"MyRouter / MyHttpClient / MyPrefStore"等"自造轮子"绕过私仓。允许的特殊场景仅限于**私仓不支持的极个别能力**（如 OSS 大文件下载、特殊 SDK 透传），需在 plan 阶段显式记录豁免理由。

## 私仓子库清单（均来自 `repo.dadoubk.cn`）

| 模块（私仓） | 用途 |
|---|---|
| `lib_common` | 公共模块（含 RouterUtils（私仓）/ PreferenceUtil（私仓）/ ColorUtils（私仓）/ BaseViewModel（私仓）/ BreakpointModel（私仓）/ WindowModel（私仓）） |
| `lib_widget` | 公共 ArkUI 组件 |
| `lib_network` | 网络请求（含 RequestUtil（私仓）/ ExternalReqUtil（私仓）） |
| `lib_payment` | 支付模块 |
| `lib_starburst` | **客户内容供给平台 SDK**（素材 / 运营位 / 推荐内容 / 灵感页接口）—— **不是数据上报**，是从客户后台拉取业务内容的统一入口 |
| `lib_umeng` | 友盟统计 |
| `lib_hmiap` | 鸿蒙联运（**不启用时锁 1.0.0**） |

## 必填 vs 按需

规范原文措辞是"**可在**根目录 oh-package.json5 中引用各个子仓库"——除了 `.ohpmrc` 接入仓库是 MUST，**子库不是全要必引**：

| 子库 | 何时引 |
|---|---|
| `lib_common` | **必引**（提供 BaseViewModel/RouterUtils/PreferenceUtil/ColorUtils/BreakpointModel/WindowModel 等核心，几乎所有规则都依赖它） |
| `lib_widget` | **强烈建议**（公共 ArkUI 组件，迁移成本低、复用收益高） |
| `lib_network` | 工程**有 HTTP 网络请求**就必引 |
| `lib_payment` | 有支付场景才引 |
| `lib_starburst` | 调用客户内容平台接口（素材/运营位/推荐内容/灵感页等）才引；调用时**直接 import 现成 API**，不要自写 HTTP/类型/解析 |
| `lib_umeng` | 用到友盟统计才引 |
| `lib_hmiap` | 鸿蒙联运：启用→引最新版；**不启用→必须锁 1.0.0**（规范明确） |

> audit 时不要一刀切要求全引——按工程实际功能判定。

## 必做配置

### `.ohpmrc`（根目录）

```
registry=https://ohpm.openharmony.cn/ohpm/,http://artifact.bytedance.com/repository/byted-ohpm/,http://repo.dadoubk.cn/harmony/repos/ohpm/
```

> 三个 registry 都要保留：官方 + 字节 + 公司私仓。模板见 `assets/ohpmrc.template`。

### 根 `oh-package.json5`

`dependencies` 引入业务用得到的 lib_*；`overrides` 把私仓版本锁定，防止子模块各自引用版本不一致。模板见 `assets/root-oh-package.json5.template`。

```json5
{
  "dependencies": {
    "lib_common": "1.1.5",
    "lib_network": "1.0.9",
    "lib_widget": "1.0.2",
    // 按需...
  },
  "overrides": {
    "lib_common": "1.1.5",
    "lib_network": "1.0.9",
    "lib_widget": "1.0.2"
  }
}
```

> **为什么要 overrides**：features/components 子模块都会各自声明 lib_common 等依赖，如果根没 overrides，hvigor 解析时不同子模块可能拿到不同版本，导致 RouterUtils 等单例行为不一致。

### 各 features / components 子模块的 oh-package.json5

直接 `"lib_common": "1.1.5"` 这样写普通依赖，根的 overrides 会保证版本统一。

## 改造步骤

1. 检查 `.ohpmrc`，若缺失或不含 `dadoubk`，覆盖为模板内容。
2. 在根 `oh-package.json5` 的 `dependencies` + `overrides` 加上规则要求的 lib_*（按 audit 结果选用，不要全加，没用到的别引以免增包体）。
3. 把 entry 里所有手撸的 router、网络、持久化、颜色工具替换为 lib_common / lib_network 提供的实现：
   - 路由 → `RouterUtils`
   - KV 存储 → `PreferenceUtil`
   - 颜色 hex 转 ColorMatrix → `ColorUtils.hexToColorMatrix`
   - 网络请求 → `RequestUtil`（公司服务器） / `ExternalReqUtil`（三方）
4. ViewModel 基类替换为 `BaseViewModel`（lib_common 提供）。
5. `pnpm` 不可用，使用 `ohpm install` 装包；如离线，确保 `.ohpm` 缓存同步。

## 鸿蒙联运分支

```
启用鸿蒙联运 → lib_hmiap 选最新匹配版本
不启用      → lib_hmiap "1.0.0"  （规则明确要求）
```

让用户在 plan 阶段拍板。
