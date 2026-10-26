# **鸿蒙 TalkSDK API 接口说明** 

文档版本: v1.8 

对应 SDK 版本: 2.6.6.5389 及以上版本 

文档更新时间: 2025/02/28 

## **安装** 

ohpm install @youme/voice_engine 

## **相关异步 / 同步处理方法介绍** 

游密音频引擎鸿蒙 SDK 提供了 ArkTs 和 C++ 两套接口,接口调用都会立即返回,凡是本身需要较长耗时的接口调用都会采用异步回调的方式,所有接口都可以在主线程中 直接使用。回调都在子线程中进行,请注意不要在回调中直接操作 UI 主线程。 

## **API 调用说明** 

**ArkTs API** 的调用可通过调用 YouMeRtcAPI.Instance(). 实例方法来直接操作。 **C++ API** 的调用可使用 IYouMeVoiceEngine::getInstance()-> 来直接操作。 

SDK 提供的 ArkTs API 接口文件位于 oh_modules/youme_voice_engine/src/main/ets/components/api.d.ets , C++ API 接口文件位于 oh_modules/youme_voice_engine/include/IYouMeVoiceEngine.h 。 

### 接口使用的基本流程为: 

设置回调 -> 初始化 -> 收到初始化成功回调通知 -> 

加入频道 -> 收到加入频道成功回调通知 -> 

设置语音属性 -> 收到语音属性设置回调 -> 

离开频道 -> 反初始化 

要确保严格按照上述的顺序使用接口。 

## **API 定义描述** 

注册 SDK 事件监听回调 

/** 

### * 注册SDK事件监听回调,需SDK初始化之前设置 

- @param callback SDK事件监听回调,事件回调包含事件类型、错误码、频道号、参数信息 

*/ 

SetEventCallback(callback: (event: YouMeRtcEvent, errCode: YouMeRtcErrorCode, channel: string, param: string) => void): void; 

### 初始化引擎 

### /** 

### * 初始化引擎 

- 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调才表明初始化完成: 

- YOUME_EVENT_INIT_OK,表明初始化成功 

- YOUME_EVENT_INIT_FAILED,表明初始化失败,最常见的失败原因是网络错误或者 AppKey/AppSecret 错误 

- 

- @param appKey 从游密申请到的app key, 应用程序的唯一标识 

- @param appSecret 应用app key的私钥, 需要妥善保存,不要暴露给其他人 

- @param serverRegion 首选连接服务器的区域码,如果在初始化时不能确定区域,可以填RTC_DEFAULT_SERVER 

- @param extServerRegionName 扩展的服务器区域简称 

- @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

Init(appKey: string, appSecret: string, serverRegion: YouMeRtcServerRegion, extServerRegionName: string): YouMeRtcErrorCode; 

### 反初始化引擎 

/** 

- 反初始化引擎,在应用退出之前需要调用这个接口释放资源 

- 这是一个同步调用接口,函数返回时表明操作已经完成 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

UnInit(): YouMeRtcErrorCode; 

判断引擎是否初始化完成 

/** 

### * 判断引擎是否初始化完成 

- @returns 返回true-初始化完成,返回false-初始化没完成 */ 

IsInited(): boolean; 

### 获取 SDK 版本号 

/** 

* 获取SDK版本号 

- @returns 返回四段式SDK版本号,比如1.0.0.0 

*/ 

GetSdkVer(): string; 

### 设置身份验证的 token 和用户加入房间的时间 

/** 

### * 设置身份验证的token和用户加入房间的时间 

- @param token 身份验证用token,设置为空字符串,清空token值 

- @param timeStamp 用户加入房间的时间戳,秒单位 

*/ 

SetTokenV3(token: string, timeStamp: number): void; 

### 设置是否允许使用移动网络 

/** 

### * 设置是否允许使用移动网络。 

- 在WIFI和移动网络都可用的情况下会优先使用WIFI,在没有WIFI的情况下,如果设置允许使用移动网络,那么会使用移动网络进行语音通信,否则通信会 * 该接口需要在初始化后,加入房间前设置。 

- @param enabled true-允许使用移动网络,false-禁止使用移动网络。 

*/ 

SetUseMobileNetworkEnabled(enabled: boolean): void; 

### 获取是否允许使用移动网络 

/** 

- 获取是否允许SDK在没有WIFI的情况使用移动网络进行语音通信。 

- @returns true-允许使用移动网络,false-禁止使用移动网络,默认情况下允许使用移动网络。 

*/ 

GetUseMobileNetworkEnabled(): boolean; 

### 加入语音频道(单频道模式) 

