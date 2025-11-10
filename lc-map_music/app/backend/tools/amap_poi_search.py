import logging
from langchain.tools import tool
import requests
from ..config import AMAP_API_KEY

logger = logging.getLogger(__name__)

@tool
def amap_poi_search(keyword: str, city: str = None) -> str:
    """
    使用高德地点搜索 API，根据关键词（以及可选城市）返回匹配POI的名称、地址与经纬度。
    
    Args:
        keyword: POI关键字，例如 '东方明珠' 或 '星巴克'
        city: 城市名称，可选，例如 '上海'
    
    Returns:
        匹配POI的详细信息字符串
    """
    logger.info(f"POI 搜索: keyword={keyword}, city={city}")
    
    if not AMAP_API_KEY:
        logger.error("未配置 AMAP_API_KEY")
        return "错误: 未配置AMAP_API_KEY"
    
    params = {
        "keywords": keyword,
        "key": AMAP_API_KEY,
        "extensions": "base",
        "offset": 5,
        "page": 1,
    }
    if city:
        params["city"] = city
    
    url = "https://restapi.amap.com/v3/place/text"
    try:
        logger.debug(f"请求高德 API: {url}")
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        logger.debug(f"API 响应状态: {data.get('status')}")
    except Exception as e:
        logger.error(f"API 请求失败: {e}", exc_info=True)
        return f"请求失败: {e}"
    
    pois = data.get("pois", [])
    if not pois:
        logger.warning(f"未找到 POI: keyword={keyword}, city={city}")
        return "未找到结果"
    
    simplified = []
    for p in pois:
        simplified.append({
            "name": p.get("name"),
            "address": p.get("address"),
            "location": p.get("location"),  # 'lng,lat'
            "type": p.get("type")
        })
    
    logger.info(f"找到 {len(simplified)} 个 POI")
    return str(simplified)

# 为了向后兼容，保留类定义
class AmapPoiSearchTool:
    def __new__(cls):
        return amap_poi_search
