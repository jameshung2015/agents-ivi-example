from app.backend.tools.amap_poi_search import AmapPoiSearchTool

# These tests won't hit real API without AMAP_API_KEY; they just ensure instantiation.

def test_poi_tool_instantiation():
    tool = AmapPoiSearchTool()
    assert tool.name == "amap_poi_search"
