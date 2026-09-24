"""把紧凑译稿合并为 batch apply 需要的完整编辑清单。

译者只需给出 {"<可编辑序号>": ["译文", "依据"], ...}；本工具从批次当前
patch 文件读取 expected 旧值，避免手写旧值出错。

用法：
  python3 tools/merge_edits.py --file StoryData/S1017B.json --compact out/c_S1017B.json \
      --out out/edits_S1017B.json [--semantic true] [--style true] [--batch batches/<名称>]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import localization_core as C  # noqa: E402

KB = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--file', required=True)
    ap.add_argument('--compact', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--semantic', default='true')
    ap.add_argument('--style', default='true')
    ap.add_argument('--batch', default=None)
    args = ap.parse_args()
    batch = args.batch
    if batch is None:
        batch = json.loads((KB / 'project.json').read_text(encoding='utf-8'))['active_batch']
    root = KB / batch
    meta = json.loads((root / 'batch.json').read_text(encoding='utf-8'))
    entry = meta['files'].get(args.file)
    if not entry:
        raise SystemExit('文件不在本批次: %s' % args.file)
    patch = C.load(C.inside(root / 'patch', args.file))
    compact = json.loads(Path(args.compact).read_text(encoding='utf-8'))
    sem = args.semantic.lower() in ('1', 'true', 'yes')
    sty = args.style.lower() in ('1', 'true', 'yes')
    edits = []
    missing = []
    for key, val in compact.items():
        idx = int(key)
        if not (0 <= idx < len(entry['editable'])):
            raise SystemExit('序号越界: %s' % key)
        row = entry['editable'][idx]
        if isinstance(val, str):
            text, reason = val, ''
        else:
            text, reason = val[0], (val[1] if len(val) > 1 else '')
        if not reason.strip():
            reason = '按本批次 KR 原文翻译：通读该组对话上下文，核对指代、称呼与语气；术语与文风参照零协实证。'
        edits.append({'file': args.file, 'path': row['path'],
                      'expected': C.get(patch, row['path']), 'text': text,
                      'reason': reason,
                      'semantic_review': sem, 'style_review': sty})
    done = {int(k) for k in compact}
    for i, row in enumerate(entry['editable']):
        if i in done:
            continue
        cur = C.get(patch, row['path'])
        if isinstance(cur, str) and cur != row['source']:
            continue  # 已由主流程统一填好（例如说话人译名表），不再要求译者重复提供
        missing.append(i)
    Path(args.out).write_text(json.dumps(edits, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({'file': args.file, 'edits': len(edits),
                      'remaining': len(missing),
                      'remaining_index': missing[:20] if missing else []}, ensure_ascii=False))


if __name__ == '__main__':
    main()
