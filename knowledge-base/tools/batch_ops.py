"""Version-bound translation batches, complete validation and reversible edits."""
from __future__ import annotations
import contextlib
import copy
import fcntl
import json
from pathlib import Path
import shutil
import tempfile
import uuid
import localization_core as C
import versioned_sources as V


@contextlib.contextmanager
def lock(batch):
    with (Path(batch)/'.lock').open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def load_batch(batch, allow_closed=False):
    batch = Path(batch).resolve()
    meta = C.load(batch/'batch.json')
    if meta.get('schema') != 1 or (meta.get('status') != 'active' and not allow_closed):
        raise C.DataError('批次不处于可操作状态')
    for which in ('old', 'new'):
        root = Path(meta[which+'_snapshot'])
        if C.file_hash(root/'manifest.json') != meta[which+'_manifest_sha256']:
            raise C.DataError('批次绑定的源快照清单已改变')
        V.snapshot(root)
    for rel, entry in meta['files'].items():
        if C.file_hash(C.inside(batch/'template',rel)) != entry['template_sha256']:
            raise C.DataError(f'受保护模板被修改: {rel}')
    for p in (batch/'transactions').glob('*/transaction.json'):
        if C.load(p)['status'] == 'prepared':
            raise C.DataError(f'存在中断事务，先回滚: {p.parent.name}')
    return meta


def create(destination, report, decisions=None):
    decisions = decisions or {}
    destination = Path(destination).resolve()
    if destination.exists():
        raise C.DataError(f'批次已存在: {destination}')
    fresh = V.plan(report['old_snapshot'], report['new_snapshot'])
    for k in ('old_manifest_sha256','new_manifest_sha256','files','history','language_differences'):
        if fresh[k] != report[k]:
            raise C.DataError(f'范围报告已过期或被改动: {k}')
    if not fresh['files']:
        raise C.DataError('没有本次原文变化，不创建翻译批次')
    known = {x['file'] for x in fresh['files']}
    if set(decisions) - known:
        raise C.DataError('决策含范围报告之外的文件')
    nr, nm = V.snapshot(fresh['new_snapshot'])
    oroot, om = V.snapshot(fresh['old_snapshot'])
    meta = {k: fresh[k] for k in ('old_snapshot','new_snapshot','old_manifest_sha256','new_manifest_sha256')}
    meta.update({'schema':1,'status':'active','created_at':V.now(),'files':{},'decisions':decisions,'retired':[],'excluded':[]})
    generated = {}
    for item in fresh['files']:
        rel = item['file']; decision = decisions.get(rel, {})
        action = decision.get('action','translate')
        reason = decision.get('reason','').strip()
        if action not in ('translate','upstream','exclude','retire'):
            raise C.DataError(f'未知处理方式: {rel}: {action}')
        lang = decision.get('schema_language',item['source_language'])
        if lang not in C.LANGS and lang is not None:
            raise C.DataError(f'无效结构来源语言: {lang}')
        if action != 'translate' and not reason:
            raise C.DataError(f'非默认决策必须说明依据: {rel}')
        if action in ('exclude','retire'):
            if action == 'retire' and item['source_language'] is not None:
                raise C.DataError(f'文件仍有官方文本，不能标为删除: {rel}')
            meta['retired' if action == 'retire' else 'excluded'].append({'file':rel,'reason':reason})
            continue
        if lang is None:
            raise C.DataError(f'原文已删除，需明确 retire 或 exclude 决策: {rel}')
        source = V.read(nr,nm,lang,rel)
        previous = V.read(oroot,om,lang,rel)
        su = V.effective_units(nr,nm,rel,lang)
        pu = V.effective_units(oroot,om,rel,lang)
        bu = C.units(V.read(nr,nm,'base',rel))
        if not su:
            raise C.DataError(f'所选源语言无文本: {rel}')
        changed = {uid for uid,u in su.items() if uid not in pu or
                   (u['text'],u['source_language']) != (pu[uid]['text'],pu[uid]['source_language'])}
        structure_changed = C.structure(source) != C.structure(previous)
        if (structure_changed and pu) or not changed:
            if not (decision.get('structure_reviewed') and reason):
                raise C.DataError(f'结构/顺序/参考语言发生变化，需 structure_reviewed 和依据: {rel}')
        if any(u['ambiguous'] for u in su.values()) and not (decision.get('alignment_reviewed') and reason):
            raise C.DataError(f'重复或空定位键需 alignment_reviewed；按完整路径逐条处理: {rel}')
        template = copy.deepcopy(source)
        editable = []
        for uid, unit in su.items():
            if not unit['text'].strip():
                continue
            base = bu.get(uid)
            safe_base = bool(base and base['text'].strip() and not base['ambiguous'] and not unit['ambiguous'])
            if action == 'upstream':
                if not safe_base:
                    raise C.DataError(f'无法确认零协覆盖全部字段: {rel} {C.pointer(unit["path"])}')
                C.put(template,unit['path'],base['text'])
                if uid in changed:
                    if not (decision.get('semantic_reviewed') is True and decision.get('style_reviewed') is True):
                        raise C.DataError('采用新源对应的上游译文也须 semantic_reviewed / style_reviewed')
                    errors = C.text_errors(unit['text'], base['text'], decision.get('display_brackets',[]))
                    if errors:
                        raise C.DataError(f'上游候选标记不适配新源: {rel} {errors}')
                    editable.append({'path':unit['path'],'uid':uid,'source':unit['text'],
                        'source_language':unit['source_language'],'source_sha256':C.digest(unit['text'].encode()),
                        'upstream_candidate':base['text'],
                        'review':{'semantic':True,'style':True,'reason':reason,
                                  'text_sha256':C.digest(base['text'].encode()),'updated_at':V.now()}})
                continue
            # Reuse only unchanged, uniquely aligned source. New/changed source never
            # inherits a nonempty but potentially stale upstream value automatically.
            if uid not in changed and safe_base and not unit['ambiguous']:
                C.put(template,unit['path'],base['text'])
                continue
            if uid in pu and uid not in changed and not safe_base and not unit['ambiguous']:
                if not (decision.get('include_history') and reason):
                    raise C.DataError(f'同文件包含历史缺口，需 include_history 明确纳入: {rel} {C.pointer(unit["path"])}')
            C.put(template,unit['path'],unit['text'])
            editable.append({'path':unit['path'],'uid':uid,'source':unit['text'],
                             'source_language':unit['source_language'],'source_sha256':C.digest(unit['text'].encode()),
                             'upstream_candidate':base['text'] if safe_base else None,
                             'review':None})
        generated[rel] = template
        meta['files'][rel] = {'source_language':lang,'editable':editable,
                              'display_brackets':decision.get('display_brackets',[]),
                              'template_sha256':C.digest(C.json_bytes(template))}
        if meta['files'][rel]['display_brackets'] and not reason:
            raise C.DataError('显示方括号例外必须附解释和证据')
    destination.parent.mkdir(parents=True,exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='.batch-',dir=destination.parent))
    try:
        (temp/'patch').mkdir(); (temp/'template').mkdir(); (temp/'transactions').mkdir()
        for rel,obj in generated.items():
            C.save(C.inside(temp/'patch',rel),obj)
            C.save(C.inside(temp/'template',rel),obj)
        C.save(temp/'batch.json',meta); C.save(temp/'scope.json',fresh)
        temp.rename(destination)
    except BaseException:
        shutil.rmtree(temp,ignore_errors=True); raise
    return meta


