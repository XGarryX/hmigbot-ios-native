## 科蓝鸿蒙 TEE 金融键盘组件(MTK)V1.0.0 使用指南 

## 一、集成方式 

### 1.1 工程中引入组件har 包 

步骤1: 将har 包放入entry 目录下的libs 目录中(没有则新建目录) 

步骤2: 修改引用har 包的工程中的oh-package.json5 文件,在 dependencies 节点下增加"@csii_mtk": "file:./libs/csii_mtk_1.0.0.har"(@csii_mtk 名称可自定义) oh-package.json5 文件案例: 

{ "name": "entry", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "@csii_mtk": "file:./libs/csii_mtk_1.0.0.har", } } 

步骤3:根据IDE Dev studio 提示进行同步,点击“sync now”执行同步 

1 

# 二、使用说明 

### 2.1 添加权限 

在entry 目录下的module.json5 文件中添加requestPermissions 权限 

{ 

//振动权限 

"name": "ohos.permission.VIBRATE" 

}, 

{ 

//关键资产存储 

"name": "ohos.permission.STORE_PERSISTENT_DATA" 

} 

### 2.2 初始化键盘 

通过发送接口获取 agreePubkey,maskcodes,rsapubkey,sm2pubkey,smfaKey 

然后发送 KeyboardNapi.importServerKeyboardKey_zs(serverEccPub, smfaKey, sm2Pubkey, rsaPubkey)来进行初始化 

通过 KeyboardNapi.initNativeMaskCodes(maskCodes)设置掩码数据 

### 2.3 数字+字母+符号键盘 

- **说明:** 

数字+字母+符号键盘 --CSIIPwdInput() 

- **参数:** 

placeholderText:描述信息 pwdHeight:键盘高度 

name: 键盘名称(若同个界面多个键盘组件,保证 name 和键盘一一对应) 

regular: 正则表达式 

maxLength:键盘最大输入长度 

minLength:键盘最小输入长度 

isRandom:是否随机 

2 

isRandomType: 随机类型 0:全部乱序或不乱序 1:数字乱序其他不乱序 2: 字母乱序其他不乱序 3:数字和字母乱序其他不乱序 

CSIIPwdInput({ 

placeholderText: "请输入密码", pwdHeight: "40vp", name: "csii_pwd, regular: "[:print:]+", maxLength: 15, minLength: 6, isRandom: true, isRandomType : 0 }) .width("300") .margin({ top: 30 }) 

### 2. 纯数字键盘 

- **说明:** 

纯数字键盘--CSIINumberInput() 

- **参数:** 

placeholderText:描述信息 pwdHeight:键盘高度 

name: 键盘名称(若同个界面多个键盘组件,保证 name 和键盘一一对应) 

regular: 正则表达式 

maxLength:键盘最大输入长度 

minLength:键盘最小输入长度 

isRandom:是否随机 

isRandomType: 随机类型 0:全部乱序或不乱序 1:数字乱序其他不乱序 2:字母乱序其 他不乱序 3:数字和字母乱序其他不乱序 

- **示例:** CSIINumberInput({ placeholderText: "请输入密码", 

3 

pwdHeight: "40vp", name: "csii_pwd, regular: "[:print:]+", maxLength: 15, minLength: 6, isRandom: true, isRandomType : 0 }) .width("300") .margin({ top: 30 }) 

# 三、接口说明 

统一使用 CSIIKeyBoardUtil.getInstance()来进行获取对象 

|接口|名称|输入|输出|
|---|---|---|---|
|getCipherValidityVe rify|密文合法性校验|name:键盘名称|0="成功" -1="密码为空" -2="密码小于最小长度" -3="密码内容不合法"|
|getInputEncy|获取密文|name:键盘名称 time: 当前时间戳|encyResult:密文|
|setRandomCode|设置随机数|name:键盘名称 isRandom: 是否随机 isRandomType: 随机类型0: 全部乱序或不乱序1:数字 乱序其他不乱序2:字母乱 序其他不乱序3:数字和字 母乱序其他不乱序|无|
|getNativeCipherLeng th|获取密文长度|name:键盘名称|Length:密文长度|
|setMaxLength|设置最大输入长度|name:键盘名称 Length: 最大输入长度|无|
|setVibrator|设置键盘振动|name:键盘名称 isVibrator: 是否振动|无|
|clearKeyboard|密码清空|name:键盘名称|无|
|setParameter|配置参数|uuid: string, //设备唯 一标识 maskCode: string//随机 数|空|

4 

5
