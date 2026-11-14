#!/usr/bin/env python3
"""Provenance, Wiki-to-Claim, and Slide-to-Claim quality gate for Fourth Mirror.
The default gate permits an in-progress project, but NEVER reports source records as real ingests.
--strict requires five independently inspected, verifiable source bodies/sections.
Also validates Wiki frontmatter source/claim consistency, raw LaTeX absence,
scene_claim_map claim-to-source coverage, bibliography scope disclosure, and HTML accessibility attributes.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

parser = argparse.ArgumentParser()
parser.add_argument('--strict', action='store_true', help='Fail unless >= 5 true verified ingest records')
args = parser.parse_args()
issues = []
warnings = []
checks = []

def check(condition, code, desc):
    checks.append({'id': code, 'passed': bool(condition), 'description': desc})
    if not condition: issues.append(f'{code}: {desc}')

sources = read_json('raw/source_registry.json')
manifest = read_json('raw/ingest_manifest.json')
claims = read_json('wiki/claims.json')
scenes = read_json('slides/scene_claim_map.json')
ids = {s['id'] for s in sources}
claim_ids = {c['id'] for c in claims}
claim_map = {c['id']: c for c in claims}
manifest_ids = {i['id'] for i in manifest}
check(len(sources) >= 5, 'source_registry', f'來源登記有 {len(sources)} 筆（不代表已 ingest）')
check(len(ids) == len(sources), 'source_ids_unique', '來源登記 ID 唯一')
check(ids == manifest_ids, 'manifest_covers_registry', 'ingest 清單涵蓋來源登記')
check(len(scenes) == 12 and sorted(x['scene_index'] for x in scenes) == list(range(12)), 'scene_map_indices', '12 幕各有唯一索引')
check(all(set(s['claim_ids']) <= claim_ids and set(s['source_ids']) <= ids for s in scenes), 'scene_map_refs', '逐幕 Claim ID / Source ID 均存在')

# Pre-check (Node G): Every scene's source_ids must cover the union of sources required by its claim_ids
scene_source_coverage_mismatches = []
for s in scenes:
    expected_sources = sorted({sid for cid in s['claim_ids'] for sid in claim_map[cid].get('sources', [])})
    if sorted(s['source_ids']) != expected_sources:
        scene_source_coverage_mismatches.append(s['scene_number'])
check(
    not scene_source_coverage_mismatches,
    'scene_claim_source_coverage',
    f'逐幕 source_ids 與其 claim_ids 所需來源集合完全一致（不一致幕：{scene_source_coverage_mismatches}）'
)

valid_ingest = []
for item in manifest:
    sid = item['id']
    if not item.get('ingested_verifiable_content'):
        continue
    # Require a real verified document read, precise evidence anchor, and date.
    if item.get('capture_status') != 'ingested_verifiable_content':
        issues.append(f'{sid}: ingested_verifiable_content=true but capture_status inconsistent')
        continue
    if not (item.get('content_access_confirmed') and item.get('retrieved_at') and item.get('verified_anchor')):
        issues.append(f'{sid}: incomplete provenance (access/date/anchor)')
        continue
    if item.get('source_body_in_repository'):
        filename=item.get('local_source_path')
        if not filename or not (ROOT/filename).is_file():
            issues.append(f'{sid}: local_source_path missing')
            continue
        sha = hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()
        if sha != item.get('checksum_sha256'):
            issues.append(f'{sid}: SHA256 mismatch')
            continue
    elif not item.get('url'):
        issues.append(f'{sid}: no local file or permanent source URL')
        continue
    valid_ingest.append(sid)

for c in claims:
    if c['kind'] not in ['fiction','editorial'] and not c.get('sources'):
        issues.append(f"{c['id']}: scholarship without sources")
    if not set(c.get('sources',[])) <= ids:
        issues.append(f"{c['id']}: nonexistent Source ID")
    if not (ROOT / 'wiki' / 'concepts' / (c['wiki'] + '.md')).is_file():
        issues.append(f"{c['id']}: missing concept page")
    if c['view']=='self2' and c.get('speaker_status') == 'inferred':
        issues.append(f"{c['id']}: inferred opinion classified as real testimony")
    if c.get('origin')=='buddhist-canonical' and '四面鏡' in c.get('claim',''):
        issues.append(f"{c['id']}: original teaching frame called Buddhist canon")

# Pre-check (Node F): Wiki concept pages frontmatter source_ids vs claim_ids consistency & no raw LaTeX $...$
concept_sync_errors = []
for cpath in (ROOT / 'wiki' / 'concepts').glob('*.md'):
    txt = cpath.read_text(encoding='utf-8')
    src_m = re.search(r'source_ids:\s*\[([^\]]*)\]', txt)
    clm_m = re.search(r'claim_ids:\s*\[([^\]]*)\]', txt)
    if src_m is not None and clm_m is not None:
        listed_srcs = sorted([x.strip() for x in src_m.group(1).split(',') if x.strip()])
        listed_clms = [x.strip() for x in clm_m.group(1).split(',') if x.strip()]
        expected_srcs = sorted({sid for cid in listed_clms if cid in claim_map for sid in claim_map[cid].get('sources', [])})
        if listed_srcs != expected_srcs:
            concept_sync_errors.append(f"{cpath.stem} (listed {listed_srcs} != expected {expected_srcs})")
check(not concept_sync_errors, 'wiki_concept_source_sync', f'Wiki 概念頁 source_ids 與 claim_ids 完全一致（不一致：{concept_sync_errors}）')

wiki_html_txt = (ROOT / 'slides' / 'wiki.html').read_text(encoding='utf-8')
check(not re.search(r'\$k\s*=', wiki_html_txt), 'no_unrendered_latex_wiki', 'slides/wiki.html 無未渲染之 $k = ...$ LaTeX 語法')
wiki_data_m = re.search(r'<script>const DATA=(\{[^\r\n]*?\});\r?\n', wiki_html_txt)
wiki_data_valid = False
if wiki_data_m:
    try:
        wdata = json.loads(wiki_data_m.group(1))
        wiki_data_valid = len(wdata.get('blocks', [])) == 15 and len(wdata.get('claims', [])) == len(claims) and len(wdata.get('sources', [])) == len(sources)
    except Exception:
        wiki_data_valid = False
check(wiki_data_valid, 'wiki_html_valid_json_data', 'slides/wiki.html 內嵌 DATA 為合法單行 JSON（無未跳脫換行，含 15 頁區塊、11 條 Claim、6 筆來源）')

html = (ROOT/'slides/deck.html').read_text(encoding='utf8')
check('const scenes=[' in html and html.count('()=>`') == 12, 'deck_12_scenes', 'HTML 仍有 12 幕')
check('sceneRefs=' in html and 'showSources' in html, 'source_drawer', '逐頁來源面板存在')
# This checks the source panel indexes align with the traceability document.
ref_match=re.search(r'const sceneRefs=(\[[^;]+\]);',html)
if ref_match:
    try:
        deck_refs=json.loads(ref_match.group(1).replace("'",'"'))
        mismatch=[i+1 for i,entry in enumerate(scenes) if deck_refs[i] != entry['source_ids']]
        check(not mismatch,'scene_refs_in_sync',f'來源面板和逐頁地圖一致（不一致頁：{mismatch}）')
    except (ValueError, IndexError):
        issues.append('scene_refs_in_sync: unable to parse current sceneRefs')
else:
    issues.append('scene_refs_in_sync: sceneRefs not found')

# Pre-check (Node H): Accessibility, valid HTML nesting, and abstract-scope disclosure in deck.html
check('class="aggregate' in html and 'data-aggregate="${x[0]}" aria-pressed=' in html, 'deck_aggregate_aria_pressed', '五蘊互動按鈕具備 aria-pressed 無障礙屬性')
check(not re.search(r'<p[^>]*>[^<]*\$\{wikiSourceTags', html), 'deck_valid_p_nesting', 'wikiSourceTags 未錯誤嵌於 <p> 標籤內')
check('PMID 34352724' in html and 'PMID 42083441' in html, 'deck_bibliography_scope_disclosure', 'deck.html 文獻面板誠實揭露 S02 與 S03 之 PubMed 摘要驗證範圍')

if len(valid_ingest) < 5:
    msg = f'目前真正有錨點、日期、存取核查的來源只有 {len(valid_ingest)} 篇，最低需要 5 篇；來源登記 {len(sources)} 筆不能代替 ingest'
    if args.strict: issues.append('ingest_minimum: ' + msg)
    else: warnings.append('ingest_minimum: ' + msg)

result = {
  'status': 'PASS' if not issues else 'FAIL',
  'mode': 'strict' if args.strict else 'development',
  'registered_sources': len(sources),
  'verified_content_ingests': len(valid_ingest),
  'verified_ingest_ids': valid_ingest,
  'claim_count': len(claims),
  'scene_count': len(scenes),
  'checks': checks,
  'warnings': warnings,
  'issues': issues,
}
out=ROOT/'tests'/('quality_gate_strict_results.json' if args.strict else 'quality_gate_results.json')
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(1 if issues else 0)