/** 

- 加入语音频道(单频道模式,用户每个时刻只能在一个语音频道里面) 

- 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调才表示加入频道完成: 

- YOUME_EVENT_JOIN_OK,表明加入频道成功 

- YOUME_EVENT_JOIN_FAILED,表明加入频道失败 

* 

- @param user 用户ID,要保证全局唯一 

- @param channel 频道ID,要保证全局唯一 

- @param role 用户角色,用于决定讲话/播放背景音乐等权限 

- @param checkExists 是否检查频道存在时才加入,设置为true表示只有当频道存在时才加入、不存在时返回错误(多用于观众角色),设置为false表示 

- @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

JoinChannelSingleMode(user: string, channel: string, role: YouMeRtcUserRole, checkExists: boolean): YouMeRtcErrorCode; 

加入语音频道(多频道模式) 

/** 

- 加入语音频道(多频道模式,可以同时听多个语音频道的内容,但每个时刻只能对着一个频道讲话) 

- 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调才表示加入频道完成: 

- YOUME_EVENT_JOIN_OK,表明加入频道成功 

- YOUME_EVENT_JOIN_FAILED,表明加入频道失败 

* 

- @param user 用户ID,要保证全局唯一 

- @param channel 频道ID,要保证全局唯一 

- @param role 用户角色,用于决定讲话/播放背景音乐等权限 

- @param checkExists checkExists 是否检查频道存在时才加入,设置为true表示只有当频道存在时才加入、不存在时返回错误(多用于观众角色),设 * @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

JoinChannelMultiMode(user: string, channel: string, role: YouMeRtcUserRole, checkExists: boolean): YouMeRtcErrorCode; 

### 退出所有的语音频道 

/** 

- 退出所有的语音频道(单频道模式下直接调用此函数离开频道即可) 

- 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调才表示退出频道完成: 

- YOUME_EVENT_LEAVED_ALL,成功退出所有语音频道 * * @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

LeaveChannelAll(): YouMeRtcErrorCode; 

### 多频道模式下,退出指定的语音频道 

/** 

- 多频道模式下,退出指定的语音频道 

- @param channel 当前应用程序的范围内唯一的频道标识 

- 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调才表示退出频道完成: 

- YOUME_EVENT_LEAVED_ONE,成功退出指定语音频道 

* 

- @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

LeaveChannelMultiMode(channel: string): YouMeRtcErrorCode; 

### 切换用户身份 

- /** 

- 切换用户身份(仅支持单频道模式,需进入房间以后设置) 

- 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调: 

- YOUME_EVENT_IDENTITY_MODIFY,角色改变事件,此事件的errCode代表角色类型,对应YouMeRtcUserRole定义 

* 

- @param role 新的用户角色,详见YouMeRtcUserRole定义 

- @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetUserRole(role: YouMeRtcUserRole): YouMeRtcErrorCode; 

### 获取用户身份 

/** 

- 功能描述:获取用户身份(仅支持单频道模式) 

- @return 身份定义,详见YouMeRtcUserRole定义 

*/ 

GetUserRole(): YouMeRtcUserRole; 

### 查询用户是否在某个语音频道内 

/** 

### * 查询用户是否在某个语音频道内 

- @param channel 当前应用程序的范围内唯一的频道标识 

- @returns 返回true-在指定频道内,返回false-没有在指定频道内 */ 

IsInChannel(channel: string): boolean; 

查询用户是否在语音频道内 

/** 

* @returns 返回true-在频道内,返回false-没有在频道内 

### * 查询用户是否在语音频道内 

*/ 

IsInAnyChannel(): boolean; 

### 多频道模式下,指定当前要讲话的频道 

/** 

### * 多频道模式下,指定当前要讲话的频道 

- 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调才表示切换频道完成: 

- YOUME_EVENT_SPEAK_SUCCESS,成功切入到指定语音频道 

- YOUME_EVENT_SPEAK_FAILED,切入指定语音频道失败,可能原因是网络或服务器有问题 

* * @param channel 当前应用程序的范围内唯一的频道标识 * @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SpeakToChannel(channel: string): YouMeRtcErrorCode; 

### 暂停通话 

- /** * 暂停通话,释放对麦克风等设备资源的占用 * 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调才表示频道暂停完成: * YOUME_EVENT_PAUSED,暂停语音频道完成 * * @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ PauseChannel(): YouMeRtcErrorCode; 

### 恢复通话 

- /** * 恢复通话,调用PauseChannel暂停通话后,可调用这个接口恢复通话 * 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调才表示频道恢复完成: * YOUME_EVENT_RESUMED,恢复语音频道完成 * * @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ ResumeChannel(): YouMeRtcErrorCode; 

### 注册频道成员变更监听回调 

|/**|
|---|
|*注册语音频道成员变更监听回调,需在sdk查询频道用户列表之前设置(getChannelUserList时需设置notifyMemChange为true才会触发MemberChange回|
|* @param callback语音频道成员变更监听回调 */ SetMemberChangeCallback(callback: (channel: string, members: string, update: boolean) => void): void;|

### 查询频道当前的用户列表 

|/**|
|---|
|*查询频道当前的用户列表,并设置是否获取频道用户进出的通知(OnMemberChange),必须自己在频道中才可以调用此接口 *这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待IYouMeMemberChangeCallback回调获取查询结果 *|
|* @param channel当前应用程序的范围内唯一的频道标识 * @param maxCount想要获取的最大人数。-1表示获取全部列表 * @param notifyMemChange其他用户进出房间时,是否要收到通知,设置为true表示自己所在频道有人进出都会有回调产生,反之false就没有对应回调 * @returns返回YOUME_SUCCESS才会有异步查询结果回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */|
|GetChannelUserList(channel: string, maxCount: number, notifyMemChange: boolean): YouMeRtcErrorCode;|

设置是否通知别人自己麦克风和扬声器的开关状态 

