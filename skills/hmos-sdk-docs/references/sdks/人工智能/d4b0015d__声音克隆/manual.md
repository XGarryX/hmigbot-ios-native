## 声音克隆鸿蒙SDK介绍 

#### 官网 

声音克隆是云知声的“音视文”AIGC(AI Generated Content)项目中“音”的重要组成部分。 其本质是通过目标人少量的录音,训练得到音色和发音风格与录音非常相似的声音模型,快速“克 隆”目标人的说话人模型,进而使用该目标说话人音色完成指定发音任务。 

#### SDK包名 : @unisound/voiceclone 

SDK版本号 : 1.0.2 

约束与限制 

在下述版本通过验证: 

|DevEco Studio版 本号|HarmonyOS SDK版本号|手机操作系统ROM版本号|
|---|---|---|
|DevEco Studio|【API11】HarmonyOS SDK|3.0.0.13(SP6DEVC00E13R6P1)|
|5.0.9.100|5.0.0(12)||
|DevEco Studio|【API23】HarmonyOS|6.1.0.117(SP6C00E115R4P9patch15)|
|6.0.2|SDK6.1.0.117(SP6)||

# 一 、SDK说明 

声音克隆是云知声的“音视文”AIGC(AI Generated Content)项目中“音”的重要组成部分。 其本质是通过目标人少量的录音,训练得到音色和发音风格与录音非常相似的声音模型,快速“克 隆”目标人的说话人模型,进而使用该目标说话人音色完成指定发音任务。 示例demo 

SDK包 

# 二、SDK集成步骤 

## 1.调用流程 

# 二、集成方法 

## 1.1 下载安装 

```
  ohpm i @unisound/voiceclone
```

## 1.2 将SDK的har包拷⻉到工程的libs目录下; 

工程结构图如下: 

在oh-package.json5文件,关联加载声音克隆库 

```
"dependencies":
  {
    "@unisound/voiceclone": "file:libs/voiceclone.har"
  }
```

# 三、申请权限 

module.json5文件添加ohos.permission.INTERNET和ohos.permission.MICROPHONE权限 

```
 "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET"
      },
      {
        "name": "ohos.permission.MICROPHONE",
        "reason": "$string:EntryAbility_mic",
        "usedScene": {
          "abilities": [
            "FormAbility"
          ],
          "when": "always"
        }
      }
    ]
```

# 四、接入流程 

## 1、创建应用 

```
VoiceClone.initConfig(this.appKey, this.appSecret, this.cloneAddress)
SpeechSynthesizer.initConfig(this.appKey, this.appSecret,
this.syntheseAddress)
```

配置参数:appKey(必填)、appSecret(必填)、cloneAddress(选填)、syntheseAddress(选 填) 

## 2、创建克隆任务 

### 创建克隆任务 

```
VoiceClone.createCloneTask(
  this.userId,
  this.taskName,
  this.gender,
  this.age,
  (data: CloneTask) => {
    if (data.id != null && data.id.length > 0) {
```

`promptAction.showToast({ message: "` 任务创建成功 `" }) this.pageStack.replacePathByName("CloneVoiceTask", data)` 

- `} else {` 

```
      promptAction.showToast({
```

`message: "` 任务创建失败 `", duration: 2000` 

- `})` 

- `}` 

```
  },
  (code: number, msg: string) => {
    promptAction.showToast({
```

`message: `` 任务创建失败, `code=${code}` , `msg=${msg}`, duration: 2000` 

- `})` 

```
  }
)
```

### 获取默认文本 

`VoiceClone.getDefaultText( (data) => { let list: DefaultTextBean[] = [] data.forEach((item) => { list.push(new DefaultTextBean(item)) }) this.defaultTextList = list }, (code, msg) => { promptAction.showToast({ message: "` 请求失败, `code=" + code + ", msg=" + msg }) } )` 

### 音频文件上传 

```
VoiceClone.uploadAudio(
  this.taskId,
  textId,
  filePath,
```

`(data: UploadAudioResult) => { let result: string if (data.valid == 0) { result = `` 成功 `(` 匹配度 `${data.matchPercent}%)` } else { result = `` 失败 `(` 匹配度 `${data.matchPercent}%)` } }, (code: number, msg: string) => { promptAction.showToast({ message: "` 请求失败, `code=" + code + ", msg=" + msg }) })` 

