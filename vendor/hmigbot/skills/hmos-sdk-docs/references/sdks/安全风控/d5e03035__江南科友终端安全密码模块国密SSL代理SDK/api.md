# **终端安全密码模块** **_接口文档 HarmonyOS Next SDK_** 

#### 广州江南科友科技股份有限公司 

Version 1.1.3, 2024-07-11 

## **目录** 

|1.对象接口. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2|
|---|
|1.1. SM2实例化. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2|
|1.2. SM2加密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2|
|1.3. SM2解密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3|
|1.4. SM2签名. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4|
|1.5. SM2验签. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5|
|1.6. SM2获取公钥值. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5|
|1.7. SM2获取私钥值. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6|
|1.8. SM3实例化. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
|1.9. SM3计算带SM2公钥和userID的HMAC值. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
|1.10. SM3计算数据摘要值. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8|
|1.11. SM3计算HMAC . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8|
|1.12. SM4实例化. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9|
|1.13. SM4 CBC加密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10|
|1.14. SM4 CBC解密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10|
|1.15. SM4 ECB加密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11|
|1.16. SM4 ECB解密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12|
|1.17. SM4获取密钥值. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13|
|2.静态接口. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14|
|2.1. SM2加密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14|
|2.2. SM2解密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14|
|2.3. SM2签名. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15|
|2.4. SM2验签. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16|
|2.5. SM4 ECB加密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17|
|2.6. SM4 ECB解密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19|
|2.7. SM4 CBC加密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20|
|2.8. SM4 CBC解密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21|
|2.9.计算数据摘要值. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22|
|2.10.计算HMAC. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23|
|2.11.验证HMAC. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24|
|2.12. SM3计算数据摘要值. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25|
|2.13. SM3计算HMAC . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26|
|2.14. SM3验证HMAC . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26|

|2.15.数字信封ECB加密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27|
|---|
|2.16.数字信封ECB解密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29|
|2.17.数字信封 计算HMAC. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31|
|2.18.数字信封 验证HMAC. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33|
|2.19.密钥管理. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34|
|2.20.密钥创建. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35|
|2.21.密钥生成. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37|
|2.22.密钥销毁. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38|
|2.23.密钥重置. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 40|
|2.24.密钥导入. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41|
|2.25.密钥导出. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 43|
|2.26. 16进制的字符串转 _Array_ 数组. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 44|
|2.27._Array_ 数组转16进制的字符串. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45|
|2.28. UTF-8进制的字符串转 _Array_ 数组. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45|
|2.29._Array_ 数组转UTF-8进制的字符串. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 46|
|2.30. BASE64字符串转 _Array_ 数组. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 47|
|2.31._Array_ 数组转BASE64字符串. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 47|
|2.32.版本信息. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 48|

Preface 

#### 终端安全密码模块 HarmonyOS Next SDK 适用于 HarmonyOS Next 环境 下的数据保护。 

##### **版权声明** 

本文档由广州江南科友科技股份有限公司(以下简称 **江南科友** )编写,江南科友保留对本文 档的所有权和解释权,任何公司和个人未经允许,不得擅自使用、复制、修改、传播本书的 内容。 

江南科友保留有对本文档进行重新修订的权利,随时可能对本文档中出现的错误、与最新资 料不符之处等做必要的修改,这些不再另行通知,但会全部编入新版文档中。 

本文档适用于江南科友的终端安全密码模块 HarmonyOS Next SDK。 

第 1 页 

1. 对象接口 

## 1. **对象接口** 

### 1.1. SM2 **实例化** 

###### 接口定义 

```
SSM.SM2(public kKey, private Key)
```

初始化一个 SM2 对象,用于加解密和签名验签,公钥私钥都不传入时自动生成密钥对 

|**输入参数**|||
|---|---|---|
|publickKey|Number[]|公钥数据|
|privateKey **输出参数**|Number[]|私钥数据|
|SM2 required|SM2|SM2实例对象|

##### **示例代码** 

```
const public Key =
SSM.util.Hex.parse('D6734C334912363913E37BCC9C11EC841C0A866BBD9E391F416007634E
F12B4BCC35843FFF47536E479640986876EE957549FF344F2F8C3805FD3030DEFF1393');
const private Key =
SSM.util.Hex.parse('C330D76BA6C77DCAEDDB7D42A34489EB299755C4057BEB3AF7D36512D9
47CFAB');
const SM2 = new SSM.SM2(public Key, private Key);
```

### 1.2. SM2 **加密** 

接口定义 

```
SM2.encrypt(plaintext)
SM2.encryptWithC1C2C3(plaintext)
```

第 2 页 

1. 对象接口 

使用一个初始化好的 SM2 对象加密明文数据,SM2 对象中必须包含可用的公钥值。 

##### **输入参数** 

|plaintext required|Number[]|明文数据内容|
|---|---|---|
|**输出参数**|||
|ciphertext required|Number[]|密文数据,默认是 C1C3C2 格式的数据,使用 `encryptWithC1C2C3` 生成C1C2C3格式的密文数 据|

##### **示例代码** 

```
const SM2 = new SSM.SM2();
const plaintext = SSM.util.UTF8.parse("test data");
const ciphertext = SM2.encrypt(plaintext);
```

### 1.3. SM2 **解密** 

接口定义 

```
SM2.decrypt(ciphertext)
SM2.decryptWithC1C2C3(ciphertext)
```

使用一个初始化好的 SM2 对象解密密文数据,SM2 对象中必须包含可用的私钥值。 

##### **输入参数** 

|ciphertext required|Number[]|密文数据内容|
|---|---|---|
|**输出参数**|||
|plaintext required|Number[]|明文数据,默认解密C1C3C2格式的数据,使用 `decryptWithC1C2C3` 解密C1C2C3格式的密文数 据|

第 3 页 

1. 对象接口 

##### **示例代码** 

```
const SM2 = new SSM.SM2();
const ciphertext =
SSM.util.Hex.parse('6C3FA8B8DEA90747D05022532D9C64D0F0A37B400D667064E8CE1023DE
A776B244EE8197EF4E1101A1DE206690EC6644207F634C53B115BA8FCC8A026ABD4D75CD35621A
1323CFE1647798573F0A5E381FDDC2622CEE83B2DF4445C039BFE20EB182F7');
const plaintext = SM2.encrypt(ciphertext);
```

### 1.4. SM2 **签名** 

###### 接口定义 

```
SM2.sign(plaintext, userId)
SM2.signWithDer(plaintext, userId)
```

使用一个初始化好的 SM2 对象生成签名数据,SM2 对象中必须包含可用的私钥值。 

##### **输入参数** 

|plaintext required|Number[]|用于签名的数据|
|---|---|---|
|userId|Number[]|用户标识,不传入则使用默认的用户标识|
|**输出参数**|||
|signature required|Number[]|签名值,默认生成 R+S 格式的签名数据,使用 `signWithDer` 生成Der格式的签名数据|

##### **示例代码** 

