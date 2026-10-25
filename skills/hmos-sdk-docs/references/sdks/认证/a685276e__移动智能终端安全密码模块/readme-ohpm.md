> 来源: ohpm 中央仓 README(T1 信源) | 包: `@sca/libscm_napi` | ohpm 最新版: 1.0.1 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# libscm_napi

## 📖 简介

本库 `libscm_napi` 是一个基于 HarmonyOS NAPI(Native API)开发的终端安全密码模块原生能力库,
采用 C++ 编写核心逻辑, 通过 NAPI 桥接为 ArkTS/JavaScript 提供高性能的原生接口调用能力。

本库以 HAR(Harmony Archive)包形式发布,支持多设备类型部署。

---

## ✨ 特性

- 🚀 **高性能**:基于 C++ 原生实现,提供高效的计算与处理能力
- 🔌 **NAPI 桥接**:通过 HarmonyOS NAPI 规范,实现 ArkTS 与 C++ 的无缝调用
- 📱 **多设备支持**:兼容 Phone、Tablet、2in1 等多种设备类型
- 🧪 **单元测试**:集成 Hypium 测试框架,确保代码质量
- 🔒 **代码混淆**:支持发布时的代码混淆与消费者规则配置
- 🛠️ **Stage 模型**:基于 HarmonyOS Stage 模型架构开发

---

## 🚀 快速开始

### 环境要求

- **DevEco Studio**: 4.0+
- **HarmonyOS SDK**: API 9+
- **Node.js**: 14.0+
- **CMake**: 3.16+
- **NDK**: HarmonyOS NDK

### 下载安装

```bash
ohpm install @sca/libscm_napi
```

### 需要权限

```
ohos.permission.INTERNET
```

### 集成使用

在项目的 `oh-package.json5` 中添加依赖:

```json5
{
  "dependencies": {
    "@sca/libscm_napi": "1.0.0",
  }
}
```

在 ArkTS 代码中导入使用:

```typescript
import libscm_napi from 'libscm_napi';

// 调用原生方法
const result = libscm_napi.someNativeMethod(params);
```

---

## 🧪 测试

本项目使用 **Hypium** 测试框架进行单元测试。

---

## 🔗 相关链接

- [HarmonyOS 开发者官网](https://developer.harmonyos.com/)
- [NAPI 开发指南](https://developer.harmonyos.com/cn/docs/documentation/doc-guides-V6/arkts-native-introduction-0000001741998635-V6)
- [Hypium 测试框架](https://gitee.com/openharmony/testfwk_arkxtest)

---

**Made with ❤️ for HarmonyOS**
