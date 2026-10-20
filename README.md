# Muse Reading → Anki

**读喜欢的英文，把指定词汇连同原文例句和同源词，带进自己的闪卡。**

这是一个可复用的 Agent Skill，包含工作流、阅读器、Anki 卡片模板、原始分级词表与本地辅助脚本。它按 `SKILL.md` 组织，不依赖未公开的 Muse 专用接口。

## 怎么用

将 [`skills/muse-reading`](skills/muse-reading) 整个目录放入宿主支持的 skills 目录。Codex 的默认位置为 `~/.codex/skills/muse-reading/`；其他宿主按其导入方式加载。脚本需要 Python 3.10+，没有第三方 Python 依赖。

可以这样开始：

> 使用 $muse-reading。我喜欢 Prince、Taylor Swift、诺兰电影和趣味科普。先给我挑4篇英文文章，等我选定后，按指定词库做成阅读器。

> 以六级为例，导入六级、四级、高考3个词库，计算六级独有词；把我选的文章写成700–900词学习稿，配15–25个生词。

阅读字数可以自己选择，例如“今天只读400–600词”。700–900词是默认建议；脚本通过 `--min-words` 与 `--max-words` 接收所选范围。

> 这是我从阅读器导出的选词。请用原文例句和同源词做成「阅读单词」闪卡，检查重复词，再按已配置的Anki连接同步。

## 一条完整的学习流程

1. **兴趣选文**：每轮准备4篇候选，附中文标题、简介、词数、来源与发布日期。
2. **指定词库改写**：对目标词库与排除词库做差集，在语境合适时使用目标词，保留事实与来源。
3. **HTML 阅读器**：点击任意单词选中；预置词显示释义；读完在文本框中导出三列TSV。
4. **你筛词，AI 制卡**：单词、音标、释义、原文例句、翻译、同源词；按日期标记。
5. **Anki 同步**：先拉回进度，再去重加卡，再推送AnkiWeb；手机端同步后复习。

定时选文需要宿主有调度能力并由用户设定时间。云端同步需要独立配置运行中的 Anki、AnkiConnect 与 AnkiWeb 账号；仓库不会自动提供云服务器或登录账户。

## 文件入口

| 内容 | 入口 |
|---|---|
| 技能说明 | [SKILL.md](skills/muse-reading/SKILL.md) |
| 阅读器模板 | [reader-template.html](skills/muse-reading/assets/reader-template.html) |
| 闪卡模板 | [card-template.md](skills/muse-reading/assets/card-template.md) |
| 分级词表与可复算差集 | [wordlists](skills/muse-reading/assets/wordlists/) |
| 输入格式与运行命令 | [data-formats.md](skills/muse-reading/references/data-formats.md) |
| 同步顺序与全量同步处理 | [anki-sync.md](skills/muse-reading/references/anki-sync.md) |

## 本地快速演示

从 `skills/muse-reading/` 目录运行：

```bash
python scripts/muse.py vocab --target assets/wordlists/raw/cet6.txt --exclude assets/wordlists/raw/cet4.txt --exclude assets/wordlists/raw/gaokao.txt --out work/target-vocab.json
python scripts/muse.py reader --article assets/examples/article.json --demo --out work/reader.html
python scripts/muse.py cards --input assets/examples/cards.json --article assets/examples/article.json --out-dir work/anki
```

演示短文是原创测试素材，用来体验点词和制卡，非完整700–900词学习稿。三个脚本子命令只处理本地文件，不连接Anki或上传内容。

## 模板与例句

闪卡采用奶油白、衬线词头、暖橙词性和黄色例句高亮。正面只考认读，背面保留原文语境和同源词。

“原文例句”指用户实际阅读的那版文本中的句子。缺句时可以补写，但必须标记为AI补充。阅读器三列TSV需补全为七字段后才能套用完整卡片模板。

用户原始阅读器模板基础上，技能版修正了重复词取句、单词重复拼接、清除选择按钮与释义安全渲染，并保留手机可复制的导出面板。

本地验证命令（仓库根目录）：`python -m unittest discover -s tests -v`。

## 词库来源

原始词表由仓库作者提供，保留其内容并记录SHA-256。名称用于标识文件，不代表已核验为某考试官方词表。实际差集随词表版本与归一化口径变化，见 [词库说明](skills/muse-reading/assets/wordlists/README.md)。

项目不附带新闻网站的文章全文、账户凭据或个人复习数据。词库和模板之外的文章内容在用户自己的工作目录处理。
