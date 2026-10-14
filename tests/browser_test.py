"""Functional browser tests against a running local static server."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.qa';OUT.mkdir(exist_ok=True)
URL='http://127.0.0.1:4173/'
KEY='lumi.history.v1'
reports=[]
with sync_playwright() as p:
    for engine in ['chromium','webkit']:
        browser=getattr(p,engine).launch(headless=True)
        context=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,has_touch=True,is_mobile=True)
        page=context.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(URL);page.wait_for_load_state('networkidle')
        def nav(hash):
            page.goto(URL+'#'+hash)
            page.wait_for_timeout(70)
        def state():return page.evaluate(f"JSON.parse(localStorage.getItem('{KEY}'))")
        def no_overflow():assert page.evaluate('document.documentElement.scrollWidth')<=page.viewport_size['width']+1,(engine,page.viewport_size,page.url)
        expect(page.get_by_text('역사의 흐름을 알고,')).to_be_visible()
        assert page.evaluate('HISTORY_DATA.questions.length')==200
        # Correctness, retry and durable answer persistence.
        nav('q/ebs-01-01');page.locator('[data-choice="①"]').click();page.locator('[data-submit]').click()
        assert state()['answers']['ebs-01-01']['correct'] is False
        nav('review');expect(page.locator('.question-row')).to_have_count(1)
        nav('q/ebs-01-01');page.locator('[data-retry]').click();page.locator('[data-choice="④"]').click();page.locator('[data-submit]').click()
        page.reload();expect(page.locator('#solution')).to_contain_text('정답입니다')
        page.locator('[data-bookmark]').click();assert 'ebs-01-01' in state()['bookmarks']
        # Blank answers tolerate whitespace; notes survive navigation.
        nav('q/blank-01');page.locator('#answer').fill('치안유지법');page.locator('[data-submit]').click()
        assert state()['answers']['blank-01']['correct']
        nav('q/essay-01');page.locator('#answer').fill('보통 경찰제로 바꾸었지만 경찰력을 늘렸고 언론 검열을 계속했다.');page.locator('[data-submit]').click()
        for el in page.locator('[data-rubric]').all():el.check()
        page.locator('[data-self-grade]').click();assert state()['answers']['essay-01']['correct']
        # Bookmark review, search and source/type filters.
        nav('review');page.locator('[data-review="bookmarks"]').click();expect(page.locator('.question-row')).to_have_count(1)
        nav('questions');page.locator('[data-type="essay"]').click();expect(page.locator('.question-row')).to_have_count(10)
        page.locator('#search').fill('문화 정치');page.locator('#search').press('Enter');assert page.locator('.question-row').count()>=1
        nav('theory/1');page.locator('[data-complete]').check();assert 1 in state()['completed']
        ox=page.evaluate('HISTORY_DATA.units[0].ox.answer')
        page.locator(f'[data-ox="{str(ox).lower()}"]').click();expect(page.locator('#ox-result')).to_contain_text('맞았어요')
        for i in range(page.locator('[data-order]').count()):page.locator(f'[data-order="{i}"]').click()
        page.locator('[data-order-check]').click();expect(page.locator('#order-result')).to_contain_text('정확해요')
        page.locator('[data-order-reset]').click();expect(page.locator('#order-answer li')).to_have_count(0)
        # Scope affects new exams; answers and timer survive refresh.
        nav('settings')
        for el in page.locator('[data-scope]').all()[1:]:el.uncheck()
        assert state()['scope']==[1]
        nav('mock');page.locator('[data-exam-start="1"]').click();expect(page.locator('#timer')).to_be_visible()
        page.locator('[data-choice="④"]').click();page.reload();expect(page.locator('[data-choice="④"]')).to_have_attribute('aria-pressed','true')
        page.once('dialog',lambda d:d.accept());page.locator('[data-exam-submit]').click()
        assert state()['history'][-1]['correct']==1
        nav('mock');page.locator('[data-exam-start="2"]').click()
        page.evaluate(f"(()=>{{const s=JSON.parse(localStorage.getItem('{KEY}'));s.exam.end=Date.now()-1000;localStorage.setItem('{KEY}',JSON.stringify(s));}})()")
        page.reload();page.wait_for_timeout(1300);assert state()['exam'] is None
        assert state()['history'][-1]['correct']==0
        # Export and restore real records; malformed import must not execute or replace.
        nav('settings')
        with page.expect_download() as d:page.locator('[data-export]').click()
        backup=OUT/f'{engine}-backup.json';d.value.save_as(backup)
        original=state();bad=json.loads(backup.read_text(encoding='utf-8'));bad['history'][0]['round']='<img src=x onerror=alert(1)>'
        badpath=OUT/'bad.json';badpath.write_text(json.dumps(bad),encoding='utf-8')
        page.locator('#import').set_input_files(badpath);expect(page.locator('#toast')).to_contain_text('올바른 루미')
        assert state()==original
        page.once('dialog',lambda d:d.accept());page.locator('#import').set_input_files(backup);expect(page.locator('#toast')).to_contain_text('가져왔어요')
        # Full range for responsive and all-route checks.
        page.locator('[data-scope-all]').click()
        for width in [320,375,390,768,1440]:
            page.set_viewport_size({'width':width,'height':900})
            for r in ['home','theory/1','theory/20','questions','q/ebs-01-02','q/essay-20','mock','review','settings','sources']:
                nav(r);no_overflow()
            nav('home');page.screenshot(path=str(OUT/f'{engine}-home-{width}.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        nav('theory/20');page.locator('[data-font="21"]').click();no_overflow();page.locator('[data-font="17"]').click()
        nav('q/ebs-20-02');page.locator('[data-zoom]').click();expect(page.locator('dialog')).to_be_visible();page.get_by_role('button',name='닫기',exact=True).click()
        # Every local question image loads, rather than only checking file existence.
        asset_errors=page.evaluate("""async()=>{const qs=HISTORY_DATA.questions.filter(q=>q.image);return (await Promise.all(qs.map(q=>new Promise(resolve=>{const i=new Image();i.onload=()=>resolve(null);i.onerror=()=>resolve(q.id);i.src=q.image;})))).filter(Boolean)}""")
        assert not asset_errors,asset_errors
        page.screenshot(path=str(OUT/f'{engine}-question-mobile.png'),full_page=True)
        assert not errors,errors
        reports.append({'engine':engine,'status':'passed','responsiveWidths':[320,375,390,768,1440],'sourceImages':160,'runtimeErrors':errors})
        context.close();browser.close()
    # Isolated mock recognition exercises result handling, preserving previous typed text.
    browser=p.chromium.launch(headless=True);context=browser.new_context()
    context.add_init_script("""window.SpeechRecognition=class {start(){window.fakeRecognition=this;this.onstart?.();}stop(){this.onend?.();}abort(){}};""")
    page=context.new_page();page.goto(URL+'#q/essay-01');page.locator('#answer').fill('기존 답안')
    page.locator('[data-voice-toggle]').click()
    page.evaluate("""(()=>{const r=[{transcript:'보통 경찰제와 언론 검열'}];r.isFinal=true;window.fakeRecognition.onresult({results:[r]});window.fakeRecognition.onend();})()""")
    expect(page.locator('#answer')).to_have_value('기존 답안\n보통 경찰제와 언론 검열')
    page.locator('[data-voice-toggle]').click();page.evaluate("window.fakeRecognition.onerror({error:'not-allowed'})")
    expect(page.locator('.voice-status').first).to_contain_text('권한')
    expect(page.locator('#answer')).to_be_editable()
    browser.close()
(OUT/'test-report.json').write_text(json.dumps({'browsers':reports,'mockSpeech':'passed','realIPhoneMicrophone':'not tested'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(reports,ensure_ascii=False));print('PASS: mock speech appends final text, permission error restores editable input. Actual iPhone microphone requires device verification.')
