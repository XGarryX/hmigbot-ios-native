#!/usr/bin/env bash
# android-oracle.sh —— arkts-ut-verifier step0 的「确定性」后端。
#
# 设计原则:**完全项目无关**。本脚本不硬编码任何仓名/目录嵌套/模块根/计数。
# 它只接收一个 ANDROID_SOURCE_ROOT(调用方传入)与「相对模块根的锚点 path」,
# 用「后缀匹配」在任意嵌套布局下定位真实文件 —— 单层/双层嵌套/monorepo/扁平都成立。
# 凡是「LLM 容易数错/跟错链」的确定性活(锚点解析、枚举全集提取、溯源行号回校、
# 安卓现成单测枚举)一律交给本脚本,LLM 只做语义归类。
#
# 子命令:
#   resolve   <ROOT> <ANCHOR_PATH> [PKG_HINT]   解析锚点到绝对路径(后缀匹配+basename兜底+包名消歧)
#   find-sym  <ROOT> <SYMBOL> [kind]            ★信息缺失时主动搜索:按符号名找其「定义」位置(class/enum/object/interface/fun)
#   grep-kw   <ROOT> <KEYWORD> [maxN]           ★关键词全仓搜(取最相关前 maxN=8 个 .kt/.java),anchor 全失/无 anchor 时兜底发现
#   enum      <FILE> <ENUM_OR_SEALED_NAME>       提取 Kotlin/Java enum 全集；sealed 返回 UNSUPPORTED
#   verifyln  <FILE> <LINE> <LITERAL>            回校:FILE 的 LINE 附近(±3)是否真含 LITERAL(防溯源伪造)
#   tests     <ROOT> [KEYWORD]                   列出测试 source set 内 .kt/.java，按路径或内容关键词过滤
#   help                                         用法
#
# 退出码:0=命中/成功, 2=MISS/未命中/UNSUPPORTED, 3=AMBIGUOUS(多命中且无法消歧), 1=用法错误。
# 输出第一列是状态标签(OK|OK_SUFFIX|DRIFT|MISS|AMBIGUOUS|...),Tab 分隔后续字段,便于 agent 机读。

set -u
SOURCE_HELPER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/android_source.py"

die() { echo "ERR	$*" >&2; exit 1; }

cmd_resolve() {
  local root="${1:-}" anchor="${2:-}" pkg="${3:-}"
  [ -n "$root" ] && [ -n "$anchor" ] || die "usage: resolve <ROOT> <ANCHOR_PATH> [PKG_HINT]"
  [ -d "$root" ] || { echo "MISS	root-not-found	$root"; return 2; }
  # 去掉锚点 path 可能的前导 ./ 和引号残留
  anchor="${anchor#./}"; anchor="${anchor%\"}"; anchor="${anchor#\"}"
  local base; base="$(basename "$anchor")"

  # 1) 直连:ROOT/ANCHOR 直接存在(无嵌套或调用方已给全路径)
  if [ -f "$root/$anchor" ]; then
    echo "OK	$root/$anchor"; return 0
  fi
  # 2) 后缀匹配:锚点 path 作为后缀出现在 ROOT 下任意位置 —— 布局无关,处理任意层嵌套
  local hits; hits="$(find "$root" -type f -path "*/$anchor" 2>/dev/null)"
  local n; n="$(printf '%s\n' "$hits" | grep -c . )"
  if [ "$n" -eq 1 ]; then
    echo "OK_SUFFIX	$(printf '%s' "$hits")"; return 0
  elif [ "$n" -gt 1 ]; then
    _disambiguate "$hits" "$pkg" "$anchor" && return 0 || { echo "AMBIGUOUS	suffix	$n	$(printf '%s' "$hits" | tr '\n' '|')"; return 3; }
  fi
  # 3) basename 兜底:路径漂移时(中段目录变了)只按文件名找,再按包名/路径段消歧 → 标 DRIFT
  local bhits; bhits="$(find "$root" -type f -name "$base" 2>/dev/null)"
  local bn; bn="$(printf '%s\n' "$bhits" | grep -c . )"
  if [ "$bn" -eq 1 ]; then
    echo "DRIFT	$(printf '%s' "$bhits")"; return 0
  elif [ "$bn" -gt 1 ]; then
    if _disambiguate "$bhits" "$pkg" "$anchor"; then return 0
    else echo "AMBIGUOUS	basename	$bn	$(printf '%s' "$bhits" | tr '\n' '|')"; return 3; fi
  fi
  echo "MISS	no-file	$anchor"; return 2
}

