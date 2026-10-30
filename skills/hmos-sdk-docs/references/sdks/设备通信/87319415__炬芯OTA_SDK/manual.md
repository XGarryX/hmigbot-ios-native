# **Actionsibluz SDK** 使用指南 

actionsibluz 是一款专为 HarmonyOS (鸿蒙)应用开发的蓝牙设备 OTA ( Over-The-Air )空中升级库,支持 BLE (低功耗蓝牙)和 SPP (传统蓝牙串口)两种通信模式。本指南将帮助您快速集成并使 用该 SDK 实现蓝牙固件升级功能。 

## **1.** 项目简介 

actionsibluz SDK 封装了复杂的底层蓝牙通信协议、文件分包传输逻 辑以及升级状态流转控制,开发者只需关注业务层面的调用,无需深 入了解蓝牙协议细节。 SDK 的核心功能包括:设备连接管理、 OTA 握手与协商、固件分包传输、传输进度监控、断点续传支持以及 CRC 校验。 

该 SDK 的主要特性涵盖双向支持,既支持 BLE 低功耗蓝牙也支持 SPP 经典蓝牙;自动分包机制能够根据设备能力自动调整分包大小; 智能断点续传在传输中断后可从断点继续;实时进度反馈提供百分比 和字节数的精确进度;版本校验确保固件与设备兼容性;超时控制内 置 20 秒握手超时保护。 

## **2.** 安装与配置 

### **2.1 SDK** 安装 

您可以通过 ohpm 包管理器安装 actionsibluz SDK 。在项目根目录执 行以下命令: 

```
ohpm install @actions/actionsibluz
```

安装完成后, SDK 会自动添加到项目的依赖配置中。您也可以选择本 地源码引用方式,将 actionsibluz 模块目录放在项目同级的 ../ actionsibluz 路径,然后在 entry/oh-package.json5 中添加依赖配 置: 

```
{
  "dependencies": {
    "@actions/actionsibluz": "file:../actionsibluz"
  }
}
```

### **2.2** 权限申请 

#### 在使用蓝牙功能之前,必须在 module.json5 中声明所需的蓝牙权 限。以下是完整的权限列表: 

```
{
  "module": {
    "requestPermissions": [
      {
        "name": "ohos.permission.DISCOVER_BLUETOOTH",
        "reason": "$string:discover_bluetooth_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"
        }
      },
      {
        "name": "ohos.permission.USE_BLUETOOTH",
        "reason": "$string:use_bluetooth_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"
        }
      },
      {
        "name": "ohos.permission.ACCESS_BLUETOOTH",
        "reason": "$string:access_bluetooth_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"
        }
      },
      {
        "name": "ohos.permission.LOCATION",
        "reason": "$string:location_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"
        }
      },
      {
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"
        }
      }
    ]
  }
}
```

#### 除了在配置文件中声明权限外,应用还需要在运行时动态请求用户授 权。以下是完整的权限请求代码: 

```
const permissions: Array<Permissions> = [
  'ohos.permission.DISCOVER_BLUETOOTH',
  'ohos.permission.USE_BLUETOOTH',
  'ohos.permission.ACCESS_BLUETOOTH',
  'ohos.permission.LOCATION',
  'ohos.permission.APPROXIMATELY_LOCATION'
];
function requestBluetoothPermissions(): void {
  let atManager = abilityAccessCtrl.createAtManager();
    if (err) {
```

`console.error('` 权限请求失败 `:', err.message);` 

`} else { console.info('` 权限请求成功 `'); }` 

```
  });
}
```

## **3. API** 核心 详解 

### **3.1 OtaManager** 类 

OtaManager 是 SDK 的核心类,负责管理整个 OTA 升级流程的生命 周期。以下是该类的主要方法: 

设置监听器 setOtaListener 方法用于注册 OTA 过程中的各类事件回 调,这些回调会实时通知您状态变更、进度更新和错误信息: 

```
setOtaListener(
  onStatus: (state: OtaStatus) => void,
  onError: (errCode: number, errMsg: string) => void,
  onWriteBytes: (count: number) => void
): void
```

参数说明如下: onStatus 是状态变更回调,当 OTA 状态发生变化时 触发,用于更新 UI 显示; onAudioDataReceived 是音频数据回调, 

用于接收远端设备发送的音频数据; onRemoteStatusReceived 是设 备状态回调,返回远端设备的固件版本、电量、主板信息等; onProgress 是进度回调,参数 progress 表示已传输字节数, total 表 示总字节数; onError 是错误回调, errCode 为错误码, errMsg 为错 误描述; onWriteBytes 是写入字节统计回调。 

