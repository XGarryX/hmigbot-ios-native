# 鸿蒙地图SDK 开发文档V1.0

# 一.概述

腾讯地图 SDK 是一套基于 HarmonyOS NEXT Beta2 及以上版本设备的应用程序接口。通过统一

便捷的接口,您可以轻松使用腾讯地图服务,构建 LBS 应用程序。

腾讯地图地图SDK 提供地图能力,支持2D、3D 地图,地图旋转,3D 楼块等;开发者集成后可

快速构建专业的地图应用。

适用于对地图强依赖场景,如导航、打车、代驾等。也可用于可穿戴设备。

SDK 名称:腾讯地图地图SDK

开发者:深圳市腾讯计算机系统有限公司

版本:1.0.0

主要功能:基础地图、地图视野、地图控件、覆盖物、检索、地图事件、组件等

个人信息处理规则:腾讯隐私保护平台

使用说明:鸿蒙地图SDK | 腾讯位置服务

| 合规指南: | 合规指南 \| 腾讯位置服务 |
|---|---|

# 二.项目创建

## 工程配置

1.

安装 DevEco Studio 开发环境

 

手机HarmonyOS 系统:OpenHarmony-5.0.0.36(Beta3)及以上

 

DevEco Studio 版本:DevEco Studio NEXT Developer Beta2(Build Version: 5.0.3.500)及

以上

2.

获取key 与生成秘钥

获取key

        登录腾讯位置服务腾讯位置服务 - 立足生态,连接未来,未注册过账号可以注册成为腾讯位

置服务开发者:

       点击创建应用,设置应用名称和应用类型,点击创建:

生成秘钥

        填写KEY 名称、描述、阅读并同意使用条款等应用信息;

        勾选地图SDK 配置,可以设置appIdentifier,appIdentifier 要和App 一致;

        (注意:appIdentifier 不是必填,如果授权应用处空白,则使用该key 的所有应用均可以使

用;如果填写了具体的app,则只有填写的app 可以使用)

        使用检索功能需要勾选WebService API;

        点击添加生成KEY;

        获取AppIdentifier 的方法

```
  import { bundleManager } from '@kit.AbilityKit';
  /**
   * 获取appIdentifier:
   */
  public getBundleAppIdentifier(): string {
    // 根据给定的bundle 名称获取BundleInfo。
    // 使用此方法需要申请 ohos.permission.GET_BUNDLE_INFO权限。
    let bundleFlags =
bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_SIGNATURE_INFO;
    let appIdentifier = "";
    try {
      let bundleInfo =
bundleManager.getBundleInfoForSelfSync(bundleFlags)
      appIdentifier = bundleInfo.signatureInfo.appIdentifier;
      console.info('getBundleAppIdentifier successfully. Data: '
+ appIdentifier );
    } catch (error) {
      console.error('getBundleAppIdentifier failed:' +
error.message);
    }
    return appIdentifier;
  }
```

3.

安装依赖

cd [module 目录]

ohpm install @tencentmap/base

ohpm install @tencentmap/map

## 权限说明

```
"requestPermissions": [
    {
        "name": "ohos.permission.INTERNET"
    },
    {
        "name": "ohos.permission.GET_NETWORK_INFO"
    },
]
```

地图SDK 需要【互联网权限】与【获取数据网络信息】权限

# 三.地图创建

## 显示地图

只需3 步即可显示地图,效果图如下:

1.

引入地图组件对象

```
import { AuthService } from "@tencentmap/base"
import { MapComponent } from '@tencentmap/map'
```

2.

在创建地图前先设置key

```
AuthService.getInstance().setKey("your key");
```

3.

创建MapComponent

```
build() {
  MapComponent().width("100%").height("100%")
}
```

## 卫星地图

支持卫星图,效果如下:

```
private mapController: MapController | undefined
build() {
  MapComponent({
    onReady: (err: BusinessError, mapController: MapController)
=> {
      this.mapController = mapController
      this.mapController.setSatelliteEnabled(true);
    }
  }).width("100%").height("100%")
}
```

## 手势控制

地图组件手势可以通过开关控制是否启用

