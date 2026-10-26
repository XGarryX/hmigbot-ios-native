"""Restricted token evidence for canonical capabilities and declared initialization.

This proves reviewed static structures, never runtime behavior. Unsupported
binding/control shapes fail explicitly instead of becoming successful evidence.
"""
from __future__ import annotations

import re

from .behavior import _target_tokens
from .core import MigrationError, digest, safe_child
from .native_structural_evidence import EvidenceIndex, IDENT, _one


class ClosureError(MigrationError):
    def __init__(self, code, detail='', unsupported=False):
        super().__init__(code + (': ' + detail if detail else ''))
        self.code, self.unsupported = code, unsupported


def require(ok, code, detail='', unsupported=False):
    if not ok:
        raise ClosureError(code, detail, unsupported)


def exact(value, keys, subject):
    require(isinstance(value, dict) and set(value) == set(keys), 'capability-schema-invalid', subject, True)


def tokens(text):
    require(isinstance(text, str), 'capability-schema-invalid', 'expression must be a string', True)
    parsed=_target_tokens(text)
    require(not any(t.literal for t in parsed),'capability-expression-literal-unsupported',
            'literal-opaque token equality cannot prove an expression',True)
    return [t.value for t in parsed]


def hits(values, pattern, start=0, end=None):
    end = len(values) if end is None else end
    return [i for i in range(start, end-len(pattern)+1) if values[i:i+len(pattern)] == pattern]


def reference_written(source, at, width):
    """Conservatively identify writes to an already resolved reference.

    The lexer emits operators as individual punctuation tokens. Parenthesized
    targets and non-null assertions are not a way to bypass write protection.
    """
    values=source.values; lexical=source.tokens
    left=at-1
    while left>=0 and values[left]=='(': left-=1
    if left>=0 and values[left]=='delete': return True
    if left>=1 and values[left-1:left+1] in (['+','+'],['-','-']): return True
    right=at+width
    while right<len(values) and values[right] in {')','!'}:
        # != / !== are comparisons, not non-null target assertions.
        if (values[right]=='!' and values[right+1:right+2]==['=']
                and lexical[right].end==lexical[right+1].start): break
        right+=1
    operator=[]; operator_start=right
    while right<len(values) and values[right] in set('=+-*/%&|^<>!?'):
        operator.append(values[right]); right+=1
    joined=''.join(operator)
    adjacent=all(lexical[i].end==lexical[i+1].start for i in range(operator_start,right-1))
    comparison=joined in {'==','===','!=','!==','<=','>='} and adjacent
    return joined in {'++','--'} or ('=' in joined and not comparison)


def segments(source, opening):
    end=source.pairs[opening]; start=opening+1; result=[]; cursor=start
    while cursor<end:
        if source.values[cursor]==',':
            result.append(source.values[start:cursor]); start=cursor+1
        cursor=source.pairs[cursor]+1 if cursor in source.pairs else cursor+1
    if start<end: result.append(source.values[start:end])
    return result


def sdk_imports(source):
    """Named SDK imports active in the lexer, with exact alias identities."""
    result={}; active={t.line for t in source.tokens if t.value=='import' and not t.literal}
    pattern=r"(?m)^import[ \t]+\{([^}]+)\}\s+from\s+['\"](@[^'\"]+)['\"]"
    for match in re.finditer(pattern,source.text):
        if source.text[:match.start()].count('\n')+1 not in active: continue
        for part in match[1].split(','):
            names=re.fullmatch(r'\s*([\w$]+)(?:\s+as\s+([\w$]+))?\s*',part)
            require(names is not None,'capability-sdk-import-unsupported',unsupported=True)
            local=names[2] or names[1]
            require(local not in result,'capability-sdk-import-ambiguous',local)
            result[local]=(match[2],names[1])
    return result


