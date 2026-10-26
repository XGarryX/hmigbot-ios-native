// 已废弃（单一形态收敛，见 IMPL-PLAN §7 / DESIGN §7），归档保留勿用
// ============================================================================
// wave-understand.js —— A2H v2 理解波 Workflow 模板（单 phase 并行 fan-out）
//
// 底稿：new_core/docs/design/corpus/aippt-understand.js（dynamic1 实测形态）
// 设计：3 册 §3.3 wave-understand（改动 3 处：TASKS 由 domain-map 填参 /
//       schema 增 ac_candidates / 大域 spec 分片经 prompt 承载）+ IMPL-CONTRACT §4。
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
//   __META_NAME__         ''    meta.name 字符串，如 "a2h-understand-aippt"
//   __META_DESCRIPTION__  ''    meta.description 字符串（一句话：读什么、产什么）
//   __META_PHASES__       []    meta.phases 数组；首项 title 必须为 "Understand"
//                               （与下方 phase() 调用及 agent 的 phase 选项逐字一致）
//   __TASKS_JSON__        []    任务数组 [{key,label}]，来自 domain-map.json#domains[].{key,title}
//                               （split 域按 split 后的子键各成一条任务）
//   __PROMPTS_JSON__      {}    prompt 对象 {taskKey: promptString}，由 assemble_prompt.py 全量组装
//                               （①红线 ②契约 ③任务书含 android_files 清单与 spec 落盘路径
//                                ④契约段 ⑤规则片段 ⑥输出要求，全部在 prompt 字符串内）
//   __MAX_PARALLEL__      0     workflow-params.json#waves.understand.max_parallel；
//                               0 或缺省 = 单批全并发
//
// ── 沙箱事实（IMPL-CONTRACT §4，模板作者/改动者必读）─────────────────────────
//   无 fs / 无 Node API / 无 Date.now / 无 Math.random；
//   可用原语仅 agent / parallel / pipeline / phase / log / args / budget。
//   模板不落盘：spec 文件由读代理用 Write 工具写（目标路径在 prompt 内烤死）；
//   state.json 与汇总落盘由主循环在波尾依据本脚本返回值调 state_update.py 执行。
//   meta 必须是纯字面量：生成器直接文本替换填好，禁止任何运行期拼接。
//
// ── 返回值契约（主循环消费面）──────────────────────────────────────────────
//   { completed: string[]   // 成功任务键（StructuredOutput 非空）
//   , summaries: object[]   // 全量 StructuredOutput（SUMMARY_SCHEMA 形状），供 state_update.py/A3 消费
//   , missing:   string[] } // 缺失任务键：代理零产出（返回 null）或生成器漏配 prompt
//   missing 处置：recovery-playbook“代理零产出死亡”条目——重派或折叠进下一 wave，
//   state.json 记 folded_into；本模板只申报，不做任何补救动作。
//
// <!-- GAP(已解决): ac_candidates 条目形状已与 agent-output.schema.json understandSummary 对齐
//      （两态：字符串断言 / {assertion 必填, source_symbol?, on_device?} 对象；本模板 schema 常量
//      引导对象形态，required 仅 assertion）。 -->
// <!-- GAP(已解决): 替换单元边界（标记+默认字面量整串替换、JSON 槽全文件唯一）已由
//      generate_waves.py 按本表实现。 -->
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

