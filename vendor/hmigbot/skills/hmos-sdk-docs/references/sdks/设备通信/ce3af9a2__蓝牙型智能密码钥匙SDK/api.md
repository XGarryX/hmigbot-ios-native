# 蓝牙Key 技术规范(鸿蒙端) 

### 神州融安科技(北京)有限公司 

2024.8.7 

# 目 录 

|蓝牙KEY 技术规范(鸿蒙端) .............................................. 1|
|---|
|修改记录.............................................................. 1|
|1. 鸿蒙平台集成方式................................................... 2|
|1.1. 接口定义....................................................... 2|
|1.1.1. 获得版本号..................................................6|
|1.1.2. 连接设备....................................................7|
|1.1.3. 连接情况下获取SN ........................................... 7|
|1.1.4. 检查是否默认PIN ............................................ 7|
|1.1.5. 获取PIN 码剩余次数..........................................8|
|1.1.6. 获取证书....................................................8|
|1.1.7. 获取证书起止时间............................................8|
|1.1.8. 获取证书CN ................................................. 9|
|1.1.9. 修改口令....................................................9|
|1.1.10. 签名-返回PKCS7 ........................................... 10|
|1.1.11. 初始化蓝牙UKey ........................................... 10|
|1.1.12. 产生证书请求..............................................11|
|1.1.13. 下载单证..................................................11|
|1.1.14. 下载双证..................................................12|
|1.1.15. 断开设备..................................................12|
|1.2. 回调函数ONSAFECALLBACK.......................................... 13|
|2. 参数定义.......................................................... 13|
|2.1. 错误码列表.................................................... 13|
|2.2. 非对称算法常量................................................ 15|
|2.3. 哈希算法常量.................................................. 15|

- 1 - 

|2.4. 证书类型常量.................................................. 15|
|---|
|4. USBKEY 交易流程....................................................16|
|4.1. 交易流程...................................................... 16|
|4.2. 交易数据模板.................................................. 16|
|4.3. 算法支持...................................................... 16|

- 2 - 

## 修改记录 

|时间|修改内容|修改人|备注|
|---|---|---|---|
|2024-6-11|增加鸿蒙接口定义|岳云龙||

第1页 

### 1. 鸿蒙平台集成方式 

厂商接口规范开发接口,使用stage 开发模型,最终提交一个库文件har 包 StandardHar.har,内部包含一个接口包IUKeyInterface.har。采用静态库方式。 

#### 1.1. 接口定义 

厂商的Har 包中要实现IUKeyInterface 类 

