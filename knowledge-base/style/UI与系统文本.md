# UI 与系统文本翻译规范（EN → CN）

适用范围：界面按钮、菜单、页签、弹窗、系统提示与错误、公告/FAQ、商店与通行证、教程文案。

本次统计样本：50 个 UI/系统文件、**5,598 组**英中对照；长度基准另有全库 `EN→CN` 短串索引 **38,928 个英文键 / 98,010 组对照**（`(文件,id,字段)` 四语对齐后取 en/cn）。
主文件：`MainUIText.json`(514)、`TutorialMainUIText.json`(1,355)、`BattleSpeechBubbleDlg.json`(885)、`Items.json`(286)、`MirrorDungeonUI_4.json`(295)、`BattleUIText.json`(218)、`IAPProduct.json`(146)、`LoginUIText.json`(91)、`ShopUI.json`(80)、`BattlePass.json`(66)、`FAQ.json`(39)。

---

## 1. 按钮 / 菜单词的「最短化」倾向

### 1.1 实测长度基准（汉字数）

| 英文长度 | 样本数 | 中位 | P75 | P90 | P99 | 最大 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 词 | 668 | **2** | 3 | 4 | 6 | 8 |
| 2 词 | 1,080 | **4** | 4 | 6 | 8 | 14 |
| 3 词 | 623 | **5** | 6 | 7 | 9 | 11 |
| 4 词 | 420 | 6 | 8 | 10 | 12 | 14 |
| 5 词 | 296 | 8 | 10 | 12 | 14 | 16 |
| **EN ≤ 3 词合计** | 2,371 | **4** | — | **6** | **8** | 14 |

**可执行规则**：

- 按钮 / 页签 / 标签：**目标 ≤ 4 字，硬上限 6 字**（P90）。超过 6 字说明在写句子，不是写标签。
- EN 1 词 → 中文优先 **2 字**（取消、关闭、详情、设置、商店、背包、编队…）；只有语义必须时才 3–4 字（`Enkephalin Box` → `脑啡肽盒子`）。
- EN 2 词 → 中文 **4 字**（`Claim All` → `全部领取`、`Edit Team` → `编辑编队`、`Clear Rewards` → `通关奖励`）。
- EN 3 词 → 中文 **5 字左右**（`Event Bonus Units` → `活动加成角色`、`Selectable E.G.O Gift +1` → `出现的饰品数量+1`）。
- 超长标签（≥10 字）都是**因为中文把隐含信息补全了**，是刻意为之而非失控：
  - `Reached Max Level.` → `执行经理已到达最大等级。`
  - `Enhancements Used` → `可进行人格升级的次数`
  - `E.C.(Enkephalin Charged.)` → `脑·肽·充·毕。（脑啡肽补充完毕。）`

### 1.2 最短化手段（按优先级）

| 手段 | 英文 | 中文 |
| --- | --- | --- |
| 去冠词/系动词 | `Cannot Purchase` | 无法购买 |
| 名词直接并置 | `Reward Exchange` | 奖励兑换 |
| 副词短语合成词 | `Higher Tier Gifts appear` | 出现饰品等级上升 |
| 数值符号化 | `Starting Cost +50` | 初始经费+50 |
| 省略「的」 | `Event Bonus Units` | 活动加成角色 |
| 固定缩写词保留 | `E.G.O Gifts` / `EXP` | E.G.O饰品 / 经验 |

---

## 2. 名词短语 vs 动词短语

### 2.1 分工原则

| 位置 | 用法 | 例 |
| --- | --- | --- |
| 按钮、动作入口 | **动词短语** | `Confirm`→确认、`Cancel`→取消、`Purchase`→购买、`Claim All`→全部领取、`Enter`→进入、`Exchange`→兑换、`Use`→使用、`Retry`→重试、`Reset`→重置、`Select`→选择 |
| 页签、标题、字段名 | **名词短语** | `Details`→详情、`Settings`→设置、`Shop`→商店、`Inventory`→背包、`Team`→编队、`Identities`→人格、`Keywords`→关键词、`Resistances`→抗性信息、`Enemy Info`→敌方信息 |
| 状态标记 | **判断式短语 / 已+X** | `Owned`→已拥有、`Purchased`→已购买、`Locked`→未开放、`Cannot Enter`→无法进入战斗、`Now Open`→开放中 |

