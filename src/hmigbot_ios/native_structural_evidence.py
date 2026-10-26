"""Bounded source evidence for native integration points; this is not a compiler.

Only explicit, typed source paths are recognized. Unknown or ambiguous syntax
fails for review, never passes by name.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re

from .behavior import _target_tokens, _target_pairs, _selected_handler_bodies
from .core import MigrationError, read_json, safe_child

SKIP = {'oh_modules','node_modules','build','.git','.hmigbot-ios','.agents','.codex','.preview','.cxx'}
TEST_PARTS = {'test','tests','ohosTest','__tests__'}
IDENT = re.compile(r'^[A-Za-z_$][A-Za-z0-9_$]*$')


@dataclass
class Member:
    name: str
    index: int
    kind: str
    static: bool
    type_tokens: list
    body: tuple | None = None
    decorators: tuple = ()


@dataclass
class Definition:
    source: object
    name: str
    start: int
    end: int
    members: dict
    kind: str = 'class'
    exported: bool = False


@dataclass
class Binding:
    name: str
    index: int
    kind: str
    exported: bool
    type_tokens: list
    initializer: int | None = None


class Source:
    def __init__(self, path, project):
        self.path = path
        self.relative = path.relative_to(project).as_posix()
        self.text = path.read_text(encoding='utf-8-sig')
        self.tokens = _target_tokens(self.text)
        self.pairs = _target_pairs(self.tokens)
        self.values = [t.value for t in self.tokens]
        self.imports = self._imports()
        self.reexports = self._imports('export')
        self.bindings = self._bindings()
        self.definitions = []
        for i, token in enumerate(self.tokens[:-2]):
            if token.value not in {'class','struct','interface'} or not IDENT.fullmatch(self.values[i+1]):
                continue
            opening = i + 2
            while opening < len(self.tokens) and self.values[opening] not in {'{',';'}:
                opening += 1
            if opening not in self.pairs:
                continue
            end = self.pairs[opening]
            exported=i>0 and self.values[i-1]=='export' or i>1 and self.values[i-2:i]==['export','default']
            self.definitions.append(Definition(self,self.values[i+1],opening,end,self._members(opening,end),token.value,exported))

    def _imports(self, keyword='import'):
        active = {t.line for t in self.tokens if t.value == keyword and not t.literal}
        imports = {}
        pattern = r"(?m)^"+keyword+r"[ \t]+\{([^}]+)\}\s+from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(pattern,self.text):
            if self.text[:match.start()].count('\n')+1 not in active:
                continue
            raw = match[2]
            if not raw.startswith('.'):
                continue
            target = (self.path.parent / raw).with_suffix('.ets').resolve()
            for part in match[1].split(','):
                names = re.fullmatch(r'\s*([\w$]+)(?:\s+as\s+([\w$]+))?\s*',part)
                if names:
                    local = names[2] or names[1]
                    imports.setdefault(local,[]).append((target,names[1]))
        return imports

    def _bindings(self):
        result={}; cursor=0
        while cursor<len(self.tokens)-1:
            if self.values[cursor] in {'const','let','var'} and IDENT.fullmatch(self.values[cursor+1]):
                name=self.values[cursor+1]; after=cursor+2; types=[]
                if after<len(self.tokens) and self.values[after]==':':
                    start=after+1;after=start
                    while after<len(self.tokens) and self.values[after] not in {'=',';'} and self.tokens[after].line==self.tokens[start].line:
                        after+=1
                    types=self.tokens[start:after]
                initializer=after+1 if after<len(self.tokens) and self.values[after]=='=' else None
                result.setdefault(name,[]).append(Binding(name,cursor+1,self.values[cursor],
                    cursor>0 and self.values[cursor-1]=='export',types,initializer))
            cursor=self.pairs[cursor]+1 if cursor in self.pairs else cursor+1
        return result

    def _decorators(self, index):
        result=[]; cursor=index-1
        modifiers={'private','public','protected','readonly','static','abstract','declare','override','async','get','set'}
        while cursor>=0:
            if self.values[cursor] in modifiers: cursor-=1; continue
            if cursor>0 and IDENT.fullmatch(self.values[cursor]) and self.values[cursor-1]=='@':
                result.insert(0,self.values[cursor]); cursor-=2; continue
            break
        return tuple(result)

    def _members(self, opening, end):
        result, i, declaration = {}, opening+1, opening+1
        while i < end:
            value = self.values[i]
            if IDENT.fullmatch(value) and i+1 < end:
                following = self.values[i+1]
                if following == '(' and i+1 in self.pairs:
                    bodies = _selected_handler_bodies(self.tokens,i,self.pairs)
                    bodies = [b for b in bodies if b < end]
                    if bodies:
                        body = bodies[0]
                        after = self.pairs[i+1]+1
                        types = self.tokens[after+1:body] if self.values[after] == ':' else []
                        kind = 'getter' if i > opening and self.values[i-1] == 'get' else 'method'
                        previous = self.values[declaration:i]
                        decorators=self._decorators(i)
                        member = Member(value,i,kind,'static' in previous,types,(body,self.pairs[body]),decorators)
                        result.setdefault(value,[]).append(member)
                        i = self.pairs[body]+1
                        declaration = i
                        continue
                elif following == ':' or following=='?' and i+2<end and self.values[i+2]==':':
                    type_start=i+3 if following=='?' else i+2
                    after=type_start
                    while after < end and self.values[after] not in {'=',';','}'} and self.tokens[after].line == self.tokens[i].line:
                        after += 1
                    types=self.tokens[type_start:after]
                    decorators=self._decorators(i)
                    result.setdefault(value,[]).append(Member(value,i,'field','static' in self.values[declaration:i],types,None,decorators))
            if i in self.pairs:
                i=self.pairs[i]+1
                declaration=i
            else:
                if value == ';': declaration=i+1
                i+=1
        return result


def _one(values):
    return values[0] if len(values) == 1 else None


def _event(definition, member, role):
    return {'role':role,'file':definition.source.relative,'line':definition.source.tokens[member.index].line,
            'class':definition.name,'member':member.name}


def product_source_roots(project):
    """Use declared HarmonyOS modules, never a project-wide ETS search.

    The bundled core reader accepts JSON-compatible JSON5 configuration. A
    configuration it cannot parse fails explicitly; it cannot widen the scan
    into historical evidence, test modules or arbitrary project directories.
    """
    profile=read_json(safe_child(project,'build-profile.json5'))
    modules=profile.get('modules') if isinstance(profile,dict) else None
    if not isinstance(modules,list) or not modules:
        raise MigrationError('Native source indexing requires declared build-profile modules')
    roots=[]; names=set(); paths=set()
    for declaration in modules:
        if not isinstance(declaration,dict):
            raise MigrationError('Malformed build-profile module declaration')
        name=declaration.get('name'); relative=declaration.get('srcPath')
        if not isinstance(name,str) or not name or name in names or not isinstance(relative,str) or not relative:
            raise MigrationError('Module needs a unique name and explicit srcPath')
        names.add(name)
        relative=relative[2:] if relative.startswith('./') else relative
        module=project if relative in {'','.'} else safe_child(project,relative)
        # safe_child's IO subclass adds Windows long-path prefixes when passed
        # to os.walk; keep path identities in their normal project namespace.
        module=Path(str(module))
        if module in paths or any(part in SKIP or part in TEST_PARTS or part.startswith('.')
                                  for part in module.relative_to(project).parts):
            raise MigrationError('Duplicate or non-product module source path')
        if module.relative_to(project).parts[:1] in [('spec',),('work',)]:
            raise MigrationError('Module source path points at control or historical evidence')
        paths.add(module)
        module_config=(module/'src/main/module.json5').resolve()
        if not module_config.is_relative_to(project):
            raise MigrationError('Configured module identity escapes project')
        config=read_json(module_config)
        identity=config.get('module') if isinstance(config,dict) else None
        if not isinstance(identity,dict) or identity.get('name')!=name or not identity.get('type'):
            raise MigrationError('Build-profile module differs from its main module identity: '+name)
        source=(module/'src/main/ets').resolve()
        if not source.is_relative_to(project):
            raise MigrationError('Configured product source escapes project: '+str(source))
        if source.is_dir(): roots.append(source)
    if not roots: raise MigrationError('No configured product ArkTS source root exists')
    return roots


class EvidenceIndex:
    def __init__(self, project):
        self.project = Path(project).resolve()
        self.sources = []
        self.source_roots=product_source_roots(self.project)
        for source_root in self.source_roots:
            for parent, directories, names in os.walk(source_root):
                directories[:] = sorted(d for d in directories if d not in SKIP|TEST_PARTS and not d.startswith('.'))
                for name in sorted(names):
                    path = Path(parent) / name
                    if path.suffix == '.ets':
                        resolved = path.resolve()
                        if not resolved.is_relative_to(source_root):
                            raise ValueError('Product source escapes configured source root: ' + str(path))
                        self.sources.append(Source(resolved,self.project))
        self.definitions = [d for s in self.sources for d in s.definitions]

    def definition(self, name, source=None):
        if source is None:
            return _one([d for d in self.definitions if d.name == name])
        local = [d for d in source.definitions if d.name == name]
        imports = source.imports.get(name,[])
        if local and imports: return None
        if local: return _one(local)
        binding = _one(imports)
        if binding is None: return None
        path, remote = binding
        return self._exported_definition(path,remote,set())

    def _exported_definition(self, path, name, seen):
        identity=(path,name)
        if identity in seen or len(seen)>=8: return None
        seen={*seen,identity}
        definitions=[d for d in self.definitions if d.name==name and d.source.path==path and d.exported]
        if definitions: return _one(definitions)
        source=next((source for source in self.sources if source.path==path),None)
        if source is None: return None
        forwarding=_one(source.reexports.get(name,[]))
        return self._exported_definition(*forwarding,seen) if forwarding else None

    def _binding(self, source, name):
        local=_one(source.bindings.get(name,[]))
        imported=_one(source.imports.get(name,[]))
        if local is not None and imported is not None: return None
        if local is not None: return source,local
        if imported is None: return None
        path,remote=imported
        provider=next((item for item in self.sources if item.path==path),None)
        if provider is None: return None
        binding=_one(provider.bindings.get(remote,[]))
        return (provider,binding) if binding and binding.exported else None

    def _binding_slot(self, source, name, slot):
        resolved=self._binding(source,name)
        if resolved is None: return None
        provider,binding=resolved
        values=[token.value for token in binding.type_tokens]
        if len(values)!=1: return None
        interface=self.definition(values[0],provider)
        if interface is None or interface.kind!='interface': return None
        field=_one(interface.members.get(slot,[]))
        if field is None: return None
        expected=self.member_type(interface,field)
        if expected is None: return None
        vals=provider.values; candidates=[]
        if binding.initializer is not None: candidates.append(binding.initializer)
        for index in range(len(vals)-2):
            if vals[index:index+2]==[binding.name,'='] and (index==0 or vals[index-1] not in {'.','const','let','var'}):
                candidates.append(index+2)
        # A local declaration or parameter with the shared export's name makes
        # producer binding ambiguous. No same-name inference is allowed.
        for index,token in enumerate(provider.tokens):
            if token.value!=binding.name or index==binding.index: continue
            if index and vals[index-1] in {'const','let','var'}: return None
            if index+1<len(vals) and vals[index+1]==':' and index and vals[index-1] in {'(',','}: return None
        producers=[]
        for opening in sorted(set(candidates)):
            if opening not in provider.pairs or vals[opening]!='{': return None
            entry=self._producer_entry(provider,opening)
            if entry is None: return None
            found=[]
            for start,end in self._segments_object(provider,opening):
                if vals[start:start+2]!=[slot,':']: continue
                if vals[start+2:start+3]!=['new'] or start+4>=end: return None
                constructor=self.definition(vals[start+3],provider)
                if constructor!=expected or vals[start+4]!='(' or provider.pairs.get(start+4)!=end-1: return None
                found.append({'role':'binding-producer','file':provider.relative,'line':provider.tokens[start].line,
                              'binding':binding.name,'slot':slot,'class':expected.name})
            if len(found)!=1: return None
            producers.extend([*found,*entry])
        if not producers: return None
        return expected,[{'role':'shared-binding','file':provider.relative,'line':provider.tokens[binding.index].line,
                          'binding':binding.name},_event(interface,field,'binding-interface'),*producers]

    def _producer_entry(self, provider, position):
        """A delayed producer must have an exact invocation from a product member.

        This is a bounded source chain, not a whole-program reachability claim.
        A declared but uncalled factory cannot initialize a shared export.
        """
        functions=[]; cursor=0; values=provider.values
        while cursor<len(values)-1:
            if values[cursor]=='function' and IDENT.fullmatch(values[cursor+1]):
                bodies=_selected_handler_bodies(provider.tokens,cursor+1,provider.pairs)
                functions.extend((cursor+1,body,provider.pairs[body]) for body in bodies)
            cursor=provider.pairs[cursor]+1 if cursor in provider.pairs else cursor+1
        enclosing=[item for item in functions if item[1]<position<item[2]]
        if not enclosing:
            # An initializer nested in any other block is unsupported.
            return [] if not any(values[start]=='{' and start<position<end
                                 for start,end in provider.pairs.items()) else None
        selected=_one(enclosing)
        if selected is None: return None
        declaration,begin,end=selected; name=values[declaration]
        if self._local_callable_contains(provider,begin,end,position): return None
        for consumer in self.sources:
            imported=_one(consumer.imports.get(name,[]))
            if consumer!=provider and imported!=(provider.path,name): continue
            if consumer!=provider and not (declaration>1 and values[declaration-2]=='export'): continue
            if consumer!=provider and consumer.bindings.get(name): continue
            for owner in consumer.definitions:
                for members in owner.members.values():
                    for member in members:
                        if not member.body: continue
                        left,right=member.body
                        if self._shadowed_parameter(consumer,name,left,right): continue
                        for index in range(left+1,right-1):
                            if consumer.values[index:index+2]!=[name,'(']: continue
                            if index and consumer.values[index-1] in {'.','function','new'}: continue
                            if self._local_callable_contains(consumer,left,right,index): continue
                            return [{'role':'producer-factory','file':provider.relative,
                                     'line':provider.tokens[declaration].line,'function':name},
                                    {'role':'producer-invocation','file':consumer.relative,
                                     'line':consumer.tokens[index].line,'class':owner.name,'member':member.name}]
        return None

    @staticmethod
    def _segments_object(source, opening):
        return EvidenceIndex._segments(source,opening)

    def top_binding_proof(self, relative, handler):
        provider=next((source for source in self.sources if source.relative==relative),None)
        if provider is None: return []
        binding=_one(provider.bindings.get(handler,[]))
        if binding is None or not binding.exported or binding.kind not in {'const','let'}: return []
        for consumer in self.sources:
            for index in range(len(consumer.values)-5):
                values=consumer.values
                if values[index:index+2]!=[handler,'.'] or values[index+3]!='.': continue
                if not any(member.body and member.body[0]<index<member.body[1]
                           and not self._local_callable_contains(consumer,*member.body,index)
                           for owner in consumer.definitions for members in owner.members.values() for member in members): continue
                if self._shadowed_parameter(consumer,handler,0,len(values)-1): continue
                resolved=self._binding(consumer,handler)
                if resolved is None or resolved[0]!=provider or resolved[1]!=binding: continue
                proof=self._binding_slot(consumer,handler,values[index+2])
                if proof is None: continue
                target,chain=proof
                member=_one(target.members.get(values[index+4],[]))
                if member is None or not self._consumed(target,member,index+5,source=consumer): continue
                return [*chain,{'role':'binding-consumer','file':consumer.relative,'line':consumer.tokens[index].line,
                                'member':values[index+4]},_event(target,member,'definition')]
        return []

    def member_type(self, definition, member):
        values=[t.value for t in member.type_tokens]
        # A single named class, optionally nullable. Arrays are only accepted
        # as provider collections below, never confused with a single value.
        named=[v for v in values if IDENT.fullmatch(v) and v not in {'undefined','null'}]
        if len(named)!=1 or any(v not in {named[0],'|','undefined','null','?'} for v in values):
            return None
        return self.definition(named[0],definition.source)

    def _provider(self, definition, member, expected):
        if member.kind != 'getter' or not member.body or self.member_type(definition,member) != expected:
            return None
        source=definition.source
        start,end=member.body
        vals=source.values
        # Bounded getters return an explicitly typed field or an element from
        # an explicitly typed collection. The declared return type alone is
        # insufficient evidence of a returned target object.
        returns=[]
        for i in range(start+1,end-3):
            if vals[i:i+3] != ['return','this','.']: continue
            field=_one(definition.members.get(vals[i+3],[]))
            if field is None or field.kind != 'field': continue
            types=[t.value for t in field.type_tokens]
            if self.member_type(definition,field) == expected:
                if vals[i+4] in {';','}'}:
                    returns.append(_event(definition,field,'provider-field'))
                continue
            named=[v for v in types if IDENT.fullmatch(v)]
            if len(named)!=1 or types not in [[named[0],'[',']']]: continue
            if self.definition(named[0],definition.source) != expected: continue
            after=i+4
            opening=after+2 if vals[after:after+3] == ['.','find','('] else after if vals[after]=='[' else None
            if opening in source.pairs:
                following=source.pairs[opening]+1
                if following==end or vals[following] in {';','}'}:
                    returns.append(_event(definition,field,'provider-collection'))
        return returns if returns else None

    def _self_provider(self, caller, provider, target):
        if (provider.kind!='method' or provider.static or not provider.body
                or self.member_type(caller,provider)!=target
                or self._segments(caller.source,provider.index+1)): return []
        source=caller.source; values=source.values; begin,end=provider.body
        returned=[]
        for index in range(begin+1,end):
            if values[index]!='return': continue
            if self._local_callable_contains(source,begin,end,index): continue
            if values[index+1:index+3]!=['this','.'] or values[index+4] not in {';','}'}: return []
            field=_one(caller.members.get(values[index+3],[]))
            if field is None or self.member_type(caller,field)!=target: return []
            returned.append(field)
        field=_one(returned)
        if field is None: return []
        for index in range(begin+1,end-6):
            if values[index:index+5]!=['this','.',field.name,'=','new']: continue
            if self._local_callable_contains(source,begin,end,index): continue
            if self.definition(values[index+5],source)!=target or values[index+6]!='(': return []
            closing=source.pairs.get(index+6)
            if closing is None or values[closing+1] not in {';','}'}: return []
            return [_event(caller,provider,'typed-self-provider'),_event(caller,field,'provider-field'),
                    {'role':'provider-initializer','file':source.relative,'line':source.tokens[index].line}]
        return []

    def _self_provider_calls(self, caller, handler, target, member):
        source=caller.source; values=source.values
        for begin,end,chain in self._handler_regions(caller,handler):
            for index in range(begin+1,end-4):
                if values[index:index+2]!=['this','.'] or values[index+3:index+5]!=['(',')']: continue
                if self._local_callable_contains(source,begin,end,index): continue
                provider=_one(caller.members.get(values[index+2],[]))
                if provider is None: continue
                proof=self._self_provider(caller,provider,target)
                if not proof: continue
                calls=[]
                if values[index+5:index+7]==['.',member.name]: calls.append(index+7)
                if index>=begin+4 and values[index-1]=='=' and values[index-3]=='const':
                    alias=values[index-2]
                    if IDENT.fullmatch(alias) and values[index+5]==';' and not self._shadowed_parameter(source,alias,index+5,end):
                        calls.extend(cursor+3 for cursor in range(index+6,end-3)
                                     if values[cursor:cursor+3]==[alias,'.',member.name]
                                     and not self._local_callable_contains(source,begin,end,cursor))
                for cursor in calls:
                    if self._consumed(caller,member,cursor):
                        return [{'role':'self-provider-call','file':source.relative,'line':source.tokens[cursor-2].line},
                                *chain,*proof,_event(target,member,'definition')]
        return []

    @staticmethod
    def _segments(source, opening):
        """Split direct arguments/parameters without splitting nested syntax."""
        end=source.pairs.get(opening)
        if end is None: return []
        result=[]; start=opening+1; cursor=start
        while cursor<end:
            if source.values[cursor]==',':
                result.append((start,cursor)); start=cursor+1
            cursor=source.pairs[cursor]+1 if cursor in source.pairs else cursor+1
        if start<end: result.append((start,end))
        return result

    def _parameter_calls(self, owner, method, target, member, parameter=None):
        if method.kind!='method' or not method.body or member.static: return []
        source=owner.source; values=source.values
        parameters=self._segments(source,method.index+1)
        for position,(start,end) in enumerate(parameters):
            if parameter is not None and position!=parameter: continue
            if start+2>=end or values[start+1]!=':': continue
            name=values[start]
            type_end=next((i for i in range(start+2,end) if values[i]=='='),end)
            typed=Member(name,start,'parameter',False,source.tokens[start+2:type_end])
            if self.member_type(owner,typed)!=target: continue
            begin,finish=method.body
            if self._shadowed_parameter(source,name,begin,finish): continue
            for i in range(begin+1,finish-2):
                if (values[i:i+3]==[name,'.',member.name] and self._consumed(owner,member,i+3)
                        and not self._local_callable_contains(source,begin,finish,i)):
                    return [_event(owner,method,'consumer-method'),_event(owner,typed,'typed-parameter'),
                            {'role':'parameter-call','file':source.relative,'line':source.tokens[i].line},
                            _event(target,member,'definition')]
        return []

    @staticmethod
    def _shadowed_parameter(source,name,begin,finish,object_keys=()):
        """Reject rebinding or any nested binding of the same parameter name.

        This deliberately rejects ambiguous forms instead of attempting JS
        lexical resolution. Capturing an unchanged parameter in an arrow (the
        normal store.write callback) remains supported.
        """
        values=source.values
        for index in range(begin+1,finish):
            if index in object_keys or values[index]!=name or values[index-1]=='.': continue
            following=values[index+1] if index+1<finish else ''
            if values[index-1] in {'const','let','var','class','function','catch'}:
                return True
            if following in {':','=','=>'}:
                return True
            # An untyped arrow/function argument can be a single identifier.
            for opening,closing in source.pairs.items():
                if values[opening]!='(' or not opening<index<closing: continue
                after=closing+1
                if after<len(values) and values[after]=='=>': return True
                if opening>0 and values[opening-1] in {'function','catch'}: return True
                if opening>1 and values[opening-2]=='function': return True
        return False

    def _handler_link(self, caller, handler, position, receiver, call_cursor):
        if handler.kind in {'method','getter'}:
            return any(begin<position<end and not self._local_callable_contains(caller.source,begin,end,position)
                       for begin,end,_ in self._handler_regions(caller,handler))
        if handler.kind!='field': return False
        if receiver==handler.name: return True
        source=caller.source
        if call_cursor>=len(source.values) or source.values[call_cursor]!='(': return False
        return any(source.values[start:end]==['this','.',handler.name]
                   for start,end in self._segments(source,call_cursor))

    @staticmethod
    def _local_callable_contains(source, begin, end, position):
        values=source.values
        for index in range(begin+1,min(position,end)):
            if values[index]=='function' and index+1<len(values):
                bodies=_selected_handler_bodies(source.tokens,index+1,source.pairs)
                if any(body<position<source.pairs[body] for body in bodies): return True
            if values[index] not in {'const','let','var'} or index+2>=end: continue
            cursor=index+2
            while cursor<end and values[cursor] not in {'=',';','{','}'}:
                cursor=source.pairs[cursor]+1 if cursor in source.pairs else cursor+1
            if cursor>=end or values[cursor]!='=': continue
            cursor+=1; arrow=None
            if cursor<end and values[cursor]=='function':
                arguments=cursor+1
                if arguments<end and IDENT.fullmatch(values[arguments]): arguments+=1
                if arguments in source.pairs and values[arguments]=='(':
                    body=source.pairs[arguments]+1
                    while body<end and values[body] not in {'{',';'}: body+=1
                    if body in source.pairs and body<position<source.pairs[body]: return True
            while cursor<end and values[cursor]!=';':
                if values[cursor]=='=>': arrow=cursor; break
                cursor=source.pairs[cursor]+1 if cursor in source.pairs else cursor+1
            if arrow is None or arrow>=position: continue
            body=arrow+1
            if body in source.pairs and values[body]=='{':
                if body<position<source.pairs[body]: return True
            elif position<end and not any(values[token]==';' for token in range(body,position)):
                return True
        return False

    def _handler_regions(self, caller, handler):
        if not handler.body: return []
        begin,end=handler.body
        regions=[(begin,end,[])]
        values=caller.source.values
        for index in range(begin+1,end-3):
            if values[index:index+2]!=['this','.'] or values[index+3]!='(': continue
            if self._local_callable_contains(caller.source,begin,end,index): continue
            helper=_one(caller.members.get(values[index+2],[]))
            if helper is None or helper is handler or helper.static or not helper.body: continue
            regions.append((*helper.body,[{'role':'handler-self-call','file':caller.source.relative,
                'line':caller.source.tokens[index].line,'from':handler.name,'to':helper.name},
                _event(caller,helper,'helper-definition')]))
        return regions

    def _handler_chain(self, caller, handler, position):
        for begin,end,chain in self._handler_regions(caller,handler):
            if begin<position<end: return chain
        return []

    @staticmethod
    def _scalar_type(member):
        values=[token.value for token in member.type_tokens]
        return frozenset(value for value in values if value!='|') if values and all(
            value in {'string','number','boolean','undefined','null','|'} for value in values) else None

    def _typed_scalar_write(self, caller, handler, target, member):
        source=caller.source; values=source.values
        if member.kind!='field': return []
        regions=self._handler_regions(caller,handler) if handler.body else [
            (*method.body,[]) for methods in caller.members.values() for method in methods if method.body]
        for begin,end,chain in regions:
            for index in range(begin+1,end-3):
                if self._local_callable_contains(source,begin,end,index): continue
                # Field/state <- exact typed receiver field, not an arbitrary
                # use of the target member somewhere in the component.
                if handler.kind=='field' and values[index:index+4]==['this','.',handler.name,'=']:
                    cursor=index+4
                    if values[cursor:cursor+2]!=['this','.']: continue
                    receiver=_one(caller.members.get(values[cursor+2],[]))
                    if receiver is None or self.member_type(caller,receiver)!=target: continue
                    if values[cursor+3:cursor+5]!=['.',member.name]: continue
                    following=cursor+5
                    if following>=len(values) or values[following] not in {';','}'}: continue
                    if self._scalar_type(handler)!=self._scalar_type(member) or self._scalar_type(member) is None: continue
                    return [{'role':'field-copy','file':source.relative,'line':source.tokens[index].line},
                            _event(caller,handler,'destination-field'),_event(caller,receiver,'typed-receiver'),
                            _event(target,member,'source-field')]
                # Planned method/getter -> this component's exact state field.
                if caller!=target or not handler.body or values[index:index+4]!=['this','.',member.name,'=']: continue
                cursor=index+4
                if cursor>=end: continue
                rhs=values[cursor]
                primitive=self._scalar_type(member)
                if primitive is None: continue
                allowed=False
                for start,finish in self._segments(source,handler.index+1):
                    if values[start]!=rhs or start+2>=finish or values[start+1]!=':': continue
                    parameter=Member(rhs,start,'parameter',False,source.tokens[start+2:finish])
                    if self._scalar_type(parameter)==primitive and not self._shadowed_parameter(source,rhs,begin,end): allowed=True
                if rhs in {'true','false'} and primitive==frozenset({'boolean'}): allowed=True
                if re.fullmatch(r'\d+',rhs) and primitive==frozenset({'number'}): allowed=True
                following=cursor+1
                if not allowed or following>=len(values) or values[following] not in {';','}'}: continue
                return [{'role':'self-field-write','file':source.relative,'line':source.tokens[index].line},
                        _event(caller,handler,'handler-definition'),_event(target,member,'destination-field'),*chain]
        return []

    def _typed_receiver_scalar_write(self, caller, handler, target, member, allowed):
        """A literal write through this exact, import-bound typed receiver."""
        if (not handler.body or handler.static or member.kind!='field' or member.static
                or caller.source.relative not in allowed or target.source.relative not in allowed): return []
        primitive=self._flow_scalar(member.type_tokens)
        if primitive is None: return []
        declaration=target.source.tokens[member.index]
        if any(token.value=='readonly' and token.line==declaration.line
               for token in target.source.tokens[max(target.start,member.index-4):member.index]): return []
        source=caller.source; values=source.values; begin,end=handler.body
        for index in range(begin+1,end-6):
            if values[index:index+2]!=['this','.'] or values[index+3:index+6]!=['.',member.name,'=']: continue
            receiver=_one(caller.members.get(values[index+2],[]))
            if receiver is None or receiver.kind!='field' or self.member_type(caller,receiver)!=target: continue
            rhs=values[index+6]; following=index+7
            if following>=len(values) or values[following] not in {';','}'}: continue
            actual=('boolean' if rhs in {'true','false'} else 'number' if re.fullmatch(r'\d+',rhs)
                    else rhs if rhs in {'undefined','null'} else None)
            if actual not in primitive: continue
            live=self._flow_callback_position_live(caller,handler,index,set(allowed))
            if not live: continue
            return [{'role':'typed-receiver-field-write','file':source.relative,'line':source.tokens[index].line,
                     'receiver':receiver.name,'member':member.name,'literal':rhs},
                    _event(caller,handler,'handler-definition'),_event(caller,receiver,'typed-receiver'),
                    *live,_event(target,member,'definition')]
        return []

    def _promise_result_carriers(self, owner, method, position):
        """A helper in typed then needs its result returned or stored, not idle."""
        source=owner.source; values=source.values; evidence=[]
        contexts=self._flow_arrow_contexts(source,*method.body,position)
        if contexts is None: return None
        for context in contexts:
            if not context['call']: continue
            opening,_=context['call']
            if values[opening-1]!='then': continue
            start=opening-5; close=source.pairs.get(opening)
            if start<method.body[0] or close is None or values[start:start+2]!=['this','.']: return None
            consumed=values[start-1]=='return'
            if start>=4 and values[start-4:start-2]==['this','.'] and values[start-1]=='=':
                field=_one(owner.members.get(values[start-2],[]))
                types=[token.value for token in field.type_tokens] if field else []
                consumed=bool(types[:2]==['Promise','<'] and types[-1:]==['>'])
            if values[start-3]=='const' and values[start-1]=='=':
                name=values[start-2]
                if not IDENT.fullmatch(name) or self._shadowed_parameter(source,name,close,method.body[1]): return None
                for cursor in range(close+1,method.body[1]-2):
                    live=self._flow_callback_position_live(owner,method,cursor,set([owner.source.relative]),service=True)
                    if values[cursor:cursor+3]==['return',name,';'] and live:
                        consumed=True; break
                    if (cursor+4<method.body[1] and values[cursor:cursor+4]==['this','.',values[cursor+2],'=']
                            and values[cursor+4:cursor+5]==[name] and live):
                        field=_one(owner.members.get(values[cursor+2],[]))
                        types=[token.value for token in field.type_tokens] if field else []
                        if types[:2]==['Promise','<'] and types[-1:]==['>']: consumed=True; break
            if not consumed: return None
            evidence.append({'role':'consumed-promise-result','file':source.relative,
                'line':source.tokens[start].line,'class':owner.name,'member':method.name})
        return evidence

    def _bounded_static_self_path(self, caller, handler, target, member, allowed):
        if (not handler.body or handler.static or not member.static or member.kind!='method'
                or caller.source.relative not in allowed): return []
        source=caller.source; values=source.values; pending=[(handler,[],0)]; visited=set()
        while pending:
            method,chain,depth=pending.pop(0)
            if method.name in visited: continue
            visited.add(method.name); begin,end=method.body
            for index in range(begin+1,end-3):
                if values[index:index+3]==[target.name,'.',member.name] and values[index+3]=='(':
                    if self.definition(target.name,source)!=target or self._shadowed_parameter(source,target.name,begin,end): continue
                    live=self._flow_callback_position_live(caller,method,index,set(allowed),service=True)
                    carrier=self._promise_result_carriers(caller,method,index)
                    if live and carrier is not None:
                        return [_event(caller,handler,'handler-definition'),*chain,*live,*carrier,
                            {'role':'bounded-static-call','file':source.relative,'line':source.tokens[index].line},
                            _event(target,member,'definition')]
                if depth>=2 or values[index:index+2]!=['this','.'] or values[index+3]!='(': continue
                callee=_one(caller.members.get(values[index+2],[]))
                if callee is None or callee.static or callee.kind!='method' or not callee.body: continue
                live=self._flow_callback_position_live(caller,method,index,set(allowed),service=True)
                carrier=self._promise_result_carriers(caller,method,index)
                if not live or carrier is None: continue
                edge={'role':'bounded-self-helper-call','file':source.relative,'line':source.tokens[index].line,
                      'from':method.name,'to':callee.name,'depth':depth+1}
                pending.append((callee,[*chain,edge,_event(caller,callee,'helper-definition'),*live,*carrier],depth+1))
        return []

    def _async_capture_rebound(self, source, name, begin, finish):
        keys=set(); values=source.values
        for opening,closing in source.pairs.items():
            if values[opening]!='{' or not begin<opening<closing<finish: continue
            if values[opening-1] in {'const','let','var'} and name in values[opening+1:closing]: return True
            if values[opening-1] in {'(', ',', '=', ':', 'return'}:
                keys.update(left for left,right in self._segments_object(source,opening)
                    if values[left+1:left+2]==[':'])
        return self._shadowed_parameter(source,name,begin,finish,keys)

    def _consumed_async_self_path(self, caller, handler, target, member, allowed):
        """One no-arg const async Promise<void> task, invoked in its handler.

        This grants no dynamic graph: the task can expose one exact typed self
        helper to the existing proof, whose recursive async fallback is disabled.
        """
        if not handler.body or handler.static or caller.source.relative not in allowed: return []
        source=caller.source; values=source.values; results=[]
        if 'Promise' in source.imports or 'Promise' in source.bindings or self.definition('Promise',source) is not None: return []
        begin,end=handler.body
        for declaration in range(begin+1,end-13):
            if values[declaration]!='const' or not IDENT.fullmatch(values[declaration+1]): continue
            if values[declaration+2:declaration+13]!=['=','async','(',')',':','Promise','<','void','>','=>','{']: continue
            opening=declaration+12; closing=source.pairs.get(opening); name=values[declaration+1]
            if closing is None or closing>=end or self._shadowed_parameter(source,name,begin,end,{declaration+1}): continue
            if not self._flow_callback_position_live(caller,handler,declaration,set(allowed)): continue
            invocations=[]
            for call in range(closing+1,end-2):
                if values[call:call+3]!=[name,'(',')']: continue
                if self._flow_arrow_contains(source,begin,end,call): continue
                live=self._flow_callback_position_live(caller,handler,call,set(allowed))
                if not live: continue
                consumed=values[call-1]=='await'
                if values[call+3:call+6]==['.','catch','('] and len(self._segments(source,call+5))==1: consumed=True
                if call>=4 and values[call-4:call-2]==['this','.'] and values[call-1]=='=':
                    field=_one(caller.members.get(values[call-2],[]))
                    if field and [token.value for token in field.type_tokens]==['Promise','<','void','>']: consumed=True
                if values[call-1]=='=':
                    for start in range(max(closing+1,call-8),call-1):
                        if values[start]=='const' and (values[start+2:call] in [['='],[':','Promise','<','void','>','=']]): consumed=True
                if consumed: invocations.append((call,live))
            if len(invocations)!=1: continue
            call,live=invocations[0]
            task=Member(name,declaration+1,'method',False,source.tokens[declaration+7:declaration+11],(opening,closing))
            for position in range(opening+1,closing-4):
                if values[position:position+2]!=['this','.'] or values[position+3]!='(': continue
                helper=_one(caller.members.get(values[position+2],[]))
                if (helper is None or helper is handler or not helper.body or helper.static
                        or [token.value for token in helper.type_tokens]!=['Promise','<','void','>']): continue
                inner=self._flow_callback_position_live(caller,task,position,set(allowed))
                if not inner or self._flow_arrow_contains(source,opening,closing,position): continue
                actual=self._segments(source,position+3); formal=self._segments(source,helper.index+1)
                if len(actual)!=len(formal): continue
                arguments=[]; valid=True
                for (left,right),(first,last) in zip(actual,formal):
                    if values[first+1:first+2]!=[':']: valid=False;break
                    expected=values[first+2:last]; expression=values[left:right]; found=[]
                    if len(expression)==1:
                        argument=expression[0]
                        if self._async_capture_rebound(source,argument,opening,closing): valid=False;break
                        for index in range(begin+1,declaration-2):
                            if values[index] in {'let','const'} and values[index+1:index+3]==[argument,':']:
                                finish=index+3
                                while finish<declaration and values[finish] not in {'=',';'}: finish+=1
                                if values[index+3:finish]==expected: found.append(index+1)
                        for start,finish in self._segments(source,handler.index+1):
                            if values[start:start+2]==[argument,':'] and values[start+2:finish]==expected: found.append(start)
                    elif len(expression)==3 and expression[:2]==['this','.']:
                        field=_one(caller.members.get(expression[2],[]))
                        if field and [token.value for token in field.type_tokens]==expected: found.append(field.index)
                    if len(found)!=1: valid=False;break
                    arguments.append({'role':'captured-task-argument','file':source.relative,'line':source.tokens[found[0]].line,'type':''.join(expected)})
                if not valid: continue
                proof=self.prove(caller.name+'.'+helper.name+' → '+target.name+'.'+member.name,allowed,_async_depth=1)
                if proof['status']!='PASS': continue
                results.append([_event(caller,handler,'handler-definition'),
                    {'role':'local-async-task-definition','file':source.relative,'line':source.tokens[declaration].line,'task':name},
                    {'role':'local-async-task-invocation','file':source.relative,'line':source.tokens[call].line,'task':name},
                    *live,*arguments,*inner,_event(caller,helper,'async-task-self-helper'),*proof['evidence']])
        return results[0] if len(results)==1 else []

    def _member_value_type(self, owner, member):
        scalar=self._flow_scalar(member.type_tokens)
        if scalar is not None: return ('scalar',scalar)
        definition=self.member_type(owner,member)
        if definition is None: return None
        nullable=frozenset(token.value for token in member.type_tokens if token.value in {'undefined','null'})
        return ('class',definition,nullable)

    def _typed_this_path(self, owner, values, allowed):
        if len(values)<3 or values[:2]!=['this','.']: return None
        current=owner; proof=[]; cursor=2; typed=None
        while cursor<len(values):
            member=_one(current.members.get(values[cursor],[]))
            if member is None: return None
            typed=self._member_value_type(current,member)
            if typed is None: return None
            proof.append(_event(current,member,'bound-value-field'))
            cursor+=1
            if cursor==len(values): break
            if values[cursor]=='!': cursor+=1
            if cursor>=len(values) or values[cursor]!='.' or typed[0]!='class': return None
            current=typed[1]
            if current.source.relative not in allowed: return None
            cursor+=1
        return (typed,proof) if cursor==len(values) else None

    @staticmethod
    def _value_assignable(actual, expected):
        if actual is None or expected is None or actual[0]!=expected[0]: return False
        return actual[1]<=expected[1] if actual[0]=='scalar' else actual[1]==expected[1] and actual[2]<=expected[2]

    def _component_build_live(self, target, member):
        if target.kind!='struct' or member.name!='build' or member.kind!='method' or not member.body: return False
        source=target.source; values=source.values; begin,end=member.body
        for index in range(begin+1,end-1):
            if values[index] not in {'Column','Row','Stack','Text','NavDestination','Navigation','Tabs','Scroll','Button'} or values[index+1]!='(': continue
            if (values[index] in source.imports or values[index] in source.bindings
                    or any(definition.name==values[index] for definition in source.definitions)): continue
            if self._flow_idle_local_contains(source,begin,end,index) or self._flow_arrow_contains(source,begin,end,index): continue
            return True
        return False

    def _sheet_handler_flow(self, caller, handler, target, member, allowed):
        if (not handler.body or handler.kind!='method' or handler.static
                or caller.source.relative not in allowed or not self._component_build_live(target,member)): return []
        source=caller.source; values=source.values; begin,end=handler.body
        prepared={}; states=[]
        for index in range(begin+1,end-4):
            if values[index:index+2]!=['this','.'] or values[index+3]!='=': continue
            field=_one(caller.members.get(values[index+2],[]))
            if field is None: continue
            live=self._flow_callback_position_live(caller,handler,index,set(allowed))
            if not live: continue
            if values[index+4:index+6]==['true',';'] and self._flow_scalar(field.type_tokens)==frozenset({'boolean'}):
                states.append((field,index,live))
            if values[index+4]=='new' and index+6<end and values[index+6]=='(':
                expected=self.member_type(caller,field); actual=self.definition(values[index+5],source)
                if expected is None or actual!=expected or actual.source.relative not in allowed: return []
                prepared[field.name]={'role':'prepared-sheet-value','file':source.relative,'line':source.tokens[index].line,'field':field.name}
        build=_one(caller.members.get('build',[]))
        if build is None or not build.body: return []
        matches=[]
        for instance in self._flow_instances(caller,set(allowed)):
            builder=instance['root']
            if instance['child'] is not target or builder.decorators!=('Builder',): continue
            arguments=[]; used_prepared=set(); valid=True
            for name,(start,finish) in instance['properties'].items():
                parameter=_one(target.members.get(name,[]))
                if parameter is None: valid=False; break
                if parameter.decorators==('Event',): continue
                if parameter.decorators!=('Param',): valid=False; break
                actual=self._typed_this_path(caller,values[start:finish],set(allowed))
                if actual is None or not self._value_assignable(actual[0],self._member_value_type(target,parameter)):
                    valid=False; break
                arguments.extend([*actual[1],_event(target,parameter,'bound-child-param')])
                if values[start:finish][:2]==['this','.'] and values[start+2] in prepared: used_prepared.add(values[start+2])
            if not valid or prepared and not used_prepared: continue
            for state,assignment,live in states:
                for index in range(build.body[0]+1,build.body[1]-2):
                    if values[index]!='.' or values[index+1] not in {'bindSheet','bindContentCover'} or values[index+2]!='(': continue
                    spans=self._segments(source,index+2)
                    if len(spans)<2: continue
                    first,second=spans[:2]
                    if values[first[0]:first[1]]!=['$$this','.',state.name] or values[second[0]:second[1]]!=['this','.',builder.name,'(',')']: continue
                    if not self._flow_callback_position_live(caller,build,index,set(allowed)): continue
                    matches.append([_event(caller,handler,'handler-definition'),*live,
                        {'role':'sheet-presentation-write','file':source.relative,'line':source.tokens[assignment].line,'state':state.name},
                        {'role':'same-state-sheet-binding','file':source.relative,'line':source.tokens[index].line,'state':state.name,'builder':builder.name},
                        *instance['evidence'],*arguments,*[prepared[name] for name in used_prepared],_event(target,member,'definition')])
        return _one(matches) or []

    @staticmethod
    def _literal_string(source, index):
        """Recover only an unescaped quoted string at this exact lexer token."""
        if index>=len(source.tokens) or not source.tokens[index].literal: return None
        cache=getattr(source,'literal_strings',{})
        if index in cache: return cache[index]
        value=None
        for match in re.finditer(r"'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\"",source.text):
            if source.text[:match.start()].count('\n')+1!=source.tokens[index].line: continue
            before=_target_tokens(source.text[:match.start()]); after=_target_tokens(source.text[:match.end()])
            if len(before)==index and len(after)==index+1 and after[-1].literal and '\\' not in match[0]:
                value=match[0][1:-1]; break
        cache[index]=value; source.literal_strings=cache
        return value

    def _is_nav_stack(self, owner, member):
        return (member is not None and member.kind=='field' and [token.value for token in member.type_tokens]==['NavPathStack']
                and not owner.source.imports.get('NavPathStack') and not owner.source.bindings.get('NavPathStack')
                and not any(definition.name=='NavPathStack' for definition in owner.source.definitions))

    def _navigation_render(self, root, method, span, target, route_parameter, primitive, stack, allowed, substitution=None):
        """The destination has one direct imported child or one typed Builder hop."""
        source=root.source; values=source.values; substitution=substitution or {}; matches=[]
        for index in range(span[0]+1,span[1]-3):
            if values[index]!=target.name or values[index+1:index+3]!=['(','{']: continue
            if self.definition(target.name,source)!=target or self._shadowed_parameter(source,target.name,*method.body): continue
            if not self._flow_callback_position_live(root,method,index,set(allowed)): continue
            close=source.pairs.get(index+1)
            if close is None or source.pairs.get(index+2)!=close-1: continue
            properties={}; valid=True
            for start,end in self._segments_object(source,index+2):
                if start+2>=end or values[start+1]!=':' or values[start] in properties: valid=False; break
                expression=values[start+2:end]
                properties[values[start]]=substitution.get(expression[0],expression) if len(expression)==1 else expression
            if not valid: continue
            stacks=[]; ids=[]; arguments=[]
            for name,expression in properties.items():
                parameter=_one(target.members.get(name,[]))
                if parameter is None: valid=False; break
                if parameter.decorators==('Event',): continue
                if parameter.decorators!=('Param',): valid=False; break
                if self._is_nav_stack(target,parameter):
                    if expression!=['this','.',stack]: valid=False; break
                    stacks.append(name)
                elif expression==[route_parameter,'as',next(iter(primitive))]:
                    if self._flow_scalar(parameter.type_tokens)!=primitive: valid=False; break
                    ids.append(name)
                else:
                    actual=self._typed_this_path(root,expression,set(allowed))
                    if actual is None or not self._value_assignable(actual[0],self._member_value_type(target,parameter)):
                        valid=False; break
                    arguments.extend(actual[1])
            if valid and len(stacks)==len(ids)==1:
                matches.append([{'role':'navigation-target-render','file':source.relative,'line':source.tokens[index].line,
                    'class':root.name,'member':method.name,'child':target.name,'stack':stack,'parameter':ids[0]},*arguments])
        if substitution: return _one(matches) or []
        for index in range(span[0]+1,span[1]-3):
            if values[index:index+2]!=['this','.'] or values[index+3]!='(': continue
            helper=_one(root.members.get(values[index+2],[]))
            if helper is None or helper.decorators!=('Builder',) or not helper.body: continue
            if not self._flow_callback_position_live(root,method,index,set(allowed)): continue
            actual=self._segments(source,index+3); formal=self._segments(source,helper.index+1)
            if len(actual)!=len(formal) or len(actual)!=2: continue
            mapping={}; valid=True
            for position,((start,end),(left,right)) in enumerate(zip(actual,formal)):
                expression=values[start:end]
                if left+2>=right or values[left+1]!=':': valid=False; break
                expected=[route_parameter,'as',next(iter(primitive))] if position==0 else ['this','.',stack]
                types=values[left+2:right]
                if expression!=expected or types!=([next(iter(primitive))] if position==0 else ['NavPathStack']): valid=False; break
                # Only keys of the exact import-bound target render are
                # identifiers in property position; nested bindings still fail.
                object_keys=set()
                for render in range(helper.body[0]+1,helper.body[1]-2):
                    if values[render:render+3]==[target.name,'(','{'] and self.definition(target.name,source) is target:
                        object_keys.update(begin for begin,finish in self._segments_object(source,render+2)
                            if values[begin+1:begin+2]==[':'])
                if self._shadowed_parameter(source,values[left],*helper.body,object_keys): valid=False; break
                mapping[values[left]]=expression
            if not valid: continue
            proof=self._navigation_render(root,helper,helper.body,target,route_parameter,primitive,stack,allowed,mapping)
            if proof:
                matches.append([{'role':'navigation-destination-helper','file':source.relative,
                    'line':source.tokens[index].line,'from':method.name,'to':helper.name},*proof])
        return _one(matches) or []

    def _navigation_handler_flow(self, caller, handler, target, member, allowed):
        if (not handler.body or handler.static or caller.source.relative not in allowed
                or not self._component_build_live(target,member)): return []
        source=caller.source; values=source.values; begin,end=handler.body; pushes=[]
        for index in range(begin+1,end-5):
            if values[index:index+2]!=['this','.'] or values[index+3:index+6]!=['.','pushPathByName','(']: continue
            field=_one(caller.members.get(values[index+2],[]))
            if not self._is_nav_stack(caller,field) or field.decorators!=('Param',): continue
            actual=self._segments(source,index+5)
            if len(actual)!=2 or actual[0][1]!=actual[0][0]+1 or actual[1][1]!=actual[1][0]+1: continue
            route=self._literal_string(source,actual[0][0]); argument=values[actual[1][0]]
            formal=[(left,right) for left,right in self._segments(source,handler.index+1)
                    if values[left]==argument and values[left+1:left+2]==[':']]
            if route is None or len(formal)!=1 or self._shadowed_parameter(source,argument,begin,end): continue
            left,right=formal[0]; primitive=self._flow_scalar(source.tokens[left+2:right])
            if primitive not in {frozenset({'string'}),frozenset({'number'})}: continue
            live=self._flow_callback_position_live(caller,handler,index,set(allowed))
            if live: pushes.append((field,route,primitive,index,live))
        if len(pushes)!=1: return []
        field,route,primitive,push,live=pushes[0]
        instances=[instance for owner in self.definitions if owner.kind=='struct' and owner.source.relative in allowed
                   for instance in self._flow_instances(owner,set(allowed)) if instance['child'] is caller]
        if len(instances)!=1: return []
        instance=instances[0]; root=instance['parent']; host=root.source; vals=host.values
        binding=instance['properties'].get(field.name)
        if binding is None: return []
        expression=vals[binding[0]:binding[1]]
        if len(expression)!=3 or expression[:2]!=['this','.']: return []
        stack=expression[2]; root_stack=_one(root.members.get(stack,[]))
        if not self._is_nav_stack(root,root_stack): return []
        build=_one(root.members.get('build',[]))
        if build is None or not build.body: return []
        matches=[]
        for index in range(build.body[0]+1,build.body[1]-1):
            if vals[index:index+2]!=['Navigation','('] or 'Navigation' in host.imports or 'Navigation' in host.bindings: continue
            arguments=self._segments(host,index+1)
            if len(arguments)!=1 or vals[arguments[0][0]:arguments[0][1]]!=['this','.',stack]: continue
            if not self._flow_callback_position_live(root,build,index,set(allowed)): continue
            body=host.pairs.get(index+1,build.body[1])+1
            if body not in host.pairs or vals[body]!='{': continue
            cursor=host.pairs[body]+1; destination=None
            while cursor+2<build.body[1] and vals[cursor]=='.' and vals[cursor+2]=='(':
                spans=self._segments(host,cursor+2)
                if vals[cursor+1]=='navDestination' and len(spans)==1:
                    value=vals[spans[0][0]:spans[0][1]]
                    if len(value)==3 and value[:2]==['this','.']: destination=value[2]
                cursor=host.pairs.get(cursor+2,build.body[1])+1
            renderer=_one(root.members.get(destination,[]))
            if renderer is None or renderer.decorators!=('Builder',) or not renderer.body: continue
            parameters=self._segments(host,renderer.index+1)
            if len(parameters)!=2: continue
            first,second=parameters
            if vals[first[0]+1:first[1]]!=[':','string'] or vals[second[0]+1:second[1]]!=[':','Object']: continue
            name=vals[first[0]]; parameter=vals[second[0]]
            for branch in range(renderer.body[0]+1,renderer.body[1]-2):
                if vals[branch:branch+2]!=['if','(']: continue
                close=host.pairs.get(branch+1)
                if close is None or vals[branch+2:close-1]!=[name,'=','=','='] or self._literal_string(host,close-1)!=route: continue
                opening=close+1
                if opening not in host.pairs or vals[opening]!='{': continue
                proof=self._navigation_render(root,renderer,(opening,host.pairs[opening]),target,parameter,primitive,stack,allowed)
                if proof:
                    matches.append([_event(caller,handler,'handler-definition'),*live,
                        {'role':'navigation-push','file':source.relative,'line':source.tokens[push].line,'route':route,'stack':field.name},
                        *instance['evidence'],_event(root,root_stack,'shared-navigation-stack'),
                        {'role':'navigation-route-binding','file':host.relative,'line':host.tokens[branch].line,'route':route,'builder':renderer.name},
                        *proof,_event(target,member,'definition')])
        return _one(matches) or []

    def _forwarded_field(self, caller, field, target, member):
        """One explicit field-to-method-argument hop, then a typed parameter call."""
        source=caller.source; values=source.values
        for i in range(caller.start+1,caller.end-5):
            if values[i:i+2]!=['this','.']: continue
            provider_field=_one(caller.members.get(values[i+2],[]))
            if provider_field is None: continue
            provider=self.member_type(caller,provider_field)
            if provider is None or values[i+3]!='.' or values[i+5]!='(': continue
            callee=_one(provider.members.get(values[i+4],[]))
            if callee is None: continue
            for position,(start,end) in enumerate(self._segments(source,i+5)):
                if values[start:end]!=['this','.',field.name]: continue
                proof=self._parameter_calls(provider,callee,target,member,position)
                if proof:
                    return [{'role':'caller','file':source.relative,'line':source.tokens[i].line},
                            _event(caller,field,'forwarded-field'),_event(caller,provider_field,'typed-provider'),*proof]
        return []

    @staticmethod
    def _flow_scalar(tokens):
        values=[token.value for token in tokens]
        atoms={'string','number','boolean','undefined','null'}
        if not values or any(value not in atoms|{'|'} for value in values): return None
        if any((index%2==0)!=(value in atoms) for index,value in enumerate(values)): return None
        return frozenset(values[::2]) if len(values)%2 else None

    def _flow_idle_local_contains(self, source, begin, end, position):
        if self._local_callable_contains(source,begin,end,position): return True
        # A callback stored in a local object/array is not a live UI binding.
        # Calls inside a declaration initializer are deliberately unsupported
        # here; direct inline callbacks passed to render/API calls remain live.
        values=source.values
        for index in range(begin+1,min(position,end)):
            if values[index] not in {'if','while'} or values[index+1]!='(': continue
            close=source.pairs.get(index+1)
            if close is None: continue
            body=close+1
            if values[index+2:close]==['false'] and body in source.pairs and body<position<source.pairs[body]: return True
            if values[index+2:close]==['true'] and body in source.pairs:
                otherwise=source.pairs[body]+1
                if values[otherwise:otherwise+2]==['else','{'] and otherwise+1 in source.pairs and otherwise+1<position<source.pairs[otherwise+1]: return True
        for index in range(begin+1,min(position,end)):
            if values[index] not in {'const','let','var'} or index+2>=end: continue
            cursor=index+2
            while cursor<end and values[cursor] not in {'=',';','{','}'}:
                cursor=source.pairs[cursor]+1 if cursor in source.pairs else cursor+1
            if cursor>=end or values[cursor]!='=': continue
            cursor+=1
            while cursor<position:
                if values[cursor]==';': break
                if cursor in source.pairs:
                    if cursor<position<source.pairs[cursor]: return True
                    cursor=source.pairs[cursor]+1
                else: cursor+=1
        return False

    def _flow_signature(self, source, start, finish):
        """Only explicit zero/one scalar-argument callbacks returning void."""
        values=source.values
        if start>=finish or values[start]!='(': return None
        close=source.pairs.get(start)
        if close is None or values[close+1:finish]!=['=>','void']: return None
        arguments=self._segments(source,start)
        if len(arguments)>1: return None
        result=[]
        for begin,end in arguments:
            if begin+2>=end or not IDENT.fullmatch(values[begin]) or values[begin+1]!=':': return None
            typed=self._flow_scalar(source.tokens[begin+2:end])
            if typed is None: return None
            result.append((values[begin],typed))
        return result

    def _flow_event(self, owner, member):
        if member.kind!='field' or member.static or member.decorators!=('Event',): return None
        source=owner.source
        # Member types retain the original token identity and position.
        if not member.type_tokens: return None
        begin=member.index+2
        return self._flow_signature(source,begin,begin+len(member.type_tokens))

    def _flow_arrow(self, source, start, finish):
        values=source.values
        if start>=finish or values[start]!='(': return None
        close=source.pairs.get(start)
        if close is None: return None
        cursor=close+1
        if values[cursor:cursor+2]==[':','void']: cursor+=2
        if cursor>=finish or values[cursor]!='=>': return None
        arguments=self._segments(source,start)
        if len(arguments)>1: return None
        parameters=[]
        for begin,end in arguments:
            if begin+2>=end or values[begin+1]!=':' or not IDENT.fullmatch(values[begin]): return None
            typed=self._flow_scalar(source.tokens[begin+2:end])
            if typed is None: return None
            parameters.append((values[begin],typed))
        begin=cursor+1; end=finish
        if values[begin]=='{':
            if source.pairs.get(begin)!=finish-1: return None
            begin+=1; end-=1
        while begin<end and values[end-1]==';': end-=1
        # An expression/body must contain exactly one effect, with no local
        # declarations, aliases, nested function, branch or parameter rebinding.
        body=values[begin:end]
        return (parameters,body,begin,end)

    def _flow_arrow_contexts(self, source, begin, end, position):
        """Every enclosing inline arrow, with its exact argument/assignment."""
        values=source.values; reverse={right:left for left,right in source.pairs.items()}; result=[]
        for index in range(begin+1,position):
            if values[index]!='=>': continue
            body=index+1
            if values[body]=='{':
                finish=source.pairs.get(body,body)+1
            else:
                finish=body
                while finish<end and values[finish] not in {';',',',')',']','}'}:
                    finish=source.pairs[finish]+1 if finish in source.pairs else finish+1
            if not body<=position<finish: continue
            previous=index-1
            if values[previous]=='void' and values[previous-1]==':': previous-=2
            start=reverse.get(previous) if values[previous]==')' else previous
            if start is None: return None
            if start>begin and values[start-1]=='async': start-=1
            calls=[]
            for opening,closing in source.pairs.items():
                if values[opening]!='(' or not begin<opening<start<closing<=end: continue
                for argument,span in enumerate(self._segments(source,opening)):
                    if span==(start,finish): calls.append((opening,argument))
            result.append({'arrow':index,'start':start,'finish':finish,'body':body,'call':_one(calls)})
        return result

    def _flow_intrinsic_handler(self, owner, method, opening):
        source=owner.source; values=source.values
        if opening<3 or values[opening-2]!='.': return False
        event=values[opening-1]; cursor=opening-3
        reverse={right:left for left,right in source.pairs.items()}
        while cursor>method.body[0]:
            if values[cursor]=='}' and cursor in reverse:
                cursor=reverse[cursor]-1; continue
            if values[cursor]!=')' or cursor not in reverse: return False
            arguments=reverse[cursor]; name=arguments-1
            if name<1 or not IDENT.fullmatch(values[name]): return False
            if values[name-1]=='.': cursor=name-2; continue
            intrinsic=values[name]
            allowed={'Button':{'onClick'},'XComponent':{'onLoad','onDestroy'}}
            return (event in allowed.get(intrinsic,set()) and intrinsic not in source.imports
                    and intrinsic not in source.bindings and not any(d.name==intrinsic for d in source.definitions)
                    and not self._shadowed_parameter(source,intrinsic,*method.body))
        return False

    def _flow_literal_dead(self, source, begin, end, position):
        values=source.values
        for index in range(begin+1,min(position,end)):
            if values[index] not in {'if','while'} or values[index+1]!='(': continue
            close=source.pairs.get(index+1)
            if close is None: continue
            body=close+1
            if values[index+2:close]==['false'] and body in source.pairs and body<position<source.pairs[body]: return True
            if values[index+2:close]==['true'] and body in source.pairs:
                otherwise=source.pairs[body]+1
                if values[otherwise:otherwise+2]==['else','{'] and otherwise+1 in source.pairs and otherwise+1<position<source.pairs[otherwise+1]: return True
        return False

    def _flow_service_carrier(self, owner, method, context, allowed, seen, depth):
        """Only typed Promise.then or an exactly registered member callback."""
        source=owner.source; values=source.values; call=context['call']
        if call:
            opening,argument=call
            if argument==0 and values[opening-5:opening]==['this','.',values[opening-3],'.','then']:
                field=_one(owner.members.get(values[opening-3],[]))
                types=[token.value for token in field.type_tokens] if field else []
                if field and types[:2]==['Promise','<'] and types[-1:]==['>']:
                    if self._flow_callback_position_live(owner,method,opening-5,allowed,seen,depth,True):
                        return [{'role':'promise-callback-carrier','file':source.relative,
                            'line':source.tokens[opening-5].line,'class':owner.name,'member':field.name}]
            return []
        start=context['start']
        if start<4 or values[start-1]!='=' or values[start-3]!='.' or not IDENT.fullmatch(values[start-4]) or not IDENT.fullmatch(values[start-2]): return []
        receiver,slot=values[start-4],values[start-2]
        # A declared local/parameter receiver is required; global identifiers
        # cannot supply a registration for an otherwise idle assignment.
        parameters=self._segments(source,method.index+1)
        if not any(values[left]==receiver and values[left+1:left+2]==[':'] for left,right in parameters): return []
        expected=[receiver,'.',slot]
        for index in range(context['finish'],method.body[1]-2):
            if values[index:index+4]==[*expected,'=']: return []
            if values[index:index+3]!=['.','on','(']: continue
            arguments=self._segments(source,index+2)
            if len(arguments)!=2: continue
            first,last=arguments
            if first[1]!=first[0]+1 or not source.tokens[first[0]].literal: continue
            if values[last[0]:last[1]]!=expected: continue
            # The registration and callback receiver must share the exact
            # typed parameter, e.g. lease.photo.on(..., lease.photoCallback).
            if index<3 or values[index-3:index-1]!=[receiver,'.'] or not IDENT.fullmatch(values[index-1]): continue
            if self._flow_callback_position_live(owner,method,index-3,allowed,seen,depth,True):
                return [{'role':'registered-member-callback','file':source.relative,
                    'line':source.tokens[index].line,'class':owner.name,'member':method.name,'binding':receiver+'.'+slot}]
        return []

    def _flow_callback_consumed(self, owner, method, parameter, allowed, seen=(), depth=0):
        if (depth>3 or owner.source.relative not in allowed or not method.body
                or method.kind!='method' or method.static): return []
        key=(owner.source.relative,method.name,parameter)
        if key in seen: return []
        seen=(*seen,key); source=owner.source; values=source.values
        formal=self._segments(source,method.index+1)
        if parameter>=len(formal): return []
        start,finish=formal[parameter]
        if values[start+1:start+2]!=[':']: return []
        signature=self._flow_signature(source,start+2,finish)
        name=values[start]; begin,end=method.body
        if signature is None or self._shadowed_parameter(source,name,begin,end): return []
        for index in range(begin+1,end-1):
            if values[index]!=name or values[index-1]=='.' or values[index+1]!='(': continue
            if len(self._segments(source,index+1))!=len(signature): continue
            carrier=self._flow_callback_position_live(owner,method,index,allowed,seen,depth,True)
            if carrier:
                return [_event(owner,method,'callback-formal-consumer'),{'role':'formal-callback-invocation',
                    'file':source.relative,'line':source.tokens[index].line,'class':owner.name,
                    'member':method.name,'parameter':name},*carrier]
        if depth==3: return []
        for index in range(begin+1,end-3):
            if values[index:index+2]!=['this','.'] or values[index+3]!='(': continue
            callee=_one(owner.members.get(values[index+2],[]))
            if callee is None or callee.kind!='method' or not callee.body or callee.static: continue
            actual=self._segments(source,index+3); destination=self._segments(source,callee.index+1)
            if len(actual)!=len(destination): continue
            carrier=self._flow_callback_position_live(owner,method,index,allowed,seen,depth,True)
            if not carrier: continue
            for position,(left,right) in enumerate(actual):
                if values[left:right]!=[name]: continue
                target_left,target_right=destination[position]
                if values[target_left+1:target_left+2]!=[':']: continue
                target_signature=self._flow_signature(source,target_left+2,target_right)
                if target_signature is None or [typed for _,typed in target_signature]!=[typed for _,typed in signature]: continue
                consumed=self._flow_callback_consumed(owner,callee,position,allowed,seen,depth+1)
                if consumed:
                    return [{'role':'callback-formal-forward','file':source.relative,'line':source.tokens[index].line,
                        'class':owner.name,'member':method.name,'parameter':name,'to':callee.name,'argument':position},*carrier,*consumed]
        return []

    def _flow_callback_position_live(self, owner, method, position, allowed, seen=(), depth=0, service=False):
        """Validate every enclosing arrow; one live outer arrow is insufficient.

        A truthy return contains the per-carrier source evidence. Unsupported
        callback storage or an unconsumed typed callback returns an empty list.
        """
        source=owner.source; begin,end=method.body
        if self._flow_literal_dead(source,begin,end,position): return []
        contexts=self._flow_arrow_contexts(source,begin,end,position)
        if contexts is None: return []
        if not contexts:
            return [] if self._flow_idle_local_contains(source,begin,end,position) else [
                {'role':'direct-handler-position','file':source.relative,'line':source.tokens[position].line,
                 'class':owner.name,'member':method.name}]
        evidence=[]; values=source.values
        for context in contexts:
            call=context['call']; consumed=[]
            if call:
                opening,argument=call
                if self._flow_intrinsic_handler(owner,method,opening):
                    consumed=[{'role':'intrinsic-ui-callback','file':source.relative,
                        'line':source.tokens[opening].line,'class':owner.name,'member':method.name,'event':values[opening-1]}]
                elif opening>=3 and values[opening-3:opening-1]==['this','.']:
                    callee=_one(owner.members.get(values[opening-1],[]))
                    if callee and callee.body and not callee.static:
                        formal=self._segments(source,callee.index+1)
                        arrow=self._flow_arrow(source,context['start'],context['finish'])
                        if arrow is not None and argument<len(formal):
                            left,right=formal[argument]
                            signature=self._flow_signature(source,left+2,right) if values[left+1:left+2]==[':'] else None
                            if signature is not None and [typed for _,typed in signature]==[typed for _,typed in arrow[0]]:
                                consumed=self._flow_callback_consumed(owner,callee,argument,allowed,seen,depth+1)
            if not consumed and service:
                consumed=self._flow_service_carrier(owner,method,context,allowed,seen,depth)
            if not consumed: return []
            evidence.extend(consumed)
        return evidence

    def _flow_roots(self, owner, allowed=None):
        build=_one(owner.members.get('build',[]))
        if build is None or build.kind!='method' or not build.body: return []
        roots=[(build,[])]
        # Only builders actually called from build enter the render set.
        # No arbitrary sibling method, lifecycle method or plan name is a root.
        source=owner.source; values=source.values
        for index in range(build.body[0]+1,build.body[1]-4):
            if values[index:index+2]!=['this','.'] or values[index+3:index+5]!=['(',')']: continue
            if self._flow_idle_local_contains(source,*build.body,index): continue
            if not self._flow_callback_position_live(owner,build,index,allowed or {source.relative}): continue
            builder=_one(owner.members.get(values[index+2],[]))
            if builder is None or not builder.body or builder.decorators!=('Builder',): continue
            if any(member is builder for member,_ in roots): continue
            roots.append((builder,[{'role':'reachable-builder','file':source.relative,
                'line':source.tokens[index].line,'class':owner.name,'member':builder.name}]))
        return roots

    def _flow_instances(self, parent, allowed):
        result=[]; source=parent.source; values=source.values
        if parent.source.relative not in allowed: return result
        for root,chain in self._flow_roots(parent,allowed):
            for index in range(root.body[0]+1,root.body[1]-3):
                if not IDENT.fullmatch(values[index]) or values[index+1:index+3]!=['(','{']: continue
                if index>0 and values[index-1] in {'.','new','function'}: continue
                if self._flow_idle_local_contains(source,*root.body,index): continue
                if not self._flow_callback_position_live(parent,root,index,allowed): continue
                if self._shadowed_parameter(source,values[index],*root.body): continue
                child=self.definition(values[index],source)
                if child is None or child.kind!='struct' or child.source.relative not in allowed: continue
                close=source.pairs.get(index+1); object_end=source.pairs.get(index+2)
                if close is None or object_end!=close-1: continue
                properties={}; malformed=False
                for begin,end in self._segments_object(source,index+2):
                    if begin+2>=end or not IDENT.fullmatch(values[begin]) or values[begin+1]!=':' or values[begin] in properties:
                        malformed=True; break
                    properties[values[begin]]=(begin+2,end)
                if malformed: continue
                result.append({'parent':parent,'child':child,'root':root,'index':index,'properties':properties,
                    'evidence':[*chain,{'role':'render-instance','file':source.relative,
                    'line':source.tokens[index].line,'class':parent.name,'member':root.name,'child':child.name}]})
        return result

    def _flow_callback(self, instance, event):
        signature=self._flow_event(instance['child'],event)
        actual=instance['properties'].get(event.name)
        if signature is None or actual is None: return None
        arrow=self._flow_arrow(instance['parent'].source,*actual)
        if arrow is None or [typed for _,typed in arrow[0]]!=[typed for _,typed in signature]: return None
        parameters,body,begin,end=arrow; parent=instance['parent']
        source=parent.source
        if any(self._shadowed_parameter(source,name,begin-1,end) for name,_ in parameters): return None
        detail={'role':'event-binding','file':source.relative,'line':source.tokens[actual[0]].line,
                'class':parent.name,'event':event.name,'child':instance['child'].name}
        if len(parameters)==1:
            name,typed=parameters[0]
            if len(body)==5 and body[:2]==['this','.'] and body[3:]==['=',name]:
                field=_one(parent.members.get(body[2],[]))
                destination=self._flow_scalar(field.type_tokens) if field else None
                if (field and field.kind=='field' and not field.static and field.decorators==('Local',)
                        and destination is not None and typed<=destination):
                    return ('write',field,[*instance['evidence'],detail,_event(parent,field,'callback-state-write')])
            if len(body)==6 and body[:2]==['this','.'] and body[3:]==['(',name,')']:
                forwarded=_one(parent.members.get(body[2],[]))
                expected=self._flow_event(parent,forwarded) if forwarded else None
                if expected is not None and len(expected)==1 and typed<=expected[0][1]:
                    return ('forward',forwarded,[*instance['evidence'],detail,_event(parent,forwarded,'forwarded-event')])
        elif not parameters:
            if len(body)==5 and body[:2]==['this','.'] and body[3]=='=':
                field=_one(parent.members.get(body[2],[]))
                typed=self._flow_scalar(field.type_tokens) if field else None
                literal=body[4]
                expected=frozenset({'boolean'}) if literal in {'true','false'} else (
                    frozenset({'number'}) if re.fullmatch(r'\d+',literal) else None)
                if (field and field.kind=='field' and field.decorators==('Local',) and expected is not None
                        and typed is not None and expected<=typed):
                    return ('write',field,[*instance['evidence'],detail,_event(parent,field,'callback-state-write')])
        return None

    def _flow_reached_methods(self, owner, allowed):
        roots=self._flow_roots(owner,allowed); result=list(roots)
        source=owner.source; values=source.values
        for root,chain in roots:
            for index in range(root.body[0]+1,root.body[1]-3):
                if values[index:index+2]!=['this','.'] or values[index+3]!='(': continue
                if self._flow_idle_local_contains(source,*root.body,index): continue
                live=self._flow_callback_position_live(owner,root,index,allowed)
                if not live: continue
                method=_one(owner.members.get(values[index+2],[]))
                if method is None or method.kind!='method' or not method.body or method.static: continue
                if any(candidate is method for candidate,_ in result): continue
                result.append((method,[*chain,*live,{'role':'build-handler-call','file':source.relative,
                    'line':source.tokens[index].line,'class':owner.name,'member':method.name}]))
        return result

    @staticmethod
    def _flow_arrow_contains(source, begin, end, position):
        # Conservative exclusion for direct emits; typed service arguments are
        # separately proven below. An anonymous callback is never a free root.
        values=source.values
        for index in range(begin+1,position):
            if values[index]!='=>': continue
            body=index+1
            if body in source.pairs and values[body]=='{':
                if body<position<source.pairs[body]: return True
            elif not any(values[cursor] in {';',','} for cursor in range(body,position)):
                return True
        return False

    def _flow_emit(self, owner, event, allowed, seen=(), depth=0):
        signature=self._flow_event(owner,event)
        if signature is None or depth>2 or (owner.source.relative,event.name) in seen: return []
        seen=(*seen,(owner.source.relative,event.name)); source=owner.source; values=source.values
        for method,chain in self._flow_reached_methods(owner,allowed):
            begin,end=method.body
            for index in range(begin+1,end-3):
                if self._flow_idle_local_contains(source,begin,end,index): continue
                if values[index:index+4]==['this','.',event.name,'(']:
                    close=source.pairs.get(index+3)
                    if close is None or self._flow_arrow_contains(source,begin,end,index): continue
                    actual=self._segments(source,index+3)
                    # Empty events emitted by a real build handler are valid;
                    # scalar events require an exactly typed handler parameter.
                    if not signature and not actual:
                        return [*chain,_event(owner,method,'event-emitter'),_event(owner,event,'event-definition'),
                            {'role':'event-emit','file':source.relative,'line':source.tokens[index].line}]
                    if len(signature)==len(actual)==1:
                        parameters=self._segments(source,method.index+1)
                        for start,finish in parameters:
                            if (values[start+1:start+2]==[':'] and values[actual[0][0]:actual[0][1]]==[values[start]]
                                    and self._flow_scalar(source.tokens[start+2:finish])==signature[0][1]
                                    and not self._shadowed_parameter(source,values[start],begin,end)):
                                return [*chain,_event(owner,method,'event-emitter'),_event(owner,event,'event-definition'),
                                    {'role':'event-emit','file':source.relative,'line':source.tokens[index].line}]
                # Exact, typed inline callback supplied to a real imported
                # instance method from an already build-reached handler.
                if values[index:index+2]!=['this','.'] or values[index+3:index+4]!=['.'] or values[index+5:index+6]!=['(']: continue
                receiver=_one(owner.members.get(values[index+2],[]))
                provider=self.member_type(owner,receiver) if receiver else None
                if provider is None or provider.source.relative not in allowed: continue
                called=_one(provider.members.get(values[index+4],[])) if provider else None
                if called is None or called.kind!='method' or not called.body or called.static: continue
                actual=self._segments(source,index+5); formal=self._segments(provider.source,called.index+1)
                if len(actual)!=len(formal): continue
                for position,span in enumerate(actual):
                    arrow=self._flow_arrow(source,*span)
                    if arrow is None or len(arrow[0])!=1 or len(signature)!=1: continue
                    start,finish=formal[position]; pv=provider.source.values
                    if pv[start+1:start+2]!=[':']: continue
                    typed=self._flow_signature(provider.source,start+2,finish)
                    if typed is None or [t for _,t in typed]!=[t for _,t in arrow[0]]: continue
                    name,scalar=arrow[0][0]
                    if (arrow[1]!=['this','.',event.name,'(',name,')'] or not scalar<=signature[0][1]
                            or self._shadowed_parameter(source,name,arrow[2]-1,arrow[3])): continue
                    consumed=self._flow_callback_consumed(provider,called,position,allowed)
                    if not consumed or not self._flow_callback_position_live(owner,method,index,allowed): continue
                    return [*chain,_event(owner,method,'event-emitter'),_event(owner,receiver,'typed-callback-receiver'),
                        _event(provider,called,'typed-callback-consumer'),*consumed,_event(owner,event,'event-definition'),
                        {'role':'live-typed-callback-emit','file':source.relative,'line':source.tokens[span[0]].line,
                         'argument':position}]
        # Parent events with empty default initializers need an actual child
        # render forwarding and a recursively proven child emitter.
        for instance in self._flow_instances(owner,allowed):
            child=instance['child']
            for candidates in child.members.values():
                child_event=_one(candidates)
                if child_event is None: continue
                callback=self._flow_callback(instance,child_event)
                if callback is None or callback[0]!='forward' or callback[1] is not event: continue
                emitted=self._flow_emit(child,child_event,allowed,seen,depth+1)
                if emitted: return [*emitted,*callback[2]]
        return []

    def _flow_paths(self, owner, event, allowed, seen=(), depth=0):
        if depth>2 or (owner.source.relative,event.name) in seen: return []
        seen=(*seen,(owner.source.relative,event.name)); paths=[]
        for parent in self.definitions:
            if parent.kind!='struct' or parent.source.relative not in allowed: continue
            for instance in self._flow_instances(parent,allowed):
                if instance['child'] is not owner: continue
                callback=self._flow_callback(instance,event)
                if callback is None: continue
                if callback[0]=='write': paths.append((parent,callback[1],[instance],callback[2]))
                else:
                    for destination,state,instances,evidence in self._flow_paths(parent,callback[1],allowed,seen,depth+1):
                        paths.append((destination,state,[instance,*instances],[*callback[2],*evidence]))
        return paths

    def _flow_param(self, instance, param, destination, state):
        if (instance['parent'] is not destination or param.kind!='field' or param.static
                or param.decorators!=('Param',)): return []
        expression=instance['properties'].get(param.name)
        if expression is None: return []
        source=destination.source
        if source.values[expression[0]:expression[1]]!=['this','.',state.name]: return []
        incoming=self._flow_scalar(state.type_tokens); accepted=self._flow_scalar(param.type_tokens)
        if incoming is None or accepted is None or not incoming<=accepted: return []
        return [*instance['evidence'],_event(instance['child'],param,'param-definition'),
            _event(destination,state,'param-source-state'),{'role':'same-instance-param-binding',
            'file':source.relative,'line':source.tokens[expression[0]].line,'param':param.name}]

    def _flow_continuation(self, caller, builder, child, event, state, emitted, contracts):
        """One declared bindSheet disappearance guard consumes this callback's
        exact boolean effect. No navigation/IPC semantics are inferred.
        """
        if self._flow_scalar(state.type_tokens)!=frozenset({'boolean'}): return []
        declarations=[item for item in contracts if item['kind']=='event_callback'
            and item['event']==child.name+'.'+event.name and item['binding']==caller.name+'.'+builder.name
            and item['consumer']==caller.name+'.'+state.name]
        declaration=_one(declarations)
        if declaration is None: return []
        producer=re.fullmatch(re.escape(child.name)+r'\.([\w$]+)',declaration['producer'])
        continuation=re.fullmatch(r'bindSheet onDisappear callback declared in '+re.escape(caller.name)
            +r'\.build -> '+re.escape(caller.name)+r'\.([\w$]+)',declaration.get('continuation',''))
        if producer is None or continuation is None: return []
        if not any(item.get('role')=='event-emitter' and item.get('class')==child.name
                   and item.get('member')==producer[1] and item.get('file')==child.source.relative for item in emitted): return []
        method=_one(caller.members.get(continuation[1],[])); build=_one(caller.members.get('build',[]))
        if method is None or method.kind!='method' or method.static or not method.body or build is None or not build.body: return []
        source=caller.source; values=source.values; begin,end=build.body
        matches=[]
        for index in range(begin+1,end-2):
            if values[index:index+3]!=['.','bindSheet','(']: continue
            if self._flow_idle_local_contains(source,begin,end,index): continue
            arguments=self._segments(source,index+2)
            if len(arguments)!=3: continue
            start,finish=arguments[1]
            if values[start:finish]!=['this','.',builder.name,'(',')']: continue
            start,finish=arguments[2]
            if values[start]!='{' or source.pairs.get(start)!=finish-1: continue
            disappear=[]
            for left,right in self._segments_object(source,start):
                if values[left:left+2]==['onDisappear',':']: disappear.append((left+2,right))
            callback=_one(disappear)
            if callback is None: continue
            arrow=self._flow_arrow(source,*callback)
            expected=['if','(','this','.',state.name,')','{','this','.',method.name,'(',')',';','}']
            if arrow is None or arrow[0] or arrow[1]!=expected: continue
            matches.append({'role':'declared-callback-continuation','file':source.relative,
                'line':source.tokens[callback[0]].line,'builder':builder.name,'guard':state.name,
                'continuation':method.name,'contract':declaration})
        return matches if len(matches)==1 else []

    def _dto_initialization_flow(self, caller, left, target, right, allowed):
        """One optional DTO -> intrinsic ForEach -> child Param -> snapshot
        Local initialization. This does not grant navigation or aliases.
        """
        allowed=set(allowed)
        if (caller.kind!='struct' or target.kind!='class' or left.kind!='field'
                or left.decorators!=('Local',) or right.kind!='field' or left.static or right.static
                or caller.source.relative not in allowed or target.source.relative not in allowed): return []
        expected=self._member_value_type(caller,left); source_type=self._member_value_type(target,right)
        if (expected is None or expected[0]!='class' or expected[2]
                or source_type is None or source_type[0]!='class' or source_type[1] is not expected[1]): return []
        value_class=expected[1]
        if value_class.source.relative not in allowed or self.definition(value_class.name,caller.source) is not value_class: return []
        ts=target.source; tv=ts.values
        if tv[right.index+1:right.index+2]!=['?']: return []

        def stripped(source, begin, end):
            return [value for value in source.values[begin:end] if value!=';']

        def parameter_type(owner, begin, end):
            source=owner.source; values=source.values; cursor=begin+1
            optional=values[cursor:cursor+1]==['?']
            if optional: cursor+=1
            if values[cursor:cursor+1]!=[':']: return None
            finish=next((index for index in range(cursor+1,end) if values[index]=='='),end)
            typed=self._member_value_type(owner,Member(values[begin],begin,'parameter',False,source.tokens[cursor+1:finish]))
            if optional and typed is not None:
                typed=(typed[0],typed[1],typed[2]|{'undefined'}) if typed[0]=='class' else ('scalar',typed[1]|{'undefined'})
            return typed

        # clone must preserve the actual constructor's scalar fields in order;
        # a typed empty/default/wrong-field clone is not a snapshot proof.
        clone=_one(value_class.members.get('clone',[])); constructor=_one(value_class.members.get('constructor',[]))
        if (clone is None or constructor is None or not clone.body or not constructor.body
                or clone.static or constructor.static or self._segments(value_class.source,clone.index+1)
                or self.member_type(value_class,clone) is not value_class): return []
        vs=value_class.source; vv=vs.values; clone_body=stripped(vs,clone.body[0]+1,clone.body[1])
        parameters=self._segments(vs,constructor.index+1)
        if not parameters or clone_body[:3]!=['return','new',value_class.name] or self.definition(value_class.name,vs) is not value_class: return []
        required=['return','new',value_class.name,'(']; assignments=[]; clone_fields=[]
        for position,(begin,end) in enumerate(parameters):
            name=vv[begin]; field=_one(value_class.members.get(name,[])); typed=parameter_type(value_class,begin,end)
            if field is None or field.kind!='field' or typed is None or typed[0]!='scalar': return []
            if not self._value_assignable(self._member_value_type(value_class,field),typed): return []
            if position: required.append(',')
            required.extend(['this','.',name]); assignments.extend(['this','.',name,'=',name]); clone_fields.append(name)
        required.append(')')
        if clone_body!=required or stripped(vs,constructor.body[0]+1,constructor.body[1])!=assignments: return []
        clone_proof=[_event(value_class,clone,'dto-value-clone'),_event(value_class,constructor,'dto-value-constructor'),
            {'role':'snapshot-fields','file':vs.relative,'line':vs.tokens[clone.index].line,'fields':clone_fields}]

        # The DTO member must snapshot its actual optional typed constructor
        # argument, not merely declare the same property name/type.
        dto_constructor=_one(target.members.get('constructor',[]))
        if dto_constructor is None or not dto_constructor.body or dto_constructor.static: return []
        dto_arguments=self._segments(ts,dto_constructor.index+1); dto_input=None; dto_position=None; dto_assignment=None
        for position,(begin,end) in enumerate(dto_arguments):
            typed=parameter_type(target,begin,end)
            if typed is None or typed[0]!='class' or typed[1] is not value_class or typed[2]!=frozenset({'undefined'}): continue
            name=tv[begin]
            needle=['this','.',right.name,'=',name,'?','.','clone','(',')']
            writes=[index for index in range(dto_constructor.body[0]+1,dto_constructor.body[1]-3)
                    if tv[index:index+4]==['this','.',right.name,'=']]
            if len(writes)!=1: continue
            index=writes[0]
            if tv[index:index+len(needle)]!=needle: continue
            if stripped(ts,index+len(needle),dto_constructor.body[1]): continue
            if self._flow_idle_local_contains(ts,*dto_constructor.body,index) or self._flow_arrow_contains(ts,*dto_constructor.body,index): continue
            if self._shadowed_parameter(ts,name,*dto_constructor.body): continue
            dto_input=name; dto_position=position; dto_assignment=index
        if dto_input is None: return []
        dto_proof=[_event(target,dto_constructor,'dto-snapshot-constructor'),_event(target,right,'dto-snapshot-member'),
            {'role':'dto-constructor-value-copy','file':ts.relative,'line':ts.tokens[dto_assignment].line,'parameter':dto_input}]

        # The supplied Param must be the FIRST branch. This exact single
        # lifecycle assignment excludes hidden later overwrites and defaults
        # which take priority over the constructor data.
        lifecycle=_one(caller.members.get('aboutToAppear',[])); child_build=_one(caller.members.get('build',[]))
        if (lifecycle is None or not lifecycle.body or lifecycle.static or self._segments(caller.source,lifecycle.index+1)
                or child_build is None or not self._component_build_live(caller,child_build)): return []
        cs=caller.source; cv=cs.values; lifecycle_body=stripped(cs,lifecycle.body[0]+1,lifecycle.body[1]); initializers=[]
        for candidates in caller.members.values():
            initial=_one(candidates)
            if initial is None or initial.decorators!=('Param',): continue
            typed=self._member_value_type(caller,initial)
            if typed is None or typed[0]!='class' or typed[1] is not value_class or typed[2]!=frozenset({'undefined'}): continue
            for other_candidates in caller.members.values():
                fallback=_one(other_candidates)
                if fallback is None or fallback.decorators!=('Param',): continue
                record=self.member_type(caller,fallback)
                if record is None or record.source.relative not in allowed: continue
                for field_candidates in record.members.values():
                    field=_one(field_candidates)
                    if field is None or not self._value_assignable(self._member_value_type(record,field),expected): continue
                    wanted=['this','.',left.name,'=','(','this','.',initial.name,'?','?',
                        'this','.',fallback.name,'?','.',field.name,'?','?','new',value_class.name,'(',')',')','.','clone','(',')']
                    if lifecycle_body==wanted:
                        initializers.append((initial,[*clone_proof,*dto_proof,_event(caller,initial,'dto-initial-param'),
                            _event(caller,lifecycle,'dto-lifecycle-initializer'),_event(caller,left,'dto-local-value'),
                            _event(record,field,'dto-fallback-value'),{'role':'dto-priority','file':cs.relative,
                                'line':cs.tokens[lifecycle.index].line,'branches':[initial.name,fallback.name+'.'+field.name,'new '+value_class.name]}]))
        selected=_one(initializers)
        if selected is None: return []
        initial,initial_proof=selected
        if not any(cv[index:index+3]==['this','.',left.name]
                   and not self._flow_idle_local_contains(cs,*child_build.body,index)
                   and not self._flow_arrow_contains(cs,*child_build.body,index)
                   for index in range(child_build.body[0]+1,child_build.body[1]-2)): return []

        # The constructor's optional argument must originate in a real typed
        # writer to the very router field used as the ForEach singleton.
        def origin_writer(parent, path):
            if len(path)!=5 or path[:2]!=['this','.'] or path[3]!='.': return []
            router_field=_one(parent.members.get(path[2],[])); router=self.member_type(parent,router_field) if router_field else None
            destination=_one(router.members.get(path[4],[])) if router else None
            if router is None or router.source.relative not in allowed or destination is None: return []
            rs=router.source; rv=rs.values
            for methods in router.members.values():
                method=_one(methods)
                if method is None or not method.body or method.static or method.kind!='method': continue
                formal=self._segments(rs,method.index+1)
                for index in range(method.body[0]+1,method.body[1]-6):
                    if rv[index:index+6]!=['this','.',destination.name,'=','new',target.name] or rv[index+6]!='(': continue
                    if self.definition(target.name,rs) is not target: continue
                    if self._flow_idle_local_contains(rs,*method.body,index) or self._flow_arrow_contains(rs,*method.body,index): continue
                    actual=self._segments(rs,index+6)
                    if len(actual)!=len(dto_arguments) or dto_position>=len(actual): continue
                    left_arg,right_arg=actual[dto_position]
                    if right_arg-left_arg!=1: continue
                    name=rv[left_arg]
                    for begin,end in formal:
                        typed=parameter_type(router,begin,end)
                        if rv[begin]!=name or typed is None or typed[0]!='class' or typed[1] is not value_class or typed[2]!=frozenset({'undefined'}): continue
                        if self._shadowed_parameter(rs,name,*method.body): continue
                        return [_event(parent,router_field,'dto-router-receiver'),_event(router,destination,'dto-router-destination'),
                            _event(router,method,'dto-origin-constructor-writer'),{'role':'dto-origin-argument','file':rs.relative,
                                'line':rs.tokens[index].line,'parameter':name,'position':dto_position}]
            return []

        matches=[]
        for parent in self.definitions:
            if parent.kind!='struct' or parent.source.relative not in allowed: continue
            parent_build=_one(parent.members.get('build',[]))
            if parent_build is None or not self._component_build_live(parent,parent_build): continue
            ps=parent.source; pv=ps.values
            for root,root_proof in self._flow_roots(parent,allowed):
                if root.decorators!=('Builder',): continue
                attachments=[]
                for index in range(parent_build.body[0]+1,parent_build.body[1]-2):
                    if pv[index:index+3]!=['.','bindSheet','(']: continue
                    arguments=self._segments(ps,index+2)
                    if len(arguments)<2 or pv[arguments[1][0]:arguments[1][1]]!=['this','.',root.name,'(',')']: continue
                    if self._flow_idle_local_contains(ps,*parent_build.body,index) or self._flow_arrow_contains(ps,*parent_build.body,index): continue
                    attachments.append({'role':'dto-live-builder-attachment','file':ps.relative,'line':ps.tokens[index].line,'builder':root.name})
                if len(attachments)!=1: continue
                for index in range(root.body[0]+1,root.body[1]-1):
                    if pv[index:index+2]!=['ForEach','('] or pv[index-1] in {'.','new','function'}: continue
                    if ('ForEach' in ps.imports or 'ForEach' in ps.bindings or any(d.name=='ForEach' for d in ps.definitions)
                            or self._shadowed_parameter(ps,'ForEach',*root.body)
                            or self._flow_idle_local_contains(ps,*root.body,index) or self._flow_arrow_contains(ps,*root.body,index)): continue
                    arguments=self._segments(ps,index+1)
                    if len(arguments)!=3: continue
                    begin,end=arguments[0]; iterable=pv[begin:end]
                    # One exact optional this.router.destination singleton.
                    if len(iterable)!=20: continue
                    path=iterable[:5]
                    if iterable!=[*path,'=','=','=', 'undefined','?','[',']',':','[',*path,']']: continue
                    typed=self._typed_this_path(parent,path,allowed)
                    if typed is None or typed[0]!=('class',target,frozenset({'undefined'})): continue
                    origin=origin_writer(parent,path)
                    if not origin: continue
                    begin,end=arguments[1]
                    if pv[begin]!='(' or begin not in ps.pairs: continue
                    close=ps.pairs[begin]; parameters=self._segments(ps,begin)
                    if len(parameters)!=1 or pv[close+1:close+3]!=['=>','{'] or ps.pairs.get(close+2)!=end-1: continue
                    first,last=parameters[0]; item=pv[first]
                    if pv[first+1:first+2]!=[':'] or self.definition(pv[first+2],ps) is not target or last-first!=3: continue
                    item_begin,item_end=close+2,end-1
                    if self._shadowed_parameter(ps,item,item_begin,item_end): continue
                    # Stable key must refer to a real scalar DTO id on this item.
                    key_begin,key_end=arguments[2]
                    if pv[key_begin]!='(' or key_begin not in ps.pairs: continue
                    key_close=ps.pairs[key_begin]; key_parameters=self._segments(ps,key_begin)
                    if len(key_parameters)!=1: continue
                    first,last=key_parameters[0]; key_name=pv[first]
                    if last-first!=3 or pv[first+1]!=':' or self.definition(pv[first+2],ps) is not target: continue
                    if pv[key_close+1:key_end]!=[':','string','=>',key_name,'.','id']: continue
                    identity=_one(target.members.get('id',[]))
                    if identity is None or self._member_value_type(target,identity)!=('scalar',frozenset({'string'})): continue
                    renders=[]
                    for render in range(item_begin+1,item_end-2):
                        if pv[render:render+3]!=[caller.name,'(','{'] or self.definition(caller.name,ps) is not caller: continue
                        if self._flow_idle_local_contains(ps,item_begin,item_end,render) or self._flow_arrow_contains(ps,item_begin,item_end,render): continue
                        if self._shadowed_parameter(ps,caller.name,item_begin,item_end): continue
                        call_end=ps.pairs.get(render+1); object_end=ps.pairs.get(render+2)
                        if call_end is None or object_end!=call_end-1: continue
                        properties={}; malformed=False
                        for first,last in self._segments_object(ps,render+2):
                            if first+2>=last or pv[first+1]!=':' or pv[first] in properties:
                                malformed=True; break
                            properties[pv[first]]=(first+2,last)
                        if malformed: continue
                        binding=properties.get(initial.name)
                        if binding is None or pv[binding[0]:binding[1]]!=[item,'.',right.name]: continue
                        if not self._value_assignable(('class',value_class,frozenset({'undefined'})),self._member_value_type(caller,initial)): continue
                        renders.append({'role':'dto-same-instance-param','file':ps.relative,'line':ps.tokens[render].line,
                            'class':parent.name,'builder':root.name,'child':caller.name,'param':initial.name,'source':item+'.'+right.name})
                    if len(renders)!=1: continue
                    matches.append([*initial_proof,*root_proof,*attachments,*typed[1],*origin,*renders,
                        {'role':'dto-intrinsic-singleton-foreach','file':ps.relative,'line':ps.tokens[index].line,'item':item,'key':key_name+'.id'},
                        _event(target,right,'definition')])
        return matches[0] if len(matches)==1 else []

    def _method_event_effect(self, caller, handler, target, field, allowed):
        """Planned child method -> exact Event -> same parent callback effect.

        Only a direct typed callback or one typed parent method is accepted.
        Literal nullable/boolean effects need not equal the event payload.
        """
        if (handler.kind!='method' or handler.static or not handler.body or field.kind!='field'
                or field.static or field.decorators!=('Local',) or caller.source.relative not in allowed
                or target.source.relative not in allowed): return []
        source=caller.source; values=source.values; results=[]
        for index in range(handler.body[0]+1,handler.body[1]-3):
            if values[index:index+2]!=['this','.'] or values[index+3]!='(': continue
            event=_one(caller.members.get(values[index+2],[])); signature=self._flow_event(caller,event) if event else None
            if signature is None or len(signature)>1: continue
            live=self._flow_callback_position_live(caller,handler,index,allowed)
            if not live: continue
            actual=self._segments(source,index+3)
            if len(actual)!=len(signature): continue
            payload=[]
            if signature:
                left,right=actual[0]; argument=values[left:right]; typed=None
                bound=self._typed_this_path(caller,argument,allowed)
                if bound and bound[0][0]=='scalar': typed=bound[0][1]; payload=bound[1]
                elif len(argument)==1:
                    for begin,end in self._segments(source,handler.index+1):
                        if values[begin]==argument[0] and values[begin+1:begin+2]==[':']:
                            typed=self._flow_scalar(source.tokens[begin+2:end])
                            if self._shadowed_parameter(source,argument[0],*handler.body): typed=None
                if typed is None or not typed<=signature[0][1]: continue
            for instance in self._flow_instances(target,allowed):
                if instance['child'] is not caller: continue
                binding=instance['properties'].get(event.name)
                arrow=self._flow_arrow(target.source,*binding) if binding else None
                if arrow is None or [t for _,t in arrow[0]]!=[t for _,t in signature]: continue
                parameters,body,begin,end=arrow; ps=target.source; pv=ps.values
                if any(self._shadowed_parameter(ps,name,begin-1,end) for name,_ in parameters): continue
                direct=self._flow_callback(instance,event)
                if direct and direct[0]=='write' and direct[1] is field:
                    results.append([*live,*payload,_event(caller,handler,'planned-event-emitter'),_event(caller,event,'event-definition'),*direct[2]])
                    continue
                # Exactly one parent method, same arguments and signatures.
                expected=['this','.',body[2] if len(body)>2 else '', '(']
                for position,(name,_) in enumerate(parameters):
                    if position: expected.append(',')
                    expected.append(name)
                expected.append(')')
                if body!=expected: continue
                method=_one(target.members.get(body[2],[]))
                if method is None or method.kind!='method' or method.static or not method.body: continue
                formal=self._segments(ps,method.index+1)
                if len(formal)!=len(parameters): continue
                typed_parameters={}; valid=True
                for (first,last),(_,typed) in zip(formal,parameters):
                    actual_type=self._flow_scalar(ps.tokens[first+2:last]) if pv[first+1:first+2]==[':'] else None
                    name=pv[first]
                    if actual_type!=typed or self._shadowed_parameter(ps,name,*method.body): valid=False; break
                    typed_parameters[name]=typed
                if not valid: continue
                writes=[cursor for cursor in range(method.body[0]+1,method.body[1]-4)
                    if pv[cursor:cursor+4]==['this','.',field.name,'='] and pv[cursor+4:cursor+5]!=['=']]
                if len(writes)!=1: continue
                cursor=writes[0]; rhs=pv[cursor+4]
                if pv[cursor+5] not in {';','}'} and ps.tokens[cursor+5].line==ps.tokens[cursor+4].line: continue
                carrier=self._flow_callback_position_live(target,method,cursor,allowed)
                if not carrier: continue
                destination=self._member_value_type(target,field)
                scalar=typed_parameters.get(rhs)
                if rhs in {'true','false'}: scalar=frozenset({'boolean'})
                elif rhs in {'undefined','null'}: scalar=frozenset({rhs})
                elif re.fullmatch(r'[0-9]+',rhs): scalar=frozenset({'number'})
                good=(destination and scalar and (destination[0]=='scalar' and scalar<=destination[1]
                    or destination[0]=='class' and scalar<=destination[2] and destination[1].source.relative in allowed))
                if not good: continue
                results.append([*live,*payload,_event(caller,handler,'planned-event-emitter'),_event(caller,event,'event-definition'),
                    *instance['evidence'],{'role':'typed-parent-event-method','file':ps.relative,'line':ps.tokens[binding[0]].line,'event':event.name,'method':method.name},
                    _event(target,method,'callback-effect-method'),*carrier,_event(target,field,'callback-state-write')])
        return results[0] if len(results)==1 else []

    @staticmethod
    def _official_import(source, name, package):
        active={token.line for token in source.tokens if token.value=='import' and not token.literal}
        matches=[]
        for match in re.finditer(r"(?m)^import[ \t]+\{([^}]+)\}\s+from\s+['\"]([^'\"]+)['\"]",source.text):
            if source.text[:match.start()].count('\n')+1 not in active: continue
            if match[2]==package and name in [part.strip() for part in match[1].split(',')]: matches.append(match)
        return len(matches)==1 and name not in source.bindings and not any(d.name==name for d in source.definitions)

    @staticmethod
    def _template_literal(source, index):
        if index>=len(source.tokens) or not source.tokens[index].literal: return None
        for match in re.finditer(r'`[^`\\]*`',source.text):
            if source.text[:match.start()].count('\n')+1!=source.tokens[index].line: continue
            before=_target_tokens(source.text[:match.start()]); after=_target_tokens(source.text[:match.end()])
            if len(before)==index and len(after)==index+1 and after[-1].literal: return match[0][1:-1]
        return None

    def _extends_official(self, definition, base, package):
        source=definition.source; values=source.values
        return (values[definition.start-3:definition.start]==[definition.name,'extends',base]
            and self._official_import(source,base,package))

    def _form_uri_producer(self, form, key, fallback, allowed):
        """Form's actual binding return -> typed service result -> exact URI key."""
        source=form.source; values=source.values; method=_one(form.members.get('onAddForm',[]))
        if (method is None or not method.body or not self._extends_official(form,'FormExtensionAbility','@kit.FormKit')
                or not self._official_import(source,'formBindingData','@kit.FormKit')): return []
        for index in range(method.body[0]+1,method.body[1]-9):
            if values[index:index+4]!=['return','formBindingData','.','createFormBindingData'] or values[index+4]!='(': continue
            if not self._flow_callback_position_live(form,method,index,allowed): continue
            arguments=self._segments(source,index+4)
            if len(arguments)!=1: continue
            begin,end=arguments[0]
            if end-begin<5 or values[begin+1]!='.' or values[begin+3]!='(' or source.pairs.get(begin+3)!=end-1: continue
            alias=values[begin]; receiver=None; provider_proof=[]
            for cursor in range(method.body[0]+1,index-7):
                if values[cursor:cursor+6]!=['const',alias,'=','this','.',values[cursor+5]] or values[cursor+6:cursor+8]!=['(',')']: continue
                provider=_one(form.members.get(values[cursor+5],[]))
                service=self.member_type(form,provider) if provider else None
                if service is None or service.source.relative not in allowed: continue
                proof=self._self_provider(form,provider,service)
                initializer=[entry for entry in proof if entry['role']=='provider-field']
                field_name=initializer[0]['member'] if len(initializer)==1 else None
                live_initializers=[pos for pos in range(provider.body[0]+1,provider.body[1]-6)
                    if values[pos:pos+5]==['this','.',field_name,'=','new']
                    and self._flow_callback_position_live(form,provider,pos,allowed)] if proof else []
                if (proof and len(live_initializers)==1 and not self._shadowed_parameter(source,alias,cursor+7,method.body[1])
                        and self._flow_callback_position_live(form,method,cursor,allowed)):
                    receiver=service;provider_proof=proof
            if receiver is None: continue
            binding=_one(receiver.members.get(values[begin+2],[]))
            output=self.member_type(receiver,binding) if binding else None
            if binding is None or not binding.body or output is None or output.kind!='interface' or output.source.relative not in allowed: continue
            property_member=_one(output.members.get(key,[]))
            if property_member is None or self._member_value_type(output,property_member)!=('scalar',frozenset({'string'})): continue
            bs=receiver.source; bv=bs.values
            for cursor in range(binding.body[0]+1,binding.body[1]-5):
                if bv[cursor:cursor+3]!=['return','this','.'] or bv[cursor+4]!='(': continue
                producer=_one(receiver.members.get(bv[cursor+3],[]))
                if (producer is None or not producer.body or self.member_type(receiver,producer) is not output
                        or not self._flow_callback_position_live(receiver,binding,cursor,allowed)): continue
                # The returned binding must consume the same optional snapshot
                # formal through a real typed source method, not a dead factory.
                formal=self._segments(bs,producer.index+1); actual=self._segments(bs,cursor+4)
                if len(actual)!=len(formal) or not formal: continue
                first,last=formal[0]; snapshot=self.definition(bv[first+2],bs) if bv[first+1:first+2]==[':'] else None
                if snapshot is None or snapshot.source.relative not in allowed or [t.value for t in bs.tokens[first+2:last]]!=[snapshot.name,'|','undefined']: continue
                argument=bv[actual[0][0]:actual[0][1]]
                calls=[]
                for position in range(actual[0][0],actual[0][1]-4):
                    if bv[position:position+2]==['this','.'] and bv[position+3:position+5]==['(',')']:
                        supplier=_one(receiver.members.get(bv[position+2],[]))
                        if supplier is None or not supplier.body or self.member_type(receiver,supplier) is not snapshot: calls=[];break
                        calls.append(_event(receiver,supplier,'form-snapshot-source'))
                if not calls or not argument: continue
                for opening in range(producer.body[0]+1,producer.body[1]-1):
                    if bv[opening:opening+2]!=['return','{'] or not self._flow_callback_position_live(receiver,producer,opening,allowed): continue
                    properties=[span for span in self._segments_object(bs,opening+1) if bv[span[0]:span[0]+2]==[key,':']]
                    if len(properties)!=1: continue
                    left,right=properties[0]; raw=bv[left+2:right]; name=bv[first]
                    if (len(raw)!=9 or raw[:6]!=[name,'=','=','=','undefined','?'] or raw[7]!=':'
                            or self._literal_string(bs,left+8)!=fallback): continue
                    template=self._template_literal(bs,left+10)
                    match=re.fullmatch(r'([a-z][a-z0-9+.-]*://[A-Za-z0-9/_-]+/)\$\{'+re.escape(name)+r'\.([A-Za-z_$][A-Za-z0-9_$]*)\}',template or '')
                    if match is None or match[1].split('://')[0]!=fallback.split('://')[0]: continue
                    identifier=_one(snapshot.members.get(match[2],[]))
                    if identifier is None or self._member_value_type(snapshot,identifier)!=('scalar',frozenset({'string'})): continue
                    if any(bv[pos:pos+2]==[name,'='] and bv[pos+2:pos+3]!=['='] for pos in range(producer.body[0]+1,producer.body[1]-2)): continue
                    return [_event(form,method,'form-binding-return'),*provider_proof,_event(receiver,binding,'form-binding-provider'),
                        _event(receiver,producer,'form-uri-producer'),_event(output,property_member,'form-binding-key'),*calls,
                        _event(snapshot,identifier,'form-uri-identifier'),{'role':'form-uri-expression','file':bs.relative,'line':bs.tokens[left].line,
                         'key':key,'fallback':fallback,'template':template}]
        return []

    @staticmethod
    def _platform_value_rebound(source, name, begin, finish):
        # Unlike the older parameter guard, equality is a read, not rebinding.
        values=source.values
        for index in range(begin+1,finish):
            if values[index]!=name or values[index-1]=='.': continue
            after=values[index+1: index+3]
            if values[index-1] in {'const','let','var','class','function','catch'}: return True
            if after[:1] in [[':'],['=>']] or after[:1]==['='] and after[1:]!=['=']: return True
            for opening,closing in source.pairs.items():
                if values[opening]=='(' and opening<index<closing and (
                        values[closing+1:closing+2]==['=>'] or opening>0 and values[opening-1] in {'function','catch'}): return True
        return False

    def _form_loaded_root(self, target, root, allowed):
        """Exact Entry loadContent path and root lifecycle, not any idle struct."""
        source=target.source; values=source.values
        stage_method=_one(target.members.get('onWindowStageCreate',[]))
        lifecycle=_one(root.members.get('aboutToAppear',[])); build=_one(root.members.get('build',[]))
        if (stage_method is None or not stage_method.body or lifecycle is None or not lifecycle.body
                or build is None or not self._component_build_live(root,build)
                or not self._official_import(source,'window','@kit.ArkUI')): return []
        prefix=root.source.values[max(0,root.start-8):root.start]
        if 'Entry' not in prefix or 'ComponentV2' not in prefix: return []
        parameters=self._segments(source,stage_method.index+1)
        if len(parameters)!=1: return []
        first,last=parameters[0]; stage=values[first]
        if values[first+1:last]!=[':','window','.','WindowStage'] or self._platform_value_rebound(source,stage,*stage_method.body): return []
        roots=[directory for directory in self.source_roots if root.source.path.is_relative_to(directory)]
        if len(roots)!=1: return []
        destination=root.source.path.relative_to(roots[0]).with_suffix('').as_posix()
        loads=[]
        for index in range(stage_method.body[0]+1,stage_method.body[1]-4):
            if values[index:index+4]!=[stage,'.','loadContent','(']: continue
            arguments=self._segments(source,index+3)
            if len(arguments)!=1 or arguments[0][1]-arguments[0][0]!=1: continue
            if self._literal_string(source,arguments[0][0])!=destination: continue
            if self._flow_callback_position_live(target,stage_method,index,allowed): loads.append(index)
        rs=root.source; rv=rs.values
        mounts=[index for index in range(lifecycle.body[0]+1,lifecycle.body[1]-4)
            if rv[index:index+5]==['this','.','onMount','(',')']
            and self._flow_callback_position_live(root,lifecycle,index,allowed)]
        if len(loads)!=1 or len(mounts)!=1: return []
        return [_event(target,stage_method,'native-root-loader'),
            {'role':'native-root-load-path','file':source.relative,'line':source.tokens[loads[0]].line,'page':destination},
            _event(root,lifecycle,'cold-root-lifecycle')]

    def _form_want_bridge(self, target, member, allowed):
        """Want.uri -> exact exported state -> root's same-state URL consumer."""
        if member.name not in {'onCreate','onNewWant'} or not member.body or not self._extends_official(target,'UIAbility','@kit.AbilityKit'): return []
        source=target.source; values=source.values; formal=self._segments(source,member.index+1)
        if not formal or not self._official_import(source,'Want','@kit.AbilityKit'): return []
        first,last=formal[0]; want=values[first]
        if values[first+1:last]!=[':','Want'] or self._shadowed_parameter(source,want,*member.body): return []
        for index in range(member.body[0]+1,member.body[1]-5):
            if values[index:index+2]!=['this','.'] or values[index+3:index+6]!=['(',want,')']: continue
            receiver=_one(target.members.get(values[index+2],[]))
            if receiver is None or not receiver.body or not self._flow_callback_position_live(target,member,index,allowed): continue
            parameters=self._segments(source,receiver.index+1)
            if len(parameters)!=1 or values[parameters[0][0]+1:parameters[0][1]]!=[':','Want']: continue
            receiver_want=values[parameters[0][0]]
            if self._shadowed_parameter(source,receiver_want,*receiver.body): continue
            for cursor in range(receiver.body[0]+1,receiver.body[1]-6):
                if values[cursor]!='const' or values[cursor+2:cursor+7]!=['=',receiver_want,'.','uri',';']: continue
                uri=values[cursor+1]
                if self._platform_value_rebound(source,uri,cursor+6,receiver.body[1]): continue
                for write in range(cursor+7,receiver.body[1]-5):
                    if values[write+1:write+6]!=['.','pendingURL','=',uri,';']: continue
                    binding=self._binding(source,values[write]); live=self._flow_callback_position_live(target,receiver,write,allowed)
                    if binding is None or not live or self._platform_value_rebound(source,values[write],*receiver.body): continue
                    state_source,state_binding=binding
                    if state_binding.kind!='const' or not state_binding.exported: continue
                    if state_source.relative not in allowed or len(state_binding.type_tokens)!=1: continue
                    state=self.definition(state_binding.type_tokens[0].value,state_source); init=state_binding.initializer
                    if state is None or state.source.relative not in allowed or init is None or state_source.values[init:init+4]!=['new',state.name,'(',')']: continue
                    pending=_one(state.members.get('pendingURL',[])); generation=_one(state.members.get('urlGeneration',[]))
                    if (pending is None or generation is None or self._member_value_type(state,pending)!=('scalar',frozenset({'string','undefined'}))
                            or self._member_value_type(state,generation)!=('scalar',frozenset({'number'}))): continue
                    increments=[pos for pos in range(write+6,receiver.body[1]-5) if values[pos:pos+6]==[values[write],'.','urlGeneration','+','=','1']
                        and self._flow_callback_position_live(target,receiver,pos,allowed)]
                    if len(increments)!=1: continue
                    for root in self.definitions:
                        if root.kind!='struct' or root.source.relative not in allowed: continue
                        loaded=self._form_loaded_root(target,root,allowed)
                        if not loaded: continue
                        rs=root.source; rv=rs.values
                        for members in root.members.values():
                            field=_one(members)
                            if field is None or field.decorators!=('Local',) or self.member_type(root,field) is not state: continue
                            at=field.index+2+len(field.type_tokens)
                            if rv[at:at+1]!=['='] or self._binding(rs,rv[at+1])!=binding: continue
                            for methods in root.members.values():
                                consumer=_one(methods)
                                if consumer is None or not consumer.body: continue
                                for read in range(consumer.body[0]+1,consumer.body[1]-8):
                                    if rv[read]!='const' or rv[read+2:read+8]!=['=','this','.',field.name,'.','pendingURL']: continue
                                    alias=rv[read+1]
                                    if self._platform_value_rebound(rs,alias,read+8,consumer.body[1]): continue
                                    destinations=[]
                                    for call in range(read+8,consumer.body[1]-5):
                                        if rv[call:call+2]!=['this','.'] or rv[call+3:call+6]!=['(',alias,')']: continue
                                        destination=_one(root.members.get(rv[call+2],[]))
                                        if destination is None or destination.name!='onOpenURL' or not destination.body: continue
                                        args=self._segments(rs,destination.index+1)
                                        if len(args)!=1 or rv[args[0][0]+1:args[0][1]]!=[':','string']: continue
                                        name=rv[args[0][0]]; uses=[]
                                        for opening in range(destination.body[0]+1,destination.body[1]-1):
                                            if rv[opening]!='(' or opening not in rs.pairs: continue
                                            if not any(rv[a:b]==[name] for a,b in self._segments(rs,opening)): continue
                                            if not self._flow_callback_position_live(root,destination,opening,allowed): continue
                                            bound=False
                                            if opening>=3 and rv[opening-3:opening-1]==['this','.']:
                                                sink=_one(root.members.get(rv[opening-1],[]))
                                                bound=bool(sink and sink.body and sink.body[1]>sink.body[0]+1)
                                            elif opening>=3 and rv[opening-2]=='.':
                                                sink_owner=self.definition(rv[opening-3],rs)
                                                sink=_one(sink_owner.members.get(rv[opening-1],[])) if sink_owner else None
                                                bound=bool(sink_owner and sink_owner.source.relative in allowed and sink and sink.static and sink.body)
                                            elif rv[opening-1]=='Text' and 'Text' not in rs.imports and 'Text' not in rs.bindings:
                                                bound=True
                                            if bound: uses.append(opening)
                                        if not uses: continue
                                        if not self._flow_callback_position_live(root,consumer,call,allowed): continue
                                        destinations.append(_event(root,destination,'root-url-consumer'))
                                    triggers=[]
                                    for methods2 in root.members.values():
                                        trigger=_one(methods2)
                                        if trigger is None or not trigger.body or trigger is consumer: continue
                                        calls=[pos for pos in range(trigger.body[0]+1,trigger.body[1]-4) if rv[pos:pos+5]==['this','.',consumer.name,'(',')']
                                            and self._flow_callback_position_live(root,trigger,pos,allowed)]
                                        if not calls: continue
                                        if trigger.name=='onMount': triggers.append(_event(root,trigger,'cold-url-consumer-trigger'))
                                        else:
                                            prefix=next((pos for pos in range(max(root.start,trigger.index-10),trigger.index-3)
                                                if rv[pos:pos+3]==['@','Monitor','('] and self._literal_string(rs,pos+3)==field.name+'.urlGeneration'),None)
                                            if prefix is not None: triggers.append(_event(root,trigger,'warm-url-consumer-monitor'))
                                    if len(destinations)==1 and {entry['role'] for entry in triggers}=={'cold-url-consumer-trigger','warm-url-consumer-monitor'}:
                                        return [_event(target,member,'native-want-entry'),_event(target,receiver,'native-want-receiver'),*live,
                                            {'role':'native-want-uri-read','file':source.relative,'line':source.tokens[cursor].line},
                                            _event(state,pending,'pending-uri-state'),_event(state,generation,'uri-generation-state'),
                                            _event(root,field,'root-same-uri-state'),_event(root,consumer,'root-uri-reader'),*loaded,*destinations,*triggers]
        return []

    def prove_platform_route(self, description, allowed_files, owned_files):
        """Exact Form router dispatch registration, never runtime dispatch proof."""
        parsed=re.fullmatch(r'\s*([\w$]+)\.([\w$]+)(?:\(\))?\s*(?:→|->)\s*([\w$]+)\.([\w$]+)(?:\(\))?\s*',description)
        if parsed is None: return self.fail('Unsupported native Form routing syntax')
        caller_name,handler_name,target_name,member_name=parsed.groups(); allowed=set(allowed_files)
        caller=_one([d for d in self.definitions if d.name==caller_name and d.source.relative in allowed])
        target=_one([d for d in self.definitions if d.name==target_name and d.source.relative in allowed])
        if caller is None or target is None or caller.kind!='struct' or target.kind!='class': return self.fail('Native Form caller or target is not an authorized exact product definition')
        handler=_one(caller.members.get(handler_name,[])); member=_one(target.members.get(member_name,[]))
        if handler is None or member is None or not handler.body or handler.static: return self.fail('Native Form exact handler or entry is missing')
        source=caller.source; values=source.values
        # A system Form carrier must keep its module standalone.
        if any(token.value=='import' for token in source.tokens): return self.fail('Native Form carrier has an unsupported import boundary')
        if values[caller.start-2:caller.start]!=['struct',caller.name]: return self.fail('Native Form caller is not a direct component declaration')
        prefix=values[max(0,caller.start-8):caller.start]
        if '@' not in prefix or 'Entry' not in prefix or 'Component' not in prefix: return self.fail('Native Form carrier decorators are missing')
        posts=[]
        for index in range(handler.body[0]+1,handler.body[1]-2):
            if values[index:index+2]!=['postCardAction','('] or index and values[index-1] in {'.','new','function'}: continue
            if ('postCardAction' in source.bindings or any(d.name=='postCardAction' for d in source.definitions)
                    or any(values[pos:pos+2]==['function','postCardAction'] for pos in range(len(values)-1))
                    or self._shadowed_parameter(source,'postCardAction',*handler.body)
                    or not self._flow_callback_position_live(caller,handler,index,allowed)): continue
            arguments=self._segments(source,index+1)
            if len(arguments)!=2 or values[arguments[0][0]:arguments[0][1]]!=['this']: continue
            left,right=arguments[1]
            if values[left]!='{' or source.pairs.get(left)!=right-1: continue
            properties={}; bad=False
            for begin,end in self._segments_object(source,left):
                if values[begin+1]!=':' or values[begin] in properties: bad=True;break
                properties[values[begin]]=(begin+2,end)
            if bad or set(properties)!={'action','uri'}: continue
            action=properties['action']; uri=properties['uri']
            if action[1]-action[0]!=1 or self._literal_string(source,action[0])!='router' or values[uri[0]:uri[1]][:2]!=['this','.'] or uri[1]-uri[0]!=3: continue
            field=_one(caller.members.get(values[uri[0]+2],[]))
            if field is None or self._member_value_type(caller,field)!=('scalar',frozenset({'string'})): continue
            at=field.index
            if values[at-5:at-2]!=['@','LocalStorageProp','('] or values[at-1]!=')': continue
            key=self._literal_string(source,at-2)
            if any(values[pos:pos+3]==['this','.',field.name] and values[pos+3] in {'=','+','-'}
                   for pos in range(caller.start+1,caller.end-3)): continue
            if not key or values[at+3:at+4]!=['=']: continue
            fallback=self._literal_string(source,at+4)
            if not re.fullmatch(r'[a-z][a-z0-9+.-]*://[A-Za-z0-9/_-]+',fallback or ''): continue
            posts.append((index,key,fallback))
        if len(posts)!=1: return self.fail('No exact live system router action with typed LocalStorage URI')
        index,key,fallback=posts[0]; scheme=fallback.split('://')[0]
        roots=[root for root in self.source_roots if target.source.path.is_relative_to(root) and source.path.is_relative_to(root)]
        if len(roots)!=1: return self.fail('Native Form and Entry belong to different configured modules')
        main=roots[0].parent; config=main/'module.json5'; relative=config.relative_to(self.project).as_posix()
        if relative not in owned_files: return self.fail('Native Form module configuration lacks exact product ownership')
        module=read_json(config).get('module',{}); abilities=[item for item in module.get('abilities',[]) if item.get('name')==target.name]
        if module.get('mainElement')!=target.name or len(abilities)!=1: return self.fail('Native Form Entry differs from mainElement registration')
        ability=abilities[0]
        if (ability.get('exported') is not True or (main/ability.get('srcEntry','')).resolve()!=target.source.path
                or not any('entity.system.browsable' in skill.get('entities',[]) and 'ohos.want.action.viewData' in skill.get('actions',[])
                    and any(uri.get('scheme')==scheme for uri in skill.get('uris',[])) for skill in ability.get('skills',[]))):
            return self.fail('Native Form Entry path, export or browsable URI scheme is not registered')
        form_proofs=[]
        for declaration in module.get('extensionAbilities',[]):
            if declaration.get('type')!='form': continue
            form_path=(main/declaration.get('srcEntry','')).resolve()
            form=_one([d for d in self.definitions if d.source.path==form_path and d.name==declaration.get('name') and d.source.relative in allowed])
            if form is None: continue
            for metadata in declaration.get('metadata',[]):
                resource=metadata.get('resource','')
                if metadata.get('name')!='ohos.extension.form' or not re.fullmatch(r'\$profile:[A-Za-z0-9_-]+',resource): continue
                profile=main/'resources/base/profile'/(resource.split(':')[1]+'.json')
                if not profile.resolve().is_relative_to(main) or profile.relative_to(self.project).as_posix() not in owned_files: continue
                forms=read_json(profile).get('forms',[])
                registrations=[item for item in forms if item.get('name')==caller.name and item.get('uiSyntax')=='arkts' and (main/item.get('src','')).resolve()==source.path]
                if len(registrations)!=1: continue
                producer=self._form_uri_producer(form,key,fallback,allowed)
                if producer: form_proofs.append([*producer,{'role':'native-form-registration','file':profile.relative_to(self.project).as_posix(),'line':1,'form':caller.name}])
        bridge=self._form_want_bridge(target,member,allowed)
        if len(form_proofs)!=1 or not bridge: return self.fail('Native Form URI producer or exact Want/state/root input bridge is incomplete')
        return {'status':'PASS','caller':source.relative,'proof':'native-form-router-source','runtime_dispatch_verified':False,
            'evidence':[{'role':'native-form-router-dispatch','file':source.relative,'line':source.tokens[index].line},
                {'role':'native-entry-uri-registration','file':relative,'line':1,'entry':target.name,'scheme':scheme},
                *form_proofs[0],*bridge,_event(target,member,'definition')]}

    def prove_declarative(self, description, allowed_files, callback_bindings=None):
        """Source-only, bounded @Event/@Param/render proof fallback.

        Plan contracts may be attached by the strict adapter, but never grant
        a missing source edge or broaden the already resolved target authority.
        """
        parsed=re.fullmatch(r'\s*([\w$]+)\.([\w$]+)(?:\(\))?\s*(→|←|->|<-)\s*([\w$]+)\.([\w$]+)(?:\(\))?\s*',description)
        if parsed is None: return self.fail('Unsupported declarative integration syntax')
        if callback_bindings is not None and not isinstance(callback_bindings,list):
            return self.fail('Malformed declarative callback contract input')
        keys={'owner','kind','producer','event','binding','consumer','input'}
        if any(not isinstance(item,dict) or not keys<=set(item) or not set(item)<=keys|{'continuation'} or any(not isinstance(value,str) or not value for value in item.values())
               for item in callback_bindings or []): return self.fail('Malformed declarative callback contract entry')
        caller_name,handler,arrow,target_name,member_name=parsed.groups()
        caller=self.definition(caller_name)
        target=_one([definition for definition in self.definitions if definition.name==target_name
                     and definition.source.relative in allowed_files])
        if caller is None or target is None or caller.kind!='struct' or target.kind!='struct':
            return self.fail('Declarative caller or authorized target is missing or ambiguous')
        left=_one(caller.members.get(handler,[])); right=_one(target.members.get(member_name,[]))
        if left is None or right is None: return self.fail('Exact declarative handler or member is missing or ambiguous')
        if caller.source.relative not in allowed_files:
            return self.fail('Declarative caller is outside the validated product ownership closure')
        allowed=set(allowed_files); evidence=[]
        if arrow in {'→','->'} and left.kind=='method' and right.kind=='field':
            evidence=self._method_event_effect(caller,left,target,right,allowed)
        if not evidence and arrow in {'→','->'} and self._flow_event(caller,left) is not None and right.decorators==('Param',):
            emitted=self._flow_emit(caller,left,allowed)
            if emitted:
                for destination,state,instances,flow in self._flow_paths(caller,left,allowed):
                    for instance in instances:
                        if instance['child'] is not target: continue
                        param=self._flow_param(instance,right,destination,state)
                        if param: evidence=[*emitted,*flow,*param]; break
                    if evidence: break
        elif arrow in {'→','->'} and left.decorators==('Param',) and right.decorators==('Local',):
            for instance in self._flow_instances(target,allowed):
                if instance['child'] is not caller: continue
                param=self._flow_param(instance,left,target,right)
                if not param: continue
                for candidates in caller.members.values():
                    event=_one(candidates)
                    if event is None: continue
                    binding=self._flow_callback(instance,event)
                    if binding is None or binding[0]!='write' or binding[1] is not right: continue
                    emitted=self._flow_emit(caller,event,allowed)
                    if emitted: evidence=[*emitted,*binding[2],*param]; break
                if evidence: break
        elif arrow in {'←','<-'} and left.kind=='method' and left.decorators==('Builder',) and self._flow_event(target,right) is not None:
            for instance in self._flow_instances(caller,allowed):
                if instance['child'] is not target or instance['root'] is not left: continue
                binding=self._flow_callback(instance,right)
                if binding is None or binding[0]!='write': continue
                emitted=self._flow_emit(target,right,allowed)
                continuation=self._flow_continuation(caller,left,target,right,binding[1],emitted,callback_bindings or []) if emitted else []
                if continuation:
                    evidence=[*emitted,*binding[2],_event(caller,left,'declared-builder'),*continuation]; break
        if not evidence: return self.fail('No complete bounded declarative event, state and same-instance param path')
        evidence.append(_event(target,right,'definition'))
        return {'status':'PASS','caller':caller.source.relative,'proof':'native-declarative-flow','evidence':evidence}

    def prove(self, description, owned_files, *, _async_depth=0):
        parsed=re.fullmatch(r'\s*([\w$]+)\.([\w$]+)(?:\(\))?\s*(?:→|←|->|<-)\s*([\w$]+)\.([\w$]+)(?:\(\))?\s*',description)
        if not parsed: return self.fail('Unsupported integration point syntax')
        caller_name,handler,target_name,member_name=parsed.groups()
        caller=self.definition(caller_name)
        targets=[d for d in self.definitions if d.name == target_name and d.source.relative in owned_files]
        target=_one(targets)
        if caller is None or target is None:
            return self.fail('Caller or owned target definition is missing or ambiguous')
        handler_member=_one(caller.members.get(handler,[]))
        member=_one(target.members.get(member_name,[]))
        if handler_member is None or member is None:
            return self.fail('Caller handler/state or exact target member is missing or ambiguous')
        vals=caller.source.values
        evidence=self._typed_scalar_write(caller,handler_member,target,member)
        if not evidence:
            evidence=self._typed_receiver_scalar_write(caller,handler_member,target,member,owned_files)
        for i in range(caller.start+1,caller.end):
            if evidence: break
            # Static access must bind the imported (or same-file) class to the
            # exact owned definition, and the member must really be static.
            if vals[i:i+3] == [target_name,'.',member_name] and member.static:
                if (self.definition(target_name,caller.source) == target
                        and not self._shadowed_parameter(caller.source,target_name,caller.start,caller.end)
                        and self._consumed(caller,member,i+3)
                        and self._handler_link(caller,handler_member,i,None,i+3)):
                    evidence=[{'role':'caller','file':caller.source.relative,'line':caller.source.tokens[i].line},
                              *self._handler_chain(caller,handler_member,i),_event(target,member,'definition')]
                    break
            # A planned method/getter may call its own exact member without
            # instantiating another copy of its component/service.
            if (caller==target and vals[i:i+3]==['this','.',member_name] and not member.static
                    and self._consumed(caller,member,i+3)
                    and self._handler_link(caller,handler_member,i,None,i+3)):
                evidence=[{'role':'same-class-call','file':caller.source.relative,'line':caller.source.tokens[i].line},
                    _event(caller,handler_member,'handler-definition'),
                    *self._handler_chain(caller,handler_member,i),_event(target,member,'definition')]
                break
            # Shared service chains must resolve the imported live export,
            # interface slot and the exact real producer, not a global name.
            if (IDENT.fullmatch(vals[i]) and i+5<caller.end and vals[i+1]=='.' and vals[i+3]=='.'
                    and vals[i+4]==member_name and not member.static):
                binding=self._binding_slot(caller.source,vals[i],vals[i+2])
                if (binding and binding[0]==target and self._consumed(caller,member,i+5)
                        and self._handler_link(caller,handler_member,i,None,i+5)
                        and not self._shadowed_parameter(caller.source,vals[i],caller.start,caller.end)):
                    evidence=[{'role':'shared-service-call','file':caller.source.relative,'line':caller.source.tokens[i].line},
                        *self._handler_chain(caller,handler_member,i),*binding[1],_event(target,member,'definition')]
                    break
            if vals[i:i+2] != ['this','.'] or i+3 >= caller.end: continue
            field=_one(caller.members.get(vals[i+2],[]))
            if field is None or field.kind != 'field': continue
            owner=self.member_type(caller,field)
            if owner is None: continue
            cursor=i+3
            if vals[cursor] in {'!','?'}: cursor+=1
            if vals[cursor] != '.': continue
            value=vals[cursor+1]
            if (owner == target and value == member_name and not member.static
                    and self._consumed(caller,member,cursor+2)
                    and self._handler_link(caller,handler_member,i,field.name,cursor+2)):
                evidence=[{'role':'caller','file':caller.source.relative,'line':caller.source.tokens[i].line},_event(caller,field,'typed-field'),_event(target,member,'definition')]
                break
            provider=_one(owner.members.get(value,[]))
            if provider is None: continue
            proof=self._provider(owner,provider,target)
            if not proof: continue
            cursor+=2
            if vals[cursor] in {'!','?'}: cursor+=1
            if (vals[cursor:cursor+2] == ['.',member_name] and not member.static
                    and self._consumed(caller,member,cursor+2)
                    and self._handler_link(caller,handler_member,i,field.name,cursor+2)):
                evidence=[{'role':'caller','file':caller.source.relative,'line':caller.source.tokens[i].line},_event(caller,field,'typed-field'),_event(owner,provider,'provider'),*proof,_event(target,member,'definition')]
                break
        if not evidence and not member.static:
            evidence=self._self_provider_calls(caller,handler_member,target,member)
        if not evidence and not member.static:
            evidence=self._parameter_calls(caller,handler_member,target,member)
        if not evidence and handler_member.kind=='field' and self.member_type(caller,handler_member)==target:
            evidence=self._forwarded_field(caller,handler_member,target,member)
        if not evidence:
            evidence=self._bounded_static_self_path(caller,handler_member,target,member,owned_files)
        if not evidence:
            evidence=self._sheet_handler_flow(caller,handler_member,target,member,owned_files)
        if not evidence:
            evidence=self._navigation_handler_flow(caller,handler_member,target,member,owned_files)
        if not evidence and re.search(r'(?:←|<-)',description):
            evidence=self._dto_initialization_flow(caller,handler_member,target,member,owned_files)
        if not evidence and _async_depth==0 and re.search(r'(?:→|->)',description):
            evidence=self._consumed_async_self_path(caller,handler_member,target,member,owned_files)
        if not evidence:
            return self.fail('No bound static/member access found; unsupported or ambiguous forms require review')
        return {'status':'PASS','caller':caller.source.relative,'evidence':evidence}

    @staticmethod
    def _consumed(caller, member, cursor, source=None):
        values=(source or caller.source).values
        if cursor >= len(values): return False
        return values[cursor] == '(' if member.kind == 'method' else values[cursor] not in {'=',':'}

    @staticmethod
    def fail(reason):
        return {'status':'FAIL','failed_check':'C2_NATIVE_BOUND_CALL_MISSING','reason':reason,
                'repair_action':'Connect the actual caller to the declared target member, or provide an unambiguous typed native provider; do not add an unused instance.', 'evidence':[]}
