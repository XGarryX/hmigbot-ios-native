# ESC Harmony SDK 指令开发手册.pdf

# **ESC Harmony SDK** 指令开发手册 

### **1.0.3** 

(注:浏览时请使用 **PDF** 左侧导航栏) 

## **1.** 更新记录 

|版本|内容|编辑者|
|---|---|---|
|1.0.1|鸿蒙ESC SDK 初始版本|dan|
|1.0.2|支持鸿蒙NEXT 版本|dan|
|1.0.3|支持纯血版的ESC 指令|dan|

## **2.** 手册信息 

本 SDK 手册提供了开发 Harmony 应用程序所需的接口信息。我们在不断地努力提高和升 级我们所有产品的功能与质量。之后,产品规格和用户手册的内容可能会更改,请联系我 们的客服确认最新版本。 

## **3.** 支持版本 

#### 5.0.0(12)及以上 

## **4.** 备注 

这个手册介绍怎么通过 SDK 实现票据打印机的打印,常量定义在 EscPrinter 和 PrinterSDK 中。打印机分辨率为 200 dpi 时,1 mm=8 dot(点);打印机分辨率为 300 dpi 时,1 mm=12 dot(点)。 

## **5. PrinterSDK** 

### **1.1. 5.1. createDevice** 

根据设备类型,创建设备。 

static createDevice(deviceType: number):IDeviceConnect 

【参数】 

  deviceType: number 设备类型 

|值|描述|
|---|---|
|DEVICE_TYPE_USB|USB 类型|
|DEVICE_TYPE_BLUETOOTH|蓝牙类型|
|DEVICE_TYPE_ETHERNET|网络类型|

【返回值】 IDeviceConnect 连接的对象 

### **1.2. getUsbNames** 

获取 USB 路径列表 

static getUsbNames(): Array<string> static getUsbDevices(): Array<usbManager.USBDevice> 

【返回值】 

USB 设备路径列表或设备对象列表 

## **2. IDeviceConnect** 

### **2.1. connect** 

连接设备,连接失败时会抛出异常。 

connect(info: string): Promise<void> 

【参数】 

  info: string 连接信息。 设备类型为 DEVICE_TYPE_USB 时,info 为 USB 路径名; 设备类型为 DEVICE_TYPE_BLUETOOTH 时,info 为系统分配的蓝牙 id 设备类型为 DEVICE_TYPE_ETHERNET 时,info 为打印机 ip 地址,或 IP 地址,端口号组合。 例:"192.168.1.100" 或 "192.168.1.100,9100" 

【返回值】 

Promise<void> 

错误码 **:** 

|错误码**ID**|描述|
|---|---|
|ERR_USB_DEVICE_ERR(-100)|找不到对应的USB 设备|
|ERR_USB_PERMISSION_DENIED(-101)|获取USB 权限失败|
|ERR_USB_TYPE_ERR(-102)|USB 设备类型错误|
|ERR_USB_OPEN_FAIL(-103)|连接USB 失败|
|其它|系统级别的异常|

### **2.2. sendData** 

此函数功能为向打印机发送数据。发送失败时,会抛出异常。 

sendData(data:Uint8Array): Promise<void> sendDatas(datas:List<Uint8Array>): Promise<void> 

【参数】 

- data:Uint8Array 

发送的字节数组 

- datas:List<Uint8Array> 

发送的字节数组集合 

#### 【返回值】 

Promise<void> 

#### 错误码 **:** 

|错误码**ID**|描述|
|---|---|
|ERR_CONNECT_DISCONNECTED(-200)|连接已经断开|
|其它|系统级别的异常|

### **2.3. getConnectInfo** 

获取连接信息。 

getConnectInfo():string 

【返回值】 

返回连接信息,对应的 connect 方法里面的 info 

### **2.4. readData** 

此函数功能为读取打印机的数据。超时时间为 3 秒 

readData(): Promise<Uint8Array> 

【返回值】 读取的数据数组 

#### 错误码 **:** 

|错误码**ID**|描述|
|---|---|
|ERR_CONNECT_DISCONNECTED(-200)|连接已经断开|
|ERR_READ_TIMEOUT|读取数据超时|
|其它|系统级别的异常|

### **2.5. close** 

此函数功能为关闭通讯。当不使用端口通讯时,请关闭端口。 

close() 

【返回值】 void 

## **7. EscPrinter** 

### **7.1. constructor** 

构造函数,创建 ESC 打印对象。 

constructor(connect: IDeviceConnect) 

【参数】 

  connect: IDeviceConnect 连接对象,可通过 PrinterSDK.createDevice(deviceType)获取。 

【返回值】 

EscPrinter 对象 

### **7.2. printString** 

此函数功能为打印文本。 

printString(data: string): EscPrinter 

#### 【参数】 

  data: string 数据内容 

【返回值】 

EscPrinter 对象 

### **7.3. printText** 

此函数功能为特定格式的文本打印。 

注:data 需以'\n'结尾,否则样式有可能会无效。 

printText(options: { data: string, alignment?: Alignment, attribute?: FntAttribute, textSize?: TextSize }): EscPrinter 

#### 【参数】 

  data: string 

数据内容 

  alignment: Alignment 

#### 文本的对齐方式,默认为 Alignment.LEFT。 

|值|描述|
|---|---|
|LEFT|左对齐|
|CENTER|居中对齐|
|RIGHT|右对齐|

####   attribute: FntAttribute 

#### 文本的属性,默认为 FntAttribute.DEFAULT 

|值|描述|
|---|---|
|DEFAULT|FontA,标准字体|
|FONTB|FontB 字体|
|BOLD|粗字体|
|REVERSE|反打印属性|
|UNDERLINE|下划线属性|
|UNDERLINE2|粗下划线属性|

####   textSize: TextSize 

打印的文本字体大小,默认为 TextSize.WIDTH1 | TextSize.HEIGHT1 

|值|描述|
|---|---|
|WIDTH1|将宽度比设置为x1|
|WIDTH2|将宽度比设置为x2|
|WIDTH3|将宽度比设置为x3|
|WIDTH4|将宽度比设置为x4|
|WIDTH5|将宽度比设置为x5|
|WIDTH6|将宽度比设置为x6|
|WIDTH7|将宽度比设置为x7|
|WIDTH8|将宽度比设置为x8|
|HEIGHT1|将高度比设置为x1|
|HEIGHT2|将高度比设置为x2|
|HEIGHT3|将高度比设置为x3|
|HEIGHT4|将高度比设置为x4|
|HEIGHT5|将高度比设置为x5|
|HEIGHT6|将高度比设置为x6|
|HEIGHT7|将高度比设置为x7|
|HEIGHT8|将高度比设置为x8|

#### 【返回值】 

EscPrinter 对象 

### **7.4. printBitmap** 

此函数功能为打印图片文件,该方法不支持 76 针式打印机。 

async printBitmap(options: { image: image.ImageSource, cWidth: number, alignment?: Alignment, model?: BmpModel }): Promise<EscPrinter> 

#### 【参数】 

- image: image.ImageSource 

- 图片对象 

- cWidth: number 

最大图片宽度,图片宽度超过该值,会等比例缩放图片。 

- alignment: Alignment 

文本的对齐方式,默认为 Alignment.LEFT。 

|值|描述|
|---|---|
|LEFT|左对齐|

|CENTER|居中对齐|
|---|---|
|RIGHT|右对齐|

  model: BmpModel 

模式,默认:BmpModel.NORMAL 

