使用本 SDK 您需要先获取 SDK ,并在 DevEco Studio 中集成安装,安装 完成后按照 SDK 集成使用指南完成服务开通、密钥申请、参数配置等 步骤,详细使用步骤请参考 SDK 官网信息或联系技术支持人员。 

VPN SDK 提供 ArkTS 与 C 两种接口形式,分别对应 HAR 文件与 SO 文 件。 

使用 ArkTS 接口: 

ArrayVpn.har 是提供 VPN 服务的静态共享包。 

VpnSdkDemo 是接口引用示例。 

ArrayApi.ts 是接口原型。 

VpnError.ts 包含所有错误码。 

*ArrayVpn-App.har 将 ArrayVpn.har 中使用的系统 VPN 接口修改为三 方 VPN 接口,供集成者选用。 

# 使用 C 接口: 

libarrayvpn.so 是提供 VPN 服务的动态库。 

VpnSdk 是接口引用示例(编译方式:将 system 或 vpn 模块编译为 har ,添加到 VpnSdkDemo 中调用)。 

arrayapi.h 是接口原型。 

vpn_eror.h 包含所有错误码。 

集成 C SDK ,需要在回调中自行实现配置 VPN 虚拟网卡的操作。 

SDK 仅支持 arm64-v8a 设备。
