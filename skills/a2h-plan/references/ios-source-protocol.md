# iOS spec 到原双计划

读取 source_platform=ios、source_anchors/source_anchors_ref 与 ios-semantics；
保持 ui-plan、indexed-v1 feature-plan、base-plan、slice、coverage-matrix、placeholder。
Stage 0 绑定 ios-resources-convert；UI 绑定 ios-ui-to-arkui；目标组件/状态/数据/导航
沿用原领域技能。保留 F-AC 和已批准差异，不能通过重新规划降低验证强度。
复杂源语义在 spec 中已解释；plan 只引用其位置、接口、唯一接线 owner 和依赖。
运行原 lint_plan_coverage，未认领/过期 digest 回流修复后再执行。
