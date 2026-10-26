# Skill Hub 维护指南

Skill Hub 是 Fuxi ArkTS 的统一分类管理系统，通过 **type × domain** 二维矩阵对所有 Skill 进行分类，并自动生成 JSON 索引、Markdown 索引和可视化 Hub 网页。

---

## 1. 整体架构

```
skill-taxonomy.yaml              ← 分类枚举注册中心
arkts-skills/                    ← Claude Code 平台 skills
  manifest.yaml                  ← 集合级元数据
  skills/<name>/SKILL.md         ← Skill 定义（frontmatter 含分类标签）
arkts-skills-opencode/           ← OpenCode 平台 skills
  manifest.yaml
  skills/<name>/SKILL.md
arkts-style-wfhc/              ← 五方合创 风格规范集
  manifest.yaml
  skills/<name>/SKILL.md
scripts/skill-hub/               ← Python 流水线
  hub.py                         ← CLI 入口
  scanner.py                     ← 扫描 manifest + 解析 frontmatter
  validator.py                   ← 校验标签合法性
  aggregator.py                  ← 跨平台合并 + 统计
  generator.py                   ← 生成 JSON / Markdown / HTML
  migrate_tags.py                ← 一次性标签迁移工具
  dist/                          ← 生成产物
    skills.json
    SKILL-INDEX.md
    index.html
templates/hub.html               ← Hub 网页模板
scripts/ci/validate-skill-hub.sh ← CI 校验脚本
```

**数据流向**：

```
scan(manifest.yaml + SKILL.md) → validate(taxonomy) → aggregate(跨平台合并) → generate(JSON/MD/HTML)
```

---

## 2. 分类体系

### 2.1 二维矩阵

每个 Skill 通过 **type**（做什么）和 **domain**（在哪个领域）两个维度定位。

| Type | 含义 |
|------|------|
| pipeline | 流水线编排 — 端到端迁移流程中的阶段性 skill |
| domain | 领域知识 — 某个技术领域的专业能力 |
| style | 风格规范 — 编码标准和最佳实践 |
| codebase | 代码操作 — 对现有代码库的分析、修改、调试 |
| tool | 工具 — 通用辅助工具，不绑定特定领域 |

| Domain | 含义 |
|--------|------|
| ui | UI/组件构建 |
| state | 状态管理 |
| navigation | 导航路由 |
| data | 数据层/网络 |
| media | 媒体/下载 |
| system | 系统能力 |
| migration | 迁移专用 |
| engineering | 工程配置 |
| general | 通用/跨领域 |

### 2.2 扩展分类

所有合法的 type、domain、style-set、platform 值定义在项目根目录的 `skill-taxonomy.yaml` 中。

**添加新分类**：直接在 `skill-taxonomy.yaml` 中增加一行即可，无需修改脚本或目录。

```yaml
# 示例：添加新的 domain
domains:
  ...
  security: "安全/隐私"
```

---

## 3. Skill 标签

### 3.1 SKILL.md frontmatter 字段

每个 SKILL.md 的 frontmatter 必须包含分类标签：

```yaml
---
name: arkts-data-layer
description: 生成 ArkTS/HarmonyOS 数据层代码...
type: domain
domain: data
---
```

**风格类 Skill** 额外需要 `style-set` 字段：

```yaml
---
name: arkts-ui-component
description: UI 组件规范...
type: style
domain: ui
style-set: wfhc-standard
---
```

| 字段 | 必需 | 校验规则 |
|------|------|----------|
| name | 是 | 非空，全局唯一 |
| description | 是 | 非空 |
| type | 是 | 必须是 `skill-taxonomy.yaml` 中定义的值 |
| domain | 是 | 必须是 `skill-taxonomy.yaml` 中定义的值 |
| style-set | 条件 | type=style 时必填，值须在 taxonomy 中 |
| tags | 否 | 自由标签列表，缺失会产生 WARN |

### 3.2 manifest.yaml 字段