准备 OTA 环境 prepare 方法初始化 OTA 升级环境,解析固件文件头 部并与远端设备完成握手: 

```
prepare(
  isBle: boolean,
  buf: ArrayBuffer,
  filePath: fileUri.FileUri,
  clientNumber?: number,
  client?: ble.GattClientDevice
): void
```

参数 isBle 标识当前蓝牙模式, true 表示 BLE 模式, false 表示 SPP 模式; buf 是 OTA 文件头部的数据缓存区,用于版本校验; filePath 是固件文件的 URI 路径; clientNumber 是 SPP 模式下的 socket 连接 标识; client 是 BLE 模式下的 GattClientDevice 实例。 

启动固件传输 upgrade 方法在设备准备就绪后开始正式传输固件数 据: 

```
upgrade(filePath: fileUri.FileUri): void
```

停止 OTA stopManager 方法停止当前的 OTA 流程,清理蓝牙监听事 件: 

```
stopManager(isBle: boolean): void
```

#### 获取固件版本 getOTAVersion 方法从文件头解析出固件版本号: 

```
getOTAVersion(bufs: ArrayBuffer): string
```

### **3.2** 枚举与数据结构 

#### OtaStatus 枚举定义了 OTA 升级的完整状态流转过程: 

`enum OtaStatus { STATE_UNKNOWN,      //` 未知状态 `STATE_IDLE,         //` 空闲状态 `STATE_PREPARING,    //` 准备中(解析文件、握手) `STATE_PREPARED,     //` 准备就绪 `STATE_TRANSFERRING, //` 固件传输中 `STATE_TRANSFERRED  //` 传输完成 

```
}
```

状态流转遵循以下顺序:初始时为 STATE_IDLE ,调用 prepare() 后 进入 STATE_PREPARING ,握手成功后变为 STATE_PREPARED ,调 用 upgrade() 后进入 STATE_TRANSFERRING ,传输完成后进入 STATE_TRANSFERRED 。如果发生错误,状态可能变为 STATE_UNKNOWN 。 

#### RemoteStatus 数据结构存储远端设备的详细信息: 

`class RemoteStatus { versionName: string;     //` 固件版本名称 `boardName: string;       //` 主板名称 `hardwareRev: string;     //` 硬件版本 `batteryThreshold: number; //` 电量阈值 `versionCode: number;    //` 版本号 `featureSupport: number;  //` 特性支持掩码 

```
}
```

#### ErrorCode 错误码定义了 OTA 过程中可能出现的错误: 

`class ErrorCode { static OK = -1;                          //` 成功 `static PACKAGE_INVALID = 1;             //` 固件包无效 

`static IO_EX = 2;                       // IO` 读写异常 `static SPP_CONNECT_ERROR = 3;          // SPP` 连接错误 `static BLE_OTA_SEND_MSG_ERROR = 4;      // BLE` 发送失败 `static OTA_TIMEOUT = 5;                //` 操作超时 `}` 

## **4. BLE OTA** 完整示例 

以下是一个完整的 BLE 模式 OTA 升级示例,展示了从设备连接、固 件选择到升级完成的全部流程。 

### **4.1** 导入依赖 

```
import { ble } from '@kit.ConnectivityKit';
import picker from '@ohos.file.picker';
import { fileUri } from '@kit.CoreFileKit';
import { buffer } from '@kit.ArkTS';
```

### **4.2 OTA** 初始化 管理器 

```
private manager: OtaManager = new OtaManager();
private isBle: boolean = true;
```

`private initOtaManager(): void { this.manager.setOtaListener( //` 状态回调 `(state: OtaStatus) => {` 

`this.onOtaStatus(state); }, //` 音频数据回调 

`(psn: number, len: number, data: Uint8Array) => { this.onAudioData(psn, len, data); }, //` 远端状态回调 `(status: RemoteStatus) => { this.onRemoteStatus(status); }, //` 进度回调 `(progress: number, total: number) => { this.onProgress(progress, total); }, //` 错误回调 

`(errCode: number, errMsg: string) => { this.onError(errCode, errMsg); }, //` 写入字节回调 

```
    (count: number) => {
      this.onWriteBytes(count);
    }
  );
}
```

### **4.3 BLE** 连接 设备 

`//` 创建 `GATT` 客户端 

```
  this.client = ble.createGattClientDevice(macAddress);
```

#### `//` 监听连接状态变化 

`if (event.state === 1) { console.info('BLE` 连接中 `...'); } else if (event.state === 2) { console.info('BLE` 连接成功 `');` 

```
      this.onConnected();
```

