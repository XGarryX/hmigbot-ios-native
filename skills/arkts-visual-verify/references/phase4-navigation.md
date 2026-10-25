> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# Step 4.0 — 导航到目标页面 + Step 4.0.a 启动弹窗速关

> 从 SKILL.md §4 Step 4.0 / 2.0.a 抽出。sub-agent 进入目标页前 Read。

---

## Step 4.0: 导航到目标页面（导航链路模式）

采用从首页逐步导航的方式到达目标页面，而非直接跳转。这种方式同时验证了导航链路的正确性。

冷启动 → 多模态/uitest 看顶层是否有启动弹窗 → **查 dismissal recipe cache**（见 Step 4.0.a）→ 命中则一步关掉、miss 则进探索模式且把成功招式写回 cache → 到达目标页面。

### iOS 源端导航（★单侧化 2026-07-12：Phase 4 常规流程**不驱动iOS**——本节仅
gate_experiment 兜底对照 / 手工排查时参考，sub-agent 禁在 batch 内执行本节命令）

```text
# 强制停止 App，排除进程残留（保留登录态/sharedPrefs；reset_app 用 pm clear 见 §dispatch）
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {device} shell am force-stop {package}
sleep 1

# 重新冷启动到主入口
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {device} shell am start -n "{package}/{launcher_activity}" -W
sleep 5  # 等待 Splash + 初始化完成

# 关启动弹窗（见 Step 4.0.a，最多 5 次）
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/dismiss_popups.py \
  --device {device} --platform ios \
  --catalog spec/visual-verify/dialog_id_catalog.json \
  --max-iter 5
# ↑ 用 --catalog（脚本不认 --target-activity）。exit 3=catalog 缺失 / exit 2=仍有 modal，需 check。

# 按导航路径逐步点击到达目标页面
# 坐标从 dumpsys 或 uiautomator dump 获取
```

### HarmonyOS 端导航（导航链路模式）

```text
# 强制停止 App（仅 kill 进程，保留登录态/PreferenceUtil；reset_app 用 bm clean -d 见 §dispatch）
hdc shell aa force-stop {bundleName}
sleep 1

# 冷启动到主入口
hdc shell aa start -a EntryAbility -b {bundleName}
sleep 9  # 等待 Splash 消失（根据 splash_wait_seconds 配置）

# 关启动弹窗：dismiss_popups.py 是 iOS 专属（catalog 由 iOS res/layout 抽取，
# 且脚本对 platform!=ios 直接 exit 3）。HMOS 端无 catalog 机制——启动弹窗由 sub-agent
# 在导航逻辑里用同样的"通用关闭阶梯"思路手动处理（文本/角标/BACK），或后续补 HMOS 版 catalog。
# 不要在 HMOS 调 dismiss_popups.py（会直接报错）。

# Step 4.0.5: 布局分析 — 获取精确坐标（必选）
hdc shell uitest dumpLayout
# 解析返回的 layout JSON，提取目标元素的 bounds
# 计算中心点坐标 = ((left + right) / 2, (top + bottom) / 2)
# ⚠️ 禁止使用目测坐标，必须从 dumpLayout 获取

# 按导航路径逐步点击到达目标页面
# 示例：首页 → 我的 tab → 设置图标 → 目标设置子页
hdc shell uitest uiInput click {tab_x} {tab_y}        # 切换 tab
sleep 1
hdc shell uitest dumpLayout                              # 重新获取布局
# 解析新布局，获取下一个点击目标的坐标
hdc shell uitest uiInput click {target_x} {target_y}   # 点击目标
sleep 2
```

### 导航路径确定规则

```
1. 从 toolkit-fact-tree.json 读取页面所属功能域和导航关系
2. 确定从首页到目标页面的最短导航路径
3. 常见路径模式:
   - 首页工具格子 → 功能页: 点击对应工具图标
   - 我的页子页: tab切换到"我的" → 点击对应入口
   - 设置子页: 我的 → 设置图标 → 点击对应设置项
   - 详情页: 先导航到列表页 → 点击某一项（data_dependent 页面通常跳过）
4. 每次导航前必须执行 dumpLayout 获取精确坐标
```

### 返回键

```text
# HarmonyOS 返回键
hdc shell uitest uiInput keyEvent Back

# iOS 返回键
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell input keyevent KEYCODE_BACK
```

---

## Step 4.0.a: 启动弹窗速关 cache

> 冷启动后常弹广告 / 协议 / 更新等。把"点哪个坐标能关掉"记在 `spec/visual-verify/cache/dismissals.json`，下次遇到同款直接复用，**不重新摸索**。

### 文件格式（单文件，平铺数组）

```jsonc
// spec/visual-verify/cache/dismissals.json
{
  "entries": [
    {
      "signature": "<截图 dHash 或顶层文字 hash>",
      "click_x": 990,
      "click_y": 480,
      "success_count": 3,
      "platform": "ios"          // "ios" | "harmonyos"
    },
    {
      "signature": "...",
      "click_x": 540,
      "click_y": 1820,
      "success_count": 1,
      "platform": "harmonyos"
    }
  ]
}
```

### dismiss 循环（替代旧的盲 BACK 5 次）

```
冷启动 → 循环最多 5 次：
  1. 截图 / dump 顶层 → 算 signature
  2. 已在目标 activity/ability → 退出 (exit 0)
  3. 查 dismissals.json：
     ├─ 命中 → 点 (click_x, click_y), success_count++ 落盘
     └─ miss → 在当前 UI 找候选按钮（id/text 含 close/skip/cancel/exit/agree/同意/跳过/暂不/我知道了/稍后）
                按优先级点：close > skip > later > cancel > confirm/agree
                点完顶层变了 → 把 (signature, x, y) 写回 dismissals.json
                点完没变化 / 没候选 → BACK 兜底
  
5 次仍未到达 → exit 2 → 调用方按 alignment-rules.md §3 升级用户
```

### signature 怎么算

- 优先：把当前截图缩到 64×64，灰度差分 hash（dHash），输出 16 位 hex
- 兜底：取 dumpLayout 前 3 行可见 text 拼接后 sha1[:16]

两端共用一份 dismissals.json，`platform` 字段做区分。iOS 截图缓存的 `app_fingerprint` 变化时**不影响本 cache**——signature 不依赖版本号，只依赖弹窗视觉特征。