```
const SM2 = new SSM.SM2();
const plaintext = SSM.util.UTF8.parse('test data');
const userId = SSM.util.UTF8.parse('test userId');
const signature = SM2.sign(plaintext, userId);
```

第 4 页 

1. 对象接口 

### 1.5. SM2 **验签** 

###### 接口定义 

```
SM2.verify(signature, plaintext, userId)
SM2.verifyWithDer(signature, plaintext, userId)
```

使用一个初始化好的 SM2 对象验证签名数据,SM2 对象中必须包含可用的公钥值。 

##### **输入参数** 

|signature required|Number[]|签名数据|
|---|---|---|
|plaintext required|Number[]|用于签名的数据|
|userId|Number[]|用户标识,不传入则使用默认的用户标识|
|**输出参数**|||
|result required|Boolean|验签结果,默认验证R+S格式的签名数据,使用 `verifyWithDer` 验证Der格式的签名数据|

##### **示例代码** 

```
const SM2 = new SSM.SM2();
const signature =
SSM.util.Hex.parse('FA015B5B404B34257D91BDB537B4C2AF87434E60A0A4E639622996AF86
4CBABEE8C0EF7168CC19E02F6B06A36C0EAF0B60950DDD1630F4095923A082FA9D7412');
const plaintext = SSM.util.UTF8.parse('test data');
const userId = SSM.util.UTF8.parse('test userId');
const result = SM2.verify(signature, plaintext, userId);
```

### 1.6. SM2 **获取公钥值** 

###### 接口定义 

```
SM2.getPublicKeyValue()
```

第 5 页 

1. 对象接口 

使用一个初始化好的 SM2 对象,获取当前的SM2对象的公钥值 

##### **输入参数** 

无参数值 **输出参数** publicKeyrequired Number[] |Null 公钥数据,不存在时返回 Null **示例代码** `const SM2 = new SSM.SM2(); const publicKey = SM2.getPublicKeyValue();` 

### 1.7. SM2 **获取私钥值** 

接口定义 

```
SM2.getPrivateKeyValue()
```

使用一个初始化好的 SM2 对象,获取当前的SM2对象的私钥值 

##### **输入参数** 

无参数值 **输出参数** privateKeyrequired Number[] |Null 公钥数据,不存在时返回 Null 

##### **示例代码** 

```
const SM2 = new SSM.SM2();
const public Key = SM2.private Key();
```

第 6 页 

1. 对象接口 

### 1.8. SM3 **实例化** 

###### 接口定义 

```
SSM.SM3()
```

初始化一个 SM3 对象,用于计算数据摘要值 

##### **输入参数** 

无参数值 **输出参数** SM3required SM3 SM3实例对象 

##### **示例代码** 

```
const SM3 = new SSM.SM3();
```

### 1.9. SM3 **计算带** SM2 **公钥和** userID **的** HMAC **值** 

###### 接口定义 

```
SM3.hmacWithPublicKey(plaintext, userID, public Key)
```

使用一个 SM3 实例对象计算带 SM2 公钥和 userID 的 HMAC 值。 

##### **输入参数** 

|plaintext required|Number[]|明文数据内容|
|---|---|---|
|userID required|Number[]|用户标识|
|publicKey required|Number[]|SM2公钥值|
|**输出参数**|||

第 7 页 

1. 对象接口 

digestDatarequired Number[] 数据摘要值 

##### **示例代码** 

```
const SM3 = new SSM.SM3();
const plaintext = SSM.util.UTF8.parse("test data");
const userID = SSM.util.UTF8.parse("test userId");
const public Key =
SSM.util.Hex.parse('35D7C27AA3369D4B2EA91589B1DE603100CA73895688D9CCCA9D6EEAC3
0DCD3094A35C85C7984147DBF418CE79943ECAE0B7B54F5CA7E75C263294BB625E786E');
const digestData = SM3.hmacWithPublicKey(plaintext, userID, public Key);
```

### 1.10. SM3 **计算数据摘要值** 

接口定义
SM3.digest(plaintext)
使用一个 SM3 实例对象计算数据摘要值。
输入参数
plaintextrequired Number[] 明文数据内容
输出参数
digestDatarequired Number[] 数据摘要值
示例代码
const SM3 = new SSM.SM3();
const plaintext = SSM.util.UTF8.parse("test data");
const digestData = SM3.digest(plaintext);

### 1.11. SM3 **计算** HMAC 

第 8 页 

1. 对象接口 

接口定义 

```
SM3.hmac(keyValue, plaintext)
```

使用一个 SM3 实例对象计算 HMAC。 

##### **输入参数** 

|keyValue required|Number[]|密钥值|
|---|---|---|
|plaintext required|Number[]|明文数据内容|
|**输出参数**|||
|digestData required|Number[]|数据摘要值|

##### **示例代码** 

```
const SM3 = new SSM.SM3();
const keyValue = SSM.util.Hex.parse('78521CBB454C57C628872C2C421DE5CC');
const plaintext = SSM.util.UTF8.parse("test data");
const digestData = SM3.hmac(keyValue, plaintext);
```

### 1.12. SM4 **实例化** 

###### 接口定义 

```
SSM.SM4(keyValue)
```

初始化一个 SM4 对象,用于加解密,密钥不传入时自动生成密钥。 

##### **输入参数** 

|keyValue|Number[]|密钥数据,密钥数组长度必须为16位|
|---|---|---|
|**输出参数** SM4 required|SM4|SM4实例对象|

第 9 页 

1. 对象接口 

##### **示例代码** 

```
const keyValue = SSM.util.Hex.parse('FF72F6E7F616121FCC880D280FA5A067');
const SM4 = new SSM.SM4(keyValue);
```

### 1.13. SM4 CBC **加密** 

###### 接口定义 

```
SM4.encryptCBC(plaintext, iv, padding)
```

使用一个初始化好的 SM4 对象CBC算法模式加密明文数据。 

|**输入参数**|||
|---|---|---|
|plaintext required|Number[]|明文数据内容|
|iv required|Number[]|初始向量,长度为16字节|
|padding required|'NoPadding' |
'PKCS5' | 'PKCS7'
| '0x80'|填充类型|
|**输出参数**|||
|ciphertext required|Number[]|密文数据|
|**示例代码**|||
|`const SM4 = new` `const plaintext` `const iv = SSM.u` `const ciphertext`|`SSM.SM4();` `= SSM.util.UTF8.pa` `til.Hex.parse('370` `= SM4.encryptCBC(`|`rse("test data");` `880788260BE0ABDB274B78863F45A');` `plaintext, iv, 'PKCS5');`|

### 1.14. SM4 CBC **解密** 

第 10 页 

1. 对象接口 

接口定义 

```
SM4.decryptCBC(ciphertext, iv, padding)
```

##### 使用一个初始化好的 SM4 对象CBC算法模式解密密文数据。 

##### **输入参数** 

