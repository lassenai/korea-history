import asyncio,json,hashlib,sys
from pathlib import Path
import edge_tts
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
async def main():
 units=json.loads((ROOT/'content/social-units.json').read_text(encoding='utf-8'));manifest=[]
 for u in units:
  text='\n\n'.join([u['title']+'.']+[s['title']+'.\n'+s['body'] for s in u['sections']])
  dest=ROOT/u['audio'];dest.parent.mkdir(parents=True,exist_ok=True)
  temp=dest.with_suffix('.tmp')
  await edge_tts.Communicate(text,'ko-KR-SunHiNeural',rate='-5%').save(str(temp))
  assert temp.stat().st_size>10000
  temp.replace(dest)
  manifest.append({'unit':u['id'],'file':u['audio'],'voice':'ko-KR-SunHiNeural','textSha256':hashlib.sha256(text.encode()).hexdigest(),'bytes':dest.stat().st_size})
  print('Generated chapter',u['id'],flush=True)
 (ROOT/'assets/social/audio/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
asyncio.run(main())
