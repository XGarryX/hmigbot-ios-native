点聚 OFD-SDK 

# 接口文档 

(HarmonyOS NEXT) 

北京点聚信息技术有限公司 

2024.08 

目录 

# 1. SDK 简介 4 

1.1. SDK 包含文件 4 

1.2. SDK 导入鸿蒙工程 4 

1.3. 初始化 DJContentView 和加载文档 4 

2. DJController 类接口介绍 5 

2.1. 打开文件 5 

2.2. 打开 PDF 文件 6 

2.3. 用户登录 6 

2.4. 盖 sel 章 6 

2.5. 盖图片章 7 

2.6. 获取当前缩放比例 7 

2.7. 设置手指可手写 7 

2.8. 设置操作状态 7 

2.9. 获取点击 / 框选位置 8 

2.10. 获取点击 / 框选位置 8 

2.11. 获取点击 / 框选页码 8 

2.12. 插入节点 8 

2.13. 合并文件 9 

2.14. 获取文档总页数 9 

2.15. 保存文件 9 

2.16. 保存文件 9 

# 2.17. 判断文档自本次打开之后是否有改动 10 

2.18. 设置笔属性 10 

2.19. 刷新文档 10 

2.20. 模版赋值 10 

2.21. 验证授权 10 

版本 

版本内容 修订日期 修订者 

V1.0.0 beta 

创建文档 

20240809 

V1.0.1 beta 

新增编辑文本框、弹出手写板相关功能接口; 新增无界面合并文件接口 

20240927 

V1.0.3 beta 新增接口 20250110 

V1.0.4 beta 增加点击编辑功能、长按选中 / 拖动功能 20250214 

V1.0.5 beta - 增加单页模式 左右翻页功能 

20250224 clf 

V1.0.7 beta 删除 setContent 方法,用 setValue 方法替代;优化卡顿问题; compatibleSdkVersion : 17 

20250710 

clf 

V1.0.8 beta 

优化 2in1PC 设备上触摸板和滚轮翻页不足 60 帧 /s 的问题; 

20250716 

clf 

V1.0.0 

- 新增单页模式 左右翻页和上下翻页;新增插入空白页接口;新增截屏 接口;新增在线授权接口;新增扫二维码授权接口; 

20260313 

clf 

SDK 简介 

SDK 包含文件 

1 个 har 文件: dianjulibrary.har( 以前也叫 dianjuHarmony.har ,这俩 是同一个包 ) 

( 注:该 har 相当于安卓版本的 dianjuAndroid4.0-V1.1.aar/ dianjuAndroid4.0-V1.1.jar 

加 libAutoSrvSealUtil.so 的集合体 ) 

SDK 导入鸿蒙工程 

将 dianjulibrary.har 拷贝到工程的 libs 文件夹下 

工程代码引入 dianjulibrary.har ,在 oh-package.json5 加入如下代码: 

注意:左侧引入 har 包的变量名必须为 dianjulibrary, 名字区分大小 写; 

初始化 DJContentView 和加载文档 

# 1) 在 UI 布局中引入 DJContentView 控件 

注: DJController 是 DJContentView 的控制器,对 DJContentView 进 行操作的方法都封装在 DJController 中, DJController 创建 private djController: DJController = new DJController(), 详细可参考 demo ;另外 DJController 中有一个接口 receiveDJMsg 需要 app 重写, 这个接口可以接收 SDK 的一些回调消息,详细可参考 DEMO 。 

DJController 中自定义的 receiveDJMsg 回调方法介绍 

receiveDJMsg(type:number,data?:number| null,datas?:number[],msg?:string) 方法 

参数: 

type 介绍: 

DJCode.AUTO_UP :表示在 

setCurrAction(OperType.AUTO_HANDLE) 状态下,抬笔的操作,该 状态下抬笔的时候 receiveDJMsg 会收到消息,并且可获取划选的位置 坐标,可进行一些插入操作 ( 比如插入文字,插入手写,插入图片 ) 

DJCode.CLICK_NODE :表示在 OperType.NONE 或者 OperType.WRITE 状态下,点到了节点内容,该状态下点到节点 receiveDJMsg 会收到消息,并且可获取到点击到的节点的相关信息。 

加载空白手写板 

代码示例: 

DJController 静态字段 

- 浏览文档 鼠标滚轮灵敏度 

DJController.SENSITIVE_WHELL = 30 

注释:表示每帧滚动 30 个像素高度,默认值 30 

# 浏览文档 -2in1 设备触摸板灵敏度 

DJController.TOUCHPAD = 30 

注释:表示每帧滚动 30 个像素高度,默认值 30 

DJController 属性字段 

# 1) 双指移动文档功能 

this.djController.twoFingerMovePage = true // 默认开启双指移动文 档功能 

DJController 类接口介绍 

设置字体目录 

setValue("SET_FONTFILES_PATH",fontDir) 

注:在打开文件前调用; 

