# **终端安全密码模块 安全键盘组件** **_用户手册 HarmonyOS Next SDK_** 

#### 广州江南科友科技股份有限公司 

Version 2.0.6, 2025-11-03 

## **目录** 

|1.概述. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2|
|---|
|1.1.目的. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2|
|1.2.功能. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2|
|1.3.适用范围. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2|
|2.产品介绍. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3|
|2.1.系统要求. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3|
|2.2.历史版本. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3|
|3.快速开始. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5|
|3.1.导入. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5|
|3.2.使用安全键盘. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5|
|4.接口. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
|4.1. init键盘初始化. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
|4.2. SecurityKeyboard安全键盘. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
|4.3. SecurityKeyboardController键盘控制器. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9|
|4.4. CustomKey自定义按键类. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11|
|4.5. setWindowPrivacyMode设置window隐私模式. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12|
|4.6. encryptWithDigitalEnvelope数字信封加密接口. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13|
|4.7. getCipherInputWithRSA RSA加密接口. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14|
|4.8. getCipherInputWithSM2 SM2加密接口. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15|
|4.9. ciphertext2klsz klsz定制加密数据. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16|
|5.键盘控制器接口. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18|
|5.1. getCipherWithSM2获取SM2加密的输入值密文. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18|
|5.2. getCipherWithRSA获取RSA加密的输入值密文. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20|
|5.3. getPasswordStrength获取密码强度. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22|
|5.4. getUUID获取密码唯一标识. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24|
|5.5. clear清空输入值. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26|
|5.6. close关闭键盘. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28|
|5.7. ciphertext2klsz获取klsz定制加密数据. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30|
|5.8. passwordStrength获取密码强度枚举. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32|
|6.类型. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35|
|6.1. InitSetting初始化参数. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35|
|6.2. SecurityKeyboardOptions安全键盘参数. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35|
|6.3. KeyboardType键盘枚举类型. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36|

|6.4. KeyboardControllerParams键盘控制器参数. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37|
|---|
|6.5. PasswordStrength密码强度类型. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37|
|6.6. CustomKeyAttrs自定义按键属性类型. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37|
|6.7. KeyType按键枚举类型. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38|
|6.8. PaddingEnum填充枚举类型. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38|
|6.9. PasswordStrengthEnum密码强度枚举类型. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38|

Preface 

终端安全密码模块 安全键盘组件 HarmonyOS Next SDK 适用于 HarmonyOS Next 环境下的数据保护。 

##### **版权声明** 

本文档由广州江南科友科技股份有限公司(以下简称 **江南科友** )编写,江南科友保留对本文 档的所有权和解释权,任何公司和个人未经允许,不得擅自使用、复制、修改、传播本书的 内容。 

江南科友保留有对本文档进行重新修订的权利,随时可能对本文档中出现的错误、与最新资 料不符之处等做必要的修改,这些不再另行通知,但会全部编入新版文档中。 

本文档适用于江南科友的终端安全控件 HarmonyOS Next SDK。 

第 1 页 

1. 概述 

## 1. **概述** 

### 1.1. **目的** 

##### **设计目标** 

- 增强安全性:终端安全控件提供安全键盘实现对键盘输入值的机密性、完整性等不同 维度的保护。 

- 简单易用:除了安全性,终端安全控件的设计目标还包括易于使用和部署。 

##### **主要用途** 

- 键盘输入值的机密性和完整性保护:终端安全控件可以通过自定义安全键盘的方式实 现对输入值数据的机密性和完整性保护。 

### 1.2. **功能** 

终端安全控件包括以下功能: 

- 导入安全键盘组件,配合 TextInput 或 TextArea 自定义键盘方法调换系统默认的键盘 

- 使用安全键盘控制器,监听输入、删除、确认等事件以及调用清空输入值、关闭键盘、获 取加密值和获取唯一标识等方法 

### 1.3. **适用范围** 

终端安全密码模块 安全键盘组件 HarmonyOS Next SDK 实现了自定义安全键盘功能,适用于 多个领域和场景。以下是终端安全控件 HarmonyOS Next SDK 的一些常见适用范围: 

- 用户密码的机密性和完整性保护:利用安全键盘的安全模式,可以对用户输入值进行机密 性保护,并通过接口获取加密值,通过接口获取的唯一标识可以比较多个安全键盘输入的 值是否一致。 

第 2 页 

2. 产品介绍 

## 2. **产品介绍** 

### 2.1. **系统要求** 

终端安全密码模块 安全键盘组件 HarmonyOS Next SDK 仅支持在搭载 HarmonyOS Next 系 统的硬件下集成。 

- 操作系统版本最低支持到 HarmonyOS Next beat1 API Version 12 Release 

### 2.2. **历史版本** 

##### **Version 1.1.4** 

- 导出键盘组件,定义键盘类型、是否安全模式、是否随机按键顺序、设置按键颜色等 属性 

- 添加安全键盘控制器,定义清空输入、关闭键盘、获取输入唯一标识 

##### **Version 1.1.5** 

- 初始化接口参数添加theme主题,titleIcon标题图标,spaceIcon空格图标属性 

- 添加灰色主题 grey-1 

- 添加长按删除键清空输入框功能 

##### **Version 1.1.6** 

- 添加SM2+SM4、RSA+3DES数字信封加密接口 

- 打包模式更换为字节码模式 

- 修改获取SM2加密密文的接口添加padding枚举参数 

- 添加获取RSA加密密文的接口 

- 添加黑色主题 black-1 

##### **Version 2.0.0** 

- 添加昆仑数智定制接口ciphertext2klsz 

