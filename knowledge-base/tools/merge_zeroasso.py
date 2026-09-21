#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把补丁里「仍用旧译」的字段合并为最新零协译文。

背景
  补丁的定位是「零协的缺口补充包」。零协每次更新都会重译一批旧内容，
  如果补丁继续用旧译覆盖，用户装了补丁反而比只用零协更旧。
  用户裁决：**字段级合并——零协有译文的一律采用零协，零协为空/缺记录处保留我们的。**

规则（务必逐条遵守）
  1. 零协某字段是**非空字符串**            → 用零协的（零协为准）
  2. 零协该字段为空/缺失，我们有内容        → 保留我们的（我们补的缺口）
  3. 零协**没有这条记录**                  → 整条保留我们的（我们独有的新增）
  4. 零协**没有这个文件**                  → 整个文件不动
  5. 非字符串字段（id/key/index/model/…）  → 一律以**补丁为准**，绝不因合并而改动
     （id/key 是定位键，动了会错位；数字索引同理）
  6. 合并后某些覆盖文件可能只剩我们独有的记录 → 仍然保留文件，不做删除

安全
  每次运行都会把「被替换的旧译文」全量写入 --report，
  可用 --revert 从报告回滚，不会出现不可逆的静默改动。

用法
  python3 tools/merge_zeroasso.py --dry-run        # 只看会改多少
  python3 tools/merge_zeroasso.py                  # 正式合并
  python3 tools/merge_zeroasso.py --limit 5        # 先试 5 个文件
