# **SDK 集成指南(Harmony)** 

## **工程添加** 

#### 将mintunnelsdp.har放入项目中 需集成的模块的oh-package.json5中添加 

```
{
"dependencies":{
"mintunnelsdp":"pathto/mintunnelsdp.har",
}
}
```

## **权限介绍** 

```
{
"requestPermissions":[
{
"name":"ohos.permission.INTERNET"
},
{
"name":"ohos.permission.GET_NETWORK_INFO"
},
{
"name":"ohos.permission.GET_WIFI_INFO"
}
]
}
```

以上权限均已在sdk中声明,集成过程中无需再次声明 

## **代码调用** 

### **参数配置** 

```
参数配置要求在隧道所有方法调用前设置
import{
  AsyncTunnelClient, ClientConfig, AppInfo
}from"mintunnelsdp";
const clientConfig: ClientConfig ={...}
const appInfo: AppInfo ={...}
AsyncTunnelClient.clientConfig = clientConfig;
AsyncTunnelClient.appInfo = appInfo;
interfaceServerAddress{
    host:string;// 服务器地址
    port:number;// 服务器端口
}
interfaceClientEncryptionConfig{
    forbiddenPrivateEncryption?:boolean;// false
    option?:number// 加密方式 = 0
    ca?:string// ca证书地址 = ""
}
interfaceClientConfigextendsServerAddress{
    alternativeServerAddress?: ServerAddress[];// 备用服务器
    clientId:string;
    public PemBase64:string;
    clientSecret:string;
    logDir:string;
    socks5ProxyAuth?:boolean;// socks代理认证 = false
    httpProxy?:boolean;// http代理 = true
    httpProxyAuth?:boolean;// http代理认证 = false
    encryption?: ClientEncryptionConfig;//
    portKnock?:boolean;// 端口敲门 = true
    initTimeOut?:number;// 初始化超时时间 = 1000
}
// 设备相关信息
export interfaceAppInfo{
    uuid:string// 设备唯一标识
    os?:string// 操作系统
    osVersion?:string// 操作系统版本
    platform?:string// 平台
    kernelArch?:string// 内核架构
    kernelVersion?:string// 内核版本
    hostname?:string;
}
```

### **初始化隧道网络** 

1. 成功后返回代理信息 

2. 该方法支持重复调用,内部会处理状态 

```
import{ AsyncTunnelClient }from"mintunnelsdp";
// 隧道网络初始化状态监听
AsyncTunnelClient.getInstance().networkStatus.addEventListener(networkStatus =>
{});
// 隧道代理信息监听
AsyncTunnelClient.getInstance().proxyConfig.addEventListener(proxyConfig =>{});
const proxyConfigResult =await AsyncTunnelClient.getInstance().initNetwork();
// 代理信息
interfaceProxyConfig{
    sock5Port:number;
    socks5Password:string;
    socks5UserName:string;
    httpPort:number;
    httpPassword:string;
}
```

### **提前获取代理信息** 

1. 可在初始化隧道网络前调用该方法,但此时代理并不生效 

2. 如没有调用过该方法,初始化隧道网络时,会自动初始化代理 

3. 该方法支持重复调用,内部会处理状态 

```
import{ AsyncTunnelClient }from"mintunnelsdp";
const proxyConfig = AsyncTunnelClient.getInstance().initProxySync();
```

### **登录** 

1. 可在初始化隧道网络前调用该方法,方法内部会自动初始化隧道网络 

2. 该方法可重复调用,已最后一次调用时的用户名为准 

```
import{ AsyncTunnelClient }from"mintunnelsdp";
// 隧道登录状态监听
AsyncTunnelClient.getInstance().authStatus.addEventListener(authStatus =>{});
const result =await AsyncTunnelClient.getInstance().login("loginName",
"password");
```

**登出** 

#### 1. 该方法可重复调用,仅在登录后调用时有效 

```
import{ AsyncTunnelClient }from"mintunnelsdp";
AsyncTunnelClient.getInstance().logout()
```

## **代理设置参考** 

### **http代理(官方)** 

```
import{ connection }from'@kit.NetworkKit';
connection.setAppHttpProxy({
  host:'127.0.0.1',
  port: proxyInfo.httpPort,
  exclusionList:[]
})
```

## **socket代理(官方)** 

```
import{ socket }from'@kit.NetworkKit';
import{ BusinessError }from'@kit.BasicServicesKit';
let tcp: socket.TCPSocket = socket.constructTCPSocketInstance();
let netAddress: socket.NetAddress ={
  address:'192.168.xx.xxx',
  port:8080
}
let socks5Server: socket.NetAddress ={
  address:'127.0.0.1',
  port: proxyInfo.sock5Port
}
let proxyOptions: socket.ProxyOptions ={
  type :1,
  address: socks5Server,
  username: proxyInfo.socks5UserName,
  password: proxyInfo.socks5Password
}
let tcpconnectoptions: socket.TCPConnectOptions ={
  address: netAddress,
  timeout:6000,
  proxy: proxyOptions,
}
tcp.connect(tcpconnectoptions,(err: BusinessError)=>{
if(err){
console.error('connect fail');
return;
}
console.log('connect success');
})
```
