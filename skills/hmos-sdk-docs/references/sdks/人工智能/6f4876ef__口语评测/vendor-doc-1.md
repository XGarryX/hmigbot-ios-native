> 来源: 厂商官方文档页(T2 信源) | https://ai.unisound.com/doc/sacalleval/HarmonyOS-SDK.html | 抓取: 2026-07-17
> 注意: 单页快照,站内其余页面见来源链接

* 一、SDK说明
  * 二、SDK集成步骤
    * 1.调用流程
  * 三、Demo使用方法
  * 四、题型说明
    * 1、罗列语法
    * 2、JSGF语法
    * 3、复述题语法
    * 4、普通题型
  * 五、返回结果
  * 六、错误码

## # 一、SDK说明

基于语音识别和评价技术对发音做客观打分,反馈发音正误和定位问题,有助于语音教学,发音练习,也可测试考生的口语水平。  
SDK详细的接口介绍及说明请参考:[HarmonyOS文档](/doc/sacalleval/HarmonyOS.html)。

[示例demo (opens new window)](https://gitee.com/unisound_sh/eval-oral/tree/master/evaldemo)

[SDK包 (opens new window)](https://gitee.com/unisound_sh/eval-oral/tree/master/libs)

## # 二、SDK集成步骤

### # 1.调用流程

## # 三、Demo使用方法

将SDK中libs下面的har包拷贝到工程的libs目录下;  
工程结构图如下: 
    
    
    "dependencies":
      {
        "unievallibrary": "file:libs/UniEvalLibrary.har"
      }
    

1  
2  
3  
4  

该代码加入到oh-package.json5  
动态获取权限,运行过程需要给予应用所需要的录音及文件写入权限

## # 四、题型说明

### # 1、罗列语法

EvalText为:{"Version":"1","DisplayText":"Enumerate Grammar Tool Generated","GrammarWeight":"{"weight_struct":[[{"weight":0.5,"key":"apple"}]]}","Grammar":"#enumerate \nI like apple best\nMy favorite fruit is apple\n"}

### # 2、JSGF语法

EvalText为:{"Version":"1","DisplayText":"Jsgf Grammar Tool Generated","GrammarWeight":"{"weight_struct":[[{"weight":0.5,"key":"apple"}]]}","Grammar":"#JSGF V1.0 utf-8 cn;\ngrammar main;\npublic < main > = "< s >"(i like apple best|my favorite fruit is apple)"";\n"}

### # 3、复述题语法

EvalText为:{"Version":1,"EvalType":"en.exam.retell","DisplayText":"OralComposition Grammar Tool Generated","Language":"en","Grammar":"","GrammarWeight":"","Reference":{"ID":"","answers":[{"type":1,"text":"I like apple best"},{"type":1,"text":"My favorite fruit is apple"}]}}

### # 4、普通题型

EvalText为:I like apple best

[置题工具 (opens new window)](https://eplat.hivoice.cn/tools/exam-tool)

## # 五、返回结果

响应结果说明

名称 | 类型 | 说明  
---|---|---  
version | string | 结果格式版本及版本号  
lines | array | 每行输入文本的评测结果  
EvalType | string | 评测类型:general(朗读评测)、askandanswer(情景问答)、composition(作文)  
sample | string | 输入的标准文本  
usertext | string | 用户实际朗读的文本(语音识别结果)  
subwords | array | 包含单词的音标、开始时间、结束时间、分数、音量信息  
begin | double | 开始时间,单位为秒  
end | double | 开始时间,单位为秒  
volume | double | 音量  
score | string | 分值  
subtext | string | 音标或重音符号信息  
integrity | double | 录入语音的完整度  
pronunciation | double | 录入语音的标准度  
fluency | double | 录入语音的流利度  
words | array | 每个词的评测结果  
text | string | 单词或音素文本  
type | int | 类型,共有6种类型,分别是:  
0 多词:仅B,C,G模式出现,当朗读内容大于文本内容时,多余的单词type值为0;eg:文本:nice to meet you,音频:nice nice to meet you,第二个nice的type值为0;  
1 漏词:所有模式都有,当朗读内容小于文本内容时,未读的单词type值为1;eg:文本:nice to meet you,音频:nice meet you,结果中to的type值为1;  
2 正常词:所有模式都有,识别正常的词;  
3 错误词:仅B,C,G模式出现,当朗读的文本某个单词识别成文本中其他单词时,该单词type值为3。 eg:文本:nice to meet you,音频:nice you meet you,结果中第一个you的type值为3;  
4 静音:所有模式;  
5 重复词:预留接口,未实现;  
7 空格or标点:仅E模式,空格和标点的结构type值为7;  
8 生词:所有模式  
sentSample | array | 句式标准文本  
sentScore | array | 句式总分  
sentPronunciation | array | 句式标准度得分  
sentFluency array | 句式流利度得分 |   
sentIntegrity | array | 句式完整度得分  
keySample | array | 关键词sample(包括关键词和每个关键词的得分  
keysScore | array | 关键词总分  
keysPronunciation | array | 关键词标准度得分  
keysIntegrity | array | 关键词完整度得分  
keysFluency | array | 关键词流利度  
standardScore | string | 客户定制,输出的分制,当前含有4分制和8分制  
StressOfSent | string | 句子重读,每个单词都输出,0:该单词没有被重读;1:该单词被重读  
StressOfWord | string | 单词重音,将用户发音和词典的重音位置做比较,0:该单词重音朗读错误;1:该单词重音朗读正确  
tone | array | 输出全部信息,数据可以用于画用户的发音曲线,目前只有内部在使用  
audiocheck | array | 音质检测结果。volume:音量过小的置信度;clipping:截幅的置信度;noise:噪音过大的置信度;cut:截断的置信度;too short:是否音频过短;emptyAudio:是否是空音频。  
备注:置信度的值为0和10,10代表可能存在该项音质问题,0代表该项检测正常  
  
## # 六、错误码

[错误码查询 (opens new window)](https://gitee.com/unisound_sh/eval-oral-ws/wikis/ErrorCodeList)

← [ iOS SDK文档 ](/doc/sacalleval/iOS-SDK.html) [ 口语评测FAQ ](/doc/sacalleval/FAQ.html) →
