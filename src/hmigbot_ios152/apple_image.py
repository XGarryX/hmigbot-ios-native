"""Decode screenshots with Apple's ImageIO; no Pillow runtime dependency."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
from hmigbot_ios.apple_tools import environment, run
from hmigbot_ios.core import MigrationError, write_json


def inspect(path):
    info, env = environment()
    source = Path(__file__).resolve().parents[2]/'providers/image-inspect/main.swift'
    identity = {'toolchain':info, 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    key = hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    root = Path(os.environ.get('HMIGBOT_APPLE_CACHE',Path.home()/'Library/Caches/hmigbot-ios'))/'image-inspect'/key
    root.mkdir(parents=True,exist_ok=True)
    binary, record = root/'image-inspect', root/'build.json'
    with (root/'build.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        valid = False
        if binary.is_file() and record.is_file():
            previous = json.loads(record.read_text())
            valid = previous.get('identity') == identity and previous.get('binary_sha256') == hashlib.sha256(binary.read_bytes()).hexdigest()
        if not valid:
            temp = root/('image-inspect-'+str(os.getpid()))
            argv = [info['swiftc'],'-O','-sdk',info['mac_sdk'],str(source),'-o',str(temp)]
            result = run(argv,env=env,timeout=180)
            temp.chmod(0o755);temp.replace(binary)
            write_json(record,{'identity':identity,'argv':argv,'exit_code':result.returncode,
                               'stderr':result.stderr.decode(),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()})
    result = run([str(binary),str(Path(path).resolve())],env=env)
    try: value = json.loads(result.stdout)
    except ValueError as exc: raise MigrationError('ImageIO provider returned invalid data') from exc
    value['png_sha256'] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return value
