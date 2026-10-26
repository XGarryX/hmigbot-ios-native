# 申朴 Harmony 开发者 SDK 使用指南 

# 1. 注册及安装 

`1>.` 注册 **`APP`** 开发人员登录私有化部署的申朴信息全链路可观测平台,注册 **`APP`** 信息,拿到允许 **`APP`** 接入的授权信息。 

`2>.` 集成 `APM SDK` 两种集成方式 `:` 方式一: **`APP`** 开发人员向申朴信息申请 `APM SDK` ,通过本地文件的方式集成 `har` 文件。 方式二:通过 `ohpm install @cisetech/apm` 集成 `APM SDK` 。 

# 2. 初始化 

`afterAgreePrivacy(): void { CiseTech.init(this.context)` _`//AbilityStage`_ 子类中 `CiseTech.setCrashUploadUrl(urlCrashAdd);` _`//`_ 上传 _`Crash`_ 地址 _`urlCrashAdd`_ `CiseTech.setLogUrl(urlLogAdd);` _`//`_ 请求日志上传地址 _`urlLogAdd`_ `}` 

# 3. 上传接口 

首页 `EntryAbility` 的 `onCreate` 方法中调用 `UploadFile(this.context,launchParam,urlOauth);` _`//launchParam`_ 是 _`onCreate`_ 方法中的参 

# 5. 测试产生崩溃 

**`cppTestNapi`** `.add(2, 3)` _`//`_ 制造 _`1`_ 个 _`cpp`_ 漰溃 **`JSON`** `.parse("");` _`//`_ 制造 _`1`_ 个 _`js(`_ 即 _`ts,arkts)`_ 漰溃 

# 6. 分析崩溃 

登录智能可观测平台,查看崩溃信息。 

# 7.DEMO 地址 

```
https://gitee.com/wujunfeng001/integrationcisetech_apm_demo.git
```
