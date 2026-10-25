#### 认证服务开发指南 

文档版本 

01 

发布日期 

2026-05-08 

华为终端有限公司 

版权所有 © 华为终端有限公司 2026 。 保留一切权利。 

本材料所载内容受著作权法的保护,著作权由华为公司或其许可人拥 有,但注明引用其他方的内容除外。未经华为公司或其许可人事先书 面许可,任何人不得将本材料中的任何内容以任何方式进行复制、经 销、翻印、播放、以超级链路连接或传送、存储于信息检索系统或者 其他任何商业目的的使用。 

商标声明 

、、、华为,以上为华为公司的商标(非详尽清单),未经华为公司 书面事先明示许可,任何第三方不得以任何形式使用。 

#### 注意 

华为会不定期对本文档的内容进行更新。 

本文档仅作为使用指导,文档中的所有陈述、信息和建议不构成任何 明示或暗示的担保。 

华为终端有限公司 

地址: 

广东省东莞市松山湖园区新城路 2 号 

网址: 

https://consumer.huawei.com 

目 录 

- 1 认证服务 1 

1.1 业务介绍 2 

1.2 典型应用场景 5 

1.3 计费说明 8 

1.4 使用限制 8 

1.5 SDK 版本更新说明 9 

1.6 开发流程 10 

1.7 开发准备 11 

1.7.1 开通服务 11 

1.7.2 启用认证方式 11 

1.7.3 (可选)安全配置 21 

1.7.4 获取 SDK 配置信息 23 

1.8 集成 SDK 24 

1.9 登录 29 

1.9.1 手机号码 29 

1.9.2 邮箱 35 

1.9.3 华为账号 41 1.9.4 自有账号 45 1.9.5 匿名账号 46 1.9.6 关联账号 47 

1.10 登出 50 

1.11 销户 51 

1.12 账号重认证 52 

1.13 异常处理 52 

1.14 通过云函数扩展 53 

1.15 用量统计 55 

1.16 管理用户 55 

1.17 FAQ 57 

- 1.18 技术支持 57 

- 1.19 SDK 隐私声明 57 

- 1.20 SDK 合规使用指南 59 

# 认证服务 

- 1.1 业务介绍 

- 1.2 典型应用场景 

- 1.3 计费说明 

- 1.4 使用限制 

- 1.5 SDK 版本更新说明 

- 1.6 开发流程 

- 1.7 开发准备 

- 1.8 集成 SDK 

- 1.9 登录 

- 1.10 登出 

- 1.11 销户 

- 1.12 账号重认证 

- 1.13 异常处理 

- 1.14 通过云函数扩展 

- 1.15 用量统计 

1.16 管理用户 

1.17 FAQ 

1.18 技术支持 

- 1.19 SDK 隐私声明 

1.20 SDK 合规使用指南 

## 业务介绍 

认证服务能为您的应用迅速搭建起安全可靠的用户认证系统,您只需 在应用中调用认证服务的相关功能,无需担心云侧的设施和实现细 节。认证服务提供了 SDK 和后端支持,内置多种认证方式,配备强大 的管理平台,让您可以轻松完成用户认证的开发与管理工作。 

了解更多信息: 

1.2 典型应用场景 

#### 1.4 使用限制 

认证服务与华为账号服务的区别和关系? 

主要功能 

您可以通过在应用中集成认证服务 SDK 来轻松快速地向您的用户推出 注册、登录等相关功能。您可以选择向您的用户提供以下一种或多种 认证方式。 

1.9.1 手机号码 

“ 通过手机号码来对用户进行身份认证,您的用户可以使用 手机号码 + 密码 ” 或者 “ 手机号码 + 验证码 ” 方式来登录您的应用。 

认证服务提供了基于手机号码的注册、登录、密码修改、密码重置、 验证短信推送等能力和接口。 

1.9.2 邮箱 

通过邮箱地址来对用户进行身份认证,您的用户可以使用邮箱地址和 密码或者邮箱地址和验证码来登录您的应用。 

认证服务提供了基于邮箱地址的注册、登录、密码修改、密码重置、 验证邮件推送等能力和接口。 

#### 1.9.3 华为账号 

通过华为账号来对用户进行身份认证。您的用户可以使用华为账号和 密码来登录您的应用。 

#### 1.9.4 自有账号 

如果您已经自行构建了认证系统,您可以通过自有账号对接让您已构 建的认证系统与认证服务协同工作,比如:让认证服务来提供您的自 有认证系统所不具备的认证方式。 

#### 1.9.5 匿名账号 

匿名账号支持应用的游客访问模式。认证服务可以为您的游客分配用 户标识,使您能够识别不同的游客并为他们提供差异化的服务。游客 可通过关联其他认证方式来转化成为正式用户,并保留其原来的用户 标识不变,以使其业务保持连贯。 

#### 注意 

中国大陆地区游戏不支持匿名登录。 

#### 1.9.6 关联账号 

您可以将身份验证提供方凭据关联至现有用户账号,允许用户使用多 个身份验证提供方服务登录您的应用。无论用户使用哪个身份验证提 供方服务登录,均可通过同一 AppGallery Connect 用户 ID 识别用户。 

如果您的游戏集成华为联运服务,请遵守与华为游戏联运有关账号的 相关约定,请参见联运游戏开发。 

#### 工作原理 

系统上下文 

认证服务提供了 SDK ,您可以在应用中集成认证服务 SDK ,以便您访 问认证服务提供的各项能力。 

认证服务提供了控制台,您的开发和运营人员可以在控制台上配置认 证服务和管理用户。 

如果您向用户提供华为账号认证方式,那么认证服务会帮助您的应用 完成在云侧与第三方认证系统的交互。 

登录流程 

获取认证凭据。 

认证方式不同,其认证凭据的获取方式也不相同。 

对于手机账号,认证凭据是用户的手机号码和密码或者手机号码和验 证码。 

对于邮箱账号,认证凭据是用户的邮箱地址和密码或者邮箱地址和验 证码。 

对于华为账号,认证凭据是第三方认证服务颁发的 OAuth 令牌。 

对于匿名账号,认证凭据是认证服务 SDK 为该应用安装实例生成的唯 一标识。 

对于自有账号,认证凭据是您已有认证系统通过 Server SDK 生成的 Token 。 

上报认证凭据。 

应用将认证凭据通过认证服务 SDK 上报给认证服务。 

验证认证凭据。 

认证服务对认证凭据进行验证。 

返回认证结果。 

认证服务将认证结果返回给应用。此时: 

应用可以访问和维护该用户的基本个人资料信息(昵称、头像等)。 

应用可以访问和操作其他 Serverless 服务中的受安全规则保护的数 据,参见认证服务与 Serverless 。 

认证服务与云开发服务 

您可以单独使用认证服务,也可以配套云开发服务一起使用。 

认证服务为云函数、云数据库、云存储等服务提供了全面且自适应的 安全支撑,可令您对用户数据的保护事半功倍。配合认证服务: 

您可以直接从云函数的参数中获取用户信息并在您的函数逻辑中使用 它。 

您也可以在云数据库和云存储中直接基于用户信息来编辑安全规则, 实现基于用户和用户属性的数据和文件访问安全控制。 

实现流程 

序号 

步骤 

详情 

1 

启用认证方式 

在认证服务控制台启用您想要支持的认证方式,并按照界面引导提供 必要的配置信息。 

对于华为账号认证,需要提供在第三方认证系统中申请的应用标识及 秘钥。 

2 

在应用客户端实现登录界面流程 

在应用客户端代码中实现用户登录所需的界面流程: 

对于手机账号和邮箱账号认证,请实现用户输入账号信息、密码或者 

验证码信息界面流程,并且实现注册、登录、密码修改、密码重置、 验证码推送等流程。 

对于华为账号认证,需要按照第三方认证系统的要求实现登录界面流 程。 

对于匿名账号认证,您需要帮助或引导游客完成匿名登录。 

对于自有账号认证,您可以保持您原有的登录体验,并在流程中增加 认证服务所需 Token 的生成和传递。 

3 

端侧集成认证服务 SDK 

在应用的端侧代码中集成认证服务 SDK ,并通过认证服务 SDK 上报认 证凭据、接收认证结果。 

## 典型应用场景 

向用户提供多种登录方式 

认证方式可以支撑您的应用向用户提供多种登录方式,并允许用户关 联多种账号,无论用户采用何种方式登录,都能获得统一的身份和业 务体验。 

通过认证服务来构建相关能力,相比传统开发模式,可以大幅降低您 的工作量 。 

#### 验证码方式登录 

为了消除用户经常忘记密码的困扰,您可以向用户提供验证码登录方 式。用户无需录入密码,只需要获取并提交验证码即可完成登录。 

认证服务的手机账号和邮箱账号都提供了验证码的支撑。对于发往中 国大陆的手机验证 / 通知短信,您需要自行购买第三方短信服务完成 发送,认证服务可对接您提供的短信发送接口,来进行后续短信的正 常下发。对于邮箱验证邮件,您无需自行对接邮箱代理,认证服务会 

帮您完成验证邮件的发送。认证服务内置了 78 种语言的验证邮件模 板,能够根据用户设备的语言自动匹配邮件语言。 

#### 游客模式 

您可以为您的应用提供游客模式,以便降低用户的访问门槛,提升您 的用户转化率。用户不必注册和登录即可访问应用的部分内容,仅当 用户在应用内进行特定操作、访问特定内容或者触发您设定的特定限 制时才引导用户进行注册和登录。 

您可以方便地使用认证服务的匿名账号来实现这一场景。当用户选择 游客模式时,您为用户进行匿名登录,此时用户会隐式注册成为一个 匿名用户。当匿名用户改用其他登录方式登录应用时,您可以将其他 登录账号关联到匿名用户,以便匿名用户转化为正式用户,正式用户 会继承匿名用户的用户标识,以确保其业务连贯。 

## 计费说明 

免费。 

认证服务中国站已不再支持发送手机验证码 / 通知短信,不涉及短信 费用。 

## 使用限制 

本章节将为您详细介绍认证服务不同类型的限制。这些限制可能会根 据实际情况随时更新,请您注意文档变化。 

电话号码验证码限额 

操作 

限额 

#### 验证码短信 

30 次每个号码 / 小时 

电子邮件验证码限额 操作 限额 验证码邮件 无限额 接口限额 操作 限额 匿名账号 100 个请求 /IP 地址 / 小时 发送验证码 1000 个请求 /IP 地址 / 小时 AccessToken 数量 每个用户,限额 500 个 / 项目 / 小时 

## **SDK** 版本更新说明 

版本号 发布时间 

#### 更新说明 

1.0.5 

2025-07-08 

修复已知问题。 

1.0.4 

2025-04-02 

支持华为账号重认证。 

使用华为账号、自有账号登录时, autoCreateUser 参数传 false 不再自 动创建新用户。 

