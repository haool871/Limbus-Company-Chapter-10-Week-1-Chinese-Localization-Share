#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核对补丁是否使用了零协会的既有译法。

做法：
  1. 从零协基础包（英中同 id 对齐）提取「英文术语 → 零协中文」对照，
     只保留「短英文 ↔ 短中文」的条目（术语/专名），且出现 ≥2 次；
  2. 从补丁的官方英文源中，一次性收集所有「命中的术语」；
  3. 逐个检查补丁中文是否含该术语的零协译法（去空格比较）。

输出: /tmp/term_report.txt
"""
from __future__ import annotations

import collections
import json
import os
import re

BASE = "LimbusLocalize_latest/LimbusCompany_Data/Lang/LLC_zh-CN"
EN = ("/home/shb/.local/share/Steam/steamapps/common/Limbus Company/"
      "LimbusCompany_Data/Assets/Resources_moved/Localize/en")
PATCH = "_kb/patch_v2"
CJK = re.compile(r"[\u4e00-\u9fff]")


def ns(s: str) -> str:
    return re.sub(r"[\s\u3000]", "", s)


def walk(root, strip_en=False):
    out = {}
    for dp, _dn, fn in os.walk(root):
        for f in fn:
            if not f.endswith(".json"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), root)
            if strip_en:
                d, b = os.path.split(rel)
                if b.startswith("EN_"):
                    b = b[3:]
                rel = os.path.join(d, b) if d else b
            out[rel] = os.path.join(dp, f)
    return out


def main() -> None:
    base = walk(BASE)
    en = walk(EN, strip_en=True)

    # 1) 建对照
    agg: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for rel, bp in base.items():
        ep = en.get(rel)
        if not ep:
            continue
        try:
            cn = json.load(open(bp, encoding="utf-8-sig")).get("dataList", [])
            e = json.load(open(ep, encoding="utf-8-sig")).get("dataList", [])
        except Exception:
            continue
        cm = {str(r.get("id", r.get("key"))): r for r in cn if isinstance(r, dict)}
        for r in e:
            if not isinstance(r, dict):
                continue
            c = cm.get(str(r.get("id", r.get("key"))))
            if not c:
                continue
            for k in ("name", "content", "displayName", "title"):
                ev, cv = r.get(k), c.get(k)
                if not (isinstance(ev, str) and isinstance(cv, str)):
                    continue
                if not CJK.search(cv):
                    continue
                evs, cvs = ev.strip(), cv.strip()
                if 3 <= len(evs) <= 24 and 2 <= len(cvs) <= 14 and "\n" not in evs:
                    agg[evs][cvs] += 1

    # 只保留出现≥2次、且英文够独特的术语
    terms = {}
    for e, c in agg.items():
        total = sum(c.values())
        if total < 2:
            continue
        terms[e] = c.most_common(1)[0][0]
    print(f"零协既有术语对照: {len(terms)} 条", flush=True)

    # 2) 预编译：按长度降序，命中即止
    ordered = sorted(terms.items(), key=lambda x: -len(x[0]))
    pats = [(e, z, re.compile(r"(?<![A-Za-z0-9])" + re.escape(e) + r"(?![A-Za-z0-9])"))
            for e, z in ordered]

    # 3) 扫补丁
    issues: dict[tuple[str, str], list] = collections.defaultdict(list)
    patch = walk(PATCH)
    for rel, pp in patch.items():
        ep = en.get(rel)
        if not ep:
            continue
        try:
            cn = json.load(open(pp, encoding="utf-8-sig")).get("dataList", [])
            e = json.load(open(ep, encoding="utf-8-sig")).get("dataList", [])
        except Exception:
            continue
        cm = {str(r.get("id", r.get("key"))): r for r in cn if isinstance(r, dict)}
        for r in e:
            if not isinstance(r, dict):
                continue
            c = cm.get(str(r.get("id", r.get("key"))))
            if not c:
                continue
            for k in ("name", "content", "displayName", "title", "desc", "text"):
                ev, cv = r.get(k), c.get(k)
                if not (isinstance(ev, str) and isinstance(cv, str)):
                    continue
                if not CJK.search(cv):
                    continue
                cvn = ns(cv)
                for term, zh, rx in pats:
                    if rx.search(ev):
                        if ns(zh) not in cvn:
                            issues[(term, zh)].append((rel, str(r.get("id")), k, ev[:60], cv[:60]))
                        break

    with open("/tmp/term_report.txt", "w", encoding="utf-8") as fh:
        fh.write(f"不一致术语: {len(issues)}\n")
        for (term, zh), v in sorted(issues.items(), key=lambda x: -len(x[1])):
            fh.write(f"\n【{term}】零协=「{zh}」({len(v)}处)\n")
            fh.write(f"   EN: {v[0][3]}\n   CN: {v[0][4]}\n")
    print(f"不一致术语: {len(issues)}  → /tmp/term_report.txt", flush=True)


if __name__ == "__main__":
    main()
