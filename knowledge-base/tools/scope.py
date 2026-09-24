#!/usr/bin/env python3
"""Compare two verified source snapshots. Read-only unless --save is supplied."""
import argparse
import collections
from pathlib import Path
import sys
import localization_core as C
import versioned_sources as V


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--old', help='旧快照；默认 project.json 中的基线')
    ap.add_argument('--new', help='游戏更新后捕获的新快照')
    ap.add_argument('--save', metavar='REPORT_JSON', help='显式保存本次报告，零变化也更新')
    ap.add_argument('--top', type=int, default=30)
    ap.add_argument('--only', help='只展示指定文件名前缀；保存仍为完整报告')
    args = ap.parse_args()
    if not args.new:
        print('等待更新：尚未指定新快照；未扫描、未生成任务、未写入清单。')
        return 0
    previous = args.old or C.state().get('baseline')
    if not previous:
        raise C.DataError('缺少旧快照，不能判断本次变化；先 snapshot capture --set-baseline')
    previous = Path(previous)
    if not previous.is_absolute() and not previous.exists():
        previous = C.KB/previous
    report = V.plan(previous, args.new)
    files = [x for x in report['files'] if not args.only or x['file'].startswith(args.only)]
    print(f'本次原文变化：{len(report["files"])} 文件；历史未覆盖候选：{len(report["history"])} 字段（不自动入批次）')
    print(f'语言间字段差异：{len(report["language_differences"])} 文件（不是漏译结论）')
    for item in files[:args.top]:
        counts = collections.Counter(x['status'] for x in item['coverage'])
        print(f'{item["file"]}  源={item["source_language"]}  {dict(counts)}')
    if args.save:
        C.save(args.save, report)
        print(f'已保存完整报告：{args.save}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (C.DataError, OSError) as exc:
        print(f'错误：{exc}', file=sys.stderr); sys.exit(2)
