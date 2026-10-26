### 2025/11/5 16:49

### Harmony(鸿蒙) SDK 接入指南 | Bugly 专业版

接入指引

Harmony(鸿蒙)

# Harmony(鸿蒙) SDK 接入指南

# Bugly Harmony SDK 简介

Bugly Harmony版本,支持Harmony OS Next平台基础异常问题的捕获上报,包含Js异常、Cpp异常、AppFreeze、

错误,异常捕获后上报到Bugly平台。Bugly Harmony SDK 基于Harmony平台arkTs开发,可通过Har包集成方式接

入,提供arkTs接口。

提醒

Bugly鸿蒙专业版暂时对业务提供免费开放支持。

# 一、注册 Harmony产品

1、在Bugly平台上注册产品,平台选择Harmony 。

2、按照提示填写产品相关信息,Bundle ID字段可填写鸿蒙AppScope->app.json5中定义的bundleName字段。

3、注册完成后,可在左侧栏- 设置- 产品信息查看APP ID、APP KEY等信息。

# 二、集成 Bugly SDK

## 自动集成(推荐)

1、配置内网鸿蒙三方库,执行以下命令。(设置默认存在该三方库,则无需配置)

### https://bugly.tds.qq.com/docs/sdk/harmony/

### 1/10

### 2025/11/5 16:49

### Harmony(鸿蒙) SDK 接入指南 | Bugly 专业版

```
ohpm config set registry https://ohpm.openharmony.cn/ohpm/
```

提醒

设置默认原始只有鸿蒙官方三方库,如添加了其他三方库,需通过ohpm config list查看设置的三方库,手

```
动将https://ohpm.openharmony.cn/ohpm/追加后重新设置。
```

2、通过ohpm安装bugly库。

```
ohpm install bugly@0.5.0
```

3、安装完成后可直接在arkTs中通过import导入引用。

## 手动集成

1、通过三方仓库或其他渠道下载Bugly.har三方SDK包。

2、在需要集成的模块下创建libs目录,将Bugly.har放入目录。

3、在模块的oh-package.json5文件中添加对应dependencies ,如下所示。

```
"dependencies": {
"bugly": "file:./libs/Bugly.har"
}
```

# 三、混淆规则配置

注意

业务二次混淆Har包代码,可能导致部分Napi符号或字符串变量不可见,引入运行问题,建议业务直接keep

Bugly Har包。

在hap工程目录下obfuscation-rules.txt混淆规则配置文件中直接添加如下规则。

```
-keep
../oh_modules/bugly
```

# 四、初始化 Bugly SDK

参考以下代码初始化 Bugly Harmony SDK,我们推荐尽早可能初始化SDK,如将初始化逻辑放在Ability的

onCreate生命周期中。可参考如下代码进行初始化。

```
import { Bugly, BuglyBuilder, AppVersionMode, ModuleName } from"bugly";
initBugly(context: Context): void {
let builder = new BuglyBuilder();
    builder.appId = 'xxxxxxx';   // 必填,Bugly产品信息中的APP ID
    builder.appKey = 'xxx-xxxx-xxxx-xxxx-xxxx';    // 必填,Bugly产品信息中的APP KEY
    builder.deviceId = "12345";     // 必填,设备ID,应保证设备ID对不同设备唯一
    builder.platform = BuglyBuilder.PLATFORM_PRO;    // 必填,设置上报平台,专业版本需设置为
[BuglyBuilder.PLATFORM_PRO]
    builder.appVersion = '1.0.0';   // 选填,业务的App版本
    builder.appVersionMode = AppVersionMode.DEBUG;  // 选填,当前App的版本类型,支持根据不同的版
```

本类型下发配置

```
    builder.buildNum = '0';         // 选填,业务App版本的构建号
    builder.appChannel = 'website'; // 选填,业务App渠道
    builder.userId = "12345";       // 选填,用户ID,如不设置则为空
    builder.deviceModel = "huawei"; // 选填,机型,如不设置则为空
    builder.debugMode = true;       // 选填,默认开启,开启后Bugly SDK会打印更多调试日志,线上版本
```

