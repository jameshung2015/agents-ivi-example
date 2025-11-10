"""
可观测性增强模块
提供统一的日志、追踪、监控和性能分析功能
"""
import logging
import time
import json
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from datetime import datetime
from functools import wraps
import threading

logger = logging.getLogger(__name__)


class ObservabilityManager:
    """可观测性管理器 - 单例模式"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.logger = logging.getLogger(__name__ + ".ObservabilityManager")

        # 追踪数据存储
        self.traces: List[Dict[str, Any]] = []
        self.metrics: Dict[str, List[float]] = {}
        self.events: List[Dict[str, Any]] = []

        # 配置
        self.max_traces = 1000
        self.max_events = 1000

        # 日志文件
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        self.logger.info("ObservabilityManager 初始化完成")

    def start_trace(self, span_name: str, metadata: Dict[str, Any] = None) -> str:
        """
        开始一个新的追踪

        Args:
            span_name: span名称
            metadata: 元数据

        Returns:
            trace_id: 追踪ID
        """
        import uuid
        trace_id = str(uuid.uuid4())[:8]

        trace = {
            "trace_id": trace_id,
            "span_name": f"{span_name}.start",
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.traces.append(trace)

        # 限制追踪数量
        if len(self.traces) > self.max_traces:
            self.traces = self.traces[-self.max_traces:]

        return trace_id

    def end_trace(self, trace_id: str, metadata: Dict[str, Any] = None):
        """
        结束追踪

        Args:
            trace_id: 追踪ID
            metadata: 元数据
        """
        trace = {
            "trace_id": trace_id,
            "span_name": "end",
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.traces.append(trace)

        # 限制追踪数量
        if len(self.traces) > self.max_traces:
            self.traces = self.traces[-self.max_traces:]

    def trace(self, trace_id: str, span_name: str, metadata: Dict[str, Any] = None):
        """
        创建追踪span

        Args:
            trace_id: 追踪ID
            span_name: span名称
            metadata: 元数据
        """
        trace = {
            "trace_id": trace_id,
            "span_name": span_name,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.traces.append(trace)

        # 限制追踪数量
        if len(self.traces) > self.max_traces:
            self.traces = self.traces[-self.max_traces:]

    def record_metric(self, metric_name: str, value: float):
        """
        记录指标

        Args:
            metric_name: 指标名称
            value: 指标值
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []

        self.metrics[metric_name].append(value)

        # 限制每个指标的存储数量
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]

    def record_event(self, event_type: str, data: Dict[str, Any]):
        """
        记录事件

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        event = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        self.events.append(event)

        # 限制事件数量
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]

        self.logger.info(f"事件记录: {event_type} - {json.dumps(data, ensure_ascii=False)}")

    def get_traces(self, trace_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取追踪记录"""
        if trace_id:
            filtered = [t for t in self.traces if t["trace_id"] == trace_id]
            return filtered[-limit:]
        return self.traces[-limit:]

    def get_metrics(self, metric_name: Optional[str] = None) -> Dict[str, List[float]]:
        """获取指标数据"""
        if metric_name:
            return {metric_name: self.metrics.get(metric_name, [])}
        return self.metrics

    def get_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取事件记录"""
        if event_type:
            filtered = [e for e in self.events if e["event_type"] == event_type]
            return filtered[-limit:]
        return self.events[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计摘要"""
        stats = {
            "total_traces": len(self.traces),
            "total_events": len(self.events),
            "metrics_count": len(self.metrics),
            "metric_summary": {}
        }

        # 计算每个指标的统计信息
        for metric_name, values in self.metrics.items():
            if values:
                stats["metric_summary"][metric_name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values)
                }

        return stats

    def export_to_file(self, filename: Optional[str] = None):
        """导出可观测数据到文件"""
        if filename is None:
            filename = f"observability_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.log_dir / filename

        data = {
            "exported_at": datetime.now().isoformat(),
            "traces": self.traces,
            "events": self.events,
            "metrics": {k: v for k, v in self.metrics.items()},
            "statistics": self.get_statistics()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"可观测数据已导出到: {filepath}")
        return str(filepath)


def trace_execution(span_name: str = None):
    """
    装饰器：追踪函数执行

    Args:
        span_name: span名称，如果为None则使用函数名
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            obs = ObservabilityManager()

            # 生成trace_id
            import uuid
            trace_id = str(uuid.uuid4())[:8]

            # 确定span名称
            name = span_name or func.__name__

            # 记录开始
            start_time = time.time()
            obs.trace(trace_id, f"{name}.start", {
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            })

            try:
                # 执行函数
                result = func(*args, **kwargs)

                # 记录成功
                execution_time = time.time() - start_time
                obs.trace(trace_id, f"{name}.success", {
                    "execution_time": execution_time
                })
                obs.record_metric(f"{name}.execution_time", execution_time)
                obs.record_event("function_success", {
                    "function": func.__name__,
                    "trace_id": trace_id,
                    "execution_time": execution_time
                })

                return result

            except Exception as e:
                # 记录失败
                execution_time = time.time() - start_time
                obs.trace(trace_id, f"{name}.error", {
                    "error": str(e),
                    "execution_time": execution_time
                })
                obs.record_event("function_error", {
                    "function": func.__name__,
                    "trace_id": trace_id,
                    "error": str(e),
                    "execution_time": execution_time
                })

                raise

        return wrapper
    return decorator


def monitor_agent_execution(agent_type: str):
    """
    装饰器：监控Agent执行

    Args:
        agent_type: Agent类型
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            obs = ObservabilityManager()

            # 记录Agent调用
            obs.record_event("agent_invocation", {
                "agent_type": agent_type,
                "function": func.__name__
            })

            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # 记录成功指标
                obs.record_metric(f"agent.{agent_type}.execution_time", execution_time)
                obs.record_metric(f"agent.{agent_type}.success", 1)

                return result

            except Exception as e:
                execution_time = time.time() - start_time

                # 记录失败指标
                obs.record_metric(f"agent.{agent_type}.execution_time", execution_time)
                obs.record_metric(f"agent.{agent_type}.failure", 1)
                obs.record_event("agent_failure", {
                    "agent_type": agent_type,
                    "error": str(e),
                    "execution_time": execution_time
                })

                raise

        return wrapper
    return decorator


# 全局实例
observability = ObservabilityManager()
