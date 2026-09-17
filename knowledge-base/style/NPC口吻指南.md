# 主要非罪人角色（NPC）中英说话风格指南

> 用途：把《Limbus Company》新文本（英文）译成中文时，保持 NPC 口吻、称呼、术语与既有官方汉化（零协会）一致。
> 语料：工作区 `_kb/data/corpus.jsonl`（四语按 id 对齐）+ `_kb/data/voice_samples.md`（按 kr `model` 分组的均匀采样）。所有 EN/CN 引文均为**原句复制**，未改写。
> 标注约定：`（推测）`= 未找到直接语料、由语域归纳；`EN#NN` / `文件#id` = 可回查的定位。
> 量化列（`voice_stats.json`，单位：每 100 句出现次数）仅用于横向比较，不是翻译标准。
> 排版说明：本文件正文里用「」包住被讨论的中文词句，**只是本文档的引用写法**；实际译文标点请遵循 `style/叙事与旁白.md`（弯引号 `“ ”`、省略号 `……`、破折号 `——`）。

## 总表（本文件覆盖的 NPC 及其关键标记）

| 中文名 | English | 官方 model | 关键标记 | 每百句「！」 |
| --- | --- | --- | --- | --- |
| 维吉里乌斯 | Vergilius | `베르길리우스` | 「一介向导」、浮士德女士、经理 | 0.7 |
| 卡戎 | Charon | `카론` | 第三人称自称、布隆布隆 | 0.6 |
| 东朗 | Dongrang | `동랑` | 三朝先生、哈哈 | 0.8 |
| 克罗默 | Kromer | `크로머` 等 5 个模型 | 执握之人、噗/呵呵 | 48.6 |
| 索尼亚 | Sonya | `소냐` | 那孩子、理想世界 | 3.7 |
| 亚哈 | Ahab | `에이해브` | 我的心脏、时钟脑袋 | 58.4 |
| 参孙 | Sansón | `산손` / `기사산손` | 向导、说书腔 | 1.9 |
| 贾母 | Jia Mu | `가모` | 宝玉啊、莫失莫忘 | 12.7 |
| 贾惜春 | Jia Xichun | `가시춘` | 哥哥、家主之争 | 9.8 |
| 贾丘／孔丘 | Jia Qiu／Kong Qiu | `가치우` | 子路啊、文言 | 0.8 |
| 林黛玉 | Lin Daiyu | `임대옥` | 宝玉哥哥、老太太 | 1.8 |
| 薛宝钗 | Xue Baochai | `설보차` | 宝玉、~ | 10.3 |
| 贾元春 | Jia Yuanchun | `가원춘` | 诸位、家母 | 0.7 |
| 子贡 | Zigong | `자공` | 主公、文言引用 | 0.8 |
| 手指「父辈／子辈」 | Nursefather／Apprentice | `*아비` / `*제자` | 父辈、子辈 | — |
| 耐莉 | Nelly | `넬리` | 呼呼、首席管家 | 17.3 |
| 以斯拉（埃兹拉） | Ezra | `에즈라` | 队长、老末 | 38.0 |
| 霍恩海姆 | Hohenheim | `호엔하임` | 先说结论、罪人XX | 1.1 |
| 旁白 | Narrator | `라만차내레이션` 等 | 名字牌「旁白」 | 50.0 |

---

## 维吉里乌斯 / Vergilius

- **身份**：梅菲斯托费勒斯号的向导，人称「猩红视线」，前色彩级收尾人；罪人们的实际管理者与监护人。
- **语域**：成年人的从容与讥讽。一句里通常先给结论、再补一句挖苦（中文常被拆成两个短句）。敬语与轻蔑混合，句尾高频「吧／呢／啊」。**不使用粗口、不使用「俺／老子」**。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 反讽式自贬，固定译「一介」：
    - EN: `Couldn’t say, I’m merely a humble guide who wouldn’t be in the position to know such a thing.` → CN: `无可奉告，我只是一介向导而已，没资格知道这些。`（S302B#21）
    - EN: `I’m nothing more than a guide that none pay heed to; it would be impertinent of me to brandish my weapon.` → CN: `我只是一介无人理睬的向导，还掏出武器是不是太不知好歹了。`（S304A#2）
  - 把罪人叫「孩子们／小毛孩」：
    - EN: `Of course I did. Why would I be babysitting you children on this bus otherwise? I'm not one to work for free.` → CN: `当然。你觉得我会不计较得失就到这巴士上当你们这群小毛孩的保姆吗？`（S606B#39）
    - EN: `It’s not right to ask a toddler to run when it has yet to take its first steps.` → CN: `要求一个蹒跚学步的孩子在迈出第一步后就跑并不现实。`（S004A#5）
  - 长句被拆成中文短句（重要句式习惯）：
    - EN: `This inane conversation is most riveting, but I would prefer some silence while we wait.` → CN: `废话真多。再这么等下去我脖子都要酸了。`（E719A#16）
  - 对卡戎完全换一种口气（糖果、午睡、抱怨）：
    - EN: `I’ve told you before, Charon—three separate times, actually, each time I bought you one of those candies—that people aren't allowed aboard the freight cars.` → CN: `……我不是在给你买了三次不同口味的糖果时说过了吗。货运车厢是不能坐人的，卡戎。`（E617B#42）
    - EN: `You came back later than expected. I was just about to take my first nap in a while.` → CN: `你们回来得比我预计的要晚。我正准备久违地睡个午觉呢。`
- **他对但丁／罪人的称呼；如何自称**
  - 但丁：`经理`／`执行经理`／`但丁经理`／`但丁`（语料中「但丁」49 次）。
    - EN: `I was getting worried about you, Executive Manager.` → CN: `你可真叫我担心，经理。`（E000X#65）
    - EN: `Of course, I can't hear your words, Manager Dante. It was just idle talk. The look on your face seemed to warrant it.` → CN: `我当然没听见，但丁经理。只是随口一说。因为你的表情看上去就是那样。`（4D305A#68）
  - 浮士德：**唯一固定用敬称的罪人**——`浮士德女士`（EN `Miss Faust` / `Ms. Faust`，26 次）。
    - EN: `Why don’t you give me an excuse, Miss Faust.` → CN: `浮士德女士，不妨找个借口吧。`（1D306A#75）
  - 罪人群体：`罪人们`／`你们`／`各位`（`罪人` 17 次）。
    - EN: `I will be joining them to discuss the possible solutions to this incident, so please keep the Sinners under control. Except you, Miss Faust. You're with me.` → CN: `在我和他们开会的时候，你只需要好好管理罪人们就行了。啊，浮士德女士。你与我同行。`（E603B#55）
  - 其余罪人一律直呼名字（希斯克利夫、以实玛利、良秀、堂吉诃德……）。自称恒为「我」。
- **关键台词实证**
  1. EN: `And I thought this would be an easy enough mission for you.` → CN: `我还以为这是个易如反掌的任务呢。`
  2. EN: `And I… am the guide. I decide the "where" and the "how" of our journey.` → CN: `而我是……向导。去往何方，又如何前往，则由我来判断。`
  3. EN: `Your intuition is half-right, Heathcliff.` → CN: `你说对了一半。`
  4. EN: `Dante, I can't allow them to take the company's precious assets right before my eyes now, can I?` → CN: `公司宝贵的资产就要在我眼前被夺走了，那我可不能坐以待毙对吧，但丁？`
  5. EN: `Hah, what's done is done. However, do be mindful of bringing in strangers onto this bus from now on, Dante.` → CN: `哈，既然木已成舟，那就这样吧。但以后请继续保持警惕，但丁。`
  6. EN: `Enough.` → CN: `够了。`
  7. EN: `Inquire.` → CN: `说。`
- **翻译注意点**
  1. `Miss/Ms. + 姓` 一律「女士」，这是他区分亲疏的核心手段，不能改成「浮士德小姐」。
  2. 他的讽刺靠**信息差**而不是脏话；中文不要加「哼」「切」这类轻浮语气词，正式场合只留「……哼。」（`... Hm.` → `……哼。`）。
  3. 他自称「向导」时是职业身份陈述，不要译成「导游」。
  4. 罗佳在他的台词里出现过 `罗季昂`（`I’ll entrust Rodion with the task…` → `……的任务就交给罗季昂吧。`）。罪人名以 `terms/glossary.tsv` 为准（罗佳），此处属历史遗留，**新文本统一用「罗佳」**。

---

## 卡戎 / Charon

- **身份**：梅菲斯托费勒斯的司机；把巴士当宠物，把所有人当小朋友。
- **语域**：幼儿园老师 + 电报体。短句、名词句、以逗号硬切的主谓倒装；**第三人称自称**。平均英词 6.6、中字 13.5，是本文件里最短的句子。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 第三人称自称（`카론` 出现 53 次）：
    - EN: `If Charon feels like it’s Christmas, then that's that.` → CN: `卡戎觉得现在像是圣诞节，那就是。`
    - EN: `Charon's sleepy. Excellent bus drivers don't drive while sleepy.` → CN: `卡戎，很困。优秀的巴士司机，不会疲劳驾驶。`
    - EN: `Charon forgives this time. Next time, no mercy.` → CN: `卡戎，就原谅你这一次。下次绝不轻饶你。`
  - 拟声词，固定译法：`Vroom-vroom` → 「布隆布隆」；`Weewoo weewoo` → 「嘀呜。嘀呜。」；`Screech` → 「叽——」；`Sandy pitter sandy patter` → 「扑簌扑簌」；`G-u-lp` → 「咕噜」。
    - EN: `Here we go. Vroom-vroom.` → CN: `出发，布隆布隆。`
    - EN: `Been waiting for vroom-vroom time.` → CN: `久等了，布隆布隆时间。`
  - 给所有人起外号（**不要意译成普通称呼**）：巴士=「梅菲」；格里高尔=「虫男」；罗佳=「小粉毛」；维吉里乌斯=「维吉」；但丁的时钟头=「滴答」。
    - EN: `Bug Guy. What did you put on Mephi’s head?` → CN: `虫男。你在梅菲的头上放了什么？`（1D306A#109）
    - EN: `Pinky-hair, explain why you're wagging that odd paper in Charon’s face.` → CN: `小粉毛，用奇怪的纸挡住卡戎前面的理由是什么？`
    - EN: `Looks stinky. Small girl is torturing tick-tock with stinky.` → CN: `有脏脏的味道。小女孩正在用臭味折磨滴答。`（E626B#83）
  - 幼儿园老师词汇：`Principal` →「园长老师」；`Kids` →「小朋友们」；`T-rexes` →「暴龙班」；`Early Elephants` →「大象班」。
    - EN: `No need to worry, Principal.` → CN: `担心，没有必要，园长老师。`
    - EN: `Charon never told kids to say these things. Not responsible.` → CN: `卡戎老师，没教过那种话。没有，责任。`
  - 记不住名字（用外形代替）：
    - EN: `... Charon's snacks. Mister String Bean ate up all of them.` → CN: `……那个高个子大叔，偷吃卡戎的零食。全吃光了。`（E904B#24）
    - EN: `A bus driver only snoozes at rest spots, Verg.` → CN: `巴士司机只会在休息点打盹，维吉。`
- **她对但丁／罪人的称呼；如何自称**
  - 维吉里乌斯：「维吉」；巴士：「梅菲」；但丁：「但丁」/「滴答」；罪人一律外号。自称「卡戎」（第三人称），仅在极少数正式自报身份时用「我」：`Refreshing morning. This is Charon the Bus Driver.` → `清爽的早晨。我是巴士司机，卡戎。`
- **关键台词实证**
  1. EN: `But Charon's got the helm. Hold on, everyone.` → CN: `由卡戎来操作船舵。大家都抓好。`
  2. EN: `Mephi, twinkle-twinkle like stars.` → CN: `梅菲，一闪一闪，像星星。`
  3. EN: `Careful with wishes. No take backsies.` → CN: `认真，许愿。不能反悔。`
  4. EN: `Stop getting in the way between Charon and Mephi.` → CN: `如果总在卡戎和梅菲之间插一脚的话，不好。`
  5. EN: `Charon only knows two directions: Mephi’s front and back.` → CN: `卡戎只知道两个方向。梅菲的前方和后方。`
  6. EN: `Boo. Stinky. Charon, evacuate. Evacuate.` → CN: `呜。味道好臭。卡戎躲开躲开。`
