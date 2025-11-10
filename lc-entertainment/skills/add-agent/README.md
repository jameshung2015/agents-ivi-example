# Add Agent Skill

这个技能提供了在 LangChain 多 Agent 系统中创建新 Agent 的完整指南。

## 内容

- **SKILL.md**: 完整的 Agent 创建指南，包括工具设计、系统提示、测试等
- **references/**: 参考文件
  - `weather_agent_example.py`: Agent 代码示例
  - `weather_tool_example.py`: 工具代码示例
  - `test_weather_agent_example.py`: 测试代码示例
  - `quick_reference.md`: 快速参考指南
- **LICENSE.txt**: MIT 许可证

## 使用方法

1. 阅读 SKILL.md 了解完整的创建流程
2. 参考 references/ 中的示例代码
3. 按照步骤创建你的新 Agent
4. 使用测试示例验证功能

## 技能结构

```
add-agent/
├── SKILL.md                                    # 主技能文档
├── LICENSE.txt                                 # 许可证
├── README.md                                   # 本文件
└── references/                                 # 参考文件
    ├── weather_agent_example.py               # Agent 示例
    ├── weather_tool_example.py                # 工具示例
    ├── test_weather_agent_example.py          # 测试示例
    └── quick_reference.md                     # 快速参考
```

## 适用场景

- 添加新的业务领域 Agent（如天气、新闻、日历）
- 集成外部 API 服务
- 创建浏览器自动化 Agent
- 扩展现有的多 Agent 系统
