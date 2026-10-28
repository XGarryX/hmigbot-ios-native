# 原生功能输入与原检查器（.36）

`check_prereq_freshness.py` 和 `check_functional_dimension.py` 的原 1.5.2 打包入口把参数字符串当列表消费。原生公共入口先解析真实参数，在一次性目录内复制真实输入，以单字符路径恢复原二进制调用；输入前后核对哈希，原退出码和诊断原样返回。`--receipt <path>` 可保存实际 argv、输入和引擎哈希及原输出。缺树、空检查和 registry 未注入仍由原核心阻断。

架构限制须如实披露：恢复的 freshness 核心实际执行默认 `pure_traditional` 规则。传 `--source` 或 `--arch` 仍记录请求架构；SwiftUI/混合的专有规则未执行，stderr/receipt 明示，不能将默认规则通过写成“已按混合规则通过”。原失败保留，尤其不填假 purpose 让树过门。

`check_dimension_prereqs.py` 是依据原 Phase 1.1.f 的可读成员探针，未经原核心差分：检查 scenario_run 和本工程 Codex visual-fixer/reviewer；缺 UNIT 返回 2，page/feature spec 双缺返回 3，部分缺失按原流程说明降级。该结果只说明成员可用，不代表视觉或功能验收。

原 `compose_registry_from_tree`、`compose_merge_into_facttree`、`fold_enum_groups` 继续执行原二进制。原生入口只在临时输入边界适配：分析键、feature_path、分组与原枚举保留；动态空文案的 `Type#component` 不再写成 tap_text。只有当前 SwiftParser 控件 ID、文件、span 和 accessibilityIdentifier 声明全部对应时，才提供 `source_native_selector`，且仍需现场确认唯一性。共享 tap 字段不承载 iOS 标识，鸿蒙侧须用自己的真实层级定位。无已证明标识则保留定位债和原分析键，不删功能项。test_intents 的期望后缀不变。

功能合并前由 `legacy_wire` 派生旧字段，完成后回到 expected_ios/ios_trusted/ios_anchor。已有原生观测按页面和原稳定键整体守护，包括 false/null；重复键或无来源的观测丢失会失败。原新算出的非空 Android oracle 不能自动升级为 iOS 真值。纯 null 静态种子仍按原 fold 折叠，核对原可逆报告与 presence/behavior 成员关系；已有实测项被改键的继承尚未接通时明确失败，不猜测继承。

实际下游入口：源设备动作走 Xcode observer/native sweep；build_batches、build_judge_input、phase2_needs、源 baseline 检查与 replay placement 走 ProjectMirror；replay compile/execute、inherit/writeback/materialize/finalize 各走既有 canonical 桥。后续实际消费者仍须执行原门控，不能由此声称全部 opaque 辅助脚本均已验证。

原 auto_install_artifacts 长参数入口的缺陷仍保留记录。原生流程可用公开 Xcode/DevEco/HDC 命令完成同一构建、签名、安装和身份核对，保存真实源码输入、HAP SHA、bundle/version、安装退出码及 observer 身份；不伪造原新鲜戳，也不使用其 skip-if-fresh 优化。迁移代码变化后重新构建并安装，再采集。

.37 功能身份使用同页唯一 feature_path，保留原允许重名的 fp_id；二者有命名空间，旧缺 path 时仅按同页双向唯一 fp_id 回退。原名称、短 ID 和分母不改，短 ID 变化只进 receipt；折叠 lineage 与删除账使用同一匹配结果。

.38 对旧 iOS 树里仍叫 android_anchor 的声明字段作输入兼容：仅 canonical ios_anchor 缺失时，按 registry 的 feature_path、hostmap、当前组件文件/行、选定 Source 文件和源哈希逐项证明，恢复 decl_file/impl_file/raw_identifier 三个静态字段，附来源记录。已有 canonical false/null 不被旧字段覆盖；旧期望、trusted 和运行时锚点附加键只记 unproved，不能升级实测真值。投影器仍只产三个原合同，merge/fold 在只读临时树中消费种子。已经丢失锚点的失败输出保留快照，恢复原 before 输入后重跑，不凭空补字段。

历史锚点核验为整批 fail-closed：任一项无法与当前源/合同/组件对应时，该批明确失败，不部分迁移后宣称完成。
