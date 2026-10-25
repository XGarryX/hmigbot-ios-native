'use strict';
// A read-only, deliberately narrow proof over the selected official ETS AST and
// checker. No token/name-only exemptions and no generated application source.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const {withCustomComponents} = require('./ets_components.cjs');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const result = {runId: input.runId, proved: false, scope: 'official ETS syntax/checker proof; 未经设备验证', symbols: []};
const digest = f => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
function requireFact(value, message) { if (!value) throw new Error(message); return value; }
try {
  const ts = require(input.parserModule), parserEntry = require.resolve(input.parserModule);
  let loader = path.dirname(parserEntry);
  while (path.basename(loader) !== 'ets-loader' && path.dirname(loader) !== loader) loader = path.dirname(loader);
  requireFact(path.basename(loader) === 'ets-loader' && typeof ts.ScriptKind.ETS === 'number', 'Selected parser is not official ETS');
  const sdk = path.resolve(loader, '../..'), config = path.join(loader, 'tsconfig.json');
  const raw = JSON.parse(fs.readFileSync(config, 'utf8')).compilerOptions;
  requireFact(raw.ets && typeof ts.convertCompilerOptionsFromJson === 'function', 'Official compiler configuration/converter unavailable');
  const converted = ts.convertCompilerOptionsFromJson(raw, loader);
  const options = {...converted.options, ets: raw.ets, noEmit: true, allowNonTsExtensions: true, strictNullChecks: true};
  let componentContext;
  const roots = [sdk];
  const companion = path.resolve(sdk, '../../hms/ets');
  if (fs.existsSync(companion)) roots.push(companion);
  const real = f => fs.realpathSync(f);
  const under = (file, root) => { const rel = path.relative(real(root), real(file)); return rel !== '..' && !rel.startsWith('..' + path.sep) && !path.isAbsolute(rel); };
  const officialFile = f => f.endsWith('.d.ts') && roots.some(root => under(f, root));
  const host = ts.createCompilerHost(options), original = host.getSourceFile;
  host.getSourceFile = (file, version, onError, fresh) => file.endsWith('.ets') && fs.existsSync(file)
    ? ts.createSourceFile(file, fs.readFileSync(file, 'utf8'), version, true, ts.ScriptKind.ETS,
        componentContext ? componentContext.forFile(file) : options)
    : original(file, version, onError, fresh);
  host.resolveModuleNames = (names, containing) => names.map(name => {
    const candidates = name.startsWith('.')
      ? [name, name + '.ets', name + '.ts', name + '.d.ts', path.join(name, 'index.ets')].map(n => path.resolve(path.dirname(containing), n))
      : roots.flatMap(root => ['kits', 'api'].map(dir => path.join(root, dir, name + '.d.ts')));
    const file = candidates.find(f => fs.existsSync(f) && fs.statSync(f).isFile());
    return file ? {resolvedFileName: file, extension: file.endsWith('.d.ts') ? ts.Extension.Dts : ts.Extension.Ts,
      isExternalLibraryImport: !name.startsWith('.')} : ts.resolveModuleName(name, containing, options, host).resolvedModule;
  });
  const components = path.join(sdk, 'component');
  const globalFiles = fs.readdirSync(components).filter(f => f.endsWith('.d.ts')).map(f => path.join(components, f));
  for (const f of [path.join(sdk, 'api/@internal/full/global.d.ts'), path.join(loader, 'declarations/global.d.ts')]) {
    if (fs.existsSync(f)) globalFiles.push(f);
  }
  const files = input.files.map(f => path.resolve(f));
  componentContext = withCustomComponents(ts, files, options, {host, roots: [...files, ...globalFiles]});
  result.componentContext = componentContext.provenance;
  const program = ts.createProgram([...files, ...globalFiles], options, host), checker = program.getTypeChecker();
  const sources = new Map(files.map(f => [real(f), requireFact(program.getSourceFile(f), 'Missing selected ETS source: ' + f)]));
  for (const source of sources.values()) requireFact(!source.parseDiagnostics.length, 'Official ETS parse diagnostics: ' + source.fileName);
  result.parser = {entry: parserEntry, sha256: digest(parserEntry), version: ts.version, config, configSha256: digest(config),
    compilerOptionsConverter: 'convertCompilerOptionsFromJson', node: process.execPath, nodeVersion: process.version};
  result.sdkSelection = input.sdkSelection;
  function children(node, predicate) { const out = []; function visit(n) { if (predicate(n)) out.push(n); ts.forEachChild(n, visit); } visit(node); return out; }
  const id = n => !!n && ts.isIdentifier(n);
  const textName = n => n && (id(n) || ts.isStringLiteral(n)) ? n.text : undefined;
  const strip = n => { while (n && ts.isParenthesizedExpression(n)) n = n.expression; return n; };
  function symbol(node, seen = new Set()) {
    if (!node) return undefined;
    node = strip(node);
    if (ts.isPropertyAccessExpression(node)) node = node.name;
    let s = checker.getSymbolAtLocation(node);
    if (!s || seen.has(s)) return s;
    seen.add(s);
    if (s.flags & ts.SymbolFlags.Alias) return checker.getAliasedSymbol(s);
    const d = s.valueDeclaration;
    if (d && ts.isVariableDeclaration(d) && d.initializer && d.parent.flags & ts.NodeFlags.Const) {
      const initial = strip(d.initializer);
      if (id(initial) || ts.isPropertyAccessExpression(initial)) return symbol(initial, seen);
    }
    return s;
  }
  function same(a, b) { return !!symbol(a) && symbol(a) === symbol(b); }
  function official(node, expected, domain) {
    const s = symbol(node), ds = s?.declarations || [];
    const ok = s && s.getName() === expected && ds.length && ds.every(d => officialFile(d.getSourceFile().fileName)) &&
      (!domain || ds.some(d => d.getSourceFile().fileName.includes(path.sep + domain + path.sep)));
    if (ok) result.symbols.push({name: expected, declarations: ds.map(d => ({file: d.getSourceFile().fileName, sha256: digest(d.getSourceFile().fileName), kind: ts.SyntaxKind[d.kind]}))});
    return !!ok;
  }
  function source(selector) {
    const f = path.resolve(input.project, selector.file);
    return requireFact(sources.get(real(f)), 'Selector is outside selected target module source files: ' + f);
  }
  function declaration(selector, name, predicate) {
    const found = source(selector).statements.filter(n => predicate(n) && textName(n.name) === name);
    return requireFact(found.length === 1 && found[0], 'Missing/ambiguous selected declaration: ' + name);
  }
  const isStruct = n => ts.isStructDeclaration?.(n) || ts.SyntaxKind[n.kind] === 'StructDeclaration';
  const namedMember = (node, name, predicate) => {
    const found = (node.members || []).filter(n => textName(n.name) === name && predicate(n));
    return requireFact(found.length === 1 && found[0], 'Missing/ambiguous member: ' + name);
  };
  const method = (node, name) => requireFact(namedMember(node, name, ts.isMethodDeclaration).body, 'Method has no implementation: ' + name).parent;
  function decorators(node) { return node.modifiers?.filter(n => n.kind === ts.SyntaxKind.Decorator) || node.decorators || []; }
  function decorator(node, name) {
    const found = decorators(node).filter(d => official(ts.isCallExpression(d.expression) ? d.expression.expression : d.expression, name, 'component'));
    return requireFact(found.length === 1 && found[0].expression, 'Missing/false official decorator: ' + name);
  }
  function noWrites(node) {
    return !children(node, n => ts.isBinaryExpression(n) && n.operatorToken.kind >= ts.SyntaxKind.FirstAssignment && n.operatorToken.kind <= ts.SyntaxKind.LastAssignment ||
      ts.isDeleteExpression(n) || (ts.isPrefixUnaryExpression(n) || ts.isPostfixUnaryExpression(n)) &&
      [ts.SyntaxKind.PlusPlusToken, ts.SyntaxKind.MinusMinusToken].includes(n.operator)).length;
  }
  function constDeclaration(node) {
    const s = checker.getSymbolAtLocation(node), d = s?.valueDeclaration;
    return d && ts.isVariableDeclaration(d) && d.parent.flags & ts.NodeFlags.Const && id(d.name) && d.initializer ? d : undefined;
  }
  function immutable(d) {
    const s = checker.getSymbolAtLocation(d.name);
    return !children(d.getSourceFile(), n => (ts.isBinaryExpression(n) && n.operatorToken.kind >= ts.SyntaxKind.FirstAssignment && n.operatorToken.kind <= ts.SyntaxKind.LastAssignment &&
      children(n.left, k => id(k) && checker.getSymbolAtLocation(k) === s).length) ||
      (ts.isPrefixUnaryExpression(n) || ts.isPostfixUnaryExpression(n)) && [ts.SyntaxKind.PlusPlusToken, ts.SyntaxKind.MinusMinusToken].includes(n.operator) && same(n.operand, d.name)).length;
  }
  function resolvedConst(expr, seen = new Set()) {
    expr = strip(expr);
    if (!id(expr)) return expr;
    const d = constDeclaration(expr);
    if (!d || seen.has(d) || !immutable(d)) return expr;
    seen.add(d); return resolvedConst(d.initializer, seen);
  }
  function oneReturn(fn) {
    requireFact(fn.body && noWrites(fn.body), 'Function mutates data or has no body');
    const statements = fn.body.statements;
    requireFact(statements.every(s => ts.isReturnStatement(s) || ts.isVariableStatement(s) && s.declarationList.flags & ts.NodeFlags.Const), 'Unsupported function control/effects');
    const returns = statements.filter(ts.isReturnStatement);
    requireFact(returns.length === 1 && returns[0] === statements[statements.length - 1], 'Expected one final return');
    return requireFact(returns[0].expression, 'Empty return');
  }
  const proof = input.proof, producer = proof.producer;
  const dataFunction = declaration(producer, producer.data_function, ts.isFunctionDeclaration);
  const parameter = requireFact(dataFunction.parameters.length === 1 && dataFunction.parameters[0], 'Producer requires one input parameter');
  requireFact(id(parameter.name) && parameter.name.text === producer.input_parameter && !parameter.dotDotDotToken && !parameter.initializer, 'Wrong producer parameter');
  const optional = !!parameter.questionToken || parameter.type && ts.isUnionTypeNode(parameter.type) && parameter.type.types.some(t => t.kind === ts.SyntaxKind.UndefinedKeyword);
  requireFact(optional, 'Producer parameter is not explicitly optional');
  const returned = oneReturn(dataFunction), object = resolvedConst(returned);
  requireFact(ts.isObjectLiteralExpression(object) && object.properties.every(p => ts.isPropertyAssignment(p) && (id(p.name) || ts.isStringLiteral(p.name))), 'Producer does not return a closed data object');
  const fields = object.properties.filter(p => textName(p.name) === producer.boolean_field);
  const presence = strip(requireFact(fields.length === 1 && fields[0].initializer, 'Missing/duplicate boolean data field'));
  requireFact(ts.isBinaryExpression(presence) && presence.operatorToken.kind === ts.SyntaxKind.ExclamationEqualsEqualsToken &&
    id(presence.left) && same(presence.left, parameter.name) && id(presence.right) && presence.right.text === 'undefined', 'Boolean field is not input !== undefined');
  const undefinedSymbol = checker.getSymbolAtLocation(presence.right);
  requireFact(!undefinedSymbol?.declarations?.some(d => !d.getSourceFile().isDeclarationFile), 'Local undefined shadow');
  // Objects/aliases may only flow to const aliases and return, never escape to
  // another call/property write that could change the established boolean.
  if (id(strip(returned))) {
    const aliases = new Set();
    function collect(expr) { const d = constDeclaration(strip(expr)); requireFact(d && immutable(d), 'Returned object alias is mutable'); if (aliases.has(d)) return;
      aliases.add(d); if (id(strip(d.initializer))) collect(d.initializer); }
    collect(returned);
    for (const d of aliases) for (const ref of children(dataFunction.body, n => id(n) && checker.getSymbolAtLocation(n) === checker.getSymbolAtLocation(d.name))) {
      if (ref === d.name) continue;
      let parent = ref.parent; while (ts.isParenthesizedExpression(parent)) parent = parent.parent;
      requireFact(ts.isReturnStatement(parent) || ts.isVariableDeclaration(parent) && aliases.has(parent) && parent.initializer, 'Returned data object escapes/mutates');
    }
  }
  const bindingFunction = declaration(producer, producer.binding_function, ts.isFunctionDeclaration);
  requireFact(bindingFunction.parameters.length === 1 && id(bindingFunction.parameters[0].name), 'Binding function requires one parameter');
  const bound = strip(oneReturn(bindingFunction));
  requireFact(ts.isCallExpression(bound) && official(bound.expression, 'createFormBindingData', 'api') && bound.arguments.length === 1, 'Binding is not direct official createFormBindingData');
  const dataCall = strip(bound.arguments[0]);
  requireFact(ts.isCallExpression(dataCall) && same(dataCall.expression, dataFunction.name) && dataCall.arguments.length === 1 &&
    id(dataCall.arguments[0]) && same(dataCall.arguments[0], bindingFunction.parameters[0].name), 'Binding does not call data function with the same parameter');
  function bindingOrigin(expr, seen = new Set()) {
    expr = strip(expr);
    if (ts.isCallExpression(expr)) return same(expr.expression, bindingFunction.name) && expr.arguments.length === 1;
    if (!id(expr)) return false;
    const d = constDeclaration(expr);
    if (!d || seen.has(d) || !immutable(d)) return false;
    const bindingSymbol = checker.getSymbolAtLocation(d.name);
    for (const ref of children(d.getSourceFile(), n => id(n) && checker.getSymbolAtLocation(n) === bindingSymbol)) {
      if (ref === d.name) continue;
      let value = ref, parent = ref.parent;
      while (ts.isParenthesizedExpression(parent)) { value = parent; parent = parent.parent; }
      if (ts.isReturnStatement(parent) && parent.expression === value) continue;
      if (ts.isVariableDeclaration(parent) && parent.initializer === value && parent.parent.flags & ts.NodeFlags.Const) continue;
      if (ts.isCallExpression(parent) && parent.arguments[1] === value && official(parent.expression, 'updateForm', 'api')) continue;
      return false;
    }
    seen.add(d); return bindingOrigin(d.initializer, seen);
  }
  const ext = proof.extension, extensionSource = source(ext);
  const extension = declaration(ext, ext.class, ts.isClassDeclaration);
  const bases = (extension.heritageClauses || []).filter(h => h.token === ts.SyntaxKind.ExtendsKeyword).flatMap(h => h.types);
  requireFact(bases.length === 1 && official(bases[0].expression, 'FormExtensionAbility', 'api'), 'Extension does not extend official FormExtensionAbility');
  let main = path.dirname(extensionSource.fileName);
  while (path.basename(main) !== 'main' && path.dirname(main) !== main) main = path.dirname(main);
  requireFact(path.basename(main) === 'main', 'Extension has no target main module');
  const json5 = require(path.join(loader, 'node_modules/json5'));
  const moduleFile = path.join(main, 'module.json5'), moduleData = json5.parse(fs.readFileSync(moduleFile, 'utf8')).module;
  const extensionEntries = (moduleData?.extensionAbilities || []).filter(e => e.type === 'form' && e.srcEntry && real(path.resolve(main, e.srcEntry)) === real(extensionSource.fileName));
  requireFact(extensionEntries.length === 1, 'Form extension is not uniquely registered in module.json5');
  const profileFile = path.resolve(input.project, ext.form_profile);
  const profileName = path.basename(profileFile).replace(/\.json5?$/, '');
  requireFact(under(profileFile, path.join(main, 'resources/base/profile')) && (extensionEntries[0].metadata || []).some(m =>
    m.name === 'ohos.extension.form' && m.resource === '$profile:' + profileName), 'Extension form profile metadata mismatch');
  const profile = json5.parse(fs.readFileSync(profileFile, 'utf8'));
  const forms = (profile.forms || []).filter(f => f.name === ext.form_name);
  requireFact(forms.length === 1 && typeof forms[0].src === 'string', 'Form profile name mismatch');
  let receiverFile = path.resolve(main, forms[0].src);
  if (!receiverFile.endsWith('.ets')) receiverFile += '.ets';
  requireFact(real(receiverFile) === real(path.resolve(input.project, proof.receiver.file)), 'Form profile receiver src mismatch');
  const onAdd = method(extension, 'onAddForm'), onUpdate = method(extension, 'onUpdateForm');
  const addReturns = children(onAdd.body, ts.isReturnStatement);
  requireFact(addReturns.length === 1 && addReturns[0].parent === onAdd.body && bindingOrigin(addReturns[0].expression), 'onAddForm does not return immutable binding origin');
  function callName(n) { return textName(n.expression?.name || n.expression) || (ts.isElementAccessExpression(n.expression) && ts.isStringLiteral(n.expression.argumentExpression) ? n.expression.argumentExpression.text : ''); }
  const moduleSources = [...sources.values()].filter(s => under(s.fileName, main));
  const publishers = moduleSources.flatMap(s => children(s, n => ts.isCallExpression(n) &&
    (callName(n) === 'updateForm' || symbol(n.expression)?.getName() === 'updateForm')));
  requireFact(publishers.length && publishers.some(n => n.pos >= onUpdate.body.pos && n.end <= onUpdate.body.end), 'onUpdateForm has no SDK publisher');
  for (const call of publishers) requireFact(official(call.expression, 'updateForm', 'api') && call.arguments.length === 2 && bindingOrigin(call.arguments[1]), 'Unproven module updateForm binding origin');
  const receiver = proof.receiver, hostStruct = declaration(receiver, receiver.component, isStruct);
  const storage = namedMember(hostStruct, receiver.storage_member, ts.isPropertyDeclaration);
  requireFact(storage.type?.kind === ts.SyntaxKind.BooleanKeyword, 'Receiver storage member is not boolean');
  const prop = decorator(storage, 'LocalStorageProp');
  requireFact(ts.isCallExpression(prop) && prop.arguments.length === 1 && ts.isStringLiteral(prop.arguments[0]) && prop.arguments[0].text === producer.boolean_field, 'LocalStorageProp key mismatch');
  const entry = decorator(hostStruct, 'Entry');
  requireFact(ts.isCallExpression(entry) && entry.arguments.length === 1 && id(entry.arguments[0]), 'Entry does not use a storage identifier');
  const storageDeclaration = constDeclaration(entry.arguments[0]);
  requireFact(storageDeclaration && storageDeclaration.parent.parent.parent === source(receiver) && immutable(storageDeclaration) &&
    ts.isNewExpression(storageDeclaration.initializer) && official(storageDeclaration.initializer.expression, 'LocalStorage', 'component'), 'Entry storage is not module-level immutable official LocalStorage');
  const uiCall = n => (ts.isCallExpression(n) || ts.SyntaxKind[n.kind] === 'EtsComponentExpression') &&
    raw.ets.components.includes(textName(n.expression)) && official(n.expression, textName(n.expression), 'component');
  const componentCall = n => ts.isCallExpression(n) || ts.SyntaxKind[n.kind] === 'EtsComponentExpression';
  function unwrapRender(expr) {
    while (ts.isCallExpression(expr) && ts.isPropertyAccessExpression(expr.expression) && componentCall(expr.expression.expression)) expr = expr.expression.expression;
    return expr;
  }
  function rendered(block, allowConditions = false) {
    const calls = [], conditions = [];
    function visit(statement) {
      if (ts.isBlock(statement)) { for (const s of statement.statements) visit(s); return; }
      if (ts.isExpressionStatement(statement)) {
        const expr = unwrapRender(statement.expression);
        if (componentCall(expr)) { calls.push(expr); if (uiCall(expr) && expr.body) visit(expr.body); }
      } else if (allowConditions && ts.isIfStatement(statement)) { conditions.push(statement); }
    }
    visit(block); return {calls, conditions};
  }
  const hostBuild = method(hostStruct, 'build'), hostCalls = rendered(hostBuild.body).calls;
  const allowedReferences = new Set(), renderFacts = [];
  for (const render of proof.render) {
    const child = declaration(render, render.component, isStruct), param = namedMember(child, render.param, ts.isPropertyDeclaration);
    decorator(param, 'Param');
    requireFact(param.type?.kind === ts.SyntaxKind.BooleanKeyword, 'Child param is not boolean');
    const calls = hostCalls.filter(n => same(n.expression, child.name));
    requireFact(calls.length > 0, 'Declared child is not actually rendered in receiver build');
    for (const call of calls) {
      requireFact(call.arguments.length === 1 && ts.isObjectLiteralExpression(call.arguments[0]), 'Child render has no literal parameter object');
      const props = call.arguments[0].properties.filter(p => ts.isPropertyAssignment(p) && textName(p.name) === render.param);
      const value = strip(requireFact(props.length === 1 && props[0].initializer, 'Child render param missing/duplicate'));
      requireFact(ts.isPropertyAccessExpression(value) && value.expression.kind === ts.SyntaxKind.ThisKeyword && same(value.name, storage.name), 'Child render does not receive receiver storage member');
      allowedReferences.add(value.name);
    }
    const build = method(child, 'build'), conditions = rendered(build.body, true).conditions;
    const matching = conditions.filter(n => ts.isPropertyAccessExpression(strip(n.expression)) && strip(n.expression).expression.kind === ts.SyntaxKind.ThisKeyword && same(strip(n.expression).name, param.name));
    requireFact(matching.length === 1, 'Child build has no unique real if(this.param)');
    const condition = matching[0];
    requireFact(ts.isBlock(condition.thenStatement) && !!condition.elseStatement === input.sourceHasElse && (!condition.elseStatement || ts.isBlock(condition.elseStatement)), 'Source/target plain else structure mismatch');
    for (const branch of [condition.thenStatement, condition.elseStatement].filter(Boolean)) requireFact(rendered(branch).calls.some(uiCall), 'Conditional branch has no actual official SDK UI node');
    renderFacts.push({file: render.file, component: render.component, param: render.param, renderCalls: calls.length, hasElse: !!condition.elseStatement});
  }
  const memberSymbol = checker.getSymbolAtLocation(storage.name);
  for (const ref of children(source(receiver), n => (id(n) || ts.isStringLiteral(n)) && checker.getSymbolAtLocation(n) === memberSymbol)) {
    if (ref === storage.name || ref.parent.name === ref && (ts.isPropertyDeclaration(ref.parent) || ts.isPropertySignature(ref.parent))) continue;
    requireFact(allowedReferences.has(ref), 'Receiver storage member has an undeclared use');
  }
  result.proved = true;
  result.chain = {producer: producer.data_function, binding: producer.binding_function, extension: ext.class,
    moduleFile, profileFile, receiver: receiver.component, publishers: publishers.length, renders: renderFacts};
  result.inputs = program.getSourceFiles().filter(s => s.fileName.endsWith('.ets') || officialFile(s.fileName)).map(s => ({file: s.fileName, sha256: digest(s.fileName)}));
} catch (error) {
  result.error = error.message;
}
process.stdout.write(JSON.stringify(result));
