# 华为HarmonyOS内存泄漏故障模式库

> 本文件由Excel故障模式库转换整理

---

## 1 使用说明

### 1.1 列字段定义

| 列名 | 说明 |
|------|------|
| 故障对象 | 发生故障的对象（如ArkTS内存、RSS内存等） |
| 故障模式 | 故障对象出现故障的具体方式 |
| 故障原因 | 导致该故障的具体原因或行为 |
| 故障影响 | 该故障导致的更高级别故障或外部表现 |
| 故障检测机制 | 如何检测该故障 |
| 改进措施 | 针对该故障的改进建议 |

### 1.2 故障传播关系

- **故障原因** = 下一级故障模式
- **故障影响** = 上一级故障模式
- **一级故障影响** = 故障场景 + 故障类型

---

## 2 对象索引目录

### 2.1 基础语言与基础库内存泄漏

- ArkTS内存
- RSS内存
- PSS内存

### 2.2 内核内存泄漏

- 内核ION内存
- 内核GPU内存
- 内核Ashmem内存
- 内核VMA内存

### 2.3 三方框架内存泄漏

- 龙雀JSVM内存
- ArkWeb V8内存
- KMP/Kotlin内存
- Flutter/Dart内存
- RN/Hermes内存

---

## 3 故障模式详情

### 3.1 ArkTS内存

**故障类型**: 基础语言与基础库内存泄漏

---

**故障模式1**: ArkTS内存OOM

- **故障原因**: 
  - 对象被ROOT_VM类型的根节点持有（被Source_Text_Module_Record或global_env持有）
  - 对象被ROOT_FRAME类型的根节点持有（栈上对象未释放）
  - 对象被ROOT_HANDLE类型的根节点持有（LocalHandle/GlobalHandle未释放）
  - 一次性分配超大对象导致OOM
  - 对象频繁变动导致hclass不断创建，引发nonmoveable space OOM

- **故障影响**: 应用闪退（基础语言与基础库内存泄漏）

- **故障检测机制**: 
  - 订阅hiAppEvent.event.RESOURCE_OVERLIMIT事件，resource_type为js_heap
  - Local Heap：主线程448M，子线程768M
  - Shared Heap：778M
  - Total Heap：1.5G

- **改进措施**: 
  - 正确使用napi_open_handle_scope/napi_close_handle_scope
  - 及时调用napi_delete_reference删除引用
  - 及时调用napi_remove_wrap解绑
  - 及时调用napi_resolve_deferred/napi_reject_deferred关闭Promise

---

**故障模式2**: 对象被ROOT_VM类型的根节点持有

- **故障原因**:
  - 泄漏对象被模块级变量持有（export对象被sourceTextModule持有）
  - 泄漏对象被全局变量持有（globalEnv/globalThis）
  - 泄漏对象被闭包持有，闭包被虚拟机持有

- **故障影响**: ArkTS内存OOM

- **故障检测机制**: 
  - 将内存对象按Retained size排序，查看distance为1的引用根节点是否是ROOT_VM类型

- **改进措施**:
  - 业务层断开模块级变量的引用
  - 业务层清理全局变量中的不必要引用
  - 清理未使用的闭包

---

**故障模式3**: 对象被ROOT_FRAME类型的根节点持有

- **故障原因**:
  - 泄漏对象在栈上被创建或被栈上相关对象引用
  - 函数未退栈导致局部变量被长期持有

- **故障影响**: ArkTS内存OOM

- **故障检测机制**: 
  - 查看对象的引用根节点（distance为1）是否是ROOT_FRAME类型

- **改进措施**:
  - 避免在长生命周期函数中创建大对象
  - 及时退栈

---

**故障模式4**: 对象被ROOT_HANDLE类型（LocalHandle）的根节点持有

- **故障原因**:
  - 开发者创建的napi_value未使用scope管理
  - 开发者创建的napi_value使用scope但未调用close
  - 系统框架创建的napi_value未使用scope管理
  - 系统框架创建的napi_value使用scope但未调用close
  - 异步函数导致scope范围失效

- **故障影响**: ArkTS内存OOM

- **故障检测机制**: 
  - 查看对象的引用根节点（distance为1）是否是ROOT_LOCAL_HANDLE类型

