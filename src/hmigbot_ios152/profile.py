"""Map native source syntax to the 13 signal classes in the original registry."""
from collections import defaultdict
from pathlib import Path
import json, re
from hmigbot_ios.core import MigrationError
from .source import Source, anchors

# Evidence of a construct, not a count of assignments or a claim of runtime behavior.
SIGNALS={
 'permission':r'\b(?:requestAuthorization|requestWhenInUseAuthorization|requestAlwaysAuthorization|requestAccess|authorizationStatus)\b',
 'error_path':r'\b(?:throw|catch)\b',
 'state_machine':r'\benum\s+\w+|\bswitch\s+\w*(?:state|State)\b',
 'concurrency':r'\bTask\s*(?:\{|\()|\b(?:async\s+let|withTaskGroup|withThrowingTaskGroup)\b|\bDispatchQueue\b',
 'serialization':r'\b(?:Codable|Decodable|Encodable|JSONDecoder|JSONEncoder|JSONSerialization|NSCoding)\b',
 'lifecycle':r'\b(?:viewDidLoad|viewWillAppear|viewDidDisappear|deinit|onAppear|onDisappear|scenePhase)\b',
 'network':r'\b(?:URLSession|URLRequest|Alamofire|AF\.request|MoyaProvider)\b',
 'persistence':r'\b(?:UserDefaults|NSPersistentContainer|NSManagedObject|ModelContext|SecItemAdd|SecItemCopyMatching)\b',
 'numeric_const':r'\b(?:static\s+let|let\s+[A-Z][A-Z_0-9]*\s*=|(?:static\s+)?const\s+\w+)\s*[^\n;]*?\b\d+(?:\.\d+)?\b',
 'navigation':r'\b(?:NavigationLink|navigationDestination|pushViewController|popViewController|present|dismiss|fullScreenCover)\s*[({]',
 'render':r'\b(?:Canvas|CGContext|drawRect|drawPath|MTKView|CALayer)\b',
 'platform_api':r'\b(?:UIApplication|UIDevice|UNUserNotificationCenter|ActivityKit|WidgetCenter|StoreKit|CLLocationManager)\b',
}
SDK={'WXApi':'com.tencent.mm','WechatOpenSDK':'com.tencent.mm','AlipaySDK':'com.alipay',
     'Firebase':'com.google.firebase','FirebaseMessaging':'com.google.firebase','FBSDKCoreKit':'com.facebook',
     'Stripe':'com.stripe','AppsFlyerLib':'com.appsflyer','Adjust':'com.adjust','OneSignal':'com.onesignal',
     'BranchSDK':'io.branch','Mixpanel':'com.mixpanel','Amplitude':'com.amplitude'}

ENUM_CASE= re.compile(r'case\s+')
EXTENDED_REGEX= re.compile(r'#+/')

def _reject_extended_regex(code):
    # Regex contents are not stripped by the lexical source view. Reject before
    # enum discovery too: a literal can itself contain a fake enum declaration.
    if match:=EXTENDED_REGEX.search(code):
        line=code.count('\n',0,match.start())+1
        raise MigrationError(
            f'Unresolved enum syntax at line {line}: '
            'extended regex literal; requires syntax provider')

def _case_keyword(code,pos):
    # Match against the original string: a sliced string invents a word boundary
    # at the "case" suffix of identifiers such as showcase and lowercase.
    if pos and not (code[pos-1].isspace() or code[pos-1] in '{};)'):
        return None
    return ENUM_CASE.match(code,pos)

def enum_cases(code):
    """Yield declared cases from a Source.code view with strings/comments masked."""
    _reject_extended_regex(code)
    for enum in re.finditer(r'\benum\s+(\w+)\s*(?::[^\{]+)?\{',code):
        pos=enum.end(); depth=1; parens=0; brackets=0
        while pos<len(code) and depth:
            char=code[pos]
            if char=='{': depth+=1
            elif char=='}':
                depth-=1
                if depth==0 and (parens or brackets):
                    line=code.count('\n',0,pos)+1
                    raise MigrationError(
                        f'Unresolved enum syntax in {enum[1]} at line {line}: '
                        'unbalanced parentheses or brackets; requires syntax provider')
            if depth==1:
                if char=='(': parens+=1
                elif char==')': parens=max(0,parens-1)
                elif char=='[': brackets+=1
                elif char==']': brackets=max(0,brackets-1)
            if depth==1 and parens==0 and brackets==0 and (match:=_case_keyword(code,pos)):
                start=pos; pos=match.end(); part_start=pos; item_parens=0; after_comma=False
                while pos<len(code):
                    char=code[pos]
                    if after_comma and char.isspace():
                        pos+=1
                        continue
                    after_comma=False
                    if char=='(': item_parens+=1
                    elif char==')': item_parens=max(0,item_parens-1)
                    if item_parens==0 and char=='\n':
                        next_pos=pos+1
                        while next_pos<len(code) and code[next_pos].isspace(): next_pos+=1
                        if next_pos<len(code) and code[next_pos]==',':
                            pos+=1
                            continue
                    if item_parens==0 and char in ',\n;{}':
                        item=re.match(r'\s*(\w+)',code[part_start:pos])
                        if item: yield enum[1],item[1],start
                        if char!=',': break
                        part_start=pos+1; after_comma=True
                    pos+=1
                continue
            pos+=1

