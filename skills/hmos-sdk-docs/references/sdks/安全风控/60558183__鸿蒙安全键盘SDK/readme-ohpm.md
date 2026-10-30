> 来源: ohpm 中央仓 README(T1 信源) | 包: `safekeyboard`(市场登记名 `@tianyu/safe_keyboard`) | ohpm 最新版: 1.3.2 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 1. 简介与说明
鸿蒙NEXT安全键盘软件SDK介绍
随着HarmonyOS NEXT操作系统的发布,鸿蒙生态系统得到迅猛发展,大量基于鸿蒙系统的智能应用发布、上架,以人工智能、大数据、云计算、区块链等为代表的新技术正不断在鸿蒙生态内应用于社会生活各领域,用户通过鸿蒙手机录入各类敏感的隐私数据,例如姓名、手机号、住址、邮箱、银行卡号、网络账号、各类密码、交易数据等,极易受到不法攻击者的监听、拦截、窃取,造成用户隐私数据泄露,危害个人信息、资金等方面安全。
目前,HarmonyOS NEXT操作系统用户输入数据的安全挑战主要有三个方面:

首先,用户信息数据在输入过程中面临被非法监听、窃取的风险。攻击者可以通过篡改程序、植入恶意代码或者截屏、录屏等方式监听、窃取用户键盘输入数据、操作轨迹。
其次,在应用的运行过程中,应用程序的各项操作数据是暴露在内存当中的,用户输入数据面临被从内存中提取、破解、篡改的风险。
最后,在应用客户端向服务端传输用户输入数据的过程中,相关数据面临被非法抓包分析、破解、泄露的风险。
同时,随着国家对用户隐私数据保护的强化,针对应用开发者的键盘输入数据安全的监管、检测、合规要求也在不断强化,需要开发者从根本上为提供用户输入数据安全保护能力。
梆梆安全介绍
北京梆梆安全科技有限公司(以下简称"梆梆安全"),基于多年自主研发的移动安全技术,建立了全面的鸿蒙生态安全防护体系,通过专业的安全产品和服务为鸿蒙应用开发者和消费者打造安全稳固可信的鸿蒙生态环境。
梆梆安全始终坚持以客户为中心,全力服务于金融、互联网、物联网、政府、运营商、企业、医疗、能源、教育等各大行业的应用开发者,不断为客户建立“稳如泰山,值得托付”的安全服务体验。

# 2. 安装命令 
>ohpm i safekeyboard

# 3. 集成方式
1. 在 module 中新建 libs目录,将SafeKeyboard-signed.har拷贝到该目录 

2. 编辑该 module 的 oh-package.json5 文件 新增
 ```
   "dependencies": {
   "@ohos/libraryHmPrevent": "file:../SafeKeyboard-signed.har"
  }
 ```
3. 在需要使用的view中新增
 ```
import { BangcleTextInput,BangcleUtils } from 'safekeyboard';

export enum EKeyboardType {
  NUMERIC, //数字键盘
  PAPERS,
  PASSWORD,
  UPPERCASE, // 大写字母键盘
  LOWERCASE, // 小写字母键盘
  SPECIAL, // 特殊字符键盘
  FULL_UPPERCASE_LOGIN,// 大写登录键盘
  FULL_LOWERCASE_LOGIN,// 小写登录键盘
  FULL_SPECIALOne,//xx定制
  FULL_SPECIALTwo,//xx定制
}
 ```
4.  初始化
 ```
  async aboutToAppear(){
    let sm2key = "04F93B986D1E826B1B2A4407A666C0AD583F0E9BE901D49B9FC39619B307411BF15DFCB2C9E8458180F026414CA46FFA743E6FC5441A5017745B0528A95CC663B3";
    await BangcleUtils.initWithSetPubKey(0,2,sm2key);
  }
  
   @State encValue: string = '';
  	  @State placeholder: string = "输入密码";
  	  curKeyboardType: EKeyboardType = EKeyboardType.PASSWORD;
	  controller: TextInputController = new TextInputController();
	  
   @Builder
  customBangcleKeyboardBuilder() {
    BangcleTextInput({
      encValue: this.encValue,            // 加密后字符串
      curKeyboardType: this.curKeyboardType,   // 加盘类型 需传入 EKeyboardType.NUMERIC 等
      placeholder: this.placeholder,     // 编辑框 预显示内容
      controller: this.controller       //textInputcontroller
    })
  }
 ```
5. 调用
   this.customBangcleKeyboardBuilder();

6. 获取加密内容
   this.encValue 中实时保存加密后的字符串

# 4.说明

需要梆梆提供授权文件放在工程的resources/rawfile目录下,没有授权文件或授权文件无效时,键盘标题会提示“未授权”字样

详细的集成细节,参考提供的集成文档和Demo
