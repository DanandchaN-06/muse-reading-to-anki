# 原始分级词表与六级差集

由用户于2026-10-20提供。原始TXT按字节保留，只改用便于命令行引用的文件名；原文件名和SHA-256见 [sources.json](sources.json)。

| 仓库文件 | 原文件名 | 非空行数 |
|---|---|---:|
| [cet6.txt](raw/cet6.txt) | 六级.txt | 5321 |
| [cet4.txt](raw/cet4.txt) | 四级.txt | 4058 |
| [gaokao.txt](raw/gaokao.txt) | 高中（高考）.txt | 3596 |
| [zhongkao.txt](raw/zhongkao.txt) | 中考.txt | 1847 |

## 六级示例

使用六级、四级、高考3个词库：**六级 −（四级 ∪ 高考）= 1174 个词条**。

- [目标词库TXT](cet6-exclusive.txt)：可以直接作为阅读改写的目标词库。
- [差集JSON与计算来源](cet6-exclusive.json)：含各输入文件的归一化计数与SHA-256。
- 中考词表作为补充原始资料收录，本次1174词计算没有额外减去中考。

归一化采用NFKC、统一大小写/撇号、合并空白；保留多词词条，不做词干化。词表名称用于识别用户文件，不表示核验为官方考试大纲。没有把整份词表改为AI生成的释义词典。

复算（从技能目录运行）：

```bash
python scripts/muse.py vocab --target assets/wordlists/raw/cet6.txt --exclude assets/wordlists/raw/cet4.txt --exclude assets/wordlists/raw/gaokao.txt --out work/target-vocab.json
```
