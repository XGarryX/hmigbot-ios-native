# **S eechEn ine** **p g** 

## 一句话识别入口,用于设置识别相关参数、发起识别、结束识别等。 

setEngineParam(engineParam: EngineParam) 

|**-**|**-**|
|---|---|
|说明|设置识别相关配置|
|版本支持|最低1.0.0|
|engineParam|识别相关参数|

setCallBack(callBack: OnSpeechEngineCallBack) 

|**-**|**-**|
|---|---|
|说明|设置识别的回调|
|版本支持|最低1.0.0|
|参数OnSpeechEngineCallBack|识别回调|

## EngineParam类说明 

|**-** 说明|**-** 识别参数|
|---|---|
|版本支持|最低1.0.0|
|appkey|(必填)通过官方申请|
|secret|(必填)通过官方申请|
|host|(必填)中文普通话:ws[s]: //ws-osasr.hivoice.cn/v1/asr ;方言、英语: ws[s]: //ws-osasr-dialect.hivoice.cn/v1/asr|
|isSpeech|(可选值) true:本次请求使用录音方式,需要先申请录音权限;false:本次请求 使用调用通过sendMessage(ArrayBuffer)设置音频数据,默认值为true。|
|userId|(可选值)默认值为UUID,该次请求session id|
|domain|(可选值)领域,可设置多个,最多4个,general(通用);movietv(影视); song(音乐);poi(地图);medical(医疗);eshopping(电商);home(家居); law(法律);childEdu(儿童教育);finance(金融),默认值为general, @EngineParamDomain|
|acousticSetting|(可选值)声学模型,near近讲,far远讲,默认值为near, @EngineParamAcousticSetting|

|**-**|**-**|
|---|---|
|format|(可选值)语音编码格式:opus,adpcm,speex,pcm,amr,默认值为pcm, @EngineParamFormat|
|sample|(可选值)采样率: 16k,8k,默认值为16k,@EngineParamSample|
|lang|(可选值)语言: cn(中文);en(英文);cantonese(粤语);sichuanese(四川 话),默认值为cn,@EngineParamLang|
|variable|(可选值)是否返回可变结果: true,false,),默认值为true|
|punctuation|(可选值)是否开启标点符号添加: true,false,默认值为true|
|postProc|(可选值)是否开启数字格式转为阿拉伯数字格式: true,false,默认值为true|
|serverVad|(可选值)是否开启智能断句: true,false,默认值为false|
|maxStartSilence|(可选值)允许的最大开始静音时长,单位是毫秒,超出后服务端将会发送结 束事件,结束本次识别,需要先设置server_vad为true,默认值为2000。|
|maxEndSilence|(可选值)允许的最大结束静音时长,单位是毫秒,有效范围200~2000ms, 超出时长服务端会发送结束事件,结束本次识别(需要注意的是后续的语音不 会继续进行识别),需要先设置server_vad为true,默认值为500。|

## OnSpeechEngineCallBack类说明 

|**-**||**-**|
|---|---|---|
|说明||事件和结果回调|
|版本支持||最低1.0.0|
|onSpeechOpen: () => void||调用start()后,连接服务器成功,会回调 onSpeechOpen()|
|onSpeechClose: () => void||主动调用stop(),或服务器主动断开连接,会回调 onSpeechClose()|
|onSpeechError: (error: stri|ng) => void|服务器返回的错误信息,@SpeechResponseCode 的返回信息|
|onSpeechResult: (data: SpeechResponse) => void||识别结果:SpeechResponse|
|**-** SpeechResponse类说明|**-**||
|说明|识别结果||
|版本支持|最低1.0.0||
|参数code|错误码,@Sp|eechResponseCode|
|参数msg|结果说明||

|**-**|**-**|
|---|---|
|参数sid|识别的唯一id|
|参数server_vad|是否服务端智能断句|
|参数end|请求是否结束|
|参数type|结果类型:"variable":可变结果,"fixed":固定结果|
|参数text|识别结果|

## SpeechResponseCode类说明 

|**-**|**-**|
|---|---|
|说明|错误码|
|版本支持|最低1.0.0|
|0|成功|
|20201|参数错误|
|20202|超过10s没有上传语音|
|20203|服务资源不足|
|20204|服务内部错误|
|20205|音频长度超过1分钟|
|20206|并发超过限制|
|20207|套餐次数使用完|
|20208|appkey不存在|
|20209|客户端ip不在白名单|

start(): void 

|**-**|**-**|
|---|---|
|说明|开启识别|
|版本支持|最低1.0.0|
|**-** stop(): void|**-**|
|说明|结束识别|
|版本支持|最低1.0.0|

sendMessage(data: ArrayBuffer): void 

|**-**|**-**|
|---|---|
|说明|发送识别的音频数据|
|版本支持|最低1.0.0|
|参数data|音频数据流|
|release(): void||
|**-**|**-**|
|说明|释放数据|
|版本支持|最低1.0.0|
