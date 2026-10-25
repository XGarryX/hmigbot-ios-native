/**
 * http-capture-proxy.js — 极简 HTTP 转发代理，抓 Android / HMOS App 的明文请求
 *
 * 用途：后端是明文 HTTP（http://）时，无需 Charles / mitmproxy / CA 证书，
 *       用本脚本即可抓到 App 发出的【完整 headers + body】+ 响应，用于：
 *         - 对账签名头（ss / tt / ee）、公参头
 *         - 对账 request body 是否与 Android 逐字节一致
 *         - 对账启动期请求时序（看请求发出顺序 / 间隔）
 *
 * 用法：
 *   node http-capture-proxy.js [port] [hostFilter]
 *     port        监听端口，默认 8888
 *     hostFilter  只打印 URL 含该子串的请求（如自有后端域名），省略则打印全部
 *
 *   # Android 模拟器指向宿主代理（10.0.2.2 = 模拟器看到的宿主 IP）：
 *   adb shell settings put global http_proxy 10.0.2.2:8888
 *   # HMOS 设备：设置 → WiFi → 当前网络 → 代理 → 手动 → 填 宿主IP:8888
 *   # 抓完务必还原（否则其它 App 也走代理）：
 *   adb shell settings put global http_proxy :0
 *
 * 限制：仅支持明文 HTTP（http://）。HTTPS 需要 CONNECT 隧道 + CA 解密，本脚本不处理 ——
 *       那种情况用 capture-android-traffic.md 方法 C 的 Charles / mitmproxy。
 */
const http = require('http');

const PORT = parseInt(process.argv[2] || '8888', 10);
const HOST_FILTER = process.argv[3] || '';

const server = http.createServer((creq, cres) => {
  const chunks = [];
  creq.on('data', (c) => chunks.push(c));
  creq.on('end', () => {
    const body = Buffer.concat(chunks);
    const url = creq.url; // HTTP 代理请求里 url 是绝对地址 http://host/path
    const interesting = HOST_FILTER === '' || url.indexOf(HOST_FILTER) !== -1;

    if (interesting) {
      console.log('\n>>> ' + creq.method + ' ' + url);
      console.log('    HEADERS ' + JSON.stringify(creq.headers));
      if (body.length > 0) {
        console.log('    BODY ' + body.toString('utf8').slice(0, 4000));
      }
    }

    let u;
    try {
      u = new URL(url);
    } catch (e) {
      cres.writeHead(400);
      cres.end('proxy: bad url');
      return;
    }

    const preq = http.request(
      {
        hostname: u.hostname,
        port: u.port || 80,
        path: u.pathname + u.search,
        method: creq.method,
        headers: creq.headers,
      },
      (pres) => {
        const rchunks = [];
        pres.on('data', (d) => rchunks.push(d));
        pres.on('end', () => {
          const rbody = Buffer.concat(rchunks);
          if (interesting) {
            console.log('<<< ' + pres.statusCode + ' ' + url + '  ' +
              rbody.toString('utf8').slice(0, 2000));
          }
          cres.writeHead(pres.statusCode, pres.headers);
          cres.end(rbody);
        });
      }
    );
    preq.on('error', (e) => {
      console.log('PROXY ERR ' + e.message + '  for ' + url);
      cres.writeHead(502);
      cres.end('proxy error');
    });
    if (body.length > 0) preq.write(body);
    preq.end();
  });
});

// CONNECT（HTTPS 隧道）不在本脚本范围 —— 直接拒绝，避免连接挂死
server.on('connect', (req, sock) => {
  try { sock.write('HTTP/1.1 405 Method Not Allowed\r\n\r\n'); sock.destroy(); } catch (e) { /* ignore */ }
});
server.on('clientError', (err, sock) => {
  try { sock.destroy(); } catch (e) { /* ignore */ }
});
server.listen(PORT, '0.0.0.0', () => {
  console.log('http-capture-proxy listening on 0.0.0.0:' + PORT +
    (HOST_FILTER ? '  (filter: ' + HOST_FILTER + ')' : '  (logging all hosts)'));
});
