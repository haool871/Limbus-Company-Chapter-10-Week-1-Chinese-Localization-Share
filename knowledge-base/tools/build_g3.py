#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G3 组批量构建与校验：把 translate/_out/ 里已有的译文 TSV 全部合并成 JSON。

输出每个文件的 ✅/❌ 与「已译/总数」，最后汇总尚未完成的文件。

用法:
  python3 tools/build_g3.py            # 构建已有译文的文件并汇总
  python3 tools/build_g3.py --status   # 只看状态，不构建
"""
from __future__ import annotations

if __name__ == "__main__":
    raise SystemExit("旧批次入口已退役。请读 workflow/版本更新流程.md，使用 snapshot / scope / batch；不会写入旧目录。")


import json
import os
import subprocess
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_KB_DIR, "tools"))

OUT = os.path.join(_KB_DIR, "translate", "_out")
SKEL = os.path.join(_KB_DIR, "translate", "_skel")


def load_groups() -> list[str]:
    with open(os.path.join(_KB_DIR, "translate", "_groups.json"), encoding="utf-8") as fh:
        return json.load(fh)["G3"]


def skel_count(name: str) -> int:
    p = os.path.join(SKEL, name)
    return sum(1 for l in open(p, encoding="utf-8") if l.strip() and not l.startswith("#"))


def main(argv: list[str]) -> None:
    status_only = "--status" in argv
    groups = load_groups()
    done, todo = [], []
    for logical in groups:
        name = logical.replace("/", "__")[:-5] + ".tsv"
        tsv = os.path.join(OUT, name)
        n = skel_count(name)
        if not os.path.exists(tsv):
            todo.append((logical, n))
            continue
        if status_only:
            got = sum(1 for l in open(tsv, encoding="utf-8") if l.strip() and not l.startswith("#"))
            done.append((logical, got, n))
            continue
        r = subprocess.run(
            [sys.executable, os.path.join(_KB_DIR, "tools", "build_translation.py"), logical, tsv],
            capture_output=True, text=True)
        line = (r.stdout or "").strip().splitlines()
        head = next((l for l in line if l.startswith(("✅", "❌"))), "(无输出)")
        print(head)
        done.append((logical, 0, n))
    print()
    print(f"已完成 {len(done)} / {len(groups)}  剩余 {len(todo)}")
    if todo:
        print("未完成：")
        for logical, n in sorted(todo, key=lambda x: x[1]):
            print(f"   {n:5d}  {logical}")


if __name__ == "__main__":
    main(sys.argv)