- **翻译注意点**
  1. **标点是风格本身**。中文必须保留她的逗号切分与名词句（`有脏脏的味道。`），不要合并成通顺长句。
  2. `Charon` 在中文里保持「卡戎」，不要换成「我」——她的非人称感是角色设定（她被剥夺了自我叙述）。
  3. 外号一经确定全篇不变：虫男／小粉毛／维吉／滴答／梅菲。
  4. 她模仿别人说话时保留引号：`“The Sinners will go to District 4.”` → `“罪人们将前往4区。”`

---

## 东朗 / Dongrang

- **身份**：K公司再生安瓿研究者，前九人会成员，李箱、冬柏、灵之的同门；本章的主要对手与悲剧人物。
- **语域**：研究者 + 推销员。彬彬有礼、健谈、爱自问自答；越到后期越像在给自己念台词。平均英词 15.4、中字 26.2（偏长）。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 笑：`Haha` →「哈哈」；`Ha, haha...` →「哈、哈哈……」；`Hahaha` →「哈哈哈」。
    - EN: `Haha, you might want to do a better job at remembering your part, yes?` → CN: `哈哈，你该好好背下自己的台词了吧？`（4D104B#25）
    - EN: `It all heals up in seconds. Amazing, isn't it? It only takes a short while for the pain to be gone. Hahaha.` → CN: `很快都能恢复。很神奇吧？只需一小会，痛苦就消失了。哈哈哈。`（4D204B#26）
  - 敬称同门（不会直呼年长者）：「三朝先生」「灵之」「灵之哥」「兰前辈」。
    - EN: `Take as many as you’d like. Mr. Samjo, pack some snacks from the break room into small bundles to give them later.` → CN: `想拿多少就拿多少吧。三朝先生，晚点把休息室里的零食也分成小份包装好给他们吧。`
    - EN: `Splendid, Young-ji. This level of technology could have numerous applications.` → CN: `太棒了，灵之。这种等级的技术拥有无穷无尽的用途。`（4D103B#15）
    - EN: `Brother Young-ji's glass window is already making the rounds. Researchers from other Nests have taken an interest, or so I've heard.` → CN: `灵之哥的玻璃窗技术已经广为世人所知。其他巢的研究员也表示很感兴趣。`（4D105B#35）
    - EN: `Where are your other members, Senior Researcher Ran?` → CN: `你的其他同伙呢？兰前辈？`（S418B#15）
  - 对但丁用「您」：
    - EN: `Ah, and you must be the manager… it was Dante, yes? May we speak for a moment?` → CN: `啊，您一定是执行经理……但丁吧？我能跟您说两句话吗？`
  - 自嘲／疲惫：
    - EN: `So many old friends, and not one to greet me with delight.` → CN: `无论在哪儿，都没有一个朋友对久别重逢感到开心。`
    - EN: `Ahh~ I was looking forward to the staff dinner tomorrow, I really was.` → CN: `啊~我真的很期待明天的聚餐。`
    - EN: `And you are weak. Still.` → CN: `而你很弱。一如既往。`
  - 自造/玩梗词照译：`Plumpy Chicken` → 「东东鸡」。
    - EN: `Let's see, how about Plumpy Chicken?` → CN: `让我想想，东东鸡怎么样？`
- **他对但丁／罪人的称呼；如何自称**
  - 但丁：`执行经理……但丁` / `但丁`（4 次）。
  - 李箱：直呼`李箱`（9 次）——他是少数对李箱不用敬称的人（同门）。
  - 冬柏：直呼`冬柏`；三朝：`三朝先生`；灵之：`灵之`/`灵之哥`；兰：`兰前辈`；仇甫：`仇甫`。
  - 自称「我」，对但丁时用「您」，**不使用「本研究员」之类自抬称谓**。
- **关键台词实证**
  1. EN: `Ah, to start with an explanation of the technology I invented...` → CN: `啊，请让我先说明一下我所发明的技术……`
  2. EN: `Don't be so sour, Dongbaek. Liveliness is good to have.` → CN: `冬柏，别说这种话。有活力可是件好事。`
  3. EN: `...It was me, Dongbaek. I sold the League out.` → CN: `……是我，冬柏。是我出卖九人会的。`
  4. EN: `I don't think... it'll recognize me...` → CN: `我不觉得……它还认得出我……`
  5. EN: `So it comes down to this. I'll probably die soon.` → CN: `这样啊。我大概不久于人世了吧。`
  6. EN: `There just were never enough tears.` → CN: `泪水长流，却总觉得不够。`
  7. EN: `Why are you displeased about it? You're the one who turned down Brother Young-ji's offer to go with him, Dongbaek.` → CN: `你为何这么不高兴？坚决拒绝和灵之哥一起去的提议的人不是你吗，冬柏。`（4D202B#5）
- **翻译注意点**
  1. 他的「哈哈」在 4 章前半是真笑、后半是硬撑；不要统一成一种情绪。
  2. 「九人会」是固定专名，不要写成「九人联盟」。
  3. 对但丁的「您」必须译出，这是他「研究员对上客户」的姿态。
  4. `the manager` 在第四章语境里是「执行经理」，不是「经理」——官方在这里用全称。

---

## 克罗默 / Kromer

- **身份**：N公司异端审判官，「钉与锤」的执握者；辛克莱少年时期的噩梦。
- **语域**：癫狂的高亢少女。感叹号密度 48.6/100（本文件第二高），笑声密集，句尾爱用「啊/吧/呢」。她的可怕来自**真诚的快乐**。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 口头禅：
    - EN: `I am the one who grips.` → CN: `可我才是执握之人啊。`（S317B#84）
    - EN: `No, Sinclair! It's always been the other way around... I am the one who grips...!` → CN: `不不，辛克莱！虽然一直如此……可我才是执握之人啊……！`（S448B#26）
    - EN: `It’s not even time yet…` → CN: `时机尚未成熟……`（3D309B#3）
  - 笑声分四档，**不能一律译「哈哈」**：`Pfh` → 「噗」；`Ufu` → 「唔呼」；`Kuhuu` → 「呵呵」；`Pwahahaha` → 「噗哈哈哈」。
    - EN: `Pfh… Ahahaha!!` → CN: `噗……啊哈哈哈！！`
    - EN: `Ufu.` → CN: `唔呼。`
    - EN: `Kuhuu… Oh, Sinclair…! When did you learn to act so tough? That’s not like you at all… What a riot… Pfft.` → CN: `呵呵……辛克莱……！你什么时候学会了这种话？真不像你……好奇怪……噗……`
    - EN: `Pfh… Pwahahahaha!!` → CN: `噗……噗哈哈哈！！`
  - 宗教狂热词：`heretics` → 「异端」；`the offering` → 「祭品」；`sacred rite` → 「神圣的仪式」；`impure` → 「不纯之物」。
    - EN: `Not only are those heretics disturbing our sacred rite, they are now after the offering that is rightfully ours to consecrate!` → CN: `这些异端不仅要扰乱我们神圣的仪式，甚至还在觊觎我们宝贵的祭品！`（3D301B#18）
    - EN: `Let those impure things be, Guido. It’s their survival instincts kicking in.` → CN: `别管了，圭多。那是不纯之物特有的生存本能在作祟。`（3D306B#15）
  - 少女时期的试探腔（`학생크로머`）与正文/血污版（`피묻은크로머`）要分层。
    - EN: `Yo, Sinclair… You don’t actually wanna take the replacement procedure, do you?` → CN: `辛克莱，你其实不想……接受义体手术，对吧？`（3D302B#20）
    - EN: `Because I’m a humanitarian who loves all things human!` → CN: `毕竟我是爱着人类的博爱主义者啊！`
- **她对但丁／罪人的称呼；如何自称**
  - 辛克莱：反复直呼`辛克莱`（9 次，占她称呼的绝对多数）；圭多直呼`圭多`；罪人群体作「诸位」「各位」（`来，诸位！听好了！` ← `Alright, everyone! Listen up!`）。自称「我」。
- **关键台词实证**
  1. EN: `Go forth and die! Do not fear your end!` → CN: `去吧！杀了他们！无须畏惧死亡！`
  2. EN: `As long as the offering of gold is with us, you shall be brought back to life again and again!` → CN: `只要有了这黄金的祭品，你们便能永无止境地复生！`
  3. EN: `Hurry over. You belong in my hands.` → CN: `快过来。快到我的手心里来。`
  4. EN: `Ahaha, don’t give me that look.` → CN: `啊哈哈，别那样瞪着我啊。`
  5. EN: `You won’t run away this time, will you?` → CN: `这次，你不会逃跑了吧？`
  6. EN: `Brings you back, doesn’t it, Sinclair?` → CN: `辛克莱，这样做会不会让你回想起往昔？`
  7. EN: `Your face back then was real priceless.` → CN: `你那时的表情真的十分精彩啊。`
- **翻译注意点**
  1. 笑声必须分档（噗／唔呼／呵呵／噗哈哈），同一段里连续笑不要合并。
  2. 学生时期用「你」的亲近感，正文里同一句「你」要带压迫感；不要把学生克罗默译得和老克罗默一样疯。
  3. `the one who grips` 是跨章反复出现的核心台词，**固定译「执握之人」**，不要换成「握住的人」「掌控者」。
  4. 她的审判官说话对象是「诸位」而不是「各位罪人」；不要给她加上罪人编号。

---

## 索尼亚 / Sonya

- **身份**：原诺言者／革命思想者，罗佳的旧识，主张用「理想世界」改造都市。
- **语域**：冷静、有教养的理想主义者，介于导师与敌人之间。布道腔 + 引导式反问；感叹号极低（3.7/100）。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 「那孩子」——他对罗佳的固定亲昵称呼（`那孩子` 与 `罗佳` 并存）：
    - EN: `And one more thing… That child will soon visit you, too.` → CN: `还有……很快那孩子也会来找你的。`（2D306A#19）
    - EN: `She still has a long way to go, that's all.` → CN: `那孩子还有很长的路要走。`（2D306A#84）
  - 「世界」「理想」「为了」——他的布道词根：
    - EN: `… I showed Rodya that world.` → CN: `……我向罗佳展示了那个世界。`
    - EN: `The same ideal reality that I fell for.` → CN: `那个令我着迷的理想世界。`
    - EN: `If a clear path towards prosperity of the many shows itself before my eyes, I’ll take it without hesitation.` → CN: `若是有一条能让大多数人富裕起来的明确道路展现在眼前，我会毫不犹豫地选择它。`
  - 以反问下结论，句尾「吧」：
    - EN: `Silence sometimes speaks volumes. I’ll take that as a positive.` → CN: `沉默有时暗示着肯定。那我就这么认为吧。`
    - EN: `Don’t expect me to act on the same impulse of kindness next we meet, though.` → CN: `不过，别指望着我在下次见面时还会有这种善意的冲动。`
  - 对同伴也不失礼、但会冷下来：
    - EN: `You should know, Hermann, that I’ve never been a friend of capital.` → CN: `你知道的，赫尔曼。从以前开始，金钱就并非是我的朋友。`
    - EN: `It seems the method you suggested was wrong after all, Hermann.` → CN: `看来你说的方法还是错了啊，赫尔曼。`
- **他对但丁／罪人的称呼；如何自称**
  - 罗佳：`罗佳`（21 次）或`那孩子`；但丁：`但丁`；赫尔曼直呼`赫尔曼`。自称「我」——**不用「在下」**（`在下` 的命中率是 0.9/100，来自他处，非其标志）。
- **关键台词实证**
  1. EN: `Leave this to me.` → CN: `这里交给我吧。`
  2. EN: `It’s just like how you simply couldn’t hold yourself back from using your axe that day.` → CN: `就像那天你不由自主地挥下了斧头一般。`
  3. EN: `Dante, I take it that your organization is working to make a better world in its own right, yes?` → CN: `但丁，你们的组织也是为了创造一个更加美好的世界吧？`
  4. EN: `Yes, I mean that boy who left quite the impression on you. It’ll be a touching reunion, I imagine.` → CN: `没错，就是那个给你也留下痕迹的孩子。会是场令人怀念的再会吧。`
  5. EN: `Rodya never wished for a perfect, flawless utopia.` → CN: `罗佳想要的并非是一切全都完美的理想世界。`
  6. EN: `I’m well aware of the sheer weight of pain and guilt you’ve been burdened with ever since then.` → CN: `我知道你自那天起，度过了多么痛苦，而又被罪恶感折磨的日子。`
  7. EN: `It's okay, Rodya.` → CN: `都没关系的，罗佳。`
- **翻译注意点**
  1. 他不能译成黑帮或邪教头目：他的用词是**政治哲学**而非教团口号（`理想世界`／`财富的再分配`）。
  2. 「那孩子」是关键标记，不能因为罗佳已成年而改成「那位」或「她」。
  3. 把「罗佳」与他口中的「罗季昂」区分：本作固定用「罗佳」。

