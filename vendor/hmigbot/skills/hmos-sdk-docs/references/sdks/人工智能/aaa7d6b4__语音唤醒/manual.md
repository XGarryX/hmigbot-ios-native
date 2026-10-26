# 语音唤醒SDK介绍 

语音唤醒SDK集成离线唤醒与命令词识别能力,为智能音箱、车载终端等设备打造精准、低功耗的 语音交互入口,无需联网即可响应唤醒与指令。 

SDK包名:@unisound/kws 

SDK版本号 : 1.0.0 

#### 约束与限制 

#### 在下述版本通过验证: 

|DevEco Studio版 本号|HarmonyOS SDK版本号|手机操作系统ROM版本号|
|---|---|---|
|DevEco Studio|【API11】HarmonyOS SDK|3.0.0.13(SP6DEVC00E13R6P1)|
|5.0.9.100|5.0.0(12)||
|DevEco Studio|【API23】HarmonyOS|6.1.0.117(SP6C00E115R4P9patch15)|
|6.0.2|SDK6.1.0.117(SP6)||

# 一 、SDK说明 

语音唤醒SDK集成离线唤醒与命令词识别能力,为智能音箱、车载终端等设备打造精准、低功耗的 语音交互入口,无需联网即可响应唤醒与指令。 

示例demo 

SDK包 

# 二、SDK集成 

## 1.1 下载安装 

```
  ohpm i @unisound/kws
```

## 1.2 将SDK的har包拷⻉到工程的libs目录下; 

#### 工程结构图如下: 

#### 在oh-package.json5文件,关联加载语音唤醒库 

```
"dependencies":
  {
    "@unisound/kws": "file:libs/kws.har"
  }
```

# 三、使用说明 

### 初始化SDK 

```
 kwsManager = new KwsManager();
```

### KwsManager说明 

|属性|类型|必填|说明|
|---|---|---|---|
|am_path|string?|是|声学模型文件路径(二进制格式)。|
|grammar_path|string?|是|语法模型文件路径(二进制格式)。|
|uniActivate|UniActivate?|是|授权激活对象(若引擎启用授权校验)。|

### UniActivate说明 

|属性|类型|必填|说明|
|---|---|---|---|
|app_key|string|是|应用appkey(需要申请)|

|app_secret|string|是|应用secret(需要申请)|
|---|---|---|---|
|unique_id|string|是|设备唯一标识|

### 语音唤醒回调事件 

```
OnKwsEngineCallBack {
    onKwsError: (code: number, error: string) => void;
    onKwsResult: (data: string) => void;
    onKwsStart: () => void;
    onKwsEnd: () => void;
}
```

# 四、申请权限 

module.json5 文件添加麦克风权限、读取媒体文件权限、网络权限 

```
  "requestPermissions": [
      {
        "name": "ohos.permission.MICROPHONE",
        "reason": "$string:EntryAbility_desc",
        "usedScene": {
          "abilities": [
            "FormAbility"
          ],
          "when": "always"
        }
      },
      {
        "name": "ohos.permission.INTERNET"
      },
      {
        "name": "ohos.permission.READ_MEDIA",
        "reason": "$string:EntryAbility_desc",
        "usedScene": {
          "abilities": [
            "FormAbility"
          ],
          "when": "always"
        }
      }
    ]
```

# 五、SDK接口说明 

## KwsManager 

开始语音唤醒 

start() 

|-|-|
|---|---|
|说明|唤醒引擎初始化|

版本支持 

最低1.0.0 

#### start(tag: string) 

|-|-|
|---|---|
|说明|唤醒引擎初始化|
|版本支持|最低1.0.0|
|tag|编译语法模型文件TAG标签|

#### process(buf: ArrayBuffer, bufSize: number) 

|-|-|
|---|---|
|说明|音频数据处理|
|版本支持|最低1.0.0|
|buf|录音数据|
|bufSize|录音数据大小|

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

addCallback(callback: OnKwsEngineCallBack) 

|-|-|
|---|---|
|说明|设置语音唤醒回调事件|
|版本支持|最低1.0.0|
|callback|语音唤醒回调|