/system/fonts/ 是鸿蒙系统字体所在目录,该目录也可直接使用; 打开文件 

openTempFile(filePath:string):number 

功能:打开文件 (aip/ofd/pdf) 

参数: 

filePath :文件本地路径 

返回值: >0 成功;其他 - 失败 

打开 PDF 文件 

openFile(filePath:string):number 

功能:打开 pdf 文件 

参数: 

filePath :文件本地路径 

返回值: >0 成功;其他 - 失败 

用户登录 

login(userID:string, userType:number, pwd:string):number 

功能:用户登录,在打开文档后调用,用来标识该文档的当前签批 人,手写内容的用户属性里面会有 userID 这个信息 

参数: 

userID :用户名 ( 汉字 / 字母 / 数字 / 下划线组合 ) 

userType : 2- 正式用户 

pwd :保留字段 , 传空字符串 

返回值: 1- 成功;其他 - 失败 

注:在未授权或者授权验证失败的情况下, login 调用必失败;在文档 打开前调用 login 必失败; 

# 盖 sel 章 

addSealEx(sealPath:string, pfxPath:string, pfxPwd:string, sealMode:number, page:number, x:number, y:number):number 

功能:盖 sel 章 ( 支持盖章文件类型: aip/pdf) 

参数: 

sealPath :本地印章路径 或者是 STRDATA: 印章 base64 

pfxPath :证书本地路径 或者是 STRDATA: 证书 base64 

pfxPwd :证书密码 

sealMode :盖章模式 

0-PDF 非互验 ( 其他工具如 adobe reader 无法验证 ) ,支持无证书盖章 

2-PDF 可互验 ( 其他工具如 adobe reader 可验证 ) ,不支持无证书盖章 

page :盖章页码 ( 从 0 开始, 0- 代表第 1 页 ) 

x :文档上 x 坐 ( 单位: 1/50000) 

y :文档上 y 坐标 ( 单位: 1/50000) 

返回值: 1- 成功;其他 - 失败 

# 盖图片章 

addPicSealEx(picPath:string, pfxPath:string, pfxPwd:string, sealMode:number, page:number, x:number, y:number, picZoom:number):number 

功能:盖图片章 ( 支持盖章文件类型: aip/pdf) 参数: 

picPath :本地图片路径 或者是 STRDATA: 图片 base64( 支持图片类 型: png/jpg/bmp) 

pfxPath :证书本地路径 或者是 STRDATA: 证书 base64 

pfxPwd :证书密码 

sealMode :盖章模式 

0-PDF 非互验 ( 其他工具如 adobe reader 无法验证 ) ,支持无证书盖章 2-PDF 可互验 ( 其他工具如 adobe reader 可验证 ) ,不支持无证书盖章 page :盖章页码 ( 从 0 开始, 0- 代表第 1 页 ) 

x :文档上 x 坐 ( 单位: 1/50000) 

y :文档上 y 坐标 ( 单位: 1/50000) 

picZoom :图片章的缩小比例 ( 范围 1-100 , 100- 代表原图大小 ) 返回值: 1- 成功;其他 - 失败 

# 获取当前缩放比例 

getCurrZoom():number 

功能:获取当前缩放比例 

参数:无 

返回值:当前缩放比例值 

设置手指可手写 

setUseFingerWrite(isUseFingerWrite:boolean):void 

功能:设置手指可手写 

参数: 

isUseFingerWrite : true- 手指可写 ( 默认 ); false- 手指可不写,但可拖动 和缩放文档 

返回值:无 

设置操作状态 

setCurrAction(currAction:number):void 

功能:设置操作状态 

参数: 

currAction : 

OperType.NONE- 浏览翻页状态 

OperType.WRITE- 手写状态 

OperType.ERASER- 擦除状态 

OperType.AUTO_HANDLE- 获取点击 / 框选位置状态 

返回值:无 

# 获取点击 / 框选位置 

getAutoRectPx():Rect 

功能:获取点击 / 框选位置 

参数:无 

返回值: Rect 对象 {left:-1,top:-1,right:-1,bottom:-1} ,数值单位是 px 像素 

注: OperType.AUTO_HANDLE 状态下在文档上划动会有值 

获取点击 / 框选位置 

getAutoRect():Rect 

功能:获取点击 / 框选位置 

参数:无 

返回值: Rect 对象 {left:-1,top:-1,right:-1,bottom:-1} ,数值单位是 vp 

注: OperType.AUTO_HANDLE 状态下在文档上划动会有值 

获取点击 / 框选页码 

getAutoRectPage():number 

功能:获取点击 / 框选页码 

参数:无 

返回值:页码 ( 从 0 开始, 0- 代表第 1 页 ) 

注: OperType.AUTO_HANDLE 状态下在文档上划动会有值 

插入节点 

insertNote(nodeName:string, nType:number, nPage:number, nPosx:number, nPosy:number, nWidth:number, nHeight:number):number 