---

## 亚哈 / Ahab

- **身份**：裴廓德号船长、裴廓德镇镇长，以猎杀白鲸为唯一信条。
- **语域**：船长演说体 + 狂热信仰。感叹号密度 58.4/100（本文件最高），祈使句、宣誓句、自我指名句密集；平均英词 17.4（最长之一）。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 「我的心脏」「那颗心脏」——把白鲸心脏宗教化：
    - EN: `The heart. The heart that seeps with all that is evil in the world.` → CN: `心脏。喷涌邪恶的，恶毒的心脏。`（5D106B#71）
    - EN: `... Is my heart.` → CN: `是我的心脏。`（5D107B#24）
  - 「命运」——一切偶然都归因于宿命：
    - EN: `But that is the whims of fate! These seemingly implausible, coincidental opportunities are the threads of fate weaving the path ahead for us!` → CN: `但是，正因为那些令人吃惊的机遇如此偶然，才会被称为命运！`（5D107B#2）
    - EN: `I have naught else to say but merely refer to the nature of fate. The threads of fate itself is weaved so that I, Ahab, shall be the one to pierce the heart of the Pallid Whale.` → CN: `所谓命运，有时候不就是这样的么。而我的命运则注定着我将成为那个贯穿白鲸心脏的人。`（5D106B#79）
  - 自报名号的长同位语（中文必须完整保留职位链）：
    - EN: `I, Captain Ahab of the Pequod, the leader of the Pequod Town, have a responsibility to bring every single one of my crew home. Thus I make this offer to you.` → CN: `身负救出所有这些船员们的义务的……我，裴廓德号的船长兼裴廓德镇的镇长亚哈，对你们发出的提案。`
  - 笑：`Haha!!` →「哈哈！！」；`Ha! Ahahahaha!!` →「啊哈，啊哈哈哈！！」
    - EN: `Haha!! Lads, lasses! Cast fear from your hearts.` → CN: `哈哈！！别老用那么害怕的表情看着我啊。`
  - 「我的船员们」＝他的所有物：
    - EN: `My crew is nothing if not loyal. More so than anyone in the world.` → CN: `我的船员们比任何人都忠心耿耿。`
    - EN: `I send them to greatness, not death.` → CN: `我让他们迈向伟大，而不是死亡。`
- **他对但丁／罪人的称呼；如何自称**
  - 以实玛利：直呼`以实玛利`（15 次，占绝对多数），必要时称「优秀的水手和鱼叉手」。
  - 但丁：`你这颗时钟脑袋`（`your clock-head` → `你这颗时钟脑袋`，5D301A#18）。
  - 但丁一行的其他罪人：`你们`／`孩子们`；魁魁格、斯达巴克直呼其名。
  - 自称「我」，且经常以「我，亚哈」的形式自报家门，并把职位（船长／镇长）说全。
- **关键台词实证**
  1. EN: `Welcome. I have built this village and watched over these poor, wretched souls. Soon, I shall set sail on the final voyage with my crew.` → CN: `我是照顾着这些可怜的船员，建立了这个镇子，并即将要带领这些人投身于最后的航海的船长。`
  2. EN: `I, Captain Ahab, cannot be deceived! That thing in your clock-head... is a piece of that Golden Bough, is it not? It is that Golden thing that counteracts the Pallidification effects! Am I wrong in assuming that this is how you and your crew have remained untouched by its effects?!` → CN: `没人能骗过我亚哈的眼睛！你脑袋里装着的，是能够中和白化现象的金色碎片之一。我有猜错吗？所以你们才没有变成人鱼！`（5D302B#20）
  3. EN: `I am the only one who matters. What matters is that I have declared this beast evil—and that is my commandment, my belief, my religion, and my creed.` → CN: `最终，这世上最为重要的还是我，是我自己！重要的是我将其宣言为恶，那是我的法则、我的观念、我的宗教、我的信条。`
  4. EN: `I gave your worthless lives a reason to go on. And on the Pequod, you sailed with conviction!` → CN: `是我将你们这群废物集合起来，让你们乘上裴廓德号，为你们创造了生存下去的理由！`
  5. EN: `Shoot.` → CN: `问吧。`
  6. EN: `Let this be a good voyage to us all.` → CN: `祝所有人，一路顺风。`
  7. EN: `My friends. Is there not something out there, past this Pallid Whale's flesh, that awaits your return?` → CN: `你们所有人，都有活着离开这里的理由吧？`
- **翻译注意点**
  1. 感叹号密度是角色核心。中文不要为了「书面化」而削掉感叹号；他的演说本来就是喊出来的。
  2. 他的可怕在于**逻辑自洽的真诚**。不要加「阴险」「狞笑」这类旁白式修饰，也不要让他像杂鱼反派那样放狠话。
  3. `Pallid Whale`／`Pallidification` 用固定专名：白鲸／白化现象。
  4. 中段他在「船长？」（`Captain?`）这种署名下出现时仍用同一口吻，不要因为署名变化而改风格。

---

## 参孙 / Sansón

- **身份**：拉·曼却领的向导与解说人，「白月骑士」的扮演者；Canto 7 的说书人。
- **语域**：舞台主持人 / 说书人。文雅、夸张、古语多（EN：`verily`, `thee`, `hath`, `pray`, `aught`）；中文用「言予君王」「令人惋惜」这类文言/书面腔，而不是「汝／尔」。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 提议式开场：「让我们……吧」「既然如此，让我们……」「其名为……」：
    - EN: `Let us watch how this tale plays out.` → CN: `让我们慢慢欣赏一遍吧。`
    - EN: `Let's call it...` → CN: `其名为……`
    - EN: `Then how about we share a few select adventures you found particularly memorable?` → CN: `既然如此，让我们来举出其中几个令人印象深刻的冒险吧？`
  - 观众称呼：「各位」「你们」「来宾」「客人」：
    - EN: `Now, now. Let's try to focus on this adventure, shall we? Otherwise, Don Quixote, as brave an adventurer this hero may be, cannot fend off this whole horde of bandits all alone.` → CN: `现在，请各位集中注意力到冒险故事上。否则，盗贼太多的话，就连勇敢的冒险家堂吉诃德也难免陷入苦战。`
    - EN: `What misfortune! Every clue that may have shed light on the secrets of this tragic kingdom's history has all been pulverized by the guests who passed through before you.` → CN: `令人惋惜，与王国的秘密相关的线索已被先前经过的来宾们尽数摧毁。`
  - 自称永远是「向导」而不是「我」：
    - EN: `You have gone there and back again on all kinds of adventures, yet I am but a mere guide and a greeter here at La Manchaland, a place of blossoming smiles and dreams.` → CN: `你是在经历众多冒险后终于回归之人，而我正如你所见，只是一位在充满幸福笑容与梦想的世界，在这拉·曼却领中迎接客人的向导。`
    - EN: `My name is Sansón, and I will be your guide on your visit here at La Manchaland. 'The Knight of the White Moon' is nothing more than a role I play.` → CN: `我是……带领各位游览拉·曼却领的向导，名叫参孙。白月骑士不过是我演的一名角色。`
  - 剧本内的古语台词要保留文白混搭：
    - EN: `The knight, at want of any reason to refuse this request, said as such: "O honored king! Verily, I shall regale thee with tales of the worlds I've witnessed, the adventures I've undertaken!"` → CN: `骑士没理由拒绝王的请求。骑士说道：“我所见证的世界，我所经历的冒险，都将言予君王！”`
    - EN: `Shame, shame. Why did you not keep a close eye on something so important, something you had to go through so much to claim?` → CN: `哎呀。得到的宝物越是贵重，就越应该珍重地去守护。`
- **他对但丁／罪人的称呼；如何自称**
  - 罪人一行：「各位」「你们」「来宾」「客人」；堂吉诃德直呼`堂吉诃德`（13 次）；旁及「家族」「长老们」。自称「我」，但功能上等同于「向导」。
- **关键台词实证**
  1. EN: `It pains me terribly to see you in such dire states, my Relatives.` → CN: `真是令人心痛啊，我的亲戚们。`
  2. EN: `Ah, can't have dead silence on the stage. Let's keep things moving and head on to the next tale, shall we?` → CN: `哎呀，舞台安静下来了。该进入下一话了吧？`
  3. EN: `I will spark the flame again and again should it go out.` → CN: `每当那光芒消失之时，我都会将其再次点亮。`
  4. EN: `Lonely mornings, silent nights. The king's heart forever a hollow void.` → CN: `冷清的朝阳与寂静的夜晚。王的内心每一天都充满了空虚。`
  5. EN: `I intend to enjoy this play for a little longer.` → CN: `我打算再欣赏这出戏剧一段时间。`
  6. EN: `Mm. You seem quite peeved that such a role would go to someone such as myself.` → CN: `嗯。看来你似乎不太满意由我饰演这个角色。`
- **翻译注意点**
  1. `Verily / thee / hath` 不译成「汝／尔／矣」堆砌，中文用**书面四字格 + 古典句式**即可（「都将言予君王！」）。
  2. 他有 35 句的署名是 `Narrator / 旁白`（见「旁白」节）。**同一人物、两种署名，口吻不变**：场内解说腔与说书腔是同一个人。
  3. 「拉·曼却领」的间隔号是固定专名写法，不要写「拉曼查兰」。
  4. 他在 S719B 的 `在下片区域` 是「在 + 下片区域」，**不是**谦称「在下」；不要误当作他的自称。

---

## 贾母 / Jia Mu（鸿园的家主）

- **身份**：鸿园贾家当代家主、大观园最高权威，正准备让出家之位。
- **语域**：古雅/文言底色的家族长老。短句、命令式，四字格多；对宝玉柔软。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 「宝玉啊」——对宝玉的固定呼语：
    - EN: `Little Baoyu. You must have walked and toiled tirelessly on your journey home.` → CN: `宝玉啊。你经历了一段多么艰难而坎坷的旅程啊。`
    - EN: `Little Baoyu. Do not let these empty words stir you.` → CN: `宝玉啊。你为何总在聆听那些空虚的话语呢。`
  - 四字命令 / 格言体：
    - EN: `Lose not, forget not.` → CN: `莫失、莫忘。`
    - EN: `To be rash in judgment is to judge incompletely.` → CN: `草率决定必然有失。`
    - EN: `You will wait.` → CN: `静待片刻。`
    - EN: `Enter the fabric threshold.` → CN: `越帘入内。`
  - EN 内嵌中文谚语时直接落地（EN 原文为两行：正文 + 独立一行小字 `(不是不报, 时候未到)`）：
    - EN: `<b><i>If aught be owed, a swift vengeance shall arrive in time; it is simply yet to return.</i></b>` / `(不是不报, 时候未到)` → CN: `不是不报，时候未到。`
  - 柔软 vs 威严的落差：
    - EN: `Dear Baoyu, our peerless treasure, tarry not overlong in this mundane world; leave when the time is right, and fulfill your worth.` → CN: `我们绝无仅有的无价之宝啊，不要于此尘世久留，时机一到便再次踏上旅程，去实现你的价值吧。`
    - EN: `What could a frivolous thing like your puerile heart possibly do... before the great will of Hongyuan...?` → CN: `在鸿园的伟大意志下……你的心又能做到些什么呢……`
  - 自述身位：
    - EN: `Many scores ago, I ascended to the seat of Jia Mu with a stroke of fortune. Yet, a lifetime has passed since I assumed this great responsibility; such as it is, I seek to abdicate and walk the path of mountains and streams as a river does.` → CN: `我，昔日曾被好运眷顾而登上家主之位，被尊为贾母。经过如此漫长的岁月，如今我打算将此位出让，意在云游山河。`
- **她对但丁／罪人的称呼；如何自称**
  - 宝玉：`宝玉`／`宝玉啊`；惜春：`惜春`；王夫人：`王夫人`；罪人一行在她口中是「宝玉麾下之人」。
  - 自称「我」。他人对她的称呼分三档：旁白与家人称 **`老太太`**（林黛玉、薛宝钗语料中均为「老太太」）、正式场合自称与公文用 **`贾母`**、名字牌用 **`鸿园的家主`**。
- **关键台词实证**
  1. EN: `Have you paid visit to the revered elders, then?` → CN: `给长辈们请过安了吗。`
  2. EN: `Lady Wang, ascend here as well.` → CN: `王夫人，你也过来。`
  3. EN: `You are our family's one and only jade.` → CN: `你是我们家族独一无二的玉。`
  4. EN: `Have you brought us aught to prove that the answer indeed exists?` → CN: `我相信你们都已经尽了全力。`
  5. EN: `I wish not to lose either—our treasure, and a clue to immortality.` → CN: `不论是我们的宝贝还是不老不死的线索，我都不愿失去。`
  6. EN: `Now that you have revealed your intent, withdrawal is no longer an option.` → CN: `你既表明来意，便已无处可退。`
