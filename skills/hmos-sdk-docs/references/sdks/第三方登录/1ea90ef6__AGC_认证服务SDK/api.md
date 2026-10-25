### 认证服务 API 参考 

文档版本 

01 

发布日期 

2026-05-08 

华为终端有限公司 

版权所有 © 华为终端有限公司 2026 。 保留一切权利。 

本材料所载内容受著作权法的保护,著作权由华为公司或其许可人拥 有,但注明引用其他方的内容除外。未经华为公司或其许可人事先书 面许可,任何人不得将本材料中的任何内容以任何方式进行复制、经 销、翻印、播放、以超级链路连接或传送、存储于信息检索系统或者 其他任何商业目的的使用。 

商标声明 

、、、华为,以上为华为公司的商标(非详尽清单),未经华为公司 书面事先明示许可,任何第三方不得以任何形式使用。 

注意 

华为会不定期对本文档的内容进行更新。 

本文档仅作为使用指导,文档中的所有陈述、信息和建议不构成任何 明示或暗示的担保。 

华为终端有限公司 

地址: 

广东省东莞市松山湖园区新城路 2 号 

网址: 

https://consumer.huawei.com 

目 录 

- 1 认证服务 API 1 

1.1 Overview 2 

- 1.2 Token 3 

- 1.3 TokenResult 3 

1.4 SignInResult 5 

1.5 PhoneVerifyCode 6 

1.6 EmailVerifyCode 6 

1.7 VerifyCodeParam 6 

1.8 PhoneCredentialInfo 7 

1.9 EmailCredentialInfo 7 

1.10 HwIdCredentialInfo 8 

1.11 SelfBuildCredentialInfo 8 

1.12 SignInParam 8 

1.13 PhoneInfo 8 

1.14 EmailInfo 9 

1.15 PasswordInfo 9 

1.16 Auth 10 

1.17 AuthUser 20 

1.18 AuthUserExtra 32 

1.19 VerifyCodeResult 33 

1.20 CredentialInfo 34 

1.21 ProviderType 35 

1.22 UserProfileInfo 35 

1.23 VerifyCodeAction 35 

1.24 Region 35 

1.25 AGCAuthError 36 

# **API** 认证服务 

1.1 Overview 

- 1.2 Token 

- 1.3 TokenResult 

- 1.4 SignInResult 

- 1.5 PhoneVerifyCode 

- 1.6 EmailVerifyCode 

- 1.7 VerifyCodeParam 

- 1.8 PhoneCredentialInfo 

- 1.9 EmailCredentialInfo 

- 1.10 HwIdCredentialInfo 

- 1.11 SelfBuildCredentialInfo 

- 1.12 SignInParam 

- 1.13 PhoneInfo 

- 1.14 EmailInfo 

- 1.15 PasswordInfo 

- 1.16 Auth 

- 1.17 AuthUser 

- 1.18 AuthUserExtra 

- 1.19 VerifyCodeResult 

- 1.20 CredentialInfo 

1.21 ProviderType 

1.22 UserProfileInfo 

1.23 VerifyCodeAction 

1.24 Region 

1.25 AGCAuthError 

## **Overview** 

Interface Summary 

Interface 

Description 

1.2 Token 

AGC 网关的 Access Token 结果信息。 

1.3 TokenResult 

已登录用户的 Access Token 结果信息。 

1.4 SignInResult 

登录结果信息。 

1.5 PhoneVerifyCode 

手机验证码信息类。 

1.6 EmailVerifyCode Email 验证码信息类。 

1.7 VerifyCodeParam 

获取验证码的相关参数类。 

### 1.8 PhoneCredentialInfo 

手机方式的凭证信息。 

### 1.9 EmailCredentialInfo 

Email 方式的凭证信息。 

1.10 HwIdCredentialInfo 

华为账号方式的凭证信息。 

1.11 SelfBuildCredentialInfo 

自有账号方式的凭证信息。 

1.12 SignInParam 

登录操作的参数类。 

### 1.13 PhoneInfo 

手机号码信息类,用于更新用户当前手机号码信息的操作。 

1.14 EmailInfo 

Email 账号信息类,用于更新用户当前 Email 账号信息的操作。 

1.15 PasswordInfo 

更新密码操作相关的密码信息类。 

1.16 Auth 

AGC 认证服务接口,使用 auth 获取服务。 

1.17 AuthUser 

当前登录的用户信息。 

1.18 AuthUserExtra 

用户的 Extra 信息。 

1.19 VerifyCodeResult 验证码申请结果信息。 

Types Summary 

Type 

Description 1.20 CredentialInfo 凭证信息类型。 1.21 ProviderType 渠道方式类型。 1.22 UserProfileInfo 个人账户信息。 

Enums Summary Enums 

Description 1.23 VerifyCodeAction 验证码行为枚举类。 

1.24 Region 存储地枚举类。 

1.25 AGCAuthError 异常行为枚举类。 

## **Token** 

AGC 网关的 Access Token 结果信息。 

Parameters 

Name 

Type 

Description 

expiration 

number 

获取当前 Token 的有效期。 

tokenString 

