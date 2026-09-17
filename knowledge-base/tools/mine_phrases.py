#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""句式模板挖掘：从官方英中对照里自动提炼「英文句式 → 中文固定说法」。

输入: terms/desc_pairs.jsonl 与 data/corpus.jsonl（按 f+id 对齐 en/cn）
算法:
  1. 英文侧把数字、{n}、[标记]、<样式> 归一化为占位类，得到"句式模式"；
  2. 相同模式聚合，统计频次；
  3. 输出高频模式的代表性与多样中文样例，供人工定义模板。

输出:
  terms/phrase_patterns.tsv   pattern<TAB>count<TAB>en_example<TAB>cn_example
  terms/_phrase_samples.jsonl 每个模式最多 8 组中英实例
  terms/_review/phrases.md    人工整理的句式模式表 + 真实中英样例（精编用证据）

模式:
  python3 tools/mine_phrases.py             # 两部分都跑
  python3 tools/mine_phrases.py --patterns  # 只跑自动模式挖掘
  python3 tools/mine_phrases.py --curated   # 只跑句式证据报告
  python3 tools/mine_phrases.py --curated --top 20
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(_KB_DIR, "data")
TERMS = os.path.join(_KB_DIR, "terms")

NUM = re.compile(r"\b\d+(?:\.\d+)?%?\b")
BR = re.compile(r"\[[^\]\n]*\]")
ANG = re.compile(r"<[^>\n]*>")
PH = re.compile(r"\{[^{}\n]*\}")


def normalize_en(t: str) -> str:
    t = ANG.sub(" ", t)
    t = PH.sub("<VAR>", t)
    t = BR.sub("<TAG>", t)
    t = NUM.sub("<N>", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"[.!?]+$", "", t)
    return t


def load_pairs():
    """合并 desc_pairs 与 corpus，得到 (en, cn) 对。"""
    buf: dict[tuple[str, str], dict[str, str]] = {}
    path = os.path.join(DATA, "corpus.jsonl")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["l"] not in ("en", "cn"):
                continue
            key = (r["f"], f"{r['id']}|{r['k']}")
            buf.setdefault(key, {})[r["l"]] = r["t"]
    pairs = []
    for _k, v in buf.items():
        if v.get("en") and v.get("cn"):
            pairs.append((v["en"], v["cn"]))
    return pairs


def main() -> None:
    if "--curated" in sys.argv:
        curated()
        return
    if "--patterns" in sys.argv:
        patterns()
        return
    patterns()
    print()
    curated()


def patterns() -> None:
    pairs = load_pairs()
    print("英中对照对数:", len(pairs))
    pat: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for en, cn in pairs:
        p = normalize_en(en)
        if len(p) < 8 or len(p.split()) < 3:
            continue
        pat[p].append((en, cn))

    ranked = sorted(pat.items(), key=lambda x: -len(x[1]))
    with open(os.path.join(TERMS, "phrase_patterns.tsv"), "w", encoding="utf-8") as fh:
        fh.write("# pattern\tcount\ten_example\tcn_example\n")
        for p, rows in ranked[:600]:
            fh.write(f"{p}\t{len(rows)}\t{rows[0][0][:150]}\t{rows[0][1][:150]}\n")
    with open(os.path.join(TERMS, "_phrase_samples.jsonl"), "w", encoding="utf-8") as fh:
        for p, rows in ranked[:300]:
            fh.write(json.dumps(
                {"pattern": p, "count": len(rows), "samples": rows[:8]},
                ensure_ascii=False) + "\n")

    print("模式数:", len(ranked), "（写出前 600 / 样例前 300）")
    print("\n=== 高频句式模式 top 40 ===")
    for p, rows in ranked[:40]:
        print(f"{len(rows):5d} | {p[:88]}")
        print(f"        EN: {rows[0][0][:100]}")
        print(f"        CN: {rows[0][1][:100]}")


# ================================================================ 人工句式表
# (分组, 标签, 正则) —— 针对英文，大小写不敏感

