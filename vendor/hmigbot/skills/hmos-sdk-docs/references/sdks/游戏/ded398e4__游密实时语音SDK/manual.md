# 游密实时语音 使用指 **Talk SDK for HarmonyOS** 

## **Talk SDK** 简介 

### **1.** 功能目标 

开发者在成功接入 Talk SDK 简介后,无需部署任何服务器即可拥有实时语音讲话能力。 

### **2.SDK** 目录讲解 

库 

`@youme/voice_engine` 包含了必须的接口和 so 库,请导入 HarmonyOS 工程。 

### **3.** 关键类及描述 

#### YouMeRtcAPI 

- 引擎服务类 `,` 单例模式。该类提供 `SDK` 操作的相关方法 `,` 例如 `:` 初始化,加入房间,参数设置 

- 等。 

#### YouMeRtcUserRole 

用户通话角色。 

#### YouMeRtcEvent 

`SDK` 事件类型 

#### YouMeRtcErrorCode 

错误码 

- YouMeRtcServerRegion 

`SDK` 语音服务地域。 

## **Talk SDK** 操作指引 

Page 1 of 6 

### **1.** 申请使用游密 **Talk SDK** 

- 首先请与游密商务联系,提供公司名称、游戏的名称、联系人电话、邮箱、 QQ 等以申请 IM 引擎 的使用权限。审批通过后会得到有效的 AppKey 和 AppSecret ,这些信息属于私密信息,请妥善保 管。 

### **2.** 配置依赖项 

在模块的 oh-package.json5 中 dependencies 增加 har 包依赖,配置如下: 

```
"dependencies": {
  "@youme/voice_engine": "1.0.15"
}
```

依赖设置完成后,需要执行 `ohpm install @youme/voice_engine` 命令安装依赖包,依赖包会 安装在该模块的 oh_modules 目录下。 

### **3.** 权限配置 

在模块的 module.json5 中 requestPermissions 添加网络和麦克风权限,配置如下: 

```
"requestPermissions": [
  {
    "name": "ohos.permission.INTERNET",
  },
  {
    "name": "ohos.permission.MICROPHONE",
    "reason": "$string:mic_reason",
    "usedScene": {
      "abilities": [
        "FormAbility"
      ],
      "when": "inuse"
    }
  }
```

## **SDK** 接入示例 

应用中使用 **ArkTs** 代码调用 **SDK ArkTs API** 

Page 2 of 6 

#### �. SDK 调用示例 - 设置 SDK 事件回调和成员列表变更回调: 

```
import { YouMeRtcAPI } from '@youme/voice_engine';
```

`let curDate = new Date(); YouMeRtcAPI.Instance().SetEventCallback( (event, errCode, channel, param) => { const ctx = getContext(this) ctx.eventHub.emit("youme_event", event, errCode, channel, param) } ); this.sdkEventInfo += `${curDate.toLocaleTimeString()}` 【 `api` 】设置事件回调 `\n YouMeRtcAPI.Instance().SetMemberChangeCallback( (channel, members, isUpdate) => { const ctx = getContext(this) ctx.eventHub.emit("youme_members", channel, members, isUpdate) } ); this.sdkEventInfo += `${curDate.toLocaleTimeString()}` 【 `api` 】设置成员列表回调 

#### �. SDK 调用示例 - 初始化 SDK : 