def verify(batch, require_reviews=True):
    batch = Path(batch)
    meta = load_batch(batch)
    expected = set(meta['files'])
    actual = {p.relative_to(batch/'patch').as_posix() for p in (batch/'patch').rglob('*') if p.is_file()}
    errors = []
    if actual != expected:
        errors.append(f'批次文件集合不同：缺 {sorted(expected-actual)}；多 {sorted(actual-expected)}')
    checked = fields = 0
    for rel, entry in meta['files'].items():
        if rel not in actual:
            continue
        checked += 1
        template = C.load(C.inside(batch/'template',rel))
        obj = C.load(C.inside(batch/'patch',rel))
        allowed = {tuple(x['path']) for x in entry['editable']}
        errors.extend(f'{rel}: {e}' for e in C.compare_structure(template,obj,allowed))
        for row in entry['editable']:
            path = row['path']; label = rel+C.pointer(path)
            try:
                text = C.get(obj,path)
            except (KeyError,IndexError,TypeError):
                errors.append(label+': 目标字段不存在'); continue
            if not isinstance(text,str):
                errors.append(label+': 非文本'); continue
            fields += 1
            errors.extend(label+': '+e for e in C.text_errors(row['source'],text,entry['display_brackets']))
            if require_reviews:
                review = row.get('review') or {}
                if (review.get('text_sha256') != C.digest(text.encode()) or
                    not review.get('semantic') or not review.get('style') or not review.get('reason')):
                    errors.append(label+': 缺少与当前译文绑定的语义/文风审校记录')
    return {'files':checked,'editable_fields':fields,'errors':errors,
            'excluded':meta['excluded'],'retired':meta['retired']}


