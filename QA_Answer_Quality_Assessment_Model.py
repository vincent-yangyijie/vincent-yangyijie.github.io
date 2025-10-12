#!/usr/bin/env python3
"""
QA回答（Question）质量评估模型

基于问题的质量特征，评估AI回答的质量水平
专门针对问题驱动的回答质量评估

核心理念：问题质量决定回答质量的上限
"""

import numpy as np
from qa_assessment_model import QAAssessmentModel
import json
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import re

class QAAssessmentModelWithAnswerEvaluation:
    """
    结合问题评估和回答评估的综合QA评估系统
    """

    def __init__(self, domain_name: str = "通用工程领域", domain_keywords: Dict[str, List[str]] = None):
        """初始化评估模型"""
        self.question_assessor = QAAssessmentModel(domain_name, domain_keywords)
        self.domain_name = domain_name
        self.domain_keywords = domain_keywords

        # 十维度回答质量评估权重分配 (总计100%)
        # A类：核心质量维度 (35%)
        # B类：匹配质量维度 (30%)
        # C类：方案质量维度 (35%)
        self.answer_weights = {
            # A类 - 核心质量维度 (35%)
            '准确性': 0.25,      # 答案是否正确 (25%)
            '完整性': 0.10,      # 覆盖程度 (10%)

            # B类 - 匹配质量维度 (30%)
            '一致性': 0.09,      # 与问题的匹配程度 (9%)
            '实用性': 0.08,      # 实际应用价值 (8%)
            '结构化': 0.07,      # 内容组织逻辑性 (7%)
            '简洁性': 0.06,      # 言简意赅程度 (6%)

            # C类 - 方案质量维度 (35%)
            '专业性': 0.15,      # 专业术语规范性 (15%)
            '先进性': 0.08,      # 知识技术的新旧程度 (8%)
            '实操性': 0.07,      # 实施难度 (7%)
            '实验性': 0.05       # 有成功案例 (5%)
        }

        # 质量等级标准
        self.level_thresholds = {
            'S': 9.0, 'A': 7.5, 'B': 6.0, 'C': 0.0
        }

        # 问题-回答质量映射矩阵
        self.quality_correlation_matrix = {
            # 问题质量等级 -> 回答质量期望得分范围
            '优秀': (8.0, 10.0),    # S级问题应获得高分回答
            '良好': (6.5, 8.5),    # A级问题应获得良好回答
            '一般': (5.0, 7.0),    # B级问题应获得一般回答
            '较差': (0, 6.0)       # C级问题获得基本回答即可
        }

    def assess_qa_pair(self, question: str, answer: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        评估问题-回答对的质量

        Args:
            question: 用户问题
            answer: AI回答
            context: 额外的上下文信息

        Returns:
            包含问题评估和回答评估的综合结果
        """

        # 首先评估问题质量
        question_result = self.question_assessor.assess_question(question)

        # 基于问题质量评估回答
        answer_result = self._assess_answer_based_on_question(question, answer, question_result)

        # 计算综合质量分数（使用标准化算法）
        overall_score = self._calculate_overall_qa_score_normalized(question_result, answer_result)

        # 确定质量等级
        overall_level = self._determine_overall_quality_level(overall_score)

        # 生成改进建议
        improvement_suggestions = self._generate_qa_improvement_suggestions(
            question_result, answer_result, overall_score
        )

        return {
            'question_evaluation': question_result,
            'answer_evaluation': answer_result,
            'overall_score': overall_score,
            'overall_level': overall_level,
            'qa_quality_satisfaction': self._calculate_qa_quality_satisfaction(question_result, answer_result),
            'improvement_suggestions': improvement_suggestions,
            'quality_factors': {
                'question_influence': self._quantify_question_influence(question_result),
                'answer_quality_contribution': self._quantify_answer_quality_contribution(answer_result),
                'context_appropriateness': self._assess_context_appropriateness(question, answer, context)
            }
        }

    def _assess_answer_based_on_question(self, question: str, answer: str,
                                       question_result: Dict[str, Any]) -> Dict[str, Any]:
        """基于问题质量评估回答"""

        answer_evaluation = {
            'dimension_assessments': [],
            'answer_quality_score': 0.0,
            'answer_quality_level': '',
            'assessment_criteria': []
        }

        # 获取问题质量等级
        question_level = question_result['overall_level']

        # 分析问题特征
        question_features = self._extract_question_features(question, question_result)

        # 评估回答各维度 (十维度体系，返回0-10的原始分数)
        dimension_scores_original = {
            # A类 - 核心质量维度
            '准确性': self._assess_answer_accuracy(answer, question_features),
            '完整性': self._assess_answer_completeness(answer, question_features),

            # B类 - 匹配质量维度
            '一致性': self._assess_answer_consistency(question, answer),
            '实用性': self._assess_answer_usefulness(answer, question_features),
            '结构化': self._assess_answer_structure(answer),
            '简洁性': self._assess_answer_conciseness(answer, question_features),

            # C类 - 方案质量维度
            '专业性': self._assess_answer_professionalism(answer, question_features),
            '先进性': self._assess_answer_advancement(answer, question_features),
            '实操性': self._assess_answer_operability(answer, question_features),
            '实验性': self._assess_answer_experimentality(answer, question_features)
        }

        # 转换为百分制评分 (0-100)
        dimensions = {dim: score * 10.0 for dim, score in dimension_scores_original.items()}

        # 计算加权得分 (百分制)
        weighted_score = 0.0
        for dimension, score in dimensions.items():
            weighted_score += score * self.answer_weights[dimension]

        # 维度分组（按A/B/C类）
        dimension_groups = {
            'A类_核心质量维度': {k: v for k, v in dimensions.items() if k in ['准确性', '完整性']},
            'B类_匹配质量维度': {k: v for k, v in dimensions.items() if k in ['一致性', '实用性', '结构化', '简洁性']},
            'C类_方案质量维度': {k: v for k, v in dimensions.items() if k in ['专业性', '先进性', '实操性', '实验性']}
        }

        # 计算各组分数
        group_scores = {}
        for group_name, group_dims in dimension_groups.items():
            group_weighted_score = sum(dimensions[dim] * self.answer_weights[dim] for dim in group_dims)
            group_total_weight = sum(self.answer_weights[dim] for dim in group_dims)
            group_scores[group_name] = {
                'score': round(group_weighted_score, 2),
                'weight': round(group_total_weight, 3),
                'contributions': {dim: {'score': dimensions[dim], 'weight': self.answer_weights[dim]} for dim in group_dims}
            }

        answer_evaluation['dimension_assessments'] = [
            {'dimension': dim, 'score': score, 'weight': self.answer_weights[dim]}
            for dim, score in dimensions.items()
        ]
        answer_evaluation['dimension_groups'] = group_scores
        answer_evaluation['answer_quality_score'] = weighted_score
        answer_evaluation['answer_quality_level'] = self._score_to_level(weighted_score)
        answer_evaluation['assessment_criteria'] = self._generate_answer_assessment_criteria(dimensions)

        return answer_evaluation

    def _assess_answer_accuracy(self, answer: str, question_features: Dict[str, Any]) -> float:
        """评估回答准确性 (返回0-10分)"""
        score = 8.0  # 基础分

        # 检查是否有明显错误
        error_indicators = ['不正确', '错误', '不对', '不是这样的', '我错了']
        if any(indicator in answer.lower() for indicator in error_indicators):
            score -= 3.0

        # 检查专业术语使用
        if question_features.get('technical_terms_detected', False):
            # 检查回答是否使用了相应的专业术语
            technical_keywords = question_features.get('technical_keywords', [])
            found_terms = sum(1 for term in technical_keywords if term in answer)
            if found_terms > 0:
                score += min(1.0, found_terms * 0.3)
            else:
                score -= 1.0

        # 检查事实一致性
        fact_check_score = self._check_factual_consistency(answer)
        score += fact_check_score

        return max(0.0, min(10.0, score))


    def normalize_question_score(self, question_result: Dict[str, Any]) -> float:
        """
        将问题评分标准化为0-100分百分制，与回答评分保持一致

        原始问题评分范围：0-1
        标准化到：0-100 (百分制)
        """
        original_score = question_result.get('overall_score', 0.5)
        normalized_score = original_score * 100.0  # 将0-1转换为0-100

        return round(normalized_score, 1)


    def _calculate_overall_qa_score_normalized(self, question_result: Dict[str, Any],
                                              answer_result: Dict[str, Any]) -> float:
        """重新计算综合得分，确保量纲一致"""
        # 将问题得分标准化到0-10范围
        question_score_normalized = self.normalize_question_score(question_result)
        answer_score = answer_result['answer_quality_score']

        # 问题质量对回答质量的影响权重（标准化后）
        question_influence_weight = 0.5  # 均衡权重
        answer_quality_weight = 0.5

        # 基于标准化问题质量调整权重
        if question_score_normalized >= 8.0:  # 优质问题
            question_influence_weight = 0.4
            answer_quality_weight = 0.6
        elif question_score_normalized < 4.0:  # 劣质问题
            question_influence_weight = 0.6
            answer_quality_weight = 0.4
        else:  # 一般问题
            question_influence_weight = 0.5
            answer_quality_weight = 0.5

        overall_score = (question_score_normalized * question_influence_weight +
                        answer_score * answer_quality_weight)

        return round(overall_score, 3)

    def _assess_answer_completeness(self, answer: str, question_features: Dict[str, Any]) -> float:
        """评估回答完整性"""
        score = 7.0  # 基础分

        # 基于问题复杂度调整期望
        question_complexity = question_features.get('complexity_score', 0.5)

        # 检查回答长度是否合理
        word_count = len(answer.split())
        expected_min_length = 20 + question_complexity * 80

        if word_count < expected_min_length * 0.5:
            score -= 2.0  # 回答太简短
        elif word_count > expected_min_length * 2:
            score -= 1.0  # 可能太啰嗦

        # 检查是否回答了问题的核心要素
        core_elements_covered = self._check_core_elements_coverage(answer, question_features)
        score += core_elements_covered * 2.0

        # 基于问题类型调整
        question_type = question_features.get('question_type', 'general')
        if question_type in ['how', 'why', 'what_process'] and '步骤' not in answer and '因为' not in answer:
            score -= 1.5  # 因果或过程型问题缺少相应结构

        return max(0.0, min(10.0, score))

    def _assess_answer_consistency(self, question: str, answer: str) -> float:
        """评估回答与问题的一致性"""
        score = 8.0  # 基础分

        # 检查是否直接回答了问题
        question_keywords = self._extract_key_terms_from_question(question)
        matched_keywords = sum(1 for keyword in question_keywords if keyword in answer)

        if matched_keywords == 0:
            score -= 3.0  # 完全没有回应问题要点
        elif matched_keywords / len(question_keywords) < 0.3:
            score -= 2.0  # 回应不足
        else:
            score += 1.0   # 良好回应

        # 检查逻辑连贯性
        coherence_score = self._assess_answer_coherence(answer)
        score += coherence_score

        return max(0.0, min(10.0, score))

    def _assess_answer_usefulness(self, answer: str, question_features: Dict[str, Any]) -> float:
        """评估回答的实用性"""
        score = 7.0  # 基础分

        # 检查是否提供了具体的指导
        practical_guidance_indicators = [
            '可以', '应该', '建议', '步骤', '方法', '注意事项',
            '避免', '确保', '检查', '监控', '调整', '优化'
        ]

        guidance_count = sum(1 for indicator in practical_guidance_indicators if indicator in answer)
        score += min(2.0, guidance_count * 0.5)

        # 检查是否包含量化建议
        quantitative_elements = len(self._extract_quantitative_elements(answer))
        score += min(1.0, quantitative_elements * 0.5)

        # 基于问题目的调整
        if question_features.get('purpose') == 'problem_solving':
            # 故障排除类问题应提供解决方案
            if '解决方案' in answer or '修复方法' in answer:
                score += 1.0

        return max(0.0, min(10.0, score))

    def _assess_answer_structure(self, answer: str) -> float:
        """评估回答结构化程度"""
        score = 6.0  # 基础分

        # 检查是否有逻辑结构
        structure_indicators = ['首先', '然后', '接着', '最后', '另外', '此外', '总之']
        has_structure = any(indicator in answer for indicator in structure_indicators)
        if has_structure:
            score += 2.0

        # 检查段落划分
        paragraphs = answer.split('\n\n')
        if len(paragraphs) > 1:
            score += 1.0

        # 检查编号或列表
        has_numbering = any(line.strip().startswith(str(i)) for i in range(1, 10) for line in answer.split('\n'))
        if has_numbering:
            score += 1.5

        return max(0.0, min(10.0, score))

    def _assess_answer_conciseness(self, answer: str, question_features: Dict[str, Any]) -> float:
        """评估回答简洁性"""
        score = 8.0  # 基础分

        # 检查冗余度
        word_count = len(answer.split())
        essential_word_count = self._estimate_essential_word_count(question_features)

        redundancy_ratio = word_count / max(essential_word_count, 1)
        if redundancy_ratio > 3.0:
            score -= 2.0  # 太啰嗦
        elif redundancy_ratio < 1.2:
            score -= 1.0  # 可能信息不足

        # 检查重复信息
        sentences = [s.strip() for s in answer.split('。') if s.strip()]
        duplicate_content = self._detect_duplicate_content(sentences)
        if duplicate_content > 0.3:  # 超过30%重复
            score -= 1.5

        return max(0.0, min(10.0, score))

    def _assess_answer_professionalism(self, answer: str, question_features: Dict[str, Any]) -> float:
        """评估回答专业性"""
        score = 7.0  # 基础分

        # 检查术语使用
        technical_terms = question_features.get('technical_keywords', [])
        if technical_terms:
            term_usage_frequency = sum(1 for term in technical_terms if term in answer) / len(technical_terms)
            score += term_usage_frequency * 2.0

        # 检查专业表述
        professional_indicators = ['根据', '参考', '标准', '规范', '经验表明', '研究显示']
        professional_score = min(2.0, sum(1 for ind in professional_indicators if ind in answer) * 0.5)
        score += professional_score

        # 检查避免口语化
        colloquial_terms = ['大概', '可能', '也许', '我觉得', '我认为']
        colloquial_penalty = sum(1 for term in colloquial_terms if term in answer) * 0.5
        score -= colloquial_penalty

        return max(0.0, min(10.0, score))

    def _assess_answer_advancement(self, answer: str, question_features: Dict[str, Any]) -> float:
        """评估回答先进性 - 知识技术的新旧程度"""
        score = 6.0  # 基础分

        # 检查现代技术指标
        modern_tech_indicators = [
            '最新', '先进', '创新', '新型', '高精度', '智能化', '自动化',
            '数字化', '物联网', '大数据', '云计算', '人工智能', '机器学习',
            'Industry 4.0', '工业互联网', '智能制造', '集成电路'
        ]

        modern_tech_count = sum(1 for ind in modern_tech_indicators if ind in answer)
        score += min(2.0, modern_tech_count * 0.3)

        # 检查技术发展阶段提及
        tech_stages = ['前沿', '领先', '主流', '传统', '过时', '淘汰']
        stage_mentions = sum(1 for stage in tech_stages if stage in answer)
        if stage_mentions > 0:
            score += 1.0

        # 检查是否有版本/年份信息（表示技术时效性）
        has_versions_years = bool(re.search(r'\b(20\d{2}|\b[vV]\d+|\d+\.\d+)\b', answer))
        if has_versions_years:
            score += 0.8

        # 检查对新技术趋势的提及
        emerging_trends = ['可持续', '绿色', '新能源', '低碳', '环保', '循环经济']
        trend_mentions = sum(1 for trend in emerging_trends if trend in answer)
        score += min(0.7, trend_mentions * 0.3)

        return max(0.0, min(10.0, score))

    def _assess_answer_operability(self, answer: str, question_features: Dict[str, Any]) -> float:
        """评估回答实操性 - 实施难度"""
        score = 5.0  # 基础分较低，因为实操性较难达到

        # 检查操作步骤的详细信息
        step_indicators = ['首先', '然后', '接着', '之后', '最后', '步骤', '流程']
        step_detail_score = sum(1 for ind in step_indicators if ind in answer)
        score += min(2.0, step_detail_score * 0.4)

        # 检查具体参数和数值
        quantitative_info = self._extract_quantitative_elements(answer)
        score += min(1.5, len(quantitative_info) * 0.3)

        # 检查工具/设备要求
        tool_indicators = ['使用', '利用', '采用', '配备', '工具', '设备', '仪器']
        tool_mentions = sum(1 for ind in tool_indicators if ind in answer)
        score += min(1.0, tool_mentions * 0.2)

        # 检查安全注意事项
        safety_indicators = ['注意', '小心', '危险', '安全', '防护', '警告', '谨慎']
        safety_mentions = sum(1 for ind in safety_indicators if ind in answer)
        score += min(1.0, safety_mentions * 0.4)

        # 检查时间/成本估算
        time_cost_indicators = ['时间', '成本', '费用', '周期', '预算', '工时', '投资']
        practical_factors = sum(1 for ind in time_cost_indicators if ind in answer)
        score += min(1.0, practical_factors * 0.3)

        # 基于问题复杂度调整期望
        question_complexity = question_features.get('complexity_score', 0.5)
        if question_complexity > 0.7:  # 复杂问题需要更多实操细节
            score += min(0.5, question_complexity * 0.3)

        return max(0.0, min(10.0, score))

    def _assess_answer_experimentality(self, answer: str, question_features: Dict[str, Any]) -> float:
        """评估回答实验性 - 方法方案是否有成功案例"""
        score = 4.0  # 基础分较低，因为实验验证较难

        # 检查成功案例相关表述
        success_indicators = [
            '成功案例', '实际应用', '验证有效', '效果良好', '得到证实',
            '经过测试', '实践证明', '实施成功', '运行良好', '效果显著'
        ]
        success_mentions = sum(1 for ind in success_indicators if ind in answer)
        score += min(2.0, success_mentions * 0.5)

        # 检查数据/统计证据
        statistical_indicators = ['数据', '统计', '实验结果', '测试数据', '性能指标']
        data_evidence = sum(1 for ind in statistical_indicators if ind in answer)
        score += min(1.5, data_evidence * 0.3)

        # 检查具体项目/企业名称
        # 简单检查是否有公司/项目名称（可能表示真实案例）
        company_name_pattern = r'[A-Z][a-z]+公司|[A-Z]+项目|\b[A-Z]{2,}'
        has_company_names = bool(re.search(company_name_pattern, answer))
        if has_company_names:
            score += 0.8

        # 检查实施结果描述
        result_indicators = ['结果显示', '证明了', '证实了', '达到了', '实现了', '提高了']
        result_descriptions = sum(1 for ind in result_indicators if ind in answer)
        score += min(1.2, result_descriptions * 0.4)

        # 检查引用研究/标准
        reference_indicators = ['文献', '研究', '标准', '规范', '指南', '手册']
        references = sum(1 for ind in reference_indicators if ind in answer)
        score += min(1.0, references * 0.3)

        # 检查是否有对比信息
        comparison_indicators = ['相比', '对比', '比之前', '提高了', '降低了', '减少了']
        comparisons = sum(1 for ind in comparison_indicators if ind in answer)
        score += min(0.8, comparisons * 0.2)

        return max(0.0, min(10.0, score))

    def _calculate_overall_qa_score(self, question_result: Dict[str, Any],
                                  answer_result: Dict[str, Any]) -> float:
        """计算问题-回答对的综合质量分数"""
        question_score = question_result['overall_score']
        answer_score = answer_result['answer_quality_score']

        # 问题质量对回答质量的影响权重
        question_influence_weight = 0.6
        answer_quality_weight = 0.4

        # 基于问题质量调整回答质量权重
        if question_score >= 0.8:  # 优质问题
            question_influence_weight = 0.4
            answer_quality_weight = 0.6
        elif question_score < 0.4:  # 劣质问题
            question_influence_weight = 0.7
            answer_quality_weight = 0.3

        overall_score = (question_score * question_influence_weight +
                        answer_score * answer_quality_weight)

        return round(overall_score, 3)

    def _calculate_qa_quality_satisfaction(self, question_result: Dict[str, Any],
                                         answer_result: Dict[str, Any]) -> float:
        """计算QA质量满意度"""
        question_level = question_result['overall_level']
        answer_score = answer_result['answer_quality_score']

        expected_range = self.quality_correlation_matrix.get(question_level, (0, 10))
        expected_min, expected_max = expected_range

        if answer_score >= expected_min and answer_score <= expected_max:
            satisfaction = 1.0  # 符合期望
        elif answer_score > expected_max:
            satisfaction = 0.9  # 超出期望
        elif answer_score >= expected_min * 0.7:
            satisfaction = 0.7  # 基本满意
        else:
            satisfaction = answer_score / expected_min  # 不满意

        return round(satisfaction, 2)

    def _generate_qa_improvement_suggestions(self, question_result: Dict[str, Any],
                                           answer_result: Dict[str, Any],
                                           overall_score: float) -> List[Dict[str, Any]]:
        """生成QA改进建议"""
        suggestions = []

        question_score = question_result['overall_score']
        answer_score = answer_result['answer_quality_score']

        # 问题质量优先改进
        if question_score < 0.6:
            suggestions.append({
                'target': 'question',
                'priority': 'high',
                'aspect': '问题质量',
                'suggestion': '首先提升问题质量，包含更多具体细节和技术参数',
                'expected_impact': '可显著改善回答质量'
            })

        # 回答质量改进
        if answer_score < 7.0:
            low_scoring_dimensions = [
                dim for dim in answer_result['dimension_assessments']
                if dim['score'] * dim['weight'] < 6.0
            ]

            if low_scoring_dimensions:
                top_issue = low_scoring_dimensions[0]['dimension']
                suggestions.append({
                    'target': 'answer',
                    'priority': 'medium',
                    'aspect': f'回答{top_issue}',
                    'suggestion': f'重点改善回答的{top_issue}方面',
                    'expected_impact': '提升整体回答质量'
                })

        # 系统性建议
        if overall_score < 6.0:
            suggestions.append({
                'target': 'system',
                'priority': 'high',
                'aspect': '问题-回答匹配',
                'suggestion': '检查问题理解模型，确保问题解析准确',
                'expected_impact': '从根本上提升QA质量'
            })

        return suggestions

    # 辅助方法实现
    def _extract_question_features(self, question: str, question_result: Dict[str, Any]) -> Dict[str, Any]:
        """提取问题特征"""
        return {
            'complexity_score': question_result.get('overall_score', 0.5),
            'technical_terms_detected': len(question_result.get('matched_keywords', [])) > 0,
            'technical_keywords': question_result.get('matched_keywords', []),
            'question_type': 'general',  # 可以通过更复杂的分析确定
            'purpose': 'information_seeking'
        }

    def _extract_key_terms_from_question(self, question: str) -> List[str]:
        """从问题中提取关键词"""
        # 简单实现，可以扩展为更复杂的NLP处理
        stop_words = ['的', '了', '和', '是', '在', '有', '为', '这', '那', '如何', '什么', '为什么']
        words = [w for w in question.split() if w not in stop_words and len(w) > 1]
        return words[:10]  # 最多返回10个关键词

    def _extract_quantitative_elements(self, text: str) -> List[str]:
        """提取文本中的量化元素"""
        # 匹配数字、百分比、范围等
        patterns = [
            r'\d+(?:\.\d+)?%',  # 百分比
            r'\d+',            # 整数
            r'\d+\.\d+',       # 小数
            r'\d+-\d+',        # 范围
        ]

        quantitative = []
        for pattern in patterns:
            quantitative.extend(re.findall(pattern, text))

        return list(set(quantitative))

    def _check_core_elements_coverage(self, answer: str, question_features: Dict[str, Any]) -> int:
        """检查核心要素覆盖度"""
        # 简化实现，实际应用中可以根据问题类型定制
        technical_keywords = question_features.get('technical_keywords', [])
        covered = sum(1 for keyword in technical_keywords if keyword in answer)
        return min(len(technical_keywords), covered) if technical_keywords else 1

    def _detect_duplicate_content(self, sentences: List[str]) -> float:
        """检测重复内容比例"""
        if len(sentences) < 2:
            return 0.0

        duplicate_pairs = 0
        total_pairs = len(sentences) * (len(sentences) - 1) / 2

        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                # 计算相似度（简化版）
                similarity = len(set(sentences[i].split()) & set(sentences[j].split())) / \
                           max(len(set(sentences[i].split())), len(set(sentences[j].split())))
                if similarity > 0.8:
                    duplicate_pairs += 1

        return duplicate_pairs / total_pairs if total_pairs > 0 else 0.0

    def _estimate_essential_word_count(self, question_features: Dict[str, Any]) -> int:
        """估算回答必要字数"""
        complexity = question_features.get('complexity_score', 0.5)
        base_words = 30
        return int(base_words + complexity * 100)

    def _assess_answer_coherence(self, answer: str) -> float:
        """评估回答连贯性"""
        coherence_score = 0.0

        # 检查连接词使用
        coherence_indicators = ['因此', '所以', '但是', '但是', '另外', '此外', '最后', '总之']
        coherence_count = sum(1 for ind in coherence_indicators if ind in answer)

        # 检查段落逻辑
        paragraphs = [p.strip() for p in answer.split('\n\n') if p.strip()]
        if len(paragraphs) > 1:
            coherence_score += 0.5

        coherence_score += min(0.5, coherence_count * 0.1)

        return coherence_score

    def _check_factual_consistency(self, answer: str) -> float:
        """检查事实一致性"""
        # 简化实现，实际应用中可以集成事实检查API
        inconsistency_indicators = ['显然矛盾', '自相矛盾', '前后不一']
        penalty = sum(1 for ind in inconsistency_indicators if ind in answer.lower())

        return -penalty * 0.5

    def _generate_answer_assessment_criteria(self, dimensions: Dict[str, float]) -> List[str]:
        """生成回答评估标准"""
        criteria = []
        for dimension, score in dimensions.items():
            level = self._score_to_level(score)
            criteria.append(f"{dimension}: {level}级 ({score:.1f}分)")

        return criteria

    def _score_to_level(self, score: float) -> str:
        """分数转换为等级"""
        if score >= 9.0:
            return '优秀'
        elif score >= 7.5:
            return '良好'
        elif score >= 6.0:
            return '一般'
        else:
            return '较差'

    def _determine_overall_quality_level(self, score: float) -> str:
        """确定总体质量等级"""
        return self._score_to_level(score)

    def _quantify_question_influence(self, question_result: Dict[str, Any]) -> float:
        """量化问题对质量的影响"""
        question_score = question_result['overall_score']
        # 高质量问题对最终评价有更大影响
        return question_score * 0.7

    def _quantify_answer_quality_contribution(self, answer_result: Dict[str, Any]) -> float:
        """量化回答质量贡献"""
        answer_score = answer_result['answer_quality_score']
        return answer_score * 0.3

    def _assess_context_appropriateness(self, question: str, answer: str,
                                      context: Dict[str, Any] = None) -> float:
        """评估上下文适宜性"""
        if not context:
            return 0.8  # 无上下文信息，给默认分数

        # 检查回答是否考虑了上下文
        context_keywords = context.get('keywords', [])
        context_references = sum(1 for keyword in context_keywords if keyword in answer)

        if context_keywords:
            appropriateness = context_references / len(context_keywords)
            return min(1.0, appropriateness + 0.3)  # 基础信任度
        else:
            return 0.7


def batch_assess_qa_pairs(qa_model: QAAssessmentModelWithAnswerEvaluation,
                         qa_pairs: List[Dict[str, str]],
                         output_file: str = None) -> Dict[str, Any]:
    """批量评估QA对"""

    results = []

    for i, qa_pair in enumerate(qa_pairs):
        try:
            question = qa_pair.get('question', '')
            answer = qa_pair.get('answer', '')

            assessment = qa_model.assess_qa_pair(question, answer, qa_pair.get('context'))

            qa_result = {
                'index': i + 1,
                'question': question,
                'answer': answer[:200] + '...' if len(answer) > 200 else answer,
                'assessment': assessment
            }

            results.append(qa_result)
            print(f"处理第{i+1}个QA对 - 综合得分: {assessment['overall_score']} ({assessment['overall_level']})")

        except Exception as e:
            print(f"处理第{i+1}个QA对时出错: {e}")
            continue

    # 计算统计信息
    if results:
        scores = [r['assessment']['overall_score'] for r in results]
        quality_distribution = defaultdict(int)
        for result in results:
            quality_distribution[result['assessment']['overall_level']] += 1

        statistics = {
            'total_pairs': len(results),
            'average_score': round(np.mean(scores), 2),
            'median_score': round(np.median(scores), 2),
            'quality_distribution': dict(quality_distribution),
            'score_range': {'min': round(min(scores), 2), 'max': round(max(scores), 2)}
        }

        # 保存结果
        if output_file:
            output_data = {
                'statistics': statistics,
                'results': results
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            print(f"\n批量评估完成！结果已保存到: {output_file}")

        return {
            'statistics': statistics,
            'results': results
        }
    else:
        return {'statistics': {}, 'results': []}


if __name__ == "__main__":
    # 演示代码
    qa_model = QAAssessmentModelWithAnswerEvaluation()

    # 示例QA对
    test_qa = {
        'question': '矿热炉温度传感器出现误差，如何处理？',
        'answer': """
        矿热炉温度传感器出现误差的主要处理步骤：

        1. 首先检查传感器连接线是否松动或损坏
        2. 验证传感器供电电压是否在正常范围内（通常为24VDC）
        3. 使用万用表检查传感器输出信号
        4. 如果传感器损坏，需要更换为同型号传感器
        5. 更换后重新标定传感器参数

        注意：传感器更换后需要重新校准，以确保测量精度达到±1%的要求。
        """
    }

    result = qa_model.assess_qa_pair(test_qa['question'], test_qa['answer'])

    print("=== QA回答质量评估结果 (十维度体系) ===")
    print(f"问题分数: {result['question_evaluation']['overall_score']}")
    print(f"回答分数: {result['answer_evaluation']['answer_quality_score']} ({result['answer_evaluation']['answer_quality_level']})")
    print(f"综合分数: {result['overall_score']} ({result['overall_level']})")
    print(f"质量满意度: {result['qa_quality_satisfaction']}")

    print("\n=== 回答十维度评估详情 ===")
    for group_name, group_data in result['answer_evaluation']['dimension_groups'].items():
        print(f"\n{group_name} (权重: {group_data['weight']}, 得分: {group_data['score']}):")
        for dim, dim_data in group_data['contributions'].items():
            print(f"  - {dim}: {dim_data['score']:.1f}分 (权重: {dim_data['weight']})")

    print("\n=== 改进建议 ===")
    for suggestion in result['improvement_suggestions']:
        print(f"[{suggestion['priority']}] {suggestion['target']} - {suggestion['suggestion']}")