### 2.2 同一个英文词按界面位置分流（重要）

不要用一个词打天下，零协会是**按上下文分别定译**的：

| EN | 出现的界面 | CN |
| --- | --- | --- |
| `Confirm` | 通用确认按钮 | 确认 |
| `Confirm` | 购买确认弹窗 | **购买** |
| `Return` | 通用返回 | 返回 |
| `Return` | 战斗结算「返还」 | **返还** |
| `Return` | 重返某地 | **重返** |
| `Resume` | 中断后续玩 | 继续 |
| `Resume Battle` | 战斗内 | **回到战斗** |
| `Rewards` | 通用 | 奖励 |
| `Rewards`（保底） | 抽取结果 | **确定奖励** |
| `Rewards Earned` | 领取结果 | **已领取奖励** |
| `Support` | 好友/编队助战位 | 助战 |
| `Support` | 被动技能栏 | **支援被动技能** |
| `Enter` | 通用 | 进入 |
| `Enter Battle` | 战斗入口 | 进入战斗 |
| `Details` | 通用 | 详情（7 次） |
| `Details`（tooltip） | 战斗内 | 更多信息 / 详细信息 / 详细情报 / 查看详情 |
| `Event` | 活动玩法 | 活动 |
| `Event` | 剧情事件 | 事件 |

→ 新文本遇到同形词，先按所在界面判断语义，再决定译法；**同一界面内必须一致**。

---

## 3. 空间限制与长度分布

### 3.1 分文件实测（EN 词均 → CN 汉字均）

| 文件 | 行数 | EN 词均 | CN 字均 | 字/词 |
| --- | ---: | ---: | ---: | ---: |
| `BattleUIText.json`（战斗按钮/提示） | 218 | 2.6 | 4.5 | **1.71** |
| `ShopUI.json` | 80 | 3.3 | 5.4 | 1.64 |
| `MainUIText.json`（主界面） | 514 | 4.8 | 7.9 | 1.63 |
| `BattleSpeechBubbleDlg.json` | 885 | 5.5 | 7.2 | 1.32 |
| `MirrorDungeonUI_2.json` | 234 | 5.9 | 9.9 | 1.66 |
| `BattlePass.json` | 66 | 7.3 | 12.5 | 1.71 |
| `Items.json`（道具说明） | 286 | 21.9 | 31.9 | 1.46 |
| `TutorialMainUIText.json` | 1,355 | 14.5 | 21.2 | 1.46 |
| `IAPProduct.json`（商品） | 146 | 13.2 | 18.1 | 1.37 |
| `FAQ.json` | 39 | 39.6 | 48.1 | **1.21** |
| **UI 合计** | 5,581 | 10.1 | 14.4 | **1.42** |
| **其中 EN≤3 词短标签** | 2,363 | 2.1 | 3.8 | **1.85** |

### 3.2 各内容类型长度基准（全库口径，供对照）

| 内容类型 | EN 词均 | CN 字均 | 字/词 |
| --- | ---: | ---: | ---: |
| 剧情 | 14.2 | 25.0 | 1.76 |
| 语音台词 | 17.2 | 28.1 | 1.63 |
| 事件 | 29.5 | 57.4 | 1.95 |
| UI | 19.6 | 36.7 | 1.87 |
| 机制/状态 | 19.9 | 46.0 | 2.31 |
| 技能/被动 | 12.7 | 59.4 | **4.68** |
| 歌词 | 6.1 | 15.6 | 2.56 |

（本次机制文件实测：`desc/summary` 16.8 词 → 27.1 字，比 1.61；技能 `levelList` 描述 9.9 词 → 15.6 字，比 1.57。）

### 3.3 空间规则

