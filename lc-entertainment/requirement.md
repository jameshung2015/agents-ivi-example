这是您请求的 **LangChain Agent 开发项目**的完整需求与方案，旨在利用 Litellm/Ollama (`deepseek-v3.1:671b-cloud`) 的推理能力和外部工具的集成。

请仔细审阅以下内容，包括技术选型、详细设计、以及关键实现步骤。

-----

## 📝 完整项目需求与方案（Review版）

### 🎯 项目目标

使用 LangChain 框架和本地 LLM（通过 Litellm 调用 Ollama 托管的 `deepseek-v3.1:671b-cloud`），开发一个多 Agent 驱动的 Web 聊天应用，实现地图搜索与音乐播放功能。

### ⚙️ 核心技术栈

| 模块 | 技术/组件 | 作用 |
| :--- | :--- | :--- |
| **LLM 框架** | **LangChain** (Python) | Agent 核心逻辑、ReAct 范式、Tool/Chain 管理。 |
| **模型调用** | **Litellm** (Python) | 统一接口调用 Ollama，作为 LangChain 的 LLM 后端。 |
| **LLM 模型** | **Ollama** + `deepseek-v3.1:671b-cloud` | 提供高性能的本地推理服务。 |
| **前端界面** | **Streamlit** (推荐) | 快速构建 Web Chat UI，支持 Agent 切换与交互。 |
| **地图工具** | Python 封装 + **高德 MCP API** | 实现 POI 搜索和路径规划。 |
| **音乐工具** | **Selenium** + **Chrome DevTools Protocol (CDP)** | 控制 QQ 音乐网页，进行搜索和播放。 |

-----

## 一、通用架构与配置

### 1.1 模型与 Litellm 配置

  * **Ollama 服务：** 确保 Ollama 运行在本地，并已拉取 `deepseek-v3.1:671b-cloud` 模型。
    ```bash
    ollama run deepseek-v3.1:671b-cloud
    ```
  * **Litellm 集成 (Python Backend)：** 使用 `ChatLiteLLM` 作为 LangChain 的 LLM 对象。
    ```python
    from langchain_community.chat_models import ChatLiteLLM

    LLM_MODEL = "ollama/deepseek-v3.1:671b-cloud"
    OLLAMA_BASE_URL = "http://localhost:11434" # Ollama 默认地址

    llm = ChatLiteLLM(
        model=LLM_MODEL,
        api_base=OLLAMA_BASE_URL,
        temperature=0.0 # 保持推理稳定性
    )
    ```

### 1.2 Web Chat UI (Streamlit)

  * **Agent 列表：** 在 Streamlit 侧边栏或主界面提供一个下拉菜单 (`st.selectbox`) 或按钮组，供用户选择 `AgentMap` 或 `AgentMusic`。
  * **Chat 交互：** 使用 `st.chat_message` 和 `st.chat_input` 构建标准聊天界面。
  * **路由逻辑：** 每次用户输入后，根据当前选中的 Agent 名称，将输入文本路由给对应的 Agent 实例 (`agentMap.invoke(user_input)`)。

-----

## 二、AgentMap：地图搜索与行程建议

### 2.1 需求分析

1.  **POI 搜索：** 根据用户需求（如“上海的东方明珠”），精确搜索 POI，获取其经纬度。
2.  **路径规划：** 根据起点/终点信息，规划驾车/公交/步行路径。
3.  **行程建议：** Agent 结合搜索结果和常识，提供综合建议（例如：游玩时长、附近餐厅）。

### 2.2 工具 (Tools) 设计

利用 **高德 Web 服务 API**（需要申请 Key）。建议复用已搜索到的 Python 开源库（如 `Tlntin/amap_api` 的逻辑）来简化 HTTP 请求和参数处理。

| Tool 名称 | LangChain 名称 | 功能描述 | 输入参数（LLM可见） |
| :--- | :--- | :--- | :--- |
| **POI 搜索** | `amap_poi_search` | 搜索 POI，返回名称、地址、经纬度。 | JSON 格式: `{"keyword": str, "city": str}` |
| **路径规划** | `amap_route_planner` | 根据经纬度和交通方式规划路线。 | JSON 格式: `{"origin": str(lng,lat), "destination": str(lng,lat), "mode": str}` |

### 2.3 AgentMap 核心 Prompt 设计

