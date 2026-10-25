版权归汉王所有 

## 手写识别项目 

## API 集成指导说明书- 鸿蒙 

2026年1月12日 

版权归汉王所有 

##### 目录 

|1. 常量定义.......................................................... 1|
|---|
|2. 接口定义.......................................................... 2|
|2.1. 接口简述.................................................... 2|
|2.2. 接口函数说明................................................ 2|
|2.2.1. 初始化................................................ 2|
|2.2.2. 识别输入笔迹.......................................... 3|
|2.2.3. 获取版本号............................................ 3|

版权归汉王所有 

# 1. 常量定义 

#### 语言定义如下: 

|常量名|数值|意义|
|---|---|---|
|HW_RC_LANGUAGE_CN|0x01|简体中文|
|HW_RC_LANGUAGE_CT|0x02|繁体中文|
|HW_RC_LANGUAGE_JP|0x03|日文|
|HW_RC_LANGUAGE_KR|0x04|韩文|
|HW_RC_LANGUAGE_English|0x05|英文|
|HW_RC_LANGUAGE_French|0x07|法文|
|HW_RC_LANGUAGE_German|0x08|德文|
|HW_RC_LANGUAGE_Portuguese|0x09|葡萄牙文|
|HW_RC_LANGUAGE_Italian|0x0a|意大利文|
|HW_RC_LANGUAGE_Spanish|0x0b|西班牙文|
|HW_RC_LANGUAGE_Hungarian|0xc|匈牙利文|
|HW_RC_LANGUAGE_Dutch|0x0d|荷兰文|
|HW_RC_LANGUAGE_Indonesian|0x10|印度尼西亚文|
|HW_RC_LANGUAGE_Malaysian|0x11|马来西亚文|
|HW_RC_LANGUAGE_Danish|0x14|丹麦文|
|HW_RC_LANGUAGE_Swedish|0x15|瑞典文|
|HW_RC_LANGUAGE_Polish|0x17|波兰文|
|HW_RC_LANGUAGE_Czech|0x18|捷克文|
|HW_RC_LANGUAGE_Romanian|0x1a|罗马尼亚文|
|HW_RC_LANGUAGE_Turkish|0x21|土耳其文|
|HW_RC_LANGUAGE_Russian|0x32|俄文|
|HW_RC_LANGUAGE_Ukrainian|0x33|乌克兰文|

第 1 页共 3 页 

版权归汉王所有 

# 2. 接口定义 

### 2.1 接口简述 

接口包含一个Recognizer类,该类包含如下函数: 

|编号|函数名称|函数描述|
|---|---|---|
|1|constructor()|初始化|
|2|recognize()|识别|
|3|getVersion()|获取版本号|

### 2.2 接口函数说明 

根据功能,接口函数包含如下: 

### 2.2.1 初始化 

设置字典和识别语言,通过jni加载Resource文件的方式,加载资源文件。 

constructor (resmgr: resourceManager.ResourceManager, dicPath: 

string, languageId: number); 

|函数名||cons|tructor||
|---|---|---|---|---|
|函数概要 ||初始化 |识别核心 ||
|输入参数|类型|名字|描述|有效值域|
||resourceManager.|resmgr|ResourceMan|非空|
||ResourceManager||agerd对象||
||string|dicPath|字典路径|有效路径|
||number|languageId|语言类型Id|参看“语言定义”|
|返回值|boolean|无|是否成功|无|

第 2 页共 3 页 

版权归汉王所有 

### 2.2.2. 识别输入笔迹 

识别属性设置完成后,即可通过如下函数对手写轨迹进行识别。 用户书写完毕整个待识别的手写轨迹后,一次性整体识别手写轨迹。 

recognize(trace: Array<number>): Array<string> 

|函数名|||recognize||||
|---|---|---|---|---|---|---|
|函数概要|||识别笔迹||||
|输入参数|类型|名字|描述|有效值|域||
||Array<number>|trace|手写轨迹数据|直角坐标序列,|笔画|结束|
|||||使用(-1,0),|整个|笔迹|
|||||结束,使用(-1,|-1)。||
|||||例如: [x0,|y0,|x1,|
|||||y1, ..., xi,|yi,|-1,|
|||||0, xj, yj, .|..,|xm,|
|||||xn, -1,|0,|xs,|
|||||ys, ..., xt,|yt,|-1,|
|||||0, -1, -1]|||
|返回值|Array<string>|无|识别结果|非空|||

### 2.2.3. 获取版本号 

获取当前引擎的版本号。 

getVersion(): string 

|函数名|||getVersion||
|---|---|---|---|---|
|函数概要|||获取版本号||
|输入参数|类型|名字|描述|有效值域|
||||无||
|返回值|string|无|当前版本号|非空|

第 3 页共 3 页