|值|描述|
|---|---|
|NORMAL|图片原始尺寸|
|WIDTH_DOUBLE|图片宽度双倍|
|HEIGHT_DOUBLE|图片高度双倍|
|WIDTH_HEIGHT_DOUBLE|图片宽高都双倍|

#### 【返回值】 

EscPrinter 对象 

### **7.5. printBarCode** 

此函数功能为打印一维条码。 

printBarCode(options: { data: string, codeType: BarCodeType, width?: number, height?: number, alignment?: Alignment, textPosition?: BarcodeTxtPosition }): EscPrinter 

#### 【参数】 

  data: string 数据内容 

  codeType: BarCodeType 类型 

|值|描述|
|---|---|
|UPCA|UPC A 类型|
|UPCE|UPCE 类型|
|EAN8|EAN-8 类型|
|EAN13|EAN-13 类型|
|JAN8|JAN-8 类型|
|JAN13|JAN-13 类型|
|ITF|ITF 类型|
|Codabar|Codabar 类型|
|Code39|Code 39 类型|
|Code93|Code 93 类型|
|Code128|Code 128 类型|

  width: number 

条码横向模块宽度,范围【2,6】,默认 3 

####   height: number 

条码高度,范围【1,255】。默认 162 

  alignment: Alignment 

条码的对齐方式,默认 Alignment.CENTER 

|值|描述|
|---|---|
|LEFT|左对齐|
|CENTER|居中对齐|
|RIGHT|右对齐|

####   textPosition: BarcodeTxtPosition 

打印条码是,为 HRI 字符选择打印的位置。默认为 BarcodeTxtPosition.BELOW。 

|值|描述|
|---|---|
|NONE|无文本|
|ABOVE|条码上方|
|BELOW|条码下方|
|BOTH|条码上、下方都打印|

【返回值】 

EscPrinter 对象 

### **7.6. feedLine** 

此函数功能为打印并向前走纸 n 行 

feedLine(lineCount: number = 1): EscPrinter 

#### 【参数】 

  lineCount: number = 1 走纸的行数。默认为 1 

【返回值】 

EscPrinter 对象 

### **7.7. printQRCode** 

此函数功能为打印二维码。 

printQRCode(options:{data: string, moduleSize?: number, ecLevel?: QrcodeErrorLevel, alignment?: Alignment}): EscPrinter 

#### 【参数】 

####   data: string 

#### 数据内容 

####   moduleSize: number = 8 

单元大小,范围【1,16】,默认值 8 

####   ecLevel: QrcodeErrorLevel 

#### 错误纠正等级, 默认值为 QrcodeErrorLevel.L 

|值|描述|
|---|---|
|L|错误纠正等级L(7%)|
|M|错误纠正等级M(15%)|
|Q|错误纠正等级Q(25%)|
|H|错误纠正等级H(30%)|

####   alignment: Alignment 

#### 条码的对齐方式,默认 Alignment.CENTER 

|值|描述|
|---|---|
|LEFT|左对齐|
|CENTER|居中对齐|
|RIGHT|右对齐|

【返回值】 EscPrinter 对象 

### **7.8. cutPaper** 

此函数功能为切纸 

cutPaper(model: CutPaperType = CutPaperType.HALF): EscPrinter cutHalfAndFeed(distance: number): EscPrinter 

#### 【参数】 

  model: CutPaperType 

切纸模式,默认 CutPaperType.HALF。 

|值|描述|
|---|---|
|ALL|全切|
|HALF|半切|

- distance: number 

进纸 distance × (纵向移动单位)英寸并且半切纸 

#### 【返回值】 

EscPrinter 对象 

### **7.9. openCashBox** 

此函数功能为打开钱箱抽屉 

openCashBox(options:{pinNum: CashDrawerPin, onTime?: number, offTime?: number}): EscPrinter 

#### 【参数】 

  pinNum: CashDrawerPin 

连接的引脚 

|值|描述|
|---|---|
|TWO|引脚2|
|FIVE|引脚5|

  onTime: number 

钱箱产生脉冲开始时间 onTime*2ms,范围【0,255】。默认值为 30 

  offTime: number 

钱箱产生脉冲结束时间 offTime*2ms,范围【0,255】,默认值为 255 如果 onTime>offTime,结束时间为 onTime*2ms。 

【返回值】 

EscPrinter 对象 

### **7.10. setCharSet** 

设置字符编码,默编码为“GBK” 

setCharset(charset: string) 

【参数】 

  charset: string 编码类型名 

【返回值】 

void 

### **7.11. setTextStyle** 

此函数功能为设置字体信息 

setTextStyle(options:{attribute: FntAttribute, textSize: TextSize}): EscPrinter 

#### 【参数】 

####   attribute: FntAttribute 文本的属性 

|值|描述|
|---|---|
|DEFAULT|FontA,标准字体|
|FONTB|FontB 字体|
|BOLD|粗字体|
|REVERSE|反打印属性|
|UNDERLINE|下划线属性|
|UNDERLINE2|粗下划线属性|

####   textSize: TextSize 

#### 打印的文本字体大小 

|值|描述|
|---|---|
|WIDTH1|将宽度比设置为x1|
|WIDTH2|将宽度比设置为x2|
|WIDTH3|将宽度比设置为x3|
|WIDTH4|将宽度比设置为x4|
|WIDTH5|将宽度比设置为x5|
|WIDTH6|将宽度比设置为x6|
|WIDTH7|将宽度比设置为x7|
|WIDTH8|将宽度比设置为x8|
|HEIGHT1|将高度比设置为x1|
|HEIGHT2|将高度比设置为x2|
|HEIGHT3|将高度比设置为x3|
|HEIGHT4|将高度比设置为x4|
|HEIGHT5|将高度比设置为x5|
|HEIGHT6|将高度比设置为x6|
|HEIGHT7|将高度比设置为x7|
|HEIGHT8|将高度比设置为x8|

EscPrinter 对象 

#### 【返回值】 

### **7.12. setAlignment** 

此函数功能为设置内容的对齐方式 

setAlignment(alignment: Alignment): EscPrinter 

#### 【参数】 

  alignment: Alignment 对齐模式。 

|值|描述|
|---|---|
|LEFT|左对齐|
|CENTER|居中对齐|
|RIGHT|右对齐|

#### 【返回值】 

EscPrinter 对象 

### **7.13. printerCheck** 

此函数功能为查询打印机所有状态。 

printerCheck(type: StatusType): Promise<Uint8Array> 

#### 【参数】 

  type: number 查询类型 

|值|描述|
|---|---|
|PRINT(1)|打印机状态|
|OFFLINE(2)|脱机状态|
|ERROR(3)|错误状态|
|PAPER(4)|传送纸状态|

【返回值】 

返回的内容为对应的打印机状态,如果无返回则返回空数组 

|**type**|位|描述|值|十进制值|
|---|---|---|---|---|
||0|固定为0|0|0|
||1|固定为1|1|2|
||2|一个或两个钱箱打开|0|0|
|PRINT||两个钱箱都关闭|1|4|
||3|联机|0|0|
|||脱机|1|8|
||4|固定为1|1|16|
||5,6,7|固定为0|0|0|
||0|固定为0|0|0|
||1|固定为1|1|2|
||2|上盖关|0|0|
|||上盖开|1|4|
||3|未按走纸键|0|0|
|OFFLINE||按下走纸键|1|8|
||4|固定为1|1|16|
||5|有纸|0|0|
|||缺纸|1|32|
||6|无错误情况|0|0|
|||有错误情况|1|64|
||7|固定为0|0|0|
||0|固定为0|0|0|
||1|固定为1|1|2|
||2|未定义|0|0|
||3|切刀无错误|0|0|
|||切刀有错误|1|8|
|ERROR|4|固定为1|1|16|
||5|无不可恢复错误|0|0|
|||有不可恢复错误|1|32|
||6|打印头温度和电压正常|0|0|
|||打印头温度或电压超出范围|1|64|
||7|固定为0|0|0|
||0|固定为0|0|0|
||1|固定为1|1|2|
||2,3|有纸|0|0|
|PAPER||纸将尽|1|12|
||4|固定为1|1|16|
||5,6|有纸|0|0|
|||纸尽|1|96|
||7|固定为0|0|0|