可关闭

```
    builder.sdkLogMode = true;      // 选填,设置debugMode或sdkLogMode均可开启Bugly sdk日志,适
```

用于线上关闭debug模式但又希望打印bugly日志的场景

```
    builder.initDelay = 0;          // 选填,延迟初始化时间,单位ms
    builder.enableJsCrashProtect = false;   // 选填,是否开启Js异常崩溃保护,设置为true后发生未捕
```

获Js异常,进程不会退出

```
    builder.enablePerfModules = ModuleName.AllModules;  // 选填,开启性能监控项,可传入单个性能模
```

块名称或一组性能模块名称,此处初始化后,还需配置开启对应模块采样率,模块才会真正开启

```
    Bugly.init(context, builder);   // 如果需等待Bugly完全初始化完成,使用await
Bugly.init(context, builder);
}
```

注意事项

1. Context需要传递ApplicationContext。

2.设备ID非常重要,Bugly使用设备ID来计算设备异常率,强烈建议应用设置正确的设备ID,以确保设备的唯

一性。

3. BuglyBuilder需在init方法前创建,且应避免重复调用init方法。

4.需要在调用Bugly.init接口,完成初始化后,再调用其他接口,进行定制化设置,否则设置不生效。

### https://bugly.tds.qq.com/docs/sdk/harmony/

### 2/10

### 2025/11/5 16:49

### Harmony(鸿蒙) SDK 接入指南 | Bugly 专业版

5.在同一进程中,应只初始化一次Bugly,仅建议在主线程中初始化,0.4.1及之后的SDK版本仅支持在主线

程中初始化。

# 五、验证数据上报

## 崩溃监控

初始化完成后,可以模拟崩溃进行上报,如执行以下调用。

```
Bugly.testCrash(Bugly.JS_CRASH); // 模拟Js异常
Bugly.testCrash(Bugly.CPP_CRASH); // 模拟native异常
```

提醒

1.异常问题发生后,需要二次启动Hap应用,即可完成上报。

2. Crash异常会上报FaultLog信息,可在附件tab的crashInfos.txt文件中查看。

异常上报后,可在崩溃->问题列表中查看上报问题,点击进入问题详情,查看上报内容。

## Freeze监控

与崩溃类似,可以通过Bugly提供的测试接口来模拟Freeze,调用后适当滑动屏幕,系统将判定为当前进程Freeze。

```
Bugly.testCrash(Bugly.APP_FREEZE); // 模拟Freeze异常
```

或是在UI线程中执行耗时逻辑,触发ANR。

```
let index = 0
while (true) {
    index++
    index = index % 2
}
```

Freeze问题触发上报后,在Freeze->问题列表中查看,点击进入问题详情,查看上报内容。

提醒

1. Freeze异常上报的是Native、arkTs混合堆栈。

2. Freeze异常会上报FaultLog信息及主线程消息信息,可在附件tab的crashInfos.txt文件中查看,

event_handler表示主线程未处理消息,event_handler_size_3s表示THREAD_BLOCK事件3s时任务

栈中任务数, event_handler_size_6s表示THREAD_BLOCK事件6s时任务栈中任务数,peer_binder表

示binder调用信息。

## 卡顿监控

卡顿指标(FPS、挂起率)

### https://bugly.tds.qq.com/docs/sdk/harmony/

### 3/10

### 2025/11/5 16:49

### Harmony(鸿蒙) SDK 接入指南 | Bugly 专业版

注意

确保卡顿指标模块开启,需在buglybuilder初始化参数enablePerfModules中添加卡顿指标模块

```
(ModuleName.JANK_METRIC ,使用ModuleName.AllModules 无需添加),同时在配置中设置卡顿指标的
```

sample_ratio设备采样率,二者缺一不可。