### 提交训练任务 

`VoiceClone.commitTask( this.taskId, () => { promptAction.showToast({ message: "` 提交成功,请等待训练完成 `" }) this.pageStack.pop() }, (code: number, msg: string) => { promptAction.showToast({ message: "` 请求失败, `code=" + code + ", msg=" + msg }) })` 

## 3、获取声音列表 

`VoiceClone.requestVoiceList( this.userId, (data) => { let list: VoiceBean[] = [] data.forEach((item) => { list.push(item) }) this.voiceList = list }, (code, msg) => { promptAction.showToast({ message: "` 请求失败, `code=" + code + ", msg=" + msg }) } )` 

## 4、文本合成音频 

##### `//` 可选配置 

`SpeechSynthesizer.getInstance().setFormat(this.format) SpeechSynthesizer.getInstance().setSample(this.sample) SpeechSynthesizer.getInstance().setSpeed(this.speed) SpeechSynthesizer.getInstance().setSpeed(this.speed) SpeechSynthesizer.getInstance().setVolume(this.volume) SpeechSynthesizer.getInstance().setPitch(this.pitch) SpeechSynthesizer.getInstance().setBright(this.bright) SpeechSynthesizer.getInstance().setUserId(this.userId) //` 必填配置 

```
SpeechSynthesizer.getInstance().setVcn(this.voiceId)
SpeechSynthesizer.getInstance().playSpeech(this.text)
```

# 五、错误码 

|错误 码|说明|解决办法|
|---|---|---|
|0|成功||
|20401|appkey不存在|检查appkey是否配置正确|
|20402|请求参数错误|客戶端检查参数是否正确|
|20403|文件为空|检查音频文件是否存在|
|20404|训练任务提交失败|检查任务编号是否正确|
|20405|可供训练的录音文件不 足|音频文件不能少于20|
|20406|套餐已用完|购买时长套餐|
|20407|环境噪音检测不通过|找个安静地方录制音频|
|20408|训练中的任务不允许删 除|训练完成后可删除|
|20499|服务器内部错误|建议重试,或者提工单,工单详情请提供任务编号|
|20501|参数错误|客戶端检查参数是否正确|

|20502|发音人不可用|到控制台查看可用发音人|
|---|---|---|
|20503|服务内部错误|建议重试,或者提工单,工单详情请提供sid|
|20504|并发超过限制|减小并发或者购买并发套餐|
|20505|套餐次数使用完|购买次数套餐|
|20506|appkey不存在|检查appkey是否合法|
|20507|客戶端ip不在白名单中|检查是否开启白名单,同时检查客戶端出口ip是否在ip白名单 中|

# 六、SDK接口说明 

## VoiceClone 

声音克隆类,用于创建克隆任务、上传任务音频、获取声音列表等。 

static initConfig(appKey: string, appSecret: string, address?: string): void; 

|-|-|
|---|---|
|说明|初始化声音克隆相关配置|
|版本支持|最低1.0.0|
|参数appKey|调用者应用的appKey|
|参数appSecret|调用者应用的appSecret|
|参数address|服务的域名或者ip地址,可为空|

static getDefaultText(onSuccess: (data: ArrayList) => void, onFailed: (code: number, msg: string) => void): void; 

|-|-|
|---|---|
|说明|获取声音克隆的训练文本|
|版本支持|最低1.0.0|
|参数onSuccess|获取训练文本成功的回调|

获取训练文本失败的回调 

参数 onFailed 

#### DefaultText类说明 

|-|-|
|---|---|
|说明|训练所使用的默认文本|
|版本支持|最低1.0.0|
|变量readText|音频文本|
|变量textId|音频文本Id|
|变量readUrl|样音url|

static createCloneTask(userId: string, name: string, gender: Gender, age: number, onSuccess: (data: CloneTask) => void, onFailed: (code: number, msg: string) => void): void; 

