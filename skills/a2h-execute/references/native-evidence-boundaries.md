# 当前结构接线与动态图片证明范围（0.13.7）

`integration_points` 是端点对的描述协议，例如 `Child.onSaved -> Parent.saved` 或 `Child.value <- Parent.state`，不是 ArkTS 代码。允许 `→`、`←`、`->`、`<-` 和端点可选空 `()`。`@Param url: string`、赋值表达式及带实参调用不属于该字段语法；它们应保留在真实代码与接口合同中，再以真实端点对描述接线。不得为迎合描述字段改坏正确业务代码。

当前 C2 依次尝试 typed call、有界 declarative event/state/same-instance param、platform route 证据。报告 `proof_attempts` 保留每次实际尝试、失败原因与可用恢复说明。声明、同名符号、计划文字和图片加载函数名称均不能单独证明连通；任意多参数 API/第三方 loader/复杂动态回调未被证明时继续保留未通过，不自动扩大白名单或把“无法证明”当成要求改写整个实现。

动态图片尺寸的 `source_bounded_image` 是另一个独立的窄范围规则：当前仅识别有源 Swift/冻结页面合同对应的 transient `image.PixelMap | undefined`、直接 `Image(this.field)`、`width('100%')`、`constraintSize({maxHeight:N})` 和 `ImageFit.Contain` 组合。它不验证网络下载、缓存、占位图或任意 URL loader；通过也保留 `source_visual_unverified`。不要把 `prove_declarative` 的描述语法误称为图片加载能力。

不能证明时先确认是描述错误、缺少明确类型/当前源证据，还是验证器确实不支持；保留实际诊断及源码依据，按原责任补证或修复，再运行原结构检查、受影响构建及已选的行为检查。静态接线通过不证明异步结果、加载成功或视觉一致。

# 占位登记读写

同一 `spec/placeholder-registry.md` 可有多个分组或重复“注册表”标题，每组使用相同六列表头及顺序：`P-ID | location | trigger_condition | status | kind | resolve_by`。读取、质量计数、Stage 3 门禁与写回共用同一解析规则，全部分组纳入；缺列、错序、重复 ID 或表外孤行明确报错，不返回伪造的零欠账。

P-ID 支持英文字母、数字、点号、下划线和连字符，如 `P-ios.button`；仍须全文件唯一。原写回命令支持该 ID 的 resolve/retag。只有显式 `registry.ensure_table_headers: true` 才修复缺表头行组，保留原文字，不隐式调整表头顺序。未知或重复 ID 的其他既有规则仍适用。
