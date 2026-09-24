"""译文对齐与一致性线索检查（只读）。

覆盖 batch verify 不检查的“语义错位”征兆：
  - 问号/省略号/数字/尖括号包裹等标点与符号不对应
  - 译文长度与原文长度比例异常（错位、漏译、串行的典型征兆）
  - 译文完全没有中日文字符而原文有韩文
  - 同一原文在不同文件/位置译法不一致（同一 src 多种 target）
  - 镜像文件族（Bufs 与 BattleKeywords 等）同源文本译法不一致

这些只是线索，不自动改译文，也不需要为消灭误报而改译。
用法：
  python3 tools/lint_alignment.py [--out out/lint_alignment.tsv] [--top 60]
"""
from __future__ import annotations
import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import localization_core as C  # noqa: E402

KB = Path(__file__).resolve().parent.parent
HANGUL = re.compile(r'[\uac00-\ud7a3]')
CJK = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')
DIGIT = re.compile(r'\d+')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='out/lint_alignment.tsv')
    ap.add_argument('--top', type=int, default=60)
    args = ap.parse_args()
    proj = json.loads((KB / 'project.json').read_text(encoding='utf-8'))
    root = KB / proj['active_batch']
    meta = json.loads((root / 'batch.json').read_text(encoding='utf-8'))
    rows = []
    src_map = collections.defaultdict(set)
    for rel, entry in meta['files'].items():
        obj = C.load(C.inside(root / 'patch', rel))
        for row in entry['editable']:
            try:
                cur = C.get(obj, row['path'])
            except Exception:
                continue
            src, tgt = row['source'], cur
            if not isinstance(tgt, str) or tgt == src or not src.strip():
                continue
            flags = []
            if ('?' in src) != ('？' in tgt) and ('?' in src or '？' in tgt):
                flags.append('问号不对应')
            if ('…' in src) != ('…' in tgt):
                flags.append('省略号不对应')
            if set(DIGIT.findall(src)) - set(DIGIT.findall(tgt)):
                flags.append('数字缺失:' + ','.join(sorted(set(DIGIT.findall(src)) - set(DIGIT.findall(tgt)))[:4]))
            if len(src) >= 10:
                r = len(tgt) / max(1, len(src))
                if r < 0.30:
                    flags.append('过短(%.2f)' % r)
                elif r > 3.2:
                    flags.append('过长(%.2f)' % r)
            if HANGUL.search(src) and not CJK.search(tgt):
                flags.append('译文无中文')
            if src.strip().startswith('<') and src.strip().endswith('>') and not (tgt.strip().startswith('<') and tgt.strip().endswith('>')):
                flags.append('尖括号包裹丢失')
            if flags:
                rows.append((rel, C.pointer(row['path']), '|'.join(flags), src[:60], tgt[:60]))
            src_map[src].add(tgt)
    # 同一原文多种译法
    incons = [(s, sorted(t)) for s, t in src_map.items() if len(t) > 1 and len(s) >= 6]
    with open(KB / args.out, 'w', encoding='utf-8') as fh:
        fh.write('# 对齐线索\n')
        for r in rows:
            fh.write('%s\t%s\t%s\t%s\t%s\n' % r)
        fh.write('# 同一原文多种译法\n')
        for s, ts in incons:
            fh.write('%s\t%s\n' % (s.replace('\n', '\\n')[:80], ' ／ '.join(t.replace('\n', '\\n')[:60] for t in ts[:4])))
    print(json.dumps({'suspect_fields': len(rows), 'inconsistent_sources': len(incons), 'out': args.out},
                     ensure_ascii=False, indent=1))
    print('\n=== 疑点最多的一批 ===')
    for r in rows[:args.top]:
        print('  %-46s %-22s %s' % (r[0][:46], r[1][:22], r[2]))
        print('      KR: %s\n      译: %s' % (r[3], r[4]))
    print('\n=== 同源异译（前 %d）===' % min(args.top, len(incons)))
    for s, ts in incons[:args.top]:
        print('  KR: %s' % s[:70])
        for t in ts[:4]:
            print('      → %s' % t[:70])


if __name__ == '__main__':
    main()
