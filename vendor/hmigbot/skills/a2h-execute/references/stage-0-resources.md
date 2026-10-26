<!-- when: a2h-execute SKILL.md §3.0 Stage 0 资源前置执行时加载 -->
<!-- topics: stage 0, resource conversion, [TODO: translate], placeholder-registry HARD-GATE, auto i18n -->

# Stage 0：资源前置（HARD-GATE，必须最先执行）

> Stage 1 转换页面时会引用 `$r('app.media.xxx')` 等资源，资源未就绪则页面编译/运行期失败——必须在 Stage 1 启动前完成资源迁移。

Stage 0 读取 `feature-plan.md` 的 Base-0 任务，执行资源全集扫描与批量迁移。

## §3.0a 执行流程

读 `plans/base-plan.md` Base-0（旧 plan 回退 feature-plan.md 旧 Phase 0 段）→ 扫 `spec/baseline/ui/page_*.md` + `features/F-*.md` + `feature-base.md` 全部 `$r('app.*.xxx')` / Lottie 资源名 / asset 引用，去重得资源 ID 全集 → 调 `android2hmos-resources-convert` 批量迁移，缺失资源写 `MISSING_xxx` 占位（编译期暴露）→ 产出 `spec/baseline/plans/resource-mapping.md` → **HARD-GATE**：全部引用可解析或显式 MISSING_xxx 才 PASS 进入 Stage 1，否则阻断 pipeline。

## §3.0a-bis 资源层占位登记 HARD-GATE

`android2hmos-resources-convert` 完成后，强制校验：每个 `[TODO: translate]` 占位与每个 fallback 资产引用必须在 `spec/placeholder-registry.md` 有对应 `kind=resource-pending-translation` / `kind=resource-pending-asset` 条目。任一不匹配即 BLOCKED，不允许进 Stage 1。

校验示例：

```bash
trans_count=$(grep -c '\[TODO: translate\]' entry/src/main/resources/*/element/*.json | awk -F: '{s+=$2} END{print s}')
registry_trans=$(grep -c 'kind=resource-pending-translation' spec/placeholder-registry.md)
test "$trans_count" -eq "$registry_trans" || exit 1
```

## §3.0b 自动调 arkts-i18n 完成翻译

若 `resource-pending-translation` 登记数 > 0，Stage 0 完成时主线程**自动调用** `arkts-i18n` skill 完成翻译，不需用户介入：

调用 `$arkts-i18n` skill（读取 `.agents/skills/arkts-i18n/SKILL.md` 并按其执行），参数：`task=translate-pending-todos source_locale=base target_locales=<auto-detect> registry=spec/placeholder-registry.md`

arkts-i18n skill 按其『硬编码字符串扫描与迁移』流程：扫 registry kind=resource-pending-translation → 借 LLM 为每个 locale 产真实翻译 → 落盘 `resources/<locale>/element/*.json` 替换 `[TODO: translate]` → 跑 `audit_i18n_completeness.sh` 验证 key 一致性 → 把对应 P-ID 的 registry status 更新为 `resolved`。

翻译完成后主线程继续 Stage 1。若 arkts-i18n skill 返回非 0（有 key_missing 等异常），写迁移报告 + 阻断 Stage 1。

## §3.0b-bis 落地 App 身份（dev 安全字段，无签名影响）

资源迁移后、进 Stage 1 前，主线程**自动调用** `arkts-app-identity`（**`scope=dev-identity`**）从 Android 源落地 App 身份，消除脚手架默认值（`app_name` 滞留 "MyApplication" / `versionName` 滞留 "1.0.0" 会卡真机识别与 a2h-verify App 身份校验项）：

```
调用 `$arkts-app-identity` skill（读取 `.agents/skills/arkts-app-identity/SKILL.md` 并按其执行），参数：`scope=dev-identity android_root=<$ANDROID_SRC> feature_base=spec/baseline/feature-base.md`

只写 dev 安全字段：`app_name`（label 文本）/ `versionName` / `versionCode` / 图标资源；**不碰 `bundleName` / `vendor`**——二者与签名 / AGC 强绑定属部署期 D-009，dev 阶段写入会致签名装机不一致（保留脚手架占位，部署期再以 `scope=full` 落地）。幂等、不覆盖无关字段。**非阻断**：身份字段非编译必需，`arkts-app-identity` 返回非 0 时写迁移报告 WARN 但不阻断 Stage 1。

## §3.0c 完成标志

报告：扫描 spec 文件数 / 引用资源 ID 数 / 已迁移数 / 显式 MISSING_xxx 数 / `resource-mapping.md` 路径 / 编译状态 / resource-pending-translation 登记数 / resource-pending-asset 登记数 / §3.0a-bis HARD-GATE 状态（FAIL 则阻断 Stage 1）/ arkts-i18n 翻译结果（若调用）。
