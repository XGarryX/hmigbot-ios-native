"""Official Apple guidance and MCP evidence with explicit, replayable provenance."""
from pathlib import Path
import subprocess
import uuid

from .core import MigrationError, digest, json_bytes, read_json, safe_child, write_json

GUIDANCE = 'spec/ref/ios-official-analysis.json'
APPLE_SKILLS = 'spec/ref/ios-apple-skills.json'


def command(output, name, argv, *, cwd, timeout=120, input_data=None):
    """Run a real tool and retain failures and partial output before raising."""
    output.mkdir(parents=True, exist_ok=True)
    record = {'argv': list(map(str, argv)), 'cwd': str(cwd), 'exit_code': None}
    if input_data is not None:
        (output / (name + '.stdin.json')).write_bytes(input_data)
        record['stdin_sha256'] = digest(input_data)
    process = None
    try:
        process = subprocess.Popen(record['argv'], cwd=cwd, stdin=subprocess.PIPE if input_data is not None else None,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=False)
        stdout, stderr = process.communicate(input=input_data, timeout=timeout)
        record['exit_code'] = process.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or b'', exc.stderr or b''
        record['error'] = 'timeout'
        process.kill()
        process.wait(timeout=5)
        # A launched GUI/helper may inherit the pipes. Do not wait for it, or
        # terminate the user's Xcode, when the bounded CLI deadline expires.
        process.stdout.close()
        process.stderr.close()
    except OSError as exc:
        stdout, stderr = b'', str(exc).encode()
        record['error'] = str(exc)
    (output / (name + '.stdout.log')).write_bytes(stdout)
    (output / (name + '.stderr.log')).write_bytes(stderr)
    record['stdout_sha256'], record['stderr_sha256'] = digest(stdout), digest(stderr)
    write_json(output / (name + '.command.json'), record)
    if record['exit_code'] != 0:
        raise MigrationError(name + ' failed; raw diagnostics: ' + str(output))
    return stdout


def topics(tokens):
    tokens = set(tokens)
    result = []
    if 'SwiftUI' in tokens or {'View', 'body'} <= tokens:
        result.append('swiftui')
    if tokens & {'UIKit', 'UIView', 'UIViewController', 'UIHostingController', 'UIViewRepresentable'}:
        result.append('uikit')
    if tokens & {'Task', 'async', 'await', 'actor', 'MainActor', 'Sendable', 'AsyncStream'}:
        result.append('concurrency')
    if tokens & {'AppIntent', 'AppEntity', 'AppIntents', 'IntentResult'}:
        result.append('app_intents')
    return result


