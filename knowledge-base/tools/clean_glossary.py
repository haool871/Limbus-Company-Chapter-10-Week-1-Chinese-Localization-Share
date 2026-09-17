#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""术语表清理：基于实证判据剔除噪声与错配，产出可复现的干净版本。

输入
    terms/glossary_all.tsv              原始挖掘（6,622 条）
    terms/_review/glossary_audit.tsv    audit_glossary.py 产出的共现证据
输出
    terms/glossary_all.clean.tsv        清理后的全量术语表
    terms/_review/glossary_removed.tsv  被剔除条目 + 原因
    terms/_review/glossary_evidence.tsv 保留条目的证据等级（供后续按证据强度检索）

清理判据（每条可复核，不臆造）
  R1 非术语       英文是功能词 / 纯数字 / 单字符 / 纯符号
  R2 无中文价值   cn 为空、纯符号，或与 en 同形（未翻译且非白名单保留）
  R3 零共现       英文在语料中出现 ≥5 次，却与该中文从不共现（prec==0）
                  —— 两者并非同一概念的对应译法
  R4 同英多译劣势 同一英文有多个中文候选时，若最佳候选 prec≥0.85
                  且本条目（E≥20）prec 比最佳低 ≥0.5，则本条目是错配
                  （如 Defense Power Up: 忍耐 0.94 ✔ / 守备威力强化 0.06 ✘）
  R5 描述性句子   以 Season/Weekly/Only/Obtained 等开头且词数 >3

白名单 KEEP：专名与机制名，命中规则也不剔除（防误伤）。
  注意：合法的多译（Identities→人格/参战人格、Person→人/人类）靠 R4 的
  「最佳候选 prec≥0.85 且差距≥0.5」阈值保护——两者 prec 差距不够大就不会被删。
