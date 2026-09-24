"""扫描 out/c_*.json 译稿，生成 out/apply_spec.json 供 apply_compacts.py 使用。

命名约定：`out/c_<批次内路径，/ 换成 __，去掉 .json>.json`
分块另加 `__<块名>`，例如 `c_RPGSystem__rpg-loc-dialogue-floor-4-b__c1.json`。
"""
from __future__ import annotations
import json
import re
from pathlib import Path

KB = Path(__file__).resolve().parent.parent


def main():
    proj = json.loads((KB / 'project.json').read_text(encoding='utf-8'))
    meta = json.loads((KB / proj['active_batch'] / 'batch.json').read_text(encoding='utf-8'))
    index = {}
    for rel in meta['files']:
        slug = rel[:-5] if rel.endswith('.json') else rel
        index[slug.replace('/', '__')] = rel
    spec = []
    unknown = []
    for p in sorted((KB / 'out').glob('c_*.json')):
        stem = p.stem[2:]
        if stem in index:
            spec.append({'file': index[stem], 'compact': 'out/' + p.name})
            continue
        m = re.match(r'^(.*)__[^_].*$', stem)
        hit = None
        while m:
            if m.group(1) in index:
                hit = index[m.group(1)]
                break
            m = re.match(r'^(.*)__[^_].*$', m.group(1))
        if hit:
            spec.append({'file': hit, 'compact': 'out/' + p.name})
        else:
            unknown.append(p.name)
    # 同一文件的多个分块按块名排序，保证写回顺序稳定
    spec.sort(key=lambda s: (s['file'], s['compact']))
    (KB / 'out' / 'apply_spec.json').write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding='utf-8')
    files = sorted({s['file'] for s in spec})
    print(json.dumps({'compacts': len(spec), 'files': len(files),
                      'unknown': unknown, 'spec': 'out/apply_spec.json'},
                     ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
