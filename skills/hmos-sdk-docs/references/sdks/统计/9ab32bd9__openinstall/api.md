# preInit 

接口描述:应用启动时预初始化 调用示例: 

```
OpenInstall.preInit(abilityStage.context)
```

# init 

## 接口描述:同意《隐私政策》之后初始化 调用示例: 

```
OpenInstall.init(uiAbility.context)
```

# getWakeUp 

## 接口描述:获取拉起参数 调用示例: 

```
OpenInstall.getWakeUp(want).then(opData => {
console.log('OpenInstall', 'getWakeUp result : ' + JSON.stringify(opData));
})
```

# getInstall 

## 接口描述:获取安装参数 调用示例: 

```
OpenInstall.getInstall().then((result: OpData) => {
console.log("OpenInstall", "getInstall result : " + JSON.stringify(result));
}).catch((reason: OpError) => {
console.log("OpenInstall", "getInstall error : " + JSON.stringify(reason));
})
```

# reportRegister 

接口描述:注册量统计 调用示例: 

```
OpenInstall.reportRegister().then(_ => {
console.log("OpenInstall", "reportRegister success");
}).catch((reason: OpError) => {
console.log("OpenInstall", "reportRegister error : " + JSON.stringify(reason));
})
```

# reportEffectPoint 

## 接口描述:效果点统计 调用示例: 

```
OpenInstall.reportEffectPoint("effect_test", 1).then(_ => {
console.log("OpenInstall", "reportEffectPoint success");
}).catch((reason: OpError) => {
console.log("OpenInstall", "reportEffectPoint error : " +
JSON.stringify(reason));
})
```

# reportEffectPoint 

## 接口描述:效果点明细统计 调用示例: 

```
let extraMap = new Map<string, string>()
extraMap.set("x", "1")
extraMap.set("y", "z")
console.log(JSON.stringify(extraMap));
OpenInstall.reportEffectPoint("effect_detail", 30, extraMap).then(_ => {
console.log("OpenInstall", "reportEffectPoint with params success");
}).catch((reason: OpError) => {
console.log("OpenInstall", "reportEffectPoint with params error : " +
JSON.stringify(reason));
})
```

# reportShare 

## 接口描述:裂变分享 调用示例: 

```
OpenInstall.reportShare("u10011", "QQ").then(_ => {
console.log("OpenInstall", "reportShare success");
}).catch((reason: OpError) => {
console.log("OpenInstall", "reportShare error : " + JSON.stringify(reason));
})
```
