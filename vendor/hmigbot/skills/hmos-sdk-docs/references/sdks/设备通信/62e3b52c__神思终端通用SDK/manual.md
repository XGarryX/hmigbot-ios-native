神 思 终 端 通 用 SDK 

接 入 文 档 

# 神思电子技术股份有限公司 

目 录 

目 录 2 

1. 背景说明 5 

2. 接口库介绍 5 

2.0 功能架构 5 

2.1 文件结构 6 

2.2 返回值 7 

2.3 接口函数 7 

2.3.1 基本接口 8 

2.3.1.1 打开设备 8 

2.3.1.2 关闭设备 8 

2.3.1.3 设置当前设备(多设备操作) 8 2.3.1.4 获取当前设备(多设备操作) 9 

2.3.1.5 获取接口库信息 9 

2.3.1.6 获取设备型号 9 

2.3.1.7 设备轮询心跳 9 

2.3.1.8 获取接收数据 10 

2.3.1.9 获取固件版本 10 

2.3.1.10 获取设备序列号 10 

2.3.2 二代证接口(二代证 / 外国人 / 港澳台) 11 

2.3.2.1 读取二代证 11 

2.3.2.2 读取追加住址 13 

2.3.2.3 获取 SAM 模块状态 13 

2.3.2.4 获取 SAM 模块编号字符串 13 

2.3.3 银行卡接口 14 

2.3.3.1 读取银行卡信息 14 

2.3.3.2 获取 ARQC 15 

2.3.3.3 执行脚本 16 

2.3.3.4 读取交易明细 16 

2.3.3.5 读取圈存记录 17 

2.3.4 社保卡接口 18 

2.3.4.1 读取社保卡信息 18 

2.3.4.2 获取读到的信息 18 

2.3.4.3 读取社保卡信息(根据卡结构) 19 

2.3.4.4 校验社保卡 PIN 码 20 

2.3.4.5 修改社保卡 PIN 码 20 2.3.4.6 重置社保卡 PIN 码 21 

2.3.5 磁条卡接口 21 

2.3.5.1 读取磁条卡(同步) 21 

2.3.5.2 写入磁条卡(同步) 21 

2.3.6 智能卡接口(接触 / 非接 CPU ) 22 

2.3.6.1 卡上电复位 22 

2.3.6.2 卡信息交互 22 

2.3.6.3 卡下电 23 

2.3.7 MifareOne 接口( M1 卡) 23 

2.3.7.1 寻卡 23 

2.3.7.2 密钥认证 23 

2.3.7.3 读块数据 24 

2.3.7.4 写块数据 24 

2.3.7.5 卡终止 24 

2.3.8 UltralightC 接口( M0 卡) 25 2.3.8.1 寻卡 25 

2.3.8.2 密钥认证 25 

2.3.8.3 读块数据 25 2.3.8.4 写块数据 25 

2.3.8.5 卡终止 26 

2.3.9 指纹仪接口 26 

2.3.9.1 采集指纹特征值 26 2.3.9.2 指纹特征值比对 26 

2.3.10 二维码接口 27 

2.3.10.1 读取二维码(同步) 27 2.3.10.2 取消读取二维码(同步) 27 2.3.10.3 允许读取二维码(异步) 27 2.3.10.4 读取二维码(异步) 28 2.3.10.5 禁止读取二维码(异步) 28 x.x.x 二代证原始信息接口 28 x.x.x.1 寻卡 28 x.x.x.2 选卡 28 

x.x.x.3 读卡 29 

x.x.x.4 读卡(含指纹) 29 

x.x.x.5 读追加地址 29 

x.x.x.6 读芯片序列号 SN 30 

x.x.x.7 获取 SAM 模块编号 30 

y.y.y 微模块原始接口 30 

y.y.y.1 读取 SAM 模块证书 30 

y.y.y.2 激活 SAM 模块 31 

y.y.y.3 解除激活 SAM 模块 31 

y.y.y.4 读取 SAM 模块激活状态 31 

y.y.y.5 获取 SAM 模块授权申请信息 32 y.y.y.6 SAM 模块授权确认 32 

y.y.y.7 核验身份证 32 

y.y.y.8 核验身份证并返回照片和指纹 33 

y.y.y.9 核验身份证比对识别码 34 

y.y.y.10 核验身份证比对识别码并返回照片和指纹 36 

y.y.y.11 核验性别或出生日期 37 

y.y.y.12 LED 氛围灯控制 38 

2.4 调用流程 38 

附录 40 

附录 A 常用语言开发调用指南 40 A1 、动态库及函数加载 40 

A2 、数据类型对应关系 41 

A3 、内存分配及调用方式 41 

附录 B 神思 USB 读卡器 VID_PID 对照表 42 

附录 C 接口兼容不同协议设备的使用方法 42 

附录 D 接口兼容其他密码键盘的方法 43 

# 1. 背景说明 

本文档旨在统一神思读卡终端与上位机通讯的用户接口,规定了接口 层具体接口的函数定义、参数及处理流程,适用于神思读卡终端上位 机接口的研发、集成及维护。 

# 2. 接口库介绍 

本接口 SDK 适用于神思读卡终端的集成开发工作,采用动态库导出函 数的方式提供接口,支持大多数开发语言的调用,提供 32 位和 64 位版 本,操作系统兼容 Windows/Linux/Android/HarmonyOS (接口规范 兼容,不同平台的 SDK 文件是独立的)。 

# 2.0 功能架构 

SDK 功能架构如下图所示: 

# 2.1 文件结构 

Windows 

Linux/Android 

HarmonyOS 

文件说明 

文 

件 

列 

表 

CommonInterface.dll 

libCommonInterface.so sdsescommoninterface.har 接口库或 har 包。所有接口均在此文件中导出 TerminalProtocol.dll libTerminalProtocol.so 

无 依赖库。通用读卡器协议层 PortCommunication.dll libPortCommunication.so 

无 依赖库。通用读卡器通讯层 WltRS.dll/unpack.dll /license.dat/msvcr100.dll 

libWltRS.so 

无 

依赖库。二代证照片解码库 

TerminalProtocolM05.dll 

libTerminalProtocolM05.so 

无 

依赖库。 SS728M05 读卡器协议层 

TerminalProtocolM03.dll 

libTerminalProtocolM03.so 

无 

依赖库。 SS728M03 读卡器协议层 

CommonInterface.ini 

CommonInterface.ini 

无 

配置文件。 AUTO 打开设备的连接参数 

CommonInterface.h 

CommonInterface.h/ 

JniCommonInterface.java 

无 

头文件。可根据需要,选择性使用 

CommonInterface.lib 

无 

# 无 

# 静态链接文件。静态加载 dll 时使用 

# 2.2 返回值 

对于没有特殊说明的接口函数,当返回值等于 0 时,表示成功;小于 0 时表示失败。返回值如下: 错误代码 

说 明 

0 

操作成功 

-1 

操作失败 

-2 

参数错误 

-3 句柄无效 

-4 暂不支持 

-5 

指针为空 

-6 

数据头错 

-7 

# 校验和错 

-8 

发送出错 

-9 

接收出错 

-10 

通讯超时 

-11 

解码库加载失败 

-12 

头像解码失败 

-13 

文件读写失败 

-14 

图片格式转换失败 

-15 

证件类型不符(二代证 / 外国人 / 港澳台) 

2.3 接口函数 

特殊说明: 

1 、调用约定:所有接口在 Windows 下使用 __stdcall 调用约定,在 Linux 、 Android 下无调用约定。 

2 、字符串编码:接口函数中未特殊说明的 “ 字符串 ” 类型参数,均为 GB18030 或 GBK 编码,可根据需要自行转换。 

例如在 Java 中获取出参 byte[] OutInfo 字符串的方式为: String s = new String(OutInfo, “GBK”).trim(); 

3 、出参内存分配:接口函数中未特殊说明的出参内容,分配 1024 字 节内存即可。 

4 、在 Android 下使用 JNI 的方式调用,因 JNI 的限制,务必保证本 SDK 包名为: com.sdses ,类名为: JniCommonInterface ,即 com.sdses 包 下的 java 文件不能修改。 

5 、在 HarmonyOS 下调用,本 SDK 包名为 sdsescommoninterface 。 

6 、 Sdt 开头的函数仅限支持 GA467 协议的设备使用。 

2.3.1 基本接口 

2.3.1.1 打开设备 

函数名称 

打开设备 

函数声明 

long OpenDevice(char *PortType, char *PortPara, char *ExtendPara); 

功能描述 

与设备建立通讯连接,返回设备句柄。 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

PortType 

IN 

# 字符串 

端口类型(详见参数补充说明) 

2 

PortPara 

IN 

# 字符串 

端口参数(详见参数补充说明) 

3 

ExtendPara 

IN 

# 字符串 

扩展参数(详见参数补充说明) 返回值 

大于 0 表示成功,数值为设备句柄;其他为失败。 

参数补充说明: 

PortType 

PortPara 

ExtendPara 

串口 

COMn 或 1~1000 

波特率( 9600 、 115200 ) 

串口扩展盒参数( 1B2541 ) 

USB 

USBn 或 1001~2000 

VID_PID ( 261A0011 、 261A0012 ) 中断传输为: MI 控制传输为: MC 网口 

SKT 

IP: 端口( 192.168.0.1:8080 ) 

蓝牙 

BTH 

蓝牙名称( SS728M801 ) 

自动 

AUTO 

# 注意事项: 

1 、 COMn 和 USBn 中 n∈1~1000 ,即 COM1~COM1000(1~1000) 和 USB1~USB1000(1001~2000) 

2 、 Linux/Android 下串口传参为: COM+ 串口文件路径,例如: 

COM/dev/ttyS4 

3 、端口类型为 AUTO 时,是指各参数通过 CommonInterface.ini 配置 文件获取,用法详见附录 C 方案二。 

神思 USB 读卡器的 VID_PID 对照表请参见附录 B 

2.3.1.2 关闭设备 

函数名称 

关闭设备 函数声明 

long CloseDevice(); 

功能描述 

断开与设备的通讯连接。 参数说明 序号 参数 

输入 / 输出 

类型 

含义 

返回值 