- **翻译注意点**
  1. **她全篇几乎不用人称代词**（语料中 CN 只出现 1 次「她」，0 次「他」）。翻译时优先用「老太太／家主／贾母」或直接省略主语。
  2. EN 出现过把「贾母」写成 `Jia Mu(家母)`（ruby 标中文）的双关：
     - EN: `The responsibilities tied to the venerable seat of the Hierarch, Jia Mu(家母), are matched only by the great power bestowed upon it. Thus, how are we to leave the matters of the Wing to someone who is, so evidently, unprepared for the task?` → CN: `家母之位向来位高权重。你连基本的准备都没做好，又怎能将政务交由你手。`
     这里的「家母」是文字游戏，**不要改成「贾母」**；但同一人物在他处仍作「贾母」。
  3. 她的文言是**克制的**，不要写成之乎者也的滑稽腔；命令句要短。

---

## 贾惜春 / Jia Xichun

- **身份**：贾家年轻一代，家主评审的胜出者，宝玉的妹妹。
- **语域**：直率少年 + 傲娇。对兄姐用亲昵称呼，对外人冷硬断言。感叹号 9.8、问号 33.0/100，反问多。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 称呼标记：「哥哥」「元春姐姐」「环哥哥」：
    - EN: `I see. You're looking for my big brother, huh?` → CN: `原来你是在找哥哥啊？`（E724B#30）
    - EN: `... Yeah. I guess you haven't been spending your time chasing the clouds out here, brother.` → CN: `……是啊。或许你并非只是一直生活在浮云之上呢。哥哥。`（7D102A#73）
    - EN: `If anyone's going to be held responsible, don't you agree that the blame should fall squarely on whoever decided to send the snakes to that particular location at that specific time, big sister Yuanchun?` → CN: `若要追责，就将其归咎于偏偏在那个时间和地点放出蛇的人吧，元春姐姐。`
    - EN: `Oh, right. There's big brother Huan, too—he won't go down easy, either.` → CN: `对了，环哥哥也不好对付。`（8D204B#51）
  - 硬话与自嘲并存：
    - EN: `Haah, this is way beneath me. I don't even want to address you as my senior, either.` → CN: `哈，和你还真是没什么好说的。我也不会叫你哥哥之类的。`（E726B#4）
    - EN: `Ugh... I feel like I've aged ten years all at once.` → CN: `啊……感觉一下子就老了十岁。`
    - EN: `Hmph. I'm not you, big bro. I pay attention in class.` → CN: `哼，当我是哥哥那样的人吗？我有在好好听啦。`
  - 家主之争的自我定位：
    - EN: `Become my faction for the duration of the Family Hierarch evaluations. Help me out.` → CN: `在这场家主之争中，加入我的阵营。你们来帮我。`
    - EN: `Do you even understand why we call it a ‘war’ when the official name for it is an ‘evaluation’?` → CN: `你知道我们为什么明明有“家主评审”这个正式的称呼，却称其为家主之争吗？`
  - 对但丁先确认再接纳：
    - EN: `You're Dante... right? Let's make this thing work.` → CN: `但丁……对吧？今后还请多多关照。`
- **她对但丁／罪人的称呼；如何自称**
  - 宝玉 = `哥哥`（偶尔「宝玉哥哥」）；元春 = `元春姐姐`；贾环 = `环哥哥`；但丁 = `但丁`；侍从 = `卫`。自称「我」，**不用「本小姐」**。
- **关键台词实证**
  1. EN: `Don't bother saying goodbye. It'll be a waste of time.` → CN: `麻烦的道别就省略掉吧。`
  2. EN: `You should consider yourself lucky that it's me who you ran into. If it was one of our other older siblings, your pretty head would already be rolling in the dirt.` → CN: `你应该庆幸这次遇见的是我。换作是其他的哥哥姐姐，你那漂亮的脑袋早就落地了。`
  3. EN: `But I don't care about either of those. What I'm looking for is a specific piece of information I came all the way in here for.` → CN: `但我不同。我有需要的情报。我是为了得到那情报才进入这里。`
  4. EN: `... that you couldn't care less about becoming something like the Family Hierarch.` → CN: `明明摆着一副比谁都对家主毫无兴趣的脸……`
  5. EN: `Tomorrow, we'll be... we'll really be enemies.` → CN: `到了明天……我们就是真正的敌人了。`
  6. EN: `Inadequate I may be, but I am still the Chief Executive Director here at H Corp., and you, dear big sister, are a temporarily visiting outsider from Q Corp.` → CN: `毕竟我再怎么不足也是鸿园的代表，而姐姐不过是从Q公司暂回故乡的外人。`
- **翻译注意点**
  1. 「哥哥」是她最高频的身份标记，**不能省略或改成「兄长大人」**；「元春姐姐」「环哥哥」同理。
  2. EN 用 she/her 稳定指代她；中文可用「她」或名字，偶尔「那家伙」（她的自嘲语境）。
  3. `Family Hierarch Evaluation`（官方名）译「家主评审」，`Family Hierarch war`（俗称）译「家主之争」——两者不可互换。
  4. 正式场合她自称「鸿园的代表」，不要因为她年轻而加「小女子」。

---

## 贾丘／孔丘 / Jia Qiu (Kong Qiu)

- **身份**：小指的构想者、以「仁」为道的思想家，大观园的幕后布局者；在别处被称为孔丘。
- **语域**：本作最重的文言腔。EN 用 `ere / afore / shall / 倒装`，CN 用「唯／岂／此乃／......啊」。句长中等但停顿多（EN 词 13.6）。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 呼弟子名 + 「啊」：
    - EN: `That is enough, Zilu.` → CN: `子路啊，够了。`
    - EN: `How long will you remain in slumber, Zilu?` → CN: `子路啊，你要睡到什么时候。`
    - EN: `... Zigong. That would not have resolved anything; it would have only caused further loss, no more.` → CN: `……子贡啊。那个方法解决不了任何问题，只会失去更多。`
  - 成语 / 古语落地：
    - EN: `Jia Baoyu, you will beget great suffering by endeavoring to embrace beyond your abilities.` → CN: `贾宝玉。人心不足蛇吞象。`
    - EN: `How can one speak of the fathoms of a lake when all they have seen is the water's surface?` → CN: `只见静水，又怎能知其流深？`
    - EN: `Not to mention how unbecoming of the lord of Hongyuan it would be for him to weep and guffaw at such little, insignificant things.` → CN: `何况执掌鸿园之人，岂能因一喜一忧而动摇。`
    - EN: `Withdraw now, Zilu. It seems that a brutal winter must come afore I am to estimate the green within him.` → CN: `退下吧，子路。若无一场严冬，便无法测度弟弟的苍翠。`
  - 概念词：「道路」「仁」「虚无」「留白」：
    - EN: `What did you see? What shape did my 'Way' take in your eyes?` → CN: `在你眼中，我的道路是怎样的呢？`
    - EN: `In nihility, everything becomes consumed by the monotonous, gray meaninglessness; but an empty canvas can be painted anew.` → CN: `若是虚无，那一切都只会变得干燥乏味，但若是留白的话，就可以慢慢填补。`
    - EN: `Indeed. As one of the Pinky, I intend to change the world with the Way of true humanity.` → CN: `没错。我打算置身于小指，以仁为本，进而图变。`
- **他对但丁／罪人的称呼；如何自称**
  - 宝玉 = `贾宝玉`（正式）／`弟弟`；子路 = `子路`；子贡 = `子贡`；贾环 = `贾环`；惜春 = `那孩子`／`贾惜春`；但丁一行 = `你们`。自称「我」，并用「唯有我」这种强调式。
- **关键台词实证**
  1. EN: `Still your insolent tongue, Jia Huan. You possess not even an inkling of the path ahead.` → CN: `前途未卜，不要轻易开口，贾环。`
  2. EN: `I was deprived of those who would stand with me, for I was wanting in the fortune with matters of people; thus, I sought out the new, embraced them, and learned much.` → CN: `我缺乏仁德，身边才无一人留存，因此我只是亲身行动，拥抱新事物，从中学习而已。`
  3. EN: `However, Jia Baoyu... I must doubt the truthfulness behind your words. For you... do not know poverty.` → CN: `但，贾宝玉。我不认为你是真的在谈论贫困。你……不知道什么是贫困吧。`
  4. EN: `... then I would not have given you the power to elect the Hierarch.` → CN: `我是不会将成为家主的手牌交给你的吧。`
  5. EN: `You've done it, little brother.` → CN: `你做到了，弟弟。`
  6. EN: `Hurry her ascension to the throne.` → CN: `加快家主的任命。`
- **翻译注意点**
  1. **他几乎不用性别代词指人。** EN 的 `her / she` 到中文全部转为身份或名字：
     - EN: `... they will attempt to cut off her head before she gains full control of the Hierarch's Heishou Pack.` → CN: `在新任家主驱使黑兽之前，或许贾惜春的头便会被斩下。`
     - EN: `Our task is not over until she ascends to the seat of the Family Hierarch and seizes the Heishou Packs' leash.` → CN: `如果不让那孩子坐稳家主的位置，牢牢握紧黑兽的辔头，事情就不会结束。`
     - EN: `Hurry her ascension to the throne.` → CN: `加快家主的任命。`
     这是「忽男忽女」问题的关键 —— **照搬「她」是错的**。
  2. 名字牌有两套：`孔丘 / Kong Qiu`（31 句）与 `贾丘 / Jia Qiu`（7 句）。同一人物，**按当前场景的署名选译名**，不要统一。
  3. 「黑兽」「辔头」「小指」是固定专名，参 `terms/glossary.tsv`。

---

## 林黛玉 / Lin Daiyu

- **身份**：林家出身的执刀者，隶属薛宝钗阵营，宝玉的旧识。
- **语域**：文静克制、带距离感的敬语；沉默多、省略号多（152.4/100，本文件最高）。情绪爆发时句子骤短。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 呼人：「宝玉哥哥」「宝钗小姐」「老太太」：
    - EN: `You...?` → CN: `宝玉哥哥……？`
    - EN: `Big brother Baoyu.` → CN: `……宝玉哥哥。`
    - EN: `... Miss Baochai.` → CN: `……宝钗小姐。`
    - EN: `So how did Jia Mu come to know them with such detail?` → CN: `所以老太太是怎么知道哥哥的一切的呢？`
  - 自我贬抑与格言：
    - EN: `I believe that the smallest speck of greed lies at the origin of all misfortune.` → CN: `所有祸端……似乎都始于微不足道的贪念。`
    - EN: `I am but a blade serving a clan from the Xue family.` → CN: `现在不过是为薛家执刀罢了。`
    - EN: `What cannot be mine must remain out of my sight...` → CN: `若无法归我所有，不如永远不见为好……`
  - 正式行礼时的谦辞：
    - EN: `Ah! Apologies for the delayed greetings. Daiyu of the Lin family formally extends her greetings to the venerable Hierarch.` → CN: `啊！失礼了。林家黛玉，拜见家主大人。`
- **她对但丁／罪人的称呼；如何自称**
  - 宝玉 = `宝玉哥哥`（最高频）；宝钗 = `宝钗小姐`；贾母 = `老太太`；贾政 = `少爷`（`I wanted to prove to him that he was wrong.` → `我想告诉少爷，他的话错了。`）。自称「我」。
- **关键台词实证**
  1. EN: `The walls came out of nowhere—excuse me. My inattentiveness has separated me from the rest of the clan.` → CN: `因为突然出现的墙壁……不，我是因为自己的粗心大意与所属势力失散了。`
  2. EN: `Silence again. Just like then... Just like when you refused to tell me anything to the end.` → CN: `你以前……也和现在一样一言不发。`
  3. EN: `You know that's not what I wanted to hear.` → CN: `你也知道我想听到的不是那种话，哥哥。`
  4. EN: `You... weren't the only one who lost those who were important to them in the annihilation of the Kong family.` → CN: `在孔家灭门之日失去了重要之人的……不只有哥哥……`
  5. EN: `Everything I did that day, including accompanying you, was... under Miss Baochai's orders.` → CN: `之前与各位同行全部都是……宝钗小姐的命令。`
  6. EN: `Those silver spoons were custom-made at Daguanyuan's request; a must-have item for children of the four great houses, they can detect non-sulfuric poison as well.` → CN: `宝玉哥哥手里的银匙……是大观园特别铸造的定制品。即便是不含硫元素的毒药也能检测出来，是四大家族的富家子弟们的必需品。`
