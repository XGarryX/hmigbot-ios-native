"""Optional Xcode MCP choice and observation, never a source gate.

This module orchestrates the installed Xcode commands. It does not grant broad
agent/folder permissions, open UI, call project tools or reinterpret iOS facts.
"""
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import time
from pathlib import Path

from .core import MigrationError, read_json, write_json

CHOICES = {'ask', 'enable', 'skip'}


def resolve_choice(project, requested=None, *, configured_server=False):
    """Reuse a project's explicit choice; inspection is not consent."""
    if requested is not None and (not isinstance(requested, str) or requested not in CHOICES):
        raise MigrationError('MCP choice must be ask, enable or skip')
    if requested in {'enable', 'skip'}:
        return requested, 'explicit_request'
    path = Path(project) / 'spec/reports/init-environment.json'
    if path.is_file():
        try:
            previous = read_json(path).get('capabilities', {}).get('xcode_mcp', {})
            if previous.get('choice') in {'enable', 'skip'}:
                return previous['choice'], 'saved_project_choice'
        except (MigrationError, OSError, ValueError, TypeError, AttributeError):
            return 'ask', 'saved_choice_unreadable'
    analysis = Path(project) / 'spec/reports/derived/source-analysis.json'
    if analysis.is_file():
        try:
            cards = read_json(analysis).get('capability_choices', [])
            selected = [c for c in cards if isinstance(c, dict) and c.get('id') == 'xcode_mcp'
                        and c.get('state') == 'selected' and c.get('selected') in {'enable', 'skip'}]
            if len(selected) == 1:
                return selected[0]['selected'], 'saved_analysis_choice'
        except (MigrationError, OSError, ValueError, TypeError, AttributeError):
            return 'ask', 'saved_choice_unreadable'
    if configured_server and requested is None:
        return 'enable', 'explicit_server_config'
    return 'ask', 'not_yet_selected'


def choice_card(preparation, *, applicable=True):
    """Host-visible alternatives; a pending choice limits MCP only."""
    choice = preparation.get('choice', 'ask')
    pending = applicable and choice == 'ask'
    host = preparation.get('host_status', {})
    return {'id': 'xcode_mcp', 'title': '选择 Xcode MCP 或 Apple CLI',
            'state': 'pending' if pending else 'selected' if applicable else 'not_applicable',
            'selected': None if choice == 'ask' else choice,
            'choice_origin': preparation.get('choice_origin', 'explicit_request'),
            'requires_user_choice': pending, 'blocks_independent_cli': False,
            'blocks_mcp_calls': choice != 'enable',
            'options': [
                {'id': 'enable', 'label': '使用只读 MCP + Apple CLI',
                 'difference': '增加 Xcode 实际提供的工程和官方文档上下文；仍使用 CLI 采集编译证据。',
                 'permissions': '需要服务可见、目标工程已打开及对应 agent/目录授权；本客户端仅调用只读白名单。'},
                {'id': 'skip', 'label': '仅使用 Apple CLI',
                 'difference': '继续 xcodebuild、xcrun、Swift/Clang 分析，不取得 MCP 上下文；缺失项如实记录。',
                 'permissions': '不申请 MCP 权限；实际构建及输出目录仍沿用本次任务授权。'}],
            'observation': {'scope': 'current_process', 'status': host.get('status', 'not_probed'),
                            'enabled': host.get('enabled'), 'running': host.get('running')},
            'host_instruction': '有已有明确选择就沿用；否则向开发者展示两项并收取选择，不能把 options JSON 当作已询问。',
            'visibility_note': '当前进程看不到 MCP 不等于宿主未开启；先比较宿主状态，再定位工程上下文或 agent 授权。'}


def render_choice(card):
    """Readable stderr companion to the machine-readable choice card."""
    if card.get('id')!='xcode_mcp':
        return ''
    if card.get('state') == 'not_applicable':
        return ''
    if card.get('requires_user_choice'):
        lines = ['【需要开发者选择：Xcode MCP】']
        for number, item in enumerate(card['options'], 1):
            lines.append(f"{number}. {item['label']}：{item['difference']} {item['permissions']}")
        lines.append('请由主控收取选择；未选择仅暂缓 MCP 调用，独立 CLI 分析可继续，不视为已选择 CLI。')
    else:
        lines = ['【Xcode MCP 选择】' + ('沿用只读 MCP + Apple CLI' if card.get('selected') == 'enable' else '沿用仅 Apple CLI')]
    observed = card.get('observation', {})
    if observed.get('enabled') is True:
        lines.append('当前进程观测到服务开关已开启；是否存在目标工程上下文及 agent 授权仍需分别核验。')
    elif observed.get('enabled') is False:
        lines.append('当前进程观测为 disabled，尚不能据此认定宿主关闭；不要重复要求开发者开启。')
    lines.append(card['visibility_note'])
    return '\n'.join(lines)


def _run(argv, *, timeout=15):
    started = time.monotonic()
    record = {'argv': list(argv), 'exit_code': None}
    try:
        process = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, shell=False)
        record.update(exit_code=process.returncode, stdout=process.stdout, stderr=process.stderr)
    except subprocess.TimeoutExpired as exc:
        def decoded(value):
            return value if isinstance(value, str) else (value or b'').decode('utf-8', errors='replace')
        record.update(error='timeout', stdout=decoded(exc.stdout), stderr=decoded(exc.stderr))
    except OSError as exc:
        record.update(error=str(exc), stdout='', stderr=str(exc))
    record['duration_seconds'] = round(time.monotonic() - started, 3)
    return record


