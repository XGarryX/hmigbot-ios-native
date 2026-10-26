# WAF BOT 1.0.0 Harmony接入文档

# Harmony应用集成SDK

您需要在应用中集成SDK,才能在控制台BOT管理中配置App防爬场景化规则。本文介绍了如何为

Harmony应用集成WAF App防护SDK(以下简称SDK)。

# 背景信息

App防护SDK主要用于对通过App客户端发起的请求进行签名。WAF服务端通过校验App请求签名,识别

App业务中的风险、拦截恶意请求,实现App防护的目的。

关于App防护提供的SDK所涉及的隐私政策,请参见Web应用防火墙App防护SDK隐私政策。

# 使用限制

●

需要在Harmony Next 4.1 及以上版本的系统运行,API版本最低支持12。

●

init初始化接口存在耗时操作,调用后不能立即同步调用vmpSign接口,请确保SDK的初始化接口和签

名接口调用时间间隔2秒以上。

●

滑块创建cptCreate涉及UI操作,需要在主线程中进行调用。

●

不支持模拟器模式调试

仅支持开启字节码打包方案

●

# 前提条件

●

已获取Harmony应用对应的SDK。

获取方法:请提交工单,联系产品技术专家获取SDK。

说明Harmony应用对应的SDK包含1个HAR文件,文件名为HarmonyOS-AliTigerTally-X.Y.Z-

date.har,其中X.Y.Z表示版本号,date表示打包日期。

●

已获取SDK认证密钥(即appkey)。

开启BOT管理后,即可在新建或编辑防护模板的防护场景定义配置导向的APP SDK集成中单击获取并

复制appkey,获取SDK认证密钥。该密钥用于发起SDK初始化请求,需要在集成代码中使用。

说明每个阿里云账号拥有唯一的appkey(适用于所有接入WAF防护的域名),且Android、iOS和

Harmony应用集成SDK时都使用该appkey。

| 认证密钥示例: ****OpKLvM6zliu6KopyHIhmneb ****u4ekci2W8i6F9vrgpEezqAzEzj2ANrVUhvA _ XMwYzgY ****vc51aEQlRovkRoUhRlVsf4IzO9dZp6nN ****Wz8pk2TDLuMo4pVIQvGaxH3vrsnS _ _ QiK****  步骤一:新建工程 以DevEco Studio工具为例,新建一个Harmony工程,并按照配置向导完成创建 。创建好的工程目录如下 图所示 。 步骤二:集成HAR包 1. 将HarmonyOS-AliyunTigerTally-X.Y.Z-date.tgzSDK包解压,将获取到的HAR文件拷贝到工程中存 放HAR包的目录 。 建议参考鸿蒙官方文档放至libs目录下。 | ****OpKLvM6zliu6KopyHIhmneb ****u4ekci2W8i6F9vrgpEezqAzEzj2ANrVUhvA |  |
|---|---|---|

|  | QiK**** |
|---|---|

2.打开App的oh-package.json5文件,在dependencies中添aliyuntigertally、captcha编译依赖,示例如

下:

重要您需要将aliyuntigertally-X.Y.Z-date.har文件的版本号X.Y.Z替换成您获取的HAR文件的版本

号。

```
{
  ...
"dependencies": {
"aliyuntigertally": "file:../libs/aliyuntigertally-X.Y.Z-date.har",
"captcha": "file:../libs/aliyuncaptcha-X.Y.Z-date.har",
    ...
  }
}
```

# 步骤三:为应用申请权限

为增强SDK的防护效果,当前需要以下权限:

| 权限 | 是否必须 | 说明 |
|---|---|---|
| ohos.permission.INTERNET | 是 | 联网权限 。SDK需要联网才能 使用 。 |
| ohos.permission.GET NETW _ ORK INFO _ | 是 | 网络状态确认 。SDK可以根据 网络状态提供更好的服务 。 |

