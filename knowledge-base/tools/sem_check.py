#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""语义复核筛子（**弱筛子，只抓机械可判的那部分**）。

裁决规则（重译手册 §0.6b）
  文风与术语 → 跟零协；**语义 → 跟韩文**。
  零协也会压缩、也会为顺口改写，所以「照抄零协」= 照抄它偶发的丢信息。

⚠️ 先说清本工具**测不出什么**（别对它抱错期待）
  「两句话都通顺、就是少说了内容」这类丢信息，靠机械指标测不出来。
  实测两个已知真问题都是零分：
    · `S1002B#2` 零协丢了「从罗佳口中」  → 风险 0.0
    · `S1005B#3` 零协丢了「赫尔曼那帮蠢货」→ 风险 0.0
  （试过用「韩文:英文体量比」「中文:韩文长度比」去抓，也都抓不到——
   那些句子长度正常、语法正常，只有对着韩文读才发现少说了东西。）
  **所以语义复核的最终手段永远是人对着韩文读，本工具只是把可疑的排到前面。**

它能可靠抓到的（判据都是「中文该有而没有」，且已排除标签污染）：
  ① **行数**：韩文行数 > 中文行数 → 少了条目（技能说明最常见）
     （⚠️ 不要用「句数」当判据：韩文用 `.` 分词条、中文用 `，`，天然不等，全是假警报）
  ② **长度比**：中文汉字数 / 韩文音节数 < 0.45 → 中文压缩
  ③ 韩文有引号／数字／否定，而中文没有（都已剥掉 `<...>`、`[...]` 再比，
     否则 `E.G.O` 的点、`#e30000` 的数字会造出假警报）
  ④ 中文用「等等／之类」概括

用法
  python3 tools/sem_check.py                    # 全量排序，只看前 40
  python3 tools/sem_check.py --top 100
  python3 tools/sem_check.py --only StoryData/S1004B.json --show
  python3 tools/sem_check.py --save             # 写 terms/_review/sem_check.tsv
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
WS = os.path.dirname(_KB)
PATCH = os.path.join(_KB, "patch_v2")
REVIEW = os.path.join(_KB, "terms", "_review")
GAME = os.environ.get(
    "LIMBUS_GAME_ROOT",
    "/home/shb/.local/share/Steam/steamapps/common/Limbus Company",
)
LOC = os.path.join(GAME, "LimbusCompany_Data", "Assets", "Resources_moved", "Localize")
KR = os.path.join(LOC, "kr")

HAN = re.compile(r"[\u4e00-\u9fff]")
HANGUL = re.compile(r"[\uac00-\ud7a3]")
NEG_KR = re.compile(r"않|없|못|말|아니|말라|마라|안 ")
NEG_CN = re.compile(r"不|没|别|勿|莫|无|未|非|拒绝|停止")
QUOTE = re.compile(r"[「『“”\"']")
NUM = re.compile(r"\d")
# ⚠️ 句数统计前必须先剥掉标签与缩写里的「点」，
#    否则 `E.G.O`、`N사 E.G.O::흉탄`、`Lv.5` 都会被当成句号，
#    造出「韩文 19 句 → 中文 6 句」这类假警报（第一版就踩了）。
_TAG = re.compile(r"<[^>]*>|\[[^\]]*\]")
_ABBR = re.compile(r"(?<=[A-Za-z])\.(?=[A-Za-z])")   # E.G.O / Lv.5 之类
TRAIL_KR = re.compile(r"[.?!]")
TRAIL_CN = re.compile(r"[。？！…]")
VAGUE_CN = re.compile(r"等等|之类|什么的|诸如此类")


def sentences(text: str, cn: bool) -> list:
    """剥掉标签/缩写后按句末标点切句。"""
    t = _TAG.sub(" ", text)
    t = _ABBR.sub("", t)
    t = re.sub(r"\d+\.\d+", "0", t)          # 小数
    pat = TRAIL_CN if cn else TRAIL_KR
    return [x for x in pat.split(t) if len(x.strip()) > 1]


