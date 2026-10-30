# 屹通安全键盘 SDK 使用文档 

本文档面向集成 YTKeyBoardLib 的 HarmonyOS 开发者,说明 SDK 的安装、配置、键盘类型、加密解密、安全设置和使用建议。 

项目 

说明 

SDK 名称 

屹通安全键盘 SDK 

包名 

@yitong/ytkeyboardlib 

主入口 

Index.ets 

SDK 类型 

HarmonyOS HAR 

当前版本 

1.0.0 

# 1. 功能概览 

YTKeyBoardLib 是面向 HarmonyOS 应用的自定义安全键盘组件库, 提供文本输入安全键盘、 Web 场景键盘、多种键盘类型、输入加密、 乱序排列、音效振动和防截屏等能力。 

能力模块 

主要 API 

用途 

文本输入键盘 

YTTextInput 、 YTKeTextInputSetting 

提供安全输入组件,支持自定义输入属性、事件回调和加密输出。 

Web 场景键盘 

YTWebInput 、 YTWebKeyBoardManager 

支持 Web 页面弹出自定义安全键盘,管理键盘的弹出、隐藏和输入 回调。 

全局配置管理 

YTKeyBoardManager 

管理全局键盘配置和解密加密输入值,支持全局配置优先级覆盖。 键盘配置参数 

KBConfigParam 

统一管理加密、乱序、最大长度、音效、振动、防截屏等所有键盘行 为配置。 输入属性与事件 

YTKeTextInputAttribute 、 YTKeTextInputEvent 

定义输入框样式属性和输入变化 / 焦点变化回调。 

键盘头部定制 

YTKeTextInputHead 

自定义键盘标题、图标和完成按钮文字。 

键盘类型 

YTKeyboardType 

枚举定义 9 种键盘类型:全字母、数字、符号、身份证、金额等。 输入加密 

KBDataSourceEnCrypt 、 KeyBoardEnCrypt 

基于 SM4 的按键级加密,支持加密值回调和统一解密。 

交互反馈 

YTKeyBoardSoundPool 、 YTKeyBoardVibrator 

提供按键音效播放和振动反馈能力。 

# 2. 安装与引入 

在宿主工程中引入 HAR 依赖后,可从包入口按需导入需要的能力。 包名以 oh-package.json5 中的 name 值为准。 

// oh-package.json5 

{ 

"dependencies": { 

"@yitong/ytbasiccorelib": "file:../YTBasicCoreLib" 

"@yitong/ytcryptolib": "file:./libs/YTCryptoLib.har" 

"@yitong/ytkeyboardlib": "file:../YTKeyBoardLib" 

} 

} 

import { 

YTTextInput, 

YTWebInput, 

YTKeyboardType, 

YTKeTextInputSetting, 

YTKeTextInputAttribute, 

YTKeTextInputEvent, 

YTKeTextInputHead, 

YTKeyBoardManager, 

YTWebKeyBoardManager, 

YTInputKeyBoardManager 

} from '@yitong/ytkeyboardlib'; 

# 3. 初始化建议 

YTKeyBoardLib 的键盘组件在使用时自动完成内部初始化(数据源、 加密密钥、音效池等),无需额外调用初始化方法。但建议在使用前 注意以下事项: 

加密密钥在进程生命周期内有效,进程重启后密钥会变化,之前加密 的值将无法解密。 

文本输入场景的防截屏功能需要传入 window.WindowStage ,建议在 UIAbility 中获取后设置到 inputWindow.stage 。 

全局键盘配置通过 YTKeyBoardManager.getInstance().config 设置, 建议在应用启动阶段完成。 

按键音效资源( key_pressed_sound.ogg )已内置在 SDK rawfile 中, 无需额外配置。 

# 4. 常用能力示例 

# 4.1 文本输入安全键盘 

YTTextInput 是最常用的安全输入组件,通过 YTKeTextInputSetting 统一管理输入属性和键盘配置。 

