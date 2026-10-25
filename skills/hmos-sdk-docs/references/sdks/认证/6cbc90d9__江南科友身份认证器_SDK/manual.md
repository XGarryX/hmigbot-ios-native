# **身份认证器** **_用户手册 HarmonyOS Next SDK_** 

#### 广州江南科友科技股份有限公司 

Version 1.0.0, 2024-12-11 

## **目录** 

|1.概述. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2|
|---|
|1.1.目的. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2|
|1.2.功能. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2|
|1.3.适用范围. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3|
|2.产品介绍. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4|
|2.1.系统要求. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4|
|2.2.历史版本. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4|
|3.快速开始. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5|
|3.1.导入. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5|
|3.2.存储库初始化. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5|
|4.接口. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
|4.1.数据库初始化. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
|4.2.获取所有令牌列表. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8|
|4.3.注销令牌. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8|
|4.4.根据加密的种子密钥注册动态令牌. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9|
|4.5.使用序列号和激活码注册令牌. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10|
|4.6.使用URL注册令牌. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11|
|4.7.生成动态口令. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12|
|4.8.生成序列号. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13|
|4.9.生成SM4加密密钥. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13|
|4.10. SM2加密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14|
|4.11. SM2解密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15|
|4.12. SM4/ECB加密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16|
|4.13. SM4/ECB解密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17|
|4.14. 16进制的字符串转 _Array_ 数组. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18|
|4.15._Array_ 数组转16进制的字符串. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18|
|4.16. UTF-8进制的字符串转 _Array_ 数组. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19|
|4.17._Array_ 数组转UTF-8进制的字符串. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19|
|4.18. BASE64字符串转 _Array_ 数组. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20|
|4.19._Array_ 数组转BASE64字符串. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20|
|5.类型. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22|
|5.1. TokenEntity令牌类型. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22|
|5.2. TokenStatus令牌状态枚举. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22|

Preface 

#### 身份认证器 HarmonyOS Next SDK 适用于 HarmonyOS Next 环境下的数 据保护。 

##### **版权声明** 

本文档由广州江南科友科技股份有限公司(以下简称 **江南科友** )编写,江南科友保留对本文 档的所有权和解释权,任何公司和个人未经允许,不得擅自使用、复制、修改、传播本书的 内容。 

江南科友保留有对本文档进行重新修订的权利,随时可能对本文档中出现的错误、与最新资 料不符之处等做必要的修改,这些不再另行通知,但会全部编入新版文档中。 

本文档适用于江南科友的终端安全控件 HarmonyOS Next SDK。 

第 1 页 

1. 概述 

## 1. **概述** 

身份验证器是基于动态口令实现的身份认证工具,本文中身份认证工具指的是身份认证器 HarmonyOS Next SDK。 

### 1.1. **目的** 

##### **设计目标** 

- 增强安全性:身份认证器提供了一种更安全的身份验证机制。通过使用一次性的密码 ,可以减少被盗用或猜测的风险,因为每个密码只能使用一次并在一定时间后失效。 

- 防止重放攻击:身份认证器通过在每次验证时生成不同的密码,有效地防止了重放攻 击。即使攻击者截获了一个密码,由于其只能在特定时间窗口内使用,无法在之后被 重复使用。 

- 简单易用:除了安全性,身份认证器的设计目标还包括易于使用和部署。身份认证器 的生成和验证过程简单明了,方便用户在各种应用场景下进行身份验证。 

##### **主要用途** 

- 身份验证:身份认证器用于用户身份验证,特别是在敏感操作或登录过程中,以增强 安全性。用户通过输入正确的一次性密码来证明其身份,确保只有合法用户能够访问 受保护的资源。 

- 二次验证:身份认证器也常用于二次验证的过程中。用户在输入常规用户名和密码之 后,还需要提供正确的一次性密码,以进一步验证其身份。这提供了一种额外的安全 层,防止仅依赖于常规凭据的攻击。 

- 网络交易:在进行在线支付或敏感交易时,身份认证器可用于验证用户的身份,以确 保交易的安全性。用户在进行交易时,可能会生成一个一次性密码,用于验证其身份 并完成交易。 

### 1.2. **功能** 

##### 身份认证器包括以下功能: 

- 身份认证器主要提供基于动态口令的身份验证功能 