def scan(source,name):
    code=source.code(name); lines=source.text(name).splitlines(); found={}
    for signal,pattern in SIGNALS.items():
        evidence=[]
        for m in re.finditer(pattern,code):
            line=code.count('\n',0,m.start())+1
            evidence.append({'file':name,'line':line,'evidence':m[0],'excerpt':lines[line-1].strip()})
        if evidence: found[signal]=evidence
    return found

def instances(source,name,rules):
    text=source.code(name,strings=True); code=source.code(name); lines=source.text(name).splitlines()
    out=defaultdict(dict)
    def add(kind,id,start):
        line=text.count('\n',0,start)+1
        item=out[kind].setdefault(id,{'id':id,'sites':[],'excerpt':lines[line-1].strip()})
        if {'file':name,'line':line} not in item['sites']: item['sites'].append({'file':name,'line':line})
    for m in re.finditer(r'\b(?:track|report|onEvent|logEvent)\s*\(\s*(?:name:\s*)?@?"([^"\n]+)"',text): add('event_name','event:'+m[1],m.start())
    for m in re.finditer(r'\b(?:static\s+let|let)\s+([A-Z][A-Z_0-9]*)\s*(?::[^=\n]+)?=\s*-?\d+(?:\.\d+)?',code): add('numeric_const','const:'+m[1],m.start())
    for m in re.finditer(r'(?:[<>]=?|==|!=)\s*(\d{3,})\b',code): add('threshold_literal','threshold:'+m[1],m.start())
    if name.endswith('.swift'):
        for node in source.syntax(name)['nodes']:
            if node['kind']=='enum_case':
                value=node['value']
                add('enum_case','enum:'+value['enum_name'].strip('`')+'.'+value['name'].strip('`'),node['start'])
    else:
        for enum_name,case_name,start in enum_cases(code):
            add('enum_case','enum:'+enum_name+'.'+case_name,start)
    for m in re.finditer(r'\b(?:requestAuthorization|requestAccess)\s*\(\s*(?:for:\s*)?\.([\w]+)',code): add('permission_site','permission:'+m[1],m.start())
    for m in re.finditer(r'\bimport\s+(\w+)',code):
        sdk=SDK.get(m[1])
        if sdk in rules.get('sdk_seams',{}).get('roots',{}): add('sdk_seam','sdk:'+sdk,m.start())
    # Native WKScriptMessageHandler methods are analogous to JS bridge methods.
    if 'WKScriptMessageHandler' in code:
        for m in re.finditer(r'\bfunc\s+(userContentController)\b',code): add('js_bridge','js:'+m[1],m.start())
    return {k:list(v.values()) for k,v in out.items()}

def one(source,md,rules):
    names=anchors(md,source); counts=defaultdict(int); evidence=defaultdict(list); enum=defaultdict(dict)
    for name in names:
        for signal,items in scan(source,name).items(): evidence[signal].extend(items); counts[signal]+=len(items)
        for kind,items in instances(source,name,rules).items():
            for item in items:
                if item['id'] in enum[kind]: enum[kind][item['id']]['sites'].extend(item['sites'])
                else: enum[kind][item['id']]=item
    modules=sorted({p.split('/')[0] for p in names})
    if len(modules)>1:
        evidence['cross_module']=[{'file':names[0],'line':None,'evidence':'anchors span modules: '+', '.join(modules),'excerpt':''}]
        counts['cross_module']=1
    required={}; addenda={}
    for rule in rules['rules']:
        items=evidence.get(rule['signal'],[])
        if not items: continue
        for kind in rule['required_kinds']:
            required[kind]={'rule_id':rule['rule_id'],'signal':rule['signal'],'required_oracle':rule['required_oracle'],
                            'why':rule['why'],'evidence_count':len(items),'evidence':items}
        if rule.get('required_addendum'): addenda[rule['required_addendum']]=rule['rule_id']
    return {'feature_file':Path(md).name,'anchored_files':names,'anchored_modules':modules,
            'anchored_LOC':sum(len(source.text(p).splitlines()) for p in names),'signal_counts':dict(counts),
            'required_obligation_kinds':required,'required_addenda':addenda,
            'enumerable_instances':{k:list(v.values()) for k,v in enum.items()}}

def build(source,features,rules):
    data={p.name:one(source,p,rules) for p in sorted(Path(features).glob('*.md'))
          if re.fullmatch(r'[A-Z]{1,4}\d+-[a-z0-9-]+\.md',p.name)}
    return {'_meta':{'rules_version':rules['version'],'ios_source_root':str(source.root),
                     'features_scanned':len(data),'features_without_anchors':[k for k,v in data.items() if not v['anchored_files']]},'features':data}
