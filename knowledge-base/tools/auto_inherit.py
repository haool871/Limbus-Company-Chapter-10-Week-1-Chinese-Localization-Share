"""序列核验的零协复用：同一 key 的对话记录中，若含当前行的上下文窗口与
基线快照逐字一致，即可判定为同一场景同一说话人，直接采用零协译文。

输出紧凑草稿 {"<可编辑序号>": [译文, 依据]}，分为
  seq  上下文窗口逐字一致（可直接采用，附证据）
  uniq 仅整句在全语料唯一命中（需人工按上下文确认）
  none 无先例（必须翻译）
用法：
  python3 tools/auto_inherit.py --file RPGSystem/rpg-loc-dialogue-floor-1-b.json --out out/draft_x.json
  python3 tools/auto_inherit.py --all --outdir out/drafts
"""
from __future__ import annotations
import argparse
import collections
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import localization_core as C  # noqa: E402
import versioned_sources as V  # noqa: E402

KB = Path(__file__).resolve().parent.parent
WINDOW = 2


def leaves(obj, path=()):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, path + (i,))


def load_batch(batch):
    return json.loads((KB / batch / 'batch.json').read_text(encoding='utf-8'))


def build_old(batch):
    """old[key][j] = (窗口 KR 元组, 该行中文, 出处)；另建全局整句索引。"""
    meta = load_batch(batch)
    oroot, om = V.snapshot(meta['old_snapshot'])
    by_key = collections.defaultdict(dict)
    by_text = collections.defaultdict(list)
    root = Path(oroot) / 'kr'
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith('.json'):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), root)
            try:
                kr = V.read(oroot, om, 'kr', rel)
                zh = V.read(oroot, om, 'base', rel)
            except Exception:
                continue
            for rec, zrec in zip((kr or {}).get('dataList') or [], (zh or {}).get('dataList') or []):
                if not (isinstance(rec, dict) and isinstance(rec.get('texts'), list)):
                    continue
                key = rec.get('key')
                texts = [t.get('text') if isinstance(t, dict) else None for t in rec['texts']]
                ztexts = [t.get('text') if isinstance(t, dict) else None for t in (zrec.get('texts') or [])]
                for j, t in enumerate(texts):
                    if not isinstance(t, str) or not t.strip():
                        continue
                    lo, hi = max(0, j - WINDOW), min(len(texts), j + WINDOW + 1)
                    win = tuple(texts[lo:hi])
                    off = j - lo
                    zh_txt = ztexts[j] if j < len(ztexts) else None
                    slot = (key, win, off)
                    if not (isinstance(zh_txt, str) and zh_txt.strip()):
                        continue
                    prev = by_key.get(slot)
                    if prev is None:
                        by_key[slot] = {'zh': zh_txt, 'file': rel, 'pos': j}
                    elif prev['zh'] != zh_txt:
                        prev['conflict'] = True
            # 整句索引覆盖所有语言文件（含剧情/技能等非 texts 结构）
            zmap = dict(leaves(zh))
            for path, text in leaves(kr):
                if not text.strip():
                    continue
                zh_txt = zmap.get(path)
                if isinstance(zh_txt, str) and zh_txt.strip() and zh_txt != text:
                    by_text[text].append({'zh': zh_txt, 'file': rel})
    return by_key, by_text


def draft_file(batch, old, rel, meta):
    by_key, by_text = old
    entry = meta['files'][rel]
    nroot, nm = V.snapshot(meta['new_snapshot'])
    lang = entry['source_language']
    obj = V.read(nroot, nm, lang, rel)
    dl = (obj or {}).get('dataList') if isinstance(obj, dict) else None
    rows = []
    for i, row in enumerate(entry['editable']):
        path = row['path']
        src = row['source']
        out = {'kind': 'none', 'text': '', 'note': ''}
        key = None
        j = None
        rec = None
        if isinstance(dl, list):
            pos = path[1] if len(path) > 1 and isinstance(path[1], int) else None
            if pos is not None and 0 <= pos < len(dl):
                rec = dl[pos]
                key = rec.get('key') if isinstance(rec, dict) else None
                for k, step in enumerate(path):
                    if step == 'texts' and k + 1 < len(path) and isinstance(path[k + 1], int):
                        j = path[k + 1]
        if j is not None and isinstance(rec, dict) and isinstance(rec.get('texts'), list):
            texts = [t.get('text') if isinstance(t, dict) else None for t in rec['texts']]
            lo, hi = max(0, j - WINDOW), min(len(texts), j + WINDOW + 1)
            win = tuple(texts[lo:hi])
            off = j - lo
            hit = by_key.get((key, win, off))
            if hit and hit.get('conflict'):
                hit = None
            if hit and hit['zh'].strip() and win[off] == src:
                out = {'kind': 'seq', 'text': hit['zh'],
                       'note': '上下文窗口(%d行)与零协 %s 同 key 记录逐字一致' % (len(win), hit['file'])}
        if out['kind'] == 'none':
            hits = [h for h in by_text.get(src, []) if h['zh'].strip()]
            uniq = {h['zh'] for h in hits}
            if len(uniq) == 1 and hits:
                out = {'kind': 'uniq', 'text': hits[0]['zh'],
                       'note': '整句在全语料唯一命中（%s，%d 处）' % (hits[0]['file'], len(hits))}
            elif len(uniq) > 1:
                out = {'kind': 'uniq', 'text': '', 'note': '整句有多种零协译法(%d 种)，需按上下文选择' % len(uniq),
                       'options': sorted(uniq)[:6]}
        rows.append(out)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--file'); ap.add_argument('--all', action='store_true')
    ap.add_argument('--out'); ap.add_argument('--outdir', default='out/drafts')
    ap.add_argument('--only', default=None, help='只处理前缀')
    ap.add_argument('--batch', default=None)
    args = ap.parse_args()
    batch = args.batch or json.loads((KB / 'project.json').read_text(encoding='utf-8'))['active_batch']
    meta = load_batch(batch)
    old = build_old(batch)
    targets = [args.file] if args.file else sorted(meta['files'])
    if args.only:
        targets = [t for t in targets if t.startswith(tuple(args.only.split(',')))]
    stats = collections.Counter()
    total = collections.Counter()
    for rel in targets:
        rows = draft_file(batch, old, rel, meta)
        for r in rows:
            stats[r['kind']] += 1
        total['fields'] += len(rows)
        if args.file and args.out:
            Path(args.out).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
        else:
            slug = rel.replace('/', '__')[:-5] if rel.endswith('.json') else rel.replace('/', '__')
            Path(args.outdir).mkdir(parents=True, exist_ok=True)
            (Path(args.outdir) / (slug + '.json')).write_text(
                json.dumps({'file': rel, 'rows': rows}, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'files': len(targets), 'fields': total['fields'], 'kinds': dict(stats)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
