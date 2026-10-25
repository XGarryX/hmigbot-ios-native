> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# Step 4.1.4 — H5 / WebView 页面验证（`capture_mode == "web"` 专用）

> 从 SKILL.md §4 Step 4.1.4 抽出。`capture_mode == "web"` 时 Read。
>
> **核心思路**：H5 页面视觉由远端 url + query 决定，原生侧只是 Web 容器。对 H5 做整图像素 diff **没有意义**——两端 WebView 内核渲染差异（字体回退、滚动条粗细、安全区、默认字号）会产生大量假阳性；而真正的跨端一致性证据是「最终渲染的是不是同一个 url + 同一份参数」。
>
> 所以 H5 页走**三段式验证**：① URL 断言（真实一致性证据）② 原生外壳视觉 diff（标题栏/返回/loading/错误态）③ WebView 视口**屏蔽**（不进 diff）。

---

## 2.1.4-a 提取两端最终加载的 URL

不能只看源码里的字符串常量——真实 url 是运行时拼接的 base + path + query。**必须从运行态抓取**：

| 端 | 抓取方法 |
|----|---------|
| HarmonyOS | ① 代码里 `Web({ src: this.url })` → 读取 `this.url` 状态：用 `hdc shell hidumper -s WebView` 或给页面加一次性 `getUrl()` 日志 → `hdc hilog` 输出里搜该日志；② 或在 ets 构造 Web 前注入 `console.info('VV_URL ' + src)`，先 `hdc hilog -r` 清缓冲，再 `hdc hilog` 输出里搜 `VV_URL`（bash 可 `\| grep`，PowerShell 用 `Select-String`，或 python 一行式过滤）|
| iOS | `adb shell dumpsys activity top` 输出里搜 `mUrl`/`loadUrl`；或 `adb logcat -d` 输出里搜 `WebView.*loadUrl`（过滤用 grep / Select-String / python 均可）；或用 `uiautomator dump` 若 WebView 节点暴露了 url 属性直接读。**以上全失败时最稳的一招（2026-07-11 AIPPT 实证，dumpsys/logcat 均无 URL 时 CDP 拿到了）**：WebView debuggable 的 app 走 Chrome DevTools 协议——`adb shell "cat /proc/net/unix"` 输出里搜 `webview_devtools`，找到 `webview_devtools_remote_<pid>` → `adb forward tcp:9222 localabstract:webview_devtools_remote_<pid>` → `curl -s localhost:9222/json`（或 `python3 -c "import urllib.request;print(urllib.request.urlopen('http://localhost:9222/json').read().decode())"`）返回每个 WebView 的 url+title（用完 `adb forward --remove`）|

抓取失败（动态 url + 无日志）→ 降级：直接对比两端 ets / Activity 源码里的 url 表达式 + 路由参数传递链路，不进视觉 diff。

---

## 2.1.4-b URL 一致性断言

解析两端抓到的 url（用 `urllib.parse`）后按以下规则比对：

```
origin + path  必须完全一致
query params   key 集合必须一致；value 按白名单忽略：
                - 忽略：timestamp / ts / nonce / _t / traceId / deviceId / uuid
                - 必须一致：业务字段（id / type / from / lang / theme）
fragment (#)   必须一致
```

任一失败 → 写入 `differences[]`：
```json
{
  "category": "web_url_mismatch",
  "severity": "high",
  "is_migration_bug": true,
  "ios_url": "...",
  "hmos_url": "...",
  "diff": ["path", "query.lang", "query.from"],
  "fix_hint": "url 拼接处可能缺 lang/from 参数（仅作 fixer 参考，由 fixer 读源核实）"
}
```

这是 H5 跨端一致性的**真实证据**，替代「看起来一样」的视觉判断。

---

## 2.1.4-c 原生外壳视觉 diff（WebView 视口屏蔽）

视觉对比只跑**原生容器**，不跑 Web 内容：

1. 从 `uitest dumpLayout` / `uiautomator dump` 读出 `Web` 组件（HMOS）或 `WebView` 节点（iOS）的 `bounds`（left, top, right, bottom）。
2. 两端截图按各自 `bounds` 把 WebView 矩形**覆盖为纯黑**（`cv2.rectangle(img, (l,t), (r,b), (0,0,0), -1)`），保留顶部标题栏 / 底部 tab / loading / 错误态等原生外壳。
3. 屏蔽后的两张图走 `compose_side_by_side.py` 生成 sbs，喂多模态按 Step 4.2 的 9 项分析——但在 prompt 里加一句「黑色区域为 WebView 视口已屏蔽，不要报告该区域内差异」。
4. 多模态找到的差异只保留 `is_native_shell: true` 的项；WebView 视口内的误报直接丢弃。

---

## 2.1.4-d 加载态覆盖检查（强制 — loaded + error 两态必跑，loading 态可选）

<HARD-GATE>

