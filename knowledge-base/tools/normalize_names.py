"""统一新拟专名的写法（显式替换表，逐条经 batch.apply 校验）。

不同翻译单元对同一新专名可能给出不同写法（如 르네앙 → 虚无者／虚无派）。
本工具按显式表把已写回译文统一，替换后仍走 text_errors 校验，
标签/占位符被破坏会被拒绝而不是静默写入。

用法：
  python3 tools/normalize_names.py            # 只报告
  python3 tools/normalize_names.py --apply    # 写回
"""
from __future__ import annotations
import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import localization_core as C  # noqa: E402

KB = Path(__file__).resolve().parent.parent

# 本轮已裁决的写法：旧写法 -> (新写法, 依据)
REPLACEMENTS = [
    ('虚无者', '虚无派', '르네앙=Le Néant；与已确立的 르루주=红派、르누아르=黑派 同构，统一用「派」'),
    ('勒内', '蕾妮', '르네=Renée；官方英文一致用 she，采用女性化译名'),
    ('红色心脏碎片', '赤红心脏碎片', '零协对 붉은 一律作「赤红」（세례[적]→洗礼[赤红]、붉은 신→赤红之神）'),
    ('红色心脏', '赤红心脏', '同上，붉은=赤红'),
    ('赤红的心脏', '赤红心脏', '同上，统一不带「的」'),
    ('옷가죽', '衣皮', '옷+가죽；统一新拟名'),
    ('噗伊', '布伊', '뿌이=布伊（terms/speaker_map_ch10p2.tsv）'),
    ('扭扭', '蠕蠕', '꼬무리=蠕蠕（本轮 §5.1 裁决）'),
]

# 需要看原文才能定的称呼档位：零协实证 관리자님→经理(514)、관리자 나리→经理老爷(76)、관리자 양반→经理兄(67)
HONORIFIC = [
    ('经理老爷', '经理', '관리자님 零协主流作「经理」(514 处)；「经理老爷」专用于 관리자 나리'),
    ('执行经理', '经理', '관리자 零协主流作「经理」(1018 处)，统一档位'),
    ('经理兄', '经理', '经理兄专用于 관리자 양반'),
]

# 需按原文判定的词族统一：(原文标记, 旧写法, 新写法, 依据)
SOURCE_AWARE = [
    ('뒤엉킴', '缠结', '缠绕', '뒤엉킴=缠绕（§5.2）；「缠结」是 걸치다 句族的写法，不可混用'),
    ('통제자', '管理者', '监管者', '통제자=监管者（§5，与 관리자=经理 区分）'),
    ('무두질', '鞣制', '鞣革', '무두질=鞣革（§5.2，与 테너=鞣皮工、태닝실=鞣革室 同族）'),
    ('무두질', '制革', '鞣革', '同上'),
    ('태너리', '制革', '鞣革', '태너리=鞣革（§5.2）'),
    ('따갑게 내리쬐는 햇살', '灼热照射的阳光', '刺眼地洒落的阳光', '§5.2 统一'),
    ('퍼니싱 버니싱 피니싱', '抛光惩戒终饰', '抛光惩罚终结', '§5.2 统一'),
    ('쉬르필', '锁边连锁', '锁边缝', '쉬르필 아 라 셴=锁边缝（§5.2）'),
    ('흙에서 태어난 자', '泥土中诞生的存在', '自土中诞生者', '§5.2 统一'),
    ('흙에서 태어난 자', '泥土中诞生者', '自土中诞生者', '同上'),
    ('재단', '裁定', '裁断', '재단=裁断（§5.2，与 수선=改衣 成对）'),
    ('뿌이', '普伊', '布伊', '뿌이=布伊（speaker_map 权威条目）'),
    ('비휘발성 보호막', '不挥发护盾', '非挥发性护盾', '§5.2 统一'),
    ('균열', '龟裂', '裂痕', '균열 零协实证：裂痕 41 处 vs 龟裂 10 处'),
    ('보유한 인격', '持有', '拥有', '零协实证「拥有…基础攻击技能的人格」'),
    ('인격', '持有赋予', '拥有赋予', '同上'),
    ('양극성', '双极性', '两极性', 'Duality；中文标准作「两极性」'),
    ('두 가위', '双剪刀', '双剪', '同族 꽃가위=花剪，取短名'),
    ('오려내기', '剪样', '剪取', '避开既有 裁剪(절삭)/裁断(재단)'),
    ('사제', '黑派祭司', '黑派司祭', '사제 零协无先例；与已定 부제=副祭 同属天主教用字'),
    ('사제', '黑派副祭', '黑派司祭', '副祭 对应 부제，사제 不应译副祭'),
    ('사나워진', '凶暴化的', '凶暴的', '零协链式前缀不加「化」（如 折射的+原名）'),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    proj = json.loads((KB / 'project.json').read_text(encoding='utf-8'))
    root = KB / proj['active_batch']
    meta = json.loads((root / 'batch.json').read_text(encoding='utf-8'))
    edits = []
    for rel, entry in meta['files'].items():
        obj = C.load(C.inside(root / 'patch', rel))
        for row in entry['editable']:
            try:
                cur = C.get(obj, row['path'])
            except Exception:
                continue
            if not isinstance(cur, str):
                continue
            new = cur
            hits = []
            for old, rep, why in REPLACEMENTS:
                if old in new:
                    new = new.replace(old, rep)
                    hits.append('%s→%s' % (old, rep))
            # 称呼档位：仅当原文不是 나리/양반 时才把敬称降为「经理」
            if '나리' not in row['source'] and '양반' not in row['source']:
                for old, rep, why in HONORIFIC:
                    if old in new:
                        new = new.replace(old, rep)
                        hits.append('%s→%s' % (old, rep))
            # 词族统一：只在原文命中标记时替换，避免误伤同形词
            for marker, old, rep, why in SOURCE_AWARE:
                if marker in row['source'] and old in new and rep not in new:
                    new = new.replace(old, rep)
                    hits.append('%s→%s(%s)' % (old, rep, marker))
            if new != cur:
                edits.append({'file': rel, 'path': row['path'], 'expected': cur, 'text': new,
                              'reason': '专名写法统一：' + '；'.join(hits) + '。依据见 terms/speaker_map_ch10p2.tsv 与本轮裁决',
                              'semantic_review': True, 'style_review': True})
    Path(KB / 'out' / 'edits_normalize.json').write_text(json.dumps(edits, ensure_ascii=False, indent=1), encoding='utf-8')
    counts = collections.Counter(e['reason'] for e in edits)
    print(json.dumps({'edits': len(edits), 'apply': bool(args.apply)}, ensure_ascii=False))
    for r, n in counts.most_common():
        print('  %3d  %s' % (n, r[:110]))
    if edits and args.apply:
        import subprocess
        p = subprocess.run([sys.executable, 'tools/batch.py', 'apply', '--edits', 'out/edits_normalize.json'],
                           cwd=str(KB), capture_output=True, text=True)
        print((p.stdout + p.stderr).strip()[:500])


if __name__ == '__main__':
    main()
