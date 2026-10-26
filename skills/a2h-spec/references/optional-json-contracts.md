<!-- when: 输出API引用视图或外置状态机时读取；topics: 可选JSON、原消费者兼容、schema、引用 -->
# 按需JSON附件

先确认应用实际需要，再按随包 `schemas/spec-plan-artifacts.json` 指定的文件名及 `schemas/spec-artifacts.schema.json` 定义生成。附件不能取代主业务MD、稳定AC或原调度账本；JSON合法只代表字段形态通过，具体状态、协议及观察结果仍须独立源复核。

## 原API清单与引用视图

`spec/baseline/api-inventory.json`保留原消费者合同 `services[].auth_type` 及 `services[].endpoints[].static.http_method/path/protocol`，源平台为ios。服务/端点ID稳定，实际协议和动态部分来自源代码或独立服务契约；未确定的内容明确unknown，不拼造响应、鉴权或可用环境。公共参数/鉴权解释仍在 `api-inventory/common.md` 精确标题。

需要将端点连接到feature/合同/源锚点时，可额外生成 `spec/baseline/api-contract-links.json`；不能将以下引用视图覆盖到旧api-inventory路径，造成原Plan/网络消费者读不到services：

```json
{
  "schema_version": 1,
  "source_platform": "ios",
  "endpoints": [
    {
      "id": "API-items",
      "feature_ids": ["F001"],
      "source_anchors": [{"path": "Services/ExampleService.swift", "line": 20}],
      "contract_ref": "spec/baseline/features/F001-example.md#API 接口"
    }
  ]
}
```

引用视图的ID须已在真实inventory登记，feature和精确合同必须存在。它不拥有另一套请求/响应语义；源或主合同改变后重建/复查。无服务时不为模板生成虚构端点；有服务但证据缺失保留受阻范围。

## 外置状态机

只有复杂状态机需要独立附件时生成 `spec/baseline/features/F001-example.state-machine.json`。主feature保留全部AC和公开目标接口，以contract_refs/impl精确指针说明如何消费；附件反指主合同，不在JSON另定义业务：

```json
{
  "schema_version": 1,
  "source_platform": "ios",
  "feature_id": "F001",
  "contract_ref": "spec/baseline/features/F001-example.md#状态管理",
  "states": ["idle", "running"],
  "transitions": [
    {
      "from": "idle",
      "event": "实际源事件",
      "to": "running",
      "ac_ids": ["F001-AC01"],
      "source_anchors": [{"path": "Services/ExampleService.swift", "line": 20}]
    }
  ]
}
```

示例只给形态，状态、事件、AC和源路径必须替换真实内容。from/to必须在states中声明；每个transition绑定存在的AC和真实源锚点。错误/取消/完成先后在主MD动作合同统一，JSON状态机只能投影相同关系。

其它外置类型/状态JSON若没有本catalog的schema和真实读取者，先登记格式、条件必填、空值、源证据、冻结和校验入口，披露尚未自动校验的部分。不能把“写了JSON文件”当作已经接入工具。