@State inputSetting: YTKeTextInputSetting = new YTKeTextInputSetting(); 

@State encryptValue: string = ''; 

aboutToAppear() { 

# // 设置键盘类型 

this.inputSetting.keyBoardType = YTKeyboardType.YTKeyboardTypeNumberSupplement; 

# // 设置输入属性 

this.inputSetting.inputAttribute.placeholder = ' 请输入密码 '; 

this.inputSetting.inputAttribute.textSize = 18; 

this.inputSetting.inputAttribute.inputWidth = 300; 

this.inputSetting.inputAttribute.inputHeight = 48; 

// 设置键盘头部 

this.inputSetting.inputHead.head_title = ' 安全输入 '; 

this.inputSetting.inputHead.head_buttonTitle = ' 完成 '; 

// 设置加密和乱序 

this.inputSetting.config.isEncrypt = true; 

this.inputSetting.config.isRandom = true; 

this.inputSetting.config.maxLength = 6; 

# // 设置输入事件 

this.inputSetting.inputEvent.onChange = (value: string, enValue: string) => { 

this.encryptValue = enValue; 

}; 

this.inputSetting.inputEvent.onEditChange = (isEditing: boolean) => { 

// isEditing=true 获得焦点, false 失焦 

}; 

} 

build() { 

YTTextInput({ 

encryptValue: $encryptValue, 

inputSetting: $inputSetting 

}) 

} 

# 4.2 自定义键盘头部 

可通过 YTKeTextInputHead 配置键盘头部,也可通过 headView 插 槽完全自定义头部视图。 

// 方式一:通过配置自定义头部文字 

this.inputSetting.inputHead.head_title = ' 安全密码键盘 '; 

this.inputSetting.inputHead.head_buttonTitle = ' 确认 '; 

// 方式二:通过 @BuilderParam 插槽完全自定义头部 

@Builder customHeadView() { 

Row() { 

Text(' 自定义标题 ').fontSize(16).fontColor('#333') 

Blank() 

Button(' 关闭 ').onClick(() => { /* 关闭键盘 */ }) 

} 

.width('100%') 

.height(44) 

.padding({ left: 16, right: 16 }) 

} 

// 使用 

YTTextInput({ 

encryptValue: $encryptValue, 

inputSetting: $inputSetting, 

headView: this.customHeadView 

}) 

# 4.3 键盘类型选择 

YTKeyboardType 枚举定义了 9 种键盘类型,覆盖不同的输入场景。 枚举值 

名称 

适用场景 

YTKeyboardTypeNone (0) 

无类型 

默认值,使用前需设置为具体类型。 

YTKeyboardTypeLetter (1) 

全字母键盘 

纯字母输入,如姓名。 

YTKeyboardTypeNumberSupplement (2) 

# 可切换数字键盘 

数字输入为主,可切换到字母键盘,如密码。 

YTKeyboardTypeSpecial (3) 

全符号键盘 

特殊符号输入。 

YTKeyboardTypeLetterWithNumber (4) 

数字 + 字母键盘 

顶部数字行 + 下方字母,如通用文本。 

YTKeyboardTypeIDCard (5) 

身份证键盘 

数字 + X ,限制 18 位, X 仅可输入一次。 YTKeyboardTypeMoney (6) 

金额键盘 

数字 + 小数点,支持小数位数控制。 

YTKeyboardTypeOnlyNumber (7) 

纯数字键盘 

仅数字,不可切换。 

YTKeyboardTypeLetterNumberRemoveChart (8) 

数字字母键盘 

数字 + 字母,无特殊字符切换按钮。 

# 4.4 输入加密与解密 

设置 config.isEncrypt = true 后,每个按键字符都会被 SM4 独立加 

# 密,以分号分隔存储。获取加密字符串后可通过 YTKeyBoardManager 统一解密。 

# // 设置加密模式 

this.inputSetting.config.isEncrypt = true; 

# // 在 onChange 回调中获取加密值 

