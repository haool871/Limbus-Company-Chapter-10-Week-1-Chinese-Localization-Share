---
name: limbus-localization
description: Use when translating, retranslating, polishing, verifying, packaging, or installing the Limbus Company Chinese localization in this workspace (漢化 / LLC_zh-CN / 零协会 / LimbusLocalize / 边狱巴士汉化) — any work on `_kb/patch_v2/`, StoryData/RPGSystem text, the terminology base, or the GitHub patch repo. Covers the whole loop from "game updated, what's new" through "translated, verified, packaged, installed".
whenToUse: The user says things like 翻译新文本、重译、润色、更新补丁、装补丁、查术语、角色语气不对、术语不一致、与零协对齐, or asks to package/publish the patch. Also use it when a new 零协会 pack appears in the workspace and scope must be recomputed.
---

# Limbus Company 汉化（本工作区专用）

## 0. 开工前必做（四条，不做会白干）

```bash
cd /home/shb/文档/汉化/_kb
```

1. **先跑体检**（30 秒，能省几小时）：
   ```bash
   python3 tools/doctor.py
   ```
   报基准包版本、补丁 JSON 合法性、游戏安装状态、术语与语料缓存，并给出「能不能开工」的结论。
   **它报错就先修它，别往下走。**
2. **读 `workflow/与零协差距教材.md`** —— 实测出的差距画像与操作规则，是缩短与零协差距的最短路径。
3. **确认基准包版本**：工具会**自动选版本号最大的零协包**，不要在任何命令里写死版本号
   （零协每次更新都换目录名）。需要指定时用 `LIMBUS_BASE_PACK=<目录名>` 或 `scope.py --base <路径>`。
4. **确认游戏没在运行**（装补丁时才需要）：`pgrep -fa Limbus || echo 未运行`

---

## 1. 目录结构（先记住这五个位置）

| 位置 | 是什么 |
| --- | --- |
| `_kb/patch_v2/` | **补丁的唯一真源**（129 个文件）。所有改动都改这里 |
| `LimbusLocalize_latest20260921/` | **现行零协基准包**（含 Canto 10）。术语与译法的权威 |
| `Limbus-zh-CN-patch/` | GitHub 仓库（`patch/` 是 `patch_v2` 的镜像，另有 `knowledge-base/`） |
| `~/.local/share/Steam/steamapps/common/Limbus Company/LimbusCompany_Data/Lang/LLC_zh-CN/` | 游戏安装目录 |
| `LLCCN-Font/` | **中文字体**（零协包不含字体，必须单独装） |

`_kb/` 下的关键资料：

| 路径 | 用途 |
| --- | --- |
| `workflow/与零协差距教材.md` | ⭐⭐开工前必读 |
| `workflow/重译手册.md` | 重译规范（§0.5 pos≠id、§0.6 以韩文为准、§0.7 并发安全、§0.8 勿磨平零协句式） |
| `workflow/通读润色手册.md` | 第二轮润色规范 |
| `workflow/更新与排障.md` | 更新六步流程 + 闪退排查 + **语料重建正确顺序** + 下一批开工清单 |
| `workflow/零协新版译名映射.md` | 零协译名对照（品牌名已意译） |
| `terms/confirmed_pairs.tsv` | ⭐**Tier-1 依据**：同现实证配对（1866 条） |
| `terms/glossary_all.clean.tsv` | Tier-2：清理后术语表（6534 条） |
| `terms/术语表.md` | Tier-3：分类权威表 |

---

## 2. 步骤一：算出「真正需要译」的范围

**游戏更新后第一步永远是更新零协基础包**，否则算不出范围（很多内容零协已经译了）。

```
python3 tools/scope.py              # 全量扫描：四类缺口 + 逐条漏译清单
python3 tools/scope.py --since      # 只看「游戏里有、零协包没有」的部分
python3 tools/scope.py --only StoryData --top 40
python3 tools/scope.py --add-missing   # 把 A 类文件按官方 en 结构建进补丁（待译）
```

⚠️ **不要假设新内容还在上次那 129 个文件里。** 新增可能出现在 StoryData、RPGSystem、UI、
道具、语音、被动……任何位置。`scope.py` 以**官方 en 的文件列表**为权威逐文件比对
「en / kr / 零协 / 本补丁」，所以文件位置事先未知也能找出来。

