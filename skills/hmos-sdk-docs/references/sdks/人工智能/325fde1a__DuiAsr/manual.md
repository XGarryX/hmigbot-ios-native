## 使用指南

## 简介

这是一个提供短语音实时识别服务的SDK。识别语音内容,并转化为相应的文字输出。

## 安装

## ohpom

```
ohpm install @aispeech/duiasr
```

## 使用方式

## 集成前提

### 创建账号

在DUI开发平台上创建账号

### 创建"技术技术"的产品

实时短语音识别

### 申请apiKey productId,productKey, productSecret

在授权管理标签申请 apiKey,这样可获取产品 apiKey, productId,productKey,

productSecret

生成Product ID,Product Key ,Product Secret ,APIKEY,SDK

Product ID:集成SDK时需用到的鉴权参数

Product Key:集成SDK时需用到的鉴权参数

Product Secret :集成SDK时需用到的鉴权参数

APIKEY:集成SDK时需用到的鉴权参数

## 初始化

```
   DUILiteSDK.init(appContext)
```

## 初始化鉴权

```
/**
  * @paramdeviceInfo设备信息
  * @paramconfig配置文件
  * @paramauthCallback授权回调
  * @paramcleanBefore是否清理之前授权文件
  **/
  DUILiteSDK.doAuth<DUILiteError>((config: DUILiteConfig,deviceInfo:
DeviceInfo,authCallback: (err:E) =>void,cleanBefore: boolean =false));
```

配置文件文档

## 初始化识别引擎

### init

//创建识别引擎

```
let asrEngine = CloudASREngine.createInstance();        //设置识别回调
 asrEngine.setCallback(asrListener)        //开始初始化
 asrEngine.init();
```

### 发送音频开始识别

```
  asrEngine.sendAudioData(data:ArrayBuffer)
```

## 回调函数

```
AsrResult {
//...
var: string;  //识别中的结果
eof: number;  //1 识别结束,0识别中
rec:string;  //识别结束的结果
//...
}
interfaceAsrListener {
//当ASR引擎初始化完成时回调
onInit():void;
//当ASR引擎发生错误时回调
onError(text: string):void;
//当ASR引擎有识别结果时回调
onResults(result: AsrResult):void;
 }
```
