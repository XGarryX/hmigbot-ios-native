# DevEco-Studio集成

支持版本:API 5.0.0(12),DevEco版本 6.0.2+

# 一、下载SDK

下载

乐变鸿蒙SDK下载并解压,得到文件夹lbsdk、lbsdk-default.tgz和配置文件

globalSetting.json、lebian.cfg、MyRunAbility.ets、MyBackgroundAbility.ets

注意:lbsdk文件夹是用于自定义UI,如果不需要自定义UI,只更换背景图片,请忽略该文件夹。自定

义UI请参考

UI定制说明

# 二、导入乐变鸿蒙SDK

在DevEco-Studio中启动项目,复制lbsdk-default.tgz到项目主模块的libs目录(一般是

entry/libs)(如果libs不存在,手动创建一下)。

# 三、添加SDK依赖

在主模块(一般是entry)的oh-package.json5文件中添加lbsdk和lbui的依赖:

```
"dependencies": {
// ...此处省略项目本身的sdk依赖
"@lebian/lbsdk": "file:./libs/lbsdk-default.tgz"
 }
```

# 四、修改AbilityStage

打开主模块(一般是entry)下的src/moudle.json5文件,查看srcEntry配置:

注意:是module下的srcEntry,不是abilities内的。

## 1、module里的srcEntry配置不存在

在主模块(一般是entry)的src/main/etc目录新建MainAbilityStage.ets文件,添加以下代

码:

```
import { LBAbilityStage } from'@lebian/lbsdk';

export classMyAbilityStageextendsLBAbilityStage {
onCreate() {
super.onCreate();
  }
}
```

并在moudle.json5文件中添加配置:

```
{
"module": {
//...此处省略其它配置
"srcEntry": "./ets/MainAbilityStage.ets"
//...此处省略其它配置
    }
}
```

## 2、srcEntry配置存在

找的srcEntry中配置的ets文件,让其中的AbilityStage继承LBAbilityStage,比如截图配

```
置的是./ets/MainAbilityStage.ets,则这样修改:
``````

1
import { LBAbilityStage } from '@lebian/lbsdk';
2

```

//...此处省略项目其它依赖

export class MyAbilityStage extends LBAbilityStage {

//...此处省略项目其它代码

    onCreate() {

// 下方这一行必须保留

super.onCreate();

//...此处省略项目其它代码

```

    }

```

//...此处省略项目其它代码

```

12
}

```

# 五、SDK参数配置

打开下载好的sdk文件夹,将文件lebian.cfg和globalSetting.json复制到项目主模块的

src/main/resources/rawfile/lebian/文件中(首次接入需要手动创建一下lebian文件

夹)。

```

## 1、项目参数

打开文件lebian.cfg,将文件中的参数替换成您自己的:

| 参数名称 | 参数内容说明 |
|---|---|
| main chid _ | 项目id,乐变后台的MainChId |
| client chid _ | 渠道id,由字母数字组成,如百度渠道可以设置成“baidu” |
| secid | 项目密钥,乐变后台的LEBIAN SECID _ |

## 2、功能参数

打开文件globalSetting.json,根据需要使用的功能修改相关配置:

| 参数名称 | 功能说明 |
|---|---|
| use streaming _ | 分包开关,true - 使用分包功能,false - 不使用分包功能 |
| use regeng _ | 热更开关,默认true,设为false时不会执行热更逻辑 |
| selected area _ | 0:使用乐变大陆服务器;(在中国大陆提审) 1:使用乐变海外服务器;(在其他地区提审,不包括台湾地区提审) 2:使用乐变台湾服务器;(在台湾地区提审。如港澳台用相同包,且在台湾提审, 那就统一设置为该值;(如港澳台不同包,则台湾地区提审选2.港澳提审选1)) 请注意不同服务器MainChId不同,账号和管理后台也不同。 |
| use http or https _ _ _ | 使用https请求开关, 0-使用http请求,1-使用https请求 |
| enable exit button _ _ | 下载提示框显示取消按钮,默认只显示下载按钮 |
| must check privacy _ _ | 隐私开关,true - 需要调用同意隐私api之后才能使用SDK功能, false - 不需要隐私 同意。默认是true |

## 3、公共接口

### 3.1  setPrivacyChecked 隐私同意 

| src/main/resources/rawfile/ | lebian | / |
|---|---|---|

must_check_privacy 打开之后,需要在用户同意隐私的地方调用

must_check_privacy默认是打开的,请务必在用户同意隐私后调用以下API

```
1
LebianSdk.setPrivacyChecked();
```

# 六、功能说明

## 1、分包功能

分包功能请参考

分包接口及配置说明

## 2、热更功能

热更功能请参考

热更接口及配置说明

## 3、华为闲时下载功能(推荐接入)

该功能是将分包和热更的资源静默下载到用户设备中,减少游戏启动后等待资源包下载的时间,解决

游戏启动慢的问题,为用户提供即开即玩的游戏体验。强烈推荐接入使用。

华为闲时下载功能请参考

华为闲时下载接入

# 七、添加LBRunAbility

1.将下载的SDK中的MyRunAbility.ets文件复制到工程主module的src/main/ets目录下

2.打开主module下的src/main/module.json5,在abilities中添加MyRunAbility配置,其中

description,icon,label,startWindowIcon,startWindowBackground配置和第一个

EntryAbility配置一样的。参考如下:

```
{
"module": {
// 此处省略项目配置
"abilities": [
// 此处省略游戏自己的EntryAbility配置
6
// 复制以下配置
      {
"name": "LBRunAbility",
"srcEntry": "./ets/entryability/MyRunAbility.ets",
```

| 1 1 1 1 1 1 1 1 1 1 2 2 2 2 2 2 2 2 2 2 3 3 3 3 3 3 | 0 "description": "$string:EntryAbility desc", _ 1 "icon": "$media:icon", 2 "label": "$string:EntryAbility desc", _ 3 "startWindowIcon": "$media:icon", 4 "startWindowBackground": "$color:start window background", _ _ 5 "exported": true, 6 "skills": [ 7 { 8 "actions": [ 9 "ohos.want.action.viewData" 0 ], 1 "uris": [ 2 { 3 "host": "www.loveota.com", 4 "scheme": "lbsdk", 5 "port": "8888", 6 "path": "run" 7 } 8 ] 9 } 0 ] 1 } 2 // 复制上方配置  3 ] 4 } 5 } |
|---|---|
| 八、验证SDK是否集成成功 分包SDK:启动后日志过滤日志 BwbxManager ,看到有 init end 即可。 v2.0.0SDK以后:启动后日志过滤有VersionManager相关日志就行 |  |
|  |  |
