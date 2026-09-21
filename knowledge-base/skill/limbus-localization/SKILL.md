---
name: limbus-localization
description: Use when translating, retranslating, polishing, verifying, packaging, or installing the Limbus Company Chinese localization in this workspace (漢化 / LLC_zh-CN / 零协会 / LimbusLocalize / 边狱巴士汉化) — any work on `_kb/patch_v2/`, StoryData/RPGSystem text, the terminology base, or the GitHub patch repo. Covers the whole loop from "game updated, what's new" through "translated, verified, packaged, installed".
whenToUse: The user says things like 游戏更新了、翻译新文本、找新增内容、重译、润色、更新补丁、装补丁、查术语、角色语气不对、术语不一致、与零协对齐, or asks to package/publish the patch. Also use it when a new 零协会 pack appears in the workspace and scope must be recomputed.
---

# Limbus Company 汉化（本工作区专用）

## 0. 铁律：**别被「0 问题」骗了**

本会话有 **4 次**工具报「0 问题 / ✅ 通过」而实际什么都没查。每次都是同一类原因：
**路径指错、目标集合为空、判据太粗** —— 而工具照样打印绿灯。

> **凡是得到「0 问题」，必须先用已知的坏样本验证工具真的能报出来。**
> 否则那个 0 可能只是工具坏了。

| 发生过的假通过 | 真相 |
| --- | --- |
| `check_established_terms.py` 报「不一致 0」 | 用**相对路径**，从 `_kb` 跑会比到空集合 → 改绝对路径后变 347 |
| `verify_retrans.py --all` 报「错误 0 / 警告 0（**0 个文件**）」 | patch 目录名不对，一个文件都没检查 → 已加硬断言，目标为空直接退出 2 |
| `scope.py` 报「没有缺口」 | 判据只比**记录数**，测不出「组内少一条对话」与「字段留空」 → 改递归后抓出 134 条真实漏译 |
| 手写红线脚本报「改动 0 处」 | 把「补丁缺字段」误当改写；位置对齐写错又会漏报 |

配套纪律：
- **任何「数字」类结论都要能复现**：写清命令、写清目录、写清比的是哪两个东西。
- **不要写死零协包版本号**（零协每次更新都换目录名）。所有工具已改为自动选 `version` 最大的包。
- **不要在翻译脚本里用 `str()` 转 id**（§4.1 Python 3.14 陷阱），并且**断言改动条数**，防静默零改动。

---

## 1. ⭐ 两条裁决线（翻译前必须背下来）

| 维度 | 以谁为准 | 管什么 |
| --- | --- | --- |
| **文风** | **零协** | 句长节奏、书面／口语度、敬语与自称、标点习惯（少破折号）、专有格式（良秀缩写「汉字·汉字」） |
| **术语** | **零协** | 专名、状态名、技能句式、机制用语、品牌名 |
| **语义** | **韩文** | **到底说了什么**：信息量、指代对象、否定与否、程度、因果、说话人 |

> **用零协的词，说韩文的话。**
> 判定顺序：先看韩文定「说了什么」，再用零协的词汇与句式说出来 —— **不能反过来**。

**为什么语义不能跟零协**：零协自己也会压缩、也会为顺口改写。实测两处真丢信息：
- `S1002B#2` 韩文有「**从罗佳口中**」，零协中文只写「那人像是听到了某个陌生的词语似的」
- `S1005B#3` 韩文骂的是「**赫尔曼那帮蠢货**」，零协中文泛化成「这种地方」

照抄零协的语义 = 照抄它偶发的丢信息。详见 `workflow/重译手册.md §0.6b`。

**对应关系**：`重译手册 §0.6`（韩 > 英）管「谁是源」，`§0.6b`（文风术语跟零协、语义跟韩文）管「怎么落笔」。

---

## 2. 目录结构（六个位置）

| 位置 | 是什么 |
| --- | --- |
| `_kb/patch_v2/` | **补丁的唯一真源**。所有改动都改这里 |
| `LimbusLocalize_latest*/` | 零协基准包（**工具自动取版本最大的**，不要写死名字） |
| `Limbus-zh-CN-patch/` | GitHub 仓库（`patch/` 是 `patch_v2` 镜像 + `knowledge-base/`） |
| `~/.local/share/Steam/steamapps/common/Limbus Company/LimbusCompany_Data/Lang/LLC_zh-CN/` | 游戏安装目录 |
| `LLCCN-Font/` | **中文字体**（零协包不含字体，必须单独装） |
| `~/.local/share/Steam/.../Assets/Resources_moved/Localize/{kr,en,jp}/` | 官方原版文本（**源语言在这**） |

