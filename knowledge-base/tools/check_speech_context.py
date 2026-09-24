#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""罪人自称／称呼一致性校验（对照零协既有语料）。

原理：从零协基础包（LimbusLocalize_latest）按 `model` 字段统计每个罪人的
自称用词分布，据此判定哪些是她的「既有习惯」、哪些是「从未用过的写法」。
新译文本（补丁）若用到某角色几乎不用的自称，或用到并非该角色习惯的称呼词，
就报出来人工复核。

用法:
  python3 tools/check_speech_context.py                 # 全量扫描补丁
  python3 tools/check_speech_context.py --files a.json  # 只查指定文件
  python3 tools/check_speech_context.py --table         # 只打印既有分布表
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import localization_core as C

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
WORKSPACE = os.path.dirname(_KB)

BASE = None
PATCH = None

# kr model 名 -> 中文名（判定说话人用 model，因为 teller 也会被本地化）
MODELS = {
    "돈키호테": "堂吉诃德", "파우스트": "浮士德", "이상": "李箱", "뫼르소": "默尔索",
    "홍루": "鸿璐", "히스클리프": "希斯克利夫", "이스마엘": "以实玛利", "로쟈": "罗佳",
    "싱클레어": "辛克莱", "오티스": "奥提斯", "그레고르": "格里高尔", "료슈": "良秀",
    "단테": "但丁",
}

# 候选自称。顺序无关，仅用于统计。
# 注意：「我」在中文里多数是「我方／我方阵营」的包容性用法（如「我们前面的」
# 「我们的规则」），并非严格自称，因此不能因为某角色少用「我们」就报错。
# 真正**只有单一译法**的自称是下面这组「独占性自称」。
SELF_WORDS = ["吾等", "吾", "本人", "在下", "咱", "我们", "我", "俺", "敝人", "本大爷", "小女子", "老夫"]

# 独占性自称：一个角色要么一律用它、要么基本不用，几乎没有中间态。
# 只有这组词会触发「她/他从不这么说」的告警。
EXCLUSIVE_SELF = ["吾等", "吾", "本人", "在下", "咱", "俺", "敝人", "本大爷", "小女子", "老夫"]

# 需要特别注意的称呼词（非该角色习惯就不该出现）
ADDRESS_WORDS = ["小朋友", "小家伙", "年轻的", "老爷", "大人", "诸位", "阁下", "您", "汝等", "汝"]


def load(path: str):
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return json.load(fh).get("dataList") or []
    except Exception as exc:
        raise C.DataError(f"无法读取 {path}: {exc}") from exc


def mine_base() -> tuple[dict, dict]:
    """返回 (每角色自称句数分布, 每角色台词总数)。"""
    dist: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    total: collections.Counter = collections.Counter()
    for dp, _dn, fn in os.walk(BASE):
        for name in fn:
            if not name.endswith(".json"):
                continue
            rel = os.path.relpath(os.path.join(dp, name), BASE)
            base_id = os.path.join(rel, name)
            for rec in load(os.path.join(dp, name)):
                if not isinstance(rec, dict):
                    continue
                who = MODELS.get(str(rec.get("model") or ""))
                if not who:
                    continue
                text = rec.get("content")
                if not isinstance(text, str) or not text.strip():
                    continue
                total[who] += 1
                for w in SELF_WORDS:
                    if w in text:
                        dist[who][w] += 1
    return dist, total


def baseline(dist: dict, total: dict) -> dict:
    """判定每角色「零协从未用过」的独占性自称。

    判据取最严谨的形式：**只在该词于零协语料中对这个角色出现 0 次时才告警**。
    例如「本人」虽罕见，但零协对奥提斯、但丁、李箱都用过，故不告警；
    「小朋友」「年轻的」对堂吉诃德是 0 次，才是真信号。
    """
    out = {}
    for who in total:
        never = [w for w in EXCLUSIVE_SELF if dist[who][w] == 0]
        out[who] = {"never": never, "dist": dist[who], "total": total[who]}
    return out


def dump_table(dist: dict, total: dict) -> None:
    print(f'{"角色":<12}{"台词句数":>8}   自称分布（出现该词的句数）')
    print("-" * 96)
    for who in sorted(total, key=lambda x: -total[x]):
        top = "  ".join(f"{w}×{c}" for w, c in dist[who].most_common(8) if c > 0)
        print(f"{who:<12}{total[who]:>8}   {top}")


def check(files: list[str] | None, base_info: dict) -> int:
    targets = []
    if files:
        targets = [os.path.join(PATCH, f) if not os.path.isabs(f) else f for f in files]
    else:
        for dp, _dn, fn in os.walk(PATCH):
            for name in fn:
                if name.endswith(".json"):
                    targets.append(os.path.join(dp, name))

    if not targets:
        raise C.DataError("没有待检查文件；未执行口吻检查")
    problems = []
    scanned = 0
    for path in targets:
        for rec in load(path):
            if not isinstance(rec, dict):
                continue
            who = MODELS.get(str(rec.get("model") or ""))
            if not who:
                continue
            text = rec.get("content")
            if not isinstance(text, str) or not text.strip():
                continue
            scanned += 1
            info = base_info.get(who)
            if not info:
                continue
            rel = os.path.relpath(path, PATCH)
            for w in info["never"]:
                if w in text:
                    problems.append((rel, rec.get("id"), who, w, text))
            # 零协对「young + 名字」既有译法是丢掉不译（young Hong Lu→鸿璐、
            # young Ishmael→以实玛利），且堂吉诃德从不说「小朋友」「年轻的」。
            if who == "堂吉诃德":
                for w in ("小朋友", "年轻的"):
                    if w in text:
                        problems.append((rel, rec.get("id"), who, w, text))

    if not scanned:
        print("不适用：所选文件无可识别角色台词，未执行口吻判定")
        return 0
    print(f"扫描台词 {scanned} 句，发现可疑 {len(problems)} 处（线索，须人工判断）")
    for rel, rid, who, w, text in problems:
        print(f"  [{rel}#{rid}] {who} 用了不属其习惯的「{w}」")
        print(f"      {text[:110]}")
    return 1 if problems else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", default=None)
    ap.add_argument("--table", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--batch")
    args = ap.parse_args()
    global BASE, PATCH
    if args.table:
        saved = C.state().get("baseline")
        BASE = str((C.KB / saved / "base") if saved else C.resolve_base())
    else:
        batch = C.active_batch(args.batch)
        import batch_ops as B
        meta = B.load_batch(batch)
        PATCH = str(batch / "patch")
        BASE = str(__import__("pathlib").Path(meta["new_snapshot"]) / "base")

    dist, total = mine_base()
    if not total:
        print(f"基础包无数据: {BASE}", file=sys.stderr)
        return 2
    if args.table or not args.quiet:
        dump_table(dist, total)
        print()
    if args.table:
        return 0
    return check(args.files, baseline(dist, total))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (C.DataError, OSError) as exc:
        print(f"未执行：{exc}", file=sys.stderr); sys.exit(2)
