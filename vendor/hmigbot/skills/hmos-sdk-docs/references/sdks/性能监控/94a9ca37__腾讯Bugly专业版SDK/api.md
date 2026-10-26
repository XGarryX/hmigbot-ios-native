# API 说明 

# 信息更新接口 

# Bugly 初始化后,更新必要字段,接口如下。 

/** * 更新 device id * @param deviceId device id */ public static updateDeviceId(deviceId: string); /** * 更新 user id * @param userId user id */ public static async updateUserId(userId: string); / ** * 更新 device model * @param deviceModel */ public static updateDeviceModel(deviceModel: string); 

# 错误上报接口 

# Bugly 支持通过如下两个接口上报 catch Error 或自定义错误。 

/** * 上报 catch Error * @param e Error * @param extraData [ 可选 ] 随错误上报的附加信息,以 userExtraByteData 附件展示 */ public static postError(e: Error, extraData?: string): void; 

/** * 上报自定义错误 * @param name 异常名 * @param message 异常 msg * @param stack 异常堆栈 * @param storeFirst [ 可选 ] 是否 优先存储 db 不立即上报,默认为 false ,仅在异常现场时采集的错误可 设置为 true * @param context [ 可选 ] 如果未初始化 Bugly 调用接口, 传入 context 可记录错误 * @param extraData [ 可选 ] 随错误上报的附 加信息,以 userExtraByteData 附件展示 */ public static postCustomError(name: string, message: string, stack: string, storeFirst: boolean = false, context?: Context, extraData?: string): void; 

# 如即时上报一条自定义错误,且添加附加信息,示例如下: 

Bugly.postCustomError("testErrorName", "testErrorMsg", "at testErrorStack 1\nat testErrorStack 2", false, undefined, "This is extra data file content"); 

# 提醒 

postError 接口适用于 arkTs 中 catch 异常的捕获,直接传入 catch 错误 的 Error 实例,会自动从 Error 实例中解析出对应的异常名称及堆栈信 息。 

postCustomError 接口适用于上报自定义异常,如采用跨端框架、游 戏框架的异常。如果在正常环境下, storeFirst 参数无需设置,如果 在进程可能被系统杀死环境下,建议设置 storeFirst 参数为 true ,当 前只以同步方式保存异常到本地文件,二次启动进程时上报。 

postCustomError 在 0.4.1 及之后的 SDK 版本支持跨线程上报错误, 但需在主线程初始化 Bugly ,或设置 storeFirst 参数设置为 true 。 

上述错误上报接口在 0.4.1 及之后的 SDK 版本中支持携带附加信息, 如有设置 extraData 附加信息参数,错误上报后,将在错误详情中 以 userExtraByteData 附件的形式提供下载。 

错误上报在 0.4.1 及之后的 SDK 版本中支持配置控制采样率,设置方 式可参考 SDK 配置。 

错误上报后,在如下 TAB 中进行展示。错误支持 arkTs 与 native 堆栈翻 译,如是自定义错误上报,需保证与崩溃堆栈格式相同。 

# 自定义数据接口 

SDK 0.2.0 开始支持设置自定义数据,自定义数据需在 Crash 、 Freeze 或 错误 发生前进行设置,可以进行更新和移除操作,异常上 报时会携带设置的自定义数据。 

/** * 添加或更新自定义数据 * @param key 自定义 key * @param value 自定义 value */ public static putUserData(key: string, value: string); /** * 移除自定义数据 * @param key 自定义 key */ public static removeUserData(key: string); 

/** * 清空自定义数据 */ public static clearUserData(); 

上报的自定义数据将在问题详情 -> 现场数据 -> 自定义字段 中进行 展示,如下图所示。 

# 自定义附件接口 

SDK 0.2.0 开始支持设置业务自定义附件,自定义附件上报当前只支 持 Crash 和 Freeze 。在发生异常前,通过如下接口设置自定义附件 的路径。 

/** * 设置自定义文件路径 * 传入参数为 string 数组,受限于 AppEvent 参数限制,数组值长度需在 1024 个字符以内 * @param paths 自定义文件路径 */ public static async setCustomFilePaths(paths: Array<string>); 

发生异常重启进程后,自定义附件会进行打包上传,在附件中展示 为 custom_log.gzip 。 

# 注意事项 

自定义数据、自定义附件、自定义标签及现场信息的关联均会使用到 系统 hiAppEvent.setEventParam 接口,该接口设置参数值长度需在 1024 个字符以内,且至多设置 64 个键值对。因此 自定义附件 Array 的 所有值长度和需在 1024 个字符以内 ,否则可能设置失败。 

如果业务有自行设置系统 hiAppEvent.setEventParam 接口,请务必 预留一定数量的键值对供 Bugly 设置 (5 个以上 ) ,否则可能影响自定义 数据、附件或现场信息关联。 

# 自定义标签接口 

SDK 0.4.1 开始支持业务自定义个例标签设置,标签随异常个例上 报。个例标签需先在 Bugly 管理台 设置 -> 产品配置 -> 标签 中进行 申请,如下所示。 

# 接着通过如下 SDK 接口,在代码中设置自定义标签 ID ,异常个例上报 时会同时上报这些标签 ID 。 

/** * 设置个例标签 * @param caseLabel 个例标签数组 */ public static async setCaseLabel(caseLabel: Array<string>); 

# 如设置如下自定义标签。 

await Bugly.setCaseLabel(["22096", "22103", "22244"]); 

# 个例标签展示如下。 

提示 

