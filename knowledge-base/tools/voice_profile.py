#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""罪人文风画像：量化说话特征 + 抽取样本句。

思路：StoryData 里 kr 的 `model` 字段是说话人标识（稳定），
en/cn 的 `content` 是同一台词。按此对齐即可得到"同一句话的三语版本"。

输出:
  _kb/data/voice_stats.json   每个说话人的量化特征
  _kb/data/voice_samples.md   每个说话人的英中对照样本（供人工/子代理写风格指南）
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pm_lib as P  # noqa: E402

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(_KB_DIR, "data")

# 12 名罪人的 kr model 标识
SINNERS = {
    "단테": ("Dante", "但丁"),
    "이상": ("Yi Sang", "李箱"),
    "파우스트": ("Faust", "浮士德"),
    "돈키호테": ("Don Quixote", "堂吉诃德"),
    "료슈": ("Ryōshū", "良秀"),
    "뫼르소": ("Meursault", "默尔索"),
    "홍루": ("Hong Lu", "鸿璐"),
    "히스클리프": ("Heathcliff", "希斯克利夫"),
    "이스마엘": ("Ishmael", "以实玛利"),
    "로쟈": ("Rodion", "罗佳"),
    "싱클레어": ("Sinclair", "辛克莱"),
    "오티스": ("Outis", "奥提斯"),
    "그레고르": ("Gregor", "格里高尔"),
}

# 中文自称/口头特征词
CN_MARK = {
    "我": r"我(?!们)",
    "我们": r"我们",
    "咱": r"咱",
    "俺": r"俺",
    "本人": r"本人",
    "在下": r"在下",
    "老夫": r"老夫",
    "人家": r"人家",
    "！": r"！",
    "？": r"？",
    "……": r"…",
    "啊": r"啊",
    "呀": r"呀",
    "呢": r"呢",
    "吧": r"吧",
    "哦": r"哦",
    "哟": r"哟",
    "啦": r"啦",
    "嗯": r"嗯",
    "哈": r"哈",
    "呜": r"呜",
}
# 英文口头特征
EN_MARK = {
    "I": r"\bI\b",
    "we": r"\bwe\b",
    "you": r"\byou\b",
    "!": r"!",
    "?": r"\?",
    "Oho": r"\bOho\b",
    "Hmm": r"\bHmm+\b",
    "verily": r"\bverily\b",
    "indeed": r"\bindeed\b",
    "hmph": r"\bhmph\b",
    "Ah": r"\bAh\b",
    "Oh": r"\bOh\b",
    "Well": r"\bWell\b",
}


def main() -> None:
    idx = P.build_index()
    story = [k for k in sorted(idx) if k.startswith("StoryData")]

    # 收集：model -> [(en, cn, kr)]
    bucket: dict[str, list[tuple[str, str, str]]] = collections.defaultdict(list)
    extra_models = collections.Counter()
    for logical in story:
        if not all(l in idx[logical] for l in ("kr", "en", "cn")):
            continue
        A = P.align(logical)
        kr = {r["_id"]: r for r in A["kr"]}
        en = {r["_id"]: r for r in A["en"]}
        cn = {r["_id"]: r for r in A["cn"]}
        for rid, krr in kr.items():
            m = krr.get("model")
            if not m:
                continue
            e = (en.get(rid) or {}).get("content")
            c = (cn.get(rid) or {}).get("content")
            if not e or not c:
                continue
            # 跳过纯省略号/空白
            if not re.search(r"[A-Za-z]", e) or not re.search(r"[\u4e00-\u9fff]", c):
                continue
            bucket[m].append((e, c, krr.get("content", "")))
            extra_models[m] += 1

    stats: dict[str, dict] = {}
    for model, rows in bucket.items():
        if len(rows) < 20:
            continue
        en_all = " ".join(r[0] for r in rows)
        cn_all = " ".join(r[1] for r in rows)
        en_len = sum(len(r[0].split()) for r in rows) / len(rows)
        cn_len = sum(len(r[1]) for r in rows) / len(rows)
        cn_hits = {k: len(re.findall(v, cn_all)) for k, v in CN_MARK.items()}
        en_hits = {k: len(re.findall(v, en_all, re.I)) for k, v in EN_MARK.items()}
        name = SINNERS.get(model, (None, None))
        stats[model] = {
            "en_name": name[0],
            "cn_name": name[1],
            "lines": len(rows),
            "avg_en_words": round(en_len, 1),
            "avg_cn_chars": round(cn_len, 1),
            "cn_marks_per_100": {k: round(v * 100 / len(rows), 1) for k, v in sorted(cn_hits.items(), key=lambda x: -x[1]) if v},
            "en_marks_per_100": {k: round(v * 100 / len(rows), 1) for k, v in sorted(en_hits.items(), key=lambda x: -x[1]) if v},
        }

    with open(os.path.join(DATA, "voice_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, ensure_ascii=False, indent=1)

    # 样本：每个主要说话人抽 60 句（均匀采样）
    with open(os.path.join(DATA, "voice_samples.md"), "w", encoding="utf-8") as fh:
        fh.write("# 说话人样本句（EN → CN，官方原文对齐）\n\n")
        fh.write("来源：StoryData 全 941 个剧情文件，按 kr `model` 字段归属说话人。\n\n")
        ordered = sorted(bucket, key=lambda m: -len(bucket[m]))
        for model in ordered:
            rows = bucket[model]
            if len(rows) < 20:
                continue
            en, cn = SINNERS.get(model, (model, model))
            fh.write(f"\n## {en} / {cn}  (model=`{model}`, {len(rows)} 句)\n\n")
            step = max(1, len(rows) // 60)
            for e, c, _k in rows[::step][:60]:
                fh.write(f"- EN: {e}\n  CN: {c}\n")
    print("说话人数:", len(stats), " 样本文件已写出")
    for m, s in sorted(stats.items(), key=lambda x: -x[1]["lines"])[:16]:
        print(f"  {s['en_name'] or m:16s} {s['cn_name'] or '':6s} 句数={s['lines']:5d} "
              f"均英词={s['avg_en_words']:5.1f} 均中字={s['avg_cn_chars']:5.1f} "
              f"自称我={s['cn_marks_per_100'].get('我',0):5.1f} 感叹={s['cn_marks_per_100'].get('！',0):5.1f}")


if __name__ == "__main__":
    main()
