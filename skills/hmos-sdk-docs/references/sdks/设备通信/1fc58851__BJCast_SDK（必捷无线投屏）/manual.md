# **BJCast** **SDK(必捷无线投屏)** 

**version V1.0.9 platform HarmonyOS NEXT license Apache-2.0** 

Apache-2.0

## 📖 **简介** 

BJCast SDK(必捷无线投屏)是一款专为 HarmonyOS NEXT 系统设计的无线投屏发送端 SDK。该 SDK 提供了完整的 音视频流编码发送能力,支持开发者快速集成无线投屏功能到自己的应用中。 

### **核心功能** 

- ✅ **音视频流编码发送** :高效编码设备屏幕内容和音频,通过网络实时传输 

- ✅ **接收端自动发现** :自动探测局域网内的投屏接收端设备 

- ✅ **投屏会话管理** :完整的会话建立、维护和结束流程 

- ✅ **投屏控制** :支持全屏控制、音频控制、投屏质量调节 

- ✅ **PIN 码认证** :支持投屏密码验证,保障投屏安全 

- ✅ **多分辨率适配** :支持 1080P、2K、4K 等多种分辨率 

- ✅ **低延迟传输** :优化的传输协议,实现低延迟投屏体验 

## 🚀 **快速开始** 

### **环境要求** 

DevEco Studio 5.0.0 及以上版本 

- HarmonyOS NEXT SDK/API Version 12 及以上 

- ohpm 1.0.0 及以上版本 

### **安装 SDK** 

#### **方式一:通过 OHPM 安装(推荐)** 

在项目的 `oh-package.json5` 中添加依赖: 

```
{
```

- `"dependencies": {` 

```
"com.bjnetworks.bjcastsender": "^1.0.9"
  }
}
```

然后执行: 

```
ohpm install
```

#### **方式二:本地 HAR 包安装** 

1. 下载 `hm_bjcast.har` 文件 

2. 将 HAR 包放入项目的 `libs` 目录 

3. 在 `oh-package.json5` 中添加: 

```
{
"dependencies": {
"hm_bjcast": "./libs/hm_bjcast.har"
  }
}
```

### **配置权限** 

在 `module.json5` 中添加以下权限: 

```
"requestPermissions": [
  {
"name": "ohos.permission.INTERNET"
  },
  {
"name": "ohos.permission.KEEP_BACKGROUND_RUNNING"
  }
]
```

### **代码示例** 

#### **1. 导入 SDK** 

```
import { BJCast } from'hm_bjcast';
```

#### **2. 初始化 SDK** 

```
import { BJCast } from'hm_bjcast';
// 初始化参数
letinitParams= {
channel_id: 0,              // SDK channel_id,由必捷网络提供
channel_code: "",           // SDK channel_code,由必捷网络提供
sender_id: "sender123",     // 发射端 ID,需保证唯一性
user_name: "user123456",    // 用户自定义名称
encoder_scene_conf: "",     // 投屏质量场景配置(可选)
encoder_ext_conf: ""// 额外配置参数(可选)
};
// 初始化 SDK
letresult=BJCast.Init(initParams);
if (result===0) {
"
console.log("SDK 初始化成功);
} else {
"
console.error("SDK 初始化失败,错误码:+result);
}
```

#### **3. 探测接收端设备** 

```
// 探测接收端
BJCast.Probe(
"192.168.1.100",  // 接收端 IP 地址
  (res) => {
// 探测成功回调
""
console.log(探测成功:+JSON.stringify(res));
letdevice=JSON.parse(JSON.stringify(res));
// 开始投屏
startCastSession(device);
  },
  (err) => {
// 探测失败回调
""
console.error(探测失败:+JSON.stringify(err));
  }
);
```

#### **4. 开始投屏** 

