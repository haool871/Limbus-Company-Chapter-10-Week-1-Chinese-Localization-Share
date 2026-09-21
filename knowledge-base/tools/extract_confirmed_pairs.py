#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从四语对齐语料中抽取「同现实证配对」，作为最高置信度的术语依据。

原理
    同一 (文件, id) 下，英文与中文同时存在，且**该记录本身很短**
    （英 ≤60 字符、中 ≤30 字符、英词数 ≤8），则这一对基本就是一条
    「英文原文 → 零协译文」的直接证据。出现 ≥2 次即认定为确认配对。

    这比「术语表条目 + 共现率」更强：它直接给出**零协实际怎么写**，
    不会像自动挖掘那样把 Section 4 配成「第4区段」（零协实际写「4科」）。

输出
    terms/confirmed_pairs.tsv   en<TAB>cn<TAB>出现次数<TAB>首个来源文件
    terms/_review/confirmed_stats.txt

用法
    python3 tools/extract_confirmed_pairs.py
    python3 tools/extract_confirmed_pairs.py --min-count 2
    python3 tools/extract_confirmed_pairs.py --query "Golden Bough"
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
TERMS = os.path.join(_KB, "terms")
CORPUS = os.path.join(_KB, "data", "corpus.jsonl")

WORD = re.compile(r"[A-Za-z][A-Za-z0-9'\-\.]*")
# 纯标点/省略号之类的「配对」无信息量
NOINFO = re.compile(r"^[\s\.…。，,、！？!?\-—《》()<>“”\"'\[\]{}|/\\+*~^%$#@&:;=]+$")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-count", type=int, default=2)
    ap.add_argument("--max-en-chars", type=int, default=60)
    ap.add_argument("--max-cn-chars", type=int, default=30)
    ap.add_argument("--max-words", type=int, default=8)
    ap.add_argument("--query")
    args = ap.parse_args()

    byid: dict[tuple, dict[str, list]] = collections.defaultdict(lambda: collections.defaultdict(list))
    with open(CORPUS, encoding="utf-8") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("l") not in ("en", "cn"):
                continue
            byid[(r["f"], r["id"])][r["l"]].append(r.get("t") or "")
    print(f"记录组 {len(byid)}")

    pairs = collections.Counter()
    src = {}
    for (f, _i), d in byid.items():
        ens, cns = d.get("en"), d.get("cn")
        if not ens or not cns:
            continue
        e = " ".join(ens).strip()
        c = " ".join(cns).strip()
        if not e or not c:
            continue
        if len(e) > args.max_en_chars or len(c) > args.max_cn_chars:
            continue
        if len(WORD.findall(e)) > args.max_words:
            continue
        if NOINFO.match(e) or NOINFO.match(c):
            continue
        if e == c:
            continue
        # ⚠️ en/cn 可能含真换行（多行文本）。若不转义，一条记录会横跨多行，
        # 直接破坏 TSV 结构（实测曾产生 207 行无制表符的碎片行）。
        e = e.replace("\r\n", "\\n").replace("\n", "\\n")
        c = c.replace("\r\n", "\\n").replace("\n", "\\n")
        pairs[(e, c)] += 1
        src.setdefault((e, c), f)

    conf = [(e, c, n) for (e, c), n in pairs.items() if n >= args.min_count]
    conf.sort(key=lambda x: -x[2])
    print(f"候选配对 {len(pairs)}，确认配对（≥{args.min_count} 次）{len(conf)}")

    if args.query:
        q = args.query.lower()
        print(f"\n===== 查询 {args.query!r} =====")
        for e, c, n in conf:
            if q in e.lower() or args.query in c:
                print(f"  x{n:<4} {e!r}  →  {c!r}")
        return 0

    with open(os.path.join(TERMS, "confirmed_pairs.tsv"), "w", encoding="utf-8") as fh:
        fh.write("# 同现实证配对：同一记录内中英直接对应（高置信）\n")
        fh.write("# en\tcn\tcount\tsource\n")
        for e, c, n in conf:
            fh.write(f"{e}\t{c}\t{n}\t{src[(e, c)]}\n")
    os.makedirs(os.path.join(TERMS, "_review"), exist_ok=True)
    with open(os.path.join(TERMS, "_review", "confirmed_stats.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"记录组 {len(byid)}\n候选配对 {len(pairs)}\n确认配对 {len(conf)}\n")
    print(f"\n已写出 terms/confirmed_pairs.tsv（{len(conf)} 条）")
    print("\n前 20 条示例：")
    for e, c, n in conf[:20]:
        print(f"  x{n:<4} {e!r:44} → {c!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
