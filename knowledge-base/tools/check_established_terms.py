#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核对补丁是否使用了零协会的既有译法（**参考工具，不是守门器**）。

⚠️ 已验证的可靠性上限（务必先读）
  本工具的做法是「从零协的短 name/displayName/title 学英文→中文对照，再扫补丁」。
  这个做法**必然有假阳性**，实测：
    补丁与零协基准**逐字相同**的文件上运行，它仍报出 85 条「不一致」，
    逐条核实后 **85/85 全是误报**（例：从 `Heads Hit` 学出术语 `Head`→「头部」，
    再拿它去要求中文出现「头部」，而那条记录里中文写的是「脑袋」）。
  原因：英文单词会作为**子串**出现在更长的短语/句子里，
  机械匹配分不清「这是术语」还是「这只是恰好包含该单词」。
  **所以：本工具的输出只能当线索，每一条都必须人工对着韩文/英文核实后才能改。**
  它已经被改进过三轮（剥 `<...>`/`[...]` 标签、只从单值字段学术语、
  要求位置一致性、最长匹配优先），把假阳性从 347 降到 85，但降不到 0。

  术语与文风的**权威依据**仍然是：`terms/confirmed_pairs.tsv`、
  `terms/glossary_all.clean.tsv`、`terms/术语表.md`，以及直接 `pm_lib.py grep`。


做法：
  1. 从零协基础包（英中同 id 对齐）提取「英文术语 → 零协中文」对照，
     只保留「短英文 ↔ 短中文」的条目（术语/专名），且出现 ≥2 次；
  2. 从补丁的官方英文源中，一次性收集所有「命中的术语」；
  3. 逐个检查补丁中文是否含该术语的零协译法（去空格比较）。

