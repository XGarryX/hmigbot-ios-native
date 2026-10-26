# 短文本语音合成SDK介绍 

unishorttextspeechlibrary SDK基于HarmonyOS开发的短文本语音合成SDK,将短文本( ≤ 500 字符)转换成自然流畅的语音,可流式播放,支持多种音色,并提供调节音量、语速、音高、亮度 等功能。适用于智能客服、语音交互、导航播报等场景。 

SDK包名:unishorttextspeechlibrary 

SDK版本号 : 1.0.0 

##### 约束与限制 

##### 在下述版本通过验证: 

|DevEco Studio版 本号|HarmonyOS SDK版本号|手机操作系统ROM版本号|
|---|---|---|
|DevEco Studio|【API12】HarmonyOS SDK|3.0.0.13(SP6DEVC00E13R6P1)|
|5.0.3.100|5.0.0.13(SP4)||
|DevEco Studio|【API22】HarmonyOS SDK|6.1.0.117(SP6C00E115R4P9patch15)|
|6.0.2|6.0.2.130||

# SDK集成说明 

## 一 、集成方式 

#### 1.1 下载安装 

ohpm i @unisound/shorttextspeechlibrary

#### 1.2 将SDK中libs下面的har包拷⻉到工程的libs目录下; 

##### 工程结构图如下: 

##### 在oh-package.json5文件,关联加载短文本语音合成库 

```
"dependencies":
  {
    "@unisound/shorttextspeechlibrary":
"file:libs/unishorttextspeechlibrary.har",
  }
```

在module.json5文件,添加网络权限 

## 二、使用说明 

### 初始化SDK 

```
 SpeechSdk.init(SDKParams.APP_KEY, SDKParams.APP_SECRET)
```

配置参数:appKey(必填)、appSecret(必填) 

### 设置语音合成参数 

```
@State speechParams: SpeechParams = {
    format: "pcm",
    vcn: "kiyo-plus",
    text: "",
    sample: 16000,
    speed: 50,
    volume: 50,
    pitch: 50,
    bright: 50
  }
SpeechEngine.getInstance().setSpeechParams(this.speechParams)
```

### 短文本合成语音 

```
  SpeechEngine.getInstance().playSpeech(this.speechParams.text)
```

### 短文本语音合成监听 

```
SpeechEngine.getInstance().setSpeechCallback({
      onInitializationComplete: (): void => {
      },
      onSpeechStart: (): void => {
      },
      onSpeechEnd: (): void => {
      },
      onError: (code: number, message: string): void => {
      },
      onStatus: (status: string): void => {
      },
      onSpeechResultData: (value: string | ArrayBuffer): void => {
      }
    })
```

## 三、TTS标签 

|类|标签|标注作用|文本标注|播报效果|
|---|---|---|---|---|
|别|||||
|数|<value>|使数字串按照数值的方式发音|这是第<value>110</value>|这是第一百|
|字|||会议室|一十会议室|
|类|<code>|使数字串按照编码的方式发音|这是第<code>110</code>会|这是一一零|
|||("1"读作"一")|议室|会议室|
||<tel>|使数字串按照电话号码的方式|会议室分机号为|会议室分机|
|||发音("1"读作"⺓")|<value>110</value>|号为⺓⺓零|

|注 音 类|<py>|使引擎按照指定的读音播报汉 字|搜索结果为<py>wei2</py> 空<py>kong1</py>会议室|搜索结果为 (wei2)空 (kong1)|
|---|---|---|---|---|
||<pname>|使引擎以正确播报姓名中的多 音字姓氏文本标注|播放<pname>单田芳 </pname>的评书|播放单 (shan4)田芳 的评书|
|断 句|<word>|根据标注的方式进行断词,用于 解决分词错误的问题,如:(乒乓|<word>乒乓</word> <word>球拍</word>|(乒乓)(球 拍)(卖完|
|类||球)(拍卖)(完了);(乒乓)(球拍) (卖完了)|<word>卖完了</word>|了)|
||<phrase>|根据标注的方式进行短语停顿 (比断词的停顿时间更长),用 于解决短语停顿错误的问题。 如:(爸爸亲了我妈妈)(也亲 了我);(爸爸亲了我)(妈妈也 亲了我)文本标注|<phrase>爸爸亲了我 </phrase><phrase>妈妈也 亲了我</phrase>|(爸爸亲了 我)(妈妈也 亲了我)|
|英 文 类|<letter>|将标注的英文单词按照逐个字 母的方式进行播报文本标注|世界卫生组织的英文缩写 <letter>WHO</letter>|世界卫生组 织的英文缩 写是(W) (H)(O)|
|其 他|<mute>|在句中手动添加适当长度的停 顿|请您再说一遍 <mute>300</mute>或说取 消|请您再说一 遍(停顿 300ms)或说 取消|
|四、|
错误码|将标注的文本使用别名中的内
容替换后进行播报|气压的测量单位是mmHg</mute>或说取
消|气压的测量
单位是毫米
汞柱|
|错误|码 说明|解决方法|||
|0|正确||||

