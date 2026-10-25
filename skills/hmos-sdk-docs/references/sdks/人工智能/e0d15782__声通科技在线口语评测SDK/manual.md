# **一、引入方式** 

第一步 工程 /entry/oh-package.json5 文件中添加依赖 

`"dependencies": { "@ohos/stkouyu": "` xxx `" }` 

## 第二步 安装 stkouyu.har 

## 1. 在工程目录下安装 

```
 ohpm install
```

## 2. 在工程 

/entry/oh_modules/.ohpm/@ohos+stkouyu@file+libs+stkouyu.ha r/oh_modules/@ohos/stkouyu 下查看版本信息 

`{ "name": "stkouyu", "version": "1.0.2",    //` 版本 `"description": "Evaluation Engine Har, Presented by ShenTong.", "main": "index.js", "author": "isuntone", "license": "isuntone", "dependencies": {}, "devDependencies": {}, "types": "index.d.ets", "artifactType": "obfuscation" }` 

## 第三步 权限申请 

`ohos.permission.READ_MEDIA       //` 允许应用读取用户外部存储中的媒体文件信息 `ohos.permission.WRITE_MEDIA            //` 允许应用读写用户外部存储中的媒体文件信息 `ohos.permission.MICROPHONE      //` 允许应用使用麦克风权限 `ohos.permission.INTERNET      //` 允许应用使用网络权限 

# **二、接口调用流程** 

备注: SDK 为单例, app 生命周期初始化一次即可。请勿重复频繁销毁、初始化 SDK ,否 则可能导致 crash 。 

### **1. 初始化引擎** 

## **代码示例** 

`import { SkEgnManager } from '@ohos/stkouyu' import { EngineSetting } from '@ohos/stkouyu' import { OnInitEngineListener } from '@ohos/stkouyu' ...... let setting = EngineSetting.getInstance(getContext(this)); setting.setOnInitEngineListener({   //` 监听初始化状态 `//` 开始初始化引擎 `onStartInitEngine: () => { //todo }, //` 初始化引擎成功 `onInitEngineSuccess: () => { //todo }, //` 初始化引擎失败 `onInitEngineFailed: (reason: string) => { //todo } });` `SkEgnManager.getInstance(getContext(this)).initCloudEngine("AppKey","SecretKey","u` `serId",setting);` 

### **2. 开始评测** 

## **代码示例** 

`import { SkEgnManager } from '@ohos/stkouyu' import { OnRecorderListener } from '@ohos/stkouyu' import { RecordSetting } from '@ohos/stkouyu' ...... let mOnRecorderListener:OnRecorderListener = { //` 开始录制 `onStart:()=>{ //todo }, //` 录制失败 `onStartRecordFail:(reason: string)=>{ //todo }, //` 录制结束 `onRecordEnd:()=>{ //todo }, //` 录制中 `onRecording:(vadStatus: number, soundIntensity: number)=>{ //todo }, //` 评分结果回调 `onScore:(score: string)=>{ //todo } //` 倒计时回调 `onTick: (remainingTime: number, percentage: number)=>{ //todo } };` 

`let recordSetting= new RecordSetting(); recordSetting.setCoreType("` xxx `"); recordSetting.setRefText("hello");` `SkEgnManager.getInstance(getContext(this)).startRecord(recordSetting,` `mOnRecorderListener);` 

### **3. 停止评测** 

## **代码示例** 

```
 import { SkEgnManager } from '@ohos/stkouyu'
 ......
 SkEgnManager.getInstance(getContext(this)).stopRecord();
```

### **4. 取消评测** 

## **代码示例** 

```
import { SkEgnManager } from '@ohos/stkouyu'
......
SkEgnManager.getInstance(getContext(this)).cancel();
```

### **5. 销毁引擎** 

## **代码示例** 

```
import { SkEgnManager } from '@ohos/stkouyu'
......
SkEgnManager.getInstance(getContext(this)).recycle();
```

### **6. 回放录音** 

## **代码示例** 

```
import { SkEgnManager } from '@ohos/stkouyu'
......
SkEgnManager.getInstance(getContext(this)).playback();
```
