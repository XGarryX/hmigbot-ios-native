> 来源: 厂商官方文档页(T2 信源,浏览器渲染抓取) | https://www.volcengine.com/docs/6431/1256322 | 抓取: 2026-07-17
> 注意: 该站正文为 JS 渲染,requests 只能拿到导航壳;本页为渲染后正文快照。深层页面(验证数据上报/使用指南/API 接口)见站内导航,按 online-lookup 浏览器渲染现场取

# 应用接入 Harmony SDK

本文介绍 Harmony SDK 的详细接入步骤。接入 SDK 后,即可在应用性能监控全链路版平台上使用相关分析功能。

## 注意事项

- Harmony SDK 目前仅限在中国大陆应用使用(不包括港澳台地区)。
- 调用 SDK 初始化接口不会采集用户信息,调用 SDK 启动接口会开始采集用户信息,请确保采集用户信息之前已经获得用户授权 SDK 隐私政策。

## Demo 说明

- Demo(APMPlus_Harmony)已经接入了所有 ApmPlus 的性能和稳定性监控的能力。
- 可以通过 Demo 模拟一些异常和性能数据;可以配置成自己的 AppID 和 AppToken,将数据上报到平台,进行 SDK 功能测试。

## 步骤一:创建产品

在火山引擎平台注册账号,然后在客户端监控控制台创建应用(参见"接入客户端应用")。创建完成后可以在平台看到 AppID、AppToken。产品创建后需要购买事件才可在平台查看上报数据;可联系在线客服提供 AppID 申请免费试用额度。

## 步骤二:获取 SDK 包,引入依赖

自动集成(推荐),通过 ohpm 安装 APMPlus SDK:

```shell
ohpm i @volcengine/apmplus@2.0.6
```

手动集成:通过三方仓库或在线客服获取 har 包,拷贝到工程(如 entry/libs),在主入口 module 的 oh-package.json5 添加离线 har 包依赖:

```json
"dependencies": {
    "@volcengine/apmplus": "file:./libs/apmplus.har"
}
```

## 步骤三:初始化 SDK 并开启监控

初始化 SDK 阶段不获取用户个人信息。在 AbilityStage 或者 Ability 的 onCreate 生命周期中添加:

```arkts
APMPlus.init(this.context);
```

启动监控,开始收集数据(**请在用户同意隐私政策后再调用**):

```arkts
APMPlus.setDeviceId("device_id");//可选,设置设备device_id,不设置会使用内部默认device_id,更新值随时调用
APMPlus.setUserId("user_id");//可选,用户标识,没有默认值,更新值随时调用

let builder = new APMPlusBuilder("AppID", "AppToken");//必填
builder.debug = true;//可选,测试阶段配置有输出日志,线上release需关闭
builder.channel = "volcengine";//可选,类型string。渠道
builder.startMonitor = true;//可选,是否开启启动监控
builder.netMonitor = true;//可选,是否开启网络监控 后续需要使用HttpMonitor进行辅助监控
builder.logRecovery = true;//可选,是否开启自定义Vlog打点回捞能力

APMPlus.start(builder);
```

说明:
- AppID 和 AppToken 获取方法参见"如何查询 AppID 和 AppToken"。
- Har 包为二进制 abc 格式。工程级 build-profile.json5 需设置 useNormalizedOHMUrl 为 true:

```json
{
  "app": {
    "products": [
      {
         "buildOption": {
           "strictMode": {
             "useNormalizedOHMUrl": true
           }
         }
      }
    ]
  }
}
```

## 步骤四:上传符号表(可选)

工程 ./hvigor/hvigor-config.json5 文件添加依赖:

```json
"dependencies": {
  "apmplus_upload": 'latest',
}
```

工程的 hvigorfile.ts 添加以下代码:

```arkts
import { ApmPlusPlugin } from 'apmplus_upload';

const config = {
    aid : 1234, // 应用的app id
    updateVersionCode : 1000000, // 应用的number类型的版本号version_code
    api_key : 4321,// 平台 全部功能->符号表管理->系统选择 Harmony 下可见 api key
    api_token : 'xxxxxx'// 同上可见 api token
};

export default {
    system: appTasks,
    plugins:[ApmPlusPlugin(config)]
}
```

(文档最近更新时间: 2026-02-10)
