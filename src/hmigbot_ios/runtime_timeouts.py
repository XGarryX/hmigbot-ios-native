"""Shared subprocess limits; these are execution guards, not acceptance evidence."""
from __future__ import annotations

import math
import os
import subprocess
import time

from .core import MigrationError


DEFAULTS = {'scheduler': 60, 'structural': 180, 'literal': 60, 'assembly': 60,
            'join': 60, 'helper': None}
VARIABLES = {stage: 'HMIGBOT_' + stage.upper() + '_TIMEOUT_SECONDS' for stage in DEFAULTS}
DEADLINE = 'HMIGBOT_DEADLINE_EPOCH_SECONDS'
MAX_STAGE_SECONDS = 604800  # Bound platform wait APIs to one week per invocation.
_DEFAULT = object()


def _number(value, variable, *, maximum=None):
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise MigrationError(variable + ' must be a finite positive number') from None
    if not math.isfinite(result) or result <= 0 or (maximum is not None and result > maximum):
        raise MigrationError(variable + ' must be finite, positive' +
                             (f' and at most {maximum} seconds' if maximum is not None else ''))
    return result


def timeout_for(stage, *, env=None, now=None, default=_DEFAULT):
    """Return min(stage cap, shared absolute deadline minus current UTC epoch).

    All configured values are validated. An omitted deadline adds no overall
    budget. A caller with a historically unbounded subprocess can supply
    default=None; explicit stage configuration and deadline still apply.
    """
    if stage not in DEFAULTS:
        raise MigrationError('Unknown subprocess timeout stage: ' + str(stage))
    env = os.environ if env is None else env
    configured = {name: _number(env[key], key, maximum=MAX_STAGE_SECONDS)
                  for name, key in VARIABLES.items() if key in env}
    seconds = configured.get(stage, DEFAULTS[stage] if default is _DEFAULT else default)
    if DEADLINE in env:
        deadline = _number(env[DEADLINE], DEADLINE)
        remaining = deadline - (time.time() if now is None else now)
        if remaining > MAX_STAGE_SECONDS:
            raise MigrationError(DEADLINE + ' must be within one week of the current time')
        if remaining <= 0:
            error = subprocess.TimeoutExpired([stage], 0, output=b'',
                stderr=b'Shared runtime deadline expired before subprocess launch.\n')
            error.ios_timeout_policy = {'stage': stage, 'deadline_epoch_seconds': deadline,
                                        'process_started': False}
            raise error
        seconds = remaining if seconds is None else min(seconds, remaining)
    return seconds


def timeout_evidence(error):
    """Retain actual partial child output without treating an old report as current."""
    def text(value):
        return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value or ''
    return {'timeout_seconds': error.timeout, 'stdout': text(error.output), 'stderr': text(error.stderr),
            'process_tree': getattr(error, 'ios_process_tree', None),
            'timeout_policy': getattr(error, 'ios_timeout_policy', None)}
