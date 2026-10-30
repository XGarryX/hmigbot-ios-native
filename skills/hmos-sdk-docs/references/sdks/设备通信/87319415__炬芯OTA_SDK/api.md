# **actionsibluz** 接口文档 

来源: actionsibluz/API.md (自动整理生成) 

生成日期: 2026-05-06 

## **1.** 模块概述 

actionsibluz 模块主要提供基于 BLE (低功耗蓝牙)和 SPP (传统蓝 牙串口)协议的 OTA (空中固件升级)能力。模块封装了复杂的底层 蓝牙通信协议、文件分包传输逻辑以及升级状态流转控制。 

## **2.** 核心类: **OtaManager** 

OtaManager 是管理 OTA 升级流程的核心控制类,提供初始化、状态 监听、启动升级以及停止等能力。 

### **2.1** 方法一览 

方法 

说明 

参数 / 返回 

setOtaListener(...) 

设置 OTA 流程中的各个事件回调监听器。 

#### 参数: 

onStatus(state: OtaStatus) 

onAudioDataReceived(psn, len, data) 

onRemoteStatusReceived(status: RemoteStatus) 

onProgress(progress, total) 

onError(errCode, errMsg) 

onWriteBytes(count) 

返回: void 

prepare(isBle, buf, filePath, clientNumber?, client?) 

初始化 OTA 升级环境,解析文件头并向远端设备发送握手 / 准备命 令。 参数: 

isBle: boolean ( true=BLE , false=SPP ) 

buf: ArrayBuffer (固件头部缓存) 

filePath: fileUri.FileUri (固件路径 URI ) 

clientNumber?: number ( SPP 专用) 

client?: ble.GattClientDevice ( BLE 专用) 

返回: void 

upgrade(filePath) 

远端准备就绪( STATE_PREPARED )后,开始读取文件并下发固件数 据。 参数: 

filePath: fileUri.FileUri 

返回: void 

stopManager(isBle) 

停止当前 OTA 管理器,注销对应蓝牙模式下的监听 / 回调。 参数: 

isBle: boolean 

返回: void 

getOTAVersion(bufs) 

从文件头 Buffer 中解析 OTA 固件包版本号信息。 参数: 

bufs: ArrayBuffer 

返回: string (版本号) 

### **2.2** 方法签名(原始定义) 

setOtaListener( 

onStatus: (state: OtaStatus) => void, 

onAudioDataReceived: (psn: number, len: number, data: Uint8Array) => void, 

onRemoteStatusReceived: (status: RemoteStatus) => void, 

onProgress: (progress: number, total: number) => void, onError: (errCode: number, errMsg: string) => void, onWriteBytes: (count: number) => void 

): void 

prepare( 

isBle: boolean, 

buf: ArrayBuffer, filePath: fileUri.FileUri, clientNumber?: number, client?: ble.GattClientDevice 

): void upgrade(filePath: fileUri.FileUri): void stopManager(isBle: boolean): void getOTAVersion(bufs: ArrayBuffer): string 

## **3.** 数据结构与枚举 

### **3.1 OtaStatus** 枚举: 

枚举值 说明 STATE_UNKNOWN 未知状态 STATE_IDLE 空闲状态 

STATE_PREPARING 

准备中(解析文件、下发握手等) 

STATE_PREPARED 

准备就绪(远端确认可升级) 

STATE_TRANSFERRING 

固件文件传输中 

STATE_TRANSFERRED 

固件传输完成 

### **3.2 RemoteStatus** 实体: 

远端设备的当前状态信息,主要在握手通信过程中接收。 属性名 

类型 说明 

versionName 

string 

远端设备当前固件版本名称 

boardName 

string 

主板名称 

hardwareRev 

string 

#### 硬件版本修订号 

batteryThreshold 

number 

电量阈值(限制升级最低电量等) 

versionCode 

number 

远端设备当前固件版本号 

featureSupport 

