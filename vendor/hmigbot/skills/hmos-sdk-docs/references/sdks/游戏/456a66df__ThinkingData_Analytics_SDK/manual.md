# 使用指南 

一、设置用户标识 

SDK 实例默认会使用随机 UUID 作为每个用户的默认访客 ID ,该 ID 将会作为用户在未登录状态下身份识别 ID 。需要注意的是,访客 ID 在用户重新安装 App 以及更换设备时将会变更。 

# 1.1 设置访客 ID 

::: tip 提示 

一般情况下,您不需要自定义访客 ID. 请确保已经理解用户识别规 则,再进行访客 ID 的设置。 

如果您需要替换访客 ID ,则应当在初始化 SDK 结束之后立即进行调 用,请勿多次调用,以免产生无用的账号 

::: 

如果您的 App 对每个用户有自己的访客 ID 管理体系,则您可以调用 setDistinctId 来设置访客 ID : 

JavaScript // 将访客 ID 设置为 Thinker TDAnalytics.setDistinctId("Thinker"); 

如果需要获得当前访客 ID ,可以调用 getDistinctId 获取: 

Java // 返回访客 ID let distinctId = TDAnalytics.getDistinctId(); 

# 1.2 设置账号 ID 

在用户进行登录时,可调用 login 来设置用户的账号 ID , TE 平台将 会以账号 ID 作为身份识别 ID ,并且设置的账号 ID 将会在调用 logout 之前一直保留。多次调用 login 将覆盖先前的账号 ID 。 

JavaScript // 用户的登录唯一标识,此数据对应上报数据里的 #account_id ,此时 #account_id 的值为 TA TDAnalytics.login("TA"); 

该方法不会上传登录事件 

# 1.3 清除账号 ID 

在用户产生登出行为之后,可调用 logout 来清除账号 ID ,在下次调 用 login 之前,将会以访客 ID 作为身份识别 ID 。 

Java // 去除上报数据里的 "#account_id" ,之后的数据将不带有 "#account_id" TDAnalytics.logout(); 

我们推荐您在显性的登出事件时调用 logout ,比如用户产生了注销账 号这一行为时才调用,而不需要在关闭 App 时调用。 

该方法不会上传登出事件 

二、发送事件 

在 SDK 初始化完成之后,您就可以进行数据埋点,收集用户的的行 为信息。一般情况下普通事件即可满足业务需求,您也可以根据自己 的实际业务场景使用首次、可更新等事件。 

# 2.1 普通事件 

您可以调用 track 来上传事件,建议您根据先前梳理的文档来设置事 件的属性,此处以用户购买某商品作为范例: 