每个集合目录根下的 `manifest.yaml` 描述集合级元数据：

```yaml
collection: arkts-skills
description: "核心迁移与开发 skills"
platform: claude-code
maintainer: mj-cjm
version: 1.0.0
skills_dir: skills/
```

| 字段 | 必需 | 说明 |
|------|------|------|
| collection | 是 | 集合名称 |
| description | 否 | 集合描述 |
| platform | 是 | 所属平台（claude-code / opencode） |
| maintainer | 否 | 维护者 |
| version | 否 | 版本号 |
| skills_dir | 是 | Skill 目录相对路径 |
| default_style_set | 否 | 风格集合的默认 style-set |

---

## 4. 常用操作

### 4.1 新增 Skill

1. 在对应集合目录下创建 Skill 目录和 SKILL.md：

```bash
mkdir -p arkts-skills/skills/arkts-new-skill/references
```

2. 编写 SKILL.md，frontmatter 中包含 `type` 和 `domain`：

```yaml
---
name: arkts-new-skill
description: 一句话描述用途
type: domain
domain: ui
---
```

3. 如果需要跨平台，在 `arkts-skills-opencode/` 下创建同名目录和 SKILL.md（`name` 字段必须一致，Hub 会自动按 name 合并）。

4. 运行校验：

```bash
cd scripts/skill-hub
python hub.py --validate-only
```

### 4.2 新增风格集

1. 创建独立的风格集目录：

```bash
mkdir -p arkts-style-<team-name>/skills
```

2. 添加 `manifest.yaml`：

```yaml
collection: arkts-style-<team-name>
description: "<team-name> 团队编码风格"
platform: claude-code
maintainer: <maintainer>
version: 1.0.0
skills_dir: skills/
default_style_set: <team-name>-standard
```

3. 在 `skill-taxonomy.yaml` 中注册新的 style-set：

```yaml
style-sets:
  wfhc-standard: "五方合创 团队编码风格"
  <team-name>-standard: "<team-name> 团队编码风格"    # 新增
```

4. 在 `skills/` 下创建各个风格 Skill，frontmatter 中标注 `type: style` 和对应的 `style-set`。

### 4.3 新增平台

1. 创建新的集合目录 `arkts-skills-<platform>/`，添加 `manifest.yaml`。

2. 在 `skill-taxonomy.yaml` 的 `platforms` 下注册新平台名。

3. Hub 的 scanner 会自动扫描所有 `arkts-*/manifest.yaml`，无需额外配置。

### 4.4 修改分类标签

直接编辑 SKILL.md 的 frontmatter，修改 `type` 或 `domain` 字段，然后运行校验确认值合法。

---

## 5. Hub CLI

所有操作通过 `scripts/skill-hub/hub.py` 执行：

```bash
cd scripts/skill-hub
```

| 命令 | 用途 |
|------|------|
| `python hub.py` | 完整流水线：扫描 → 校验 → 聚合 → 生成产物到 `dist/` |
| `python hub.py --validate-only` | 仅校验，不生成文件（CI 用，有 ERROR 时 exit 1） |
| `python hub.py --out <DIR>` | 指定输出目录（默认 `dist/`） |
| `python hub.py --info <skill-name>` | 以 JSON 格式打印某个 Skill 的详细信息 |

### 5.1 生成产物

运行 `python hub.py` 后在 `dist/` 下生成三个文件：

| 文件 | 说明 |
|------|------|
| `skills.json` | 完整的聚合数据（skills、stats、matrix、gaps） |
| `SKILL-INDEX.md` | Markdown 格式的 Skill 索引，按 type 分组 |
| `index.html` | 可视化 Hub 网页（基于 `templates/hub.html` 模板） |

### 5.2 Hub 网页

`index.html` 是一个自包含的静态 HTML 文件，功能包括：

