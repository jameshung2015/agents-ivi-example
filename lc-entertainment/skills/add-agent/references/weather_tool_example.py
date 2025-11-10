"""
示例工具 - 天气查询
展示如何创建符合规范的工具
"""
from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)

@tool
def weather_query(location: str) -> dict:
    """
    查询指定地点的当前天气情况。
    
    Args:
        location: 要查询天气的地点名称，如"北京"、"上海"等
        
    Returns:
        包含天气信息的字典，包括温度、天气状况、湿度、风力等
    """
    logger.info(f"执行天气查询: {location}")
    
    # 这里是示例实现，实际应该调用天气 API
    try:
        # 模拟 API 调用
        result = {
            "status": "success",
            "location": location,
            "temperature": "22°C",
            "condition": "晴",
            "humidity": "65%",
            "wind": "东南风3级"
        }
        logger.info(f"天气查询成功: {result}")
        return result
    except Exception as e:
        logger.error(f"天气查询失败: {str(e)}")
        return {
            "status": "error",
            "message": f"查询天气失败: {str(e)}"
        }

@tool
def weather_forecast(location: str, days: int = 3) -> dict:
    """
    查询指定地点的未来天气预报。
    
    Args:
        location: 要查询天气的地点名称
        days: 预报天数，默认3天，最多7天
        
    Returns:
        包含未来天气预报的字典
    """
    logger.info(f"执行天气预报查询: {location}, {days}天")
    
    try:
        # 模拟 API 调用
        forecast_data = []
        for i in range(min(days, 7)):
            forecast_data.append({
                "date": f"第{i+1}天",
                "temperature_high": f"{20+i}°C",
                "temperature_low": f"{15+i}°C",
                "condition": "多云转晴"
            })
        
        result = {
            "status": "success",
            "location": location,
            "forecast": forecast_data
        }
        logger.info(f"天气预报查询成功")
        return result
    except Exception as e:
        logger.error(f"天气预报查询失败: {str(e)}")
        return {
            "status": "error",
            "message": f"查询天气预报失败: {str(e)}"
        }
