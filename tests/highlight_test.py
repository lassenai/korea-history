from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch();page=b.new_page(viewport={'width':390,'height':844});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  for i in range(1,21):
   page.goto('http://127.0.0.1:4173/#theory/'+str(i));page.wait_for_function('(i)=>document.querySelector(".theory-body h1")?.textContent===HISTORY_DATA.units[i-1].title',arg=i)
   assert page.locator('mark.key-concept').count()>0,(engine,i)
   assert page.locator('mark.key-date').count()>0,(engine,i)
   result=page.evaluate('''i=>{const u=HISTORY_DATA.units[i-1];return u.sections.every(s=>Array.from(document.querySelectorAll('.theory-body>section')).some(el=>el.querySelector('h2')?.textContent===s.title&&el.querySelector('p')?.textContent===s.body));}''',i)
   assert result,(engine,i,'text altered')
  page.goto('http://127.0.0.1:4173/#theory/12');page.wait_for_selector('mark.key-people');page.locator('[data-speak-unit]').click();page.wait_for_function('document.querySelector("audio").currentTime>0.1');page.locator('[data-highlights]').click();assert page.locator('.highlights-off').count()==1;assert page.locator('audio').evaluate('(a)=>!a.paused')
  page.reload();page.wait_for_selector('.highlights-off');page.locator('[data-highlights]').click();assert page.locator('.highlights-off').count()==0
  for w in [320,390,768,1440]:
   page.set_viewport_size({'width':w,'height':900});assert page.evaluate('document.documentElement.scrollWidth')<=w+1
  page.set_viewport_size({'width':390,'height':844});page.locator('.highlight-guide').scroll_into_view_if_needed();page.screenshot(path=f'.qa/highlight-{engine}.png')
  assert not errors,errors;b.close();print('PASS',engine,'20 units, preserved text, highlighting, persistence, uninterrupted audio, responsive')

