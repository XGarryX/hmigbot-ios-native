# 接口文档 

# 简介 

接口文档列出部分场景的部分接口,如需所有接口的内容,请查看详 情 安全密码算法 

密钥生成 

接口名称 

ohAegRandomHex(len: number): string 

# 接口说明 

导入模块: import { SafeRandom } from '@hw-agconnect/petalaegis'; 

生成十六进制编码格式的安全随机数,可用于对称加解密的密钥、 iv 等。 

参数说明 

参数: 

参数名 

类型 

必填 

说明 

len 

number 

是 

# 待生成安全随机数长度。 

返回值: 

参数 

类型 

说明 

字符串 

hexString 

生成 hexString 类型的安全随机数,长度为 len 。 

# 样例 

import {SafeRandom} from "@hms-security/agoh-crypto" 

let input = 20 

let Rest = SafeRandom. ohAegRandomHex (input) 

console.log("ohAegRandomHex", Rest); 

消息摘要计算 

接口名称 

ohAegSha256TextHex 

# 接口说明 

导入模块: import { AegSha256 } from '@hw-agconnect/petalaegis'; 

SHA256 消息摘要算法,返回十六进制编码的 SHA256 值 

参数说明 

参数: 参数名 类型 必填 说明 text string 或 Uint8Array 是 明文内容 返回值: 参数 类型 说明 字符串 

hexString 生成的加密 hexString 字符串。 样例 

import { AegSha256 } from "@hms-security/agoh-crypto" 

let input = "hello " let Rest = AegSha256. ohAegSha256TextHex (input) console.log("ohAegSha256TextHex ", Rest);
