> 来源: ohpm 中央仓 README(T1 信源) | 包: `libtunnelapi` | ohpm 最新版: 1.0.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# libtunnelapi

## 简介

libtunnelapi是三未信安综合安全网关配套的鸿蒙平台SDK。搭配其配套的综合安全网关可实现用户数据的国密传输,保障了用户数据在公共网络环境下的安全。使用三未信安综合安全网关和libtunnelapi可大大减少原有业务的国密改造成本。libtunnelapi使用HarmonyOS的vpnExtension扩展,需要使用真机调试。

## 配置

### 引入 libtunnelapi

1. 将libtunnelapi.har包文件放入项目适当的文件夹中,如libs或assets目录。

2. 在entry的oh-package.json5目录中增加如下配置

```

{

  "name": "entry",

  "version": "1.0.0",

  "description": "Please describe the basic information.",

  "main": "",

  "author": "",

  "license": "",

  "dependencies": {

    "libtunnelapi" : "file:../lib/libtunnelapi"

  }

}

```

3. 执行ohpm install,执行成功后会在目录中出现oh_modules。

### 权限设置

libtunnelapi需要网络权限,在在entry的module.json5文件中添加ohos.permission.INTERNET权限。

### 添加VpnExtAbility

复制demo中的MyVpnExtAbility.ets文件到合适目录下。并在module.json5文件中添加配置。

```c

"extensionAbilities": [

      {

        "name": "EntryBackupAbility",

        "srcEntry": "./ets/entrybackupability/EntryBackupAbility.ets",

        "type": "backup",

        "export ed": false,

        "metadata": [

          {

            "name": "ohos.extension.backup",

            "resource": "$profile:backup_config"

          }

        ],

      },

      {

        "name": "MyVpnExtAbility",

        "description": "vpnservice",

        "type": "vpn",

        "srcEntry": "./ets/serviceextability/MyVpnExtAbility.ets"

      }

    ]

```

module.json5 中添加的type类型需要写vpn,如果编译报错提示没有vpn类型,就在报错提示的enum中手动添加上vpn。

MyVpnExtAbility.ets文件中的blockedAppName 要改成项目实际的包名。

## 启动和停止VpnExtAbility

引入vpnExtension, 通过vpnExtension.startVpnExtensionAbility和vpnExtension.stopVpnExtensionAbility启动和停止VPN。Want对象如下所示,注意bundleName和abilityName按照实际情况填写。

```c

import {TunnelAPI} from "libtunnelapi"

import { common, Want } from "@kit.AbilityKit";

import { vpnExtension } from '@kit.NetworkKit';

let context = getContext(this) as common.VpnExtensionContext;

let want: Want = {

  deviceId: "",

  bundleName: "com.sansec.secgw.client",

  abilityName: "MyVpnExtAbility",

  parameters: {

    wgConfigParam: "this is wgConfigParam"

  }

};

@Entry

@Component

struct Index {

  @State message: string = 'Hello World';

  private context = getContext(this) as common.UIAbilityContext;

  build() {

    Column() {

      Button('Start Extension').onClick(() => {

        console.log("开启VPN")

        vpnExtension.startVpnExtensionAbility(want)

      }).width('70%').margin(6)

      Button('Stop Extension').onClick(() => {

        console.info("停止VPN")

        vpnExtension.stopVpnExtensionAbility(want)

      }).width('70%').margin(6)

    }

    .height('100%')

    .width('100%')

  }

}

```
