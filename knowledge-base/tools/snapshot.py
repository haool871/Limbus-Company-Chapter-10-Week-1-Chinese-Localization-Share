#!/usr/bin/env python3
"""Capture/verify official sources and Zero Association in immutable snapshots."""
import argparse
from pathlib import Path
import sys
import localization_core as C
import versioned_sources as V


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    cap = sub.add_parser('capture')
    cap.add_argument('--name', required=True)
    cap.add_argument('--game-root', default=str(C.GAME))
    cap.add_argument('--base')
    cap.add_argument('--game-version')
    cap.add_argument('--set-baseline', action='store_true')
    check = sub.add_parser('verify'); check.add_argument('path')
    args = ap.parse_args()
    if args.command == 'verify':
        root, manifest = V.snapshot(args.path)
        print(f'快照校验通过：{len(manifest["files"])} 文件；{root}')
        return 0
    s = C.state()
    if args.set_baseline and (s.get('active_batch') or s.get('baseline')):
        raise C.DataError('已有基线或活动批次；不能直接替换。完成批次后用 batch finish 推进基线')
    if not args.name or Path(args.name).name != args.name or args.name in ('.','..'):
        raise C.DataError('--name 必须是单个目录名')
    dest = C.KB/'snapshots'/args.name
    manifest = V.capture(dest, args.game_root, args.base, args.game_version)
    if args.set_baseline:
        C.save(C.KB/'project.json', {'schema':1,'phase':'waiting','baseline':str(dest.relative_to(C.KB)), 'active_batch':None})
    print(f'快照已保存：{dest}；{len(manifest["files"])} 文件；Steam build={manifest["steam_buildid"]}；无新翻译目录')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (C.DataError, OSError) as exc:
        print(f'错误：{exc}', file=sys.stderr); sys.exit(2)
