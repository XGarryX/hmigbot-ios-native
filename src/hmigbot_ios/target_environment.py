# Adapted from Garry hmigbot-ios-1.5.2.32 env_doctor; one optional target-environment entry.
"""Read-only HarmonyOS preflight with a regular argv boundary.

The retained compiled distributor cannot pass an argv list to this helper.
These are the documented mechanical checks, not a build or signing result.
"""
from pathlib import Path,PureWindowsPath
import argparse,json,math,os,platform,re,shutil,signal,subprocess,sys,tempfile

IDENT=re.compile(r'[A-Za-z_$][A-Za-z0-9_$]*')
KEY_END=re.compile(r'(?:\s|//[^\r\n\u2028\u2029]*(?:[\r\n\u2028\u2029]|$)|/\*[\s\S]*?\*/)*:')
NUMBER=re.compile(r'[+-]?(?:0[xX][0-9a-fA-F]+|(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?|Infinity|NaN)')
CLOSING=re.compile(r'\s*[}\]]')
LINE_END=re.compile(r'[\r\n\u2028\u2029]')

def string_value(source,start):
    quote=source[start];i=start+1;value=[]
    escapes=dict(zip('bfnrtv0',map(chr,[8,12,10,13,9,11,0])))
    while i<len(source):
        c=source[i];i+=1
        if c==quote:return ''.join(value),i
        if c in '\r\n':raise ValueError('Unescaped JSON5 line terminator')
        if c!='\\':value.append(c);continue
        if i==len(source):raise ValueError('Incomplete JSON5 escape')
        c=source[i];i+=1
        if c in '\r\n\u2028\u2029':
            if c=='\r' and source[i:i+1]=='\n':i+=1
            continue
        if c in 'xu':
            count=2 if c=='x' else 4;digits=source[i:i+count]
            if len(digits)!=count or re.fullmatch(r'[0-9a-fA-F]+',digits) is None:raise ValueError('Invalid JSON5 hexadecimal escape')
            value.append(chr(int(digits,16)));i+=count
        elif c in '123456789' or (c=='0' and source[i:i+1] in tuple('0123456789')):raise ValueError('JSON5 decimal escape is not allowed')
        else:value.append(escapes.get(c,c))
    raise ValueError('Unterminated JSON5 string')

def json5(path):
    """Read common Harmony JSON5, preserving JSON5 string/number semantics."""
    source=Path(path).read_text(encoding='utf-8-sig');tokens=[];i=0
    while i<len(source):
        if source.startswith('//',i):
            end=LINE_END.search(source,i);i=len(source) if end is None else end.start();tokens.append(' ')
        elif source.startswith('/*',i):
            end=source.find('*/',i+2)
            if end<0:raise ValueError('Unterminated JSON5 comment')
            i=end+2;tokens.append(' ')
        elif source[i] in ('"',"'"):
            value,i=string_value(source,i)
            tokens.append(json.dumps(value,ensure_ascii=True))
        else:
            match=IDENT.match(source,i)
            if match:
                word=match[0];i+=len(word)
                key=KEY_END.match(source,i)
                tokens.append(json.dumps(word) if key else word)
            else:
                number=NUMBER.match(source,i)
                if number:
                    token=number[0];unsigned=token.lstrip('+-')
                    if unsigned.lower().startswith('0x'):value=int(token,16)
                    else:
                        if re.match(r'0[0-9]',unsigned):raise ValueError('Leading zero in JSON5 number')
                        value=float(token) if any(c in token for c in '.eE') or unsigned in ('Infinity','NaN') else int(token)
                    tokens.append(json.dumps(value));i=number.end()
                else:tokens.append(' ' if source[i].isspace() or source[i]=='\ufeff' else source[i]);i+=1
    text=''.join(tokens);out=[];quoted=False;escaped=False;previous=''
    for i,c in enumerate(text):
        if not quoted and c==',' and CLOSING.match(text,i+1) and previous and previous not in '{[:,':continue
        out.append(c)
        if not c.isspace():previous=c
        if c=='"' and not escaped:quoted=not quoted
        escaped=(c=='\\' and not escaped) if quoted else False
    return json.loads(''.join(out))

