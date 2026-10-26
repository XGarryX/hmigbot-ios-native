# 应用数据安全 SDK 

2024 年 11 月 

接口文档 V1.0 

# 版权申明 

“ ” 本文档版权归指掌易科技有限公司(以下简称 指掌易 )所有,并保 留一切权利,非经本公司书面许可任何单位和个人不得擅自摘抄、复 制本书内容的部分或者全部,并不得以任何形式进行传播。对应本文 档出现的其他公司的商标,产品标识和商品名称,由各自权利人拥 有。 

# 免责声明 

本文档仅供参考,指掌易不对其内容的准确性或适用性提供任何明示 或暗示的保证。用户需根据实际需求对 SDK 功能进行验证。如需获取 最新文档请联系指掌易科技有限公司。 

# 联系我们 

网址: www.zhizhangyi.com 

服务电话: 400 898 7798 

渠道合作: 13346475656 

地址:北京市朝阳区航空科技大厦 A 座 7 层 

# 目录 

# 1. SDK 接口说明 4 

2. 联系我们 4 

# SDK 接口说明 

初始化接口 

接口名称 

VsaSdk.init 

调用方式 

在 AbilityStage 的 onCreate 方法中调用 

请求参数 

stage: AbilityStage – 传入当前的 AbilityStage 对象 

返回参数 

无 

# 调用示例 

export default class MyAbilityStage extends AbilityStage { onCreate(): void { 

// 应用的 HAP 在首次加载的时,为该 Module 初始化操作 

VsaSdk.init(this); 

} 

# 错误码 

无 

# 应用内复制粘贴接口 

# 接口名称 

VsaSdk.beforeSetPasteboard 

调用方式 

# 在更新系统剪贴板之前调用 

请求参数 

pasteboardData: pasteboard.PasteData – 复制粘贴数据 

返回参数 

无 

# 调用示例 

let dataText = 'hello world'; 

let pasteData: pasteboard.PasteData = pasteboard.createData(pasteboard.MIMETYPE_TEXT_PLAIN, dataText); 

VsaSdk.beforeSetPasteboard(pasteData); 

pasteboard.getSystemPasteboard().setData(pasteData); 

错误码 

无 

# 联系我们 

北京指掌易科技有限公司 

地址:北京市朝阳区航空科技大厦 A 座 7 层 

服务电话: 400 898 7798 

网址: www.zhizhangyi.com
