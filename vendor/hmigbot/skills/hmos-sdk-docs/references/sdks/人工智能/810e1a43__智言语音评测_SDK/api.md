# **智言语音评测接口** 

###### **智言语音评测接口** 

交互流程 一 . 创建 Token 请求地址 Header Body (JSON) Response 二. 发起HTTP POST请求 连接地址 发起请求 Header 1 Body(JSON 格式) 2 Body(form-data 格式) 三、返回结果 四、状态码表 五、常见问题 

### **交互流程** 

## 创建token 

## 发送POST请求 

## 返回评测结果 

POST 请求支持 **JSON 格式** 和 **form-data 格式** ,请根据您的需求 **选择其一** 即可。 

### **一** **. 创建 Token** 

#### **请求地址** 

POST https://api.ai.smart-speech.com/auth/v2/createToken/{appId} 

{appId} 为商务分配给贵公司的 appId ,在 URL 中传参。 

#### **Header** 

|**参数名称**|**类型**|**说明**|**默认值**|
|---|---|---|---|
|Content-Type|String|请求类型|application/json|

#### **Body (JSON)** 

|**参数名称**|**类型**|**说明**|**默认值**|
|---|---|---|---|
|timestamp|Int|unix时间戳(10位)|必填|
|signature|String|数字签名|必填|
|sdk|String|传固定值: http|必填|

###### signature 的构造方式: 

1. 使用 appId 和 timestamp 请求参数构造规范化的请求字符串 stringToSign (注意参数顺序),如: 

appId=XXXX-XXXX-XXXX&timestamp=1234567890 

2. 将上一步构造的请求字符串使用 HMAC-SHA1 签名算法计算出对应的数字签名(Base64编码)。请使用商务 分配给贵公司的 appSecret 作为签名算法的密钥。 

signature = Base64(HMAC-SHA1(stringToSign, appSecret)) 

###### HMAC-SHA1 在线计算工具可用于比对生成的数字签名是否正确: 

- 消息:填入步骤 1 中构造的 stringToSign(请求字符串) 

- 算法:选择 SHA1 

- 密钥:填入您的 appSecret 

- 不要勾选下方的复选框 

- 点击计算按钮,“结果 B”即为正确的数字签名,如果您生成的数字签名与该结果一致,说明您生成的签名 是正确的 

###### **数字签名示例代码** 

Python Java Golang C语言 C#

#### **Response** 