# 功能:插入节点 

参数: 

nodeName :节点 id 

nType :节点类型 

3- 遮盖类型 

14- 文本类型 ( 带签名章 + 日期 ) 

- 4- 文本类型 ( 不带签名章和日期 ) 

- 2- 普通手写区域 

13- 多行手写区域 

nPage :页码 ( 从 0 开始 ) nPosx :插入区域 x 坐标 ( 单位 :1/50000) nPosy :插入区域 y 坐标 ( 单位 1/50000) nWidth :插入区域宽度 ( 单位 1/50000) nHeight :插入区域高度 ( 单位 1/50000) 

返回值: 1- 成功;其他 - 失败 

合并文件 

mergeFile(filePath:string, pageIndex:number):number 

功能:合并文件 

参数: 

filePath :要合并上来的文件的本地路径 

pageIndex :要合并到当前文档的位置 ( 从 0 开始 ) 

返回值: 1- 成功;其他 - 失败 

# 获取文档总页数 

getPageCount():number 

功能:获取文档总页数 

参数:无 

返回值:文档总页数 

保存文件 

saveFile(savePath:string):number 

功能:保存并关闭当前文档 ( 关闭后文档不可操作 ) 

参数: 

savePath :本地路径,当为空字符串时,仅关闭当前文档。 

返回值: 1- 成功;其他 - 失败 

注:每个打开的文档,在不再使用情况下,必须进行关闭,否则会一 直驻留内存。 

保存文件 

saveFileEx(savePath:string,closeDoc: number) 

功能:保存文件 

参数: 

savePath :本地路径 

closeDoc : 1- 关闭当前文档; 0- 不关闭当前文档 

返回值: 1- 成功;其他 - 失败 

判断文档自本次打开之后是否有改动 

issaved():number 

# 功能:判断文档自本次打开之后是否有改动 

参数:无 

返回值: 0- 有改动; 1- 无改动 

注:如果文件有修改,该方法返回 0 ,在调用 savefileex 、 savefile 方法 之后,再调该方法返回 1 

# 设置笔属性 

setPenProp(penW: number,penCol: number|string|Color):number 

功能:设置笔宽和颜色 

参数: 

penW :笔宽 1-27 

penCol :颜色 ; 如: #ECFEEA 或者 Color.Green 

返回值: 1- 成功;其他 - 失败 

注:打开文档后调用有效 

刷新文档 

freshPDF():void 

功能:刷新文档 

参数:无 

返回值:无 

刷新文档 

freshClearPDF():void 

功能:刷新文档界面 ( 非立即刷新出内容,有清晰图之后才刷新界面 ) 参数:无 

# 返回值:无 

# 设置属性 / 节点赋值 

setValue(nodeId:string, value:string):number 

功能:设置属性 

参数: 

nodeId :节点 id 

value :属性值 

返回值: 1- 成功 ; 其他 - 失败 

# 在线注册授权 

public async getLicOnline(ip: string, userId: string): Promise<string> 

功能:在线注册授权 

参数: 

ip :固定地址 https://auth.dianju.cn 

userId :点聚提供的授权账号 

返回值: ok- 成功;其他 - 失败 

注:鸿蒙版本授权账号和安卓版本授权账号不能相互通用;应用卸载 后再重新安装设备号不变,不同的 app 采集的设备号不同; 

弹二维码方式注册授权 ( 离线方式注册授权 ) 

public verifyByQRCode(userId: string): number 

功能:弹二维码方式注册授权 

参数: 

# userId :点聚提供的授权账号 

返回值: 1- 授权验证成功;其他 - 授权验证失败,且 SDK 会自动弹出一 个设备信息的二维码; 

扫描授权信息写入设备成功后会有如下回调消息: 

注:该接口需要搭配点聚扫码授权工具使用 (DJserial-260202.apk) 

验证授权 

verifyUc(str:string):number 

功能:万能码授权验证,授权验证成功,用户登录 login 方法才能调用 成功,否则 login 调用必然失败。 

参数: 

str :授权码 

返回值: 1- 成功;其他 - 失败 

获取页对应图片 

getPixelMap(page:number,width:number,height:number,mZoom:number): PixelMap|null 

功能:获取文档某页的 PixelMap 。 

参数: 

page :页码 ( 从 0 开始 ) 

width :宽度 ( 单位 : 像素 ) 

height :高度 ( 单位 : 像素 ) 

nZoom :缩放比例 ( 如果前面设置了宽度或者高度,缩放比例设置无 效 ) 

# 返回值:某页对应的 PixelMap 

获取页对应图片 base64 

功能:获取文档某页的对应图片的 base64 。 

参数: 

page :页码 ( 从 0 开始 ) 

width :宽度 ( 单位 : 像素 ) 

height :高度 ( 单位 : 像素 ) 

nZoom :缩放比例 ( 如果前面设置了宽度或者高度,缩放比例设置无 效 ) 

