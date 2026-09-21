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
        if any(isinstance(v, str) and v.strip()
               for k, v in r.items()
               if k not in ("id", "key", "model", "teller", "index", "speaker")):
            n += 1
    return n


def texts(rec) -> list[str]:
    out = []

    def go(o):
        if isinstance(o, str):
            if o.strip():
                out.append(o)
        elif isinstance(o, dict):
            for k, v in o.items():
                if k in ("id", "key", "index", "speaker", "model", "teller", "place"):
                    continue
                go(v)
        elif isinstance(o, list):
            for v in o:
                go(v)
    go(rec)
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
        if br is None:
            # ① 零协完全没有这条
            fields = [f for f, v in er.items()
                      if isinstance(v, str) and v.strip()
                      and f not in ("id", "key", "model", "teller", "index", "speaker")]
            out.append({"id": k, "fields": fields, "why": "零协缺此记录"})
            continue
        # ② 零协有这条，但哪些文本字段是空的
        empty = []
        for f, v in er.items():
            if f in ("id", "key", "model", "teller", "index", "speaker"):
                continue
            if not isinstance(v, str) or not v.strip():
                continue
            bv = br.get(f)
            if not isinstance(bv, str) or not bv.strip():
                empty.append(f)
        if empty:
            out.append({"id": k, "fields": empty, "why": "零协该字段为空"})
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
                    help="把 A 类文件（零协没有的）从官方 en 复制结构进补丁，供翻译")
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

        en_n = recs(enp)
        if en_n <= 0:
            continue                      # 官方这文件也是空的 → 还没内容
        base_n = recs(bp) if os.path.exists(bp) else -1
        pat_n = recs(pp) if os.path.exists(pp) else -1

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
    if args.add_missing:
        made = 0
        for rel, kind, en_n, base_n, pat_n, kr_n in scope:
            if not kind.startswith("A"):
                continue
            enp = os.path.join(EN, os.path.dirname(rel), "EN_" + os.path.basename(rel))
            pp = os.path.join(PATCH, rel)
            if os.path.exists(pp):
                continue
            j = load(enp)
            if not isinstance(j, dict):
                continue
            os.makedirs(os.path.dirname(pp), exist_ok=True)
            # 结构照抄官方 en（键序/嵌套一致），文本暂留英文作为待译标记
            with open(pp, "w", encoding="utf-8") as fh:
                json.dump(j, fh, ensure_ascii=False, indent=2)
            made += 1
            print(f"  ➕ 已建 {rel}")
        if made:
            print(f"\n  共建 {made} 个文件。注意：文本仍是英文，需逐个翻译后跑 verify_retrans。")

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
        print(f"\n📄 已写出 {os.path.relpath(p, WS)}（{len(scope)} 个文件，待补记录约 {tot}）")
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