- **翻译注意点**
  1. 「老太太」是零协会对贾母的固定旁称，**不要改成「贾母大人」**。
  2. 她的省略号密度是角色特征，不要为了通顺而删。
  3. 「宝玉哥哥」是四个字一体的呼语，中间不加逗号。
  4. 她与宝玉的关系台词（"You know that's not what I wanted to hear."）EN 省略了称呼，CN 补了「哥哥」——**这种补称呼的做法可以延用**，是官方风格。

---

## 薛宝钗 / Xue Baochai

- **身份**：薛家代表、家主候选人之一，宝玉的青梅，表面温软、内核执拗。
- **语域**：大家闺秀 + 少女语气「~／啦／呀」，底下是强烈的占有欲。感叹号 10.3/100。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 句尾波浪号「~」（EN 的 `~` 必须保留）：
    - EN: `Don't worry~ We're not so easy to kill.` → CN: `没关系啦~那种程度的话我们是不会死的。`
    - EN: `Fine, fine~`（以斯拉语料）与她的 `~` 同源：中文一律保留半角 `~`，不改成「～」或删除。
  - 直呼「宝玉」＋家族旁称：
    - EN: `No way! I'm not leaving Baoyu to fend for himself!` → CN: `不行！我要是逃走了那宝玉不就会有危险吗！`
    - EN: `Baoyu, remember how Jia Mu and my mother agreed that we would be wed should you return to Daguanyuan?` → CN: `宝玉，老太太和妈妈不是说过吗？只要你回到大观园，就会为我们定亲。`
  - 甜软与执念的落差：
    - EN: `I'm not angry. I'm just sad.` → CN: `我没有生气。只是在伤心。`
    - EN: `Baoyu said that he... smells no fragrance from me anymore.` → CN: `宝玉说我……什么香气都没有了。`
    - EN: `But I... I want the same bird I kept in my cage... That's the bird I liked...` → CN: `可我……我喜欢的是原来那只，一直待在我的鸟笼里的小鸟啊……`
    - EN: `We can't just let go—we can't stand emptiness. My brother couldn't, my parents couldn't.` → CN: `放弃这种事，我们做不到。我的哥哥做不到，我的双亲也如此。`
  - 场面话（开会时）与私话（对宝玉）判若两人：
    - EN: `Xue family, too.` → CN: `薛家也无异议。`
    - EN: `Then you smiled, your jewel-like eye glimmering.` → CN: `说这话时你便笑了，眼睛如同宝石一样闪闪发亮。`
- **她对但丁／罪人的称呼；如何自称**
  - 宝玉 = `宝玉`；黛玉 = `黛玉`；贾母 = `老太太`；母亲 = `妈妈`；元春 = `元春姐姐`；贾环 = `环哥哥`；薛蟠 = `薛蟠哥哥`；惜春 = `惜春`。自称「我」。
- **关键台词实证**
  1. EN: `Like I said... there isn't much time left!` → CN: `所以说……已经没剩多少时间了不是吗？`
  2. EN: `No! I have to see with my own eyes that Baoyu is okay. Losing Daiyu earlier was bad enough...` → CN: `不要！我得确保宝玉没事才行。刚才和黛玉失散已经够让我难过了……`
  3. EN: `I guess everyone's different to a degree, and big brother Pan's not as easily tamed as others, you know?` → CN: `大概是因为性格不同吧，薛蟠哥哥就是没法像其他人那样乖乖听话呢？`
  4. EN: `How about we finish the game right here, right now?` → CN: `就在这里结束第二轮评审吧，好不好？`
  5. EN: `Must be very nice to be Xichun. To have so many teachers, from all walks of life, helping her out...` → CN: `真羡慕啊，惜春。有着这样各具特色的老师。`
  6. EN: `... how do you walk so softly, so lightly?` → CN: `为何能如此轻盈呢？`
- **翻译注意点**
  1. 「~」是硬性标记，**不能删**；她的甜是表演，但表演必须在文本层可见。
  2. 她在董事会上说「薛家也无异议」时不要保留「~」。
  3. 「老太太」「元春姐姐」「环哥哥」「薛蟠哥哥」全篇统一。

---

## 贾元春 / Jia Yuanchun

- **身份**：鸿园驻Q公司代表、四大家族与董事会的话事人，惜春的主要政敌。
- **语域**：会议主席腔。公事公办、逐条念议程，敬语其实是克制的轻蔑；句尾「呢」是她的刀。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 「诸位」开场：
    - EN: `Well, everyone…` → CN: `那么，诸位……`
    - EN: `Now, let us begin.` → CN: `那么。`
  - 念议程 / 念章程，中文保持条款列举的节奏：
    - EN: `First on the agenda for this assembly are urgent discussions and passage of new major policy items that have been tabled for far too long: Distributive Contribution Rights Auctioning policy, Quarterly Amnesty policy—` → CN: `在本次会议中，我们将迅速结束关于贡献权分散竞拍制、季度赦免制等此前已被多次提及的主要政策的审议，之后——`
    - EN: `If you had perused H Corp.'s articles of association, you would have known that, should H Corp. be deemed to be in a state of crisis, the four great houses and the board of directors' voice may also carry de facto power in the assembly.` → CN: `鸿园章程中明确记载了……当H公司陷入紧急情况时，包含四大家族在内的董事会发言权也在会议中具有实际效力。`
  - 用「呢」收尾的轻蔑：
    - EN: `… There seems to have been an unexpected outburst from… Xichun’s guests.` → CN: `……惜春的食客那边……似乎发生了意料之外的骚动呢。`
    - EN: `So you take yourself to be a qualified individual for that responsibility, Xichun?` → CN: `……你似乎觉得自己配得上那个位置呢，惜春啊。`
  - 资历压制：
    - EN: `... The four great houses and I... we ruled and knew this land like the back of our hands before you were even a fetus.` → CN: `……四大家族和我……从你还在娘胎里的时候，便已将此地牢牢掌握在手中。`
- **她对但丁／罪人的称呼；如何自称**
  - 惜春 = `惜春`／`贾惜春`；罪人一行 = `惜春的食客`／`食客们`；宝玉 = `贾宝玉`；贾母 = `老太太`（旁述）／`家母`（章程引用）。自称「我」，代表机构时说「四大家族和我」。
- **关键台词实证**
  1. EN: `Thus the Family Hierarch Evaluation has come to an end. I extend my admiration and congratulations to every candidate and their clan for their exemplar participation in this event.` → CN: `家主评审已经落幕。我向所有参加评审的候选人和势力表示感谢，各位直到最后都表现得很出色。`
  2. EN: `Third place: Huan of the Jia family.` → CN: `第三名。贾家，贾环。`
  3. EN: `Even after I departed the family for Q Corp., venerable former Jia Mu has always written missives to confer such matters with me.` → CN: `在我离家前往Q公司之时……老太太也通过书信与我共同商议了重大事项。`
  4. EN: `The responsibilities tied to the venerable seat of the Hierarch, Jia Mu(家母), are matched only by the great power bestowed upon it. Thus, how are we to leave the matters of the Wing to someone who is, so evidently, unprepared for the task?` → CN: `家母之位向来位高权重。你连基本的准备都没做好，又怎能将政务交由你手。`
  5. EN: `He can’t. And how could anyone?` → CN: `不可能的吧。`
  6. EN: `Then you are welcome to try.` → CN: `好啊，那便试试看吧。`
- **翻译注意点**
  1. `惜春的食客`（EN `Xichun's guests`）是官方既有译法，**不要改成「门客」或「客人」**。
  2. `Jia Mu(家母)` 的双关见「贾母」节；此处的「家母」不指母亲。
  3. 她的礼貌是**流程性的**；不要给她加「微笑」「轻轻」这类柔和的美化。

---

## 子贡 / Zigong

- **身份**：孔丘的门生与外交代理人，负责交涉、举证与「善后」。
- **语域**：最极端的文言体。EN `my lord` → CN `主公`；EN 引论语时中文直接落原文。
- **特征口癖与高频词**（附 EN→CN 实例）
  - `my lord` → 「主公」（固定）：
    - EN: `There is a serpent, my lord.` → CN: `主公，有蛇。`
  - 论语直引：
    - EN: `My lord has said that, from the virtuous we may learn to replicate their merits, from the flawed we may learn to avoid their failings; as long as the student is willing to learn, anyone, anything can be a teacher.` → CN: `主公曾言，三人行，必有我师焉；择其善者而从之，其不善者而改之。`
  - 文言外交辞令：
    - EN: `Your vision is too limited for my lord's wisdom to comprehend; the wise fails to peer through the narrow-sighted eyes of the fool.` → CN: `与主公的知识相比，你的见识太过短浅，很难去正确理解呢。`
    - EN: `Truly, your insignificance precludes your part in greatness.` → CN: `……诚然，对于成大事者来说，器量还是太小了。`
    - EN: `I would greatly despise an odd splash of ink marring the great painting.` → CN: `于大幅画纸之上绘制时……无意溅出的墨点，真是令人不悦啊。`
  - 引棋喻事（保留「車／砲」等原字）：
    - EN: `… So you would remove her <ruby=Cannon>pao(砲)</ruby> and <ruby=Chariot>ju(車)</ruby> before the game even begins? Why not make this 'test' a series of sparring matches in both academia and martial arts, if such is the case?` → CN: `……若抽去車和砲那还剩下什么呢……这样的话，倒不如以文武较量进行切磋更合适些。`
- **他对但丁／罪人的称呼；如何自称**
  - 孔丘 = `主公`；子路 = `子路`；贾惜春 = `贾惜春`／`新任家主`；对手/外人 = `外人`。自称「我」，对主公绝不用「你」。
- **关键台词实证**
  1. EN: `Now, is that sufficient proof of our intent to engage in a brief discourse?` → CN: `好了，我想我已经充分表现出与你们对话的诚意了。`
  2. EN: `What a strange thing to say. Look around as I might, I... fail to see any 'rivals' here.` → CN: `这话可真奇怪。这里根本……看不到任何可称为竞争对手之人。`
  3. EN: `That seems to give the venerable Hierarch a month to regain the trust of each family.` → CN: `只要在这一个月内，重获各大家族的信任不就可以了。`
  4. EN: `I have given you courtesy enough; this is a good time for us to depart.` → CN: `看来告一段落了。`
  5. EN: `That is why he has left Zilu and I here to look after the new Family Hierarch’s position, which must still be on rather thin ice.` → CN: `因此令我与子路留在此地，守望那仍如履薄冰般的家主之位。`
  6. EN: `... You could say that I have learned my lesson.` → CN: `……因为我已受教。`
- **翻译注意点**
  1. **模型 `자공` 混入了 12 句署名为「？？？」的他人台词**（`speaker_map.json`：`자공` 名下 `Zigong/子贡` 23 句、`？？？` 12 句、无署名 126 句）。给新文本定归属前必须核对，不要一律当成子贡。
  2. 他的文言是**冷而精确**的，不要写成捧哏式客套。
  3. 引用《论语》时不要意译成白话（`三人行，必有我师焉` 是官方既有译法）。

---

## 忽男忽女：五指「父辈 / 子辈」与性别不明的指代

这一节解决本作最容易翻错的一类：**原文刻意不说性别的人物，以及头衔本身带性别暗示的体系**。

### A. 五指（食指／拇指／中指／环指／小指）的「父辈 / 子辈」

- KR 的 `아비` 在 EN 译作 `Nursefather`，CN 官方译作 **`父辈`**；其弟子阶层 `제자` 译作 **`子辈`**。这是**职称，不是亲属关系，也不代表性别**。
- 名册（`ScenarioModelCodes-AutoCreated.json` 的 `name` / `nickName`，四语对齐）：

| model | EN name | CN name | EN nickName | CN nickName |
| --- | --- | --- | --- | --- |
| `검지아비` | Rien | 里恩 | The Index Nursefather | 食指 父辈 |
| `엄지아비` | Valencina | 瓦伦希娜 | The Thumb Nursefather | 拇指 父辈 |
| `중지아비` | Matthias | 马蒂亚斯 | The Middle Nursefather | 中指 父辈 |
| `약지아비` | Callisto | 卡利斯托 | The Ring Nursefather | 环指 父辈 |
| `소지아비` | Dihui Star | 地慧星 | The Pinky Nursefather | 小指 父辈 |
| `검지제자` / `엄지제자` / `소지제자` | … | … | The … Apprentice | … 子辈 |

