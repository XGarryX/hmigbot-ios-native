> 来源: ohpm 中央仓 README(T1 信源) | 包: `inodevpnsdk` | ohpm 最新版: 1.0.1 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 准入MC SDK使用说明<a name="ZH-CN_TOPIC_0000001115464207"></a>

## 简介<a name="section1470103520301"></a>

MC SDK是一款针对鸿蒙手机端完成的SSL VPN网络准入功能的开发工具,为了帮助开发者快速集成准入MC SDK,我们提供了一系列的接口使用,开发者按照需要集成sdk,调用功能接口完成VPN网络接入。  
本开发工具是基于Stage模型进行的开发集成,若SDK集成方采用FA模型,请尝试在功能对应的文件中做修改

## 具体实现
 连接VPN设备、VPN账号认证、创建VPN隧道、销毁VPN隧道,接口封装在linkAndLoginVPN(一键式接口)、vpnConnect、loginForV7、startVpn、stopVpn接口中,具体调用方式可参考《H3C iES Harmony SDK应用开发指导.docx》。

## 约束<a name="section18841871178"></a>
1. 安装应用示例之前,请确认应用示例是否为stage模型  
   若为Stage模型需要查看entry/src/main路径下的module.json5文件中的"deviceType"字段来确认该应用支持的设备类型   
   若为FA模型,查看entry/src/main路径下的config.json文件中的"deviceType"字段来确认该应用示例支持的设备类型  
   两种模型都可尝试通过修改该字段使其可以在相应类型的设备上运行
2. 应用集成方,集成MC SDK时,编译使用的SDK版本,须为18及以上

## 使用准备<a name="section17988202503116"></a>
1. 将MC SDK Har包放在工程的libs文件夹下,并在工程的oh-package.json5文件中,添加SDK的依赖
2. 需要在工程目录的entry\src\main\module.json5文件中,增加ohos.permission.INTERNET、ohos.permission.GET_WIFI_INFO、ohos.permission.GET_NETWORK_INFO权限  

## 下载
如需下载本har包,执行如下命令:

```
ohpm i inodevpnsdk
或
ohpm install inodevpnsdk
```

## Changlog<a name="section17988202503117"></a>

应用修改记录:[changelog](changelog.md)
