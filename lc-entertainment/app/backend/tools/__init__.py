from .amap_poi_search import amap_poi_search
from .amap_route_planner import amap_route_planner
from .qq_music_cdp import (
    qq_music_search_cdp, qq_music_play_cdp,
    netease_music_search_cdp, netease_music_play_cdp
)

# 向后兼容的类实例
AmapPoiSearchTool = amap_poi_search
AmapRoutePlannerTool = amap_route_planner
QQMusicSearchToolCDP = qq_music_search_cdp
QQMusicPlayToolCDP = qq_music_play_cdp
NetEaseMusicSearchToolCDP = netease_music_search_cdp
NetEaseMusicPlayToolCDP = netease_music_play_cdp

__all__ = [
    "amap_poi_search",
    "amap_route_planner",
    "qq_music_search_cdp",
    "qq_music_play_cdp",
    "netease_music_search_cdp",
    "netease_music_play_cdp",
    "AmapPoiSearchTool",
    "AmapRoutePlannerTool",
    "QQMusicSearchToolCDP",
    "QQMusicPlayToolCDP",
    "NetEaseMusicSearchToolCDP",
    "NetEaseMusicPlayToolCDP",
]
