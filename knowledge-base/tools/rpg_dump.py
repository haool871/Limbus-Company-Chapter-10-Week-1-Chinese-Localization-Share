#!/usr/bin/env python3
"""RPG context entry point; retain every group, speaker, index and field path."""
import sys
import localization_core as C
from ctx_dump import main
if __name__=='__main__':
    try: sys.exit(main())
    except (C.DataError,OSError) as exc:
        print(f'错误：{exc}',file=sys.stderr); sys.exit(2)
