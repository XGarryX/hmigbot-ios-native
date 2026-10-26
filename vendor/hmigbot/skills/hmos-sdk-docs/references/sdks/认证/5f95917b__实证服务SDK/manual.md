# 实证服务HarmonyOS SDK接入指南(上架)

# 1.简介

本文档介绍了鸿蒙系统ArkTS应用接入实证服务SDK:

-
 SDK的配置使用了鸿蒙系统的共享包HAR,内部由ts及.so文件组成

-
IDE:HUAWEI DevEco Studio

-
语言:ArkTs语言

-
SDK产物:HAR

# 2.实证服务HarmonyOS SDK 基本信息

| 基础版本 | 类型 | sdk大小 | 运行后增长 |  |
|---|---|---|---|---|
| IDOCR.PubSdk.I.HMOS.Std.IT.NFC.Test. 1.0.0 | .har | 532KB | 暂无 |  |

测试账号信息:

Appid:TESTID20240918160203

Ip:es-test.eidlink.com

Port:9699

envCode:26814

nfc位置端口:1444

# 3.版本记录

| 更新内容 | 版本 | 编写时间 |
|---|---|---|
| har更改为releaseApi | V1.1.2 | 2024/09/18 |
| 二代证+旅行证件Test版本 | V1.1.1 | 2024/06/20 |

# 4.集成HarmonyOS SDK

## 4.1 工程配置

## 4.1.1创建项目

### 4.1.1.1 IDE下载及参数版本:

官网:https://developer.harmonyos.com/cn/develop/deveco-studio#download

相关配置:

SDK版本:API 12 及以上

### 4.1.1.2 创建项目:

1.create Project

2.选择不同类型的ablity,这里先选择empty ablity

##  4.1.2配置module.json5

1.打开 project/entry/src/main/module.json5文件

2.在module.json5中配置 skills、requestPermissions关键字

代码:

```
{
"module": {
"abilities": [
            {
"skills": [
                    {
"actions": [
"ohos.nfc.tag.action.TAG_FOUND"
                        ],
```

/* 此配置用于在系统侧贴卡跳转或选择 app中的贴卡ablity,若

只用于app内部贴卡,可以不用添加

```
                        "uris": [ // 卡片类型
                            {
                                "type":"tag-tech/NfcB"
                            },
                            {
                                "type":"tag-tech/IsoDep"
                            }
                        ]
                        */
                    }
                ]
            }
        ],
"requestPermissions": [
            {
"name": "ohos.permission.NFC_TAG",
"reason": "tag",
            }
        ]
    }
}
```

3.配置网络权限

代码:

```
"requestPermissions": [
      {
"name": "ohos.permission.GET_NETWORK_INFO"
      },{
"name": "ohos.permission.SET_NETWORK_INFO"
      },{
"name": "ohos.permission.INTERNET"
      }
    ],
```

## 4.1.3 配置字节码

1.在工程级build-profile.json5中设置useNormalizedOHMUrl为true(DevEco -Studio beta2版本及以

上)

```
//指定为HarmonyOS/OpenHarmony
"buildOption": {
"strictMode": {
"useNormalizedOHMUrl": true
  }
}
```

## 4.1.4 添加HAR包

在项目终端运行:

```
1
```

方式一:在Terminal窗口中,执行如下命令进行安装,并会在oh-package.json5中自动添加依赖。

```
ohpm install ../folder
```

方式二:在工程的oh-package.json5中设置三方包依赖,配置示例如下:

```
"dependencies": {
"folder": "file:../harName.har"
}
```

依赖设置完成后,需要执行ohpm install命令安装依赖包,依赖包会存储在工程的oh_modules目录

下。

```
9
ohpm install
```

## 4.1.5 页面配置NFC

```
// 1.导入NFC
import tag from '@ohos.nfc.tag';
// 2.配置变量和nfc回调
5
//身份证
let discTech: number[] = [tag.ISO_DEP, tag.NFC_B];
//旅行证件
let discTech: number[] = [tag.ISO_DEP, tag.NFC_B, tag.NFC_A];
let elementName: bundleManager.ElementName;
// 3.注册nfc回调
onForeground() {
try {
    tag.registerForegroundDispatch(elementName, discTech, (err: BusinessError,
tagInfo: tag.TagInfo) => {
try {
ParamsUtils.startTime = systemDateTime.getTime(false);
ReadCardManager.eid.readIDCard(1, tagInfo, {
onSuccess(data: string) {
          },
onFailed(code: number, msg: string, biz_id: string) {
          }
        },
        );
      } catch (e) {
      }
    });
  } catch (e) {
  }
}
// 5.取消注册监听
onBackground() {
console.log("onBackground");
try {
    tag.unregisterForegroundDispatch(elementName);
  } catch (e) {
  }
}
```

完整代码见demo-EntryAblity.ts

## 4.2 开始使用

## 4.2.1 SDK初始化(需向我司申请配置信息)

```
/**
 *
 * @param appid   我司分配的appid
 * @param rdData  是否反信息
* @param ip    ip
* @param port   port
* @param envCode   环境码
```

 * @param listener,初始化成功/失败的回调(如果传null,则不回调)

```
 */
