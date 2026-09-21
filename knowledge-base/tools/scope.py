#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""变更检测：算出「这一批到底有哪些内容需要译」。

不预设文件类型——剧情、RPG、机制、UI、语音、道具名，任何位置的新增都能找出来。

四个数据源
  EN    游戏内官方英文原文   …/Assets/Resources_moved/Localize/en
  KR    游戏内官方韩文原文   …/Localize/kr          （源语言，以它为准）
  BASE  最新零协汉化包       LimbusLocalize_latest*  （权威译法）
  PATCH 本补丁               _kb/patch_v2            （只有 129 个文件）

四类缺口（按优先级）
  A  游戏有 / 零协无此文件          → 全新文件，要全译
  A0 游戏有 / 零协是空占位          → 零协还没开始，要全译（游戏刚更新的典型信号）
  B  零协有但未译完（EN 字段更多）  → 只补差额
  （无缺口则报告「零协已覆盖」，此时不必自己译）

输出
  控制台报告 + terms/_review/scope.tsv（机器可读，供后续脚本消费）

用法
  python3 tools/scope.py                     # 全量扫描
  python3 tools/scope.py --top 40            # 只列前 40
  python3 tools/scope.py --only StoryData    # 只看某个目录
  python3 tools/scope.py --since            # 只看「游戏比零协包新」的部分
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
WS = os.path.dirname(_KB)
PATCH = os.path.join(_KB, "patch_v2")
GAME = os.environ.get(
    "LIMBUS_GAME_ROOT",
    "/home/shb/.local/share/Steam/steamapps/common/Limbus Company",
)
LOC = os.path.join(GAME, "LimbusCompany_Data", "Assets", "Resources_moved", "Localize")
EN = os.path.join(LOC, "en")
KR = os.path.join(LOC, "kr")
REVIEW = os.path.join(_KB, "terms", "_review")


# 由 --base 覆盖（还支持 LIMBUS_BASE_PACK 环境变量）
BASE_OVERRIDE: str | None = os.environ.get("LIMBUS_BASE_PACK")


def latest_base() -> str | None:
    """最新零协包目录（按 Info/version.json 的 version 取最大）。"""
    if BASE_OVERRIDE:
        return BASE_OVERRIDE
    best, best_v = None, -1
    for p in glob.glob(os.path.join(WS, "LimbusLocalize_latest*",
                                    "LimbusCompany_Data", "Lang", "LLC_zh-CN")):
        try:
            v = json.load(open(os.path.join(p, "Info", "version.json"),
                               encoding="utf-8-sig")).get("version", 0)
        except Exception:
            v = 0
        if v > best_v:
            best, best_v = p, v
    return best


def load(p):
    try:
        with open(p, encoding="utf-8-sig") as fh:
            return json.load(fh)
    except Exception:
        return None


def recs(p) -> int:
    """文件里「有内容」的**记录数**（空占位文件返回 0；文件不存在返回 -1）。

    统一按记录数而不是字段数，避免拿记录数比字段数导致口径错乱。
    """
    j = load(p)
    if not isinstance(j, dict):
        return -1
    dl = j.get("dataList")
    if not isinstance(dl, list):
        return 0
    n = 0
    for r in dl:
        if not isinstance(r, dict):
            continue
        # ⚠️ 必须递归：RPG 记录只有 `key` + `texts:[{index,speaker,text}]`，
        #    顶层没有任何字符串字段。旧写法只看顶层，会让这类文件恒为 0，
        #    进而误报「官方无韩文」（本会话排练时踩到）。
        if texts(r):
            n += 1
    return n


# 非文本字段：定位键、说话人、枚举值等，不参与「有没有译文」的统计
SKIP_FIELDS = ("id", "key", "index", "model", "teller", "place",
               "speaker", "nickName", "icon", "sprite", "type")


def str_count(p) -> int:
    """文件里**递归**可译字符串的条数（文件不存在返回 -1）。

    ⚠️ 为什么不能只看 `len(dataList)`：
    RPG 分组记录的正文在 `texts: [{index, speaker, text}]` 这种**对象数组**里。
    零协「记录数一样、但组内少了一条对话」时，比记录数完全测不出来——
    实测 `rpg-loc-dialogue-*.json` 新增一条台词就属于这种情况。
    所以文件级判据用本函数，递归进所有嵌套结构数「有内容的字符串」。
    """
    j = load(p)
    if not isinstance(j, dict):
        return -1
    dl = j.get("dataList")
    if not isinstance(dl, list):
        return 0
    n = 0
    for r in dl:
        n += len(texts(r))
    return n