def export_skills(source, project, run, inventory, *, enabled=True, available=True):
    cached = None
    pointer = project / APPLE_SKILLS
    if enabled and pointer.is_file():
        try:
            ref = read_json(pointer)
            item = safe_child(project, ref['path'])
            if not item.is_relative_to((project / 'spec/ref').resolve()) or digest(item.read_bytes()) != ref['sha256']:
                raise MigrationError('Apple skill cache receipt changed')
            cached = read_json(item)
            if cached.get('source_sha256') != inventory['snapshot']['sha256'] or not cached.get('loaded'):
                cached = None
            if cached:
                for skill in cached.get('loaded', []):
                    for resource in skill['resources']:
                        path = safe_child(project, resource['path'])
                        if not path.is_relative_to((project / 'spec/ref').resolve()) or digest(path.read_bytes()) != resource['sha256']:
                            raise MigrationError('Apple skill cache resource changed')
                        path.read_text(encoding='utf-8')
                cached = {**cached, 'status': 'loaded', 'replayed': True,
                          'used': False, 'guidance_loaded': True, 'application_status': 'requires_source_review',
                          'selection_reason': 'Current source-bound official export and resource hashes revalidated'}
        except (OSError, ValueError, KeyError, TypeError) as exc:
            cached = None
            write_json(run / 'apple-skills-cache-failure.json', {'status': 'unavailable', 'error': str(exc)})
    if not enabled or not available:
        if cached:
            return cached
        return {'status': 'unavailable', 'reason': 'Official skill export disabled or Xcode tools unavailable',
                'publisher': 'Apple', 'loaded': [], 'used': False}
    from .xcode_mcp import status as mcp_status, running_instances
    service, instances = mcp_status(), running_instances()
    write_json(run / 'apple-service-observation.json', {'service': service, 'instances': instances})
    if not service.get('enabled') and not instances['instances']:
        # The export launcher may otherwise start a GUI Xcode. Keep this task's
        # CLI-only boundary; a current verified export remains reusable.
        if cached:
            return {**cached, 'live_export_skipped': 'No observed active Xcode service; GUI launch is not authorized'}
        return {'status': 'unavailable', 'publisher': 'Apple', 'loaded': [], 'used': False,
                'export_attempted': False, 'reason': 'No Xcode service visible to this process; automatic GUI launch was not attempted',
                'fallback': 'Continue compiler/CLI evidence; export in an authorized host context or choose optional MCP preparation'}
    destination = run / 'apple-skills'
    result = {'status': 'unavailable', 'publisher': 'Apple', 'loaded': [], 'used': False,
              'source_sha256': inventory['snapshot']['sha256'], 'method': 'xcrun agent skills export'}
    try:
        version = command(run / 'official-tools', 'xcode-version', ['xcodebuild', '-version'], cwd=source, timeout=30).decode().strip()
        command(run / 'official-tools', 'apple-skills-export',
                ['xcrun', 'agent', 'skills', 'export', '--output-dir', str(destination)], cwd=project, timeout=60)
        wanted = set(topics(inventory['tokens']))
        selected = {}
        if 'swiftui' in wanted:
            selected['swiftui-specialist'] = 'swiftui'
        if 'app_intents' in wanted:
            selected['app-intents-specialist'] = 'app_intents'
        tokens = set(inventory['tokens'])
        if tokens & {'DocumentGroup', 'FileDocument', 'ReferenceFileDocument', 'DocumentReader', 'DocumentWriter'}:
            selected['building-document-based-swiftui-applications'] = 'swiftui'
        if tokens & {'__counted_by', '__sized_by', '__bidi_indexable', '__single'}:
            selected['adopt-c-bounds-safety'] = 'c_bounds'
        loaded = []
        for entry in sorted(destination.glob('*/SKILL.md')):
            if entry.parent.name not in selected:
                continue
            # Capture the entry and references as data for the analysis owner.
            resources = []
            for path in [entry, *sorted((entry.parent / 'references').glob('*.md'))]:
                if path.is_symlink() or not path.resolve().is_relative_to(destination.resolve()):
                    raise MigrationError('Official skill export contains an escaping link')
                text = path.read_text(encoding='utf-8')
                resources.append({'path': path.relative_to(project).as_posix(),
                                  'sha256': digest(text.encode('utf-8'))})
            loaded.append({'skill': entry.parent.name, 'topic': selected[entry.parent.name],
                           'publisher': 'Apple', 'resources': resources})
        result.update(status='loaded' if loaded else 'not_applicable', loaded=loaded,
                      xcode_version=version, exported_skill_count=len(list(destination.glob('*/SKILL.md'))),
                      used=False, guidance_loaded=bool(loaded), application_status='requires_source_review',
                      use_scope='Loaded guidance only; applied source reviews are recorded separately by expertise-review')
        write_json(run / 'apple-skills.json', result)
        write_json(project / APPLE_SKILLS, {'path': (run / 'apple-skills.json').relative_to(project).as_posix(),
                                          'sha256': digest((run / 'apple-skills.json').read_bytes())})
        return result
    except (MigrationError, OSError, ValueError) as exc:
        result['error'] = str(exc)
        write_json(run / 'apple-skills-failure.json', result)
        if cached:
            return {**cached, 'live_export_error': str(exc)}
        return result


