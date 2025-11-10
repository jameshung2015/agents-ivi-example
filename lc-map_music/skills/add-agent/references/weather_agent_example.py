"""
天气 Agent - 负责天气查询和预报
这是一个示例 Agent，展示如何创建新的 Agent
"""
import logging
from langchain.agents import create_agent
from ..llm import llm
from ..tools import weather_query, weather_forecast

logger = logging.getLogger(__name__)

WEATHER_SYSTEM_PROMPT = (
    "你是 AgentWeather，一个专业的天气查询助理。\n\n"
    "工作流程:\n"
    "1. 理解用户想查询的地点和时间范围。\n"
    "2. 如果查询当前天气，调用 weather_query 工具。\n"
    "3. 如果查询未来天气预报，调用 weather_forecast 工具。\n"
    "4. 基于工具返回的数据，给出清晰的天气描述和建议。\n\n"
    "可用工具:\n"
    "- weather_query: 查询指定地点的当前天气\n"
    "- weather_forecast: 查询指定地点的未来天气预报\n\n"
    "注意: 给出建议时考虑温度、降水、风力等因素，提供实用的出行或穿衣建议。"
)

def create_weather_agent():
    """创建天气 Agent"""
    logger.info("创建天气 Agent...")
    
    tools = [weather_query, weather_forecast]
    logger.info(f"已加载 {len(tools)} 个工具: {[t.name for t in tools]}")
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=WEATHER_SYSTEM_PROMPT,
    )
    
    logger.info("天气 Agent 创建成功")
    return agent
