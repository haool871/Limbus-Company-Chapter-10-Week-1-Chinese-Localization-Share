"""韩文键术语表：由权威术语表 + 基线快照同路径对齐生成，供韩文源文查词。

现有 `terms/术语表.md` / `glossary_all.clean.tsv` 是英→中键；本轮源文为韩文，
因此按“同一文件同一路径”把 kr/en/base(cn) 三语对齐，直接得到韩→中实证，
并把能在术语表里找到对应英文的行标记为 curated。

用法：
  python3 tools/glossary_kr.py build [--out terms/术语表_kr.tsv]
  python3 tools/glossary_kr.py lookup --query "시지프" [--limit 8]
  python3 tools/glossary_kr.py lookup --query "화장실,마네킹" --limit 5
"""
from __future__ import annotations
import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import localization_core as C  # noqa: E402
import versioned_sources as V  # noqa: E402

KB = Path(__file__).resolve().parent.parent
TSV = KB / 'terms' / '术语表_kr.tsv'
GLOSSARY = KB / 'terms' / '术语表.md'


def leaves(obj, path=()):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, path + (i,))


def load_curated():
    """解析术语表.md 的 en->cn，用于标注 curated。"""
    pairs = {}
    if not GLOSSARY.exists():
        return pairs
    for line in GLOSSARY.read_text(encoding='utf-8').splitlines():
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 2 or cells[0] in ('English', '---') or set(cells[0]) <= {'-'}:
            continue
        if cells[0].startswith('**') or cells[0] == '':
            continue
        pairs.setdefault(cells[0], cells[1])
    return pairs


def build(out):
    proj = json.loads((KB / 'project.json').read_text(encoding='utf-8'))
    batch = proj['active_batch']
    meta = json.loads((KB / batch / 'batch.json').read_text(encoding='utf-8'))
    root, man = V.snapshot(meta['old_snapshot'])
    curated = load_curated()
    rows = {}
    base = Path(root)
    for dirpath, _, files in os.walk(base / 'kr'):
        for fn in files:
            if not fn.endswith('.json'):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), base / 'kr')
            try:
                kr = V.read(root, man, 'kr', rel)
                cn = V.read(root, man, 'base', rel)
                en = V.read(root, man, 'en', rel)
            except Exception:
                continue
            emap = dict(leaves(en))
            cmap = dict(leaves(cn))
            for path, k in leaves(kr):
                if not k.strip():
                    continue
                c = cmap.get(path)
                if not isinstance(c, str) or not c.strip() or c == k:
                    continue
                e = emap.get(path)
                e = e if isinstance(e, str) else ''
                key = (k, c)
                row = rows.get(key)
                if row is None:
                    rows[key] = {'en': e, 'src': rel,
                                 'curated': 'Y' if (e and e in curated and curated[e] == c) else ''}
                else:
                    if not row['en'] and e:
                        row['en'] = e
                    if e and e in curated and curated[e] == c:
                        row['curated'] = 'Y'
    lines = ['# kr\tcn\ten\tcurated\tsource']
    for (k, c), r in sorted(rows.items()):
        lines.append('%s\t%s\t%s\t%s\t%s' % (k.replace('\n', '\\n'), c.replace('\n', '\\n'),
                                             r['en'].replace('\n', '\\n'), r['curated'], r['src']))
    Path(out).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return {'entries': len(rows), 'curated': sum(1 for r in rows.values() if r['curated']), 'out': str(out)}


def lookup(queries, limit, curated_only=False, max_len=None):
    if not TSV.exists():
        raise SystemExit('缺少 %s，先运行 build' % TSV)
    rows = []
    for line in TSV.read_text(encoding='utf-8').splitlines()[1:]:
        parts = line.split('\t')
        if len(parts) < 5:
            continue
        rows.append(parts)
    for q in queries:
        hits = [r for r in rows if q in r[0]]
        if curated_only:
            hits = [r for r in hits if r[3] == 'Y']
        if max_len:
            hits = [r for r in hits if len(r[0]) <= max_len]
        hits.sort(key=lambda r: (len(r[0]), r[0]))
        print('# %s  （命中 %d 条，显示前 %d）' % (q, len(hits), min(limit, len(hits))))
        seen = set()
        n = 0
        for r in hits:
            if (r[0], r[1]) in seen:
                continue
            seen.add((r[0], r[1]))
            print('  %s\t%s\t[en: %s]%s\t← %s' % (r[0], r[1], r[2][:40], ' ★术语表' if r[3] == 'Y' else '', r[4]))
            n += 1
            if n >= limit:
                break
        print()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build'); b.add_argument('--out', default=str(TSV))
    l = sub.add_parser('lookup')
    l.add_argument('--query', required=True); l.add_argument('--limit', type=int, default=8)
    l.add_argument('--curated-only', action='store_true'); l.add_argument('--max-len', type=int, default=None)
    a = ap.parse_args()
    if a.cmd == 'build':
        print(json.dumps(build(a.out), ensure_ascii=False))
    else:
        lookup([q.strip() for q in a.query.split(',') if q.strip()], a.limit, a.curated_only, a.max_len)


if __name__ == '__main__':
    main()
