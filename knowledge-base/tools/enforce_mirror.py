"""镜像文件一致性：同一组文件里"同路径 + 同源文"的字段必须同译。

`Bufs*.json` 与 `BattleKeywords*.json` 是同一批状态条目（本批次 1,609 处韩文逐字相同），
两个翻译单元并行各译一份就会分裂。本工具按显式镜像组检查并统一到指定的一侧。

用法：
  python3 tools/enforce_mirror.py                 # 只报告
  python3 tools/enforce_mirror.py --apply        # 统一到 --prefer 指定的一侧
  python3 tools/enforce_mirror.py --prefer left  # 默认统一到右侧
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

MIRRORS = [
    ('Bufs.json', 'BattleKeywords.json'),
    ('Bufs-a1c10p2.json', 'BattleKeywords-a1c10p2.json'),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--prefer', choices=['left', 'right'], default='right')
    ap.add_argument('--out', default='out/edits_mirror.json')
    args = ap.parse_args()
    proj = json.loads((KB / 'project.json').read_text(encoding='utf-8'))
    root = KB / proj['active_batch']
    meta = json.loads((root / 'batch.json').read_text(encoding='utf-8'))
    edits, conflicts, same = [], [], 0
    for left, right in MIRRORS:
        if left not in meta['files'] or right not in meta['files']:
            continue
        lo = C.load(C.inside(root / 'patch', left))
        ro = C.load(C.inside(root / 'patch', right))

        def keyed(obj, rows):
            """按「记录 id/key + 记录内字段路径」配对：镜像文件里同一条目的 dataList 下标可能不同。"""
            dl = obj.get('dataList') if isinstance(obj, dict) else None
            out = {}
            for r in rows:
                p = list(r['path'])
                if len(p) >= 2 and p[0] == 'dataList' and isinstance(p[1], int) and isinstance(dl, list) and p[1] < len(dl):
                    rec = dl[p[1]]
                    rid = None
                    if isinstance(rec, dict):
                        rid = rec.get('id', rec.get('key'))
                        if isinstance(rid, dict):
                            rid = rid.get('id')
                    if not isinstance(rid, (str, int, float, type(None))):
                        rid = None
                    # 只用「记录 id + 记录内路径」，不含 dataList 下标——两份文件的条目下标不同
                    out[(rid, tuple(p[2:]))] = r
                else:
                    out[(None, tuple(p))] = r
            return out

        lmap, rmap = keyed(lo, meta['files'][left]['editable']), keyed(ro, meta['files'][right]['editable'])
        for k, lrow in lmap.items():
            rrow = rmap.get(k)
            if not rrow or lrow['source'] != rrow['source']:
                continue
            try:
                lt, rt = C.get(lo, list(lrow['path'])), C.get(ro, list(rrow['path']))
            except Exception:
                continue
            if not isinstance(lt, str) or not isinstance(rt, str):
                continue
            if lt == rt:
                same += 1
                continue
            keep, fix, fixpath, fixfile = ((lt, rt, list(rrow['path']), right) if args.prefer == 'left'
                                           else (rt, lt, list(lrow['path']), left))
            conflicts.append((fixfile, C.pointer(fixpath), fix, keep))
            edits.append({'file': fixfile, 'path': fixpath, 'expected': fix, 'text': keep,
                          'reason': '镜像文件一致性：%s 与 %s 中同一条目（%s）源文逐字相同，两处必须同译；'
                                    '此处统一为%s的写法' % (left, right, lrow['source'][:30],
                                                     '左侧' if args.prefer == 'left' else '右侧'),
                          'semantic_review': True, 'style_review': True})
    Path(KB / args.out).write_text(json.dumps(edits, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({'identical': same, 'conflicts': len(conflicts), 'edits': len(edits),
                      'prefer': args.prefer}, ensure_ascii=False, indent=1))
    for f, p, a, b in conflicts:
        print('  冲突 %s %s\n     现: %s\n     统一为: %s' % (f, p, a[:70], b[:70]))
    if edits and args.apply:
        proc = subprocess.run([sys.executable, 'tools/batch.py', 'apply', '--edits', args.out],
                              cwd=str(KB), capture_output=True, text=True)
        print((proc.stdout + proc.stderr).strip()[:400])


if __name__ == '__main__':
    main()
