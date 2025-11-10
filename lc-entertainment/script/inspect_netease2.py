"""
Inspect NetEase search page by typing in search box and examining the results DOM.
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
    """Navigate to NetEase search, type query, and inspect DOM."""
    try:
        browser = pychrome.Browser(url="http://localhost:9222")
        tab = browser.new_tab()
        tab.start()
        time.sleep(1)
        
        # Navigate to NetEase home
        print("Navigating to NetEase home...")
        tab.call_method("Page.navigate", url="https://music.163.com/")
        time.sleep(5)
        
        # Try to find and fill search input
        print("Typing in search box...")
        fill_script = """
        (function(){
            const input = document.getElementById('m-search-input') || 
                         document.querySelector('input[type="text"].srch') ||
                         document.querySelector('input[placeholder*="搜索"]');
            if (input) {
                input.focus();
                input.value = '周杰伦';
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                return { found: true, selector: 'found' };
            }
            return { found: false };
        })();
        """
        res = tab.call_method("Runtime.evaluate", expression=fill_script, returnByValue=True)
        print(f"Search input result: {res}")
        
        # Press Enter
        time.sleep(1)
        print("Pressing Enter...")
        tab.call_method("Input.dispatchKeyEvent", type="keyDown", key="Enter")
        tab.call_method("Input.dispatchKeyEvent", type="keyUp", key="Enter")
        
        # Wait for results
        time.sleep(5)
        
        # Now inspect the results in iframe
        print("\n=== Inspecting search results ===")
        inspect_script = """
        (function(){
            const iframe = document.getElementById('g_iframe');
            if (!iframe) return { error: 'no iframe' };
            
            try {
                const doc = iframe.contentDocument || iframe.contentWindow.document;
                
                // Find first song list item
                let items = doc.querySelectorAll('.srchsongst li');
                if (!items.length) items = doc.querySelectorAll('.m-table tbody tr');
                if (!items.length) items = doc.querySelectorAll('.f-cb');
                
                console.log('Found items:', items.length);
                
                if (items.length > 0) {
                    const first = items[0];
                    const html = first.outerHTML.substring(0, 2000);
                    const classes = first.className;
                    
                    // Find all clickable elements in first item
                    const buttons = first.querySelectorAll('a, button, span[onclick], div[onclick]');
                    const buttonInfo = [];
                    for (let i = 0; i < Math.min(5, buttons.length); i++) {
                        const btn = buttons[i];
                        buttonInfo.push({
                            tag: btn.tagName,
                            class: btn.className,
                            text: (btn.innerText || btn.textContent || '').substring(0, 30),
                            onclick: btn.onclick ? 'true' : 'false',
                            dataAction: btn.getAttribute('data-action')
                        });
                    }
                    
                    return {
                        itemCount: items.length,
                        firstItemHTML: html,
                        firstItemClass: classes,
                        buttons: buttonInfo
                    };
                }
                
                return { error: 'no items found', itemCount: 0 };
            } catch (e) {
                return { error: e.toString() };
            }
        })();
        """
        
        res = tab.call_method("Runtime.evaluate", expression=inspect_script, returnByValue=True)
        result = res.get('result', {}).get('value', {})
        
        print("\n=== Results Analysis ===")
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Items found: {result.get('itemCount', 0)}")
            print(f"First item class: {result.get('firstItemClass', '')}")
            print(f"\nFirst item HTML (first 2000 chars):")
            print(result.get('firstItemHTML', ''))
            print(f"\nButtons in first item:")
            for btn in result.get('buttons', []):
                print(f"  {btn['tag']}.{btn['class']} - text:'{btn['text']}' onclick:{btn['onclick']} data-action:{btn.get('dataAction')}")
        
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