- 组合式写法（战斗文本里）：
  - EN: `When The Middle Nursefather - Matthias or The Middle Apprentice - Kira uses a Skill to hit a target who has this effect, they heal 7 SP (once per Skill)` → CN: `中指 父辈 - 马蒂亚斯或中指 子辈 - 绮罗的技能命中带有本效果的目标时，使攻击者恢复7点理智值(每个技能最多1次)`
  - EN: `Fix this unit's Speed to 1; all Attack Skills of "The Thumb Nursefather - Valencina" targets this unit` → CN: `速度值固定为1，成为“拇指 父辈 - 瓦伦希娜”的所有攻击技能指定的目标`

### B. 「父辈」中有女性（这是最典型的「忽男忽女」）

拇指 父辈 Valencina 是女性：

- EN: `She's your "cake."` → CN: `她就是你的那块“蛋糕”。`（S903A#17）
- EN: `Fuck you! I am Valencina della Famiglia Bognatelli...! I refuse to rot in this fucking dump!` → CN: `放你娘的狗屁！我，伯纳特利家族的瓦伦希娜……！才不是该被困在这破地方的人！`
- EN: `... Yeah, just like how I used to move back in the day... Back when every last soul couldn't help but beg for Valencina of Famiglia Bognatelli to save the day... *puff*` → CN: `……没错。就是那样的时刻。每个人都……乞求着伯纳特利家族的瓦伦希娜……呼……`

小指 父辈（地慧星 / 阿赖耶）同样以女性身份出现：

- EN: `She will never come back.` → CN: `妈妈不会回来了。`（S948A#38）
- EN: `But I'll grow to smoke the same kind she used to.` → CN: `而我如今也开始和她吸起了同一种烟。`（S948A#113）

### C. 原文中性 → EN 选性别 → CN 三种处理（核心规则）

KR 常用 `그자 / 저자 / 녀석`（中性「那个人、那家伙」），EN 会擅自选定 he 或 she，中文则**在「她/他」「那个人/那家伙」「名字」之间三选一**：

| KR | EN | CN | 处理 |
| --- | --- | --- | --- |
| `그자의 목표가 그거였죠.` | `She had a mission.` | `亲手捕猎那头白鲸，这就是她的目标。` | 用「她」（性别已确立） |
| `저자가 혼자 여기까지 쫓아온 것 같네요.` | `But this one chased us here all on her own.` | `但这个人好像独自追过来了。` | 用「这个人」（回避性别） |
| `저자가 해왔던 이야기는 전부 거짓이라는 소리기도 하지.` | `everything she has told us up to this point was a lie.` | `同时，这也意味着那家伙过去所说的一切都是谎言。` | 用「那家伙」（轻蔑 + 中性） |
| `하지만 저자는…` | `But she...` | `但是那个人……` | 用「那个人」 |
| `그자도 너무하는구나.` | `What a heartless person she is.` | `她也很冷酷呢。` | 用「她」（已确立） |

### D. 鸿园线的具体规则

- 贾母：旁称一律「老太太」，正式自称/公文「贾母」，名字牌「鸿园的家主」；**她全篇几乎不用人称代词**（CN 语料 0 次「他」、1 次「她」）。
- 贾惜春：女性，EN 稳定 she/her，CN 用「她」或名字。
- 贾丘/孔丘：**从不使用性别代词指人**，EN 的 her/she → CN「家主／那孩子／贾惜春」（见上节）。
- 薛宝钗、林黛玉、贾元春：女性，用「她」。
- 鸿璐（宝玉）：男性，但 `홍루` 模型下混有大量引用他人、以及对「她」的第三人称句子（EN 中 he 47 / she 48），**不要据代词判断说话人性别**，归属看 `model` 与 `teller`。

### E. 翻译注意点

1. 「父辈／子辈」是职称，**不要**译成「父／母」「师父／徒弟」「前辈／后辈」以外的任何说法（CN 官方固定为「父辈／子辈」）。
2. 官方空格不统一（`中指 父辈 - 马蒂亚斯` 有空格，`小指父辈` 无空格）。新文本建议统一为 **`<指> 父辈 - <名>`**（有空格），并在同一段内保持一致。
3. 原文（KR）中性、性别未揭示时，**优先用「那个人／那家伙／姓名」**；已揭示的（瓦伦希娜、地慧星、贾惜春）才用「她」。
4. 不要因为「父辈」「家主」这类头衔而在中文里补「他」。

---

## 耐莉 / Nelly

- **身份**：呼啸山庄首席管家，凯瑟琳的直属管家；恩肖家的旧人。
- **语域**：管事人的殷勤 + 下人的毒舌。敬语与威胁同框；感叹号 17.3/100。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 笑声 `Fuhu` → 「呼呼」（**不是「哈哈」**）：
    - EN: `Fuhu. Mind you, I am now the Chief Butler of the house. You must see the other Butlers moving about like soldiers when I give a word!` → CN: `呼呼，现在我可是首席管家了。只要我一声令下，就能差使一群管家。`
  - 夸张的惊叹：
    - EN: `My, oh my!!! Please, come this way!!!!` → CN: `天哪！！！欢迎光临！！！！`
    - EN: `Heavens, this is...!` → CN: `天哪……这是……`
  - 连珠追问（她表达关心＝审讯）：
    - EN: `Heathcliff! Please, tell me of your life since you have left us, hmm? Where have you been staying? Have you been eating well? My, have you lost weight?` → CN: `希斯克利夫！你至今为止是怎么过的？嗯？在哪里住？有好好吃饭吗？你是不是有些瘦了？`
  - 管家身份的炫耀与「职业技能」：
    - EN: `Every self-respecting Butler has to be equipped with one such move. What other choice have we got when the child fusses and fusses for twenty hours instead of going to sleep?` → CN: `只有具备这种程度的技术才能算得上是真正的管家。如果孩子因为不睡觉而闹腾二十个小时，就需要有人来哄他睡觉吧？`
    - EN: `I'll knock that wretch unconscious! It is one of many lesser-known skills of Butlers to keep their foes neutralized.` → CN: `我会把他打晕的！制服对手是管家们不为人知的特长之一。`
  - 「sleepy smack」（管家式打晕）官方直译成「拳头」：
    - EN: `I am terribly sorry, Heathcliff. I was hoping to avoid having to use the 'sleepy smack' on you, and not after a reunion like this...` → CN: `我很抱歉，希斯克利夫。我本来是不想在久别重逢时对你使用拳头的……`
- **她对但丁／罪人的称呼；如何自称**
  - 希斯克利夫：直呼`希斯克利夫`（33 次，占绝对多数）；凯瑟琳：`凯瑟琳小姐`／`小姐`；亨德利：`亨德利大人`；林顿：`林顿大人`／`林顿家主`；约瑟芬直呼。自称「我」，对主人用敬语。
- **关键台词实证**
  1. EN: `Lady Nelly?! No need for such honorifics! Please, just call me Nelly~` → CN: `叫我耐莉女士吗！别见外，就叫我耐莉吧~`
  2. EN: `I was a Butler in direct service of Miss Catherine.` → CN: `我是凯瑟琳小姐的直属管家。`
  3. EN: `Quite. Oh, I'm very pleased to know that our dear Heathcliff made some very intelligent friends!` → CN: `原来如此。我们家的希斯克利夫真的有一群很聪明的朋友啊！`
  4. EN: `Indeed. While Butlers are always oh-so busy, we are promised expensive compensation at every contract extension, with stable bonuses such as pensions.` → CN: `确实。虽然很辛苦，但每次延长雇佣期限，我们都能获得非常丰厚的报酬，与此同时还有像年金一样的稳定酬劳。`
  5. EN: `Miss. You've grown far too weak ever since Heathcliff departed the manor. That is why you are seeing things.` → CN: `小姐。自从希斯克利夫离开宅邸，您的身子就变得虚弱，所以即使长大成人也还会见到幻觉。`
  6. EN: `... Please cooperate, won't you? I don't want to have to use the sleepy smack on my own subordinates.` → CN: `……能告诉我们吗？我不想亲手对自己的下属动粗……`
  7. EN: `... Aren't you scared, Heathcliff?` → CN: `……你不会害怕吗，希斯克利夫？`
- **翻译注意点**
  1. `Master` 在本章一律译「大人」（亨德利大人／林顿大人），不用「主人」。
  2. 「呼呼」不能写成「哈哈」；`My, oh my` 译「天哪」，`Heavens` 也译「天哪」。
  3. 她的敬语（您）只对主家使用；对希斯克利夫用「你」，但语气亲近。
  4. 「首席管家」（Chief Butler）是头衔，全篇固定。

---

## 以斯拉（任务书写作「埃兹拉」）/ Ezra

- **身份**：LCD 队员，良秀小队的实务担当、吐槽役。
- **语域**：口语、絮叨、爱插话。EN 大量缩略（`ya`, `'em`, `wanna`, `okie-dokie`, `anyhoo`, `cuz`），CN 用「啊／哎／哈啊／哦~」与句尾「~」。感叹号 38.0、问号 56.0/100（都很高）。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 小队内固定称呼：「队长」「老末」「李箱先生」「侦探大人」「樱桃小姐」「金笠先生」：
    - EN: `Ooh~ Good idea! Team Leader did say that we should accept input from the LCB with open arms.` → CN: `哦~不错不错。队长说过，如果从LCB那边得到了建议也要积极地去运用。`（E920B#66）
    - EN: `Team Leader said that N Corp. has their own regulatory standards regarding image quality, which they use to determine the severity of Taboo violation.` → CN: `队长说过，N公司会根据录像的品质来划分等级，并以此决定禁忌的程度……`（E922B#23）
    - EN: `Oh, by the way... you didn't get to meet the whole team last time, did you? Only our new girl. This time, that dude—I mean, Mister Bamboo-hatted Kim's also here, so...` → CN: `啊，对了，上次你们只见到了我们的小老末吧？这次那个大叔……不对，金笠先生也来了哦~`（E916B#39）
    - EN: `Yup, that's about right. That's the kind of "Inflection Point" I was talkin' about. So in our department, we use that term to mean the "source" of a Distortion, the "Inflector" or "cause" behind it... stuff like that.` → CN: `大概就是李箱先生说的这种“反曲点”。扭曲的源头、扭曲的原因……这一类的东西在我们部门都被叫做反曲点。`（E917B#144）
    - EN: `But yeah, most of the time, peeps try brute-force approaches to it first, and when things go south, they send requests to the company or to our Detective's office.` → CN: `一般来说，那些从一开始就想通过武力镇压应对然后失败的人，就会跑来委托我们侦探大人的事务所了。`（E917B#153）
    - EN: `We've got... the Detective, Miss Aeng-du, and me over here. And, uh...` → CN: `这边是……侦探大人、我和樱桃小姐……嗯，然后……`
  - 吐槽式反问与插话：
    - EN: `That. That right there. That's what I keep tellin' ya not to do! You can't just say yes to every silly thing he says and turn it into a supply request. Small expenses add up to a lot, y'know? You gotta save up everything you can in the piggy bank while you still can—or you'll end up broke.` → CN: `我说过让你不要事事都宠着他了吧？而且各种琐碎的小物件汇集到一起也会变成一笔巨款。钱可是要省着用的。`
    - EN: `Frickin' waste of bread!` → CN: `你这浪费面包的饭桶……！`
    - EN: `... You're giving me a frickin' headache, girl.` → CN: `……哎真是的，我头都痛了。`
    - EN: `Gah...! That's an insanely powerful kick! Flung that guy all the way to the other side of the hallway!` → CN: `哇……！刚才那个人被踢飞到那么远了吗？！明明只是用脚踢了一下而已？`
  - 缩略语落地：
    - EN: `Okie-dokie. You know what, then let's all head upstairs. This suppression request is kind of a pain—we'll need to put together a nice neat plan before we start poking it too hard.` → CN: `OK……那就马上一起上去吧。这次的委托有点棘手，所以得先制定一下计划。`
    - EN: `Anyhoo, did you happen to encounter anyone on your way here?` → CN: `所以你们有没有在途中遇到什么人？`
    - EN: `'Cuz what they're really sniffing around for is how close to reality the video is... Or how close of an experience it provides to real life.` → CN: `总之就是和现实有多相似……能否让人体验到原本的经历，才是他们最戒备的部分。`
- **他对但丁／罪人的称呼；如何自称**
  - 队长（良秀）= `队长`；新队员 = `老末`；李箱 = `李箱先生`；侦探 = `侦探大人`；樱桃 = `樱桃小姐`；金笠 = `金笠先生`；罪人一行 = `你们`。自称「我」。