- 身份认证器包括以下 API 功能: 

   - 注册动态令牌:使用来自 OTPS3.5(SM3) 和 OTPS3.6(SM4) 的动态令牌信息注册动 态令牌,以及使用加密的种子密钥和账号信息注册动态令牌 

   - 生成动态口令:使用指定的令牌生成当前时间周期内的口令 

   - 动态令牌管理:包括创建动态令牌、注销动态令牌、获取动态令牌 

   - 提供SM2、SM4/ECB加解密功能 

第 2 页 

1. 概述 

### 1.3. **适用范围** 

身份认证器 HarmonyOS Next SDK 使用的是动态口令这种通用的身份验证机制,适用于多个 领域和场景。以下是身份认证器的一些常见适用范围: 

- 用户登录和身份认证:身份认证器可用于用户登录过程中的身份验证。用户在输入常规的 用户名和密码之后,还需要提供正确的一次性密码来验证其身份。这提供了额外的安全层 ,防止仅依赖于常规凭据的攻击。 

- 二次验证:身份认证器也用于二次验证(Two-Factor Authentication,2FA)的实现。 在进行敏感操作或访问受保护资源时,用户除了输入常规的凭据外,还需要提供正确的一 次性密码。这种方式提供了额外的安全层,确保只有合法用户能够访问敏感信息。 

- 在线支付和电子商务:身份认证器用于增强在线支付和电子商务交易的安全性。用户在进 行支付或敏感交易时,可能会生成一个一次性密码,用于验证其身份并完成交易。这有助 于防止未经授权的访问和欺诈行为。 

- 远程访问和 VPN:身份认证器用于远程访问和虚拟私人网络(VPN)的身份验证。用户 在远程连接到内部网络或敏感资源时,需要提供正确的一次性密码来验证其身份,确保安 全的远程访问。 

- 电子邮件和社交媒体:一次性密码也可以用于电子邮件和社交媒体账户的安全验证。在进 行密码重置、账户恢复或其他敏感操作时,用户可能会生成一个一次性密码,用于验证其 身份。 

- 临时访问权限:身份认证器也用于提供临时访问权限。例如,某个应用程序或服务需要向 临时用户提供访问权限,可以生成一个一次性密码,该密码在特定时间窗口内有效,之后 失效,从而限制了访问权限的时间和范围。 

第 3 页 

2. 产品介绍 

## 2. **产品介绍** 

### 2.1. **系统要求** 

身份认证器 HarmonyOS Next SDK 仅支持在搭载 HarmonyOS Next 系统的硬件下集成。 

- 操作系统版本最低支持到 HarmonyOS NEXT Beta1 SDK(API Version 12 Release) 

### 2.2. **历史版本** 

##### **Version 1.0.0** 

- 导出SM2加解密、SM4/ECB/PKCS7加解密接口 

- 支持通过加密的种子密钥和令牌序号注册令牌;支持 OTPS3.5 和 OTPS3.6 格式的动态 令牌注册 

- 支持动态令牌的管理:包括注册、获取和注销 

- 支持生成动态口令 

第 4 页 

3. 快速开始 

## 3. **快速开始** 

本章节主要描述,如何快速地使用身份认证器 HarmonyOS Next SDK。 

### 3.1. **导入** 

将authenticator_ohos_sdk.har包放在项目一个目录中,如 

_entry/libs/authenticator_ohos_sdk.har_ ,然后在需要使用的模块中声明使用依赖,如在 _entry/oh-package.json5_ 文件中的添加声明,最后执行同步项目的依赖 

```
{
"license": "",
"devDependencies": {},
"author": "",
"name": "entry",
"description": "Please describe the basic information.",
"main": "",
"version": "1.0.0",
"dependencies": {
"authenticator_ohos_sdk": "file:./libs/authenticator_ohos_sdk.har"
  }
}
```

### 3.2. **存储库初始化** 

需要在项目中初始化存储库保存动态令牌信息,因此需要在 _EntryAbility.ets_ 文件中执行初始 化存储库的方法,例子如下 

第 5 页 

3. 快速开始 

```
import { initStore } from 'authenticator_ohos_sdk'
export default class EntryAbility extends UIAbility {
```

`async onWindowStageCreate(windowStage: window.WindowStage): Promise<void> { //` 将 `onWindowStageCreate` 

