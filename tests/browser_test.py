from pathlib import Path
from playwright.sync_api import sync_playwright
import functools, http.server, json, os, platform, shutil, threading
root=Path(__file__).resolve().parents[1]
# Serve the project over a real local HTTP server so relative links behave as on GitHub Pages.
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root))
http.server.SimpleHTTPRequestHandler.log_message=lambda *a:None
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/slides/'
results={'checks':[],'issues':[],'execution_mode':'real browser navigating '+base+'deck.html via local HTTP server','browser_platform':platform.platform()}
def check(n,condition,detail=None):
    results['checks'].append({'test':n,'pass':bool(condition),'detail':detail})
    if not condition:results['issues'].append(f'{n}: {detail}')
with sync_playwright() as p:
    # Cross-platform: Windows usually has Chrome or Edge; Linux may use /usr/bin/chromium.
    attempts=[]
    custom=os.environ.get('CHROME_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
    launch_options=[{'headless':True}]
    if custom:
        launch_options.append({'headless':True,'executable_path':custom, 'args':['--no-sandbox'] if os.name!='nt' else []})
    launch_options+= [{'headless':True,'channel':'chrome'},{'headless':True,'channel':'msedge'}]
    browser=None
    for opts in launch_options:
        try:
            browser=p.chromium.launch(**opts)
            results['browser']=f"{opts.get('channel') or opts.get('executable_path') or 'playwright-chromium'} {browser.version}"
            break
        except Exception as exc:
            attempts.append(str(exc)[:240])
    if browser is None:
        raise RuntimeError('Cannot launch Chromium. Run `python -m playwright install chromium`, or set CHROME_PATH to your browser executable. Attempts: ' + str(attempts))
    for label, viewport in [('desktop',{'width':1440,'height':900}),('mobile',{'width':390,'height':844})]:
        pg=browser.new_page(viewport=viewport)
        errors=[]
        pg.on('pageerror',lambda e:errors.append(str(e)))
        pg.goto(base+'deck.html',wait_until='load')
        check(label+' initial title','第四面鏡' in pg.locator('body').inner_text())
        check(label+' pages',pg.locator('#counter').inner_text().strip()=='01 / 12')
        if label=='desktop':pg.screenshot(path=str(root/'tests'/'screenshot_cover.png'),full_page=True)
        pg.locator('[data-go="1"]').click()
        pg.locator('[data-reaction="worry"]').focus()
        pg.keyboard.press('Enter')
        check(label+' keyboard Enter selects reaction',pg.locator('[data-reaction="worry"]').get_attribute('aria-pressed')=='true')
        check(label+' reaction persists','他們是不是不喜歡我的報告' in pg.locator('#stage').inner_text())
        pg.locator('#next').click() # 3
        pg.locator('#next').click() # 4
        pg.locator('#next').click() # 5
        check(label+' self3 reflecting choice','他們是不是不喜歡我的報告' in pg.locator('#stage').inner_text())
        if label=='desktop':pg.screenshot(path=str(root/'tests'/'screenshot_self3.png'),full_page=True)
        pg.locator('#next').click() # 6
        pg.locator('[data-action="accuse"]').click()
        pg.locator('[data-go="6"]').click()
        check(label+' branch story','直接質問' in pg.locator('#stage').inner_text())
        pg.locator('[data-go="7"]').click() # 8
        pg.locator('[data-explore="ask"]').click() # 7
        check(label+' alternate route','詢問意見' in pg.locator('#stage').inner_text())
        pg.locator('[data-go="7"]').click() # 8
        pg.locator('#next').click() #9
        pg.locator('[data-quiz="c"]').click()
        check(label+' quiz correct','正確' in pg.locator('#stage').inner_text())
        pg.locator('#next').click() #10
        pg.locator('[data-thought="question"]').click()
        pg.locator('#next').click() #11
        pg.locator('[data-aggregate="識"]').click()
        check(label+' buddhist aggregate','識知依條件' in pg.locator('#stage').inner_text())
        if label=='desktop':pg.screenshot(path=str(root/'tests'/'screenshot_anatta.png'),full_page=True)
        pg.locator('#next').click() #12
        check(label+' final reflection','不必預設固定的我' in pg.locator('#stage').inner_text())
        if label=='desktop':pg.screenshot(path=str(root/'tests'/'screenshot_final.png'),full_page=True)
        pg.locator('#sourcesButton').click()
        check(label+' source drawer',pg.locator('#drawer').get_attribute('aria-hidden')=='false' and pg.locator('#sourceList a').count()>=2)
        pg.keyboard.press('Escape')
        check(label+' Escape closes drawer',pg.locator('#drawer').get_attribute('aria-hidden')=='true')
        pg.locator('[data-restart]').click()
        check(label+' restart clears',pg.locator('#counter').inner_text().strip()=='01 / 12')
        overflow=pg.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
        check(label+' no horizontal overflow',not overflow,{'scrollWidth':pg.evaluate('document.documentElement.scrollWidth'),'innerWidth':viewport['width']})
        check(label+' no JS errors',not errors,errors)
        pg.close()
    wiki=browser.new_page(viewport={'width':1280,'height':850})
    wiki.goto(base+'wiki.html',wait_until='load')
    check('wiki pages',wiki.locator('.wiki-page').count()>=15,wiki.locator('.wiki-page').count())
    wiki.locator('#filter').fill('後設知覺')
    check('wiki search',wiki.locator('.wiki-page:not(.hidden)').count()>=1)
    wiki.screenshot(path=str(root/'tests'/'screenshot_wiki.png'),full_page=False)
    wiki.close()
    link=browser.new_page()
    link.goto(base+'deck.html',wait_until='load')
    with link.context.expect_page() as popup_info:  # the link opens in a new tab (target=_blank)
        link.locator('a[href="wiki.html"]:visible').first.click()
    popup=popup_info.value
    popup.wait_for_load_state('load')
    check('deck -> wiki relative link',popup.url.endswith('/slides/wiki.html') and popup.locator('.wiki-page').count()>=15,popup.url)
    popup.close()
    link.close()
    browser.close()

server.shutdown()
results['status']='PASS' if not results['issues'] else 'FAIL'
(root/'tests'/'browser_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
print('status',results['status'],'tests',len(results['checks']))
for x in results['issues']:print('FAIL',x)
