> 来源: ohpm 中央仓 README(T1 信源) | 包: `@eyeofcloud/abtesting` | ohpm 最新版: 2.0.2 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# Eyeofcloud Harmony SDK

Harmony SDK使用说明

## 安装

通过 ohpm 安装本 SDK:

```

ohpm i @eyeofcloud/abtesting

```

## 快速开始

在你的 ArkTS/ETS 文件中导入并初始化 SDK:

```

import {

  Client,

  createInstance,

  EventTags,

  UserAttributes,

  setDatafileUrlTemplate,

  setEventUrl

} from "@eyeofcloud/abtesting"

//初始化 SDK

const eyeofcloudClient = createInstance({sdkKey: "Your_SDKKey"})

//调用AB实验接口进行分桶

this.eyeofcloudClient?.onReady().then(() => {

  let attributes: UserAttributes = {city: "南京"};

  let user = this.eyeofcloudClient?.createUserContext("3", attributes)

  try {

    let decision = user?.decide("Your_flagKey")

    let tags: EventTags = {name: "event"}

    user?.trackEvent("buy", tags)

  }catch (e) {

    console.log(e)

  }

})

```

## 权限配置

使用时添加http权限

在modules.json5文件中添加如下配置:

```

"requestPermissions": [

  {

    "name": "ohos.permission.INTERNET",

    "usedScene": {

      "when": "always"

    }

  }

]

```

## 说明

目前本SDK对外开放的接口或类型如下:

|方法或类型| 说明                            |

|--|-------------------------------|

|createInstance| 创建eyeofcloud实例的方法,参数一般填sdkKey |

|setDatafileUrlTemplate| 设置eyeofcloud实例获取数据文件的方法       |

|setEventUrl| 设置事件接收地址的方法                   |

|Client| eyeofcloud实例的类型               |

|UserAttributes| 用户属性的类型                       |

|EventTags| 储存事件                          |

## 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](https://www.apache.org/licenses/LICENSE-2.0.txt?spm=a2ty_o01.29997173.0.0.230a5171BhlYnu&file=LICENSE-2.0.txt) 文件。

## 支持

如有问题,请联系zhangweixue@heliyuntong.cn