def run(command,timeout,env=None):
    """Wait for the main probe; inherited output handles cannot delay its exit."""
    base=Path(tempfile.gettempdir()).resolve();scratch=Path(tempfile.mkdtemp(prefix='hmigbot-env-probe-',dir=base)).resolve()
    result=None
    try:
        with tempfile.TemporaryFile(dir=base) as out,tempfile.TemporaryFile(dir=base) as err:
            proc=subprocess.Popen([str(x) for x in command],stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=env,cwd=scratch,shell=False,start_new_session=os.name!='nt')
            expired=False
            try:proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                expired=proc.poll() is None
                if expired:
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    if proc.poll() is None:proc.kill()
                    proc.wait(timeout=2)
            out.seek(0);err.seek(0)
            result={'exit_code':None if expired else proc.returncode,'stdout':out.read(65536).decode('utf-8',errors='replace'),'stderr':err.read(65536).decode('utf-8',errors='replace'),'timed_out':expired}
    except OSError as exc:result={'exit_code':None,'stdout':'','stderr':str(exc),'timed_out':False,'error_type':type(exc).__name__}
    finally:
        if scratch.resolve()==scratch and scratch.is_relative_to(base) and scratch.name.startswith('hmigbot-env-probe-') and not scratch.is_symlink() and not getattr(scratch,'is_junction',lambda:False)():
            shutil.rmtree(scratch,ignore_errors=True)
        if result is not None:result['scratch_cleaned']=not scratch.exists()
    return result

def check(identifier,name,status,detail,**fields):return {'id':identifier,'name':name,'status':status,'detail':detail,**fields}
def worst(rows):return 'FAIL' if any(v['status']=='FAIL' for v in rows) else 'WARN' if any(v['status']=='WARN' for v in rows) else 'PASS'
def resolve(root,value):
    path=Path(value).expanduser()
    return path if path.is_absolute() else root/path

def installation(project,cfg):
    configured=cfg.get('deveco');candidates=[resolve(project,configured)] if configured else []
    if not candidates:
        candidates += [Path(os.environ[n]).expanduser() for n in ('DEVECO_HOME','DEVECO_SDK_HOME') if os.environ.get(n)]
        candidates += [Path('/Applications/DevEco-Studio.app/Contents')]
    roots=[p/'Contents' if (p/'Contents/tools').is_dir() else p for p in candidates]
    chosen=next((p for p in roots if p.is_dir() and (configured or (p/'tools/hvigor').is_dir())),None)
    if chosen is None:return None,check('deveco','DevEco Studio','FAIL','Configured installation is missing' if configured else 'No installation in fixed candidate locations',tools={})
    suffix='';exe=''  # Other host adapters are deferred by the release profile.
    tools={'hvigorw':chosen/('tools/hvigor/bin/hvigorw'+suffix),'ohpm':chosen/('tools/ohpm/bin/ohpm'+suffix),'java':chosen/('jbr/bin/java'+exe),'node':chosen/('tools/node/node'+exe),'hdc':chosen/('sdk/default/openharmony/toolchains/hdc'+exe)}
    sdk=Path(os.environ['DEVECO_SDK_HOME']).expanduser() if os.environ.get('DEVECO_SDK_HOME') else chosen/'sdk'
    sdk_candidates=[sdk/'default/openharmony/toolchains',sdk/'openharmony/toolchains',sdk/'toolchains']
    tools['sdk_toolchains']=next((p for p in sdk_candidates if p.is_dir()),sdk_candidates[0])
    tools['hdc']=tools['sdk_toolchains']/('hdc'+exe)
    for key,alternative in [('java',chosen/('jbr/Contents/Home/bin/java'+exe)),('node',chosen/('tools/node/bin/node'+exe))]:
        if not tools[key].is_file() and alternative.is_file():tools[key]=alternative
    for key in ('hvigorw','hdc'):
        if cfg.get(key):tools[key]=resolve(project,cfg[key])
    missing=[name for name,path in tools.items() if name!='hdc' and not (path.is_dir() if name=='sdk_toolchains' else path.is_file())]
    return tools,check('deveco','DevEco Studio','FAIL' if missing else 'PASS','Missing tools: '+', '.join(missing) if missing else 'Installation and build tool files found',root=str(chosen),tools={name:str(path) for name,path in tools.items()})

