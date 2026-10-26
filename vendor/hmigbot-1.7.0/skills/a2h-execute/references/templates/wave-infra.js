// 已废弃（单一形态收敛，见 IMPL-PLAN §7 / DESIGN §7），归档保留勿用
// ============================================================================
// wave-infra.js —— A2H v2 基建波 Workflow 模板（并行 fan-out，文件所有权两两不相交）
//
// 底稿：new_core/docs/design/corpus/aippt-infra.js（dynamic1 实测形态）
// 设计：3 册 §3.3 wave-infra（改动 2 处：TASKS 从 contracts.json#modules[owner^=infra:] 生成 /
//       导出签名细则由契约条目渲染进 prompt，不再手写）+ 2 册 §2.7 域/infra 输出 schema
//       + IMPL-CONTRACT §3 枚举、§4 沙箱事实。
//
// 本文件是 generate_waves.py 的填参模板：占位符替换后落盘 <project>/spec/waves/。
// 未填参时本文件本身即合法 JS（有 node 时可用 node --check 自检），
// 但 TASKS/PROMPTS 为空、不可实际运行。
//
// ── 占位符表 ─────────────────────────────────────────────────────────────────
//   完整替换单元 = 块注释标记 + 紧随其后的默认字面量（如「块注释包裹的 __META_NAME__ 后跟 ''」）。
//   生成器把完整单元整串精确替换为 python json.dumps(v, ensure_ascii=True) 产物
//   （纯 ASCII 输出，对冲 Windows 编码；JSON 是 JS 字面量子集）；
//   每个完整单元在本文件**恰好出现一次**（生成器替换前应校验唯一性）——
//   因此本表只写〈标记名 | 默认字面量〉，不写完整单元串，避免与正文占位撞串。
//   标记名                默认  注入值
//   __META_NAME__         ''    meta.name 字符串，如 "a2h-infra-aippt"
//   __META_DESCRIPTION__  ''    meta.description 字符串（一句话：建哪些共享层）
//   __META_PHASES__       []    meta.phases 数组；首项 title 必须为 "Infra"
//                               （与下方 phase() 调用及 agent 的 phase 选项逐字一致）
//   __TASKS_JSON__        []    任务数组 [{key,label}]；key 为去掉 "infra:" 前缀的任务键
//                               （如 owner="infra:api-pay" → key="api-pay"），
//                               来源 contracts.json#modules[owner^=infra:] 按 owner 聚组
//   __PROMPTS_JSON__      {}    prompt 对象 {taskKey: promptString}，assemble_prompt.py 全量组装
//                               （YOUR FILES 白名单/spec 指针/契约条目渲染的导出签名细则/
//                                同波并行契约按需条件注入，全部在 prompt 字符串内）
//   __MAX_PARALLEL__      0     每批最大并发；0 或缺省 = 单批全并发
//
// ── 沙箱事实（IMPL-CONTRACT §4，模板作者/改动者必读）─────────────────────────
//   无 fs / 无 Node API / 无 Date.now / 无 Math.random；
//   可用原语仅 agent / parallel / pipeline / phase / log / args / budget。
//   模板不落盘：.ets 由建设代理写；state.json/契约回写由主循环在波尾执行。
//   meta 必须是纯字面量：生成器直接文本替换填好，禁止任何运行期拼接。
//
// ── 返回值契约（主循环消费面，波尾据此跑 contract_sync）─────────────────────
//   { completed:     string[]   // 有 StructuredOutput 产出的任务键（含 final_state≠PASS 者）
//   , results:       object[]   // 全量 StructuredOutput（IMPL_SCHEMA 形状），state_update.py 落盘
//   , missing:       string[]   // 零产出任务键（代理死亡/漏配 prompt）
//   , non_pass:      object[]   // [{task, final_state, escalation}]，final_state≠PASS 清单
//   , files_touched: string[] } // 去重并集：contract_sync 对账与按 ownership 精确回滚的参照
//   波尾主循环标准序列（3 册 §3.3）：
//   state_update.py 落盘 → contract_sync.py --blueprint <dir> --ets-root <dir> 实盘对账
//   （modules[].status planned→implemented 回写；漂移三分类处置）→ 编译门 #1（gate_check.py）
//   → missing 走折叠协议、non_pass 走升级/降档 —— 回写完成才放行 wave-domains。
//
// <!-- GAP: workflow-params.json §2.5 的 waves.infra 例只有 model/tasks_from，无 max_parallel
//      字段；本模板缺省 0=全并发。生成器若要对 infra 波限流，需在 workflow-params schema
//      增补该字段（schemas 所有者对齐）。 -->
// <!-- GAP(已解决): 替换单元边界（标记+默认字面量整串替换、JSON 槽全文件唯一）已由
//      generate_waves.py 按本表实现；IMPL_SCHEMA 已对齐 agent-output.schema.json infraImpl
//      分支（2 册 §2.7 版，旧 corpus 版 stubs 字段废除）。 -->
// ============================================================================

