# 破坏性组件:遭遇记账 → 末尾读 handler → 末尾真验(trip-end 三段式)

> **v2(2026-07-25 用户拍板重构)**:破坏性组件的验证从「编译期预读全部 handler 定档」改成
> **「遍历时遇到才记,trip 结尾统一读、统一验」**——由已实测的资金收尾趟机制推广到全部破坏性。
> 决定"某破坏性功能点能不能在共享账号上安全 probe"的**唯一依据**仍是鸿蒙 handler 是否"点击即弹二次确认模态窗"
> ——不是iOS有没有弹窗(iOS有弹窗≠鸿蒙有,后者正是要验的迁移点)。**读不准=保守当"点即执行"不点。**

## 为什么改(v1 的三个病)
1. **预读全部低效**:树里破坏性个位数到几十个,但其中大量**根本不渲染**(未实装的 no-op 入口、VIP/态门控),
   为它们读 handler 是纯浪费。实测某轮:计划 15 个破坏性 → 真渲染只有 5 个。
2. **hprof 会过期**(审核 MAJOR 长期未修):编译前产的静态档,源码一变即失效,且无人校验。
3. **两套机制**:非资金走编译期 safe_probe、资金走 fund_probe_trip_end,并行维护易漂移。

改后:hprof 从"编译前静态档"变成**"本轮现产的派生物"**,过期问题结构性消失;两套机制并成一套。

## 三段式流程

```
① 编译期(零 hprof 依赖)
   compile_replay_plan.py   # 不再需要 --hmos-profile
   破坏性 functional_checks / dialog_edge 一律标 {defer_to_trip_end:true, is_fund:<词表判>}
   （is_fund 用 _FUND_RE 词表:退款/退订/取消订阅/解约/注销/提现/充值/关闭续费——确定性,零源码依赖）

② 正常趟(0-LLM 机械回放)
   replay_exec.py           # 不带 --trip-end-pass
   遇到 defer 元素 → **定位但绝不点**:
     定位到  → outcome=encountered_destructive + 存屏证据 → 入 encountered_destructive.json
     没定位到 → outcome=destructive_not_rendered + 附 page_text_hints → 也入账(标 located:false)
   ★ 未定位≠一定没渲染,也可能树名≠屏名(鸿蒙 dump 无 rid 只能文本匹配)——所以仍入账,
     由 ③ 读 handler 时顺带解出屏名(hmos_label),④ 再精确定位。宁可多读一条,不可静默丢覆盖。

③ trip 末尾:读 handler(唯一的 LLM 步,一次批读)
   输入 = encountered_destructive.json(**只含本轮真遇到的**,不是全树)
   对每条:grep 鸿蒙 ArkTS 源码定位该控件 onClick → 读 handler 体判"点击后第一步行为" →
   产本轮 hmos_destructive_profile.json(schema 见下)。读不到/读不准 → **不写该条**(缺省=保守不点)。

④ trip 末尾:真验(机械)
   trip_end_slice.py --plan --encountered --hprof --out   # 三重收窄裁最小走序
   replay_exec.py --trip-end-pass --hmos-profile <本轮hprof>
   执行器**运行时再分层一次**(不信裁剪器一家):
     is_fund + 无确认门         → 永不点(fund_no_modal_never_tap)
     hmos_shows_modal==true     → safe_probe:tap→**必须 modal_type() 检出真模态**→白名单点取消→BACK
     direct_harmless + 非资金非支付 → 普通 tap 真验(如清缓存 toast)
     其余(读不准/点即执行)     → 永不点,记未验证
```

## 三重收窄(读码量与走路量塌缩的来源)
```
计划里的破坏性            15
 → ②遭遇且定位到(渲染实证)  5    ← 未实装 no-op 入口 / VIP·态门控 自动出局
 → ③hprof 判可安全验        3    ← 资金无确认门 / 点即执行 / 读不准 一律不走
 → ④走序 168 步 → 6 步
```
被挡在走序外的**不是被静默跳过**:它们在判读侧全部落 `unverified_destructive` 强制报缺桩(见下)。

## schema(hmos_destructive_profile.json,本轮现产)
```jsonc
{
  // 键:功能点 name;或 "@anchor:<rid>"(名字漂移时按 anchor 命中)
  "退出登录": {"hmos_shows_modal": true, "cancel_label": "取消", "hmos_label": "退出登录",
             "handler_ref": "pages/AccountInfoPage.ets:65 showLogoutDialog"},
  "清除缓存": {"direct_harmless": true, "hmos_label": "清除缓存",
             "handler_ref": "viewmodels/MineViewModel.ets:53 clearCache→toast「已清除缓存」,无确认窗"},
  "快速退款": {"hmos_shows_modal": false, "hmos_label": "一键退款",
             "handler_ref": "components/MineTabComponent.ets:309 onClick 为 no-op,确认弹窗 UI 未实装(GAP-5)"}
}
```
- **`hmos_label` 是必填项之一**:鸿蒙 dump 无 rid,执行器只能文本匹配;树名常≠屏名
  (实测「快速退款」↔屏上「一键退款」)。读 handler 时顺带把渲染该控件的字面量文案读出来。
- `handler_ref` 附文件:行 + 方法名,可审计。

## 安全铁律
- **确定/确认/是 键两端永不点**(共享账号真扣款/真退订/真注销不可逆);
- **支付类硬闸**:名字/rid 命中 `支付|开通|续费|购买|充值|下单|pay|purchase` 的,
  **哪怕 hprof 误标 direct_harmless 也绝不真点**——零信任 profile 的兜底;
- 资金不可逆(退款/退订/注销/提现)**无确认门一律不点**;有确认门才允许"到弹窗即止+白名单取消";
- 执行器 safe_probe **不信编译/裁剪一家**:tap 后必须 `modal_type()` 检出真模态,
  没有 → `destructive_no_modal_SAFETY` 立即中止本页(可能是"缺二次确认"也可能是"点即执行",两解并列交人工);
  弹窗含结果词(成功/已提交/已退…)→ `result_dialog_SAFETY`(疑似执行后窗)同样中止;
- **SAFETY break 零静默缺口**:中止时本页后续元素记 `skipped_after_safety_break` 进判读闸;
- 读不准一律保守不点;profile 是每 app 数据,住工程侧,不进执行器代码(零 app 常量)。

## 判读侧(build_judge_input 机械闸)
下列 outcome/状态一律落 `unverified_destructive` 强制报缺桩,judge **必出单不得判 PASS**:
`skipped_destructive_unverified` / `destructive_no_modal_SAFETY` / `result_dialog_SAFETY` /
`skipped_after_safety_break` / **`encountered_destructive`**(遭遇未验) /
**`destructive_not_rendered`**(★控件压根没渲染——iOS有真值而鸿蒙不渲染 = 功能缺失,是真问题单) /
capture_status ∈ `pruned_unverified` / `deferred_trip_end`。
