# Harmony平台BJCast发射端SDK接口 

当前版本:V1.0.9 

©苏州必捷网络有限公司 

**1 概述** 

1.1 目的 1.2 读者对象 1.3 缩略语定义 **2 范围** 

2.1 功能 2.2 总体框架 

2.3 SDK交付物 **3 接口** 

3.1 BJCast命名空间中的接口说明 

3.1.1 初始化接口 

3.1.2 探测接收端接口 

3.1.3 开始投屏接口 

3.1.4 请求全屏控制接口 

3.1.5 退出全屏控制接口 

3.1.6 结束投屏接口 

3.1.7 音频控制接口 

3.1.8 设置投屏质量场景配置接口 

3.1.9 PIN码校验接口 

**4 如何使用SDK** 

4.1 集成SDK简要说明 

修订记录:文档初始拟定时,可不填“评审人”以及“修改内容要点” 

|**版本号**|**拟制/修改人**|**拟制/修改日期**|**修改内容要点**|
|---|---|---|---|
|1.0.0|谢清华|2025/01/16|SDK接口文档撰写|
|1.0.7|谢清华|2025/04/03|SDK新增接口字段,代码优化|
|1.0.8|谢清华|2025/04/28|SDK打包类型从HSP改为HAR,SDK接口文档更新|
|1.0.9|谢清华|2025/05/14|SDK新增PIN码校验接口|

## **1 概述** 

### **1.1 目的** 

用于指导用户使用必捷无线投屏SDK开发Harmony发送端应用程序。 

### **1.2 读者对象** 

本文档适用于Harmony发送端应用程序的开发人员和测试人员。 

### **1.3 缩略语定义** 

|**缩写名称**|**英文**|**中文**|
|---|---|---|
|BJCast|BJCast|必捷无线投屏协议|

## **2 范围** 

### **2.1 功能** 

本SDK为BJCast发射端SDK,和BJCast接收端SDK配合进行无线投屏。 

本SDK为标准的 Harmony 静态共享包HAR模块,提供API接口供应用集成。 

### **2.2 总体框架** 

总体框架分为两层: 

1. SDK层: **hm_bjcast.har** 是一个Harmony 静态共享包HAR模块。实现了投屏控制协议,录屏功能,媒体传输 和处理协议。提供ArkTS接口供外部应用集成。 

2. 应用层:我司基于SDK开发的Demo APP,用于简化用户的应用集成,用户可参考此demo进行开发修改,也可 直接使用。其依赖于 **hm_bjcast.har** 。 

### **2.3 SDK交付物** 

SDK库文件 

- Demo APP源代码,Demo APP基于最新SDK,作为参考实现提供给客户 

- SDK接口文档 

## **3 接口** 

### **3.1 BJCast命名空间中的接口说明** 

#### **3.1.1 初始化接口** 

```
functionInit(initParams: BJCastSenderInitPara): number;
```

##### **描述** 

初始化BJCastSenderSDK,App在启动时作初始化调用。 

##### **参数** 

|**名称**|**描述**|
|---|---|
|initParams|SDK初始化参数|

其中 **BJCastSenderInitPara** 支持以下参数的设置: 

|**参数名**|**描述**|**必填**|
|---|---|---|
|channel_id|**SDK channel_id,由我司提供**|是|
|channel_code|**SDK channel_code,由我司提供**|是|
|sender_id|发射端ID,由应用层随机生成并传入,需保证唯一性|是|
|user_name|用户自定义|是|
|encoder_scene_conf|投屏质量场景配置json字符串|否|
|encoder_ext_conf **BJCast.Init** 有以下返回值:|投屏质量场景配置额外参数,当前无需设置|否|
|**返回值**|**含义**||
|0|初始化成功||
|-1|初始化失败||
|-101|初始化SDK channel信息失败||

##### **示例代码:** 