|-|-|
|---|---|
|说明|创建克隆任务|
|版本支持|最低1.0.0|
|参数userId|接入方需保证用戶ID唯一性|
|参数name|克隆任务名称|
|参数gender|性别,Gender枚举类|
|参数number|年龄,0:成年(>=12),1:儿童(<12,内测中)|
|参数onSuccess|创建克隆任务成功的回调|
|参数onFailed CloneTask类说明|创建克隆任务失败的回调|
|-|-|
|说明|声音克隆任务类|

|版本支持|最低1.0.0|
|---|---|
|变量id|克隆任务Id|
|变量user_id|用戶Id|
|变量name|克隆任务名称|
|变量gender|性别|
|变量age|年龄|

static uploadAudio(id: string, textId: string, filePath: string, onSuccess: (data: UploadAudioResult) => void, onFailed: (code: number, msg: string) => void): void; 

|-|-|
|---|---|
|说明|音频提交检测|
|版本支持|最低1.0.0|
|参数id|克隆任务id|
|参数textId|训练文本id|
|参数 flePath|用戶音频地址|
|参数onSuccess|音频提交检测成功的回调|
|参数onFailed|音频提交检测失败的回调|

#### UploadAudioResult类说明 

|-|-|
|---|---|
|说明|声音克隆任务类|
|版本支持|最低1.0.0|
|变量valid|音频是否可用,0:是,1:否|
|变量matchPercent|音频、文本匹配度|
|变量highText|标记为匹配失败的文本段|

static commitTask(id: string, onSuccess: () => void, onFailed: (code: number, msg: string) => void): void; 

|-|-|
|---|---|
|说明|录制完成提交训练任务|
|版本支持|最低1.0.0|
|参数id|克隆任务id|
|参数onSuccess|录制完成提交训练任务成功的回调|
|参数onFailed|录制完成提交训练任务失败的回调|

static requestVoiceList(userId: string, onSuccess: (data: ArrayList) => void, onFailed: (code: number, msg: string) => void): void; 

|-|-|
|---|---|
|说明|获取我的声音列表|
|版本支持|最低1.0.0|
|参数userId|用戶Id|
|参数onSuccess|获取我的声音列表成功的回调|
|参数onFailed|获取我的声音列表失败的回调|

#### VoiceBean类说明 

|-|-|
|---|---|
|说明|声音信息类|
|版本支持|最低1.0.0|
|变量age|年龄|
|变量gender|性别|
|变量id|克隆任务Id|

|变量name|克隆任务名称|
|---|---|
|变量voiceId|音色Id,用于合成音频的数据|
|变量trainState|训练状态,0:无效训练1:训练成功2:训练中3:训练失败4:已过期5:已 删除|
|变量|训练失败的唯一码|
|errorCode||
|变量errorMsg|训练失败的描述信息|

static deleteVoice(id: string, onSuccess: () => void, onFailed: (code: number, msg: string) => void): void; 

|-|-|
|---|---|
|说明|删除声音|
|版本支持|最低1.0.0|
|参数id|克隆任务编号|
|参数onSuccess|删除声音成功的回调|
|参数onFailed|删除声音失败的回调|

static taskStatus(id: string, onSuccess: (data: TaskStatus) => void, onFailed: (code: number, msg: string) => void): void; 

|-|-|
|---|---|
|说明|查询训练状态|
|版本支持|最低1.0.0|
|参数id|克隆任务编号|
|参数onSuccess|查询训练状态成功的回调|
|参数onFailed|查询训练状态失败的回调|

TaskStatus类说明 

|-|-|
|---|---|
|说明|训练状态类|
|版本支持|最低1.0.0|
|变量trainState|训练状态,0:无效训练1:训练成功2:训练中3:训练失败4:已过期 5:已删除|
|变量 modelAddress|离线模型下载地址,仅限离线合成场景使用|
|变量errorCode|训练失败的唯一码|
|变量errorMsg|训练失败的描述信息|

static checkEnvironment(filePath: string, onSuccess: (data: EnvironmentStatus) => void, onFailed: (code: number, msg: string) => void): void; 

|-|-|
|---|---|
|说明|环境噪音检测|
|版本支持|最低1.0.0|
|参数 flePath|环境检测音频文件地址|
|参数onSuccess|环境噪音检测成功的回调|
|参数onFailed|环境噪音检测失败的回调|

#### EnvironmentStatus类说明 

