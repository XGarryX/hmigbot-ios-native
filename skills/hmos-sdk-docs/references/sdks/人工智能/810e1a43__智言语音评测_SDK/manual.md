# **Harmon** **SDK y** 

## **一** **、集成步骤** 

### **1. 集成方式** 

#### **1.1 添加har依赖(本地集成)** 

将 speech_eval_sdk.har 放入项目的 libs 目录内,进入该目录下 安装 

命令 :ohpm install speech_eval_sdk.har 

引入以下依赖 

ohpm install @ohos/crypto-js 

#### **1.2 ohpem仓集成(远程集成)** 

命令 :ohpm install speech_eval_sdk 

引入以下依赖 

ohpm install @ohos/crypto-js 

### **2. 添加应用相关权限** 

在该工程下的module.json5文件中添加 

"requestPermissions": [ { "name" : "ohos.permission.MICROPHONE", "reason": "$string:麦克风权限", "usedScene": { "abilities": [ "FormAbility" ], "when":"always" } }, { "name": "ohos.permission.INTERNET" }, { "name": "ohos.permission.READ_MEDIA", "reason": "$string:读取权限", "usedScene": { "when": "always" } } ] 

### **3. 调用步骤/示例代码** 

调用SDK录音 start(recorder) stop() onResult获取结果
创建评测类对象 设置公共参数 初始化引擎init() 设置题型相关参数 手动发音频包 start() feed(data) cancel() 取消评测 无结果 destroy()
传音频文件 start(wavPath) 发送完成后自动结束 onResult获取结果

#### **1 获取权限** 

async function requestPermissions() { const permissions: Array<Permissions> = [ 'ohos.permission.INTERNET',//允许使用Internet网络 

'ohos.permission.READ_MEDIA',//允许应用读取用户外部存储中的媒体文件信息 

'ohos.permission.WRITE_MEDIA',//允许应用读写用户外部存储中的媒体文件信息 

'ohos.permission.MICROPHONE',//允许应用使用麦克风 

]; let atManager = abilityAccessCtrl.createAtManager(); 

await atManager.requestPermissionsFromUser(context, permissions).then((data) => { console.log('TAG', `Request permissions succeed, data is: ${data}`); 

}).catch((error: Error) => { console.log('TAG', `Request permissions failed, error is: ${error}`); }); } 

#### **2 初始化引擎实例** 

```arkts
eval: SpeechEval = SpeechEval.getInstance(context) // 设置监听器 const listeners: Listener = { onWsStart: (taskId: string): void => { //在线评测ws建立成功时回调 }, onResult: (result: string, online: boolean): void => { //评测返回结果回调 }, onStartRecording: (): void => { //录音开始回调 }, onStopSending: (): void => { //录音停止时回调 }, onGetAudio: (data: ArrayBuffer | undefined): void => { //录音方式 返回实时录音的音频 }, onGetVolume: (volume: number): void => { //实时返回音量信息回调 }, onWarning: (taskId: string, code: string, msg: string): void => { //提醒、警告信息,根据自己业务端需求进行处理 }, onError: (taskId: string, code: string, msg: string): void => { //评测错误回调 }, onRealtimeResult: (msg: string): void => { //realtime设置为true时,中/英文 sentence、chapter、freedom 题型,以及中文 poem、recite 题型 , //会实时返回评测数据 }, onSaveAudioFile: (localPath: string): void => { // 设置 setSaveAudio(true) 时,此方法会回调 }, engineInitState: (code: string, msg: string): void => { if (code === "00000") { promptAction.showToast({ message: "初始化成功" }) } else { promptAction.showToast({ message: code + msg }) } } }; eval.setListener(listeners); //设置回调监听 //配置英文评测,如果有该语种,则配置 OralOnLine,没有可以不设置,或者设置为None eval.setInitLanguageEn(InitSettingOnline.OralOnLine); //配置中文评测,如果有该语种,则配置 OralOnLine,没有可以不设置,或者设置为None 
```

eval.setInitLanguageZn(InitSettingOnline.OralOnLine); //初始化的状态请查看回调方法 engineInitState // userId , 建议设置, 以方便区分不同的用户 eval.init(appId, appSecret, userId); 

