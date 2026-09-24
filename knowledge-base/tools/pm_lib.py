#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Project Moon 本地化文本检索库（Limbus Company 四语语料）。

语言代码:
  cn = 零协会汉化 (LimbusLocalize_latest/LimbusCompany_Data/Lang/LLC_zh-CN)
  kr = 官方韩文原文
  en = 官方英文
  jp = 官方日文

官方目录内文件名带语言前缀 (KR_/EN_/JP_)，汉化目录不带前缀。

用法:
  python3 pm_lib.py build                 # 生成/刷新语料索引
  python3 pm_lib.py find 1D101A           # 按文件关键字列出所有语言的同源文件
  python3 pm_lib.py show 1D101A           # 按 id 对齐打印四语文本
  python3 pm_lib.py grep 事务所 -l cn      # 在指定语言里搜文本
"""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Iterable
import collections
import localization_core as C

# ---------------------------------------------------------------- 路径配置

# 游戏安装目录（官方 ko/en/jp 原版文本来源）
GAME_ROOT = os.environ.get(
    "LIMBUS_GAME_ROOT",
    "/home/shb/.local/share/Steam/steamapps/common/Limbus Company",
)
OFFICIAL_LOCALIZE = os.path.join(
    GAME_ROOT, "LimbusCompany_Data", "Assets", "Resources_moved", "Localize"
)

# 工作区根（汉化包来源），默认取本文件上溯两级
_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE = os.environ.get("LIMBUS_WORKSPACE", os.path.dirname(_KB_DIR))
_snapshot = os.environ.get("LIMBUS_SNAPSHOT") or C.state().get("baseline")
CN_LOCALIZE = str(C.KB / _snapshot / "base") if _snapshot else str(C.resolve_base())

LANG_PREFIX = {"kr": "KR_", "en": "EN_", "jp": "JP_"}
LANG_DIR = {
    "cn": CN_LOCALIZE,
    "kr": os.path.join(OFFICIAL_LOCALIZE, "kr"),
    "en": os.path.join(OFFICIAL_LOCALIZE, "en"),
    "jp": os.path.join(OFFICIAL_LOCALIZE, "jp"),
}
LANGS = ("cn", "kr", "en", "jp")
# Pin queries to a recorded baseline unless a snapshot is explicitly selected.
_snapshot = os.environ.get("LIMBUS_SNAPSHOT") or C.state().get("baseline")
if _snapshot:
    from pathlib import Path
    _root = Path(_snapshot)
    if not _root.is_absolute():
        _root = C.KB / _root
    LANG_DIR = {"cn": str(_root / "base"), **{l: str(_root / l) for l in ("kr", "en", "jp")}}


# 索引缓存位置
INDEX_PATH = os.path.join(_KB_DIR, "data", "_file_index.json")

# ---------------------------------------------------------------- 命名映射


def logical_name(lang: str, relpath: str) -> str:
    """把某语言的相对路径映射成'逻辑名'（即汉化包里的相对路径）。

    官方文件统一带语言前缀，去掉即可与汉化包对齐。
    """
    d, b = os.path.split(relpath)
    prefix = LANG_PREFIX.get(lang)
    if prefix and b.startswith(prefix):
        b = b[len(prefix):]
    return os.path.join(d, b) if d else b


def build_index(force: bool = False) -> dict[str, dict[str, str]]:
    """扫描四种语言目录，返回 {逻辑名: {lang: 实际相对路径}}。"""
    for root in LANG_DIR.values():
        if not os.path.isdir(root):
            raise C.DataError(f"语料目录不存在: {root}")
    signature = {lang: {"root": root, "files": sorted(
        (os.path.relpath(os.path.join(dp,f),root), os.stat(os.path.join(dp,f)).st_size,
         os.stat(os.path.join(dp,f)).st_mtime_ns)
        for dp, _dirs, files in os.walk(root) for f in files if f.endswith(".json"))}
        for lang,root in LANG_DIR.items()}
    signature_hash = C.digest(__import__("json").dumps(signature,sort_keys=True).encode())
    meta_path = INDEX_PATH + ".meta.json"
    if not force and os.path.exists(INDEX_PATH) and os.path.exists(meta_path):
        if C.load(meta_path).get("signature") == signature_hash:
            return C.load(INDEX_PATH)

    index: dict[str, dict[str, str]] = {}
    for lang in LANGS:
        root = LANG_DIR[lang]
        if not os.path.isdir(root):
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for fn in filenames:
                if not fn.endswith(".json"):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, fn), root)
                if rel.startswith("Info" + os.sep) or rel.startswith("Font" + os.sep):
                    continue  # 元数据/字体，不是文本
                index.setdefault(logical_name(lang, rel), {})[lang] = rel

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=0, sort_keys=True)
    C.save(meta_path, {"signature": signature_hash, "roots": LANG_DIR})
    return index


# ---------------------------------------------------------------- 读取文本


def load_file(lang: str, relpath: str) -> list[dict[str, Any]]:
    """读一个 json，统一返回记录列表。"""
    path = os.path.join(LANG_DIR[lang], relpath)
    try:
        with open(path, encoding="utf-8-sig") as fh:
            data = json.load(fh)
    except Exception as exc:
        raise C.DataError(f"无法读取语料 {path}: {exc}") from exc
    if isinstance(data, dict):
        for key in ("dataList", "list", "data"):
            if isinstance(data.get(key), list):
                return [r for r in data[key] if isinstance(r, dict)]
        return [data]
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    return []


def record_key(rec: dict[str, Any]) -> str | None:
    """取记录的稳定 id（字符串化）。"""
    for k in ("id", "key", "Id", "ID"):
        if k in rec and rec[k] is not None:
            return str(rec[k])
    return None


def text_fields(rec: dict[str, Any], keep_meta: bool = False) -> dict[str, str]:
    """抽出记录里所有可能的文本字段。

    keep_meta=True 时额外保留 model/teller 等"署名"字段（说话人分析需要）。
    """
    out = {}
    # Keep exact nested field paths instead of flattening by traversal order.
    for path, _logical, value, _ambiguous in C.text_leaves(rec):
        if not keep_meta and any(k in ("model", "teller") for k in path):
            continue
        if not value.strip():
            continue
        key = ""
        for item in path:
            key += f"[{item}]" if isinstance(item,int) else ("." if key else "") + item
        out[key] = value
    if keep_meta:
        for key in ("model", "teller"):
            if isinstance(rec.get(key),str):
                out[key] = rec[key]
    return out


def align(logical: str) -> dict[str, list[dict[str, Any]]]:
    """返回 {lang: 已按 id 归并的记录列表}，用于跨语言对齐。"""
    index = build_index()
    entry = index.get(logical) or index.get(logical.replace(os.sep, "/"))
    if entry is None:
        # 允许用文件名关键字模糊匹配
        cands = [k for k in index if logical in k]
        if len(cands) == 1:
            entry = index[cands[0]]
        elif cands:
            raise SystemExit(
                f"'{logical}' 有多个候选：\n  " + "\n  ".join(sorted(cands)[:20])
            )
        else:
            raise SystemExit(f"找不到文件: {logical}")
    out: dict[str, list[dict[str, Any]]] = {}
    for lang, rel in entry.items():
        recs = load_file(lang, rel)
        seen = collections.Counter()
        totals = collections.Counter(C.identity(rec) for rec in recs)
        aligned = []
        for i, rec in enumerate(recs):
            identity = C.identity(rec)
            occurrence = seen[identity]; seen[identity] += 1
            token = [*identity,occurrence]
            if totals[identity] > 1 or identity[0] == "position":
                token += ["ambiguous", lang]
            key = json.dumps(token,ensure_ascii=False)
            aligned.append({"_id":key, "_position":i, **text_fields(rec, keep_meta=True)})
        out[lang] = aligned
    return out


# ---------------------------------------------------------------- 语料导出


def iter_corpus(langs: Iterable[str] = LANGS):
    """逐文件产出 (逻辑名, lang, 记录)。"""
    index = build_index()
    for logical in sorted(index):
        for lang in langs:
            rel = index[logical].get(lang)
            if not rel:
                continue
            for rec in load_file(lang, rel):
                yield logical, lang, rec


# ---------------------------------------------------------------- CLI


def _cmd_build() -> None:
    index = build_index(force=True)
    per_lang = {l: 0 for l in LANGS}
    for logical, entry in index.items():
        for l in entry:
            per_lang[l] = per_lang.get(l, 0) + 1
    print(f"逻辑文件数: {len(index)}")
    print("各语言文件数:", ", ".join(f"{k}={v}" for k, v in per_lang.items()))


def _cmd_find(kw: str) -> None:
    index = build_index()
    hits = [k for k in index if kw.lower() in k.lower()]
    for k in sorted(hits)[:50]:
        langs = "".join(sorted(index[k]))
        print(f"[{langs}] {k}")
    print(f"共 {len(hits)} 个匹配")


def _cmd_show(logical: str) -> None:
    data = align(logical)
    ids: list[str] = []
    for lang in LANGS:
        for rec in data.get(lang, []):
            if rec["_id"] not in ids:
                ids.append(rec["_id"])
    by_lang = {l: {r["_id"]: r for r in data.get(l, [])} for l in LANGS}
    label = {"cn": "CN", "kr": "KR", "en": "EN", "jp": "JP"}
    for rid in ids:
        print(f"\n### id={rid}")
        for lang in ("kr", "en", "cn", "jp"):
            rec = by_lang[lang].get(rid)
            if not rec:
                continue
            for field, val in rec.items():
                if field == "_id":
                    continue
                print(f"  {label[lang]}.{field}: {val}")


def _cmd_grep(pattern: str, lang: str, limit: int = 40) -> None:
    rx = re.compile(pattern)
    n = 0
    for logical, lg, rec in iter_corpus([lang]):
        for field, val in text_fields(rec).items():
            if rx.search(val):
                rid = record_key(rec)
                print(f"{logical}\t{rid}\t{field}\t{val[:160]}")
                n += 1
                break
        if n >= limit:
            break
    print(f"命中(截断至) {n} 条", file=sys.stderr)


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print(__doc__)
        return
    cmd = argv[1]
    if cmd == "build":
        _cmd_build()
    elif cmd == "find":
        _cmd_find(argv[2])
    elif cmd == "show":
        _cmd_show(argv[2])
    elif cmd == "grep":
        lang = "cn"
        args = argv[2:]
        if "-l" in args:
            i = args.index("-l")
            lang = args[i + 1]
            del args[i:i + 2]
        _cmd_grep(args[0], lang)
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv)
