from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
units=json.loads((ROOT/'content/units.json').read_text(encoding='utf-8'))
qs=json.loads((ROOT/'content/ebs.json').read_text(encoding='utf-8'))
for u in units:
    for typ,key in [('blank','blank'),('essay','essay')]:
        q=u[key]
        qs.append(dict(id=f'{typ}-{u["id"]:02}',unit=u['id'],number=9 if typ=='blank' else 10,type=typ,title=q['prompt'],text=q['prompt'],answer=q.get('answer',q.get('model')),explanation=q.get('explanation',q.get('model')),criteria=q.get('criteria',[]),source='자체 제작',sourceBook='EBSi 한국사2 자료 참고 · 자체 작성',sourcePage=u['sourcePages'][0]))
conversions=json.loads((ROOT/'content/choice-conversions.json').read_text(encoding='utf-8'))
for q in qs:
    if q['type']=='choice':continue
    c=conversions[q['id']]
    correct=c.get('correct',' '.join(q['answer'].split()))
    q['originalType']=q['type']
    q['originalAnswer']=q['answer']
    q['type']='choice'
    q['converted']=True
    q['options']=list(c['distractors'])
    index=(q['unit']+q['number'])%5
    q['options'].insert(index,correct)
    q['answer']='①②③④⑤'[index]
    q['answerText']=correct
    q.pop('criteria',None)
    if 'prompt' in c:q['title']=q['text']=c['prompt']
    elif q['id'].startswith('blank-'):q['title']=q['text']='빈칸에 들어갈 말로 옳은 것은?\n'+q['text']
    assert len(q['options'])==len(set(q['options']))==5
assert len(conversions)==70
qs.sort(key=lambda q:(q['unit'],q['number']))
assert len(qs)==200 and len({q['id'] for q in qs})==200
data={'units':units,'questions':qs,'groups':['일제 식민 통치와 민족운동','대한민국의 발전','오늘날의 대한민국'],'version':2}
(ROOT/'data.js').write_text('window.HISTORY_DATA = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print(f'Built {len(units)} units and {len(qs)} questions')
