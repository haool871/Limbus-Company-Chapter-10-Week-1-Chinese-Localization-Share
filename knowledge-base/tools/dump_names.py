#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从四语对齐索引里抽取专名行（name/content/title 字段），输出 TSV 供人工筛选。"""
from __future__ import annotations

import os
import pickle
import sys

KB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(KB, "data", "_align.pkl")


def main() -> None:
    idx = pickle.load(open(CACHE, "rb"))
    fpats = sys.argv[1].split(",") if len(sys.argv) > 1 else [""]
    keys = sys.argv[2].split(",") if len(sys.argv) > 2 else ["name", "content"]
    rows = []
    for (f, i, k), d in sorted(idx.items()):
        if not any(p.lower() in f.lower() for p in fpats):
            continue
        if k not in keys:
            continue
        en = (d.get("en") or "").strip()
        if not en or len(en) > 60 or "\n" in en:
            continue
        rows.append((en, (d.get("cn") or "").strip(), (d.get("kr") or "").strip(),
                     f"{f}#{i}"))
    for r in rows:
        print("\t".join(r))
    print(f"--- {len(rows)} 行", file=sys.stderr)


if __name__ == "__main__":
    main()
