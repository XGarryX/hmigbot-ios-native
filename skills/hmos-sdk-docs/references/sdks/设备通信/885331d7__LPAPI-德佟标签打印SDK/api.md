# 接口说明

## BLE蓝牙相关

### 1. 检查BLE功能是否可用(蓝牙开关、所需权限检测)

```
 readyEnvironment (callback?: ErrorCallback)
```

参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| callback | ErrorCallback | 否 | 蓝牙环境检测错误回调,通常为蓝牙开关、蓝牙权限异常。 |

### 2. 开始打印机扫描

```
 scanPrinters (params?: DzLPAPIScanParam)
```

参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| scanTime | number | 否 | 扫描时间,单位:毫秒, 默认10*1000 |
| deviceName | string | 否 | 需要匹配的设备名称 |
| deviceId | string | 否 | 需要匹配的设备ID |
| onScan | Callback<DzLPAPIPrinterInfo[]> | 否 | 扫描结果回调 |
| onScanFinish | Callback | 否 | 扫描结束回调 |
| onError | ErrorCallback | 否 | 扫描错误信息回调 |
| minRSSI | number | 否 | 需要忽略的信号强度 |
| trades | string | 否 | 行业限定, 可以是多个行业限定编码, 用英文分号分隔,示例说明: 1)行业编码不包含, 以英文减号为前缀并声明,比如:"- |

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
|  |  |  | D;-Y;...."; 2)行业编码包含,无符号前缀 或 英文加号为前缀并声明, 比如:"+D;Y;...."; |
| models | string | 否 | 型号限定, 可以是多个型号限定名称, 用英文分号分隔,示例说明: 1)型号名称不包含, 以英文减号为前缀并声明,比如:"- DP20S;-DT60S;...."; 2)型号名称包含,无符号前缀 或 英文加号为前缀并声明, 比如:"+DT60S;DT20S;...."; |

示例代码:

```
this.apiInstance.scanPrinters({
      scanTime: 15 * 1000,
      onError: (err: BusinessError) => {},
      onScan: (printers: DzLPAPIPrinterInfo[]) => {
         //todo your work
      },
      onScanFinish: () => {
        //todo your work
      }
});
```

### 3. 停止扫描

```
 stopScan ()
```

### 4. 获取扫描结果列表

```
 getScanPrinters ()
```

### 5. 连接打印机

```
 openPrinter (params: DzLPAPIConnectParam)
```

参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| deviceId | string | 是 | 蓝牙设备ID |
| onConnect | Callback<boolean> | 否 | 连接回调 |
| onDisconnect | Callback<void> | 否 | 断开连接回调 |

示例代码:

```
this.apiInstance.openPrinter({
      deviceId: "xxx",
      onConnect: (connect: boolean) => {
        if (connect) {
          // 真正意义上的连接成功
        } else {
          // 连接失败
        }
      },
      onDisconnect: () => {
        // 连接断开
      }
});
```

### 6. 断开已连接打印机

```
 closePrinter (callback?: Callback<void>)
```

参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| callback | Callback<void> | 否 | 断开连接回调 |

### 7. 是否已连接打印机

```
 isPrinterOpened(): boolean
```

### 8. 获取当前已连接打印机信息

```
 getPrinterInfo(): DzLPAPIPrinterInfo | undefined
```

## 标签绘制相关

### 1. 绘制文本

```
/**
 * 文字绘制指定自定义字体说明(限API20+):
 * 自定义字体注册有以下两种方式:
 * 一种是通过ArkUI的异步接口this.uiContext.getFont().registerFont注册,调用后立即绘制可能会导致自定
 * 另一种是直接调用字体引擎的fontCollection.loadFontSync接口来注册自定义字体到字体引擎。
 * 在直接调用字体引擎接口注册自定义字体时,fontCollection的实例需要是text.FontCollection.getGlobalI
 */
drawText(params: DzLPAPIDrawTextParam):boolean
```

