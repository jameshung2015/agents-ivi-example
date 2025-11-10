from typing import Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
except Exception:  # pragma: no cover
    webdriver = None

class QQMusicPlayInput(BaseModel):
    element_locator: str = Field(..., description="来自搜索工具的定位(href简化)")

class QQMusicPlayTool(BaseTool):
    name: str = "qq_music_play"
    description: str = "根据搜索返回的定位信息打开歌曲页面并尝试播放。"
    args_schema: Type[BaseModel] = QQMusicPlayInput

    def _run(self, element_locator: str) -> str:  # type: ignore
        if webdriver is None:
            return "错误: Selenium 未安装或不可用"
        try:
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            # 使用 webdriver-manager 自动管理 chromedriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(element_locator)
            time.sleep(3)
            # Attempt to click play button - selector may need refinement
            try:
                play_btn = driver.find_element(By.CSS_SELECTOR, 'i.play_btn__1uLQX')
                play_btn.click()
                status = "已点击播放"
            except Exception:
                status = "未找到播放按钮"
            driver.quit()
            return status
        except Exception as e:
            try:
                driver.quit()  # type: ignore
            except Exception:
                pass
            return f"播放失败: {e}"

    async def _arun(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("qq_music_play 不支持异步")
