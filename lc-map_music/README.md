# Map & Music Multi-Agent (LangChain + Ollama + Streamlit + Chrome DevTools MCP)

## 概述

基于 LangChain 的多 Agent 示例：
- **AgentMap**: 负责高德地图 POI 搜索与路径规划
- **AgentMusic**: 使用 **Chrome DevTools MCP** 控制 QQ 音乐网页播放

LLM 通过 Litellm 访问本地 Ollama 部署的 `deepseek-v3.1:671b-cloud` 模型。

**新增特性**: 集成 Chrome DevTools MCP 提供更稳定的浏览器自动化和与 AI 编码工具（Claude、Cursor 等）的原生集成。

## 目录结构

```
lc-map_music/
  requirement.md                # 原始需求说明
  requirements.txt              # 依赖列表
  .env.example                  # 环境变量示例
  mcp-config.json              # Chrome DevTools MCP 配置
  run_app.py                    # Python 启动脚本
  README.md                     # 本文件
  app/
    backend/
      config.py                 # 配置管理
      llm.py                    # LLM 调用封装
      logging_config.py         # 日志配置
      tools/
        amap_poi_search.py      # 高德 POI 搜索工具
        amap_route_planner.py   # 高德路线规划工具
        qq_music_search.py      # QQ 音乐搜索工具
        qq_music_play.py        # QQ 音乐播放工具
        qq_music_cdp.py         # 基于 Chrome DevTools MCP 的工具
      agents/
        map_agent.py            # 地图 Agent
        music_agent.py          # 音乐 Agent
    frontend/
      app.py                    # Streamlit 前端入口
  doc/
    CDP_INTEGRATION.md          # MCP 集成详细指南
  tests/
    test_llm_connection.py      # LLM 连接测试
    test_map_tools.py           # 地图工具测试
    test_pychrome.py            # Chrome 自动化测试
  script/
    inspect_netease.py          # 网易云音乐检查脚本
    inspect_netease2.py         # 网易云音乐检查脚本 v2
    inspect_netease3.py         # 网易云音乐检查脚本 v3
    inspect_qq.py               # QQ 音乐检查脚本
  skills/
    (Agent 扩展技能)
```

## 环境准备

### 前置条件

1. **Python 3.9+** 和虚拟环境
2. **Ollama**: 本地运行 `deepseek-v3.1:671b-cloud` 模型
3. **高德 API Key**: 用于地图功能
4. **Node.js v20+** (可选，仅用于 Chrome DevTools MCP)

### 快速启动

```powershell
# 1. 创建虚拟环境
python -m venv .venv
.\.venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 复制环境变量文件
Copy-Item .env.example .env

# 4. 编辑 .env，填入你的高德 API Key
# 编辑器中打开 .env 文件，找到 AMAP_API_KEY 并设置值

# 5. 在另一个终端启动 Ollama（保持运行）
ollama run deepseek-v3.1:671b-cloud

# 6. 启动应用
python run_app.py
```

## 环境变量配置

在 `.env` 文件中配置（根据 `.env.example` 创建）：

| 变量 | 说明 | 必需 | 示例 |
|------|------|------|------|
| `AMAP_API_KEY` | 高德 Web 服务 Key | ✓ | `<your_amap_api_key>` |
| `OLLAMA_BASE_URL` | Ollama 服务地址 | ✗ | `http://localhost:11434` |
| `LLM_MODEL` | 使用的模型 | ✗ | `ollama/deepseek-v3.1:671b-cloud` |

### 获取高德 API Key

1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册/登录账户
3. 创建应用或使用已有应用
4. 创建 Web 服务 API Key（需要勾选"Web 端"）
5. 复制 Key 值粘贴到 `.env` 中

## 使用方式

### 基础使用（无需 MCP）

应用启动后会在浏览器打开 Streamlit 界面：

1. **地图功能**:
   - 在侧边栏选择"地图Agent"
   - 输入：`查询上海东方明珠到外滩的驾车路线`
   - Agent 会搜索位置并规划路径

