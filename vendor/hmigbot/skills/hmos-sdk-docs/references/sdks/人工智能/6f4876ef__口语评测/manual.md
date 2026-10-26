# **口语评测鸿蒙SDK介绍** 

**官网** 

unievallibrary SDK是基于HarmonyOS开发的口语评测SDK,口语评测是基于语音识别和评价技术对发 音做客观打分,反馈发音正误和定位问题,有助于语音教学,发音练习,也可测试考生的口语水平。 **SDK包名** : **unievallibrary SDK版本号** : **1.0.0** 

**约束与限制** 

在下述版本通过验证: 

|**DevEco Studio版本号**|**HarmonyOS SDK版本号**|**手机操作系统ROM版本号**|
|---|---|---|
|DevEco Studio 5.0.3.100|【API12】HarmonyOS SDK 5.0.0.13(SP4)|3.0.0.13(SP6DEVC00E13R6P1)|

# **SDK集成说明** 

## **1.时序图** 

## **2.集成方式** 

## **2.1 下载安装** 

```
ohpmiunievallibrary
```

## **2.2 将SDK中libs下面的har包拷贝到工程的libs目录下;** 

工程结构图如下: 

```
"dependencies":
  {
    "unievallibrary": "file:libs/UniEvalLibrary.har"
  }
```

并在oh-package.json5中添加添加ohos.permission.INTERNET和ohos.permission.MICROPHONE权限 

运行过程动态申请ohos.permission.MICROPHONE权限 

## **3.题型说明** 

## **1、罗列语法** 