##### 初始化状态回调方法 engineInitState 对应状态码: 

###### 在线 

"00000","success" "13010", "缺少网络权限" "13011", "无网络连接" "10002", "参数错误" "11011", "signature错误" "11012", "appid不可用" "11013", "appid不存在" "11014", "生成token错误" "11015", "非法的当前时间" 

#### **3 设置参数** 

##### **评测参数** 

请参考 公共参数:评测参数 文档。 

- 使用 eval.setKEY(VALUE); 的方法设置评测参数 

- 必填参数如缺失或赋值超出范围,将在 onError 中返回错误码、错误信息 

- 选填参数如缺失,将取默认值;如赋值超出范围,将取默认值,并在 onWarning 中返回错误码、错误信息 

##### **题型参数** 

##### 请参考对应题型的 接口参数 文档。 

##### **示例代码** 

/** * 在评测前设置或修改 ,有默认值的数据 ,可以不设置 * */ eval.setLangType(SpeechEval.LangType.enUS);  //设置要评测的语种,没有默认值(必填),必须在评测前 设置 eval.setSampleRate(16000);  //设置采样率,只支持16000,必填 eval.setAudioUrl(false);  //设置是否保存音频(服务端),默认为false(不保存) eval.setSaveAudio(true);  //设置是否保存音频(手机端),默认false,不做保存。也可以根据onGetVolume 返回的实时片段保存数据 eval.setAudioSavePath("/sdcard/xxx/abc.pcm");  //设置音频保存路径,setSaveAudio 为true时,才生 效 eval.setScale(100);     //评分分制,默认为100 eval.setRatio(1);   //设置拉升系数,取值范围为0.8-1.5,默认为1.0 eval.setLooseness(4);  //设置评分宽松度,聚会范围为0-9,默认为为4 

eval.setClientData("1111");  //设置自定义参数,客户可以传入自己需要的参数,会在响应结果中返回 clentData字段,其它类型建议转为字符串类型 

//构建题型相关参数JSON(以单词题型为例) 

```arkts
const paramsJson: ParamsJson = { mode: this.mode.toString(), refText: this.reTxet } eval.setParamsJson(paramsJson); 
```

#### **4开始/停止评测** 

##### **开始评测(录音方式)** 

eval.start(); //此时开始使用麦克风接收音频 // ... //接收完成后手动停止录音完成评测 eval.stop(); 

##### **开始评测(发送音频文件方式)** 

//开始 String Path = "/sdcard/xxx/abc.pcm" eval.startPath(Path);  //传入PCM格式音频数据,要求为16000Hz、16Bit、单声道音频文件 //自动读取音频文件并发送,完成后自动停止评测 

#### **5 处理评测结果** 

参考 2 创建评测类对象 在 listener 中处理评测结果 

#### **6释放评测资源** 

eval.destroy(); 

### **4.混淆机制** 

//如果要做混淆,排除SDK做混淆即可 

## **二、接口文档** 

### **SpeechEval 类** 

发音评测主类 

**createInstance** 

|**函数原型**|**public static getInstance(context: Context): SpeechEval**|
|---|---|
|功能描述|创建评测类对象|
|输入参数|context: Context对象|
|返回值|无|
|使用说明|创建评测类对象|

##### **setListener** 

|**函数原型**|**public setListener(listener: Listener): void**|
|---|---|
|功能描述|设置Listener|
|输入参数|listener: Listener对象|
|返回值|无|
|使用说明|设置Listener|

##### **setLangType** 

|**函数原型**|**setLangType(langType: LangType)**|
|---|---|
|功能描述|设置语种|
|输入参数|langType:语种代码|
|返回值|无|
|使用说明|设置语种|

##### **setScale** 

|**函数原型**|**setScale(scale: number)**|
|---|---|
|功能描述|设置评分分制|
|输入参数|scale:评分分制1-100|
|返回值|无|
|使用说明|设置评分分制|

##### **setSampleRate** 