| ohos.permission.STORE PER _ SISTENT DATA _ | 否(推荐赋予) | 允许应用存储持久化的数据 。 SDK可以增加设备指纹稳定性 |
|---|---|---|
| ohos.permission.DISTRIBUTE D DATASYNC _ | 否(推荐赋予) | 多设备协同 。SDK可以检测多 设备状态,增强安全效果 |
| ohos.permission.APP TRACK _ ING CONSENT _ | 否(推荐赋予) | 获取广告标识符权限 。SDK获 取IDFA信息,增强设备ID稳定 性 |

# 步骤四:添加集成代码

## 一、添加头文件

```
import { TigerTallyAPI, TTCode } from'aliyuntigertally';
import { TTCaptcha, TTCaptchaOption, TTCaptchaListener} from
'aliyuntigertally';
```

## 二、设置数据签名

1.设置业务自定义的终端用户标识,方便您更灵活地配置WAF防护策略。

```
/**
 * 设置用户账户
 *
 * @param account 账户
 * @return 错误码
 */
public staticsetAccount(account: string): number
```

○

参数说明:account,string类型,表示标识一个用户的字符串,建议您使用脱敏后的格式。

○

返回值:number类型,返回是否设置成功,0表示成功,-1表示失败。

○

示例代码:

```
// 游客身份可以暂时先不setAccount,直接初始化;登录以后调用setAccount和重
新初始化
letaccount: string = "user001";
TigerTallyAPI.setAccount(account);
```

2.初始化SDK,执行一次初始化采集。

一次初始化采集表示采集一次终端设备信息,您可以根据业务的不同,重新调用init函数进行初始化

采集。

```
/**
 * 初始化回调
 */
export interfaceTTInitListener {
/**
   * SDK状态码回调
   * @param code
   */
onInitFinish: (code: number) => void;
}
/**
 * SDK 初始化,带 callback
 *
 * @param ctx
 * @param userAppKey
 * @param options 各类参数选项
 * @param listener
 */
public staticinit(ctx: Context, userAppKey: string,
options: Map<string, string> | null,
listener: TTInitListener | null): number
```

参数说明:

○

■

ctx:Context类型,传入您应用的上下文。

■

userAppkey:string类型,设置为您的SDK认证密钥。

■

options:Map<String, String>类型,信息采集可选项,默认可以为null。可选参数如下

| 字段名 | 说明 | 示例 |
|---|---|---|
| IPv6 | 是否使用IPv6域名上报设备信息。 默认为“0”:使用IPv4域名;“1”:使用IPv6域名。 | “1” |
| Intl | 是否使用国际域名上报设备信息。 默认为“0”:国内上报;“1”:国际上报。 | “1” |

■

listener:TTInitListener类型,SDK初始化回调接口,可在回调中判断初始化结果的具体

状态,默认可以传null。

| TTCode | Code | 备注 |
|---|---|---|
| TT SUCCESS _ | 0 |  |
| TT NOT INIT _ _ | -1 |  |
| TT NOT PERMISSION _ _ | -2 |  |

| TT UNKNOWN ERROR _ _ | -3 |
|---|---|
| TT NETWORK ERROR _ _ | -4 |
| TT NETWORK ERROR EMPTY _ _ _ | -5 |
| TT NETWORK ERROR INVALID _ _ _ | -6 |
| TT PARSE SRV CFG ERROR _ _ _ _ | -7 |
| TT NETWORK RET CODE ERRO _ _ _ _ R | -8 |
| TT APPKEY EMPTY _ _ | -9 |
| TT PARAMS ERROR _ _ | -10 |
| TT FGKEY ERROR _ _ | -11 |
| TT APPKEY ERROR _ _ | -12 |

-8

网关返回失败

○

返回值:number类型,返回初始化结果,0表示成功,-1表示失败。

○

示例代码:

```
// appkey代表阿里云客户平台分配的认证密钥
constappkey: string = "******";
// 可选参数, 可配置IPv6与国际上报
letoptions: Map<string, string> = newMap<string, string>();
options.set("IPv6", "0");// 配置为IPv4
options.set("Intl", "0");// 配置为国内上报
// 一次初始化采集,代表一次设备信息采集,可以根据业务的不同,重新调用函数
init初始化采集
letret: number = TigerTallyAPI.init(getContext(this), appkey,
options, null);
```