1. **短标签**（按钮/页签/状态）：≤ 4 字最佳，≤ 6 字合格，> 8 字必须重新拆分或改名词化。
2. **长文**（FAQ/公告/教程/商品说明）：按 **1.2–1.5 字/词** 估行宽；FAQ 实测压到 **1.21**，是最省的文体。
3. **机制/技能文本不受 UI 字数上限约束**：中文比英文长 1.6–4.7 倍属**正常**，零协会采用完整书面句式，**不得为压缩而删掉触发条件、目标或次数限制**。压缩只能压虚词（`的`、`进行`、`将会`）。
4. 数值、颜色标签、占位符不占「可压缩额度」。

---

## 4. 系统提示与错误信息

### 4.1 固定句式

| 英文句式 | 中文固定说法 | 实例 |
| --- | --- | --- |
| `Not enough X.` / `Insufficient X.` | **`X不足。`** | `Not enough Thread.` → `纺锤不足。`；`Not enough Starlight.` → `星芒不足。`；`※ Not enough Lunacy.` → `※ 狂气不足。` |
| `You don't have enough X.` | `X不足。`（不用「你没有足够的」） | `You don’t have enough Lunacy.` → `狂气不足。` |
| `Cannot X` / `You cannot X` | **`无法X`** | `Cannot Purchase` → `无法购买`；`Cannot Claim` → `无法领取`；`Cannot Exchange` → `无法兑换`；`Cannot Enter` → `无法进入战斗` |
| `X is not available` | `无法X` / `已结束` | `Unselectable` → `无法选择`；`Unprojectable` → `无法投影` |
| `Are you sure you want to X?` | **`要X吗？`**（短）/ **`您确定要X吗？`**（含风险） | `Are you sure you want to skip?` → `要跳过吗？`；`Are you sure you want to skip the tutorial?` → `您确定要跳过所有教程吗？`；`Are you sure you want to reset {0}?` → `要重置{0}吗？` |
| `Will you X?` / `Would you like to X?` | **`是否X？`** | `Will you enter {0}?` → `是否进入{0}？`；`Would you like to skip the battle?` → `是否跳过战斗？`；`Would you like to purchase Enkephalin Boxes?` → `要购买脑啡肽盒子吗？` |
| `X has been Y.` | `X已Y。` | `Enkephalin Charged` → `脑啡肽已补充`；`Enkephalin has been refilled.` → `脑啡肽已重新充满。` |
| `Please check X.` | **`请检查X。`** | `The network is unstable.`⏎`Please check your Internet connection.` → `网络连接不稳定。`⏎`请检查网络状态。`（原文为同一字段内的两行） |
| `Please X to download/retry.` | `请X以…` | `The game will be closed; please restart the game to download the update.` → `游戏即将关闭，请重启游戏以下载。`；`Please download new resources and try again.` → `请下载资源并重试。`（两条均为多行字段中的一行） |
| `X Remaining` / `N left` | `剩余X` / `剩余N天` | `Extractions Remaining` → `剩余提取次数`；`{0} days left` → `剩余{0}天` |
| `Unlocked at Tier {0}` | `在同步阶段{0}解锁` | `Clear Ch. {0} to Unlock` → `通过第{0}章后解锁` |
| 上限类 | `已达到上限` / `已耗尽` | `Daily Quota Exhausted` → `今日配额已耗尽` |

### 4.2 语域：系统提示用敬语

实测词频（FAQ / 登录界面 / 通行证）：

| 词 | FAQ.json | LoginUIText.json |
| --- | ---: | ---: |
| 您 | **24** | 4 |
| 你 | **0** | 0 |
| 请 | **20** | 13 |

**规则**：面向玩家的提示、公告、FAQ、购买确认一律用「**您**」+「**请**」，**不用「你」**（「你」只出现在剧情对话里）。带风险的操作要提示后果：

```
EN: Upon entry, you will no longer be able to travel to other nodes of the dungeon; {0} will fully heal HP and have their SP reset to 0.
    Are you sure you want to proceed?
CN: 进入后，您将无法再移动到迷宫的其他地点；罪人{0}的体力将会全部恢复，理智值将会重置为0。
    您确定要继续吗？
```

### 4.3 提示文案的常见改写

