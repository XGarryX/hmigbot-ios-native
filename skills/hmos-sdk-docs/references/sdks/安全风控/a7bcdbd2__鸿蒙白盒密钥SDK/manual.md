天密接口说明文档 

1 

天密接口说明文档 

2 

天密接口说明文档 

3 

天密接口说明文档 

4 

天密接口说明文档 

5 

天密接口说明文档 

6 

天密接口说明文档 

```
import { SoftMethods } from "@tianyu/WhiteBox"
let instance: SoftMethods = SoftMethods.getInstance();
```

7 

天密接口说明文档 

```
async wbInit(context: Context, userInfo: string, conTimeout: number, readTimeout:
number, debug: bollean): Promise<number>
```

8 

天密接口说明文档 

```
wbGetSdkVersion(): string
async wbLoadExportedKey(cipher: Uint8Array, name: string, safekey: bigint[]):
Promise<number>
```

9 

天密接口说明文档 

```
byte[]
wbCreateCipher(long safekey, int alg, int mode, int isPading, int direction, Str
ing pin, byte[] iv, byte[] in)
```

10 

天密接口说明文档 

11 

天密接口说明文档 

```
wbCreateSign(safekey: bigint, alg: number, pin: string, src: Uint8Array): ResultVo
```

12 

天密接口说明文档 

```
wbVerifySign(alg: number, sign: Uint8Array, pubkey: Uint8Array, src: Uint8Array):
number
```

13 

天密接口说明文档 

```
wbGetSafeKeyByName(name: string, safeKey: bigint[]): number
wbFreeSafeKey(safeKey: bigint): Promise<number>
```

14 

天密接口说明文档 

```
async wbClear(): Promise<number>
```

15 

天密接口说明文档 

16 

天密接口说明文档 

17 

天密接口说明文档 

18
