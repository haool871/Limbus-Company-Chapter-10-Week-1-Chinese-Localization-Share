#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从游戏官方术语类文件中抽取中英对照候选。

输出:
  _kb/terms/candidates.tsv        en<TAB>cn<TAB>来源文件<TAB>id   （名字类，精炼）
  _kb/terms/desc_pairs.jsonl      {f,id,en,cn}  名字+描述的完整对照（供文风学习）
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pm_lib as P  # noqa: E402

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS = os.path.join(_KB_DIR, "terms")
os.makedirs(TERMS, exist_ok=True)

# 术语类文件（按逻辑名前缀匹配）
TERM_PREFIXES = (
    "BattleKeywords",
    "UnitKeyword",
    "KeywordDictionary",
    "AssociationName",
    "IntroduceCharacter",
    "AbnormalityGuides",
    "Enemies",
    "Skills",
    "Passives",
    "Bufs",
    "EGOgift",
    "PanicInfo",
    "Items",
    "StageNode",
    "DungeonNode",
    "DungeonArea",
    "ActionEvents",
    "AbEvents",
    "AbEventsResultLog",
    "BattleResultHint",
    "BattleHint",
    "RailwayDungeon",
    "MirrorDungeon",
    "StoryTheaterDanteNote",
    "DanteAbility",
    "Personalities",
    "EGOgiftCategory",
    "SeasonTitle",
    "BattlePass",
)
# 这些文件整体是长文本，只取名字字段即可
NAME_FIELDS = ("name", "content", "title", "keyword", "codeName")
DESC_FIELDS = ("desc", "description", "simpleDesc", "summary", "eventDesc", "story")


def main() -> None:
    index = P.build_index()
    targets = [
        k for k in sorted(index)
        if os.path.basename(k).split("-")[0].split("_")[0].startswith(TERM_PREFIXES)
        or os.path.basename(k).split(".")[0] in TERM_PREFIXES
    ]
    print("术语类文件数:", len(targets))
    seen: set[tuple[str, str]] = set()
    rows: list[tuple[str, str, str, str]] = []
    ndesc = 0
    with open(os.path.join(TERMS, "desc_pairs.jsonl"), "w", encoding="utf-8") as fh:
        for logical in targets:
            try:
                data = P.align(logical)
            except SystemExit:
                continue
            en = {r["_id"]: r for r in data.get("en", [])}
            cn = {r["_id"]: r for r in data.get("cn", [])}
            for rid, cr in cn.items():
                er = en.get(rid)
                if not er:
                    continue
                # 名字类字段：取第一个非空
                def pick(rec, fields):
                    for f in fields:
                        v = rec.get(f)
                        if isinstance(v, str) and v.strip():
                            return f, v.strip()
                    return None, None
                ef, ev = pick(er, NAME_FIELDS)
                cf, cv = pick(cr, NAME_FIELDS)
                if ef and cf:
                    key = (ev, cv)
                    if key not in seen and len(ev) < 60 and len(cv) < 60:
                        seen.add(key)
                        rows.append((ev, cv, logical, rid))
                # 描述类：取最长的一组对照
                ed = max((er.get(f) or "" for f in DESC_FIELDS), key=len, default="")
                cd = max((cr.get(f) or "" for f in DESC_FIELDS), key=len, default="")
                if ed.strip() and cd.strip():
                    ndesc += 1
                    fh.write(json.dumps(
                        {"f": logical, "id": rid, "en": ed.strip(), "cn": cd.strip()},
                        ensure_ascii=False) + "\n")

    rows.sort(key=lambda r: r[2])
    with open(os.path.join(TERMS, "candidates.tsv"), "w", encoding="utf-8") as fh:
        fh.write("# en\tcn\tsource\tid\n")
        for r in rows:
            fh.write("\t".join(r) + "\n")
    print(f"名字类候选: {len(rows)}")
    print(f"描述对照: {ndesc}")
    print("样例:")
    for r in rows[:15]:
        print("   ", r[0], "|", r[1], "|", r[2])


if __name__ == "__main__":
    main()
