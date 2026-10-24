"""Official Apple guidance and MCP evidence with explicit, replayable provenance."""
from pathlib import Path
import subprocess
import uuid

from .core import MigrationError, digest, json_bytes, read_json, safe_child, write_json

GUIDANCE = 'spec/ref/ios-official-analysis.json'
APPLE_SKILLS = 'spec/ref/ios-apple-skills.json'


def command(output, name, argv, *, cwd, timeout=120):
    """Run a real tool and retain failures and partial output before raising."""
    output.mkdir(parents=True, exist_ok=True)
    record = {'argv': list(map(str, argv)), 'cwd': str(cwd), 'exit_code': None}
    process = None
    try:
        process = subprocess.Popen(record['argv'], cwd=cwd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=False)
        stdout, stderr = process.communicate(timeout=timeout)
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
                          'selection_reason': 'Current source-bound official export and resource hashes revalidated'}
        except (OSError, ValueError, KeyError, TypeError) as exc:
            cached = None
            write_json(run / 'apple-skills-cache-failure.json', {'status': 'unavailable', 'error': str(exc)})
    if not enabled or not available:
        if cached:
            return cached
        return {'status': 'unavailable', 'reason': 'Official skill export disabled or Xcode tools unavailable',
                'publisher': 'Apple', 'loaded': [], 'used': False}
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
                      used=bool(loaded), use_scope='Loaded guidance for analysis; not a reviewed semantic conclusion')
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
    path = run / 'mcp-server.json'
    write_json(path, {k: v for k, v in server.items() if not k.startswith('_')})
    result = discover(server, source, run / 'mcp-discovery')
    return {**result, 'config': str(path), 'publisher': 'Apple' if server['_official'] else 'user_configured',
            'selection_reason': reason}


def query_mcp(project, source, graph, run, inventory, discovery):
    from .source_mcp import capture
    result = {'status': 'not_run', 'publisher': discovery.get('publisher'), 'captures': [], 'failures': []}
    if discovery.get('status') != 'discovered':
        result['reason'] = discovery.get('error', discovery.get('reason', 'MCP not connected'))
        return result
    tools = {t.get('name'): t for t in discovery['tools']}
    tool = tools.get('DocumentationSearch')
    if tool is None or tool.get('annotations', {}).get('readOnlyHint') is False:
        result['reason'] = 'Server does not expose the permitted DocumentationSearch tool'
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
            result['failures'].append({'topic': topic, 'reason': str(exc)})
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
                if not item.is_relative_to((project / 'spec/ref').resolve()) or digest(item.read_bytes()) != resource['sha256']:
                    raise MigrationError('Official analysis resource changed')
                resolved.append({'path': str(item), 'sha256': resource['sha256']})
            changed.append({**review, 'resources': resolved, 'resource_origin': 'Apple',
                            'selection_reason': 'Applicable exported Apple guidance or actual official MCP evidence'})
        else:
            changed.append({**review, 'resource_origin': 'third_party',
                            'selection_reason': 'No applicable current official resource; explicit third-party fallback'})
    return changed, digest(path.read_bytes())