```
// 导入BJCast方法集
import { BJCast } from'hm_bjcast'
// 初始化参数结构体
interfaceBJCastSenderInitPara {
channel_id: number;
channel_code: string;
sender_id: string;
user_name: string;
encoder_scene_conf: string;
encoder_ext_conf: string;
}
// 设置初始化参数
letinitParams: BJCastSenderInitPara = {
channel_id: 0,           // SDK channel_id,由我司提供
channel_code: "",        // SDK channel_code,由我司提供
sender_id: "sender123",  // 由应用层随机生成,需保证唯一性
user_name: "user123456", // 用户自定义
encoder_scene_conf: "",  // 传入场景配置字符串 =>
JSON.stringify(encoder_scene_conf.scene_define[2])
encoder_ext_conf: ""// 场景配置额外参数,当前无需设置
};
// 使用BJCast中的Init方法
this.result=BJCast.Init(initParams);
```

**encoder_scene_conf.json** 字符串文件示例: 

```
{
"scene_define":[
    {
"scene_name":"",
"scene_id":0,
"scene_encoder_config":
      [
        {
"codec": 1,
"width":1918,
"height":1078,
"min_width":0,
"min_height":0,
"bitrate": 1000,
"framerate": 30,
"qmin":-1,
"qmax":-1
        },
        {
"codec": 1,
"width":1920,
"height":1080,
"min_width":1918,
"min_height":1078,
"bitrate": 1000,
"framerate": 30,
"qmin":-1,
"qmax":-1
        },
        {
"codec": 1,
"width":2560,
"height":1440,
"min_width":1922,
"min_height":1082,
"bitrate": 2000,
"framerate": 30,
"qmin":-1,
"qmax":-1
        },
        {
"codec": 1,
"width":3840,
"height":2160,
"min_width":2562,
"min_height":1442,
"bitrate": 4000,
"framerate": 30,
"qmin":-1,
"qmax":-1
        }
"scene_name":"",
"scene_id":1,
"scene_encoder_config":
"codec": 1,
"width":1918,
"height":1078,
"min_width":0,
"min_height":0,
"bitrate": 1500,
"framerate": 30,
"qmin":-1,
"qmax":-1
"codec": 1,
"width":1920,
"height":1080,
"min_width":1918,
"min_height":1078,
"bitrate": 3000,
"framerate": 60,
"qmin":-1,
"qmax":-1
"codec": 1,
"width":2560,
"height":1440,
"min_width":1922,
"min_height":1082,
"bitrate": 6000,
"framerate": 60,
"qmin":-1,
"qmax":-1
"codec": 1,
"width":3840,
"height":2160,
"min_width":2562,
"min_height":1442,
"bitrate": 6000,
"framerate": 30,
"qmin":-1,
"qmax":-1
    {
"scene_name":"",
"scene_id":2,
"scene_encoder_config":
      [
        {
"codec": 1,
"width":1918,
"height":1078,
"min_width":0,
"min_height":0,
"bitrate": 2000,
"framerate": 60,
"qmin":-1,
"qmax":-1
        },
        {
"codec": 1,
"width":1920,
"height":1080,
"min_width":1918,
"min_height":1078,
"bitrate": 4000,
"framerate": 60,
"qmin":-1,
"qmax":-1
        },
        {
"codec": 1,
"width":2560,
"height":1440,
"min_width":1922,
"min_height":1082,
"bitrate": 8000,
"framerate": 60,
"qmin":-1,
"qmax":-1
        },
        {
"codec": 1,
"width":3840,
"height":2160,
"min_width":2562,
"min_height":1442,
"bitrate": 8000,
"framerate": 30,
"qmin":-1,
"qmax":-1
        }
      ]
    }
  ]
}
```

#### **3.1.2 探测接收端接口** 

```
functionProbe(targetIp: string,
fucSuccess: (res: string | Object | ArrayBuffer) => void,
fucError: (err: BusinessError) => void): Promise<void>;
```

##### **描述** 

##### 向接收端发起探测流程以获取接收端的能力集。 

##### **参数** 

|**名称**|**描述**|
|---|---|
|targetIp|需要探测的接收端IP地址|
|fucSuccess|探测成功回调函数|
|fucError|探测失败回调函数|

##### **fucSuccess回调函数:(string | Object | ArrayBuffer 为可能的返回值类型)** 

