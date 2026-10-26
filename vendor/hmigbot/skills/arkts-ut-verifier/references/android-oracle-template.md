# 安卓 oracle 表模板（step0 产物 · step1/step2 消费）

> step0 使用主线程给出的准确 `FEATURE_FILE`、`ADDENDUM_FILES`、`AC_INPUTS` 和独占 `ORACLE_FILE`。主文件与关联补充节共同定位行为，已勾选 AC 不跳过。无锚点先走发现阶梯，找到事实后同样保存；安卓根缺失或整个 Feature 的差异已明确批准时返回有原因的 SKIPPED。
> step1 读取 `collection_complete: true` 且已核验适用的文件，允许复用有效证据；据 `oracle_status` 逐行区分可用预期与待复核缺口，不降低断言标准。
> 落盘在 `spec/verify/ut/android-oracle/`（`arkts-ut-fixer` 禁写区、`arkts-ut-test-executor` 只读）→ 与 fix-loop 的 `round-N/` 不同子目录，零冲突。
> 本模板**项目无关**；末尾「填写示例」用的具体类名仅为示例。

## 文件结构（机读 markdown，frontmatter + 6 节）

```markdown
---
feature: F003
feature_name: handwriting-canvas
feature_file: <实际 Spec 绝对路径>
collection_complete: false  # 每组事实增量保存；协议检查完成并回读后改为 true
oracle_status: full | partial | spec_only | spec_only(diverges)
android_source_root: <运行时实际解析到的根，记录用，非硬编码>
gate_checked: [A-anchor, C-completeness, E-algoIO]   # 已勾选(强 oracle)的闸门项，正向告诉 step1 哪些维度可信
gate_unchecked: [D-wire, ...]        # partial 时未勾选的闸门项
generated_key: <spec hash + 安卓源 hash，缓存键>
---

## §0 锚点解析表
| role | spec 写的 path | 解析到的绝对路径 | 状态 | 说明 |
|---|---|---|---|---|
| presenter | note_components/.../HandWritingNoteActivity.kt | <abs> | OK_SUFFIX | |
| repository | .../document/FDDocumentGenerateManager.kt | <abs>/note/model/... | DRIFT | basename 兜底 |
| service | .../Foo.kt | — | MISS | 不影响其它锚点 |

## §1 枚举值表（enum-value）
| 枚举名 | 成员 | 值/code | 来源 path:line | 备注 |
|---|---|---|---|---|
| FDBrushType | PEN | 0 | <abs>/FDBrushType.kt:53 | 脚本 enum 全集 |
| ...（逐成员，全集，不抽查） | | | | |

## §2 完整性清单（completeness）
| 集合名 | 全集成员（逐一） | size | spec 声称 | diff | 来源 |
|---|---|---|---|---|---|
| FDBrushType | PEN/BALLPOINT/HIGHLIGHTER/PENCIL/TAPE/PIXEL_ERASE | 6 | 6 | null | enum 全 entry |

## §3 wire/字段表（wire-tag）
| model 字段 | wire 字段名 | tag | 类型/ordinal | 权威来源(Kotlin writeTo/parseFrom) | proto 参照 | 置信 |
|---|---|---|---|---|---|---|
| force | force | 7 | float | <abs>/FDStrokePoint.kt:writeTo:LL | <abs>/X.proto:NN | full |
| ...（差异先核对实际调用链；仍无法确定的标 wire-uncertain，不能仅用 round-trip 替代） | | | | | | |

## §4 算法 I-O 表（algo-IO）
| 算法/函数 | 输入（具体值） | 期望输出（具体值） | 来源 | cross_test |
|---|---|---|---|---|
| FDTapeThicknessType.cellModel() | thickness1 | (15.0, 30.0, 10.0) | <abs>/FDBrushType.kt:LL | — |
| EraserPressure... | ... | ... | — | <abs>/EraserPressureConfigTest.kt:NN |

## §5 golden 降级清单（不可静态拿，禁臆造硬字面量）
| 项 | 为何不可静态拿 | 替代 |
|---|---|---|
| FDPenType.Steel.value | decrypt(byteArray)+资源查表，运行时解密 | golden-degraded + needs_review，未验证；**不取注释/fileKey 当真值或放宽断言** |
```

## 强制约束（每行必带，step2 与回校脚本据此审计）