def transaction(batch, updates):
    """Full-byte backup before any mutation; recover partial writes with rollback."""
    batch = Path(batch)
    tid = uuid.uuid4().hex
    root = batch/'transactions'/tid
    root.mkdir(parents=True)
    journal = {'schema':1,'status':'prepared','created_at':V.now(),'files':{}}
    for rel, raw in updates.items():
        target = C.inside(batch,rel)
        old = target.read_bytes()
        backup = C.inside(root/'before',rel)
        C.atomic_bytes(backup,old)
        journal['files'][rel] = {'before':C.digest(old),'after':C.digest(raw)}
    C.save(root/'transaction.json',journal)
    try:
        for rel,raw in updates.items():
            target = C.inside(batch,rel)
            if C.file_hash(target) != journal['files'][rel]['before']:
                raise C.DataError(f'并发修改，事务中止: {rel}')
            C.atomic_bytes(target,raw)
        journal['status']='applied'; C.save(root/'transaction.json',journal)
    except BaseException:
        # Preserve an independently changed file; journal remains recoverable.
        for rel,hashes in journal['files'].items():
            target=C.inside(batch,rel)
            if C.file_hash(target) == hashes['after']:
                C.atomic_bytes(target,C.inside(root/'before',rel).read_bytes())
        raise
    return tid


def apply(batch, edits, dry_run=False):
    batch = Path(batch)
    if not isinstance(edits,list) or not edits:
        raise C.DataError('编辑清单必须是非空数组')
    with lock(batch):
        meta = load_batch(batch)
        objects = {}; seen=set()
        for edit in edits:
            rel = edit['file']; path=edit['path']; marker=(rel,tuple(path))
            if marker in seen:
                raise C.DataError('同一字段被多次编辑')
            seen.add(marker)
            entry = meta['files'].get(rel)
            if not entry:
                raise C.DataError(f'文件不在本批次: {rel}')
            row = next((x for x in entry['editable'] if x['path']==path),None)
            if row is None:
                raise C.DataError(f'字段不在允许修改范围: {rel} {path}')
            if rel not in objects:
                objects[rel] = C.load(C.inside(batch/'patch',rel))
            obj=objects[rel]
            if C.get(obj,path) != edit['expected']:
                raise C.DataError(f'旧值不匹配: {rel} {path}')
            text=edit['text']
            if not isinstance(text,str) or not edit.get('reason','').strip():
                raise C.DataError('译文必须是字符串，且需修改/审校依据')
            errors=C.text_errors(row['source'],text,entry['display_brackets'])
            if errors:
                raise C.DataError(f'{rel} {path}: {errors}')
            C.put(obj,path,text)
            row['review']={'semantic':edit.get('semantic_review') is True,
                           'style':edit.get('style_review') is True,'reason':edit['reason'],
                           'text_sha256':C.digest(text.encode()),'updated_at':V.now()}
        updates={'patch/'+rel:C.json_bytes(obj) for rel,obj in objects.items()}
        updates['batch.json']=C.json_bytes(meta)
        if dry_run:
            return {'fields':len(edits),'files':len(objects),'written':False}
        tid=transaction(batch,updates)
        return {'fields':len(edits),'files':len(objects),'written':True,'transaction':tid}


def rollback(batch, tid):
    batch=Path(batch)
    with lock(batch):
        if C.load(batch/'batch.json').get('status') != 'active':
            raise C.DataError('已归档批次不可回滚修改；保留历史证据')
        root=C.inside(batch/'transactions',tid)
        journal=C.load(root/'transaction.json')
        if journal['status']=='reverted':
            return {'transaction':tid,'status':'already_reverted'}
        for rel,hashes in journal['files'].items():
            before=C.inside(root/'before',rel)
            if C.file_hash(before)!=hashes['before']:
                raise C.DataError('回滚备份损坏')
            current=C.file_hash(C.inside(batch,rel))
            if current not in (hashes['before'],hashes['after']):
                raise C.DataError(f'文件已被后续修改；必须按逆序回滚: {rel}')
        for rel in journal['files']:
            C.atomic_bytes(C.inside(batch,rel),C.inside(root/'before',rel).read_bytes())
        journal['status']='reverted'; C.save(root/'transaction.json',journal)
        return {'transaction':tid,'status':'reverted','files':len(journal['files'])}
