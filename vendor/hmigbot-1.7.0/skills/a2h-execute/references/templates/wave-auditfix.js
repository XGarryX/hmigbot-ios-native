// 已废弃（单一形态收敛，见 IMPL-PLAN §7 / DESIGN §7），归档保留勿用
// =============================================================================
// wave-auditfix.js — Wave 4「审计修复」workflow 模板（a2h-execute v2，tmpl-2 所有）
// =============================================================================
// 底稿：corpus/aippt-verify.js + corpus/aippt-verify2.js 合并（dynamic1 实测形态）。
// 设计：3 册 §3.3 wave-auditfix（3 处改动 + round-0/1/2 结构 + 分片规则）；
// findings/fix schema 逐字对齐 2 册 §2.7（wave-auditfix 标准件）。
//
// 三段结构：
// · round-0（本模板之外，LLM 之前）：主循环先跑脚本预检族（audit_skeletons /
//   verify_slice_wiring / router-verify 脚本族 / icon_audit / audit_i18n /
//   design-tokens 正则 / CHECK-2 grep 表 / deferred 对账），机械 findings 经
//   __ROUND0_FINDINGS_JSON__ 槽注入，直接并入 round-1 各域修复清单——脚本能抓
//   的不烧 token。
// · round-1（Audit/Fix 两 phase）：pipeline(域数组, auditFn, fixFn)，audit 落地即
//   fix；audit 空 findings（且该域无 round-0 机械项）短路不起 fixer；findings 机械
//   转写进 fix prompt（含 android_ref / failure_scenario 字段）。
// · round-2（Sweep/Repair 两 phase）：__LENSES_JSON__ 驱动的横切镜头（默认三镜头
//   nav-contracts / runtime-safety / flow-integrity；failure_scenario 必填）。
//   分片规则（防大库静默退化为抽样扫描）：代码库行数 > lens_shard_loc_threshold
//   （默认 5 万）时，生成器把每个 lens 按 ownership 分区展开为 N 个条目（shard
//   字段 {partition, files_hint}，files_hint 由 round-0 预筛脚本产出，lens 代理以
//   清单为导航而非全库自由扫描）；模板检测到任一 shard 条目即切换为
//   「全量 fan-out 扫描 → 按 lens 汇总机械去重 → 每 lens 一个修复代理」两段式。
// 波尾（本模板之外）：编译门 #3 = 终态全量编译 → state.json 全量核账
// （ESCALATED > escalated_block_ratio 阻断）→ 迁移报告脚本聚合。
// 重跑：本模板单轮通过即止；repair_max_rounds=2 由主循环经
// generate_waves.py --wave auditfix --retry-failed 计数执行（3 册 §3.4 归一）。
//
// ── 占位符清单（generate_waves.py 填充；与 tmpl-1 系列模板同一规约）──────────
// A. 文本槽 {{<大写名>}}：出现在字符串字面量内，生成器逐字替换（不加引号）：
//    {{APP_KEY}}       应用短名（meta.name 前缀），如 aippt
//    {{APP_NAME}}      应用可读名（meta.description 文案用）
//    {{DOMAIN_COUNT}}  round-1 域数（meta phase 文案用）
//    {{LENS_COUNT}}    round-2 镜头条目数（meta phase 文案用）
// B. JSON 槽：块注释标记 __NAME_JSON__（形态 = 块注释包裹的标记 + 紧跟的默认
//    字面量 null/{}/[]），生成器把「标记+默认字面量」整体替换为 json.dumps(值)：
//    __PROMPTS_JSON__          { "audit:<domainKey>": "<完整审计 prompt，含该域
//                                acceptance[] 条目 AC 双端核对 + source-notes 路径
//                                注入 + 审计纪律原文 'Only report defects you have
//                                VERIFIED by reading both sides — 5 certain > 25
//                                guesses'>",
//                                "fix:<domainKey>": "<修复 prompt 骨架，含该域
//                                ownership 白名单（YOUR FILES）与 <<FINDINGS_LIST>>
//                                token>",
//                                "repair:<lensKey>": "<round-2 修复 prompt 骨架，
//                                同上>" }
//    __AREAS_JSON__            round-1 域数组（domain-map.json 生成）：
//                              [{ "key": "member-pay", "owner": "domain:member-pay" }]
//    __LENSES_JSON__           round-2 镜头条目（默认三镜头各 1 条；分片时生成器按
//                              lens_shard_loc_threshold 展开为每 lens N 条）：
//                              [{ "key": "runtime-safety",
//                                 "prompt": "<完整扫描 prompt（分片条目内嵌
//                                            files_hint 清单导航）>",
//                                 "shard": { "partition": "p1",
//                                            "files_hint": ["..."] } }]
//                              shard 字段可选；无分片时省略。
//    __ROUND0_FINDINGS_JSON__  round-0 脚本预检机械 findings（条目 = findings item
//                              schema）：{ "<domainKey>": [ { "file": "...", "line": 0,
//                                "severity": "P1", "kind": "functional",
//                                "summary": "...", "fix": "..." } ] }
// C. prompt 内联 token（出现在 fix:/repair: prompt 骨架里，模板运行期替换）：
//    <<FINDINGS_LIST>>  机械转写的 findings 清单 + 修复纪律块的插入点；骨架未含
//                       该 token 时模板将两者追加到 prompt 尾部。
//
// ── 返回值契约（主循环消费，state_update.py / gate_check.py 落盘判定）─────────
// { wave: 'auditfix',
//   round1: { total, domains: [{ domain, audit_ok, findings, findings_from_script,
//             fix }...], findings_total, fixed_total },
//   round2: { entries, lenses: [{ lens, shards, sweeps_missing, findings,
//             repair }...], findings_total, fixed_total },
//   missing: ['audit:<k>'|'fix:<k>'|'sweep:<k>[@p]'|'repair:<k>'...],
//   cross_domain_backlog: [{ round, task, finding_ref, reason, required_owner }...],
//     // 跨域项 → 主循环阶段边界统一快修（2 册 §2.2 裁决/并行执行规约）
//   decision_gaps: [...], files_touched: [...] }
//
// <!-- GAP(已解决): 占位符规约（JSON 槽 = 块注释标记紧跟默认字面量、文本槽 = 双花括号）
//      已由 generate_waves.py 按本清单实现（整串替换 + 唯一性校验 + 残留检查）。 -->
// <!-- GAP(已解决 2026-08-02): round-0 预检族由 round0_precheck.py 统一编排（legacy
//      脚本按可用性调用，缺席→skipped_checks 不阻断；findings 归因落
//      spec/reports/round0/<domain>.json，生成器读入注入本槽，缺席时注入 {}）。 -->
// <!-- GAP(已解决): lenses 第三镜头 "e2e-journeys"（2 册 §2.5）与 "flow-integrity"
//      （3 册 §3.3 / corpus）系同一镜头两名——generate_waves.py 经别名表归一到同一
//      checklist，两名皆可在 workflow-params.lenses 使用。 -->
// <!-- GAP: 2 册 §2.7 audit schema 字段名为 domain；round-2 镜头无域概念，本模板令
//      domain 字段承载 lens key（schema description 已注明）。如需独立 lens 字段名
//      需契约修订（保持逐字对齐优先，未擅自加字段）。 -->
// =============================================================================