方法改为异步方法,等待存储库的初始化完成,加载页面 `try { await initStore(this.context) } catch (e) { console.error(e) } windowStage.loadContent('pages/Index', (err, data) => { if (err.code) { hilog.error(0x0000, 'testTag', 'Failed to load the content. Cause: %{public}s', JSON.stringify(err) ?? ''); return; } hilog.info(0x0000, 'testTag', 'Succeeded in loading the content. Data: %{public}s', JSON.stringify(data) ?? ''); }); } }` 

第 6 页 

4. 接口 

## 4. **接口** 

### 4.1. **数据库初始化** 

###### 接口定义 

```
initStore(content)
```

若没有初始化数据库则进行初始化,获取数据库操作实例 

##### **输入参数** 

required content 

##### **输出参数** 

无 

AppContext.Bas UIAbilityContext,保存状态的UIAbility所对 eContext 应的context 

##### **示例代码** 

`//` 如 `src/main/ets/entryability/EntryAbility.ets` 文件 

```
async onWindowStageCreate(windowStage: window.WindowStage): Promise<void> {
  try {
    await initStore(this.context)
  } catch (e) {
    console.error(e)
  }
  windowStage.loadContent('pages/Index', (err) => {
    if (err.code) {
      hilog.error(0x0000, 'testTag', 'Failed to load the content. Cause:
%{public}s', JSON.stringify(err) ?? '');
      return;
    }
    hilog.info(0x0000, 'testTag', 'Succeeded in loading the content.');
  });
}
```

第 7 页 

4. 接口 

### 4.2. **获取所有令牌列表** 

###### 接口定义 

```
listTokens()
```

获取所有令牌列表 

##### **输入参数** 

无 

##### **输出参数** 

listrequired 

Promise<TokenEntity[]> 令牌实例列表 

##### **示例代码** 

```
import { listTokens } from 'authenticator_ohos_sdk'
async function test() {
  const tokens = await listTokens()
  for (const item of tokens.entries()) {
    console.info(`index-${item[0]}`, JSON.stringify(item[1]))
  }
}
```

### 4.3. **注销令牌** 

###### 接口定义 

```
revokeToken(uid)
```

获取所有令牌列表 

##### **输入参数** 

uidrequired string 令牌唯一标识 

##### **输出参数** 

第 8 页 

4. 接口 

listrequired 

Promise<TokenEntity[]> 注销后的令牌实例列表 

##### **示例代码** 

```
import { listTokens, revokeToken } from 'authenticator_ohos_sdk'
async function test() {
  const tokens = await listTokens()
  if (tokens.length > 0) {
    const tokens2 = await revokeToken(tokens[0].uid)
  }
}
```

### 4.4. **根据加密的种子密钥注册动态令牌** 

###### 接口定义 

```
registerTokenWithSeed(encryptedSeed, account, keyID)
```

##### 使根据加密的种子密钥注册动态令牌 

##### **输入参数** 

|encryptedSeed required|number[]|加密的种子密钥|
|---|---|---|
|account required|string|令牌别名,账号信息,长度不大于256|
|keyID required|string|解密种子密钥的密钥ID|
|**输出参数**|||
|tokenId required|Promise<string>|动态令牌id|

##### **示例代码** 

第 9 页 

4. 接口 

```
import { generateKey, util, decryptWithSM2, encryptECB, registerTokenWithSeed }
from 'authenticator_ohos_sdk'
const Hex = util.Hex
const pk =
Hex.parse('9DC2C13D84A935C344A2BAD3A1517B29F28DE6A111E5FF26F25BE99E9692337B18B9
C7CF3034832C88D1A47AB74306458308CB4DD1033B7339F710AD46982776')
const vk =
Hex.parse('32E7FD71F4C80D54A63EC3EFFDC4A6CABE51E410619621CB14388B4D2E5404D1')
const seed = '50A3267FA6626C38FF00D3DF6B3658145FD243CD'
async function test() {
```

`//` 获取加密密钥 `const keyRet = await generateKey(Hex.parse(pk)) //` 解密获取密钥 

`const key = decryptWithSM2(keyRet.encryptedKey, Hex.parse(vk)) //` 加密种子 

`const encryptedSeed = encryptECB(Hex.parse(seed), key, 'PKCS7') //` 注册令牌 

```
  const tokenId = await registerTokenWithSeed(encryptedSeed, 'test',
keyRet.keyID)
}
```