### **7.14. setPrintArea** 

此函数功能为在页模式下设置打印区域 

setPrintArea(options:{width: number, height: number, x?: number, y?: number}): EscPrinter 

【参数】 

  width: number 宽度(单位:点)。   height: number 高度(单位:点)。   x: number 起始横坐标,单位为点。默认为 0   y: number 起始纵坐标,单位为点。默认为 0 

【返回值】 EscPrinter 对象 

### **7.15. setPageModel** 

此函数功能为开启或者关闭页模式 

setPageModel(isOpen: boolean): EscPrinter 

【参数】 

  isOpen: boolean true 表示开启页模式,false 表示关闭页模式 

【返回值】 

EscPrinter 对象 

### **7.16. printPageModelData** 

打印页模式下的数据,并回到标准模式。 

printPageModelData(): EscPrinter 

EscPrinter 对象 

#### 【返回值】 

### **7.17. setPrintDirection** 

设置页模式下的打印区域方向 

setPrintDirection(direction: PrintDirection): EscPrinter 

#### 【参数】 

  direction: PrintDirection 方向 

|值|描述|
|---|---|
|LEFT_TOP|从左上角开始往右|
|LEFT_BOTTOM|从左下角开始往上|
|RIGHT_BOTTOM|从右下角开始往左|
|RIGHT_TOP|从右上角开始往下|

【返回值】 EscPrinter 对象 

### **7.18. setAbsoluteHorizontal** 

设置横向绝对打印位置 

setAbsoluteHorizontal(position: number): EscPrinter 

【参数】 

  position: number 开始的位置 

【返回值】 

EscPrinter 对象 

### **7.19. setRelativeHorizontal** 

此函数功能为设置相对横向打印位置 

setRelativeHorizontal(position: number): EscPrinter 

【参数】 

  position: number 开始的位置 

【返回值】 EscPrinter 对象 

### **7.20. downloadNVImage** 

此函数功能为保存图片到 flash 中 

async downloadNVImage(imgs: List<image.ImageSource>, imageWidth: number): Promise<EscPrinter> 

#### 【参数】 

  imgs: List<image.ImageSource> 图片对象列表   imageWidth: number 最大图片宽度,图片宽度超过该值,会等比例缩放图片。 

【返回值】 EscPrinter 对象 

### **7.21. printNVImage** 

此函数功能为打印存储在 Flash 中的图片 

printNVImage(options:{index: number, model?: BmpModel}): EscPrinter 

【参数】 

  index: number 图片下标,范围【1,255】 

  model: BmpModel 

模式 

|值|描述|
|---|---|
|NORMAL|图片原始尺寸|
|WIDTH_DOUBLE|图片宽度双倍|
|HEIGHT_DOUBLE|图片高度双倍|
|WIDTH_HEIGHT_DOUBLE|图片宽高都双倍|

#### 【返回值】 

EscPrinter 对象 

### **7.22. initializePrinter** 

此函数功能为初始化打印机,清除打印缓冲区的数据 

initializePrinter(): EscPrinter 

【返回值】 

EscPrinter 对象 

### **7.23. selectBitmapModel** 

#### 此函数功能为选择位图模式 

async selectBitmapModel(options: {img: image.ImageSource, width: number, model: SelectBmpMode}): Promise<EscPrinter> 

#### 【参数】 

  model: number 

模式 

|变量|描述|
|---|---|
|SINGLE_DENSITY_8|8点单密度|
|DOUBLE_DENSITY_8|8点双密度|
|SINGLE_DENSITY_24|24点单密度(76针式打印机不支持)|
|DOUBLE_DENSITY_24|24点双密度(76针式打印机不支持)|

  width: number 

最大图片宽度,图片宽度超过该值,会等比例缩放图片。 

  img: image.ImageSource 图片对象 

【返回值】 EscPrinter 对象 

### **7.24. feedDot** 

此函数功能为打印并走纸对应的距离 

feedDot(dotCount: number): EscPrinter 

【参数】 

  dotCount: number 走纸的距离,单位为点。 

【返回值】 EscPrinter 对象 

### **7.25. setLineSpacing** 

此函数功能为设置行高 

setLineSpacing(space: number): EscPrinter 

【参数】 

  space: number 行空间高度,如果想恢复到默认,则传入 SPACE_DEFAULT。 

【返回值】 EscPrinter 对象 

### **7.26. setTurnUpsideDownMode** 

此函数功能为选择或取消倒置打印模式 

setTurnUpsideDownMode(on: boolean): EscPrinter 

#### 【参数】 

  on: boolean true 表示选择 false 表示取消 

#### 【返回值】 

EscPrinter 对象 

### **7.27. selectCodePage** 

此函数功能为选择字符代码表 

selectCodePage(page: number): EscPrinter 

#### 【参数】 

  page: number 代码表值 

