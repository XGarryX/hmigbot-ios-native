# **引用SDK** 

将附件中的HAR包引用到项目中,有如下两种方式: 

- 方式一:在Terminal窗口中,执行如下命令进行安装,并会在oh-package.json5中自动添加依赖。 

```
ohpm install /path/to/Qt-signed.har
```

- 方式二:在工程的oh-package.json5中设置三方包依赖,配置示例如下: 

```
"dependencies": {  "package": "file:/path/to/Qt-signed.har"}
```

依赖设置完成后,需要执行 **ohpm install** 命令安装依赖包,依赖包会存储在工程的oh_modules目录下。 

```
ohpm install
```

# **全流量校准调用** 

在UIAbility类中的onCreate生命周期方法中调用如下方法初始化SDK: 

Qt.init(ability: UIAbility, QMAppKey: string = "", uid: string = "", callback: Function) 

使用QMAppKey初始化SDK, uid为加码方使用的用户唯一标识,callback为SDK数据上报回调方法 ,实现 callback方法可查看SDK上报数据详细信息,如下: 

```
{
"msg": "success",
"server": "10.10.4.9",
"code": 0,
"mySelfUid": "123456789",
"qmUid": "eceedeb1d8b38f53798f125c07ee5f6c",
"ts": 1722929565,
"scene": "onForeground"
}
```

code = 0 表示数据上报成功 

示例代码: 

```
export defaultclassEntryAbilityextendsUIAbility {
onCreate() {
```

`const myCallBack = (message: string) => { hilog.info(0x0000, 'QuestMobile', '%{public}s', 'QuestMobile DataCallBack : ' + message); } Qt.enableLog=true; // SDK` 日志控制开关 `Qt.init(this, 'testAppKey', '123456789', myCallBack); } };` 

# **记录事件(可选)** 

## 方法 

```
Qt.onEvent(ability: UIAbility, eventName: string, eventValue: string = "")
```

## 具体参照如下代码 

```
Qt.onEvent(this, "play", "startPlay");
```

# **日志开关** 

```
Qt.enableLog=trueorfalse
```

日志开关默认为 `true,` 会在 `Log` 控制台打印 `SDK` 事件以及占用主线程时间等信息 `,` 也可作为判断 `SDK` 是否集成成功的标志 

## 技术支持: 

tel: 13366386286 

mail: phone@questmobile.com.cn
