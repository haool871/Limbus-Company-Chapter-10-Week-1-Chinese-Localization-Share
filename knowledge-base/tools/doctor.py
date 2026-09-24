#!/usr/bin/env python3
"""Read-only project readiness: waiting, active and archived are distinct states."""
import argparse
import sys
import localization_core as C
import versioned_sources as V


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--quick',action='store_true',help='省略快照全量哈希检查')
    args=ap.parse_args()
    s=C.state(); problems=[]
    print(f'项目状态：{s["phase"]}')
    baseline=s.get('baseline')
    if baseline:
        p=C.KB/baseline
        manifest=C.load(p/'manifest.json') if args.quick else V.snapshot(p)[1]
        print(f'基线：{p}\n零协版本：{manifest["zeroasso_version"]}；Steam build：{manifest.get("steam_buildid")}')
        print('快照：仅检查清单（quick）' if args.quick else f'快照：{len(manifest["files"])} 文件哈希通过')
    else:
        problems.append('尚未冻结官方原文基线')
    if s.get('active_batch'):
        batch=C.active_batch()
        meta=C.load(batch/'batch.json')
        print(f'活动批次：{batch}；预期 {len(meta["files"])} 文件。验收请运行 batch verify')
    else:
        if s.get('phase')!='waiting': problems.append('状态与活动批次不一致')
        print('等待游戏更新；没有修改源。译文验收不适用（未执行），无需创建空目录。')
    for rel in ['terms/confirmed_pairs.tsv','terms/glossary_all.clean.tsv','terms/术语表.md']:
        if not (C.KB/rel).is_file(): problems.append(f'参考资料缺失: {rel}')
    for error in problems: print('问题：'+error)
    print('准备检查完成；不代表译文或游戏加载通过')
    return 1 if problems else 0


if __name__=='__main__':
    try: sys.exit(main())
    except (C.DataError,OSError) as exc:
        print(f'错误：{exc}',file=sys.stderr); sys.exit(2)
