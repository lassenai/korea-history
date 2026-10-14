"""Real MP3 playback tests; local server on port 4173 required."""
from playwright.sync_api import sync_playwright
import hashlib,json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_audio import script
ROOT=Path(__file__).resolve().parents[1]
units=json.loads((ROOT/'content/units.json').read_text(encoding='utf-8'))
manifest=json.loads((ROOT/'assets/audio/manifest.json').read_text(encoding='utf-8'))
assert len(manifest)==20
for u,m in zip(units,manifest):
 assert u['id']==m['unit']
 assert hashlib.sha256(script(u).encode()).hexdigest()==m['textSha256']
 assert (ROOT/'assets/audio'/m['file']).stat().st_size==m['bytes']
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch();page=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
  page.goto('http://127.0.0.1:4173/#theory/1')
  page.locator('[data-speak-unit]').click()
  page.wait_for_function("document.querySelector('audio').currentTime>0.1")
  page.select_option('[data-audio-rate]','1.5')
  assert page.locator('audio').evaluate('(a)=>a.playbackRate')==1.5
  page.locator('audio').evaluate('(a)=>a.pause()')
  page.locator('[data-speak-unit]').click()
  page.wait_for_function("!document.querySelector('audio').paused")
  page.locator('[data-speech-stop]').click()
  assert page.locator('audio').evaluate('(a)=>a.paused && a.currentTime===0')
  page.locator('[data-speak-unit]').click();page.wait_for_function("!document.querySelector('audio').paused")
  page.evaluate("window.oldAudio=document.querySelector('audio');location.hash='theory/2'")
  page.wait_for_selector('audio[src*=theory-02]')
  assert page.evaluate('oldAudio.paused')
  assert page.evaluate('document.documentElement.scrollWidth')==390
  # Every generated file must decode to a meaningful duration.
  for i in range(1,21):
   duration=page.evaluate('''async (i)=>{const a=window.testAudio=new Audio('./assets/audio/theory-'+String(i).padStart(2,'0')+'.mp3');a.preload='metadata';return await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('metadata timeout '+i)),10000);a.onloadedmetadata=()=>{clearTimeout(timer);resolve(a.duration);};a.onerror=()=>{clearTimeout(timer);reject(Error('decode '+i));};a.load();});}''',i)
   assert 30<duration<1200,(engine,i,duration)
   print(engine,i,round(duration,1),flush=True)
  page.evaluate("location.hash='theory/3'");page.wait_for_selector('audio[src*=theory-03]');page.locator('audio').evaluate("a=>{a.src='./assets/audio/missing-audio-test.mp3';a.load();}");page.locator('[data-speak-unit]').click()
  page.wait_for_function("document.querySelector('audio').error!==null")
  assert page.locator('#speech-status').inner_text()
  b.close();print('PASS',engine,'20 decoded MP3 files; playback, pause, resume, speed, reset, navigation, network error')
