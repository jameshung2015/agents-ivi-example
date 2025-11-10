"""
地图 Agent - 负责 POI 搜索和路径规划
"""
import logging
from langchain.agents import create_agent
from ..llm import llm
from ..tools import amap_poi_search, amap_route_planner

logger = logging.getLogger(__name__)

MAP_SYSTEM_PROMPT = (
    "你是 AgentMap，一个专业的地图和行程规划助理。\n\n"
    "工作流程:\n"
    "1. 分析用户意图 (搜索POI还是规划路径)。\n"
    "2. 若需要地点经纬度，必须先调用 amap_poi_search。\n"
    "3. 获得经纬度后，如用户需要路径，调用 amap_route_planner。\n"
    "4. 最终基于工具返回数据与常识给出行程建议(里程/时长/附近推荐)。\n"
)

def create_map_agent():
    """创建地图 Agent"""
    logger.info("创建地图 Agent...")
    
    tools = [amap_poi_search, amap_route_planner]
    logger.info(f"已加载 {len(tools)} 个工具: {[t.name for t in tools]}")
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=MAP_SYSTEM_PROMPT,
    )
    
    logger.info("地图 Agent 创建成功")
    return agent