|**函数原型**|**public void setSampleRate(int sampleRate)**|
|---|---|
|功能描述|设置采样率|
|输入参数|sampleRate:采样率16000|
|返回值|无|
|使用说明|设置采样率|

##### **setLooseness** 

|**函数原型**|**public void setLooseness(int looseness)**|
|---|---|
|功能描述|设置评分宽松度|
|输入参数|looseness:评分宽松度0-9|
|返回值|无|
|使用说明|设置评分宽松度|

##### **setConnectTimeout** 

|**函数原型**|**public void setConnectTimeout(int timeout)**|
|---|---|
|功能描述|设置连接超时时间|
|输入参数|timeout:超时时间1-60|
|返回值|无|
|使用说明|设置连接超时时间|

##### **setResponseTimeout** 

|**函数原型**|**public void setResponseTimeout(int timeout)**|
|---|---|
|功能描述|设置响应超时时间|
|输入参数|timeout:超时时间1-60|
|返回值|无|
|使用说明|设置响应超时时间|

##### **setRatio** 

|**函数原型**|**public void setRatio(float ratio)**|
|---|---|
|功能描述|设置评分调节系数|
|输入参数|ratio:评分调节系数0.8-1.5|
|返回值|无|
|使用说明|该系数的作用是对30~90之间的得分(百分制)进行上调或下调,其他范围内的得分不变 ratio>1.0时,对评分进行上调,越接近75分,调节程度越高 ratio<1.0时,对评分进行下调,越接近75分,调节程度越高 ratio=1.0时,不进行评分调节|

##### **setSaveAudio** 

|**函数原型**|**public void setSaveAudio(boolean saveAudio)**|
|---|---|
|功能描述|设置是否保存录音音频|
|输入参数|saveAudio: true为保存本地音频,false为不保存本地音频|
|返回值|无|
|使用说明|设置是否保存录音音频|

##### **setModelPath** 

|**函数原型**|**public void setSaveAudio(String modelPath)**|
|---|---|
|功能描述|设置离线模型加载路径|
|输入参数|modelPath传路径目录,不传为默认getExternalFilesDir(null).getPath()/model|
|返回值|无|
|使用说明|必须是可访问操作的路径。是模型的文件存放与解压下后的路径|

##### **setMaxPrefixSilence** 

|**函数原型**|**public void setMaxPrefixSilence(int maxPrefixSilence)**|
|---|---|
|功能描述|设置语音前置静音检测阈值(秒)|
|输入参数|maxPrefixSilence:范围1-30|
|返回值|无|
|使用说明|音开始后静音时长超过该阈值会返回一次Warning事件|

##### **setMaxSuffixSilence** 

|**函数原型**|**public void setMaxSuffixSilence(int maxSuffixSilence)**|
|---|---|
|功能描述|设置语音后置静音检测阈值(秒)|
|输入参数|maxSuffixSilence:范围1-30|
|返回值|无|
|使用说明|句尾静音时长超过该阈值会自动结束评测|

##### **setMaxPrefixSilenceMs** 

|**函数原型**|**public void setMaxPrefixSilence(int maxPrefixSilenceMs)**|
|---|---|
|功能描 述|设置语音前置静音检测阈值(毫秒)|
|输入参 数|maxPrefixSilenceMs:范围[0-30000]|
|返回值|无|
|使用说 明|音开始后静音时长超过该阈值会返回一次Warning事件,为0时代表不进行句首静音检测,为0时不 返回Warning事件|

##### **setMaxSuffixSilenceMs** 

|**函数原型**|**public void setMaxSuffixSilence(int maxSuffixSilenceMs)**|
|---|---|
|功能描述|设置语音后置静音检测阈值(毫秒)|
|输入参数|maxSuffixSilenceMs:范围[0-30000]|
|返回值|无|
|使用说明|句尾静音时长超过该阈值会自动结束评测,为0时代表不进行句尾静音检测|

##### **setPrecision** 

|**函数原型**|**public void setPrecision(String precision)**|
|---|---|
|功能描 述|设置打分精度|
|输入参 数|precision:默认为0,只支持0、0.1、0.25、0.5、1,如果设置的值不是这五个中的一个,则按0 处理|
|返回值|无|
|使用说 明|根据业务需要的打分精度进行设置|