DzLPAPIDrawTextParam 参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| text | string | 是 | 文本内容。 |
| x | number | 是 | 绘制的文本的起始点x坐标,单位:毫米。 |
| y | number | 是 | 绘制的文本的起始点y坐标,单位:毫米。 |
| width | number | 否 | 绘制文本显示宽度,单位:毫米。 |
| height | number | 否 | 绘制文本显示高度,单位:毫米。 |
| fontHeight | number | 否 | 绘制文本字体高度,单位:毫米, 默认3.20毫米。 |
| fontStyle | DzLPAPIFontStyle | 否 | 绘制文本字体样式,默认值: DzLPAPIFontStyle.REGULAR。 |
| fontName | string | 否 | 绘制文本自定义字体系列(限API20+), 默认:sans-serif。 |
| lineSpace | number | 否 | 绘制文本行间距,单位:毫米。 |
| wrapMode | DzLPAPIWrapMode | 否 | 文字换行模式,默认值: DzLPAPIWrapMode.CHAR。 |
| antiColor | boolean | 否 | 是否反色绘制,默认值:false。 |
| rotation | DzLPAPIRotate | 否 | 绘制元素旋转角度,默认值: DzLPAPIRotate.ANGLE 0。 _ |

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| horizontalAlignment | DzLPAPIAlignment | 否 | 绘制元素水平对齐方式,默认值: DzLPAPIAlignment.START。 |
| verticalAlignment | DzLPAPIAlignment | 否 | 绘制元素垂直对齐方式,默认值: DzLPAPIAlignment.START。 |

### 2. 绘制弧形文字

```
drawArcText(params: DzLPAPIDrawArcTextParam):boolean
```

DzLPAPIDrawArcTextParam 参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| text | string | 是 | 文本内容。 |
| x | number | 是 | 绘制的文本的起始点x坐标,单位:毫米。 |
| y | number | 是 | 绘制的文本的起始点y坐标,单位:毫米。 |
| width | number | 是 | 绘制显示区域宽度,单位:毫米。 |
| height | number | 是 | 绘制显示区域高度,单位:毫米。 |
| fontHeight | number | 否 | 绘制文本字体高度,单位:毫米。 |
| fontStyle | number | 否 | 绘制文本字体样式,可选值:0 正常(默认);1 粗体。 |
| fontName | string | 否 | 绘制文本自定义字体系列(限API20+),默认:sans- serif。 |
| lineWidth | number | 否 | 绘制文本弧形线条宽度,单位:毫米,默认0.25毫米。 |
| antiColor | boolean | 否 | 是否反色绘制,默认值:false。 |
| rotation | DzLPAPIRotate | 否 | 绘制元素旋转角度,默认值: DzLPAPIRotate.ANGLE 0。 _ |

### 3. 绘制线条

```
drawLine(params: DzLPAPIDrawLineParam):boolean
```

DzLPAPIDrawLineParam 参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| x1 | number | 是 | 绘制的线条的起始点X坐标,单位:毫米。 |
| y1 | number | 是 | 绘制的线条的起始点Y坐标,单位:毫米。 |
| x2 | number | 是 | 绘制的线条的结束点X坐标,单位:毫米。 |
| y2 | number | 是 | 绘制的线条的结束点Y坐标,单位:毫米。 |
| lineWidth | number | 否 | 绘制边框线条宽度,单位:毫米,默认0.5毫米。 |
| dashLens | number[] | 否 | 描述线段如何交替和线段间距长度的数组,单位:毫米。 |
| rotation | DzLPAPIRotate | 否 | 绘制元素旋转角度,默认值: DzLPAPIRotate.ANGLE 0。 _ |

### 4. 绘制直角矩形

```
drawRect(params: DzLPAPIDrawRectParam):boolean
```

