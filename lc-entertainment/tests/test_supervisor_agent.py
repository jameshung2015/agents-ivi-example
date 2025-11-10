"""
测试 Supervisor Agent 的任务路由和执行能力
"""
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.backend.agents import get_supervisor_agent
from app.backend.observability import observability

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_intent_recognition():
    """测试意图识别功能"""
    logger.info("\n" + "="*80)
    logger.info("测试 1: 意图识别")
    logger.info("="*80)

    supervisor = get_supervisor_agent()

    test_cases = [
        ("查询上海东方明珠到外滩的路线", "map"),
        ("播放周杰伦的青花瓷", "music"),
        ("今天天气怎么样", "general"),
        ("从北京天安门到故宫怎么走", "map"),
        ("在网易云音乐播放告白气球", "music"),
        ("你好", "general"),
    ]

    correct = 0
    for user_input, expected_agent in test_cases:
        detected_agent = supervisor.analyze_intent(user_input)
        is_correct = detected_agent == expected_agent
        correct += is_correct

        status = "✅" if is_correct else "❌"
        logger.info(f"{status} 输入: '{user_input}'")
        logger.info(f"   期望: {expected_agent}, 检测: {detected_agent}")

    accuracy = correct / len(test_cases) * 100
    logger.info(f"\n意图识别准确率: {accuracy:.1f}% ({correct}/{len(test_cases)})")

    return accuracy >= 80  # 期望至少80%准确率


def test_map_agent_routing():
    """测试地图Agent路由"""
    logger.info("\n" + "="*80)
    logger.info("测试 2: 地图Agent任务执行")
    logger.info("="*80)

    supervisor = get_supervisor_agent()

    queries = [
        "查询北京天安门的位置",
        "从上海人民广场到东方明珠的驾车路线",
    ]

    for query in queries:
        logger.info(f"\n查询: {query}")
        result = supervisor.execute_task(query)

        logger.info(f"Agent类型: {result.agent_type}")
        logger.info(f"执行状态: {'成功' if result.success else '失败'}")
        logger.info(f"执行时间: {result.metadata.get('execution_time', 0):.2f}秒")
        logger.info(f"返回内容: {result.content[:200]}...")

        # 验证是否正确路由到map agent
        assert result.agent_type == "map", f"期望使用map agent,实际使用了{result.agent_type}"

    return True


def test_music_agent_routing():
    """测试音乐Agent路由"""
    logger.info("\n" + "="*80)
    logger.info("测试 3: 音乐Agent任务执行")
    logger.info("="*80)

    supervisor = get_supervisor_agent()

    queries = [
        "播放周杰伦的晴天",
        "在QQ音乐搜索夜曲",
    ]

    for query in queries:
        logger.info(f"\n查询: {query}")
        result = supervisor.execute_task(query)

        logger.info(f"Agent类型: {result.agent_type}")
        logger.info(f"执行状态: {'成功' if result.success else '失败'}")
        logger.info(f"执行时间: {result.metadata.get('execution_time', 0):.2f}秒")
        logger.info(f"返回内容: {result.content[:200]}...")

        # 验证是否正确路由到music agent
        assert result.agent_type == "music", f"期望使用music agent,实际使用了{result.agent_type}"

    return True


def test_manual_routing():
    """测试手动指定Agent"""
    logger.info("\n" + "="*80)
    logger.info("测试 4: 手动指定Agent类型")
    logger.info("="*80)

    supervisor = get_supervisor_agent()

    # 用一个地图类查询，但手动指定使用general agent
    query = "查询北京天安门"
    logger.info(f"查询: {query}")
    logger.info("手动指定使用: general agent")

    result = supervisor.execute_task(query, agent_type="general")

    logger.info(f"实际使用: {result.agent_type}")
    assert result.agent_type == "general", "手动指定Agent失败"

    return True


def test_task_history():
    """测试任务历史记录"""
    logger.info("\n" + "="*80)
    logger.info("测试 5: 任务历史记录")
    logger.info("="*80)

    supervisor = get_supervisor_agent()

    # 执行几个任务
    queries = [
        "你好",
        "查询上海外滩",
        "播放青花瓷"
    ]

    for query in queries:
        supervisor.execute_task(query)

    # 获取历史记录
    history = supervisor.get_task_history(limit=10)

    logger.info(f"历史记录数量: {len(history)}")

    for record in history[-3:]:  # 显示最近3条
        logger.info(f"\nTask ID: {record['task_id']}")
        logger.info(f"  输入: {record['user_input']}")
        logger.info(f"  Agent: {record['agent_type']}")
        logger.info(f"  状态: {'成功' if record['success'] else '失败'}")
        logger.info(f"  耗时: {record['execution_time']:.2f}秒")

    return len(history) >= 3


def test_statistics():
    """测试统计功能"""
    logger.info("\n" + "="*80)
    logger.info("测试 6: 统计信息")
    logger.info("="*80)

    supervisor = get_supervisor_agent()
    stats = supervisor.get_statistics()

    logger.info(f"总任务数: {stats['total_tasks']}")
    logger.info(f"成功率: {stats['success_rate']*100:.1f}%")
    logger.info(f"平均执行时间: {stats['avg_execution_time']:.2f}秒")
    logger.info(f"Agent使用分布:")
    for agent_type, count in stats['agent_usage'].items():
        logger.info(f"  {agent_type}: {count}次")

    return True


def test_observability():
    """测试可观测性功能"""
    logger.info("\n" + "="*80)
    logger.info("测试 7: 可观测性")
    logger.info("="*80)

    # 获取可观测性数据
    obs_stats = observability.get_statistics()

    logger.info(f"追踪记录数: {obs_stats['total_traces']}")
    logger.info(f"事件记录数: {obs_stats['total_events']}")
    logger.info(f"指标数量: {obs_stats['metrics_count']}")

    # 导出数据
    filepath = observability.export_to_file()
    logger.info(f"可观测数据已导出到: {filepath}")

    return True


def run_all_tests():
    """运行所有测试"""
    logger.info("\n" + "#"*80)
    logger.info("# Supervisor Agent 完整测试套件")
    logger.info("#"*80)

    tests = [
        ("意图识别", test_intent_recognition),
        ("地图Agent路由", test_map_agent_routing),
        ("音乐Agent路由", test_music_agent_routing),
        ("手动指定Agent", test_manual_routing),
        ("任务历史记录", test_task_history),
        ("统计功能", test_statistics),
        ("可观测性", test_observability),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success, None))
            logger.info(f"\n✅ {test_name} - 通过")
        except Exception as e:
            results.append((test_name, False, str(e)))
            logger.error(f"\n❌ {test_name} - 失败: {e}", exc_info=True)

    # 汇总结果
    logger.info("\n" + "="*80)
    logger.info("测试结果汇总")
    logger.info("="*80)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for test_name, success, error in results:
        status = "✅ 通过" if success else f"❌ 失败: {error}"
        logger.info(f"{test_name}: {status}")

    logger.info(f"\n总计: {passed}/{total} 通过 ({passed/total*100:.1f}%)")

    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n测试执行失败: {e}", exc_info=True)
        sys.exit(1)
