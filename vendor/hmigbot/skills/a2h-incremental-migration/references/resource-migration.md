# §A 资源迁移附录（references 详细版）

主 SKILL.md §A 的详细执行手册。资源层（图片/字符串/字体/字符串/权限）的具体迁移规则与命令。

## A.1 图片文件格式转换

| Android 源 | 处理 | HMOS 路径 |
|---|---|---|
| `*.png` / `*.jpg` / `*.webp` | 直接复制 | `resources/base/media/{name}.png` |
| `*.9.png` | 复制（去 `.9`） | `resources/base/media/{name}.png` |
| XML vector drawable | 转 SVG | `resources/base/media/{name}.svg` |
| Lottie JSON / 字体 | 直接复制 | `resources/base/rawfile/{name}` |
| `mipmap-*/ic_launcher*` | 一般可跳过 | - |

**XML vector → SVG 转换规则**：
- `<vector>` 的 `android:width/height` → SVG 的 `width/height/viewBox`
- `<path android:pathData="..." android:fillColor="..."/>` → `<path d="..." fill="..."/>`

## A.2 从 GitHub 下载二进制

```bash
gh api repos/{owner}/{repo}/contents/{path}?ref={sha} --jq '.content' | base64 -d > /tmp/{file}
# 或
curl -L "https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{path}" -o /tmp/{file}
```

## A.3 命名规则

- 保持 Android 原始名，**去密度后缀**（`-hdpi` / `-xhdpi` 等）
- HMOS 已用不同名引用同一图标时，**以 HMOS 侧命名为准**，不要引入重复文件

## A.4 字符串资源

| Android | HMOS |
|---------|------|
| `res/values/strings.xml` | `resources/base/element/string.json` |
| `res/values-zh/strings.xml` | `resources/zh_CN/element/string.json`（如存在）|

## A.5 子代理输出约束

委托扫描给 Explore / general-purpose 子代理时：

1. **每条扫描命令的 stdout 原文必须以 code fence 形式返回**
2. 看到 `Assumed` / `Estimated` / `likely` / `appears to` / `~N%` 等估算词 → **打回重跑**
3. 真跑失败必须写 `SKIPPED(原因)`，**不能编数字**
4. 返回 > 500 行时可落盘 `/tmp/xxx.md`，但主代理**必须亲自 Read 关键章节验证**
