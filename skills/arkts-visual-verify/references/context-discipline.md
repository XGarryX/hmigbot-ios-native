# Context Discipline —— 上下文纪律细则（SKILL.md §0 的完整版）

> 本 skill 历史上出过两次**对话上下文压缩事故**：同时 Read `SKILL.md`（曾 1900 行）+ `spec/toolkit-fact-tree.json`（数十到上百页 entries），叠加任何业务文件就触顶。SKILL.md §0 列了六/八条强制铁律的**标题**；本文件是每条的**完整说明 + 例子 + 历史教训**，需要时读这一篇。

## 0.1 禁止 Read `spec/toolkit-fact-tree.json`
**绝对不要**用 Read 工具读这个文件——它给脚本吃，不给 LLM 吃。需要页面队列时**只读 `spec/visual-verify/page_queue.json`**（紧凑版，几 KB）：
```text
# Phase 1 Step 1.2 必跑，由本 skill 直接 Bash 调用：
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/build_page_queue.py \
    --tree spec/toolkit-fact-tree.json \
    --out  spec/visual-verify/page_queue.json
```
需要某页 navigation/sub_components 详情时用 python 一行式/`grep` 按需取片段，不要整文件 Read（跨平台，无 jq 依赖）：
```text
python3 -c "import json;print(json.dumps([p for p in json.load(open('spec/toolkit-fact-tree.json'))['pages'] if p['name']=='HomePage'],ensure_ascii=False,indent=1))"
```

## 0.2 reference 文件按需 Read，不预加载
SKILL.md 主文件保持精简（目标 < 400 行）。所有 reference **仅在对应 phase 真正用到时**才 Read。**不要 Phase 1 一上来就并行 Read 所有 references**——会重蹈覆辙。reference Read 时机见 SKILL.md §4 每个 Phase 标注的"详见 references/xxx.md"。

## 0.3 大文件操作走 script，不走 Read
模式：**任何 > 200 行的项目级 JSON / spec 文件，先用 Python（脚本或 `python3 -c` 一行式）处理写出小中间文件，再 Read 那个中间文件。**
- ✅ `python3 -c "import json;print(len(json.load(open('spec/toolkit-fact-tree.json'))['pages']))"` → 拿到 56，Read 0 字节
- ✅ `build_page_queue.py` → 写 page_queue.json，Read 几 KB
- ❌ Read `spec/toolkit-fact-tree.json`（offset/limit 也别用——容易反复 Read 同一文件累计触顶）

进度文件 `spec/visual-verify/progress.json` 同理：写小段补丁，不整文件 Read 后整文件 Write。

## 0.4 主会话禁止 Read 截图（绝对铁律）
主会话**永远不**用 Read 工具读 `spec/visual-verify/screenshots/**/*.{png,jpeg,jpg}`。
**为什么**：单张 1800px sbs JPEG 进 context ≈ 1.5K–5K tokens；56 页全量扫累计 100–280K，单会话注定爆。多模态读图 + 写 markdown 这条最重的链路整体外包给 **batch sub-agent**（详见 Phase 4）。
**主会话只读三类**：`page_queue.json`/`batches.json`（< 10KB）、`batches/{batch}/manifest.json`（每 batch < 5KB）、`spec/fix/round-N/ui/*.md`（小文本）。
**唯一例外**：用户明确要求肉眼抽检 1-3 张图；累计 > 3 张视为违规。
历史教训：v1/v2 把 56 张图 Read 给主会话当多模态用，必然爆栈。**违反 0.4 等同回到 v2 失败模式，整轮 visual-verify 视为执行失败**。

## 0.5 markdown schema 100% 合规
**写第一个 markdown 前必 Read [`fix-file-schema.md`](fix-file-schema.md) 一次**（唯一权威源，禁凭记忆猜 schema）。frontmatter 字段名 / kind / severity / fixer_layer 枚举、5 sections 标题、id=文件名规则、自检脚本全在 schema 文档里。
**事故防线**：写完每个 markdown 立即跑 schema §十 自检；连续 3 个写错 → sub-agent 停写、写 fatal_error 到 manifest 退出；主会话有 `scripts/reformat_markdown_to_schema.py` 兜底批量 reformat。

## 0.6/0.7 screenshots 命名 + reset_app 双端等价
- **路径**：iOS `screenshots/ios/{trip_id}/{page_id}.png`（跨 round 复用）；HMOS `screenshots/harmony/round-{N}/{trip_id}/{page_id}.jpeg`（每轮独立，禁覆盖）；sbs 同 HMOS。trip_id ∈ {`trip_1_logged_out`, `trip_2_logged_in_vip`}，必须分目录避免双态页互覆盖（如 HomePage 登录/未登录两态）。
- **reset 分级（★单侧化 2026-07-12，与 SKILL.md §0.6/0.7 对齐）**：**trip 边界=主会话专属**——iOS `pm clear` / HMOS `aa force-stop && bm clean -d -n` 归零后重建 trip 态（过首启链/登录），一个 trip 只做一次；**batch/页内 reset=只 kill 进程**（iOS `am force-stop` / HMOS `aa force-stop`），**禁 pm clear / bm clean**——清数据会抹掉主会话在 trip 边界建好的登录态/门链态，下一页冷启就撞回首启链（旧口径"每页必须 bm clean 否则首启链全跳过"已废止：首启链页由 trip 边界建态时链式连采/--capture-only 顺手采集，普通页正要跳过首启链直落主页）。
- 详 [`output-layout.md`](output-layout.md)（路径完整规约）+ [`phase4-navigation.md`](phase4-navigation.md)（reset 双场景）。

## 0.8 一次 Agent dispatch = 一个 batch
主代理派 sub-agent 必须循环：`next_batch.py`(exit 2 收工) → 若 `trip_scenarios_needed=true` 主代理先跑 `run_scenario_with_verify.py` 双端（**禁止直跑 scenario_run.py**，包装脚本管失败计数 + transient retry）→ Agent dispatch（prompt 只含 1 个 batch_id；自查 `grep -c <batch_id>` ≤ 1）→ `mark_batch_done.py` 回写 progress.json → 下一轮 next_batch。**不许凭记忆挑 batch / 不许塞多 batch 给单 sub-agent**。progress.json 是 SSOT，支持断点续跑。
scenario 包装脚本的 **exit code 路由表 + 门禁功能对照实验铁律** → 见 [`phase4-dispatch.md`](phase4-dispatch.md) 末尾。