Prompt 应明确引导 Agent 的多步推理过程（ReAct 模式）：

```markdown
**你是 AgentMap，一个专业的地图和行程规划助理。**

**你的工作流程：**
1. **分析用户意图：** 确定用户是想搜索地点（POI）还是规划路线。
2. **使用工具：** * 如果需要**地点经纬度**，**必须**先使用 `amap_poi_search`。
    * 获得经纬度后，使用 `amap_route_planner` 进行路径规划。
3. **提供建议：** **最后**，基于工具返回的原始数据和你的常识，提供友好的**行程建议**（如总里程、预计时长、附近推荐）。

**可用工具：** {tools}
**思考过程和最终回复必须遵循 LangChain ReAct 格式。**
```

-----

## 三、AgentMusic：QQ 音乐播放控制

### 3.1 需求分析

1.  **控制能力：** 能够模拟用户在 QQ 音乐网页上的搜索和点击播放操作。
2.  **精确播放：** 搜索用户提供的歌曲名，并播放列表中最相似的一个（即第一个结果）。
3.  **技术要求：** 必须使用 **Selenium** 配合 **Chrome DevTools Protocol (CDP)**，以实现对浏览器更深层次的控制，避免常规 Selenium 可能遇到的播放器拦截问题。

### 3.2 工具 (Tools) 设计

| Tool 名称 | LangChain 名称 | 功能描述 | 输入参数（LLM可见） |
| :--- | :--- | :--- | :--- |
| **音乐搜索** | `qq_music_search` | 打开 QQ 音乐网页，搜索歌曲名，返回搜索结果第一条的**元素定位符**和**歌曲名**。 | 字符串: `song_name` |
| **音乐播放** | `qq_music_play` | 根据搜索工具返回的定位符，模拟点击播放按钮，开始播放音乐。 | 字符串: `element_locator` |

### 3.3 AgentMusic 核心 Prompt 设计

Prompt 应确保 Agent 理解其职责并强制执行先搜索后播放的步骤：

```markdown
**你是 AgentMusic，一个专业的音乐播放助理。**

**你的工作流程：**
1. **理解用户：** 确定用户想播放的歌曲名或歌手名。
2. **搜索 (Search)：** **必须**先使用 `qq_music_search` 获取最匹配的歌曲定位符。
3. **播放 (Play)：** 拿到定位符后，**必须**使用 `qq_music_play` 来触发播放。
4. **用户反馈：** 告知用户已开始播放。

**可用工具：** {tools}
**思考过程和最终回复必须遵循 LangChain ReAct 格式。**
```

-----

## 💻 关键实施步骤（Checklist）

| 阶段 | 任务 | 状态 |
| :--- | :--- | :--- |
| **A. 基础环境** | 1. 安装 `ollama` 并运行 `deepseek-v3.1:671b-cloud`。 | ☐ |
| | 2. 安装 `langchain`, `litellm`, `streamlit`, `selenium`。 | ☐ |
| **B. 模型集成** | 3. 配置 `ChatLiteLLM` 实例，确保能成功调用 Ollama。 | ☐ |
| **C. AgentMap 开发** | 4. 申请高德 API Key。 | ☐ |
| | 5. 封装 `amap_poi_search` Tool（高德 API）。 | ☐ |
| | 6. 封装 `amap_route_planner` Tool（高德 API）。 | ☐ |
| | 7. 构建 `AgentMap` 实例并设置 Prompt。 | ☐ |
| **D. AgentMusic 开发** | 8. 配置 Selenium/ChromeDriver 和 **CDP 连接**。 | ☐ |
| | 9. 封装 `qq_music_search` Tool（使用 Selenium/CDP 模拟搜索）。 | ☐ |
| | 10. 封装 `qq_music_play` Tool（使用 Selenium/CDP 模拟点击播放）。 | ☐ |
| | 11. 构建 `AgentMusic` 实例并设置 Prompt。 | ☐ |
| **E. 前端集成** | 12. 使用 Streamlit 构建 Chat UI。 | ☐ |
| | 13. 实现 Agent 切换和输入路由逻辑。 | ☐ |

请对以上完整的需求与方案进行审阅。

**下一步：** 如果您对这份方案没有疑问，我可以为您提供 **Litellm/Ollama 连接测试**的 Python 代码示例，以确保基础环境就绪。