string 

获取当前 AGC 网关 Access Token 的信息。 

Sample Code 

```arkts
let token = await auth.getToken(false, Region.CN); let tokenString = token.tokenString; let expiration = token.expiration; 
```

## **TokenResult** 

已登录用户的 Access Token 结果信息。 

Method Summary 

Qualifier and Type 

Method Name and Description 

string 

getString() 

获取当前登录用户的 Access Token 信息。 

number 

getExpirePeriod() 

获取当前登录用户 Token 的有效期。 

Methods 

getString 

Method 

getString():string 

获取当前登录用户的 Access Token 信息。 

Return 

Type 

Description 

string 

### 返回当前登录用户的 Access Token 信息。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.getCurrentUser().then(user => { if (user == null) { return; } user.getToken(false).then(tokenResult =>{ let tokenString = tokenResult.getToken(); }).catch((err: BusinessError) => { // 获取 Access Token 失败 }); } 
```

getExpirePeriod 

Method 

getExpirePeriod():number 

获取当前登录用户 Token 的有效期。 

Return 

Type 

Description 

number 

返回 Token 的有效期,单位为秒。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.getCurrentUser().then(user => { if (user == null) { return; } user.getToken(false).then(tokenResult =>{ let tokenPeriod = tokenResult.getExpirePeriod(); }).catch((err: BusinessError) => { // 获取 Access Token 有效期失败 }); } 
```

## **SignInResult** 

### 登录结果信息。 

Method Summary 

Qualifier and Type 

Method Name and Description 

1.17 AuthUser 

getUser() 

返回当前登录的用户信息。 

Methods 

getUser 

Method 

getUser():1.17 AuthUser 

返回当前登录的用户信息。 

Return 

Type 

Description 

