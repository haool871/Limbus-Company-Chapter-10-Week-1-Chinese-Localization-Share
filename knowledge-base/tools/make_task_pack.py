"""为当前批次生成翻译工作包：上下文、可复用零协实证、术语线索。

用法：
  python3 tools/make_task_pack.py build-index [--batch batches/<名称>]
  python3 tools/make_task_pack.py pack --file StoryData/S1017B.json [--from 0 --to 40] --out out/pack.txt
  python3 tools/make_task_pack.py list [--batch batches/<名称>]

索引把基线快照的韩文原文与当时零协中文按“同文件同路径”配对，再按
  ①(说话人, 原文) ②(原文)  两种键聚合。同一韩文句在旧路线里已有零协译文时，
可直接作为本轮候选；脚本只给证据，是否采用仍需按上下文判断。
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
LANGS = ('kr', 'en', 'jp')


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
    meta = json.loads((KB / batch / 'batch.json').read_text(encoding='utf-8'))
    return meta


def index_path(batch):
    return KB / 'out' / ('reuse_index_%s.json' % Path(batch).name)


def build_index(batch):
    meta = load_batch(batch)
    oroot, om = V.snapshot(meta['old_snapshot'])
    by_text = collections.defaultdict(list)
    by_spk = collections.defaultdict(list)
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
            zmap = dict(leaves(zh))
            for path, text in leaves(kr):
                if not text.strip():
                    continue
                target = zmap.get(path)
                if not isinstance(target, str) or not target.strip() or target == text:
                    continue
                spk = None
                if len(path) >= 2 and path[-1] == 'text' and path[-3] == 'texts':
                    rec = kr
                    try:
                        for step in path[:-1]:
                            rec = rec[step]
                        if isinstance(rec, dict):
                            spk = rec.get('speaker')
                    except Exception:
                        spk = None
                rec_ = {'zh': target, 'file': rel, 'speaker': spk, 'path': C.pointer(path)}
                by_text[text].append(rec_)
                if spk:
                    by_spk[(spk, text)].append(rec_)
    data = {'old_snapshot': meta['old_snapshot'],
            'pairs': len(by_text), 'by_text': by_text,
            'by_speaker': {'%s\x1f%s' % k[0:2]: v for k, v in by_spk.items()}}
    out = index_path(batch)
    out.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return {'index': str(out), 'distinct_text': len(by_text),
            'distinct_speaker_text': len(by_spk),
            'occurrences': sum(len(v) for v in by_text.values())}


def load_index(batch):
    p = index_path(batch)
    if not p.exists():
        raise SystemExit('缺少复用索引，先运行：python3 tools/make_task_pack.py build-index')
    return json.loads(p.read_text(encoding='utf-8'))


def reuse_for(idx, text, speaker):
    hits = []
    if speaker:
        hits = idx['by_speaker'].get('%s\x1f%s' % (speaker, text), [])
    if hits:
        return hits, 'speaker'
    return idx['by_text'].get(text, []), 'text'


def record_context(obj, path, window=2):
    """返回 (说话人, 上下文行列表, 当前行下标)。上下文按同一 dataList 记录内 texts 展开。"""
    if not isinstance(obj, dict):
        return None, [], None, None
    dl = obj.get('dataList')
    if not isinstance(dl, list):
        return None, [], None, None
    pos = None
    for i, step in enumerate(path):
        if step == 'dataList' and i + 1 < len(path):
            pos = path[i + 1]
            break
    if not isinstance(pos, int) or not (0 <= pos < len(dl)):
        return None, [], None, None
    rec = dl[pos]
    lines = []
    cur = None
    if isinstance(rec, dict) and isinstance(rec.get('texts'), list):
        tj = None
        for i, step in enumerate(path):
            if step == 'texts' and i + 1 < len(path) and isinstance(path[i + 1], int):
                tj = path[i + 1]
        for j, t in enumerate(rec['texts']):
            if not isinstance(t, dict):
                continue
            lines.append({'speaker': t.get('speaker'), 'text': t.get('text', ''), 'mark': j == tj})
            if j == tj:
                cur = len(lines) - 1
    elif isinstance(rec, dict):
        last = path[-1]
        for k, v in rec.items():
            if isinstance(v, str):
                lines.append({'speaker': None, 'text': v, 'mark': k == last})
                if k == last:
                    cur = len(lines) - 1
    speaker = lines[cur]['speaker'] if cur is not None else None
    return (rec.get('key') if isinstance(rec, dict) else None), lines, cur, speaker


def make_pack(batch, rel, start, end, out):
    meta = load_batch(batch)
    idx = load_index(batch)
    nroot, nm = V.snapshot(meta['new_snapshot'])
    oroot, om = V.snapshot(meta['old_snapshot'])
    entry = meta['files'][rel]
    lang = entry['source_language']
    kr = V.read(nroot, nm, lang, rel)
    out_lines = []
    out_lines.append('# 翻译工作包 %s（源=%s，本批次可编辑字段 %d）' % (rel, lang, len(entry['editable'])))
    out_lines.append('# 语义以本包 KR 原文为准；术语与文风参考零协实证；写回用 edits.json')
    for i, row in enumerate(entry['editable']):
        if i < start or (end is not None and i > end):
            continue
        path = row['path']
        key, lines, cur, speaker = record_context(kr, path)
        en = None
        try:
            en = C.get(V.read(nroot, nm, 'en', rel), path)
        except Exception:
            en = None
        out_lines.append('')
        out_lines.append('## [%d] %s' % (i, C.pointer(path)))
        out_lines.append('KR: %s' % row['source'].replace('\n', '\\n'))
        if isinstance(en, str) and en.strip() and en != row['source']:
            out_lines.append('EN: %s' % en.replace('\n', '\\n'))
        if lines:
            lo = max(0, (cur if cur is not None else 0) - 2)
            hi = min(len(lines), (cur if cur is not None else 0) + 3)
            for j in range(lo, hi):
                mark = '>>' if lines[j]['mark'] else '  '
                out_lines.append('%s %s: %s' % (mark, lines[j]['speaker'] or '-', lines[j]['text'].replace('\n', '\\n')))
        cand, how = reuse_for(idx, row['source'], speaker)
        uniq = {}
        for h in cand:
            uniq.setdefault(h['zh'], h)
        if uniq:
            out_lines.append('零协候选(%s, %d 种):' % (how, len(uniq)))
            for zh, h in list(uniq.items())[:4]:
                out_lines.append('    %s   ← %s @%s' % (zh.replace('\n', '\\n'), h['file'], h['path']))
        else:
            out_lines.append('零协候选: 无')
    Path(out).write_text('\n'.join(out_lines) + '\n', encoding='utf-8')
    return out


def term_query(batch, queries, limit, scope=None):
    """在基线快照的韩文原文中找含指定词的字段，列出零协当时的中文与出处。"""
    meta = load_batch(batch)
    oroot, om = V.snapshot(meta['old_snapshot'])
    if scope:
        prefixes = tuple(scope.split(','))
    else:
        prefixes = None
    hits = collections.defaultdict(list)
    root = Path(oroot) / 'kr'
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith('.json'):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), root)
            if prefixes and not rel.startswith(prefixes):
                continue
            try:
                kr = V.read(oroot, om, 'kr', rel)
                zh = V.read(oroot, om, 'base', rel)
            except Exception:
                continue
            zmap = dict(leaves(zh))
            for path, text in leaves(kr):
                if not text.strip():
                    continue
                for q in queries:
                    if q in text:
                        target = zmap.get(path)
                        if isinstance(target, str) and target.strip():
                            hits[q].append((text, target, rel, C.pointer(path)))
    for q in queries:
        print('# 术语实证: %s  （命中 %d 条）' % (q, len(hits[q])))
        seen = set()
        shown = 0
        for text, target, rel, ptr in hits[q]:
            if (text, target) in seen:
                continue
            seen.add((text, target))
            print('  KR: %s' % text.replace('\n', '\\n')[:180])
            print('  ZH: %s' % target.replace('\n', '\\n')[:180])
            print('      ← %s @%s' % (rel, ptr))
            shown += 1
            if shown >= limit:
                break
        print()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build-index'); b.add_argument('--batch', default=None)
    p = sub.add_parser('pack')
    p.add_argument('--file', required=True); p.add_argument('--from', dest='start', type=int, default=0)
    p.add_argument('--to', dest='end', type=int, default=None); p.add_argument('--out', required=True)
    p.add_argument('--batch', default=None)
    l = sub.add_parser('list'); l.add_argument('--batch', default=None)
    t = sub.add_parser('terms')
    t.add_argument('--query', required=True); t.add_argument('--limit', type=int, default=6)
    t.add_argument('--scope', default=None); t.add_argument('--batch', default=None)
    args = ap.parse_args()
    batch = args.batch
    if batch is None:
        proj = json.loads((KB / 'project.json').read_text(encoding='utf-8'))
        batch = proj.get('active_batch')
        if not batch:
            raise SystemExit('没有活动批次')
    if args.cmd == 'build-index':
        print(json.dumps(build_index(batch), ensure_ascii=False, indent=1))
    elif args.cmd == 'list':
        meta = load_batch(batch)
        rows = sorted(((len(e['editable']), r, e['source_language']) for r, e in meta['files'].items()), reverse=True)
        for n, r, lg in rows:
            print('%5d  [%s] %s' % (n, lg, r))
    elif args.cmd == 'terms':
        term_query(batch, [q.strip() for q in args.query.split(',') if q.strip()], args.limit, args.scope)
    else:
        print(make_pack(batch, args.file, args.start, args.end, args.out))


if __name__ == '__main__':
    main()