|ciphertext required|Number[]|密文数据内容|
|---|---|---|
|iv required|Number[]|初始向量,长度为16字节|
|padding required|'NoPadding' |
'PKCS5' | 'PKCS7'
| '0x80'|填充类型|
|**输出参数**|||
|plaintext required|Number[]|明文数据|
|**示例代码**|||

```
const SM4 = new SSM.SM4();
const ciphertext = SSM.util.Hex.parse('0F27C383623494438428E0EDB92A4C29');
const iv = SSM.util.Hex.parse('370880788260BE0ABDB274B78863F45A');
const plaintext = SM4.decryptCBC(ciphertext, iv, 'PKCS5');
```

### 1.15. SM4 ECB **加密** 

###### 接口定义 

```
SM4.encryptECB(plaintext, padding)
```

使用一个初始化好的 SM4 对象ECB算法模式加密明文数据。 

##### **输入参数** 

plaintextrequired Number[] 明文数据内容 

第 11 页 

1. 对象接口 paddingrequired 'NoPadding' | 填充类型 'PKCS5' | 'PKCS7' | '0x80' **输出参数** ciphertextrequired Number[] 密文数据 

##### **示例代码** 

```
const SM4 = new SSM.SM4();
const plaintext = SSM.util.UTF8.parse("test data");
const ciphertext = SM4.encryptECB(plaintext, 'PKCS5');
```

### 1.16. SM4 ECB **解密** 

###### 接口定义 

```
SM4.decryptECB(ciphertext, padding)
```

使用一个初始化好的 SM4 对象ECB算法模式解密密文数据。 

##### **输入参数** 

ciphertextrequired Number[] 密文数据内容 paddingrequired 'NoPadding' | 填充类型 'PKCS5' | 'PKCS7' | '0x80' **输出参数** plaintextrequired Number[] 明文数据 **示例代码** 

```
const SM4 = new SSM.SM4();
const ciphertext = SSM.util.Hex.parse('0F27C383623494438428E0EDB92A4C29');
const plaintext = SM4.decryptECB(ciphertext, 'PKCS5');
```

第 12 页 

1. 对象接口 

### 1.17. SM4 **获取密钥值** 

|接口定义 `SM2.getValue()`|
|---|
|使用一个初始化好的SM4对象,获取当前的SM4对象的密钥值|
|**输入参数**|
|无参数值|
|**输出参数**|
|keyValue required Number[] 密钥数据|
|**示例代码**|
|`const SM4 = new SSM.SM4();` `const keyValue = SM4.getValue();`|

第 13 页 

2. 静态接口 

## 2. **静态接口** 

### 2.1. SM2 **加密** 

###### 接口定义 

```
Asymmetric.encryptWithSM2(key, plaintext, mode)
```

SM2算法加密 

##### **输入参数** 

|key required|AsymmetricKey|SM2非对称密钥实例|
|---|---|---|
|plaintext required|Number[]|明文数据内容,数据长度建议不超过2M大小|
|mode|"C1C3C2" |
"C1C2C3"|密文格式,默认"C1C3C2"|
|**输出参数** ciphertext required|Promise<Number []>|密文数据,根据参数mode生成相应格式的密文数 据|

##### **示例代码** 

```
const AsymmetricKey = SSM.AsymmetricKey
const Asymmetric = SSM.Asymmetric
const util = SSM.util
const key = new AsymmetricKey(Asymmetric.SM2,
util.Hex.parse('437DAF98EC0B0C7DC67229A3A714636013ECF60F54810C9C2F51192D37E358
606BCA4A593C782799F30021ED49F1E04DC588878B4FA17D3CA753C86AE1C38173'))
const plaintext = util.UTF8.parse("test data");
const ciphertext = await Asymmetric.encryptWithSM2(key, plaintext,
Asymmetric.C1C3C2);
```

### 2.2. SM2 **解密** 

第 14 页 

2. 静态接口 

###### 接口定义 

```
Asymmetric.decryptWithSM2(key, ciphertext, mode)
```

##### SM2算法解密 

|**输入参数**|||
|---|---|---|
|key required|AsymmetricKey|SM2非对称密钥实例,需要包含SM2私钥|
|ciphertext required|Number[]|密文数据内容|
|mode|"C1C3C2" |
"C1C2C3"|密文格式,默认"C1C3C2"|
|**输出参数**|||
|plaintext required|Promise<Number []>|明文数据|
|**示例代码**|||

```
const AsymmetricKey = SSM.AsymmetricKey
const Asymmetric = SSM.Asymmetric
const util = SSM.util
const key = new AsymmetricKey(Asymmetric.SM2, {
  PrivateKey:
util.Hex.parse('4E2A0B5E2FA55018B9009B091780B8FFF1B36F3D625FC81F62C838D92EABB8
BE')
})
const ciphertext =
util.Hex.parse("FB6E8BCE1CD7C47AD34CD018C68F1D8B6CA4353398C79D1BBDFDA5E4B9D6AB
C062CF4C7F330E526D41355AEB587ADBF22797A0E6532E61077450644B2CAA7C598FA9DACF14CA
ECFDBDE2FFEDA262BCD1DBECBB4BD542788DD51D1CED8CEB1E86C5B52D");
const plaintext = await Asymmetric.decryptWithSM2(key, ciphertext,
Asymmetric.C1C3C2);
```

### 2.3. SM2 **签名** 

第 15 页 

2. 静态接口 

接口定义 

```
SM2.signWithSM2(key, plaintext, userId)
```

##### SM2 签名,签名格式为 R+S。 

##### **输入参数** 

|key required|AsymmetricKey|SM2非对称密钥实例,需包含SM2私钥|
|---|---|---|
|plaintext required|Number[]|用于签名的数据,数据长度建议不超过2M大小|
|userId required|Number[]|用户标识|
|**输出参数**|||
|signature required|Promise<Number []>|签名值|

##### **示例代码** 

```
const AsymmetricKey = SSM.AsymmetricKey
const Asymmetric = SSM.Asymmetric
const util = SSM.util
const key = new AsymmetricKey(Asymmetric.SM2, {
  PrivateKey:
util.Hex.parse('4E2A0B5E2FA55018B9009B091780B8FFF1B36F3D625FC81F62C838D92EABB8
BE')
```

##### `})` 

```
const plaintext = util.Hex.parse("test data");
const userId = util.UTF8.parse('test userId');
const signature = await Asymmetric.signWithSM2(key, plaintext, userId);
```

### 2.4. SM2 **验签** 

###### 接口定义 

```
SM2.verifyWithSM2(key, plaintext, userId, signature)
```

第 16 页 

2. 静态接口 

SM2 验签,签名格式为 R+S 

##### **输入参数** 

|key required|AsymmetricKey|SM2非对称密钥实例|
|---|---|---|
|plaintext required|Number[]|用于签名的数据|
|userId required|Number[]|用户标识|
|signature required|Number[]|签名数据|
|**输出参数** result required|Promise<Boolean >|验签结果|

##### **示例代码** 