- **Skills 列表** — 排行榜式表格视图，支持搜索（`/` 快捷键聚焦）和筛选（按 type / domain）
- **Matrix 视图** — type × domain 二维矩阵，直观展示覆盖情况，点击单元格跳转到对应筛选
- **Analytics 视图** — Type 分布饼图、Domain 覆盖柱状图、Coverage Gaps 列表
- **详情面板** — 点击行项打开右侧滑入面板，查看完整信息

模板文件位于 `templates/hub.html`，使用 `{{SKILLS_DATA}}` 占位符注入 JSON 数据。修改模板后重新运行 `python hub.py` 即可更新。

---

## 6. 校验规则

### 6.1 ERROR（阻断性）

| 规则 | 说明 |
|------|------|
| name 必填 | frontmatter 缺少 name 字段 |
| type 必填且合法 | type 不在 `skill-taxonomy.yaml` 定义的值中 |
| domain 必填且合法 | domain 不在 `skill-taxonomy.yaml` 定义的值中 |
| style-set 条件必填 | type=style 时 style-set 缺失或不在 taxonomy 中 |
| platform 合法 | manifest.yaml 的 platform 不在 taxonomy 中 |
| name 全局唯一 | 同一平台内 name 重复 |

### 6.2 WARN（警告性）

| 规则 | 说明 |
|------|------|
| description 为空 | frontmatter 缺少 description |
| tags 缺失 | frontmatter 没有 tags 字段 |

---

## 7. CI 集成

CI 脚本位于 `scripts/ci/validate-skill-hub.sh`，执行 `python hub.py --validate-only`。

有 ERROR 时返回 exit code 1（CI 失败），仅 WARN 时返回 0（CI 通过）。

添加到 CI 流水线：

```bash
npm run check:skill-hub   # 或直接调用 scripts/ci/validate-skill-hub.sh
```

---

## 8. 批量标签迁移

`scripts/skill-hub/migrate_tags.py` 用于批量为 SKILL.md 注入 `type`/`domain`/`style-set` 标签。

```bash
cd scripts/skill-hub

# 预览变更（不实际修改文件）
python migrate_tags.py --dry-run

# 执行迁移
python migrate_tags.py
```

**特性**：

- 幂等执行 — 已有 type 字段的 SKILL.md 会跳过
- 分类映射定义在脚本内的 `CLASSIFICATION` 字典中
- 新增 Skill 后如需批量标签，更新 `CLASSIFICATION` 字典后重新执行

---

## 9. 目录命名规范

| 集合类型 | 命名模式 | 示例 |
|----------|----------|------|
| 平台 Skills | `arkts-skills[-<platform>]/` | `arkts-skills/`、`arkts-skills-opencode/` |
| 风格集 | `arkts-style-<team>/` | `arkts-style-wfhc/` |

Scanner 自动扫描项目根目录下所有匹配 `arkts-*/manifest.yaml` 的目录，新集合只需遵循此命名即可被识别。

---

## 10. 常见问题

### Q: 新增了 type 或 domain，需要改脚本吗？

不需要。只在 `skill-taxonomy.yaml` 中添加一行即可，校验和聚合会自动识别。

### Q: 同一个 Skill 在 claude-code 和 opencode 都有，Hub 怎么处理？

Hub 按 `name` 字段自动合并。同名 Skill 会聚合到一条记录中，`platforms` 字段列出所有支持的平台。两边的 `name` 必须完全一致。

### Q: Hub 网页怎么自定义样式？

修改 `templates/hub.html` 中的 CSS，然后运行 `python hub.py` 重新生成 `dist/index.html`。模板是自包含的单文件 HTML，CSS/JS 全部内联。

### Q: validate-only 报了 WARN 但没有 ERROR，影响 CI 吗？

不影响。只有 ERROR 才会导致 exit 1。WARN 是建议性提示（如 tags 缺失），不阻断流水线。

### Q: 怎么查看某个 Skill 的聚合结果？

```bash
cd scripts/skill-hub
python hub.py --info arkts-data-layer
```

会输出该 Skill 合并后的完整 JSON，包括所有平台信息。
