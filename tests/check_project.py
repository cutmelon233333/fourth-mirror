#!/usr/bin/env python3
"""Deterministic structural + provenance QA. No external dependencies."""
from pathlib import Path
import re,json,sys
ROOT=Path(__file__).resolve().parents[1]
CLAIMS=json.loads((ROOT/'wiki'/'claims.json').read_text(encoding='utf8'))
SOURCES=json.loads((ROOT/'raw'/'source_registry.json').read_text(encoding='utf8'))
source_ids={s['id'] for s in SOURCES}
issues=[]

def validate_claim(c):
    err=[]
    if c['kind'] in ['scholarly','scholarly-synthesis','operational-definition','interpretive-synthesis'] and not c.get('sources'):
        err.append('來源缺漏')
    if not set(c.get('sources',[])).issubset(source_ids):err.append('來源 ID 不存在')
    if c.get('view')=='self2' and c.get('speaker_status')=='inferred':err.append('Self 3 的猜測被標作 Self 2')
    if c.get('origin')=='buddhist-canonical' and '四面鏡' in c['claim']:err.append('四面鏡被錯誤歸為佛教原典')
    return err

for c in CLAIMS:
    errors=validate_claim(c)
    issues+= [f'{c["id"]}: {e}' for e in errors]
    page=ROOT/'wiki'/'concepts'/(c['wiki']+'.md')
    if not page.exists():issues.append(f'{c["id"]}: 對應 Wiki 頁缺失 {c["wiki"]}')
for s in SOURCES:
    for rel in [f'raw/{s["id"]}_source_record.md',f'wiki/sources/{s["id"]}.md']:
        if not (ROOT/rel).exists():issues.append(f'缺少 {rel}')
if len(SOURCES)<5:issues.append('ingest 資料少於 5 篇')
index=(ROOT/'wiki'/'index.md').read_text(encoding='utf8')
for s in SOURCES:
    if f'[[{s["id"]}]]' not in index:issues.append('索引缺少 '+s['id'])
for concept in (ROOT/'wiki'/'concepts').glob('*.md'):
    if f'[[{concept.stem}]]' not in index:issues.append('索引缺少概念 '+concept.stem)
    src=concept.read_text(encoding='utf8')
    for x in re.findall(r'\[\[([^\]]+)\]\]',src):
        if x not in source_ids and not (ROOT/'wiki'/'concepts'/(x+'.md')).exists():issues.append(f'壞連結 {concept.name} → {x}')
html=(ROOT/'slides'/'deck.html').read_text(encoding='utf8')
if 'const scenes=[' not in html or html.count('()=>`')!=12:issues.append('互動簡報頁數應為 12')
for x in ['data-reaction','data-action','data-explore','data-quiz','data-aggregate','data-restart','showSources','ArrowRight']:
    if x not in html:issues.append('缺少互動 '+x)
for sid in source_ids:
    if f'{sid}:' not in html:issues.append('簡報來源面板缺少 '+sid)
if 'self1' not in html.lower() and 'self 1' not in html.lower():issues.append('缺少 Self 1')
# Deliberately broken fixtures, measuring guards BEFORE slides.
fixtures=json.loads((ROOT/'tests'/'fixtures.json').read_text(encoding='utf8'))
fixture_results=[]
for f in fixtures:
    got=validate_claim(f['claim'])
    expected=f['expect']
    fixture_results.append({'fixture':f['id'],'expected':expected,'detected':got,'passed':expected in got})
    if expected not in got:issues.append('未阻擋合成錯誤 '+f['id'])
report={'status':'PASS' if not issues else 'FAIL','sources_registered':len(SOURCES),'claims':len(CLAIMS),'concept_pages':len(list((ROOT/'wiki'/'concepts').glob('*.md'))),'slides':html.count('()=>`'),'fixtures':fixture_results,'issues':issues}
(ROOT/'tests'/'structural_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(0 if not issues else 1)
