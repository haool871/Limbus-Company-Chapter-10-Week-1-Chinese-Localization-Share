#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""译文质检：对比英文基准文件与中文译文文件。

用法:
  python3 qa_check.py <en.json> <cn.json>
  python3 qa_check.py --official StoryData/1D101A.json     # 用已装官方英文做基准

检查项:
  1. id 覆盖：英文有而中文缺的记录
  2. 标记完整性：[] 方括号标签、<style=...> 标签、{0} 占位符 是否逐字符一致
  3. 空译文 / 未翻译（中文侧仍含大量英文）
  4. 长度异常（中文字数 / 英文词数 明显偏离经验区间）
"""
from __future__ import annotations

import json
import os
import re
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_KB_DIR, "tools"))
import pm_lib as P  # noqa: E402

BRACKET = re.compile(r"\[([^\]\n]*)\]")
ANGLE = re.compile(r"<[^>\n]*>")
PLACEHOLDER = re.compile(r"\{[^{}\n]*\}")
CJK = re.compile(r"[\u4e00-\u9fff]")
LATIN = re.compile(r"[A-Za-z]")

# 方括号里是**引擎标签**（拉丁标识符）：必须原样保留
ENGINE_TAG = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# 方括号里是**显示文本**（人名、状态名等）：应随语言翻译
# 例：[Hong Lu] → [鸿璐]，[<s>Great Sister</s>] → [<s>长姊</s>]
# 注意：零协会有时会删除 <s>/<i> 等样式标签，故样式标签不匹配只告警

# 长度经验区间（字/词），取自 workflow/翻译流程.md §5.4
RATIO = {"default": (1.2, 3.2), "Skills": (2.5, 7.5), "Passives": (2.5, 7.5),
         "BattleKeywords": (1.5, 4.0), "Bufs": (1.5, 4.0)}


def load(path: str) -> dict[str, dict]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    recs = data.get("dataList", data) if isinstance(data, dict) else data
    out = {}
    for i, r in enumerate(recs):
        key = str(r.get("id", r.get("key", f"#{i}")))
        out.setdefault(key, r)
    return out


def fields(rec: dict) -> dict[str, str]:
    return {k: v for k, v in rec.items()
            if isinstance(v, str) and k not in ("id", "key")}


def ratio_bounds(name: str) -> tuple[float, float]:
    base = os.path.basename(name).split("-")[0].split("_")[0]
    return RATIO.get(base, RATIO["default"])


def main(argv: list[str]) -> None:
    if len(argv) < 3:
        print(__doc__)
        return
    if argv[1] == "--official":
        logical = argv[2].replace("\\", "/")
        A = P.align(logical)
        idx = P.build_index()
        en_path = os.path.join(P.LANG_DIR["en"], idx[logical]["en"])
        cn_path = os.path.join(P.LANG_DIR["cn"], idx[logical]["cn"])
        name = logical
    else:
        en_path, cn_path = argv[1], argv[2]
        name = os.path.basename(cn_path)

    en, cn = load(en_path), load(cn_path)
    problems = 0

    missing = [k for k in en if k not in cn]
    extra = [k for k in cn if k not in en]
    if missing:
        problems += len(missing)
        print(f"[缺译] 英文有 {len(missing)} 条中文缺失：{missing[:20]}{' ...' if len(missing) > 20 else ''}")
    if extra:
        print(f"[多余] 中文多出 {len(extra)} 条 id：{extra[:10]}")

    lo, hi = ratio_bounds(name)
    for k in en:
        if k not in cn:
            continue
        ef, cf = fields(en[k]), fields(cn[k])
        for f, ev in ef.items():
            if not isinstance(ev, str):
                continue
            cv = cf.get(f)
            if cv is None:
                print(f"[缺字段] id={k} 字段 {f} 中文缺失")
                problems += 1
                continue
            # 1) 引擎标签（方括号内的拉丁标识符）必须原样保留。
            #    但方括号里也可能是**显示文本**（人名/状态名），如 [Heathcliff] → [希斯克利夫]。
            #    判别：若中文侧同名标签被改为中文，说明它是显示文本，属正常翻译；
            #    若中文侧出现纯 ASCII 标签且英文侧没有，才是真问题。
            a = sorted(BRACKET.findall(ev))
            b = sorted(BRACKET.findall(cv))
            engine_b_only = sorted(
                t for t in b
                if ENGINE_TAG.match(t.strip()) and t not in a
            )
            if engine_b_only:
                print(f"[引擎标签多余] id={k}.{f} 中文侧出现英文侧没有的标签: {engine_b_only}\n"
                      f"    EN: {a}\n    CN: {b}")
                problems += 1
            # 若英文侧有引擎标签而中文侧整组消失，提示（可能是漏译）
            if a and not b and any(ENGINE_TAG.match(t.strip()) for t in a):
                print(f"[引擎标签丢失?] id={k}.{f} 英文有标签 {a}，中文无任何方括号")
                problems += 1
            # 1b) {} 占位符必须一致
            pa, pb = sorted(PLACEHOLDER.findall(ev)), sorted(PLACEHOLDER.findall(cv))
            if pa != pb:
                print(f"[占位符不符] id={k}.{f}\n    EN: {pa}\n    CN: {pb}")
                problems += 1
            # 1c) 显示类方括号（人名等）应被翻译：若中文侧与英文侧**完全相同**
            #     且内容是拉丁字母单词，则疑似漏译（引擎标签不在此列）
            disp_a = [t.strip() for t in a if not ENGINE_TAG.match(t.strip())]
            disp_b = [t.strip() for t in b if not ENGINE_TAG.match(t.strip())]
            if disp_a and sorted(disp_a) == sorted(disp_b):
                latin_disp = [t for t in disp_a if LATIN.search(t) and not CJK.search(t)]
                if latin_disp:
                    print(f"[方括号显示文本疑似未译] id={k}.{f}: {latin_disp}")
                    problems += 1
            # 1d) 样式标签 <s>/<i> 等：允许删除，仅告警
            aa, bb = ANGLE.findall(ev), ANGLE.findall(cv)
            if aa and not bb:
                print(f"[提示] id={k}.{f} 中文删除了样式标签 {sorted(set(aa))}（零协会有此习惯，确认是否有意）")
            # 2) 中文侧未翻译
            if not CJK.search(cv) and LATIN.search(cv) and LATIN.search(ev):
                print(f"[疑似未译] id={k}.{f}: {cv[:80]}")
                problems += 1
            # 3) 空译文
            if ev.strip() and not cv.strip():
                print(f"[空译] id={k}.{f}")
                problems += 1
            # 4) 长度异常（先剥离 <...> 样式标签与 [...] 标记，否则富文本会误报）
            ew = len(ANGLE.sub("", BRACKET.sub("", ev)).split())
            cc = len(ANGLE.sub("", BRACKET.sub("", cv)))
            if ew >= 4 and cc >= 4:
                r = cc / ew
                if r < lo * 0.6 or r > hi * 1.6:
                    print(f"[长度异常] id={k}.{f} 英文{ew}词/中文{cc}字 比值{r:.1f}（经验 {lo}-{hi}）")
                    problems += 1

    print(f"\n检查完成：{name}  英文 {len(en)} 条 / 中文 {len(cn)} 条 / 问题 {problems} 处")
    if problems == 0:
        print("✅ 未发现结构性问题（语义仍需人工通读）")


if __name__ == "__main__":
    main(sys.argv)
