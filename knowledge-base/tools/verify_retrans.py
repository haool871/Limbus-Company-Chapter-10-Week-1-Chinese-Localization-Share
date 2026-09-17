#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重译成品校验（结构无关版）：一次性检查结构、标签、占位符、空译、第一人称、禁用语。

支持补丁里的全部三种数据形态
  ① StoryData 等      dataList[] 里每条有 `id`，正文在 `content`
  ② RPG 分组          dataList[] 里每条有 `key` + `texts[{index,text,speaker}]`
  ③ RPG 扁平          dataList[] 里每条有 `key` + 若干字符串字段
                      （`text` / `displayName` / `description` / `title` …）

对齐方式
  - 有 `id`  → 按 id 对齐官方 EN（也用 KR 作参考）
  - 有 `key` → 按 key 对齐
逐条把「同一路径」的字符串与英文源比对：必须保留的标签、占位符、空译、禁用语。
「但丁旁白/独白漏第一人称」只在**旁白条目**（无 model / speaker 为空）上判。

用法
  python3 tools/verify_retrans.py StoryData/S1002B.json
  python3 tools/verify_retrans.py RPGSystem/rpg-loc-item-common-a1c10p1.json
  python3 tools/verify_retrans.py --all-story
  python3 tools/verify_retrans.py --all-rpg
  python3 tools/verify_retrans.py --all
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
WORKSPACE = os.path.dirname(_KB)
PATCH = os.path.join(_KB, "patch_v2")
# 零协汉化基础包：**覆盖文件**的权威基准。
# 对「基础包已有该 id」的记录，零协原文就是唯一标准，
# 不能拿官方英文源去比对（两者字段名/结构并不一致，会制造大量伪错误）。
BASE = os.path.join(WORKSPACE, "LimbusLocalize_latest",
                    "LimbusCompany_Data", "Lang", "LLC_zh-CN")
GAME = os.environ.get("LIMBUS_GAME_ROOT",
                      "/home/shb/.local/share/Steam/steamapps/common/Limbus Company")
LOC = os.path.join(GAME, "LimbusCompany_Data", "Assets", "Resources_moved", "Localize")

# 必须逐字符保留的标签（可选的 <i>/<b>/<u>/<s> 不在内）
MUST_TAG = re.compile(r"</?(?:color|size|style|mark)(?:=[^>]*)?>", re.I)
PLACEHOLDER = re.compile(r"\{[^}]*\}")
FP_MARK = re.compile(r"\b(I|I'm|I've|I'd|I'll|my|me|myself|mine)\b")
# 韩文第一人称标记（用于「以韩文为准」时判断中文可否省略主语）
FP_MARK_KR = re.compile(r"나|내|저|제|우리|저희")

# 禁用语：这些写法在零协语料中不成立（见 workflow/重译手册.md §3）
BANNED = ["黄金枝", "辣喊助威", "第4区段", "攻击等级强化", "防御等级强化",
          "守备威力强化", "提振士气", "星芒奖励", "异邦人", "修改师", "两件套"]

# 不作为译文比对的字段（结构/元数据）
SKIP_KEYS = ("id", "key", "model", "teller", "index", "place", "speaker",
             "nickName", "icon", "sprite", "type", "level", "count")


def load(p):
    try:
        with open(p, encoding="utf-8-sig") as fh:
            return json.load(fh).get("dataList") or []
    except Exception:
        return []


def src_path(rel, lang, pre):
    d, f = os.path.split(rel)
    for c in (pre + f, f):
        p = os.path.join(LOC, lang, d, c)
        if os.path.exists(p):
            return p
    return None


def strings_of(rec, out, path=""):
    """递归收集 (路径, 字符串)，跳过结构字段。"""
    if isinstance(rec, str):
        out.append((path, rec))
    elif isinstance(rec, dict):
        for k, v in rec.items():
            if k in SKIP_KEYS:
                continue
            strings_of(v, out, f"{path}.{k}" if path else k)
    elif isinstance(rec, list):
        for i, v in enumerate(rec):
            strings_of(v, out, f"{path}[{i}]")
    return out


def is_narration(rec) -> bool:
    """旁白判定。

    - StoryData：无 `model` 字段的记录＝旁白／但丁内心独白（`model` 是说话人键）。
    - RPG：`speaker` 为空＝旁白。
      ⚠️ RPG 里 `speaker="???"` 是**未揭示身份的角色在说话**，不是旁白——
      早期版本把它当旁白，导致大量「漏第一人称」误报（93 条全是假的）。
    """
    if not isinstance(rec, dict):
        return False
    if rec.get("model"):
        return False
    if "speaker" in rec:
        return not str(rec.get("speaker") or "").strip()
    # RPG 的组记录没有 speaker，真正的叶子条目才有 → 这种情况不算旁白
    if "texts" in rec:
        return False
    return True