- 0 表示成功;非 0 表示失败。 

2.3.1.3 设置当前设备(多设备操作) 

# 函数名称 

# 设置当前设备 

# 函数声明 

long SetCurrentDevice(long DevHandle); 

# 功能描述 

一台 PC 连接多台读卡器时,通过设备句柄设置接下来要操作的设备。 参数说明 

序号 参数 

输入 / 输出 

类型 

含义 

1 

PortHandle 

IN 

长整型 

设备句柄 

返回值 

0 表示成功;非 0 表示失败。 

2.3.1.4 获取当前设备(多设备操作) 

函数名称 

获取当前设备 

# 函数声明 

long GetCurrentDevice(); 

功能描述 

一台 PC 连接多台读卡器时,获取当前操作的设备句柄。 参数说明 序号 参数 输入 / 输出 类型 含义 

返回值 返回当前设备的句柄。 2.3.1.5 获取接口库信息 函数名称 获取接口库信息 函数声明 

long GetLibraryInfo(char *Version, char * Description); 功能描述 

获取当前已加载的接口库详细信息。 

# 参数说明 

序号 参数 输入 / 输出 类型 含义 1 Version OUT 字符串 接口库版本 2 Description OUT 字符串 接口库描述 返回值 0 表示成功;非 0 表示失败。 2.3.1.6 获取设备型号 函数名称 获取设备型号 

# 函数声明 

long TerminalGetModel(char *TerminalModel); 

功能描述 

获取读卡器的型号。 参数说明 

序号 参数 输入 / 输出 类型 含义 

1 

TerminalModel 

OUT 

字符串 设备型号 返回值 0 表示成功;非 0 表示失败。 2.3.1.7 设备轮询心跳 函数名称 设备轮询心跳 函数声明 

long TerminalHeartBeat(); 

# 功能描述 

与设备进行握手通讯,用于检测与读卡器是否已建立连接并且通讯正 常。 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

返回值 

0 表示成功;非 0 表示失败。 

# 2.3.1.8 获取接收数据 

函数名称 

获取接收数据 

函数声明 

long GetLastRecvData(unsigned char *LastRecvData); 

功能描述 

获取最后一次通讯收到的数据,一般用于获取读卡器协议层错误信 息。 

参数说明 

序号 参数 输入 / 输出 类型 含义 1 LastRecvData OUT 字节数组 返回最后一次通讯收到的数据 返回值 返回收到的数据长度。 

2.3.1.9 获取固件版本 函数名称 获取设备固件版本 函数声明 

long TerminalGetFirmVersion(char *FirmVersion, char *HardwareVersion); 

功能描述 获取读卡器的固件版本号。 参数说明 

序号 

# 参数 

输入 / 输出 

类型 含义 

1 FirmVersion 

OUT 字符串 设备固件版本号 

2 

HardwareVersion 

OUT 字符串 设备硬件版本号 返回值 

0 表示成功;非 0 表示失败。 

2.3.1.10 获取设备序列号 

函数名称 获取设备序列号 函数声明 

long TerminalGetSn(char *TerminalSn); 

# 功能描述 

获取读卡器的固件版本号。 参数说明 

序号 参数 输入 / 输出 类型 含义 

1 

TerminalSn 

OUT 

字符串 设备序列号 返回值 

0 表示成功;非 0 表示失败。 

2.3.2 二代证接口(二代证 / 外国人 / 港澳台) 

2.3.2.1 读取二代证 函数名称 读取二代证 

# 函数声明 

long IdReadCard(unsigned char CardType, unsigned char InfoEncoding, char *IdCardInfo, 

long TimeOutMs); 

long SdtReadCard(unsigned char CardType, unsigned char InfoEncoding, char *IdCardInfo, 

long TimeOutMs); ( GA467 协议) 

功能描述 

读取第二代居民身份证或外国人永久居留证或港澳台居民居住证 参数说明 

序号 参数 

输入 / 输出 

类型 

含义 

1 

CardType 

IN 

字节 读取卡类型 

0x00 :读取二代证或外国人或港澳台 0x01 :只读二代证 0x02 :只读外国人 0x03 :只读港澳台 

以上参数不含指纹信息 

# 以下参数包含指纹信息 

0x10 :读取二代证或外国人或港澳台 (含指纹) 

0x11 :只读二代证(含指纹) 

0x12 :只读外国人(含指纹) 

0x13 :只读港澳台(含指纹) 

2 

# InfoEncoding 

IN 

字节 

返回信息的编码方式 

0x01 : GB18030 编码( GBK ) 

0x02 : UTF16-LE 编码 

0x03 : UTF-8 编码 

3 

IdCardInfo 

OUT 

字符串 

读取到的二代证 / 外国人 / 港澳台信息 

(至少分配 10240 字节的内存) 

4 

TimeOutMs 

# IN 

长整型 

读卡超时时间,单位为毫秒 

= 0 :不等待,无卡立即返回 

> 0 :等待放卡,指定时间内等待放卡 

返回值 

0 表示成功;非 0 表示失败。 

读卡返回信息 IdCardInfo 格式为以英文冒号分割的信息项,具体如 下: 

证件类型 : 中文姓名 : 英文姓名 : 性别 : 性别代码 : 民族 : 民族代码 : 出生日期 : 住址 : 身份证号码 : 签发机关 : 发卡日期 : 卡有效期 : 证件版本号 : 头像 JPG 照片 base64 编码 : 指纹特征值 base64 编码 

以上信息为二代证、外国人、港澳台信息项的并集,如果当前类型的 证件中不存在该项信息,则该项为空,具体证件中包含的信息项如 下: 

序号 

信息项 

二代证 

外国人 

港澳台 

自动解析函数 

0 

证件类型 

A 

I 或 Y 

J 

IdCardGetTypeFlag 

1 

中文姓名 姓名 中文姓名 姓名 

IdCardGetName 

2 

英文姓名 

英文姓名 

IdCardGetNameEn 

3 

性别 

性别 性别 

性别 

IdCardGetGender 

4 

性别代码 

性别代码 性别代码 性别代码 

IdCardGetGenderId 

5 

民族 民族 国籍或所在地区 

IdCardGetNation 

6 

民族代码 民族代码 国籍或所在地区代码 通行证号码 

IdCardGetNationId 

7 

出生日期 出生日期 出生日期 出生日期 

IdCardGetBirthDate 

8 

住址 

住址 

/ 永久居留证号码关联项 

住址 

IdCardGetAddress 

9 

身份证号码 

公民身份号码 

永久居留证号码 / 证件号码 公民身份号码 

IdCardGetIdNumber 

10 

签发机关 

签发机关 

当次申请受理机关代码 

签发机关 

IdCardGetSignOrgan 

11 

发卡日期 

有效期 

起始日期 

证件签发日期 

有效期 

起始日期 

IdCardGetBeginTerm 

12 

卡有效期 有效期 截止日期 证件终止日期 有效期 截止日期 

IdCardGetValidTerm 13 

证件版本号 

证件版本号 / 换证次数 签发次数 

IdCardGetVersion 

14 头像 JPG 照片 base64 编码 头像照片 base64 编码 头像照片 base64 编码 头像照片 base64 编码 

15 

指纹特征值 base64 编码 

指纹特征值 base64 编码 

指纹特征值 base64 编码 

各信息项建议通过拆分 IdCardInfo 字符串得到,不建议使用以下函数 获取: 

long IdCardGetName(char *Name); 

long IdCardGetNameEn(char *NameEn); long IdCardGetGender(char *Gender); long IdCardGetGenderId(char *GenderId); long IdCardGetNation(char *Nation); 

long IdCardGetNationId(char *NationId); long IdCardGetBirthDate(char *BirthDate); 

long IdCardGetAddress(char *Address); long IdCardGetIdNumber(char *IdNumber); long IdCardGetSignOrgan(char *SignOrgan); long IdCardGetBeginTerm(char *BeginTerm); long IdCardGetValidTerm(char *ValidTerm); long IdCardGetTypeFlag(char *TypeFlag); long IdCardGetVersion(char *Version); 

long IdCardGetFPBuffer(unsigned char *FPBuffer, long 

*FPBufferLen);// 返回 1024 字节指纹信息(两个手指) 

long IdCardGetPhotoFile(char *PhotoFile);// 入参 PhotoFile 为生成头 像文件的全路径,支持扩展名 wlt/bmp/jpg 

long IdCardGetPhotoBuffer(unsigned char WltBmpJpg, unsigned char *PhotoBuffer, long *PhotoBufferLen); 

WltBmpJpg 入参: 0x01 : wlt 格式 0x02 : bmp 格式 0x03 : jpg 格式 

# // 获取二代证原始信息 

long IdCardGetRawInfo(unsigned char *CHMsg, long *CHMsgLen, // 文字信息 

unsigned char *PHMsg, long *PHMsgLen, // 照片信息 

unsigned char *FPMsg, long *FPMsgLen); // 指纹信息 

2.3.2.2 读取追加住址 

函数名称 

# 读取追加住址 

# 函数声明 

long IdReadNewAddress(char *NewAddress); 

long SdtReadNewAddress(char *NewAddress); ( GA467 协议) 

功能描述 

读取二代证的追加住址信息 

参数说明 

序号 

参数 

# 输入 / 输出 

类型 

含义 

1 

NewAddress 

OUT 

字符串 

返回读取到的追加住址信息 返回值 

0 表示成功;非 0 表示失败。 2.3.2.3 获取 SAM 模块状态 函数名称 

获取 SAM 模块状态 函数声明 

long SamGetStatus(); long SdtSamGetStatus(); ( GA467 协议) 

功能描述 

获取公安部 SAM 安全模块状态。 

参数说明 

序号 参数 

输入 / 输出 

类型 

# 含义 

# 返回值 

0 表示成功;非 0 表示失败。 

2.3.2.4 获取 SAM 模块编号字符串 

函数名称 

获取 SAM 模块编号字符串 

函数声明 

long SamGetIdStr(char *SamIdStr); 

long SdtSamGetIdStr(char *SamIdStr); ( GA467 协议) 

功能描述 

获取公安部 SAM 安全模块编号字符串。(内部将编号转换为字符串) 参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

# SamIdStr 