export const meta = {
  name: '{{APP_KEY}}-auditfix',
  description: 'Wave 4 (auditfix): round-1 per-domain adversarial parity audit+fix, round-2 cross-cutting lens sweep+repair for {{APP_NAME}}',
  phases: [
    { title: 'Audit', detail: 'round-1: {{DOMAIN_COUNT}} per-domain auditors compare implementation vs spec + Android source' },
    { title: 'Fix', detail: 'round-1: each audit feeds a fixer that closes the verified gaps (pipeline)' },
    { title: 'Sweep', detail: 'round-2: {{LENS_COUNT}} cross-cutting lens agents (sharded on large codebases)' },
    { title: 'Repair', detail: 'round-2: per-lens repair after shard merge + dedupe' },
  ],
}

// ---- 生成器注入区（JSON 槽，规约见文件头 B 节）-------------------------------
const PROMPTS = /*__PROMPTS_JSON__*/{}
const AREAS = /*__AREAS_JSON__*/[]
const LENSES = /*__LENSES_JSON__*/[]
const ROUND0_FINDINGS = /*__ROUND0_FINDINGS_JSON__*/{}

// ---- findings / fix schema（逐字对齐 2 册 §2.7，枚举与 IMPL-CONTRACT §3 一致）----
const FINDINGS_SCHEMA = {
  type: 'object',
  required: ['domain', 'findings'],
  properties: {
    domain: { type: 'string', description: 'round-1: the domain key under audit; round-2: the lens key' },
    findings: {
      type: 'array',
      description: 'every VERIFIED parity defect; an empty array is a valid and respectable answer',
      items: {
        type: 'object',
        required: ['file', 'severity', 'kind', 'summary', 'fix'],
        properties: {
          file: { type: 'string' },
          line: { type: 'number' },
          severity: { type: 'string', enum: ['P0', 'P1', 'P2'] },
          kind: { type: 'string', enum: ['functional', 'visual', 'arkts', 'nav', 'runtime'] },
          summary: { type: 'string', description: 'what Android/the spec does vs what the current code does' },
          android_ref: { type: 'string', description: 'Android source reference, file:line' },
          fix: { type: 'string', description: 'concrete change to make' },
          failure_scenario: { type: 'string', description: 'when/how it breaks (REQUIRED in round-2)' },
        },
      },
    },
    decision_gaps: {
      type: 'array',
      items: {
        type: 'object',
        required: ['g_id', 'category', 'blocking'],
        properties: {
          g_id: { type: 'string' },
          category: { type: 'string' },
          blocking: { type: 'string' },
        },
      },
    },
  },
}