建议测试时,配置设备采样率设为1,设置方式可参考配置使用。

指标说明:

FPS:帧率,在应用运行时,GPU和CPU合作可产生的图像数量,反应了UI图像刷新的频率,计量单位帧/秒

(FramePerSecond,缩写FPS),通常是评估硬件性能与应用流畅度的指标。鸿蒙FPS的计算借鉴了Android、

iOS实现方式,采用归一化的方式进行统计,以60HZ为基准,突出反映应用在影响用户体验(低于60HZ)运行

时的状态,即应用越流畅,归一化FPS越接近60HZ,反之越低。

挂起率:如果应用在主线程中的单条消息执行时间过长,则可能导致UI卡顿,此时认为应用不能很好地响应用户

的交互,累计执行的时间到挂起时间中。一个设备的挂起率,指这个设备在一天中,总的挂起时间除以其前台总

时长,单位是秒/小时。

验证上报:

初始化卡顿指标能力并命中采样后,在debug模式下,可以看到如下日志,以判断卡顿指标已被开启。

```
03-27 20:05:31.683   14562-14562   A00000/com.ten...looper_metric  com.tencent.bugly     I
Jank metric module start!
```

在有多个页面切换,并切换前后台时,可以看到卡顿指标上报日志。

```
04-02 15:12:34.938   61473-61473   A00000/com.tencent.bugly/Bugly  com.tencent.bugly     I
[Upload] upload Success, upload event: looper_metric, record id: a84630f6-ffb4-4d9b-8033-
8c288507d58f.
```

卡顿指标上报后,可在如下页面中查看对应数据统计,并支持App版本、页面场景等维度下钻分析。

提示

1.卡顿指标以页面场景为统计维度,在应用有页面切换时记录指标数据,退至后台时上报数据。

2.应尽早初始化Bugly,才能及时开启卡顿指标的统计。如果Bugly初始化时间较晚,将在用户下一次切前后

台操作后开启采集。

卡顿个例

注意

确保卡顿个例模块开启,需在buglybuilder初始化参数enablePerfModules中添加卡顿个例模块

(ModuleName.JANK ,使用ModuleName.AllModules 无需添加),同时在配置中设置卡顿个例的

sample_ratio设备采样率,二者缺一不可。

建议测试时,配置设备采样率设为1,设置方式可参考配置使用。

个例说明:

卡顿堆栈监控能力基于系统API 5.0.0(12) HiAppEvent主线程超时事件开发,兼容API 12及以上版本,默认超时

时间150ms,抓栈次数固定10次,在进程生命周期中,仅会触发一次。详情可参考:鸿蒙主线程超时事件。

验证上报:

初始化卡顿个例监控并命中采样后,在debug模式下,可以看到如下日志,以判断卡顿个例监控已被开启。

```
03-27 20:05:31.683   14562-14562   A00000/com.ten...-looper_stack  com.tencent.bugly     I
Jank monitor module start!
```

可通过在点击事件中连续触发以下代码,来构造触发卡顿事件。

```
let t = Date.now();
while (Date.now() - t <= 350) {}
```

成功触发后,可看到如下上报日志,表明卡顿个例已成功上报。

```
04-02 16:06:24.405   61473-61473   A00000/com.ten...-looper_stack  com.tencent.bugly     I
[Jank] jank event received!!! domain: OS
```

### https://bugly.tds.qq.com/docs/sdk/harmony/

### 4/10

### 2025/11/5 16:49

### Harmony(鸿蒙) SDK 接入指南 | Bugly 专业版

