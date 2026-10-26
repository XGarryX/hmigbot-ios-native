# 接口文档 

**1. 初始化接口 APM.init 请求方法** 静态方法 **接口名称 init 调用方式 APM.init(config: APMConfig, modules: any[]) 请求参数** 

- **config: APMConfig** (必填) 

   - **context: Context** (必填):应用上下文 

   - **appKey: string** (必填):控制台获取的AppKey 

   - **appSecret: string** (必填):控制台获取的AppSecret 

   - **nick: string** (可选):用户昵称 

   - **userId: string** (可选):用户唯一ID 

   - **channel: string** (可选):应用渠道标识 

   - **hiLog: boolean** (可选):是否启用SDK 内部日志 

   - **customLogger: Logger** (可选):自定义日志处理器 

• **modules: any[]** (必填):可传入 **[performanceApi、crashAnalysisApi] 返回参数** 无返回值 **调用示例** APM.init(apmConfig, [performanceApi]); **认证机制** 通过 **appKey** 和 **appSecret** 参数完成身份验证 

**2. 启动接口 APM.start 请求方法** 静态方法 **接口名称 start 调用方式 APM.start() 请求参数** 无参数 **返回参数** 无返回值 **调用示例** APM.start(); 

**依赖条件** 必须在 **APM.init** 成功执行后调用
