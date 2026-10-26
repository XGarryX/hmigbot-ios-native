sdk 使用指南 

典型应用场景 

加密用户个人数据 

应用需要对用户的个人数据进行加密存储或者传输时,可使用 Aegis 安全编码 SDK 对数据进行对称加密或者非对称加密,保障用户个人数 据的机密性。 

验证数字签名 

应用需要对服务端返回的信息或者其他应用传入的信息进行数字签名 验证,调用 Aegis 安全编码 SDK 验签接口,确保信息的完整性和不可抵 赖性。 

保障敏感信息安全 

为保障敏感信息传输过程中的完整性、不可抵赖性和机密性,可以调 用 Aegis 安全编码 SDK 签名和加密接口,将敏感信息先签名后加密。 

集成 SDK 

配置 SDK 依赖 

您需要在 DevEco Studio 项目中配置 SDK 依赖。 

Aegis 的 OpenHarmony 三方库中心仓地址为 @hw-agconnect/petalaegis ,您可以通过以下任意一种方式配置 SDK 依赖。 

方式一 

打开 DevEco Studio 应用级(一般为 entry )下的 “oh-package.json5” 文 件。 

在 “oh-package.json5” 文件的 “dependencies” 中添加 Aegis 的 SDK 依 赖。 

"dependencies": { 

"@hw-agconnect/petal-aegis": "1.4.9-300" 

} 

打开修改完的 “oh-package.json5” 文件,右上方出现 “Sync Now” 链 接,点击 “Sync Now” 等待同步完成。 

方式二 

打开您的工程,在命令行窗口执行 cd entry 命令,切换到工程 的 “entry” 目录。 

安装 SDK 到您的项目中。 

ohpm install @hw-agconnect/petal-aegis 

# 说明 

工程的应用框架必须为 Stage 模型,即 “apiType” 配置 为 “stageMode” 。 

Stage 模型仅 Compile API 版本为 12 及以上支持,请确保 SDK 的 Compile API 版本不低于 12 。 

请确保采用 ohpm 方式编译。 

SDK 也支持开发 OpenHarmony 应用( API 12 及以上版本)。