def pick_base(explicit=None):
    if explicit:
        return explicit
    env = os.environ.get("LIMBUS_BASE_PACK")
    if env:
        return os.path.join(WS, env, "LimbusCompany_Data", "Lang", "LLC_zh-CN")
    best, best_v = None, -1
    for d in sorted(glob.glob(os.path.join(WS, "LimbusLocalize_latest*"))):
        try:
            with open(os.path.join(d, "LimbusCompany_Data", "Lang", "LLC_zh-CN",
                                   "Info", "version.json"), encoding="utf-8-sig") as fh:
                v = json.load(fh).get("version", 0)
        except Exception:
            v = 0
        if v > best_v:
            best, best_v = d, v
    return os.path.join(best or "", "LimbusCompany_Data", "Lang", "LLC_zh-CN")


def load(p):
    with open(p, encoding="utf-8-sig") as fh:
        return json.load(fh)


def kr_path(rel):
    d, b = os.path.split(rel)
    p = os.path.join(KR, d, "KR_" + b)
    return p if os.path.exists(p) else os.path.join(KR, rel)


def pairs_of(rel, base):
    """产出 (记录键, 中文, 韩文) 三元组；只取两边都非空的字段。"""
    # 中文侧：零协没有这个文件时退回补丁自己的译文
    # （那 9 个文件官方也还没出韩文，下面 kr_path 会直接返回空）
    cp = os.path.join(base, rel)
    if not os.path.exists(cp):
        cp = os.path.join(PATCH, rel)
    if not os.path.exists(cp):
        return []
    kp = kr_path(rel)
    if not os.path.exists(kp):
        return []
    cn = load(cp)
    kr = load(kp)
    cl = cn.get("dataList") if isinstance(cn, dict) else cn
    kl = kr.get("dataList") if isinstance(kr, dict) else kr
    if not isinstance(cl, list) or not isinstance(kl, list):
        return []

    def key(r):
        return r.get("id") if r.get("id") is not None else r.get("key")

    kmap = {}
    for i, r in enumerate(kl):
        if isinstance(r, dict):
            kmap.setdefault(key(r), []).append((i, r))

    out = []
    for i, cr in enumerate(cl):
        if not isinstance(cr, dict):
            continue
        cands = kmap.get(key(cr)) or []
        krr = None
        for pos, r in cands:
            if pos == i:
                krr = r
                break
        if krr is None and cands:
            krr = cands[0][1]
        if krr is None:
            continue
        _collect(cr, krr, f"{key(cr)}", out)
    return out


def _collect(cv, kv, path, out):
    if isinstance(kv, str) and isinstance(cv, str):
        if HANGUL.search(kv) and HAN.search(cv):
            out.append((path, cv, kv))
    elif isinstance(kv, dict) and isinstance(cv, dict):
        for f, v in kv.items():
            if f in cv:
                _collect(cv[f], v, f"{path}.{f}", out)
    elif isinstance(kv, list) and isinstance(cv, list):
        km = {e.get("index"): e for e in kv if isinstance(e, dict) and "index" in e}
        for i, e in enumerate(cv):
            if not isinstance(e, dict):
                continue
            k = km.get(e.get("index")) or (kv[i] if i < len(kv) and isinstance(kv[i], dict) else None)
            if k:
                _collect(e, k, f"{path}[{e.get('index', i)}]", out)