DzLPAPIDrawRectParam 参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| x | number | 是 | 绘制矩形的起始点X坐标,单位:毫米。 |
| y | number | 是 | 绘制矩形的起始点Y坐标,单位:毫米。 |
| width | number | 是 | 绘制矩形区域的宽度,单位:毫米。 |
| height | number | 是 | 绘制矩形区域的高度,单位:毫米。 |
| lineWidth | number | 否 | 绘制矩形线条宽度,单位:毫米,默认0.5毫米。 |
| fill | boolean | 否 | 绘制区域是否填充,默认:false。 |
| color | string | 否 | 绘制区域填充颜色,通常为六位16进制颜色字符串。 |
| rotation | DzLPAPIRotate | 否 | 绘制元素旋转角度,默认值: DzLPAPIRotate.ANGLE 0。 _ |

### 5. 绘制圆角矩形

```
drawRoundRect(params: DzLPAPIDrawRoundRectParam):boolean
```

DzLPAPIDrawRoundRectParam 参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| x | number | 是 | 绘制圆角矩形的起始点X坐标,单位:毫米。 |
| y | number | 是 | 绘制圆角矩形的起始点Y坐标,单位:毫米。 |
| width | number | 是 | 绘制圆角矩形区域的宽度,单位:毫米。 |
| height | number | 是 | 绘制圆角矩形区域的高度,单位:毫米。 |
| radius | number | 是 | 绘制圆角矩形圆角宽度,单位:毫米。 |
| lineWidth | number | 否 | 绘制圆角矩形线条宽度,单位:毫米,默认0.5毫米。 |
| fill | boolean | 否 | 绘制区域是否填充,默认:false。 |
| color | string | 否 | 绘制区域填充颜色,通常为六位16进制颜色字符串。 |
| rotation | DzLPAPIRotate | 否 | 绘制元素旋转角度,默认值: DzLPAPIRotate.ANGLE 0。 _ |

### 6. 绘制圆形

```
drawCircle(params: DzLPAPIDrawCircleParam):boolean
```

DzLPAPIDrawCircleParam 参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| x | number | 是 | 绘制圆形的圆心起始点X坐标,单位:毫米。 |
| y | number | 是 | 绘制圆形的圆心起始点Y坐标,单位:毫米。 |
| radius | number | 是 | 绘制圆形半径,单位:毫米。 |
| width | number | 否 | 绘制圆形区域的宽度,单位:毫米。 |
| height | number | 否 | 绘制圆形区域的高度,单位:毫米。 |

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| lineWidth | number | 否 | 绘制圆形线条宽度,单位:毫米,默认0.5毫米。 |
| fill | boolean | 否 | 绘制区域是否填充,默认:false。 |
| color | string | 否 | 绘制区域填充颜色,通常为六位16进制颜色字符串。 |
| rotation | DzLPAPIRotate | 否 | 绘制元素旋转角度,默认值: DzLPAPIRotate.ANGLE 0。 _ |

### 7. 绘制椭圆

```
drawEllipse(params: DzLPAPIDrawRectParam):boolean
```

DzLPAPIDrawRectParam 参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| x | number | 是 | 绘制椭圆的起始点X坐标,单位:毫米。 |
| y | number | 是 | 绘制椭圆的起始点Y坐标,单位:毫米。 |
| width | number | 是 | 绘制椭圆区域的宽度,单位:毫米。 |
| height | number | 是 | 绘制椭圆区域的高度,单位:毫米。 |
| lineWidth | number | 否 | 绘制椭圆线条宽度,单位:毫米,默认0.5毫米。 |
| fill | boolean | 否 | 绘制区域是否填充,默认:false。 |
| color | string | 否 | 绘制区域填充颜色,通常为六位16进制颜色字符串。 |
| rotation | DzLPAPIRotate | 否 | 绘制元素旋转角度,默认值: DzLPAPIRotate.ANGLE 0。 _ |

### 8. 绘制图片

```
drawImage(params: DzLPAPIDrawImageParam):boolean
```

参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| image | ImageBitmap或PixelMap | 是 | 绘制的图像数据。 |
| x | number | 是 | 绘制图像的起始点x坐标,单位:毫米。 |
| y | number | 是 | 绘制图像的起始点y坐标,单位:毫米。 |
| width | number | 否 | 绘制图像显示宽度,单位:毫米。 |
| height | number | 否 | 绘制图像显示高度,单位:毫米。 |
| rotation | DzLPAPIRotate | 否 | 绘制元素旋转角度,默认值: DzLPAPIRotate.ANGLE 0。 _ |

