# 初始化 

# **CreateInstance(config: Config)** 

Const eyeoflcoudClinet = createInstance({sdk: “<your SDKkey>”}) 

|**config** 参数列表|描述|
|---|---|
|**Context**(可选)|上下文|
|**Datafile**(可选)|表示项目的**JSON** 字符串。必须至少提供一个 **sdkKey** 或数据文件。|
|**sdkKey**(可选)|与项目中的环境关联的键。必须至少提供一个 **sdkKey** 或数据文件。|
|**eventDispatcher**(可选)|用于管理网络调用的事件调度程序。具有调度事 件方法的对象|
|**logger(**可选**)**|用于记录消息的记录器实现。具有日志方法的对 象。|
|**errorHandler(**可选**)**|用于处理错误的错误处理程序对象。具有句柄错 误方法的对象。|
|**userProfileService(**可选**)**|用户配置文件服务。具有查找和保存方法的对 象。|
|**jsonSchemaValidator(**可选**)**|跳过**JSON** 架构验证可提高初始化期间的性能。|
|**datafileOptions(**可选**)**|具有用于自动数据文件管理的配置的对象。|
|**defaultDecideOptions(**可选**)**|**Array of EyeofcloudDecideOption enums.**|

# 创建用户上下文 

# **createUserContext** 

let user = eyeofcloudClinet.createUserContext(“user123”) 

|接口参数列表|描述|
|---|---|
|**userId**|用户**ID**|
|**attributes(**可选**)**|用户属性|

# 分桶方法 

# **Decide** 

let deciion = user.decide(“”product_sort) 

|接口参数列表|描述|
|---|---|
|**flagKey**|特性标帜的键|
|**Options**(可选)|**Array of EyeofcloudDecideOption**|
||**enums.**|

# 跟踪事件 

# **trackEvent** 

User.trackEvent(“purchace”) 

|接口参数列表|描述|
|---|---|
|**eventName**|要跟踪的事件的键|
|**eventTags(**可选**)**|指定此特定事件的标签名称及其相应 标签值的键值对映射。值可以是字符|
||串、数字或布尔值。|
