# arkts-strict — 严格模式规则（编译存活线）

## 类型纪律
1. 禁 `any`/`unknown`；SDK 返回 unknown 立刻断言：`x as object[]`、`ctx.pathInfo.param as Foo`。
2. `as T` 是唯一转换语法（可配 instanceof 窄化）；禁 `<Type>x`、`as const`。
3. 对象字面量必须有显式 class/interface 类型；禁索引签名、解构、class 实例展开、`delete`、计算属性名。
4. 禁 structural typing：class 变量必须 `new C()`，`let c: C = {x:1}` 非法；匿名类非法。
5. 回调参数禁对象字面量类型，用 class/interface；返回类型不可平凡推断的函数/箭头必须显式标注；`.then/.catch` 一律 `(e: Error): void => { ... }` 块体。
6. 禁函数表达式 `function(){}` 当值，一律箭头函数。
7. `JSON.parse(s) as C` 不带类方法——按纯数据 interface 处理。
8. 禁 `// @ts-ignore`；用类型断言/操作替代。

## UI / 组件纪律
9. 组件是 `struct` 非 class（V2 `@ComponentV2`、V1 `@Component`；不能继承/new）；UI 是链式 `Comp().prop(v)`，禁 JSX。
10. build() 只放 UI 描述：禁声明变量、console.log、逻辑语句。
11. V1/V2 装饰器禁混用：@ComponentV2 内禁 @State/@Prop/@Link/@Watch，改 @Local/@Param(+@Event)/@Monitor。
12. @Param/@Prop/@State 必须初始化（`@Param title: string = ''`）；struct 字段必须标类型。
13. 深层 builder 禁隐式捕获 this，用箭头函数。
14. 别虚构属性：Text 用 `.fontColor()` 无 `.color()`；Image 源在构造参数非 `.src()`；尺寸直接用 vp 数字（px2vp 已废弃）。

## 环境差异
15. 无 DOM（禁 document.*）、无 npm 包。
16. import 用 `@kit.*`（'@kit.ArkUI'/'@kit.NetworkKit' 等）；`@ohos.*` 已废弃；禁 `@ohos.router`（用 Navigation+NavPathStack）。
17. 禁虚构 SDK API / sys.symbol 名；不确定用最简单的已文档 API 或参照工程 common/ 既有写法；真未知才标 [待验证]。
18. 权限串精确匹配：网络是 `ohos.permission.INTERNET`（无 NETWORK）；`LOCATION` 必须与 `APPROXIMATELY_LOCATION` 同时申请，单独申请必失败。

<!-- source: docs/skills_optimization_818/design/corpus/CONTRACT.md:L39-48 + arkts-knowledge-verifier/SKILL.md:L145-217 -->
