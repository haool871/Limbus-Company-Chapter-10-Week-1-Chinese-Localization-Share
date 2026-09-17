#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把频率加权后的候选整理成可用术语表。

策略：候选来自官方术语文件（已与官方英文对齐），因此**低噪声**；
用出现频次 + 形态规则做筛选：剔除纯 UI 动作词、纯数字、模板占位。

输出:
  _kb/terms/glossary.tsv          精选（供翻译直接查）
  _kb/terms/glossary_all.tsv      全量（带频次，淘金用）
"""
from __future__ import annotations

import os
import re

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(_KB_DIR, "terms", "glossary_ranked.tsv")
OUT = os.path.join(_KB_DIR, "terms", "glossary.tsv")
OUT_ALL = os.path.join(_KB_DIR, "terms", "glossary_all.tsv")

# 纯 UI/系统动作词与噪声：不进入"术语表"，但保留在全量表
UI_NOISE = {
    "select", "enter", "return", "resume", "restart", "close", "cancel", "confirm",
    "back", "next", "ok", "yes", "no", "on", "off", "free", "owned", "locked",
    "unlock", "bonus", "cost", "ticket", "team", "loadout", "reward", "rewards",
    "hard", "normal", "easy", "default", "apply", "start", "end", "end stage",
    "buy", "sell", "use", "save", "load", "skip", "auto", "manual", "replay",
    "complete", "clear", "fail", "success", "failure", "win", "lose", "level up",
    "max", "min", "total", "count", "score", "rank", "tier", "class", "floor",
    "chapter", "stage", "episode", "part", "quest", "mission", "goal", "goals",
    "progress", "percentage", "time", "date", "day", "week", "month", "hour",
    "minute", "second", "gaze", "face", "core", "body", "hands", "head", "heart",
    "person", "people", "children", "family", "friend", "friends", "waiting",
    "understanding", "happiness", "jade", "wei", "run.", "run", "left", "right",
    "up", "down", "size", "color", "name", "title", "text", "icon", "image",
    "none", "null", "empty", "blank", "unknown", "???", "past [過去]",
    "present [現在]", "future [未來]", "launcher [始]", "shin (心)", "mang (望)",
    "nirmāna", "les clous", "karma", "resonance", "lunacy", "enkaphalin",
}
# 明确要保留的设定术语（即使被上面的规则命中）
KEEP = {
    "the city", "the backstreets", "the nest", "the nests", "wing", "wings",
    "fixer", "fixers", "syndicate", "distortion", "distortions", "the index",
    "the thumb", "the middle", "the pinky", "the ring", "the head", "lobotomy corporation",
    "library of ruina", "the golden bough", "the golden boughs", "the heart",
    "gaze", "corrosion", "refraction", "mirror dungeons", "identity", "identities",
    "ego", "e.g.o", "sinner", "sinners", "manager", "executive manager",
}


def is_ok(en: str, cn: str) -> bool:
    e = en.strip().lower()
    if e in KEEP:
        return True
    if e in UI_NOISE:
        return False
    if re.fullmatch(r"[\d\s\.\-\+…%]+", en) or re.fullmatch(r"[\d\s\.\-\+…%]+", cn):
        return False
    if "{0}" in en or "{0}" in cn or "{}" in en:
        return False
    if en.startswith("..."):
        return False
    # 纯数字/罗马数字/单字母
    if re.fullmatch(r"[ivxlcdm]+\.?", e):
        return False
    return True


def main() -> None:
    rows = []
    for line in open(SRC, encoding="utf-8"):
        if line.startswith("#"):
            continue
        p = line.rstrip("\n").split("\t")
        if len(p) < 4:
            continue
        en, cn, eh, ch = p[0], p[1], int(p[2]), int(p[3])
        src = p[4] if len(p) > 4 else ""
        rows.append((en, cn, eh, ch, src))

    with open(OUT_ALL, "w", encoding="utf-8") as fh:
        fh.write("# en\tcn\ten_hits\tcn_hits\tsource\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")

    good = [r for r in rows if is_ok(r[0], r[1])]
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("# Limbus Company 英→中术语表（来源：官方术语文件 + 零协会汉化，四语 id 对齐）\n")
        fh.write("# en\tcn\t出现次数(en+cn)\tsource\n")
        for en, cn, eh, ch, src in good:
            fh.write(f"{en}\t{cn}\t{eh+ch}\t{src}\n")

    print(f"全量 {len(rows)}，精选 {len(good)}")
    print("\n=== 精选表前 70 条 ===")
    for en, cn, eh, ch, src in good[:70]:
        print(f"{eh+ch:6d} | {en[:44]:44s} | {cn[:24]}")


if __name__ == "__main__":
    main()
