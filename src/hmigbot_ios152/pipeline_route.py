"""Prepare fresh pipeline measurements and the optional native binding input.

Unfinished transaction journals are checked before pipeline measurement can
write. Missing binding declarations do not run the optional binding projection.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


_JOURNALS = 'spec/execution/autofix-log/native-icon-input/*/pipeline-transactions/*/transaction.json'
_CLEAR = frozenset(('committed', 'rolled_back'))
_DECLARATION = 'spec/baseline/ui/target-binding-projections.json'


class PipelineRoutingError(RuntimeError):
    def __init__(self, message, exit_code):
        super().__init__(message)
        self.exit_code = exit_code


def check_unfinished(project):
    """Only read journal paths and statuses; do not recover or import adapters."""
    try:
        for path in sorted(Path(project).glob(_JOURNALS)):
            try:
                record = json.loads(path.read_bytes())
                status = record.get('status') if isinstance(record, dict) else None
            except (OSError, ValueError, TypeError):
                status = None
            if status not in _CLEAR:
                raise PipelineRoutingError(
                    'Unfinished pipeline transaction requires explicit recovery: ' + str(path), 3)
    except OSError as error:
        raise PipelineRoutingError('Cannot inspect pipeline transaction journals: ' + str(error), 3) from error


def prepare_runner(argv):
    """Keep non-pipeline routing; measure native and visible-source orphans together."""
    if not argv or argv[0] != 'iterate' or '--help' in argv or '-h' in argv:
        return None
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--mode')
    parser.add_argument('--project-root')
    args, _ = parser.parse_known_args(argv[1:])
    if args.mode != 'pipeline' or not args.project_root:
        return None
    project = Path(args.project_root).resolve()
    if not project.is_dir():
        return None  # The unchanged CLI owns ordinary argument validation.
    check_unfinished(project)
    path = project / _DECLARATION
    try:
        path.lstat()
    except FileNotFoundError:
        try:
            from .pipeline_adapter import make_runner
            return make_runner()
        except Exception as error:
            raise PipelineRoutingError('Cannot prepare native pipeline adapter: ' + str(error), 3) from error
    except OSError as error:
        raise PipelineRoutingError('Cannot inspect native binding declarations: ' + str(error), 2) from error
    # Neither module is loaded when the formal input is absent. Import errors
    # are tool failures; they must not silently select the original engine.
    try:
        from .binding_projection import load_declarations, ProjectionInputError
    except Exception as error:
        raise PipelineRoutingError('Cannot load native binding input reader: ' + str(error), 3) from error
    try:
        declaration = load_declarations(project)
        if declaration is None:
            raise ProjectionInputError('Native binding declaration disappeared during input selection')
    except ProjectionInputError as error:
        raise PipelineRoutingError(str(error), 2) from error
    except Exception as error:
        raise PipelineRoutingError('Native binding input reader failed: ' + str(error), 3) from error
    try:
        from .pipeline_adapter import make_runner
        return make_runner(declaration)
    except Exception as error:
        raise PipelineRoutingError('Cannot prepare native pipeline adapter: ' + str(error), 3) from error