### 4.5. **使用序列号和激活码注册令牌** 

###### 接口定义 

```
registerTokenWithSerial(serial, activeCode)
```

使用序列号和激活码注册令牌 

##### **输入参数** 

|serial required|string|序列号|
|---|---|---|
|activeCode required|string|激活码|
|**输出参数**|||
|tokenId required|Promise<string>|动态令牌id|

第 10 页 

4. 接口 

##### **参数校验** 

- 序列号长度必须为8 

- 激活码长度必须为12 

##### **示例代码** 

```
import { registerTokenWithSerial } from 'authenticator_ohos_sdk'
async function test() {
  const serial = '0EF9BCE1'
  const activeCode = '595144867096'
  const tokenId = await registerTokenWithSerial(serial, activeCode)
}
```

### 4.6. **使用** URL **注册令牌** 

###### 接口定义 

```
registerTokenWithURL(url)
```

##### 使用序列号和激活码注册令牌 

##### **输入参数** 

urlrequired string **输出参数** tokenIdrequired Promise<string> 动态令牌id 

包含动态令牌信息的URK字符串, 如 `otpauth://totp/unknown:harmony01? algorithm=SM4&digits=6&issuer=unk nown&period=60&secret=CDUTXA3IDOU GB5XKHMSMBM3TA4` 

##### **参数校验** 

第 11 页 

4. 接口 

- url 的协议必须是 `otpauth://` 

- url 的主机名必须是 `totp` 

- url 的路径由 `issuer:account` 组成,需要从中解析出令牌的颁发者和令牌账号信息 

- url 的查询参数中必须包含一个值为 Base32 字符串的 `secret` 参数,作为动态令牌的 种子密钥 

- url 的查询参数中可能还包含: 

   - ◦algorithm: 动态令牌的算法,只能是 `SM4` 

   - ◦digits: 生成动态口令的长度,取值范围必须再 [6, 10] 

   - ◦issuer: 动态令牌的颁发者,该值必须和路径中声明的值一致 

   - ◦period: 动态令牌的变化周期,起之范围再 [1, 60] 

##### **示例代码** 

```
import { registerTokenWithURL } from 'authenticator_ohos_sdk'
async function test() {
  const url =
'otpauth://totp/unknown:harmony01?algorithm=SM4&digits=6&issuer=unknown&period=
60&secret=CDUTXA3IDOUGB5XKHMSMBM3TA4'
  const tokenId = await registerTokenWithURL(url)
}
```

### 4.7. **生成动态口令** 

###### 接口定义 

```
generateOTP(uid, challenge)
```

生成动态口令 

##### **输入参数** 

|uid required|string|令牌唯一标识|
|---|---|---|
|challenge **输出参数**|string|挑战码,挑战码的长度不能小于4,大于64|
|otp required|Promise<string>|动态口令|

第 12 页 

4. 接口 

##### **示例代码** 

```
import { listTokens, revokeToken } from 'authenticator_ohos_sdk'
async function test() {
  const tokens = await listTokens()
  if (tokens.length > 0) {
    const otp = await generateOTP(tokens[0].uid)
  }
}
```

### 4.8. **生成序列号** 

###### 接口定义 

```
generateSerial()
```

获取所有令牌列表 

##### **输入参数** 

无 

##### **输出参数** 

serialrequired 

string 序列号,长度为8 

##### **示例代码** 

```
import { generateSerial } from 'authenticator_ohos_sdk'
const serial = generateSerial()
```

### 4.9. **生成** SM4 **加密密钥** 

###### 接口定义 

```
generateKey(public Key)
```

生成SM4加密密钥密文 

第 13 页 

4. 接口 

##### **输入参数** 

|publicKey required **输出参数**|number[]|SM2公钥|
|---|---|---|
|result required **KeyEntity类型说明**|Promise<KeyEn tity>|加密密钥实例|
|encryptedKey required|number[]|密文密文|
|keyID required|string|密钥ID|

##### **示例代码** 

```
import { generateKey, util } from 'authenticator_ohos_sdk'
const Hex = util.Hex
const pk =
Hex.parse('9DC2C13D84A935C344A2BAD3A1517B29F28DE6A111E5FF26F25BE99E9692337B18B9
C7CF3034832C88D1A47AB74306458308CB4DD1033B7339F710AD46982776')
generateKey(pk).then((result) => {
```

