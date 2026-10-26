// 已废弃（单一形态收敛，见 IMPL-PLAN §7 / DESIGN §7），归档保留勿用
// =============================================================================
// wave-domains.js — Wave 3「域实现」workflow 模板（a2h-execute v2，tmpl-2 所有）
// =============================================================================
// 底稿：new_core/docs/design/corpus/aippt-pages.js（dynamic1 实测形态）。
// 设计：3 册 §3.3 wave-domains（6 处改动）；schema 见 2 册 §2.7 + IMPL-CONTRACT §3。
//
// 本文件是「填参模板」：generate_waves.py 读 blueprint 四件 JSON 后做纯文本替换，
// 产出可直接投递 Workflow 引擎的脚本，落盘工程 spec/waves/wave-domains.js（禁落
// 会话 scratchpad）。模板遵守 Workflow 沙箱约束（IMPL-CONTRACT §4）：无 fs、无
// Node API、无 Date.now/Math.random，只用 agent/parallel/pipeline/phase/log 原语；
// 模板不做任何文件写入——一切落盘由主循环在波尾依据本脚本返回值调用
// state_update.py / gate_check.py 完成。
//
// ── 占位符清单（generate_waves.py 填充；与 tmpl-1 系列模板同一规约）──────────
// A. 文本槽 {{<大写名>}}：出现在字符串字面量内，生成器逐字替换（不加引号）：
//    {{APP_KEY}}     应用短名（meta.name 前缀），如 aippt
//    {{APP_NAME}}    应用可读名（meta.description 文案用）
//    {{TASK_COUNT}}  任务数（meta.phases[0].detail 文案用）
// B. JSON 槽：块注释标记 __NAME_JSON__（形态 = 块注释包裹的标记 + 紧跟的默认
//    字面量 null/{}/[]），生成器把「标记+默认字面量」整体替换为 json.dumps(值)
//    （单行输出，JSON 字符串字面量天然免疫反引号/${} 冲突）：
//    __PROMPTS_JSON__         { "<taskKey>": "<assemble_prompt.py 组装的完整 prompt>" }
//                             组装序见 3 册 §3.2：①红线 ②项目契约 ③任务书（YOUR
//                             FILES 白名单由 ownership.json 渲染）④契约段 cheat
//                             sheet ⑤规则片段 ⑥输出要求。complex 域追加
//                             vm-three-phase.md 且任务书要求代理写盘
//                             spec/domains/<key>.source-notes.md。
//    __TASKS_JSON__           任务数组（domain-map.json#domains 派生，split 域已由
//                             生成器展开为多任务），条目：
//                             { "key": "member-pay", "title": "…",
//                               "complex": true, "needs_immersive_safearea": false }
//    __PEER_CONTRACTS_JSON__  同波契约段（dynamic1 DB_CONTRACT 机制的通用化），
//                             按契约 id 键控：
//                             { "<contractId>": { "text": "<契约段原文>",
//                               "applies_to": ["*" 或 taskKey...],
//                               "exclude": [taskKey...] } }
//                             exclude 通常 = 提供者任务自身（其任务书里已把该契约
//                             作为实现规格内嵌，不再重复注入）。
// C. prompt 内联 token（出现在 PROMPTS 的字符串值里，模板运行期替换）：
//    <<PEER_CONTRACTS>>  同波契约段插入点（组装序之④）；prompt 未含该 token 时
//                        模板将契约段追加到 prompt 尾部。
//
// ── 返回值契约（主循环消费，state_update.py 落盘）───────────────────────────
// { wave: 'domains', total, done,
//   missing: [taskKey...],            // 零产出/断连任务 → 折叠协议（recovery-playbook）
//   escalated: [{ task, final_state, escalation }...],
//   results: [{ key, output }...],    // output = 代理 StructuredOutput 原样
//   files: [...], deferred_items: [...], decision_gaps: [...] }
// 主循环波尾职责（不在模板内，3 册 §3.3）：state_update.py 逐任务落盘；
// deferred_items 汇入 contracts.json#deferred（登记由脚本做，代理只申报）；
// 一次性收束 = pageMap 全量生成 + main_pages.json 单项不变量校验 + Hello World
// 三联清理 → gate_check.py --gate compile#2（编译错误按 ownership 归因到域）。
//
// <!-- GAP(已解决): 占位符规约（JSON 槽 = 块注释标记紧跟默认字面量、文本槽 = 双花括号）
//      已由 generate_waves.py 按本清单实现（整串替换 + 唯一性校验 + 残留检查）；
//      PEER_CONTRACTS 因 contracts.json#modules 无 depends_on 字段暂注入 {}（planned 模块
//      契约已由 assemble_prompt ④段按 depends_on_infra 注入，语义等价的最小实现）。 -->
// <!-- GAP: workflow-params.waves.domains.model 的落点未定义——corpus 的 agent()
//      options 仅见 label/phase/schema，模板未传 model；若引擎支持 model 选项，
//      需 generate_waves.py 扩展注入面（契约缺口，上报勿越界）。 -->
// <!-- GAP: complex 域 source-notes 落盘（spec/domains/<key>.source-notes.md）由
//      任务书指令要求代理写盘（代理有 fs，模板无）；该指令属 assemble_prompt.py
//      的③段职责，本模板仅以 schema 强制 source_summary_roles，需 script-S1 确认。 -->
// =============================================================================