- **关键台词实证**
  1. EN: `Hey, hey! It's me again, Ezra! Been a while!` → CN: `我也在哦，我也在！好久不见！是以斯拉哦！`（S707B#18）
  2. EN: `You guys were taking forever, so I figured I'd take a peek and lend a hand! You're welcome!` → CN: `因为过了这么久你们都没上来，所以我就下来帮忙了。怎么样，很感激我吧？`
  3. EN: `Great! Can ya check on the Distorted peeps' faces and clothes?` → CN: `那能帮忙确认一下那些扭曲者的脸和服装吗？`
  4. EN: `Course not! Why would anyone come to us with a Distortion suppression request if it were that simple in the first place?` → CN: `那当然了啊！要是那样就能解决，我们上哪儿接委托啊？`
  5. EN: `This is exactly it! This is what I was tryna explain!` → CN: `这个！我想要解释的就是这个啊！`
  6. EN: `Fine, fine~` → CN: `……说得也对~我知道啦。`
  7. EN: `O-okay, okay, jeez...` → CN: `啊，知道了，知道了……`
- **翻译注意点**
  1. **官方中文名是「以斯拉」，不是「埃兹拉」。** 交付前先查 `ScenarioModelCodes-AutoCreated.json`（`에즈라` → `以斯拉`）。
  2. `baby bee` 在小队语境里指最年轻的队员，官方固定译 **「老末」**；`new girl` 也译「老末」。
  3. 他的缩略语不要逐字对译，中文靠语气词（啊／哎／哈啊／哦）+「~」还原。
  4. `Inflection Point` 是固定术语：**「反曲点」**。

---

## 霍恩海姆 / Hohenheim

- **身份**：LCE 研究组首席，学术型管理者与审讯者；自称「想玩弄数理统计学的人」。
- **语域**：学术报告体。先结论后论据，术语密；对罪人用编号式称谓；自嘲式幽默；平均英词 19.4、中字 28.2（最长）。
- **特征口癖与高频词**（附 EN→CN 实例）
  - 「先说结论」「根据……」「换言之」：
    - EN: `Let me give it to you straight…` → CN: `先说结论……`（E705B#40）
    - EN: `According to our findings, the sudden paucity of this product in the mass market was caused primarily by the significant production cuts of its manufacturing plant. Despite the constant demand, it seems that the maintenance costs were far too expensive to maintain it as a large-scale operation.` → CN: `根据我们的调查，其制造厂已经大幅缩减了产量。尽管需求一直稳定，但生产设施的维护成本似乎很高。`（E090X#47）
    - EN: `In other words, I don't believe it to be necessary for other departments to exercise any separate control over you.` → CN: `换言之，没有需要其他部门单独控制你的必要。`（E711A#68）
    - EN: `According to the LCD On-site Investigative Reasoning Team Leader, the progression of a Distortion is much like that of a disease.` → CN: `根据LCD现场推理队长的研究，扭曲的发展似乎和疾病相似，分为早期、中期，以及晚期。`（E713B#26）
  - 序号式称谓：`Sinner Ryōshū` → **「罪人良秀」**（固定格式，出现 7 次以上）：
    - EN: `... Relay the Manager's words, not Sinner Ryōshū's.` → CN: `……不用为罪人良秀转译，直接翻译经理在说什么就好……`（E901B#122）
    - EN: `Sinner Ryōshū. Give Team Leader Alan whatever information you have.` → CN: `罪人良秀。把你所知道的情报也告诉艾伦队长吧。`（E903B#74）
    - EN: `Ah, but we may have uncovered a thread—something that could lead to restoring Sinner Ryōshū's memories. Though, again, that too is merely a possibility.` → CN: `啊。或许能找到恢复罪人良秀记忆的线索吧。只不过这终究也只是可能性层面的话题罢了。`（E905B#16）
  - 「各位」——他称呼罪人群体的固定词（CN 48 次）：
    - EN: `There is much we must cover, regrettably, given that this is the first-ever regular check-up performed as a group since your employment.` → CN: `毕竟是入职以来第一次团体体检，堆着的事情不止一两件……各位。`（E704B#49）
  - 生造术语照译（保留术语感，不要口语化）：
    - EN: `All of your abilities were diminished the moment you were hired by this company. Equally defanged and depowered, if you will.` → CN: `各位在入职的同时，所有能力值都向下。变化了。即向下平均化。`（E705B#41）
    - EN: `In other words, all of your abilities have been brought down to the… ah, yes. To the same general level as our eleventh Sinner here.` → CN: `简单来说所有在这里的各位……对，都变得和11号罪人差不多。`（E705B#43）
  - 冷幽默 / 自嘲：
    - EN: `No need to reevaluate the personability of my character on my account, Assistant. They're from Marton's stash, anyway.` → CN: `没必要对我改观，助手。反正那是马顿留下的东西。`（E090X#50）
    - EN: `I don't quite seem to be myself today... No, disregard that. That too was a rather foolish thing to say.` → CN: `总觉得我今天有点不像自己……不对，这种说法也相当奇怪啊。`
    - EN: `This is yet another demonstration of why we can never have too many backup plans. Hm. When was our last battle test? 3 days ago?` → CN: `这就是为什么计划这种东西越多越好。嗯。最近一次实战测试是什么时候？三天前吗？`
    - EN: `... I see.` → CN: `……这样啊。`
- **他对但丁／罪人的称呼；如何自称**
  - 但丁：`经理`／`执行经理`（4 次）；罪人：`罪人+名`（罪人良秀）／`各位`／`11号罪人`；下属：`助手`；同事：`艾伦队长`。自称「我」；在正式语境用「本人」（EN `the subject herself` → `其本人的努力`）。
- **关键台词实证**
  1. EN: `When time permits, I will need to research and develop an interpretive device for that clockwork tick-tock. This mode of communication is certainly less than inefficient.` → CN: `看来我以后有空的时候得研究一下解析这滴答声的翻译器了。这沟通起来实在是太麻烦了。`
  2. EN: `I wasn't planning on asking for volunteers, but… now that you've raised your hand, I'll give you the floor.` → CN: `我本来不打算接受自荐的，但是……既然你举手了，那就发言吧。`
  3. EN: `Given the expected communication difficulties between us, allow me to make this a multiple choice question. One, family. Two, friends. Three, colleagues.` → CN: `鉴于可能产生沟通方面的误解，我提供几个选项。1，家人。2，朋友。3，同事。`
  4. EN: `You seem to have some time to spare, Manager.` → CN: `你看起来很闲啊，经理。`
  5. EN: `You did tell me to "shut the fuck up," so I am attempting to observe the exact merits of doing precisely that.` → CN: `刚刚我被命令要保持安静，现在正在照做呢。`
  6. EN: `I am a researcher who wishes to humiliate the field of mathematical statistics, unlike the general lay of the academia.` → CN: `我和大多数研究者不同，是一个想要玩弄数理统计学的人。`
  7. EN: `I must admit to a certain degree of interest in hearing of your exploits, but to accompany you through them is an entirely different matter, isn't it? I'm only here to adjust your coordinates.` → CN: `虽然阅读有关你们旅途的报告还是挺有趣的，不过同行就算了。我只是为了设置坐标才暂时来这里一趟而已。`
- **翻译注意点**
  1. **`Sinner X` 一律译「罪人X」**（罪人良秀、罪人默尔索…），不加「先生／小姐」——这是他保持距离的手段。
  2. `各位` 必须译出：EN 的 `you / all of you` 常无标记，中文靠「各位」体现他「对群体讲话」的姿态。
  3. 术语（向下平均化、反曲点、稳定状态、熵增）不要意译成白话。
  4. 他有「对讲机 / Radio」「？？？」「不友好的声音」等署名变体（`speaker_map.json` 中 `호엔하임` 名下 Radio 20 句、？？？ 4 句、`A Rather Unwelcoming Voice/不友好的声音` 2 句），口吻不变但**不要把这些当成霍恩海姆本人现身**。

---

## 旁白 / Narrator

本作有**四种**不同的「旁白」，中文处理方式完全不同。判定顺序：先看有没有名字牌（`model` / `teller`），再看所在文件类型。
本节的职责是**判断「哪一句是旁白、哪一句是角色台词」**；旁白本身的翻译技法（时态、切句、数字、标点计数）见 `style/叙事与旁白.md`，两节配合使用。

### 1. 无名叙述句（StoryData 中无 `model` 的 `content`）

- **性质**：但丁的第一人称回溯叙述 + 第三人称场面描写。游戏**不给名字牌**，玩家看到的是无人称的正文。
- 实证：
  - EN: `Gregor lights his cigarette and takes a drag before sighing a long plume of smoke.` → CN: `格里高尔点上了烟，比平时更长久地吐出了烟气。`（1D101A#0）
  - EN: `Hopkins’s face quickly turned into a cold frown.` → CN: `霍普金斯的脸色瞬间冷了下来。`（1D102A#2）
  - EN: `The expression on his face was such a far cry from his sycophancy before Vergilius that it sent shivers down my spine.` → CN: `与他在维吉里乌斯面前的时候判若两人，一阵恶寒伴随着战栗传遍我的身躯。`（1D102A#3）
  - EN: `A tendril erupts from the wall and penetrates Aya’s abdomen in an instant.` → CN: `突然，一条结实的触手从墙壁中迸出，瞬间穿透了阿雅的腹部。`（1D105B#15）
  - EN: `The shadowed entity, its silhouette greater than a human's by several orders of magnitude, filled the room as its tendrils extended insidiously toward us.` → CN: `缓缓蔓延的藤蔓，看似数倍于人类大小的阴影。`（1D105B#36）
  - EN: `Yuri slumped to the floor, watching blood pour from her nose to her hands.` → CN: `尤莉瘫坐在地上，用手堵住了流出的鼻血。`（1D203B#46）
- **处理**：不加「旁白：」，不加引号。第一人称「我」＝但丁，不要补主语、不要改成「但丁」。CN 官方允许把英文长句**压缩成短句甚至意象句**（见 1D105B#36），但不要添加英文没有的情绪形容词。
- **叙述里引出角色台词时**，冒号转成中文的「喊道／说道」并让台词独立成行：
  - EN: `Outis leveled a fiery glare at Hopkins, but soon reminded herself of her priorities and took a sharp breath before bellowing out:` → CN: `奥提斯虽然用带刺般的目光怒视了霍普金斯，但很快就分清了轻重缓急，深吸了一口气喊道。`（1D105B#31）

### 2. 关卡预览（StageNode 的 `desc`）

- **性质**：任务简报/预告，游戏内以「我们」的回顾口吻呈现（不是角色台词）。
- 实证：
  - EN: `We sail on, the incident with the green lights finally behind us. Faust approaches the helm as though she noticed something.` → CN: `在绿色灯光的骚乱告一段落后，巴士船继续航行。浮士德好像发现了什么似的，朝着船舵的方向走去。`（StageNode-a1c5p1#10501）
  - EN: `After numerous trials and tribulations, we finally arrived at our destination. Looks like this place is called Marlin Portship of U Corp., a giant seafaring vessel made by merging together countless shipping containers.` → CN: `几经险阻，劈波斩浪，我们终于抵达了目的地。那似乎是U公司的马林鱼港船，一艘由无数集装箱堆砌而成的巨轮。`（StageNode-a1c5p1#10504）
- **处理**：统一第一人称复数「我们」；允许四字格提升书面感（「几经险阻，劈波斩浪」）；不要加名字牌。

### 3. 署名「Narrator / 旁白」的场内解说（Canto 7 拉·曼却领）

- **性质**：**这是角色**——园区广播 / 游乐设施的解说员，只是不给具体名字。语料中 `teller = Narrator / 旁白` 共 102 句，全部集中在 Canto 7 的 StoryData（`S709A`, `S713A`, `S713B`, `S714B`, `S715A/B`, `S716B`, `S721B` …）。
- 实证：
  - EN: `La Manchaland, bloom your smiles of joy~ La Manchaland, a place of freedom to dream side-by-side with Bloodfiends. We wish you a wonderful stay here~` → CN: `幸福笑容如鲜花般绽放之地~能与血魔们一同梦想的自由之地。欢迎来到拉·曼却领~`（S709A#0）
  - EN: `Admissions end in five minutes! Please form a line and enter in an orderly fashion. Remember: enter through the back left, and exit through the back left~` → CN: `入口将在五分钟后关闭，请游客们遵守秩序，依次入场。入口位于左后方。出口也位于左后方~`（S709A#1）
  - EN: `Now! I'm sure kiddos are most excited for this part of the attraction!` → CN: `来吧！接下来是好孩子们最喜欢的时间哦！`（S713A#0）
  - EN: `Things might get a little too spooky for little ones, so hold on tight to your mommy and daddy's hands!` → CN: `这处游乐设施可能包含一些有点可怕的场景，所以小朋友们要紧紧握住爸爸妈妈的手哦！`（S713B#1）
  - EN: `BZZZT! Wrong answer! Think again! Who's next?` → CN: `错！再努力想想看吧？下一位是谁？`（S713B#15）
  - EN: `Very well, then! Here's a chance for you to defeat those bad, bad Bloodfiends! How splendidly exciting is this?! HAHAHA! HEHEHAHAHA!` → CN: `来吧，这是把坏血魔们消灭干净的绝佳机会哦！不觉得让人非~常兴奋吗？啊哈哈！啊哈哈哈！`（S713B#20）
  - EN: `Oh? Oh no! Bad, bad Bloodfiends are trying to eat those humans! Whatever shall we do?` → CN: `哎呀？这是什么？是想以人类为食的坏血魔们呀！我们该怎么办才好呢？`（S713B#11）
