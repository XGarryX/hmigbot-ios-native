> 来源: ohpm 中央仓 README(T1 信源) | 包: `sdsescommoninterface` | ohpm 最新版: 1.0.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# sdsescommoninterface HAR 包安装与使用教程

## 简介

本SDK面向神思SS628、SS728M全系列终端,提供统一的多通信方式、多卡片类型、生物识别的二次开发接口,帮助开发者快速将身份证、IC卡、磁条卡及生物识别等功能集成到业务系统中。

## entry-default-signed.hap安装

进入entry-default-signed.har所在目录,执行命令:

```

hdc install entry-default-signed.hap

```

文档参考:[安装命令install](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/bm-tool#安装命令install)

## Demo项目目录结构说明

```

SdsesCommonInterfaceDemo/

├── har/                                    # HAR 包存放目录

│   ├── sdsescommoninterface.har     # 通用接口 HAR 包(标准版)

│   

├── entry/                                  # 主模块

│   ├── src/main/

│   │   ├── ets/

│   │   │   ├── components/                # 组件目录

│   │   │   │   ├── ConnectDeviceComp.ets  # 设备连接组件

│   │   │   │   ├── SdsesSoTestComp.ets    # 测试组件(演示用法)

│   │   │   │   └── infoRow.ets            # 信息行组件

│   │   │   ├── entryability/              # Ability 入口

│   │   │   │   └── EntryAbility.ets

│   │   │   ├── entrybackupability/        # 备份能力

│   │   │   │   └── EntryBackupAbility.ets

│   │   │   ├── model/                     # 数据模型

│   │   │   │   └── LogModel.ets           # 日志管理模型

│   │   │   ├── pages/                     # 页面目录

│   │   │   │   ├── Index.ets              # 首页

│   │   │   │   ├── MainPage.ets           # 主界面

│   │   │   │   ├── IdCardPage.ets         # 身份证页面

│   │   │   │   ├── BankPage.ets           # 银行卡页面

│   │   │   │   ├── SocialSecurityPage.ets # 社保卡页面

│   │   │   │   ├── M1Page.ets             # M1卡页面

│   │   │   │   ├── MagneticPage.ets       # 磁条卡页面

│   │   │   │   ├── CpuPage.ets            # CPU卡页面

│   │   │   │   ├── QrCodePage.ets         # 二维码页面

│   │   │   │   ├── InternalTestingPage.ets# 内部测试页面

│   │   │   │   └── SdsesSoTestPage.ets    # SO测试页面

│   │   │   └── utils/                     # 工具类

│   │   │       └── utils.ets              # 数据类型转换工具

│   │   ├── resources/                     # 资源文件

│   │   └── module.json5                   # 模块配置文件(含权限声明)

│   └── oh-package.json5                   # 模块依赖配置

├── oh_modules/                            # 依赖包目录(自动安装)

│   └── .ohpm/

│       └── sdsescommoninterface@.../      # 已安装的 sdsescommoninterface 包

├── oh-package.json5                       # 项目级依赖配置

└── build-profile.json5                    # 构建配置

```

### 核心文件说明

| 文件路径 | 说明 |

|---------|------|

| `har/sdsescommoninterface.har` | HAR 包源文件 |

| `entry/oh-package.json5` | 声明 HAR 包依赖 |

| `entry/src/main/module.json5` | 权限配置文件 |

| `entry/src/main/ets/components/ConnectDeviceComp.ets` | 设备连接示例 |

| `entry/src/main/ets/components/SdsesSoTestComp.ets` | 完整功能测试示例 |

| `entry/src/main/ets/utils/utils.ets` | 数据转换工具类 |

| `entry/src/main/ets/model/LogModel.ets` | 日志管理模型 |

---

## HAR 包安装

### 步骤 1:放置 HAR 包

将 `sdsescommoninterface.har` 文件放置在项目的 `har/` 目录下:

```

SdsesCommonInterfaceDemo/

└── har/

    ├── sdsescommoninterface.har           # 标准版(通用设备)

```

### 步骤 2:配置依赖

在 `entry/oh-package.json5` 文件中添加依赖声明:

```json5

{

  "name": "entry",

  "version": "1.0.0",

  "description": "Please describe the basic information.",

  "main": "",

  "author": "",

  "license": "",

  "dependencies": {

    "sdsescommoninterface": "file:../har/sdsescommoninterface.har"

  }

}

```

**关键点:**

- 使用 `"file:../har/sdsescommoninterface.har"` 指定本地 HAR 包路径

- 包名为 `sdsescommoninterface`(必须是sdsescommoninterface,不可自定义)

- 根据设备型号选择对应的HAR包:

    - 标准设备使用 `sdsescommoninterface.har`

### 步骤 3:安装依赖

在项目根目录执行以下命令:sdsescommoninterface.har

```bash

ohpm install sdsescommoninterface

```

### 步骤 4:验证安装

安装成功后,会在以下位置生成包文件:

```

oh_modules/.ohpm/sdsescommoninterface@<版本哈希>/

└── oh_modules/

    ├── sdsescommoninterface/     # 主包

    │   ├── Index.d.ets           # 类型定义入口

    │   ├── ets/                  # 编译后的字节码

    │   ├── libs/                 # 库文件

    │   └── src/main/ets/sdses/   # 源码(调试用)

    └── libCommonInterface.so/    # Native SO 库

```

---

## 蓝牙权限配置(使用蓝牙必须配置)

在 `entry/src/main/module.json5` 中配置权限:

```json5

{

  "module": {

    "name": "entry",

    "type": "entry",

    // ... 其他配置 ...

    "requestPermissions": [

      {

        "name": "ohos.permission.ACCESS_BLUETOOTH",

        "reason": "$string:approximately_bluetooth_permission_reason",

        "usedScene": {

          "abilities": ["EntryAbility"],

          "when": "inuse"

        }

      }

    ]

  }

}

```

#### 权限说明字符串

在 `entry/src/main/resources/base/element/string.json` 中添加权限说明:

```json

{

  "string": [

    {

      "name": "approximately_bluetooth_permission_reason",

      "value": "用于蓝牙连接的权限"

    }

  ]

}

```

## 使用示例

import { GetUsbPermission, OpenDevice, IdReadCard, CloseDevice} from 'sdsescommoninterface';

1. 连接设备(USB或蓝牙通信方式)

```

  const CONNECT_TYPES: ConnectType[] = [

    {

      name: 'USB',

      portType: 'USB',

      portPara: '261A0011',//VID PID

      extendPara: '',

      portTypeLabel: 'USB',

      portParaLabel: 'VID_PID',

      extendParaLabel: '传输方式',

      portTypeEnable: true,

      portParaEnable: true,

      extendParaEnable: true

    },

    {

      name: '蓝牙 (BTH)',

      portType: 'BTH',

      portPara: 'SS',

      extendPara: '',

      portTypeLabel: 'BTH',

      portParaLabel: '蓝牙名称',

      extendParaLabel: '无',

      portTypeEnable: false,

      portParaEnable: true,

      extendParaEnable: false

    }

  ];

  @Local portType: string = CONNECT_TYPES[0].portType;

  @Local portPara: string = CONNECT_TYPES[0].portPara;

  @Local extendPara: string = CONNECT_TYPES[0].extendPara;

    try {

      const type = this.getCurrentType();

      let handle: number = -1;

      if (type.portType.toUpperCase() === 'USB') {

        const vid = parseInt(this.portPara.substring(0, 4), 16);

        const pid = parseInt(this.portPara.substring(4, 8), 16);

        this.logManager.info('GetUsbPermission', `请求USB权限,VID=0x${vid.toString(16).toUpperCase()}, PID=0x${pid.toString(16).toUpperCase()}`);

        const permStatus = await GetUsbPermission(vid, pid);

        if (permStatus !== 0) {

          this.message = `获取USB权限失败或未插入设备,错误代码:${permStatus}`;

          this.logManager.error('GetUsbPermission', `获取USB权限失败,错误代码:${permStatus}`);

          this.isConnecting = false;

          return;

        }

        this.logManager.success('GetUsbPermission', '获取USB权限成功');

        this.logManager.info('OpenDevice', `打开USB设备,PortType=${this.portType}, PortPara=${this.portPara}`);

        handle = await OpenDevice(this.portType, this.portPara, this.extendPara);

      } else {

        this.logManager.info('OpenDevice', `打开设备,PortType=${this.portType}, PortPara=${this.portPara}, ExtendPara=${this.extendPara}`);

        handle = await OpenDevice(this.portType, this.portPara, this.extendPara);

      }

      if (handle < 0) {

        this.message = `连接设备失败,错误代码:${handle}`;

        this.logManager.error('OpenDevice', `连接设备失败,错误代码:${handle}`);

      } else {

        this.message = `连接设备成功,设备句柄:${handle}`;

        this.logManager.success('OpenDevice', `连接设备成功,设备句柄:${handle}`);

        this.pageStack.replacePath({name:"MainPage"})

      }

    } catch (e) {

      this.message = `连接异常:${e}`;

      this.logManager.error('ConnectDevice', `连接异常:${e}`);

    } finally {

      this.isConnecting = false;

    }

```

2. 读身份证

```

    const IdCardInfo = new Uint8Array(40960)

    const CardType = this.isFingerprint ? 0x10 : 0x00

    const res = await IdReadCard(CardType, 3, IdCardInfo, 10)

    if (res !== 0) {

      this.message = `读卡失败,错误代码:${res}`

      this.logManager.error('IdReadCard', `失败,错误代码:${res}`)

      return

    }

    this.logManager.success('IdReadCard', '读卡成功')

    const info = uint8ArrayToString(IdCardInfo).replace(/\0/g, '').trimEnd()

    console.info('IdCardPage IdCardInfo: ' + info)

    const parts = info.split(':')

    console.info('IdCardPage parts length: ' + parts.length)

```

3. 关闭设备

```

    const res = await CloseDevice()

    if (res !== 0) {

      this.logManager.error('CloseDevice', `关闭设备失败,错误代码:${res}`)

    } else {

      this.logManager.success('CloseDevice', '关闭设备成功,返回初始界面')

    }

```

## 约束与限制

在下述版本验证通过:

- DevEco Studio 版本: 6.0.0 Release(6.0.0.878)

- 在 API18+ 支持。

**文档版本:** 1.0.0  

**更新日期:** 2026-07-15 

**适用 SDK 版本:** API 18+