export const meta = {
  name: '{{APP_KEY}}-domains',
  description: 'Wave 3 (domains): implement all pages/dialogs/domain logic 1:1 from the migration specs of {{APP_NAME}}',
  phases: [{ title: 'Domains', detail: '{{TASK_COUNT}} domain agents implementing pages + dialogs in parallel fan-out' }],
}

// ---- 生成器注入区（JSON 槽，规约见文件头 B 节）-------------------------------
const PROMPTS = /*__PROMPTS_JSON__*/{}
const TASKS = /*__TASKS_JSON__*/[]
const PEER_CONTRACTS = /*__PEER_CONTRACTS_JSON__*/{}

// ---- 代理输出 schema（2 册 §2.7 域/infra 实现代理 schema 的域波实例）----------
// 枚举值跨文件逐字一致（IMPL-CONTRACT §3）：final_state 4 值、deferred.kind 6 值。
// schema 常量直接写在模板里（schemas/agent-output.schema.json 的对应子集）。
const RESULT_SCHEMA = {
  type: 'object',
  required: ['task', 'final_state', 'files'],
  properties: {
    task: { type: 'string', description: "task id, e.g. 'domain:member-pay'" },
    final_state: { type: 'string', enum: ['PASS', 'ESCALATED', 'ROLLED_BACK', 'BLOCKED'] },
    files: { type: 'array', items: { type: 'string' }, description: 'every file you created or modified (project-relative paths)' },
    exports: { type: 'array', items: { type: 'string' }, description: 'reusable exported symbols with signatures, if this domain added any (contract-sync input)' },
    deferred_items: {
      type: 'array',
      description: 'placeholders you registered per the placeholder taxonomy — declare only, the main loop scripts write the ledger',
      items: {
        type: 'object',
        required: ['kind', 'location', 'trigger'],
        additionalProperties: false,
        properties: {
          kind: { type: 'string', enum: ['thirdparty-sdk', 'forward-ref', 'resource-pending-translation', 'resource-pending-asset', 'forward-ref-uncertain', 'handoff'] },
          location: {
            anyOf: [
              { type: 'string', minLength: 1 },
              { type: 'object', required: ['file', 'anchor'], additionalProperties: false,
                properties: { file: { type: 'string', minLength: 1 }, anchor: { type: 'string', minLength: 1 } } },
            ],
            description: 'file#anchor shorthand or {file, anchor}',
          },
          trigger: {
            anyOf: [
              { type: 'string', pattern: '^(symbol-implemented|sdk-available|decision-chosen|api-online|resource-ready|grep|artifact|slice):.+$' },
              { type: 'object', required: ['type', 'arg'], additionalProperties: false,
                properties: {
                  type: { type: 'string', enum: ['symbol-implemented', 'sdk-available', 'decision-chosen', 'api-online', 'resource-ready', 'grep', 'artifact', 'slice'] },
                  arg: { type: 'string', minLength: 1 },
                  check_cmd: { type: 'string' },
                } },
            ],
          },
          resolve_by: { type: 'string', description: 'REQUIRED when kind is forward-ref / forward-ref-uncertain' },
          side_effects: { oneOf: [
            { type: 'string', enum: ['none'] },
            { type: 'array', items: { type: 'string', minLength: 1 } },
          ] },
          note: { type: 'string', description: 'free-form prose belongs only here' },
        },
        allOf: [
          { if: { properties: { kind: { enum: ['forward-ref', 'forward-ref-uncertain'] } }, required: ['kind'] },
            then: { required: ['resolve_by'] } },
          { if: { properties: { kind: { const: 'thirdparty-sdk' } }, required: ['kind'] },
            then: { required: ['side_effects'] } },
        ],
      },
    },
    resolved_refs: { type: 'array', items: { type: 'string', minLength: 1 }, description: 'resolved forward-ref ledger IDs or file#anchor locations' },
    decision_gaps: {
      type: 'array',
      description: 'decisions missing from the blueprint that blocked or degraded your work (G-ID protocol)',
      items: {
        type: 'object',
        required: ['g_id', 'category', 'blocking'],
        properties: {
          g_id: { type: 'string' },
          category: { type: 'string' },
          blocking: { type: 'string', description: 'what exactly is blocked and how you proceeded' },
        },
      },
    },
    escalation: {
      type: 'object',
      description: 'REQUIRED when final_state is not PASS',
      properties: { reason: { type: 'string' }, g_id: { type: 'string' } },
    },
    source_summary_roles: { type: 'array', items: { type: 'string' }, description: 'complex domains MUST list the Kotlin class name mapped to each source-understanding role' },
    safearea_layers: { type: 'array', items: { type: 'string' }, description: 'immersive domains MUST list the 4 safearea layers as file:line' },
    rereads: { type: 'array', items: { type: 'string' } },
    sdk_skills_read: { type: 'array', items: { type: 'string' } },
  },
}