|  |  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|---|
|  | 类 |  |  | 接口 |  |  | 说明 |  |
|  |  |  |  |  |  |  |  |  |
| MapController |  |  |  | setMoveGestureEnable(enable: |  | 滑动开关开启或关闭 |  |  |
|  |  |  |  | boolean) |  |  |  |  |
|  |  |  |  |  |  |  |  |  |
|  | MapController |  |  | isMoveGestureEnable(): boolean |  |  | 获取滑动开关状态 |  |
|  |  |  |  |  |  |  |  |  |
| MapController |  |  |  | setPinchGestureEnable(enable: |  | 捏合开关开启或关闭 |  |  |
|  |  |  |  | boolean) |  |  |  |  |
|  |  |  |  |  |  |  |  |  |
|  | MapController |  |  | isPinchGestureEnable(): boolean |  |  | 获取捏合开关状态 |  |
|  |  |  |  |  |  |  |  |  |
|  | MapController |  |  | setSkewGestureEnable(enable: |  |  | 双指倾斜开关开启或关闭 |  |
|  |  |  |  |  |  |  |  |  |

|  |  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  | boolean) |  |  |  |  |
|  |  |  |  |  |  |  |  |  |
|  | MapController |  |  | isSkewGestureEnable(): boolean |  |  | 获取双指倾斜开关状态 |  |
|  |  |  |  |  |  |  |  |  |
| MapController |  |  |  | setRotatedGestureEnable(enable: |  | 双指旋转开关开启或关闭 |  |  |
|  |  |  |  | boolean) |  |  |  |  |
|  |  |  |  |  |  |  |  |  |
|  | MapController |  |  | isRotatedGestureEnable(): boolean |  |  | 获取双指旋转开关状态 |  |
|  |  |  |  |  |  |  |  |  |
| MapController |  |  |  | setDoubleTapByOneFingerGestureEn |  | 单指双击开关开启或关闭 |  |  |
|  |  |  |  | able(enable: boolean) |  |  |  |  |
|  |  |  |  |  |  |  |  |  |
| MapController |  |  |  | isDoubleTapByOneFingerGestureEna |  | 获取单指双击开关状态 |  |  |
|  |  |  |  | ble(): boolean |  |  |  |  |
|  |  |  |  |  |  |  |  |  |
| MapController |  |  |  | setSingleTapByTwoFingersGestureEn |  | 双指单击开关开启或关闭 |  |  |
|  |  |  |  | able |  |  |  |  |
|  |  |  |  |  |  |  |  |  |
| MapController |  |  |  | isSingleTapByTwoFingersGestureEna |  | 获取双指单击开关状态 |  |  |
|  |  |  |  | ble(): boolean |  |  |  |  |
|  |  |  |  |  |  |  |  |  |
| MapController |  |  |  | setAllGestureEnable(enable: |  | 设置所有手势开关 |  |  |
|  |  |  |  | boolean) |  |  |  |  |
|  |  |  |  |  |  |  |  |  |

示例代码

```
private mapController: MapController | undefined
build() {
  MapComponent({
    onReady: (err: BusinessError, mapController: MapController)
=> {
      this.mapController = mapController
      // 滑动开关
      this.mapController.setMoveGestureEnable(true);
      // 捏合开关
      this.mapController.setPinchGestureEnable(true);
      // 双指倾斜开关
      this.mapController.setSkewGestureEnable(true);
      // 双指旋转开关
      this.mapController.setRotatedGestureEnable(true);
      // 单指双击开关
this.mapController.setDoubleTapByOneFingerGestureEnable(true);
      // 双指单击开关
this.mapController.setSingleTapByTwoFingersGestureEnable(true);
      // 所有手势开关
      this.mapController.setAllGestureEnable(true);
    }
  }).width("100%").height("100%")
}
```

# 四.地图覆盖物

## 点标记

### 普通Marker

可以在地图上添加Marker 标记

效果图如下:

Marker 标记支持添加、更新、删除、点击事件

添加Marker

```
build() {
  MapComponent({
    onReady: (err: BusinessError, mapController: MapController)
=> {
      this.mapController = mapController
      this.marker = new Marker(
        {
          position: new LatLng(39.984186, 116.307503),
          icon: { uri: "rawfile://BLUE.png" },
          alpha: 1.0,
          rotate: 0,
          scaleX: 1.0,
          scaleY: 1.0,
          anchorX: 0.5,
          anchorY: 0.5
        }
      );
      this.mapController?.addMarker(this.marker)
    }
  }).width("100%").height("100%")
}
```

参数说明:

