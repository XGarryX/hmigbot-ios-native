# §3.5 HMOS Spec 双重验证（references 详细版）

主 SKILL.md §3.5 的详细执行手册。所有 §M1/§M2/§M3 模式产出"行为变化清单"时**必跑**。

## 1. 目的与定位

产出"行为变化候选"时，除读 HMOS 源码（`.ets`）外，必须查 HMOS 侧 spec 文档作为第二信源。两者互相校准能：
1. 防止误改已实现功能（spec 已签收的不重复进 🔴）
2. 辅助定位真正的新增（spec 没提的更可能是真新增）
3. 避免破坏性改动（spec 反查告知"改动会触碰哪些已签收功能"）

## 2. 扫描哪些 spec 文档

```bash
HMOS={hmos_project}

# (a) 基线 spec
ls $HMOS/spec/baseline/
#   spec/baseline/ui-manifest.md       — 页面清单 + 已实现组件
#   spec/baseline/feature-index.md     — 功能索引
#   spec/baseline/features/*.md        — 每个基线功能详细 spec

# (b) 增量 spec
ls $HMOS/spec/features/          # F-xxx-{title}.md

# (c) 审计/变更记录（如存在）
ls $HMOS/spec/audit/ $HMOS/spec/CHANGELOG*
```

**spec 目录不存在时**：向用户确认"HMOS 项目未做过 a2h-spec 或 evolver"，本步降级为仅源码对齐，§S2 清单需标"本轮缺乏 spec 对照"。

## 3. Spec ↔ 候选差异交叉比对（两步）

### Step A — Spec 命中检查

```bash
KW="上传作品|uploadItem|batch-upload"
grep -rn -E "$KW" $HMOS/spec/
```

| 命中位置 | 处理 |
|---------|------|
| `baseline/` 且描述完整 | 已签收。源码有 → ✅ 已覆盖；源码无 → "spec 已定义但代码缺失" 特殊桶，进 §S2 让用户判 |
| `features/F-xxx.md` | 增量已做过，同上 |
| 未命中任何 spec | 真候选新增，保留在 🔴/🟠 |

### Step B — 改动影响预览

反向查"预计改动文件"在 spec 里是否被现有功能引用：

```bash
grep -rn "MainPage\.ets\|MainPage 页面" $HMOS/spec/
```

命中的 spec 条目 = 将与改动共存的已有功能，必须作为 §S3 evolver 委托时的 `existing_spec_refs` 带入。

## 4. HMOS 代码反向扫描（第三源，必跑）

§3.5.1~3.5.3 解决"spec 有没有描述"，不解决"代码实际是否实现"。命名差异会让 grep 方法名空命中构成假 🔴。

### 适用对象

每一条**候选 🔴**（尚未定稿，来自 §M1.3 / §M2.2 / §M3.1）。

### 执行步骤

**1. 提取 3~5 个同义关键词**

- 至少含 1 个**中文文案**（按钮文本 / Toast / 对话框标题，从 Android layout XML 或 strings.xml 拉）
- 至少含 1 个**同义动词**（save/export, upload/publish, refresh/reload, delete/remove, collect/favorite, pin/top 等）
- 可选：图标 / 资源 id / 路由 url 片段 / 常量值
- **禁止**：Android 类名 / 方法名 / field 名（§1.1 / §2.5 禁令 #7 已否决）

**2. 对每个关键词在 HMOS 源码 grep**

```bash
grep -rn "{关键词}" {hmos_project}/entry/src/main/ets/
```

**3. 汇总分桶**

| 命中数 | 处理 |
|--------|------|
| 0 命中 | 真缺 → 🔴 确认保留，`confidence: high` |
| ≥1 命中 | **强制降级**为 "⚠ 待人工复核"，主代理亲自读命中文件上下文（前后 ≥20 行）判等价性，不委托子代理 |

### 示例

```yaml
候选 🔴: 大纲保存到本地
keywords:
  - "保存本地"          # 中文文案
  - "保存大纲"          # 中文文案
  - "DocumentViewPicker"  # HMOS 常见保存 API
  - "user_files"        # 目录名
  - "save"              # 同义动词
grep_results:
  - "保存本地": CreateItemPage.ets:846        ← 命中
  - "DocumentViewPicker": CreateItemPage.ets:519
  - "save": 多处
结论: ⚠ 待人工复核
主代理复核: 读 CreateItemPage.ets:480-550 → 确认完整实现 → 从 🔴 移除，改为 ✅
```

## 5. 三源校验汇总（产出格式）

| 源 | 校验内容 | 产出字段 |
|---|---|---|
| Android 源码 | 功能存在且有行为轨迹 | `android_trace` |
| HMOS spec | 功能是否已签收 / 现有 spec 是否受影响 | `hmos_spec_status` + `existing_spec_refs` |
| HMOS 源码 | 代码层是否已实现（防假阳性）| `hmos_reverse_scan` |

**三项齐全才允许进 🔴**，任一缺失 → `confidence: low`，进"待验证桶"。

## 6. §S2 清单显式格式

§S2 用户对齐清单的每一条必须附以下字段：

```
1. 🔴 作品页批量上传
   Android 行为：FAB → picker → POST /api/items/batch-upload
   HMOS 源码：MainPage.Items 无入口，services/ 无接口
   HMOS Spec：❌ baseline/features/ 和 features/F-*.md 均未提及
   将触碰的已有 spec：spec/baseline/features/F-works-list.md
   hmos_reverse_scan: 关键词 [上传作品/upload/作品 FAB], 全部 0 命中 → confidence: high

2. 🟠 Campaign 弹窗倒计时
   HMOS Spec：⚠ baseline/features/F-campaign-dialog.md 定义了"用户可关闭"，未定义倒计时
            → 属于在已签收 spec 上扩展

3. ⚠ spec/代码不一致（特殊桶）
   HMOS Spec：F-refund-reason.md 定义 6 个理由
   HMOS 源码：RefundReasonDialog.ets 只实现了 4 个
   请用户判断
```

## 7. 与 §M3 Targeted 模式的交互

§M3 的 A_CLOSURE / H_TARGETS 产出时，对每个 H_TARGETS 文件额外跑一次本节 §6 Step B 反查，把"该文件当前承载的已有功能列表"作为 scope-lock 边界条件——evolver 委托时带入，Gate 1 让用户看到"本次改动将与 X/Y/Z 共存"。

## 8. 硬性要求（HARD-GATE 集中表）

- §S2 清单每条必须有 `HMOS Spec:` 字段（❌/✅/⚠ 三选一）
- §S2 清单每条 🔴 必须附 `hmos_reverse_scan` 字段，列出关键词 + 每个的命中数
- 关键词数 < 3 = 跳过 §3.5.5 = skill 失败
- 三项齐全才允许进 🔴
