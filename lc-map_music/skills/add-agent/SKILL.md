---
name: add-agent
description: This skill should be used when users want to add a new agent to the LangChain multi-agent system. It provides guidance on creating new agents with proper tool integration, system prompts, and factory functions following the established patterns in the codebase.
license: MIT
---

# Add Agent Skill

## Purpose

This skill guides the creation of new agents in the LangChain-based multi-agent system. It ensures consistency with existing agent patterns, proper tool integration, and follows best practices for agent design.

## When to Use This Skill

Use this skill when:
- Creating a new specialized agent for a specific domain (e.g., weather, news, calendar)
- Adding an agent with custom tools and workflows
- Extending the multi-agent system with new capabilities
- Implementing agents that interact with external APIs or services

## Project Structure Context

The multi-agent system follows this structure:

```
app/backend/
  agents/
    __init__.py          # Agent registry and exports
    map_agent.py         # Example: Map and routing agent
    music_agent.py       # Example: Music playback agent
  tools/
    __init__.py          # Tool registry and exports
    amap_poi_search.py   # Example: POI search tool
    qq_music_cdp.py      # Example: Browser automation tool
  llm.py                 # Shared LLM instance
  config.py              # Configuration management
```

## Agent Creation Process

### Step 1: Define Agent Tools

Before creating the agent, identify and create the tools it needs:

1. Navigate to `app/backend/tools/`
2. Create tool files following the naming pattern: `{service}_{action}.py`
3. Each tool should:
   - Use `@tool` decorator from LangChain
   - Have clear docstrings describing functionality
   - Include type hints for parameters
   - Handle errors gracefully
   - Log important operations

Example tool structure:
```python
from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)

@tool
def example_tool(param: str) -> dict:
    """
    Tool description that the LLM will see.
    
    Args:
        param: Parameter description
        
    Returns:
        Dictionary with results
    """
    logger.info(f"Executing example_tool with param: {param}")
    # Tool implementation
    return {"status": "success", "data": result}
```

4. Export the tool in `app/backend/tools/__init__.py`:
```python
from .example_tool import example_tool

__all__ = [
    # ... existing tools
    "example_tool",
]
```

### Step 2: Create the Agent File

1. Navigate to `app/backend/agents/`
2. Create a new file: `{domain}_agent.py` (e.g., `weather_agent.py`)
3. Follow this template structure:

```python
"""
{Domain} Agent - Brief description
"""
import logging
from langchain.agents import create_agent
from ..llm import llm
from ..tools import tool1, tool2, tool3

logger = logging.getLogger(__name__)

{DOMAIN}_SYSTEM_PROMPT = (
    "你是 Agent{Domain}，一个专业的{domain}助理。\n\n"
    "工作流程:\n"
    "1. 理解用户需求和意图。\n"
    "2. 调用相关工具获取信息。\n"
    "3. 基于工具返回的数据给出有用的回复。\n\n"
    "可用工具说明:\n"
    "- tool1: Tool 1 description\n"
    "- tool2: Tool 2 description\n"
)

def create_{domain}_agent():
    """创建{domain} Agent"""
    logger.info("创建{domain} Agent...")
    
    tools = [tool1, tool2, tool3]
    logger.info(f"已加载 {len(tools)} 个工具: {[t.name for t in tools]}")
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt={DOMAIN}_SYSTEM_PROMPT,
    )
    
    logger.info("{domain} Agent 创建成功")
    return agent
```

### Step 3: System Prompt Design

Design an effective system prompt that:

1. **Clearly defines the agent's role and identity**
   - Use a clear name (e.g., "AgentWeather", "AgentNews")
   - State the agent's domain expertise

2. **Describes the workflow explicitly**
   - Break down the steps the agent should follow
   - Include decision points and conditional logic
   - Specify when to use which tools

3. **Lists available tools with descriptions**
   - Help the LLM understand what each tool does
   - Mention any tool dependencies or ordering requirements

4. **Sets expectations and constraints**
   - Define response format preferences
   - Specify error handling behavior
   - Note any platform-specific considerations

### Step 4: Register the Agent

1. Export the agent factory function in `app/backend/agents/__init__.py`:

```python
from .{domain}_agent import create_{domain}_agent

__all__ = [
    # ... existing agents
    "create_{domain}_agent",
]
```