```
const AsymmetricKey = SSM.AsymmetricKey
const Asymmetric = SSM.Asymmetric
const util = SSM.util
const key = new AsymmetricKey(Asymmetric.SM2, {
  PublicKey:
util.Hex.parse('437DAF98EC0B0C7DC67229A3A714636013ECF60F54810C9C2F51192D37E358
606BCA4A593C782799F30021ED49F1E04DC588878B4FA17D3CA753C86AE1C38173')
```

##### `})` 

```
const plaintext = util.UTF8.parse('test data');
const userId = util.UTF8.parse('test userId');
const signature =
util.Hex.parse('3044022020F92E52739651B5BE35722A20B07BD873B975B1CA5ACEBCD3AD9A
21EE73CDD002200826D8D7FE0801E1B995DC54614F1A2544E4E4AC416CA2F0182D8B14458DD1B5
');
const result = await Asymmetric.verifyWithSM2(key, plaintext, userId,
signature);
```

### 2.5. SM4 ECB **加密** 

第 17 页 

2. 静态接口 

###### 接口定义 

```
Symmetric.encryptWithECB(key, padding, plaintext)
```

##### SM4 ECB算法模式加密明文数据。 

|**输入参数** key required|SymmetricKey|SM4对称密钥实例|
|---|---|---|
|padding required|"NoPadding" |
"ZeroPadding"
|
"PKCS7Padding" |
"ISO10126Paddin
g"
|
"ISO_ICE_7816d4P
adding"
|
"Ansix923Padding
"|填充类型|
|plaintext required|Number[]|明文数据内容,数据长度建议不超过2M大小|
|**输出参数**|||
|ciphertext required|Promise<Number []>|密文数据|
|**示例代码**|||
|`const Symmetric` `const SymmetricK` `const util = SSM` `const key = new` `Key: util.Hex.` `})` `const plaintext` `const ciphertext` `plaintext);`|`= SSM.Symmetric` `ey = SSM.Symmetric` `.util` `SymmetricKey(Symme` `parse('B7C089072F5` `= util.UTF8.parse(` `= await Symmetric`|`Key` `tric.SM4, {` `26EF9CF69BAB3DDE34E70')` `"test data");` `.encryptWithECB(key, Symmetric.ZeroPadding,`|

第 18 页 

2. 静态接口 

### 2.6. SM4 ECB **解密** 

###### 接口定义 

```
Symmetric.decryptWithECB(key, padding, ciphertext)
```

##### SM4 ECB算法模式解密密文数据。 

|**输入参数** key required|SymmetricKey SM4对称密钥实例|
|---|---|
|padding required|"NoPadding" |
"ZeroPadding"
|
"PKCS7Padding" |
"ISO10126Paddin
g"
|
"ISO_ICE_7816d4P
adding"
|
"Ansix923Padding
"
填充类型|
|ciphertext required|Number[] 密文数据内容|
|**输出参数**||
|plaintext required|Promise<Number []> 明文数据|
|**示例代码**||
|`const Symmetric` `const SymmetricK` `const util = SSM` `const key = new` `Key: util.Hex.` `})` `const ciphertext` `const plaintext` `ciphertext);`|`= SSM.Symmetric` `ey = SSM.SymmetricKey` `.util` `SymmetricKey(Symmetric.SM4, {` `parse('B7C089072F526EF9CF69BAB3DDE34E70')` `= util.Hex.parse('0F27C383623494438428E0EDB92A4C29');` `= await Symmetric.decryptWithECB(key, Symmetric.ZeroPadding,`|

第 19 页 

2. 静态接口 

### 2.7. SM4 CBC **加密** 

###### 接口定义 

```
Symmetric.encryptWithCBC(key, padding, plaintext, iv)
```

##### SM4 CBC算法模式加密明文数据。 

##### **输入参数** 

|key required|SymmetricKey|SM4对称密钥实例|
|---|---|---|
|padding required|"NoPadding" |
"ZeroPadding"
|
"PKCS7Padding" |
"ISO10126Paddin
g"
|
"ISO_ICE_7816d4P
adding"
|
"Ansix923Padding
"|填充类型|
|plaintext required|Number[]|明文数据内容,数据长度建议不超过2M大小|
|iv required|Number[]|初始向量,长度为16字节|
|**输出参数**|||
|ciphertext required|Promise<Number []>|密文数据|

第 20 页 

2. 静态接口 

##### **示例代码** 

```
const Symmetric = SSM.Symmetric
const SymmetricKey = SSM.SymmetricKey
const util = SSM.util
const key = new SymmetricKey(Symmetric.SM4, {
  Key: util.Hex.parse('B7C089072F526EF9CF69BAB3DDE34E70')
})
const plaintext = util.UTF8.parse("test data");
const iv = util.Hex.parse('00000000000000000000000000000000')
const ciphertext = await Symmetric.encryptWithCBC(key, Symmetric.ZeroPadding,
plaintext, iv);
```

### 2.8. SM4 CBC **解密** 

###### 接口定义 

```
Symmetric.decryptWithCBC(key, padding, ciphertext, iv)
```

##### SM4 CBC算法模式解密密文数据。 

##### **输入参数** 

|key required|SymmetricKey|SM4对称密钥实例|
|---|---|---|
|padding required|"NoPadding" |
"ZeroPadding"
|
"PKCS7Padding" |
"ISO10126Paddin
g"
|
"ISO_ICE_7816d4P
adding"
|
"Ansix923Padding
"|填充类型|
|ciphertext required|Number[]|密文数据内容|
|iv required|Number[]|初始向量,长度为16字节|

第 21 页 

2. 静态接口 

##### **输出参数** 

plaintextrequired Promise<Number 明文数据 []> 

##### **示例代码** 

```
const Symmetric = SSM.Symmetric
const SymmetricKey = SSM.SymmetricKey
const util = SSM.util
const key = new SymmetricKey(Symmetric.SM4, {
  Key: util.Hex.parse('B7C089072F526EF9CF69BAB3DDE34E70')
})
const ciphertext = util.Hex.parse('0F27C383623494438428E0EDB92A4C29');
const iv = util.Hex.parse('00000000000000000000000000000000')
const plaintext = await Symmetric.decryptWithCBC(key, Symmetric.ZeroPadding,
ciphertext, iv);
```

### 2.9. **计算数据摘要值** 

###### 接口定义 

```
Hash.digest(algorithm, plaintext)
```

计算数据摘要值。 

##### **输入参数** 

|algorithm required|'SM3'|算法类型|
|---|---|---|
|plaintext required|Number[]|明文数据内容,数据长度建议不超过5M大小|
|**输出参数**|||
|digestData required|Promise<Number []>|数据摘要值|

第 22 页 

2. 静态接口 

##### **示例代码** 

```
const Hash = SSM.Hash
const plaintext = util.UTF8.parse("test data");
const digestData = await Hash.digest(Hash.SM3, plaintext);
```

### 2.10. **计算** HMAC 

###### 接口定义 

