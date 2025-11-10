# Add Agent Skill - Quick Reference

## 创建新 Agent 的快速步骤

### 1. 创建工具 (app/backend/tools/)

```python
from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)

@tool
def your_tool_name(param: str) -> dict:
    """
    工具的功能描述（LLM 会看到这个描述）
    
    Args:
        param: 参数说明
        
    Returns:
        返回值说明
    """
    logger.info(f"执行工具: {param}")
    # 工具实现
    return {"status": "success", "data": result}
```

### 2. 注册工具 (app/backend/tools/__init__.py)

```python
from .your_tool_file import your_tool_name

__all__ = [
    # ... 现有工具
    "your_tool_name",
]
```

### 3. 创建 Agent (app/backend/agents/your_agent.py)

```python
"""
Your Agent - 简短描述
"""
import logging
from langchain.agents import create_agent
from ..llm import llm
from ..tools import your_tool_name

logger = logging.getLogger(__name__)

YOUR_SYSTEM_PROMPT = (
    "你是 AgentYour，一个专业的XXX助理。\n\n"
    "工作流程:\n"
    "1. 步骤1\n"
    "2. 步骤2\n"
    "3. 步骤3\n"
)

def create_your_agent():
    """创建 Your Agent"""
    logger.info("创建 Your Agent...")
    
    tools = [your_tool_name]
    logger.info(f"已加载 {len(tools)} 个工具: {[t.name for t in tools]}")
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=YOUR_SYSTEM_PROMPT,
    )
    
    logger.info("Your Agent 创建成功")
    return agent
```

### 4. 注册 Agent (app/backend/agents/__init__.py)

```python
from .your_agent import create_your_agent

__all__ = [
    # ... 现有 agents
    "create_your_agent",
]
```

### 5. 添加到前端 (app/frontend/app.py)

```python
from app.backend.agents import create_your_agent

# 在 Agent 选择中添加
agent_type = st.sidebar.selectbox(
    "选择 Agent",
    ["地图Agent", "音乐Agent", "YourAgent"]
)

# 在创建逻辑中添加
if agent_type == "YourAgent":
    agent = create_your_agent()
```

### 6. 创建测试 (tests/test_your_agent.py)

```python
"""
测试 Your Agent
"""
import logging
from app.backend.agents import create_your_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_your_agent():
    logger.info("测试 Your Agent...")
    agent = create_your_agent()
    
    queries = ["测试查询1", "测试查询2"]
    
    for query in queries:
        logger.info(f"\n查询: {query}")
        response = agent.invoke({"messages": [{"role": "user", "content": query}]})
        logger.info(f"回复: {response}")

if __name__ == "__main__":
    test_your_agent()
```

## 设计 System Prompt 的关键要素

1. **身份定义**: 明确 Agent 的名称和角色
2. **工作流程**: 列出清晰的步骤序列
3. **工具说明**: 描述每个工具的用途
4. **约束条件**: 说明限制和注意事项

## 常见模式

### API 集成型 (参考 map_agent.py)
- 调用外部 REST API
- 处理 API 错误
- 解析和格式化响应

### 浏览器自动化型 (参考 music_agent.py)
- 使用 Chrome DevTools Protocol
- 处理页面元素选择
- 管理浏览器状态

## 调试技巧

1. **启用详细日志**: `logging.basicConfig(level=logging.DEBUG)`
2. **单独测试工具**: 在集成前先测试工具功能
3. **检查 System Prompt**: 确保指令清晰明确
4. **验证工具注册**: 确认工具在 `__init__.py` 中正确导出
