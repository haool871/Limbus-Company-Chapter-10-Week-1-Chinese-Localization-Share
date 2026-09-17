#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""基于「官方对齐语料」的机制文本翻译器。

数据来源：`data/_mech_pairs.json` —— 从官方英/中四语对齐语料里逐行挖出的
25,813 组「英文原子句 → 官方中文」对照（由 mine_pairs 逻辑生成）。

翻译顺序：
  1. 整句精确命中对照表 → 直接采用官方译文；
  2. 未命中则按**从官方对照归纳出的参数化模板**替换（长模板优先）；
  3. 引擎标签 `[X]`、`<style=...>`、数字与百分号原样保留；
  4. 仍无法处理的部分保留英文，交给人工复核（调用方会打印待复核清单）。

该模块只做可验证的机械转换，不做自由创作。
"""
from __future__ import annotations

import json
import os
import re

_KB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PAIRS_PATH = os.path.join(_KB_DIR, "data", "_mech_pairs.json")

_EXACT: dict[str, str] = {}
try:
    with open(_PAIRS_PATH, encoding="utf-8") as _fh:
        for _a, _b, _n in json.load(_fh):
            # 保留出现次数多、且英文更长的对照（更具体）
            if _a not in _EXACT or len(_a) > 0:
                _EXACT.setdefault(_a, _b)
except Exception:
    pass

# 参数化模板（全部由官方对照归纳）
TEMPLATES: list[tuple[re.Pattern, str]] = [
    # 状态赋予：Inflict = 对目标 / Gain = 使自身
    (re.compile(r"^(.*?)\[OnSucceedAttack\] Inflict \+(\d+) (\[\w+\]) Count$"),
     r"\1[OnSucceedAttack] 对目标施加\2层\3"),
    (re.compile(r"^(.*?)\[OnSucceedAttack\] Inflict (\d+) (\[?\w+\]?) Count$"),
     r"\1[OnSucceedAttack] 对目标施加\2层\3"),
    (re.compile(r"^(.*?)\[OnSucceedAttack\] Inflict \+(\d+) (\[\w+\])$"),
     r"\1[OnSucceedAttack] 对目标施加\2层\3"),
    (re.compile(r"^(.*?)\[OnSucceedAttack\] Inflict (\d+) (\[?\w+\]?)$"),
     r"\1[OnSucceedAttack] 使目标增加\2级\3强度"),
    (re.compile(r"^(.*?)\[OnSucceedAttack\] Gain \+(\d+) (\[\w+\]) Count$"),
     r"\1[OnSucceedAttack] 获得+\2层\3"),
    (re.compile(r"^(.*?)\[OnSucceedAttack\] Gain (\d+) (\[\w+\]) Count$"),
     r"\1[OnSucceedAttack] 获得\2层\3"),
    (re.compile(r"^(.*?)\[(\w+)\] Gain \+(\d+) (\[\w+\]) Count$"),
     r"\1[\2] 使自身获得\3层\4"),
    (re.compile(r"^(.*?)\[(\w+)\] Gain (\d+) (\[\w+\]) Count$"),
     r"\1[\2] 使自身获得\3层\4"),
    (re.compile(r"^(.*?)\[(\w+)\] Gain \+(\d+) (\[\w+\])$"),
     r"\1[\2] 使自身获得\3层\4"),
    (re.compile(r"^(.*?)\[(\w+)\] Gain (\d+) (\[\w+\])$"),
     r"\1[\2] 使自身增加\3级\4强度"),
    # 触发
    (re.compile(r"^(.*?)Trigger (\[\w+\]); then, reduce target's (\[\w+\]) Count by (\d+)(.*)$"),
     r"\1使目标\2，并使其\3层数减少\4层\5"),
    # 伤害
    (re.compile(r"^Deal \+\(([^()]+)\)% damage \(max ([\d.]+)%\)$"),
     r"造成的伤害+(\1)%(最多\2%)"),
    (re.compile(r"^Deal \+([\d.]+)% damage$"), r"造成的伤害+\1%"),
    (re.compile(r"^deal \+([\d.]+)% damage$"), r"造成的伤害+\1%"),
    (re.compile(r"^Deal \+\(([^()]+)\)% damage$"), r"造成的伤害+(\1)%"),
    # 条件（时间前缀）
    (re.compile(r"^(.*?)At fewer than (\d+) (\[\w+\]) Count(.*)$"),
     r"\1若\3层数低于\2\4"),
    (re.compile(r"^(.*?)At (\d+)\+ (\[\w+\]) Potency(.*)$"),
     r"\1若\3强度不低于\2\4"),
    (re.compile(r"^(.*?)At (\d+)\+ (\[\w+\]) Count(.*)$"),
     r"\1若\3层数不低于\2\4"),
    (re.compile(r"^(.*?)At (\d+)\+ (\[\w+\])(.*)$"), r"\1若\3不低于\2\4"),
    (re.compile(r"^(.*?)At fewer than ([\d.]+)% HP(.*)$"),
     r"\1若现存体力低于\2%\3"),
    (re.compile(r"^(.*?)At ([\d.]+)%\+ HP(.*)$"), r"\1若现存体力不低于\2%\3"),
    (re.compile(r"^(.*?)At ([\d.]+)% or lower HP(.*)$"),
     r"\1若现存体力不高于\2%\3"),
    # 消耗
    (re.compile(r"^(.*?)Consume up to (\d+) (\[\w+\])(.*)$"),
     r"\1最多消耗\2层\3\4"),
    (re.compile(r"^(.*?)consume up to (\d+) (\[\w+\])(.*)$"),
     r"\1最多消耗\2层\3\4"),
    (re.compile(r"^(.*?)Consume (\d+) (\[\w+\])(.*)$"), r"\1消耗\2层\3\4"),
    (re.compile(r"^(.*?)consume (\d+) (\[\w+\])(.*)$"), r"\1消耗\2层\3\4"),
    # 护盾/体力
    (re.compile(r"^(.*?)[Gg]ain Shield equal to ([^()\n]+?) of this unit's max HP(.*)$"),
     r"\1获得等同于自身最大体力\2的护盾\3"),
    (re.compile(r"^(.*?)Heal ([^(),\n]+?)% HP(.*)$"), r"\1恢复\2%的体力\3"),
    (re.compile(r"^(.*?)heal ([^(),\n]+?)% HP(.*)$"), r"\1恢复\2%的体力\3"),
    (re.compile(r"^(.*?)consume ([^()\n]+?)% HP on self(.*)$"),
     r"\1消耗自身\2%的体力\3"),
    # 每 N 层
    (re.compile(r"^(.*?)for every (\d+) (\[\w+\])(.*)$"), r"\1每带有\2层\3\4"),
    (re.compile(r"^(.*?)for every (\[\w+\])(.*)$"), r"\1每带有1层\2\3"),
    (re.compile(r"^(.*?)for every (\d+) (\[\w+\]) on target(.*)$"),
     r"\1目标每带有\2层\3\4"),
    # 自持/目标持有
    (re.compile(r"^(.*?)this unit has (\[\w+\])(.*)$"), r"\1自身带有\2\3"),
    (re.compile(r"^(.*?)this unit does not have (\[\w+\])(.*)$"),
     r"\1自身不带有\2\3"),
    (re.compile(r"^(.*?)target has (\d+)\+ (\[\w+\])(.*)$"),
     r"\1目标带有不低于\2层\3\4"),
    (re.compile(r"^(.*?)target's (\[\w+\]) Count by (\d+)(.*)$"),
     r"\1目标的\2层数减少\3层\4"),
    # 时间/次数
    (re.compile(r"next turn"), "下回合"),
    (re.compile(r"this turn"), "本回合"),
    (re.compile(r"once per turn"), "每回合最多1次"),
    (re.compile(r"once per Skill"), "每技能最多1次"),
    (re.compile(r"once per Encounter"), "每场战斗最多1次"),
    (re.compile(r"\((\d+) times per turn\)"), r"(每回合最多\1次)"),
    (re.compile(r"\((\d+) times per Encounter\)"), r"(每场战斗最多\1次)"),
    (re.compile(r"^Turn Start:"), "回合开始时："),
    (re.compile(r"^Turn End:"), "回合结束时："),
    # 单个词
    (re.compile(r"\bPotency\b"), "强度"),
    (re.compile(r"\bCount\b"), "层数"),
    (re.compile(r"\bStack\b"), "层数"),
    (re.compile(r"\bdamage\b"), "伤害"),
    (re.compile(r"\btarget\b"), "目标"),
    (re.compile(r"\bmax\b"), "最多"),
    (re.compile(r"\band\b"), "并"),
    (re.compile(r"\bIf\b"), "若"),
    (re.compile(r"\bif\b"), "若"),
    # ── 通用补充（不限行首，处理复合条件句）──
    (re.compile(r"Inflict \+(\d+) (\[\w+\]) Count"), r"对目标施加\1层\2"),
    (re.compile(r"Inflict (\d+) (\[\w+\]) Count"), r"对目标施加\1层\2"),
    (re.compile(r"Inflict \+(\d+) (\[\w+\])"), r"对目标施加\1层\2"),
    (re.compile(r"Inflict (\d+) (\[\w+\])"), r"使目标增加\1级\2强度"),
    (re.compile(r"\bgain \+(\d+) (\[\w+\]) Count(?:s)?"), r"使自身获得\1层\2"),
    (re.compile(r"\bgain (\d+) (\[\w+\]) Count(?:s)?"), r"使自身获得\1层\2"),
    (re.compile(r"\bGain \+(\d+) (\[\w+\]) Count(?:s)?"), r"使自身获得\1层\2"),
    (re.compile(r"\bGain (\d+) (\[\w+\]) Count(?:s)?"), r"使自身获得\1层\2"),
    (re.compile(r"\bgain \+(\d+) (\[\w+\])"), r"使自身获得\1层\2"),
    (re.compile(r"\bgain (\d+) (\[\w+\])"), r"使自身增加\1级\2强度"),
    (re.compile(r"\bGain \+(\d+) (\[\w+\])"), r"使自身获得\1层\2"),
    (re.compile(r"\bGain (\d+) (\[\w+\])"), r"使自身增加\1级\2强度"),
    (re.compile(r"[Cc]lash Power \+(\d+)"), r"拼点威力+\1"),
    (re.compile(r"[Ff]inal Power \+(\d+)"), r"最终威力+\1"),
    (re.compile(r"[Cc]oin Power \+(\d+)"), r"硬币威力+\1"),
    (re.compile(r"\bdeal \+([\d.]+)% damage"), r"造成的伤害+\1%"),
    (re.compile(r"\bDeal \+([\d.]+)% damage"), r"造成的伤害+\1%"),
    (re.compile(r"\bdeal \+\(([^()]+)\)% damage"), r"造成的伤害+(\1)%"),
    (re.compile(r"\bDeal \+\(([^()]+)\)% damage"), r"造成的伤害+(\1)%"),
    (re.compile(r"\bto 获得等同于"), r"以获得等同于"),
    (re.compile(r"\bgain Shield equal to"), r"获得等同于"),
    (re.compile(r"\bGain Shield equal to"), r"获得等同于"),
    (re.compile(r"\bconsume (\d+) (\[\w+\]) Count"), r"消耗\1层\2"),
    (re.compile(r"\bConsume (\d+) (\[\w+\]) Count"), r"消耗\1层\2"),
    (re.compile(r"\bconsume up to (\d+) (\[\w+\]) Count"), r"最多消耗\1层\2"),
    (re.compile(r"\bConsume up to (\d+) (\[\w+\]) Count"), r"最多消耗\1层\2"),
    (re.compile(r"\bconsume all (\[\w+\]) Count"), r"消耗所有\1层数"),
    (re.compile(r"\bConsume all (\[\w+\]) Count"), r"消耗所有\1层数"),
    (re.compile(r"\btrigger (\[\w+\])"), r"使目标\1"),
    (re.compile(r"\bTrigger (\[\w+\])"), r"使目标\1"),
    (re.compile(r"\bto deal\b"), r"以使造成的"),
    (re.compile(r"\bto gain\b"), r"以获得"),
    (re.compile(r"\bto apply\b"), r"以应用"),
    (re.compile(r"\bto raise\b"), r"以提升"),
    (re.compile(r"\bto heal\b"), r"以恢复"),
    (re.compile(r"\bto activate\b"), r"以发动"),
    (re.compile(r"\bconvert\b"), r"转化"),
    (re.compile(r"\benter\b"), r"进入"),
    (re.compile(r"\bapplied to self\b"), r"对自身施加的"),
    (re.compile(r"\bon self\b"), r"自身"),
    (re.compile(r"\bfor the rest of\b"), r"在余下的"),
    (re.compile(r"\bthis Encounter\b"), r"本场战斗"),
    (re.compile(r"\bthis Skill\b"), r"本技能"),
    (re.compile(r"\bthis Coin's final damage\b"), r"本次硬币的最终伤害"),
    (re.compile(r"\bCoin's\b"), r"硬币的"),
    (re.compile(r"\bat (\d+)/(\d+)\+ (\[\w+\]) Potency"), r"若\3强度不低于\1/\2"),
    (re.compile(r"\bat (\d+)\+/(\d+)\+ (\[\w+\]) Potency"), r"若\3强度不低于\1/\2"),
    (re.compile(r"\bfor every\b"), r"每有"),
    (re.compile(r"\bevery\b"), r"每"),
    (re.compile(r"\bper target\b"), r"每个目标"),
    (re.compile(r"\bper enemy\b"), r"每名敌人"),
    (re.compile(r"\bper Skill\b"), r"每技能"),
    (re.compile(r"\bEncounter\b"), r"战斗"),
    (re.compile(r"\bSkill Slot\b"), r"行动槽"),
    (re.compile(r"\bDeployment (?:order|orders)\b"), r"编入顺位"),
    (re.compile(r"\bexclusive Skill\b"), r"专属技能"),
    (re.compile(r"\bSkills?\b"), r"技能"),
    (re.compile(r"\bCoins?\b"), r"硬币"),
    (re.compile(r"\bshield\b"), r"护盾"),
    (re.compile(r"\bShield\b"), r"护盾"),
    (re.compile(r"\bHP\b"), r"体力"),
    (re.compile(r"\bally\b"), r"友方单位"),
    (re.compile(r"\ballies\b"), r"友方单位"),
    (re.compile(r"\bat least\b"), r"至少"),
    (re.compile(r"\bactivate\b"), r"发动"),
    (re.compile(r"\bActivate\b"), r"发动"),
    (re.compile(r"\brandom\b"), r"随机"),
    (re.compile(r"\bremovable negative effect\b"), r"可解除的负面效果"),
    (re.compile(r"\bnegative effect\b"), r"负面效果"),
    (re.compile(r"\bthe said\b"), r"该"),
    (re.compile(r"\babove effect\b"), r"上述效果"),
    (re.compile(r"\beffect\b"), r"效果"),
    (re.compile(r"\bthis unit\b"), r"自身"),
    (re.compile(r"\baffected\b"), r"受影响的"),
    (re.compile(r"\bIdentity\b"), r"人格"),
    (re.compile(r"\bPierce damage\b"), r"突刺伤害"),
    (re.compile(r"\bLust damage\b"), r"色欲伤害"),
    (re.compile(r"\bequal to\b"), r"等同于"),
    (re.compile(r"\bcurrent\b"), r"当前"),
    (re.compile(r"\bConsumed\b"), r"消耗的"),
    (re.compile(r"\bconsumed\b"), r"消耗的"),
    (re.compile(r"\bcumulative\b"), r"累计"),
    (re.compile(r"\bcombat start\b"), r"战斗开始时"),
    (re.compile(r"\bbelow\b"), r"低于"),
    (re.compile(r"\babove\b"), r"高于"),
    (re.compile(r"\byou hear\?"), r"懂吗？"),
]

ENGINE = re.compile(r"\[[A-Za-z_][A-Za-z0-9_]*\]")
ANGLE = re.compile(r"<[^>\n]*>")


def translate(text: str) -> tuple[str, bool]:
    """返回 (译文, 是否完全译出)。未译出的片段保留英文。"""
    # 1) 整句精确命中
    hit = _EXACT.get(text)
    if hit:
        return hit, True
    # 2) 逐行处理
    out_lines = []
    ok = True
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            out_lines.append(line)
            continue
        if s in _EXACT:
            out_lines.append(_EXACT[s])
            continue
        cur = s
        for pat, rep in TEMPLATES:
            cur = pat.sub(rep, cur)
        # 仍有连续拉丁单词（3+ 字母）且不在标签/标记内 → 未完全译出
        probe = ANGLE.sub("", ENGINE.sub("", cur))
        if re.search(r"[A-Za-z]{3,}", probe):
            ok = False
        out_lines.append(cur)
    return "\n".join(out_lines), ok