PATTERNS: list[tuple[str, str, str]] = [
    ("A. 触发时机", "At the start of the Combat Phase / turn", r"at the start of (?:the )?(?:combat phase|battle|turn)"),
    ("A. 触发时机", "At the end of the turn", r"at the end of (?:the )?(?:turn|combat phase|battle)"),
    ("A. 触发时机", "Every turn / every N turns", r"\bevery (?:turn|\d+ turns?)\b"),
    ("A. 触发时机", "On hit / when hit", r"\bon hit\b|\bwhen (?:this unit )?(?:is )?hit\b|\bupon being hit\b"),
    ("A. 触发时机", "On Clash Win / Lose", r"on (?:clash )?(?:win|loss|lose)\b"),
    ("A. 触发时机", "On kill", r"\bon kill\b|\bwhen this unit kills\b"),
    ("A. 触发时机", "When attacking / on use", r"\bwhen (?:using|attacking)\b|\bon use\b|\bupon use\b"),
    ("A. 触发时机", "After / before attacking", r"\b(?:after|before) (?:attacking|the attack)\b"),
    ("A. 触发时机", "While / as long as", r"\bwhile (?:this unit|the target)\b|\bas long as\b"),
    ("A. 触发时机", "If the target / if this unit", r"\bif the (?:target|enemy|ally)\b|\bif this unit\b"),
    ("A. 触发时机", "When this unit dies", r"\bwhen this unit (?:dies|is defeated)\b"),
    ("A. 触发时机", "This effect is not applied", r"\bthis effect is not applied\b"),
    ("A. 触发时机", "At the start of the next turn", r"\bat the start of the next turn\b"),
    ("A. 触发时机", "When N or more", r"\bwhen \d+ or more\b|\bif \w+ is \d+ or (?:more|higher|less|lower)\b"),
    ("B. 赋予与获得", "Gain", r"\bgains?\b"),
    ("B. 赋予与获得", "Inflict", r"\binflicts?\b"),
    ("B. 赋予与获得", "Apply", r"\bapplies?\b|\bapplied\b"),
    ("B. 赋予与获得", "Deal N damage", r"\bdeal(?:s|ing)?\b"),
    ("B. 赋予与获得", "Take N damage", r"\btakes? .*damage\b|\bdamage taken\b"),
    ("B. 赋予与获得", "Heal / Recover / Restore", r"\bheals?\b|\brecovers?\b|\brestores?\b"),
    ("B. 赋予与获得", "Lose HP / SP", r"\bloses? (?:hp|sp|sanity)\b"),
    ("B. 赋予与获得", "Increase / Decrease / Reduce by", r"\b(?:increases?|decreases?|reduces?) (?:by|to)\b"),
    ("B. 赋予与获得", "Gain +N / -N", r"\bgains? [+-]\d"),
    ("B. 赋予与获得", "Add / Remove", r"\badds?\b|\bremoves?\b"),
    ("B. 赋予与获得", "Double / Halve", r"\bdoubles?\b|\bhalves?\b|\bhalved\b"),
    ("C. 层数强度数值", "Potency / Count", r"\b(?:potency|count)\b"),
    ("C. 层数强度数值", "+/-N Potency or Count", r"[+-]\d+ (?:potency|count)"),
    ("C. 层数强度数值", "equal to", r"\bequal to\b"),
    ("C. 层数强度数值", "for every / for each", r"\bfor (?:every|each)\b"),
    ("C. 层数强度数值", "per N", r"\bper (?:\d+|stack|count|point)"),
    ("C. 层数强度数值", "based on", r"\bbased on\b"),
    ("C. 层数强度数值", "to a maximum of / up to", r"\bto a maximum of\b|\bup to \d"),
    ("C. 层数强度数值", "(the) number of", r"\bthe number of\b"),
    ("C. 层数强度数值", "N time(s)", r"\b\d+ times?\b|\bonce\b|\btwice\b"),
    ("C. 层数强度数值", "by N%", r"\bby \d+(?:\.\d+)?%"),
    ("C. 层数强度数值", "the lower / higher of", r"\bthe (?:lower|higher) of\b"),
    ("D. 消耗与转化", "Consume / Spend", r"\bconsumes?\b|\bspends?\b|\bexpends?\b"),
    ("D. 消耗与转化", "Detonate / Burst / Trigger", r"\bdetonates?\b|\bbursts?\b|\btriggers?\b|\bactivates?\b"),
    ("D. 消耗与转化", "Convert / Change into", r"\bconverts?\b|\bchanges? (?:in)?to\b|\bturns? into\b"),
    ("D. 消耗与转化", "Remove all / clear", r"\bremoves? all\b|\bclears?\b"),
    ("D. 消耗与转化", "increase the count by", r"\bincreases? (?:the )?(?:count|potency) by\b"),
    ("D. 消耗与转化", "as much as / equivalent to", r"\bas much as\b|\bequivalent to\b"),
    ("E. 目标范围", "all enemies / allies", r"\ball (?:enemies|allies|units|targets)\b"),
    ("E. 目标范围", "single / one target", r"\ba single target\b|\bone target\b"),
    ("E. 目标范围", "random target(s)", r"\brandom (?:target|enemy|ally|enemies|allies)"),
    ("E. 目标范围", "the target with the lowest / highest", r"\bthe (?:target|enemy|ally) with the (?:lowest|highest)\b"),
    ("E. 目标范围", "selected / this target", r"\bthe (?:selected|chosen) target\b|\bthis target\b"),
    ("E. 目标范围", "main target", r"\bmain target\b"),
    ("E. 目标范围", "targets N time(s)", r"\btargets? (?:the )?(?:target|enemy) \d+ times?\b"),
    ("F. 战斗UI提示", "Cannot use / cannot be", r"\bcannot (?:use|be used|equip)"),
    ("F. 战斗UI提示", "Insufficient / not enough", r"\binsufficient\b|\bnot enough\b|\black of\b"),
    ("F. 战斗UI提示", "Success rate / chance", r"\bsuccess rate\b|\b\d+% chance\b"),
    ("F. 战斗UI提示", "Are you sure", r"\bare you sure\b"),
    ("F. 战斗UI提示", "You obtained / acquired", r"\byou (?:have )?(?:obtained|acquired|received)\b"),
    ("F. 战斗UI提示", "Not unlocked / locked", r"\bnot (?:yet )?(?:unlocked|available)\b|\blocked\b"),
    ("F. 战斗UI提示", "Please select / choose / wait", r"\bplease (?:select|choose|check|wait)\b"),
    ("F. 战斗UI提示", "There is no / nothing", r"\bthere (?:is|are) no\b|\bnothing (?:to|happened)"),
    ("G. 通行证商店", "Battle Pass / pass level", r"\bpass level\b|\bbattle pass\b"),
    ("G. 通行证商店", "Claim / obtain reward", r"\bclaim (?:the )?reward|\bobtain (?:the )?reward|\breceive (?:the )?reward"),
    ("G. 通行证商店", "Can be purchased", r"\bcan be purchased\b|\bpurchas(?:e|able)\b"),
    ("G. 通行证商店", "Remaining / left", r"\bremaining\b|\btime remaining\b"),
    ("G. 通行证商店", "Available until", r"\bavailable until\b"),
    ("H. 剧情旁白", "It was / there was", r"\b(?:it|there) (?:was|were|is|are) \w+"),
    ("H. 剧情旁白", "I ... (first person)", r"\bI (?:am|was|have|had|do|did|cannot|can't|will|would)\b"),
    ("H. 剧情旁白", "We ...", r"\bwe (?:are|were|have|had|must|should|need)\b"),
    ("H. 剧情旁白", "You ...", r"\byou (?:are|were|have|must|should|would)\b"),
    ("H. 剧情旁白", "As if / it seems", r"\bas if\b|\bit seems\b|\bappears to\b"),
]

