# 文鼎创蓝牙 Key SDK 使用指南 

深圳市文鼎创数据科技有限公司 版权所有 侵权必究 

All rights reserved 

产品模块列表 

序号 部件名称 产品信息 

1 

ESBankSdk 库 

部署方式:编译集成 

厂商提交 har : ESBankSdk.har 

2 

# 文鼎创蓝牙 Key 

厂商单独提供:已配置好 RSA 和 SM2 证书的蓝牙 Key 

# SDK 使用说明 

我司提供的 SDK 的使用方式是:静态集成 ESBankSdk.har ,以下是主 要步骤(更详细步骤请查看接入文档): 

"dependencies": { 

"es_banksdk": "file:./dependencies/ESBankSdk.har", 

} 

"dependencies": { 

"es_banksdk": "file:./dependencies/ESBankSdk.har", 

} 

将 ESBankSdk.har 放入工程对应目录下,并在对应 oh-package.json5 的 dependencies{} 中添加依赖。 

import { IUKeyInterface, ESBankBT_WD} from 'es_banksdk' 

let device: IUKeyInterface = ESBankBT_WD.getInstance(getContext(this)); 

import { IUKeyInterface, ESBankBT_WD} from 'es_banksdk' 

let device: IUKeyInterface = ESBankBT_WD.getInstance(getContext(this)); 

加载 SDK ,获取接口实例,示例代码如下: 

调用 device 接口实例的方法,使用相关功能。 

在 module.json5 中添加必要的权限 

{ 

"requestPermissions": [ 

{ 

"name": "ohos.permission.ACCESS_BLUETOOTH", 

"reason": " 用于蓝牙连接 Key" 

} 

] 

}
