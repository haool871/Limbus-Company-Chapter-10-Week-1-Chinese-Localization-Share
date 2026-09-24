---
name: limbus-localization
description: 在 Limbus Company 汉化工作区中查询术语与角色口吻、准备版本基线、检测游戏更新、翻译本轮新增或变更文本、审校和生成补丁交付物。仅查询或准备时不创建翻译批次；安装和发布仅在任务包含这些动作时执行。
---

# Limbus Company 汉化

先定位包含 `tools/batch.py`、`workflow/版本更新流程.md` 与 `terms/` 的知识库根目录（本工作区为 `_kb/`；发布副本可能名为 `knowledge-base/`）。以下相对命令均在该目录运行。不要依赖用户名或固定绝对路径。

## 按请求选择范围

| 请求 | 执行范围 |
| --- | --- |
| 查术语、口吻、读项目 | 读索引，检索对应版本证据；不建批次、不翻译、不安装 |
| 为下次更新准备 | 核对或保存当前官方原文与零协快照，保持等待状态 |
| 游戏更新了、翻译新内容 | 对比更新前后原文，核对上游适用性，再创建独立批次 |
| 重译、润色 | 仅处理当前任务明确的字段；无批次时先明确原文快照与范围，不能恢复旧补丁充当新任务 |
| 验证、审计 | 执行对应只读检查；报告证据与局限，不因查出疑点自动改写全文 |
| 安装、打包、发布 | 按本次授权完成相应环节；翻译、查询与本地导出本身不等于安装或推送 |

当前状态以 `project.json` 与 `python3 tools/batch.py status` 为准。`phase=waiting` 且 `active_batch=null` 表示无修改源。`archives/` 中的旧补丁不是本次任务；不要创建空 `patch_v2/` 迎合旧脚本。

## 更新工作的入口

开始更新前阅读已定位知识库中的 `workflow/版本更新流程.md`，其参数和 JSON 格式是现行工程规范。

1. **查基线**：`python3 tools/doctor.py`。旧快照必须在游戏更新前保存；已有基线不覆盖。显示游戏版本未知时留空，可记录实际 Steam build ID。
2. **捕获新版本**：`python3 tools/snapshot.py capture --name <新的构建标识>`。保留三语原始 JSON、对应零协文本与哈希；零协未更新时仍能检查原文变化。
3. **比较**：`python3 tools/scope.py --new snapshots/<新的构建标识> --save out/update_scope.json`。不提供 `--save` 则只读；不是比较文本数量，也不是扫描所有历史漏译。
4. **判定**：读报告中的 `files`、`history`、`language_differences` 与 `coverage`。新增、变更、删除、移动和结构变化均核对。上游非空译文不代表已经适配新源；同 id 改数值也需要处理。
5. **建批次**：`python3 tools/batch.py create --name <批次名> --report out/update_scope.json`，复杂对齐或排除项用 `--decisions`，格式见主流程。只有此时才创建 `batches/<批次名>/patch/`。
6. **翻译与审校**：先导出上下文，完成语义与文风两轮检查，用显式编辑清单 `batch apply` 写回。
7. **验收与交付**：`batch verify`；需要本地交付时 `batch export --out <新目录>`。完成当前请求要求的交付后 `batch finish` 归档并回到等待状态。

不要把 `merge_zeroasso.py` 当作开工第一步。旧自动合并已退役；新版兼容入口只处理明确的字段编辑和事务回滚。旧 TSV 写入器也不属于当前流程。

## 翻译判断

语义以批次记录的实际源文为准，韩文优先；术语与文风用当前适用的零协实证。英文可能丢敬称、改人称或添加比喻，只作参考；没有韩文时标注实际来源。

术语先查当前版本上游原始记录，再查 `terms/confirmed_pairs.tsv`、`terms/glossary_all.clean.tsv`、`terms/术语表.md`。它们是有上下文和版本的证据，不按总频次机械决定所有语境。没有证据才拟新译，并登记依据。