```
Hash.hmac(algorithm, plaintext, key, padding)
```

##### 计算 HMAC。 

##### **输入参数** 

|algorithm required|'SM3'|算法类型|
|---|---|---|
|plaintext required|Number[]|明文数据内容,数据长度建议不超过5M大小|
|key required|SecretData|SecretData密钥实例|
|padding required|"NoPadding" |
"ZeroPadding"
|
"PKCS7Padding"|填充方式|
|**输出参数**|||
|digestData required|Promise<Number []>|数据摘要值|

第 23 页 

2. 静态接口 

##### **示例代码** 

```
const Hash = SSM.Hash
const SecretData = SSM.SecretData
const util = SSM.util
const key = new
SecretData(util.Hex.parse('37C48170F3E0ECA188A3A525078C497D'));
const plaintext = util.UTF8.parse("test data");
const digestData = await Hash.hmac(Hash.SM3, plaintext, key, 'NoPadding');
```

### 2.11. **验证** HMAC 

###### 接口定义 

```
Hash.hmacVerify(algorithm, plaintext, key, padding, mac)
```

##### 验证 HMAC 

##### **输入参数** 

|algorithm required|'SM3'|算法类型|
|---|---|---|
|plaintext required|Number[]|明文数据内容|
|key required|SecretData|SecretData密钥实例|
|padding required|"NoPadding" |
"ZeroPadding"
|
"PKCS7Padding"|填充方式|
|mac required|Number[]|数据摘要值|
|**输出参数**|||
|result required|Promise<Boolean >|验证结果|

第 24 页 

2. 静态接口 

##### **示例代码** 

```
const Hash = SSM.Hash
const SecretData = SSM.SecretData
const util = SSM.util
const key = new
SecretData(util.Hex.parse('37C48170F3E0ECA188A3A525078C497D'));
const plaintext = util.UTF8.parse("test data");
const mac =
util.Hex.parse('C12139F7C56AFE09A1001AB8F3D3CD341B8F0CFC53EE85222DC5154A4C4BDF
01');
const result = await Hash.hmacVerify(Hash.SM3, plaintext, key, 'NoPadding',
mac);
```

### 2.12. SM3 **计算数据摘要值** 

###### 接口定义 

```
Hash.sm3(plaintext)
```

SM3 计算数据摘要值。 **输入参数** required plaintext Number[] 明文数据内容,数据长度建议不超过5M大小 **输出参数** digestDatarequired Promise<Number 数据摘要值 []> **示例代码** `const Hash = SSM.Hash const plaintext = util.UTF8.parse("test data"); const digestData = await Hash.sm3(plaintext);` 

第 25 页 

2. 静态接口 

### 2.13. SM3 **计算** HMAC 

###### 接口定义 

```
Hash.sm3hmac(plaintext, key, padding)
```

SM3 计算 HMAC。 

##### **输入参数** 

|plaintext required|Number[]|明文数据内容,数据长度建议不超过5M大小|
|---|---|---|
|key required|SecretData|SecretData密钥实例|
|padding required|"NoPadding" |
"ZeroPadding"
|
"PKCS7Padding"|填充方式|
|**输出参数**|||
|digestData required|Promise<Number []>|数据摘要值|

##### **示例代码** 

```
const Hash = SSM.Hash
const SecretData = SSM.SecretData
const util = SSM.util
const key = new
SecretData(util.Hex.parse('37C48170F3E0ECA188A3A525078C497D'));
const plaintext = util.UTF8.parse("test data");
const digestData = await Hash.sm3hmac(plaintext, key, 'NoPadding');
```

### 2.14. SM3 **验证** HMAC 

###### 接口定义 

```
Hash.sm3hmacVerify(plaintext, key, padding, mac)
```

第 26 页 

2. 静态接口 

SM3 验证 HMAC。 

##### **输入参数** 

|plaintext required|Number[]|明文数据内容|
|---|---|---|
|key required|SecretData|SecretData密钥实例|
|padding required|"NoPadding" |
"ZeroPadding"
|
"PKCS7Padding"|填充方式|
|mac required|Number[]|数据摘要值|
|**输出参数**|||
|result required|Promise<Boolean >|验证结果|

##### **示例代码** 

```
const { Hash, SecretData } = SSM;
const Hash = SSM.Hash
const SecretData = SSM.SecretData
const util = SSM.util
const key = new
SecretData(util.Hex.parse('37C48170F3E0ECA188A3A525078C497D'));
const plaintext = util.UTF8.parse("test data");
const mac =
util.Hex.parse('C12139F7C56AFE09A1001AB8F3D3CD341B8F0CFC53EE85222DC5154A4C4BDF
01');
const result = await Hash.sm3hmacVerify(plaintext, key, 'NoPadding', mac);
```

### 2.15. **数字信封** ECB **加密** 

###### 接口定义 

```
Envelope.ecbEnvelopeEncrypt(key, algorithm, bits, padding, plaintext, mode)
```

第 27 页 

2. 静态接口 

##### SM4 ECB算法模式加密明文数据。 

|**输入参数** key required|AsymmetricKey|SM2对称密钥实例|
|---|---|---|
|algorithm required|'SM4'|指定具体的对称算法|
|bits required|Number|指定密钥的长度|
|padding required|"NoPadding" |
"ZeroPadding"
|
"PKCS7Padding" |
"ISO10126Paddin
g"
|
"ISO_ICE_7816d4P
adding"
|
"Ansix923Padding
"|填充类型|
|plaintext required|Number[]|明文数据内容,数据长度建议不超过2M大小|
|mode|"C1C3C2" |
"C1C2C3"|SM2加密密文格式,默认"C1C3C2"|
|**输出参数**|||
|envelope required|Promise<Envelop e>|Envelope实例对象: • 通过 `Envelope.getCiphertext()` 方法获 取数据密文(_Array_)。 • 通过 `Envelope.getSymmetricKey()` 获 取加密数据的对称密钥对象(_SymmetricKey_ _对象_),可在对称加解密接口使用。 • 通过 `Envelope.getEncryptedKey()` 获 取到公钥加密的对称密钥密文(_Array_)。|

第 28 页 

2. 静态接口 

##### **示例代码** 

```
const Envelope = SSM.Envelope
const AsymmetricKey = SSM.AsymmetricKey
const Asymmetric = SSM.Asymmetric
const util = SSM.util
const key = new AsymmetricKey(Asymmetric.SM2, {
  PublicKey:
util.Hex.parse('437DAF98EC0B0C7DC67229A3A714636013ECF60F54810C9C2F51192D37E358
606BCA4A593C782799F30021ED49F1E04DC588878B4FA17D3CA753C86AE1C38173')
})
const plaintext = util.UTF8.parse("test data");
const envelop = await Envelope.ecbEnvelopeEncrypt(key, 'SM4', 128,
Symmetric.PKCS7Padding, plaintext);
const ciphertext = envelop.getCiphertext();
const symmetriKey = envelop.getSymmetricKey();
const encryptedKey = envelop.getEncryptedKey();
```

