"""
Navigate directly to a NetEase search results URL and inspect the song list structure.
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
        "--user-data-dir=C:\\temp\\chrome_debug_inspect",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    return True

def inspect_netease():
    """Navigate directly to search result and inspect."""
    try:
        browser = pychrome.Browser(url="http://localhost:9222")
        tab = browser.new_tab()
        tab.start()
        time.sleep(1)
        
        # Navigate to a known working search result page
        url = "https://music.163.com/#/search/m/?s=周杰伦"
        print(f"Navigating to: {url}")
        tab.call_method("Page.navigate", url=url)
        time.sleep(6)
        
        # Inspect the entire iframe document
        inspect_script = """
        (function(){
            const iframe = document.getElementById('g_iframe');
            if (!iframe) return { error: 'no iframe' };
            
            try {
                const doc = iframe.contentDocument || iframe.contentWindow.document;
                const body = doc.body;
                
                // Get all song list items (try various selectors)
                let items = doc.querySelectorAll('tr[data-id]');  // table row with song ID
                if (!items.length) items = doc.querySelectorAll('.srchsongst li');
                if (!items.length) items = doc.querySelectorAll('.m-table tbody tr');
                if (!items.length) {
                    // Get everything and look at structure
                    const allDivs = doc.querySelectorAll('div, tr, li');
                    const textContent = body.innerText.substring(0, 500);
                    return {
                        error: 'No standard selectors found',
                        bodyText: textContent,
                        totalElements: allDivs.length
                    };
                }
                
                console.log('Found song items:', items.length);
                
                // Analyze first item
                if (items.length > 0) {
                    const first = items[0];
                    const html = first.outerHTML.substring(0, 3000);
                    
                    // Find play button - look for common classes
                    const playSelectors = ['.ply', '.u-btni.play', '.btn-play', '.icon-play', 'a.play', '[onclick*="play"]'];
                    let foundPlay = null;
                    for (const sel of playSelectors) {
                        const el = first.querySelector(sel);
                        if (el) {
                            foundPlay = { selector: sel, text: el.innerText?.substring(0, 30) };
                            break;
                        }
                    }
                    
                    return {
                        itemCount: items.length,
                        firstItemTag: first.tagName,
                        firstItemClass: first.className,
                        firstItemId: first.id || first.getAttribute('data-id'),
                        firstItemHTML: html,
                        playButton: foundPlay,
                        innerText: first.innerText.substring(0, 200)
                    };
                }
                
                return { error: 'items array empty' };
            } catch (e) {
                return { error: e.toString() };
            }
        })();
        """
        
        res = tab.call_method("Runtime.evaluate", expression=inspect_script, returnByValue=True)
        result = res.get('result', {}).get('value', {})
        
        print("\n=== NetEase Song List Analysis ===")
        if 'error' in result:
            print(f"Error: {result['error']}")
            if 'bodyText' in result:
                print(f"Page text snippet:\n{result['bodyText']}")
        else:
            print(f"Items found: {result.get('itemCount', 0)}")
            print(f"First item tag: {result.get('firstItemTag')}")
            print(f"First item class: {result.get('firstItemClass')}")
            print(f"First item ID/data-id: {result.get('firstItemId')}")
            print(f"Play button: {result.get('playButton')}")
            print(f"Inner text preview: {result.get('innerText')}")
            print(f"\nFirst item HTML (first 3000 chars):")
            print(result.get('firstItemHTML', ''))
        
        # Also try to get the complete body HTML to see page structure
        print("\n=== Full Body Structure ===")
        body_script = """
        (function(){
            const iframe = document.getElementById('g_iframe');
            if (!iframe) return { error: 'no iframe' };
            try {
                const doc = iframe.contentDocument || iframe.contentWindow.document;
                return doc.body.outerHTML.substring(0, 5000);
            } catch (e) {
                return e.toString();
            }
        })();
        """
        
        body_res = tab.call_method("Runtime.evaluate", expression=body_script, returnByValue=True)
        body_html = body_res.get('result', {}).get('value', '')
        print(body_html)
        
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
