#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为 G7 的 UserBanner-* / UserTicket-* 生成译文表。

这些文件的内容与既有 UserBanner.json / UserTicket-{L,R,EGOBg}.json 的对应 id 完全相同，
因此直接沿用既有汉化（EN->CN 权威映射），确保跨赛季一致；无既有译文的 ?? 占位保持原样。
"""
from __future__ import annotations

import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pm_lib as P  # noqa: E402

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TR = os.path.join(_KB_DIR, "translate")

# 目标文件 -> 取映射的基准文件
TARGETS = {
    "UserBanner-a1c7p3": "UserBanner.json",
    "UserBanner-a1c8p1": "UserBanner.json",
    "UserTicket-L-a1c7p3": "UserTicket-L.json",
    "UserTicket-L-a1c8p1": "UserTicket-L.json",
    "UserTicket-L-a1c10p1": "UserTicket-L.json",
    "UserTicket-R-a1c7p3": "UserTicket-R.json",
    "UserTicket-R-a1c8p1": "UserTicket-R.json",
    "UserTicket-R-a1c10p1": "UserTicket-R.json",
    "UserTicket-EGOBg-a1c7p3": "UserTicket-EGOBg.json",
    "UserTicket-EGOBg-a1c8p1": "UserTicket-EGOBg.json",
    "UserTicket-EGOBg-a1c10p1": "UserTicket-EGOBg.json",
}


def build_maps() -> dict[str, dict[str, dict[str, str]]]:
    """{基准文件: {en_name: {name,desc}}}"""
    out = {}
    for base in set(TARGETS.values()):
        A = P.align(base)
        en = {r["_id"]: r for r in A.get("en", [])}
        cn = {r["_id"]: r for r in A.get("cn", [])}
        m = {}
        for k, er in en.items():
            cr = cn.get(k)
            if not cr:
                continue
            m[er.get("name", "")] = {"name": cr.get("name", ""), "desc": cr.get("desc", "")}
        out[base] = m
    return out


def main() -> None:
    maps = build_maps()
    for target, base in TARGETS.items():
        src = os.path.join(P.LANG_DIR["en"], P.build_index()[f"{target}.json"]["en"])
        with open(src, encoding="utf-8") as fh:
            data = json.load(fh)
        rows = []
        rows.append(f"# {target}.json  译文表：把第三列替换为中文（沿用既有汉化）")
        miss = 0
        for rec in data["dataList"]:
            rid = str(rec["id"])
            en_name = rec.get("name", "")
            m = maps[base].get(en_name)
            for field in ("name", "desc"):
                if field not in rec:
                    continue
                if m and m.get(field):
                    val = m[field]
                else:
                    val = rec[field]
                    miss += 1
                rows.append(f"{rid}\t{field}\t{val}")
        out = os.path.join(TR, f"{target}.tsv")
        with io.open(out, "w", encoding="utf-8") as fh:
            fh.write("\n".join(rows) + "\n")
        print(f"{target}.tsv  行={len(rows)-1}  未匹配字段={miss}")


if __name__ == "__main__":
    main()