"""
from __future__ import annotations

import argparse
import glob
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
WS = os.path.dirname(_KB)
PATCH = os.path.join(_KB, "patch_v2")
REVIEW = os.path.join(_KB, "terms", "_review")


def pick_base(explicit: str | None = None) -> str:
    """零协基准包目录：取 version 最大的 LimbusLocalize_latest*。"""
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
    if not best:
        raise SystemExit("❌ 找不到零协基础包")
    return os.path.join(best, "LimbusCompany_Data", "Lang", "LLC_zh-CN")


def load(p):
    with open(p, encoding="utf-8-sig") as fh:
        return json.load(fh)


def rec_key(r: dict):
    return r.get("id") if r.get("id") is not None else r.get("key")


def merge_value(pr, bv, path, changes, stat):
    """递归合并单个值。以「零协为准、零协留空处保留我们」为核心。

    - 两边都是 str  → 零协非空则采用零协；零协为空而我们非空 → 保留我们的
    - 两边都是 dict → 递归（零协有而我们没有的非空字段补上）
    - 两边都是 list → 按元素的 index 字段对齐（无 index 则按位置），递归
    - 其余（int/bool/None 等定位类字段）→ 规则 5：一律以补丁为准，不动
    """
    if isinstance(bv, str) and isinstance(pr, str):
        if bv.strip():
            if bv != pr:
                changes.append((".".join(path), pr, bv))
                stat["adopted"] += 1
                return bv
            return pr
        # 零协留空：保留我们的（规则 2）
        stat["field_only_ours"] += 1
        return pr

    if isinstance(bv, dict) and isinstance(pr, dict):
        for f, v in bv.items():
            if f not in pr:
                if isinstance(v, str):
                    if v.strip():
                        pr[f] = v
                        stat["adopted"] += 1
                elif isinstance(v, (dict, list)):
                    if v:
                        pr[f] = v
                        stat["adopted"] += 1
                continue
            pr[f] = merge_value(pr[f], v, path + [f], changes, stat)
        return pr

    if isinstance(bv, list) and isinstance(pr, list):
        bidx = {}
        for e in bv:
            if isinstance(e, dict) and "index" in e:
                bidx.setdefault(e["index"], []).append(e)
        for i, pe in enumerate(pr):
            if not isinstance(pe, dict):
                continue
            cands = bidx.get(pe.get("index")) if "index" in pe else None
            if not cands:
                cands = [bv[i]] if i < len(bv) and isinstance(bv[i], dict) else []
            if not cands:
                continue
            be = cands[0]
            for f in list(be.keys()):
                if f not in pe:
                    v = be[f]
                    if isinstance(v, str) and v.strip():
                        pe[f] = v
                        stat["adopted"] += 1
                    continue
                pe[f] = merge_value(pe[f], be[f], path + [str(pe.get("index", i)), f],
                                    changes, stat)
        return pr

    # 非字符串标量：规则 5，以补丁为准
    return pr


def merge_file(patch_obj, base_obj, keep_extra=True):
    """就地合并一个文件，返回 (改动列表, 统计)。

    改动列表元素: (记录键, 字段路径, 旧值, 新值)
    """
    changes = []
    stat = {"adopted": 0, "rec_only_ours": 0, "field_only_ours": 0}

    pl = patch_obj.get("dataList") if isinstance(patch_obj, dict) else patch_obj
    bl = base_obj.get("dataList") if isinstance(base_obj, dict) else base_obj
    if not isinstance(pl, list) or not isinstance(bl, list):
        return changes, stat

    bmap = {}
    for i, r in enumerate(bl):
        if isinstance(r, dict):
            bmap.setdefault(rec_key(r), []).append((i, r))

    for i, pr in enumerate(pl):
        if not isinstance(pr, dict):
            continue
        k = rec_key(pr)
        cands = bmap.get(k) or []
        if not cands:
            stat["rec_only_ours"] += 1
            continue
        # ⚠️ id=null 的记录会全部落进同一个键桶（S1004B/S1005B 就有），
        #    此时「整表下标」才是唯一可靠的对齐依据，
        #    绝不能拿整表下标 i 去索引桶内列表（会错位到别的记录）。
        br = None
        for pos, r in cands:
            if pos == i:
                br = r
                break
        if br is None:
            # 同 id 多条：取桶内第 (i - 该键首次出现位置) 个
            first = cands[0][0]
            j = i - first
            br = cands[j][1] if 0 <= j < len(cands) else cands[0][1]

        # 记录层字段：先复制键集合，避免边遍历边插入
        for field in list(br.keys()):
            if field not in pr:
                bv = br[field]
                if isinstance(bv, str) and bv.strip():
                    pr[field] = bv
                    stat["adopted"] += 1
                continue
            pr[field] = merge_value(pr[field], br[field], [str(k), field], changes, stat)
    return changes, stat


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=None, help="指定零协基础包 Lang/LLC_zh-CN 路径")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个文件（试跑用）")
    ap.add_argument("--report", default=os.path.join(REVIEW, "merge_zeroasso.tsv"))
    ap.add_argument("--revert", action="store_true", help="按报告回滚（忽略 --base 比对）")
    args = ap.parse_args()

    os.makedirs(REVIEW, exist_ok=True)

    # ── 回滚模式
    if args.revert:
        rows = []
        with open(args.report, encoding="utf-8") as fh:
            for line in fh:
                rel, k, field, old, new = line.rstrip("\n").split("\t")
                rows.append((rel, k, field, old, new))
        touched = {}
        for rel, k, field, old, _new in rows:
            p = os.path.join(PATCH, rel)
            if p not in touched:
                touched[p] = load(p)
            pl = touched[p].get("dataList")
            for r in pl:
                if isinstance(r, dict) and str(rec_key(r)) == k and field in r:
                    r[field] = old
                    break
        for p, obj in touched.items():
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(obj, fh, ensure_ascii=False, indent=2)
        print(f"↩️  已按报告回滚 {len(rows)} 处，涉及 {len(touched)} 个文件")
        return 0

    base = pick_base(args.base)
    print(f"零协基准: {os.path.relpath(base, WS)}")

    files = sorted(glob.glob(os.path.join(PATCH, "**", "*.json"), recursive=True))
    if args.limit:
        files = files[:args.limit]

    all_changes = []
    nfile = 0
    tot = {"adopted": 0, "rec_only_ours": 0, "field_only_ours": 0}
    for p in files:
        rel = os.path.relpath(p, PATCH)
        bp = os.path.join(base, rel)
        if not os.path.exists(bp):
            continue
        pobj, bobj = load(p), load(bp)
        changes, stat = merge_file(pobj, bobj)
        for path, o, n in changes:
            all_changes.append((rel, path, o.replace("\n", "\\n").replace("\t", " "),
                                n.replace("\n", "\\n").replace("\t", " ")))
        for kk in tot:
            tot[kk] += stat[kk]
        if changes:
            nfile += 1
            if not args.dry_run:
                with open(p, "w", encoding="utf-8") as fh:
                    json.dump(pobj, fh, ensure_ascii=False, indent=2)

    if not args.dry_run:
        with open(args.report, "w", encoding="utf-8") as fh:
            for row in all_changes:
                fh.write("\t".join(row) + "\n")

    print(f"\n{'（dry-run，未写入）' if args.dry_run else '✅ 已写入'}")
    print(f"  采用零协译文     : {tot['adopted']} 处（涉及 {nfile} 个文件）")
    print(f"  我们独有的记录   : {tot['rec_only_ours']} 条（零协还没译，保留）")
    print(f"  零协为空我们补的 : {tot['field_only_ours']} 处（保留）")
    if not args.dry_run:
        print(f"  报告（可回滚）   : {os.path.relpath(args.report, WS)}")
        print(f"  回滚：python3 tools/merge_zeroasso.py --revert")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