this.inputSetting.inputEvent.onChange = (value: string, enValue: string) => { 

this.encryptValue = enValue; // 加密字符串,如 "enc1;enc2;enc3" 

}; 

# // 需要明文时解密 

const plainText = 

YTKeyBoardManager.getInstance().decryptedKeyValue(this.encryptValue); 

加密算法使用 SM4 ,密钥在 KBDataSourceEnCrypt 首次初始化时随 机生成。 

加密字符串以分号分隔,每段为一个按键字符的密文。 

加密模式下,输入框显示为等长的 * 号掩码。 

解密密钥仅当前进程生命周期内有效,进程重启后无法解密历史数 据。 

# 4.5 金额键盘 

金额键盘自动处理小数点和前导零,通过 maxDecimal 控制小数位 数。 

this.inputSetting.keyBoardType = YTKeyboardType.YTKeyboardTypeMoney; 

this.inputSetting.config.maxDecimal = 2; // 最大 2 位小数 

this.inputSetting.config.maxLength = 10; // 最大 10 个字符 

this.inputSetting.config.isLengthWithDecimal = false; // false= 小 数点计入长度, true= 不计入 

# 4.6 身份证键盘 

身份证键盘限制最大 18 位, X 仅可输入一次且只能在最后位。 

this.inputSetting.keyBoardType = YTKeyboardType.YTKeyboardTypeIDCard; 

this.inputSetting.config.maxLength = 18; // 默认限制 18 位 

# 4.7 按键乱序 

设置 config.isRandom = true 启用按键乱序排列,每次键盘类型切换 时使用 Fisher-Yates 算法重新洗牌。 

this.inputSetting.config.isRandom = true; // 启用乱序排列 

# 4.8 防截屏与窗口保护 

设置 config.isScreenShotEnable = false (默认值)可启用防截屏。 文本输入场景下在输入框获得焦点时自动开启窗口隐私模式,失焦时 关闭。 

// 设置窗口上下文(用于防截屏) 

this.inputSetting.inputWindow.stage = windowStage; // 传入 UIAbility 的 WindowStage 

this.inputSetting.inputWindow.context = this.context; // 传入上下 文 

# // 启用防截屏(默认 false ,即默认启用防截屏) 

this.inputSetting.config.isScreenShotEnable = false; 

# // 如需允许截屏 

this.inputSetting.config.isScreenShotEnable = true; 

# 4.9 按键音效与振动 

通过 bSound 和 bVibrator 开关控制按键音效和振动反馈。 

this.inputSetting.config.bSound = true; // 开启按键音效 

this.inputSetting.config.bVibrator = true; // 开启振动反馈 

音效使用内置 rawfile 资源 key_pressed_sound.ogg ,无需额外配置。 振动使用系统 haptic.effect.soft 效果,首次使用时检查设备是否支 持。 

音效和振动仅在对应开关为 true 时触发,不影响键盘核心功能。 4.10 Web 场景键盘 

Web 场景下通过 YTWebKeyBoardManager 管理键盘弹窗的生命周 期,键盘内容使用 YTWebInput 组件渲染。 

# // 1. 设置键盘参数和回调 

YTWebKeyBoardManager.getInstance().setParams( 

YTKeyboardType.YTKeyboardTypeNumberSupplement, 

new KBConfigParam() 

); 

YTWebKeyBoardManager.getInstance().onChange = (data: string, enData: string) => { 

// data= 明文 , enData= 加密值 

}; 

YTWebKeyBoardManager.getInstance().onShow = (err) => { 

# // 键盘显示回调 

}; 

YTWebKeyBoardManager.getInstance().onHide = (err) => { 

# // 键盘隐藏回调 

}; 

YTWebKeyBoardManager.getInstance().defaultValue = ' 初始值 '; 

// 2. 弹出键盘 

YTWebKeyBoardManager.getInstance().showKeyBoard('pages/ KeyboardPage', this.context); 

// 3. 隐藏键盘 

YTWebKeyBoardManager.getInstance().hidKeyBoard(); 