OUT 

字符串 

SAM 模块编号字符串 

返回值 

0 表示成功;非 0 表示失败。 

2.3.3 银行卡接口 

2.3.3.1 读取银行卡信息 

函数名称 

读取银行卡信息 

# 函数声明 

long IccGetCardInfo(int ICtype, char *AIDList, char *TagList, char *IcCardInfo); 

功能描述 

读取金融 IC 卡信息。 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

# ICtype 

IN 

# 整型 

IC 卡类型, 0 接触, 1 非接, 2 自动 

2 

AIDList 

IN 

# 字符串 

应用列表,值为金融 IC 卡的应用列表,借记卡 为 “A000000333010101” ,贷记卡为 “A000000333010102” ,也可以 传入空, NULL 或 “” 。 

3 

TagList 

IN 

# 字符串 

要读取的信息标签,例: ”A” 。 

具体标签含义内容请看下面的标签列表 

4 

IcCardInfo 

OUT 

字符串 

返回读取信息 

格式:标签( 1 个字节) + 十进制长度( 3 个字节) + 数据( N 字 节); 

例: A0196228231825021494762 (标签为 A ,长度为 019 ,内容为 6228231825021494762 ) 

# 返回值 

0 表示成功;非 0 表示失败。 

标签列表: 数据元 

来自 IC 卡的数据 

标签 

标签 ASCII 码 卡号 

0x41 

A 

姓名 

0x42 

B 

证件类型 

00 :身份证 

01 :军官证 

02 :护照 

03 :入境证 

# 04 :临时身份证 

05 :其它 

0x43 C 

证件号码 

0x44 D 余额 不带小数点 0x45 E 

余额上限 不带小数点 

0x46 F 

单笔交易限额 

0x47 

G 

交易货币代码 

0x48 

H 

# 失效日期 

0x49 I IC 卡序列号 

0x4A 

J 二磁道信息 

0x4B 

K 

一磁道信息 

0x4C 

L 三磁道信息 

0x4D 

M 

卡类型 0: 接触 IC ; 1: 非接 IC 2: 磁条卡 

0x4F 

X 

# IC 卡当前 AID 

0x59 

Y 

2.3.3.2 获取 ARQC 

# 函数名称 

获取 ARQC 

# 函数声明 

long IccGetARQC(int ICtype, char *trData, char *AIDList, char *ARQC, char *trAppData); 

# 功能描述 

获取金融 IC 卡授权请求密文 ARQC 。 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

ICtype 

IN 

# 整型 

IC 卡类型, 0 接触, 1 非接, 2 自动 

2 

trData 

IN 

# 字符串 

交易数据,产生 ARQC 的数据,包含多个标签变量,参考下面标签列 表 

3 

AIDList 

IN 

# 字符串 

应用列表,值为金融 IC 卡的应用列表,借记卡 为 “A000000333010101” ,贷记卡为 “A000000333010102” ,也可以 传入空, NULL 或 “” 。 

4 

# ARQC 

OUT 

# 字符串 

授权请求密文及其相关数据,按银联规范中 55 域的数据 , ASCII 码的形 式 

5 

trAppData 

OUT 

# 字符串 

交易应用数据,将在检验 ARPC 时作为传入的数据。 返回值 

0 表示成功;非 0 表示失败。 

标签列表 : 

数据元 来自终端的数据 标签 

标签 ASCII 码 长度 授权金额 不带小数点,单位为分 0x50 P 012 其它金额 不带小数点,单位为分 0x51 

Q 012 交易货币代码 0x0156 ( 人民币 CNY ) 

0x52 

R 

004 

交易日期 

YYMMDD 

0x53 

S 

006 

# 交易类型 

《中国银联银行卡联网联合技术规范 V2.1 第 2 部分 报文接口规 范 .pdf 》 6.4 域 3 交易处理码 

0x54 

T 

002 

交易时间 

时分秒中间无分隔符 如: “110530” 

0x55 

U 

006 

商户名称 

0x57 

W 

# 2.3.3.3 执行脚本 

# 函数名称 

执行脚本 

# 函数声明 

long IccARPCExeScript(int ICtype, char *trData, char *ARPC, char *trAppData, 

char *ScriptResult, char *TC); 

功能描述 

执行银行返回的授权响应密文 ARPC 中的脚本。 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

ICtype 

IN 

整型 

IC 卡类型, 0 接触, 1 非接, 2 自动 

2 

trData 

# IN 

# 字符串 

交易数据,需与获取 ARQC 时数据一致 

3 

ARPC 

# IN 

# 字符串 

授权响应密文,后台返回的银联规范的 55 域数据, ASCII 码的形式。 若有执行脚本,需在后面添加脚本数据域,再执行脚本,没有脚本, 则完成操作。 

4 

trAppData 

IN 

# 字符串 

交易应用数据,在获取 ARQC 时返回的数据。 

5 

ScriptResult 

OUT 

# 字符串 

脚本执行结果,标签 DF31 ,输出转为半字节方式。例如: DF310521xxxxxxxx , DF31 是标签, 05 是后面五个字节数据, ‘2’ 代表 脚本执行成功, ‘1’ 代表失败,第 8 字节代表脚本号,后面 xxxxxxx 是发 卡行脚本标识。 

6 

TC 

OUT 

字符串 

GENERATE AC 2 返回的交易证书 TC 

返回值 

0 表示成功;非 0 表示失败。 

2.3.3.4 读取交易明细 

函数名称 

读取交易明细 

函数声明 

long IccGetTrDetail(int ICtype, char *AIDList, char *TrDetail); 功能描述 

读取金融 IC 卡中存储的交易记录明细。 

参数说明 

序号 参数 

输入 / 输出 

类型 

含义 

1 

ICtype 

IN 

# 整型 

IC 卡类型, 0 接触, 1 非接, 2 自动 

2 

AIDList 

IN 

# 字符串 

应用列表,值为金融 IC 卡的应用列表,借记卡 为 “A000000333010101” ,贷记卡为 “A000000333010102” ,也可以 传入空, NULL 或 “” 。 

3 

TrDetail 

OUT 

# 字符串 

返回的交易日志,每条日志数据包含多个标签变量。数据组合形式 为:明细条数( 2 位) + 明细总长度( 3 位) + 各条明细数据。各条明 细数据组合形式为:标签( 1 位) + 长度( 3 位) + 数据 

# 返回值 

0 表示成功;非 0 表示失败。 

TxDetail 标签列表 

数据元 

数据类型 

# 标签 

标签 ASCII 码 

授权金额 

不带小数点 , 单位为分 

0x50 

P 其它金额 

不带小数点 , 单位为分 

0x51 

Q 

交易货币代码 

0x52 

R 

交易日期 

YYMMDD 

0x53 

S 

交易类型 2 字节 

0x54 

T 

交易时间 

# HHMMSS 

0x55 

U 

终端国家代码 

0x56 V 商户名称 

0x57 

W 应用交易计数器( ATC ) 按十进制输出 0x58 X 2.3.3.5 读取圈存记录 函数名称 读取圈存记录 函数声明 

long IccGetLoadDetail(int ICtype, char *AIDList, char *LoadDetail); 功能描述 读取金融 IC 卡中存储的圈存记录。 

参数说明 

序号 参数 

输入 / 输出 

类型 

含义 

1 

ICtype 

IN 

# 整型 

IC 卡类型, 0 接触, 1 非接, 2 自动 

2 

AIDList 

IN 

# 字符串 

应用列表,值为金融 IC 卡的应用列表,借记卡 为 “A000000333010101” ,贷记卡为 “A000000333010102” ,也可以 传入空, NULL 或 “” 。 

3 

LoadDetail 

OUT 

# 字符串 

返回的圈存日志,每条日志数据包含多个标签变量。数据组合形式 

为:明细条数( 2 位) + 明细总长度( 3 位) + 各条明细数据。各条明 细数据组合形式为:标签( 1 位) + 长度( 3 位) + 数据;标签参考读 取交易明细标签 

返回值 

0 表示成功;非 0 表示失败。 

2.3.4 社保卡接口 

2.3.4.1 读取社保卡信息 

函数名称 

读取社保卡信息 

函数声明 

long SsseReadCard(int iType, char *SSCardInfo, char *SSErrorInfo);// 读第一、二代社保卡无需 PSAM ,读三代社保卡需要 PSAM 

long SsseReadCard2(int iType, char *SSCardInfo, char 

*SSErrorInfo); // 读第一、二代社保卡无需 PSAM ,读三代社保卡,插 入 PSAM 卡可读全部信息,不插 PSAM ,可读部分信息,读不出的信息 返回空 

# 功能描述 

读取第一 / 二 / 三代社保卡中的基本信息。(第三代社保卡需要配套的 PSAM 卡) 

参数说明 

序号 

参数 

输入 / 输出 

类型 

# 含义 

1 

iType 

IN 

整型 

社保卡类型: 

- 1 :接触式操作卡 

- 2 :非接触式操作卡 

- 3 :自动寻卡,接触式操作卡优先 

- 4 :自动寻卡,非接触式操作卡优先 

2 

# SSCardInfo 

OUT 

字符串 

返回读取到的社保卡信息,信息项以英文冒号分割,格式如下: 

卡的识别码 : 卡的类别 : 规范版本 : 初始化机构编号 : 发卡日期 : 卡有效期 : 卡号 : 身份证号码 : 姓名 : 姓名扩展 : 性别 : 民族 : 出生地 : 出生日期 

3 

SSErrorInfo 

OUT 

字符串 

# 出错时返回错误提示信息 

返回值 

0 表示成功;非 0 表示失败。 

2.3.4.2 获取读到的信息 

函数名称 

获取读到的信息 

函数声明 

long SsseGetCardInfo(char *Tag, char *SSCardInfo); 

# 功能描述 

获取 SsseReadCard 函数读取到的各项信息。(建议通过拆分 CardInfo 字符串得到,不建议使用此函数获取) 参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

Tag 

IN 

字符串 

要获取的信息标签值: 

# “01” :卡的识别码 

- “02” :卡的类别 

- “03” :规范版本 

- “04” :初始化机构编号 

- “05” :发卡日期 

- “06” :卡有效期 

