# 进入首页 UIAbility 的子类 EntryAbility 

```
import { UploadFile } from '@cisetech/apm';
UploadFile(this.context,launchParam,urlOauth20);
```

# 参数说明 

`this.context` : `EntryAbility//` 必填 `launchParam` : `AbilityConstant.LaunchParam//` 必填 `urlOauth20` : `token` 地址 `urlOauth//` 必填 

# 返回错误代码说明 

`200` :成功 `401` : `token` 无效 `404` :无资源 `500` :响应超时 

# UploadFile 具体实现 

**`export function UploadFile`** `(context: common.UIAbilityContext,launchParam: AbilityConstant.LaunchParam,url: stri` **`let`** `session = rcp.createSession()` _`//`_ 创建会话 **`let`** `req =` **`new`** `rcp.Request(url, 'GET')` _`//`_ 创建 _`get`_ 请求 `session.fetch(req).then((res: rcp.Response) => {` _`//`_ 发送请求获取应答 `LogUtil.debug(`${JSON.stringify(res)}`);` **`if`** `(res.statusCode == 200) {` **`let`** `result = res.toJSON();` **`if`** `(result != null) {` **`let`** `token: string = result["data"]['access_token']; DbHelper.getInstance().query(` **`new`** `CallBackOpenThenUpLoadImpl(token)); FaultLoggerCombinUtil.getInstance().setToken(token); FaultLoggerCombinUtil.getInstance().queryCrash(launchParam); } } }).catch((e: Error) => { }).finally(() => { session.close()` _`//`_ 关闭会话 `}) }`
