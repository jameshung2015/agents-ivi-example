# Supervisor Agent 使用指南

## 概述

Supervisor Agent 是一个智能路由系统，能够：
1. 自动分析用户意图
2. 选择最合适的子Agent执行任务
3. 回收和标准化执行结果
4. 提供完整的可观测性和追踪能力

## 架构设计

```
┌─────────────┐
│   用户输入   │
└──────┬──────┘
       │
       v
┌─────────────────────────────┐
│   Supervisor Agent          │
│  ┌───────────────────────┐ │
│  │  1. 意图分析          │ │
│  │  2. Agent选择         │ │
│  │  3. 任务执行          │ │
│  │  4. 结果回收          │ │
│  └───────────────────────┘ │
└─────────────┬───────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    v         v         v
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Map    │ │  Music  │ │ General │
│  Agent  │ │  Agent  │ │   LLM   │
└─────────┘ └─────────┘ └─────────┘
```

## 核心功能

### 1. 自动意图识别

Supervisor Agent 使用 LLM 分析用户输入，自动判断应该使用哪个专业Agent：

- **Map Agent**: 处理地图、导航、POI搜索、路径规划等任务
- **Music Agent**: 处理音乐搜索、播放、平台选择等任务
- **General**: 处理一般性对话和其他任务

示例：
```python
supervisor = get_supervisor_agent()

# 自动识别为 map agent
result = supervisor.execute_task("查询上海东方明珠的位置")

# 自动识别为 music agent
result = supervisor.execute_task("播放周杰伦的青花瓷")

# 自动识别为 general
result = supervisor.execute_task("今天天气怎么样")
```

### 2. 手动指定Agent

如果需要，也可以手动指定使用哪个Agent：

```python
# 手动指定使用 map agent
result = supervisor.execute_task(
    "查询北京景点", 
    agent_type="map"
)

# 手动指定使用 music agent
result = supervisor.execute_task(
    "搜索歌曲", 
    agent_type="music"
)
```

### 3. 标准化结果处理

所有任务执行结果都被包装在 `TaskResult` 对象中：

```python
class TaskResult:
    success: bool           # 执行是否成功
    agent_type: str         # 使用的Agent类型
    content: str            # 返回内容
    metadata: Dict          # 元数据（task_id, 执行时间等）
    error: str              # 错误信息（如果失败）
```

使用示例：
```python
result = supervisor.execute_task("查询上海外滩")

if result.success:
    print(f"执行成功，耗时: {result.metadata['execution_time']:.2f}秒")
    print(f"使用的Agent: {result.agent_type}")
    print(f"返回内容: {result.content}")
else:
    print(f"执行失败: {result.error}")
```

### 4. 任务历史追踪

Supervisor Agent 自动记录所有任务执行历史：

```python
# 获取最近10条任务记录
history = supervisor.get_task_history(limit=10)

for record in history:
    print(f"Task ID: {record['task_id']}")
    print(f"  用户输入: {record['user_input']}")
    print(f"  使用Agent: {record['agent_type']}")
    print(f"  执行状态: {record['success']}")
    print(f"  执行时间: {record['execution_time']}秒")
```

### 5. 统计分析

获取系统运行统计信息：

```python
stats = supervisor.get_statistics()

print(f"总任务数: {stats['total_tasks']}")
print(f"成功率: {stats['success_rate'] * 100}%")
print(f"平均执行时间: {stats['avg_execution_time']}秒")
print(f"Agent使用分布: {stats['agent_usage']}")
```

## 可观测性功能

### 1. 执行追踪

系统自动记录所有函数执行的追踪信息：

```python
from app.backend.observability import observability

# 获取所有追踪记录
traces = observability.get_traces(limit=100)

# 获取特定task的追踪
traces = observability.get_traces(trace_id="abc123")
```

### 2. 事件记录

系统记录重要事件：

```python
# 获取所有事件
events = observability.get_events(limit=100)

# 获取特定类型的事件
events = observability.get_events(event_type="agent_failure")
```