1.17 AuthUser 当前登录的用户信息。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; auth.signIn(credential).then(result=>{ let user = result.getUser(); }) 
```

## **PhoneVerifyCode** 

手机验证码信息类。 

Parameters 

Name 

Type 

Description kind 

'phone' 

标识当前的验证码类型为手机类型。 

phoneNumber string 手机号码。 countryCode string 国家码,例如中国: “86” 。 

## **EmailVerifyCode** 

Email 验证码信息类。 

Parameters 

Name 

Type 

Description 

kind 

'email' 标识当前的验证码类型为 Email 类型。 

email 

string 

Email 账号。 

## **VerifyCodeParam** 

获取验证码的相关参数类。 

Parameters 

Name 

Type 

Description 

verifyCodeType 

1.5 PhoneVerifyCode | 1.6 EmailVerifyCode 

编译器会根据其中 kind 自动推断类型,例如其内部 kind 填 为: 'phone' ,则类型被推断为 “PhoneVerifyCode” 。 

action 

1.23 VerifyCodeAction 

验证码动作类型。 

lang 

string 

验证码文字语言,例如中文: “zh_CN” 。 

sendInterval 

number 

可选,验证码超时时间,默认为 60s 。 

## **PhoneCredentialInfo** 

手机方式的凭证信息。 

Parameters 

Name 

Type 

Description 

kind 

'phone' 

标识当前的凭证种类为手机类型。 

countryCode 

string 

国家码,例如中国: “86” 。 

phoneNumber 

string 

手机号码。 

password 

string 

可选,密码。 

密码和验证码必须选择其一,若同时输入了密码和验证码,则会对密 码和验证码都做校验。 

verifyCode 

string 

可选,验证码。 

密码和验证码必须选择其一,若同时输入了密码和验证码,则会对密 码和验证码都做校验。 

## **EmailCredentialInfo** 

Email 方式的凭证信息。 

Parameters 

Name 

Type 

Description 

kind 

'email' 

标识当前的凭证种类为 Email 类型。 

email 

string 

Email 账号。 

password 

string 

可选,密码。 

密码和验证码必须选择其一,若同时输入了密码和验证码,则会对密 

码和验证码都做校验。 

verifyCode 

string 

可选,验证码。 

密码和验证码必须选择其一,若同时输入了密码和验证码,则会对密 码和验证码都做校验。 

## **HwIdCredentialInfo** 

华为账号方式的凭证信息。 

Parameters 

Name 

Type 

Description 

kind 

'hwid' 

标识当前的凭证种类为华为账号类型。 

## **SelfBuildCredentialInfo** 

自有账号方式的凭证信息。 

Parameters 

Name 

Type 

Description 

kind 

'selfBuild' 

标识当前的凭证种类为自有账号类型。 

accessToken 

string 

用户的 JWT Token 。 

## **SignInParam** 

登录操作的参数类。 

Parameters 

Name 

Type 

Description 

credentialInfo 

1.20 CredentialInfo 

凭证信息。编译器会根据其中 kind 自动推断类型,例如其内部 kind 填 为: 'phone' ,则类型被推断为 “PhoneCredentialInfo” 。 

autoCreateUser 

boolean 

可选,默认为 true 。表示如果尚未创建用户,是否自动创建。 

## **PhoneInfo** 

手机号码信息类,用于更新用户当前手机号码信息的操作。 Parameters Name Type 

Description phoneNumber string 手机号码。 countryCode string 国家码,例如中国: “86” 。 verifyCode string 手机验证码。 lang string 验证码文字语言,例如中文: “zh_CN” 。 

## **EmailInfo** 

Email 账号信息类,用于更新用户当前 Email 账号信息的操作。 

Parameters 

Name 

Type 

Description 

email 

string Email 账号。 verifyCode 

string Email 验证码。 

lang 

string 

验证码文字语言,例如中文: “zh_CN” 。所有支持的语言类型请参考 认证服务验证码语言类型。 

## **PasswordInfo** 

更新密码操作相关的密码信息类。 

Parameters 

Name 

Type 

Description 

password 

string 

新的密码。 

verifyCode 

string 

验证码。申请验证码时 VerifyCodeAction 需使用 VerifyCodeAction.RESET_PASSWORD 方式。 

providerType 

1.21 ProviderType 

渠道类型, 'email' 、 'phone' 、 'hwid' 或 'selfBuild' 。 

## **Auth** 

AGC 认证服务接口,使用 auth 获取服务。 

Method Summary Qualifier and Type 

Method Name and Description 

void 

init(applicationContext: Context, json: string) 

初始化 Auth SDK 。 

Promise<void> 

setRegion(region: string) 

### 设置存储地。 

Promise<1.2 Token> 

getToken(refresh?: boolean, region?: string) 

获取 AGC 网关的 AccessToken 。 

void 

setClientId(clientId: string) 

设置 clientId 。 

void 

setClientSecret(clientSecret: string) 

设置 clientSecret 。 Promise<1.19 VerifyCodeResult> 

requestVerifyCode(verifyCodeParam: 1.7 VerifyCodeParam) 申请验证码。 

Promise<1.4 SignInResult> 

createUser(credentialInfo: 1.20 CredentialInfo) 

创建账户。 

Promise<void> 

resetPassword(credentialInfo: 1.20 CredentialInfo) 

重置密码。 

Promise<1.4 SignInResult> 

signIn(signInParam: 1.12 SignInParam) 

登录接口,通过第三方认证来登录 AGC 平台。 

### Promise<1.4 SignInResult> 

signInAnonymously() 

匿名登录。 

Promise<void> 

deleteUser() 

在 AGC 服务器侧删除当前用户信息,并清除缓存信息。 

Promise<void> 

signOut() 

登出接口。 

Promise<1.17 AuthUser | null> 

getCurrentUser() 

获取当前登录的用户信息。 

cloudCommon.AuthProvider 

getAuthProvider() 

获取当前登录用户的 authProvider ,作为 Cloud Foundation Kit 的 CloudCommon.init 方法的入参。 

Methods 

init 

Method 

init(applicationContext: Context, json: String): void 

初始化 Auth SDK 。 

Parameters 

Name 

Type 

Description 

applicationContext 

Context 

应用上下文。 

json 

String 

由 agconnect-services.json 文件生成的 JSON 字符串。 

Sample Code 

import auth from '@hw-agconnect/auth'; onCreate(want, launchParam) { let file = 

```arkts
this.context.resourceManager.getRawFileContentSync('agconnectservices.json'); let json: string = buffer.from(file.buffer).toString(); auth.init(this.context, json); } 
```

setRegion 

Method 

setRegion(region: string): Promise<void> 

设置存储地。 

Parameters 

Name 

Type 

Description 

region 

string 

存储地,入参使用 1.24 Region 里的枚举值。 

Return 

Type 

Description 

Promise<void> 

void 类型的 Promise 对象。 

Sample Code 

import auth from '@hw-agconnect/auth'; await auth.setRegion(Region.CN) ; 

getToken 

Method 

getToken(refresh?: boolean, region?: string): Promise<1.2 Token> 获取 AGC 网关的 AccessToken 。 

Parameters 

Name 

Type 

Description 

refresh 

boolean 

### 是否强制刷新,默认为 false 。 

region 

string 

存储地。 

Return 

Type 

Description 

Promise<1.2 Token> 

Token 类型的 Promise 对象。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; let token = await auth.getToken(false, Region.CN); let tokenString = token.tokenString; let expiration = token.expiration; 
```

setClientId 

Method 

setClientId(clientId: string): void 

设置 clientId 。 

Parameters 

Name 

Type 

Description 

clientId 

### string 

AGC 平台 “ 开发与服务 > 项目设置 > 常规 ” 页面上项目的 Client ID 。 

Sample Code 

import auth from '@hw-agconnect/auth'; auth.setClientId("your clientId"); 

setClientSecret 

Method 

setClientSecret(clientSecret: string): void 

设置 clientSecret 。 

Parameters 

Name 

Type 

Description 

clientSecret 

string 

AGC 平台 “ 开发与服务 > 项目设置 > 常规 ” 页面上项目的 Client Secret 。 

Sample Code 

import auth from '@hw-agconnect/auth'; auth.setClientSecret("your clientSecret"); 

requestVerifyCode 

Method 

requestVerifyCode(verifyCodeParam: 1.7 VerifyCodeParam): Promise<1.19 VerifyCodeResult> 

