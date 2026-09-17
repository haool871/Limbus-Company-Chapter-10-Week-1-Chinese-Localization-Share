#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""术语候选频率加权与生成。

思路（避免 O(候选数 × 语料行数)）:
  en 侧：把语料 tokenize 成 1..4-gram 计数，术语直接查表；
  cn 侧：统计每条中文文本被引用次数，对候选做子串计数（候选数有限）。

输出:
  _kb/terms/glossary_ranked.tsv   en<TAB>cn<TAB>en_hits<TAB>cn_hits<TAB>source<TAB>id
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(_KB_DIR, "data", "corpus.jsonl")
CAND = os.path.join(_KB_DIR, "terms", "candidates.tsv")
OUT = os.path.join(_KB_DIR, "terms", "glossary_ranked.tsv")

TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-\.]*")


def main() -> None:
    en_gram: collections.Counter = collections.Counter()
    cn_texts: collections.Counter = collections.Counter()
    for line in open(CORPUS, encoding="utf-8"):
        r = json.loads(line)
        t = r["t"]
        if r["l"] == "en":
            toks = TOKEN.findall(t)
            low = [w.lower() for w in toks]
            for n in (1, 2, 3, 4):
                for i in range(len(low) - n + 1):
                    en_gram[" ".join(low[i:i + n])] += 1
        elif r["l"] == "cn":
            cn_texts[t] += 1
    print("en n-gram 词表:", len(en_gram), " cn 唯一文本:", len(cn_texts))

    cn_items = list(cn_texts.items())
    rows = []
    for line in open(CAND, encoding="utf-8"):
        if line.startswith("#"):
            continue
        p = line.rstrip("\n").split("\t")
        if len(p) < 2:
            continue
        en, cn = p[0], p[1]
        en_hits = en_gram.get(en.lower().strip(), 0)
        cn_hits = sum(c for t, c in cn_items if cn in t)
        rows.append((en, cn, en_hits, cn_hits, p[2] if len(p) > 2 else "", p[3] if len(p) > 3 else ""))

    rows.sort(key=lambda r: -(r[2] + r[3]))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("# en\tcn\ten_hits\tcn_hits\tsource\tid\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print("写出", OUT, len(rows))
    print("\n=== top 60 ===")
    for r in rows[:60]:
        print(f"{r[2]:5d} {r[3]:5d} | {r[0][:40]:40s} | {r[1][:20]:20s} | {r[4]}")


if __name__ == "__main__":
    main()
