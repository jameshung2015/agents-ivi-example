"""
测试天气 Agent 和工具
这是一个示例测试文件，展示如何测试新创建的 Agent
"""
import logging
from app.backend.agents import create_weather_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_weather_agent():
    """测试天气 Agent 的各种查询"""
    logger.info("开始测试天气 Agent...")
    
    agent = create_weather_agent()
    
    # 测试查询列表
    queries = [
        "查询北京现在的天气",
        "上海未来三天的天气预报",
        "深圳今天适合出门吗",
    ]
    
    for query in queries:
        logger.info(f"\n{'='*60}")
        logger.info(f"查询: {query}")
        logger.info(f"{'='*60}")
        
        try:
            response = agent.invoke({"messages": [{"role": "user", "content": query}]})
            logger.info(f"回复: {response}")
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")

if __name__ == "__main__":
    test_weather_agent()
