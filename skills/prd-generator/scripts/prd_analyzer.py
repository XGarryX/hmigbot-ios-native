#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD分析工具 - 基于终端V2.1模板
分析PRD文档，检查完整性、验证KEP/KEI、检查公共需求覆盖
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set


@dataclass
class KEP:
    """关键体验路径"""
    id: str
    description: str
    scenario_name: str
    scenario_id: str
    use_case_name: str
    use_case_id: str
    ir_requirement_id: str

    def is_valid(self) -> Tuple[bool, str]:
        """验证KEP格式"""
        if not self.scenario_id:
            return False, f"KEP缺少场景编号"
        if not self.use_case_id:
            return False, f"KEP缺少用例编号"
        if not self.ir_requirement_id:
            return False, f"KEP缺少IR需求编号"
        return True, "OK"


@dataclass
class KEI:
    """关键体验指标"""
    evaluation_system: str
    dimension: str
    evaluation_type: str
    required: bool
    evaluation_standard: str
    ir_requirement_id: str
    feature_name: str
    feature_code: str


@dataclass
class PublicRequirement:
    """公共需求/能力"""
    category: str
    name: str
    involved: bool
    rules: str
    reason: str


@dataclass
class PRDDocument:
    """PRD文档元数据和内容"""
    file_path: str
    version: str = ""
    date: str = ""
    author: str = ""
    status: str = ""
    content: str = ""

    # 提取的内容
    keps: List[KEP] = field(default_factory=list)
    keis: List[KEI] = field(default_factory=list)
    public_requirements: List[PublicRequirement] = field(default_factory=list)
    sections: Dict[str, bool] = field(default_factory=dict)