# 重复调用自定义标签接口设置时,标签值会进行覆盖。 

# 自定义场景接口 

SDK 0.5.0 开始支持业务自定义场景,自定义场景可应用在异常时的 场景字段,以及性能指标的场景下钻中。 

# 业务自定义场景字段设置接口如下: 

/** * 进入自定义场景 * @param sceneName 自定义场景 */ public static enterScene(sceneName: string): void; /** * 退出自定义场景 * @param sceneName 自定义场景 */ public static exitScene(sceneName: string): void; 

# 注意 

业务自定义场景字段设置一般适用于跨端框架、自定义组件等无法通 过鸿蒙原生页面生命周期回调拿到页面名称的情况。 

自定义场景的进入与退出设置需成对出现,若调用退出自定义场景的 名称与当前场景名称不符,则不会退出;若多次调用进入自定义场 景,则后调用的场景名称会覆盖之前的设置。 

自定义场景在异常时的展示示例: 

# 日志导出接口 

SDK 0.2.0 开始支持导出 Bugly 日志打印到业务日志系统中(不设置则 默认打印到系统 HiLog 日志系统中),在初始化前调用如下接口进行 设置 。 

/** * 设置 Bugly 日志适配器 * @param adapter 适配器 */ public static setLogAdapter(adapter: BuglyLogAdapter); /** * Bugly 日志适 配接口 */ export interface BuglyLogAdapter { // debug 级别日志 debug(tag: string, arg: string): void; // info 级别日志 info(tag: string, arg: string): void; // warn 级别日志 warn(tag: string, arg: string): void; // error 级别日志 error(tag: string, arg: string): void; // fatal 级 别日志 fatal(tag: string, arg: string): void; } 

# 注意 

SDK 0.3.7 及之后的版本新增了日志导出接口 tag 参数,如有导出 Bugly 日志,请进行适配调整。 

# FaultLog 附件管理接口 

Bugly 注册系统异常回调后,会自动管理系统异常 FaultLog 文件,默 认上报完后会进行删除,否则缓存区满会影响后续 FaultLog 文件生 成。如不希望 Bugly 对 FaultLog 文件进行删除,而是自行管理,可通 过以下接口进行设置。 

/** * 设置是否在 bugly 上报完 fault log 附件后删除 * @param shouldDelete 是否需要 bugly 删除 */ public static setDeleteFaultLogFileAfterUpload(shouldDelete: boolean); 

# 异常回调接口 

SDK 0.3.3 开始支持 Js Crash 、 Cpp Crash 的异常回调,方便在发生异 常时,能回调业务进行一些自定义操作。 

SDK 0.3.5 也提供 HiAppEvent 收到异常信息时的回调,简化业务注册 流程,设置接口如下。 

/** * 异常回调接口 */ export interface ICrashListener { /** * 异常 发生时回调 * @param crashType 异常类型,当前仅支持 JsCrash 、 CppCrash * @param crashName 异常名称,具体异常名称 * @param crashMsg 异常信息, CppCrash 不支持 * @param crashStack 异常堆栈, CppCrash 不支持 */ onCrash(crashType: string, crashName: string, crashMsg: string, crashStack: string): void; /** 

* HiAppEvent 收到异常信息时回调,支持 Crash 和 Freeze * @param crashType 异常类型 * @param crashName 异常名称 * @param crashMsg 异常信息 * @param crashStack 异常堆栈 */ onHiAppEventReceive(crashType: string, crashName: string, crashMsg: string, crashStack: string): void; } 

# 设置异常回调接口示例如下。 

// 在 Bugly 初始化前定义接口实现 class DemoCrashListener implements ICrashListener { onCrash(crashType: string, crashName: string, crashMsg: string, crashStack: string): void { 

```arkts
console.info('receive callback in demo.'); console.info(`Crash Type: ${crashType}`); console.info(`Crash Name: ${crashName}`); console.info(`Crash Message: ${crashMsg}`); console.info(`Crash Stack: ${crashStack}`); } onHiAppEventReceive(crashType: string, crashName: string, crashMsg: string, crashStack: string): void { console.info('[demo] receive hiAppEvent crash in demo.'); console.info(`[demo] Crash Type: ${crashType}`); console.info(`[demo] Crash Name: ${crashName}`); console.info(`[demo] Crash Message: ${crashMsg}`); console.info(`Crash Stack: ${crashStack}`); } } // Bugly 初始化逻辑 let builder = new BuglyBuilder(); ... // 初始化时将接口示例传递给 builder.crashListener 参数 builder.crashListener = new DemoCrashListener(); ... await Bugly.init(context, builder); 
```

# 注意事项 

暂不支持 App Freeze 异常回调。 

# Cpp Crash 回调暂不支持提供堆栈信息。 

请勿在回调中进行复杂操作,异常现场回调暂时无法保障稳定性,可 能引入未知风险,请谨慎开启。 

# 动态开关 

SDK 支持质量和性能异常监控模块动态开关,可通过以下接口在业务 需要的场景中动态开启或关闭异常监控上报。 

/** * 质量异常监听动态开关 * @param isFreeze true 为 Freeze 监控, false 为 Crash 监控 ( 包括 Js Crash 和 Cpp Crash) * @param isAble 打开 或关闭 */ public static setCrashMonitorAble(isFreeze: boolean, isAble: boolean): void; /** * 性能模块动态开关 * @param modules 性能模块项或列表 * @param isAble 打开或关闭 */ public static setPerfMonitorsAble(modules: string | Array<string>, isAble: boolean): void;