|**返回值含义**||
|---|---|
|json字符串 探测成功,解析jso|n字符串成功为ProbeDevice对象;否则为BusinessError错误码|
|`// ProbeDevice对象结构体` `interface ProbeDevice {` `DeviceIPList: string[],` `DeviceId: string,`|`// IP地址列表` `//设备ID`|
|`DeviceName: string,`|`//设备名称`|
|`ft: number,`|`// ft值,默认为31`|
|`max_framerate: number,`|`//接收端支持的最大帧率`|
|`max_resolution: number,`|`//接收端支持的最大分辨率`|
|`msg: string,`|`//接收端返回的信息`|
|`screen_orientation: number` `}`|`//接收端横竖屏状态:  0:横屏  1:竖屏`|

##### **ProbeDevice对象结构体:** 

|**字段**|**含义**|
|---|---|
|DeviceIPList|IP地址列表|
|DeviceId|设备ID|
|DeviceName|设备名称|
|ft|ft值,默认为31|

|**字段**|**含义**|
|---|---|
|max_framerate|接收端支持的最大帧率|
|max_resolution|接收端支持的最大分辨率|
|msg|接收端返回的信息|
|screen_orientation|接收端横竖屏状态:0:横屏1:竖屏|

##### **fucError回调函数:(BusinessError为返回值类型)** 

|**返回值**|**含义**|
|---|---|
|json字符串|解析json字符串为BusinessError错误码|

##### **BusinessError错误码** 

|**BusinessError错误码**|**含义**|
|---|---|
|401|Parameter error(参数错误)|
|2300006|Couldn't resolve host name(无法解析主机名)|
|2300007|Couldn't connect to server(无法连接服务)|
|2300028|Timeout was reached(访问超时)|
|2301099|Address not available(IP地址无效)|

##### **示例代码:** 

```
// 导入BJCast方法集
import { BJCast } from'hm_bjcast'
import { BusinessError } from'@kit.BasicServicesKit';
// ProbeDevice对象结构体
interfaceProbeDevice {
DeviceIPList: string[],
DeviceId: string,
DeviceName: string,
ft: number,
max_framerate: number,
max_resolution: number,
msg: string,
screen_orientation: number
}
// Probe错误返回的回调函数,由应用层定义
private on_probe_callback_err(err: BusinessError) {
console.log("on_probe_callback==>"+JSON.stringify(err))
}
// Probe探测IP地址合法性
BJCast.Probe(this.ipInputValue, (res: string | Object | ArrayBuffer) => {
console.log("on_probe_callback==>"+JSON.stringify(res))
letdevice: ProbeDevice =JSON.parse(JSON.stringify(res))
lettm_screen_orientation=0;
if (device.screen_orientation!=null) {
tm_screen_orientation=device.screen_orientation; // 接收端横竖屏状态:0:横屏 1:
竖屏
          }
letparams: BJCastSenderPara = {
ipaddress: device.DeviceIPList[0],  //IP地址
port: 8190,                         //端口号, 默认为8190
pin: "",                            //Pin码功能
ft: device.ft,                      //ft值, 默认为31
deviceName: device.DeviceName,      //设备名称
remote_max_resolution: device.max_resolution, //默认为0
screen_orientation: tm_screen_orientation// 接收端横竖屏状态:0:横屏  1:竖屏
          };
console.log("start cast session ip="+device.DeviceIPList[0])
// 探测成功后再执行投屏操作
BJCast.StartBJCastSession(params,
this.on_session_end_cb,
this.on_start_session_result_cb,
this.on_session_update_cb
          );
        }, this.on_probe_callback_err);
```

#### **3.1.3 开始投屏接口** 

###### `function StartBJCastSession(params: BJCastSenderPara,` 

```
on_session_end_cb: (reason: number) => void,
on_start_session_result_cb: (reason: number) => void,
on_session_update_cb: (reason: number) => void): number;
```

##### **描述** 

通过此接口发起投屏,发起投屏的结果会通过 **on_start_session_result_cb** 回调函数通知用户。 

##### **参数** 

|**名称**|**描述**|
|---|---|
|BJCastSenderPara|投屏参数,BJCastSenderPara类型。|