export const meta = {
  name: /*__META_NAME__*/'',
  description: /*__META_DESCRIPTION__*/'',
  phases: /*__META_PHASES__*/[],
}

// 任务清单与 prompt 全部由生成器注入。
// JSON 是 JS 字面量的子集：json.dumps 注入天然免疫反引号/${}/引号转义冲突。
const TASKS = /*__TASKS_JSON__*/[]
const PROMPTS = /*__PROMPTS_JSON__*/{}
const MAX_PARALLEL = /*__MAX_PARALLEL__*/0

// schema 常量直接写在模板里（IMPL-CONTRACT §4；= schemas/agent-output.schema.json 的 infraImpl 分支，
// 2 册 §2.7 版为准——旧 corpus 版的 area/stubs 字段不再使用，stub/偏离点经 exports 的 notes 语义
// 与 deferred_items 承载）。枚举逐字对齐 IMPL-CONTRACT §3（final_state 四值、deferred.kind 六值）。
const IMPL_SCHEMA = {
  type: 'object',
  required: ['task', 'final_state', 'files', 'exports'],
  properties: {
    task: { type: 'string', description: "任务标识 'infra:<key>'，如 'infra:api-pay'" },
    final_state: {
      type: 'string',
      enum: ['PASS', 'ESCALATED', 'ROLLED_BACK', 'BLOCKED'],
      description: '任务终态四值枚举（IMPL-CONTRACT §3，跨文件逐字一致）',
    },
    files: { type: 'array', items: { type: 'string' }, description: '实际写入的文件（工程相对路径）' },
    exports: {
      type: 'array', items: { type: 'string' },
      description: '导出符号+完整签名（一行一条）——contract_sync.py 对账 contracts.json#modules[].exports 的申报侧输入；实盘 AST/grep 抽取为准，此处供快速 diff。被 stub/偏离 Android 语义的导出在此行尾注明原因，无法落成导出的 stub 走 deferred_items 申报',
    },
    deferred_items: {
      type: 'array',
      description: '占位申报——登记进 contracts.json#deferred 由脚本执行，代理只申报不登记；无则空数组',
      items: {
        type: 'object',
        required: ['kind', 'location', 'trigger'],
        properties: {
          kind: {
            type: 'string',
            enum: ['thirdparty-sdk', 'forward-ref', 'resource-pending-translation',
                   'resource-pending-asset', 'forward-ref-uncertain', 'handoff'],
            description: '六类枚举（IMPL-CONTRACT §3 逐字）',
          },
          location: { type: 'string', description: '文件+锚点，如 store/PayService.ets#wechatNative' },
          trigger: { type: 'string', description: '结构化触发条件（何时可解除，禁散文式 defer）' },
          resolve_by: { type: 'string', description: 'kind ∈ {forward-ref, forward-ref-uncertain} 必填' },
        },
      },
    },
    decision_gaps: {
      type: 'array',
      description: '运行期决策缺口（G-ID 上报，fail-fast 阻断相关任务而非全局）；无则空数组',
      items: {
        type: 'object',
        required: ['g_id', 'category', 'blocking'],
        properties: {
          g_id: { type: 'string', description: 'G-ID，schema 原样保留' },
          category: { type: 'string', description: '决策类目 C0–C17' },
          blocking: { type: 'string', description: '阻断了什么（哪个文件/功能等决策）' },
        },
      },
    },
    escalation: {
      type: 'object',
      description: 'final_state ≠ PASS 时填写；gate_check 据此区分“重跑/等决策/已回滚”',
      properties: {
        reason: { type: 'string' },
        g_id: { type: 'string', description: '关联 decision_gaps 的 G-ID（如有）' },
      },
    },
  },
}

