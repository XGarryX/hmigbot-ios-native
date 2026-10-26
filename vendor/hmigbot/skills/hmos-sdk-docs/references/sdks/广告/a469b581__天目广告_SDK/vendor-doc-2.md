> 来源: 厂商官方文档页(T2 信源) | https://doc.admobile.top/ssp/pages/tianmu_compliance/ | 抓取: 2026-07-17
> 注意: 单页快照,站内其余页面见来源链接

# # 【重要】天目Ads SDK合规使用指南

**尊敬的开发者,您好!** 为帮助使用天目广告 SDK的开发者和运营者(以下简称“您”)在符合相关法律法规、政策及标准的规定下开展第三方SDK业务,更好地落实用户个人信息保护相关要求,特别是保护个人信息和隐私的方法和措施。为了保证您的App顺利通过检测,结合当前监管关注重点,我们制作了广告SDK初始化合规规范。

## # 一、接入/升级至满足监管新规的最新SDK版本

我们高度重视SDK的功能优化、个人信息安全和保护,将适时升级迭代SDK版本以提升产品的安全性和稳定性,确保符合相关法律法规及、监管及标准的最新合规要求。强烈建议您升级使用最新版本SDK,以便保障您正常使用SDK最新功能、避免因您更新不及时产生的不利影响(例如APP被通报或下架等)。 SDK的获取地址如下:

SDK名称| 仓库地址| 安装方法  
---|---|---  
天目Ads SDK - Android| <https://gitee.com/admobile/tianmu-advertising-sdk-android>| 参见《README》  
天目Ads SDK - iOS| <https://gitee.com/admobile/tianmu-advertising-sdk-ios>| 参见《README》  
天目Ads SDK - Harmony| <https://ohpm.openharmony.cn/#/cn/detail/@admobile%2Ftianmu>| ohpm i @admobile/tianmu  
  
## # 二、APP隐私政策中应披露天目Ads SDK相关情况

确保您开发或运营的应用制定符合**监管要求的《隐私政策》** 文本。请务必明确告知终端用户您的App集成了天目Ads SDK服务。  
请您在《隐私政策》添加关于本SDK收集使用个人信息的目的、方式和范围等,和本SDK的开发运营者名称及隐私政策链接。

您应在**APP 登录注册页面及 APP 首次运行** 时,通过**简洁明显且易于访问的方式告知用户《隐私政策》** , 向最终用户告知个人信息处理主体、处理目的、处理方式、处理类型、保存期限等内容的个人信息处理规则,并且获得最终用户授权同意后才能处置用户数据。隐私政策弹窗应提供同意按钮和拒绝同意的按钮,并由最终用户主动选择。我们提供告知文案示例供您参考,您可以通过文字或表格方式向用户告知。

  1. 将天目Ads SDK的名称、公司名称、处理个人信息种类及目的、采集方式和范围、隐私政策链接等内容进行披露。

