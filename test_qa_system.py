#!/usr/bin/env python3
"""
QA评估系统测试脚本

测试QA回答质量评估系统的各项功能
"""

import os
import sys
import json
import time
from pathlib import Path

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from qa_evaluation_system import QAEvaluationSystem, create_test_qa_data
    from QA_Answer_Quality_Assessment_Model import QAAssessmentModelWithAnswerEvaluation
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保相关文件在当前目录中")
    sys.exit(1)


def test_single_evaluation():
    """测试单对评估功能"""
    print("\n" + "="*60)
    print("🧪 测试1: 单对QA评估")
    print("="*60)

    system = QAEvaluationSystem()

    test_question = "矿热炉温度传感器出现误差，如何处理？"
    test_answer = "首先检查传感器连接线是否松动或损坏，验证供电电压是否在24VDC范围内，使用万用表测试输出信号。如果损坏则更换传感器并重新标定参数，确保测量精度达到±1%要求。"

    print(f"问题: {test_question}")
    print(f"回答: {test_answer[:100]}...")
    print()

    start_time = time.time()
    result = system.evaluate_single_qa(test_question, test_answer)
    processing_time = time.time() - start_time

    if 'error' in result:
        print(f"❌ 评估失败: {result['error']}")
        return False

    print("✅ 评估成功!"    print(f"📊 综合得分: {result['overall_score']} ({result['overall_level']})")
    print(",")
    print(f"📝 回答得分: {result['answer_evaluation']['answer_quality_score']} ({result['answer_evaluation']['answer_quality_level']})")
    print(".3f")
    print()

    # 显示维度分组结果
    if 'dimension_groups' in result['answer_evaluation']:
        print("📋 维度分类详情:"        for group_name, group_data in result['answer_evaluation']['dimension_groups'].items():
            print(f"  • {group_name}: {group_data['score']}分 (权重: {group_data['weight']})")
            # 显示该组的具体维度
            for dim in group_data['contributions']:
                dim_name = dim['dimension']
                dim_score = dim['score']
                print(f"    - {dim_name}: {dim_score:.1f}分")
        print()

    if 'improvement_suggestions' in result and result['improvement_suggestions']:
        print("💡 改进建议:"        for suggestion in result['improvement_suggestions']:
            print(f"  • [{suggestion['priority']}] {suggestion['target']}: {suggestion['suggestion']}")

    return True


def test_batch_evaluation():
    """测试批量评估功能"""
    print("\n" + "="*60)
    print("🧪 测试2: 批量QA评估")
    print("="*60)

    system = QAEvaluationSystem()
    test_qa_pairs = create_test_qa_data()

    print(f"📊 准备测试 {len(test_qa_pairs)} 个QA对")
    for i, qa in enumerate(test_qa_pairs, 1):
        print(f"  {i}. {qa['question'][:50]}...")
    print()

    start_time = time.time()
    result = system.evaluate_batch_qa(test_qa_pairs, max_workers=2)
    total_time = time.time() - start_time

    print("✅ 批量评估完成!"    print(".2f"    print()

    stats = result['statistics']
    print("📈 统计结果:"    print(f"  • 评估总数: {stats['total_pairs']} 对")
    print(f"  • 有效结果: {stats['valid_results']} 对")
    print(".3f"    print(".3f"    print(f"  • 得分范围: {stats['score_range']['min']} - {stats['score_range']['max']}")
    print()

    print("🏆 质量分布:"    for level, count in stats['quality_distribution'].items():
        percentage = round(count / stats['total_pairs'] * 100, 1)
        print(f"  • {level}: {count} 对 ({percentage}%)")
    print()

    print("⚡ 性能指标:"    perf = stats['performance_metrics']
    print(".2f"    print(".3f")
    print()

    # 显示维度洞察
    if 'dimension_insights' in stats and stats['dimension_insights']:
        insights = stats['dimension_insights']
        print("🔍 维度洞察:"        if 'dimension_averages' in insights:
            print("  • 各维度平均分:"            for dim, avg in insights['dimension_averages'].items():
                print(f"    - {dim}: {avg}分")
            print()

        if 'strengths' in insights and insights['strengths']:
            print("  ✅ 优势维度:"            for dim, score in insights['strengths']:
                print(f"    - {dim}: {score}分")
            print()

        if 'weaknesses' in insights and insights['weaknesses']:
            print("  ⚠️  薄弱维度:"            for dim, score in insights['weaknesses']:
                print(f"    - {dim}: {score}分")

    return True


def test_report_generation():
    """测试报告生成功能"""
    print("\n" + "="*60)
    print("🧪 测试3: 报告生成")
    print("="*60)

    system = QAEvaluationSystem()
    test_qa_pairs = create_test_qa_data()[:3]  # 使用少量测试数据

    # 执行评估
    result = system.evaluate_batch_qa(test_qa_pairs, max_workers=1)

    # 生成不同格式的报告
    formats = ['json', 'html', 'markdown']
    generated_reports = []

    for fmt in formats:
        try:
            print(f"📄 生成{fmt.upper()}报告...")
            report_file = system.generate_report(result, fmt)
            generated_reports.append(report_file)
            print(f"  ✅ {report_file}")
        except Exception as e:
            print(f"  ❌ {fmt.upper()}报告生成失败: {e}")

    if generated_reports:
        print(f"\n📂 报告文件已保存在 evaluation_results/ 目录")

        # 显示HTML报告位置
        html_reports = [r for r in generated_reports if r.endswith('.html')]
        if html_reports:
            print("
💡 提示: 在浏览器中打开HTML报告查看可视化结果"            for html_report in html_reports:
                print(f"   {html_report}")

    return len(generated_reports) > 0


def test_domain_adaptation():
    """测试领域适配功能"""
    print("\n" + "="*60)
    print("🧪 测试4: 领域适配")
    print("="*60)

    # 测试不同领域的配置
    domains = {
        '机械工程': {
            '机械传动': ['轴承', '齿轮', '链条', '减速器'],
            '液压系统': ['泵', '阀', '缸', '油路'],
            '电气控制': ['PLC', '变频器', '传感器', '继电器']
        },
        '化工过程': {
            '反应系统': ['反应釜', '搅拌器', '换热器', '催化剂'],
            '分离提纯': ['蒸馏塔', '吸收塔', '离心机', '过滤器'],
            '控制仪表': ['压力表', '流量计', '温度计', 'PH计']
        }
    }

    test_question = "如何提高矿热炉的热效率？"
    test_answer = "采用新型耐火材料，优化燃烧系统，增加余热回收，改进保温结构，实施自动控制。"

    for domain_name, keywords in domains.items():
        print(f"🏭 测试领域: {domain_name}")

        # 创建领域特定的系统
        config = {'domain_keywords': keywords}
        system = QAEvaluationSystem(domain_name=domain_name, config=json.dumps(config))

        result = system.evaluate_single_qa(test_question, test_answer)

        if 'error' not in result:
            print(".3f"            print(f"   领域关键字: {list(keywords.keys())[:3]}...")  # 只显示前3个子领域
        else:
            print(f"   ❌ 评估失败: {result.get('error', '未知错误')}")

        print()
        system.cleanup()

    return True


def test_performance_stress():
    """测试性能压力"""
    print("\n" + "="*60)
    print("🧪 测试5: 性能压力测试")
    print("="*60)

    system = QAEvaluationSystem()

    # 生成大量测试数据
    base_qa_pairs = create_test_qa_data()
    large_test_data = base_qa_pairs * 10  # 50个样本

    print(f"🎯 压力测试: {len(large_test_data)} 个QA对")
    print("⚡ 使用并发处理 (4个工作线程)"

    start_time = time.time()
    result = system.evaluate_batch_qa(large_test_data, max_workers=4)
    total_time = time.time() - start_time

    print(f"\n✅ 压力测试完成!")
    print(f"⏱️  总处理时间: {total_time:.2f}秒")
    print(f"📊 平均吞吐量: {result['statistics']['performance_metrics']['throughput']} QA对/秒"
    print(f"⏱️  平均处理时间: {result['statistics']['performance_metrics']['evaluation_efficiency']} 秒/QA对"
    print(".1f"
    # 检查是否有性能问题
    if result['statistics']['performance_metrics']['throughput'] < 5:
        print("⚠️  警告: 吞吐量较低，可能存在性能问题")
    else:
        print("✅ 性能表现良好")

    return True


def run_all_tests():
    """运行所有测试"""
    print("🚀 QA评估系统综合测试")
    print("时间:", time.strftime('%Y-%m-%d %H:%M:%S'))

    tests = [
        ("单对评估", test_single_evaluation),
        ("批量评估", test_batch_evaluation),
        ("报告生成", test_report_generation),
        ("领域适配", test_domain_adaptation),
        ("性能压力", test_performance_stress)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            print(f"\n🔄 开始测试: {test_name}")
            start_time = time.time()
            success = test_func()
            duration = time.time() - start_time

            if success:
                print(".2f"                results.append((test_name, "✅ 通过", f"{duration:.2f}s"))
            else:
                print(f"❌ {test_name} 测试失败"
                results.append((test_name, "❌ 失败", f"{duration:.2f}s"))

        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, "❌ 异常", "N/A"))

    # 测试总结
    print("\n" + "="*80)
    print("📋 测试总结报告")
    print("="*80)

    passed = sum(1 for _, status, _ in results if "✅" in status)
    total = len(results)

    print(f"测试完成率: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"总测试时间: {sum(float(duration.rstrip('s')) for _, _, duration in results if duration != 'N/A'):.2f}秒")
    print()

    print("详细结果:"    for test_name, status, duration in results:
        print(f"  {status} {test_name:<12} - {duration}")

    print("\n" + "🎯 系统状态检查:")

    if passed == total:
        print("✅ 所有测试通过！QA评估系统运行正常")
        print("💡 可以使用以下命令运行系统:"        print("   python qa_evaluation_system.py --mode test  # 运行基本测试")
        print("   python qa_evaluation_system.py --mode web    # 启动Web界面")
        print("   python qa_evaluation_system.py --mode batch --input qa_data.json  # 批量评估")

    else:
        print("⚠️  部分测试失败，请检查系统配置")

    return passed == total


def main():
    """主函数"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        test_functions = {
            'single': test_single_evaluation,
            'batch': test_batch_evaluation,
            'report': test_report_generation,
            'domain': test_domain_adaptation,
            'stress': test_performance_stress
        }

        if test_name in test_functions:
            print(f"🎯 运行指定测试: {test_name}")
            test_functions[test_name]()
        else:
            print(f"❌ 未知测试名称: {test_name}")
            print(f"可用测试: {list(test_functions.keys())}")
    else:
        run_all_tests()


if __name__ == "__main__":
    main()
