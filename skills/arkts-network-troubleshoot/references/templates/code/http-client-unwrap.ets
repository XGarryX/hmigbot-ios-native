/**
 * HTTP 客户端机制模板（通用机制 + 壳解析 + token 失效模式）
 *
 * 通用（直接复用）：execute / expectDataType:STRING / 空 body 守卫 / coerceToString / methodHeaders / try-finally / 日志。
 * 项目级（按决策清单填占位）：响应壳形状（嵌套/扁平、成功字段名与类型）、字段镜像表、token 失效码集
 *   —— 见 network-decision-checklist.md，取值去你当前项目 Android 源 + 真包确认。
 */

export class HttpClientConfig {
  baseUrl: string = '';
  connectTimeout: number = 15000;
  readTimeout: number = 15000;
  interceptors: HttpInterceptor[] = [];
  defaultHeaders: Record<string, string> = {};

  /**
   * 是否启用壳 unwrap + 字段镜像（按你项目 envelope 决定，见决策清单 #5/#6）。
   * "嵌套"壳：顶层 { data: {...} } → 抽 data + 镜像成功码/文案字段；"扁平"壳（如 {code,msg,data}）按需调整。
   * 三方域 / 结构不同的域：设 false，原样返回不 unwrap。
   */
  unwrapBaseBean: boolean = false;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
    // Accept 适用所有方法；Content-Type 在 methodHeaders() 里按 GET/POST 区分追加
    // 避免 GET 误带 Content-Type（pitfalls I2）
    this.defaultHeaders['Accept'] = 'application/json';
  }

  /**
   * 按 HTTP 动词区分 default headers
   * GET / DELETE：仅 Accept（无 body 不应带 Content-Type，pitfalls I2）
   * POST / PUT / PATCH：Content-Type + Accept
   */
  static methodHeaders(method: http.RequestMethod): Record<string, string> {
    const isGetLike = method === http.RequestMethod.GET || method === http.RequestMethod.DELETE;
    if (isGetLike) {
      return { 'Accept': 'application/json' };
    }
    return { 'Content-Type': 'application/json', 'Accept': 'application/json' };
  }
}

export class HttpClient {
  private static _defaultInstance: HttpClient | null = null;
  private static _vendorInstance: HttpClient | null = null;

  /** 自有业务实例 —— 启用 unwrap */
  static defaultInstance(): HttpClient {
    if (HttpClient._defaultInstance === null) {
      const config = new HttpClientConfig(HttpClient.resolveDefaultBaseUrl());
      config.unwrapBaseBean = true;   // ← 自有业务启用 unwrap
      config.interceptors = [
        new CommonRequestInterceptor(),
        new RequestInterceptor(),
        new ResponseInterceptor(),
        new HttpLogInterceptor()
      ];
      HttpClient._defaultInstance = new HttpClient(config);
    }
    return HttpClient._defaultInstance;
  }

  /**
   * 三方厂商实例（如调用某第三方 API 服务）—— 不启用 unwrap
   * <VENDOR_BASE_URL> 替换为你项目实际的三方厂商域名；多个三方厂商各建一个实例
   */
  static vendorInstance(): HttpClient {
    if (HttpClient._vendorInstance === null) {
      const config = new HttpClientConfig('<VENDOR_BASE_URL>');
      // config.unwrapBaseBean = false  ← 默认 false，三方域不 unwrap
      config.interceptors = [new HttpLogInterceptor()];
      HttpClient._vendorInstance = new HttpClient(config);
    }
    return HttpClient._vendorInstance;
  }

  private config: HttpClientConfig;
  private constructor(config: HttpClientConfig) { this.config = config; }

  private async executeAndParse<T>(req: HttpRequest): Promise<T> {
    const resp = await this.execute(req);
    // 空 body 守卫（pitfalls I3）— JSON.parse('') 会抛 SyntaxError，必须显式区分
    if (resp.body.length === 0) {
      return JSON.parse('{}') as T;
    }
    let root: Object;
    try {
      root = JSON.parse(resp.body) as Object;
    } catch (_e) {
      const friendlyMsg = resp.code === 200 ? '响应数据格式错误' : '服务异常 (HTTP ' + resp.code.toString() + ')';
      throw new HttpException(friendlyMsg, resp.code, -7);
    }
    if (this.config.unwrapBaseBean && typeof root === 'object' && root !== null) {
      return HttpClient.unwrapAndMirror(root) as T;
    }
    return root as T;
  }

