# grep / hilog 速查表

## Android 源码扫描

```bash
# URL 常量 object（Phase 1.1）
grep -rn 'object\s\+\w*Url\b' android_src --include='*.kt' | grep -v '/build/'
grep -rn 'const val\s\+\w\+\s*=\s*"/' android_src --include='*.kt' | grep -v '/build/'
grep -rn '@POST("/\|@GET("/' android_src --include='*.kt' | grep -v '/build/'

# body 构造函数（Phase 1.2）
grep -rn 'mutableMapOf("' android_src --include='*.kt' -A 5 | grep -v '/build/'
grep -rn 'fun\s\+\w*[Bb]ody\b' android_src --include='*.kt' -A 3 | grep -v '/build/'

# @SerializedName 全表（Phase 1.3）
grep -rn '@SerializedName(' android_src --include='*.java' --include='*.kt' | grep -v '/build/'

# 签名算法（Phase 1.4）
grep -rln 'HmacSHA1\|MessageDigest\|MD5_TABLE\|b2hStr\|byteToHex' android_src --include='*.java' --include='*.kt' | grep -v '/build/'
grep -A 3 -B 1 "'[a-fA-F]'" $(grep -rln 'MD5_TABLE\|toHex\|b2hStr' android_src --include='*.kt' --include='*.java')

# 拦截器实现
grep -rln 'Interceptor\|chain\.proceed' android_src --include='*.kt' | grep -v '/build/'

# 公参 / platformInfo（Phase 1.5）
grep -rln 'AppFormInfo\|PlatformInfo\|CommonParams' android_src --include='*.kt' --include='*.java' | grep -v '/build/'

# 构建期注入字段（Phase 1.6）
grep -n 'productFlavors\|manifestPlaceholders\|buildConfigField' android_src/app/build.gradle*
grep -A 1 '<meta-data' android_src/app/src/main/AndroidManifest.xml
cat android_src/channel/product.xml 2>/dev/null
```

## HMOS 源码扫描

```bash
# URL 常量（对账 Android）
grep -rn "const URL_" hmos_src/network/services --include='*.ets'

# AppStorage 写入点
grep -rn "AppStorage.setOrCreate\|AppStorage.set\b" hmos_src --include='*.ets'

# 找拦截器
grep -rn "implements HttpInterceptor" hmos_src --include='*.ets'

# 找加密相关
grep -rn 'cryptoFramework\|createMd\|createMac\|createSymKeyGenerator' hmos_src --include='*.ets'

# 找 @Prop 滥用（应改 @StorageProp 的）
grep -rn "@Prop\s\+isLogin\|@Prop\s\+isVip\|@Prop\s\+userId\|@Prop\s\+userName" hmos_src --include='*.ets'

# 找 dot-notation AppStorage 误用（pitfalls B3）
grep -rn "AppStorage\.get<.*>\(['\"]\w\+\.\w" hmos_src --include='*.ets'

# 找行内 {} 字面值（pitfalls B4 编译期错）
grep -rn "= {}" hmos_src --include='*.ets'
```

## hilog 实时筛选

```bash
# 看请求/响应（依赖 HttpLogInterceptor isDebug=true）
hdc shell hilog | grep -E 'HTTP >>>|HTTP <<<'

# 看启动初始化
hdc shell hilog | grep -E 'EntryAbility|SplashService|PreferencesUtil'

# 看登录链路
hdc shell hilog | grep -E 'LoginService|UserRepository|USER_DATA_UPDATE'

# 看 OAID / androidId
hdc shell hilog | grep -E 'aggregateOaid|ensureAndroidId|requestOAID'

# 看签名
hdc shell hilog | grep -E 'SignUtil|hmacSha|signature|computeVendor'

# 看拦截器
hdc shell hilog | grep -E 'HttpInterceptor|ResponseInterceptor|RequestInterceptor'

# 看业务码 / Token 过期
hdc shell hilog | grep -E 'errorCode|-1001|TokenExpired'

# 看 cryptoFramework 字节级错误
hdc shell hilog | grep -E 'ConvertSymmKey|HCF|AsyncConvertKey|convert sym key'

# 实时跟踪某 domain ID
hdc shell hilog -G 0x0013

# 看错误级别
hdc shell hilog -L E

# 清缓冲后再跟
hdc shell hilog -r && hdc shell hilog | grep -E '<pattern>'
```

## 字节级诊断（SignUtil 内一次性加日志）

```typescript
hilog.info(DOMAIN, TAG,
  'utf8Bytes diagnostic: input.len=%{public}d encoded.byteOffset=%{public}d encoded.buffer.size=%{public}d encoded.length=%{public}d',
  str.length, encoded.byteOffset, encoded.buffer.byteLength, encoded.length);
```

判定：`byteOffset === 0` ✅ + `encoded.buffer.byteLength === encoded.length` ✅ + `encoded.length` 是真实 UTF-8 字节数 ✅。任一不符 → 走防御性拷贝。

## 编译期错误速查

```bash
hvigorw assembleHap 2>&1 | tee build.log
grep "ERROR\|Error Message" build.log | head -20
ohpm list
hvigorw clean && hvigorw assembleHap --no-daemon
```

项目根目录无 `hvigorw` 包装脚本时（用 DevEco SDK 自带 hvigor）：

```bash
# Windows：用 DevEco 内置 node 调 hvigorw.js（路径含空格要引号）
node "<DevEco>/tools/hvigor/bin/hvigorw.js" clean assembleHap --mode module -p product=<product> -p buildMode=debug --no-daemon
# 或直接触发 hmos-fix-build-errors skill —— 自带「编译→修错→再编译」闭环，也会处理 wrapper 缺失
```

## adb / hdc 常用

```bash
hdc list targets
hdc install <path-to-hap>
hdc uninstall <bundle-name>
hdc shell aa start -b <bundle> -a EntryAbility
hdc shell aa force-stop <bundle>
hdc shell bm clean -n <bundle> -d         # 清应用数据
# hdc 不在 PATH 时用全路径：<DevEco>/sdk/default/openharmony/toolchains/hdc(.exe)
```

## ⚠ Windows + git-bash：设备路径参数会被 MSYS 改写

git-bash(MSYS) 会把**任何以 `/` 开头的命令行参数**当 Unix 路径转成 Windows 路径。hdc/adb
命令里的**设备侧路径**（`/data/local/tmp/...`、`/sdcard/...`）因此被改写成
`<git安装目录>/data/local/tmp/...`，报 `realpath nullptr` / `file ... invalid` / `no such file`。

典型受害命令：`hdc file recv /data/local/tmp/x`、`hdc shell snapshot_display -f /data/...`、
`hdc shell ls /data/...`、`adb shell ...`（参数本身不带 `/` 的命令不受影响，故 `aa start`/`hilog` 等正常）。

**修复 —— 命令前置一次即可：**

```bash
export MSYS_NO_PATHCONV=1      # 之后整段命令里的 /device/path 不再被改写
hdc file recv /data/local/tmp/shot.jpeg ./shot.jpeg
hdc shell snapshot_display -f /data/local/tmp/shot.jpeg
```

或把命令交给 `cmd.exe //c "<command>"` 执行（绕过 MSYS）。本机侧路径含空格仍要加引号。
