/**
 * verify-sign.js — 签名算法离线验证脚手架（Phase 3）
 *
 * 用途：把 Phase 0 抓到的真实请求（body + ts/时间戳 + token + 期望签名）喂进来，
 *       用 Node crypto 跑你"按 Android 源码翻译"的候选签名算法，逐字节比对期望值。
 *       **对上了再去写 HMOS SignUtil** —— 把"实现后赌联调"变成"验证后写代码"。
 *
 * 用法：
 *   1) 编辑【② 候选算法】computeSign()，按 Android 源码把签名算法翻译过来。
 *   2) 编辑【③ 测试向量】TEST_VECTORS，从抓包（http-capture-proxy / logcat）粘贴真实样本。
 *   3) 运行：node verify-sign.js
 *   4) 全 PASS → 算法确认，HMOS SignUtil 照抄；有 MISMATCH → 按中间值定位（大小写 / 拼接顺序 / 编码）。
 */
const crypto = require('crypto');

// ============ ① 通用哈希助手（够用直接调，一般不用改） ============
const fmt = (hex, up) => (up ? hex.toUpperCase() : hex.toLowerCase());
const md5 = (s, up) => fmt(crypto.createHash('md5').update(Buffer.from(s, 'utf-8')).digest('hex'), up);
const sha1 = (s, up) => fmt(crypto.createHash('sha1').update(Buffer.from(s, 'utf-8')).digest('hex'), up);
const sha256 = (s, up) => fmt(crypto.createHash('sha256').update(Buffer.from(s, 'utf-8')).digest('hex'), up);
const hmacSha1B64 = (s, key) =>
  crypto.createHmac('sha1', Buffer.from(key, 'utf-8')).update(Buffer.from(s, 'utf-8')).digest('base64');
const hmacSha1Hex = (s, key, up) =>
  fmt(crypto.createHmac('sha1', Buffer.from(key, 'utf-8')).update(Buffer.from(s, 'utf-8')).digest('hex'), up);
// Kotlin Long 逐级整除（避免 JS 一次性除法的中间精度差）
const longDiv = (n, ...divs) => divs.reduce((acc, d) => Math.floor(acc / d), n);

// ============ ② 候选算法 —— 按 Android 源码改这里 ============
// 入参 v 是【③】里的一条测试向量。返回算出的签名串。
function computeSign(v) {
  // ↓↓↓ 示例：自有业务签名 ss = SHA1upper( body + ts + token + MD5upper(分钟桶 + token) + key )
  //     对账 Android cn.sanfate.pub.network.Sign.createHttpSign（分钟桶 = ts/1000/60 Long 整除）
  const minute = longDiv(v.ts, 1000, 60);
  const inner = md5(String(minute) + v.token, true);
  const content = v.body + String(v.ts) + v.token + inner + v.key;
  return sha1(content, true);
  // ↑↑↑ 换成你项目的真实算法（讯飞类厂商签名常见：hmacSha1B64(md5(appId+ts,false), secret)）
}

// ============ ③ 测试向量 —— 从真实抓包粘贴 ============
// 每条 = 一次真实请求：把抓到的 body / ts(请求头 tt) / token / key / 期望签名(请求头 ss) 填进来。
const TEST_VECTORS = [
  // {
  //   name: '/app/config',
  //   body: '{"platformInfo":{...原样粘贴抓包 body...}}',
  //   ts: 1778897853330,                                  // 请求头 tt
  //   token: '8ee6ab12cbdff2faec1ca50669b9de72',
  //   key: 'z27vsnfeeb4nuxkjzfcd35nqvpx7xwd9',
  //   expectSign: '5BCAD179EA5B6CED33DC68E2679DDC20DB652C9F',  // 请求头 ss
  //   expectBodyLen: 461,                                 // 可选：body 的 UTF-8 字节数（核对粘贴完整）
  // },
];

// ============ runner（不用改） ============
if (TEST_VECTORS.length === 0) {
  console.log('⚠ TEST_VECTORS 为空 —— 先从抓包粘贴真实样本到【③】，再运行。');
  process.exit(0);
}
let allPass = true;
for (const v of TEST_VECTORS) {
  const got = computeSign(v);
  const signOk = got === v.expectSign;
  let line = `--- ${v.name} ---\n  sign : got=${got}\n  sign : exp=${v.expectSign}  ${signOk ? 'OK' : 'MISMATCH'}`;
  if (v.expectBodyLen !== undefined) {
    const len = Buffer.from(v.body, 'utf-8').length;
    const lenOk = len === v.expectBodyLen;
    line += `\n  body-len : got=${len} exp=${v.expectBodyLen}  ${lenOk ? 'OK' : 'MISMATCH (body 粘贴不完整?)'}`;
    if (!lenOk) allPass = false;
  }
  if (!signOk) allPass = false;
  console.log(line);
}
console.log('\n=== ' + (allPass ? 'ALL PASS — 算法已确认，可照抄 HMOS SignUtil' : 'FAIL — 见上方 MISMATCH') + ' ===');