export interface IUKeyInterface { 

// 获取版本号 getVersion():string; 

// 连接接口 connect(SN:string, callback: (stateCode:number, result:number) => void):void; 

// 修改pin 

modifyPIN(SN:string, oldpin:string, newpin:string, cfmpin:string, callback: 

(stateCode:number, result:string) => void):void; 

// 获取ukey 的序列号 

getSn(callback: (stateCode:number, result:string) => void):void; 

// 检查是否默认PIN isDefaultPin(SN:string, callback: (stateCode:number, result:boolean) => void):void; 

// 获取PIN 码剩余次数 

getPinRetryTimes(SN:string, callback: (stateCode:number, result:number) => void):void; 

// 获取证书CN 

getCertCN(SN:string, CertType:number, callback: (stateCode:number, 

第2页 

result:string) => void):void; 

// 获取证书起止时间 

getCertTime(SN:string, CertType:number, callback: (stateCode:number, result:string) => void):void; 

// 获取证书 

getCert(SN:string, certType:number, callback: (stateCode:number, result:string) => void):void; 

##### // 签名 

sign(SN:string, signData:string, pin:string, signAlg:number, hashAlg:number, callback: (stateCode:number, result:string) => void):void; 

// 电子合同签名 

signHash(SN:string, xmlTips:string, signData:string, pin:string, signAlg:number, hashAlg:number, callback: (stateCode:number, result:string) => void):void; 

##### // 初始化 

initToken(SN:string, pin:string, callback: (stateCode:number, result:string) => void):void; 

// 生成P10 

generateP10(SN:string, pin:string, alg:number, hash:number, certType:number, dn:string, challenge:string, callback: (stateCode:number, result:string) => void):void; 

##### // 写入证书 

downloadCert(SN:string, pin:string, cer:string, callback: (stateCode:number, result:string) => void):void; 

第3页 

// 断开连接 disConnect():void; } 

export class Consts{ 

// 非对称算法定义 public static RSA = 0x00000001; public static SM2 = 0x00000002; 

// HASH 算法定义 public static MD5 = 0x00000001; public static SHA1 = 0x00000002; public static SHA256 = 0x00000003; public static SHA384 = 0x00000004; public static SHA512 = 0x00000005; public static SM3 = 0x00000006; public static SHAMD5 = 0x00000007; 

// 证书类型定义 

public static CERT_UNIVERSAL = 0x00000007; // 通用证书 public static CERT_DEAL = 0x00000008; // 交易证书 public static CERT_NORMAL = 0x00000009; // 普通证书 

//P7 类型定义 

public static readonly AttachPKCS7 = 1; public static readonly DetachPKCS7 = 2; public static readonly OnlySign = 3; } 

export class ErrorCodes{ 

// 错误码定义 

第4页 

public static KEY_SUCCESS = 0x00000000;// 操作成功 

public static KEY_OPERATION_FAILED = 0x00000001;// 操作失败 

public static KEY_NO_DEVICE = 0x00000002;// 设备未连接 

public static KEY_DEVICE_BUSY = 0x00000003;// 设备忙 

public static KEY_INVALID_PARAMETER = 0x00000004;// 参数错误 

public static KEY_PASSWORD_INVALID = 0x00000005;// 密码错误 

public static KEY_USER_CANCEL = 0x00000006;// 用户取消操作 

public static KEY_OPERATION_TIMEOUT = 0x00000007;// 操作超时 

public static KEY_NO_CERT = 0x00000008;// 没有证书 

public static KEY_CERT_INVALID = 0x00000009;// 证书格式不正确 

public static KEY_UNKNOW_ERROR = 0x0000000A;// 未知错误 

public static KEY_PIN_LOCK = 0x0000000B;// PIN 码锁定 

public static KEY_OPERATION_INTERRUPT = 0x0000000C;// 操作被打断(如来电等 

) 

public static KEY_COMM_FAILED = 0x0000000D;// 通讯错误 

public static KEY_ENERGY_LOW = 0x0000000E;// 设备电量不足,不能进行通讯 

public static KEY_BLUETOOTH_DISABLE = 0x0000000F;// 蓝牙未打开 

第5页 

public static KEY_DEV_WITHOUT_BLE = 0x00000010;// 不支持蓝牙ble 

public static KEY_PRESS_KEY = 0x00000011;// 请按键 

public static KEY_DEFAULT_PIN = 0x00000012;// PIN 码为默认PIN 

public static KEY_PIN_FORMAT_ERROR = 0x00000013; // PIN 码格式错误 

public static KEY_KEY_DISCONNECT = 0x00000014;// 设备连接断开 

public static KEY_PIN_INVALID_LENGTH = 0x00000015;// PIN 码长度错误 

public static KEY_PIN_TOO_SIMPLE = 0x00000016;// PIN 码过于简单 

public static KEY_PIN_SAME = 0x00000017;// 新旧密码相同 

public static KEY_SN_NOT_MATCH = 0x00000018;// 序列号与设备不匹配 

public static KEY_PIN_PRESS_KEY = 0x00000019;// 验PIN 按键确认 

public static KEY_PIN_NOT_MATCH = 0x00000020;// 新密码和确认密码不相同 

public static KEY_PIN_DECRYPT_ERROR = 0x00000021;// PIN 解密失败 public static KEY_PRESS_KEY_TWO = 0x00000022;// 交易签名第二次按键确认 public static KEY_PROGRESS = 0x00000023;// 产生P10 或下载证书过程的进度 

} 