`_kb/` 下关键资料：

| 路径 | 用途 |
| --- | --- |
| `workflow/与零协差距教材.md` | ⭐⭐开工前必读：差距画像与操作规则 |
| `workflow/重译手册.md` | 重译规范（§0.5 pos≠id、§0.6 韩>英、§0.6b 文风术语跟零协·语义跟韩文、§0.7 并发、§0.8 勿磨平零协句式） |
| `workflow/通读润色手册.md` | 第二轮润色规范 |
| `workflow/更新与排障.md` | §0.9b 合并机制、§0.9c 语义复核、§0.9d 工具可信度、§2 闪退排查、§6 开工清单 |
| `workflow/零协新版译名映射.md` | 零协译名对照（品牌名已意译） |
| `terms/confirmed_pairs.tsv` | ⭐**Tier-1 依据**：同现实证配对 |
| `terms/glossary_all.clean.tsv` | Tier-2：清理后术语表 |
| `terms/术语表.md` | Tier-3：分类权威表 |

---

## 3. ⭐ 游戏更新后的标准流程（七步，本次已用合成场景全流程排练验证）

### 第 0 步：体检
```bash
cd /home/shb/文档/汉化/_kb
python3 tools/doctor.py
```
报基准包版本、补丁 JSON 合法性、游戏安装、术语与语料缓存、能否开工。**报错先修它。**

### 第 1 步：更新零协基础包（不先做，后面全白做）
1. 下载最新零协包，解包到工作区（目录名形如 `LimbusLocalize_latest2026xxxx`）
2. **不要覆盖/删除旧包** —— 工具按 `Info/version.json` 的 `version` 自动取最大的
3. 记录版本号：
   ```bash
   for p in ../LimbusLocalize_latest*/LimbusCompany_Data/Lang/LLC_zh-CN/Info/version.json; do
     echo "$p: $(tr -d '\n ' < "$p")"; done
   ```

### 第 2 步：重建语料（⚠️ 必须先删索引缓存）
```bash
rm -f data/_file_index.json          # ← 关键！不删会整块漏掉新内容（踩过）
python3 tools/pm_lib.py build
python3 tools/export_corpus.py
rm -f data/_align.pkl
python3 tools/align_index.py build
python3 tools/extract_confirmed_pairs.py    # 重抽实证配对（会自动转义换行）
python3 tools/audit_glossary.py --stats --save && python3 tools/clean_glossary.py
```
**验收**：`corpus.jsonl` 里 cn 行数与 kr 接近（重建后若 cn 少几千行 = 索引缓存没删干净）。

### 第 3 步：先合并（消除与零协的版本漂移）
零协每次更新都会**重译一批旧内容**。补丁若继续用旧译覆盖，用户装了反而比只用零协更旧。
```bash
python3 tools/merge_zeroasso.py --dry-run    # 先看会改多少
python3 tools/merge_zeroasso.py              # 正式合并（写报告，--revert 可回滚）
```
裁决规则：**零协有译文的一律采用零协；零协为空、零协缺记录处保留我们的。**

三个必踩的坑（`更新与排障 §0.9b`）：
1. **必须递归进 `texts`/`steps`/`levelList`** —— RPG 正文是 `[{index,speaker,text}]` 对象数组，
   只合并顶层字符串会漏掉**全部对话**（第一次就漏了 973 条）
2. **`id: null` 的记录会落进同一个键桶**（`S1004B`/`S1005B`），桶内对齐必须用**整表下标**
3. **`id`/`key`/`index`/`level` 等定位字段一律以补丁为准**，合并绝不能动

**验收**：`git diff --stat` 里改了哪些文件应≈零协重译过的文件数；残余差异应能被红线检查覆盖。

### 第 4 步：⭐ 算范围（找「新增的、零协还没译的」）
```bash
python3 tools/scope.py                 # 四类缺口 + 逐条漏译清单
python3 tools/scope.py --since         # 只看「游戏里有、零协没有」的部分
python3 tools/scope.py --only StoryData --top 40
```

⚠️ **不要假设新内容还在上次那批文件里**。新增可能出现在 StoryData、RPGSystem、UI、
道具、语音、被动……任何位置。`scope.py` 以**官方 en 的文件列表**为权威逐文件比对
「en / kr / 零协 / 本补丁」，所以位置事先未知也能找出来。