返回值:某页对应图片的 base64 字符串 

设置 aip 文件上可编辑的模版节点 

setEditTempNodes(editNodes:ArrayList<string>|null):void 

功能:设置 aip 文件上可编辑的模版节点 ( 默认不可编辑 aip 制作模版时 创建的节点 ) 

参数: 

editNodes :可编辑的模版节点列表 

返回值:无 

注:仅针对于属于 aip 模版上的节点需要配置是否可编辑,默认 aip 模 版上的节点都不可编辑,也就是 OperType.NONE 和 OperType.WRITE 状态下,点击这些节点, receiveDJMsg 方法不会收到 DJCode.CLICK_NODE 消息。 

设置 aip 文件上的所有模版节点可编辑 

setAllTempNodeEdit(canEdit:boolean):void 

功能:设置 aip 文件上的所有模版节点可编辑 

参数: 

canEdit : true 所有模版节点可编辑,为 true 时, setEditTempNodes 方法失效。 

false( 默认 ) 所有模版节点不可编辑,为 false 时, setEditTempNodes 方 法有效。 

返回值:无 

# 获取文档中全部的节点字符串数据 

getNodes():string 

功能:获取文档中全部的节点字符串数据 

参数: 

无 

返回值:签批字符串 ( 注意:空值返回一个 errorcode+ 数字 ) 

# 获取文档中某用户的节点字符串数据 

getNodesEx(pageIndex:number,userId:string):string 

功能:获取文档中某用户的节点字符串数据 

参数: 

pageIndex :页码 (-1 代表所有页 ) 

userId :用户 ID 

返回值:签批字符串 ( 注意:空值返回一个 errorcode+ 数字 ) 

将节点字符串数据恢复到原空内容的文件上 

pasteNodes(strNodes:string):number 

功能:将节点数据恢复到原文件上 

参数: 

strNodes : getNodes 方法获取到的节点字符串内容 

返回值: 1- 成功;其他 - 失败; 

注:合成后 aip 文件上的模版节点可能会有重复的,可以配置 

setValue("ADD_FORCETYPE_VALUE6", 0x800) 去重复 

将手写数据合成到文档的某个手写区域内 

pasteNodesToArea(areaName:string, strNodes:string):number 

功能:将手写数据合成到文档上的某个手写区域内 

参数: 

areaName :手写区域的节点名 

strNodes: 手写数据字符串 ( 仅限在空白手写板上 getNodes 方法获取到 的纯手写内容的数据 ) 

返回值: 1- 成功;其他 - 失败; 

获取页面对应图片 

getPixelMap(page:number,width:number,height:number,mZoom:number) 

功能:获取每页对应的 PixelMap 图像 

参数: 

page :页码 ( 从 0 开始 ) 

width :宽度 ( 单位 : 像素 ) 

height :高度 ( 单位 : 像素 ) 

mZoom :缩放比例 ( 如果前面设置了宽度或者高度大于 0 ,缩放比例设 置无效 ) 

返回值:某页对应 pixelmap 

判断节点类型 

getNodeType(nodeName:string):number 

功能:判断节点类型 参数: 

nodeName :节点名 

返回值: 

101- 普通文本节点 

102- 带附加用户的文本节点 

103- 遮盖层 

104- 普通日期节点 

105- 中文日期节点 

106- 浮点类型节点 

107- 整数类型节点 

108- 大写金额节点 

201- 手写节点 

- 1- 附件类型注释节点 

- 2- 复选框节点 

- 3- 单选框节点 

- 4- 组合框节点 

# 5- 音频节点 

# 6- 图片和印章及二维条码 

- 其他 暂未定义类型 

使用场景:编辑状态下点击不同的节点,根据节点的类型弹出不同的 UI 界面 

锁住 / 解锁 DJContentView 屏幕 

lockScreen(lock:boolean):void 

功能:锁住 / 解锁 DJContentView 屏幕 

参数: 

lock : true- 锁住 ; false- 解锁 

返回值:无; 

# 设置附加用户的文字 / 图片署名 

setUserInfoEx(userId:string, lServerID: number,lType: number,value: string):number 

功能:设置附加用户的图片署名 ( 文字署名 ) 

参数: 

userId :用户名 ( 汉字 / 字母 / 数字 / 下划线组合 ) 

lServerID : 0- 固定值 

IType : 1- 文字; 7- 图片; 

Value :文字内容 / 本地图片路径 

返回值: 1- 成功;其他 - 失败 

特殊用法 1 : IType=8 为设置用户排序等级,不再介绍 IType=8 的使 

用,已封装为 setUserLevel 方法,关于用户排序等级方法的设置,参 见 setUserLevel 方法 

# 设置用户排序等级 

setUserLevel(userId:string, level:number):number 

功能:设置用户排序等级 

参数: 

level : 0-63( 等级越大,显示靠前 ( 上 )) 

返回值: 1- 成功;其他 - 失败 

