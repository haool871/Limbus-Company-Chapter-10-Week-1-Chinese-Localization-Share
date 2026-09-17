#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把风格指南里未展开的引用标记还原成真实的中英例句。

标记格式: @@<韩文model>|<文件相对路径>|<id或序号>@@
还原为:
  - **EN**: <英文原文>
  - **CN**: <零协会中文>

用法:
  python3 resolve_citations.py style/角色/辛克莱.md
  python3 resolve_citations.py --all          # 处理 style/角色/*.md
"""
from __future__ import annotations

import os
import re
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_KB_DIR, "tools"))
import pm_lib as P  # noqa: E402

TOKEN = re.compile(r"@@([^@|]+)\|([^@|]+)\|([^@]+)@@")


def resolve(logical: str, rid: str):
    """返回 (en, cn) 文本对；找不到返回 (None, None)。"""
    logical = logical.replace("\\", "/")
    A = P.align(logical)
    en, cn = A.get("en", []), A.get("cn", [])
    by_id = {r["_id"]: r for r in en}
    rec = by_id.get(rid)
    if rec is None:
        try:
            i = int(rid)
        except ValueError:
            return None, None
        if 0 <= i < len(en):
            rec = en[i]
        else:
            return None, None
    crec = next((r for r in cn if r["_id"] == rec["_id"]), None)
    if crec is None:
        return None, None
    pick = ("content", "dlg", "desc", "name", "text", "story", "title", "flavor")
    def first(r):
        for f in pick:
            v = r.get(f)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return None
    return first(rec), first(crec)


def process(path: str) -> tuple[int, int]:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    ok = fail = 0

    def repl(m: re.Match) -> str:
        nonlocal ok, fail
        _model, logical, rid = m.group(1), m.group(2), m.group(3)
        en, cn = resolve(logical, rid)
        if not en or not cn:
            fail += 1
            return f"`[{logical}#{rid}]`（原引用未找到）"
        ok += 1
        return (f"\n  - **EN**: {en}\n  - **CN**: {cn}")

    new = TOKEN.sub(repl, text)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new)
    return ok, fail


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print(__doc__)
        return
    if argv[1] == "--all":
        d = os.path.join(_KB_DIR, "style", "角色")
        paths = [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".md")]
    else:
        paths = argv[1:]
    total_ok = total_fail = 0
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            if "@@" not in fh.read():
                print(f"跳过（无标记）: {os.path.basename(p)}")
                continue
        ok, fail = process(p)
        total_ok += ok
        total_fail += fail
        print(f"{os.path.basename(p)}: 还原 {ok} 处，失败 {fail} 处")
    print(f"合计 还原 {total_ok}，失败 {total_fail}")


if __name__ == "__main__":
    main(sys.argv)