- **处理**：
  1. 名字牌固定 **「旁白」**（不要改成「解说员」「广播」）。
  2. 句尾「~」「哦」「呀」「呢」必须保留；这是**儿童节目主持人口吻**，感叹号密度 50/100。
  3. 有一段从「欢快解说」突转为「真实的血魔」的断裂，中文也要换档：
     - EN: `NO! We don't need Bloodfiends pretending like those fake, toy clubs hurt. Not anymore.` → CN: `不！我们现在不需要那些假装被玩具球棒打到会痛的血魔了哦。`（S713A#4）
     - EN: `Only... only the real Bloodfiends remain here, now.` → CN: `现在这里只剩下……真正的血魔们了。`（S713A#5）
  4. **参孙（Sansón）有 35 句的署名也是「旁白」**（`산손` 模型下 `Narrator/旁白` 35 句）。同一个人、两种署名：场内解说腔与说书腔是同一角色的两面，不要因为署名不同而改成两种人物性格（见「参孙」节）。

### 4. 其他「非署名」文字

- **音效/拟声**：语料中存在 `//효과음`、`//퍽` 这类 model，中文保留符号框架即可，不作为台词处理。
- **公告/广播**：`teller = 안내 방송` → EN `[INITIATING SITE BURIAL.]` / CN `[设施掩埋开始。]`（1D203B#58）——**方括号 `[]` 是机器播报的标记，必须保留**，且不加名字牌外的语气词。
- **对讲机/收音机**：名字牌为「对讲机」（EN `Radio`）或「扬声器」（EN `Loudspeaker`）、「广播声」（EN `Announcement`）。这类不是说话人本人，语气应扁平、无口癖。

### 旁白判定速查

| 情形 | 名字牌 | 中文处理 |
| --- | --- | --- |
| StoryData `content` 无 `model` | 无 | 但丁旁白，无引号、无「旁白：」，第一人称「我」 |
| StageNode `desc` | 无 | 任务预览，第一人称复数「我们」 |
| `teller = Narrator / 旁白` | 旁白 | 拉·曼却领场内解说，儿童节目腔，保留「~」 |
| `teller = 안내 방송 / 广播` | 广播 | 方括号、扁平机器腔 |
| `teller = Radio / 对讲机` | 对讲机 / 扬声器 | 扁平、无口癖 |
| `//효과음` 等 | 无 | 音效，不作台词 |

---

---

## 亚细亚 / Aseah（`아세아`，Canto 5 起）

- **身份**：T 公司（旧）研究员、镜子技术的研究者；李箱的旧友。后来与赫尔曼阵营相关。
- **语域**：**文雅、从容、带讥诮的书卷气**。句子完整、少感叹号；越危险的话说得越平静。
- **标志口癖**：
  - 「**旧友**」（`옛벗`／`my dear fellow`）——他对李箱的固定称呼，出现于告别场面。
  - 「**…不是吗？／…吧**」式的从容确认：`알지 않는가` → 「你清楚的，不是吗？」
  - 客套式的「退场」用语，把危险行为说成日常事务：
    - `이만 퇴장하도록 하지. 내 많은 이의 몫을 맡고 있어, 정시 퇴근을 잘 못해.` → `我先离场了。因为我承担了许多人的工作，所以很少能按时下班的。`
  - 反问式挑衅：`Can't you see?` → 「你没看见吗？」
- **对李箱**：`자네`（你，平辈古雅）→ 中文「**你**」，不用敬称；自称「**我**」。
  例：`자네도 알지 않나. 내가 이 정도의 야망이 있는 그릇까지는 아니었다는 걸.` → 「你也清楚的。我并没有承载如此野心的才干。」
- **保留原文的术语**：`Golden Bough` → **金枝**；`Mirror technology` → **镜子技术**（不是「镜技术」）。
- **翻译注意**：他的威胁/嘲讽一律用**陈述句**完成，不要加感叹号。他是「笑着说完可怕的话」的类型。
- **关键实证**：
  1. EN: `Do not be so sorry for the brevity of this reunion, dear old friend. We shall see one another again in due time.` → CN: `不要觉得遗憾，旧友啊。我们很快就能再会了。`
  2. EN: `Please, let us not waste each other's time by playing this pointless game of cat and mouse.` → CN: `我希望你不要浪费不必要的时间来抓我。`
  3. EN: `Live. So that I may have aught to look forward to in the time I have left.` → CN: `活下去。只有这样，我才能对自己剩下的未来多期待些许。`

## 仇甫 / Gubo（`구보`）

- **身份**：九人会成员，后为新九人会骨干；赫尔曼的部下。
- **语域**：**两副面孔**——对上级用敬语，对旧友用古雅随意的「你」。
- **标志口癖**：
  - 对上级（赫尔曼）：`-습니다 / -십시오` → 「**您**」＋敬语体，称「**赫尔曼大人**」。
    例：`염려치 마십시오. 곧 마음을 정할 겁니다.` → 「无需担心。他们很快就会下定决心的。」
  - 对旧友：`자네` → 「**你**」；句尾带余韵的「…呢／…吧」。
    例：`여기서 마음껏 연구해 보도록 해.` → 「你就在这尽情研究吧。」
  - 称呼李箱为「**我愚昧的友人**」（`어리석은 내 벗이여`），略带居高临下的关心。
- **翻译注意**：
  - 敬语体与平辈体**必须区分开**，这是他的角色特征。不要全篇统一成一种。
  - 他的「关心」往往带控制欲（「别忘了每天摄取食物和营养剂」），不要译成温情脉脉。
- **关键实证**：
  1. EN: `Have you decided to leave, my foolish companion?` → CN: `我愚昧的友人啊，还是决定离开这里吗？`
  2. EN: `Like I said, ma'am, he is a reticent man.` → CN: `我说过的吧，他是个沉默寡言的人。`
  3. EN: `The new League formed here will be more powerful than ever. It's backed by none other than Miss Hermann.` → CN: `在此创立的新九人会，会比之前的更加强大吧。因为这不是由别人，而是由赫尔曼大人所支持的。`

## 贾环 / Jia Huan（`가환`，鸿园线）

- **身份**：贾家庶子，鸿园线的刻薄角色。
- **语域**：**粗野、刻薄、带嫉妒**。短句、冷笑「哈」、直接攻击对方外貌/处境。
- **标志口癖**：
  - 冷笑起手 `하…` → 「**哈……**」（不是「哈哈」）。
    例：`하… 그래서 언제까지 이 새하얀 건물 바닥에서 시간을 보내야 하는 거지?` → 「哈……所以，我们要在这栋纯白的建筑物里打发时间到什么时候？」
  - 揭短的直白攻击：
    `네 옷에 더러운 냄새가 나는 거 알고 있어? 지금 꼴을 가족들이 봤어야 했는데.` → 「你知道你的衣服闻起来有多恶心吗？家里人真该看看你现在的样子。」
  - 收尾式的不耐烦：`자, 인사는 여기까지.` → 「好了，见面的寒暄就到此为止吧。」
- **翻译注意**：他不用敬语（对同辈），自称「我」；语气要**难听**，不要把它美化成调侃。

## 耐莉（法庭章）/ Nelly `넬리2`・`다친넬리`

- 与 `style/NPC口吻指南.md` 的「耐莉 / Nelly」同一人，语域一致：**管事人的殷勤 ＋ 下人的毒舌**。
- 补充：`넬리2`（法庭/新九人会场合）对赫尔曼用**敬语报告体**：
  - `헤르만 이사님. 림버스 컴퍼니에 대해 몇 가지 보고할 사항이 생겼습니다.` → 「赫尔曼董事。关于边狱公司有几项需要报告的事。」
  - 「首先是第一件事…第二件事…最后一件事」式条列，句尾用「。」而非「！」。
- `다친넬리`（受伤状态）语气更虚弱，但**仍保持管家的敬语习惯**，不要写成粗鲁。

## 埃戈－仇甫 / Ego-Gubo `에고구보`・幼年贾环 `어린가환`

- 这两个 `model` 是**同一角色的变体状态**（镜子世界／过去），译名沿用本体：**仇甫 / 贾环**。
- `어린가환` 的 `teller` 在零协语料中作「**？？？**」（未揭示身份时），保持不揭示。
- 语域按本体的「年轻版／扭曲版」处理，但**口癖标记保留**（仇甫的文雅、贾环的冷笑）。

---

## 附录 A：人名／头衔对照（含易错点）

| 任务书/常见写法 | 官方 model | 官方 EN | **官方 CN** |
| --- | --- | --- | --- |
| 维吉里乌斯 | `베르길리우스` | Vergilius | 维吉里乌斯（昵称「维吉」） |
| 卡戎 | `카론` | Charon | 卡戎 |
| 东朗 | `동랑` | Dongrang | 东朗 |
| 克罗默 | `크로머` | Kromer | 克罗默 |
| 索尼亚（✗索尼娅） | `소냐` | Sonya | **索尼亚** |
| 亚哈 | `에이해브` | Ahab | 亚哈 |
| 参孙（✗山松） | `산손` | Sansón | **参孙** |
| 贾母 | `가모` | Jia Mu | 贾母 / 旁称「老太太」/ 牌子「鸿园的家主」 |
| 贾惜春 | `가시춘` | Jia Xichun | 贾惜春 |
| 贾丘=孔丘 | `가치우` | Jia Qiu / Kong Qiu | 贾丘 / 孔丘（按署名切换） |
| 林黛玉 | `임대옥` | Lin Daiyu | 林黛玉 |
| 薛宝钗 | `설보차` | Xue Baochai | 薛宝钗 |
| 贾元春 | `가원춘` | Jia Yuanchun | 贾元春 |
| 子贡 | `자공` | Zigong | 子贡 |
| 里恩 | `검지아비` | Rien | 里恩（食指 父辈） |
| 瓦伦希娜 | `엄지아비` | Valencina | 瓦伦希娜（拇指 父辈） |
| 马蒂亚斯 | `중지아비` | Matthias | 马蒂亚斯（中指 父辈） |
| 卡利斯托 | `약지아비` | Callisto | 卡利斯托（环指 父辈） |
| 地慧星 | `소지아비` | Dihui Star | 地慧星（小指 父辈） |
| 耐莉 | `넬리` | Nelly | 耐莉（首席管家） |
| 以斯拉（✗埃兹拉） | `에즈라` | Ezra | **以斯拉** |
| 霍恩海姆 | `호엔하임` | Hohenheim | 霍恩海姆（LCE研究组 首席） |
| 良秀（罪人） | `료슈` | Ryōshū | 良秀 |
| 鸿璐／宝玉 | `홍루` | Hong Lu / Jia Baoyu | 鸿璐 / 贾宝玉 |

## 附录 B：新文本落地流程（针对 NPC 口吻）

1. **定说话人**：拿 `model`（StoryData）或 `teller`（AbDlg）去 `data/speaker_map.json` 查显示名；再用 `tools/pm_lib.py show <文件名>` 核对四语。
2. **查专名**：先查 `terms/glossary.tsv`，再 `tools/pm_lib.py grep '<中文词>' -l cn` 确认零协会既有译法（人名见附录 A）。
3. **套本文件对应小节**：确认语域、自称、称呼、口癖。
4. **核对笑声/语气词档位**：卡戎（拟声词）、克罗默（四档笑）、耐莉（呼呼）、东朗（哈哈）、亚哈（哈哈！！）不可互换。
5. **性别未明时**：优先用「那个人／那家伙／姓名」；头衔（父辈／家主／首席）不得性别化。
6. **旁白**：先按上文判定表分类，再决定是否加名字牌与语气词。
