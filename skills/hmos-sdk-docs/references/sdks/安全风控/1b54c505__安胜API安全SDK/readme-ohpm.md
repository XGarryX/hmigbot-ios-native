> 来源: ohpm 中央仓 README(T1 信源) | 包: `@yd/security`(市场登记名 `@ansheng/security_sdk`) | ohpm 最新版: 1.1.7 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# **Security**

by ya dong 

[MIT License]

## Security

Security is core. It provides AES encrypt, AES decrypt, Hash(MD5, HmacMD5, SHA1~SHA512) messages.

#### MD5:

```arkts
let md5 = Security.md5("md5")
```

#### HMacSha:

```arkts
// HMacSha256
let hMacSha256 = await Security.hMacSha256('hMacSha256', '123456')
```

#### Sha:

```arkts
// sha256
let sha256 = await Security.sha256('sha256')
```

#### AES Encrypt & Decrypt:

```arkts
let plainText = '1662100123'
let key = 'afae4ec844ed14ca'
let iv = '67e7d725dfe24ca1'

// Encrypt
let result = await Security.aesEncrypt(plainText, key, iv)

// Decrypt
let dResult = await Security.aesDecrypt(result.data(), key, iv)

// DecryptWithHexString
let d2Result: string = (await Security.aesDecryptWithHexString("323342D5B1B8558F002A75BE1EAEF305",
            "afae4ec844ed14ca", "67e7d725dfe24ca1")).utf8String()
```

## SecurityResult

SecurityResult is the result class of Security. It provides convert result data to Uint8Array, string, HEX string,
Base64 string. The code indicating success or failure.

```arkts
data(): Uint8Array 
utf8String(): string 
hex(): string 
hexLower(): string
base64(): string
```

## install

```arkts
ohpm install @yd/security
```