- “07” :卡号 

- “08” :身份证号码 

- “09” :姓名 

- “4E” :姓名扩展 

- “0A” :性别 

- “0B” :民族 

- “0C” :出生地 

- “0D” :出生日期 

2 

SSCardInfo 

OUT 

字符串 

返回 Tag 对应的信息内容 

返回值 

- 0 表示成功;非 0 表示失败。 

2.3.4.3 读取社保卡信息(根据卡结构) 

# 函数名称 

读取社保卡信息(根据卡结构) 

# 函数声明 

long SsseReadCardEx(int iType, int iAuthType, char* pFileAddr, char* pOutInfo); 

# 功能描述 

根据社保卡规范中的卡结构,读取需要的信息项。(注意:部分信息 读取需要 PSAM 卡) 参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

iType 

IN 

整型 

社保卡类型: 

- 1 :接触式操作卡 

- 2 :非接触式操作卡 

- 3 :自动寻卡,接触式操作卡优先 

# 4 :自动寻卡,非接触式操作卡优先 

2 

iAuthType 

IN 

# 整型 

读控制认证方式,定义如下: 

1-PIN 校验; 

2-RK 密钥认证 

3 

pFileAddr 

IN 

# 字符串 

指定需要读取的文件名和数据项标签。 文件名及各数据项之间 以 “|” 分隔,且最后一个数据项以 “|” 结尾,文件以 “$” 结尾,文件名和 数据线参考社保卡规范文件结构。例如: SSSEEF05|06|07| $SSSEEF06|08|09|$ 

4 

pOutInfo 

OUT 

# 字符串 

返回的各数据项,其格式与输入参数 pFileAddr 严格对应且分隔符完 全一致。例如: 

# SSSEEF05| 卡有效期 | 卡号 |$SSSEEF06| 社会保障号码 | 姓名 |$ 

返回值 

0 表示成功;非 0 表示失败。 

2.3.4.4 校验社保卡 PIN 码 

函数名称 

校验社保卡 PIN 码 

# 函数声明 

long SsseVerifyPin(int iType, char* Pin, char* pOutInfo); 

# 功能描述 

校验社保卡卡片 PIN 码。(注意:密码错误次数过多会造成密码锁 定) 参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

iType 

IN 

整型 

社保卡类型: 

# 1 :接触式操作卡 

- 2 :非接触式操作卡 

- 3 :自动寻卡,接触式操作卡优先 

- 4 :自动寻卡,非接触式操作卡优先 

2 

Pin 

IN 

字符串 

待校验的 PIN 码字符串 

3 

pOutInfo 

OUT 

字符串 

当函数执行成功时,该输出参数为空字符串。 当函数执行失败时,该输出参数为错误信息描述。 返回值 

- 0 表示成功;非 0 表示失败。 

2.3.4.5 修改社保卡 PIN 码 

函数名称 

修改社保卡 PIN 码 

函数声明 

long SsseChangePin(int iType, char* OldPin, char* NewPin, char* pOutInfo); 

功能描述 

修改社保卡卡片 PIN 码。(注意:密码错误次数过多会造成密码锁 定) 参数说明 

序号 参数 输入 / 输出 

类型 

含义 

1 

iType 

IN 

整型 社保卡类型: 

- 1 :接触式操作卡 

- 2 :非接触式操作卡 

- 3 :自动寻卡,接触式操作卡优先 

- 4 :自动寻卡,非接触式操作卡优先 

2 

OldPin 

# IN 

字符串 

修改前的原 PIN 码 

3 

NewPin 

IN 

字符串 

修改后的新 PIN 码 

4 

pOutInfo 

OUT 

字符串 

当函数执行成功时,该输出参数为空字符串。 当函数执行失败时,该输出参数为错误信息描述。 

返回值 

0 表示成功;非 0 表示失败。 

2.3.4.6 重置社保卡 PIN 码 

函数名称 

重置社保卡 PIN 码 

函数声明 

long SsseReloadPIN(int iType, char* pCardInfo, char* NewPin, char* pOutInfo); 

# 功能描述 

忘记 PIN 码时,强制给社保卡重置一个新的 PIN 码。(注意:需要 PSAM 卡密钥支持) 参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

iType 

IN 

整型 社保卡类型: 

- 1 :接触式操作卡 

- 2 :非接触式操作卡 

- 3 :自动寻卡,接触式操作卡优先 

- 4 :自动寻卡,非接触式操作卡优先 

2 

pCardInfo 

IN 

字符串 

传入社保卡的基本信息,依次为:卡识别码、卡号。各数据项之间 以 “|” 分割 

3 

NewPin 

IN 

字符串 

新 PIN 码 

4 

pOutInfo 

OUT 

字符串 

当函数执行成功时,该输出参数为空字符串。 当函数执行失败时,该输出参数为错误信息描述。 返回值 

0 表示成功;非 0 表示失败。 

# 2.3.5 磁条卡接口 

2.3.5.1 读取磁条卡(同步) 

函数名称 

读取磁条卡(同步) 

函数声明 

long MagRead(unsigned char Tracks, char *TrackData1, char *TrackData2, char *TrackData3, unsigned char TimeOutSec); 

# 功能描述 

读取磁条卡磁道信息。 参数说明 

序号 参数 输入 / 输出 类型 含义 

1 

Tracks 

# IN 

字节 

读取磁道号: 1 、 2 、 3 、 12 、 13 、 23 、 123 

2 

TrackData1 

OUT 

字符串 一磁道信息 

3 

TrackData2 

OUT 

# 字符串 

二磁道信息 

4 

TrackData3 

OUT 

字符串 三磁道信息 

5 

TimeOutSec 

IN 

字节 等待刷卡超时时间,单位:秒 返回值 

0 表示成功;非 0 表示失败。 

2.3.5.2 写入磁条卡(同步) 函数名称 

写入磁条卡(同步) 函数声明 

long MagWrite(unsigned char Tracks, char *TrackData1, char *TrackData2, char *TrackData3, unsigned char TimeOutSec); 

功能描述 

写入磁条卡磁道信息。 

# 参数说明 

序号 参数 

输入 / 输出 类型 含义 

1 

Tracks 

IN 

字节 

写入磁道号: 1 、 2 、 3 、 12 、 13 、 23 、 123 

2 

TrackData1 

IN 

字符串 一磁道信息 

3 

TrackData2 

IN 

字符串 

二磁道信息 

4 

TrackData3 

IN 

字符串 

三磁道信息 

5 

TimeOutSec 

IN 

字节 

等待刷卡超时时间,单位:秒 返回值 

0 表示成功;非 0 表示失败。 

2.3.6 智能卡接口(接触 / 非接 CPU ) 

2.3.6.1 卡上电复位 

函数名称 

卡上电复位 

函数声明 

long CpuPowerOn(unsigned char Slot, unsigned char *ATRS, long *ATRSLen); 

# 功能描述 

对接触卡进行上电复位,返回 ATR ;对非接卡进行寻卡选卡,返回 ATS 。 

# 参数说明 

序号 参数 输入 / 输出 类型 含义 1 Slot IN 字节 卡槽号 

0x01~0x05 :接触用户大卡 0x11~0x15 :接触 PSAM 卡 0x41 :非接 Type A ,( 0x41 即字符 A ) 0x42 :非接 Type B ,( 0x42 即字符 B ) 

2 

ATRS 

OUT 

字节数组 卡片复位信息 

3 

# ATRSLen 

OUT 

# 长整型 

卡片复位信息长度 

返回值 

0 表示成功;非 0 表示失败。 

2.3.6.2 卡信息交互 

# 函数名称 

卡信息交互 

# 函数声明 

long CpuApdu(unsigned char Slot, long SendApduLen, unsigned char *SendApdu, unsigned char *RecvApdu, long *RecvApduLen); 

# 功能描述 

与卡片进行信息交互,收发 COS 支持的 APDU 指令。 

# 参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

Slot 

IN 

字节 

卡槽号(同上) 

2 

SendApduLen 

IN 

长整型 发送 APDU 的长度 

3 

SendApdu 

IN 

字节数组 发送 APDU 的数据 

4 

RecvApdu 

OUT 

字节数组 接收 APDU 的数据 

5 

RecvApduLen 

# OUT 

长整型 

接收 APDU 的长度 

返回值 

0 表示成功;非 0 表示失败。 

2.3.6.3 卡下电 

函数名称 

卡下电 

函数声明 

long CpuPowerOff(unsigned char Slot); 

功能描述 

对卡片下电。 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

Slot 

IN 

字节 

卡槽号(同上) 

返回值 

0 表示成功;非 0 表示失败。 

# 2.3.7 MifareOne 接口( M1 卡) 

2.3.7.1 寻卡 

函数名称 

寻卡 

# 函数声明 

long M1FindCard(unsigned char *UID, long *UIDLen); 

功能描述 

寻找选取读卡器上放置的 M1 卡。 

参数说明 

序号 参数 

输入 / 输出 

类型 

含义 

1 

UID 

OUT 

字节数组 

卡片 UID ,(一般是 4 字节) 

2 

UIDLen 

OUT 

长整型 

卡片 UID 的长度 

返回值 

0 表示成功;非 0 表示失败。 

2.3.7.2 密钥认证 

函数名称 

密钥认证 

函数声明 

long M1Authentication(unsigned char KeyType, unsigned char SecAddr, unsigned char *Key, unsigned char *UID); 

# 功能描述 

认证 M1 卡指定扇区的密钥。 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

KeyType 

IN 

字节 

# 密钥类型 

0x41 :密钥 A ,( 0x41 即字符 A ) 0x42 :密钥 B ,( 0x42 即字符 B ) 

2 

SecAddr 

IN 

字节 

扇区号,( 0~15 ) 

3 

Key 

IN 

字节数组 

密钥,( 6 字节) 

4 

UID 

IN 

字节数组 

# 寻卡返回的卡片 UID ,( 4 字节) 

返回值 

0 表示成功;非 0 表示失败。 

2.3.7.3 读块数据 

函数名称 

读块数据 

# 函数声明 

long M1ReadBlock(unsigned char BlockAddr, unsigned char *BlockData, long *BlockDataLen); 

功能描述 

