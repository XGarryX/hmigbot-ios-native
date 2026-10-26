"""Optional Xcode MCP preparation through Apple's CLI, never a source gate.

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

from .core import MigrationError, write_json

CHOICES = {'ask', 'enable', 'skip'}


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
              'tool_calls_performed': False}
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
    """Explain choices first; only an explicit enable+apply may change the switch.

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
            command = _run(['sudo', '-n', 'xcrun', 'mcp-server', 'enable', '--format', 'json'], timeout=30)
            result['commands'].append(command)
            result['enable_attempted'] = True
            if command['exit_code'] == 0:
                checked = status()
                result['commands'].extend(checked['commands'])
                result.update(host_status=checked, status='enabled' if checked.get('enabled') else 'needs_host_verification')
            else:
                result.update(status='needs_administrator' if 'password' in command.get('stderr', '').lower()
                              else 'enable_failed', error=command.get('stderr') or command.get('error'),
                              next='Run the manual command in a host terminal or choose CLI; do not share the administrator password')
    current = result.get('host_status', {})
    result['tool_access'] = {
        'capability_available': False if current.get('status') == 'not_applicable' else None,
        'authorized': None, 'actually_invoked': False, 'result': 'not_run',
        'scope': 'Project/document tool access; a service switch or status command is not a tool invocation'}
    if output is not None:
        write_json(Path(output), result)
    return result