### 9. 绘制条码

```
drawBarcode(params: DzLPAPIDrawBarcodeParam):boolean
```

DzLPAPIDrawBarcodeParam 参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| text | string | 是 | 条码文本内容。 |
| x | number | 是 | 绘制条码的起始点x坐标,单位:毫米。 |
| y | number | 是 | 绘制条码的起始点y坐标,单位:毫米。 |
| width | number | 否 | 绘制条码显示宽度,单位:毫米。 |
| height | number | 否 | 绘制条码显示高度,单位:毫米。 |
| barcodeType | DzLPAPIBarcodeType | 否 | 条码类型,默认DzBarcodeType.CODE128。 |
| fontHeight | number | 否 | 条码文本内容显示高度,单位:毫米, 默认2.30毫米。 |
| fontStyle | DzLPAPIFontStyle | 否 | 绘制文本字体样式,默认值: DzLPAPIFontStyle.REGULAR。 |
| fontName | string | 否 | 绘制文本自定义字体系列(限API20+),默认: sans-serif。 |

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| textAlignment | DzLPAPIAlignment | 否 | 条码文本内容水平对齐方式,,默认: DzLPAPIAlignment.CENTER。 |
| rotation | DzLPAPIRotate | 否 | 绘制元素旋转角度,默认值: DzLPAPIRotate.ANGLE 0。 _ |

### 10. 绘制二维码

```
drawQRCode(params: DzLPAPIDrawQRCodeParam):boolean
```

DzLPAPIDrawQRCodeParam 参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| text | string | 是 | 二维码文本内容。 |
| x | number | 是 | 绘制二维码的起始点x坐标,单位:毫米。 |
| y | number | 是 | 绘制二维码的起始点y坐标,单位:毫米。 |
| width | number | 是 | 绘制二维码显示宽度,单位:毫米。 |
| height | number | 否 | 绘制二维码显示高度,单位:毫米。 |
| rotation | DzLPAPIRotate | 否 | 绘制元素旋转角度,默认值:DzLPAPIRotate.ANGLE 0。 _ |

## 打印相关

### 1. 开始一个打印绘制任务

```
 startDraw (params?: DzLPAPIDrawParam):boolean
```

参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| labelWidth | number | 否 | 标签宽度,单位:毫米,默认40毫米。 |
| labelHeight | number | 否 | 标签高度,单位:毫米,默认30mm。 |
| background | ImageBitmap 或 PixelMap | 否 | 背景图,非打印模式下有效。 |

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| backgroundColor | string | 否 | 绘制背景色,非打印模式下有效, 通常为六位16进制颜色字符串,默认值: #FFFFFF。 |
| color | string | 否 | 绘制色,非打印模式下有效, 通常为六位16进制颜色字符串,默认值: #000000。 |
| printMode | boolean | 否 | 当前绘制任务是否是打印模式, 默认非打印模式。 |
| printOrientation | DzLPAPIRotate | 否 | 出纸方向,默认值: DzLPAPIRotate.ANGLE 0。 _ |

示例代码:

```
this.apiInstance.startDraw({
  labelWidth: 40,
  labelHeight: 30,
  printMode: true,
  printOrientation: 0
});
```

### 2. 获取打印绘制图像数据

```
 endDraw ():PixelMap | ImageData | undefined
```

示例代码:

```
/**
 * 当startDraw指定printMode为true时,返回的数据类型为可用于【打印】的ImageData图像数据;
 * 当startDraw指定printMode为false时,返回的数据类型为可用于【预览】的PixelMap图像数据
 */
this.apiInstance.endDraw();
```

### 3. 打印绘制图像数据

```
 printImageData (params: DzLPAPIPrintParam)
```