`console.info('` 加密密钥 `', Hex.stringify(result.encryptedKey)) console.info('` 密钥 `id', result.keyID) })` 

### 4.10. SM2 **加密** 

###### 接口定义 

```
encryptWithSM2(plaintext, public Key, mode)
```

使用公钥加密明文数据 

##### **输入参数** 

|plaintext required|number[]|明文数据内容|
|---|---|---|
|publicKey required|number[]|公钥|

第 14 页 

||4.接口|
|---|---|
|mode|'C1C3C2' |
'C1C2C3'
密文格式,默认'C1C3C2'|
|**输出参数**||
|ciphertext required|number[] 密文数据|

##### **示例代码** 

```
import { encryptWithSM2, util } from 'authenticator_ohos_sdk'
const Hex = util.Hex
const plainText = Hex.parse('313233343536')
const pk =
Hex.parse('9DC2C13D84A935C344A2BAD3A1517B29F28DE6A111E5FF26F25BE99E9692337B18B9
C7CF3034832C88D1A47AB74306458308CB4DD1033B7339F710AD46982776')
const ciphertext = encryptWithSM2(plainText, pk)
```

### 4.11. SM2 **解密** 

###### 接口定义 

```
decryptWithSM2(ciphertext, private Key, mode)
```

使用私钥解密密文数据 

##### **输入参数** 

|ciphertext required|number[]|密文数据内容|
|---|---|---|
|privateKey required|number[]|私钥|
|mode|'C1C3C2' 'C1C2C3'||
密文格式,默认'C1C3C2'|
|**输出参数**|||
|plaintext required|number[]|明文数据|

##### **示例代码** 

第 15 页 

4. 接口 

```
import { decryptWithSM2, util } from 'authenticator_ohos_sdk'
const Hex = util.Hex
const ciphertext =
Hex.parse('1B29D3326B622BD225617E21818907933E89AC30E73BC8DD3DBF32E35CE989FE931C
0827F12E632AE0430DD5833020914F45C4813A6CF81C74F0485C1279C50A56BAB36C7369FCCB09F
A8AA5995E502276D8D8A8893172D22EB594EAD21374A305C4D0B2026C');
const vk =
Hex.parse('32E7FD71F4C80D54A63EC3EFFDC4A6CABE51E410619621CB14388B4D2E5404D1')
const plaintext = decryptWithSM2(ciphertext, vk);
```

### 4.12. SM4/ECB **加密** 

###### 接口定义 

```
encryptECB(plaintext, key, padding)
```

|使用ECB算法模式加密明文数据。|
|---|

##### **输入参数** 

|plaintext required|number[]|明文数据内容|
|---|---|---|
|key required|number[]|对称密钥|
|padding required|'NoPadding' | 'PKCS5' | 'PKCS7' | '0x80' |
'Ansix923Padding'
|
'ISO10126Padding'|填充类型|
|**输出参数**|||
|ciphertext required|number[]|密文数据|

##### **示例代码** 

第 16 页 

4. 接口 

```
import { encryptECB, util } from 'authenticator_ohos_sdk'
const Hex = util.Hex
const UTF8 = util.UTF8
const key = Hex.parse('AEAF1AE5C6A685D1A973F27C8F3AAFF8')
const plaintext = UTF8.parse("test data")
const ciphertext = encryptECB(plaintext, key, 'PKCS7')
```

### 4.13. SM4/ECB **解密** 

###### 接口定义 

```
decryptECB(ciphertext, key, padding)
```

使用ECB算法模式解密密文数据。 

##### **输入参数** 

|ciphertext required|number[]|密文数据内容|
|---|---|---|
|key required|number[]|对称密钥|
|padding required|'NoPadding' | 'PKCS5' | 'PKCS7' | '0x80' |
'Ansix923Padding'
|
'ISO10126Padding'|填充类型|
|**输出参数**|||
|plaintext required|number[]|明文数据|

##### **示例代码** 

```
import { decryptECB, util } from 'authenticator_ohos_sdk'
const Hex = util.Hex
const key = Hex.parse('AEAF1AE5C6A685D1A973F27C8F3AAFF8')
const ciphertext = Hex.parse("BEBFD6601F4AEA9CF75F143F96DE0A59")
const plaintext = decryptECB(ciphertext, key, 'PKCS7')
```