/** * 设置是否通知别人自己麦克风和扬声器的开关状态,打开设置后在同一个频道的其他用户可以获取该用户的麦克风和扬声器的开关状态 * 回调对应事件: 

- 设置是否通知别人自己麦克风和扬声器的开关状态,打开设置后在同一个频道的其他用户可以获取该用户的麦克风和扬声器的开关状态 

- YOUME_EVENT_OTHERS_MIC_ON 

- YOUME_EVENT_OTHERS_MIC_OFF * YOUME_EVENT_OTHERS_SPEAKER_ON * YOUME_EVENT_OTHERS_SPEAKER_OFF * * @param autoSend 设置true表示通知别人自己麦克风和扬声器的开关状态,设置false表示不通知 */ SetAutoSendStatus(autoSend: boolean): void; 

### 把人踢出频道 

- /** * 把人踢出频道 * 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调: * YOUME_EVENT_KICK_RESULT,发送踢人消息的结果回调,param为被踢者ID。被踢的人会自动退出所在频道,并收到YOUME_EVENT_KICK_NOTIFY事件通知 * * @param user 被踢的用户ID * @param channel 从哪个频道踢出(自己需要在频道内) * @param lastTime 踢出后,多长时间内不允许再次进入(单位:秒) * @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ KickOtherFromChannel(user: string, channel: string, lastTime: number): YouMeRtcErrorCode; 

### 设置声音输出到扬声器 / 听筒 

- /** * 设置声音输出到扬声器/听筒,在加入房间成功后设置 * 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调: * YOUME_EVENT_SWITCH_OUTPUT,音频输出切换结果回调 * * @param outputToSpeaker true-输出到扬声器,false-输出到听筒 * @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ SetOutputToSpeaker(outputToSpeaker: boolean): YouMeRtcErrorCode; 

### 打开 / 关闭麦克风 

- /** 

### * 打开/关闭麦克风,该状态值在加入房间成功后设置才有效 

- 这是一个异步调用接口,收到以下事件回调表示执行成功: 

- YOUME_EVENT_LOCAL_MIC_OFF 

- YOUME_EVENT_LOCAL_MIC_ON 

- 

* @param mute true-关闭麦克风,false-开启麦克风 */ SetMicMute(mute: boolean): void; 

### 获取当前麦克风状态 

/** 

- 获取当前麦克风状态。(尽量避免逻辑上设置了麦克风状态后立刻调用该接口) 

- @returns true-麦克风关闭,false-麦克风开启 

*/ 

GetMicMute(): boolean; 

### 打开 / 关闭扬声器 

/** 

### * 打开/关闭扬声器,该状态值在加入房间成功后设置才有效 

- 这是一个异步调用接口,收到以下事件回调表示执行成功: 

- YOUME_EVENT_LOCAL_SPEAKER_OFF 

- YOUME_EVENT_LOCAL_SPEAKER_ON 

- 

- @param mute true-关闭扬声器,false-开启扬声器 

*/ 

SetSpeakerMute(mute: boolean): void; 

获取当前扬声器状态 

/** 

* 获取当前扬声器状态。(尽量避免逻辑上设置了扬声器状态后立刻调用该接口) 

* @returns true-扬声器关闭,false-扬声器开启 

*/ 

GetSpeakerMute(): boolean; 

### 设置当前程序输出音量大小 

/** 

### * 设置当前程序输出音量大小,建议该状态值在加入房间成功后按需设置 

* @param volume 音量大小,范围[0-100] 

*/ 

SetVolume(volume: number): void; 

### 获取当前程序输出音量大小 

/** 

### * 获取当前程序输出音量大小 

- @returns 当前输出音量大小,范围[0-100] 

*/ 

GetVolume(): number; 

### 设置远端单个用户音量增益 

/** 

- 设置远端单个用户音量增益(0-300),100为正常值,0为无声, 150以内相对安全,超过150可能有明显的破音。 

- 注:仅在本端设备生效,自己退出频道时设置失效,被调节的用户进出频道可以保持有效。 

- @param user 被调节的用户id 

- @param volume 音量大小,范围[0-300] 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 

*/ 

SetUserVolume(user: string, volume: number): YouMeRtcErrorCode; 

### 释放麦克风 

/** 

### * 调用后完成麦克风释放,只是为了方便使用IM的录音接口时切换麦克风使用权 

- @returns 返回true,表示释放成功,可以认为只要在占用麦克风的状态肯定能释放成功 

*/ 

ReleaseMicSync(): boolean; 

### 恢复麦克风 

/** 

* 调用后恢复麦克风到释放前的状态,只是为了方便使用IM的录音接口时切换麦克风使用权 

* @returns 返回true,表示恢复成功,可以认为只要在释放的状态,肯定可以恢复成功 

*/ 

ResumeMicSync(): boolean; 

### 设置当麦克风静音时,是否释放麦克风设备 

