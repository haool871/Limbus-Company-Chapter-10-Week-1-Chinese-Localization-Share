#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 data/corpus.jsonl 汇成 (f,id,k) -> {lang: text} 的四语对齐索引，缓存到 data/_align.pkl。

用法:
  python3 tools/align_index.py build
  python3 tools/align_index.py probe <正则> [--maxlen N] [--limit N] [--files f1,f2]
  python3 tools/align_index.py kr <中文词>          # 由中文反查英/韩
  python3 tools/align_index.py en '<英文词>'        # 由英文正查中/韩
"""
from __future__ import annotations

import json
import os
import pickle
import re
import sys

KB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(KB, "data", "corpus.jsonl")
CACHE = os.path.join(KB, "data", "_align.pkl")
LANGS = ("cn", "kr", "en", "jp")


def build() -> dict:
    idx: dict[tuple, dict[str, str]] = {}
    with open(CORPUS, encoding="utf-8") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except Exception:
                continue
            key = (r["f"], r["id"], r["k"])
            idx.setdefault(key, {})[r["l"]] = r["t"]
    with open(CACHE, "wb") as fh:
        pickle.dump(idx, fh, protocol=4)
    return idx


def load() -> dict:
    if not os.path.exists(CACHE):
        return build()
    with open(CACHE, "rb") as fh:
        return pickle.load(fh)


def fmt(f, i, k, d, langs=("en", "cn", "kr", "jp")):
    parts = [f"{L.upper()}={d[L]}" for L in langs if L in d]
    return f"[{f} #{i} .{k}]\n  " + "\n  ".join(parts)


def probe(rx: str, field: str, maxlen: int, limit: int, files: list[str] | None):
    idx = load()
    pat = re.compile(rx)
    n = 0
    for (f, i, k), d in idx.items():
        if files and not any(x.lower() in f.lower() for x in files):
            continue
        t = d.get(field)
        if not t or len(t) > maxlen or not pat.search(t):
            continue
        print(fmt(f, i, k, d))
        n += 1
        if n >= limit:
            break
    print(f"--- 命中 {n} 条（上限 {limit}）", file=sys.stderr)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return
    cmd = argv[1]
    if cmd == "build":
        idx = build()
        print(f"对齐键 {len(idx)} 个")
        return
    rx = argv[2]
    maxlen, limit, files, field = 80, 30, None, "en"
    a = argv[3:]
    for j, x in enumerate(a):
        if x == "--maxlen":
            maxlen = int(a[j + 1])
        elif x == "--limit":
            limit = int(a[j + 1])
        elif x == "--files":
            files = a[j + 1].split(",")
        elif x == "--field":
            field = a[j + 1]
    probe(rx, field, maxlen, limit, files)


if __name__ == "__main__":
    main(sys.argv)