def inspect_tools(tools,timeout):
    rows=[];env=dict(os.environ)
    if tools:
        env['PATH']=os.pathsep.join(dict.fromkeys([str(p.parent) for p in tools.values()]+[p for p in env.get('PATH','').split(os.pathsep) if p]))
        if tools['java'].is_file():env['JAVA_HOME']=str(tools['java'].parent.parent)
    for name in ('hvigorw','ohpm','java','node'):
        path=tools.get(name) if tools else None
        if not path or not path.is_file():rows.append({'tool':name,'status':'FAIL','path':str(path) if path else None,'version':None,'hint':'Tool file missing'});continue
        result=run([path,'--version'],timeout,env)
        output=result['stdout']+'\n'+result['stderr']
        marker=r'(?im)^\s*(?:openjdk|java)(?:\s+version)?\s+["\']?(\d+(?:\.\d+){0,3})(?![\w.-])' if name=='java' else r'(?im)^\s*(?:(?:'+re.escape(name)+r')(?:\s+version)?\s*[:=]?\s*)?v?(\d+(?:\.\d+){1,3})\b'
        match=re.search(marker,output);version=match[1] if match else None
        status='WARN' if result['timed_out'] else 'FAIL' if result['exit_code']!=0 else 'WARN' if version is None else 'PASS'
        hint='Version probe timed out' if result['timed_out'] else result.get('error_type','Version command failed') if result['exit_code']!=0 else 'No recognized tool version' if not version else 'Version below the documented minimum' if status=='FAIL' else ''
        rows.append({'tool':name,'status':status,'path':str(path),'version':version,'exit_code':result['exit_code'],'timed_out':result['timed_out'],'hint':hint})
    return check('toolchain','编译工具链',worst(rows),', '.join(v['tool']+'='+str(v['version'] or v['status']) for v in rows),rows=rows)

def devices(tools,timeout):
    path=tools.get('hdc') if tools else None
    if not path or not path.is_file():return check('devices','鸿蒙设备','WARN','hdc unavailable; target execution deferred',hmos_targets=[],hdc_timed_out=False)
    result=run([path,'list','targets'],min(timeout,10))
    targets=[v.strip() for v in result['stdout'].splitlines() if re.fullmatch(r'[^\s\[\]]+',v.strip())] if result['exit_code']==0 else []
    return check('devices','鸿蒙设备','PASS' if targets else 'WARN','Target device identifiers listed; authorization and usability unverified' if targets else 'No target device listed; not a build result',hdc=str(path),hmos_targets=targets,hdc_timed_out=result['timed_out'],exit_code=result['exit_code'],source_platform='ios',source_runtime_verified=False)

def permission_products(data,haps):
    """Describe only explicit product membership; never guess missing targets."""
    products=data.get('app',{}).get('products')
    if not isinstance(products,list) or not products or any(not isinstance(p,dict) or not isinstance(p.get('name'),str) or not p['name'] for p in products):
        return {},['Product membership not determined']
    names=[p['name'] for p in products]
    if len(set(names))!=len(names):return {},['Duplicate product names']
    groups={name:{'haps':[],'provided_by':[]} for name in names};unknown=[]
    for hap in haps:
        module=data['modules'][hap['module_index']]
        targets=module.get('targets');members=set();known=True
        if not isinstance(targets,list) or not targets:known=False
        else:
            for target in targets:
                applies=target.get('applyToProducts') if isinstance(target,dict) else None
                if not isinstance(applies,list) or not applies or any(not isinstance(p,str) or p not in groups for p in applies):
                    known=False
                else:members.update(applies)
        if not known or not members:unknown.append(str(hap['module']))
        for name in members:
            groups[name]['haps'].append(hap['module'])
            if hap['internet_declared']:groups[name]['provided_by'].append(hap['module'])
    return groups,unknown

