"""Bind only advertised, read-only Xcode context; never open a project."""
import json
from pathlib import Path

from .core import MigrationError


def _records(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from _records(item)
    elif isinstance(value, list):
        for item in value:
            yield from _records(item)
    elif isinstance(value, str):
        try:
            parsed = json.loads(value)
        except (ValueError, TypeError):
            return
        if not isinstance(parsed, str):
            yield from _records(parsed)


def bind_arguments(client, tools, definition, arguments, source):
    schema = definition.get('inputSchema', {})
    required = schema.get('required', [])
    properties = schema.get('properties')
    if isinstance(properties, dict) and schema.get('additionalProperties') is False and set(arguments)-set(properties):
        raise MigrationError('missing project_context: arguments belong to a different advertised schema')
    if 'tabIdentifier' not in required:
        return dict(arguments), None
    # Even a supplied tab must be checked against fresh window context. No
    # cached tab can silently bind a newly selected project or another instance.
    candidates = [t for t in tools if t.get('name') in {'XcodeListWorkspaces', 'XcodeListWindows'}
                  and not t.get('inputSchema', {}).get('required')
                  and t.get('annotations', {}).get('readOnlyHint') is not False]
    official = client.config.get('command') in (['xcrun','mcpbridge'], ['/usr/bin/xcrun','mcpbridge'])
    candidates = [t for t in candidates if t['name'] != 'XcodeListWindows' or
                  official and t.get('annotations', {}).get('readOnlyHint') is True]
    if not candidates:
        raise MigrationError('missing window_context: no verified read-only context tool is advertised')
    selected = sorted(candidates, key=lambda t:t['name'])[0]
    response = client.request('tools/call', {'name':selected['name'], 'arguments':{}})
    if response.get('isError'):
        raise MigrationError('Xcode context query failed: ' + str(response))
    matches = {}
    source = Path(source).resolve()
    for record in _records(response):
        tab = record.get('tabIdentifier')
        path = record.get('workspacePath', record.get('projectPath'))
        if not isinstance(tab,str) or not tab or not isinstance(path,str):
            continue
        target = Path(path).resolve()
        if target == source or target.is_relative_to(source):
            matches[(tab,str(target))] = record
    supplied = arguments.get('tabIdentifier')
    exact = {key:value for key,value in matches.items() if key[0] == supplied}
    if exact:
        matches = exact
    if len(matches) != 1:
        raise MigrationError('missing project_context: expected one window for the configured source, found '+str(len(matches)))
    (tab, workspace), _ = next(iter(matches.items()))
    result = dict(arguments, tabIdentifier=tab)
    if any(name not in result for name in required):
        raise MigrationError('missing project_context: other required schema arguments cannot safely be inferred')
    return result, {'tool':selected['name'], 'tabIdentifier':tab,'workspacePath':workspace,
                    'rebound_stale_tab':supplied not in (None, tab),
                    'scope':'same connected instance; current read-only window context'}
