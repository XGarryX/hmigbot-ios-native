# ohpm 搜索渠道与质量评估

> 查找 OpenHarmony/HarmonyOS 三方库的完整指南。

---

## 搜索渠道（按优先级）

### 1. ohpm 官方仓库
- **地址**：https://ohpm.openharmony.cn
- **搜索方式**：关键词搜索（如 "image"、"http"、"json"）
- **优势**：官方收录，质量有一定保证

### 2. OpenHarmony TPC (Third Party Components)
- **地址**：https://gitee.com/openharmony-tpc
- **特点**：社区维护的三方组件集合（556+ 仓库）
- **搜索方式**：在 gitee 组织页面搜索

### 3. HarmonyOS TPC
- **地址**：https://gitee.com/HarmonyOS-tpc
- **特点**：华为主导的三方组件迁移
- **搜索方式**：在 gitee 组织页面搜索

### 4. GitCode openharmony-tpc
- **地址**：https://gitcode.com/openharmony-tpc
- **特点**：部分库迁移到此平台

### 5. GitHub/Gitee 直接搜索
- **搜索关键词**：`"harmonyos" OR "openharmony" OR "ohos" + 功能关键词`
- **注意**：需要自行评估质量

---

## 质量评估清单

找到候选库后，按以下清单评估是否可用：

| 检查项 | 通过标准 | 权重 |
|-------|---------|------|
| 最近更新时间 | 6 个月内有提交 | 高 |
| 兼容 API 版本 | 支持 API 12+ | 高 |
| Star/Fork 数 | Star > 50 | 中 |
| 下载量 | > 100 | 中 |
| 文档完整性 | 有 README + 使用示例 | 中 |
| Issue 响应率 | 有人回复 issue | 中 |
| 开源许可 | 与项目许可兼容 | 中 |
| 仓库状态 | 未标记 archived | 高 |

---

## 安装与验证

```bash
# 安装 ohpm 包
ohpm install @ohos/imageknife

# 验证安装
cat entry/oh-package.json5  # 检查 dependencies 中是否有该包
```

---

## 已验证常用库列表

以下库经实战项目验证可用：

| 库 | 安装命令 | 用途 | 验证项目 |
|----|---------|------|---------|
| `@ohos/imageknife` | `ohpm install @ohos/imageknife` | 图片加载+缓存（类似 Glide） | Gallery |
| `@ohos/lottie` | `ohpm install @ohos/lottie` | Lottie 动画 | 通用 |
| `@ohos/axios` | `ohpm install @ohos/axios` | HTTP 请求（类似 Retrofit） | 通用 |
| `@ohos/pulltorefresh` | `ohpm install @ohos/pulltorefresh` | 下拉刷新 | 通用 |
| `@ohos/largeimage` | `ohpm install @ohos/largeimage` | 大图缩放（类似 SubsamplingScaleImageView） | Gallery |