// 4. KeyboardPage 中使用 YTWebInput 

build() { 

YTWebInput({ headView: this.customHeadView }) 

} 

# 4.11 全局配置管理 

YTKeyBoardManager 提供全局键盘配置,当全局配置的 keyBoardName 非空且具体键盘未设置 keyBoardName 时,全局配置 将覆盖具体键盘配置。 

# // 设置全局配置 

YTKeyBoardManager.getInstance().config.keyBoardName = 'global_password'; 

YTKeyBoardManager.getInstance().config.isEncrypt = true; 

YTKeyBoardManager.getInstance().config.isRandom = true; YTKeyBoardManager.getInstance().config.maxLength = 6; 

# // 解密加密输入值 

const plainText = YTKeyBoardManager.getInstance().decryptedKeyValue(encryptValue); 

# 5. 配置参数参考 

KBConfigParam 包含所有键盘行为配置参数。 

参数 类型 

默认值 

说明 

keyBoardName 

string '' 

键盘名称,用于全局配置匹配。 

isEncrypt 

boolean 

false 

是否加密输入值,加密后每个字符 SM4 加密并以分号分隔。 

isRandom 

boolean 

false 

# 按键是否乱序排列,每次键盘切换时重新洗牌。 

upperDefault 

boolean 

false 

# 字母键盘是否默认大写模式。 

sm_x 

string? '' 

SM2 公钥 X 坐标(预留配置,当前未启用)。 

sm_y string? '' 

SM2 公钥 Y 坐标(预留配置,当前未启用)。 

isNeedHighlight 

boolean? 

false 

按键是否高亮显示。 

needBigStatus 

boolean? 

false 

是否开启按键放大效果。 

maxLength 

number? 

undefined 

最大输入长度,不限制。 

maxDecimal 

number? 

undefined (实际默认 2 ) 

金额键盘最大小数位数。 

isLengthWithDecimal 

boolean? 

undefined (即 false ) 

最大长度是否计算小数点。 true= 不计算, false= 计算。 isScreenShotEnable 

boolean? 

false 

是否允许截屏。 false= 防截屏(默认), true= 允许截屏。 needBgViewHide 

boolean? 

undefined 

是否点击悬浮背景区域收起键盘。 

bgViewColor 

ResourceColor? 

undefined 

# 键盘悬浮区域背景颜色。 

bSound 

boolean? 

undefined 

是否开启按键音效。 

bVibrator 

boolean? undefined 

是否开启按键振动反馈。 

customData 

string | object? undefined 

自定义参数,可传递业务数据。 

6. 输入属性与事件参考 

6.1 输入属性 

YTKeTextInputAttribute 用于定义输入框的外观和交互属性。 属性 类型 

默认值 

说明 

placeholder 

string | Resource 

'' 

占位文本。 

placeholderSize number 18 

占位文字大小。 placeholderColor Color | Resource Color.Gray 占位文字颜色。 backgroundColor Color | Resource Color.Gray 输入框背景色。 textColor 

Color | Resource Color.Black 输入文字颜色。 textSize number 

18 

输入文字大小。 

inputType 

InputType InputType.Normal 输入框类型。 inputWidth number 200 输入框宽度。 inputHeight number 40 输入框高度。 textAlign TextAlign TextAlign.Start 文字对齐方式。 controller TextInputController new TextInputController() 输入框控制器。 

copyOption CopyOptions 

# CopyOptions.None 

是否允许粘贴,默认不允许。 

dFocus 

boolean 

false 

是否自动聚焦。 

6.2 输入事件 

YTKeTextInputEvent 提供输入变化和焦点变化的回调。 

回调 

签名 

说明 

onChange 

(data: string, enData: string) => void 

键盘输入变化回调。 data= 明文值, enData= 加密值。 onEditChange 

(isEditing: boolean) => void 

焦点变化回调。 true= 获得焦点, false= 失焦。 

6.3 键盘头部配置 

