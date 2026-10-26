# 静态分析与 App 身份

## CHECK-1：静态分析

扫描本次范围内各模块的生产 `.ets` 文件，排除构建产物、缓存和第三方依赖。使用 `rg -n -g '*.ets'` 定位候选，再读取上下文确认；注释、字符串和普通同名标识符不作为违规。

| 检查项 | 定位与复核方式 | 级别 |
|---|---|---|
| `any` 类型 | 搜索 `\bany\b`，确认是否为类型用法 | ERROR |
| 旧 `@ohos.*` 导入 | 搜索 `@ohos\.`，确认 import 来源，列出迁移建议 | WARN |
| SQL 拼接 | 搜索 SQL 关键字与数据库执行调用，复核是否通过字符串拼接构造 SQL | ERROR |
| `as` 类型断言 | 搜索 `\bas\b`，确认断言用法 | WARN |
| `eval()` | 搜索 `\beval\s*\(`，确认动态执行调用 | ERROR |
| `aboutToAppear` 中获取路由参数 | 定位 `aboutToAppear` 方法，复核其中的 `pathInfo` 参数读取 | ERROR |

每个有效命中记录文件、行号、规则和简短依据。ERROR 为 0 则 PASS；有 ERROR 则 FAIL。WARN 只附报告，不单独触发修复回环。没有找到应验证的源码时记录输入缺口，不能以零命中判 PASS。

## CHECK-2：App 身份校验

读取 `AppScope/app.json5`、模块配置及实际引用的字符串/图标资源；名称以项目已有 Spec 中的 App 名称为依据。

| 项目 | 检查规则 | 判定 |
|---|---|---|
| bundleName | 仍匹配 `com.example.*` | FAIL |
| vendor | 仍为 `example` | FAIL |
| versionName | 仍为 `1.0.0`，可能未与 Android 同步 | WARN |
| app_name | 解析应用实际引用的名称资源；与 Spec 已明确记录的名称不一致 | FAIL |
| 前景/背景图标 | 对实际使用的 foreground/background PNG 检查大小，≤ 1 KB 时提示疑似默认图 | WARN |
| 自适应图标 | `layered_image.json` 存在，前景/背景引用均可解析到实际资源 | 缺失或引用错误为 FAIL |

路径与资源名按当前工程解析，避免把示例文件名当作唯一合法配置。未记录预期 App 名称时注明未做名称一致性比较；无法读取必要配置或资源时记录相应缺口。

有明确 FAIL 则 CHECK-2 为 FAIL；仅因缺失输入无法完成必要判断时为 PARTIAL/DEFERRED；其余为 PASS，附 WARN 和不适用项说明。可按需参考 `arkts-app-identity` 解释配置，以上规则也可直接执行。
