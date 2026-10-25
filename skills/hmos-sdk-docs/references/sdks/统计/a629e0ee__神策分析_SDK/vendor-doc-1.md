> 来源: 厂商官方文档页(T2 信源) | https://gitee.com/openharmony-tpc/docs/blob/master/OpenHarmony_har_usage.md | 抓取: 2026-07-17
> 注意: 单页快照,站内其余页面见来源链接

__代码拉取完成,页面将自动刷新

__

[仓库状态说明](https://help.gitee.com/repository/settings/status#%E6%9A%82%E5%81%9C%E5%92%8C%E5%85%B3%E9%97%AD%E4%BB%93%E5%BA%93)

[ ](https://chat.gitee.com?repo_owner=openharmony-tpc&repo_path=docs)

__

Watch 

__

[__不关注](/openharmony-tpc/docs/unwatch)[ __关注所有动态](/openharmony-tpc/docs/watch)[ __仅关注版本发行动态](/openharmony-tpc/docs/release_only_watch)[ __关注但不提醒动态](/openharmony-tpc/docs/ignoring_watch)

[4 ](/openharmony-tpc/docs/watchers "4") [__Star](/login)[30 ](/openharmony-tpc/docs/stargazers "30") [__Fork](/login "你必须登录后才可以fork一个仓库")[18 ](/openharmony-tpc/docs/members "18")

##  [__](/open_harmony)__[OpenHarmony-TPC](/openharmony-tpc "OpenHarmony-TPC")/[docs](/openharmony-tpc/docs "docs")

关闭

[__代码](/openharmony-tpc/docs)[ __Issues 193  ](/openharmony-tpc/docs/issues)[__Pull Requests 2  ](/openharmony-tpc/docs/pulls)[__Wiki](/openharmony-tpc/docs/wikis)[ __统计](/openharmony-tpc/docs/graph/master)[ __流水线](/openharmony-tpc/docs/gitee_go)

__服务 __

[ JavaDoc  ](/openharmony-tpc/docs/javadoc)[ PHPDoc  ](/openharmony-tpc/docs/phpdoc)[ 质量分析  ](/openharmony-tpc/docs/quality_analyses?platform=sonar_qube)[ Jenkins for Gitee  ](https://gitee.com/help/articles/4193)[ 腾讯云托管  ](https://gitee.com/help/articles/4318)[ 腾讯云 Serverless  ](https://gitee.com/help/articles/4330)[ 悬镜安全  ](/openharmony-tpc/docs/open_sca)[ 阿里云 SAE  ](https://help.gitee.com/devops/connect/Aliyun-SAE)[ Codeblitz  ](https://gitee.com/link?target=https%3A%2F%2Fcodeblitz.cloud.alipay.com%2Fgitee%2Fopenharmony-tpc%2Fdocs%2Ftree%2Fmaster%2FOpenHarmony_har_usage.md)[ SBOM  ](/openharmony-tpc/docs/sbom)[ 开发画像分析  ](/openharmony-tpc/docs/qilin_profile) 我知道了,不再自动展开 

加入 Gitee 

与超过 1400万 开发者一起发现、参与优秀开源项目,私有仓库也完全免费 :) 

[免费加入](/signup?from=project-guide)

已有帐号? [立即登录](/login?from=project-guide)

文件

[ ](/openharmony-tpc/docs/compare/master...master)

master 

__

分支 (2) 

[管理](/openharmony-tpc/docs/branches)

[管理](/openharmony-tpc/docs/tags)

master

revert-merge-18-master

master 

__

分支 (2) 

[管理](/openharmony-tpc/docs/branches)

[管理](/openharmony-tpc/docs/tags)

master

revert-merge-18-master

克隆/下载 __

__

克隆/下载 

HTTPS SSH SVN SVN+SSH [__下载ZIP](/openharmony-tpc/docs/repository/archive/master.zip)

__

提示 

下载代码请复制以下命令到终端执行 

__

为确保你提交的代码身份被 Gitee 正确识别,请执行以下命令完成配置 

git config --global user.name userName  git config --global user.email userEmail __

初次使用 SSH 协议进行代码克隆、推送等操作时,需按下述提示完成 SSH 配置 

1 生成 RSA 密钥 

__

2 获取 RSA 公钥内容,并配置到[ SSH公钥 ](/profile/sshkeys) 中 

__

在 Gitee 上使用 SVN,请访问[ 使用指南 ](https://help.gitee.com/enterprise/code-manage/%E4%BB%A3%E7%A0%81%E6%89%98%E7%AE%A1/%E4%BB%A3%E7%A0%81%E4%BB%93%E5%BA%93/Gitee%20SVN%E6%94%AF%E6%8C%81)

使用 HTTPS 协议时,命令行会出现如下账号密码验证步骤。基于安全考虑,Gitee 建议[ 配置并使用私人令牌 ](/profile/personal_access_tokens)替代登录密码进行克隆、推送等操作 

Username for 'https://gitee.com': userName

Password for 'https://userName@gitee.com': # 私人令牌 

[ ](/openharmony-tpc/docs/compare/master...master)

master 

__

分支 (2) 

[管理](/openharmony-tpc/docs/branches)

[管理](/openharmony-tpc/docs/tags)

master

revert-merge-18-master

[docs ](/openharmony-tpc/docs/tree/master)

/ 

**OpenHarmony_har_usage.md** __

[__分支 2](/openharmony-tpc/docs/branches)

[__标签 0](/openharmony-tpc/docs/tags)

[docs ](/openharmony-tpc/docs/tree/master)

/ 

**OpenHarmony_har_usage.md**

__ OpenHarmony_har_usage.md  6.10 KB

# OpenHarmony HAR OpenHarmony js/ts三方库使用的是OpenHarmony静态共享包,即HAR(Harmony Archive),可以包含js/ts代码、c++库、资源和配置文件。通过HAR,可以实现多个模块或者多个工程共享ArkUI组件、资源等相关代码。HAR不同于HAP,不能独立安装运行在设备上,只能作为应用模块的依赖项被引用。 # 如何安装OpenHarmony HAR 引用三方HAR,包括从仓库进行安装和从本地库模块中进行安装两种方式。  ## 引用仓库安装的HAR:  引用ohpm仓中的HAR,首先需要设置三方HAR的仓库信息,DevEco Studio默认仓库地址是[ohpm](https://repo.harmonyos.com/ohpm/),如果您想设置自定义仓库,请在DevEco Studio的Terminal窗口执行如下命令进行设置(执行命令前,请确保将DevEco Studio中ohpm安装地址配置在“环境变量-系统变量-PATH”中): ``` ohpm config set registry=your_registry1,your_registry2 ``` 说明:ohpm支持多个仓库地址,采用英文逗号分隔。 然后通过如下两种方式设置三方包依赖信息: \- 方式一:在Terminal窗口中,执行如下命令安装三方包,DevEco Studio会自动在工程的oh-package.json5中自动添加三方包依赖。 ``` ohpm install @ohos/lottie ``` \- 方式二:在工程的oh-package.json5中设置三方包依赖,配置示例如下: ``` "dependencies": { "@ohos/lottie": "^2.0.0"} ``` 依赖设置完成后,需要执行ohpm install命令安装依赖包,依赖包会存储在工程的oh_modules目录下。 ``` ohpm install ``` ## 引用本地库模块的文件和资源: \- 方式一:在Terminal窗口中,执行如下命令进行安装,并会在oh-package5.json中自动添加依赖。 ``` ohpm install ../library ``` \- 方式二:在工程的oh-package.json5中设置三方包依赖,配置示例如下: ``` "dependencies": { "@ohos/library": "file:../library" } ``` 依赖设置完成后,需要执行ohpm install命令安装依赖包,依赖包会存储在工程的oh_modules目录下。 ``` ohpm install ``` ## 在引用OpenHarmony HAR时,请注意以下事项:  \- 当前只支持在模块和工程下的oh-package.json5文件中声明dependencies依赖,才会被当做OpenHarmony依赖使用,并在编译构建过程中进行相应的处理。 \- 引用的模块的compileSdkVersion不能低于其依赖的OpenHarmony ohpm三方包(可在oh_modules目录下,找到引用的ohpm包的src > main > module.json5 中查看)。 ## 引用OpenHarmony HAR hml页面  在JS工程范式中,组件功能由hml承载,开发者可以在JS工程的hml页面通过<element>标签来引入OpenHarmony HAR中的共享hml页面,示例如下: ``` <element name="comp" src="@ohos/library/src/main/js/components/index/index.hml"></element> ``` 其中,@ohos/library为OpenHarmony HAR的包名,hml页面的路径为OpenHarmony HAR中的相对路径。  随后便可以通过设置的name来使用该element元素,以引用OpenHarmony HAR中的hml页面,示例如下: ```typescript <element name="comp" src="@ohos/library/src/main/js/components/index/index.hml"></element>  <comp></comp> <text class="title"> {{ $t('strings.hello') }} {{ title }} </text>  ``` ## 引用OpenHarmony HAR ArkTS页面  ArkTS是TypeScript的扩展,因此导出和引入的语法与TypeScript一致。在OpenHarmony ohpm模块中,可以通过export导出ArkTS页面,示例如下: ```typescript // library/src/main/ets/components/MainPage/MainPage.ets @Entry @Component export struct MainPage { @State message: string = 'Hello World' build() {  Row() {  Column() {  Text(this.message) .fontSize(50) .fontWeight(FontWeight.Bold) }  .width('100%')  } .height('100%')  } } ``` 然后在其它模块中通过import引入导出的ArkTS页面,示例如下所示: ```typescript // entry/MainAbility/pages/index.ets import { MainPage } from "@ohos/library" @Entry @Component struct Index { @State message: string = 'Hello World' build() {  Column() {  MainPage()  Row() {  Text(this.message) .fontSize(50) .fontWeight(FontWeight.Bold) } .width('100%') }  .height('10%')  } } ``` 引用OpenHarmony HAR内ts/js方法ts/js方法的导出和引用,与ArkTS页面的引用相同,即在OpenHarmony ohpm模块中,可以通过export导出ts/js方法,示例如下所示: ```typescript // library/index.js export function func() { return "[ohpm] func1"; } ``` 然后在其它的ts/js页面中,通过import引入导出的ts/js方法,示例如下所示: ```typescript // entry/src/main/js/MainAbility/pages/index/index.js import {func} from "@ohos/library" export default { data: { title: "" }, onInit() { this.title = func(); } } ``` 引用OpenHarmony HAR内资源支持在OpenHarmony ohpm模块和依赖OpenHarmony ohpm的模块中引用OpenHarmony ohpm模块内的资源。例如在OpenHarmony ohpm模块的scr/main/resources里添加字符串资源(在string.json中定义,name:hello_ohpm)和图片资源(icon_ohpm.png)。然后在Entry模块中引用该字符串资源和图片资源的示例如下: 当前暂不支持类Web范式引用i18n文件中的国际化资源。 ```typescript // entry/src/main/ets/MainAbility/pages/index.ets @Entry @Component struct Index { @State message: string = 'Hello World' build() { Column() { Row() { Text($r("app.string.hello_ohpm")) // 字符串资源 .fontSize(40) .fontWeight(FontWeight.Bold) } .width('50%') Image($r("app.media.icon_ohpm")) // 图片资源 } .height('100%') } } ``` 在编译构建HAP中,DevEco Studio会从HAP模块及依赖的模块中收集资源文件,如果不同模块的相同限定词目录下的资源文件出现重名冲突时,DevEco Studio会按照以下优先级进行覆盖(优先级由高到低): \- AppScope(仅API 9的Stage模型支持) \- HAP包自身模块 \- 依赖的OpenHarmonyHarmony ohpm模块 一键复制 [编辑](/openharmony-tpc/docs/edit/master/OpenHarmony_har_usage.md "暂停/关闭状态下的仓库无法执行该操作") [原始数据](https://gitee.com/openharmony-tpc/docs/raw/master/OpenHarmony_har_usage.md) [按行查看](/openharmony-tpc/docs/blame/master/OpenHarmony_har_usage.md) [历史](/openharmony-tpc/docs/commits/master/OpenHarmony_har_usage.md)

[zhongluping](/zhong-luping) 提交于 2023-11-24 14:55 +08:00  . [添加tpc贡献指导文档&调整docs目录](/openharmony-tpc/docs/commit/fb573a7de1c6e8419caa7bc9a74dd1ba382a1a47)

__

# OpenHarmony HAR OpenHarmony js/ts三方库使用的是OpenHarmony静态共享包,即HAR(Harmony Archive),可以包含js/ts代码、c++库、资源和配置文件。通过HAR,可以实现多个模块或者多个工程共享ArkUI组件、资源等相关代码。HAR不同于HAP,不能独立安装运行在设备上,只能作为应用模块的依赖项被引用。 # 如何安装OpenHarmony HAR 引用三方HAR,包括从仓库进行安装和从本地库模块中进行安装两种方式。  ## 引用仓库安装的HAR:  引用ohpm仓中的HAR,首先需要设置三方HAR的仓库信息,DevEco Studio默认仓库地址是[ohpm](https://repo.harmonyos.com/ohpm/),如果您想设置自定义仓库,请在DevEco Studio的Terminal窗口执行如下命令进行设置(执行命令前,请确保将DevEco Studio中ohpm安装地址配置在“环境变量-系统变量-PATH”中): ``` ohpm config set registry=your_registry1,your_registry2 ``` 说明:ohpm支持多个仓库地址,采用英文逗号分隔。 然后通过如下两种方式设置三方包依赖信息: \- 方式一:在Terminal窗口中,执行如下命令安装三方包,DevEco Studio会自动在工程的oh-package.json5中自动添加三方包依赖。 ``` ohpm install @ohos/lottie ``` \- 方式二:在工程的oh-package.json5中设置三方包依赖,配置示例如下: ``` "dependencies": { "@ohos/lottie": "^2.0.0"} ``` 依赖设置完成后,需要执行ohpm install命令安装依赖包,依赖包会存储在工程的oh_modules目录下。 ``` ohpm install ``` ## 引用本地库模块的文件和资源: \- 方式一:在Terminal窗口中,执行如下命令进行安装,并会在oh-package5.json中自动添加依赖。 ``` ohpm install ../library ``` \- 方式二:在工程的oh-package.json5中设置三方包依赖,配置示例如下: ``` "dependencies": { "@ohos/library": "file:../library" } ``` 依赖设置完成后,需要执行ohpm install命令安装依赖包,依赖包会存储在工程的oh_modules目录下。 ``` ohpm install ``` ## 在引用OpenHarmony HAR时,请注意以下事项:  \- 当前只支持在模块和工程下的oh-package.json5文件中声明dependencies依赖,才会被当做OpenHarmony依赖使用,并在编译构建过程中进行相应的处理。 \- 引用的模块的compileSdkVersion不能低于其依赖的OpenHarmony ohpm三方包(可在oh_modules目录下,找到引用的ohpm包的src > main > module.json5 中查看)。 ## 引用OpenHarmony HAR hml页面  在JS工程范式中,组件功能由hml承载,开发者可以在JS工程的hml页面通过<element>标签来引入OpenHarmony HAR中的共享hml页面,示例如下: ``` <element name="comp" src="@ohos/library/src/main/js/components/index/index.hml"></element> ``` 其中,@ohos/library为OpenHarmony HAR的包名,hml页面的路径为OpenHarmony HAR中的相对路径。  随后便可以通过设置的name来使用该element元素,以引用OpenHarmony HAR中的hml页面,示例如下: ```typescript <element name="comp" src="@ohos/library/src/main/js/components/index/index.hml"></element>  <comp></comp> <text class="title"> {{ $t('strings.hello') }} {{ title }} </text>  ``` ## 引用OpenHarmony HAR ArkTS页面  ArkTS是TypeScript的扩展,因此导出和引入的语法与TypeScript一致。在OpenHarmony ohpm模块中,可以通过export导出ArkTS页面,示例如下: ```typescript // library/src/main/ets/components/MainPage/MainPage.ets @Entry @Component export struct MainPage { @State message: string = 'Hello World' build() {  Row() {  Column() {  Text(this.message) .fontSize(50) .fontWeight(FontWeight.Bold) }  .width('100%')  } .height('100%')  } } ``` 然后在其它模块中通过import引入导出的ArkTS页面,示例如下所示: ```typescript // entry/MainAbility/pages/index.ets import { MainPage } from "@ohos/library" @Entry @Component struct Index { @State message: string = 'Hello World'  build() {  Column() {  MainPage()  Row() {  Text(this.message) .fontSize(50) .fontWeight(FontWeight.Bold) } .width('100%') }  .height('10%')  } } ``` 引用OpenHarmony HAR内ts/js方法ts/js方法的导出和引用,与ArkTS页面的引用相同,即在OpenHarmony ohpm模块中,可以通过export导出ts/js方法,示例如下所示: ```typescript // library/index.js export function func() { return "[ohpm] func1"; } ``` 然后在其它的ts/js页面中,通过import引入导出的ts/js方法,示例如下所示: ```typescript // entry/src/main/js/MainAbility/pages/index/index.js import {func} from "@ohos/library" export default { data: { title: "" }, onInit() { this.title = func(); } } ``` 引用OpenHarmony HAR内资源支持在OpenHarmony ohpm模块和依赖OpenHarmony ohpm的模块中引用OpenHarmony ohpm模块内的资源。例如在OpenHarmony ohpm模块的scr/main/resources里添加字符串资源(在string.json中定义,name:hello_ohpm)和图片资源(icon_ohpm.png)。然后在Entry模块中引用该字符串资源和图片资源的示例如下: 当前暂不支持类Web范式引用i18n文件中的国际化资源。 ```typescript // entry/src/main/ets/MainAbility/pages/index.ets @Entry @Component struct Index { @State message: string = 'Hello World' build() { Column() { Row() { Text($r("app.string.hello_ohpm")) // 字符串资源 .fontSize(40) .fontWeight(FontWeight.Bold) } .width('50%') Image($r("app.media.icon_ohpm")) // 图片资源 } .height('100%') } } ``` 在编译构建HAP中,DevEco Studio会从HAP模块及依赖的模块中收集资源文件,如果不同模块的相同限定词目录下的资源文件出现重名冲突时,DevEco Studio会按照以下优先级进行覆盖(优先级由高到低): \- AppScope(仅API 9的Stage模型支持) \- HAP包自身模块 \- 依赖的OpenHarmonyHarmony ohpm模块

Loading...

跳转 

__

举报 

__

举报成功 

我们将于2个工作日内通过站内信反馈结果给你! 

请认真填写举报原因,尽可能描述详细。 

举报类型 

请选择举报类型 

__

举报原因 

取消 

发送 

__

误判申诉 

此处可能存在不合适展示的内容,页面不予展示。您可通过相关编辑功能自查并修改。

如您确认内容无涉及 不当用语 / 纯广告导流 / 暴力 / 低俗色情 / 侵权 / 盗版 / 虚假 / 无价值内容或违法国家有关法律法规的内容,可点击提交进行申诉,我们将尽快为您处理。

取消

提交

#### 简介

暂无描述 [ 展开 __](javascript:void\(0\);) [ 收起 __](javascript:void\(0\);)

暂无标签

__ []()

__ Apache-2.0 

使用 Apache-2.0 开源许可协议

__[ 30  Stars ](/openharmony-tpc/docs/stargazers "30")

__[ 4  Watching ](/openharmony-tpc/docs/watchers "4")

__[ 18  Forks ](/openharmony-tpc/docs/members "18")

保存更改 

取消 

#### 发行版

暂无发行版 

####  贡献者 

[全部](/openharmony-tpc/docs/contributors?ref=master)

#### 近期动态

[加载更多 __](javascript:void\(0\);)

不能加载更多了

__

编辑仓库简介

简介内容

主页

取消 保存更改

马建仓 AI 助手

__

尝试更多

代码解读

代码找茬

代码优化

1

https://gitee.com/openharmony-tpc/docs.git

git@gitee.com:openharmony-tpc/docs.git

openharmony-tpc

docs

docs

master

__

点此查找更多帮助

### 搜索帮助

__

__

[__ Git 命令在线学习 ](https://help.gitee.com/learn-git-branching/?utm_source==gitee-help-widget "Git 命令在线学习")[__ 如何在 Gitee 导入 GitHub 仓库 ](https://gitee.com/help/articles/4261?utm_source==gitee-help-widget "如何在 Gitee 导入 GitHub 仓库")

[Git 仓库基础操作](/help/articles/4114)

[企业版和社区版功能对比](/help/articles/4166)

[SSH 公钥设置](/help/articles/4191)

[如何处理代码冲突](/help/articles/4194)

[仓库体积过大,如何减小?](/help/articles/4232)

[如何找回被删除的仓库数据](/help/articles/4279)

[Gitee 产品配额说明](/help/articles/4283)

[GitHub仓库快速导入Gitee及同步更新](/help/articles/4284)

[什么是 Release(发行版)](/help/articles/4328)

[将 PHP 项目自动发布到 packagist.org](/help/articles/4354)

__

评论

__

仓库举报 

__

回到顶部

__

登录提示 

该操作需登录 Gitee 帐号,请先登录后再操作。 

立即登录 

没有帐号,去注册
