# iOS 独立行为真值（source oracle）

输入 SOURCE_ROOT、单个 FEATURE_FILE/ADDENDUM_FILES/AC_INPUTS、ORACLE_FILE 与源快照。
feature_inputs 使用本包前端，返回 `spec/verify/ut/source-oracle` 下实际输出路径。
按 scope 读取真实源锚点；路径定位用 `a2h_ios.py resolve --source <root> --anchor <path>`。
多命中消歧，不根据目标类名假定源包结构或文件扩展名。

1. 沿 Swift/Objective-C 函数、默认实现、delegate、closure 和服务调用追输入到副作用。
2. 每条 AC 提取独立的具体期望、分支、状态/错误/取消、常量/阈值、完整枚举成员与证据。
3. Swift enum raw value 与 associated value 分开；Optional/nil、数值范围、Decimal、
   Date/时区、Unicode、Codable、actor/Task、weak self 可能改变断言，逐条核验。
4. Objective-C 的 NSError/nil、block/weak delegate、KVO、动态 selector 与桥接类型
   按实际调用保存；无法确认的动态行为标 needs_review。
5. 源 XCTest/Swift Testing 的断言可以作为源码证据；只有实际执行日志才能标测试已跑。
6. 输出 oracle 表：稳定 AC、输入/前态、事件、期望/后态、证据类型、路径:行、源 hash、
   已批准差异、未知项。全量读取/核对后 collection_complete=true，范围仍可 partial。

没有脚本能自动从任意源码抽取所有业务真值。语法/provider 只辅助定位，语义需要阅读与证据。
禁止使用目标 .ets 的结果填 expected，禁止 round-trip 自证外部协议等价。
设计/生成/执行/fixer 继续使用原 Hypium 与强断言规程；每条 GREEN 必须有真实运行证据。