{ "status":"00000", "message":"success", "data":{ "appId":"my-app-id-xxxxx",//创建token的appid "token":"xxxxxxxxxxxxxxxxxx", //生成的token, 有效期168小时 "currentTime": 1660523938, //当前服务器时间 "expireTime": 1660527538 //token过期时间戳(服务器时间) } } 

### **二. 发起HTTP POST请求** 

#### **连接地址** 

格式为: 

https://api.ai.smart-speech.com/soe/{语种代码}/{题型代码}/v2/api 

语种代码:英语 en-US ,中文 zh-cmn-Hans-CN 

请参考 题型文档 获取对应的题型代码。 

例如,中文单词题型(题型代码:word)的连接地址为: 

https://api.ai.smart-speech.com/soe/zh-cmn-Hans-CN/word/v2/api 

#### **发起请求** 

###### **注意:** 

评测耗时与音频和文本长度密切相关。对于 chapter、topic、retell 题型有可能耗时较长,因此请关注这些 题型的 responseTimeout 参数设置,以防返回结果超时。 

##### **Header** 

|**参数名称类型说明**|**默认值**|
|---|---|
|Authorization String 标准HTTP头,设置鉴权信息。要求格式必须是标准 Bearer <Token> 的形式(注意 Bearer 后面的空格)。|必填|
|sdk String 传固定值: http|必填|
|version String 传固定值: 1.0.0.0|选填|
|os String 操作系统和版本,例: Ubuntu 18.04|选填|
|deviceId String 设备唯一标识符,例: 0A15C7578CA2 **1 Body(JSON格式)**|按设备数 计费时必 填|
|**参数名称类型说明**|**默认值**|
|langType string 语种选项,英语 en-US,中文 zh-cmn-Hans-CN|必填|
|format string 音频格式,支持 wav、 mp3、 amr|必填|
|sampleRate int 音频采样率(Hz),当前仅支持 16000|必填|
|audioBase64 string 音频文件的Base64编码|与audioLink 二选一|
|audioLink string 音频文件的公网下载地址|与 audioBase64 二选一|
|looseness int 评分宽松度,范围:0-9,数值越大越宽松|4|
|connectTimeout int 连接超时时间(秒),范围:5-60|15|
|responseTimeout int 响应超时时间(秒),范围:5-60|chapter、 topic、retell 题型:45 其他题型:15|
|scale int 评分分制,范围:1-100|100|
|ratio float 评分调节系数,范围:0.8-1.5(最多保留3位小数) 该系数的作用是对30~90之间的得分(百分制)进行 上下调整,其他范围内的得分不变 ratio>1.0时,对评分进行上调,越接近75分,调 节程度越高 ratio<1.0时,对评分进行下调,越接近75分,调 节程度越高 ratio=1.0时,不进行评分调节|1.0|

|userId|string|userId建议设置,以方便区分不同的用户|空|
|---|---|---|---|
|audioUrl|boolean|是否返回音频地址 音频默认保留约30天,如需持久保存,建议接入方 下载至自己的服务器|false|
|maxPrefixSilenceMs|int|语音前置静音检测阈值(毫秒),范围[0~30000]。 录音开始后静音时长超过该阈值会返回一次Warning 事件。 参数值传0或不传该参数时,不开启前置静音检测功 能。|0|
|maxSuffixSilenceMs|int|语音后置静音检测阈值(毫秒),范围[0~30000]。 句尾静音时长超过该阈值会自动结束评测。 参数值传0或不传该参数时,不开启后置静音检测功 能。|0|
|connti|int|是否开启连读和失爆检测,默认为0,只针对英文 connti为0时,不开启 connti为1时, 开启||
|mini|int|默认为0,返回全量数据,当使用1时,只会返回简单 数据(总分、流利度、准确度、完整度等)||
|precision|string|设置打分精度,默认为0,只支持0、0.1、0.25、 0.5、1,如果设置的值不是这五个中的一个,则按0 处理||
|clientData|string|客户端自定义参数,会在返回结果中体现,建议不要 传过大的数据,否则影响评测|""|
|**params**|**dict**|题型参数,请参考 题型文档 获取对应的题型参数格 式。|必填|

###### **Body(JSON 格式) 示例** 

{ "params": { "mode": "word", "refText": "hello" }, "audioBase64": "xxxxxxxxxxxxxxxxxxxxx", "sampleRate": 16000, "format": "mp3", "langType": "en-US", "looseness": 4, "userId": "uid115862530" } 

##### **2 Body(form-data 格式)** 

|**参数名称**|**类型**|**说明**|**默认值**|
|---|---|---|---|
|langType|text|语种选项,英语 en-US,中文 zh-cmn-Hans-CN|必填|
|format|text|音频格式,支持 wav、 mp3 、 amr|必填|
|sampleRate|text|音频采样率(Hz),当前仅支持 16000|必填|
|audioFile|file|音频文件|必填|
|looseness|text|评分宽松度,范围:0-9,数值越大越宽松|4|
|connectTimeout|text|连接超时时间(秒),范围:5-60|15|
|responseTimeout|text|响应超时时间(秒),范围:5-60|chapter、 topic、retell题 型:45 其他题型:15|
|scale|text|评分分制,范围:1-100|100|
|ratio|float|评分调节系数,范围:0.8-1.5(最多保留3位小数) 该系数的作用是对30~90之间的得分(百分制)进行上下调 整,其他范围内的得分不变 ratio>1.0时,对评分进行上调,越接近75分,调节程度 越高 ratio<1.0时,对评分进行下调,越接近75分,调节程度 越高 ratio=1.0时,不进行评分调节|1.0|
|userId|text|userId建议设置,以方便区分不同的用户|空|
|audioUrl|boolean|是否返回音频地址 音频默认保留约30天,如需持久保存,建议接入方下载至 自己的服务器|false|
|maxPrefixSilence|int|语音前置静音检测阈值(秒),范围1~30。录音开始后静 音时长超过该阈值会返回一次Warning事件。 参数值传0或不传该参数时,不开启前置静音检测功能。|0|
|maxSuffixSilence|int|语音后置静音检测阈值(秒),范围1~30。句尾静音时长 超过该阈值会自动结束评测。 参数值传0或不传该参数时,不开启后置静音检测功能。|0|
|maxPrefixSilenceMs|int|语音前置静音检测阈值(毫秒),范围[0~30000]。录音开 始后静音时长超过该阈值会返回一次Warning事件。 参数值传0或不传该参数时,不开启前置静音检测功能。 **备注:** 优先级大于maxPrefixSilence|0|
|maxSuffixSilenceMs|int|语音后置静音检测阈值(毫秒),范围[0~30000]。句尾静 音时长超过该阈值会自动结束评测。 参数值传0或不传该参数时,不开启后置静音检测功能。 **备注:** 优先级大于maxSuffixSilence|0|
|||是否开启连读和失爆检测,默认为0,只针对英文||

|connti|int|connti为0时,不开启 connti为1时, 开启|0|
|---|---|---|---|
|mini|int|默认为0,返回全量数据,当使用1时,只会返回简单数据 (总分、流利度、准确度、完整度等)|0|
|precision|string|设置打分精度,默认为0,只支持0、0.1、0.25、0.5、1, 如果设置的值不是这五个中的一个,则按0处理|0|
|**params**|text|题型参数,请参考 题型文档 获取对应的题型参数格式。|必填|

###### **Body(form-data 格式) 示例** 

以 Postman 测试为例: 

### **三、返回结果** 

###### 请参考对应的 题型文档 。 

### **四、状态码表** 

|类 型|错误 码|说明|英文|提示开发者|提示最终用 户|备注|
|---|---|---|---|---|---|---|
|录 音 错 误|13000|缺少录音 权限|Missing recording permission|获取录音权限|获取录音权 限|重试获取录音权限|
|录 音 错|13001|录音占用|Recording in use|-|录音占用|比如接电话等情况|
|误|||||||
|录 音|13002|启动录音|Failed to start|-|重试|其他无法启动录音的错误|

|错 误||失败|recording||||
|---|---|---|---|---|---|---|
|网 络 错 误|13010|缺少网络 权限|Missing network permission|安卓:在AndroidManifest.xml中声明 Internet权限|联系客服||
|网 络 错 误|13011|无网络连 接|No network connection|-|检查网络连 接|有网络权限但没联网或网络信号差|
|在 线 调 用|11002|没有可用 次数|No available times|联系商务增加调用次数|联系客服|剩余可调用次数为0|
|在 线 调 用|11003|并发错误|Concurrency error|控制并发或联系商务增加并发配额|重试|超过并发限制|
|在 线 调 用|11004|语种过期|Language expired|联系商务|联系客服||
|在 线 调 用|11005|默认的内 部调用错 误|Default internal call error|重试,如仍无法解决需联系商务确认在 线服务状态|重试||
|在 线 调 用|11006|JSON序列 化失败|JSON serialization failure|检查JSON格式|联系客服|发送JSON格式不正确|
|在 线 调 用|11007|token过 期|Token expired|重新初始化(更新token)|重试|建立WebSocket连接时,token过期|
|在 线 调 用|11008|token错 误|Token error|重新初始化(更新token)|重试|建立WebSocket连接时,token错误|
|在 线 调 用|11009|sdk版本 错误|SDK version error|联系商务确认SDK|联系客服|该错误码暂未实现|
|在 线 调 用|11010|获取 token超 时|Token retrieval timeout|重新初始化,如仍无法解决需联系商务 确认在线服务状态|重试|请求createToken接口超时|
|在 线 调 用|11011|signature 错误|Signature error|检查appSecret,如仍无法解决需联系 商务确认SDK|联系客服|字符串拼接错误或appSecret错误|
|在 线 调 用|11012|appid不 可用|AppId not available|联系商务确认appId状态|联系客服|appid在线功能被禁用|
|在 线 调 用|11013|appid不 存在|AppId does not exist|检查appId|联系客服|appid不存在|
|在|||||||

|线 调 用|11014|生成 token错 误|Token generation error|重新初始化,如仍无法解决需联系商务 确认在线服务状态|重试|调用createToken接口时,缓存、数据库操作 失败|
|---|---|---|---|---|---|---|
|在 线 调 用|11015|非法的当 前时间|Illegal current time|校正系统时间|提示设备类 问题|设备时间与北京时间相差超过1小时|
|在 线 调 用|11016|内部并发 错误|Internal concurrency error|重试,如仍无法解决需联系商务确认在 线服务状态|重试|超过解码器并发限制|
|在 线 调 用|11017|不支持的 SDK类型|Unsupported SDK type|联系商务确认授权项|联系客服|SDK类型未授权|
|在 线 调 用|11018|不支持的 题型|Unsupported question type|联系商务确认授权项|联系客服|题型未授权|
|在 线 调 用|11019|不支持的 语种|Unsupported language|联系商务确认授权项|联系客服|appid不支持该语种|
|音 频 错 误|23100|音频格式 与参数不 匹配|Audio format does not match parameters|检查音频格式和format参数|联系客服||
|音 频 错 误|23101|音频长度 为0|Audio length is 0|检查音频数据长度|联系客服|音频时长=0时,回调onWarning同时返回评测 结果|
|音 频 错 误|23102|音频长度 超限|Audio length exceeds limit|交互界面上控制用户录音时间,避免录 音过长|联系客服|详见题型简介文档|
|音 频 错 误|23103|音频长度 过短|Audio length too short|交互界面上控制用户录音时间,避免录 音过短|点击过快|0<音频时长<240ms时,回调onWarning同时 返回评测结果|
|音 频 错 误|23104|音频音量 过低|Audio volume too low|检查录音正确性|提高说话音 量|音量过低时,回调onWarning同时返回评测结 果 (当音频短且音量低时,优先返回23104音 量过低)|
|音 频 错 误|23105|音频文件 大小超限|Audio file size exceeds limit|检查音频文件大小|-|音标、单词1MB,句子2MB|
|音 频 错 误|23106|无效的音 频地址|Invalid audio address|检查音频文件路径|-|访问地址后响应码不是200|
|音 频 错 误|23107|获取音频 文件超时|Audio file retrieval timeout|检查音频文件路径、检查下载速度|-|下载文件耗时超过responseTimeout|
|音 频 错 误|23108|句尾静音 长度超过 阈值|Sentence end silence exceeds threshold|-|停顿时间过 长,自动结 束评测|静音长度超过设置的maxSuffixSilence值,回 调onWarning同时返回评测结果|

|音 频 错 误|23109|句首静音 长度超过 阈值|Sentence start silence exceeds threshold|-|未检测到语 音|静音长度超过设置的maxPrefixSilence值,回 调onWarning|
|---|---|---|---|---|---|---|
|连 接 错 误|23110|连接超时|Connection timeout|重试|提示网络类 错误,并重 试|建立websocket超时|
|连 接 错 误|23111|连接断开|Connection lost|重试|提示网络类 错误,并重 试|websocket连接已断开但仍在发数据|
|连 接 错 误|23112|返回结果 超时|Return result timeout|重试|重试||
|连 接 错 误|23113|调用顺序 错误|Call sequence error|按照正确顺序调用|联系客服||
|连 接 错 误|23114|读取客户 端数据超 时|Reading client data timeout|重试|重试|因长时间没有接收到客户端数据,websocket 连接断开,弱网环境有可能发生|
|参 数 错 误|23120|XX参数类 型错误|XX parameter type error|联系商务确认SDK|联系客服||
|参 数 错 误|23121|XX参数缺 失|XX parameter missing|检查 langType/sampleRate/refText/mode 参数|联系客服|必填参数缺失|
|参 数 错 误|23122|XX参数错 误|XX parameter error|回调onError时,检查mode等必填参 数 回调onWarning时,检查scale等非 必填参数|联系客服||
|参 数 错 误|23123|评测文本 内容错误|Evaluation text content error|检查评测文本内容|联系客服|1输入文本为空 2输入文本只含标点符号、非 评测语种字符、类似(t:1)等韵律标签|
|参 数 错 误|23124|评测文本 长度超限|Evaluation text length exceeds limit|检查评测文本长度|联系客服|评测文本长度超限|
|参 数 错 误|23126|读音频文 件错误|Reading audio file error|检查路径和权限|联系客服|路径错误或权限不足|
|参 数 错 误|23127|taskId错 误|TaskId error|检查taskId|重试|HTTP分片传输接口|
|处 理 错 误|233xx|评分失败|Scoring failure|联系商务确认具体错误情况|重试||
|处 理|23301|服务处理|Service processing|-|重试||

错 误 

超时 

timeout 

### **五、常见问题** 

###### 1. **目前支持的最小安卓系统版本号是多少?** 

答:Android版本SDK目前支持4.4及以上版本。 

###### 2. **语音评测支持哪些应用平台?** 

目前语音评测支持:Android、HarmonyOS、iOS、Web、小程序、Linux、Windows、词典笔、RTOS等应 用平台 

###### 3. **语音评测支持的音频格式有哪些?** 

音频格式介绍,请查看 支持音频格式 文档 

###### 4. **错误码及相关的解决方案** 

错误码介绍,请查看 状态码 文档 

###### 5. **语音评测支持的题型、文本、音频时长限制、结果及各字段的含义** 

语音引擎支持题型、文本、音频时长限制,请查看 题型文档 和 参数介绍 文档 

###### 6. **为什么返回结果中没有音频 audioUrl地址,或者audioUrl地址为空?** 

如果是在线评测,需要在评测前传递audioUrl=true ,结果中才会返回audioUrl音频地址 

如果是离线评测,无论audioUrl=true或者false,都不会返回 

###### 7. **评测音频地址存储多久?** 

默认保留 **30** 天,如果需要更长时间存储,建议下载至自己的服务器
