# 1 概述 

本文介绍 harmony 设备接入及集成 ASR 语音识别。 

# 2 工程配置 

# 2.1 SDK 导入 

将开发包中 libs 目录下 hy_asr_library.har 文件拷贝至 Harmony 工程的 新建 libs 目录下,如图 

# 2.2 权限设置 

需要配置录音权限,参考 Harmony 开发文档 

https://developer.huawei.com/consumer/cn/doc/harmonyosguides-V5/request-user-authorization-V5 

- 3 Harmony 开发 

# 3.1 语音识别 

# 3.1.1 setAsrParams 配置语音识别参数 

setAsrParams(asrParam: AsrParam) 

# 3.1.2 setAsrCallback 配置语音识别数据返回回调 

setAsrCallback(asrCallback: RDAsrCallback) 

# 3.1.3 startAsrRecord 开始识别 

startAsrRecord() 

# 3.1.4 stopAsrRecord 停止识别 

stopAsrRecord() 

# 3.1.5 releaseAsrRecord 回收并释放语音识别 

releaseAsrRecord() 

4 常见错误码