### 2.16. **数字信封** ECB **解密** 

###### 接口定义 

```
Envelope.ecbEnvelopeDecrypt(key, algorithm, encryptedKey, padding, plaintext,
mode)
```

##### SM4 ECB算法模式加密明文数据。 

##### **输入参数** 

|key required|AsymmetricKey|SM2对称密钥实例,需要包含私钥|
|---|---|---|
|algorithm required|'SM4'|指定具体的对称算法|
|encryptedKey require d|Number[]|ECB数字信封加密的密钥密文|

第 29 页 

|||2.静态接口|
|---|---|---|
|padding required|"NoPadding" |
"ZeroPadding"
|
"PKCS7Padding" |
"ISO10126Paddin
g"
|
"ISO_ICE_7816d4P
adding"
|
"Ansix923Padding
"|填充类型|
|plaintext required|Number[]|ECB数字信封加密的数据密文|
|mode|"C1C3C2" |
"C1C2C3"|SM2加密密文格式,默认"C1C3C2"|
|**输出参数**|||
|result required|Promise<Number []>|明文数据|

第 30 页 

2. 静态接口 

##### **示例代码** 

```
const Envelope = SSM.Envelope
const AsymmetricKey = SSM.AsymmetricKey
const Asymmetric = SSM.Asymmetric
const util = SSM.util
const key = new AsymmetricKey(Asymmetric.SM2, {
  PublicKey:
util.Hex.parse('F5E6C9E11B6995226B340B301F73D6CFA178BC09C580347B218FC09DA8F9D4
2CEBE7C6D4A1527086D78B5EE68BA842DE6A1EAD6EF6897F5AD7E3F4B9785C593A'),
  PrivateKey:
util.Hex.parse('85CE68D3370A9FC5D7F05B7578E223DF118AE8BD960EB274533DE99F53F180
C0')
```

##### `})` 

```
const plaintext = util.UTF8.parse("test data");
const envelop = await Envelope.ecbEnvelopeEncrypt(key, 'SM4', 128,
Symmetric.PKCS7Padding, plaintext);
const ciphertext = envelop.getCiphertext();
const symmetriKey = envelop.getSymmetricKey();
const encryptedKey = envelop.getEncryptedKey();
const result = await Envelope.ecbEnvelopeDecrypt(key, 'SM4', encryptedKey,
Symmetric.PKCS7Padding, ciphertext)
```

### 2.17. **数字信封 计算** HMAC 

###### 接口定义 

```
Envelope.hmac(key, bits, hashAlgorithm, padding, plaintext, mode)
```

##### 数字信封 HMAC。 

##### **输入参数** 

|key required|AsymmetricKey|SM2非对称实例对象|
|---|---|---|
|bits required|Number|HMAC的密钥长度,单位bit,最小值为64|
|hashAlgorithm requi red|'SM3'|算法类型|

第 31 页 

|||2.静态接口|
|---|---|---|
|padding required|"NoPadding" |
"ZeroPadding"
|
"PKCS7Padding"|填充方式|
|plaintext required|Number[]|明文数据内容,数据长度建议不超过5M大小|
|mode|"C1C3C2" |
"C1C2C3"|SM2加密密文格式,默认"C1C3C2"|
|**输出参数**|||
|envelope required **示例代码**|Promise<Envelop e>|Envelop实例对象: • 通过 `Envelope.getEncryptedKey()` 获 取加密的密钥 `encryptedCAK` 字节数组 (_Array_)。 • 通过 `Envelope.getHmac()` 获取数据的 mac字节数组(_Array_)。 • 通过 `Envelope.getSecretData()` 获取 HMAC密钥(_SecretData对象_)。|

```
const Envelope = SSM.Envelope
const AsymmetricKey = SSM.AsymmetricKey
const Asymmetric = SSM.Asymmetric
const util = SSM.util
const key = new AsymmetricKey(Asymmetric.SM2, {
  PublicKey:
util.Hex.parse('437DAF98EC0B0C7DC67229A3A714636013ECF60F54810C9C2F51192D37E358
606BCA4A593C782799F30021ED49F1E04DC588878B4FA17D3CA753C86AE1C38173')
})
const plaintext = util.UTF8.parse("test data");
const envelop = await Envelope.hmac(key, 64, Hash.SM3, 'NoPadding',
plaintext);
const hmac = envelop.getHmac();
const secretData = envelop.getSecretData();
const encryptedKey = envelop.getEncryptedKey();
```

第 32 页 

2. 静态接口 

### 2.18. **数字信封 验证** HMAC 

###### 接口定义 

```
Envelope.hmacVerify(key, hashAlgorithm, encryptedKey, padding, plaintext,
hmac, mode)
```

数字信封 HMAC。 

##### **输入参数** 

|key required|AsymmetricKey|SM2非对称实例对象,需包含私钥|
|---|---|---|
|hashAlgorithm requi red|'SM3'|算法类型|
|encryptedKey require d|Number[]|数字信封hmac计算得到的密钥密文|
|padding required|"NoPadding" |
"ZeroPadding"
|
"PKCS7Padding"|填充方式|
|plaintext required|Number[]|明文数据内容|
|hmac required|Number[]|数字信封hmac计算得到的mac字节数组|
|mode|"C1C3C2" |
"C1C2C3"|SM2加密密文格式,默认"C1C3C2"|
|**输出参数**|||
|result required|Promise<Boolean >|hmac验证结果|

第 33 页 

2. 静态接口 

##### **示例代码** 

```
const Envelope = SSM.Envelope
const AsymmetricKey = SSM.AsymmetricKey
const Asymmetric = SSM.Asymmetric
const util = SSM.util
const key = new AsymmetricKey(Asymmetric.SM2, {
  PublicKey:
util.Hex.parse('F5E6C9E11B6995226B340B301F73D6CFA178BC09C580347B218FC09DA8F9D4
2CEBE7C6D4A1527086D78B5EE68BA842DE6A1EAD6EF6897F5AD7E3F4B9785C593A'),
  PrivateKey:
util.Hex.parse('85CE68D3370A9FC5D7F05B7578E223DF118AE8BD960EB274533DE99F53F180
C0')
})
const plaintext = util.UTF8.parse("test data");
const envelop = await Envelope.hmac(key, 64, Hash.SM3, 'NoPadding',
plaintext);
const hmac = envelop.getHmac();
const secretData = envelop.getSecretData();
const encryptedKey = envelop.getEncryptedKey();
const result = await Envelope.hmacVerify(key, Hash.SM3, encryptedKey,
'NoPadding', plaintext, hmac)
```

### 2.19. **密钥管理** 

##### 密钥管理包括: 

- 密钥生成:SDK 中由 `KeyGenerator` 类提供密钥生成服务。 

- 密钥创建:SDK 中由 `KeyCreator` 类提供密钥创建服务。 

- 密钥导入:SDK 中由 `KeyImport` 类提供密钥导入服务。 

