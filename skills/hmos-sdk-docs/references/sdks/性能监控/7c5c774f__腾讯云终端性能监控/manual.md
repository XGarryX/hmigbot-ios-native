腾讯云可观测平台 

# 鸿蒙应用场景 

最近更新时间:2024-10-10 15:12:51 

本文指导您使用鸿蒙 SDK 的集成与初始化。 

最低支持鸿蒙 SDK 5.0.0(API12),最低支持系统版本 NEXT.0.0.36。 

操作步骤
步骤一:SDK 下载

1. 配置鸿蒙三方仓库,执行以下命令。 

ohpm config set registry  https://ohpm.openharmony.cn/ohpm/

2. 下载安装。 

ohpm install qapmsdk@latest

1. 在 entry 根目录加入 QAPMPlugin.ts 文件,代码爆红可忽略,可能是 IDE 解析问题,不影响使用。 

2. 在 entry 模块的 hvigorfile.ts 中加入以下代码。 

// 引入QAPMPlugin依赖
import  QAPMPlugin  { } from './QAPMPlugin'
...
export default {
...
    plugins:[
// 加入插件
QAPMPlugin()
] /* Custom plugin to extend the functionality of Hvigor. */
...
}
...

鸿蒙端二次混淆 Har 包代码,可能会导致 SDK 运行异常。为了避免 SDK 包跟随业务代码混淆,而导致功能失效,建议业务侧在 hap 工程 下的混淆配置文件(obfuscation-rules.txt)中加入以下规则。 

-keep
./oh_modules/qapmsdk

版权所有:腾讯云计算(北京)有限责任公司 

第49 共75页 

腾讯云可观测平台 

1. 登录 腾讯云可观测平台 控制台,在终端性能监控页面 ,选择 应用管理 > 应用设置 后,获取 Appkey(上报 ID)。 

## 2. 拷贝下面代码,并修改其中部分字段。 

```arkts
import { QAPM } from 'qapmsdk' // 导入QAPM模块 import BuildProfile from 'BuildProfile'; // 引入BuildProfile,该文件编译时生成,可忽略报错 initQAPM(context: common.UIAbilityContext): void { // 初始化SDK QAPM.getInstance() .setContext(context)                         // 需要传入UIAbilityContext,必须 .setAppKey("your appkey")                         // 填写你的AppKey,必填,用于区分上报的产 品,该值由终端性能监控的产品配置页面获取,可参考前一步骤 .setUserId("userId")                              // 填写你的用户ID,选填,不填默认值为 USER_NOT_SET .setDeviceId("deviceId")                          // 填写设备ID,必填,应保证该值的唯一性 .setModel("model")                                // 填写设备类型,选填,不填默认值为 USER_NOT_SET,参考 deviceInfo.productModel .setLogLevel(QAPM.LogDebugLevel)                  // 设置日志等级,选填,开发阶段开启Debug, 线上请关闭 .setBuildId(BuildProfile.QAPM_UUID)               // 设置BuildId,选填,用于拉取被混淆堆栈的 mapping (若使用了QAPM符号表上传插件,可以直接使用该变量,否则请遵循UUID格式,自行传入该参数,请注意 UUID与一次构建是相互对应关系,为了区分不同的构建版本,建议每次构建更新该参数),该变量会在编译前生成,报 错信息可忽略,该设置如不填会影响后续堆栈翻译 .setHost("https://app.rumt-zh.com")               // 设置QAPM的外网上报域名,必填 “ ” .setCollectOptionalFields(true)                   // 为响应工信部 26号文 要求,提供该设置用 于告知SDK是否可以进行可选个人信息的采集,该设置需要最先配置,一旦设置则全局生效。默认可以采集,设置为 false则不采集,可能会影响到控制台的搜索、展示等。可选个人信息包括但不限于以下信息:设备制造商、系统、设备 型号等,详见 《QAPM SDK合规使用指南》 } // 启动QAPM startQAPM(): void { // 启动SDK 
```

版权所有:腾讯云计算(北京)有限责任公司 

第50 共75页 

腾讯云可观测平台 

QAPM.getInstance() 

.start(QAPM.ModeAll)                              // 开启所有功能,当前功能包含JsCrash、 CppCrash、AppFreeze } 

AppKey 可参考步骤四,在 终端性能监控 > 应用管理 > 应用设置 页面获取。 崩溃与 AppFreeze 分析均采用全量采集上报策略,不做采样处理。 

## 1. 检测 SDK 接入是否正常 

需要开启 QAPM 的日志等级为 Debug,启动 App,打开 Hilog,过滤 TAG 为 QAPM_,如出现以下日志代表接入成功。 

如出现 launch QAPM error, please check environment! 的错误,请检查 appkey 或者域名是否设置错误。 

如出现 no monitor turned on! 则可能是抽样未命中,请前往 终端性能监控 > 应用管理 > 白名单管理页面加入用户或者设备白名 单,日志中可搜索 user_id 或者 device_id 查看具体值。 

## 2. 我们在 SDK 中内嵌了一些崩溃测试 API,如下: 

调用 QAPM.getInstance().testJsCrash(),触发 Js 崩溃,下次启动时观察日志是否有[plugin::744]的上报。 

版权所有:腾讯云计算(北京)有限责任公司 

第51 共75页 

腾讯云可观测平台 

调用 QAPM.getInstance().testCppCrash(),触发 Cpp 崩溃,下次启动时观察日志是否有[plugin::746]的上报。 调用 QAPM.getInstance().testAppFreeze(),触发 AppFreeze,下次启动时观察日志是否有[plugin::740]的上报。 

版权所有:腾讯云计算(北京)有限责任公司 

第52 共75页 

腾讯云可观测平台 

# 控制台操作指南 

# 崩溃 

最近更新时间:2024-07-11 10:20:41 

终端性能监控通过对崩溃问题个例提取关键特征进行聚合,便于您针对 App 崩溃的根因分析。 

1. 登录 终端性能监控控制台 。 

2. 在左侧导航栏中选择崩溃,选择需要查看的业务系统、应用、时间范围等分析崩溃问题。 

多维分析

多维分析基于应用版本、崩溃类型、系统版本、设备类型、应用状态等多个维度分析关键指标,便于您聚焦的现象进行针对性的崩溃根因分 析。 

版权所有:腾讯云计算(北京)有限责任公司 

第53 共75页 

腾讯云可观测平台 

## 崩溃问题列表展示了所有设备的崩溃问题。您可以根据问题异常类型、问题设备 ID、特定函数或文件名快速筛选相关崩溃问题。您还可以单 击问题概述查看崩溃问题详情,定位分析崩溃根因。 

指标说明

## 相关指标说明如下表所示: 

|指标名称|指标说明|
|---|---|
|崩溃率|指定时间范围内崩溃发生次数/App 启动次数|
|崩溃用户率|指定时间范围内受到崩溃影响的用户数/启动 App 的用户数|
|崩溃次数|指定时间范围内崩溃发生次数|
|崩溃用户数|指定时间范围内受到崩溃影响的用户数|
|崩溃类型|按照崩溃问题发生位置将崩溃类型分类为 Java 崩溃与 Native 崩溃|
|SDK 启动次数|应用 SDK 启动次数|

版权所有:腾讯云计算(北京)有限责任公司 

第54 共75页
