#!/bin/bash
# cold_start_probe.sh — 冷启冒烟探针（能力交付契约第③层，60 秒）
# 主判据（二值机械）：①冷启不 crash ②首个网络请求出网。文案 grep 仅附加证据。
# 用法: cold_start_probe.sh <bundleName> [ability=EntryAbility] [wait=8]
set -u
BUNDLE=${1:?bundleName required}; ABILITY=${2:-EntryAbility}; WAIT=${3:-8}
command -v hdc >/dev/null || { echo "SKIP: hdc 不可用（记 unverified-cold-start 粘性债）"; exit 3; }
hdc list targets 2>/dev/null | grep -qv '^\[Empty' || { echo "SKIP: 无在线设备（记 unverified-cold-start 粘性债）"; exit 3; }
hdc shell aa force-stop "$BUNDLE" >/dev/null 2>&1; sleep 1
hdc shell hilog -r >/dev/null 2>&1
hdc shell aa start -b "$BUNDLE" -a "$ABILITY" >/dev/null 2>&1 || { echo "FAIL: 拉起失败"; exit 1; }
sleep "$WAIT"
# ① crash 判定
if hdc shell hilog -x 2>/dev/null | grep -qE "cppcrash|jscrash|AppRecovery|Fault.*$BUNDLE"; then
  echo "FAIL: 冷启窗口内 crash"; exit 1; fi
hdc shell "ps -ef | grep -v grep | grep -q $BUNDLE" || { echo "FAIL: 进程已死"; exit 1; }
# ② 首个网络请求出网（hilog 网络栈痕迹：RCP/http 发包日志）
NET=$(hdc shell hilog -x 2>/dev/null | grep -icE "rcp|httpclient|netstack|OH_Http|request.*(GET|POST)" || true)
# 附加证据：未配置类文案（仅记录，不作判据——措辞可被游戏）
TOAST=$(hdc shell uitest dumpLayout -p /data/local/tmp/csp.json >/dev/null 2>&1 && \
        hdc shell cat /data/local/tmp/csp.json 2>/dev/null | grep -ocE "未配置|尚未就绪|暂不可用|unavailable|not ready" || echo 0)
echo "冷启存活 ✓ | 网络栈日志条数=$NET | 未配置类文案=$TOAST"
if [ "${NET:-0}" -eq 0 ]; then
  echo "FAIL: 冷启 ${WAIT}s 内零网络请求出网——网络基座疑似未装配（NetworkRuntimeState 事故形态）"; exit 1
fi
echo "PASS"
