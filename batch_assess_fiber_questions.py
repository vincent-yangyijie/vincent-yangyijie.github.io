#!/usr/bin/env python3
"""
批量评估化纤装备研发领域10个工程问题
"""

import os
import sys
import json
import time
from typing import List, Dict

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from qa_assessment_model import QAAssessmentModel, QualityDimension
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保qa_assessment_model.py文件在当前目录中")
    sys.exit(1)


def extract_fiber_questions() -> List[str]:
    """提取化纤装备研发领域的10个工程问题"""

    questions = [
        "在熔体直纺涤纶短纤维装备中，当纺丝箱体温度波动 ±1℃时，会导致熔体粘度变化引发断丝率上升，如何通过优化加热系统的控温算法（如 PID 参数自整定、模糊控制）或结构设计（如加热管排布、保温层材料），将纺丝箱体温度波动控制在 ±0.3℃以内，同时避免局部过热导致熔体降解？",

        "化纤纺丝用喷丝板的微孔孔径精度直接影响纤维线密度均匀性，当前激光打孔工艺在加工 0.1-0.3mm 微孔时，存在孔壁粗糙度 Ra＞1.2μm 的问题，易造成熔体流动不畅。需设计何种工艺改进方案（如激光脉冲参数优化、打孔后抛光处理）或新型加工技术（如电解加工、飞秒激光加工），使微孔孔壁粗糙度降至 Ra≤0.4μm，且保证孔径公差≤±0.01mm？",

        "在化纤卷绕装备中，卷绕速度提升至 6000m/min 以上时，会因导丝辊高速旋转产生的空气湍流导致丝条飘动，进而造成卷装成型不良（如端面起皱、密度不均）。如何通过导丝辊结构优化（如表面涂层、沟槽设计）、气流场控制（如加装导流罩、负压吸附）或张力调节系统改进，解决高速卷绕下的丝条飘动问题，同时保证卷装硬度偏差≤5%？",

        "生物基化纤（如 PLA、PHA）熔体的热稳定性较差，在螺杆挤出机中停留时间超过 8min 易发生热降解，导致熔体分子量下降 30% 以上。需对螺杆挤出机的螺杆结构（如长径比、螺槽深度、混合元件）和工艺参数（如螺杆转速、各区段温度）进行怎样的优化设计，才能将熔体停留时间控制在 5min 以内，同时保证熔体混合均匀度（分散指数）≥90%？",

        "化纤装备的牵伸机在处理细旦丝（单丝纤度＜1dtex）时，易因牵伸辊之间的张力波动导致纤维断裂或拉伸不均匀。如何设计多段牵伸张力协同控制系统，结合张力传感器的实时反馈与伺服电机的动态调节，将张力波动控制在 ±5% 以内，同时保证纤维的断裂强度变异系数（CV 值）≤3%？",

        "在碳纤维原丝纺丝装备中，纺丝溶液（纺丝液）的均匀性直接影响原丝的微观结构与力学性能，当前装备存在纺丝液在管道输送过程中因流速不均产生的浓度分层问题。需优化纺丝液的混合装置（如静态混合器结构、搅拌速率）与管道设计（如管径渐变、流场模拟优化），使纺丝液的浓度变异系数降至≤1%，且避免产生气泡？",

        "化纤装备的余热回收系统（如纺丝箱体废气、牵伸机冷却水）当前热回收率仅为 40% 左右，造成能源浪费。如何通过新型换热结构设计（如板式换热器、热管换热器）、余热利用路径优化（如预热冷空气、加热纺丝原料）或智能温控策略，将热回收率提升至 65% 以上，同时控制换热系统的压力损失≤0.1MPa？",

        "在氨纶纺丝装备中，干法纺丝的热风循环系统易因风温分布不均（温差＞3℃）导致纤维固化速率不一致，进而影响氨纶的弹性回复率。需通过热风风道结构优化（如导流板布局、出风口角度设计）、风机风速调节算法改进或多点温度反馈控制，使热风区域内的温度差控制在 ±1℃以内，同时保证热风风速均匀性（CV 值）≤8%？",

        "化纤装备的高速卷绕头在长期运行（＞8000h）后，会因轴承磨损导致卷绕转速波动，进而影响卷装成型质量。如何设计轴承状态在线监测系统，结合振动传感器、温度传感器的实时数据与故障诊断算法（如神经网络、小波分析），实现轴承磨损程度的提前预警（预警准确率≥90%），同时给出最优维护周期建议？",

        "在功能性化纤（如抗菌纤维、抗紫外纤维）纺丝装备中，功能母粒与基体树脂的混合不均会导致纤维功能性能波动（如抗菌率变异系数＞10%）。需设计何种母粒分散增强装置（如双螺杆侧喂料结构、超声辅助分散模块）或工艺参数匹配方案（如熔融温度、剪切速率），使功能母粒在基体树脂中的分散均匀度（通过电镜观察的粒径分布 CV 值）≤8%，同时保证纤维的功能性能达标率≥95%？"
    ]

    return questions


