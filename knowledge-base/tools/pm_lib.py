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
def _pick_base_pack() -> str:
    """零协基础包目录名。

    优先环境变量 LIMBUS_BASE_PACK；否则扫描工作区里所有
    LimbusLocalize_latest*，按 Info/version.json 的 version 取最大的那个。

    ⚠️ 不要写死版本号——零协每次更新都会换目录名，写死会导致
       零协一升级、旧目录一删，全部工具就指向不存在的路径。
    """
    env = os.environ.get("LIMBUS_BASE_PACK")
    if env:
        return env
    import glob
    best, best_v = None, -1
    for d in sorted(glob.glob(os.path.join(WORKSPACE, "LimbusLocalize_latest*"))):
        vj = os.path.join(d, "LimbusCompany_Data", "Lang", "LLC_zh-CN",
                          "Info", "version.json")
        try:
            with open(vj, encoding="utf-8-sig") as fh:
                v = json.load(fh).get("version", 0)
        except Exception:
            v = 0
        if v > best_v:
            best, best_v = os.path.basename(d), v
    return best or "LimbusLocalize_latest"


CN_LOCALIZE = os.path.join(
    WORKSPACE, _pick_base_pack(), "LimbusCompany_Data", "Lang", "LLC_zh-CN",
)

LANG_PREFIX = {"kr": "KR_", "en": "EN_", "jp": "JP_"}
LANG_DIR = {
    "cn": CN_LOCALIZE,
    "kr": os.path.join(OFFICIAL_LOCALIZE, "kr"),
    "en": os.path.join(OFFICIAL_LOCALIZE, "en"),
    "jp": os.path.join(OFFICIAL_LOCALIZE, "jp"),
}
LANGS = ("cn", "kr", "en", "jp")

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
    if not force and os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, encoding="utf-8") as fh:
            return json.load(fh)

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
    return index


# ---------------------------------------------------------------- 读取文本


def load_file(lang: str, relpath: str) -> list[dict[str, Any]]:
    """读一个 json，统一返回记录列表。"""
    path = os.path.join(LANG_DIR[lang], relpath)
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        return []
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
    skip = {"id", "key", "Id", "ID", "scene", "code", "type", "category"}
    if not keep_meta:
        skip |= {"model", "teller"}
    out: dict[str, str] = {}
    for k, v in rec.items():
        if k in skip:
            continue
        if isinstance(v, str) and v.strip():
            out[k] = v
        elif isinstance(v, list):
            # 例如 options / levelList：递归收集其中的字符串
            stack = list(v)
            i = 0
            while stack:
                item = stack.pop()
                if isinstance(item, str) and item.strip():
                    out[f"{k}[{i}]"] = item
                    i += 1
                elif isinstance(item, dict):
                    stack.extend(item.values())
                elif isinstance(item, list):
                    stack.extend(item)
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
        merged: dict[str, dict[str, Any]] = {}
        order: list[str] = []
        for i, rec in enumerate(recs):
            key = record_key(rec) or f"#{i}"
            if key not in merged:
                order.append(key)
                merged[key] = {"_id": key}
            for fk, fv in text_fields(rec, keep_meta=True).items():
                merged[key].setdefault(fk, fv)
        out[lang] = [merged[k] for k in order]
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
