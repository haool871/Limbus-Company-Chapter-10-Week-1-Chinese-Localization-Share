#!/usr/bin/env python3
"""Compatibility entry point: validates the same explicit batch as verify_retrans."""
import sys
import localization_core as C
from verify_retrans import main

if __name__=='__main__':
    try: sys.exit(main())
    except (C.DataError,OSError) as exc:
        print(f'未通过/不适用：{exc}',file=sys.stderr); sys.exit(2)