**四类缺口**（报告直接给类名）：

| 类别 | 含义 | 该怎么做 |
| --- | --- | --- |
| `A 游戏有 / 零协无此文件` | 零协压根没建这个文件 | **全译**（先 `--add-missing` 建骨架） |
| `A0 游戏有 / 零协是空占位` | 零协建了文件但是 `{}` | **全译**，这是「游戏刚更新」的典型信号 |
| `B 零协有但未译完` | en 记录数 > 零协记录数 | **只补差额** |
| 无缺口 | 零协已覆盖 | **不要自己译**，用了反而偏离零协 |

**真正的工作清单**在 `terms/_review/scope_untranslated.tsv`：逐条给出零协漏了哪条记录、
漏在哪个字段（`零协缺此记录` / `零协该字段为空`）。`B` 类文件里大部分记录零协已经译好，
要译的往往只有几条——照单译，不要整篇重译。

**源语言标记**：每行末尾 `源=KR(n)` 或 `源=EN(⚠无韩文)`。带 `⚠无韩文` 的说明官方还没出韩文
（常见于 `UserBanner-*`、`UserTicket-*` 这类配置），此时退而用英文，并留意英文的七类固有错误
（`重译手册.md §0.6`）。

`--add-missing` **不会覆盖已存在的补丁文件**，可放心重复跑。

### 2.0 ⭐ 两条裁决线（翻译前必须背下来）

| 维度 | 以谁为准 | 管什么 |
| --- | --- | --- |
| 文风 | **零协** | 句长节奏、书面／口语度、敬语自称、标点习惯（少破折号）、专有格式（良秀缩写「汉字·汉字」） |
| 术语 | **零协** | 专名、状态名、技能句式、机制用语、品牌名 |
| **语义** | **韩文** | **到底说了什么**：信息量、指代对象、否定与否、程度、因果、说话人 |

**一句话：用零协的词，说韩文的话。**
判定顺序是先看韩文定「说了什么」，再用零协的词汇与句式说出来——不能反过来。
零协自己也会压缩、也会为顺口改写（实测 `S1002B#2` 丢了「从罗佳口中」、
`S1005B#3` 丢了「赫尔曼那帮蠢货」），照抄零协的语义 = 照抄它偶发的丢信息。
详见 `workflow/重译手册.md §0.6b`。

⚠️ **别指望脚本替你判语义**。实测「中文少说了内容」这类问题**测不出来**：
`tools/sem_check.py` 对那两个已知真问题都给 0 分。
它能可靠抓的只有机械项（行数少了、长度比过低、数字/否定/引号对不上）。
**语义复核的最终手段永远是人对着韩文读。**

### 2.1 ⚠️ 每次零协更新后，还要重跑一次「字段级合并」

零协每次更新都会**重译一批旧内容**。补丁若继续用旧译覆盖，用户装了补丁反而比只用零协更旧。
裁决规则：**零协有译文的一律采用零协；零协为空、零协缺记录处保留我们的。**

```
python3 tools/merge_zeroasso.py --dry-run   # 先看会改多少
python3 tools/merge_zeroasso.py             # 正式合并（写报告，可 --revert 回滚）
```

三个必踩的坑见 `workflow/更新与排障.md §0.9b`：① 必须递归进 `texts`/`steps`/`levelList`
（RPG 正文是对象数组，只合并顶层会漏掉全部对话）；② `id: null` 的记录要用**整表下标**对齐；
③ `id`/`key`/`index` 等定位字段一律以补丁为准，绝不能动。

**合并 ≠ 语义已复核。** 合并是「不再跟零协版本脱节」，语义仍要按 §2.0 用韩文复核：
零协中文相对韩文**少说了内容**的地方，按韩文补回来，**但词汇与句式仍用零协的**。
现在 120 个文件与零协逐字相同，所以**改必须改在 `_kb/patch_v2/` 里**，
否则下次合并又被零协译文盖回去。

---

## 3. 步骤二：译（按文件类型选工具与「翻译单位」）

