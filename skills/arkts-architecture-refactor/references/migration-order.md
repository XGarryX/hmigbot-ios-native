# 改造拓扑顺序

Phase 3 必须按此序执行，逆序会反复返工。

## 阶段 0：根配置（必须最先）

1. 写 `.ohpmrc`（assets/ohpmrc.template）
2. 写根 `oh-package.json5`（assets/root-oh-package.json5.template，按用户选定的 lib_* 子集裁剪）
3. 改 `build-profile.json5`：
   - `app.products[]`：保留现有签名配置
   - `modules[]`：把原 entry 改名为 `phone` 并指向 `./products/phone`，新增 features/components 模块条目
   - 给 phone 模块 targets 加 `buildProfileFields`（assets/build-profile-target.template.json5）
4. `ohpm install`，确认根级依赖能解析（如解析失败先停下排查私仓 token / 网络）

## 阶段 1：骨架（建空目录 + 模块声明）

按 audit/plan 决定的 business 拆分清单：

```
products/phone/                 (从原 entry 迁来)
features/business_common/       (必建，给其他模块依赖)
features/business_<name>/...    (按 plan 列的模块清单)
components/module_<name>/...    (按 plan 列的清单)
```

每个新模块至少包含：
- `oh-package.json5`（feature-oh-package.json5.template）
- `module.json5`
- `Index.ets`（占位空导出）
- `src/main/ets/{components,constants,pages,viewmodel,bean,util}/.gitkeep`

## 阶段 2：基础设施（business_common 优先填充）

把跨业务复用的内容下沉到 `business_common`：
- 颜色 `color.json`（assets/color.json.template）
- 字符串资源
- 通用常量
- 通用 util

> **必须先填 business_common**，因为其他 business 模块依赖它；如果业务模块先迁移再建公共层，会出现循环 import。

## 阶段 3：按 business 模块迁移业务代码

每个 business 一次只迁一个，顺序：
1. 把 entry 里属于该 business 的 .ets 文件按职责分到 `components/constants/pages/viewmodel/bean/util`。
2. ViewModel：替换继承为 `extends BaseViewModel`；组件改 `@ComponentV2`，状态字段改 v2 装饰器。
3. 路由调用：`router.pushUrl/back` → `RouterUtils.push/back`。
4. 网络调用：`@ohos/axios / http.createHttp` → `RequestUtil/ExternalReqUtil`，加 AbortController。
5. DTO：class → interface，可空字段加 `?`。
6. 持久化：直 `@ohos.data.preferences` → `PreferenceUtil`；复杂数据 → `@ohos/dataorm`。
7. UI 适配：硬编码间距 → `breakpoint.pagePadding`；安全区 → `windowTopPadding/BottomPadding`；嵌套深 → `RelativeContainer`。
8. 资源：png/gif → webp/svg。

> 每完成一个 business，跑一次编译确认；不要把全部 business 都改完才编译。

## 阶段 4：components/module_*（公共独立组件）

通常是从原 entry 抽出来的可复用 UI（广告、分享、字号设置等），独立成模块。最后再做，因为它们不依赖 business 但 business 可能依赖它们——先 business 跑通后再下沉公共组件，避免“先下沉后又改回去”。

## 阶段 4.5：壳工程 Index.ets（必须用生成器，禁止手写）⚠️

`products/phone/src/main/ets/pages/Index.ets` 是 Navigation 路由根页，**手写极易漏 NavDestination 包裹**——编译期不报错、运行时所有页面变白屏。强制走生成器：

```bash
# 1. 确保各 business Index.ets 已 export 自家 Page
#    (export { LoginPage } from './src/main/ets/pages/LoginPage';)
# 2. 跑生成器（脚本扫 features/business_*/Index.ets 自动收集 page）
python3 <skill-dir>/assets/gen-page-map.py <project-root> --initial SplashPage

# 3. 静态校验（生成器内置 + 这里再确认一次）
INDEX=<project-root>/products/phone/src/main/ets/pages/Index.ets
grep -A 60 '@Builder' "$INDEX" | grep -q 'NavDestination(' \
  || { echo "❌ FATAL: PageMap 未用 NavDestination 包裹"; exit 1; }
```

详见 [`references/04-state-routing.md` § R6.4-CRITICAL](./04-state-routing.md)。

## 阶段 5：编译闭环

调用 `hmos-fix-build-errors`：

```
build harmony app at <root> in unsigned mode, fix errors in loop until success
```

编译通过后**进入 Phase 4 验证（含 ⑤ 运行时冒烟 HARD-GATE）**——只过编译不算成功，必须看到首屏非空。

通过后输出 `spec/refactor-report.md`。
