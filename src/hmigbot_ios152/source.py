"""One source context shared by UI, API, profiles and ownership scans."""
from pathlib import Path
import json
import re
from hmigbot_ios.core import MigrationError, snapshot, safe_child
from hmigbot_ios.swiftui import tokenize

CODE={'.swift','.m','.mm','.h','.c','.cpp'}
EXCLUDED={'Pods','Carthage','.build','DerivedData','build','Tests','UITests','test','tests'}

def config(project):
    p=Path(project)/'.migbot/config.json'
    return json.loads(p.read_text(encoding='utf-8-sig')) if p.is_file() else {}

def ios_source(src, project=None):
    if any(Path(src).rglob('*.xcodeproj')) or (Path(src)/'Package.swift').is_file(): return True
    if project and config(project).get('source_platform')=='ios': return True
    return next(Path(src).rglob('*.swift'),None) is not None or next(Path(src).rglob('*.m'),None) is not None

def migration_members(root,selection):
    """Embedded products belong to the build closure, not implicitly to user scope."""
    from hmigbot_ios.xcode import OpenStep
    objects=OpenStep(safe_child(Path(root),selection['project_path']).read_text(encoding='utf-8-sig')).parse()['objects']
    products={v['name'] for v in objects.values() if v.get('productType') in {
              'com.apple.product-type.application','com.apple.product-type.app-extension'}}
    allowed=(set(selection['target_closure'])-products)|set(selection['targets'])
    return {f['path'] for f in selection['source_membership'] if set(f['targets'])&allowed}

class Source:
    def __init__(self, root, project=None):
        if project is None:
            for candidate in (Path.cwd(),*Path.cwd().parents):
                cfg=config(candidate); ios=cfg.get('ios',{})
                value=ios.get('source_root') if isinstance(ios,dict) else ios
                value=value or cfg.get('android')
                if value and (candidate/value).resolve()==Path(root).resolve(): project=candidate; break
        self.root=Path(root).resolve(); self.project=Path(project).resolve() if project else None
        self.config=config(project) if project else {}
        self.view=None; self.selection=None
        if project:
            from hmigbot_ios.conditional_source import for_project
            self.view=for_project(self.project,self.root)
            ios=self.config.get('ios',{})
            variant=ios.get('variant') if isinstance(ios,dict) else None
            if variant:
                from hmigbot_ios.project_scope import resolve
                self.selection=resolve(self.root,variant)
        snap=snapshot(self.root)
        self.fingerprint=snap['sha256']
        self.records={f['path']:f for f in snap['files']}
        self.files={p for p in self.records if Path(p).suffix in CODE and Path(p).name!='Package.swift'
                    and not EXCLUDED.intersection(Path(p).parts)}
        if self.selection: self.files.intersection_update(migration_members(self.root,self.selection))
        if self.view: self.files={p for p in self.files if self.view.includes(p)}
        self._text={}; self._tokens={}; self._syntax=None

    def syntax(self, name):
        if Path(name).suffix != '.swift': return None
        if self._syntax is None:
            from hmigbot_ios.apple_tools import syntax
            from hmigbot_ios.core import digest
            inputs=[]
            for path in sorted(p for p in self.files if p.endswith('.swift')):
                text=self.view.text(path) if self.view else safe_child(self.root,path).read_text(encoding='utf-8-sig')
                inputs.append({'path':path,'sha256':digest(text.encode('utf-8')),'source':text})
            self._syntax=syntax(inputs) if inputs else {}
        return self._syntax[name]

    def text(self, name):
        if name not in self._text:
            self._text[name]=self.view.text(name) if self.view else safe_child(self.root,name).read_text(encoding='utf-8-sig')
            if Path(name).suffix=='.swift' and not self.view:
                # Selecting DEBUG=false is insufficient for canImport/os/SDK conditions.
                # Technical input gaps are surfaced rather than silently profiling both branches.
                if any(n['kind']=='conditional_compilation' for n in self.syntax(name)['nodes']):
                    raise MigrationError('Release source view required for conditional Swift: '+name+
                        '; import Xcode Release settings and run prepare-source with SwiftIfConfig')
        return self._text[name]

    def tokens(self,name):
        if name not in self._tokens:
            self.text(name)
            if name.endswith('.swift'):
                from hmigbot_ios.apple_tools import mapped_tokens
                self._tokens[name]=mapped_tokens(self.syntax(name)['tokens'])
            else: self._tokens[name]=tokenize(self.text(name))
        return self._tokens[name]

    def code(self,name,strings=False):
        text=self.text(name); result=list(text)
        tokens=self.tokens(name)
        # Whitespace and positions remain unchanged; comments never become evidence.
        for index,c in enumerate(result):
            if c not in '\r\n': result[index]=' '
        for token in tokens:
            if token.kind=='regex' or token.kind=='string' and not strings: continue
            result[token.start:token.end]=text[token.start:token.end]
        return ''.join(result)