YTKeTextInputHead 用于自定义键盘顶部标题栏。 

属性 

类型 

默认值 

# 说明 

head_title 

string | Resource 

' ' 上海屹通安全键盘 

标题文字。 

head_image 

string | Resource? undefined 标题图标。 

head_buttonTitle string | Resource ' ' 完成 完成按钮的文字。 

# 7. 权限与合规说明 

YTKeyBoardLib 的 HAR 模块自身未声明系统权限。宿主应用应按实 际启用能力声明和申请权限。 

能力 

可能涉及权限或系统能力 

建议 

按键振动 

如平台要求,宿主应用按需声明振动相关权限。 

仅在用户开启振动反馈时触发。 

# 按键音效 

播放 SDK rawfile 中的按键音资源,通常不需要录音、存储等权限。 音效资源已内置,无需额外权限。 

防截屏 

调用窗口隐私模式能力,通常不需要运行时权限。 

在输入敏感信息(密码、身份证等)时建议启用。 

Web 键盘 

宿主 Web 页面和通信能力由宿主应用自行合规处理。 

Web 场景的输入数据安全由宿主应用负责。 

输入加密 

使用 SM4 算法在本地加密,不涉及网络传输。 

加解密均在本地完成,密钥不落盘。 

开发者应遵循最小必要原则,仅在用户触发具体输入场景时启用加 密、音效、振动和窗口保护等能力。不应将加密密钥、明文输入值写 入日志或不安全的本地缓存。 

# 8. 最佳实践 

按需导入 API ,避免业务模块依赖整个键盘库的实现细节。 

敏感输入场景(密码、身份证、金额)建议启用 isEncrypt 和 isScreenShotEnable=false ,并设乱序 isRandom=true 。 

加密密钥仅在当前进程生命周期内有效,如需持久化输入值应重新加 密或妥善保管密钥。 

全局配置通过 YTKeyBoardManager 统一管理,避免在每个键盘实例 中重复设置相同参数。 

金额键盘使用时应根据业务需求合理设置 maxDecimal 和 maxLength ,避免输入异常。 

Web 场景使用完毕后及时调用 hidKeyBoard() 销毁弹窗,避免内存泄 漏。 

生产环境避免在日志中输出加密密钥、加密密文或明文输入值。 

自定义键盘头部时注意高度一致性(默认 44px ),避免不同页面键 盘高度不一致。 

9. 常见问题 

问题 

说明 

加密后的值为什么在进程重启后无法解密? 

加密密钥在 KBDataSourceEnCrypt 首次初始化时随机生成,仅当前 进程生命周期有效。进程重启后密钥会重新生成,之前加密的值将无 法解密。如需持久化存储,应在解密后使用业务自己的加密方案重新 加密。 

YTTextInput 和 YTWebInput 有什么区别? 

YTTextInput 用于原生页面中的安全输入键盘,绑定 YTKeTextInputSetting 管理状态。 YTWebInput 用于 Web 场景弹出 独立窗口的自定义键盘,由 YTWebKeyBoardManager 管理生命周期 和回调。 

# 如何实现键盘乱序排列? 

→ 设置 config.isRandom = true 即可。每次键盘类型切换(如数字 字 母)时,会使用 Fisher-Yates 算法重新洗牌按键顺序。 

# 防截屏在哪些场景生效? 

文本输入场景下,在输入框获得焦点时自动开启 window.setWindowPrivacyMode(true) ,失焦时关闭。 Web 场景下, 在创建弹窗时根据配置一次性设置。 

# 音效和振动需要申请额外权限吗? 

音效使用内置 rawfile 资源,无需录音权限。振动使用系统 haptic 能 

力,通常不需要额外运行时权限。如平台有特定要求,宿主应用按需 声明。 

全局配置和局部配置的优先级是什么? 

当 YTKeyBoardManager.getInstance().config.keyBoardName 非空且 具体键盘的 config.keyBoardName 为空时,全局配置覆盖局部配置。 否则局部配置优先。 

文档结束
