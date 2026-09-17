#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 glossary_all.tsv（官方术语文件 × 零协会汉化，id 级对齐）精编成分类权威术语表。

输入:  terms/glossary_all.tsv     en / cn / en_hits / cn_hits / source
输出:  terms/术语表.md             分类权威术语表（600-1000 条）
       terms/_review/missing.txt  INCLUDE 里没能在语料中找到的英文（应为空）

设计原则
  1. **不得臆造译名**：中文一律从 glossary_all.tsv 取；脚本只会「挑选」，不会「生成」。
  2. 采用「显式清单（INCLUDE）+ 规则兜底」，便于人工复核与复现。
  3. 同一个英文对应多个中文时全部保留，并在备注里写明区分条件（POLYSEMY_NOTE）。

用法:
  python3 tools/curate_glossary.py           # 生成术语表
  python3 tools/curate_glossary.py --review  # 打印每类内容供复核
"""
from __future__ import annotations

import collections
import os
import re
import sys

_KB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(_KB, "terms", "glossary_all.tsv")
OUT = os.path.join(_KB, "terms", "术语表.md")
REVIEW_DIR = os.path.join(_KB, "terms", "_review")

CAT_TITLES = {
    "world": "一、剧情设定与世界观",
    "combat": "二、战斗机制",
    "unit": "三、单位与敌人",
    "item": "四、道具与经济",
    "story": "五、剧情专名",
    "ui": "六、UI 与系统",
    "event": "七、活动与通行证",
}
CAT_ORDER = ["world", "combat", "unit", "item", "story", "ui", "event"]

# ============================================================ 显式清单
# 每行一个英文词条；大小写不敏感匹配 glossary_all.tsv。

WORLD = """
The City
The Backstreets
The Nests
The Wings
The Associations
Offices
Workshops
Fixer
Fixers
Syndicate
Syndicates
Distortions
Singularities
Color Fixer
Colours
Taboo
The Outskirts
The Great Lake
The Fingers
The Index
The Thumb
The Middle
The Ring
The Pinky
The Golden Bough
The Golden Boughs
Mirror Dungeons
Mirror Worlds
The Library
Lobotomy Corporation
Limbus Company
Mephistopheles
Threadspinning
Identity Uptying
Upgrading Identities
Identities
E.G.O
E.G.O Gear
Effloresced E.G.O
Abnormalities
Peccatula
Stage 2 Peccatula
Stage 3 Peccatula
Monsters
Risk Levels
Sweepers
Bloodfiend
Bloodfiends
Kindred
First Kindred
Second Kindred
Third Kindred
Anamnaworm
The Sign
Monolith
The Backdoor
Refraction Railways
Refraction Railway
Refraction Railway Line 1
Refraction Railway Line 2
Refraction Railway Line 3
Refraction Railway Line 4
Refraction Railway Line 5
Luxcavation Dungeons
Dimensional Container
Canned Experience
Memory Wipe Procedure
Concept Incinerator
Districts
The House of Spiders
The Blade Lineage
The Kurokumo Clan
Heishou Pack
The Heishou Pack
Prescript
Abnormality Corrosion
Pallidified
Pallidification
Sea Terror
LCB
LCA
LCC
LCD
LCE
Grade 8 Fixers
Combat Capability
PDA Device
The Second Smoke War
Smoke War
Night in the Backstreets
Bloodfiend Hunter
Corpse
"""

COMBAT = """
Wrath
Lust
Sloth
Gluttony
Gloom
Pride
Envy
Rage
Sin Resistance
Bleed
Burn
Tremor
Rupture
Sinking
Charge
Poise
Bind
Paralyze
Protection
Fragile
Haste
Aggro
Ammo
Attack Power Up
Attack Power Down
Power Up
Power Down
Damage Up
Damage Down
Offense Level Up
Offense Level Down
Defense Level Up
Defense Level Down
Defense Power Up
Defense Power Down
Clash Power Up
Clash Power Down
Base Power Up
Final Power Up
Plus Coin Boost
Plus Coin Drop
Max HP Up
HP Healing Boost
HP Healing Down
SP Heal Efficiency
SP Heal Efficiency Down
Tremor Burst
Tremor Sync
Sinking Deluge
Charge Barrier
Self-charge
Overcharge
Damage Taken
Take Less Damage
Unbreakable Coin
Clashable Guard
Wrath Boost
Wrath Power Up
Wrath Power Down
Wrath Fragility
Wrath DMG Up
Lust Boost
Lust Power Up
Lust Power Down
Lust Fragility
Lust DMG Up
Sloth Boost
Sloth Power Up
Sloth Power Down
Sloth Fragility
Sloth DMG Up
Gluttony Boost
Gluttony Power Up
Gluttony Power Down
Gluttony Fragility
Gluttony DMG Up
Gloom Boost
Gloom Power Up
Gloom Power Down
Gloom Fragility
Gloom DMG Up
Pride Boost
Pride Power Up
Pride Power Down
Pride Fragility
Pride DMG Up
Envy Boost
Envy Power Up
Envy Power Down
Envy Fragility
Envy DMG Up
Slash Power Up
Pierce Power Up
Blunt Power Up
Slash Fragility
Pierce Fragility
Blunt Fragility
Slash DMG Up
Pierce DMG Up
Blunt DMG Up
Slash Protection
Pierce Protection
Blunt Protection
Gaze
Contempt
Gaze of Contempt
Hardblood
Bloodfeast
Curse
Nails
Talisman
Tears
Marked
Stigmatized
Smoke
Cold
Frozen
Poison
Shock
Spark
Ember
Embers
Petals
Blazing
Regenerate
Discard
Vengeance
Vengeance Mark
Tribulation
Resentment
Hatred
Despair
Determination
Struggle
Rampage
Thorns
Urge
Hunger
Appetite
Desirous
Fear
Anguish
Anxiety
Guilt
Solitude
Emptiness
Relief
Grace
Blessing
Purity
Ruin
Blooming
Fully Bloomed
Wandering
Accelerating
Immobilized
Immobilize
Resurrect
Running
Agitated
Hardening
Splitting
Bereavement
Thirsting
Overwhelmed
Heal All
Inhaling
E.G.O Corrosion
Corrosion
Fever
Frenzy
Maddened
Ecstatic
Nervous
Stressed
Tipsy
Charmed
Dueling
Declared Duel
High Noon
Magic Bullet
Lasso
Capture
Captivity
Entanglement
Tangle
Trussed
Reload
Lightning
Instincts
Level Boost
Resilient
Keenness
Body Reinforcement
Frailness
Headstrong
Regroup
Firepower
Brutality
Outlash
Compulsion
Superiority
Karmic Consequence
Understanding
Happiness
Mental Awakening
Blind Obsession
Silent Regard
Time Moratorium
Time Acceleration
Interlocking Time
Shared Time
Borrowed Time
Amplitude Conversion
Amplitude Entanglement
Dimensional Rift
Unobservable
Weakness Analyzed
E.G.O Passives
E.G.O Resource Amp
"""

UNIT = """
Person
Core
Body
Head
Heart
Hands
Brain
Face
Left Arm
Right Arm
Left Leg
Right Leg
Left Eye
Right Eye
Shell
Tail
Roots
Wings
Maw
Flesh
Flower
Dimension
Device
Peccatulum Irae
Peccatulum Pigritiae
Peccatulum Morositatis
Peccatulum Gulae
Peccatulum Superbiae
Peccatulum Luxuriae
Peccatulum Invidiae
Lobotomy E.G.O
Effloresced E.G.O::GasHarpoon
Effloresced E.G.O::Spicebush
Effloresced E.G.O::Farmwatch
Effloresced E.G.O::Procuration
Kromer
Cassetti
Sasha
Butterfly of Entangled Lives
The Time Ripper
Portrait
Portrait of a Certain Day
Doomsday Calendar
Doomsday Calendar-A
Alleyway Watchdog
Pink Shoes
Pink Shoes-A
Headless Ichthys
kqe-1j-23
Hurting Teddy Bear
Golden Apple
False Apple
Yinglong
The Knight of Despair
The Knight of the White Moon
The Last Knight
Fairy Queen
Ebony Queen's Apple
Distorted Hohenheim
Distorted Bamboo-hatted Kim
You Want To Get Beat? Hurtily?
Will You Play?
Sleeping Bag of a Bygone Day
Der Fluchschütze
Flash Phenomenon
Fairy Mass
Headchicken a.k.a. Bongy
Papa Bongy
Spiced-up Papa Bongy
Dongrang, Who Denies All
Mimicry Corroded
Coil Corroded
Feral Mane Corroded
Brazen Bull - Tearful
Mayors, the Yearning Flotsam
Siltcurrent
Dream-Devouring Siltcurrent
Skin Prophet
Ambling Pearl
Shock Centipede
Drifting Fox
Fairy Gentleman
Fairy-Long-Legs
Fairy Longlegs
My Form Empties
Blubbering Toad
Four-hundred Roses
Dreaming Electric Sheep
The King in Binds
Wayward Passenger
Sign of Roses
Steam Transport Machine
The Carousel
Ardor Blossom Moth
Spiral of Contempt
Fell Bullet
Faelantern
Drenched Gossypium
Erlking Heathcliff
Rose Hunter
Baba Yaga
Baba Yaga-A
Baba Yaga-B
Stuffed Toy
Old Umbrella
Fairy Wine
Telepole
Sack
Seaborn
Doomsday Clay Doll
King Trash Crab
Leafy Gnome
Cherry Gnome
Shadowy Gnome
Hand of the Saint
Bloodbag
W Corp. Bloodbag
"""

ITEM = """
Coin
Lunacy
Paid Lunacy
Free Lunacy
Egoshards
Thread
Threadskein
Thread Crate
Enkephalin
Enkephalin Module
Enkephalin Box
Extraction Ticket
Decaextraction Ticket
3★ Guarantee Decaextraction Ticket
Identity Training Ticket I
Identity Training Ticket II
Identity Training Ticket III
Identity Training Ticket IV
Level Boost Ticket I
Level Boost Ticket II
Level Boost Ticket III
Level Boost Ticket IV
Level Boost Ticket V
Level Boost Ticket VI
Identity Takeoff Ticket
Takeoff Module - ID Uptie
Takeoff Module - E.G.O Spinning [ZAYIN]
Takeoff Module - E.G.O Spinning [TETH]
Nominable Identity Ticket
Nominable S1 Identity Ticket
Nominable S2 Identity Ticket
Nominable S3 Identity Ticket
Cost
Starlight
Starlight Bonus
Pocket Watch
Pocket Watch Bundle
Bus-modifying Scrap
Rare Horseshoe with Bus-modifying Scrap
Trinkets Sack
Huge Trinkets Sack
Photos
Photo Bundles
Amassed Data
Classified Data
Bloodied Scabbard
Sea Terror Sample
Luminous Sea Terror Sample
Severed Thread
Severed and Scorched Skein
Civilian Recov. Pack
Fixer Recov. Pack
Unrolled Film
Starlight of Immortality
Spinchains
K Corp Ampule
K Corp. Emergency Ampule
Regeneration Ampules
Decay Ampules
Decay Ampule
Wish Canister
E.G.O Gifts
E.G.O Gift Compendium
Fuse E.G.O Gift
Acquire E.G.O Gift
Purchase E.G.O Gifts
Selected E.G.O Gift
E.G.O Gift Tiers
Rest
Hammer
Nagel
Nail and Hammer
Potentialities
Faith
Wealth
Unbending
Hardship
Awe
Oracle
Reminiscence
Grandeur
Cultivation
Sunshower
Employee Card
Respite
The Spider's Thread
Resolution
Squalidity
Downpour
Fluorescent Lamp
Sword Sharpened with Tears
Rags
Four-leaf Clover
Devotion
Bongy Plush
Exquisite Artwork
A Drop
Rusted Hilt
Black Ledger
Equalizer
Chains of Loyalty
Lightning Rod
Broken Blade
Fractured Blade
Metronome
Carmilla
Artistic Sense
Reverberation
Golden Hour
Homeward
Thrill
Prejudice
Finifugality
Ragged Umbrella
Bloodflame Sword
Red Tassel
Worn Hilt
Green Spirit
Crown of Roses
Glimpse of Flames
Material Interference Force Field
Uncapped Defibrilator
Crown of Thorns
Kaleidoscope
Ragged Bamboo Hat
Fiery Down
Bloody Gadget
Talisman Bundle
White Gossypium
Nixie Divergence
Voodoo Doll
Old Wooden Doll
Ruptured Blood Sac
Sublimity
Resplendence
Hardblood Glaive
Cetacean Heart
"""

STORY = """
Yi Sang
Faust
Don Quixote
Ryōshū
Meursault
Hong Lu
Heathcliff
Ishmael
Rodion
Sinclair
Outis
Gregor
Vergilius
Catherine
Hindley
Ahab
Queequeg
Starbuck
Sancho
Dulcinea
Hohenheim
Araya
Nelly
Jia Baoyu
Jia Xichun
Jia Mu
Lin Daiyu
Xue Baochai
Xiren
Xue Pan
Wang Qingshan
Shi Yihua
Shi Huazhen
Shi Sijing
Lei Heng
Zilu
Bamboo-hatted Kim
Siegfried
Yuri
Aida
Josephine
Ricardo
Erlking
The Barber
The Priest
The Adept
The Master
The Inquisitor
Inquisitors
The Cleanup Agent
Baoyu, the Precious Jade
Dead Rabbits Boss
Tingtang Boss
Captain of the Pequod
The Big Brother
The First Mate
Mr. Pilot
The Indigo Elder
The Pallid Whale
K Corp.
T Corp.
N Corp.
W Corp.
R Corp.
S Corp.
P Corp.
H Corp.
L Corp.
G Corp.
U Corp.
X Corp.
M Corp.
A Corp.
Old G Corp.
Lobotomy Corp. Branch
Lobotomy Corp. Headquarters
Cinq Association
Zwei Association
Liu Association
Seven Association
Dieci Association
Shi Association
Devyat' Association
Öufi Association
Dawn Office
Full-Stop Office
Fanghunt Office
Hook Office
Molar Office
Jeong's Office
MultiCrack Office
Kurokumo Clan
Blade Lineage
Heishou Pack - Mao Branch
Heishou Pack - Si Branch
Heishou Pack - Wu Branch
Heishou Pack - Wei Branch
Heishou Pack - You Branch
Heishou Pack Adept
Jia Family
Shi Family
Xue Family
Wang Family
Edgar Family
Twinhook Pirates
Night Awls
Tingtang Gang
Los Mariachis
Tieqiu Crew
Dihui Star
The Pequod
Rosespanner Workshop
School of Fauvism
School of Pointillism
School of Corporism
N Corp. Fanatic
Family Hierarch
Family Hierarch Candidate
The Dead Rabbits
Technology Liberation Alliance
La Manchaland
Yurodiviye
Limbus Kindergarten
Perky Penguins
Cheery Chickies
Early Elephants
R.B.
Maestro
Student
Docent
Capo IIII
Soldato II
Soldato III
War Hero
Royalty
Tiansha Star
The Oracle's Proxy
Abraxas Chariot
Wuthering Heights
Pequod Town
Kezhan
Yihongyuan
District 20 Backstreets
Rhodes Island
Terra
Shelter
Ritual Square
Heart of the Whale
Right Heart Atrium
Right Heart Ventricle
Sinew Bridge
Whale Guts
Torture Chamber
Underground Church
Chapel
Screening Room
Training Yard
Memories
Children
Family
Nursefathers
Bloodfiends
"""

UI = """
Sinners
Identities
Team
Loadout
Select
Default
Leave
Enter
Activate
Deactivate
Reward
Rewards
Claim Rewards
Clear Rewards
Enhance
Fuse
Floor Theme
Theme Pack
Theme Pack Compendium
Parallel Superposition
Parallel Superposition Mode
Adversity
Trials
Challenge
Points
Hard Difficulty
Extra Charge
Select Sinner
On Team
Backup
Backup Deployed
Chain
Cycle Count
Final Turn Count
Clear Turns
Encounters
Elite Encounter
Rest Stop
Rest Bonus
Starter Buffs
Weekly Bonuses
Shop
Refresh
Purchased
Acquired
Available
Completed
Incomplete
Exploring
Hidden
Unacquired
Selectable
Unselectable
Activated
Participating
Guaranteed
Featured
Recent
Simulation
Rights
Prediction
Projection Rate
Effective Affinities
Info. Team Passage
Info. Team Lobby
Safety Team
Lost & Found
The Terminus
Section 1
Section 2
Section 3
Section 4
Line 1
Line 2
Line 3
Line 4
Line 5
Line 6
Enemy Buffs
Active Effects
Choice Effects
Banner Requisites
Recommended Levels
Try Again
Details
Summary
E.G.O Gift Search
Pack Search
Theme Pack Observation
Keyword Refresh
Floor Theme
E.G.O Gift Compendium
Starlight Bonus
The Present
The Past
The Future
End Stage
Continue
"""

EVENT = """
Battle Pass
Limbus Pass
Season 3
Season 4
Season 5
Season 6
Season 7
Combat
Free
Buy
Regular
Daily
Weekly
Seasonal
Mnestic Experience
Battle Pass XP
Max Pass Level Reward
Limbus Pass Package Special Banner
Walpurgis Night
The 2nd Walpurgis Night
The 3rd Walpurgis Night
The 4th Walpurgis Night
The 5th Walpurgis Night
The 6th Walpurgis Night
The 8th Walpurgis Night
Mirror of Immortality
Mirror of the Dreaming
Mirror of Names and Spiders
Mirror of Mirrors
Mirror of the Lake
Mirror of the Wuthering
Mirror of the Beginning
Timekilling Time
Timekilling Time BokGak
Nocturnal Sweeping
Nocturnal Sweeping BokGak
LCB Regular Check-up
LCB Regular Check-up BokGak
Pilgrimage of Compassion
Nagel und Hammer
Spring Cultivation
The Dawn of Green
Chachihu
Murder on the WARP Express
Murder on the WARP Express BokGak
Hell's Chicken
S.E.A.
The Noon of Violet
The Dusk of Amber
Miracle in District 20
Twining Threads
Yield My Flesh to Claim Their Bones
Hatred and Despair
Falling Flowers
Code Purple
The Unsevering
The Dream Ending
Full-Stopped by a Bullet
Deep Sigh
Unrelenting Might
The Unchanging
The Unconfronting
The Heartbreaking
Bloodtinged Ichthyic Odor
CLEAR ALL CATHY
BON VOYAGE
ORIENTATION
OBLIVION
REMINISCENCE
Kumo no Ito · otI on akA
Walpurgis Night
"""

# ============================================================ 语料补充
# 有些核心词（伤害类型、战斗 UI 词汇、主要人名）没被术语文件抽取器收进 glossary_all.tsv，
# 但它们在语料里是**逐 id 对照**的。这里显式给出 (英文, 来源文件) 从 corpus.jsonl 直接取中文，
# 同样是"取自语料"，不是自拟。

CORPUS_ADD = {
    "world": [
        ("The Head", "ScenarioModelCodes-AutoCreated.json"),
        ("Distortion", "ScenarioModelCodes-AutoCreated.json"),
        ("Abnormality", "StoryData/P10414.json"),
    ],
    "combat": [
        ("Slash", "EgoGiftCategory.json"),
        ("Pierce", "EgoGiftCategory.json"),
        ("Blunt", "EgoGiftCategory.json"),
        ("Potency", "BattleUIText.json"),
        ("Count", "BattleUIText.json"),
        ("Stack", "BattleUIText.json"),
        ("Turns", "BattleUIText.json"),
        ("Sanity", "BattleUIText.json"),
        ("HP", "MainUIText.json"),
        ("Max HP", "TooltipUIText.json"),
        ("Speed", "FormationUI_S6.json"),
        ("Offense Level", "BattleUIText.json"),
        ("Defense Level", "BattleUIText.json"),
        ("Damage", "BattleUIText.json"),
        ("Guard", "BattleUIText.json"),
        ("Evade", "BattleUIText.json"),
        ("Counter", "BattleUIText.json"),
        ("Defense", "BattleUIText.json"),
        ("STAGGER", "BattleUIText.json"),
        ("BREAKDOWN", "BattleUIText.json"),
        ("Low Morale", "BattleUIText.json"),
        ("Panic", "BattleUIText.json"),
        ("Status", "BattleUIText.json"),
        ("Effects", "BattleUIText.json"),
        ("Resistances", "BattleUIText.json"),
        ("Awakening", "BattleUIText.json"),
        ("Corrosion", "BattleUIText.json"),
        ("Resonance", "BattleUIText.json"),
        ("A-Res", "BattleUIText.json"),
        ("Atk Weight", "BattleUIText.json"),
        ("Attack Weight", "TooltipUIText.json"),
        ("Offset", "BattleUIText.json"),
        ("Unopposed", "BattleUIText.json"),
        ("One-sided Guard", "BattleUIText.json"),
        ("Part Broken", "BattleUIText.json"),
        ("Slash Resistance", "TooltipUIText.json"),
        ("Pierce Resistance", "TooltipUIText.json"),
        ("Blunt Resistance", "TooltipUIText.json"),
        ("Wrath Resistance", "TooltipUIText.json"),
        ("Lust Resistance", "TooltipUIText.json"),
        ("Sloth Resistance", "TooltipUIText.json"),
        ("Gluttony Resistance", "TooltipUIText.json"),
        ("Gloom Resistance", "TooltipUIText.json"),
        ("Pride Resistance", "TooltipUIText.json"),
        ("Envy Resistance", "TooltipUIText.json"),
    ],
    "story": [
        ("Dante", "StoryData/S001A.json"),
        ("Charon", "Announcer.json"),
        ("Demian", "StoryData/3D309A.json"),
        ("Sonya", "StoryData/2D306B.json"),
        ("Hermann", "StoryData/S647B.json"),
        ("Linton", "StoryData/S647B.json"),
        ("Pip", "StoryData/S647B.json"),
        ("Camille", "StoryData/S647B.json"),
        ("Hopkins", "StoryData/3D307B.json"),
        ("Effie", "StoryData/4D303A.json"),
        ("Saude", "StoryData/4D303A.json"),
        ("Bari", "StoryData/S951B.json"),
    ],
    "ui": [
        ("Check Passed", "BattleUIText.json"),
        ("Check Failed", "BattleUIText.json"),
        ("Check Skipped", "BattleUIText.json"),
        ("Success Rate", "BattleUIText.json"),
        ("Win Rate", "BattleUIText.json"),
        ("Threshold", "BattleUIText.json"),
        ("Floor Boss", "BattleUIText.json"),
        ("Checkpoint", "BattleUIText.json"),
        ("Saferoom", "BattleUIText.json"),
        ("Regular Encounter", "BattleUIText.json"),
        ("Focused Encounter", "BattleUIText.json"),
        ("Risky Encounter", "BattleUIText.json"),
        ("Boss Encounter", "BattleUIText.json"),
        ("Combat Encounter", "BattleUIText.json"),
        ("Part HP", "BattleUIText.json"),
        ("Current HP", "BattleUIText.json"),
        ("Obs. Level", "BattleUIText.json"),
        ("All Parts", "BattleUIText.json"),
        ("Destructible", "BattleUIText.json"),
        ("Retreating", "BattleUIText.json"),
        ("Incapacitated", "BattleUIText.json"),
        ("Conditional", "BattleUIText.json"),
        ("Always Active", "BattleUIText.json"),
        ("Passives", "BattleUIText.json"),
        ("Skill Effects", "BattleUIText.json"),
        ("Skill", "BattleUIText.json"),
        ("Skill Attack Type", "FormationUI.json"),
        ("Skill Affinity", "FormationUI.json"),
        ("E.G.O Attack Type", "FormationUI.json"),
        ("E.G.O Affinity", "FormationUI.json"),
        ("Speed Range", "TooltipUIText.json"),
        ("Team Code", "FormationUI.json"),
        ("Announcers", "FormationUI.json"),
        ("Rarity", "FormationUI.json"),
        ("Collection Rate", "FormationUI.json"),
        ("Sort By", "FormationUI.json"),
        ("Support Identities", "FormationUI.json"),
        ("Enemy Info", "BattleUIText.json"),
        ("Extra Objective", "BattleUIText.json"),
        ("AoE Skills", "BattleUIText.json"),
        ("Commence Battle", "BattleUIText.json"),
        ("Legend", "BattleUIText.json"),
        ("Choices", "BattleUIText.json"),
        ("Proceed", "BattleUIText.json"),
        ("Start", "BattleUIText.json"),
        ("Event", "BattleUIText.json"),
    ],
    "event": [
        ("Season 1", "MainUIText.json"),
        ("Season 2", "UserInfo_Friends.json"),
    ],
}

# 明确的存疑标记（译法来自语料，但用词可疑或语境特殊）
SUSPECT = {
    "colours", "districts", "anamnaworm", "monsters", "corpse",
    "pallidification", "canned experience",
}
SUSPECT_NOTE = {
    "colours": "剧情节点标题用「颜色」，与「特色（Color Fixer）」不是一回事，勿混用",
    "districts": "但丁笔记里的「地区」条目名，正文中很少直接出现，疑为条目名而非行文用语",
    "anamnaworm": "但丁笔记中 Anamnaworm 只译作「虫」；正文里「虫」也泛指昆虫，直接套用有歧义，建议查证后再定",
    "monsters": "但丁笔记里的分类名，正文中「怪物」是通用词，术语化存疑",
    "corpse": "KeywordDictionary 条目，正文中「尸体」是通用词",
    "pallidification": "与 Pallidified 同义（白化），但词性不同，行文中按「白化」处理",
    "canned experience": "但丁笔记中的道具名，仅此一处出现",
}

# ============================================================ 备注

POLYSEMY_NOTE = {
    ("simulation", "模拟"): "镜像迷宫难度/模式项",
    ("simulation", "难易度：模拟"): "设置项完整标签写法",
    ("featured", "可能出现"): "主题卡包内可能出现的 E.G.O 饰品",
    ("featured", "可出现"): "图鉴内的可获得标记",
    ("active effects", "生效的效果"): "折射轨道队伍当前生效效果",
    ("active effects", "当前效果"): "镜像迷宫内当前生效效果",
    ("base power up", "基础威力提升"): "战斗关键词标准写法",
    ("base power up", "基础威力强化"): "镜像迷宫内写法",
    ("max hp up", "体力上限提升"): "战斗关键词标准写法",
    ("max hp up", "体力上限强化"): "镜像迷宫内写法",
    ("final turn count", "总计回合数"): "折射轨道结算总回合",
    ("final turn count", "总计清剿回合数"): "折射轨道清剿回合统计",
    ("respite", "安息之地"): "E.G.O 饰品名（镜像迷宫）",
    ("respite", "暂息"): "异想体被动名（walpu6）",
    ("reminiscence", "追忆"): "E.G.O 饰品名",
    ("reminiscence", "REMINISCENCE"): "赛季标题，沿用原文大写",
    ("the spider's thread", "蜘蛛网"): "E.G.O 饰品名",
    ("the spider's thread", "蜘蛛丝"): "剧情节点名",
    ("crown of thorns", "冠冕"): "战斗关键词（Refraction2）",
    ("crown of thorns", "荆棘头冠"): "E.G.O 饰品名",
    ("ragged umbrella", "破损的雨伞"): "E.G.O 饰品名",
    ("ragged umbrella", "磨损殆尽的伞"): "异想体被动名",
    ("kumo no ito · oti on aka", "蛛丝赤"): "战斗通行证内的曲名/主题",
    ("kumo no ito · oti on aka", "Kumo no ito · oti on akA"): "赛季标题，沿用原文",
    ("feral mane corroded", "兽鬃侵蚀者"): "同一异想体的两种写法，优先用「兽鬃侵蚀者」",
    ("the present", "现在"): "折射轨道“现在”时间轴",
    ("the past", "过去"): "折射轨道“过去”时间轴",
    ("the future", "未来"): "折射轨道“未来”时间轴",
    ("kqe-1j-23", "Kqe-1j-23"): "异想体编号，不译",
    ("starlight", "星芒"): "货币名",
    ("starlight", "星芒奖励"): "结算界面标题",
    ("details", "详情"): "镜像迷宫内关卡详情页",
    ("details", "详细信息"): "折射轨道详情面板",
    ("details", "详细内容"): "通用详情弹窗",
    ("details", "详细情报"): "折射轨道敌人/关卡情报",
    ("default", "基础"): "编队/装备的“基础”预设",
    ("default", "默认"): "通用设置默认值",
    ("default", "默认排序"): "排序方式",
    ("owned", "拥有"): "持有数量标签",
    ("owned", "已拥有"): "已获得标记",
    ("owned", "已持有"): "商店内已持有标记",
    ("person", "人"): "敌人部件/人群（Enemies_Refraction）",
    ("person", "人类"): "单位类型（Enemies）",
    ("identities", "人格"): "设定/图鉴用语",
    ("identities", "参战人格"): "编队界面：本次出战的人格",
    ("enter", "完成"): "确认按钮（完成输入）",
    ("enter", "进入战斗"): "进入战斗节点",
    ("activate", "激活"): "界面内激活 E.G.O 饰品/效果",
    ("activate", "发动"): "战斗中发动但丁能力",
    ("gaze", "视线"): "状态效果（BF-a1c8p3）",
    ("gaze", "凝视"): "状态效果（BF 主表）",
    ("offense level up", "攻击等级提升"): "战斗关键词标准写法",
    ("offense level up", "攻击等级强化"): "镜像迷宫内写法",
    ("defense level up", "防御等级提升"): "战斗关键词标准写法",
    ("defense level up", "防御等级强化"): "镜像迷宫内写法",
    ("defense power up", "忍耐"): "战斗关键词标准写法",
    ("defense power up", "守备威力强化"): "镜像迷宫内写法",
    ("backup", "待命人员"): "折射轨道编队替补",
    ("backup", "掩护"): "被动技能名",
    ("shell", "壳"): "白鲸章生物躯壳",
    ("shell", "外壳"): "机械/结构外壳",
    ("starlight", "星芒"): "货币名",
    ("starlight", "星芒奖励"): "结算界面标题",
    ("marked", "标记"): "状态效果（通用）",
    ("marked", "标识"): "状态效果（章节专用）",
    ("rampage", "挣扎"): "状态效果名",
    ("rampage", "狂暴"): "异想体被动名",
    ("struggle", "挣扎"): "状态效果名",
    ("struggle", "苦斗"): "异想体被动名",
    ("support", "呐喊助威"): "被动技能名",
    ("support", "辣喊助威"): "边狱幼儿园活动的官方趣味错字，沿用",
    ("progress", "当前进度"): "迷宫内进度",
    ("progress", "成就进度"): "成就/奖杯进度",
    ("total turns", "累计回合数"): "折射轨道实时显示",
    ("total turns", "最终累计回合"): "结算结果",
    ("clear rewards", "通关奖励"): "镜像迷宫",
    ("clear rewards", "清剿奖励"): "折射轨道",
    ("compulsion", "强迫"): "状态效果：强迫",
    ("compulsion", "自残"): "状态效果：自残",
    ("superiority", "优势"): "异想体被动",
    ("superiority", "优越感"): "异想体被动（Refraction2）",
    ("determination", "觉悟"): "状态效果",
    ("determination", "决意"): "异想体/被动名",
    ("resolution", "觉悟"): "被动技能名",
    ("resolution", "决意"): "E.G.O 饰品名",
    ("concentration", "沉浸"): "异想体被动",
    ("concentration", "集中精神"): "被动技能名",
    ("strife", "争斗"): "剧情节点名",
    ("strife", "斗争"): "被动技能名",
    ("homeward bound", "回家"): "剧情节点名（第九章）",
    ("homeward bound", "归乡"): "剧情节点名（第八章）",
    ("morale boost", "昂扬"): "战斗关键词",
    ("morale boost", "提振士气"): "被动技能名",
    ("keen observation", "观察"): "被动技能名",
    ("keen observation", "观察力"): "战斗关键词",
    ("resentment", "仇怨"): "状态效果（主表）",
    ("resentment", "怨恨"): "状态效果（exme 活动）",
    ("resentment", "疙瘩"): "敌人部件名",
    ("persistence", "执念"): "敌人被动",
    ("persistence", "坚韧"): "战斗关键词",
    ("not enough cost", "经费"): "提示词简写",
    ("not enough cost", "经费不足"): "提示语完整写法",
    ("happiness", "喜"): "状态效果（a1c8p3）",
    ("rage", "暴怒"): "战斗关键词：暴怒（罪孽属性别名）",
    ("fever", "狂热"): "战斗关键词",
    ("frenzy", "狂暴"): "战斗关键词",
    ("frenzy", "热气"): "异想体被动（mr7-extreme）",
    ("hard", "困难"): "难度选项",
    ("hard", "Hard"): "未汉化的难度枚举，沿用原文",
    ("normal", "普通"): "难度选项",
    ("normal", "Normal"): "未汉化的难度枚举，沿用原文",
    ("struggle", "挣扎"): "状态效果名",
    ("coin", "铜钱"): "镜像迷宫 E.G.O 饰品（a1c8p2）",
    ("refraction", "折射"): "战斗关键词 / 设定词",
    ("corrosion", "侵蚀"): "异想体被动",
    ("corrosion", "侵蚀"): "异常状态（异想体施加）",
    ("corrosion", "侵蚀技能"): "E.G.O 的侵蚀形态技能，战斗 UI 用语",
    ("e.g.o", "E.G.O"): "不译，保留原文缩写",
    ("sloth", "怠惰"): "罪孽属性",
    ("wrath", "暴怒"): "罪孽属性",
    ("lust", "色欲"): "罪孽属性",
    ("gluttony", "暴食"): "罪孽属性",
    ("gloom", "忧郁"): "罪孽属性",
    ("pride", "傲慢"): "罪孽属性",
    ("envy", "嫉妒"): "罪孽属性",
    ("sancho", "桑丘"): "堂吉诃德的“桑丘”人格/血魔真名",
    ("don quixote", "堂吉诃德"): "罪人；同时是其血魔真名（桑丘）的对照",
    ("erlking", "魔王"): "呼啸山庄章节的“魔王希斯克利夫”",
    ("the erlking", "魔王"): "同上",
    ("kromer", "克罗默"): "N公司相关角色 / 异想体“欲成原初的克罗默”",
    ("piers", "皮埃尔斯"): "存疑",
}

EXTRA_NOTE = {
    "the city": "世界观核心：人类最后的都市",
    "the backstreets": "巢外区域，与“巢”相对",
    "the nest": "翼所管辖的城区，通称“巢”",
    "the nests": "复数形式",
    "wing": "世界设定中的巨型企业（K公司、N公司等）",
    "the wings": "复数形式",
    "the head": "都市的最高统治者",
    "the associations": "收尾人行业协会总称（Hana/Zwei/Shi/Cinq…）",
    "the fingers": "五大手指：食指·拇指·中指·环指·小指",
    "the index": "手指之一",
    "the thumb": "手指之一",
    "the middle": "手指之一",
    "the ring": "手指之一",
    "the pinky": "手指之一",
    "fixer": "都市中以接受委托为业的职业，按阶分级",
    "fixers": "复数形式",
    "syndicate": "帮派（后巷势力）",
    "syndicates": "复数形式",
    "office": "收尾人事务所，接受委托的单位",
    "offices": "复数形式",
    "workshop": "工坊，生产武器/义体/装备",
    "workshops": "复数形式",
    "singularity": "翼赖以立足的独有技术",
    "singularities": "复数形式",
    "distortion": "扭曲：心之崩溃后的异形化现象",
    "distortions": "复数形式",
    "color fixer": "特色收尾人，收尾人的最高阶",
    "grade 8 fixers": "按阶分级：8阶为最低阶",
    "taboo": "都市的禁忌事项",
    "the outskirts": "都市外围的荒野",
    "the great lake": "大湖，裴廓德号等故事的舞台",
    "the golden bough": "金枝，边狱公司的回收目标",
    "the golden boughs": "复数形式",
    "identity": "人格：罪人的可替换身份",
    "mirror dungeons": "镜像迷宫",
    "mirror worlds": "镜像世界（人格/E.G.O 的来源）",
    "threadspinning": "异想解析，把异想体分解为纺锤",
    "identity uptying": "人格同步（提升人格等级上限）",
    "upgrading identities": "人格强化",
    "refraction railway": "折射轨道",
    "the library": "图书馆（《废墟图书馆》舞台）",
    "lobotomy corporation": "脑叶公司（前作）",
    "library of ruina": "废墟图书馆（前作）",
    "limbus company": "边狱公司（本作组织名）",
    "mephistopheles": "边狱公司的巴士名",
    "abnormality": "异想体",
    "abnormalities": "复数形式",
    "peccatula": "罪种，罪孽属性的具现化敌人",
    "sweepers": "清道夫，后巷深宵时出现的清扫者",
    "bloodfiend": "血魔",
    "bloodfiends": "复数形式",
    "kindred": "眷属（血魔的下级）",
    "prescript": "食指发出的指令",
    "e.g.o": "不译，保留原文缩写",
    "e.g.o gear": "E.G.O 装备",
    "effloresced e.g.o": "绽放 E.G.O（异想体专用 E.G.O 形态）",
    "risk levels": "危险等级（ZAYIN/TETH/HE/WAW/ALEPH）",
    "wx": "",
    "wrath": "罪孽属性：暴怒（红）",
    "lust": "罪孽属性：色欲（橙）",
    "sloth": "罪孽属性：怠惰（黄）",
    "gluttony": "罪孽属性：暴食（绿）",
    "gloom": "罪孽属性：忧郁（青）",
    "pride": "罪孽属性：傲慢（蓝）",
    "envy": "罪孽属性：嫉妒（紫）",
    "slash": "伤害类型：斩击",
    "pierce": "伤害类型：突刺",
    "blunt": "伤害类型：打击",
    "bleed": "状态：流血",
    "burn": "状态：烧伤",
    "tremor": "状态：震颤",
    "rupture": "状态：破裂",
    "sinking": "状态：沉沦",
    "charge": "状态：充能",
    "poise": "状态：呼吸法",
    "bind": "状态：束缚",
    "paralyze": "状态：麻痹",
    "protection": "状态：守护",
    "fragile": "状态：易损",
    "haste": "状态：迅捷",
    "aggro": "挑衅值",
    "ammo": "弹药",
    "potency": "层数（效果强度）",
    "count": "计数（持续回合数）",
    "coin": "硬币；镜像迷宫内亦作 E.G.O 饰品名“铜钱”",
    "clash": "拼点",
    "stagger": "眩晕；显示层数“失衡”",
    "sanity": "理智值",
    "hp": "体力",
    "sp": "理智值",
    "max hp": "体力上限",
    "max sp": "理智值上限",
    "offense level": "攻击等级",
    "defense level": "防御等级",
    "combat passive": "战斗被动",
    "support passive": "支援被动",
    "e.g.o passives": "E.G.O 被动",
    "skill replacement": "技能替换",
    "cost": "经费（镜像迷宫内货币）",
    "starlight": "星芒（镜像迷宫内货币）",
    "thread": "纺锤，人格同步/异想解析的通用素材",
    "egoshards": "自我碎片（人格碎片）",
    "lunacy": "狂气（抽卡货币）",
    "enkephalin": "脑啡肽（体力）",
    "identity": "人格",
    "battle pass": "战斗通行证",
    "limbus pass": "边狱通行证",
    "walpurgis night": "瓦尔普吉斯之夜（限定主题）",
    "mirror of immortality": "永生之镜（镜像迷宫名称）",
    "bokgak": "复刻（韩文 복각 的罗马字，官译沿用不译）",
}


# ============================================================ 载入 / 渲染

def load_rows():
    rows = []
    with open(SRC, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 5:
                continue
            rows.append({
                "en": p[0], "cn": p[1],
                "hits": int(p[2]) + int(p[3]),
                "src": p[4],
            })
    return rows


def parse_block(block: str) -> list[str]:
    out = []
    for line in block.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line.lower())
    return out


def build_index(rows):
    """{lower_en: [row, ...]}，按 hits 降序。"""
    idx: dict[str, list] = {}
    for r in rows:
        idx.setdefault(r["en"].strip().lower(), []).append(r)
    for k in idx:
        idx[k].sort(key=lambda r: -r["hits"])
    return idx


def clean(rows):
    """丢掉带富文本标签 / 模板占位 / 纯韩文的条目。"""
    out = []
    for r in rows:
        en, cn = r["en"], r["cn"]
        if "<" in en and ">" in en:
            continue
        if "{" in en or "}" in en:
            continue
        if re.search(r"[\uac00-\ud7af]", en):  # 韩文出现在英文侧 = 源文件噪声
            continue
        if en.strip() == "" or cn.strip() == "":
            continue
        out.append(r)
    return out


def load_corpus_index():
    """从 corpus.jsonl 建 (file, id, field) -> {lang: text}，再反查 英文 -> 中文。

    用于 CORPUS_ADD：只做**精确整串匹配**，避免把恰好同形的技能名当成术语。
    """
    import json
    recs: dict[tuple, dict] = {}
    path = os.path.join(_KB, "data", "corpus.jsonl")
    if not os.path.exists(path):
        return {}, {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            recs.setdefault((r["f"], r["id"], r["k"]), {})[r["l"]] = r["t"]
    by_src: dict[tuple, str] = {}
    by_en: dict[str, collections.Counter] = {}
    for (f, _i, _k), v in recs.items():
        en = v.get("en", "").strip()
        cn = v.get("cn", "").strip()
        if not en or not cn:
            continue
        by_src[(en, f)] = cn
        by_en.setdefault(en, collections.Counter())[cn] += 1
    return by_src, by_en


def corpus_lookup(key: str, en: str, hint: str, by_src, by_en):
    cn = by_src.get((en, hint))
    if cn:
        return {"en": en, "cn": cn, "hits": 1, "src": hint, "from": "corpus"}
    c = by_en.get(en)
    if c:
        cn, _n = c.most_common(1)[0]
        return {"en": en, "cn": cn, "hits": 0, "src": hint, "from": "corpus"}
    return None


def dedupe_cn(rows):
    """同一 cn 只保留一次（不同来源但译法相同 → 不算一词多译）。"""
    seen, out = set(), []
    for r in rows:
        if r["cn"] in seen:
            continue
        seen.add(r["cn"])
        out.append(r)
    return out


def note_for(key: str, rows) -> str:
    uniq = dedupe_cn(rows)
    notes = []
    if key in EXTRA_NOTE and EXTRA_NOTE[key]:
        notes.append(EXTRA_NOTE[key])
    if len(uniq) > 1:
        parts = []
        for r in uniq:
            n = POLYSEMY_NOTE.get((key, r["cn"]))
            src = r["src"].replace(".json", "") or "未知来源"
            parts.append(f"{r['cn']}：{n}" if n else f"{r['cn']}（见 {src}）")
        notes.insert(0, "**一词多译** — " + "；".join(parts))
    out = "；".join(notes)
    if key in SUSPECT:
        sn = SUSPECT_NOTE.get(key, "")
        tag = f"（存疑：{sn}）" if sn else "（存疑）"
        out = (out + "；" + tag) if out else tag
    return out


def cn_cell(rows) -> str:
    return " / ".join(r["cn"] for r in dedupe_cn(rows))


def main() -> None:
    rows = clean(load_rows())
    idx = build_index(rows)
    by_src, by_en = load_corpus_index()

    blocks = {
        "world": WORLD, "combat": COMBAT, "unit": UNIT,
        "item": ITEM, "story": STORY, "ui": UI, "event": EVENT,
    }

    os.makedirs(REVIEW_DIR, exist_ok=True)
    missing = []
    buckets: dict[str, list] = {c: [] for c in CAT_ORDER}
    seen: dict[str, str] = {}
    for cat, block in blocks.items():
        for key in parse_block(block):
            if key in seen:
                continue  # 同一词只归第一次出现的类别
            found = idx.get(key)
            if not found:
                missing.append(f"{cat}\t{key}")
                continue
            seen[key] = cat
            buckets[cat].append((key, found))

    # 语料兜底：术语文件里没抽到的核心词（可与既有条目合并成"一词多译"）
    existing = {(k, r["cn"]) for c in CAT_ORDER for k, rs in buckets[c] for r in rs}
    for cat, adds in CORPUS_ADD.items():
        for en, hint in adds:
            key = en.lower()
            rec = corpus_lookup(key, en, hint, by_src, by_en)
            if not rec:
                missing.append(f"{cat}\t(en){en}")
                continue
            if (key, rec["cn"]) in existing:
                continue
            merged = False
            for i, (k2, rs2) in enumerate(buckets[cat]):
                if k2 == key:                      # 与既有条目合并 → 形成"一词多译"
                    buckets[cat][i] = (k2, rs2 + [rec])
                    merged = True
                    break
            if not merged:
                seen[key] = cat
                buckets[cat].append((key, [rec]))
            existing.add((key, rec["cn"]))

    # 按类别内最高频降序，便于阅读
    for c in CAT_ORDER:
        buckets[c].sort(key=lambda kv: (-kv[1][0]["hits"], kv[0]))

    with open(os.path.join(REVIEW_DIR, "missing.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(missing) + ("\n" if missing else ""))

    total = sum(len(v) for v in buckets.values())
    lines = [
        "# Limbus Company 权威术语表",
        "",
        "> **数据来源**：游戏官方术语文件（`BattleKeywords.json`、`UnitKeyword.json`、",
        "> `Enemies*.json`、`Skills*.json`、`EGOGift*.json`、`AbnormalityGuides.json`、",
        "> `StageNode*.json`、`Passives*.json`、`Items.json` 等）与**零协会官方汉化**",
        "> 按 `id` 逐条对齐后的结果。中文侧是**既有权威译法**，不是机器翻译。",
        ">",
        "> **用法**：翻译新文本时先查本表；本表没有的专名，用 "
        "`python3 tools/pm_lib.py grep '<词>' -l cn` 在语料里找既有译法；",
        "> 确实找不到再自拟，并在提交说明里标注。",
        ">",
        "> **一致性铁律**：同一英文全篇必须用同一中文；若本表标注「一词多译」，",
        "> 按备注里的区分条件选择，不要自行统一。",
        ">",
        "> 生成脚本：`tools/curate_glossary.py`（可复现）。",
        "",
        "## 目录",
        "",
    ]
    for c in CAT_ORDER:
        anchor = CAT_TITLES[c].replace("、", "").replace(" ", "-")
        lines.append(f"- [{CAT_TITLES[c]}](#{anchor})（{len(buckets[c])} 条）")
    lines.append("")
    lines.append(f"**共 {total} 条词条。**")
    lines.append("")

    for c in CAT_ORDER:
        items = buckets[c]
        if not items:
            continue
        lines.append(f"## {CAT_TITLES[c]}")
        lines.append("")
        lines.append("| English | 中文 | 备注/来源 |")
        lines.append("| --- | --- | --- |")
        for key, rws in items:
            cn = cn_cell(rws)
            note = note_for(key, rws)
            if not note:
                note = rws[0]["src"].replace(".json", "") or "—"
            en = rws[0]["en"]
            lines.append(f"| {en} | {cn} | {note} |")
        lines.append("")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print(f"词条 {total} 条 -> {OUT}")
    for c in CAT_ORDER:
        print(f"  {CAT_TITLES[c]:22s} {len(buckets[c]):4d}")
    if missing:
        print(f"\n[!] {len(missing)} 个 INCLUDE 词条在语料中未找到（见 "
              f"{os.path.join(REVIEW_DIR, 'missing.txt')}）：")
        for m in missing:
            print("   ", m)

    if "--review" in sys.argv:
        for c in CAT_ORDER:
            print(f"\n########## {CAT_TITLES[c]} ##########")
            for key, rws in buckets[c]:
                cn = " / ".join(r["cn"] for r in rws)
                print(f"{rws[0]['hits']:7d} | {rws[0]['en'][:44]:44s} | {cn[:30]}")


if __name__ == "__main__":
    main()
