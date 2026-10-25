# 鸿蒙银行卡 SDK 开发文档 

文档版本: 1.0.0 

起草时间: 2024 年 04 月 

文档修改记录: 

日期 修改说明 变更人 审核人 

2024-4-18 初稿( 1.0.0-2.5.5.0 ) 卫东东 

2024-7-3 

修改 

卫东东 

基本说明 

本开发包集成了支持各类银行卡(储蓄卡、信用卡)卡号、包括 15~19 位凸面数字、及平面数字的图片文件转数字字符的识别功 能;同时支持显示银行行名、行号、卡片名称、卡片类型、信用卡有 效日期相关信息。 

平台要求 

鸿蒙 os 

# 集成步骤(暂时只适配主工程集成) 

将 bankCardLibrary module 导入到工程中 

在 oh-package.json5 的 dependencies 添加依赖: 

"bankCardLibrary": "file:../bankCardLibrary" 

复制鸿蒙授权文件 authmodehar.lsc 到 bankCardLibrary/src/main/ resources/rawfile/bank 目录下 

替换开发码: Config.devcode 

# 主要类说明 

pages/Index.ets: 项目入口,视频识别、导入识别 

pages/CameraPage.ets: 相机页面 

camera/CameraServer.ets: 相机相关设置以及识别调用 

pages/ResultPage.ets: 结果显示页面 

识别服务设置: 

# 错误码说明 

- -10401 :授权文件未找到 

- -10601 :开发码错误 

- -10602 : bundleName 错误,与授权文件中绑定的信息不匹配 

-10603 :授权过期 

- -10604 :核心版本号错误 

- -10605 :项目名称错误 

- -10606 :公司名称错误 

-10608 :未找到 company_name 

-10610 :版本号文件未找到 

- -10611 :其他错误 

- -10612 :未匹配到授权类型 

- -10613 :非鸿蒙授权 

-10701 : libraryName 未找到 

# 其他可选功能说明 

Config.backCallback :自定义相机返回处理 Config.resultCallback :自定义处理扫描结果 Config.permissionCallback :自定义权限请求返回结果处理
