#!/usr/bin/env python3
"""旧自动合并器已退役。仅应用经过范围审核的显式字段清单，支持完整字节回滚。"""
import argparse
import json
import sys
import localization_core as C
import batch_ops as B


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--batch')
    ap.add_argument('--edits',help='同 batch apply 的显式编辑清单；不会自动采用上游字符串')
    ap.add_argument('--apply',action='store_true')
    ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--revert',metavar='TRANSACTION_ID')
    args=ap.parse_args()
    if args.apply and args.dry_run: raise C.DataError('--apply 与 --dry-run 互斥')
    if args.revert and (args.edits or args.apply or args.dry_run): raise C.DataError('回滚不能与编辑混用')
    batch=C.active_batch(args.batch)
    if args.revert:
        result=B.rollback(batch,args.revert)
    elif args.edits:
        result=B.apply(batch,C.load(args.edits),dry_run=not args.apply)
    else:
        raise C.DataError('自动合并旧补丁已停用；先按新旧原文确定批次，再提供 --edits。默认只预览')
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0


if __name__=='__main__':
    try: sys.exit(main())
    except (C.DataError,OSError,KeyError,TypeError) as exc:
        print(f'错误：{exc}',file=sys.stderr); sys.exit(2)
