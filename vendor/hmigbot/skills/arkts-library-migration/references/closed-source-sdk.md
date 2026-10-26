# 闭源 SDK 处理方案

> 当 Android 项目使用了闭源商业 SDK，且该 SDK 没有公开源码时的处理策略。

---

## 三条处理路径

```
闭源 SDK X
  ├─ 路径 A: 厂商已出/将出鸿蒙版 → 等待或催促，直接替换
  ├─ 路径 B: JS-Bridge 过渡 → ArkWeb 加载 JS SDK，postMessage 通信
  └─ 路径 C: 功能替代或厂商更换 → 换用有鸿蒙版的竞品
```

---

## 路径 A：厂商适配

**适用条件**：厂商已发布或明确计划发布鸿蒙版

| SDK | 鸿蒙适配状态 | 处理 |
|-----|------------|------|
| 支付宝 SDK | 已适配 | 直接使用鸿蒙版 |
| 极光推送 | 已适配 | 直接使用鸿蒙版 |
| 友盟+ | 已适配 | 直接使用鸿蒙版 |
| 个推 | 已适配 | 直接使用鸿蒙版 |
| 微信 SDK | 适配中 | 联系厂商获取时间表 |

**操作**：联系厂商商务或技术支持，获取鸿蒙版 SDK 和接入文档。

---

## 路径 B：JS-Bridge 过渡

**适用条件**：
- SDK 有 JS/Web 版本
- 厂商鸿蒙版即将发布但项目等不及
- 功能复杂度适中，JS 性能可接受

### 代码模板

```typescript
// ArkTS 侧 — 创建 Web 组件作为桥接容器（V2，API 12+）
@ComponentV2
struct SdkBridge {
  private webController: WebviewController = new WebviewController()
  private bridgeObject: BridgeInterface = new BridgeImpl()

  build() {
    Web({ src: $rawfile('sdk_bridge.html'), controller: this.webController })
      .javaScriptProxy({
        object: this.bridgeObject,
        name: 'nativeBridge',
        methodList: ['onResult', 'onError'],
        controller: this.webController
      })
      .width(0)  // 隐藏 Web 组件
      .height(0)
  }
}

// Bridge 接口实现
class BridgeImpl {
  onResult(data: string): void {
    const result = JSON.parse(data)
    // 处理 SDK 返回结果
  }

  onError(error: string): void {
    // 处理错误
  }
}
```

```html
<!-- resources/rawfile/sdk_bridge.html -->
<script src="vendor-sdk.js"></script>
<script>
  // 调用 SDK 功能
  function callSdkMethod(params) {
    vendorSdk.doSomething(params, function(result) {
      nativeBridge.onResult(JSON.stringify(result));
    }, function(error) {
      nativeBridge.onError(error.message);
    });
  }
</script>
```

### 注意事项
- JS-Bridge 通信是异步的，注意回调时序
- 传输数据量大时考虑性能影响
- 这是过渡方案，厂商发布鸿蒙版后应替换

---

## 路径 C：功能替代

**适用条件**：
- 厂商无鸿蒙版计划
- 无 JS 版本可用于 Bridge
- 存在功能等价的竞品已适配鸿蒙

**操作**：
1. 评估竞品功能覆盖度
2. 评估迁移成本（API 差异）
3. 商务沟通（价格、合同）
4. 实施替换

---

## 决策流程

```
闭源 SDK X
  ├─ 厂商有鸿蒙版？
  │   ├─ 已发布 → 路径 A：直接替换
  │   └─ 计划中 → 时间可等？
  │       ├─ 是 → 等待 + 先用 Mock
  │       └─ 否 → 有 JS 版本？
  │           ├─ 是 → 路径 B：JS-Bridge 过渡
  │           └─ 否 → 路径 C：竞品替代或功能降级
  └─ 无鸿蒙版计划
      └─ 有竞品已适配？
          ├─ 是 → 路径 C：更换厂商
          └─ 否 → 功能降级 / 标记 Skip
```
