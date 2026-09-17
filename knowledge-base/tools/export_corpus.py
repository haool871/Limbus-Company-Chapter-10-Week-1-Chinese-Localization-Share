#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导出全量四语对齐语料，并统计规模。

输出: _kb/data/corpus.jsonl
每行: {"f": 逻辑文件名, "l": 语言, "id": 记录id, "k": 字段名, "t": 文本}
"""
from __future__ import annotations

import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pm_lib import LANGS, iter_corpus, text_fields, record_key  # noqa: E402

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(_KB_DIR, "data", "corpus.jsonl")


def main() -> None:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    counts = collections.Counter()
    files = collections.Counter()
    n = 0
    with open(OUT, "w", encoding="utf-8") as fh:
        for logical, lang, rec in iter_corpus(LANGS):
            rid = record_key(rec) or ""
            fields = text_fields(rec)
            if not fields:
                continue
            files[(logical, lang)] += 1
            for k, v in fields.items():
                counts[lang] += 1
                n += 1
                fh.write(
                    json.dumps(
                        {"f": logical, "l": lang, "id": rid, "k": k, "t": v},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
    size = os.path.getsize(OUT)
    print(f"写入 {OUT}")
    print(f"总文本行: {n}  大小: {size/1e6:.1f} MB")
    print("各语言文本行数:", dict(counts))


if __name__ == "__main__":
    main()
