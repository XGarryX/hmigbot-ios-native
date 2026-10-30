- 

- 

- 

●

- 

- 

"dependencies": { 

"@ohos/axios": "2.2.0", "@sheca/cafeaturekit": "file:./libs/arm64-v8a/cafeaturekit.har "@alipay/afservicesdk": "file:./libs/arm64-v8a/afservicesdk-1. "esldtsdk": "file:./libs/arm64-v8a/esldtSDK.har", 

"@sheca/dyrzsdk_esliving": "file:./libs/arm64-v8a/dyrzsdk_esliv "@sheca/dyrzsdk_alipayauth": "file:./libs/arm64-v8a/dyrzsdk_al "@sheca/dyrzsdk": "file:./libs/arm64-v8a/dyrzsdk.har" }, 

// "querySchemes": [ "apmqpdispatch" ] 

● 

export declare class DYRZInterface { 

```arkts
static SDKVersion(): string; static startAuth(url: string, userInfo: Record<string, strin static handleAliPayAuth(want: Want): void; } 
```

● 

```arkts
declare class DYRZLivingDetection { setEnv(url: string, appId: string, appName: string): void; constructor(); verifyInit(mode: number): Promise<string>; startLivingDetect(token: string): Promise<string>; exit(): void; } 
```

● 

declare class DYRZAliPayAuth { 

canOpenAliPay(): boolean; aliPayAuth(state: string, isRelease: boolean, scheme: string 

handleAliPayAuth(want: Want): void; 

} 

● 

|import { DYRZInterface, DYRZCode } from '@sheca/dyrzsdk'|
|---|
|async testSassAuth() { // const url = ' CA '|
|//|
|const extra: Record<string, object> = { 'authType': ["bank",|
|//  userInfo idType " ", nam|
|const userInfo: Record<string, object> = { 'extra': extra }|
|// url|
|DYRZInterface.startAuth(url, userInfo,|
|(result?: Record<string, string | number | object>, erro|
|if (error) {|
|//|
|promptAction.showToast({ message: JSON.stringi|
|} else {|
|//|
|const code = result?.code as string|
|promptAction.showToast({ message: code, durati|
|}|
|})|
|} onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam)|

● 

- import { dyrzLivingInstance, DYRZLivingDetectionCode } from '@sh async testLiving() { 

- // 1. CA 

- dyrzLivingInstance.setEnv(this.serviceURL, this.appId, this // 2. 

```arkts
const initMsg = await dyrzLivingInstance.verifyInit(6) // 3. token DEMO const token = await this.requestToken(initMsg) // 4. const verifyMsg = await dyrzLivingInstance.startLivingDetect dyrzLivingInstance.exit() if (verifyMsg) { // 5. DEMO await this.requestVerifyResult(verifyMsg) console.log(' ' + verifyMsg) } else { console.log(' ') } } 
```

● 

import { dyrzAliPayAuthInstance } from '@sheca/dyrzsdk_alipayauth' 

async testAlipayAuth() { 

await dyrzAliPayAuthInstance.aliPayAuth(state, isRelease, '', (authCode) => { // }) } onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): v // dyrzAliPayAuthInstance.handleAliPayAuth(want) } 

// 1. authType 

// 2. const extra  = {"authType" : ["alipay", "mobile","bank", "foreign"]
