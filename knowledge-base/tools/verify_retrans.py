#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重译成品校验：一次性检查结构、标签、空译、第一人称、禁用语。

这是重译流程的守门工具（见 workflow/重译手册.md §5）。

用法
    python3 tools/verify_retrans.py StoryData/S1002B.json
    python3 tools/verify_retrans.py --all-story        # 全部剧情文件
    python3 tools/verify_retrans.py StoryData/S1002B.json --verbose
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
PATCH = os.path.join(_KB, "patch_v2")
GAME = os.environ.get("LIMBUS_GAME_ROOT", "/home/shb/.local/share/Steam/steamapps/common/Limbus Company")
LOC = os.path.join(GAME, "LimbusCompany_Data", "Assets", "Resources_moved", "Localize")

# 必须逐字符保留的标签（可选的 <i>/<b>/<u>/<s> 不在内）
MUST_TAG = re.compile(r"</?(?:color|size|style|mark)(?:=[^>]*)?>", re.I)
ALL_TAG = re.compile(r"</?(?:i|b|u|s|color|size|style|mark)(?:=[^>]*)?>", re.I)
PLACEHOLDER = re.compile(r"\{[^}]*\}")
ENGINE_BRACKET = re.compile(r"\[[A-Za-z_][A-Za-z0-9_]*\]")

# 禁用语：这些写法在零协语料中对特定角色/全局都不成立
FP_MARK = re.compile(r"\b(I|I'm|I've|I'd|I'll|my|me|myself|mine)\b")

BANNED = ["黄金枝", "辣喊助威", "第4区段", "攻击等级强化", "防御等级强化", "守备威力强化", "提振士气", "星芒奖励"]


def load(p):
    try:
        with open(p, encoding="utf-8-sig") as fh:
            return json.load(fh).get("dataList") or []
    except Exception:
        return []


def walk(o, skip=("id", "model", "teller")):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            if k in skip:
                continue
            yield from walk(v, skip)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v, skip)


def src_path(rel, lang, pre):
    d, f = os.path.split(rel)
    for c in (pre + f, f):
        p = os.path.join(LOC, lang, d, c)
        if os.path.exists(p):
            return p
    return None


def check_one(rel, verbose=False):
    p = os.path.join(PATCH, rel)
    if not os.path.exists(p):
        return None, [f"文件不存在: {rel}"]
    cn = load(p)
    ep = src_path(rel, "en", "EN_")
    kp = src_path(rel, "kr", "KR_")
    en = load(ep) if ep else []
    kr = load(kp) if kp else []
    errs, warns = [], []

    # 结构
    if en:
        if len(cn) != len(en):
            errs.append(f"记录数不符: CN={len(cn)} EN={len(en)}")
        kc = collections.Counter(tuple(sorted(r.keys())) for r in cn if isinstance(r, dict))
        ke = collections.Counter(tuple(sorted(r.keys())) for r in en if isinstance(r, dict))
        if kc != ke:
            errs.append(f"键集合不一致: CN={dict(kc)} EN={dict(ke)}")
        if [r.get("id") for r in cn] != [r.get("id") for r in en]:
            errs.append("id 序列与英文源不一致")

    en_by_id = collections.defaultdict(list)
    for r in en:
        if isinstance(r, dict):
            en_by_id[str(r.get("id"))].append(r)

    first_person = 0
    for r in cn:
        if not isinstance(r, dict):
            continue
        rid = str(r.get("id"))
        txt = r.get("content") or ""
        # 标签
        ens = en_by_id.get(rid, [])
        en_txt = " ".join(x for e in ens for x in walk(e) if isinstance(x, str))
        if en_txt:
            if sorted(MUST_TAG.findall(txt)) != sorted(MUST_TAG.findall(en_txt)):
                errs.append(f"id={rid} 必须保留标签不一致")
            if sorted(PLACEHOLDER.findall(txt)) != sorted(PLACEHOLDER.findall(en_txt)):
                errs.append(f"id={rid} 占位符不一致")
        # 空译
        if not txt.strip() and en_txt.strip():
            errs.append(f"id={rid} 空译（英文有内容）")
        # 禁用语
        for b in BANNED:
            if b in txt:
                errs.append(f"id={rid} 含禁用语「{b}」")
        # 但丁旁白是**第一人称**（见 style/叙事与旁白.md §3）。
        # 英文出现第一人称标记时，中文必须让「我」可见，否则叙述会失去视角。
        # 已知漏译模式：my vision→「映入眼帘」、that dress→「那条裙」、I guess→「原来」。
        if not r.get("model") and en_txt:
            hits = FP_MARK.findall(en_txt)
            if hits and "我" not in txt:
                warns.append(
                    f"id={rid} 但丁旁白漏第一人称（EN 含 {','.join(sorted(set(hits)))}）: {txt[:50]}")
            elif hits:
                first_person += 1

    return {"rel": rel, "records": len(cn), "first_person": first_person}, errs, warns


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?")
    ap.add_argument("--all-story", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if args.all_story:
        targets = [os.path.relpath(os.path.join(dp, f), PATCH)
                   for dp, _dn, fn in os.walk(os.path.join(PATCH, "StoryData"))
                   for f in sorted(fn) if f.endswith(".json")]
    elif args.target:
        targets = [args.target]
    else:
        ap.error("需要指定文件或 --all-story")

    total_err = total_warn = 0
    for rel in targets:
        info, errs, warns = check_one(rel, args.verbose)
        if info is None:
            print(f"❌ {errs[0]}")
            total_err += 1
            continue
        mark = "✅" if not errs else "❌"
        print(f"{mark} {rel}  记录 {info['records']}  第一人称旁白 {info['first_person']}")
        for e in errs:
            print(f"     ❌ {e}")
        for w in warns:
            print(f"     ⚠  {w}")
        total_err += len(errs)
        total_warn += len(warns)

    print(f"\n合计：错误 {total_err} / 警告 {total_warn}（{len(targets)} 个文件）")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
