# WebGate APP Harmony OS Next 接入文档 

#### 北京宝兰德软件股份有限公司 

Beijing Baolande Software Corporation 

#### 版权所有 侵权必究 

All rights reserved 

#### 目录 

|**1、**|**添加依赖 ............................................................................................................................................3**|
|---|---|
|**2、**|**同步和刷新项目 ................................................................................................................................3**|
|**3、**|**添加配置文件 ....................................................................................................................................4**|
|**4、**|**初始化 ................................................................................................................................................5**|
|**5、**|**WEBVIEW 监控 .................................................................................................................................7**|
|**6、**|**HTTP 监控 .........................................................................................................................................8**|
|6.1|RCP: ................................................................................................................................................................ 8|
|6.2|AXIOS: ............................................................................................................................................................ 8|

## 1. 添加依赖 

根目录新建libs 文件夹,放入bes_apm.har,在EntryAbility 所在项目的ohpackage.json5 文件中,添加bes_apm 依赖: 

"@bes/webgate": "file:../libs/bes_apm.har" 

示例: 

## 2. 同步和刷新项目 

## 3. 添加配置文件 

在resources/rawfile 中添加json 文件 

示例: 

## 4. 初始化 

在EntryAbility 的 onCreate 方法中初始化,startUpload 可以放在同意隐私协议之后: 

import { WebgateApm } from '@bes/webgate'; 

##### //初始化 

WebgateApm.init({ 

context: this.context, 

url: 'http://xxxxxxxxxxx/collector/app/api/v1/report', key: 'xxxxxxx-xxxxxx-xxxxxxx-xxxxxxxx' 

}); 

##### //开始上传数据 

WebgateApm.startUpload(); 

##### 示例: 

log 出现[BES] webgate apm init success 表示初始化成功 

## 5. webview 监控 

如果需要监控webview,需要在Web 组件下添加下面代码: 

import { WebgateApm } from '@bes/webgate'; 

.onPageEnd((event) => { 

... 

//参数1 为event,参数2 为web 对应的controller 

WebgateApm.onPageEnd(event, data.controller); 

}) 

.onConsole((event) => { 

... 

//参数1 为event,参数2 为web 对应的controller 

WebgateApm.onConsole(event, data.controller); 

return false; 

}) 

示例: 

## 6. http 监控 

http 监控目前支持rcp、axios 框架 

### 6.1 rcp: 

import { WebgateApm } from '@bes/webgate'; 

let besSession = WebgateApm.getBesSession(rcp.createSession()); 

该方法传入原有session 得到新的session,新session 发出的请求将会被监控 

### 6.2 axios: 

无感接入,使用axios 框架发出的请求都会被监控