### 申请验证码。 

Parameters 

Name 

Type 

Description 

verifyCodeParam 

1.7 VerifyCodeParam 

申请验证码的相关参数类。 

Return 

Type 

Description 

Promise<1.19 VerifyCodeResult> 

验证码结果的 Promise 对象。 

Sample Code 

```arkts
import { VerifyCodeAction } from '@hw-agconnect/auth'; import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; // 申请手机验证码 auth.requestVerifyCode({ action: VerifyCodeAction.REGISTER_LOGIN, lang: 'zh_CN', sendInterval: 60, verifyCodeType: { phoneNumber: '138********', countryCode: '86', kind: 'phone' } }).then(verifyCodeResult => { // 验证码申请成功 }).catch((err: BusinessError) => { // 验证码申请 失败 }); // 申请 email 验证码 auth.requestVerifyCode({ action: VerifyCodeAction.REGISTER_LOGIN, lang: 'zh_CN', sendInterval: 60, 
```

verifyCodeType: { email: 'xxxx@xxx.com', kind: 'email', } }).then(verifyCodeResult => { // 验证码申请成功 }).catch((err: BusinessError) => { // 验证码申请失败 }); 

createUser 

Method 

createUser(credentialInfo: 1.20 CredentialInfo): Promise<1.4 SignInResult> 

创建账户。 

Parameters 

Name 

Type 

Description 

credentialInfo 

### 1.20 CredentialInfo 

凭证信息。编译器会根据其中 kind 自动推断类型,例如其内部 kind 填 为: 'phone' ,则类型被推断为 “PhoneCredentialInfo” 。 

Return 

Type 

Description 

Promise<1.4 SignInResult> 

登录结果信息的 Promise 对象。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; // 创建手机用户 auth.createUser({ kind: 'phone', countryCode: '86', phoneNumber: '138********', password: '123456',// 可以给用户设置初始密码。后续可以用密码来 登录 verifyCode: 'xxxxxx' }).then(result => { // 创建用户成功 }).catch((err: BusinessError) => { // 创建用户失败 }) // 创建 email 用户 auth.createUser({ kind: 'email', email: 'xxxx@xxx.com', password: '123456',// 可以给用户设置初始密码。后续可以用密码来 登录 verifyCode: 'xxxxxx' }).then(result => { // 创建账号成功后, 默认已登录 }).catch((err: BusinessError) => { // 创建用户失败 }) 
```

resetPassword 

Method 

resetPassword(credentialInfo: 1.20 CredentialInfo): Promise<void> 

### 重置密码。 

Parameters 

Name 

Type 

Description 

credentialInfo 

1.20 CredentialInfo 

凭证信息。编译器会根据其中 kind 自动推断类型,例如其内部 kind 填 为: 'phone' ,则类型被推断为 “PhoneCredentialInfo” 。 

Return 

Type 

Description 

Promise<void> 

void 类型的 Promise 对象。 

Sample Code 

import auth from '@hw-agconnect/auth'; // 重置手机账户密码 auth.resetPassword({ kind: 'phone', password: '123456', phoneNumber: '138********', countryCode: '86', verifyCode: 'xxxxxx' }) // 重置 email 账户密码 auth.resetPassword({ kind: 'email', password: '123456', email: 'xxxx@xxx.com', verifyCode: 'xxxxxx' }) 

signIn 

Method 

signIn(signInParam: 1.12 SignInParam):Promise<1.4 SignInResult> 

登录接口,通过第三方认证来登录 AGC 平台。 

Parameters 

Name 

Type 

Parameter desc 

signInParam 

1.12 SignInParam 

登录操作的参数类。 

Return 

Type 

Description 

### Promise<1.4 SignInResult> 

### 登录结果信息的 Promise 对象。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; // 手机账户登录 auth.signIn({ credentialInfo: { kind: 'phone', phoneNumber: '138********', countryCode: '86', password: '123456' } }).then(user => { // 登录 成功 }).catch((err: BusinessError) => { // 登录失败 }); // email 账 户登录 auth.signIn({ credentialInfo: { kind: 'email', password: '123456', email: 'xxxx@xxx.com' } }).then(user => { // 登录成功 }).catch((err: BusinessError) => { // 登录失败 }); 
```

signInAnonymously 

### Method 

signInAnonymously(): Promise<1.4 SignInResult> 

### 匿名登录。 

Return 

Type 

Description 

Promise<1.4 SignInResult> 

登录结果信息的 Promise 对象。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.signInAnonymously().then(() => { // 登录成功 }).catch((err: BusinessError) => { // 登录失败 }) 
```

deleteUser 

Method 

deleteUser():Promise<void> 

### 在 AGC 服务器侧删除当前用户信息,并清除缓存信息。 

Return 

Type 

Description 

Promise<void> 

void 类型的 Promise 对象。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.deleteUser().then(() => { // 销 户成功 }).catch((err: BusinessError) => { // 销户失败 }) 
```

signOut 

Method 

signOut():Promise<void> 

登出接口。退出登录状态,删除缓存数据。 

Return 

Type 

Description 

Promise<void> 

void 类型的 Promise 对象。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; import { BusinessError } from '@kit.BasicServicesKit'; auth.signOut().then(() => { // 登出成 功 }).catch((err: BusinessError) => { // 登出失败 }) 
```

getCurrentUser 

Method 

getCurrentUser():Promise<1.17 AuthUser | null> 

获取当前登录的用户信息,如果未登录则返回 null 。 

Return 

Type 

Description 

Promise<1.17 AuthUser | null> 

用户信息的 Promise 对象。 

Sample Code 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ // 业务逻辑 } }); 

getAuthProvider 

Method 

getAuthProvider():cloudCommon.AuthProvider 

获取当前登录用户的 AuthProvider ,作为 Cloud Foundation Kit 的 CloudCommon.init 方法的入参。 

Return 

Type 

Description 

cloudCommon.AuthProvider 

Cloud Foundation Kit 的 CloudCommon.init 方法的入参。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; init(): void { let provider = auth.getAuthProvider(); cloudCommon.init({authProvider: provider}); } 
```

## **AuthUser** 

当前登录的用户信息。 

Method Summary 

Qualifier and Type 

Method Name and Description 

string 

getUid() 

获取用户 ID ,此 ID 由 AGConnect 生成。 

string 

getEmail() 获取用户邮箱。 

string 

getPhone() 

### 获取用户手机号码。 

string 

getDisplayName() 获取用户名称。 

string 

getPhotoUrl() 获取用户头像。 

string getProviderId() 

获取当前用户的提供者,第三方认证平台的名称。 

Array<Map<String, String>> 

getProviderInfo() 获取全部第三方平台的用户信息。 

Promise<1.3 TokenResult> 

getToken(forceRefresh: boolean) 

获取已登录 AGC 用户的 Access Token 信息。 

Promise<1.18 AuthUserExtra> 

getUserExtra() 

获取当前用户的 Extra 信息。 

boolean 

isAnonymous() 

是否是匿名登录用户。 

boolean 

getEmailVerified() 

获取邮箱验证标记。 

boolean 

getPasswordSetted() 

获取密码设置标记。 

Promise<1.4 SignInResult> 

link(credentialInfo: 1.20 CredentialInfo) 

当前用户关联新的登录方式。 

Promise<1.4 SignInResult> 

unlink(type: 1.21 ProviderType) 当前用户解除关联的登录方式。 

Promise<void> 

updateEmail(emailInfo: 1.14 EmailInfo) 

更新当前用户邮箱。 

Promise<void> 

updatePhone(phoneInfo: 1.13 PhoneInfo) 

更新当前用户手机号码。 

Promise<void> 

updatePassword(passwordInfo: 1.15 PasswordInfo) 

更新当前用户密码。 

Promise<void> 

updateProfile(userProfile: 1.22 UserProfileInfo) 

更新当前用户的个人信息。 

Promise<1.4 SignInResult> 

userReauthenticate(signInParam: 1.12 SignInParam) 用户登录后重认证。 

Methods 

getUid 

Method 

getUid():string 

获取用户 ID ,此 ID 由 AGC 生成。 

Return 

Type 

Description 

string 

用户 ID 。 

```arkts
Sample Code import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ let uid = user.getUid(); } }) 
```

getEmail 

Method 

getEmail():string 

### 获取用户邮箱地址。 

Return 

Type 

Description 

string 

用户 Email 。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ let email = user.getEmail(); } }) 
```

getPhone 

Method 

getPhone():string 

获取用户手机号码。 

Return 

Type 

Description 

string 

用户手机号码。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ let phone = 
```

user.getPhone(); } }) 

