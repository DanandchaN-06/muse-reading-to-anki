# Anki 卡片模板：英语阅读单词

## 字段（7 个）
`Word`（单词） · `Phonetic`（音标） · `POS`（词性） · `Definition`（中文释义） · `Example`（例句） · `ExampleCN`（例句中文翻译） · `Cognates`（同源词）

## 正面模板（Front Template）
```html
<div class="word">{{Word}}</div>
<div class="phonetic">{{Phonetic}}</div>
```

## 背面模板（Back Template）
```html
{{FrontSide}}
<div class="answer">
<div><span class="pos">{{POS}}</span><span class="def">{{Definition}}</span></div>
<div class="example">{{Example}}</div>
<div class="examplecn">{{ExampleCN}}</div>
{{#Cognates}}<div class="cognates"><span class="coglabel">同源词</span>{{Cognates}}</div>{{/Cognates}}
</div>
```

## 样式（Styling / CSS）
```css
.card {
  --bg: #f7f5f0; --fg: #2b2b2b; --muted: #9a9a9a; --accent: #b3541e;
  --exfg: #4a4a4a; --hl: #ffe9a8; --line: #e2ddd0;
  font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Segoe UI", sans-serif;
  background: var(--bg); color: var(--fg);
  text-align: center; padding: 30px 22px;
}
.nightMode .card {
  --bg: #2e2e30; --fg: #e6e6e6; --muted: #8f8f8f; --accent: #d08a3e;
  --exfg: #bdbdbd; --hl: #5a4a1f; --line: #4a4a4c;
}
.word {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 46px; font-weight: 700; letter-spacing: .5px; color: var(--fg);
  white-space: nowrap; word-break: keep-all;
}
.phonetic { margin-top: 8px; color: var(--muted); font-size: 15px; }
.answer { margin-top: 20px; border-top: 1px solid var(--line); padding-top: 20px; }
.pos { color: var(--accent); font-style: italic; font-size: 15px; margin-right: 10px; }
.def { font-size: 23px; font-weight: 600; }
.example {
  margin: 18px auto 0; max-width: 520px; text-align: left;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 16.5px; line-height: 1.8; color: var(--exfg); font-style: italic;
  border-left: 3px solid var(--accent); padding: 2px 0 2px 14px;
}
.example b { font-style: normal; color: var(--fg); background: var(--hl); padding: 0 4px; border-radius: 4px; }
.examplecn { margin: 10px auto 0; max-width: 520px; text-align: left; font-size: 14px; color: var(--muted); line-height: 1.7; }
.cognates { margin: 14px auto 0; max-width: 520px; text-align: left; font-size: 14.5px; line-height: 1.9; color: var(--muted); border-top: 1px dashed var(--accent); padding-top: 10px; }
.cognates .coglabel { display: inline-block; font-size: 11px; letter-spacing: 1px; color: var(--accent); border: 1px solid var(--accent); border-radius: 4px; padding: 0 6px; margin-right: 8px; vertical-align: 1px; }
```

## 设计说明
- 正面只考认读：大号衬线单词（`white-space: nowrap` 强制一行，长词也不断行）+ 音标。
- 背面：词性（斜体橙色）+ 中文释义大字；例句中目标词加粗并以 `#ffe9a8` 高亮；附例句中文翻译。
- 「同源词」区仅在字段非空时显示：格式为 `词 词性. 中文`，多个用 `·` 分隔，如 `heraldic adj. 纹章的 · heraldry n. 纹章学`。
- 支持夜间模式（`.nightMode` 变量切换）。
