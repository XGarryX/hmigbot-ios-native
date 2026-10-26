# **SkEgnManager** 

### **1.initCloudEngine** 

## **含义:初始化引擎** 

## **参数** 

|**参数**|**说明**|
|---|---|
|appkey|appkey,必填|
|secretKey|secretkey|
|userId|用户在应用中的唯一识别|
|engineSetting|初始化引擎的参数|

## **代码示例** 

```
import { SkEgnManager } from '@ohos/stkouyu'
import { EngineSetting } from '@ohos/stkouyu'
import { OnInitEngineListener } from '@ohos/stkouyu'
......
```

`let setting = EngineSetting.getInstance(getContext(this)); setting.setOnInitEngineListener({   //` 监听初始化状态 

`//` 开始初始化引擎 `onStartInitEngine: () => { //todo` 

```
  },
```

`//` 初始化引擎成功 `onInitEngineSuccess: () => { //todo },` 

`//` 初始化引擎失败 

```
  onInitEngineFailed: (reason: string) => {
//todo
  }
});
SkEgnManager.getInstance(getContext(this)).initCloudEngine("AppKey","SecretKey","u
serId",setting);
```

### **2. startRecord** 

## **含义:开始录音** 

## **参数** 

|**参数**|**说明**|
|---|---|
|recordSetting|开始录音设置的参数|
|onRecorderListener|评测结果回调|

## **代码示例** 

```
import { SkEgnManager } from '@ohos/stkouyu'
import { OnRecorderListener } from '@ohos/stkouyu'
import { RecordSetting } from '@ohos/stkouyu'
......
let mOnRecorderListener:OnRecorderListener = {
```

`//` 开始录制 `onStart:()=>{ //todo },` 

`//` 录制失败 `onStartRecordFail:(reason: string)=>{ //todo },` 

`//` 录制结束 `onRecordEnd:()=>{ //todo }, //` 录制中 `onRecording:(vadStatus: number, soundIntensity: number)=>{ //todo }, //` 评分结果回调 `onScore:(score: string)=>{ //todo } //` 倒计时回调 `onTick: (remainingTime: number, percentage: number)=>{ //todo } }; let recordSetting= new RecordSetting(); recordSetting.setCoreType("` xxx `"); recordSetting.setRefText("hello");` `SkEgnManager.getInstance(getContext(this)).startRecord(recordSetting,` `mOnRecorderListener);` 

### **3. stopRecord** 

## **含义:停止录音** 

## **代码示例** 

```
 import { SkEgnManager } from '@ohos/stkouyu'
 ......
 SkEgnManager.getInstance(getContext(this)).stopRecord();
```

### **4. cancel** 

## **含义:取消评测** 

## **代码示例** 

```
import { SkEgnManager } from '@ohos/stkouyu'
......
SkEgnManager.getInstance(getContext(this)).cancel();
```

### **5. recycle** 

## **含义:销毁 SDK 实例** 

## **代码示例** 

```
import { SkEgnManager } from '@ohos/stkouyu'
......
SkEgnManager.getInstance(getContext(this)).recycle();
```

### **6. playback** 

## **含义:回放录音** 

## **代码示例** 

```
import { SkEgnManager } from '@ohos/stkouyu'
......
SkEgnManager.getInstance(getContext(this)).playback();
```
