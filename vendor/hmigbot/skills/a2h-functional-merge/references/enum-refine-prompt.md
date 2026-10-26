# Phase 3 枚举入口精修 — sub-agent prompt 模板

主 skill 在确定性映射后,对 `confidence=low` 的枚举功能点派一个 sub-agent 精修。下面是 prompt 要点,主代理按实际路径渲染。

## 背景给 sub-agent

A2H 的 `functional_registry` 里有一批"创作工具",每个是 `FunctionToolType`(或 `ChatProportion` / `VideoProportionBean` 等)枚举值。点击宫格后,代码在一个**分发中枢**里用 `when(toolType){ X.type -> openXxx() }` 转发,真正的 `startActivity` 在 `openXxx` 内部。纯 grep 取众数会抓到金币规则表/通用结果页/作品列表等**次要引用**,所以确定性映射只能给 low。要把它精修到**真入口宿主页**。

## 输入(主代理注入)

- 待精修枚举(confidence=low 的功能点):`[{name, raw_identifier}]`
- 合法目标:fact-tree 的 record id 清单(mapped_record 必须在内,否则标 not_in_facttree)
- 安卓源码根路径

## 方法(逐条)

1. `grep -rn "<枚举值,如 IMAGE_ENHANCEMENT>" --include=*.kt`(排除 `/build/` 和枚举声明文件本身)。
2. 找**入口分发点**:宫格 onClick → 分发中枢的 `X.type -> { ... }` 分支。常见中枢是 `HomeViewModel.drawSameStyle()` 一类。
3. 顺分支体往下读:
   - 直接 `startActivity<Xxx>()` / `Intent(.., Xxx::class.java)` → Xxx 即入口页;
   - 转调 `Xxx.openXxx(type)` / ARouter → 再追该方法体里的 startActivity。
4. **区分入口页 vs 噪声**:入口页是"点工具后第一个落地的承载页";`*Details / *Preview / *SaveSuccess / *Dialog / 作品列表` 一般是结果/详情/弹窗,**不是入口**。
5. 不少工具进**通用承载页**(HSVFXPreviewActivity / PictureVideoActivity / AiPaintChatActivity)再用 type 区分内容——**入口就是该承载页**,notes 注明 "type=X 区分"。
6. 分发分支被注释 / 不在宫格菜单的工具 → 标 "已下线",仍给历史承载页 + notes(下游测试需跳过,否则误判成"鸿蒙未实现")。
7. mapped_record 必须在 fact-tree record 清单里;对不上给最接近真实类名 + `in_facttree:false`。

## 输出

只输出一个 JSON 对象,写到 `enum_refine_overrides.json`,键用 raw_identifier:

```jsonc
{
  "FunctionToolType.IMAGE_ENHANCEMENT": {
    "mapped_record": "HSVFXPreviewActivity",
    "impl_file": "aipaint/.../HSVFXPreviewActivity.kt",
    "confidence": "high",
    "evidence": "HomeViewModel.drawSameStyle:382 → HSVFXPreviewActivity.openHSVFXPreviewPage(type)",
    "notes": "通用承载页,type=IMAGE_ENHANCEMENT 区分"
  }
}
```

主 skill 拿这个文件 `--enum-refine` 重跑 merge,把 host 升 high、补 impl_file。

## 注意

- 认真读源码追分发,**别拿 grep 众数糊弄**——确定性映射的 current_guess 很多是噪声(如 文生视频→某弹窗),你的任务就是纠正。
- 只碰传入的 low 置信枚举,不动其它功能点。
