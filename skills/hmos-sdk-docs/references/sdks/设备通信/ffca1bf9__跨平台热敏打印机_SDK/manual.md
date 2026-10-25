```
@psdk/
oh-package.json5
{
"dependencies": {
"@psdk/frame-father": "^0.7.6",
"@psdk/cpcl": "^0.7.6",
"@psdk/tspl": "^0.7.6",
"@psdk/esc": "^0.7.6",
"@psdk/ohos-bluetooth-le": "^0.7.6",
"@psdk/ohos-bluetooth-classic": "^0.7.6",
"@psdk/ohos-network": "^0.7.6",
"@psdk/ohos-usb": "^0.7.6"
  }
}
ohpminstall
```

|`@psdk/frame-father`|
|---|
|`@psdk/frame-imageb`|
|`@psdk/cpcl`|
|`@psdk/esc`|
|`@psdk/tspl`|
|`@psdk/ohos-bluetooth-le`|
|`@psdk/ohos-bluetooth-classic`|
|`@psdk/ohos-bluetooth-classic-raw`|
|`@psdk/ohos-network`|
|`@psdk/ohos-usb`|
|`@psdk/device-bluetooth-traits`|

```
module.json5
{
"module": {
"requestPermissions": [
      {
"name": "ohos.permission.ACCESS_BLUETOOTH"
      },
      {
"name": "ohos.permission.DISCOVER_BLUETOOTH"
      },
      {
"name": "ohos.permission.MANAGE_BLUETOOTH"
      },
      {
"name": "ohos.permission.APPROXIMATELY_LOCATION"
      }
    ]
  }
}
{
"module": {
"requestPermissions": [
      {
"name": "ohos.permission.INTERNET"
      }
    ]
  }
}
import { OhosBluetoothLe } from'@psdk/ohos-bluetooth-le';
import { ConnectedDevice, Lifecycle } from'@psdk/frame-father';
import { CPCL, GenericCPCL } from'@psdk/cpcl';
import { JluetoothDevice } from'@psdk/device-bluetooth-traits';
import ble from'@ohos.bluetooth.ble';
private ohosBluetoothLe =newOhosBluetoothLe({
  allowNoName: false,
  allowedWriteCharacteristic: '49535343-8841-43F4-A8D4-ECBE34729BB3',
  allowedReadCharacteristic: '49535343-1e4d-4bd9-ba61-23c647249616'
});
@State discoveredDevices: Array<JluetoothDevice<ble.ScanResult>>= [];
aboutToAppear() {
this.ohosBluetoothLe.discovered((devices)=> {
    devices.forEach(device => {
const isDuplicate = this.discoveredDevices.find(
        item => item.deviceId === device.deviceId
      );
if (!isDuplicate) {
this.discoveredDevices.push(device);
      }
    });
return Promise.resolve();
  });
}
async discovery() {
this.discoveredDevices= [];
try {
awaitthis.ohosBluetoothLe.startDiscovery();
  } catch (err) {
''
    console.error(Discovery error:, err);
  }
}
@State connectedDevice?: ConnectedDevice =undefined;
async onConnect(device: JluetoothDevice<ble.ScanResult>) {
try {
this.connectedDevice=awaitthis.ohosBluetoothLe.connect(device);
''
    console.log(Connected:, this.connectedDevice.deviceName());
  } catch (err) {
''
    console.error(Connection error:, err);
  }
}
async onDisconnect() {
if (this.connectedDevice) {
this.connectedDevice.disconnect();
this.connectedDevice=undefined;
  }
}
import { OhosBluetoothClassic } from'@psdk/ohos-bluetooth-classic';
import { ConnectedDevice } from'@psdk/frame-father';
import { JluetoothDevice } from'@psdk/device-bluetooth-traits';
private ohosBluetoothClassic =newOhosBluetoothClassic({
  allowNoName: false
});
@State discoveredDevices: Array<JluetoothDevice<string>>= [];
aboutToAppear() {
this.ohosBluetoothClassic.discovered((devices)=> {
    devices.forEach(device => {
const isDuplicate = this.discoveredDevices.find(
        item => item.deviceId === device.deviceId
      );
if (!isDuplicate) {
this.discoveredDevices.push(device);
      }
    });
return Promise.resolve();
  });
}
async discovery() {
this.discoveredDevices= [];
try {
awaitthis.ohosBluetoothClassic.startDiscovery();
  } catch (err) {
''
    console.error(Discovery error:, err);
  }
}
async onConnect(device: JluetoothDevice<string>) {
try {
this.connectedDevice=awaitthis.ohosBluetoothClassic.connect(device);
''
    console.log(Connected:, this.connectedDevice.deviceName());
  } catch (err) {
''
    console.error(Connection error:, err);
  }
}
import { OhosNetwork } from'@psdk/ohos-network';
import { ConnectedDevice } from'@psdk/frame-father';
private ohosNetwork =newOhosNetwork();
async connectWifi(ip: string, port: number) {
try {
this.connectedDevice=awaitthis.ohosNetwork.connect({
      address: ip,
      port: port
    });
''
    console.log(Connected to:, ip);
  } catch (err) {
''
    console.error(Connection error:, err);
  }
}
import { OhosUsb } from'@psdk/ohos-usb';
import { ConnectedDevice } from'@psdk/frame-father';
private ohosUsb =newOhosUsb();
async connectUsb() {
try {
const devices = await this.ohosUsb.getDevices();
if (devices.length>0) {
this.connectedDevice=awaitthis.ohosUsb.connect(devices[0]);
''
      console.log(USB connected);
    }
  } catch (err) {
''
    console.error(USB connection error:, err);
  }
}
import { CPCL, GenericCPCL } from'@psdk/cpcl';
import { Lifecycle } from'@psdk/frame-father';
const lifecycle = newLifecycle(this.connectedDevice);
const cpcl:GenericCPCL = CPCL.generic(lifecycle);
const psdk = cpcl
.page({ width: 576, height: 400 })
''
.text({ x: 50, y: 50, content:  })
''
.barcode({ x: 50, y: 150, content: 1234567890 })
.print();
await psdk.write();
import { CPCL } from'@psdk/cpcl';
import { Lifecycle } from'@psdk/frame-father';
const lifecycle = newLifecycle(this.connectedDevice);
const cpcl = CPCL.generic(lifecycle);
const psdk = cpcl
.page({ width: 576, height: 400 })
//
.center()
.setMag({ x: 2, y: 2 })
''
.text({ x: 0, y: 30, font: 24, content:  })
.setMag({ x: 1, y: 1 })
//
.left()
.line({ x1: 30, y1: 80, x2: 546, y2: 80, width: 2 })
''
.text({ x: 30, y: 100, font: 24, content: :  })
''
.text({ x: 30, y: 140, font: 24, content: : 500g/ })
''
.text({ x: 30, y: 180, font: 24, content: :  })
.setBold(true)
''
.text({ x: 30, y: 220, font: 24, content: : 25.90 })
.setBold(false)
//
.barcode({
    x: 100, y: 280,
    type: '128',
    ratio: 2,
    height: 50,
    content: '6901234567890'
  })
//
.qrcode({
    x: 400, y: 100,
    content: 'https://example.com/product/123'
  })
.print();
await psdk.write();
import { TSPL, GenericTSPL } from'@psdk/tspl';
import { Lifecycle } from'@psdk/frame-father';
const lifecycle = newLifecycle(this.connectedDevice);
const tspl:GenericTSPL = TSPL.generic(lifecycle);
const psdk = tspl
.page({ width: 60, height: 40 })
.gap(3)
.cls()
''
.text({ x: 50, y: 50, content:  })
.print(1);
await psdk.write();
import { TSPL } from'@psdk/tspl';
import { Lifecycle } from'@psdk/frame-father';
const lifecycle = newLifecycle(this.connectedDevice);
const tspl = TSPL.generic(lifecycle);
const psdk = tspl
.page({ width: 60, height: 40 })
.gap(3)
''
.direction(up)
.cls()
//
.text({
    x: 180, y: 30,
    font: 'TSS24.BF2',
    xMulti: 2, yMulti: 2,
    content: ''
  })
//
.bar({ x: 30, y: 80, width: 420, height: 2 })
//
''''
.text({ x: 30, y: 100, font: TSS24.BF2, content: :  })
''''
.text({ x: 30, y: 140, font: TSS24.BF2, content: : 500g/ })
''''
.text({ x: 30, y: 180, font: TSS24.BF2, content: : 25.90 })
//
.barcode({
    x: 100, y: 220,
    type: '128',
    height: 60,
    content: '6901234567890'
  })
//
.qrcode({
    x: 350, y: 100,
    cellWidth: 4,
    content: 'https://example.com'
  })
.print(1);
await psdk.write();
import { ESC, GenericESC } from'@psdk/esc';
import { Lifecycle } from'@psdk/frame-father';
const lifecycle = newLifecycle(this.connectedDevice);
const esc:GenericESC = ESC.generic(lifecycle);
const psdk = esc
.initialize()
''
.align(center)
''
.text()
''
.align(left)
''
.text(A x1  29.90)
.cut();
await psdk.write();
import { ESC } from'@psdk/esc';
import { Lifecycle } from'@psdk/frame-father';
const lifecycle = newLifecycle(this.connectedDevice);
const esc = ESC.generic(lifecycle);
const psdk = esc
.initialize()
//
''
.align(center)
.textSize({ width: 2, height: 2 })
.bold(true)
''
.text(XX )
.bold(false)
.textSize({ width: 1, height: 1 })
''
.text(: 20240115001)
''
.text(================================)
//
''
.align(left)
''
.text( 500ml    x2    6.00)
''
.text(     x1    8.50)
.text('--------------------------------')
//
.textSize({ width: 1, height: 2 })
''
.text(: 14.50)
.textSize({ width: 1, height: 1 })
//
''
.align(center)
''
.qrcode({ content: https://shop.example.com, size: 5 })
''
.text()
.feed(3)
.cut();
await psdk.write();
import { CPCL, GenericCPCL } from'@psdk/cpcl';
import { ESC, GenericESC } from'@psdk/esc';
import { ConnectedDevice, Lifecycle } from'@psdk/frame-father';
import { GenericTSPL, TSPL } from'@psdk/tspl';
export classPrinterUtil {
static instance:PrinterUtil|null=null;
private _connectedDevice?:ConnectedDevice;
private _cpcl?:GenericCPCL;
private _tspl?:GenericTSPL;
private _esc?:GenericESC;
static getInstance() {
if (!PrinterUtil.instance) {
      PrinterUtil.instance=newPrinterUtil();
    }
return PrinterUtil.instance;
  }
private constructor() {}
init(connectedDevice:ConnectedDevice) {
this._connectedDevice= connectedDevice;
constlifecycle = newLifecycle(connectedDevice);
this._cpcl=CPCL.generic(lifecycle);
this._tspl=TSPL.generic(lifecycle);
this._esc=ESC.generic(lifecycle);
  }
isConnected():boolean {
return this._connectedDevice!=null;
  }
connectedDevice():ConnectedDevice|undefined {
return this._connectedDevice;
  }
cpcl():GenericCPCL {
if (!this._connectedDevice)
throwError('The device is not connected');
return this._cpcl!;
tspl():GenericTSPL {
if (!this._connectedDevice)
throwError('The device is not connected');
return this._tspl!;
  }
esc():GenericESC {
if (!this._connectedDevice)
throwError('The device is not connected');
return this._esc!;
  }
}
//
this.connectedDevice=awaitthis.ohosBluetoothLe.connect(device);
PrinterUtil.getInstance().init(this.connectedDevice);
//
const cpcl = PrinterUtil.getInstance().cpcl();
const psdk = cpcl
.page({ width: 576, height: 400 })
''
.text({ x: 50, y: 50, content:  })
.print();
await psdk.write();
async safeWrite(psdk: PSDK<GenericTSPL>|PSDK<GenericCPCL>|
PSDK<GenericESC>) {
try {
//
const report = await psdk.write();
//
// const report = await psdk.write({
//   enableChunkWrite: true,
//   chunkSize: 20
// });
''
    console.log(Print report:, report);
  } catch (e) {
''
    console.error(Print error:, e);
  }
}
import { OhosBluetoothLe } from'@psdk/ohos-bluetooth-le';
```