```
04-02 16:06:24.406   61473-61473   A00000/com.ten...-looper_stack  com.tencent.bugly     I
[Jank] event group name: MAIN_THREAD_JANK
04-02 16:06:24.406   61473-61473   A00000/com.ten...-looper_stack  com.tencent.bugly     I
[Jank] jank begin time: 1743581180178, end time: 1743581180530, log paths:
["/data/storage/el2/log/watchdog/MAIN_THREAD_JANK_20250402160622_61473.txt"]
04-02 16:06:26.170   61473-61473   A00000/com.tencent.bugly/Bugly  com.tencent.bugly     I
bugly do upload, type: 3, event: looper_stack
04-02 16:06:26.453   61473-61473   A00000/com.tencent.bugly/Bugly  com.tencent.bugly     I
[Upload] upload Success, upload event: looper_stack, record id: cd6623ba-e5e5-474d-b70b-
bf087120aa44.
```

卡顿个例上报后,可在如下页面中查看抓取全部堆栈聚合而成的火焰图、堆栈树数据,堆栈支持上传符号表翻译。

## 内存监控

内存指标

注意

确保内存指标模块开启,需在buglybuilder初始化参数enablePerfModules中添加内存指标模块

```
(ModuleName.MEMORY_METRIC ,使用ModuleName.AllModules 无需添加),同时在配置中设置内存指标
```

的sample_ratio设备采样率,二者缺一不可。

建议测试时,配置设备采样率设为1,设置方式可参考配置使用。

Bugly鸿蒙内存指标统计应用运行时内存峰值,当一个进程使用的内存越多,被系统kill掉的风险就越大,GC导致的性

能问题影响也越大,内存峰值指标可以在一定程度上衡量这些问题的影响程度。

指标说明:

PSS:进程生命周期里达到的最大物理内存占用(含按比例分配的共享内存部分)大小。

VSS:进程生命周期里达到的最大虚拟内存占用大小。

JS堆:进程生命周期里达到的最大JS堆内存占用大小。

验证上报:

初始化内存指标能力并命中采样后,在debug模式下,可以看到如下日志,以判断内存指标上报已命中采样。

```
09-22 19:16:19.437   10331-10331   A00000/com.ten...mory_quantile  com.tencent.bugly     I
Memory metric collector start!
09-22 19:16:19.437   10331-10331   A00000/com.ten...mory_quantile  com.tencent.bugly     I
Start to upload memory metric data after delay time.
```

在进程启动时,会上报上一个进程的内存峰值指标数据,可以看到如下上报日志。

```
09-22 19:16:19.700   10331-10331   A00000/com.tencent.bugly/Bugly  com.tencent.bugly     I
[Upload] upload Success, upload event: memory_quantile, record id: 6cd87765-f779-4a3c-b7fe-
2bfa068e3f19.
```

内存指标上报后,可以在如下页面中查看对应数据统计,指标支持场景、APP版本、系统版本、机型等字段下钻分

析。

# API说明

### https://bugly.tds.qq.com/docs/sdk/harmony/

### 5/10

### 2025/11/5 16:49

### Harmony(鸿蒙) SDK 接入指南 | Bugly 专业版

## 信息更新接口

Bugly初始化后,更新必要字段,接口如下。

```
/**
 * 更新device id
 * @param deviceId device id
 */
public staticupdateDeviceId(deviceId: string);
/**
 * 更新user id
 * @param userId user id
 */
public staticasyncupdateUserId(userId: string);
/**
 * 更新device model
 * @param deviceModel
 */
public staticupdateDeviceModel(deviceModel: string);
```

## 错误上报接口

Bugly支持通过如下两个接口上报catch Error或自定义错误。

```
/**
 * 上报catch Error
 * @param e Error
 * @param extraData [可选] 随错误上报的附加信息,以userExtraByteData附件展示
 */
public staticpostError(e: Error, extraData?: string): void;
/**
```

 * 上报自定义错误

```
 * @param name 异常名
 * @param message 异常msg
 * @param stack 异常堆栈
```

 * @param storeFirst [可选] 是否优先存储db不立即上报,默认为false,仅在异常现场时采集的错误可设置为