| 手法 | EN | CN |
| --- | --- | --- |
| 双句合一句 | `Cannot use this E.G.O. Please check your resources.` | `E.G.O资源不足，无法使用E.G.O。` |
| 检查项替换成结论 | `Cannot use this E.G.O. Please check available space.` | `行动槽已被占用，无法使用E.G.O。` |
| 简短前缀 | `The [Reward Exchange]'s open duration is shown here.` | `此处显示了[奖励兑换]页面的开放时间。` |
| 语气词收敛 | `Unlocking Nocturnal Sweeping` | `深夜清扫 已开放` |

---

## 5. 公告 / FAQ / 活动页

1. **符号原样保留**：`※`（UI 语料 104 次）、`■`（FAQ 6 次）、`▶`、`·`、`-`。
   - `※ Maximum capacity is 100; expired mail will be <color=#990000>deleted</color>.` → `※最多可保管100个，过期的礼物将被<color=#990000>删除</color>。`
   - `■ Possible Solutions for Failed Transactions` → `■ 交易失败的可能解决方案`
   - `▶ Receive a 「Decaextraction Ticket」 by collecting 7 Attendance Checks` → `▶累计签到七天可获得一张[十连提取券]`
2. **编号格式**：`1)` / `1）` 两种写法并存，以**全角 `1）`为主**（FAQ.json 内 3 条 `2) 3) 4)` 用半角、4 条用全角），**同一篇公告内必须统一**；`(1)` 半角行式（法律条款）保持半角：`(1) Contents used or applied immediately upon purchase` → `(1) 购买后立即使用或生效的内容`。
3. **HTML 标签原样保留**：`<b>`、`<color=#xxxxxx>`、`<u>`、`<link="...">`、`<size=90%>`。FAQ 正文里 `<b>Monthly Lunacy Supply</b>` 对应 `<b>每月狂气补给</b>`。
4. **时区/时间本地化**（不是直译）：
   ```
   EN: ※ You can receive log-in rewards each day when entering the game based on the game’s daily resets (D-0 06:00 ~ D+1 05:59 <KST>).
   CN: ※ 以游戏内每日重置为基准（当日05:00 ~ 次日04:59 [CST]），每天都可以领取登录当天对应的奖励。
   （原字段还有第二行：※ Unclaimed rewards are lost the next day, so please make sure to redeem them in time.
     → ※ 当天未领取的奖励将于次日过期，届时无法补领。因此请务必及时领取。）
   ```
   （`<KST>` → `[CST]`，`06:00~05:59` → `05:00~04:59`，方括号格式也一并本地化。）
5. **长句压缩**：FAQ 是压缩率最高的文体（1.21 字/词）——删掉语气连接，保留条件与数值，并把英文的从句改成中文的时间状语：
   ```
   EN: When you purchase the <b>Monthly Lunacy Supply</b>, you will be given 650 Lunacy upfront,
       and you become eligible to receive the daily rewards listed below for the following 30 days.
   CN: 当您购买<b>每月狂气补给</b>后，您将立即获得650付费狂气，
       并且您可在含购买日当天在内的三十天内获得以下每日奖励。
   ```
   注意三点官方做法：①`650 Lunacy` 在**此处**补成「付费狂气」；②`for the following 30 days` 展开为「含购买日当天在内的三十天」，把「含当天」这一隐含信息显化；③`Monthly Lunacy Batch` 不译作「批量」，而是与 Supply 对仗译成「**每月小份狂气补给**」。
6. **公告标题用名词短语**，不带句号：`Refraction Railway Opening` → `折射轨道 开放`；`The Battle Pass is unlocked!` → `战斗通行证已开放！`（感叹号随原文）。

---

## 6. 商店 / 通行证

### 6.1 货币与资源词表（必须一致）