  /**
   * 执行真实 http 请求（精简版示意，工程内按需扩展拦截器链 / retry / metrics）
   *
   * 关键防御点（与 pitfalls Class I 对应）：
   * 1. expectDataType: http.HttpDataType.STRING —— 强制 result 为 string，避免框架按 Content-Type
   *    自动 parse 为 Object 导致 typeof !== 'string' 走错分支（pitfalls I1）
   * 2. methodHeaders(method) —— GET/DELETE 仅 Accept，POST/PUT 含 Content-Type（pitfalls I2）
   * 3. coerceToString(result) —— 即使框架版本变化返回 Object/ArrayBuffer 也能兼容（pitfalls I1 防御性）
   *
   * 前置：必须在 entry/src/main/module.json5 声明 ohos.permission.INTERNET 权限（pitfalls I4）
   * 否则所有请求未发出即被系统拒绝
   */
  private async execute(req: HttpRequest): Promise<{ code: number; body: string }> {
    const request = http.createHttp();
    try {
      const headers = HttpClientConfig.methodHeaders(req.method);
      // 合并业务 headers（如 token / sign / tt / ss）覆盖 default
      for (const k of Object.keys(req.headers ?? {})) {
        headers[k] = req.headers[k];
      }
      const response: http.HttpResponse = await request.request(req.url, {
        method: req.method,
        header: headers,
        extraData: req.body,
        expectDataType: http.HttpDataType.STRING,   // ← 关键：强制 string，避免自动 parse 陷阱
        readTimeout: this.config.readTimeout,
        connectTimeout: this.config.connectTimeout
      });
      return { code: response.responseCode, body: HttpClient.coerceToString(response.result) };
    } finally {
      request.destroy();
    }
  }

  /**
   * 把 response.result（string | Object | ArrayBuffer）兼容性地转为 string
   * 即使框架行为变化也能 fallback（pitfalls I1 防御性）
   * - string → 直接返回
   * - ArrayBuffer → UTF-8 解码
   * - Object → JSON.stringify 兜底（理论上 expectDataType=STRING 后不会触发）
   * - null/undefined → ''
   */
  private static coerceToString(result: string | Object | ArrayBuffer): string {
    if (typeof result === 'string') {
      return result;
    }
    if (result instanceof ArrayBuffer) {
      try {
        const decoder = util.TextDecoder.create('utf-8');
        return decoder.decodeToString(new Uint8Array(result));
      } catch (_e) {
        return '';
      }
    }
    if (result !== null && result !== undefined) {
      try { return JSON.stringify(result); } catch (_e) { return ''; }
    }
    return '';
  }

  /**
   * 解包 + 镜像字段名（处理"嵌套 data + 镜像"这一种常见壳；扁平壳按你项目调整）。
   * 字段名（data 容器名、成功码字段、文案字段）按你项目 envelope 替换占位（决策清单 #5/#6）。
   */
  private static unwrapAndMirror(root: Object): Object {
    const top = root as Record<string, Object>;

    // 1) 抽取 data 部分（如有），不存在则用扁平顶层
    let body: Record<string, Object>;
    const dataField = top['data'];
    if (typeof dataField === 'object' && dataField !== null && !Array.isArray(dataField)) {
      body = dataField as Record<string, Object>;
    } else {
      body = top;
    }

    // 2) 镜像 @SerializedName 等价
    HttpClient.mirrorFields(body);

    // 3) 兜底：顶层成功码/文案字段也镜像到内层（字段名按你项目 envelope，<...> 为占位）
    if (body !== top) {
      // if (top['<successField>'] !== undefined && body['<okField>'] === undefined) body['<okField>'] = top['<successField>'];
      // if (top['<messageField>'] !== undefined && body['<msgField>'] === undefined) body['<msgField>'] = top['<messageField>'];
    }
    return body;
  }

  /**
   * 字段镜像表（HarmonyOS 无 @SerializedName，须手工镜像）—— 每条 [后端 JSON 字段名, 代码字段名]。
   * 全部按你项目 Android @SerializedName 照搬，下面均为占位。
   */
  private static FIELD_MAP: Map<string, string> = new Map([
    ['<jsonFieldA>', '<codeFieldA>'],
    ['<jsonFieldB>', '<codeFieldB>'],
    // ... 按你项目实际 @SerializedName 扩展
  ]);

