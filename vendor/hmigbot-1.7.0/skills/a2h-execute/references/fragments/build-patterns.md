# build-patterns — 编译错误速查（错误特征→修法）

> a2h-retrospect 按修复实绩回写，新 pattern 按频次插入。

| 错误特征 | 修法 |
|---|---|
| `arkts-identifiers-as-prop-names`（ValuesBucket 计算属性名） | 字面量内禁 `[expr]: v`；先建空对象再逐条 `bucket[Col.X] = v` |
| EventData 取值类型错 | 两步断言：`const r = data.data as Record<string, Object>;` 再 `r['k'] as string` |
| `arkts-no-untyped-obj-literals` | 定义 interface/class，先赋显式类型变量再用/再传参 |
| promptAction 按钮 color 类型错 | 用 `Color.Red` 或 `$r('app.color.x')`，禁裸 hex 串 |
| @Param/@Prop 撞内置属性名（title/content/action…） | 加域前缀改名：itemTitle/feedTitle |
| `arkts-limited-throw` | `throw (e instanceof Error) ? e : new Error(String(e))` |
| `arkts-no-noninferrable-arr-literals` | 显式类型：`const a: Item[] = xs.map((x): Item => ({...}))` |
| `.margin({vertical/horizontal})` 不存在 | 换 `{top,bottom}` / `{left,right}` |
| List 直接放 Divider 报错 | List 子级只准 ListItem；分隔线用 `.border({width:{bottom:1}})` |
| `TextDecoder` 不存在 | Uint8Array 遍历 `String.fromCharCode` 拼接 |
| http `on('requestEnd')`/`on('error')` | 改 `on('dataEnd')`；error 走 Promise catch |
| 自定义类 `Property 'x' does not exist` | 成员漏声明，补进类体 `private x: number = ...` |
| Button 内 emoji 渲染异常 | 换纯文本 |
| `new ValuesBucket()`/`.put()` 报错 | 它是 type alias：`type VB = Record<string, number\|string\|boolean\|Uint8Array\|null>`，`b['k'] = v` |
| `fromResultSet(rs: any)` 被拒 | 参数改 `Object`：`(rs as Record<string,Function>)['getLong'](idx) as number` |
| `arkts-no-var` | 改 let/const |
| `10903329` Unknown resource | 核对 resources/；`sys.media.ohos_ic_public_*` 可能不存在→改 `app.media.*` 并补图标文件 |
| `10505001` Resource[]→ResourceColor | 去数组括号：`.fontColor($r(...))` |
| `00303221` 非法权限 | 从 module.json5 删除，只用 SDK 预定义权限名 |
| Cannot find name 'xxx' | 补 `@kit.*` import |
| await 报需要 async | 外层函数加 async |
| struct 缺 build() | 补 `build() {}` |
| Duplicate identifier | 删除/改名重复声明 |
| `new SomeType()` 报错 | 先查它是 type alias 还是 class |

<!-- source: hmos-fix-build-errors/references/{known-patterns,arkts-strict-patterns,rdb-entity-pattern}.md + hmos-fix-build-errors/SKILL.md:L141-155 -->
