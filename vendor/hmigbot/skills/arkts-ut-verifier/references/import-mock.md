# import mock 配置与边界隔离

先读 [最小必要 mock 策略](mock-policy.md)。import mock 用于确需隔离且无法通过已有注入点或局部替换满足的模块边界，不因源码使用系统 kit、第三方库或 ESM import 就自动启用。

[官方 Mock 指南](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/ide-test-mock)说明：Instrument Test 和 Local Test 支持模块 mock，此配置能力适用于 **API 11 及以上的 Stage 模型工程**。本 skill 仍使用设备上的 ohosTest 流程；不能把预览器或 Local Test 的环境假设直接套入设备测试。

## 1. 配置入口与路径

开发者编辑的是模块根下 `src/mock/mock-config.json5`，mock 实现也位于 `src/mock/`。下面是配置格式示例，只有测试需求明确要求替换这些模块时才加入：

```json5
{
  "@ohos.bundle.bundleManager": {
    "source": "src/mock/ut/F001/bundle-manager.mock.ets"
  },
  "common/calc.ets": {
    "source": "src/mock/ut/F002/calc.mock.ets"
  }
}
```

- **系统模块**：核对目标 kit 成员对应的系统模块标识。例：`@kit.AbilityKit` 的 `bundleManager` 对应 `@ohos.bundle.bundleManager`；不把整个 kit 作为统一替换目标。
- **本地模块**：key 为 `ets/` 下相对路径，带文件后缀，例如 `common/calc.ets`。
- **第三方依赖模块**：核对项目实际依赖名、导出入口及构建解析结果；不拼造 `@ohos.xxx`。
- **source**：相对模块根的 mock 源文件路径；mock 的导出形状及成员签名需要兼容实际消费者。

JSON5 源配置与 HAP 内可能出现的 `mock/mock-config.json`、归一化模块标识/路径不是同一层。由构建任务转换和复制的内容，应检查实际构建产物；不能让生成 agent 直接把运行时资源路径当作源配置写入，也不能默认原始 source 值就是加载器所需路径。

## 2. 并发生成，统一合并

每个生成 agent 只写自己 Feature 的文件：

- `entry/src/mock/ut/F{编号}/<name>.mock.ets`
- `entry/src/ohosTest/mock-requests/F{编号}.json`

请求文件记录本 Feature 的全部需求；没有模块替换需求时写空数组，防止旧请求残留：

```json
{
  "feature": "F001",
  "entries": [
    {
      "target": "@ohos.bundle.bundleManager",
      "source": "src/mock/ut/F001/bundle-manager.mock.ets",
      "reason": "构造查包失败，验证真实 service 的错误处理",
      "tests": ["F001_AC01_bundle_error"],
      "realDependencies": ["FeatureService", "ResultMapper"]
    }
  ]
}
```

以上为项目内部的汇总格式，不是官方 mock-config 格式。执行 agent 在生成 barrier 后，按本轮设计与测试清单读取请求，排除过期 Feature，统一生成/合并 `entry/src/mock/mock-config.json5`：

- 同一 target、同一实现可以合并；同一 target 的不同实现先比较可否共用可重置的场景状态，否则分运行组。
- 已有用户配置必须读取并保留；冲突不采用“最后写入覆盖”。明确该配置是否影响当前用例的真实链路，必要时使用独立测试配置。
- 每组固定测试集合和模块映射。临时切换配置时保存原配置，成功或失败均恢复；记录实际构建/安装与运行组的对应关系。
- 没有模块替换需求时，不为了凑齐目录或流程生成全量系统 mock。

`MODE=register` 由 executor 负责输入质量检查、测试注册及 mock 请求核对/合并，不编译或实跑；实际运行时由同一 executor 按组切换并恢复共享配置。

## 3. Runner 接线

优先保留项目或 DevEco 生成的 runner 和 mock 初始化流程，检查构建任务是否已消费源配置、产物中是否包含 mock 实现、初始化是否早于依赖加载。官方配置指南没有要求所有工程手写同一段 onRun 代码。

若项目使用自定义 runner 且缺失初始化，按该 SDK/构建产物的实际格式接入 [AbilityDelegator.setMockList](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-inner-application-abilitydelegator#setmocklist11)。该 API 接收 `Record<string, string>`：

1. 从已确认的配置产物获得目标与替代模块路径，校验每个值是有效字符串。
2. 在被替换模块首次加载前注册映射；同时检查 runner、TestAbility 与初始化 helper 的传递依赖。
3. 如果顶层静态导入测试套会提前求值，使用注册完成后的动态 `import('../test/List.test')`。单纯移动 onRun 内的几行代码不能撤销已完成的静态导入。
4. 使用目标 SDK 支持的模块上下文和资源读取方式；不硬编码测试模块名为 `entry_test`，不猜测资源一定在 `rawfile/mock/`。
5. 用真实焦点调用、期望的边界响应以及导出兼容性检查确认接线生效。接线失败归测试基础设施错误，不通过增加 mock 或修改生产返回值掩盖。

不使用 import mock 的工程可保持静态导入。不能用吞异常后继续跑真实依赖的方式“兜底”mock 初始化失败。

## 4. 替换范围与真/mock 共存

import mock 替换的是模块加载结果，而不是仅某条 it 的调用。已注册映射会影响同一加载环境中解析该目标的消费者；测试筛选、MockKit.clear 或改场景返回值都不等于撤销模块替换。不要依赖逐用例重注册来恢复已缓存的真实模块。

模块级替换需要兼容本运行组所有消费者用到的导出。只提供一个方法的 mock，不会自动令其余导出回落到真实实现；在 mock 中重新 import 同一被替换目标也不能假定可获得真实模块。

同一依赖既要测试真实行为、又要模拟错误时，依次考虑：

1. 用已有对象/注入点局部隔离，使无需替换的真实调用保持可达。
2. 分独立构建/运行组，各自使用明确的配置和全新测试进程。只有 `-s class` 或 `-s tag` 不足以隔离模块映射；未选中的测试文件也可能已被静态加载。
3. 确认前两者均无法满足，才评估最小生产接缝；不默认拆业务模块。

报告分别列出真实运行与模块隔离的证据。同一用例因运行分组多次执行时保留每次结果，不能重复增加覆盖数或用某次 PASS 覆盖相关运行中的失败。
