"""One source-visible rule for discovering feature specification documents.

The divergence and traceability helpers ship as compiled binaries, so their
filename filters cannot be audited or patched here.  This module is the single
Python definition of which Markdown files carry feature specifications.  It is
used by the two gate wrappers and mirrors the rule already implemented by
``artifact_contract._primary_feature`` and ``native_authoring._inventory``:

* the stable identity is the ``F<digits>`` prefix of the file stem;
* a main document is an ``F<digits>...`` ``.md`` file whose stem does not carry
  an extra dot-separated addendum suffix;
* an addendum is ``F<digits>[-_]<name>.<slug>.md`` and belongs to the main
  document with the same F-ID; it never introduces a new F-ID;
* Unicode names such as ``F001-账号与引导.md`` are ordinary names, not aliases.

The rule is intentionally a superset of the helpers' historical ASCII-only
filter: ``F001-account.md``, ``F001_Account.md`` and ``F001-账号与引导.md`` are
all main documents of feature ``F001``.  The wrappers keep the original helper
as the implementation of its own rules and add this rule as a counting
contract around it.

This module only reads directory entries and Markdown text.  It never renames,
moves or writes project files.  Duplicate identities, orphan addenda and AC
identifiers that do not belong to their document are reported as errors
instead of being silently dropped.
"""
from __future__ import annotations
from .core import trusted_system_alias

from dataclasses import dataclass
import re
from pathlib import Path

# Same suffix rule as artifact_contract._primary_feature / native_authoring.
_ADDENDUM = re.compile(r'^(?P<id>F\d+)[-_].+\.(?P<slug>[^.\\/]+)\.md$')
_FEATURE_PREFIX = re.compile(r'^(?P<id>F\d+)')
_AC_ID = re.compile(r'^F\d+-AC\d+$')


class DiscoveryError(ValueError):
    """A document set that cannot be turned into a trustworthy object set."""

    def __init__(self, code: str, message: str):
        super().__init__('%s: %s' % (code, message))
        self.code = code
        self.detail = message


def reject_links(path: Path) -> None:
    """Inspect the lexical path before resolve can hide a link or junction."""
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if (part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction())) and not trusted_system_alias(part):
            raise DiscoveryError('INPUT_LINK', 'materialize linked input before gating: %s' % part)


@dataclass(frozen=True)
class FeatureDocument:
    """A discovered feature Markdown file and its stable identity."""

    feature_id: str
    name: str
    path: Path
    kind: str  # 'main' or 'addendum'
    slug: str | None = None

    @property
    def is_main(self) -> bool:
        return self.kind == 'main'


@dataclass(frozen=True)
class Discovery:
    """The closed set of feature documents under one features directory."""

    spec_dir: Path
    documents: tuple[FeatureDocument, ...]
    mains: tuple[FeatureDocument, ...]
    addenda: tuple[FeatureDocument, ...]

    def main_ids(self) -> tuple[str, ...]:
        return tuple(document.feature_id for document in self.mains)

    def main_by_id(self) -> dict[str, FeatureDocument]:
        return {document.feature_id: document for document in self.mains}

    def addenda_for(self, feature_id: str) -> tuple[FeatureDocument, ...]:
        return tuple(document for document in self.addenda if document.feature_id == feature_id)


def classify_name(name: str) -> FeatureDocument | None:
    """Return the feature document identity of a file name, or ``None``.

    The function is pure so callers and tests can compare the rule with
    ``artifact_contract._primary_feature`` without touching the filesystem.
    Files without the uppercase ``F<digits>`` prefix and files that are not
    Markdown are ignored; that matches the original helpers' scope.
    """
    if not name.endswith('.md'):
        return None
    prefix = _FEATURE_PREFIX.match(name)
    if prefix is None:
        return None
    addendum = _ADDENDUM.match(name)
    if addendum is not None:
        return FeatureDocument(feature_id=addendum['id'], name=name, path=Path(name),
                               kind='addendum', slug=addendum['slug'])
    return FeatureDocument(feature_id=prefix['id'], name=name, path=Path(name), kind='main')


