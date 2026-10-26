# §M2.4 资源层符号差集（references 详细版）

主 SKILL.md §M2.4 的详细执行手册。**本模式唯一允许的符号扫描**（name-as-identity 高效准确）。

## 完整差集命令

```bash
ANDROID={android_dir}; HMOS={hmos_project}

# (a) 图片资源差集
grep -rh "@mipmap/\|@drawable/" $ANDROID/app/src/main/res/layout/ \
  | grep -oP '(?<=@mipmap/|@drawable/)[a-z0-9_]+' | sort -u > /tmp/a_imgs.txt
grep -rh "R\.mipmap\.\|R\.drawable\." $ANDROID/app/src/main/java/ \
  | grep -oP '(?<=R\.mipmap\.|R\.drawable\.)[a-z0-9_]+' | sort -u >> /tmp/a_imgs.txt
ls $HMOS/entry/src/main/resources/base/media/ | sed 's/\.[^.]*$//' | sort -u > /tmp/h_imgs.txt
comm -23 <(sort -u /tmp/a_imgs.txt) /tmp/h_imgs.txt

# (b) strings.xml key 差集（覆盖所有 values-* qualifier）
grep -rhoE '<string name="[a-z_0-9]+"' $ANDROID/app/src/main/res/values*/strings.xml \
  | sed -E 's/.*name="([^"]+)".*/\1/' | sort -u > /tmp/a_keys.txt
grep -rhoE '"name"[[:space:]]*:[[:space:]]*"[a-z_0-9]+"' \
  $HMOS/entry/src/main/resources/*/element/string.json \
  | sed -E 's/.*"name"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/' | sort -u > /tmp/h_keys.txt
comm -23 /tmp/a_keys.txt /tmp/h_keys.txt | head -100

# (c) Retrofit endpoint 差集
grep -rhoE '@(GET|POST|PUT|DELETE|PATCH)\("[^"]+"\)' $ANDROID \
  | sed -E 's/.*"([^"]+)".*/\1/' | sort -u > /tmp/a_apis.txt
grep -rhoE "(url|path)[[:space:]]*[:=][[:space:]]*['\"][^'\"]+['\"]" \
  $HMOS/entry/src/main/ets/services/ \
  | sed -E "s/.*['\"]([^'\"]+)['\"].*/\1/" | sort -u > /tmp/h_apis.txt
comm -23 /tmp/a_apis.txt /tmp/h_apis.txt

# (d) 权限差集（再用 §4.3 映射表筛）
grep -oE '<uses-permission[^/]+android:name="[^"]+"' $ANDROID/app/src/main/AndroidManifest.xml \
  | sed -E 's/.*android:name="([^"]+)".*/\1/' | sort -u
```

## HARD-GATE

- 每个差集命令的 stdout 必须在对话里以 code fence 形式出现
- 命令返回空 → 明确写"空结果"，**不是**跳过
- 命令报错 → 写 `SKIPPED(原因)`
- 差集结果**不等于**"一定要迁"——image/string key 可能是废弃的；endpoint 可能已在 HMOS 用不同字符串表达。每条要 LLM 读上下文判断再进 §S2