def status():
    """Report what this process can observe; sandbox visibility is not host truth."""
    if platform.system() != 'Darwin' or not shutil.which('xcrun'):
        return {'status': 'not_applicable', 'reason': 'Xcode MCP requires the installed macOS Xcode CLI',
                'blocking': False, 'cli_fallback': True, 'commands': []}
    command = _run(['xcrun', 'mcp-server', 'status', '--format', 'json'])
    result = {'status': 'unavailable', 'blocking': False, 'cli_fallback': True,
              'commands': [command], 'visibility': 'current_process', 'connected': False,
              'tool_calls_performed': False, 'observed_at': time.time(),
              'host_enabled': None, 'scope': 'current process observation; never an authorization verdict for another connection'}
    try:
        if command['exit_code'] != 0:
            raise ValueError(command.get('stderr') or command.get('error') or 'status command failed')
        value = json.loads(command['stdout'])
        permission = value['permission']
        if not isinstance(permission.get('enabled'), bool) or not isinstance(value.get('running'), bool):
            raise ValueError('Xcode MCP status omitted configuration/process state')
        result.update(status='enabled' if permission['enabled'] else 'disabled',
                      enabled=permission['enabled'], running=value['running'],
                      unsafe_always_allow_all_agents=permission.get('unsafeAlwaysAllowAllAgents'),
                      observed=value)
        if not permission['enabled']:
            result['visibility_note'] = ('If MCP was already enabled in a host terminal, compare status in that '
                                         'same host context. A restricted process may see different permission '
                                         'state; do not repeatedly ask the developer to enable it.')
    except (ValueError, TypeError, KeyError) as exc:
        result['error'] = str(exc)
    return result


def running_instances():
    """Discover actual Xcode processes without launching Xcode or reading its UI."""
    if platform.system() != 'Darwin':
        return {'status': 'not_applicable', 'instances': [], 'commands': []}
    command = _run(['/bin/ps', '-axo', 'pid=,comm='])
    instances = []
    if command['exit_code'] == 0:
        for line in command['stdout'].splitlines():
            pid, separator, executable = line.strip().partition(' ')
            executable = executable.strip()
            if separator and pid.isdecimal() and executable.endswith('.app/Contents/MacOS/Xcode'):
                instances.append({'pid': int(pid), 'executable': executable})
    # Store only Xcode candidates, not the other processes' command lines.
    safe_command = {**command, 'stdout': '\n'.join(str(v['pid']) + ' ' + v['executable'] for v in instances)}
    return {'status': 'observed' if command['exit_code'] == 0 else 'unavailable',
            'instances': instances, 'commands': [safe_command]}


def prepare(*, choice='ask', apply=False, output=None):
    """Explain/record the choice; system settings are changed by the developer.

    Apple's agent/folder trust is broader than a tool-name allowlist. This
    client enforces read-only calls; it does not claim the server is globally
    read-only or silently approve pending agents/folders.
    """
    if choice not in CHOICES:
        raise MigrationError('MCP choice must be ask, enable or skip')
    result = {'choice': choice, 'blocking': False, 'cli_fallback': True,
              'client_read_only': True, 'server_read_only_enforced': False,
              'permission_scope': 'No automatic agent/folder approvals; no all-agent setting',
              'benefits': ['Xcode project context and available native build-setting/compiler-flag queries',
                           'Applicable official documentation tools when actually advertised by the server'],
              'tradeoffs': ['Requires Xcode MCP access and possibly separate agent/project authorization',
                           'Only this client read allowlist is enforced; server trust is not a global read-only switch'],
              'options': {'enable': 'Explicitly choose --mcp enable with --prepare, or enable in Xcode settings',
                          'skip': 'Choose --mcp skip and continue xcodebuild/xcrun/Swift/Clang CLI evidence'},
              'manual_enable_command': 'sudo xcrun mcp-server enable',
              'manual_settings_path': 'Xcode > Settings > Intelligence > Model Context Protocol',
              'commands': [], 'product_verified': False}
    if choice == 'skip':
        result.update(status='declined', reason='Developer selected CLI evidence; no MCP command was run')
    else:
        current = status()
        result.update(host_status=current, commands=list(current['commands']))
        if current['status'] == 'not_applicable':
            result.update(status='not_applicable', reason=current['reason'])
        elif current.get('enabled'):
            result.update(status='enabled', enable_attempted=False,
                          next=('Choose MCP use for this project or continue CLI' if choice == 'ask' else
                                'Discover actual tools; request only the already authorized read operations'))
        elif choice == 'ask':
            result.update(status='choice_available', enable_attempted=False,
                          next='Explain both choices and retain CLI operation until the developer chooses')
        elif not apply:
            result.update(status='enable_requested', enable_attempted=False,
                          next='Apply the explicit choice with --prepare; this inspection did not change settings')
        else:
            result.update(status='needs_host_verification', enable_attempted=False,
                          next='Compare the host status first. If actually disabled, the developer may enable it in Xcode settings or a host terminal; this tool does not change system authorization settings')
    current = result.get('host_status', {})
    result['tool_access'] = {
        'capability_available': False if current.get('status') == 'not_applicable' else None,
        'authorized': None, 'actually_invoked': False, 'result': 'not_run',
        'scope': 'Project/document tool access; a service switch or status command is not a tool invocation'}
    result['system_settings_changed'] = False
    result['choice_card'] = choice_card(result, applicable=current.get('status') != 'not_applicable')
    if output is not None:
        write_json(Path(output), result)
    return result