- 剧情先读 `workflow/重译手册.md`，按对话回合通读。用 `ctx_dump.py <文件> --out <输出>`，各语言保持原始顺序，不能把重复/空 id 自动合并。
- RPG 用 `rpg_dump.py` 通读整组 `texts`；`texts[].speaker` 是已核实的显示名，而 `model/key/index` 等结构标识受保护，陌生结构先核对。
- 角色查 `style/角色/*.md`；机制套 `style/机制句式模板.md`；UI 查对应文体指南。
- `workflow/与零协差距教材.md` 是历史文风参考：避免加戏、吞掉称呼语气、滥用破折号。不能按历史统计强行改句子或设置每文件改动数量。
- 第二轮按 `workflow/通读润色手册.md` 修明确问题；有效继承的上游字段不顺手重写，历史语义疑点另列。

旧源对应的有效零协译文受保护；新源发生变化后，应重新判断旧译是否适用。这解决了“必须补回所有上游语义”和“任何上游字句都不许动”的旧冲突。

## 写回与检查

用 `batch.json` 给出的完整路径，编辑项含 `file/path/expected/text/reason/semantic_review/style_review`。`expected` 必须逐字符匹配当前值；不符即中止，不静默跳过。审校标志只记录实际完成的工作。

```bash
python3 tools/batch.py apply --edits out/edits.json --dry-run
python3 tools/batch.py apply --edits out/edits.json
python3 tools/batch.py verify
```

保留引擎标记、占位符、标签顺序和合法嵌套；显示用方括号例外须明确记录。`<I think …>` 是但丁正文，不是斜体标签。禁止 JSON 文本级正则清洗和跨文件全局替换。

事务会保存完整修改前文件。需要恢复时使用 `batch rollback --transaction <编号>`，按逆序执行；后续文件已改变时不会盲目覆盖。中断事务先恢复，再继续。

`verify_retrans.py` / `verify_output.py` 与 `batch verify` 检查同一个批次。没有活动批次时是“不适用”，不是0错误通过。对新工具或修复后的工具，用能触发已知问题的样例验证检查能力；已有回归测试见 `tests/test_update_pipeline.py`。

`check_speech_context.py`、`sem_check.py`、`polish_scan.py`、`check_established_terms.py` 都只提供复核线索。零命中不代表语义正确，也不需要为了消灭误报而改译文。

## 完成边界

- 查询任务：给出对应版本的证据与结论即可。
- 准备任务：原文基线已冻结，状态仍是等待更新，没有活动修改目录。
- 翻译任务：本轮范围有明确处置，结构与标记检查通过，语义和文风实际审阅并记录；输出与源版本绑定。
- 本地交付：使用全新的交付目录与文件哈希清单，保留历史版本。
- 安装/发布：仅完成当前任务要求的动作。安装前核对目标游戏仍匹配快照；不随意删除字体或用户文件，不用 `git add -A` 带入无关更改，不清空旧 ZIP。
- **发布仓库**：`../limbus-zh-10ch`（<https://github.com/haool871/limbus-zh-10ch>）。
  它是给玩家的仓库，只放 `patch/` + 安装说明 + CHANGELOG + `publish.sh`。
  发布用 `./publish.sh ../_kb/out/delivery_<批次名> v<版本>`——**要求交付目录含 `delivery.json`**
  （即必须来自 `batch export`），会先列差异再确认，且不自动 push。
  历史版本靠 git tag 保留；交付集为空时不打 tag（否则 Releases 出现空包）。
  术语库与流程文档留在知识库仓库，**不要在发布仓库里再放一份**。
  详细步骤见 `workflow/版本更新流程.md §6.1`。

源码检查不能证明游戏一定能加载，人工审校记录不能替代审校行为本身。汇报实际检查了什么，不将未执行项描述成通过。