H5 页面的 `loaded` 态和 `error` 态**必须**各跑一次，两端独立抓外壳 + URL，差异按态归类。理由：iOS 源端 WebView 通常自带兜底错误页（断网/load failed），HMOS Web 组件**默认行为可能白屏 / 不一致**，这是真实迁移 bug 的高发区，不可省。

`loading` 态保留为可选——大多数静态 H5 瞬间 loaded，跑 loading 截图性价比不高；只有当 sub-agent 明确判断"该页加载慢"（首屏延迟 > 1s）时才扩展。

</HARD-GATE>

| 态 | 触发方法 | 是否强制 | 预期 |
|----|---------|------|------|
| loading | 页面打开后立即截图（页面进入 ≤200ms 内） | ⏭️ 可选（仅加载慢页） | 两端都显示 loading 或占位骨架 |
| **loaded** | 等 `onPageEnd` / `onPageFinished` 后截图（HMOS 监听 `OnPageEnd` 事件，iOS 用 `WebViewClient.onPageFinished`） | ✅ **强制** | 两端 url 一致 + 原生外壳 visual diff |
| **error** | 断网后截图：`hdc shell svc wifi disable` / `adb shell svc wifi disable` ；截完恢复网络 `svc wifi enable` | ✅ **强制** | 两端都走错误页（关键看 HMOS 是否白屏 / 是否有兜底错误提示） |

### 错误态实施细则

1. 跑顺序固定为 `loaded → error`（不要先 error，否则 loaded 态可能拿不到 url）
2. 进入 error 态前确保 WebView 已加载过一次（loaded 态截完）
3. 断网命令：
   - HMOS: `hdc shell svc wifi disable` 或 `hdc shell power-shell ui-control set airplane-mode 1`（airplane mode 更彻底）
   - iOS: `adb -s {device} shell svc wifi disable` 再 `adb -s {device} shell svc data disable`
4. 断网后 `am start` / `aa start` 再次启动该 WebView 页面（force-stop → 冷启动让 WebView 走加载流程），等 5 秒让加载失败发生
5. 截图两端，diff
6. **恢复网络**（重要，避免污染后续 batch）：
   - HMOS: `hdc shell svc wifi enable` 或 `hdc shell power-shell ui-control set airplane-mode 0`
   - iOS: `adb shell svc wifi enable` 再 `adb shell svc data enable`
7. 等 wifi 上线（轮询 `connectivity check` 或简单 sleep 5）后才能跑下一个 batch

### error 态差异分类

| 现象 | category | severity |
|---|---|---|
| iOS 显示兜底错误页（如"加载失败,点击重试" + reload 按钮），HMOS 白屏 | `web_error_page_missing_hmos` | P0 |
| 两端都有错误页但文案/样式不一致 | `web_error_page_drift` | P1 |
| HMOS 直接崩溃 / native error (e.g. ARK 抛 ECMA error) | `web_error_crash_hmos` | P0 + CRASH md |
| 两端都白屏（iOS 也没兜底页） | `web_error_uniform_blank` | P2（iOS 源端的设计选择，HMOS 一致即可） |

### 断网态截图独立保存

```
spec/visual-verify/screenshots/{side}/round-N/
  {page_id}.jpeg              # loaded 态（主图）
  {page_id}_error.jpeg        # error 态（断网截图）
  {page_id}_loading.jpeg      # loading 态（可选）
```

sbs 合成对应：
```
spec/visual-verify/screenshots/sbs/round-N/{trip_id}/
  {page_id}.jpeg              # loaded sbs
  {page_id}_error.jpeg        # error sbs
```

写 markdown 时 evidence 段同时列两态：
```yaml
evidence:
  - spec/visual-verify/screenshots/sbs/round-N/{trip_id}/{page_id}.jpeg          # loaded
  - spec/visual-verify/screenshots/sbs/round-N/{trip_id}/{page_id}_error.jpeg    # error
```

**降级允许**：如果断网命令在某模拟器上失效（`svc wifi disable` 返回 error）→ 标 `error_state_unverified: env_no_wifi_control`，仍写 markdown 但归 `manual_review`，不阻塞 batch。但同 batch 内 ≥2 个 WebView 页都标 env_no_wifi_control → 主会话需在 Phase 6 报告中升级警告。

---

## 2.1.4-e 产物与降级

```
spec/visual-verify/screenshots/{side}/
  {page_id}.png                  # 原图（外壳 + WebView）
  {page_id}_masked.png           # WebView 屏蔽后的图，进 diff 用
  {page_id}_web.json             # { "url": "...", "parsed": {...}, "webview_bounds": [...] }
```

降级路径：
- 2.1.4-a url 抓取失败 + 2.1.4-c dumpLayout 也拿不到 WebView bounds → 标 `capture_mode: "web_fallback"`，**完全跳过视觉 diff**，只输出源码层面的 url 表达式对比结果，在报告里写明「H5 页面已跨端，视觉差异不纳入 bug 判定」。
- url 完全一致但原生外壳有 high 差异 → 照常走 Step 4.3 分类 + Step 4.4 写 ALIGN_*.md（外壳 bug 和 H5 无关）。