# 注:使用该方法需要在打开文件前配置 

setValue("ADD_FORCETYPE_VALUE5", 0x80000) 开启等级排序功 能。 

# 设置展示效果 

setShowMode(showMode:number):void 

功能:设置展示效果 

参数: 

showMode : 0- 适应窗口(整页都在屏幕中) 

适应页宽(宽度铺满屏幕 , 可缩小到宽度铺满屏幕 , 默认值) 适应页高(高度铺满屏幕 , 可缩小到高度铺满屏幕) 

- 6- 首页宽度铺满屏幕,可缩小到宽度铺满屏幕; 

11- 适应页宽(宽度铺满屏幕 , 可缩小到整页都在屏幕中) 

12- 适应页高(高度铺满屏幕 , 可缩小到整页都在屏幕中) 

返回值:无 

# 设置缩放比例 

setZoomByCenter(zoom:number):void 

功能:设置缩放比例 ( 以中心位置缩放文档 ) 参数: zoom :缩放比例 返回值:无 

跳转到某页 

gotoPage(page:number):void 功能:跳转到某页 参数: page :页码 (0- 代表第 1 页 ) 返回值:无; 

跳转到某页的 y 位置 gotoPosition(page:number, y:number):void 功能:跳转到某页 y 位置 参数: page :页码 

y :取值范围 (0-50000) 

返回值:无 

# 显示滚动条 

setShowScroll(showScroll:number):void 

功能:显示滚动条 

参数: 

showScroll : 0- 不显示滚动条 ( 默认 ); 

显示滚动条 ( 多页文件且滚动文件时才会显示出来 ) ,尚未支持该值, 开 发中 ; 

2- 显示滚动条 ( 多页文件显示滚动条 ) 

注: 1 页文件和文件总长度小于屏幕高情况下不显示滚动条 

返回值:无 

获取所有节点 

getAllNodeInfo():ArrayList<string>|null 

功能:获取所有节点 

参数: 

无 

返回值:节点 id 集合 

获取某用户的节点集合 

getUserNodes(userId:string|null):ArrayList<string>|null 

功能:获取某用户的节点集合 

参数: 

userId :用户 ID( 为空的时候获取到为所有的节点 ) 

# 返回值:节点集合 

# 撤销 

undoAll(all:boolean):number 

功能:撤销 参数: 

all : true- 全部撤销 

false- 单步撤销 

返回值: 1- 成功;其他 - 失败 

# 获取当前页码 

getCurrPage():number 

功能:获取当前页码 参数: 

无 

返回值:当前页码 

# 查找文字 

findText2(strText:string, nCase:number, nStartPage:number, nEndPage:number, nReverse:number, nMiddle:number,nSetSearchIndex:number):string 

功能:查找文字 

参数: 

strText :文字内容 

nCase : 1- 大小写敏感; 0- 不敏感 

nStartPage :起始页 ( 从 0 开始 ) 

nEndPage :结束页 

nReverse : 1- 反向查找; 0- 正向查找 ( 默认 ) 

nMiddle : 0:lefttop, 1:center, 2:rightbottom 

nSetSearchIndex : 1- 代表第 1 个 

返回值:页码 ,x,y, 保留值 

# 查找文字并选中 

searchText(strText:string, nCase:number, nReverse:number, nFindMode:number, 

nStartPage:number, nEndPage:number):string 

功能:查找文字并选中 

参数: 

strText :文字内容 

nCase : 1- 大小写敏感; 0- 不敏感 

nReverse : 1- 反向查找; 0- 正向查找 ( 默认 ) 

nFindMode : 0- 查找第 1 个; 1- 连续查找; 2- 查找所有 

nStartPage :起始页 ( 从 0 开始 ) 

nEndPage :结束页 

返回值:页码 ,x,y, 保留值 

获取对应 DJContentView 的 px 坐标位置 

getScreenPointFrom5W(page:number, x:number, y:number):Point| null 

# 功能:获取对应 DJContentView 的坐标位置 

参数: 

page :文档页码 

x : x 单位 :1/50000 

y : y 单位: 1/50000 

返回值: {x:1,y:2} 

获取对应 DJContentView 的 px 坐标位置 

getScreenRectFrom5W(page:number, left:number, top:number, right:number, 

bottom:number):DJRect|null 

功能:获取对应 DJContentView 的坐标位置 

参数: 

page :文档页码 

left : left 单位 :1/50000 

top : top 单位: 1/50000 

right : right 单位 :1/50000 

bottom : bottom 单位: 1/50000 

返回值: {left:1,top:2,right:1,bottom:2} 

获取对应 DJContentView 的 px 坐标位置 

getScreenRectFromNode(nodeId:string):DJRect|null 

功能:获取对应 DJContentView 的坐标位置 

参数: 

nodeId :节点 id 

返回值: {left:1,top:2,right:1,bottom:2} 

设置可以通过点击节点编辑 aip 上的文本内容 