| 类别 | 含义 | 该怎么做 |
| --- | --- | --- |
| `A 游戏有 / 零协无此文件` | 零协压根没建这个文件 | **全译** |
| `A0 游戏有 / 零协是空占位` | 零协建了文件但是 `{}` | **全译**，这是「游戏刚更新」的典型信号 |
| `B 零协有但未译完` | 递归文本条数 en > 零协 | **只补差额** |
| 无缺口 | 零协已覆盖 | **不要自己译**，用了反而偏离零协 |

**真正的工作清单**：`terms/_review/scope_untranslated.tsv`，逐条给出零协漏了哪条、漏在哪个字段
（`零协缺此记录` / `零协缺此条目/字段`，字段路径形如 `texts[1].text`）。

> 判据是**递归可译文本条数**，不是记录数 —— 记录数测不出「组内少一条对话」。
> 实测本次工作区因此多抓出 3 个文件 / 约 130 条真实漏译（`P10705.json` 零协只译了 36/72）。
> 本文档 §0「假通过」表的第 3 行就是这个教训。

**源语言标记**：每行末尾 `源=KR(n)` 或 `源=EN(⚠无韩文)`。带 `⚠无韩文` 的说明官方还没出韩文
（常见于 `UserBanner-*`、`UserTicket-*`），此时退而用英文，并留意英文的七类固有错误（`重译手册 §0.6`）。

**建骨架**（A 类文件按官方 en 结构建进补丁）：
```bash
python3 tools/scope.py --add-missing          # 默认只列计划
python3 tools/scope.py --add-missing --yes    # 确认后写入
```
⚠️ **默认不写，必须 `--yes`** —— 基准包指错时 A 类会膨胀成「几乎整个官方 en 目录」，
一次写出几千个文件（排练时误操作过一次，写了 2147 个）。已存在的补丁文件**绝不覆盖**。

### 第 5 步：译（按文件类型选工具与「翻译单位」）

| 文件类型 | 导出上下文 | **翻译单位** |
| --- | --- | --- |
| `StoryData/*.json` | `python3 tools/ctx_dump.py StoryData/X.json --out /tmp/x.txt` | **对话回合**（看说话人序列 + 相邻条目） |
| `RPGSystem/rpg-loc-dialogue-*.json` | `python3 tools/rpg_dump.py RPGSystem/X.json --out /tmp/x.txt` | **一组（`key`）** |
| `RPGSystem/rpg-loc-item/npc/quest/location/*.json` | 同上 | 单条（同文件内保持一致） |
| 机制/UI/技能/被动 | 直接读 | 单条，套 `style/机制句式模板.md` |

**译前必读**：① `与零协差距教材.md`（三大病：叙事爱加戏／对话缩过头／破折号滥用）
② `style/角色/<说话人>.md` ③ 术语三级依据（§5）。

### 第 6 步：两轮审校（顺序不可颠倒）
1. **带上下文重译** —— 修**语义**（回应关系、比喻、反讽、指代、漏译、半句跨条）：`重译手册.md`
2. **通读润色** —— 修**读不顺**（跟英文被撑长、漏信息、生硬句式）：`通读润色手册.md`

先「意思对」，再「读得顺」。第二轮**务必先读手册**，否则会按个人偏好把零协的正式文风磨平
（`所…的` 零协用 3169 次、`对于` 239 次 —— 那是这个体裁的正常文风，不是病）。

**语义复核**（§1 裁决线的落地）：合并只是「不脱节」，语义仍要对着韩文过一遍。
```bash
python3 tools/sem_check.py --save      # 弱筛子：排可疑项
```
> ⚠️ **它测不出「句子通顺但少说了内容」**。实测两个已知真问题都拿 **0 分**
> （`S1002B#2`、`S1005B#3`）。试过「韩文:英文体量比」「中文:韩文长度比」也抓不到。
> **语义复核的最终手段永远是人对着韩文读**，筛子只负责把可疑的排到前面。

**⚠️ 改必须改在 `_kb/patch_v2/`**：现在多数文件与零协逐字相同，
改在游戏目录或别处，下次合并又被零协译文盖回去。