|**名称**|**描述**||
|---|---|---|
|on_session_end_cb|结束投屏会话回调函数,由应用层定义||
|on_start_session_result_cb|开始投屏会话返回结果回调函数,由应用层定义||
|on_session_update_cb|更新投屏会话回调函数,由应用层定义||
|**参数名** 其中**BJCastSenderPara**支持以|**描述** 下参数的设置:|**必填**|
|ipaddress|IP地址,根据Probe接口返回值填写:device.DeviceIPList[0]|是|
|port|端口号|是|
|pin|投屏密码,无密码则填空字符串"",注意不可填null|是|
|ft|ft值,根据Probe接口返回值填写:device.ft|是|
|deviceName|设备名称,根据Probe接口返回值填写:device.DeviceName|是|
|remote_max_resolution|接收端支持的最大分辨率,根据Probe接口返回值填写: device.max_resolution|是|
|screen_orientation|接收端横竖屏状态(默认为0):0:横屏1:竖屏,根据Probe接口返回值填 写:device.screen_orientation|是|

##### **BJCast.StartBJCastSession** 有以下返回值: 

|**返回值**|**含义**|
|---|---|
|0|投屏成功|
|-1|投屏失败|
|-121 **on_session_e**|SDK channel信息错误 **nd_cb回调函数有以下返回值:**|
|**返回值**|**含义**|
|2|接收端踢出投屏|
|0|退出投屏|
|-17|心跳丢失(盒子断网,盒子重启,切换到其他不通的网络等)|
|-31|网络切换变动(切换到互通的网络)|

**on_start_session_result_cb 回调函数有以下返回值:** 

|**返回值**|**含义**|
|---|---|
|0|投屏成功|
|-6|网络异常|
|-7|请求超时|
|-8|无效参数|
|-14|当前投屏被拒绝|
|-15|接收端投屏已满|
|-16|PIN码错误或触发PIN码投屏事件|
|-51|媒体部分错误|

##### **on_session_update_cb 回调函数(用于全屏控制返回结果):** 

|**返回值**|**含义**|
|---|---|
|0|请求全屏成功/退出全屏成功|

##### **示例代码:** 

```
// 导入BJCast方法集
import { BJCast } from'hm_bjcast'
import { BusinessError } from'@kit.BasicServicesKit';
// 投屏参数结构体
interfaceBJCastSenderPara {
ipaddress: string;
port: number;
pin: string;
ft: number;
deviceName: string;
remote_max_resolution: number;
screen_orientation: number;
}
// ProbeDevice对象结构体
interfaceProbeDevice {
DeviceIPList: string[],
DeviceId: string,
DeviceName: string,
ft: number,
max_framerate: number,
max_resolution: number,
msg: string,
screen_orientation: number
}
```

###### `// 设置全局变量` 

```
@StateipInputValue: string='192.168.'
@StateonCreateStartCastSession: number=0// 开始结束投屏时,控制界面显示变化,根据需求定义
@StateonCreateIsFullCast: number=0// 放大缩小时,控制界面显示变化,根据需求定义
// Probe错误返回的回调函数,由应用层定义
private on_probe_callback_err(err: BusinessError) {
console.log("on_probe_callback==>"+JSON.stringify(err))
}
// 结束投屏会话回调函数,由应用层定义
on_session_end_cb= (reason: number) => {
console.log(`Session ended with reason: ${reason}`);
if (reason==0||reason==2||reason==-17||reason==-31) {
this.onCreateStartCastSession=0;
this.onCreateIsFullCast=0
   }
}
// 开始投屏会话返回结果回调函数,由应用层定义
on_start_session_result_cb= (reason: number) => {
console.log(`Session notify with reason: ${reason}`);
if (reason==0) {
this.onCreateStartCastSession=1;
  }
}
// 更新投屏会话回调函数,由应用层定义
on_session_update_cb= (reason: number) => {
console.log(`Session update with reason: ${reason}`);
if (reason==0) {
this.onCreateIsFullCast=1
    } elseif (reason==1) {
this.onCreateIsFullCast=2
  }
}
// Probe探测IP地址合法性
BJCast.Probe(this.ipInputValue,
        (res: string | Object | ArrayBuffer) => {
console.log("on_probe_callback==>"+JSON.stringify(res))
letdevice: ProbeDevice =JSON.parse(JSON.stringify(res))
lettm_screen_orientation=0;
if (device.screen_orientation!=null) {
tm_screen_orientation=device.screen_orientation; // 接收端横竖屏状态:0:横屏  1:
竖屏
          }
letparams: BJCastSenderPara = {
ipaddress: device.DeviceIPList[0],  // IP地址
port: 8190,                         // 端口号, 默认为8190
pin: "",                            // Pin码功能
ft: device.ft,                      // ft值, 默认为31
deviceName: device.DeviceName,      // 设备名称
remote_max_resolution: device.max_resolution, // 默认为0
screen_orientation: tm_screen_orientation// 接收端横竖屏状态:0:横屏  1:竖屏
          };
console.log("start cast session ip="+device.DeviceIPList[0])
// 调用开始投屏接口
BJCast.StartBJCastSession(params,
this.on_session_end_cb,
this.on_start_session_result_cb,
this.on_session_update_cb
          );
        }, this.on_probe_callback_err);
```