|  |  |  |  |  |  |
|---|---|---|---|---|---|
|  | 参数 |  |  | 说明 |  |
|  |  |  |  |  |  |
|  | position |  |  | 经纬度 |  |
|  |  |  |  |  |  |
|  | icon |  |  | 图片地址,资源位置相对于src/main/resources/rawfile/目录 |  |
|  |  |  |  |  |  |
|  | alpha |  |  | 透明度 0-1 |  |
|  |  |  |  |  |  |

|  |  |  |  |  |  |
|---|---|---|---|---|---|
|  | rotate |  |  | 旋转角度 0-360 |  |
|  |  |  |  |  |  |
|  | scaleX |  |  | X 方向缩放,默认1.0 |  |
|  |  |  |  |  |  |
|  | scaleY |  |  | Y 方向缩放,默认1.0 |  |
|  |  |  |  |  |  |
|  | anchorX |  |  | 锚点X,默认0.5 |  |
|  |  |  |  |  |  |
|  | anchorY |  |  | 锚点Y,默认0.5 |  |
|  |  |  |  |  |  |

更新Marker

```
this.mapController?.updateMarker(this.marker)
```

删除Marker

```
this.mapController?.removeMarker(this.marker)
```

设置点击事件

```
this.marker.setOnClickListener(() => {
  // do your work
})
```

### 带InfoWindow 的Marker

可以在地图上添加带InfoWindow 的Marker

效果图如下:

```
@State
private infoWindowInfo: InfoWindowInfo = new InfoWindowInfo();
```

2.

可以把任意Component 作为InfoWindow,比如示例中的Text。将Text 与

MapComponent 放到同一容器下,Text 需要设置id, visibility, position 3 个属性,其中

visibility 和position 属性固定设置为

```
.visibility(this.infoWindowInfo.visible ? Visibility.Visible :
Visibility.Hidden)
.position({ x: this.infoWindowInfo.x, y: this.infoWindowInfo.y })
```

3.

设置marker 的infoWindow 属性,关联第1 步的infoWindowInfo 对象和第2 步的id

```
this.marker.infoWindow = {
  componentId: "my_info_window",
  infoWindowInfo: this.infoWindowInfo,
  offsetX: 0,
  offsetY: 0
}
```

注:offsetX 和offsetY 可以调整infoWindow 的位置,单位像素(px)

完整示例如下:

```
this.marker.showInfoWindow()
this.makrer.hideInfoWindow()
```

更新、删除、点击事件

同普通Marker

## 绘制线

### 实线

可以在地图上添加线

效果图如下:

线支持添加、更新、删除、点击事件

添加实线

```
const points: Array<LatLng> = RandomUtils.randomLatLngArray();
this.line = new Line(
  {
    points: points,
    lineType: LineType.NormalLine,
    width: 30,
    borderWidth: 10,
    param: {
      segments: [{
        fromIndex: 0,
        toIndex: points.length - 1,
        color: "#ff0000",
        borderColor: "#00ff00"
      }],
    }
  }
);
this.mapController?.addLine(this.line);
```

参数说明:

|  |  |  |  |  |  |
|---|---|---|---|---|---|
|  | 参数 |  |  | 说明 |  |
|  |  |  |  |  |  |
|  | points |  |  | 经纬度点串 |  |
|  |  |  |  |  |  |
|  | lineType |  |  | 线的类型:NormalLine、DottedLine |  |
|  |  |  |  |  |  |
|  | width |  |  | 线的宽度,单位是像素(px) |  |
|  |  |  |  |  |  |
|  | borderWidth |  |  | 边框的宽度,单位是像素(px) |  |
|  |  |  |  |  |  |
|  | param |  |  | 线的详细参数,实线为NormalLineExtraParam,虚线为 |  |
|  |  |  |  |  |  |

|  |  |  |  |
|---|---|---|---|
|  |  | DottedLineExtraParam |  |
|  |  |  |  |

NormalLineExtraParam 参数说明

|  |  |  |  |  |  |
|---|---|---|---|---|---|
|  | 参数 |  |  | 说明 |  |
|  |  |  |  |  |  |
|  | segments |  |  | 路线段 |  |
|  |  |  |  |  |  |

Segment 参数说明

|  |  |  |  |  |  |
|---|---|---|---|---|---|
|  | 参数 |  |  | 说明 |  |
|  |  |  |  |  |  |
|  | color |  |  | 段颜色 |  |
|  |  |  |  |  |  |
|  | borderColor |  |  | 段边框颜色 |  |
|  |  |  |  |  |  |
|  | fromIndex |  |  | 段起始索引 |  |
|  |  |  |  |  |  |
|  | toIndex |  |  | 段终点索引 |  |
|  |  |  |  |  |  |