setCanClickEdit(edit:number) 

功能:设置在 OperType.NONE 和 OperType.WRITE 状态下支持点击文 本内容进行再编辑 

参数: 

edit : 0- 不支持点击编辑; 1- 支持点击编辑; 2- 保留的后续扩展功能参 数 返回值:无 

注:在 OperType.WRITE 状态下,点击编辑节点功能具有特殊性:笔 ” ” 只能进行手写,不能触发 点击编辑 的功能,只有手指在能拖动文档 ” ” 的情况下,手指才具有 点击编辑 的功能,如果手指也能进行手写, 则手指也不具有点击编辑的功能。 

设置可以通过长按选中 aip 上本人自己的节点 

setCanLongPress(longPress:number) 

功能:设置在 OperType.NONE 和 OperType.WRITE 状态下支持长按选 中节点,选中后可以拖动或者缩放或者编辑节点 

参数: 

longPress : 0- 不支长按选中; 1- 支持长按选中; 2- 保留的后续扩展功 能参数 

返回值:无 

注:在 OperType.WRITE 状态下,长按选中功能具有特殊性:笔只能 ” ” 进行手写,不能触发 长按选中 的功能,只有手指在能拖动文档的情 ” ” 况下,手指才具有 长按选中 的功能,如果手指也能进行手写,则手 指也不具有长按选中的功能。 

# 设置文档打开之后显示的页码位置 

setToPageAfterOpen(page:number) 

功能:设置文档打开之后显示的页码位置,默认打开显示首页 参数: 

page : 0- 表示首页; -1- 表示最后一页 

返回值:无 

# 设置翻页模式 

setPageMode(pagemode:PageMode) 

功能:设置翻页模式,默认上下连续页 参数: 

pagemode : 

PageMode.MultiPage 上下连续页 

- PageMode.SinglePage 单页模式 左右翻页 

- PageMode.SinglePage_Y 单页模式 上下翻页 

返回值:无 

# 设置单页模式下是否允许通过滑动翻页 

setAllowTurnPage(turnpage:boolean) 

功能:设置是否允许通过滑动进行翻页,默认允许 参数: 

turnpage : true- 允许; false- 不允许 

返回值:无 

# 设置文档滑动翻页的翻页临界距离 

setTurnPageRatio(ratio:number) 

功能:设置文档滑动翻页的翻页临界距离,默认 ratio 为 0.3 ,表示 0.3* 屏幕宽度的距离 

# 参数: 

ratio :取值范围 0-1, 表示的临界翻页距离为 ratio* 屏幕宽度 

返回值:无 

# 获取文本框中的文本内容 

getNodeText(nodeName:string):string 

功能:获取文本框中的文本内容 

参数: 

nodeName :节点名称 

返回值:文本内容 

# 设置文档背景颜色 

setPageBackcolor(pageBackcolor:Color | string | null):number 

功能:设置文档背景颜色 

参数: 

pageBackcolor :背景颜色,如: #ECFEEA 或者 Color.Green( 传 null表示取消颜色设置,使用默认白底色 ) 

注:关于设置文档背景色,需要文档本身可支持设置背景色,如果文 档本身数据带有不透明背景,该颜色设置看不到效果; 

插入空白页 

insertEmptyPage(pageIndex?:number,isA4?:boolean):number 

功能:插入空白页 

参数: 

pageIndex :插入位置: 0- 代表首页位置; -1 或者不传表示最后页位 置; 

isA4 : true- 表示插入纸张为 a4 大小; false 或者不传 - 表示插入纸张同 首页大小相同; 

返回值: 1- 成功;其他 - 失败 

# 控件界面截图 

getScreenShot():PixelMap 

功能:控件界面截图 

参数: 

无 

返回值:界面图的 PixelMap 对象; 

# 开启窗口改变自适应改变文档大小 

public setCanAdaptive(canAdaptive: boolean) 

功能: DJContentView 窗口大小变化时,重新初始化文档大小到占满 屏幕; 

参数: 

canAdaptive :默认为 false 

返回值:无 

注:鸿蒙二合一的 PC 设备上不支持调用该方法设置为 true; 

# 盖章接口 

addMoveSealEntity(entity: SealEntity, page: number, x: number, y: number): void 

功能:盖章,多用于扩展对接外部签名的盖章方式 

参数: 

entity :盖章的一些配置对象, SealEntity 是一个 abstract class , SDK 中 LmGmSealEntity 集成自 SealEntity ,其中封装了跟龙脉 UKey 盖章相 关的签名接口; 

page :盖章页码 

x :盖章位置 x 坐标 

y :盖章位置 y 坐标 

返回值:无 

注: 

- 1) 使用该盖章接口一般提供 DEMO ,结合 DEMO 代码进行理解; 

2) 盖章结果在 receiveDJMsg 回调中返回: data=1 表示盖章成功;其 他表示失败; msg 表示失败原因; ( 详情请参考 DEMO) 