def discover(spec_dir: Path, *, allow_empty: bool = False) -> Discovery:
    """Classify every feature document under ``spec_dir`` and validate IDs.

    ``allow_empty`` is the explicit, auditable exception for a source scope
    that provably has no feature documents.  Without it an empty or missing
    directory raises ``ZERO_OBJECTS`` instead of passing on zero objects.
    """
    spec_dir = Path(spec_dir)
    reject_links(spec_dir)
    if not spec_dir.is_dir():
        raise DiscoveryError('SPEC_DIR_MISSING', '%s is not a directory' % spec_dir)

    mains: dict[str, FeatureDocument] = {}
    addenda: dict[tuple[str, str], FeatureDocument] = {}
    documents: list[FeatureDocument] = []
    for path in sorted(spec_dir.iterdir(), key=lambda item: item.name):
        reject_links(path)
        if not path.is_file():
            continue
        found = classify_name(path.name)
        if found is None:
            continue
        document = FeatureDocument(feature_id=found.feature_id, name=found.name,
                                   path=path, kind=found.kind, slug=found.slug)
        if document.is_main:
            previous = mains.get(document.feature_id)
            if previous is not None:
                raise DiscoveryError(
                    'DUPLICATE_FEATURE_ID',
                    '%s appears in %s and %s' % (document.feature_id, previous.name, document.name))
            mains[document.feature_id] = document
        else:
            key = (document.feature_id, document.slug or '')
            previous = addenda.get(key)
            if previous is not None:
                raise DiscoveryError(
                    'DUPLICATE_ADDENDUM',
                    '%s.%s appears in %s and %s'
                    % (document.feature_id, document.slug, previous.name, document.name))
            addenda[key] = document
        documents.append(document)

    for (feature_id, slug), document in addenda.items():
        if feature_id not in mains:
            raise DiscoveryError(
                'ORPHAN_ADDENDUM',
                '%s (%s.%s) has no main document for %s'
                % (document.name, feature_id, slug, feature_id))

    if not mains and not allow_empty:
        raise DiscoveryError(
            'ZERO_OBJECTS',
            'no main F<digits> document in %s; pass --allow-empty only for a proven '
            'not-applicable source scope' % spec_dir)

    return Discovery(spec_dir=spec_dir, documents=tuple(documents),
                     mains=tuple(mains[key] for key in sorted(mains)),
                     addenda=tuple(addenda[key] for key in sorted(addenda)))


def read_document(document: FeatureDocument) -> str:
    reject_links(document.path)
    try:
        return document.path.read_text(encoding='utf-8-sig')
    except (OSError, UnicodeDecodeError) as exc:
        raise DiscoveryError('DOCUMENT_UNREADABLE', '%s: %s' % (document.name, exc)) from exc


def acceptance_documents(discovery: Discovery) -> dict[FeatureDocument, list[tuple[str, str]]]:
    """Stable AC identities per document, with prefix and duplicate checks.

    The AC parser is the formal spec gate's ``spec_contract.acceptance`` so
    every consumer counts the same authored lines.  Addenda are included in
    identity checks but not in the helper parity/index counts: the original
    helpers only index main documents, and this wrapper does not invent a
    second AC set. Each main must contain at least one authored AC;
    ``--allow-empty`` only permits a scope with no main documents at all.
    """
    from .spec_contract import acceptance

    result: dict[FeatureDocument, list[tuple[str, str]]] = {}
    seen: dict[str, str] = {}
    for document in discovery.documents:
        items = acceptance(read_document(document))
        if document.is_main and not items:
            raise DiscoveryError('ZERO_ACCEPTANCE_CRITERIA',
                                 '%s is a main document with no authored ACs' % document.name)
        for ac_id, body in items:
            if not _AC_ID.match(ac_id):
                raise DiscoveryError('MALFORMED_AC_ID', '%s: %s' % (document.name, ac_id))
            if not ac_id.startswith(document.feature_id + '-AC'):
                raise DiscoveryError(
                    'MISMATCHED_AC_ID',
                    '%s: %s does not belong to %s' % (document.name, ac_id, document.feature_id))
            previous = seen.get(ac_id)
            if previous is not None:
                raise DiscoveryError(
                    'DUPLICATE_AC_ID', '%s in %s and %s' % (ac_id, previous, document.name))
            seen[ac_id] = document.name
        result[document] = items
    return result


def divergence_counts(
        discovery: Discovery,
        acceptance: dict[FeatureDocument, list[tuple[str, str]]] | None = None) -> dict[str, int]:
    """Expected helper summary: mains plus parity/divergence AC classification.

    The compiled helper classifies an AC as divergence when its authored body
    carries an ASCII ``决:`` anchor and as parity when it carries an ASCII
    ``源:`` anchor and no ``决:`` anchor.  Addenda do not enter these counts.
    """
    if acceptance is None:
        acceptance = acceptance_documents(discovery)
    parity = divergence = 0
    for document in discovery.mains:
        for _, body in acceptance[document]:
            if '决:' in body:
                divergence += 1
            elif '源:' in body:
                parity += 1
    return {'mains': len(discovery.mains), 'parity': parity, 'divergence': divergence}


@dataclass(frozen=True)
class RequirementExpectation:
    """One stable AC identity that the traceability index must contain."""

    requirement_id: str
    feature_id: str
    document: FeatureDocument


def expected_requirements(
        discovery: Discovery,
        acceptance: dict[FeatureDocument, list[tuple[str, str]]] | None = None
) -> tuple[RequirementExpectation, ...]:
    """Main-document AC identities in document order (the helper's scope)."""
    if acceptance is None:
        acceptance = acceptance_documents(discovery)
    expected: list[RequirementExpectation] = []
    for document in discovery.mains:
        for ac_id, _ in acceptance[document]:
            expected.append(RequirementExpectation(ac_id, document.feature_id, document))
    return tuple(expected)