letparams = new EidLinkInitParams(appId, Ip, port, envCode);
letlistener = {
onSuccess: () => {
  },
onFailed: (code: number) => {
  }
}
leteid = EidLinkSEFactory.getEidLinkSE(new EidLinkInitParams(appId, Ip, port,
envCode), listener)
```

## 4.2.2 身份证读卡方法

```
1
```

/** 二代证/电子证照读卡暂只支持二代证

```
 * @param type      卡片类型目前仅支持二代证 1
 * @param tagInfo    nfc 标签
 * @param mResultListener 读取回调
 */
voidreadIDCard( type:number, tagInfo : tag.TagInfo,
mResultListener:OnGetResultListener);
```

OnGetResultListener:

```
/**
```

 * 读卡成功

```
 *
 * @param result
 */
voidonSuccess(result:EidLinkResult);
/**
```

 * 读卡失败

```
 *
 * @param code 错误码
 * @param msg  错误描述
 * @param msg  bizid
 */
voidonFailed( code:number,  msg:string, bizid:string);
16
```

## 4.2.3 旅行证件读卡方法

```
/**
```

*旅行证件

```
 * @param tagInfo  NFC标签
 * @param idnum    护照号码
 * @param birthday 出生日期
* @param validity 护照有效期
* @param mResultListener 读取回调
 */
readTravel(tagInfo: tag.TagInfo,
idnum: string,
birthday: string,
validity: string,
listener: OnGetResultListener): void;
```

OnGetResultListener:

```
/**
```

 * 读卡成功

```
 *
 * @param result
 */
voidonSuccess(result:EidLinkResult);
/**
```

 * 读卡失败

```
 *
 * @param code 错误码
 * @param msg  错误描述
 * @param msg  bizid
 */
voidonFailed( code:number,  msg:string, bizid:string);
```

## 4. SDK方法说明

1.获取SDK版本号

```
/**
 *  获取SDK版本号
 */
varversion = EidLinkSESDK.getSDKVersion();
```

2.Eid对象方法说明:

```
/**
```

 *  设置SDK是否反信息

```
@param callData true反信息 false不反信息;默认不反信息
 */
setGetDataFromSdk(callData:boolean)
/**
```

 * 设置二代证/电子证照是否读取图片

```
@param needPic true读照片 false不读照片;默认读照片
 */
setReadPicture(needPic:boolean)
/**
```

 * 设置reqid返回长度

```
@param 0 返回40位reqid  1 返回 88位reqid
 */
setReqidType(versionType: number)
/**
```

 * 设置自定义sn,设备标识长度最大64且输入内容为可见ASCII字符

```
@param 0 返回40位reqid  1 返回 88位reqid
 */
setCustomSnValue(deviceId: string)
/**
```

 *  获取时延

```
 *  @param times 重复次数范围1~5
 *  @param listener 获取时延结果回调
 */
getTimeDelay(times : number,listener : GetTimeDelayListener) : void;
/**
```

 *  获取设备NFC位置

```
 *  @param placePort 我司提供获取nfc位置端口
 *  @param listener 获取位置结果回调
 *  PS:
```

 *  1.应用id、环境识别码、ip可与读卡参数一致

```
37
```

 *  2.获取设置NFC端口与读卡端口不一致

```
38
 */
getDeviceNFCPlace(placePort:string,listener : GetDeviceNFCPlaceListener) :
void;
/**
```

 * 读卡过程中关闭当前读卡

```
 */
stopReadingCard()
```

# 5.错误码说明

| 结果码 | 含义说明 | 可能问题及解决方法(中文描述) |
|---|---|---|
| 0 | 成功 |  |
| -1 | 移动卡片 | 将证件对准NFC区域重新读取 |
| -93003 | 未寻到卡片 | 将证件对准NFC区域重新读取,多次报错请联系客服 |
| -13003 | 获取到的客户ID无效 | 填写正确的APPID |
| -13009 | 初始化参数错误 | 填写正确读卡参数 |
| -13014 | SN无效 | 填写正确SN |
| -20001 | 网络连接异常 | 请确保网络连接正常,重新读卡 |
| -22003 | 数据传输错误 | 请确保网络连接正常,重新读卡 |
| -45001 | 环境识别码配置错误 | 请检查环境识别码是否正确 |
| -53002 | NFC会话出现异常 | 重新NFC读卡 |
| -91005 | 认证超时 | 请确保网络环境良好,可尝试切换网络或移动位置调整网络情况,重新 读卡 |
| -93001 | 读取卡片芯片数据失败 | 读取超时,读取时请勿移动卡片 |
| -93002 | 使用不支持的卡片读卡 | 使用正确的卡片读卡 |
| -93008 | 设备不支持NFC | 此设备不支持当前功能,请咨询客服 |
| -93009 | 设备NFC未打开 | 请打开设备NFC |
| -93010 | NFC关闭 | 请重试 |

-99001

系统版本不支持读卡

升级系统版本

| -99008 | 服务未开通 | 请联系客服 |
|---|---|---|
| -99009 | 设备未授权或已过期 | 请联系客服 |
| -99011 | 读卡返信息未启用 | 请联系客服 |
| -99012 | eid读取错误 | 将证件对准NFC区域重新读取,多次报错请联系客服 |
| -99098 | 等待用户操作超时 | 在指定时间内无贴卡操作 |
| -99099 | 用户取消操作 | 用户主动点击NFC界面取消按钮 |
