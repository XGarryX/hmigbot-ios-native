# 海泰方圆电子签章系统SDK 接口文档 

(Harmony OS 版本) 

### 目录 

|海泰方圆电子签章系统SDK 接口文档........................................................ 1|
|---|
|一、 常量介绍...................................................................................... 3|
|二、 接口说明...................................................................................... 3|
|2.1 返回组件提供者信息............................................................ 3|
|2.2 获取电子印章列表................................................................ 4|
|2.3 获取电子印章........................................................................ 4|
|2.4 获取电子印章信息................................................................ 4|
|2.5 获取电子印章图像................................................................ 5|
|2.6 获取签名时间........................................................................ 6|
|2.7 获取签名算法标识................................................................ 6|
|2.8 获取摘要算法标识................................................................. 6|
|2.9 代理计算摘要........................................................................ 6|
|2.10 代理计算签名...................................................................... 7|
|2.11 代理验证签名...................................................................... 7|
|2.12 获取电子签章图像.............................................................. 8|
|2.13 获取错误信息....................................................................... 8|

## 一、 常量介绍 

### 1.1 函数返回值常量 

### 函数返回值定义如表 1 所示。 

|序号|含义|取值|备注|
|---|---|---|---|
|1|调用成功|0x00000000|常量名为OES_OK|
|2|使用者主动取消|0x00000010|常量名为OES_CANCEL|
|3|预留使用|0x00000000~0x00001111|错误码不得占用|

|1.2 印章图 序号|像常量 含义|取值|备注|
|---|---|---|---|
|1|用于显示|0x00000000|常量名为OES SEALIMAGE FLAG DISPLAY|
|2|用于打印|0x00000001|常量名为OES SEALIMAGE FLAG PRINT|
|3|用于打印预览|0x00000002|常量名为OES SEALIMAGE FLAG_PREVIEW|

## 二、 接口说明 

### 2.1 返回组件提供者信息 

功能说明:返回签章组件提供者信息。 接口原型: 

int OES GetProviderInfo(unsigned char * puchName, int* piNameLen,unsigned char * puchCompany,int* piCompanyLen,unsigned char * puchVersion,int* piVersionLen,unsigned char * puchExtend, int* piExtendLen) 

参数说明(8 个参数): 参数1:[out] puchName 名称(UTF-8 编码); 参数2:[out/in]piNameLen 名称长度; 参数3:[out] puchCompany 公司名称(UTF-8 编码); 参数4:[out/in] piCompanyLen 公司名称长度; 参数5:[out]puchVersion 版本(UTF-8 编码); 参数6:[out/in]piVersionLen 版本长度; 参数7:[out] puchExtend 扩展信息(UTF-8 编码); 参数8:[out/in] piExtendLen 扩展信息长度 返回值说明:调用成功返回 OES OK,否则是错误代码, 

### 2.2 获取电子印章列表 

功能说明: 

获取电子印章列表,该函数用于进行印章名称到标识的转换 接口原型: 

int OES GetSealList(unsigned char * puchSealListData,int * piSealListDataLen)参数说明(2 个参数): 参数1:[out] puchSealListData 印章列表数据(UTF-8 编码); 参数2:[out/in】piSealListDataLen 印章列表数据长度。 返回值说明: 调用成功返回 OES OK,否则是错误代码。 

### 2.3 获取电子印章 

功能说明: 

获取指定标识的电子印章数据接口原型: 

piSealDataLen) 

参数说明(3 个参数): 参数1:[in]puchSealld 印章标识或名称(字符串); 参数 2:[in]iSealldLen 印章标识或名称长度; 参数3:[out]puchSealData 印章数据; 参数4:[out/in] piSealDataLen 印章数据长度。 返回值说明: 调用成功返回 OESOK,否则是错误代码: 

### 2.4 获取电子印章信息 

功能说明: 获取电子印章信息, 接口原型: int OES GetSealInfo(unsigned char * puchSealData,int iSealDataLen, unsigned char * puchSealld,int* piSealldLen, unsigned char * puchVersion,int * piVersionLen, unsigned char * puchVenderId,int* piVenderldLen, unsigned char * puchSealType,int * piSealTypeLen, unsigned char * puchSealName,int * piSealNameLen, unsigned char * puchCertInfo,int * piCertInfoLen, unsigned char * puchValidStart,int * piValidStartLen,unsigned char * unsigned char * puchValidEnd,int * piValidEndlen,char *unsignec unsigned char * puchSignedDate,int * piSignedDateLen,unsigned char * unsigned char * puchSignerName,int * piSignerNamel unsigned char * puchSignMethod,int * piSignMethodLen) 参数说明(24 个参数) 

