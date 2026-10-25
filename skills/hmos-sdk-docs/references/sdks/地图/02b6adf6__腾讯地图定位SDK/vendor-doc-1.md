> 来源: 厂商官方文档页(T2 信源) | https://lbs.qq.com/mobile/harmonyos-location-sdk/development-guide/overview | 抓取: 2026-07-17
> 注意: 单页快照,站内其余页面见来源链接

鸿蒙定位 SDK

开发指南

  * 概述
  * 接入指南
  * SDK 初始化
  * 核心类
  * 连续定位
  * 单次定位
  * 最后定位
  * 后台定位
  * 地理围栏
  * 辅助功能

[API 参考](https://mapapi.qq.com/sdk/locationSDK/HarmonyOS/api-reference/index.html)
* 下载
[合规说明](https://lbs.qq.com/complianceGuides/guides/sdkGuides/positionSdkComplianceGuide)

鸿蒙定位 SDK

开发指南

概述

# 概述

定位 SDK 是一套基于 HarmonyOS NEXT (API 12) 及以上版本设备的应用程序接口。通过统一便捷的接口,您可以轻松使用定位服务,构建 LBS 应用程序。

定位 SDK 包括 GPS 定位与网络定位,实现了经纬度坐标偏转与当前位置的 POI 名称、地址或者行政区划的查询。

SDK名称:腾讯地图定位 SDK

开发者:深圳市腾讯计算机系统有限公司

版本:1.1.0

主要功能:连续定位、单次定位、最后定位、后台定位、地理围栏、辅助功能等

个人信息处理规则:<https://privacy.qq.com/document/preview/dbd484ce652c486cb6d7e43ef12cefb0>

使用说明:<https://lbs.qq.com/mobile/harmonyos-location-sdk/development-guide/integration-guide>

合规指南:<https://lbs.qq.com/complianceGuides/guides/sdkGuides/positionSdkComplianceGuide>

  

  * 包名:@tencentmap/location_sdk
  * MD5:5ec9c4b0a709eabd2ab980f90843b53c

* * *

  

## 产品优势

### 性能稳定可靠

  * **日请求次数** :1800 亿+
  * **服务可靠性** :99.99%
  * **定位成功率** :99.2%

### 数据覆盖广泛

  * **Wi-Fi 数据** :19 亿
  * **基站数据** :2.3 亿
  * **日更新数据占比** :85%

### 轻量易集成

封装 HarmonyOS 系统定位能力,提供统一简洁的 API 接口,降低接入成本,助力开发者快速构建 LBS 应用。

## 主要功能

功能 | 说明  
---|---  
**连续定位** | 按设定的时间间隔持续获取位置更新,适用于轨迹记录、实时导航等场景  
**单次定位** | 快速获取一次当前位置后自动停止,适用于签到、定位搜索等轻量场景  
**最后定位** | 获取最后一次成功的定位结果,无需发起新的定位请求,响应速度快  
**后台定位** | 应用退至后台后持续获取位置信息,支持后台任务配置  
**地理围栏** | 设定圆形区域,当设备进出围栏时触发回调通知  
**辅助功能** | 提供两点距离计算、圆形区域判断等实用工具方法  
  
## 适用场景

  * **出行打车** :精准定位上车点和目的地,优化司乘匹配效率
  * **外卖配送** :实时追踪骑手位置,为用户提供配送进度展示
  * **运动健身** :记录跑步、骑行轨迹,提供平滑运动路线
  * **社交应用** :实现"附近的人"、实时位置分享等 LBS 社交功能
  * **智能硬件** :儿童手表、宠物追踪器等设备的持续定位与围栏告警
  * **物流追踪** :货物运输全程位置监控,结合地理围栏实现到站提醒

## 文档适用对象

本文档适合具有一定 HarmonyOS NEXT 开发经验并了解 ArkTS 语言的开发者。建议开发者对地图产品和 LBS 服务有基本了解。

## 兼容性

支持 HarmonyOS NEXT (API 12) 及以上版本。

试试AI总结 

不想看文档?直接问AI~ 

这篇文档对您是否有帮助? 

有帮助 

没帮助 

本页内容