number 

远端设备支持的特性掩码(如 CRC 支持位等) 

### **3.3 ErrorCode** 常量: 

OTA 过程中的错误码及默认错误信息定义: 常量名 

错误码值 

含义说明 

OK 

-1 

成功 

PACKAGE_INVALID 

1 

固件包无效 

IO_EX 

2 

IO 读写异常 

SPP_CONNECT_ERROR 

3 

SPP 蓝牙连接错误 

BLE_OTA_SEND_MSG_ERROR 

4 

BLE 消息发送失败 

OTA_TIMEOUT 

5 

OTA 交互握手 / 传输超时 

默认提供的静态提示字符串: 

MESSAGE_UNKNOWN: 'unknown error' 

MESSAGE_PACKAGE_INVALID: 'OTA package invalid, exit ota mode.' 

MESSAGE_BLE_ERROR: 'BLE SEND ERROR!' 

MESSAGE_TIMEOUT: 'OTA time out' 

## **4.** 蓝牙协议栈设计 

协议栈涵盖底层通信方式、数据包组装结构( TLV 格式)、交互指令 流以及断点续传设计。 

### **4.1** 蓝牙基础配置 

协议栈同时支持 BLE 与 SPP ,相关 UUID 默认定义如下: 

SPP UUID : 00006666-0000-1000-8000-00805F9B34FB 

BLE Service UUID : e49a25f8-f69a-11e8-8eb2-f2801f1b9fd1 

BLE Write 特征值: e49a25e0-f69a-11e8-8eb2-f2801f1b9fd1 (支持 WRITE_NO_RESPONSE ) 

BLE Read/Notify 特征值: e49a28e1-f69a-11e8-8eb2-f2801f1b9fd1 

CCCD (配置描述符): 00002902-0000-1000-8000-00805f9b34fb 

### **4.2 TLV** 数据包与 封装结构 

消息结构采用 ServiceID + CommandID + TLVs 格式,附加参数均 使用 TLV ( Type-Length-Value )封装。 基础 TLV 结构: 

Type (1B) :标识参数类型 

Length (2B) :小端序,表示 Value 字节长度 

Value (nB) :实际数据内容 

指令组装结构: 

第 1 字节: ServiceID ( OTA 固定 0x09 ) 

第 2 字节: CommandID ( 0x01~0x07 等) 

第 3 字节起: SuperTLV ( Type=0x80 ),其内部包含一个或多个子 SubTLVs 。 

### **4.3 Command IDs** 核心指令交互流程( ) 

OTA 状态机由远端设备与手机端的 0x09 Service 命令交互来驱动。 

握手与准备阶段( STATE_PREPARING ): 

获取设备参数( Tx ): 0x09 0x02 

设备状态上报( Rx ): 0x09 0x01 

就绪通知( Tx ): 0x09 0x09 

设备 OTA 参数协商( Rx ): 0x09 0x02 

数据传输阶段( STATE_TRANSFERRING ): 

数据请求( Rx ): 0x09 0x03 (携带 offset/length/bitmap ,用于断 点续传) 

发送数据分片( Tx ): 0x09 0x04 或 0x09 0x0B 

不支持 CRC (0x09 0x04): 0x09 0x04 0x80 Len(2B) Seq(1B) [Data...] 

支持 CRC32 (0x09 0x0B): 0x09 0x0B 0x80 Len(2B) Seq(1B) CRC32(4B) [Data...] 

进度与 ACK 确认( Rx ): 0x09 0x05 

结束阶段( STATE_TRANSFERRED ): 

包校验结果( Rx ): 0x09 0x06 ( valid=1 通过; valid=0 抛出 PACKAGE_INVALID ) 

异常处理: 

错误上报( Rx ): 0x09 0x07 (例如 110000 表示 bin 文件错误) 握手超时控制: 20 秒超时,超时触发 OTA_TIMEOUT 并中断流程。
