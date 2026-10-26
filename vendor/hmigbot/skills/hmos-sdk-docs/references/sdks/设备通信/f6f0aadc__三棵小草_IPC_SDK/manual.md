# **Flutter 连接播放SDK** 

## **文档信息** 

文档版本1.0 

最低适配版本 HarmonyOS 5.0.1 

## **1.概述** 

### **1.1 ipc插件功能** 

初始化sdk,直播,sd卡,云存音视频处理,以及连接上的set/get操作 

### **1.2 xc_common插件功能** 

实体类定义 

### **1.3 xc_grpc插件功能** 

网络请求库 

## **2.环境准备** 

开发工具: DevEco Studio 最新版本 SDK: HarmonyOS Next SDK 目标设备: 支持HarmonyOS 5.0.1 及以上的设备 

## **3.sdk** 

### **3.1 启动sdk** 

只能调用一次,进入app调用 

import 'package:ipc/xc_ipc.dart' as ipc; await ipc.start(logFilePath);//日志文件路径 

### **3.2 createSession** 

登录成功后调用 

import 'package:xc_common/proto/generate/useragent/CreateSession.pbgrpc.dart' as CreateSession; import 'package:ipc/xc_ipc.dart' as ipc; CreateSession.Resp resp= await ipc.LocalGrpc().createSession( String countryCode, String user, String pass, String clientId, String clientSeckey, String iotgw, String glbs, String cloudPath) 

### **3.3 destroyedSession** 

#### 退出登录调用 

import 'package:xc_common/proto/generate/useragent/DestroyedSession.pbgrpc.dart' as DestroyedSession; import 'package:ipc/xc_ipc.dart' as ipc; DestroyedSession.Resp resp = await ipc.LocalGrpc().destroyedSession() 

## **4.直播视频接入** 

### **4.1 播放控件接入** 

#### **1.AndroidVIew,OhosView,onPlatformViewCreated回调里面,会触发saveKey和removeKey两个方法** 

- **2.saveKey回调需要调用bindConfig函数,并且保存ptr同时后续和音视频相关的功能的接口需要传入该值** 

import 'package:ipc/xc_ipc.dart' as ipc; /// ptr 通过AndroidView OhosView获取 /// did 设备did /// channel 通道,通过数小于等于1 传0,大于1,传入 1,2....N /// source 直播传入 1,sd 2 云存 3 ipc.bindConfig(ptr, did, channle, source); 

#### **3.removeKey回调中需要将保存ptr置为0** 

#### **AndroidView** 

import 'package:ipc/xc_ipc.dart' as ipc; AndroidView( viewType: "surface_view_type", creationParamsCodec: const StandardMessageCodec(), onPlatformViewCreated: (viewId) { final eventChannel = MethodChannel("surface_view_type/$viewId"); eventChannel!.setMethodCallHandler((call) async { Map<String, dynamic> map = Map<String, dynamic>.from(call.arguments); 

if (call.method == "saveKey") { int ptr = map["ptr"]; nativePlayerPtr = ptr; // 保存本地 ipc.bindConfig(ptr,did,channel,source); 

} else if (call.method == "removeKey") { nativePlayerPtr = 0; } }); }, ) 

#### **OhosView** 