|值|描述|值|描述|
|---|---|---|---|
|0|PC437(Std.Europe)|56|PC861(Icelandic)|
|1|Katakana|57|PC863(Canadian)|
|2|PC850(Multilingual)|58|PC865(Nordic)|
|3|PC860(Portugal)|59|PC866(Russian)|
|4|PC863(Canadian)|60|PC855(Bulgarian)|
|5|PC865(Nordic)|61|PC857(Turkey)|
|6|West Europe|62|PC862(Hebrew)|
|7|Greek|63|PC864(Arabic)|
|8|Hebrew|64|PC737(Greek)|
|9|East Europe|65|PC851(Greek)|
|10|Iran|66|PC869(Greek)|
|16|WPC1252|67|PC928(Greek)|
|17|PC866(Cyrillic#2)|68|PC772(Lithuanian)|
|18|PC852(Latin2)|69|PC774(Lithuanian)|
|19|PC858|70|PC874(Thai)|
|20|IranII|71|WPC1252(Latin-1)|
|21|Latvian|72|WPC1250(Latin-2)|
|22|Arabic|73|WPC1251(Cyrillic)|
|23|PT1511251|74|PC3840(IBM-Russian)|
|24|PC747|75|PC3841(Gost)|
|25|WPC1257|76|PC3843(Polish)|
|27|Vietnam|77|PC3844(CS2)|
|28|PC864|78|PC3845(Hungarian)|
|29|PC1001|79|PC3846(Turkish)|

|30|Uigur|80|PC3847(Brazil-ABNT)|
|---|---|---|---|
|31|Hebrew|81|PC3848(Brazil)|
|32|WPC1255(Israel)|82|PC1001(Arabic)|
|255|Thai|83|PC2001(Lithuan)|
|33|WPC1256|84|PC3001(Estonian-1)|
|50|PC437(Std.Europe)|85|PC3002(Eston-2)|
|51|Katakana|86|PC3011(Latvian-1)|
|52|PC437(Std.Europe)|87|PC3012(Tatv-2)|
|53|PC858(Multilingual)|88|PC3021(Bulgarian)|
|54|PC852(Latin-2)|89|PC3041(Maltese)|
|55|PC860(Portuguese)|||

【返回值】 EscPrinter 对象 

### **7.28. selectCharacterFont** 

此函数功能为设置字体 

selectCharacterFont(font: FontType): EscPrinter 

【参数】 

  font: number 

字体类型 

|值|描述|
|---|---|
|STANDARD|标准ASCII 码字体(12 × 24)|
|COMPRESS|压缩ASCII 码字体(9 × 17)|

【返回值】 EscPrinter 对象 

### **7.29. setCharRightSpace** 

此函数功能为设置字符的右间距 

setCharRightSpace(space: number): EscPrinter 

【参数】 

  space: number 

右间距距离为[n×横向移动单位或纵向移动单位]英寸。 

【返回值】 EscPrinter 对象 

### **7.30. printPDF417** 

此函数功能为打印 PDF417 二维码,部分机器支持。 

printPDF417(options:{pdfData: string, cellWidth?: number, cellHeightRatio?: number, numberOfColumns?: number, numberOfRows?: number, eclType?: number, eclValue?: number, alignment?: Alignment}): EscPrinter 

【参数】 

  pdfData: string 数据内容   cellWidth: number = 3 单元宽度, 范围[2- 8],默认为 3   cellHeightRatio: number = 3 设置行高. 范围[2-8],默认为 3。 cellHeight = cellHeightRatio x cellWidth   numberOfColumns: number = 0 数据区域的列数。范围[0-30], 0 表示自动处理,默认为 0   numberOfRows: number = 0 设置行数,范围[0, 3-90],0 表示自动处理,默认为 0   eclType: number = 48 错误纠正等级类型,范围[48-49]。 48:误差校正级别由级别来设定 49:误差校正级别由比率设定。比率为 eclValue x 10%   eclValue: number = 48 错误纠正等级值, eclType = 48:范围[ 48 – 56 ]. eclType = 49:范围[ 1 – 40 ].   alignment: Alignment 

#### 文本的对齐方式,默认为 Alignment.LEFT。 

|值|描述|
|---|---|
|LEFT|左对齐|
|CENTER|居中对齐|
|RIGHT|右对齐|

【返回值】 EscPrinter 对象 

### **7.31. sendBuff** 

此函数功能为发送缓存中的数据。 

async sendBuff():Promise<void> 

【返回值】 

Promise<void> 

### **7.32. setIp** 

此函数功能为设置网络 ip 地址 

setIp(ip: Uint8Array): EscPrinter 

#### 【参数】 

  ip: Uint8Array ip 地址,长度为 4 的字节数组。如:new Uint8Array([192,168,1,100]) 

【返回值】 EscPrinter 对象 

### **7.33. setMask** 

此函数功能为设置子网掩码 

setMask(mask: Uint8Array): EscPrinter 

【参数】 

  mask: Uint8Array 子网掩码,长度为 4 的字节数组。 

【返回值】 

EscPrinter 对象 

### **7.34. setGateway** 

此函数功能为设置默认网关 

setGateway(gateway: Uint8Array): EscPrinter 

#### 【参数】 

  gateway: Uint8Array 默认网关,长度为 4 的字节数组 

【返回值】 

EscPrinter 对象 

### **7.35. setNetAll** 

此函数功能为设置网络信息 

setNetAll(options:{ip: Uint8Array, mask: Uint8Array, gateway: Uint8Array, dhcpIsOpen: boolean}): EscPrinter 

#### 【参数】 

- ip: Uint8Array 

ip 地址,长度为 4 的字节数组。如:new Uint8Array([192,168,1,100]) 

  mask: Uint8Array 

子网掩码,长度为 4 的字节数组。 

- gateway: Uint8Array 

默认网关,长度为 4 的字节数组 

- dhcpIsOpen: boolean 

是否打开 DHCP。 true 打开 false 关闭。 

#### 【返回值】 

EscPrinter 对象 

### **7.36. setBluetooth** 

此函数功能为设置蓝牙信息 

setBluetooth(options:{name: string, pin: string}): EscPrinter 

【参数】 

  name: string 蓝牙名称   pin: string 蓝牙的 pin 码 

【返回值】 EscPrinter 对象 

### **7.37. getSerialNumber** 

此函数功能为获取打印机序列号 

getSerialNumber(): Promise<Uint8Array> 

#### 【返回值】 

查询到的 SN 码的字节数组。无返回则返回空数组 

---

# TSPL Harmony SDK 指令开发手册.pdf

# **TSPL Harmony SDK** 指令开发手册 

**1.0.2** 

## **1.** 更新记录 

|版本|内容|编辑者|
|---|---|---|
|1.0.2|鸿蒙TSPL SDK 初始版本|dan|

## **2.** 手册信息 

本 SDK 手册提供了开发 Harmony 应用程序所需的接口信息。我们在不断地努力提高和升 级我们所有产品的功能与质量。之后,产品规格和用户手册的内容可能会更改,请联系我 们的客服确认最新版本。 

## **3.** 支持版本 

#### 5.0.0(12)及以上 

## **4.** 备注 

这个手册介绍怎么通过 SDK 实现票据打印机的打印,常量定义在 TSPLPrinter 和 PrinterSDK 中。打印机分辨率为 200 dpi 时,1 mm=8 dot(点);打印机分辨率为 300 dpi 时,1 mm=12 dot(点)。 

## **5. PrinterSDK** 

### **5.1. createDevice** 

根据设备类型,创建设备。 

static createDevice(connectType: ConnectType): IDeviceConnect 

#### 【参数】 

  deviceType: number 

#### 设备类型 

|值|描述|
|---|---|
|USB|USB 类型|
|BLUETOOTH|蓝牙类型|
|ETHERNET|网络类型|

【返回值】 IDeviceConnect 连接的对象 

### **5.2. getUsbNames** 

获取 USB 路径列表 

static getUsbNames(): Array<string> static getUsbDevices(): Array<usbManager.USBDevice> 

【返回值】 

USB 设备路径列表或设备对象列表 

## **6. IDeviceConnect** 

### **6.1. connect** 

连接设备,连接失败时会抛出异常。 

connect(info: string): Promise<void> 

【参数】 

  info: string 连接信息。 设备类型为 USB 时,info 为 USB 路径名; 设备类型为 BLUETOOTH 时,info 为系统分配的蓝牙 id 设备类型为 ETHERNET 时,info 为打印机 ip 地址,或 IP 地址,端口号组合。 例:"192.168.1.100" 或 "192.168.1.100,9100" 

【返回值】 

Promise<void> 

错误码 **:** 

|错误码**ID**|描述|
|---|---|
|ERR_USB_DEVICE_ERR(-100)|找不到对应的USB 设备|

|ERR_USB_PERMISSION_DENIED(-101)|获取USB 权限失败|
|---|---|
|ERR_USB_TYPE_ERR(-102)|USB 设备类型错误|
|ERR_USB_OPEN_FAIL(-103)|连接USB 失败|
|其它|系统级别的异常|

### **6.2. sendData** 

此函数功能为向打印机发送数据。发送失败时,会抛出 PrintError 异常。 

sendData(data:Uint8Array): Promise<void> 

sendDatas(datas:List<Uint8Array>): Promise<void> 

【参数】 

  data:Uint8Array 

发送的字节数组 

  datas:List<Uint8Array> 发送的字节数组集合 

【返回值】 

Promise<void> 

#### 错误码 **:** 

|错误码**ID**|描述|
|---|---|
|ERR_CONNECT_DISCONNECTED(-200)|连接已经断开|
|其它|系统级别的异常|

### **6.3. getConnectInfo** 

获取连接信息。 

getConnectInfo():string 

【返回值】 

返回连接信息,对应的 connect 方法里面的 info 

### **6.4. readData** 

此函数功能为读取打印机的数据。超时时间为 3 秒。失败会抛 PrintError 异常 

readData(): Promise<Uint8Array> 

【返回值】 读取的数据数组 

#### 错误码 **:** 

|错误码**ID**|描述|
|---|---|
|ERR_CONNECT_DISCONNECTED(-200)|连接已经断开|
|ERR_READ_TIMEOUT|读取数据超时|
|其它|系统级别的异常|

### **6.5. close** 

此函数功能为关闭通讯。当不使用端口通讯时,请关闭端口。 

close() 

【返回值】 

void 

## **7. TSPLPrinter** 

### **7.1. constructor** 

构造函数,创建 TSPL 打印对象。 

constructor(connect: IDeviceConnect) 

【参数】 

  connect: IDeviceConnect 连接对象,可通过 PrinterSDK.createDevice(deviceType)获取。 

【返回值】 

TSPLPrinter 对象 

### **7.2. addSize** 

#### 设置标签尺寸。 

addSize(options: { width: number, height: number, unit?: SizeUnit }): TSPLPrinter 【参数】 

  width: number 尺寸宽度   height: number 尺寸高度   unit 

尺寸单位。默认为 SizeUnit.MILLIMETER(毫米) 

【返回值】 

TSPLPrinter 对象 

### **7.3. addGap** 

#### 定义两个标签间距 

addGap(options: { gapHeight: number, offset: number, unit?: SizeUnit }): TSPLPrinter 

【参数】 

  m: number 标签间隙高度   n: number 标签间隙高度的补偿值 

  unit 

尺寸单位。默认为 SizeUnit.MILLIMETER(毫米) 

【返回值】 TSPLPrinter 对象 

### **7.4. addSpeed** 

#### 设置打印速度 

addSpeed(options: { speed: number }): TSPLPrinter 

【参数】 

  speed: number 每秒的打印速度,以英寸计算。 

【返回值】 

TSPLPrinter 对象 

### **7.5. addDensity** 

#### 设置打印浓度 

addDensity(options: { density: number }): TSPLPrinter 

【参数】 

  density: number 

浓度, 范围【0, 15】 

【返回值】 

TSPLPrinter 对象 

### **7.6. addCls** 

清空打印缓冲区 addCls(): TSPLPrinter 

【返回值】 TSPLPrinter 对象 

### **7.7. addOffset** 

##### 定义标签于打印完后额外推出的长度 

addOffset(options: { offset: number, unit?: SizeUnit }): TSPLPrinter 

【参数】 

  offset: number 推出的长度,范围【-1, 1】(inch) 

  unit 尺寸单位。默认为 SizeUnit.MILLIMETER(毫米) 

【返回值】 

TSPLPrinter 对象 

### **7.8. addDirection** 

设置打印方向 

addDirection(options: { direction: FeedDirection, isMirror?: boolean }): TSPLPrinter 

【参数】 

  direction: number 打印的方向 

|变量|描述|
|---|---|
|DIRECTION_FORWARD|向前|
|DIRECTION_REVERSE|反向|

  isMirror: boolean 

是否镜像,默认为 false 

【返回值】 TSPLPrinter 对象 

### **7.9. addFeed** 

将标签纸推进对应的长度 

addFeed(options: { length: number }): TSPLPrinter 

【参数】 

  length: number 走纸长度,单位为点。范围【1,9999】 

【返回值】 

TSPLPrinter 对象 

### **7.10. addReference** 

#### 定义标签纸的原点坐标 

addReference(options: { x: number, y: number }): TSPLPrinter 

【参数】 

  x: number 水平坐标单位为点   y: number 垂直坐标,单位为点 

【返回值】 

TSPLPrinter 对象 

### **7.11. addBar** 

#### 绘制长条 

addBar(options: { x: number, y: number, width: number, height: number }): TSPLPrinter 

【参数】 

  x: number 长条起始横坐标,单位为点   y: number 长条起始纵坐标,单位为点 

- width: number 

长条宽度,单位为点   height: number 长条高度,单位为点 

【返回值】 TSPLPrinter 对象 

### **7.12. addBox** 

绘制矩形 

addBox(options: { x: number, y: number, width: number, height: number, thickness: number }): TSPLPrinter 

【参数】   x: number 矩形起始横坐标,单位为点   y: number 矩形起始纵坐标,单位为点   width: number 矩形宽度,单位为点   height: number 矩形高度,单位为点   thickness: number 线条宽度 【返回值】 TSPLPrinter 对象 

### **7.13. addBackFeed** 

将标签纸向后回拉指定的长度 addBackFeed(options: { length: number }): TSPLPrinter 

【参数】   length: number 回拉长度,单位为点。范围【1,9999】 

【返回值】 

TSPLPrinter 对象 

### **7.14. addFormFeed** 

将标签纸向前推送一张标签纸的距离 addFormFeed(): TSPLPrinter 

【返回值】 TSPLPrinter 对象 

### **7.15. addHome** 

对标签位置进行校准 addHome(): TSPLPrinter 

【返回值】 TSPLPrinter 对象 

### **7.16. print** 

加入打印指令,并且发送缓冲区的内容,清空缓冲区。 async print(options: { count?: number }): Promise<void> 

【参数】 

  count: number = 1 打印次数,默认为 1。 

【返回值】 

Promise<void> 

#### 错误码 **:** 

|错误码**ID**|描述|
|---|---|
|ERR_CONNECT_DISCONNECTED(-200)|连接已经断开|
|其它|系统级别的异常|

### **7.17. codePage** 

#### 设置国际代码页 

addCodePage(options: { page: string }): TSPLPrinter 

#### 【参数】 

  page: string 

#### 国际代码页 

|7-bit co|de page|8-|bit code page|Windo|ws code page|ISO cod|e page|
|---|---|---|---|---|---|---|---|
|page|Name|page|Name|page|Name|page|Name|
|**USA**|USA|**437**|United States|**1250**|Central Europe|**8859-1**|Latin 1|
|**BRI**|British|**737**|Greek|**1251**|Cyrillic|**8859-2**|Latin 2|
|**GER**|German|**850**|Multilingual|**1252**|Latin I|**8859-3**|Latin 3|
|**FRE**|French|**851**|Greek 1|**1253**|Greek|**8859-4**|Baltic|
|**DAN**|Danish|**852**|Slavic|**1254**|Turkish|**8859-5**|Cyrillic|
|**ITA**|Italian|**855**|Cyrillic|**1255**|Hebrew|**8859-6**|Arabic|
|**SPA**|Spanish|**857**|Turkish|**1256**|Arabic|**8859-7**|Greek|
|**SWE**|Swedish|**860**|Portuguese|**1257**|Baltic|**8859-8**|Hebre w|
|**SWI**|Swiss|**861**|Icelandic|**1258**|Vietnam|**8859-9**|Turkish|
|||**862**|Hebrew|**932**|Japanese Shift-JIS|**8859-10**|Latin 6|
|||**863**|Canadian/Frenc h|**936**|Simplified Chinese GBK|**8859-15**|Latin 9|
|||**864**|Arabic|**949**|Korean|||
|||**865**|Nordic|**950**|Traditional Chinese Big5|||
|||**866**|Russian|**UTF-8**|UTF 8|||
|||**869**|Greek 2|||||

#### 【返回值】 

TSPLPrinter 对象 

### **7.18. addSound** 

#### 控制蜂鸣器发声 

addSound(options: { level: number, interval: number }): TSPLPrinter 

【参数】 

  level: number 声音阶级,范围【0,9】 

- interval: number 

每次发声时间及两次发声的间隔时间,单位 ms。范围【1~4095】 

#### 【返回值】 

TSPLPrinter 对象 

### **7.19. addLimitFeed** 

限定间隙校正执行的最大长度,若在此长度范围内无法测得间隙存在,则将感应器模 式定在连续纸模式下。 

addLimitFeed(options: { length: number, unit?: SizeUnit }): TSPLPrinter 

【参数】 

  length: number 限定长度。 

  unit 尺寸单位。默认为 SizeUnit.MILLIMETER(毫米) 

【返回值】 

TSPLPrinter 对象 

### **7.20. addBarcode** 

绘制一维条码 

addBarcode(options: { 

x: number, y: number, codeType: BarcodeType, height: number, content: string, 

readable?: ReadablePosition, rotation?: PrinterRotation, narrow?: number, wide?: number }): TSPLPrinter 

【参数】 

  x: number 条码起始点横坐标,单位为点 

  y: number 条码起始点纵坐标,单位为点 

####   codeType: BarcodeType 条码类型 

|变量|描述|
|---|---|
|TYPE_128|Code 128, switching code subset automatically.|
|TYPE_128M|Code 128, switching code subset manually.|
|TYPE_EAN128|EAN128, switching code subset automatically.|
|TYPE_25|Interleaved 2 of 5.|
|TYPE_25C|Interleaved 2 of 5 with check digit.|
|TYPE_39|Code 39, switching standard and full ASCII mode automatically.|
|TYPE_39C|Code 39 with check digit.|
|TYPE_93|Code 93.|
|TYPE_EAN13|EAN 13.|
|TYPE_EAN13_2|EAN 13 with 2 digits add-on.|
|TYPE_EAN13_5|EAN 13 with 5 digits add-on.|
|TYPE_EAN8|EAN 8.|
|TYPE_EAN8_2|EAN 8 with 2 digits add-on.|
|TYPE_EAN8_5|EAN 8 with 5 digits add-on.|
|TYPE_CODA|Codabar.|
|TYPE_POST|Postnet.|
|TYPE_UPCA|UPC-A.|
|TYPE_UPCA_2|UPC-A with 2 digits add-on.|
|TYPE_UPCA_5|UPC-A with 5 digits add-on.|
|TYPE_UPCE|UPC-E.|
|TYPE_UPCE_2|UPC-E with 2 digits add-on.|
|TYPE_UPCE_5|UPC-E with 5 digits add-on.|
|TYPE_CPOST|China post.|
|TYPE_MSI|MSI.|
|TYPE_MSIC|MSI with check digit.|
|TYPE_PLESSEY|PLESSEY.|
|TYPE_ITF14|ITF14.|
|TYPE_EAN14|EAN14.|
|TYPE_11|Code 11.|
|TYPE_TELEPEN|Telepen.|
|TYPE_TELEPENN|Telepen number.|
|TYPE_PLANET|Planet.|
|TYPE_CODE49|Code 49.|
|TYPE_DPI|Deutsche Post Identcode.|

TYPE_DPL 

Deutsche Post Leitcode. 

####   height: number 

条码高度,单位为点 readable: ReadablePosition 

#### 是否打印可识别字符,默认 ReadablePosition.LEFT 

|变量|描述|
|---|---|
|NONE|不显示可识别字符|
|LEFT|显示在左边|
|CENTER|显示再中间|
|RIGHT|显示再右边|

####   rotation: PrinterRotation 

#### 顺时针旋转角度,默认 PrinterRotation.DEGREE_0 

|变量|描述|
|---|---|
|DEGREE_0|不旋转|
|DEGREE_90|顺时针旋转90度|
|DEGREE_180|顺时针旋转180度|
|DEGREE_270|顺时针旋转270度|

  narrow: number 

窄条码比例因子,单位为点,默认为 2 

  wide: number 

宽条码比例因子,单位为点,默认为 2 

  content: string 条码内容 

【返回值】 

TSPLPrinter 对象 

### **7.21. addBitmap** 

绘制图片 

async addBitmap(options: { image: image.ImageSource, x: number, y: number, mode?: BmpMode, cWidth: number }): Promise<TSPLPrinter> 

【参数】 

  x: number 图片起始横坐标 

- y: number 

- 图片起始纵坐标 

- mode: number 

绘制图片的方式 

- cWidth: BmpMode 

图片的打印宽度 

- image: image.ImageSource 

- 图片对象 

【返回值】 

Promise<TSPLPrinter> 

### **7.22. addQrcode** 

#### 绘制二维条码 

addQrcode(options: { x: number, y: number, cellWidth: number, rotation?: PrinterRotation, content: string, mode?: QrCodeMode, ecLevel?: ErrorCorrectionLevel, model?: QrCodeModel, mask?: string}): TSPLPrinter 

【参数】 

- x: number 

- 二维码起始横坐标 

- y: number 

- 二维码起始纵坐标 

- ecLevel: ErrorCorrectionLevel 

#### 错误纠正能力等级,默认为 ErrorCorrectionLevel.L 

|变量|描述|
|---|---|
|L|错误纠正能力等级L (7%)|
|M|错误纠正能力等级M (15%)|
|Q|错误纠正能力等级Q (25%)|
|H|错误纠正能力等级H (30%)|

####   cellWidth: number 

单元格大小,范围【1,10】 

- mode: string 

#### 生成编码模式, 默认为 QrCodeMode.AUTO 

|变量|描述|
|---|---|
|AUTO|自动生成编码|
|MANUAL|手动生成编码|

  rotation?: PrinterRotation 

#### 顺时针旋转角度,默认 DEGREE_0 

|变量|描述|
|---|---|
|DEGREE_0|不旋转|
|DEGREE_90|顺时针旋转90度|
|DEGREE_180|顺时针旋转180度|
|DEGREE_270|顺时针旋转270度|

####   model: QrCodeModel, 默认为 QrCodeModel.M1 

|变量|描述|
|---|---|
|M1|原始版本|
|M2|扩大版本(大部分的智能手机支持此版本)|

  mask?: string S0~S8, 默认为 S7 

  data: string 二维码资料内容 

【返回值】 TSPLPrinter 对象 

### **7.23. addText** 

绘制文本 

addText(options: {x: number, y: number, font: string, content: string, rotation?: PrinterRotation, xRatio?: number, yRatio?: number }): TSPLPrinter 【参数】 

  x: number 文本的起始 X 值 

  y: number 

文本的起始 y 值 

  font: string 

文本的字体类型 

|变量|描述|
|---|---|
|FNT_8_12|8 x 12英数字体|
|FNT_12_20|12 x 20英数字体|
|FNT_16_24|16 x 24英数字体|

|FNT_24_32|24 x 32英数字体|
|---|---|
|FNT_32_48|32 x 48英数字体|
|FNT_14_19|14 x 19英数字体OCR-B|
|FNT_14_25|14 x 25英数字体OCR-A|
|FNT_21_27|21 x 27英数字体OCR-B|
|FNT_SIMPLIFIED_CHINESE|简体中文24x24字体(GB码)|
|FNT_TRADITIONAL_CHINESE|繁体中文24x24字体(大五码)|
|FNT_KOREAN|韩文24x24字体(KS码)|

  rotation?: PrinterRotation 

顺时针旋转角度,默认 DEGREE_0 

|变量|描述|
|---|---|
|DEGREE_0|不旋转|
|DEGREE_90|顺时针旋转90度|
|DEGREE_180|顺时针旋转180度|
|DEGREE_270|顺时针旋转270度|

  xRatio: number = 1 文字横向放大倍数,范围【1,10】   yRatio: number = 1 字体纵向放大倍数,范围【1,10】 

  content: string 文本内容 

【返回值】 TSPLPrinter 对象 

### **7.24. addErase** 

#### 擦除指定区域的数据 

addErase(options: { x: number, y: number, width: number, height: number }): TSPLPrinter 

【参数】 

- x: number 

- 区域起始横坐标 

- y: number 

- 区域起始纵坐标 

- width: number 

区域宽度 

  height: number 区域高度 

【返回值】 TSPLPrinter 对象 

### **7.25. addReverse** 

#### 将指定区域的数据黑白反向显示 

addReverse(options: { x: number, y: number, width: number, height: number }): TSPLPrinter 

【参数】 

  x: number 区域起始横坐标   y: number 区域起始纵坐标   width: number 区域宽度   height: number 区域高度 

【返回值】 TSPLPrinter 对象 

### **7.26. addCut** 

切纸 

addCut(): TSPLPrinter 

【返回值】 

TSPLPrinter 对象 

### **7.27. setPeel** 

设定启动/关闭自动剥纸器功能。预设值为关闭状态,当此功能被开启时,打印机会在每 印完一张时即暂停,直到标签纸被取走后才会打印下一张标签。 

setPeel(options: { isOpen: boolean }): TSPLPrinter 

【参数】 

  isOpen: boolean true 开启自动剥纸器的功能 false 关闭自动剥纸器的功能 

【返回值】 TSPLPrinter 对象 

### **7.28. setTear** 

设定开启/关闭送纸至撕纸线的功能 setTear(options: { isOpen: boolean }): TSPLPrinter 

【参数】 

  isOpen: boolean true 标签打印结束时将送纸至撕纸位置 false 标签打印结束时会将标签起印点停留至打印线位置 

【返回值】 TSPLPrinter 对象 

### **7.29. setBline** 

设定黑标高度及使用者定义标签印完后标签额外送出的长度 setBline(options: { m: number, n: number, unit?: SizeUnit }): TSPLPrinter 

【参数】 

  m: number 黑标高度,范围:【0.1, 1】英尺或【2.54,25.4】毫米   n: number 额外送出纸张长度。范围【0, lable length】   unit 尺寸单位。默认为 SizeUnit.MILLIMETER(毫米) 

【返回值】 

TSPLPrinter 对象 

### **7.30. setCutter** 

此函数功能为设置切刀工作模式 

setCutter(options: { pieces: number }): TSPLPrinter 

【参数】 

  pieces: number 

切纸模式,0=关闭切刀功能;-1=打印任务结束后切纸;1-65535=打印多少张标签后切。 

### **7.31. putBmp** 

打印本地 BMP 格式的图片 

putBmp(options: { x: number, y: number, fileName: string }): TSPLPrinter 

【参数】 

  x: number 起始 x 值   y: number 起始 y 值   fileName: string 本地的 BMP 格式的文件名,包含后缀名。 

【返回值】 

TSPLPrinter 对象 

### **7.32. printerStatus** 

获取打印机状态 

async printerStatus(): Promise<number> 

【返回值】 

Promise<number>,打印机状态值。错误或超时,会抛出异常 

|status(HEX)|描述|
|---|---|
|00|正常|
|01|前盖开|

|02|卡纸|
|---|---|
|03|卡纸且前盖开|
|04|缺纸|
|05|缺纸且前盖开|
|08|无色带|
|09|无色带且前盖开|
|0A|无色带且卡纸|
|0B|无色带、卡纸且前盖开|
|0C|无色带、缺纸|
|0D|无色带、缺纸且前盖开|
|10|暂停|
|20|打印中|
|80|其他错误|

#### 异常错误码 **:** 

|错误码**ID**|描述|
|---|---|
|ERR_CONNECT_DISCONNECTED(-200)|连接已经断开|
|ERR_READ_TIMEOUT|读取数据超时|
|其它|系统级别的异常|

### **7.33. setCharSet** 

设置字符编码,默编码为“gbk” 

setCharset(charset: string) 

参数 **:** 

charset: string 编码类型名 

返回值 **:** 

void 

### **7.34. addToBuf** 

该方法用于添加指令数据到缓冲区 addToBuf(data: string): TSPLPrinter 

【参数】 

  data: string 需发送的字符串 【返回值】 TSPLPrinter 对象 

---

# 家用 Harmony SDK 指令开发手册.pdf

# 家用 **Harmony SDK** 指令开发手册 

### **1.0.4** 

(注:浏览时请使用 **PDF** 左侧导航栏) 

## **1.** 更新记录 

|版本|内容|编辑者|
|---|---|---|
|1.0.1|鸿蒙ESC SDK 初始版本|dan|
|1.0.2|支持鸿蒙NEXT 版本|dan|
|1.0.3|支持纯血版的ESC 指令|dan|
|1.0.4|支持家用T2W 和P83C 型号|dan|

## **2.** 手册信息 

本 SDK 手册提供了开发 Harmony 应用程序所需的接口信息。我们在不断地努力提高和升 级我们所有产品的功能与质量。之后,产品规格和用户手册的内容可能会更改,请联系我 们的客服确认最新版本。 

## **3.** 支持版本 

#### 5.0.0(12)及以上 

## **4.** 备注 

这个手册介绍怎么通过 SDK 实现票据打印机的打印,常量定义 PrinterSDK 中。打印机分辨 率为 200 dpi 时,1 mm=8 dot(点);打印机分辨率为 300 dpi 时,1 mm=12 dot(点)。 

## **5. PrinterSDK** 

### **5.1. createDevice** 

根据设备类型,创建设备。 

#### static createDevice(deviceType: number):IDeviceConnect 

【参数】 

  deviceType: number 设备类型,家用机型只支持蓝牙。 

|值|描述|
|---|---|
|DEVICE_TYPE_USB|USB 类型|
|DEVICE_TYPE_BLUETOOTH|蓝牙类型|
|DEVICE_TYPE_ETHERNET|网络类型|

【返回值】 IDeviceConnect 连接的对象 

### **5.2. getUsbNames** 

获取 USB 路径列表 

static getUsbNames(): Array<string> static getUsbDevices(): Array<usbManager.USBDevice> 

【返回值】 

USB 设备路径列表或设备对象列表 

## **6. IDeviceConnect** 

### **6.1. connect** 

连接设备,连接失败时会抛出异常。 

connect(info: string): Promise<void> 

【参数】 

  info: string 连接信息。 设备类型为 DEVICE_TYPE_USB 时,info 为 USB 路径名; 设备类型为 DEVICE_TYPE_BLUETOOTH 时,info 为系统分配的蓝牙 id 设备类型为 DEVICE_TYPE_ETHERNET 时,info 为打印机 ip 地址,或 IP 地址,端口号组合。 例:"192.168.1.100" 或 "192.168.1.100,9100" 

【返回值】 

Promise<void> 

错误码 **:** 

|错误码**ID**|描述|
|---|---|
|ERR_USB_DEVICE_ERR(-100)|找不到对应的USB 设备|
|ERR_USB_PERMISSION_DENIED(-101)|获取USB 权限失败|
|ERR_USB_TYPE_ERR(-102)|USB 设备类型错误|
|ERR_USB_OPEN_FAIL(-103)|连接USB 失败|
|其它|系统级别的异常|

### **6.2. sendData** 

此函数功能为向打印机发送数据。发送失败时,会抛出异常。 

sendData(data:Uint8Array): Promise<void> sendDatas(datas:List<Uint8Array>): Promise<void> 

【参数】 

- data:Uint8Array 

发送的字节数组 

- datas:List<Uint8Array> 

发送的字节数组集合 

#### 【返回值】 

Promise<void> 

#### 错误码 **:** 

|错误码**ID**|描述|
|---|---|
|ERR_CONNECT_DISCONNECTED(-200)|连接已经断开|
|其它|系统级别的异常|

### **6.3. getConnectInfo** 

获取连接信息。 

getConnectInfo():string 

【返回值】 

返回连接信息,对应的 connect 方法里面的 info 

### **6.4. readData** 

此函数功能为读取打印机的数据。超时时间为 3 秒 

readData(): Promise<Uint8Array> 

【返回值】 

读取的数据数组 

#### 错误码 **:** 

|错误码**ID**|描述|
|---|---|
|ERR_CONNECT_DISCONNECTED(-200)|连接已经断开|
|ERR_READ_TIMEOUT|读取数据超时|
|其它|系统级别的异常|

### **6.5. close** 

此函数功能为关闭通讯。当不使用端口通讯时,请关闭端口。 

close() 

【返回值】 

void 

### **6.6. setConnectionInterruptedListener** 

此函数用于监听连接断开。由于系统没有蓝牙断开回调,故发送异常时,SDK 才能通过异 常感知到连接断开。 

setConnectionInterruptedListener(callback: Callback<void>); 

【参数】 

  callback: Callback<void> 断开回调 

【返回值】 

void 

## **7. HomePrinter** 

### **7.1. constructor** 

构造函数,创建 HomePrinter 对象。 

constructor(connect: IDeviceConnect, printerModel: PrinterModel) 

#### 【参数】 

####   connect: IDeviceConnect 

连接对象,可通过 PrinterSDK.createDevice(deviceType)获取。 

  printerModel: PrinterModel 

打印机型号 

|值|描述|
|---|---|
|MEMOBIRD_T2W|MEMOBIRD T2W 连续纸|
|MEMOBIRD_T2W_MARK|MEMOBIRD T2W 黑标纸|
|P83C|P83C 连续纸|
|P83C_MARK|P83C 黑标纸|

【返回值】 

HomePrinter 对象 

### **7.2. setPrinterModel** 

设置打印机型号 

setPrinterModel(printerModel: PrinterModel) 

#### 【参数】 

- printerModel: PrinterModel 

- 打印机型号 

|值|描述|
|---|---|
|MEMOBIRD_T2W|MEMOBIRD T2W 连续纸|
|MEMOBIRD_T2W_MARK|MEMOBIRD T2W 黑标纸|
|P83C|P83C 连续纸|
|P83C_MARK|P83C 黑标纸|

【返回值】 

void 

### **7.3. setStateCallback** 

设置打印机状态监听 

setStateCallback(callback: Callback<HPrinterState>) 

#### 【参数】 

  callback: Callback<HPrinterState> 

监听的回调。HPrinterState 属性介绍如下: 

|属性|类型|描述|
|---|---|---|
|isCharging|boolean|是否充电中|
|isCoverOpen|boolean|是否开盖|
|isOutOfPaper|boolean|是否缺纸|
|isOverheating|boolean|是否过热|
|isBatteryLow|boolean|是否低电量|
|batteryLevel|number|电量百分比(0-100)|
|density|number|打印浓度(0-31)|
|speed|number|打印速度|
|isCarbonRibbonExhausted|boolean|是否碳带用尽|
|isPrintCancel|boolean|是否打印取消|

#### 【返回值】 

void 

### **7.4. configureWifi** 

给打印机配置 WiFi 

async configureWifi(ssid: string, password: string, callback: Callback<ConfigureWiFiResult>): Promise<void> 

【参数】 

  ssid: string WiFi 名 

  password: string WiFi 密码,密码可以为空。 

- callback: Callback<ConfigureWiFiResult> 

#### 配置 WiFi 结果回调 

|值|描述|
|---|---|
|CONFIG_WIFI_SUCCESS|配网成功|
|CONFIG_WIFI_FAILURE_OVERTIME|配网超时|
|CONFIG_WIFI_FAILURE_DEFAULT|配网失败密码错误|
|CONFIG_WIFI_FAILURE_NOT_FIND_AP|配网失败,找不到wifi|

#### 【返回值】 

Promise<void> 

### **7.5. setAutoOffTime** 

设置自动关机时间 

async setAutoOffTime(time: number): Promise<void> 

#### 【参数】 

####   time: number 

自动关机时间,单位为秒。0 为不自动关机,最小关机时间为 30 秒,如设置 1~30,打印机会 自动按照 30 处理 

#### 【返回值】 

Promise<void> 

### **7.6. getAutoOffTime** 

获取自动关机时间 

async getAutoOffTime(callback: Callback<HOffTimeMo>): Promise<void> 

#### 【参数】 

  callback: Callback<HOffTimeMo> 自动关机时间回调。HOffTimeMo 中的 offTime 属性为关机时间。0 为不自动关机。 

【返回值】 

Promise<void> 

### **7.7. getPrinterVersion** 

获取打印机版本 

async getPrinterVersion(callback: Callback<HVersionMo>): Promise<void> 

#### 【参数】 

####   callback: Callback<HVersionMo> 

打印机版本回调。HVersionMo 对象中的 versionInfo 为当前打印机版本。 

【返回值】 

Promise<void> 

### **7.8. updateFirmware** 

更新打印机固件 

async updateFirmware(path: string, progress: Callback<number>): Promise<void> 

#### 【参数】 

- path: string 

- 要升级的固件的应用程序沙盒路径或文件 URI 

- progress: Callback<number> 

更新进度回调。范围为 0~100. 100 表示更新成功 

【返回值】 

Promise<void> 

### **7.9. printBitmap** 

打印图片 

async printBitmap(options: HPrintBitmapOptions): Promise<void> 

#### 【参数】 

- image: image.ImageSource 

- 图片对象 

- cWidth: number 

打印宽度,图片超过打印宽度时会做等比例压缩处理 

- algorithm?: ImageAlgorithm 

- 图片处理算法. 默认为 ImageAlgorithm.IMG 

- thermalType?: ImageThermalType 

热敏类型.默认为 ImageThermalType.DIRECT 

- density: number 

打印浓度 

- isFirst: boolean 

是否是首页 

- isLast: boolean 

是否是最后一页 

  callback: Callback<HEventTaskMo> 

打印结果回调。回调介绍如下: 

|方法|描述|
|---|---|
|isApplySuccess(): boolean|申请任务是否成功|
|isApplyFailed(): boolean|是否申请任务失败|
|isExecuteCompleted(): boolean|打印任务是否完成|

【返回值】 

Promise<void> 

### **7.10. exit** 

退出打印,停止事件监听 

exit() 

【返回值】 

void 

### **7.11. addToBuf** 

该方法用于添加指令数据到缓冲区 

ddToBuf(data: Uint8Array): HomePrinter 

【参数】 

  data: Uint8Array 需发送的字节数组 

【返回值】 

TSPLPrinter 对象 

### **7.31. sendBuff** 

此函数功能为发送缓存中的数据。 

async sendBuff():Promise<void> 

【返回值】 Promise<void>
