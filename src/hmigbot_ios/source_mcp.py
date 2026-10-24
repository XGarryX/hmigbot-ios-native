"""Bounded stdio MCP reads, immutable responses and explicit evidence limits."""
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
import uuid

from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot, write_json

VERSIONS = {'2025-11-25', '2025-06-18', '2025-03-26', '2024-11-05'}
READ_TOOLS = {
    'serena': {'find_symbol', 'find_referencing_symbols', 'get_symbols_overview', 'search_for_pattern', 'read_file'},
    'xcode': {'XcodeRead', 'XcodeGrep', 'XcodeGlob', 'XcodeListWindows', 'DocumentationSearch'},
    'sourcekit': {'find_symbols', 'references', 'definition', 'implementations', 'hover', 'diagnostics',
                  'call_hierarchy', 'type_hierarchy', 'get_definition', 'get_references'},
}
INDEX = 'spec/ref/ios-mcp-index.json'
LIMIT = 8 * 1024 * 1024


class StdioClient:
    def __init__(self, config, cwd, logs):
        argv = config.get('command')
        if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or not a for a in argv):
            raise MigrationError('MCP command must be a nonempty argv array')
        timeout = config.get('timeout_seconds', 30)
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not 0 < timeout <= 60:
            raise MigrationError('MCP timeout must be between 0 and 60 seconds')
        self.deadline = time.monotonic() + timeout
        self.events, self.transcript, self.stderr = queue.Queue(maxsize=256), [], bytearray()
        self.sequence = 0
        env = os.environ.copy()
        supplied_env = config.get('env', {})
        if (not isinstance(supplied_env, dict) or set(supplied_env) - {'MCP_XCODE_PID', 'MCP_XCODE_SESSION_ID'}
                or any(not isinstance(v, str) or not v for v in supplied_env.values())):
            raise MigrationError('MCP environment supports scoped Xcode PID/session strings only')
        env.update(supplied_env)
        self.process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, shell=False, env=env)
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
        self.sequence += 1
        ident = self.sequence
        self.send({'jsonrpc': '2.0', 'id': ident, 'method': method, 'params': params})
        while True:
            remaining = self.deadline - time.monotonic()
            if remaining <= 0:
                raise MigrationError('MCP query deadline exceeded')
            try:
                message = self.events.get(timeout=remaining)
            except queue.Empty as exc:
                self.send({'jsonrpc': '2.0', 'method': 'notifications/cancelled', 'params': {'requestId': ident, 'reason': 'deadline'}})
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
            return message['result']

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
        for thread in self.threads:
            thread.join(timeout=1)
        write_json(self.logs / 'transcript.json', self.transcript)
        (self.logs / 'stderr.log').write_bytes(self.stderr)
        self.process.stdout.close(); self.process.stderr.close()


def discover(config, source, output):
    """Actually negotiate the server and enumerate tools; never claim a query ran."""
    output.mkdir(parents=True, exist_ok=False)
    client = None
    try:
        client = StdioClient(config, source, output)
        from . import __version__
        init = client.request('initialize', {'protocolVersion': '2025-11-25', 'capabilities': {},
                                             'clientInfo': {'name': 'hmigbot-ios-source', 'version': __version__}})
        if init.get('protocolVersion') not in VERSIONS or not isinstance(init.get('serverInfo'), dict) or 'tools' not in init.get('capabilities', {}):
            raise MigrationError('MCP version or tool capability negotiation failed')
        client.send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
        tools, cursor = [], None
        for _ in range(50):
            page = client.request('tools/list', {'cursor': cursor} if cursor else {})
            if page.get('isError'):
                raise MigrationError('MCP tools/list failed: ' + str(page.get('content', page))[:2000])
            if not isinstance(page.get('tools'), list):
                raise MigrationError('MCP tools/list omitted tools')
            tools.extend(page['tools'])
            cursor = page.get('nextCursor')
            if not cursor:
                break
        else:
            raise MigrationError('MCP tool pagination limit exceeded')
        result = {'status': 'discovered', 'server': init['serverInfo'],
                  'protocol_version': init['protocolVersion'], 'tools': tools,
                  'tool_calls_performed': False}
        write_json(output / 'discovery.json', result)
        return result
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result = {'status': 'unavailable', 'error': str(exc), 'tool_calls_performed': False}
        write_json(output / 'failure.json', result)
        return result
    finally:
        if client:
            client.close()


