from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
topics=json.loads((ROOT/'content/social-theory-topics.json').read_text(encoding='utf-8'))
# Complement the theory PDF with concepts explicitly tested in the question PDF.
topics[0]['topics'][4][2]+=' 자산 관리에서는 안전성(원금 보전 가능성), 수익성(수익을 얻을 가능성), 유동성(현금으로 바꾸기 쉬운 정도)을 함께 고려합니다.'
topics[1]['topics'][-1][4]='울릉도와 독도를 구분하세요. 독도는 우리나라 영토의 가장 동쪽에 있으며, 이어도 종합 해양 과학 기지와 혼동하면 안 됩니다.'
topics[1]['topics'].extend([
 ['국제 사회의 행위 주체','보완','국가는 영토·국민·주권을 갖춘 국제 사회의 기본적인 행위 주체입니다. 정부 간 국제기구는 여러 국가의 정부가 협력하여 구성하며, 국제 비정부 기구는 민간의 개인이나 단체를 중심으로 활동합니다.','국제 연합(UN)은 정부 간 국제기구, 국경 없는 의사회는 국제 비정부 기구입니다. 누가 구성하고 어떤 목적을 추구하는지 구분하세요.','이름에 국제라는 말이 있다고 모두 정부 간 국제기구인 것은 아닙니다.','20',['국가','주권','정부 간 국제기구','국제 비정부 기구']],
 ['통일 비용·분단 비용·통일 편익','보완','분단 비용은 분단 상태를 유지하면서 반복적으로 치르는 비용입니다. 통일 비용은 서로 다른 체제를 통합하는 과정에서 발생하는 비용이고, 통일 편익은 통일로 얻는 이익입니다.','분단 비용의 감소와 시장 확대 등은 통일 편익에 포함됩니다. 통일의 의미를 평가할 때 비용뿐 아니라 장기적 편익도 함께 비교합니다.','통일 비용은 통일 이전에만 발생하는 것이 아니라 통일 전후의 통합 과정에서 발생합니다.','24',['분단 비용','통일 비용','통일 편익']]
])
units=[]
for group,u in enumerate(topics,1):
 sections=[];pitfalls=[];words=[]
 for t in u['topics']:
  source=f'EBSi 이론 자료 {t[1]}쪽' if t[1]!='보완' else 'EBSi 문제 자료의 학습 개념 보완'
  sections.append({'title':t[0],'body':t[2]+'\n\n선택지 판단 포인트: '+t[3]+'\n\n헷갈리지 않기: '+t[4],'source':source,'related':t[5]})
  pitfalls.append(t[4]);words.extend(t[6])
 words=list(dict.fromkeys(words))
 units.append({'id':u['id'],'group':group,'title':u['title'],'summary':f"{u['id']}강 핵심 개념을 읽고, 자료와 선택지에서 정답의 근거를 찾아보세요.",'keywords':words[:8],'highlights':{'people':['애덤 스미스','케인스','프리드먼','갈퉁','국제 연합'],'concept':words},'sections':sections,'timeline':[],'pitfalls':pitfalls,'sourcePages':list(range(int(u['pages'].split('~')[0]),int(u['pages'].split('~')[1])+1)),'audio':f'assets/social/audio/theory-{u["id"]:02}.mp3'})
(ROOT/'content/social-units.json').write_text(json.dumps(units,ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared 3 chapters with',sum(len(u['sections']) for u in units),'theory topics')