def functions(source):
    result={}; cursor=0
    while cursor<len(source.values)-3:
        if source.values[cursor:cursor+2]==['export','function']:
            name=source.values[cursor+2]; paren=cursor+3
            require(source.values[paren]=='(' and paren in source.pairs,'capability-syntax-unsupported',name,True)
            after=source.pairs[paren]+1
            while after<len(source.values) and source.values[after] not in {'{',';'}: after+=1
            require(after in source.pairs,'capability-syntax-unsupported',name,True)
            require(name not in result,'capability-source-ambiguous',name)
            result[name]=(after,source.pairs[after]); cursor=source.pairs[after]+1
        else: cursor=source.pairs[cursor]+1 if cursor in source.pairs else cursor+1
    return result


def member(definition, name):
    value=_one(definition.members.get(name,[])) if definition else None
    require(value is not None and value.body is not None,'capability-method-missing',name)
    body=definition.source.values[value.body[0]+1:value.body[1]]
    require(body and not (body[0]=='throw' and body.count(';')<=1),'capability-method-stub',name)
    return value


def validate_initialization(value):
    for role in ('hosts','chains'):
        for rule in value[role]:
            exact(rule,{'path','owner','method','calls','guards','result'},'initialization rule')
            require(all(isinstance(rule[k],str) for k in ('path','owner','method'))
                    and isinstance(rule['calls'],list) and isinstance(rule['guards'],list),'capability-init-invalid',unsupported=True)
            for item in rule['calls']:
                exact(item,{'receiver','method','arguments','slot'},'call')
                require(all(isinstance(item[k],str) for k in ('receiver','method','slot'))
                        and isinstance(item['arguments'],list) and all(isinstance(a,str) for a in item['arguments']),
                        'capability-init-invalid',unsupported=True)
            for guard in rule['guards']:
                exact(guard,{'mode','condition'},'guard')
                require(isinstance(guard['mode'],str) and guard['mode'] in {'if','early-return'} and isinstance(guard['condition'],str),'capability-init-invalid',unsupported=True)
            result=rule['result']
            if result=='none': continue
            require(isinstance(result,dict),'capability-init-invalid',unsupported=True)
            mode=result.get('mode')
            fields={'return-call':{'mode','call'},'expression':{'mode','expression'},
                    'boolean-state':{'mode','field','error_method','early_returns'}}
            require(isinstance(mode,str) and mode in fields,'capability-init-result-unsupported',unsupported=True)
            exact(result,fields[mode],'initialization result')
            if mode=='return-call':
                item=result['call']; exact(item,{'receiver','method','arguments','slot'},'return call')
                require(all(isinstance(item[k],str) for k in ('receiver','method','slot'))
                        and isinstance(item['arguments'],list) and all(isinstance(a,str) for a in item['arguments']),
                        'capability-init-invalid',unsupported=True)
            if mode=='expression': require(isinstance(result['expression'],str),'capability-init-invalid',unsupported=True)
            if mode=='boolean-state':
                require(isinstance(result['field'],str) and isinstance(result['error_method'],str)
                        and isinstance(result['early_returns'],list),'capability-init-invalid',unsupported=True)
                for early in result['early_returns']:
                    exact(early,{'condition','expression'},'early return')
                    require(all(isinstance(v,str) for v in early.values()),'capability-init-invalid',unsupported=True)
    for edge in value['injections']:
        exact(edge,{'slot','dependency','parameter','field'},'injection')
        require(all(isinstance(edge[k],str) for k in ('slot','dependency','field')) and type(edge['parameter']) is int,
                'capability-init-invalid',unsupported=True)
        require(edge['parameter']>=0,'capability-init-invalid',unsupported=True)


