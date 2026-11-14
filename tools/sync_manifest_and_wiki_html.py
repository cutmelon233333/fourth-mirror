#!/usr/bin/env python3
"""Refresh SHA-256 checksums in raw/ingest_manifest.json and rebuild slides/wiki.html DATA from the Markdown Wiki.

Non-destructive: existing manifest fields (retrieval time, access scope, notes) are kept; only checksum_sha256 is recomputed.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 1. Recompute checksums of raw/original/S0X_verified_ingest.md (raw evidence itself is never rewritten here)
manifest_path = ROOT / "raw" / "ingest_manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
for entry in manifest:
    full_path = ROOT / entry["local_source_path"]
    entry["checksum_sha256"] = hashlib.sha256(full_path.read_bytes()).hexdigest()
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# 2. Rebuild DATA in slides/wiki.html from wiki/concepts/*.md, wiki/sources/*.md, wiki/claims.json, raw/source_registry.json
from urllib.parse import quote

sources = json.loads((ROOT / "raw" / "source_registry.json").read_text(encoding="utf-8"))

def md_to_simple_html(md_text: str) -> str:
    # Strip YAML frontmatter
    md_text = re.sub(r"^---\n.*?\n---\n", "", md_text, flags=re.S).strip()
    lines = md_text.splitlines()
    out = []
    in_ul = False
    para = []

    def flush_para():
        nonlocal para
        if para:
            text = " ".join(para)
            out.append(f"<p>{inline_fmt(text)}</p>")
            para = []

    def inline_fmt(t: str) -> str:
        # Links [label](url)
        t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
        # Wiki links [[Page]]
        def repl_wiki(m):
            target = m.group(1)
            return f'<a href="#p-{quote(target)}">{target}</a>'
        t = re.sub(r"\[\[([^\]]+)\]\]", repl_wiki, t)
        # Bold **...**
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        # Italic *...*
        t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
        # Code `...`
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        return t

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            flush_para()
            if in_ul:
                out.append("</ul>")
                in_ul = False
            continue
        if line.startswith("# "):
            flush_para()
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h1>{inline_fmt(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            flush_para()
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h2>{inline_fmt(line[3:].strip())}</h2>")
        elif line.startswith("- "):
            flush_para()
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_fmt(line[2:].strip())}</li>")
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if raw_line.endswith("  "):
                para.append(line + "<br />")
            else:
                para.append(line)
    flush_para()
    if in_ul:
        out.append("</ul>")
    return "\n".join(out) + "\n"

blocks = []
for cpath in sorted((ROOT / "wiki" / "concepts").glob("*.md"), key=lambda p: p.stem):
    blocks.append({
        "name": cpath.stem,
        "html": md_to_simple_html(cpath.read_text(encoding="utf-8")),
        "kind": "概念",
        "file": f"wiki/concepts/{cpath.name}",
    })
for spath in sorted((ROOT / "wiki" / "sources").glob("*.md"), key=lambda p: p.stem):
    blocks.append({
        "name": spath.stem,
        "html": md_to_simple_html(spath.read_text(encoding="utf-8")),
        "kind": "來源",
        "file": f"wiki/sources/{spath.name}",
    })

claims = json.loads((ROOT / "wiki" / "claims.json").read_text(encoding="utf-8"))
data_obj = {
    "blocks": blocks,
    "claims": claims,
    "sources": sources,
}
data_json = json.dumps(data_obj, ensure_ascii=False).replace("</", "<\\/")

wiki_html_path = ROOT / "slides" / "wiki.html"
wiki_html = wiki_html_path.read_text(encoding="utf-8")
wiki_html_updated = re.sub(
    r"<script>const DATA=\{.*?\};\n",
    lambda _: f"<script>const DATA={data_json};\n",
    wiki_html,
    count=1,
    flags=re.S,
)
wiki_html_path.write_text(wiki_html_updated, encoding="utf-8")
print("Manifest updated and slides/wiki.html synchronized. Verified ingests:", len(manifest))
