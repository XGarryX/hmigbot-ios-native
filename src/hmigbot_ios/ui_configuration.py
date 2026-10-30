"""Official configuration observations with explicit application/device scope.

System preferences do not prove an app's overridden SwiftUI/ArkUI environment.
Missing observations stay unknown; failed commands never default to light/en/1.
"""
from datetime import datetime, timezone
from pathlib import Path
import plistlib
import re
import subprocess
import time

from .core import MigrationError, write_json

KEYS = ('language','locale','theme','content_size')
UUID = re.compile(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}')


def collect_simulator_context(device_id, bundle_id, output):
    """Read only the explicit simulator; do not start it or change settings."""
    if not isinstance(device_id,str) or not UUID.fullmatch(device_id):
        raise MigrationError('Configuration observation needs an exact Simulator UUID')
    if not isinstance(bundle_id,str) or not bundle_id:
        raise MigrationError('Configuration observation needs the selected app bundle id')
    output = Path(output)
    if output.exists():
        raise MigrationError('Configuration observation needs a fresh output directory')
    output.mkdir(parents=True)
    observed, calls, missing = {}, [], []
    commands = {
        'theme':['xcrun','simctl','ui',device_id,'appearance'],
        'content_size':['xcrun','simctl','ui',device_id,'content_size'],
        'language':['xcrun','simctl','spawn',device_id,'defaults','read','-g','AppleLanguages'],
        'locale':['xcrun','simctl','spawn',device_id,'defaults','read','-g','AppleLocale'],
    }
    for field, argv in commands.items():
        started = time.monotonic()
        code, stdout, stderr, timed_out = None, b'', b'', False
        try:
            run = subprocess.run(argv,capture_output=True,timeout=10,shell=False)
            code, stdout, stderr = run.returncode, run.stdout, run.stderr
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, timed_out = exc.stdout or b'', exc.stderr or b'', True
        except OSError as exc:
            stderr = str(exc).encode()
        for suffix, raw in [('stdout',stdout),('stderr',stderr)]:
            (output/(field+'.'+suffix)).write_bytes(raw)
        call = {'argv':argv,'kind':'device_configuration_observation','scope':'device',
                'actual_call_now':True,'exit_code':code,'timed_out':timed_out,
                'elapsed_seconds':time.monotonic()-started,
                'stdout':field+'.stdout','stderr':field+'.stderr'}
        calls.append(call)
        value = stdout.decode('utf-8',errors='replace').strip() if code == 0 and not timed_out else ''
        if field == 'theme' and value not in {'light','dark'}:
            value = ''
        elif field == 'content_size' and value not in {
                'extra-small','small','medium','large','extra-large','extra-extra-large','extra-extra-extra-large',
                'accessibility-medium','accessibility-large','accessibility-extra-large',
                'accessibility-extra-extra-large','accessibility-extra-extra-extra-large'}:
            value = ''
        elif field == 'language' and value:
            try:
                languages = plistlib.loads(stdout)
            except (ValueError,plistlib.InvalidFileException):
                found = re.fullmatch(r'\(\s*"?([A-Za-z]{2,3}(?:[-_][A-Za-z0-9]+)*)"?\s*(?:,.*)?\)',value,re.S)
                languages = [found[1]] if found else []
            value = languages[0] if isinstance(languages,list) and languages and isinstance(languages[0],str) else ''
            if not re.fullmatch(r'[A-Za-z]{2,3}(?:[-_][A-Za-z0-9]+)*',value):
                value = ''
        elif field == 'locale' and not re.fullmatch(r'[A-Za-z]{2,3}(?:[-_][A-Za-z0-9]+)+(?:@[A-Za-z0-9=;-]+)?',value):
            value = ''
        if value:
            observed[field] = {'value':value,'scope':'device','actual':True,'call_index':len(calls)-1}
        else:
            missing.append({'field':field,'reason':'native_read_failed_or_output_not_recognized',
                            'call_index':len(calls)-1})
    result = {'schema_version':'hmigbot-device-ui-context/1','platform':'ios',
              'observed_at':datetime.now(timezone.utc).isoformat(),
              'bundle_id':bundle_id,'device_id':device_id,'observed':observed,'calls':calls,'missing':missing,
              'application_configuration_proven':False,'settings_changed':False}
    write_json(output/'context.json',result)
    return result


def _canonical(field,value):
    if field in {'language','locale'}:
        return value.replace('_','-').casefold()
    return value


def compare_contexts(source_receipt, target_receipt):
    """Consume verified native app receipts; retain partial and device evidence."""
    values, gaps, differences = {}, [], []
    for platform,receipt in [('ios',source_receipt),('harmonyos',target_receipt)]:
        values[platform] = {}
        calls = receipt.get('calls',[])
        native = (receipt.get('observations_actual') is True and isinstance(calls,list)
                  and any(isinstance(c,dict) and c.get('actual_call_now') is True
                          and type(c.get('exit_code')) is int and c['exit_code'] == 0
                          and not c.get('timed_out') and c.get('kind') in {'app_ui_test','configuration_observation'}
                          for c in calls))
        observed = receipt.get('observed_configuration',{})
        for field in KEYS:
            value = observed.get(field) if isinstance(observed,dict) else None
            known = native and isinstance(value,str) and value.casefold() not in {'','unknown','unsupported'}
            values[platform][field] = {'value':value if known else None,'scope':'application','actual':bool(known)}
            if not known:
                gaps.append({'platform':platform,'field':field,'reason':'actual_application_configuration_not_observed'})
        # This is supplementary evidence, not a replacement for an app override.
        values[platform]['device_context'] = receipt.get('device_context')
    for field in KEYS:
        a,b = values['ios'][field],values['harmonyos'][field]
        if a['actual'] and b['actual'] and _canonical(field,a['value']) != _canonical(field,b['value']):
            differences.append({'field':field,'source':a['value'],'target':b['value'],
                                'reason':'observed_application_configuration_differs; no blanket exemption'})
    return {'values':values,'gaps':gaps,'differences':differences,
            'application_configuration_comparable':not gaps and not differences,
            'requested_configuration_is_observation':False}
