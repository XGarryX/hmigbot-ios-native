"""Object-contract launcher for the bundled traceability-index helper.

Responsibility split
--------------------
* ``hmigbot_ios.spec_discovery`` (source-visible) owns the discovery rule: it
  decides which Markdown files are main feature documents or addenda, their
  stable ``F<digits>`` identities and the authored AC identities that the
  index must contain.
* The bundled helper under ``vendor/hmigbot`` owns index derivation: parsing
  ``判:``/``真:``/oracle fields, ``feature_id`` derivation, digests, status and
  ``_meta`` counters.  This launcher does not re-implement those rules.
* This launcher bridges the helper's historical ASCII filename filter through
  a temporary shadow directory, validates every emitted requirement against
  the source-visible document set, maps aliases back to the real Unicode file
  names and only then publishes the index atomically.  Project files and an
  existing index are never touched when validation fails.

Protocol boundary
-----------------
CLI: ``--project-root`` (required) and ``--out`` are forwarded to the helper.
``--allow-empty`` is consumed here and is the only way to accept a scope with
zero main documents.  A relative ``--out`` is resolved against the current
directory (the original helper crashed on one).  Exit codes: 0 success,
1 object-contract failure, 2 usage or unreadable input, 3 duplicate AC
identities (the helper's own exit code for that condition).  Diagnostics are
plain text; the published index is the only JSON output.
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
    raise SystemExit(exit_code)


def _real_out(argument, project_root):
    if argument is None:
        return project_root / 'spec/.a2h/requirements-index.json'
    out = Path(argument)
    if not out.is_absolute():
        out = Path.cwd() / out
    return out


try:
    helper = spec_helpers.helper_script(_root, spec_helpers.TRACEABILITY)
except spec_helpers.HelperError as exc:
    raise SystemExit(str(exc))

arguments = list(sys.argv[1:])
parsed = spec_helpers.parse_traceability_arguments(arguments)

# Help and missing-argument handling stay exactly the helper's own.
if parsed.project_root is None or any(token in ('-h', '--help') for token in arguments):
    result = spec_helpers.run_helper(helper, arguments)
    spec_helpers.forward(result)
    raise SystemExit(result.returncode)

project_root = Path(parsed.project_root)
features_dir = project_root / 'spec/baseline/features'

try:
    discovery = spec_discovery.discover(features_dir, allow_empty=parsed.allow_empty)
except spec_discovery.DiscoveryError as exc:
    _guard(exc, exit_code={'SPEC_DIR_MISSING': 2, 'DUPLICATE_AC_ID': 3}.get(exc.code, 1))
try:
    spec_discovery.expected_requirements(discovery)  # fail fast on AC identity problems
except spec_discovery.DiscoveryError as exc:
    _guard(exc, exit_code=3 if exc.code == 'DUPLICATE_AC_ID' else 1)

real_root = project_root.resolve()
real_out = _real_out(parsed.out, real_root)
try:
    spec_helpers.validate_output_path(real_out, real_root, discovery)
except (spec_helpers.ObjectContractError, spec_discovery.DiscoveryError) as exc:
    _guard(exc)

with spec_helpers.shadow_features(features_dir, discovery,
                                  spec_helpers.TRACEABILITY) as shadow:
    shadow_out = shadow.root / 'spec/.a2h/requirements-index.json'
    forwarded = spec_helpers.rewrite_option(parsed.forward, '--project-root',
                                            str(shadow.root))
    forwarded = spec_helpers.rewrite_option(forwarded, '--out', str(shadow_out))
    replacements = spec_helpers.path_replacements(shadow.root, real_root) + (
        (str(shadow_out), str(real_out)),
        (str(shadow_out).replace('\\', '/'), str(real_out).replace('\\', '/')),
    )
    result = spec_helpers.run_helper(helper, forwarded)
    if result.returncode == 0:
        try:
            payload = spec_helpers.load_json(shadow_out)
            normalized, _stats = spec_helpers.validate_traceability_index(
                payload, discovery, shadow.aliases)
        except spec_helpers.ObjectContractError as exc:
            _guard(exc, result, shadow.aliases, replacements, exit_code=1)

if result.returncode != 0:
    spec_helpers.forward(result, aliases=shadow.aliases, replacements=replacements)
    raise SystemExit(result.returncode)

try:
    spec_helpers.validate_output_path(real_out, real_root, discovery)
    spec_helpers.write_index(real_out, normalized)
except (spec_helpers.ObjectContractError, spec_discovery.DiscoveryError) as exc:
    _guard(exc)
spec_helpers.forward(result, aliases=shadow.aliases, replacements=replacements)
raise SystemExit(0)
