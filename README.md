# 边狱巴士 第十章 第一周 汉化分享

《Limbus Company》第十章第一周内容的个人 AI 汉化补丁与翻译知识库。
感觉有用还望 star 一下 ⭐

> 演示文稿：`docs/边狱巴士第十章.pptx`

---

## 说明与叠甲

- 本汉化**全程使用 deepv4.1-flash 模型**进行翻译，建立在 **「都市零协会汉化组」的过往汉化**、月亮计划过往游戏汉化数据基础之上。
- **只做分享，拒绝任何可能的商业化行为。**
- UP 水平有限，且像 **以实玛利·Le Rouge 精品店** 这类术语难以译成中文，故**汉化不完全**。请当**尝鲜**用，之后**务必换回都市零协会的汉化**。
- 在 **Ubuntu 26.04** 测试可运行。**未经完整测试，可能出现文字显示问题。**

---

## 安装（三分钟）

> ## 📌 一句话说清怎么装
>
> ### 把 `patch` 里的东西**全选**，**放到** `LimbusCompany_Data/Lang/LLC_zh-CN/` **下**，弹窗选**覆盖**。
>
> 就这样。下面的步骤只是把这句话拆开细说。

---

### 第 0 步：先装好零协会汉化包

本补丁是**补丁**，不是完整汉化包。请先按官方指南装好零协会汉化：
<https://www.zeroasso.top/docs/install/install>

**装好的标志**：游戏目录里存在 `LimbusCompany_Data/Lang/LLC_zh-CN/` 这个文件夹。

> ⚠️ 没装过零协会包就直接放本补丁，游戏会缺一大堆文件。

### 第 1 步：找到游戏目录

Steam → 库 → 右键 **Limbus Company** → **管理** → **浏览本地文件**。

打开的文件夹里能看到 `LimbusCompany_Data`。

### 第 2 步：进到要放补丁的文件夹

依次进入：

```
LimbusCompany_Data  →  Lang  →  LLC_zh-CN
```

这个 `LLC_zh-CN` 就是**补丁要放进的地方**。

### 第 3 步：全选 → 放到 LLC_zh-CN 下 → 覆盖 ⭐关键步骤

打开仓库里的 `patch` 文件夹，它长这样：

```
patch/
├── Announcer.json              ┐
├── BattleKeywords.json         │
├── Skills_personality-04.json  │  散装 json 文件（61 个）
├── ……                          ┘
├── RPGSystem/                  ┐
├── StoryData/                  │  文件夹（4 个）
├── PersonalityVoiceDlg/        │
└── BattleAnnouncerDlg/         ┘
```

**⚠️ 不要去挑文件，也不用管哪个是哪个。**

**就三步：**

1. **全选** —— 在 `patch` 文件夹里按 **Ctrl + A**
2. **复制** —— **Ctrl + C**
3. **放到 LLC_zh-CN 下并覆盖** —— 进到第 2 步的 `LLC_zh-CN` 文件夹，按 **Ctrl + V**，弹窗选 **「替换目标中的文件」**

| 操作 | 在哪做 |
| --- | --- |
| **Ctrl + A**（全选） | 在 `patch` 文件夹里 |
| **Ctrl + C**（复制） | 同上 |
| **Ctrl + V**（粘贴到 `LLC_zh-CN` 下） | 进到第 2 步的 `LLC_zh-CN` 文件夹 |
| 弹窗问是否替换 → 选 **「替换目标中的文件」** | — |

> **macOS**：`Cmd + A` / `Cmd + C` / `Cmd + V`，弹窗选「替换」。
>
> **Linux / Steam Deck**：终端执行
> ```bash
> cp -r patch/. "…/LimbusCompany_Data/Lang/LLC_zh-CN/"
> ```

**✅ 装对的样子**：`LLC_zh-CN` 里出现了 `RPGSystem` 和 `StoryData` 两个**文件夹**。
如果只有一堆散装 json，说明文件夹没复制过去，回第 3 步重做。

### 第 4 步：启动游戏

直接开游戏即可，**不需要**在游戏里重新选语言。

---

## 装完能看到什么

- 商城 / 编队里两个人格的**技能名与描述**：良秀 · Le Noir鞋履馆、以实玛利 · Le Rouge精品店
- 他们的**被动**与新增**状态**关键词
- **第十章迷宫**（西西弗百货 1F–4F、B1–B2）的对话、道具、任务
- **主线第十章**剧情（S1000B–S1016B）、新人格剧情 P10416 / P10816
- 章节名、抽取标题、赛季横幅、战斗语音等

---

## 常见问题

**Q：patch 里几十个文件，我要挑着装吗？**
不用挑，**全选（Ctrl+A）→ 放到 `LLC_zh-CN` 下 → 覆盖**，一个都不能少。文件多只是因为内容多。

**Q：为什么还要先装零协会汉化包？**
本补丁只含「零协会还没做」的部分（第十章新内容）。游戏其余文本、中文字体、语言列表都来自零协会的包。

**Q：装完还是英文 / 还是韩文？**
1. 检查 `LLC_zh-CN` 里是否有 `RPGSystem`、`StoryData` 两个**文件夹**（最容易漏的一步）。
2. 进游戏确认语言选的是 `LLC_zh-CN`（主界面左下角第二个按钮）。