def risk(cn, kr):
    """返回 (风险分, 理由列表)。分越高越可能丢信息。"""
    reasons = []
    score = 0.0

    # ⚠️ 不要用「句数」当判据：韩文技能说明习惯用 `.` 分词条，中文习惯用 `，`，
    #    两边句数天然不等，会造出大量假警报（第一版就是栽在这里）。
    #    改用「行数」——行是真正的条目边界，少一行就是少一条信息。
    kr_lines = [x for x in kr.split("\n") if len(x.strip()) > 1]
    cn_lines = [x for x in cn.split("\n") if len(x.strip()) > 1]
    if len(kr_lines) > len(cn_lines):
        d = len(kr_lines) - len(cn_lines)
        score += 3.0 * d
        reasons.append(f"韩文 {len(kr_lines)} 行 → 中文 {len(cn_lines)} 行（疑漏条目）")

    kc, cc = len(HANGUL.findall(kr)), len(HAN.findall(cn))
    if kc >= 6:
        ratio = cc / kc
        if ratio < 0.45:
            score += (0.45 - ratio) * 10
            reasons.append(f"长度比偏低 {cc}汉字/{kc}音节={ratio:.2f}")

    kr_t, cn_t = _TAG.sub(" ", kr), _TAG.sub(" ", cn)
    if QUOTE.search(kr_t) and not QUOTE.search(cn_t):
        score += 1.5
        reasons.append("韩文有引号，中文无")

    # ⚠️ 数字也必须先剥标签：`<color=#e30000>`、`<sprite name="X2">`
    #    里的十六进制与序号会被当成数值，造出「数字 30→6」这类假警报。
    kn = len(NUM.findall(_TAG.sub(" ", kr)))
    cn_n = len(NUM.findall(_TAG.sub(" ", cn)))
    if kn > cn_n:
        score += 2.0 * (kn - cn_n)
        reasons.append(f"数字 {kn}→{cn_n}")

    if NEG_KR.search(kr_t) and not NEG_CN.search(cn_t):
        score += 2.5
        reasons.append("韩文有否定，中文无")

    if VAGUE_CN.search(cn) and cc < kc * 0.8:
        score += 1.0
        reasons.append("中文用「等等」概括")

    return score, reasons


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--only", default=None, help="只看某文件（相对 patch_v2）")
    ap.add_argument("--min", type=float, default=3.0, help="风险分下限")
    ap.add_argument("--show", action="store_true", help="打印原文对照")
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--base", default=None)
    args = ap.parse_args()

    base = pick_base(args.base)
    print(f"零协基准: {os.path.relpath(base, WS)}")
    print(f"韩文原文: {KR}\n")

    files = ([args.only] if args.only
             else sorted(os.path.relpath(p, PATCH)
                         for p in glob.glob(os.path.join(PATCH, "**", "*.json"), recursive=True)))

    rows = []
    nopair = 0
    for rel in files:
        ps = pairs_of(rel, base)
        if not ps:
            nopair += 1
            continue
        for path, cn, kr in ps:
            sc, rs = risk(cn, kr)
            if sc >= args.min:
                rows.append((sc, rel, path, cn, kr, rs))

    rows.sort(key=lambda x: -x[0])
    print(f"有韩文可对照的文件 {len(files) - nopair} 个；命中风险 {len(rows)} 处（阈值 {args.min}）\n")
    print("=" * 78)
    for sc, rel, path, cn, kr, rs in rows[:args.top]:
        print(f"\n[{sc:5.1f}] {rel} {path}")
        print(f"   韩文: {kr[:150]}")
        print(f"   中文: {cn[:150]}")
        print(f"   疑点: {'；'.join(rs)}")
        if args.show:
            print(f"   （完整韩文 {len(kr)} 字 / 中文 {len(cn)} 字）")

    if args.save:
        os.makedirs(REVIEW, exist_ok=True)
        out = os.path.join(REVIEW, "sem_check.tsv")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("risk\tfile\tpath\tkr\tcn\treasons\n")
            for sc, rel, path, cn, kr, rs in rows:
                esc = lambda t: t.replace("\r\n", "\\n").replace("\n", "\\n").replace("\t", " ")
                fh.write(f"{sc:.1f}\t{rel}\t{path}\t{esc(kr)}\t{esc(cn)}\t{'; '.join(rs)}\n")
        print(f"\n📄 已写出 {os.path.relpath(out, WS)}（{len(rows)} 行）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
