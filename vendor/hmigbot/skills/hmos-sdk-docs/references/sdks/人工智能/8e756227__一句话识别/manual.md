[[toc]] 

# **一** **、SDK说明** 

把语音(≤60秒)转换成对应的文字信息,适用于较短的语音交互场景,如语音搜索、语音输入、语音控制 等。 

SDK详细的接口介绍及说明请参考:HarmonyOS文档。 

示例demo 

SDK包 

# **二、集成方法** 

将SDK中libs下面的UnisoundSpeechLibrary.har包拷贝到工程的libs目录下。 以下代码加入到oh-package.json5 

```
"dependencies":
  {
    "library": "file:libs/UnisoundSpeechLibrary.har"
  }
```

并在oh-package.json5中添加添加ohos.permission.INTERNET和ohos.permission.MICROPHONE权 限 

运行过程动态申请ohos.permission.MICROPHONE权限 

# **三、识别结果** 

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

|**-**|**-**|
|---|---|
|参数|描述|
|code|错误码|
|msg|结果说明|
|sid|识别的唯一id|
|server_vad|是否服务端智能断句|
|end|请求是否结束|

|**-**|**-**|
|---|---|
|type|结果类型:"variable":可变结果,"fixed":固定结果|
|text|识别结果|

# **四、错误码** 

错误码查询
