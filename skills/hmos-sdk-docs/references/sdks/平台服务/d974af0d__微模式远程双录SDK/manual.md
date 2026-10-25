# SDK 接入使用说明 

SDK 包名: remotedoublerecord 

# 1.SDK 集成使用方式 

以新建的一个 entry 模块集成本公司 SDK 为例,来说明 SDK 的集成方式 和使用方法。 

第一步,在新建的项目的根目录下,新建 libs 文件夹,将本公司的 SDK ,即 RemoteDoubleRecord.har 和 zegoliveroom.har 文件拷贝到 libs 目录下。 

第二步,在项目的根目录下的 oh-package.json5 文件中添加如下红色 框内的配置,并点击右上角的 Sync Now 。 

第三步,在要引入本公司的 SDK 的模块,这里是 entry 模块,即该模块 的模块级的 oh-package.json5 文件中添加如下红色框内的配置,并点 击右上角的 Sync Now. 

第四步,在要跳转 SDK 的页面文件中使用 import 语句导入 SDK 首页文 件,并使用 router.pushNameRoute() 方法携带约定好的参数,即可跳 转到 SDK 的首页,即环境检测界面。如下图: 

环境检测界面如下图: 

第五步,双录结束对接。 

双录结束后,通过接口方法通知手机银行双录结束,手机银行实现该 接口,并在该接口实现逻辑中进行相关处理,在第四步调用 SDK 的时 候把这个接口的实现类传递给 SDK 。如下图: 

# 附: SDK 不涉及接口调用