- 密钥导出:SDK 中由 `KeyExport` 类提供密钥导出服务。 

- 密钥销毁:SDK 中由 `KeyDestroy` 类提供密钥销毁服务。 

- 密钥重置:SDK 中由 `KeyReset` 类提供密钥销毁服务。 

##### **SymmetricKey** 

- 可以通过 _SymmetricKey.getKey()_ 方法获取生成的密钥值。 

- 可使用 _SSM.util.Hex.stringify(byte)_ 转换密钥值为 16 进制字符串。 

- 可使用 _SSM.util.Helper.arrayToBase64(byte)_ 转换密钥值为 Base64 字符串。 

第 34 页 

2. 静态接口 

##### **AsymmetricKey** 

- 通过 _AsymmetricKey.getPublicKey()_ 方法获取生成的密钥公钥值。 

- 通过 _AsymmetricKey.getPrivateKey()_ 方法获取生成的密钥私钥值。 

- 可使用 _SSM.util.Hex.stringify(byte)_ 转换密钥值为 16 进制字符串。 

- 可使用 _SSM.util.Helper.arrayToBase64(byte)_ 转换密钥值为 Base64 字符串。 

##### **SecretData** 

- 可以通过 _SecretData.getKey()_ 方法获取生成的密钥值。 

- 可使用 _SSM.util.Hex.stringify(byte)_ 转换密钥值为 16 进制字符串。 

- 可使用 _SSM.util.Helper.arrayToBase64(byte)_ 转换密钥值为 Base64 字符串。 

### 2.20. **密钥创建** 

密钥创建是指在 SSM 中生成一把密钥并将密钥存储到 SSM,并返回密钥的 ID。 

##### **密钥属性** 

##### 密钥属性通过 **new ssm.KeyAttributes(exportable, expiration)** 进行设置。 

- 通过 **KeyAttributes.exportable** 指定创建的密钥是否允许导出 

- 通过 **KeyAttributes.expiration** 指定创建的密钥的过期时间 

###### 接口定义 

```
KeyCreator.createSM4(keyAttr)
```

创建 SM4 密钥 

##### **输入参数** 

|keyAttr|KeyAttributes|密钥属性|
|---|---|---|
|**输出参数** key required|Promise<Symmet ricKey>|SM4对称密钥实例|

##### **示例代码** 

```
const key = await SSM.KeyCreator.createSM4(new SSM.KeyAttributes(true, new
Date(1712733327440)))
```

第 35 页 

2. 静态接口 

接口定义 

```
KeyCreator.createSM2(keyAttr)
```

##### 创建 SM2 密钥 

##### **输入参数** 

|keyAttr **输出参数**|KeyAttributes|密钥属性|
|---|---|---|
|key required|Promise<Asymme tricKey>|SM2非对称密钥实例|

##### **示例代码** 

```
const key = await SSM.KeyCreator.createSM2(new SSM.KeyAttributes(true, new
Date(1712733327440)))
```

###### 接口定义 

```
KeyCreator.createSecret(bits, keyAttr)
```

创建 Secret 密钥 

##### **输入参数** 

|bits required|Number|密钥长度|
|---|---|---|
|keyAttr|KeyAttributes|密钥属性|
|**输出参数**|||
|key required|Promise<SecretDa ta>|SecretData密钥实例|

第 36 页 

2. 静态接口 

##### **示例代码** 

```
const key = await SSM.KeyCreator.createSecret(128, new SSM.KeyAttributes(true,
new Date(1712733327440)))
```

### 2.21. **密钥生成** 

###### 接口定义 

```
KeyGenerator.generateSM4()
```

生成 SM4 密钥 

##### **输入参数** 

无参数 

##### **输出参数** 

keyrequired SymmetricKey SM4对称密钥实例 

##### **示例代码** 

```
const key = SSM.KeyGenerator.generateSM4()
```

###### 接口定义 

```
KeyGenerator.generateSM2()
```

生成 SM2 密钥 

##### **输入参数** 

无参数 

##### **输出参数** 

keyrequired AsymmetricKey SM2非对称密钥实例 

第 37 页 

2. 静态接口 

##### **示例代码** 

```
const key = SSM.KeyGenerator.generateSM2()
```

###### 接口定义 

```
KeyGenerator.generateSecret(bits)
```

生成 Secret 密钥 

##### **输入参数** 

|bits required **输出参数**|Number|密钥长度|
|---|---|---|
|key required|SecretData|SecretData密钥实例|

##### **示例代码** 

```
const key = SSM.KeyGenerator.generateSecret(128)
```

### 2.22. **密钥销毁** 

###### 接口定义 

```
KeyDestroy.destroySymmetricKey(keyID)
```

销毁对称密钥 

##### **输入参数** 

|keyID required **输出参数**|String|密钥ID|
|---|---|---|
|void|Promise<void>|无返回值|

第 38 页 

2. 静态接口 

##### **示例代码** 

```
const key = SSM.KeyDestroy.destroySymmetricKey('123')
```

###### 接口定义 

```
KeyDestroy.destroyPublicKey(keyID)
```

销毁公钥 

##### **注意事项** 

销毁公钥是指销毁通过 SSM.KeyCreator.importSM2 接口导入的公钥 

##### **输入参数** 

|keyID required|String|密钥ID|
|---|---|---|
|**输出参数**|||
|void|Promise<void>|无返回值|

##### **示例代码** 

```
const key = SSM.KeyDestroy.destroyPublicKey('123')
```

###### 接口定义 

```
KeyDestroy.destroyPrivateKey(keyID)
```

销毁私钥 

##### **注意事项** 

销毁私钥是指销毁通过 SSM.KeyCreator.createSM2 接口创建的密钥对,这里公私钥都会被 销毁,因为私钥销毁后公钥存在着没有任何密码学上的意义 

##### **输入参数** 

第 39 页 

2. 静态接口 

|keyID required|String|密钥ID|
|---|---|---|
|**输出参数**|||
|void|Promise<void>|无返回值|

##### **示例代码** 

```
const key = SSM.KeyDestroy.destroyPrivateKey('123')
```

###### 接口定义 

```
KeyDestroy.destroySecret()
```

销毁 Secret 密钥 

##### **输入参数** 

|keyID required|String|密钥ID|
|---|---|---|
|**输出参数**|||
|void|Promise<void>|无返回值|
|**示例代码**|||

```
const key = SSM.KeyDestroy.destroySecret('123')
```

### 2.23. **密钥重置** 

##### 此接口会删除所有的密钥,请谨慎使用。 

###### 接口定义 

```
KeyReset.reset()
```

删除所有密钥 

第 40 页 

2. 静态接口 

##### **输入参数** 

无参数 

##### **输出参数** 

void Promise<void> 无返回值 **示例代码** `const key = SSM.KeyReset.reset()` 

### 2.24. **密钥导入** 

###### 接口定义 

`KeyImport.importSM4(key)` 导入 SM4 密钥 