def permission_check(data,details,network_mode):
    mode=network_mode or 'unknown';source='default' if network_mode is None else 'cli'
    if mode not in {'unknown','required','not-required'}:raise ValueError('Invalid network mode')
    invalid=[v for v in details if v['status']=='FAIL']
    haps=[v for v in details if 'internet_declared' in v]
    providers=[v['module'] for v in haps if v['internet_declared']]
    library_declarations=[v['module'] for v in details if v.get('library_internet_declared')]
    products,unknown=permission_products(data,haps)
    uncovered=[name for name,p in products.items() if p['haps'] and not p['provided_by']]
    fields={'network_mode':mode,'network_mode_source':source,'offline_verified':False,
            'needs_confirmation':False,'provided_by':providers,'products':products,
            'membership_unknown':unknown,'uncovered_products':uncovered,'library_declarations':library_declarations,
            'dependency_permissions_verified':False,'applicable':True,'modules':details,
            'declaration_scope':'Configured src/main/module.json5 only; built variants and runtime not verified'}
    if invalid:
        return check('permissions','网络权限','FAIL','; '.join(str(v['module'])+': '+v.get('hint','') for v in invalid),**fields)
    if not haps:
        fields.update(applicable=False)
        return check('permissions','网络权限','WARN','No configured HAP modules; library declarations do not provide application permissions',**fields)
    if mode=='unknown':
        status='WARN';detail='Network permission requirement is unknown; confirm capability scope before permission acceptance'
        fields['needs_confirmation']=True
    elif mode=='not-required':
        status='PASS';detail='Not applicable: caller declares INTERNET is not required; offline application behavior was not verified'
        fields['applicable']=False
    elif not providers and library_declarations:
        status='WARN';detail='INTERNET declared in libraries but not HAPs; dependency inclusion, product scope and build-time permission merging not verified'
        fields['needs_confirmation']=True
    elif not providers:
        status='FAIL';detail='INTERNET required by caller but missing from configured main manifests; external dependencies and built variants not checked; confirm actual application permission absence before repair'
    elif len(providers)==len(haps):
        status='PASS';detail='INTERNET declared in every configured HAP; permission declaration check only'
    elif products and not unknown and all(p['provided_by'] for p in products.values() if p['haps']):
        status='PASS';detail='INTERNET provided within every explicitly mapped HAP product; declaration check only'
    else:
        status='WARN';detail='INTERNET declared, but product coverage is mixed or unknown; resolve actual build scope before permission acceptance'
        if uncovered:detail+='; configured products without a HAP declaration: '+', '.join(uncovered)
        fields['needs_confirmation']=True
    for hap in haps:
        hap.update(status=status,applicable=fields['applicable'])
        hap['provided_by']=list(dict.fromkeys(p for product in products.values() if hap['module'] in product['haps'] for p in product['provided_by']))
        if hap['internet_declared'] and hap['module'] not in hap['provided_by']:hap['provided_by'].append(hap['module'])
    return check('permissions','网络权限',status,detail,**fields)

def project_checks(project,network_mode=None):
    rows=[];profile=project/'build-profile.json5'
    if not profile.is_file():return [check('signing','签名配置','WARN','build-profile.json5 absent'),check('permissions','网络权限','WARN','Project modules not determined')]
    try:
        data=json5(profile);configs=data.get('app',{}).get('signingConfigs',[]);missing=[];declared=0
        if not isinstance(configs,list):raise ValueError('signingConfigs must be an array')
        for config in configs:
            for key,value in config.get('material',{}).items():
                if key not in {'storeFile','certpath','profile','certificate'}:continue
                declared+=1
                if not isinstance(value,str) or not value:
                    missing.append({'configuration':config.get('name'),'field':key});continue
                alien=PureWindowsPath(value).is_absolute()
                if alien or not resolve(project,value).is_file():missing.append({'configuration':config.get('name'),'field':key})
        rows.append(check('signing','签名配置','WARN' if missing else 'PASS' if declared else 'WARN','Declared signing material paths missing' if missing else 'Declared signing paths exist; signing not performed' if declared else 'No signing material paths; unsigned build may be possible',missing=missing,declared_paths=declared,signing_required=False,signing_verified=False))
        modules=data.get('modules',[]);details=[]
        if not isinstance(modules,list):raise ValueError('modules must be an array')
        for index,module in enumerate(modules):
            path=resolve(project,module.get('srcPath',module.get('name','')))/'src/main/module.json5'
            if not path.is_file():details.append({'module':module.get('name'),'status':'FAIL','hint':'module.json5 missing'});continue
            manifest=json5(path).get('module',{})
            permissions=manifest.get('requestPermissions',[])
            if not isinstance(permissions,list) or any(not isinstance(p,dict) or not isinstance(p.get('name'),str) or not p['name'] for p in permissions):
                raise ValueError('requestPermissions must be an array of named permission objects')
            names={p.get('name') for p in permissions if isinstance(p,dict)}
            if manifest.get('type') in {'har','shared'}:
                details.append({'module':module.get('name'),'status':'PASS','applicable':False,
                    'library_internet_declared':'ohos.permission.INTERNET' in names,
                    'network_info_declared':'ohos.permission.GET_NETWORK_INFO' in names,
                    'hint':'Library declaration only; dependency inclusion and permission merging not verified'});continue
            details.append({'module':module.get('name'),'module_index':index,'status':'PASS',
                'internet_declared':'ohos.permission.INTERNET' in names,'network_info_declared':'ohos.permission.GET_NETWORK_INFO' in names})
        rows.append(permission_check(data,details,network_mode))
    except (OSError,ValueError,TypeError,AttributeError) as exc:rows.append(check('project_config','工程配置','FAIL','Project configuration parse failed: '+type(exc).__name__))
    return rows