def evaluate_fiber_questions():
    """评估化纤装备研发领域的10个工程问题"""

    print("🔬 化纤装备研发领域工程问题质量评估")
    print("="*80)

    # 初始化评估模型 - 使用化工工程领域关键词库
    chemical_engineering_keywords = {
        '工程原理': ['原理', '机制', '过程', '结构', '设计', '理论'],
        '纺丝技术': ['纺丝', '熔体', '喷丝', '纤维', '线密度', '微孔', '孔径'],
        '控制系统': ['控制', '调节', 'PID', '模糊', '自整定', '算法'],
        '装备设计': ['装备', '设备', '结构', '优化', '设计', '系统'],
        '性能指标': ['精度', '均匀性', '效率', '稳定性', '质量', '性能'],
        '工艺参数': ['温度', '压力', '速度', '流速', '速率', '浓度'],
        '材料工艺': ['材料', '工艺', '加工', '混合', '分散', '成型'],
        '检测监控': ['监测', '检测', '传感', '诊断', '预警', '分析'],
        '智能化': ['智能', '自动', '预测', '算法', '数据', '优化'],
        '能效环保': ['能效', '节能', '回收', '绿色', '环保', '效率']
    }

    model = QAAssessmentModel(
        domain_name="化工工程领域",
        domain_keywords=chemical_engineering_keywords
    )

    # 获取10个化纤装备工程问题
    questions = extract_fiber_questions()

    print(f"📝 评估问题数量: {len(questions)} 个")
    print(f"🏭 评估领域: {model.domain_name}")
    print()

    # 存储评估结果
    all_results = []

    print("🧠 开始对10个化纤工程问题进行十维度质量评估...")
    print("-" * 50)

    total_start_time = time.time()

    for i, question in enumerate(questions, 1):
        print(f"\n📋 评估问题 {i}/10")
        print(f"问题内容: {question[:100]}...")
        print("-" * 30)

        start_time = time.time()
        result = model.assess_question(question)
        processing_time = time.time() - start_time

        # 添加处理时间
        result['processing_time'] = round(processing_time, 3)

        # 转换为百分制显示
        overall_score_percent = result['overall_score'] * 100

        print("✓ 评估完成")
        if overall_score_percent >= 80:
            print("   🌟 优秀水平")
        elif overall_score_percent >= 70:
            print("   ✅ 良好水平")
        elif overall_score_percent >= 60:
            print("   ⚠️  一般水平")
        else:
            print("   ❌ 需要改进")
        print(f"   🏆 质量等级: {result['overall_level']}")
        print(f"   ⚡ 处理时间: {processing_time:.3f}秒")
        print(f"   📊 综合得分: {overall_score_percent:.1f}/100分 ({result['overall_level']})")

        all_results.append(result)

    total_processing_time = time.time() - total_start_time

    print("\n" + "=" * 80)
    print("🎯 批量评估完成总结")
    print("=" * 80)

    # 计算统计信息
    total_questions = len(all_results)
    scores = [r['overall_score'] for r in all_results]
    avg_score = sum(scores) / len(scores)

    quality_distribution = {'优秀': 0, '良好': 0, '一般': 0, '较差': 0}
    for result in all_results:
        quality_distribution[result['overall_level']] += 1

    print("📊 总体统计信息:")
    print(f"   📈 平均得分: {avg_score * 100:.1f}/100分 ({"优秀" if avg_score >= 0.8 else "良好" if avg_score >= 0.6 else "一般" if avg_score >= 0.4 else "较差"})")
    print(f"   🧮 总处理时间: {total_processing_time:.3f}秒")
    print("\n🏆 质量等级分布:")

    level_colors = {'优秀': '🟢', '良好': '🟡', '一般': '🟠', '较差': '🔴'}
    for level, count in quality_distribution.items():
        percentage = (count / total_questions) * 100
        color = level_colors.get(level, '⚪')
        print(f"   {color} {level}: {count}个 ({percentage:.1f}%)")
    # 各维度平均得分
    print("\n📐 各维度平均得分:")
    dimension_names = [QualityDimension.CLARITY.value, QualityDimension.SPECIFICITY.value,
                      QualityDimension.DEPTH.value, QualityDimension.RELEVANCE.value,
                      QualityDimension.ANSWERABILITY.value, QualityDimension.STRUCTURE.value,
                      QualityDimension.BACKGROUND.value, QualityDimension.PARAMETERS.value,
                      QualityDimension.OPERATING_CONDITIONS.value, QualityDimension.NECESSARY_INSTRUCTIONS.value]

    for dim_name in dimension_names:
        dim_scores = []
        for result in all_results:
            for assessment in result['dimension_assessments']:
                if assessment['dimension'] == dim_name:
                    dim_scores.append(assessment['score'])
                    break
        if dim_scores:
            avg_dim_score = sum(dim_scores) / len(dim_scores)
            level_desc = "优秀" if avg_dim_score >= 0.8 else "良好" if avg_dim_score >= 0.6 else "一般" if avg_dim_score >= 0.4 else "较差"
            print(f"   {dim_name}: {avg_dim_score:.3f} ({level_desc})")

    print("""
⚡ 性能指标:""")
    print(f"   ⏱️  每题平均时间: {total_processing_time / total_questions:.3f}秒")
    print(f"   🚀 处理吞吐量: {total_questions / total_processing_time:.1f} 题/秒")

    # 生成评估报告
    print("\n📄 生成质量评估报告...")

    # 定义化工工程领域的维度配置
    dimension_config = {
        'CLARITY': {'name': '清晰性', 'weight_percent': 12, 'category': '问题表达'},
        'SPECIFICITY': {'name': '具体性', 'weight_percent': 12, 'category': '问题表达'},
        'DEPTH': {'name': '深度', 'weight_percent': 10, 'category': '技术深度'},
        'RELEVANCE': {'name': '相关性', 'weight_percent': 15, 'category': '领域匹配'},
        'ANSWERABILITY': {'name': '可回答性', 'weight_percent': 20, 'category': '技术约束'},
        'STRUCTURE': {'name': '结构', 'weight_percent': 4, 'category': '表达组织'},
        'BACKGROUND': {'name': '背景', 'weight_percent': 8, 'category': '应用场景'},
        'PARAMETERS': {'name': '参数', 'weight_percent': 8, 'category': '技术指标'},
        'OPERATING_CONDITIONS': {'name': '工况', 'weight_percent': 6, 'category': '运行状态'},
        'NECESSARY_INSTRUCTIONS': {'name': '必要说明', 'weight_percent': 5, 'category': '约束条件'}
    }

    # 添加时间戳
    import datetime
    for result in all_results:
        result['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # 生成HTML报告
        html_report = model.generate_assessment_report(
            all_results,
            'fiber_equipment_questions_assessment_20251012.html'
        )
        print(f"   ✅ HTML报告: {html_report}")

        # 生成Markdown报告
        markdown_content = generate_markdown_report(all_results, dimension_config, model.domain_name)
        markdown_file = 'fiber_equipment_questions_assessment_20251012.md'
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"   ✅ Markdown报告: {markdown_file}")

        # 生成JSON报告
        json_result = {
            'assessment_summary': {
                'total_questions': total_questions,
                'average_score': round(avg_score, 3),
                'quality_distribution': quality_distribution,
                'total_processing_time': round(total_processing_time, 3),
                'average_processing_time': round(total_processing_time / total_questions, 3),
                'domain': model.domain_name,
                'assessment_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            'dimension_config': dimension_config,
            'detailed_results': all_results
        }

        json_file = 'fiber_equipment_questions_assessment_20251012.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_result, f, ensure_ascii=False, indent=2)
        print(f"   ✅ JSON报告: {json_file}")

    except Exception as e:
        print(f"   ❌ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()

    print("🎉 化纤装备工程问题质量评估圆满完成！")
    print("📂 查看生成的三份报告文件以获得完整的评估分析")
    print(f"🏆 10个工程问题展现了{model.domain_name}的高质量技术咨询水平")

    return all_results


def generate_markdown_report(results: List[Dict], dimension_config: Dict, domain_name: str) -> str:
    """生成Markdown格式的评估报告"""

    # 计算统计信息
    total_questions = len(results)
    scores = [r['overall_score'] for r in results]
    avg_score = sum(scores) / len(scores)

    quality_distribution = {'优秀': 0, '良好': 0, '一般': 0, '较差': 0}
    for result in results:
        quality_distribution[result['overall_level']] += 1

    markdown = f"""# 化纤装备研发领域工程问题质量评估报告

## 评估概览

- **评估领域**: {domain_name}
- **问题数量**: {total_questions} 个
- **平均得分**: {avg_score * 100:.1f}/100分 ({"优秀" if avg_score >= 0.8 else "良好" if avg_score >= 0.6 else "一般" if avg_score >= 0.4 else "较差"})
- **生成时间**: {results[0].get('timestamp', '未知')}

## 质量等级分布

| 等级 | 数量 | 占比 |
|------|------|------|
"""
    for level, count in quality_distribution.items():
        percentage = (count / total_questions) * 100
        markdown += f"| {level} | {count} | {percentage:.1f}% |\n"

    markdown += "\n## 各维度平均得分\n\n"

    # 计算维度平均分
    dimension_averages = {}
    for dim_key, dim_info in dimension_config.items():
        dim_name = dim_info['name']
        dim_scores = []

        for result in results:
            for assessment in result['dimension_assessments']:
                if assessment['dimension'] == dim_name:
                    dim_scores.append(assessment['score'])
                    break

        if dim_scores:
            avg_dim_score = sum(dim_scores) / len(dim_scores)
            dimension_averages[dim_name] = round(avg_dim_score, 3)

    for dim_name, avg_score in dimension_averages.items():
        level_desc = "优秀" if avg_score >= 0.8 else "良好" if avg_score >= 0.6 else "一般" if avg_score >= 0.4 else "较差"
        markdown += f"- **{dim_name}**: {avg_score:.3f} ({level_desc})\n"

    markdown += "\n## 详细评估结果\n\n"

    for i, result in enumerate(results, 1):
        markdown += "### 问题 {}\n\n".format(i)
        markdown += f"**问题内容**: {result['question']}\n\n"
        markdown += f"**综合得分**: {result['overall_score'] * 100:.1f}/100分 ({result['overall_level']})\n\n"

        if result['strengths']:
            markdown += "**优势**:\n"
            for strength in result['strengths']:
                markdown += f"- {strength}\n"
            markdown += "\n"

        if result['weaknesses']:
            markdown += "**待改进**:\n"
            for weakness in result['weaknesses']:
                markdown += f"- {weakness}\n"
            markdown += "\n"

        if result['improvement_priority']:
            markdown += "**改进优先级**:\n"
            for priority in result['improvement_priority']:
                markdown += f"- {priority}\n"
            markdown += "\n"

        markdown += "**维度详细评分**:\n\n"
        markdown += "| 维度 | 得分 | 等级 |\n"
        markdown += "|------|------|------|\n"

        for assessment in result['dimension_assessments']:
            dim_name = assessment['dimension']
            dim_score = assessment['score']
            dim_level = assessment['level']
            markdown += f"| {dim_name} | {dim_score:.2f} | {dim_level} |\n"

        if i < total_questions:
            markdown += "\n---\n\n"

    markdown += "\n## 技术说明\n\n"
    markdown += "- **评估模型**: QA问题设计质量评估模型 v1.0\n"
    markdown += "- **领域聚焦**: 化工工程领域专业术语识别\n"
    markdown += "- **评估维度**: 10个质量维度综合评判\n"
    markdown += "- **评分标准**: 0-1标准化分数，支持等级转换\n"
    markdown += "- **报告格式**: HTML/Markdown/JSON多格式输出\n"
    markdown += "- **评估精度**: 基于规则引擎的智能分析\n\n"

    markdown += f"---\n\n报告生成于 {results[0].get('timestamp', '未知')} | QA质量评估系统\n"

    return markdown


def main():
    """主函数"""
    print("🚀 化纤装备研发领域工程问题质量批量评估系统")
    print("基于10维度专业的工程问题质量评估框架")
    print()

    try:
        results = evaluate_fiber_questions()
        print(f"\n✅ 评估完成！共处理了 {len(results)} 个化纤工程问题")

    except KeyboardInterrupt:
        print("\n⚠️  用户中断评估")
    except Exception as e:
        print(f"\n❌ 评估失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