**Q：怎么卸载？**
- **彻底删汉化**：删掉整个 `Lang` 文件夹。
- **只撤本补丁**：用零协会包里的同名文件覆盖回去（25 个），再删掉新增的 104 个文件。

---

## 本次补丁汉化什么

零协会汉化还没更新，所以以下内容「英文 / 韩文有、中文缺失」，游戏里只能显示英文。本补丁进行汉化补齐：

`patch` 共 **129 个文件**，分两类：

| 类型 | 文件数 | 说明 |
| --- | ---: | --- |
| **新增** | 104 | 零协会包里**完全没有**的内容（本补丁从无到有译出），共 3282 条记录 |
| **覆盖** | 25 | 零协会包里**有但落后**的内容，补齐其中缺失的 106 条记录 |

**新增文件分布**

| 目录 | 文件数 | 内容 |
| --- | ---: | --- |
| `RPGSystem/` | 44 | 第十章迷宫全部中文（1F–4F / B1–B2：对话、道具、地点、NPC、任务、UI） |
| `StoryData/` | 21 | 主线 S1000B–S1016B、新人格剧情 P10416 / P10816 |
| 根目录 | 36 | 新版本技能、被动、敌人、状态、活动、商店、通行证 |
| `PersonalityVoiceDlg/` | 2 | 新人格语音台词 |
| `BattleAnnouncerDlg/` | 1 | 商场播报员台词 |

**覆盖文件补了什么**

| 文件 | 补的条数 | 内容 |
| --- | ---: | --- |
| `BattleSpeechBubbleDlg.json` | 16 | 新人格战斗语音气泡 |
| `ScenarioModelCodes-AutoCreated.json` | 16 | 剧情内 NPC 代号 |
| `Passives.json` | 8 | 两个人格的新被动（含风味文本） |
| `MainUIText.json` | 7 | 经验采光迷宫 #10、剧情续看提示 |
| `BattleKeywords.json` / `Bufs.json` | 各 6 | 新状态：华达呢大衣、保存、Armure Éveillée、搏动、更衣室、全面改造 |
| `Skills_personality-04.json` | 5 | **良秀 · Le Noir鞋履馆 全部技能** |
| `Skills_personality-08.json` | 5 | **以实玛利 · Le Rouge精品店 全部技能** |
| `Egos.json` | 4 | 新 E.G.O 名称（拒斥、镜触、空洞） |
| `IntroductionPreset.json` | 4 | 人格介绍标语 |
| `Personality_Get_Condition.json` | 4 | 获取条件（商城显示） |
| 其余 15 个 | 25 | 赛季标题、横幅、章节名、抽取标题、登录提示等 |

质量说明：技能与被动按官方既成句式翻译（如 `Inflict N [X]` → `使目标增加N级[X]强度`）；
`<color=#...>`、`<style="highlight">`、`<size=95%>`、`[ChargeNoirAlly]` 等标记与引擎标签
均与英文源**逐字符一致**。

---

## 翻译工作流

1. **实机演示** —— 见 `docs/边狱巴士第十章.pptx`
2. **安装说明** —— 见上方「安装（三分钟）」
3. **翻译流程** —— 见 `knowledge-base/workflow/翻译流程.md`

思路：拿官方 **英 / 韩 / 日** 原版文本与零协会既有汉化做**四语对齐**，
建立术语与文风基线后，用 AI 批量翻译，再用脚本校验标记、占位符与漏译。

---

## 使用知识库（想继续翻译）

入口：`knowledge-base/00_索引.md`

| 路径 | 内容 |
| --- | --- |
| `knowledge-base/terms/术语表.md` | 权威术语表（约 1000 条，含「一词多译」区分） |
| `knowledge-base/terms/常用表达表.md` | 高频句式与 UI 文案 |
| `knowledge-base/style/角色口吻速查.md` | 各角色口吻速查（自称、称呼、标点密度） |
| `knowledge-base/style/角色/*.md` | 各罪人完整文风指南（含中英实例） |
| `knowledge-base/style/机制句式模板.md` | 技能 / 被动高频句式模板 |
| `knowledge-base/worldview/共享世界观.md` | 都市 / 巢 / 翼 / 首脑 / 手指 等设定术语 |
| `knowledge-base/worldview/专名对照.md` | 人名、组织、异想体、E.G.O 专名表 |
| `knowledge-base/workflow/翻译流程.md` | 从检索到交付的完整 SOP |

工具（`knowledge-base/tools/`，需要 Python 3）：

```bash
python3 tools/pm_lib.py show MainUIText.json    # 四语逐条对照
python3 tools/pm_lib.py grep 事务所 -l cn        # 搜既有译法
python3 tools/verify_output.py <文件名>          # 校验译文
```

> 语料缓存（约 160 MB）未入库，可用 `tools/export_corpus.py` 重新生成。

---

## 许可与致谢

- 本补丁基于**都市零协会汉化组**译文（未改动其原文，只补齐缺失条目），
  遵循 **CC BY-NC-SA 4.0**：署名、非商业性使用、相同方式共享。
- 感谢零协会汉化组开源。原始汉化：<https://www.zeroasso.top>
- 本仓库仅为个人分享，**禁止任何商业化行为**。
