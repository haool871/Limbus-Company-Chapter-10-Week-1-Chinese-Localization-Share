"""按清单把各紧凑译稿合成编辑清单并写回批次。

清单 `out/apply_spec.json`：[{"file": "<批次内相对路径>", "compact": "out/c_xxx.json"}, ...]
同一文件可有多条（分块翻译），按清单顺序依次写回；每条都先 dry-run，
期望值由 merge_edits 从批次当前内容读取，因此先后顺序安全。

用法：
  python3 tools/apply_compacts.py --spec out/apply_spec.json            # 只做 dry-run 汇总
  python3 tools/apply_compacts.py --spec out/apply_spec.json --apply    # 实际写回
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

KB = Path(__file__).resolve().parent.parent
TOOLS = KB / 'tools'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def remaining_hangul(KB, root, rel, entry):
    sys.path.insert(0, str(KB / 'tools'))
    import localization_core as C
    HANGUL = re.compile(r'[\uac00-\ud7a3]')
    obj = C.load(C.inside(root / 'patch', rel))
    n = 0
    for row in entry['editable']:
        cur = C.get(obj, row['path'])
        if isinstance(cur, str) and cur == row['source'] and HANGUL.search(row['source']):
            n += 1
    return n


def run(cmd):
    p = subprocess.run([sys.executable] + cmd, cwd=str(KB), capture_output=True, text=True)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', default='out/apply_spec.json')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--only', default=None)
    ap.add_argument('--force', action='store_true', help='忽略已应用记录，强制重放')
    ap.add_argument('--seed', action='store_true',
                    help='把"对应文件已无待译韩文"的译稿登记为已应用（不再重放，避免旧稿回退新修）')
    args = ap.parse_args()
    spec = json.loads((KB / args.spec).read_text(encoding='utf-8'))
    state_path = KB / 'out' / 'applied_compacts.json'
    state = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {}
    proj0 = json.loads((KB / 'project.json').read_text(encoding='utf-8'))
    root0 = KB / proj0['active_batch']
    meta0 = json.loads((root0 / 'batch.json').read_text(encoding='utf-8'))
    if args.seed:
        added = 0
        for item in spec:
            rel, comp = item['file'], item['compact']
            if not (KB / comp).exists() or comp in state:
                continue
            if remaining_hangul(KB, root0, rel, meta0['files'][rel]) == 0:
                state[comp] = digest(KB / comp)
                added += 1
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf-8')
        print(json.dumps({'seeded': added, 'total_recorded': len(state)}, ensure_ascii=False))
        return
    if args.only:
        spec = [s for s in spec if s['file'].startswith(tuple(args.only.split(',')))]
    ok = fail = skipped = 0
    fields = 0
    problems = []
    for item in spec:
        rel, comp = item['file'], item['compact']
        if not (KB / comp).exists():
            problems.append('%s: 缺译稿 %s' % (rel, comp))
            fail += 1
            continue
        if not args.force and state.get(comp) == digest(KB / comp):
            skipped += 1
            continue
        slug = Path(comp).stem
        edits = 'out/edits_auto_%s.json' % slug
        rc, out = run(['tools/merge_edits.py', '--file', rel, '--compact', comp, '--out', edits])
        if rc != 0:
            problems.append('%s: merge 失败 %s' % (rel, out.strip()[:200]))
            fail += 1
            continue
        info = json.loads(out.strip().splitlines()[-1])
        rc, out = run(['tools/batch.py', 'apply', '--edits', edits, '--dry-run'])
        if rc != 0:
            problems.append('%s: dry-run 失败 %s' % (rel, out.strip()[:300]))
            fail += 1
            continue
        if args.apply:
            rc, out = run(['tools/batch.py', 'apply', '--edits', edits])
            if rc != 0:
                problems.append('%s: apply 失败 %s' % (rel, out.strip()[:300]))
                fail += 1
                continue
        ok += 1
        fields += info['edits']
        state[comp] = digest(KB / comp)
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf-8')
        if info['remaining']:
            problems.append('%s: 仍有 %d 个字段未覆盖（%s…）' % (rel, info['remaining'], info['remaining_index'][:8]))
    report = {'entries': len(spec), 'ok': ok, 'fail': fail, 'skipped': skipped, 'fields': fields,
              'applied': bool(args.apply), 'problems': problems}
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
