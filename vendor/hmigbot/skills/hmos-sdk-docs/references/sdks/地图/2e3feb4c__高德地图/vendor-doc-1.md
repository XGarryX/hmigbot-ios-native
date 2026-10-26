> 来源: 厂商官方文档页(T2 信源) | https://lbs.amap.com/api/harmonyosnext-map3d-sdk/summary | 抓取: 2026-07-17
> 注意: 单页快照,站内其余页面见来源链接

HarmonyOS NEXT 地图SDK

  * [ 概述 ](/api/harmonyosnext-map3d-sdk/summary)
  * [ 入门指南 ](/api/harmonyosnext-map3d-sdk/gettingstarted)
  * 开发指南 __
    * [获取key](/api/harmonyosnext-map3d-sdk/guide/get-key)
    * [开发注意事项](/api/harmonyosnext-map3d-sdk/guide/dev-attention)
    * 创建地图
      * [显示地图](/api/harmonyosnext-map3d-sdk/guide/create-map/show-map)
      * [切换地图图层](/api/harmonyosnext-map3d-sdk/guide/create-map/satellite-map)
      * [显示定位蓝点](/api/harmonyosnext-map3d-sdk/guide/create-map/mylocation)
      * [显示室内地图](/api/harmonyosnext-map3d-sdk/guide/create-map/indoor)
      * [显示3D地形图](/api/harmonyosnext-map3d-sdk/guide/create-map/terrain)
      * [自定义地图](/api/harmonyosnext-map3d-sdk/guide/create-map/custom)
      * [显示英文地图](/api/harmonyosnext-map3d-sdk/guide/create-map/english-map)
      * [使用离线地图](/api/harmonyosnext-map3d-sdk/guide/create-map/offline-map)
      * [世界地图](/api/harmonyosnext-map3d-sdk/guide/create-map/world-map)
    * 在地图上绘制
      * [绘制点标记](/api/harmonyosnext-map3d-sdk/guide/draw-on-map/marker)
      * [绘制线](/api/harmonyosnext-map3d-sdk/guide/draw-on-map/polyline)
      * [绘制弧线](/api/harmonyosnext-map3d-sdk/guide/draw-on-map/arc)
      * [绘制面](/api/harmonyosnext-map3d-sdk/guide/draw-on-map/polygon)
      * [绘制图片图层](/api/harmonyosnext-map3d-sdk/guide/draw-on-map/groundoverlay)
      * [绘制海量点图层](/api/harmonyosnext-map3d-sdk/guide/draw-on-map/mass-points-overlay)
      * [点平滑移动](/api/harmonyosnext-map3d-sdk/guide/draw-on-map/smooth-move)
      * [绘制热力图](/api/harmonyosnext-map3d-sdk/guide/draw-on-map/draw-heatmap)
      * [绘制3D模型](/api/harmonyosnext-map3d-sdk/guide/draw-on-map/opengl)
      * [轨迹纠偏](/api/harmonyosnext-map3d-sdk/guide/draw-on-map/track-sdk)
    * 与地图交互
      * [控件交互](/api/harmonyosnext-map3d-sdk/guide/interaction-with-map/control-interaction)
      * [手势交互](/api/harmonyosnext-map3d-sdk/guide/interaction-with-map/gesture-interaction)
      * [调用方法交互](/api/harmonyosnext-map3d-sdk/guide/interaction-with-map/method-interaction)
      * [地图截屏功能](/api/harmonyosnext-map3d-sdk/guide/interaction-with-map/map-screenshot)
    * 获取地图数据
      * [获取POI数据](/api/harmonyosnext-map3d-sdk/guide/map-data/poi)
      * [获取地址描述数据](/api/harmonyosnext-map3d-sdk/guide/map-data/geo)
      * [获取行政区划数据](/api/harmonyosnext-map3d-sdk/guide/map-data/district)
      * [获取天气数据](/api/harmonyosnext-map3d-sdk/guide/map-data/weather)
      * [获取公交数据](/api/harmonyosnext-map3d-sdk/guide/map-data/amap-bus)
    * 出行路线规划
      * [驾车出行路线规划](/api/harmonyosnext-map3d-sdk/guide/route-plan/drive)
      * [步行出行路线规划](/api/harmonyosnext-map3d-sdk/guide/route-plan/walk)
      * [公交出行路线规划](/api/harmonyosnext-map3d-sdk/guide/route-plan/bus)
      * [骑行出行路线规划](/api/harmonyosnext-map3d-sdk/guide/route-plan/ride)
      * [货车出行路线规划](/api/harmonyosnext-map3d-sdk/guide/route-plan/truck)
      * [未来行程路线规划](/api/harmonyosnext-map3d-sdk/guide/route-plan/etd)
    * 地图计算工具
      * [坐标转换](/api/harmonyosnext-map3d-sdk/guide/computing-equipment/coordinate-transformation)
      * [距离测量](/api/harmonyosnext-map3d-sdk/guide/computing-equipment/distancesearch)
      * [距离/面积计算](/api/harmonyosnext-map3d-sdk/guide/computing-equipment/calcute-distance-tool)
  * [ 参考手册 ](https://a.amap.com/lbs-dev-yuntu/static/reference/harmonyosnext-sdk/map/docs/index.html)
  * [ 常见问题 ](/api/harmonyosnext-map3d-sdk/faq)
  * 更新日志 __
    * [3D 地图 SDK](/api/harmonyosnext-map3d-sdk/changelog/3d)
    * [搜索 SDK](/api/harmonyosnext-map3d-sdk/changelog/search)
  * [ 相关下载 ](/api/harmonyosnext-map3d-sdk/download-demo)

[开发](/api) __ HarmonyOS NEXT 地图SDK __ 概述

#  概述 最后更新时间: 2024年07月12日

## 地图SDK适配鸿蒙NEXT特性介绍

### 赋能开发者-提供地图鸿蒙原生ArkTS开发接口

  * 开发者可以使用鸿蒙NEXT推荐的ArkTS接口开发应用集成地图功能,组件使用ArkUI原生组件,兼容方舟UI框架

  * 代码全面适配鸿蒙NEXTSDK,所有系统接口均使用鸿蒙NEXTAPI。

### 接口易用性-最大程度的保证和Android/鸿蒙历史版本的接口的一致性

  * 接口设计最大程度的保证和之前android/鸿蒙历史版本接口的架构的一致性,方便开发者能够快速接入使用。

[ 返回顶部 ](javascript:void\(0\);)[ 示例中心 ](/demo/center)[ 常见问题 ](/faq)[ 智能客服 ](javascript:void\(0\))[ 公众号  
二维码 ](javascript:void\(0\))