- `} else if (event.state === 0) { console.info('BLE` 连接断开 `');` 

- `}` 

- `});` 

#### `//` 开始连接 

```
  this.client.connect();
}
async onConnected(): Promise<void> {
```

- `if (this.client) { //` 获取设备服务 

```
    let services = await this.client.getServices();
    for (let service of services) {
```

- `//` 匹配 `OTA Service UUID` 

- `let bleServiceUUID = await preferences.get(` 

- `SPKeys.SP_PATH,` 

```
        SPKeys.SP_BLE_SERVICE_UUID,
        Global.ACTIONS_BLE_SERVICE_UUID
```

- `) as string;` 

#### `//` 获取读写特征值 

```
        let writeUUID = await preferences.get(
          SPKeys.SP_PATH,
          SPKeys.SP_BLE_SERVICE_WRITE_UUID,
```

- `Global.ACTIONS_BLE_SERVICE_WRITE_UUID` 

- `) as string;` 

```
        let readUUID = await preferences.get(
          SPKeys.SP_PATH,
          SPKeys.SP_BLE_SERVICE_READ_UUID,
          Global.ACTIONS_BLE_SERVICE_READ_UUID
```

- `) as string;` 

```
        for (let char of service.characteristics) {
```

- `this.readCharacteristic = char;` 

```
            this.writeCharacteristic = char;
          }
        }
```

`//` 启用通知 

```
        }
      }
    }
  }
}
```

- `//` 配置 `CCCD` 描述符 

```
  let descriptors: Array<ble.BLEDescriptor> = [];
  let bufferDesc = new ArrayBuffer(2);
  let descV = new Uint8Array(bufferDesc);
  descV[0] = 1;
  let descriptor: ble.BLEDescriptor = {
    serviceUuid: characteristic.serviceUuid,
    descriptorValue: bufferDesc
  };
  descriptors[0] = descriptor;
  let notifyCharacteristic: ble.BLECharacteristic = {
    serviceUuid: characteristic.serviceUuid,
    characteristicValue: new ArrayBuffer(0),
    descriptors: descriptors
  };
}
```

### **4.4** 选择固件文件 

```
async selectOtaFile(): Promise<void> {
  try {
    if (result && result.length > 0) {
      let uri = result[0];
      this.selectFile = new fileUri.FileUri(uri);
```

#### `//` 缓存文件路径 

#### `//` 读取文件内容 

```
        this.arrayBuffer = arrayBuffer;
      });
    }
```

`} catch (err) { console.error('` 选择文件失败 `:', err);` 

```
  }
}
```

### **4.5 OTA** 执行 升级 

`//` 步骤 `1` :准备 `OTA` 环境 

`async prepareOta(): Promise<void> { if (!this.arrayBuffer || !this.selectFile) { console.error('` 请先选择固件文件 `'); return;` 

```
  }
```

`if (this.manager && this.client) { this.manager.prepare( this.isBle,      // true` 表示 `BLE` 模式 `this.arrayBuffer, this.selectFile, undefined,       // SPP` 专用参数 `this.client      // BLE` 专用参数 `); } }` 

#### `//` 步骤 `2` :开始固件传输 

```
async startOtaUpgrade(): Promise<void> {
  if (this.manager && this.selectFile) {
    this.manager.upgrade(this.selectFile);
  }
}
```

#### `//` 清理资源 

```
aboutToDisappear(): void {
  if (this.manager) {
    this.manager.stopManager(this.isBle);
  }
  if (this.client) {
    this.client.off('BLEConnectionStateChange');
  }
}
```

### **4.6** 处理回调 

`private onOtaStatus(state: OtaStatus): void { switch (state) { case OtaStatus.STATE_PREPARING: console.info('OTA` 准备中 `...'); break;` 

`case OtaStatus.STATE_PREPARED: console.info('` 设备准备就绪,可以开始升级 `');` 

`this.canStartUpgrade = true; break; case OtaStatus.STATE_TRANSFERRING: console.info('` 固件传输中 `...'); break; case OtaStatus.STATE_TRANSFERRED: console.info('` 固件传输完成 `!'); break; case OtaStatus.STATE_UNKNOWN: console.error('OTA` 发生错误 `'); break; } }` 

