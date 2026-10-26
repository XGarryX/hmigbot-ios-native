#!/bin/bash
# cold_start_probe.sh — 冷启冒烟探针（能力交付契约第③层，60 秒）
# 主判据（二值机械）：①冷启不 crash ②首个网络请求出网。文案 grep 仅附加证据。
# 用法: cold_start_probe.sh <bundleName> [ability=EntryAbility] [wait=8]
# E172（AIPPT_930 移植）：①原始证据落盘 $A2H_COLD_EVIDENCE_DIR（targets/force-stop/hilog/ps/dump）；②hdc shell 对远端
#   命令失败仍 exit 0——hilog 回「Invalid log type [CODE:-3]」/Usage 之类时按 EVIDENCE_LOST 判 FAIL，不能拿零日志当无崩溃；
#   ③网络判据只数本应用进程（hilog -P <pid>）的网络栈日志——别的应用出网不能替本应用过闸；④多设备按 A2H_HDC_TARGET 选靶。
#   AIPPT_930 closeout 实证：冷启存活但 hilog 无有效原文，旧探针照样往下判。
set -u
BUNDLE=${1:?bundleName required}; ABILITY=${2:-EntryAbility}; WAIT=${3:-8}
# E254：命令自身报错的守卫只看「非日志行」且只看输出开头——hilog 转储正文里应用 / 系统日志带 Invalid、Usage: 字样很常见
# （ds closeout 冷启闸：hilog-all 里 3 行无害日志触发 EVIDENCE_LOST）；命令失败时 hilog 不出任何日志、报错在最前面几行
LOGLINE='^[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+'
cmd_err() { head -n 5 "$1" | grep -vE "$LOGLINE" | grep -qiE "$2"; }
EVIDENCE=${A2H_COLD_EVIDENCE_DIR:-spec/reports/smoke/cold-start-evidence}
mkdir -p "$EVIDENCE"
command -v hdc >/dev/null || { echo "SKIP: hdc 不可用（记 unverified-cold-start 粘性债）"; exit 3; }
HDC=(hdc)
if [ -n "${A2H_HDC_TARGET:-}" ]; then HDC+=(-t "$A2H_HDC_TARGET"); fi
hdc list targets > "$EVIDENCE/targets.txt" 2>&1
if ! grep -qvE '^\[Empty|^$' "$EVIDENCE/targets.txt"; then
  echo "SKIP: 无在线设备（记 unverified-cold-start 粘性债）"; exit 3
fi
"${HDC[@]}" shell aa force-stop "$BUNDLE" > "$EVIDENCE/force-stop.txt" 2>&1
sleep 1
"${HDC[@]}" shell hilog -r > "$EVIDENCE/hilog-reset.txt" 2>&1
if [ "$?" -ne 0 ] || cmd_err "$EVIDENCE/hilog-reset.txt" '\[CODE[[:space:]]*:[[:space:]]*-|Invalid|Usage:'; then
  echo "FAIL: EVIDENCE_LOST hilog reset failed"; exit 1
fi
"${HDC[@]}" shell aa start -b "$BUNDLE" -a "$ABILITY" > "$EVIDENCE/start.txt" 2>&1
if [ "$?" -ne 0 ] || grep -qiE 'error|failed' "$EVIDENCE/start.txt"; then echo "FAIL: 拉起失败"; exit 1; fi
sleep "$WAIT"
# ① crash 判定 + 进程存活（PID 作为本应用日志的过滤键）
"${HDC[@]}" shell ps -ef > "$EVIDENCE/processes.txt" 2>&1
PID=$(awk -v bundle="$BUNDLE" '$NF == bundle {print $2; exit}' "$EVIDENCE/processes.txt")
if ! [[ "$PID" =~ ^[0-9]+$ ]]; then echo "FAIL: 进程已死或PID证据缺失"; exit 1; fi
"${HDC[@]}" shell hilog -x -t app,core > "$EVIDENCE/hilog-all.txt" 2>&1
RC_ALL=$?
"${HDC[@]}" shell hilog -x -P "$PID" -t app,core > "$EVIDENCE/hilog-app.txt" 2>&1
RC_APP=$?
HILOG_ERR='\[CODE[[:space:]]*:[[:space:]]*-|Invalid log type|Usage:|commands can.t'
if [ "$RC_ALL" -ne 0 ] || [ "$RC_APP" -ne 0 ] ||
   cmd_err "$EVIDENCE/hilog-all.txt" "$HILOG_ERR" || cmd_err "$EVIDENCE/hilog-app.txt" "$HILOG_ERR" ||
   ! grep -qE '^[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9]+[[:space:]]+[DIWEF][[:space:]]+' "$EVIDENCE/hilog-all.txt"; then
  echo "FAIL: EVIDENCE_LOST hilog采集无有效原文，不能据零日志判无崩溃"; exit 1
fi
if grep -qiE 'cppcrash|jscrash|AppRecovery' "$EVIDENCE/hilog-app.txt" ||
   grep -iF "$BUNDLE" "$EVIDENCE/hilog-all.txt" | grep -qiE 'cppcrash|jscrash|AppRecovery|Fault'; then
  echo "FAIL: 冷启窗口内 crash"; exit 1
fi
# ② 首个网络请求出网（只数本应用进程的网络栈日志：RCP/http 发包）
NET=$(grep -icE 'rcp|httpclient|netstack|OH_Http|request.*(GET|POST)' "$EVIDENCE/hilog-app.txt" || true)
# 附加证据：未配置类文案（仅记录，不作判据——措辞可被游戏）
"${HDC[@]}" shell uitest dumpLayout -p /data/local/tmp/csp.json > "$EVIDENCE/dump-command.txt" 2>&1
"${HDC[@]}" shell cat /data/local/tmp/csp.json > "$EVIDENCE/dump.json" 2>&1
TOAST=$(grep -ocE '未配置|尚未就绪|暂不可用|unavailable|not ready' "$EVIDENCE/dump.json" || true)
echo "冷启存活 ✓ | PID=$PID | 本应用网络栈日志条数=${NET:-0} | 未配置类文案=${TOAST:-0} | 证据=$EVIDENCE"
if [ "${NET:-0}" -eq 0 ]; then
  echo "FAIL: 冷启 ${WAIT}s 内零网络请求出网——本应用日志未观测到出网，须核网络基座装配/隐私启动状态与请求证据"; exit 1
fi
echo "PASS"
