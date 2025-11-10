from typing import Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import time

# Selenium imports are optional to allow tests without browser
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
except Exception:  # pragma: no cover - environment may not have selenium
    webdriver = None

QQ_MUSIC_URL = "https://y.qq.com/"

class QQMusicSearchInput(BaseModel):
    song_name: str = Field(..., description="要搜索的歌曲或歌手名")

class QQMusicSearchTool(BaseTool):
    name: str = "qq_music_search"
    description: str = "在QQ音乐网页搜索歌曲，返回第一个结果的内部定位信息(简化)。"
    args_schema: Type[BaseModel] = QQMusicSearchInput

    def _run(self, song_name: str) -> str:  # type: ignore
        if webdriver is None:
            return "错误: Selenium 未安装或不可用"
        try:
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            # 使用 webdriver-manager 自动管理 chromedriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(QQ_MUSIC_URL)
            time.sleep(2)
            search_box = driver.find_element(By.CSS_SELECTOR, 'input.search_input__3Z-Qx')
            search_box.clear()
            search_box.send_keys(song_name)
            search_box.send_keys(Keys.ENTER)
            time.sleep(3)
            # Simplified: grab first song title element
            first_title = driver.find_element(By.CSS_SELECTOR, 'a.songlist__item_title')
            song_title = first_title.text
            locator = first_title.get_attribute('href')  # use href as simplified locator
            driver.quit()
            return str({"locator": locator, "title": song_title})
        except Exception as e:
            try:
                driver.quit()  # type: ignore
            except Exception:
                pass
            return f"搜索失败: {e}"

    async def _arun(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("qq_music_search 不支持异步")
