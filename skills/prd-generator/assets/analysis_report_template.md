# PRD 分析报告模板

此模板用于生成基于终端V2.1模板的PRD分析报告。

---

```markdown
# PRD 需求分析报告

**生成时间**: {{GENERATION_TIME}}
**分析工具**: CBG PRD Generator v1.0
**分析模板**: 终端V2.1

---

## 1. 文档信息

| 项目 | 内容 |
|------|------|
| PRD文件 | {{PRD_FILE_NAME}} |
| 文档路径 | {{PRD_FILE_PATH}} |
| 版本号 | {{PRD_VERSION}} |
| 创建日期 | {{PRD_DATE}} |
| 最后更新 | {{PRD_LAST_UPDATE}} |
| 文档状态 | {{PRD_STATUS}} |
| 文档作者 | {{PRD_AUTHOR}} |

---

## 2. 需求概述

### 2.1 基本信息

| 项目 | 内容 |
|------|------|
| 需求来源 | {{REQUIREMENT_SOURCE}} |
| 需求分类 | {{REQUIREMENT_CATEGORY}} |
| 需求背景 | {{REQUIREMENT_BACKGROUND}} |
| 业务定位 | {{BUSINESS_POSITIONING}} |

### 2.2 需求价值分析

| 价值维度 | 描述 |
|----------|------|
| KPI提升 | {{KPI_IMPROVEMENT}} |
| 用户体验改善 | {{UX_IMPROVEMENT}} |
| 运营工作量减少 | {{OPERATION_WORKLOAD}} |

### 2.3 需求适用范围

**产品品类覆盖**：
{{PRODUCT_CATEGORY_COVERAGE}}

**发布范围**：
{{RELEASE_REGION_COVERAGE}}

---

## 3. KEP/KEI分析

### 3.1 KEP清单

| 场景编号 | 场景名称 | 场景类型 | 涉及Actor | 优先级 | 状态 |
|----------|----------|----------|-----------|--------|------|
{{KEP_TABLE_ROWS}}
| ... | ... | ... | ... | ... | ... |

### 3.2 KEI清单

| 评估体系 | 维度 | 评估类型 | 是否必选 | 评估标准 |
|----------|------|----------|----------|----------|
{{KEI_TABLE_ROWS}}
| ... | ... | ... | ... | ... |

### 3.3 KEP/KEI完整性验证

| 检查项 | 结果 | 详情 |
|--------|------|------|
| KEP数量 | {{KEP_COUNT_RESULT}} | {{KEP_COUNT_DETAIL}} |
| 场景覆盖 | {{SCENARIO_COVERAGE_RESULT}} | {{SCENARIO_COVERAGE_DETAIL}} |
| KEI可测性 | {{KEI_MEASURABILITY_RESULT}} | {{KEI_MEASURABILITY_DETAIL}} |
| 映射完整性 | {{MAPPING_INTEGRITY_RESULT}} | {{MAPPING_INTEGRITY_DETAIL}} |

---

## 4. 完整性检查

### 4.1 章节完整性

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 文档信息 | {{DOC_INFO_STATUS}} | {{DOC_INFO_DETAIL}} |
| 文档变更记录 | {{CHANGE_RECORD_STATUS}} | {{CHANGE_RECORD_DETAIL}} |
| 需求来源 | {{REQUIREMENT_SOURCE_STATUS}} | {{REQUIREMENT_SOURCE_DETAIL}} |
| 需求背景及业务定位 | {{REQUIREMENT_BACKGROUND_STATUS}} | {{REQUIREMENT_BACKGROUND_DETAIL}} |
| 需求价值分析 | {{REQUIREMENT_VALUE_STATUS}} | {{REQUIREMENT_VALUE_DETAIL}} |
| 需求适用范围分析 | {{REQUIREMENT_SCOPE_STATUS}} | {{REQUIREMENT_SCOPE_DETAIL}} |
| 目标用户分析 | {{TARGET_USER_STATUS}} | {{TARGET_USER_DETAIL}} |
| 竞品分析 | {{COMPETITIVE_ANALYSIS_STATUS}} | {{COMPETITIVE_ANALYSIS_DETAIL}} |
| 需求描述 | {{REQUIREMENT_DESC_STATUS}} | {{REQUIREMENT_DESC_DETAIL}} |
| KEP/KEI | {{KEP_KEI_STATUS}} | {{KEP_KEI_DETAIL}} |
| 公共需求/能力交互影响分析 | {{PUBLIC_REQUIREMENTS_STATUS}} | {{PUBLIC_REQUIREMENTS_DETAIL}} |
| 运营策略 | {{OPERATION_STRATEGY_STATUS}} | {{OPERATION_STRATEGY_DETAIL}} |
| 非功能需求 | {{NON_FUNCTIONAL_STATUS}} | {{NON_FUNCTIONAL_DETAIL}} |
| 附录 | {{APPENDIX_STATUS}} | {{APPENDIX_DETAIL}} |
| 审批记录 | {{APPROVAL_RECORD_STATUS}} | {{APPROVAL_RECORD_DETAIL}} |

### 4.2 完整性评分

**总分**: {{COMPLETENESS_SCORE}} / 30

**评级**: {{COMPLETENESS_LEVEL}}

```
{{COMPLETENESS_BAR_GRAPH}}
```

### 4.3 缺失项汇总

{{MISSING_ITEMS_LIST}}

---

## 5. 公共需求/能力交互影响分析

### 5.1 整体分析

| 公共需求/能力分类 | 名称 | 是否涉及 | 须遵从的规则和要求 | 涉及或不涉及的理由 |
|---|---|---|---|---|
{{PUBLIC_REQUIREMENTS_TABLE_ROWS}}
| ... | ... | ... | ... | ... |

### 5.2 涉及的公共需求汇总

{{INVOLVED_PUBLIC_REQUIREMENTS_SUMMARY}}

### 5.3 合规性检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 国际化合规 | {{I18N_COMPLIANCE}} | {{I18N_COMPLIANCE_DETAIL}} |
| 安全隐私合规 | {{SECURITY_PRIVACY_COMPLIANCE}} | {{SECURITY_PRIVACY_COMPLIANCE_DETAIL}} |
| 无障碍支持 | {{ACCESSIBILITY_SUPPORT}} | {{ACCESSIBILITY_SUPPORT_DETAIL}} |
| 适老化支持 | {{ELDERLY_SUPPORT}} | {{ELDERLY_SUPPORT_DETAIL}} |

---

## 6. 冲突检测

### 6.1 冲突汇总

{{#if CONFLICTS_FOUND}}
| 冲突类型 | 严重程度 | 描述 | 建议 |
|----------|----------|------|------|
{{CONFLICT_TABLE_ROWS}}
| ... | ... | ... | ... |
{{else}}
✅ 未发现明显需求冲突
{{/if}}

### 6.2 详细说明

{{CONFLICT_DETAILS}}

---

## 7. 运营策略分析

### 7.1 运营目标

| 产品/特性/需求名称 | 用户触点 | 运营目标 | 运营策略 |
|:---|:---|:---|:---|
{{OPERATION_STRATEGY_TABLE_ROWS}}
| ... | ... | ... | ... |

### 7.2 运营策略评估

| 评估项 | 结果 | 说明 |
|--------|------|------|
| 端内运营策略 | {{END_TO_END_STRATEGY}} | {{END_TO_END_STRATEGY_DETAIL}} |
| 门店体验及演示 | {{STORE_EXPERIENCE}} | {{STORE_EXPERIENCE_DETAIL}} |
| 北极星指标定义 | {{NORTH_STAR_METRIC}} | {{NORTH_STAR_METRIC_DETAIL}} |

---

## 8. 非功能需求评估

### 8.1 性能要求

| 指标 | 要求 | 备注 |
|------|------|------|
{{PERFORMANCE_REQUIREMENTS_ROWS}}

### 8.2 安全要求

{{SECURITY_REQUIREMENTS_SUMMARY}}

### 8.3 兼容性要求

| 平台 | 版本要求 | 备注 |
|------|----------|------|
{{COMPATIBILITY_REQUIREMENTS_ROWS}}

---

## 9. 改进建议

### 9.1 PRD文档改进

{{PRD_IMPROVEMENT_SUGGESTIONS}}

### 9.2 需求澄清

{{CLARIFICATION_NEEDED}}

### 9.3 公共需求补充建议

{{PUBLIC_REQUIREMENTS_SUGGESTIONS}}

---

## 10. 附录

### 10.1 完整需求列表

{{FULL_REQUIREMENT_LIST}}

### 10.2 术语表

| 术语 | 定义 |
|------|------|
{{GLOSSARY_ROWS}}

### 10.3 参考资料

- PRD文档: {{PRD_FILE_PATH}}
- PRD模板: 终端V2.1
- 相关规范: {{RELATED_STANDARDS}}

---

**报告结束**

*本报告由 CBG PRD Generator 自动生成*
```

---

## 模板变量参考

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{GENERATION_TIME}}` | 报告生成时间戳 | 2026-02-10 20:00:00 |
| `{{PRD_FILE_NAME}}` | PRD 文件名 | prd_v21.md |
| `{{PRD_VERSION}}` | PRD 版本号 | V2.1 |
| `{{REQUIREMENT_SOURCE}}` | 需求来源 | 运营需求 |
| `{{KEP_COUNT_RESULT}}` | KEP数量检查结果 | ✅ 符合要求 |
| `{{COMPLETENESS_SCORE}}` | 完整性评分 | 25/30 |
| `{{COMPLETENESS_LEVEL}}` | 完整性等级 | 良好 |