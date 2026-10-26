# **娜迦科技白盒秘钥SDK HarmonyOS 使用文档** 

娜迦科技白盒秘钥SDK 是基于白盒密钥保护的随机密文加密算法。 

## **1. SDK集成** 

#### 1). 将 wbklib.har 放入工程的libs目录下。 

2). 在工程目录下执行 ohpm install libs/wbklib.har 

## **2. SDK 使用例子** 

//引用har中的类 import { C } from 'wbklib' 

//白盒密钥,是通过平台生成的密钥。 

let boxkey = "YThhZmRkZWFmNmY3YWJkMmYxZWRkM2Y4ZDdjYmMzZjhjZGNhYThhZmNkZGFjOG //加密密钥向量, 需要传Uint8Array 

let iv = "SBlgNVac5OZajGS3"; 

let iv_cbc_Uint8Array = new util.TextEncoder().encodeInto(iv); // for cbc mo let iv_ecb_Uint8Array = new Uint8Array(0); // for ecb mode //明文 

let text = "Hello World"; 

//SM4加密算法加密 

let encode = C.s1(text, boxkey, iv_cbc_Uint8Array); 

hilog.info(0x0000, 'Cipher_test', 'encode text -> %{public}s', encode); 

##### //SM4解密算法解密 

```arkts
let decode = C.s2(encode, boxkey, iv_cbc_Uint8Array); hilog.info(0x0000, 'Cipher_test', 'decode text -> %{public}s', decode); 
```

## **3. SDK API 说明** 

|**变量**|**说明**|**备注**|
|---|---|---|
|data|明文||
|cihperStr|密文||
|cihperArray|密文||
|key|密钥||
|iv|加密向量||

### **3.1 AES 算法接口** 

##### // 加密字符串接口 

static a1(data: string, key: string, iv: Uint8Array): string; 

##### // 解密字符串接口 

static a2(cihperStr: string, key: string, iv: Uint8Array): string; 

##### // 加密字节接口 

static a3(data: Uint8Array, key: string, iv: Uint8Array): Uint8Array; // 解密字节接口 static a4(cihperArray: Uint8Array, key: string, iv: Uint8Array): Uint8Array; 

### **3.2 DES 算法接口** 

##### // 加密字符串接口 

static d1(data: string, key: string, iv: Uint8Array): string; 

##### // 解密字符串接口 

static d2(cihperStr: string, key: string, iv: Uint8Array): string; 

##### // 加密字节接口 

static d3(data: Uint8Array, key: string, iv: Uint8Array): Uint8Array; // 解密字节接口 static d4(cihperArray: Uint8Array, key: string, iv: Uint8Array): Uint8Array; 

### **3.3 3DES 算法接口** 

##### // 加密字符串接口 

static t1(data: string, key: string, iv: Uint8Array): string; 

##### // 解密字符串接口 

static t2(cihperStr: string, key: string, iv: Uint8Array): string; // 加密字节接口 static t3(data: Uint8Array, key: string, iv: Uint8Array): Uint8Array; // 解密字节接口 static t4(cihperArray: Uint8Array, key: string, iv: Uint8Array): Uint8Array; 

### **3.4 SM4 算法接口** 

##### // 加密字符串接口 

static s1(str: string, key: string, iv: Uint8Array): string; 

##### // 解密字符串接口 

static s2(str: string, key: string, iv: Uint8Array): string; 

##### // 加密字节接口 

static s3(data: Uint8Array, key: string, iv: Uint8Array): Uint8Array; // 解密字节接口 static s4(data: Uint8Array, key: string, iv: Uint8Array): Uint8Array;
