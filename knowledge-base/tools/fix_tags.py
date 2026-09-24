#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复富文本标签错位（把英文源的标签序列按顺序重注入到译文对应容器）。

背景：RPGSystem 的 `texts` 数组是「说话人名 / 台词」交替。若译文重排了台词，
英文里某个槽位的 `<color=...>` 会落到错误的槽位，导致开/闭标签配错。

做法：**只重排标签，不改动任何译文字符**
  对每个容器记录（如 texts）：
    en_seq = 英文按顺序抽出的标签序列
    cn_seq = 译文按顺序抽出的标签序列（当前错位的）
    - 若标签种类与数量一致 → 把 en_seq 按顺序写回译文各叶子（去掉原有全部标签后重加）
    - 数量不一致 → 只做「补齐/截断」：把 en_seq 中多出来的标签追加到
      原本含有同类标签的叶子之后；缺失的直接忽略并告警
用法:
  python3 fix_tags.py RPGSystem/rpg-loc-dialogue-floor-2.json --apply
"""
from __future__ import annotations

if __name__ == "__main__":
    raise SystemExit("旧批次入口已退役。请读 workflow/版本更新流程.md，使用 snapshot / scope / batch；不会写入旧目录。")


import json
import os
import re
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_KB_DIR, "tools"))
import pm_lib as P  # noqa: E402
from build_translation import STRICT_TAG  # noqa: E402

TR_DIR = os.path.join(_KB_DIR, "translate")
OUT_DIR = os.path.join(_KB_DIR, "out", "LLC_zh-CN")


def find_container_paths(rec):
    """找出所有「子节点全是字符串叶子」的 list/dict 容器路径。"""
    res = []
    def walk(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                p = f"{path}.{k}" if path else k
                if isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
                    for i, sub in enumerate(v):
                        walk(sub, f"{p}[{i}]")
                    res.append(p)
                elif isinstance(v, dict):
                    walk(v, p)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")
    walk(rec)
    return res


def collect_text_paths(rec, container):
    """返回容器下按顺序的文本叶子路径（如 texts[0].text）。"""
    cur = rec
    toks = re.findall(r"([^.\[\]]+)|\[(\d+)\]", container)
    for name, idx in toks:
        cur = cur[name] if name else cur[int(idx)]
    out = []
    if isinstance(cur, list):
        for i, sub in enumerate(cur):
            if isinstance(sub, dict):
                for k, v in sub.items():
                    if isinstance(v, str):
                        out.append(f"{container}[{i}].{k}")
    elif isinstance(cur, dict):
        for k, v in cur.items():
            if isinstance(v, str):
                out.append(f"{container}.{k}")
    return out


def get_by_path(rec, path):
    cur = rec
    for name, idx in re.findall(r"([^.\[\]]+)|\[(\d+)\]", path):
        cur = cur[name] if name else cur[int(idx)]
    return cur


def set_by_path(rec, path, value):
    toks = re.findall(r"([^.\[\]]+)|\[(\d+)\]", path)
    cur = rec
    for i, (name, idx) in enumerate(toks):
        key = name if name else int(idx)
        if i == len(toks) - 1:
            cur[key] = value
        else:
            cur = cur[key]


def container_tags(rec, container):
    seq = []
    for p in collect_text_paths(rec, container):
        seq.extend(STRICT_TAG.findall(get_by_path(rec, p)))
    return seq


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return
    logical = argv[1].replace("__", "/")
    apply = "--apply" in argv
    idx = P.build_index()
    stem = logical.replace("/", "__")[:-5] + ".tsv"
    tsv = next((c for c in (os.path.join(TR_DIR, stem), os.path.join(TR_DIR, "_out", stem))
                if os.path.exists(c)), None)
    if not tsv:
        raise SystemExit("找不到译文表 " + stem)
    # 当前译文 JSON（由译文表构建，结构同英文）
    with open(os.path.join(P.LANG_DIR["en"], idx[logical]["en"]), encoding="utf-8") as fh:
        en_src = json.load(fh)
    en_by = {}
    for r in (en_src["dataList"] if isinstance(en_src, dict) else en_src):
        en_by[str(r.get("id", r.get("key")))] = r
    with open(os.path.join(OUT_DIR, logical), encoding="utf-8") as fh:
        cn_doc = json.load(fh)
    cn_by = {str(r.get("id", r.get("key"))): r for r in (cn_doc["dataList"] if isinstance(cn_doc, dict) else cn_doc)}

    # 建立 (id, 叶子路径) -> 新值 的映射
    updates: dict[tuple[str, str], str] = {}
    for rid, en_rec in en_by.items():
        cn_rec = cn_by.get(rid)
        if not cn_rec:
            continue
        for container in find_container_paths(en_rec):
            en_paths = collect_text_paths(en_rec, container)
            cn_paths = collect_text_paths(cn_rec, container)
            if len(en_paths) != len(cn_paths):
                continue
            en_seq, cn_seq = container_tags(en_rec, container), container_tags(cn_rec, container)
            if en_seq == cn_seq:
                continue
            if len(en_seq) == len(cn_seq):
                # 数量相同 → 按顺序重新分配
                it = iter(en_seq)
                for p_e, p_c in zip(en_paths, cn_paths):
                    n = len(STRICT_TAG.findall(get_by_path(en_rec, p_e)))
                    want = [next(it) for _ in range(n)]
                    base = STRICT_TAG.sub("", get_by_path(cn_rec, p_c))
                    # 保持「开标签在前、闭标签在后」的简单排布
                    opens = [t for t in want if not t.startswith("</")]
                    closes = [t for t in want if t.startswith("</")]
                    updates[(rid, p_c)] = "".join(opens) + base + "".join(closes)
                print(f"  ✅ {rid}: 重排 {len(en_seq)} 个标签（{container}）")
            else:
                print(f"  ⚠ {rid}: 标签数不一致 EN={len(en_seq)} CN={len(cn_seq)}（{container}）→ 跳过，需人工")
    print(f"\n可自动修复叶子数: {len(updates)}（{'写入' if apply else '试运行'}）")
    if apply and updates:
        # 写回译文表
        out_lines = []
        for line in open(tsv, encoding="utf-8"):
            if line.startswith("#") or not line.strip():
                out_lines.append(line)
                continue
            c = line.rstrip("\n").split("\t")
            key = (c[0], c[1])
            if len(c) >= 3 and key in updates:
                c[2] = updates[key].replace("\n", "\\n")
            out_lines.append("\t".join(c) if len(c) >= 3 else line)
        open(tsv, "w", encoding="utf-8").write("\n".join(l.rstrip("\n") for l in out_lines) + "\n")
        print("已写回", tsv)


if __name__ == "__main__":
    main(sys.argv)
