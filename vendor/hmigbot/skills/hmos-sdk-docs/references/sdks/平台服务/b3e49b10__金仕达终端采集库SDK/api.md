``` 

```

## 2.1 接口说明 

getSystemInfo ## 获取采集信息 getApiVersion ## 获取采集版本 ``` 

## 2.2 导入接口 

``` 

import { getSystemInfo, getApiVersion } from 'libkcy_hm'; ``` 

```

## 2.3 调用接口示例 

``` 

private testApiDemo() { 

// 获取采集库版本 

let libraryVersion = getApiVersion(); console.log(" 系统的版本为 :" + libraryVersion); 

// 获取采集信息 

let systemInfo = getSystemInfo(); 

systemInfo.then(result => { 

console.log(" 系统的加密信息为 :" + result); 

}); 

} 

```