BATTLE_FILE = re.compile(r"BattleKeyword|Passives|Skills|Bufs|AbnormalityGuides|EGOgift", re.I)
STORY_FILE = re.compile(r"Story|AbDlg|Dialog|StageNode", re.I)


def all_pairs() -> list[tuple[str, str, str]]:
    """[(en, cn, file)] —— desc_pairs.jsonl + corpus.jsonl 逐 id 对齐。"""
    pairs, seen = [], set()
    dpath = os.path.join(TERMS, "desc_pairs.jsonl")
    if os.path.exists(dpath):
        for line in open(dpath, encoding="utf-8"):
            r = json.loads(line)
            en, cn = (r.get("en") or "").strip(), (r.get("cn") or "").strip()
            if en and cn:
                pairs.append((en, cn, r.get("f", "")))
                seen.add((en, cn))
    buf: dict[tuple, dict] = {}
    for line in open(os.path.join(DATA, "corpus.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        if r["l"] not in ("en", "cn"):
            continue
        buf.setdefault((r["f"], r["id"], r["k"]), {})[r["l"]] = r["t"]
    for (f, _i, _k), v in buf.items():
        en, cn = (v.get("en") or "").strip(), (v.get("cn") or "").strip()
        if not en or not cn or (en, cn) in seen:
            continue
        seen.add((en, cn))
        pairs.append((en, cn, f))
    return pairs


def squash(s: str, n: int = 170) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n] + " …"


def curated() -> None:
    top = 10
    if "--top" in sys.argv:
        top = int(sys.argv[sys.argv.index("--top") + 1])

    pairs = all_pairs()
    battle = [p for p in pairs if BATTLE_FILE.search(p[2])]
    story = [p for p in pairs if STORY_FILE.search(p[2])]
    print(f"语料对 {len(pairs)}（战斗类 {len(battle)} / 剧情类 {len(story)}）")

    outdir = os.path.join(TERMS, "_review")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "phrases.md")
    lines = [
        "# 常用表达 · 语料证据报告",
        "",
        f"语料对 **{len(pairs)}** 组（战斗类 {len(battle)} / 剧情类 {len(story)}）。",
        "每个模式给出命中数与**真实中英对照样例**，供人工精编 `terms/常用表达表.md`。",
        "生成：`python3 tools/mine_phrases.py --curated`",
        "",
    ]
    stats = []
    for group, label, pat in PATTERNS:
        rx = re.compile(pat, re.I)
        hits = [p for p in pairs if rx.search(p[0])]
        stats.append((group, label, len(hits)))
        lines.append(f"\n## [{group}] {label}")
        lines.append(f"`{pat}` — 命中 **{len(hits)}** 组\n")
        if not hits:
            lines.append("_（无命中）_\n")
            continue
        hits.sort(key=lambda t: (0 if BATTLE_FILE.search(t[2]) else 1, -len(t[0])))
        for e, c, f in hits[:top]:
            lines.append(f"- `{f}`")
            lines.append(f"  - EN: {squash(e)}")
            lines.append(f"  - CN: {squash(c)}")
        lines.append("")
    lines.append("\n## 命中统计\n")
    lines.append("| 分组 | 模式 | 命中 |")
    lines.append("| --- | --- | --- |")
    for g, l, n in stats:
        lines.append(f"| {g} | {l} | {n} |")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"报告 -> {out}")
    for g, l, n in stats:
        print(f"  {n:6d}  [{g}] {l}")


if __name__ == "__main__":
    main()
