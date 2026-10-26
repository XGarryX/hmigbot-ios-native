# a2h-execute · runbook 各条规则的实证记录（按节分组）

> 本文件收纳 M1 减量时从 `SKILL.md` runbook 保留文本中摘出的实证/事故叙述；规则本身仍在 runbook，此处只是证据。被整段搬到 `runbook-*.md` 的章节（§5/§6/§7/§7b、产物写权 E24、回执可信 830、构建纪律、条件波、机制 bullet）的实证随原文留在各自文件内。读取时机：想核对某条规则背后的实证时；不改变任何动作。

## §1 前置自检（E19）

- `host_parallel_check.py`：上限低于计划 max_parallel 时超出的子代理会静默挂住。
- 四拍之外的原生子代理与窗口共用同一宿主额度（E19）：a2h-spec 的 api-inventory 后台代理、主会话同期清单里派出的任何 agent 都占线程；计划并行度 = 宿主上限 − `gates.side_agent_reserve`（缺省 1）——超了就是 test1 那种「在飞零产出」。

## §2 四拍循环

- E199（拍④⑤合一）：AIPPT_930 主会话 land_results 196 次 + next_batch 222 次，每次请求重发约 27 万上下文。
- `wait` 行「禁止等整批全部回来才落账」：AIPPT-v4 实证：整批等待 + 缺 result 误判让 18 域切成三波 61 分钟。
- `wait` 行 E50（stale 只列不判）：AIPPT_0903 test4 实证（2026-09-05 01:48–03:29）：宿主休眠 1h41m，主会话与 3 个 closure 代理同时冻结，醒来后阈值把 2 个正要回执的存活代理判 RETRY_NEEDED 重派。
- `next` 行（V21 `next.cmd` 同一条消息里紧接着执行）：v5 实证主线落账 8 次没接拍①，3 域白等 9.5 分钟。
- 错峰派发 E34：同一分钟起跑 11 个代理各读 15 万 token 是 429 的直接原因，回执驱动的逐个补位从未撞限。E80：AIPPT_0903 r3 实证：11 槽只跑 4 个，9 分钟一轮。`wait_agent` 超时设成 `retry_after_sec`：r4 实证：提示给了，主会话仍连续 wait 7 分钟、4 槽空转。E133：AIPPT 2026-09-06 16:13–16:54 实证：11 槽只跑 4 个、四批派发间隔 11/8/22 分钟。
- 契约接线 I5：AIPPT_0903 实证：wires=0 时接线率被探针托到 1.13，实际 38 处 startActivity 只接了 5 处、运行白屏。
- 修复类侧代理只能零在途时派：并发改同一文件必互相覆盖（AIPPT_0903 2026-09-05：builder 与 closure converter 同时改 MemberCenterBody.ets，修好的 19 错下一拍回魂）。
- E47 审批文件：AIPPT_0903 test4 实证（2026-09-04 17:15）：fix-backlog 13 条 open / 7 条 P0 待批，主会话自写 approved:true by:user，随后 escalated-ratio 红灯被它当作可跳过的障碍。
- E115 unattended_runner：AIPPT r6 实证：两次满载崩溃的恢复此前全靠人手。
- E139/E139b repair 次数：AIPPT 2026-09-06：每轮 repair 都把错误压到 1 条然后记账，最后那条永远没人修。
- E138 资源引用回填：编译门此前被『Unknown resource name』刷屏（wiring 波 212 错里 167 条）。
- E140 闭包类级覆盖：此前 rescan 只看 detector，非 UI 137/212 也能判『收敛』直接 closeout。
- E46 前波 ERROR：同一实证：主会话跳过 escalated-ratio 升级直接生成 wiring 波，遇「owner app-entry 无白名单」又改了 `spec/blueprint/ownership.json`，auditfix / closeout 两份 plan 契约哈希随即失配。
- E41 拍①不可重复调用：AIPPT_0903 test4 实证（2026-09-04 20:47:51 拍① 得 p1–p4 → 未 spawn → 20:49:03 又拍① 得 p5–p8 只 spawn 后者）：p1–p4 空等 40 分钟后按缺失重派，attempts 直接到 2。
- 四条拒绝规则（非终态未落账拒吐新批 / hash 不一致拒续跑 / 待审批出 approval / 重试超限出 escalate）使「跳过落账」在机制上不可能——拍①④两条命令不跑则无法推进。

## §3 派发纪律

- 任务书正文不进主会话上下文（V20）：AIPPT-v4 实证：逐个 cat 100KB 任务书派发耗 0.6 分钟/个，缓存读占成本 46%。
- K7 `--infra-fail`（不再把回执写成占位文件）：v5 实证占位文件在重派后被重复扫成 INFRA_FAIL 四次、误触 health_probe。
- E38 每一条回执到达即跑拍④→拍①：AIPPT_0903 test4 实证（2026-09-04 20:00–20:25）：主会话按「批」等最后一个回执，在途从 4 空转到 0 才补 4，窗口 11 从未填满，批间空窗 4–10 分钟。
- V21 重派前先确认代理已终止（§15-4）：v5 实证：8 个「重派」任务原代理还活着，重派 = 双倍付费 + 两份半成品。
- V21 主会话不写检查脚本：v5 execute 期 98 段手写 python、176 次二次加工。
- `contract_hash` 不对 contracts.json 实时重算：v5 实证主线误以为改契约会撞门，绕路修复。
- 孤儿/接线任务按 owner 切分：v5：49 个孤儿一个代理两次撞 80 轮上限、382k token 无报告。