| 文件类型 | 导出上下文 | **翻译单位** |
| --- | --- | --- |
| `StoryData/*.json` | `python3 tools/ctx_dump.py StoryData/X.json --out /tmp/x.txt` | **对话回合**（看说话人序列 + 相邻条目） |
| `RPGSystem/rpg-loc-dialogue-*.json` | `python3 tools/rpg_dump.py RPGSystem/X.json --out /tmp/x.txt` | **一组（`key`）** |
| `RPGSystem/rpg-loc-item/npc/quest/location/*.json` | 同上 | 单条（同文件内保持一致） |
| 机制/UI/技能/被动 | 直接读 | 单条，套 `style/机制句式模板.md` |

### 译前必读清单

1. **`workflow/与零协差距教材.md`** —— 三大病：① 叙事爱加戏 ② 对话缩过头 ③ 破折号滥用
2. **`style/角色/<说话人>.md`** —— 语气规范
3. **术语三级依据**：
   ```
   ① terms/confirmed_pairs.tsv          （同现实证配对，最高置信）
   ② terms/glossary_all.clean.tsv       （清理后术语表）
   ③ terms/术语表.md                    （分类权威表）
   ④ python3 tools/pm_lib.py grep <词> -l cn   （直接查零协语料）
   ```

### 核心操作规则（来自与零协的逐字段比对）

- **原文一行 → 译文一行**。不要加意象、比喻、心理补白。
  （我原来写「他本可以选择说出来……但他始终没有」是**原文没有的**）
- **对话保留句尾语气助词**（`吧`/`呢`/`吗`/`哦`）与**敬称**（`그분`→**那位大人**）。
- **破折号几乎不用**（零协同口径 0.48/千条，我 23.7/千条 → 差 50 倍）。
- **`<...>` 是但丁内心独白，保留半角尖括号**。
- **引擎方括号标记原样保留**（`[OnSucceedAttack]`），显示方括号要译（`[鸿璐]`）。
- **`<color=…>`/`<size=…>`/`<style=…>`/`<mark=…>`/`{0}` 逐字符不变**（`<i>`/`<b>`/`<u>`/`<s>` 可删）。

---

## 4. 步骤三：写回（三条铁律）

### 4.1 绝不用正则清洗 JSON
```python
import json
j = json.load(open(p, encoding='utf-8-sig'))
for r in j['dataList']:
    if isinstance(r, dict) and r.get('id') in fix:   # ⚠️ 用原始类型，不要 str()
        assert r['content'] == expected[r['id']], '原文不符，已被他人改动，中止'  # 并发保险
        r['content'] = fix[r['id']]; n += 1
assert n == len(fix), f'期望 {len(fix)} 实际 {n}'    # 防静默零改动
json.dump(j, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
```

- **⚠️ Python 3.14 陷阱**：`int` 键字典不接受 `str` 查找，`'1' in {1:'a'}` **静默返回 False**。
- **⚠️ `ctx_dump` 的 `posN` ≠ `id`**：有 `id: null` 记录时会错位，**按真实 `id` 写回**。
- **⚠️ 并发**：多代理并行时，原文精确匹配→不符即中止；汇报时把跳过的单列为「已被他人处理」。

### 4.2 只改该改的字段
`teller` / `title` / `place` / `displayName` **也是要译的显示名**，别只改正文；
`key` / `index` / `speaker` / `model` **不动**。

### 4.3 `id` 可能重复
同文件内同 `id` 的重复记录**要一起改**（用列表遍历，不要建 id 字典）。

---

## 5. 步骤四：两轮审校（顺序不可颠倒）

| 轮次 | 修什么 | 手册 |
| --- | --- | --- |
| **1. 带上下文重译** | **语义错误**：回应关系、比喻、反讽、指代、漏译、半句跨条 | `workflow/重译手册.md` |
| **2. 通读润色** | **读不顺**：跟英文被撑长、漏信息、生硬句式 | `workflow/通读润色手册.md` |

先保证「意思对」，再保证「读得顺」。第二轮**务必先读手册**，否则会按个人偏好把零协的正式文风磨平
（`所…的` 零协用 3169 次、`对于` 239 次 —— 那是正常文风，不是病）。

---

## 6. 步骤五：验收（每次改完都跑）

