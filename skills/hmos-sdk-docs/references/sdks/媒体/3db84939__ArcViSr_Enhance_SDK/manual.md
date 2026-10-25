ArcViSr当虹画质增强SDK集成说明文档 

# **ArcViSr当虹画质增强SDK集成说明文档** 

|版本号|更新日期|维护人|更新信息|
|---|---|---|---|
|Ver1.0.0.1|2026/05/25|ArcVideo|ArcViSr当虹画质增强SDK集成说明文档|

ArcViSr当虹画质增强SDK集成说明文档 

## **ArcViSr当虹画质增强SDK集成说明文档** 

## **1. 文档说明** 

本文档用于说明当虹画质增强SDK(下称'ArcViSr')的集成方式、输入输出处理方式、状态码处理方 式和典型调用流程。 

## **2. SDK能力说明** 

- 输入格式:NV12。 

- 输出格式:NV21。 

- 支持输入分辨率:960x540、1280x720、1920x1080。 

- 输出分辨率:1920x1080。 

- 输入 `pts` 会透传到对应输出帧。 

## **3. 输入输出处理方式** 

调用方需要设置环境变量 `FSSRV_WORKSPACE`,ArcViSr会在该目录中查找模型文件。否则,接口 会自动从依赖库同目录下寻找指定模型。 

ArcViSr根据初始化接口 `ArcViSr_init(input_width, input_height)` 

传入的宽高自动选择模型。模型文件名必须包含对应分辨率字段。 

|初始化宽高|输入格式|输出分辨率|输出格式|模型文件名要求|
|---|---|---|---|---|
|`ArcViSr_init(960,|NV12|1920x1080|NV21|文件名包含|
|540)`||||`960x540`|
|`ArcViSr_init(1280,|NV12|1920x1080|NV21|文件名包含|
|720)`||||`1280x720`|
|`ArcViSr_init(1920, 1080)`|NV12|1920x1080|NV21|文件名包含 `1920x1080`|

#### 如果 `FSSRV_WORKSPACE` 

目录中存在多个匹配文件,ArcViSr会按文件名排序后选择第一个可读取文件。 

## **4. 对外头文件和库** 

#include "arcvisr.h" 

头文件路径: 

inc/arcvisr.h 

动态库名称: 

libArcvisr.so 

ArcViSr当虹画质增强SDK集成说明文档 

## **5. 状态码** 

接口返回 `ArcViSrStatus`。调用方应根据状态码判断调用结果,不建议只按是否为 0 做简单判断。 

|状态码|数值|含义|建议处理|
|---|---|---|---|
|`ARC_VI_SR_STATUS_OK`|0|操作成功|正常继续|
|`ARC_VI_SR_STATUS_NO_ OUTPUT`|1|当前没有可取输出|稍后继续轮询|
|`ARC_VI_SR_STATUS_DRAI NED`|2|drain 等待完成|可继续取剩余输出或结束|
|`ARC_VI_SR_STATUS_INVA LID_HANDLE`|-1|handle 为空或无效|检查初始化是否成功|
|`ARC_VI_SR_STATUS_INVA LID_ARGUMENT`|-2|输入参数无效|检查输入或输出指针|
|`ARC_VI_SR_STATUS_STO PPED`|-3|SDK 正在停止或已经停止|停止调用并释放资源|
|`ARC_VI_SR_STATUS_MO DEL_PATH_EMPTY`|-10|未找到匹配模型,或 `FSSRV_WORKSPACE` 未设置|检查模型目录和文件名|
|`ARC_VI_SR_STATUS_UNS UPPORTED_MODEL`|-11|输入宽高不支持,或模型文 件分辨率不匹配|检查初始化宽高和模型文件 名|
|`ARC_VI_SR_STATUS_MO DEL_PROBE_FAILED`|-12|模型加载或输出尺寸探测失 败|检查模型文件是否存在和可 读|
|`ARC_VI_SR_STATUS_MO DEL_OUTPUT_MISMATCH `|-13|模型输出尺寸不符合链路要 求|检查模型是否匹配当前 SDK|
|`ARC_VI_SR_STATUS_INVA LID_MODEL_CONFIG`|-14|模型或帧尺寸配置无效|检查模型配置|
|`ARC_VI_SR_STATUS_WOR KER_INIT_FAILED`|-15|推理 worker 初始化失败|检查运行环境和模型|
|`ARC_VI_SR_STATUS_UNK NOWN_ERROR`|-100|未分类错误|记录日志并联系当虹 维护方|

