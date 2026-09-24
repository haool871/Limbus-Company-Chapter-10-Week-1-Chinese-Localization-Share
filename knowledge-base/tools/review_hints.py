"""Optional human-review hints over exact fields in a version-bound batch."""
import argparse
import collections
import csv
import json
import re
from pathlib import Path
import sys
import localization_core as C
import batch_ops as B
import versioned_sources as V


def main(mode):
    ap=argparse.ArgumentParser(description='仅提供人工复核线索，不判断语义通过，不自动修改译文')
    ap.add_argument('--batch'); ap.add_argument('--only'); ap.add_argument('--top',type=int,default=40)
    ap.add_argument('--save',metavar='REPORT_JSON')
    args=ap.parse_args()
    batch=C.active_batch(args.batch); meta=B.load_batch(batch)
    nr,nm=V.snapshot(meta['new_snapshot'])
    rows=[]; scanned=0
    terms=[]
    if mode=='terms':
        with (C.KB/'terms/confirmed_pairs.tsv').open(encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'): continue
                parts=line.rstrip('\n').split('\t')
                if len(parts)>=2 and parts[0] and parts[1]: terms.append(parts[:2])
    for rel,entry in meta['files'].items():
        if args.only and not rel.startswith(args.only): continue
        obj=C.load(C.inside(batch/'patch',rel))
        en=C.units(V.read(nr,nm,'en',rel)) if mode=='terms' else {}
        for field in entry['editable']:
            text=C.get(obj,field['path']); source=field['source']; why=[]; scanned+=1
            if mode=='semantic':
                if collections.Counter(re.findall(r'\d+',source))!=collections.Counter(re.findall(r'\d+',text)):
                    why.append('数字不同（含标记数字，可能误报）')
                if source.count('\n')>text.count('\n'): why.append('译文行数较少')
                if re.search(r'않|없|못|아니',source) and not re.search(r'不|没|无|未|非|别',text): why.append('核对否定')
            elif mode=='polish':
                for rx,label in [(r'的[^，。！？]{1,10}的[^，。！？]{1,10}的','核对多层“的”'),(r'\.\.\.\.\.\.|……。|「|」','核对标点'),(r'——','核对破折号是否必要')]:
                    if re.search(rx,text): why.append(label)
            elif mode=='terms':
                reference=en.get(field['uid'])
                if reference and not reference['ambiguous']:
                    for english,chinese in terms:
                        if re.search(r'(?<!\w)'+re.escape(english)+r'(?!\w)',reference['text'],re.I) and chinese not in text:
                            why.append(f'术语线索 {english} → {chinese}；须按语境核实')
            if why: rows.append({'file':rel,'path':field['path'],'source_language':field['source_language'],'source':source,'translation':text,'hints':why})
    report={'mode':mode,'scanned_fields':scanned,'hints':rows,'conclusion':'仅线索；零命中不代表语义正确'}
    print(f'扫描本批次可编辑字段 {scanned}；疑点 {len(rows)}。零命中不代表通过。')
    for row in rows[:args.top]: print(json.dumps(row,ensure_ascii=False))
    if args.save: C.save(args.save,report)
    return 0


def entry(mode):
    try: sys.exit(main(mode))
    except (C.DataError,OSError,KeyError,TypeError) as exc:
        print(f'未执行：{exc}',file=sys.stderr); sys.exit(2)
