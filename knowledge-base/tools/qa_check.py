#!/usr/bin/env python3
"""Explicit source/translation check, or full version-bound batch validation."""
import sys
import localization_core as C
from verify_retrans import compare_file, main as batch_main


def main():
    if len(sys.argv)==3 and not sys.argv[1].startswith('--'):
        errors=compare_file(sys.argv[1],sys.argv[2])
        for error in errors: print(error)
        print(f'结构与标记问题 {len(errors)}；语义须另行审校')
        return 1 if errors else 0
    if '--official' in sys.argv:
        raise C.DataError('--official 已停用：它曾检查基础包而非新译文。使用 --batch，或显式提供源 JSON 与译文 JSON')
    return batch_main()


if __name__=='__main__':
    try: sys.exit(main())
    except (C.DataError,OSError) as exc:
        print(f'错误：{exc}',file=sys.stderr); sys.exit(2)