```
true
 * @param context [可选] 如果未初始化Bugly调用接口,传入context可记录错误
 * @param extraData [可选] 随错误上报的附加信息,以userExtraByteData附件展示
 */
public staticpostCustomError(name: string, message: string, stack: string, storeFirst:
boolean = false, context?: Context, extraData?: string): void;
```

如即时上报一条自定义错误,且添加附加信息,示例如下:

```
Bugly.postCustomError("testErrorName", "testErrorMsg", "at testErrorStack 1\nat
testErrorStack 2", false, undefined, "This is extra data file content");
```

提醒

1.postError接口适用于arkTs中catch异常的捕获,直接传入catch错误的Error实例,会自动从Error实例中

解析出对应的异常名称及堆栈信息。

2.postCustomError接口适用于上报自定义异常,如采用跨端框架、游戏框架的异常。如果在正常环境下,

storeFirst参数无需设置,如果在进程可能被系统杀死环境下,建议设置storeFirst参数为true,

当前只以同步方式保存异常到本地文件,二次启动进程时上报。

3.postCustomError在0.4.1及之后的SDK版本支持跨线程上报错误,但需在主线程初始化Bugly,或设置

storeFirst参数设置为true。

4.上述错误上报接口在0.4.1及之后的SDK版本中支持携带附加信息,如有设置extraData附加信息参

数,错误上报后,将在错误详情中以userExtraByteData附件的形式提供下载。

5.错误上报在0.4.1及之后的SDK版本中支持配置控制采样率,设置方式可参考 SDK配置。

错误上报后,在如下TAB中进行展示。错误支持arkTs与native堆栈翻译,如是自定义错误上报,需保证与崩溃堆栈格

式相同。

## 自定义数据接口

SDK 0.2.0开始支持设置自定义数据,自定义数据需在Crash、Freeze或错误发生前进行设置,可以进行更新和

移除操作,异常上报时会携带设置的自定义数据。

```
/**
```

 * 添加或更新自定义数据

```
 * @param key 自定义key
 * @param value 自定义value
```

### https://bugly.tds.qq.com/docs/sdk/harmony/

### 6/10

### 2025/11/5 16:49

### Harmony(鸿蒙) SDK 接入指南 | Bugly 专业版

```
 */
public staticputUserData(key: string, value: string);
/**
```

 * 移除自定义数据

```
 * @param key 自定义key
 */
public staticremoveUserData(key: string);
/**
```

 * 清空自定义数据

```
 */
public staticclearUserData();
```

上报的自定义数据将在问题详情->现场数据->自定义字段中进行展示,如下图所示。

## 自定义附件接口

SDK 0.2.0开始支持设置业务自定义附件,自定义附件上报当前只支持Crash和Freeze。在发生异常前,通过如

下接口设置自定义附件的路径。

```
/**
```

 * 设置自定义文件路径

 * 传入参数为string数组,受限于AppEvent参数限制,数组值长度需在1024个字符以内

```
 * @param paths 自定义文件路径
 */
public staticasyncsetCustomFilePaths(paths: Array<string>);
```

发生异常重启进程后,自定义附件会进行打包上传,在附件中展示为custom_log.gzip 。

注意事项

1.自定义数据、自定义附件、自定义标签及现场信息的关联均会使用到系统hiAppEvent.setEventParam接

口,该接口设置参数值长度需在1024个字符以内,且至多设置64个键值对。因此自定义附件Array的所有

值长度和需在1024个字符以内,否则可能设置失败。

2.如果业务有自行设置系统hiAppEvent.setEventParam接口,请务必预留一定数量的键值对供Bugly设置

(5个以上),否则可能影响自定义数据、附件或现场信息关联。

## 自定义标签接口

SDK 0.4.1开始支持业务自定义个例标签设置,标签随异常个例上报。个例标签需先在Bugly管理台设置->产品配

置->标签中进行申请,如下所示。

接着通过如下SDK接口,在代码中设置自定义标签ID,异常个例上报时会同时上报这些标签ID。

```
/**
```

   * 设置个例标签