  private static mirrorFields(body: Record<string, Object>): void {
    HttpClient.FIELD_MAP.forEach((arktsName, jsonName) => {
      if (body[jsonName] !== undefined && body[arktsName] === undefined) {
        body[arktsName] = body[jsonName];
      }
    });
  }

  /**
   * token 失效处理模式（通用骨架）。接到 executeAndParse 解析出业务码后 + HTTP 鉴权失败两处。
   *
   * ⚠ 失效码集是【项目级】（决策清单 #7）：从你项目 token 失效判定逻辑照搬，替换 TOKEN_INVALID_CODES。
   * 关键防御（多项目实践验证）：
   *  1. 重入守卫：token 已空 → 直接 return（防并发请求重复清 + 重复广播/跳转）。
   *  2. 单一事实源读 token：从你项目状态层读（V2 用 AppStorageV2.connect 读 V2 单例）；
   *     **不要**把 V2 @ObservedV2 实例镜像进 V1 AppStorage（见 pitfalls B7）。
   *  3. 不清设备级标识（设备 id 跨账号保留）。
   *  4. 区分"已绑定账号 token 过期"与"游客/匿名态"：若匿名 token 会被某些接口拒，匿名态失效码**不应**
   *     清掉刚建立的匿名 token（否则登录链路 token 永远为空，见 pitfalls D4c）。
   *  5. 动作（跳登录 / 广播登录态）按项目；跳转前判断是否已在登录页，防重入。
   */
  private static readonly TOKEN_INVALID_CODES: readonly string[] = ['<your token-invalid code set>'];

  private static handleTokenInvalidIfNeeded(bizCode: string, httpStatus: number): void {
    const invalid: boolean = HttpClient.TOKEN_INVALID_CODES.includes(bizCode) || httpStatus === 401;
    if (!invalid) {
      return;
    }
    const currentToken: string = HttpClient.readTokenFromSingleSource();
    if (currentToken.length === 0) {
      return; // 重入守卫
    }
    // 仅在该失效语义"应清"时清（已绑定 token 过期 → 清；匿名态被拒 → 不清，见防御 4）
    HttpClient.clearTokenInSingleSource();
    // + 广播登录态 / 按需跳登录（防重入）—— 按项目实现
  }

  // 占位：接你项目状态层（单一事实源）；勿用 V1 AppStorage 镜像 V2 对象（见 pitfalls B7）
  private static readTokenFromSingleSource(): string { return ''; }
  private static clearTokenInSingleSource(): void { /* 接你项目状态层 */ }

  // ... 其他 HttpClient 实现（buildUrl / mergeHeaders / execute / resolveDefaultBaseUrl 等略）
}

/**
 * HttpLogInterceptor 模板 —— hilog 输出格式（Phase 6 双端对账靠它）
 *
 * 关键：HMOS 侧 hdc 无法脚本化挂代理，hilog 是 HMOS 端唯一可自动抓的通道。
 * hilog 只打你 log 的内容 —— 因此请求日志行**必须带签名头摘要（ss / tt / token）**，
 * 否则 Phase 6 没法对账签名头。日志前缀固定 `HTTP >>>` / `HTTP <<<`，便于 grep。
 */
export class HttpLogInterceptor implements HttpInterceptor {
  private static readonly DOMAIN = 0x0002;
  private static readonly TAG = 'HttpClient';

  onRequest(req: HttpRequest): HttpRequest {
    // isDebug 守卫：AppStorage('isDebug') 为 false 时应静默。
    // 日志须带你项目的签名/鉴权头摘要（双端对账靠它）；头名按你项目替换下面占位。
    const h = req.headers;
    hilog.info(HttpLogInterceptor.DOMAIN, HttpLogInterceptor.TAG,
      'HTTP >>> %{public}s sign=%{public}s token=%{public}s body=%{public}s',
      req.url, h['<signHeader>'] ?? '', h['token'] ?? '', req.body ?? '');
    return req;
  }

  onResponse(url: string, code: number, body: string): string {
    hilog.info(HttpLogInterceptor.DOMAIN, HttpLogInterceptor.TAG,
      'HTTP <<< %{public}s code=%{public}d resp=%{public}s', url, code, body);
    return body;
  }
}
