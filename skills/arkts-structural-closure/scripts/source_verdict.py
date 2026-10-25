"""Original 1.5.2 convergence rules, including the high-level custom cap.

The standalone compiled loop_runner CLI has no custom-cap input. This compatibility
implementation is checked against that CLI at its default and against the original
structural_loop at every supported cap. No old verdict or finding is filtered.
"""
MAX_ITER = 8
STALLED_THRESHOLD = 2
REGRESSION_THRESHOLD = 1.5


def fail_count(value):
    return (value.get('audit_fail', 0) + value.get('wiring_repair_actions', 0) +
            value.get('handoff_escape_hatches', 0))


def fingerprint_key(values):
    # Keep original values and multiplicity. The type tags are only comparison
    # keys; integers still sort numerically and strings still sort lexically.
    def component(value):
        if isinstance(value, (int, float)):
            return (0, value)
        if isinstance(value, str):
            return (1, value)
        return (2, str(value))
    return tuple(sorted((tuple(item) for item in values),
                        key=lambda item: tuple(component(value) for value in item)))


def evaluate(history, current, max_iter=MAX_ITER):
    iteration = current['iter']
    count = fail_count(current)
    previous_count = None
    if count == 0:
        verdict, reason, escalation = ('CONVERGED', f'all checks pass at iteration {iteration}', 'NONE')
    elif iteration + 1 >= max_iter:
        verdict, reason, escalation = ('EXHAUSTED', f'hit MAX_ITER={max_iter} without converging; still {count} findings', 'MANUAL')
    else:
        previous = history[-1] if history else None
        previous_count = fail_count(previous) if previous is not None else None
        if previous_count is not None and previous_count > 0 and count > previous_count * REGRESSION_THRESHOLD:
            verdict, reason, escalation = ('REGRESSED', f'findings grew from {previous_count} → {count} (> 1.5× threshold); repair likely introduced new problems', 'ROLLED_BACK')
        elif previous is not None and fingerprint_key(current.get('fingerprint', [])) == fingerprint_key(previous.get('fingerprint', [])):
            key = fingerprint_key(current.get('fingerprint', []))
            sample = key[:4] if key else '<empty>'
            verdict, reason, escalation = ('STALLED', f'findings fingerprint unchanged for {STALLED_THRESHOLD} consecutive rounds ({sample}... × {len(key)} items)', 'MANUAL')
        else:
            verdict, reason, escalation = ('CONTINUE', f'{count} findings remain; dispatch repair worker for iter {iteration + 1}', 'NONE')
    result = {'verdict': verdict, 'reason': reason, 'escalation': escalation,
              'iteration': iteration, 'current_fail': count, 'prev_fail': previous_count}
    return result, 0 if verdict == 'CONVERGED' else 1 if verdict == 'CONTINUE' else 2
