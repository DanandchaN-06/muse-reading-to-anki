# 输入与输出

所有脚本只使用 Python 3.10+ 标准库，默认不联网。相对路径以当前工作目录为准；命令示例假设已进入 `skills/muse-reading/`。

## 词库差集

UTF-8 TXT，每行一个词条，允许短语。忽略空行和 `#` 开头注释，执行 Unicode NFKC、空白合并、撇号统一和小写处理。不做词干化。

```bash
python scripts/muse.py vocab --target assets/wordlists/raw/cet6.txt --exclude assets/wordlists/raw/cet4.txt --exclude assets/wordlists/raw/gaokao.txt --out work/target-vocab.json
```

结果包括目标词、归一化计数、各文件 SHA-256 和实际差集数量。脚本不重写源词库。

## 阅读文章 JSON

```json
{
  "title": "A short learning article",
  "source_title": "原始文章标题",
  "source_url": "https://example.com/article",
  "publication_date": "2026-10-20",
  "adaptation_note": "学习改写；原文较短，扩写部分另行标注",
  "paragraphs": ["First paragraph.", "Second paragraph."],
  "vocab": {
    "worldly": {
      "pos": "adj.",
      "zh": "世俗的；老练的",
      "ex": "His worldly outlook shaped the music he made."
    }
  }
}
```

`title`、非空 `paragraphs` 必填。`source_url` 可空，存在时只能是 HTTP(S) URL。日期无法核实写“未知”，不推断为今天。

每个 `vocab` 键必须是正文实际出现的单词形式；释义和例句不可空，例句必须来自输入正文。字数范围由用户选择：用 `--min-words 400 --max-words 600` 等参数传入；省略时默认700–900词。正式稿同时校验15–25个生词；`--demo`仅用于明确标注的短文演示，不可拿演示稿充当完整学习稿。

正文和元数据会转义为安全 HTML，词表 JSON 会安全嵌入脚本。HTML 完全自包含，无外部字体、统计或网络依赖。

## 卡片 JSON

```json
{
  "date": "2026-10-20",
  "deck": "阅读单词",
  "model": "Muse 阅读单词",
  "cards": [{
    "Word": "worldly",
    "Phonetic": "/ˈwɜːldli/",
    "POS": "adj.",
    "Definition": "世俗的；老练的",
    "Example": "His worldly outlook shaped the music he made.",
    "ExampleCN": "他对世事的看法影响了他的音乐创作。",
    "Cognates": "worldliness n. 世故；老练",
    "ExampleOrigin": "original"
  }]
}
```

- `date` 必须显式填写用户当地 ISO 日期，避免用服务器时区推断。
- 例句输入纯文本，不自己加入 HTML。脚本转义后，将匹配的目标词包在 `<b>` 中。
- 例句若使用屈折变化，可填 `ExampleTerm`（例如单词 `shape`，例句形式 `shaped`）。这只控制高亮，不声称它属于某份词库。
- `ExampleOrigin` 默认为 `original`，此时 `--article` 必填且例句必须匹配正文；补写例句用 `ai_supplement`，输出额外标签便于区分。
- `Cognates` 可以空。其余7字段中的6个内容字段必须非空。
- `--existing-words existing.txt` 可在离线导出时跳过已经存在的词条；同步入库前仍需读取真实牌组去重。

输出：

- `cards.tsv`：7字段、无标题行，含HTML高亮，用UTF-8导入，开启允许HTML并按字段顺序映射。
- `notes.json`：含 `deckName`、`modelName`、7字段、日期和来源类型标签；这是请求数据，不会自动调用网络。
- `report.json`：新增数量、跳过的重复词及输入日期。

TSV 本身不携带第8列标签。手动导入时在Anki导入界面设置日期标签；通过 `notes.json` 入库则逐条带标签。
