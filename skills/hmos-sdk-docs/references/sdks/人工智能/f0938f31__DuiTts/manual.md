# TTS使用指南

# 简介

这是一个提供文本在线合成语音服务的SDK。为设备提供将文字信息转化为声音信息的能力,相

当于给应用适配了“嘴巴” 功能

# 安装

## ohpom

```
ohpm install @aispeech/duitts
```

# 使用方式

## 集成前提

## 创建账号

在

DUI开发平台上创建账号

## 创建"技术技术"的产品

在线语音合成

## 申请apiKey productId,productKey, productSecret

在授权管理标签申请 apiKey,这样可获取产品 apiKey, productId,productKey,

productSecret

生成Product ID,Product Key ,Product Secret ,APIKEY,SDK

Product ID:集成SDK时需用到的鉴权参数

Product Key:集成SDK时需用到的鉴权参数

Product Secret :集成SDK时需用到的鉴权参数

APIKEY:集成SDK时需用到的鉴权参数

## 初始化

```
   DUILiteSDK.init(appContext)```
```

### 初始化鉴权

```
```  js   /**   * @param deviceInfo 设备信息

* @paramconfig配置文件
* @paramauthCallback授权回调
* @paramcleanBefore是否清理之前授权文件
  **/
  DUILiteSDK.doAuth<DUILiteError>((config: DUILiteConfig,deviceInfo:
DeviceInfo,authCallback: (err:E) =>void,cleanBefore:boolean=false));

```
[配置文件文档](https://www.duiopen.com/docs/ct_asr_rt_2)
```

### 初始化合成引擎

```
#### init
```js

```

//创建合成引擎

```

let engine = AICouldTTSEngine.getInstance()  let engine.initEngine(new
TtsCallbackImpl(this));  //开始初始化,设置回调

```

```

## 文本转音频

```
  engine.speak(    this.intent,    this.ttsTextDefaultHint??"2023年10月1
日,the weather还不错,车牌号京N16882,关闭车外行人警示音110",
"1024")
```

## 回调函数

```
interfaceAITTSListener {  /**   * 合成引擎初始化结束后执行
  *   * @param status   *            {@link AIConstant#OPT_SUCCESS}:初始化成
功;
  *            {@link AIConstant#OPT_FAILED}:初始化失败,
  */onInit(status: number):void;
```

/**   * 发生错误时执行

```
  * @paramutteranceId本次合成对应的ID
  *   * @param error   *            错误信息
  */onError(utteranceId: string, error:AIError):void;
```

/**   * 数据准备就绪,可以播放时执行

```
  * @paramutteranceId本次合成对应的ID
  */onReady(utteranceId: string):void;
```

/**   * 播放完毕后执行

```
  * @paramutteranceId本次合成对应的ID
  */onCompletion(utteranceId: string):void;
/**   * 播放进度
  *   * @param currentTime   *            当前播放时间 (单位:100ms)
  * @paramtotalTime   *            已经送入内核的文本合成的总时长 (单位:100ms)
  *            云端合成没有此项
  */onProgress(currentTime: number, totalTime: number):void;
```

/**   * 合成开始的回调,在子线程,若需要更新UI控件需要做线程转换

```
  *   * @param utteranceId utteranceId   */onSynthesizeStart(utteranceId:
string):void;
```

/**   * 合成完成的回调 ,在子线程,若需要更新UI控件需要做线程转换

```
  *   * @param utteranceId utteranceId   */
onSynthesizeFinish(utteranceId: string):void;  ```
```
