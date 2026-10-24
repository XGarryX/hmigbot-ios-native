"""Machine-readable CLI output that also works in legacy Windows consoles."""
from __future__ import annotations

import io
import json
import sys


def configure_utf8(*streams):
    """Prefer UTF-8 and report whether every stream exposes that encoding."""
    confirmed = []
    for stream in streams:
        reconfigure = getattr(stream, 'reconfigure', None)
        if reconfigure is not None:
            try:
                reconfigure(encoding='utf-8')
            except (AttributeError, OSError, ValueError):
                # Embedded callers may supply a fixed-encoding or closed wrapper.
                # emit_json still has a lossless ASCII JSON fallback below.
                pass
        encoding = getattr(stream, 'encoding', None)
        confirmed.append(isinstance(encoding, str) and encoding.lower().replace('_', '-').replace('-', '') in {'utf8', 'utf8sig'})
    return all(confirmed)


def emit_json(value, *, stream=None, indent=2):
    stream = sys.stdout if stream is None else stream
    utf8 = configure_utf8(stream) or isinstance(stream, io.StringIO)
    # Pure Chinese is encodable as GBK but those bytes are not UTF-8. Escape
    # proactively whenever the stream's output encoding cannot be confirmed.
    payload = json.dumps(value, ensure_ascii=not utf8, indent=indent)
    try:
        stream.write(payload + '\n')
    except UnicodeEncodeError:
        # JSON escapes retain the exact Unicode value; they are valid UTF-8 too.
        stream.write(json.dumps(value, ensure_ascii=True, indent=indent) + '\n')