def server_config(project, cfg, *, available):
    if cfg.get('mode') in {'static', 'replay'}:
        return None, 'No live MCP call in explicitly static/replay mode'
    preparation = project / 'spec/reports/init-environment.json'
    if preparation.is_file():
        try:
            preference = read_json(preparation).get('capabilities', {}).get('xcode_mcp', {})
            if preference.get('choice') == 'skip':
                return None, 'Developer selected CLI evidence during initialization'
            if preference.get('choice') == 'ask':
                return None, 'MCP use is awaiting the developer choice; CLI evidence continues'
        except (MigrationError, OSError, ValueError, TypeError, AttributeError):
            return None, 'MCP preparation preference is unreadable; retain CLI until its intended choice is established'
    if cfg.get('mcp_server'):
        path = Path(cfg['mcp_server'])
        path = path if path.is_absolute() else safe_child(project, cfg['mcp_server'])
        value = read_json(path)
        # Configured third-party servers keep their actual provider/origin.
        value = dict(value)
        value['_official'] = value.get('command') in (['xcrun', 'mcpbridge'], ['/usr/bin/xcrun', 'mcpbridge'])
        return value, 'Explicit MCP server configuration'
    if not available:
        return None, 'Apple Xcode MCP requires a native Xcode host'
    return {'provider': 'xcode', 'transport': 'stdio', 'command': ['xcrun', 'mcpbridge'],
            'env': {'MCP_XCODE_SESSION_ID': str(uuid.uuid4())},
            'timeout_seconds': 10, '_official': True}, 'Prefer the Apple bridge exported by Xcode with one scoped session per run'


def discover_mcp(source, project, run, cfg, *, available):
    from .source_mcp import discover
    server, reason = server_config(project, cfg, available=available)
    if server is None:
        return {'status': 'unavailable', 'reason': reason, 'tool_calls_performed': False}
    candidates = [server]
    if server['_official'] and not cfg.get('mcp_server'):
        from .xcode_mcp import running_instances, status
        instances, host_status = running_instances(), status()
        write_json(run / 'mcp-host-status.json', host_status)
        write_json(run / 'mcp-running-instances.json', instances)
        for instance in instances['instances']:
            candidates.append({**server, 'env': {**server.get('env', {}), 'MCP_XCODE_PID': str(instance['pid'])}})
    attempts, selected, selected_server = [], None, server
    for index, candidate in enumerate(candidates):
        output = run / ('mcp-discovery' if index == 0 else 'mcp-discovery-instance-' + str(index))
        result = discover(candidate, source, output)
        names = {tool.get('name') for tool in result.get('tools', [])
                 if tool.get('annotations', {}).get('readOnlyHint') is not False}
        score = 100 if 'DocumentationSearch' in names else 10 if 'GetTargetBuildSettings' in names else 1 if names else 0
        attempts.append({'path': str(output), 'status': result['status'], 'score': score,
                         'pid': candidate.get('env', {}).get('MCP_XCODE_PID'),
                         'error': result.get('error'), 'failure_kind': result.get('failure_kind')})
        if selected is None or score > selected[0]:
            selected, selected_server = (score, result), candidate
        if score == 100:
            break
    path = run / 'mcp-server.json'
    write_json(path, {k: v for k, v in selected_server.items() if not k.startswith('_')})
    write_json(run / 'mcp-discovery-selection.json', {'attempts': attempts, 'selected_config': str(path)})
    result = selected[1]
    return {**result, 'config': str(path), 'publisher': 'Apple' if server['_official'] else 'user_configured',
            'selection_reason': reason, 'attempts': attempts,
            'documentation_search': 'available' if any(t.get('name') == 'DocumentationSearch' for t in result.get('tools', [])) else 'not_advertised'}


