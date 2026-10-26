# API 13~21 增量变化清单

> 本文件记录 API 12 之后每个版本的增量变化，只列出影响代码生成的变更。
> 无重大变化的版本仅简要说明。
>
> **装饰器版本**：API 12 引入 ArkTS V2 装饰器（`@ComponentV2 / @Local / @Param / @Event / @Provider / @Consumer / @ObservedV2 / @Trace / @Monitor / @Computed / AppStorageV2 / PersistenceV2`）。本项目锁 V2，下文 §"版本兼容性总结"中"API 11- → API 12+"的迁移除导入/路由/`@Prop` 初始化外，还包含 V1→V2 装饰器升级（参阅 [`v2-migration-patterns.md`](./v2-migration-patterns.md)）。

---

## API 13（HarmonyOS 5.0.1，2025.01）

**类型**：增量优化，无 Breaking Changes。

- ArkUI 组件微调和 Bug 修复
- 部分系统 API 参数优化
- 无需调整已有代码

---

## API 14（HarmonyOS 5.0.2，2025.02）

**新增能力**：
- **Reader Kit**：文档阅读和渲染能力
- **GPU 渲染增强**：自定义渲染管线 API

**影响代码生成**：
- 新增 `@kit.ReaderKit`（如用户需要文档预览功能）
- GPU 相关 API 通过 C API 提供，ArkTS 层面影响较小

---

## API 15（HarmonyOS 5.0.3，2025.03）

**新增能力**：
- **2in1 设备 API**：折叠/翻转设备状态检测
- **C API 扩展**：更多 Native 接口

**影响代码生成**：
- 2in1 设备需要额外的设备状态监听
- `deviceTypes` 可新增 `"2in1"` 类型
- 响应式布局需要考虑更多屏幕形态

```json5
// module.json5 中可新增 2in1 设备类型
"deviceTypes": ["phone", "tablet", "2in1"]
```

---

## API 17（HarmonyOS 5.0.5，2025.03）

**ArkUI 变更**：
- 部分组件属性签名调整
- List 组件性能优化
- Scroll 组件新增滚动相关事件

**Ability 变更**：
- UIAbility 生命周期方法微调
- Want 参数传递优化

**ArkData 变更**：
- RelationalStore 部分接口参数调整
- Preferences 无变化

**影响代码生成**：
- 如果使用 RelationalStore（关系型数据库），需要检查接口是否有参数变化
- 其他模块向下兼容，API 12 代码可直接运行

---

## API 18（HarmonyOS 5.1.0，2025.06）

**媒体能力增强**：
- 新增音视频编解码 API
- AVPlayer/AVRecorder 接口扩展

**Web 能力增强**：
- WebView 组件功能完善
- 新增 JavaScript 桥接 API

**影响代码生成**：
- 媒体相关需求可以使用更丰富的 API
- Web 组件配置项增加

---

## API 20（HarmonyOS 6.0.0，2025.06）

**大版本更新**，主要变化：

**ArkUI**：
- 组件能力进一步增强
- 动画系统优化
- 新增 UI 组件

**系统服务**：
- 权限模型微调
- 新增分布式能力 API

**影响代码生成**：
- API 12 代码在 API 20 上一般可以运行
- 新增的 API 可以通过 canIUse() 检测后使用
- 建议查阅官方 Release Notes 了解具体新增 API

---

## API 21（HarmonyOS 6.0.1，2025.11）

**当前最新稳定版**。

- 各模块稳定性优化
- 新增设备管理 API
- Bug 修复和性能优化

**影响代码生成**：
- 向下兼容 API 12，无需修改已有代码
- 新增 API 需要在使用前检查版本兼容性

---

## API 23（HarmonyOS 6.x，2026.02，Dev Beta）

**最新开发预览版**，注意：
- Beta API 可能在正式版中变更
- 不建议在生产项目中使用 Beta API
- 如需使用，应做好特性检测和降级处理

---

## 版本兼容性总结

| 从版本 | 到版本 | 兼容性 | 注意事项 |
|---|---|---|---|
| API 12 | API 13~15 | 完全兼容 | 无需修改 |
| API 12 | API 17 | 基本兼容 | 检查 RelationalStore 接口 |
| API 12 | API 18~21 | 基本兼容 | 向下兼容，新 API 需 canIUse 检测 |
| API 11- | API 12+ | 需要迁移 | @Prop 初始化、@ohos→@kit、router→Navigation；本项目还需进一步 V1→V2 装饰器升级（@Component→@ComponentV2 / @State→@Local / @Prop→@Param 等，详见 v2-migration-patterns.md） |

---

## 查阅最新变化

如需了解某个版本的具体变化，使用 WebFetch 或 WebSearch：

```
WebSearch "HarmonyOS API [版本号] release notes site:developer.huawei.com"
```

或直接访问：
- https://developer.huawei.com/consumer/cn/doc/harmonyos-releases/
