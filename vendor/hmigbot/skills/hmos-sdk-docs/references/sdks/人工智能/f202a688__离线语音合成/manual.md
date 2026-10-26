# 离线语音合成SDK介绍 

unittslibrary SDK基于HarmonyOS开发的离线语音合成SDK,支持离线文本转语音,提供多音 色、多情感发音人,输出 PCM/WAV/MP3 多格式音频,适配短播报、长朗读等全场景语音合成需 求。 

SDK包名:@unisound/tts 

SDK版本号 : 1.0.0 

约束与限制 

#### 在下述版本通过验证: 

|DevEco Studio版 本号|HarmonyOS SDK版本号|手机操作系统ROM版本号|
|---|---|---|
|DevEco Studio|【API11】HarmonyOS SDK|3.0.0.13(SP6DEVC00E13R6P1)|
|5.0.9.100|5.0.0(12)||
|DevEco Studio|【API23】HarmonyOS|6.1.0.117(SP6C00E115R4P9patch15)|
|6.0.2|SDK6.1.0.117(SP6)||

# 一 、SDK说明 

基于HarmonyOS开发的离线语音合成SDK,支持离线文本转语音,提供多音色、多情感发音人, 输出 PCM/WAV/MP3 多格式音频,适配短播报、长朗读等全场景语音合成需求。 示例demo 

SDK包 

# 二、SDK集成步骤 

## 1.1 下载安装 

```
  ohpm i @unisound/tts
```

## 1.2 将SDK的har包拷⻉到工程的libs目录下; 

#### 工程结构图如下: 

在oh-package.json5文件,关联加载离线语音合成库 

```
"dependencies":
  {
    "@unisound/tts": "file:libs/tts.har"
  }
```

# 三、申请权限 

module.json5 文件添加读取媒体文件权限、网络权限 

`"requestPermissions": [ { "name": "ohos.permission.INTERNET" }, { "name": "ohos.permission.READ_MEDIA", //` 使用自定义权限名称 `"reason": "$string:EntryAbility_desc", "usedScene": { "abilities": [ "FormAbility" ], "when": "always" } } ]` 

# 四、SDK使用说明 

### 初始化SDK 

```
 ttsManager = new TtsManager();
```

### TtsManager说明 

|属性|类型|必填|说明|
|---|---|---|---|
|fchmodel_path|string?|是|基础模型文件路径(二进制格式)。|
|bchmodel_path|string?|是|发言人模型文件路径(二进制格式)。|
|uniActivate|UniActivate?|是|授权激活对象(若引擎启用授权校验)。|

### UniActivate说明 

|属性|类型|必填|说明|
|---|---|---|---|
|app_key|string|是|应用appkey(需要申请)|

|app_secret|string|是|应用secret(需要申请)|
|---|---|---|---|
|unique_id|string|是|设备唯一标识|

### 离线语音合成回调事件 

```
OnTtsEngineCallBack {
    onTtsError: (code: number, error: string) => void;
    onTtsStart: () => void;
    onTtsEnd: () => void;
    onTtsBuffer: (data: ArrayBuffer) => void;
}
```

# 五、SDK接口说明 

## TtsManager 

#### 初始化离线语音合成引擎 

init() 

|-|-|
|---|---|
|说明|初始化离线语音合成引擎|
|版本支持|最低1.0.0|
|play(text: string) -|-|
|说明|离线语音合成处理|
|版本支持|最低1.0.0|
|text stop()|合成文本|
|-|-|

|说明|结束离线语音合成|
|---|---|
|版本支持|最低1.0.0|

#### addCallback(callback: OnTtsEngineCallBack) 

|-|-|
|---|---|
|说明|设置离线语音合成回调事件|
|版本支持|最低1.0.0|
|callback|离线语音合成回调|