参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| imageData | ImageData | 是 | 创建绘制任务指定为打印模式时,调用endDraw() 方法返回的ImageData图像数据。 |
| onSuccess | Callback<void> | 否 | 打印成功回调。 |
| onFail | Callback<string> | 否 | 打印失败回调。 |

示例代码:

```
this.apiInstance.printImageData({
        imageData: imageData,
        onSuccess: () => {
          // 打印成功
        },
        onFail: (error: BusinessError) => {
          // 打印失败,失败原因:error.message
       }
});
```

## 打印设置相关

### 1. 设置打印机打印浓度

```
 setPrinterDarkness(value: number)
```

参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| value | number | 是 | 打印浓度,可选值:1(最淡)、2、3、4(较淡)、5、6(正常) ... 10(较浓)、11、12、13、14、15(最浓),默认随打印机设置。 |

### 2. 设置打印机打印速度

```
 setPrinterSpeed(value: number)
```

参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| value | number | 是 | 打印速度,可选值:1、2、3、4、5,默认随打印机设置。 |

### 3. 设置打印机纸张类型

```
 setPrinterGapType(value: number)
```

参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| value | number | 是 | 纸张间隔类型,可选值:0 小票纸;2 不干胶;3 卡纸;4 透明贴。 |

### 4. 设置打印机纸张间隔长度

```
 setPrinterGapLength(value: number)
```

参数说明:

| 参数 | 类型 | 必选 | 说明 |
|---|---|---|---|
| value | number | 是 | 纸张间隔长度,单位:毫米。 |

# 类型声明

## DzLPAPIPrinterInfo

打印机信息

| 参数 | 类型 | 说明 |
|---|---|---|
| deviceName | string | 打印机设备名称 |
| deviceId | string | 打印机设备ID |
| printerType | number | 打印机设备类型 |
| dpi | number | 打印精度 |
| width | number | 打印宽度 |
| factory | string | 厂商名称 |

| 参数 | 类型 | 说明 |
|---|---|---|
| mac | string | MAC 地址 |
| softVersion | string | 软件版本号 |
| hardVersion | string | 硬件版本号 |
| rssi | number | 蓝牙信号强度 |
| deviceRecord | ArrayBuffer | 蓝牙广播数据 |

## DzLPAPIBarcodeType

条码编码类型

| 键 | 值 |
|---|---|
| UPC A _ | 20 |
| UPC E _ | 21 |
| EAN13 | 22 |
| EAN8 | 23 |
| CODE39 | 24 |
| ITF25 | 25 |
| CODABAR | 26 |
| CODE93 | 27 |
| CODE128 | 28 |
| ISBN | 29 |
| ECODE39 | 30 |
| ITF14 | 31 |

## DzLPAPIRotate

绘制元素旋转角度枚举

| 键 | 值 | 说明 |
|---|---|---|
| ANGLE 0 _ | 0 | 不旋转 |
| ANGLE 90 _ | 90 | 顺时针旋转90度 |
| ANGLE 180 _ | 180 | 顺时针旋转180度 |
| ANGLE 270 _ | 270 | 逆时针旋转90度 |

## DzLPAPIAlignment

绘制内容对齐方式

| 键 | 值 | 说明 |
|---|---|---|
| START | 0 | 水平居左、垂直居上 |
| CENTER | 1 | 居中 |
| END | 2 | 水平居右、垂直居下 |
| SPACE | 3 | 等间距分隔 |

## DzLPAPIFontStyle

绘制文本内容字体风格

| 键 | 值 | 说明 |
|---|---|---|
| REGULAR | 0x00 | 常规 |
| BOLD | 0x01 | 粗体 |
| UNDERLINE | 0x04 | 下划线 |
| STRIKEOUT | 0x08 | 删除线 |

## DzLPAPIWrapMode

绘制文本内容文字换行模式

| 键 | 值 | 说明 |
|---|---|---|
| NONE | 0 | 不自动换行 |
| CHAR | 1 | 按字符换行 |
| WORD | 2 | 按词换行 |
