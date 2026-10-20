#!/usr/bin/env python3
"""Local helpers for Muse reading: vocabulary difference, HTML reader, Anki files."""
import argparse
import csv
import hashlib
import html
import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parents[1]
FIELDS = ("Word", "Phonetic", "POS", "Definition", "Example", "ExampleCN", "Cognates")
WORD = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")


def norm(text):
    return " ".join(unicodedata.normalize("NFKC", text).replace("’", "'").split()).casefold()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def words_file(path):
    path = Path(path)
    data = path.read_bytes()
    lines = data.decode("utf-8-sig").splitlines()
    entries = [norm(s) for s in lines if s.strip() and not s.lstrip().startswith("#")]
    words = set(entries)
    return words, {
        "file": path.name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "entries": len(entries),
        "unique_normalized": len(words),
    }


def vocabulary(args):
    target, provenance = words_file(args.target)
    excluded = set()
    sources = []
    for path in args.exclude:
        entries, source = words_file(path)
        excluded.update(entries)
        sources.append(source)
    result = sorted(target - excluded)
    write_json(args.out, {
        "operation": "target minus union(exclusions)",
        "normalization": "NFKC, lowercase, curly apostrophe to ASCII, collapse whitespace; no stemming",
        "target": provenance, "exclusions": sources, "count": len(result), "words": result,
    })
    print(f"Vocabulary: {len(result)} entries -> {args.out}")


def paragraphs(article):
    values = article.get("paragraphs")
    if not isinstance(values, list) or not values or any(not isinstance(x, str) or not x.strip() for x in values):
        raise ValueError("paragraphs must be a nonempty list of nonempty strings")
    return values


def in_article(sentence, parts):
    sentence = " ".join(sentence.split())
    return any(sentence in " ".join(p.split()) for p in parts)


def required(data, key):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a nonempty string")
    return value.strip()


def reader(args):
    article = read_json(args.article)
    parts = paragraphs(article)
    title = required(article, "title")
    count = len(WORD.findall(" ".join(parts)))
    vocab = article.get("vocab", {})
    if not isinstance(vocab, dict):
        raise ValueError("vocab must be an object")
    if not 0 < args.min_words <= args.max_words:
        raise ValueError("Word-count limits must satisfy 0 < min-words <= max-words")
    if not args.demo and not (args.min_words <= count <= args.max_words and 15 <= len(vocab) <= 25):
        raise ValueError(f"Expected {args.min_words}–{args.max_words} words and 15–25 vocab entries; got {count} and {len(vocab)}. --demo is for labeled short demos only.")
    normalized_vocab = {}
    present = {norm(w) for w in WORD.findall(" ".join(parts))}
    for key, value in vocab.items():
        key = norm(key)
        if key not in present:
            raise ValueError(f"Vocabulary entry absent as a single word in article: {key}")
        if key in normalized_vocab:
            raise ValueError(f"Duplicate normalized vocabulary entry: {key}")
        pos, zh, ex = (required(value, field) for field in ("pos", "zh", "ex"))
        if not in_article(ex, parts):
            raise ValueError(f"Vocabulary example is not in article: {key}")
        normalized_vocab[key] = {"pos": pos, "zh": zh, "ex": ex}
    url = article.get("source_url", "")
    if not isinstance(url, str):
        raise ValueError("source_url must be a string")
    if url and (urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc):
        raise ValueError("source_url must be an absolute HTTP(S) URL or empty")
    source = html.escape(str(article.get("source_title") or "用户提供文本"))
    if url:
        source = f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{source}</a>'
    meta = source + " · " + html.escape(str(article.get("publication_date") or "日期未知")) + f" · {count} words"
    adaptation = str(article.get("adaptation_note") or "学习阅读稿")
    if args.demo:
        adaptation = "短文演示（非完整学习稿） · " + adaptation
    meta += " · " + html.escape(adaptation)
    safe_json = json.dumps(normalized_vocab, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    values = {
        "DOC_TITLE": html.escape(title), "ARTICLE_TITLE": html.escape(title),
        "META_LINE": meta, "PARAGRAPHS": "\n".join("<p>" + html.escape(p) + "</p>" for p in parts),
        "VOCAB_JSON": safe_json, "EXPORT_BASENAME": "muse-vocab",
    }
    template = (BASE / "assets/reader-template.html").read_text(encoding="utf-8")
    result = re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: values[m[1]], template)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result, encoding="utf-8")
    print(f"Reader: {count} words / {len(vocab)} vocabulary entries -> {output}")