# 获取空白手写板上的矢量签批数据 

public getVectorWriteP1024():string 

- 功能:空白手写板 获取签批内容的矢量数据 

参数: 

无; 

返回值:矢量字符串 ( 格式如下 ) 

w,h,P1024(x1,y1,p1;x2,y2,p2;...)(x1,y1,p1;x2,y2,p2;...) 

(x1,y1,p1;x2,y2,p2;...)... 

注:使用该接口需开启配置 setRecordSignData(true); 

对应还原的方法: setValueEx(nodename, 44, 0/1, signDatas) 

注: 0- 原始大小的比例; 1- 会放大填充 

setValue 方法介绍 

说明: 0x 代表的是十六进制数据,在往接口中传值的时候,需要传对 应的十进制数到接口,比如: 

0x2000 表示 2*16*16*16 = 8192 

- 1) 带附加用户的文本框开启用户等级排序功能 ( 打开文当前调用 ) 

setValue("ADD_FORCETYPE_VALUE5", 0x80000) 

- 2) 设置字体目录 ( 打开文当前调用 ) 

setValue("SET_FONTFILES_PATH", dirpath) 

# 设置水印 

设置水印模式 ( 该设置为水印设置必须项 ) 

setValue("SET_WATERMARK_MODE",mode); 

mode 取值: 

- 1- 居中 ( 文字 ) 

- 2- 平铺 ( 文字 ) 

- 3- 居中带阴影 ( 文字 ) 

# 4- 平铺带阴影 ( 文字 ) 

5- 居中 ( 图片 ) 

6- 平铺 ( 图片 ) 

# 2] 设置水印的内容 

setValue("SET_WATERMARK_TEXTORPATH", 文字 /picPath); 

注:传空字符串会清空水印内容; 

# 3] 设置水印透明度 

setValue("SET_WATERMARK_ALPHA","alpha"); alpha 取值: 1-63( 愈大愈透明 ) 

4] 设置文字水印的文字颜色 

setValue("SET_WATERMARK_TEXTCOLOR","color"); color : int 类型的 rgb 颜色值或者 HTML 颜色字符串 (#ff000000) 

5] 设置水印旋转角度 (*0.1 度 ) 

setValue("SET_WATERMARK_ANGLE","value"); value 取值: -3600 至 3600( 左旋转 360° 至右旋转 360°) 

6] 设置水印缩放比例 

setValue("SET_WATERMARK_TXTHORIMGZOOM","value"); value 取值: 

- 文字模式 字体高度(可以为负,单位为相对于页面高度千分之一)。 - 图片模式 缩放比例 

例如: setValue("SET_WATERMARK_TXTHORIMGZOOM","1000") 表 示当前水印高度为页面高度 

6-2] 设置文字水印字号 ( 单位磅 pt) 

setValue("SET_WATERMARK_TXTFONTSIZE","22") 

# 7] 设置文字水印字体类型 

contentView.setValue("SET_WATERMARK_ADDITION","5") 

注: 1: 宋体 ,2: 仿宋 ,3: 楷体 ,4: 隶书 ,5: 黑体 

# 设置水印边距 

setValue("SET_WATERMARK_POSX","8000")// 设置左右边距 setValue("SET_WATERMARK_POSY","6000")// 设置上下边距 注:单位为 1/50000 

说明:文档宽高均划分为 50000 大小,设置 8000 等价于 (8000/50000)* 页宽 ( 或页高 ) 的大小; 

- 框选文字 按文字块排列,否则文字会按照位置排列 (0x10) 

setValue("ADD_FORCETYPE_VALUEA", “16”) 

# - 框选文字 标记色 

contentView.setValue("PREDEF_HIGHLIGHT_COLOR","color") color : int 类型的 rgb 颜色值或者 HTML 颜色字符串 (#000000) 配置弹框手写能擦 (0x80000) 

setValue("SET_TEMPFLAG_MODE2_ADD", "524288") 

getValueEx 方法介绍 

getValueEx(nodeName,6,"",0,"") 获取节点 x 坐标 

getValueEx(nodeName,7,"",0,"") 获取节点 y 坐标 

getValueEx(nodeName,8,"",0,"") 获取节点 w 

getValueEx(nodeName,9,"",0,"") 获取节点 h 

getValueEx(nodeName,20,"",0,"") 获取节点所在页码 

getValueEx(nodeName,21,"",0,"") 获取节点所属用户 

getValueEx(nodeName, 2, "", 0, "") 获取节点文本内容 ( 如果是空的文 本内容,返回值为 errorcode 开头的字符串 ,) 

getValueEx(nodeName, 14, "jpg", 0, "") 获取节点对应图片 

getValueEx(nodeName, 2, username, 0, "")// 适用于带附加用户的文 本框取值,取最后一条且是 username 的记录 

getValueEx(nodeId,54,"",0,"")// 获取带有标记色的文字内容; 

setValueEx(nodeId,54,1,str)// 给标记色节点设置文字内容; 

setValueEx 方法介绍 

1) 文档剪裁显示 ( 打开文档后调用 ) 