第 17 页 

4. 接口 

### 4.14. 16 **进制的字符串转** _Array_ **数组** 

###### 接口定义 

```
util.Hex.parse(data)
```

16 进制的字符串转 _Array_ 数组 

##### **输入参数** 

datarequired string 待处理 16 进制的字符串数据 **输出参数** resultrequired number[] 生成的 _Array_ 数据 

##### **示例代码** 

```
import {util} from 'authenticator_ohos_sdk'
const res = util.Hex.parse('414141')
```

### 4.15. _Array_ **数组转** 16 **进制的字符串** 

###### 接口定义 

```
util.Hex.stringify(data)
```

_Array_ 数组转 16 进制的字符串 

##### **输入参数** 

datarequired number[] 待处理 _Array_ 数据 **输出参数** resultrequired string 生成的 16 进制的字符串数据 

##### **示例代码** 

第 18 页 

4. 接口 

```
import {util} from 'authenticator_ohos_sdk'
const arr = util.Hex.parse('414141')
const res = util.Hex.stringify(arr)
```

### **-** 4.16. UTF 8 **进制的字符串转** _Array_ **数组** 

###### 接口定义 

`util.UTF8.parse(data)` UTF-8 进制的字符串转 _Array_ 数组 

##### **输入参数** 

datarequired string 待处理 UTF-8 进制的字符串数据 **输出参数** resultrequired number[] 生成的 _Array_ 数据 

##### **示例代码** 

```
import {util} from 'authenticator_ohos_sdk'
const res = util.UTF8.parse('test data')
```

### **-** 4.17. _Array_ **数组转** UTF 8 **进制的字符串** 

###### 接口定义 

```
util.UTF8.stringify(data)
```

_Array_ 数组转 UTF-8 进制的字符串 

##### **输入参数** 

datarequired number[] 待处理 _Array_ 数据 

##### **输出参数** 

第 19 页 

4. 接口 

resultrequired 

生成的 UTF-8 进制的字符串数据 

string 

##### **示例代码** 

```
import {util} from 'authenticator_ohos_sdk'
const arr = util.UTF8.parse('test data')
const res = util.UTF8.stringify(arr)
```

### 4.18. BASE64 **字符串转** _Array_ **数组** 

###### 接口定义 

```
util.Helper.base64ToArray(data)
```

BASE64 字符串转 _Array_ 数组 

##### **输入参数** 

datarequired string 待处理 BASE64 字符串数据 **输出参数** resultrequired number[] 生成的 _Array_ 数据 

##### **示例代码** 

```
import {util} from 'authenticator_ohos_sdk'
const res = util.Helper.base64ToArray('QUFB')
```

### 4.19. _Array_ **数组转** BASE64 **字符串** 

###### 接口定义 

```
util.Helper.arrayToBase64(data)
```

_Array_ 数组转 BASE64 字符串 

第 20 页 

4. 接口 

##### **输入参数** 

|data required|number[]|待处理 _Array_ 数据|
|---|---|---|
|**输出参数**|||
|result required|string|生成的BASE64字符串数据|

##### **示例代码** 

```
import {util} from 'authenticator_ohos_sdk'
const arr = util.Helper.base64ToArray('QUFB')
const res = util.Helper.arrayToBase64(arr)
```

第 21 页 

5. 类型 

## 5. **类型** 

### 5.1. TokenEntity **令牌类型** 

|名称|类型|描述|
|---|---|---|
|uid|String|令牌标识ID|
|algorithm|'SM3' | 'SM4'|算法标识|
|account|String|别名、序列号或者账户信息|
|issuer|String|颁发者|
|period|Number|变化周期,单位秒,默认60|
|length|Number|动态口令长,默认长度6,取值范围为[6, 10]|
|challengeCode|String|挑战码,挑战因子,可产于到动态口令生成, 默认为空|
|status|TokenStatus|状态|
|createAt|Number|创建时间,精确到秒的时间戳|

### 5.2. TokenStatus **令牌状态枚举** 

|名称|类型|描述|
|---|---|---|
|NotActivated|Number|未激活|
|Ready|Number|就绪|
|BeLocked|Number|锁定|
|HuangUp|Number|挂起|
|Invalidate|Number|作废|

第 22 页
