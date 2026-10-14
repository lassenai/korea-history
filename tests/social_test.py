"""Multi-subject browser regression, local server on 4173."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
questions=json.loads((ROOT/'content/social-questions.json').read_text(encoding='utf-8'))
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch();page=b.new_page(viewport={'width':390,'height':844});errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:4173/')
  expect(page.locator('.subject-switch a').first).to_have_text('통합사회2')
  expect(page.locator('h1')).to_contain_text('사회를 이해하고')
  assert 'subject=social' in page.url
  def nav(route):
   page.goto('http://127.0.0.1:4173/?subject=social#'+route)
  for q in questions:
   nav('q/'+q['id']);expect(page.locator('[data-choice]')).to_have_count(5)
   page.locator('.question-image').evaluate('(i)=>i.decode()')
   assert page.locator('.source-tag').inner_text()=='[EBSi 문제]'
   expect(page.locator('.tags').first).to_contain_text(str(q['examYear'])+'년')
   page.locator('[data-choice="'+q['answer']+'"]').click();page.locator('[data-submit]').click()
   expect(page.locator('#solution')).to_contain_text('정답입니다')
  nav('q/social-01');page.locator('[data-retry]').click();page.locator('[data-choice="①"]').click();page.locator('[data-submit]').click();page.locator('[data-bookmark]').click()
  nav('review');expect(page.locator('.question-row')).to_have_count(1)
  saved=page.evaluate('localStorage.getItem("lumi.social.v1")')
  page.locator('.subject-switch a').nth(1).click()
  expect(page.locator('h1')).to_contain_text('역사의 흐름')
  page.goto('http://127.0.0.1:4173/?subject=history#q/ebs-01-01')
  page.locator('[data-choice="①"]').click();page.locator('[data-submit]').click()
  history=page.evaluate('localStorage.getItem("lumi.history.v1")')
  page.locator('.subject-switch a').first.click()
  assert saved==page.evaluate('localStorage.getItem("lumi.social.v1")')
  for chapter in [3,4,5]:
   nav('theory/'+str(chapter));expect(page.locator('audio')).to_have_count(1)
   assert page.locator('mark.key-concept').count()>0
   page.locator('[data-speak-unit]').click();page.wait_for_function('document.querySelector("audio").currentTime>0.1')
   assert page.locator('audio').evaluate('(a)=>a.duration>120')
   page.locator('[data-audio-rate]').select_option('1.2');assert page.locator('audio').evaluate('(a)=>a.playbackRate')==1.2
   page.locator('[data-highlights]').click();assert page.locator('audio').evaluate('(a)=>!a.paused')
   page.locator('[data-highlights]').click()
   page.locator('[data-complete]').check()
  nav('mock');page.locator('[data-exam-start="1"]').click();expect(page.locator('.exam-grid button')).to_have_count(10)
  page.on('dialog',lambda d:d.accept());page.locator('[data-exam-submit]').click();expect(page.locator('h1')).to_contain_text('마쳤어요')
  assert history==page.evaluate('localStorage.getItem("lumi.history.v1")')
  for width in [320,390,768,1440]:
   page.set_viewport_size({'width':width,'height':900})
   for route in ['home','theory/4','questions','q/social-28','settings','sources']:
    nav(route);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(engine,width,route)
  nav('home');page.screenshot(path=str(ROOT/f'.qa/social-live-{engine}.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(ROOT/f'.qa/social-live-mobile-{engine}.png'),full_page=True)
  assert not errors,errors
  b.close();print('PASS',engine,'30 grading, audio, storage isolation, review, mocks, responsive',flush=True)