#### **3.1.4 请求全屏控制接口** 

```
functionRequestFullScreen(): number;
```

##### **描述** 

只有在投屏状态,并且多路投屏时,才可通过此接口请求全屏控制,会通过 **on_session_update_cb** 回调函数返回结 果。 

##### **返回值** 

**返回值 含义** 0 成功请求全屏 

#### **3.1.5 退出全屏控制接口** 

```
functionExistFullScreen(): number;
```

##### **描述** 

只有在投屏状态,多路投屏并且处于全屏状态时,才可通过此接口退出全屏控制,会通过 **on_session_update_cb** 回 调函数返回结果。 

##### **返回值** 

|**返回值**|**含义**|
|---|---|
|0|成功退出全屏|

#### **3.1.6 结束投屏接口** 

```
functionStopBJCastSession(): number;
```

##### **描述** 

正在投屏或退出程序时,通过此接口结束投屏,会通过 **on_session_end_cb** 回调函数返回结果。 

##### **返回值** 

|**返回值**|**含义**|
|---|---|
|0|成功结束投屏|

#### **3.1.7 音频控制接口** 

```
functionAudioControl(audioType: number): void;
```

##### **描述** 

SDK初始化后,投屏前可通过此接口对是否采集音频进行控制 

##### **参数** 

|**名称**|**描述**|**必填**|
|---|---|---|
|audioType|音频类型:0:关闭声音1:开启声音|否|

##### **示例代码:** 

```
// 音频控制(在初始化后, 投屏前设置)
BJCast.AudioControl(0); //0: 关闭声音 1:开启声音
```

#### **3.1.8 设置投屏质量场景配置接口** 

```
functionSetEncoderSceneConfig(encoderSceneConfig: string): void;
```

##### **描述** 

SDK初始化后,投屏前可通过此接口对投屏质量进行控制 

##### **参数** 

|**名称**|**描述**|**必填**|
|---|---|---|
|encoderSceneConfig|投屏质量场景配置json字符串|否|
|**示例代码:**|||

```
BJCast.SetEncoderSceneConfig(JSON.stringify(encoder_scene_conf.scene_define[0]))
```

**encoder_scene_conf.json** 字符串文件示例: 

