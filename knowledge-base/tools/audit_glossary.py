#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""术语表审计（快速版）：用「同一 id 内中英共现率」量化每条 en→cn 映射是否可信。

判据
    含 en 的 id 集合 = E；含 cn 的 id 集合 = C
    support = |E ∩ C|      同一条记录里中英同时出现 = 该映射的直接证据
    prec    = support / |E| 英文出现时中文出现得有多「必然」

    真术语（Golden Bough → 金枝）prec ≈ 1；
    错配（Section 4 → 第4区段）prec 很低（零协实际写「南部4科」）；
    普通词（Available / Wrath）不是术语，无检索价值。

实现要点（性能）
    不做「术语 × 全语料」的正则扫描。改为**遍历语料一次**：
    对每条记录的英文按 1–6 词窗口生成短语，与术语表英文集合做 O(1) 查表，
    同时在该记录的中文里检查对应中文串是否存在。复杂度 ~O(语料 × 窗口数)。

用法
    python3 tools/audit_glossary.py --stats
    python3 tools/audit_glossary.py --dump noise --limit 60
    python3 tools/audit_glossary.py --save            # 写出 terms/_review/glossary_audit.tsv
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
TERMS = os.path.join(_KB, "terms")
CORPUS = os.path.join(_KB, "data", "corpus.jsonl")
REVIEW = os.path.join(TERMS, "_review")

MAX_NGRAM = 6

STOPWORDS = set("""
a an the and or but if then else of to in on at by for with from as is are was were be been being
do does did done have has had will would shall should can could may might must
this that these those it its their there here what which who whom whose when where why how
all any both each few more most other some such no nor not only own same so than too very
just also even still yet again once ever never always often sometimes
you your yours we our ours they them he she his her him i me my mine
one two three four five six seven eight nine ten
new old good bad big small long short high low
damage turn turns target targets ally allies enemy enemies unit units skill skills
increase decrease gain lose apply inflict deal take use used using
power up down level count stack stacks max min
""".split())

GENERIC_HINT = re.compile(
    r"^(the\s+)?(same|other|next|last|first|second|third|total|current|maximum|minimum|"
    r"available|obtained|required|unlocked|selected|random|additional|following|"
    r"all|any|each|every|none|both)\b", re.I)


def load_glossary(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 2 or not p[0].strip() or not p[1].strip():
                continue
            try:
                n = int(p[2]) if len(p) >= 3 else 0
            except ValueError:
                n = 0
            rows.append([p[0].strip(), p[1].strip(), n, p[3] if len(p) >= 4 else ""])
    return rows


WORD = re.compile(r"[A-Za-z0-9'\-\.]+")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=os.path.join(TERMS, "glossary_all.tsv"))
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--dump", choices=["noise", "suspect", "weak", "ok"])
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()

    rows = load_glossary(args.file)
    print(f"术语表 {os.path.basename(args.file)}: {len(rows)} 条")

    # en(小写) -> 行索引列表；同一英文可能对应多个中文
    en2rows = collections.defaultdict(list)
    for i, (en, cn, _n, _s) in enumerate(rows):
        en2rows[en.lower()].append(i)
    # 中文串 -> 行索引（用于反查）
    cn2rows = collections.defaultdict(list)
    for i, (en, cn, _n, _s) in enumerate(rows):
        cn2rows[cn].append(i)

    # 第一步：只扫英文侧，找出「英文出现在哪些 id」。
    # 注意：不能只用「按词切分的 n-gram 查表」，因为术语表里有
    #   'Shin (心)'、'Launcher [始]'、'Ryōshū' 这类含括号/长音符的条目，
    #   分词后永远匹配不到。做法改为：
    #   先用首词做字符级预筛（大幅缩小候选），再对候选做**原文子串**判定。
    first_char = collections.defaultdict(list)
    for en, cn, _n, _s in rows:
        first_char[en[0].lower()].append(en)

    E = [set() for _ in rows]
    en_hits: dict[tuple, set] = {}
    n_en = 0
    with open(CORPUS, encoding="utf-8") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("l") != "en":
                continue
            text = r.get("t") or ""
            if not text:
                continue
            n_en += 1
            key = (r["f"], r["id"], r["k"])
            low = text.lower()
            # 预筛：只在文中出现过的首字母分桶里找
            cand = []
            seen_first = set()
            for ch in low:
                if ch in first_char and ch not in seen_first:
                    seen_first.add(ch)
                    cand.extend(first_char[ch])
            hit = set()
            for en in cand:
                if en.lower() in low:
                    for ri in en2rows[en.lower()]:
                        hit.add(ri)
            if hit:
                en_hits[key] = hit
                for ri in hit:
                    E[ri].add(key)
    print(f"英文记录 {n_en} 条，其中命中术语的 {len(en_hits)} 条")

    # 第二步：只对「英文命中过」的记录读中文，看对应中文串在不在同一 id 里。
    S = [set() for _ in rows]
    n_rec = 0
    with open(CORPUS, encoding="utf-8") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("l") != "cn":
                continue
            key = (r["f"], r["id"], r["k"])
            hit = en_hits.get(key)
            if not hit:
                continue
            n_rec += 1
            text = r.get("t") or ""
            for ri in hit:
                if rows[ri][1] in text:
                    S[ri].add(key)

    print(f"其中中文同 id 记录 {n_rec} 条，完成共现统计\n")

    out = []
    buckets = collections.Counter()
    for i, (en, cn, n, src) in enumerate(rows):
        e, s = len(E[i]), len(S[i])
        prec = (s / e) if e else 0.0
        lv = classify(en, prec, s)
        buckets[lv] += 1
        out.append((en, cn, n, src, e, s, prec, lv))

    total = len(out)
    print(f"{'等级':<9}{'条数':>7}{'占比':>8}   含义")
    print("-" * 76)
    for lv, desc in (("ok", "可信：英文出现时中文几乎必然出现"),
                     ("weak", "较弱：共现率 60–85%，需抽查"),
                     ("suspect", "可疑：共现率 <60%，疑似错配"),
                     ("noise", "噪声：通用词/零共现，应剔除")):
        c = buckets[lv]
        print(f"{lv:<9}{c:>7}{c/total*100:>7.1f}%   {desc}")

    if args.dump:
        sel = [x for x in out if x[7] == args.dump]
        key = (lambda x: x[6]) if args.dump != "ok" else (lambda x: -x[5])
        print(f"\n===== {args.dump}（前 {args.limit} 条）=====")
        for en, cn, n, src, e, s, prec, lv in sorted(sel, key=key)[: args.limit]:
            print(f"  prec={prec:5.2f} n={n:<6} E={e:<5} sup={s:<5} {en!r:40} → {cn!r:18} {src}")

    if args.save:
        os.makedirs(REVIEW, exist_ok=True)
        p = os.path.join(REVIEW, "glossary_audit.tsv")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# en\tcn\tfreq\tsource\ten_ids\tsupport\tprec\tlevel\n")
            for en, cn, n, src, e, s, prec, lv in out:
                fh.write(f"{en}\t{cn}\t{n}\t{src}\t{e}\t{s}\t{prec:.3f}\t{lv}\n")
        print(f"\n已写出 {p}")
    return 0


def classify(en, prec, sup):
    if sup == 0:
        return "noise"
    if en.lower() in STOPWORDS:
        return "noise"
    if GENERIC_HINT.match(en):
        return "noise"
    if prec < 0.6:
        return "suspect"
    if prec < 0.85:
        return "weak"
    return "ok"


if __name__ == "__main__":
    sys.exit(main())
