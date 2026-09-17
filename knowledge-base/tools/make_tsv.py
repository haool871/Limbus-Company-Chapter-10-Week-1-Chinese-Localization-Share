#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「译文片段表」按骨架顺序拼成 build_translation.py 需要的 TSV。

设计目的：
  长文件（如 rpg-loc-dialogue-floor-1，1251 字段）若直接手写 TSV，
  制表符与换行极易出错。本工具改为：

  1. 译者只写「值」，按骨架顺序一行一个，放进 _kb/translate/_parts/<名字>.txt
     - 空行 = 保持英文原样（不译）
     - 多行文本：用 \\n 转义写成一行，或使用 <<< >>> 包裹的整块
     - 以 #! 开头的行是注释（不会计入行数）
  2. 本脚本读取骨架 TSV（含 id / 字段路径 / 英文原文）与译文值文件，
     逐行配对生成最终 TSV。
  3. 行数不符会明确报错并指出第几行，绝不静默错位。

用法：
  python3 make_tsv.py <骨架tsv> <译文值txt> [-o 输出tsv]
  python3 make_tsv.py --check <骨架tsv> <译文值txt>    # 只检查行数
"""
from __future__ import annotations

import os
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 显式「保持英文原样」标记：用于 dev/未使用记录。
# 比空行安全——文件末尾的空行会被编辑器/工具吞掉，导致行数错位。
KEEP = "@KEEP@"


def load_skeleton(path: str) -> list[tuple[str, str, str]]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                # 英文原文为空的行（如 steps[0].index 之类）
                while len(parts) < 3:
                    parts.append("")
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def load_values(path: str) -> list[str]:
    """读译文值文件。

    - 以 #! 开头 = 注释，忽略
    - <<< 单独一行 开始块，直到 >>> 单独一行；块内保留真实换行
    - 其他非空行：一行一个值，其中的 \\n 会被还原为换行
    - 空行 = 空值（表示不翻译，保持英文）
    """
    out: list[str] = []
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    i = 0
    buf: list[str] | None = None
    while i < len(lines):
        raw = lines[i]
        if buf is not None:
            if raw.strip() == ">>>":
                out.append("\n".join(buf))
                buf = None
            else:
                buf.append(raw)
            i += 1
            continue
        if raw.strip() == "<<<":
            buf = []
            i += 1
            continue
        if raw.startswith("#!"):
            i += 1
            continue
        if raw.strip() == "":
            out.append("")
            i += 1
            continue
        if raw.strip() == KEEP:
            out.append("")
            i += 1
            continue
        out.append(raw)
        i += 1
    if buf is not None:
        raise SystemExit("❌ 译文值文件里有未闭合的 <<< 块")
    # split 会在文件末尾多出一个空元素（终止换行造成），只去掉这一个；
    # 其余空值必须保留，否则行数会与骨架错位。
    if out and out[-1] == "":
        out.pop()
    return out


def main(argv: list[str]) -> None:
    args = argv[1:]
    check_only = False
    if args and args[0] == "--check":
        check_only = True
        args = args[1:]
    out_path = None
    if "-o" in args:
        i = args.index("-o")
        out_path = args[i + 1]
        del args[i:i + 2]
    if len(args) < 2:
        print(__doc__)
        raise SystemExit(1)
    skel_path, val_path = args[0], args[1]
    skel = load_skeleton(skel_path)
    vals = load_values(val_path)

    if len(skel) != len(vals):
        print(f"❌ 行数不符：骨架 {len(skel)} 行，译文值 {len(vals)} 行（差 {len(vals)-len(skel)}）")
        n = min(len(skel), len(vals))
        for i in range(n):
            if skel[i][2].strip() != "" and vals[i].strip() == "":
                pass
        print("   前 5 行对照：")
        for i in range(min(5, n)):
            print(f"     [{i+1}] 骨架={skel[i][2][:50]!r}  译={vals[i][:50]!r}")
        if len(vals) > n:
            print(f"   多出的第 {n+1} 行: {vals[n][:80]!r}")
        elif len(skel) > n:
            print(f"   缺少的第 {n+1} 行（骨架）: {skel[n][2][:80]!r}")
        raise SystemExit(1)

    empty = sum(1 for v in vals if not v.strip())
    if not check_only:
        if out_path is None:
            # 默认输出到 translate/_out/，绝不写回骨架文件
            # （translate/<名>.tsv 是骨架，被覆盖后需用 rebuild_skeleton.py 重建）
            out_dir = os.path.join(_KB_DIR, "translate", "_out")
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, os.path.basename(skel_path))
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(f"# {os.path.basename(skel_path)}  由 make_tsv.py 生成\n")
            for (rid, field, _en), val in zip(skel, vals):
                # 空值 → 保持英文原样（英文原文已是 \n 转义形式）
                v = val if val.strip() else _en
                # 值里的真实换行统一转成字面量 \n，否则会撑破 TSV 的行结构
                v = v.replace("\n", "\\n")
                fh.write(f"{rid}\t{field}\t{v}\n")
        print(f"✅ {os.path.basename(out_path)}: {len(skel)} 行"
              f"（未译为英文原样的 {empty} 行）")
    else:
        print(f"✅ 行数一致：{len(skel)} 行（空值 {empty} 行）")


if __name__ == "__main__":
    main(sys.argv)
