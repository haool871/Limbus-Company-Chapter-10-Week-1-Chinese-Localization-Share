#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""语料分析：说话人分布、n-gram 词频候选、术语候选、术语表覆盖率。

输出到 _kb/data/:
  speakers.json      每个角色/模型的台词条数（按目录与模型）
  term_candidates.json  中文 n-gram 与英文词频候选
  glossary_check.json   术语表在语料中的命中统计
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pm_lib import (  # noqa: E402
    CN_LOCALIZE,
    LANGS,
    align,
    build_index,
    iter_corpus,
    load_file,
    record_key,
    text_fields,
)

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(_KB_DIR, "data")
os.makedirs(DATA, exist_ok=True)

CJK = re.compile(r"[\u4e00-\u9fff]")
EN_WORD = re.compile(r"[A-Za-z][A-Za-z'\-]{1,}")
EN_STOP = set(
    """the a an and or but if then than that this these those it its it's is are was were be been being
    to of in on at by for with from as into over under about after before while when where who whom whose
    you your yours i me my mine we our ours he him his she her hers they them their theirs
    not no nor so such very just only also even still yet too much many more most some any all
    do does did done have has had having will would shall should can could may might must
    what which how why there here now out up down off again once
    """.split()
)
ZH_STOP_FRAG = {
    "的了", "是的", "不是", "什么", "这个", "那个", "一个", "没有", "可以", "就是",
    "我们", "你们", "他们", "自己", "这样", "那样", "因为", "所以", "但是", "如果",
    "已经", "还是", "知道", "现在", "时候", "地方", "东西", "家伙", "怎么", "为了",
}


def read_corpus():
    path = os.path.join(DATA, "corpus.jsonl")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            yield json.loads(line)


# ------------------------------------------------------------ 1. 说话人统计


def speaker_stats() -> None:
    """按 文件类别 + model 字段 统计各语言台词条数。"""
    counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    model_en: collections.Counter = collections.Counter()
    for rec in read_corpus():
        logical, lang, f = rec["f"], rec["l"], rec["k"]
        cat = logical.split(os.sep)[0] if os.sep in logical else "root"
        if f == "model":
            counts[f"{cat}|{lang}"][rec["t"]] += 1
        if lang == "en" and f == "teller":
            model_en[rec["t"]] += 1

    out = {k: dict(v.most_common()) for k, v in counts.items()}
    payload = {
        "by_category_lang": out,
        "teller_counts_en": dict(model_en.most_common()),
    }
    with open(os.path.join(DATA, "speakers.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print("[speakers] 类别:", sorted({k.split('|')[0] for k in counts}))
    print("[speakers] kr model 数:", len(counts.get("StoryData|kr", {})))


# ------------------------------------------------------------ 2. 术语候选


def ngram_candidates(lang: str, n_range=(2, 5), top=800) -> list[tuple[str, int]]:
    """对 CJK 文本做 n-gram 频次统计（无分词库时的术语发现手段）。"""
    cnt: collections.Counter = collections.Counter()
    for rec in read_corpus():
        if rec["l"] != lang or not CJK.search(rec["t"]):
            continue
        text = "".join(CJK.findall(rec["t"]))
        for n in range(n_range[0], n_range[1] + 1):
            for i in range(len(text) - n + 1):
                g = text[i:i + n]
                if g in ZH_STOP_FRAG:
                    continue
                cnt[g] += 1
    # 过滤：被更长 gram 完全包含且频次接近的短 gram（取最长高置信）
    items = [(g, c) for g, c in cnt.items() if c >= 3]
    items.sort(key=lambda x: (-x[1], -len(x[0])))
    return items[:top]


def word_candidates(lang: str, top=500) -> list[tuple[str, int]]:
    cnt: collections.Counter = collections.Counter()
    for rec in read_corpus():
        if rec["l"] != lang:
            continue
        for w in EN_WORD.findall(rec["t"]):
            lw = w.lower()
            if lw in EN_STOP or len(lw) < 3:
                continue
            cnt[lw] += 1
    return cnt.most_common(top)


def term_candidates() -> None:
    zh = ngram_candidates("cn")
    en = word_candidates("en")
    with open(os.path.join(DATA, "term_candidates.json"), "w", encoding="utf-8") as fh:
        json.dump({"cn_ngram": zh, "en_words": en}, fh, ensure_ascii=False, indent=1)
    print("[terms] cn n-gram 候选:", len(zh), " en 词候选:", len(en))
    print("[terms] cn top20:", [g for g, _ in zh[:20]])


# ------------------------------------------------------------ 3. 术语表校验


def glossary_check() -> None:
    """读取 glossary.tsv (en<TAB>cn<TAB>备注) 并统计在语料中的出现次数与一致性。"""
    path = os.path.join(_KB_DIR, "terms", "glossary.tsv")
    if not os.path.exists(path):
        print("[glossary] 尚无 glossary.tsv，跳过")
        return
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                rows.append(parts)
    # 逐条统计：中英各自出现次数
    cache: dict[str, collections.Counter] = {"cn": collections.Counter(), "en": collections.Counter()}
    for rec in read_corpus():
        if rec["l"] not in cache:
            continue
        t = rec["t"]
        cache[rec["l"]][t] += 1

    result = []
    for parts in rows:
        en, cn = parts[0], parts[1]
        note = parts[2] if len(parts) > 2 else ""
        en_hits = sum(c for t, c in cache["en"].items() if en.lower() in t.lower())
        cn_hits = sum(c for t, c in cache["cn"].items() if cn in t)
        result.append({"en": en, "cn": cn, "note": note, "en_hits": en_hits, "cn_hits": cn_hits})
    with open(os.path.join(DATA, "glossary_check.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
    miss = [r for r in result if r["en_hits"] == 0]
    print(f"[glossary] 条目 {len(result)}，英文零命中 {len(miss)}")
    for r in miss[:10]:
        print("   缺:", r["en"], "/", r["cn"])


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "speakers"):
        speaker_stats()
    if what in ("all", "terms"):
        term_candidates()
    if what in ("all", "glossary"):
        glossary_check()