/** 

### * 设置当麦克风静音时,是否释放麦克风设备 

* @param enabled true-当麦克风静音时,释放麦克风设备,此时允许第三方模块使用麦克风设备录音;false-不管麦克风是否静音,麦克风设备都会被占 * @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetReleaseMicWhenMute(enabled: boolean): YouMeRtcErrorCode; 

设置当前用户的语音消息接收白名单 

|/**|
|---|
|*设置当前用户的语音消息接收白名单,其语音消息只会转发到白名单的用户,不设置该接口则默认转发至频道内所有人 *这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调才表示设置完成:|
|* YOUME_EVENT_SET_WHITE_USER_LIST_OK,成功在指定语音频道设置白名单,有异常用户会返回错误码YOUME_ERROR_WHITE_SOMEUSER_ABNORMAL|
|* YOUME_EVENT_SET_WHITE_USER_LIST_FAILED,在指定语音频道设置白名单失败,可能原因是网络或服务器有问题 *|

- @param channel 要设置的频道(兼容多频道模式) * @param whiteUserList 白名单用户列表, 以|分隔,如:User1|User2;表示语音消息只发送到User1,User2. "all"表示转发至频道内所有人;设置为 * @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetWhiteUserList(channel: string, whiteUserList: string): YouMeRtcErrorCode; 

### 控制他人的麦克风状态 

/** * 控制他人的麦克风状态(也就是关闭或者开启他人的麦克风) * @param user 要控制的用户ID * @param status true-静音别人的麦克风,false-开启别人的麦克风 * @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetOtherMicMute(user: string, status: boolean): YouMeRtcErrorCode; 

### 控制他人的扬声器状态 

/** * 控制他人的扬声器状态(也就是关闭或者开启他人的扬声器) * @param user 要控制的用户ID * @param status true-静音别人的扬声器,false-开启别人的扬声器 * @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetOtherSpeakerMute(user: string, status: boolean): YouMeRtcErrorCode; 

### 设置是否听某人的语音 

/** * 设置是否听某人的语音 * @param user 要控制的用户ID * @param on true-开启接收指定用户的语音,false-屏蔽指定用户的语音 * @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetListenOtherVoice(user: string, on: boolean): YouMeRtcErrorCode; 

### 设置是否开启语音检测回调 

/** 

### * 设置是否开启语音检测回调,开启后频道内有人正在讲话与结束讲话都会发起相应回调通知 

- (需要游密后台配置开启,该状态值在加入房间成功后设置才有效,并且需要频道内所有用户都设置才生效) 

- 开启成功后用户收到的回调事件有: 

- YOUME_EVENT_OTHERS_VOICE_ON,用户进入讲话状态 

- YOUME_EVENT_OTHERS_VOICE_OFF,用户进入静默状态 * 

- @param enabled true-打开,false-关闭 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetVadCallbackEnabled(enabled: boolean): YouMeRtcErrorCode; 

### 设置是否开启监听自己讲话音量回调 

/** 

### * 设置是否开启监听自己讲话音量回调, 并设置相应的参数 

### * 开启成功后用户收到的回调事件有: 

- YOUME_EVENT_MY_MIC_LEVEL * 

- @param maxLevel 音量最大时对应的级别,需大于1,最大可设100。比如你只在UI上呈现10级的音量变化,那就设10就可以了。设0表示关闭回调。 * @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetMicLevelCallback(maxLevel: number): YouMeRtcErrorCode; 

### 设置是否开启远端讲话音量级别回调 

/** 

### * 设置是否开启远端讲话音量级别回调, 并设置相应的参数 

### * 开启成功后用户收到的回调事件有: 

- YOUME_EVENT_FAREND_VOICE_LEVEL 

* 

- @param maxLevel 单个用户音量对应的最大级别,需大于1,最大可设100。比如你只在UI上呈现10级的音量变化,那就设10就可以了。设0表示关闭回调 

- @param maxMixedLevel 有远端用户音量混音后对应的最大级别,需大于1,最大可设100。比如你只在UI上呈现10级的音量变化,那就设10就可以了。设 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 

*/ 

SetFarendVoiceLevelCallback(maxLevel: number, maxMixedLevel: number): YouMeRtcErrorCode; 

### 在语音频道内广播文本消息 

- /** 

- 在语音频道内,广播一个文本消息。 

- 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调: 

- YOUME_EVENT_SEND_MESSAGE_RESULT,其中param为requestID的字符串。 

* 

- 广播成功后,频道内其他人收到文本消息通知的回调如下: 

- YOUME_EVENT_MESSAGE_NOTIFY,其中param为文本内容。 

* 

- @param channel 频道ID(自己需要进入这个频道) 

- @param content 要广播的文本内容。 

- @returns 返回包含错误码和广播请求ID的数组,错误码为YOUME_SUCCESS才会有异步回调通知,错误码为其它值表示发生了错误,错误码参考YouMeRtc */ 

SendMessage(channel: string, content: string): [YouMeRtcErrorCode, number]; 

### 设置当前录音的时间戳 

/** 

- 设置当前录音的时间戳。当通过录游戏脚本进行直播时,要保证观众端音画同步,在主播端需要进行时间对齐。 

- 这个接口设置的就是当前游戏画面录制已经进行到哪个时间点了。 

- @param timeMs 当前游戏画面对应的时间点,单位为毫秒。 

*/ 

SetRecordingTimeMs(timeMs: number); 

### 设置当前声音播放的时间戳 

/** 

- 设置当前声音播放的时间戳。当通过录游戏脚本进行直播时,要保证观众端音画同步,游戏画面的播放需要和声音播放进行时间对齐。 

- 这个接口设置的就是当前游戏画面播放已经进行到哪个时间点了。 

- @param timeMs 当前游戏画面播放对应的时间点,单位为毫秒。 

*/ 

SetPlayingTimeMs(timeMs: number); 

### 设置是否开启混响音效 

/** 

- 设置是否开启混响音效,这个对主播/指挥有用 

- @param enabled true-打开,false-关闭 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 

*/ 

SetReverbEnabled(enabled: boolean): YouMeRtcErrorCode; 

### 设置是否用耳机监听自己的声音或战歌,这个接口仅对主播 / 指挥有用 