3.数据签名。

对输入数据input进行签名处理,并且返回wtoken字符串用于请求认证。

```
/**
 * 数据签名
 *
 * @param type  数据类型
 * @param input 签名数据
 * @return wToken
 */
```

参数说明:

○

■

type:number类型,设置数据签名类型,固定取值0。

■

input:string类型,表示待签名的数据,一般是整个请求体request body。

○

返回值:string类型,返回wtoken字符串。

○

示例代码:

```
letbody: string = "i am the request body, encrypted or not!";
letwtoken: string = TigerTallyAPI.vmpSign(0, body);
```

说明

当wtoken为以下字符串时表示初始化流程存在异常:

■

●

you must call init first:表示未调用init函数。

●

you must input correct data:表示传入数据错误。

●

you must input correct type:表示传入类型错误。

●

inner error:表示系统内部错误。

### 三、二次校验

1.判断结果。

根据response中cookie和body字段判断是否要进行二次校验。header中可能存在多个Set-Cookie。

```
/**
 * 判断是否进行二次校验
 *
 * @param cookie  cookie
 * @param body    body
 * @return 0:通过 1:二次校验
 */
public staticcptCheck(cookie: string, body: string): number
```

参数说明:

○

■

cookie:string类型,设置请求response中全部cookie。

■

body:string类型,设置请求response中全部body。

○

返回值:number类型,返回决策结果,0表示通过,1表示需要二次校验。

○

示例代码:

```
letcookie: string = "key1=value1;kye2=value2;";
letbody: string = "....";
letrecheck: number = TigerTallyAPI.cptCheck(cookie, body);
```

2.创建滑块。

根据cptCheck返回结果决定是否要创建一个滑块对象,TTCaptcha对象提供show和dismiss方法,对

应显示滑块和隐藏滑块窗口。TTCaptchaOption封装了滑块可配置的参数,TTCaptchaListener包含

了滑块的2种回调状态。

```
/**
 * 创建滑块对象
 *
 * @param ctx
 * @param option    参数
 * @param listener  回调
 * @return 滑块验证对象
 */
public staticcptCreate(ctx: UIContext, option: TTCaptchaOption,
listener: TTCaptchaListener): TTCaptcha
/**
 * 滑块对象
 */
export classTTCaptcha {
/**
     * 显示滑块
     */
public show(): void
/**
     * 隐藏滑块
     */
public dismiss(): void
}
/**
 * 滑块参数
 */
export classTTCaptchaOption {
// 是否支持点击空白处隐藏滑块
cancelable: boolean;
}
/**
 * 滑块回调
 */
export interfaceTTCaptchaListener {
/**
   * 验证成功
   *
   * @param captcha 滑块对象
   * @param code, 默认为 traceId
   */
success: (captcha: TTCaptcha, code: string) => void;
/**
   * 验证失败或异常
   *
   * @param captcha 滑块对象
   * @param code    错误码
   */
fail: (captcha: TTCaptcha, code: string) => void;
}
```

参数说明:

○

■

ctx:UIContext类型,设置当前页面UIContext。

■

option:TTCaptchaOption类型,设置滑块配置参数。

■

listener:TTCaptchaListener类型,设置滑块状态回调。

○

返回值:TTCaptcha类型,返回滑块对象。

○

示例代码:

```
letoption: TTCaptchaOption = newTTCaptchaOption();
// option.cancelable = false;
letcaptcha: TTCaptcha =
TigerTallyAPI.cptCreate(this.getUIContext(), option, {
success: (captcha: TTCaptcha, code: string) => {
    console.log("captcha success:", code);
    captcha.dismiss();
  },
fail: (captcha: TTCaptcha, code: string) => {
    console.log("captcha failed:", code);
    captcha.dismiss();
  }
});
captcha.show();
```

说明

■

创建滑块cptCreate接口涉及UI操作,需要在主线程中调用

