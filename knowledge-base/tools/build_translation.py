#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把译文映射合并回官方英文 JSON，生成汉化包格式的中文文件。

设计要点（保证美术风格零改动）：
  1. **结构/键序/缩进完全照抄英文源文件**，只替换指定字段的字符串值；
  2. 未提供译文的字段**原样保留英文**（宁可漏译，不可破坏）；
  3. 合并后自动校验：颜色/样式标签、引擎标签、占位符是否与英文逐字符一致；
  4. 输出文件名去掉语言前缀（EN_ → 无），与汉化包目录结构一致。

译文表格式（TSV，UTF-8）:
  id<TAB>字段名<TAB>译文
  - 译文中的 \\n 会被还原为真实换行
  - 以 # 开头的行为注释

用法:
  python3 build_translation.py <英文源文件路径或逻辑名> <译文表路径> [-o 输出目录]
  python3 build_translation.py --all <译文表目录>            # 批量
"""
from __future__ import annotations

if __name__ == "__main__":
    raise SystemExit("旧批次入口已退役。请读 workflow/版本更新流程.md，使用 snapshot / scope / batch；不会写入旧目录。")


import json
import os
import re
import shutil
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_KB_DIR, "tools"))
import pm_lib as P  # noqa: E402

CN_DIR = P.CN_LOCALIZE
OUT_DIR = os.path.join(_KB_DIR, "out", "LLC_zh-CN")

ANGLE = re.compile(r"<[^>\n]*>")
BRACKET = re.compile(r"\[([^\]\n]*)\]")
PLACEHOLDER = re.compile(r"\{[^{}\n]*\}")
ENGINE_TAG = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# 颜色/样式/强调标签：必须逐字符一致
# 注意：**不加 re.I**。但丁的心声用 <I ...> 包裹（官方中文同样保留 <...>），
# 若忽略大小写会把 <I think...> 误判成斜体标签 <i>。
# 只认「自闭合标签」或「标签名后紧跟 = 属性」两种形态，
# 且不加 re.I —— 否则 <I think...>/<...> 这类**心声文本**会被误判。
STRICT_TAG = re.compile(
    r"<(?:/?(?:color|mark|b|u|i|s|noparse|size|voffset|cspace|style|sprite|link)"
    r"(?:\s*=[^>\n]*)?)>"
)

# ---------------------------------------------------------------------------
# 方括号里的内容有两种性质，不能一律当引擎标签：
#   (a) 引擎标签：[Vibration] [Sinking] [OnSucceedAttack] … → 原样保留
#   (b) 显示文本：[Crimson] [Season 8] [Inchoate Life] … → 必须翻译
#
# 判别依据（数据驱动，非人工猜测）：真正的引擎标签在**韩/日/中**三种语言里
# 都至少有一处保留 `[拉丁原文]`；而显示文本在三语里都被译成本国文字。
# 例：BattleKeywords-a1c10p1 的 `Baptism [Crimson]`
#     KR `세례[적]` / JP `洗礼[赤]` / CN `洗礼[赤]` —— 三语全译 ⇒ 是显示文本。
#     （对照 `[Laceration]`：KR/JP/CN 均保留 `[Laceration]` ⇒ 是引擎标签。）
#
# 实现：直接扫描 data/corpus.jsonl，收集「韩/日/中语料里**从未**以 [拉丁] 形式
# 出现过、但英文侧出现过」的标记 → 这些就是被翻译的显示文本。
# 结果缓存在 data/_display_brackets.json，避免每次构建都重扫 106MB 语料。
# 删除缓存即可重新推导。
_DISPLAY_CACHE = os.path.join(_KB_DIR, "data", "_display_brackets.json")
_DISPLAY_BRACKET: set[str] | None = None


def is_engine_bracket(token: str) -> bool:
    """判定方括号内容是「引擎标签」还是「显示文本」。

    引擎标签：拉丁标识符（无空格），且该标记在韩/日/中语料中从未被翻译。
    显示文本：含空格的多词短语（如 "Season 8" / "Inchoate Life"），
              或已被 display_brackets() 判定为显示性的标记（如 "Crimson"）。
    """
    t = token.strip()
    if not ENGINE_TAG.match(t):
        return False          # 含空格/标点/非 ASCII → 显示文本
    return t not in display_brackets()


def display_brackets() -> set[str]:
    """返回应被视为**显示文本**（可翻译）的方括号标记集合。"""
    global _DISPLAY_BRACKET
    if _DISPLAY_BRACKET is not None:
        return _DISPLAY_BRACKET
    if os.path.exists(_DISPLAY_CACHE):
        try:
            with open(_DISPLAY_CACHE, encoding="utf-8") as fh:
                _DISPLAY_BRACKET = set(json.load(fh))
            return _DISPLAY_BRACKET
        except Exception:
            pass
    corpus = os.path.join(_KB_DIR, "data", "corpus.jsonl")
    out: set[str] = set()
    if os.path.exists(corpus):
        en_seen: set[str] = set()
        other_seen: set[str] = set()
        with open(corpus, encoding="utf-8") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                toks = {
                    t.strip() for t in BRACKET.findall(r.get("t", ""))
                    if ENGINE_TAG.match(t.strip())
                }
                if r.get("l") == "en":
                    en_seen |= toks
                elif r.get("l") in ("kr", "jp", "cn"):
                    other_seen |= toks
        out = en_seen - other_seen
    try:
        with open(_DISPLAY_CACHE, "w", encoding="utf-8") as fh:
            json.dump(sorted(out), fh, ensure_ascii=False, indent=1)
    except Exception:
        pass
    _DISPLAY_BRACKET = out
    return out


def load_translations(path: str) -> dict[tuple[str, str], str]:
    """读译文表 → {(id, field): text}"""
    out: dict[tuple[str, str], str] = {}
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                print(f"  ⚠ 第 {lineno} 行字段不足，跳过: {line[:60]!r}")
                continue
            rid, field, text = parts[0], parts[1], "\t".join(parts[2:])
            out[(rid, field)] = text.replace("\\n", "\n")
    return out


def tags_of(text: str) -> tuple[list[str], list[str], list[str]]:
    strict = sorted(STRICT_TAG.findall(text))
    disp = display_brackets()
    # 引擎标签：拉丁标识符，且不属于"三语均已译出"的显示文本
    engine = sorted(
        t for t in BRACKET.findall(text)
        if ENGINE_TAG.match(t.strip()) and t.strip() not in disp
    )
    ph = sorted(PLACEHOLDER.findall(text))
    return strict, engine, ph


# 开发用元数据字段：内容是韩文制作备注，不是玩家可见文本，禁止翻译
DEV_FIELDS = {"id", "key", "_id", "coindescs_index", "index", "level", "coinindex", "subIndex"}


def walk_strings(node, path: str = ""):
    """递归产出 (路径, 字符串)。路径形如 levelList[0].name / texts[3]"""
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str):
                yield (f"{path}.{k}" if path else k), v
            elif isinstance(v, (dict, list)):
                yield from walk_strings(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            p = f"{path}[{i}]"
            if isinstance(v, str):
                yield p, v
            elif isinstance(v, (dict, list)):
                yield from walk_strings(v, p)


def set_by_path(node, path: str, value: str) -> None:
    """按路径写回（只写已存在的字符串叶子）。"""
    cur = node
    tokens = re.findall(r"([^.\[\]]+)|\[(\d+)\]", path)
    for i, (name, idx) in enumerate(tokens):
        last = i == len(tokens) - 1
        key = name if name else int(idx)
        if last:
            cur[key] = value
        else:
            cur = cur[key]


def translate_record(rec: dict, rid: str, tr, problems: list[str], stats: list[int],
                     skip_fields: set[str], untranslated: list[str]) -> None:
    """就地翻译一条记录里的所有字符串叶子。"""
    for path, val in list(walk_strings(rec)):
        if not val.strip():
            continue
        leaf = path.split(".")[-1].split("[")[0]
        if leaf in DEV_FIELDS or leaf in skip_fields:
            continue
        stats[1] += 1
        key = (rid, path)
        if key not in tr:
            stats.append(0)  # 占位，略
            untranslated.append(f"{rid}.{path}")
            continue
        cn = tr[key]
        a, b, c = tags_of(val)
        x, y, z = tags_of(cn)
        if a != x:
            problems.append(f"id={rid}.{path} 颜色/样式标签不一致\n    EN: {a}\n    CN: {x}")
        if b != y:
            problems.append(f"id={rid}.{path} 引擎标签不一致\n    EN: {b}\n    CN: {y}")
        if c != z:
            problems.append(f"id={rid}.{path} 占位符不一致\n    EN: {c}\n    CN: {z}")
        set_by_path(rec, path, cn)
        stats[0] += 1


def merge(en_path: str, tr, skip_fields: set[str] | None = None):
    """返回 (合并后的对象, 问题列表, 已译数, 总数)"""
    with open(en_path, encoding="utf-8") as fh:
        data = json.load(fh)
    recs = data["dataList"] if isinstance(data, dict) and "dataList" in data else data
    if isinstance(recs, dict):
        recs = [recs]
    problems: list[str] = []
    stats = [0, 0]  # [已译, 总数]
    untranslated: list[str] = []
    for rec in recs:
        if not isinstance(rec, dict):
            continue
        rid = str(rec.get("id", rec.get("key", rec.get("_id", ""))))
        translate_record(rec, rid, tr, problems, stats, skip_fields or set(), untranslated)
    return data, problems, stats[0], stats[1], untranslated


def output_name(logical: str) -> str:
    """逻辑名 → 汉化包内的相对路径（去掉 EN_ 前缀）。"""
    d, b = os.path.split(logical)
    if b.startswith(("EN_", "KR_", "JP_")):
        b = b[3:]
    return os.path.join(d, b) if d else b


def build_one(logical: str, tr_path: str, out_dir: str) -> None:
    idx = P.build_index()
    if logical not in idx or "en" not in idx[logical]:
        raise SystemExit(f"找不到英文源文件: {logical}")
    en_path = os.path.join(P.LANG_DIR["en"], idx[logical]["en"])
    tr = load_translations(tr_path)
    # 每文件可选的跳过字段：与译文表同目录的 <tsv名>.skip，每行一个字段名
    skip_fields: set[str] = set()
    skip_path = tr_path + ".skip"
    if os.path.exists(skip_path):
        with open(skip_path, encoding="utf-8") as fh:
            skip_fields = {ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")}
    data, problems, done, total, untranslated = merge(en_path, tr, skip_fields)
    rel = output_name(logical)
    dest = os.path.join(out_dir, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    name = os.path.basename(dest)
    if problems:
        print(f"❌ {name}: 已译 {done}/{total}，但发现 {len(problems)} 处标记问题：")
        for p in problems[:12]:
            print("   ", p)
    else:
        print(f"✅ {name}: 已译 {done}/{total} 字段，标记校验全部通过 → {dest}")
    if untranslated:
        print(f"   ⚠ 未译 {len(untranslated)} 条：{untranslated[:6]}")


def main(argv: list[str]) -> None:
    if len(argv) < 3:
        print(__doc__)
        return
    out_dir = OUT_DIR
    args = argv[1:]
    if "-o" in args:
        i = args.index("-o")
        out_dir = args[i + 1]
        del args[i:i + 2]
    if args[0] == "--all":
        trdir = args[1]
        idx = P.build_index()
        for fn in sorted(os.listdir(trdir)):
            if not fn.endswith(".tsv"):
                continue
            logical = fn[:-4].replace("__", "/")
            if logical not in idx:
                print(f"⚠ 跳过 {fn}（逻辑名 {logical} 不在索引中）")
                continue
            build_one(logical, os.path.join(trdir, fn), out_dir)
    else:
        build_one(args[0], args[1], out_dir)


if __name__ == "__main__":
    main(sys.argv)
