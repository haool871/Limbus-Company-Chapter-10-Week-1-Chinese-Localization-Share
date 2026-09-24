"""Shared, lossless JSON addressing and project paths for versioned localization."""
from __future__ import annotations

import collections
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

KB = Path(os.environ.get('LIMBUS_KB_ROOT', Path(__file__).resolve().parent.parent)).resolve()
WS = Path(os.environ.get('LIMBUS_WORKSPACE', KB.parent)).resolve()
GAME = Path(os.environ.get('LIMBUS_GAME_ROOT', Path.home()/'.local/share/Steam/steamapps/common/Limbus Company'))
LANGS = ('kr', 'en', 'jp')
STRUCTURAL = {'id', 'Id', 'ID', 'key', 'index', 'model', 'speaker', 'icon', 'sprite',
              'type', 'level', 'count', 'scene', 'code', 'category'}
TAG = re.compile(r'<(/?)([A-Za-z][A-Za-z0-9-]*)(?:=[^>]*|\s+[A-Za-z][A-Za-z0-9_-]*\s*=[^>]*)?/?>')
VOID_TAGS = {'sprite', 'br', 'space', 'page', 'pos', 'alpha'}
BRACKET = re.compile(r'\[([A-Za-z_][A-Za-z0-9_]*)\]')
PLACEHOLDER = re.compile(r'\{[^{}\n]*\}')


class DataError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return digest(Path(path).read_bytes())