### 第 7 步：验收（每次改完都跑）
```bash
python3 tools/verify_retrans.py --all             # 必须 错误 0；且末尾必须出现「✅ 红线」行
python3 tools/check_speech_context.py             # 口吻：0 告警
python3 tools/polish_scan.py --story --limit 30   # 挑可疑长句人工过
python3 tools/check_established_terms.py          # 术语线索（⚠️ 参考用，见 §6）
```
**验收的三个硬条件**：
1. `verify_retrans --all` 报的文件数**等于补丁实际文件数**（不是 0）
2. 末尾出现 `✅ 红线：未改写零协任何已有原文`
3. 合并过的批次，补丁与零协基准的**残余差异能被解释**（要么零协没有，要么零协留空）

---

## 4. 写回的三条铁律

### 4.1 绝不用正则清洗 JSON
```python
import json
j = json.load(open(p, encoding='utf-8-sig'))
for r in j['dataList']:
    if isinstance(r, dict) and r.get('id') in fix:      # ⚠️ 用原始类型，不要 str()
        assert r['content'] == expected[r['id']], '原文不符，已被他人改动，中止'   # 并发保险
        r['content'] = fix[r['id']]; n += 1
assert n == len(fix), f'期望 {len(fix)} 实际 {n}'         # 防静默零改动
json.dump(j, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
```
- **⚠️ Python 3.14 陷阱**：`int` 键字典不接受 `str` 查找，`'1' in {1:'a'}` **静默返回 False**。
- **⚠️ `ctx_dump` 的 `posN` ≠ `id`**：有 `id: null` 记录时会错位（`S1004B`/`S1005B`），**按真实 `id` 写回**。
- **⚠️ 并发**：多代理并行时原文精确匹配→不符即中止；汇报时把跳过的单列为「已被他人处理」。

### 4.2 只改该改的字段
`teller` / `title` / `place` / `displayName` **也是要译的显示名**，别只改正文；
`key` / `index` / `speaker` / `model` **不动**。

### 4.3 `id` 可能重复
同文件内同 `id` 的重复记录**要一起改**（用列表遍历，不要建 id 字典）。

---

## 5. 术语三级依据（按置信度）

```
① terms/confirmed_pairs.tsv              （同现实证配对，最高置信）
② terms/glossary_all.clean.tsv           （清理后术语表）
③ terms/术语表.md                        （分类权威表）
④ python3 tools/pm_lib.py grep <词> -l cn （直接查零协语料）
```
**判据**：查零协语料里哪个写法是主流，用主流的那个：
```bash
BASE="$(ls -d ../LimbusLocalize_latest* | sort | tail -1)/LimbusCompany_Data/Lang/LLC_zh-CN"
grep -rho <词> "$BASE" | wc -l
```

---

## 6. ⚠️ 别信这两个脚本的「干净」

| 工具 | 能干什么 | 不能干什么 |
| --- | --- | --- |
| `sem_check.py` | 排**机械**疑点（行数少了／长度比过低／数字·否定·引号对不上，已剥标签） | **测不出语义丢信息**（两个已知真问题 0 分）→ 必须人对着韩文读 |
| `check_established_terms.py` | 给术语**线索** | 在**与零协逐字相同**的文件上仍报 85 条，逐条核实 **85/85 全误报**（`Head` 从 `Heads Hit` 学来）。**不是守门器** |

---

## 7. 常见故障与处置

| 症状 | 处置 |
| --- | --- |
| **游戏闪退** | `更新与排障 §2` 排查优先级表 + §3 二分定位法。先查游戏侧 JSON、目录结构、字体、基准包版本 |
| **某语言整块缺失**（重建语料后 cn 比 kr 少很多） | `_file_index.json` 是缓存，**重建语料必须先删它** |
| **TSV 出现无制表符的碎片行** | 文本含真换行，写出前转义 `\n` |
| **工具报「0 问题」** | 见 §0。先用坏样本验证工具真能报出来，再信这个 0 |
| **术语不一致** | 查零协语料哪个写法是主流（§5），用主流的 |
| **补丁装了没效果** | 查 `Lang/config.json` 是否 `{"lang":"LLC_zh-CN"}`、字体是否就位 |

---

## 8. 并行翻译的标准分派方式

工作量大时用子代理并行。**每个子代理的 prompt 必须自包含**（它看不到本对话），至少含：

