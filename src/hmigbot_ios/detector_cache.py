"""Reuse complete, immutable detector evidence for identical consumed inputs."""
from pathlib import Path
import subprocess

from .core import digest, json_bytes, read_json, safe_child, write_json


def identity(inputs, rules, arguments):
    normalized=[];skip=False
    for argument in map(str,arguments):
        if skip:skip=False;continue
        if argument in {'--state-file','--output-json','--max-iter'}:skip=True;continue
        normalized.append(argument)
    return digest(json_bytes({'policy':'detector-evidence/1','inputs':inputs,'rules':rules,'arguments':normalized}))


def load(project, path, signature):
    if not path.is_file():return None
    try:
        record=read_json(path)
        if record.get('signature')!=signature:return None
        raw=safe_child(project,record['directory'])
        expected=record['files']
        if not isinstance(expected,dict) or not {'state.json','result.json'}<=expected.keys():return None
        actual={p.name:digest(p.read_bytes()) for p in raw.iterdir() if p.is_file() and not p.is_symlink()}
        if actual!=expected:return None
        process=record['process']
        if process.get('returncode') not in (0,1,2) or not all(isinstance(process.get(k),str) for k in ('stdout','stderr')):return None
        return raw,subprocess.CompletedProcess(process['args'],process['returncode'],process['stdout'],process['stderr'])
    except (OSError,ValueError,KeyError,TypeError):
        return None


def save(project, path, signature, raw, process):
    files={p.name:digest(p.read_bytes()) for p in raw.iterdir() if p.is_file() and not p.is_symlink()}
    write_json(path,{'schema_version':1,'signature':signature,'directory':raw.relative_to(project).as_posix(),
                    'files':files,'process':{'args':list(map(str,process.args)) if isinstance(process.args,(list,tuple)) else str(process.args),
                      'returncode':process.returncode,'stdout':process.stdout,'stderr':process.stderr}})