| EN | CN | 出处 |
| --- | --- | --- |
| Lunacy | 狂气 | `MainUIText.json` / `BattlePass.json` |
| Paid / Free Lunacy | 付费狂气 / 免费狂气 | `IAPProduct.json`：`Contains 140 Paid Lunacy.` → `包含140付费狂气。` |
| Enkephalin | 脑啡肽 | `MainUIText.json` |
| Enkephalin Box | 脑啡肽盒子 | `ShopUI.json` |
| Thread | 纺锤 | `Items.json` |
| Egoshards | 自我碎片 | `MainUIText.json` |
| Starlight | 星芒 | `MirrorDungeonUI_6.json` |
| Cost | 经费 | `MirrorDungeonUI_2.json`：`Starting Cost +50` → `初始经费+50` |
| Stamina | 体力 | `MainUIText.json` |
| Currency | 道具 | `MainUIText.json` |
| EXP | 经验 | `MainUIText.json` |
| Coin（剧情物品） | 铜钱 | 仅剧情/饰品语境，**勿与战斗「硬币」混用** |

### 6.2 商品命名

`Lunacy Bundle` → `一捆狂气`；`Lunacy Bouquet` → `一束狂气`；`Identity Growth Pack` → `人格养成组合包`；`Target Extraction Pack` → `特别提取组合包`；`E.G.O Upgrade Pack` → `E.G.O成长组合包`；`Fixer Recov. Pack` → `收尾人乘客复原包`。
→ **`Pack` 一律「组合包」**，量词（捆/束）按原英文意象保留。

### 6.3 通行证词表

| EN | CN |
| --- | --- |
| Battle Pass | 战斗通行证 |
| Pass Level | 通行证等级 |
| Pass Missions | 通行证任务 |
| Daily / Weekly / Seasonal | 日常任务 / 周常任务 / 赛季任务 |
| Season 1 | 第1赛季 |
| Battle Pass XP | 战斗通行证经验值 |
| Paid {0} Free {1} | 付费{0} 免费{1} |
| Weekly Bonuses | 每周加成 |

### 6.4 购买确认

```
EN: Confirm Purchase        CN: 确认购买
EN: Would you like to purchase Enkephalin Boxes?   CN: 要购买脑啡肽盒子吗？
EN: Convert to {0} Thread?  CN: 要购买{0}个纺锤吗？
EN: ※ Spent Enkephalin Modules will not be refunded.
CN: ※已消耗的脑啡肽模块将不会返还。
```

---

## 7. 常见 UI 词表（EN → CN，按界面区域：110 行 / 约 125 条术语）

### A. 按钮 / 动作（28 行）

| EN | CN | | EN | CN |
| --- | --- | --- | --- | --- |
| Confirm | 确认 | | Select | 选择 |
| Cancel | 取消 | | Select All | 全选 |
| Close | 关闭 | | Deselect All | 取消全选 |
| Continue | 继续 | | Skip（Tutorial） | 跳过（教程） |
| Resume（Battle） | 继续（回到战斗） | | Give Up / Forfeit Stage | 放弃关卡 |
| Return | 返回 / 返还 / 重返 | | Retry | 重试 |
| Claim | 领取 | | Reset | 重置 / 恢复默认 |
| Claim All | 全部领取 | | Sort | 排序 |
| Purchase / Buy | 购买 | | Filter | 筛选 |
| Confirm Purchase | 确认购买 | | Search | 搜索 |
| Exchange | 兑换 | | Delete | 删除 |
| Use | 使用 | | Unequip | 解除 |
| Sell | 售卖 | | Apply | 使用 |
| Enter（Battle） | 进入（进入战斗） | | Download | 下载 |

### B. 页签 / 标题 / 字段（38 行）

