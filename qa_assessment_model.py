"""
QA问题设计质量评估模型
针对工程领域问题（示例：矿热炉智能化运维）的QA问题设计质量评估系统
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np

class QualityLevel(Enum):
    EXCELLENT = "优秀"
    GOOD = "良好"
    FAIR = "一般"
    POOR = "较差"

class QualityDimension(Enum):
    CLARITY = "清晰性"
    SPECIFICITY = "具体性"
    DEPTH = "深度"
    RELEVANCE = "相关性"
    ANSWERABILITY = "可回答性"
    STRUCTURE = "结构"
    BACKGROUND = "背景"
    PARAMETERS = "参数"
    OPERATING_CONDITIONS = "工况"
    NECESSARY_INSTRUCTIONS = "必要说明"

@dataclass
class AssessmentResult:
    dimension: QualityDimension
    score: float
    level: QualityLevel
    analysis: str
    suggestions: List[str]

class QAAssessmentModel:
    """QA问题设计质量评估模型"""

    def __init__(self, domain_name="通用工程领域", domain_keywords=None):
        """初始化QA评估模型
        Args:
            domain_name: 领域名称 (默认为通用工程领域)
            domain_keywords: 自定义领域关键词字典，如果为None则使用通用工程关键词
        """
        if domain_keywords is None:
            # 通用工程问题领域关键词库
            self.domain_keywords = {
                '工程原理': ['原理', '机制', '过程', '结构', '设计', '理论', '基础'],
                '技术系统': ['系统', '设备', '设备', '装置', '设施', '平台', '模块', '组件'],
                '控制优化': ['控制', '调节', '优化', '改进', '提高', '降低', '最佳', '精准'],
                '运行维护': ['运行', '维护', '保养', '检修', '操作', '管理', '监控', '诊断'],
                '参数指标': ['参数', '指标', '性能', '效率', '质量', '精度', '可靠性', '稳定性'],
                '异常故障': ['故障', '异常', '报警', '预警', '问题', '风险', '失效', '损坏'],
                '测量检测': ['测量', '检测', '监控', '传感', '仪表', '测试', '检验'],
                '设计制造': ['设计', '制造', '加工', '装配', '材料', '工艺', '标准'],
                '智能化': ['智能', '自动', '预测', '算法', '数据', '学习', 'AI', '数字化'],
                '能效环保': ['能效', '节能', '环保', '绿色', '可持续', '资源', '排放']
            }
        else:
            self.domain_keywords = domain_keywords

        self.domain_name = domain_name
        self.parameter_patterns = [
            r'\d+(\.\d+)?\s*[°℃%MPaNm³/hkWtkJ/kgVHz]',
            r'温度|压力|流量|功率|效率|能耗|产量|速度|频率|电压',
            r'\b\d{1,3}(\.\d{1,2})?\b.*(?:<=|>=|<|>|=).*',
        ]

    def assess_question(self, question: str) -> Dict[str, any]:
        """评估单个QA问题"""
        assessments = []

        # 1. 清晰性评估
        clarity_assessment = self._assess_clarity(question)
        assessments.append(clarity_assessment)

        # 2. 具体性评估
        specificity_assessment = self._assess_specificity(question)
        assessments.append(specificity_assessment)

        # 3. 深度评估
        depth_assessment = self._assess_depth(question)
        assessments.append(depth_assessment)

        # 4. 相关性评估
        relevance_assessment = self._assess_relevance(question)
        assessments.append(relevance_assessment)

        # 5. 可回答性评估
        answerability_assessment = self._assess_answerability(question)
        assessments.append(answerability_assessment)

        # 6. 结构评估
        structure_assessment = self._assess_structure(question)
        assessments.append(structure_assessment)

        # 7. 背景评估
        background_assessment = self._assess_background(question)
        assessments.append(background_assessment)

        # 8. 参数评估
        parameters_assessment = self._assess_parameters(question)
        assessments.append(parameters_assessment)

        # 9. 工况评估
        conditions_assessment = self._assess_operating_conditions(question)
        assessments.append(conditions_assessment)

        # 10. 必要说明评估
        instructions_assessment = self._assess_necessary_instructions(question)
        assessments.append(instructions_assessment)

        # 计算综合得分
        overall_score = np.mean([assessment.score for assessment in assessments])
        overall_level = self._get_quality_level(overall_score)

        return {
            'question': question,
            'overall_score': round(overall_score, 2),
            'overall_level': overall_level.value,
            'dimension_assessments': [
                {
                    'dimension': assessment.dimension.value,
                    'score': assessment.score,
                    'level': assessment.level.value,
                    'analysis': assessment.analysis,
                    'suggestions': assessment.suggestions
                }
                for assessment in assessments
            ],
            'strengths': self._get_strengths(assessments),
            'weaknesses': self._get_weaknesses(assessments),
            'improvement_priority': self._get_improvement_priority(assessments)
        }

    def _assess_clarity(self, question: str) -> AssessmentResult:
        """评估清晰性"""
        score = 0.0
        analysis = ""
        suggestions = []

        # 检查问题结构完整性
        has_subjective_verb = any(word in question for word in ['如何', '为什么', '什么', '哪些', '多少', '怎么样'])

        if has_subjective_verb:
            score += 0.4
            analysis += "问题结构完整，包含疑问词。"
        else:
            suggestions.append("添加适当的疑问词（如如何、为什么、什么）")

        # 检查歧义词汇
        ambiguous_words = ['大概', '可能', '也许', '大约', '左右', '等等']
        has_ambiguous = any(word in question for word in ambiguous_words)
        if not has_ambiguous:
            score += 0.3
            analysis += "问题表达明确，没有歧义词汇。"
        else:
            analysis += "问题包含歧义词汇，可能影响理解。"
            suggestions.append("避免使用模糊词汇，使用具体描述")

        # 检查语言复杂度
        words = question.split()
        if len(words) < 50:  # 假设简短问题更清晰
            score += 0.3
            analysis += "问题表述简洁。"
        else:
            analysis += "问题较长，可能需要简化表达。"
            suggestions.append("简化问题表述，突出核心疑问")

        level = self._get_quality_level(score)
        if not analysis:
            analysis = "需要进一步分析问题清晰性"

        return AssessmentResult(
            dimension=QualityDimension.CLARITY,
            score=score,
            level=level,
            analysis=analysis,
            suggestions=suggestions
        )

    def _assess_specificity(self, question: str) -> AssessmentResult:
        """评估具体性"""
        score = 0.0
        analysis = ""
        suggestions = []

        # 检查是否包含具体参数或指标
        has_parameters = self._contains_parameters(question)
        if has_parameters:
            score += 0.4
            analysis += "问题包含具体参数或指标。"
        else:
            suggestions.append("添加具体的技术参数或性能指标")

        # 检查范围限制词
        scope_words = ['具体', '特定', '某个', '在什么情况下', '如何处理']
        has_scope_limitation = any(word in question for word in scope_words)
        if has_scope_limitation:
            score += 0.3
            analysis += "问题有限定范围。"
        else:
            analysis += "问题范围可能过广。"
            suggestions.append("明确问题适用的具体场景或条件")

        # 检查问题焦点
        word_count = len(question.split())
        if word_count > 10 and word_count < 30:
            score += 0.3
            analysis += "问题长度适中，焦点集中。"
        else:
            suggestions.append("精炼问题描述，聚焦核心技术点")

        level = self._get_quality_level(score)
        if not analysis:
            analysis = "需要进一步分析问题具体性"

        return AssessmentResult(
            dimension=QualityDimension.SPECIFICITY,
            score=score,
            level=level,
            analysis=analysis,
            suggestions=suggestions
        )

    def _assess_depth(self, question: str) -> AssessmentResult:
        """评估深度"""
        score = 0.0
        analysis = ""
        suggestions = []

        # 检查是否涉及因果关系
        causal_words = ['为什么', '原因', '导致', '影响', '如何影响', '关系']
        has_causal = any(word in question for word in causal_words)
        if has_causal:
            score += 0.3
            analysis += "问题涉及因果分析。"
        else:
            suggestions.append("考虑添加因果关系分析")

        # 检查是否涉及原理机制
        mechanism_words = ['原理', '机制', '过程', '如何工作', '怎么实现']
        has_mechanism = any(word in question for word in mechanism_words)
        if has_mechanism:
            score += 0.3
            analysis += "问题涉及工作原理。"
        else:
            suggestions.append("探讨底层技术原理或实现机制")

        # 检查是否涉及优化改进
        optimization_words = ['优化', '改进', '提高', '降低', '最佳', '如何提高']
        has_optimization = any(word in question for word in optimization_words)
        if has_optimization:
            score += 0.4
            analysis += "问题涉及优化改进方向。"
        else:
            suggestions.append("考虑性能优化或改进方案")

        level = self._get_quality_level(score)
        if not analysis:
            analysis = "需要进一步分析问题深度"

        return AssessmentResult(
            dimension=QualityDimension.DEPTH,
            score=score,
            level=level,
            analysis=analysis,
            suggestions=suggestions
        )

    def _assess_relevance(self, question: str) -> AssessmentResult:
        """评估相关性"""
        score = 0.0
        analysis = ""
        suggestions = []
        relevance_keywords = 0

        # 检查各领域关键词匹配度
        for category, keywords in self.domain_keywords.items():
            if any(keyword in question for keyword in keywords):
                score += 0.15
                relevance_keywords += 1
                analysis += f"包含{category}相关关键词。"

        if relevance_keywords == 0:
            analysis = f"未发现{self.domain_name}相关关键词。"
            suggestions.append(f"明确问题与{self.domain_name}的关联")
            suggestions.append("添加领域相关技术术语")

        score = min(score, 1.0)  # 限制最大分数为1.0

        level = self._get_quality_level(score)

        return AssessmentResult(
            dimension=QualityDimension.RELEVANCE,
            score=score,
            level=level,
            analysis=analysis,
            suggestions=suggestions
        )

    def _assess_answerability(self, question: str) -> AssessmentResult:
        """评估可回答性"""
        score = 0.0
        analysis = ""
        suggestions = []

        # 检查是否有明确的技术指向
        technical_indicators = ['温度', '压力', '效率', '功率', '能耗', '产量', '监控']
        has_technical = any(indicator in question for indicator in technical_indicators)
        if has_technical:
            score += 0.3
            analysis += "问题涉及可量化技术指标。"
        else:
            suggestions.append("添加可量化或可验证的技术指标")

        # 检查问题是否过于主观
        subjective_words = ['最好', '应该', '必须', '总是', '永远']
        has_subjective = any(word in question for word in subjective_words)
        if not has_subjective:
            score += 0.3
            analysis += "问题相对客观。"
        else:
            analysis += "问题包含主观判断。"
            suggestions.append("减少主观表述，使用事实性问题")

        # 检查是否基于现有知识可回答
        has_parameters = self._contains_parameters(question)
        has_conditions = self._contains_operating_conditions(question)
        if has_parameters or has_conditions:
            score += 0.4
            analysis += "问题基于具体参数和条件，可操作性强。"
        else:
            suggestions.append("提供具体的参数范围或运行条件")

        level = self._get_quality_level(score)

        return AssessmentResult(
            dimension=QualityDimension.ANSWERABILITY,
            score=score,
            level=level,
            analysis=analysis,
            suggestions=suggestions
        )

    def _assess_structure(self, question: str) -> AssessmentResult:
        """评估结构"""
        score = 0.0
        analysis = ""
        suggestions = []

        # 检查问题组成部分
        parts = self._analyze_question_parts(question)
        if len(parts) >= 2:
            score += 0.4
            analysis += f"问题包含{len(parts)}个明确部分。"
        else:
            suggestions.append("将复杂问题分解为多个具体子问题")

        # 检查逻辑连贯性
        connector_words = ['和', '与', '或', '以及', '但是', '然而']
        has_connectors = any(word in question for word in connector_words)
        if has_connectors:
            score += 0.3
            analysis += "问题逻辑连贯。"
        else:
            suggestions.append("使用连接词增强问题逻辑性")

        # 检查层次感
        sentences = re.split(r'[。！？]', question)
        if len(sentences) > 1:
            score += 0.3
            analysis += "问题层次分明。"
        else:
            suggestions.append("分层表述问题，提高可读性")

        level = self._get_quality_level(score)

        return AssessmentResult(
            dimension=QualityDimension.STRUCTURE,
            score=score,
            level=level,
            analysis=analysis,
            suggestions=suggestions
        )

    def _assess_background(self, question: str) -> AssessmentResult:
        """评估背景"""
        score = 0.0
        analysis = ""
        suggestions = []

        # 检查是否明确应用场景
        scenario_words = ['在生产中', '运行时', '维护期间', '故障时', '启动过程', '高温高压环境下', '高温', '高压', '生产环境', '运行环境']
        has_scenario = any(word in question for word in scenario_words)
        if has_scenario:
            score += 0.3
            analysis += "明确了应用场景。"
        else:
            suggestions.append("描述具体应用场景或业务背景")

        # 检查是否明确目标
        objective_words = ['为了', '目的是', '目标是', '实现', '达到', '周期', '多少', '如何']
        has_objective = any(word in question for word in objective_words)
        if has_objective:
            score += 0.3
            analysis += "明确了业务目标。"
        else:
            suggestions.append("阐述问题解决后的预期效果或业务价值")

        # 检查系统层次
        system_words = ['系统', '设备', '子系统', '模块', '组件', '矿热炉', '智能化']
        has_system = any(word in question for word in system_words)
        if has_system:
            score += 0.4
            analysis += "明确了系统层次。"
        else:
            suggestions.append("指明涉及的系统层次或组件")

        level = self._get_quality_level(score)

        return AssessmentResult(
            dimension=QualityDimension.BACKGROUND,
            score=score,
            level=level,
            analysis=analysis,
            suggestions=suggestions
        )

    def _assess_parameters(self, question: str) -> AssessmentResult:
        """评估参数"""
        score = 0.0
        analysis = ""
        suggestions = []

        # 检查定量参数
        quantitative_patterns = [
            r'\d+(\.\d+)?\s*[°℃%MPaNm³/hkWtkJ/kg]',
            r'\b\d{1,3}(\.\d{1,2})?\b',
        ]

        has_quantitative = False
        for pattern in quantitative_patterns:
            if re.search(pattern, question):
                has_quantitative = True
                break

        if has_quantitative:
            score += 0.4
            analysis += "包含定量参数。"
        else:
            suggestions.append("添加具体的数值参数或量纲")

        # 检查参数完整性
        parameter_types = ['温度', '压力', '流量', '功率', '效率']
        has_parameter_types = any(pt in question for pt in parameter_types)
        if has_parameter_types:
            score += 0.3
            analysis += "参数类型明确。"
        else:
            suggestions.append("明确参数类型和单位")

        # 检查参数关系
        relation_words = ['高于', '低于', '超过', '达到', '保持在', '控制在']
        has_relations = any(word in question for word in relation_words)
        if has_relations:
            score += 0.3
            analysis += "明确了参数关系和阈值。"
        else:
            suggestions.append("添加参数的控制范围或阈值条件")

        level = self._get_quality_level(score)

        return AssessmentResult(
            dimension=QualityDimension.PARAMETERS,
            score=score,
            level=level,
            analysis=analysis,
            suggestions=suggestions
        )

    def _assess_operating_conditions(self, question: str) -> AssessmentResult:
        """评估工况"""
        score = 0.0
        analysis = ""
        suggestions = []

        # 检查运行状态
        status_words = ['正常运行', '故障', '报警', '启动', '停机', '检修']
        has_status = any(word in question for word in status_words)
        if has_status:
            score += 0.3
            analysis += "明确了运行状态。"
        else:
            suggestions.append("描述设备的当前运行状态")

        # 检查环境条件
        env_words = ['高温', '高压', '负荷', '季节', '天气', '外部条件']
        has_environment = any(word in question for word in env_words)
        if has_environment:
            score += 0.3
            analysis += "考虑了环境条件。"
        else:
            suggestions.append("考虑外部环境因素的影响")

        # 检查时序特征
        time_words = ['期间', '时候', '时', '过程', '阶段', '持续']
        has_timing = any(word in question for word in time_words)
        if has_timing:
            score += 0.4
            analysis += "包含时序特征。"
        else:
            suggestions.append("描述事件发生的时序或持续时间")

        level = self._get_quality_level(score)

        return AssessmentResult(
            dimension=QualityDimension.OPERATING_CONDITIONS,
            score=score,
            level=level,
            analysis=analysis,
            suggestions=suggestions
        )

    def _assess_necessary_instructions(self, question: str) -> AssessmentResult:
        """评估必要说明"""
        score = 0.0
        analysis = ""
        suggestions = []

        # 检查约束条件
        constraint_words = ['必须', '要求', '限制', '条件', '前提']
        has_constraints = any(word in question for word in constraint_words)
        if has_constraints:
            score += 0.3
            analysis += "明确了约束条件。"
        else:
            suggestions.append("说明必要的约束条件或前提假设")

        # 检查范围限定
        scope_words = ['针对', '适用于', '在...情况下', '当...时']
        has_scope = any(word in question for word in scope_words)
        if has_scope:
            score += 0.3
            analysis += "限定了适用范围。"
        else:
            suggestions.append("明确问题的适用范围和边界条件")

        # 检查假设前提
        assumption_words = ['假设', '基于', '前提', '已知', '已配置']
        has_assumptions = any(word in question for word in assumption_words)
        if has_assumptions:
            score += 0.4
            analysis += "明确了假设前提。"
        else:
            suggestions.append("说明必要的假设前提或已知条件")

        level = self._get_quality_level(score)

        return AssessmentResult(
            dimension=QualityDimension.NECESSARY_INSTRUCTIONS,
            score=score,
            level=level,
            analysis=analysis,
            suggestions=suggestions
        )

    def _get_quality_level(self, score: float) -> QualityLevel:
        """根据分数确定质量等级"""
        if score >= 0.8:
            return QualityLevel.EXCELLENT
        elif score >= 0.6:
            return QualityLevel.GOOD
        elif score >= 0.4:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR

    def _contains_parameters(self, question: str) -> bool:
        """检查是否包含参数"""
        for pattern in self.parameter_patterns:
            if re.search(pattern, question):
                return True
        return False

    def _contains_operating_conditions(self, question: str) -> bool:
        """检查是否包含工况信息"""
        condition_words = ['正常', '异常', '故障', '报警', '运行', '停止', '启动']
        return any(word in question for word in condition_words)

    def _analyze_question_parts(self, question: str) -> List[str]:
        """分析问题组成部分"""
        parts = []
        # 按标点符号分割问题部分
        separators = r'[，。！？；：]'
        segments = re.split(separators, question)
        parts = [seg.strip() for seg in segments if seg.strip()]
        return parts

    def _get_strengths(self, assessments: List[AssessmentResult]) -> List[str]:
        """获取问题优势"""
        strengths = []
        for assessment in assessments:
            if assessment.level in [QualityLevel.EXCELLENT, QualityLevel.GOOD]:
                strengths.append(f"{assessment.dimension.value}: {assessment.analysis}")
        return strengths[:3]  # 返回前3个优势

    def _get_weaknesses(self, assessments: List[AssessmentResult]) -> List[str]:
        """获取问题弱点"""
        weaknesses = []
        for assessment in assessments:
            if assessment.level in [QualityLevel.POOR, QualityLevel.FAIR]:
                weaknesses.append(f"{assessment.dimension.value}: {assessment.analysis}")
        return weaknesses[:3]  # 返回前3个弱点

    def _get_improvement_priority(self, assessments: List[AssessmentResult]) -> List[str]:
        """获取改进优先级"""
        low_score_assessments = sorted(
            [a for a in assessments if a.score < 0.6],
            key=lambda x: x.score
        )
        return [f"{a.dimension.value} ({a.level.value})" for a in low_score_assessments[:3]]

    def batch_assess_from_file(self, input_file: str) -> List[Dict[str, any]]:
        """从文件批量评估QA问题"""
        results = []

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                questions = json.load(f)

            if isinstance(questions, list):
                for question in questions:
                    if isinstance(question, str):
                        result = self.assess_question(question)
                        results.append(result)
                    elif isinstance(question, dict) and 'question' in question:
                        result = self.assess_question(question['question'])
                        results.append(result)
            else:
                print(f"Error: {input_file} 格式不正确，应为问题列表")
                return []

        except FileNotFoundError:
            print(f"Error: 文件 {input_file} 不存在")
            return []
        except json.JSONDecodeError:
            print(f"Error: {input_file} 不是有效的JSON文件")
            return []

        return results

    def generate_assessment_report(self, results: List[Dict[str, any]], output_file: str = "assessment_report.html"):
        """生成评估报告"""
        html_content = self._generate_html_report(results)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_file

    def _generate_html_report(self, results: List[Dict[str, any]]) -> str:
        """生成HTML格式的评估报告"""
        # 计算统计数据
        total_questions = len(results)
        score_distribution = {'优秀': 0, '良好': 0, '一般': 0, '较差': 0}

        dimension_avg_scores = {}
        for dimension in QualityDimension:
            dimension_avg_scores[dimension.value] = []

        for result in results:
            score_distribution[result['overall_level']] += 1

            for assessment in result['dimension_assessments']:
                dimension_name = assessment['dimension']
                dimension_avg_scores[dimension_name].append(assessment['score'])

        # 计算维度平均分
        for dimension in dimension_avg_scores:
            scores = dimension_avg_scores[dimension]
            dimension_avg_scores[dimension] = round(np.mean(scores), 2) if scores else 0.0

        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QA问题设计质量评估报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .summary {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background-color: #3498db;
            color: white;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
        }}
        .excellent {{ background-color: #27ae60; }}
        .good {{ background-color: #2ecc71; }}
        .fair {{ background-color: #f39c12; }}
        .poor {{ background-color: #e74c3c; }}
        .question-card {{
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 20px;
            padding: 20px;
        }}
        .question-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .question-text {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .overall-score {{
            font-size: 20px;
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 3px;
            color: white;
        }}
        .dimension-scores {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }}
        .dimension-score {{
            background-color: #f8f9fa;
            padding: 8px;
            border-radius: 3px;
            text-align: center;
            font-size: 14px;
        }}
        .strengths, .weaknesses {{
            margin-top: 15px;
        }}
        .strengths {{
            color: #27ae60;
        }}
        .weaknesses {{
            color: #e74c3c;
        }}
        .suggestions {{
            margin-top: 10px;
            padding-left: 20px;
        }}
        .chart-container {{
            margin: 30px 0;
            text-align: center;
        }}
        .footer {{
            text-align: center;
            color: #7f8c8d;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>QA问题设计质量评估报告</h1>
        <div class="summary">
            <h2>评估概览</h2>
            <p>总计评估了 <strong>{total_questions}</strong> 个QA问题</p>
            <p>评估时间: {results[0]['timestamp'] if results and 'timestamp' in results[0] else '未知'}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card excellent">
                <h3>优秀</h3>
                <div style="font-size: 24px;">{score_distribution['优秀']}</div>
                <div>({100 * score_distribution['优秀'] // total_questions if total_questions > 0 else 0}%)</div>
            </div>
            <div class="stat-card good">
                <h3>良好</h3>
                <div style="font-size: 24px;">{score_distribution['良好']}</div>
                <div>({100 * score_distribution['良好'] // total_questions if total_questions > 0 else 0}%)</div>
            </div>
            <div class="stat-card fair">
                <h3>一般</h3>
                <div style="font-size: 24px;">{score_distribution['一般']}</div>
                <div>({100 * score_distribution['一般'] // total_questions if total_questions > 0 else 0}%)</div>
            </div>
            <div class="stat-card poor">
                <h3>较差</h3>
                <div style="font-size: 24px;">{score_distribution['较差']}</div>
                <div>({100 * score_distribution['较差'] // total_questions if total_questions > 0 else 0}%)</div>
            </div>
        </div>

        <h2>各维度平均得分</h2>
        <div class="dimension-scores">
"""

        for dimension, avg_score in dimension_avg_scores.items():
            color_class = ''
            if avg_score >= 0.8:
                color_class = 'excellent'
            elif avg_score >= 0.6:
                color_class = 'good'
            elif avg_score >= 0.4:
                color_class = 'fair'
            else:
                color_class = 'poor'

            html_template += f"""
            <div class="dimension-score {color_class}">
                <div>{dimension}</div>
                <div style="font-size: 18px; font-weight: bold;">{avg_score:.2f}</div>
            </div>
"""

        html_template += """
        </div>

        <h2>详细评估结果</h2>
"""

        for i, result in enumerate(results, 1):
            overall_level = result['overall_level']
            level_class = overall_level.lower() if overall_level in ['优秀', '良好', '一般', '较差'] else 'fair'

            html_template += f"""
        <div class="question-card">
            <div class="question-header">
                <div class="question-text">问题 {i}</div>
                <div class="overall-score {level_class}">{result['overall_score'] * 100:.1f}/100分 ({overall_level})</div>
            </div>
            <p>{result['question']}</p>

            <div class="dimension-scores">
"""

            for assessment in result['dimension_assessments']:
                dim_level = assessment['level']
                dim_class = dim_level.lower() if dim_level in ['优秀', '良好', '一般', '较差'] else 'fair'
                html_template += f"""
                <div class="dimension-score {dim_class}">
                    <div>{assessment['dimension']}</div>
                    <div style="font-size: 16px; font-weight: bold;">{assessment['score']:.2f}</div>
                </div>
"""

            html_template += """
            </div>
"""

            if result['strengths']:
                html_template += """
            <div class="strengths">
                <strong>优势:</strong>
                <ul>
"""
                for strength in result['strengths']:
                    html_template += f"                    <li>{strength}</li>\n"

                html_template += """
                </ul>
            </div>
"""

            if result['weaknesses']:
                html_template += """
            <div class="weaknesses">
                <strong>待改进:</strong>
                <ul>
"""
                for weakness in result['weaknesses']:
                    html_template += f"                    <li>{weakness}</li>\n"

                html_template += """
                </ul>
            </div>
"""

            if result['improvement_priority']:
                html_template += """
            <div>
                <strong>改进优先级:</strong>
                <ul>
"""
                for priority in result['improvement_priority']:
                    html_template += f"                    <li>{priority}</li>\n"

                html_template += """
                </ul>
            </div>
"""

            html_template += """
        </div>
"""

        html_template += """
        <div class="footer">
            <p>报告生成时间: 2025-10-12 | QA问题设计质量评估系统 v1.0</p>
            <p>基于矿热炉智能化运维领域专业评估框架</p>
        </div>
    </div>
</body>
</html>
"""

        return html_template

