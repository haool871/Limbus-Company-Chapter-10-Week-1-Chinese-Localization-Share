#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 _parts_split/ 下已译完的分片合并回 translate/<逻辑名>.tsv，并重建 JSON。

分片命名: <骨架名>.part<N>.tsv   （骨架名形如 RPGSystem__rpg-loc-dialogue-floor-1）

规则：
  - 按 part 序号顺序拼接，去掉各分片的注释行（只保留一份表头）；
  - 校验：拼接后的行数必须等于骨架行数；每行 (id, 路径) 必须与骨架逐行一致；
  - 任一分片仍有大量未译（默认阈值：含中文字符 < 50%）则拒绝合并并给出提示。

用法:
  python3 tools/coalesce_parts.py                    # 合并所有已完备的
  python3 tools/coalesce_parts.py <骨架名>           # 只合并一个
  python3 tools/coalesce_parts.py --status           # 只看状态
"""
from __future__ import annotations

import glob
import os
import re
import subprocess
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPLIT = os.path.join(_KB_DIR, "translate", "_parts_split")
SKEL = os.path.join(_KB_DIR, "translate", "_skel")
CJK = re.compile(r"[\u4e00-\u9fff]")


def parts_of(stem: str) -> list[str]:
    fs = glob.glob(os.path.join(SPLIT, stem + ".part*.tsv"))
    return sorted(fs, key=lambda p: int(re.search(r"part(\d+)", p).group(1)))


def read_rows(path: str) -> list[list[str]]:
    rows = []
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        c = line.rstrip("\n").split("\t")
        if len(c) >= 3:
            rows.append(c)
    return rows


def cjk_ratio(rows) -> float:
    if not rows:
        return 1.0
    return sum(1 for c in rows if CJK.search(c[2])) / len(rows)


def main(argv: list[str]) -> None:
    stems = sorted({os.path.basename(p).rsplit(".part", 1)[0]
                    for p in glob.glob(os.path.join(SPLIT, "*.part*.tsv"))})
    status_only = "--status" in argv
    picked = [a for a in argv[1:] if not a.startswith("--")]
    if picked:
        stems = [s for s in stems if s in picked]
    ok = 0
    for stem in stems:
        parts = parts_of(stem)
        rows_all: list[list[str]] = []
        ratios = []
        for p in parts:
            r = read_rows(p)
            rows_all.extend(r)
            ratios.append((os.path.basename(p), len(r), cjk_ratio(r)))
        skel_path = os.path.join(SKEL, stem + ".tsv")
        if not os.path.exists(skel_path):
            print(f"❌ {stem}: 找不到骨架")
            continue
        skel = read_rows(skel_path)
        seq_ok = [x[:2] for x in rows_all] == [x[:2] for x in skel]
        complete = all(rt >= 0.5 for _n, _l, rt in ratios)
        mark = "✅" if (seq_ok and complete and len(rows_all) == len(skel)) else "⏳"
        print(f"{mark} {stem}: 分片 {len(parts)}  行 {len(rows_all)}/{len(skel)}  "
              f"对齐={'是' if seq_ok else '否'}  完成度={min(rt for _n,_l,rt in ratios):.0%}")
        for n, l, rt in ratios:
            print(f"      {n}: {l} 行, 中文 {rt:.0%}")
        if status_only:
            continue
        if not (seq_ok and complete and len(rows_all) == len(skel)):
            continue
        dst = os.path.join(_KB_DIR, "translate", stem + ".tsv")
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(f"# {stem.replace('__','/')}  （由分片合并）\n")
            for c in rows_all:
                fh.write("\t".join(c) + "\n")
        logical = stem.replace("__", "/") + ".json"
        r = subprocess.run([sys.executable, os.path.join(_KB_DIR, "tools", "build_translation.py"),
                            logical, dst], capture_output=True, text=True)
        print("      ", ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-1][:110])
        ok += 1
    print(f"\n本次合并 {ok} 个文件")


if __name__ == "__main__":
    main(sys.argv)