##### **setConnti** 

|**函数原型**|**public void setConnti(int connti)**|
|---|---|
|功能描述|是否开启连读和失爆检测,默认为0,只针对英文|
|输入参数|connti为0时,不开启 connti为1时, 开启|
|返回值|无|
|使用说明|默认为0,无此功能可不设置,或者设置为0,设置为1时会开启连读和失去爆检测|

##### **setServerAPI** 

|**函数原型**|**public void setServerAPI(String serverAPI)**|
|---|---|
|功能描述|设置在线服务器地址,请求指定域名服务器|
|输入参数|serverAPI,提供的域名|
|返回值|无|
|使用说明|需要在初使化前设置,不设置使用通用域名|

##### **setTestServerAPI** 

|**函数原型**|**public void setTestServerAPI(String testServerAPI)**|
|---|---|
|功能描述|设置在线测试服务器地址,请求指定域名服务器|
|输入参数|testServerAPI,提供的域名|
|返回值|无|
|使用说明|需要在初使化前设置,不设置使用通用域名|

##### **setI18n** 

|**函数原型**|**public void setI18n(SpeechEval.I18n i18n)**|
|---|---|
|功能 描述|设置国际化返回语言类型,根据设置的语言类型返回对应的提示信息(warning和error)|
|输入 参数|i18n,语言类型参数 ,支持枚举EN、ZH、None , EN:英文 ,ZH:中文 ,None: sdk会取系统语言|
|返回 值|无|
|使用 说明|需要在初使化前设置,不设置此方法或者设置为None,则取系统语言,系统语言为中文返回中文提 示信息,其它语言类型返回英文提示信息|

##### **init** 

|**函数原型**|**public ErrorCodes.ErrorCode init(String appId, String appSecret, String userId)**|
|---|---|
|功能描述|初始化服务|
|输入参数|userId:用户身份标识,用于统计信息|
|返回值|错误码对象,包含错误码与错误信息|
|使用说明|初始化服务|

##### **setParamsJson** 

|**函数原型**|**public void setParamsJson(JSONObject json)**|
|---|---|
|功能描述|设置参数对象|
|输入参数|无|
|返回值|JSON对象|
|使用说明|用于设置JSON参数|

##### **setClientData** 

|**函数原型**|**public void setClientData(String clientData)**|
|---|---|
|功能描 述|设置自定义参数,客户可以传入自己需要的参数,会在响应结果中返回clentData字段|
|输入参 数|无|
|返回值|无|
|使用说|用于设置自定义请求参数,只支持字符串类型,如果想传入其它类型,建议转成字符串类型传|
|明|入。|

##### **createRecorder** 

|**函数原型**|**public Recorder createRecorder()**|
|---|---|
|功能描述|获取Recorder对象|
|输入参数|无|
|返回值|Recorder对象|
|使用说明|使用SDK录音时,获取Recorder对象,传入start()方法中|
|**函数原型start**|**public ErrorCodes.ErrorCode start(Recorder recorder)**|
|功能描述|开始评测(使用SDK录音)|
|输入参数|recorder:createRecorder()后获得的Recorder对象|
|返回值|错误码对象|
|使用说明|开始评测(使用SDK录音)|
|**函数原型**|**public ErrorCodes.ErrorCode start(String wavPath)**|
|功能描述|开始评测(传音频文件)|
|输入参数|wavPath:音频文件路径|
|返回值|错误码对象|
|使用说明|开始评测(传音频文件),开始后自动发送音频,发送完成后自动结束完成评测|

|**函数原型**|**public ErrorCodes.ErrorCode start()**|
|---|---|
|功能描述|开始评测(手动发音频包)|
|输入参数|无|
|返回值|错误码对象|
|使用说明|开始评测(手动发音频包),后续需要调用feed()方法来发送音频数据包|

##### **feed** 