```
// 投屏参数
letcastParams= {
ipaddress: device.DeviceIPList[0],      // 接收端 IP
port: 8190,                              // 端口号
pin: "",                                 // 投屏密码(无密码填空字符串)
ft: device.ft,                           // ft 值
deviceName: device.DeviceName,           // 设备名称
remote_max_resolution: device.max_resolution,  // 最大分辨率
screen_orientation: device.screen_orientation// 横竖屏状态
};
// 开始投屏
BJCast.StartBJCastSession(
castParams,
on_session_end_cb,           // 结束投屏回调
on_start_session_result_cb,  // 开始投屏结果回调
on_session_update_cb// 投屏更新回调
);
```

#### **5. 回调函数处理** 

```
// 结束投屏回调
leton_session_end_cb= (reason: number) => {
""
console.log(投屏结束,原因:+reason);
// reason: 0-正常退出,2-被踢出,-17-心跳丢失,-31-网络切换
};
// 开始投屏结果回调
leton_start_session_result_cb= (reason: number) => {
""
console.log(投屏结果:+reason);
// reason: 0-成功,-6-网络异常,-7-超时,-14-被拒绝,-15-投屏已满,-16-PIN 码错误
};
// 投屏更新回调
leton_session_update_cb= (reason: number) => {
""
console.log(投屏更新:+reason);
// reason: 0-请求全屏成功,1-退出全屏成功
};
```

#### **6. 结束投屏** 

```
// 结束投屏
BJCast.StopBJCastSession();
```

#### **7. 音频控制(可选)** 

```
// 0-关闭声音,1-开启声音
BJCast.AudioControl(1);
```

#### **8. PIN 码校验(如需要)** 

```
// PIN 码错误时调用
BJCast.ReAuth("123456");
```

## 📚 **API 文档** 

详细 API 文档请参考:BJCast 发射端 SDK 接口文档_Harmony 平台.md 

### **主要接口列表** 

|**接口名称**|**功能描述**|
|---|---|
|`BJCast.Init()`|初始化SDK|
|`BJCast.Probe()`|探测接收端设备|
|`BJCast.StartBJCastSession()`|开始投屏|
|`BJCast.StopBJCastSession()`|结束投屏|
|`BJCast.RequestFullScreen()`|请求全屏控制|
|`BJCast.ExistFullScreen()`|退出全屏控制|
|`BJCast.AudioControl()`|音频控制|

|**接口名称**|**功能描述**|
|---|---|
|`BJCast.SetEncoderSceneConfig()`|设置投屏质量场景配置|
|`BJCast.ReAuth()`|PIN码校验|

## 🔧 **高级配置** 

### **投屏质量场景配置** 

```
letencoder_scene_conf= {
"scene_define": [
    {
"scene_name": "高清模式",
"scene_id": 0,
"scene_encoder_config": [
        {
"codec": 1,
"width": 1920,
"height": 1080,
"bitrate": 4000,
"framerate": 60,
"qmin": -1,
"qmax": -1
        }
      ]
    }
  ]
};
BJCast.SetEncoderSceneConfig(JSON.stringify(encoder_scene_conf.scene_define[0]));
```

## ⚠ **注意事项** 

1. **录屏权限** :首次投屏需要用户授权录屏权限 

2. **本地录屏中断** :投屏时本地录屏会断开,这是 HarmonyOS NEXT 系统的正常行为 

3. **网络要求** :确保发射端和接收端在同一局域网内 

4. **唯一性要求** :sender_id 需保证全局唯一性 

5. **PIN 码处理** :无密码投屏时 pin 参数填空字符串"",不可填 null 

## 📄 **相关文档** 

合规使用说明 

隐私政策 

接口文档 

CHANGELOG 

LICENSE 

## 🔗 **相关链接** 

必捷网络官网 

HarmonyOS 开发者文档 

OHPM 中心仓 

操作演示视频 

## 📮 **联系我们** 

如有任何问题或建议,请通过以下方式联系我们: 

- **邮箱** : marketing@bijienetworks.com 

- **官网** : https://www.bijienetworks.com/ 

- **地址** : 苏州市相城区泰元路 100 号 宏能永乐科技园 2 楼 232 号 

## 📝 **许可证** 

本项目采用 Apache-2.0 许可证,详见 LICENSE 文件。 

**苏州必捷网络有限公司 Copyright © 2026**