删除线

```
this.mapController?.removeLine(this.line);
```

更新线

```
this.mapController?.updateLine(this.line);
```

设置点击事件

```
this.line.setOnClickListener(()=>{
})
```

### 彩虹线

可以在地图上添加彩虹线

效果图如下:

彩虹线支持添加、更新、删除、点击事件

添加彩虹线

和实线使用方式基本一致,segments 参数分段设置多种颜色即可,以下是完整示例,4 个点,3

个段:

```
const points: Array<LatLng> = RandomUtils.randomLatLngArray(4);
this.line = new Line(
  {
    points: points,
    lineType: LineType.NormalLine,
    width: 30,
    borderWidth: 10,
    param: {
      segments: [
        {
          fromIndex: 0,
          toIndex: 1,
          color: "#ff0000",
          borderColor: "#00ff00"
        },
        {
          fromIndex: 1,
          toIndex: 2,
          color: "#fff3d127",
          borderColor: "#ff1e4a80"
        },
        {
          fromIndex: 2,
          toIndex: 3,
          color: "#ffe226cf",
          borderColor: "#ff232623"
        }
      ],
    }
  }
);
this.mapController?.addLine(this.line);
```

更新、删除、设置点击事件

同实线

### 虚线

可以在地图上添加虚线

效果图如下:

虚线支持添加、更新、删除、点击事件

添加虚线

1.

设置线的类型

```
lineType: LineType.DottedLine,
```

2.

设置虚线参数

```
param: {
  color: "#ff00ff",
  borderColor: "#ffff00",
  pattern: [1, 2, 3, 4]
}
```

完整示例

```
const points: Array<LatLng> = RandomUtils.randomLatLngArray(4);
this.line = new Line(
  {
    points: points,
    lineType: LineType.DottedLine,
    width: 30,
    borderWidth: 10,
    param: {
      color: "#ff00ff",
      borderColor: "#ffff00",
      pattern: [1, 2, 3, 4]
    }
  }
);
this.mapController?.addLine(this.line);
this.mapController?.moveCamera(points);
```

DottedLineExtraParam 参数说明

|  |  |  |  |  |  |
|---|---|---|---|---|---|
|  | 参数 |  |  | 说明 |  |
|  |  |  |  |  |  |
|  | color |  |  | 线的颜色 |  |
|  |  |  |  |  |  |
|  | borderColor |  |  | 边框颜色 |  |
|  |  |  |  |  |  |
| pattern |  |  |  | 虚线样式,偶数个,含义[实部长度1, 虚部长度1, 实部长度2, 虚 |  |
|  |  |  |  | 部长度2...],单位是像素(px) |  |
|  |  |  |  |  |  |

this.mapController?.addLine(this.line);

更新、删除、设置点击事件

同实线

多边形支持添加、更新、删除

添加多边形

```
const points = RandomUtils.randomLatLngArray(4)
this.polygon = new Polygon({
  points: points,
  fillColor: "#ff0000",
  strokeWidth: 12,
  strokeColor: "#ffff00",
  pattern: [10, 20, 30, 40],
  holes: undefined
})
this.mapController?.addPolygon(this.polygon);
```

参数说明

|  |  |  |  |  |  |
|---|---|---|---|---|---|
|  | 参数 |  |  | 说明 |  |
|  |  |  |  |  |  |
|  | points |  |  | 多边形点串 |  |
|  |  |  |  |  |  |
|  | fillColor |  |  | 填充色 |  |
|  |  |  |  |  |  |
|  | strokeWidth |  |  | 边框宽度,单位像素(px) |  |
|  |  |  |  |  |  |
|  | strokeColor |  |  | 边框颜色 |  |
|  |  |  |  |  |  |
| pattern |  |  |  | 虚线样式,偶数个,含义[实部长度1, 虚部长度1, 实部长度2, 虚 |  |
|  |  |  |  | 部长度2...],单位像素(px),不填默认是undefined,代表实线 |  |
|  |  |  |  |  |  |
|  | holes |  |  | 孔洞信息,不填写无孔洞 |  |
|  |  |  |  |  |  |

Hole 参数说明

```
this.mapController?.updatePolygon(this.polygon);
```

删除多边形

```
this.mapController?.removePolygon(this.polygon);
```

