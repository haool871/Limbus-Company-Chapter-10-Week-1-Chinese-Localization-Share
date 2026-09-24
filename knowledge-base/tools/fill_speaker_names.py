"""用统一说话人译名表填写 texts[].speaker 显示名。

说话人字段在本批次里共 3,108 个、只有 84 个不同取值，属于机械但必须一致的字段。
译名来自 terms/speaker_map_ch10p2.tsv（零协实证 + 官方英文 + 新拟依据）。

用法：
  python3 tools/fill_speaker_names.py --dry-run
  python3 tools/fill_speaker_names.py --apply
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import localization_core as C  # noqa: E402

KB = Path(__file__).resolve().parent.parent
MAP = KB / 'terms' / 'speaker_map_ch10p2.tsv'


def load_map():
    mapping, evidence = {}, {}
    for line in MAP.read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            continue
        mapping[parts[0]] = parts[1]
        evidence[parts[0]] = parts[3] if len(parts) > 3 else '零协既有译名'
    return mapping, evidence


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--force', action='store_true', help='即使字段已填也按译名表更正')
    ap.add_argument('--out', default='out/edits_speakers.json')
    args = ap.parse_args()
    mapping, evidence = load_map()
    proj = json.loads((KB / 'project.json').read_text(encoding='utf-8'))
    root = KB / proj['active_batch']
    meta = json.loads((root / 'batch.json').read_text(encoding='utf-8'))
    edits, missing, already = [], set(), 0
    for rel, entry in meta['files'].items():
        needs = [r for r in entry['editable'] if r['path'][-1] == 'speaker']
        if not needs:
            continue
        obj = C.load(C.inside(root / 'patch', rel))
        for row in needs:
            src = row['source']
            if src not in mapping:
                missing.add(src)
                continue
            cur = C.get(obj, row['path'])
            if cur == mapping[src]:
                already += 1
                continue
            if cur != src and not args.force:
                already += 1
                continue
            edits.append({'file': rel, 'path': row['path'], 'expected': cur,
                          'text': mapping[src],
                          'reason': '说话人显示名统一映射：%s→%s（%s）' % (src, mapping[src], evidence[src]),
                          'semantic_review': True, 'style_review': True})
    Path(KB / args.out).write_text(json.dumps(edits, ensure_ascii=False, indent=1), encoding='utf-8')
    info = {'edits': len(edits), 'already_filled': already, 'unmapped': sorted(missing)}
    if missing:
        print(json.dumps(info, ensure_ascii=False, indent=1))
        raise SystemExit('有说话人未在译名表中，未写回')
    if args.apply:
        p = subprocess.run([sys.executable, 'tools/batch.py', 'apply', '--edits', args.out],
                           cwd=str(KB), capture_output=True, text=True)
        info['apply'] = (p.stdout + p.stderr).strip()
    elif args.dry_run:
        p = subprocess.run([sys.executable, 'tools/batch.py', 'apply', '--edits', args.out, '--dry-run'],
                           cwd=str(KB), capture_output=True, text=True)
        info['dry_run'] = (p.stdout + p.stderr).strip()
    print(json.dumps(info, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
