"""Source-backed native navigation facts shared by ROUTE and visual verification.

Swift facts use Apple's SwiftSyntax nodes and source-accurate tokens. This is a
static evidence graph, not a runtime view hierarchy or Swift type checker.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from hmigbot_ios.core import MigrationError, safe_child

SCHEMA = 'native-routes.v1'
CONTAINERS = {'NavigationStack', 'NavigationView', 'NavigationSplitView', 'TabView',
              'VStack', 'HStack', 'ZStack', 'Group', 'ScrollView', 'List', 'Form',
              'Section', 'ForEach', 'GeometryReader', 'AnyView', 'WindowGroup'}
INTERACTIVE = {'Button', 'NavigationLink', 'Toggle', 'Picker', 'DatePicker', 'Slider',
               'Stepper', 'TextField', 'SecureField', 'TextEditor', 'Menu', 'Link',
               'UIButton', 'UITextField', 'UITextView', 'UISwitch', 'UISlider',
               'UIStepper', 'UISegmentedControl', 'UIDatePicker', 'UIAlertAction'}
CONTROLS = INTERACTIVE | CONTAINERS | {'Text', 'Image', 'Label', 'ProgressView',
              'Divider', 'Spacer', 'UITableView', 'UICollectionView', 'UILabel',
              'UIImageView', 'UIStackView', 'UIAlertAction'}
MODAL_APIS = {'sheet', 'fullScreenCover', 'alert', 'confirmationDialog', 'popover'}
NAV_APIS = {'NavigationLink', 'navigationDestination', 'pushViewController',
            'present', 'show', 'showDetailViewController', 'performSegue'} | MODAL_APIS
IB_CONTROL = {'button':'UIButton', 'textField':'UITextField', 'textView':'UITextView',
              'switch':'UISwitch', 'slider':'UISlider', 'stepper':'UIStepper',
              'segmentedControl':'UISegmentedControl', 'datePicker':'UIDatePicker',
              'label':'UILabel', 'imageView':'UIImageView', 'tableView':'UITableView',
              'collectionView':'UICollectionView'}


def sha(value):
    if not isinstance(value, bytes): value = str(value).encode('utf-8')
    return hashlib.sha256(value).hexdigest()


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


class SwiftFile:
    def __init__(self, source, name):
        self.name = name
        self.text = source.text(name)
        self.tokens = source.tokens(name)
        self.nodes = source.syntax(name)['nodes']
        self.offsets = {0:0}
        byte = 0
        for i, char in enumerate(self.text):
            byte += len(char.encode('utf-8')); self.offsets[byte] = i + 1
        self.calls = [n for n in self.nodes if n['kind'] == 'call']
        self.types = [n for n in self.nodes if n['kind'] in {'type', 'extension'}]
        self.brackets = {}; stack=[]
        for i,t in enumerate(self.tokens):
            if t.kind in {'string','regex'}: continue
            if t.value in {'(', '{', '['}: stack.append(i)
            elif t.value in {')','}',']'} and stack:
                j=stack.pop()
                if (self.tokens[j].value,t.value) in {('(',')'),('{','}'),('[',']')}:
                    self.brackets[j]=i

    def span(self, obj):
        if 'start' in obj: start,end=obj['start'],obj['end']
        else:
            try: start,end=self.offsets[obj['start_utf8']],self.offsets[obj['end_utf8']]
            except (KeyError,TypeError) as exc: raise MigrationError('Missing official native syntax span: '+self.name) from exc
        return {'file':self.name,'line':self.text.count('\n',0,start)+1,'start':start,'end':end}

    def owner(self,node):
        owners=node.get('value',{}).get('owners')
        if owners: return '.'.join(owners)
        if node.get('kind')=='type':
            parents=[n for n in self.types if n['start']<=node['start'] and node['end']<=n['end'] and (n['start'],n['end'])!=(node['start'],node['end'])]
            parents.sort(key=lambda n:-(n['end']-n['start']))
            return '.'.join([n['value'].get('name',n['value'].get('type','')) for n in parents]+[node['value']['name']])
        enclosing=[n for n in self.types if n['start']<=node['start'] and node['end']<=n['end']]
        if not enclosing: return '<file>'
        owner=min(enclosing,key=lambda n:n['end']-n['start'])
        return self.owner(owner) if owner['kind']=='type' else owner['value'].get('type','<file>')

    def within(self, span, kind=None):
        return [n for n in (self.calls if kind=='call' else self.nodes)
                if span['start']<=n['start'] and n['end']<=span['end'] and (kind in (None,'call') or n['kind']==kind)]

    def toks(self, span):
        return [t for t in self.tokens if span['start']<=t.start and t.end<=span['end']]

    def literal(self, span):
        tokens=self.toks(span)
        if len(tokens)==1 and tokens[0].kind=='string' and tokens[0].literal_is_static:
            return tokens[0].literal_value
        # LocalizedStringKey/String(localized:)/NSLocalizedString are explicit APIs.
        calls=self.within(span,'call')
        for call in calls:
            if call['value'].get('callee_name') in {'String','LocalizedStringKey','NSLocalizedString'}:
                for arg in call['value']['arguments']:
                    child=self.span(arg['span']); ts=self.toks(child)
                    if len(ts)==1 and ts[0].kind=='string' and ts[0].literal_is_static: return ts[0].literal_value
        return None

    def closures(self, call):
        result=[]
        for row in call['value'].get('trailing_closures',[]):
            result.append({'label':row['label'],**self.span(row['span']), 'body':self.span(row['body'])})
        for arg in call['value'].get('arguments',[]):
            if arg.get('is_closure'):
                sp=self.span(arg['span']); ns=[n for n in self.within(sp,'closure') if n['start']==sp['start']]
                result.append({'label':arg['label'],**sp,'body':self.span(ns[0]['value']['body']) if ns else sp})
        return result


def _xml_spans(raw,path):
    """Expat byte positions mapped to character spans for real IB element IDs."""
    import xml.parsers.expat
    parser=xml.parsers.expat.ParserCreate();stack=[];result={}
    text=raw.decode('utf-8-sig');offsets={0:0};byte=0
    # Interface Builder emits UTF-8. An explicit unsupported encoding fails visibly.
    if raw.startswith(b'\xef\xbb\xbf'):byte=3;offsets={3:0}
    for i,c in enumerate(text):byte+=len(c.encode('utf-8'));offsets[byte]=i+1
    def end_tag(start):
        quote=None
        for i in range(start,len(raw)):
            c=raw[i]
            if c in (34,39):
                if quote==c:quote=None
                elif quote is None:quote=c
            if c==62 and quote is None:return i+1
        raise MigrationError('Unclosed IB element in '+path)
    def begin(name,attrs):
        start=parser.CurrentByteIndex;tag_end=end_tag(start)
        stack.append((attrs.get('id'),start,tag_end,raw[start:tag_end].rstrip().endswith(b'/>'),parser.CurrentLineNumber))
    def end(name):
        ident,start,tag_end,empty,line=stack.pop()
        finish=tag_end if empty else end_tag(parser.CurrentByteIndex)
        if ident:result[ident]={'file':path,'line':line,'start':offsets[start],'end':offsets[finish]}
    parser.StartElementHandler=begin;parser.EndElementHandler=end
    parser.Parse(raw,True)
    return result,text


def analyze(source):
    """Return serializable facts; offsets index Source.text(), including Release view.

    Stable collections: symbols/pages/controls/routes/unknowns are lists; methods
    and modals are dictionaries keyed by native symbol/method identity. Every
    fact has file/line/start/end provenance where there is a source declaration.
    """
    if not source.root.is_dir(): raise MigrationError('Native source directory does not exist: '+str(source.root))
    if not source.files: raise MigrationError('Selected native source contains no code files')
    cache=getattr(source,'_native_routes',None)
    if cache is not None: return cache
    from .native_context import describe
    from .native_resources import selected
    resources=selected(source)
    context=describe(source)
    result={'schema':SCHEMA,'source_sha':'','source_root':str(source.root),
            'context':context,'resource_scope':resources,'symbols':[],'pages':[],'controls':[],'methods':{},
            'routes':[],'modals':{},'unknowns':[],'tab_groups':[],'native_tab_groups':[],'localization':{},'localization_records':[],
            'selected_products':list(source.selection.get('targets',[])) if source.selection else [],
            'source_product_owners':{},'source_product_ownership_scope':('selected-target-source-membership' if source.selection else 'unknown-no-product-selection')}
    files={p:SwiftFile(source,p) for p in sorted(source.files) if p.endswith('.swift')}
    identity={'root':str(source.root),'files':{p:sha(source.text(p)) for p in sorted(source.files)},
              'selection':source.selection,'configuration':source.config.get('ios',{}),
              'resources':{p:sha(safe_child(source.root,p).read_bytes()) for p in resources['files']},
              'resource_owners':{p:sorted(resources.get('owners',{}).get(p,[])) for p in resources['files']}}
    products=set(result['selected_products'])
    membership={row['path']:set(row.get('targets',[])) for row in source.selection.get('source_membership',[])} if source.selection else {}
    result['source_product_owners']={path:sorted(membership.get(path,set())&products) for path in sorted(source.files)}
    symbols={}; all_calls=[]; method_nodes={}; owner_properties={}; property_spans={}

    def unknown(reason, file, node=None, **extra):
        f=files.get(file)
        loc=f.span(node) if f and node else {'file':file,'line':1,'start':0,'end':len(source.text(file)) if file in source.files else 0}
        row={'reason':reason,**loc,**extra}
        row['id']='U'+sha(canonical_json(row))[:12]
        result['unknowns'].append(row)
        return row

    for name,f in files.items():
        for n in f.nodes:
            v=n['value']; owner=f.owner(n)
            if n['kind']=='type':
                sym=f.owner(n); row={'name':sym,'short':v['name'],'owner':owner,'kind':v['kind'],'inherits':v.get('inherits',[]),**f.span(n)}
                symbols.setdefault(sym,[]).append(row);result['symbols'].append(row)
            elif n['kind'] in {'function','initializer'}:
                signature=v.get('parameters',[])
                # Complete external label+type disambiguates overloads; extensions use real owner.
                labels=','.join(p['first_name']+':'+p['type'] for p in signature)
                key=owner+'.'+v['name']+'('+labels+')'
                if key in result['methods']:
                    key+='@'+name+':'+str(n['line'])
                span=f.span(n);body=f.span(v['body']) if v.get('body') else span
                method={'key':key,'owner':owner,'name':v['name'],'signature':v.get('signature',''),
                        'parameters':signature,'body':f.text[body['start']:body['end']],
                        'body_span':body,**span}
                method['sha256']=sha(method['body']);result['methods'][key]=method
                method_nodes.setdefault(name,[]).append(method)
            elif n['kind']=='variable':
                for binding in v['bindings']:
                    prop={'name':binding['pattern'],'type':binding['type'],'initializer':binding['initializer'],
                          'attributes':v.get('attributes',''),**f.span(n)}
                    owner_properties.setdefault(owner,[]).append(prop)
                    if binding.get('accessor'):
                        span=f.span(binding['accessor']);key=owner+'.'+binding['pattern']
                        method={'key':key,'owner':owner,'name':binding['pattern'],'signature':'computed property',
                                'parameters':[],'body':f.text[span['start']:span['end']], 'body_span':span,**span}
                        method['sha256']=sha(method['body']);result['methods'][key]=method
                        method_nodes.setdefault(name,[]).append(method);property_spans[(owner,binding['pattern'])]=span
            elif n['kind']=='call': all_calls.append((name,n))
    view_symbols={s for s,rows in symbols.items() if any(any(t in {'View','UIViewController','UINavigationController','UITabBarController','UITableViewController','UICollectionViewController','UIHostingController','App','Widget','WidgetBundle'} for base in r['inherits'] for t in re.findall(r'\w+',base)) for r in rows)}
    # Include custom subclasses of known controllers by fixed-point inheritance.
    while True:
        more={s for s,rows in symbols.items() if any(set(re.findall(r'\w+',' '.join(r['inherits'])))&view_symbols for r in rows)}
        if more<=view_symbols: break
        view_symbols|=more
    for s in sorted(view_symbols): result['pages'].extend(symbols[s])
    # Representables may share a presentation's content with ordinary Views.
    # Include them only when resolving destination candidates: omitting one can
    # falsely turn a sibling control into the sole destination. This does not
    # classify every embedded native wrapper as a standalone page.
    representables={s for s,rows in symbols.items() if any(
        set(re.findall(r'\w+',' '.join(r['inherits']))) &
        {'UIViewRepresentable','UIViewControllerRepresentable'} for r in rows)}
    while True:
        more={s for s,rows in symbols.items() if any(
            set(re.findall(r'\w+',' '.join(r['inherits']))) & representables for r in rows)}
        if more<=representables:break
        representables|=more
    destination_symbols=view_symbols|representables

    def method_at(name,node,closure=True):
        f=files[name]
        candidates=[m for m in method_nodes.get(name,[]) if m['start']<=node['start'] and node['end']<=m['end']]
        if closure:
            cs=[n for n in f.nodes if n['kind']=='closure' and n['start']<=node['start'] and node['end']<=n['end']]
            if cs:
                n=min(cs,key=lambda x:x['end']-x['start']);owner=f.owner(n);span=f.span(n)
                key=owner+'.<closure>@'+name+':'+str(span['line'])+':'+str(span['start'])
                if key not in result['methods']:
                    body=f.span(n['value']['body']);text=f.text[body['start']:body['end']]
                    result['methods'][key]={'key':key,'owner':owner,'name':'<closure>','signature':n['value'].get('signature',''),
                           'parameters':[],'body':text,'body_span':body,'sha256':sha(text),**span}
                candidates.append(result['methods'][key])
        if candidates: return min(candidates,key=lambda m:m['end']-m['start'])
        span=f.span(node);owner=f.owner(node);key=owner+'.<file>@'+name+':'+str(span['line'])+':'+str(span['start'])
        method={'key':key,'owner':owner,'name':'<file>','parameters':[],'body':f.text[span['start']:span['end']],
                'body_span':span,'signature':'source expression',**span}
        method['sha256']=sha(method['body']);result['methods'].setdefault(key,method)
        return result['methods'][key]

    def call_name(call): return call['value'].get('callee_name','')

    def call_type(call):
        v=call['value'];name=call_name(call);qualified=v.get('callee_base','')+'.'+name
        if qualified in symbols:return qualified
        if name in symbols:return name
        matches=[s for s in symbols if s.rsplit('.',1)[-1]==name]
        return matches[0] if len(matches)==1 else None

    def matching_helpers(name,call,owner):
        labels=[a['label'] for a in call['value']['arguments']]
        rows=[]
        for m in method_nodes.get(name,[]):
            if m['owner']!=owner or m['name']!=call_name(call):continue
            params=m['parameters'];expected=['' if p['first_name']=='_' else p['first_name'] for p in params]
            if labels==expected[:len(labels)] and len(labels)<=len(params) and all(p.get('default') for p in params[len(labels):]):rows.append(m)
        return rows

    def controls_in(name,span):
        return [c for c in result['controls'] if c['file']==name and span['start']<=c['start'] and c['end']<=span['end']]

    for name,n in all_calls:
        f=files[name];v=n['value'];typ=call_type(n) or call_name(n)
        if typ not in CONTROLS and typ not in view_symbols: continue
        span=f.span(n);args=v['arguments'];text=None;text_expr=None
        for arg in args:
            if arg['label'] in {'','title','label','titleKey'}:
                text=f.literal(f.span(arg['span']));text_expr=arg['expression']
                if text is not None: break
        if text is None:
            for closure in f.closures(n):
                if closure['label']=='label' or typ not in {'NavigationLink','Button'}:
                    labels=[c for c in f.within(closure['body'],'call') if call_name(c) in {'Text','Label'}]
                    for label in labels:
                        if label['value']['arguments']:
                            text=f.literal(f.span(label['value']['arguments'][0]['span']))
                            if text is not None: break
        row={'id':'C'+sha(name+':'+str(span['start']))[:12],'owner':f.owner(n),'type':typ,
             'text':text,'text_expression':text_expr,'interactive':typ in INTERACTIVE,
             'evidence':'SwiftSyntax call','visibility':'static declaration',**span}
        result['controls'].append(row)

    for control in result['controls']:
        f=files.get(control['file'])
        if not f:continue
        for node in f.nodes:
            if node['kind']!='variable':continue
            for b in node['value']['bindings']:
                if b.get('initializer_span'):
                    span=f.span(b['initializer_span'])
                    if span['start']<=control['start'] and control['end']<=span['end']:
                        control['variable']=b['pattern']
    # UIKit outlets/properties may declare a control without constructing it in Swift.
    for owner,props in owner_properties.items():
        for prop in props:
            if any(c.get('variable')==prop['name'] and c['owner']==owner for c in result['controls']):continue
            typ=prop['type'].removeprefix('UIKit.').rstrip('?!')
            if typ not in CONTROLS or not typ.startswith('UI'):continue
            result['controls'].append({'id':'C'+sha(prop['file']+':'+str(prop['start']))[:12],
                'owner':owner,'type':typ,'text':None,'text_expression':None,'interactive':typ in INTERACTIVE,
                'variable':prop['name'],'prototype':True,'evidence':'SwiftSyntax variable type; render visibility unobserved',
                'visibility':'static declaration',**{k:prop[k] for k in ['file','line','start','end']}})

    def declaration_scope(name,span):
        rows=[m for m in method_nodes.get(name,[]) if m['start']<=span['start'] and span['end']<=m['end']]
        return min(rows,key=lambda m:m['end']-m['start'])['key'] if rows else None

    def variable_control(name,variable,span):
        f=files[name];owner=f.owner({'value':{},**span});scope=declaration_scope(name,span)
        rows=[]
        for c in result['controls']:
            if c['owner']!=owner or c.get('variable')!=variable:continue
            declared_scope=declaration_scope(c['file'],c)
            if declared_scope is None:rows.append(c)
            elif c['file']==name and declared_scope==scope and c['start']<span['start']:rows.append(c)
        local=[c for c in rows if declaration_scope(c['file'],c) is not None]
        if local:return max(local,key=lambda c:c['start'])
        return rows[0] if len(rows)==1 else None

    def ax_value(f,span,allow_text=False):
        ts=f.toks(span)
        if len(ts)==1 and ts[0].kind=='string' and ts[0].literal_is_static:return ts[0].literal_value
        if allow_text:
            calls=f.within(span,'call')
            root=[n for n in calls if n['start']==span['start'] and n['end']==span['end'] and n['value'].get('callee_name')=='Text']
            if root and root[0]['value']['arguments']:
                return ax_value(f,f.span(root[0]['value']['arguments'][0]['span']))
        return None

    def attach_ax(control,field,value,expression,span):
        assignments=control.setdefault(field+'_assignments',[])
        assignments.append({'value':value,'expression':expression,'evidence':span})
        conflict=any(a['value']!=value for a in assignments)
        control[field]=None if conflict else value;control[field+'_expression']=expression
        control[field+'_dynamic']=value is None or conflict;control[field+'_evidence']=span
        if conflict:unknown('multiple accessibility values require state adjudication',span['file'],{'value':{},'start':span['start'],'end':span['end']},control_id=control['id'],field=field)

    for name,node in all_calls:
        f=files[name];v=node['value'];api=v.get('callee_name')
        if api not in {'accessibilityIdentifier','accessibilityLabel'} or not v['arguments']:continue
        arg=v['arguments'][0];arg_span=f.span(arg['span']);api_span=f.span(v['callee_name_span'])
        # The last dot before the actual modifier name terminates its exact base.
        dots=[t for t in f.tokens if node['start']<=t.start<api_span['start'] and t.value=='.']
        base={'file':name,'line':node['line'],'start':node['start'],'end':dots[-1].start if dots else api_span['start']}
        candidates=[c for c in result['controls'] if c['file']==name and c['start']==base['start'] and c['end']<=base['end']]
        control=max(candidates,key=lambda c:c['end']) if candidates else None
        if control is None:
            ts=f.toks(base);values=[t.value for t in ts]
            if len(values)==1 and ts[0].kind=='identifier':control=variable_control(name,values[0],base)
            elif len(values)==3 and values[:2]==['self','.']:control=variable_control(name,values[2],base)
        value=ax_value(f,arg_span,api=='accessibilityLabel');field='accessibility_identifier' if api=='accessibilityIdentifier' else 'accessibility_label'
        if control is not None:
            attach_ax(control,field,value,arg['expression'],api_span)
            control[field+'_value_span']=arg_span
            if value is None:unknown('dynamic '+field,name,node,control_id=control['id'],expression=arg['expression'])
        else:unknown('accessibility modifier base is not a uniquely resolved direct UI declaration',name,node,field=field,expression=arg['expression'])
    for name,f in files.items():
        for i,t in enumerate(f.tokens[:-4]):
            if t.kind!='identifier' or f.tokens[i+1].value!='.' or f.tokens[i+2].value not in {'accessibilityIdentifier','accessibilityLabel'} or f.tokens[i+3].value!='=':continue
            if i>=2 and f.tokens[i-1].value=='.' and f.tokens[i-2].value!='self':
                unknown('UIKit accessibility receiver requires source resolution',name,{'value':{},'start':t.start,'end':f.tokens[i+4].end});continue
            rhs=f.tokens[i+4];span={'file':name,'line':t.line,'start':t.start,'end':rhs.end}
            control=variable_control(name,t.value,span)
            if control is None:
                unknown('UIKit accessibility assignment variable is unresolved',name,{'value':{},**span});continue
            field='accessibility_identifier' if f.tokens[i+2].value=='accessibilityIdentifier' else 'accessibility_label'
            following=f.tokens[i+5] if i+5<len(f.tokens) else None
            single=following is None or following.value in {';','}'} or (following.line>rhs.end_line and following.value not in {'+','.', '??','?', '[','(','as','is'})
            value=rhs.literal_value if single and rhs.kind=='string' and rhs.literal_is_static else None
            expression=f.text[rhs.start:rhs.end]
            if not single and following is not None:expression=f.text[rhs.start:following.end]
            attach_ax(control,field,value,expression,span)
            if value is None:unknown('dynamic '+field,name,{'value':{},**span},control_id=control['id'],expression=expression)

    for name,node in all_calls:
        f=files[name];v=node['value']
        if v.get('callee_name') not in {'setTitle','setAttributedTitle'} or not v['arguments']:continue
        base=v.get('callee_base','').removeprefix('self.')
        text=f.literal(f.span(v['arguments'][0]['span']))
        if text is not None:
            for c in result['controls']:
                if c['file']==name and c.get('variable')==base and c['owner']==f.owner(node):c['text']=text;c['text_evidence']=f.span(node)
    for name,f in files.items():
        for i,t in enumerate(f.tokens[:-4]):
            if t.kind!='identifier' or f.tokens[i+1].value!='.' or f.tokens[i+2].value not in {'text','placeholder','title'} or f.tokens[i+3].value!='=':continue
            literal=f.tokens[i+4]
            if literal.kind!='string' or not literal.literal_is_static:continue
            for c in result['controls']:
                if c['file']==name and c.get('variable')==t.value:c['text']=literal.literal_value;c['text_evidence']={'file':name,'line':t.line,'start':t.start,'end':literal.end}

    # Source-accurate route helpers, including variables initialized to native destinations.
    def destinations(name,span,owner=None,seen=None):
        f=files[name];seen=seen or set();found=[]
        candidate_calls=[c for c in f.within(span,'call') if call_type(c) in destination_symbols or call_name(c)=='UIAlertController']
        for c in candidate_calls:
            typ=call_type(c) or call_name(c)
            if any(o['start']<=c['start'] and c['end']<=o['end'] and (o['start'],o['end'])!=(c['start'],c['end']) for o in candidate_calls):continue
            if typ in destination_symbols or typ=='UIAlertController':
                if typ not in found: found.append(typ)
        if found: return found
        ts=f.toks(span);words=[t.value for t in ts]
        if len(words)<=3:
            var=words[-1] if words else ''
            if var not in seen:
                seen=seen|{var}
                # Variable declarations must be from this scope/owner, before use.
                for n in f.nodes:
                    if n['kind']!='variable' or n['start']>span['start'] or (owner and f.owner(n)!=owner): continue
                    for b in n['value']['bindings']:
                        if b['pattern']==var and b.get('initializer_span'):
                            values=destinations(name,f.span(b['initializer_span']),owner,seen)
                            if values: return values
            # A helper returning a single concrete destination remains source evidence.
        for c in f.within(span,'call'):
            typ=call_name(c)
            helpers=[m for m in matching_helpers(name,c,owner) if m['key'] not in seen]
            if len(helpers)>1:continue
            for m in helpers:
                values=destinations(name,m['body_span'],owner,seen|{m['key']})
                found.extend(x for x in values if x not in found)
        return found

    def triggering_control(name,node):
        f=files[name]
        rows=[c for c in result['controls'] if c['file']==name and c['interactive'] and c['start']<=node['start'] and node['end']<=c['end']]
        if rows: return min(rows,key=lambda c:c['end']-c['start'])
        # A method called from an action is a genuine indirect trigger, not a definition edge.
        m=method_at(name,node,False)
        calls=[c for c in f.calls if call_name(c)==m['name'] and not (m['start']<=c['start']<m['end']) and f.owner(c)==m['owner'] and [h['key'] for h in matching_helpers(name,c,m['owner'])]==[m['key']]]
        controls=[]
        for call in calls:
            controls.extend(c for c in result['controls'] if c['file']==name and c['interactive'] and c['start']<=call['start'] and call['end']<=c['end'])
        if controls:return min(controls,key=lambda c:c['end']-c['start'])
        return None

    def binding_trigger(name,owner,expression):
        f=files[name]
        variable=expression.lstrip('$').removeprefix('self.').rsplit('.',1)[-1]
        for i,t in enumerate(f.tokens[:-2]):
            if t.kind!='identifier' or t.value!=variable:continue
            next_t=f.tokens[i+1]
            toggle=next_t.value=='.' and f.tokens[i+2].value=='toggle'
            if next_t.value!='=' and not toggle:continue
            if not toggle and f.tokens[i+2].value in {'false','nil'}:continue
            tiny={'start':t.start,'end':f.tokens[i+2].end,'line':t.line,'value':{}}
            if f.owner(tiny)!=owner:continue
            control=triggering_control(name,tiny)
            if control:return control,method_at(name,tiny)
        return None,None

    def route(name,node,target,via,target_type='page',binding=None,declared=False,reason=None,guard='none'):
        f=files[name];owner=f.owner(node);method=method_at(name,node);control=triggering_control(name,node)
        if binding:
            bc,bm=binding_trigger(name,owner,binding)
            if bc:control,method=bc,bm
        resolution='direct' if target else 'dynamic'
        span=f.span(node)
        api_span=f.span(node['value']['callee_name_span']) if node.get('value',{}).get('callee_name_span') else span
        row={'source':owner,'source_file':name,'context':('intra_helper' if control and method['name'] not in {'<closure>','body','<file>'} else 'onClick') if control else 'programmatic',
             'trigger_by':'text' if control and control['text'] else 'programmatic',
             'trigger_value':control['text'] if control and control['text'] else method['key'],
             'trigger_text':control['text'] if control else None,'target':target,'target_type':target_type,
             'registered':None,'via':via,'resolution':resolution,'static_verdict':'wired' if target else 'unresolved',
             'guard':('state:'+binding if binding else guard),'evidence_file':name,'evidence_line':api_span['line'],'api_span':api_span,'method_key':method['key'],
             'method_sha':method['sha256'],'control_id':control['id'] if control else None,
             'state_binding':binding,'declaration_only':declared,**span}
        if reason:row['unknown_reason']=reason
        result['routes'].append(row)
        if not target or declared:
            unknown(reason or 'destination declaration requires trigger adjudication',name,node,method_key=method['key'],route_index=len(result['routes'])-1)
        return row

    def modal(name,node,target,api):
        f=files[name];span=f.span(node)
        if target in symbols:
            decl=symbols[target][0];mf=files.get(decl['file']);content_span=decl
            controls=controls_in(decl['file'],decl)
            props=owner_properties.get(target,[])
            params=[{'name':p['name'],'type':p['type'],'default':p['initializer'] or None,
                     'is_callback':'->' in p['type']} for p in props if p['name']!='body' and '@State' not in p.get('attributes','')]
            for m in result['methods'].values():
                if m['owner']==target and m['name']=='init':
                    params=[{'name':p['second_name'] or p['first_name'],'type':p['type'],'default':p['default'] or None,'is_callback':'->' in p['type']} for p in m['parameters']]
            file=decl['file']
        else:
            params=[];content=f.closures(node);content_spans=[c['body'] for c in content]
            controls=[c for c in result['controls'] if c['file']==name and any(sp['start']<=c['start'] and c['end']<=sp['end'] for sp in content_spans)]
            content_span={'file':name,'line':content_spans[0]['line'],'start':min(sp['start'] for sp in content_spans),'end':max(sp['end'] for sp in content_spans)} if content_spans else span
            file=name
        result['modals'][target]={'name':target,'api':api,'file':file,'route_relevant':True,
            'native_arguments':[{'label':a['label'],'expression':a['expression'],'literal':f.literal(f.span(a['span'])),**f.span(a['span'])} for a in node['value'].get('arguments',[])],
            'unsupported_content':('UIAlertController content/action data flow requires source adjudication' if target=='UIAlertController' else None),
            'ctor_params':params,'callbacks':[p for p in params if p['is_callback']],
            'layout':None,'native_content_span':content_span,'controls':[
                {'tag':c['type'],'id':c['id'],'text':c['text'],'interactive':c['interactive'],
                 'file':c['file'],'line':c['line']} for c in controls]}

    def tab_declaration(name,node):
        """Static declarations for the original host/file/tabs wire, never nav sites.

        Tab title/key/source spans remain native evidence. Anonymous nested or
        runtime-repeated entries are explicit unknowns, not flattened siblings.
        """
        f=files[name];owner=f.owner(node);bodies=[c['body'] for c in f.closures(node)]
        calls=[c for body in bodies for c in f.within(body,'call')]
        blockers=[c for c in calls if call_name(c) in {'TabView','ForEach'}]
        modifiers=[c for c in calls if call_name(c)=='tabItem']
        label_bodies=[cl['body'] for c in modifiers for cl in f.closures(c)]
        def inside(c,span):return span['start']<=c['start'] and c['end']<=span['end']
        blockers=[b for b in blockers if not any(inside(b,label) for label in label_bodies)]
        def blocked(c):return any(inside(c,b) for b in blockers)
        candidates=[c for c in calls if call_type(c) in view_symbols and not blocked(c) and not any(inside(c,b) for b in label_bodies)]
        candidates=[c for c in candidates if not any(inside(c,o) and (c['start'],c['end'])!=(o['start'],o['end']) for o in candidates)]
        modifiers=[c for c in modifiers if not blocked(c)]
        # A repeated postfix modifier is one declaration, not two tabs.
        by_start={}
        for c in modifiers:
            if c['start'] not in by_start or c['end']>by_start[c['start']]['end']:by_start[c['start']]=c
        modifiers=sorted(by_start.values(),key=lambda c:c['start']);items=[];covered=set()
        def label_for(modifier):
            values=[];expressions=[];anchors=[];dynamic=False
            for closure in f.closures(modifier):
                for c in f.within(closure['body'],'call'):
                    if call_name(c) not in {'Label','Text'}:continue
                    args=c['value']['arguments']
                    if not args:continue
                    # Label(title: {...}, icon: {...}) carries text in its Text child.
                    if args[0].get('is_closure'):continue
                    arg=args[0];span=f.span(arg['span']);value=f.literal(span)
                    expressions.append(arg['expression']);anchors.append(span)
                    if value is None:dynamic=True
                    elif value not in values:values.append(value)
            return (values[0] if len(values)==1 and not dynamic else None,expressions,anchors)
        for modifier in modifiers:
            limit=f.span(modifier['value']['callee_name_span'])['start']
            roots=[c for c in candidates if modifier['start']<=c['start'] and c['end']<limit]
            covered.update(c['start'] for c in roots)
            label,expressions,anchors=label_for(modifier)
            target=call_type(roots[0]) if len(roots)==1 else None
            tags=[c for c in calls if call_name(c)=='tag' and c['start']==modifier['start'] and not blocked(c)]
            tag=max(tags,key=lambda c:c['end']) if tags else None
            tag_arg=tag['value']['arguments'][0] if tag and tag['value']['arguments'] else None
            item={'target':target,'target_candidates':[call_type(c) for c in roots],
                  'label':label,'label_expressions':expressions,'label_anchors':anchors,
                  'label_kind':'declared-text-or-localization-key' if label is not None else 'unknown',
                  'key_expression':tag_arg['expression'] if tag_arg else None,
                  'key_anchor':f.span(tag_arg['span']) if tag_arg else None,
                  'source':f.span(modifier),'target_source':f.span(roots[0]) if len(roots)==1 else None}
            items.append(item)
            if target is None:unknown('Tab entry has no unique direct native page type',name,modifier,host=owner,candidates=item['target_candidates'])
            if label is None:unknown('Tab label is dynamic or unavailable',name,modifier,host=owner,tab_target=target,expressions=expressions)
        for c in candidates:
            if c['start'] in covered:continue
            target=call_type(c);items.append({'target':target,'target_candidates':[target],'label':None,
                'label_kind':'unknown','label_expressions':[],'label_anchors':[],
                'key_expression':None,'key_anchor':None,'source':f.span(c),'target_source':f.span(c)})
            unknown('Tab label is dynamic or unavailable',name,c,host=owner,tab_target=target)
        # Only top-level unresolved containers belong to this group; their nested
        # TabView declarations are analyzed separately in the normal call walk.
        top_blockers=[c for c in blockers if not any(inside(c,b) and (c['start'],c['end'])!=(b['start'],b['end']) for b in blockers)]
        for c in top_blockers:
            reason='runtime ForEach tab membership is unresolved' if call_name(c)=='ForEach' else 'anonymous nested TabView has no standalone page target'
            wrapping=[m for m in modifiers if m['start']<=c['start'] and c['end']<f.span(m['value']['callee_name_span'])['start']]
            existing=next((item for item in items if wrapping and item['source']['start']==wrapping[0]['start']),None)
            item=existing or {'target':None,'target_candidates':destinations(name,f.span(c),owner),'label':None,
                  'label_kind':'unknown','label_expressions':[],'label_anchors':[],
                  'key_expression':None,'key_anchor':None,'source':f.span(c),'target_source':None}
            item['reason']=reason
            if existing is None:items.append(item)
            unknown(reason,name,c,host=owner,candidates=item['target_candidates'])
        items.sort(key=lambda item:item['source']['start'])
        members=list(dict.fromkeys(item['target'] for item in items if item['target']))
        declaration={'host':owner,'file':name,'line':node['line'],'source':f.span(node),
             'members':members,'items':items,'wire_group_emitted':len(members)>1,
             'evidence_kind':'native TabView declaration, not runtime navigation/action evidence',
             'status':'partial_unknowns' if any(item.get('reason') or item['target'] is None or item['label'] is None for item in items) else 'static'}
        result['native_tab_groups'].append(declaration)
        if len(members)>1:result['tab_groups'].append({'host':owner,'file':name,'tabs':members})

    path_bindings={}
    for name,n in all_calls:
        if call_name(n)=='NavigationStack':
            for arg in n['value']['arguments']:
                if arg['label']=='path':path_bindings.setdefault((name,files[name].owner(n)),set()).add(arg['expression'].lstrip('$').removeprefix('self.'))
    for name,n in all_calls:
        f=files[name];v=n['value'];api=call_name(n);owner=f.owner(n);args=v['arguments'];closures=f.closures(n)
        if api in {'append','removeLast','removeAll'} and v.get('callee_base','').removeprefix('self.') in path_bindings.get((name,owner),set()):
            if api=='append':route(name,n,None,'NavigationPath.append',reason='value/path destination needs native method adjudication')
            else:route(name,n,owner,'NavigationPath.'+api,'back')
            continue
        if api not in NAV_APIS and api!='TabView':continue
        if api in {'NavigationLink','navigationDestination'}|MODAL_APIS:
            content=[]
            for a in args:
                if a['label'] in {'destination','content'}:content.append(f.span(a['span']))
            for c in closures:
                if c['label'] in {'destination','content'} or (c['label']=='' and api not in {'alert','confirmationDialog'}):content.append(c['body'])
            binding=next((a['expression'] for a in args if a['label'] in {'isPresented','isActive','item'}),None)
            if api in {'alert','confirmationDialog'}:
                api_line=f.span(v['callee_name_span'])['line'] if v.get('callee_name_span') else n['line']
                target=owner+'.'+api+'@'+str(api_line)
                route(name,n,target,api,'dialog',binding);modal(name,n,target,api);continue
            targets=[]
            for span in content:
                targets.extend(x for x in destinations(name,span,owner) if x not in targets)
            declaration=(api=='navigationDestination' and not binding) or len(targets)>1
            if not targets:
                route(name,n,None,api,'dialog' if api in MODAL_APIS else 'page',binding,
                      declared=declaration,reason='dynamic/unsupported destination expression');continue
            for target in targets:
                route(name,n,target,api,'dialog' if api in MODAL_APIS else 'page',binding,declared=declaration)
                if api in MODAL_APIS:modal(name,n,target,api)
        elif api=='TabView':
            tab_declaration(name,n)
        elif api=='performSegue':
            ident=next((f.literal(f.span(a['span'])) for a in args if a['label']=='withIdentifier'),None)
            route(name,n,None,api,reason='segue identifier needs storyboard resolution' if ident else 'dynamic segue identifier')
            result['routes'][-1]['segue_identifier']=ident
        else:
            arg=next((a for a in args if a['label'] in {'','viewController','viewControllerToPresent'}),None)
            targets=destinations(name,f.span(arg['span']),owner) if arg else []
            if not targets:
                edge=route(name,n,None,api,'dialog' if api=='present' else 'page',reason='dynamic UIKit controller expression')
                if arg:
                    for nested in f.within(f.span(arg['span']),'call'):
                        if call_name(nested)=='instantiateViewController':
                            edge['controller_identifier']=next((f.literal(f.span(a['span'])) for a in nested['value']['arguments'] if a['label']=='withIdentifier'),None)
            for target in targets:
                kind='dialog' if api=='present' else 'page';route(name,n,target,api,kind)
                if kind=='dialog':
                    modal(name,n,target,api)
                    if target=='UIAlertController':
                        edge=result['routes'][-1];edge['unknown_reason']='UIAlertController content/action data flow requires source adjudication'
                        unknown(edge['unknown_reason'],name,n,method_key=edge['method_key'],route_index=len(result['routes'])-1)
        # UIKit root assignment is represented by official tokens, not source regex.
    for name,f in files.items():
        for i,t in enumerate(f.tokens[:-2]):
            if t.kind!='identifier' or t.value!='rootViewController' or f.tokens[i+1].value!='=':continue
            start=f.tokens[i+2].start;end=start
            for next_t in f.tokens[i+2:]:
                if next_t.line>t.line and next_t.value not in {'.','(','['}:break
                end=next_t.end
            span={'start':start,'end':end,'line':t.line,'value':{}}
            targets=destinations(name,span,f.owner(span))
            if not targets:route(name,span,None,'rootViewController',reason='dynamic root controller assignment')
            for target in targets:route(name,span,target,'rootViewController')

    # A destination builder is a separate presentation context. Its inline
    # controls remain facts/dialog evidence, but never inflate its host's census.
    for control in result['controls']:
        control['render_context']='host_content'
        control['native_component_reference']=control['type'] in view_symbols
    for name,n in all_calls:
        api=call_name(n)
        if api not in NAV_APIS:continue
        f=files[name];spans=[]
        for arg in n['value']['arguments']:
            if arg['label'] in {'destination','content'} or (api in {'pushViewController','present','show','showDetailViewController'} and arg['label']==''):
                spans.append(f.span(arg['span']))
        for c in f.closures(n):
            if c['label'] in {'destination','content','actions','message'} or (c['label']=='' and api in {'NavigationLink','navigationDestination'}|MODAL_APIS):spans.append(c['body'])
        for control in result['controls']:
            if control['file']==name and any(sp['start']<=control['start'] and control['end']<=sp['end'] for sp in spans):
                control['render_context']='modal_content' if api in MODAL_APIS else 'navigation_destination'

    # Interface Builder XML is a declaration graph. Segues are not proof of a live tap.
    ib_segues={};ib_identifiers={};ib_outlets=[]
    for path in sorted(p for p in resources['files'] if Path(p).suffix in {'.storyboard','.xib'}):
        if source.view and not source.view.includes(path):continue
        raw=safe_child(source.root,path).read_bytes();identity['resources'][path]=sha(raw)
        if b'<!ENTITY' in raw.upper() or b'<!DOCTYPE' in raw.upper():raise MigrationError('Unsupported XML entity in '+path)
        try:tree=ET.fromstring(raw);ib_spans,ib_text=_xml_spans(raw,path)
        except ET.ParseError as exc:raise MigrationError('Invalid Interface Builder document '+path) from exc
        ib_targets={}
        for element in tree.iter():
            if element.tag.endswith('Controller') or element.tag=='viewController':
                ident=element.get('id');name=element.get('customClass') or element.tag+'#'+str(ident)
                ib_targets[ident]=name
                if element.get('storyboardIdentifier'):ib_identifiers.setdefault(element.get('storyboardIdentifier'),set()).add(name)
                result['pages'].append({'name':name,'kind':'storyboard_controller',**ib_spans[ident],'storyboard_id':ident,'initial':ident==tree.get('initialViewController')})
        def visit(element,owner=None):
            if element.get('id') in ib_targets:owner=ib_targets[element.get('id')]
            if owner and element.tag in IB_CONTROL:
                typ=IB_CONTROL[element.tag];text=element.get('text') or element.get('title')
                if text is None:
                    state=element.find('state');text=state.get('title') if state is not None else None
                result['controls'].append({'id':element.get('id'),'owner':owner,'type':typ,'text':text,'interactive':typ in INTERACTIVE,
                    **ib_spans[element.get('id')],'evidence':'Interface Builder element','visibility':'static declaration'})
            if owner and element.tag=='outlet':
                ib_outlets.append({'owner':owner,'variable':element.get('property'),'destination':element.get('destination'),'file':path})
            if owner and element.tag=='segue':
                target=ib_targets.get(element.get('destination'));ident=element.get('identifier')
                if ident:ib_segues.setdefault((owner,ident),set()).add(target)
                result['routes'].append({'source':owner,'source_file':path,'context':'storyboard','trigger_by':'segue','trigger_value':ident or element.get('id'),
                  'trigger_text':None,'target':target,'target_type':'dialog' if element.get('kind') in {'presentation','popoverPresentation'} else 'page',
                  'registered':target is not None,'via':'storyboard.segue','resolution':'declaration','static_verdict':'declared','guard':'none',
                  'evidence_file':path,'evidence_line':ib_spans[element.get('id')]['line'],**ib_spans[element.get('id')],'declaration_only':True,
                  'method_key':owner+'.<segue>@'+path+':'+str(element.get('id')),'method_sha':sha(raw), 'control_id':None})
            for child in element:visit(child,owner)
        visit(tree)
        initial=tree.get('initialViewController')
        if initial in ib_targets:
            result.setdefault('storyboard_initial',[]).append({'file':path,'controller':ib_targets[initial],'id':initial})
    for outlet in ib_outlets:
        declared=[c for c in result['controls'] if c.get('prototype') and c['owner']==outlet['owner'] and c.get('variable')==outlet['variable']]
        native=[c for c in result['controls'] if c['file']==outlet['file'] and c['id']==outlet['destination']]
        if len(declared)==1 and len(native)==1:
            prototype=declared[0];control=native[0]
            control['variable']=prototype['variable'];control['source_declaration']={k:prototype[k] for k in ['file','line','start','end']}
            for key,value in prototype.items():
                if key.startswith('accessibility_') or key=='text_evidence':control[key]=value
            if prototype.get('text') is not None:control['text']=prototype['text']
            result['controls'].remove(prototype)

    for edge in result['routes']:
        if edge.get('controller_identifier') and len(ib_identifiers.get(edge['controller_identifier'],set()))==1:
            edge.update(target=next(iter(ib_identifiers[edge['controller_identifier']])),resolution='storyboard_identifier',static_verdict='wired');edge.pop('unknown_reason',None)
        if edge['via']=='performSegue' and edge.get('segue_identifier'):
            targets=ib_segues.get((edge['source'],edge['segue_identifier']),set())
            if len(targets)==1:
                target=next(iter(targets));edge.update(target=target,resolution='storyboard_identifier',static_verdict='wired');edge.pop('unknown_reason',None)
        if edge['via']=='storyboard.segue':
            key=edge['method_key'];path=edge['file'];text=safe_child(source.root,path).read_text(encoding='utf-8-sig');body=text[edge['start']:edge['end']];edge['method_sha']=sha(body)
            result['methods'][key]={'key':key,'owner':edge['source'],'name':'<segue>','signature':'Interface Builder segue declaration','parameters':[],
                'body':body,'sha256':edge['method_sha'],'evidence_kind':'IB segue declaration (not an imperative method)','body_span':{k:edge[k] for k in ['file','line','start','end']},**{k:edge[k] for k in ['file','line','start','end']}}
            if edge['target_type']=='dialog' and edge['target']:
                result['modals'].setdefault(edge['target'],{'name':edge['target'],'file':path,'route_relevant':True,'ctor_params':[],'callbacks':[],
                    'layout':None,'native_content_span':{'file':path,'line':1,'start':0,'end':len(body)},'controls':[
                        {'tag':c['type'],'id':c['id'],'text':c.get('text'),'interactive':c['interactive'],'file':c['file'],'line':c['line']}
                        for c in result['controls'] if c['owner']==edge['target']]})
    # Objective-C is unresolved evidence, bounded to actual lexical method bodies.
    # No SwiftParser facts or type-resolution claims are fabricated for Objective-C.
    for path in sorted(p for p in source.files if Path(p).suffix in {'.m','.mm'}):
        text=source.text(path);tokens=source.tokens(path);pairs={};stack=[]
        for i,t in enumerate(tokens):
            if t.kind in {'string','regex'}:continue
            if t.value in {'(','{','['}:stack.append(i)
            elif t.value in {')','}',']'} and stack:
                j=stack.pop()
                if (tokens[j].value,t.value) in {('(',')'),('{','}'),('[',']')}:pairs[j]=i
        implementations=list(re.finditer(r'@implementation\s+(\w+)',source.code(path)))
        objc_methods=[]
        for i,t in enumerate(tokens[:-2]):
            if t.value not in {'-','+'} or tokens[i+1].value!='(' or i+1 not in pairs:continue
            cursor=pairs[i+1]+1;begin=None
            while cursor<len(tokens):
                value=tokens[cursor].value
                if value==';':break
                if value=='{':begin=cursor;break
                if value=='(' and cursor in pairs:cursor=pairs[cursor]+1
                else:cursor+=1
            if begin is None or begin not in pairs:continue
            finish=pairs[begin];owner=next((m[1] for m in reversed(implementations) if m.start()<t.start),Path(path).stem)
            signature=text[t.start:tokens[begin].start].strip()
            # Selector labels come from the actual method signature tokens.
            selector=[];j=pairs[i+1]+1
            while j<begin:
                if tokens[j].kind=='identifier':
                    if j+1<begin and tokens[j+1].value==':':selector.append(tokens[j].value+':')
                    elif not selector and j==pairs[i+1]+1:selector.append(tokens[j].value)
                if tokens[j].value=='(' and j in pairs:j=pairs[j]+1
                else:j+=1
            key=owner+'.'+t.value+''.join(selector)
            span={'file':path,'line':t.line,'start':t.start,'end':tokens[finish].end}
            body_span={'file':path,'line':tokens[begin].line,'start':tokens[begin].start,'end':tokens[finish].end}
            body=text[body_span['start']:body_span['end']]
            objc_methods.append({'key':key,'owner':owner,'name':''.join(selector),'parameters':[],
                'signature':signature,'body':body,'body_span':body_span,'sha256':sha(body),
                'evidence_kind':'Objective-C lexical method; Clang/LLM resolution required',**span})
        markers=[t for t in tokens if t.value in {'pushViewController','presentViewController','showViewController','performSegueWithIdentifier','rootViewController'}]
        unknown('Objective-C navigation requires source adjudication',path,detected_navigation=len(markers))
        for t in markers:
            matches=[m for m in objc_methods if m['start']<=t.start<m['end']]
            if matches:method=min(matches,key=lambda m:m['end']-m['start'])
            else:
                span={'file':path,'line':t.line,'start':t.start,'end':t.end}
                key=Path(path).stem+'.<source-expression>@'+path+':'+str(t.start)
                method={'key':key,'owner':Path(path).stem,'name':'<source-expression>','parameters':[],
                    'signature':'Objective-C expression; enclosing method unavailable','body':text[t.start:t.end],
                    'body_span':span,'sha256':sha(text[t.start:t.end]),'evidence_kind':'unresolved source expression',**span}
            key=method['key'];result['methods'][key]=method
            result['routes'].append({'source':method['owner'],'source_file':path,'context':'programmatic','trigger_by':'programmatic','trigger_value':key,'trigger_text':None,
                'target':None,'target_type':'page','registered':None,'via':t.value,'resolution':'dynamic','static_verdict':'unresolved','guard':'none',
                'evidence_file':path,'evidence_line':t.line,'method_key':key,'method_sha':method['sha256'],'unknown_reason':'Objective-C requires adjudication',
                'file':path,'line':t.line,'start':t.start,'end':t.end})
    # Keep per-file/product/locale evidence. The old union is compatibility only;
    # thin_shell must not borrow an extension's localized value for an app page.
    for path in sorted(p for p in resources['files'] if Path(p).suffix in {'.strings','.xcstrings'}):
        raw=safe_child(source.root,path).read_bytes();identity['resources'][path]=sha(raw)
        text=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
        declared_owners=sorted(resources.get('owners',{}).get(path,[]))
        product_owners=sorted(set(declared_owners)&products)
        locale=next((part[:-6] for part in Path(path).parts if part.endswith('.lproj')),None)
        def record(key,values,language,reason=None):
            result['localization_records'].append({'key':key,'values':values,'file':path,
                'product_owners':product_owners,'resource_owners':declared_owners,'locale':language,
                'ownership_evidence':resources.get('evidence'),'scope':resources.get('scope'),
                'value_status':reason or 'static_string_values'})
        if path.endswith('.xcstrings'):
            try:catalog=json.loads(text)
            except ValueError as exc:raise MigrationError('Invalid string catalog: '+path) from exc
            for key,row in catalog.get('strings',{}).items():
                values=[]
                for language,loc in row.get('localizations',{}).items():
                    value=loc.get('stringUnit',{}).get('value')
                    static=[value] if isinstance(value,str) else []
                    record(key,static,language,None if static else 'no_static_string_unit')
                    values.extend(static)
                if not row.get('localizations'):record(key,[],None,'no_declared_localizations')
                result['localization'].setdefault(key,[]).extend(values or [key])
        else:
            for key,value in re.findall(r'"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;',text):
                result['localization'].setdefault(key,[]).append(value);record(key,[value],locale)
    result['unknowns']=[u for u in result['unknowns'] if 'route_index' not in u or not result['routes'][u['route_index']].get('target') or result['routes'][u['route_index']].get('declaration_only') or result['routes'][u['route_index']].get('unknown_reason')]
    for control in result['controls']:
        control.setdefault('accessibility_identifier',None)
        control.setdefault('accessibility_label',None)
    for symbol in result['symbols']:
        symbol['properties']=owner_properties.get(symbol['name'],[])
    for i,edge in enumerate(result['routes'],1):edge['id']='E'+str(i).zfill(3)
    result['source_sha']=sha(canonical_json(identity))
    result['input_identity']={'schema':SCHEMA,'source_sha':result['source_sha'],'source_root':str(source.root),'analyzer_sha':sha(Path(__file__).read_bytes())}
    source._native_routes=result
    return result


def expected_nav(facts):
    edges=facts['routes'];clickable=[e for e in edges if e.get('trigger_by') in {'text','id','tab'}]
    resolved=[e for e in clickable if e.get('target')]
    precise=[e for e in clickable if e.get('trigger_text') or e.get('trigger_by')=='id']
    return {'platform':'ios','ios_root':facts['source_root'],'android_root':facts['source_root'],
        'first_party_pkgs':[],'input_identity':facts['input_identity'],'source_facts_schema':SCHEMA,
        'stats':{'total_nav_sites':len(edges),'by_context':dict(Counter(e['context'] for e in edges)),
          'by_resolution':dict(Counter(e['resolution'] for e in edges)), 'by_static_verdict':dict(Counter(e['static_verdict'] for e in edges)),
          'clickable_sites':len(clickable),'clickable_target_resolved':len(resolved),
          'clickable_resolved_rate':len(resolved)/len(clickable) if clickable else None,
          'clickable_with_precise_trigger':len(precise),'clickable_trigger_rate':len(precise)/len(clickable) if clickable else None,
          'programmatic_sites':len(edges)-len(clickable),'unresolved_or_dynamic':sum(not e.get('target') or e.get('declaration_only',False) for e in edges),
          'screens_total':len({p['name'] for p in facts['pages']}),'screens_by_kind':dict(Counter(p['kind'] for p in facts['pages'])),
          'unknown_facts':len(facts['unknowns'])},
        'tab_groups':facts.get('tab_groups',[]),'edges':edges,'unknowns':facts['unknowns']}


def worklist(facts,expected):
    if expected.get('input_identity')!=facts['input_identity']:raise MigrationError('Native source changed; rerun extract_nav_graph from this breakpoint')
    items=[]
    for e in expected['edges']:
        flag='A_target_dynamic' if not e.get('target') else ('C_programmatic_adjudge' if e['trigger_by']=='programmatic' or e.get('declaration_only') or e.get('unknown_reason') else ('B_indirect_trigger' if e.get('context')=='intra_helper' else None))
        if not flag:continue
        key=e.get('method_key');method=facts['methods'].get(key)
        if not method or method['sha256']!=e.get('method_sha'):raise MigrationError('Missing/stale native method evidence for '+str(key))
        items.append({'edge_id':e['id'],'flag':flag,'source':e['source'],'file':e['source_file'],'line':e['evidence_line'],
          'method':method['name'],'method_key':key,'method_sha':method['sha256'],'via':e['via'],'resolution':e['resolution'],
          'current_target':e['target'],'current_trigger':e['trigger_by']+':'+str(e['trigger_value']),'method_body':method['body']})
    return {'count':len(items),'by_flag':dict(Counter(i['flag'] for i in items)),
      'unique_methods':len({i['method_key'] for i in items}),'input_identity':facts['input_identity'],
      'expected_sha':sha(canonical_json(expected)),'items':items}


def apply_verdicts(facts,expected,work,verdicts,allow_stale=False):
    fresh=worklist(facts,expected)
    if work!=fresh:raise MigrationError('Stale native worklist; rerun llm_worklist before apply_llm')
    methods=verdicts.get('method_verdicts',{});target_rules=verdicts.get('target_rules',{})
    keys={i['method_key'] for i in work['items']}
    aliases={k:facts['methods'][k]['owner']+'.'+facts['methods'][k]['name'] for k in keys}
    counts=Counter(aliases.values())
    def method_rule(key):
        if key in methods:return methods[key]
        alias=aliases.get(key)
        # Legacy short keys are safe only when no overload/closure ambiguity exists.
        if alias and counts[alias]==1:return methods.get(alias)
        return None
    covered={k for k in keys if isinstance(method_rule(k),dict)}
    coverage=len(covered)/len(keys) if keys else 1.0
    if coverage<0.85 and not allow_stale:
        raise MigrationError('裁决覆盖率 %.0f%%（%d/%d 个唯一 flag 方法）<85%%；补齐真实 method_key 裁决'%(coverage*100,len(covered),len(keys)))
    full=[];kept=[];delta=Counter();seen=set()
    for original in expected['edges']:
        e=dict(original);rule=target_rules.get(e.get('target')) or method_rule(e.get('method_key'))
        kind='dialog' if e['target_type']=='dialog' else ('back' if e['target_type']=='back' else 'page_nav')
        keep=True;note=None
        if rule is not None:
            if not isinstance(rule,dict) or type(rule.get('keep')) is not bool:raise MigrationError('Native verdict requires boolean keep: '+str(e.get('method_key')))
            keep=rule['keep'];kind=rule.get('nav_kind',kind);note=rule.get('note')
            for old,new in [('target','target'),('target_override','target'),('trigger_text','trigger_text'),('trigger_value','trigger_value'),('trigger_by','trigger_by')]:
                if old in rule:e[new]=rule[old]
            delta['llm_'+kind if keep else 'llm_ui_state_dropped']+=1
        else:delta['script_'+kind]+=1
        if not keep and not note:raise MigrationError('Dropped native route requires note: '+e['id'])
        e.update(nav_kind=kind,keep=keep,llm_note=note);full.append(e)
        canon=(e['source'],e.get('target'),e['target_type'],e['trigger_by'],str(e['trigger_value']))
        if keep and canon not in seen:kept.append(e);seen.add(canon)
    meta={'input_identity':facts['input_identity'],'expected_sha':sha(canonical_json(expected)),
          'worklist_sha':sha(canonical_json(work)),'verdicts_sha':sha(canonical_json(verdicts)),
          'coverage':{'covered_methods':len(covered),'flag_methods':len(keys),'ratio':coverage},
          'unknowns':facts['unknowns'],'unresolved_or_dynamic':sum(not e.get('target') for e in kept)}
    return ({'count':len(kept),'by_nav_kind':dict(Counter(e['nav_kind'] for e in kept)),**meta,'edges':kept},
            {'stats_delta':dict(delta),**meta,'edges':full})