参数1:[in] puchSealData 印章数据; 

参数2:[in] iSealDataLen 印章数据长度; 

参数3:[out] puchSealld 头信息-印章标识; 

参数4:[out/in] piSealIdLen 头信息-印章标识长度; 

参数5:[out] puchVersion 头信息-版本; 

参数6:[out/in] puchVersionLen 头信息-版本长度; 

参数7:[out] puchVenderld 头信息-厂商标识; 

参数8:[out/in] puchVenderldLen 头信息-厂商标识长度; 

参数9:[out] puchSealType 印章信息-印章类型; 

参数10:[out/in] puchSealTypeLen 印章信息-印章类型长度; 

参数11:[out] puchSealName 印章信息-印章名称 

参数 12[out/in] piSealNameLen 印章信息-印章名称长度;out/in 参数 13:[out] puchCertInfo 印章信息-证书列表信息; 参数 14:[out/in] puchCertInfoLen 印章信息-证书列表信息长度; 参数 15:[out] puchValidStart 印章信息-有效起始时间, 参数 16:[out/in] piValidStartLen 印章信息-有效起始时间长度; 参数 17:[out] puchValidEnd 印章信息-有效结束时间; 

参数18:[out/in] piValidEndLen 印章信息-有效结束长度; 参数 19:[out] puchSignedDate 印章信息-制作日期; 参数20:[out/in] piSignedDateLen 印章信息-制作日期长度: 参数21:[out] puchSignerName 签名信息-制章人; 参数22:[out/in] piSignerNameLen 签名信息-制章人长度; 参数23:[out] puchSignMethod 签名信息-制章签名方法; 

### 2.5 获取电子印章图像 

功能说明: 获取电子印章图像 接口原型:int OES GetSealImage(unsigned char * puchSealData, int iSealDataLen,int iRenderFlag,unsigned char * puchSeallmage,int* piSeallmageLen,int* piSealWidth, int* piSealHeight) 

参数说明(7 个参数): 

参数1:[in]puchSealData 印章数据; 参数 2:[in]iSealDataLen 印章数据长度; 参数 3:[in] iiRenderFlag 绘制用途标记; 参数4:[out] puchSealmage 印章图像数据; 

参数 5:[out/in]piSeallmageLen 印章图像数据长度 

参数6:[out/in]piSealWidth 印章宽度(单位 mm); 参数 7:[out/in]piSealHeight 印章高度(单位 mm) 返回值说明: 

调用成功返回 OES_OK,否则是错误代码。 

### 2.6 获取签名时间 

功能说明: 获取签名时间(时间戳或明文形式) 接口原型: 

int OES_GetSignDateTime(unsigned char *puchSignDateTime,int * piSignDateTimeLen) 参数说明(2 个参数): 

