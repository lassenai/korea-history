"""Generate static Korean neural narration. Run: pip install edge-tts; python scripts/build_audio.py.
No credentials are embedded or needed in the published site.
"""
import asyncio,hashlib,json
from pathlib import Path
import edge_tts
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'audio'
VOICE='ko-KR-SunHiNeural'
def script(u):
    return '\n\n'.join([u['title']+'.',*[s['title']+'.\n'+s['body'] for s in u['sections']]])
async def main():
    OUT.mkdir(exist_ok=True)
    units=json.loads((ROOT/'content/units.json').read_text(encoding='utf-8'))
    previous=json.loads((OUT/'manifest.json').read_text(encoding='utf-8')) if (OUT/'manifest.json').exists() else []
    known={m['unit']:m for m in previous}
    manifest=[]
    for u in units:
        text=script(u)
        filename=f"theory-{u['id']:02d}.mp3"
        dest=OUT/filename
        digest=hashlib.sha256(text.encode()).hexdigest()
        cached=known.get(u['id'],{})
        if not (dest.exists() and cached.get('textSha256')==digest and cached.get('voice')==VOICE and cached.get('bytes')==dest.stat().st_size):
            temp=dest.with_suffix('.tmp')
            await edge_tts.Communicate(text,VOICE,rate='-5%').save(str(temp))
            if temp.stat().st_size<10000:raise RuntimeError('Empty audio')
            temp.replace(dest)
        manifest.append({'unit':u['id'],'file':filename,'voice':VOICE,'rate':'-5%','textSha256':digest,'bytes':dest.stat().st_size})
        print(f"Generated {u['id']}/20",flush=True)
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':asyncio.run(main())
