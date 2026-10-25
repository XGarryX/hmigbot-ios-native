> 来源: ohpm 中央仓 README(T1 信源) | 包: `libhmprevent` | ohpm 最新版: 3.1.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 1. 简介与说明
鸿蒙NEXT通信协议保护软件SDK介绍
HarmonyOS NEXT应用面临的通信传输安全风险

随着HarmonyOS NEXT操作系统的发布,鸿蒙生态系统得到迅猛发展,以人工智能、大数据、云计算、区块链等为代表的新技术正不断在鸿蒙生态各个领域内得到应用,如何保护包括用户隐私数据、资金交易数据、身份认证数据等敏感信息在内的传输数据安全,是当前HarmonyOS NEXT应用开发者亟需解决的问题。

目前,HarmonyOS NEXT应用通信传输面临的安全挑战主要有三个方面:

首先,通信数据破解风险。攻击者可以通过数据抓包、中间人攻击等方式截获通信数据,并对数据进行破解、篡改等攻击。
其次,通信密钥泄露风险。攻击者可以通过对应用逆向、动态调试,分析并提取用于加解密通信数据的密钥,进而对加密数据进行解密、窃取等攻击。
最后,通信接口滥用风险。攻击者可以轻易提取出应用内进行通信传输的接口,并进行非法批量盗用,严重影响企业基于移动应用运营活动的正常秩序。
同时,随着国家数据安全法、用户隐私保护法、密码法的发布,在涉及重要数据、敏感数据以及密码密钥的安全保障上,针对移动应用通信传输安全的监管、检测、合规要求也在不断强化,需要开发者具备可靠的通信协议安全保护能力。

# 2. 安装命令 
>ohpm i libhmprevent

# 3. 集成方式
 1. 在 module 中新建 libs目录,将libHmPrevent-signed.har拷贝到该目录
 2.  编辑该 module 的 oh-package.json5 文件 新增
 ```
   "dependencies": {
   "@ohos/libraryHmPrevent": "file:../libHmPrevent-signed.har"
  }
 ```

# 4. 使用方式
1. 加密
 ```
hmEncryptMessage(this.testStr)
              .then((encryptedMessage) => {
                log.debug(0x0001,"Encrypted message",encryptedMessage)
                this.ens = encryptedMessage;
              })
              .catch((error: BusinessError) => {
                log.error(0x0001,"Encrypted message",error.message)
                this.tipsMessage = error.message
                if (this.dialogController != null) {
                  this.dialogController.open()
                }
              });

 ```
2. 解密
 ```
hmDecryptMessage(this.ens)
              .then((decryptedMessage) => {
                log.debug(0x0001,"Decrypted message:",decryptedMessage)
                this.des = decryptedMessage;
              })
              .catch((error: BusinessError) => {
                log.error(0x0001,"Decrypted message:",error.message)
                this.tipsMessage = error.message
                if (this.dialogController != null) {
                  this.dialogController.open()
                }
              });
 ```
 # 5. 说明

 需要梆梆提供授权文件放在工程的resources/rawfile目录下,没有授权文件或授权文件无效时,加解密不能正常使用
