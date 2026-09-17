#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成品验证：把生成的译文 JSON 与官方英文源逐字段对比。

检查项（任一不通过即视为不可交付）：
  1. 结构一致性：记录数、id 序列、字段名集合与英文源完全相同（不增不减不改名）
  2. 富文本标记：<color>/<b>/<u>/<mark>/<i> 等与英文源**逐字符一致**
  3. 引擎标签：[] 内的拉丁标识符一致
  4. 占位符：{0} 等一致
  5. 译出率：统计仍是纯英文（未译）的字段比例

用法:
  python3 verify_output.py                    # 验证 out/LLC_zh-CN 下全部文件
  python3 verify_output.py MainUIText-a1c10p1.json
"""
from __future__ import annotations

import json
import os
import re
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_KB_DIR, "tools"))
import pm_lib as P  # noqa: E402
from build_translation import (  # noqa: E402
    BRACKET,
    DEV_FIELDS,
    PLACEHOLDER,
    STRICT_TAG,
    is_engine_bracket,
    walk_strings,
)

OUT_DIR = os.path.join(_KB_DIR, "out", "LLC_zh-CN")
CJK = re.compile(r"[\u4e00-\u9fff]")
LATIN = re.compile(r"[A-Za-z]")


def fields_of(rec: dict, skip: set[str]) -> dict[str, str]:
    out = {}
    for path, val in walk_strings(rec):
        leaf = path.split(".")[-1].split("[")[0]
        if leaf in DEV_FIELDS or leaf in skip:
            continue
        out[path] = val
    return out


def load_records(obj):
    recs = obj["dataList"] if isinstance(obj, dict) and "dataList" in obj else obj
    if isinstance(recs, dict):
        recs = [recs]
    out = {}
    order = []
    for i, r in enumerate(recs):
        if not isinstance(r, dict):
            continue
        rid = str(r.get("id", r.get("key", f"#{i}")))
        out.setdefault(rid, r)
        order.append(rid)
    return out, order


def verify_one(logical: str) -> tuple[int, int, list[str]]:
    idx = P.build_index()
    if logical not in idx or "en" not in idx[logical]:
        return 0, 0, [f"逻辑名不存在: {logical}"]
    en_rel = idx[logical]["en"]
    d, b = os.path.split(logical)
    if b.startswith(("EN_", "KR_", "JP_")):
        b = b[3:]
    cn_rel = os.path.join(d, b) if d else b
    out_path = os.path.join(OUT_DIR, cn_rel)
    if not os.path.exists(out_path):
        return 0, 0, [f"未生成: {cn_rel}"]
    with open(os.path.join(P.LANG_DIR["en"], en_rel), encoding="utf-8") as fh:
        src = json.load(fh)
    with open(out_path, encoding="utf-8") as fh:
        dst = json.load(fh)

    # 跳过字段（与译文表同目录的 .skip）
    skip: set[str] = set()
    tsv = os.path.join(_KB_DIR, "translate", logical.replace("/", "__")[:-5] + ".tsv")
    skip_path = tsv + ".skip"
    if os.path.exists(skip_path):
        with open(skip_path, encoding="utf-8") as fh:
            skip = {ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")}

    src_recs, src_order = load_records(src)
    dst_recs, dst_order = load_records(dst)
    problems: list[str] = []
    if src_order != dst_order:
        problems.append(f"记录 id 序列不一致\n  EN: {src_order[:8]}\n  CN: {dst_order[:8]}")
    if set(src_recs) != set(dst_recs):
        problems.append(f"记录集合不一致，缺 {sorted(set(src_recs)-set(dst_recs))[:5]}，多 {sorted(set(dst_recs)-set(src_recs))[:5]}")

    translated = total = 0
    for rid, srec in src_recs.items():
        drec = dst_recs.get(rid)
        if drec is None:
            continue
        sf, df = fields_of(srec, skip), fields_of(drec, skip)
        if set(sf) != set(df):
            problems.append(f"id={rid} 字段集合不一致：缺 {sorted(set(sf)-set(df))[:5]}，多 {sorted(set(df)-set(sf))[:5]}")
        for path, ev in sf.items():
            cv = df.get(path)
            if cv is None:
                continue
            total += 1
            # 标记校验
            if sorted(STRICT_TAG.findall(ev)) != sorted(STRICT_TAG.findall(cv)):
                problems.append(f"id={rid}.{path} 样式标签不一致\n    EN: {sorted(STRICT_TAG.findall(ev))}\n    CN: {sorted(STRICT_TAG.findall(cv))}")
            ea = sorted(t for t in BRACKET.findall(ev) if is_engine_bracket(t))
            ca = sorted(t for t in BRACKET.findall(cv) if is_engine_bracket(t))
            if ea != ca:
                problems.append(f"id={rid}.{path} 引擎标签不一致\n    EN: {ea}\n    CN: {ca}")
            if sorted(PLACEHOLDER.findall(ev)) != sorted(PLACEHOLDER.findall(cv)):
                problems.append(f"id={rid}.{path} 占位符不一致\n    EN: {sorted(PLACEHOLDER.findall(ev))}\n    CN: {sorted(PLACEHOLDER.findall(cv))}")
            # 译出率：英文源含字母、中文侧完全无汉字 → 未译
            if LATIN.search(ev) and not CJK.search(cv):
                if cv.strip() == ev.strip():
                    pass  # 有意保留原文（商品名等）
                else:
                    pass
            if CJK.search(cv) or cv.strip() != ev.strip():
                translated += 1
    return translated, total, problems


def main(argv: list[str]) -> None:
    if len(argv) > 1:
        targets = argv[1:]
    else:
        idx = P.build_index()
        targets = []
        for logical in sorted(idx):
            b = os.path.basename(logical)
            if b.startswith(("EN_", "KR_", "JP_")):
                b = b[3:]
            d = os.path.dirname(logical)
            rel = os.path.join(d, b) if d else b
            if os.path.exists(os.path.join(OUT_DIR, rel)):
                targets.append(logical)
    grand = [0, 0]
    bad = 0
    for logical in targets:
        tr, tot, probs = verify_one(logical)
        grand[0] += tr
        grand[1] += tot
        status = "✅" if not probs else "❌"
        print(f"{status} {logical:56s} {tr:5d}/{tot:5d}" + (f"  {len(probs)} 问题" if probs else ""))
        for p in probs[:6]:
            print("     ", p)
        if probs:
            bad += 1
    print(f"\n共 {len(targets)} 个文件，{bad} 个有问题；已译字段 {grand[0]}/{grand[1]}")


if __name__ == "__main__":
    main(sys.argv)