“连接设备”、“获取设备SN”、“获取PIN 码剩余次数”、“获取证书”、“获取证 书起止时间”、“获取证书CN”、“修改口令”、“签名”、“断开设备”,具体的接口定 义如下: 

#### 1.1.1. 获得版本号 

第6页 

- 定 义:getVersion():string; 

- 功 能:获得驱动版本号。 

- 参 数:无。 

- 说 明:无。 

#### 1.1.2. 连接设备 

定 义:connect(SN:string, connectTime:number, callback: (stateCode:number, result:number) => void):void; 

- 功 能:连接蓝牙KEY. 

- 参 数: 

SN [IN] 蓝牙KEY 的序列号。 connectTime [IN] 连接超时时间,单位秒,可以填20。 callback [IN] 回调函数,可通过回调提示设备断开。 

- 说 明:错误码通过回调返回。蓝牙断开连接状态在这个接口的回调中返回,还有蓝牙UKey 低电量回调。 

#### 1.1.3. 连接情况下获取SN 

- 定 义:getSn(callback: (stateCode:number, result:string) => void):void; 

- 功 能:连接情况下,获取蓝牙key 的SN 

参 数: callback [IN] 回调函数,可通过回调提示按键 

- 说 明:错误码通过回调返回。 

#### 1.1.4. 检查是否默认PIN 

定 义:isDefaultPin(SN:string, callback: (stateCode:number, result:boolean) => void):void; 

- 功 能:通过序列号获取密码是否未默认PIN。 

- 参 数: 

SN [IN] 蓝牙KEY 的序列号。 callback [IN] 回调函数,可通过回调提示按键。 

第7页 

说 明:当读取PIN 信息成功时,通过回调返回是否是默认PIN,true 为默认PIN,false 为非默认PIN。 

#### 1.1.5. 获取PIN 码剩余次数 

定 义:getPinRetryTimes(SN:string, callback: (stateCode:number, result:number) => void):void; 

功 能:通过序列号获取密码剩余次数。 

参 数: 

SN [IN] 蓝牙KEY 的序列号。 callback [IN] 回调函数,可通过回调提示按键。 

说 明:当获取密码剩余次数成功时,通过回调返回密码剩余次数 , 其它情况通过回调返回错 误码。建议手机银行客户端调用交易签名之前,先调用此接口,一方面判断是否PIN 已锁定( 如果PIN 锁定,则不用弹出提示用户输入PIN,提前返回PIN 码已锁定的错误提示) 

#### 1.1.6. 获取证书 

定 义:getCert(SN:string, certType:number, callback: (stateCode:number, result:string) => void):void; 功 能:通过序列号获取证证书。 

参 数: 

SN [IN] 蓝牙KEY 的序列号。 certType [IN] 查看的证书类型,1 为rsa 签名证书,2 为sm2 签名证书( 

对应非对称算法常量)。 

callback [IN] 回调函数,可通过回调提示按键 

说 明:当读取证书内容成功时,通过回调返回证书内容的Base64 编码字符串;错误码通过 回调返回。该函数为读取蓝牙KEY 中证书内容所使用,读取蓝牙KEY 中证书之前需进行序列号 是否正确的检查,参数SN 即是用来进行序列号检查的。序列号需实时从蓝牙型UKey 内取得, 厂商接口不得缓存序列号。序列号检查不正确时,不予进行读取证书操作。 

#### 1.1.7. 获取证书起止时间 

第8页 

定 义:getCertTime(SN:string, CertType:number, callback: (stateCode:number, result:string) => void):void; 

功 能:通过序列号获取证书起止时间。 

参 数: 

SN [IN] 蓝牙KEY 的序列号。 

certType [IN] 查看的证书类型,1 为rsa 签名证书,2 为sm2 签名证书(对应非对 

称算法常量) 

callback [IN] 回调函数,可通过回调提示按键。 

说 明:当读取证书起止时间成功时,通过回调返回证书起止时间,格式为”XXXX-XXXX:XXXX-XX-XX”,其它情况错误码通过回调返回 

#### 1.1.8. 

#### 获取证书CN 

