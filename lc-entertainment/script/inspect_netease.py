"""
Inspect NetEase search page to find correct play button and list item selectors.
Navigates to the NetEase search URL and dumps DOM structure for debugging.
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
    
    if not os.path.exists(chrome_path):
        print("Chrome not found")
        return False
    
    cmd = [
        chrome_path,
        "--remote-debugging-port=9222",
        "--user-data-dir=C:\\temp\\chrome_debug_inspect",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    print("Starting Chrome...")
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    return True

def inspect_netease():
    """Navigate to NetEase search and inspect DOM."""
    try:
        browser = pychrome.Browser(url="http://localhost:9222")
        tab = browser.new_tab()
        tab.start()
        time.sleep(1)
        
        # Navigate to NetEase search for "周杰伦"
        search_url = "https://music.163.com/#/search/m/?s=%E5%91%A8%E6%9D%B0%E4%BC%A6"
        print(f"Navigating to: {search_url}")
        tab.call_method("Page.navigate", url=search_url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Poll for readyState
        start = time.time()
        while time.time() - start < 15:
            try:
                res = tab.call_method("Runtime.evaluate", expression="document.readyState", returnByValue=True)
                state = res.get('result', {}).get('value')
                if state in ("interactive", "complete"):
                    print(f"Page ready (state={state})")
                    break
            except:
                pass
            time.sleep(0.5)
        
        # Wait extra time for iframe to render
        time.sleep(3)
        
        # Dump iframe structure and look for list items
        dump_script = """
        (function(){
            const iframe = document.getElementById('g_iframe');
            console.log('iframe found:', !!iframe);
            
            if (iframe) {
                try {
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    console.log('iframe content accessible: true');
                    
                    // Find song list items
                    const items = doc.querySelectorAll('.srchsongst li, .srchsongst, .m-table tr, .f-cb');
                    console.log('Found items count:', items.length);
                    
                    if (items.length > 0) {
                        const first = items[0];
                        console.log('First item HTML (first 500 chars):', first.outerHTML.substring(0, 500));
                        console.log('First item classes:', first.className);
                        
                        // Look for play buttons/icons in first item
                        const playBtns = first.querySelectorAll('.ply, .u-btni, .icon-play, .btn, a, span');
                        console.log('Play-like elements in first item:', playBtns.length);
                        if (playBtns.length > 0) {
                            for (let i = 0; i < Math.min(3, playBtns.length); i++) {
                                const btn = playBtns[i];
                                console.log(`Button ${i}: tag=${btn.tagName}, class=${btn.className}, text=${btn.innerText?.substring(0, 50)}`);
                            }
                        }
                    }
                    
                    // Dump all elements with "play" or "播放" text
                    const allElems = doc.querySelectorAll('*');
                    let playCount = 0;
                    for (const elem of allElems) {
                        const text = elem.innerText || elem.textContent || '';
                        if (text.includes('播放') && playCount < 5) {
                            console.log(`Play text found in ${elem.tagName}.${elem.className}: "${text.substring(0, 50)}"`);
                            playCount++;
                        }
                    }
                } catch (e) {
                    console.log('Error accessing iframe:', e.toString());
                }
            }
            
            // Top-level search
            const topItems = document.querySelectorAll('.srchsongst li, .m-table tr');
            console.log('Top-level items:', topItems.length);
            
            return { iframe: !!iframe, itemsInIframe: items ? items.length : -1 };
        })();
        """
        
        res = tab.call_method("Runtime.evaluate", expression=dump_script, returnByValue=True)
        print("\n=== DOM Inspection Result ===")
        print(res)
        
        # Also dump a HTML snapshot of the iframe
        snapshot_script = """
        (function(){
            const iframe = document.getElementById('g_iframe');
            if (iframe) {
                try {
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    const body = doc.body.outerHTML;
                    return {
                        iframeHTML: body.substring(0, 3000),
                        bodyClass: doc.body.className
                    };
                } catch (e) {
                    return { error: e.toString() };
                }
            }
            return { error: 'no iframe' };
        })();
        """
        
        snap = tab.call_method("Runtime.evaluate", expression=snapshot_script, returnByValue=True)
        snap_val = snap.get('result', {}).get('value', {})
        
        if 'iframeHTML' in snap_val:
            print("\n=== Iframe Body HTML (first 3000 chars) ===")
            print(snap_val['iframeHTML'])
        elif 'error' in snap_val:
            print(f"\n=== Iframe Error ===\n{snap_val['error']}")
        
        print("\n=== Instructions ===")
        print("1. Look at the HTML to find the actual play button class/selector")
        print("2. Look for onclick handlers or data attributes")
        print("3. Update selectors in qq_music_cdp.py based on findings")
        
        tab.stop()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if start_chrome():
        inspect_netease()
    else:
        print("Failed to start Chrome")
