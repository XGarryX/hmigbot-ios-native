# SVG/XML 资源输入边界

此历史文件名保留给引用方，原生 iOS 输入不包含通过改命名空间得到的 drawable 格式。Storyboard/XIB 是 UI 归档，不能当 SVG；Asset Catalog 的 Contents.json 是目录元数据；PDF、SF Symbols 和 Core Graphics 绘制需要各自的转换或明确替代决策。

仅真实 SVG 可按标准 SVG XML 处理：保留 viewBox、path 坐标、transform 顺序/旋转中心、clipPath、fill/stroke、opacity、渐变/引用、width/height 与目标渲染限制。坐标空间和显示尺寸独立。不得用正则统一乘所有数字（圆弧 flags、旋转、指数及负号并非可同样缩放的坐标）。优先保留几何并变换 viewBox/transform；需要重写 path 时使用真正的 path parser 并核验。

不自动把白色图标改黑；需读取 tint/rendering mode、背景和深浅色变体。无法准确转换则进入原资源决策/占位流程，输出来源与限制。转换结果要经原资源引用检查和实际渲染验证，不能以 SVG 可解析代替视觉通过。
