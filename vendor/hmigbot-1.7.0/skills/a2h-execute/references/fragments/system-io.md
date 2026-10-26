# system-io — 系统 IO / 隐式 Want 硬事实

1. **FetchResult 是游标不是数组**：`for...of` 不可用——`getFirstObject()` + `getNextObject()` 逐个取，`close()` 放 finally（否则泄漏）。视频类型 URI 传给 Image 显示灰白，视频项用占位图。
2. **文件只能写沙箱**：`context.filesDir` / `context.cacheDir`；绝对路径（`/storage/emulated/0/...`）→ Permission denied。
3. **隐式拉起需 module.json5 `skills` 声明**：相机须 `entity.system.camera` + `ohos.want.action.camera`；响应外部查看须 `ohos.want.action.view`。无需声明：浏览器跳转（`viewData` 内置）、显式 Want 跳系统设置。
4. **workScheduler 后台定时任务**：须在 module.json5 声明对应 `extensionAbilities` type，裸调不生效。

<!-- provenance: runtime（真机迁移实证）
     source: arkts-system-capabilities/SKILL.md L141-147,L161-175,L250-282 -->