def anchors(md, source):
    """Read file-level source_anchors; legacy fields remain accepted on import."""
    text=Path(md).read_text(encoding='utf-8-sig')
    names=[]
    for m in re.finditer(r'(?:path:\s*|:\s*[\"\'])([^\n\"\']+\.(?:swift|mm|m|h|c|cpp))',text):
        value=m.group(1).strip().strip('"\'').replace('\\','/')
        if value in source.files and value not in names: names.append(value)
    # Glob anchors have the same file-level meaning, never one AC per assignment.
    for value in re.findall(r'path:\s*[\"\']?([^\n\"\']*[*?][^\n\"\']*)',text):
        for p in sorted(source.files):
            if Path(p).match(value.strip()) and p not in names: names.append(p)
    return names

def declarations(source,name):
    if name.endswith('.swift'):
        source.text(name)
        result=set()
        for n in source.syntax(name)['nodes']:
            v=n['value']
            if n['kind'] in {'type','function'}: result.add(v['name'].strip('`'))
            elif n['kind']=='extension': result.add(v['type'].split('.')[0].strip('`'))
        return result
    code=source.code(name)
    return set(re.findall(r'\b(?:class|struct|enum|protocol|func|extension|interface|implementation)\s+([\w]+)',code))

def entrypoints(source):
    """Native counterparts of declared screen entry points, not all UI components."""
    types={}; requested=set(); app_roots=[]
    for name in sorted(source.files):
        code=source.code(name)
        if name.endswith('.swift'):
            for n in source.syntax(name)['nodes']:
                v=n['value']; bases=v.get('inherits',[])
                base_names={word for base in bases for word in re.findall(r'\b\w+\b',base)}
                if n['kind']=='type' and v['kind'] in {'class','struct'} and base_names&{'App','View','UIViewController','UINavigationController','UITabBarController'}:
                    symbol=v['name'].strip('`')
                    types[symbol]={'short':symbol,'file':name,'line':n['line'],'kind':', '.join(bases)}
                    if 'App' in base_names and '@main' in v.get('attributes',''): app_roots.append(symbol)
        for m in ([] if name.endswith('.swift') else re.finditer(r'\b(?:class|struct|interface)\s+(\w+)(?:<[^>]+>)?\s*:\s*([^\{\n]+)',code)):
            if re.search(r'\b(?:App|View|UIViewController|UINavigationController|UITabBarController)\b',m[2]):
                types[m[1]]={'short':m[1],'file':name,'line':code.count('\n',0,m.start())+1,
                             'kind':m[2].strip()}
                if re.search(r'\bApp\b',m[2]) and '@main' in code[max(0,m.start()-60):m.start()]: app_roots.append(m[1])
        for pattern in [r'\b(?:WindowGroup|NavigationLink|navigationDestination|sheet|fullScreenCover)\b[^\{\n]*\{\s*(\w+)\s*\(',
                        r'\b(?:pushViewController|present)\s*\(\s*(\w+)\s*\(',
                        r'\brootViewController\s*=\s*(\w+)\s*\(',
                        r'\b(?:pushViewController|presentViewController):\s*\[\[\s*(\w+)\s+alloc\]']:
            requested.update(re.findall(pattern,code))
    requested.update(app_roots)
    # Storyboard initial controllers and storyboard IDs are declarations; reusable XIB views are not screens.
    import xml.etree.ElementTree as ET
    for path in sorted(p for p in source.records if p.endswith('.storyboard')):
        raw=safe_child(source.root,path).read_bytes()
        if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper(): raise MigrationError('Unsupported XML entities in '+path)
        tree=ET.fromstring(raw)
        for node in tree.iter():
            cls=node.get('customClass')
            if cls and (node.get('id')==tree.get('initialViewController') or node.get('storyboardIdentifier')):
                requested.add(cls)
    return [types[n] for n in sorted(requested) if n in types]
