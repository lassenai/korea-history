from pathlib import Path
import json,re
from PIL import Image
from pypdf import PdfReader
root=Path(__file__).resolve().parents[1]
units=json.loads((root/'content/units.json').read_text(encoding='utf-8'))
qs=json.loads((root/'content/ebs.json').read_text(encoding='utf-8'))
pdf=PdfReader(Path.home()/'Downloads/최소성취수준보장지도_한국사2_학습지(통합본).pdf')
assert [u['id'] for u in units]==list(range(1,21))
for u in units:
    assert len(u['sections'])>=3 and len(u['essay']['criteria'])==3
    assert u['blank']['answer'] and '____' in u['blank']['prompt']
for u in range(1,21):
    batch=[q for q in qs if q['unit']==u]
    assert len(batch)==8 and {q['number'] for q in batch}==set(range(1,9))
    key=dict(re.findall(r'(\d+)\.\s*답\s*([^\n]+)',pdf.pages[u*3].extract_text()))
    for q in batch:
        assert q['answer']==key[str(q['number'])].strip(),q['id']
        assert q['explanation'] and len(q['explanation'])>50
        assert re.match(rf'^{q["number"]}\.',q['text']),q['id']
        image=Image.open(root/q['image'])
        assert image.width>=700 and image.height>=180,(q['id'],image.size)
assert len(qs)==160
print('PASS: 20 units, all 160 source answers match PDF, all original question crops and explanations present; 40 authored questions ready.')
