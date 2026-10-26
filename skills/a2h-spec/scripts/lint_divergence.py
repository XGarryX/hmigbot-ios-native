"""Object-contract launcher for the bundled divergence helper.

Responsibility split
--------------------
* ``hmigbot_ios.spec_discovery`` (source-visible) owns the discovery rule: it
  decides which Markdown files are main feature documents or addenda, their
  stable ``F<digits>`` identities, the authored AC identities and the expected
  ``mains / parity ACs / divergence ACs`` counts.
* The bundled helper under ``vendor/hmigbot`` owns every divergence and
  decision-ledger rule (``源:`` / ``决:`` classification, R1/R2/R3/R5).  This
  launcher does not re-implement, replace or relax those rules.
* This launcher only bridges the helper's historical ASCII filename filter: a
  main document the filter would miss is presented to the helper under a
  deterministic ASCII alias in a temporary shadow directory.  The caller's
  ledger path and ``--gate`` semantics are forwarded unchanged, and project
  files are never renamed, copied over or edited.

Protocol boundary
-----------------
CLI: ``--spec-dir`` (required), ``--ledger`` and ``--gate`` are forwarded to
the helper.  ``--allow-empty`` is consumed here and is the only way to accept
a proven not-applicable scope with zero main documents.  Exit codes follow the
helper: 0 pass, 1 gate/object failure, 2 usage error.  Diagnostics are plain
text; ``RESULT: PASS`` is emitted only when the helper passed and its reported
object counts equal the source-visible expectation.
"""
import json
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_skill = next((parent for parent in _here.parents if (parent / 'SKILL.md').is_file()), None)
if _skill is None:
    raise SystemExit('a2h-spec SKILL.md not found above %s' % _here)
_runtime = _skill / 'runtime.json'
if _runtime.exists():
    try:
        _root = (_skill / json.loads(_runtime.read_text(encoding='utf-8'))['runtime_relative']).resolve()
    except (OSError, ValueError, KeyError) as exc:
        raise SystemExit('runtime.json is not usable: %s' % exc)
else:
    _root = _skill.parents[1]

sys.path.insert(0, str(_root / 'src'))
try:
    from hmigbot_ios import spec_discovery, spec_helpers
    from hmigbot_ios.cli_output import configure_utf8
except Exception as exc:  # fail closed instead of running an unguarded helper
    raise SystemExit(
        'Object gate sources are missing from %s/src (%s); reinstall the complete plugin'
        % (_root, exc))

configure_utf8(sys.stdout, sys.stderr)


def _guard(exc, helper_result=None, aliases=None, replacements=(), exit_code=1):
    if helper_result is not None:
        out, err = spec_helpers.rendered(helper_result, aliases=aliases,
                                         replacements=replacements)
        text = out
        if err:
            text += ('' if not text or text.endswith('\n') else '\n') + err
        text = text.replace('RESULT: PASS', 'RESULT: FAIL')
        if text:
            sys.stdout.buffer.write(text.encode('utf-8'))
            sys.stdout.buffer.flush()
    print('OBJECT GUARD: %s: %s' % (exc.code, exc.detail))
    last = [line for line in (text.splitlines() if helper_result is not None else [])
            if line.strip()]
    if not last or last[-1].strip() != 'RESULT: FAIL':
        print('RESULT: FAIL')
    raise SystemExit(exit_code)


try:
    helper = spec_helpers.helper_script(_root, spec_helpers.DIVERGENCE)
except spec_helpers.HelperError as exc:
    raise SystemExit(str(exc))

arguments = list(sys.argv[1:])
parsed = spec_helpers.parse_divergence_arguments(arguments)

# Help and missing-argument handling stay exactly the helper's own.
if parsed.spec_dir is None or any(token in ('-h', '--help') for token in arguments):
    result = spec_helpers.run_helper(helper, arguments)
    spec_helpers.forward(result)
    raise SystemExit(result.returncode)

try:
    discovery = spec_discovery.discover(parsed.spec_dir, allow_empty=parsed.allow_empty)
except spec_discovery.DiscoveryError as exc:
    _guard(exc, exit_code=2 if exc.code == 'SPEC_DIR_MISSING' else 1)
try:
    spec_discovery.divergence_counts(discovery)  # fail fast on malformed AC identities
except spec_discovery.DiscoveryError as exc:
    _guard(exc, exit_code=1)

with spec_helpers.shadow_features(Path(parsed.spec_dir), discovery,
                                  spec_helpers.DIVERGENCE) as shadow:
    ledger = (parsed.ledger if parsed.ledger is not None
              else spec_helpers.default_ledger(parsed.spec_dir))
    try:
        spec_discovery.reject_links(Path(ledger))
    except spec_discovery.DiscoveryError as exc:
        _guard(exc)
    forwarded = spec_helpers.rewrite_option(parsed.forward, '--spec-dir',
                                            str(shadow.features_dir))
    forwarded = spec_helpers.rewrite_option(forwarded, '--ledger', ledger,
                                            append_if_missing=parsed.ledger is None)
    result = spec_helpers.run_helper(helper, forwarded)
    # The helper names the shadow project only in diagnostics; map it back.
    real_root = Path(parsed.spec_dir).resolve().parent.parent.parent
    replacements = spec_helpers.path_replacements(shadow.root, real_root)

if result.returncode != 0:
    spec_helpers.forward(result, aliases=shadow.aliases, replacements=replacements)
    raise SystemExit(result.returncode)

text = (result.stdout + b'\n' + result.stderr).decode('utf-8', 'replace')
try:
    reported = spec_helpers.parse_divergence_counts(text)
    spec_helpers.verify_divergence_objects(discovery, reported,
                                           allow_empty=parsed.allow_empty)
except spec_helpers.ObjectContractError as exc:
    _guard(exc, result, shadow.aliases, replacements, exit_code=1)

spec_helpers.forward(result, aliases=shadow.aliases, replacements=replacements)
raise SystemExit(0)