getDisplayName 

Method 

getDisplayName():string 

获取用户名称。 

Return 

Type 

Description 

string 用户名称。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ let phone = user.getDisplayName(); } }) 
```

getPhotoUrl 

Method 

getPhotoUrl():string 

获取用户头像的 url 。 

Return 

Type 

Description 

string 

### 用户头像的 url 。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ let phone = user.getPhotoUrl(); } }) 
```

getProviderId 

Method 

getProviderId():string 

### 获取当前用户的提供者,即第三方认证平台的名称。 

Return 

Type 

Description 

string 

用户的提供者。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ let providerId = user.getProviderId(); } }) 
```

getProviderInfo 

Method 

getProviderInfo():Array<Map<String, String>> 

获取全部第三方平台的用户信息。 

Return 

Type 

Description 

Array<Map<String, String>> 

### 当前登录的各个第三方认证平台用户信息的列表。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ let providerInfo = user.getProviderInfo(); } }) 
```

getToken 

Method 

getToken(forceRefresh:boolean):Promise<TokenResult> 

获取已登录 AGC 用户的 Access Token 信息。 

Parameters 

Name 

Type 

Description 

forceRefresh 

boolean 

可选,默认为 false 。是否强制刷新 Access Token 。 

Return 

Type 

Description 

Promise<1.3 TokenResult> 

已登录 AGC 用户的 Access Token 信息的 Promise 对象。 

