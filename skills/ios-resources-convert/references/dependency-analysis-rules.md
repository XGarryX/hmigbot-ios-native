# 原生资源依赖分析

在选定 Source 上读取 Image/Color/LocalizedStringKey/NSLocalizedString、Bundle 资源、UIImage/UIColor、字体注册、Storyboard/XIB 和实际三方 bundle 引用。动态名称沿表达式、分支与调用方追踪，未解出的保留 unknown 与源锚点，不能用零正则命中当作无资源。

建立源名称/路径 → Asset Catalog/本地化/Bundle → 目标资源 ID 的映射。区分同名跨 bundle、locale、scale、appearance、idiom 与三方版本；不把未展开 build setting 当文件路径，不用目标文件夹名推断源语义。

转换前后验证实际引用、同名冲突、所有变体、占位符与 fallback。第三方缺资源先检查锁定依赖及真实 bundle，不伪造已下载资源。源文件不修改，生产合并由原 execute 单写者负责；未解决引用沿原资源占位登记和门禁处理。