class RuntimeEvidence:
    def __init__(self, project, entries, assembly_paths, initialization):
        self.index=EvidenceIndex(project); self.entries=entries; self.init=initialization
        self.function_rules={(r['path'],r['method']) for r in initialization['chains'] if not r['owner']}
        self.rule_keys={(r['path'],r['owner'],r['method']) for role in ('hosts','chains') for r in initialization[role]}
        self.sources={s.relative:s for s in self.index.sources}
        builtins={'Error','Date','Set','Map','Array','Promise','Uint8Array','ArrayBuffer','NavPathStack'}
        for source in self.index.sources:
            require(not hits(source.values,['Reflect','.','construct','('])
                    and not hits(source.values,['Object','.','create','(']),
                    'capability-reflective-construction-unsupported',source.relative,True)
            external=set()
            active={t.line for t in source.tokens if t.value=='import' and not t.literal}
            for match in re.finditer(r"(?m)^import[ \t]+\{([^}]+)\}\s+from\s+['\"](@[^'\"]+)['\"]",source.text):
                if source.text[:match.start()].count('\n')+1 in active:
                    for part in match[1].split(','):
                        names=part.strip().split(' as '); external.add(names[-1].strip())
            for i,value in enumerate(source.values[:-2]):
                if value=='new' and self.index.definition(source.values[i+1],source) is None:
                    require(source.values[i+1] in builtins|external,'capability-constructor-unresolved',
                            source.relative+':'+str(source.tokens[i].line),True)
        self.slots={e['slot']:e for e in entries if e['kind']=='runtime-slot'}
        require(len(self.slots)==sum(e['kind']=='runtime-slot' for e in entries),'capability-slot-duplicate')
        self.definitions={}; self.variables={}; self.injected={}; self.proved=set(); self.registrations={}
        candidates=[]
        for path in assembly_paths:
            source=self.sources.get(path)
            if source and source.bindings.get('capabilityTable'): candidates.append(source)
        require(len(candidates)==1,'capability-table-not-exported','unique Base-6.5 assembly required')
        self.assembly=candidates[0]
        self.bind_table()
        self.bind_entries()
        self.bind_injections()
        for role in ('hosts','chains'):
            for rule in self.init[role]: self.check_rule(rule)
        for entry in entries:
            for method in entry['lifecycle']:
                require((entry['slot'],method) in self.proved,'capability-lifecycle-uncovered',entry['key']+'.'+method)

    def definition(self, entry):
        source=self.sources.get(entry['path'])
        require(source is not None,'capability-not-materialized',entry['path'])
        return self.index._exported_definition(source.path,entry['symbol'],set())

    def bind_table(self):
        s=self.assembly; binding=_one(s.bindings.get('capabilityTable',[]))
        require(binding and binding.exported and binding.kind=='const' and binding.initializer in s.pairs,
                'capability-table-not-exported')
        require(s.values[binding.initializer]=='{','capability-table-unsupported',unsupported=True)
        # Any local shadow/table assignment is ambiguous, even outside the root.
        for source in self.index.sources:
            for i,v in enumerate(source.values):
                if v=='capabilityTable' and i and source.values[i-1] in {'const','let','var'}:
                    require(source==s and i==binding.index,'capability-table-shadow')
                if v=='capabilityTable' and source.values[i+1:i+2]==['=']:
                    require(source==s and i==binding.index,'capability-table-reassigned')
        seen={}
        for part in segments(s,binding.initializer):
            require(len(part)==3 and part[1]==':' and IDENT.fullmatch(part[0]) and IDENT.fullmatch(part[2]),
                    'capability-table-unsupported','only slot: canonicalIdentifier is supported',True)
            key,value=part[0],part[2]
            require(key not in seen,'capability-slot-duplicate',key); seen[key]=value
        require(set(seen)==set(self.slots),'capability-kind-slot-mismatch','table and runtime slots differ')
        for source in self.index.sources:
            aliases={name for name,targets in source.imports.items() if _one(targets)==(s.path,'capabilityTable')}
            if source==s: aliases.add('capabilityTable')
            ranges=[(i+1,source.pairs[i+1]) for i,value in enumerate(source.values[:-1])
                    if value=='import' and source.values[i+1]=='{' and i+1 in source.pairs]
            for i,value in enumerate(source.values):
                if value not in aliases: continue
                if source==s and i==binding.index or any(a<i<b for a,b in ranges): continue
                require(i==0 or source.values[i-1]!='.','capability-table-shadow',source.relative)
                part=source.values[i+1:i+3]
                require(len(part)==2 and part[0]=='.' and part[1] in self.slots,
                        'capability-table-alias-unsupported',source.relative,True)
                require(not reference_written(source,i,3)
                        and (i==0 or source.values[i-1]!='delete'),'capability-table-mutated',source.relative)
        for slot,name in seen.items():
            b=_one(s.bindings.get(name,[])); e=self.slots[slot]
            require(b and b.kind=='const' and b.initializer is not None,'capability-slot-not-canonical',slot)
            at=b.initializer
            require(s.values[at]=='new' and s.values[at+2]=='(' and at+2 in s.pairs,
                    'capability-slot-null-or-unsupported',slot)
            definition=self.index.definition(s.values[at+1],s)
            require(definition is not None and definition.source.relative==e['path'] and definition.name==e['symbol'],
                    'capability-slot-provider-mismatch',slot)
            arguments=segments(s,at+2)
            require(all(len(arg)==1 and IDENT.fullmatch(arg[0]) for arg in arguments),
                    'capability-constructor-unsupported',slot,True)
            self.variables[slot]={'name':name,'arguments':[arg[0] for arg in arguments],'definition':definition}
        require(len({v['name'] for v in self.variables.values()})==len(self.variables),'capability-slot-alias-duplicate')

    def bind_entries(self):
        for e in self.entries:
            s=self.sources.get(e['path']); require(s is not None,'capability-not-materialized',e['path'])
            d=self.definition(e)
            # enum and exported @Builder functions are genuine non-class exports.
            if d is None:
                exported_enum=[at for at in hits(s.values,['export','enum',e['symbol']])
                               if not any(a<at<b for a,b in s.pairs.items() if s.values[a]=='{')]
                exported_function=e['symbol'] in functions(s)
                require(e['kind']=='artifact-only' and (exported_enum or exported_function),
                        'capability-export-missing',e['key'])
            self.definitions[e['key']]=d
            constructions=[]
            for consumer in self.index.sources:
                for i,v in enumerate(consumer.values[:-2]):
                    if v!='new': continue
                    resolved=self.index.definition(consumer.values[i+1],consumer)
                    if resolved and d and resolved.source.path==d.source.path and resolved.name==d.name:
                        require(consumer.values[i+2]=='(' and i+2 in consumer.pairs,'capability-constructor-unsupported',e['key'],True)
                        constructions.append((consumer,i))
            if e['kind']=='runtime-slot':
                require(d is not None and d.kind=='class','capability-runtime-not-class',e['key'])
                require(len(constructions)==1 and constructions[0][0]==self.assembly,'capability-instance-duplicate',e['key'])
            elif e['kind']=='scoped':
                require(d is not None and d.kind=='class','capability-scoped-not-class',e['key'])
                external=[(source,i) for source,i in constructions if source.path!=d.source.path]
                require(external,'capability-scoped-no-consumer',e['key'])
                for source,i in constructions:
                    scopes=[m.body for definition in source.definitions for members in definition.members.values() for m in members if m.body]
                    scopes+=list(functions(source).values())
                    inside=any(a<i<b for a,b in scopes)
                    for owner in source.definitions:
                        if owner.start<i<owner.end:
                            preceding=[m for values in owner.members.values() for m in values if m.index<i]
                            latest=max(preceding,key=lambda m:m.index) if preceding else None
                            if latest and latest.kind=='field' and not latest.static: inside=True
                    require(inside,'capability-scoped-global-instance',e['key'])
            elif e['kind']=='framework-created':
                require(not constructions,'capability-framework-manual-instance',e['key'])
                self.framework(e,d)
            else:
                require(not constructions,'capability-artifact-instance',e['key'])
                if d and d.kind=='class':
                    require(all(m.static for members in d.members.values() for m in members),
                            'capability-artifact-class-unsupported',e['key'],True)
                    require(not any(self.index.member_type(d,m)==d for members in d.members.values() for m in members),
                            'capability-artifact-factory',e['key'])
            for method in e['lifecycle']: member(d,method)

    def framework(self,entry,definition):
        require(definition is not None and definition.kind=='class','capability-framework-class-missing',entry['key'])
        source=definition.source; imports=sdk_imports(source); values=source.values
        declarations=hits(values,['class',definition.name])
        require(len(declarations)==1,'capability-framework-class-ambiguous',entry['key'])
        at=declarations[0]; header=values[at+2:definition.start]
        require(len(header)>=2 and header[0]=='extends','capability-framework-base-unsupported',entry['key'],True)
        base=header[1]; identity=imports.get(base)
        require(not source.bindings.get(base) and not any(d.name==base for d in source.definitions),
                'capability-framework-base-shadowed',base)
        roots=[r for r in self.index.source_roots if source.path.is_relative_to(r)]
        require(len(roots)==1,'capability-framework-module-ambiguous',entry['path'])
        main=roots[0].parent; module_file=main/'module.json5'
        from .artifact_contract import _json
        def registration(path):
            try:
                data=path.read_bytes(); value=_json(data.decode('utf-8-sig'))
            except (OSError,UnicodeError,MigrationError) as exc:
                raise ClosureError('capability-registration-unreadable',
                    'Use a real JSON-compatible module/profile registration: '+path.relative_to(self.index.project).as_posix(),True) from exc
            self.registrations[path.relative_to(self.index.project).as_posix()]=digest(data)
            return value
        module=registration(module_file)
        require(isinstance(module,dict) and isinstance(module.get('module'),dict),'capability-registration-invalid')
        relative=source.path.relative_to(main).as_posix()
        spellings={relative,'./'+relative}
        if identity==('@kit.FormKit','FormExtensionAbility'):
            require(header==['extends',base],'capability-framework-base-unsupported',entry['key'],True)
            rows=module['module'].get('extensionAbilities',[])
            require(isinstance(rows,list),'capability-registration-invalid')
            matches=[row for row in rows if isinstance(row,dict) and isinstance(row.get('srcEntry'),str) and row.get('srcEntry') in spellings]
            require(len(matches)==1 and matches[0].get('type')=='form','capability-framework-registration-mismatch',entry['key'])
        elif identity==('@kit.AbilityKit','InsightIntentEntryExecutor'):
            require(len(header)==5 and header[2]=='<' and IDENT.fullmatch(header[3]) and header[4]=='>',
                    'capability-framework-base-unsupported',entry['key'],True)
            cursor=at
            while cursor>0 and values[cursor-1] in {'export','default'}: cursor-=1
            reverse={end:start for start,end in source.pairs.items()}
            opening=reverse.get(cursor-1)
            require(opening is not None and opening>=2 and values[opening-2]=='@',
                    'capability-framework-decorator-missing',entry['key'])
            decorator=values[opening-1]
            require(imports.get(decorator)==('@kit.AbilityKit','InsightIntentEntry')
                    and not source.bindings.get(decorator),'capability-framework-decorator-mismatch',entry['key'])
            profile_file=main/'resources/base/profile/insight_intent.json'
            profile=registration(profile_file)
            require(isinstance(profile,dict) and isinstance(profile.get('insightIntentsSrcEntry'),list),
                    'capability-registration-invalid')
            matches=[row for row in profile['insightIntentsSrcEntry'] if isinstance(row,dict) and isinstance(row.get('srcEntry'),str) and row.get('srcEntry') in spellings]
            require(len(matches)==1,'capability-framework-registration-mismatch',entry['key'])
        else:
            require(False,'capability-framework-base-unsupported',entry['key'],True)

    def bind_injections(self):
        declared={}
        for edge in self.init['injections']:
            exact(edge,{'slot','dependency','parameter','field'},'injection')
            slot,dependency,position,field=(edge[k] for k in ('slot','dependency','parameter','field'))
            require(slot in self.variables and dependency in self.variables and type(position) is int and position>=0
                    and isinstance(field,str) and IDENT.fullmatch(field),'capability-injection-invalid')
            key=(slot,position); require(key not in declared,'capability-injection-duplicate'); declared[key]=edge
            variable=self.variables[slot]; args=variable['arguments']
            require(position<len(args) and args[position]==self.variables[dependency]['name'],'capability-injection-mismatch',slot)
            d=variable['definition']; ctor=member(d,'constructor'); s=d.source
            paren=ctor.index+1; params=segments(s,paren)
            require(position<len(params) and len(params[position])>=3 and params[position][1]==':','capability-constructor-unsupported',slot,True)
            require(all(len(p)==3 and IDENT.fullmatch(p[0]) and p[1]==':' and IDENT.fullmatch(p[2]) for p in params),
                    'capability-constructor-unsupported',slot,True)
            param=params[position][0]; body=s.values[ctor.body[0]+1:ctor.body[1]]
            names={p[0] for p in params}; assigned=[]
            # Only direct, unconditional parameter-to-field statements are
            # supported. No early exit, parameter replacement or hidden branch.
            require(len(body)%6==0,'capability-injection-control-unsupported',slot,True)
            for offset in range(0,len(body),6):
                statement=body[offset:offset+6]
                require(statement[0:2]==['this','.'] and IDENT.fullmatch(statement[2])
                        and statement[3]=='=' and statement[4] in names and statement[5]==';',
                        'capability-injection-control-unsupported',slot,True)
                assigned.append(statement[2])
            require(len(assigned)==len(set(assigned)),'capability-injection-field-reassigned',slot)
            require(len(hits(body,['this','.',field,'=',param,';']))==1,'capability-injection-field-mismatch',slot+'.'+field)
            writes=[at for at in hits(s.values,['this','.',field],d.start,d.end) if reference_written(s,at,3)]
            require(len(writes)==1,'capability-injection-field-reassigned',slot+'.'+field)
            self.injected[(d.source.relative,d.name,field)]=dependency
        expected={(slot,i) for slot,var in self.variables.items() for i in range(len(var['arguments']))}
        require(set(declared)==expected,'capability-injection-uncovered')

    def table_import(self,source,name='capabilityTable'):
        require(_one(source.imports.get(name,[]))==(self.assembly.path,'capabilityTable'),
                'capability-table-import-mismatch',source.relative)

    def receiver(self,source,owner,expression,slot,method):
        if slot:
            require(slot in self.slots,'capability-init-slot-unknown',slot)
            valid=source==self.assembly and expression==self.variables[slot]['name']
            parts=expression.split('.')
            if len(parts)==2 and parts[1]==slot and parts[0]!='this':
                self.table_import(source,parts[0]); valid=True
            if expression.startswith('this.') and owner:
                field=expression[5:]
                valid=self.injected.get((source.relative,owner.name,field))==slot
                if not valid:
                    m=_one(owner.members.get(field,[]))
                    if m:
                        at=m.index
                        while at<owner.end and source.values[at] not in {'=',';'}: at+=1
                        piece=source.values[at:at+5]
                        if len(piece)==5 and piece[0]=='=' and piece[2:]==['.',slot,';']:
                            self.table_import(source,piece[1]); valid=True
                            require(not hits(source.values,['this','.',field,'='],owner.start,owner.end),
                                    'capability-init-field-reassigned',field)
            require(valid,'capability-init-receiver-mismatch',expression+' -> '+slot)
            if method is not None:
                member(self.variables[slot]['definition'],method); self.proved.add((slot,method))
        elif expression=='this':
            member(owner,method)
            require((source.relative,owner.name,method) in self.rule_keys,'capability-init-local-call-uncovered',method)
        elif expression=='':
            target=_one(source.imports.get(method,[]))
            valid=source==self.assembly and method in functions(source)
            if target: valid=target[0]==self.assembly.path and target[1] in functions(self.assembly)
            remote=target[1] if target else method
            require((self.assembly.relative,remote) in self.function_rules,'capability-init-function-uncovered',method)
            require(valid,'capability-init-function-mismatch',method)
        else: require(False,'capability-init-receiver-unsupported',expression,True)

    def call(self,source,owner,body,call):
        exact(call,{'receiver','method','arguments','slot'},'call')
        receiver,method,args,slot=(call[k] for k in ('receiver','method','arguments','slot'))
        require(isinstance(receiver,str) and isinstance(method,str) and IDENT.fullmatch(method)
                and isinstance(slot,str) and isinstance(args,list) and all(isinstance(a,str) for a in args),
                'capability-init-invalid','call shape',True)
        self.receiver(source,owner,receiver,slot,method)
        pattern=tokens(receiver+'.' if receiver else '')+[method,'(']
        for i,arg in enumerate(args):
            if i: pattern.append(',')
            pattern+=tokens(arg)
        pattern.append(')')
        positions=[i for i in hits(source.values,pattern,body[0]+1,body[1]) if source.values[i-1]!='.']
        require(len(positions)==1,'capability-init-call-mismatch',receiver+'.'+method)
        return positions[0],pattern

    def check_rule(self,rule):
        exact(rule,{'path','owner','method','calls','guards','result'},'initialization rule')
        require(all(isinstance(rule[k],str) for k in ('path','owner','method')) and isinstance(rule['calls'],list)
                and isinstance(rule['guards'],list),'capability-init-invalid','rule shape',True)
        source=self.sources.get(rule['path']); require(source is not None,'capability-init-host-missing',rule['path'])
        owner=None
        if rule['owner']:
            owner=_one([d for d in source.definitions if d.name==rule['owner']])
            body=member(owner,rule['method']).body
        else:
            body=functions(source).get(rule['method']); require(body is not None,'capability-init-function-missing',rule['method'])
        expressions=[arg for item in rule['calls'] for arg in item['arguments']]+[g['condition'] for g in rule['guards']]
        if isinstance(rule['result'],dict) and rule['result'].get('mode')=='expression': expressions.append(rule['result']['expression'])
        for expression in expressions:
            parts=tokens(expression)
            for at in range(len(parts)-2):
                if owner and parts[at:at+2]==['this','.']:
                    field=_one(owner.members.get(parts[at+2],[]))
                    if field and field.kind=='getter':
                        require((source.relative,owner.name,field.name) in self.rule_keys,'capability-init-predicate-uncovered',field.name)
                    elif field:
                        expected=self.index.member_type(owner,field)
                        matches=[slot for slot,var in self.variables.items() if var['definition']==expected]
                        if len(matches)==1: self.receiver(source,owner,'this.'+field.name,matches[0],None)
        positions=[self.call(source,owner,body,call)[0] for call in rule['calls']]
        allowed_enclosures=set()
        require(positions==sorted(positions),'capability-init-call-order',rule['method'])
        for guard in rule['guards']:
            exact(guard,{'mode','condition'},'guard')
            condition=tokens(guard['condition'])
            require(condition and not any(value in {'true','false'} or value.isdecimal() for value in condition),
                    'capability-init-constant-guard-unsupported',rule['method'],True)
            if len(condition)>1 and IDENT.fullmatch(condition[0]) and condition[1]=='(':
                self.receiver(source,owner,'','',condition[0])
            pattern=['if','(']+condition+[')']
            matches=hits(source.values,pattern,body[0]+1,body[1])
            require(len(matches)==1,'capability-init-guard-missing',rule['method'])
            require(not any(body[0]<a<matches[0]<b for a,b in source.pairs.items() if source.values[a]=='{'),
                    'capability-init-guard-nondominating',rule['method'],True)
            at=matches[0]+len(pattern); end=source.pairs.get(at)
            require(end is not None and source.values[at]=='{','capability-init-guard-unsupported',rule['method'],True)
            if guard['mode']=='if': allowed_enclosures.add(at)
            if guard['mode']=='early-return':
                require(source.values[at+1:end]==['return',';'] and all(p>end for p in positions),
                        'capability-init-guard-mismatch',rule['method'])
            elif guard['mode']=='if':
                require(positions and all(at<p<end for p in positions),'capability-init-guard-mismatch',rule['method'])
            else: require(False,'capability-init-guard-unsupported',unsupported=True)
        result=rule['result']; values=source.values; inner=values[body[0]+1:body[1]]
        for position in positions:
            for opening,closing in source.pairs.items():
                if body[0]<opening<position<closing and values[opening]=='{':
                    is_try=opening>0 and values[opening-1]=='try' and isinstance(result,dict) and result.get('mode')=='boolean-state'
                    require(opening in allowed_enclosures or is_try,'capability-init-call-control-unsupported',rule['method'],True)
        if result=='none': return
        require(isinstance(result,dict) and 'mode' in result,'capability-init-result-invalid',unsupported=True)
        if result['mode']=='return-call':
            exact(result,{'mode','call'},'return-call')
            position,pattern=self.call(source,owner,body,result['call'])
            require(values[position-1]=='return' and values[position+len(pattern):body[1]]==[';']
                    and inner.count('return')==1,'capability-init-return-source')
        elif result['mode']=='expression':
            exact(result,{'mode','expression'},'expression result')
            require(inner==['return']+tokens(result['expression'])+[';'],'capability-init-return-mismatch')
        elif result['mode']=='boolean-state':
            exact(result,{'mode','field','error_method','early_returns'},'boolean-state')
            field=result['field']; error_method=result['error_method']
            require(owner is not None and isinstance(field,str) and IDENT.fullmatch(field)
                    and isinstance(error_method,str),'capability-init-result-invalid',unsupported=True)
            error_member=member(owner,error_method)
            require([t.value for t in error_member.type_tokens]==['string'],'capability-init-error-type-unsupported',unsupported=True)
            tries=hits(values,['try','{'],body[0]+1,body[1]); require(len(tries)==1,'capability-init-failure-propagation')
            start=tries[0]+1; end=source.pairs[start]
            require(values[end+1:end+3]==['catch','('] and end+2 in source.pairs,'capability-init-failure-propagation')
            catchparen=end+2; error=values[catchparen+1]; catch=source.pairs[catchparen]+1; catchend=source.pairs.get(catch)
            require(catchend is not None,'capability-init-failure-propagation')
            require('finally' not in inner and catchend+1==body[1]
                    and not any(body[0]<a<tries[0]<b for a,b in source.pairs.items() if values[a]=='{'),
                    'capability-init-exit-control-unsupported',rule['method'],True)
            require(values[catch+1:catchend]==['this','.',field,'=','this','.',error_method,'(',error,')',';','return','false',';'],
                    'capability-init-failure-propagation')
            success=values[start+1:end]
            clears=hits(values,['this','.',field,'=','null',';'],start+1,end)
            require(success[-3:]==['return','true',';'] and success.count('return')==1
                    and len(clears)==1, 'capability-init-success-propagation')
            clear=clears[0]
            require((clear==start+1 or values[clear-1] in {';','}'})
                    and not any(start<a<clear<b for a,b in source.pairs.items() if values[a] in {'{','(','['}),
                    'capability-init-success-control-unsupported',rule['method'],True)
            state_writes=[at for at in hits(values,['this','.',field],owner.start,owner.end)
                          if reference_written(source,at,3)]
            require(state_writes==[clear,catch+1], 'capability-init-state-overwritten',field)
            before=values[body[0]+1:tries[0]]
            expected=[]
            for early in result['early_returns']:
                exact(early,{'condition','expression'},'early return')
                expected+=['if','(']+tokens(early['condition'])+[')','{','return']+tokens(early['expression'])+[';','}']
            # Other ordinary assignments before try are allowed; every return
            # before it must belong to an explicitly declared early return.
            for early in result['early_returns']:
                pattern=['if','(']+tokens(early['condition'])+[')','{','return']+tokens(early['expression'])+[';','}']
                require(len(hits(before,pattern))==1,'capability-init-early-return-mismatch')
            require(before.count('return')==len(result['early_returns']),'capability-init-early-return-mismatch')
            require(all(start<p<end for p in positions),'capability-init-chain-outside-success')
        else: require(False,'capability-init-result-unsupported',unsupported=True)
