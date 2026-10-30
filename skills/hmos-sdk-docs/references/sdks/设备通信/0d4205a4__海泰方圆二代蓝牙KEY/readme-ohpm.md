> 来源: ohpm 中央仓 README(T1 信源) | 包: `ble` | ohpm 最新版: 1.0.2 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

海泰方圆二代蓝牙KEY SDK ,是一个基于BLE蓝牙协议通讯的硬件介质设备。本SDK基于鸿蒙操作系统进行适配,使其可以运行在 HarmonyOS中,满足商密算法应用,保障应用数据安全等需求。

- BLE通讯

- 商密算法,支持SM2、SM3、SM4

- 数字证书使用

- 可实现签名/验签、加密/解密操作

- 抗抵赖、保证数据安全

## 一、SDK使用说明 ##

**1.1 SDK 文件说明**

海泰方圆蓝牙KEY  SDK参考手册 V1.0 For Harmony OS 是基于鸿蒙系统平台开发的,针对鸿蒙系统提供的一个集成HAR包。我们将提供的压缩包含有以下文件夹:

	(1)doc:该文件夹下的内容是开发参考手册。

	(2)SDK:该文件夹下的内容是集成包文件。

	(3)demo:该文件夹下的内容是使用本 SDK 的Harmony OS示例工程。

**1.2 SDK 使用配置**

	(1).首先将SDK目录文件ble.har放到您的工程目录的某个文件夹下。

	(2).在您的工程目录下的oh_package.json5文件中的dependencies

	节点添加package,如截图所示:

	(3).使用import导入您需要调用的HAR提供的API函数,即可调用我司提供的功能,具体可参考DEMO。

	(4).添加权限,在您工程的模块的文件夹中找到module.json5文件中的requestPermissions节点中添加需要的权限,如截图所示:

## 二、接口说明 ##

**2.1 连接设备**

	函数	export function connectDev(component: object, deviceSN: string, callback: (code: number) => void)

	参数说明	component	上下文环境

	deviceSN	设备序列号

	callback	连接回调函数

	备注	

**2.2 断开连接**

	函数	export function disconnectDev(callback: (code: number) => void)

	参数说明	callback	断开连接回调函数

	备注	

**2.3 校验PIN**

	函数	export function verifyUserPin(pin: string, callback: (code: number, pdwRetryNum: number) => void)

	参数说明	pin	用户PIN

	callback	校验PIN回调函数

	备注	

**2.4 修改PIN**

	函数	export function changeUserPin(oldPin: string, newPin: string, callback: (code: number, pdwRetryNum: number) => void)

	参数说明	oldPIN	用户原PIN

	newPIN	用户新PIN

	callback	修改PIN回调函数

	备注	

**2.5 枚举证书**

	函数	export function enumCert(callback: (code: number, certList: ArrayList<HTUserCertInfo>) => void)

	参数说明	callback	枚举证书回调函数

	备注	

**2.6 报文签名**

	函数	export function sign(certInfo: HTUserCertInfo, hashAlg: number, pin: string, data: string, isP7: boolean,callback: (code: number, signData: string) => void)

	参数说明	certInfo	证书信息

	hashAlg	签名算法(HT_SHA1、HT_SHA256、HT_SM3)

	pin	用户PIN

	data	报文

	isP7	是否P7

	callback	签名回调函数

	备注	

**

2.7 KEY是否连接**

	函数	export function isConnected(callback: (isConnected: boolean) => void)

	参数说明	callback	获取KEY是否连接回调函数

	备注	

**2.8 是否初始化PIN**

	函数	export function isInitPin(callback: (code: number, isInitPin: boolean) => void)

	参数说明	callback	获取KEY是否初始化PIN回调函数

	备注	

**2.9 获取PIN剩余次数**

	函数	export function getPinRetryNum(callback: (code: number, pdwRetryNum: number) => void)

	参数说明	callback	获取PIN剩余次数回调函数

	备注	

## 三、错误码 ##

**3.1错误码**

	返回码	状态码	描述

	0	HT_SUCCESS	操作成功

	1	HT_OPERATION_FAILED	操作失败

	2	HT_NO_DEVICE	设备未连接

	3	HT_DEVICE_BUSY	设备忙

	4	HT_INVALID_PARAMETER	参数错误

	5	HT_PIN_ERROR	密码错误

	6	HT_USER_CANCEL	用户取消操作

	7	HT_OPERATION_TIMEOUT	操作超时

	8	HT_NO_CERT	没有找到证书

	9	HT_PIN_LOCK	PIN码锁定

	10	HT_COMM_ERROR	通讯错误

	11	HT_CERT_NOTMATCH	证书不匹配

	12	HT_PHONE_BT_CLOSE	手机蓝牙未开启

	13	HT_BLE_PLATFORM_NOT_SUPPORT_BLE	此设备不支持蓝牙4.0协议

	14	HT_SIGN_ALG_ERROR	签名算法错误

	15	HT_BT_DISCONNECT	蓝牙断开连接

	16	HT_TIP_USER	提示用户按键操作

您可查看错误码定义文件为”HTKeyReturnCode.ets”

## 四、数据结构及宏定义 ##

**4.1证书结构体**

//证书结构体定义

	HTUserCertInfo

		{

    		certType:number;//证书类型(1加密证书,2签名证书)

			certSN: string;//证书数列号

			certEndTime: string;//证书终止时间

			certStartTime: string;//证书起始时间

			certContainerName: string;//证书所在容器名

			cert: string;//证书BASE64编码值

			certIssuer: string;//证书颁发者信息

			certSubjectDN: string;//证书持有者信息

			certContainerParam: string;//证书所在容器属性

			certSignType: number;//证书签名属性(0 RSA,1 SM2)

		}

## 五、ohpm 安装指令 ##

	ohpm i ble