```
import { YouMeRtcAPI } from '@youme/voice_engine';
const promise = new Promise<number>((resolve, reject) => {
let error = YouMeVoiceAPI.Instance().Init(this.appCustom.appKey, this
if (error == 0) {
resolve(error);
} else {
reject(new Error("error call failed"));
}
});
promise
.then(result => {
hilog.info(logFlag, logTag, `call init sdk succ:${result} region:
})
.catch((e: Error) => {
hilog.error(logFlag, logTag, `call init sdk err:${e.message} zone
});
```

#### �. SDK 调用示例 - 监听 SDK 事件: 

Page 3 of 6 

```
import { YouMeRtcErrorCode, YouMeRtcEvent } from '@youme/voice_engine';
```

`eventLister: Function = (event:YouMeRtcEvent, err:YouMeRtcErrorCode, chan let curDate = new Date(); switch (event){ case YouMeRtcEvent.YOUME_EVENT_LOCAL_MIC_ON: case YouMeRtcEvent.YOUME_EVENT_LOCAL_MIC_OFF: case YouMeRtcEvent.YOUME_EVENT_LOCAL_SPEAKER_ON: case YouMeRtcEvent.YOUME_EVENT_LOCAL_SPEAKER_OFF: case YouMeRtcEvent.YOUME_EVENT_SWITCH_OUTPUT:{ this.sdkEventInfo += `${curDate.toLocaleTimeString()}` 【 `event` 】 `${eve break; } case YouMeRtcEvent.YOUME_EVENT_MY_MIC_LEVEL:{ this.selfVolumeLevel = err break; } case YouMeRtcEvent.YOUME_EVENT_FAREND_VOICE_LEVEL:{ this.farendVolumeLevel = err this.farendUser = param break; } case YouMeRtcEvent.YOUME_EVENT_OTHERS_VOICE_ON:{ this.sdkEventInfo += `${curDate.toLocaleTimeString()}` 【 `vad` 】 `${event break; } case YouMeRtcEvent.YOUME_EVENT_OTHERS_VOICE_OFF:{ this.sdkEventInfo += `${curDate.toLocaleTimeString()}` 【 `vad` 】 `${event break; } case YouMeRtcEvent.YOUME_EVENT_PAUSED: { this.sdkEventInfo += `${curDate.toLocaleTimeString()}` 【 `vad` 】 `${event break; } case YouMeRtcEvent.YOUME_EVENT_RESUMED: { this.sdkEventInfo += `${curDate.toLocaleTimeString()}` 【 `vad` 】 `${event break; } case YouMeRtcEvent.YOUME_EVENT_OTHERS_MIC_ON: { this.sdkEventInfo += `${curDate.toLocaleTimeString()}` 【 `event` 】 `${eve break; } case YouMeRtcEvent.YOUME_EVENT_OTHERS_MIC_OFF: { this.sdkEventInfo += `${curDate.toLocaleTimeString()}` 【 `event` 】 `${eve` 

Page 4 of 6 

`break; } case YouMeRtcEvent.YOUME_EVENT_OTHERS_SPEAKER_ON: { this.sdkEventInfo += `${curDate.toLocaleTimeString()}` 【 `event` 】 `${eve break; } case YouMeRtcEvent.YOUME_EVENT_OTHERS_SPEAKER_OFF: { this.sdkEventInfo += `${curDate.toLocaleTimeString()}` 【 `event` 】 `${eve break; } default:{ break; } } }` 

### 应用中使用 **C++** 代码调用 **SDK C++ API** 

- �. 调用 SDK C++ API ,需要先在 Native C++ 代码的 CMakeList.txt 中配置依赖的 SDK 头文件和库文件路 径,示例如下: 

```
# the minimum version of CMake.
cmake_minimum_required(VERSION 3.5.0)
project(entry)
set(NATIVERENDER_ROOT_PATH ${CMAKE_CURRENT_SOURCE_DIR})
if(DEFINED PACKAGE_FIND_FILE)
    include(${PACKAGE_FIND_FILE})
endif()
include_directories(${NATIVERENDER_ROOT_PATH}
                    ${NATIVERENDER_ROOT_PATH}/include
                    ${CMAKE_CURRENT_SOURCE_DIR}/../../../oh_modules/@youm
set(YOUME_LIB_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../../../oh_modules/@youme
link_directories(${YOUME_LIB_PATH}/${CMAKE_OHOS_ARCH_ABI})
add_library(entry SHARED napi_init.cpp youme_native.cpp)
target_link_libraries(entry PUBLIC libyoume_voice_engine.so libace_napi.z
```

#### �. 应用 C++ 代码引入 SDK 头文件即可调用 C++ API 。 

Page 5 of 6 

```
#include "IYouMeVoiceEngine.h"
#include "IYouMeEventCallback.h"
#include "YouMeConstDefine.h"
```

#### `//` 定义 `SDK` 回调监听类 

```
class YouMeCallback:
    public IYouMeEventCallback,
    public IRestApiCallback,
    public IYouMeMemberChangeCallback,
    public IYouMeAVStatisticNewCallback,
    public IYouMeChannelMsgCallback,
    public IYouMePcmCallback,
    public IYouMeDetectNetworkCallback
{
public:
    void onEvent(const YouMeEvent event, const YouMeErrorCode error, cons
    void onRequestRestAPI(int requestID, const YouMeErrorCode &iErrorCode
    void onDetectNetWorkCompleteCb(bool bNetworkOK, const char*  strResul
    void onAVStatisticNew(YouMeAVStatisticType type, const char* userID,
    void onMemberChange(const char*  channel, const char* listMemberChang
    void onBroadcast(const YouMeBroadcast bc, const char*  channel, const
    void onPcmDataRemote(int channelNum, int samplingRateHz, int bytesPer
    void onPcmDataRecord(int channelNum, int samplingRateHz, int bytesPer
    void onPcmDataMix(int channelNum, int samplingRateHz, int bytesPerSam
```

#### `}` 

#### `//` 设置回调 

```
YouMeCallback* inst = new YouMeCallback();
IYouMeVoiceEngine::getInstance()->setRestApiCallback(inst);
IYouMeVoiceEngine::getInstance()->setMemberChangeCallback(inst);
IYouMeVoiceEngine::getInstance()->setNotifyCallback(inst);
IYouMeVoiceEngine::getInstance()->setDetectNetworkCallback(inst);
IYouMeVoiceEngine::getInstance()->setAVStatisticNewCallback(inst);
```

#### `//` 初始化 `SDK` 

```
YouMeErrorCode ec = IYouMeVoiceEngine::getInstance()->init(inst, appKey,
```

Page 6 of 6
