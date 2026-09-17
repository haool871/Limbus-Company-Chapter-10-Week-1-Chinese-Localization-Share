#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把重译补丁 TSV 精确应用到 patch_v2/RPGSystem/rpg-loc-dialogue-floor-N.json。

用法:
    python3 tools/apply_rpg_retrans.py <json相对路径> <patch.tsv> [--dry-run]

规则（见 workflow/重译手册.md §7）：
  * 只改 texts[].text；key / index / speaker 一律不动。
  * 用 json.load 读入，按 key 定位组、按 index（int）精确定位，赋值后 json.dump 整文件。
  * 断言：每个补丁行的 (key, index) 都必须存在；实际改动条数 == 补丁行数（去重后）。
  * 不存在的 key/index 一律报错退出，**不静默跳过**。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
PATCH = os.path.join(_KB, "patch_v2")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="相对 patch_v2 的路径，如 RPGSystem/rpg-loc-dialogue-floor-3.json")
    ap.add_argument("tsv", help="补丁 TSV：key<TAB>index<TAB>新文本")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    jp = os.path.join(PATCH, args.target)
    with open(jp, encoding="utf-8-sig") as fh:
        doc = json.load(fh)

    rows = []
    with open(args.tsv, encoding="utf-8") as fh:
        for ln, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) != 3:
                print(f"❌ {args.tsv}:{ln} 列数={len(parts)}（应为 3）", file=sys.stderr)
                return 2
            key, idx, txt = parts
            rows.append((key, int(idx), txt, ln))

    # 去重检查
    seen = {}
    for key, idx, txt, ln in rows:
        if (key, idx) in seen:
            print(f"❌ 补丁重复: {key}#{idx}（行 {seen[(key,idx)]} 与 {ln}）", file=sys.stderr)
            return 2
        seen[(key, idx)] = ln

    groups = {g.get("key"): g for g in doc.get("dataList") or [] if isinstance(g, dict)}

    changed = 0
    missing = []
    for key, idx, txt, ln in rows:
        g = groups.get(key)
        if g is None:
            missing.append(f"行{ln} key 不存在: {key}")
            continue
        target = None
        for t in g.get("texts") or []:
            if isinstance(t, dict) and t.get("index") == idx:  # int 比较，不做 str()
                target = t
                break
        if target is None:
            missing.append(f"行{ln} {key} 无 index={idx}")
            continue
        if target.get("text") != txt:
            changed += 1
        target["text"] = txt

    if missing:
        for m in missing:
            print(f"❌ {m}", file=sys.stderr)
        return 2

    print(f"补丁行数={len(rows)} 实际改动条数={changed}")
    assert changed == len(rows), f"断言失败: 改动 {changed} != 补丁 {len(rows)}"

    if args.dry_run:
        print("（dry-run，未写盘）")
        return 0

    with open(jp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
    print(f"✅ 已写回 {jp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