|401|签名校验失败|客戶端检查参数参数是否正确|
|---|---|---|
|403|时钟偏移校验失败|客戶端检查时间参数参数是否正确|
|10001|appKey为空|客戶端检查Appkey参数是否正确|
|10002|appSecret为空|客戶端检查AppSecret参数是否正确|
|10003|基础地址为空|客戶端检查参数是否正确|
|10004|音频下载地址为空|客戶端检查下载地址是否正确|
|10005|文本为空|客戶端检查合成文本是否正确|
|10101|文本超过限制长度|文本长度控制500字以内|
|10201|连接错误|重新连接或者检查网络|
|20301|参数错误|客戶端检查参数是否正确|
|20302|发音人不可用|到控制台查看可用发音人|
|20303|服务内部错误|建议重试,或者提工单,工单详情请提供sid|
|20304|并发超过限制|减小并发或者购买并发套餐|
|20305|套餐次数使用完|购买次数套餐|
|20306|appKey不存在|检查appkey是否合法|
|20307|客戶端ip不在白名单 中|检查是否开启白名单,同时检查客戶端出口ip是否在ip白名单 中|

## 五、发音人列表 

音库类型 发音人名称 发音人风格 发音人代码 发音人描述

|精品音库|橙橙|默认|chengcheng-neutral-plus|知性大方|
|---|---|---|---|---|
|||开心|chengcheng-happy-plus||
|||生气|chengcheng-angry-plus||
|||厌恶|chengcheng-disgust-plus||
|||害怕|chengcheng-fear-plus||
|||难过|chengcheng-sad-plus||
|||吃惊|chengcheng-amazed-plus||
||莎莎|默认|shasha-neutral-plus|亲和自然|
|||开心|shasha-happy-plus||
|||生气|shasha-angry-plus||
|||厌恶|shasha-disgust-plus||
|||害怕|shasha-fear-plus||
|||难过|shasha-sad-plus||
|||惊喜|shasha-surprise-plus||
||晓迪|默认|xiaodi-plus|温柔舒缓|
|||温暖|xiaodi-warm-plus||
||Kiyo|元气|kiyo-plus|可爱女生|
|||职业|suren-plus||
||萱萱|默认|xuanxuan-plus|甜美女生|
|||端庄|xuanxuan-dignifed-plus||
||晓琴|默认|xiaoqin-plus|亲切温和|
||Jenny|默认|jenny-plus|纯正美音|

|小峰|默认|xiaofeng-plus|男播音员|
|---|---|---|---|
||庄重|xiaofeng-solemn-plus||
|小雯|默认|xiaowen-plus|女播音员|
||庄重|xiaowen-solemn-plus||
|天天|默认|tiantian-plus|天真男孩|
|糖糖|默认|tangtang-plus|活泼女孩|
|珍妮|默认|zhenni-plus|异域风情|
|玲玲|默认|lingling-plus|台湾女生|
|晓珂|默认|xiaoke-plus|漂亮御姐|
|宁宁|默认|ningning-plus|粤语女声|
|冰冰|默认|bingbing-duihua-plus|明亮利落|
||客服|bingbing-kefu-plus||
||消极|bingbing-neg-plus||
||积极|bingbing-pos-plus||
|⻉儿|默认|beier-plus|元气少女|