def inspect(project,timeout,network_mode=None,include_devices=False):
    from .host import require_supported_host
    require_supported_host()
    cfg={};root=project or Path.cwd()
    if project and (project/'.migbot/config.json').is_file():
        cfg=json.loads((project/'.migbot/config.json').read_text(encoding='utf-8-sig'))
        if not isinstance(cfg,dict):raise ValueError('Migration config must be an object')
    tools,item=installation(root,cfg)
    device = devices(tools,timeout) if include_devices else check('devices','鸿蒙设备','NOT_SELECTED','Device discovery is optional and was not called',actual_call=None)
    rows=[item,inspect_tools(tools,timeout),device,check('python','Python','PASS' if sys.version_info>=(3,11) else 'FAIL',platform.python_version())]
    if project:rows+=project_checks(project,network_mode)
    return {'platform':sys.platform,'generated_by':'hmos-env-doctor/scripts/env_doctor.py','implementation':'native-python-argv-adapter','project':str(project) if project else None,'checks':rows,'verdict':worst(rows),'network_mode':network_mode or 'unknown','network_mode_source':'default' if network_mode is None else 'cli','read_only':True,'external_tool_side_effects_possible':True,'source_build_verified':False,'source_runtime_verified':False,'target_build_verified':False,'behavior_verified':False}

def markdown(result):
    escape=lambda text:str(text).replace('|','\\|').replace('\r',' ').replace('\n',' ')
    return '# 环境诊断报告\n\n| 检查项 | 状态 | 详情 |\n|---|---|---|\n'+''.join('| '+escape(v['name'])+' | '+v['status']+' | '+escape(v['detail'])+' |\n' for v in result['checks'])+'\n整体：'+result['verdict']+'。本报告不证明构建、签名或行为通过。\n'

def positive(value):
    number=float(value)
    if not math.isfinite(number) or not 0<number<=600:raise argparse.ArgumentTypeError('Timeout must be finite and in (0, 600] seconds')
    return number

def main(argv=None):
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path);parser.add_argument('--timeout',type=positive,default=15)
    parser.add_argument('--network-mode',choices=['unknown','required','not-required'],default=None,
                        help='Confirmed INTERNET permission requirement; omission remains unknown (WARN)')
    parser.add_argument('--include-devices',action='store_true',help='Explicitly opt in to read-only hdc target discovery; no device control')
    parser.add_argument('--json',action='store_true');parser.add_argument('--markdown',type=Path);args=parser.parse_args(argv)
    try:
        project=args.project.resolve(strict=True) if args.project else None
        if project and not project.is_dir():raise ValueError('Project must be a directory')
        result=inspect(project,args.timeout,args.network_mode,args.include_devices)
        if args.markdown:
            output=args.markdown.resolve()
            if output.is_relative_to(Path(__file__).resolve().parents[2]):
                raise ValueError('Environment reports belong outside the tool runtime directory')
            output.parent.mkdir(parents=True,exist_ok=True);output.write_text(markdown(result),encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False))
        if not args.json:print('\n'.join(v['status']+' '+v['name']+': '+v['detail'] for v in result['checks']),file=sys.stderr)
        return 1 if result['verdict']=='FAIL' else 0
    except Exception as exc:
        print(json.dumps({'error':str(exc),'read_only':True},ensure_ascii=False),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
