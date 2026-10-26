# 产品使用指南 

##### 概述 

一 、注册登录 

二、企业认证 

三、创建应用 

Android相关信息说明 

iOS相关信息说明 

HS相关信息说明 

Harmony相关信息说明 

四、 应用版本审核规则 

五、 获取 AppID/AppKey 

六、开始对接 

## 概述 

创蓝闪验控制台提供给开发者使用,用于配置应用、查看数据统计及计费的平台系统。 

## 一 、注册登录 

用户通过浏览器访问官网,点击“进入控制台”按钮。注册并登录控制台。 

1 

## 二、企业认证 

新用户登录后需在控制台首页中认证企业,只有认证完成的企业才能完整使用创蓝闪验SDK产品。具体 操作可以查看以下地址。 

https://www.chuanglan.com/document/6110e48109fd9600010209d3/632c630a272e290001af3e8 8 

## 三、创建应用 

1.企业用户在认证完成通过后,点击顶部“工作台”,选择创蓝闪验SDK,点击“使用”按钮,进入创蓝闪验 

管理界面。 

2 

- “ ” 

- 2.点击应用管理,点击 + 号,根据您的需要选择创建 Android/iOS/H5/Harmony闪验应用。 

3.按照要求填写相关平台应的信息,点击“确定”创建应用,等待审核通过即可对接调试。 

### Android相关信息说明 

- 包名:指 build 文件 applicationId 对应的名称,如下图: 

- 包签名:a. 您可以在 Android 手机上安装 签名获取工具 (点击下载),选择或填写您的 APP 包名 (该手机中必须已经安装了您的 APP),快速获取签名信息。b. Android studio 可以通过下面方法 获取:1 配置签名文件,可以参考 demo 示例这样配置: 

3 

2 配置签名文件后,按照下面 3 步获取: 

注意:配置签名文件后再获取,确保获取的是 release 签名。不配置签名文件,默认获取的是 

debug 签名,会导致后期打 release 包报错,需要重新创建应用、重新等待审核 

### iOS相关信息说明 

> ● Bundle ID: 开发者需创建自己的项目并获取 Bundle Identifier 

4 

### H5相关信息说明 

#### 合作方需报备集成取号能力的 `H5` 页面地址和域名,用于安全校验。必须按照规则填写,填写错误或将影 响功能使用。 

- 登录页地址(referer) 指集成了取号页面的完整页面地址和域名,用英文逗号隔开,若多个页面集 成,都需要填写并用英文逗号分隔, 不允许使用通配符 。 几种示例如下: 

   - 1 - 假如业务方集成取号的页面访问地址为:https://abc.com/a/mobile.html 

则填写:https://abc.com/a/mobile.html ,https://abc.com/ 

- 2 - 假如业务方集成取号的页面访问地址为:http://www.abc.com/a/mobile.html/#/abc 

则填写:http://www.abc.com/a/mobile.html/  ,http://www.abc.com/ 

- 3 - 假如业务方集成取号的页面访问地址为:http://www.abc.com/a/mobile.html/?abc 

则填写:http://www.abc.com/a/mobile.html/,http://www.abc.com/ 

- 4 - 假如业务方集成取号的页面访问地址为:https://abc.com/a/mobile.html和 https://123.com/a/mobile.html 

#### 则填写: 

https://abc.com/a/mobile.html,https://abc.com/,https://123.com/a/mobile.html,https://123.com/ 

- 登录页域名(origin) 指发起请求的业务来源,一般为 protocol+host,不包含路径等信息,若有多个需要用英文逗号隔 开, 注意末尾不要有 `"/"` 。 

几种示例如下: 

- 1 - 假如业务方集成取号的页面访问地址为:http://www.abc.com/a/mobile.html 则填写:http://www.abc.com 

- 2 - 假如业务方集成取号的页面访问地址为:https://www.abc.com/a/mobile.html 则填写:https://www.abc.com 

- 3 - 假如业务方集成取号的页面访问地址为:http://127.0.0.1:8080/a/mobile.html 

5 

则填写:http://127.0.0.1:8080 

- 4 - 假如业务方集成取号的页面访问地址为:https://127.0.0.1:8080/a/mobile.html 则填写:https://127.0.0.1:8080 

### Harmony相关信息说明 

- Harmony应用包名 

指鸿蒙应用的bundlename 

- Harmony应用签名 

鸿蒙提供的签名方式分别是 module在线签名和手动生成证书打包。 

module在线签名:通过 DevEco Studio 的 Project Structure 勾选 Automaticallygenerate signature 自动生成签名文件,自动生成的.p7b 文件通常默认在系统用户目录下。 如:C:/Users/zhangsan/.ohos/config/default MyDemo xxxx.p7b 

手动生成证书: 按照鸿蒙官方的如何使用手动生成证书打包文档操作,可获得一个 .p7b 文件。 

使用记事本打开 .p7b 文件,找到 development-certificate 字段(发布证书这个字段为distributioncertificate),将其后的内容复制到文本中之后,去掉其中的 \n 字符后将文本的后缀改为 cer,例如 test.cer。 

#### 注: 

1. 记事本打开可能出现乱码,-----BEGIN CERTIFICATE-----和-----END CERTIFICATE---- 

- 之间的不乱码即可。 

2. -----BEGIN CERTIFICATE-----和-----END CERTIFICATE-----分别位于首行和尾行,不 要与内容同行。如图: 

使用命令keytool -printcert -file test.cer 查询保存有.p7b文件证书信息的 test.cer 文件,fingerprint 为 SHA256 去掉冒号后的64个字符。 

- 1 - 查询工程所对应的 .p7b 文件 

- 2 - 获取 cer 证书 

- 3 - 查询证书 

6 

如"7265454aa66fb198041e78deed7e68d93ff73dc6c5fa11274612635e05caee85" 

- 应用唯一标识指鸿蒙应用的appIdentifier信息。该appIdentifier信息就是在华为AppGallery 

   - Connect上获取到的APPID值,保存后无法修改。 

## 四、 应用版本审核规则 

应用提交后即进入应用审核状态,应用审核约需 2 小时(工作日:9:00 ~ 18:00) 

应用信息将提交运营商进行审核,包名、包签名请务必正确填写,若无法获知可询问贵公司 Android 开发人员获得,避免审核重复。 

## 五、 获取 AppID/AppKey 

应用版本创建成功后,即可查看当前应用版本的 AppID 和 Appkey。 

一 AppID 为应用的唯 标识,Appkey 用于服务器端 API 调用时与 AppID 配合使用达到鉴权的目的,请保 管好 Appkey 防止外泄。 

## 六、开始对接 

完成以上操作后可以按照开发文档进行 SDK 集成。 

7
