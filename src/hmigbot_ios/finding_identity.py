"""iOS extraction identities without changing the shared findings queue."""
from __future__ import annotations

import json


def extraction_finding(queue, issue):
    """Keep legacy path identity for unscoped issues; split target subjects.

    The old path key was ambiguous across targets, so scoped findings start
    fresh rather than inheriting another target's occurrence/decision state.
    Diagnostic messages are deliberately excluded from identity.
    """
    path = str(issue.get('path', 'project'))
    rule = 'IOS.EXTRACTION_UNRESOLVED'
    advisory = issue.get('rule') == 'IOS.PROVIDER_RETRY' or issue.get('severity') == 'warn' or issue.get('blocking') is False
    if issue.get('target') is None:
        finding = queue.make(rule, 'spec', path, str(issue), severity='warn' if advisory else None)
        if advisory:
            finding['advisory_basis'] = 'Historical provider attempt or producer-classified diagnostic; current evidence is checked independently.'
        return finding
    identity = {'issue_code': issue.get('code') or issue.get('rule') or 'unresolved',
                'project': issue.get('project_path') or path, 'target': issue['target']}
    configuration = issue.get('configuration', issue.get('config'))
    if configuration is not None:
        identity['configuration'] = configuration
    subject = 'ios-extraction:' + json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    finding = queue.make(rule, 'spec', subject, str(issue), subject_ref=path, severity='warn' if advisory else None)
    finding['display_subject'] = path + ' [' + str(issue['target']) + ']'
    finding['extraction_subject'] = identity
    if finding.get('impact'):
        finding['impact']['affected_objects'] = [path]
        finding['impact']['target'] = issue['target']
        if configuration is not None:
            finding['impact']['configuration'] = configuration
    return finding
