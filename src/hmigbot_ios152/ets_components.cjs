'use strict';
// Mirror the SDK's per-file component collection before its final ETS parse.
// This supplies parser context only. It does not prove rendering or type safety.
const fs = require('fs'), path = require('path'), crypto = require('crypto');

function withCustomComponents(ts, files, options, context = {}) {
  if (!options?.ets || typeof ts.isStructDeclaration !== 'function') {
    throw new Error('Official ETS parser configuration is unavailable');
  }
  const real = file => fs.realpathSync(file);
  const digest = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  const roots = context.roots || files;
  const host = context.host || ts.createCompilerHost(options);
  const originalSource = host.getSourceFile.bind(host);
  if (!context.host) host.getSourceFile = (file, version, onError, fresh) =>
    file.endsWith('.ets') && fs.existsSync(file)
      ? ts.createSourceFile(file, fs.readFileSync(file, 'utf8'), version, true, ts.ScriptKind.ETS, options)
      : originalSource(file, version, onError, fresh);
  function resolve(name, containing) {
    const supplied = context.resolveModule?.(name, containing);
    if (supplied) return typeof supplied === 'string'
      ? {resolvedFileName: supplied, extension: supplied.endsWith('.d.ts') ? ts.Extension.Dts : ts.Extension.Ts}
      : supplied;
    if (name.startsWith('.')) {
      const candidates = [name, name + '.ets', name + '.d.ets', name + '.ts', name + '.d.ts',
        path.join(name, 'index.ets'), path.join(name, 'index.d.ets'), path.join(name, 'index.ts'), path.join(name, 'index.d.ts')];
      const found = candidates.map(n => path.resolve(path.dirname(containing), n))
        .find(f => fs.existsSync(f) && fs.statSync(f).isFile());
      if (found) return {resolvedFileName: found, extension: found.endsWith('.d.ts') ? ts.Extension.Dts : ts.Extension.Ts};
    }
    return ts.resolveModuleName(name, containing, options, host).resolvedModule;
  }
  if (!context.host || context.resolveModule) host.resolveModuleNames = (names, containing) => names.map(name => resolve(name, containing));
  const metadataReads = new Map();
  const originalRead = host.readFile?.bind(host);
  if (originalRead) host.readFile = (file, ...args) => {
    const text = originalRead(file, ...args);
    if (typeof text === 'string' && file.endsWith('.json') && fs.existsSync(file)) {
      metadataReads.set(real(file), {file: real(file), sha256: digest(file)});
    }
    return text;
  };
  let program;
  try { program = ts.createProgram(roots.map(f => path.resolve(f)), options, host); }
  finally { if (originalRead) host.readFile = originalRead; }
  const checker = program.getTypeChecker();
  const sources = new Map(program.getSourceFiles().map(source => [real(source.fileName), source]));
  const declarations = [], firstPassDiagnostics = [], scopes = new Map();
  const isStruct = node => ts.isStructDeclaration(node);
  function resolvedSymbol(node) {
    let symbol = checker.getSymbolAtLocation(node);
    if (symbol?.flags & ts.SymbolFlags.Alias) symbol = checker.getAliasedSymbol(symbol);
    return symbol;
  }
  function structs(symbol) { return (symbol?.declarations || []).filter(isStruct); }
  function record(scope, name, declaration, kind) {
    scope.names.add(name);
    const source = declaration.getSourceFile();
    declarations.push({file: scope.file, name, kind, originFile: real(source.fileName),
      originName: declaration.name?.text, originSha256: digest(source.fileName),
      originStart: declaration.getStart(source), originEnd: declaration.end});
  }
  for (const source of sources.values()) {
    if (!source.fileName.endsWith('.ets')) continue;
    const scope = {file: real(source.fileName), names: new Set()};
    scopes.set(scope.file, scope);
    firstPassDiagnostics.push({file: scope.file, count: source.parseDiagnostics.length,
      codes: source.parseDiagnostics.map(diagnostic => diagnostic.code)});
    for (const statement of source.statements) {
      if (isStruct(statement) && statement.name) record(scope, statement.name.text, statement, 'local');
      if (!ts.isImportDeclaration(statement) || !statement.importClause) continue;
      const clause = statement.importClause;
      if (clause.name) for (const declaration of structs(resolvedSymbol(clause.name))) {
        record(scope, clause.name.text, declaration, 'default-import');
      }
      const bindings = clause.namedBindings;
      if (bindings && ts.isNamedImports(bindings)) for (const element of bindings.elements) {
        for (const declaration of structs(resolvedSymbol(element.name))) record(scope, element.name.text, declaration, 'named-import');
      }
      if (bindings && ts.isNamespaceImport(bindings)) {
        const symbol = resolvedSymbol(bindings.name);
        if (symbol) for (const exported of checker.getExportsOfModule(symbol)) {
          const target = exported.flags & ts.SymbolFlags.Alias ? checker.getAliasedSymbol(exported) : exported;
          for (const declaration of structs(target)) record(scope, exported.getName(), declaration, 'namespace-import');
        }
      }
    }
  }
  const inputFiles = [...new Map([...metadataReads.values(), ...[...sources.values()].map(source =>
    ({file: real(source.fileName), sha256: digest(source.fileName)}))].map(record => [record.file, record])).values()]
    .sort((a, b) => a.file.localeCompare(b.file));
  function forFile(file) {
    const scope = scopes.get(real(file));
    if (!scope) throw new Error('ETS source is outside the measured component context: ' + file);
    return {...options, ets: {...options.ets,
      components: [...new Set([...(options.ets.components || []), ...scope.names])].sort()}};
  }
  const provenance = {
    helper: {file: __filename, sha256: digest(__filename)},
    files: inputFiles,
    scopes: [...scopes.values()].map(scope => ({file: scope.file, componentNames: [...scope.names].sort()}))
      .sort((a, b) => a.file.localeCompare(b.file)),
    declarations, firstPassDiagnostics,
    componentNames: [...new Set([...scopes.values()].flatMap(scope => [...scope.names]))].sort()
  };
  return {options, forFile, ...provenance, provenance};
}

module.exports = {withCustomComponents};
