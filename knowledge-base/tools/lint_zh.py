#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中文译文专项质检：查术语、标点、口吻红线、残留英文。

与 verify_output.py 的分工：
  verify_output.py  → 与英文源对比（结构/标记/占位符），机器可判定
  本脚本            → 只看中文译文本身的质量问题，机器可判定的部分

用法:
  python3 lint_zh.py                     # 扫 out/LLC_zh-CN 下全部
  python3 lint_zh.py StoryData/S1002B.json
"""
from __future__ import annotations

import json
import os
import re
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_KB_DIR, "tools"))
import pm_lib as P  # noqa: E402
from build_translation import walk_strings, BRACKET, is_engine_bracket, DEV_FIELDS, STRICT_TAG  # noqa: E402

OUT_DIR = os.path.join(_KB_DIR, "out", "LLC_zh-CN")

CJK = re.compile(r"[\u4e00-\u9fff]")
LATIN = re.compile(r"[A-Za-z]")

# ── 禁止/错误的写法 → 说明 ────────────────────────────────
# 术语误译：左边是错误的写法（英文原词），右边是应使用的译名
BAD_TERMS = [
    # 注意：Coin 在战斗语境既有译法就是「硬币」（Coin Power→硬币威力，
    # Unbreakable Coin→不可摧毁的硬币）；仅镜像迷宫的 E.G.O 饰品名作「铜钱」。
    # 故此处不再把「硬币」判为错误。
    # 说明：以下只收「一定是误译」的词。像 身份/巢穴/平衡 这类
    # 在普通语境内完全正确的词不收（英文 identity/nest/balance 作普通名词时
    # 本就该译「身份/巢穴/平衡」，例如 "uncover her identity"→「弄清她的身份」）。
    ("修复者", "Fixer 应为「收尾人」"),
    ("无名指", "The Ring 应为「环指」"),
    ("世界之翼", "语料不存在此写法，只有「翼」"),
    ("协助防御", "Assist Defense 既有译法为「援护防御」"),
    ("大百货店", "应为「西西弗百货」"),
    ("西西弗大百货店", "应为「西西弗百货」"),
]
# 标点错误
PUNCT_RULES = [
    ("「", "直角引号「」全库 0 例，应用弯引号 “”"),
    ("」", "直角引号「」全库 0 例，应用弯引号 “”"),
    ("~~~", "波浪号异常重复"),
]

# ── 未译残留：中文值与英文源完全相同、且看起来是英文句子 ─────────────
# 白名单：品牌名/专名/缩写/纯符号，允许保留原文
KEEP_AS_IS = re.compile(
    r"^(?:"
    r"Le Noir|Le Rouge|Haute Couture|Boutique[^\u4e00-\u9fff]*|Maison[^\u4e00-\u9fff]*|"
    r"L'Inamovible|L'Incolore|Avant|Garde|G\.M\. Sisyphe|PUNCTUM|"
    r"E\.G\.O[^\u4e00-\u9fff]*|LCCB|LCE|LCC|"
    r"[A-Z] ?Corp\.[^\u4e00-\u9fff]*|.+::.+|ma puce|coq au vin|Café de Flore|"
    r"[-\d\s\.%×+*/#@!?？！，。、“”…:：()（）\[\]{}<>=]*"
    r")$"
)

# 已知「有意保留」的英文/拉丁条目（品牌名、缩写、法语术语、韩文内部标识等）
KEEP_LIST = {
    "FOMO", "Armure Éveillée", "Le Noir Hammer", "Prêt-à-porter",
    "L'Inamovible", "L'Incolore", "Le Noir", "Le Rouge", "Haute Couture",
    "뉴비1 npc", "달퐁이 사체",
}


def is_intentional(ev: str) -> bool:
    t = ev.strip()
    if t in KEEP_LIST:
        return True
    # 纯法文/拉丁术语（含变音符号），原文保留
    inner = t.strip("<>").strip()
    if inner in KEEP_LIST:
        return True
    if re.fullmatch(r"[A-Za-zÀ-ÿ'’\-\s]+", inner):
        return True
    if t.startswith("<") and t.endswith(">") and re.search(r"[éèêàç]", t):
        return True          # 法语术语心声，如 <Prêt-à-porter?>
    if re.search(r"[\uac00-\ud7af]", t):
        return True          # 韩文内部标识/开发备注
    if re.search(r"\bSD\b|클론|오브젝트|화장실", t):
        return True
    return False


def check_untranslated(rec, en_rec, rid: str, issues: list[str]) -> None:
    """对比英文源，找出「中文侧与英文完全相同且含拉丁单词」的字段。"""
    import json as _json
    for path, ev in walk_strings(en_rec):
        leaf = path.split(".")[-1].split("[")[0]
        if leaf in DEV_FIELDS or leaf in ("id", "key"):
            continue
        if not isinstance(ev, str) or not ev.strip():
            continue
        # 取中文同路径
        cur = rec
        ok = True
        for name, ix in re.findall(r"([^.\[\]]+)|\[(\d+)\]", path):
            try:
                cur = cur[name] if name else cur[int(ix)]
            except Exception:
                ok = False
                break
        if not ok or not isinstance(cur, str):
            continue
        if cur.strip() != ev.strip():
            continue
        if not re.search(r"[A-Za-z]{3,}", ev) or KEEP_AS_IS.match(ev.strip()):
            continue
        if is_intentional(ev):
            continue
        # 纯引擎标签 / 纯富文本标签（无可译文字）不算未译
        stripped = STRICT_TAG.sub("", BRACKET.sub("", ev)).strip(" .。·-—…")
        if not stripped:
            continue
        issues.append(f"id={rid}.{path} 疑似未译（与英文源完全相同）\n      {ev[:90]}")


# 角色口吻红线
def load_speakers():
    return {
        "이상": ("李箱", [("吾", "李箱全语料「吾」0 次"), ("汝", "李箱全语料「汝」0 次")]),
        "료슈": ("良秀", []),
        "뫼르소": ("默尔索", [("啊", "默尔索几乎不用语气词"), ("吧", "默尔索几乎不用语气词")]),
        "돈키호테": ("堂吉诃德", []),
    }


def lint_file(logical: str) -> tuple[int, list[str]]:
    idx = P.build_index()
    b = os.path.basename(logical)
    if b.startswith(("EN_", "KR_", "JP_")):
        b = b[3:]
    d = os.path.dirname(logical)
    rel = os.path.join(d, b) if d else b
    path = os.path.join(OUT_DIR, rel)
    if not os.path.exists(path):
        return 0, []
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    en_recs = {}
    if logical in idx and "en" in idx[logical]:
        for r in P.load_file("en", idx[logical]["en"]):
            en_recs[str(r.get("id", r.get("key", "")))] = r
    recs = data["dataList"] if isinstance(data, dict) and "dataList" in data else data
    if isinstance(recs, dict):
        recs = [recs]
    issues: list[str] = []
    checked = 0
    # 说话人：从 kr 源取 model
    models: dict[str, str] = {}
    if logical in idx and "kr" in idx[logical]:
        for r in P.load_file("kr", idx[logical]["kr"]):
            rid = str(r.get("id", r.get("key", "")))
            m = r.get("model")
            if isinstance(m, str) and CJK.search(m) is False and m:
                models[rid] = m
    for rec in recs:
        if not isinstance(rec, dict):
            continue
        rid = str(rec.get("id", rec.get("key", "")))
        if rid in en_recs:
            check_untranslated(rec, en_recs[rid], rid, issues)
        for fpath, val in walk_strings(rec):
            if not CJK.search(val):
                continue
            checked += 1
            # 术语误译
            for bad, why in BAD_TERMS:
                if bad in val:
                    issues.append(f"id={rid}.{fpath} 术语可疑「{bad}」：{why}\n      {val[:90]}")
            # 标点
            for bad, why in PUNCT_RULES:
                if bad in val:
                    issues.append(f"id={rid}.{fpath} 标点「{bad}」：{why}\n      {val[:90]}")
            # 中英之间空格：本批为品牌名（Le Rouge 等）刻意加空格，属中文排版惯例，
            # 语料中无空格 : 有空格 ≈ 19:1，但主要是 W公司/K公司 这类专名连写，
            # 故仅在中英边界**且为纯小写英文单词**时提示，供人工判断，不算错误。
            if re.search(r"[\u4e00-\u9fff] [a-z]{2,}|[a-z]{2,} [\u4e00-\u9fff]", val):
                issues.append(f"id={rid}.{fpath} 中英空格请确认是有意（品牌名可保留）\n      {val[:90]}")
            # 显示性方括号未译（引擎标签已由 verify_output 严格校验，此处查显示性）
            for tok in BRACKET.findall(val):
                inner = tok[1:-1].strip()
                if not is_engine_bracket(inner) and LATIN.search(inner) and not CJK.search(inner):
                    issues.append(f"id={rid}.{fpath} 显示性方括号疑似未译：{tok}\n      {val[:90]}")
            # 角色口吻红线
            m = models.get(rid)
            if m in ("이상",):
                for w in ("吾", "汝"):
                    if w in val:
                        issues.append(f"id={rid}.{fpath} 李箱不应使用「{w}」\n      {val[:90]}")
    return checked, issues


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
    total_fields = total_issues = 0
    bad_files = 0
    for logical in targets:
        checked, issues = lint_file(logical)
        if checked == 0:
            continue
        total_fields += checked
        total_issues += len(issues)
        if issues:
            bad_files += 1
            print(f"⚠ {logical}  ({len(issues)} 处)")
            for s in issues[:8]:
                print("   ", s)
    print(f"\n扫描 {len(targets)} 文件 / {total_fields} 个中文字段；"
          f"{bad_files} 个文件有 {total_issues} 处提示")


if __name__ == "__main__":
    main(sys.argv)
