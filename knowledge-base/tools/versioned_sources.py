"""Immutable source snapshots and field-level update reports."""
from __future__ import annotations
import datetime
import json
from pathlib import Path
import re
import shutil
import tempfile
import localization_core as C


def now():
    return datetime.datetime.now().astimezone().isoformat()


def logical_files(root, lang=None):
    root = Path(root)
    if not root.is_dir():
        raise C.DataError(f'来源目录缺失: {root}')
    out = {}
    for p in sorted(root.rglob('*.json')):
        rel = p.relative_to(root)
        if rel.parts[0] in ('Info', 'Font'):
            continue
        name = rel.name
        prefix = (lang or '').upper() + '_'
        if lang and name.startswith(prefix):
            name = name[len(prefix):]
        logical = (rel.parent/name).as_posix()
        if logical in out:
            raise C.DataError(f'重复逻辑文件: {logical}')
        out[logical] = p
    return out


def capture(destination, game=C.GAME, base=None, game_version=None):
    destination = Path(destination).resolve()
    if destination.exists():
        raise C.DataError(f'快照已存在，禁止覆盖: {destination}')
    base = C.resolve_base(base)
    loc = Path(game)/'LimbusCompany_Data/Assets/Resources_moved/Localize'
    sources = {lang: logical_files(loc/lang, lang) for lang in C.LANGS}
    if not sources['kr'] and not sources['en']:
        raise C.DataError('KR/EN 都没有原文，拒绝创建空基线')
    sources['base'] = logical_files(base)
    if not sources['base']:
        raise C.DataError('零协包没有文本，拒绝创建空基线')
    manifest = {'schema': 1, 'created_at': now(), 'game_version': game_version,
                'steam_buildid': None, 'zeroasso_version': C.load(base/'Info/version.json')['version'],
                'origins': {'game': str(Path(game).resolve()), 'base': str(base)},
                'files': {}, 'languages': {}}
    for p in Path(game).parent.parent.glob('appmanifest_*.acf'):
        text = p.read_text(encoding='utf-8')
        match = re.search(r'"installdir"\s+"([^"]+)"', text)
        build = re.search(r'"buildid"\s+"([^"]+)"', text)
        if match and match[1] == Path(game).name and build:
            manifest['steam_buildid'] = build[1]
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='.snapshot-', dir=destination.parent))
    try:
        for lang, files in sources.items():
            table = manifest['languages'][lang] = {}
            for logical, source in files.items():
                raw = source.read_bytes()
                try:
                    C.records(json.loads(raw.decode('utf-8-sig')))
                except (ValueError, UnicodeError) as exc:
                    raise C.DataError(f'来源结构无效 {source}: {exc}') from exc
                rel = lang+'/'+logical
                dest = C.inside(temp, rel)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
                manifest['files'][rel] = {'sha256': C.digest(raw), 'bytes': len(raw)}
                table[logical] = rel
        C.save(temp/'manifest.json', manifest)
        for lang, files in sources.items():
            for logical, source in files.items():
                if C.file_hash(source) != manifest['files'][lang+'/'+logical]['sha256']:
                    raise C.DataError(f'创建快照期间源文件变化: {source}')
        temp.rename(destination)
    except BaseException:
        shutil.rmtree(temp, ignore_errors=True)
        raise
    return manifest


def snapshot(path):
    root = Path(path).resolve()
    manifest = C.load(root/'manifest.json')
    if manifest.get('schema') != 1 or not manifest.get('files'):
        raise C.DataError(f'无效或空快照: {root}')
    listed = set(manifest['files'])
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p != root/'manifest.json'}
    if actual != listed:
        raise C.DataError(f'快照文件集合发生变化: {root}')
    for rel, entry in manifest['files'].items():
        p = C.inside(root, rel)
        if p.stat().st_size != entry['bytes'] or C.file_hash(p) != entry['sha256']:
            raise C.DataError(f'快照校验失败: {p}')
    for lang, table in manifest['languages'].items():
        for logical, rel in table.items():
            if rel != lang+'/'+logical or rel not in listed:
                raise C.DataError('快照语言索引无效')
    return root, manifest


def read(root, manifest, lang, logical):
    rel = manifest['languages'].get(lang, {}).get(logical)
    return C.load(C.inside(root, rel)) if rel else {'dataList': []}