读取 M1 卡指定块的数据。 

参数说明 

序号 参数 

输入 / 输出 

类型 

含义 

1 

BlockAddr 

IN 

字节 

块号,( 0~63 ) 

2 

# BlockData 

OUT 

字节数组 

块数据,(一般是 16 字节) 

3 

BlockDataLen 

OUT 

长整型 

块数据长度 

返回值 

0 表示成功;非 0 表示失败。 

2.3.7.4 写块数据 

函数名称 

写块数据 

函数声明 

long M1WriteBlock(unsigned char BlockAddr, long BlockDataLen, unsigned char *BlockData); 

功能描述 

写入 M1 卡指定块的数据。 

参数说明 

序号 

# 参数 

输入 / 输出 类型 含义 

1 

BlockAddr 

IN 

字节 块号,( 0~63 ) 

2 

BlockDataLen 

IN 

长整型 块数据长度 

3 

BlockData 

IN 

字节数组 

块数据,(一般是 16 字节) 返回值 

0 表示成功;非 0 表示失败。 

2.3.7.5 卡终止 

函数名称 

卡终止 函数声明 

long M1Halt(); 功能描述 将 M1 卡置于暂停工作状态。 参数说明 序号 参数 输入 / 输出 类型 含义 

返回值 

0 表示成功;非 0 表示失败。 

2.3.8 UltralightC 接口( M0 卡) 

2.3.8.1 寻卡 

函数名称 

寻卡 

# 函数声明 

long M0FindCard(unsigned char *UID, long *UIDLen); 功能描述 

寻找选取读卡器上放置的 M0 卡。 

参数说明 序号 参数 输入 / 输出 类型 含义 

1 

UID 

OUT 

字节数组 卡片 UID ,(一般是 7 字节) 

2 

UIDLen 

OUT 

长整型 卡片 UID 的长度 返回值 

# 0 表示成功;非 0 表示失败。 

# 2.3.8.2 密钥认证 

函数名称 

密钥认证 

函数声明 

long M0Authentication(unsigned char *Key); 功能描述 认证 M0 卡的密钥。 参数说明 序号 参数 输入 / 输出 

类型 

含义 

1 

Key 

IN 

字节数组 密钥,( 16 字节) 返回值 

0 表示成功;非 0 表示失败。 

2.3.8.3 读块数据 

# 函数名称 

# 读块数据 

# 函数声明 

long M0ReadBlock(unsigned char BlockAddr, unsigned char *BlockData, long *BlockDataLen); 

功能描述 读取 M0 卡指定块的数据。 参数说明 序号 参数 输入 / 输出 类型 含义 

1 

BlockAddr 

IN 

字节 块号,( 0~48 ) 

2 

BlockData OUT 

字节数组 

# 块数据,(一般是 4 字节) 

3 

BlockDataLen 

OUT 

长整型 

块数据长度 

返回值 

0 表示成功;非 0 表示失败。 

2.3.8.4 写块数据 

函数名称 

写块数据 

函数声明 

long M0WriteBlock(unsigned char BlockAddr, long BlockDataLen, unsigned char *BlockData); 

功能描述 

写入 M0 卡指定块的数据。 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

# BlockAddr 

IN 

字节 

块号,( 0~48 ) 

2 

BlockDataLen 

IN 

长整型 

块数据长度 

3 

BlockData 

IN 

字节数组 

块数据,(一般是 4 字节) 返回值 

0 表示成功;非 0 表示失败。 

2.3.8.5 卡终止 

函数名称 

卡终止 

函数声明 

long M0Halt(); 

功能描述 

将 M0 卡置于暂停工作状态。 

参数说明 序号 参数 

输入 / 输出 类型 含义 

返回值 

0 表示成功;非 0 表示失败。 

2.3.9 指纹仪接口 

2.3.9.1 采集指纹特征值 

函数名称 

采集指纹特征值 

函数声明 

long FpCapFeature(unsigned char *Feature, long *FeatureLen); 功能描述 

采集当前采集器上按压手指的指纹特征值。 

# 参数说明 

序号 参数 输入 / 输出 类型 含义 

1 

Feature 

# OUT 

字节数组 

指纹特征值,(一般是 512 字节) 

2 

FeatureLen 

OUT 

长整型 指纹特征值长度 返回值 

0 表示成功;非 0 表示失败。 

2.3.9.2 指纹特征值比对 

函数名称 

指纹特征值比对 

# 函数声明 

long FpMatchFeature(long FeatureLen1, unsigned char *Feature1, 

long FeatureLen2, unsigned char *Feature2, long *Score); 功能描述 

比对传入的两枚指纹特征值,并返回比对结果。 参数说明 

序号 参数 

输入 / 输出 

类型 

含义 

1 

FeatureLen1 

IN 

# 长整型 

特征值 1 的长度 

2 

Feature1 

IN 

字节数组 

特征值 1 

3 

FeatureLen2 

IN 

长整型 特征值 2 的长度 

4 

Feature2 

IN 

字节数组 

特征值 2 

5 

Score 

OUT 

长整型 返回的比对分数( 0~1000 ) 返回值 

0 表示成功;非 0 表示失败。 

2.3.10 二维码接口 2.3.10.1 读取二维码(同步) 函数名称 

读取二维码(同步) 

# 函数声明 

long QrRead(char *QrData, unsigned char TimeOutSec); 功能描述 

在指定的超时时间内,等待读取二维码信息。函数会阻塞,直到获取 到二维码信息或超时,函数才会返回。 参数说明 序号 参数 输入 / 输出 类型 含义 1 

QrData OUT 字符串 返回的二维码信息 

2 

TimeOutSec 

IN 

字节 等待扫码超时时间,单位:秒 返回值 

0 表示成功;非 0 表示失败。 

2.3.10.2 取消读取二维码(同步) 

函数名称 

取消读取二维码(同步) 

函数声明 

long QrCancel(); 

# 功能描述 

同步读取二维码时,未到超时时间,可通过该接口主动取消二维码读 取,取消后读取二维码接口会立即返回。 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

返回值 

- 0 表示成功;非 0 表示失败。 

2.3.10.3 允许读取二维码(异步) 

函数名称 

允许读取二维码(异步) 

# 函数声明 

long QrAsynEnable(unsigned char TimeOutSec); 

功能描述 

允许在指定的超时时间内读取二维码,本函数会立即返回。二维码内 容通过后续的 QrAsynRead 接口获取 参数说明 

序号 参数 

输入 / 输出 类型 含义 

1 

TimeOutSec 

IN 

字节 等待扫码超时时间,单位:秒 返回值 

0 表示成功;非 0 表示失败。 

2.3.10.4 读取二维码(异步) 

函数名称 

读取二维码(异步) 

函数声明 

long QrAsynRead(char *QrData); 

功能描述 

读取二维码信息,若存在已经扫描的二维码信息,则返回成功,否则 返回失败。无论有没有二维码信息,函数都会立即返回,不会阻塞。 参数说明 

序号 参数 

输入 / 输出 

类型 

含义 

1 

QrData 

OUT 

字符串 返回的二维码信息 返回值 

0 表示成功;非 0 表示失败。 2.3.10.5 禁止读取二维码(异步) 函数名称 禁止读取二维码(异步) 

函数声明 

long QrAsynDisable(); 

# 功能描述 

在不需要读取二维码信息时,调用该禁止读取函数。禁止后,即使扫 码二维码, QrAsynRead 也无法获取二维码信息了。 

参数说明 

序号 

参数 

输入 / 输出 类型 

含义 

返回值 

0 表示成功;非 0 表示失败。 

x.x.x 二代证原始信息接口 

x.x.x.1 寻卡 函数名称 寻卡 函数声明 

long IdFindCard(); 

long SdtFindCard(unsigned char *pucManaInfo); ( GA467 协议) 功能描述 

# 寻找读卡器上放置的二代证。 

参数说明 

序号 参数 

输入 / 输出 

类型 

含义 

# 返回值 

0 表示成功;非 0 表示失败。 

x.x.x.2 选卡 函数名称 选卡 

函数声明 

long IdSelectCard(); 

long SdtSelectCard(unsigned char *pucManaMsg); ( GA467 协议) 功能描述 

选取读卡器上放置的二代证。 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

# 返回值 

0 表示成功;非 0 表示失败。 

x.x.x.3 读卡 函数名称 读卡 

# 函数声明 

long IdReadBaseMsg(unsigned char *pucCHMsg, long *puiCHMsgLen, 

unsigned char *pucPHMsg, long *puiPHMsgLen); 

long SdtReadBaseMsg(unsigned char *pucCHMsg, long *puiCHMsgLen, 

unsigned char *pucPHMsg, long *puiPHMsgLen); ( GA467 协议) 功能描述 

读取二代证文字信息和相片信息。 

参数说明 

序号 

# 参数 

输入 / 输出 

类型 

含义 

1 

pucCHMsg 

OUT 

字节数组 

文字信息( 256 字节, UTF16_LE 编码) 

2 

puiCHMsgLen 

OUT 

长整型 文字信息长度 

3 

pucPHMsg 

OUT 

字节数组 

相片信息( 1024 字节, wlt 格式) 

4 

# puiPHMsgLen 

OUT 

长整型 

相片信息长度 

返回值 

0 表示成功;非 0 表示失败。 x.x.x.4 读卡(含指纹) 

函数名称 

读卡(含指纹) 

# 函数声明 

long IdReadBaseFpMsg(unsigned char *pucCHMsg, long *puiCHMsgLen, 

unsigned char *pucPHMsg, long *puiPHMsgLen, 

unsigned char *pucFPMsg, long *puiFPMsgLen); 

long SdtReadBaseFpMsg(unsigned char *pucCHMsg, long *puiCHMsgLen, 

unsigned char *pucPHMsg, long *puiPHMsgLen, 

unsigned char *pucFPMsg, long *puiFPMsgLen); ( GA467 协议) 

# 功能描述 

读取二代证文字信息、相片信息和指纹信息。 

# 参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

pucCHMsg 

OUT 

字节数组 

文字信息( 256 字节, UTF16_LE 编码) 

2 

puiCHMsgLen 

OUT 

长整型 文字信息长度 

3 

