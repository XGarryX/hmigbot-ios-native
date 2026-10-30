/**
 * 加密 / 签名原语（HarmonyOS cryptoFramework，仅通用机制 + 易错点）
 *
 * ⚠ 签名 / 加密的【具体算法步骤、参与内容、密钥】是项目级（决策清单 #3/#4）——
 *   从你项目 Android 源照搬，本文件**不预设任何算法 / 密钥**。下面只提供 HarmonyOS 侧
 *   md5 / sha / hmac / hex / base64 原语 + 3 个高频踩坑点，供你拼装出项目自己的签名。
 *
 * 三个必避坑（与 pitfalls Class A 对应）：
 *  1. utf8 字节防御性拷贝 —— TextEncoder.encodeInto 可能返回 byteOffset>0 / 共享 ArrayBuffer 的视图，
 *     直接喂 crypto 会多读字节 → 摘要错。必须 new Uint8Array(len).set(encoded) 拷成独立 buffer。
 *  2. createSymKeyGenerator('HMAC') 不带 digest 后缀 —— 'HMAC|SHA1' 等组合在部分 HarmonyOS 版本
 *     触发 ConvertSymmKey key length invalid。
 *  3. hex 大小写 —— 大写表 / 小写表喂给下一步（HMAC 输入 / 字符串拼接）字节不同 → 签名不一致。
 *     **照搬你项目 Android 端实际用的大小写**，不要默认。
 */

import { cryptoFramework } from '@kit.CryptoArchitectureKit';
import { util } from '@kit.ArkTS';
import { hilog } from '@kit.PerformanceAnalysisKit';

const TAG = 'SignUtil';
const DOMAIN = 0x0000;

/**
 * 签名 / 加密**原语工具**。用这些原语按你项目 Android 算法拼装具体签名（本文件不写具体算法）。
 */
export class SignUtil {
  // ===== hash → hex（upperCase 按你项目 Android 实际用的大小写选）=====
  static async md5(input: string, upperCase: boolean = true): Promise<string> {
    return SignUtil.digestHex(input, 'MD5', upperCase);
  }
  static async sha1(input: string, upperCase: boolean = true): Promise<string> {
    return SignUtil.digestHex(input, 'SHA1', upperCase);
  }
  static async sha256(input: string, upperCase: boolean = true): Promise<string> {
    return SignUtil.digestHex(input, 'SHA256', upperCase);
  }

  // ===== HMAC =====

  /** HMAC → 原始字节（再按需 bytesToHex / bytesToBase64）。alg 默认 SHA1，按项目改 SHA256 等。 */
  static async hmacBytes(input: string, secret: string, alg: string = 'SHA1'): Promise<Uint8Array> {
    const mac = cryptoFramework.createMac(alg);
    const keyBlob: cryptoFramework.DataBlob = { data: SignUtil.utf8Bytes(secret) };
    const symKeyGen = cryptoFramework.createSymKeyGenerator('HMAC'); // ← 坑 2：无 digest 后缀
    const symKey = await symKeyGen.convertKey(keyBlob);
    await mac.init(symKey);
    await mac.update({ data: SignUtil.utf8Bytes(input) });
    return (await mac.doFinal()).data;
  }

  static async hmacHex(input: string, secret: string, upperCase: boolean = false, alg: string = 'SHA1'): Promise<string> {
    return SignUtil.bytesToHex(await SignUtil.hmacBytes(input, secret, alg), upperCase);
  }
  static async hmacBase64(input: string, secret: string, alg: string = 'SHA1'): Promise<string> {
    return new util.Base64Helper().encodeToStringSync(await SignUtil.hmacBytes(input, secret, alg));
  }

  // ===== 字节工具 =====

  /** 坑 1：字符串 → UTF-8 独立 buffer（byteOffset=0），喂任何 crypto 前必做。 */
  private static utf8Bytes(str: string): Uint8Array {
    const encoded: Uint8Array = new util.TextEncoder('utf-8').encodeInto(str);
    const own: Uint8Array = new Uint8Array(encoded.length);
    own.set(encoded);
    return own;
  }

  private static async digestHex(input: string, algorithm: string, upperCase: boolean): Promise<string> {
    try {
      const md = cryptoFramework.createMd(algorithm);
      await md.update({ data: SignUtil.utf8Bytes(input) });
      const result: cryptoFramework.DataBlob = await md.digest();
      return SignUtil.bytesToHex(result.data, upperCase);
    } catch (e) {
      hilog.error(DOMAIN, TAG, 'digest %{public}s failed: %{public}s', algorithm, (e as Error).message);
      return '';
    }
  }

  /** 坑 3：hex 大小写按项目实际。 */
  private static bytesToHex(bytes: Uint8Array, upperCase: boolean): string {
    const digits: string = upperCase ? '0123456789ABCDEF' : '0123456789abcdef';
    let out: string = '';
    for (let i = 0; i < bytes.length; i++) {
      const b: number = bytes[i] & 0xFF;
      out += digits.charAt((b >>> 4) & 0x0F);
      out += digits.charAt(b & 0x0F);
    }
    return out;
  }
}