定 义:getCertCN(SN:string, CertType:number, callback: (stateCode:number, result:string) => void):void; 

功 能:通过序列号获取证书CN 

参 数: 

SN [IN] 蓝牙KEY 的序列号。 certType [IN] 查看的证书类型,1 为rsa 签名证书,2 为sm2 签名证书(对应非对 

称算法常量)。 

callback [IN] 回调函数,可通过回调提示按键。 

说 明:当读取证书CN 成功时,通过回调返回证书CN,其它情况错误码通过回调返回, 格式 为“证书颁发者CN-证书拥有者CN” 

#### 1.1.9. 修改口令 

定 义:modifyPIN(SN:string, oldpin:string, newpin:string, cfmpin:string, callback: (stateCode:number, result:string) => void):void; 

功 能:修改蓝牙KEY 的PIN 码;如果是初始默认密码,则设置密码,用修改pin 的接口, oldpin 参数传空。 

参 数: 

SN [IN] 蓝牙KEY 的序列号。 oldpin [IN] 蓝牙KEY 旧PIN 码。 

第9页 

newpin [IN] 蓝牙KEY 的新PIN 码。 callback [IN] 回调函数,可通过回调获取PIN 的剩余次数,以及是否需要按键。 

说 明:修改密码成功时通过回调返回值KEY_SUCCESS 表示成功,其它情况错误码通过回调返 回。该函数会通过应用提供的回调函数展示界面,提示用户按键确认。PIN 码长度6-12 位, 可以为数字、字母组合形式。密码不能为相同、顺序、逆序。 

#### 1.1.10. 签名-返回PKCS7 

定 义:sign(SN:string, signData:string, pin:string, signAlg:number, hashAlg:number, callback: (stateCode:number, result:string) => void):void; 

功 能:通过指定的密钥对类型和Hash 算法签名。 

参 数: 

SN [IN] 蓝牙KEY 的序列号。 signData [IN] 签名的原文。 pin [IN] 蓝牙KEY 的PIN 码。 signAlg [IN] signAlg 签名的密钥对类型(RSA,SM2 等)(3.2 非对称算法常量) hashAlg [IN] 签名的hash 算法(SHA-1,SHA-256、SHA512 等)(3.3 哈希算法常量) callback [IN] 回调函数,可通过回调提示按键。 

说 明:成功通过回调返回签名结果, 该签名结果为返 回attached 的P KCS7 格式的base64 , 否则通过回调返回错误码,当为交易数据签名时该函数会通过应用提供的回调函数展示界面, 提示用户按键确认。 

#### 1.1.11. 初始化蓝牙UKey 

定 义:initToken(SN:string, pin:string, callback: (stateCode:number, result:string) => void):void; 

功 能:初始化蓝牙设备,将清空设备中的证书,并将密码恢复到默认密码。 

参 数: 

SN [IN] 蓝牙KEY 的序列号。 

Pin[IN] 蓝牙KEY 的PIN 码(要传入默认PIN 码,或传入空或长度为0,SDK 自动填 

充默认PIN:123456)。 

callback [IN] 回调函数,可通过回调提示按键。 

第10页 

说 明:通过回调返回结果,其中stateCode 为KEY_SUCCESS 表示成功,此时result 为 Integer 类型的密码剩余次数,stateCode 为KEY_PRESS_KEY 时表示需要用户按键确认。 

#### 1.1.12. 产生证书请求 

定 义:generateP10(SN:string, pin:string, alg:number, hash:number, certType:number, dn:string, challenge:string, callback: (stateCode:number, result:string) => void):void; 

功 能:产生证书请求P10,此时蓝牙设备已调用过initToken 接口,密码为默认密码。 

参 数: 

SN [IN] 蓝牙KEY 的序列号。 pin [IN] 蓝牙KEY 的PIN 码。如果由APP 传入PIN,则用APP 传入;如果不传 入,则尝试用缓存PIN,如果不传PIN 且没有缓存PIN 则报错。 

