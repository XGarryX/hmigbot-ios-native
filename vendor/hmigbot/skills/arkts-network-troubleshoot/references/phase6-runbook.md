# Phase 6 HMOS 联调操作手册

> Phase 6 的展开。phases.md 讲「测什么 / 通过标准」，本文讲「HMOS 侧具体怎么操作」：
> 编译 → 签名 → 装包 → 冷启 → 过隐私门 → 抓 hilog → 与 Android 基线对账。
> Windows + git-bash 环境，所有 hdc 命令注意 MSYS 路径陷阱（见 grep-cheatsheet.md）。

## 0. 前置

- HMOS 模拟器 / 真机在线：`hdc list targets` 有输出。
- hdc 路径：`<DevEco>/sdk/default/openharmony/toolchains/hdc(.exe)`，不在 PATH 用全路径。
- 已知 HMOS bundleName（看 `AppScope/app.json5`）。

## 1. 编译出 HAP

用 `hmos-fix-build-errors` skill（自带编译 → 修错闭环），或直接 hvigor：

```bash
node "<DevEco>/tools/hvigor/bin/hvigorw.js" assembleHap --mode module -p module=entry --no-daemon
```

产物在 `entry/build/default/outputs/default/`。

## 2. 装包 —— 必须用 signed HAP

**模拟器 / 真机只接受签名 HAP**，`entry-default-unsigned.hap` 装不上（签名校验失败）。
DevEco 打开过项目会自动在 `build-profile.json5` 生成 debug 签名配置 → 编译同时产出
`entry-default-signed.hap`，装它：

```bash
cd entry/build/default/outputs/default        # 用相对路径，避免 MSYS 改写
hdc -t <target> install -r entry-default-signed.hap
```

无签名配置 → 用 `hmos-fix-build-errors --signed`，或在 DevEco
`File → Project Structure → Signing Configs` 勾「Automatically generate signature」。

## 3. 冷启 + 过隐私门

```bash
hdc -t <target> shell aa force-stop <bundle>
hdc -t <target> shell hilog -r                              # 清 hilog 缓冲
hdc -t <target> shell aa start -b <bundle> -a EntryAbility
```

**国产 App 冷启第一屏是隐私弹窗** —— 不点同意，启动网络链一条不发
（hilog 见 `initThirdSdk skip: ...AGREE... != 1`）。过门：

```bash
export MSYS_NO_PATHCONV=1
hdc -t <target> shell snapshot_display -f /data/local/tmp/s.jpeg
hdc -t <target> file recv /data/local/tmp/s.jpeg ./s.jpeg   # 读图定位「同意」按钮
# 注意截图分辨率 vs 显示缩放，换算真实像素坐标后：
hdc -t <target> shell uinput -T -c <x> <y>                  # 点「同意」
```

点完隐私门，startup 链（config / initUser / 首启上报）才会发出。

## 4. 抓 hilog

```bash
sleep 25                                                    # 等启动链发完
hdc -t <target> shell hilog -x > hmos_capture.log           # dump 后退出
grep -E 'HTTP >>>|HTTP <<<' hmos_capture.log                # 看请求 / 响应
```

前提：HMOS 端 HttpLogInterceptor 正常打日志（`AppStorage('isDebug')=true`，见 Phase 2.1），
且请求日志行带签名头摘要（见 [templates/code/http-client-unwrap.ets](templates/code/http-client-unwrap.ets)
末尾的 HttpLogInterceptor 模板）。hdc 无法脚本化挂代理 —— **HMOS 侧 hilog 是唯一可自动抓的通道**，
要对账 ss/tt 头就得在日志里打出来。

## 5. 与 Android 基线逐接口对账

| 启动接口 | HMOS 发出? | URL path | request body | response |
|---|---|---|---|---|
| /app/config | | 前缀一致? | 字段集 + 类型一致? | status/data 正确 unwrap? |
| /user/initUser | | | platformInfo 公参齐全? 签名一致? | token/userId 非空? |

差异 → 命中 pitfall → 回对应 Phase 闭环：

- HMOS 漏发某接口 → init 没跑（Phase 2 启动顺序 / 隐私门没过）
- URL 缺 `/user/` `/app/` 等前缀 → D2（Phase 1.1）
- body 少字段 / 类型错 → D3（Phase 1.2）
- 公参为空 / 字段值与 Android 不一致 → D4（Phase 1.5）—— 注意设备态对齐
- 后端 `-500` NPE（`Cannot invoke "...Enum.ordinal()"`）→ D4：先抓 Android `pm clear` 冷启基线逐字段对齐
- HTTP 200 但响应字段 undefined → D1（Phase 4 unwrap）
- 签名被拒（401）→ A 类（Phase 3）

## 常见卡点速查

| 现象 | 原因 | 处理 |
|---|---|---|
| `hdc file recv` 报 `realpath nullptr` / `file invalid` | git-bash MSYS 改写 `/device/path` | `export MSYS_NO_PATHCONV=1`（见 grep-cheatsheet.md） |
| 装包失败，提示签名校验 | 装了 unsigned HAP | 改装 `entry-default-signed.hap` |
| 冷启后无任何 HTTP 日志 | 隐私门没过 | 截图 + `uinput` 点同意（见第 3 步） |
| hilog 无 HttpLogInterceptor 输出 | `isDebug` 为 false | Phase 2.1 注入 `AppStorage('isDebug')=true` |
| 请求全失败 / 无网络 | 缺 `ohos.permission.INTERNET` | module.json5 加该权限 |
| 找不到 hvigor / hdc / DevEco | 工具链未在 PATH | DevEco 装在 `<盘>/DevEco Studio x.x.x`；hdc 在 `<DevEco>/sdk/default/openharmony/toolchains/` |
