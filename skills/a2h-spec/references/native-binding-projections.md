# 可选原生目标显隐投影

本格式供原 C4/SPEC 作者记录已经批准的平台映射，原阶段、门禁、AC 和源显隐账保持不变。不因出现某类系统控件而要求所有工程创建此文件。

唯一机器输入为目标工程 `spec/baseline/ui/target-binding-projections.json`。不存在时沿用原 binding 检测结果，pipeline 仍核对新鲜孤儿图；存在但格式损坏/未知键/重复 id 或行号时返回 2，不能静默回退。合法但过期或无法证明的项保留原行 FAIL；不修改源账或业务代码来迎合检测。

## 格式

```json
{
  "schema": "native-binding-projections.v1",
  "projections": [{
    "id": "approved-form-presence",
    "source_row_index": 0,
    "source_row_sha256": "原 rows 数组内该行完整原始字节的 SHA256",
    "mapping_ref": {"file": "spec/baseline/features/F001-example.mapping.md", "anchor": "form-presence-mapping", "section_sha256": "该节原始字节 SHA256"},
    "proof": {
      "kind": "harmony-form-optional-presence.v1",
      "producer": {"file": "entry/src/main/ets/form/Binding.ets", "data_function": "makeData", "input_parameter": "payload", "boolean_field": "hasPayload", "binding_function": "makeBinding"},
      "extension": {"file": "entry/src/main/ets/form/FormProvider.ets", "class": "FormProvider", "form_profile": "entry/src/main/resources/base/profile/form_config.json", "form_name": "ExampleForm"},
      "receiver": {"file": "entry/src/main/ets/form/pages/FormEntry.ets", "component": "FormEntry", "storage_member": "hasPayload"},
      "render": [{"file": "entry/src/main/ets/form/pages/FormBody.ets", "component": "FormBody", "param": "hasPayload"}]
    }
  }]
}
```

示例值需替换为实际事实，不能直接作为正式输入。`source_row_index` 从原 `visibility-bindings.json` 的 `rows` 数组按 0 开始编号。原行 SHA 使用 UTF-8 原始行对象字节，不能反序列化后重新格式化计算。mapping 节包含 `projection-id:<id>` 反向指针；该节原始字节哈希绑定已批准的语义说明。源路径和表达式从原行取得，不另写第二份源事实。

## 证明范围

当前支持单一 Swift `if let value = member.path { … }`，可带一个普通 `else`。使用现有选定 Release Source 和 Xcode 的 SwiftSyntax tokens/visibility 事实定位；不支持的语法保持原 FAIL。源表达式的完整成员路径对应同一谓词，drivers 里的词项不是多个独立条件。

目标证明使用所选官方 HarmonyOS SDK 的 ETS parser/checker：可选参数经严格 `!== undefined` 形成不可改写布尔字段，实际返回官方 FormBindingData；真实注册的 FormExtensionAbility 和所有模块 updateForm 数据来自该绑定；profile 指向真实 Entry/LocalStorage，字段经 LocalStorageProp 传给实际渲染的 V2 Param，并控制包含真实 SDK UI 的条件分支。每个声明的 render 都必须完整证明，额外未声明使用会失败。源有普通 else 时目标保留对应结构。源码语义对应依赖已批准 mapping，不宣称机械证明文案、视觉、投递或设备行为等价。

原来 PASS 的行保持 PASS。原非 runtime 类检查保持原测量。逐行原生测量失败或与全量类别不等价返回 3，不用更少的 crash 计数取代原失败；仅 SDK 证明失败保留原行 FAIL 和 proof_error。原始原生测量、证明输入签名与 adapter 结果分别留证。

原 13 检测器在 pipeline 中仍真实测量，临时结果不作为 canonical verdict。事实重算后沿原历史与收敛规则生成结果；state 最后提交，替换失败恢复旧字节，未完成事务阻止两条 pipeline 路由继续。完整的测量/事务证据位于原 `native-icon-input` 证据目录。没有新增阶段、用户审批或自动回退。
