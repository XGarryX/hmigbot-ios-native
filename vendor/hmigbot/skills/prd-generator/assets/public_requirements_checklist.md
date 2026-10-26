# 公共需求/能力检查清单模板

本文档用于生成PRD中的公共需求/能力检查清单。

---

## 1）整体分析（必选）

| 公共需求/能力分类 | 名称 | 是否涉及 | 须遵从的规则和要求 | 涉及或不涉及的理由 |
|---|---|---|---|---|
| 国际化 | 中国大陆 | {{CN_INTERNATIONALIZATION}} | 发文：《关于终端平台及产品多语言预置策略要求》<br>6种语言（中/英/港/台/藏/维） | {{CN_REASON}} |
| | 全球 | {{GLOBAL_INTERNATIONALIZATION}} | 分析是否涉及海外销售/上架，是否收集个人信息，若涉及，需满足如下规范<br>单框架设计规范-全球化-国际化<br>全球化规范，规范编号 DKBA 10299-2025.05 | {{GLOBAL_REASON}} |
| 安全隐私 | 儿童账号 | {{CHILD_ACCOUNT}} | 分析是否面向儿童开展业务，是否收集儿童个人信息，如果涉及，需满足如下规范<br>儿童个人数据保护政策<br>单框架安全隐私方案 未成年人保护<br>**儿童保护机制排查整改** | {{CHILD_ACCOUNT_REASON}} |
| | 已收集个人信息清单单上报 | {{PERSONAL_INFO_COLLECTION}} | 分析是否涉及及个人信息收集，若涉及，需在隐私声明中明确<br>收集个人信息清单落地指导 | {{PERSONAL_INFO_REASON}} |
| | 隐私空间 | {{PRIVATE_SPACE}} | 分析隐私空间下是否有不支持的功能，如果有，需隐藏<br>单框架设计规范-Pattern-灰显和隐藏 | {{PRIVATE_SPACE_REASON}} |
| | 停止服务 | {{STOP_SERVICE}} | 单框架"停止服务"/注销服务方案 | {{STOP_SERVICE_REASON}} |
| **全局业务** | 无障碍 | {{ACCESSIBILITY}} | 1、 规范编号 DKBA 17637-2025.07<br>2、 涉及页面交互的，须输出页面走焦和播报文本，更多要求参考 [增加屏幕朗读全局属性指导](https://www.example.com) | {{ACCESSIBILITY_REASON}} |
| | 适老化 | {{ELDERLY_FRIENDLY}} | 规范编号 DKBA 17637-2025.07 和 单框架设计规范 | {{ELDERLY_REASON}} |
| | 退账号 | {{ACCOUNT_EXIT}} | 分析应用使用的是系统账号（默认）还是应用账号，如果是系统账号，无需提供单独退出入口，但要随设置里的账号一并退出；如果是后者要构建独立的账号中心及独立退出机制<br>规范编号 DKBA 11569-2023.05 | {{ACCOUNT_EXIT_REASON}} |
| | 注销账号 | {{ACCOUNT_CANCEL}} | 单框架"停止服务"/注销服务方案 | {{ACCOUNT_CANCEL_REASON}} |
| | OOBE | {{OOBE}} | 单框架安全隐私方案-OOBE方案 | {{OOBE_REASON}} |
| | 克隆备份 | {{CLONE_BACKUP}} | 规范编号 DKBA 17637-2025.07 | {{CLONE_BACKUP_REASON}} |
| | 旋转屏 | {{ROTATION}} | 分析是否支持横屏<br>单框架设计规范-多设备响应式设计-横竖屏&控孔适配 | {{ROTATION_REASON}} |
| | 分屏 | {{SPLIT_SCREEN}} | 分析支持分屏<br>单框架设计规范-系统特性-多窗口交互 | {{SPLIT_SCREEN_REASON}} |
| | 外屏适配 | {{EXTERNAL_SCREEN}} | 分析是否支持折叠机外屏使用，分析是否有特殊改造 | {{EXTERNAL_SCREEN_REASON}} |
| | 自由多窗 | {{FREE_MULTI_WINDOW}} | 规范编号 DKBA 17637-2025.07 | {{FREE_MULTI_WINDOW_REASON}} |
| | 双升单 | {{DUAL_TO_SINGLE}} | 规范编号 DKBA 17637-2025.07 | {{DUAL_TO_SINGLE_REASON}} |
| | 三方应用关联启动管理 | {{THIRD_PARTY_LAUNCH}} | 单框架隐私方案-关联启动 | {{THIRD_PARTY_LAUNCH_REASON}} |
| | 单回退双 | {{SINGLE_TO_DUAL}} | 分析数据继承关系，图片、视频、音频、文档、录音、联系人、短信、通话记录、备忘录、日程、笔记等核心数据要继承，新版本特性或设置无需继承<br>单到双数据回退方案 | {{SINGLE_TO_DUAL_REASON}} |
| | 小艺问答操控 | {{CICIYA_CONTROL}} | 分析该特性是否需要支持小艺问答操控，比如是否涉及到小艺语音进行开关操控，是否涉及一句话进行功能闭环，更多详细操作指导参见：https://onebox.huawei.com/v/b4d98d3ff5ab2d384075aea0241b5d?type=1 | {{CICIYA_CONTROL_REASON}} |
| | 统一交互 | {{UNIFIED_INTERACTION}} | 分析该特效是否需要适配统一交互要求：长按/横滑/滑动多选/点击回顶/拖拽/浅层级交互/沉浸浏览/导航条/系统返回/跟手交互/分栏拖动/统一缩放/侧边面板。<br>规范明细参见：https://uxd.rnd.huawei.com/designGuideline/cn/home/11411 | {{UNIFIED_INTERACTION_REASON}} |

## 2）受影响的相关功能分析（可选）

写作说明：具体描述哪些功能需要支持上述能力/要求；有些功能需要支持，有些功能不需要支持，必须在此章节说明；默认所有功能都需要支持的能力/要求，不强制输出该章节的内容：

| 公共需求/能力名称 | 功能点 | 是否支持 | 说明 |
| :--- | :--- | :--- | :--- |
| 无障碍 | {{ACCESSIBILITY_FEATURE_1}} | | |
| | {{ACCESSIBILITY_FEATURE_2}} | | |
| | ... | | |
| 适老化 | {{ELDERLY_FEATURE_1}} | | |
| | ... | | |
| 克隆备份 | {{CLONE_BACKUP_FEATURE_1}} | | |
| | ... | | |
| 小艺问答操控 | {{CICIYA_FEATURE_1}} | | |
| | ... | | |
| ... | | | |

---

## 模板变量说明

| 变量 | 说明 | 可选值 |
|------|------|--------|
| `{{CN_INTERNATIONALIZATION}}` | 中国大陆国际化 | 涉及/不涉及 |
| `{{GLOBAL_INTERNATIONALIZATION}}` | 全球国际化 | 涉及/不涉及 |
| `{{CHILD_ACCOUNT}}` | 儿童账号 | 涉及/不涉及 |
| `{{PERSONAL_INFO_COLLECTION}}` | 个人信息收集 | 涉及/不涉及 |
| `{{PRIVATE_SPACE}}` | 隐私空间 | 涉及/不涉及 |
| `{{STOP_SERVICE}}` | 停止服务 | 涉及/不涉及 |
| `{{ACCESSIBILITY}}` | 无障碍 | 涉及/不涉及 |
| `{{ELDERLY_FRIENDLY}}` | 适老化 | 涉及/不涉及 |
| `{{ACCOUNT_EXIT}}` | 退账号 | 涉及/不涉及 |
| `{{ACCOUNT_CANCEL}}` | 注销账号 | 涉及/不涉及 |
| `{{OOBE}}` | OOBE | 涉及/不涉及 |
| `{{CLONE_BACKUP}}` | 克隆备份 | 涉及/不涉及 |
| `{{ROTATION}}` | 旋转屏 | 涉及/不涉及 |
| `{{SPLIT_SCREEN}}` | 分屏 | 涉及/不涉及 |
| `{{EXTERNAL_SCREEN}}` | 外屏适配 | 涉及/不涉及 |
| `{{FREE_MULTI_WINDOW}}` | 自由多窗 | 涉及/不涉及 |
| `{{DUAL_TO_SINGLE}}` | 双升单 | 涉及/不涉及 |
| `{{THIRD_PARTY_LAUNCH}}` | 三方应用关联启动管理 | 涉及/不涉及 |
| `{{SINGLE_TO_DUAL}}` | 单回退双 | 涉及/不涉及 |
| `{{CICIYA_CONTROL}}` | 小艺问答操控 | 涉及/不涉及 |
| `{{UNIFIED_INTERACTION}}` | 统一交互 | 涉及/不涉及 |

### 原因说明变量

每个能力对应一个 `_REASON` 后缀的变量，用于填写"涉及或不涉及的理由"

### 功能点变量

用于"受影响的相关功能分析"章节：
- `{{ACCESSIBILITY_FEATURE_N}}` - 无障碍功能点
- `{{ELDERLY_FEATURE_N}}` - 适老化功能点
- `{{CLONE_BACKUP_FEATURE_N}}` - 克隆备份功能点
- `{{CICIYA_FEATURE_N}}` - 小艺问答操控功能点