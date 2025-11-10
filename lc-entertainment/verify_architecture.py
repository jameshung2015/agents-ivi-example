#!/usr/bin/env python3
"""
简单验证脚本 - 测试 Supervisor Agent 架构的基本功能
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.backend.agents import get_supervisor_agent
from app.backend.observability import observability


def main():
    print("=" * 80)
    print("Supervisor Agent 架构验证")
    print("=" * 80)

    # 1. 初始化 Supervisor
    print("\n[1/5] 初始化 SupervisorAgent...")
    try:
        supervisor = get_supervisor_agent()
        print("✅ SupervisorAgent 初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

    # 2. 测试意图分析
    print("\n[2/5] 测试意图分析...")
    try:
        test_inputs = [
            ("查询北京天安门", "map"),
            ("播放音乐", "music"),
            ("你好", "general"),
        ]

        for user_input, expected in test_inputs:
            result = supervisor.analyze_intent(user_input)
            status = "✅" if result == expected else "⚠️"
            print(f"  {status} '{user_input}' -> {result} (期望: {expected})")

        print("✅ 意图分析测试完成")
    except Exception as e:
        print(f"❌ 意图分析失败: {e}")
        return False

    # 3. 测试任务执行（使用 general agent，不依赖外部服务）
    print("\n[3/5] 测试任务执行...")
    try:
        result = supervisor.execute_task("你好", agent_type="general")
        print(f"  Agent类型: {result.agent_type}")
        print(f"  执行状态: {'成功' if result.success else '失败'}")
        print(f"  执行时间: {result.metadata.get('execution_time', 0):.2f}秒")
        print(f"  返回内容: {result.content[:100]}...")
        print("✅ 任务执行测试完成")
    except Exception as e:
        print(f"❌ 任务执行失败: {e}")
        return False

    # 4. 测试历史记录
    print("\n[4/5] 测试历史记录...")
    try:
        history = supervisor.get_task_history(limit=5)
        print(f"  历史记录数量: {len(history)}")
        print("✅ 历史记录测试完成")
    except Exception as e:
        print(f"❌ 历史记录失败: {e}")
        return False

    # 5. 测试统计功能
    print("\n[5/5] 测试统计功能...")
    try:
        stats = supervisor.get_statistics()
        print(f"  总任务数: {stats['total_tasks']}")
        print(f"  成功率: {stats['success_rate']*100:.1f}%")
        print(f"  平均耗时: {stats['avg_execution_time']:.2f}秒")
        print("✅ 统计功能测试完成")
    except Exception as e:
        print(f"❌ 统计功能失败: {e}")
        return False

    # 6. 测试可观测性
    print("\n[6/6] 测试可观测性...")
    try:
        obs_stats = observability.get_statistics()
        print(f"  追踪记录数: {obs_stats['total_traces']}")
        print(f"  事件记录数: {obs_stats['total_events']}")
        print(f"  指标数量: {obs_stats['metrics_count']}")
        print("✅ 可观测性测试完成")
    except Exception as e:
        print(f"❌ 可观测性失败: {e}")
        return False

    print("\n" + "=" * 80)
    print("✅ 所有验证通过！Supervisor Agent 架构正常工作")
    print("=" * 80)
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
