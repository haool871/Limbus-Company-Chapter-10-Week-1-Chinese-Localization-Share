#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按索引译文表生成缺口补丁文件。

输入：`/tmp/gaps2.json`（缺口条目列表）与索引键译文表（JSON: {"索引": "中文"}）。
输出：patch/LLC_zh-CN/<相对路径>（补齐后的完整文件，可直接安装）。
校验：`<...>` 样式标签与 `[...]` 引擎标签必须与英文源完全一致。
"""
from __future__ import annotations

if __name__ == "__main__":
    raise SystemExit("旧批次入口已退役。请读 workflow/版本更新流程.md，使用 snapshot / scope / batch；不会写入旧目录。")


import json
import os
import re
import sys

_KB = "/home/shb/文档/汉化/_kb"
sys.path.insert(0, os.path.join(_KB, "tools"))
from build_translation import walk_strings, DEV_FIELDS, is_engine_bracket  # noqa: E402
from fill_gaps import EN_DIR, LD, PATCH  # noqa: E402

ANGLE = re.compile(r"<[^>\n]*>")
BRACKET = re.compile(r"\[[^\]\n]*\]")


def apply_gaps(gaps: list[list], tr: dict[str, str], label: str) -> int:
    by_file: dict[str, dict[str, str]] = {}
    for i, (fn, rid, path, en) in enumerate(gaps):
        if str(i) in tr:
            by_file.setdefault(fn, {})[f"{rid}|{path}"] = tr[str(i)]

    made = 0
    for fn, mapping in by_file.items():
        en_p = os.path.join(EN_DIR, "EN_" + fn)
        if not os.path.exists(en_p):
            print(f"  ⚠ 跳过 {fn}（英文源不存在）")
            continue
        en_doc = json.load(open(en_p, encoding="utf-8-sig"))
        cnp = os.path.join(LD, fn)
        if os.path.exists(cnp):
            cn_doc = json.load(open(cnp, encoding="utf-8-sig"))
        else:
            cn_doc = dict(en_doc)          # 中文缺失则新建
            cn_doc["dataList"] = []
        cn_list = cn_doc.get("dataList", [])
        by_id = {str(r.get("id", r.get("key"))): r for r in cn_list}

        new = 0
        for r in en_doc.get("dataList", []):
            rid = str(r.get("id", r.get("key")))
            if rid in by_id:
                continue
            rec = json.loads(json.dumps(r, ensure_ascii=False))
            for path, ev in walk_strings(rec):
                if path.split(".")[-1].split("[")[0] in DEV_FIELDS:
                    continue
                cn = mapping.get(f"{rid}|{path}")
                if cn is None:
                    continue
                # 标记校验
                # 引擎标签用与主构建脚本相同的判定（豁免显示性方括号如 [Aggro]）
                e_eng = sorted(t for t in BRACKET.findall(ev) if is_engine_bracket(t))
                c_eng = sorted(t for t in BRACKET.findall(cn) if is_engine_bracket(t))
                if sorted(ANGLE.findall(ev)) != sorted(ANGLE.findall(cn)) or e_eng != c_eng:
                    print(f"  ❌ 标记不一致 {fn} {rid}.{path}")
                    print(f"     EN<> {sorted(ANGLE.findall(ev))}")
                    print(f"     CN<> {sorted(ANGLE.findall(cn))}")
                    continue
                cur = rec
                toks = re.findall(r"([^.\[\]]+)|\[(\d+)\]", path)
                for j, (nm, ix) in enumerate(toks):
                    k = nm if nm else int(ix)
                    if j == len(toks) - 1:
                        cur[k] = cn
                    else:
                        cur = cur[k]
            by_id[rid] = rec
            new += 1

        enids = {str(r.get("id", r.get("key"))) for r in en_doc.get("dataList", [])}
        ordered = [by_id[str(r.get("id", r.get("key")))] for r in en_doc.get("dataList", [])
                   if str(r.get("id", r.get("key"))) in by_id]
        ordered += [r for r in cn_list if str(r.get("id", r.get("key"))) not in enids]
        out = dict(cn_doc)
        out["dataList"] = ordered
        dst = os.path.join(PATCH, fn)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        print(f"  ✅ {fn}: 补 {new} 条（共 {len(ordered)} 条）")
        made += 1
    return made


if __name__ == "__main__":
    gaps = json.load(open("/tmp/gaps2.json", encoding="utf-8"))
    tr = json.load(open("/tmp/pass_tr.json", encoding="utf-8"))
    tr.update(json.load(open("/tmp/rest_tr.json", encoding="utf-8")))
    print(f"译文条目 {len(tr)} / 缺口 {len(gaps)}")
    apply_gaps(gaps, tr, "all")
