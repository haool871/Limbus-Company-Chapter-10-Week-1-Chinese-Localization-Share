#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导出 RPGSystem（探索模式）对话的「按组」对照，供带上下文重译。

RPGSystem 的对话天然成组（`key` + `texts[]`），**翻译单位就是一组**。
本工具按组输出 KR / EN / CN 三语逐条对照，并标注说话人与组内条数。

用法:
  python3 tools/rpg_dump.py RPGSystem/rpg-loc-dialogue-floor-1.json --out /tmp/rpg_f1.txt
  python3 tools/rpg_dump.py --list
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
PATCH = os.path.join(_KB, "patch_v2")
GAME = os.environ.get("LIMBUS_GAME_ROOT",
                      "/home/shb/.local/share/Steam/steamapps/common/Limbus Company")
LOC = os.path.join(GAME, "LimbusCompany_Data", "Assets", "Resources_moved", "Localize")

NAMES = {
    "돈키호테": "堂吉诃德", "파우스트": "浮士德", "이상": "李箱", "뫼르소": "默尔索",
    "홍루": "鸿璐", "히스클리프": "希斯克利夫", "이스마엘": "以实玛利", "로쟈": "罗佳",
    "싱클레어": "辛克莱", "오티스": "奥提斯", "그레고르": "格里高尔", "료슈": "良秀",
    "단테": "但丁",
}


def load(p):
    try:
        with open(p, encoding="utf-8-sig") as fh:
            return json.load(fh).get("dataList") or []
    except Exception:
        return []


def idx(p):
    return {g.get("key"): g for g in load(p) if isinstance(g, dict)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        for f in sorted(os.listdir(os.path.join(PATCH, "RPGSystem"))):
            if f.endswith(".json"):
                print(f"RPGSystem/{f}")
        return 0

    rel = args.target
    cn_path = os.path.join(PATCH, rel)
    if not os.path.exists(cn_path):
        print(f"不存在: {cn_path}", file=sys.stderr)
        return 2
    base = os.path.basename(rel)
    K = idx(os.path.join(LOC, "kr", "RPGSystem", "KR_" + base))
    E = idx(os.path.join(LOC, "en", "RPGSystem", "EN_" + base))
    C = load(cn_path)

    lines = [f"# {rel}",
             f"# 组数={len(C)}  KR={'有' if K else '无'}  EN={'有' if E else '无'}",
             "> 翻译单位＝一组（key）。同组内一问一答，必须整组一起读、一起译。", ""]
    for g in C:
        if not isinstance(g, dict):
            continue
        key = g.get("key")
        kg, eg = K.get(key) or {}, E.get(key) or {}
        kts, ets = kg.get("texts") or [], eg.get("texts") or []
        ts = g.get("texts") or []
        lines.append(f"=== {key}  ({len(ts)} 条) ===")
        for i, t in enumerate(ts):
            if not isinstance(t, dict):
                continue
            sp = str(t.get("speaker") or "")
            sp_disp = NAMES.get(sp, sp) or "（无）"
            lines.append(f"  [{i}] {sp_disp}")
            if i < len(kts) and isinstance(kts[i], dict) and (kts[i].get("text") or "").strip():
                lines.append(f"      KR| {kts[i]['text']}")
            if i < len(ets) and isinstance(ets[i], dict) and (ets[i].get("text") or "").strip():
                lines.append(f"      EN| {ets[i]['text']}")
            lines.append(f"      CN| {t.get('text')}")
        lines.append("")

    out = "\n".join(lines)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"已写出 {args.out}（{len(out.splitlines())} 行，{len(C)} 组）")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