2. If the agent should be available in the frontend, update `app/frontend/app.py`:

```python
from app.backend.agents import create_{domain}_agent

# Add to agent selection
agent_type = st.sidebar.selectbox(
    "选择 Agent",
    ["地图Agent", "音乐Agent", "{Domain}Agent"]  # Add your agent
)

# Add to agent creation logic
if agent_type == "{Domain}Agent":
    agent = create_{domain}_agent()
```

### Step 5: Testing

Create a test file in `tests/`:

1. Create `test_{domain}_agent.py`:

```python
"""
Test {domain} agent and tools
"""
import logging
from app.backend.agents import create_{domain}_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_{domain}_agent():
    """Test {domain} agent with sample queries"""
    logger.info("Testing {domain} agent...")
    
    agent = create_{domain}_agent()
    
    # Test queries
    queries = [
        "Sample query 1",
        "Sample query 2",
    ]
    
    for query in queries:
        logger.info(f"\n{'='*60}")
        logger.info(f"Query: {query}")
        logger.info(f"{'='*60}")
        
        response = agent.invoke({"messages": [{"role": "user", "content": query}]})
        logger.info(f"Response: {response}")

if __name__ == "__main__":
    test_{domain}_agent()
```

2. Run the test:
```bash
python tests/test_{domain}_agent.py
```

## Best Practices

### Tool Design
- Keep tools focused on single responsibilities
- Use descriptive names that indicate the action
- Provide comprehensive docstrings for the LLM
- Handle API errors gracefully with meaningful error messages
- Log tool executions for debugging

### System Prompt Guidelines
- Write in Chinese for Chinese-language applications (matching existing agents)
- Use clear, numbered workflows
- Be explicit about tool usage sequences
- Include examples when tool usage is complex
- Keep prompts concise but comprehensive

### Error Handling
- Validate inputs before making external API calls
- Catch and log exceptions
- Return structured error responses
- Provide fallback behaviors when tools fail

### Integration with Existing Code
- Import shared LLM instance from `..llm`
- Follow existing logging patterns
- Use the same agent creation pattern (`create_agent`)
- Maintain consistent naming conventions

## Common Patterns

### Browser Automation (CDP-based)
For agents controlling web browsers via Chrome DevTools Protocol:
- Study `music_agent.py` and `qq_music_cdp.py` as references
- Use the MCP chrome-devtools server tools
- Handle browser state and navigation
- Consider page load timing and selectors

### API Integration
For agents calling REST APIs:
- Study `map_agent.py` and `amap_poi_search.py` as references
- Use environment variables for API keys (via `config.py`)
- Implement proper request error handling
- Cache responses when appropriate

### Multi-step Workflows
For agents with complex decision trees:
- Break workflows into discrete steps in the system prompt
- Use conditional logic to decide tool execution order
- Validate outputs before proceeding to next steps
- Provide intermediate feedback to users

## Reference Examples

### Map Agent (API-based)
Location: `app/backend/agents/map_agent.py`

Key features:
- Uses high德地图 API for POI search and routing
- Two-step workflow: search locations, then plan route
- Provides distance and duration estimates

### Music Agent (Browser Automation)
Location: `app/backend/agents/music_agent.py`

Key features:
- Multi-platform support (QQ Music, NetEase)
- Browser automation via CDP
- Platform selection based on user preference
- Search-then-play workflow

## Troubleshooting

### Common Issues

**Agent doesn't call tools:**
- Check system prompt clarity about when to use tools
- Verify tools are imported and included in the tools list
- Ensure tool docstrings are descriptive

**Tool execution fails:**
- Check API credentials and configuration
- Verify network connectivity
- Review tool error handling and logging
- Test tools independently before integration

**Agent produces incorrect responses:**
- Refine system prompt with more explicit instructions
- Add example scenarios to the prompt
- Validate tool outputs match expected formats
- Check LLM model capabilities

**Import errors:**
- Verify `__init__.py` exports are updated
- Check relative import paths (`..llm`, `..tools`)
- Ensure all dependencies are installed

## Extending This Skill

When the project evolves:

1. Update this SKILL.md with new patterns
2. Add new reference examples to the list
3. Document new tool types or integration methods
4. Keep best practices current with project standards