|惠惠|默认|huihui-normal-plus|成熟大方|
|---|---|---|---|
||中立|huihui-neutral-plus||
||生气|huihui-angry-plus||
||害怕|huihui-fear-plus||
||开心|huihui-happy-plus||
||难过|huihui-sad-plus||
||惊喜|huihui-surprise-plus||
||讽刺|huihui-sarcastic-plus||
||可疑|huihui-suspicious-plus||
|晨阳|默认|chenyang-normal-plus|真实自然|
||中立|chenyang-neutral-plus||
||生气|chenyang-angry-plus||
||害怕|chenyang-fear-plus||
||开心|chenyang-happy-plus||
||难过|chenyang-sad-plus||
||惊喜|chenyang-surprise-plus||
||讽刺|chenyang-sarcastic-plus||
||可疑|chenyang-suspicious-plus||
|小颖|默认|xiaoying-plus|亲和自然|
|雅琳|默认|yalin-plus|成熟温和|
|小亮|默认|xiaoliang-plus|清朗明快|
|明宇|默认|mingyu-plus|稳重浑厚|
|盈盈|默认|yingying-plus|四川女声|

||Tifany|默认|tifany-plus|纯正美音|
|---|---|---|---|---|
||Johnny|默认|johnny-plus|纯正美音|
||飞行少年|默认|feixingshaonian-plus|Rapper|
||嘉仪|默认|jiayi-plus|粤语女声|
||云婧|默认|yunjing-plus|女声|
||知轩|默认|zhixuan-plus|男声|
||云悠|默认|yunyou-plus|女声|
||姗姗|默认|shanshan-plus|四川女声|
||知翔|默认|zhixiang-plus|男声|
||绵儿|默认|mianer-plus|四川女声|
||zoey|默认|zoey-plus|英语女声|
||bill|默认|bill-plus|英语男声|
||jane|默认|jane-plus|英语女声|
|普通音库|Kiyo|默认|kiyo-base|可爱女生|
||小雯|默认|xiaowen-base|女播音员|
||小峰|默认|xiaofeng-base|男播音员|
||萱萱|默认|xuanxuan-base|甜美女生|
||天天|默认|tiantian-base|天真男孩|
||糖糖|默认|tangtang-base|活泼女孩|
||玲玲|默认|lingling-base|台湾女生|

# SDK接口说明 

## SpeechSdk 

静态类,用于设置短文本语音合成相关参数 

init(appKey: string, appSecret: string, baseUrl: string, downloadUrl: string) -|- 

:--|:-- 

版本支持|最低1.0.0 

参数 appKey(必填)|appKey访问凭证 

参数 appSecret(必填)|appSecret访问凭证 

参数 baseUrl(非必填)|服务的域名或者ip地址,不能为空 

参数 downloadUrl(非必填)|语音下载服务的域名或者ip地址,不能为空 

## SpeechEngine 

##### 用于设置短文本语音合成 

playSpeech(text: string) 

|-|-|
|---|---|
|说明|短文本合成语音|
|版本支持|最低1.0.0|
|变量text|(必填)短文本内容|

##### stopSpeech() 

|-|-|
|---|---|
|说明|停止短文本语音合成|
|版本支持|最低1.0.0|

##### setSpeechParams(params: SpeechParams) 

|-|-|
|---|---|
|说明|设置短文本语音合成参数|
|版本支持|最低1.0.0|

##### setSpeechCallback(callback: SpeechCallback) 

-

- - 

|说明|设置短文本语音合成回调事件|
|---|---|
|版本支持|最低1.0.0|
|callback|短文本语音合成回调|

## SpeechParams类说明 

|-|-|
|---|---|
|说明|语音合成参数|
|版本支持|最低1.0.0|
|参数format|音频格式,可选值pcm,默认pcm|
|参数sample|采样率(单位Hz),可选值8000,16000,24000,默认16000|
|参数vcn|发音人,参考发音人列表|
|参数speed|语速,可选值0~100,默认50|
|参数volume|音量,可选值0~100,默认50|
|参数pitch|音高,可选值0~100,默认50|
|参数bright|亮度,可选值0~100,默认50|
|参数text|需要合成的文本,最大500字符|

## SpeechCallback类说明 

|-|-|
|---|---|
|说明|短文本语音合成回调函数|
|版本支持|最低1.0.0|
|onInitializationComplete()|初始化回调|
|onSpeechStart()|语音合成开始|
|onSpeechEnd()|语音合成结束|

|onError(code: number, message: string)|错误回调|
|---|---|
|onStatus(status: string)|语音合成开始|
|onSpeechResultData(value: string | ArrayBufer,end:boolean)|语音合成开始|