```
{
"scene_define":[
    {
"scene_name":"",
"scene_id":0,
"scene_encoder_config":
      [
        {
"codec": 1,
"width":1918,
"height":1078,
"min_width":0,
"min_height":0,
"bitrate": 1000,
"framerate": 30,
"qmin":-1,
"qmax":-1
        },
        {
"codec": 1,
"width":1920,
"height":1080,
"min_width":1918,
"min_height":1078,
"bitrate": 1000,
"framerate": 30,
"qmin":-1,
"qmax":-1
        },
        {
"codec": 1,
"width":2560,
"height":1440,
"min_width":1922,
"min_height":1082,
"bitrate": 2000,
"framerate": 30,
"qmin":-1,
"qmax":-1
        },
        {
"codec": 1,
"width":3840,
"height":2160,
"min_width":2562,
"min_height":1442,
"bitrate": 4000,
"framerate": 30,
"qmin":-1,
"qmax":-1
"scene_name":"",
"scene_id":1,
"scene_encoder_config":
"codec": 1,
"width":1918,
"height":1078,
"min_width":0,
"min_height":0,
"bitrate": 1500,
"framerate": 30,
"qmin":-1,
"qmax":-1
"codec": 1,
"width":1920,
"height":1080,
"min_width":1918,
"min_height":1078,
"bitrate": 3000,
"framerate": 60,
"qmin":-1,
"qmax":-1
"codec": 1,
"width":2560,
"height":1440,
"min_width":1922,
"min_height":1082,
"bitrate": 6000,
"framerate": 60,
"qmin":-1,
"qmax":-1
"codec": 1,
"width":3840,
"height":2160,
"min_width":2562,
"min_height":1442,
"bitrate": 6000,
"framerate": 30,
"qmin":-1,
"qmax":-1
"scene_name":"",
"scene_id":2,
"scene_encoder_config":
"codec": 1,
"width":1918,
"height":1078,
"min_width":0,
"min_height":0,
"bitrate": 2000,
"framerate": 60,
"qmin":-1,
"qmax":-1
"codec": 1,
"width":1920,
"height":1080,
"min_width":1918,
"min_height":1078,
"bitrate": 4000,
"framerate": 60,
"qmin":-1,
"qmax":-1
"codec": 1,
"width":2560,
"height":1440,
"min_width":1922,
"min_height":1082,
"bitrate": 8000,
"framerate": 60,
"qmin":-1,
"qmax":-1
"codec": 1,
"width":3840,
"height":2160,
"min_width":2562,
"min_height":1442,
"bitrate": 8000,
"framerate": 30,
"qmin":-1,
"qmax":-1
    }
  ]
}
```

#### **3.1.9 PIN码校验接口** 

```
functionReAuth(pin: string): void;
```

##### **描述** 

PIN码错误或触发PIN码事件后,通过此接口校验PIN码 

##### **参数** 

|**名称**|**描述**|**必填**|
|---|---|---|
|pin|用户输入的PIN码|是|

##### **示例代码:** 

```
import { ImmersiveMode, LevelMode } from'@kit.ArkUI';
@StatepinCode: string=''; // 用户输入的PIN码
showPinDialog: number=0; // 控制PIN码输入框显示
// 处理PIN码验证
private handlePinAuth() {
if (this.pinCode.trim() ==='') {
hilog.error(0x0000, 'MY_TAG', 'PIN Code cannot be empty!');
return;
    }
try {
this.uiContext.getPromptAction().closeCustomDialog(this.showPinDialog);
BJCast.ReAuth(this.pinCode);  // 调用PIN码校验接口
this.pinCode='';
    } catch (error) {
hilog.error(0x0000, 'MY_TAG', 'Auth failed: %{public}s', error.message);
    }
  }
@Builder
pinCodeDialogComponent(uiContext: UIContext) {
this.pinCodeDialogBuilder(uiContext);
  }
@Builder
pinCodeDialogBuilder(uiContext: UIContext) {
Column() {
Text('请输入PIN码')
        .fontSize(18)
        .margin({ bottom: 20 });
TextInput({ placeholder: 'PIN码', text: this.pinCode })
        .onChange(value=>this.pinCode=value)
        .width('80%')
        .margin({ bottom: 20 });
Row() {
Button("确认").onClick(() =>this.handlePinAuth())
          .backgroundColor('#e9007dff')
          .width(120);
Blank().width(50)
Button("取消")
          .onClick(() => {
this.pinCode='';
BJCast.StopBJCastSession();
uiContext.getPromptAction().closeCustomDialog(this.showPinDialog);
          })
          .backgroundColor('#f3ff0000')
          .width(120);
      }
    }.padding(20)
  }
startCastSession() {
// Probe
if (this.result==0) {
BJCast.Probe(this.ipInputValue,
        (res: string | Object | ArrayBuffer) => {
// console.log("on_probe_callback==>" + JSON.stringify(res))
letdevice: ProbeDevice =JSON.parse(JSON.stringify(res))
lettm_screen_orientation=0;
if (device.screen_orientation!=null) {
tm_screen_orientation=device.screen_orientation; // 接收端横竖屏状态:0:横屏  1:
竖屏
          }
letparams: BJCastSenderPara = {
ipaddress: device.DeviceIPList[0],  //IP地址
port: 8190,                         //端口, 默认为8190
pin: this.pinCode,                  //Pin码功能
ft: device.ft,                      //ft值, 默认为31
deviceName: device.DeviceName,      //设备名称
remote_max_resolution: device.max_resolution, //默认为0
screen_orientation: tm_screen_orientation// 接收端横竖屏状态:0:横屏  1:竖屏
          };
console.log("start cast session ip="+device.DeviceIPList[0])
// 音频控制(在初始化后,投屏前设置)
BJCast.AudioControl(0); //0: 关闭声音 1:开启声音
BJCast.StartBJCastSession(params,
this.on_session_end_cb,
this.on_start_session_result_cb,
this.on_session_update_cb
          );
        }, this.on_probe_callback_err);
    } else {
console.log(`init error: ${this.result}`)
    }
  }
on_session_end_cb= (reason: number) => {
console.log(`Session ended with reason: ${reason}`);
if (reason==0||reason==2||reason==-17||reason==-31) {
this.onCreateStartCastSession=0;
this.onCreateIsFullCast=0
    }
  }
on_start_session_result_cb= (reason: number) => {
console.log(`Session notify with reason: ${reason}`);
if (reason==0) {
this.onCreateStartCastSession=1;
    }
elseif(reason==-16)
    {
constnode: FrameNode |null=this.getUIContext().getFrameNodeById("test_text") ||
null;
this.uiContext.getPromptAction().openCustomDialog({
builder: () => {
this.pinCodeDialogComponent(this.uiContext);
        },
levelMode: LevelMode.EMBEDDED, // 启用页面级弹出框
levelUniqueId: node?.getUniqueId(), // 设置页面级弹出框所在页面的任意节点ID
immersiveMode: ImmersiveMode.EXTEND, // 设置页面级弹出框蒙层的显示模式
autoCancel: false
      }).then((dialogId: number) => {
this.showPinDialog=dialogId;
      })
    }
elseif(reason==-7)
    {
//请求超时,自动关闭PIN码输入对话框
this.uiContext.getPromptAction().closeCustomDialog(this.showPinDialog);
    }
  }
on_session_update_cb= (reason: number) => {
console.log(`Session update with reason: ${reason}`);
if (reason==0) {
this.onCreateIsFullCast=1
    } elseif (reason==1) {
this.onCreateIsFullCast=2
    }
  }
```

