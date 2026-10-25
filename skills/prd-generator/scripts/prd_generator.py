#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD Generator Tool

基于终端V2.1模板生成产品需求文档(PRD)

Usage:
    python prd_generator.py generate <config_file> [options]
    python prd_generator.py analyze <prd_file> [options]
    python prd_generator.py validate <prd_file> [options]

Options:
    --output <file>     输出文件路径
    --format <format>   输出格式 (markdown|json|yaml)
    --check-completeness    检查完整性
    --check-public-req  检查公共需求
    --extract-kep       提取KEP列表
    --extract-kei       提取KEI列表
"""

import argparse
import json
import re
import sys
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple


@dataclass
class KEP:
    """关键体验路径 (Key Experience Path)"""
    phase: str
    scenario_type: str
    actor: str
    kep_description: str
    scenario_name: str
    scenario_number: str
    use_case_name: str
    use_case_number: str
    ir_requirement_number: str


@dataclass
class KEI:
    """关键体验指标 (Key Experience Indicator)"""
    evaluation_system: str
    dimension: str
    evaluation_type: str
    is_required: str
    evaluation_standard: str
    ir_requirement_number: str
    function_name: str
    function_code: str


@dataclass
class PublicRequirement:
    """公共需求"""
    category: str
    name: str
    involved: str
    rules: str
    reason: str


@dataclass
class PRDMetadata:
    """PRD文档元数据"""
    document_name: str
    version: str
    create_date: str
    last_update: str
    document_status: str


@dataclass
class RequirementSource:
    """需求来源"""
    department: str
    contact: str
    requirement_type: str  # 运营需求、优化需求、用户反馈需求、规划需求


@dataclass
class RequirementBackground:
    """需求背景及业务定位"""
    original_request: str
    problem_to_solve: str
    expected_outcome: str


@dataclass
class RequirementValue:
    """需求价值分析"""
    kpi_improvement: str
    user_experience_improvement: str
    operation_workload_reduction: str


@dataclass
class ProductScope:
    """需求适用范围分析"""
    product_categories: List[Dict[str, str]]
    release_regions: List[Dict[str, str]]


@dataclass
class UserAnalysis:
    """目标用户分析"""
    user_id: str
    user_type: str
    basic_info: str
    usage_experience: str
    motivation: str
    needs_and_pain_points: str
    user_voice: str


@dataclass
class CompetitorAnalysis:
    """竞品分析"""
    scenario: str
    hw_capability: str
    competitor1: str
    competitor2: str
    comparison_analysis: str


@dataclass
class NonFunctionalRequirements:
    """非功能需求"""
    performance: List[Dict[str, str]]
    security: str
    compatibility: List[Dict[str, str]]


@dataclass
class PRDConfig:
    """PRD配置"""
    metadata: PRDMetadata
    requirement_source: RequirementSource
    requirement_background: RequirementBackground
    requirement_value: RequirementValue
    product_scope: ProductScope
    user_analysis: List[UserAnalysis]
    competitor_analysis: List[CompetitorAnalysis]
    public_requirements: List[PublicRequirement]
    non_functional_requirements: NonFunctionalRequirements
    keps: List[KEP] = field(default_factory=list)
    keis: List[KEI] = field(default_factory=list)


class PRDGenerator:
    """PRD生成器"""

    def __init__(self, template_path: Optional[Path] = None):
        self.template_path = template_path or Path(__file__).parent.parent / "assets" / "prd_template.md"
        self.template_content = ""
        if self.template_path.exists():
            self.template_content = self.template_path.read_text(encoding='utf-8')

    def load_config(self, config_file: str) -> PRDConfig:
        """加载配置文件"""
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")

        # 根据文件扩展名选择解析方式
        if config_path.suffix == '.json':
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        elif config_path.suffix in ['.yaml', '.yml']:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        else:
            raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")

        return self._parse_config(config_data)

    def _parse_config(self, config_data: Dict[str, Any]) -> PRDConfig:
        """解析配置数据为PRDConfig对象"""
        metadata = PRDMetadata(**config_data.get('metadata', {}))
        requirement_source = RequirementSource(**config_data.get('requirement_source', {}))
        requirement_background = RequirementBackground(**config_data.get('requirement_background', {}))
        requirement_value = RequirementValue(**config_data.get('requirement_value', {}))
        
        product_scope_data = config_data.get('product_scope', {})
        product_scope = ProductScope(
            product_categories=product_scope_data.get('product_categories', []),
            release_regions=product_scope_data.get('release_regions', [])
        )
        
        user_analysis_data = config_data.get('user_analysis', [])
        user_analysis = [UserAnalysis(**ua) for ua in user_analysis_data]
        
        competitor_analysis_data = config_data.get('competitor_analysis', [])
        competitor_analysis = [CompetitorAnalysis(**ca) for ca in competitor_analysis_data]
        
        public_requirements_data = config_data.get('public_requirements', [])
        public_requirements = [PublicRequirement(**pr) for pr in public_requirements_data]
        
        non_functional_data = config_data.get('non_functional_requirements', {})
        non_functional_requirements = NonFunctionalRequirements(**non_functional_data)
        
        keps_data = config_data.get('keps', [])
        keps = [KEP(**k) for k in keps_data]
        
        keis_data = config_data.get('keis', [])
        keis = [KEI(**k) for k in keis_data]

        return PRDConfig(
            metadata=metadata,
            requirement_source=requirement_source,
            requirement_background=requirement_background,
            requirement_value=requirement_value,
            product_scope=product_scope,
            user_analysis=user_analysis,
            competitor_analysis=competitor_analysis,
            public_requirements=public_requirements,
            non_functional_requirements=non_functional_requirements,
            keps=keps,
            keis=keis
        )

    def generate(self, config: PRDConfig, output_format: str = "markdown") -> str:
        """生成PRD文档"""
        if output_format == "markdown":
            return self._generate_markdown(config)
        elif output_format == "json":
            return self._generate_json(config)
        elif output_format == "yaml":
            return self._generate_yaml(config)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

    def _generate_markdown(self, config: PRDConfig) -> str:
        """生成Markdown格式PRD"""
        lines = []
        
        # 文档标题
        lines.append(f"# {config.metadata.document_name}")
        lines.append("")
        
        # 文档信息
        lines.append("## 文档信息")
        lines.append("")
        lines.append("| 项目 | 内容 |")
        lines.append("|------|------|")
        lines.append(f"| 文档名称 | {config.metadata.document_name} |")
        lines.append(f"| 版本号 | {config.metadata.version} |")
        lines.append(f"| 创建日期 | {config.metadata.create_date} |")
        lines.append(f"| 最后更新 | {config.metadata.last_update} |")
        lines.append(f"| 文档状态 | {config.metadata.document_status} |")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 变更记录
        lines.append("## 1. 文档变更记录")
        lines.append("")
        lines.append("| 版本 | 日期 | 修改人 | 修改内容 | 备注 |")
        lines.append("|------|------|--------|----------|------|")
        lines.append(f"| {config.metadata.version} | {config.metadata.create_date} | [姓名] | [修改描述] | [备注] |")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 产品需求
        lines.append("## 2. 产品需求")
        lines.append("")
        
        # 2.1 需求来源
        lines.append("### 2.1 需求来源")
        lines.append("")
        lines.append(f"- **需求提出部门**: {config.requirement_source.department}")
        lines.append(f"- **接口人**: {config.requirement_source.contact}")
        lines.append(f"- **需求分类**: {config.requirement_source.requirement_type}")
        lines.append("")
        
        # 2.2 需求背景及业务定位
        lines.append("### 2.2 需求背景及业务定位")
        lines.append("")
        lines.append(f"**原始诉求**: {config.requirement_background.original_request}")
        lines.append("")
        lines.append(f"**需要解决的问题**: {config.requirement_background.problem_to_solve}")
        lines.append("")
        lines.append(f"**期望达到的诉求**: {config.requirement_background.expected_outcome}")
        lines.append("")
        
        # 2.3 需求价值分析
        lines.append("### 2.3 需求价值分析")
        lines.append("")
        if config.requirement_value.kpi_improvement:
            lines.append(f"**KPI提升**: {config.requirement_value.kpi_improvement}")
        if config.requirement_value.user_experience_improvement:
            lines.append(f"**用户体验改善**: {config.requirement_value.user_experience_improvement}")
        if config.requirement_value.operation_workload_reduction:
            lines.append(f"**减少运营工作量**: {config.requirement_value.operation_workload_reduction}")
        lines.append("")
        
        # 2.4 需求适用范围分析
        lines.append("### 2.4 需求适用范围分析")
        lines.append("")
        
        if config.product_scope.product_categories:
            lines.append("**产品品类**: ")
            lines.append("| 需求分类 | 名称 | 是否涉及 | 备注说明 |")
            lines.append("| :--- | :--- | :--- | :--- |")
            lines.append("| **产品品类** | | | |")
            for category in config.product_scope.product_categories:
                lines.append(f"| | {category.get('name', '')} | {category.get('involved', '')} | {category.get('remark', '')} |")
            lines.append("")
        
        if config.product_scope.release_regions:
            lines.append("**发布范围**: ")
            lines.append("| 需求分类 | 名称 | 是否涉及 | 备注说明 |")
            lines.append("| :--- | :--- | :--- | :--- |")
            lines.append("| **发布范围** | | | |")
            for region in config.product_scope.release_regions:
                lines.append(f"| | {region.get('name', '')} | {region.get('involved', '')} | {region.get('remark', '')} |")
            lines.append("")
        
        # 2.5 目标用户分析
        if config.user_analysis:
            lines.append("### 2.5 目标用户分析")
            lines.append("")
            for i, user in enumerate(config.user_analysis, 1):
                lines.append(f"**主要目标用户{i}**: {user.user_type}")
                lines.append("")
                lines.append("| 分类 | 信息 |")
                lines.append("| :--- | :--- |")
                lines.append(f"| **用户基本信息** | {user.basic_info} |")
                lines.append(f"| **产品/服务使用情况及使用经验** | {user.usage_experience} |")
                lines.append(f"| **动机与关注点** | {user.motivation} |")
                lines.append(f"| **需求及痛点** | {user.needs_and_pain_points} |")
                lines.append(f"| **用户原声** | {user.user_voice} |")
                lines.append("")
        
        # 2.6 竞品分析
        if config.competitor_analysis:
            lines.append("### 2.6 竞品分析")
            lines.append("")
            lines.append("| 序号 | 典型场景/规格 | HW | 竞品1 | 竞品2 | 对比分析 |")
            lines.append("|---|---|---|---|---|---|")
            for i, competitor in enumerate(config.competitor_analysis, 1):
                lines.append(f"| {i} | {competitor.scenario} | {competitor.hw_capability} | {competitor.competitor1} | {competitor.competitor2} | {competitor.comparison_analysis} |")
            lines.append("")
            lines.append("**优劣势总结**: [请补充]")
            lines.append("")
            lines.append("**竞争力构建计划**: [请补充]")
            lines.append("")
        
        # 2.7 需求描述
        lines.append("### 2.7 需求描述")
        lines.append("")
        lines.append("#### 2.7.1 需求参与者（角色）")
        lines.append("")
        lines.append("- 最终用户")
        lines.append("")
        
        lines.append("#### 2.7.2 前置条件")
        lines.append("")
        lines.append("- [请填写设备要求]")
        lines.append("- [请填写系统版本要求]")
        lines.append("")
        
        lines.append("#### 2.7.3 业务流程")
        lines.append("")
        lines.append("- **正常业务流程**: [请描述]")
        lines.append("- **异常业务流程**: [请描述]")
        lines.append("")
        
        lines.append("#### 2.7.4 业务功能描述")
        lines.append("")
        lines.append("| 标题 | IR需求编号 | 描述 | 功能名称 | 功能编码 | 备注 |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        lines.append("| [功能1] | [编号] | [描述] | | | 界面示意图（UI 低保真） |")
        lines.append("| [功能2] | [编号] | [描述] | | | |")
        lines.append("")
        
        # 1.7.5 关键体验路径 (KEP)
        if config.keps:
            lines.append("#### 2.7.5 关键体验路径（KEP）")
            lines.append("")
            lines.append("| 阶段 | 场景类型 | 涉及Actor | KEP描述 | 场景名称 | 场景编号 | 用例名称 | 用例编号 | IR需求编号 |")
            lines.append("|---|---|---|---|---|---|---|---|---|")
            for kep in config.keps:
                lines.append(f"| {kep.phase} | {kep.scenario_type} | {kep.actor} | {kep.kep_description} | {kep.scenario_name} | {kep.scenario_number} | {kep.use_case_name} | {kep.use_case_number} | {kep.ir_requirement_number} |")
            lines.append("")
        
        # 1.7.6 关键体验指标 (KEI)
        if config.keis:
            lines.append("#### 2.7.6 关键体验指标（KEI）")
            lines.append("")
            lines.append("| 评估体系 | 维度 | 评估类型 | 是否必选 | 评估标准 | IR需求编号 | 功能名称 | 功能编码 |")
            lines.append("|---|---|---|---|---|---|---|---|")
            for kei in config.keis:
                lines.append(f"| {kei.evaluation_system} | {kei.dimension} | {kei.evaluation_type} | {kei.is_required} | {kei.evaluation_standard} | {kei.ir_requirement_number} | {kei.function_name} | {kei.function_code} |")
            lines.append("")
        
        # 1.7.7 公共需求/能力交互影响分析
        if config.public_requirements:
            lines.append("#### 2.7.7 公共需求/能力交互影响分析")
            lines.append("")
            lines.append("## 1）整体分析（必选）")
            lines.append("")
            lines.append("| 公共需求/能力分类 | 名称 | 是否涉及 | 须遵从的规则和要求 | 涉及或不涉及的理由 |")
            lines.append("|---|---|---|---|---|")
            for pr in config.public_requirements:
                # 处理rules中的换行
                rules_formatted = pr.rules.replace('
', '<br>')
                lines.append(f"| {pr.category} | {pr.name} | {pr.involved} | {rules_formatted} | {pr.reason} |")
            lines.append("")
        else:
            lines.append("#### 2.7.7 公共需求/能力交互影响分析")
            lines.append("")
            lines.append("> 请根据实际需求填写公共需求/能力交互影响分析")
            lines.append("")
        
        # 4. 非功能需求
        lines.append("## 4. 非功能需求")
        lines.append("")
        
        # 4.1 性能要求
        lines.append("### 4.1 性能要求")
        lines.append("")
        lines.append("| 指标 | 要求 | 备注 |")
        lines.append("|------|------|------|")
        if config.non_functional_requirements.performance:
            for perf in config.non_functional_requirements.performance:
                lines.append(f"| {perf.get('metric', '')} | {perf.get('requirement', '')} | {perf.get('remark', '')} |")
        else:
            lines.append("| 响应时间 | [具体数值] | [说明] |")
            lines.append("| 并发用户数 | [具体数值] | [说明] |")
        lines.append("")
        
        # 4.2 安全要求
        lines.append("### 4.2 安全要求")
        lines.append("")
        if config.non_functional_requirements.security:
            lines.append(config.non_functional_requirements.security)
        else:
            lines.append("[请列出安全相关的需求，如数据加密、权限控制等]")
        lines.append("")
        
        # 4.3 兼容性要求
        lines.append("### 4.3 兼容性要求")
        lines.append("")
        lines.append("| 平台 | 版本要求 | 备注 |")
        lines.append("|------|----------|------|")
        if config.non_functional_requirements.compatibility:
            for compat in config.non_functional_requirements.compatibility:
                lines.append(f"| {compat.get('platform', '')} | {compat.get('version', '')} | {compat.get('remark', '')} |")
        else:
            lines.append("| [平台1] | [版本] | [说明] |")
            lines.append("| [平台2] | [版本] | [说明] |")
        lines.append("")
        
        # 12. 附录
        lines.append("## 12. 附录")
        lines.append("")
        
        lines.append("### 12.1 术语表")
        lines.append("")
        lines.append("| 术语 | 定义 |")
        lines.append("|------|------|")
        lines.append("| [术语1] | [定义] |")
        lines.append("| [术语2] | [定义] |")
        lines.append("")
        
        lines.append("### 12.2 参考资料")
        lines.append("")
        lines.append("- [文档1]")
        lines.append("- [文档2]")
        lines.append("")
        
        lines.append("### 12.3 相关文档")
        lines.append("")
        lines.append("- [文档名称]")
        lines.append("- [文档名称]")
        lines.append("")
        lines.append("---")
        
        # 13. 审批记录
        lines.append("## 13. 审批记录")
        lines.append("")
        lines.append("| 角色 | 姓名 | 日期 | 签名 |")
        lines.append("|------|------|------|------|")
        lines.append("| 产品经理 | [姓名] | [日期] | [签名] |")
        lines.append("| 技术负责人 | [姓名] | [日期] | [签名] |")
        lines.append("| 测试负责人 | [姓名] | [日期] | [签名] |")
        lines.append("| 项目经理 | [姓名] | [日期] | [签名] |")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("**文档结束**")
        
        return "
".join(lines)

    def _generate_json(self, config: PRDConfig) -> str:
        """生成JSON格式PRD"""
        data = asdict(config)
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _generate_yaml(self, config: PRDConfig) -> str:
        """生成YAML格式PRD"""
        data = asdict(config)
        return yaml.dump(data, allow_unicode=True, default_flow_style=False)


class PRDAnalyzer:
    """PRD分析器"""

    def __init__(self, prd_file: str):
        self.prd_file = Path(prd_file)
        self.content = ""
        self.issues: List[str] = []
        self.warnings: List[str] = []

    def load(self) -> bool:
        """加载PRD文件"""
        if not self.prd_file.exists():
            self.issues.append(f"PRD文件不存在: {self.prd_file}")
            return False

        try:
            self.content = self.prd_file.read_text(encoding='utf-8')
            return True
        except Exception as e:
            self.issues.append(f"读取PRD文件失败: {e}")
            return False

    def extract_keps(self) -> List[Dict]:
        """提取KEP列表"""
        keps = []
        
        # 查找KEP表格
        kep_table_pattern = r'\|\s*阶段\s*\|\s*场景类型\s*\|\s*涉及Actor\s*\|\s*KEP描述.*?
((?:\|.*?\|\s*
)+)'
        kep_match = re.search(kep_table_pattern, self.content, re.MULTILINE | re.DOTALL)
        
        if kep_match:
            table_content = kep_match.group(1)
            rows = [line.strip() for line in table_content.split('
') if line.strip() and line.startswith('|')]
            
            for row in rows[1:]:  # 跳过表头
                cells = [cell.strip() for cell in row.split('|')[1:-1]]  # 移除首尾的空单元格
                if len(cells) >= 9:
                    keps.append({
                        'phase': cells[0],
                        'scenario_type': cells[1],
                        'actor': cells[2],
                        'kep_description': cells[3],
                        'scenario_name': cells[4],
                        'scenario_number': cells[5],
                        'use_case_name': cells[6],
                        'use_case_number': cells[7],
                        'ir_requirement_number': cells[8]
                    })
        
        return keps

    def extract_keis(self) -> List[Dict]:
        """提取KEI列表"""
        keis = []
        
        # 查找KEI表格
        kei_table_pattern = r'\|\s*评估体系\s*\|\s*维度\s*\|\s*评估类型.*?
((?:\|.*?\|\s*
)+)'
        kei_match = re.search(kei_table_pattern, self.content, re.MULTILINE | re.DOTALL)
        
        if kei_match:
            table_content = kei_match.group(1)
            rows = [line.strip() for line in table_content.split('
') if line.strip() and line.startswith('|')]
            
            for row in rows[1:]:  # 跳过表头
                cells = [cell.strip() for cell in row.split('|')[1:-1]]
                if len(cells) >= 8:
                    keis.append({
                        'evaluation_system': cells[0],
                        'dimension': cells[1],
                        'evaluation_type': cells[2],
                        'is_required': cells[3],
                        'evaluation_standard': cells[4],
                        'ir_requirement_number': cells[5],
                        'function_name': cells[6],
                        'function_code': cells[7]
                    })
        
        return keis

    def check_completeness(self) -> Dict:
        """检查PRD完整性"""
        required_sections = [
            "文档信息",
            "文档变更记录",
            "产品需求",
            "需求来源",
            "需求背景及业务定位",
            "需求价值分析",
            "需求适用范围分析",
            "需求描述",
            "业务流程",
            "业务功能描述",
            "关键体验路径",
            "关键体验指标",
            "公共需求",
            "非功能需求",
            "性能要求",
            "安全要求",
            "兼容性要求",
            "附录",
            "审批记录"
        ]
        
        missing_sections = []
        present_sections = []
        
        for section in required_sections:
            if section in self.content:
                present_sections.append(section)
            else:
                missing_sections.append(section)
        
        return {
            'total_sections': len(required_sections),
            'present_sections': present_sections,
            'missing_sections': missing_sections,
            'completeness_score': len(present_sections) / len(required_sections) * 100
        }

    def check_public_requirements(self) -> Dict:
        """检查公共需求"""
        public_items = [
            "国际化", "安全隐私", "无障碍", "适老化", "退账号",
            "注销账号", "OOBE", "克隆备份", "旋转屏", "分屏",
            "外屏适配", "自由多窗", "双升单", "三方应用关联启动管理",
            "单回退双", "小艺问答操控", "统一交互"
        ]
        
        analysis_result = {}
        
        for item in public_items:
            if item in self.content:
                # 检查是否填写了是否涉及列
                pattern = rf'{item}.*?涉及/(?:不)?涉及'
                match = re.search(pattern, self.content, re.MULTILINE | re.DOTALL)
                if match:
                    analysis_result[item] = {
                        'found': True,
                        'analyzed': True,
                        'status': 'completed'
                    }
                else:
                    analysis_result[item] = {
                        'found': True,
                        'analyzed': False,
                        'status': 'incomplete'
                    }
            else:
                analysis_result[item] = {
                    'found': False,
                    'analyzed': False,
                    'status': 'missing'
                }
        
        return analysis_result

    def generate_analysis_report(self, format: str = "markdown") -> str:
        """生成分析报告"""
        keps = self.extract_keps()
        keis = self.extract_keis()
        completeness = self.check_completeness()
        public_reqs = self.check_public_requirements()
        
        if format == "json":
            return json.dumps({
                'prd_file': str(self.prd_file),
                'keps': keps,
                'keis': keis,
                'completeness': completeness,
                'public_requirements': public_reqs
            }, ensure_ascii=False, indent=2)
        
        # Markdown格式
        lines = []
        lines.append("# PRD分析报告")
        lines.append("")
        lines.append(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**PRD文件**: {self.prd_file.name}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 完整性检查
        lines.append("## 1. 完整性检查")
        lines.append("")
        lines.append(f"**完整性评分**: {completeness['completeness_score']:.1f}%")
        lines.append(f"**已包含章节**: {completeness['total_sections'] - len(completeness['missing_sections'])}/{completeness['total_sections']}")
        lines.append("")
        
        if completeness['missing_sections']:
            lines.append("### 缺失章节")
            for section in completeness['missing_sections']:
                lines.append(f"- ❌ {section}")
            lines.append("")
        
        # KEP列表
        lines.append("## 2. 关键体验路径 (KEP)")
        lines.append("")
        if keps:
            lines.append(f"**找到 {len(keps)} 个KEP**")
            lines.append("")
            lines.append("| 阶段 | 场景类型 | Actor | KEP描述 | 场景名称 | 场景编号 |")
            lines.append("|------|----------|-------|---------|----------|----------|")
            for kep in keps:
                lines.append(f"| {kep['phase']} | {kep['scenario_type']} | {kep['actor']} | {kep['kep_description']} | {kep['scenario_name']} | {kep['scenario_number']} |")
        else:
            lines.append("⚠️ 未找到KEP定义")
        lines.append("")
        
        # KEI列表
        lines.append("## 3. 关键体验指标 (KEI)")
        lines.append("")
        if keis:
            lines.append(f"**找到 {len(keis)} 个KEI**")
            lines.append("")
            lines.append("| 评估体系 | 维度 | 评估类型 | 是否必选 | 评估标准 |")
            lines.append("|----------|------|----------|----------|----------|")
            for kei in keis:
                lines.append(f"| {kei['evaluation_system']} | {kei['dimension']} | {kei['evaluation_type']} | {kei['is_required']} | {kei['evaluation_standard']} |")
        else:
            lines.append("⚠️ 未找到KEI定义")
        lines.append("")
        
        # 公共需求检查
        lines.append("## 4. 公共需求检查")
        lines.append("")
        completed = sum(1 for v in public_reqs.values() if v['status'] == 'completed')
        incomplete = sum(1 for v in public_reqs.values() if v['status'] == 'incomplete')
        missing = sum(1 for v in public_reqs.values() if v['status'] == 'missing')
        
        lines.append(f"- ✅ 已完成: {completed}")
        lines.append(f"- ⚠️ 未完成: {incomplete}")
        lines.append(f"- ❌ 缺失: {missing}")
        lines.append("")
        
        lines.append("### 详细状态")
        lines.append("| 公共需求 | 状态 |")
        lines.append("|----------|------|")
        for item, status in public_reqs.items():
            status_icon = "✅" if status['status'] == 'completed' else ("⚠️" if status['status'] == 'incomplete' else "❌")
            lines.append(f"| {item} | {status_icon} {status['status']} |")
        lines.append("")
        
        return "
".join(lines)


class PRDValidator:
    """PRD验证器"""

    def __init__(self, prd_file: str):
        self.prd_file = Path(prd_file)
        self.content = ""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load(self) -> bool:
        """加载PRD文件"""
        if not self.prd_file.exists():
            self.errors.append(f"PRD文件不存在: {self.prd_file}")
            return False

        try:
            self.content = self.prd_file.read_text(encoding='utf-8')
            return True
        except Exception as e:
            self.errors.append(f"读取PRD文件失败: {e}")
            return False

    def validate(self) -> Dict[str, Any]:
        """验证PRD"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'checks': {}
        }
        
        # 1. 检查文档信息
        doc_info_check = self._check_document_info()
        result['checks']['document_info'] = doc_info_check
        if not doc_info_check['valid']:
            result['valid'] = False
            result['errors'].extend(doc_info_check['errors'])
        
        # 2. 检查必需章节
        sections_check = self._check_required_sections()
        result['checks']['required_sections'] = sections_check
        if not sections_check['valid']:
            result['valid'] = False
            result['errors'].extend(sections_check['errors'])
        
        # 3. 检查KEP格式
        kep_check = self._check_kep_format()
        result['checks']['kep_format'] = kep_check
        if not kep_check['valid']:
            result['valid'] = False
            result['errors'].extend(kep_check['errors'])
        
        # 4. 检查KEI格式
        kei_check = self._check_kei_format()
        result['checks']['kei_format'] = kei_check
        if not kei_check['valid']:
            result['valid'] = False
            result['errors'].extend(kei_check['errors'])
        
        # 5. 检查公共需求
        public_req_check = self._check_public_requirements()
        result['checks']['public_requirements'] = public_req_check
        if not public_req_check['valid']:
            result['valid'] = False
            result['errors'].extend(public_req_check['errors'])
        
        result['errors'] = self.errors
        result['warnings'] = self.warnings
        
        return result

    def _check_document_info(self) -> Dict:
        """检查文档信息"""
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        required_fields = [
            ("文档版本", r"\|\s*版本号\s*\|"),
            ("创建日期", r"\|\s*创建日期\s*\|"),
            ("文档状态", r"\|\s*文档状态\s*\|")
        ]
        
        for field_name, pattern in required_fields:
            if not re.search(pattern, self.content):
                result['valid'] = False
                result['errors'].append(f"缺少文档信息: {field_name}")
        
        return result

    def _check_required_sections(self) -> Dict:
        """检查必需章节"""
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        required_sections = [
            "## 2. 产品需求",
            "### 2.1 需求来源",
            "### 2.2 需求背景及业务定位",
            "### 2.3 需求价值分析",
            "### 2.4 需求适用范围分析",
            "### 2.7 需求描述",
            "## 4. 非功能需求",
            "### 4.1 性能要求",
            "### 4.2 安全要求",
            "### 4.3 兼容性要求",
            "## 12. 附录",
            "## 13. 审批记录"
        ]
        
        for section in required_sections:
            if section not in self.content:
                result['valid'] = False
                result['errors'].append(f"缺少必需章节: {section}")
        
        return result

    def _check_kep_format(self) -> Dict:
        """检查KEP格式"""
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        # 检查是否有KEP章节
        if "关键体验路径" not in self.content and "KEP" not in self.content:
            result['valid'] = False
            result['errors'].append("未找到关键体验路径(KEP)章节")
        else:
            # 检查KEP表格格式
            kep_table_pattern = r'\|\s*阶段\s*\|\s*场景类型\s*\|\s*涉及Actor'
            if not re.search(kep_table_pattern, self.content):
                result['valid'] = False
                result['errors'].append("KEP表格格式不正确，缺少必需列")
        
        return result

    def _check_kei_format(self) -> Dict:
        """检查KEI格式"""
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        # 检查是否有KEI章节
        if "关键体验指标" not in self.content and "KEI" not in self.content:
            result['warnings'].append("未找到关键体验指标(KEI)章节")
        else:
            # 检查KEI表格格式
            kei_table_pattern = r'\|\s*评估体系\s*\|\s*维度\s*\|\s*评估类型'
            if not re.search(kei_table_pattern, self.content):
                result['valid'] = False
                result['errors'].append("KEI表格格式不正确，缺少必需列")
        
        return result

    def _check_public_requirements(self) -> Dict:
        """检查公共需求"""
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        # 检查是否有公共需求章节
        if "公共需求" not in self.content:
            result['valid'] = False
            result['errors'].append("缺少公共需求/能力交互影响分析章节")
        
        return result

    def generate_validation_report(self, format: str = "markdown") -> str:
        """生成验证报告"""
        validation_result = self.validate()
        
        if format == "json":
            return json.dumps(validation_result, ensure_ascii=False, indent=2)
        
        # Markdown格式
        lines = []
        lines.append("# PRD验证报告")
        lines.append("")
        lines.append(f"**验证时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**PRD文件**: {self.prd_file.name}")
        lines.append(f"**验证结果**: {'✅ 通过' if validation_result['valid'] else '❌ 未通过'}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 错误摘要
        if validation_result['errors']:
            lines.append("## 错误")
            lines.append("")
            for error in validation_result['errors']:
                lines.append(f"- ❌ {error}")
            lines.append("")
        
        # 警告摘要
        if validation_result['warnings']:
            lines.append("## 警告")
            lines.append("")
            for warning in validation_result['warnings']:
                lines.append(f"- ⚠️ {warning}")
            lines.append("")
        
        # 详细检查结果
        lines.append("## 详细检查结果")
        lines.append("")
        
        for check_name, check_result in validation_result['checks'].items():
            status = "✅ 通过" if check_result['valid'] else "❌ 未通过"
            lines.append(f"### {check_name}: {status}")
            lines.append("")
            
            if check_result['errors']:
                lines.append("**错误**:")
                for error in check_result['errors']:
                    lines.append(f"- {error}")
                lines.append("")
            
            if check_result['warnings']:
                lines.append("**警告**:")
                for warning in check_result['warnings']:
                    lines.append(f"- {warning}")
                lines.append("")
        
        return "
".join(lines)


def main():
    parser = argparse.ArgumentParser(description="PRD Generator and Analyzer")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # Generate命令
    gen_parser = subparsers.add_parser('generate', help='生成PRD文档')
    gen_parser.add_argument('config_file', help='配置文件路径 (JSON/YAML)')
    gen_parser.add_argument('--output', '-o', help='输出文件路径')
    gen_parser.add_argument('--format', choices=['markdown', 'json', 'yaml'], default='markdown', help='输出格式')
    
    # Analyze命令
    analyze_parser = subparsers.add_parser('analyze', help='分析PRD文档')
    analyze_parser.add_argument('prd_file', help='PRD文件路径')
    analyze_parser.add_argument('--output', '-o', help='输出文件路径')
    analyze_parser.add_argument('--format', choices=['markdown', 'json'], default='markdown', help='输出格式')
    
    # Validate命令
    validate_parser = subparsers.add_parser('validate', help='验证PRD文档')
    validate_parser.add_argument('prd_file', help='PRD文件路径')
    validate_parser.add_argument('--output', '-o', help='输出文件路径')
    validate_parser.add_argument('--format', choices=['markdown', 'json'], default='markdown', help='输出格式')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        # 生成PRD
        generator = PRDGenerator()
        config = generator.load_config(args.config_file)
        prd_content = generator.generate(config, format=args.format)
        
        output_path = args.output or f"prd_{config.metadata.version.replace('V', '')}.md"
        Path(output_path).write_text(prd_content, encoding='utf-8')
        print(f"PRD已生成: {output_path}")
        
    elif args.command == 'analyze':
        # 分析PRD
        analyzer = PRDAnalyzer(args.prd_file)
        if not analyzer.load():
            print(f"错误: 无法加载PRD文件", file=sys.stderr)
            return 1
        
        report = analyzer.generate_analysis_report(format=args.format)
        
        if args.output:
            Path(args.output).write_text(report, encoding='utf-8')
            print(f"分析报告已生成: {args.output}")
        else:
            print(report)
            
    elif args.command == 'validate':
        # 验证PRD
        validator = PRDValidator(args.prd_file)
        if not validator.load():
            print(f"错误: 无法加载PRD文件", file=sys.stderr)
            return 1
        
        report = validator.generate_validation_report(format=args.format)
        
        if args.output:
            Path(args.output).write_text(report, encoding='utf-8')
            print(f"验证报告已生成: {args.output}")
        else:
            print(report)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())