| EN | CN | | EN | CN |
| --- | --- | --- | --- | --- |
| Details | 详情 | | Level | 等级 |
| Info | 信息 | | EXP | 经验 |
| Settings | 设置 | | Difficulty | 难度 / 推荐等级 |
| Combat / Encounter | 战斗 | | Normal / Hard / Easy | 普通 / 困难 / 简单 |
| Shop | 商店 | | Regular | 常规 |
| Inventory | 背包 | | Default | 基础 / 默认 |
| Team / Formation / Team Loadout | 编队 | | Progress / Progression | 进度 / 流程说明 |
| Edit Team | 编辑编队 | | Cycle | 巡回 |
| Identities | 人格 | | Cost | 经费 |
| Identity List | 人格列表 | | Currency | 道具 |
| Select Identity | 选择人格 | | Quantity / Amount | 总数 / 获取数量 |
| E.G.O List | E.G.O列表 | | Expiry | 截止时间 |
| E.G.O Gifts | E.G.O饰品 | | Remaining | 剩余 |
| E.G.O Gift Compendium | E.G.O饰品图鉴 | | Tier 1–4 | 1级–4级 |
| E.G.O Resources | E.G.O资源 | | Uptie / Uptie Tier | 同步 / 同步阶段 |
| Passives | 被动技能 | | Awakening / Corrosion | 觉醒技能 / 侵蚀技能 |
| Keywords | 关键词 | | Status | 能力值 |
| Skill Effects | 技能效果 | | Resistances | 抗性信息 |
| Active Effects | 生效的效果 | | Enemy Info | 敌方信息 |

### C. 系统状态 / 玩法（44 行）

| EN | CN | | EN | CN |
| --- | --- | --- | --- | --- |
| Owned | 已拥有 | | Event Period | 活动时间 |
| Purchased | 已购买 | | Event Stages | 活动关卡 |
| Locked | 未开放 | | Event Encounters | 活动战斗 |
| Now Open / Open | 开放中 / 已开放 | | Event Bonus Units | 活动加成角色 |
| Cannot Purchase | 无法购买 | | Reward Exchange | 奖励兑换 |
| Cannot Claim | 无法领取 | | Mirror Dungeons | 镜像迷宫 |
| Not enough X. | X不足。 | | Mirror Worlds | 镜像世界 |
| Free / Paid | 免费 / 付费 | | Refraction Railway | 折射轨道 |
| Rewards | 奖励 | | Theater | 放映室 |
| Clear Rewards / Clear Info | 通关奖励 / 通关信息 | | Jukebox / Playlist | 点唱机 / 播放列表 |
| Missions（列表） | 任务列表 | | Achievements | 成就 |
| Battle Pass | 战斗通行证 | | Collection | 收集 |
| Pass Level | 通行证等级 | | Observation Logs | 图鉴 |
| Season | 赛季 | | Lost & Found | 失物招领处 |
| Lunacy | 狂气 | | Façades | 外观投影 |
| Enkephalin (Box) | 脑啡肽（盒子） | | Weave Projection | 投影制作 |
| Thread | 纺锤 | | Starter Buffs | 开局增益 |
| Egoshards | 自我碎片 | | Theme Pack-Exclusive | 主题卡包限定 |
| Starlight | 星芒 | | Recommended Specs | 推荐配置 |
| Stamina | 体力 | | Support | 助战 / 支援被动技能 |
| Terms of Service | 服务条款 | | Weekly Bonuses | 每周加成 |
| Refund Policy | 退款政策 | | Chain Battle Encounters | 连续遭遇战关卡 |

---

## 8. 交付前自检

```bash
python3 tools/qa_check.py --official <文件名>   # id 覆盖 / 标签 / 占位符 / 未译 / 长度异常
```

- [ ] 按钮/标签是否 ≤ 6 字（P90）？超过 8 字是否已重写为名词短语？
- [ ] 同一英文词是否按界面位置分流（Confirm→确认/购买、Return→返回/返还/重返、Rewards→奖励/确定奖励）？
- [ ] 系统提示是否用「您 / 请」，且**没有**出现「你」？
- [ ] 不足/无法/是否/要…吗 的句式是否与 §4.1 一致？
- [ ] `※ ■ ▶ · <b> <color> <link> {0}` 等符号、标签、占位符是否逐字保留？
- [ ] `1)` 是否改成了 `1）`，而 `(1)` 保持半角？
- [ ] 时间/时区是否做了本地化（不用 KST）？
- [ ] 货币与资源名是否与 §6.1 完全一致（尤其 Coin 在战斗=硬币、剧情=铜钱）？
- [ ] 是否为了塞进界面而删掉了条件/数值？——UI 文案可压缩虚词，**不可删信息**；机制文本更不允许压缩条件。