| 说明 | 验证异常,表示在加载滑块过程中检测到异常情况;验证失败,表示用户滑动结束后检测异 |
|---|---|

常情况。

具体错误码如下所示:

■

1001:验证失败判定不通过。

■

1002:系统异常。

■

1003:参数错误。

■

1005:验证取消。

■

8001:滑块唤起错误。

■

8002:滑块验证异常。

■

8004:网络错误。

# 最佳实践示例

```
import http from '@ohos.net.http';
import { BusinessError } from '@ohos.base';
import { TigerTallyAPI, TTCode } from 'aliyuntigertally';
import { TTCaptcha, TTCaptchaOption, TTCaptchaListener} from
'aliyuntigertally';
@Entry
@Component
structIndex {
  build() {
    ...
  }
  aboutToAppear() {
this.onTest();
  }
async onTest() {
constAPP_KEY: string = "xxxxxx";
constAPP_URL: string = "xxxxxx";
constAPP_HOST: string = "xxxxxx";
```

|  | // 初始化 let options: Map<string, string> = new Map<string, string>(); options.set("IPv6", "0");// 配置为IPv4 options.set("Intl", "0");// 配置为国内上报 let retCode: number = TigerTallyAPI.init(getContext(this), APP KEY, _ options, null); console.log("TigerTally init:", retCode); // 不能立即同步调用 const sleep = (duration: number) => { return new Promise<void>(resolve => setTimeout(resolve, duration)); }; await sleep(2000); // 数据签名 let data: string = "i am the request body, encrypted or not!"; let wtoken: string = TigerTallyAPI.vmpSign(0, data); console.log("TigerTally vmpSign:", wtoken); // 请求接口 this.doPost(APP URL, APP HOST, wtoken, data, (code, cookie, body) _ _ => { // 判断是否需要显示滑块 let recheck: number = TigerTallyAPI.cptCheck(cookie, body); console.log("TigerTally captcha check:", recheck); if (recheck === 0) return; this.doShow(); }); } // 显示滑块 async doShow() { console.log("滑块显示"); let option: TTCaptchaOption = new TTCaptchaOption(); // option.cancelable = false; let captcha: TTCaptcha = TigerTallyAPI.cptCreate(this.getUIContext(), option, { success: (captcha: TTCaptcha, code: string) => { console.log("captcha success:", code); captcha.dismiss(); |  |
|---|---|---|

|  | }, fail: (captcha: TTCaptcha, code: string) => { console.log("captcha failed:", code); captcha.dismiss(); } }); captcha.show(); } // 发送请求 async doPost(url: string, host: string, wtoken: string, body: string, callback: (code: number, cookie: string, body: string) => void): Promise<void> { let response code: number = 0; _ let response body: string = ""; _ let response cookie: string = ""; _ try { let httpRequest = http.createHttp(); let response: http.HttpResponse = await new Promise<http.HttpResponse>((resolve, reject) => { httpRequest.request( url, { method: http.RequestMethod.POST, header: { "Content-Type": "text/x-markdown", "User-Agent": "", "Host": host, "wToken": wtoken, }, extraData: body.length > 0 ? body : undefined, connectTimeout: 12000, }, (err: BusinessError, data: http.HttpResponse) => { if (!err) { resolve(data); } else { reject(err); } httpRequest.destroy(); } ); }); |  |
|---|---|---|

```
if (response != null) {
        response_code = response.responseCode;
letsuccess: boolean = (response_code === 200);
if (success) {
          response_body = response.result ? response.result.toString()
: "";
          response_cookie = response.header["set-cookie"] ?
response.header["set-cookie"].join(";") : "";
        } else {
          response_body = response.result ? response.result.toString()
: "";
        }
      } else {
        response_code = -1;
      }
      console.log("response code:", response_code);
      console.log("response body:", response_body);
      console.log("response cookie:", response_cookie);
    } catch (error) {
      console.log("response error:", error.code, error.message);
      response_code = -1;
      response_body = error.message;
    } finally {
if (callback != null) {
        callback(response_code, response_cookie, response_body);
      }
    }
```
