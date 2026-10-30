# 验证编号、适用性与本次范围

融合版只采用以下七项编号。旧五项结果的 schema 与编号不可直接当作本版通过证据；跨版只用稳定 key 建立对应，保留原调用与原结果。

| 稳定 key | 融合版编号 | 独立 Git 旧编号 | 本次执行原则 |
|---|---|---|---|
| compilation | CHECK-1 | 独立构建轴 | 当前 SDK 命令、配置与真实产物绑定；可复用合法同输入证据 |
| static_analysis | CHECK-2 | CHECK-1 | 源/目标结构实际错误；文字或风格命中仅提示 |
| placeholders | CHECK-3 | 无独立编号 | 按真实占位范围检查；N/A 须当前证据和理由，不能覆盖未注册占位的真 FAIL |
| app_identity | CHECK-4 | CHECK-2 | 按已确认的产品身份；未知待确认，不猜测样例包名失败 |
| page_state | CHECK-5 | 无独立编号 | 存在真实页面时适用；不依赖截图或设备权限 |
| routing | CHECK-6 | 无独立编号 | 存在导航时适用；优先静态文件证据，不能假称真实跳转已跑 |
| visual_runtime | CHECK-7 | CHECK-3 | 明确选择且具备相应授权才调用；当前禁止的 UI/设备操作仍禁用 |
| unit_tests | 独立专项 | CHECK-4 | 已选真实 UT 结果单列，不挤占其它编号 |
| behavior | 独立专项 | CHECK-5 | 真实行为用例及独立源 oracle；未跑不计通过 |

默认基础范围 1–4，报告根据真实已存在的页面/导航事实加入 5/6；`checks` 显式给出时以该子集为本次范围，按规范编号排序。示例：`{"checks":["CHECK-1","CHECK-2"],"behavior":"not_selected"}`。通过 `verify-report --scope <scope.json>` 生成报告，`verify-scope` 可只读核对选择。

每个结果可附稳定 `key`；给出时必须与编号相符。`NOT_APPLICABLE` 仅用于 3/5/6/7 的有据适用性结论，仍需当前 source/spec/target/contract 绑定、实际检查产物、exit 0 与具体理由；缺少证据是 DEFERRED。所选项无证据不能变 PASS，未选项单列 not_selected。

无论本次是否选择，当前有效且已归因的真实产品 FAIL 保留在报告并阻断对应验收；缩小检查范围不能擦除已发现缺陷。所选范围通过为 PASS_SELECTED_SCOPE，完整迁移验收保持独立。