// round-2 镜头版：failure_scenario 必填（3 册 §3.3），其余逐字同上。
const LENS_FINDINGS_SCHEMA = JSON.parse(JSON.stringify(FINDINGS_SCHEMA))
LENS_FINDINGS_SCHEMA.properties.findings.items.required.push('failure_scenario')

const FIX_SCHEMA = {
  type: 'object',
  required: ['domain', 'fixed', 'skipped', 'files_touched'],
  properties: {
    domain: { type: 'string', description: 'round-1: the domain key; round-2: the lens key' },
    fixed: { type: 'array', items: { type: 'string' }, description: 'finding ref + what was actually changed' },
    skipped: {
      type: 'array',
      items: {
        type: 'object',
        required: ['finding_ref', 'reason'],
        properties: {
          finding_ref: { type: 'number', description: '1-based index into the findings list you were given' },
          reason: { type: 'string', description: 'why not fixed (finding wrong / already handled / out of whitelist)' },
          required_owner: { type: 'string', description: "REQUIRED when the fix needs another owner's file, e.g. 'domain:home'" },
        },
      },
    },
    files_touched: { type: 'array', items: { type: 'string' } },
  },
}

// ---- findings 机械转写（不改写不综述，逐字段搬运；含 android_ref/failure_scenario）----
function transcribeFindings(findings, scriptCount) {
  return findings.map((f, i) => {
    const loc = f.file + (f.line ? ':' + f.line : '')
    const tag = i < scriptCount ? ' [script:round-0]' : ''
    return (i + 1) + '. [' + (f.severity || 'P1') + '/' + (f.kind || 'functional') + '] ' + loc + tag +
      '\n   PROBLEM: ' + (f.summary || '') +
      '\n   ANDROID REF: ' + (f.android_ref || 'n/a') +
      '\n   FAILS WHEN: ' + (f.failure_scenario || 'n/a') +
      '\n   FIX: ' + (f.fix || 'see PROBLEM')
  }).join('\n')
}