|-|-|
|---|---|
|说明|环境噪音状态类|
|版本支持|最低1.0.0|
|变量envDecibel|环境噪音分⻉值|
|变量valid|样音检测编码,0:声音检测成功,1:环境检测不通过(声音大于20分⻉)|

## SpeechSynthesizer 

y 

#### 声音合成类,用于将文本合成音频。 

static initConfig(appKey: string, appSecret: string, address?: string): void; 

|-|-|
|---|---|
|说明|初始化声音合成相关配置|
|版本支持|最低1.0.0|
|参数appKey|调用者应用的appKey|
|参数appSecret|调用者应用的appSecret|
|参数address|服务的域名或者ip地址,可为空|

#### static getInstance(): SpeechSynthesizer; 

|-|-|
|---|---|
|说明|获取声音合成类的实例对象|
|版本支持|最低1.0.0|

#### setSyntheseCallback(callback: SyntheseCallback): void; 

|-|-|
|---|---|
|说明|设置声音合成的过程回调接口|
|版本支持|最低1.0.0|
|参数callback|回调接口实例对象|

#### playSpeech(text: string): void; 

|-|-|
|---|---|
|说明|开始合成音频|
|版本支持|最低1.0.0|
|参数text|需要合成的文本|

#### stopSpeech(): void; 

|- -|
|---|
|说明 停止合成音频|
|版本支持 最低1.0.0|
|setFormat(format: string): void; - -|
|说明 设置合成音频的音频格式|
|版本支持 最低1.0.0|
|参数format 音频格式|

setVcn(code: string): void; 

|-|-|
|---|---|
|说明|设置合成音频的音色id(voiceId)|
|版本支持|最低1.0.0|
|参数code|音色id(voiceId)|

setSpeed(speed: number): void; 

|-|-|
|---|---|
|说明|设置合成音频的语速|
|版本支持|最低1.0.0|
|参数speed|语速|

setVolume(volume: number): void; 

|-|-|
|---|---|
|说明|设置合成音频的音量|

|版本支持|最低1.0.0|
|---|---|
|参数volume|音量|

#### setPitch(pitch: number): void; 

|-|-|
|---|---|
|说明|设置合成音频的音高|
|版本支持|最低1.0.0|
|参数pitch|音高|

setBright(bright: number): void; 

|-|-|
|---|---|
|说明|设置合成音频的亮度|
|版本支持|最低1.0.0|
|参数bright|亮度|

setSample(sample: number): void; 

|-|-|
|---|---|
|说明|设置合成音频的采样率(单位Hz)|
|版本支持|最低1.0.0|
|参数sample|采样率(单位Hz)|

setUserId(userId: string): void; 

|-|-|
|---|---|
|说明|设置合成音频的用戶标识|
|版本支持|最低1.0.0|
|参数userId|用戶标识|

#### setSpeechParams(params: SyntheseParams): void; 

|-|-|
|---|---|
|说明|设置合成音频的参数配置|
|版本支持|最低1.0.0|
|参数params|音频参数配置|

#### SyntheseParams类说明 

|-|-|
|---|---|
|说明|音频参数配置类|
|版本支持|最低1.0.0|
|变量format|音频格式|
|变量sample|采样率(单位Hz)|
|变量vcn|音色id(voiceId)|
|变量speed|语速|
|变量volume|音量|
|变量pitch|音高|
|变量bright|亮度|
|变量userId|用戶标识|

## SyntheseCallback 

声音合成过程回调接口 

onSpeechStart: () => void 

声音合成开始回调 

onSpeechEnd: () => void 

- 声音合成结束回调 

#### onError: (code: number, message: string) => void; 

声音合成错误回调 

|参数||说明|
|---|---|---|
|code||错误码|
|message||错误信息|
|onStatus: (status: string) => void; 声音合成过程状态回调 参数|说明 参数|说明||
|status|状态|信息|

#### onSpeechResultData: (value: string | ArrayBuffer, end: boolean) => boolean 

#### 声音合成数据回调 

|参数||说明|
|---|---|---|
|value||音频数据|
|end||是否合成结束|
|返回|说明||
|boolean|是否应用内部 音频|自己处理音频,true则SDK不播报音频,false则SDK自动播放合成的|