// 分批工具：MAX_PARALLEL<=0 或不小于任务数时单批全并发（dynamic1 的 7 路同秒 fan-out 形态）
function toBatches(list, size) {
  if (size <= 0 || size >= list.length) return [list]
  const batches = []
  for (let i = 0; i < list.length; i += size) batches.push(list.slice(i, i + size))
  return batches
}

phase('Infra')

if (TASKS.length === 0) {
  log('FATAL: TASKS 为空——生成器未填参或 contracts.json 无 infra 模块；返回空结果交由主循环阻断')
  return { completed: [], results: [], missing: [], non_pass: [], files_touched: [] }
}

// 生成器缺口自检：漏配 prompt 的任务不派发，直接计入 missing（确定性失败优于空 prompt 派发）
const dispatchable = TASKS.filter(t => typeof PROMPTS[t.key] === 'string' && PROMPTS[t.key].length > 0)
const promptless = TASKS
  .filter(t => !(typeof PROMPTS[t.key] === 'string' && PROMPTS[t.key].length > 0))
  .map(t => t.key)
if (promptless.length > 0) log('警告: 以下任务缺 prompt（生成器缺口），计入 missing: ' + promptless.join(', '))

log('基建波 fan-out: ' + dispatchable.length + ' 个建设代理（文件所有权两两不相交）'
  + (MAX_PARALLEL > 0 ? '，每批最多 ' + MAX_PARALLEL : '，单批全并发'))

const completed = []
const collected = []
const missing = promptless.slice()

const batches = toBatches(dispatchable, MAX_PARALLEL)
for (let b = 0; b < batches.length; b++) {
  const batch = batches[b]
  if (batches.length > 1) log('批次 ' + (b + 1) + '/' + batches.length + ': ' + batch.map(t => t.key).join(', '))
  const results = await parallel(batch.map(t => () =>
    agent(PROMPTS[t.key], { label: 'infra:' + t.key, phase: 'Infra', schema: IMPL_SCHEMA })
  ))
  // parallel 结果与入参同序（Promise.all 语义）；失败代理返回 null——
  // 按下标回配任务键（IMPL-CONTRACT §4：.filter(Boolean) 容错 + 缺失列入 missing）
  for (let i = 0; i < batch.length; i++) {
    const r = results[i]
    if (r) {
      completed.push(batch[i].key)
      collected.push(r)
    } else {
      missing.push(batch[i].key)
    }
  }
}

// 汇总面（不做裁决，只给主循环结构化输入）：
// non_pass = 有产出但终态非 PASS；files_touched = 去重并集（contract_sync/精确回滚参照）
const nonPass = []
const filesTouched = []
for (let i = 0; i < collected.length; i++) {
  const r = collected[i]
  if (r.final_state !== 'PASS') {
    nonPass.push({ task: completed[i], final_state: r.final_state, escalation: r.escalation || null })
  }
  const files = r.files || []
  for (let j = 0; j < files.length; j++) {
    if (filesTouched.indexOf(files[j]) === -1) filesTouched.push(files[j])
  }
}

log('基建波完成: ' + completed.length + '/' + TASKS.length + ' 有产出'
  + (nonPass.length > 0 ? '；非 PASS: ' + nonPass.map(x => x.task + '=' + x.final_state).join(', ') : '')
  + (missing.length > 0 ? '；缺失: ' + missing.join(', ') : ''))
log('波尾交主循环: state_update 落盘 → contract_sync 对账回写 → 编译门 #1 → 折叠/降档裁决')
return {
  completed: completed,
  results: collected,
  missing: missing,
  non_pass: nonPass,
  files_touched: filesTouched,
}
