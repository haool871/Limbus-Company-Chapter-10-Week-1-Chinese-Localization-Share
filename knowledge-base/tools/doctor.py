#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""汉化项目环境自检：一条命令摸清「能不能开工、范围多大、有哪些待办」。

用法:
  python3 tools/doctor.py            # 完整自检
  python3 tools/doctor.py --quick    # 只看关键项
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
WS = os.path.dirname(_KB)
PATCH = os.path.join(_KB, "patch_v2")
GAME = os.environ.get(
    "LIMBUS_GAME_ROOT",
    "/home/shb/.local/share/Steam/steamapps/common/Limbus Company",
)
CN = os.path.join(GAME, "LimbusCompany_Data", "Lang", "LLC_zh-CN")
EN = os.path.join(GAME, "LimbusCompany_Data", "Assets", "Resources_moved", "Localize", "en")


def ok(msg): print(f"  \033[32m✅\033[0m {msg}")
def warn(msg): print(f"  \033[33m⚠\033[0m  {msg}")
def bad(msg): print(f"  \033[31m❌\033[0m {msg}")


def load(p):
    try:
        with open(p, encoding="utf-8-sig") as fh:
            return json.load(fh)
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    problems = 0

    print("═══ 1. 基准包 ═══")
    packs = sorted(glob.glob(os.path.join(WS, "LimbusLocalize_latest*",
                                          "LimbusCompany_Data", "Lang", "LLC_zh-CN")))
    cur = None
    for p in packs:
        v = load(os.path.join(p, "Info", "version.json")) or {}
        name = os.path.relpath(p, WS).split(os.sep)[0]
        mark = ""
        if cur is None or v.get("version", 0) > (load(os.path.join(cur, "Info", "version.json")) or {}).get("version", 0):
            cur = p
        print(f"    {name}: version={v.get('version')}  文件={len(glob.glob(os.path.join(p,'**','*.json'),recursive=True))}")
    if cur:
        ok(f"现行基准 = {os.path.relpath(cur, WS).split(os.sep)[0]}")
        env = os.environ.get("LIMBUS_BASE_PACK")
        print(f"      工具基准: {env or '(自动=最新包)'}")
    else:
        bad("找不到零协基础包"); problems += 1

    print("\n═══ 2. 补丁 ═══")
    files = glob.glob(os.path.join(PATCH, "**", "*.json"), recursive=True)
    badjson = [p for p in files if load(p) is None]
    if badjson:
        bad(f"JSON 损坏 {len(badjson)} 个"); problems += 1
    else:
        ok(f"{len(files)} 个文件 JSON 合法")
    if not args.quick:
        groups = {}
        for p in files:
            k = os.path.relpath(p, PATCH).split(os.sep)[0]
            groups[k] = groups.get(k, 0) + 1
        print(f"      分布: {groups}")

    print("\n═══ 3. 游戏安装 ═══")
    if not os.path.isdir(CN):
        bad(f"游戏侧没有 LLC_zh-CN: {CN}"); problems += 1
    else:
        cfg = os.path.join(GAME, "LimbusCompany_Data", "Lang", "config.json")
        lang = (load(cfg) or {}).get("lang")
        (ok if lang == "LLC_zh-CN" else bad)(f"config.json lang={lang!r}")
        if lang != "LLC_zh-CN":
            problems += 1
        font = os.path.join(CN, "Font", "Context", "ChineseFont.ttf")
        if os.path.exists(font) and os.path.getsize(font) > 0:
            ok(f"字体 {os.path.getsize(font)/1048576:.1f} MB")
        else:
            bad("缺少中文字体 ChineseFont.ttf"); problems += 1
        gjson = len(glob.glob(os.path.join(CN, "**", "*.json"), recursive=True))
        print(f"      游戏侧 JSON: {gjson}")
        # 补丁是否已同步到游戏
        miss = [os.path.relpath(p, PATCH) for p in files
                if not os.path.exists(os.path.join(CN, os.path.relpath(p, PATCH)))]
        if miss:
            warn(f"补丁有 {len(miss)} 个文件未装到游戏")
        else:
            ok("补丁文件全部已装到游戏")

    print("\n═══ 4. 术语资料 ═══")
    for name, path, floor in (
        ("confirmed_pairs.tsv", os.path.join(_KB, "terms", "confirmed_pairs.tsv"), 1000),
        ("glossary_all.clean.tsv", os.path.join(_KB, "terms", "glossary_all.clean.tsv"), 5000),
        ("术语表.md", os.path.join(_KB, "terms", "术语表.md"), 100),
    ):
        if os.path.exists(path):
            n = sum(1 for _ in open(path, encoding="utf-8"))
            (ok if n >= floor else warn)(f"{name}: {n} 行")
        else:
            bad(f"{name} 缺失"); problems += 1

    print("\n═══ 5. 语料缓存 ═══")
    for name, path in (("corpus.jsonl", os.path.join(_KB, "data", "corpus.jsonl")),
                       ("_align.pkl", os.path.join(_KB, "data", "_align.pkl")),
                       ("_file_index.json", os.path.join(_KB, "data", "_file_index.json"))):
        if os.path.exists(path):
            print(f"    {name}: {os.path.getsize(path)/1048576:.1f} MB  "
                  f"({__import__('time').strftime('%m-%d %H:%M', __import__('time').localtime(os.path.getmtime(path)))})")
        else:
            warn(f"{name} 不存在（需先重建语料）")

    print("\n═══ 6. 能不能开工 ═══")
    if problems:
        bad(f"有 {problems} 项阻塞问题，先解决")
    else:
        ok("环境就绪")
    print("\n  下一步：")
    print("    1) 读 workflow/与零协差距教材.md（开工前必读）")
    print("    2) 算范围：python3 tools/scope.py        （新增在哪 + 逐条漏译清单）")
    print("    3) 建骨架：python3 tools/scope.py --add-missing")
    print("    4) 改完跑：python3 tools/verify_retrans.py --all")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
