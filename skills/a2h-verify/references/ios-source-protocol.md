> **当前发行边界：旧设备/视觉后端延期，官方应用测试单独取证。** `arkts-scenario-runner`、`arkts-visual-verify`、`arkts-ui-verifier`、`ios-screenshot-analyzer`（及历史 Android 截图别名）和 `scenario-builder` / `visual-fixer` / `visual-fixer-reviewer` 尚未恢复交付，不调用或要求补装这些旧后端，也不因其缺件阻断基本转换/构建/报告。指定应用/模拟器的官方截图、控件查询和固定回放按执行交界合同及实际适配入口运行，不因旧后端延期或缺少桌面屏幕权限一概记 not_run。许可、宿主可用、已实现、实际执行与验收结果分开；缺真实后端/输入仅限制对应检查。外部原始证据核对版本、配置、范围和来源，未执行不记 PASS，真实产品失败保留。下文旧调用/目录仅为兼容映射。

# iOS源验证输入

保留原四项CHECK、选择规则、修复回流和verify-report格式。源根取config.ios，源预期来自iOS源码/测试/真实观察及已批平台决策。

- CHECK-1继续原目标静态分析。
- CHECK-2源身份从Info.plist/构建变量/Asset Catalog取得；核对名称、版本和已映射图标。bundleName/vendor/签名仍由实际目标部署配置决定，不能把bundle identifier机械覆盖成签名身份。
- 历史 CHECK-3 的视觉语义在当前编号中属于 CHECK-7。旧后端延期不禁止新官方应用测试：按明确应用/设备/场景运行实际适配器，或消费可核验外部证据，核对当前版本/配置/检查点。无证据不生成视觉一致率；只有一端不记双端通过，截图不作为开始转换的前置条件。
- CHECK-4继续arkts-ut-verifier设计→生成→执行→fix-loop，先读该技能的iOS oracle协议。Hypium、双HAP、设备执行、强断言和独占写入责任不变。

源端无Mac/设备不妨碍可执行的目标检查；缺失的已选检查记DEFERRED/PARTIAL，不能自动变SKIP。未选项仍按原规则，不扩大用户范围。
源码、目标和配置版本改变使相关旧结果失效；保留原始记录，在原findings家族关闭重测后不再出现的问题。

## 结构检查的实测边界

原wiring检查能拦截孤立ViewModel和缺失页面，但仅清空事件处理器中的业务调用时可能仍PASS。结构PASS不能作为功能AC通过的证据。验收必须沿按钮事件到ViewModel副作用审查，并执行具有独立iOS真值的行为测试；没有运行环境时保持DEFERRED，不将静态检查升格为行为一致。