def check_one(rel, verbose=False):
    p = os.path.join(PATCH, rel)
    if not os.path.exists(p):
        return None, [f"文件不存在: {rel}"], []
    cn = load(p)
    en = load(src_path(rel, "en", "EN_") or "")
    errs, warns = [], []

    # 对齐键：优先 id，其次 key
    def align_key(r):
        if not isinstance(r, dict):
            return None
        if r.get("id") is not None:
            return ("id", r.get("id"))
        if r.get("key") is not None:
            return ("key", r.get("key"))
        return None

    en_by, kr_by, base_by = {}, {}, {}
    bp = os.path.join(BASE, rel)
    bd = load(bp) if os.path.exists(bp) else []
    for r in bd:
        k = align_key(r)
        if k:
            base_by.setdefault(k, []).append(r)
    kr = load(src_path(rel, "kr", "KR_") or "")
    for r in en:
        k = align_key(r)
        if k:
            en_by.setdefault(k, []).append(r)
    for r in kr:
        k = align_key(r)
        if k:
            kr_by.setdefault(k, []).append(r)

    kc = [align_key(r) for r in cn if isinstance(r, dict)]
    ke = [align_key(r) for r in en if isinstance(r, dict)]
    if en and kc != ke:
        errs.append(f"对齐键序列与英文源不一致（CN {len(kc)} / EN {len(ke)}）")

    n_text = 0
    first_person = 0
    for rec in cn:
        if not isinstance(rec, dict):
            continue
        k = align_key(rec)
        ens = en_by.get(k, []) if k else []
        # 只记录**英文源确实存在**的字段路径。
        # 中英两侧字段名/结构并不总是一致（如 CN `desc` 对应 EN `summary`
        # 或 EN 根本没有该字段），用不存在当基准会制造大量伪「空译/标签不一致」。
        en_map, kr_map = {}, {}
        # 该记录零协已有 → 以零协原文为准：不做英文基准比对，
        # 禁用语检查也豁免（禁用语表是为本补丁新译内容定的，不追溯零协原文）。
        from_base = bool(base_by.get(k))
        if from_base:
            ens = []
        if ens:
            for path, s in strings_of(ens[0], []):
                if s.strip():
                    en_map[path] = s
        krs = kr_by.get(k, []) if k else []
        if krs:
            for path, s in strings_of(krs[0], []):
                if s.strip():
                    kr_map[path] = s
        narr = is_narration(rec)
        for path, txt in strings_of(rec, []):
            n_text += 1
            # `speaker` 在 RPG 的每个 text 条目里（不在组记录上），
            # 所以这里要在「条目自身」上再判一次旁白。
            leaf_rec = rec
            m = re.match(r"texts\[(\d+)\]", path)
            if m and isinstance(rec.get("texts"), list):
                idx = int(m.group(1))
                if 0 <= idx < len(rec["texts"]) and isinstance(rec["texts"][idx], dict):
                    leaf_rec = rec["texts"][idx]
            leaf_narr = is_narration(leaf_rec)
            etxt = en_map.get(path, "")
            ktxt = kr_map.get(path, "")
            if etxt:
                if sorted(MUST_TAG.findall(txt)) != sorted(MUST_TAG.findall(etxt)):
                    errs.append(f"{k}#{path} 必须保留标签不一致")
                if sorted(PLACEHOLDER.findall(txt)) != sorted(PLACEHOLDER.findall(etxt)):
                    errs.append(f"{k}#{path} 占位符不一致")
                if not txt.strip():
                    errs.append(f"{k}#{path} 空译（英文有内容）")
            if not from_base:
                for b in BANNED:
                    if b in txt:
                        errs.append(f"{k}#{path} 含禁用语「{b}」")
            # 已知误报：这三条的英文有 I/myself，但中文「把自己弄干净」「听了说明」
            # 「但愿如此」都是正常的无主语句，且韩文也无第一人称标记（项目以韩文为准）。
            if k and k[1] in ("I990904", "Q1031", "Q3009"):
                etxt = ""
            if leaf_narr and etxt:
                # 项目规则「以韩文为准」：韩文若也没有第一人称标记，
                # 中文省略主语是正常的（如「试着坐下」），不算漏译。
                if not FP_MARK_KR.search(ktxt):
                    etxt = ""
                hits = FP_MARK.findall(etxt)
                if hits and "我" not in txt:
                    warns.append(f"{k}#{path} 旁白漏第一人称"
                                 f"（EN 含 {','.join(sorted(set(hits)))}）: {txt[:50]}")
                elif hits:
                    first_person += 1
    return {"rel": rel, "records": len(cn), "texts": n_text,
            "first_person": first_person}, errs, warns


def collect(mode):
    if mode == "story":
        root = os.path.join(PATCH, "StoryData")
    elif mode == "rpg":
        root = os.path.join(PATCH, "RPGSystem")
    else:
        return [os.path.relpath(os.path.join(dp, f), PATCH)
                for dp, _dn, fn in os.walk(PATCH) for f in sorted(fn) if f.endswith(".json")]
    return [os.path.relpath(os.path.join(root, f), PATCH)
            for f in sorted(os.listdir(root)) if f.endswith(".json")]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="相对 patch_v2 的路径")
    ap.add_argument("--all-story", action="store_true")
    ap.add_argument("--all-rpg", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if args.all:
        targets = collect("all")
    elif args.all_story:
        targets = collect("story")
    elif args.all_rpg:
        targets = collect("rpg")
    elif args.target:
        targets = [args.target]
    else:
        ap.error("需要指定文件，或 --all-story / --all-rpg / --all")

    total_err = total_warn = 0
    bad_files = []
    for rel in targets:
        info, errs, warns = check_one(rel, args.verbose)
        if info is None:
            print(f"❌ {errs[0]}")
            total_err += 1
            bad_files.append(rel)
            continue
        mark = "✅" if not errs else "❌"
        print(f"{mark} {rel}  记录 {info['records']}  文本 {info['texts']}"
              f"  第一人称旁白 {info['first_person']}")
        for e in errs:
            print(f"     ❌ {e}")
        if args.verbose:
            for w in warns:
                print(f"     ⚠  {w}")
        total_err += len(errs)
        total_warn += len(warns)
        if errs:
            bad_files.append(rel)

    print(f"\n合计：错误 {total_err} / 警告 {total_warn}（{len(targets)} 个文件）")
    if bad_files:
        print("有错误的文件：")
        for f in bad_files:
            print(f"  - {f}")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