参数 1:[out] puchSignDateTime 签名时间(字符时用 UTF-8 编码;时间戳时二进制值); 参数2:[out/inpiSignDateTimeLen 时间截长度 

返回值说明: 

调用成功返回 OES_OK,否则是错误代码。 

### 2.7 获取签名算法标识 

功能说明: 获取签名算法标识。 接口原型: 

int OES GetSignMethod(unsigned char * puchSignMethod,int * piSignMethodLen) 参数说明(2 个参数): 

参数1:[out] puchSignMethod 签名算法(UTF-8 编码); 参数2:[out/in]piSignMethodLen 签名算法长度。 返回值说明: 调用成功返回 OES_OK,否则是错误代码 

### 2.8 获取摘要算法标识 

功能说明: 获取摘要算法标识。 接口原型: 

int OES GetDigestMethod(unsigned char * puchDigestMethod,int * piDigestMethodLen) 参数说明(2 个参数): 

参数1:[out] puchDigestMethod 摘要算法(UTF-8 编码); 参数2:[out/in] piDigestMethoden 摘要算法长度。 返回值说明: 调用成功返回 OES_OK,否则是错误代码。 

### 2.9 代理计算摘要 

功能说明: 代理计算摘要 接口原型: 

int OES Digest(unsigned char * puchData,int iDataLen, unsigned char * puchDigestMethod,int iDigestMethodLen, unsigned char * puchDigestValue,int* piDigestValueLen) 参数说明(6 个参数): 

参数1:[in]:puchData 待摘要的数据 参数2:[in]: iDataLen 待摘要的数据长度 参数3:[in]: puchDigestMethod 摘要算法 参数4:[in]: iDigestMethodLen 摘要算法长度 参数5:[out]: puchDigestValue 摘要值 参数6:[out/in]: piDigestValueLen 摘要值长度 返回值说明 调用成功返回OES_OK,否则是错误代码。 

### 2.10 代理计算签名 

功能说明: 代理计算签名,如果计算前需要输入密码,应由组件实现者需要提供输入界面。 接口原型: 

int OES Sign(unsigned char * puchSealld,int iSealldLen, unsigned char * puchDocProperty,int iDocPropertyLen, unsigned char * puchDigestData,intiDigestDataLen, unsigned char * puchSignMethod,int iSignMethodLen, unsigned char * puchSignDateTime,int iSignDateTimeLen, unsigned char * puchSignValue,int* piSignValueLen) 参数说明(12 个参数): 

参数1:[in] puchSealld 印章标识; 参数 2:[in]iSealldLen 印章标识长度; 参数 3:[in] puchDocProperty 文档信息,一般为 Signature.xml 的绝对路径; 参数 4:[in]文档信息长度;iDocPropertyLen 参数 5:[in]puchDigestData 摘要数据; 参数 6:[in]iDigestDataLen 摘要数据长度; 参数 7:[in] puchSignMethod 签名算法; 参数 8:[in] iSignMethodLen 签名算法长度; 参数 9:[in] puchSignDateTime 签名时间; 参数 10:[in] iSignDateTimeLen 签名时间长度; 参数11:[out] puchSignValue 签名值; 参数 12:[out/in] piSignValueLen 签名值长度。 返回值说明: 调用成功返回 OES_OK,否则是错误代码 

### 2.11 代理验证签名 

功能说明: 

### 代理验证签名,离线验证时该接口应在不插入智能密码钥匙时可用。接口原型: 

int OES Verify(unsigned char * puchSealData,int iSealDataLen, unsigned char * puchDocProperty,int iDocPropertyLen, unsigned char * puchDigestData,int iDigestDataLen, unsigned char * puchSignMethod,int iSignMethodLen, unsigned char * puchSignDateTime,int iSignDateTimeLen, unsigned char * puchSignValue,int iSignValueLen, int iOnline) 参数说明(11 个参数): 

参数1:[in]puchSealData 印章数据; 参数 2:[in]iSealDataLen 印章数据长度; 参数 3:[in]puchDocProperty 文档信息; 参数 4:[in]iDocPropertyLen 文档信息长度; 参数 5:[in]puchSignMethod 签名算法; 参数 6:[in]iSignMethodLen 签名算法长度; 参数 7:[in]puchSignDateTime 签名时间; 参数 8:[inpiSignDateTimeLen 签名时间长度; 参数 9:[in]puchSignValue 签名值; 参数 10:[in]iSignValueLen 签名值长度; 参数 11:[in]iOnline 是否在线验证。 返回值说明: 调用成功返回 OES_OK,否则是错误代码。 

### 2.12 获取电子签章图像 

### 功能说明: 

获取电子签章数据中的图像及其他信息,该接口应在不插入智能密码钥匙时可用。接口原型: int OES_GetSignlmage(unsigned char * puchSignedValueData,int iSignedValueLen,int iRenderFla unsigned char * puchSeallmage,int* piSeallmageLen,int * piSealWidth,int * piSealHeight) 参数说明(7 个参数): 

参数1:[in]puchSignedValueData 签章数据; 参数 2:[in] iSignedValueLen 签章数据长度; 参数 3:[in]iRenderFlag 绘制用途标记; 参数4:[out] puchSealmage 印章图像数据; 参数5:[out/in] piSeallmageLen 印章图像数据长度; 参数6:[out/in]piSealWidth 印章宽度(单位 mm); 参数7:[out/in]piSealHeight 印章高度(单位 mm)。 返回值说明: 

调用成功返回 OES_OK,否则是错误代码。 

### 2.13 获取错误信息 

功能说明: 

获取错误信息。 接口原型: int OES GetErrMessage(unsigned long errCode, unsigned char* puchErrMessage,int* piErrMessageLen)参数说明(3 个参数): 参数1:[in] errCode 错误代码; 错误信息(UTF-8 编码); 参数2:[outpuchErrMessage 参数3:[out/in】 piErrMessageLen 错误信息长度。 返回值说明: 无
