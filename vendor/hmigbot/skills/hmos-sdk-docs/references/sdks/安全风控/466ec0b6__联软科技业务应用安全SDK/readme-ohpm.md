> 来源: ohpm 中央仓 README(T1 信源) | 包: `@emmsdk/emmthirdsdk` | ohpm 最新版: 5.14.20260618 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# EMMThirdSDK

## 简介

`EMMThirdSDK` 联软科技业务应用安全SDK(三方SDK),面向 OpenHarmony 应用提供与 EMM 门户联动的基础接入能力。  

SDK 适用于三方业务应用接入 EMM 门户后的初始化、网关认证、安全隧道建立等场景。

当前版本建议重点使用以下核心能力:

- SDK 初始化

- 网关认证与安全隧道初始化

## 环境要求

- OpenHarmony 5.0.0(API 12)及以上

- DevEco Studio 5.0.0 及以上

- `ohpm` 作为依赖管理工具

## 安装教程

### 方式一:通过 ohpm 中心仓安装

```bash

ohpm install @emmsdk/emmthirdsdk

```

或在应用模块的 `oh-package.json5` 中添加依赖:

```json5

{

  "dependencies": {

    "@emmsdk/emmthirdsdk": "5.14.20260618"

  }

}

```

### 方式二:本地 HAR 集成

如果当前项目以本地包方式集成,也可以将 `EMMThirdSDK.har` 引入到业务工程,并在 `oh-package.json5` 中配置本地依赖:

```json5

{

  "dependencies": {

    "@emmsdk/emmthirdsdk": "file:../libs/EMMThirdSDK.har"

  }

}

```

## 使用说明

### 1. 导入 SDK

```ts

import { EMMToolsUtil } from '@emmsdk/emmthirdsdk';

```

### 2. 初始化 SDK

建议在应用启动阶段完成初始化,例如在 `AbilityStage` 或应用启动入口中执行:

```ts

import { AbilityStage } from '@kit.AbilityKit';

import { EMMToolsUtil } from '@emmsdk/emmthirdsdk';

export default class EntryAbilityStage extends AbilityStage {

  onCreate(): void {

    EMMToolsUtil.init(this.context, 'com.leagsoft.emm.xxx', {

      isDebug: true,

      callback: {

        receiverEventState: (eventType: string, eventMsg: string) => {

          console.info(`EMM event: ${eventType}, msg: ${eventMsg}`);

        }

      }

    });

  }

}

```

参数说明:

- `context`:应用上下文

- `bundleName`:EMM 门户应用包名

- `config.isDebug`:是否开启调试日志,生产环境建议关闭

- `config.callback`:可选事件回调,用于接收 EMM 状态事件

### 3. 网关认证

初始化完成后,可调用 `initTunnel()` 发起网关认证并建立安全隧道:

```ts

import { EMMToolsUtil } from '@emmsdk/emmthirdsdk';

async function authGateway(): Promise<void> {

  try {

    await EMMToolsUtil.initTunnel();

    console.info('网关认证成功,安全隧道已初始化');

  } catch (err) {

    console.error(`网关认证失败: ${JSON.stringify(err)}`);

  }

}

```

## 公开接口

`EMMThirdSDK` 的对外接口通过 [EMMToolsUtil.ets](H:\workcode_hm\uniEMM_sdk\EMMSDK5.0_devgithub\EMMSDK5.0\sdk\EMMThirdSDK\src\main\ets\com\leagsoft\emm\thirdsdk\EMMToolsUtil.ets) 暴露。

本文档仅说明核心初始化与网关认证接口。

### `init(context: Context, bundleName: string, config?: EMMInitConfig): void`

用于初始化三方 SDK 运行环境,并设置 EMM 门户包名。

参数说明:

- `context`:应用上下文

- `bundleName`:EMM 门户应用包名

- `config.isDebug`:是否开启调试日志

- `config.callback`:三方 SDK 状态回调

### `initTunnel(): Promise<void>`

用于执行网关认证并初始化安全隧道。

说明:

- 该接口内部会调用网关认证流程,认证成功后即可使用隧道相关能力。

- 建议在 SDK 初始化完成后调用。

- 如接入流程依赖 EMM 门户传递的认证信息,请确保宿主应用已完成与 EMM 门户的拉起和参数同步。

## 回调说明

如果在初始化时传入 `callback`,可接收以下事件状态:

- `emmlogout`:EMM 注销

- `clearemmdata`:EMM 清除沙箱数据

- `formemm`:是否从 EMM 门户启动打开,`eventMsg` 为 `true` 或 `false`

- `sandboxinit`:EMM 沙箱初始化结果,`eventMsg` 为 `success` 或 `failed`

## 权限说明

SDK 依赖企业移动管理相关能力,宿主应用应根据实际业务场景声明并授予相关权限。  

结合当前实现,常用权限包括但不限于:

- `ohos.permission.INTERNET`

- `ohos.permission.GET_NETWORK_INFO`

- `ohos.permission.STORE_PERSISTENT_DATA`

- `ohos.permission.GET_WIFI_INFO`

如接入安全相机、水印、文件容器等扩展能力,还需要根据实际功能补充对应权限。

## 约束与注意事项

- `bundleName` 必须填写正确的 EMM 门户应用包名。

- 建议先调用 `init()`,再调用 `initTunnel()`。

- `isDebug` 仅建议在调试阶段开启,正式发布建议关闭。

- 网关认证依赖 EMM 门户侧传递的用户态与会话信息,接入时请确保门户联动流程完整。

## License

本项目采用商业授权方式发布,详见当前目录下的 [LICENSE](./LICENSE) 文件。
