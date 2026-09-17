# 边狱巴士 第十章 第一周 汉化分享

《Limbus Company》第十章第一周内容的个人 AI 汉化补丁与翻译知识库。感觉有用还望star一下

> 演示文稿：`docs/边狱巴士第十章.pptx`
> 详细安装说明（中文）：`docs/说明.md`，当然只看这个其实也够了

---

## 说明与叠甲

- 本汉化**全程使用 deepv4.1-flash 模型**进行翻译。
- 建立在 **「都市零协会汉化组」的过往汉化**、月亮计划过往游戏汉化数据基础之上。
- **只做分享，并拒绝任何可能的商业化行为。**
- 因 UP 文化水平有限，且存在术语如 **以实玛利·Le Rouge 精品店** 难以翻译为中文，故导致**汉化不完全**，希望各位仅把本汉化当作**尝鲜使用**，之后**务必重新使用都市零协会提供的汉化**。
- 本补丁在 **Ubuntu 26.04** 成功运行。
- **本汉化未进行任何测试，可能出现任何文字显示问题。**

---

## 内容一览

| 目录 | 作用 | 使用者 |
| --- | --- | --- |
| `patch/` | **汉化补丁**：25 个 json，补齐零协会汉化包缺失的最新内容 | 想玩游戏的人 |
| `knowledge-base/` | **翻译知识库**：术语表、角色文风指南、世界观专名、翻译流程与工具 | 想继续翻译的人 |
| `docs/` | 演示文稿与详细说明 | — |

`patch/` 里的 25 个文件是**完整可用的整份文件**，不是差异片段。

---

## 一、安装补丁

### 前提

游戏目录下要**已经有**零协会汉化包（即已存在 `Lang/LLC_zh-CN/` 目录）。
若还没装，请先按官方指南安装：<https://www.zeroasso.top/docs/install/install>

### 游戏目录在哪

打开 Steam → 库 → 右键 **Limbus Company** → 管理 → **浏览本地文件**。
目录里应有 `LimbusCompany_Data`。补丁要放的位置是：

```
LimbusCompany_Data/Lang/LLC_zh-CN/
```

### 安装

把 `patch/` 里的 **25 个 json 文件**复制到上面的 `LLC_zh-CN` 目录，提示覆盖时选**覆盖**。

**Windows（资源管理器）**

1. 打开 `patch` 文件夹，全选（Ctrl+A）
2. 复制（Ctrl+C）
3. 进入 `LimbusCompany_Data\Lang\LLC_zh-CN\`
4. 粘贴（Ctrl+V），选择「替换目标中的文件」

**Linux / Steam Deck**

```bash
cp -r patch/. "/你的路径/steamapps/common/Limbus Company/LimbusCompany_Data/Lang/LLC_zh-CN/"
```

### 装完后

- 直接启动游戏即可，**不需要**在游戏里重新选语言。
- 生效范围：商城/编队里新人格的**技能名与描述**、被动、状态关键词、章节名、抽取标题、赛季横幅、战斗语音气泡、剧情内 NPC 代号等。

### 卸载 / 回滚

用零协会官方汉化包里的同名文件覆盖回去即可（25 个文件同名）。

更彻底的回滚（若你只想删掉整个汉化）：

```bash
rm -rf "…/LimbusCompany_Data/Lang"
```

---

## 二、翻译工作流（演示提纲）

1. **翻译实机演示** —— 见 `docs/边狱巴士第十章.pptx`
2. **安装说明** —— 见上方「安装补丁」
3. **翻译工作流** —— 见 `knowledge-base/workflow/翻译流程.md`

基本思路：以官方 **英 / 韩 / 日** 原版文本与零协会既有汉化做**四语对齐**，
建立术语与文风基线后，用 AI 批量翻译，再用脚本校验标记、占位符与漏译。

---

## 三、使用知识库（继续翻译）

入口是 `knowledge-base/00_索引.md`。

主要文档：

| 路径 | 内容 |
| --- | --- |
| `knowledge-base/00_索引.md` | 总索引与「必读铁律」 |
| `knowledge-base/terms/术语表.md` | 权威术语表（约 1000 条，含「一词多译」区分说明） |
| `knowledge-base/terms/常用表达表.md` | 高频句式与 UI 文案 |
| `knowledge-base/style/角色口吻速查.md` | 各角色口吻速查（自称、称呼、标点密度） |
| `knowledge-base/style/角色/*.md` | 各罪人的完整文风指南（含中英实例） |
| `knowledge-base/style/机制句式模板.md` | 技能/被动的高频句式模板 |
| `knowledge-base/worldview/共享世界观.md` | 都市 / 巢 / 翼 / 首脑 / 手指 等设定术语 |
| `knowledge-base/worldview/专名对照.md` | 人名、组织、异想体、E.G.O 专名表 |
| `knowledge-base/workflow/翻译流程.md` | 从检索到交付的完整 SOP |

工具（`knowledge-base/tools/`，需要 Python 3）：

```bash
# 看某文件的中英韩日四语逐条对照
python3 tools/pm_lib.py show MainUIText.json

# 在中文语料里搜既有译法
python3 tools/pm_lib.py grep 事务所 -l cn

# 校验译文（标记/占位符/漏译）
python3 tools/verify_output.py <文件名>
```

> 工具依赖 `knowledge-base/data/` 下的索引文件。语料缓存（约 160 MB，可由 `tools/export_corpus.py` 重新生成）**未包含**在本仓库内。

---

## 四、本次补丁修了什么

零协会汉化包落后于游戏版本，以下内容「英文 / 韩文有、中文缺失」，游戏里只能显示英文。本补丁全部补齐：

| 文件 | 补的条数 | 内容 |
| --- | ---: | --- |
| `Skills_personality-04.json` | 5 | 良秀 · Haute Couture::Le Noir鞋履馆 的全部技能 |
| `Skills_personality-08.json` | 5 | 以实玛利 · Haute Couture::Le Rouge精品店 的全部技能 |
| `Passives.json` | 8 | 上述两个人格的新被动（含风味文本） |
| `BattleKeywords.json` / `Bufs.json` | 各 6 | 新状态：华达呢大衣、保存、Armure Éveillée、搏动、更衣室、全面改造 |
| `Personalities.json` / `Personality_Get_Condition.json` | 2 / 4 | 人格名称与获取条件 |
| `ScenarioModelCodes-AutoCreated.json` | 16 | 剧情内 NPC 代号 |
| `BattleSpeechBubbleDlg.json` | 16 | 新人格战斗语音气泡 |
| 其余 14 个文件 | 37 | 章节名、抽取标题、赛季横幅、登录提示、E.G.O 名称等 |

质量说明：技能与被动译文按官方既成句式（如 `Inflict N [X]` → `使目标增加N级[X]强度`）；
`<color=#...>`、`<style="highlight">`、`<size=95%>`、`[ChargeNoirAlly]` 等标记与引擎标签
均与英文源**逐字符一致**。

---

## 许可与致谢

- 补丁内容基于**都市零协会汉化组**译文（未改动其原文，仅补齐其缺失条目），
  遵循其 **CC BY-NC-SA 4.0** 协议：署名、非商业性使用、相同方式共享。
- 感谢零协会汉化组开源。原始汉化请见 <https://www.zeroasso.top>
- 本仓库仅为个人分享，**禁止任何商业化行为**。
