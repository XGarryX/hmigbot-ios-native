# 乐播投屏SDK 

## 简介 

乐播投屏 SDK 是一套高效稳定的投屏解决方案,已覆盖 5 亿台智能电视,让开发者快速获得投屏能力。支持视频、音频、直播等内容投屏,提供推送与镜 像、播控等功能,满足从娱乐到办公的各种场景需求。集成便捷,专业支持,打造无缝跨屏体验 

## 下载安装 

``` ohpm install @lebo/lelink-sdk ``` 

```

## 权限 

``` // sdk 已经内置,可以不用重复申请 ohos.permission.INTERNET ohos.permission.GET_NETWORK_INFO ohos.permission.GET_WIFI_INFO ohos.permission.STORE_PERSISTENT_DATA 

``` 

## 接口 

1. 初始化 lelink.initial(LelinkSourceSDKOptions) 

``` interface LelinkSourceSDKOptions { /** * 是否开启 debug 模式 */ debug?: boolean, /** * UIAbilityContext */ context: Context, /** 

* 应用申请的 appID */ appID: string, /** * 应用申请的 appSecret */ appSecret: string, /** * 设备唯一号,开通 license 授权时需要传递。 */ licenseSerialNumber?: string, } ``` 

2. 应用鉴权 lelink.authorize() 3. 设备发现 

``` 

// 设备发现结果监听 lelink.on('devices-find', this.deviceFindEvent) //开启设备发现 supportDLNA:boolean 是否支持dlna lelink.emit('start-device-browser', ${supportDLNA}) // 关闭设备发现 lelink.emit('stop-device-browser') ``` 

# 4. 设备连接/断开 lelink.emit($by,$args) 

| 连接方法  $by         | 参数类型  $args       | 解释     | |-------------------|-------------------|--------| | connect-by-device | LelinkServiceInfo | 设备连接   | | connect-by-qr     | string            | 二维码连接  | | connect-by-pin    | string            | pin码连接 | | disconnect        | LelinkServiceInfo | 断开连接   | 

5. 镜像 lelink.emit('start-mirror',LelinkServiceInfo) 

6. 推送 lelink.emit('push',LelinkPlayerInfo) 

| 播控     | 参数类型              | 解释      | 

|--------|-------------------|---------| 

| pause  | LelinkServiceInfo | 暂停      | | stop   | PlayerStopPayload | 停止      | | resume | LelinkServiceInfo | 从暂停恢复播放 |
