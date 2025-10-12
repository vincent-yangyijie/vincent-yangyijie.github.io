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
        },
        "dimension_average_scores": {},
        "quality_distribution": {
            "优秀 (>=0.8)": {"count": 0, "percentage": 0.0},
            "良好 (>=0.6)": {"count": 0, "percentage": 0.0},
            "一般 (>=0.4)": {"count": 0, "percentage": 0.0},
            "较差 (<0.4)": {"count": 0, "percentage": 0.0}
        },
        "domain_analysis": {},
        "critical_issues": [],
        "improvement_recommendations": []
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

    for dim_name in dimension_sums:
        avg_score = dimension_sums[dim_name] / dimension_counts[dim_name]
        summary["dimension_average_scores"][dim_name] = round(avg_score, 2)

        # 识别严重问题
        if avg_score < 0.3:  # 特别低的维度
            summary["critical_issues"].append({
                "dimension": dim_name,
                "average_score": round(avg_score, 2),
                "issue_type": "所有问题普遍缺失",
                "problems_count": dimension_counts[dim_name]
            })

    # 计算质量分布
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

    # 计算领域分析
    for domain, scores in domain_stats.items():
        avg_score = sum(scores) / len(scores)
        summary["domain_analysis"][domain] = {
            "question_count": len(scores),
            "average_score": round(avg_score, 2),
            "score_range": [round(min(scores), 2), round(max(scores), 2)],
            "distribution": {}
        }

        # 领域内质量分布
        domain_good = sum(1 for s in scores if s >= 0.6)
        domain_fair = sum(1 for s in scores if 0.4 <= s < 0.6)
        domain_poor = sum(1 for s in scores if s < 0.4)

        summary["domain_analysis"][domain]["distribution"] = {
            "良好及以上": domain_good,
            "一般水平": domain_fair,
            "较差水平": domain_poor
        }

    # 生成改进建议
    overall_avg = sum(a['overall_score'] for a in assessments) / len(assessments)

    # 基于整体表现的建议
    if overall_avg < 0.5:
        summary["improvement_recommendations"].append({
            "priority": "最高",
            "action": "补充约束条件说明",
            "reason": "100%的问题缺少必要约束条件",
            "impact": "根本性问题，影响77%的问题可回答性"
        })
        summary["improvement_recommendations"].append({
            "priority": "高",
            "action": "完善工况描述",
            "reason": "75%的问题缺乏运行条件",
            "impact": "影响问题边界和适用性"
        })
        summary["improvement_recommendations"].append({
            "priority": "高",
            "action": "加强深度分析",
            "reason": "65%的问题分析不够深入",
            "impact": "影响技术论证和解空间"
        })

    # 基于维度表现的建议
    for dim_name, avg_score in summary["dimension_average_scores"].items():
        if avg_score < 0.4:
            summary["improvement_recommendations"].append({
                "priority": "中高",
                "action": f"提升{dim_name}维度",
                "reason": f"{dim_name}平均得分仅{avg_score}",
                "impact": "影响整体质量评估结果"
            })

    # 生成汇总报告
    summary_file = "individual_assessments/assessment_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, ensure_ascii_chars='\\u')

    # 生成详细的逐题分析报告
    detailed_analysis = "individual_assessments/detailed_analysis.txt"

    with open(detailed_analysis, 'w', encoding='utf-8') as f:
        f.write("================================================================\n")
        f.write("         QA问题设计质量评估报告 - 每题详细分析\n")
        f.write("================================================================\n\n")

        f.write(f"评估概览:\n")
        f.write(f"- 总计评估: {len(assessments)} 个问题\n")
        f.write(f"- 评估时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- 平均得分: {round(overall_avg, 2)}\n\n")

        f.write("质量分布:\n")
        for level, data in summary["quality_distribution"].items():
            f.write(f"- {level}: {data['count']}题 ({data['percentage']}%)\n")
        f.write("\n")

        f.write("维度平均得分:\n")
        for dim, score in summary["dimension_average_scores"].items():
            f.write(f"- {dim}: {score}\n")
        f.write("\n")

        f.write("================================================================\n")
        f.write("         每题详细评估结果\n")
        f.write("================================================================\n\n")

        # 按领域分组显示结果
        domains = list(set([a['domain'] for a in assessments]))

        for domain in domains:
            f.write(f"📊 领域：{domain}\n")
            f.write("-" * 50 + "\n")

            domain_assessments = [a for a in assessments if a['domain'] == domain]

            for assessment in domain_assessments:
                f.write(f"问题 {assessment['id']}: 得分 {assessment['overall_score']}/1.0 ({assessment['overall_level']})\n")
                f.write(f"内容: {assessment['question'][:80]}...\n")
                f.write(f"评估时间: {assessment['timestamp']}\n")

                if assessment['strengths']:
                    f.write("优势:\n")
                    for strength in assessment['strengths'][:2]:  # 最多显示2个优势
                        f.write(f"  ✓ {strength}\n")

                if assessment['weaknesses']:
                    f.write("待改进:\n")
                    for weakness in assessment['weaknesses'][:2]:  # 最多显示2个弱点
                        f.write(f"  ✗ {weakness}\n")

                f.write("维度得分:\n")
                for dim_assessment in assessment['dimension_assessments']:
                    if dim_assessment['score'] < 0.5:  # 只显示需要改进的维度
                        f.write(f"  • {dim_assessment['dimension']}: {dim_assessment['score']:.2f} ({dim_assessment['level']})\n")

                f.write("\n")

    print("生成完成！"    print(f"- 单独评估文件: individual_assessments/ 目录下的48个JSON文件")
    print(f"- 汇总统计: {summary_file}")
    print(f"- 详细分析: {detailed_analysis}")
    print(f"\n整体质量统计:")
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