2. **音乐功能**:
   - 在侧边栏选择"音乐Agent"  
   - 输入：`播放周杰伦的青花瓷`
   - Agent 会搜索并播放歌曲

### 高级使用（集成 Chrome DevTools MCP）

如果想通过 Claude Desktop、Cursor 等 AI 工具控制应用：

1. 安装 Node.js: https://nodejs.org/ (v20 或更新)
2. 参考 `doc/CDP_INTEGRATION.md` 完成 MCP 配置
3. 在 AI 工具配置中加入 Chrome DevTools MCP

详见 `doc/CDP_INTEGRATION.md`。

## Agent 介绍

### AgentMap - 地图和路线规划

**工具**:
- `amap_poi_search`: 搜索地点 POI，返回经纬度和地址
- `amap_route_planner`: 规划驾车或步行路线

**工作流**:
1. 理解用户意图（搜索地点或规划路线）
2. 调用 POI 搜索获取坐标
3. 根据需要调用路线规划
4. 基于结果提供建议（距离、时长、路线描述）

**示例输入**:
- "查询上海迪士尼乐园的位置"
- "从人民广场到东方明珠的自驾路线"

### AgentMusic - QQ 音乐播放（基于 CDP）

**工具**:
- `qq_music_search_cdp`: 在 QQ 音乐搜索歌曲
- `qq_music_play_cdp`: 播放搜索结果

**工作流**:
1. 理解用户要求播放的歌曲名
2. 调用搜索工具找到歌曲
3. 调用播放工具开始播放
4. 返回播放状态

**示例输入**:
- "播放周杰伦的青花瓷"
- "播放梦想家 周深"

## 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `streamlit: 无法识别` | 虚拟环境未激活或依赖未安装 | 激活虚拟环境并运行 `pip install -r requirements.txt` |
| "No module named 'app'" | Python 路径问题 | 使用 `python run_app.py` 启动应用 |
| 高德 API 返回 `INVALID_USER_KEY` | Key 不正确或未启用 | 检查高德平台的 Key 和应用状态 |
| Ollama 连接失败 | 服务未运行或端口错误 | 确认 Ollama 已启动：`ollama list` |
| QQ 音乐搜索无结果 | 页面选择器过期 | 参考 `doc/CDP_INTEGRATION.md` 调试 |

## 后续增强计划

- [ ] 增加公交路线（transit）支持
- [ ] 缓存 POI 搜索结果
- [ ] 添加日志和调试工具
- [ ] 集成性能分析（利用 CDP）
- [ ] 支持更多音乐平台
- [ ] 增加地图可视化

## 技术栈

| 组件 | 版本/框架 | 用途 |
|------|---------|------|
| LLM | LangChain | Agent 框架和工具管理 |
| 模型调用 | Litellm | 统一接口调用 Ollama |
| 推理引擎 | Ollama + deepseek-v3.1 | 本地 LLM 推理 |
| 前端 | Streamlit | Web 聊天界面 |
| 地图 API | 高德地图 Web API | POI 搜索和路线规划 |
| 浏览器自动化 | Chrome DevTools MCP | 音乐播放控制 |

## 相关文档

- 📖 [Chrome DevTools MCP 集成指南](./doc/CDP_INTEGRATION.md)
- 📋 [原始项目需求](./requirement.md)
- 🔧 [高德 API 文档](https://lbs.amap.com/api)
- 🌐 [LangChain 文档](https://python.langchain.com/)

## License

示例代码仅供学习与演示使用。

## 快速命令参考

```powershell
# 首次设置
.\setup.ps1

# 启动应用（从项目根目录）
python run_app.py

# 或从 lc-map_music 目录启动
cd .\lc-map_music
streamlit run app/frontend/app.py

# 启动 Ollama（另一个终端）
ollama run deepseek-v3.1:671b-cloud

# 运行测试
pytest

# 激活虚拟环境
.\.venv\Scripts\activate

# 安装新依赖
pip install <package_name>
```

## 支持与反馈

如有问题或建议，欢迎提交 Issue 或 Pull Request。