import 'package:ipc/xc_ipc.dart' as ipc; OhosView( viewType: "surface_view_type", creationParamsCodec: const StandardMessageCodec(), onPlatformViewCreated: (viewId) { final eventChannel = MethodChannel("surface_view_type/$viewId"); eventChannel.setMethodCallHandler((call) async { Map<String, dynamic> map = Map<String, dynamic>.from(call.arguments); if (call.method == "saveKey") { int ptr = map["ptr"]; nativePlayerPtr = ptr; // 保存本地 ipc.bindConfig(ptr,did,channel,source); } else if (call.method == "removeKey") { nativePlayerPtr = 0; } }); }, ) 

### **4.2 播放/暂停视频** 

registerOutImageCallback,removeOutImageCallback,connVideoPlay,connVideoPause保证成对调用 

import 'package:ipc/xc_ipc.dart' as ipc; import 'package:xc_common/proto/generate/useragent/ConnVideoPlay.pbgrpc.dart' as ConnVideoPlay; 

///注册视频出图回调,只回调一次,二次回调需要配合resetOutImage使用 ///key 唯一即可 ipc.registerOutImageCallback(dynamic key, (String did, int channel, int source) { }, ) ///取消视频出图回调 ///key 和registerOutImageCallback一致 ipc.removeOutImageCallback(dynamic key); 

///是否重新回调registerOutImageCallback ///ptr 通过AndroidView OhosView获取 ipc.resetOutImage(int ptr); /// 连接设备 /// did 设备did await ipc.LocalGrpc().openDevice(did); /// 播放视频 /// did 设备did /// nativeWindowPtr 通过AndroidView OhosView获取 /// channel 通道,通过数小于等于1 传0,大于1,传入 1,2....N /// qos 1-5: 480; 6-10: 720; 11-15: 960; 16-20: 1080; 21-25:2k 默认0设备自己选择 /// speed 建议码率: bps 默认0 /// cache true 先缓存300ms数据后播放 await ipc.LocalGrpc().connVideoPlay( String did, int nativeWindowPtr, int channel, { int qos = 0, int speed = 0, bool cache = false, }); /// 关闭视频播放 /// did 设备did /// channel 通道,通过数小于等于1 传0,大于1,传入 1,2....N await ipc.LocalGrpc().connVideoPause( String did, int channel); 

### **4.3播放/暂停音频** 

connAudioPlay,connAudioPause成对调用 

import 'package:ipc/xc_ipc.dart' as ipc; /// 播放音频 /// did 设备did /// nativeWindowPtr 通过AndroidView OhosView获取 /// channel 无特殊需求默认传0 await ipc.LocalGrpc().connAudioPlay( String did, int nativeWindowPtr, {int channel = 0}); /// 关闭音频播放 /// did 设备did /// nativeWindowPtr 通过AndroidView OhosView获取 

/// channel 无特殊需求默认传0 await ipc.LocalGrpc()connAudioPause(String did, int nativeWindowPtr, {int channel = 0}) 

### **4.4对讲** 

connTalkbackPlay,connTalkbackPlay成对调用 

import 'package:ipc/xc_ipc.dart' as ipc; ///开始对讲 /// did 设备did /// channel 无特殊需求默认传0 await ipc.LocalGrpc().connTalkbackPlay(String did, {int channel = 0}); 

///关闭对讲 /// did 设备did /// channel 无特殊需求默认传0 await ipc.LocalGrpc().connTalkbackPlay(String did, {int channel = 0}); 

### **4.5保存图片** 

import 'package:ipc/xc_ipc.dart' as ipc; 

///保存图片 ///prt 通过AndroidView OhosView获取 ///path 图片保存路径,xxx/xxx/xxx.jpg ///return 0表示成功 ipc.saveImage(int ptr, String path); 

### **4.6录制mp4** 

registerRecordSecCallback,removeRecordSecCallback,startRecord,stopRecord成对调用 

import 'package:ipc/xc_ipc.dart' as ipc; ///注册录制音视频时间回调 单位秒 ///key 唯一即可 ipc.registerRecordSecCallback( dynamic key, ///sec 录制视频时长 单位秒 (did, channel, source, sec) { }, ); ///取消录制音视频时间回调 ///key 和registerRecordSecCallback一致 

ipc.removeRecordSecCallback(dynamic key); 

///开始录制音视频 ///ptr 通过AndroidView OhosView获取 ///path 视频保存路径,xxx/xxx/xxx.mp4 ///hasAudio 点击录制那一个时刻,音频播放是否打开 ///sync 是否音画同步录制, true 同步(此时需要设备音频视频时间戳准确,单位毫秒ms) ipc.startRecord(int ptr, String path, bool hasAudio, bool sync); 

///结束录制音视频 

///ptr 通过AndroidView OhosView获取 ///return 0 表示成功 ipc.stopRecord(int ptr); 

## **5.sd卡视频接入** 

### **5.1sd卡信息列表** 

import 'package:ipc/xc_ipc.dart' as ipc; import 'package:xc_common/proto/generate/useragent/ConnHistoryDays.pbgrpc.dart' as ConnHistoryDays; 

import 'package:xc_common/proto/generate/useragent/ConnHistoryDayList.pbgrpc.dart' as ConnHistoryDayList; 

import 'package:xc_common/proto/generate/useragent/ConnHistoryThumGet.pbgrpc.dart' as ConnHistoryThumGet; 

///获取某年某月哪些天有录像 

/// did 设备did /// year 如2026 /// month 1-12 

/// return 取数组days的值,例如[1,6,8,31]表示1,6,8,31号有录像 

ConnHistoryDays.Resp resp = await ipc.LocalGrpc().connHistoryDays(String did, int year, int month, 

{int channel = 0}) 

///获取具体某一天的录像 /// did 设备did /// day 如20260114 

/// startTime  设备不支持索引 2026-01-14 23:59:59 下一页用当前页的数据最后一条数据的start_time ///            反之用 2026-01-14 00:00:00时间,同时分页startTime不变 

/// types /// order 默认传1 /// page 1开始 /// channel 通道,通过数小于等于1 传0,大于1,传入 1,2....N /// pageSize 不超过20 

/// return 根据实际应用两种数据结构,二选一,或者一起返回 ///   HistoryInfo historys 时间形式 ///       start_time 录像开始时间 ///       length 单位ms; SD卡录像的(音视频)的时间戳必须等于: start_time+length ///       file_id 文件ID,用于唯一标识文件(取文件时使用) 

///       thum_fid 录像文件的缩略图id ///       history_type 录像分类 ///   HistoryTimeRange history_range 支持连续录像,返回该值 ///       start_time 录像开始时间 ///       length 单位ms; SD卡录像的(音视频)的时间戳必须等于: start_time+length ///       history_type 录像分类 ConnHistoryDayList.Resp resp = await ipc.LocalGrpc().connHistoryDayList( String did, int day, int startTime, List<int> types, int order, int page, {int channel = 0, int pageSize = 20}) 

/// 获取文件缩略图 /// did 设备did /// id 文件缩略图id /// return 取thum_body 缩略图二进制文件 ConnHistoryThumGet.Resp resp = await ipc.LocalGrpc()connHistoryThumGet(String did, int id, {int channel = 0}) 

///删除sd卡录像 /// did 设备did /// fileIds sd卡文件唯一id集合 根据设备硬件能力自定义大小,一次不能太多 await ipc.LocalGrpc().connHistoryDel(String did, int channel, List<int> fileIds) 

### **5.2播放sd卡视频** 

import 'package:ipc/xc_ipc.dart' as ipc; 

///注册视频出图回调,只回调一次,二次回调需要配合resetOutImage使用 ///key 唯一即可 ipc.registerOutImageCallback(dynamic key, (String did, int channel, int source) { }, ) ///取消视频出图回调 ///key 和registerOutImageCallback一致 ipc.removeOutImageCallback(dynamic key); 

///是否重新回调registerOutImageCallback ///ptr 通过AndroidView OhosView获取 ipc.resetOutImage(int ptr); 

///注册播放视频时间戳回调 ///key 唯一即可 ipc.registerTimeMsCallback(dynamic key, (did, channel, source, timeMs) {}); 

##### ///取消播放视频时间戳回调 

ipc.removeTimeMsCallback(dynamic key); 

///历史视频播放 默认不播放音频 

/// did 设备did /// nativeWindowPtr 通过AndroidView OhosView获取 /// channel 通道,通过数小于等于1 传0,大于1,传入 1,2....N /// fileId sd卡文件id /// startTime 播放开始时间 /// cache true 先缓存300ms数据后播放 await ipc.LocalGrpc().connHistoryPlay( String did, int nativeWindowPtr, int channel, int fileId, int startTime, {bool cache = false}) 

/// 历史音视频暂停 /// did 设备did /// nativeWindowPtr 通过AndroidView OhosView获取 /// channel 通道,通过数小于等于1 传0,大于1,传入 1,2....N /// fileId sd卡文件id await ipc.LocalGrpc().connHistoryPause(String did, int nativeWindowPtr, int channel, int fileId) ///暂停sd卡音频 /// nativeWindowPtr 通过AndroidView OhosView获取 await ipc.LocalGrpc().connHistoryAudioPause(int nativeWindowPtr) 

///播放sd卡音频 /// nativeWindowPtr 通过AndroidView OhosView获取 await ipc.LocalGrpc().connHistoryAudioStart(int nativeWindowPtr) 

## **6.云存接入** 

### **6.1云存播放** 

import 'package:ipc/xc_ipc.dart' as ipc; 

///注册视频出图回调,只回调一次,二次回调需要配合resetOutImage使用 ///key 唯一即可 ipc.registerOutImageCallback(dynamic key, (String did, int channel, int source) { }, ) ///取消视频出图回调 ///key 和registerOutImageCallback一致 ipc.removeOutImageCallback(dynamic key); 

///是否重新回调registerOutImageCallback ///ptr 通过AndroidView OhosView获取 ipc.resetOutImage(int ptr); 

///注册播放视频时间戳回调 ///key 唯一即可 ipc.registerTimeMsCallback(dynamic key, (did, channel, source, timeMs) {}); 

///取消播放视频时间戳回调 

ipc.removeTimeMsCallback(dynamic key); 

/// 播放云存文件 /// nativeWindowPtr 通过AndroidView OhosView获取 /// fileInfo 参考cloud_file_case /// playstartms 播放文件的开始时间 /// playendms 播放文件的结束时间 await ipc.LocalGrpc().playCloudFilePlay(int nativeWindowPtr, CSFileByEvent.FileInfo fileInfo, int playstartms, int playendms, {int channel = 0}); /// 播放下一个云存文件,用于一个事件对应多个云存的问题 /// fileInfo 参考cloud_file_case /// channel 通道,通过数小于等于1 传0,大于1,传入 1,2....N await ipc.LocalGrpc().playCloudFilePlayNext( CSFileByEvent.FileInfo fileInfo, {int channel = 0}); ///暂停云存 ipc.LocalGrpc().playCloudPause(); ///停止云存 ipc.LocalGrpc().layCloudStop(); 

///音频暂停 /// nativeWindowPtr 通过AndroidView OhosView获取 ipc.LocalGrpc().connCloudAudioPause(int nativeWindowsPtr); 

///音频播放 

/// nativeWindowPtr 通过AndroidView OhosView获取 ipc.LocalGrpc().connCloudAudioStart(int nativeWindowsPtr); 

///继续播放云存 connCloudAudioPause后可以使用 ipc.LocalGrpc().playCloudContinue(); 

##### /// 设置云存播放速率 

/// speed 设置倍速播放: 1, 2, 4, 8, 16 ; 支持慢速播放,取值为实际播放速度*100; 最小支持0.2倍速播放; 设置值为: 0.2*100=20 

ipc.LocalGrpc().playCloudSpeed(int speed); 

### **6.2云存下载** 

import 'package:ipc/xc_ipc.dart' as ipc; 

///注册播放视频时间戳回调 ///key 唯一即可 ///source == 6 表示下载的当前文件结束,结束调用 ipc.registerTimeMsCallback(dynamic key, (did, channel, source, timeMs) {}); 

///取消播放视频时间戳回调 

ipc.removeTimeMsCallback(dynamic key); 

///下载云存 /// did 设备did /// path 云存文件保存路径 /// key 唯一即可 /// fileInfo 参考cloud_file_case /// playstartms 播放文件的开始时间 /// playendms 播放文件的结束时间 /// chan 下载通道 /// next 继续下载 true 下载下一个文件 false 重新开始下载 /// sync 是否音画同步录制, true 同步(此时需要设备音频视频时间戳准确,单位毫秒ms) await ipc.LocalGrpc().playCloudGetAllAVPackets( String did, String path, int key, CSFileByEvent.FileInfo fileInfo, int playstartms, int playendms, int chan, bool next, {bool sync = false}); ///结束下载 ///key 和LocalGrpc().playCloudGetAllAVPackets一致 /// return 0 下载成功 !0 失败 int ret = ipc.LocalGrpc().playCloudStopDownload(int key) 

## **7.其他接口** 

import 'package:ipc/xc_ipc.dart' as ipc; ///断开连接 /// did 设备did await ipc.LocalGrpc().closeDevice(String did); 

///设置视频分辨率 /// did 设备did /// nativeWindowPtr 通过AndroidView OhosView获取 /// channel 通道,通过数小于等于1 传0,大于1,传入 1,2....N /// qos 1-5: 480; 6-10: 720; 11-15: 960; 16-20: 1080; 21-25:2k 默认0设备自己选择 /// speed 建议码率: bps 默认0 await ipc.LocalGrpc().connVideoQosSet(String did, int channel, int qos, {int speed = 0}) /// 切换播放通道 /// did 设备did /// channel 通道,通过数小于等于1 传0,大于1,传入 1,2....N await ipc.LocalGrpc().connChanState(String did,int channel) 

/// 多通道播放,一般nvr使用 /// did 设备did /// channels 通道[1,3,4,5,8,12,16] await ipc.LocalGrpc().connVideoChanChange(String did, List<int> channels) 

/// 录像计划设置 /// did 设备did /// recordType 1, 连续录像; 2, 事件录像 /// channel 通道,无特殊需求传0 /// tt [Time.Timetask] ///       days 日期构成,表示只在特定的日期触发; 与week_day互斥: YYYYMMDD=20190101 ///       week_day  0-6: 0 星期天 1 星期一.... ///       enable 是否启用; 0: disable; 1: enable; 2: 不支持时间设置 ///       time [Time.Timeinfo] ///                start_sec 开始时间,单位秒;相对于每天零点的时间差值 ///                end_sec  end_sec >= start_sec; 如果小于 start_sec 表示隔天(如果表示隔天,必 须要满足 days,  week_day, month_day 的参数) ///       month_day 月份中的天数表达: 1-31 await ipc.LocalGrpc().connVideoChanChange(String did, int recordType, List<Time.Timetask> tt, 

{int channel = 0}) 

///录像计划获取 /// did 设备did /// channel 通道,无特殊需求传0 /// return [ConnHistoryPlanGet.Resp] ///            record_type 录像类型: 1, 连续录像; 2, 事件录像 ///            tt [Time.Timetask] 参考 connHistoryPlanSet ///            enable 是否启用; 0: disable; 1: enable await ipc.LocalGrpc().connHistoryPlanGet(String did, int recordType, List<Time.Timetask> tt, 

{int channel = 0}) 

/// 告警参数获取 /// did 设备did /// channel 通道,无特殊需求传0 /// return [ConnAlarmGet.Resp] ///           motion 移动侦测灵敏度: 0 关闭; 1 低; 2 中; 3 高 ///           sound 响声侦测灵敏度: 0 关闭; 1 低; 2 中; 3 高 ///           smoke 烟雾检测:  0 关闭; 1 打开 ///           shadow 视频遮挡: 0 关闭; 1 打开 await ipc.LocalGrpc().connAlarmGet(String did, {int channel = 0}) 

///告警参数设置 /// did 设备did /// channel 通道,无特殊需求传0 /// motion 移动侦测灵敏度: 0 关闭; 1 低; 2 中; 3 高 /// sound 响声侦测灵敏度: 0 关闭; 1 低; 2 中; 3 高 /// smoke 烟雾检测:  0 关闭; 1 打开 /// shadow 视频遮挡: 0 关闭; 1 打开 await ipc.LocalGrpc().connAlarmGet(String did, {int channel = 0}) 

/// 获取设备最后的配置参数 /// did 设备did /// channel 通道,无特殊需求传0 /// return [ConnConfigGet.Resp] ///            flip 翻转信息: 1: Upright, 2: Flip Horizontal,3 :Flip Vertical,4: turn 180 ///            led_mode LED状态: 1 常开;2 常关; ///            ircut_mode IRCut状态: 1 常开;2 常关; 3 自动 ///            secret_mode 私密模式: 0 不开启私有模式; 1 开始私有模式 ///            volume 0-10; 0 静音; 1-10 数字越大音量越大 ///            power_freq 0 自动; 50 50HZ; 60 60HZ ///            duration 录像时长,单位秒: 5, 10, 15, 30 ///            wifi [ConnConfigGet.WifiInfo] wifi信息 ///                      support 0 不支持WIFI;1 支持WIFI ///                      ssid ///                      qos ///            notify [ConnConfigGet.NotifyInfo] 通知参数 ///                       states  0 disable; 1 enable; ///                       tt  [Time.Timetask] 参考 connHistoryPlanSet; ///                       level  1: low; 2: middle; 3: frequent  low: 运动开始触发一条,在3分 钟内如果持续有移动不再触发;如果超过3分钟后再触发 middle: 触发间隔是1分钟 frequent: 触发间隔是30秒 

await ipc.LocalGrpc().connConfigGet(String did, {int channel = 0}) ///自定义命令通道 /// did 设备did /// argInts int32参数组 /// argBytes 字节数组 /// argStrings 字符串数组 /// return [ConnCustomCmd.Resp] ///             argInts int32参数组 ///             argBytes 字节数组 ///             argStrings 字符串数组 await ipc.LocalGrpc().connConfigGet(String did,List<int> argInts,List<int> argBytes,List<String>argStrings); 

/// 获得事件录像参数 /// did 设备did /// channel 通道,无特殊需求传0 /// return  [ConnEventRecordGet.Resp] ///               duration 录像时长,单位秒: 5, 10, 15, 30 await ipc.LocalGrpc().connEventRecordGet(String did, {int channel = 0}); 

/// 设置事件录像参数 /// did 设备did /// channel 通道,无特殊需求传0 /// duration 录像时长,单位秒: 5, 10, 15, 30 await ipc.LocalGrpc().connEventRecordSet(String did, int duration, {int channel = 0}); 

///通知固件更新 

/// did 设备did /// channel 通道,无特殊需求传0 /// return [ConnFirmwareNotify.Resp] ///             rate 0 执行升级; 大于0表示正在升级,并且返回升级进度;如果是平台通知升级则不用返回进度 await ipc.LocalGrpc().connFirmwareNotify(String did, {int channel = 0}); ///翻转状态获取 /// did 设备did /// channel 通道,无特殊需求传0 /// return [ConnFlipGet.Resp] ///             flip 1: Upright, 2: Flip Horizontal,3 :Flip Vertical,4: turn 180 await ipc.LocalGrpc().connFlipGet(String did, {int channel = 0}); 

///翻转状态设置 /// did 设备did /// channel 通道,无特殊需求传0\ /// flip 1: Upright, 2: Flip Horizontal,3 :Flip Vertical,4: turn 180 await ipc.LocalGrpc().connFlipSet(String did, int flip, {int channel = 0}); 

///获取设备的网络信息 /// did 设备did /// channel 通道,无特殊需求传0 /// return [ConnGetNetworkInfo.Resp] ///             ssid 

///             qos 网络质量: 1-6; 0 不支持;数字越大网络质量越好; 只有在接入是无线的情况下表示; 1 无 信号 ///             ipaddr IP地址 ///             netmask 子网掩码 ///             gateway 网关地址 ///             dns1 ///             dns2 ///             mac MAC地址 await ipc.LocalGrpc().connGetNetworkInfo(String did, {int channel = 0}) 

/// 获取红外灯工作状态 /// did 设备did /// channel 通道,无特殊需求传0 /// return [ConnIRCutGet.Resp] ///             mode 1 常开;2 常关; 3 自动 -> 10-1000; 对应灵敏度 await ipc.LocalGrpc().connIRCutGet(String did, {int channel = 0}) 

/// 设置红外工作状态 /// did 设备did /// channel 通道,无特殊需求传0 /// mode 1 常开;2 常关; 3 自动 -> 10-1000; 对应灵敏度 await ipc.LocalGrpc().connIRCutSet(String did, int mode, {int channel = 0}) 

///获取状态灯 

/// did 设备did /// channel 通道,无特殊需求传0 /// return [ConnLedGet.Resp] ///            mode  1 常开;2 常关 await ipc.LocalGrpc().connLedGet(String did, {int channel = 0}); 

/// 开启/关闭状态灯 /// did 设备did /// channel 通道,无特殊需求传0 /// mode  1 常开;2 常关 await ipc.LocalGrpc().connLedSet(String did, int mode, {int channel = 0}) /// 获取运动区间参数 /// did 设备did /// channel 通道,无特殊需求传0 /// return [ConnMotionzoneGet.Resp] ///             mz 该区块被选中,则为1,反之为0 ///                编号是左上⻆计数为0,0开始; 从左到右,从上到下,按位进行表示 ///                网格宽高比对应占用字节: 4*3 = 2字节 ;  8*6 = 6字节; 12*9 = 14字节; ///                 16*12 = 24字节; 20*15 =  38字节; 24*18 = 54字节 ///             points [ConnMotionzoneGet.XYPoint] 界面设置的坐标; 最大5个 ///                        leftup_x ///                        leftup_y ///                        rightdown_x ///                        rightdown_y await ipc.LocalGrpc().connMotionZoneGet(String did,{int channel = 0} 

/// 运动区间设置 /// did 设备did /// channel 通道,无特殊需求传0 /// mz 参考 connMotionZoneGet ConnMotionzoneGet.Resp mz /// points 参考 connMotionZoneGet ConnMotionzoneGet.XYPoint await ipc.LocalGrpc().connMotionZoneSet( String did, { int channel = 0, List<int> mz = const [], List<ConnMotionzoneSet.XYPoint> points = const [], }) /// 获取通知参数 /// did 设备did /// channel 通道,无特殊需求传0 /// return [ConnNotifyGet.Resp] ///             states  0 disable; 1 enable; ///             tt  [Time.Timetask] 参考 connHistoryPlanSet; ///             level  1: low; 2: middle; 3: frequent  low: 运动开始触发一条,在3分钟内如果持续 有移动不再触发;如果超过3分钟后再触发 middle: 触发间隔是1分钟 frequent: 触发间隔是30秒 

await ipc.LocalGrpc().connNotifyGet(String did, {int channel = 0}); 

/// 设置通知参数 /// did 设备did /// channel 通道,无特殊需求传0 /// states  0 disable; 1 enable; /// tt  [Time.Timetask] 参考 connHistoryPlanSet; /// level  1: low; 2: middle; 3: frequent  low: 运动开始触发一条,在3分钟内如果持续有移动不再触 发;如果超过3分钟后再触发 middle: 触发间隔是1分钟 frequent: 触发间隔是30秒 await ipc.LocalGrpc().connNotifySet( String did, int state, Time.Timetask tt, {int channel = 0, int level = 1}); /// pir获取 /// did 设备did /// channel 通道,无特殊需求传0 /// return [ConnPirGet.Resp] ///            pirs [ConnPirGet.PirInfo] ///                     num PIR编号,当一个设备有多个PIR的时候,从左到右。数字从1开始进行+1编号;如 果为0表示所有PIR ///                     level 设备端支持红外测距: 该值是距离的表达,单位米 ///                           设备端不支持红外测距: 该值是灵敏度表达: 0 关闭; 1, 低; 2, 中; 3, 高 

await ipc.LocalGrpc().connPirGet(String did, {int channel = 0}) /// Pir设置 /// did 设备did /// channel 通道,无特殊需求传0 /// pir 参考 connPirGet await ipc.LocalGrpc().connPirSet(String did, ConnPirSet.PirInfo pir, {int channel = 0}); 

/// 获得电源频率 /// did 设备did /// channel 通道,无特殊需求传0 /// return [ConnPowerFreqGet.Resp] ///             power_freq 0 自动: 50=50HZ, 60=60HZ await ipc.LocalGrpc().connPowerFreqGet(String did, {int channel = 0}) 

/// 设置电源频率 /// did 设备did /// channel 通道,无特殊需求传0 /// powerFreq 0 自动: 50=50HZ, 60=60HZ await ipc.LocalGrpc().connPowerFreqSet(String did, int powerFreq, {int channel = 0}); /// 设置预置点 /// 参考源码local_grpc.dart await ipc.LocalGrpc().connPspAdd(String did, String pspName, bool isDef, {int channel = 0, int pspId = 0}) 

/// 呼叫预置点 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connPspCall(String did, int pspId, {int channel = 0}) 

/// 删除预置点 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connPspDel(String did, int pspId, {int channel = 0}) 

/// 获取预置点 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connPspList(String did, {int channel = 0}) 

/// 云台控制 /// 参考源码local_grpc.dart await ipc.LocalGrpc().connPtzCtrl(String did, int ptz, {int channel = 0, int para1 = 0, int para2 = 0}) 

/// 重启设备 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connReboot(String did, {int channel = 0,}) 

/// 重置设备 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connReset(String did, {int channel = 0,}) 

##### /// 获取设备最新截图 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connScreenshot(String did, {int channel = 0,}) 

##### /// 获取私有模式 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connSecretGet(String did, {int channel = 0,}) 

##### /// 开启私有模式,不处理音视频,不录像 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connSecretSet(String did, int secret, {int channel = 0,}) 

##### /// 格式化存储 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connStorageFormat(String did, {int channel = 0}) 

##### /// 获取存储基本信息 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connStorageInfo(String did, {int channel = 0}) 

##### /// 获得设备时间 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connTimeGet(String did, {int channel = 0}) 

##### /// 设置设备时间 

/// 参考源码local_grpc.dart 

await ipc.LocalGrpc().connTimeSet(String did, int nowTime, String timeZone, int dst, int offset, {int channel = 0}) 

/// 获取定时巡航参数 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connTimedcruiseGet(String did, {int channel = 0}) 

/// 设置定时巡航 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connTimedcruiseSet(String did, int state, int mode, Time.Timetask tt, int interval, {int channel = 0}) 

/// 获取喇叭音量 /// 参考源码local_grpc.dart await ipc.LocalGrpc().connVolumeGet(String did, {int channel = 0}) 

/// 调整喇叭音量 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connVolumeSet(String did, int volume, {int channel = 0}) 

/// 获取设备当前WIFI参数 /// 参考源码local_grpc.dart await ipc.LocalGrpc().connWifiGet(String did, {int channel = 0}) 

/// 变更设备当前WIFI连接参数 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connWifiSet(String did, String ssid, String pwd, {int channel = 0}) 

/// 获取WIFI路由列表 /// 参考源码local_grpc.dart await ipc.LocalGrpc().connWifiAPGet(String did, {int channel = 0}) 

/// 传输IOT命令 /// 参考源码local_grpc.dart await ipc.LocalGrpc().connExecIOTCMD(String did, Iot.PpiotCmd? iotCmds, Iot.TimetaskCmd? ttcmd, {int channel = 0}) 

/// 获取OSD参数 /// 参考源码local_grpc.dart await ipc.LocalGrpc().connOsdGet(String did, {int channel = 0}) 

/// 设置OSD参数 /// 参考源码local_grpc.dart await ipc.LocalGrpc().connOsdSet(String did, ConnOsdSet.OsdInfo osd, {int channel = 0}) 

/// 获取设备低功耗状态参数 

/// 参考源码local_grpc.dart await ipc.LocalGrpc().connLowPowerGet(String did, {int channel = 0,}) 

/// 设置设备低功耗状态参数 

/// 参考源码local_grpc.dart 

await ipc.LocalGrpc().connLowPowerSet(String did, int state, {int channel = 0}) 

/// 根据did获取wifi名字 /// 参考源码local_grpc.dart await ipc.LocalGrpc().getWifiConf(String did) 

####
