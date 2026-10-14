"""All-choice regression suite, requires local server :4173."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data.js').read_text(encoding='utf-8').removeprefix('window.HISTORY_DATA = ').strip().removesuffix(';'))
qs=d['questions'];assert len(qs)==200
assert all(q['type']=='choice' and q['answer'] in '①②③④⑤' for q in qs)
converted=[q for q in qs if q.get('converted')];assert len(converted)==70
original=json.loads((ROOT/'content/ebs.json').read_text(encoding='utf-8'))
for q in qs:
 if q.get('converted'):
  assert len(q['options'])==len(set(q['options']))==5
  assert q['options']['①②③④⑤'.index(q['answer'])]==q['answerText']
 elif q['id'].startswith('ebs-'):
  old=next(x for x in original if x['id']==q['id']);assert q['answer']==old['answer']
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch();page=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:4173/#questions');page.wait_for_selector('.question-row')
  def nav(route):
   page.goto('http://127.0.0.1:4173/#'+route);page.wait_for_timeout(40)
  # Every new question has exactly five readable choices, works on mobile, and grades correctly.
  for q in converted:
   nav('q/'+q['id']);expect(page.locator('[data-choice]')).to_have_count(5)
   assert page.locator('[data-answer]').count()==0
   assert page.locator('.text-choices').inner_text()
   assert page.evaluate('document.documentElement.scrollWidth')<=391
   page.locator('[data-choice="'+q['answer']+'"]').click();page.locator('[data-submit]').click()
   expect(page.locator('#solution')).to_contain_text('정답입니다')
  # All original choice answers still grade correctly, including source image prompts.
  for q in [x for x in qs if not x.get('converted')]:
   nav('q/'+q['id']);page.locator('[data-choice="'+q['answer']+'"]').click();page.locator('[data-submit]').click();expect(page.locator('#solution')).to_contain_text('정답입니다')
  q=converted[0];nav('q/'+q['id']);page.locator('[data-retry]').click()
  wrong=next(c for c in '①②③④⑤' if c!=q['answer']);page.locator('[data-choice="'+wrong+'"]').click();page.locator('[data-submit]').click();expect(page.locator('#solution')).to_contain_text('다시 기억')
  page.locator('[data-bookmark]').click();nav('review');expect(page.locator('.question-row')).to_have_count(1)
  # Migrate old short/essay answers without losing original choices/bookmarks.
  legacy=page.evaluate("JSON.parse(localStorage.getItem('lumi.history.v1'))")
  legacy.pop('choiceRevision',None);legacy['answers']={'ebs-01-01':{'value':'④','correct':True},'ebs-06-01':{'value':'모던 보이, 모던 걸','correct':True}};legacy['drafts']={'ebs-06-01':'모던 보이, 모던 걸'};legacy['bookmarks']=['ebs-06-01']
  page.evaluate("x=>localStorage.setItem('lumi.history.v1',JSON.stringify(x))",legacy);page.reload();nav('theory/1')
  migrated=page.evaluate("JSON.parse(localStorage.getItem('lumi.history.v1'))")
  assert migrated['answers']['ebs-01-01']['correct'] and 'ebs-06-01' not in migrated['answers']
  assert migrated['legacyWritten']['answers']['ebs-06-01']['correct'] and migrated['bookmarks']==['ebs-06-01']
  nav('q/ebs-06-01');expect(page.locator('[data-submit]')).to_be_enabled()
  nav('mock');page.locator('[data-exam-start="1"]').click();page.wait_for_selector('[data-exam-submit]');page.locator('[data-choice="①"]').click()
  page.once('dialog',lambda dialog:dialog.accept());page.locator('[data-exam-submit]').click();page.wait_for_selector('.results-list')
  for width in [320,375,390,768,1440]:
   page.set_viewport_size({'width':width,'height':900})
   for route in ['questions','q/essay-08','q/blank-01','q/ebs-06-01','theory/1','review','mock']:
    nav(route);assert page.evaluate('document.documentElement.scrollWidth')<=width+1,(engine,width,route)
  page.set_viewport_size({'width':390,'height':844});nav('q/essay-08');page.screenshot(path=str(ROOT/'.qa'/f'{engine}-all-choice.png'),full_page=True)
  assert not errors,errors
  b.close();print('PASS',engine,'200 questions graded, 70 conversions, migration, mock, review, responsive widths',flush=True)