def capture(project, server_path, request_path):
    from .native_pipeline import context
    from .ios_facts import validate_graph
    source, project = context(project)
    graph, _ = validate_graph(source, project)
    config, request = read_json(server_path), read_json(request_path)
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
    try:
        client = StdioClient(config, source, output)
        from . import __version__
        init = client.request('initialize', {'protocolVersion': '2025-11-25', 'capabilities': {},
                                             'clientInfo': {'name': 'hmigbot-ios-source', 'version': __version__}})
        if init.get('protocolVersion') not in VERSIONS or not isinstance(init.get('serverInfo'), dict) or 'tools' not in init.get('capabilities', {}):
            raise MigrationError('MCP version or tool capability negotiation failed')
        client.send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
        tools, cursor = [], None
        for _ in range(50):
            page = client.request('tools/list', {'cursor': cursor} if cursor else {})
            if not isinstance(page.get('tools'), list):
                raise MigrationError('MCP tools/list omitted tools')
            if page.get('isError'):
                raise MigrationError('MCP tools/list failed: ' + str(page.get('content', page))[:2000])
            tools.extend(page['tools']); cursor = page.get('nextCursor')
            if not cursor:
                break
        else:
            raise MigrationError('MCP tool pagination limit exceeded')
        matches = [v for v in tools if v.get('name') == tool]
        if len(matches) != 1 or matches[0].get('annotations', {}).get('readOnlyHint') is False:
            raise MigrationError('Requested read tool is unavailable, ambiguous or advertised as mutating')
        schema = matches[0].get('inputSchema', {})
        if any(k not in arguments for k in schema.get('required', [])):
            raise MigrationError('MCP request omitted a required tool argument')
        response = client.request('tools/call', {'name': tool, 'arguments': arguments})
        if response.get('isError'):
            raise MigrationError('MCP tool returned isError: ' + str(response.get('content', response))[:2000])
        if not response.get('content') and not response.get('structuredContent'):
            raise MigrationError('MCP tool returned no evidence')
        if snapshot(source)['sha256'] != graph['source_sha256']:
            raise MigrationError('Source changed during MCP query; re-index and review')
        artifact = {'schema_version': 1, 'id': ident, 'status': 'captured', 'provider': provider,
                    'server': init['serverInfo'], 'protocol_version': init['protocolVersion'],
                    'source_sha256': graph['source_sha256'], 'graph_sha256': digest(json_bytes(graph)),
                    'fact_ids': ids, 'source_anchors': [facts[i]['anchor'] for i in ids],
                    'request': request, 'tool_definition': matches[0], 'response': response,
                    'resolution': 'tool_response', 'build_context': 'unverified', 'behavior_verified': False}
        write_json(output / 'artifact.json', artifact)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        write_json(output / 'failure.json', {'id': ident, 'status': 'failed', 'provider': provider,
                                             'source_sha256': graph['source_sha256'], 'error': str(exc), 'behavior_verified': False})
        raise MigrationError('MCP capture failed; evidence: ' + str(output)) from exc
    finally:
        if client:
            client.close()
    path = project / INDEX
    index = read_json(path) if path.exists() else {'schema_version': 1, 'captures': []}
    index['captures'].append({'id': ident, 'path': (output / 'artifact.json').relative_to(project).as_posix(),
                              'sha256': digest((output / 'artifact.json').read_bytes()),
                              'transcript_sha256': digest((output / 'transcript.json').read_bytes())})
    write_json(path, index)
    return {'status': 'captured', 'id': ident, 'path': str(output), 'resolution': 'tool_response', 'behavior_verified': False}


def validate_captures(project, graph, requested_ids, claim_fact_ids=None):
    if not requested_ids:
        return
    index = read_json(project / INDEX)
    captures = {c['id']: c for c in index['captures']}
    if len(captures) != len(index['captures']):
        raise MigrationError('Duplicate MCP evidence IDs')
    facts = {f['id']: f for f in graph['facts']}
    for ident in requested_ids:
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