JavaScript TDAnalytics.track({ eventName: "product_buy", // 事件 名称 properties: { product_name: " 商品名 " } // 事件属性 }); 

# 2.2 首次事件 

首次事件是指针对某个设备或者其他维度的 ID ,只会记录一次的事 件。例如在一些场景下,您可能希望记录在某个设备上的激活事件, 则可以用首次事件来上报数据。 

JavaScript TDAnalytics.trackFirst({ eventName: "device_activation", properties: { key: "value" } }); 

如果您希望以设备以外的其他维度来判断是否首次,则可以为首次事 件自定义 first_check_id: 

JavaScript // 将用户 ID 设置为首次事件的 first_check_id ,实现用户首 次激活事件的采集 TDAnalytics.trackFirst({ eventName: "account_activation", firstCheckId: "TA", properties: { key: "value" } 

# }); 

注意:由于在服务端完成对是否首次的校验,首次事件默认会延时 1 小时入库。 

# 2.3 可更新事件 

您可以通过可更新事件实现特定场景下需要修改事件数据的需求。可 更新事件需要指定标识该事件的 ID ,并在创建可更新事件对象时传 入。 TE 将根据事件名和事件 ID 来确定需要更新的数据。 

JavaScript // 示例: 上报可被更新的事件,假设事件名为 UPDATABLE_EVENT // 上报后事件属性 status 为 3, price 为 100 TDAnalytics.trackUpdate({ eventName: "UPDATABLE_EVENT", properties: { status: 3, price: 100 }, eventId: "test_event_id" }); // 上 报后事件属性 status 被更新为 5, price 不变 TDAnalytics.trackUpdate({ eventName: "UPDATABLE_EVENT", properties: { status: 5 }, eventId: "test_event_id" }); 

# 2.4 可重写事件 

可重写事件与可更新事件类似,区别在于可重写事件会用最新的数据 完全覆盖历史数据,从效果上看相当于删除前一条数据,并入库最新 的数据。 TE 将根据事件名和事件 ID 来确定需要更新的数据。 

JavaScript // 示例: 上报可被重写的事件,假设事件名为 OVERWRITE_EVENT // 上报后事件属性 status 为 3, price 为 100 TDAnalytics.trackOverwrite({ eventName: "OVERWRITE_EVENT", properties: { status: 3, price: 100 }, eventId: "test_event_id" }); // 上 报后事件属性 status 被更新为 5, price 属性被删除 TDAnalytics.trackOverwrite({ eventName: "OVERWRITE_EVENT", properties: { status: 5 }, eventId: "test_event_id" }); 

# 2.5 公共事件属性 

对于一些重要的属性,譬如用户的设备 ID 、来源渠道、用户状态等, 这些属性需要设置在每个事件中,此时您可以将这些属性设置为公共 属性,即每个事件中都带有的属性。我们推荐您在发送事件前,先设 置公共属性。 

# 2.5.1 静态公共事件属性 

对于一些重要的属性,譬如用户的渠道、昵称、 ID 等,这些属性需要 设置在每个事件中,您可以调用 setSuperProperties 来设置静态公共 事件属性,静态公共事件属性会对全局生效。 

JavaScript // 设置公共事件属性,所有数据事件中都会带有这些属性 TDAnalytics.setSuperProperties({ channel: " 渠道名 ", user_name: " 用 户名 " }); 

除了属性设置,我们也提供其他 API 来操作静态公共事件属性,满足 日常的业务需求。 

```arkts
JavaScript // 获取静态公共事件属性 let superProperties = TDAnalytics.getSuperProperties(); // 清除一条静态公共事件属性, 比如将之前设置 'channel' 属性清除,之后的数据将不会该属性 TDAnalytics.unsetSuperProperty("channel"); // 清除所有静态公共事 件属性 TDAnalytics.clearSuperProperties(); 
```

# 2.5.2 动态公共事件属性 

通过 setDynamicSuperProperties 设置动态公共属性的回调函数, SDK 将会在事件上报时触发回调函数,并把返回 JSON 对象加入到事 件属性中。 setDynamicSuperProperties 的参数是一个函数,函数需 要返回一个 JSON 对象。 

JavaScript // 设置动态公共属性,在事件上报时触发回调函数,并把 返回的 JSON 对象加入到事件属性中 

TDAnalytics.setDynamicSuperProperties(() => { return { dy_name: 'xxx', dy_age: 18 } }) 

# 2.6 记录事件时长 

如果您需要记录某个事件的持续时长,可以调用 timeEvent 来开始计 时。配置您想要计时的事件名称,当您上传该事件时,将会自动在您 的事件属性中加入 #duration 这一属性来表示记录的时长,单位为 秒。需要注意的是,同一个事件名只能有一个在计时的任务。 

JavaScript // 以下示例,完成用户在某个商品页面停留时长的统计 TDAnalytics.timeEvent("stay_shop"); /**do someting ....... **/ // 用 户离开商品页面,计时结束, "stay_shop" 这一事件中将会带有表示事 件时长的属性 #duration TDAnalytics.track({ eventName: "stay_shop", properties: { product_name: " 商品名 " } }); 

# 三、用户属性 

TA 平台支持的用户属性设置 API 有 : userSet 、 userSetOnce 、 userAdd 、 userUnset 、 userDelete 、 userAppend 、 userUniqAppend 。 

# 3.1 userSet 

对于一般的用户属性,您可以调用 userSet 来进行设置。使用该接口 上传的属性将会覆盖原有的属性值,如果之前不存在该用户属性,则 会新建该用户属性,类型与传入属性的类型一致,此处以设置用户名 为例: 

JavaScript // username 为 TA TDAnalytics.userSet({ properties: { username: "TA" } }); //username 为 TE TDAnalytics.userSet({ properties: { username: "TE" } }); 

# 3.2 userSetOnce 

如果您要上传的用户属性只要设置一次,则可以调用 userSetOnce 来 进行设置,当该属性之前已经有值的时候,将会忽略这条信息,以设 置首次付费时间来为例: 

JavaScript //first_payment_time 为 2018-01-01 01:23:45.678 TDAnalytics.userSetOnce({ properties: { first_payment_time: "2018-01-01 01:23:45.678" } }); //first_payment_time 仍然为 2018-01-01 01:23:45.678 TDAnalytics.userSetOnce({ properties: { first_payment_time: "2018-12-31 01:23:45.678" } }); 

# 3.3 userAdd 

当您要上传数值型的属性时,您可以调用 userAdd 来对该属性进行累 加操作,如果该属性还未被设置,则会赋值 0 后再进行计算。如果传 入负值,等同于减法操作。 

JavaScript // 此时 total_revenue 为 30 TDAnalytics.userAdd({ properties: { total_revenue: 30 } }); // 此时 total_revenue 为 678 TDAnalytics.userAdd({ properties: { total_revenue: 648 } }); 

# 3.4 userUnset 

当您要清空用户的用户属性值时,您可以调用 userUnset 来对指定属 性进行清空操作,如果该属性还未在集群中被创建,则 userUnset 不 

# 会创建该属性 

JavaScript // 清空该用户属性名为 userPropertykey 的用户属性值, 即设置成 NULL TDAnalytics.userUnset({ property: "userPropertykey" }); 

# 3.5 userDelete 

如果您要删除某个用户,可以调用 userDelete 将这名用户删除,您将 无法再查询该名用户的用户属性,但该用户产生的事件仍然可以被查 询到。 

JavaScript TDAnalytics.userDelete(); 

# 3.6 userAppend 

您可以调用 userAppend 对数组类型的用户数据追加元素。 

JavaScript TDAnalytics.userAppend({ properties: { user_list: ["apple", "ball"] } }); 

# 3.7 userUniqAppend 

您可以调用 userUniqAppend 对 Array (List) 类型的用户数据追加唯 一元素。调用 userUniqAppend 接口会对追加的用户属性进行去重, userAppend 接口不做去重,用户属性可存在重复。 

JavaScript // 此时 user_list 的属性值为 ["apple" , "ball"] TDAnalytics.userAppend({ properties: { user_list: ["apple", "ball"] } }); // 此时 user_list 的属性值为 ["apple","apple","ball","cube"] TDAnalytics.userAppend({ properties: { user_list: ["apple", "cube"] } }); // 此时 user_list 的属性值为 ["apple" , "ball","cube"] TDAnalytics.userUniqAppend({ properties: { user_list: ["apple", "cube"] } }); 

# 四、加密功能 

SDK 支持使用 AES+RSA 加密数据。数据加密功能需要客户端和服务 端配合完成,具体使用方法请咨询客户成功人员。 

JavaScript let config = new TDConfig() config.appId = 'app_id' config.serverUrl = 'server_url' // 开启加密功能 设置公钥信息 

config.enableEncrypt(1,'publicKey') 

五、开启与 H5 页面的打通 

如果需要与采集 H5 页面数据的 JavaScript SDK 进行打通,在初始化 WebView 时调用如下接口 

TypeScript controller: webview.WebviewController = new webview.WebviewController(); TDAnalytics.setJsBridge(controller) 

六、其他功能 

# 5.1 获取设备 ID 

您可以调用 getDeviceId() 获取设备 ID 。 

JavaScript let deviceId = TDAnalytics.getDeviceId(); 

设备 ID 会保存在缓存中,用户清理缓存,设备 ID 会被重置。 

# 5.2 校准时间 

SDK 默认会使用本机时间作为事件发生时间,如果用户手动修改设备 时间会影响到您的业务分析,此时可以通过校准时间操作保证事件发 生时间的准确性。我们提供时间戳、自动两种时间校准方式。 

您可以使用从服务端获取的当前时间戳对 SDK 的时间进行校准。此 后,所有未指定时间的调用,包括事件数据和用户属性设置操作,都 会使用校准后的时间作为发生时间。 

JavaScript // 1585633785954 为当前 unix 时间戳,单位为毫秒,对 应北京时间 2020-03-31 13:49:45 TDAnalytics.calibrateTime(1585633785954) 

您也可以设置自动时间校准,之后 SDK 会尝试从 config 接口中获取 当前时间,并对 SDK 时间进行校准。如果未获取正确的返回结果, 后续将使用本地时间上报数据。 

JavaScript let config = new TDConfig() config.appId = 'appId' config.serverUrl = 'serverUrl' // 设置为 true 开启自动时间校准 config.enableAutoCalibrated = true 

TDAnalytics.initWithConfig(this.context, config) 

# 5.3 设置默认时区 

默认情况下 ,SDK 会使用本机时间作为事件发生时间。您也可以通过 设置默认时区接口,指定时区,这样所有的事件都将按照您设置的时 区来对齐事件时间: 

JavaScript import I18n from '@ohos.i18n'; let config = new TDConfig() config.appId = 'appId' config.serverUrl = 'serverUrl' config.defaultTimeZone = I18n.getTimeZone('Australia/Sydney') TDAnalytics.initWithConfig(this.context, config) 

用指定时区对齐事件时间,会丢掉设备本机时区信息。如果需要保留 设备本机时区信息,目前需要您自己为事件添加相关属性。 

# 5.4 立即上报数据 

在某些业务场景下,如果您期望数据立即上报到 TE 服务器,可以通 过调用 flush 接口完成 

JavaScript TDAnalytics.flush(); 

# 自动采集 

OpenHarmony SDK 支持包括安装、启动、关闭等在内事件的自动采 集。 

一、介绍 

TE 系统提供自动化收集数据的接口,您可根据业务需求自行选择需 要自动收集的数据。 

目前支持的自动采集事件类型有: 

安装事件:记录 APP 被安装的行为 

启动事件:包括打开 APP 和从后台打开 APP 

关闭事件:包括关闭 APP 和 App 进入后台 

浏览事件:用户在 APP 中浏览页面( Ability ) 

点击事件:用户在 APP 中点击控件 

崩溃事件: APP 发生崩溃时记录崩溃信息( native 层的崩溃暂不支 持) 接下来将会详细介绍每种数据的采集方法 

二、开启自动采集 

您可以调用 enableAutoTrack ,打开自动采集功能: 

JavaScript //APP 安装事件 TDAutoTrackEventType.APP_INSTALL // APP 启动事件 TDAutoTrackEventType.APP_START //APP 关闭事件 TDAutoTrackEventType.APP_END //APP 浏览页面事件 TDAutoTrackEventType.APP_VIEW_SCREEN //APP 点击控件事件 TDAnalytics.TDAutoTrackEventType.APP_CLICK //APP 崩溃事件 TDAutoTrackEventType.APP_CRASH 

TDAnalytics.enableAutoTrack(context,TDAutoTrackEventType.APP_START | TDAutoTrackEventType.APP_INSTALL | TDAutoTrackEventType.APP_END | TDAutoTrackEventType.APP_VIEW_SCREEN | TDAutoTrackEventType.APP_CLICK | TDAutoTrackEventType.APP_CRASH) 

enableAutoTrack 需要在主线程中调用,如果需要在 work 线程中初始 化 SDK ,可参考下面的代码 

TypeScript const workerInstance = new worker.ThreadWorker("./ workers/worker.ets"); TDAnalytics.enableAutoTrack(this.context, TDAutoTrackEventType.APP_START | TDAutoTrackEventType.APP_INSTALL | TDAutoTrackEventType.APP_END | TDAutoTrackEventType.APP_VIEW_SCREEN | TDAutoTrackEventType.APP_CRASH | 

TDAutoTrackEventType.APP_CLICK, (command: string, params: Object, appId?: string) => { // 这里会将需要触发的自动采集事件回 调出来,需要将消息发送到 work 线程去处理 

workerInstance.postMessage({ type: command, params: params }) 

# }) 

```arkts
TypeScript const workerPort = worker.workerPort; workerPort.onmessage = (d: MessageEvents): void => { if (d.data.type === 'track') { TDAnalytics.track(d.data.params); } else if (d.data.type === 'timeEvent') { 
```

TDAnalytics.timeEvent(d.data.params); } else if (d.data.type === 'flush') { TDAnalytics.flush() } } 

三、详细介绍 

# 3.1 安装事件 

APP 安装事件将会记录 APP 的实际安装,在 APP 启动时上报,事件 触发时间是 APP 安装后首次启动的时间, APP 升级并不会触发安装 事件,而删除重装后会上报安装事件。 

事件名: ta_app_install 

# 3.2 启动事件 

APP 启动事件将会在用户开启 APP ,或从后台唤醒 APP 时触发,详 细的事件介绍如下: 

事件名: ta_app_start 

预置属性: #resume_from_background ,布尔型,表示 APP 是用户开 启还是从后台唤醒,取值为 true 表示从后台唤醒, false 为直接开 启。 

通过 ApplicationStateChangeCallback 中的 onApplicationForeground 回调来触发 

# 3.3 关闭事件 

APP 关闭事件将会在用户关闭 APP ,或将 APP 调至后台时触发,详 细的事件介绍如下: 

事件名: ta_app_end 

预置属性: #duration ,数值型,表示该次 APP 访问(自启动至结 

束)的时长,单位是秒。 

通过 ApplicationStateChangeCallback 中的 onApplicationBackground 回调来触发 

# 3.4 浏览页面事件 

APP 浏览页面事件会在用户浏览页面( Ability )时触发,详细的事件 介绍如下: 

事件名: ta_app_view 

预置属性: 

#screen_name ,字符串型,为 Ability 的简单类名 

# 3.5 点击事件 

APP 控件点击事件将会在用户点击控件( view )时触发 

事件名: ta_app_click 

预置属性: 

#screen_name ,字符串型,为控件所属 Activity 的包名 . 类名 

#element_type ,字符串型,为控件的类型 

#element_id ,字符串型,为控件的 ID 

# 3.6 崩溃事件 

当 APP 出现未捕获异常时,会上报 APP 崩溃事件 

事件名: ta_app_crash 

预置属性: #app_crashed_reason ,字符型,记录崩溃时的堆栈轨迹 

通过 ErrorObserver 的 onUnhandledException 来监听,暂不支持 native 的崩溃采集。 

预置属性 

一、 所有事件带有的预置属性 

以下预置属性,是 OpenHarmony SDK 中所有事件(包括自动采集事 件)都会带有的预置属性 

属性名 

中文名 

属性类型 

采集时机 

说明 

#ip 

IP 地址 

文本 

服务端采集 

用户的 IP 地址, TE 将以此获取用户的地理位置信息 

#country 

国家 

文本 

服务端采集 

用户所在国家,根据 IP 地址生成 

#country_code 

国家代码 

文本 

# 服务端采集 

用户所在国家的国家代码 (ISO 3166-1 alpha-2 ,即两位大写英文字 母 ) ,根据 IP 地址生成 

#province 

省份 

文本 

服务端采集 

用户所在省份,根据 IP 地址生成 

#city 

城市 

文本 

服务端采集 

用户所在城市,根据 IP 地址生成 

#os_version 

操作系统版本 

文本 

初始化时采集一次 

iOS 11.2.2 、 Android 8.0.0 等 

#manufacturer 

设备制造商 

文本 

初始化时采集一次 

# 用户设备的制造商,如 Apple , vivo 等 

#os 

操作系统 

文本 

初始化时采集一次 

如 Android 、 iOS 、 HarmonyOS 等 

#device_id 

设备 ID 

文本 

初始化时采集一次 

用户的设备 ID , iOS 取用户的 IDFV 或 UUID , Android 取 androidID 

#screen_height 

屏幕高度 

数值 

初始化时采集一次 

用户设备的屏幕高度,如 1920 等 

#screen_width 

屏幕宽度 

数值 

初始化时采集一次 用户设备的屏幕高度,如 1080 等 

#device_model 

设备型号 

文本 

初始化时采集一次 

用户设备的型号,如 iPhone 8 等 

#device_type 

设备类型 文本 

初始化时采集一次 

设备类型,如 "Tablet" 、 "Phone" #app_version APP 版本 

文本 初始化时采集一次 您的 APP 的版本 #bundle_id 应用唯一标识 文本 初始化时采集一次 应用包名或进程名 #lib 

SDK 类型 

# 文本 

初始化时采集一次 

您接入 SDK 的类型,如 Android , iOS 等 

#lib_version 

SDK 版本 

文本 

初始化时采集一次 您接入 SDK 的版本 

#network_type 

网络状态 

文本 初始化时采集一次,网络状态变化时采集 上传事件时的网络状态,如 WIFI 、 3G 、 4G 等 #carrier 

网络运营商 

文本 初始化时采集一次 

用户设备的网络运营商,如中国移动,中国电信等 #zone_offset 

时区偏移 

# 数值 

事件发生时采集 

# 数据时间相对 UTC 时间的偏移小时数 

#install_time 

程序安装时间 

时间 

初始化时采集一次 

用户安装应用的时间,值来源于系统 

#system_language 

系统语言 

文本 

初始化时采集一次 

用户设备的系统语言 (ISO 639-1 ,即两位小写英文字母 ) ,如 zh, en 等 二、获取预置属性 

可以调用 getPresetProperties() 方法获取预置属性。 

服务端埋点需要 App 端的一些预置属性时,可以通过此方法获取 App 端的预置属性,再传给服务端。 

TDAnalytics.getPresetProperties() /** { "#os": "HarmonyOS", "#os_version": 10, "#bundle_id": "com.example.tdharmonyosdemo", "#install_time": "2023-10-19 18:46:00.105", "#manufacturer": "HUAWEI", "#device_model": "NOH-AN00", "#device_type": "phone", "#screen_width": 1344, "#screen_height": 2772, "#system_language": "zh-Hans", "#carrier": " 中国电信 ", "#app_version": "1.0.1", "#device_id": "9811b90b-ee24-45c1-950a-77ee0ffc7a1c", 

"#zone_offset": 8 } */ 

# 多实例 

一、功能介绍 

我们支持使用多个 Appid ,创建 SDK 实例,我们简称为多实例。通过 多实例功能,您可以上报数据到不同的项目。 

二、创建多实例 

传入不同的 APP ID 完成 SDK 初始化,即可创建多个 SDK 实例: 

JavaScript // 初始化配置 1 var config_1 = { appId: "app-id-1", serverUrl: "https://youserverurl.1.com" }; TDAnalytics.init(config_1); // 初始化配置 2 var config_2 = { appId: "app-id-2", serverUrl: "https://youserverurl.2.com" }; TDAnalytics.init(config_2); // 上报事件到配置 1 (不传 app-id ,默认 上报到配置 1 ) TDAnalytics.track({ eventName: 'event_from_appid_1' }); // 上报事件到配置 1 (指定 app-id-1 ) TDAnalytics.track({ eventName: 'event_from_appid_1' }, 'app-id-1'); // 上报事件到配置 2 (指定 app-id-2 ) TDAnalytics.track({ eventName: 'event_from_appid_2' }, 'app-id-2'); 

请注意多个 SDK 实例的 APP ID 必须不同,多实例之间的大多数数据 “ ” 是不共通的,详情可参考第四节 多实例间的数据、设置共享 。 

# 三、多实例间的数据共享 

大多数接口都是由实例对象所调用,因此绝大部分数据与设置在多 APPID 实例、父实例与轻量实例间是不共享的,但有部分数据与设置 会对所有实例生效,以下是所有数据与设置在多实例间是否共享的详 细说明: 

# 账号相关信息 

系统默认生成的访客 ID#distinct_id :共享 

调用 identify 设置的访客 ID#distinct_id :不共享 

调用 login 设置的账号 ID#account_id :不共享 

事件上报 track 与用户属性上报 user_set 、 user_setOnce 、 user_add 、 user_delete :不共享 

公共属性 setSuperProperties 和动态公共属性 setDynamicSuperPropertiesTracker :不共享 

记录事件时长 timeEvent :不共享
