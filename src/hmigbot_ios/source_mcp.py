"""Bounded stdio MCP reads, immutable responses and explicit evidence limits."""
import json
import os
from pathlib import Path
import queue
import re
import signal
import subprocess
import threading
import time
import uuid

from .core import source_snapshot
from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot, write_json

VERSIONS = {'2025-11-25', '2025-06-18', '2025-03-26', '2024-11-05'}
READ_TOOLS = {
    'serena': {'find_symbol', 'find_referencing_symbols', 'get_symbols_overview', 'search_for_pattern', 'read_file'},
    'xcode': {'XcodeRead', 'XcodeGrep', 'XcodeGlob', 'XcodeLS', 'DocumentationSearch',
              'GetTargetBuildSettings', 'GetFileCompilerFlags', 'GetBuildLog',
              'XcodeListWorkspaces', 'XcodeListTargets', 'XcodeListSchemes',
              'XcodeListRunDestinations', 'XcodeListTestPlans'},
    'sourcekit': {'find_symbols', 'references', 'definition', 'implementations', 'hover', 'diagnostics',
                  'call_hierarchy', 'type_hierarchy', 'get_definition', 'get_references'},
}
INDEX = 'spec/ref/ios-mcp-index.json'
LIMIT = 8 * 1024 * 1024


def failure_kind(error):
    """Separate service visibility, authorization and unavailable tool evidence."""
    if isinstance(error, OSError):
        return 'process_visibility_or_transport_error'
    text = str(error).lower().replace('\\', '').replace('’', "'")
    if any(value in text for value in ('timed out', 'timeout', 'deadline exceeded')):
        return 'timeout'
    if 'access is disabled' in text or 'no xcode tool service' in text:
        return 'service_disabled_or_not_visible'
    if any(value in text for value in ('permission', 'approval', 'not approved', "isn't approved", 'not authorized', 'denied', 'not permitted')) or re.search(r'isn.?t.{0,30}approv', text):
        return 'authorization_required'
    if any(value in text for value in ('tabidentifier', 'window_context', 'project_context', 'workspace context')):
        return 'missing_project_or_window_context'
    if any(value in text for value in ('unavailable, ambiguous', 'outside the source read allowlist', 'method not found')):
        return 'tool_unavailable'
    return 'transport_or_tool_error'


def recovery_options(kind):
    """Actionable alternatives do not authorize additional capability use."""
    options = [{'id': 'continue_cli', 'action': 'Continue the selected xcodebuild/xcrun/Swift/Clang CLI evidence',
                'difference': 'Keeps conversion moving without MCP project/document context; missing native evidence remains explicit',
                'requires_choice': False}]
    if kind == 'authorization_required':
        options.append({'id': 'authorize_selected_context',
                        'action': 'Open the selected project manually in Xcode and approve only the intended agent and project access when prompted',
                        'difference': 'Enables the requested Xcode context; the service trust is per agent/folder, while this client still calls read tools only',
                        'requires_choice': True})
        options.append({'id': 'inspect_pending_request', 'command': ['xcrun', 'mcp-server', 'status', '--format', 'json'],
                        'action': 'Inspect official pending IDs before any scoped approval; never guess an ID from logs',
                        'difference': 'Read-only diagnosis. If no actual pending ID exists, no CLI approval can be inferred',
                        'requires_choice': False})
    elif kind == 'service_disabled_or_not_visible':
        options.append({'id': 'verify_host_visibility', 'command': ['xcrun', 'mcp-server', 'status', '--format', 'json'],
                        'action': 'Compare with the already authorized host terminal before changing settings again',
                        'difference': 'Distinguishes host disabled access from restricted-process visibility', 'requires_choice': False})
        options.append({'id': 'choose_optional_mcp', 'action': 'Use init-environment --mcp enable --prepare only after choosing MCP, or enable it manually in Xcode settings',
                        'difference': 'May need administrator and separate agent/project authorization; CLI remains available',
                        'requires_choice': True})
    elif kind == 'timeout':
        options.append({'id':'retry_selected_context','action':'Retain the selected instance/session and retry within bounded phase budgets; timeout is not a permission decision',
                        'difference':'Inspect timings.json and current visibility; independent CLI remains available','requires_choice':False})
    elif kind == 'missing_project_or_window_context':
        options.append({'id':'refresh_selected_context','action':'Rediscover the same instance schema and read-only window context; bind only one matching configured source',
                        'difference':'Do not open a project, guess a tab, or reuse another instance parameters','requires_choice':False})
    else:
        options.append({'id': 'use_available_read_tools', 'action': 'Inspect actual advertised schemas or connect to an already running Xcode instance',
                        'difference': 'A missing documentation tool does not imply build-setting or file-read tools are unavailable',
                        'requires_choice': False})
    return options