setValueEx("SET_EXTEND_PAGE", 2,0," 起始页 ; 结束页 ; 左扩展 ; 上扩展 ; 右扩展 ; 下扩展 ;") 

参数 1 :固定值 

参数 2 : 0 表示按比例扩展, 2 表示按 0.01 毫米单位扩展 

参数 3 :固定值 0 

起始页:从 0 开始 

# 结束页: -1 表示最后页; 

# 打开文当前调用方式: 

preSetValueEx("SET_EXTEND_PAGE",2,0,"0;-1;0;-3700;0;-2500") ; 注:该方法效率更高,调用该方法,会在文档打开后界面未渲染之前 进行剪裁操作,剪裁后再渲染界面; 

# DjUtils 方法介绍 

显示设备信息 dialog 

DJUtils.showDeviceInfo(context: UIContext) 

功能:显示设备信息 dialog ,支持复制设备信息到系统剪贴板 参数: 

context :系统 UIContext 

2in1 笔记本设备 

注:文档下面提到 ”PC” 内容均指 2in1 设备; 

PC 键盘功能集成 

需要 app 层捕捉键盘事件,传递到 SDK ,具体方法如下: 

支持功能: 

键盘上下键:上翻 / 下翻文档 

PC 支持功能 

支持触摸板双指拖动文档;支持鼠标滚轮轮动文档;支持上下箭头按 键滚动文档 

支持触摸板双指缩放文档;支持 ctrl+ 滚轮缩放文档; 

# PC 插龙脉 UKey 盖章功能 

# 注: 

UKey 暂时仅支持从 UKey 中读取 1 个印章,所以不涉及多个印章选章的 功能,下个版本支持多个印章选章功能; 

暂时仅支持国密证书签名盖章,未支持 RSA 证书的 UKey; 

操作龙脉 UKey 相关接口 (LmUtil 中封装 ) 

连接 UKey 设备 

static connectLmUkey():LmRet 

功能:连接 UKey 

参数: 

无 

返回值: LmRet 对象 

注: LmRet 介绍 

LmRet{ 

- code:number = 0;//1- 成功;其他 失败; 

msg:string = "";// 失败原因; 

} 

# 验证 Pin 码 

static verifyPin(inputPin:string):LmRet 

功能:验证 Pin 码 

参数: 

inputPin : pin 码 

# 返回值: LmRet 对象 

# 注: pin 码验证成功才能从 UKey 读取印章、证书、盖章; 

# 读取 UKey 中的证书 

static readCert():ReadCertRet 

功能:从 UKey 中读取证书 

参数: 

无 

返回值: ReadCertRet 对象 

注: ReadCertRet 介绍 

ReadCertRet{ 

- code:number = 0;//1- 成功;其他 失败; 

type:number = -999;//1-RSA 容器; 2-SM2 容器; 0- 未定、尚未分配 类型或者为空容器; 

msg:string = "";// 失败原因 

certBase64:string = "";// 公钥证书 base64 

} 

# 读取 UKey 中的印章 

static readSeal():ReadSealRet 

功能:从 UKey 中读取印章 

参数: 

无 

返回值: ReadSealRet 对象 

注: ReadSealRet 介绍 

ReadSealRet{ 

- code:number = 0;//1- 成功;其他 失败; msg:string = "";// 失败原因 seals:ArrayList<LmSealBean>|null = null;// 印章列表数据 

} 

LmSealBean { 

id:number = 0;// 印章 id( 预留,暂未有数据 ) sealname:string = "";// 印章名称 ( 预留,暂未有数据 ) sealtype:number = 0;// 印章类型 ( 预留,暂未有数据 ) picbase64:string = "";// 预览图 base64( 预留,暂未有数据 ) sealbase64:string = "";// 印章 base64 

} 

关闭 UKey 连接 

static disConnectLmUkey():void 

功能:关闭连接 

参数: 无 返回值:无 

调用龙脉 UKey 盖章操作 

盖章代码 

LmGmSealEntity lmGmEntity = new LmGmSealEntity(SealEntity.FILETYPE_OFD,UKey 中读出的证书 base64) 

this.lmGmEntity.setSeal(SealEntity.SEALTYPE_SEL,`STRDATA: ${sealbase64}`) 

this.djController.addMoveSealEntity(this.lmGmEntity,page,x,y); 

this.djController.freshClearPDF(); 

注: LmGmSealEntity 是 SDK 中封装的跟龙脉 UKey 签名签章相关的内 容; addMoveSealEntity 方法是 SDK 封装的一个盖章的方法,该方法 无返回值,盖章结果在 receiveDJMsg 回调中返回: data=1 表示盖章 成功;其他表示失败; msg 表示失败原因; ( 详情请参考 DEMO)