##### **输入参数** 

|key required Number[] **输出参数**|SM4对称密钥|
|---|---|
|key required Promise<Symmet ricKey>|SM4对称密钥实例,可以通过 `SymmetricKey#getKeyID()` 方法获取密钥的ID|
|**示例代码**||
|`const sm4Key = SSM.util.Hex.parse(` `const key = await SSM.KeyImport.im` `const keyID = key.getKeyID();`|`'6364AA97A840881991246905DE4EF588');` `portSM4(sm4Key);`|

第 41 页 

2. 静态接口 

接口定义 

```
KeyImport.importSM2(public Key)
```

##### 导入 SM2 密钥 

##### **输入参数** 

publicKeyrequired Number[] SM2非对称密钥公钥 **输出参数** keyrequired Promise<Asymme SM2非对称密钥实例 tricKey> 

##### **示例代码** 

```
const public Key =
SSM.util.Hex.parse('4A097F07FD2430E0D2C0B399F17EC0105B90417FBFA835746D5435E9D3
69E361E14064C1EAC583278EBCC5190A31276573D1ED0BC171FCFB74CFB9D05B87E9CF')
const key = await SSM.KeyImport.importSM2(public Key)
```

###### 接口定义 

```
KeyImport.importSecret(key)
```

导入 Secret 密钥 

##### **输入参数** 

|key required|Number[]|Secret密钥|
|---|---|---|
|**输出参数** key required|Promise<SecretDa ta>|SecretData密钥实例|

第 42 页 

2. 静态接口 

##### **示例代码** 

```
const secret = SSM.util.Hex.parse('857BC2108C7CAF1A7C9358D825C2A242')
const key = await SSM.KeyImport.importSecret(secret)
```

### 2.25. **密钥导出** 

###### 接口定义 

```
KeyExport.export SM4(keyID)
```

导出对称密钥 

##### **输入参数** 

|keyID required|String|密钥ID|
|---|---|---|
|**输出参数**|||
|key required|Promise<Symmet ricKey>|SM4对称密钥实例对象,可以通过 `SymmetricKey#getKey()` 方法获取密钥值|

##### **示例代码** 

```
const key = await SSM.KeyExport.export SM4('123')
const keyValue = key.getKey()
```

###### 接口定义 

```
KeyExport.export SM2(keyID)
```

##### 导出SM2非对称密钥 

##### **注意事项** 

导出公钥是指导出通过 SSM.KeyCreator.importSM2 接口导入的公钥 

##### **输入参数** 

第 43 页 

2. 静态接口 

required keyID String 密钥ID **输出参数** keyrequired Promise<Asymme SM2非对称密钥实例对象 tricKey> 

##### **示例代码** 

```
const key = await SSM.KeyExport.export SM2('123')
```

###### 接口定义 

```
KeyExport.export Secret()
```

导出 Secret 密钥 

##### **输入参数** 

|keyID required|String|密钥ID|
|---|---|---|
|**输出参数**|||
|key required|Promise<SecretDa ta>|SecretData密钥实例对象|
|**示例代码**|||

```
const key = await SSM.KeyExport.export Secret('123')
```

### 2.26. 16 **进制的字符串转** _Array_ **数组** 

###### 接口定义 

```
util.Hex.parse(data)
```

16 进制的字符串转 _Array_ 数组 

第 44 页 

2. 静态接口 

##### **输入参数** 

datarequired String 待处理 16 进制的字符串数据 **输出参数** resultrequired Number[] 生成的 _Array_ 数据 

##### **示例代码** 

```
const res = SSM.util.Hex.parse('414141')
```

### 2.27. _Array_ **数组转** 16 **进制的字符串** 

###### 接口定义 

```
util.Hex.stringify(data)
```

_Array_ 数组转 16 进制的字符串 

##### **输入参数** 

datarequired Number[] 待处理 _Array_ 数据 **输出参数** resultrequired String 生成的 16 进制的字符串数据 **示例代码** 

```
const arr = SSM.util.Hex.parse('414141')
const res = SSM.util.Hex.stringify(arr)
```

### **-** 2.28. UTF 8 **进制的字符串转** _Array_ **数组** 

第 45 页 

2. 静态接口 

接口定义 

```
util.UTF8.parse(data)
```

UTF-8 进制的字符串转 _Array_ 数组 

##### **输入参数** 

|data required|String|待处理UTF-8进制的字符串数据|
|---|---|---|
|**输出参数** result required|Number[]|生成的 _Array_ 数据|

##### **示例代码** 

```
const res = SSM.util.UTF8.parse('test data')
```

### **-** 2.29. _Array_ **数组转** UTF 8 **进制的字符串** 

###### 接口定义 

```
util.UTF8.stringify(data)
```

_Array_ 数组转 UTF-8 进制的字符串 

##### **输入参数** 

|data required|Number[]|待处理 _Array_ 数据|
|---|---|---|
|**输出参数** result required|String|生成的UTF-8进制的字符串数据|

##### **示例代码** 

```
const arr = SSM.util.UTF8.parse('test data')
const res = SSM.util.UTF8.stringify(arr)
```

第 46 页 

2. 静态接口 

### 2.30. BASE64 **字符串转** _Array_ **数组** 

###### 接口定义 

```
util.Helper.base64ToArray(data)
```

BASE64 字符串转 _Array_ 数组 

##### **输入参数** 

|data required|String|待处理BASE64字符串数据|
|---|---|---|
|**输出参数** result required|Number[]|生成的 _Array_ 数据|

##### **示例代码** 

```
const res = SSM.util.Helper.base64ToArray('QUFB')
```

### 2.31. _Array_ **数组转** BASE64 **字符串** 

###### 接口定义 

```
util.Helper.arrayToBase64(data)
```

_Array_ 数组转 BASE64 字符串 

##### **输入参数** 

|data required|Number[]|待处理 _Array_ 数据|
|---|---|---|
|**输出参数** result required|String|生成的BASE64字符串数据|

第 47 页 

2. 静态接口 

##### **示例代码** 

```
const arr = SSM.util.Helper.base64ToArray('QUFB')
const res = SSM.util.Helper.arrayToBase64(arr)
```

### 2.32. **版本信息** 

###### 接口定义 

```
Version.getVersion()
```

SM2算法加密 

##### **输入参数** 

无参数值 

##### **输出参数** 

|version required|Promise<Version>|版本信息对象:|
|---|---|---|

- 通过 `Version.getName()` 方法获取包名称 ( _String_ )。 

- 通过 `Version.getVersions()` 获取版本 号( _String_ )。 

- • 通过 `Version.getBuildTime()` 获取构建 时间( _String_ )。 

- • 通过 `Version.getCommitID()` 获取提 交ID( _String_ )。 

##### **示例代码** 

```
const version = await SSM.Version.getVersion()
const name = version.getName()
const version = version.getVersions()
const buildTime = version.getBuildTime()
const commitID = version.getCommitID()
```

第 48 页