// schema 常量直接写在模板里（IMPL-CONTRACT §4；对应 schemas/agent-output.schema.json 的 summary 子集）。
// = dynamic1 SUMMARY_SCHEMA 原样 + ac_candidates[]（3 册 §3.3）
//   + extraSpecFiles（split 大域多份 spec 申报通道，单份 ≤60KB 的分片纪律在 prompt 内）。
const SUMMARY_SCHEMA = {
  type: 'object',
  required: ['area', 'specFile', 'screens', 'apis', 'risks', 'ac_candidates'],
  properties: {
    area: { type: 'string', description: '任务键，与派发 label 的 <key> 一致' },
    specFile: { type: 'string', description: '落盘的域 spec 文件路径（多份时填首份主文件）' },
    extraSpecFiles: {
      type: 'array', items: { type: 'string' },
      description: 'split 大域的额外 spec 分片路径（无分片则省略或空数组）',
    },
    screens: { type: 'array', items: { type: 'string' }, description: '覆盖到的 screen/dialog/component 名' },
    apis: { type: 'array', items: { type: 'string' }, description: '发现的 API 端点（method + path）' },
    storageKeys: { type: 'array', items: { type: 'string' }, description: 'MMKV/SP/Room 等存储键（精确串）' },
    risks: {
      type: 'array', items: { type: 'string' },
      description: '无干净 HarmonyOS 等价物的点 + 建议处置',
    },
    crossRefs: {
      type: 'array', items: { type: 'string' },
      description: '对其他子系统的依赖（只读参考，不产生执行顺序）',
    },
    ac_candidates: {
      type: 'array',
      description: '验收断言候选——A3 生成 contracts.json#acceptance 的素材（3 册 §3.3）。'
        + '两态形态（agent-output.schema.json understandSummary 为准）：本 schema 引导对象形态；'
        + '纯字符串断言亦为下游合法输入（parse_agent_output.py 同步接受两态）',
      items: {
        type: 'object',
        required: ['assertion'],
        properties: {
          assertion: { type: 'string', description: '一句话可验收断言（行为/视觉，与 Android 对齐可核对）' },
          source_symbol: {
            type: 'string',
            description: 'Android 侧锚点符号（类.方法 或 布局元素），对应 acceptance[].anchor.source_symbol；'
              + '能锚定时必给（parity 锚素材）',
          },
          on_device: { type: 'boolean', description: '建议真机验证（缺省视为 false）' },
        },
      },
    },
  },
}

// 分批工具：MAX_PARALLEL<=0 或不小于任务数时单批全并发（dynamic1 的 13 路同秒 fan-out 形态）
function toBatches(list, size) {
  if (size <= 0 || size >= list.length) return [list]
  const batches = []
  for (let i = 0; i < list.length; i += size) batches.push(list.slice(i, i + size))
  return batches
}

phase('Understand')

if (TASKS.length === 0) {
  log('FATAL: TASKS 为空——生成器未填参或 domain-map 无域；返回空结果交由主循环阻断')
  return { completed: [], summaries: [], missing: [] }
}

// 生成器缺口自检：漏配 prompt 的任务不派发，直接计入 missing（确定性失败优于空 prompt 派发）
const dispatchable = TASKS.filter(t => typeof PROMPTS[t.key] === 'string' && PROMPTS[t.key].length > 0)
const promptless = TASKS
  .filter(t => !(typeof PROMPTS[t.key] === 'string' && PROMPTS[t.key].length > 0))
  .map(t => t.key)
if (promptless.length > 0) log('警告: 以下任务缺 prompt（生成器缺口），计入 missing: ' + promptless.join(', '))

log('理解波 fan-out: ' + dispatchable.length + ' 个域读代理'
  + (MAX_PARALLEL > 0 ? '，每批最多 ' + MAX_PARALLEL : '，单批全并发'))

const completed = []
const summaries = []
const missing = promptless.slice()

const batches = toBatches(dispatchable, MAX_PARALLEL)
for (let b = 0; b < batches.length; b++) {
  const batch = batches[b]
  if (batches.length > 1) log('批次 ' + (b + 1) + '/' + batches.length + ': ' + batch.map(t => t.key).join(', '))
  const results = await parallel(batch.map(t => () =>
    agent(PROMPTS[t.key], { label: 'read:' + t.key, phase: 'Understand', schema: SUMMARY_SCHEMA })
  ))
  // parallel 结果与入参同序（Promise.all 语义）；失败代理返回 null——
  // 按下标回配任务键（IMPL-CONTRACT §4：.filter(Boolean) 容错 + 缺失列入 missing）
  for (let i = 0; i < batch.length; i++) {
    const r = results[i]
    if (r) {
      completed.push(batch[i].key)
      summaries.push(r)
    } else {
      missing.push(batch[i].key)
    }
  }
}

log('理解波完成: ' + completed.length + '/' + TASKS.length + ' 成功'
  + (missing.length > 0 ? '；缺失: ' + missing.join(', ') : ''))
// 波尾主循环动作（本模板不落盘）：state_update.py 记任务态 → spec 文件存在性/尺寸核验 →
// missing 走 recovery-playbook（重派或折叠）→ 汇总 ac_candidates 供 A3。
return { completed: completed, summaries: summaries, missing: missing }
