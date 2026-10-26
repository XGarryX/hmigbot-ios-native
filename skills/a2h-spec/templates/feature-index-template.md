<!-- when: 生成feature-index或更新范围结构时加载；topics: 功能边界、依赖、页面创建、格式版本 -->
# feature-index.md 模板

新生成使用spec_contract_version=2，机器核心章节/表头见随包 `schemas/spec-plan-artifacts.json`。下列示例用于格式，不给项目添加示例业务。保留稳定F/page/AC ID；范围排除保留原ID及依据。

```markdown
# Feature Index

spec_contract_version: 2

## 领域模型概览
列实际核心实体、身份与关系；完整字段在feature-base精确标题定义，本节链接该合同。不得由实体数量推导功能完备。

## 功能清单
| ID | 功能 | 优先级 | 排序依赖 | 契约依赖 | 关联页面 | 创建页面 | complexity | tier | depth | 状态 | spec |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F001 | 实际完整能力名称 | P0 | base | spec/baseline/feature-base.md#数据模型 | page_0001 | page_0001 | simple | core | full | pending | spec/baseline/features/F001-example.md |

## 依赖图
base → F001

## 执行顺序（拓扑排序）
1. feature-base
2. F001
```

字段语义：

- `排序依赖`：真实先后约束，使用base、F-ID；无依赖写none。图和拓扑序必须与此一致，不能以双向业务关联制造循环。
- `契约依赖`：功能消费的稳定接口/共享合同精确路径和标题；消费已确定接口不自动成为施工串行依赖。若确实需要provider先完成，在排序依赖另列。
- `关联页面`：由manifest登记的page ID，可被多功能消费；`创建页面`只有唯一创建责任，无创建写none。创建不意味着独占全部服务接线。
- `complexity`：simple/complex；`tier`：core/standard/peripheral；`depth`：full/stub。stub只保留分析缺口，不可作为完整实施输入。
- `spec`：存在的项目相对主feature路径；优先级P0/P1/P2。主feature元数据与本表必须一致。

状态列沿原写者纪律：Spec只初始化pending/有据skipped；execute经原writeback回写implemented；后续验证按其实际证据更新。旧verified仅是兼容进度，不自动解释为行为或视觉通过；交接摘要分别给生成、编译、结构、行为、视觉证据。

只允许进度字段由授权写者更新。依赖、范围、页面归属、合同指针、complexity/tier/depth及spec路径属于计划输入；更改须复核并显式重排，不能因为索引带进度列而豁免整文件。

功能拆分按用户可感知完整能力和真实系统行为，不按class/file。API聚类可提示遗漏，但不能凭路径前缀直接产生功能、业务或验收标准。
