> 来源: ohpm 中央仓 README(T1 信源) | 包: `ctaccount` | ohpm 最新版: 1.1.3 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

SDK安装说明
使用 ohpm install ctaccount 命令进行安装

SDK接口调用说明
1.初始化接口
【接口说明】
预取号需要激活蜂窝网络,建议尽量提前做SDK初始化,例如:EntryAbility.ets中onCreate() 进行初始化,在Index.ets中进行预取号
【调用示例】
EntryAbility.ets:
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
CtAuth.getInstance().init(this.context, "Appid", "APPsecret");
}
Index.ets:
aboutToAppear() {
CtAuth.getInstance().requestPreLogin(Ct, this.testL)
}
【请求参数】
参数名	类型	必填	说明
Ctx
Context	是
上下文
Appid
string	是
平台申请的Appid

APPsecret
string	是
平台申请的appSecret

2.预取号接口
【接口说明】
在调用该接口前,建议先做本地预判断处理,符合条件再调用预登录接口。预登录接口可获取脱敏手机号、accessCode等信息,其中脱敏手机号可用于登录界面的展示,accessCode默认有效期为60分钟。
【调用示例】
import { AuthResult, AuthResultListener, CtAuth } from 'ctaccount/Index';
import { CtSetting } from 'ctaccount/Index';

CtAuth.getInstance().requestPreLogin(new CtSetting(), new AuthResultAdapter()))
class AuthResultAdapter implements AuthResultListener {

onResult(result : AuthResult): void {
if(result != null){
const code : string = result.code;
const accessCode : string = result.accessCode;
const msg : string = result.msg;
const expiredTime : string = result.expiredTime;
const operatorType : string = result.operatorType;
const number : string = result.number;
console.log("DebugLog:"+'code:'+code+'&msg:'+msg+'&accessCode:'+accessCode+"&expiredTime:"+expiredTime+"&number:"+number+"&operatorType:"+operatorType)
AlertDialog.show(
{
title: '提示',
message: 'code:'+code+'&msg:'+msg+'&accessCode:'+accessCode+"&expiredTime:"+expiredTime+"&number:"+number+"&operatorType:"+operatorType,
autoCancel: true,
alignment: DialogAlignment.Center,
gridCount:3,
confirm: {
value: '确认',
action: () => {

            }
          }

        }
      )
    }
}
}

【请求参数】
参数名	类型	必填	说明
Ct	CtSetting
是
请求时间控制器
Listener
AuthResultListener
是
平台申请的appSecret

【响应参数】
返回结果result的json格式说明:
参数名	类型	字段含义	说明
result	AuthResult
请求结果	请求结果
result格式说明:
参数名	类型	字段含义	说明
code	String	结果码	返回参数结果码,0表示成功,
详细参考错误码定义(3.1)
Msg	String	结果信息	返回参数结果信息
详细参考错误码定义(3.1)
accessCode	String	授权码	天翼账号授权码,默认时效性60分钟
operatorType	String	运营商标识	CT电信,CU联通,CM移动,UN其他
expiredTime	int	code失效时间	表示该accessCode的有效时间,时间单位为s
number	String	脱敏号码	当前上网卡的脱敏号码
reqID	String	请求ID	当次请求ID,异常时进行排障使用