def main():
    """主函数：演示QA评估模型"""
    import sys
    import datetime

    model = QAAssessmentModel()

    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--batch' and len(sys.argv) > 2:
            # 批量处理模式
            input_file = sys.argv[2]
            output_report = sys.argv[3] if len(sys.argv) > 3 else "assessment_report.html"

            print(f"批量处理文件: {input_file}")
            results = model.batch_assess_from_file(input_file)

            if results:
                # 添加时间戳
                for result in results:
                    result['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 生成报告
                report_file = model.generate_assessment_report(results, output_report)
                print(f"评估报告已生成: {report_file}")
                print(f"总计处理了 {len(results)} 个问题")

                # 显示总体统计
                total_score = sum(r['overall_score'] for r in results) / len(results)
                level_counts = {}
                for r in results:
                    level = r['overall_level']
                    level_counts[level] = level_counts.get(level, 0) + 1

                print(f"平均得分: {total_score:.2f}")
                print("质量等级分布:")
                for level, count in level_counts.items():
                    percentage = (count / len(results)) * 100
                    print(f"{level}: {count}个 ({percentage:.1f}%)")

            return

    # 单问题演示模式
    print("=== QA问题设计质量评估系统 ===")
    print(f"(基于{model.domain_name})")
    print()

    # 示例问题
    sample_questions = [
        "矿热炉运行时，如何监控炉温参数？",
        "为什么矿热炉智能化系统会产生 false positive 报警，该如何优化？",
        "在高温高压环境下，矿热炉的维护周期是多少？",
        "矿热炉的能耗优化需要考虑哪些因素？"
    ]

    for i, question in enumerate(sample_questions, 1):
        print(f"问题 {i}: {question}")
        print("-" * 50)

        result = model.assess_question(question)

        print(f"综合得分: {result['overall_score']}/1.0 ({result['overall_level']})")
        print()

        if result['strengths']:
            print("优势:")
            for strength in result['strengths']:
                print(f"  ✓ {strength}")
            print()

        if result['weaknesses']:
            print("待改进:")
            for weakness in result['weaknesses']:
                print(f"  ✗ {weakness}")
            print()

        if result['improvement_priority']:
            print("改进优先级:")
            for priority in result['improvement_priority']:
                print(f"  • {priority}")
            print()

        # 显示详细评估结果
        print("详细评估:")
        for assessment in result['dimension_assessments']:
            print(f"  {assessment['dimension']}: {assessment['score']:.2f} ({assessment['level']})")
            if assessment['suggestions']:
                for suggestion in assessment['suggestions'][:1]:  # 只显示最重要的建议
                    print(f"    建议: {suggestion}")
        print()

        # 保存评估结果到JSON文件
        output_file = f"qa_assessment_result_{i}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"详细结果已保存到: {output_file}")
        print("=" * 60)
        print()

    # 提示如何使用批量处理
    print("批量处理使用说明:")
    print("python qa_assessment_model.py --batch sample_questions.json [report.html]")
    print()

    # 尝试批量处理示例
    print("正在进行批量评估示例...")
    batch_results = model.batch_assess_from_file("sample_questions.json")
    if batch_results:
        # 添加时间戳
        for result in batch_results:
            result['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 生成报告
        report_file = model.generate_assessment_report(batch_results, "assessment_report.html")

        # 简单统计
        total_score = sum(r['overall_score'] for r in batch_results) / len(batch_results)
        level_counts = {}
        for r in batch_results:
            level = r['overall_level']
            level_counts[level] = level_counts.get(level, 0) + 1

        print(f"平均得分: {total_score:.2f}")
        print(f"报表已生成: {report_file}")

if __name__ == "__main__":
    main()
