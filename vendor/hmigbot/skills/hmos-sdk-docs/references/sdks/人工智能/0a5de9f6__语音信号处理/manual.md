## 语音信号处理SDK介绍 

语音信号处理是搭载降噪、回声消除(AEC)核心功能,优化嘈杂环境下的语音信号质量,为后续 语音识别、通话等模块筑牢清晰信号基础。 

#### SDK包名 : @unisound/ssp 

#### SDK版本号 : 1.0.1 

#### 约束与限制 

在下述版本通过验证: 

|DevEco Studio版 本号|HarmonyOS SDK版本号|手机操作系统ROM版本号|
|---|---|---|
|DevEco Studio|【API11】HarmonyOS SDK|3.0.0.13(SP6DEVC00E13R6P1)|
|5.0.9.100|5.0.0(12)||
|DevEco Studio|【API23】HarmonyOS|6.1.0.117(SP6C00E115R4P9patch15)|
|6.0.2|SDK6.1.0.117(SP6)||

# 一 、SDK说明 

SDK基于HarmonyOS开发的信号处理SDK,搭载降噪、回声消除(AEC)核心功能,优化嘈杂环 境下的语音信号质量,为后续语音识别、通话等模块筑牢清晰信号基础 

示例demo 

SDK包 

# 二、SDK集成步骤 

## 1.调用流程 

# 二、集成方法 

## 1.1 下载安装 

```
  ohpm i @unisound/ssp
```

## 1.2 将SDK的har包拷⻉到工程的libs目录下; 

工程结构图如下: 

#### 在oh-package.json5文件,关联加载声音克隆库 

```
"dependencies":
  {
    "@unisound/ssp": "file:libs/ssp.har"
  }
```

# 三、申请权限 

module.json5 文件添加录音权限 

```
 "requestPermissions": [
      {
        "name": "ohos.permission.MICROPHONE",
        "reason": "$string:EntryAbility_mic",
        "usedScene": {
          "abilities": [
            "FormAbility"
          ],
          "when": "always"
        }
      }
    ]
```

# 四、使用说明 

### 初始化SDK 

```
 sspManager = new SspManager();
```

### SspManager说明 

|属性|类型|必 填|说明||
|---|---|---|---|---|
|`cfg_path`|`string?`|是|配置文 数、算|件路径(JSON格式),描述采样率、通道 法参数等。|
|`model4_path`|`string?`|是|降噪/波|束模型文件路径(二进制格式)。|
|`uniActivate` UniActivate说|`UniActivate?` 明|是|授权激|活对象(若引擎启用授权校验)。|
|属性|类型||必填|说明|
|`app_key`|`string`||是|应用appkey(需要申请)|
|`app_secret`|`string`||是|应用secret(需要申请)|

一 设备唯 标识 

是 

```
unique_idstring
```

### ssp处理回调事件 

```
OnSspEngineCallBack {
    onSspError: (code: number, error: string) => void;
    onSspStart: () => void;
    onSspEnd: () => void;
}
```

# SDK接口说明 

## SspManager 

开始ssp处理 

start() 

|-|-|
|---|---|
|说明|ssp引擎初始化|
|版本支持|最低1.0.0|

process(mic: ArrayBuffer, echo_ref: ArrayBuffer, out_asr: ArrayBuffer, out_vad: ArrayBuffer, out_len: ArrayBuffer) 

|-|-|
|---|---|
|说明|音频数据处理|
|版本支持|最低1.0.0|
|mic|录音数据|
|echo_ref|回采数据|
|out_asr|处理后用于识别数据|
|out_vad|处理后用于vad检测数据|
|out_len|处理后用音频数据长度|

#### stop() 

|-|-|
|---|---|
|说明|结束音频处理|
|版本支持|最低1.0.0|

#### release() 

|-|-|
|---|---|
|说明|释放引擎|
|版本支持|最低1.0.0|

#### addCallback(callback: OnSspEngineCallBack) 

|-|-|
|---|---|
|说明|设置ssp处理回调事件|
|版本支持|最低1.0.0|
|callback|ssp处理回调|
