"""One optional, human-readable progress note inside the configured target.

This is a derived view of actual calls, never a source/plan contract or a gate.
It does not select a project, create another state ledger, or use CODEX_HOME.
"""
from datetime import datetime
from pathlib import Path
import sys
import time

from .core import MigrationError, atomic_write, read_json, safe_child

REPORT = 'spec/reports/ios-progress.md'
START = '<!-- hmigbot-ios:progress:start -->'
END = '<!-- hmigbot-ios:progress:end -->'
STAGES = {
    'init': 'init', 'init-environment': 'init', 'repair-permissions': 'init',
    **dict.fromkeys(('source-index', 'source-refresh', 'source-analysis', 'facts',
        'literals', 'product-literals', 'harness-init', 'import-legacy', 'expertise-plan',
        'expertise-review', 'mcp-query', 'manifest-evaluate', 'conditional-capture',
        'spec-scaffold', 'spec-authoring', 'spec-upgrade', 'source-check'), 'spec'),
    **dict.fromkeys(('plan-ir', 'replan', 'recover-blocked'), 'plan'),
    **dict.fromkeys(('execution-contract', 'next-batch', 'land-results', 'build'), 'execute'),
    **dict.fromkeys(('resource-delta-init', 'resource-delta-submit',
                    'resource-delta-merge', 'resource-delta-recover'), 'execute'),
    **dict.fromkeys(('harness-check', 'behavior-check', 'verify-report'), 'verify'),
    'gate-artifacts': 'report', 'migration-report': 'report', 'spec-summary': 'report',
    'ui-ios-run': 'verify', 'ui-harmony-run': 'verify', 'ui-pair': 'verify',
    'ui-harmony-prepare': 'verify',
    'ui-repair-run': 'verify',
    'ui-delivery-draft': 'plan', 'ui-delivery-consume': 'execute',
}


def records_command(args):
    if not getattr(args, 'project', None) or args.command not in STAGES:
        return False
    if any(getattr(args, key, False) for key in ('report_only', 'plan_only', 'check')):
        return False
    if args.command == 'init-environment':
        return args.prepare
    if args.command in {'execution-contract', 'spec-upgrade', 'ui-delivery-draft'}:
        return bool(args.apply)
    if args.command == 'spec-scaffold':
        return bool(args.apply or args.output)
    if args.command in {'spec-authoring', 'spec-summary', 'migration-report'}:
        return bool(args.output)
    return True


def _text(value):
    return str(value).replace('\r', ' ').replace('\n', ' ').replace('|', '\\|')