Sample Code 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then((user) => { if(user){ user.getToken(false).then(tokenResult => { console.log(`accessToken:${tokenResult.getString()} ExpirePeriod: ${tokenResult.getExpirePeriod()}`); }) } }) 

getUserExtra 

Method 

getUserExtra():Promise<1.18 AuthUserExtra> 

### 获取当前用户的 Extra 信息。 

Return 

Type 

Description 

Promise<1.18 AuthUserExtra> 

用户的 Extra 信息的 Promise 对象。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ let userExtra = user.getUserExtra(); } }) 
```

isAnonymous 

### Method 

isAnonymous():boolean 

是否是匿名登录用户。 

Return 

Type 

Description 

boolean 

是否是匿名用户。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ let isAnonymous = user.isAnonymous(); } }) 
```

getEmailVerified 

Method 

getEmailVerified():boolean 

获取邮箱认证标记。 

Return 

Type 

Description 

boolean 

邮箱验证标记。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ let emailVerified = user.getEmailVerified(); } }) 
```

getPasswordSetted 

Method 

getPasswordSetted():boolean 

获取密码设置标记。 

Return 

Type 

Description 

boolean 

密码设置标记。 

Sample Code 

```arkts
import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user=>{ if(user){ let passwordSetted = user.getPasswordSetted(); } }) 
```

link 

Method 

link(credentialInfo: 1.20 CredentialInfo): Promise<1.4 SignInResult> 

当前用户关联新的登录方式。 

此接口会验证用户 Access Token 和 Refresh Token ,请确保用户 Refresh Token 在有效期内,否则会抛出错误码 203817986 ,表示用 户 Refresh Token 无效。 

收到此错误码后,请重新登录应用,获取新的 Access Token 和 Refresh Token 。 

Parameters 

Name 

Type 

Description 

credentialInfo 

1.20 CredentialInfo 

必选,凭证信息。编译器会根据其中 kind 自动推断类型,例如其内部 kind 填为: 'phone' ,则类型被推断为 “PhoneCredentialInfo” 。 

Return 

Type 

Description 

Promise<1.4 SignInResult> 

登录结果信息的 Promise 对象。 

若您在注册或登录时使用了密码,则调用 link() 接口时无需再传入 password 字段,否则会导致关联失败。 

Sample Code 

import auth from '@hw-agconnect/auth'; // 关联新的 email 账户 auth.getCurrentUser().then(user => { if(user){ user.link({ kind: 'email', password: '123456', email: 'yyyy@xxxx.com', verifyCode: 

'xxxxxx' }); } }); // 关联新的手机账户 auth.getCurrentUser().then(user => { if(user){ user.link({ kind: 'phone', phoneNumber: '138********', countryCode: '86', verifyCode: 'xxxxxx' }); } }); 

unlink 

Method 

unlink(type: 1.21 ProviderType): Promise<1.4 SignInResult> 

当前用户解除已关联的登录方式。 

此接口会验证用户 Access Token 和 Refresh Token ,请确保用户 Refresh Token 在有效期内,否则会抛出错误码 203817986 ,表示用 户 Refresh Token 无效错误码。 

收到此错误码后,请重新登录应用,获取新的 Access Token 和 Refresh Token 。 

Parameters 

Name 

Type 

Description 

type 

1.21 ProviderType 

必选,渠道类型支持 'email' 、 'phone' 、 'hwid' 或 'selfBuild' 。 

Return 

Type 

Description 

Promise<1.4 SignInResult> 

### 登录结果信息的 Promise 对象。 

Sample Code 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then(user => { if(user){ user.unlink('phone'); } }); 

updateEmail 

Method 

updateEmail(emailInfo: 1.14 EmailInfo): Promise<void> 用户邮箱登录后,更新用户邮箱地址。 

Parameters 

Name 

Type 

Description 

emailInfo 

1.14 EmailInfo 

Email 账号信息类。 

Return 

Type 

Description 

Promise<void> 

void 类型的 Promise 对象。 

Sample Code 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then((user) => { if(user){ user.updateEmail({ email: 'xxxx@xxx.com', lang: 'zh_CN', verifyCode: 'xxxxxx' }) } }) 

updatePhone 

Method 

updatePhone(phoneInfo: 1.13 PhoneInfo): Promise<void> 用户手机登录后,更新用户手机号码。 

Parameters 

Name 

Type 

Description 

phoneInfo 

1.13 PhoneInfo 

必选,手机号码信息类。 

Return 

Type 

Description 

Promise<void> 

void 类型的 Promise 对象。 

Sample Code 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then((user) => { if(user){ user.updatePhone({ countryCode: '86', phoneNumber: '138********', verifyCode: 'xxxxxx', lang: 'zh_CN' }) } }) 

updatePassword 

Method 

updatePassword(passwordInfo: 1.15 PasswordInfo): Promise<void> 

更新当前用户密码。 

Parameters 

Name 

Type 

Description 

passwordInfo 

1.15 PasswordInfo 

必选,更新密码操作相关的密码信息类。 

Return 

Type 

Description 

Promise<void> 

void 类型的 Promise 对象。 

Sample Code 

import auth from '@hw-agconnect/auth'; auth.getCurrentUser().then((user) => { if(user){ user.updatePassword({ password: '123456', verifyCode: 'xxxxxx', providerType: 'phone' }) } }) 

updateProfile 

Method 

updateProfile(userProfile: 1.22 UserProfileInfo): Promise<void> 更新当前用户的个人信息。 

Parameters 

Name 

Type 

Description userProfile 1.22 UserProfileInfo 

必选,个人账户信息类。 

Return 

Type 

Description 

Promise<void> 

void 类型的 Promise 对象。 

Sample Code 

import auth from '@hw-agconnect/auth'; 

auth.getCurrentUser().then(user => { if(user){ user.updateProfile({ photoUrl: 'https://xxx.png', displayName: 'HamonyOSUser' }) } }) 

userReauthenticate 

Method 

userReauthenticate(signInParam: 1.12 SignInParam): Promise<1.4 SignInResult> 

用户登录后重认证。 

Parameters 

Name 

Type 

Description 

signInParam 

1.12 SignInParam 

必选,登录操作的参数类。 

Return 

Type 

Description 

Promise<1.4 SignInResult> 

登录结果信息的 Promise 对象。 

Sample Code 

import auth from '@hw-agconnect/auth'; 

auth.getCurrentUser().then(user => { if (!user) { return; } user.userReauthenticate({ credentialInfo: { kind: 'phone', password: '123456', phoneNumber: '138********', countryCode: '86', verifyCode: 'xxxxxx' } }); }); 

## **AuthUserExtra** 

用户的 Extra 信息。 

Method Summary Qualifier and Type 

Method Name and Description string getCreateTime() 获取创建用户时间。 

string getLastSignInTime() 

获取最近一次登录时间。 

Methods getCreateTime Method getCreateTime(): string 

获取创建用户时间。 

Return 

Type 

Description string 返回创建用户时间。 

getLastSignInTime Method getLastSignInTime(): string 获取用户最近一次登录时间。 

Return 

Type 

Description string 返回用户最近一次登录时间。 

## **VerifyCodeResult** 

验证码申请结果信息。 

Method Summary Qualifier and Type Method Name and Description 

string 

getShortestInterval() 

获取两次发送验证码的最小时间间隔。 

string 

getValidityPeriod() 

获取验证码有效期。 

Methods 

getShortestInterval 

Method getShortestInterval(): string 

获取两次发送验证码的最小时间间隔。 

Return 

Type 

Description string 返回最小时间间隔,单位为秒。 

getValidityPeriod 

Method 

getValidityPeriod(): string 获取验证码有效期。 

Return 

Type 

Description 

string 返回验证码有效期,单位为秒。 

## **CredentialInfo** 

凭证信息类型。 

Parameters 

Type 

Description 

1.8 PhoneCredentialInfo 手机方式的凭证信息。 1.9 EmailCredentialInfo Email 方式的凭证信息。 

1.10 HwIdCredentialInfo 华为账号方式的凭证信息。 1.11 SelfBuildCredentialInfo 自有账号方式的凭证信息。 

## **ProviderType** 

### 渠道方式类型。 

Parameters 

Type 

Description 'email' Email 方式。 'phone' Phone 方式。 'hwid' 华为账号方式。 'selfBuild' 自有账号方式。 

**UserProfileInfo** 

个人账户信息。 

Parameters 

Name 

Type 

Description displayName 

string 

用来展示的个人名字。 

photoUrl 

string 

头像 url 。 

## **VerifyCodeAction** 

验证码行为枚举类。 

Enum Name 

Value 

Description VerifyCodeAction.REGISTER_LOGIN 1001 

注册 / 登录 / 重认证。 

VerifyCodeAction.RESET_PASSWORD 

1002 修改 / 重置密码。 

## **Region** 

存储地枚举类。 

Enum Name 

Value 

Description CN CN 中国区。 DE DE 德国,欧洲区。 RU RU 俄罗斯区。 SG SG 新加坡,亚洲区 

## **AGCAuthError** 

异常行为枚举类。 Parameters Name Type Description 

code 

number 

异常错误码。 

message 

string 

异常消息。 

### 错误码 

捕捉认证服务 SDK 的异常,其中 2038XXXXX 的错误码为后端服务器的 错误信息,其他的为 SDK 内部错误信息。 错误码 

错误码值 

说明 

NULL_TOKEN 

1210001 

Token 为空,建议重新登录。 

NOT_SIGN_IN 

1210002 

当前无已登录用户。 

USER_LINK_FAILED 

1210003 

用户关联失败。 

USER_UNLINK_FAILED 

1210004 

用户取消关联失败。 

ALREADY_SIGN_IN_USER 

1210005 

已经使用一个账号登录,在未登出情况下使用此账号或者其他账号登 录。 

FAIL_TO_GET_ACCESS_TOKEN 

1210006 

获取 Access Token 失败。 

FAIL_TO_UPDATE_PROFILE 

1210007 

更新用户信息失败。 

FAIL_TO_UPDATE_EMAIL 

1210008 

更新用户邮箱失败。 

CREDENTIAL_INVALID 

1210009 

凭证信息不合法。 

INVALID_EMAIL 

203817223 

输入的邮箱地址不合法。 

INVALID_PHONE 

203817224 

### 输入的手机号码不合法。 

GET_UID_ERROR 

203817728 

获取用户 ID 失败。 

UID_PRODUCTID_NOT_MATCH 

203817729 

用户 ID 和项目 ID 不匹配。 

GET_USER_INFO_ERROR 

203817730 

获取用户信息失败。 

PRODUCT_STATUS_ERROR 

203817744 

项目没有开通认证服务。 

PASSWORD_VERIFICATION_CODE_OVER_LIMIT 

203817811 

密码验证码次数超过限制。 

INVALID_TOKEN 

203817984 

Client Token 不可用。 

INVALID_ACCESS_TOKEN 

203817985 

Access Token 不可用。 

INVALID_REFRESH_TOKEN 

203817986 

Refresh Token 不可用。 

用户的 Refresh Token 过期,重新登录,获取新的 Refresh Token 。 

TOKEN_AND_PRODUCTID_NOT_MATCH 

203817987 

Token 和 product_id (即项目 ID )不匹配,建议检查 “agconnectservices.json” 是否与平台上申请的信息一致。 

AUTH_METHOD_IS_DISABLED 

203817988 

不支持的认证方式。 

ACCESS_TOKEN_OVER_LIMIT 

203817991 

AccessToken 数量超过了限定数量,配额是每个项目每个用户每小时 500 个。 

FAIL_TO_USER_LINK 

203817992 

关联用户失败。 

FAIL_TO_USER_UNLINK 

203817993 

取消用户关联失败。 

ANONYMOUS_SIGNIN_OVER_LIMIT 

### 203818019 

同一 IP 下的匿名用户登录超过限制,配额是每小时 100 个请求。 INVALID_APPID 

203818020 

AppID 不可用。 

INVALID_APPSECRET 203818021 

App Secret 不可用。 

PASSWORD_VERIFY_CODE_ERROR 

203818032 

密码和验证码错误。 

SIGNIN_USER_STATUS_ERROR 

203818036 

用户被开发者停用。 

SIGNIN_USER_PASSWORD_ERROR 

203818037 

用户密码错误。 

PROVIDER_USER_HAVE_BEEN_LINKED 

203818038 

身份验证提供方已经被其他用户绑定。 

PROVIDER_HAVE_LINKED_ONE_USER 

203818039 

### 账号中该身份验证提供方类型已经被绑定过。 

FAIL_GET_PROVIDER_USER 

203818040 

获取身份验证提供方用户失败。 

CANNOT_UNLINK_ONE_PROVIDER_USER 203818041 

不能对单一的身份验证提供方做取消关联操作。 

VERIFY_CODE_INTERVAL_LIMIT 

203818048 

在发送间隔内发送验证码。 

VERIFY_CODE_EMPTY 

203818049 

验证码为空。 

VERIFY_CODE_LANGUAGE_EMPTY 

203818050 

验证码发送语言为空。 

VERIFY_CODE_RECEIVER_EMPTY 

203818051 

验证码接收器为空。 

VERIFY_CODE_ACTION_ERROR 

203818052 

验证码类型为空。 

### VERIFY_CODE_TIME_LIMIT 

203818053 

验证码发送次数超过限制。 

ACCOUNT_PASSWORD_SAME 

203818064 

用户名密码一致。 

PASSWORD_STRENGTH_LOW 

203818065 

密码强度太低。 

UPDATE_PASSWORD_ERROR 

203818066 

更新密码失败。 

PASSWORD_SAME_AS_BEFORE 

203818067 

密码与老密码相同。 

PASSWORD_IS_EMPTY 

203818068 

密码为空。 

PASSWORD_LENGTH_ERROR 

203818071 

密码长度错误,请在 AGC“ 认证服务 - 配置 ” 页面确认密码复杂度。 SENSITIVE_OPERATION_TIMEOUT 

### 203818081 

### 敏感操作的最近登录时间超时。 

ACCOUNT_HAVE_BEEN_REGISTERED 

203818082 

账号已经被注册。 

UPDATE_ACCOUNT_ERROR 203818084 

更新账号失败。 

USER_NOT_REGISTERED 

203818087 

用户没有注册。 

VERIFY_CODE_ERROR 203818129 

验证码错误。 

USER_HAVE_BEEN_REGISTERED 

203818130 

用户已经被注册。 

REGISTER_ACCOUNT_IS_EMPTY 

203818132 

注册账号为空。 

VERIFY_CODE_FORMAT_ERROR 

203818134 

验证码格式错误。 

VERIFY_CODE_AND_PASSWORD_BOTH_NULL 

203818135 

验证码和密码都为空。 

SEND_EMAIL_FAIL 

203818240 

发送邮件失败。 

SEND_MESSAGE_FAIL 

203818241 

发送短信失败。 

CONFIG_LOCK_TIME_ERROR 

203818261 

密码 / 验证码最大尝试次数超过设定值后对账号进行冻结处理,冻结 期间用户无法使用该账号进行密码验证 / 验证码验证。
