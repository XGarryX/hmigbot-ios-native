> 来源: ohpm 中央仓 README(T1 信源) | 包: `@tinet/ticloud_rtc` | ohpm 最新版: 1.0.3 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# TiCloudRTC SDK

## 简介
欢迎使用"AICC"的 TiCloudRTC 外呼功能。我们提供在安卓、iOS、鸿蒙Next原生开发中对接外呼(不包含uniapp框架对接),支持企微、微信平台跳转小程序外呼,可以在您的App及小程序中快速对接并实现拨打电话的能力。

## 安装

```typescript
ohpm install @tinet/ticloud_rtc
```

## 快速开始

### 1. 引入所需模块

```typescript
import { 
  TiCloudRTC, 
  CreateClientOption, 
  CallOption
} from '@tinet/ticloud_rtc'
```

### 2. 初始化 SDK

```typescript
// 创建配置选项
let createClientOption = new CreateClientOption()
createClientOption.rtcEndpoint = "YOUR_RTC_ENDPOINT"   // RTC服务地址
createClientOption.enterpriseId = "YOUR_ENTERPRISE_ID" // 企业ID
createClientOption.userId = "YOUR_USER_ID"             // 用户ID
createClientOption.accessToken = "YOUR_ACCESS_TOKEN"   // 访问令牌
createClientOption.advancedConnectConfig = new Map()   // 高级配置
createClientOption.context = context                   // 上下文,使用ability或者component的context
createClientOption.debug = true                        // 是否开启调试模式

// 初始化引擎
TiCloudRTC.shared.CreateEngine(createClientOption, {
  onSuccess: () => {
    console.info('引擎初始化成功');
  },
  onFailed: (errorCode: number, errorMessage: string) => {
    console.error('引擎初始化失败:', errorMessage);
  }
});
```

### 3. 设置事件监听

```typescript
// 实现 TiCloudRTCEventListener 接口
class MyEventListener implements TiCloudRTCEventListener {
  onError?(errorCode: number, errorMessage: string): void {
    console.error('发生错误:', errorMessage);
  }
  
  onCallingStart?(requestUniqueId: string): void {
    console.info('开始呼叫:', requestUniqueId);
  }
  
  onRinging?(): void {
    console.info('正在振铃');
  }
  
  onCalling?(): void {
    console.info('通话进行中');
  }
  
  // ... 实现其他需要的回调方法
}

// 设置事件监听
TiCloudRTC.shared.setEventListener(new MyEventListener());
```

### 4. 发起呼叫

```typescript
let callOption = new CallOption();
callOption.tel = "PHONE_NUMBER"      // 被叫号码
callOption.type = 6                  // 呼叫类型
callOption.clid = "DISPLAY_NUMBER"   // 外显号码

TiCloudRTC.shared.call(callOption);
```

### 5. 通话控制

```typescript
// 挂断通话
TiCloudRTC.shared.hangup();

// 控制扬声器
TiCloudRTC.shared.setEnableSpeakerphone(true);  // 开启扬声器
TiCloudRTC.shared.setEnableSpeakerphone(false); // 关闭扬声器

// 控制麦克风
TiCloudRTC.shared.setMicrophoneMute(true);  // 静音
TiCloudRTC.shared.setMicrophoneMute(false); // 取消静音
```

### 6. 回呼处理

```typescript
// 接受回呼
TiCloudRTC.shared.acceptCall();

// 拒绝回呼
TiCloudRTC.shared.refuseCall();
```

### 7. Token 相关操作

```typescript
// 更新 AccessToken
TiCloudRTC.shared.renewAccessToken("NEW_ACCESS_TOKEN");
```

### 8. 其他功能

```typescript
// 发送 DTMF 按键信号
TiCloudRTC.shared.dtmf("1234");

// 获取 SDK 版本号
const version = await TiCloudRTC.shared.getVersion();
```

## 事件监听说明

TiCloudRTCEventListener 接口提供以下回调方法:

- `onError`: 错误信息回调
- `onCallingStart`: 开始外呼回调
- `onRinging`: 振铃回调
- `onCallCancelled`: 呼叫取消回调
- `onCallRefused`: 呼叫被拒绝回调
- `onCalling`: 通话中回调
- `onLocalHangup`: 本地挂断回调
- `onRemoteHangup`: 远端挂断回调
- `onCallingEnd`: 通话结束回调
- `onCallFailure`: 呼叫失败回调
- `onAccessTokenWillExpire`: Token 即将过期回调
- `onAccessTokenHasExpired`: Token 已过期回调
- `networkQuality`: 本地网络质量回调
- `networkQualityWithUid`: 通话质量回调

## 注意事项

1. 使用前请确保已获取必要的权限(如麦克风权限)
2. 建议在应用启动时进行 SDK 初始化
3. 请妥善保管 AccessToken,并注意及时更新
4. 在通话结束后及时释放资源
5. 注意处理网络状态变化和错误情况

## 错误码说明

常见错误码:
- 10000: SDK未初始化
- 10001: 网络异常
- 12000: 不支持的呼叫场景
- 12001: 呼叫参数错误
- 12002: 呼叫重复
- 12007: 无音频采集权限

更多错误码请参考 `TiCloudRtcErrorCode` 类的定义。

## 更多信息
详细使用可以参考[官方集成网站](https://develop.clink.cn/develop/mobile/rtc-mobile.html)
