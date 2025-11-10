import logging
from langchain.tools import tool
import requests
from ..config import AMAP_API_KEY

logger = logging.getLogger(__name__)

@tool
def amap_route_planner(origin: str, destination: str, mode: str = "driving") -> str:
    """
    使用高德路径规划API，提供起终点经纬度和出行方式，返回距离与预计耗时。
    
    Args:
        origin: 起点，经纬度 'lng,lat'
        destination: 终点，经纬度 'lng,lat'
        mode: 模式: driving|walking|transit
    
    Returns:
        路径规划结果字符串
    """
    logger.info(f"路径规划: origin={origin}, destination={destination}, mode={mode}")
    
    if not AMAP_API_KEY:
        logger.error("未配置 AMAP_API_KEY")
        return "错误: 未配置AMAP_API_KEY"
    
    if mode not in {"driving", "walking"}:  # transit需要更复杂参数，这里先限制
        logger.warning(f"不支持的模式 {mode}，使用 driving")
        mode = "driving"
    
    if mode == "driving":
        url = "https://restapi.amap.com/v5/direction/driving"
        params = {
            "key": AMAP_API_KEY,
            "origin": origin,
            "destination": destination,
        }
    else:  # walking
        url = "https://restapi.amap.com/v3/direction/walking"
        params = {
            "key": AMAP_API_KEY,
            "origin": origin,
            "destination": destination,
        }
    
    try:
        logger.debug(f"请求高德 API: {url}")
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        logger.debug(f"API 响应状态: {data.get('status')}")
    except Exception as e:
        logger.error(f"API 请求失败: {e}", exc_info=True)
        return f"请求失败: {e}"
    
    # Simplify response
    if mode == "driving":
        routes = data.get("route", {}).get("paths", [])
    else:
        routes = data.get("route", {}).get("paths", [])
    
    if not routes:
        logger.warning(f"未找到路径: origin={origin}, destination={destination}")
        return "未找到路径"
    
    path = routes[0]
    distance = path.get("distance")
    duration = path.get("duration")
    steps = path.get("steps", [])
    simplified_steps = [s.get("instruction") for s in steps if s.get("instruction")]
    
    result = {
        "mode": mode,
        "distance_m": distance,
        "duration_s": duration,
        "steps": simplified_steps[:10],
    }
    
    logger.info(f"找到路径: distance={distance}m, duration={duration}s")
    return str(result)

# 为了向后兼容，保留类定义
class AmapRoutePlannerTool:
    def __new__(cls):
        return amap_route_planner

    async def _arun(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("amap_route_planner 不支持异步")