- 不设时间预算。首次取得有溯源的事实即保存，后续直接更新正文；`collection_complete: false` 表示仍在采集，不供下游消费。无事实时可返回有依据的 `spec_only/SKIPPED`，不能伪造空表为成功。
- 每节每行强制带 `来源 path:line` + `category`（`enum-value|wire-tag|algo-IO|completeness|golden`）。**无来源行不许存在。**
- 完整性项记 `size + spec_claim + diff`。Kotlin/Java enum 仅使用脚本退出 0 的完整结果；sealed/其它集合须附模块范围和继承闭合证据。无法证明完整时 size 留空并列缺口，不把 UNSUPPORTED 或局部成员计数写成全集。
- 未核验 golden 项**绝不写硬字面量**；wire 不一致先核查 Android 实际调用链，仍不确定的字段保持未验证，不能以 round-trip 代替外部字段/tag 契约。
- 复用安卓 `src/test` 的行必带 `cross_test`（供 fix-loop 不误判实现缺失）。
- step2 把这些值翻成 `assertEqual(具体值)`，并在 `it()` 上方加 `// oracle: <abs>:<line> (category)`；
  step3 计 GREEN 前用 `scripts/android-oracle.sh verifyln` 回校该行号真含该值；失败时先核对行号漂移与源行为，仍无有效证据则标 `needs_review`、不计该行为已验证，禁止放宽断言。

## oracle_status 三态语义（frontmatter，step1 一眼判走向）

- `full`：闸门全勾 → step1 用具体值回填全部焦点函数。
- `partial`：有已核验且适用 oracle 的行用具体值+溯源；缺证据行标 `needs_review`、未验证，不退回猜测 Spec 或弱断言。
- `spec_only`：发现阶梯走完仍无可用事实 → 可继续 Spec 范围与 AC 盘点；没有有效复用证据或批准差异的行不能自动填预期。无锚点本身不是直接降级依据；ROOT 缺失则返回 SKIPPED，无须产文件。
- `spec_only(diverges)`：整个 Feature 均有明确批准的平台差异与对应契约，才不回填；局部差异按行记录，剩余行为仍遵循 Android。

---

## 填写示例（示例，非硬编码 —— 来自本仓 F003 实测，换项目类名即变）

```markdown
---
feature: F003
feature_name: handwriting-canvas
feature_file: <实际 Spec 绝对路径>
collection_complete: true
oracle_status: partial
gate_unchecked: [golden-encrypted-penvalue]
---
## §2 完整性清单
| 集合名 | 全集成员 | size | spec 声称 | diff | 来源 |
| FDBrushType（数据模型层） | PEN/BALLPOINT/HIGHLIGHTER/PENCIL/TAPE/PIXEL_ERASE | 6 | — | — | enum 全 entry @ notepadShared/.../FDBrushType.kt:52 |
| FDPenType（工具/UI 层，spec"N 种笔刷"指这层） | <逐个列出已核实子类型，不能用省略号代替全集> | — | "10 种笔刷" | sealed 完整性尚未证明 → needs_review | <已读源码与继承关系；待核实同模块其它子类型> |

> **⚠️ 两层枚举不可互相回填 size**：数据层 `FDBrushType`(6) 与工具层 `FDPenType`(11) 是不同概念。
> spec 的"10 种笔刷"指**工具层**；**绝不**拿数据层的 6 去断 spec 的 10。口径未对齐 → `needs_review`，不自动二选一。
## §4 算法 I-O 表
| FDTapeThicknessType.cellModel() | thickness1 | (15f,30f,10f) | FDBrushType.kt:LL | — |
## §5 golden 降级清单
| FDPenType.Steel.value | FDConst.get(decrypt(byteArray)) 运行时解密 | golden-degraded + needs_review，未验证 |
```

> 注意示例里 `diff` 那行：spec 散文说"10 种"而安卓枚举是 6 个成员（两者是工具笔种 vs 笔刷数据类型的不同概念）。
> **oracle 与 Spec 冲突先核对口径**：层级或范围未对齐时记 `diff`、标 `needs_review`，不能拿任一数硬写 size 断言。实际行为和对应层级已核实且无批准偏离时，以 Android 为准并记录 Spec 差异；明确批准的平台差异按其限定范围执行。