- **改进措施**:
  - 正确配对使用napi_open_handle_scope/napi_close_handle_scope
  - 异步函数中使用独立的scope
  - 分析调用栈确认是应用创建还是框架创建

---

**故障模式5**: 对象被ROOT_HANDLE类型（GlobalHandle）的根节点持有

- **故障原因**:
  - napi_create_reference创建的引用未删除
  - napi_wrap强引用未解绑
  - napi_threadsafe_function引用计数未清零
  - napi_create_promise未闭环
  - 闭包被GlobalHandle持有
  - 定时器setInterval未清理

- **故障影响**: ArkTS内存OOM

- **故障检测机制**: 
  - 查看对象的引用根节点（distance为1）是否是ROOT_GLOBAL_HANDLE类型

- **改进措施**:
  - 及时调用napi_delete_reference
  - 及时调用napi_remove_wrap
  - 及时调用napi_release_threadsafe_function
  - 及时调用napi_resolve_deferred/napi_reject_deferred
  - 及时清理定时器

---

### 3.2 RSS内存

**故障类型**: 基础语言与基础库内存泄漏

---

**故障模式1**: RSS泄漏

---

**故障模式1**: RSS泄漏

- **故障原因**:
  - NativeHeap堆过大（malloc/new未释放）
  - 匿名映射过大（mmap未释放）
  - ArkTS虚拟机堆过大
  - 龙雀JSVM虚拟机堆过大
  - KMP/Kotlin堆过大
  - Flutter/Dart虚拟机堆过大
  - RN/Hermes虚拟机堆过大
  - ArkWeb V8虚拟机堆过大
  - 共享库过大
  - 数据库文件过大
  - 字体文件过大
  - HAP包过大

- **故障影响**: 应用闪退（基础语言与基础库内存泄漏）

- **故障检测机制**: 
  - 单进程RSS值超4G，且整机内存小于800MB

- **改进措施**:
  - 使用hidebug接口抓取profiler分析内存使用
  - 合理管理malloc/new配对
  - 合理管理mmap/unmap配对

---

### 3.3 PSS内存

**故障类型**: 基础语言与基础库内存泄漏

---

**故障模式1**: 进程泛PSS泄漏

- **故障原因**:
  - RSS内存过大
  - ION内存过大
  - GPU内存过大

- **故障影响**: 应用闪退（基础语言与基础库内存泄漏）

- **故障检测机制**: 
  - 单进程PSS值超基线

- **改进措施**:
  - 参考各子类型内存的改进措施

---

### 3.4 内核ION内存

**故障类型**: 内核内存泄漏

---

**故障模式1**: 内核ION内存泄漏

- **故障原因**:
  - 应用通过AvCodec持有的Ashmem+ION内存未释放
  - Media创建播放器实例总量超50MB
  - GPU内存占用过大

- **故障影响**: 应用闪退（内核内存泄漏）

- **故障检测机制**: 
  - 整机ION内存200s检测一次，需要5次超过2800M

- **改进措施**:
  - 及时释放AvCodec资源
  - 控制播放器实例数量
  - 媒体领域设立独立查杀规格

---

### 3.5 内核GPU内存

**故障类型**: 内核内存泄漏

---

**故障模式1**: 内核GPU内存泄漏

- **故障原因**:
  - Image控件泄漏或缓存过多
  - ArkWeb控件泄漏
  - XComponent组件泄漏或缓存过多
  - 视频软硬编解码器API使用不当
  - 单应用GPU内存占用超过整机内存1/3

- **故障影响**: 应用闪退（内核内存泄漏）

- **故障检测机制**: 
  - 整机GPU内存200s检测一次，需要5次超过2300M

- **改进措施**:
  - 及时释放Image/ArkWeb/XComponent资源
  - 正确使用视频编解码器API

---

### 3.6 内核Ashmem内存

**故障类型**: 内核内存泄漏

---

**故障模式1**: 内核Ashmem内存泄漏

- **故障原因**:
  - ArkTS API使用不配对（ashmem.create/closeAshmem, mapAshmem/unmapAshmem）
  - OH_DDK接口使用不配对（CreateAshmem/DestroyAshmem, MapAshmem/UnmapAshmem）
  - posix接口使用不配对（open/close, mmap/unmap）
  - 应用截图导致