```
   * @param caseLabel 个例标签数组
   */
public staticasyncsetCaseLabel(caseLabel: Array<string>);
```

如设置如下自定义标签。

```
await Bugly.setCaseLabel(["22096", "22103", "22244"]);
```

个例标签展示如下。

### https://bugly.tds.qq.com/docs/sdk/harmony/

### 7/10

|  |  | 置 |
|---|---|---|

### 2025/11/5 16:49

### Harmony(鸿蒙) SDK 接入指南 | Bugly 专业版

提示

重复调用自定义标签接口设置时,标签值会进行覆盖。

## 自定义场景接口

SDK 0.5.0开始支持业务自定义场景,自定义场景可应用在异常时的场景字段,以及性能指标的场景下钻中。

业务自定义场景字段设置接口如下:

```
/**
```

 * 进入自定义场景

```
 * @param sceneName 自定义场景
 */
public staticenterScene(sceneName: string): void;
/**
```

 * 退出自定义场景

```
 * @param sceneName 自定义场景
 */
public staticexitScene(sceneName: string): void;
```

注意

1.业务自定义场景字段设置一般适用于跨端框架、自定义组件等无法通过鸿蒙原生页面生命周期回调拿到页面

名称的情况。

2.自定义场景的进入与退出设置需成对出现,若调用退出自定义场景的名称与当前场景名称不符,则不会退

出;若多次调用进入自定义场景,则后调用的场景名称会覆盖之前的设置。

自定义场景在异常时的展示示例:

## 日志导出接口

SDK 0.2.0开始支持导出Bugly日志打印到业务日志系统中(不设置则默认打印到系统HiLog日志系统中),在初始化

前调用如下接口进行设置。

```
/**
```

 * 设置Bugly日志适配器

```
 * @param adapter 适配器
 */
public staticsetLogAdapter(adapter: BuglyLogAdapter);
/**
```

 * Bugly日志适配接口

```
 */
export interface BuglyLogAdapter {
// debug级别日志
debug(tag: string, arg: string): void;
// info级别日志
info(tag: string, arg: string): void;
// warn级别日志
warn(tag: string, arg: string): void;
// error级别日志
error(tag: string, arg: string): void;
// fatal级别日志
fatal(tag: string, arg: string): void;
}
```

注意

SDK 0.3.7及之后的版本新增了日志导出接口tag参数,如有导出Bugly日志,请进行适配调整。

## FaultLog附件管理接口

Bugly注册系统异常回调后,会自动管理系统异常FaultLog文件,默认上报完后会进行删除,否则缓存区满会影响

后续FaultLog文件生成。如不希望Bugly对FaultLog文件进行删除,而是自行管理,可通过以下接口进行设置。

```
/**
```

 * 设置是否在bugly上报完fault log附件后删除

```
 * @param shouldDelete 是否需要bugly删除
 */
public staticsetDeleteFaultLogFileAfterUpload(shouldDelete: boolean);
```

## 异常回调接口

### https://bugly.tds.qq.com/docs/sdk/harmony/

### 8/10

### 2025/11/5 16:49

### Harmony(鸿蒙) SDK 接入指南 | Bugly 专业版

SDK 0.3.3开始支持Js Crash、Cpp Crash的异常回调,方便在发生异常时,能回调业务进行一些自定义操作。

SDK 0.3.5也提供HiAppEvent收到异常信息时的回调,简化业务注册流程,设置接口如下。

```
/**
```

 * 异常回调接口

```
 */
export interface ICrashListener {
/**
```

   * 异常发生时回调

```
   * @param crashType 异常类型,当前仅支持 JsCrash、CppCrash
   * @param crashName 异常名称,具体异常名称
   * @param crashMsg 异常信息,CppCrash不支持
   * @param crashStack 异常堆栈,CppCrash不支持
   */
onCrash(crashType: string, crashName: string, crashMsg: string, crashStack: string):
void;
/**
   * HiAppEvent收到异常信息时回调,支持Crash和Freeze
   * @param crashType 异常类型
   * @param crashName 异常名称
   * @param crashMsg 异常信息
   * @param crashStack 异常堆栈
   */
onHiAppEventReceive(crashType: string, crashName: string, crashMsg: string, crashStack:
string): void;
}
```

