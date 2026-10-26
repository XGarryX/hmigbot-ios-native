"""Review existing CLI startup evidence without operating a device or reading UI.

This adapter binds observations to one application, PID and time window.
Missing observations remain unverified. It is not a device capture provider.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys


def timestamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Evidence timestamps must include a timezone')
    return result


def evaluate(*, bundle, pid, started_at, ended_at, process, log, network_scenario=None):
    start, end = timestamp(started_at), timestamp(ended_at)
    if not isinstance(bundle, str) or not bundle or type(pid) is not int or pid <= 0 or end < start:
        raise ValueError('Provide one application/PID and an ordered capture window')
    if (not isinstance(process, dict) or process.get('bundle_name') != bundle
            or process.get('pid') != pid or type(process.get('alive')) is not bool):
        raise ValueError('Process evidence must bind the same bundle_name and integer PID')
    observed = timestamp(process.get('observed_at', ''))
    if not start <= observed <= end:
        raise ValueError('Process observation is outside the capture window')
    events, unattributed = [], 0
    # Explicit CLI-log export format: ISO timestamp, pid=<decimal>, message.
    # Other formats stay unclassified rather than becoming this app's failure.
    pattern = re.compile(r'^(\S+)\s+pid=(\d+)\s+(.*)$')
    for number, line in enumerate(log.splitlines(), 1):
        match = pattern.match(line)
        if not match:
            unattributed += 1
            continue
        try:
            when = timestamp(match[1])
        except ValueError:
            unattributed += 1
            continue
        if int(match[2]) != pid or not start <= when <= end:
            continue
        message = match[3]
        crash = bool(re.search(r'\b(?:cppcrash|jscrash)\b|\bFATAL\b.*\b(?:exception|signal|crash)\b', message, re.I))
        request = bool(re.search(r'\b(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b', message)
                       and re.search(r'\b(?:request|send|sent|sending)\b', message, re.I))
        if crash or request:
            events.append({'line': number, 'timestamp': match[1], 'pid': pid,
                           'kind': 'crash' if crash else 'network_request', 'message': message})
    crashes = [item for item in events if item['kind'] == 'crash']
    startup = {'status': 'failed' if crashes or not process['alive'] else 'observed_alive',
               'process_alive_at_observation': process['alive'], 'crash_lines': [item['line'] for item in crashes]}
    network = {'status': 'not_applicable', 'scope': 'No startup network scenario selected'}
    if network_scenario:
        requests = [item for item in events if item['kind'] == 'network_request']
        network = {'status': 'observed' if requests else 'unverified',
                   'scenario': network_scenario, 'request_lines': [item['line'] for item in requests],
                   'scope': 'Request observation only; absent logs do not prove no request or network success'}
    return {'schema_version': 1, 'kind': 'existing_cli_startup_review',
            'bundle_name': bundle, 'pid': pid, 'window': {'started_at': started_at, 'ended_at': ended_at},
            'startup': startup, 'network': network, 'events': events,
            'unclassified_log_lines': unattributed, 'device_operation_performed': False,
            'ui_observation_performed': False, 'behavior_equivalence': 'not_verified',
            'status': 'failed' if startup['status'] == 'failed' else
                      'unverified' if network['status'] == 'unverified' else 'reviewed'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle')
    parser.add_argument('--pid', type=int)
    parser.add_argument('--started-at')
    parser.add_argument('--ended-at')
    parser.add_argument('--process-evidence', type=Path)
    parser.add_argument('--log', type=Path)
    parser.add_argument('--network-scenario')
    args = parser.parse_args(argv)
    if any(value is None for value in (args.pid, args.started_at, args.ended_at, args.process_evidence, args.log)):
        print(json.dumps({'status': 'not_run', 'reason': 'Provide existing CLI process/log files and exact PID/time window; this command never operates a device or reads UI.',
                          'resume': 'After an authorized capture, supply --process-evidence, --log, --pid, --started-at and --ended-at.',
                          'alternatives': [{'id': 'partial_record', 'available': True,
                              'command': [sys.executable, str(Path(__file__).resolve()), args.bundle],
                              'capability': 'Keep an honest not_run record and resume inputs',
                              'evidence_scope': 'No startup, network, device or UI result is claimed'},
                              {'id': 'evidence_format', 'available': True,
                               'command': [sys.executable, str(Path(__file__).resolve()), '--help'],
                               'capability': 'Inspect the installed CLI evidence options',
                               'evidence_scope': 'Describes input format only; performs no capture'}]}))
        return 3
    try:
        process_raw, log_raw = args.process_evidence.read_bytes(), args.log.read_bytes()
        result = evaluate(bundle=args.bundle, pid=args.pid, started_at=args.started_at, ended_at=args.ended_at,
                          process=json.loads(process_raw), log=log_raw.decode('utf-8-sig'),
                          network_scenario=args.network_scenario)
        result['input_hashes'] = {str(args.process_evidence): hashlib.sha256(process_raw).hexdigest(),
                                  str(args.log): hashlib.sha256(log_raw).hexdigest()}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result['status'] == 'failed' else 3 if result['status'] == 'unverified' else 0
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({'status': 'invalid_evidence', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