输出: /tmp/term_report.txt
"""
from __future__ import annotations

import collections
import json
import os
import re

_TOOLS = os.path.dirname(os.path.abspath(__file__))   # …/_kb/tools
_KB = os.path.dirname(_TOOLS)                        # …/_kb
_WS = os.path.dirname(_KB)                           # 工作区根
GAME = os.environ.get(
    "LIMBUS_GAME_ROOT",
    "/home/shb/.local/share/Steam/steamapps/common/Limbus Company",
)


def _pick_base() -> str:
    """零协基准包：取 version 最大的 LimbusLocalize_latest*（不要写死版本号）。"""
    import glob
    best, best_v = None, -1
    for d in sorted(glob.glob(os.path.join(_WS, "LimbusLocalize_latest*"))):
        try:
            with open(os.path.join(d, "LimbusCompany_Data", "Lang", "LLC_zh-CN",
                                   "Info", "version.json"), encoding="utf-8-sig") as fh:
                v = json.load(fh).get("version", 0)
        except Exception:
            v = 0
        if v > best_v:
            best, best_v = d, v
    return os.path.join(best or _WS, "LimbusCompany_Data", "Lang", "LLC_zh-CN")


BASE = (os.path.join(_WS, os.environ["LIMBUS_BASE_PACK"],
                      "LimbusCompany_Data", "Lang", "LLC_zh-CN")
        if os.environ.get("LIMBUS_BASE_PACK") else _pick_base())
# ⚠️ 一律用绝对路径：这些常量曾经是相对路径（"LimbusLocalize_latest/..."、" _kb/patch_v2"），
#    只有在工作区根目录下运行时才对。从 _kb 里跑会静默比到空集合、永远报「0 不一致」，
#    看起来像「检查通过」，实际什么都没查（本会话就因此误信过一次 0）。
EN = os.path.join(GAME, "LimbusCompany_Data", "Assets", "Resources_moved",
                  "Localize", "en")
PATCH = os.path.join(_KB, "patch_v2")
CJK = re.compile(r"[\u4e00-\u9fff]")


# 三个根目录都必须存在。缺任何一个都会让比对「静默通过」，
# 那种假通过比直接报错危险得多（本会话已因此误信过一次 0 不一致）。
for _name, _p in (("BASE", BASE), ("EN", EN), ("PATCH", PATCH)):
    if not os.path.isdir(_p):
        raise SystemExit(f"❌ {_name} 目录不存在：{_p}\n"
                         f"   检查 LIMBUS_GAME_ROOT / LIMBUS_BASE_PACK，或零协包是否已解包。")


def ns(s: str) -> str:
    return re.sub(r"[\s\u3000]", "", s)


# ⚠️ 匹配前必须剥掉引擎标签与富文本标签：
#    `- Clash Win: Inflict 1 [Sinking] on target` 里的 `[Sinking]` 是**引擎标签**，
#    中英两侧都原样保留，但 learner 会把 `Sinking` 学成「沉沦」，
#    于是报「零协=沉沦，补丁用 [Sinking]」——整批假警报里这类占大多数。
_TAGS = re.compile(r"<[^>]*>|\[[^\]]*\]|\{[0-9]+\}")


def walk(root, strip_en=False):
    out = {}
    for dp, _dn, fn in os.walk(root):
        for f in fn:
            if not f.endswith(".json"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), root)
            if strip_en:
                d, b = os.path.split(rel)
                if b.startswith("EN_"):
                    b = b[3:]
                rel = os.path.join(d, b) if d else b
            out[rel] = os.path.join(dp, f)
    return out


def main() -> None:
    base = walk(BASE)
    en = walk(EN, strip_en=True)

    # 1) 建对照
    agg: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for rel, bp in base.items():
        ep = en.get(rel)
        if not ep:
            continue
        try:
            cn = json.load(open(bp, encoding="utf-8-sig")).get("dataList", [])
            e = json.load(open(ep, encoding="utf-8-sig")).get("dataList", [])
        except Exception:
            continue
        cm = {str(r.get("id", r.get("key"))): r for r in cn if isinstance(r, dict)}
        for r in e:
            if not isinstance(r, dict):
                continue
            c = cm.get(str(r.get("id", r.get("key"))))
            if not c:
                continue
            # ⚠️ 只从**单值字段**学术术（name/displayName/title）。
            #    绝不能从 content/desc 这种整句里学：那会把
            #    `Turn End: Lose 1 Stack`、`Gain (Wrath Reson.)` 里的
            #    `Turn End`、`Gain` 当成术语，再拿它们的译文去要求别处出现，
            #    造出几百条假警报（第一版 347 条里绝大多数是这么来的）。
            #    另外要求英文侧「像一个术语」：短、无句末标点、无换行、无 <标签>。
            for k in ("name", "displayName", "title"):
                ev, cv = r.get(k), c.get(k)
                if not (isinstance(ev, str) and isinstance(cv, str)):
                    continue
                if not CJK.search(cv):
                    continue
                evs, cvs = ev.strip(), cv.strip()
                if not (3 <= len(evs) <= 24 and 2 <= len(cvs) <= 14):
                    continue
                if "\n" in evs or "<" in evs or ":" in evs or "." in evs or "," in evs:
                    continue
                if not re.fullmatch(r"[A-Za-z][A-Za-z0-9 '\-+]*", evs):
                    continue
                agg[evs][cvs] += 1

    # 只保留出现≥2次、且英文够独特的术语
    terms = {}
    for e, c in agg.items():
        total = sum(c.values())
        if total < 2:
            continue
        # ⚠️ 要求「位置一致性」：同一英文若在不同文件里对应不同中文，
        #    那它多半只是普通词（如 `Muscle in Charge` 里的 Charge、
        #    或 `Head` 出现在 `Heads Hit` 里），不是术语，学进来只会制造噪声。
        if len(c) > 1:
            continue
        terms[e] = c.most_common(1)[0][0]
    print(f"零协既有术语对照: {len(terms)} 条", flush=True)

    # 2) 预编译：按长度降序，命中即止
    ordered = sorted(terms.items(), key=lambda x: -len(x[0]))
    pats = [(e, z, re.compile(r"(?<![A-Za-z0-9])" + re.escape(e) + r"(?![A-Za-z0-9])"))
            for e, z in ordered]

    # 3) 扫补丁
    issues: dict[tuple[str, str], list] = collections.defaultdict(list)
    patch = walk(PATCH)
    for rel, pp in patch.items():
        ep = en.get(rel)
        if not ep:
            continue
        try:
            cn = json.load(open(pp, encoding="utf-8-sig")).get("dataList", [])
            e = json.load(open(ep, encoding="utf-8-sig")).get("dataList", [])
        except Exception:
            continue
        cm = {str(r.get("id", r.get("key"))): r for r in cn if isinstance(r, dict)}
        for r in e:
            if not isinstance(r, dict):
                continue
            c = cm.get(str(r.get("id", r.get("key"))))
            if not c:
                continue
            # ⚠️ 必须把 desc/text 也扫进去：技能与状态说明几乎全在 desc 里，
            #    只扫 name/content/displayName/title 会让本检查形同虚设
            #    （曾因此把一次故意改错的术语「误报为 0 不一致」）。
            # ⚠️ 命中一个术语不能 break：一句话里常有多个术语，每个都要查。
            for k in ("name", "content", "displayName", "title", "desc",
                      "text", "flavor", "summary", "statText"):
                ev, cv = r.get(k), c.get(k)
                if not (isinstance(ev, str) and isinstance(cv, str)):
                    continue
                if not CJK.search(cv):
                    continue
                cvn = ns(cv)
                ev = _TAGS.sub(" ", ev)
                # ⚠️ 最长匹配优先：`Offense Level Up` 命中后，
                #    它的子串 `Level Up`/`Up` 不应再算命中，
                #    否则长术语会被短术语抢占，报出「零协=攻击等级强化」却
                #    拿 `Level Up` 去要求别处出现 —— 全是假警报。
                taken = []          # 已占用的英文区间
                for term, zh, rx in pats:
                    m = rx.search(ev)
                    if not m:
                        continue
                    if any(m.start() < b and a < m.end() for a, b in taken):
                        continue       # 与更长的命中重叠 → 跳过
                    taken.append((m.start(), m.end()))
                    if ns(zh) not in cvn:
                        issues[(term, zh)].append(
                            (rel, str(r.get("id")), k, ev[:60], cv[:60]))

    with open("/tmp/term_report.txt", "w", encoding="utf-8") as fh:
        fh.write(f"不一致术语: {len(issues)}\n")
        for (term, zh), v in sorted(issues.items(), key=lambda x: -len(x[1])):
            fh.write(f"\n【{term}】零协=「{zh}」({len(v)}处)\n")
            fh.write(f"   EN: {v[0][3]}\n   CN: {v[0][4]}\n")
    print(f"不一致术语: {len(issues)}  → /tmp/term_report.txt", flush=True)


if __name__ == "__main__":
    main()
