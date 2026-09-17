#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用工具：按 (id, texts索引) → 译文 的映射，生成 *_parts 值文件。

用法:
  python3 tools/make_parts.py <骨架名> <映射.json>

映射.json 结构（键为 "id|index"）:
  {"T": {"D2002|0": "台词…"}, "S": {"D2002|0": "Heathcliff"}}
未提供的行自动写 @KEEP@。
"""
import json, os, re, sys

KB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def key2tuple(k):
    rid, i = k.rsplit('|', 1)
    return (rid, int(i))


def build(name, T, S=None):
    S = S or {}
    T = {key2tuple(k): v for k, v in T.items()}
    S = {key2tuple(k): v for k, v in S.items()}
    skel = os.path.join(KB, 'translate', '_skel', name + '.tsv')
    out, miss = [], 0
    for line in open(skel, encoding='utf-8'):
        if line.startswith('#') or not line.strip():
            continue
        rid, field, en = line.rstrip('\n').split('\t')
        m = re.match(r'texts\[(\d+)\]\.(text|speaker)$', field)
        if m:
            i = int(m.group(1))
            d = T if m.group(2) == 'text' else S
            if (rid, i) in d:
                out.append(d[(rid, i)])
                continue
        out.append('@KEEP@')
        miss += 1
        if en.strip():
            print(f"  未提供: {rid} {field} | {en[:70]}")
    p = os.path.join(KB, 'translate', '_parts', name + '.txt')
    open(p, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print(f"{name}: {len(out)} 行（未提供 {miss}）")


if __name__ == '__main__':
    name = sys.argv[1]
    spec = json.load(open(sys.argv[2], encoding='utf-8'))
    build(name, spec.get('T', {}), spec.get('S', {}))