def preferred(manifest, logical, root):
    for lang in C.LANGS:
        if logical in manifest['languages'].get(lang, {}):
            if any(u['text'].strip() for u in C.units(read(root, manifest, lang, logical)).values()):
                return lang
    return None


def delta(old_obj, new_obj):
    old, new = C.units(old_obj), C.units(new_obj)
    rows = []
    for uid in sorted(old.keys() | new.keys()):
        a, b = old.get(uid), new.get(uid)
        kind = 'added' if a is None else 'deleted' if b is None else 'modified' if a['text'] != b['text'] else 'moved' if a['path'] != b['path'] else None
        if kind:
            rows.append({'kind': kind, 'old': a, 'new': b, 'ambiguous': bool((a and a['ambiguous']) or (b and b['ambiguous']))})
    return rows


def effective_units(root, manifest, logical, schema_language):
    """Keep target schema paths, but choose semantic source per uniquely aligned field."""
    if not schema_language:
        return {}
    maps = {lang:C.units(read(root,manifest,lang,logical)) for lang in C.LANGS}
    result = {}
    for uid, target in maps[schema_language].items():
        chosen, language = target, schema_language
        if not target['ambiguous']:
            for lang in C.LANGS:
                candidate = maps[lang].get(uid)
                if candidate and candidate['text'].strip() and not candidate['ambiguous']:
                    chosen, language = candidate, lang
                    break
        result[uid] = {**target, 'text':chosen['text'], 'source_language':language}
    return result


def plan(old_path, new_path):
    old_root, old = snapshot(old_path)
    new_root, new = snapshot(new_path)
    names = set()
    for m in (old, new):
        for lang in C.LANGS:
            names.update(m['languages'].get(lang, {}))
    result = {'schema': 1, 'created_at': now(), 'old_snapshot': str(old_root),
              'new_snapshot': str(new_root), 'old_manifest_sha256': C.file_hash(old_root/'manifest.json'),
              'new_manifest_sha256': C.file_hash(new_root/'manifest.json'),
              'files': [], 'history': [], 'language_differences': []}
    for logical in sorted(names):
        changes = {}
        for lang in C.LANGS:
            op = old['languages'].get(lang, {}).get(logical)
            np = new['languages'].get(lang, {}).get(logical)
            oh = old['files'][op]['sha256'] if op else None
            nh = new['files'][np]['sha256'] if np else None
            if oh == nh:
                continue
            a, b = read(old_root, old, lang, logical), read(new_root, new, lang, logical)
            changes[lang] = {'file_change': 'added' if not op else 'deleted' if not np else 'modified',
                             'structure_changed': C.structure(a) != C.structure(b), 'fields': delta(a,b)}
        lang = preferred(new, logical, new_root)
        su = effective_units(new_root,new,logical,lang)
        bu = C.units(read(new_root,new,'base',logical))
        obu = C.units(read(old_root,old,'base',logical))
        old_units = effective_units(old_root,old,logical,lang)
        status = []
        for uid, unit in su.items():
            upstream = bu.get(uid)
            available = upstream and upstream['text'].strip() and not upstream['ambiguous'] and not unit['ambiguous']
            changed = uid not in old_units or (unit['text'],unit['source_language']) != (old_units[uid]['text'],old_units[uid]['source_language'])
            if unit['ambiguous']:
                state = 'manual_alignment'
            elif changed:
                state = 'upstream_review' if available else 'needs_translation'
            elif available:
                state = 'inherited'
            else:
                state = 'historical_gap' if uid in old_units else 'needs_translation'
            row = {'uid': uid, 'path': unit['path'], 'source': unit['text'], 'status': state,
                   'source_language':unit['source_language'],
                   'upstream': upstream['text'] if upstream else None,
                   'upstream_changed': bool(upstream and (uid not in obu or upstream['text'] != obu[uid]['text']))}
            if state == 'historical_gap' and unit['text'].strip():
                result['history'].append({'file': logical, 'source_language': lang, **row})
            status.append(row)
        if changes:
            result['files'].append({'file': logical, 'source_language': lang, 'changes': changes, 'coverage': status})
        if lang:
            en = C.units(read(new_root,new,'en',logical))
            only_en = sorted(en.keys() - su.keys())
            if only_en:
                result['language_differences'].append({'file': logical, 'selected': lang, 'en_only_paths': [en[k]['path'] for k in only_en]})
    return result