### 3. 性能指标

系统收集各种性能指标：

```python
# 获取所有指标
metrics = observability.get_metrics()

# 获取特定指标
metrics = observability.get_metrics("agent.map.execution_time")
```

### 4. 数据导出

导出完整的可观测性数据：

```python
# 导出到JSON文件
filepath = observability.export_to_file()
print(f"数据已导出到: {filepath}")

# 自定义文件名
filepath = observability.export_to_file("my_export.json")
```

## Web界面使用

### 启动应用

使用新的supervisor版本前端：

```bash
# 方式1: 使用启动脚本
python run_app_supervisor.py

# 方式2: 直接运行streamlit
cd lc-entertainment
streamlit run app/frontend/app_supervisor.py
```

### 界面功能

#### 1. 智能路由模式

在侧边栏选择"智能路由"模式，系统会自动分析用户输入并选择合适的Agent。

优点：
- 用户体验更自然
- 无需了解系统内部结构
- 适合一般用户

#### 2. 手动选择模式

在侧边栏选择"手动选择"模式，可以明确指定使用哪个Agent。

优点：
- 控制更精确
- 适合调试和测试
- 适合专业用户

#### 3. 系统统计

侧边栏实时显示：
- 总任务数
- 成功率
- 平均执行时间
- Agent使用分布

#### 4. 执行历史

点击"查看执行历史"按钮可以查看：
- 任务执行时间
- Task ID
- 用户输入
- 使用的Agent
- 执行状态
- 执行时长

#### 5. 数据导出

点击"导出追踪数据"按钮可以导出完整的可观测性数据到JSON文件。

## 添加新Agent

### 步骤1: 创建Agent文件

在 `app/backend/agents/` 创建新的Agent文件，例如 `weather_agent.py`：

```python
"""
天气 Agent
"""
import logging
from langchain.agents import create_agent
from ..llm import llm
from ..tools import weather_query  # 你的工具

logger = logging.getLogger(__name__)

WEATHER_SYSTEM_PROMPT = """
你是 AgentWeather，一个专业的天气查询助理。
...
"""

def create_weather_agent():
    logger.info("创建天气 Agent...")
    tools = [weather_query]
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=WEATHER_SYSTEM_PROMPT,
    )
    logger.info("天气 Agent 创建成功")
    return agent
```

### 步骤2: 注册到Supervisor

修改 `supervisor_agent.py`：

```python
# 在 __init__ 方法中添加
def _init_sub_agents(self):
    from .map_agent import create_map_agent
    from .music_agent import create_music_agent
    from .weather_agent import create_weather_agent  # 新增
    
    self.sub_agents = {
        "map": create_map_agent(),
        "music": create_music_agent(),
        "weather": create_weather_agent(),  # 新增
    }
```

### 步骤3: 更新意图识别

在 `analyze_intent` 方法中更新提示词：

```python
classification_prompt = f"""
可用的Agent类型：
- map: 地图相关任务
- music: 音乐相关任务
- weather: 天气查询任务  # 新增
- general: 其他一般性对话

用户输入: {user_input}

请只返回Agent类型（map/music/weather/general）
"""
```

### 步骤4: 更新前端

在 `app_supervisor.py` 中添加新Agent到手动选择列表：

```python
manual_agent = st.selectbox(
    "选择Agent",
    ["map", "music", "weather", "general"],  # 添加 "weather"
    format_func=lambda x: {
        "map": "🗺️ 地图Agent",
        "music": "🎵 音乐Agent",
        "weather": "🌤️ 天气Agent",  # 新增
        "general": "💬 通用对话"
    }[x]
)
```

## 测试

运行完整测试套件：

```bash
cd lc-entertainment
python tests/test_supervisor_agent.py
```

测试包括：
1. 意图识别准确性测试
2. 各Agent路由测试
3. 手动指定Agent测试
4. 任务历史记录测试
5. 统计功能测试
6. 可观测性测试

## 最佳实践

### 1. 错误处理

始终检查任务执行结果：

