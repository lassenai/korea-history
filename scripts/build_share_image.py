from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={'width':1200,'height':630},device_scale_factor=1)
    page.goto((root/'scripts/share-card.html').as_uri())
    page.evaluate('document.fonts.ready')
    page.locator('.lumi').evaluate('(img)=>img.decode()')
    page.screenshot(path=str(root/'assets/share-kakao-v1.jpg'),type='jpeg',quality=90)
    browser.close()
