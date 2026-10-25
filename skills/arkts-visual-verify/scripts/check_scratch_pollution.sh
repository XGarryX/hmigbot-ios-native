#!/usr/bin/env bash
# check_scratch_pollution.sh — 收口卫生检查：项目根目录不得散落设备截图/dump。
# 背景（2026-08-26 客户实报）：主会话排查视觉问题时手写 hdc snapshot/recv，
# recv 默认落 cwd=项目根，累积数十张 route_*.jpeg / *_ui.json 无人管理。
# 规范落点 = spec/visual-verify/screenshots/adhoc/<page>__<tag>_<HHMMSS>.jpeg
# （对齐 check_replay.py 的现行命名与 screenshots/ 按类型分目录惯例）。
# 用法: bash check_scratch_pollution.sh [项目根，默认 .] [--archive]
#   无 --archive: 0=干净, 1=发现散落（WARN 报告，列清单+一键命令）
#   --archive:    自动归档进 adhoc/archived-<mmdd>/ 并打印移动清单，恒 exit 0
#                 （移动非删除，可恢复；收口清单用此模式——不依赖任何人自觉）
set -u
ROOT="${1:-.}"
MODE="${2:-report}"
ADHOC="spec/visual-verify/screenshots/adhoc"
found=$(find "$ROOT" -maxdepth 1 \( -name "*.jpeg" -o -name "*.jpg" -o -name "*.png" -o -name "*_ui.json" \) -type f 2>/dev/null)
if [ -z "$found" ]; then
  echo "scratch-pollution: PASS（项目根无散落截图/dump）"
  exit 0
fi
n=$(echo "$found" | wc -l | tr -d ' ')
echo "scratch-pollution: WARN — 项目根散落 $n 个截图/dump 文件（应落 $ADHOC/）:"
echo "$found" | head -20 | sed 's/^/  /'
[ "$n" -gt 20 ] && echo "  …共 $n 个"
if [ "$MODE" = "--archive" ]; then
  DEST="$ROOT/$ADHOC/archived-$(date +%m%d)"
  mkdir -p "$DEST"
  echo "$found" | while read -r f; do [ -n "$f" ] && mv "$f" "$DEST/" && echo "  归档: $(basename "$f") → $DEST/"; done
  echo "scratch-pollution: 已自动归档 $n 个文件（移动非删除，可恢复）"
  exit 0
fi
echo "一键归档:"
echo "  bash \$SKILLS_ROOT/arkts-visual-verify/scripts/check_scratch_pollution.sh $ROOT --archive"
exit 1