class ProjectProgress:
    def __init__(self, args):
        self.project = Path(args.project) if getattr(args, 'project', None) else None
        self.command = args.command
        self.enabled = records_command(args)
        self.started = time.monotonic()
        self.warning_shown = False
        self.counters = {}
        self.measurement_token = None
        self.measurement_finished = False

    def _path(self):
        project = self.project.resolve() if self.project is not None else None
        if not project or not project.is_dir() or project in {Path('/'), Path.home()}:
            return None
        runtime = Path(__file__).resolve().parents[2]
        if project == runtime or project.is_relative_to(runtime):
            return None
        config = project / '.migbot/config.json'
        if not config.is_file():
            return None  # init writes its first note only after configure succeeds.
        config = read_json(config)
        if not isinstance(config, dict) or config.get('source_platform') != 'ios' or not config.get('ios'):
            return None
        source = Path(config['ios'])
        source = (source if source.is_absolute() else project / source).resolve()
        if source == project or source.is_relative_to(project) or project.is_relative_to(source):
            return None
        declared = Path(config.get('harmonyos') or project)
        declared = (declared if declared.is_absolute() else project / declared).resolve()
        if declared != project:
            return None
        for name in ('spec', 'spec/reports', REPORT):
            if (project / name).is_symlink():
                raise MigrationError('Progress note cannot follow a symlink: ' + name)
        self.project = project
        return safe_child(project, REPORT)

    def record(self, status, result=None, *, exit_code=None):
        if not self.enabled:
            return
        try:
            path = self._path()
            if path is None:
                return
            # Metrics are derived observations; failure cannot alter the actual
            # command, and read-only commands never reach this branch.
            try:
                from .execution_measurements import observe_start, observe_end
                category = ('build' if self.command == 'build' else 'merge'
                            if self.command in {'resource-delta-merge', 'resource-delta-recover'} else 'work')
                if not self.measurement_finished and self.measurement_token is None and status == 'running':
                    self.measurement_token = observe_start(self.project, STAGES[self.command], self.command, category)
                if self.measurement_token is not None and not self.measurement_finished and exit_code is not None:
                    observe_end(self.project, self.measurement_token, status, exit_code=exit_code)
                    self.measurement_finished = True
            except (MigrationError, OSError, ValueError, TypeError, KeyError) as exc:
                print('Measurement unavailable (original result unchanged): ' + str(exc), file=sys.stderr)
            result = result if isinstance(result, dict) else {}
            counters = result.get('progress', result)
            self.counters.update({key: counters[key] for key in
                ('total', 'completed', 'failed', 'blocked', 'current') if key in counters})
            lines = [START, '# iOS → HarmonyOS 转换进度', '',
                '- 更新：' + datetime.now().astimezone().isoformat(timespec='seconds'),
                '- 当前阶段：' + STAGES[self.command],
                '- 实际调用：`' + self.command + '`',
                '- 本次调用状态：' + _text(status),
                '- 本次调用耗时：' + str(round(time.monotonic() - self.started, 2)) + ' 秒']
            if exit_code is not None:
                lines.append('- 实际退出码：' + str(exit_code))
            if self.counters:
                lines += ['', '本次调用的步骤计数（不代表整个应用完成率）：', '']
                lines += ['- ' + key + '：' + _text(self.counters[key]) for key in
                          ('total', 'completed', 'failed', 'blocked', 'current') if key in self.counters]
            if result.get('error'):
                lines += ['', '当前问题：' + _text(result['error'])]
            stages = result.get('stages')
            if isinstance(stages, list) and stages:
                lines += ['', '已实际调用的子步骤：', '']
                for stage in stages:
                    if isinstance(stage, dict):
                        lines.append('- ' + _text(stage.get('name', 'unknown')) + '：' + _text(stage.get('status', 'unknown')))
            references = ('spec/reports/derived/source-analysis.json',
                          'spec/reports/init-environment.json', 'spec/.a2h/open-findings.json',
                          'spec/migration-report.md', 'spec/reports/ios-ui-preflight.json',
                          'spec/reports/ios-ui-pair.json')
            found = []
            for name in references:
                try:
                    if safe_child(self.project, name).is_file():
                        found.append(name)
                except MigrationError:
                    continue  # An unrelated old link cannot prevent progress reporting.
            if found:
                lines += ['', '项目内已有证据（历史文件需按原协议检查是否仍有效）：', '']
                for name in found:
                    # The note lives two levels below the target root.
                    lines.append('- [' + name + '](../../' + name + ')')
            next_steps = result.get('next')
            if not isinstance(next_steps, list) or not next_steps:
                next_steps = (['等待当前调用结果；不要重复派发同一工作。'] if status == 'running' else
                              ['先处理本次错误，核对项目内保留的原始证据，再恢复或重跑本命令。']
                              if exit_code not in (None, 0) else
                              ['按原阶段合同和调度结果继续；本命令完成不代表应用已通过生成、编译或行为验收。'])
            lines += ['', '下一步 / 恢复条件：', ''] + ['- ' + _text(item) for item in next_steps]
            lines += ['', '本文件仅用于查找进度，不批准迁移、不改变原账本，不作为门禁或正式输入。', END]
            section = '\n'.join(lines) + '\n'
            old = path.read_text(encoding='utf-8') if path.exists() else ''
            if START in old or END in old:
                if old.count(START) != 1 or old.count(END) != 1 or old.index(END) < old.index(START):
                    raise MigrationError('Progress note markers are ambiguous; user text retained')
                left, rest = old.split(START, 1)
                _, right = rest.split(END, 1)
                section = left + section.rstrip('\n') + right
            elif old:
                section = old + ('' if old.endswith('\n') else '\n') + '\n' + section
            atomic_write(path, section.encode('utf-8'))
        except (MigrationError, OSError, ValueError, TypeError, KeyError) as exc:
            if not self.warning_shown:
                self.warning_shown = True
                try:
                    print('Progress note unavailable (original command result unchanged): ' + str(exc), file=sys.stderr)
                except (OSError, UnicodeError):
                    pass
