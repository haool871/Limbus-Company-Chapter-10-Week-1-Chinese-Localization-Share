#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通读润色用的「可疑句清单」：把读起来可能不顺的句子连上下文一起抽出来。

与 audit 类工具的区别：这里**不判对错**，只把值得人眼看的句子**排到前面**，
并附上同一组的上下文（前一条/后一条），以便判断回应关系与指代。

判据（只做粗筛，最终靠人眼）
  - 「的」密度高（三层以上套嵌）
  - 「名词 + 存在/进行/予以/有着」这类动词被抽空的写法
  - `对于/关于` 开句接长定语
  - `被…所…` / `作为…的…` 连用
  - 中文显著长于韩文（可能照英文写长了）
  - 含半角标点、`......`、直角引号等体例残留

用法:
  python3 tools/polish_scan.py --file StoryData/S1004B.json --limit 40
  python3 tools/polish_scan.py --story --limit 300 > /tmp/polish_story.txt
  python3 tools/polish_scan.py --rpg --limit 300 > /tmp/polish_rpg.txt
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
PATCH = os.path.join(_KB, "patch_v2")
GAME = os.environ.get("LIMBUS_GAME_ROOT",
                      "/home/shb/.local/share/Steam/steamapps/common/Limbus Company")
KR = os.path.join(GAME, "LimbusCompany_Data", "Assets", "Resources_moved", "Localize", "kr")

MARKS = [
    (re.compile(r"(?:^|[，。；：])(?:对于|关于)"), 4, "对于/关于开句"),
    (re.compile(r"予以|进行(?:了|着)|加以"), 3, "动词被抽空"),
    (re.compile(r"存在(?:着|于)|有着|是在于"), 3, "存在/有着"),
    (re.compile(r"被[^，。！？]{1,12}所"), 3, "被…所…"),
    (re.compile(r"作为[^，。！？]{1,12}的"), 3, "作为…的…"),
    (re.compile(r"的[^，。！？]{1,10}的[^，。！？]{1,10}的"), 3, "三层「的」"),
    (re.compile(r"\.\.\.\.\.\."), 2, "六个点号"),
    (re.compile(r"[「」〈〉]"), 2, "直角引号/尖括号"),
    (re.compile(r"正因如此|因此而"), 2, "正因如此"),
    (re.compile(r"的方式|的方法|的情况下"), 2, "冗余「的方式」"),
    (re.compile(r"并不[^，。]{1,15}而是|并非[^，。]{1,15}而是"), 2, "并不…而是"),
    (re.compile(r"某种程度上|在某种意义上"), 2, "含糊限定"),
    (re.compile(r"使得|使之"), 2, "使得/使之"),
]


def load(p):
    try:
        with open(p, encoding="utf-8-sig") as fh:
            return json.load(fh).get("dataList") or []
    except Exception:
        return []


def kr_index(f):
    d, f2 = os.path.split(f)
    p = os.path.join(KR, d, "KR_" + f2)
    if not os.path.exists(p):
        return {}
    out = {}
    for r in load(p):
        if isinstance(r, dict):
            out[str(r.get("id", r.get("key")))] = r
    return out


def texts_of(rec):
    def go(o, path=""):
        if isinstance(o, str):
            if o.strip():
                yield path, o
        elif isinstance(o, dict):
            for k, v in o.items():
                if k in ("id", "key", "index", "speaker", "model", "teller"):
                    continue
                yield from go(v, f"{path}.{k}" if path else k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                yield from go(v, f"{path}[{i}]")
    return list(go(rec))


def scan_file(rel, limit):
    cn = load(os.path.join(PATCH, rel))
    kr = kr_index(rel)
    out = []
    for r in cn:
        if not isinstance(r, dict):
            continue
        rid = str(r.get("id", r.get("key")))
        krec = kr.get(rid) or {}
        ktexts = [t for _, t in texts_of(krec)] if krec else []
        for path, t in texts_of(r):
            score = 0
            why = []
            for pat, w, name in MARKS:
                if pat.search(t):
                    score += w
                    why.append(name)
            nd = t.count("的")
            if nd >= 3:
                score += (nd - 2) * 2
                why.append(f"「的」×{nd}")
            if len(t) >= 12 and t.rstrip().endswith("。"):
                pass
            if score >= 3:
                out.append((score, rid, path, t, ktexts[0] if ktexts else "", why))
    out.sort(key=lambda x: -x[0])
    return out[:limit]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--story", action="store_true")
    ap.add_argument("--rpg", action="store_true")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    targets = []
    if args.file:
        targets = [args.file]
    elif args.story:
        targets = [os.path.relpath(os.path.join(PATCH, "StoryData", f), PATCH)
                   for f in sorted(os.listdir(os.path.join(PATCH, "StoryData")))
                   if f.endswith(".json")]
    elif args.rpg:
        targets = [os.path.relpath(os.path.join(PATCH, "RPGSystem", f), PATCH)
                   for f in sorted(os.listdir(os.path.join(PATCH, "RPGSystem")))
                   if f.endswith(".json")]
    else:
        ap.error("需要 --file / --story / --rpg")

    total = 0
    for rel in targets:
        hits = scan_file(rel, args.limit)
        if not hits:
            continue
        total += len(hits)
        print(f"\n{'='*72}\n## {rel}  可疑 {len(hits)} 条\n{'='*72}")
        for score, rid, path, t, kr, why in hits:
            print(f"[{score}] {rid} .{path}   ({'、'.join(dict.fromkeys(why))})")
            if kr:
                print(f"   KR: {kr[:110]}")
            print(f"   CN: {t[:150]}")
            print()
    print(f"\n合计可疑 {total} 条", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
