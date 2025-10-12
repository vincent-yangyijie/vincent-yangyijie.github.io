#!/usr/bin/env python3
"""
每题单独评估的报告生成脚本
针对48个工程技术问题的独立质量评估
"""

import json
import datetime
from qa_assessment_model import QAAssessmentModel

def generate_individual_assessments(input_file="engineering_problems_48.json"):
    """生成每题单独的评估报告"""
    print("开始每题单独评估...")

    # 初始化评估模型
    model = QAAssessmentModel(domain_name="通用工程领域")

    # 读取问题文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            problems = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")
        return
    except json.JSONDecodeError:
        print(f"错误: {input_file} 不是有效的JSON文件")
        return

    print(f"共读取到 {len(problems)} 个问题")

    # 创建结果目录
    import os
    if not os.path.exists("individual_assessments"):
        os.makedirs("individual_assessments")

    # 逐题评估
    assessments = []
    domain_stats = {}

    print("开始逐题评估...")
    for i, problem in enumerate(problems, 1):
        print(f"评估问题 {i}/{len(problems)}: {problem['question'][:50]}...")

        # 评估问题
        assessment = model.assess_question(problem['question'])
        assessment['id'] = problem['id']
        assessment['domain'] = problem['domain']
        assessment['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 保存单独的JSON文件
        filename = f"individual_assessments/question_{problem['id']:02d}_assessment.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(assessment, f, ensure_ascii=False, indent=2, ensure_ascii_chars='\\u')

        # 记录统计信息
        assessments.append(assessment)

        # 统计领域分布
        domain = problem['domain']
        if domain not in domain_stats:
            domain_stats[domain] = []
        domain_stats[domain].append(assessment['overall_score'])

        if i % 10 == 0:
            print(f"已完成 {i}/{len(problems)} 个问题的评估")

    print("评估完成，开始生成汇总报告...")

    # 生成汇总统计
    summary = {
        "evaluation_overview": {
            "total_questions": len(assessments),
            "evaluation_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_version": "v1.0",
            "evaluation_framework": "基于矿热炉智能化运维领域专业评估标准"
        }
    }

    # 计算维度平均分
    dimension_sums = {}
    dimension_counts = {}
    for assessment in assessments:
        for dim_assessment in assessment['dimension_assessments']:
            dim_name = dim_assessment['dimension']
            dim_score = dim_assessment['score']

            if dim_name not in dimension_sums:
                dimension_sums[dim_name] = 0.0
                dimension_counts[dim_name] = 0
            dimension_sums[dim_name] += dim_score
            dimension_counts[dim_name] += 1

    summary["dimension_average_scores"] = {}
    for dim_name in dimension_sums:
        avg_score = dimension_sums[dim_name] / dimension_counts[dim_name]
        summary["dimension_average_scores"][dim_name] = round(avg_score, 2)

    # 计算质量分布
    summary["quality_distribution"] = {
        "优秀 (>=0.8)": {"count": 0, "percentage": 0.0},
        "良好 (>=0.6)": {"count": 0, "percentage": 0.0},
        "一般 (>=0.4)": {"count": 0, "percentage": 0.0},
        "较差 (<0.4)": {"count": 0, "percentage": 0.0}
    }

    total_questions = len(assessments)
    for assessment in assessments:
        score = assessment['overall_score']
        if score >= 0.8:
            summary["quality_distribution"]["优秀 (>=0.8)"]["count"] += 1
        elif score >= 0.6:
            summary["quality_distribution"]["良好 (>=0.6)"]["count"] += 1
        elif score >= 0.4:
            summary["quality_distribution"]["一般 (>=0.4)"]["count"] += 1
        else:
            summary["quality_distribution"]["较差 (<0.4)"]["count"] += 1

    # 计算百分比
    for level in summary["quality_distribution"]:
        count = summary["quality_distribution"][level]["count"]
        summary["quality_distribution"][level]["percentage"] = round(count / total_questions * 100, 1)

    # 生成汇总报告
    summary_file = "individual_assessments/assessment_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, ensure_ascii_chars='\\u')

    # 生成简化的文本汇总
    overall_avg = sum(a['overall_score'] for a in assessments) / len(assessments)

    print("🔔 生成完成！")
    print(f"- 单独评估文件: individual_assessments/ 目录下的48个JSON文件")
    print(f"- 汇总统计: {summary_file}")
    print()
    print("🎯 整体质量统计:")
    print(f"- 平均得分: {round(overall_avg, 2)}")
    print(f"- 优秀问题: {summary['quality_distribution']['优秀 (>=0.8)']['count']}题")
    print(f"- 良好问题: {summary['quality_distribution']['良好 (>=0.6)']['count']}题")
    print(f"- 一般问题: {summary['quality_distribution']['一般 (>=0.4)']['count']}题")
    print(f"- 较差问题: {summary['quality_distribution']['较差 (<0.4)']['count']}题")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "engineering_problems_48.json"

    generate_individual_assessments(input_file)