## 设置覆盖物显示隐藏

Marker、线、多边形支持设置显示隐藏控制及显示隐藏状态状态获取

设置显示隐藏

设置显示层级

```
this.mapController?.setZIndex(this.marker, 10)
this.mapController?.setZIndex(this.line, 14);
this.mapController?.setZIndex(this.polygon, 8)
```

zIndex 大的在上面

获取显示层级

```
this.mapController?.getZIndex(this.marker);
this.mapController?.getZIndex(this.line);
this.mapController?.getZIndex(this.polygon);
```

# 五.地图事件

## CameraChange 事件

可以监听地图的视野变化

效果图如下:

支持注册监听、注销监听

注册监听

1.

实现OnCameraChangeListener 接口并创建对象

```
private listener: OnCameraChangeListener = {
  onCameraChange: () => {
    this.message = "onCameraChange-" + (this.tag++);
  },
  onCameraChangeFinish: () => {
    this.message = "onCameraChangeFinish-" + (this.tag++);
  }
}
```

2.

注册监听

```
this.mapController?.addOnCameraChangeListener(this.listener);
```

onCameraChange:当调用接口或手势触发地图Camera 视野发生变化时,触发该回调(视野变

化中会持续回调)

onCameraChangeFinish:当地图Camera 视野变化完成时触发该回调

注销监听

```
this.mapController?.removeOnCameraChangeListener(this.listener);
```

## 手势事件

可以监听地图手势

效果图如下:

支持注册监听、注销监听

注册监听

1.

实现监听

```
private listener: GestureListener = {
  onSingleTap: (x: number, y: number) => {
    this.message = `onSingleTap x:${x.toFixed(2)}
y:${y.toFixed(2)}`
  },
  onDoubleTap: (x: number, y: number) => {
    this.message = `onDoubleTap x:${x.toFixed(2)}
y:${y.toFixed(2)}`
  }
}
```

2.

注册监听

```
this.mapController?.addGestureListener(this.listener);
```

onSingleTap:单击地图时触发,参数x, y 为屏幕坐标,单位像素(px),位置相对于

MapComponent(即MapComponent 左上角为(0,0),右下角为(MapComponent 宽,

MapComponent 高))

onDoubleTap:双击地图时触发,参数x, y 为屏幕坐标,单位像素(px),位置相对于

MapComponent(即MapComponent 左上角为(0,0),右下角为(MapComponent 宽,

MapComponent 高))

注销监听

|  |  |  |  |  |
|---|---|---|---|---|
|  |  |  | MapComponent 高)) |  |
|  |  |  |  |  |

示例代码

screenToGeo 示例

```
const geo = this.mapController.screenToGeo(x, y);
```

geoToScreen 示例

```
const screen = this.mapController.geoToScreen(lat, lng);
```

应用示例,在屏幕MapComponent 位置所在的4 个角和中心点各加一个marker

```
// 获取MapComponent 位置、大小等信息,"my-id"是你添加MapComponent 组件
```

时设置的id

```
const info = new ComponentUtils().getRectangleById("my-id");
const left = 0;
const top = 0;
const right = info.size.width;
const bottom = info.size.height;
// MapComponent 的4 个角和中心点各加一个marker
const points = [[left, top], [right, top], [left, bottom],
[right, bottom], [(left + right) / 2, (top + bottom) / 2]];
const iconUri = RandomUtils.randomMarkerIcon();
points.forEach((value) => {
  const geo = this.mapController.screenToGeo(value[0], value[1]);
  const marker = new Marker({
    position: geo,
    icon: { uri: iconUri }
  })
  this.mapController.addMarker(marker);
})
```

# 八.服务能力

## 地点搜索

| 地点搜索 PoiSearch 接口,封装了 | WebService API \| 腾讯位置服务 | 功能,更详细的接口描述可以 |
|---|---|---|

查阅官网。这里对 SDK 提供的地点搜索接口做简要描述。

使用步骤

1.

安装依赖 ohpm install @tencentmap/search

2.

设置secret key 若在控制台设置了SN 校验,会生成SecretKey (SK),用于请求地图

| WebServiceAPI 时计算签名,详见 | 常见问题 \| 腾讯位置服务 |
|---|---|

```
AuthService.getInstance().setSecretKey("your secret key");
```

3.

调用search 接口