- alg [IN] alg 签名的密钥对类型(RSA,SM2 等)(3.2 非对称算法常量) hash [IN] 签名的hash 算法(SHA-1,SHA-256、SHA512 等)(3.3 哈希算法常量) certType [IN] certType 签名的密钥对类型(RSA,SM2 等)(3.2 非对称算法常量) DN [IN] 证书DN。 challenge [IN] 挑战码(保留参数,默认不用传值)。 

callback [IN] 回调函数,可通过回调提示按键。 

说 明:通过回调返回结果,其中stateCode 为KEY_SUCCESS 表示成功,此时result 为 String 类型返回值,格式base64 编码的证书请求;stateCode 为KEY_PASSWORD_INVALID 时表 示密码错误,此时result 为密码剩余次数;stateCode 为KEY_PIN_LOCK 时表示密码已被锁定 ,result 为”0”;stateCode 为KEY_OPERATION_FAILED 时result 返回一个大于0 的错误码。 

#### 1.1.13. 下载单证 

定 义:downloadCert(SN:string, pin:string, cer:string, callback: 

- (stateCode:number, result:string) => void):void; 

功 能:下载单证。 

参 数: 

SN [IN] 蓝牙KEY 的序列号。 

第11页 

pin [IN] 蓝牙KEY 的PIN 码。如果由APP 传入PIN,则用APP 传入;如果不传 

入,则尝试用缓存PIN,如果不传PIN 且没有缓存PIN 则报错。 

cert [IN] 证书,base64 编码。 callback [IN] 回调函数,可通过回调提示按键。 

说 明:通过回调返回结果,其中stateCode 为KEY_SUCCESS 表示成功;stateCode 为 KEY_OPERATION_FAILED 时result 返回一个大于0 的错误码。 

#### 1.1.14. 下载双证 

定 义:downloadDualCert(SN:string, pin:string, priKey:string, exchangeCert:string, signCert:string, callback: (stateCode:number, result:number) => void):void; 

功 能:下载单证。 参 数: 

SN [IN] 蓝牙KEY 的序列号。 pin [IN] 蓝牙KEY 的PIN 码。如果由APP 传入PIN,则用APP 传入;如果不传 入,则尝试用缓存PIN,如果不传PIN 且没有缓存PIN 则报错。 priKey [IN] 加密证书私钥,base64 编码 exchangeCert[ IN] 加密证书,base64 编码 signCert [IN] 签名证书,base64 编码。 callback [IN] 回调函数,可通过回调提示按键。 

说 明:通过回调返回结果,其中stateCode 为KEY_SUCCESS 表示成功;stateCode 为 KEY_OPERATION_FAILED 时result 返回一个大于0 的错误码。 

#### 1.1.15. 断开设备 

定 义:disConnect():void; 

功 能:断开手机网银APP 与蓝牙KEY 的连接。 参 数:无。 返回值:无。 

第12页 

#### 1.2. 回调函数OnSafeCallback 

export interface OnSafeCallback<T> { 

/** 

- @Description 执行结果回调函数 

- @param stateCode 状态码 

- @param result 回调数据,可以是pin 码的可重试次数 

* 

- 

*/ onResult(errorCode:number, result:T); 

} 

说明:回调接口时用于在接口的调用过程中app 与接口之前的交互工作,比如在签名过程中需 要用户进行按键确认,这时候就需要利用回调通知app 提示用户进行按键。 stateCode 定义:KEY_PRESS_KEY 按键确认提示,这个状态值可根据实际需求进行扩充。 

### 2. 参数定义 

#### 2.1. 错误码列表 

|错误码|错误码变量名|错误码含义|
|---|---|---|
|0x00000000|KEY_SUCCESS|操作成功|
|0x00000001|KEY_OPERATION_FAILED|操作失败|
|0x00000002|KEY_NO_DEVICE|设备未连接|
|0x00000003|KEY_DEVICE_BUSY|设备忙|
|0x00000004|KEY_INVALID_PARAMETER|参数错误|
|0x00000005|KEY_PASSWORD_INVALID|密码错误|
|0x00000006|KEY_USER_CANCEL|用户取消操作|