- `import { ConnectedDevice } from '@psdk/frame-father';` 

```
import { JluetoothDevice } from'@psdk/device-bluetooth-traits';
import { PrinterUtil } from'../common/PrinterUtil';
import ble from'@ohos.bluetooth.ble';
import promptAction from'@ohos.promptAction';
@Entry
@Component
struct PrinterPage {
@State discoveredDevices: Array<JluetoothDevice<ble.ScanResult>>= [];
''
@State connectionState: string =Not connected;
```

- `@State connectedDevice?: ConnectedDevice = undefined;` 

```
  private ohosBluetoothLe =newOhosBluetoothLe({
    allowNoName: false,
    allowedWriteCharacteristic: '49535343-8841-43F4-A8D4-ECBE34729BB3',
    allowedReadCharacteristic: '49535343-1e4d-4bd9-ba61-23c647249616'
  });
aboutToAppear() {
this.ohosBluetoothLe.discovered((devices)=> {
      devices.forEach(device => {
const isDuplicate = this.discoveredDevices.find(
          item => item.deviceId === device.deviceId
        );
if (!isDuplicate) {
this.discoveredDevices.push(device);
        }
      });
return Promise.resolve();
    });
  }
  async discovery() {
this.discoveredDevices= [];
awaitthis.ohosBluetoothLe.startDiscovery();
  }
  async onConnect(device: JluetoothDevice<ble.ScanResult>) {
try {
''
      promptAction.showToast({ message: Connecting..., duration: 2000 });
this.connectedDevice=awaitthis.ohosBluetoothLe.connect(device);
      PrinterUtil.getInstance().init(this.connectedDevice);
this.connectionState= `${this.connectedDevice.deviceName()}
connected`;
      promptAction.showToast({
''
        message: Connected successfully,
        duration: 2000
      });
    } catch (err) {
''
      promptAction.showToast({ message: Connection failed, duration: 2000
});
    }
  }
  async onPrint() {
if (!this.connectedDevice) {
''
      promptAction.showToast({ message: Please connect device, duration:
2000 });
return;
    }
try {
const cpcl = PrinterUtil.getInstance().cpcl();
const psdk = cpcl
.page({ width: 576, height: 400 })
.center()
''
.text({ x: 0, y: 50, font: 24, content: Test Print })
.print();
await psdk.write({ enableChunkWrite: true, chunkSize: 20 });
''
      promptAction.showToast({ message: Print success, duration: 2000 });
    } catch (e) {
''
      promptAction.showToast({ message: Print failed, duration: 2000 });
    }
  }
onDisconnect() {
if (this.connectedDevice) {
this.connectedDevice.disconnect();
''
this.connectionState=Not connected;
this.connectedDevice=undefined;
''
      promptAction.showToast({ message: Disconnected, duration: 2000 });
    }
  }
build() {
Column() {
Text(this.connectionState)
.fontSize(20)
.margin(20)
Button('Start Discovery')
.onClick(()=>this.discovery())
.margin(10)
List() {
ForEach(this.discoveredDevices, (device:
JluetoothDevice<ble.ScanResult>)=> {
ListItem() {
Text(device.name)
.onClick(()=>this.onConnect(device))
          }
        })
      }
''
.height(40%)
Button('Print Test')
.onClick(()=>this.onPrint())
.margin(10)
Button('Disconnect')
.onClick(()=>this.onDisconnect())
.margin(10)
    }
''
.width(100%)
''
.height(100%)
  }
}
await psdk.write({ enableChunkWrite: true, chunkSize: 20 });
module.json5
try {
await psdk.write();
''
  console.log(Print success);
} catch (error) {
''
  console.error(Print error:, error.message);
  promptAction.showToast({
    message: `Print failed: ${error.message}`,
    duration: 2000
  });
}
```