```
const poiSearch = new PoiSearch();
poiSearch.search({
  keyword: "学校",
  boundary: "nearby(40.040589,116.273543,1000)",
  page_size: 10,
  page_index: 1,
  filter: "category=大学,中学",
  orderby: "_distance",
  added_fields: "category_code",
  get_subpois: 1,
}).then((result: PoiSearchResult | undefined) => {
  console.log("[search]" + JSON.stringify(result))
})
```

请求参数

|  |  |  |  |  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|---|---|---|---|
|  | 参数 |  |  | 必填 |  |  | 说明 |  |  | 示例 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |
| keyword |  |  | 是 |  |  |  | 搜索关键字,长度最大96 个字 |  | keyword=酒店,注意键值要 进行URL 编码(推荐 encodeURI),如 keyword=%e9%85%92%e5 %ba%97 |  |  |
|  |  |  |  |  |  |  | 节,注:keyword 仅支持检索一 |  |  |  |  |
|  |  |  |  |  |  |  | 个。 |  |  |  |  |
|  |  |  |  |  |  |  | (API 采用UTF-8 字符编码,1 |  |  |  |  |
|  |  |  |  |  |  |  | 个英文字符占用1 个字节, |  |  |  |  |
|  |  |  |  |  |  |  | 1 个中文字符占3 个字节,具体 |  |  |  |  |
|  |  |  |  |  |  |  | 请参阅相关技术资料) |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |  |

|  |  |  |  |  |  |
|---|---|---|---|---|---|
|  |  |  | 值 |  |  |
|  |  |  | 0 仅在当前城市搜索; |  |  |
|  |  |  | 1 [默认] 若当前城市搜索无结 |  |  |
|  |  |  | 果,则自动扩大范围; |  |  |
|  |  |  | 2 限制在当前区/县范围搜索,无 |  |  |
|  |  |  | 结果时不自动扩大范围(仅在传 |  |  |
|  |  |  | 入city name 为区级或区级行政 _ |  |  |
|  |  |  | 区划代码时有效)。 |  |  |
|  |  |  | lat,lng:[可选] 当keyword 使用 |  |  |
|  |  |  | 酒店、超市等泛分类关键词时, |  |  |
|  |  |  | 这类场景大多倾向于搜索附近, |  |  |
|  |  |  | 传入此经纬度,搜索结果会优先 |  |  |
|  |  |  | 就近地点,体验更优。格式顺序 |  |  |
|  |  |  | 为纬度在前,经度在后 |  |  |
|  |  |  |  |  |  |
| get subpoi _ s | 否 |  | 是否返回子地点,如大厦停车 |  | get subpois=1 _ |
|  |  |  | 场、出入口等取值: |  |  |
|  |  |  | 0 [默认]不返回 |  |  |
|  |  |  | 1 返回 |  |  |
|  |  |  |  |  |  |