|**函数原型**|**public void feed(byte[] data)**|
|---|---|
|功能描述|手动发音频数据包|
|输入参数|音频数据,建议每次发送的音频数据长度为1920 Byte|
|返回值|错误码对象|
|使用说明|调用start()后,**循环调用**feed()用于传入音频数据|

##### **stop** 

|**函数原型**|**public void stop()**|
|---|---|
|功能描述|停止评测|
|输入参数|无|
|返回值|无|
|使用说明|停止评测|

##### **cancel** 

|**函数原型**|**public void cancel()**|
|---|---|
|功能描述|开始评测后取消评测|
|输入参数|无|
|返回值|无|
|使用说明|开始评测后取消评测,不返回评测结果|

##### **destroy** 

|**函数原型**|**public void destroy()**|
|---|---|
|功能描述|释放评测资源|
|输入参数|无|
|返回值|无|
|使用说明|一般可以放在Activity.onDestroy中调用|

##### **update** 

|**函数原型**|**public void update(true, OnUpdateListener listener)**|
|---|---|
|功能描述|手动生成新token|
|输入参数|listener:更新完成的回调|
|返回值|无|
|使用说明|一般无需主动调用|

##### **getExpireTimestamp** 

|**函数原型**|**public long getExpireTimestamp(true)**|
|---|---|
|功能描述|查询token过期时间|
|输入参数|固定为true|
|返回值|UNIX时间戳|
|使用说明|token有效期为168小时|

### **SpeechEval.LangType 类** 

发音评测语种 

|**成员**|**含义**|
|---|---|
|enUS|英语|

### **SpeechEval.Mode 类** 

发音评测题型 

|**成员**|**含义**|
|---|---|
|WORD|单词题型|
|SENTENCE|句子题型|
|CHAPTER|段落题型|
|PHONEME|音标题型|
|QA|问答题型|
|TOPIC|看图说话/口语作文题型|
|RETELL|复述题型|
|RECITE|背诵题型|
|WORDCHECK|单词纠错题型|
|SENTENCECHECK|句子纠错题型|
|EXTCHOICE|扩展选择题型|

### **SpeechEval.Listener 类** 

发音评测回调接口 

##### **onResult** 

|**函数原型**|**void onResult(String result)**|
|---|---|
|功能描述|评测结果回调方法|
|输入参数(回调返回值)|result评测结果|
|返回值|无|
|使用说明|评测结果回调方法|

##### **onStartRecording** 

|**函数原型**|**void onStartRecording(String taskId)**|
|---|---|
|功能描述|开始录音回调方法|
|输入参数(回调返回值)|无|
|返回值|无|
|使用说明|开始录音回调方法|

##### **onStopSending** 

|**函数原型**|**void onStopSending()**|
|---|---|
|功能描述|评测结束回调方法|
|输入参数(回调返回值)|无|
|返回值|无|
|使用说明|评测结束回调方法|

##### **onGetAudio** 

|**函数原型**|**void onGetAudio(byte[] data)**|
|---|---|
|功能描述|实时返回录音方式调用评测时的音频|
|输入参数(回调返回值)|data:音频数据|
|返回值|无|
|使用说明|使用录音方式进行评测时,实时返回音频数据|
|**函数原型onGetVolume**|**void onGetVolume(double volume)**|
|功能描述|实时返回录音方式调用评测时的音量|
|输入参数(回调返回值)|volume:音量大小|
|返回值|无|
|使用说明|使用录音方式进行评测时,实时返回音量大小|

##### **onError** 

|**函数原型**|**void onError(String taskId,String code, String msg)**|
|---|---|
|功能描述|评测错误时的回调|
|输入参数(回调返回值)|code:错误码 msg:错误信息|
|返回值|无|
|使用说明|评测错误时的回调,onResult无结果|

##### **onWarning** 

|**函数原型**|**void onWarning(String taskId,String code, String msg)**|
|---|---|
|功能描述|评测警告时的回调|
|输入参数(回调返回值)|code:错误码 msg:错误信息|
|返回值|无|
|使用说明|评测警告时的回调,onResult有结果|

## **三、响应结果** 

请参考对应题型的 接口参数 文档。 

## **四、状态码表** 

请参考 状态码 文档。
