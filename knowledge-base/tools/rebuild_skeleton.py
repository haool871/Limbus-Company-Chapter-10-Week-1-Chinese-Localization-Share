#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按官方英文 JSON 重建 G3 组的骨架 TSV（id<TAB>字段路径<TAB>英文原文）。

用途：`translate/RPGSystem__*.tsv` 既是骨架又是输出，误覆盖后可从英文源重建。
输出到 `_kb/translate/_skel/<同名>.tsv`，不碰原始文件。

行序规则：严格按 dataList 顺序 → 每条记录的字符串叶子深度优先顺序，
与 `build_translation.py` 的 walk_strings 一致（脚本内已用未受损骨架校验）。
"""
from __future__ import annotations

import json
import os
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_KB_DIR, "tools"))
import pm_lib as P  # noqa: E402

DEV_FIELDS = {"id", "key", "_id", "coindescs_index", "index", "level",
              "coinindex", "subIndex"}


def walk_strings(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str):
                yield (f"{path}.{k}" if path else k), v
            elif isinstance(v, (dict, list)):
                yield from walk_strings(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            p = f"{path}[{i}]"
            if isinstance(v, str):
                yield p, v
            elif isinstance(v, (dict, list)):
                yield from walk_strings(v, p)


def skeleton_rows(logical: str):
    idx = P.build_index()
    en_path = os.path.join(P.LANG_DIR["en"], idx[logical]["en"])
    with open(en_path, encoding="utf-8") as fh:
        data = json.load(fh)
    recs = data["dataList"] if isinstance(data, dict) and "dataList" in data else data
    rows = []
    for rec in recs:
        if not isinstance(rec, dict):
            continue
        rid = str(rec.get("id", rec.get("key", rec.get("_id", ""))))
        for path, val in walk_strings(rec):
            if not val.strip():
                continue
            leaf = path.split(".")[-1].split("[")[0]
            if leaf in DEV_FIELDS:
                continue
            rows.append((rid, path, val.replace("\n", "\\n")))
    return rows


def main(argv: list[str]) -> None:
    out_dir = os.path.join(_KB_DIR, "translate", "_skel")
    os.makedirs(out_dir, exist_ok=True)
    logicals = argv[1:]
    if not logicals:
        groups = json.load(open(os.path.join(_KB_DIR, "translate", "_groups.json"),
                                encoding="utf-8"))
        logicals = groups["G3"]
    for logical in logicals:
        rows = skeleton_rows(logical)
        name = logical.replace("/", "__")[:-5] + ".tsv"
        dest = os.path.join(out_dir, name)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(f"# {logical}  骨架（重建）\n")
            for rid, path, val in rows:
                fh.write(f"{rid}\t{path}\t{val}\n")
        print(f"  {name}: {len(rows)} 行")


if __name__ == "__main__":
    main(sys.argv)
