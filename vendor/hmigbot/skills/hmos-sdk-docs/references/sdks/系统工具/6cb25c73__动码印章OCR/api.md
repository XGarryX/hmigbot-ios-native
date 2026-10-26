# 动码印章OCR 识别SDK 接口文档(鸿蒙) v1.0.0 

## 编写目的 

为了用户更好的使用动码印章OCR 识别SDK(鸿蒙版)的相关功能,特编写该 文档。 

## 适用范围 

本文档适用于使用动码印章OCR 图片识别SDK(鸿蒙版)的客户公司内部开发 人员、测试人员,动码印章安全技术人员、测试人员、售后实施人员。 

## 功能简介: 

- 1、通用OCR 文字识别,支持离线识别。 

- 2、OCR 文字提取,支持印刷体简体中文、英文、数字等,综合识别准确率高。 

- 3、支持BMP\JPG\PNG 等格式图像输入。 

- 4、可精准检测出不同场景图片中的文本,实现快速定位识别,支持SDK 形式应 用到鸿蒙系统。 

- 5、强大的图像处理功能,可实现自动倾斜矫正、自动过滤红章等干扰背景。 

- 6、针对合同文件、复杂版面,如表格等办公场景中的复杂背景图像中出现的文 

字,数字,英文,进行自动定位、准确识别。 

## 接口文档: 

接口名:图片OCR 文字识别 

方法 :createOCR2 

### 参数说明: 

|参数名|类型|默认值|描述|
|---|---|---|---|
|resourceManager|Object|必填|OCR 处理所需的 资源管理器上下 文。 |
|det_onnx_dir|string|"dbnet.onnx"|检测模型的ONNX 文件路径。|
|rec_onnx_dir|string|"rec.onnx"|识别模型的ONNX 文件路径。|
|yolo_onnx_dir|string|"yolo640.onnx"|YOLO 模型的 ONNX 文件路径。|
|rmseal_onnx_dir|string|"rv_seal256.onnx"|RMSeal 模型的 ONNX 文件路径。|
|max_side_len|string|640|图像处理时的最大 边长。范围: 320 - 2048|
|det_db_thresh|number|0.3|DB(Differentiable Binarization)检测阈 值。范围: 0.0 - 1.0|
|det_db_box_thresh|number|0.5|DB 框检测的阈值。 范围: 0.0 - 1.0|
|det_db_unclip_ratio|number|2.0|扩展检测框的比 例。范围: 1.0 - 3.0|
|use_dilation|number|true|是否对检测框应用 膨胀操作。|
|use_polygon_score|boolean|false|是否使用多边形评 分机制。|
|rec_batch_num|boolean|32|识别模型的批处理 大小。范围: 1 - 128|
|rec_img_h|number|32|识别图像的高度。 范围: 16 - 128|
|rec_img_w|number|32|识别图像的宽度。 范围: 16 - 128|
|yolo_batch_num|number|1|YOLO 模型的批处 理大小。范围: 1 - 64|
|yolo_thresh_num|number|0.5|YOLO 检测的阈 值。范围: 0.0 - 1.0|

|yolo_precision_num|number|0.1|YOLO 的精度参 数。范围: 0.0 - 1.0|
|---|---|---|---|
|debug|boolean|true|是否启用调试模 式。|
|pixelMap|pixelMap|必填|表示图像数据的像 素映射对象,用于|
||||OCR 处理。|
