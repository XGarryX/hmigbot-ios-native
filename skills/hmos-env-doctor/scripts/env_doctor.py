"""Project-local native environment diagnostic entry point."""
from pathlib import Path
import json,sys
if __name__=='__main__':
    try:
        skill=Path(__file__).resolve().parents[1];runtime=skill/'runtime.json'
        root=(skill/json.loads(runtime.read_text(encoding='utf-8-sig'))['runtime_relative']).resolve() if runtime.is_file() else skill.parents[1]
        sys.path.insert(0,str(root/'src'))
        from hmigbot_ios152.env_doctor import main
        raise SystemExit(main())
    except Exception as exc:
        if hasattr(sys.stderr,'reconfigure'):sys.stderr.reconfigure(encoding='utf-8')
        print(json.dumps({'error':'Environment entry failed: '+type(exc).__name__},ensure_ascii=False),file=sys.stderr)
        raise SystemExit(2)