/** 

- 设置是否用耳机监听自己的声音或战歌,这是一个同步调用接口。这个功能必须进入频道传入身份为主播/指挥才能使用。 

- @param micEnabled 是否监听麦克风 true-监听,false-不监听。 

- @param bgmEnabled 是否监听战歌 true-监听,false-不监听。 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetHeadsetMonitorOn(micEnabled: boolean, bgmEnabled: boolean): YouMeRtcErrorCode; 

设置监听时 mic 的音量 

/** 

### * 设置监听时mic的音量 

- @param volume 监听时mic的音量,范围 0-100 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 

*/ 

SetMicBypassVolume(volume: number): YouMeRtcErrorCode; 

### 获取监听时 mic 的音量 

/** 

### * 获取监听时mic的音量 

- @returns 监听时mic的音量,范围 0-100 

*/ GetMicBypassVolume(): number; 

### 设置频道内的广播消息回调 

### /** 

### * 设置频道内的广播消息回调(抢麦、连麦等) 

### * @param cb 频道内的广播消息回调 

*/ 

SetChannelBroadcastCallback(cb: (broadcast: YouMeRtcBroadcast, channel: string, param1: string, param2: string, content: strin 

### 抢麦相关设置 

### /** 

### * 抢麦相关设置(抢麦活动发起前调用此接口进行设置) 

- @param channel 抢麦活动的频道id 

- @param mode 抢麦模式(1:先到先得模式;2:按权重分配模式)。先到先得模式中,抢麦活动会持续,用户可以继续抢其他用户释放的麦 

- @param maxAllowCount 允许能抢到麦的最大人数(要大于0) 

- @param maxTalkTime 允许抢到麦后使用麦的最大时间(单位:秒,要大于0) 

- @param voteTime 抢麦仲裁时间(单位:秒,要大于0),过了指定时间后服务器将进行仲裁谁最终获得麦(仅在按权重分配模式下有效) 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 

*/ 

SetGrabMicOption(channel: string, mode: number, maxAllowCount: number, maxTalkTime: number, voteTime: number): YouMeRtcErrorCo 

### 发起抢麦活动 

/** 

### * 发起抢麦活动。接口需要加入房间后再调用 

- @param channel 抢麦活动的频道id 

- @param content 游戏传入的上下文内容,通知回调会传回此内容(目前只支持纯文本格式) 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

StartGrabMicAction(channel: string, content: string): YouMeRtcErrorCode; 

### 停止抢麦活动 

### /** 

### * 停止抢麦活动 

- @param channel 抢麦活动的频道id 

- @param content 游戏传入的上下文内容,通知回调会传回此内容(目前只支持纯文本格式) 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 

*/ 

StopGrabMicAction(channel: string, content: string): YouMeRtcErrorCode; 

### 发起抢麦请求 

### /** 

### * 发起抢麦请求 

- @param channel 抢麦的频道id 

- @param score 积分(权重分配模式下有效,游戏根据自己实际情况设置) 

- @param isAutoOpenMic 抢麦成功后是否自动开启麦克风权限 

- @param content 游戏传入的上下文内容,通知回调会传回此内容(目前只支持纯文本格式) 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

RequestGrabMic(channel: string, score: number, isAutoOpenMic: boolean, content: string): YouMeRtcErrorCode; 

释放抢到的麦 

/** * 释放抢到的麦 * @param channel 抢麦的频道id * @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

ReleaseGrabMic(channel: string): YouMeRtcErrorCode; 

### 连麦相关设置 

- /** 

- 连麦相关设置(角色是频道的管理者或者主播时调用此接口进行频道内的连麦设置) 

- @param channel 连麦的频道id 

- @param waitTimeout 等待对方响应超时时间(秒) 

- @param maxTalkTime 最大通话时间(秒) 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetInviteMicOption(channel: string, waitTimeout: number, maxTalkTime: number): YouMeRtcErrorCode; 

### 发起与某人的连麦请求 

/** 

- 发起与某人的连麦请求(主动呼叫)。支持跨频道发起连麦 

- @param channel 连麦的频道id 

- @param user 被叫方的用户id 

- @param content 游戏传入的上下文内容,通知回调会传回此内容(目前只支持纯文本格式) 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

RequestInviteMic(channel: string, user: string, content: string): YouMeRtcErrorCode; 

### 对连麦请求做出回应 

- /** 

- 对连麦请求做出回应(被动应答) 

- @param user 主叫方的用户id 

- @param isAccept 是否同意连麦 

- @param content 游戏传入的上下文内容,通知回调会传回此内容(目前只支持纯文本格式) 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

ResponseInviteMic(user: string, isAccept: boolean, content: string): YouMeRtcErrorCode; 

### 停止连麦 

- /** * 停止连麦 * @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

StopInviteMic(): YouMeRtcErrorCode; 

### 设置变声是否可用 

- /** 

- 设置变声是否可用(增值服务),需要配合游密变声管理模块文档使用。 

- @param enabled 设置变声是否可用,开启后会略微增大声音延迟。 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetMagicVoiceEnable(enabled: boolean): YouMeRtcErrorCode; 

### 设置变声功能参数 

- /** * 设置变声功能参数 * @param effectInfo 由变声管理模块获取到的变声音效信息中的参数,设置时将变声器置为可用 * @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetMagicVoiceInfo(effectInfo: string): YouMeRtcErrorCode; 

### 清除变声功能参数 

/** 

### * 清除变声功能参数 

* @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

ClearMagicVoiceInfo(): YouMeRtcErrorCode; 

### 变声参数微调 

/** 

### * 设置变声参数微调接口 

* @param fs 音色的微调值,范围-1.0f~1.0f,在后台下发的基准值的基础上按百分比调节,值减小音色会变厚重,值增大音色会变尖锐 

* @param semitones 音调的微调值,范围-1.0f~1.0f,在后台下发的基准值的基础上按百分比调节,值减小音调会低,值增大音调会变高 

* @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetMagicVoiceAdjust(fs: number, semitones: number): YouMeRtcErrorCode; 

### 获取变声器效果是否可用 

/** 

### * 获取变声器效果是否可用 

* @returns 变声器是否可用,为false时表示当前没有变声效果生效,可以不创建变声器 

*/ 

GetMagicVoiceEffectEnabled(): boolean; 

### 获取变声音调 

/** 

- 获取变声音调(增值服务,需要后台配置开启) 

- @returns 当前变声音调的值,范围[-12 ~ +12] 

*/ 

GetSoundtouchPitchSemiTones(): number; 

### 设置变声音调 

/** 

- 设置变声音调(增值服务,需要后台配置开启),需在进入房间成功后调用,仅对当前房间有效,退出房间时重置为0。 

- @param floatPitchSemiTones 变声音调的值,范围[-12 ~ +12] 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetSoundtouchPitchSemiTones(floatPitchSemiTones: number): YouMeRtcErrorCode; 

### 设置音频 pcm 数据监听回调 

/** 

- 设置是否开启音频pcm回调,以及开启哪种类型的pcm回调。 本接口可以在加入房间前,或者加入房间后调用。 

* 

- @param callbacks 音频pcm回调数组,需按顺序设置远端音频回调,录音音频回调,以及远端和录音数据的混合音频回调 

- @param flag 说明需要哪些类型的音频回调,取值参考YouMeRtcPcmCallBackFlag定义,比如PCMCALLBACK_FLAG_REMOTE|PCMCALLBACK_FLAG_RECOR * @param outputToSpeaker 是否扬声器静音:true-不静音,false-静音 

- @param outputSampleRate 音频回调数据的采样率: 8000/16000/32000/44100/48000/64000 

- @param outputChannel 音频回调数据的通道数:1-单通道,2-立体声 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetPcmCallbackEnable(callbacks: ((channelNum: number, samplingRateHz: number, bytesPerSample: number, data: ArrayBuffer) => vo flag: number, outputToSpeaker: boolean, outputSampleRate: number, outputChannel: number): YouMeRtcErrorCode; 

### 设置网络质量检测结果回调 

/** 

### * 设置网络质量检测结果回调 

### * @param cb 网络质量检测结果回调。 

- isNetworkOK - 检测网络是否可用,目前如果lossPer<=0.2并且avgRtt<400,就认为网络是可用的,并且这两个阈值将支持服务器动态下发控制。 *    result - 检测的结果值,json格式,包含avgRtt(平均往返延迟,整型,单位毫秒)和lossPer(丢包率,浮点型,范围0.0~1.0),示例:{"avg * 

*/ 

SetDetectNetworkCallback(cb: (isNetworkOK: boolean, result: string) => void): void; 

开始网络质量检测 

/** 

- 开始网络质量检测,检测结束后会收到DetectNetworkCallback回调返回结果(此功能需要联系游密后台开通) 

- @param detectTime 发包检测时长,单位为秒,建议3秒,范围(0,100] 

- @param overTime 检测终止时长,单位为秒,建议4秒,范围(0,110] 

- @param intervalMs 发包间隔,单位毫秒,建议20毫秒,范围[20,30000],发包间隔不能超过检测时长或终止时长 

- @param packSize 发包大小,单位字节,建议300字节,范围[64,1400] 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义。如之前的检测还在进行中,再次调用该接 */ 

DetectNetworkQuality(detectTime: number, overTime: number, intervalMs: number, packSize: number): YouMeRtcErrorCode; 

### 终止检测网络质量 

/** * 终止检测网络质量,终止后将不会收到DetectNetworkCallback回调。 * @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义。如未在进行网络质量检测就调用该接口将返 */ 

StopDetectNetworkQuality(): YouMeRtcErrorCode; 

### 注册 RestAPI 请求响应监听回调 

- /** * 注册RestAPI请求响应监听回调 * @param callback RestAPI请求响应回调 */ 

SetRestApiCallback(callback: (requestID: number, errCode: YouMeRtcErrorCode, query: string, result: string) => void): void; 

### 通过 RestAPI 向服务器请求额外数据 

/** 

- 通过RestAPI, 向服务器请求额外数据 

- @param command 请求的命令字符串 

- @param query 请求需要的数据, json格式 

- @returns 返回包含错误码和请求ID的数组,错误码为YOUME_SUCCESS才会有异步RestApiCallback回调通知,错误码为其它值表示发生了错误,错误码参 */ 

RequestRestApi(command: string, query: string): [YouMeRtcErrorCode, number]; 

### 设置 Audio 统计数据监听回调 

/** 

### * 设置Audio统计数据监听回调 

- @param callback Audio统计数据监听回调 

*/ 

SetAVStatisticCallback(callback: (statType: YouMeRtcAVStatisticType, user: string, value: number, param: string) => void): voi 

### 设置缓存自己最近的一段语音时长 

/** 

### * 设置缓存自己最近的一段语音的时长 

- @param timeInSec 保存语音的时长,秒单位 

- @returns 返回YOUME_SUCCESS表示成功,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

SetReportBufferTime(timeInSec: number): YouMeRtcErrorCode; 

### 把缓存语音保存为文件 

/** 

- 把缓存自己的最近的一段语音保存为文件 

- 这是一个异步调用接口,如果函数返回YOUME_SUCCESS,则需要等待以下事件回调: 

- YOUME_EVENT_REPORT_AUDIO,其中param为保存的文件路径 

* 

- @returns 返回YOUME_SUCCESS才会有异步回调通知,返回其它值表示发生了错误,错误码参考YouMeRtcErrorCode定义 */ 

ReportAudio(): YouMeRtcErrorCode; 

设置服务器模式 

/** * 设置后台服务器模式,需结合SetServerAddress使用才能生效 

* @param mode SDK服务器模式 */ SetServerMode(mode: YouMeRtcServerMode): void; 

设置服务器地址 

/** 

- 设置SetServerMode设置的服务器类型对应的后台服务器地址 

- @param ip 指定的服务器ip地址 * @param port 指定的服务器端口号 */ 

SetServerAddress(ip: string, port: number): void; 

设置服务器区域 

/** 

- 设置服务器区域,如果在初始化时不能确定区域,可以填RTC_DEFAULT_SERVER,后面确定时通过SetServerRegion设置 

* @param region 服务器区域 

- @param extName 设置一个自定的区域值(如中国用"cn"或者"ch"表示),然后把这个自定义的区域值同步给游密,游密在后台配置映射到最佳区域的服 * @param append 是否追加 

*/ 

SetServerRegion(region: YouMeRtcServerRegion, extName: string, append: boolean): void; 

## **SDK 接入说明** 

### 添加 har 依赖 

首选把 har 文件放在 entry 模块的 libs 目录下,并在 entry 模块 oh-package.json5 中添加对 har 静态库的依赖,示例如下: 

{ 

"license": "", "devDependencies": { }, "author": "游密科技(youme.im)", "name": "entry", "description": "游密实时语音SDK Demo", "main": "", "version": "1.0.0", "dependencies": { "@youme/voice_engine": "file:./libs/youme_voice_engine.har" } } 

- 添加依赖后,在 DevEco Studio 中完成工程同步,并在工程目录下执行 “ohpm install” 安装依赖模块。 

应用中使用 ArkTs 代码调用 SDK ArkTs API 

1. SDK 调用示例 - 设置 SDK 事件回调和成员列表变更回调: 

import { YouMeRtcAPI } from '@youme/voice_engine'; 

```arkts
let curDate = new Date(); YouMeRtcAPI.Instance().SetEventCallback( (event, errCode, channel, param) => { const ctx = getContext(this) ctx.eventHub.emit("youme_event", event, errCode, channel, param) } ); this.sdkEventInfo += `${curDate.toLocaleTimeString()} 【api】设置事件回调\n` YouMeRtcAPI.Instance().SetMemberChangeCallback( (channel, members, isUpdate) => { const ctx = getContext(this) ctx.eventHub.emit("youme_members", channel, members, isUpdate) } ); this.sdkEventInfo += `${curDate.toLocaleTimeString()} 【api】设置成员列表回调\n` 
```

2. SDK 调用示例 - 初始化 SDK : 

import { YouMeRtcAPI } from '@youme/voice_engine'; 

```arkts
const promise = new Promise<number>((resolve, reject) => { let error = YouMeVoiceAPI.Instance().Init(this.appCustom.appKey, this.appCustom.appSecret, this.selectedRegion, ""); if (error == 0) { resolve(error); } else { reject(new Error("error call failed")); } }); promise .then(result => { hilog.info(logFlag, logTag, `call init sdk succ:${result} region:${this.selectedRegion}`); }) .catch((e: Error) => { hilog.error(logFlag, logTag, `call init sdk err:${e.message} zone:${this.selectedRegion}`); }); 
```

3. SDK 调用示例 - 监听 SDK 事件: 

|import { YouMeRtcErrorCode, YouMeRtcEvent } from '@youme/voice_engine'; eventLister: Function = (event:YouMeRtcEvent, err:YouMeRtcErrorCode, channel:string, param:string) => {|
|---|
|let curDate = new Date(); |
|switch (event){ |
|case YouMeRtcEvent.YOUME_EVENT_LOCAL_MIC_ON:|
|case YouMeRtcEvent.YOUME_EVENT_LOCAL_MIC_OFF: |
|case YouMeRtcEvent.YOUME_EVENT_LOCAL_SPEAKER_ON:|
|case YouMeRtcEvent.YOUME_EVENT_LOCAL_SPEAKER_OFF:|
|case YouMeRtcEvent.YOUME_EVENT_SWITCH_OUTPUT:{|
|this.sdkEventInfo += `${curDate.toLocaleTimeString()}【event】${eventStrings[event]}错误码:${err}频道:${channel}参数:$ break; |
|} case YouMeRtcEvent.YOUME_EVENT_MY_MIC_LEVEL:{|
|this.selfVolumeLevel = err |
|break;|
|}|
|case YouMeRtcEvent.YOUME_EVENT_FAREND_VOICE_LEVEL:{ |
|this.farendVolumeLevel = err|
|this.farendUser = param |
|break; |
|} case YouMeRtcEvent.YOUMEEVENTOTHERSVOICEON:{|
|____ this.sdkEventInfo += `${curDate.toLocaleTimeString()}【vad】${eventStrings[event]}用户${param}开始说话\n` bk|
|rea;|
|} |
|case YouMeRtcEvent.YOUME_EVENT_OTHERS_VOICE_OFF:{|
|this.sdkEventInfo += `${curDate.toLocaleTimeString()}【vad】${eventStrings[event]}用户${param}停止说话\n`|
|break; |
|} case YouMeRtcEvent.YOUMEEVENTPAUSED: {|
|__ this.sdkEventInfo += `${curDate.toLocaleTimeString()}【vad】${eventStrings[event]}通话暂停${err}\n` bk|
|rea;|
|} |
|case YouMeRtcEvent.YOUME_EVENT_RESUMED: {|
|this.sdkEventInfo += `${curDate.toLocaleTimeString()}【vad】${eventStrings[event]}通话恢复${err}\n`|
|break; |
|} case YouMeRtcEvent.YOUME_EVENT_OTHERS_MIC_ON: { |
|this.sdkEventInfo += `${curDate.toLocaleTimeString()}【event】${eventStrings[event]}用户${param}麦克风开启\n` |
|break; }|
|
case YouMeRtcEvent.YOUME_EVENT_OTHERS_MIC_OFF: {|
|this.sdkEventInfo += `${curDate.toLocaleTimeString()}【event】${eventStrings[event]}用户${param}麦克风关闭\n` break;|
|
}|
|case YouMeRtcEvent.YOUME_EVENT_OTHERS_SPEAKER_ON: {|
|this.sdkEventInfo += `${curDate.toLocaleTimeString()}【event】${eventStrings[event]}用户${param}扬声器开启\n` |
|break; }|
|
case YouMeRtcEvent.YOUME_EVENT_OTHERS_SPEAKER_OFF: {|
|this.sdkEventInfo += `${curDate.toLocaleTimeString()}【event】${eventStrings[event]}用户${param}扬声器关闭\n`|
|break; |
|}|
|default:{|
|
break;|
|
}|
|} |
|}|

应用中使用 C++ 代码调用 SDK C++ API 

1. 调用 SDK C++ API ,需要先在 Native C++ 代码的 CMakeList.txt 中配置依赖的 SDK 头文件和库文件路径,示例如下: 

# the minimum version of CMake. cmake_minimum_required(VERSION 3.5.0) project(entry) 

set(NATIVERENDER_ROOT_PATH ${CMAKE_CURRENT_SOURCE_DIR}) 

if(DEFINED PACKAGE_FIND_FILE) include(${PACKAGE_FIND_FILE}) endif() 

include_directories(${NATIVERENDER_ROOT_PATH} ${NATIVERENDER_ROOT_PATH}/include ${CMAKE_CURRENT_SOURCE_DIR}/../../../oh_modules/@youme/voice_engine/include) set(YOUME_LIB_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../../../oh_modules/@youme/voice_engine/libs) 

link_directories(${YOUME_LIB_PATH}/${CMAKE_OHOS_ARCH_ABI}) add_library(entry SHARED napi_init.cpp youme_native.cpp) 

target_link_libraries(entry PUBLIC libyoume_voice_engine.so libace_napi.z.so libhilog_ndk.z.so) 

### 2. 应用 C++ 代码引入 SDK 头文件即可调用 C++ API 。 

#include "IYouMeVoiceEngine.h" #include "IYouMeEventCallback.h" #include "YouMeConstDefine.h" 

### // 定义SDK回调监听类 

class YouMeCallback: public IYouMeEventCallback, public IRestApiCallback, public IYouMeMemberChangeCallback, public IYouMeAVStatisticNewCallback, public IYouMeChannelMsgCallback, public IYouMePcmCallback, public IYouMeDetectNetworkCallback { public: 

void onEvent(const YouMeEvent event, const YouMeErrorCode error, const char * channel, const char * param); void onRequestRestAPI(int requestID, const YouMeErrorCode &iErrorCode, const char* strQuery, const char* strResult); void onDetectNetWorkCompleteCb(bool bNetworkOK, const char*  strResult); 

void onAVStatisticNew(YouMeAVStatisticType type, const char* userID, int value, const char* param); void onMemberChange(const char*  channel, const char* listMemberChange, bool bUpdate); 

void onBroadcast(const YouMeBroadcast bc, const char*  channel, const char*  param1, const char*  param2, const char*  str void onPcmDataRemote(int channelNum, int samplingRateHz, int bytesPerSample, void* data, int dataSizeInByte); void onPcmDataRecord(int channelNum, int samplingRateHz, int bytesPerSample, void* data, int dataSizeInByte); void onPcmDataMix(int channelNum, int samplingRateHz, int bytesPerSample, void* data, int dataSizeInByte); } 

### // 设置回调 

YouMeCallback* inst = new YouMeCallback(); IYouMeVoiceEngine::getInstance()->setRestApiCallback(inst); IYouMeVoiceEngine::getInstance()->setMemberChangeCallback(inst); IYouMeVoiceEngine::getInstance()->setNotifyCallback(inst); IYouMeVoiceEngine::getInstance()->setDetectNetworkCallback(inst); IYouMeVoiceEngine::getInstance()->setAVStatisticNewCallback(inst); 

### // 初始化SDK 

YouMeErrorCode ec = IYouMeVoiceEngine::getInstance()->init(inst, appKey, appSecret, (YOUME_RTC_SERVER_REGION)serverRegion, ext