def query_mcp(project, source, graph, run, inventory, discovery):
    from .source_mcp import capture, recovery_options
    result = {'status': 'not_run', 'publisher': discovery.get('publisher'), 'captures': [], 'failures': []}
    if discovery.get('status') != 'discovered':
        result['reason'] = discovery.get('error', discovery.get('reason', 'MCP not connected'))
        result['options'] = discovery.get('options', recovery_options(discovery.get('failure_kind')))
        return result
    tools = {t.get('name'): t for t in discovery['tools']}
    tool = tools.get('DocumentationSearch')
    if tool is None or tool.get('annotations', {}).get('readOnlyHint') is False:
        result['reason'] = 'Server does not expose the permitted DocumentationSearch tool'
        result['options'] = recovery_options('tool_unavailable')
        return result
    queries = {'swiftui': 'SwiftUI state data flow view identity ForEach',
               'uikit': 'UIKit UIViewController lifecycle Auto Layout delegate ownership',
               'concurrency': 'Swift concurrency task cancellation actor isolation',
               'app_intents': 'App Intents execution model entity stable identity'}
    ids = [f['id'] for f in graph['facts']]
    if not ids:
        result['reason'] = 'No source facts to bind an MCP query'
        return result
    for topic in topics(inventory['tokens']):
        arguments = {'query': queries[topic]}
        required = tool.get('inputSchema', {}).get('required', [])
        if any(k not in arguments for k in required):
            result['failures'].append({'topic': topic, 'reason': 'Tool requires context not safely derivable: ' + ','.join(required)})
            continue
        request = run / ('mcp-query-' + topic + '.json')
        write_json(request, {'source_sha256': graph['source_sha256'],
                             'graph_sha256': digest(json_bytes(graph)), 'fact_ids': ids,
                             'tool': 'DocumentationSearch', 'arguments': arguments})
        try:
            saved = capture(project, Path(discovery['config']), request)
            result['captures'].append({**saved, 'topic': topic,
                                       'publisher': discovery.get('publisher')})
        except (MigrationError, OSError, ValueError) as exc:
            diagnostic = getattr(exc, 'diagnostic', {})
            result['failures'].append({'topic': topic, 'reason': str(exc),
                                       'failure_kind': diagnostic.get('failure_kind'),
                                       'execution': diagnostic.get('execution'),
                                       'options': diagnostic.get('options', recovery_options(None))})
    result['status'] = 'captured' if result['captures'] else 'unavailable'
    return result


def publish_guidance(project, graph, skills, mcp):
    resources = {}
    for entry in skills.get('loaded', []):
        resources.setdefault(entry['topic'], []).extend(entry['resources'])
    if mcp.get('publisher') == 'Apple':
        for entry in mcp.get('captures', []):
            path = Path(entry['path']) / 'artifact.json'
            resources.setdefault(entry['topic'], []).append(
                {'path': path.relative_to(project).as_posix(), 'sha256': digest(path.read_bytes())})
    result = {'schema_version': 1, 'source_sha256': graph['source_sha256'],
              'graph_sha256': digest(json_bytes(graph)), 'policy': 'official_first',
              'official_resources': resources, 'apple_skills': skills, 'xcode_mcp': mcp,
              'semantic_review': 'required', 'behavior_verified': False}
    write_json(project / GUIDANCE, result)
    provenance_path = project / 'spec/ref/ios-analysis-provenance.json'
    provenance = read_json(provenance_path) if provenance_path.exists() else {'schema_version': 1}
    provenance['official_analysis'] = {
        'path': GUIDANCE, 'sha256': digest((project / GUIDANCE).read_bytes()),
        'source_sha256': graph['source_sha256'], 'graph_sha256': result['graph_sha256'],
        'apple_skills_status': skills.get('status'), 'xcode_mcp_status': mcp.get('status'),
        'semantic_review': 'required', 'behavior_verified': False}
    write_json(provenance_path, provenance)
    return result


def preferred_reviews(project, source, graph, reviews):
    path = project / GUIDANCE
    if not path.is_file():
        return reviews, None
    value = read_json(path)
    if value.get('source_sha256') != graph['source_sha256'] or value.get('graph_sha256') != digest(json_bytes(graph)):
        raise MigrationError('Official analysis guidance is stale; rerun source-analysis and review')
    changed = []
    for review in reviews:
        official = value.get('official_resources', {}).get(review['pack'], [])
        if official:
            resolved = []
            for resource in official:
                item = safe_child(project, resource['path'])
                if (not item.is_relative_to((project / 'spec/ref').resolve()) or not item.is_file()
                        or digest(item.read_bytes()) != resource['sha256']):
                    raise MigrationError('Official analysis resource changed')
                resolved.append({'path': str(item), 'sha256': resource['sha256']})
            changed.append({**review, 'resources': resolved, 'resource_origin': 'Apple',
                            'selection_reason': 'Applicable exported Apple guidance or actual official MCP evidence'})
        else:
            changed.append({**review, 'resource_origin': 'third_party',
                            'selection_reason': 'No applicable current official resource; explicit third-party fallback'})
    return changed, digest(path.read_bytes())
