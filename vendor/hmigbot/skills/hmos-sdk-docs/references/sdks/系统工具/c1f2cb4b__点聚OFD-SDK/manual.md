点聚 OFD-SDK 

# 使用指南 

(HarmonyOS NEXT) 

北京点聚信息技术有限公司 

2026.05 

目录 

1. SDK 简介 2 

2. SDK 导入鸿蒙工程 3 

3. 使用 SDK 快速加载一个 pdf 文档指南 3 

版本 

版本内容 修订日期 修订者 

V1.0.0 

SDK 简介 

SDK 包含 1 个 har 文件: dianjulibrary.har 

( 注:该 har 相当于安卓版本的 dianjuAndroid4.0-V1.1.aar/ dianjuAndroid4.0-V1.1.jar 

加 libAutoSrvSealUtil.so 的集合体 ) 

# SDK 导入鸿蒙工程 

将 dianjulibrary.har 拷贝到工程的 libs 文件夹下 

工程代码引入 dianjulibrary.har ,在 oh-package.json5 加入如下代码: 

注意:左侧引入 har 包的变量名必须为 dianjulibrary, 名字区分大小 写; 

SDK 导入完成。 

使用 SDK 快速加载一个 pdf 文档指南 

struct OpenFile { 

// 创建接口库对象 

private djController: DJController = new DJController(this.getUIContext()); 

private mFilePath: string = ''; 

aboutToAppear() { 

this.mFilePath = getContext(this).filesDir+"/files/test.pdf"; 

// 调用接口加载 pdf 文档 

let openRet:number = this.djController.openTempFile(filePath); 

} 

build() { 

Column() { 

// 显示控件,显示 pdf 文档内容 

DJContentView({ controller: this.djController }) 

}.width('100%') .height('100%') 

} 

}