# 多命中消歧:优先用 PKG_HINT(FQCN 或 com/xx/yy 包路径)做路径子串匹配;否则用锚点 path 里的包段
_disambiguate() {
  local hits="$1" pkg="$2" anchor="$3"
  # 把 FQCN 的 . 转成 / 作为路径子串;若没给 pkg,从 anchor 抽 com/.../ 段
  local needle=""
  if [ -n "$pkg" ]; then needle="$(printf '%s' "$pkg" | tr '.' '/')"; fi
  if [ -z "$needle" ]; then needle="$(printf '%s' "$anchor" | grep -oE '(com|cn|org)/[a-zA-Z0-9_/]+/' | head -1)"; fi
  [ -n "$needle" ] || return 1
  local m; m="$(printf '%s\n' "$hits" | grep -F "$needle" )"
  local mn; mn="$(printf '%s\n' "$m" | grep -c . )"
  if [ "$mn" -eq 1 ]; then echo "DRIFT	$(printf '%s' "$m")"; return 0; fi
  return 1
}

# 枚举解析拒绝不支持的语法与无法证明全集的 sealed 层级，不能将非零退出当成空集。
cmd_enum() {
  [ -n "${1:-}" ] && [ -n "${2:-}" ] || die "usage: enum <FILE> <NAME>"
  python3 "$SOURCE_HELPER" enum "$@"
}

# 溯源行号回校:断言里写了 // oracle: FILE:LINE,这里确认该行±3 真含 LITERAL。防 LLM 贴错行号/伪造来源。
cmd_verifyln() {
  local file="${1:-}" line="${2:-}" lit="${3:-}"
  [ -n "$file" ] && [ -n "$line" ] && [ -n "$lit" ] || die "usage: verifyln <FILE> <LINE> <LITERAL>"
  [ -f "$file" ] || { echo "FAIL	file-not-found	$file"; return 2; }
  local lo=$((line-3)); [ "$lo" -lt 1 ] && lo=1; local hi=$((line+3))
  if sed -n "${lo},${hi}p" "$file" 2>/dev/null | grep -Fq -- "$lit"; then
    echo "OK	$file:$line 含 '$lit'"; return 0
  fi
  echo "FAIL	$file:$line 附近未见 '$lit' —— 回核版本、符号与推导，不得弱化断言"; return 2
}

# 搜索结果用于定位候选，MISS 只表示本次搜索未命中，不证明源码不存在。
cmd_find_sym() {
  [ -n "${1:-}" ] && [ -n "${2:-}" ] || die "usage: find-sym <ROOT> <SYMBOL> [kind]"
  python3 "$SOURCE_HELPER" find-sym "$@"
}
cmd_grep_kw() {
  [ -n "${1:-}" ] && [ -n "${2:-}" ] || die "usage: grep-kw <ROOT> <KEYWORD> [maxN]"
  python3 "$SOURCE_HELPER" grep-kw "$@"
}
cmd_tests() {
  [ -n "${1:-}" ] || die "usage: tests <ROOT> [KEYWORD]"
  python3 "$SOURCE_HELPER" tests "$@"
}

case "${1:-help}" in
  resolve)   shift; cmd_resolve "$@";;
  find-sym)  shift; cmd_find_sym "$@";;
  grep-kw)   shift; cmd_grep_kw "$@";;
  enum)      shift; cmd_enum "$@";;
  verifyln)  shift; cmd_verifyln "$@";;
  tests)     shift; cmd_tests "$@";;
  help|-h|--help)
    sed -n '2,32p' "$0";;
  *) die "unknown subcommand: $1 (try: help)";;
esac