#### 1.0.3 

2025-02-25 

支持 1.9.4 自有账号认证方式。 

1.0.2 

2024-12-02 

修复更新用户信息后导致的应用再次启动获取用户信息失败的问题。 

1.0.1 

2024-11-08 

支持 1.9.3 华为账号认证方式。 

新增 Auth.getAuthProvider 支持通过 Cloud Foundation Kit 初始化 AGC Token 。 

1.0.0-beta 

2024-08-26 

首次发布版本,支持使用 ArkTS 语言开发 HarmonyOS 应用,更加简 洁,更贴合前端开发者的使用习惯, API Version 不得低于 12 。 

## 开发流程 

序号 

任务 

说明 

1 

创建项目 

创建应用 

项目是您在 AppGallery Connect 资源的组织实体,您可以将一个应用 的不同平台版本添加到同一个项目中。 

说明 

您可以通过创建不同的项目,实现分别在测试环境和开发环境使用认 证服务。 

2 

1.7.1 开通服务 

- 

3 

获取 agconnect-services.json 文件 

- 

4 

#### 1.8 集成 SDK 

在工程中集成 AGC SDK 以及认证服务 SDK 。 

5 

根据业务需要,实现不同账号的登录认证。 

1.9.1 手机号码 

1.9.2 邮箱 

1.9.3 华为账号 

1.9.4 自有账号 

1.9.5 匿名账号 

1.9.6 关联账号 

- 

6 

1.10 登出 

当用户不需要使用应用,或者需要切换其他账号登录认证时,可以进 行登出。登出后,端侧保留的用户信息和 Token 将被删除。 

7 

#### 1.11 销户 

当用户需要注销当前账号时,可以进行销户。 

## 开发准备 

### 开通服务 

#### 前提条件 

您已经在 AppGallery Connect 上创建项目,详细操作请参见创建项 目。 

您已经在 AppGallery Connect 上创建应用,详细操作请参见创建应 用。 

开通认证服务 

登录 AppGallery Connect ,点击 “ 开发与服务 ” 。 

在项目列表中找到需要开通认证服务的项目。 

选择 “ 云开发( Serverless ) > 认证服务 ” ,进入认证服务的页面。如 “ ” 果首次使用认证服务,请点击 立即开通 开通服务。 

在弹出的提示框内启用数据处理位置和设置默认数据处理位置,点 “ ” 击 确定 。 

如需了解数据处理位置更多设置场景和对数据处理位置进行管理,请 参见管理数据处理位置。 

### 启用认证方式 

“ ” 开通认证服务后,您可以进入 认证方式 页签,点击需要启用的认证 “ ” 方式所在行的 启用 。 

当前平台支持的认证方式请参见主要功能。 

“ ” 当您的应用需要支持多数据处理位置时,请在 数据处理位置 选择其 他存储地后再分别进行配置。 

启用手机号码 

为进一步保障短信业务的安全性与合规性,依照国家反诈工作部署及 相关行业监管政策要求,国内短信签名需符合以下任一条件:企事业 单位名、已上线 App 名称、已注册商标名,且均需完成运营商实名制 报备,不再支持网站、公众号、小程序、电商店铺等其他签名来源。 “ ” “ 基于当前短信签名标准,如果您的项目 数据处理位置 设置为 中 ” 国 且启用了手机号码认证方式,为保障您业务的正常运行,认证服 务的验证 / 通知短信将不再由 HUAWEI AppGallery Connect 发送,需 要您自行购买第三方短信服务。认证服务可对接您提供的短信发送接 口,来进行后续短信的正常下发。 

#### 配置短信请求接收地址 

认证服务已不再支持向中国大陆推送手机验证码 / 通知短信。如果您 “ ” “ ” 的项目 数据处理位置 设置为 中国 站点,在向中国大陆手机号码推 送手机验证码 / 通知短信之前,请务必配置 “ 短信请求接收地址 ” 。如 “ ” 果 数据处理位置 设置为非中国站点,您可以根据实际业务需求决定 “ ” 是否配置 短信请求接收地址 (即当存在向中国大陆手机号码推送手 机验证码 / 通知短信的场景时,则需配置;反之,则无需配置)。 

“ ” “ ” 认证服务支持通过 云函数 和 服务器 两种方式对接第三方短信服 务: 

云函数(如果您没有自己的服务器,可选择此方式) 

“ ” “ ” 仅当账号注册地为中国,且项目的 数据处理位置 设置为 中国 站点 时,才支持通过云函数对接第三方短信服务。如果设置为非中国站 “ ” “ ” 点, 短信请求接收地址 处将不会显示 云函数 选项。 

“ ” “ ” 短信请求接收地址 选择 云函数 ,系统将自动同步当前项目中已存 “ ” 在的云函数供您选择。配置完成后,点击 确定 。 

“ ” 如果尚未创建云函数,您可以点击 去创建 ,进入云函数服务界面创 建函数。创建完成后,再返回此处进行设置。 

如果云函数数量较多,您可以通过输入关键词来模糊筛选云函数名 称。 

云函数代码可参考如下示例实现(以 Node.js 语言为例): 

let myHandler = function(event, context, callback, logger) { 

logger.info("--------Start-------"); // 1 、处理入参 logger.info("event: ",event); // event 格式如下: // event: { action: '1001', phoneNumber: '+86-xxx', productId: 'xxx', taskId: 'xxx', verifyCode: 'xxx' } // 2 、调用短信提供方服务器地址进行短信发送 // 3 、返回成 功或者具体的错误码 res = {"code": 0, "message": "success", "requestId": "xxx"}; callback(res); }; module.exports.myHandler = myHandler; 

服务器(如果您搭建了自己的服务器,可选择此方式) 

“ ” “ ” 短信请求接收地址 选择 服务器 ,在文本框中输入您的服务器地 址,须以 “http://" 或 "https://" 开头,且不可包含 "@" 字符。配置完成 “ ” 后,点击 确定 。 

认证服务将发送 POST 请求给您的服务器,消息格式如下: 

POST {{ 短信请求接收地址 }}{ "Request Headers": { "X-AGCTimestamp":"1746585196948", // 时间戳 "X-AGC-Auth":"****", // 签名信息 "Content-Type":"application/json" }, "Request Body": { "action":"1001", // 验证码行为。 1001 :注册登录; 1002 :重置密 码; 1003 :修改手机号(此种情况下, verifyCode 为空,仅发送一个 短信通知) "phoneNumber":"+86-12345678910", // 手机号。格式 为 ”+86-xxxxxxxxxxx” "productId":"1234****5678", // 项目 ID "taskId":"023d579****b444bb3224ea125478545", // 任务 Id "verifyCode":"00**52" // 验证码 } } 

收到 POST 请求后,您需要按照如下步骤进行操作: 

验证请求头中的 “X-AGC-Auth” 签名信息。 

判断 POST 消息发送时间戳与服务端时间戳,相差时间不能超过 3 分 钟。 

使用 “POST”+ URL (短信请求接收地址) + 时间戳 + Body ( POST 请求体)进行验签。 

完整示例代码如下: 

“TypeScript” import { Buffer } from 'buffer'; import { createVerify } from 'crypto'; import * as crypto from "node:crypto"; // 认证服务地 址 const serverAddress: string = "https://developer.huawei.com/ 

```arkts
consumer/cn/service/josp/agc/auth/keys" // 获取认证服务的公 钥。公钥获取一次即可,然后存放在本地静态常量中,以提升性能。 let PUBLIC_KEY: string | null = null; /** * 验证签名是否合法 * * @param xAGCAuth 请求头中的签名信息 * @param xAGCTimestamp 请求头中的时间戳 * @param thirdSmsUrl 短信请 求接收地址 * @param thirdSmsReq POST 请求体 */ async function verifyAuth(xAGCAuth: string, xAGCTimestamp: string, thirdSmsUrl: string, thirdSmsReq: ThirdSmsReq): Promise<boolean> { // 1. 检 查时间戳是否过期(不可超过三分钟),业务也可以把该时间调小, 比如: 1 * 60 * 1000L 。 const allowedTimeWindowMs: number = 3 * 60 * 1000; const currentTime = Date.now(); const timestamp = parseInt(xAGCTimestamp, 10); if (isNaN(timestamp) || 
Math.abs(timestamp - currentTime) > allowedTimeWindowMs) { throw new Error("Timestamp expired or invalid"); } // 2. 拼接待验 签字符串(必须与签名方顺序保持一致) const parts = ["POST", thirdSmsUrl, xAGCTimestamp, JSON.stringify(thirdSmsReq)]; const dataToVerify = parts.join("\n"); if (PUBLIC_KEY === null) { PUBLIC_KEY = await getPublicKey() } return 
verifySignature(dataToVerify, xAGCAuth, PUBLIC_KEY); } /** * 验 证签名 * * @param data 待验签字符串 * @param signature 请求头 中的签名信息 * @param public KeyStr 认证服务的公钥 */ async function verifySignature(data: string, signature: string, public KeyStr: string): Promise<boolean> { try { // 创建验签对象 const verify = createVerify('RSA-SHA256'); verify.update(data, 'utf8'); // 验证签名 return verify.verify( { key: public KeyStr, padding: crypto.constants.RSA_PKCS1_PSS_PADDING, saltLength: crypto.constants.RSA_PSS_SALTLEN_DIGEST }, Buffer.from(signature, 'base64') ); } catch (error) { 
console.error('Signature verification failed:', error); return false; } } /** * 获取认证服务的公钥。 * 该方法在您的代码中仅需调用一次。 获取到公钥后,保存在本地的静态常量中即可,不需要每次都调用。 * * @return 公钥 */ async function getPublicKey(): Promise<string | null> { if (PUBLIC_KEY !== null) { return PUBLIC_KEY; } try { const response = await fetch(serverAddress); if (!response.ok) { return null; } const result = await response.text(); const jsonObject: string = JSON.parse(result); const key: string = 
```

Object.values(jsonObject)[0]; const cleanedKey = key .replace('----BEGIN CERTIFICATE-----', '-----BEGIN PUBLIC KEY-----') // 重要:替 换为公钥标记 .replace('-----END CERTIFICATE-----', '-----END PUBLIC KEY-----') .trim(); console.log(cleanedKey) PUBLIC_KEY = 

cleanedKey; return cleanedKey; } catch (e: any) { console.log(e.toString()); } return ''; } // POST 请求体 ThirdSmsReq interface ThirdSmsReq { action: string, // 验证码行为。 1001 :注册 登录; 1002 :重置密码; 1003 :修改手机号(此种情况下, verifyCode 为空 ,仅发送一个短信通知) phoneNumber: string, // 手机号。格式为 ”+86-xxxxxxxxxxx” productId: string, // 项目 ID taskId: string, // 任务 ID 。无实际语义,问题定位使用 verifyCode: string, // 验证码 } 

“Java” import com.alibaba.fastjson.JSON; import com.alibaba.fastjson.JSONObject; import org.apache.http.Consts; import org.apache.http.HttpStatus; import org.apache.http.client.methods.CloseableHttpResponse; import org.apache.http.client.methods.HttpGet; import org.apache.http.impl.client.CloseableHttpClient; import org.apache.http.impl.client.HttpClients; import java.io.BufferedReader; import java.io.InputStreamReader; import java.nio.charset.StandardCharsets; import java.security.KeyFactory; import java.security.NoSuchAlgorithmException; import java.security.PublicKey; import java.security.Signature; import java.security.spec.InvalidKeySpecException; import 

java.security.spec.X509EncodedKeySpec; import java.util.Base64; public class SmsSendService { // 获取认证服务的公钥。公钥获取一 次即可,然后存放在本地静态常量中,提升性能。 private static final String PUBLIC_KEY = getPublicKey(); /** * 验证签名是否合法 * * @param xAGCAuth 请求头中的签名信息 * @param xAGCTimestamp 请求头中的时间戳 * @param thirdSmsUrl 短信请 求接收地址 * @param thirdSmsReq POST 请求体 */ public boolean verifyAuth(String xAGCAuth, String xAGCTimestamp, String thirdSmsUrl, ThirdSmsReq thirdSmsReq) throws Exception { // 1. 检查时间戳是否过期(不可超过三分钟),业务也可以把该时间调 小,比如: 1 * 60 * 1000L 。 long allowedTimeWindowMs = 3 * 60 

* 1000L; long currentTime = System.currentTimeMillis(); if (Math.abs(currentTime - Long.parseLong(xAGCTimestamp)) > allowedTimeWindowMs) { throw new 

SecurityException("Timestamp expired or invalid"); } // 2. 拼接待验 签字符串(必须与签名方顺序保持一致) String dataToVerify = String.join("\n", "POST", thirdSmsUrl, xAGCTimestamp, JSON.toJSONString(thirdSmsReq)); return 

verifySignature(dataToVerify, xAGCAuth, PUBLIC_KEY); } /** * 获 

取认证服务的公钥。 * 该方法在您的代码中仅需调用一次。获取到公 钥后,保存在本地的静态常量中即可,不需要每次都调用。 * * @return 公钥 */ private static String getPublicKey() { HttpGet get = new HttpGet("https://developer.huawei.com/consumer/cn/ service/josp/agc/auth/keys"); try { CloseableHttpClient httpClient = HttpClients.createDefault(); CloseableHttpResponse httpResponse = httpClient.execute(get); int statusCode = 

httpResponse.getStatusLine().getStatusCode(); if (statusCode == HttpStatus.SC_OK) { BufferedReader br = new BufferedReader(new InputStreamReader(httpResponse.getEntity().getContent(), Consts.UTF_8)); String result = br.readLine(); JSONObject object = JSON.parseObject(result); String key = (String) object.values().toArray()[0]; return key.replace("-----BEGIN CERTIFICATE-----", "").replace("-----END CERTIFICATE-----", "").trim(); } } catch (Exception e) { e.printStackTrace(); } return null; } // 验证签名 private static boolean verifySignature(String data, String signature, String publicKey) throws Exception { byte[] e = Base64.getDecoder().decode(publicKey); Signature 

publicSignature = Signature.getInstance("SHA256WithRSA/PSS"); publicSignature.initVerify(newPublicKey(e, "RSA")); publicSignature.update(data.getBytes(StandardCharsets.UTF_8)); byte[] signatureBytes = Base64.getDecoder().decode(signature); return publicSignature.verify(signatureBytes); } /** * 还原公钥 * * @param keyByte 公钥 byte 数组 * @param algName 算法名称 * @return 公钥 * @throws */ private static PublicKey newPublicKey(byte[] keyByte, String algName) throws Exception { try { X509EncodedKeySpec x509KeySpec = new X509EncodedKeySpec(keyByte); KeyFactory keyFactory = KeyFactory.getInstance(algName); return keyFactory.generatePublic(x509KeySpec); } catch (NoSuchAlgorithmException | InvalidKeySpecException e) { throw new Exception("Fail to create public key", e); } } } 