// 修复纪律块（模板常量，结构性保证注入每个 fix/repair prompt）：
// 复核否决权原文 'auditors sometimes misread'（dynamic1 实测 35% 否决率来源）
// + 所有权白名单边界（越界 → skipped 带 required_owner）。
const FIX_DISCIPLINE = 'For EACH finding: open the file, confirm the defect is real (re-check against the spec / Android source — auditors sometimes misread; dynamic1 measured a ~35% veto rate), then fix it properly and minimally. If a finding is wrong or already handled elsewhere, skip it with its finding_ref and the reason. Findings tagged [script:round-0] come from deterministic pre-check scripts — still re-verify the surrounding context before editing. Do not refactor beyond the fix. ArkTS strict mode must stay valid (no any/unknown, explicit return types, typed object literals, block-bodied typed arrow callbacks) — a fix that breaks the build is worse than the defect it removes. ONLY touch files inside the YOUR FILES whitelist given above; if a fix requires another owner\'s file, report it in skipped with reason + required_owner (e.g. \'domain:home\') and the exact change needed — the main loop resolves cross-owner items at the phase boundary.'

function buildFixPrompt(base, findings, scriptCount) {
  const block = transcribeFindings(findings, scriptCount) + '\n\n' + FIX_DISCIPLINE
  if (base.indexOf('<<FINDINGS_LIST>>') >= 0) return base.replace('<<FINDINGS_LIST>>', block)
  return base + '\n\nVERIFIED DEFECTS TO FIX:\n\n' + block
}

// 分片汇总去重：机械指纹 file + line + kind + severity + summary 前 64 字符。
// 同 lens 各分片按 ownership 分区扫描，跨分区边界（如 nav 两端各在一区）会重复
// 报告同一缺陷，在此收敛；语义近似但措辞不同的重复项不强行合并（宁重勿漏）。
function dedupeFindings(findings) {
  const seen = {}
  const out = []
  findings.forEach((f) => {
    const fp = f.file + '#' + (f.line || 0) + '#' + (f.kind || '') + '#' + (f.severity || '') + '#' + (f.summary || '').slice(0, 64)
    if (seen[fp]) return
    seen[fp] = true
    out.push(f)
  })
  return out
}

// ---- 聚合器 ------------------------------------------------------------------
const missing = []
const gaps = []
const backlog = []

function collectGaps(res) {
  const gd = (res && res.decision_gaps) || []
  gd.forEach((g) => gaps.push(g))
}

function collectBacklog(round, key, fixRes) {
  const sk = (fixRes && fixRes.skipped) || []
  sk.forEach((s) => {
    if (s && s.required_owner) backlog.push({ round: round, task: key, finding_ref: s.finding_ref, reason: s.reason, required_owner: s.required_owner })
  })
}

// =============================================================================
// round-1：逐域 audit → fix（pipeline 原语保证 audit 落地即 fix）
// =============================================================================
phase('Audit')
log('round-1: auditing ' + AREAS.length + ' domains, each audit feeds a fixer as it lands')