def cards(args):
    data = read_json(args.input)
    day = required(data, "date")
    if date.fromisoformat(day).isoformat() != day:
        raise ValueError("date must be YYYY-MM-DD")
    source_cards = data.get("cards")
    if not isinstance(source_cards, list):
        raise ValueError("cards must be a list")
    parts = paragraphs(read_json(args.article)) if args.article else None
    existing = words_file(args.existing_words)[0] if args.existing_words else set()
    seen, notes, skipped = set(existing), [], []
    for raw in source_cards:
        word = required(raw, "Word")
        key = norm(word)
        if key in seen:
            skipped.append(word)
            continue
        plain = {name: (str(raw.get(name) or "") if name == "Cognates" else required(raw, name)) for name in FIELDS}
        origin = raw.get("ExampleOrigin", "original")
        if origin not in ("original", "ai_supplement"):
            raise ValueError(f"Unknown ExampleOrigin: {origin}")
        if origin == "original" and (parts is None or not in_article(plain["Example"], parts)):
            raise ValueError(f"Original example not verified against --article: {word}")
        term = raw.get("ExampleTerm", word)
        if not isinstance(term, str) or not term.strip():
            raise ValueError(f"Invalid ExampleTerm: {word}")
        pattern = re.compile(r"(?<![A-Za-z])" + re.escape(term.strip()) + r"(?![A-Za-z])", re.I)
        matches = list(pattern.finditer(plain["Example"]))
        if not matches:
            raise ValueError(f"Example does not contain {term!r}")
        fields = {k: html.escape(" ".join(v.split())) for k, v in plain.items()}
        chunks, start = [], 0
        for match in matches:
            chunks.extend((html.escape(plain["Example"][start:match.start()]), "<b>" + html.escape(match.group()) + "</b>"))
            start = match.end()
        chunks.append(html.escape(plain["Example"][start:]))
        fields["Example"] = " ".join("".join(chunks).split())
        notes.append({
            "deckName": data.get("deck") or "阅读单词",
            "modelName": data.get("model") or "Muse 阅读单词",
            "fields": fields,
            "tags": ["muse", "muse::date::" + day, "muse::" + origin],
        })
        seen.add(key)
    folder = Path(args.out_dir)
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "cards.tsv").open("w", encoding="utf-8-sig", newline="") as stream:
        csv.writer(stream, delimiter="\t", lineterminator="\n").writerows([[n["fields"][k] for k in FIELDS] for n in notes])
    write_json(folder / "notes.json", notes)
    write_json(folder / "report.json", {"date": day, "prepared": len(notes), "skipped_duplicates": skipped, "network_actions": 0})
    print(f"Cards: {len(notes)} prepared / {len(skipped)} duplicates skipped -> {folder}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("vocab", help="Compute target minus union of exclusions")
    v.add_argument("--target", required=True)
    v.add_argument("--exclude", action="append", default=[])
    v.add_argument("--out", required=True)
    v.set_defaults(run=vocabulary)
    r = sub.add_parser("reader", help="Create a standalone reading HTML")
    r.add_argument("--article", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--demo", action="store_true")
    r.add_argument("--min-words", type=int, default=700)
    r.add_argument("--max-words", type=int, default=900)
    r.set_defaults(run=reader)
    c = sub.add_parser("cards", help="Prepare seven-field TSV and AnkiConnect note data; no networking")
    c.add_argument("--input", required=True)
    c.add_argument("--article")
    c.add_argument("--existing-words")
    c.add_argument("--out-dir", required=True)
    c.set_defaults(run=cards)
    args = parser.parse_args()
    try:
        args.run(args)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
