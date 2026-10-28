'use strict';
// Official ETS AST facts only. No product source rewriting or SPEC input.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const output = {runId: input.runId, valid: false, tabGroups: [], overlayBindings: [], optionalPushes: [], registrations: [], unknowns: [], deadBuilders: [],
  scope: 'official ETS render/instance binding facts; original Tab policy; no device/reachability verdict'};
const digest = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const need = (value, message) => { if (!value) throw new Error(message); return value; };
try {
  const ts = require(input.parserModule), parserEntry = require.resolve(input.parserModule);
  let loader = path.dirname(parserEntry);
  while (path.basename(loader) !== 'ets-loader' && path.dirname(loader) !== loader) loader = path.dirname(loader);
  need(path.basename(loader) === 'ets-loader' && typeof ts.ScriptKind.ETS === 'number', 'Selected parser is not official ETS');
  const sdk = path.resolve(loader, '../..'), config = path.join(loader, 'tsconfig.json');
  const raw = JSON.parse(fs.readFileSync(config, 'utf8')).compilerOptions;
  need(raw.ets && typeof ts.convertCompilerOptionsFromJson === 'function', 'Official ETS compiler configuration unavailable');
  const converted = ts.convertCompilerOptionsFromJson(raw, loader);
  const options = {...converted.options, ets: raw.ets, noEmit: true, allowNonTsExtensions: true, strictNullChecks: true};
  const files = input.files.map(file => path.resolve(file)), selected = new Set(files.map(file => fs.realpathSync(file)));
  const roots = [sdk], companion = path.resolve(sdk, '../../hms/ets');
  if (fs.existsSync(companion)) roots.push(companion);
  const real = file => fs.realpathSync(file);
  const under = (file, root) => { const rel = path.relative(real(root), real(file)); return rel !== '..' && !rel.startsWith('..' + path.sep) && !path.isAbsolute(rel); };
  const officialFile = file => file.endsWith('.d.ts') && roots.some(root => under(file, root));
  let custom;
  const host = ts.createCompilerHost(options), previousSource = host.getSourceFile;
  host.getSourceFile = (file, version, onError, fresh) => file.endsWith('.ets') && fs.existsSync(file)
    ? ts.createSourceFile(file, fs.readFileSync(file, 'utf8'), version, true, ts.ScriptKind.ETS, custom ? custom.forFile(file) : options)
    : previousSource(file, version, onError, fresh);
  function resolveModule(name, containing) {
    const candidates = name.startsWith('.')
      ? [name, name + '.ets', name + '.d.ets', name + '.ts', name + '.d.ts', path.join(name, 'index.ets')].map(value => path.resolve(path.dirname(containing), value))
      : roots.flatMap(root => ['kits', 'api'].map(dir => path.join(root, dir, name + '.d.ts')));
    const file = candidates.find(file => fs.existsSync(file) && fs.statSync(file).isFile());
    return file ? {resolvedFileName: file, extension: file.endsWith('.d.ts') ? ts.Extension.Dts : ts.Extension.Ts,
      isExternalLibraryImport: !name.startsWith('.')} : ts.resolveModuleName(name, containing, options, host).resolvedModule;
  }
  host.resolveModuleNames = (names, containing) => names.map(name => resolveModule(name, containing));
  const globals = fs.readdirSync(path.join(sdk, 'component')).filter(file => file.endsWith('.d.ts')).map(file => path.join(sdk, 'component', file));
  for (const file of [path.join(sdk, 'api/@internal/full/global.d.ts'), path.join(loader, 'declarations/global.d.ts')]) if (fs.existsSync(file)) globals.push(file);
  custom = require('./ets_components.cjs').withCustomComponents(ts, files, options, {resolveModule, host, roots: [...files, ...globals]});
  const program = ts.createProgram([...files, ...globals], options, host), checker = program.getTypeChecker();
  const sources = new Map(files.map(file => [real(file), need(program.getSourceFile(file), 'Selected ETS source missing: ' + file)]));
  for (const source of sources.values()) need(!source.parseDiagnostics.length, 'Official ETS parse diagnostics: ' + source.fileName + ' ' + source.parseDiagnostics.map(d => d.code).join(','));
  output.parser = {entry: parserEntry, sha256: digest(parserEntry), version: ts.version, config, configSha256: digest(config),
    loader, node: process.execPath, nodeVersion: process.version};
  output.sdkSelection = input.sdkSelection;
  output.componentContext = custom.provenance;
  output.contextFiles = [...new Map([...custom.files, ...program.getSourceFiles().map(source =>
    ({file: real(source.fileName), sha256: digest(source.fileName)}))].map(record => [record.file, record])).values()];
  const relative = file => path.relative(path.resolve(input.project), real(file)).split(path.sep).join('/');
  const id = node => !!node && ts.isIdentifier(node);
  const name = node => node?.name && (id(node.name) || ts.isStringLiteral(node.name)) ? node.name.text : undefined;
  const isStruct = node => ts.isStructDeclaration(node);
  const isCall = node => ts.isCallExpression(node) || ts.SyntaxKind[node.kind] === 'EtsComponentExpression';
  const strip = node => { while (node && ts.isParenthesizedExpression(node)) node = node.expression; return node; };
  const symbol = node => {
    if (!node) return undefined;
    const raw = checker.getSymbolAtLocation(ts.isPropertyAccessExpression(node) ? node.name : node);
    return raw?.flags & ts.SymbolFlags.Alias ? checker.getAliasedSymbol(raw) : raw;
  };
  const official = (node, expected) => {
    const value = symbol(node), declarations = value?.declarations || [];
    return !!value && (!expected || value.getName() === expected) && declarations.length > 0 && declarations.every(declaration => officialFile(declaration.getSourceFile().fileName));
  };
  function decorated(node, expected) {
    const decorators = [];
    ts.forEachChild(node, child => { if (child.kind === ts.SyntaxKind.Decorator) decorators.push(child); });
    return decorators.some(decorator => official(isCall(decorator.expression) ? decorator.expression.expression : decorator.expression, expected));
  }
  const component = node => isStruct(node) && (decorated(node, 'Component') || decorated(node, 'ComponentV2'));
  const builder = node => !!node?.body && ts.isMethodDeclaration(node) && isStruct(node.parent) && decorated(node, 'Builder');
  function anchor(node, kind, extra = {}) {
    const source = node.getSourceFile(), start = node.getStart(source), end = node.end;
    return {kind, file: relative(source.fileName), file_sha256: digest(source.fileName),
      start_utf16: start, end_utf16: end, line: source.getLineAndCharacterOfPosition(start).line + 1,
      end_line: source.getLineAndCharacterOfPosition(end).line + 1, node_kind: ts.SyntaxKind[node.kind], ...extra};
  }
  const emittedUnknown = new Set();
  function unknown(reason, node, context, extra = {}) {
    const value = {reason, source: name(context.owner), ...anchor(node, 'unresolved'),
      ...(context.originalTabPolicy ? {legacy_tab_scope: true} : {}), ...extra};
    const key = JSON.stringify(value);
    if (!emittedUnknown.has(key)) { emittedUnknown.add(key); output.unknowns.push(value); }
    return {unknown: true};
  }
  const scopeNames = new Map();
  for (const declaration of custom.declarations) {
    const key = real(declaration.file) + '::' + declaration.name;
    if (!scopeNames.has(key)) scopeNames.set(key, new Set());
    scopeNames.get(key).add(real(declaration.originFile) + ':' + declaration.originStart);
  }
  function declaration(expr, context) {
    expr = strip(expr);
    if (!expr || !(id(expr) || ts.isPropertyAccessExpression(expr))) return undefined;
    if (id(expr) && (scopeNames.get(real(context.source.fileName) + '::' + expr.text)?.size || 0) > 1) return {ambiguous: true};
    const value = symbol(expr), ds = value?.declarations || [];
    if (ds.length !== 1) return ds.length ? {ambiguous: true} : undefined;
    return ds[0];
  }
  function directComponentBinding(expr, value, context) {
    if (!id(expr)) return false;
    if (real(value.getSourceFile().fileName) === real(context.source.fileName)) return true;
    const binding = checker.getSymbolAtLocation(expr), declarations = binding?.declarations || [];
    if (!(binding?.flags & ts.SymbolFlags.Alias) || declarations.length !== 1 || !ts.isImportSpecifier(declarations[0])) return false;
    let imported = declarations[0].parent;
    while (imported && !ts.isImportDeclaration(imported)) imported = imported.parent;
    const moduleName = imported?.moduleSpecifier;
    if (!moduleName || !ts.isStringLiteral(moduleName) || !moduleName.text.startsWith('.')) return false;
    const base = path.resolve(path.dirname(context.source.fileName), moduleName.text);
    // Only directly measured named/aliased file imports. Re-exported indexes,
    // package names and default imports stay visible unknowns, never guesses.
    return [base, base + '.ets', base + '.d.ets'].some(file => fs.existsSync(file) &&
      fs.statSync(file).isFile() && real(file) === real(value.getSourceFile().fileName));
  }
  function sameBuilder(node, context) {
    const expr = strip(node.expression), value = declaration(expr, context);
    if (!value) return undefined;
    if (value.ambiguous) return {unsupported: 'ambiguous render declaration'};
    if (builder(value) && ts.isPropertyAccessExpression(expr) && expr.expression.kind === ts.SyntaxKind.ThisKeyword && value.parent === context.owner) {
      if (value.parameters.length || node.arguments?.length) return {unsupported: 'parameterized Builder'};
      return {node: value};
    }
    if (decorated(value, 'BuilderParam')) return {unsupported: 'BuilderParam is outside this supplement'};
    if (decorated(value, 'Builder')) return {unsupported: 'global/cross-struct Builder is outside this supplement'};
    return undefined;
  }
  const entered = new Set(), activeRegistrations = [], pendingPushes = [], handledPushes = new Set();
  function recursionFrom(member, context, seen = []) {
    if (seen.includes(member)) return true;
    let recursive = false;
    function visit(node) {
      if (recursive || ts.isArrowFunction(node) || ts.isFunctionExpression(node) || ts.isFunctionDeclaration(node)) return;
      if (isCall(node)) {
        const found = sameBuilder(node, context);
        if (found?.node && recursionFrom(found.node, context, [...seen, member])) recursive = true;
      }
      if (!recursive) ts.forEachChild(node, visit);
    }
    visit(member.body);
    return recursive;
  }
  function invoke(node, context, chain, stack, callback) {
    const found = sameBuilder(node, context);
    if (found?.unsupported) return unknown(found.unsupported, node, context);
    if (!found?.node) return undefined;
    const value = found.node;
    if (stack.includes(value) || recursionFrom(value, context)) return unknown('recursive Builder render chain', node, context);
    entered.add(value);
    const next = [...chain, anchor(node, 'builder-call', {builder: name(value)}), anchor(value, 'builder-declaration', {builder: name(value)})];
    return callback(value.body, context, next, [...stack, value]);
  }
  // Source order deliberately follows the original engine's first custom
  // component in a TabContent, including its first syntactic if/else branch.
  // Conditionality is disclosed; it is not a selected runtime branch.
  function firstComponent(node, context, chain, stack) {
    if (!node) return undefined;
    if (ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node) || ts.isArrowFunction(node)) return unknown('lambda/function render body unsupported', node, context);
    if (ts.isIfStatement(node)) {
      if (context.strictConditions) return unknown('conditional overlay/registration Builder is unsupported', node, context);
      unknown('conditional TabContent uses original first-syntactic-component policy, not runtime branch selection', node, context);
      return firstComponent(node.thenStatement, context, [...chain, anchor(node, 'conditional-render')], stack) || firstComponent(node.elseStatement, context, [...chain, anchor(node, 'conditional-render')], stack);
    }
    if (isCall(node)) {
      const expr = node.expression;
      if (ts.isPropertyAccessExpression(expr) && isCall(expr.expression)) return firstComponent(expr.expression, context, chain, stack);
      if (official(expr, 'ForEach') || official(expr, 'LazyForEach')) return unknown('dynamic ForEach render cardinality unsupported', node, context);
      if (official(expr, 'Tabs')) return unknown('nested Tabs is not one TabContent destination', node, context);
      const value = declaration(expr, context);
      if (value?.ambiguous) return unknown('ambiguous component declaration/import', node, context);
      if (value && component(value)) {
        if (!directComponentBinding(expr, value, context)) return unknown('component binding is outside original direct-identifier import wire', node, context);
        const target = expr.text;
        return {target, target_declaration: anchor(value, 'target-declaration', {declaration_name: name(value)}),
          call_site: anchor(node, 'component-construction'), chain: [...chain, anchor(node, 'component-construction', {target, declaration_name: name(value)})]};
      }
      const invoked = invoke(node, context, chain, stack, firstComponent);
      if (invoked) return invoked;
      if (ts.SyntaxKind[node.kind] === 'EtsComponentExpression' && official(expr)) return firstComponent(node.body, context, [...chain, anchor(node, 'builtin-render')], stack);
      // A plain unresolved UI-looking call can conceal the first component;
      // never skip it and invent a later known target as the tab destination.
      return unknown('render call has no supported unique component/Builder declaration', node, context);
    }
    if (ts.isVariableStatement(node)) return undefined;
    let result;
    ts.forEachChild(node, child => { if (!result) result = firstComponent(child, context, chain, stack); });
    return result;
  }
  function sameBuilderReference(expr, context, parameters = 0) {
    expr = strip(expr);
    const value = declaration(expr, context);
    if (!value || value.ambiguous || !builder(value) || !ts.isPropertyAccessExpression(expr) ||
        expr.expression.kind !== ts.SyntaxKind.ThisKeyword || value.parent !== context.owner ||
        value.parameters.length !== parameters) return undefined;
    return value;
  }
  function baseCall(node) {
    let value = node;
    while (isCall(value) && ts.isPropertyAccessExpression(value.expression) && isCall(value.expression.expression)) value = value.expression.expression;
    return value;
  }
  function navigationProperty(expr, context) {
    expr = strip(expr);
    if (!expr || !ts.isPropertyAccessExpression(expr) || expr.expression.kind !== ts.SyntaxKind.ThisKeyword) return undefined;
    const value = declaration(expr, context);
    if (!value || value.ambiguous || !ts.isPropertyDeclaration(value) || value.parent !== context.owner) return undefined;
    const valueType = checker.getNonNullableType(checker.getTypeAtLocation(expr)), s = valueType.getSymbol?.();
    const ds = s?.declarations || [];
    if (s?.getName() !== 'NavPathStack' || !ds.length || !ds.every(d => officialFile(d.getSourceFile().fileName))) return undefined;
    return value;
  }
  function registerDestination(node, context, chain) {
    const rootCall = baseCall(node), ref = node.arguments?.[0], value = declaration(ref, context);
    if (!official(rootCall.expression, 'Navigation') || !value || value.ambiguous || !builder(value) ||
        value.parent !== context.owner || !ts.isPropertyAccessExpression(ref) || ref.expression.kind !== ts.SyntaxKind.ThisKeyword ||
        !value.parameters.length || !id(value.parameters[0].name)) {
      unknown('navDestination registration is not a supported same-struct Builder', node, context); return;
    }
    const stackProperty = navigationProperty(rootCall.arguments?.[0], context);
    if (!stackProperty) { unknown('Navigation stack is not the same-struct official NavPathStack property', node, context); return; }
    entered.add(value);
    activeRegistrations.push({node, context, chain, builder: value, stackProperty,
      firstParameter: value.parameters[0], site: anchor(node.expression.name, 'navDestination-binding')});
  }
  function eventPushes(node, context, chain) {
    const callback = strip(node.arguments?.[0]);
    if (!callback || !(ts.isArrowFunction(callback) || ts.isFunctionExpression(callback))) return;
    const control = baseCall(node), start = [...chain, anchor(node.expression.name, 'onclick-binding')];
    function visit(value, nested = false) {
      if (!value || nested && (ts.isArrowFunction(value) || ts.isFunctionExpression(value) || ts.isFunctionDeclaration(value))) return;
      if (ts.isIfStatement(value) || ts.isSwitchStatement(value) || ts.isForStatement(value) || ts.isForOfStatement(value) || ts.isWhileStatement(value)) {
        unknown('conditional/iterated optional push requires model triage', value, context); return;
      }
      if (isCall(value) && ts.isPropertyAccessExpression(value.expression) && value.expression.name.text === 'pushPathByName' && value.expression.questionDotToken) {
        handledPushes.add(value);
        const prop = navigationProperty(value.expression.expression, context), target = value.arguments?.[0];
        if (!prop || !official(value.expression, 'pushPathByName') || !target || !ts.isStringLiteral(target) || value.questionDotToken) {
          unknown('optional push requires same-struct official NavPathStack and literal route name', value, context); return;
        }
        pendingPushes.push({node: value, context, chain: [...start, anchor(value, 'optional-navpath-push')],
          stackProperty: prop, target: target.text, control_site: anchor(control, 'trigger-control')});
        return;
      }
      ts.forEachChild(value, child => visit(child, true));
    }
    visit(callback.body);
  }
  function modifier(node, context, chain, stack) {
    const prop = node.expression;
    if (!ts.isPropertyAccessExpression(prop)) return;
    const api = prop.name.text;
    if (api === 'navDestination' && official(prop, 'navDestination')) registerDestination(node, context, chain);
    if (api === 'onClick' && official(prop, 'onClick')) eventPushes(node, context, chain);
    if (!['bindSheet', 'bindContentCover'].includes(api) || !official(prop, api)) return;
    const ref = node.arguments?.[1], value = ref && sameBuilderReference(ref, context);
    if (!value) {
      if (ref && ts.isPropertyAccessExpression(ref)) unknown('overlay Builder reference is not unique same-struct zero-argument Builder', ref, context, {api});
      return;
    }
    if (recursionFrom(value, context)) { unknown('recursive overlay Builder render chain', ref, context, {api}); return; }
    entered.add(value);
    const next = [...chain, anchor(prop.name, 'overlay-binding', {api}), anchor(ref, 'builder-reference', {builder: name(value)}), anchor(value, 'builder-declaration', {builder: name(value)})];
    const member = firstComponent(value.body, {...context, strictConditions: true}, next, [...stack, value]);
    if (!member || member.unknown) { unknown('overlay Builder has no supported static component', ref, context, {api}); return; }
    output.overlayBindings.push({source: name(context.owner), source_file: relative(context.source.fileName), api,
      line: anchor(prop.name, 'overlay-api').line, call_site: anchor(prop.name, 'overlay-api'),
      target: member.target, target_declaration: member.target_declaration, chain: member.chain, supplement: 'ets_ast'});
  }
  function tabContents(node, context, chain, stack, records) {
    if (!node) return;
    if (ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node) || ts.isArrowFunction(node)) { unknown('lambda TabContent producer unsupported', node, context); return; }
    if (isCall(node)) {
      const expr = node.expression;
      if (ts.isPropertyAccessExpression(expr) && isCall(expr.expression)) { tabContents(expr.expression, context, chain, stack, records); return; }
      if (official(expr, 'TabContent')) {
        const member = firstComponent(node.body, context, [...chain, anchor(node, 'tab-content')], stack);
        records.push(member ? {...member, tab_content: anchor(node, 'tab-content')} : unknown('TabContent has no statically resolved component', node, context));
        return;
      }
      if (official(expr, 'ForEach') || official(expr, 'LazyForEach')) { unknown('dynamic TabContent cardinality unsupported', node, context); records.push({unknown: true}); return; }
      if (official(expr, 'Tabs')) { unknown('nested Tabs producer unsupported', node, context); records.push({unknown: true}); return; }
      const invoked = invoke(node, context, chain, stack, (body, ctx, next, seen) => { tabContents(body, ctx, next, seen, records); return {visited: true}; });
      if (invoked) { if (invoked.unknown) records.push(invoked); return; }
      if (ts.SyntaxKind[node.kind] === 'EtsComponentExpression' && official(expr)) { tabContents(node.body, context, [...chain, anchor(node, 'builtin-render')], stack, records); return; }
      unknown('TabContent producer has no supported render binding', node, context); records.push({unknown: true}); return;
    }
    if (ts.isIfStatement(node)) { unknown('conditional TabContent group cardinality unsupported', node, context); records.push({unknown: true}); return; }
    if (!ts.isVariableStatement(node)) ts.forEachChild(node, child => tabContents(child, context, chain, stack, records));
  }
  function walk(node, context, chain, stack) {
    if (!node || ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node) || ts.isArrowFunction(node) || ts.isVariableStatement(node)) return;
    if (isCall(node)) {
      const expr = node.expression;
      if (ts.isPropertyAccessExpression(expr) && isCall(expr.expression)) { modifier(node, context, chain, stack); walk(expr.expression, context, chain, stack); return; }
      if (official(expr, 'ForEach') || official(expr, 'LazyForEach')) { unknown('dynamic render loop unsupported', node, context); return; }
      if (official(expr, 'Tabs')) {
        const records = [], next = [...chain, anchor(node, 'tabs')];
        tabContents(node.body, {...context, originalTabPolicy: true}, next, stack, records);
        const members = records.filter(record => !record.unknown);
        if (records.length >= 2 && records.every(record => !record.unknown)) {
          output.tabGroups.push({wire: {host: name(context.owner), file: relative(context.source.fileName), tabs: members.map(record => record.target)},
            call_site: anchor(node, 'tabs'), members, supplement: 'ets_ast'});
        } else if (records.length) unknown('Tabs group incomplete or has fewer than two static members', node, context, {resolved_members: members.map(record => record.target), total_members: records.length});
        return;
      }
      const invoked = invoke(node, context, chain, stack, (body, ctx, next, seen) => { walk(body, ctx, next, seen); return {visited: true}; });
      if (invoked) return;
      if (ts.SyntaxKind[node.kind] === 'EtsComponentExpression' && official(expr)) { walk(node.body, context, [...chain, anchor(node, 'builtin-render')], stack); return; }
      return;
    }
    ts.forEachChild(node, child => walk(child, context, chain, stack));
  }
  for (const source of sources.values()) for (const owner of source.statements.filter(component)) {
    const builds = owner.members.filter(member => ts.isMethodDeclaration(member) && name(member) === 'build' && member.body);
    if (builds.length !== 1) { unknown('component build method is missing/ambiguous', owner, {owner, source}); continue; }
    const build = builds[0], context = {owner, source};
    walk(build.body, context, [anchor(build, 'build-entry', {owner: name(owner)})], []);
    for (const member of owner.members.filter(builder)) {
      let references = 0;
      function referencesTo(node) {
        if (node !== member.name && id(node) && symbol(node)?.declarations?.includes(member)) references++;
        ts.forEachChild(node, referencesTo);
      }
      referencesTo(owner);
      if (!references) output.deadBuilders.push({source: name(owner), builder: name(member), reason: 'zero AST symbol references', ...anchor(member, 'dead-builder')});
      else if (!entered.has(member)) unknown('Builder referenced outside supported render chain', member, context, {builder: name(member), reference_count: references});
    }
  }
  for (const pending of pendingPushes) {
    const registrations = [];
    for (const record of activeRegistrations.filter(record => record.context.owner === pending.context.owner && record.stackProperty === pending.stackProperty)) {
      const parameterSymbol = symbol(record.firstParameter.name);
      function branches(node) {
        if (!node) return;
        if (ts.isIfStatement(node)) {
          const condition = strip(node.expression);
          if (ts.isBinaryExpression(condition) && condition.operatorToken.kind === ts.SyntaxKind.EqualsEqualsEqualsToken) {
            const left = strip(condition.left), right = strip(condition.right);
            const match = id(left) && symbol(left) === parameterSymbol && ts.isStringLiteral(right) && right.text === pending.target ||
              id(right) && symbol(right) === parameterSymbol && ts.isStringLiteral(left) && left.text === pending.target;
            if (match) {
              const next = [...record.chain, record.site, anchor(record.builder, 'destination-builder'), anchor(node, 'literal-route-branch', {route_name: pending.target})];
              const destination = firstComponent(node.thenStatement, {...record.context, strictConditions: true}, next, []);
              if (destination && !destination.unknown) registrations.push({route_name: pending.target,
                stack_property: anchor(record.stackProperty, 'navigation-stack-property'), builder: anchor(record.builder, 'destination-builder'),
                binding: record.site, target: destination.target, target_declaration: destination.target_declaration,
                chain: destination.chain, supplement: 'ets_ast'});
            }
          }
          branches(node.elseStatement);
          return;
        }
        if (!ts.isArrowFunction(node) && !ts.isFunctionExpression(node) && !ts.isFunctionDeclaration(node)) ts.forEachChild(node, branches);
      }
      branches(record.builder.body);
    }
    if (registrations.length !== 1) {
      unknown('optional push has missing/ambiguous literal navDestination registration; routerMap-only not proved by this supplement', pending.node, pending.context, {route_name: pending.target, registration_count: registrations.length});
      continue;
    }
    const registration = registrations[0];
    output.registrations.push(registration);
    output.optionalPushes.push({source: name(pending.context.owner), source_file: relative(pending.context.source.fileName),
      target: pending.target, line: pending.control_site.line, control_site: pending.control_site,
      call_site: anchor(pending.node, 'optional-navpath-push'), stack_property: anchor(pending.stackProperty, 'navigation-stack-property'),
      chain: pending.chain, registration, supplement: 'ets_ast'});
  }
  const boundRoutes = require('./target_route_bindings.cjs').collect({
    ts, checker, sources, selected, real, relative, anchor, official, officialFile,
    decorated, component, builder, isCall, strip, id, name, symbol, declaration,
    directComponentBinding, baseCall, unknown, output, entered
  });
  const measuredKey = node => { const a = anchor(node, 'identity'); return `${a.file}:${a.start_utf16}:${a.end_utf16}`; };
  const replacedReasons = new Set(['parameterized Builder', 'BuilderParam is outside this supplement',
    'Builder referenced outside supported render chain', 'dynamic render loop unsupported',
    'conditional overlay/registration Builder is unsupported', 'dynamic ForEach render cardinality unsupported',
    'overlay Builder has no supported static component']);
  output.unknowns = output.unknowns.filter(row => row.legacy_tab_scope || !replacedReasons.has(row.reason) ||
    !boundRoutes.resolvedKeys.has(`${row.file}:${row.start_utf16}:${row.end_utf16}`));
  for (const source of sources.values()) {
    function unhandled(node) {
      if (isCall(node) && ts.isPropertyAccessExpression(node.expression) && node.expression.name.text === 'pushPathByName' && node.expression.questionDotToken && !handledPushes.has(node) && !boundRoutes.resolvedKeys.has(measuredKey(node))) {
        let owner = node.parent;
        while (owner && !isStruct(owner)) owner = owner.parent;
        if (owner) unknown('optional push outside supported direct render-bound onclick callback', node, {owner, source});
      }
      ts.forEachChild(node, unhandled);
    }
    unhandled(source);
  }
  output.valid = true;
} catch (error) {
  output.error = String(error?.stack || error);
  process.exitCode = 2;
}
process.stdout.write(JSON.stringify(output, null, 2));
