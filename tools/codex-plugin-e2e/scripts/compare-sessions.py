#!/usr/bin/env python3
"""本地转录 vs 远端导出 —— 逐字节对比(基本集成用例的验证环节)。

    python compare-sessions.py <工程目录> --from-downloads      # 首选:取浏览器刚下载的包
    python compare-sessions.py <工程目录> --tar <下载的 .tar.gz>
    python compare-sessions.py <工程目录> --from-dashboard      # 无人值守:用 .env 里的账号登录下载
    python compare-sessions.py <工程目录> --local-server        # 本地 migbot-server 直接导出

**首选路径:让用户自己在浏览器里登录看板**,然后在那个已登录的浏览器里点
「迁移事件流」→「下载本次会话数据」,包落到浏览器下载目录,再用 `--from-downloads`
接上。这样不需要密码,也不受图形验证码影响。

无人值守时才用 `--from-dashboard`,账号写在**本 skill 目录下的 `.env`**(已 gitignore,照 `.env.example` 建):

    A2H_DASHBOARD_URL=https://<看板地址>:8443
    A2H_DASHBOARD_USER=<用户名>
    A2H_DASHBOARD_PASSWORD=<密码>

没有账号 → 停下来向 migbot-server 管理员申请,不要用本地替身绕过。
密码只留在 .env 里:不写进文档、issue、报告,也不要贴进对话。

工程目录 = 跑迁移的那个目录(HarmonyOS 工程根,含 .migbot/)。

判定口径(用户裁定,2026-08-30):**导出包里每个会话文件必须与客户端本地转录逐字节
相同**;"看板上看得到"不算通过。

退出码 0 = 全部一致;非 0 = 有不一致,按提示写 issue。
"""
import argparse, glob, hashlib, http.cookiejar, json, os, subprocess, sys, tarfile, tempfile
import time
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("--tar", help="从看板下载的导出包")
ap.add_argument("--from-downloads", nargs="?", const="~/Downloads", metavar="DIR",
                help="取该目录下最新的 .tar.gz(默认 ~/Downloads)——浏览器刚下载的那个")
ap.add_argument("--from-dashboard", action="store_true",
                help="读 skill 目录下的 .env,登录看板并下载本轮导出包")
ap.add_argument("--env", help=".env 路径(默认:脚本同级目录的 .env)")
ap.add_argument("--local-server", action="store_true",
                help="调本地 migbot-server 的 export_run_stages 直接产包")
ap.add_argument("--server-repo", default=os.path.expanduser("~/Workspace/migbot_set/migbot-server"))
ap.add_argument("--run", help="run_id,默认取 .migbot/config.json")
a = ap.parse_args()

proj = os.path.abspath(a.project)
cfg = json.load(open(f"{proj}/.migbot/config.json"))
run = a.run or cfg["run_id"]
msid = cfg.get("hmigbot_session_id") or cfg.get("migbot_session_id")
print(f"project={proj}\nrun_id={run}\nmsid={msid}\n")

# ── 0. 先把客户端队列排空,否则尾部字节还没上传,对比必然不等 ──────────────
bin_ = f"{proj}/.migbot/bin/a2h"
if os.path.exists(bin_):
    r = subprocess.run([bin_, "flush", "--drain"], cwd=proj, capture_output=True, text=True)
    print("flush:", (r.stdout + r.stderr).strip().splitlines()[-1:] or "(no output)")
    st = subprocess.run([bin_, "status", "--json"], cwd=proj, capture_output=True, text=True).stdout
    try:
        ob = json.loads(st).get("outbox") or {}
        print(f"outbox: pending={ob.get('pending')} dead={ob.get('dead')}")
        if ob.get("pending") or ob.get("dead"):
            print("  ⚠ 队列没清空 —— 先查网络/端点,再对比;dead>0 本身就是要报的 bug")
    except Exception:
        print("status --json 解析失败:", st[:200])

