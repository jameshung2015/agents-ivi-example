import streamlit as st
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Now safe to import from app.backend
from app.backend.logging_config import setup_logging
from app.backend.agents import create_map_agent, create_music_agent

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Map & Music Agents", page_icon="🗺️")

if "map_agent" not in st.session_state:
    st.session_state["map_agent"] = create_map_agent()
if "music_agent" not in st.session_state:
    st.session_state["music_agent"] = create_music_agent()

st.title("Multi-Agent Chat: 地图 & 音乐")
agent_choice = st.sidebar.selectbox("选择Agent", ["地图Agent", "音乐Agent"], index=0)

# 音乐平台选择
music_platform = None
if agent_choice == "音乐Agent":
    music_platform = st.sidebar.selectbox(
        "选择音乐平台",
        ["QQ音乐", "网易云音乐"],
        index=0,
        help="选择要使用的音乐播放平台"
    )

chat_key = "chat_history"
if chat_key not in st.session_state:
    st.session_state[chat_key] = []

for role, content in st.session_state[chat_key]:
    with st.chat_message(role):
        st.write(content)

user_input = st.chat_input("请输入您的需求，例如: '查询上海东方明珠到外滩的驾车路线' 或 '播放 周杰伦 青花瓷'")
if user_input:
    # 根据选择的音乐平台调整查询
    original_input = user_input
    if agent_choice == "音乐Agent" and music_platform:
        if music_platform == "网易云音乐" and "网易" not in user_input:
            user_input = f"在网易云音乐上{user_input}"
        elif music_platform == "QQ音乐" and "QQ" not in user_input and "腾讯" not in user_input:
            user_input = f"在QQ音乐上{user_input}"

    logger.info(f"用户输入: {original_input}, 选择Agent: {agent_choice}, 音乐平台: {music_platform}")
    st.session_state[chat_key].append(("user", original_input))
    with st.chat_message("user"):
        st.write(original_input)
    
    if agent_choice == "地图Agent":
        agent = st.session_state["map_agent"]
    else:
        agent = st.session_state["music_agent"]
    
    with st.chat_message("assistant"):
        try:
            logger.info(f"调用 {agent_choice}...")
            # 新的 create_agent API 返回的图使用 messages 格式
            result = agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })
            logger.debug(f"Agent 响应: {result}")
            
            # 获取最后一条助手消息
            messages = result.get("messages", [])
            if messages:
                last_message = messages[-1]
                output = last_message.content if hasattr(last_message, 'content') else str(last_message)
            else:
                output = "(无输出)"
            
            logger.info(f"{agent_choice} 执行成功")
        except Exception as e:
            logger.error(f"{agent_choice} 执行失败: {e}", exc_info=True)
            import traceback
            output = f"错误: {e}\n{traceback.format_exc()}"
        st.write(output)
    st.session_state[chat_key].append(("assistant", output))