- 修复当打开键盘时路由跳转到新页面并同时打开新键盘时,无法设置隐私模式导致拦 截截屏失效的问题 

- 添加控制是否打开拦截截屏的接口 

##### **Version 2.0.1** 

- 修复异或方法参数改为Uint8数据类型进行异或运算错误问题 

##### **Version 2.0.2** 

- 添加白色-1(white-1)主题 

- 添加初始化的设置空格图标高度的参数 

第 3 页 

2. 产品介绍 

##### **Version 2.0.3** 

- 修复白色-1主题数字键盘的无乱序时的键盘值错误问题 

##### **Version 2.0.4** 

- 修复白色主-1主题键盘类型为只数字键盘时仍可以切换到字母和符号键盘的问题 

##### **Version 2.0.5** 

- 开放键盘加密接口 

##### **Version 2.0.6** 

- 添加获取键盘密码强度枚举值(返回0-7的数字)接口 

- 修复白色键盘1主题对于€£¥·等多byte符号删除逻辑不正确的问题 

第 4 页 

3. 快速开始 

## 3. **快速开始** 

本章节主要描述,如何快速地使用终端安全控件。 

### 3.1. **导入** 

将ssm_ohos_keyboard.har包放在项目一个目录中,如 _entry/libs/ssm_ohos_keyboard.har_ , 然后在需要使用的模块中声明使用依赖,如在 _entry/oh-package.json5_ 文件中的添加声明,最 后执行同步项目的依赖 

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
"ssm_ohos_keyboard": "file:./libs/ssm_ohos_keyboard.har"
  }
}
```

### 3.2. **使用安全键盘** 

使用安全键盘,需要在项目中使用 _@Builder_ 创建一个键盘组件构造器,然后在 _TextInput_ 或 者 _TextArea_ 组件的 _customKeyboard_ 方法的参数传入,例子如下 

```
import {
  SecurityKeyboard,
  KeyboardType,
  SecurityKeyboardController,
  util,
} from 'ssm_ohos_keyboard'
import { util as ohosUtil } from '@kit.ArkTS';
@Component
export default struct TestKeyboard {
```

第 5 页 

3. 快速开始 

```
  inputController: TextInputController = new TextInputController()
  keyboardController = new SecurityKeyboardController({
    inputEventCallback: (len: number, input: string) => {
      this.value = input
    },
    deleteEventCallback: (len: number, input: string) => {
      this.value = input
    },
  })
  uuid: string = ohosUtil.generateRandomUUID()
  @State value: string = ''
  type: KeyboardType = KeyboardType.Letter
```

`@Builder keyboardBuilder() { SecurityKeyboard({ keyboardId: this.uuid, type: this.type, inputController: this.inputController, controller: this.keyboardController }) } build() { Row() { TextInput({ controller: this.inputController, text: this.value }) .customKeyboard(this.keyboardBuilder())//` 绑定自定义键盘 `} } }` 

第 6 页 

4. 接口 

## 4. **接口** 

### 4.1. init **键盘初始化** 

###### 接口定义 

`init(value)` 设置安全键盘全局属性 **输入参数** valuerequired InitSetting 安全键盘全局属性设置参数 **输出参数** 无 **示例代码** `import { init } from 'ssm_ohos_keyboard' init({ title: '` 安全键盘 `', theme: 'default', //` 图片资源请在相应模块下的 `src/main/resources/base/media` 添加 `titleIcon: $r('app.media.startIcon'), spaceIcon: $r('app.media.spaceIcon'), spaceIconHeight: 38, })` 

##### **示例代码** 

### 4.2. SecurityKeyboard **安全键盘** 

###### 接口定义 

```
SecurityKeyboard(value)
```

第 7 页 

4. 接口 

实例化一个安全键盘组件对象,一般用于 `@Builder` 装饰的组件构造器中,然后将构造器通 过 `TextInput/TextArea` 组件的 `customKeyboard` 方法传入 

##### **输入参数** 

|value required|SecurityKeyboa rdOptions|安全键盘属性设置|
|---|---|---|
|**输出参数**|||
|SecurityKeyboard required|Component|安全键盘组件|

##### **示例代码** 

```
import {
  SecurityKeyboard,
  KeyboardType,
  SecurityKeyboardController,
  util,
  KeyType,
  CustomKey,
} from 'ssm_ohos_keyboard'
import { util as ohosUtil } from '@kit.ArkTS';
@Component
export default struct TestKeyboard {
  inputController: TextInputController = new TextInputController()
  keyboardController = new SecurityKeyboardController({
    inputEventCallback: (len: number, input: string) => {
      this.value = input
    },
    deleteEventCallback: (len: number, input: string) => {
      this.value = input
    },
  })
  uuid: string = ohosUtil.generateRandomUUID()
  @State value: string = ''
  type: KeyboardType = KeyboardType.Letter
  cipherInput: string = ''
  customKeys: CustomKey[] = [
    new CustomKey(KeyType.COMPLETE,{ fontColor: Color.Red })
```

第 8 页 

4. 接口 

```
  ]
```

`@Builder keyboardBuilder() { SecurityKeyboard({ keyboardId: this.uuid, value: this.value, type: this.type, inputController: this.inputController, controller: this.keyboardController, security: true, letterRandom: true, setting: { title: '` 安全键盘 `' }, keysAttrs: this.customKeys }) } build() { Row() { TextInput({ controller: this.inputController, text: this.value }) .customKeyboard(this.keyboardBuilder())//` 绑定自定义键盘 `} } }` 

### 4.3. SecurityKeyboardController **键盘控制器** 

接口定义 

```
new SecurityKeyboardController(value)
```

初始化一个 SecurityKeyboardController 对象,用于处理安全键盘组件的事件回调以及调用 相关方法 

第 9 页 

4. 接口 

##### **输入参数** 

|value|KeyboardContr ollerParams|定义安全键盘控制器的事件回调方法|
|---|---|---|
|**输出参数** object required|SecurityKeyboa rdController|安全键盘控制器实例|

##### **示例代码** 

`import { SecurityKeyboard, KeyboardType, SecurityKeyboardController, util, } from 'ssm_ohos_keyboard' import { util as ohosUtil } from '@kit.ArkTS'; @Component export default struct TestKeyboard { inputController: TextInputController = new TextInputController() keyboardController = new SecurityKeyboardController({ inputEventCallback: (length: number, input: string) => { console.info('length', length) //` 通过输入事件回显输入值 `this.value = input }, deleteEventCallback: (length: number, input: string) => { console.info('length', length) //` 通过输入事件回显输入值 `this.value = input }, sureEventCallback: (input: string) => { console.info('input', input) } }) uuid: string = ohosUtil.generateRandomUUID() @State value: string = ''` 

第 10 页 

4. 接口 

```
  type: KeyboardType = KeyboardType.Letter
```

`@Builder keyboardBuilder() { SecurityKeyboard({ keyboardId: this.uuid, value: this.value, type: this.type, inputController: this.inputController, controller: this.keyboardController }) } build() { Row() { TextInput({ controller: this.inputController, text: this.value }) .customKeyboard(this.keyboardBuilder())//` 绑定自定义键盘 `} } }` 

### 4.4. CustomKey **自定义按键类** 

###### 接口定义 

```
new CustomKey(keyType, keyAttrs)
```

返回一个按键的自定义属性实例 

##### **输入参数** 

keyTyperequired keyAttrsrequired 

##### **输出参数** 

KeyType 按键类型 CustomKeyAttrs 按键自定义属性 

第 11 页 

4. 接口 

required 

按键自定义属性实例 

CustomKey 

customKey 

##### | **示例代码** 

```
import { CustomKey, KeyType } from 'ssm_ohos_keyboard'
const customKeys: CustomKey[] = [
  new CustomKey(KeyType.INPUT, { fontColor: Color.Red })
]
```

### 4.5. setWindowPrivacyMode **设置** window **隐私模式** 

###### 接口定义 

```
setWindowPrivacyMode(uiContext, mode)
```

##### 设置window隐私模式,控制是否打开拦截截屏和录屏的功能 

##### **输入参数** 

|uiContext required|UIContext|UI组件的上下文,可通 过`this.getUIContext()`方法获取|
|---|---|---|
|mode required|boolean|是否拦截截屏和录屏|

##### **输出参数** 

无 

##### **示例代码** 

第 12 页 

4. 接口 

```
import { setWindowPrivacyMode } from 'ssm_ohos_keyboard'
@Entry
@Component
struct Keyboard {
  onPageShow(): void {
    setWindowPrivacyMode(this.getUIContext(), true)
  }
}
```

### 4.6. encryptWithDigitalEnvelope **数字信封加密接口** 

接口定义 

```
encryptWithDigitalEnvelope(data, pk, isSM2)
```

使用数字信封的方式加密数据,支持 RSA + 3DES 和 SM2 + SM4 的算法组合。3DES 使用的 是双 倍长的密钥(16 bytes);RSA 加密密钥使用 PKCS#1 填充;SM2 加密密钥不对密钥做 填充;3DES 和 SM4 加密数据使用 PKCS#5 填充数据。3DES 和 SM4 使用的算法模式为ECB 

##### **输入参数** 

|data required|string|待加密的数据,必须是16进制的字符串|
|---|---|---|
|pk required|string|用户加密的公钥,必须是16进制的字符串|
|isSM2 required|boolean|为true时使用SM2 + SM4的组合加密数据, 为false时使用RSA + 3DES的组合加密数据|
|**输出参数**|||
|result required|object|结果对象,包含 KeyCipher 密钥密文和 MessageCipher加密密文属性|

##### **示例代码** 

第 13 页 

4. 接口 

```
import { encryptWithDigitalEnvelope } from 'ssm_ohos_keyboard'
const sm2_pk =
```

`'FB396F018752B9314F5F08AF9CB5161FCE44CEA89F18B7AE20D9776B4949BDEEC6793B7E5726CA D8678ADBB241D1CF3FB180C0649E51FB707F41D6A3CBDE5FF9' const data = '31323334353637383930' const res = encryptWithDigitalEnvelope(data, sm2_pk, true) console.info('` 密钥密文 `', res.KeyCipher) console.info('` 加密密文 `', res.MessageCipher)` 

### 4.7. getCipherInputWithRSA RSA **加密接口** 

|接口定义 `getCipherInputWith` 使用RSA算法加密|`RSA(plaintext, pk,`|`padding)`|
|---|---|---|
|**输入参数**|||
|plaintext required|Uint8Array|待加密的数据|
|pk required|Uint8Array|RSA加密的公钥值|
|padding required|PaddingEnum|填充枚举类型|
|**输出参数**|||
|ciphertext required|Uint8Array|加密密文|

##### **示例代码** 

第 14 页 

4. 接口 

```
import { getCipherInputWithRSA, util, PaddingEnum } from 'ssm_ohos_keyboard'
const pk =
util.Hex.parse('308201080282010100B399C2E73CC3788D0B6C0AC6E6AB3A16A78060BCB756F
616A5F7B910B301DE020A82C20C419F77E0302BDA399D1C823CA7AC63204C226BD37D6A4E4CC0F7
4CACDAA9998F52AD96BD84745C4F4EB28DFBE63BD9D1633BB0EC9069D196819D08BC4F5E060D993
A075A80D353998A1FC5DDEFE80EA2B78057CA13A18AB4171EBDF081419266DE3E3F9CE46EC27F13
8F8A781E289E099846756134C9E2B91124DF799FFBB69A95139D6E7993F28352F5B24AB23AB33A4
4CFB5363EA638B49827F193ED63BD96E6517B9DE7506E33464B31780FC118A4DC934CB28EF5E2FA
7B5A823963405BA9A3EC1A74426234AC4D10D74D14F4F8BED78624670E6D6E2A1898EFB5020103'
)
```

`const data = util.Hex.parse('31323334353637383930') const ciphertext = getCipherInputWithRSA(data, pk, PaddingEnum.RSALoginCodeFixedPadding) console.info('` 加密密文 `', util.Hex.stringify(ciphertext))` 

### 4.8. getCipherInputWithSM2 SM2 **加密接口** 

###### 接口定义 

```
getCipherInputWithSM2(plaintext, pk, padding, mode)
```

使用SM2算法加密数据 

##### **输入参数** 

|plaintext required|Uint8Array|待加密的数据|
|---|---|---|
|pk required|Uint8Array|SM2加密公钥|
|padding required|PaddingEnum|填充枚举类型|
|mode|'C1C3C2' |
'C1C2C3'|密文格式,默认'C1C3C2'|
|**输出参数** ciphertext required|Uint8Array|加密密文|

##### **示例代码** 

第 15 页 

4. 接口 

```
import { getCipherInputWithSM2, util, PaddingEnum } from 'ssm_ohos_keyboard'
const pk =
```

`util.Hex.parse('FB396F018752B9314F5F08AF9CB5161FCE44CEA89F18B7AE20D9776B4949BDE EC6793B7E5726CAD8678ADBB241D1CF3FB180C0649E51FB707F41D6A3CBDE5FF9') const data = util.Hex.parse('31323334353637383930') const ciphertext = getCipherInputWithSM2(data, pk, PaddingEnum.SM2CodeFixedPadding) console.info('` 加密密文 `', util.Hex.stringify(ciphertext))` 

### 4.9. ciphertext2klsz klsz **定制加密数据** 

###### 接口定义 

```
ciphertext2klsz(plaintext, encryptKey, envelopeKey, timestamp)
```

使用RSA算法加密 

|**输入参数**|||
|---|---|---|
|plaintext required|Uint8Array|待加密的数据|
|encryptKey required|Uint8Array|加密PIN的SM2公钥|
|envelopeKey required|Uint8Array|加密信封的SM2公钥|
|timestamp|string|时间字符串,如'20250312103544'|
|**输出参数**|||
|encryptRes required|EnvelopeData|加密结果对象|
|**EnvelopeData类型**|||
|encryptKey required|Uint8Array|加密信封的公钥加密的密文数据|
|encryptData required|Uint8Array|对称密钥加密的数据密文数据|

##### **示例代码** 

第 16 页 

4. 接口 

```
import { ciphertext2klsz, util, PaddingEnum } from 'ssm_ohos_keyboard'
```

`const pk1 = util.Hex.parse('B8BE200E85FE5301537654D57EFEC6177C8238B7ABE3237473F4AF2ACF7F8D3 6FAED9407D37FBEC47A6EF291AD1416AB3241D85DD2C4CD6FB0CF58EBEFE13301') const data = util.Hex.parse('31323334353637383930') const pk2 = util.Hex.parse('D1B2403C618E23925206C6A6A2D310E2F54D6A6B18AA5841E8E6B2C212EF215 AA3785F5E3F56294D0FA1D0E2D783B0C7FA74DA6357E93159BCFA8F48297C9B01') const data = util.Hex.parse('31323334353637383930') const encryptRes = ciphertext2klsz(data, pk1, pk2, '20250312103544') console.info('` 加密值 `', util.Hex.stringify(encryptRes.encryptData)) console.info('` 加密密钥 `', util.Hex.stringify(encryptRes.encryptKey))` 

第 17 页 

5. 键盘控制器接口 

## 5. **键盘控制器接口** 

### 5.1. getCipherWithSM2 **获取** SM2 **加密的输入值密文** 

###### 接口定义 

```
new SecurityKeyboardController().getCipherWithSM2(pk, padding, mode)
```

已实例化的键盘控制器对象调用,根据枚举类型先对输入值进行预处理,然后使用SM2算法加 密,返回输入值密文 

##### **输入参数** 

|pk required|Uint8Array|SM2加密的公钥值|
|---|---|---|
|padding required|PaddingEnum|填充枚举类型|
|mode|'C1C3C2' 'C1C2C3'||
密文格式,默认'C1C3C2'|
|**输出参数**|||
|ciphertext required|Uint8Array|被SM2算法加密的输入值密文|

##### **示例代码** 

```
import {
  SecurityKeyboard,
  KeyboardType,
  SecurityKeyboardController,
  util,
  PaddingEnum,
} from 'ssm_ohos_keyboard'
import { util as ohosUtil } from '@kit.ArkTS';
@Component
export default struct TestKeyboard {
  inputController: TextInputController = new TextInputController()
  keyboardController = new SecurityKeyboardController({
    inputEventCallback: (len: number, input: string) => {
```

第 18 页 

5. 键盘控制器接口 

```
      this.value = input
    },
    deleteEventCallback: (len: number, input: string) => {
      this.value = input
    },
  })
  uuid: string = ohosUtil.generateRandomUUID()
  @State value: string = ''
  type: KeyboardType = KeyboardType.Letter
  pk: Uint8Array =
util.Hex.parse('1B12BADAD7E86028FFDE332A8527BC84352753BB7DD3A3DBA45D963CF269E0A
0801666B6B9C6340D061C7638AE84473444FC34AB43B0C747C3F0CB2B5042F65D')
```

`@Builder keyboardBuilder() { SecurityKeyboard({ keyboardId: this.uuid, value: this.value, type: this.type, inputController: this.inputController, controller: this.keyboardController, security: true }) } build() { Column({ space: 2 }) { Row() { TextInput({ controller: this.inputController, text: this.value }) .customKeyboard(this.keyboardBuilder())//` 绑定自定义键盘 `} Row() { Button('` 获取 `SM2` 密文 `')` 

第 19 页 

5. 键盘控制器接口 

```
          .onClick(() => {
            const ciphertext =
this.keyboardController.getCipherWithSM2(this.pk,
PaddingEnum.SM2CodeFixedPadding)
          })
      }
    }
  }
}
```

### 5.2. getCipherWithRSA **获取** RSA **加密的输入值密文** 

接口定义 

```
new SecurityKeyboardController().getCipherWithRSA(pk, padding)
```

已实例化的键盘控制器对象调用,根据枚举类型先对输入值进行预处理,然后使用RSA算法加 密,返回输入值密文 

##### **输入参数** 

|pk required|Uint8Array|RSA加密的公钥值|
|---|---|---|
|padding required|PaddingEnum|填充枚举类型|
|**输出参数**|||
|ciphertext required|Uint8Array|被RSA算法加密的输入值密文|

##### **示例代码** 

```
import {
  SecurityKeyboard,
  KeyboardType,
  SecurityKeyboardController,
  util,
  PaddingEnum,
} from 'ssm_ohos_keyboard'
import { util as ohosUtil } from '@kit.ArkTS';
@Component
```

第 20 页 

5. 键盘控制器接口 

```
export default struct TestKeyboard {
  inputController: TextInputController = new TextInputController()
  keyboardController = new SecurityKeyboardController({
    inputEventCallback: (len: number, input: string) => {
      this.value = input
    },
    deleteEventCallback: (len: number, input: string) => {
      this.value = input
    },
  })
  uuid: string = ohosUtil.generateRandomUUID()
  @State value: string = ''
  type: KeyboardType = KeyboardType.Letter
  pk: Uint8Array =
util.Hex.parse('308201080282010100B399C2E73CC3788D0B6C0AC6E6AB3A16A78060BCB756F
616A5F7B910B301DE020A82C20C419F77E0302BDA399D1C823CA7AC63204C226BD37D6A4E4CC0F7
4CACDAA9998F52AD96BD84745C4F4EB28DFBE63BD9D1633BB0EC9069D196819D08BC4F5E060D993
A075A80D353998A1FC5DDEFE80EA2B78057CA13A18AB4171EBDF081419266DE3E3F9CE46EC27F13
8F8A781E289E099846756134C9E2B91124DF799FFBB69A95139D6E7993F28352F5B24AB23AB33A4
4CFB5363EA638B49827F193ED63BD96E6517B9DE7506E33464B31780FC118A4DC934CB28EF5E2FA
7B5A823963405BA9A3EC1A74426234AC4D10D74D14F4F8BED78624670E6D6E2A1898EFB5020103'
)
  @Builder
  keyboardBuilder() {
    SecurityKeyboard({
      keyboardId: this.uuid,
      value: this.value,
      type: this.type,
      inputController: this.inputController,
      controller: this.keyboardController,
      security: true
    })
  }
  build() {
    Column({
      space: 2
    }) {
      Row() {
```

第 21 页 

5. 键盘控制器接口 

`TextInput({ controller: this.inputController, text: this.value }) .customKeyboard(this.keyboardBuilder())//` 绑定自定义键盘 `} Row() { Button('` 获取 `RSA` 密文 `') .onClick(() => { const ciphertext = this.keyboardController.getCipherWithRSA(this.pk, PaddingEnum.RSALoginCodeFixedPadding) }) } } } }` 

### 5.3. getPasswordStrength **获取密码强度** 

接口定义 

```
new SecurityKeyboardController().getPasswordStrength()
```

已实例化的键盘控制器对象调用,获取当前输入值的强度 

##### **输入参数** 

无 

##### **输出参数** 

strengthObjectrequired PasswordStreng 密码强度对象 th 

##### **示例代码** 

```
import {
  SecurityKeyboard,
  KeyboardType,
```

第 22 页 

5. 键盘控制器接口 

```
  SecurityKeyboardController,
  util,
  PasswordStrength
} from 'ssm_ohos_keyboard'
import { util as ohosUtil } from '@kit.ArkTS';
@Component
export default struct TestKeyboard {
  inputController: TextInputController = new TextInputController()
  keyboardController = new SecurityKeyboardController({
    inputEventCallback: (len: number, input: string) => {
      this.value = input
    },
    deleteEventCallback: (len: number, input: string) => {
      this.value = input
    },
  })
  uuid: string = ohosUtil.generateRandomUUID()
  @State value: string = ''
  type: KeyboardType = KeyboardType.Letter
  @Builder
  keyboardBuilder() {
    SecurityKeyboard({
      keyboardId: this.uuid,
      value: this.value,
      type: this.type,
      inputController: this.inputController,
      controller: this.keyboardController,
      security: true
    })
  }
  build() {
    Column({
      space: 2
    }) {
      Row() {
        TextInput({
          controller: this.inputController,
```

第 23 页 

5. 键盘控制器接口 

`text: this.value }) .customKeyboard(this.keyboardBuilder())//` 绑定自定义键盘 `} Row() { Button('` 获取密码强度 `') .onClick(() => { const strengthObject = this.keyboardController.getPasswordStrength() }) } } } }` 

### 5.4. getUUID **获取密码唯一标识** 

接口定义 

```
new SecurityKeyboardController().getUUID(pk)
```

##### 已实例化的键盘控制器对象调用,获取输入值唯一标识,可用于判断多个密码是否一致 

##### **输入参数** 

pkrequired **输出参数** uuidrequired 

Uint8Array SM2加密的公钥值 string 输入值唯一标识 

##### **示例代码** 

```
import {
  SecurityKeyboard,
  KeyboardType,
  SecurityKeyboardController,
  util,
} from 'ssm_ohos_keyboard'
```

第 24 页 

5. 键盘控制器接口 

```
import { util as ohosUtil } from '@kit.ArkTS';
@Component
export default struct TestKeyboard {
  inputController: TextInputController = new TextInputController()
  keyboardController = new SecurityKeyboardController({
    inputEventCallback: (len: number, input: string) => {
      this.value = input
    },
    deleteEventCallback: (len: number, input: string) => {
      this.value = input
    },
  })
  uuid: string = ohosUtil.generateRandomUUID()
  @State value: string = ''
  type: KeyboardType = KeyboardType.Letter
  pk: Uint8Array =
util.Hex.parse('1B12BADAD7E86028FFDE332A8527BC84352753BB7DD3A3DBA45D963CF269E0A
0801666B6B9C6340D061C7638AE84473444FC34AB43B0C747C3F0CB2B5042F65D')
  @Builder
  keyboardBuilder() {
    SecurityKeyboard({
      keyboardId: this.uuid,
      value: this.value,
      type: this.type,
      inputController: this.inputController,
      controller: this.keyboardController,
    })
  }
  build() {
    Column({
      space: 2
    }) {
      Row() {
        TextInput({
          controller: this.inputController,
          text: this.value
```

第 25 页 

5. 键盘控制器接口 

`}) .customKeyboard(this.keyboardBuilder())//` 绑定自定义键盘 `} Row() { Button('` 获取密码唯一标识 `') .onClick(() => { const uuid = this.keyboardController.getUUID(this.pk) }) } } } }` 

### 5.5. clear **清空输入值** 

###### 接口定义 

```
new SecurityKeyboardController().clear()
```

##### 已实例化的键盘控制器对象调用,清空当前输入值 

##### **输入参数** 

无 

##### **输出参数** 

无 

##### **示例代码** 

```
import {
  SecurityKeyboard,
  KeyboardType,
  SecurityKeyboardController,
  util,
} from 'ssm_ohos_keyboard'
import { util as ohosUtil } from '@kit.ArkTS';
@Component
```

第 26 页 

5. 键盘控制器接口 

```
export default struct TestKeyboard {
  inputController: TextInputController = new TextInputController()
  keyboardController = new SecurityKeyboardController({
    inputEventCallback: (len: number, input: string) => {
      this.value = input
    },
    deleteEventCallback: (len: number, input: string) => {
      this.value = input
    },
  })
  uuid: string = ohosUtil.generateRandomUUID()
  @State value: string = ''
  type: KeyboardType = KeyboardType.Letter
```

`@Builder keyboardBuilder() { SecurityKeyboard({ keyboardId: this.uuid, value: this.value, type: this.type, inputController: this.inputController, controller: this.keyboardController, }) } build() { Column({ space: 2 }) { Row() { TextInput({ controller: this.inputController, text: this.value }) .customKeyboard(this.keyboardBuilder())//` 绑定自定义键盘 `} Row() { Button('` 清空输入值 `') .onClick(() => {` 

第 27 页 

5. 键盘控制器接口 

```
            this.keyboardController.clear()
          })
      }
    }
  }
}
```

### 5.6. close **关闭键盘** 

接口定义 

```
new SecurityKeyboardController().clear()
```

##### 已实例化的键盘控制器对象调用,关闭控制器绑定的安全键盘 

##### **输入参数** 

无 

##### **输出参数** 

无 

##### **示例代码** 

```
import {
  SecurityKeyboard,
  KeyboardType,
  SecurityKeyboardController,
  util
} from 'ssm_ohos_keyboard'
import { util as ohosUtil } from '@kit.ArkTS';
@Component
export default struct TestKeyboard {
  inputController: TextInputController = new TextInputController()
  keyboardController = new SecurityKeyboardController({
    inputEventCallback: (len: number, input: string) => {
      this.value = input
    },
```

第 28 页 

5. 键盘控制器接口 

```
    deleteEventCallback: (len: number, input: string) => {
      this.value = input
    },
  })
  uuid: string = ohosUtil.generateRandomUUID()
  @State value: string = ''
  type: KeyboardType = KeyboardType.Letter
```

`@Builder keyboardBuilder() { SecurityKeyboard({ keyboardId: this.uuid, value: this.value, type: this.type, inputController: this.inputController, controller: this.keyboardController, }) } build() { Column({ space: 2 }) { Row() { TextInput({ controller: this.inputController, text: this.value }) .customKeyboard(this.keyboardBuilder())//` 绑定自定义键盘 `} Row() { Button('` 关闭键盘 `') .onClick(() => { this.keyboardController.clear() }) } } } }` 

第 29 页 

5. 键盘控制器接口 

### 5.7. ciphertext2klsz **获取** klsz **定制加密数据** 

接口定义 

```
new SecurityKeyboardController().ciphertext2klsz(encryptKey, envelopeKey,
timestamp)
```

已实例化的键盘控制器对象调用,根据定制规则对输入值进行加密,返回输入值密文以及密钥 密文,当没有输入值时会抛出错误 

##### **输入参数** 

|encryptKey required|Uint8Array|加密PIN的SM2公钥|
|---|---|---|
|envelopeKey required|Uint8Array|加密信封的SM2公钥|
|timestamp|string|时间字符串,如'20250312103544'|
|**输出参数**|||
|encryptRes required|EnvelopeData|加密结果对象|
|**EnvelopeData类型**|||
|encryptKey required|Uint8Array|加密信封的公钥加密的密文数据|
|encryptData required|Uint8Array|对称密钥加密的数据密文数据|

##### **示例代码** 

```
import {
  SecurityKeyboard,
  KeyboardType,
  SecurityKeyboardController,
  util,
  PaddingEnum,
} from 'ssm_ohos_keyboard'
import { util as ohosUtil } from '@kit.ArkTS';
@Component
export default struct TestKeyboard {
  inputController: TextInputController = new TextInputController()
```

第 30 页 

5. 键盘控制器接口 

```
  keyboardController = new SecurityKeyboardController({
    inputEventCallback: (len: number, input: string) => {
      this.value = input
    },
    deleteEventCallback: (len: number, input: string) => {
      this.value = input
    },
  })
  uuid: string = ohosUtil.generateRandomUUID()
  @State value: string = ''
  type: KeyboardType = KeyboardType.Letter
  pk1: Uint8Array =
util.Hex.parse('B8BE200E85FE5301537654D57EFEC6177C8238B7ABE3237473F4AF2ACF7F8D3
6FAED9407D37FBEC47A6EF291AD1416AB3241D85DD2C4CD6FB0CF58EBEFE13301')
  pk2: Uint8Array =
util.Hex.parse('D1B2403C618E23925206C6A6A2D310E2F54D6A6B18AA5841E8E6B2C212EF215
AA3785F5E3F56294D0FA1D0E2D783B0C7FA74DA6357E93159BCFA8F48297C9B01')
```

`@Builder keyboardBuilder() { SecurityKeyboard({ keyboardId: this.uuid, value: this.value, type: this.type, inputController: this.inputController, controller: this.keyboardController, security: true }) } build() { Column({ space: 2 }) { Row() { TextInput({ controller: this.inputController, text: this.value }) .customKeyboard(this.keyboardBuilder())//` 绑定自定义键盘 

第 31 页 

5. 键盘控制器接口 

```
      }
```

`Row() { Button('` 获取 `klsz` 加密信息 `')` 

```
          .onClick(() => {
            try {
              const encryptRes =
```

`this.keyboardController2.ciphertext2klsz(this.pk1, this.pk2, '20250312103544') console.info('` 加密值 `',` 

`util.Hex.stringify(encryptRes.encryptData)) console.info('` 加密密钥 `', util.Hex.stringify(encryptRes.encryptKey)) AlertDialog.show({ title: '` 结果 `', message: '` 加密成功 `' }) } catch (e) { console.error(e) AlertDialog.show({ title: '` 报错 `', message: e.message, }) } }) } } } }` 

### 5.8. passwordStrength **获取密码强度枚举** 

###### 接口定义 

```
new SecurityKeyboardController().passwordStrength()
```

已实例化的键盘控制器对象调用,获取当前输入值的密码强度枚举 

##### **输入参数** 

无 

第 32 页 

5. 键盘控制器接口 

##### **输出参数** 

strengthEnumrequired 

PasswordStreng 密码强度枚举 thEnum 

##### **示例代码** 

```
import {
  SecurityKeyboard,
  KeyboardType,
  SecurityKeyboardController,
  util
} from 'ssm_ohos_keyboard'
import { util as ohosUtil } from '@kit.ArkTS';
@Component
export default struct TestKeyboard {
  inputController: TextInputController = new TextInputController()
  keyboardController = new SecurityKeyboardController({
    inputEventCallback: (len: number, input: string) => {
      this.value = input
    },
    deleteEventCallback: (len: number, input: string) => {
      this.value = input
    },
  })
  uuid: string = ohosUtil.generateRandomUUID()
  @State value: string = ''
  type: KeyboardType = KeyboardType.Letter
  @Builder
  keyboardBuilder() {
    SecurityKeyboard({
      keyboardId: this.uuid,
      value: this.value,
      type: this.type,
      inputController: this.inputController,
      controller: this.keyboardController,
      security: true
    })
```

第 33 页 

5. 键盘控制器接口 

`} build() { Column({ space: 2 }) { Row() { TextInput({ controller: this.inputController, text: this.value }) .customKeyboard(this.keyboardBuilder())//` 绑定自定义键盘 `} Row() { Button('` 获取密码强度枚举 `') .onClick(() => { const strengthEnum = this.keyboardController.passwordStrength() }) } } } }` 

第 34 页 

6. 类型 

## 6. **类型** 

### 6.1. InitSetting **初始化参数** 

|名称|类型|描述|
|---|---|---|
|title|ResourceStr|安全键盘标题,不设置默认显示"安全键盘"|
|titleIcon|Resource|安全键盘标题左边图标|
|theme|'default' | 'grey- 1' | 'black-1' |
'white-1'|安全键盘主题,不设置默认应用默认主题
default|
|spaceIcon|Resource|安全键盘空格图标|
|spaceIconHeight|Resource|安全键盘空格图标高度,宽度根据长宽比自动 适应|

##### 主题描述 

|主题|描述|
|---|---|
|default|默认主题,包含数字、字母、特殊字符键盘|
|grey-1|灰色主题-1,只包含数字和字母键盘,字母键盘的空格无法点击|
|black-1|黑色主题-1,只包含数字和字母键盘|
|white-1|白色主题-1,包含数字和字母和特殊字符键盘,头部为切换键盘类型的三 个标签|

### 6.2. SecurityKeyboardOptions **安全键盘参数** 

|名称|类型|说明||
|---|---|---|---|
|keyboardId required|string|键盘id,可以通过 `@kit.ArkTS` `util.generateRandomUUID` 生成|的|

第 35 页 

|id|6.|类型|
|---|---|---|
|type requre|KeyboardType|双向绑定,键盘类型枚举,可通过修改 type 改变显示键盘类型|
|inputController required|TextInputContr oller |
TextAreaContro
ller|输入控制器,与 `TextInput/TextArea` 组
件进行绑定|
|controller|SecurityKeyboa rdController|键盘控制器,用于调用安全键盘组件的各个接 口|
|security|boolean|是否安全键盘,默认为false,设置为true则 安全键盘的value输入值将会返回为●,设置 为false则安全键盘的value返回真实的输入 值|
|numberRandom|boolean|数字键盘是否乱序,默认为false|
|letterRandom|boolean|字母键盘是否乱序,默认为false|
|symbolRandom|boolean|特殊字符键盘是否乱序,默认为false|
|length|number|允许输入的最大长度,默认不限制|
|setting|Partial<InitSetti ng>|安全键盘组件配置,将会覆盖全局 `init` 方法 的配置|
|keysAttrs|CustomKey[]|自定义按键属性配置|

### 6.3. KeyboardType **键盘枚举类型** 

|名称|描述|
|---|---|
|Numeric required|只显示数字键盘类型|
|Letter required|优先显示字母的混合键盘|
|NumericMix required|优先显示数字的混合键盘|
|SymbolMix required|优先显示特殊字符的混合键盘|

第 36 页 

6. 类型 

### 6.4. KeyboardControllerParams **键盘控制器参数** 

|名称|类型|说明|
|---|---|---|
|inputEventCallback|(length: number, input: string) ⇒ void|数据输入事件回调方法,回调函数参数包含输 入值的长度和输入值,注意安全键盘模式下返 回的是如'●●●●●●'不可见字符|
|deleteEventCallback|(length: number, input: string) ⇒ void|删除事件回调方法,回调函数参数包含输入值 的长度和输入值,注意安全键盘模式下返回的 是如'●●●●●●'不可见字符|
|sureEventCallback|(input: string) ⇒ void|确认事件回调方法,默认为关闭键盘,注意安 全键盘模式下返回的是如'●●●●●●'不可见字 符|

### 6.5. PasswordStrength **密码强度类型** 

|属性|描述|hasNumber required|
|---|---|---|
|boolean|是否包含数字|hasUppercase required|
|boolean|是否包含小写字 母|hasLowercase required|
|boolean|是否包含大写字 母|hasSpecialChars required|

### 6.6. CustomKeyAttrs **自定义按键属性类型** 

|名称|类型|描述|
|---|---|---|
|fontColor|ResourceColor|按键字体颜色|
|backgroundColor|ResourceColor|按键背景颜色|
|shadowColor|ResourceColor|按键阴影颜色|

第 37 页 

6. 类型 

### 6.7. KeyType **按键枚举类型** 

|名称|描述|
|---|---|
|INPUT required|输入类型按键|
|DELETE required|删除按键|
|NUMERIC required|切换数字键盘按键|
|CAPSLOCK required|切换大小写按键|
|SPECIAL required|切换特殊字符按键|
|LETTER required|切换字母按键|
|COMPLETE required|确认按键|
|6.8. PaddingEnum 名称|**填充枚举类型** 描述|
|NoPadding required|不填充|
|XORPadding required|异或模式填充|
|RandomFillPadding required|随机数模式填充|
|CodeLengthPadding required|密码长度前置填充|
|RSALoginCodeFixedPadding requir|ed 国际登录密码固定填充|
|RSATransactionCodeFixedPaddi|ng required 国际交易密码固定填充|
|SM2CodeFixedPadding required|国密固定填充|

### 6.9. PasswordStrengthEnum **密码强度枚举类型** 

描述

|名称|强度|描述|
|---|---|---|

第 38 页 

||6.类|型|
|---|---|---|
|PasswordIsEmpty required|0|密码为空|
|PasswordLenLessThanSix required|1|密码长度在1 - 5字符 之间|
|PasswordLenMoreThanFiveIncludeOn eCharacterType required|2|密码长度>= 6字符,且包含字母、数字、 特殊字符中的一种|
|PasswordLenMoreThanFiveIncludeT woCharacterType required|3|密码长度>= 6字符,且包含字母、数字、 特殊字符中的两种|
|PasswordLenMoreThanFiveIncludeTh reeCharacterType required|4|密码长度>= 6字符,且包含大写、小写字 母、数字、特殊字符中的三种|
|PasswordLenMoreThanFiveIncludeAll CharacterType required|5|密码长度>= 6字符,且包含大写和小写字 母、数字、特殊字符|
|PasswordLenEqualToSixIncludeOnlyN umber required|6|密码长度== 6字符,仅包含数字|
|PasswordLenMoreThanFiveIncludeNu mberAndLetter required|7|密码长度>= 6字符,仅包含字母和数字|

第 39 页
