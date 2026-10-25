'use strict';
// Official ETS AST/checker proof of same-file UI composition only. No source edits.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const output = {runId: input.runId, valid: false, proofs: [], scope: 'official ETS same-file composition; no device validation'};
const digest = f => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const requireFact = (value, message) => { if (!value) throw new Error(message); return value; };
try {
  const ts = require(input.parserModule), parserEntry = require.resolve(input.parserModule);
  let loader = path.dirname(parserEntry);
  while (path.basename(loader) !== 'ets-loader' && path.dirname(loader) !== loader) loader = path.dirname(loader);
  requireFact(path.basename(loader) === 'ets-loader' && typeof ts.ScriptKind.ETS === 'number', 'Selected parser is not official ETS');
  const sdk = path.resolve(loader, '../..'), config = path.join(loader, 'tsconfig.json');
  const raw = JSON.parse(fs.readFileSync(config, 'utf8')).compilerOptions;
  requireFact(raw.ets && typeof ts.convertCompilerOptionsFromJson === 'function', 'Official ETS compiler configuration unavailable');
  const converted = ts.convertCompilerOptionsFromJson(raw, loader);
  const baseOptions = {...converted.options, ets: raw.ets, noEmit: true, allowNonTsExtensions: true, strictNullChecks: true};
  const files = input.files.map(f => path.resolve(f));
  const roots = [sdk], companion = path.resolve(sdk, '../../hms/ets');
  if (fs.existsSync(companion)) roots.push(companion);
  const real = f => fs.realpathSync(f);
  const under = (file, root) => { const rel = path.relative(real(root), real(file)); return rel !== '..' && !rel.startsWith('..' + path.sep) && !path.isAbsolute(rel); };
  const officialFile = f => f.endsWith('.d.ts') && roots.some(root => under(f, root));
  let custom;
  const host = ts.createCompilerHost(baseOptions), original = host.getSourceFile;
  host.getSourceFile = (file, version, onError, fresh) => file.endsWith('.ets') && fs.existsSync(file)
    ? ts.createSourceFile(file, fs.readFileSync(file, 'utf8'), version, true, ts.ScriptKind.ETS, custom ? custom.forFile(file) : baseOptions)
    : original(file, version, onError, fresh);
  function resolveModule(name, containing) {
    const candidates = name.startsWith('.')
      ? [name, name + '.ets', name + '.ts', name + '.d.ts', path.join(name, 'index.ets')].map(n => path.resolve(path.dirname(containing), n))
      : roots.flatMap(root => ['kits', 'api'].map(dir => path.join(root, dir, name + '.d.ts')));
    const file = candidates.find(f => fs.existsSync(f) && fs.statSync(f).isFile());
    return file ? {resolvedFileName: file, extension: file.endsWith('.d.ts') ? ts.Extension.Dts : ts.Extension.Ts,
      isExternalLibraryImport: !name.startsWith('.')} : ts.resolveModuleName(name, containing, baseOptions, host).resolvedModule;
  }
  host.resolveModuleNames = (names, containing) => names.map(name => resolveModule(name, containing));
  const globals = fs.readdirSync(path.join(sdk, 'component')).filter(f => f.endsWith('.d.ts')).map(f => path.join(sdk, 'component', f));
  for (const f of [path.join(sdk, 'api/@internal/full/global.d.ts'), path.join(loader, 'declarations/global.d.ts')]) {
    if (fs.existsSync(f)) globals.push(f);
  }
  custom = require('./ets_components.cjs').withCustomComponents(ts, files, baseOptions,
    {resolveModule, host, roots: [...files, ...globals]});
  const options = custom.options;
  const program = ts.createProgram([...files, ...globals], options, host), checker = program.getTypeChecker();
  const sources = new Map(files.map(f => [real(f), requireFact(program.getSourceFile(f), 'Selected ETS source missing: ' + f)]));
  for (const source of sources.values()) requireFact(!source.parseDiagnostics.length, 'Official ETS parse diagnostics: ' + source.fileName);
  output.parser = {entry: parserEntry, sha256: digest(parserEntry), version: ts.version, config,
    configSha256: digest(config), node: process.execPath, nodeVersion: process.version};
  output.sdkSelection = input.sdkSelection;
  output.customComponents = {names: custom.componentNames, declarations: custom.declarations,
    files: custom.files, firstPassDiagnostics: custom.firstPassDiagnostics};
  const relative = source => path.relative(path.resolve(input.project), path.resolve(source.fileName));
  const id = n => !!n && ts.isIdentifier(n);
  const isStruct = n => ts.isStructDeclaration?.(n) || ts.SyntaxKind[n.kind] === 'StructDeclaration';
  const isCall = n => ts.isCallExpression(n) || ts.SyntaxKind[n.kind] === 'EtsComponentExpression';
  const strip = n => { while (n && ts.isParenthesizedExpression(n)) n = n.expression; return n; };
  const name = n => n?.name && (id(n.name) || ts.isStringLiteral(n.name)) ? n.name.text : undefined;
  const decorators = n => {
    const values = [];
    // ETS global @Builder functions expose their decorator through the official
    // child visitor even when neither TS modifiers nor the legacy field has it.
    ts.forEachChild(n, child => { if (child.kind === ts.SyntaxKind.Decorator) values.push(child); });
    return values;
  };
  const rawSymbol = n => checker.getSymbolAtLocation(ts.isPropertyAccessExpression(n) ? n.name : n);
  function officialSymbol(n, expected) {
    const symbol = rawSymbol(n), ds = symbol?.declarations || [];
    return symbol?.getName() === expected && ds.length && ds.every(d => officialFile(d.getSourceFile().fileName));
  }
  function decorated(n, expected) {
    return decorators(n).some(d => officialSymbol(isCall(d.expression) ? d.expression.expression : d.expression, expected));
  }
  const component = n => isStruct(n) && (decorated(n, 'Component') || decorated(n, 'ComponentV2'));
  const builder = n => !!n?.body && decorated(n, 'Builder') &&
    (ts.isFunctionDeclaration(n) && ts.isSourceFile(n.parent) || ts.isMethodDeclaration(n) && isStruct(n.parent));
  const parameter = n => !!n && ts.isPropertyDeclaration(n) && isStruct(n.parent) && decorated(n, 'BuilderParam');
  const structs = new Map(), nodeKeys = new Map(), targets = new Map(), seeds = [];
  function structKey(n) { return relative(n.getSourceFile()) + '::' + name(n); }
  function key(n) {
    if (nodeKeys.has(n)) return nodeKeys.get(n);
    const owner = isStruct(n.parent) ? name(n.parent) + '.' : '';
    const value = isStruct(n) ? structKey(n) : relative(n.getSourceFile()) + '::' + owner + (name(n) || 'closure@' + n.getStart());
    nodeKeys.set(n, value); return value;
  }
  for (const source of sources.values()) {
    for (const node of source.statements) {
      if (component(node) && id(node.name)) structs.set(structKey(node), node);
    }
  }
  for (const target of input.targets) {
    const value = target.file + '::' + target.name;
    if (structs.has(value)) targets.set(value, target);
  }
  for (const seed of input.seeds) {
    const value = seed.file + '::' + seed.name;
    if (structs.has(value)) seeds.push({record: seed, node: structs.get(value), key: value});
  }
  function directDeclaration(expr, context) {
    expr = strip(expr);
    if (!expr || !(id(expr) || ts.isPropertyAccessExpression(expr) && expr.expression.kind === ts.SyntaxKind.ThisKeyword)) return undefined;
    const symbol = rawSymbol(expr);
    if (!symbol || symbol.flags & ts.SymbolFlags.Alias || symbol.declarations?.length !== 1) return undefined;
    const declaration = symbol.valueDeclaration || symbol.declarations[0];
    if (real(declaration.getSourceFile().fileName) !== real(context.file.fileName)) return undefined;
    if (id(expr) && isStruct(declaration) && ts.isSourceFile(declaration.parent)) return declaration;
    if (id(expr) && ts.isFunctionDeclaration(declaration) && ts.isSourceFile(declaration.parent)) return declaration;
    if (ts.isPropertyAccessExpression(expr) && declaration.parent === context.owner) return declaration;
    return undefined;
  }
  function callback(expr, context, bindingNode=expr) {
    expr = strip(expr);
    if (!expr) return undefined;
    if (ts.isArrowFunction(expr) || ts.isFunctionExpression(expr)) {
      return {node: expr, body: expr.body, owner: context.owner, bindings: context.bindings,
        file: context.file, key: key(expr), links: [{to: key(expr), node: bindingNode, kind: 'builder-param-binding'}]};
    }
    const declaration = directDeclaration(expr, context);
    if (parameter(declaration)) {
      const value = context.bindings.get(declaration);
      return value ? {...value, links: [{to: key(declaration), node: bindingNode, kind: 'builder-param-forward'}, ...value.links]} : undefined;
    }
    if (!builder(declaration)) return undefined;
    return {node: declaration, body: declaration.body, owner: ts.isMethodDeclaration(declaration) ? declaration.parent : undefined,
      bindings: context.bindings, file: declaration.getSourceFile(), key: key(declaration),
      links: [{to: key(declaration), node: bindingNode, kind: 'builder-param-binding'}]};
  }
  function edge(from, to, kind, node) {
    const source = node.getSourceFile(), position = node.getStart(source);
    return {from, to, kind, file: relative(source), startUtf16: position,
      line: source.getLineAndCharacterOfPosition(position).line + 1, nodeKind: ts.SyntaxKind[node.kind]};
  }
  const proofs = new Map(), visited = new Set();
  function contextKey(context) {
    return context.key + '|' + [...context.bindings.entries()].map(([property,value]) => key(property)+'='+value.key).sort().join('|');
  }
  function evaluate(context, chain, seed) {
    const identity = contextKey(context);
    if (visited.has(identity)) return;
    visited.add(identity);
    walk(context.body, context, chain, seed);
  }
  function render(declaration, call, context, chain, seed) {
    const targetKey = key(declaration), target = targets.get(targetKey);
    const next = [...chain, edge(context.key, targetKey, 'same-file-render', call)];
    if (target && !proofs.has(targetKey)) proofs.set(targetKey, {target, targetKey, seed: seed.record, seedKey: seed.key, chain: next});
    const build = (declaration.members || []).find(m => ts.isMethodDeclaration(m) && name(m) === 'build' && m.body);
    if (!build) return;
    const bindings = new Map(), receiver = {node: declaration, owner: declaration, key: targetKey,
      file: declaration.getSourceFile(), body: build.body, bindings};
    const parameters = (declaration.members || []).filter(parameter);
    const args = call.arguments || [];
    const literal = args.length === 1 && ts.isObjectLiteralExpression(strip(args[0])) ? strip(args[0]) : undefined;
    const closed = !args.length || !!literal && literal.properties.every(p => ts.isPropertyAssignment(p) && (id(p.name) || ts.isStringLiteral(p.name)));
    for (const property of parameters) {
      const values = literal?.properties.filter(p => (id(p.name) || ts.isStringLiteral(p.name)) && p.name.text === name(property)) || [];
      if (values.length === 1) {
        const value = callback(values[0].initializer, context, values[0]);
        if (value) bindings.set(property, value);
      } else if (!values.length && closed && property.initializer) {
        const value = callback(property.initializer, receiver, property.initializer);
        if (value) bindings.set(property, value);
      }
    }
    if (call.body && ts.isBlock(call.body) && parameters.length === 1 && !bindings.has(parameters[0])) {
      bindings.set(parameters[0], {node: call.body, body: call.body, owner: context.owner,
        bindings: context.bindings, file: context.file, key: key(call.body),
        links: [{to: key(call.body), node: call.body, kind: 'builder-param-binding'}]});
    }
    evaluate(receiver, next, seed);
  }
  function walk(node, context, chain, seed) {
    if (!node) return;
    if (ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node) || ts.isArrowFunction(node) || ts.isVariableStatement(node)) return;
    if (ts.isIfStatement(node)) { walk(node.thenStatement, context, chain, seed); walk(node.elseStatement, context, chain, seed); return; }
    if (isCall(node)) {
      const declaration = directDeclaration(node.expression, context);
      if (declaration && component(declaration)) { render(declaration, node, context, chain, seed); return; }
      if (declaration && parameter(declaration)) {
        const value = context.bindings.get(declaration);
        if (value) {
          const propertyKey = key(declaration);
          const next = [...chain, edge(context.key, propertyKey, 'builder-param-invoke', node)];
          let cursor = propertyKey;
          for (const link of value.links) { next.push(edge(cursor, link.to, link.kind, link.node)); cursor = link.to; }
          requireFact(cursor === value.key, 'Builder binding chain is disconnected');
          evaluate({...value}, next, seed);
        }
        return;
      }
      if (declaration && builder(declaration)) {
        const value = callback(node.expression, context);
        evaluate(value, [...chain, edge(context.key, value.key, 'builder-call', node)], seed);
        return;
      }
      // Official built-in UI tails are render bodies. Arbitrary callback bodies
      // and action arguments are not entered. Modifier chains retain their base.
      const symbol = rawSymbol(node.expression), ds = symbol?.declarations || [];
      if (ts.SyntaxKind[node.kind] === 'EtsComponentExpression' && ds.length && ds.every(d => officialFile(d.getSourceFile().fileName))) {
        walk(node.body, context, chain, seed);
      } else if (ts.isPropertyAccessExpression(node.expression) && isCall(node.expression.expression)) {
        walk(node.expression.expression, context, chain, seed);
      }
      return;
    }
    ts.forEachChild(node, child => walk(child, context, chain, seed));
  }
  for (const seed of seeds) {
    const build = (seed.node.members || []).find(m => ts.isMethodDeclaration(m) && name(m) === 'build' && m.body);
    if (build) evaluate({node: seed.node, owner: seed.node, file: seed.node.getSourceFile(),
      body: build.body, key: seed.key, bindings: new Map()}, [], seed);
  }
  output.proofs = [...proofs.values()];
  output.valid = true;
  output.files = files.map(file => ({file, sha256: digest(file)}));
} catch (error) {
  output.error = error.message;
}
process.stdout.write(JSON.stringify(output));
if (!output.valid) process.exitCode = 3;