const round1 = await pipeline(
  AREAS,
  (a) => {
    const p = PROMPTS['audit:' + a.key]
    if (!p) return Promise.resolve(null)
    return agent(p, { label: 'audit:' + a.key, phase: 'Audit', schema: FINDINGS_SCHEMA })
  },
  (auditRes, a) => {
    if (!auditRes && !PROMPTS['audit:' + a.key]) missing.push('audit:' + a.key + ' (no prompt injected)')
    else if (!auditRes) missing.push('audit:' + a.key)
    collectGaps(auditRes)
    // round-0 机械 findings 并入该域修复清单（脚本项在前，转写时打 [script:round-0] 标）
    const script = ROUND0_FINDINGS[a.key] || []
    const llm = (auditRes && auditRes.findings) || []
    const all = script.concat(llm)
    if (all.length === 0) {
      // audit 空 findings 且无机械项 → 短路，不起 fixer（空清单是合法且体面的答案）
      return { domain: a.key, audit_ok: !!auditRes, findings: [], findings_from_script: 0, fix: { domain: a.key, fixed: [], skipped: [], files_touched: [] } }
    }
    const base = PROMPTS['fix:' + a.key]
    if (!base) {
      missing.push('fix:' + a.key + ' (no prompt injected)')
      return { domain: a.key, audit_ok: !!auditRes, findings: all, findings_from_script: script.length, fix: null }
    }
    return agent(buildFixPrompt(base, all, script.length), { label: 'fix:' + a.key, phase: 'Fix', schema: FIX_SCHEMA })
      .then((fixRes) => {
        if (!fixRes) missing.push('fix:' + a.key)
        collectBacklog(1, a.key, fixRes)
        return { domain: a.key, audit_ok: !!auditRes, findings: all, findings_from_script: script.length, fix: fixRes }
      })
  }
)

const r1FindingsTotal = round1.reduce((n, r) => n + r.findings.length, 0)
const r1FixedTotal = round1.reduce((n, r) => n + ((r.fix && r.fix.fixed) ? r.fix.fixed.length : 0), 0)
log('round-1 done: ' + r1FindingsTotal + ' findings (' + round1.reduce((n, r) => n + r.findings_from_script, 0) + ' from round-0 scripts), ' + r1FixedTotal + ' fixed')

// =============================================================================
// round-2：横切镜头 sweep → repair（__LENSES_JSON__ 驱动；分片时两段式）
// =============================================================================
const hasShards = LENSES.some((l) => !!l.shard)
phase('Sweep')
log('round-2: ' + LENSES.length + ' lens entries' + (hasShards ? ' (sharded mode: fan-out -> merge/dedupe -> per-lens repair)' : ' (pipeline mode)'))

