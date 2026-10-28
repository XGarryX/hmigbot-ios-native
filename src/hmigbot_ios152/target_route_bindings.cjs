'use strict';
// Render-bound target facts. The caller supplies the selected official ETS program.
// No source edits, dynamic evaluation, SPEC aliases or runtime reachability claims.
function collect(api) {
  const {ts, checker, sources, selected, real, relative, anchor, official, decorated,
    component, builder, isCall, strip, id, name, symbol, declaration,
    directComponentBinding, baseCall, unknown, output, entered} = api;
  const resolvedKeys = new Set(), active = new Set(), concreteOwners = new Set(), registrations = [], pending = [];
  const key = n => { const a = anchor(n, 'identity'); return `${a.file}:${a.start_utf16}:${a.end_utf16}`; };
  const resolved = n => { if (n) resolvedKeys.add(key(n)); };
  const sameMethod = (d, c) => d && ts.isMethodDeclaration(d) && d.parent === c.owner && !!d.body;
  const member = (d, c) => d && ts.isPropertyDeclaration(d) && d.parent === c.owner;
  const context = (owner, instance, bindings = new Map(), guards = []) =>
    ({owner, source: owner.getSourceFile(), instance, bindings, guards});
  function origin(expr, c, seen = new Set()) {
    expr = strip(expr);
    const d = expr && declaration(expr, c);
    if (!d || d.ambiguous || seen.has(d)) return {expr, context: c};
    const value = c.bindings.get(d);
    if (!value) return {expr, context: c};
    return origin(value.expr, value.context, new Set([...seen, d]));
  }
  function callContext(fn, call, c) {
    const bindings = new Map(c.bindings);
    if (call.arguments?.some(arg => ts.isSpreadElement(arg))) return undefined;
    for (let i = 0; i < fn.parameters.length; i++) {
      const p = fn.parameters[i];
      if (!id(p.name) || p.dotDotDotToken) return undefined;
      const expr = call.arguments?.[i] || p.initializer;
      if (expr) bindings.set(p, {expr, context: c});
    }
    return {...c, bindings};
  }
  function callable(expr, c, call) {
    const value = origin(expr, c); expr = value.expr; c = value.context;
    if (!expr) return undefined;
    if (ts.isArrowFunction(expr) || ts.isFunctionExpression(expr) || ts.isBlock(expr))
      return {node: expr, body: ts.isBlock(expr) ? expr : expr.body, context: c};
    const d = declaration(expr, c);
    if (sameMethod(d, c)) {
      const next = call ? callContext(d, call, c) : c;
      return next ? {node: d, body: d.body, context: next} : undefined;
    }
    return undefined;
  }
  function enter(callableValue, chain, trail, fn) {
    if (!callableValue) return;
    const {node, body, context: c} = callableValue;
    if (trail.includes(node)) { unknown('recursive render/event binding', node, c); return; }
    const next = [...chain, anchor(node, builder(node) ? 'builder-declaration' : 'callback-declaration')];
    if (builder(node)) entered.add(node);
    resolved(node);
    fn(body, c, next, [...trail, node]);
  }
  function componentContext(d, call, c) {
    if (!selected.has(real(d.getSourceFile().fileName))) return undefined;
    const build = d.members.filter(m => ts.isMethodDeclaration(m) && name(m) === 'build' && m.body);
    if (build.length !== 1) return undefined;
    const args = call.arguments || [], literal = args.length === 1 && ts.isObjectLiteralExpression(strip(args[0])) ? strip(args[0]) : undefined;
    if (args.length && !literal) return undefined;
    if (literal?.properties.some(p => !(ts.isPropertyAssignment(p) || ts.isShorthandPropertyAssignment(p)) || !(id(p.name) || ts.isStringLiteral(p.name)))) return undefined;
    const next = context(d, `${c.instance}>${key(call)}`, new Map(), c.guards);
    for (const property of d.members.filter(ts.isPropertyDeclaration)) {
      const supplied = literal?.properties.filter(p => name(p) === name(property)) || [];
      if (supplied.length > 1) return undefined;
      if (supplied.length === 1) {
        const p = supplied[0]; next.bindings.set(property, {expr: ts.isShorthandPropertyAssignment(p) ? p.name : p.initializer, context: c});
      } else if (property.initializer && (decorated(property, 'BuilderParam') || decorated(property, 'Event'))) {
        next.bindings.set(property, {expr: property.initializer, context: next});
      }
    }
    const parameters = d.members.filter(p => ts.isPropertyDeclaration(p) && decorated(p, 'BuilderParam'));
    if (call.body && ts.isBlock(call.body) && parameters.length === 1 &&
        !(literal?.properties.some(p => name(p) === name(parameters[0]))))
      next.bindings.set(parameters[0], {expr: call.body, context: c});
    concreteOwners.add(d);
    return {context: next, build: build[0]};
  }
  function loopBody(node, c) {
    if (!official(node.expression, 'ForEach')) return undefined;
    const callback = strip(node.arguments?.[1]);
    return callback && (ts.isArrowFunction(callback) || ts.isFunctionExpression(callback))
      ? {node: callback, body: callback.body, context: c} : undefined;
  }
  function guarded(c, expression, branch) {
    return {...c, guards: [...c.guards, anchor(expression, 'conditional-render', {branch, runtime_value: 'unknown'})]};
  }
  function uniqueComponent(body, c, chain, trail) {
    const candidates = [], measured = [], conditions = [], loops = []; let incomplete = false;
    function visit(node, cc, links, seen) {
      if (!node || incomplete) return;
      measured.push(node);
      if (ts.isIfStatement(node)) {
        conditions.push(anchor(node.expression, 'conditional-render', {runtime_value: 'unknown'}));
        visit(node.thenStatement, guarded(cc, node.expression, 'then'), [...links, anchor(node.expression, 'conditional-render', {branch: 'then'})], seen);
        visit(node.elseStatement, guarded(cc, node.expression, 'else'), [...links, anchor(node.expression, 'conditional-render', {branch: 'else'})], seen); return;
      }
      if (ts.isVariableStatement(node)) return;
      if (ts.isFunctionDeclaration(node) || ts.isArrowFunction(node) || ts.isFunctionExpression(node)) { incomplete = true; return; }
      if (isCall(node)) {
        const expr = strip(node.expression);
        if (ts.isPropertyAccessExpression(expr) && isCall(expr.expression)) { visit(expr.expression, cc, links, seen); return; }
        if (official(expr, 'ForEach')) {
          const cb = loopBody(node, cc);
          if (!cb) { incomplete = true; return; }
          loops.push(anchor(node, 'symbolic-render-loop', {cardinality: 'unknown'}));
          visit(cb.body, cc, [...links, anchor(node, 'symbolic-render-loop', {cardinality: 'unknown'})], seen); return;
        }
        const d = declaration(expr, cc);
        if (d?.ambiguous) { incomplete = true; return; }
        if (d && component(d)) {
          if (!directComponentBinding(expr, d, cc)) { incomplete = true; return; }
          candidates.push({target: expr.text, target_declaration: anchor(d, 'target-declaration', {declaration_name: name(d)}),
            call_site: anchor(node, 'component-construction'), chain: [...links, anchor(node, 'component-construction', {target: expr.text})], guards: cc.guards});
          return;
        }
        const cb = callable(expr, cc, node);
        if (cb && builder(cb.node) || cb && (ts.isArrowFunction(cb.node) || ts.isFunctionExpression(cb.node) || ts.isBlock(cb.node))) {
          if (seen.includes(cb.node)) { incomplete = true; return; }
          if (builder(cb.node)) entered.add(cb.node);
          measured.push(cb.node);
          visit(cb.body, cb.context, [...links, anchor(node, 'builder-call'), anchor(cb.node, 'builder-declaration')], [...seen, cb.node]); return;
        }
        if (official(expr)) {
          if (node.body) visit(node.body, cc, [...links, anchor(node, 'builtin-render')], seen);
          return;
        }
        incomplete = true; return;
      }
      ts.forEachChild(node, child => visit(child, cc, links, seen));
    }
    visit(body, c, chain, trail);
    const identities = new Set(candidates.map(v => `${v.target}|${v.target_declaration.file}:${v.target_declaration.start_utf16}`));
    if (incomplete || identities.size !== 1) return {unknown: true, reason: incomplete ? 'unresolved render branch' : 'multiple/no static component targets', candidates};
    for (const node of measured) resolved(node);
    return {...candidates[0], conditionality: conditions, render_loops: loops,
      possible_instances: loops.length ? 'unknown' : candidates.length, all_constructions: candidates.map(v => v.call_site)};
  }
  const overlaySites = new Map();
  const overlayIdentity = row => `${row.source_file}|${row.source}|${row.line}|${row.api}`;
  function overlay(node, c, chain) {
    const prop = node.expression, ref = node.arguments?.[1];
    if (!ref || !['bindSheet', 'bindContentCover'].includes(prop.name.text) || !official(prop, prop.name.text)) return;
    const location = {source: name(c.owner), source_file: relative(c.source.fileName),
      line: anchor(prop.name, 'overlay-api').line, api: prop.name.text};
    const identity = overlayIdentity(location), observations = overlaySites.get(identity) || [];
    overlaySites.set(identity, observations);
    const observation = {node, context: c, seed: !c.instance.includes('>'), entry: decorated(c.owner, 'Entry')};
    observations.push(observation);
    const called = isCall(strip(ref)), target = called ? strip(ref).expression : ref;
    const cb = callable(target, c, called ? strip(ref) : undefined);
    if (!cb || !(builder(cb.node) || ts.isArrowFunction(cb.node) || ts.isFunctionExpression(cb.node) || ts.isBlock(cb.node))) {
      unknown('overlay instance has unresolved Builder binding', ref, c, {api: prop.name.text, instance: c.instance}); return;
    }
    if (builder(cb.node)) entered.add(cb.node);
    const next = [...chain, anchor(prop.name, 'overlay-binding', {api: prop.name.text}), anchor(ref, called ? 'builder-call' : 'builder-reference'), anchor(cb.node, 'builder-declaration')];
    const found = uniqueComponent(cb.body, cb.context, next, [cb.node]);
    if (found.unknown) { unknown('overlay has no unique resolved static component', ref, c, {api: prop.name.text, instance: c.instance, details: found.reason, candidate_targets: found.candidates.map(v => v.target)}); return; }
    resolved(ref); resolved(cb.node);
    const row = {source: name(c.owner), source_file: relative(c.source.fileName), api: prop.name.text,
      line: anchor(prop.name, 'overlay-api').line, call_site: anchor(prop.name, 'overlay-api'), target: found.target,
      target_declaration: found.target_declaration, chain: found.chain, conditions: found.conditionality,
      render_loops: found.render_loops, possible_instances: found.possible_instances, all_constructions: found.all_constructions,
      instance: c.instance, supplement: 'ets_ast'};
    observation.row = row;
  }
  const mutations = new Map();
  function reassigned(property) {
    if (mutations.has(property)) return mutations.get(property);
    let changed = false;
    function scan(node) {
      if (ts.isBinaryExpression(node) && node.operatorToken.kind >= ts.SyntaxKind.FirstAssignment && node.operatorToken.kind <= ts.SyntaxKind.LastAssignment && symbol(node.left)?.declarations?.includes(property)) changed = true;
      ts.forEachChild(node, scan);
    }
    scan(property.parent); mutations.set(property, changed); return changed;
  }
  function stackRef(expr, c, seen = new Set(), links = []) {
    expr = strip(expr);
    const d = expr && declaration(expr, c);
    if (!d || d.ambiguous || seen.has(d)) return undefined;
    // V1 @Prop copies object values; every intermediate member must also be
    // stable. A bound expression alone does not prove reference identity.
    if (reassigned(d) || decorated(d, 'Prop')) return undefined;
    const bound = c.bindings.get(d);
    if (bound) return stackRef(bound.expr, bound.context, new Set([...seen, d]), [...links, anchor(d, 'stack-parameter-binding')]);
    if (!member(d, c) || !ts.isPropertyAccessExpression(expr) || expr.expression.kind !== ts.SyntaxKind.ThisKeyword || decorated(d, 'Param') || decorated(d, 'Prop') || decorated(d, 'Link') || decorated(d, 'ObjectLink')) return undefined;
    const s = checker.getNonNullableType(checker.getTypeAtLocation(expr)).getSymbol?.();
    if (s?.getName() !== 'NavPathStack' || !(s.declarations || []).length || !s.declarations.every(n => api.officialFile(n.getSourceFile().fileName)) || reassigned(d)) return undefined;
    return {property: d, context: c, identity: `${key(d)}|${c.instance}`, links};
  }
  function register(node, c, chain) {
    const call = baseCall(node), ref = node.arguments?.[0];
    if (!official(call.expression, 'Navigation')) return;
    const stack = stackRef(call.arguments?.[0], c), cb = callable(ref, c);
    if (!stack || !cb || !builder(cb.node) || !cb.node.parameters.length || !id(cb.node.parameters[0].name)) return;
    entered.add(cb.node); resolved(cb.node);
    registrations.push({node, context: c, chain, stack, builder: cb.node, parameter: cb.node.parameters[0], site: anchor(node.expression.name, 'navDestination-binding')});
  }
  function events(node, c, chain) {
    const control = baseCall(node), first = callable(node.arguments?.[0], c);
    if (!first) return;
    const originControl = {context: c, node: control, binding: node.expression.name}, firstChain = [...chain, anchor(node.expression.name, 'onclick-binding')];
    const pendingStart = pending.length; let recursive = false;
    function visit(n, cc, links, trail, indirect = false) {
      if (!n) return false;
      if (ts.isBlock(n)) {
        for (const statement of n.statements) if (visit(statement, cc, links, trail, indirect)) return true;
        return false;
      }
      if (ts.isReturnStatement(n) || ts.isThrowStatement(n)) {
        if (n.expression) visit(n.expression, cc, links, trail, indirect);
        return true;
      }
      if (ts.isArrowFunction(n) || ts.isFunctionExpression(n) || ts.isFunctionDeclaration(n)) return;
      if (ts.isIfStatement(n)) {
        const stoppedThen = visit(n.thenStatement, guarded(cc, n.expression, 'then'), [...links, anchor(n.expression, 'event-guard', {branch: 'then'})], trail, indirect);
        const stoppedElse = visit(n.elseStatement, guarded(cc, n.expression, 'else'), [...links, anchor(n.expression, 'event-guard', {branch: 'else'})], trail, indirect); return !!stoppedThen && !!stoppedElse;
      }
      if (ts.isTryStatement(n) || ts.isConditionalExpression(n) ||
          ts.isBinaryExpression(n) && [ts.SyntaxKind.AmpersandAmpersandToken, ts.SyntaxKind.BarBarToken,
            ts.SyntaxKind.QuestionQuestionToken, ts.SyntaxKind.AmpersandAmpersandEqualsToken,
            ts.SyntaxKind.BarBarEqualsToken, ts.SyntaxKind.QuestionQuestionEqualsToken].includes(n.operatorToken.kind)) {
        unknown('conditional event expression requires triage', n, cc); return;
      }
      if (ts.isForStatement(n) || ts.isForOfStatement(n) || ts.isWhileStatement(n) || ts.isSwitchStatement(n)) { unknown('dynamic event control flow requires triage', n, cc); return; }
      if (isCall(n)) {
        const expr = strip(n.expression);
        if (ts.isPropertyAccessExpression(expr) && expr.name.text === 'pushPathByName') {
          const target = strip(n.arguments?.[0]);
          if (!official(expr, 'pushPathByName') || !target || !ts.isStringLiteral(target)) {
            if (expr.questionDotToken || n.questionDotToken) unknown('optional push has dynamic/nonofficial route call', n, cc); return;
          }
          const stack = stackRef(expr.expression, cc);
          if (!stack) { if (expr.questionDotToken || n.questionDotToken) unknown('optional push has unbound/mutable/nonofficial stack instance', n, cc, {instance: cc.instance}); return; }
          if (links.some(link => link.kind === 'event-guard')) {
            if (expr.questionDotToken || n.questionDotToken) unknown('guarded optional event push requires triage', n, cc, {instance: cc.instance}); return;
          }
          pending.push({node: n, context: cc, stack, target: target.text, originControl, indirect,
            optionalTokens: [expr.questionDotToken && anchor(expr.questionDotToken, 'optional-token', {token_text: expr.questionDotToken.getText(), placement: 'receiver'}),
              n.questionDotToken && anchor(n.questionDotToken, 'optional-token', {token_text: n.questionDotToken.getText(), placement: 'call'})].filter(Boolean),
            optional: !!expr.questionDotToken || !!n.questionDotToken, chain: [...links, anchor(n, 'navpath-push')], guards: cc.guards});
          return;
        }
        const d = declaration(expr, cc), value = origin(expr, cc), cb = callable(expr, cc, n);
        if (cb && (sameMethod(cb.node, cb.context) || ts.isArrowFunction(cb.node) || ts.isFunctionExpression(cb.node))) {
          if (trail.includes(cb.node)) { recursive = true; unknown('recursive event method binding', n, cc); return; }
          const forwarded = value.context !== cc || !!cc.bindings.get(d);
          resolved(n);
          visit(cb.body, cb.context, [...links, anchor(n, forwarded ? 'event-parameter-invoke' : 'event-method-call'), anchor(cb.node, 'event-method-declaration')], [...trail, cb.node], indirect || forwarded || ts.isMethodDeclaration(cb.node));
          return;
        }
        // Calls with arbitrary callback arguments are not event execution proof.
        return;
      }
      ts.forEachChild(n, child => visit(child, cc, links, trail, indirect));
    }
    visit(first.body, first.context, firstChain, [first.node], ts.isMethodDeclaration(first.node) || first.context !== c);
    if (recursive) pending.splice(pendingStart);
  }
  function walk(node, c, chain, trail) {
    if (!node || ts.isArrowFunction(node) || ts.isFunctionExpression(node) || ts.isFunctionDeclaration(node) || ts.isVariableStatement(node)) return;
    if (ts.isIfStatement(node)) {
      walk(node.thenStatement, guarded(c, node.expression, 'then'), [...chain, anchor(node.expression, 'conditional-render', {branch: 'then'})], trail);
      walk(node.elseStatement, guarded(c, node.expression, 'else'), [...chain, anchor(node.expression, 'conditional-render', {branch: 'else'})], trail); return;
    }
    if (isCall(node)) {
      const expr = strip(node.expression);
      if (ts.isPropertyAccessExpression(expr) && isCall(expr.expression)) {
        if (official(expr, 'navDestination')) register(node, c, chain);
        if (official(expr, 'onClick')) events(node, c, chain);
        overlay(node, c, chain);
        walk(expr.expression, c, chain, trail); return;
      }
      if (official(expr, 'ForEach')) {
        const cb = loopBody(node, c);
        if (!cb) { unknown('official ForEach render callback unresolved', node, c); return; }
        resolved(node);
        enter(cb, [...chain, anchor(node, 'symbolic-render-loop', {cardinality: 'unknown'})], trail, walk); return;
      }
      const d = declaration(expr, c);
      if (d && !d.ambiguous && component(d) && directComponentBinding(expr, d, c)) {
        const next = componentContext(d, node, c);
        if (!next) { unknown('component instance bindings unresolved/outside target scope', node, c); return; }
        const identity = `${key(d)}|${c.instance}`;
        if (active.has(identity) || trail.includes(d)) { unknown('recursive component render chain', node, c); return; }
        active.add(identity);
        walk(next.build.body, next.context, [...chain, anchor(node, 'component-instance'), anchor(next.build, 'component-build')], [...trail, d]);
        active.delete(identity); resolved(node); return;
      }
      const cb = callable(expr, c, node);
      if (cb && (builder(cb.node) || ts.isArrowFunction(cb.node) || ts.isFunctionExpression(cb.node) || ts.isBlock(cb.node))) {
        resolved(node); enter(cb, [...chain, anchor(node, 'builder-call')], trail, walk); return;
      }
      if (ts.SyntaxKind[node.kind] === 'EtsComponentExpression' && official(expr)) walk(node.body, c, [...chain, anchor(node, 'builtin-render')], trail);
      return;
    }
    ts.forEachChild(node, child => walk(child, c, chain, trail));
  }
  for (const source of sources.values()) for (const owner of source.statements.filter(component)) {
    const builds = owner.members.filter(m => ts.isMethodDeclaration(m) && name(m) === 'build' && m.body);
    if (builds.length === 1) walk(builds[0].body, context(owner, `seed:${key(owner)}`), [anchor(builds[0], 'build-entry')], [owner]);
  }
  // A call site has one original wire row. Resolve all concrete instances
  // together; neither traversal order nor an uninstantiated seed selects it.
  output.overlayBindings = output.overlayBindings.filter(row => !overlaySites.has(overlayIdentity(row)));
  for (const observations of overlaySites.values()) {
    const concrete = observations.filter(value => !value.seed);
    const relevant = concrete.length ? observations.filter(value => !value.seed || value.entry) : observations;
    const rows = relevant.filter(value => value.row).map(value => value.row);
    const targets = new Set(rows.map(row => `${row.target}|${row.target_declaration.file}:${row.target_declaration.start_utf16}`));
    if (rows.length !== relevant.length || targets.size !== 1) {
      const first = relevant[0];
      unknown('overlay call site has ambiguous/unresolved concrete instance targets', first.node, first.context,
        {instances: relevant.map(value => ({instance: value.context.instance, target: value.row?.target || null}))});
      continue;
    }
    output.overlayBindings.push({...rows[0], instance_witnesses: rows});
  }
  output.eventBindings ||= [];
  const pushKeys = new Set(output.optionalPushes.map(row => `${row.call_site.file}:${row.call_site.start_utf16}:${row.call_site.end_utf16}`));
  const emitted = new Set();
  for (const p of pending) {
    if (!p.context.instance.includes('>') && !decorated(p.context.owner, 'Entry') && concreteOwners.has(p.context.owner)) {
      if (p.optional) unknown('independent seed push excluded in favour of concrete component instances', p.node, p.context,
        {instance: p.context.instance});
      continue;
    }
    const found = [];
    for (const r of registrations.filter(r => r.stack.identity === p.stack.identity)) {
      const parameterSymbol = symbol(r.parameter.name);
      function branches(node) {
        if (!node) return;
        if (ts.isIfStatement(node)) {
          const condition = strip(node.expression);
          if (ts.isBinaryExpression(condition) && condition.operatorToken.kind === ts.SyntaxKind.EqualsEqualsEqualsToken) {
            const left = strip(condition.left), right = strip(condition.right);
            if (id(left) && symbol(left) === parameterSymbol && ts.isStringLiteral(right) && right.text === p.target || id(right) && symbol(right) === parameterSymbol && ts.isStringLiteral(left) && left.text === p.target) {
              const target = uniqueComponent(node.thenStatement, r.context, [...r.chain, r.site, anchor(node, 'literal-route-branch')], [r.builder]);
              if (!target.unknown) found.push({route_name: p.target, target: target.target, target_declaration: target.target_declaration,
                stack_property: anchor(r.stack.property, 'navigation-stack-property'), binding: r.site, builder: anchor(r.builder, 'destination-builder'),
                instance: r.stack.context.instance, stack_identity: r.stack.identity, chain: target.chain, conditions: target.conditionality, supplement: 'ets_ast'});
            }
          }
          branches(node.elseStatement); return;
        }
        if (!ts.isArrowFunction(node) && !ts.isFunctionExpression(node) && !ts.isFunctionDeclaration(node)) ts.forEachChild(node, branches);
      }
      branches(r.builder.body);
    }
    const unique = [...new Map(found.map(row => [`${row.binding.file}:${row.binding.start_utf16}|${row.target}`, row])).values()];
    if (unique.length !== 1) {
      if (p.optional) unknown('optional push has missing/ambiguous literal navDestination registration for its stack instance', p.node, p.context,
        {route_name: p.target, registration_count: unique.length, instance: p.context.instance, stack_identity: p.stack.identity});
      continue;
    }
    const registration = unique[0], identity = `${key(p.node)}|${p.context.instance}|${p.stack.identity}`;
    if (emitted.has(identity)) continue; emitted.add(identity);
    const pushSite = anchor(p.node, 'optional-navpath-push'), control = anchor(p.originControl.node, 'trigger-control');
    const row = {source: name(p.context.owner), source_file: relative(p.context.source.fileName), target: p.target,
      line: p.indirect ? pushSite.line : control.line, control_site: control, onclick_binding: anchor(p.originControl.binding, 'onclick-binding'),
      call_site: pushSite, push_call_site: pushSite, optional_token: p.optionalTokens[0], optional_tokens: p.optionalTokens,
      stack_property: anchor(p.stack.property, 'navigation-stack-property'), stack_binding_chain: p.stack.links,
      chain: p.chain, registration, indirect: p.indirect, instance: p.context.instance, stack_identity: p.stack.identity,
      guards: p.guards, optional: p.optional, supplement: 'ets_ast'};
    output.eventBindings.push(row);
    if (p.optional && !pushKeys.has(key(p.node))) {
      pushKeys.add(key(p.node)); output.optionalPushes.push(row); output.registrations.push(registration); resolved(p.node);
    }
  }
  // Keep a legacy SDK candidate only as provenance. The active record must
  // use the current concrete-instance proof, including its registration chain.
  const provedOptional = new Set(output.eventBindings.filter(row => row.optional)
    .map(row => `${row.call_site.file}:${row.call_site.start_utf16}:${row.call_site.end_utf16}`));
  output.optionalPushes = output.optionalPushes.flatMap(row => {
    const identity = `${row.call_site.file}:${row.call_site.start_utf16}:${row.call_site.end_utf16}`;
    if (provedOptional.has(identity)) {
      const witnesses = output.eventBindings.filter(value => value.optional && `${value.call_site.file}:${value.call_site.start_utf16}:${value.call_site.end_utf16}` === identity);
      const proof = witnesses[0];
      return [{...proof, instance_witnesses: witnesses.map(value => ({...value})),
        registration_variants: witnesses.map(value => value.registration),
        line_semantics: 'SDK push/trigger anchor only; original-engine measurement supplies wire line',
        ...(row !== proof ? {legacy_sdk_candidate: row} : {})}];
    }
    output.unknowns.push({...row.call_site, kind: 'unresolved', source: row.source,
      reason: 'optional push lacks current render-bound stable-stack proof'});
    return [];
  });
  output.legacyRegistrationCandidates = output.registrations;
  output.registrations = [...new Map(output.eventBindings.map(row => {
    const value = row.registration;
    return [`${value.binding.file}:${value.binding.start_utf16}|${value.stack_identity}|${value.target}`, value];
  })).values()];
  return {resolvedKeys};
}
module.exports = {collect};