1. `cd /home/shb/文档/汉化/_kb`
2. **先读 `workflow/与零协差距教材.md`（§1–§5）与 `重译手册 §0.6b`**
3. 指定文件 + 用哪个 dump 工具导出上下文（`ctx_dump.py` / `rpg_dump.py`）
4. **两条裁决线**（文风术语跟零协、语义跟韩文）+ 三大病 + 术语三级依据 + 红线（§3 第 5 步、§4）
5. 自检命令（`verify_retrans.py <文件>` 必须 0 错误）
6. 汇报：每条给出 `文件#id`、韩文、原译、新译、属于哪类问题、为什么
7. **「改动宜少不宜多」**：每个文件 5–30 条正常，超过 50 条说明判据放宽了

**分派原则**：
- 一个代理**不要**同时负责两个以上会互相影响的文件（避免并发覆盖）
- 文件按体量分组，最大的单派
- 全部完成后**统一做一次跨文件术语扫描**（保证品牌名/称呼一致）

---

## 9. 发布（六步）

```bash
cd /home/shb/文档/汉化
# ① 确认游戏没在运行
pgrep -fa Limbus || echo 未运行
# ② 同步到游戏
cp -r _kb/patch_v2/. "$HOME/.local/share/Steam/steamapps/common/Limbus Company/LimbusCompany_Data/Lang/LLC_zh-CN/"
# ③ 同步到仓库（用 python/cp，不要 rsync --delete，避免误删仓库独有文件）
python3 - <<'PY'
import filecmp, os, shutil
src, dst = '_kb/patch_v2', 'Limbus-zh-CN-patch/patch'
for r, d, fs in os.walk(src):
    for f in fs:
        s = os.path.join(r, f); t = os.path.join(dst, os.path.relpath(s, src))
        if not os.path.exists(t) or not filecmp.cmp(s, t, shallow=False):
            os.makedirs(os.path.dirname(t), exist_ok=True); shutil.copy2(s, t)
PY
# ④ 一致性核对（都必须是 0）
LANG=C diff -rq _kb/patch_v2 Limbus-zh-CN-patch/patch | wc -l
# ⑤ 提交推送
cd Limbus-zh-CN-patch && git add -A && git commit -F - <<'MSG'
...（写清改了什么、为什么、验收结果）...
MSG
git fetch -q origin && git rebase -q origin/main && git push -q origin main
# ⑥ 重建发布包（文件名带当日日期；旧包删掉避免混淆）
cd .. && rm -f Limbus汉化补丁+知识库_v*.zip
zip -qr "Limbus汉化补丁+知识库_v$(date +%Y%m%d).zip" \
  Limbus-zh-CN-patch/patch Limbus-zh-CN-patch/knowledge-base \
  Limbus-zh-CN-patch/README.md Limbus-zh-CN-patch/LICENSE Limbus-zh-CN-patch/docs \
  -x '*/__pycache__/*' '*.pyc' '*/terms/_review/merge_zeroasso.tsv' '*/terms/_review/sem_check.tsv'
```

**知识库同步**（改了文档/术语/工具时）：
```bash
K=Limbus-zh-CN-patch/knowledge-base
cp _kb/workflow/*.md $K/workflow/; cp _kb/terms/*.tsv $K/terms/; cp _kb/tools/*.py $K/tools/; cp _kb/00_索引.md $K/
cp .dsh/skills/limbus-localization/SKILL.md $K/skill/limbus-localization/
```
> `data/corpus.jsonl`、`_align.pkl`、`words/voice_samples.md` **不入库**（体积大、可再生）。

---

## 10. 「这次做完了」的定义

- [ ] `doctor.py` 环境就绪
- [ ] 语料已重建且 cn 行数与 kr 相当
- [ ] `merge_zeroasso.py` 已跑（若零协有更新）
- [ ] `scope.py` 的缺口清单已全部处理：A/A0 全译、B 按 `scope_untranslated.tsv` 逐条补
- [ ] `verify_retrans.py --all` 错误 0 **且文件数 = 补丁文件数**、**且末尾有「✅ 红线」**
- [ ] 语义按韩文过了一遍（不依赖脚本判绿）
- [ ] 术语与零协一致（§5 三级依据查过）
- [ ] 游戏目录 / 仓库 / 发布包三者一致
- [ ] 提交已推送，README 与发布包版本号已更新

---

## 11. 一句话记法

> **文风术语跟零协，语义跟韩文；一行原文一行译文；改动改在 `patch_v2`；
> 任何「0 问题」先用坏样本验工具；改完必跑 `verify_retrans --all`。**