SDK名称| 所属公司| 使用目的及功能场景| 个人信息字段与类型| SDK隐私政策  
---|---|---|---|---  
天目Ads SDK| 杭州艾狄墨搏信息服务有限公司| 广告投放及监测归因、反作弊、统计分析、减少APP崩溃、提供可靠稳定的服务| 必选信息:  
设备信息(设备品牌、设备型号、设备名称、操作系统名称、操作系统版本、屏幕密度、屏幕分辨率、设备语言、sim卡信息(mcc&mnc)、sim卡状态、CPU信息、可用存储空间大小、内存空间、磁盘总空间、手机系统重启时间、电量,iOS如IDFV、系统更新时间、磁盘信息、设备类型、设备时区)  
应用信息(开发者应用名、应用包名、应用版本号、应用前后台状态、UserAgent(UA))  
网络信息(运营商信息、网络状态、Wi-Fi状态)  
广告信息(对广告的展示、点击及转化等交互数据)  
性能数据(如崩溃数据、性能数据)  
可选信息:  
设备信息(设备标识符(如OAID、IDFA))  
应用信息(软件列表信息)  
网络信息(IP地址)  
位置信息(**精确位置信息** 、粗略位置信息)  
传感器信息(加速度传感器、陀螺仪传感器、线性加速度传感器、磁场传感器、旋转矢量传感器、方向传感器)| [艾狄墨搏隐私政策](https://www.admobile.top/privacyPolicy.html)  
  
请您理解SDK不同版本提供的功能服务及所需的字段信息可能会因开发者的选择或配置不同而存在差异,因此请您参考SDK隐私政策及您实际接入使用的SDK运行情况向用户进行充分告知并获得用户的同意。

  2. 《隐私政策》的“第三方信息共享清单”或类似章节中中增加如下参考条款:

> “我们与第三方 SDK 类服务商共享个人数据:**我们相关服务或产品中可能会包含第三方SDK或其他类似的应用程序,如您在我们平台上使用这类由第三方提供的服务或产品时,您同意将由其直接收集和处理您的信息(如以嵌入代码、插件等形式)。前述服务商收集和处理信息等行为遵守其自身的隐私条款,而不适用于本隐私政策。但我们也会努力审查该第三方的业务准入资质并努力要求该服务商的合法合规性与安全性。为了最大程度保障您的信息安全,我们强烈建议您在使用任何第三方SDK类服务前先行查看其隐私条款。为保障您的合法权益,如您发现这等SDK或其他类似的应用程序存在风险时,建议您立即终止相关操作并及时与我们取得联系。**

## # 三、获得用户同意后再初始化SDK

为满足法律法规及监管要求,您应确保在获得用户的同意后再初始化天目Ads SDK,并在用户触发SDK具体功能服务后通过配置SDK的相关参数完成发送请求的调用,此时SDK才会按照您设置的配置方式采集功能所需的个人信息或申请功能所需的权限。注意事项如下

  1. 天目Ads SDK的初始化请在**用户同意App隐私政策** /声明后进行,并在隐私政策中披露接入天目Ads SDK的情况。如果用户**不同意** 《隐私政策》授权,则**不能调用初始化** 接口。
  2. 请不要在用户同意隐私政策之前动态申请涉及用户信息的敏感设备权限。
  3. 请不要在用户同意隐私政策之前私自采集和上报用户信息(尤其注意Android_ID、MAC地址、硬件序列号、应用安装列表等用户信息)。
  4. 《隐私政策》应由用户**自主选择是否同意** ,不应以默认勾选同意的方式或是以欺骗诱导的方式取得用户授权。

## # 四、可选信息配置开关

天目Ads SDK向您提供了可选个人信息及权限的控制开关,您可以根据APP所需的SDK功能服务自行配置打开或关闭隐私信息请求开关。

  1. SDK可选个人信息的配置说明 请您注意,SDK不强制获取可选权限,即使没有获取可选权限,SDK提供的基本功能也能正常运行。您可以配置可选权限,以便使用SDK提供的其他可选功能。建议调用请求前在合适的时机调用SDK提供的方法,在用户授权的情况下获取声明中的权限。点击以下链接查看详细操作指引:

Android: <https://doc.admobile.top/ssp/pages/tmsdkand/>[在新窗口打开](https://doc.admobile.top/ssp/pages/tmsdkand/)

iOS: <https://doc.admobile.top/ssp/pages/tmsdkios/>[在新窗口打开](https://doc.admobile.top/ssp/pages/tmsdkios/)

Harmony: <https://doc.admobile.top/ssp/pages/tmsdkhm/>[在新窗口打开](https://doc.admobile.top/ssp/pages/tmsdkhm/)

可选个人信息类型|  字段| 用途和目的| 使用场景  
---|---|---|---  
设备信息| 【Android、Harmony】设备标识符(OAID)  
【仅iOS】设备标识符(如IDFA)| 广告投放及广告反作弊|  在进行广告投放和广告投放效果分析时使用  
应用信息| 【仅Android】软件列表信息| 广告投放及广告反作弊  
网络信息| 【Android、iOS、Harmony】IP地址| 广告投放及广告反作弊  
位置信息| 【Android、iOS】**精确位置信息** 、  
【Android、iOS、Harmony】粗略位置信息| 广告投放及广告反作弊  
  
  2. SDK申请系统权限的配置说明 为实现天目Ads SDK产品的相应功能,我们可能通过应用开发者的应用申请开启终端用户设备操作系统的特定权限。具体的使用场景和申请目的如下:
  3. Android操作系统应用权限列表:

权限| 功能| 用途和目的| 权限申请时机  
---|---|---|---  
INTERNET| 【必选】允许使用Internet网络| 网络访问| SDK初始化时,开始调用  
READ_PHONE_STATE| 【可选】读取手机设备标识等信息| 广告投放及广告监测归因、反作弊| 请在SDK初始化完成后,开始请求获取广告时  
ACCESS_COARSE_LOCATION| 【可选】获取位置信息| 广告投放及反作弊  
**ACCESS_FINE_LOCATION**  
ACCESS_WIFI_STATE| 【可选】允许应用程序访问有关Wi-Fi 网络的信息| 广告投放及广告监测归因、反作弊  
QUERY_ALL_PACKAGESE| 【可选】获取应用软件列表| 广告投放、反作弊  
REQUEST_INSTALL_PACKAGES| 【可选】获取安装权限| 应用下载广告安装  
ACCESS_NETWORK_STATE| 【可选】获取网络状态| 检测网络状态,SDK 会根据网络状态选择更新广告策略  
ACCESS_WIFI_STATE| 【可选】允许应用程序访问有关Wi-Fi网络的信息| 广告投放及广告监测归因、反作弊  
VIBRATE| 【可选】摇一摇权限| 广告互动   
  
**可选信息配置方式**

相关配置权限可以通过不在配置文件中添加对应的配置内容的方式设置为可不获取,如下为允许获取后在配置文件中添加后的内容:
    
    
    <!-- 广告可选权限,提升广告填充,允许应用检测网络状态,SDK 会根据网络状态选择是否发送数据 -->
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <!-- 广告可选权限,提升广告填充,允许应用获取 MAC 地址。广告投放及广告监测归因、反作弊 -->
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <!-- 广告可选权限,提升广告填充,影响广告填充,强烈建议的权限,获取设备信息,允许应用获取手机状态(包括手机号码、IMEI、IMSI权限等)。广告投放及广告监测归因、反作弊 -->
    <uses-permission android:name="android.permission.READ_PHONE_STATE" />
    <!-- 为了提高广告收益,建议设置的权限,获取精准位置信息,用于广告投放。精准广告投放及反作弊 -->
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <!-- 为了提高广告收益,建议设置的权限,获取粗略位置信息。精准广告投放及反作弊 -->
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    
    <!-- 广告可选权限,摇一摇权限,用于广告互动 -->
    <uses-permission android:name="android.permission.VIBRATE"/>
    

针对部分权限,如上面添加了权限配置,依旧可以使用如下 API 进行主动关闭/开启。 true 为开启,false 为关闭。
    
    
    TianmuSDK.getInstance().init(this, new TianmuInitConfig.Builder()
        ...
        //【慎改】是否同意隐私政策,将禁用一切设备信息读起严重影响收益
        .agreePrivacyStrategy(true)
        // 是否可获取定位数据
        .isCanUseLocation(true)
        // 是否可获取设备信息
        .isCanUsePhoneState(true)
        //是否禁用传感器(可禁用摇一摇、扭一扭)。参数说明:true:禁用,false:启用
        .isSensorDisable(true)
        ...
        .build());
    

详情见可见[对接文档](/ssp/2jieru/11.androidTianmuREADME..html)

  2. iOS操作系统应用权限列表:

权限| 功能| 用途和目的  
---|---|---  
NSAppTransportSecurity| 【可选】添加http权限| http网络请求  
NSLocationWhenInUseUsageDescription| 【可选】仅APP被使用时获取地理位置| 广告投放及广告监测归因、反作弊  
NSLocationAlwaysAndWhenInUseUsageDeion| 【可选】持续获取地理位置| 广告投放及广告监测归因、反作弊  
NSUserTrackingUsageDescription| 【可选】获取设备标识| 广告投放及广告监测归因、反作弊  
  
**可选信息配置方式** :iOS 相关可选权限的配置方式, 只需要在主项目 info.plist 文件中,不配置相关的权限 key 值即可禁止权限的获取。如需要使用需将对应的 key 配置在 info.plist 文件中。

针对 NSUserTrackingUsageDescription 权限,如果开发者配置了,只要开发者不主动调用如下方法,即不使用:
    
    
      [ATTrackingManager requestTrackingAuthorizationWithCompletionHandler:^(ATTrackingManagerAuthorizationStatus status) {
      
      }];
    
      /// 关闭传感器监听
      @property (nonatomic, assign) bool disableMotion;
    

详情可见[对接文档在新窗口打开](//2jieru/12.TianmuREADMEios.md)

  3. Harmony操作系统应用权限列表:

权限名称| 权限说明| 使用目的| 权限申请时机  
---|---|---|---  
ohos.permission.INTERNET| 【必选】允许使用Internet网络| 网络访问| SDK初始化时,开始调用  
ohos.permission.GET_NETWORK_INFO| 【必选】允许应用获取数据网络信息|  用于及时更新广告位配置  
ohos.permission.APP_TRACKING_CONSENT| 【可选】允许应用读取开放匿名设备标识符| 广告投放及广告监测归因、反作弊| 请在SDK初始化完成,开始请求获取广告前  
ohos.permission.APPROXIMATELY_LOCATION| 【可选】允许应用获取设备模糊位置信息| 广告投放及广告监测归因、反作弊  
  
**可选信息配置方式:**

  * ohos.permission.APP_TRACKING_CONSENT 权限:开发者在 module.json 文件中不进行网络权限的 "ohos.permission.APP_TRACKING_CONSENT" 配置即可。如配置并动态获取了开放匿名设备标识符,可通过Tianmu.Sdk.setOaid(oaid: string)方法传入开放匿名设备标识符,不传入则不会使用。
  * ohos.permission.APPROXIMATELY_LOCATION 权限:开发者在 module.json 文件中不进行网络权限的 "ohos.permission.APP_TRACKING_CONSENT" 配置即可,如配置了可通过 isCanReadLocation(b:boolean) 方法关闭/开启

## # 五、 SDK扩展业务功能的配置说明

天目Ads SDK提供的主要扩展业务个性化广告推荐,天目Ads SDK为开发者提供退出个性化广告能力的接口,开发者可以调用接口,向最终用户提供退出个性化广告的能力。退出后,最终用户看到的广告数量不变,相关度会降低。开发者需遵守相关法律法规的要求,在APP内为最终用户提供退出个性化广告的功能,保证在最终用户点击退出功能后调用天目Ads SDK的能力接口。开发者可按照对接文档中提供的方法进行实现关闭退出功能,下面是相关代码:

2.2.1 安卓代码如下:
    
    
    // 设置个性化广告,true:开启、false:关闭
    TianmuSDK.setPersonalizedAds(boolean enablePersonalized);
    

2.2.2 iOS 代码如下;
    
    
    // 是否开启个性化广告;默认YES,建议初始化SDK之前设置
    TianmuSDK.enablePersonalAd = NO;
    

详见可见 SDK 对接文档。