EvalText为:{"Version":"1","DisplayText":"Enumerate Grammar Tool 

Generated","GrammarWeight":"{"weight_struct": 

[[{"weight":0.5,"key":"apple"}]]}","Grammar":"#enumerate \nI like apple best\nMy favorite fruit is apple\n"} 

## **2、JSGF语法** 

EvalText为:{"Version":"1","DisplayText":"Jsgf Grammar Tool Generated","GrammarWeight":" {"weight_struct":[[{"weight":0.5,"key":"apple"}]]}","Grammar":"#JSGF V1.0 utf-8 cn;\ngrammar main;\npublic < main > = "< s >"(i like apple best|my favorite fruit is apple)"";\n"} 

## **3、复述题语法** 

EvalText为:{"Version":1,"EvalType":"en.exam.retell","DisplayText":"OralComposition Grammar Tool Generated","Language":"en","Grammar":"","GrammarWeight":"","Reference": 

{"ID":"","answers":[{"type":1,"text":"I like apple best"},{"type":1,"text":"My favorite fruit is apple"}]}} **4、普通题型** 

EvalText为:I like apple best 

## **置题工具** 

## **4.返回结果** 

## 响应结果说明 

|**名称**|**类型**|**说明**|
|---|---|---|
|version|string|结果格式版本及版本号|
|lines|array|每行输入文本的评测结果|
|EvalType|string|评测类型:general(朗读评测)、askandanswer(情景问 答)、composition(作文)|
|sample|string|输入的标准文本|
|usertext|string|用户实际朗读的文本(语音识别结果)|
|subwords|array|包含单词的音标、开始时间、结束时间、分数、音量信息|
|begin|double|开始时间,单位为秒|
|end|double|开始时间,单位为秒|
|volume|double|音量|
|score|string|分值|
|subtext|string|音标或重音符号信息|

|**名称**|**类型**|**说明**|
|---|---|---|
|integrity|double|录入语音的完整度|
|pronunciation|double|录入语音的标准度|
|fluency|double|录入语音的流利度|
|words|array|每个词的评测结果|
|text|string|单词或音素文本|
|type|int|类型,共有6种类型,分别是: 0多词:仅B,C,G模式出现,当朗读内容大于文本内容时, 多余的单词type值为0;eg:文本:nice to meet you,音 频:nice nice to meet you,第二个nice的type值为0; 1漏词:所有模式都有,当朗读内容小于文本内容时,未读的 单词type值为1;eg:文本:nice to meet you,音频:nice meet you,结果中to的type值为1; 2正常词:所有模式都有,识别正常的词; 3错误词:仅B,C,G模式出现,当朗读的文本某个单词识别 成文本中其他单词时,该单词type值为3。eg:文本:nice to meet you,音频:nice you meet you,结果中第一个you的 type值为3; 4静音:所有模式; 5重复词:预留接口,未实现; 7空格or标点:仅E模式,空格和标点的结构type值为7; 8生词:所有模式|
|sentSample|array|句式标准文本|
|sentScore|array|句式总分|
|sentPronunciation|array|句式标准度得分|
|sentFluency array|句式流 利度得 分||
|sentIntegrity|array|句式完整度得分|
|keySample|array|关键词sample(包括关键词和每个关键词的得分|
|keysScore|array|关键词总分|
|keysPronunciation|array|关键词标准度得分|
|keysIntegrity|array|关键词完整度得分|
|keysFluency|array|关键词流利度|
|standardScore|string|客户定制,输出的分制,当前含有4分制和8分制|
|StressOfSent|string|句子重读,每个单词都输出,0:该单词没有被重读;1:该单 词被重读|

|**名称**|**类型**|**说明**|
|---|---|---|
|StressOfWord|string|单词重音,将用户发音和词典的重音位置做比较,0:该单词 重音朗读错误;1:该单词重音朗读正确|
|tone|array|输出全部信息,数据可以用于画用户的发音曲线,目前只有内 部在使用|
|audiocheck|array|音质检测结果。volume:音量过小的置信度;clipping:截幅 的置信度;noise:噪音过大的置信度;cut:截断的置信度; too short:是否音频过短;emptyAudio:是否是空音频。 备注:置信度的值为0和10,10代表可能存在该项音质问题, 0代表该项检测正常|

## **5.错误码** 

错误码查询 

# **SDK接口说明** 

## **UniEvalUtil** 

## 评测静态工厂类,用于设置评测相关参数、发起评测、结束评测等。 

- init(ipAddress: string, uniEvalParam: UniEvalParam, callback: (event: number, result: string) => void, isUseLocalAudioCapturer?: Boolean): void; 

|**-**|**-**|
|---|---|
|说明|初始化评测相关配置|
|版本支持|最低1.0.0|
|参数ipAddress|服务的域名或者ip地址,可为空|
|参数uniEvalParam|评测相关参数|
|参数callback|事件和结果回调|
|参数isUseLocalAudioCapturer|是否使用sdk内部默认录音机|

## UniEvalParam类说明 

|**-**|**-**|
|---|---|
|说明|初始化时候需传入该对象|
|版本支持|最低1.0.0|
|变量Mode|(必填) mode可设置的内容值为word,sent,para,qa,retell,设置评测模 式|
|变量DisplayText|(普通评测必填) displayText评测文本|
|变量Appkey|(必填) appkey访问凭证|

|**-**|**-**|
|---|---|
|变量AudioFormat|(必填)audioFormat音频格式,支持16K单声道mp3,speex格式|
|变量eof|(必填)eof设置eof消息包内容,客户端需要该内容的唯一性,可选用 uuid|
|变量 ScoreCoefficient|(可选值) scoreCoefficient打分系数,值范围:0.6-1.9|
|变量userID|(可选值) userID用户信息|
|变量EvalType|(可选值)可设置的内容值为word,sentence,paragraph|
|变量Language|(可选值)语种,可设置的内容值为cn|
|变量ID|(可选值)一般为UUID,该次请求session id|

## callback类说明 

|**-**|**-**|
|---|---|
|说明|事件和结果回调|
|版本支持|最低1.0.0|
|参数|事件类型,-1代表错误回调,0代表正常评测结果回调,1代表评测结束,2代表评测|
|event|开始|
|参数 result|事件对应的结果|

start(): Promise 

|**-**|**-**|
|---|---|
|说明|开启评测|
|版本支持|最低1.0.0|
|**-** stop(): Promise|**-**|
|说明|结束评测|
|版本支持|最低1.0.0|

sendMessage(data: string | ArrayBuffer): void 

|**-**|**-**|
|---|---|
|说明|发送评测音频数据|
|版本支持|最低1.0.0|

|**-**|**-**|
|---|---|
|参数data|音频数据流|

setAudioCallback(callback: (buffer: ArrayBuffer, size: number) => void): void; 

|**-**|**-**|
|---|---|
|说明|设置音频数据回调事件|
|版本支持|最低1.0.0|
|参数callback|音频数据回调|
