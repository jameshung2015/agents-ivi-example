"""
主路由 Agent (Supervisor) - 负责任务分析、分发和结果协调
"""
import logging
from typing import Literal, Dict, Any, List
from langchain_core.messages import HumanMessage
from ..llm import llm

logger = logging.getLogger(__name__)

# Agent类型定义
AgentType = Literal["map", "music", "general"]


class TaskResult:
    """任务执行结果的标准化包装"""
    def __init__(
        self,
        success: bool,
        agent_type: AgentType,
        content: str,
        metadata: Dict[str, Any] = None,
        error: str = None
    ):
        self.success = success
        self.agent_type = agent_type
        self.content = content
        self.metadata = metadata or {}
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "agent_type": self.agent_type,
            "content": self.content,
            "metadata": self.metadata,
            "error": self.error
        }


class SupervisorAgent:
    """
    主路由Agent，负责：
    1. 分析用户意图
    2. 选择合适的子Agent
    3. 执行任务并回收结果
    4. 记录执行过程
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".SupervisorAgent")
        self.task_history: List[Dict[str, Any]] = []

        # 创建子Agent实例
        self._init_sub_agents()

        self.logger.info("SupervisorAgent 初始化完成")

    def _init_sub_agents(self):
        """初始化所有子Agent"""
        from .map_agent import create_map_agent
        from .music_agent import create_music_agent

        self.sub_agents = {
            "map": create_map_agent(),
            "music": create_music_agent()
        }

        self.logger.info(f"已加载 {len(self.sub_agents)} 个子Agent: {list(self.sub_agents.keys())}")

    def analyze_intent(self, user_input: str) -> AgentType:
        """
        分析用户意图，决定使用哪个子Agent

        Args:
            user_input: 用户输入文本

        Returns:
            AgentType: 应该使用的Agent类型
        """
        self.logger.info(f"开始分析用户意图: {user_input}")

        # 使用LLM进行意图分类
        classification_prompt = f"""你是一个任务分类助手。根据用户的输入，判断应该使用哪个专业Agent来处理。

可用的Agent类型：
- map: 地图相关任务，包括POI搜索、路径规划、地点查询、导航等
- music: 音乐相关任务，包括搜索歌曲、播放音乐、音乐平台操作等
- general: 其他一般性对话或无法分类的任务

用户输入: {user_input}

