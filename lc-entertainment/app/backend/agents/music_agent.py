"""
音乐 Agent - 负责多平台音乐搜索和播放控制 (QQ音乐、网易云音乐)
"""
import logging
import os
from langchain.agents import create_agent
from ..llm import llm
from ..tools import (
    qq_music_search_cdp, qq_music_play_cdp,
    netease_music_search_cdp, netease_music_play_cdp
)

logger = logging.getLogger(__name__)

MUSIC_SYSTEM_PROMPT = (
    "你是 AgentMusic，一个专业的多平台音乐播放助理。\n\n"
    "支持的音乐平台:\n"
    "- QQ音乐 (https://y.qq.com/)\n"
    "- 网易云音乐 (https://music.163.com/)\n\n"
    "流程:\n"
    "1. 理解用户给出的歌曲/歌手名和平台偏好。\n"
    "2. 根据用户需求选择合适的平台:\n"
    "   - 如果用户指定了平台，使用对应的工具\n"
    "   - 如果未指定，使用配置的默认平台\n"
    "3. 先调用对应平台的搜索工具获取定位信息。\n"
    "4. 然后调用对应平台的播放工具播放。\n"
    "5. 回复用户播放状态。\n\n"
    "工具说明:\n"
    "- qq_music_search_cdp: QQ音乐搜索\n"
    "- qq_music_play_cdp: QQ音乐播放\n"
    "- netease_music_search_cdp: 网易云音乐搜索\n"
    "- netease_music_play_cdp: 网易云音乐播放\n\n"
    "注意: 这些工具通过 Chrome DevTools Protocol 直接控制浏览器执行实际操作。"
)

def create_music_agent():
    """创建音乐 Agent"""
    logger.info("创建音乐 Agent...")

    # 从环境变量获取音乐平台配置，默认使用QQ音乐
    music_platform = os.getenv("MUSIC_PLATFORM", "qq").lower()
    
    if music_platform == "qq":
        tools = [qq_music_search_cdp, qq_music_play_cdp]
        platform_name = "QQ音乐"
    elif music_platform == "netease":
        tools = [netease_music_search_cdp, netease_music_play_cdp]
        platform_name = "网易云音乐"
    else:
        # 默认使用QQ音乐
        tools = [qq_music_search_cdp, qq_music_play_cdp]
        platform_name = "QQ音乐"
        logger.warning(f"未知的MUSIC_PLATFORM: {music_platform}，使用默认平台QQ音乐")
    
    logger.info(f"已配置音乐平台: {platform_name}")
    logger.info(f"已加载 {len(tools)} 个工具: {[t.name for t in tools]}")

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=MUSIC_SYSTEM_PROMPT,
    )

    logger.info("音乐 Agent 创建成功")
    return agent
