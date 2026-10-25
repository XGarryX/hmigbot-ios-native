# §M2.4 资源层符号差集

保留原四类候选和 HARD-GATE，只替换源平台输入。Source 侧使用本轮真实资源/接口/权限事实，目标侧保留实际 resources、services 和 module.json5；不能把两端同名当行为等价。

| 差集 | 源端真实输入 | 目标端对照 |
|---|---|---|
| 图片 | 实际 Image/UIImage 使用与已核对 Asset Catalog/其他资源清单，记录使用位置、变体和 scale | 目标 media 与实际代码引用；名称转换使用本轮已有映射 |
| 字符串 | 实际 strings/xcstrings、复数与语言 key | resources/*/element/string.json 与相应引用 |
| endpoint | 本轮 API inventory 中已确认的方法、路径和动态拼接来源 | 真实目标 service 请求；方法名不能代替服务端路径 |
| 权限 | 实际权限 API、Info.plist 使用说明、entitlements/能力与版本条件 | 按既有平台映射核对 module.json5、目标 API 与运行时请求 |

优先复用已经生成且出处明确的清单或转换报告，按其实际路径/字段读取。没有来源清单时通过选定 Source 与实际资源解析补取，不能创建虚构中间文件再声称已运行扫描；缺少解析器或材料按原 SKIPPED(原因) 披露。源端代码定点取证可复用 [Source 查询](../../arkts-network-troubleshoot/references/native-source-search.md)，其关键词命中仍只是候选。

## HARD-GATE（原语义）

- 每个实际差集操作的命令/程序与 stdout 原文以 code fence 记录；明确实际输入清单和字段。
- 实际返回空时写“空结果”；不得把未执行、失败或缺材料记为空差集。
- 解析/命令报错或工具能力缺失时写 SKIPPED(原因)，不伪造成功。
- 差集不等于一定要迁：废弃资源、映射后改名、动态 URL 等均须按实际上下文判断，再进入原 §S2 用户对齐。
