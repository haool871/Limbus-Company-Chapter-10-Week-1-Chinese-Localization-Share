#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补齐基础汉化包缺失的记录（英文/韩文有、中文没有）。

零协会基础包落后于游戏版本，部分文件缺少新人格/新机制的条目，
导致这些内容在游戏里显示英文。本工具：

  1. 读官方英文文件（完整记录集）与已装中文文件；
  2. 对中文缺失的记录，用「英文结构 + C 栏译文」生成中文记录；
  3. 按**英文字典序（id 顺序）**把中文记录插入到正确位置；
  4. 输出到 patch/ 目录，供安装覆盖。

译文表格式: translate_patch/<文件名>.tsv
  id <TAB> 字段路径 <TAB> 中文
未提供译文的字段保留英文。

用法:
  python3 fill_gaps.py --list                     # 列出所有缺口的文件与条数
  python3 fill_gaps.py <文件名>                    # 生成该文件的补齐版
  python3 fill_gaps.py --all                      # 生成全部
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
    DEV_FIELDS,
    walk_strings,
    set_by_path,
)
from verify_output import OUT_DIR  # noqa: E402

GAME = P.GAME_ROOT
EN_DIR = os.path.join(GAME, "LimbusCompany_Data", "Assets", "Resources_moved", "Localize", "en")
LD = os.path.join(GAME, "LimbusCompany_Data", "Lang", "LLC_zh-CN")
PATCH = os.path.join(_KB_DIR, "patch", "LLC_zh-CN")
TRDIR = os.path.join(_KB_DIR, "translate_patch")


def en_path(rel: str) -> str:
    d, b = os.path.split(rel)
    return os.path.join(EN_DIR, d, "EN_" + b)


def recs_of(path: str) -> list[dict]:
    with open(path, encoding="utf-8-sig") as fh:
        d = json.load(fh)
    r = d.get("dataList", d) if isinstance(d, dict) else d
    return r if isinstance(r, list) else []


def rid_of(r: dict) -> str:
    return str(r.get("id", r.get("key", "")))


def find_gaps() -> list[tuple[str, list[dict]]]:
    """返回 [(相对路径, 缺失的英文记录列表)]，按 id 顺序。"""
    out = []
    for dp, _dn, fn in os.walk(EN_DIR):
        for f in fn:
            if not f.startswith("EN_") or not f.endswith(".json"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), EN_DIR)[3:]  # 去掉 EN_
            cnp = os.path.join(LD, rel)
            if not os.path.exists(cnp):
                continue
            en = recs_of(os.path.join(dp, f))
            cn = recs_of(cnp)
            have = {rid_of(r) for r in cn}
            miss = [r for r in en if rid_of(r) not in have]
            if miss:
                out.append((rel, miss))
    out.sort(key=lambda x: -len(x[1]))
    return out


def merged(rel: str, tr: dict[tuple[str, str], str]) -> dict:
    """把缺失记录（带译文）插回中文文件，输出完整 JSON 对象。"""
    with open(en_path(rel), encoding="utf-8-sig") as fh:
        en_doc = json.load(fh)
    en_list = en_doc.get("dataList", en_doc)
    with open(os.path.join(LD, rel), encoding="utf-8-sig") as fh:
        cn_doc = json.load(fh)
    cn_list = cn_doc["dataList"]
    have = {rid_of(r) for r in cn_list}

    # 以英文结构为模板，套用译文生成缺失记录
    new_recs = []
    for r in en_list:
        rid = rid_of(r)
        if rid in have:
            continue
        rec = json.loads(json.dumps(r, ensure_ascii=False))  # 深拷贝，保持结构与键序
        for path, ev in walk_strings(rec):
            leaf = path.split(".")[-1].split("[")[0]
            if leaf in DEV_FIELDS:
                continue
            key = (rid, path)
            if key in tr:
                set_by_path(rec, path, tr[key])
        new_recs.append(rec)

    # 按英文字典序合并：以英文顺序为准重排全部记录
    by_id = {rid_of(r): r for r in cn_list}
    for r in new_recs:
        by_id[rid_of(r)] = r
    ordered = [by_id[rid_of(r)] for r in en_list if rid_of(r) in by_id]
    # 保留中文里存在但英文没有的记录（放到末尾，避免丢失）
    extra = [r for r in cn_list if rid_of(r) not in {rid_of(x) for x in en_list}]
    ordered.extend(extra)
    cn_doc["dataList"] = ordered
    return cn_doc


def load_tr(rel: str) -> dict[tuple[str, str], str]:
    p = os.path.join(TRDIR, rel.replace("/", "__")[:-5] + ".tsv")
    tr: dict[tuple[str, str], str] = {}
    if not os.path.exists(p):
        return tr
    for line in open(p, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        c = line.rstrip("\n").split("\t")
        if len(c) >= 3:
            tr[(c[0], c[1])] = "\t".join(c[2:]).replace("\\n", "\n")
    return tr


def main(argv: list[str]) -> None:
    gaps = find_gaps()
    if "--list" in argv or len(argv) < 2:
        print(f"{'文件':52s}{'缺失条数':>8s}{'缺失字段':>9s}")
        tf = 0
        for rel, miss in gaps:
            n = sum(1 for r in miss for p_, v in walk_strings(r)
                    if isinstance(v, str) and v.strip() and p_.split(".")[-1].split("[")[0] not in DEV_FIELDS)
            tf += n
            print(f"{rel:52s}{len(miss):8d}{n:9d}")
        print(f"\n共 {len(gaps)} 个文件，{sum(len(m) for _, m in gaps)} 条记录，{tf} 个字段")
        return

    targets = [rel for rel, _ in gaps] if "--all" in argv else argv[1:]
    os.makedirs(PATCH, exist_ok=True)
    for rel in targets:
        if rel not in [r for r, _ in gaps]:
            print(f"跳过（无缺口）: {rel}")
            continue
        tr = load_tr(rel)
        doc = merged(rel, tr)
        dst = os.path.join(PATCH, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2)
        miss = dict(gaps)[rel]
        print(f"✅ {rel}: 补齐 {len(miss)} 条（已译字段 {len(tr)}）→ {dst}")


if __name__ == "__main__":
    main(sys.argv)