返回结果

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | 名称 |  |  |  |  | 类型 |  |  | 必有 |  |  | 说明 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| status |  |  |  |  | number |  |  | 是 |  |  |  | 状态码,0 为正常,其它为异常,详细 |  |
|  |  |  |  |  |  |  |  |  |  |  |  | 请参阅状态码说明 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | message |  |  |  |  | string |  |  | 是 |  |  | 状态说明 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| count |  |  |  |  | number |  |  | 是 |  |  |  | 本次搜索结果总数,另外本服务限制 |  |
|  |  |  |  |  |  |  |  |  |  |  |  | 最多返回200 条数据(data), |  |
|  |  |  |  |  |  |  |  |  |  |  |  | 翻页(page index)超过搜索结果总 _ |  |
|  |  |  |  |  |  |  |  |  |  |  |  | 数返回空,未超过搜索总数但超过 |  |
|  |  |  |  |  |  |  |  |  |  |  |  | 200 条限制时,将返回最后一页数 |  |
|  |  |  |  |  |  |  |  |  |  |  |  | 据。 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| request id _ |  |  |  |  | string |  |  | 是 |  |  |  | 本次请求的唯一标识,由系统自动生 |  |
|  |  |  |  |  |  |  |  |  |  |  |  | 成,用于追查结果有异常时使用 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| data |  |  |  |  | array |  |  | 是 |  |  |  | 搜索结果POI(地点)数组,每项为 |  |
|  |  |  |  |  |  |  |  |  |  |  |  | 一个POI(地点)对象 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  | id |  |  | string |  |  | 是 |  |  | POI(地点)唯一标识 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  | title |  |  |  |  | string |  |  | 是 |  |  | POI(地点)名称 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | address |  |  |  |  | string |  |  | 是 |  |  | 地址 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | tel |  |  |  |  | string |  |  | 是 |  |  | 电话 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | category |  |  |  |  | string |  |  | 是 |  |  | POI(地点)分类 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | category code _ |  |  |  |  | number |  |  | 否 |  |  |  | POI(地点)分类编码,设置 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | added fields=category code 时返 _ _ |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 回 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | type |  |  |  |  | number |  |  | 是 |  |  |  | POI 类型,值说明:0:普通POI / 1:公 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 交车站 / 2:地铁站 / 3:公交线路 / 4:行 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 政区划 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | location |  |  |  |  | object |  |  | 是 |  |  | 坐标 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  | lat |  |  | number |  |  | 是 |  |  | 纬度 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  | lng |  |  | number |  |  | 是 |  |  | 经度 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | distance _ |  |  |  |  | number |  |  | 是 |  |  |  | 距离,单位: 米,在周边搜索、城市 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 范围搜索传入定位点时返回 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  | ad info _ |  |  |  |  | object |  |  | 是 |  |  | 行政区划信息 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  | adcode |  |  | number |  |  | 是 |  |  |  | 行政区划代码,详见:WebService |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | API \| 腾讯位置服务 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  | province |  |  | string |  |  | 是 |  |  | 省 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  | city |  |  | string |  |  | 是 |  |  |  | 市,如果当前城市为省直辖县级区 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 划,此字段会返回为空,由district 字 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 段返回。 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 注:省直辖县级区划adcode 第3 和 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 第4 位分别为9、0,如济源市 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | adcode 为419001 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  | district |  |  | string |  |  | 是 |  |  | 区 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| sub pois _ |  |  |  |  |  | array |  |  | 否 |  |  |  | 子地点列表,仅在输入参数 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | get subpois=1 时返回 _ |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | parent id _ |  |  |  |  | string |  |  | 是 |  |  | 主地点ID,对应data 中的地点ID |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | id |  |  |  |  | string |  |  | 是 |  |  | 地点唯一标识 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  | title |  |  |  |  | string |  |  | 是 |  |  | 地点名称 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | tel |  |  |  |  | string |  |  | 是 |  |  | 电话 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | category |  |  |  |  | string |  |  | 是 |  |  | POI(地点)分类 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | type |  |  |  |  | number |  |  | 是 |  |  |  | POI 类型,值说明:0:普通POI / 1:公 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 交车站 / 2:地铁站 / 3:公交线路 / 4:行 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 政区划 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | address |  |  |  |  | string |  |  | 是 |  |  | 地址 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | location |  |  |  |  | object |  |  | 是 |  |  | 坐标 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  | lat |  |  | number |  |  | 是 |  |  | 纬度 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  | lng |  |  | number |  |  | 是 |  |  | 经度 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | ad info _ |  |  |  |  | object |  |  | 是 |  |  | 行政区划信息 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  | adcode |  |  | number |  |  | 是 |  |  |  | 行政区划代码,详见:WebService |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | API \| 腾讯位置服务 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  | province |  |  | string |  |  | 是 |  |  | 省 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  | city |  |  | string |  |  | 是 |  |  |  | 市,如果当前城市为省直辖县级区 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 划,此字段会返回为空,由district 字 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 段返回。 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 注:省直辖县级区划adcode 第3 和 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 第4 位分别为9、0,如济源市 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | adcode 为419001 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  | district |  |  | string |  |  | 是 |  |  | 区 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| lin | es |  |  |  |  | array |  |  | 否 |  |  |  | 搜索公交线路数组,每项为一个公交 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  | 路线对象 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | id |  |  |  |  | string |  |  | 否 |  |  | 公交线路唯一标识 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | title |  |  |  |  | string |  |  | 否 |  |  | 公交线路名称 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | origin |  |  |  |  | object |  |  | 否 |  |  | 当前公交线路的始发站 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  | title |  |  | string |  |  | 否 |  |  | 始发站站点名称 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | destination |  |  |  |  | object |  |  | 否 |  |  | 当前公交线路的终点站 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  | title |  |  | string |  |  | 否 |  |  | 终点站站点名称 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

| lin | es |
|---|---|

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | region |  |  |  |  | object |  |  | 是 |  |  | POI 数据所属地区 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  | title |  |  | string |  |  | 是 |  |  | 所属地区名称 |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
