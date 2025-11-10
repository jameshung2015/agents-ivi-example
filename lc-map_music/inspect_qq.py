"""
Inspect QQ Music search page to find correct play button selector.
Navigate to QQ search results and dump DOM structure for the play button.
"""

import pychrome
import time
import subprocess
import os

def start_chrome():
    """Start Chrome with remote debugging."""
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    
    cmd = [
        chrome_path,
        "--remote-debugging-port=9222",
        "--user-data-dir=C:\\temp\\chrome_debug_qq",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    return True

def inspect_qq():
    """Navigate to QQ search and inspect the play button structure."""
    try:
        browser = pychrome.Browser(url="http://localhost:9222")
        tab = browser.new_tab()
        tab.start()
        time.sleep(1)
        
        # Navigate to QQ search for "晴天"
        url = "https://y.qq.com/n/ryqq/search?w=%E6%99%B4%E5%A4%A9&t=song&remoteplace=txt.yqq.top"
        print(f"Navigating to: {url}")
        tab.call_method("Page.navigate", url=url)
        time.sleep(3)
        
        # Wait for content to load by polling for search results
        for attempt in range(10):
            check_script = """
            (function(){
                // Check if search results are loaded
                const songList = document.querySelectorAll('.songlist__item, .song-item, .song, [data-songid], tr[data-id]');
                const playBtn = document.querySelector('.songlist__play-all, .play-all-btn, .btn-play');
                return {
                    hasResults: songList.length > 0,
                    itemCount: songList.length,
                    hasPlayBtn: playBtn != null
                };
            })();
            """
            res = tab.call_method("Runtime.evaluate", expression=check_script, returnByValue=True)
            status = res.get('result', {}).get('value', {})
            print(f"  Attempt {attempt + 1}: items={status.get('itemCount', 0)}, playBtn={status.get('hasPlayBtn', False)}")
            
            if status.get('hasResults') or status.get('hasPlayBtn'):
                print(f"Content loaded!")
                break
            time.sleep(1)
        
        # Inspect the page structure
        inspect_script = """
        (function(){
            // Look for play buttons and list items
            
            // Try various possible selectors for play button
            const playSelectors = [
                '.songlist__play-all',
                '.play-all-btn',
                'button.btn-play',
                '.songlist__item .songlist__action .icon-play',
                '.songlist__item .songlist__play',
                '.ply',
                'a[data-action="play"]',
                'button[data-action="play"]',
                '.btn-group .btn-play',
                '.player-icon-play'
            ];
            
            let playButtonInfo = null;
            for (const sel of playSelectors) {
                const el = document.querySelector(sel);
                if (el) {
                    playButtonInfo = {
                        selector: sel,
                        tag: el.tagName,
                        class: el.className,
                        text: (el.innerText || el.textContent || '').substring(0, 50),
                        id: el.id || 'N/A'
                    };
                    console.log("Found play button: " + sel);
                    break;
                }
            }
            
            // Find song list items
            let items = document.querySelectorAll('.songlist__item, .song-item, .song, [data-songid], tr[data-id]');
            
            let firstItemInfo = null;
            if (items.length > 0) {
                const first = items[0];
                const html = first.outerHTML.substring(0, 3000);
                
                // Find clickable elements in first item
                const buttons = first.querySelectorAll('a, button, div[data-id], [onclick], [role="button"]');
                const btns = [];
                for (let i = 0; i < Math.min(8, buttons.length); i++) {
                    const btn = buttons[i];
                    btns.push({
                        tag: btn.tagName,
                        class: btn.className,
                        text: (btn.innerText || btn.textContent || '').substring(0, 30),
                        title: btn.title || btn.getAttribute('aria-label') || btn.getAttribute('data-action') || '',
                        id: btn.id || ''
                    });
                }
                
                firstItemInfo = {
                    itemHTML: html,
                    buttons: btns
                };
            }
            
            // Also dump structure around song list
            const container = document.querySelector('.search_content, .songlist, .song-list-container, [class*="songlist"]');
            let containerHtml = '';
            if (container) {
                containerHtml = container.outerHTML.substring(0, 3000);
            }
            
            return {
                itemsFound: items.length,
                playButton: playButtonInfo,
                firstItem: firstItemInfo,
                containerHtml: containerHtml
            };
        })();
        """
        
        res = tab.call_method("Runtime.evaluate", expression=inspect_script, returnByValue=True)
        result = res.get('result', {}).get('value', {})
        
        print("\n=== QQ Music Page Analysis ===")
        print(f"Song items found: {result.get('itemsFound', 0)}")
        
        if result.get('playButton'):
            print(f"\nPlay button found:")
            pb = result['playButton']
            print(f"  Selector: {pb.get('selector')}")
            print(f"  Tag: {pb.get('tag')}")
            print(f"  Class: {pb.get('class')}")
            print(f"  Text: {pb.get('text')}")
            print(f"  ID: {pb.get('id')}")
        else:
            print("\nNo standard play button found, checking first item...")
        
        if result.get('firstItem'):
            fi = result['firstItem']
            print(f"\nFirst song item HTML (first 3000 chars):")
            print(fi.get('itemHTML', ''))
            
            if fi.get('buttons'):
                print(f"\n\nButtons/clickable elements in first item ({len(fi['buttons'])} found):")
                for i, btn in enumerate(fi['buttons']):
                    print(f"  [{i}] <{btn['tag']}.{btn['class']}> text='{btn['text']}' title='{btn.get('title')}' id='{btn.get('id')}'")
        
        if result.get('containerHtml'):
            print(f"\n=== Container HTML (first 3000 chars) ===")
            print(result.get('containerHtml', ''))
        
        tab.stop()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if start_chrome():
        inspect_qq()
    else:
        print("Failed to start Chrome")