```bash
cd /home/shb/文档/汉化/_kb
python3 tools/verify_retrans.py --all        # 必须 错误 0（结构/标签/占位符/空译/禁用语/第一人称）
python3 tools/check_speech_context.py        # 口吻：0 告警
python3 tools/polish_scan.py --story --limit 30   # 挑出可疑长句人工过
python3 -c "import json,glob;[json.load(open(p,encoding='utf-8-sig')) for p in glob.glob('patch_v2/**/*.json',recursive=True)];print('JSON OK')"
```

**零协原文保护**（覆盖文件里基础包已有的记录，共享字段差异必须为 0）：
见 `workflow/更新与排障.md` §4.1 的脚本。

---

## 7. 步骤六：发布

```bash
cd /home/shb/文档/汉化
# ① 同步到游戏（先确认没在运行）
cp -r _kb/patch_v2/. "$GAME/"
# ② 同步到仓库
rsync -a --delete _kb/patch_v2/ Limbus-zh-CN-patch/patch/
# ③ 一致性核对（都必须是 0）
LANG=C diff -rq _kb/patch_v2 Limbus-zh-CN-patch/patch | wc -l
LANG=C diff -rq _kb/patch_v2 "$GAME" | grep -vc '^Only in'
# ④ 提交推送
cd Limbus-zh-CN-patch && git add -A && git commit -m "..." && git fetch -q origin main && git rebase -q origin/main && git push -q origin main
# ⑤ 重建发布包
cd .. && rm -f "Limbus汉化补丁+知识库_v20260917.zip"
zip -qr "Limbus汉化补丁+知识库_v20260917.zip" Limbus-zh-CN-patch/patch Limbus-zh-CN-patch/README.md Limbus-zh-CN-patch/docs Limbus-zh-CN-patch/knowledge-base Limbus-zh-CN-patch/LICENSE
```

**知识库也要同步**（改了文档/术语/工具时）：
```bash
K=Limbus-zh-CN-patch/knowledge-base
cp _kb/workflow/*.md $K/workflow/ ; cp _kb/terms/*.tsv $K/terms/ ; cp _kb/tools/*.py $K/tools/ ; cp _kb/00_索引.md $K/
```
> `data/corpus.jsonl` 与 `_align.pkl` **不入库**（`.gitignore` 已排除，体积大、可再生）。

---

## 8. 常见故障与处置

| 症状 | 处置 |
| --- | --- |
| **游戏闪退** | 见 `workflow/更新与排障.md` §2 的排查优先级表 + §3 二分定位法。先查游戏侧 JSON、目录结构、字体、基础包版本 |
| **某语言整块缺失**（重建语料后 cn 比 kr 少很多） | `_file_index.json` 是缓存，**重建语料必须先删它**（§0 顺序） |
| **TSV 出现无制表符的碎片行** | 文本含真换行，入库前转义 `\n`（见 `workflow/更新与排障.md`） |
| **术语不一致** | 查零协语料里哪个写法是主流：`grep -rho <词> $BASE | wc -l`，用主流的 |
| **代理互相覆盖** | 写回加「原文精确匹配→不符即中止」，并在汇报里单列跳过项 |
| **补丁装了没效果** | 查 `Lang/config.json` 是否 `{"lang":"LLC_zh-CN"}`、字体是否就位 |

---

## 9. 并行翻译的标准分派方式

工作量大时用子代理并行。**每个子代理的 prompt 必须自包含**（它看不到本对话），至少含：

1. 工作目录 `cd /home/shb/文档/汉化/_kb`
2. **先读 `workflow/与零协差距教材.md`**（§1–§5）
3. 指定文件 + 用哪个 dump 工具导出上下文
4. **三大病 + 术语三级依据 + 红线**（见本文 §3、§4）
5. 自检命令（`verify_retrans.py` 必须 0 错误）
6. 汇报要求：每条给出 `文件#id`、韩文、原译、新译、属于哪类问题、为什么
7. **「改动宜少不宜多」**：每个文件 5–30 条正常，超过 50 条说明判据放宽了

**分派原则**：
- 一个代理**不要**同时负责两个以上会互相影响的文件（避免并发覆盖）
- 文件按体量分组，最大的单派
- 全部代理完成后，**统一做一次跨文件术语扫描**（保证品牌名/称呼一致）

---

## 10. 一句话记法

> **零协怎么译，我就怎么译；原文一行，译文一行；术语先查 `confirmed_pairs.tsv`；改完必跑 `verify_retrans`。**
