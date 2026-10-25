"""Original cold-start criteria, using verified HDC responses and host grep."""
import argparse
import math
import re
import secrets
import shlex
import shutil
import subprocess
import time


class ProbeResult(Exception):
    def __init__(self, code, reason):
        self.code, self.reason = code, reason


def remote(hdc, args):
    nonce = secrets.token_hex(16)
    marker = 'HMIGBOT_REMOTE_' + nonce + '_RC='
    # ps can echo its shell argv. Keep the complete marker out of that argv.
    command = (shlex.join(args) + '\nhmigbot_probe_rc=$?\nprintf "\\n%s%s_RC=%s\\n" '
               + shlex.quote('HMIGBOT_REMOTE_' + nonce[:16]) + ' '
               + shlex.quote(nonce[16:]) + ' "$hmigbot_probe_rc"')
    try:
        result = subprocess.run([hdc, 'shell', command], capture_output=True,
                                text=True, errors='replace', timeout=25)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProbeResult(3, 'HDC 不可观测: ' + str(exc)) from exc
    if result.returncode != 0:
        raise ProbeResult(3, 'HDC 传输失败: ' + result.stdout + result.stderr)
    lines = result.stdout.splitlines(keepends=True)
    matches = [(i, re.fullmatch(re.escape(marker) + r'([0-9]+)', line.strip()))
               for i, line in enumerate(lines) if marker in line]
    if len(matches) != 1 or not matches[0][1]:
        raise ProbeResult(3, 'HDC 远端状态标记缺失或不唯一')
    index, match = matches[0]
    return int(match.group(1)), ''.join(lines[:index] + lines[index + 1:]) + result.stderr


def start_result(rc, output):
    # OpenHarmony official aa-tool.md, start return values / error codes (85-103):
    # https://raw.githubusercontent.com/openharmony/docs/master/zh-cn/application-dev/tools/aa-tool.md
    codes = re.findall(r'Error\s+Code\s*:\s*(\d+)', output, re.I)
    success = any(line.strip() == 'start ability successfully.' for line in output.splitlines())
    if codes and set(codes) == {'10106102'} and not success:
        raise ProbeResult(3, '锁屏 10106102，记 unverified-cold-start 粘性债\n' + output.rstrip())
    if rc != 0 or codes or re.search(r'\berror\b', output, re.I) or not success:
        raise ProbeResult(1, '拉起失败或 aa 输出无法确认成功\n' + output.rstrip())


def process_alive(output, bundle):
    lines = [line.split() for line in output.splitlines() if line.strip()]
    if not lines or lines[0][-1] not in ('CMD', 'COMMAND', 'NAME', 'ARGS') or 'PID' not in lines[0]:
        raise ProbeResult(3, 'ps 输出为空或缺少可识别表头')
    column = len(lines[0]) - 1
    pid_column = lines[0].index('PID')
    return any(len(row) > column and row[pid_column].isdecimal() and row[column] == bundle
               for row in lines[1:])


def grep(args, output):
    # Preserve the original POSIX grep patterns, flags, count and case semantics.
    result = subprocess.run(['grep', *args], input=output, capture_output=True, text=True)
    if result.returncode not in (0, 1):
        raise ProbeResult(1, '主机 grep 判据执行失败: ' + result.stderr)
    return result.returncode, result.stdout


def crash_detected(output, bundle):
    # Framework setters such as SetAppRecoveryFlag are not recovery events:
    # ability_ability_runtime/services/abilitymgr/src/ability_record.cpp.
    recovery = r'(^|[^[:alnum:]_])AppRecovery([^[:alnum:]_]|$)'
    if grep(['-qE', 'cppcrash|jscrash|' + recovery], output)[0] == 0:
        return True
    # Official docs/master/zh-cn/application-dev/dfx/hilog.md:35-47:
    # date time PID TID severity domain/tag. Only proven D/I lines are excluded;
    # warnings, errors, fatal and unknown layouts retain the original failure.
    _, candidates = grep(['-E', 'Fault.*' + bundle], output)
    for line in candidates.splitlines():
        level = re.match(r'^\s*\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+\d+\s+\d+\s+([DIWEF])\s+\S', line)
        if level is None or level.group(1) not in ('D', 'I'):
            return True
    return False


def run(bundle, ability, wait):
    hdc = shutil.which('hdc')
    if not hdc:
        raise ProbeResult(3, 'hdc 不可用（记 unverified-cold-start 粘性债）')
    try:
        targets = subprocess.run([hdc, 'list', 'targets'], capture_output=True,
                                 text=True, errors='replace', timeout=25)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProbeResult(3, '设备列表不可用: ' + str(exc)) from exc
    if targets.returncode or not any(line.strip() and not line.startswith('[Empty')
                                    for line in targets.stdout.splitlines()):
        raise ProbeResult(3, '无在线设备（记 unverified-cold-start 粘性债）')
    remote(hdc, ['aa', 'force-stop', bundle])  # original best-effort stop
    time.sleep(1)
    rc, _ = remote(hdc, ['hilog', '-r'])
    if rc:
        raise ProbeResult(3, '无法清空冷启观测窗口')
    rc, output = remote(hdc, ['aa', 'start', '-b', bundle, '-a', ability])
    start_result(rc, output)
    time.sleep(wait)
    rc, logs = remote(hdc, ['hilog', '-x'])
    if rc:
        raise ProbeResult(3, '无法获取 crash 日志')
    if crash_detected(logs, bundle):
        raise ProbeResult(1, '冷启窗口内 crash')
    rc, processes = remote(hdc, ['ps', '-ef'])
    if rc:
        raise ProbeResult(3, '无法获取进程列表')
    if not process_alive(processes, bundle):
        raise ProbeResult(1, '进程已死')
    rc, logs = remote(hdc, ['hilog', '-x'])
    if rc:
        raise ProbeResult(3, '无法获取网络日志')
    net = grep(['-icE', 'rcp|httpclient|netstack|OH_Http|request.*(GET|POST)'], logs)[1].strip()
    rc, _ = remote(hdc, ['uitest', 'dumpLayout', '-p', '/data/local/tmp/csp.json'])
    toast = '0'
    if rc == 0:
        rc, layout = remote(hdc, ['cat', '/data/local/tmp/csp.json'])
        if rc == 0:
            code, count = grep(['-ocE', '未配置|尚未就绪|暂不可用|unavailable|not ready'], layout)
            toast = (count + ('0\n' if code else '')).rstrip('\n')
    print('冷启存活 ✓ | 网络栈日志条数=' + net + ' | 未配置类文案=' + toast)
    if int(net or '0') == 0:
        raise ProbeResult(1, '冷启 ' + str(wait) + 's 内零网络请求出网——网络基座疑似未装配（NetworkRuntimeState 事故形态）')
    print('PASS')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle')
    parser.add_argument('ability', nargs='?', default='EntryAbility')
    parser.add_argument('wait', nargs='?', type=float, default=8)
    args = parser.parse_args()
    if not math.isfinite(args.wait) or args.wait < 0:
        parser.error('wait must be a finite nonnegative number')
    try:
        run(args.bundle, args.ability, args.wait)
    except ProbeResult as exc:
        print(('SKIP: ' if exc.code == 3 else 'FAIL: ') + exc.reason)
        return exc.code
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
