"""iOS wire and canonical adapters for the retained visual verification engine.

The canonical source is always iOS. Historical Android field/path names exist
only in disposable, checked input projections consumed by the original engine.
No image judgement, coverage threshold or round verdict is invented here.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET

from hmigbot_ios.core import MigrationError, atomic_write, read_json, write_json

TRIPS = ('trip_1_logged_out', 'trip_2_logged_in_vip')
FIELDS = {'expected_ios':'expected_android', 'ios_trusted':'android_trusted',
          'ios_anchor':'android_anchor'}
EXCLUDED = {'.git','.agents','.codex','.hmigbot-ios','.hvigor','oh_modules',
            'node_modules','build','DerivedData','__pycache__','.DS_Store'}
FINALIZE_ORDER = (
    ('walk_inherit','phase2-edge-walk.md §3 step4.1: same-destination inheritance'),
    ('writeback_walk','phase2-edge-walk.md §3 step4.2: grounding and edge truth'),
    ('materialize_blackbox_to_factree','phase2-edge-walk.md §3 step4.3: blackbox oracle'),
    ('native_source_placement','phase2-edge-walk.md §3 step4.4: frozen paired baseline'),
    ('source_readiness','phase2-edge-walk.md §3 step4.5 / §6: all ledgers and inbound conservation'),
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ios_tree(value):
    source = value.get('source')
    return value.get('source_platform') == 'ios' or source == 'ios' or (
        isinstance(source,dict) and source.get('platform') == 'ios') or value.get('app',{}).get('source_platform') == 'ios'


def page_records(tree):
    for key in ('pages','fragments','dialogs'):
        values = tree.get(key, [])
        if not isinstance(values,list):
            raise MigrationError('Native visual tree requires original record arrays: '+key)
        for value in values:
            if not isinstance(value,dict):raise MigrationError('Invalid native page record in '+key)
            yield value


def _safe_name(value, kind='page'):
    if not isinstance(value,str) or not value or value in {'.','..'} or any(c in value for c in ('/','\\','\x00')):
        raise MigrationError('Unsafe '+kind+' filename')
    return value


def _source_current(tree, project, *, allow_blackbox_refresh=False, allow_manifest_collection=False):
    """Use the same selected-source identity as the native route/fact producer."""
    if not ios_tree(tree):
        raise MigrationError('An iOS canonical tree is required')
    if not isinstance(tree.get('source'),dict):
        raise MigrationError('Incompatible native fact-tree source schema; regenerate the fact tree with its source object before verification')
    project=Path(os.environ.get('HMIGBOT_NATIVE_CANONICAL_PROJECT',project)).resolve()
    expected = tree.get('native_source_sha256') or tree['source'].get('source_sha256')
    root = tree.get('native_source_root') or (tree['source'].get('ios_root') if expected else None)
    if expected or root:
        if not expected or not root:
            raise MigrationError('Incomplete native source provenance')
        from .source import Source
        from .native_routes import analyze
        context = project if (Path(project)/'.migbot/config.json').is_file() else None
        current = analyze(Source(root, context))['source_sha']
        if current != expected:
            raise MigrationError('Native source changed; regenerate affected source facts before visual verification')
    if allow_blackbox_refresh:return None
    if _blackbox_present(tree):
        receipt=_verify_blackbox_receipt(tree,project,allow_manifest_collection=allow_manifest_collection)
        return {'native_blackbox_source_inputs_sha256':receipt['inputs']['source_inputs_sha256'],
                'native_classification_status':'pending_rematerialization' if receipt.get('_collection_pending') else 'current'}
    if allow_manifest_collection and (tree.get('native_source_root') or tree['source'].get('ios_root')):
        inputs=_blackbox_source_inputs(tree,project)
        return {'native_blackbox_source_inputs_sha256':_json_digest(inputs),'native_classification_status':'raw_observation'}
    return None


def legacy_wire(value):
    """One-way derived aliases. Old wire values never override iOS truth."""
    if isinstance(value,list): return [legacy_wire(x) for x in value]
    if not isinstance(value,dict): return value
    out = {k:legacy_wire(v) for k,v in value.items() if k not in FIELDS.values()}
    for native,old in FIELDS.items():
        if native in value: out[old] = legacy_wire(value[native])
    return out


def native_writeback(before, wire):
    """Bring only original-owned changes back, removing transient wire aliases."""
    if isinstance(wire,list):
        originals = before if isinstance(before,list) else []
        return [native_writeback(originals[i] if i<len(originals) else {},v) for i,v in enumerate(wire)]
    if not isinstance(wire,dict): return wire
    original = before if isinstance(before,dict) else {}
    out = {k:native_writeback(original.get(k),v) for k,v in wire.items()
           if k not in FIELDS.values() and k != '_native_wire'}
    for native,old in FIELDS.items():
        if old in wire: out[native] = native_writeback(original.get(native), wire[old])
    return out


class InputGuard:
    def __init__(self): self.files = {}
    def add(self,path):
        path = Path(path).resolve()
        if not path.is_file(): raise MigrationError('Missing native verification input: '+str(path))
        value = sha(path)
        if path in self.files and self.files[path] != value:
            raise MigrationError('Input changed during native projection: '+str(path))
        self.files[path] = value
        return value
    def verify(self):
        for path,digest in self.files.items():
            if not path.is_file() or sha(path) != digest:
                raise MigrationError('Canonical input changed during native projection: '+str(path))


@contextmanager
def wire_copy(canonical, project=None, *, allow_blackbox_refresh=False):
    path = Path(canonical).resolve(); guard = InputGuard(); digest = guard.add(path)
    value = read_json(path)
    _source_current(value, Path(project or path.parent.parent).resolve(),allow_blackbox_refresh=allow_blackbox_refresh)
    with tempfile.TemporaryDirectory(prefix='hmigbot-ios-wire-') as directory:
        root = Path(directory); target = root/path.name
        wire = legacy_wire(value)
        wire['_native_wire'] = {'source_platform':'ios','canonical_path':str(path),'canonical_sha256':digest}
        write_json(target,wire)
        manifest = {'canonical_path':str(path),'canonical_sha256':digest,'wire_sha256':sha(target)}
        guard.verify()
        yield target,manifest,guard
        guard.verify()


def verify_projection(canonical, wire, manifest):
    if sha(canonical) != manifest['canonical_sha256'] or sha(wire) != manifest['wire_sha256']:
        raise MigrationError('Native wire/canonical hash mismatch')
    value = read_json(wire)
    if value.get('_native_wire',{}).get('canonical_sha256') != manifest['canonical_sha256']:
        raise MigrationError('Native wire provenance mismatch')


def _core(command,argv,scripts,*,cwd=None,env=None):
    from .compiled_runtime import execute
    return execute(command,list(map(str,argv)),scripts,cwd=cwd,env=env,capture_output=True,text=True)


def _emit(process, normalizer=lambda s:s):
    import sys
    try:
        stdout=normalizer(process.stdout) if process.stdout else ''
        stderr=normalizer(process.stderr) if process.stderr else ''
    except MigrationError as exc:
        if not process.returncode:raise
        print('[adapter_normalization_error] '+str(exc)+'; raw backend output follows',file=sys.stderr)
        stdout,stderr=process.stdout,process.stderr
    if stdout:print(stdout,end='')
    if stderr:print(stderr,end='',file=sys.stderr)
    return process.returncode


def _option(argv,name,default=None):
    for i,argument in enumerate(argv):
        if argument == name:
            if i+1 >= len(argv): raise MigrationError('Missing value for '+name)
            return argv[i+1]
        if argument.startswith(name+'='): return argument.split('=',1)[1]
    return default


def _replace(argv,name,value):
    result=[]; skip=False
    for item in argv:
        if skip: skip=False; continue
        if item == name: skip=True; continue
        if item.startswith(name+'='): continue
        result.append(item)
    return [*result,name,str(value)]


def _png_size(path):
    with Path(path).open('rb') as stream: header=stream.read(24)
    if len(header)!=24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise MigrationError('Native baseline is not a PNG: '+str(path))
    w,h=struct.unpack('>II',header[16:24])
    if w<=0 or h<=0: raise MigrationError('Invalid native PNG dimensions')
    return w,h


def capture_pair(meta):
    """Validate all three pieces of one actually arrived capture before placing."""
    if not isinstance(meta,dict) or meta.get('status') != 'ok' or meta.get('source_platform') != 'ios':
        raise MigrationError('Native capture metadata is absent or unsuccessful')
    paths={key:Path(meta[field]).resolve() for key,field in
           (('png','shot_path'),('xml','dump_path'),('native_json','native_json')) if meta.get(field)}
    if len(paths)!=3: raise MigrationError('Native baseline needs PNG, iOS XML and original snapshot')
    digests=meta.get('sha256',{})
    for name,path in paths.items():
        if not path.is_file() or digests.get(name)!=sha(path):
            raise MigrationError('Native capture is missing, stale or unpaired: '+name)
    for name,field in (('png','raw_png'),('xml','raw_xml')):
        if meta.get(field):
            raw=Path(meta[field])
            if not raw.is_file() or sha(raw)!=meta.get('raw_sha256',{}).get(name):
                raise MigrationError('Immutable native capture original changed: '+name)
    xml=ET.fromstring(paths['xml'].read_bytes()); native=read_json(paths['native_json'])
    if xml.get('platform')!='ios' or native.get('platform')!='ios':
        raise MigrationError('Native capture platform mismatch')
    request=native.get('request_id')
    if not request or xml.get('request_id')!=request or xml.get('native_snapshot_sha256')!=digests['native_json']:
        raise MigrationError('Native XML/snapshot capture ID or hash mismatch')
    for name,key in (('capture_started_at','started_at'),('capture_finished_at','finished_at')):
        stamp=native.get(key)
        if (type(stamp) not in {str,int,float} or not stamp or
                (isinstance(stamp,float) and not math.isfinite(stamp)) or xml.get(name)!=str(stamp)):
            raise MigrationError('Native snapshot/XML timestamp mismatch')
    arrival=meta.get('arrival',{})
    if arrival.get('arrived') is not True or arrival.get('request_id')!=request:
        raise MigrationError('Native capture arrival was not independently established')
    _png_size(paths['png'])
    return paths,xml,native


def _immutable_capture(meta):
    if not isinstance(meta,dict):return meta
    meta=copy.deepcopy(meta)
    if meta.get('raw_png') and meta.get('raw_xml') and meta.get('raw_sha256'):
        if meta.get('sha256',{}).get('native_json')!=meta['raw_sha256'].get('native_json'):
            raise BindingError('Native immutable snapshot digest disagrees with capture metadata',22)
        meta.update(shot_path=meta['raw_png'],dump_path=meta['raw_xml'],sha256=copy.deepcopy(meta['raw_sha256']))
    return meta


def _historical_capture_binding(meta, tree, source_app, guard):
    """Revalidate an archived trip observation, never relabel a newer capture."""
    from .native_source_build import app_build_identity
    from .native_visual import identities_from_tree, arrival
    if not source_app:
        raise MigrationError('Historical trip placement needs --source-app from the current source build')
    current=app_build_identity(source_app);recorded=meta.get('source_app_build')
    expected=tree.get('native_context',{}).get('source_sha256')
    if (not isinstance(recorded,dict) or not current.get('build_record_binding') or
            current!=recorded or not expected or current.get('source_sha256')!=expected):
        raise MigrationError('Historical capture Source/build differs from the current source app')
    app=Path(current['app']);guard.add(app/'Info.plist')
    import plistlib
    info=plistlib.loads((app/'Info.plist').read_bytes())
    guard.add(app/info['CFBundleExecutable']);guard.add(Path(current['build_record']))
    for key,field in (('png','shot_path'),('xml','dump_path')):
        if sha(Path(meta[field]))!=meta.get('raw_sha256',{}).get(key):
            raise MigrationError('Archived trip copy differs from its immutable raw '+key)
    native=read_json(Path(meta['native_json']));identities=identities_from_tree(tree)
    page=meta.get('page_id');contract=identities.get(page,{})
    if not contract.get('required') or contract.get('scope','app')!=native.get('scope','app'):
        raise MigrationError('Historical capture has no matching current page identity/scope')
    live={}
    for check in meta.get('arrival',{}).get('checks',[]):
        old=check.get('live_queries');current_contract=identities.get(check.get('page'),{})
        if old is None:continue
        exact=all([r.get('selector') for r in old.get(group,[])]==current_contract.get(group,[])
                  for group in ('required','excluded'))
        if exact:live[check['page']]=old
        elif check.get('page')==page:
            raise MigrationError('Historical capture page identity selectors changed')
    if page not in live or not arrival(native,page,identities,live)['arrived']:
        raise MigrationError('Historical capture does not establish the current source page identity')


def place_baselines(tree_path, edgewalk, project, trip, *, no_resize=False, dry_run=False, reason_overrides=None, source_app=None):
    """Original frozen-baseline lifecycle, with three-way native evidence pairing."""
    tree_path=Path(tree_path).resolve(); edgewalk=Path(edgewalk).resolve(); project=Path(project).resolve()
    trip=_safe_name(trip,'trip'); tree=read_json(tree_path); _source_current(tree,project)
    ledger=read_json(edgewalk/'ledger.json'); plan=read_json(edgewalk/'walk_plan.json')
    by_id={p['id']:p for p in page_records(tree)}
    if len(by_id)!=sum(1 for _ in page_records(tree)): raise MigrationError('Duplicate page IDs in native tree')
    assignment_path=project/'spec/visual-verify/_trip_assignment.json'
    assignment=read_json(assignment_path) if assignment_path.is_file() else None
    planned_trips={}
    for walk in plan.get('walks',[]):
        if walk.get('trip_id'):
            for name in walk.get('settles',[]): planned_trips.setdefault(name,set()).add(walk['trip_id'])
    output=project/'spec/visual-verify/screenshots/ios'/trip
    result={'trip':trip,'placed':[],'skipped_exist':[],'skipped_other_trip':[],
            'blocked_created':[],'unreached':[],'source_platform':'ios'}
    candidates=[]; historical_names=set();guard=InputGuard();guard.add(tree_path);guard.add(edgewalk/'ledger.json');guard.add(edgewalk/'walk_plan.json')
    if assignment_path.is_file():guard.add(assignment_path)
    for name in ledger.get('targets',[]):
        _safe_name(name)
        if name not in by_id: raise MigrationError('Walk target missing from native source tree: '+name)
        eligible=planned_trips.get(name,set())
        if eligible and trip not in eligible:
            result['skipped_other_trip'].append(name);continue
        if assignment:
            # Original assignment output supports page_to_trips and assignments.
            mapping=assignment.get('pages') or assignment.get('page_to_trips') or assignment.get('assignments') or {}
            value=mapping.get(name)
            if isinstance(value,dict):value=value.get('trips') or value.get('trip_ids')
            if isinstance(value,str):value=[value]
            if isinstance(value,list) and value and trip not in value:
                result['skipped_other_trip'].append(name);continue
        row=ledger.get('settled',{}).get(name)
        row_meta=(row or {}).get('capture_meta',{})
        row_trip=(row or {}).get('trip') or row_meta.get('trip') or row_meta.get('trip_id')
        historical=False
        if not row or row_trip and row_trip!=trip:
            saved=ledger.get('settled_by_trip',{}).get(trip,{}).get(name)
            if saved:
                row=saved;historical=True
                saved_meta=row.get('capture_meta',{})
                if (saved_meta.get('trip')!=trip or
                        row.get('trip') is not None and row['trip']!=trip or
                        saved_meta.get('trip_id') is not None and saved_meta['trip_id']!=trip):
                    raise MigrationError('Archived capture trip conflicts with its requested trip bucket')
        if not row:
            result['unreached'].append(name);continue
        meta=row.get('capture_meta',{});row_trip=row.get('trip') or meta.get('trip')
        if row_trip and row_trip!=trip:
            result['skipped_other_trip'].append(name);continue
        png,xml=output/(name+'.png'),output/(name+'.ios.xml')
        existing=by_id[name].get('screenshots',{}).get(trip)
        if png.exists() or xml.exists() or existing:
            if existing:_variant_baseline_current(tree,by_id[name],existing)
            result['skipped_exist'].append(name);continue
        paths,document,native=capture_pair(meta)
        if historical:
            _historical_capture_binding(meta,tree,source_app,guard)
            historical_names.add(name)
        if meta.get('page_id')!=name or meta['arrival'].get('expected_page')!=name:
            raise MigrationError('Captured page identity does not match walk target: '+name)
        if by_id[name].get('type')=='PageVariant' and by_id[name].get('source')=='blackbox_discovery':
            ref=_receipt_binding(tree)
            if not ref or meta.get('native_blackbox_source_inputs_sha256')!=ref['source_inputs_sha256']:
                raise BindingError('Native variant observation predates current classification inputs; recapture before placement',22)
        for path in paths.values():guard.add(path)
        if not row.get('via') and not meta.get('reach_path'):
            raise MigrationError('Native capture is missing its actual reach path: '+name)
        candidates.append((name,row,meta,paths,document,native))
    if dry_run:return result
    overrides=read_json(Path(reason_overrides)) if reason_overrides else {}
    if not isinstance(overrides,dict):raise MigrationError('Invalid original reason override mapping')
    edges=read_json(edgewalk/'edge_results.json') if (edgewalk/'edge_results.json').is_file() else []
    blocked=[]
    for name in result['unreached']:
        reason=overrides.get(name,'structurally_unreachable' if name in plan.get('orphans',[]) else 'nav_unreachable')
        if isinstance(reason,dict):reason=reason.get('reason')
        if not isinstance(reason,str) or '\n' in reason:raise MigrationError('Invalid BLOCKED reason override')
        notes=[str(e.get('note')) for e in edges if e.get('to')==name and e.get('status')!='confirmed' and e.get('note')]
        text='# BLOCKED baseline '+name+' ('+trip+')\nreason: '+reason+'\nsource: native edge-walk placement\n'
        text+='time: '+time.strftime('%Y-%m-%dT%H:%M:%S')+'\n\n归因素材：'+('；'.join(notes) or '边行走未到达，暂无归因素材')+'\n'
        text+='\n默认 nav_unreachable 仍为技术债；必须由原 baseline gate 判定，不因占位文件而算作真实截图。\n'
        blocked.append((project/'spec/fix/baseline-blocked'/('BLOCKED_baseline_'+name+'_'+trip+'.md'),text))
    guard.verify();output.mkdir(parents=True,exist_ok=True)
    staged=[]
    with tempfile.TemporaryDirectory(prefix='.native-place-',dir=output.parent) as temp:
        stage=Path(temp)
        for name,row,meta,paths,document,native in candidates:
            png=stage/(name+'.png');xml=stage/(name+'.ios.xml');shutil.copy2(paths['png'],png)
            before=_png_size(png);commands=[]
            if not no_resize and max(before)>1800:
                argv=['/usr/bin/sips','-Z','1800',str(png)]
                process=subprocess.run(argv,capture_output=True,text=True)
                commands.append({'argv':argv,'exit_code':process.returncode,'stdout':process.stdout,'stderr':process.stderr})
                if process.returncode:raise MigrationError('Official PNG resize failed: '+process.stderr.strip())
            after=_png_size(png);sx,sy=after[0]/before[0],after[1]/before[1]
            if (sx,sy)!=(1,1):
                if document.get('bounds_coordinate_space')!='screenshot_pixels':
                    raise MigrationError('Unknown native bounds coordinate space; cannot resize safely')
                for element in document.iter('node'):
                    box=re.fullmatch(r'\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]',element.get('bounds',''))
                    if not box:raise MigrationError('Invalid native pixel bounds')
                    x,y,right,bottom=map(int,box.groups());element.set('bounds','[%d,%d][%d,%d]'%(round(x*sx),round(y*sy),round(right*sx),round(bottom*sy)))
                for key,factor in (('pixel_per_point_x',sx),('pixel_per_point_y',sy)):
                    document.set(key,str(float(document.attrib[key])*factor))
            document.set('canonical_png_sha256',sha(png))
            document.set('source_capture_png_sha256',meta['sha256']['png'])
            document.set('canonical_resize_scale_x',str(sx));document.set('canonical_resize_scale_y',str(sy))
            atomic_write(xml,ET.tostring(document,encoding='utf-8',xml_declaration=True)+b'\n')
            canonical_png=output/png.name;canonical_xml=output/xml.name
            reach=meta.get('reach_path') or [row['via']]
            record={k:copy.deepcopy(v) for k,v in meta.items() if k not in {'sha256','shot_path','dump_path'}}
            record.update(shot_path=str(canonical_png),dump_path=str(canonical_xml),reach_path=reach,
                capture_id=native['request_id'],source_platform='ios',
                sha256={'png':sha(png),'xml':sha(xml),'native_json':sha(paths['native_json'])},
                raw_capture={'shot_path':str(meta.get('raw_png') or paths['png']),
                             'dump_path':str(meta.get('raw_xml') or paths['xml']),
                             'native_json':str(paths['native_json']),
                             'sha256':copy.deepcopy(meta.get('raw_sha256') or meta['sha256'])},
                canonical_transform={'raw_pixel_size':list(before),'canonical_pixel_size':list(after),
                                     'scale_x':sx,'scale_y':sy,'commands':commands})
            if by_id[name].get('type')=='PageVariant' and by_id[name].get('source')=='blackbox_discovery':
                record['native_blackbox_input_identity']=_receipt_binding(tree)
            staged.append((name,png,xml,canonical_png,canonical_xml,record))
        guard.verify()
        # Recheck freezing just before publication; never replace an old baseline.
        if any(p.exists() or x.exists() for _,_,_,p,x,_ in staged):
            raise MigrationError('Native baseline appeared during placement; frozen inputs not overwritten')
        published=[]
        try:
            for name,png,xml,target_png,target_xml,record in staged:
                os.link(png,target_png);published.append(target_png)
                os.link(xml,target_xml);published.append(target_xml)
                by_id[name].setdefault('screenshots',{})[trip]=record
                result['placed'].append(name)
                if name in historical_names:
                    result.setdefault('placement_sources',{})[name]='settled_by_trip'
            guard.verify()
            for path,text in blocked:
                atomic_write(path,text.encode());result['blocked_created'].append(path.stem)
            write_json(tree_path,tree)
        except BaseException:
            for path in published:path.unlink(missing_ok=True)
            raise
    return result


def place_baselines_cli(argv,scripts):
    parser=argparse.ArgumentParser(description='Native source placement; original frozen baseline lifecycle')
    parser.add_argument('--dir',default=os.environ.get('VV_EDGEWALK_DIR','spec/visual-verify/edgewalk'))
    parser.add_argument('--trip',required=True);parser.add_argument('--project-root',default='.')
    parser.add_argument('--tree',default='spec/toolkit-fact-tree.json');parser.add_argument('--reason-overrides')
    parser.add_argument('--no-resize',action='store_true')
    parser.add_argument('--source-app',help='Current verified source .app, required for archived-trip observations')
    args=parser.parse_args(argv)
    result=place_baselines(args.tree,args.dir,args.project_root,args.trip,no_resize=args.no_resize,reason_overrides=args.reason_overrides,source_app=args.source_app)
    print(json.dumps(result,ensure_ascii=False))
    # Like the original placement command, this reports dispositions; the
    # finalizer/readiness gates decide whether those dispositions are complete.
    return 0


def _baseline_record(tree,page,baseline):
    records=[p for p in page_records(tree) if p.get('id')==page]
    if len(records)!=1: raise BindingError('Baseline page is absent/ambiguous in current source tree: '+page,22)
    values=records[0].get('screenshots',{})
    for item in values.values():
        if isinstance(item,dict) and item.get('shot_path') and Path(item['shot_path']).resolve()==baseline/(page+'.png'):
            _variant_baseline_current(tree,records[0],item)
            return item
    capture=baseline/(page+'.capture.json')
    if capture.is_file():
        item=read_json(capture);_variant_baseline_current(tree,records[0],item);return item
    raise MigrationError('Native baseline lacks its paired capture provenance: '+page)


def _mirror_baseline(tree,baseline,destination,guard):
    baseline=Path(baseline).resolve();destination=Path(destination);destination.mkdir(parents=True)
    if not baseline.is_dir():raise MigrationError('Native baseline directory does not exist: '+str(baseline))
    mapping={}
    for png in sorted(baseline.glob('*.png')):
        page=png.stem
        if page.endswith('_long') or re.search(r'_seg_\d+$',page):continue
        _safe_name(page)
        xml=baseline/(page+'.ios.xml')
        # Never consult residual .android.xml, even if the native pair is missing.
        if not xml.is_file():raise MigrationError('Native source baseline is missing its .ios.xml: '+page)
        meta=_baseline_record(tree,page,baseline)
        paths,_,native=capture_pair(meta)
        if paths['png']!=png.resolve() or paths['xml']!=xml.resolve():
            raise MigrationError('Native baseline provenance points at a different image/dump: '+page)
        for path in paths.values():guard.add(path)
        image=destination/png.name;dump=destination/(page+'.xml')
        shutil.copy2(png,image);shutil.copy2(xml,dump)
        image.chmod(0o444);dump.chmod(0o444)
        mapping[page]={'canonical_png':str(png.resolve()),'canonical_xml':str(xml.resolve()),
                       'native_json':str(paths['native_json']),
                       'native_json_sha256':sha(paths['native_json']),
                       'canonical_png_sha256':sha(png),'canonical_xml_sha256':sha(xml),
                       'mirror_xml_sha256':sha(dump),'capture_id':native['request_id']}
    return mapping


def _verify_mirror(mapping,folder,guard):
    guard.verify()
    for page,row in mapping.items():
        if sha(Path(folder)/(page+'.xml'))!=row['mirror_xml_sha256']:
            raise MigrationError('Native baseline mirror hash mismatch: '+page)


def _walk_strings(value,convert):
    if isinstance(value,str):return convert(value)
    if isinstance(value,list):return [_walk_strings(x,convert) for x in value]
    if isinstance(value,dict):return {convert(str(k)):_walk_strings(v,convert) for k,v in value.items()}
    return value


def compile_replay_cli(argv,scripts):
    tree_path=Path(_option(argv,'--tree','spec/toolkit-fact-tree.json')).resolve()
    output_value=_option(argv,'--out')
    if not output_value:raise MigrationError('Missing --out for replay compiler')
    output=Path(output_value).resolve();tree=read_json(tree_path)
    if output==tree_path:raise MigrationError('Replay output must not overwrite its canonical input tree')
    baseline=_option(argv,'--baseline-dir')
    if not baseline:raise MigrationError('Missing native replay baseline directory')
    project=Path(_option(argv,'--project-root',tree_path.parent.parent)).resolve()
    _source_current(tree,project)
    with wire_copy(tree_path,project) as (wire,manifest,guard), tempfile.TemporaryDirectory(prefix='hmigbot-ios-replay-') as temp:
        work=Path(temp); projected=work/'baseline'; mapping=_mirror_baseline(tree,baseline,projected,guard)
        args=_replace(argv,'--tree',wire);args=_replace(args,'--baseline-dir',projected)
        # --project-root belongs to native integration, not the original compiler.
        if '--project-root' in args:
            idx=args.index('--project-root');args=args[:idx]+args[idx+2:]
        baseline2=_option(argv,'--baseline-dir2');mapping2={}
        if baseline2:
            mapping2=_mirror_baseline(tree,baseline2,work/'baseline2',guard)
            args=_replace(args,'--baseline-dir2',work/'baseline2')
        guard.add(Path(_option(argv,'--walk-plan')))
        for option in ('--annotations','--grounding','--edge-results','--hmos-profile'):
            value=_option(argv,option)
            if value:
                path=Path(value).resolve();guard.add(path)
                if option=='--grounding':
                    derived=work/'grounding.json';write_json(derived,legacy_wire(read_json(path)))
                    derived.chmod(0o444);args=_replace(args,option,derived)
        staged=work/'plan.json';args=_replace(args,'--out',staged)
        verify_projection(tree_path,wire,manifest);_verify_mirror(mapping,projected,guard)
        if mapping2:_verify_mirror(mapping2,work/'baseline2',guard)
        process=_core('compile_replay_plan',args,scripts)
        guard.verify();_verify_mirror(mapping,projected,guard)
        if mapping2:_verify_mirror(mapping2,work/'baseline2',guard)
        if process.returncode:return _emit(process)
        if not staged.is_file():raise MigrationError('Original replay compiler did not produce a fresh plan')
        result=read_json(staged)
        # Missing arrival anchors must remain an incomplete source-to-target plan.
        sentinels=result.get('node_sentinels',{})
        for step in result.get('steps',[]):
            target=step.get('to')
            if step.get('action') in {'tap','verify','coldstart'} and target in mapping:
                kind=step.get('expect',{}).get('kind')
                if kind not in {'none','toast','system_ui_expected'} and not (step.get('expect',{}).get('sentinel') or sentinels.get(target)):
                    raise MigrationError('Native replay arrival sentinel is missing: '+target)
        replacements={str(wire):str(tree_path),str(projected):str(Path(baseline).resolve()),str(staged):str(output)}
        if baseline2:replacements[str(work/'baseline2')]=str(Path(baseline2).resolve())
        def normalize(value):
            for old,new in sorted(replacements.items(),key=lambda x:-len(x[0])):value=value.replace(old,new)
            # Original .xml input names are internal only. Evidence names are canonical iOS.
            for page,row in {**mapping,**mapping2}.items():
                value=value.replace(str(Path(baseline).resolve()/(page+'.xml')),row['canonical_xml'])
                if baseline2:value=value.replace(str(Path(baseline2).resolve()/(page+'.xml')),row['canonical_xml'])
            if str(work) in value or str(wire.parent) in value:
                raise MigrationError('Temporary native replay path escaped into a published plan')
            return value
        result=_walk_strings(result,normalize)
        result['compiled_from_tree_hash']=manifest['canonical_sha256'][:len(result.get('compiled_from_tree_hash','')) or 16]
        result['native_input_provenance']={'source_platform':'ios','canonical_tree':str(tree_path),
            'canonical_tree_sha256':manifest['canonical_sha256'],'wire_sha256':manifest['wire_sha256'],
            'baseline':mapping,'baseline2':mapping2,
            'note':'Read-only bare-XML input projection; original compiler gates and denominator retained'}
        if tree.get('native_blackbox_input_identity'):
            result['native_input_provenance']['native_blackbox_input_identity']=copy.deepcopy(tree['native_blackbox_input_identity'])
        guard.verify();write_json(output,result)
        # Logs are normalized too; no temporary evidence path is presented as canonical.
        return _emit(process,lambda s:normalize(s))


class ProjectMirror:
    """Disposable original-layout view; authoritative project bytes never change.

    Positional gates with the upstream argv-dispatch defect receive a string
    whose individual characters are actual temporary file/trip aliases. The
    same original core runs, with its default layout and all original checks.
    Alias characters are chosen outside the complete input text so restoration
    is unambiguous. They are never published as source/device identities.
    """
    def __init__(self,project,*,round_number=None,short_trips=False,source_family='ios'):
        self.project=Path(project).resolve();self.round=round_number;self.short_trips=short_trips
        self.guard=InputGuard();self.temporary=None;self.restore={};self.trip_alias={};self.outputs=[]
        self.path_restore={}
        self.source_family=source_family;self.capture_entries={};self.plan_entries={}
    def _layout(self,relative):
        parts=list(relative.parts)
        if len(parts)>=4 and parts[:3]==['spec','visual-verify','screenshots']:
            if self.source_family=='ios' and parts[3]=='ios':parts[3]='android'
            if parts[3] in {'android','harmony','sbs'}:
                index=4 if parts[3]=='android' else 5
                if len(parts)>index:parts[index]=self.trip_alias.get(parts[index],parts[index])
        return self.root.joinpath(*parts)
    def __enter__(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='hmigbot-ios-canonical-')
        self.work=Path(self.temporary.name)
        files=[];text=[];directories=[]
        for directory,dirs,names in os.walk(self.project):
            base=Path(directory);dirs[:]=[d for d in dirs if d not in EXCLUDED]
            relative_dir=base.relative_to(self.project)
            if not (self.source_family=='ios' and relative_dir.parts[:4]==('spec','visual-verify','screenshots','android')):
                directories.append((base,relative_dir,base.stat()))
            for name in names:
                path=base/name;relative=path.relative_to(self.project)
                if name in EXCLUDED or path.is_symlink():continue
                if self.source_family=='ios' and relative.parts[:4]==('spec','visual-verify','screenshots','android'):continue
                if relative.parts[0]!='spec' and path.suffix not in {'.ets','.ts','.json','.json5','.yaml','.yml','.md'}:continue
                if relative.parts[0] not in {'spec','.migbot','entry','AppScope'} and path.suffix!='.ets':continue
                data=path.read_bytes();self.guard.add(path);files.append((path,relative,data))
                if path.suffix in {'.json','.json5','.yaml','.yml','.md','.ets','.ts'}:
                    try:text.append(data.decode('utf-8-sig'))
                    except UnicodeError:pass
        corpus='\n'.join(text)
        aliases=(chr(i) for i in range(0xE000,0xF8FF) if chr(i) not in corpus and chr(i) not in str(self.project))
        self.aliases=aliases
        self.root_alias=next(aliases);self.capture_alias=next(aliases);self.plan_alias=next(aliases)
        self.root=self.work/self.root_alias;self.root.mkdir()
        self.restore[self.root_alias]=str(self.project)
        baseline=self.project/('spec/visual-verify/screenshots/'+self.source_family)
        if baseline.is_dir():
            for trip in sorted(p.name for p in baseline.iterdir() if p.is_dir()):
                self.trip_alias[trip]=next(aliases) if self.short_trips else trip
        for actual,alias in self.trip_alias.items():
            if actual!=alias:self.restore[alias]=actual
        self.originals={};self.projected={}
        for path,relative,data in files:
            target=self._layout(relative);parts=target.relative_to(self.root).parts
            # Native originals remain evidence elsewhere; old baseline readers
            # see only copied PNG and explicit native XML content aliases.
            if path.suffix=='.xml' and str(path).endswith('.ios.xml') and 'screenshots' in parts:
                target=target.with_name(target.name[:-len('.ios.xml')]+'.android.xml')
            if path.suffix=='.json':
                try:value=json.loads(data.decode('utf-8-sig'))
                except (ValueError,UnicodeError) as exc:raise MigrationError('Unreadable canonical JSON in visual mirror: '+str(path)) from exc
                native=isinstance(value,dict) and ios_tree(value)
                source_root=value.get('native_source_root') if native else None
                if native:value=legacy_wire(value)
                if self.short_trips:value=_walk_strings(value,self.internalize)
                if source_root:value['native_source_root']=source_root
                if native or self.short_trips:data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
            elif path.suffix in {'.yaml','.yml','.md'} and self.short_trips:
                try:
                    value=data.decode('utf-8-sig')
                    for actual,alias in sorted(self.trip_alias.items(),key=lambda x:-len(x[0])):
                        value=re.sub(r'(?<![\w])'+re.escape(actual)+r'(?![\w])',lambda _:alias,value)
                    data=value.encode()
                except UnicodeError:pass
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);shutil.copystat(path,target)
            self.originals[target]=path;self.projected[target]=data
        if self.short_trips:self._rehash_derived_references()
        write_json(self.root/'.hmigbot-native-wire.json',{'source_platform':'ios','canonical_project':str(self.project)})
        # An empty, real round directory still supplies the upstream clock.
        # Preserve existing spec directories; do not invent absent rounds.
        for original,relative,stat in directories:
            if relative.parts and relative.parts[0]=='spec':self._layout(relative).mkdir(parents=True,exist_ok=True)
        # Original evidence_channel compares adhoc file mtimes with the round
        # directory's mtime. Restore timestamps after *all* internal writes,
        # including JSON rehash and marker creation. No touch/lock/log/seed may
        # alter the round tree before that original Phase6 step0 is evaluated.
        for file,original in self.originals.items():
            stat=original.stat();shutil.copystat(original,file)
            os.utime(file,ns=(stat.st_atime_ns,stat.st_mtime_ns));file.chmod(0o444)
        for original,relative,stat in sorted(directories,key=lambda row:-len(row[1].parts)):
            target=self._layout(relative)
            if target.is_dir():
                shutil.copystat(original,target)
                os.utime(target,ns=(stat.st_atime_ns,stat.st_mtime_ns))
                if target.stat().st_mtime_ns!=stat.st_mtime_ns:
                    raise MigrationError('Native mirror cannot preserve the original evidence clock at nanosecond precision')
        self.guard.verify()
        return self
    def __exit__(self,*args):
        try:self.guard.verify()
        finally:self.temporary.cleanup()
    def internalize(self,value):
        if value in self.trip_alias:return self.trip_alias[value]
        for actual,alias in self.trip_alias.items():
            value=value.replace('/'+actual+'/', '/'+alias+'/')
            if value.endswith('/'+actual):value=value[:-len(actual)]+alias
        # Keep paths to real source evidence readable. Only known project paths
        # are projected, never arbitrary system/source/device paths.
        if value.startswith(str(self.project)+'/'):
            return str(self.root)+value[len(str(self.project)):]
        return value
    def normalize(self,value):
        # Declared --out files live outside the project alias. Restore exact
        # paths, including quoted JSON/repr values, before alias restoration.
        declared=[]
        for path,actual in self.path_restore.items():
            for origin in {path,str(Path(path).resolve())}:
                declared.extend([(json.dumps(origin,ensure_ascii=True),json.dumps(actual,ensure_ascii=True)),
                                 (repr(origin),repr(actual)),(origin,actual)])
        for origin,actual in sorted(declared,key=lambda pair:-len(pair[0])):
            pattern=r'(?<![\w./\\-])'+re.escape(origin)+r'(?=$|[\s\x27\x22<>:,;)\]}])'
            value=re.sub(pattern,lambda _:actual,value)
        mappings=[]
        for alias,actual in self.restore.items():
            for origin in (str(self.work/alias),str((self.work/alias).resolve()),'../'+alias):
                mappings.extend([(origin,actual),
                    (json.dumps(origin,ensure_ascii=True)[1:-1],json.dumps(actual,ensure_ascii=True)[1:-1])])
        for origin,actual in sorted(mappings,key=lambda pair:-len(pair[0])):
            value=value.replace(origin,actual)
        for alias,actual in self.restore.items():
            value=value.replace(alias,actual)
            value=value.replace('\\u%04x'%ord(alias),actual)
        if str(self.work) in value:
            raise MigrationError('Temporary gate evidence path escaped native alias normalization')
        return value
    def _rehash_derived_references(self):
        """Only valid original hash references follow their derived copy.

        A stale/unknown source hash is never "fixed": it is deliberately left
        stale so the original freshness gate rejects it. Native provenance
        always retains the authoritative canonical hash.
        """
        originals={path:sha(source) for path,source in self.originals.items()}
        current=dict(originals)
        for _ in range(8):
            mapping={old:sha(path) for path,old in originals.items()}
            short={old[:16]:new[:16] for old,new in mapping.items()}
            changed=False
            for path,data in self.projected.items():
                if path.suffix!='.json':continue
                value=json.loads(data)
                def update(node,key=''):
                    if isinstance(node,list):return [update(x,key) for x in node]
                    if isinstance(node,dict):
                        return {k:(v if k in {'native_input_provenance','_native_wire'} else update(v,k)) for k,v in node.items()}
                    if isinstance(node,str) and any(x in key.lower() for x in ('sha','hash','digest')):
                        return mapping.get(node,short.get(node,node))
                    return node
                result=(json.dumps(update(value),ensure_ascii=False,indent=2)+'\n').encode()
                if path.read_bytes()!=result:path.write_bytes(result);changed=True
            if not changed:return
        raise MigrationError('Cyclic/unsupported metadata hash references in native gate projection')
    def add_capture(self,directory):
        source=Path(directory).resolve()
        if source in self.capture_entries:return self.capture_entries[source]
        alias=self.capture_alias if not self.capture_entries else next(self.aliases)
        self.capture_entries[source]=alias;target=self.work/alias
        if not source.is_dir():raise MigrationError('Target replay output directory does not exist')
        self.restore[alias]=str(source)
        for directory,dirs,names in os.walk(source):
            base=Path(directory);dirs[:]=[d for d in dirs if d not in EXCLUDED]
            for name in names:
                path=base/name
                if path.is_symlink():raise MigrationError('Replay input contains a symlink')
                self.guard.add(path);dest=target/path.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True)
                if path.suffix=='.json' and self.short_trips:
                    value=_walk_strings(read_json(path),self.internalize);write_json(dest,value)
                else:shutil.copy2(path,dest)
                dest.chmod(0o444)
        return alias
    def add_plan(self,path):
        path=Path(path).resolve();self.guard.add(path)
        if path in self.plan_entries:return self.plan_entries[path]
        alias=self.plan_alias if not self.plan_entries else next(self.aliases)
        self.plan_entries[path]=alias
        target=self.work/alias;write_json(target,_walk_strings(read_json(path),self.internalize));target.chmod(0o444)
        self.restore[alias]=str(path)
        return alias
    def verify(self):self.guard.verify()
    def release_output(self,path):
        """After all input checks, release only an explicitly owned output."""
        path=Path(path).resolve()
        for item in list(self.guard.files):
            if item==path or item.is_relative_to(path):self.guard.files.pop(item)


def target_gate_cli(command,argv,scripts):
    """Run the unchanged original gate core through its positional argv ABI."""
    if command=='assert_evidence_channel':
        if len(argv)!=2:raise MigrationError('Usage: evidence gate root round')
        project,round_value=argv;trip=None;capture=None;plan=None
    elif command=='assert_round_complete':
        if len(argv)!=2 or any(x.startswith('-') for x in argv):
            raise MigrationError('Original round gate argv ABI supports native root/round only; optional path flags require canonical default layout')
        project,round_value=argv;trip=None;capture=None;plan=None
    elif command=='assert_replay_artifacts':
        if len(argv)!=5:raise MigrationError('Usage: root round trip capture_dir plan.json')
        project,round_value,trip,capture,plan=argv
    elif command=='assert_gap_ticket_coverage':
        if len(argv)!=4:raise MigrationError('Usage: root round trip replay_out_dir')
        project,round_value,trip,capture=argv;plan=None
    else:raise MigrationError('Unsupported original target gate')
    if not round_value.isdigit() or len(round_value)!=1:
        raise MigrationError('Original positional gate ABI cannot encode this round; no verdict produced')
    root=Path(project).resolve();tree_path=root/'spec/toolkit-fact-tree.json'
    native=tree_path.is_file() and ios_tree(read_json(tree_path))
    if native:_source_current(read_json(tree_path),root)
    family='ios' if native or (root/'spec/visual-verify/screenshots/ios').is_dir() else 'android'
    with ProjectMirror(root,round_number=int(round_value),short_trips=True,source_family=family) as mirror:
        if trip and trip not in mirror.trip_alias:
            raise MigrationError('No canonical iOS baseline for this target verification trip')
        args='x'+mirror.root_alias+round_value
        if trip:args+=mirror.trip_alias[trip]
        if capture:args+=mirror.add_capture(capture)
        if plan:args+=mirror.add_plan(plan)
        state=mirror.root/f'spec/fix/round-{round_value}/_run_state.json'
        pure_check=command in {'assert_evidence_channel','assert_replay_artifacts','assert_gap_ticket_coverage'}
        previous_state_sha=sha(state) if pure_check and state.is_file() else None
        if not pure_check:state.unlink(missing_ok=True)
        mirror.verify();process=_core(command,[args],scripts,cwd=mirror.work);mirror.verify()
        # These original cores are read-only. Retain their actual input and do
        # not republish unchanged state: either action changes the upstream
        # round start/close mtime window and corrupts a repeated evidence check.
        if state.is_file() and sha(state)!=previous_state_sha:
            result=_walk_strings(read_json(state),mirror.normalize)
            result.setdefault('native_input_provenance',{}).update(source_platform='ios',
                adapter='original-positional-core-alias',canonical_project=str(root),
                note='Original gate verdict, denominator and failures retained; temporary legacy layout restored')
            output=root/f'spec/fix/round-{round_value}/_run_state.json'
            mirror.release_output(output);write_json(output,result)
        return _emit(process,mirror.normalize)


def _project_for(argv):
    explicit=_option(argv,'--project-root') or _option(argv,'--root') or _option(argv,'--hmos-project')
    if explicit:return Path(explicit).resolve()
    if argv and not argv[0].startswith('-') and Path(argv[0]).is_dir():
        candidate=Path(argv[0]).resolve()
        if (candidate/'spec').is_dir() or (candidate/'.migbot/config.json').is_file():return candidate
    tree=_option(argv,'--tree') or _option(argv,'--fact-tree') or _option(argv,'--factree')
    if not tree:
        tree=next((x for x in argv if not x.startswith('-') and x.endswith('.json') and Path(x).is_file()),None)
    if tree:
        path=Path(tree).resolve()
        if path.parent.name=='spec':return path.parent.parent
        for parent in path.parents:
            if (parent/'spec/toolkit-fact-tree.json').is_file():return parent
    return Path.cwd()


def _active_mirror():
    value=os.environ.get('HMIGBOT_NATIVE_MIRROR')
    if not value:return None
    path=Path(value).resolve();marker=path/'.hmigbot-native-wire.json'
    if not marker.is_file():raise MigrationError('Native mirror environment lacks its owned input marker')
    data=read_json(marker)
    if data.get('source_platform')!='ios' or data.get('canonical_project')!=os.environ.get('HMIGBOT_NATIVE_CANONICAL_PROJECT'):
        raise MigrationError('Native mirror/project context mismatch')
    return path


def _validate_project_baselines(project):
    path=project/'spec/toolkit-fact-tree.json'
    if not path.is_file():raise MigrationError('Native visual source tree is missing')
    tree=read_json(path);_source_current(tree,project)
    root=project/'spec/visual-verify/screenshots/ios'
    if root.is_dir():
        for folder in root.iterdir():
            if not folder.is_dir():continue
            for image in folder.glob('*.png'):
                if image.stem.endswith('_long') or re.search(r'_seg_\d+$',image.stem):continue
                capture_pair(_baseline_record(tree,image.stem,folder.resolve()))
    return tree


def _data_arguments(command,argv,project,mirror):
    """Project only declared path arguments of the retained data commands."""
    path_options={'--tree','--fact-tree','--factree','--root','--project-root','--hmos-project',
                  '--capture-dir','--baseline-dir','--baseline-dir2','--android-baseline-dir',
                  '--ios-baseline-dir','--plan','--batches','--annotations','--grounding','--edge-results','--dir'}
    scalar_options={'phase2_needs':{'--trip','--page'},'build_batches':{'--batch-size'},
                    'build_judge_input':{'--round','--trip','--prev-round','--skip-pages'},
                    'replay_place_artifacts':{'--round','--trip','--only-pages'}}
    positional_paths={'phase2_needs':{0}}
    args=[];outputs=[];i=0;position=0;options=True
    while i<len(argv):
        item=argv[i]
        if item=='--' and options:
            args.append(item);options=False;i+=1;continue
        key,separator,value=item.partition('=') if options else (item,'','')
        if options and key in path_options|{'--out'}:
            if not separator:
                if i+1==len(argv):args.append(item);i+=1;continue
                value=argv[i+1];i+=1
            actual=Path(value).resolve()
            name='--android-baseline-dir' if key=='--ios-baseline-dir' else key
            if key=='--out':
                dest=mirror.work/'requested-output.json';outputs.append((dest,actual))
                mirror.path_restore[str(dest)]=value
            elif actual==project:dest=mirror.root
            elif actual.is_relative_to(project):
                relative=actual.relative_to(project)
                if relative.parts[:4]==('spec','visual-verify','screenshots','ios'):
                    relative=Path('spec/visual-verify/screenshots/android',*relative.parts[4:])
                dest=mirror.root/relative
            elif key=='--capture-dir':dest=mirror.work/mirror.add_capture(actual)
            else:dest=actual
            args.extend([name,str(dest)]);i+=1;continue
        if options and key in scalar_options.get(command,set()) and not separator:
            args.append(item)
            if i+1<len(argv):args.append(argv[i+1]);i+=1
            i+=1;continue
        if not options or not item.startswith('-'):
            if position in positional_paths.get(command,set()):
                path=Path(item).resolve()
                if path.is_relative_to(project):item=str(mirror.root/path.relative_to(project))
            position+=1
        args.append(item);i+=1
    return args,outputs


def data_cli(command,argv,scripts,*,project_override=None):
    """Adapt source data paths/fields; execute the original data/check algorithm."""
    active=_active_mirror()
    if active:
        args=['x'] if command in {'check_android_screenshot','check_blackbox_evidence'} else argv
        return _emit(_core(command,args,scripts,cwd=active))
    project=Path(project_override).resolve() if project_override else _project_for(argv)
    tree_path=project/'spec/toolkit-fact-tree.json'
    if command in {'check_android_screenshot','build_batches','phase2_needs'}:
        _validate_project_baselines(project)
    elif tree_path.is_file():_source_current(read_json(tree_path),project)
    with ProjectMirror(project) as mirror:
        args,outputs=_data_arguments(command,argv,project,mirror)
        if command in {'check_android_screenshot','check_blackbox_evidence'}:args=['x']
        debt=mirror.root/'spec/visual-verify/_baseline_debt.json'
        # Both known writers recompute this owned derivative. Consumers keep
        # their copied debt input; the canonical file remains guarded.
        if command in {'check_android_screenshot','build_batches'}:debt.unlink(missing_ok=True)
        env={'HMIGBOT_NATIVE_MIRROR':str(mirror.root),'HMIGBOT_NATIVE_CANONICAL_PROJECT':str(project)}
        mirror.verify();process=_core(command,args,scripts,cwd=mirror.root,env=env);mirror.verify()
        if debt.is_file():
            destination=project/'spec/visual-verify/_baseline_debt.json'
            mirror.release_output(destination);write_json(destination,_walk_strings(read_json(debt),mirror.normalize))
        if process.returncode:return _emit(process,mirror.normalize)
        for staged,actual in outputs:
            if not staged.is_file():raise MigrationError('Original visual data command did not produce a fresh requested output')
            result=_walk_strings(read_json(staged),mirror.normalize)
            mirror.release_output(actual);write_json(actual,result)
        if command in {'replay_place_artifacts','build_judge_input'}:
            round_value=_option(argv,'--round');trip=_option(argv,'--trip')
            if not round_value or not trip:raise MigrationError('Target source-data bridge needs explicit round and trip')
            _safe_name(trip,'trip')
            if not round_value.isdigit():raise MigrationError('Invalid target round')
            bases=['sbs'] if command=='build_judge_input' else ['harmony','sbs']
            for family in bases:
                relative=Path(f'spec/visual-verify/screenshots/{family}/round-{round_value}')/trip
                staged=mirror.root/relative;actual=project/relative
                if not staged.is_dir():continue
                # Original placement owns this exact round/trip; its stale-file
                # clearing behavior is preserved rather than merging old shots.
                with tempfile.TemporaryDirectory(prefix='.native-publish-',dir=actual.parent if actual.parent.is_dir() else project) as temp:
                    prepared=Path(temp)/trip;shutil.copytree(staged,prepared)
                    for file in prepared.rglob('*.json'):
                        value=_walk_strings(read_json(file),mirror.normalize);write_json(file,value)
                    mirror.verify()
                    mirror.release_output(actual)
                    if actual.exists():shutil.rmtree(actual)
                    actual.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(prepared),actual)
            if command=='build_judge_input':
                capture=Path(_option(argv,'--capture-dir')).resolve()
                relative=capture.relative_to(project) if capture.is_relative_to(project) else None
                staged=mirror.root/relative if relative is not None else mirror.work/mirror.capture_alias
                for file in staged.glob('judge_input*.json'):
                    mirror.release_output(capture/file.name)
                    write_json(capture/file.name,_walk_strings(read_json(file),mirror.normalize))
            capture=Path(_option(argv,'--capture-dir')).resolve()
            proof=(project/f'spec/visual-verify/screenshots/harmony/round-{round_value}'/trip/'_placement.json'
                   if command=='replay_place_artifacts' else capture/f'judge_input_round{round_value}.json')
            mirror.release_output(proof)
            _record_target_provenance(command,project,int(round_value),trip,capture,proof)
        return _emit(process,mirror.normalize)


def _json_digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def _blackbox_present(tree):
    return 'native_blackbox_input_identity' in tree or any(
        (p.get('type')=='PageVariant' and p.get('source')=='blackbox_discovery') or p.get('blackbox_behavior')
        for p in page_records(tree))


def _blackbox_source(tree,project):
    from .source import Source
    info=tree.get('source',{});root=tree.get('native_source_root') or info.get('ios_root')
    if not root:
        config=Path(project)/'.migbot/config.json';cfg=read_json(config) if config.is_file() else {}
        ios=cfg.get('ios',{});root=ios.get('source_root') if isinstance(ios,dict) else None
    if not root:raise MigrationError('Native blackbox discoveries require the selected iOS source; regenerate source facts')
    root=Path(root);root=root if root.is_absolute() else Path(project)/root
    if not root.is_dir():raise MigrationError('Native blackbox source is unavailable: '+str(root))
    return Source(root,Path(project) if (Path(project)/'.migbot/config.json').is_file() else None)


def _blackbox_source_inputs(tree,project,*,source=None,facts=None):
    """Independent identity: default ROUTE source_sha is deliberately unchanged."""
    from .native_routes import analyze
    from .native_resources import selected
    source=source or _blackbox_source(tree,project);facts=facts or analyze(source)
    resources=selected(source,text_resources=True)
    package=Path(__file__).resolve().parents[1];toolkit=package.parent
    modules=['hmigbot_ios152/native_canonical.py','hmigbot_ios152/native_system_ui.py','hmigbot_ios152/native_semantics.py','hmigbot_ios152/native_routes.py',
        'hmigbot_ios152/native_resources.py','hmigbot_ios152/native_context.py','hmigbot_ios152/source.py',
        'hmigbot_ios/apple_tools.py','hmigbot_ios/project_scope.py','hmigbot_ios/conditional_source.py',
        'hmigbot_ios/swiftui.py','hmigbot_ios/core.py']
    code={name:sha(package/name) for name in modules}
    provider=toolkit/'providers/swift-syntax/main.swift'
    if not provider.is_file():raise MigrationError('Native classifier provider source is missing')
    code['providers/swift-syntax/main.swift']=sha(provider)
    return {'source_root':str(source.root),'route_source_sha256':facts['source_sha'],
        'source_code':{name:sha(source.root/name) for name in sorted(source.files)},
        'selection':source.selection,'context':facts['context'],'resource_scope':{k:v for k,v in resources.items() if k!='excluded'},
        'text_resources':{name:sha(source.root/name) for name in resources['files']},'classifier_code':code}


def _blackbox_manifest_inputs(directory,project):
    directory=Path(directory).resolve();values={};observations={};entries={};headers={}
    for file in sorted(directory.rglob('*__manifest.json')):
        values[file.relative_to(directory).as_posix()]=sha(file)
        value=read_json(file)
        name=file.relative_to(directory).as_posix()
        headers[name]=_json_digest({k:v for k,v in value.items() if k not in {'discoveries','behavior_ledger','blackbox_stats'}})
        for section in ('discoveries','behavior_ledger'):
            for number,row in enumerate(value.get(section,[])):
                if not isinstance(row,dict):raise BindingError('Malformed native blackbox collection row',22)
                key=name+':'+section+':'+str(row.get('id',row.get('key',number)))
                if key in entries:raise BindingError('Duplicate native collection entry identity',22)
                entries[key]=_json_digest(row)
        for row in value.get('discoveries',[]):
            if not isinstance(row,dict):continue
            for key in ('capture_meta','trigger_capture_meta'):
                meta=row.get(key)
                if not isinstance(meta,dict):continue
                fields=['native_json','raw_png' if meta.get('raw_png') else 'shot_path','raw_xml' if meta.get('raw_xml') else 'dump_path']
                for field in fields:
                    if meta.get(field):
                        path=Path(meta[field]).resolve();observations[str(path)]=sha(path) if path.is_file() else None
    pending_path=Path(project)/'spec/visual-verify/edgewalk/pending_bindings.json'
    pending=read_json(pending_path) if pending_path.is_file() else []
    if not isinstance(pending,list):raise BindingError('Malformed native pending binding collection',22)
    for number,row in enumerate(pending):
        if not isinstance(row,dict):raise BindingError('Malformed native pending binding row',22)
        key='pending:'+str(row.get('id',number))
        if key in entries:raise BindingError('Duplicate pending native collection identity',22)
        entries[key]=_json_digest(row)
    return {'directory':str(directory),'manifests':values,'observations':observations,'headers':headers,
            'entries':entries,'pending_sha256':sha(pending_path) if pending_path.is_file() else None}


def _variant_projection(tree):
    fields=('id','type','fq_class','label','purpose','uncertain','ios_file','harmony_target','parent_page',
            'parent_ability','via_trigger','blackbox_landing_signature','blackbox_screenshot','source',
            'components','navigation','reach_paths','navigation_contract')
    return {p['id']:{key:p.get(key) for key in fields} for p in page_records(tree)
            if p.get('type')=='PageVariant' and p.get('source')=='blackbox_discovery'}


def _verify_blackbox_receipt(tree,project,*,allow_manifest_collection=False):
    ref=tree.get('native_blackbox_input_identity')
    if not isinstance(ref,dict):raise BindingError('Native blackbox was materialized without its input receipt; re-materialize from current source',22)
    path=(Path(project)/str(ref.get('receipt',''))).resolve()
    if not path.is_relative_to(Path(project).resolve()) or not path.is_file() or sha(path)!=ref.get('sha256'):
        raise BindingError('Native blackbox classification receipt is missing or changed',22)
    receipt=read_json(path)
    if receipt.get('schema')!='native-blackbox-inputs.v1':raise BindingError('Incompatible native blackbox receipt; re-materialize',22)
    source_inputs=_blackbox_source_inputs(tree,project);digest=_json_digest(source_inputs)
    if digest!=receipt['inputs'].get('source_inputs_sha256') or digest!=ref.get('source_inputs_sha256'):
        raise BindingError('Native blackbox source/resources/classifier changed; re-materialize after the original source guard',22)
    from .native_semantics import verify_binding
    for row in receipt.get('outputs',{}).get('classifications',[]):
        for proof in row.get('evidence',[]):
            if proof.get('kind')=='Apple real Source typecheck and AST binding':
                try:verify_binding(proof)
                except (MigrationError,KeyError,TypeError,ValueError,OSError) as exc:
                    raise BindingError('Native system-presentation binding is stale; re-materialize: '+str(exc),22) from exc
    projection=_variant_projection(tree);variant_hash=_json_digest(projection);set_hash=_json_digest(sorted(projection))
    if variant_hash!=receipt['outputs'].get('variant_records_sha256') or set_hash!=ref.get('variant_set_sha256'):
        raise BindingError('Native blackbox variant output no longer matches its classification receipt',22)
    old=receipt['inputs']['discovery'];current=_blackbox_manifest_inputs(old['directory'],project)
    if allow_manifest_collection:
        for group in ('entries','headers','observations'):
            if any(current[group].get(key)!=value for key,value in old[group].items()):
                raise BindingError('Collector cannot edit/delete previously materialized native discovery evidence',22)
        receipt=copy.deepcopy(receipt);receipt['_collection_pending']=current!=old
    elif current!=old:
        raise BindingError('Native blackbox discoveries/observations changed; materialize the complete current ledger before consuming variants',22)
    return receipt


def _receipt_binding(tree):
    ref=tree.get('native_blackbox_input_identity')
    return {key:ref.get(key) for key in ('sha256','source_inputs_sha256','variant_set_sha256')} if isinstance(ref,dict) else None


def _variant_baseline_current(tree,page,record):
    if page.get('type')!='PageVariant' or page.get('source')!='blackbox_discovery':return
    expected=_receipt_binding(tree);actual=record.get('native_blackbox_input_identity')
    if not expected or not isinstance(actual,dict) or any(actual.get(k)!=expected[k] for k in ('source_inputs_sha256','variant_set_sha256')):
        raise BindingError('Frozen native variant baseline references an earlier classification; restart from the affected source baseline',22)


def _publish_blackbox_receipt(path,tree,project,source_inputs,directory,rows,previous_sha):
    projection=_variant_projection(tree)
    receipt={'schema':'native-blackbox-inputs.v1','inputs':{'source':source_inputs,
        'source_inputs_sha256':_json_digest(source_inputs),'discovery':_blackbox_manifest_inputs(directory,project)},
        'outputs':{'classifications':rows,'variant_records_sha256':_json_digest(projection),
                   'variant_set_sha256':_json_digest(sorted(projection))},'previous_receipt_sha256':previous_sha}
    raw=(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode();digest=hashlib.sha256(raw).hexdigest()
    relative=Path('spec/visual-verify/edgewalk/native-blackbox-receipts')/(digest+'.json');target=Path(project)/relative
    if target.exists():
        if sha(target)!=digest:raise BindingError('Immutable native receipt path has conflicting bytes',22)
    else:atomic_write(target,raw)
    tree['native_blackbox_input_identity']={'schema':'native-blackbox-inputs.v1','receipt':str(relative),
        'sha256':digest,'source_inputs_sha256':receipt['inputs']['source_inputs_sha256'],
        'variant_set_sha256':receipt['outputs']['variant_set_sha256']}
    for page in page_records(tree):
        if page.get('type')=='PageVariant' and page.get('source')=='blackbox_discovery':page['native_blackbox_receipt_sha256']=digest
    # Immutable receipt is committed first; atomic tree-pointer replacement is
    # the pair's commit. Failure leaves the previous pair recoverable.
    write_json(path,tree)
    return receipt


class NativeTriggerIndex:
    """Native source-consumer replacement for the original Android grep.

    Swift values come from SwiftParser, never source-string grep.  Callable
    roots and selected resource membership retain their evidence.  This is a
    conservative declaration graph, not a Swift type checker: unresolved
    liveness/decoding is an LLM binding debt, never an inferred dynamic item.
    """
    def __init__(self,tree,project,guard):
        from .native_routes import analyze,SwiftFile
        from .native_resources import selected
        self.source=_blackbox_source(tree,project)
        self.facts=analyze(self.source);self.guard=guard;self.values=[];self.dynamic=[];self.issues=[]
        self.source_inputs=_blackbox_source_inputs(tree,project,source=self.source,facts=self.facts)
        self.source_inputs_sha256=_json_digest(self.source_inputs)
        methods=[m for m in self.facts['methods'].values() if not m['name'].startswith('<')]
        symbols={p.get('fq_class') or p.get('id') for p in page_records(tree)}
        declared={p['name'] for p in self.facts.get('pages',[])}
        roots={s for s in declared if s in symbols or any(str(x).endswith('.'+s) or s.endswith('.'+str(x)) for x in symbols if x)}
        # The native fact producer may not yet have enriched every statically
        # declared view. The original source search was application-wide.
        roots.update(declared)
        live={m['key'] for m in methods if m['owner'] in roots and m['name'] in {
            'body','init','loadView','viewDidLoad','viewWillAppear','viewDidAppear','makeUIView','updateUIView',
            'makeUIViewController','updateUIViewController','getTimeline','getSnapshot','placeholder'}}
        files={name:SwiftFile(self.source,name) for name in sorted(self.source.files) if name.endswith('.swift')}
        self.swift_files=files;self.live_calls={}
        # Stored values are followed only when referenced by a live render or
        # handler declaration. Uncalled helpers and unused declarations do not
        # turn a discovery static merely because they contain its text.
        for name,f in files.items():
            guard.add(self.source.root/name)
            for node in f.nodes:
                if node['kind']!='variable':continue
                for binding in node['value']['bindings']:
                    if not binding.get('initializer_span'):continue
                    span=f.span(binding['initializer_span']);key=f.owner(node)+'.'+binding['pattern']+'@'+name+':'+str(span['start'])
                    methods.append({'key':key,'name':binding['pattern'],'owner':f.owner(node),'body_span':span,**span})
        dead={}
        for name,f in files.items():
            # Exact constant branches, using official tokens/spans. Exclude
            # calls here too, so an if-false helper cannot make dead text live.
            dead[name]=[]
            for i,t in enumerate(f.tokens):
                if t.value!='if' or i+2>=len(f.tokens):continue
                condition,brace=f.tokens[i+1:i+3]
                if condition.value not in {'false','true'} or brace.value!='{' or i+2 not in f.brackets:continue
                end=f.brackets[i+2]
                if condition.value=='false':dead[name].append((brace.start,f.tokens[end].end))
                elif end+2<len(f.tokens) and f.tokens[end+1].value=='else' and f.tokens[end+2].value=='{' and end+2 in f.brackets:
                    dead[name].append((f.tokens[end+2].start,f.tokens[f.brackets[end+2]].end))
        changed=True
        while changed:
            changed=False
            for m in methods:
                if m['key'] not in live:continue
                f=files.get(m['file'])
                if not f:continue
                identifiers={t.value for t in f.toks(m['body_span']) if t.kind not in {'string','regex'}
                             and not any(a<=t.start and t.end<=b for a,b in dead[m['file']])}
                for child in methods:
                    if child['owner']==m['owner'] and child['name'] in identifiers and child['key'] not in live:
                        live.add(child['key']);changed=True
        self.live=[]
        for name,f in files.items():
            def is_live(start,end):
                if any(a<=start and end<=b for a,b in dead[name]):return False
                containers=[m for m in methods if m['file']==name and m['body_span']['start']<=start and end<=m['body_span']['end']]
                if not containers:return False
                closest=min(containers,key=lambda m:m['body_span']['end']-m['body_span']['start'])
                return closest['key'] in live
            self.live_calls[name]=[call for call in f.calls if is_live(call['start'],call['end'])]
            for t in f.tokens:
                if t.kind!='string' or not is_live(t.start,t.end):continue
                evidence={'kind':'SwiftParser represented literal','file':name,'line':t.line,'start':t.start,'end':t.end,'sha256':sha(self.source.root/name)}
                if getattr(t,'literal_is_static',False):self.values.append((t.literal_value,evidence))
            for control in self.facts.get('controls',[]):
                if control.get('file')!=name or not is_live(control['start'],control['end']):continue
                self.live.append(control)
                expr=control.get('text_expression')
                expressions=[]
                for call in f.calls:
                    if call['start']!=control['start'] or call['end']!=control['end']:continue
                    expressions.extend(f.toks(f.span(arg['span'])) for arg in call['value']['arguments'] if arg.get('expression')==expr)
                runtime=any(any((t.kind=='string' and not getattr(t,'literal_is_static',False) and re.search(r'\\#*\(',t.value))
                                   or (t.kind=='identifier' and t.value not in {'true','false','nil'}) for t in tokens) for tokens in expressions)
                if expr and control.get('text') is None and runtime:
                    # A nonliteral control expression is positive runtime-data
                    # evidence only when the discovery is bound to that exact
                    # source control, not when a source search just missed.
                    self.dynamic.append(control)
        resources=selected(self.source,text_resources=True)
        self.resource_scope=resources
        self.issues.extend(resources.get('issues',[]))
        self.live.extend(c for c in self.facts.get('controls',[]) if c.get('file') in resources['files'])
        def strings(value):
            if isinstance(value,str):yield value
            elif isinstance(value,dict):
                for key,item in value.items():yield str(key);yield from strings(item)
            elif isinstance(value,list):
                for item in value:yield from strings(item)
        for name in resources['files']:
            path=self.source.root/name;guard.add(path)
            evidence={'kind':'selected native resource text','file':name,'sha256':sha(path),
                      'scope':resources['scope'],'membership_evidence':resources['evidence']}
            try:
                suffix=path.suffix.lower()
                if suffix in {'.strings','.stringsdict','.plist'}:
                    process=subprocess.run(['/usr/bin/plutil','-convert','json','-o','-',str(path)],capture_output=True,text=True)
                    if process.returncode:raise ValueError(process.stderr or process.stdout)
                    values=list(strings(json.loads(process.stdout)))
                elif suffix in {'.json','.xcstrings'}:values=list(strings(read_json(path)))
                elif suffix in {'.xib','.storyboard','.xml','.svg'}:
                    document=ET.fromstring(path.read_bytes());values=[]
                    for item in document.iter():values.extend(item.attrib.values());values.extend([item.text or '',item.tail or ''])
                    # .id and arbitrary XML ids never become AX identifiers.
                else:
                    raw=path.read_bytes();values=[raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')]
                self.values.extend((v,evidence) for v in values if v)
            except (MigrationError,ValueError,UnicodeError,ET.ParseError) as exc:
                self.issues.append({'file':name,'reason':'resource_text_not_decoded','detail':str(exc)})

    def classify(self,discovery,parent=None,manifest=None):
        text=discovery.get('trigger_text') or '';identifier=discovery.get('trigger_native_identifier') or discovery.get('native_identifier') or ''
        if not isinstance(text,str) or not isinstance(identifier,str):raise MigrationError('Native trigger text/identifier must be strings')
        if discovery.get('trigger_resource_id'):
            raise MigrationError('Native discovery must retain a real accessibilityIdentifier separately; resource-id must be empty')
        observed=_immutable_capture(discovery.get('trigger_capture_meta'))
        if observed:
            if observed.get('native_blackbox_source_inputs_sha256')!=self.source_inputs_sha256:
                raise BindingError('Native trigger observation predates current classification inputs',22)
            paths,_,snapshot=capture_pair(observed)
            for path in paths.values():self.guard.add(path)
            nodes=[]
            def walk(node):
                if not isinstance(node,dict):return
                nodes.append(node)
                for child in node.get('children',[]):walk(child)
            walk(snapshot.get('tree'))
            matches=[n for n in nodes if identifier and n.get('identifier')==identifier and n.get('exists') is True]
            if not text and identifier and len(matches)==1:
                return {'classification':'static','evidence':[{'kind':'observed accessibilityIdentifier','identifier':identifier,
                    'native_json':str(paths['native_json']),'sha256':sha(paths['native_json']),'request_id':snapshot['request_id']}]}
        if parent is not None:
            from .native_system_ui import share_presentation
            presentation=share_presentation(self,parent,discovery,manifest)
            if presentation is not None:return presentation
        if not text and identifier:
            matches=[c for c in self.live if c.get('accessibility_identifier')==identifier]
            if matches:return {'classification':'static','evidence':[{'kind':'SwiftParser accessibilityIdentifier',**{k:c[k] for k in ('file','line','start','end')},'identifier':identifier} for c in matches]}
        if text:
            hits=[e for value,e in self.values if text in value]
            if hits:return {'classification':'static','evidence':hits}
            anchor=discovery.get('source_anchor') or {}
            if not isinstance(anchor,dict):raise MigrationError('Native discovery source_anchor must be an evidence object')
            for c in self.dynamic:
                bound=identifier and c.get('accessibility_identifier')==identifier
                bound=bound or (anchor.get('file')==c.get('file') and
                    (anchor.get('start')==c.get('start') or anchor.get('line')==c.get('line')))
                if bound:return {'classification':'dynamic','evidence':[{'kind':'bound runtime control text expression',
                    'expression':c['text_expression'],**{k:c[k] for k in ('file','line','start','end')}}]}
        return {'classification':'unknown','evidence':[],
                'reason':'No live decoded native static anchor or positively bound dynamic expression',
                'issues':self.issues}


def _native_variant(parent,discovery):
    """Measured 1.5.2 PageVariant projection; native identity stays native."""
    text=discovery.get('trigger_text') or '';identifier=discovery.get('trigger_native_identifier') or discovery.get('native_identifier') or ''
    landing=discovery.get('landing_ability')
    if not isinstance(landing,str) or not landing:raise MigrationError('Native discovery has no observed landing symbol')
    # Actual 1.5.2 core: preserve leading/trailing '_' and truncate at 40.
    slug=re.sub(r'[^\w\-]+','_',text or identifier)[:40] or 'anon'
    name=landing+'#via='+slug;_safe_name(name)
    uncertain=bool(discovery.get('uncertain',False))
    via={'text':text,'content_desc':discovery.get('trigger_content_desc') or '',
         'resource_id':'','native_identifier':identifier,'class':discovery.get('trigger_class') or '',
         'center':discovery.get('trigger_center')}
    page={'id':name,'type':'PageVariant','fq_class':landing,'label':landing+' ('+(text or identifier)+')',
          'purpose':"由 blackbox 发现：从 "+parent['id']+" 点击 '"+(text or identifier)+"' 进入",
          'uncertain':uncertain,'ios_file':None,'harmony_target':None,'parent_page':parent['id'],
          'parent_ability':landing,'via_trigger':via,'blackbox_landing_signature':discovery.get('landing_signature'),
          'blackbox_screenshot':discovery.get('screenshot'),'source':'blackbox_discovery','components':[],
          'navigation':{'inbound':[{'from':parent['id'],'trigger_text':text}],'outbound':[]},'reach_paths':[],
          'navigation_contract':{'relationship_kind':'blackbox_discovered','from_state':'parent_visible',
              'trigger_actions':[{'type':'click_by_text','label':text,'resource_id':'','native_identifier':identifier}],
              'verify_signal':{'text_contains':None},'contract_uncertain':uncertain,'generated_from':['blackbox_discovery']}}
    edge={'to':name,'trigger_kind':'click_by_text','trigger_text':text,'trigger_resource_id':'',
          'trigger_native_identifier':identifier,'source':'blackbox_discovery'}
    extra={'variant_id':name,'trigger_text':text,'trigger_resource_id':'','trigger_native_identifier':identifier,
           'landing_ability':landing,'landing_signature':discovery.get('landing_signature'),
           'screenshot':discovery.get('screenshot'),'source':'blackbox_discovery'}
    return page,edge,extra


def materialize_native_cli(argv,scripts):
    """Retain original behavior producer; replace only native source variants."""
    parser=argparse.ArgumentParser(description='Original behavior materializer with native source/variant adapter')
    parser.add_argument('--factree',required=True);parser.add_argument('--discoveries-dir',required=True)
    parser.add_argument('--dry-run',action='store_true');args=parser.parse_args(argv)
    path=Path(args.factree).resolve();directory=Path(args.discoveries_dir).resolve();project=_project_for(argv)
    before=read_json(path);_source_current(before,project,allow_blackbox_refresh=True);guard=InputGuard();guard.add(path)
    manifests=[];has_discoveries=False
    for file in sorted(directory.rglob('*__manifest.json')):
        guard.add(file);value=read_json(file)
        if not isinstance(value.get('discoveries',[]),list) or not isinstance(value.get('behavior_ledger',[]),list):
            raise MigrationError('Malformed native blackbox manifest: '+str(file))
        manifests.append((file,value));has_discoveries=has_discoveries or bool(value.get('discoveries'))
    has_blackbox=has_discoveries or any(v.get('behavior_ledger') for _,v in manifests) or _blackbox_present(before)
    if has_blackbox and not (before.get('native_source_sha256') or before['source'].get('source_sha256')):
        raise MigrationError('Native blackbox materialization needs current source facts with native_source_sha256; regenerate scaffold/enrich')
    index=NativeTriggerIndex(before,project,guard) if has_discoveries else None
    source_inputs=(index.source_inputs if index else _blackbox_source_inputs(before,project)) if has_blackbox else None
    source_inputs_sha=_json_digest(source_inputs) if source_inputs else None
    if source_inputs:
        for name in set(source_inputs['source_code'])|set(source_inputs['text_resources']):guard.add(Path(source_inputs['source_root'])/name)
    previous_variants={p['id']:copy.deepcopy(p) for p in page_records(before) if p.get('type')=='PageVariant' and p.get('source')=='blackbox_discovery'}
    old_ref=before.get('native_blackbox_input_identity') or {};same_inputs=old_ref.get('source_inputs_sha256')==source_inputs_sha
    rows=[];result=copy.deepcopy(before);pending=[];placements={}
    # Classification is recomputed as a whole. Unrelated ART/runtime facts are
    # retained only for the same stable source inputs, never as classifications.
    for key in ('pages','fragments','dialogs'):result[key]=[p for p in result.get(key,[]) if p['id'] not in previous_variants]
    by_id={p['id']:p for p in page_records(result)}
    for parent in by_id.values():
        if isinstance(parent.get('navigation'),dict):parent['navigation']['outbound']=[e for e in parent['navigation'].get('outbound',[]) if e.get('to') not in previous_variants]
        if 'extras_variants' in parent:parent['extras_variants']=[e for e in parent['extras_variants'] if e.get('variant_id') not in previous_variants]
    summary={'parents_processed':0,'variants_added':0,'edges_added':0,'skipped_dup':0,
             'skipped_dynamic':0,'pruned_dynamic':0,'baselines_copied':0,'dumps_copied':0,
             'classifications':{'static':0,'dynamic':0,'unknown':0},'system_ui_expected':0,
             'pruned_system_ui':0,'source_platform':'ios',
             'replacement':'native source classification and variant producer; original behavior core retained'}
    for file,manifest in manifests:
        parent=by_id.get(manifest.get('parent_page_id'));trip=_safe_name(manifest.get('trip_id'),'trip')
        if parent is None:raise MigrationError('Native discovery parent is absent from canonical tree: '+str(manifest.get('parent_page_id')))
        if manifest.get('discoveries'):summary['parents_processed']+=1
        for offset,discovery in enumerate(manifest.get('discoveries',[])):
            if not isinstance(discovery,dict):raise MigrationError('Malformed native discovery')
            classification=index.classify(discovery,parent,manifest)
            identity=hashlib.sha256(json.dumps({'manifest':str(file),'key':discovery.get('key',offset),
                'parent':parent['id'],'trip':trip},sort_keys=True).encode()).hexdigest()
            row={'id':identity,'manifest':str(file),'manifest_sha256':sha(file),'discovery_index':offset,
                 'discovery_key':discovery.get('key',offset),'parent':parent['id'],'trip':trip,**classification}
            rows.append(row);summary['classifications'][classification['classification']]+=1
            if classification['classification']=='unknown':
                pending.append({**row,'type':'native_blackbox_classification','node':parent['id'],
                    'verdict':None,'applied':False});continue
            if classification.get('destination_ownership')=='system':
                variant,_,_=_native_variant(parent,discovery);name=variant['id'];old=previous_variants.get(name)
                if old and (old.get('screenshots') or list((project/'spec/visual-verify/screenshots/ios').glob('*/'+name+'.png'))):
                    raise BindingError('System presentation ownership changes a frozen variant; resume from its affected Source baseline',22)
                summary['system_ui_expected']+=1
                if old:summary['pruned_system_ui']+=1
                continue
            if classification['classification']=='dynamic':
                summary['skipped_dynamic']+=1
                old_variant,_,_=_native_variant(parent,discovery);name=old_variant['id'];old=previous_variants.get(name)
                if old and old.get('source')=='blackbox_discovery' and old.get('parent_page')==parent['id']:
                    for key in ('pages','fragments','dialogs'):result[key]=[p for p in result.get(key,[]) if p['id']!=name]
                    parent.setdefault('navigation',{})['outbound']=[e for e in parent.get('navigation',{}).get('outbound',[]) if e.get('to')!=name]
                    parent['extras_variants']=[e for e in parent.get('extras_variants',[]) if e.get('variant_id')!=name]
                    by_id.pop(name,None);summary['pruned_dynamic']+=1
                    # Freeze forbids silently deleting previously accepted
                    # evidence. Affected-baseline invalidation is explicit.
                    frozen=old.get('screenshots') or list((project/'spec/visual-verify/screenshots/ios').glob('*/'+name+'.png'))
                    if frozen:pending.append({**row,'type':'native_blackbox_capture','node':name,
                        'reason':'Positive dynamic evidence invalidates a frozen static variant; restart from affected source baseline',
                        'verdict':None,'applied':False})
                continue
            variant,edge,extra=_native_variant(parent,discovery);name=variant['id']
            if name in by_id:summary['skipped_dup']+=1
            else:
                old=previous_variants.get(name)
                if old:
                    summary['skipped_dup']+=1
                    for key,value in old.items():
                        if key=='screenshots' or same_inputs and (key not in variant or key in {'components','reach_paths'}):variant[key]=copy.deepcopy(value)
                    if same_inputs:variant['navigation']['outbound']=copy.deepcopy(old.get('navigation',{}).get('outbound',[]))
                else:summary['variants_added']+=1
                result.setdefault('pages',[]).append(variant);by_id[name]=variant
            nav=parent.setdefault('navigation',{}).setdefault('outbound',[])
            if not any(e.get('to')==name and e.get('source')=='blackbox_discovery' for e in nav):nav.append(edge);summary['edges_added']+=1
            extras=parent.setdefault('extras_variants',[])
            if not any(e.get('variant_id')==name for e in extras):extras.append(extra)
            meta=_immutable_capture(discovery.get('capture_meta'))
            try:
                capture_paths,_,_=capture_pair(meta)
                for item in capture_paths.values():guard.add(item)
                if meta.get('page_id')!=name or meta['arrival'].get('expected_page')!=name or meta.get('trip')!=trip:
                    raise MigrationError('Variant capture must have actual arrival for its canonical variant and trip')
                if meta.get('native_blackbox_source_inputs_sha256')!=source_inputs_sha:
                    raise BindingError('Variant observation was captured with different native classification inputs; recapture',22)
                existing=placements.setdefault(trip,{}).get(name)
                if existing and existing['sha256']!=meta['sha256']:raise MigrationError('Conflicting native variant captures')
                placements[trip][name]=meta
            except MigrationError as exc:
                pending.append({**row,'type':'native_blackbox_capture','node':name,'reason':str(exc),
                                'verdict':None,'applied':False})
    if args.dry_run:
        print(json.dumps({'dry_run':True,'summary':summary,'classifications':rows,'pending':pending},ensure_ascii=False));return 0
    # The opaque core receives complete behavior ledgers and no discoveries or
    # PageVariants. Thus its Android source filter is outside this call's data
    # domain; missing android_root cannot classify or prune native discoveries.
    with wire_copy(path,project,allow_blackbox_refresh=True) as (wire,manifest,wire_guard),tempfile.TemporaryDirectory(prefix='native-blackbox-ledgers-') as temp:
        original=read_json(wire)
        for key in ('pages','fragments','dialogs'):original[key]=[p for p in original.get(key,[]) if p.get('type')!='PageVariant']
        write_json(wire,original);manifest['wire_sha256']=sha(wire)
        for file,value in manifests:
            staged=Path(temp)/file.relative_to(directory);copy_value=copy.deepcopy(value);copy_value['discoveries']=[];write_json(staged,copy_value)
        verify_projection(path,wire,manifest)
        process=_core('materialize_blackbox_to_factree',['--factree',str(wire),'--discoveries-dir',temp],scripts)
        guard.verify();wire_guard.verify()
        if process.returncode:return _emit(process,lambda text:text.replace(str(wire),str(path)).replace(temp,str(directory)))
        produced=native_writeback(before,read_json(wire));behaviors={p['id']:p.get('blackbox_behavior') for p in page_records(produced)}
        for page in page_records(result):
            if behaviors.get(page['id']) is not None:page['blackbox_behavior']=behaviors[page['id']]
        _emit(process,lambda text:text.replace(str(wire),str(path)).replace(temp,str(directory)))
    guard.verify();backup=path.with_name(path.name+'.bak_before_materialize')
    if not backup.exists():shutil.copy2(path,backup)
    ew=project/'spec/visual-verify/edgewalk';ledger_path=ew/'pending_bindings.json'
    previous=read_json(ledger_path) if ledger_path.is_file() else []
    if not isinstance(previous,list):raise MigrationError('Invalid pending binding ledger')
    reconsidered={r['id'] for r in rows}
    other=[r for r in previous if r.get('type') not in {'native_blackbox_classification','native_blackbox_capture'}
           or r.get('id') not in reconsidered]
    write_json(ledger_path,other+pending)
    if source_inputs:_publish_blackbox_receipt(path,result,project,source_inputs,directory,rows,old_ref.get('sha256'))
    else:write_json(path,result)
    # The original source-placement lifecycle enforces freezing, three-way
    # pairing, resize geometry and screenshot record schema for each variant.
    for trip,metas in placements.items():
        missing={}
        for name,meta in metas.items():
            existing=by_id[name].get('screenshots',{}).get(trip)
            if existing:
                try:_variant_baseline_current(result,by_id[name],existing)
                except BindingError as exc:pending.append({'id':'frozen:'+trip+':'+name,'node':name,'type':'native_blackbox_capture',
                    'reason':str(exc),'verdict':None,'applied':False})
            else:missing[name]=meta
        if not missing:continue
        with tempfile.TemporaryDirectory(prefix='native-variant-placement-') as temp:
            placement_ew=Path(temp);write_json(placement_ew/'walk_plan.json',{'walks':[{'trip_id':trip,'settles':list(missing)}]})
            write_json(placement_ew/'ledger.json',{'targets':list(missing),'settled':{name:{'via':'blackbox discovered from '+by_id[name]['parent_page'],
                'trip':trip,'capture_meta':meta} for name,meta in missing.items()}})
            placed=place_baselines(path,placement_ew,project,trip)
            summary['baselines_copied']+=len(placed['placed']);summary['dumps_copied']+=len(placed['placed'])
            for name in placed['skipped_exist']:
                pending.append({'id':'frozen:'+trip+':'+name,'node':name,'type':'native_blackbox_capture',
                    'reason':'A frozen variant baseline exists without its current canonical capture record',
                    'verdict':None,'applied':False})
    # Recalculation from the same selected source/capture evidence, not a user
    # supplied verdict, settles these records. Unrelated pending debts survive.
    write_json(ledger_path,other+pending)
    if source_inputs:
        result=read_json(path)
        _publish_blackbox_receipt(path,result,project,source_inputs,directory,rows,old_ref.get('sha256'))
    native_pending=[r for r in other+pending if r.get('type') in {'native_blackbox_classification','native_blackbox_capture'}]
    write_json(ew/'native_blackbox_materialization.json',{'summary':summary,'classifications':rows,'pending':native_pending})
    print('[native_summary] '+json.dumps(summary,ensure_ascii=False))
    if native_pending:print('Native blackbox classification/capture evidence remains pending; original finalize binding gate is red');return 20
    return 0


def tree_write_cli(command,argv,scripts):
    """Run original tree writer in a checked disposable wire, then publish iOS."""
    if command=='materialize_blackbox_to_factree':return materialize_native_cli(argv,scripts)
    option='--factree' if command=='materialize_blackbox_to_factree' else '--tree'
    value=_option(argv,option)
    if not value:raise MigrationError('Missing canonical tree argument '+option)
    path=Path(value).resolve();before=read_json(path);project=_project_for(argv)
    before_edges=sum(len(p.get('inbound_triggers',[])) for p in page_records(before))
    with wire_copy(path,project,allow_blackbox_refresh=True) as (wire,manifest,guard):
        args=_replace(argv,option,wire)
        grounding=_option(argv,'--grounding')
        if grounding:
            source=Path(grounding).resolve();guard.add(source)
            judgments=read_json(source)
            if not isinstance(judgments,list) or any(not isinstance(j,dict) for j in judgments):
                raise MigrationError('Native grounding judgments require the original row list')
            from .native_visual import functional_snapshot
            pages={p['id']:p for p in page_records(before)}
            for judgment in judgments:
                expected=judgment.get('functional_checks_sha256')
                node=judgment.get('node');bindings=set()
                if node in pages:
                    directories={source.parent/'grounding',project/'spec/visual-verify/edgewalk/grounding'}
                    configured=os.environ.get('VV_EDGEWALK_DIR')
                    if configured:directories.add(Path(configured).resolve()/'grounding')
                    for directory in directories:
                        for meta_path in directory.glob('*/run_meta.json'):
                            metadata=read_json(meta_path)
                            if metadata.get('node',meta_path.parent.name)!=node:continue
                            guard.add(meta_path);binding=metadata.get('functional_checks_sha256')
                            if binding:bindings.add(binding)
                if len(bindings)>1 or bindings and expected not in bindings:
                    raise MigrationError('Native indexed grounding must retain its collector snapshot identity')
                if expected and (judgment.get('node') not in pages or expected!=functional_snapshot(pages[judgment['node']])):
                    raise MigrationError('Native grounding functional snapshot is stale before writeback')
                if expected:
                    page=pages[judgment['node']];idx=judgment.get('check_idx',judgment.get('idx'))
                    checks=page.get('functional_checks',[])
                    if type(idx) is not int or not 0<=idx<len(checks):raise MigrationError('Invalid native grounding page-local check_idx')
                    check=checks[idx]
                    if judgment.get('feature_path')!=check.get('feature_path') or judgment.get('check_name')!=check.get('name',check.get('check_name')):
                        raise MigrationError('Native grounding identity differs from its indexed check')
            derived=wire.parent/'grounding.json';write_json(derived,legacy_wire(judgments))
            args=_replace(args,'--grounding',derived)
        verify_projection(path,wire,manifest)
        process=_core(command,args,scripts);guard.verify()
        if process.returncode:return _emit(process,lambda text:text.replace(str(wire),str(path)))
        if '--dry-run' in argv:return _emit(process,lambda text:text.replace(str(wire),str(path)))
        result=native_writeback(before,read_json(wire))
        after_edges=sum(len(p.get('inbound_triggers',[])) for p in page_records(result))
        if command=='writeback_walk' and after_edges!=before_edges:
            raise MigrationError('Original writeback changed inbound edge existence; refusing canonical publication')
        result['source_platform']='ios';guard.verify()
        code=_emit(process,lambda text:text.replace(str(wire),str(path)))
    write_json(path,result)
    return code


def inherit_cli(argv,scripts):
    from .native_inheritance import prepare_inputs, bind_results, bind_retap
    from .native_functional import publish
    edgewalk=Path(_option(argv,'--dir',os.environ.get('VV_EDGEWALK_DIR','spec/visual-verify/edgewalk'))).resolve()
    guard=InputGuard()
    prior_path=edgewalk/'grounding_results.json'
    if prior_path.is_file():
        guard.add(prior_path)
        prior_grounding=read_json(prior_path)
    else:prior_grounding=[]
    with tempfile.TemporaryDirectory(prefix='hmigbot-ios-inherit-') as temp:
        destination=Path(temp)/'edgewalk';destination.mkdir()
        for file in edgewalk.rglob('*.json'):
            if file.is_symlink():raise MigrationError('Symlink in native walk ledger')
            guard.add(file);out=destination/file.relative_to(edgewalk)
            write_json(out,legacy_wire(read_json(file)))
        args=_replace(argv,'--dir',destination)
        bindings,receipt=prepare_inputs(edgewalk,destination,guard,argv)
        process=_core('walk_inherit',args,scripts);guard.verify()
        if process.returncode:return _emit(process,lambda text:text.replace(str(destination),str(edgewalk)))
        outputs={}
        for name in ('grounding_results.json','needs_retap.json'):
            file=destination/name
            if file.is_file():
                current=read_json(edgewalk/name) if (edgewalk/name).is_file() else []
                result=native_writeback(current,read_json(file))
                if receipt:
                    result=(bind_results(result,bindings,receipt,prior_grounding) if name=='grounding_results.json'
                            else bind_retap(result,bindings,receipt))
                outputs[edgewalk/name]=result
        if receipt:
            outputs[edgewalk/'inherit.native-input.json']=receipt
        if outputs:publish(outputs,guard)
        return _emit(process,lambda text:text.replace(str(destination),str(edgewalk)))


def _judgement_debt(edgewalk,tree=None):
    path=edgewalk/'pending_bindings.json'
    if path.is_file():
        pending=read_json(path)
        if not isinstance(pending,list):raise MigrationError('Unrecognized pending binding ledger shape')
        for row in pending:
            if not isinstance(row,dict):raise MigrationError('Invalid pending binding record')
            if row.get('type') in {'native_blackbox_classification','native_blackbox_capture'}:
                return 'Native blackbox evidence must be reclassified/materialized from its source and capture anchors: '+str(row.get('node'))
            if row.get('verdict') is None or row.get('applied') is False:
                return 'Unjudged or unapplied native page binding: '+str(row.get('node'))
    grounding=read_json(edgewalk/'grounding_results.json') if (edgewalk/'grounding_results.json').is_file() else []
    if not isinstance(grounding,list):raise MigrationError('Invalid source grounding judgement ledger')
    judged={(r.get('node'),r.get('check_idx',r.get('idx')),r.get('check_name')) for r in grounding if isinstance(r,dict)}
    for file in (edgewalk/'grounding').glob('*/run_meta.json'):
        meta=read_json(file)
        fingerprint=meta.get('functional_checks_sha256')
        if fingerprint and tree is not None:
            from .native_visual import functional_snapshot
            pages=[p for p in page_records(tree) if p['id']==meta.get('node',file.parent.name)]
            if len(pages)!=1 or fingerprint!=functional_snapshot(pages[0]):
                return 'Native grounding functional snapshot is stale: '+str(file)
        checks=meta.get('checks')
        if not isinstance(checks,list):raise MigrationError('Unknown native grounding run_meta shape')
        names=[r.get('name') or r.get('check_name') for r in checks if isinstance(r,dict)]
        for row in checks:
            if row.get('status') not in {'ok','found_no_text'}:continue
            node=meta.get('node',file.parent.name);idx=row.get('idx');name=row.get('name') or row.get('check_name')
            matches=[x for x in judged if x[0]==node and (x[1]==idx if x[1] is not None and idx is not None
                      else x[2]==name and names.count(name)==1)]
            if not matches:return 'Observed native behavior is unjudged: '+str(node)+'/'+str(name)
            if fingerprint:
                bound=[g for g in grounding if isinstance(g,dict) and g.get('node')==node
                    and g.get('check_idx',g.get('idx'))==idx and g.get('check_name')==name
                    and g.get('functional_checks_sha256')==fingerprint and g.get('feature_path')==row.get('feature_path')]
                if not bound:return 'Indexed native judgement lost its collector snapshot identity: '+str(node)+'/'+str(name)
    return None


def finalize_cli(argv,scripts):
    """Readable orchestration for the broken original main(argv) dispatcher.

    It replaces orchestration only, in the documented order. The original
    inheritance, writeback, blackbox and readiness cores still decide their
    own evidence and failures. Native placement is the source-specific step.
    """
    parser=argparse.ArgumentParser(description='Native source finalize; original five-step order and gates')
    parser.add_argument('--trip',required=True);parser.add_argument('--tree',default='spec/toolkit-fact-tree.json')
    parser.add_argument('--dir',default=os.environ.get('VV_EDGEWALK_DIR','spec/visual-verify/edgewalk'))
    parser.add_argument('--project-root',default='.');parser.add_argument('--walk-id',default='walk_native')
    parser.add_argument('--reason-overrides');parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--source-app',help='Current verified source .app for archived-trip observations')
    args=parser.parse_args(argv);tree=Path(args.tree).resolve();ew=Path(args.dir).resolve();project=Path(args.project_root).resolve()
    before=read_json(tree);_source_current(before,project,allow_blackbox_refresh=True)
    debt=_judgement_debt(ew,before)
    if debt:print(debt);return 20
    if args.dry_run:
        print(json.dumps({'dry_run':True,'source_platform':'ios','order':FINALIZE_ORDER,
                          'note':'No canonical write or original step was claimed executed'},ensure_ascii=False));return 0
    print('1. '+FINALIZE_ORDER[0][1])
    code=inherit_cli(['--dir',str(ew),'--device-state',args.trip],scripts)
    if code:return code
    retap=read_json(ew/'needs_retap.json') if (ew/'needs_retap.json').is_file() else []
    if retap:print('Same-destination behaviors still require actual retaps');return 20
    debt=_judgement_debt(ew,before)
    if debt:print(debt);return 20
    # Preserve the existing pre-writeback backup, without making another gate.
    backup=ew/'backups'/(tree.stem+'.before_'+args.walk_id+'.json')
    _safe_name(args.walk_id,'walk');backup.parent.mkdir(parents=True,exist_ok=True)
    if not backup.exists():shutil.copy2(tree,backup)
    print('2. '+FINALIZE_ORDER[1][1])
    command=['--tree',str(tree),'--walk-id',args.walk_id]
    if (ew/'grounding_results.json').is_file():command+=['--grounding',str(ew/'grounding_results.json')]
    if (ew/'edge_results.json').is_file():command+=['--edges',str(ew/'edge_results.json')]
    code=tree_write_cli('writeback_walk',command,scripts)
    if code:return code
    print('3. '+FINALIZE_ORDER[2][1])
    discoveries=project/'spec/visual-verify/blackbox_discoveries'
    code=tree_write_cli('materialize_blackbox_to_factree',['--factree',str(tree),'--discoveries-dir',str(discoveries)],scripts)
    if code:return code
    print('4. '+FINALIZE_ORDER[3][1])
    result=place_baselines(tree,ew,project,args.trip,reason_overrides=args.reason_overrides,source_app=args.source_app)
    print(json.dumps(result,ensure_ascii=False))
    if result['skipped_exist']:return 20
    print('5. '+FINALIZE_ORDER[4][1])
    after=read_json(tree)
    if sum(len(x.get('inbound_triggers',[])) for x in page_records(before))!=sum(len(x.get('inbound_triggers',[])) for x in page_records(after)):
        print('Inbound edge count changed during finalization');return 20
    for name in ('phase2_needs','check_android_screenshot','check_blackbox_evidence'):
        options=[str(tree),'--trip',args.trip] if name=='phase2_needs' else []
        code=data_cli(name,options,scripts,project_override=project)
        if code:return code
    print(json.dumps({'status':'finalized','source_platform':'ios','trip':args.trip,
                      'note':'Source ledgers finalized; no target round verdict implied'},ensure_ascii=False));return 0


def _check_plan_binding(plan_path,project,guard):
    """Validate native compilation provenance before a target run consumes it."""
    plan_path=Path(plan_path).resolve();guard.add(plan_path);plan=read_json(plan_path)
    provenance=plan.get('native_input_provenance')
    if not isinstance(provenance,dict) or provenance.get('source_platform')!='ios':
        raise MigrationError('Target replay needs a plan compiled from current native source baselines')
    tree=Path(provenance['canonical_tree']).resolve()
    if sha(tree)!=provenance.get('canonical_tree_sha256'):
        raise MigrationError('Replay plan references a stale canonical native tree')
    guard.add(tree);source_tree=read_json(tree);_source_current(source_tree,project)
    for mapping in (provenance.get('baseline',{}),provenance.get('baseline2',{})):
        for page,row in mapping.items():
            for key,hashkey in (('canonical_png','canonical_png_sha256'),('canonical_xml','canonical_xml_sha256')):
                path=Path(row[key]);guard.add(path)
                if sha(path)!=row.get(hashkey):raise MigrationError('Replay plan native baseline hash mismatch')
            path=Path(row['native_json']);guard.add(path)
            if sha(path)!=row.get('native_json_sha256'):
                raise MigrationError('Replay plan original native snapshot hash mismatch')
            capture_pair(_baseline_record(source_tree,page,Path(row['canonical_png']).parent.resolve()))
    return plan


def replay_exec_cli(argv,scripts):
    """Retain the real HMOS executor; bind its manifest to actual input hashes."""
    from .compiled_runtime import run as original
    plan_value=_option(argv,'--plan');out_value=_option(argv,'--out-dir')
    if not plan_value or not out_value:raise MigrationError('Target replay needs explicit --plan and --out-dir')
    project=_project_for(argv);guard=InputGuard();plan=_check_plan_binding(plan_value,project,guard)
    output=Path(out_value).resolve();manifest=output/'capture_manifest.json'
    prior=sha(manifest) if manifest.is_file() else None;started=time.time()
    code=original('replay_exec',argv,scripts);guard.verify()
    if manifest.is_file() and sha(manifest)!=prior:
        value=read_json(manifest)
        if value.get('role')!='capture':raise MigrationError('Target executor did not produce a capture manifest')
        previous=value.get('native_input_provenance')
        if '--resume-from' in argv and previous and previous.get('plan_sha256')!=sha(plan_value):
            raise MigrationError('Target replay resume changed its frozen plan')
        value['native_input_provenance']={'source_platform':'ios','plan_path':str(Path(plan_value).resolve()),
            'plan_sha256':sha(plan_value),'canonical_tree_sha256':plan['native_input_provenance']['canonical_tree_sha256'],
            'baseline':copy.deepcopy(plan['native_input_provenance'].get('baseline',{})),
            'invocation_started_at':started,'invocation_finished_at':time.time(),
            'backend_exit_code':code,'note':'Written after actual retained HMOS replay invocation; no verdict override'}
        write_json(manifest,value)
    return code


class BindingError(MigrationError):
    def __init__(self,message,code=22):super().__init__(message);self.code=code


def _native_target_binding(project,capture,plan_path,round_number=None,trip=None):
    guard=InputGuard();plan=_check_plan_binding(plan_path,project,guard)
    manifest_path=Path(capture)/'capture_manifest.json';guard.add(manifest_path);manifest=read_json(manifest_path)
    provenance=manifest.get('native_input_provenance',{})
    if provenance.get('plan_sha256')!=sha(plan_path) or provenance.get('baseline')!=plan['native_input_provenance'].get('baseline',{}):
        raise BindingError('Target capture was not bound to this native source plan and baseline')
    if round_number is not None:
        proofs=[Path(project)/f'spec/visual-verify/screenshots/harmony/round-{round_number}'/trip/'_placement.json',
                Path(capture)/f'judge_input_round{round_number}.json']
        for file in proofs:
            if not file.is_file():raise BindingError('Current target placement/judge packet is missing',20)
            data=read_json(file);binding=data.get('native_input_provenance',{})
            if binding.get('round')!=round_number or binding.get('trip')!=trip:
                raise BindingError('Target artifact provenance has no matching round/trip',20)
            if binding.get('capture_manifest_sha256')!=sha(manifest_path) or binding.get('plan_sha256')!=sha(plan_path):
                raise BindingError('Target artifacts reference a different replay manifest or plan')
            for relative,digest in binding.get('artifact_sha256',{}).items():
                path=Path(project)/relative;guard.add(path)
                if sha(path)!=digest:raise BindingError('Canonical target artifact hash changed after placement/judge preparation')
    guard.verify()
    result={'plan_sha256':sha(plan_path),'capture_manifest_sha256':sha(manifest_path),
            'canonical_tree_sha256':plan['native_input_provenance']['canonical_tree_sha256']}
    ref=plan['native_input_provenance'].get('native_blackbox_input_identity')
    if ref:result['native_blackbox_input_identity']=copy.deepcopy(ref)
    return result


def _record_target_provenance(command,project,round_number,trip,capture,proof):
    manifest=read_json(Path(capture)/'capture_manifest.json')
    plan_path=manifest.get('native_input_provenance',{}).get('plan_path')
    if not plan_path:raise MigrationError('Target data placement lacks a native replay input receipt')
    binding=_native_target_binding(project,capture,plan_path)
    if not proof.is_file():raise MigrationError('Original target data command did not produce its existing proof artifact')
    value=read_json(proof)
    artifacts={}
    families=['harmony','sbs'] if command=='build_judge_input' else ['harmony']
    for family in families:
        base=Path(project)/f'spec/visual-verify/screenshots/{family}/round-{round_number}'/trip
        for path in sorted(base.rglob('*')) if base.is_dir() else []:
            if path.is_file() and path.name!='_placement.json' and path.suffix in {'.jpeg','.jpg','.png','.json'}:
                artifacts[str(path.relative_to(project))]=sha(path)
    value['native_input_provenance']={**binding,'source_platform':'ios','round':round_number,'trip':trip,
        'artifact_sha256':artifacts,'producer':command,
        'note':'Hashes recorded after retained mechanical placement/judge preparation; original arrival/coverage gates remain authoritative'}
    write_json(proof,value)


def _ticket_tool_debts(project,round_number,missing):
    """Classify only after the original gap core has validated every claim.

    This is not a replacement YAML/gap validator. Unrecognized complex YAML
    remains unclassified rather than being declared a valid tool debt.
    """
    found={}
    for file in (Path(project)/f'spec/fix/round-{round_number}').rglob('*.md'):
        text=file.read_text(encoding='utf-8-sig');match=re.match(r'\A---\s*\n(.*?)\n---',text,re.S)
        if not match:continue
        values={}
        for line in match[1].splitlines():
            row=re.match(r'^([A-Za-z_][\w-]*):\s*(.*?)\s*$',line)
            if not row:continue
            key,value=row.groups()
            try:value=json.loads(value)
            except ValueError:value=value
            values[key]=value
        page=values.get('page_id')
        if page not in missing or values.get('is_migration_bug') is not False:continue
        implementation=values.get('hmos_impl');evidence=values.get('not_migration_evidence')
        real_impl=isinstance(implementation,str) and implementation not in {'','unknown','null'} and (Path(project)/implementation).is_file()
        valid_evidence=bool(evidence) and not (isinstance(evidence,str) and evidence in {'unknown','null'})
        if real_impl or valid_evidence:
            found[page]={'ticket':str(file.relative_to(project)),'hmos_impl':implementation,
                         'not_migration_evidence':evidence,'device_verified':False}
    return found


def _artifact_conditions(process):
    return re.findall(r'❌\s*cond\s+(\d+[a-z]?)',process.stdout+'\n'+process.stderr)


def round_aggregate_cli(argv,scripts):
    """Replace only broken trip enumeration/aggregation, retaining per-trip cores.

    Contract: Android 1.5.2 SKILL Phase 6 step0 and §6.4, replay-run §4.1.
    Platform-specific baseline projection stays in ProjectMirror. This adapter
    does not write round_budget's _state.yaml or advance any round.
    """
    parser=argparse.ArgumentParser(description='Original-contract round aggregation with retained per-trip gates')
    parser.add_argument('root');parser.add_argument('round',type=int)
    parser.add_argument('--trip-out',action='append',default=[]);parser.add_argument('--plan',action='append',default=[])
    args=parser.parse_args(argv);project=Path(args.root).resolve()
    if not 0<=args.round<=9:raise MigrationError('Original positional core ABI cannot encode this round')
    def mapping(values):
        out={}
        for value in values:
            if '=' not in value:raise MigrationError('Expected TRIP=PATH')
            trip,path=value.split('=',1)
            if not trip or not path or trip in out:raise MigrationError('Missing or duplicate trip input')
            out[trip]=str(Path(path).resolve())
        return out
    outs,plans=mapping(args.trip_out),mapping(args.plan)
    tree=project/'spec/toolkit-fact-tree.json'
    native=tree.is_file() and ios_tree(read_json(tree))
    family='ios' if native or (project/'spec/visual-verify/screenshots/ios').is_dir() else 'android'
    source=project/('spec/visual-verify/screenshots/'+family)
    if not source.is_dir():raise MigrationError('Frozen canonical source baseline directory is missing')
    expected=sorted(p.name for p in source.iterdir() if p.is_dir() and any(p.glob('*.png')))
    if not expected:raise MigrationError('Canonical source baseline has no executed trips')
    if native:_validate_project_baselines(project)
    with ProjectMirror(project,round_number=args.round,short_trips=True,source_family=family) as mirror:
        state_path=mirror.root/f'spec/fix/round-{args.round}/_run_state.json'
        encoded='x'+mirror.root_alias+str(args.round)
        evidence=_core('assert_evidence_channel',[encoded],scripts,cwd=mirror.work)
        state_path.unlink(missing_ok=True)
        # The original seed still owns ticket parsing, open/product counts and
        # per-trip SBS completeness. Its default "no --trip-out" verdict is not
        # used as the aggregate result.
        seed_process=_core('assert_round_complete',[encoded],scripts,cwd=mirror.work)
        if not state_path.is_file():raise MigrationError('Original round core did not emit its ticket/denominator seed')
        seed=_walk_strings(read_json(state_path),mirror.normalize)
        failures=[];trips={};events=[];tool_debts={}
        if evidence.returncode:
            failures.append({'gate':'evidence_channel','exit_code':evidence.returncode,
                             'detail':mirror.normalize(evidence.stdout+evidence.stderr)})
            events.append((30,'EVIDENCE_BYPASSED') if evidence.returncode==30 else (20,'ROUND_INCOMPLETE'))
        for trip in expected:
            baseline={p.stem for p in (source/trip).glob('*.png') if not p.stem.endswith('_long') and not re.search(r'_seg_\d+$',p.stem)}
            harmony=project/f'spec/visual-verify/screenshots/harmony/round-{args.round}'/trip
            delivered={p.stem for p in harmony.glob('*.jpeg')} if harmony.is_dir() else set()
            missing=sorted(baseline-delivered)
            row=copy.deepcopy(seed.get('trips',{}).get(trip,{}))
            row.update(android_denominator=len(baseline),out_dir=outs.get(trip),harmony_dir_exists=harmony.is_dir(),
                       delivered=len(baseline&delivered),replay_assert_exit=None,gap_ticket_exit=None,notes=[])
            trips[trip]=row
            if trip not in outs or trip not in plans or not (Path(outs.get(trip,''))/'capture_manifest.json').is_file() or not Path(plans.get(trip,'')).is_file():
                row['notes'].append('Missing this trip\'s explicit replay output, plan or capture manifest; trip was not executed')
                failures.append({'trip':trip,'gate':'trip_inputs','exit_code':20,'detail':row['notes'][-1]});events.append((20,'ROUND_INCOMPLETE'));continue
            if native:
                try:row['native_input_binding']=_native_target_binding(project,outs[trip],plans[trip],args.round,trip)
                except MigrationError as exc:
                    code=getattr(exc,'code',22);verdict='STALE_ARTIFACTS' if code==22 else 'ROUND_INCOMPLETE'
                    row['notes'].append(str(exc));failures.append({'trip':trip,'gate':'native_input_binding','exit_code':code,'detail':str(exc)});events.append((code,verdict));continue
            ca=mirror.add_capture(outs[trip]);pa=mirror.add_plan(plans[trip])
            prefix=encoded+mirror.trip_alias[trip]+ca
            artifact=_core('assert_replay_artifacts',[prefix+pa],scripts,cwd=mirror.work)
            gap=_core('assert_gap_ticket_coverage',[prefix],scripts,cwd=mirror.work)
            row['replay_assert_exit']=artifact.returncode;row['gap_ticket_exit']=gap.returncode
            conditions=_artifact_conditions(artifact)
            row['artifact_failed_conditions']=conditions
            row['notes']=[mirror.normalize(artifact.stdout+artifact.stderr),mirror.normalize(gap.stdout+gap.stderr)]
            if artifact.returncode:failures.append({'trip':trip,'gate':'replay_artifacts','exit_code':artifact.returncode,'conditions':conditions,'detail':row['notes'][0]})
            if gap.returncode:failures.append({'trip':trip,'gate':'gap_ticket','exit_code':gap.returncode,'detail':row['notes'][1]})
            # Phase6 step0 already preceded this loop. Within each frozen trip,
            # artifact precedes gap as in replay-run §4.1; all failures remain.
            if artifact.returncode and '0' in conditions:events.append((22,'STALE_ARTIFACTS'))
            elif artifact.returncode and conditions and set(conditions)=={'1'} and missing:
                if gap.returncode:events.append((21,'GAP_UNTICKETED'))
                else:
                    debts=_ticket_tool_debts(project,args.round,missing)
                    if set(debts)==set(missing):
                        tool_debts[trip]=debts;events.append((11,'ACCOUNTED_WITH_DEBT'))
                    else:events.append((20,'ROUND_INCOMPLETE'))
            elif artifact.returncode:events.append((20,'ROUND_INCOMPLETE'))
            elif gap.returncode:events.append((21,'GAP_UNTICKETED'))
            elif row.get('sbs_missing'):events.append((20,'ROUND_INCOMPLETE'))
        mirror.verify()
        # A debt disposition is not a successful round. A later true failure
        # still prevents accounting; do not let an earlier debt mask it.
        blocking=[event for event in events if event[0]!=11]
        if blocking:code,verdict=blocking[0]
        elif events:code,verdict=11,'ACCOUNTED_WITH_DEBT'
        elif seed.get('open_findings',0):code,verdict=10,'ALIGNMENT_HAS_FINDINGS'
        else:code,verdict=0,'ALIGNMENT_CLEAN'
        result={'round':args.round,'expected_trips':expected,'trips':trips,'verdict':verdict,
            'evidence_channel_exit':evidence.returncode,'evidence_channel_notes':[mirror.normalize(evidence.stdout+evidence.stderr)],
            'open_findings':seed.get('open_findings',0),'product_findings':seed.get('product_findings',0),'exit_code':code,
            'findings':failures,'tool_boundary_debt':tool_debts,
            'native_input_provenance':{'adapter':'readable-original-contract-round-aggregation',
                'contract':'Android 1.5.2 SKILL Phase6 step0 / §6.4; replay-run §4.1',
                'per_trip':'Original artifact, gap and evidence cores; positional alias projection',
                'aggregation_equivalence':'Contract tests; equivalence with broken compiled aggregation has not been established',
                'source_family':family,'canonical_baseline_sha256':{str(p.relative_to(project)):sha(p) for p in sorted(source.rglob('*.png'))},
                'round_budget_unchanged':True}}
        if native and read_json(tree).get('native_blackbox_input_identity'):
            result['native_input_provenance']['native_blackbox_input_identity']=copy.deepcopy(read_json(tree)['native_blackbox_input_identity'])
        destination=project/f'spec/fix/round-{args.round}/_run_state.json'
        mirror.release_output(destination);write_json(destination,result)
        print(json.dumps({'round':args.round,'verdict':verdict,'exit_code':code,
                          'expected_trips':expected,'tool_debt_count':sum(map(len,tool_debts.values())),
                          'run_state':str(destination)},ensure_ascii=False))
        return code
