import streamlit as st
import sys
import logging
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Now safe to import from app.backend
from app.backend.logging_config import setup_logging
from app.backend.agents import get_supervisor_agent
from app.backend.observability import observability

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="智能多Agent系统", 
    page_icon="🤖",
    layout="wide"
)

# 初始化SupervisorAgent
if "supervisor" not in st.session_state:
    st.session_state["supervisor"] = get_supervisor_agent()
    logger.info("SupervisorAgent 已初始化")

# 侧边栏配置
with st.sidebar:
    st.title("🤖 系统配置")
    
    # 模式选择
    mode = st.radio(
        "运行模式",
        ["智能路由", "手动选择"],
        help="智能路由：系统自动选择Agent；手动选择：用户指定Agent"
    )
    
    # 手动选择Agent（仅在手动模式下显示）
    manual_agent = None
    if mode == "手动选择":
        manual_agent = st.selectbox(
            "选择Agent",
            ["map", "music", "general"],
            format_func=lambda x: {
                "map": "🗺️ 地图Agent",
                "music": "🎵 音乐Agent",
                "general": "💬 通用对话"
            }[x]
        )
    
    st.divider()
    
    # 系统统计信息
    st.subheader("📊 系统统计")
    
    supervisor = st.session_state["supervisor"]
    stats = supervisor.get_statistics()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("总任务数", stats["total_tasks"])
        st.metric("平均耗时", f"{stats['avg_execution_time']:.2f}s")
    with col2:
        st.metric("成功率", f"{stats['success_rate']*100:.1f}%")
    
    # Agent使用情况
    if stats["agent_usage"]:
        st.subheader("Agent使用分布")
        agent_df = pd.DataFrame([
            {"Agent": k, "次数": v} 
            for k, v in stats["agent_usage"].items()
        ])
        st.dataframe(agent_df, use_container_width=True)
    
    st.divider()
    
    # 可观测性控制
    st.subheader("🔍 可观测性")
    
    if st.button("查看执行历史"):
        st.session_state["show_history"] = True
    
    if st.button("导出追踪数据"):
        filepath = observability.export_to_file()
        st.success(f"数据已导出到: {filepath}")
    
    if st.button("清除历史记录"):
        supervisor.task_history.clear()
        st.success("历史记录已清除")
        st.rerun()

# 主界面
st.title("🤖 智能多Agent系统")
st.caption("基于 LangChain + DeepSeek 的多Agent协作平台")

# 显示当前模式
if mode == "智能路由":
    st.info("🎯 当前模式：智能路由 - 系统将自动分析您的需求并选择最合适的Agent")
else:
    agent_name = {
        "map": "🗺️ 地图Agent",
        "music": "🎵 音乐Agent",
        "general": "💬 通用对话"
    }[manual_agent]
    st.info(f"👆 当前模式：手动选择 - 使用 {agent_name}")

# 聊天历史
chat_key = "chat_history"
if chat_key not in st.session_state:
    st.session_state[chat_key] = []

# 显示聊天记录
for role, content, metadata in st.session_state[chat_key]:
    with st.chat_message(role):
        st.write(content)
        # 显示元数据
        if metadata and role == "assistant":
            with st.expander("📋 执行详情", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Agent类型", metadata.get("agent_type", "unknown"))
                with col2:
                    st.metric("执行时间", f"{metadata.get('execution_time', 0):.2f}s")
                with col3:
                    status = "✅ 成功" if metadata.get("success") else "❌ 失败"
                    st.metric("状态", status)

# 用户输入
user_input = st.chat_input("请输入您的需求...")

if user_input:
    logger.info(f"用户输入: {user_input}, 模式: {mode}")
    
    # 添加用户消息到历史
    st.session_state[chat_key].append(("user", user_input, None))
    
    # 显示用户消息
    with st.chat_message("user"):
        st.write(user_input)
    
    # 执行任务
    supervisor = st.session_state["supervisor"]
    
    with st.chat_message("assistant"):
        with st.spinner("正在处理..."):
            try:
                # 根据模式执行
                if mode == "智能路由":
                    result = supervisor.execute_task(user_input)
                else:
                    result = supervisor.execute_task(user_input, agent_type=manual_agent)
                
                # 显示结果
                st.write(result.content)
                
                # 显示执行详情
                with st.expander("📋 执行详情", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Agent类型", result.agent_type)
                    with col2:
                        st.metric("执行时间", f"{result.metadata.get('execution_time', 0):.2f}s")
                    with col3:
                        status = "✅ 成功" if result.success else "❌ 失败"
                        st.metric("状态", status)
                    
                    # 显示任务ID
                    st.code(f"Task ID: {result.metadata.get('task_id')}")
                
                # 添加到历史
                st.session_state[chat_key].append((
                    "assistant",
                    result.content,
                    {
                        "agent_type": result.agent_type,
                        "execution_time": result.metadata.get("execution_time", 0),
                        "success": result.success,
                        "task_id": result.metadata.get("task_id")
                    }
                ))
                
            except Exception as e:
                error_msg = f"执行失败: {str(e)}"
                logger.error(error_msg, exc_info=True)
                st.error(error_msg)
                st.session_state[chat_key].append(("assistant", error_msg, None))

# 显示执行历史（如果请求）
if st.session_state.get("show_history", False):
    st.divider()
    st.subheader("📜 执行历史")
    
    history = supervisor.get_task_history(limit=20)
    
    if history:
        # 创建表格显示
        history_data = []
        for record in reversed(history):  # 最新的在前
            history_data.append({
                "时间": record["timestamp"][:19],
                "Task ID": record["task_id"],
                "用户输入": record["user_input"][:30] + "..." if len(record["user_input"]) > 30 else record["user_input"],
                "Agent": record["agent_type"],
                "状态": "✅" if record["success"] else "❌",
                "耗时(s)": f"{record['execution_time']:.2f}"
            })
        
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True)
        
        # 关闭历史视图
        if st.button("关闭历史记录"):
            st.session_state["show_history"] = False
            st.rerun()
    else:
        st.info("暂无执行历史")

# 页脚
st.divider()
st.caption("💡 提示：可以询问地图导航、音乐播放或一般问题，系统会智能选择合适的Agent处理")