def texts(rec) -> list[str]:
    out = []

    def go(o):
        if isinstance(o, str):
            if o.strip():
                out.append(o)
        elif isinstance(o, dict):
            for k, v in o.items():
                if k in SKIP_FIELDS:
                    continue
                go(v)
        elif isinstance(o, list):
            for v in o:
                go(v)
    go(rec)
    return out


def str_paths(rec, prefix="") -> list:
    """递归收集 (路径, 文本) —— 路径形如 `content` 或 `texts[1].text`。

    逐条漏译清单要能指出「是哪一条对话漏了」，所以必须带路径。
    """
    out = []

    def go(o, path):
        if isinstance(o, str):
            if o.strip():
                out.append((path, o))
        elif isinstance(o, dict):
            for k, v in o.items():
                if k in SKIP_FIELDS:
                    continue
                go(v, f"{path}.{k}" if path else k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                tag = f"[{v.get('index')}]" if isinstance(v, dict) and "index" in v else f"[{i}]"
                go(v, f"{path}{tag}")
    go(rec, prefix)
    return out


def untranslated(rel: str, base: str) -> list[dict]:
    """精确定位「零协漏译的记录」。

    判据（两条都算漏译）：
      ① 零协文件里**没有这条记录**（官方新增了记录，零协未补）
      ② 零协里有这条记录，但**文本字段为空**（零协只建了占位）

    返回 [{id, fields: [待译字段名], kr: 参考源}, ...]
    """
    enp = os.path.join(EN, os.path.dirname(rel), "EN_" + os.path.basename(rel))
    kp = os.path.join(KR, os.path.dirname(rel), "KR_" + os.path.basename(rel))
    if not os.path.exists(kp):
        kp = os.path.join(KR, rel)
    bp = os.path.join(base, rel)

    def key(r):
        if not isinstance(r, dict):
            return None
        for k in ("id", "key"):
            if r.get(k) is not None:
                return str(r[k])
        return None

    def idx(p):
        j = load(p)
        out = {}
        for r in (j or {}).get("dataList") or []:
            k = key(r)
            if k:
                out.setdefault(k, r)
        return out

    E, K, B = idx(enp), idx(kp), idx(bp)
    out = []
    for k, er in E.items():
        br = B.get(k)
        epaths = str_paths(er)
        if br is None:
            # ① 零协完全没有这条记录
            out.append({"id": k, "fields": [p for p, _ in epaths],
                        "why": "零协缺此记录"})
            continue
        # ② 零协有这条，但某个嵌套字段为空/缺失
        #    （递归比路径，所以 `texts[1].text` 这种组内漏译也能报出来）
        bmap = dict(str_paths(br))
        empty = [p for p, _ in epaths if not (bmap.get(p) or "").strip()]
        if empty:
            out.append({"id": k, "fields": empty, "why": "零协缺此条目/字段"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--only", help="只看形如 StoryData / RPGSystem 的顶层目录")
    ap.add_argument("--since", action="store_true",
                    help="只列「游戏里有、零协包没有」的部分（游戏更新后的场景）")
    ap.add_argument("--save", action="store_true", default=True)
    ap.add_argument("--base", default=None,
                    help="指定零协基础包目录（默认取工作区里版本号最大的 LimbusLocalize_latest*）")
    ap.add_argument("--patch", default=None, help="指定本补丁目录（默认 _kb/patch_v2）")
    ap.add_argument("--add-missing", action="store_true",
                    help="把 A 类文件（零协没有的）从官方 en 复制结构进补丁，供翻译"
                         "（默认只列计划，加 --yes 才真正写入）")
    ap.add_argument("--yes", action="store_true",
                    help="确认执行 --add-missing 的写入")
    ap.add_argument("--from", dest="from_tsv", default=None,
                    help="按清单文件建骨架（每行一个 rel，取第一列）；"
                         "用于处理本次缺口之外的已知新文件，如官方新增但尚未纳入扫描的")
    args = ap.parse_args()

    global BASE_OVERRIDE, PATCH, EN, KR
    if args.base:
        BASE_OVERRIDE = os.path.abspath(args.base)
    if args.patch:
        PATCH = os.path.abspath(args.patch)

    base = latest_base()
    if not base:
        print("❌ 找不到零协基础包", file=sys.stderr)
        return 2
    bv = (load(os.path.join(base, "Info", "version.json")) or {}).get("version")
    print(f"零协基准: {os.path.relpath(base, WS).split(os.sep)[0]} (version={bv})")
    print(f"英文原文: {EN}")
    print(f"本补丁  : {PATCH}\n")

    # 枚举官方英文文件（这是「游戏现在有什么」的权威列表）
    en_files = []
    for dp, _dn, fn in os.walk(EN):
        for f in fn:
            if f.endswith(".json") and f.startswith("EN_"):
                rel = os.path.relpath(os.path.join(dp, f), EN)
                en_files.append(os.path.join(os.path.dirname(rel), f[3:]))
    en_files = sorted(set(en_files))
    print(f"官方英文文件: {len(en_files)} 个")

    scope = []
    cnt = collections.Counter()
    for rel in en_files:
        if args.only and not rel.startswith(args.only):
            continue
        enp = os.path.join(EN, os.path.dirname(rel), "EN_" + os.path.basename(rel))
        bp = os.path.join(base, rel)
        pp = os.path.join(PATCH, rel)
        # 韩文路径：官方 KR 前缀不一定存在，要去前缀后校验
        kp = os.path.join(KR, os.path.dirname(rel), "KR_" + os.path.basename(rel))
        if not os.path.exists(kp):
            kp = os.path.join(KR, rel)

        # 判据用「递归可译字符串条数」而不是记录数：
        # 记录数测不出「组内少一条对话」，而那正是 RPG 最常见的新增形态。
        en_n = str_count(enp)
        if en_n <= 0:
            continue                      # 官方这文件也是空的 → 还没内容
        base_n = str_count(bp) if os.path.exists(bp) else -1
        pat_n = str_count(pp) if os.path.exists(pp) else -1

        # ── 关键判据：游戏有内容、而零协包「没有」或「是空占位」
        #    这正是「游戏刚更新、零协还没跟上」的情形，也是下次翻译最可能遇到的。
        if base_n < 0:
            kind = "A 游戏有 / 零协无此文件"
        elif base_n == 0:
            kind = "A0 游戏有 / 零协是空占位（零协未开始）"
        elif base_n < en_n:
            kind = "B 零协有但未译完（补差额）"
        else:
            kind = None
        # 官方韩文有没有内容（判断「这批是不是真的新」）
        kr_n = recs(kp) if os.path.exists(kp) else -1
        if kr_n < 0:
            kr_n = 0
        if kind is None and args.since:
            continue
        if kind is None:
            continue
        scope.append((rel, kind, en_n, base_n, pat_n, kr_n))
        cnt[kind] += 1

    print(f"\n{'='*72}")
    if not scope:
        print("✅ 没有缺口：官方英文有内容的文件，零协都已覆盖")
    for kind in sorted(cnt):
        rows_k = [x for x in scope if x[1] == kind]
        print(f"\n## {kind} —— {len(rows_k)} 个文件")
        rows_k.sort(key=lambda x: -(x[2] - max(x[3], 0)))
        for rel, _k, en_n, base_n, pat_n, kr_n in rows_k[:args.top]:
            gap = en_n - max(base_n, 0)
            flag = "🔴" if gap > 50 else ("🟡" if gap > 10 else "⚪")
            # 源可用性：有韩文→以韩文为源；只有英文→以英文为源（需在汇报里标注）
            if kr_n > 0:
                src = f"源=KR({kr_n})"
            else:
                src = "源=EN(⚠无韩文)"
            print(f"  {flag} {rel:<50} EN {en_n:>4}  零协 {base_n if base_n>=0 else '—':>4}  "
                  f"缺 {gap if gap>0 else 0:>4}  {src}")
        if len(rows_k) > args.top:
            print(f"     …还有 {len(rows_k)-args.top} 个")

    # ── --add-missing：把零协没有的文件按官方 en 的结构建进补丁（待译）
    if args.add_missing or args.from_tsv:
        # 目标文件集：默认取本次 A 类缺口；给了 --from 就按清单（清单优先）
        if args.from_tsv:
            rels = []
            with open(args.from_tsv, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        rels.append(line.split("\t")[0].strip())
        else:
            rels = [r for r, kind, *_ in scope if kind.startswith("A")]
        # ⚠️ 安全闸：这一步会按官方英文的结构**新建文件**。
        #    一旦基准包指错（例如忘了传 --base，拿真实零协包去比合成树），
        #    A 类会膨胀成「几乎整个官方 en 目录」，一次写出几千个文件。
        #    本会话排练时就误操作过一次（写了 2147 个）。所以默认只列计划。
        to_make = [r for r in rels
                   if os.path.exists(os.path.join(EN, os.path.dirname(r),
                                                  "EN_" + os.path.basename(r)))
                   and not os.path.exists(os.path.join(PATCH, r))]
        # 基准包通常形如 <工作区>/<包名>/LimbusCompany_Data/Lang/LLC_zh-CN
        _bp = base
        for _ in range(3):
            _bp = os.path.dirname(_bp)
        print(f"\n  待建骨架 {len(to_make)} 个文件"
              f"（基准包 {os.path.basename(_bp) or base}，写入 {os.path.relpath(PATCH, WS)}）")
        if len(to_make) > 30:
            print(f"  🚨 数量异常大（>30）。请确认 --base 指向的是**当前游戏版本对应的零协包**；")
            print(f"     若基准包比游戏旧，几乎所有文件都会被判为 A 类。")
        if not args.yes:
            for rel in to_make[:40]:
                print(f"     ＋ {rel}")
            if len(to_make) > 40:
                print(f"     …还有 {len(to_make)-40} 个")
            print("\n  ⏸  未写入。确认无误后加 --yes 执行。")
            return 0

        made = skipped = 0
        for rel in to_make:
            enp = os.path.join(EN, os.path.dirname(rel), "EN_" + os.path.basename(rel))
            pp = os.path.join(PATCH, rel)
            j = load(enp)
            if not isinstance(j, dict):
                print(f"  ⚠️ {rel} 结构异常，跳过")
                skipped += 1
                continue
            os.makedirs(os.path.dirname(pp), exist_ok=True)
            # 结构照抄官方 en（键序/嵌套一致），文本暂留英文作为待译标记
            with open(pp, "w", encoding="utf-8") as fh:
                json.dump(j, fh, ensure_ascii=False, indent=2)
            made += 1
            print(f"  ➕ 已建 {rel}")
        if made:
            print(f"\n  共建 {made} 个文件（跳过 {skipped}：已存在或官方也没有）。")
            print("  ⚠️ 文本仍是英文，需逐个翻译后跑 verify_retrans。")

    # ── 对「零协未译完」的文件，逐条列出漏译记录（这是下次翻译的真实工作清单）
    detail = {}
    if scope:
        print(f"\n{'='*72}")
        print("## 逐条漏译清单（零协漏了哪些记录）")
        for rel, kind, en_n, base_n, pat_n, kr_n in scope:
            if not kind.startswith("B"):
                continue
            us = untranslated(rel, base)
            if not us:
                continue
            detail[rel] = us
            print(f"\n### {rel}  —— 漏 {len(us)} 条")
            for u in us[:args.top]:
                print(f"    id={u['id']:<14} {u['why']:<14} 待译字段: {', '.join(u['fields'])}")
            if len(us) > args.top:
                print(f"    …还有 {len(us)-args.top} 条")

    if args.save and scope:
        os.makedirs(REVIEW, exist_ok=True)
        p = os.path.join(REVIEW, "scope.tsv")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# 变更检测结果：这一批需要译什么\n")
            fh.write("# rel\tkind\ten_records\tbase_records\tpatch_records\tkr_records\n")
            for rel, kind, en_n, base_n, pat_n, kr_n in scope:
                fh.write(f"{rel}\t{kind}\t{en_n}\t{base_n}\t{pat_n}\t{kr_n}\n")
        with open(os.path.join(REVIEW, "scope_untranslated.tsv"), "w", encoding="utf-8") as fh:
            fh.write("# 逐条漏译清单：零协没译的记录（下次翻译的工作清单）\n")
            fh.write("# rel\tid\twhy\tfields\n")
            for rel, us in detail.items():
                for u in us:
                    fh.write(f"{rel}\t{u['id']}\t{u['why']}\t{','.join(u['fields'])}\n")
        tot = sum(x[2] - max(x[3], 0) for x in scope if x[2] > max(x[3], 0))
        print(f"\n📄 已写出 {os.path.relpath(p, WS)}（{len(scope)} 个文件，待补文本约 {tot} 条）")
        if detail:
            print(f"   📄 逐条清单: terms/_review/scope_untranslated.tsv"
                  f"（{sum(len(v) for v in detail.values())} 条）")
        print(f"   下一步：按类型选工具导出上下文——")
        print(f"     StoryData/*.json      → python3 tools/ctx_dump.py <rel> --out /tmp/x.txt")
        print(f"     RPGSystem/dialogue-*  → python3 tools/rpg_dump.py <rel> --out /tmp/x.txt")
        print(f"     其余（机制/UI/道具）  → 直接读，套 style/机制句式模板.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
