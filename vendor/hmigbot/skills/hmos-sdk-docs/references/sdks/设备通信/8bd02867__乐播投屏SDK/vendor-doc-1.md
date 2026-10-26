> 来源: 厂商官方文档页(T2 信源) | https://cloud.lebo.cn/document/8a10384bcfe1e565.html | 抓取: 2026-07-17
> 注意: 单页快照,站内其余页面见来源链接

* 首页 

  * 产品功能 

发送投屏SDK 

接收投屏SDK 

  * 解决方案 

会议室解决方案 

酒店解决方案 

  * 开发者支持 

文档中心 

下载中心 

注册 

登录控制台

文档中心 下载中心

发送端-推送SDK 

产品

[ 发送端-推送SDK ](/document/69376a7f44395ce2.html)[ 发送端-镜像SDK ](/document/9790727bb205722e.html)[ 接收端SDK ](/document/70c0a1c537e4fe69.html)

其他说明

[ OpenAPI ](/document/fa80f880af0eaa13.html)[ 控制台说明 ](/document/2c41121f19af6334.html)[ 资料库 ](/document/1da6c33c7813dd4f.html)

  * 产品介绍 __

    * 产品概述 

    * 价值优势 

    * 功能介绍 

  * 快速开始 __

    * 跑通示例代码 __

      * Android 

      * iOS 

    * SDK集成 __

      * Android 

      * HarmonyOS 

      * iOS 

    * License 认证 __

      * Android 

      * HarmonyOS 

      * iOS 

  * 合规指南 __

    * 数据采集说明 __

      * Android-发送端 

      * Android-接收端 

      * iOS-发送端 

      * HarmonyOS-发送端 

    * 权限说明 __

      * Android-发送端 

      * Android-接收端 

      * iOS-发送端 

      * HarmonyOS-发送端 

    * 隐私政策 __

      * 2024-03-05 隐私政策 

      * 2023-04-25 隐私政策 

      * 2024-11-08 隐私政策 

      * 2025-02-24 隐私政策 

      * 2025-12-03 隐私政策 

      * 2026-03-11 隐私政策 

      * 2026-05-26 隐私政策 

      * 2026-06-30 隐私政策 

    * 第三方合规接入指引 

    * 个人信息处理规则 

    * 用户协议 

    * 软件许可与服务协议 

  * 有 UI 推送投屏 __

    * Android 

    * iOS 

  * 无 UI 推送投屏 __

    * 搜索和连接 __

      * Android 

      * HarmonyOS 

      * iOS 

    * 视频推送 __

      * Android 

      * HarmonyOS 

      * iOS 

  * 进阶功能 __

    * 日志上报 __

      * Android 

      * iOS 

    * 推送列表 __

      * Android 

      * iOS 

    * 扫码、pin码获取服务 __

      * Android 

      * HarmonyOS 

      * iOS 

    * 收藏设备和历史设备 __

      * Android 

      * iOS 

  * API __

    * Android 

    * iOS 

  * 更新日志 __

    * Android 

    * HarmonyOS 

    * iOS 

  * 错误码 __

    * Android 

    * iOS 

  * 常见问题 __

    * 投屏引导 

    * 常见问题 

    * 注意事项 

    * 播放器格式参考 

    * 问题分析参考 

  * 合规指南 __

    * 隐私政策 

发送端-推送SDK  快速开始  SDK集成  HarmonyOS 

# # SDK集成(HarmonyOS)

**这里主要指导您如何将乐播sdk集成到您的项目中并且能够顺利调用乐播sdk提供的api接口**

集成投屏SDK您只需要简单的两步:

  * 一 SDK导入及配置
  * 二 SDK初始化

## # 1\. SDK导入及配置

### # 1.1 导入SDK

  * 请将har导入到工程中的libs中

  * 然后在`entry/oh-package.json5` 中添加以下配置

    
    
    "dependencies": {
      "@lebo/lelink-sdk": "file:../libs/lelink-sdk.har"
    }
    

接下来,您就可以调用我们的api了

### # 1.2 配置权限

以下为投屏SDK需要的权限,har包自带有,无需再次配置
    
    
    // sdk 已经内置,可以不用重复申请
    ohos.permission.INTERNET
    ohos.permission.GET_NETWORK_INFO
    ohos.permission.GET_WIFI_INFO
    ohos.permission.STORE_PERSISTENT_DATA
    
    // 需要在依赖 lelink-sdk 的模块的 module.json5 中添加
    ohos.permission.MICROPHONE
    ohos.permission.KEEP_BACKGROUND_RUNNING // keep-alive
    ohos.permission.CAMERA
    

### # 1.3 配置 keep-alive

> 镜像时需要保活
> 
> entry/src/man/module.json5
    
    
    {
      "module":{
        "abilities": [
          {
           "name": "EntryAbility",
           // ...
           "backgroundModes":["audioRecording"]
         }
        ]
      }
    }
    

### # 1.4 其他配置

由于 lelink-sdk 含字节码的HAR,所以项目级`build-profile.json5` 配置 "useNormalizedOHMUrl": true
    
    
    {
      "app":{
            "products": [
          {
            "name": "default",
            "signingConfig": "default",
            "compatibleSdkVersion": "5.0.0(12)",
            "runtimeOS": "HarmonyOS",
            "buildOption": {
              "strictMode": {
                "useNormalizedOHMUrl": true // 必须配置,否则构建会失败
              }
            }
          }
        ],
      }
    }
    

## # 2\. SDK初始化

> 关于AppId & AppSecret 的获取,请参考[控制台说明 (opens new window)](https://cloud.lebo.cn/document/8911c7547bfcba36.html)
    
    
      //最好是放到EntryAbility#onCreate()
    
      let appID:string='${appID}' // 应用申请的appID
      let appSecret:string='${appSecret}' // 应用申请的appSecret
      lelink.initial({
           context: this.context,
           appID: "your appID",
           appSecret: "your appSecret",
           licenseSerialNumber:"your license serial number"
          })
    

**SDK 初始化需要传入 1 个参数,包含以下几个字段:**
    
    
    interface LelinkSourceSDKOptions {
      /**
      * 是否开启 debug 模式
      */
      debug?: boolean,
      /**
      * UIAbilityContext
      */
      context: Context,
      /**
      * 应用申请的 appID
      */
      appID: string,
      /**
      * 应用申请的 appSecret
      */
      appSecret: string,
      /**
       * 设备唯一号,开通 license 授权时需要传递。
       */
      licenseSerialNumber?: string,
    }
    

  * context:应用程序的 context
  * appID:在开发者中心申请的 AppID
  * appSecret:在开发者中心申请的 AppSecret
  * licenseSerialNumber: 由开发者自主生成,确保唯一性。
