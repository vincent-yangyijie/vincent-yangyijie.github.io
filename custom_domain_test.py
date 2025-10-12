#!/usr/bin/env python3
"""
测试自定义领域关键词功能
"""

from qa_assessment_model import QAAssessmentModel

def test_custom_domain():
    """测试自定义领域关键词功能"""

    # 定义机械工程领域的关键词库
    mechanical_keywords = {
        '机械结构': ['结构', '机构', '传动', '轴承', '齿轮', '轴', '杆', '梁'],
        '动力系统': ['电机', '发动机', '动力', '扭矩', '转速', '功率', '效率'],
        '制造工艺': ['加工', '焊接', '切削', '铸造', '锻造', '模具', '装配'],
        '材料性能': ['强度', '硬度', '韧性', '疲劳', '腐蚀', '耐磨', '导电'],
        '控制系统': ['PLC', '伺服', '传感器', '变频器', '控制器', '自动化'],
        '维护保养': ['润滑', '保养', '检修', '更换', '维修', '故障'],
        '安全性': ['安全', '防护', '危险', '风险', '应急', '规范'],
        '检测监测': ['振动', '温度', '压力', '流量', '位移', '应变']
    }

    # 创建机械工程领域的评估模型
    mechanical_model = QAAssessmentModel(domain_name="机械工程领域", domain_keywords=mechanical_keywords)

    # 测试问题
    test_questions = [
        "电机轴的振动频率如何影响轴承寿命？",
        "如何优化齿轮传动系统的效率和噪音？",
        "铸造工艺中常见的缺陷有哪些，如何预防？",
        "伺服电机控制系统的精度调校方法是什么？"
    ]

    print("=== 机械工程问题质量评估测试 ===")
    print()

    for i, question in enumerate(test_questions, 1):
        print(f"问题 {i}: {question}")
        print("-" * 60)

        result = mechanical_model.assess_question(question)
        print(".2f")
        print(f"质量等级: {result['overall_level']}")
        print()

        relevance_assessment = None
        for assessment in result['dimension_assessments']:
            if assessment['dimension'] == '相关性':
                relevance_assessment = assessment
                break

        if relevance_assessment:
            print(f"相关性分析: {relevance_assessment['analysis']}")
            print(".2f")

        print("=" * 60)
        print()

    # 比较不同领域设置的影响
    print("=== 对比不同领域设置的影响 ===")

    # 使用通用工程领域模型重新评估第一个问题
    general_model = QAAssessmentModel()  # 默认通用工程领域

    question = test_questions[0]
    print(f"测试问题: {question}")
    print()

    mechanical_result = mechanical_model.assess_question(question)
    general_result = general_model.assess_question(question)

    print(".2f")
    print(".2f")
    print()

    # 比较相关性得分
    mech_rel = None
    gen_rel = None

    for assessment in mechanical_result['dimension_assessments']:
        if assessment['dimension'] == '相关性':
            mech_rel = assessment
            break

    for assessment in general_result['dimension_assessments']:
        if assessment['dimension'] == '相关性':
            gen_rel = assessment
            break

    if mech_rel and gen_rel:
        print("相关性维度对比:")
        print(".2f")
        print(".2f")
        print()
        print(f"机械工程分析: {mech_rel['analysis']}")
        print(f"通用工程分析: {gen_rel['analysis']}")

if __name__ == "__main__":
    test_custom_domain()