class MCPReadError(MigrationError):
    def __init__(self, message, diagnostic):
        super().__init__(message)
        self.diagnostic = diagnostic


class StdioClient:
    def __init__(self, config, cwd, logs):
        argv = config.get('command')
        if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or not a for a in argv):
            raise MigrationError('MCP command must be a nonempty argv array')
        timeout = config.get('timeout_seconds', 30)
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not 0 < timeout <= 60:
            raise MigrationError('MCP timeout must be between 0 and 60 seconds')
        budgets = config.get('timeouts', {})
        if not isinstance(budgets, dict) or set(budgets)-{'connect', 'discover', 'call', 'overall'}:
            raise MigrationError('Invalid MCP phase budgets')
        self.budgets = {name: budgets.get(name, timeout) for name in ('connect', 'discover', 'call')}
        self.budgets['overall'] = budgets.get('overall', max(180, timeout*3))
        if any(type(v) not in (int,float) or not 0<v<=1800 for v in self.budgets.values()):
            raise MigrationError('MCP budgets must be finite, positive and bounded by 1800 seconds')
        self.started = time.monotonic()
        self.deadline = self.started + self.budgets['overall']
        self.request_records = []
        self.initialized = None
        self.tools = None
        self.config = config
        self.events, self.transcript, self.stderr = queue.Queue(maxsize=256), [], bytearray()
        self.sequence = 0
        self.last_sent_id = None
        env = os.environ.copy()
        supplied_env = config.get('env', {})
        if (not isinstance(supplied_env, dict) or set(supplied_env) - {'MCP_XCODE_PID', 'MCP_XCODE_SESSION_ID'}
                or any(not isinstance(v, str) or not v for v in supplied_env.values())):
            raise MigrationError('MCP environment supports scoped Xcode PID/session strings only')
        env.update(supplied_env)
        self.process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, shell=False, env=env, start_new_session=True)
        self.logs = logs
        self.threads = [threading.Thread(target=self.pump, daemon=True), threading.Thread(target=self.pump_error, daemon=True)]
        for thread in self.threads:
            thread.start()

    def pump(self):
        total = 0
        try:
            while True:
                line = self.process.stdout.readline(LIMIT + 1)
                if not line:
                    self.events.put_nowait(MigrationError('MCP closed stdout')); return
                total += len(line)
                if total > LIMIT:
                    raise MigrationError('MCP response exceeded evidence limit')
                message = json.loads(line)
                if not isinstance(message, dict) or message.get('jsonrpc') != '2.0':
                    raise MigrationError('Invalid MCP JSON-RPC response')
                self.events.put_nowait(message)
        except Exception as exc:
            try:
                self.events.put_nowait(exc)
            except queue.Full:
                self.process.terminate()

    def pump_error(self):
        while len(self.stderr) < LIMIT:
            part = self.process.stderr.read(4096)
            if not part:
                break
            self.stderr.extend(part[:LIMIT - len(self.stderr)])

    def send(self, message):
        self.transcript.append({'direction': 'client', 'message': message})
        self.process.stdin.write((json.dumps(message, ensure_ascii=False) + '\n').encode('utf-8'))
        self.process.stdin.flush()

    def request(self, method, params):
        if time.monotonic() >= self.deadline:
            raise MigrationError('MCP operation overall deadline exceeded before request')
        self.sequence += 1
        ident = self.sequence
        started = time.monotonic()
        phase = 'connect' if method == 'initialize' else 'discover' if method == 'tools/list' else 'call'
        deadline = min(self.deadline, started + self.budgets[phase])
        self.send({'jsonrpc': '2.0', 'id': ident, 'method': method, 'params': params})
        self.last_sent_id = ident
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self.send({'jsonrpc':'2.0','method':'notifications/cancelled','params':{'requestId':ident,'reason':'deadline'}})
                self.request_records.append({'method':method,'phase':phase,'status':'timeout','elapsed_seconds':time.monotonic()-started})
                raise MigrationError('MCP query deadline exceeded')
            try:
                message = self.events.get(timeout=min(remaining, 5))
            except queue.Empty as exc:
                if time.monotonic() < deadline:
                    import sys
                    print('MCP '+method+' still waiting; elapsed '+str(round(time.monotonic()-started,1))+'s',file=sys.stderr)
                    continue
                self.send({'jsonrpc': '2.0', 'method': 'notifications/cancelled', 'params': {'requestId': ident, 'reason': 'deadline'}})
                self.request_records.append({'method':method,'phase':phase,'status':'timeout','elapsed_seconds':time.monotonic()-started})
                raise MigrationError('MCP query timed out') from exc
            if isinstance(message, Exception):
                raise MigrationError('MCP transport failed: ' + str(message))
            self.transcript.append({'direction': 'server', 'message': message})
            if 'method' in message:
                if 'id' in message:
                    self.send({'jsonrpc': '2.0', 'id': message['id'], 'error': {'code': -32601, 'message': 'Client capability unavailable'}})
                continue
            if message.get('id') is None and 'error' in message:
                raise MigrationError('MCP server unavailable: ' + str(message['error']))
            if message.get('id') != ident:
                raise MigrationError('MCP returned an unexpected response ID')
            if 'error' in message:
                raise MigrationError('MCP request error: ' + str(message['error']))
            if not isinstance(message.get('result'), dict):
                raise MigrationError('MCP response has no object result')
            self.request_records.append({'method':method,'phase':phase,'status':'returned','elapsed_seconds':time.monotonic()-started})
            return message['result']

    def prepare(self):
        if self.initialized is not None:
            return self.initialized, self.tools
        from . import __version__
        init = self.request('initialize', {'protocolVersion':'2025-11-25','capabilities':{},
                'clientInfo':{'name':'hmigbot-ios-source','version':__version__}})
        if init.get('protocolVersion') not in VERSIONS or not isinstance(init.get('serverInfo'),dict) or 'tools' not in init.get('capabilities',{}):
            raise MigrationError('MCP version or tool capability negotiation failed')
        self.send({'jsonrpc':'2.0','method':'notifications/initialized'})
        tools, cursor, seen = [], None, set()
        for _ in range(50):
            page=self.request('tools/list',{'cursor':cursor} if cursor else {})
            if page.get('isError') or not isinstance(page.get('tools'),list):
                raise MigrationError('MCP tools/list failed: '+str(page))
            tools.extend(page['tools']);cursor=page.get('nextCursor')
            if not cursor:break
            if not isinstance(cursor,str) or cursor in seen:raise MigrationError('MCP repeated pagination cursor')
            seen.add(cursor)
        else:raise MigrationError('MCP tool pagination limit exceeded')
        self.initialized,self.tools=init,tools
        return init,tools

    def close(self):
        try:
            self.process.stdin.close()
        except OSError:
            pass
        try:
            self.process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill(); self.process.wait(timeout=1)
        try:
            os.killpg(self.process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            os.killpg(self.process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        for thread in self.threads:
            thread.join(timeout=1)
        write_json(self.logs / 'transcript.json', self.transcript)
        write_json(self.logs / 'timings.json', {'budgets':self.budgets,'requests':self.request_records,
                                              'elapsed_seconds':time.monotonic()-self.started})
        (self.logs / 'stderr.log').write_bytes(self.stderr)
        self.process.stdout.close(); self.process.stderr.close()


def discover(config, source, output):
    """Actually negotiate the server and enumerate tools; never claim a query ran."""
    output.mkdir(parents=True, exist_ok=False)
    client = None
    try:
        client = StdioClient(config, source, output)
        init, tools = client.prepare()
        result = {'status': 'discovered', 'server': init['serverInfo'],
                  'protocol_version': init['protocolVersion'], 'tools': tools,
                  'tool_calls_performed': False,
                  'discovery_execution': {'capability_available': True, 'authorized': True,
                                          'actually_invoked': True, 'result': 'discovered',
                                          'scope': 'Protocol negotiation and tools/list only'},
                  'project_access': {'capability_available': any(tool.get('name') in READ_TOOLS.get(config.get('provider'), set()) for tool in tools),
                                     'authorized': None, 'actually_invoked': False, 'result': 'not_run'}}
        if config.get('provider') == 'xcode':
            try:
                from .xcode_context import bind_arguments
                matches=[t for t in tools if t.get('name')=='GetTargetBuildSettings' and t.get('annotations',{}).get('readOnlyHint') is not False]
                if len(matches)!=1:raise MigrationError('Requested read tool is unavailable, ambiguous')
                arguments,binding=bind_arguments(client,tools,matches[0],{},source)
                if any(k not in arguments for k in matches[0].get('inputSchema',{}).get('required',[])):
                    raise MigrationError('missing project_context: required schema inputs are not known')
                probe=client.request('tools/call',{'name':'GetTargetBuildSettings','arguments':arguments})
                if probe.get('isError'):raise MigrationError('MCP project tool returned isError: '+str(probe))
                if not probe.get('content') and not probe.get('structuredContent'):raise MigrationError('MCP project tool returned no evidence')
                result['project_access']={'authorized':True,'actually_invoked':True,'result':'captured','context':binding,'response':probe}
            except (MigrationError,OSError,ValueError,TypeError,KeyError) as exc:
                kind=failure_kind(exc)
                result['project_access']={'authorized':False if kind=='authorization_required' else None,
                    'actually_invoked':any(r['method']=='tools/call' for r in client.request_records),
                    'result':'unverified','failure_kind':kind,'error':str(exc)}
        write_json(output / 'discovery.json', result)
        return result
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result = {'status': 'unavailable', 'error': str(exc), 'failure_kind': failure_kind(exc),
                  'tool_calls_performed': False, 'blocking': False,
                  'recovery': 'Keep CLI evidence; compare host status before changing access, and resolve only the actual pending agent/project request'}
        result['options'] = recovery_options(result['failure_kind'])
        result['discovery_execution'] = {'capability_available': None,
                                        'authorized': False if result['failure_kind'] == 'authorization_required' else None,
                                        'actually_invoked': client is not None, 'result': 'unavailable',
                                        'scope': 'Protocol negotiation and tools/list only'}
        write_json(output / 'failure.json', result)
        return result
    finally:
        if client:
            client.close()


def capture(project, server_path, request_path, *, shared_client=None):
    from .native_pipeline import context
    from .ios_facts import validate_graph
    source, project = context(project)
    graph, _ = validate_graph(source, project)
    config, request = read_json(server_path), read_json(request_path)
    if shared_client is not None and any(shared_client.config.get(k) != config.get(k) for k in ('provider','command','env')):
        raise MigrationError('Shared MCP connection differs from the selected instance/session')
    provider, tool = config.get('provider'), request.get('tool')
    if provider not in READ_TOOLS or tool not in READ_TOOLS[provider]:
        raise MigrationError('MCP tool is outside the source read allowlist')
    if config.get('transport') != 'stdio':
        raise MigrationError('This adapter supports stdio only; remote Mac may use an explicitly configured SSH stdio bridge')
    if request.get('source_sha256') != graph['source_sha256'] or request.get('graph_sha256') != digest(json_bytes(graph)):
        raise MigrationError('MCP query must pin current source and fact graph')
    facts = {f['id']: f for f in graph['facts']}
    ids = request.get('fact_ids')
    if not isinstance(ids, list) or not ids or any(i not in facts for i in ids):
        raise MigrationError('MCP query needs real source fact IDs')
    arguments = request.get('arguments')
    if not isinstance(arguments, dict):
        raise MigrationError('MCP tool arguments must be an object')
    # Query provenance is tied to actual fact spans. Returned external locations
    # remain untrusted until reviewed; no automatic promotion to compiler_binding.
    ident = 'MCP-' + uuid.uuid4().hex
    output = project / 'spec/ref/mcp-runs' / ident
    output.mkdir(parents=True)
    client = None
    tool_called, tool_advertised = False, None
    try:
        client = shared_client or StdioClient(config, source, output)
        init, tools = client.prepare()
        matches = [v for v in tools if v.get('name') == tool]
        tool_advertised = len(matches) == 1
        if len(matches) != 1 or matches[0].get('annotations', {}).get('readOnlyHint') is False:
            raise MigrationError('Requested read tool is unavailable, ambiguous or advertised as mutating')
        from .xcode_context import bind_arguments
        arguments, context_binding = bind_arguments(client, tools, matches[0], arguments, source) if provider == 'xcode' else (arguments, None)
        schema = matches[0].get('inputSchema', {})
        if any(k not in arguments for k in schema.get('required', [])):
            raise MigrationError('MCP request omitted a required tool argument')
        previous_sent = client.last_sent_id
        try:
            response = client.request('tools/call', {'name': tool, 'arguments': arguments})
        finally:
            tool_called = client.last_sent_id != previous_sent
        if response.get('isError'):
            raise MigrationError('MCP tool returned isError: ' + str(response.get('content', response)))
        if not response.get('content') and not response.get('structuredContent'):
            raise MigrationError('MCP tool returned no evidence')
        if source_snapshot(source)['sha256'] != graph['source_sha256']:
            raise MigrationError('Source changed during MCP query; re-index and review')
        artifact = {'schema_version': 1, 'id': ident, 'status': 'captured', 'provider': provider,
                    'server': init['serverInfo'], 'protocol_version': init['protocolVersion'],
                    'source_sha256': graph['source_sha256'], 'graph_sha256': digest(json_bytes(graph)),
                    'fact_ids': ids, 'source_anchors': [facts[i]['anchor'] for i in ids],
                    'request': request, 'effective_arguments': arguments, 'context_binding': context_binding,
                    'tool_definition': matches[0], 'response': response,
                    'execution': {'capability_available': True, 'authorized': True, 'actually_invoked': True,
                                  'result': 'captured', 'scope': tool},
                    'resolution': 'tool_response', 'build_context': 'unverified', 'behavior_verified': False}
        write_json(output / 'artifact.json', artifact)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        diagnostic = {'id': ident, 'status': 'failed', 'provider': provider,
                      'source_sha256': graph['source_sha256'], 'error': str(exc),
                      'failure_kind': failure_kind(exc), 'behavior_verified': False,
                      'connection': {'provider':provider,'session_id':config.get('env',{}).get('MCP_XCODE_SESSION_ID'),
                                     'instance':config.get('env',{}).get('MCP_XCODE_PID','background')},
                      'timings':client.request_records if client else []}
        diagnostic['options'] = recovery_options(diagnostic['failure_kind'])
        diagnostic['execution'] = {'capability_available': tool_advertised,
                                   'authorized': False if diagnostic['failure_kind'] == 'authorization_required' else None,
                                   'actually_invoked': tool_called, 'result': 'failed', 'scope': tool}
        write_json(output / 'failure.json', diagnostic)
        raise MCPReadError('MCP capture failed; evidence: ' + str(output), diagnostic) from exc
    finally:
        if client and shared_client is None:
            client.close()
        elif client:
            write_json(output / 'transcript.json', client.transcript)
    path = project / INDEX
    index = read_json(path) if path.exists() else {'schema_version': 1, 'captures': []}
    index['captures'].append({'id': ident, 'path': (output / 'artifact.json').relative_to(project).as_posix(),
                              'sha256': digest((output / 'artifact.json').read_bytes()),
                              'transcript_sha256': digest((output / 'transcript.json').read_bytes())})
    write_json(path, index)
    return {'status': 'captured', 'id': ident, 'path': str(output), 'resolution': 'tool_response',
            'execution': {'capability_available': True, 'authorized': True, 'actually_invoked': True,
                          'result': 'captured', 'scope': tool}, 'behavior_verified': False}


def validate_captures(project, graph, requested_ids, claim_fact_ids=None):
    if not requested_ids:
        return
    index = read_json(project / INDEX)
    if not isinstance(requested_ids, list) or any(not isinstance(ident, str) or not ident for ident in requested_ids):
        raise MigrationError('Requested MCP evidence IDs must be nonempty strings')
    selected = set(requested_ids)
    captures = {}
    for item in index['captures']:
        ident = item.get('id') if isinstance(item, dict) else None
        if not isinstance(ident, str) or ident not in selected:
            continue  # Unreferenced history cannot invalidate a selected claim.
        if ident in captures:
            if any(captures[ident].get(key) != item.get(key) for key in ('path', 'sha256', 'transcript_sha256')):
                raise MigrationError('Conflicting selected MCP evidence ID: ' + ident)
            continue
        captures[ident] = item
    facts = {f['id']: f for f in graph['facts']}
    for ident in dict.fromkeys(requested_ids):
        if ident not in captures:
            raise MigrationError('Unknown MCP evidence ID: ' + str(ident))
        item = captures[ident]
        path = safe_child(project, item['path'])
        if not item['path'].startswith('spec/ref/mcp-runs/') or path.name != 'artifact.json':
            raise MigrationError('MCP evidence path outside capture store')
        if digest(path.read_bytes()) != item['sha256'] or digest((path.parent / 'transcript.json').read_bytes()) != item['transcript_sha256']:
            raise MigrationError('MCP evidence was edited')
        data = read_json(path)
        if data.get('id') != ident or data.get('status') != 'captured' or data.get('source_sha256') != graph['source_sha256'] or data.get('graph_sha256') != digest(json_bytes(graph)):
            raise MigrationError('MCP evidence is failed or stale')
        if claim_fact_ids is not None and not set(data['fact_ids']).intersection(claim_fact_ids):
            raise MigrationError('MCP evidence is unrelated to the linked claim facts')
        if data.get('source_anchors') != [facts[i]['anchor'] for i in data['fact_ids']]:
            raise MigrationError('MCP source anchor mismatch')
        if data.get('resolution') != 'tool_response' or data.get('behavior_verified') is not False:
            raise MigrationError('MCP evidence cannot promote itself to runtime or compiler proof')