## **4 如何使用SDK** 

### **4.1 集成SDK简要说明** 

##### 1. **导入SDK** 

导入 **hm_bjcast.har** ,在 **app** 目录下新建 **libs** 目录,并将 **hm_bjcast.har** 文件放在该目录下,然后在 **ohpackage.json5** 文件中的 **dependencies** 字段中添加如下代码: 

```
"dependencies": {
"hm_bjcast": "./libs/hm_bjcast.har"
}
```

##### 2. **使用SDK** 

在前端页面使用SDK时,需要导入 **hm_bjcast** 中的 **BJCast** 

##### **示例代码:** 

```
// 导入SDK中的方法集
import { BJCast } from'hm_bjcast';
// 初始化参数结构体
interfaceBJCastSenderInitPara {
sender_id: string;
user_name: string;
}
// 设置初始化参数
letinitParams: BJCastSenderInitPara = {
channel_id: 0,           // SDK channel_id,由我司提供
channel_code: "",        // SDK channel_code,由我司提供
sender_id: "sender123",  // 由应用层随机生成,需保证唯一性
user_name: "user123456", // 用户自定义
encoder_scene_conf: "",  // 传入场景配置字符串 =>
JSON.stringify(encoder_scene_conf.scene_define[2])
encoder_ext_conf: ""
};
// 使用BJCast中的Init方法
BJCast.Init(initParams);
```

##### 3. **SDK开发环境:** 

鸿蒙开发工具: **DevEco Studio 5.0.0** , **SDK/API Version: 12** 

##### 4. **SDK使用所需权限** 

在使用SDK时,项目工程需要在 **module.json5** 文件中配置相关权限: 

```
// 网络权限, 后台运行权限
"requestPermissions": [
   {
"name": "ohos.permission.INTERNET",   // 网络权限
   },
   {
"name": "ohos.permission.KEEP_BACKGROUND_RUNNING"//后台运行权限
   }
]
```