// complex 域必填 source_summary_roles（旧「无类名→WORKER FAIL」的机械化）；
// needs_immersive_safearea 域必填 safearea_layers（4 层 file:line）。
// 按任务克隆 schema 动态收紧 required——结构保证优先于 prompt 告诫；
// state_update.py 落盘时仍反查校验（双保险，3 册 §3.2 确定性注入源）。
function schemaFor(t) {
  const s = JSON.parse(JSON.stringify(RESULT_SCHEMA))
  if (t.complex) s.required.push('source_summary_roles')
  if (t.needs_immersive_safearea) s.required.push('safearea_layers')
  return s
}

// ---- 同波契约段条件注入（dynamic1 DB_CONTRACT 机制的通用化，3 册 §3.2 之④）----
// 同波并行提供者的导出契约按任务 key 条件拼接：命中 applies_to（'*' 或本任务
// key）且不在 exclude（通常是提供者自身）内的契约段全部注入——消费者「先按契约
// 名编码，文件落盘后以实盘为准」，与旧 DB_CONTRACT 语义逐字同构。
function peerContractsFor(key) {
  const parts = []
  Object.keys(PEER_CONTRACTS).forEach((cid) => {
    const c = PEER_CONTRACTS[cid]
    if (!c || !c.text) return
    const applies = c.applies_to || ['*']
    const hit = applies.indexOf('*') >= 0 || applies.indexOf(key) >= 0
    const excluded = (c.exclude || []).indexOf(key) >= 0
    if (hit && !excluded) parts.push(c.text)
  })
  return parts.length > 0 ? parts.join('\n') : ''
}

function buildPrompt(t) {
  const base = PROMPTS[t.key] || ''
  const peers = peerContractsFor(t.key)
  if (base.indexOf('<<PEER_CONTRACTS>>') >= 0) return base.replace('<<PEER_CONTRACTS>>', peers)
  return peers ? base + '\n' + peers : base
}

// ---- 执行：parallel fan-out（改动点：TASKS 从 domain-map 生成，不再手写清单）----
if (TASKS.length === 0) {
  log('wave-domains: no tasks injected — nothing to do (generator produced an empty TASKS array)')
  return { wave: 'domains', total: 0, done: 0, missing: [], escalated: [], results: [], files: [], deferred_items: [], decision_gaps: [] }
}

const runnable = TASKS.filter((t) => PROMPTS[t.key])
const promptless = TASKS.filter((t) => !PROMPTS[t.key]).map((t) => t.key)
if (promptless.length > 0) log('WARN wave-domains: tasks without injected prompt (generator gap): ' + promptless.join(', '))

phase('Domains')
log('Implementing ' + runnable.length + '/' + TASKS.length + ' domains as parallel agents')

const raw = await parallel(runnable.map((t) => () =>
  agent(buildPrompt(t), { label: 'domain:' + t.key, phase: 'Domains', schema: schemaFor(t) })
))

// ---- 容错聚合（IMPL-CONTRACT §4：失败代理返回 null → filter(Boolean) + missing[]）----
const ok = raw.filter(Boolean)
const missing = promptless.slice()
const results = []
runnable.forEach((t, i) => {
  if (raw[i]) results.push({ key: t.key, output: raw[i] })
  else missing.push(t.key)
})

const files = []
const deferredItems = []
const resolvedRefs = []
const decisionGaps = []
const escalated = []
results.forEach((r) => {
  const o = r.output
  const of = o.files || []
  of.forEach((f) => files.push(f))
  const od = o.deferred_items || []
  od.forEach((d) => deferredItems.push(d))
  const or = o.resolved_refs || []
  or.forEach((ref) => resolvedRefs.push(ref))
  const og = o.decision_gaps || []
  og.forEach((g) => decisionGaps.push(g))
  if (o.final_state !== 'PASS') escalated.push({ task: r.key, final_state: o.final_state, escalation: o.escalation || null })
})

log(ok.length + '/' + TASKS.length + ' domain agents done; missing: [' + missing.join(', ') + ']; non-PASS: ' + escalated.length)
if (deferredItems.length > 0) log(deferredItems.length + ' deferred items declared — main loop must fold them into contracts.json#deferred')
if (decisionGaps.length > 0) log(decisionGaps.length + ' decision gaps reported (G-ID) — fail-fast per affected domain, not global')

// 波尾收束（pageMap 全量生成 / main_pages 校验 / Hello World 清理 / 编译门 #2）
// 全部由主循环在本脚本返回后执行——见文件头「返回值契约」。
return {
  wave: 'domains',
  total: TASKS.length,
  done: ok.length,
  missing: missing,
  escalated: escalated,
  results: results,
  files: files,
  deferred_items: deferredItems,
  resolved_refs: resolvedRefs,
  decision_gaps: decisionGaps,
}