"""
from __future__ import annotations

import argparse
import collections
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
TERMS = os.path.join(_KB, "terms")
REVIEW = os.path.join(TERMS, "_review")

STOPWORDS = set("""
a an the and or but if then else of to in on at by for with from as is are was were be been being
do does did done have has had will would shall should can could may might must
this that these those it its their there here what which who whom whose when where why how
all any both each few more most other some such no nor not only own same so than too very
just also even still yet again once ever never always often sometimes
you your yours we our ours they them he she his her him i me my mine
one two three four five six seven eight nine ten
new old good bad big small long short high low
""".split())

# 白名单：专名 / 机制名 / 官方术语，命中任何规则都保留
KEEP = set("""
E.G.O E.G.O Gift Identity Identities Sanity SP HP Coin Coins Stagger Staggered
Tremor Rupture Sinking Bleed Burn Poise Charge Haste Bind Fragile Protection
Wrath Lust Sloth Gluttony Gloom Pride Envy
Sinclair Faust Heathcliff Ishmael Rodya Rodion Meursault Outis Gregor Hong Lu
Ryōshū Ryoshu Don Quixote Dante Vergilius Charon
N Corp. K Corp. L Corp. T Corp. U Corp. W Corp. J Corp. M Corp. P Corp. Q Corp.
Öufi Association Zwei Association Liu Association Cinq Association Seven Association
Dieci Association Oufi Association Tres Association Shi Association Devyat Association
Person People Slot Slots Deck Team Floor Floors Stage Stages Chapter Chapters
""".split())

R5_HEAD = re.compile(
    r"^(Season\s*\d|Weekly|Daily|Monthly|Only|Obtained|Available|Unlock(ed)?|"
    r"Required|Reward|Purchase|Contains|Includes)\b", re.I)
# 中文里出现这些 = 该条目带专名/物品名，是术语而非纯程序性描述，R5 不剔
R5_PROPER = re.compile(
    r"葬花吟|忘却|自我碎片|异想解析|通行证|折射轨道|绽放|代行|"
    r"E\.G\.O|赛季：|：|自我|碎片")


def load_tsv(path, ncol):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) >= ncol:
                rows.append(p[:ncol])
    return rows


def load_audit(path):
    a = {}
    if not os.path.exists(path):
        return a
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 8:
                continue
            try:
                a[(p[0], p[1])] = (int(p[4]), int(p[5]), float(p[6]), p[7])
            except ValueError:
                continue
    return a


def is_symbolic(s: str) -> bool:
    return not re.search(r"[0-9A-Za-z\u4e00-\u9fff\uac00-\ud7af]", s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--min-e", type=int, default=5, help="R3 触发所需的最小英文出现数")
    ap.add_argument("--min-e-r4", type=int, default=20, help="R4 触发所需的最小英文出现数")
    ap.add_argument("--gap", type=float, default=0.5, help="R4 与最佳候选的 prec 差距阈值")
    args = ap.parse_args()

    all_rows = load_tsv(os.path.join(TERMS, "glossary_all.tsv"), 5)
    audit = load_audit(os.path.join(REVIEW, "glossary_audit.tsv"))
    print(f"读入 {len(all_rows)} 条；审计证据 {len(audit)} 条")

    # 统计「拉丁串在中文语料里出现」的次数，用于 R2 判定同形条目是否为零协原样保留
    need = {en for en, cn, *_ in all_rows if en == cn}
    latin_in_cn = collections.Counter()
    CORPUS = os.path.join(_KB, "data", "corpus.jsonl")
    if need and os.path.exists(CORPUS):
        import json as _json
        with open(CORPUS, encoding="utf-8") as fh:
            for line in fh:
                try:
                    r = _json.loads(line)
                except Exception:
                    continue
                if r.get("l") != "cn":
                    continue
                t = r.get("t") or ""
                if not t:
                    continue
                for en in need:
                    if en in t:
                        latin_in_cn[en] += 1
        print(f"中文语料中的同形拉丁串统计完成（{len(latin_in_cn)} 个有出现）")

    # R4 需要：每个英文的「最佳候选」
    best = {}
    for (en, cn), (e, s, pr, lv) in audit.items():
        if e >= args.min_e_r4 and pr >= 0.85:
            cur = best.get(en)
            if cur is None or pr > cur[1]:
                best[en] = (cn, pr)

    kept, removed = [], []
    reasons = collections.Counter()
    keepset = {k.lower() for k in KEEP}

    for en, cn, eh, ch, src in all_rows:
        why = None
        low = en.strip().lower()
        if not en.strip() or (is_symbolic(en) and not re.search(r"[\u4e00-\u9fff]", en)):
            why = "R1 空/纯符号"
        elif low in STOPWORDS:
            why = "R1 功能词"
        elif re.fullmatch(r"[\d\s%+\-.]+", en):
            why = "R1 纯数字/数值"
        elif len(en) <= 1:
            why = "R1 单字符"
        elif not cn.strip() or (is_symbolic(cn) and cn != en):
            why = "R2 中文为空/纯符号"
        elif re.search(r"[\uac00-\ud7af]", en) and re.search(r"[\uac00-\ud7af]", cn) \
                and not re.search(r"[\u4e00-\u9fff]", cn):
            # 英中两侧都是韩文 = 开发内部键（如 '던전 103003 선택지'、'항아리_보기'），不是术语
            why = "R2 韩文内部键（英中两侧均韩文）"
        elif cn == en and low not in keepset:
            # 同形条目分两种：
            #   LCC / LCB / LCA / E.G.O 这类——零协在中文里**确实照用拉丁原名**，应保留；
            #   Hard / Normal / OFF / {0} 这类——是 UI 枚举值或占位符，不是术语。
            # 判据：该拉丁串是否也出现在**中文语料**里。出现在中文里 = 零协主动这么用。
            if latin_in_cn.get(en, 0) >= 3 or re.search(r"[\u4e00-\u9fff]", en):
                pass  # 保留（含中文的专名，如 'Zàng Huā Yín [EVENT]' 的变体）
            else:
                why = "R2 同形且中文语料不用（非术语/占位符）"
        elif R5_HEAD.match(en) and len(en.split()) > 3 and not R5_PROPER.search(cn):
            # 只有「纯程序性描述」才剔；含专名/关键名词的赛季条目（葬花吟、自我碎片…）要保留
            why = "R5 描述性句子"
        else:
            e, s, pr, lv = audit.get((en, cn), (0, 0, 0.0, "noise"))
            if e >= args.min_e and s == 0:
                why = "R3 零共现（英中出现、中文从不共现）"
            elif (en in best and e >= args.min_e_r4
                  and best[en][0] != cn and best[en][1] - pr >= args.gap):
                why = f"R4 同英多译劣势（正解 {best[en][0]} prec={best[en][1]:.2f}，本条 {pr:.2f}）"

        if why and low not in keepset and cn not in KEEP:
            removed.append((en, cn, eh, ch, src, why))
            reasons[why.split("（")[0]] += 1
        else:
            kept.append((en, cn, eh, ch, src))

    print(f"\n保留 {len(kept)} / 剔除 {len(removed)}  （原始 {len(all_rows)}）")
    for r, c in reasons.most_common():
        print(f"   {c:>5}  {r}")

    if args.dry_run:
        print("\n--dry-run，未写文件")
        print("\n剔除样本：")
        for r in removed[:25]:
            print(f"   {r[0]!r:34} → {r[1]!r:16} {r[5]}")
        return 0

    os.makedirs(REVIEW, exist_ok=True)
    with open(os.path.join(TERMS, "glossary_all.clean.tsv"), "w", encoding="utf-8") as fh:
        fh.write("# en\tcn\ten_hits\tcn_hits\tsource\n")
        for r in kept:
            fh.write("\t".join(r) + "\n")
    with open(os.path.join(REVIEW, "glossary_removed.tsv"), "w", encoding="utf-8") as fh:
        fh.write("# en\tcn\ten_hits\tcn_hits\tsource\treason\n")
        for r in removed:
            fh.write("\t".join(r) + "\n")
    with open(os.path.join(REVIEW, "glossary_evidence.tsv"), "w", encoding="utf-8") as fh:
        fh.write("# en\tcn\ten_ids\tsupport\tprec\tlevel\n")
        for en, cn, *_ in kept:
            e, s, pr, lv = audit.get((en, cn), (0, 0, 0.0, "no-evidence"))
            fh.write(f"{en}\t{cn}\t{e}\t{s}\t{pr:.3f}\t{lv}\n")
    print(f"\n已写出：")
    print(f"  terms/glossary_all.clean.tsv       {len(kept)} 条")
    print(f"  terms/_review/glossary_removed.tsv  {len(removed)} 条（含原因）")
    print(f"  terms/_review/glossary_evidence.tsv {len(kept)} 条（含证据等级）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
