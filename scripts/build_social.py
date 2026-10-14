"""Build the social studies question bank from the supplied PDF and reviewed theory."""
from pathlib import Path
import json,re,sys,subprocess
import pymupdf as fitz
from PIL import Image,ImageOps,ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path.home()/'Downloads/박봄의[1등급2주특강]_2학기2차_20232025기출_2권_35단원.pdf'
doc=fitz.open(SOURCE)
out=ROOT/'assets/social/questions';out.mkdir(parents=True,exist_ok=True)
answers={int(n):a for n,a in re.findall(r'(\d+)\s*([①②③④⑤])',doc[-1].get_text())}
assert len(answers)==30
questions=[]
for pi in range(1,19):
 p=doc[pi];markers=[]
 for b in p.get_text('dict')['blocks']:
  for line in b.get('lines',[]):
   text=''.join(s['text'] for s in line['spans'])
   m=re.match(r'^(\d+)\.\s',text)
   if m and abs(line['bbox'][0]-85.08)<2 and 1<=int(m[1])<=30:markers.append((int(m[1]),line['bbox'],text))
 for ix,(n,box,title) in enumerate(markers):
  end=markers[ix+1][1][1]-12 if ix+1<len(markers) else p.rect.height-48
  # Preserve charts and tables, including non-text images, between question headings.
  option_ends=[w[3] for w in p.get_text('words') if '⑤' in w[4] and box[1]<w[1]<end]
  assert option_ends,n
  end=min(end,max(option_ends)+15)
  clip=fitz.Rect(76,box[1]-5,p.rect.width-70,end)
  text=p.get_text(clip=clip,sort=True).strip()
  date=re.search(r'\[(20\d{2})\.\s*(\d+)\.\s*(\d+)번\]',text)
  assert date,(n,text)
  pix=p.get_pixmap(matrix=fitz.Matrix(2.4,2.4),clip=clip,alpha=False)
  im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
  im.save(out/f'social-{n:02}.webp',quality=90)
  questions.append(dict(id=f'social-{n:02}',unit=3 if n<=14 else 4 if n<=24 else 5,number=n,type='choice',title=re.sub(r'^\d+\.\s*','',title),text=text,image=f'assets/social/questions/social-{n:02}.webp',answer=answers[n],source='EBSi 문제',sourceBook='EBSi 통합사회2 문제 자료',sourcePage=pi+1,printedPage=pi+1,answerPage=20,examYear=int(date[1]),examMonth=int(date[2]),examNumber=int(date[3])))
assert len(questions)==len({q['id'] for q in questions})==30
explanations=json.loads((ROOT/'content/social-explanations.json').read_text(encoding='utf-8'))
for q in questions:q['explanation']=explanations[str(q['number'])]
(ROOT/'content/social-questions.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2),encoding='utf-8')
units=json.loads((ROOT/'content/social-units.json').read_text(encoding='utf-8'))
data={'units':units,'questions':questions,'groups':[u['title'] for u in units],'version':1}
(ROOT/'social-data.js').write_text('window.SOCIAL_DATA = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print('Built 3 social chapters and 30 verified answer keys')
sheet=Image.new('RGB',(1200,((len(questions)+3)//4)*440),'#ddd');draw=ImageDraw.Draw(sheet)
for i,q in enumerate(questions):
 im=Image.open(ROOT/q['image']);im.thumbnail((290,408));x=(i%4)*300;y=(i//4)*440;sheet.paste(im,(x,y+25));draw.text((x+5,y+5),str(q['number']),fill='black')
sheet.save(ROOT/'.qa/social-contact.jpg')
