# ArkTS 知识验证索引

> 本文件是整个 skill 体系的知识查找索引。
> 当你不确定某个 ArkTS 知识点时，先按类别找到对应的 reference 文件，读取后再生成代码。
>
> **装饰器版本**：本项目锁 ArkTS V2，下表"首选查找位置"V2 主参考优先；V1 历史参考（legacy）仅用于阅读老代码或迁移老项目。

---

## 按类别查找

| 类别 | 不确定时的典型问题 | 首选查找位置 |
|---|---|---|
| **组件属性** | "Text 有没有 .color() 属性？" "Image 的 objectFit 怎么设？" | `arkts-component-builder/references/common-components.md` |
| **V2 装饰器语法** | "`@Local` 必须初始化吗？" "`@Param + @Once` 是什么？" "`@ObservedV2` 怎么和 `@Trace` 配合？" "`@Monitor` 的签名是什么？" | `arkts-state-manager/references/v2-decorators.md`（主参考）+ 本 skill `references/v2-decorator-rules.md` |
| **V1 装饰器历史** | "`@State` 可以不初始化吗？" "`@ObjectLink` 怎么和 `@Observed` 配合？"（仅用于老项目兼容） | `arkts-state-manager/references/state-decorators.md`（legacy） |
| **V1 → V2 装饰器迁移** | "我的 `@StorageLink` 升 V2 怎么写？" "`@Link` 在 V2 怎么实现双向？" | 本 skill `references/v2-migration-patterns.md` |
| **装饰器版本判定** | "`@State` 是 V2 装饰器吗？" "我能在 `@ComponentV2` 中用 `@Watch` 吗？" | 本 skill `SKILL.md` 顶部"装饰器版本快速判定"表 |
| **权限名称** | "网络请求需要什么权限？" "相机权限的完整字符串是什么？" | `arkts-project-scaffolder/SKILL.md` → 权限速查表 |
| **配置字段** | "module.json5 里 type 字段有哪些值？" "compileSdkVersion 格式？" | `arkts-project-scaffolder/references/config-reference.md` |
| **网络 API** | "http.createHttp() 的参数？" "怎么设请求超时？" | `arkts-data-layer/references/network-service.md` |
| **动画 API** | "animateTo 有哪些参数？" "TransitionEffect 怎么组合？" | `arkts-animation-builder/references/explicit-animation.md` |
| **导航 API** | "NavPathStack 有哪些方法？" "onReady 的 context 结构？" | `arkts-navigation-builder/references/nav-patterns.md` |
| **版本兼容** | "这个 API 是哪个版本引入的？" "@ohos 对应哪个 @kit？" "V2 装饰器要哪个 API 版本？" | 本 skill `references/api12-baseline.md`, `references/api13-21-changes.md`, `references/v2-decorator-rules.md` |
| **迁移步骤（API）** | "router 怎么迁移到 Navigation？" "@ohos 怎么改成 @kit？" | 本 skill `references/migration-patterns.md` |
| **迁移步骤（V1→V2）** | "完整 V1 项目升 V2 步骤？" "`@StorageLink` 怎么改 `AppStorageV2.connect`？" | 本 skill `references/v2-migration-patterns.md` |
| **语言限制** | "ArkTS 能用 any 吗？" "build() 里能写变量吗？" | 本 skill `references/arkts-vs-typescript.md` |
| **状态更新（V2）** | "V2 数组 push 触发刷新吗？" "嵌套 `@ObservedV2` 怎么观察？" | `arkts-state-manager/references/v2-update-patterns.md` |
| **状态更新（V1 legacy）** | "V1 数组 push 为什么 UI 不刷新？" | `arkts-state-manager/references/update-patterns.md`（legacy） |
| **全局状态（V2）** | "`AppStorageV2.connect` 怎么用？" "`PersistenceV2.globalConnect` 能存对象吗？" | `arkts-state-manager/references/v2-global-state.md` |
| **全局状态（V1 legacy）** | "`AppStorage.setOrCreate` 怎么用？" "`PersistentStorage.persistProp` 能存对象吗？" | `arkts-state-manager/references/global-state.md`（legacy） |
| **布局方式** | "Grid 和 List 怎么选？" "Flex 怎么换行？" | `arkts-component-builder/references/layout-patterns.md` |
| **响应式设计** | "折叠屏怎么适配？" "断点怎么设？" | `arkts-component-builder/references/responsive-design.md` |
| **项目结构** | "多模块项目怎么组织？" "HAR 模块怎么配置？" | `arkts-project-scaffolder/references/multi-module-template.md` |
| **数据源** | "IDataSource 怎么实现？" "BasicDataSource 完整代码？" | `arkts-data-layer/references/datasource-patterns.md` |
| **功能模式** | "搜索功能怎么做？" "下拉刷新怎么实现？" | `arkts-pattern-library/references/` |
| **三方库迁移** | "Glide 用什么替代？" "build.gradle 依赖怎么迁移？" | `arkts-library-migration/SKILL.md` + `references/library-mapping-table.md` |
| **系统能力** | "怎么获取相册图片？" "后台播放怎么实现？" "文件存哪里？" | `arkts-system-capabilities/SKILL.md` + `references/` |
| **数据库操作** | "RdbStore 怎么初始化？" "ResultSet 怎么遍历？" | `arkts-data-layer/references/rdbstore-dao-patterns.md` |
| **Skill 路由** | "这个需求该用哪个 skill？" "多个 skill 怎么配合？" | 本 skill `references/skill-routing-guide.md` |

---

## 使用方法

1. 根据你不确定的知识点，在上表中找到对应类别
2. 读取"首选查找位置"指向的 reference 文件
3. 如果 reference 文件中没有找到答案，尝试使用分层查找策略（见 SKILL.md）
4. 如果所有本地 reference 都无法确认，标注 `[待验证]` 并说明推理依据
