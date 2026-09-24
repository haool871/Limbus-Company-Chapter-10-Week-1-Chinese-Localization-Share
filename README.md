# 边狱巴士 第十章 第一周 汉化分享

> **开发流程更新（2026-09-22）**：仓库 `patch/` 保留上一轮交付内容；下一次游戏更新不会继续默认修改这批文件。新流程先冻结原文基线、比较新旧版本，再建立独立翻译批次，见 [版本更新流程](knowledge-base/workflow/版本更新流程.md) 与 [修复记录](knowledge-base/workflow/流程修复记录_20260922.md)。本次仅更新工具与文档，没有发布新补丁。

《Limbus Company》第十章第一周内容的个人 AI 汉化补丁与翻译知识库。
感觉有用还望 star 一下 ⭐

> 演示文稿：`docs/边狱巴士第十章.pptx`

---

## 说明与叠甲

- 本汉化**全程使用 deepv4.1-flash 模型**进行翻译，建立在 **「都市零协会汉化组」的过往汉化**、月亮计划过往游戏汉化数据基础之上。
- **只做分享，拒绝任何可能的商业化行为。**
- **已做两轮审校**：
  1. 「**带上下文重译**」——全部 21 个剧情文件 + 44 个探索模式文件按「对话回合／对话组」而非单句重译
     （详见 `knowledge-base/workflow/重译手册.md`）
  2. 「**通读润色**」——逐句对照韩文理顺读不顺的句子
     （详见 `knowledge-base/workflow/通读润色手册.md`）
  并统一了跨文件术语（`异邦人→外来者`、`管理人→经理`、`经理阁下→经理老爷`、`两件套→西装组` 等，均以零协语料实证为准）。
  但 AI 翻译**仍可能有错**，请当**尝鲜**用，之后**务必换回都市零协会的汉化**。
- **✅ 已与零协 `2026092102` 逐值对齐**：零协最新版重译过的内容，本补丁**一律改用零协译文**
  （共 7082 处，含剧情、探索模式、技能、BUFF 说明与嵌套的对话文本），
  逐条逐值比对后与零协的**残余差异为 0 处**。
  本补丁因此只剩两个作用：① 零协**留空或漏掉**的 2 处；② 零协**完全没有**的 9 个文件 / 46 条记录。
  也就是说，**装了零协最新版的话，本补丁不装也不影响剧情阅读**。
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
<https://www.zeroasso.top/docs/install/autoinstall>

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

- 商城 / 编队里两个人格的**技能名与描述**：良秀 · 黑派制鞋馆、以实玛利 · 红派精品店
- 他们的**被动**与新增**状态**关键词
- **第十章迷宫**（西西弗百货 1F–4F、B1–B2）的对话、道具、任务
- **主线第十章**剧情（S1000B–S1016B）、新人格剧情 P10416 / P10816
- 章节名、抽取标题、赛季横幅、战斗语音等

---

## 常见问题

**Q：patch 里一百多个文件，我要挑着装吗？**
不用挑，**全选（Ctrl+A）→ 放到 `LLC_zh-CN` 下 → 覆盖**。
其中 120 个文件的内容已与零协最新版**逐字相同**（装了等于没装），
真正起作用的是零协**没有**的 9 个文件和零协**留空**的 2 处。
所以：**先装零协最新版，再覆盖本补丁**，是最省事也最正确的顺序。

**Q：为什么还要先装零协会汉化包？**
本补丁只补零协**没有**的部分。游戏其余文本、中文字体、语言列表都来自零协会的包。
若零协包太旧，本补丁覆盖的 120 个文件会把你带回旧译——**务必用最新零协包**。

**Q：装完还是英文 / 还是韩文？**
1. 检查 `LLC_zh-CN` 里是否有 `RPGSystem`、`StoryData` 两个**文件夹**（最容易漏的一步）。
2. 进游戏确认语言选的是 `LLC_zh-CN`（主界面左下角第二个按钮）。

**Q：怎么卸载？**
- **彻底删汉化**：删掉整个 `Lang` 文件夹。
- **只撤本补丁**：删掉 `StoryTheaterMain-a1c7p1.json`、`UserBanner-a1c7p3.json`、
  `UserBanner-a1c8p1.json`、`UserTicket-EGOBg-a1c7p3.json`、`UserTicket-EGOBg-a1c8p1.json`、
  `UserTicket-L-a1c7p3.json`、`UserTicket-L-a1c8p1.json`、`UserTicket-R-a1c7p3.json`、
  `UserTicket-R-a1c8p1.json` 这 **9 个**（零协本来就没有），
  再用零协包覆盖一遍即可。其余 120 个文件的内容与零协一致，删不删都一样。

---

## 本补丁现在汉化什么

零协 `2026092102`（2026-09-21 版）**已经把第十章汉化完了**，所以本补丁的定位已经变了：

| 类型 | 文件数 | 说明 |
| --- | ---: | --- |
| **与零协逐字一致** | 120 | 内容已全部改用零协最新译文。装了等于没装，**留着是为了保证覆盖顺序不会把你带回旧译** |
| **零协没有** | 9 | `StoryTheaterMain-a1c7p1`、`UserBanner-a1c7p3`/`a1c8p1`、`UserTicket-{EGOBg,L,R}-a1c7p3`/`a1c8p1`——**只有本补丁有** |
| **零协留空** | 2 处 | `rpg-loc-location-floor-3` 的 `130600`、`rpg-loc-quest-floor-1` 的 `Q1001` |

**结论：先装零协最新版；想要那 9 个文件就再覆盖本补丁。**

**那 9 个文件是什么**

| 文件 | 条数 | 内容 |
| --- | ---: | --- |
| `UserBanner-a1c8p1.json` | 8 | 第 8 赛季横幅 |
| `UserTicket-EGOBg-a1c8p1.json` | 8 | E.G.O 背景券 |
| `UserTicket-L-a1c8p1.json` | 8 | 左栏票券 |
| `UserTicket-R-a1c8p1.json` | 8 | 右栏票券 |
| `UserBanner-a1c7p3.json` | 4 | 第 7 赛季第 3 部分横幅 |
| `UserTicket-EGOBg-a1c7p3.json` | 3 | E.G.O 背景券 |
| `UserTicket-L-a1c7p3.json` | 3 | 左栏票券 |
| `UserTicket-R-a1c7p3.json` | 3 | 右栏票券 |
| `StoryTheaterMain-a1c7p1.json` | 1 | 剧场主界面 |

> ⚠️ 这 9 个文件官方**尚未出韩文**（只有英文），所以是**以英文为源**译的，
> 可能带有英文源固有的七类错误。这点已经在 `knowledge-base/workflow/重译手册.md §0.6` 记录。

---

**零协留空、由本补丁补上的 2 处**

| 位置 | 内容 |
| --- | --- |
| `RPGSystem/rpg-loc-location-floor-3.json` → `130600.text` | `(临时)共用-3层-(52,64)-4层 (临时)`（官方也是占位文本，非正式文案） |
| `RPGSystem/rpg-loc-quest-floor-1.json` → `Q1001.description` | `未使用` |

> 这两处在游戏里是否显示取决于版本，补上只是让文本完整，**不含剧情信息**。

质量说明：技能与被动按官方既成句式翻译（如 `Inflict N [X]` → `使目标增加N级[X]强度`）；
`<color=#...>`、`<style="highlight">`、`<size=95%>`、`[ChargeNoirAlly]` 等标记与引擎标签
均与英文源**逐字符一致**。合并后已跑 `verify_retrans.py --all`：**129 文件 / 错误 0 / 警告 0**。

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
