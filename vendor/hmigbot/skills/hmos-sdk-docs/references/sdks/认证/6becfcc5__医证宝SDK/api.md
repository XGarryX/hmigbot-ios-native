# 医证宝 sdk 接口文档 

版本: 

V1.0 编制: 

审核: 

批准: 

四川省数字证书认证管理中心有限公司 2025 年 05 月 

目录 

1 、 接入前配置 - 1 - 

1.1 、 包名配置 - 1 - 

2 、 Sdk 授权登录流程图 - 1 - 

3 、 鸿蒙文档 - 1 - 

3.1 、 sdk 说明 - 1 - 

3.2 、 SccaHealthUIKit 集成 - 2 - 

4 、 服务端接口文档 - 3 - 

4.1 、 接口鉴权 - 3 - 

4.2 、 接口设计 - 5 - 

接入前配置 

包名配置 

提供接入客户端, ios , android ,鸿蒙的包名,包名由运营认证在运 营中心配置 包名配置完,才能进行 sdk 人脸识别操作 

Sdk 授权登录流程图 

# 鸿蒙文档 

sdk 说明 

医证宝 harmonysdk 分为两个部分, SccaHealthKit 和 SccaHealthUIKit SccaHealthKit 医证宝 sdk 核心包,可以单独集成集成 

SccaHealthUIKit 医证宝 sdk 封装 UI 包,需要依赖 SccaHealthKit 

SccaHealthUIKit 集成 

# 1 、手动添加的依赖库 

SccaHealthUIKit.har 

# 2 、需要申请存储权限 

"requestPermissions":[ {"name":"ohos.permission.INTERNET"}, {"name":"ohos.permission.GET_NETWORK_INFO"}, {"name":"ohos.permission.SET_NETWORK_INFO"}, {"name":"ohos.permission.GET_BUNDLE_INFO"}, {"name":"ohos.permission.STORE_PERSISTENT_DATA"} ] 

# 3 、接入注意事项 

# 3.1 、当前版本需要项目路由模式为 Navigation 

3.2 、 UI 组件入口路由名称 HealthHomePage 

# 授权登录 

URL:pushPathByName 

功能描述:初始化服务 

参数说明: 

参数分类 

参数名 

参数类型 

是否比传 

参数说明 输入参数 

companyId 

String 是 应用 id manageIp String 是 管理端 ip managePort String 是 管理端端口号 serverIp String 是 服务端 ip serverPort String 是 服务端端口号 

httpsCode 

String 

是 

是否为 https1- 是 0- 否 

callbackRouterName String 

是 

# 成功回调 

返回参数格式类型 AuthResultModel classAuthResultModel{ signData:'';// 签名值 authCode:'';// 授权码 

} 

服务端接口文档 

接口鉴权 

通讯协议 

身份认证服务和应用系统基于 HTTPS 协议,报文格式定义如下: a )请求数据封装格式: application/json 

b )返回数据封装格式: application/json 

# c )请求和响应参数组成结构说明如下: 

接口请求和响应的均为 JSON 格式数据报文,数据报文由公共参数和 业务参数两部分构成,请求报文需要由应用系统使用 HMAC 签名算法 进行签名计算,支持 HMAC-SM3 的签名算法。 

请求方法和 URL 规则 

支持 HTTPSGETPOST 方法。 

—— 使用 GET 方法时,输入参数附加在请求的 URL 上,输出参数为 JSON 格式。 

# 示例如下: 

https://{ip:port}/open/{signature}?{paramkey}={paramValue} 

—— 使用 POST 方法时,输入和输出参数均采用 JSON 格式。 示例如下: 

https://{ip:port}/open/{signature} 

注: { 斜体 } 为可变内容域,是身份认证服务网络地址,下同。 

# 授权类别 

——trusted ,当前支持的授权类别必须经过验证签名。 

# 认证信息 

应用系统在与身份认证服务通讯时,应提供认证信息,用于鉴别其身 份。可以通过验证签名的方式鉴别各个接入的应用系统的身份。 

—— 身份认证服务向申请接入的应用系统分配的唯一 app_id 和 app_secret 。 

—— 通过接口传输数据时,调用方应通过 HMAC-SM3 算法对请求数据 进行加签计算。 

—— 开放接口采用 https 协议。 

公共参数放入请求头中进行传输,请求的 Header 中包含认证信息如 下: 

参数名 

参数类型 

参数说明 

app_id 

string 

接入应用系统 app_id, 由身份认证服务统一分配。 

signature 

string 

参数签名值,由分配 app_secret 和请求参数计算得出结果,采用 HEX 编码 

timestamp 

string 

请求发送的时间戳 (UnixTimestamp, 毫秒 ) 

nonce 

string 

请求随机数,每笔业务在一定时间内唯一 (2 分钟 ) 

签名值生成规则 : 

——JSON 提交 

a ) JSON 字符串后面拼接随机数 (nonce 对应值,随机数在前 ) 和时间戳 ( timestamp 对应值)得到字符串。 

b )将 a 得到的字符串进行 HMAC-SM3 运算,计算后将结果转换为 16 进制 ( 小写 ) ,即为签名信息,放入请求头 (signature) 中。 

# 状态信息 

身份认证服务 API 返回状态信息,状态信息包含字符形式的状态码和 状态描述。状态码见附录 A 的规定。 

# 回调数据 

因部分操作是异步操作,当异步操作完成后,身份认证服务向应用系 统的回调地址发送回调数据。回调数据格式: 

参数名 

参数类型 

参数说明 

result_code 

string 

结果码, 0 表示成功 

result_msg 

string 

结果描述 

success 

bool 

成功失败,成功: true ,失败: false 

body 

object 

响应内容 

回调数据样例: 

{ 

"result_code":"0", 

"result_msg":" 请求成功 ", 

"success":true, 

"body":{} 

} 

接口设计 

根据授权码和签名值获取登录信息 

URL:/open/auth/userInfo 请求方式 :POST 

功能描述:根据授权码和签名值获取登录信息 参数说明: 

参数分类 

参数名 

参数类型 

是否必传 

参数说明 输入参数 

authCode 

String 

是 

授权码 

signedData 

String 是 签名值 Success 返回值说明 参数分类 参数名 参数类型 是否必须 参数说明 返回对象 success Bool 是 true 成功 false 失败 result_msg String 是 提示信息 result_code 

Int 

是 0 成功其他失败 body Object 是 Body 对象 openId String 是 用户唯一标识 realName String 是 姓名 phoneNumber String 是 手机号
