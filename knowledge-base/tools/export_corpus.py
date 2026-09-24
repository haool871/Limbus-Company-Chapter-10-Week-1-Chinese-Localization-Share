#!/usr/bin/env python3
"""Export lossless records; ambiguous IDs stay separate across languages."""
import collections
import json
import os
from pathlib import Path
import tempfile
import pm_lib as P
import localization_core as C

OUT=C.KB/'data/corpus.jsonl'


def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.corpus-',dir=OUT.parent)
    counts=collections.Counter(); n=0
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            for logical,entry in sorted(P.build_index().items()):
                for lang,rel in entry.items():
                    recs=P.load_file(lang,rel)
                    totals=collections.Counter(C.identity(r) for r in recs)
                    seen=collections.Counter()
                    for pos,rec in enumerate(recs):
                        ident=C.identity(rec); occurrence=seen[ident]; seen[ident]+=1
                        token=[*ident,occurrence]
                        ambiguous=totals[ident]>1 or ident[0]=='position'
                        if ambiguous: token += ['ambiguous',lang]
                        record=json.dumps(token,ensure_ascii=False)
                        for field,text in P.text_fields(rec).items():
                            row={'f':logical,'l':lang,'id':P.record_key(rec) or '',
                                 'record':record,'position':pos,'ambiguous':ambiguous,'k':field,'t':text}
                            stream.write(json.dumps(row,ensure_ascii=False)+'\n')
                            counts[lang]+=1; n+=1
            stream.flush(); os.fsync(stream.fileno())
        os.replace(name,OUT)
    finally:
        if os.path.exists(name): os.unlink(name)
    C.save(str(OUT)+'.meta.json',{'schema':2,'roots':P.LANG_DIR,'records':n,'languages':dict(counts),'sha256':C.file_hash(OUT)})
    print(f'导出 {n} 文本字段；{dict(counts)}；重复/空id未跨语言自动配对')


if __name__=='__main__': main()