#### 状态码可通过下面接口转成字符串: 

const char* ArcViSr_StatusToString(ArcViSrStatus status); 

初始化失败时,`ArcViSr_init(...)` 返回 `nullptr`,可通过下面接口获取失败原因: 

ArcViSrStatus ArcViSr_GetLastStatus(); 

## **6. 接口说明** 

### **6.1 初始化** 

ArcViSrHandle* ArcViSr_init(int input_width, int input_height); 

ArcViSr当虹画质增强SDK集成说明文档 

#### 参数说明: 

|参数|说明|
|---|---|
|`input_width`|输入 NV12 图像宽度。支持 960、1280、1920。|
|`input_height`|输入 NV12 图像高度。支持 540、720、1080。|

#### 返回值说明: 

|返回值|说明|
|---|---|
|非空 handle|初始化成功|
|`nullptr`|初始化失败,可调用 `ArcViSr_GetLastStatus()` 获取原因|

#### 初始化前需要设置模型目录: 

export FSSRV_WORKSPACE=/path/to/model_dir 

#### 或根据调用方的设置方式进行设置。 

### **6.2 输入一帧** 

ArcViSrStatus ArcViSr_SetInput( ArcViSrHandle* handle, const uint8_t* input_nv12_addr, int64_t pts ); 

#### 参数说明: 

|参数|说明|
|---|---|
|`handle`|`ArcViSr_init` 返回的句柄|
|`input_nv12_addr`|输入 NV12 帧地址。传 `nullptr` 表示 drain 等待|
|`pts`|输入帧时间戳,会透传到输出帧|

### **6.3 获取输出** 

ArcViSrStatus ArcViSr_GetOutput( ArcViSrHandle* handle, uint8_t* output_nv21_addr, int64_t* output_pts ); 

#### 参数说明: 

|参数|说明|
|---|---|
|`handle`|`ArcViSr_init` 返回的句柄|
|`output_nv21_addr`|输出 NV21 缓冲区地址,至少 `1920 * 1080 * 3 / 2` 字节|
|`output_pts`|输出帧对应的输入 `pts`,可传 `nullptr`|

ArcViSr当虹画质增强SDK集成说明文档 

### **6.4 释放** 

void ArcViSr_Release(ArcViSrHandle* handle); 

#### 也可以使用兼容封装: 

ArcViSr_Uninit(handle); 

## **7. 推荐调用流程** 

ArcViSrHandle* handle = ArcViSr_init(input_width, input_height); if (handle == nullptr) { ArcViSrStatus status = ArcViSr_GetLastStatus(); printf("ArcViSr_init failed: %d(%s)\n", (int)status, ArcViSr_StatusToString(status)); return -1; } ArcViSrStatus status = ArcViSr_SetInput(handle, input_nv12, pts); if (status != ARC_VI_SR_STATUS_OK) { printf("SetInput failed: %d(%s)\n", (int)status, ArcViSr_StatusToString(status)); } uint8_t* output_nv21 = ...; int64_t output_pts = 0; status = ArcViSr_GetOutput(handle, output_nv21, &output_pts); if (status == ARC_VI_SR_STATUS_OK) { // 成功获得一帧输出 } else if (status == ARC_VI_SR_STATUS_NO_OUTPUT) { // 当前还没有输出,稍后继续轮询 } else { printf("GetOutput failed: %d(%s)\n", (int)status, ArcViSr_StatusToString(status)); } ArcViSr_Release(handle); 

## **8. drain方式** 

当调用方不再送入新帧,但希望等待内部剩余帧处理完成时,可以调用: 

ArcViSrStatus status = ArcViSr_SetInput(handle, nullptr, pts); 

返回 `ARC_VI_SR_STATUS_DRAINED` 表示 drain 等待完成。 

## **9. 集成注意事项** 

- 调用方必须保证初始化宽高、输入 NV12 尺寸和模型文件名三者匹配。 

- 调用方必须保证输出缓冲区大小不小于 `1920 * 1080 * 3 / 2` 字节。 

ArcViSr当虹画质增强SDK集成说明文档 

- `ArcViSr_GetOutput` 返回 `ARC_VI_SR_STATUS_NO_OUTPUT` 

- 不是错误,只表示当前还没有输出。 

- 不要在 `ArcViSr_Release` 之后继续使用同一个 handle。
