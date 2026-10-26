> 来源: ohpm 中央仓 README(T1 信源) | 包: `gamesdklibrary` | ohpm 最新版: 1.0.3 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# GameSDK Library

QuickGame 鸿蒙(HarmonyOS)HAR SDK,提供账号登录、支付、数据统计 等能力。

## 快速开始

### 1) 安装依赖

按你的接入方式二选一。

#### 方式 A:从仓库安装

```bash
ohpm install gamesdklibrary
```

#### 方式 B:使用本地 HAR

在 `oh-package.json5` 中配置:

```json
"dependencies": {
  "gamesdklibrary": "file:./libs/gamesdkLibrary.har"
}
```

然后执行:

```bash
ohpm install
```

### 2) 导入核心 API

```ts
import {
  GameSDKManager,
  GameSDKOrderInfo,
  NotificationCenter,
  GAMESDK_NOTIFICATION_KEY_INIT_SUCCESS,
  GAMESDK_NOTIFICATION_KEY_LOGIN_SUCCESS,
  GAMESDK_NOTIFICATION_KEY_PAY_SUCCESS,
  GAMESDK_NOTIFICATION_KEY_PAY_FAIL
} from 'gamesdklibrary'
```

### 3) 最小接入流程

```ts
const productCode = '你的ProductCode'
const sdk = GameSDKManager.getInstance(productCode)

// 初始化
sdk.initWithProductCode(productCode)

// 登录(需传 UIContext)
// sdk.login(this.getUIContext())

// 支付
// const orderInfo = new GameSDKOrderInfo()
// ...填充业务订单参数
// sdk.payWithOrderInfo(orderInfo)
```

### 4) 注册回调(建议)

```ts
NotificationCenter.getInstance().addObserver(
  GAMESDK_NOTIFICATION_KEY_INIT_SUCCESS,
  (_name, data) => {
    console.info(`SDK init success: ${JSON.stringify(data)}`)
  }
)
```

## 运行配置

默认配置文件:`src/main/resources/rawfile/sdk_config.json`

当前支持的关键项:

- `mainurl`:SDK 主接口地址(`default` 使用内置默认地址)
- `enableNumberAuthLogin`:是否开启阿里云号码认证(`0/1`)
- `enableNumberAuthLoginFirst`:是否优先拉起一键登录(`0/1`)
- `numberAuthSdkInfo`:阿里云号码认证密钥串

## 可选能力说明

- 阿里云号码认证为可选能力;未配置 `numberAuthSdkInfo` 时不会生效。
- 抖音、巨量能力由构建脚本按客户配置注入,默认发布可不包含。

## 常见问题

- HAR 替换后不生效:确认 `version` 已变更,并执行 `ohpm install`。
- 本地依赖路径错误:检查 `file:` 路径是否相对当前 `oh-package.json5`。
- 初始化失败:先检查 `productCode` 与 `mainurl` 是否匹配目标环境。

## 导出能力

SDK 对外入口见 `Index.ets`,核心导出包括:

- `GameSDKManager`
- `GameSDKOrderInfo`
- `NotificationCenter`
- 登录/支付/初始化等通知常量(`GAMESDK_NOTIFICATION_KEY_*`)

## 版本与许可

- 当前版本见 `oh-package.json5` 的 `version` 字段
- 变更记录见 [CHANGELOG.md](./CHANGELOG.md)
- 许可协议见 [LICENSE](./LICENSE)(Apache-2.0)