def json_bytes(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as exc:
        raise DataError(f'无法读取 JSON {path}: {exc}') from exc


def atomic_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def save(path, obj):
    atomic_bytes(path, json_bytes(obj))


def inside(root, rel):
    root = Path(root).resolve()
    path = (root / rel).resolve()
    if path == root or root not in path.parents:
        raise DataError(f'路径越界: {rel}')
    return path


def resolve_base(value=None):
    value = value or os.environ.get('LIMBUS_BASE_PACK')
    if value:
        root = Path(value).expanduser()
        if not root.is_absolute():
            root = WS / root
        candidates = [root, root/'LimbusCompany_Data/Lang/LLC_zh-CN']
        for candidate in candidates:
            if (candidate/'Info/version.json').is_file():
                load(candidate/'Info/version.json')
                return candidate.resolve()
        raise DataError(f'零协目录无有效 Info/version.json: {root}')
    packs = []
    for root in WS.glob('LimbusLocalize_latest*'):
        candidate = root/'LimbusCompany_Data/Lang/LLC_zh-CN'
        if (candidate/'Info/version.json').is_file():
            version = load(candidate/'Info/version.json').get('version')
            if not isinstance(version, int):
                raise DataError(f'零协版本号无效: {candidate}')
            packs.append((version, str(candidate)))
    if not packs:
        raise DataError('找不到零协包；请用 --base 指定包根目录或 LLC_zh-CN 目录')
    return Path(max(packs)[1]).resolve()


def state():
    p = KB/'project.json'
    return load(p) if p.exists() else {'schema': 1, 'phase': 'waiting', 'baseline': None, 'active_batch': None}


def active_batch(explicit=None, required=True):
    selected = explicit or state().get('active_batch')
    if not selected:
        if required:
            raise DataError('当前等待更新，无活动批次；此检查不适用，未执行验收')
        return None
    p = Path(selected)
    if not p.is_absolute():
        p = KB/p
    if not (p/'batch.json').is_file():
        raise DataError(f'批次不存在: {p}')
    return p.resolve()


def patch_root(explicit=None):
    if explicit:
        p = Path(explicit).resolve()
        if not p.is_dir():
            raise DataError(f'译文目录不存在: {p}')
        return p
    return active_batch()/'patch'


def records(obj):
    if isinstance(obj, dict) and not obj:
        return []
    if not isinstance(obj, dict) or not isinstance(obj.get('dataList'), list):
        raise DataError('预期对象包含 dataList 数组（或空占位对象）')
    if any(not isinstance(r, dict) for r in obj['dataList']):
        raise DataError('dataList 含非对象记录，需明确结构适配')
    return obj['dataList']


def identity(rec):
    for key in ('id', 'key', 'Id', 'ID'):
        if rec.get(key) is not None:
            value = rec[key]
            if not isinstance(value, (str, int)) or isinstance(value, bool):
                raise DataError(f'不支持的记录定位类型: {key}={value!r}')
            return (key, type(value).__name__, value)
    return ('position', 'null', None)


def structural_key(key, parent_path):
    # Verified RPG schema: texts[].speaker is a displayed name (KR 단테 / CN 但丁).
    # A top-level speaker identifier, and model/key/index everywhere, stay structural.
    if key == 'speaker' and len(parent_path) >= 2 and parent_path[-2] == 'texts' and isinstance(parent_path[-1], int):
        return False
    return key in STRUCTURAL


def text_leaves(obj, path=(), logical=(), ambiguous=False):
    """Yield physical and semantic paths. Duplicate list identities retain occurrence."""
    if isinstance(obj, str):
        yield path, logical, obj, ambiguous
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if not structural_key(key, path):
                yield from text_leaves(value, path+(key,), logical+(key,), ambiguous)
    elif isinstance(obj, list):
        counts = collections.Counter()
        identities = []
        for i, value in enumerate(obj):
            if isinstance(value, dict) and value.get('index') is not None:
                if type(value['index']) not in (str, int):
                    raise DataError('嵌套 index 类型必须为字符串或整数')
                token = ('index', type(value['index']).__name__, value['index'])
            else:
                token = ('position', 'int', i)
            identities.append(token)
        totals = collections.Counter(identities)
        for i, (value, token) in enumerate(zip(obj, identities)):
            occurrence = counts[token]; counts[token] += 1
            segment = json.dumps([*token, occurrence], ensure_ascii=False)
            yield from text_leaves(value, path+(i,), logical+(segment,), ambiguous or totals[token] > 1)


def units(obj):
    rows = records(obj)
    tokens = [identity(r) for r in rows]
    totals = collections.Counter(tokens)
    counts = collections.Counter()
    out = {}
    for pos, (rec, token) in enumerate(zip(rows, tokens)):
        occurrence = counts[token]; counts[token] += 1
        record_id = [*token, occurrence]
        ambiguous = token[0] == 'position' or totals[token] > 1
        for path, logical, text, nested_ambiguous in text_leaves(rec, ambiguous=ambiguous):
            uid = json.dumps([record_id, logical], ensure_ascii=False, separators=(',', ':'))
            out[uid] = {'uid': uid, 'record': record_id, 'position': pos,
                        'path': ['dataList', pos, *path], 'field': list(path),
                        'text': text, 'ambiguous': nested_ambiguous}
    return out


def get(obj, path):
    for part in path:
        obj = obj[part]
    return obj


def put(obj, path, value):
    target = obj
    for part in path[:-1]:
        target = target[part]
    if type(target[path[-1]]) is not type(value):
        raise DataError(f'不允许改变字段类型: {path}')
    target[path[-1]] = value


def pointer(path):
    return '/' + '/'.join(str(x).replace('~', '~0').replace('/', '~1') for x in path)


def structure(obj, path=()):
    if isinstance(obj, str):
        return '<text>'
    if isinstance(obj, list):
        return [structure(x, path+(i,)) for i,x in enumerate(obj)]
    if isinstance(obj, dict):
        return {k: v if structural_key(k,path) else structure(v,path+(k,)) for k,v in obj.items()}
    return obj


def text_errors(source, target, display_brackets=()):
    errors = []
    if source.strip() and not target.strip():
        errors.append('空译')
    if collections.Counter(PLACEHOLDER.findall(source)) != collections.Counter(PLACEHOLDER.findall(target)):
        errors.append('占位符不同')
    def engine(s):
        return collections.Counter(t for t in BRACKET.findall(s) if t not in display_brackets)
    if engine(source) != engine(target):
        errors.append('引擎方括号标记不同（显示文本例外须显式声明）')
    stags = [m.group() for m in TAG.finditer(source)]
    ttags = [m.group() for m in TAG.finditer(target)]
    if stags != ttags:
        errors.append('富文本标签序列不同')
    bare_source = TAG.sub('', source).strip()
    bare_target = TAG.sub('', target).strip()
    if bare_source.startswith('<') and bare_source.endswith('>'):
        if not (bare_target.startswith('<') and bare_target.endswith('>')):
            errors.append('但丁/引擎正文尖括号包裹丢失')
    stack = []
    for m in TAG.finditer(target):
        closing, name = m.group(1), m.group(2).lower()
        if m.group().endswith('/>') or name in VOID_TAGS:
            continue
        if closing:
            if not stack or stack.pop() != name:
                errors.append('富文本标签嵌套无效')
                break
        else:
            stack.append(name)
    if stack:
        errors.append('富文本标签未闭合')
    return errors


def compare_structure(expected, actual, editable=(), path=()):
    """Every non-editable value must match, not just intersecting string fields."""
    errors = []
    if type(expected) is not type(actual):
        return [pointer(path)+': 类型不同']
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            errors.append(pointer(path)+': 字段集合不同')
        for key in expected.keys() & actual.keys():
            errors.extend(compare_structure(expected[key], actual[key], editable, path+(key,)))
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            errors.append(pointer(path)+': 数组长度不同')
        for i, (a,b) in enumerate(zip(expected, actual)):
            errors.extend(compare_structure(a,b,editable,path+(i,)))
    elif path not in editable and expected != actual:
        errors.append(pointer(path)+': 受保护字段被修改')
    return errors
