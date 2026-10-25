'use strict';
// Read-only facts from the installed official SDK parser. No source rewriting.
const fs = require('fs');
const crypto = require('crypto');
const path = require('path');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const ts = require(input.parserModule);
const parserEntry = require.resolve(input.parserModule);
let loader = path.dirname(parserEntry);
while (path.basename(loader) !== 'ets-loader' && path.dirname(loader) !== loader) loader = path.dirname(loader);
const configPath = path.join(loader, 'tsconfig.json');
if (path.basename(loader) !== 'ets-loader' || !fs.existsSync(configPath) || typeof ts.ScriptKind.ETS !== 'number') {
  throw new Error('Selected parser is not an official ets-loader SDK with its configuration');
}
const compilerOptions = JSON.parse(fs.readFileSync(configPath, 'utf8')).compilerOptions;
if (!compilerOptions?.ets) throw new Error('Official SDK ETS parser configuration is unavailable');
function componentHelper() {
  if (input.componentHelper) return input.componentHelper;
  for (let directory = __dirname; ; directory = path.dirname(directory)) {
    const runtime = path.join(directory, 'runtime.json');
    if (fs.existsSync(runtime)) {
      const root = path.resolve(directory, JSON.parse(fs.readFileSync(runtime, 'utf8')).runtime_relative);
      const helper = path.join(root, 'src/hmigbot_ios152/ets_components.cjs');
      if (fs.existsSync(helper)) return helper;
    }
    const helper = path.join(directory, 'src/hmigbot_ios152/ets_components.cjs');
    if (fs.existsSync(helper)) return helper;
    if (directory === path.dirname(directory)) break;
  }
  throw new Error('Bundled ETS component context helper is unavailable');
}
const converted = ts.convertCompilerOptionsFromJson(compilerOptions, loader);
const componentContext = require(componentHelper()).withCustomComponents(ts, input.files,
  {...converted.options, ets: compilerOptions.ets, noEmit: true, allowNonTsExtensions: true});
