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
