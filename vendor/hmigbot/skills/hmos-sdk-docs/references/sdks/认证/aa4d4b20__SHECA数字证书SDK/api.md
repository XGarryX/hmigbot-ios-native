@sheca/digit-cert SDK 集成指南 

SDK 说明 

SDK 版本: v1.0.0 

# SDK 文件包: 

# 工程配置 

# 参考 DEMO 工程目录按功能需要添加并安装依赖库。 

"dependencies": { "@tencent/mmkv": "2.0.0", "@ohos/axios": "2.2.0", "@sheca/cafeaturekit": "file:./libs/cafeaturekit.har", "etaslibrary": "file:./libs/etasLibrary.har", "@sheca/caifaa": "file:./libs/caifaa.har", "@sheca/shecaseckitservice": "file:./libs/shecaseckitservice.har", "@alipay/afservicesdk": "file:./libs/ afservicesdk-1.0.241118203225.har", "esldtsdk": "file:./libs/ esldtSDK.har", "@sheca/dyrzsdk_esliving": "file:./libs/ dyrzsdk_esliving.har", "@sheca/dyrzsdk_alipayauth": "file:./libs/ dyrzsdk_alipayauth.har", "@sheca/dyrzsdk": "file:./libs/dyrzsdk.har", "@sheca/cawebkit": "file:./libs/cawebkit.har" }, 

支付宝认证回调需要在 Entry 模块的 module.json 中配置如下 scheme 。 

// 支付宝授权登录 "querySchemes": [ "apmqpdispatch" ] 

# 业务场景接口 

通过 cawebkit 包的 FRYZTInterface 调用 

1. 初始化 SDK 

export enum CASDKType { unknow = 0, QYY = 1, // 企业云 SDK 

SMY = 2, // 市民云 SDK }   /// 初始化 SDK 类型 /// @param context UIContext 对象 function initSDKType(type: CASDKType) 

# 2. 加载场景 

/// 加载场景 /// @param context Context 对象 /// @param url 服 务地址 /// @param headers 页面请求头信息,企业云不需要,市民 云需要放 cookie /// @param params 业务参数 /// @param isCoordinateEncryptKey 是否协同加密 key /// @param callback 数 据回调 function loadScene(context: Context, url: string, headers: Record<string, Object> | undefined, params: Record<string, Object> | undefined, isCoordinateEncryptKey: boolean, callback: (data: Record<string, Object>) => void) 

# 3 业务回调 

/// 加载场景 loadScene 的 callback 参数 

# 证书功能接口 

通过 shecaseckitservice 包中的 ssksInstance 对象调用 

# 1. 证书基本项 

/// 获取证书基本项 /// @param cert 证书内容 /// @param itemNo SSKSCertItemNo 类型 function getCertItem(cert: string, itemNo: SSKSCertItemNo):string; 

# 2. 证书扩展项 

/// 获取证书扩展项 /// @param cert 证书内容 /// @param oid oid 编码 function getCertExtension(cert: string, oid: string): string; 

状态码 状态码 说明 

0 

成功 

50001 用户退出(点击) 60001 场景值为用证时:用户本机无证书
