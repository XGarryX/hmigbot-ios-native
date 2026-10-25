"""Source-backed snapshot scaffolds in the original meta/view wire format."""
from pathlib import Path
import posixpath, re, xml.etree.ElementTree as ET
from hmigbot_ios.core import MigrationError
from .source import declarations

def files_for(source,symbol):
    return [p for p in sorted(source.files) if symbol.split('.')[-1] in declarations(source,p)]

def meta(source,symbol,page_id,package='',existing=None):
    files=files_for(source,symbol)
    if not files: raise MigrationError('No native declaration for '+symbol)
    value=dict(existing or {})
    if value.get('page_id') not in (None,'',page_id):
        raise MigrationError('Existing metadata belongs to a different page_id')
    if value.get('activity') and value['activity'].split('.')[-1]!=symbol.split('.')[-1]:
        raise MigrationError('Existing metadata belongs to a different native activity')
    value.update({'page_id':page_id,'activity':symbol,'package':package or value.get('package','')})
    # Enrich adds missing metadata; reviewed source/style and semantic facts survive.
    defaults={'label':'','confidence':'medium','layout_sources':files,'menu_sources':[],
        'style_sources':files,'fragment_tags':[],'recycler_item_layouts':[],
        'navigation_targets':[],'navigation_mode':'UNKNOWN',
        'dynamic_menus':{},'clickable_elements':[],'page_type':'unknown',
        'needs_immersive_safearea':None,'view_xml_synthesized':False,
        'source_platform':'ios','source_evidence':'static native declarations, not an observed device hierarchy',
        'analysis_notes':['Complete the original Phase A semantic/page-type/safe-area enrichment before Gate B']}
    for key,default in defaults.items(): value.setdefault(key,default)
    layouts=value['layout_sources']
    if not isinstance(layouts,list) or not all(isinstance(p,str) for p in layouts):
        raise MigrationError('layout_sources must be a list of native source paths')
    value['layout_sources']=list(layouts)
    seen={posixpath.normpath(p) for p in layouts}
    for path in files:
        key=posixpath.normpath(path)
        if key not in seen:
            value['layout_sources'].append(path)
            seen.add(key)
    return value

def view(source,layouts):
    root=ET.Element('hierarchy',{'synthesized':'true','source-platform':'ios','bounds-evidence':'unavailable'})
    for name in layouts:
        if name not in source.files: raise MigrationError('UI source outside selected product: '+name)
        parent=ET.SubElement(root,'node',{'class':Path(name).stem,'source-file':name,'bounds':'','resource-id':'',
                 'clickable':'false','text':'','source-evidence':'lexical-outline'})
        tokens=source.tokens(name)
        # This is a call-site outline; LLM Phase A enriches ownership, conditions and navigation.
        # Never pretend this flat outline is a computed SwiftUI layout or runtime view tree.
        for index,t in enumerate(tokens[:-1]):
            if tokens[index+1].value not in {'(','{'}: continue
            if t.value not in {'Text','Button','Toggle','TextField','SecureField','Image','List','ScrollView',
                               'VStack','HStack','ZStack','NavigationStack','NavigationLink','TabView','Picker','ForEach'}: continue
            text=''
            if index+2<len(tokens) and tokens[index+2].kind=='string': text=tokens[index+2].value
            ET.SubElement(parent,'node',{'class':'SwiftUI.'+t.value,'resource-id':'','bounds':'',
                'text':text,'source-file':name,'source-line':str(t.line),
                'clickable':'true' if t.value in {'Button','Toggle','NavigationLink','Picker'} else 'false',
                'enabled':'unknown','visibility':'unknown'})
    return ET.tostring(root,encoding='unicode')+'\n'

def visibility(source):
    result=[]; unresolved=[]
    for p in sorted(source.files):
        if p.endswith('.swift'):
            source.text(p)
            for node in source.syntax(p)['nodes']:
                if node['kind'] not in {'visibility','visibility_unresolved'}: continue
                value=node['value']
                row={'kind':'runtime-toggle','screen':value['owner'],'view_id':'',
                    'view_id_camel':'','drivers':value['drivers'],'src':p+':'+str(node['line']),
                    'expression':value['expression']}
                if node['kind']=='visibility': result.append(row)
                else: unresolved.append({**row,'reason':'render context needs original Phase A semantic enrichment'})
            continue
        # The limited Objective-C path remains unchanged; it is not Swift semantic evidence.
        code=source.code(p)
        pattern=r'\bif\s+([^\{\n]+)\{\s*(?:Text|Button|VStack|HStack|ZStack|Image|List|ScrollView)\b|\.(hidden|opacity)\s*\(([^\n]+)\)|\.isHidden\s*=\s*([^\n;]+)'
        for m in re.finditer(pattern,code):
            expr=next((v for v in (m[1],m[3],m[4]) if v),'')
            drivers=[v for v in re.findall(r'\b[A-Za-z_]\w*\b',expr) if v not in {'self','true','false','nil'}]
            line=code.count('\n',0,m.start())+1
            result.append({'kind':'runtime-toggle','screen':Path(p).stem,'view_id':'',
                'view_id_camel':'','drivers':drivers,'src':p+':'+str(line),'expression':expr})
    return {'schema':'visibility-bindings.v1','source_platform':'ios','rows':result,
            'unresolved':unresolved}

def visibility_warnings(value):
    return ['visibility: Phase A semantic enrichment required at '+row['src']+': '+row['expression']
            for row in value.get('unresolved',[])]
