> 来源: ohpm 中央仓 README(T1 信源) | 包: `@emmsdk/emmopensdk` | ohpm 最新版: 5.14.20260618 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# EMMOpenSDK

## 简介

`EMMOpenSDK` 联软科技零信任网络访问安全SDK(门户SDK),面向 OpenHarmony 应用提供企业移动管理能力接入。  

SDK 基于 HarmonyOS NEXT / OpenHarmony Stage 模型开发,适用于企业应用在 OpenHarmony 设备上的初始化接入、用户认证、会话管理与注销等场景。

当前版本重点提供以下核心能力:

- SDK 初始化

- 用户名密码认证

- 注销登录

## 环境要求

- OpenHarmony 5.0.0(API 12)及以上

- DevEco Studio 5.0.0 及以上

- `ohpm` 作为依赖管理工具

## 安装教程

### 方式一:通过 ohpm 中心仓安装

```bash

ohpm install @emmsdk/emmopensdk

```

或在应用模块的 `oh-package.json5` 中添加依赖:

```json5

{

  "dependencies": {

    "@emmsdk/emmopensdk": "5.14.20260618"

  }

}

```

### 方式二:本地 HAR 集成

如果当前项目以本地包方式集成,也可以将 `EMMOpenSDK.har` 引入到业务工程,并在 `oh-package.json5` 中配置本地依赖:

```json5

{

  "dependencies": {

    "@emmsdk/emmopensdk": "file:../libs/EMMOpenSDK.har"

  }

}

```

## 使用说明

### 1. 导入 SDK

```ts

import { EMMToolsUtil, EMMConfigBean } from '@emmsdk/emmopensdk';

```

### 2. 初始化 SDK

建议在应用启动阶段完成初始化,例如在 `AbilityStage` 中执行:

```ts

import { AbilityStage } from '@kit.AbilityKit';

import { EMMToolsUtil, EMMConfigBean } from '@emmsdk/emmopensdk';

export default class EntryAbilityStage extends AbilityStage {

  onCreate(): void {

    let config: EMMConfigBean = new EMMConfigBean();

    config.serverhost = 'your-emm-server.example.com';

    config.tunnelhost = 'your-emm-server.example.com';

    config.apiport = '8888';

    config.tunnelport = '8890';

    config.mdmserviceport = '8889';

    EMMToolsUtil.initOpenSDK(this.context, {

      isDebug: true,

      configBean: config,

      iScenesType: 1

    });

  }

}

```

`iScenesType` 说明:

- `1`:每次都通过用户名密码认证

- `2`:首次用户名密码认证,后续二次认证刷新票据

- `3`:首次用户名密码认证后自动维护会话(当前暂不支持)

- `4`:首次用户名密码认证后再进行 PIN 码认证

### 3. 用户名密码认证

```ts

import { EMMToolsUtil } from '@emmsdk/emmopensdk';

async function login(): Promise<void> {

  try {

    const result = await EMMToolsUtil.authUserName({

      userid: 'test_user',

      securitycode: '123456'

    });

    console.info(`认证成功,返回参数数量:${result.size}`);

  } catch (err) {

    console.error(`认证失败: ${JSON.stringify(err)}`);

  }

}

```

认证成功后返回 `ThirdAppMap`,可用于获取服务端返回的三方扩展参数。

### 4. 注销登录

```ts

import { EMMToolsUtil } from '@emmsdk/emmopensdk';

async function logout(): Promise<void> {

  try {

    const result = await EMMToolsUtil.logout();

    console.info(`注销完成: status=${result.status}, msg=${result.msg}`);

  } catch (err) {

    console.error(`注销失败: ${JSON.stringify(err)}`);

  }

}

```

## 公开接口

以下接口均通过唯一出口文件 `sdk/EMMOpenSDK/src/main/ets/com/leagsoft/emm/opensdk/EMMToolsUtil.ets` 对外暴露。

### `initOpenSDK(context: Context, configBean: EMMInitConfig): void`

用于初始化 SDK 运行环境。

参数说明:

- `context`:应用上下文

- `configBean.isDebug`:是否开启调试日志,生产环境建议关闭

- `configBean.configBean`:EMM 服务端配置

- `configBean.iScenesType`:认证场景类型

### `authUserName(authParams: EMMAuthParams): Promise<ThirdAppMap>`

用于执行用户名密码认证。

参数说明:

- `userid`:用户名

- `securitycode`:密码

- `imagecode`:验证码,可选

- `externParams`:扩展业务参数,可选

### `logout(): Promise<BaseApiBean>`

用于注销当前登录用户,清理当前会话状态。

返回值说明:

- `status`:响应状态码

- `msg`:响应描述信息

- `rawData`:原始返回数据

## 权限说明

SDK 依赖企业移动管理能力,宿主应用应根据实际业务场景声明并授予相关权限。  

结合当前实现,常用权限包括但不限于:

- `ohos.permission.INTERNET`

- `ohos.permission.GET_NETWORK_INFO`

- `ohos.permission.STORE_PERSISTENT_DATA`

- `ohos.permission.GET_WIFI_INFO`

如开启安全相机、日志分享或其他增强能力,还需要根据实际功能额外配置对应权限。

## 约束与注意事项

- 初始化前请先准备正确的 EMM 服务端地址、端口与网关配置。

- `isDebug` 仅建议在调试阶段开启,正式发布建议关闭。

- 认证、注销等接口均为异步接口,建议统一做好异常捕获与状态提示。

## License

本项目采用商业授权方式发布,详见当前目录下的 [LICENSE](./LICENSE) 文件。
