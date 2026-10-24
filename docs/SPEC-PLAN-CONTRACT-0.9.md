# 0.9.0 Spec/Plan 合同与使用

本轮优化作用于工具的 MD 规程、模板、角色和 Python 检查/派发接口。业务规格仍以 MD 为权威，结构通过不证明语义完整或运行等价。

| 层 | 规则与实际入口 |
|---|---|
| 分析与生成 | iOS 分析规程沿入口、状态、异步完成/取消、持久恢复读源；Spec 模板约束提纲和具体目标接口。页面按组件层级、布局约束、ArkUI 映射与资源引用生成。 |
| Spec 产物 | [产物目录](../skills/a2h-spec/references/artifact-contracts.md)、[catalog](../schemas/spec-plan-artifacts.json)、[JSON schema](../schemas/spec-artifacts.schema.json)与`spec-check`共同发布；固定核心表头，领域扩展另表；有据N/A和未知不能混用。 |
| 动作与复核 | [动作合同](../skills/a2h-spec/references/action-contracts.md)一处定义、精确引用；独立复核从真实入口列分母，联读定义、消费者、页面、AC与排除，原owner修复后独立重查。 |
| Plan 与施工 | [Plan合同](../skills/a2h-plan/references/plan-delivery-contract.md)约束 indexed MD→plan_items→typed task，校验AC/页面/精确写权/依赖/验证义务。共享文件的阶段工作合并到唯一owner；独立FV只读，问题回owner。 |
| 冻结与消费 | 冻结公共合同传递闭包、索引结构及工具合同版本；仅状态进度可变。worker实际读取完整受影响输入；读取预算不足分批，不能用deferred宣称完成。 |

## 项目版本与升级

新项目`harness-init`写入`ios_harness.spec_contract_version: 2`；已有harness缺字段时写1，保持原格式，不能静默升级。profile与JSON载荷版本分开，页面meta载荷仍为1、facts/coverage仍为2。

已有项目升级先保存原产物和稳定ID，按新模板补实际内容及精确引用，再把项目配置`ios_harness.spec_contract_version`显式设为2。运行Spec与源门禁、独立源复核，生成新的MD计划和typed request；已有冻结计划使用带`replan_review`的`replan`归档原控制产物再生成，不能手改三账本或继承旧成功。存在in-flight任务时先按原协议收口。未完成上述工作可继续原profile 1，但不宣称通过profile 2。已经冻结profile 2后改回1、删字段或改变工具合同摘要会被拒绝。

## 命令与派生视图

以下命令以安装后的目标工程为工作目录；源码/目标从项目配置读取。

```powershell
python .hmigbot-ios/plugin/scripts/a2h_ios.py spec-check --project .
python .hmigbot-ios/plugin/scripts/a2h_ios.py source-check --project . --harness
python .hmigbot-ios/plugin/scripts/a2h_ios.py plan-check --project . --input domains.json
python .hmigbot-ios/plugin/scripts/a2h_ios.py product-literals --project . --output spec/reports/product-literals.json
python .hmigbot-ios/plugin/scripts/a2h_ios.py spec-summary --project . --build-evidence D:/evidence/build.json
```

`plan-check`执行与`plan-ir`相同的输入门禁，不创建控制账本。派生视图默认输出到标准输出；指定`--output`只允许`spec/reports/`下，防止覆盖源合同和账本。

产品字面量视图重新核对raw提取结果、源事实图、覆盖摘要及AC；每条保留raw集合/下标和精确来源。同文案多处出现仍分条。分类为`product|preview|test|dependency|excluded|unknown`，全部先保留`usage: unresolved`，由资源owner沿实际调用确认消费。Preview分类只是精确源区间识别，不自动批准源义务排除。测试/依赖/N/A处置需当前全源摘要、精确文件hash/行范围和理由；旧无绑定处置需补证据。转换视图不修改raw、不替代strings/xcstrings资源清单、不按目录名猜范围。

证据汇总从当前AC/索引行/placeholder登记行重建计数，不信正文手填Total。历史`verified`单列展示；placeholder格式错误呈报`parse_error`。生成仅报告回执存在，真正landing仍由原调度器验收。编译需当前目标/源/规格及HAP摘要绑定；行为需实际进程观察、当前AC、规格、目标和日志绑定。旧无绑定报告为`legacy_unclassified`，输入变化为`stale`。视觉未识别到可核验协议保持`not_run`或历史未分类；本版没有新增能自动判视觉通过的协议。

编译与行为轴是已声明命令和证据的当前性检查，不能认证日志作者、设备真实性或全部源语义；独立oracle和双端设备验证继续沿原流程完成。新元数据不会为旧报告补造运行事实。

## 验收与边界

回归覆盖合法/缺失结构、N/A证据、共享动作冲突与排除、Plan映射、写权/依赖/进度、冻结降级、真实原调度、字面量混合来源和过期证据。实际模型规则对照样本另见`tests/evaluations/spec-plan-v2/`的源、生成记录与独立复核；小样本不能外推真实项目迁移成功率。

发行与安装验证入口见验证说明（本地过程记录：`VALIDATION.md`）。未在本轮完成Chunky或其他真实App的iOS/鸿蒙双端设备验收。
