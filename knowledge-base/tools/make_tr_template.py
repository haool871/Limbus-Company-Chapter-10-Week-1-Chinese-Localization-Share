#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为某个官方英文文件生成译文表骨架（含嵌套路径），供填写中文。

用法:
  python3 make_tr_template.py <逻辑名> [-o 输出tsv]
  例: python3 make_tr_template.py StoryData/S1002B.json
      → translate/StoryData__S1002B.tsv

骨架每行: id <TAB> 路径 <TAB> 英文原文（原文中的换行写成 \\n）
翻译时把第三列替换为中文即可；未翻译的行保持原样(英文)不影响交付（但会记为未译）。
"""
from __future__ import annotations

import json
import os
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_KB_DIR, "tools"))
import pm_lib as P  # noqa: E402
from build_translation import DEV_FIELDS, walk_strings  # noqa: E402

TR_DIR = os.path.join(_KB_DIR, "translate")


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print(__doc__)
        return
    logical = argv[1].replace("__", "/")
    out = None
    if "-o" in argv:
        out = argv[argv.index("-o") + 1]
    idx = P.build_index()
    if logical not in idx or "en" not in idx[logical]:
        raise SystemExit(f"找不到英文源文件: {logical}")
    recs = P.load_file("en", idx[logical]["en"])
    if out is None:
        os.makedirs(TR_DIR, exist_ok=True)
        out = os.path.join(TR_DIR, logical.replace("/", "__")[:-5] + ".tsv")
    skip_fields: set[str] = set()
    if os.path.exists(out + ".skip"):
        with open(out + ".skip", encoding="utf-8") as fh:
            skip_fields = {ln.strip() for ln in fh if ln.strip()}
    n = 0
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(f"# {logical}  译文表：把第三列替换为中文\n")
        for rec in recs:
            rid = str(rec.get("id", rec.get("key", "")))
            for path, val in walk_strings(rec):
                if not val.strip():
                    continue
                leaf = path.split(".")[-1].split("[")[0]
                if leaf in DEV_FIELDS or leaf in skip_fields:
                    continue
                fh.write(f"{rid}\t{path}\t{val.replace(chr(10), chr(92)+'n')}\n")
                n += 1
    print(f"写出 {out}（{n} 条待译）")


if __name__ == "__main__":
    main(sys.argv)
