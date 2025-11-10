import pychrome
import time
import subprocess
import os

# Test pychrome API
try:
    # Start browser first
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(chrome_path):
        cmd = [chrome_path, "--remote-debugging-port=9222", "--user-data-dir=C:\\temp\\chrome_debug", "--no-first-run", "--no-default-browser-check"]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)

    print("Connecting to browser...")
    browser = pychrome.Browser(url="http://localhost:9222")
    tab = browser.new_tab()
    tab.start()
    time.sleep(1)

    # Set up event listener for page load
    def on_page_loaded(**kwargs):
        print("Page loaded!")

    tab.set_listener("Page.loadEventFired", on_page_loaded)

    # Test different API calls
    print("Testing Page.navigate...")
    tab.call_method("Page.navigate", url="https://www.google.com")
    print("Navigation called successfully")

    # Wait for page to load
    time.sleep(5)
    print("Waited for page load")

    # Test Runtime.evaluate
    print("Testing Runtime.evaluate...")
    result = tab.call_method("Runtime.evaluate", expression="document.title", returnByValue=True)
    print(f"Page title: {result}")

    tab.stop()
    browser.close()
    print("Test completed successfully")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()