# ── 1. 本地转录清单:水位线文件记录了每个会话的真实转录路径 ────────────────
wm = sorted(glob.glob(f"{proj}/.migbot/metrics/{run}/session-watermarks/*.enqueue-state.json"))
if not wm:
    sys.exit(f"FAIL 本地没有任何会话水位线({proj}/.migbot/metrics/{run}/session-watermarks/)\n"
             f"     → 会话根本没被采集,这是 bug,按 issue 模板报『会话零上传』")
local = {}
for p in wm:
    d = json.load(open(p))
    local[d["session_id"]] = d
print(f"\n本地会话 {len(local)} 个")

# ── 2. 远端导出包 ────────────────────────────────────────────────────────
def _load_env(path):
    """.env → dict;只认 KEY=VALUE,忽略注释与空行。"""
    out = {}
    if not os.path.exists(path):
        sys.exit(f"FAIL 没有 {path}\n"
                 f"     → 看板账号写在这里(照同目录 .env.example 建)。\n"
                 f"     → 还没有账号?停在这一步,向 migbot-server 管理员申请看板账号密码,\n"
                 f"       不要改用 --local-server 绕过 —— 客户拿不到自己的数据本身就是问题。")
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def fetch_from_dashboard(run_id, msid, envfile):
    e = _load_env(envfile)
    base = (e.get("A2H_DASHBOARD_URL") or "").rstrip("/")
    user, pw = e.get("A2H_DASHBOARD_USER"), e.get("A2H_DASHBOARD_PASSWORD")
    missing = [k for k, v in [("A2H_DASHBOARD_URL", base), ("A2H_DASHBOARD_USER", user),
                              ("A2H_DASHBOARD_PASSWORD", pw)] if not v]
    if missing:
        sys.exit(f"FAIL {envfile} 缺 {', '.join(missing)} —— 向管理员要看板账号后补上")
    op = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
        urllib.request.ProxyHandler({}))          # 系统代理会掐内网/本地连接

    def post(path, body):
        req = urllib.request.Request(base + path, data=json.dumps(body).encode(),
                                     method="POST",
                                     headers={"content-type": "application/json"})
        return op.open(req, timeout=180)

    print(f"登录 {base} as {user}")
    try:
        post("/api/v1/auth/login", {"username": user, "password": pw}).read()
    except urllib.error.HTTPError as ex:
        body = ex.read().decode()[:300]
        if "captcha" in body:
            sys.exit("FAIL 看板开着图形验证码,脚本登不进去。\n"
                     "     → 用浏览器登录看板,点该行的「会话数据下载」,再 --tar <下载的包> 跑一遍。")
        sys.exit(f"FAIL 登录失败 {ex.code} {body}\n"
                 f"     → 账号密码不对就找管理员;连续失败 5 次会锁 10 分钟。")
    try:
        r = post("/api/v1/agent-perf/export-stages",
                 {"run_id": run_id, "migbot_session_id": msid})
    except urllib.error.HTTPError as ex:
        sys.exit(f"FAIL 导出失败 {ex.code} {ex.read().decode()[:300]}\n"
                 f"     → 403 project_forbidden = 这个账号没有该项目的权限,找管理员加。")
    out = os.path.join(tempfile.mkdtemp(prefix="cmp-dl-"), f"export-{run_id[:8]}.tar.gz")
    with open(out, "wb") as f:
        f.write(r.read())
    print(f"已下载 {out} ({os.path.getsize(out)} B)")
    return out


if a.tar:
    tgz = a.tar
elif a.from_downloads:
    d = os.path.expanduser(a.from_downloads)
    cands = sorted(glob.glob(f"{d}/*.tar.gz"), key=os.path.getmtime, reverse=True)
    if not cands:
        sys.exit(f"FAIL {d} 下没有 .tar.gz\n"
                 f"     → 在已登录的浏览器里打开该会话的「迁移事件流」,点「下载本次会话数据」,\n"
                 f"       等下载完成后重跑;换了下载目录就 --from-downloads <目录>。")
    tgz = cands[0]
    age = (time.time() - os.path.getmtime(tgz)) / 60
    print(f"取最新下载 {tgz}({age:.1f} 分钟前)")
    if age > 30:
        print("  ⚠ 这个包是 30 分钟前的,可能不是本轮 —— 确认一下,或用 --tar 指定")