`let percent = (progress / total * 100).toFixed(1); console.info(`` 传输进度 `this.progressValue = progress / total * 100; }` 

`console.error(`OTA` 错误 `[${errCode}]: ${errMsg}`); promptAction.showToast({ message: `` 升级失败 `: ${errMsg}`, duration: 3000 }); }` 

`private onRemoteStatus(status: RemoteStatus): void { console.info('` 远端设备信息 `:'); console.info('` 版本 `:', status.versionName); console.info('` 版本号 `:', status.versionCode); console.info('` 主板 `:', status.boardName); console.info('` 硬件版本 `:', status.hardwareRev); console.info('` 电量阈值 `:', status.batteryThreshold);` 

```
  this.remoteStatus = status;
}
```

## **5. SPP OTA** 完整示例 

SPP 模式与 BLE 模式的主要区别在于连接方式和数据传输方式。以下 是 SPP 模式的关键代码: 

### **5.1 SPP** 连接 设备 

```
private clientNumber: number = -1;
private isBle: boolean = false;
```

`try { //` 获取 `SPP UUID let sppUUID = await preferences.get( SPKeys.SP_PATH, SPKeys.SP_SPP_UUID, Global.ACTIONS_SPP_UUID ) as string;` 

`//` 打开 `SPP` 客户端连接 

`//` 监听数据接收 

`console.info('` 收到 `SPP` 数据 `'); //` 数据由 `OtaManager` 处理 

```
    });
```

`} catch (err) { console.error('SPP` 连接失败 `:', err); }` 

```
}
```

### **5.2 SPP OTA** 流程 

`//` 准备 `SPP OTA async prepareSppOta(): Promise<void> { if (!this.arrayBuffer || !this.selectFile) { console.error('` 请先选择固件文件 `'); return; }` 

`if (this.manager) { this.manager.prepare( this.isBle,      // false` 表示 `SPP` 模式 `this.arrayBuffer, this.selectFile, this.clientNumber  // SPP` 连接标识 `); } }` 

`//` 断开 `SPP` 连接 `async disconnectSpp(): Promise<void> { if (this.clientNumber !== -1) { socket.sppCloseClientSocket(this.clientNumber); this.clientNumber = -1; } }` 

## **6.** 进阶功能 

### **6.1** 断点续传 

SDK 自动支持断点续传功能。当传输过程中发生中断(如蓝牙断 开),重新连接后调用 upgrade() 方法, SDK 会自动根据设备返回的 

bitmap 信息,仅传输未收到的数据包,无需重传整个固件文件。 

### **6.2 CRC** 校验 

如果远端设备支持 CRC32 校验(通过 featureSupport 掩码判断), SDK 会自动启用带 CRC 校验的数据分包传输模式,确保数据传输的 可靠性: 

`//` 设备返回的 `featureSupport` 中第 `0` 位标识 `CRC` 支持 `let crcSupport = (status.featureSupport & 0x01) === 0x01; console.info('` 远端设备 `CRC` 支持 `:', crcSupport);` 

### **6.3 UUID** 自定义 配置 

如果您的设备使用不同的 BLE Service 和 Characteristic UUID ,可以 通过 SPKeys 和 preferences 进行自定义配置: 

`//` 设置自定义 `UUID` 

`async setCustomUUIDs(): Promise<void> { //` 自定义 `SPP UUID` 

`//` 自定义 `BLE Service UUID` 

`//` 自定义 `BLE Write Characteristic UUID` 

`//` 自定义 `BLE Read Characteristic UUID` 

```
}
```

### **6.4 OTA** 单元大小配置 

#### SDK 默认使用 256 字节作为单包传输大小。您可以在传输参数协商 后获取设备指定的单元大小: 

`async getOtaUnitSize(): Promise<number> { let unitSize = await preferences.get( SPKeys.SP_PATH, SPKeys.SP_OTA_UNIT, 256  //` 默认值 

`) as number; console.info('OTA` 单元大小 `:', unitSize); return unitSize;` 

```
}
```

## **7.** 最佳实践 

### **7.1** 资源管理 

#### 始终在组件的 aboutToDisappear() 生命周期中释放蓝牙资源,避免 内存泄漏: 

`aboutToDisappear(): void { //` 停止 `OTA` 流程 

```
  if (this.manager) {
    this.manager.stopManager(this.isBle);
  }
```

#### `//` 断开蓝牙连接 

```
  if (this.isBle && this.client) {
    this.client.off('BLEConnectionStateChange');
    this.client.disconnect();
```

- `} else if (!this.isBle && this.clientNumber !== -1) {` 

```
    socket.off('sppRead', this.clientNumber);
    socket.sppCloseClientSocket(this.clientNumber);
  }
}
```

### **7.2** 错误处理 

#### 建议在 UI 层和业务层都实现完善的错误处理机制: 

`let userMessage: string; switch (errCode) { case 1:  // PACKAGE_INVALID userMessage = '` 固件包无效,请检查固件文件是否正确 `'; break; case 2:  // IO_EX userMessage = '` 文件读写错误,请重试 `'; break; case 3:  // SPP_CONNECT_ERROR userMessage = '` 蓝牙连接异常,请重新连接设备 `'; break; case 4:  // BLE_OTA_SEND_MSG_ERROR userMessage = '` 数据发送失败,请检查蓝牙信号 `'; break; case 5:  // OTA_TIMEOUT userMessage = '` 操作超时,设备响应过慢,请重试 `'; break; default: userMessage = `` 未知错误 `: ${errMsg}`; } promptAction.showToast({ message: userMessage, duration: 3000, bottom: 150 });` 

```
}
```

### **7.3** 用户体验优化 

#### 在 OTA 升级过程中,建议向用户展示清晰的进度信息和当前状态: 

`switch (state) { case OtaStatus.STATE_IDLE: return '` 等待开始 `'; case OtaStatus.STATE_PREPARING: return '` 正在连接设备 `...'; case OtaStatus.STATE_PREPARED: return '` 设备就绪,准备升级 `'; case OtaStatus.STATE_TRANSFERRING: return '` 正在升级中 `'; case OtaStatus.STATE_TRANSFERRED: return '` 升级完成 `'; case OtaStatus.STATE_UNKNOWN: return '` 发生错误 `'; default: return '` 未知状态 `'; } }` 

### **7.4** 固件版本校验 

#### 在开始升级前,建议先检查固件版本与设备兼容性: 

```
  if (!this.arrayBuffer || !this.remoteStatus) {
    return false;
  }
```

#### `//` 获取固件版本 

#### `//` 版本比较逻辑(根据实际需求实现) 

`if (this.remoteStatus.versionName === otaVersion) { promptAction.showToast({ message: '` 当前已是最新版本 `', duration: 2000 }); return false; } return true; }` 

## **8.** 蓝牙协议基础 

### **8.1 UUID** 默认 配置 

SDK 使用以下默认 UUID 配置,如需修改请参考 6.3 节: 类型 

UUID 

SPP UUID 

00006666-0000-1000-8000-00805F9B34FB 

BLE Service UUID 

e49a25f8-f69a-11e8-8eb2-f2801f1b9fd1 

BLE Write Characteristic 

e49a25e0-f69a-11e8-8eb2-f2801f1b9fd1 

BLE Read Characteristic 

e49a28e1-f69a-11e8-8eb2-f2801f1b9fd1 

CCCD Descriptor 

00002902-0000-1000-8000-00805f9b34fb 

### **8.2** 通信协议结构 

SDK 采用 TLV ( Type-Length-Value )格式封装通信数据: ServiceID ( 1 字节): OTA 业务固定为 0x09 

CommandID ( 1 字节):指令类型,如握手、数据请求等 TLV 数据:后续为多个 TLV 结构 

### **8.3** 握手超时 

SDK 内置 20 秒的握手超时控制。如需调整,请修改 HANDSHAKE_TIMEOUT 常量值。 

## **9.** 常见问题 

Q1 :为什么设备一直处于 PREPARING 状态? A1 :请检查设备是否 正确响应了握手请求,确认蓝牙连接稳定,以及设备端的 OTA 功能 是否已启用。另外,检查设备返回的状态码是否为预期的成功码。 

Q2 :固件传输进度不更新怎么办? A2 :确保 onProgress 回调正常触 发,检查蓝牙信号强度,尝试缩短设备与手机之间的距离。如果问题 持续,可能需要检查设备端的接收处理逻辑。 

Q3 :如何支持自定义的固件文件格式? A3 : SDK 预期固件文件以 

“AOTA” ( 4 字节)作为文件头标识。如需支持其他格式,可能需要 修改 OtaManager 中的文件解析逻辑,或对固件文件进行预处理。 

Q4 : OTA 升级过程中设备断开连接怎么处理? A4 : SDK 会触发 onError 回调并返回错误码。实现断线重连逻辑后,重新调用 prepare() 和 upgrade() 方法, SDK 会自动处理断点续传。 

Q5 : BLE 和 SPP 模式如何选择? A5 : BLE 模式功耗更低,适合电池 供电设备; SPP 模式传输更稳定,适合大数据量传输。根据设备能力 和应用场景选择合适的模式。 

## **10.** 总结 

本指南详细介绍了 actionsibluz SDK 的安装配置、核心 API 、完整集 成示例以及最佳实践。通过遵循本指南,您应该能够快速在 HarmonyOS 应用中实现蓝牙固件升级功能。如有任何问题或需要进 一步的帮助,请参考项目源码或联系技术支持团队。
