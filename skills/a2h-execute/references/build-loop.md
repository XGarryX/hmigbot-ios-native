<!-- when: 编译检查点派发 hmos-builder agent + placeholder 回填时加载 -->
<!-- topics: 编译闭环, hmos-builder agent, placeholder 回填, trigger 白名单 6 类, 升级诊断, 构建操作纪律 -->

# 编译修复流程细节

body 只留四句：派发 Codex 子代理 `hmos-builder`（定义于 `.codex/agents/hmos-builder.toml`；最多 20 轮）→ agent 返回结构化报告（PASS/FAIL）→ PASS 后主线程按 trigger 白名单回填 placeholder → FAIL 时调 arkts-knowledge-verifier 升级诊断。完整流程图与 trigger 6 类判定在此。

```
派发子代理 hmos-builder（CALLER=<上游>, STAGE_HINT=<阶段>, ROUND=<轮次>）
  │
  ├─ agent 内部：build-fix 循环（最多 20 轮，构建日志全部留在 agent context）
  │
  ├─ agent 返回结构化报告（BUILD_STATUS / ITERATIONS / FILES_CHANGED / [PASS]HAP_OUTPUT / [FAIL]REMAINING_ERRORS+DIAGNOSIS）
  │
  ├─ [可选] 本轮 ERRORS_FIXED_TOTAL >= 5 时:
  │   ├─ 主线程调用 a2h-retrospect --incremental
  │   ├─ 分析本轮错误模式
  │   ├─ 新模式写入 skill references
  │   └─ 后续 task 立即受益
  │
  ├─ BUILD_STATUS=PASS → 主线程执行占位符回填:
  │   ├─ 读取 spec/placeholder-registry.md
  │   ├─ 对每个 status=pending 的条目:
  │   │   ├─ 解析 trigger_condition 自动判定（白名单 7 类）:
  │   │   │   ├─ `D-{N} chosen`           → grep "D-{N}.*chosen" spec/migration-decisions.md
  │   │   │   ├─ `<file-path> 实现 <symbol>` → grep -n "<symbol>" <file-path>
  │   │   │   ├─ `<业务类别> SDK 入仓`     → 按 trigger 实际指定的检测方式查（新 skill 入仓 / 私仓 har / 官方适配文档 / 团队决策记录等任一形式满足即可）
  │   │   │   ├─ `<api-endpoint> 上线`     → grep "<api-endpoint>" entry/src/main/ets/network/
  │   │   │   ├─ `<resource-id> 就绪`      → grep "<resource-id>" entry/src/main/resources/（同时覆盖 resource-pending-asset：fallback 资产被真实资产替换后命中）
  │   │   │   ├─ `Slice {N} Step {3c|3d}`  → `kind=forward-ref` 专用：检测 location 文件已无 `// FWD-REF:` marker（即接线已完成）
  │   │   │   └─ `Slice {N} Step 3a 确认`  → `kind=forward-ref-uncertain` 专用：Slice N Step 3a worker 报告 `uncertain_regions_resolved[]` 含本 P-ID（execute 主线程更新 status）
  │   │   ├─ trigger 命中 → status: pending → due，发出 hilog warning + 写迁移报告
  │   │   ├─ trigger 未命中 → status 维持 pending
  │   │   ├─ status=due 时尝试回填: 目标已实现 → 回填真实代码 + status → resolved
  │   │   └─ 回填失败（仍找不到实现） → status: due → fired，记入告警清单
  │   └─ 回填后如有代码变更 → 再次派发 hmos-builder（ROUND+=1）验证
  │
  ├─ BUILD_STATUS=PASS + 回填完成 → SUCCESS
  │
  └─ BUILD_STATUS=FAIL（20 轮仍失败） → 升级处理:
      ├─ 主线程读 agent 返回的 REMAINING_ERRORS + DIAGNOSIS → 调 arkts-knowledge-verifier 诊断
      ├─ verifier 给出 patch 建议 → 主线程派 worker（按 fixer_layer 分轨）应用 patch
      ├─ 再次派发 hmos-builder（ROUND+=1） → 编译通过 → SUCCESS
      └─ 仍失败 → 标记 FAILED（按调用方阶段规则处理）
```

---

## 构建操作纪律（hmos-fix-build-errors / hmos-builder / group-closer 的任何构建 subagent 必须遵守）

### Cache Cleanliness

- 首编后所有构建默认**增量**（热 daemon、不 clean）；仅命中腐坏征兆（<1s 空退 / 00303208×2）按 hmos-fix-build-errors 安全阀 `--stop-daemon` 处置。
- `hvigorw clean` 最多执行 **1 次**。禁止 `rm -rf entry/build`（会破坏 hvigor daemon 增量状态）。
- `ohpm install` 只在构建循环开始前执行一次，不在循环内部重复执行。

### Checkpoint 提交

- 每次 `BUILD SUCCESSFUL` 之后必须立刻 `git commit`，提交消息格式：`checkpoint(base-N): build pass after K fixes`。
- 若 linter 回改导致文件变更，用 `git checkout -- <file>` 恢复而非重新编辑。

### CLI 构建降级策略

出现以下情况时禁止继续 CLI 构建，必须**升级到 IDE 构建**：
- `hvigorw` 在 <1 秒内退出且无编译错误行 → Daemon 僵死，重试 1 次后仍失败则升级
- SDK 路径错误 `00303208`/`00303217` 连续出现 2 次 → 升级
- `module.json5` 语法损坏（`00305008`）连续出现 2 次 → 升级且禁止手动修改 module.json5
- 单个文件被 linter 回改超过 3 次 → 升级，由 IDE 环境验证最终状态

### 降级时输出

```
构建环境已不稳定，无法继续 CLI 构建验证。
请在 DevEco Studio IDE 中 Build → Build HAP(s) 验证项目完整性。
```
