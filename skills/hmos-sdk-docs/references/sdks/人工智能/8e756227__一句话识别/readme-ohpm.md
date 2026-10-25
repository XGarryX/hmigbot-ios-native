> 来源: ohpm 中央仓 README(T1 信源) | 包: `unisoundspeechlibrary` | ohpm 最新版: 1.0.3 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

## 一、一句话识别SDK说明

一句话识别是将短时长(≤60秒)的语音片段高效、准确地转换为对应的文字信息。 它特别适用于各类需要快速、便捷交互的轻量级语音场景。例如:

语音搜索: 用户无需打字,直接说出关键词即可快速查找信息或服务。

语音输入: 在需要输入文字的地方(如聊天框、搜索栏、记事本),通过说话代替键盘输入,提升效率。

语音控制: 用户通过简洁的语音指令操作设备或应用(如“播放音乐”、“打开灯光”、“下一首”)。

其核心价值在于提供即时响应、解放用户双手,显著提升移动交互和效率场景下的用户体验。

SDK详细的接口介绍及说明请参考:

[示例demo](https://gitee.com/unisound_sh/asr-onesent/tree/master/)

[SDK包](https://gitee.com/unisound_sh/asr-onesent/tree/master/entry/libs)

## 二、集成方法

1、下载安装

* ohpm i unisoundspeechlibrary

2、将SDK中libs下面的UnisoundSpeechLibrary.har包拷贝到工程的libs目录下。

以下代码加入到oh-package.json5

```

"dependencies":

  {

    "library": "file:libs/UnisoundSpeechLibrary.har"

  }

```  

并在oh-package.json5中添加添加ohos.permission.INTERNET和ohos.permission.MICROPHONE权限

运行过程动态申请ohos.permission.MICROPHONE权限

## 三、识别结果

```

{

	"code": 0,

	"end": false,

	"msg": "success",

	"server_vad": false,

	"sid": "67165a9676dc4a818500545be0d9075a",

	"text": "北京",

	"type": "variable"

}

```

-|-  

:--|:--

参数	|描述

code|错误码

msg|结果说明

sid|识别的唯一id

server_vad|是否服务端智能断句

end|请求是否结束

type|结果类型:"variable":可变结果,"fixed":固定结果	

text|识别结果

## 四、错误码

[错误码查询](https://gitee.com/unisound_sh/asr-onesent/wikis/asrOneSent_result)