elif a.from_dashboard:
    tgz = fetch_from_dashboard(run, msid,
                               a.env or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
elif a.local_server:
    sys.path.insert(0, f"{a.server_repo}/src")
    from services.parse_worker import run_once            # noqa: E402
    for _ in range(6):
        if not run_once():
            break
    from services.stage_export import export_run_stages   # noqa: E402
    tgz = export_run_stages(run, tempfile.mkdtemp(prefix="cmp-"))
else:
    sys.exit("选一种取远端数据的方式:--from-downloads(浏览器刚下载的包,首选) / "
             "--tar <包路径> / --from-dashboard(.env 账号,无人值守) / "
             "--local-server(本地服务端形态)")
print(f"远端导出包 {tgz}")

out = tempfile.mkdtemp(prefix="cmp-x-")
with tarfile.open(tgz) as t:
    t.extractall(out)
# 包是不是本轮的?先按 manifest 核对 run_id,避免拿错包后误报「远端缺失」
mans = glob.glob(f"{out}/**/manifest.json", recursive=True)
runs_in_pkg = set()
for m in mans:
    try:
        d = json.load(open(m))
    except Exception:
        continue
    for r in (d.get("runs") or []):
        if isinstance(r, dict) and r.get("run_id"):
            runs_in_pkg.add(r["run_id"])
    if d.get("run_id"):
        runs_in_pkg.add(d["run_id"])
if runs_in_pkg and run not in runs_in_pkg:
    sys.exit(f"FAIL 这个包不是本轮的 —— 包里是 run {sorted(runs_in_pkg)},本轮是 {run}\n"
             f"     包:{tgz}\n"
             f"     → 在已登录的浏览器里打开**本轮那一行**的「迁移事件流」再点下载,"
             f"或用 --tar 指定正确的包。")

remote = {}
for p in glob.glob(f"{out}/**/sessions/*.jsonl", recursive=True):
    remote[os.path.basename(p)] = p
print(f"远端会话文件 {len(remote)} 个(run 核对通过)\n")

# ── 3. 逐字节对比 ────────────────────────────────────────────────────────
bad = []
for sid, d in sorted(local.items()):
    tp = d.get("transcript_path", "")
    hits = [v for k, v in remote.items() if sid in k]
    if not hits:
        bad.append((sid, "远端缺失", f"本地 {d.get('enqueued_bytes')}B 已入队,导出包里没有该会话"))
        print(f"FAIL {sid[:12]} 远端缺失")
        continue
    if not os.path.exists(tp):
        bad.append((sid, "本地转录不见了", tp))
        print(f"FAIL {sid[:12]} 本地转录不存在 {tp}")
        continue
    lb, rb = open(tp, "rb").read(), open(hits[0], "rb").read()
    if lb == rb:
        print(f"PASS {sid[:12]} {len(lb)}B {hashlib.md5(lb).hexdigest()[:8]} {d.get('kind')}")
        continue
    if lb.startswith(rb):
        why = f"远端只到 {len(rb)}B / 本地 {len(lb)}B —— 尾部未上传(前缀一致)"
    elif rb.startswith(lb):
        why = f"远端 {len(rb)}B 比本地 {len(lb)}B 长 —— 远端多出内容"
    else:
        off = next((i for i in range(min(len(lb), len(rb))) if lb[i] != rb[i]), 0)
        why = (f"第 {off} 字节起不同 local={lb[off:off+60]!r} remote={rb[off:off+60]!r}")
    bad.append((sid, "内容不一致", why))
    print(f"FAIL {sid[:12]} {why}")

print()
if bad:
    print(f"❌ {len(bad)}/{len(local)} 个会话不一致 —— 按 issue 模板逐条上报:")
    for sid, kind, why in bad:
        print(f"  · {sid} [{kind}] {why}")
    print(f"\n  证据请带上:run_id={run} msid={msid} 导出包={tgz}")
    sys.exit(1)
print(f"✅ {len(local)}/{len(local)} 个会话本地与远端逐字节一致")
