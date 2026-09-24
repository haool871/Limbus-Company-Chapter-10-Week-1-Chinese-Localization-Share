#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨文件一致性检查：找出「同一英文概念出现多种中文译法」及禁用变体。

用途：多组并行翻译后统一口径。收录方式：在 GROUPS 里登记一组应为同一译法的候选词，
脚本会在全部产出 JSON 中统计各变体出现次数，出现 >1 种即报警。

也可直接跑内置的禁用变体与专名清单检查。

用法:
  python3 check_consistency.py            # 全部检查
  python3 check_consistency.py --terms    # 只查登记过的同义组
"""
from __future__ import annotations

if __name__ == "__main__":
    raise SystemExit("旧批次入口已退役。请读 workflow/版本更新流程.md，使用 snapshot / scope / batch；不会写入旧目录。")


import collections
import json
import os
import re
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(_KB_DIR, "out", "LLC_zh-CN")

# 应为同一译法的同义组（每组第一个是推荐写法）
GROUPS = [
    ["西西弗百货"],                       # 禁用变体由 BANNED 负责
    ["黄金皮毛", "黄金外皮", "黄金皮"],
    ["黄金松脂", "黄金树脂"],
    # 注意：「修改师」（Modification Shop 职称，S1009B）与「改衣师」（Alterationist，P10416）
    # 语义不同，不合并。
    ["西西弗之刑", "西西弗罚则"],
    ["援护防御", "协助防御", "支援防御"],
    ["楼层经理", "楼面经理"],
    ["泉眼", "泉水", "泉源"],
    ["副主厨", "厨师长"],
    ["缝纫之王", "裁缝之王"],
    ["勒卡基", "卡基", "Kaki"],
    ["赤色之神", "绯红之神", "深红之神"],
    ["生命线", "命线", "生命之线"],
    ["那位", "珍爱之人"],
    ["影界", "暗影界"],
    ["针人", "针怪"],
    ["皮钱包", "皮革钱包"],
    ["更衣室", "试衣间"],
    ["警戒过度", "过度警戒"],
    ["聆听的谢意", "倾听的感谢"],
    ["切好的食材", "切碎的食材"],
]

# 禁用变体（明确错误/已裁定弃用）
BANNED = [
    ("大百货店", "应为「西西弗百货」"),
    ("西西弗大百货店", "应为「西西弗百货」"),
    ("无名指", "The Ring 应为「环指」"),
    ("世界之翼", "语料不存在该写法，只有「翼」"),
    ("修复者", "Fixer 应为「收尾人」"),
    ("协助防御", "Assist Defense 既有译法为「援护防御」"),
]


def all_texts():
    """产出 (文件, 文本)。"""
    for dp, _dn, fn in os.walk(OUT_DIR):
        for f in fn:
            if not f.endswith(".json"):
                continue
            p = os.path.join(dp, f)
            try:
                data = json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
            recs = data["dataList"] if isinstance(data, dict) and "dataList" in data else data
            if isinstance(recs, dict):
                recs = [recs]
            rel = os.path.relpath(p, OUT_DIR)
            stack = [recs]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    stack.extend(node.values())
                elif isinstance(node, list):
                    stack.extend(node)
                elif isinstance(node, str) and any("\u4e00" <= c <= "\u9fff" for c in node):
                    yield rel, node


def main(argv: list[str]) -> None:
    counts: dict[str, collections.Counter] = {g[0]: collections.Counter() for g in GROUPS}
    where: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    banned_hits: dict[str, collections.Counter] = {b[0]: collections.Counter() for b in BANNED}
    n = 0
    for f, t in all_texts():
        n += 1
        for g in GROUPS:
            for v in g:
                # 跳过「是组内更长候选的子串」的短写法，避免 勒卡基/卡基 这类重复计数
                if any(v != w and v in w for w in g):
                    continue
                if v in t:
                    counts[g[0]][v] += 1
                    if len(where[(g[0], v)]) < 4:
                        where[(g[0], v)].append(f)
        for b, _why in BANNED:
            if b in t:
                banned_hits[b][f] += 1

    print(f"扫描 {n} 条中文文本\n")
    print("=== 禁用变体 ===")
    any_bad = False
    for b, why in BANNED:
        c = banned_hits[b]
        if c:
            any_bad = True
            print(f"  ❌ 「{b}」出现 {sum(c.values())} 次（{len(c)} 个文件）— {why}")
            for f, k in c.most_common(4):
                print(f"        {f}: {k}")
    if not any_bad:
        print("  ✅ 未发现禁用变体")

    print("\n=== 同义组（组内出现 >1 种即需统一）===")
    any_mixed = False
    for g in GROUPS:
        present = {v: c for v, c in counts[g[0]].items() if c}
        if len(present) > 1:
            any_mixed = True
            print(f"  ⚠ 需统一：{g[0]}")
            for v, c in sorted(present.items(), key=lambda x: -x[1]):
                print(f"        {v}: {c} 次   例: {where[(g[0], v)][:2]}")
        elif len(present) == 1:
            v, c = next(iter(present.items()))
            print(f"  ✅ {g[0]}：仅「{v}」({c} 次)")
    if not any_mixed:
        print("  （无混用）")


if __name__ == "__main__":
    main(sys.argv)