class PRDAnalyzer:
    """PRD文档分析器"""

    # 必需章节
    REQUIRED_SECTIONS = {
        "文档信息": False,
        "文档变更记录": False,
        "产品需求": False,
        "需求来源": False,
        "需求背景及业务定位": False,
        "需求价值分析": False,
        "需求适用范围分析": False,
        "竞品分析": False,  # 可选但推荐
        "需求描述": False,
        "需求参与者": False,
        "前置条件": False,
        "业务流程": False,
        "业务功能描述": False,
        "关键体验路径": False,
        "关键体验指标": False,
        "公共需求/能力交互影响分析": False,
        "运营策略": False,
        "非功能需求": False,
        "性能要求": False,
        "安全要求": False,
        "兼容性要求": False,
        "附录": False,
        "审批记录": False,
    }

    # 公共需求分类
    PUBLIC_REQUIREMENT_CATEGORIES = {
        "国际化": ["中国大陆", "全球"],
        "安全隐私": ["儿童账号", "已收集个人信息清单单上报", "隐私空间", "停止服务"],
        "全局业务": [
            "无障碍", "适老化", "退账号", "注销账号", "OOBE",
            "克隆备份", "旋转屏", "分屏", "外屏适配", "自由多窗",
            "双升单", "三方应用关联启动管理", "单回退双",
            "小艺问答操控", "统一交互"
        ],
    }

    def __init__(self, prd_file: str):
        self.prd_file = Path(prd_file)
        self.prd = PRDDocument(file_path=str(self.prd_file))
        self.issues: List[str] = []
        self.warnings: List[str] = []

    def load(self) -> bool:
        """加载并解析PRD文件"""
        if not self.prd_file.exists():
            self.issues.append(f"PRD文件未找到: {self.prd_file}")
            return False

        try:
            self.prd.content = self.prd_file.read_text(encoding='utf-8')
        except Exception as e:
            self.issues.append(f"读取PRD文件失败: {e}")
            return False

        self._parse_metadata()
        self._extract_keps()
        self._extract_keis()
        self._extract_public_requirements()
        self._check_sections()

        return True

    def _parse_metadata(self):
        """从头部提取PRD元数据"""
        content = self.prd.content

        # 提取版本号
        version_match = re.search(r'\|\s*版本号\s*\|\s*([Vv]?\d+\.?\d*)', content)
        if version_match:
            self.prd.version = version_match.group(1)

        # 提取创建日期
        date_match = re.search(r'\|\s*创建日期\s*\|\s*\[?([^\]|]+)\]?', content)
        if date_match:
            self.prd.date = date_match.group(1).strip()

        # 提取文档状态
        status_match = re.search(r'\|\s*文档状态\s*\|\s*([^
|]+)', content)
        if status_match:
            self.prd.status = status_match.group(1).strip()

    def _extract_keps(self):
        """提取KEP定义"""
        content = self.prd.content

        # 查找KEP表格
        kep_section = re.search(
            r'###?\s*关键体验路径.*?
((?:\|.*?
)+)',
            content,
            re.DOTALL
        )

        if kep_section:
            table_text = kep_section.group(1)
            lines = [line.strip() for line in table_text.split('
') if line.strip().startswith('|')]

            # 跳过表头
            if len(lines) > 2:
                for line in lines[2:]:  # 跳过表头和分隔行
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]  # 移除首尾空单元格
                    if len(cells) >= 8:
                        kep = KEP(
                            id=f"{cells[5] if cells[5] else ''}",
                            description=cells[3] if len(cells) > 3 else "",
                            scenario_name=cells[4] if len(cells) > 4 else "",
                            scenario_id=cells[5] if len(cells) > 5 else "",
                            use_case_name=cells[6] if len(cells) > 6 else "",
                            use_case_id=cells[7] if len(cells) > 7 else "",
                            ir_requirement_id=cells[8] if len(cells) > 8 else ""
                        )
                        self.prd.keps.append(kep)

    def _extract_keis(self):
        """提取KEI定义"""
        content = self.prd.content

        # 查找KEI表格
        kei_section = re.search(
            r'###?\s*关键体验指标.*?
((?:\|.*?
)+)',
            content,
            re.DOTALL
        )

        if kei_section:
            table_text = kei_section.group(1)
            lines = [line.strip() for line in table_text.split('
') if line.strip().startswith('|')]

            # 跳过表头
            if len(lines) > 2:
                for line in lines[2:]:
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]
                    if len(cells) >= 7:
                        kei = KEI(
                            evaluation_system=cells[0],
                            dimension=cells[1],
                            evaluation_type=cells[2],
                            required=cells[3] == "是" if len(cells) > 3 else False,
                            evaluation_standard=cells[4] if len(cells) > 4 else "",
                            ir_requirement_id=cells[5] if len(cells) > 5 else "",
                            feature_name=cells[6] if len(cells) > 6 else "",
                            feature_code=cells[7] if len(cells) > 7 else ""
                        )
                        self.prd.keis.append(kei)

    def _extract_public_requirements(self):
        """提取公共需求/能力分析"""
        content = self.prd.content

        # 查找公共需求表格
        pub_req_section = re.search(
            r'##?\s*公共需求/能力交互影响分析.*?整体分析.*?
((?:\|.*?
)+)',
            content,
            re.DOTALL
        )

        if pub_req_section:
            table_text = pub_req_section.group(1)
            lines = [line.strip() for line in table_text.split('
') if line.strip().startswith('|')]

            if len(lines) > 2:
                for line in lines[2:]:
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]
                    if len(cells) >= 4 and cells[1]:  # 有名称
                        pub_req = PublicRequirement(
                            category=cells[0],
                            name=cells[1],
                            involved="涉及" in cells[2] if len(cells) > 2 else False,
                            rules=cells[3] if len(cells) > 3 else "",
                            reason=cells[4] if len(cells) > 4 else ""
                        )
                        self.prd.public_requirements.append(pub_req)

    def _check_sections(self):
        """检查章节完整性"""
        content = self.prd.content

        for section in self.REQUIRED_SECTIONS:
            self.prd.sections[section] = section in content

    def check_completeness(self) -> Dict:
        """检查PRD完整性"""
        result = {
            "score": 0,
            "max_score": len(self.REQUIRED_SECTIONS),
            "sections": {},
            "missing": [],
            "warnings": []
        }

        for section, present in self.prd.sections.items():
            if present:
                result["score"] += 1
                result["sections"][section] = "✅"
            else:
                result["sections"][section] = "❌"
                if section not in ["竞品分析"]:  # 竞品分析是可选的
                    result["missing"].append(section)
                else:
                    result["warnings"].append(f"建议补充{section}")

        # 计算完整性等级
        score = result["score"]
        max_score = result["max_score"]
        percentage = (score / max_score) * 100

        if percentage >= 90:
            result["level"] = "优秀"
        elif percentage >= 75:
            result["level"] = "良好"
        elif percentage >= 60:
            result["level"] = "一般"
        else:
            result["level"] = "较差"

        result["percentage"] = percentage

        return result

    def validate_keps(self) -> Dict:
        """验证KEP"""
        result = {
            "total": len(self.prd.keps),
            "valid": 0,
            "invalid": [],
            "issues": []
        }

        for kep in self.prd.keps:
            is_valid, msg = kep.is_valid()
            if is_valid:
                result["valid"] += 1
            else:
                result["invalid"].append({
                    "scenario_id": kep.scenario_id,
                    "error": msg
                })

        # 检查是否有KEP
        if result["total"] == 0:
            result["issues"].append("未找到任何KEP定义")

        return result

    def validate_keis(self) -> Dict:
        """验证KEI"""
        result = {
            "total": len(self.prd.keis),
            "required_count": 0,
            "issues": []
        }

        for kei in self.prd.keis:
            if kei.required:
                result["required_count"] += 1
            if not kei.evaluation_standard:
                result["issues"].append(f"KEI '{kei.dimension}' 缺少评估标准")

        if result["total"] == 0:
            result["issues"].append("未找到任何KEI定义")

        return result

    def check_public_requirements(self) -> Dict:
        """检查公共需求覆盖"""
        result = {
            "analyzed": len(self.prd.public_requirements),
            "involved": 0,
            "not_involved": 0,
            "missing_categories": [],
            "issues": []
        }

        # 统计涉及和不涉及
        for req in self.prd.public_requirements:
            if req.involved:
                result["involved"] += 1
                # 检查是否提供了理由
                if not req.reason:
                    result["issues"].append(f"{req.category}-{req.name} 涉及但未说明理由")
            else:
                result["not_involved"] += 1

        # 检查是否覆盖了所有主要分类
        covered_categories = set(req.category for req in self.prd.public_requirements)
        for category in self.PUBLIC_REQUIREMENT_CATEGORIES:
            if category not in covered_categories:
                result["missing_categories"].append(category)

        return result

    def check_compliance_requirements(self) -> Dict:
        """检查规范性要求"""
        result = {
            "personal_info_collection": self._check_personal_info_collection(),
            "minor_protection": self._check_minor_protection(),
            "internationalization_ui": self._check_internationalization_ui(),
            "overall_compliance": {
                "score": 0,
                "issues": [],
                "warnings": []
            }
        }

        # 计算总体合规评分
        checks = result["personal_info_collection"]["passed"] + result["minor_protection"]["passed"] + result["internationalization_ui"]["passed"]
        total = result["personal_info_collection"]["total"] + result["minor_protection"]["total"] + result["internationalization_ui"]["total"]

        if total > 0:
            result["overall_compliance"]["score"] = round((checks / total) * 100, 1)

        # 收集所有问题和警告
        for category in ["personal_info_collection", "minor_protection", "internationalization_ui"]:
            result["overall_compliance"]["issues"].extend(result[category]["issues"])
            result["overall_compliance"]["warnings"].extend(result[category]["warnings"])

        return result

    def _check_personal_info_collection(self) -> Dict:
        """检查收集个人信息清单合规性"""
        result = {
            "passed": 0,
            "total": 5,
            "issues": [],
            "warnings": [],
            "details": []
        }

        content = self.prd.content

        # 检查1: 是否涉及个人信息收集
        if "个人信息" in content or "个人数据" in content:
            result["details"].append("✓ 检测到个人信息收集相关内容")
            result["passed"] += 1

            # 检查2: 隐私声明中是否明确列出
            if "隐私声明" in content:
                result["details"].append("✓ 包含隐私声明")
                result["passed"] += 1
            else:
                result["issues"].append("缺少隐私声明")
                result["details"].append("✗ 缺少隐私声明")

            # 检查3: 是否有收集个人信息清单
            if "收集个人信息清单" in content or "已收集个人信息清单" in content:
                result["details"].append("✓ 包含收集个人信息清单")
                result["passed"] += 1
            else:
                result["warnings"].append("建议添加收集个人信息清单")
                result["details"].append("⚠ 建议添加收集个人信息清单")

            # 检查4: 敏感个人信息是否突出明示
            if "敏感个人信息" in content:
                result["details"].append("✓ 包含敏感个人信息说明")
                result["passed"] += 1
            else:
                result["warnings"].append("如涉及敏感个人信息，需突出明示")
                result["details"].append("⚠ 如涉及敏感个人信息，需突出明示")

            # 检查5: 收集方式是否明确
            if any(keyword in content for keyword in ["用户输入", "APP收集", "第三方共享", "从合作伙伴获取"]):
                result["details"].append("✓ 收集方式说明")
                result["passed"] += 1
            else:
                result["warnings"].append("建议明确个人信息收集方式")
                result["details"].append("⚠ 建议明确个人信息收集方式")
        else:
            result["details"].append("○ 未检测到个人信息收集内容")
            result["passed"] += 5  # 不涉及，直接通过

        return result

    def _check_minor_protection(self) -> Dict:
        """检查未成年人保护合规性"""
        result = {
            "passed": 0,
            "total": 4,
            "issues": [],
            "warnings": [],
            "details": []
        }

        content = self.prd.content

        # 检查1: 是否涉及儿童/未成年人
        if "儿童" in content or "未成年人" in content:
            result["details"].append("✓ 检测到未成年人相关内容")
            result["passed"] += 1

            # 检查2: 是否有未成年人保护方案
            if "未成年人保护" in content or "儿童保护" in content:
                result["details"].append("✓ 包含未成年人保护方案")
                result["passed"] += 1
            else:
                result["issues"].append("涉及未成年人但缺少未成年人保护方案")
                result["details"].append("✗ 缺少未成年人保护方案")

            # 检查3: 个性化广告/营销限制
            if "个性化广告" in content or "商业营销" in content:
                if "禁止" in content or "不提供" in content:
                    result["details"].append("✓ 包含未成年人商业营销限制")
                    result["passed"] += 1
                else:
                    result["warnings"].append("建议明确未成年人不能通过自动化决策进行商业营销")
                    result["details"].append("⚠ 建议明确未成年人商业营销限制")
            else:
                result["passed"] += 1  # 不涉及个性化广告，直接通过

            # 检查4: 基本功能模式
            if "基本功能模式" in content or "基本功能服务" in content:
                result["details"].append("✓ 包含基本功能模式说明")
                result["passed"] += 1
            else:
                result["warnings"].append("建议说明未成年人基本功能模式")
                result["details"].append("⚠ 建议说明未成年人基本功能模式")
        else:
            result["details"].append("○ 未检测到未成年人相关内容")
            result["passed"] += 4  # 不涉及，直接通过

        return result

    def _check_internationalization_ui(self) -> Dict:
        """检查国际化界面规范"""
        result = {
            "passed": 0,
            "total": 3,
            "issues": [],
            "warnings": [],
            "details": []
        }

        content = self.prd.content

        # 检查1: 是否涉及国际化
        if "国际化" in content or "多语言" in content:
            result["details"].append("✓ 检测到国际化相关内容")
            result["passed"] += 1

            # 检查2: 语言支持
            if any(lang in content for lang in ["中文", "英文", "繁体中文", "藏文", "维文"]):
                result["details"].append("✓ 包含语言支持说明")
                result["passed"] += 1
            else:
                result["warnings"].append("建议明确支持的语言列表")
                result["details"].append("⚠ 建议明确支持的语言列表")

            # 检查3: 海外发布
            if "海外" in content or "全球" in content:
                if "全球化规范" in content or "合规" in content:
                    result["details"].append("✓ 包含海外合规说明")
                    result["passed"] += 1
                else:
                    result["warnings"].append("涉及海外发布，建议明确全球化规范")
                    result["details"].append("⚠ 建议明确全球化规范")
            else:
                result["passed"] += 1  # 不涉及海外发布，直接通过
        else:
            result["details"].append("○ 未检测到国际化相关内容")
            result["passed"] += 3  # 不涉及，直接通过

        return result

    def generate_report(self, format: str = "markdown") -> str:
        """生成分析报告"""
        completeness = self.check_completeness()
        kep_validation = self.validate_keps()
        kei_validation = self.validate_keis()
        pub_req_check = self.check_public_requirements()
        compliance_check = self.check_compliance_requirements()

        if format == "json":
            return json.dumps({
                "meta": {
                    "generated_at": datetime.now().isoformat(),
                    "tool_version": "1.0.0",
                    "prd_file": self.prd_file.name
                },
                "document_info": {
                    "file": self.prd_file.name,
                    "path": str(self.prd_file),
                    "version": self.prd.version,
                    "date": self.prd.date,
                    "status": self.prd.status
                },
                "completeness": completeness,
                "kep_validation": kep_validation,
                "kei_validation": kei_validation,
                "public_requirements": pub_req_check,
                "compliance": compliance_check
            }, ensure_ascii=False, indent=2)

        # Markdown格式
        lines = []
        lines.append("# PRD分析报告")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("**分析工具**: prd-generator v1.0")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 1. 文档信息")
        lines.append("")
        lines.append("| 项目 | 内容 |")
        lines.append("|------|------|")
        lines.append(f"| PRD文件 | {self.prd_file.name} |")
        lines.append(f"| 版本号 | {self.prd.version} |")
        lines.append(f"| 创建日期 | {self.prd.date} |")
        lines.append(f"| 文档状态 | {self.prd.status} |")
        lines.append("")

        # 完整性检查
        lines.append("## 2. 完整性检查")
        lines.append("")
        lines.append(f"**评分**: {completeness['score']}/{completeness['max_score']} ({completeness['percentage']:.1f}%)")
        lines.append(f"**等级**: {completeness['level']}")
        lines.append("")
        lines.append("| 章节 | 状态 |")
        lines.append("|------|------|")
        for section, status in completeness["sections"].items():
            lines.append(f"| {section} | {status} |")
        lines.append("")

        if completeness["missing"]:
            lines.append("### 缺失章节")
            for item in completeness["missing"]:
                lines.append(f"- {item}")
            lines.append("")

        if completeness["warnings"]:
            lines.append("### 建议补充")
            for item in completeness["warnings"]:
                lines.append(f"- {item}")
            lines.append("")

        # KEP验证
        lines.append("## 3. KEP验证")
        lines.append("")
        lines.append(f"**KEP总数**: {kep_validation['total']}")
        lines.append(f"**有效数量**: {kep_validation['valid']}")
        lines.append("")

        if self.prd.keps:
            lines.append("| 场景编号 | 场景名称 | 用例编号 | 状态 |")
            lines.append("|----------|----------|----------|------|")
            for kep in self.prd.keps[:10]:  # 最多显示10个
                is_valid, _ = kep.is_valid()
                status = "✅" if is_valid else "❌"
                lines.append(f"| {kep.scenario_id} | {kep.scenario_name} | {kep.use_case_id} | {status} |")
            lines.append("")

        if kep_validation["issues"]:
            lines.append("### 问题")
            for issue in kep_validation["issues"]:
                lines.append(f"- {issue}")
            lines.append("")

        # KEI验证
        lines.append("## 4. KEI验证")
        lines.append("")
        lines.append(f"**KEI总数**: {kei_validation['total']}")
        lines.append(f"**必选数量**: {kei_validation['required_count']}")
        lines.append("")

        if self.prd.keis:
            lines.append("| 维度 | 评估类型 | 是否必选 | 评估标准 |")
            lines.append("|------|----------|----------|----------|")
            for kei in self.prd.keis[:10]:
                required = "是" if kei.required else "否"
                lines.append(f"| {kei.dimension} | {kei.evaluation_type} | {required} | {kei.evaluation_standard[:30]}... |")
            lines.append("")

        if kei_validation["issues"]:
            lines.append("### 问题")
            for issue in kei_validation["issues"]:
                lines.append(f"- {issue}")
            lines.append("")

        # 公共需求检查
        lines.append("## 5. 公共需求/能力分析")
        lines.append("")
        lines.append(f"**已分析**: {pub_req_check['analyzed']} 项")
        lines.append(f"**涉及**: {pub_req_check['involved']} 项")
        lines.append(f"**不涉及**: {pub_req_check['not_involved']} 项")
        lines.append("")

        if self.prd.public_requirements:
            lines.append("| 分类 | 名称 | 是否涉及 |")
            lines.append("|------|------|----------|")
            for req in self.prd.public_requirements[:15]:
                involved = "✅ 涉及" if req.involved else "❌ 不涉及"
                lines.append(f"| {req.category} | {req.name} | {involved} |")
            lines.append("")

        if pub_req_check["issues"]:
            lines.append("### 问题")
            for issue in pub_req_check["issues"]:
                lines.append(f"- {issue}")
            lines.append("")

        if pub_req_check["missing_categories"]:
            lines.append("### 未分析的分类")
            for category in pub_req_check["missing_categories"]:
                lines.append(f"- {category}")
            lines.append("")

        # 规范性检查
        lines.append("## 6. 规范性检查")
        lines.append("")
        lines.append(f"**合规评分**: {compliance_check['overall_compliance']['score']:.1f}%")
        lines.append("")

        # 收集个人信息清单检查
        lines.append("### 6.1 收集个人信息清单")
        lines.append("")
        personal_info = compliance_check["personal_info_collection"]
        lines.append(f"**通过**: {personal_info['passed']}/{personal_info['total']}")
        lines.append("")
        for detail in personal_info["details"]:
            lines.append(f"- {detail}")
        lines.append("")

        # 未成年人保护检查
        lines.append("### 6.2 未成年人保护")
        lines.append("")
        minor = compliance_check["minor_protection"]
        lines.append(f"**通过**: {minor['passed']}/{minor['total']}")
        lines.append("")
        for detail in minor["details"]:
            lines.append(f"- {detail}")
        lines.append("")

        # 国际化界面用户规范检查
        lines.append("### 6.3 国际化界面用户规范")
        lines.append("")
        intl = compliance_check["internationalization_ui"]
        lines.append(f"**通过**: {intl['passed']}/{intl['total']}")
        lines.append("")
        for detail in intl["details"]:
            lines.append(f"- {detail}")
        lines.append("")

        # 总体问题汇总
        if compliance_check["overall_compliance"]["issues"]:
            lines.append("### 合规问题")
            for issue in compliance_check["overall_compliance"]["issues"]:
                lines.append(f"- ❌ {issue}")
            lines.append("")

        if compliance_check["overall_compliance"]["warnings"]:
            lines.append("### 改进建议")
            for warning in compliance_check["overall_compliance"]["warnings"]:
                lines.append(f"- ⚠️ {warning}")
            lines.append("")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="PRD分析工具 - 基于终端V2.1模板")
    parser.add_argument("prd_file", help="PRD文件路径")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="输出格式")

    args = parser.parse_args()

    analyzer = PRDAnalyzer(args.prd_file)
    if not analyzer.load():
        print(f"错误: {analyzer.issues[0]}", file=sys.stderr)
        return 1

    report = analyzer.generate_report(format=args.format)

    if args.output:
        Path(args.output).write_text(report, encoding='utf-8')
        print(f"报告已保存到: {args.output}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())