- **故障影响**: 应用闪退（内核内存泄漏）

- **故障检测机制**: 
  - 整机ashmem内存200s检测一次，需要5次超过阈值

- **改进措施**:
  - 正确配对使用API接口
  - 及时释放截图资源

---

### 3.7 内核VMA内存

**故障类型**: 内核内存泄漏

---

**故障模式1**: 内核VMA内存泄漏

- **故障原因**:
  - 应用不合理使用mmap和unmap，没有配对
  - 内存分配器实现问题，粒度过细导致VMA个数过多

- **故障影响**: 应用闪退（内核内存泄漏）

- **故障检测机制**: 
  - 应用进程VMA内存块个数超阈值65535*90%

- **改进措施**:
  - 合理配对使用mmap/unmap

---

### 3.8 KMP/Kotlin内存

**故障类型**: 三方框架内存泄漏

---

**故障模式1**: KMP/Kotlin内存泄漏

- **故障原因**:
  - Kotlin对象被Global对象持有（JNI GLOBAL）
  - Kotlin对象被线程本地存储或运行栈中对象持有（JAVA LOCAL）

- **故障影响**: 应用闪退（三方框架内存泄漏）

- **故障检测机制**: 
  - 超过水线（待定）

- **改进措施**:
  - 避免全局变量持有Kotlin对象
  - 正确使用@ThreadLocal
  - 及时清理Worker任务

---

### 3.9 Flutter/Dart内存

**故障类型**: 三方框架内存泄漏

---

**故障模式1**: Flutter/Dart内存泄漏

- **故障原因**:
  - Dart对象被Native持有（PersistentHandle未删除）
  - Dart对象被Dart自身持有（全局根对象引用）
  - Dart对象持有Native对象，存在循环引用
  - 闭包把BuildContext带进异步世界
  - AnimationController没有dispose
  - pop前忘cancel，State随事件链常驻

- **故障影响**: 应用闪退（三方框架内存泄漏）

- **故障检测机制**: 
  - 超过水线（待定）

- **改进措施**:
  - 及时调用Dart_DeletePersistentHandle
  - 清理全局根对象引用
  - 及时dispose AnimationController
  - 及时cancel订阅

---

### 3.10 龙雀JSVM内存

**故障类型**: 三方框架内存泄漏

---

**故障模式1**: 龙雀JSVM OOM

- **故障原因**:
  - JS对象长期被JS持有（ROOT_Stack_Roots、Root_Micro_Tasks）
  - JS对象被Native持有（GlobalHandle、LocalHandle）
  - js对象被context持有（创建大量context未销毁）

- **故障影响**: 应用闪退（三方框架内存泄漏）

- **故障检测机制**: 
  - 堆内存大小超过阈值1400MB

- **改进措施**:
  - 正确使用HandleScope
  - 及时删除global/persistentHandle
  - 及时释放Context

---

### 3.11 ArkWeb V8内存

**故障类型**: 三方框架内存泄漏

---

**故障模式1**: ArkWeb v8 OOM

- **故障原因**:
  - JS对象被Global对象持有
  - JS对象被闭包函数长期持有
  - JS对象被全局缓存集合持有（Map/Set/Array无限堆积）
  - JS对象被Native持有

- **故障影响**: 应用闪退（三方框架内存泄漏）

- **故障检测机制**: 
  - 堆内存大小超过阈值2048MB

- **改进措施**:
  - 清理全局缓存
  - 及时清理闭包引用
  - 正确使用HandleScope

---

### 3.12 RN/Hermes内存

**故障类型**: 三方框架内存泄漏

---

**故障模式1**: RN/Hermes内存泄漏

- **故障原因**:
  - JS对象被Global对象间接持有
  - JS对象被闭包捕获导致内存无法释放
  - 事件监听器未正确移除
  - global/persistentHandle构造后未释放
  - Context::New调用后未释放
  - TurboModule异步回调未释放JS对象引用

- **故障影响**: 应用闪退（三方框架内存泄漏）

- **故障检测机制**: 
  - 超过水线（待定）

- **改进措施**:
  - 正确移除事件监听器
  - 及时释放global/persistentHandle
  - 及时释放Context

---