"""
Multi-platform music tools using direct Chrome DevTools Protocol.

This module provides tools to control multiple music platforms (QQ Music, NetEase Music) via direct CDP connection.
"""

import logging
import time
import json
from langchain.tools import tool
import pychrome
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import urllib.parse

logger = logging.getLogger(__name__)

# Music platform URLs
MUSIC_PLATFORMS = {
    "qq": "https://y.qq.com/",
    "netease": "https://music.163.com/"
}

class MusicPlatformController(ABC):
    """Abstract base class for music platform controllers"""

    def __init__(self, platform_name: str, base_url: str):
        self.platform_name = platform_name
        self.base_url = base_url
        self.browser = None
        self.tab = None

    def start_browser(self):
        """Start Chrome browser with remote debugging"""
        try:
            import subprocess
            import os

            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            if not os.path.exists(chrome_path):
                chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

            if not os.path.exists(chrome_path):
                raise Exception("Chrome not found in standard locations")

            # Start Chrome with remote debugging
            cmd = [
                chrome_path,
                "--remote-debugging-port=9222",
                "--user-data-dir=C:\\temp\\chrome_debug",
                "--no-first-run",
                "--no-default-browser-check"
            ]

            logger.info("Starting Chrome browser...")
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Wait for Chrome to start
            time.sleep(3)

            # Connect to Chrome
            self.browser = pychrome.Browser(url="http://localhost:9222")
            self.tab = self.browser.new_tab()

            logger.info("Chrome browser started and connected")
            return True

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False

    def wait_for_ready(self, timeout: int = 10) -> bool:
        """Wait until document.readyState becomes 'interactive' or 'complete'."""
        try:
            start = time.time()
            while time.time() - start < timeout:
                try:
                    res = self.tab.call_method("Runtime.evaluate", expression="document.readyState", returnByValue=True)
                    state = res.get('result', {}).get('value')
                    if state in ("interactive", "complete"):
                        return True
                except Exception:
                    # sometimes Runtime isn't ready yet
                    pass
                time.sleep(0.4)
        except Exception as e:
            logger.debug(f"wait_for_ready error: {e}")
        return False

    def wait_for_iframe_content(self, selector: str, timeout: int = 12) -> bool:
        """Wait until the iframe (#g_iframe) or top-level document contains elements matching selector."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                check = f"""
                (function(){{
                    const iframe = document.getElementById('g_iframe');
                    try{{
                        const doc = iframe ? (iframe.contentDocument || iframe.contentWindow.document) : document;
                        return doc.querySelectorAll('{selector}').length>0;
                    }}catch(e){{
                        return false;
                    }}
                }})();
                """
                res = self.tab.call_method("Runtime.evaluate", expression=check, returnByValue=True)
                val = res.get('result', {}).get('value')
                if val:
                    return True
            except Exception:
                pass
            time.sleep(0.6)
        return False

    def navigate_url(self, url: str, timeout: int = 10) -> bool:
        """Navigate to a URL and wait until page is ready."""
        try:
            # ensure tab started
            try:
                self.tab.start()
            except Exception:
                # already started or cannot start; ignore
                pass

            self.tab.call_method("Page.navigate", url=url)
            # wait for ready state
            self.wait_for_ready(timeout=timeout)
            # small extra wait for dynamic content
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"navigate_url failed: {e}")
            return False

    def navigate_to_platform(self):
        """Navigate to music platform website"""
        try:
            return self.navigate_url(self.base_url, timeout=12)
        except Exception as e:
            logger.error(f"Failed to navigate to {self.platform_name}: {e}")
            return False

    @abstractmethod
    def search_song(self, song_name: str) -> Optional[Dict[str, Any]]:
        """Search for a song - platform specific implementation"""
        pass

    @abstractmethod
    def play_song(self, song_info: Dict[str, Any]) -> str:
        """Play the found song - platform specific implementation"""
        pass

    def close(self):
        """Close browser"""
        try:
            if self.tab:
                self.tab.stop()
            if self.browser:
                self.browser.close()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

class QQMusicController(MusicPlatformController):
    """QQ Music browser controller"""

    def __init__(self):
        super().__init__("QQ Music", MUSIC_PLATFORMS["qq"])

    def search_song(self, song_name: str) -> Optional[Dict[str, Any]]:
        """Search for a song on QQ Music"""
        try:
            # Use QQ Music search URL to avoid interacting with dynamic inputs
            query = urllib.parse.quote_plus(song_name)
            # QQ search URL pattern (site may change; this is current observed pattern)
            search_url = f"https://y.qq.com/n/ryqq/search?w={query}&t=song&remoteplace=txt.yqq.top"
            logger.debug(f"Navigating to QQ search url: {search_url}")
            if not self.navigate_url(search_url, timeout=12):
                logger.error("Failed to load QQ search page")
                return None

            # Wait a bit for results to render
            time.sleep(1.5)

            # Try to extract first song title from DOM
            result = self.tab.call_method("Runtime.evaluate", expression="""
                (function(){
                    const songs = document.querySelectorAll('.songlist__item, .song_item, .song-list-item, [data-songid]');
                    if (songs.length>0){
                        const s = songs[0];
                        // attempt to pick a text node
                        return {title: s.innerText || s.textContent || s.outerHTML.substring(0,200)};
                    }
                    // fallback selectors
                    const list = document.querySelectorAll('.songlist__item__name, .songlist__songname');
                    if (list.length>0) return {title: list[0].innerText || list[0].textContent};
                    return null;
                })();
            """, returnByValue=True)

            song_info = result.get('result', {}).get('value') if result else None
            if song_info:
                logger.info(f"Found song: {song_info.get('title')}")
                return {"title": song_info.get('title')}
            else:
                logger.warning("No songs found on QQ")
                return None

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return None

    def play_song(self, song_info: Dict[str, Any]) -> str:
        """Play the found song by clicking the play button in the song item"""
        try:
            # Click the play button (播放) within the first song item
            # QQ structure: .songlist__item > .songlist__songname > .mod_list_menu > .list_menu__item.list_menu__play
            click_res = self.tab.call_method("Runtime.evaluate", expression="""
                (function(){
                    // Find the first song item and click its play button
                    const items = document.querySelectorAll('.songlist__item');
                    if (items && items.length > 0) {
                        const first = items[0];
                        // Find the play button within this item
                        const playBtn = first.querySelector('.list_menu__item.list_menu__play');
                        if (playBtn) {
                            try { 
                                playBtn.click(); 
                                return {clicked: true}; 
                            } catch(e) {
                                return {clicked: false, err: e.toString()};
                            }
                        }
                    }
                    return {clicked: false};
                })();
            """, returnByValue=True)

            clicked = click_res.get('result', {}).get('value', {}).get('clicked') if click_res else False
            if clicked:
                logger.info("Clicked play button on QQ")
                return "歌曲开始播放"
            else:
                logger.warning("Play button not found or not clickable on QQ")
                return "找到歌曲但无法播放"

        except Exception as e:
            logger.error(f"Play failed: {e}")
            return f"播放失败: {e}"

class NetEaseMusicController(MusicPlatformController):
    """NetEase Music browser controller"""

    def __init__(self):
        super().__init__("NetEase Music", MUSIC_PLATFORMS["netease"])

    def search_song(self, song_name: str) -> Optional[Dict[str, Any]]:
        """Search for a song on NetEase Music"""
        try:
            # Use NetEase search URL (site uses hash routing)
            # Use percent-encoding (spaces -> %20) to match NetEase URL pattern
            query = urllib.parse.quote(song_name, safe='')
            # NetEase search URL pattern observed: https://music.163.com/#/search/m/?s=<query>
            search_url = f"https://music.163.com/#/search/m/?s={query}"
            logger.debug(f"Navigating to NetEase search url: {search_url}")
            if not self.navigate_url(search_url, timeout=12):
                logger.error("Failed to load NetEase search page")
                return None

            # Wait for results to render inside iframe
            # wait for common item selectors inside iframe (give a bit longer)
            if not self.wait_for_iframe_content('.srchsongst .item', timeout=12):
                logger.debug('No list items detected in iframe after wait')
                # still continue to try extracting fallback selectors

            # Extract title from results
            result = self.tab.call_method("Runtime.evaluate", expression="""
                (function(){
                    // NetEase renders results inside an iframe #g_iframe
                    const iframe = document.getElementById('g_iframe');
                    try{
                        const doc = iframe ? iframe.contentDocument || iframe.contentWindow.document : document;
                        // First song item is in .srchsongst > .item; song title is in .item > .td.w0 > .sn > .text > a > b
                        const items = doc.querySelectorAll('.srchsongst .item');
                        if (items && items.length>0) {
                            const first = items[0];
                            const titleElem = first.querySelector('.sn .text a b, .sn .text a');
                            if (titleElem) return {title: titleElem.innerText || titleElem.textContent};
                        }
                    }catch(e){}
                    return null;
                })();
            """, returnByValue=True)

            song_info = result.get('result', {}).get('value') if result else None
            if song_info:
                logger.info(f"Found song on NetEase: {song_info.get('title')}")
                return {"title": song_info.get('title')}
            else:
                logger.warning("No songs found on NetEase")
                return None

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return None

    def play_song(self, song_info: Dict[str, Any]) -> str:
        """Play the found song"""
        try:
            # NetEase song list renders inside #g_iframe.
            # DOM structure: .srchsongst > .item (song row) > .td > .hd > a.ply (play button)
            # where a.ply has data-res-action="play"
            script = '''(function(){
                const iframe = document.getElementById('g_iframe');
                const doc = iframe ? (iframe.contentDocument || iframe.contentWindow.document) : document;
                
                // Find first song item with play button
                const items = doc.querySelectorAll('.srchsongst .item');
                if (items && items.length > 0) {
                    const first = items[0];
                    const playBtn = first.querySelector('a.ply[data-res-action="play"]');
                    if (playBtn) {
                        try {
                            playBtn.click();
                            return { clicked: true };
                        } catch (e) {
                            return { clicked: false, err: e.toString() };
                        }
                    }
                }
                return { clicked: false };
            })();'''

            # wait for list to appear before attempting click
            self.wait_for_iframe_content('.srchsongst .item', timeout=12)
            click_res = self.tab.call_method("Runtime.evaluate", expression=script, returnByValue=True)
            clicked = click_res.get('result',{}).get('value',{}).get('clicked') if click_res else False
            if clicked:
                logger.info("Clicked play button on NetEase")
                time.sleep(1.2)
                return "歌曲开始播放"
            else:
                logger.error("Could not click on first NetEase search result")
                return "无法选择歌曲"

        except Exception as e:
            logger.error(f"Play failed: {e}")
            return f"播放失败: {e}"
            click_res = self.tab.call_method("Runtime.evaluate", expression=script, returnByValue=True)
            clicked = click_res.get('result',{}).get('value',{}).get('clicked') if click_res else False
            if clicked:
                logger.info("Clicked play button on NetEase")
                time.sleep(1.2)
                return "歌曲开始播放"
            else:
                logger.error("Could not click on first NetEase search result")
                return "无法选择歌曲"

        except Exception as e:
            logger.error(f"Play failed: {e}")
            return f"播放失败: {e}"

# Global controller instances
_controllers = {}

def get_controller(platform: str) -> MusicPlatformController:
    """Get or create music platform controller"""
    if platform not in _controllers:
        if platform == "qq":
            _controllers[platform] = QQMusicController()
        elif platform == "netease":
            _controllers[platform] = NetEaseMusicController()
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    return _controllers[platform]

@tool
def qq_music_search_cdp(song_name: str) -> str:
    """
    使用 Chrome DevTools 在QQ音乐网页搜索歌曲，并返回搜索结果。

    Args:
        song_name: 要搜索的歌曲或歌手名

    Returns:
        搜索结果信息
    """
    logger.info(f"开始搜索QQ音乐歌曲: {song_name}")

    controller = get_controller("qq")

    # Start browser if not started
    if not controller.browser:
        if not controller.start_browser():
            return "无法启动浏览器"

    # Navigate to QQ Music
    if not controller.navigate_to_platform():
        return "无法访问QQ音乐网站"

    # Search for song
    song_info = controller.search_song(song_name)

    if song_info:
        return f"找到歌曲: {song_info.get('title', '未知歌曲')}"
    else:
        return f"未找到歌曲: {song_name}"

@tool
def qq_music_play_cdp(song_name: str) -> str:
    """
    播放指定的QQ音乐歌曲。

    Args:
        song_name: 要播放的歌曲名

    Returns:
        播放结果
    """
    logger.info(f"开始播放QQ音乐歌曲: {song_name}")

    controller = get_controller("qq")

    # Start browser if not started
    if not controller.browser:
        if not controller.start_browser():
            return "无法启动浏览器"

    # Navigate to QQ Music if not already there
    if not controller.navigate_to_platform():
        return "无法访问QQ音乐网站"

    # Search and play
    song_info = controller.search_song(song_name)
    if song_info:
        result = controller.play_song(song_info)
        return f"播放结果: {result}"
    else:
        return f"未找到歌曲: {song_name}"

@tool
def netease_music_search_cdp(song_name: str) -> str:
    """
    使用 Chrome DevTools 在网易云音乐网页搜索歌曲，并返回搜索结果。

    Args:
        song_name: 要搜索的歌曲或歌手名

    Returns:
        搜索结果信息
    """
    logger.info(f"开始搜索网易云音乐歌曲: {song_name}")

    controller = get_controller("netease")

    # Start browser if not started
    if not controller.browser:
        if not controller.start_browser():
            return "无法启动浏览器"

    # Navigate to NetEase Music
    if not controller.navigate_to_platform():
        return "无法访问网易云音乐网站"

    # Search for song
    song_info = controller.search_song(song_name)

    if song_info:
        return f"找到歌曲: {song_info.get('title', '未知歌曲')}"
    else:
        return f"未找到歌曲: {song_name}"

@tool
def netease_music_play_cdp(song_name: str) -> str:
    """
    播放指定的网易云音乐歌曲。

    Args:
        song_name: 要播放的歌曲名

    Returns:
        播放结果
    """
    logger.info(f"开始播放网易云音乐歌曲: {song_name}")

    controller = get_controller("netease")

    # Start browser if not started
    if not controller.browser:
        if not controller.start_browser():
            return "无法启动浏览器"

    # Navigate to NetEase Music if not already there
    if not controller.navigate_to_platform():
        return "无法访问网易云音乐网站"

    # Search and play
    song_info = controller.search_song(song_name)
    if song_info:
        result = controller.play_song(song_info)
        return f"播放结果: {result}"
    else:
        return f"未找到歌曲: {song_name}"

# 为了向后兼容，保留类定义
class QQMusicSearchToolCDP:
    def __new__(cls):
        return qq_music_search_cdp

class QQMusicPlayToolCDP:
    def __new__(cls):
        return qq_music_play_cdp

class NetEaseMusicSearchToolCDP:
    def __new__(cls):
        return netease_music_search_cdp

class NetEaseMusicPlayToolCDP:
    def __new__(cls):
        return netease_music_play_cdp