```python
result = supervisor.execute_task(user_input)

if result.success:
    # 处理成功情况
    process_result(result.content)
else:
    # 处理失败情况
    handle_error(result.error)
```

### 2. 性能监控

定期检查统计信息：

```python
stats = supervisor.get_statistics()

if stats['success_rate'] < 0.8:
    logger.warning(f"成功率过低: {stats['success_rate']}")

if stats['avg_execution_time'] > 10:
    logger.warning(f"平均执行时间过长: {stats['avg_execution_time']}秒")
```

### 3. 日志配置

在生产环境中配置适当的日志级别：

```python
# 开发环境：详细日志
setup_logging(log_level=logging.DEBUG)

# 生产环境：只记录重要信息
setup_logging(log_level=logging.INFO)
```

### 4. 历史记录管理

定期清理历史记录以避免内存占用过多：

```python
# SupervisorAgent 自动限制为最多100条
# 可以手动清理
supervisor.task_history.clear()
```

### 5. 数据导出

定期导出可观测性数据用于分析：

```python
import schedule

def export_daily_data():
    observability.export_to_file(
        f"daily_export_{datetime.now().strftime('%Y%m%d')}.json"
    )

# 每天导出一次
schedule.every().day.at("23:59").do(export_daily_data)
```

## 故障排查

### 问题1: 意图识别不准确

**症状**: Agent选择经常错误

**解决方案**:
1. 检查 LLM 模型是否正常运行
2. 优化 `analyze_intent` 中的分类提示词
3. 增加更多示例到提示词中
4. 考虑使用更强大的模型

### 问题2: 执行时间过长

**症状**: 任务执行耗时超过预期

**解决方案**:
1. 检查网络连接（如调用外部API）
2. 优化子Agent的工具实现
3. 增加超时控制
4. 使用异步执行

### 问题3: 可观测数据过多

**症状**: 内存占用持续增长

**解决方案**:
1. 定期导出并清理数据
2. 调整 ObservabilityManager 的容量限制
3. 实现数据持久化到数据库

### 问题4: SubAgent执行失败

**症状**: 某个Agent总是返回错误

**解决方案**:
1. 检查Agent的工具配置
2. 验证API密钥和环境变量
3. 查看详细日志定位问题
4. 单独测试该Agent

## 进阶功能

### 自定义路由逻辑

如果需要更复杂的路由逻辑，可以覆盖 `analyze_intent` 方法：

```python
class CustomSupervisorAgent(SupervisorAgent):
    def analyze_intent(self, user_input: str):
        # 自定义路由逻辑
        if "紧急" in user_input:
            return "priority_agent"
        
        # 使用规则+ LLM混合
        keywords = {
            "map": ["导航", "路线", "地图", "位置"],
            "music": ["播放", "音乐", "歌曲"],
        }
        
        for agent_type, words in keywords.items():
            if any(word in user_input for word in words):
                return agent_type
        
        # 回退到LLM分析
        return super().analyze_intent(user_input)
```

### 集成外部监控系统

将可观测性数据导出到外部系统：

```python
# 导出到 Prometheus
from prometheus_client import Counter, Histogram

task_counter = Counter('agent_tasks_total', 'Total tasks', ['agent_type'])
task_duration = Histogram('agent_task_duration_seconds', 'Task duration')

# 在执行任务时记录
task_counter.labels(agent_type=result.agent_type).inc()
task_duration.observe(result.metadata['execution_time'])
```

## 总结

Supervisor Agent 提供了完整的多Agent协作和可观测性解决方案：

✅ **智能路由**: 自动分析意图，选择最佳Agent
✅ **标准化接口**: 统一的结果格式和错误处理
✅ **完整追踪**: 记录所有任务执行历史
✅ **性能监控**: 收集指标和统计信息
✅ **易于扩展**: 简单添加新Agent到系统
✅ **开发友好**: 详细的日志和调试信息

通过这个系统，你可以轻松构建复杂的多Agent应用，同时保持良好的可观测性和维护性。
