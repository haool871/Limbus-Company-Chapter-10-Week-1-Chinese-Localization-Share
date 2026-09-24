#!/usr/bin/env python3
"""Lossless context dump. Each language keeps its own order and duplicate IDs."""
import argparse
import json
from pathlib import Path
import sys
import localization_core as C
import versioned_sources as V


def render(obj,label):
    lines=['## '+label]
    for pos,rec in enumerate(C.records(obj)):
        speaker=rec.get('model',rec.get('speaker',rec.get('teller','旁白/未注明')))
        lines.append(f'--- pos={pos} identity={json.dumps(C.identity(rec),ensure_ascii=False)} speaker={speaker}')
        for path,logical,text,ambiguous in C.text_leaves(rec):
            lines.append(f'{C.pointer(["dataList",pos,*path])}: {text}')
    return lines


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('target',nargs='?'); ap.add_argument('--snapshot'); ap.add_argument('--batch')
    ap.add_argument('--out'); ap.add_argument('--list',action='store_true')
    args=ap.parse_args()
    batch=C.active_batch(args.batch,required=False)
    selected=args.snapshot or (C.load(batch/'batch.json')['new_snapshot'] if batch else C.state().get('baseline'))
    if not selected: raise C.DataError('无快照；请显式提供 --snapshot')
    root=Path(selected)
    if not root.is_absolute() and not root.exists(): root=C.KB/root
    root,m=V.snapshot(root)
    names=sorted(set().union(*(set(t) for t in m['languages'].values())))
    if args.list:
        print('\n'.join(names)); return 0
    if args.target not in names: raise C.DataError('指定文件不在快照中')
    lines=['# '+args.target,'各语言独立按原始顺序呈现；重复/空 id 不自动配对。修改使用完整字段路径。','']
    for lang in ('kr','en','jp','base'):
        lines.extend(render(V.read(root,m,lang,args.target),lang))
    if batch and (batch/'patch'/args.target).is_file():
        lines.extend(render(C.load(C.inside(batch/'patch',args.target)),'本批次中文'))
    text='\n'.join(lines)+'\n'
    if args.out: Path(args.out).write_text(text,encoding='utf-8'); print(f'已写出 {args.out}')
    else: print(text,end='')
    return 0


if __name__=='__main__':
    try: sys.exit(main())
    except (C.DataError,OSError) as exc:
        print(f'错误：{exc}',file=sys.stderr); sys.exit(2)