pucPHMsg 

OUT 

字节数组 

相片信息( 1024 字节, wlt 格式) 

4 

puiPHMsgLen 

OUT 

长整型 

相片信息长度 

5 

pucFPMsg 

OUT 

字节数组 

指纹信息( 1024 字节,两枚 512 特征值) 

6 

puiFPMsgLen 

OUT 

长整型 指纹信息长度 返回值 

0 表示成功;非 0 表示失败。 

x.x.x.5 读追加地址 函数名称 

读追加地址 

函数声明 

long IdReadNewAppMsg(unsigned char *pucAppMsg, long *puiAppMsgLen); 

long SdtReadNewAppMsg(unsigned char *pucAppMsg, long 

# *puiAppMsgLen); ( GA467 协议) 

功能描述 

读取二代证追加地址信息。 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

pucAppMsg 

OUT 

字节数组 

追加地址信息( 70 字节, UTF16_LE 编码) 

2 

puiAppMsgLen 

OUT 

长整型 

追加地址信息长度 

返回值 

0 表示成功;非 0 表示失败。 

# x.x.x.6 读芯片序列号 SN 

# 函数名称 

读芯片序列号 SN 

# 函数声明 

long IdReadSn(unsigned char *SN, long *SNLen); 

功能描述 

读取二代证芯片序列号 SN 。 参数说明 

序号 参数 输入 / 输出 

类型 

含义 

1 

SN 

OUT 

字节数组 

芯片序列号 SN ( 8 字节) 

2 

SNLen 

OUT 

# 长整型 

芯片序列号 SN 的长度 

返回值 

0 表示成功;非 0 表示失败。 

x.x.x.7 获取 SAM 模块编号 

函数名称 

获取 SAM 模块编号 

# 函数声明 

long SamGetId(unsigned char *SamId, long *SamIdLen); 

long SdtSamGetId(unsigned char *SamId, long *SamIdLen); ( GA467 协议) 

# 功能描述 

获取公安部 SAM 安全模块编号。 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

SamId 

OUT 

# 字节数组 

# SAM 模块编号 

2 

SamIdLen 

OUT 

长整型 SAM 模块编号长度 返回值 

0 表示成功;非 0 表示失败。 y.y.y 微模块原始接口 y.y.y.1 读取 SAM 模块证书 

函数名称 读取 SAM 模块证书 函数声明 

long MIdSamGetCert(unsigned char *Cert, long *CertLen); 功能描述 读取公安部 SAM 微模块签名证书。 参数说明 

序号 参数 输入 / 输出 

类型 

# 含义 

1 

Cert 

OUT 

字节数组 

SAM 签名证书 

2 

CertLen 

OUT 

长整型 

SAM 签名证书长度 返回值 

0 表示成功;非 0 表示失败。 

y.y.y.2 激活 SAM 模块 

函数名称 

激活 SAM 模块 

函数声明 

long MIdSamEnable(long EnableDataLen, unsigned char *EnableData); 

# 功能描述 

激活公安部 SAM 微模块。微模块只有在激活后,身份证核验 API 接口 “ ” 功能才可以正常调用(找卡、选卡接口除外)。 从未激活 的微模 

块,身份证核验 API 接口只支持有限次调用,且返回的 “ 核验信息 ” 为 测试信息。 

参数说明 

序号 参数 

输入 / 输出 

类型 含义 

1 

EnableDataLen 

OUT 

长整型 激活数据长度 

2 

EnableData 

OUT 

字节数组 激活数据 返回值 

0 表示成功;非 0 表示失败。 y.y.y.3 解除激活 SAM 模块 

函数名称 

# 解除激活 SAM 模块 

# 函数声明 

long MIdSamDisable(long DisableDataLen, unsigned char *DisableData); 

功能描述 

解除激活公安部 SAM 微模块。 “ 解除激活 ” 后,微模块身份证核验 API 接口功能被禁用。 

参数说明 

序号 参数 

输入 / 输出 

类型 

含义 

1 

DisableDataLen 

OUT 

长整型 解除激活数据长度 

2 

DisableData 

OUT 

字节数组 

# 解除激活数据 

返回值 

0 表示成功;非 0 表示失败。 

# y.y.y.4 读取 SAM 模块激活状态 

# 函数名称 

# 读取 SAM 模块激活状态 

# 函数声明 

long MIdSamGetEnableState(unsigned char *EnableState, long *RemainNum, char *EnableTime, char *DisableTime, unsigned char *SecondCert, long *SecondCertLen, unsigned char *EncryptCert, long *EncryptCertLen, unsigned char *SignCert, long *SignCertLen); 

# 功能描述 

解除激活公安部 SAM 微模块。 “ 解除激活 ” 后,微模块身份证核验 API 接口功能被禁用。 

# 参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

EnableState 

OUT 

字节 

激活状态 

0x00 :从未激活 

0x01 :已经激活 

0x02 :解除激活 

2 

RemainNum 

OUT 

长整型 

剩余授权调用次数 

在激活状态下,为 0xFF, 表示剩余授权次数大于或等于 0xFF ,其他值 为剩余授权次数;未激活状态下,为 0x00 

3 

EnableTime 

OUT 

字符串 

激活时间 

4 

DisableTime 

OUT 

字符串 

# 解除激活时间 

5 

SecondCert 

OUT 字节数组 系统二级证书 

6 

SecondCertLen OUT 长整型 系统二级证书长度 

7 

EncryptCert 

OUT 字节数组 系统加密证书 

8 

EncryptCertLen 

OUT 

长整型 

# 系统加密证书长度 

9 

SignCert 

OUT 

字节数组 

系统签名证书 

10 

SignCertLen 

OUT 

长整型 

系统签名证书长度 返回值 

0 表示成功;非 0 表示失败。 

y.y.y.5 获取 SAM 模块授权申请信息 函数名称 

获取 SAM 模块授权申请信息 

函数声明 

long MIdSamAuthRequest(unsigned char *RequestData56); 

功能描述 

获取公安部 SAM 微模块授权申请信息。调用申请授权接口前,必须保 证 SAM 模块已经被激活。 

参数说明 

序号 参数 

输入 / 输出 

类型 含义 

1 RequestData56 

OUT 

字节数组 长度为 56 字节的授权申请信息 返回值 

0 表示成功;非 0 表示失败。 y.y.y.6 SAM 模块授权确认 函数名称 

SAM 模块授权确认 函数声明 

long MIdSamAuthConfirm(unsigned char *ConfirmData89); 

功能描述 

对公安部 SAM 微模块进行授权。调用授权确认接口前,必须先调用申 请授权接口。 参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 ConfirmData89 

IN 

字节数组 

长度为 89 字节的授权确认信息 

返回值 

0 表示成功;非 0 表示失败。 

y.y.y.7 核验身份证 

函数名称 

核验身份证 

函数声明 

long MIdReadChkData(unsigned char *Random16, unsigned char *RemainAuthNum, char *SamId22, unsigned char 

*BeginAndValidTerm32, unsigned char *ShortCode16, unsigned char *CheckData, long *CheckDataLen, unsigned char *Sign64); 

# 功能描述 

核验身份证返回短识别码( 16 字节)和核验信息等数据。调用核验身 份证接口前,必须先调用寻卡选卡,即 IdFindCard 、 IdSelectCard 。 当需要将微模块核验身份后返回的数据上报后台时,需要将本函数接 口的输出数据进行如下方式拼接(将下述变量中有效数据按照顺序拷 贝到同一个存储空间中),形成如下带签名的上报数据: 

SamId22||Random16||BeginAndValidTerm32||ShortCode16|| CheckDataLenH||CheckDataLenL||CheckData||Sign64 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

Random16 

IN 

字节数组 

16 字节的随机数 

2 

RemainAuthNum 

OUT 

长整型 

剩余授权调用次数 

在激活状态下,为 0xFF, 表示剩余授权次数大于或等于 0xFF ,其他值 为剩余授权次数;未激活状态下,为 0x00 

3 

SamId22 

OUT 

字符串 

SAM 模块号 

4 

BeginAndValidTerm32 

OUT 

字节数组 

长度 32 字节的身份证有效期 

UTF16_LE 编码,前 16 字节为有效期起始,后 16 字节为有效期截止 

5 

ShortCode16 

OUT 

字节数组 

16 字节的短识别码 

6 

CheckData 

OUT 

字节数组 核验信息 

7 

CheckDataLen 

OUT 

# 长整型 

# 核验信息长度 

CheckDataLenH 代表高字节、 CheckDataLenL 代表低字节。 

8 

Sign64 

OUT 

# 字节数组 

# 64 字节的签名数据 

对如下数据( SamId22 、 Random16 、 BeginAndValidTerm32 、 ShortCode16 、 CheckDataLenH 、 CheckDataLenL 、 CheckData )按 顺序拼接后的签名值 

# 返回值 

0 表示成功;非 0 表示失败。 

# y.y.y.8 核验身份证并返回照片和指纹 

# 函数名称 

# 核验身份证并返回照片和指纹 

# 函数声明 

long MIdReadChkDataPF(unsigned char *Random16, unsigned char *RemainAuthNum, char *SamId22, unsigned char 

*BeginAndValidTerm32, unsigned char *ShortCode16, unsigned char *CheckData, long *CheckDataLen,unsigned char *Hash32, unsigned char *Sign64, unsigned char *PH, long *PHLen, unsigned char *FP, long *FPLen); 

# 功能描述 

核验身份证返回短识别码、核验信息及相片、指纹信息等。调用核验 身份证接口前,必须先调用寻卡选卡,即 IdFindCard 、 IdSelectCard 。当需要将微模块核验身份后返回的数据上报后台时, 需要将本函数接口的输出数据进行如下方式拼接(将下述变量中有效 数据按照顺序拷贝到同一个存储空间中),形成如下带签名的上报数 据: 

SamId22||Random16||BeginAndValidTerm32||ShortCode16|| CheckDataLenH||CheckDataLenL||CheckData||Hash32||Sign64 

参数说明 

序号 参数 

输入 / 输出 

类型 含义 

1 

Random16 

IN 

字节数组 

16 字节的随机数 

2 

RemainAuthNum 

OUT 

长整型 

# 剩余授权调用次数 

在激活状态下,为 0xFF, 表示剩余授权次数大于或等于 0xFF ,其他值 为剩余授权次数;未激活状态下,为 0x00 

3 

SamId22 

OUT 

字符串 

SAM 模块号 

4 

BeginAndValidTerm32 

OUT 

字节数组 

长度 32 字节的身份证有效期 

UTF16_LE 编码,前 16 字节为有效期起始,后 16 字节为有效期截止 

5 

ShortCode16 

OUT 

字节数组 

16 字节的短识别码 

6 

CheckData 

# OUT 

字节数组 

核验信息 

7 

CheckDataLen 

OUT 

长整型 

核验信息长度 

CheckDataLenH 代表高字节、 CheckDataLenL 代表低字节。 

7 

Hash32 

OUT 

# 字节数组 

Random 及人像指纹信息的 Hash 值 

8 

Sign64 

OUT 

字节数组 

64 字节的签名数据 

对如下数据( SamId22 、 Random16 、 BeginAndValidTerm32 、 ShortCode16 、 CheckDataLenH 、 CheckDataLenL 、 CheckData 、 Hash32 )按顺序拼接后的签名值 

9 PH OUT 字节数组 wlt 照片数据 10 PHLen OUT 长整型 wlt 照片数据长度 11 FP OUT 字节数组 指纹数据 12 FPLen OUT 长整型 指纹数据长度 

返回值 

# 0 表示成功;非 0 表示失败。 

# y.y.y.9 核验身份证比对识别码 

# 函数名称 

# 核验身份证比对识别码 

# 函数声明 

long MIdCheckShortLongCode(unsigned char *Random16, unsigned char ShortCodeCount, unsigned char *ShortCode, unsigned char LongCodeCount, unsigned char *LongCode, unsigned char 

*RemainAuthNum, char *SamId22, unsigned char 

*BeginAndValidTerm32, unsigned char *MatchCode, unsigned char 

*MatchCodeLen, unsigned char *CheckData, long *CheckDataLen, unsigned char *Sign64); 

# 功能描述 

核验身份证比对识别码,返回核验信息。调用核验身份证接口前,必 须先调用寻卡选卡,即 IdFindCard 、 IdSelectCard 。当需要将微模块 核验身份后返回的数据上报后台时,需要将本函数接口的输出数据进 行如下方式拼接(将下述变量中有效数据按照顺序拷贝到同一个存储 空间中),形成如下带签名的上报数据: 

SamId22||Random16||BeginAndValidTerm32||MatchCodeLen|| MatchCode||CheckDataLenH||CheckDataLenL||CheckData||Sign64 

# 参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

Random16 

IN 

字节数组 16 字节的随机数 

2 

ShortCodeCount 

IN 

字节 

短识别码的数量 

3 

ShortCode 

IN 

# 字节数组 

单组或多组短识别码数据 

16* ShortCodeCount 字节 

4 

LongCodeCount 

IN 

字节 

长识别码的数量 

5 

LongCode 

IN 

字节数组 

单组或多组长识别码数据 

64* LongCodeCount 字节 

6 

RemainAuthNum 

OUT 

长整型 

剩余授权调用次数 

在激活状态下,为 0xFF, 表示剩余授权次数大于或等于 0xFF ,其他值 为剩余授权次数;未激活状态下,为 0x00 

7 

SamId22 

OUT 

字符串 

SAM 模块号 

8 

BeginAndValidTerm32 

OUT 

# 字节数组 

长度 32 字节的身份证有效期 

UTF16_LE 编码,前 16 字节为有效期起始,后 16 字节为有效期截止 

9 

MatchCode 

OUT 

字节数组 匹配到的识别码 

10 

MatchCodeLen 

OUT 

字节 匹配到的识别码长度 

11 

CheckData 

OUT 

字节数组 核验信息 

12 

CheckDataLen 

OUT 

# 长整型 

# 核验信息长度 

CheckDataLenH 代表高字节、 CheckDataLenL 代表低字节。 

13 

Sign64 

OUT 

# 字节数组 

# 64 字节的签名数据 

对如下数据( SamId22 、 Random16 、 BeginAndValidTerm32 、 MatchCodeLen 、 MatchCode 、 CheckDataLenH 、 CheckDataLenL 、 CheckData )按顺序拼接后的签名值 

# 返回值 

0 表示成功;非 0 表示失败。 

# y.y.y.10 核验身份证比对识别码并返回照片和指纹 

# 函数名称 

# 核验身份证比对识别码并返回照片和指纹 

# 函数声明 

long MIdCheckShortLongCodePF(unsigned char *Random16, unsigned char ShortCodeCount, unsigned char *ShortCode, unsigned char LongCodeCount, unsigned char *LongCode, unsigned char *RemainAuthNum, char *SamId22,unsigned char 

*BeginAndValidTerm32, unsigned char *MatchCode, unsigned char 

*MatchCodeLen, unsigned char *CheckData, long *CheckDataLen, unsigned char *Hash32, unsigned char *Sign64, unsigned char *PH, long *PHLen, unsigned char *FP, long *FPLen); 

# 功能描述 

核验身份证比对识别码,返回核验信息、相片信息和指纹信息。调用 核验身份证接口前,必须先调用寻卡选卡,即 IdFindCard 、 IdSelectCard 。当需要将微模块核验身份后返回的数据上报后台时, 需要将本函数接口的输出数据进行如下方式拼接(将下述变量中有效 数据按照顺序拷贝到同一个存储空间中),形成如下带签名的上报数 据: 

SamId22||Random16||BeginAndValidTerm32||MatchCodeLen|| MatchCode||CheckDataLenH||CheckDataLenL||CheckData|| Hash32||Sign64 

参数说明 

序号 

参数 

输入 / 输出 

类型 

含义 

1 

Random16 

IN 

字节数组 

16 字节的随机数 

2 

ShortCodeCount 

IN 

字节 

短识别码的数量 

3 

ShortCode 

IN 

字节数组 单组或多组短识别码数据 16* ShortCodeCount 字节 

4 

LongCodeCount 

IN 

字节 

长识别码的数量 

5 

LongCode 

IN 

字节数组 

单组或多组长识别码数据 

64* LongCodeCount 字节 

6 

RemainAuthNum 

OUT 

长整型 

剩余授权调用次数 

在激活状态下,为 0xFF, 表示剩余授权次数大于或等于 0xFF ,其他值 为剩余授权次数;未激活状态下,为 0x00 

7 

SamId22 

OUT 

字符串 

SAM 模块号 

8 

BeginAndValidTerm32 

OUT 

字节数组 

长度 32 字节的身份证有效期 

UTF16_LE 编码,前 16 字节为有效期起始,后 16 字节为有效期截止 

9 

MatchCode 

OUT 

字节数组 

# 匹配到的识别码 

10 

MatchCodeLen 

OUT 

字节 匹配到的识别码长度 

11 

CheckData 

OUT 

字节数组 核验信息 

12 

CheckDataLen 

OUT 

长整型 核验信息长度 

CheckDataLenH 代表高字节、 CheckDataLenL 代表低字节。 

13 

Hash32 

OUT 

# 字节数组 

Random 及人像指纹信息的 Hash 值 

14 

Sign64 

OUT 

字节数组 

64 字节的签名数据 

对如下数据( SamId22 、 Random16 、 BeginAndValidTerm32 、 MatchCodeLen 、 MatchCode 、 CheckDataLenH 、 CheckDataLenL 、 CheckData 、 Hash32 )按顺序拼接后的签名值 

15 

PH 

OUT 

字节数组 

wlt 照片数据 

16 

PHLen 

OUT 

长整型 

wlt 照片数据长度 

17 

FP 

OUT 

字节数组 

指纹数据 

18 

FPLen 

OUT 

长整型 

指纹数据长度 

返回值 

0 表示成功;非 0 表示失败。 

y.y.y.11 核验性别或出生日期 

函数名称 

核验性别或出生日期 

# 函数声明 

long MIdCheckProperty(unsigned char *Random16, unsigned char PropertyCode, unsigned char PropertyValLen, unsigned char *PropertyVal, unsigned char *RemainAuthNum, char *SamId22, unsigned char *CheckResult, unsigned char *CheckData, long *CheckDataLen, unsigned char *Sign64); 

# 功能描述 

核验身份证性别或出生日期。调用核验身份证接口前,必须先调用寻 卡选卡,即 IdFindCard 、 IdSelectCard 。当需要将微模块核验身份后 返回的数据上报后台时,需要将本函数接口的输出数据进行如下方式 拼接(将下述变量中有效数据按照顺序拷贝到同一个存储空间中), 

# 形成如下带签名的上报数据: 

SamId22||Random16||PropertyCode||PropertyVal||CheckResult|| CheckDataLenH||CheckDataLenL||CheckData||Sign64 

参数说明 

序号 参数 

输入 / 输出 

类型 含义 

1 

Random16 

IN 

字节数组 

16 字节的随机数 

PropertyCode 

IN 

字节 核验属性代码 

0x02 :核验性别代码 0x04 :核验出生日期 

PropertyValLen 

IN 

字节 

属性长度 

PropertyVal 

IN 

字节数组 

属性值 

UTF16_LE 编码 

2 

RemainAuthNum 

OUT 

长整型 

剩余授权调用次数 

在激活状态下,为 0xFF, 表示剩余授权次数大于或等于 0xFF ,其他值 为剩余授权次数;未激活状态下,为 0x00 

3 

SamId22 

OUT 

字符串 

SAM 模块号 

4 

# CheckResult 

OUT 

字节 

核验结果 

性别核验结果: 

0x00 :性别一致 

0x01 :性别不一致 出生日期核验结果: 

0x90 :出生日期一致 

0xA0 :身份证读取的出生日期比输入的出生日期晚 

0x80 :身份证读取的出生日期比输入的出生日期早 

6 

# CheckData 

# OUT 

字节数组 

核验信息 

7 

CheckDataLen 

OUT 

长整型 

# 核验信息长度 

CheckDataLenH 代表高字节、 CheckDataLenL 代表低字节。 

8 

Sign64 

OUT 

字节数组 

64 字节的签名数据 

对如下数据( SamId22 、 Random16 、 PropertyCode 、 PropertyVal 、 CheckResult 、 CheckDataLenH 、 CheckDataLenL 、 CheckData )按 顺序拼接后的签名值 

返回值 

0 表示成功;非 0 表示失败。 

y.y.y.12 LED 氛围灯控制 

函数名称 

LED 氛围灯控制 

# 函数声明 

long LedOnOff(unsigned char LedNo, unsigned char OnOff); 

功能描述 

控制 LED 氛围灯亮灭。 

参数说明 

序号 

参数 

# 输入 / 输出 

类型 含义 1 LedNo IN 字节 氛围灯颜色 0x00 :绿色 0x01 :红色 0x02 :黄色 2 OnOff IN 字节 氛围灯状态 0x00 :绿色 0x01 :红色 返回值 0 表示成功;非 0 表示失败。 2.4 调用流程 

# 接口的调用流程如下图所示: 

# 附录 

附录 A 常用语言开发调用指南 

A1 、动态库及函数加载 

加载 

语言 

静态加载方式 

C/C++ 

#include “CommonInterface.h” 

#pragma comment(lib, “CommonInterface.lib”) 

C# 

using System.Runtime.InteropServices; 

[DllImport("CommonInterface.dll")] 

public static extern int OpenDevice(string PortType, string PortPara, string ExtendPara); 

Java ( JNA ) 

import com.sun.jna.Native; 

import com.sun.jna.win32.StdCallLibrary; 

public class JnaTest { 

public interface CommonInterface extends StdCallLibrary { 

CommonInterface instance = (CommonInterface) Native.loadLibrary("CommonInterface", CommonInterface.class); 

int OpenDevice(String PortType, String PortPara, String ExtendPara); 

} 

} 

Delphi 

implementation 

{$R *.dfm} 

function OpenDevice(PortType:AnsiString; PortPara:AnsiString; ExtendPara:AnsiString): LongInt;stdcall; 

far;external 'CommonInterface.dll' name 'OpenDevice' 

VB 

Private Declare Function OpenDevice Lib " CommonInterface.dll" Alias "OpenDevice" (ByVal PortType As String, ByVal PortPara As String, ByVal ExtendPara As String) As Long 

PB 

public function long OpenDevice(string PortType, string PortPara, string ExtendPara) library "CommonInterface.dll" alias for "OpenDevice" 

注:上述表格中列出的加载方式均为静态加载,另各语言也均可使用 动态加载 LoadLibrary 的方式加载动态库及函数,具体使用方法请参见 Windows API 。 

A2 、数据类型对应关系 

语言 

类型 

入参 

# 出参 

C/C++ C# Java ( JNA ) Delphi VB PB8/PB11 整型 IN OUT int int* int ref int int int[] Integer PInteger Long ByRef As Long long 

ref long 

# 长整型 

IN OUT long long* int ref int int int[] LongInt PLongInt Long ByRef As Long long ref long 字符串 IN OUT char* char* string 

StringBuilder 

String 

byte[] 

AnsiString 

PAnsiChar 

ByVal As String ByVal As String string ref string 字节数组 

IN/OUT unsigned char* 

byte[] 

byte[] PByteArray ByRef As Byte ref char[]/ ref byte[] 字符 

IN char 

char 

char 

# AnsiChar 

ByVal As Byte 

char 

字节 

IN 

unsigned char 

byte 

byte 

Byte 

ByVal As Byte 

char/byte 

注:在本文档中,一般 char* 为可见字符串,即可用键盘敲出的字 符; unsigned char* 为字节数组(不可见的字节数据),一般会有一 个与之对应的长度参数,来指示有效数据的实际长度。 

A3 、内存分配及调用方式 

内存 

语言 

需要分配内存的类型 

内存分配方式 

调用 

C/C++ 

char* 

unsigned char* 

char test[1024] = {0};// 或者用 malloc/free 、 new/delete 

unsigned char test[1024] = {0};// 或者用 malloc/free 、 new/delete 

Func(test) 

Func(test) 

C# 

StringBuilder byte[] 

StringBuilder test = new StringBuilder(1024); 

byte[] test = new byte[1024]; 

Func(test) 

Func(test) 

Java ( JNA ) 

int [] 

byte[] 

int[] test = new int[2]; 

byte[] test = new byte[1024]; 

Func(test) 

Func(test) 

Delphi 

PAnsiChar 

PByteArray 

test:PAnsiChar; test := AllocMem(1024); 

test:array[0..1024] of byte 

Func(test) 

Func(@test) 

VB 

String 

ByRef As Byte 

Dim test As String; test = String$(1024, Chr$(0)) 

Dim test(1024) As Byte 

Func(test) 

Func(test(0)) 

PB 

string 

ref char[] 

ref byte[] 

string test; test = space(1024) ,最好初始化为 0 

char test[] = space(1024) ,最好初始化为 0 

PB11 引入的新类型,不太了解如何分配, byte test[] = {0,0,0,0,0,0} Func(test) 

Func(ref test) 

Func(ref test) 

附录 B 神思 USB 读卡器 VID_PID 对照表 

读卡器型号 

PortType PortPara ( VID_PID ) 

ExtendPara 

SS628100U 

USB 

0400C35A 

SS628100H 

USB 

261A0007 

SS728M-05 

USB 

261A000C 

MC 

SS628100X1 

USB 

261A0011 

SS728M-801 

USB 261A0012 

SS628100Wm 

USB 

261A001C 

# 附录 C 接口兼容不同协议设备的使用方法 

【方案一】(适用于 Windows 、 Linux 、 Android ) 

long SetAutoPara(char *PortType, char *PortPara, char 

*ExtendPara, char *DllName = (char*)"TerminalProtocol.dll", int UsingGA467 = 0); 

步骤 1 、将需要兼容的设备协议层接口库 TerminalProtocol.dll 拷贝到 CommonInterface.dll 所在的目录并重命名增加设备名称后缀,例如 TerminalProtocol100X1.dll 、 TerminalProtocolM05.dll 等。 

步骤 2 、在程序初始化时,调用 SetAutoPara 接口,将所要兼容的设备 信息全部设置一遍,示例: 

SetAutoPara(“USB”, “261A0011”, “”, “TerminalProtocol100X1.dll”, 0); 

SetAutoPara(“USB”, “261A000C”, “MC”, “TerminalProtocolM05.dll”, 0); 

步骤 3 、在调用打开设备 OpenDevice 函数时,设备端口类型传 入 “AUTO” 或 “auto” ,其余两个参数传空字符串即可。此时接口库会 根据 SetAutoPara 所配置的参数,逐个尝试打开设备,直到成功为 止。 

OpenDevice (“AUTO”, “”, “”); 

【方案二】(仅在 Windows 、 Linux 下支持) 

步骤 1 、将需要兼容的设备协议层接口库 TerminalProtocol.dll 拷贝到 CommonInterface.dll 所在的目录并重命名增加设备名称后缀,例如 TerminalProtocol100X1.dll 、 TerminalProtocolM05.dll 等。 

# 步骤 2 、在 CommonInterface.dll 所在的目录建立配置文件: CommonInterface.ini ,配置文件内容示例: 

[Device1] 

DllName = TerminalProtocol100X1.dll 

PortType = USB 

PortPara = 261A0011 

[Device2] 

DllName = TerminalProtocol100X1.dll 

PortType = USB 

PortPara = 0400C35A 

GA467 = 1 

[Device3] 

DllName = TerminalProtocolM05.dll 

PortType = USB 

PortPara = 261A000C 

ExtendPara = MC 

...... 可依次增加 [DeviceN] 节点,从而兼容 N 种设备。 

步骤 3 、在调用打开设备 OpenDevice 函数时,设备端口类型传 入 “AUTO” 或 “auto” ,其余两个参数传空字符串即可。此时接口库会 根据配置文件中配置的参数,逐个尝试打开设备,直到成功为止。 

OpenDevice (“AUTO”, “”, “”); 

注:默认 01SDK 文件夹下已完成步骤 1 、步骤 2 的操作,可选择性忽 

略,直接进入步骤 3. 

【方案三】(适用于 Windows 、 Linux 、 Android ) 

方法:在读卡器改变时,调用 SetTerminalLibrary 接口,设置协议层 接口库。 

long SetTerminalLibrary(char *LibraryFileName);// LibraryFileName 为协议层接口库文件名或全路径文件名 

# 示例: 

SetTerminalLibrary(“TerminalProtocolM05.dll”);// 设置协议层接口 库为 M05 协议层接口库 

OpenDevice(“USB”, “261A000C”, “MC”);// 连接 SS728M-05 读卡器 

// 进行读卡操作 

CloseDevice(); 

OpenDevice(“USB”, “261A000C”, “MC”);// 读卡器不变,无需再次 SetTerminalLibrary 

// 进行读卡操作 

CloseDevice(); 

SetTerminalLibrary(“TerminalProtocol100X1.dll”);// 设置协议层接 口库为 100X1 协议层接口库 

OpenDevice(“USB”, “261A0011”, “”);// 读卡器变为 100X1 ,所以在 此之前需要 SetTerminalLibrary 

// 进行读卡操作 

CloseDevice(); 

附录 D 接口兼容其他密码键盘的方法 

在跨省社保接口 SSCardDriver.dll 中, PIN 相关的函数内部会自动驱动 密码键盘输入密码,若要兼容其他型号的密码键盘,在 dll ( so )同目 录放上 

TerminalProtocolKeyboard.dll ( libTerminalProtocolKeyboard.so ) 动态库即可,动态库要求如下: 

- 1 、动态库名称: 

TerminalProtocolKeyboard.dll ( libTerminalProtocolKeyboard.so ) 

2 、函数名称: long __stdcall KeybordGetInputPassword(unsigned char VoiceCode, char *Password, unsigned char TimeOutSec); 

3 、参数说明: 

VoiceCode :入参,播放声音 

//1-“ 请输入密码 ” , 

//2-“ 请输入旧密码 ” , 

//3-“ 请输入新密码 ” , 

//4-“ 请再次输入新密码 ” 

Password :出参,返回输入的密码 

TimeOutSec :入参,输入超时时间,单位秒