请只返回Agent类型（map/music/general），不要返回其他内容。
"""

        try:
            response = llm.invoke([HumanMessage(content=classification_prompt)])
            agent_type = response.content.strip().lower()

            # 验证返回的类型
            if agent_type not in ["map", "music", "general"]:
                self.logger.warning(f"LLM返回了未知的Agent类型: {agent_type}，默认使用general")
                agent_type = "general"

            self.logger.info(f"意图分析结果: {agent_type}")
            return agent_type

        except Exception as e:
            self.logger.error(f"意图分析失败: {e}", exc_info=True)
            return "general"

    def execute_task(
        self,
        user_input: str,
        agent_type: AgentType = None
    ) -> TaskResult:
        """
        执行任务

        Args:
            user_input: 用户输入
            agent_type: 指定的Agent类型，如果为None则自动分析

        Returns:
            TaskResult: 任务执行结果
        """
        import time
        start_time = time.time()

        # 生成任务ID用于追踪
        import uuid
        task_id = str(uuid.uuid4())[:8]

        self.logger.info(f"[任务 {task_id}] 开始执行")
        self.logger.info(f"[任务 {task_id}] 用户输入: {user_input}")

        # 记录到可观测性系统
        from ..observability import observability
        trace_id = observability.start_trace(f"execute_task.{task_id}", {"user_input": user_input})

        try:
            # 1. 意图识别
            if agent_type is None:
                observability.record_event("intent_analysis", {"task_id": task_id})
                agent_type = self.analyze_intent(user_input)

            self.logger.info(f"[任务 {task_id}] 选择Agent: {agent_type}")
            observability.record_event("agent_selection", {"task_id": task_id, "agent_type": agent_type})

            # 2. 执行任务
            if agent_type == "general":
                # 一般性对话，直接用LLM回复
                response = llm.invoke([HumanMessage(content=user_input)])
                result_content = response.content

            elif agent_type in self.sub_agents:
                # 使用子Agent执行
                agent = self.sub_agents[agent_type]
                self.logger.info(f"[任务 {task_id}] 调用 {agent_type} Agent")
                observability.record_event("agent_invocation", {"task_id": task_id, "agent_type": agent_type})

                response = agent.invoke({
                    "messages": [{"role": "user", "content": user_input}]
                })

                # 提取最后一条消息
                messages = response.get("messages", [])
                if messages:
                    last_message = messages[-1]
                    result_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
                else:
                    result_content = "(Agent未返回内容)"
            else:
                raise ValueError(f"未知的Agent类型: {agent_type}")

            # 3. 记录执行信息
            execution_time = time.time() - start_time

            result = TaskResult(
                success=True,
                agent_type=agent_type,
                content=result_content,
                metadata={
                    "task_id": task_id,
                    "execution_time": execution_time,
                    "user_input": user_input,
                    "trace_id": trace_id
                }
            )

            # 4. 保存到历史记录和可观测性系统
            self._record_task(task_id, user_input, agent_type, result, execution_time)
            observability.end_trace(trace_id, {"success": True, "execution_time": execution_time})
            observability.record_metric(f"agent.{agent_type}.execution_time", execution_time)
            observability.record_metric(f"agent.{agent_type}.success", 1)

            self.logger.info(f"[任务 {task_id}] 执行成功，耗时: {execution_time:.2f}秒")
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"[任务 {task_id}] 执行失败: {e}", exc_info=True)

            result = TaskResult(
                success=False,
                agent_type=agent_type or "unknown",
                content=f"任务执行失败: {str(e)}",
                error=str(e),
                metadata={
                    "task_id": task_id,
                    "execution_time": execution_time,
                    "user_input": user_input,
                    "trace_id": trace_id
                }
            )

            self._record_task(task_id, user_input, agent_type, result, execution_time)
            observability.end_trace(trace_id, {"success": False, "error": str(e)})
            observability.record_metric(f"agent.{agent_type or 'unknown'}.failure", 1)
            return result

    def _record_task(
        self,
        task_id: str,
        user_input: str,
        agent_type: AgentType,
        result: TaskResult,
        execution_time: float
    ):
        """记录任务执行历史"""
        import datetime

        record = {
            "task_id": task_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "user_input": user_input,
            "agent_type": agent_type,
            "success": result.success,
            "execution_time": execution_time,
            "result": result.to_dict()
        }

        self.task_history.append(record)

        # 限制历史记录数量
        if len(self.task_history) > 100:
            self.task_history = self.task_history[-100:]

    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取任务执行历史"""
        return self.task_history[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.task_history:
            return {
                "total_tasks": 0,
                "success_rate": 0,
                "avg_execution_time": 0,
                "agent_usage": {}
            }

        total = len(self.task_history)
        success_count = sum(1 for t in self.task_history if t["success"])

        # 按Agent类型统计
        agent_usage = {}
        for task in self.task_history:
            agent_type = task["agent_type"]
            if agent_type not in agent_usage:
                agent_usage[agent_type] = 0
            agent_usage[agent_type] += 1

        # 平均执行时间
        avg_time = sum(t["execution_time"] for t in self.task_history) / total

        return {
            "total_tasks": total,
            "success_rate": success_count / total,
            "avg_execution_time": avg_time,
            "agent_usage": agent_usage
        }


# 全局单例
_supervisor_instance = None


def get_supervisor_agent() -> SupervisorAgent:
    """获取或创建SupervisorAgent单例"""
    global _supervisor_instance
    if _supervisor_instance is None:
        _supervisor_instance = SupervisorAgent()
    return _supervisor_instance


def create_supervisor_agent() -> SupervisorAgent:
    """创建SupervisorAgent实例（为了保持与其他Agent的接口一致）"""
    return get_supervisor_agent()