其中, POST 请求体 ThirdSmsReq 定义如下: 

“TypeScript” // POST 请求体 ThirdSmsReq interface ThirdSmsReq { action: string, // 验证码行为。 1001 :注册登录; 1002 :重置密 码; 1003 :修改手机号(此种情况下, verifyCode 为空 ,仅发送一 个短信通知) phoneNumber: string, // 手机号。格式为 ”+86xxxxxxxxxxx” productId: string, // 项目 ID taskId: string, // 任务 

ID 。无实际语义,问题定位使用 verifyCode: string, // 验证码 } 

“Java” public class ThirdSmsReq { private String action; // 验证码 行为。 1001 :注册登录; 1002 :重置密码; 1003 :修改手机号(此 种情况下, verifyCode 为空,仅发送一个短信通知) private String phoneNumber; // 手机号。格式为 ”+86-xxxxxxxxxxx” private String productId; // 项目 ID private String taskId; // 任务 ID 。无实际 语义,问题定位使用 private String verifyCode; // 验证码 } 

处理 POST 请求。将入参里面的短信验证码 “verifyCode” 通过短信提供 商提供的 API 接口进行短信发送。 

POST 请求处理成功后,须按如下字段返回响应。 

{ "code": "0", "message": "OK", "requestId": "xxx" } 

其中, code 和 message 根据处理结果设置返回值。对于 requestId ,业 务可以设置为短信发送接口返回的回执 Id 。或者业务自定义的 traceId 。如果业务不关注该字段,也可以直接设置为入参里面的 taskId 。 

如果业务处理成功,需要将 code 返回 "0" , message 信息自定义即可。 

如果业务处理失败,例如验签失败、时间戳时间和本地时间戳时间相 隔太长、调用短信发送接口失败等,则 code 填写业务自定义的错误 码, message 填写业务自定义的错误原因。 

#### 发送验证码 / 通知模拟测试消息 

为了便于您与第三方短信服务器进行对接和联调,认证服务提供了发 送验证码 / 通知模拟测试消息功能。您可以手动触发以下几种测试消 息: 

#### 验证手机号码 

选中 “ 验证手机号码 ” ,文本框中输入 11 位手机号码,点击 “ 发送 ” 。 重置登录密码 

选中 “ 重置登录密码 ” ,文本框中输入 11 位手机号码,点击 “ 发送 ” 。 

#### 更改手机号码通知 

选中 “ 更改手机号码通知 ” ,文本框中输入 11 位手机号码,点击 “ 发 ” 送 。 

发送模拟测试消息(以验证手机号码为例)后,下方将显示返回结 果: 

正确的响应结果类似下图所示。 

如果响应结果为空,则表示您的接口实现未按照 code 、 message 、 requestId 结构体返回,或 code 、 message 、 requestId 均为空。 

如果返回其他结果,请按照 message 提示进行相应处理。例如下图 中,返回结果显示 Read timed out ,则表示超过 10s 仍未收到响应。 

启用邮箱地址 

“ ” 如果您启用了邮箱验证码认证,请进入 配置 页签配置邮箱服务器相 关信息。 

您默认配置的邮箱服务器是默认数据处理位置的配置,当您的应用需 “ ” 要支持多数据处理位置时,请在 数据处理位置 选择其余存储地后再 分别进行配置。 

您可以选择使用 “ 内置 SMTP” 或者 “ 自定义 SMTP” 。 

使用 “ 内置 SMTP” 时固定 “ 发件人名称 ” 为项目名称, “ 发件人地址 ” 为 auth-verifycode@mail.agconnect.link 。 

使用 “ 自定义 SMTP” 时配置如下信息: 

发件人地址:邮件发送方的邮箱地址 

SMTP 用户账号和 SMTP 用户密码:登录发送邮件服务器所需的用户名 和密码 SMTP 服务主机:提供 SMTP 发件服务的主机名称,例如: QQ 的企业 

发送邮件服务主机为 smtp.exmail.qq.com 

SMTP 服务端口和 SMTP 安全类型:端口和安全类型存在对应关系, TLS 对应 465 端口 

启用手机号码、邮箱以外的账号 

下表所示认证方式在启用时需要在弹出框中配置应用所需的相关信 息,相关认证方式和配置信息获取方式如下所示。 

认证方式 

获取信息 

获取方式 

华为账号 

Client ID 和 Client Secret 

您可以登录 AppGallery Connect ,在 “ 开发与服务 > 项目设置 ” 页 “ ” 面,顶端切换到要查询的应用后,在 应用 区域即可找到应用 的 “OAuth 2.0 客户端 ID” 信息。 

自有账号 

签名公钥 

获取 JWT 

### (可选)安全配置 

“ ” 开通认证服务后,您可以根据需要进入 配置 页签进行用户账户的安 全配置。 

您默认配置的安全配置是默认数据处理位置的配置,当您的应用需要 “ ” 支持多数据处理位置时,请在 数据处理位置 选择其余存储地后再分 

#### 别进行配置。 

#### 配置项 

说明 

密码 / 验证码尝试次数计算周期 

密码 / 验证码失败次数的统计周期,周期结束后将重新统计失败次 数。 

默认值: 60 

单位:分钟 

取值范围: 1-1440 之间的整数。 

密码 / 验证码最大尝试次数 

允许账号采用密码验证 / 验证码验证的最大尝试次数,达到上限会对 账号进行冻结处理,冻结期间用户无法使用该账号进行密码验证 / 验 证码验证。 

默认值: 10 

取值范围: 1-100 之间的整数。 

密码 / 验证码校验冻结时长 

账号采用密码验证 / 验证码验证达到最大尝试次数后冻结的时长,冻 结期间用户无法使用该账号进行密码验证 / 验证码验证。 

默认值: 24 

单位:小时 

取值范围: 1-720 之间的整数。 

密码复杂度 

注意 

密码复杂度描述允许用户使用的密码最低强度,更低强度的密码会让 用户更容易记忆,但是会带来安全性的降低。 

我们强烈建议您不要调低密码复杂度,以免为用户带来风险。除非您 已经充分了解并愿意承担相关风险。 

密码最短长度。 

默认值: 8 

取值范围: 6-1024 之间的整数。 

密码最少字符类型。 

默认值: 2 

字符类型包括: 

小写字母 

大写字母 

数字 

特殊字符: `!@#$%^&*()-_=+\|[{}];:'",<.>/? 和空格 

密码是否可以与账号名相同。 

默认值:不可以 

账号名包括: 

手机号码 

邮箱地址 

### **SDK** 获取 配置信息 

获取 agconnect-services.json 文件 

为了简化您的配置步骤, AppGallery Connect 为您提供了应用配置信 息,您只需要将配置信息添加到您的项目中。 

登录 AppGallery Connect ,选择 “ 开发与服务 ” 。 

在项目列表中找到您的项目,在项目下的应用列表中选择您的应用。 

在 “ 项目设置 ” 页面下载配置文件 “agconnect-services.json” 。 

“ 不包含密钥 ” 开关默认关闭,配置文件中将会包含 AppGallery Connect 为应用分配的客户端密钥和 API 密钥信息,其中客户端密钥和 API 密钥均为密文。 

您也可以在下载 JSON 文件前打开 “ 不包含密钥 ” 开关,配置文件中将 不包含密钥信息,客户端密钥和 API 密钥需要由您自行调用 AGC SDK 的接口手动配置。 

如果您的套餐升级到了付费档,为避免被冒用产生异常账单,建议您 “ ” 打开 不包含密钥 开关,将密钥存储在您自己的服务器,并妥善保 管。 

## **SDK** 集成 

AGC 认证服务 SDK 能为您的应用迅速搭建安全可靠的用户认证系统, 您只需在应用中调用认证服务的相关功能,无需担心云侧的设施和实 现细节。内置了多种认证方式,让您可以轻松完成用户认证的开发工 作。 

SDK 名称: AGC 认证服务 SDK 

包名: @hw-agconnect/auth 

版本号: 1.0.5 

md5 值: 53d14451f0cb3d97a049a6ebc8e84297 

#### 开发者:华为软件技术有限公司 

隐私政策: 1.19 SDK 隐私声明 

合规指引: 1.20 SDK 合规使用指南 

前提条件 

安装 HUAWEI DevEco Studio 5.0.3.100 及以上版本 

配置 SDK API Version 12 及以上 

Compile SDK Version 12 及以上 

Compatible SDK Version 12 及以上 

添加应用配置文件 

获取 “agconnect-services.json” 文件。 

将 “agconnect-services.json” 文件拷贝到 DevEco Studio 项目 的 “AppScope/resources/rawfile” 目录下。 

“AppScope/resources” 目录下默认不存在 “rawfile” 文件夹,需要您手 动创建。 

#### 配置 SDK 依赖 

添加配置文件后,需要在 DevEco Studio 项目中配置 SDK 依赖,您可以 通过以下任意一种方式配置 SDK 依赖: 

方式一 

打开 DevEco Studio 应用级(一般为 entry )下的 “oh-package.json5” 文 件。 

在 “oh-package.json5” 文件里面添加认证服务的编译依赖和 SDK 依 赖。 

"dependencies": { "@hw-agconnect/auth": "^1.0.5" } 

打开修改完的 “oh-package.json5” 文件,右上方出现 “Sync Now” 链 接,点击 “Sync Now” 等待同步完成。 

方式二 

打开您的工程,在命令行窗口执行 cd entry 命令,切换到工程 的 “entry” 目录。 

安装 SDK 到您的项目中。 

ohpm install @hw-agconnect/auth 

集成 SDK 

工程的应用框架必须为 Stage 模型,即 “apiType” 为 “stageMode” 。 请确保 SDK 的 Compile API 版本不低于 12 。 

请确保采用 ohpm 方式编译。 

在您的项目中导入 agc 组件。 

import auth from '@hw-agconnect/auth'; 

在您的应用初始化阶段使用 context 初始化 SDK ,推荐在 “entry/src/ main/ets/entryability/EntryAbility.ets” 的 onCreate 中进行。 

// 初始化 SDK onCreate(want, launchParam) { let file = this.context.resourceManager.getRawFileContentSync('agconnectservices.json'); let json: string = buffer.from(file.buffer).toString(); auth.init(this.context, json); } 

在 “entry/src/main/module.json5” 文件中添加网络权限。 

"requestPermissions": [ { "name": "ohos.permission.INTERNET" } ] 

(可选)设置配置文件参数 

“ ” 如果您在下载配置文件时选择了 不包含密钥 ,配置信息中将不包含 Client ID 和 Client Secret ,您还需调用 AGC SDK 的接口手动将 Client 

ID 和 Client Secret 传给 AppGallery Connect 使用。 

在 “ 项目设置 > 常规 ” 页面中获取 Client ID 和 Client Secret 。 

#### 在应用启动调用初始化方法完成后将参数设置给 AGC SDK 。 

import auth from '@hw-agconnect/auth'; let file = 

```arkts
this.context.resourceManager.getRawFileContentSync('agconnectservices.json'); let json: string = buffer.from(file.buffer).toString(); auth.init(this.context, json); auth.setClientId("xxx"); // 设置 Client ID auth.setClientSecret("xxx"); // 设置 Client Secret 
```

#### 配置混淆脚本 

当前认证服务 SDK 开启了混淆,如果您的工程中也开启了混淆并配置 了混淆规则,则需要您在工程的混淆规则配置文件 “obfuscationrules.txt” 中添加认证服务 SDK 的混淆规则。 

打开混淆规则配置文件 “obfuscation-rules.txt” 。 

#### 参照如下示例添加混淆规则。 

-keep XXX/oh_modules/@hw-agconnect/auth 

其中, “XXX” 表示认证服务 SDK 在 “oh_modules” 文件夹下的路径,例 如下图中 “oh_modules” 和 “obfuscation-rules.txt” 同在 “entry” 目录下。 

## 登录 

### 手机号码 

“ 您可以在应用中集成手机账号认证方式,您的用户可以使用 手机号 码 + 密码 ” 或者 “ 手机号码 + 验证码 ” 的方式来登录您的应用。 前提条件 

您需要在 AppGallery Connect1.7.1 开通服务。 

您需要先在您的应用中 1.8 集成 SDK 。 

注册 

申请手机号码注册的验证码。 

在使用手机号码注册之前,需要先验证您的手机,确保该手机归您所 有。 

当前认证服务暂不支持向中国大陆推送手机验证码 / 通知短信。如果 “ ” “ ” 您项目的 数据处理位置 设置为 中国 且需要向中国大陆推送手机验 证码 / 通知消息,请通过您的云函数或服务器接收验证码并发送短 信。详情可参考启用手机号码。 

调用 Auth.requestVerifyCode 申请验证码。 

```arkts
import auth from '@hw-agconnect/auth'; import { VerifyCodeAction } from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.requestVerifyCode({ action: VerifyCodeAction.REGISTER_LOGIN, lang: 'zh_CN', sendInterval: 60, verifyCodeType: { phoneNumber: '138********', countryCode: '86', kind: 'phone', } }).then(verifyCodeResult => { // 验证码申请成功 }).catch((error: BusinessError) => { // 验证码申请失败 }) 
```

#### 使用手机号码注册用户。 

调用 Auth.createUser 注册用户。注册成功后,系统会自动登录,无需 再次调用登录接口。 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.createUser({ kind: 'phone', countryCode: '86', phoneNumber: '138********', password: 'your password',// 可以给用户设置初始密码,后续可以用密码来登录 verifyCode: 'xxxxxx' }).then(result => { // 创建用户成功 }).catch((error: BusinessError) => { // 创建用户失败 }) 
```

登录成功后可以调用 Auth.getCurrentUser 获取用户账号数据。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser(); 

#### 密码登录 

在应用的登录界面,初始化 Auth 实例,获取 AppGallery Connect 的用 户信息,检查是否有已经登录的用户。如果有,则可以直接进入用户 界面,否则显示登录界面。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ // 业务逻辑 } }); 

调用 Auth.signIn 实现登录。 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.signIn({ credentialInfo: { kind: 'phone', phoneNumber: '138********', countryCode: '86', password: 'your password' } }).then(user => { // 登录成功 }).catch((error: BusinessError) => { // 登录失败 }); 
```

#### 验证码登录 

在应用的登录界面,初始化 Auth 实例,获取 AGC 的用户信息,检查是 否有已经登录的用户。如果有,则可以直接进入用户界面,否则显示 登录界面。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ // 业务逻辑 } }); 

调用 Auth.requestVerifyCode 申请手机登录验证码。 

当前认证服务暂不支持向中国大陆推送手机验证码 / 通知短信。如果 “ ” “ ” 您项目的 数据处理位置 设置为 中国 且需要向中国大陆推送手机验 证码 / 通知消息,请通过您的云函数或服务器接收验证码并发送短 信。详情可参考启用手机号码。 

```arkts
import auth from '@hw-agconnect/auth'; import { VerifyCodeAction } from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.requestVerifyCode({ action: VerifyCodeAction.REGISTER_LOGIN, lang: 'zh_CN', sendInterval: 60, 
```

verifyCodeType: { phoneNumber: '138********', countryCode: '86', kind: 'phone' } }).then(verifyCodeResult => { // 验证码申请成功 }).catch((error: BusinessError) => { // 验证码申请失败 }); 

调用 Auth.signIn 实现登录。 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.signIn({ credentialInfo: { kind: 'phone', phoneNumber: '138********', countryCode: '86', verifyCode: 'xxxxxx' } }).then(user => { // 登录成功 }).catch((error: BusinessError) => { // 登录失败 }); 
```

#### 修改手机号码 

修改手机号码需要用户处于登录状态。 

当前认证服务暂不支持向中国大陆推送手机验证码 / 通知短信。如果 “ ” “ ” 您项目的 数据处理位置 设置为 中国 且需要向中国大陆推送手机验 证码 / 通知消息,请通过您的云函数或服务器接收验证码并发送短 信。详情可参考启用手机号码。 

调用 Auth.requestVerifyCode 申请验证码。 

```arkts
import auth from '@hw-agconnect/auth'; import { VerifyCodeAction } from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.requestVerifyCode({ action: VerifyCodeAction.REGISTER_LOGIN, lang: 'zh_CN', sendInterval: 60, verifyCodeType: { phoneNumber: '138********', countryCode: '86', kind: "phone" } }).then(verifyCodeResult => { // 验证码申请成功 }).catch((error: BusinessError) => { // 验证码申请失败 }); 
```

调用 AuthUser.updatePhone 修改手机号码。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then((user) => { if(user){ user.updatePhone({ countryCode: '86', phoneNumber: '138********', verifyCode: 'xxxxxx', lang: 'zh_CN' }) } }) 

对于修改手机号码操作,要求用户必须在 5 分钟内登录过应用才能执 

行。若登录已超时,请参见 1.12 账号重认证先完成重认证。 

修改密码 

修改密码时需要用户处于登录状态。 

调用 AuthUser.updatePassword 修改密码。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then((user) => { if(user){ user.updatePassword({ password: 'your password', providerType: 'phone' }) } }) 

对于修改手机密码操作,要求用户必须在 5 分钟内登录过应用才能执 行。若登录已超时,请参见 1.12 账号重认证先完成重认证。 重置密码 

#### 重置密码时用户可以不登录。 

当前认证服务暂不支持向中国大陆推送手机验证码 / 通知短信。如果 “ ” “ ” 您项目的 数据处理位置 设置为 中国 且需要向中国大陆推送手机验 证码 / 通知消息,请通过您的云函数或服务器接收验证码并发送短 信。详情可参考启用手机号码。 

调用 Auth.requestVerifyCode 申请验证码。 

```arkts
import auth from '@hw-agconnect/auth'; import { VerifyCodeAction } from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.requestVerifyCode({ action: VerifyCodeAction.RESET_PASSWORD, lang: 'zh_CN', sendInterval: 60, verifyCodeType: { phoneNumber: '138********', countryCode: '86', kind: 'phone' } }).then(verifyCodeResult => { // 验证码申请 成功 }).catch((error: BusinessError) => { // 验证码申请失败 }); 
```

调用 Auth.resetPassword 重置密码。 

import auth from '@hw-agconnect/auth'; auth.resetPassword({ 

kind: 'phone', password: '123456', phoneNumber: '138********', countryCode: '86', verifyCode: 'xxxxxx' }) 

#### 更多信息 

您如果想让用户可以使用多个账号登录您的应用,可以 1.9.6 关联账 号。 

当用户不需要使用应用,或者需要切换其他账号登录认证,可以先执 行 1.10 登出。 

当用户需要注销当前用户,可以进行 1.11 销户。 

对于销户、修改密码、关联账号以及重置手机账号和邮箱账号等敏感 操作,为了提高安全性,需要用户必须在 5 分钟内登录过才能执行。 如果用户执行敏感操作时登录超过 5 分钟,需要 1.12 账号重认证后再 执行敏感操作。 

您可以参考 1.13 异常处理实现自己的异常处理机制,从而减少异常情 况的发生。 

您可以使用云函数触发器来接收用户注册、登录、销户等关键事件, 从而 1.14 通过云函数扩展。 

您可以参考 1.16 管理用户对用户进行解锁、停用等操作。 

### 邮箱 

“ 您可以在应用中集成邮箱账号认证方式,您的用户可以使用 邮箱地 址 + 密码 ” 或者 “ 邮箱地址 + 验证码 ” 的方式来登录您的应用。 前提条件 

您需要在 AppGallery Connect1.7.1 开通服务。 

您需要先在您的应用中 1.8 集成 SDK 。 

注册 

在使用邮箱注册之前,需要先验证您的邮箱,确保该邮箱账户归您所 

有。 

#### 调用 Auth.requestVerifyCode 申请验证码。 

```arkts
import auth from '@hw-agconnect/auth'; import { VerifyCodeAction } from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.requestVerifyCode({ action: VerifyCodeAction.REGISTER_LOGIN, lang: 'zh_CN', sendInterval: 60, verifyCodeType: { email: 'xxxx@xxx.com', kind: 'email' } }).then(verifyCodeResult => { // 验证码申请成功 }).catch((error: BusinessError) => { // 验证码申请失败 }); 
```

#### 使用邮箱账号注册用户。 

#### 调用 Auth.createUser 注册用户。注册成功后,系统会自动登录,无需 再次调用登录接口。 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.createUser({ "kind": 'email', "email": 'xxxx@xxx.com', "password": 'your password', "verifyCode": 'xxxxxx' }).then(result => { // 创建账号成功后,默认已登录 }).catch((error: BusinessError) => { // 创建用户失败 }) 
```

登录成功后可以调用 Auth.getCurrentUser 获取用户账号数据。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser(); 

#### 密码登录 

在应用的登录界面,初始化 Auth 实例,获取 AGC 的用户信息,检查是 否有已经登录的用户。如果有,则可以直接进入用户界面,否则显示 登录界面。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ // 业务逻辑 }}); 

调用 Auth.signIn 实现登录。 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.signIn({ autoCreateUser: true, credentialInfo: { kind: 'email', password: 'your password', email: 
```

'xxxx@xxx.com' } }).then(user => { // 登录成功 }).catch((error: BusinessError) => { // 登录失败 }); 

#### 验证码登录 

在应用的登录界面,初始化 Auth 实例,获取 AGC 的用户信息,检查是 否有已经登录的用户。如果有,则可以直接进入用户界面,否则显示 登录界面。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ // 业务逻辑 } }); 调用 Auth.requestVerifyCode 申请登录验证码。 

```arkts
import auth from '@hw-agconnect/auth'; import { VerifyCodeAction } from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.requestVerifyCode({ action: VerifyCodeAction.REGISTER_LOGIN, lang: 'zh_CN', sendInterval: 60, verifyCodeType: { email: 'xxxx@xxx.com', kind: 'email' } }).then(verifyCodeResult => { // 验证码申请成功 }).catch((error: BusinessError) => { // 验证码申请失败 }); 
```

调用 Auth.signIn 实现登录。 

password 参数可以不传,如果同时输入了密码和验证码,则会同时验 证密码和验证码。 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.signIn({ credentialInfo: { kind: 'email', password: 'your password', email: 'xxxx@xxx.com', verifyCode: 'xxxxxx' } }).then(user => { // 登录成功 }).catch((error: BusinessError) => { // 登录失败 }); 
```

#### 修改邮箱地址 

修改邮箱地址时需要用户处于登录状态。 

调用 Auth.requestVerifyCode 申请验证码。 

```arkts
import auth from '@hw-agconnect/auth'; import { VerifyCodeAction } from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.requestVerifyCode({ action: VerifyCodeAction.REGISTER_LOGIN, lang: 'zh_CN', sendInterval: 60, verifyCodeType: { email: 'xxxx@xxx.com', kind: 'email' } }).then(verifyCodeResult => { // 验证码申请成功 }).catch((error: BusinessError) => { // 验证码申请失败 }); 
```

调用 AuthUser.updateEmail 修改邮箱地址。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then((user) => { if(user){ user.updateEmail({ email: 'xxxx@xxx.com', lang: 'zh_CN', verifyCode: 'xxxxxx' }) } }) 

对于修改邮箱地址操作,要求用户必须在 5 分钟内登录过应用才能执 行。若登录已超时,请参见 1.12 账号重认证先完成重认证。 

#### 修改邮箱密码 

修改邮箱密码时需要用户处于登录状态。 

调用 AuthUser.updatePassword 修改密码。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then((user) => { if(user){ user.updatePassword({ password: 'your password', verifyCode: 'xxxxxx', providerType: 'email' }) } }) 

对于修改邮箱密码操作,要求用户必须在 5 分钟内登录过应用才能执 行。若登录已超时,请参见 1.12 账号重认证先完成重认证。 

#### 重置密码 

重置密码时用户可以不登录。 

调用 Auth.requestVerifyCode 申请验证码。 

```arkts
import auth from '@hw-agconnect/auth'; import { VerifyCodeAction } from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.requestVerifyCode({ action: VerifyCodeAction.RESET_PASSWORD, lang: 'zh_CN', sendInterval: 60, verifyCodeType: { email: 'xxx@xxx.com', kind: 'email', } }).then(verifyCodeResult => { // 验证码申请成功 }).catch((error: BusinessError) => { // 验证码申请失败 }); 
```

调用 Auth.resetPassword 重置密码。 

import auth from '@hw-agconnect/auth'; auth.resetPassword({ kind: 'email', password: 'your password', email: 'xxxx@xxx.com', verifyCode: 'xxxxxx' }) 

更多信息 

您如果想让用户可以使用多个账号登录您的应用,可以 1.9.6 关联账 号。 

当用户不需要使用应用,或者需要切换其他账号登录认证,可以先执 行 1.10 登出。 当用户需要注销当前用户,可以进行 1.11 销户。 

对于销户、修改密码、关联账号以及重置手机账号和邮箱账号等敏感 操作,为了提高安全性,需要用户必须在 5 分钟内登录过才能执行。 如果用户执行敏感操作时登录超过 5 分钟,需要 1.12 账号重认证后再 执行敏感操作。 

您可以参考 1.13 异常处理实现自己的异常处理机制,从而减少异常情 况的发生。 

您可以使用云函数触发器来接收用户注册、登录、销户等关键事件, 从而 1.14 通过云函数扩展。 

您可以参考 1.16 管理用户对用户进行解锁、停用等操作。 

### 华为账号 

您可以在应用中集成华为账号认证方式,让您的用户可以使用自己的 

#### 华为账号进行 AppGallery Connect 身份验证。 

前提条件 

您需要在 AppGallery Connect1.7.1 开通服务和申请华为账号权限。 

您需要先在您的应用中 1.8 集成 SDK 。 

配置应用签名公钥指纹 

登录 AppGallery Connect ,点击 “ 开发与服务 ” 。 

在项目列表中找到您的项目,在项目中点击您的 HarmonyOS 应用 / 元 服务。 

在 “ 项目设置 > 常规 ” 页面的 “ 应用 ” 区域,点击 “SHA256 证书 / 公钥指 ” “ ” 纹 后的 添加公钥指纹 。 

在 “ 添加 SHA256 公钥指纹 ” 窗口, “ 添加方式 ” 选择 “ 选择指纹 ” ,然后选 择应用 / 元服务使用的证书对应的指纹,点击 “ 确认 ” 。 

调试阶段请选择应用 / 元服务使用的调试证书指纹,发布阶段请选择 应用 / 元服务使用的发布证书指纹。 

过期或废弃的证书不在此展示。 

指纹添加成功后,将展示在 “SHA256 证书 / 公钥指纹 ” 栏。 

指纹最迟在 25 小时后生效。如您急需指纹生效,请执行下一步操作。 

(可选)如果希望配置的公钥指纹快速生效,请在指纹成功配置 10 分 钟后,通过改变应用 / 元服务工程 “app.json5” 文件中 的 “versionCode” 字段的值触发指纹生效。例如,原先值 为 “1000000” ,修改为 “1000001” 。 

配置 Client ID 

#### 登录 AppGallery Connect ,点击 “ 开发与服务 ” 。 

“ 在项目列表中找到您的项目,在项目中选择目标应用,获取 项目设 置 > 常规 ” 页面 “ 应用 ” 区域的 Client ID 。 

在工程中 “entry” 模块的 “module.json5” 文件中,新增 metadata ,配置 name 为 client_id , value 为上一步获取的 Client ID 的值。示例如下: 

"module": { "name": "xxx", "type": "entry", "description": "xxx", "mainElement": "xxx", "deviceTypes": [], "pages": "xxx", "abilities": [], "metadata": [ // 配置信息如下 { "name": "client_id", "value": "xxx" } ] } 

#### 开发步骤 

#### 调用 Auth.signIn ,登录华为账号。 

```arkts
import auth from '@hw-agconnect/auth'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { BusinessError } from '@kit.BasicServicesKit'; auth.signIn({ autoCreateUser: true, "credentialInfo": { "kind": 'hwid' } }).then(signInResult => { hilog.info(0x0000, 'testTag', '%{public}s', `signInHwid success. result: ${signInResult.getUser().getUid()}`); }) .catch((error: BusinessError) => { hilog.error(0x0000, 'testTag', '%{public}s', `signInHwid error, Code: ${error.code}, message: ${error.message} `); }) 
```

#### 更多信息 

您如果想让用户可以使用多个账号登录您的应用,可以 1.9.6 关联账 号。 

当用户不需要使用应用,或者需要切换其他账号登录认证,可以先执 行 1.10 登出。 当用户需要注销当前用户,可以进行 1.11 销户。 

对于销户、修改密码、关联账号以及重置手机账号和邮箱账号等敏感 操作,为了提高安全性,需要用户必须在 5 分钟内登录过才能执行。 如果用户执行敏感操作时登录超过 5 分钟,需要 1.12 账号重认证后再 

#### 执行敏感操作。 

您可以参考 1.13 异常处理实现自己的异常处理机制,从而减少异常情 况的发生。 

您可以使用云函数触发器来接收用户注册、登录、销户等关键事件, 从而 1.14 通过云函数扩展。 

您可以参考 1.16 管理用户对用户进行解锁、停用等操作。 

### 自有账号 

如果您已经自行构建了认证系统,您可以通过自有账号来对接认证服 务,让您的用户可以使用自有账号进行 AppGallery Connect 身份验 证。 

前提条件 

您需要在 AppGallery Connect1.7.1 开通服务。 

您需要先在您的应用中 1.8 集成 SDK 。 

开发步骤 

自有账号登录,并获取自有账号的用户授权信息。 

当用户登录开发者的服务器后,将其登录信息(例如用户名、头像信 息等)发送给开发者自己的身份验证服务器,身份验证服务器对用户 的身份进行验证,验证通过后,用于身份验证的服务器会产生一个自 定义的令牌(例如 Json Web Token ),开发者将此令牌传递给 AppGallery Connect 。 

使用从自有账号获取的 JWT 信息生成 credentialInfo ,并调用 Auth.signIn 实现登录。 

```arkts
import auth from '@hw-agconnect/auth'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { BusinessError } from '@kit.BasicServicesKit'; auth.signIn({ 'credentialInfo': { kind: 'selfBuild', accessToken: 'JWT Token' } }).then(signInResult => { 
```

hilog.info(0x0000, 'testTag', '%{public}s', `signInselfBuild success. result: ${signInResult.getUser().getUid()}`); }) .catch((error: BusinessError) => { hilog.error(0x0000, 'testTag', '%{public}s', `signInselfBuild error, Code: ${error.code}, message: ${error.message}`); }) 

#### 更多信息 

您如果想让用户可以使用多个账号登录您的应用,可以 1.9.6 关联账 号。 

当用户不需要使用应用,或者需要切换其他账号登录认证,可以先执 行 1.10 登出。 当用户需要注销当前用户,可以进行 1.11 销户。 

对于销户、修改密码、关联账号以及重置手机账号和邮箱账号等敏感 操作,为了提高安全性,需要用户必须在 5 分钟内登录过才能执行。 如果用户执行敏感操作时登录超过 5 分钟,需要 1.12 账号重认证后再 执行敏感操作。 

您可以参考 1.13 异常处理实现自己的异常处理机制,从而减少异常情 况的发生。 

您可以使用云函数触发器来接收用户注册、登录、销户等关键事件, 从而 1.14 通过云函数扩展。 

您可以参考 1.16 管理用户对用户进行解锁、停用等操作。 

### 匿名账号 

您可以在应用中集成匿名账号认证方式,让您的用户可以使用游客模 式进行身份验证。 

前提条件 

您需要在 AppGallery Connect1.7.1 开通服务。 

您需要先在您的应用中 1.8 集成 SDK 。 

#### 开发步骤 

在应用的登录界面,初始化 Auth 实例,获取 AGC 的用户信息,检查是 否有已经登录的用户。如果有,则可以直接进入用户界面,否则显示 登录界面。可通过 AuthUser.isAnonymous 判断是否是匿名登录用 户。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ // 业务逻辑 } }); 调用 Auth.signInAnonymously 进行匿名登录,返回匿名用户信息。 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.signInAnonymously().then(user => { // 匿名登录成功 }).catch((error: BusinessError) => { // 匿 名登录失败 }); 
```

更多信息 

您如果想让用户可以使用多个账号登录您的应用,可以 1.9.6 关联账 号。 

当用户不需要使用应用,或者需要切换其他账号登录认证,可以先执 行 1.10 登出。 当用户需要注销当前用户,可以进行 1.11 销户。 

对于销户、修改密码、关联账号以及重置手机账号和邮箱账号等敏感 操作,为了提高安全性,需要用户必须在 5 分钟内登录过才能执行。 如果用户执行敏感操作时登录超过 5 分钟,需要 1.12 账号重认证后再 执行敏感操作。 

您可以参考 1.13 异常处理实现自己的异常处理机制,从而减少异常情 况的发生。 

您可以使用云函数触发器来接收用户注册、登录、销户等关键事件, 从而 1.14 通过云函数扩展。 

您可以参考 1.16 管理用户对用户进行解锁、停用等操作。 

### 关联账号 

#### 前提条件 

您需要在 AppGallery Connect1.7.1 开通服务。 

您需要先在您的应用中 1.8 集成 SDK 。 

将身份验证提供方凭据与用户账号关联 

您可以将身份验证提供方凭据关联至现有用户账号,允许用户使用多 个身份验证提供方服务登录您的应用。无论用户使用哪个账号登录, 均可通过同一 AGC 用户 ID 识别用户。例如,使用手机账号登录的用户 可以关联邮箱账号,以后便可使用这两种方法中的任意一种登录。 

目前关联账号功能支持的账号类型包括手机、邮箱和华为账号。 

关联账号前,需要为应用增加对两个或多个身份验证提供方(可以包 括匿名身份验证)的支持。 

关联的认证方式只能有一个账号,例如手机账号关联邮箱账号,只能 关联一个邮箱账号,不能关联多个。另外被关联的账号需要没有登录 过应用,例如已经通过认证服务登录过的邮箱账号也无法进行关联。 

使用任意身份验证提供方让用户登录,如使用手机号的认证方式进行 登录。 

调用 AuthUser.link 关联用户新的认证方式。关联成功后,即可以使用 任意一个提供方的凭证来登录相同的 AGC 账号。 

手机方式。示例如下: 

```arkts
import auth from '@hw-agconnect/auth'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { BusinessError } from '@kit.BasicServicesKit'; auth.getCurrentUser().then((user:AuthUser | null) => { user!.link({ kind: 'phone', phoneNumber: '180****1485', countryCode: '86', verifyCode: 'xxxxxx' 
```

}).then(signInResult => { hilog.info(0x0000, 'testTag', '%{public} s', `link success. result: ${signInResult.getUser().getUid()}`); 

}).catch((error: BusinessError) => { hilog.error(0x0000, 'testTag', '%{public}s', `link error, Code: ${error.code}, message: ${error.message}`); }) }) 

#### 邮箱方式。示例如下: 

```arkts
import auth from '@hw-agconnect/auth'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { BusinessError } from '@kit.BasicServicesKit'; auth.getCurrentUser().then((user:AuthUser | null) => { user!.link({ kind: 'email', password: '****', email: 'xxxx@huawei.com', verifyCode: 'xxxxxx' }).then(signInResult => { hilog.info(0x0000, 'testTag', '%{public}s', `link success. result: ${signInResult.getUser().getUid()}`); }).catch((error: BusinessError) => { hilog.error(0x0000, 'testTag', '%{public}s', `link error, Code: ${error.code}, message: ${error.message}`); }) }) 
```

#### 华为账号方式。示例如下: 

```arkts
import auth from '@hw-agconnect/auth'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { BusinessError } from '@kit.BasicServicesKit'; auth.getCurrentUser().then((user:AuthUser | null) => { user!.link({ kind: 'hwid' }).then(signInResult => { hilog.info(0x0000, 'testTag', '%{public}s', `link success. result: ${signInResult.getUser().getUid()}`); }).catch((error: BusinessError) => { hilog.error(0x0000, 'testTag', '%{public}s', `link error, Code: ${error.code}, message: ${error.message}`); }) }) 
```

#### 自有账号方式。示例如下: 

```arkts
import auth from '@hw-agconnect/auth'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { BusinessError } from '@kit.BasicServicesKit'; auth.getCurrentUser().then((user:AuthUser | null) => { user!.link({ kind: 'selfBuild', accessToken: 'JWT Token' }).then(signInResult => { hilog.info(0x0000, 'testTag', '%{public} s', `link success. result: ${signInResult.getUser().getUid()}`); }).catch((error: BusinessError) => { hilog.error(0x0000, 'testTag', '%{public}s', `link error, Code: ${error.code}, message: ${error.message}`); }) }) 
```

取消身份验证提供方凭据与用户账号的关联 

您也可以取消身份验证提供方凭据与用户账号的关联,以便用户不再 使用该身份验证提供方进行登录。 

取消关联时,需提供要取消的身份验证提供方 ID ,然后调用 AuthUser.unlink 接口进行取消。 

当仅有一个身份验证提供方时不能进行取消关联操作。 

目前 AuthUser.unlink 接口的 “ProviderType” 入参支持 'email' 、 'phone' 或 'hwid' 。下面以取消手机账号关联为例。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user => { user.unlink('phone'); }); 

#### 更多信息 

当用户不需要使用应用,或者需要切换其他账号登录认证,可以先执 行 1.10 登出。 当用户需要注销当前用户,可以进行 1.11 销户。 

对于销户、修改密码、关联账号以及重置手机账号和邮箱账号等敏感 操作,为了提高安全性,需要用户必须在 5 分钟内登录过才能执行。 如果用户执行敏感操作时登录超过 5 分钟,需要 1.12 账号重认证后再 执行敏感操作。 

您可以参考 1.13 异常处理实现自己的异常处理机制,从而减少异常情 况的发生。 

您可以参考 1.16 管理用户对用户进行解锁、停用等操作。 

## 登出 

前提条件 

您需要在 AppGallery Connect1.7.1 开通服务。 

您需要先在您的应用中 1.8 集成 SDK 。 

#### 开发步骤 

当用户不再使用应用,或者需要使用其他账号登录时,需要调用 Auth.signOut 登出当前用户。用户一旦被登出,端侧的用户信息和 Token 将被清除。 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.signOut().then(() => { // 登出成 功 }).catch((error: BusinessError) => { // 登出失败 }); 
```

## 销户 

#### 前提条件 

您需要在 AppGallery Connect1.7.1 开通服务。 

您需要先在您的应用中 1.8 集成 SDK 。 

开发步骤 

当用户不再使用应用,可以注销当前用户。您需要调用 Auth.deleteUser 实现该功能,用户一旦被注销,将会在删除服务端侧 用户信息的同时,清空客户端侧用户信息和 Token 。 

import auth from '@hw-agconnect/auth'; auth.deleteUser(); 

对于销户操作,要求用户必须在 5 分钟内登录过应用才能执行。若登 录已超时,请参见 1.12 账号重认证先完成重认证。 

## 账号重认证 

#### 前提条件 

您需要在 AppGallery Connect1.7.1 开通服务。 

您需要先在您的应用中 1.8 集成 SDK 。 

#### 开发步骤 

对于销户、修改密码、关联账号以及重置手机账号和邮箱账号这些敏 感操作,要求用户必须在 5 分钟内登录过应用才能执行。如果您执行 敏感操作时已经登录超过 5 分钟,该操作会抛出 AGCAuthError 异常, 并收到错误码为 203818081 的错误,这种情况下您可以先调用 AuthUser.userReauthenticate ,重认证账号后再执行敏感操作。 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user => { if (!user) { return; } user.userReauthenticate({ credentialInfo: { kind: 'phone', password: 'your password', phoneNumber: '138********', countryCode: '86', verifyCode: 'xxxxxx' } }); }); 

## 异常处理 

在某些情况下,程序无法按预想的情况正常执行,而是会发生异常。 您可以根据 AGCAuthError 实例对象或者 AGCError 实例对象返回的错 误码定制实现自己的异常处理方案,给用户带来更友好体验。 

#### 处理异常 

处理接口异常时,您可以从接口抛出的异常来获取到请求失败的相关 信息。您需要判断该方式回调的异常对象是否是一个 AGCAuthError 实例对象,然后您可以根据返回的错误码定制实现您自己的异常处理 场景。 

```arkts
import { AGCAuthError } from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.signIn(signInParam).then(user => { // 登录成功 }).catch((error: BusinessError) => { // 登录失败 if (error instanceof AGCAuthError) { // 根据错误码进行处理 } }); 
```

#### 错误码 203817986 特殊处理说明 

用户登录成功后,认证服务 SDK 会保存当前用户的 Access Token 和 

#### Refresh Token 。 

Access Token :用户的访问令牌,表明用户的唯一身份,涉及到用户 级别的操作,都需要验证 Access Token 。 

Refresh Token :刷新用户的 Access Token ,由认证服务 SDK 自动刷 新。 

Access Token 有效期为 1 小时, Refresh Token 为 2 个月。用户如果连 续 2 个月没有登录操作,在调用涉及用户级别的接口时, Refresh Token 失效,会抛出错误码 203817986 。 

您应该在代码中显式捕获该错误码,提示用户重新登录。 

## 通过云函数扩展 

认证服务为您提供了基于云函数的扩展机制,您可以通过为云函数配 置相应事件类型的认证服务触发器来接收用户的注册、登录等关键事 件,并在云函数中扩展您的处理。 

比如,您可以创建函数并监听用户注册事件以便进行用户业务数据的 初始化,您也可以创建函数并监听用户销户事件以便进行用户业务数 据的清理。 

为函数设置认证服务触发器 

为函数添加触发器时,可以选择认证服务触发器,请参见创建认证服 务触发器。 

认证服务触发器提供了四种事件类型: 

用户注册 

用户销户 

用户登录 

用户登出 

#### 在函数中获取用户信息 

您可以从认证服务触发的云函数的参数中获取相关的用户信息,请参 见认证服务触发器对象格式。 

// 获取用户标识 var uid = event.uid; // 获取用户操作类型 : 0 用户 注册 , 1 用户销户 , 2 用户登录 , 3 用户登出 var op = event.op; 

## 用量统计 

#### 查看认证服务配额使用情况 

您可以进入 “ 开发与服务 > 项目设置 ” 页面,在 “ 项目配额 ” 页签下选 择认证服务,查看您的验证短信配额和用量情况。 

## 管理用户 

“ ” 同一个项目下已经登录过的用户都会展现在 用户 页签。您可以在此 管理用户,可对用户进行停用、启用、解锁和删除的操作。 启用用户 

您可以将已停用的用户进行重新启用,用户便可重新登录应用。 

在认证服务页面,点击 “ 用户 ” 页签,在搜索框中输入 UID 、手机号 码、邮箱地址、三方 ID 或自有账号 ID 查询用户,在状态为 “ 已停用 ” 的 “ ” “ ” 用户的 操作 列点击 启用 。 

“ ” “ ” 在系统弹出的对话框中点击 确定 ,用户状态变更为 正常 。 

解锁用户 

“ ” 下面以 手机号码 认证方式为例进行说明。 

“ ” 用户使用 手机号码 的认证方式登录应用时,输入的密码或验证码次 

“ 数达到了尝试次数的上限,该用户会被锁定即用户状态变更为 已锁 ” “ ” 定 。锁定期间,该用户将不能再以 手机号码 认证方式登录应用。如 果用户需要立即解锁账号,您可以帮助用户进行解锁,用户的状态变 “ ” 更为 正常 。 

“ ” 如果用户使用 手机号码 认证方式登录时被锁定,该用户的其他认证 方式(如邮箱账号)依然可以正常登录。 

在认证服务页面,点击 “ 用户 ” 页签,在搜索框中输入 UID 、手机号 码、邮箱地址、三方 ID 或自有账号 ID 查询用户,在状态为 “ 已锁定 ” 的 “ ” “ ” 用户的 操作 列点击 解锁 。 

“ ” “ 在系统弹出的对话框中点击 确定 ,用户即可解锁,状态变更为 正 ” 常 。 

#### 停用用户 

您可以将暂时不需要登录的用户进行停用,停用后,用户需要重新启 用后才可以登录应用。 

在认证服务页面,点击 “ 用户 ” 页签,在搜索框中输入 UID 、手机号 码、邮箱地址、三方 ID 或自有账号 ID 查询用户,在需要停用用户 “ ” “ ” 的 操作 列点击 停用 。 

“ ” “ ” 在系统弹出的对话框中点击 确定 ,用户状态变更为 已停用 。 

删除用户 

如果用户不需要继续使用您的应用,您可以在此将用户删除,删除后 若想再次登录,需要重新认证登录。 

在认证服务页面,点击 “ 用户 ” 页签,在搜索框中输入 UID 、手机号 码、邮箱地址、三方 ID 或自有账号 ID 查询用户,在需要删除用户 “ ” “ ” 的 操作 列点击 删除 。 

“ ” 在系统弹出的对话框中点击 确定 ,用户从列表中删除。 

## **FAQ** 

通用 

认证服务与华为账号服务的区别和关系? 

认证服务和华为账号服务关注的是开发者两个不同层面的诉求。 

华为账号服务致力于华为账号的开放,可以让您的用户方便快捷地使 用其华为账号登录您的应用和游戏。而认证服务则致力于帮助您快速 地低成本构建一个安全可靠的用户认证系统。 

两者并不冲突,认证服务支持与包括华为账号服务在内的多种第三方 认证系统对接,支持您的用户采用包括华为账号在内的多种认证方式 来登录您的应用和游戏。 

无论您的应用和游戏是否已经集成了华为账号服务,或者是否打算集 成华为账号服务,我们都推荐您使用认证服务来构建您的用户认证系 统,这有助于减少您在用户认证系统构建和运维上的投入和成本。 

## 技术支持 

当您集成 AGC 相关服务遇到问题时,可以按照以下顺序寻求帮助。 

请先仔细阅读文档,部分功能对设备和系统有限制,请参见 1.4 使用 限制。 

查看 1.17 FAQ 和错误码。 

通过智能客服查找问题解决方案。 

登录 Stack Overflow 社区和华为开发者社区参与问题讨论。 

如果以上方法仍未解决您的问题,可以通过在线工单系统与我们进行 联系。提交工单后,可登录华为开发者联盟官网,鼠标置于右上角头 “ ” 像处,在下拉框内点击 我的工单 查看工单处理进展。 

## **SDK** 隐私声明 

认证服务是由华为软件技术有限公司(注册地:江苏省南京市雨花台 区软件大道 101 号)(以下简称 “ 我们 ” 或 “ 华为 ” )面向应用开发者 “ ” (以下简称 开发者 )提供安全可靠的用户认证系统开放能力及服 务。 

开发者根据认证服务的开发文档和指南在其应用中集成了认证服务 SDK 后,我们将通过被集成的认证服务 SDK 向开发者的最终用户(以 “ ” “ ” 下简称 您 或 用户 )提供相关服务,处理开发者应用相关的数据, 相关数据中可能包含您的个人信息。华为非常重视您的个人信息和隐 私保护,我们将会按照法律要求和业界成熟的安全标准,为您的个人 信息提供相应的安全保护措施。我们将通过本声明向您说明我们如何 收集、使用、披露、保护、存储及传输您的个人信息。 

请注意:我们要求集成认证服务 SDK 的所有开发者严格遵循法律法 规、开发者协议和 1.20 SDK 合规使用指南的要求处理您的个人信息; 在接入、使用各开放能力前,我们要求开发者在其产品应用的隐私政 策中向您告知其集成 SDK 处理个人信息的基本情况,并获取您的同意 或取得其他合法性基础。但我们无法控制开发者及其开发者应用如何 处理开发者所控制的个人信息,也不对其行为负责。我们建议您认真 阅读开发者应用相关用户协议及隐私政策,在确认充分了解并同意开 发者如何处理您的个人信息后再使用开发者应用。 

#### 我们如何收集和使用您的个人信息 

华为仅会根据本声明以下所述目的和方式收集和使用您的个人信息, 如果我们要将收集的您的个人信息用于本声明未载明的其他目的,我 们会以合理的方式自行或通过开发者明确向您告知,并再次获取您的 同意或取得其他合法性基础。如果 SDK 存在扩展功能或收集和使用了 可选个人信息,我们会在下文特别说明。 

#### 认证功能 

AGC 认证服务 SDK 为第三方登录类 SDK ,支持多种账号类型的用户认 证系统, SDK 会收集开发者应用调用 SDK 接口的信息。处理的必要个 人信息包括可变设备标识符( AAID )、用户信息(邮箱地址、手机 号码、密码)、认证提供方信息( ProviderUid 、头像、昵称)、 AGC 认证服务信息( AgcUid 、头像、昵称)、应用信息(应用包名、 应用版本号)。 

#### 设备权限调用 

当您使用相应功能及服务时,我们会通过开发者应用向系统申请您设 “ ” 备的相应权限。您可以在设备的设置功能或 隐私设置 中查看权限状 态,并可自行选择开启或关闭部分或全部权限。 

开发者在集成、使用相应开放能力时,将自行决定权限的调用范围, 因此开发者应对权限的调用及用途向您进行说明。您根据开发者应用 的请求开启任一权限即代表授权我们可以处理相关个人信息来为您提 供对应服务。一旦您关闭任一权限即代表您取消了授权,我们将不再 基于对应权限继续处理相关个人信息,可能无法继续为您提供该权限 所对应的服务。请注意,您关闭权限的决定不会影响此前基于您授权 所进行的个人信息处理活动的效力。 

权限 

权限描述 

使用目的 

申请时机 

ohos.permission.INTERNET 

允许使用 Internet 网络 

用于 SDK 与后端服务 HTTPS 网络通讯 

调用认证服务登录、获取手机验证码等网络请求相关接口时使用 

#### 对未成年人的保护 

我们非常重视对未成年人个人信息的保护,华为将严格按照国家法律 法规要求对未成年人提供服务并对未成年人提供保护。如果您是未成 年人,需要您的父母或其他监护人同意您使用本应用并同意相关应用 的服务条款。父母或其他监护人也应采取适当的预防措施来保护未成 年人,包括监督其对本应用的使用。 

特别地,如果您是儿童(不满十四周岁的未成年人),在您使用我们 的服务前,请务必通知您的父母或其他监护人一起仔细阅读本声明以 及我们专门制定的《华为消费者业务儿童隐私保护声明》,并在您的 

父母或其他监护人同意或指导后,使用我们的服务或向我们提供信 息。如果您是儿童的父母或其他监护人,请确保您监护的儿童在您的 同意或指导下使用我们的服务和向我们提供信息。 

管理您的个人信息 

华为非常尊重您对个人信息的关注,我们将遵照相关法律法规的要 求,协调、支持并保障您行使访问、复制、更正、删除等个人信息主 体权利。 

由于您是通过开发者应用使用认证服务 SDK 和服务,如果您希望访 问、复制或更正与认证服务 SDK 和服务相关的个人信息,您应通过开 发者应用提供的路径实现您的个人信息主体权利。 

为保障您访问、复制、更正和删除个人信息的权利实现,我们明确要 求开发者承诺根据法律法规要求向您提供便捷的权利实现方式。同 时,我们的开放能力也向开发者提供了相关的接口,支持开发者通过 接口调用方式来执行您关于个人信息的访问、复制、更正和删除的权 “ 利请求。如开发者未按照承诺进行提供,您可以通过本声明 如何联 ” 系我们 章节中所述联系方式与我们取得联系,我们将尽力协调、支 持并保障您的上述权利实现。 

当您直接向我们提出个人信息主体权利时,为了保障您的数据安全和 其他合法权益,我们可能会对您的身份进行验证并要求您提供验证身 份所必要的个人信息,同时我们也可能会向开发者提供收集的身份验 证信息以核实您的身份。在验证确认您的身份后,我们会根据法律法 规要求及时响应您的相关请求。 

如您对您的数据主体权利有进一步要求或存在任何疑问、意见或建 “ ” 议,可通过本声明中 如何联系我们 章节中所述方式与我们取得联 系,并行使您的相关权利。 

信息存储地点及期限 

(一)存储地 

上述信息将会传输并保存至中华人民共和国境内的服务器。 

(二)存储期限 

我们仅在实现本声明所述目的所必需的时间内保留您的个人信息,并 在超出下述保留时间后删除或匿名化处理您的个人信息,除非法律法 

#### 规另有要求。 

AGC 认证服务 SDK 收集的认证提供方信息( ProviderAccessToken )仅 用于获取三方用户信息,服务端不做存储。 

AGC 认证服务信息( AgcAccessToken ),在用户取消订阅后 48h 删 除,( AgcRefreshToken )销户后 1 个月删除。 

其他信息销户后同步删除。 

此外,当我们的产品或服务发生停止运营的情形时,我们将以推送通 知、公告等形式通知您,并在合理的期限内删除您的个人信息或进行 匿名化处理。 

#### 如何联系我们 

我们指定了个人信息保护负责人,您可以通过此链接联系个人信息保 护负责人。您可以通过访问隐私问题页面与其取得联系,我们会尽快 回复。您也可以联系应用的开发者行使您的相关权利,我们在收到来 自开发者的相关请求并验证请求的真实合法性后,会积极配合响应请 求。 

如果您对我们的回复不满意,特别是当我们的个人信息处理行为损害 了您的合法权益时,您还可以通过向有管辖权的人民法院提起诉讼、 向行业自律协会或政府相关管理机构投诉等外部途径进行解决。您也 可以向我们了解可能适用的相关投诉途径的信息。 

华为将始终遵照我们的隐私政策来收集和使用您的信息。有关我们的 隐私政策,可参阅华为消费者业务隐私声明。 

## **SDK** 合规使用指南 

《中华人民共和国个人信息保护法》自 2021 年 11 月 1 日起正式施行 后,监管部门、各行业参与方和终端消费者越来越关注用户的隐私保 护问题。为了有效治理 App 违规收集使用个人信息的现象,监管部门 也陆续出台相关标准规范。 

您作为开发者为最终用户提供服务,知悉并确认将遵守适用的法律法 规和相关的标准规范,履行个人信息保护义务,并遵循合法、正当、 

必要和诚信的原则处理用户个人信息,包括但不限于《中华人民共和 国个人信息保护法》、《中华人民共和国网络安全法》、《中华人民 共和国数据安全法》以及其他适用的法律法规和相关的标准规范。 

此文档用于帮助您更好地了解认证服务 SDK 并合规使用认证服务 SDK 服务,仅适用于开发者的业务区域为中国大陆地区的场景。 基本要求 

您的产品及服务需要尊重用户隐私,遵守国家的数据保护法律和法 规。禁止参与任何干扰、干涉、损害、未授权访问任何终端设备、服 务器、网络的活动。 

(一)隐私政策要求 

您需根据法律要求以自身名义发布隐私政策,并就个人信息的处理行 为获取用户同意或取得其他合法性基础。隐私政策的要求包括但不限 于如下: 

有独立文本,不能作为用户协议的一部分。 

App 首次运行收集处理个人信息前需要以醒目方式提示用户阅读隐私 政策。隐私政策需方便用户查看,例如用户在 App 主功能界面中通过 4 次以内的点击或滑动操作即可访问。 

描述语言需要清晰通俗,符合通用语言习惯,避免使用有歧义的语 言。 

隐私政策内容要包含产品及服务收集个人信息的目的、方式和范围, 个人信息处理者的名称和联系方式等。 

您的产品及服务如涉及向第三方共享个人信息或集成了第三方的 SDK 时,需要在隐私政策中向用户进行披露和说明,获取用户的授权或同 意。 

(二)处理个人信息要求 

您的产品及服务在处理用户个人信息时,需要遵守的要求包括但不限 于如下: 

处理个人信息需要基于使用目的所必需,满足最小化原则。 

实际收集和处理的个人信息范围、使用目的需要与隐私政策的范围保 持一致。 

收集个人信息的频率需与隐私政策保持一致,禁止超频次收集个人信 息。 

有明确的个人信息到期删除机制,个人信息的存留期与隐私政策保持 一致,到期按时删除个人信息或对个人信息进行匿名化处理。 

如涉及处理不满十四周岁未成年人个人信息前,应取得未成年人的父 母或其他监护人的同意。 

如涉及处理个人信息用于个性化推荐功能或大数据分析业务的,应告 知并取得最终用户的授权同意情况下方可开展相关业务功能。 

如涉及处理敏感个人信息前,应取得最终用户的单独同意。 

如涉及跨境传输个人信息,需要按照国家网信部门会同国务院有关部 门制定的办法和相关标准进行安全评估,并符合其要求。同时您还取 得最终用户的单独同意。 

支持用户方便的行使数据主体权利,例如查阅、复制、更正、删除个 人信息等权利。 

声明 SDK 处理的个人信息 

在您接入、使用认证服务 SDK 服务前,我们要求您在 App 的隐私政策 中向用户告知我们 SDK 的名称、 SDK 提供方名称、收集个人信息类 型、使用目的、隐私政策链接,并通过弹窗等方式,在最终用户使用 SDK 提供的功能服务前,征得最终用户同意 SDK 收集用户个人信息或 取得其他合法性基础,以保障用户基本权益。 

您可以参考如下方式提供条款内容: 

以文字方式向用户告知 

第三方 SDK 名称: AGC 认证服务 SDK ( HarmonyOS ArkTS API12 版) 

第三方公司名称:华为软件技术有限公司 

收集个人信息类型:必要个人信息包括可变设备标识符( AAID )、 

用户信息(邮箱地址、手机号码、密码)、认证提供方信息 ( ProviderUid 、头像、昵称)、 AGC 认证服务信息( AgcUid 、头 像、昵称)、应用信息(应用包名、应用版本号) 

使用目的:在认证提供方系统中最终用户的唯一标识,使最终用户可 通过其在认证提供方系统中的标识来登录客户的应用,并在客户的应 用中展示最终用户的个人信息。 

隐私政策链接: 1.19 SDK 隐私声明 

以表格方式向用户告知 

第三方 SDK 名称 

第三方公司名称 

收集个人信息类型 

使用目的 

隐私政策链接 

AGC 认证服务 SDK ( HarmonyOS ArkTS API12 版) 

华为软件技术有限公司 

必要个人信息包括可变设备标识符( AAID )、用户信息(邮箱地 址、手机号码、密码)、认证提供方信息( ProviderUid 、头像、昵 称)、 AGC 认证服务信息( AgcUid 、头像、昵称)、应用信息(应用 包名、应用版本号) 

在认证提供方系统中最终用户的唯一标识,使最终用户可通过其在认 证提供方系统中的标识来登录客户的应用,并在客户的应用中展示最 终用户的个人信息。 

#### 1.19 SDK 隐私声明 

#### 权限使用要求 

我们 SDK 在提供服务时会最小化的使用系统权限,您需要根据实际使 用的功能申请对应的系统权限并向用户告知征得其同意。 

#### 权限 

权限描述 

使用目的 

申请时机 

ohos.permission.INTERNET 

允许使用 Internet 网络 

用于 SDK 与后端服务 HTTPS 网络通讯 

调用认证服务登录、获取手机验证码等网络请求相关接口时使用 

#### 延迟初始化要求 

为了避免开发者的应用在未获取您的同意前, SDK 提前启动收集使用 您的个人信息。认证服务 SDK 提供了初始化接口 Auth.init(applicationContext: Context, json: string) ,要求开发者的 应用获取您的同意后才能调用此接口初始化 SDK 。 

最小化使用功能要求 

不涉及。 

保障个人信息主体权利 

为了保障用户便捷的实现访问、复制、更正和删除个人信息,我们在 SDK 中提供了相关的接口,支持您通过接口调用方式来执行用户关于 个人信息的访问、复制、更正和删除的权利请求。 

#### 如何获取用户的数据 

您可以通过调用 Auth.getCurrentUser 获取用户数据副本。 

如何删除用户的数据 

您可以通过调用 Auth.deleteUser 删除用户数据副本。
