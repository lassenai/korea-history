"""Render source-faithful question crops and extract the supplied EBS answer key.
Run: python scripts/extract_ebs.py (requires pymupdf, pillow, pypdf).
Source PDFs remain outside the public repository.
"""
from pathlib import Path
import json, re, sys
import pymupdf as fitz
from PIL import Image
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path.home() / 'Downloads/최소성취수준보장지도_한국사2_학습지(통합본).pdf'
doc = fitz.open(SOURCE)
reader = PdfReader(SOURCE)
out = ROOT / 'assets/questions'
out.mkdir(parents=True, exist_ok=True)

def lines(page):
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            yield line['bbox'], ''.join(s['text'] for s in line['spans'])

questions=[]
for unit in range(1,21):
    keypage=unit*3
    keytext=reader.pages[keypage].extract_text()
    matches=list(re.finditer(r'(\d+)\.\s*답\s*([^\n]+)',keytext))
    keys={}
    for j,m in enumerate(matches):
        end=matches[j+1].start() if j+1<len(matches) else len(keytext)
        exp=keytext[m.end():end].strip()
        exp=re.sub(r'\n\d+\s*\n최소 성취수준.*','',exp,flags=re.S)
        keys[int(m[1])]=(m[2].strip(),exp)
    assert set(keys)==set(range(1,9)),(unit,keys)
    for pi in [unit*3-2,unit*3-1]:
        page=doc[pi]
        markers=[]
        for box,t in lines(page):
            m=re.match(r'^([1-8])\.\s',t.strip())
            if m and (abs(box[0]-62.36)<2 or abs(box[0]-311.81)<2):
                markers.append((int(m[1]),box,t))
        assert len(markers)==4,(unit,pi,markers)
        for num,box,title in markers:
            left=box[0]<300
            x0,x1=(56,291) if left else (305,548)
            next_y=min([b[1]-8 for n,b,t in markers if (b[0]<300)==left and b[1]>box[1]+3]+[784])
            words=page.get_text('words',clip=fitz.Rect(x0,box[1]-3,x1,next_y))
            bottom=min(next_y,max(w[3] for w in words)+9)
            clip=fitz.Rect(x0,box[1]-6,x1,bottom)
            pix=page.get_pixmap(matrix=fitz.Matrix(3,3),clip=clip,alpha=False)
            image=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
            ident=f'ebs-{unit:02}-{num:02}'
            image.save(out/(ident+'.webp'),quality=88,method=6)
            text=page.get_text(clip=clip,sort=True).strip()
            answer,explanation=keys[num]
            kind='choice' if answer in '①②③④⑤' else 'short'
            questions.append(dict(id=ident,unit=unit,number=num,type=kind,title=title,
                text=text,image=f'assets/questions/{ident}.webp',answer=answer,
                explanation=explanation,source='EBSi 문제',sourceBook=SOURCE.name,
                sourcePage=pi+1,printedPage=pi,answerPage=keypage+1))
questions.sort(key=lambda q:(q['unit'],q['number']))
assert len(questions)==160
(ROOT/'content/ebs.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Extracted {len(questions)} questions; {sum(q["type"]=="choice" for q in questions)} choice questions.')