第13页 

|0x00000007|KEY_OPERATION_TIMEOUT|操作超时|
|---|---|---|
|0x00000008|KEY_NO_CERT|没有证书|
|0x00000009|KEY_CERT_INVALID|证书格式不正确|
|0x0000000A|KEY_UNKNOW_ERROR|未知错误|
|0x0000000B|KEY_PIN_LOCK|PIN 码锁定|
|0x0000000C|KEY_OPERATION_INTERRUPT|操作被打断(如来电等)|
|0x0000000D|KEY_COMM_FAILED|通讯错误|
|0x0000000E|KEY_ENERGY_LOW|设备电量不足,不能进行通讯|
|0x0000000F|KEY_BLUETOOTH_DISABLE|蓝牙未打开|
|0x00000010|KEY_DEV_WITHOUT_BLE|不支持蓝牙ble|
|0x00000011|KEY_PRESS_KEY|按键确认|
|0x00000012|KEY_DEFAULT_PIN|PIN 码为默认PIN|
|0x00000013|KEY_CONNECT_TIMEOUT|设备连接超时|
|0x00000014|KEY_KEY_DISCONNECT|设备连接断开|
|0x00000015|KEY_PIN_INVALID_LENGTH|PIN 码长度错误|
|0x00000016|KEY_PIN_TOO_SIMPLE|PIN 码过于简单|
|0x00000017|KEY_PIN_SAME|新旧密码相同|
|0x00000018|KEY_SN_NOT_MATCH|序列号与设备不匹配|
|0x00000019|KEY_PIN_PRESS_KEY|验PIN 按键确认|
|0x00000020|KEY_PIN_NOT_MATCH|新密码与确认密码不相同|
|0x00000021|KEY_PIN_DECRYPT_ERROR|PIN 解密失败|
|0x00000022|KEY_PRESS_KEY_TWO|交易签名第二次按键确认|

第14页 

|0x00000023 KEY_PROGRESS|产生P10 或下载证书过程的进度|
|---|---|

#### 2.2. 非对称算法常量 

|常量|常量名|常量含义|
|---|---|---|
|0x01|RSA|RSA 类型证书|
|0x02|SM2|SM2 类型证书|

#### 2.3. 哈希算法常量 

|常量|常量名|常量含义|
|---|---|---|
|0x01|MD5|MD5 哈希算法|
|0x02|SHA1|SHA1 哈希算法|
|0x03|SHA256|SHA256 哈希算法|
|0x04|SHA384|SHA384 哈希算法|
|0x05|SHA512|SHA512 哈希算法|
|0x06|SM3|SM3 哈希算法|

#### 2.4. 证书类型常量 

|常量|常量名|常量含义|
|---|---|---|
|0x07|CERT_UNIVERSAL|通用证书|
|0x08|CERT_DEAL|交易证书|
|0x09|CERT_NORMAL|普通证书|

第15页 

### 4. USBKey 交易流程 

#### 4.1. 交易流程 

- A. 用户提交转账交易内容,弹出密码输入框请求用户输入USBKey 密码; 

- B. USBKey 对用户输入的密码进行校验,密码认证通过后,将交易报文发给USBKey 进行显示; 

- C. USBKey 显示收款人名称、收款人账号和交易金额,用户可以通过USBKey 上物理“上翻”、 “下翻”键进行显示内容查看,可通过USBKey 的“取消”键进行交易取消,通过USBKey 的“确定”键进行交易确认; 

- D. USBKey 用户确认前,可以通过USBKey 的“取消”键取消签名,如用户没有取消也没有确 认,USBKey 在超时时间后自动取消交易并返回错误码; 

- E. 用户按USBKey 的“确定”键进行交易确认。 

#### 4.2. 交易数据模板 

见文档《XML 报文说明.pdf》和《XML 报文格式.xml》 

#### 4.3. 算法支持 

对于交易数据签名,建议的算法组合如下: 

SHA256 + RSA2048 SHA512 + RSA2048 

SM3 + SM2 

第16页
