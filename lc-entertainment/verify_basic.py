#!/usr/bin/env python3
"""
基础验证脚本 - 测试 Supervisor Agent 架构的基本结构（不依赖 LLM 服务）
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    print("=" * 80)
    print("Supervisor Agent 架构基础验证")
    print("=" * 80)

    # 1. 测试模块导入
    print("\n[1/5] 测试模块导入...")
    try:
        from app.backend.agents import (
            get_supervisor_agent,
            create_supervisor_agent,
            SupervisorAgent,
            TaskResult
        )
        from app.backend.observability import observability
        print("✅ 所有模块导入成功")
        print("  - SupervisorAgent")
        print("  - TaskResult")
        print("  - ObservabilityManager")
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

    # 2. 测试 TaskResult 类
    print("\n[2/5] 测试 TaskResult 类...")
    try:
        result = TaskResult(
            success=True,
            agent_type="test",
            content="测试内容",
            metadata={"key": "value"}
        )
        result_dict = result.to_dict()
        assert result_dict["success"] == True
        assert result_dict["agent_type"] == "test"
        assert result_dict["content"] == "测试内容"
        print("✅ TaskResult 类工作正常")
    except Exception as e:
        print(f"❌ TaskResult 测试失败: {e}")
        return False

    # 3. 测试 ObservabilityManager
    print("\n[3/5] 测试 ObservabilityManager...")
    try:
        # 测试追踪
        trace_id = observability.start_trace("test_span", {"test": "data"})
        observability.end_trace(trace_id, {"success": True})

        # 测试指标
        observability.record_metric("test.metric", 1.23)

        # 测试事件
        observability.record_event("test_event", {"data": "test"})

        # 获取统计
        stats = observability.get_statistics()
        assert stats["total_traces"] >= 2
        assert stats["total_events"] >= 1

        print("✅ ObservabilityManager 工作正常")
        print(f"  - 追踪记录: {stats['total_traces']}")
        print(f"  - 事件记录: {stats['total_events']}")
        print(f"  - 指标数量: {stats['metrics_count']}")
    except Exception as e:
        print(f"❌ ObservabilityManager 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 4. 测试文件结构
    print("\n[4/5] 测试文件结构...")
    try:
        required_files = [
            "app/backend/agents/supervisor_agent.py",
            "app/backend/observability.py",
            "app/frontend/app_supervisor.py",
            "tests/test_supervisor_agent.py",
            "run_app_supervisor.py",
        ]

        missing_files = []
        for file_path in required_files:
            full_path = project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            print(f"❌ 缺少文件: {missing_files}")
            return False

        print("✅ 所有必需文件存在")
        for file_path in required_files:
            print(f"  - {file_path}")
    except Exception as e:
        print(f"❌ 文件结构测试失败: {e}")
        return False

    # 5. 测试导出功能
    print("\n[5/5] 测试数据导出...")
    try:
        filepath = observability.export_to_file()
        export_path = Path(filepath)

        if export_path.exists():
            file_size = export_path.stat().st_size
            print(f"✅ 数据导出成功")
            print(f"  - 文件路径: {filepath}")
            print(f"  - 文件大小: {file_size} bytes")
        else:
            print(f"❌ 导出文件不存在: {filepath}")
            return False
    except Exception as e:
        print(f"❌ 数据导出失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 80)
    print("✅ 所有基础验证通过！")
    print("=" * 80)
    print("\n提示：")
    print("  - 完整功能测试需要 LLM 服务（Ollama）运行")
    print("  - 运行 'python tests/test_supervisor_agent.py' 进行完整测试")
    print("  - 运行 'python run_app_supervisor.py' 启动 Web 界面")
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
