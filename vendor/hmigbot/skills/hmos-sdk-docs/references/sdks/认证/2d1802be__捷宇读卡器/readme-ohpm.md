> 来源: ohpm 中央仓 README(T1 信源) | 包: `@joyusing/idcard` | ohpm 最新版: 1.0.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 捷宇读卡器接口

## 1.接口简要说明

### 初始化、打开设备

`export const Init:(devid: number) => number;`

### 查卡

`export const IdCardSearch:()=>number;`

### 找卡

`export const IdCardSelect:()=>number;`

## 读卡,返回身份证信息json

`export const FetchCardInfo:()=>string;`

### 关闭

`export const IdentityCardClose:()=>number;`

## 2.返回的身份证信息字段

| 参数名称          | 类型     | 必填 | 描述                       |

|:--------------|:-------|:---|:-------------------------|

| `name`        | String | 是  | 名字                       |

| `sex`         | String | 是  | 性别                       |

| `nation`      | String | 是  | 民族                       |

| `birthday`    | String | 是  | 出生日期	                    |

| `address`     | String | 是  | 地址	                      |

| `cardNo`      | String | 否  | 身份证号                     |

| `department`  | String | 是  | 签发机关                     |

| `beginday`    | String | 是  | 起始日期                     |

| `endday`      | String | 是  | 截止日期                     |

| `photobase64` | String | 是  | 照片base64	                |

| `cardType`    | String | 是  | 类型,居民身份证/港澳台居住证/外国人永久居住证 |

| `passNum`     | String | 否  | 通行证号码	港澳台                |

| `issuances`   | String | 否  | 签证次数	港澳台                 |

| `enName`      | String | 否  | 英文名	外国人永久居住证             |

| `countryCode` | String | 否  | 国家代码,新版永居证	              |

| `oldCardNo`   | String | 否  | 既往证件号,新版永居证	             |

| `enName2`     | String | 否  | 英文名备用,新版永居证	             |

| `numCert`     | String | 否  | 证件类型,新版永居证	              |

## 3.所需权限

开发基于USB DDK,故接口应在DriverExtensionAbility生命周期内使用,所需匹配权限

### 3.1 所需匹配权限

```

ohos.permission.ACCESS_DDK_USB  用于读卡功能

```

### 3.2.设备vid/pid

#### 3.2.1 vid

`0x2b19,0x0400,0103`

#### 3.2.2 pid

`0x0200,0xc35a,6066`

## 4.接口调用例子

```

       //库连接测试

        let msg = idCardT.SayHello('Hello');

        console.log(`捷宇身份证,SayHello:${msg}`);

        //初始化

        idCardT.Init(dev);

        //寻卡

        let search = idCardT.IdCardSearch();

        //找卡

        let select = idCardT.IdCardSelect();

        //读卡

        let fetch  = idCardT.FetchCardInfo();

        //关闭

        let close  = idCardT.IdentityCardClose();

```

# 集成方式

### 1.1 安装(OHPM)

从 **OHPM 三方库中心仓** 安装本包(在项目根目录或目标模块目录执行均可,以实际工程与 OHPM 文档为准):

```bash

ohpm install @joyusing/idcard

```

简写:

```bash

ohpm i @joyusing/idcard

```

安装完成后,宿主模块的 `oh-package.json5` 中会出现对应依赖;再在工程内执行 `ohpm install` 拉取依赖树。

### 1.2 本地依赖(源码 / 工程内路径)

在宿主模块的 `oh-package.json5` 中增加本地路径依赖(例子:与引用模块内 `entry` 一致时可使用 `file:`):

```json5

{

  "dependencies": {

    "@joyusing/idcard": "file:../doccamerasdk"

  }

}

```