设置异常回调接口示例如下。

// 在Bugly初始化前定义接口实现

```
class DemoCrashListener implements ICrashListener {
onCrash(crashType: string, crashName: string, crashMsg: string, crashStack: string): void
{
    console.info('receive callback in demo.');
    console.info(`Crash Type: ${crashType}`);
    console.info(`Crash Name: ${crashName}`);
    console.info(`Crash Message: ${crashMsg}`);
    console.info(`Crash Stack: ${crashStack}`);
  }
onHiAppEventReceive(crashType: string, crashName: string, crashMsg: string, crashStack:
string): void {
    console.info('[demo] receive hiAppEvent crash in demo.');
    console.info(`[demo] Crash Type: ${crashType}`);
    console.info(`[demo] Crash Name: ${crashName}`);
    console.info(`[demo] Crash Message: ${crashMsg}`);
    console.info(`Crash Stack: ${crashStack}`);
  }
}
// Bugly初始化逻辑
let builder = new BuglyBuilder();
...
// 初始化时将接口示例传递给builder.crashListener参数
builder.crashListener = new DemoCrashListener();
...
await Bugly.init(context, builder);
```

注意事项

1.暂不支持App Freeze异常回调。

2. Cpp Crash回调暂不支持提供堆栈信息。

3.请勿在回调中进行复杂操作,异常现场回调暂时无法保障稳定性,可能引入未知风险,请谨慎开启。

## 动态开关

SDK支持质量和性能异常监控模块动态开关,可通过以下接口在业务需要的场景中动态开启或关闭异常监控上报。

```
/**
```

 * 质量异常监听动态开关

```
 * @param isFreeze true为Freeze监控,false为Crash监控(包括Js Crash和Cpp Crash)
 * @param isAble 打开或关闭
 */
public staticsetCrashMonitorAble(isFreeze: boolean, isAble: boolean): void;
/**
```

 * 性能模块动态开关

```
 * @param modules 性能模块项或列表
 * @param isAble 打开或关闭
 */
public staticsetPerfMonitorsAble(modules: string | Array<string>, isAble: boolean): void;
```

# FAQ

## 1.为什么本地崩溃没有上报?如何进行排查?

首先确认Bugly本地已被正确初始化,在初始化时将Bugly的debug模式builder.debugMode设置为true,查看hiLog

日志打印如下,则表明Bugly已被正确初始化。

### https://bugly.tds.qq.com/docs/sdk/harmony/

### 9/10

### 2025/11/5 16:49

### Harmony(鸿蒙) SDK 接入指南 | Bugly 专业版

|  | 04-18 00:30:20.192 11522-11522 A00000/Bugly pid-11522 I ------------------------------- ------------------------------------------------------------- 04-18 00:30:20.192 11522-11522 A00000/Bugly pid-11522 I [init] Bugly debug模式开启 -- Bugly running in debug model. 04-18 00:30:20.192 11522-11522 A00000/Bugly pid-11522 I [init] Bugly debug模式将输出详细 SDK Log -- More detailed log of Bugly SDK will be output in debug model. 04-18 00:30:20.192 11522-11522 A00000/Bugly pid-11522 I ------------------------------- ------------------------------------------------------------- |
|---|---|
| Bugly监控定位 无极智能低码 Hippy开发框架 Shiply容器与发布 Copyright © 1998 - 2024 Tencent. All Rights Reserved. 服务协议 隐私保护声明 腾讯公司 版权所有 主体备案号粤B2-20090059 |  |

| armony(鸿蒙) | 接入指南 |
|---|---|

### https://bugly.tds.qq.com/docs/sdk/harmony/

### 10/10
