#!/usr/bin/env python3
"""Validate the version-bound active batch; an absent batch is not a pass."""
import argparse
import json
from pathlib import Path
import sys
import localization_core as C
import batch_ops as B


def compare_file(source, target, display_brackets=()):
    src=C.load(source); dst=C.load(target)
    C.records(src); C.records(dst)
    expected=C.units(src)
    editable={tuple(u['path']) for u in expected.values()}
    errors=C.compare_structure(src,dst,editable)
    for unit in expected.values():
        try: text=C.get(dst,unit['path'])
        except (KeyError,IndexError,TypeError): continue
        if isinstance(text,str):
            errors.extend(C.pointer(unit['path'])+': '+x for x in C.text_errors(unit['text'],text,display_brackets))
    return errors


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('target',nargs='?')
    ap.add_argument('--batch')
    ap.add_argument('--all',action='store_true',help='兼容旧调用；始终检查完整批次')
    ap.add_argument('--source',help='显式源 JSON，仅做结构与标记检查')
    ap.add_argument('--translation',help='显式译文 JSON')
    args=ap.parse_args()
    if args.source or args.translation:
        if not args.source or not args.translation:
            raise C.DataError('--source 与 --translation 必须同时提供')
        errors=compare_file(args.source,args.translation)
        print(json.dumps({'errors':errors,'scope':'结构与标记；不代表语义已审校'},ensure_ascii=False,indent=2))
        return 1 if errors else 0
    batch=C.active_batch(args.batch)
    if args.target and args.target not in C.load(batch/'batch.json')['files']:
        raise C.DataError('指定文件不在本批次')
    with B.lock(batch): result=B.verify(batch)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    print('批次验收通过（语义依据为人工审校记录）' if not result['errors'] else '批次验收未通过')
    return 1 if result['errors'] else 0


if __name__=='__main__':
    try: sys.exit(main())
    except (C.DataError,OSError) as exc:
        print(f'未通过/不适用：{exc}',file=sys.stderr); sys.exit(2)
