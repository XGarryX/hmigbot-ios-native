# 原生序列帧 / SVGA 迁移

## 1. UIImageView 序列帧 / 原生帧资源 → ImageAnimator 候选

读取 UIImageView.animationImages / highlightedAnimationImages、animationDuration、animationRepeatCount、startAnimating / stopAnimating、GIF/APNG 解码器的实际帧时间与释放逻辑。UIKit repeatCount=0 表示持续重复；目标 ImageAnimator 的次数语义须按目标 API 核验后映射。不能只凭图片文件名推断帧序、循环次数或持续时间。

保留逐帧时长、尺寸、Asset Catalog scale/appearance、暂停/重入/取消/后台行为和完成回调。复用原 arkts-animation-builder 的目标 ImageAnimator 实现；资源由 ios-resources-convert 按真实源引用转换。缺资源、私有格式或仅有编译产物时按原决策/占位流程披露，不能声称无损还原。

## 2. SVGA

只有实际依赖与调用证明使用 SVGA 时才迁移。读取真实原生播放器类型、播放范围/次数、动态文本/图像替换、回调和资源生命周期；目标候选库须核验版本/许可/API。若需换资源格式或退化效果，进入原产品决策，不能自动改成静态成功图。
