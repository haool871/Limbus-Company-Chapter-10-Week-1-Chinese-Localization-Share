#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导出某个 StoryData/RPG 文件的「带上下文」逐条对照，供人工重译。

输出每条：pos / id / model(说话人) / place / KR / EN / CN，
并额外打印「同场景连续性提示」：相邻条目的说话人序列，便于判断回应关系。

用法:
  python3 tools/ctx_dump.py StoryData/S1004B.json
  python3 tools/ctx_dump.py StoryData/S1004B.json --out /tmp/x.txt
  python3 tools/ctx_dump.py --list                # 列出可导出的文件
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB = os.path.dirname(_HERE)
WORKSPACE = os.path.dirname(_KB)
PATCH = os.path.join(_KB, "patch_v2")
GAME = os.environ.get(
    "LIMBUS_GAME_ROOT",
    "/home/shb/.local/share/Steam/steamapps/common/Limbus Company",
)
LOC = os.path.join(GAME, "LimbusCompany_Data", "Assets", "Resources_moved", "Localize")

NAMES = {
    "돈키호테": "堂吉诃德", "파우스트": "浮士德", "이상": "李箱", "뫼르소": "默尔索",
    "홍루": "鸿璐", "히스클리프": "希斯克利夫", "이스마엘": "以实玛利", "로쟈": "罗佳",
    "싱클레어": "辛克莱", "오티스": "奥提斯", "그레고르": "格里高尔", "료슈": "良秀",
    "단테": "但丁",
}


def load(path):
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return json.load(fh).get("dataList") or []
    except Exception:
        return []


def idx(path):
    return {str(r.get("id")): r for r in load(path) if isinstance(r, dict)}


def find(rel: str, lang: str, prefix: str):
    d, f = os.path.split(rel)
    for cand in (prefix + f, f):
        p = os.path.join(LOC, lang, d, cand)
        if os.path.exists(p):
            return p
    return None


def speaker(rec: dict) -> str:
    m = str(rec.get("model") or "")
    if not m:
        return "（旁白）"
    return NAMES.get(m, m)


def walk_texts(rec):
    """按字段路径产出 (path, text)。"""
    def go(o, path=""):
        if isinstance(o, str):
            if o.strip():
                yield path, o
        elif isinstance(o, dict):
            for k, v in o.items():
                if k in ("id",):
                    continue
                yield from go(v, f"{path}.{k}" if path else k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                yield from go(v, f"{path}[{i}]")
    return list(go({k: v for k, v in rec.items() if k != "id"}))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        for dp, _dn, fn in os.walk(PATCH):
            for f in sorted(fn):
                if f.endswith(".json"):
                    print(os.path.relpath(os.path.join(dp, f), PATCH))
        return 0

    rel = args.target
    cn_path = os.path.join(PATCH, rel)
    if not os.path.exists(cn_path):
        print(f"不存在: {cn_path}", file=sys.stderr)
        return 2
    kp, ep = find(rel, "kr", "KR_"), find(rel, "en", "EN_")
    K = idx(kp) if kp else {}
    E = idx(ep) if ep else {}
    C = load(cn_path)

    lines = []
    lines.append(f"# {rel}")
    lines.append(f"# KR={'有' if kp else '无'}  EN={'有' if ep else '无'}  记录={len(C)}")
    lines.append("")
    # 说话人序列（看回应关系）
    seq = []
    for i, r in enumerate(C):
        if isinstance(r, dict) and r.get("model"):
            seq.append(speaker(r))
        else:
            seq.append("（旁白）")
    lines.append("## 说话人序列")
    lines.append(" → ".join(f"{i}:{s}" for i, s in enumerate(seq)))
    lines.append("")
    lines.append("## 逐条对照")
    lines.append("")
    for i, r in enumerate(C):
        if not isinstance(r, dict):
            continue
        rid = str(r.get("id"))
        k = K.get(rid, {})
        e = E.get(rid, {})
        pl = r.get("place") or k.get("place") or e.get("place") or ""
        lines.append(f"--- pos{i} id={rid} [{speaker(r)}]" + (f" place={pl}" if pl else ""))
        if isinstance(k.get("content"), str) and k["content"].strip():
            lines.append(f"  KR| {k['content']}")
        if isinstance(e.get("content"), str) and e["content"].strip():
            lines.append(f"  EN| {e['content']}")
        # 其它字段（teller/title 等）也列出，避免漏译
        for path, txt in walk_texts(r):
            if path == "content":
                lines.append(f"  CN| {txt}")
            else:
                lines.append(f"  CN.{path}| {txt}")
        lines.append("")

    out = "\n".join(lines)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"已写出 {args.out}（{len(out.splitlines())} 行）")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
