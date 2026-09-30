#!/usr/bin/env python3
"""
Extract every cefr/texts source document to plain text, for auditing and
for feeding the reading-page/audio pipeline.

Why this exists: the reading library shipped as .docx + .pdf only, with no
HTML, so the text had to be recovered before it could be reviewed or
converted. Uses nothing but the stdlib -- a .docx is a zip of XML, and this
machine has no python-docx/pandoc.

Source of truth is the .docx where one exists; the .pdf is ignored (they are
exports of the same document). Only `mind-games` was pdf-only, and it was
image-based with no extractable text, so it was deleted.

Walking only <w:t> nodes is the obvious approach and is wrong: Word stores a
non-breaking hyphen as its own <w:noBreakHyphen/> element, so "risk-adjusted"
comes out as "riskadjusted" and "per-transaction" as "pertransaction". Line
breaks (<w:br/>) and tabs (<w:tab/>) are separate elements too. para_text()
handles all of them.

Also strips the teacher contact block Word keeps in each document's header
text box (the site's own chrome supplies that on the page), and collapses the
duplicated title lines that text boxes leave behind.

Usage:
    python3 scripts/extract_source_docs.py <output-dir>
"""
import zipfile, re, sys, json
from pathlib import Path
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
SRC = Path(__file__).resolve().parent.parent / 'cefr' / 'texts'
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
BOILER = re.compile(r'^(Teacher|Renan Grossi|Tel\.:?\s*98135\s*3067|\(51\)\s*98135\s*3067)$')

def para_text(p):
    parts = []
    for el in p.iter():
        t = el.tag
        if t == f'{W}t':
            parts.append(el.text or '')
        elif t == f'{W}noBreakHyphen':
            parts.append('-')
        elif t == f'{W}softHyphen':
            parts.append('')
        elif t in (f'{W}tab',):
            parts.append('\t')
        elif t in (f'{W}br', f'{W}cr'):
            parts.append('\n')
    return ''.join(parts)

def docx_paras(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    return [para_text(p).strip() for p in root.find(f'{W}body').iter(f'{W}p')]

def clean(paras):
    res = []
    for p in paras:
        p = re.sub(r'(TeacherRenan Grossi(\(51\)|Tel\.:)?\s*98135\s*3067)+', '', p).strip()
        if not p or BOILER.match(p):
            continue
        res.append(p)
    # collapse the duplicated title lines Word leaves in text boxes
    out = []
    for p in res:
        if out and p == out[-1]:
            continue
        out.append(p)
    return out

index = {}
bases = sorted({f.stem for f in SRC.iterdir() if f.suffix in ('.docx', '.pdf')})
for b in bases:
    dx = SRC / f'{b}.docx'
    if not dx.exists():
        index[b] = {'source': 'pdf-only'}
        continue
    try:
        paras = clean(docx_paras(dx))
    except Exception as e:
        index[b] = {'error': f'{e}'}; continue
    txt = '\n'.join(paras)
    (OUT / f'{b}.txt').write_text(txt, encoding='utf-8')
    index[b] = {'source': 'docx', 'paras': len(paras), 'words': len(txt.split()),
                'title': paras[0] if paras else ''}
Path(OUT / '_index.json').write_text(json.dumps(index, indent=1, ensure_ascii=False))
ok = [k for k,v in index.items() if 'words' in v]
print(f'extracted {len(ok)}/{len(bases)}; words={sum(v["words"] for v in index.values() if "words" in v)}')
