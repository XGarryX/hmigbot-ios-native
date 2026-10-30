"""Complete the existing final feature status field around the original writer."""
import argparse
import json
from pathlib import Path
import re
import sys
from registry_table_format import cells, replace_bytes


def _rows(raw, requested):
    lines=raw.splitlines(keepends=True);found={name:[] for name in requested}
    active=None;fence=None
    for index,line in enumerate(lines):
        text=line.decode('utf-8').rstrip('\r\n')
        mark=re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$',text)
        if mark:
            token,tail=mark.groups()
            if fence is None:fence=(token[0],len(token))
            elif token[0]==fence[0] and len(token)>=fence[1] and not tail.strip():fence=None
            active=None;continue
        if fence is not None:continue
        row=cells(line)
        if row and index+1<len(lines):
            separator=cells(lines[index+1])
            if separator and len(row)==len(separator) and all(re.fullmatch(r':?-{3,}:?',x) for x in separator):
                ids=[i for i,x in enumerate(row) if x.casefold()=='id']
                statuses=[i for i,x in enumerate(row) if x.casefold() in ('status','状态')]
                active=(len(row),ids[0],statuses[0]) if len(ids)==len(statuses)==1 else None
                continue
        if not active or not row or len(row)!=active[0]:
            active=None;continue
        width,id_col,status_col=active
        if row[id_col] in found:found[row[id_col]].append((index,status_col,row))
    result={}
    for name,matches in found.items():
        if len(matches)!=1:raise ValueError('Feature ID needs one unambiguous template row: '+name)
        index,col,row=matches[0]
        if row[col] not in ('implemented','verified'):
            raise ValueError('Feature must be implemented before final verification: '+name)
        result[name]=(index,col,row)
    return lines,result


def _updated(raw,requested,previous=None):
    lines,rows=_rows(raw,requested);changed=[]
    for name,(index,col,row) in rows.items():
        if previous is not None:
            old=previous[name][2]
            if old!=row:
                raise ValueError('Original writer changed a verified target row: '+name)
        if row[col]=='verified':continue
        full=lines[index].decode('utf-8');text=full.rstrip('\r\n');ending=full[len(text):]
        pipes=[]
        for pos,char in enumerate(text):
            if char!='|':continue
            backslashes=0;j=pos-1
            while j>=0 and text[j]=='\\':backslashes+=1;j-=1
            if backslashes%2==0:pipes.append(pos)
        if len(pipes)!=len(row)+1:raise ValueError('Feature row delimiters changed: '+name)
        start,end=pipes[col]+1,pipes[col+1];value=text[start:end]
        leading=value[:len(value)-len(value.lstrip())];trailing=value[len(value.rstrip()):]
        lines[index]=(text[:start]+leading+'verified'+trailing+text[end:]+ending).encode('utf-8')
        changed.append(name)
    return b''.join(lines),rows,changed


def apply_if_requested(argv,run_original):
    """Return None for legacy selection; never substitute a native success."""
    if '-h' in argv or '--help' in argv:return None
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('manifest',nargs='?');parser.add_argument('--project-root',default='.')
    parser.add_argument('--dry-run',action='store_true');args,unknown=parser.parse_known_args(argv)
    if unknown or not args.manifest:return None
    try:manifest=json.loads(Path(args.manifest).read_text(encoding='utf-8'))
    except (OSError,ValueError):return None
    feature=manifest.get('feature_index',{}) if isinstance(manifest,dict) else {}
    if not isinstance(feature,dict) or 'verified' not in feature:return None
    requested=feature['verified']
    if manifest.get('mode')!='final':raise ValueError('feature_index.verified is a final-mode field')
    if not isinstance(manifest.get('id'),str) or not manifest['id'].strip() or any(c in manifest['id'] for c in '\r\n\0'):
        raise ValueError('Final writeback needs a valid manifest id')
    if not isinstance(requested,list) or any(not isinstance(x,str) or not x.strip() for x in requested):
        raise ValueError('feature_index.verified must be a string list')
    if len(requested)!=len(set(requested)):raise ValueError('Duplicate verified feature IDs')
    implemented=feature.get('implemented',[])
    if not isinstance(implemented,list) or any(not isinstance(x,str) for x in implemented):
        raise ValueError('feature_index.implemented must be a string list')
    if set(requested)&set(implemented):raise ValueError('A feature cannot be implemented and verified in the same writeback')
    project=Path(args.project_root).resolve(strict=True);path=project/'spec/baseline/feature-index.md'
    for part in (path,*path.parents):
        if part.is_symlink() or getattr(part,'is_junction',lambda:False)():raise ValueError('Feature status path cannot traverse links')
    before=path.read_bytes();_,rows,planned=_updated(before,requested)
    dry=list(argv) if args.dry_run else [*argv,'--dry-run']
    code=run_original(dry)
    if code!=0:return code
    if args.dry_run:
        print('feature_index.verified dry-run: '+json.dumps(planned,ensure_ascii=False),flush=True)
        return 0
    code=run_original(argv)
    if code!=0:return code
    try:
        current=path.read_bytes();updated,_,changed=_updated(current,requested,rows)
        if path.read_bytes()!=current:raise ValueError('Feature status input changed before final write')
        if updated!=current:replace_bytes(path,updated)
    except (OSError,ValueError) as exc:
        print('feature_index.verified post-write failure (native effects retained; replay original manifest): '+str(exc),file=sys.stderr)
        return 3
    print('feature_index.verified: '+str(len(changed))+' changed / '+str(len(requested)-len(changed))+' no-op',flush=True)
    return 0
