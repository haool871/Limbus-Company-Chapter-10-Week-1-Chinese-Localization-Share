#!/usr/bin/env python3
"""Create, edit, verify, export and archive an explicitly scoped translation batch."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import localization_core as C
import batch_ops as B


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest='command',required=True)
    sub.add_parser('status')
    create=sub.add_parser('create'); create.add_argument('--name',required=True); create.add_argument('--report',required=True); create.add_argument('--decisions')
    for name in ('apply','verify','rollback','finish','export'):
        p=sub.add_parser(name); p.add_argument('--batch')
        if name=='apply': p.add_argument('--edits',required=True); p.add_argument('--dry-run',action='store_true')
        if name=='rollback': p.add_argument('--transaction',required=True)
        if name=='export': p.add_argument('--out',required=True)
    args=ap.parse_args()
    if args.command=='status':
        print(json.dumps(C.state(),ensure_ascii=False,indent=2)); return 0
    if args.command=='create':
        if C.state().get('active_batch'):
            raise C.DataError('已有活动批次；先完成或处理该批次')
        if Path(args.name).name!=args.name or args.name in ('.','..'):
            raise C.DataError('批次名必须是单个目录名')
        dest=C.KB/'batches'/args.name
        report=C.load(args.report)
        meta=B.create(dest,report,C.load(args.decisions) if args.decisions else None)
        s=C.state(); s.update(phase='active',active_batch=str(dest.relative_to(C.KB)))
        C.save(C.KB/'project.json',s)
        print(f'已创建批次 {dest}；{len(meta["files"])} 文件'); return 0
    batch=C.active_batch(args.batch)
    if args.command=='apply':
        print(json.dumps(B.apply(batch,C.load(args.edits),args.dry_run),ensure_ascii=False)); return 0
    if args.command=='rollback':
        print(json.dumps(B.rollback(batch,args.transaction),ensure_ascii=False)); return 0
    with B.lock(batch):
        result=B.verify(batch)
        if args.command=='verify' or result['errors']:
            print(json.dumps(result,ensure_ascii=False,indent=2)); return 1 if result['errors'] else 0
        if args.command=='export':
            out=Path(args.out).resolve()
            if out.exists(): raise C.DataError('交付目录已存在，拒绝混入旧文件')
            shutil.copytree(batch/'patch',out/'patch')
            meta=C.load(batch/'batch.json')
            C.save(out/'delivery.json',{'batch':str(batch),'snapshot':meta['new_snapshot'],
                   'files':{r:C.file_hash(C.inside(out/'patch',r)) for r in meta['files']},
                   'retired':meta['retired'],'excluded':meta['excluded'],'validation':result})
            print(f'已生成本地交付目录：{out}；未安装或发布'); return 0
        s=C.state()
        if not s.get('active_batch') or C.active_batch()!=batch:
            raise C.DataError('只能完成 project.json 指向的活动批次')
        meta=C.load(batch/'batch.json')
        dest=C.KB/'archives'/('batch_'+batch.name)
        if dest.exists(): raise C.DataError('归档目标已存在')
        C.save(batch/'validation.json',result)
        meta['status']='archived'; C.save(batch/'batch.json',meta)
        dest.parent.mkdir(parents=True,exist_ok=True); batch.rename(dest)
        s.update(phase='waiting',active_batch=None,baseline=meta['new_snapshot'],last_batch=str(dest.relative_to(C.KB)))
        C.save(C.KB/'project.json',s)
        print(f'批次已归档：{dest}；基线已推进，回到等待更新'); return 0


if __name__=='__main__':
    try: sys.exit(main())
    except (C.DataError,OSError,KeyError,TypeError) as exc:
        print(f'错误：{exc}',file=sys.stderr); sys.exit(2)