let round2 = []
if (!hasShards) {
  // 默认路径（≤ lens_shard_loc_threshold）：与 corpus/aippt-verify2.js 同构的 pipeline
  round2 = await pipeline(
    LENSES,
    (l) => {
      if (!l.prompt) return Promise.resolve(null)
      return agent(l.prompt, { label: 'sweep:' + l.key, phase: 'Sweep', schema: LENS_FINDINGS_SCHEMA })
    },
    (res, l) => {
      if (!res) missing.push('sweep:' + l.key)
      collectGaps(res)
      const fs = (res && res.findings) || []
      if (fs.length === 0) {
        return { lens: l.key, shards: 1, sweeps_missing: res ? 0 : 1, findings: [], repair: { domain: l.key, fixed: [], skipped: [], files_touched: [] } }
      }
      const base = PROMPTS['repair:' + l.key]
      if (!base) {
        missing.push('repair:' + l.key + ' (no prompt injected)')
        return { lens: l.key, shards: 1, sweeps_missing: 0, findings: fs, repair: null }
      }
      return agent(buildFixPrompt(base, fs, 0), { label: 'repair:' + l.key, phase: 'Repair', schema: FIX_SCHEMA })
        .then((rep) => {
          if (!rep) missing.push('repair:' + l.key)
          collectBacklog(2, l.key, rep)
          return { lens: l.key, shards: 1, sweeps_missing: 0, findings: fs, repair: rep }
        })
    }
  )
} else {
  // 分片路径（> lens_shard_loc_threshold）：全量 fan-out 扫描 → 按 lens 汇总去重 →
  // 每 lens 一个修复代理。分片代理以 files_hint 清单为导航（prompt 内嵌，生成器
  // 由 round-0 预筛脚本产出），修复白名单 = 该 lens repair prompt 里渲染的 ownership。
  const sweepRaw = await parallel(LENSES.map((l) => () => {
    if (!l.prompt) return Promise.resolve(null)
    const label = 'sweep:' + l.key + (l.shard ? '@' + l.shard.partition : '')
    return agent(l.prompt, { label: label, phase: 'Sweep', schema: LENS_FINDINGS_SCHEMA })
  }))

  const order = []
  const byKey = {}
  LENSES.forEach((l, i) => {
    if (!byKey[l.key]) {
      byKey[l.key] = { lens: l.key, shards: 0, sweeps_missing: 0, findings: [] }
      order.push(l.key)
    }
    const b = byKey[l.key]
    b.shards += 1
    const r = sweepRaw[i]
    if (!r) {
      b.sweeps_missing += 1
      missing.push('sweep:' + l.key + (l.shard ? '@' + l.shard.partition : ''))
      return
    }
    collectGaps(r)
    const fs = r.findings || []
    fs.forEach((f) => b.findings.push(f))
  })
  order.forEach((k) => { byKey[k].findings = dedupeFindings(byKey[k].findings) })

  phase('Repair')
  const repairRaw = await parallel(order.map((k) => () => {
    const b = byKey[k]
    if (b.findings.length === 0) return Promise.resolve({ domain: k, fixed: [], skipped: [], files_touched: [] })
    const base = PROMPTS['repair:' + k]
    if (!base) return Promise.resolve(null)
    return agent(buildFixPrompt(base, b.findings, 0), { label: 'repair:' + k, phase: 'Repair', schema: FIX_SCHEMA })
  }))
  round2 = order.map((k, i) => {
    const b = byKey[k]
    const rep = repairRaw[i]
    if (b.findings.length > 0 && !rep) missing.push('repair:' + k + (PROMPTS['repair:' + k] ? '' : ' (no prompt injected)'))
    collectBacklog(2, k, rep)
    return { lens: k, shards: b.shards, sweeps_missing: b.sweeps_missing, findings: b.findings, repair: rep }
  })
}

const r2FindingsTotal = round2.reduce((n, r) => n + r.findings.length, 0)
const r2FixedTotal = round2.reduce((n, r) => n + ((r.repair && r.repair.fixed) ? r.repair.fixed.length : 0), 0)
log('round-2 done: ' + r2FindingsTotal + ' findings across ' + round2.length + ' lenses, ' + r2FixedTotal + ' fixed')

// ---- 汇总（files_touched 去重聚合，gate_check.py --gate compile#3 的参考面）----
const filesTouched = []
const seenFile = {}
function addFiles(fx) {
  const fl = (fx && fx.files_touched) || []
  fl.forEach((f) => {
    if (seenFile[f]) return
    seenFile[f] = true
    filesTouched.push(f)
  })
}
round1.forEach((r) => addFiles(r.fix))
round2.forEach((r) => addFiles(r.repair))

if (backlog.length > 0) log(backlog.length + ' cross-owner skipped items — main loop must resolve them at the phase boundary')
if (gaps.length > 0) log(gaps.length + ' decision gaps reported (G-ID) — fail-fast per affected domain, not global')
log('auditfix wave complete; missing: [' + missing.join(', ') + ']')

// 波尾编译门 #3 / ESCALATED 比例核账 / 迁移报告聚合由主循环执行——见文件头契约。
return {
  wave: 'auditfix',
  round1: { total: AREAS.length, domains: round1, findings_total: r1FindingsTotal, fixed_total: r1FixedTotal },
  round2: { entries: LENSES.length, lenses: round2, findings_total: r2FindingsTotal, fixed_total: r2FixedTotal },
  missing: missing,
  cross_domain_backlog: backlog,
  decision_gaps: gaps,
  files_touched: filesTouched,
}