const facts = {};
function named(node, source) { return node?.name ? node.name.getText(source) : undefined; }
function expressionName(node, source) { return node ? node.getText(source) : ''; }
for (const file of input.files) {
  const text = fs.readFileSync(file, 'utf8');
  const source = ts.createSourceFile(file, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.ETS, componentContext.forFile(file));
  const customNames = new Set(componentContext.scopes.find(scope => scope.file === fs.realpathSync(file)).componentNames
    .filter(name => !compilerOptions.ets.components.includes(name)));
  const item = {sha256: crypto.createHash('sha256').update(text).digest('hex'),
    declarations: [], imports: [], reexports: [], instances: [], types: [], references: [], methods: [], objects: [], bindings: [], writes: [], calls: [], comments: [], literals: [],
    diagnostics: source.parseDiagnostics.map(d => {
      const position = source.getLineAndCharacterOfPosition(d.start || 0);
      return {start: d.start, length: d.length, code: d.code,
        line: position.line + 1, columnUtf16: position.character + 1,
        message: ts.flattenDiagnosticMessageText(d.messageText, '\n')};
    })};
  const commentsAt = (position, trailing = false) => (trailing ? ts.getTrailingCommentRanges(text, position) : ts.getLeadingCommentRanges(text, position)) || [];
  function collectComments(node) {
    const values = new Map();
    function add(ranges) { for (const c of ranges) values.set(c.pos + ':' + c.end, {start: c.pos, end: c.end, text: text.slice(c.pos, c.end)}); }
    function walk(n) { add(commentsAt(n.pos)); add(commentsAt(n.end, true));
      if (ts.isBlock(n)) add(commentsAt(n.getStart(source) + 1)); ts.forEachChild(n, walk); }
    walk(node);
    if (ts.isBlock(node)) add(commentsAt(node.getStart(source) + 1));
    return [...values.values()];
  }
  function statementInfo(node) {
    return {start: node.getStart(source), end: node.end, text: node.getText(source),
      comments: collectComments(node), kind: ts.SyntaxKind[node.kind]};
  }
  function visit(node) {
    const name = named(node, source);
    if (name && node.members && (ts.isClassDeclaration(node) || ts.isInterfaceDeclaration(node) ||
      (ts.isStructDeclaration && ts.isStructDeclaration(node)) || ts.SyntaxKind[node.kind] === 'StructDeclaration')) {
      const heritage = (node.heritageClauses || []).flatMap(h => h.types.map(t => t.expression.getText(source)));
      const properties = (node.members || []).filter(m => m.name && m.type).map(m =>
        ({name: m.name.getText(source).replace(/^['"]|['"]$/g, ''), type: m.type.getText(source)}));
      item.declarations.push({name, kind: ts.SyntaxKind[node.kind], heritage, properties,
        default: !!node.modifiers?.some(m => m.kind === ts.SyntaxKind.DefaultKeyword), start: node.getStart(source), end: node.end});
    }
    if (ts.isImportDeclaration(node) && node.importClause) {
      const bindings = node.importClause.namedBindings;
      const names = bindings?.elements?.map(e => ({imported: (e.propertyName || e.name).text, local: e.name.text})) || [];
      if (node.importClause.name) names.push({imported: 'default', local: node.importClause.name.text});
      item.imports.push({source: node.moduleSpecifier.text, names,
        namespace: bindings && ts.isNamespaceImport(bindings) ? bindings.name.text : undefined});
    }
    if (ts.isExportDeclaration(node)) {
      const names = node.exportClause?.elements?.map(e => ({imported: (e.propertyName || e.name).text, exported: e.name.text}));
      item.reexports.push({source: node.moduleSpecifier?.text || null, names: names || null});
    }
    if (ts.isNewExpression(node)) item.instances.push({name: expressionName(node.expression, source), kind: 'new', start: node.getStart(source)});
    const componentName = node.expression && (ts.isIdentifier(node.expression) ? node.expression.text
      : ts.isPropertyAccessExpression(node.expression) ? node.expression.name.text : undefined);
    if (ts.isCallExpression(node) || ts.isEtsComponentExpression?.(node) && customNames.has(componentName)) {
      const expression = node.expression;
      item.calls.push({callee: expression.getText(source), args: node.arguments.map(a => a.getText(source))});
      if (ts.isIdentifier(expression) && /^[A-Z]/.test(expression.text)) item.instances.push({name: expression.text, kind: 'render', start: node.getStart(source)});
      if (ts.isPropertyAccessExpression(expression) && expression.name.text === 'getInstance') item.instances.push({name: expression.expression.getText(source), kind: 'getInstance', start: node.getStart(source)});
    }
    if (ts.isNewExpression(node)) item.calls.push({callee: 'new ' + node.expression.getText(source), args: (node.arguments || []).map(a => a.getText(source))});
    if ((ts.isVariableDeclaration(node) || ts.isParameter(node) || ts.isPropertyDeclaration(node)) && name) {
      let value = node.initializer;
      while (value && ts.isParenthesizedExpression(value)) value = value.expression;
      const statement = node.parent?.parent;
      item.bindings.push({name: ts.isPropertyDeclaration(node) ? 'this.' + name : name,
        expression: value?.getText(source), identifier: value && ts.isIdentifier(value) ? value.text : undefined,
        constructor: value && ts.isNewExpression(value) ? value.expression.getText(source) : undefined,
        const: ts.isVariableDeclaration(node) && !!(node.parent.flags & ts.NodeFlags.Const),
        topLevel: ts.isVariableDeclaration(node) && statement?.parent === source,
        exported: !!statement?.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword)});
    }
    if (ts.isBinaryExpression(node) && node.operatorToken.kind >= ts.SyntaxKind.FirstAssignment && node.operatorToken.kind <= ts.SyntaxKind.LastAssignment) item.writes.push(node.left.getText(source));
    if (ts.isDeleteExpression(node)) item.writes.push(node.expression.getText(source));
    if ((ts.isPrefixUnaryExpression(node) || ts.isPostfixUnaryExpression(node)) &&
      [ts.SyntaxKind.PlusPlusToken, ts.SyntaxKind.MinusMinusToken].includes(node.operator)) item.writes.push(node.operand.getText(source));
    if (ts.isTypeReferenceNode(node)) item.types.push(node.typeName.getText(source));
    if (ts.isPropertyAccessExpression(node)) item.references.push({text: node.getText(source), start: node.getStart(source), end: node.end});
    if (ts.isVariableDeclaration(node) && node.initializer && ts.isObjectLiteralExpression(node.initializer)) {
      const properties = [];
      for (const prop of node.initializer.properties) {
        if (!ts.isPropertyAssignment(prop)) continue;
        const value = prop.initializer;
        properties.push({name: prop.name.getText(source).replace(/^['"]|['"]$/g, ''),
          constructor: ts.isNewExpression(value) ? value.expression.getText(source) : undefined,
          identifier: ts.isIdentifier(value) ? value.text : undefined,
          expression: value.getText(source)});
      }
      const statement = node.parent?.parent;
      item.objects.push({name, properties, type: node.type?.getText(source),
        closedLiteral: node.initializer.properties.every(p => ts.isPropertyAssignment(p) &&
          (ts.isIdentifier(p.name) || ts.isStringLiteral(p.name))),
        exported: !!statement?.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword)});
    }
    if (ts.isStringLiteral(node) || node.kind === ts.SyntaxKind.RegularExpressionLiteral ||
      node.kind === ts.SyntaxKind.NoSubstitutionTemplateLiteral || ts.isTemplateExpression(node)) {
      item.literals.push({start: node.getStart(source), end: node.end});
    }
    const isArrowMember = ts.isArrowFunction(node) && node.parent?.name &&
      (ts.isPropertyDeclaration(node.parent) || ts.isPropertyAssignment(node.parent));
    const methodName = isArrowMember ? named(node.parent, source) : name;
    if ((ts.isMethodDeclaration(node) || ts.isFunctionDeclaration(node) || ts.isGetAccessorDeclaration(node) || ts.isSetAccessorDeclaration(node) || isArrowMember) && methodName && node.body) {
      const start = node.body.getStart(source);
      const block = ts.isBlock(node.body);
      item.methods.push({name: methodName, nameStart: (isArrowMember ? node.parent.name : node.name).getStart(source), start: node.getStart(source), end: node.end, bodyStart: start, bodyEnd: node.body.end, block,
        body: text.slice(start + (block ? 1 : 0), node.body.end - (block ? 1 : 0)), comments: collectComments(node.body),
        leading: commentsAt(node.pos).map(c => ({start: c.pos, end: c.end, text: text.slice(c.pos, c.end)})),
        statements: (node.body.statements || []).map(statementInfo),
        diagnostics: item.diagnostics.filter(d => d.start >= start && d.start < node.body.end)});
    }
    ts.forEachChild(node, visit);
  }
  visit(source);
  item.comments = collectComments(source);
  // TypeScript offsets count UTF-16 units; Python indexes Unicode code points.
  const pointAt = new Uint32Array(text.length + 1);
  for (let u = 0, point = 0; u < text.length; point++) {
    pointAt[u] = point;
    const width = text.codePointAt(u) > 0xFFFF ? 2 : 1;
    if (width === 2) pointAt[u + 1] = point;
    u += width;
    pointAt[u] = point + 1;
  }
  const positions = new Set(['start', 'end', 'nameStart', 'bodyStart', 'bodyEnd']);
  function codePointPositions(value) {
    if (Array.isArray(value)) return value.map(codePointPositions);
    if (value && typeof value === 'object') {
      if ('code' in value && 'length' in value && 'start' in value) {
        return {nativeStartUtf16: value.start, nativeLengthUtf16: value.length, code: value.code,
          line: value.line, columnUtf16: value.columnUtf16, message: value.message};
      }
      return Object.fromEntries(Object.entries(value).map(([key, entry]) =>
        [key, positions.has(key) && typeof entry === 'number' ? pointAt[entry] : codePointPositions(entry)]));
    }
    return value;
  }
  facts[file] = {...codePointPositions(item), positionEncoding: 'unicode-codepoint'};
}
process.stdout.write(JSON.stringify({runId: input.runId, parser: input.parserModule, parserEntry,
  parserSha256: crypto.createHash('sha256').update(fs.readFileSync(parserEntry)).digest('hex'),
  configPath, configSha256: crypto.createHash('sha256').update(fs.readFileSync(configPath)).digest('hex'),
  sdkSelection: input.sdkSelection, version: ts.version, nodeVersion: process.version,
  nodeExecutable: process.execPath, componentContext: componentContext.provenance, files: facts}));
