#!/usr/bin/env python3
"""
QA 回答质量评估系统

基于十维度评估体系的综合QA质量评估平台
支持单对评估、批量评估、Web界面和API服务
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加当前目录到路径，以便导入本地模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from QA_Answer_Quality_Assessment_Model import QAAssessmentModelWithAnswerEvaluation
except ImportError as e:
    print(f"Error importing QA assessment model: {e}")
    print("Please ensure QA_Answer_Quality_Assessment_Model.py is in the current directory")
    sys.exit(1)


class QAEvaluationSystem:
    """QA 回答质量评估系统主类"""

    def __init__(self, domain_name: str = "通用工程领域", config_file: str = None):
        """
        初始化评估系统

        Args:
            domain_name: 评估领域名称
            config_file: 配置文件路径
        """

        self.domain_name = domain_name
        self.config = self._load_config(config_file)
        self.assessment_model = self._initialize_model()

        # 设置日志
        self._setup_logging()

        # 数据存储
        self.results_history = []
        self.cache_file = Path(self.config.get('cache_file', 'evaluation_cache.json'))

        # 加载历史缓存
        self._load_cache()

        print(f"✓ QA评估系统初始化完成 - 领域: {domain_name}")

    def _load_config(self, config_file: str = None) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            'domain_name': self.domain_name,
            'log_level': 'INFO',
            'cache_file': 'evaluation_cache.json',
            'max_workers': 4,
            'output_directory': 'evaluation_results',
            'web_host': 'localhost',
            'web_port': 5000,
            'quality_thresholds': {
                'excellent': 8.5,
                'good': 7.0,
                'average': 6.0,
                'poor': 0.0
            }
        }

        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                    print(f"✓ 配置文件加载完成: {config_file}")
            except Exception as e:
                print(f"⚠ 配置文件加载失败，使用默认配置: {e}")

        return default_config

    def _initialize_model(self) -> QAAssessmentModelWithAnswerEvaluation:
        """初始化评估模型"""
        domain_keywords = self.config.get('domain_keywords', {})
        return QAAssessmentModelWithAnswerEvaluation(
            domain_name=self.domain_name,
            domain_keywords=domain_keywords
        )

    def _setup_logging(self):
        """设置日志配置"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('qa_evaluation.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('QAEvaluationSystem')

    def _load_cache(self):
        """加载缓存的评估结果"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.results_history = cache_data.get('results', [])
                    print(f"✓ 缓存数据加载完成，共 {len(self.results_history)} 条记录")
            except Exception as e:
                print(f"⚠ 缓存文件读取失败: {e}")
        else:
            print("ℹ 没有找到缓存文件，将创建新的缓存")

    def _save_cache(self):
        """保存缓存数据"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'total_results': len(self.results_history),
                'results': self.results_history[-100:]  # 只保存最近100条记录
            }

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"缓存保存失败: {e}")

    def evaluate_single_qa(self, question: str, answer: str,
                          context: Dict[str, Any] = None,
                          save_result: bool = True) -> Dict[str, Any]:
        """
        评估单个QA对

        Args:
            question: 用户问题
            answer: AI回答
            context: 上下文信息
            save_result: 是否保存结果

        Returns:
            评估结果字典
        """

        start_time = time.time()

        try:
            # 执行评估
            result = self.assessment_model.assess_qa_pair(question, answer, context)

            # 添加元数据
            result['metadata'] = {
                'evaluation_timestamp': datetime.now().isoformat(),
                'domain': self.domain_name,
                'processing_time': round(time.time() - start_time, 3),
                'input_length': {'question': len(question), 'answer': len(answer)}
            }

            # 保存到历史记录
            if save_result:
                history_record = {
                    'timestamp': datetime.now().isoformat(),
                    'question': question[:200],  # 截断长问题
                    'answer': answer[:500],      # 截断长回答
                    'result': result
                }
                self.results_history.append(history_record)

                # 定期保存缓存
                if len(self.results_history) % 10 == 0:
                    self._save_cache()

            self.logger.info(f"评估完成 - 综合得分: {result['overall_score']}")

            return result

        except Exception as e:
            error_info = {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'question_length': len(question),
                'answer_length': len(answer)
            }
            self.logger.error(f"评估失败: {e}")
            return {'error': '评估失败', 'details': error_info}

    def evaluate_batch_qa(self, qa_pairs: List[Dict[str, str]],
                         max_workers: int = None,
                         output_file: str = None) -> Dict[str, Any]:
        """
        批量评估QA对

        Args:
            qa_pairs: QA对列表
            max_workers: 最大并发数
            output_file: 输出文件路径

        Returns:
            批量评估结果统计
        """

        if max_workers is None:
            max_workers = self.config.get('max_workers', 4)

        print(f"🚀 开始批量评估 {len(qa_pairs)} 个QA对 (并发数: {max_workers})")

        results = []
        start_time = time.time()

        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.evaluate_single_qa,
                              qa.get('question', ''),
                              qa.get('answer', ''),
                              qa.get('context'),
                              save_result=False): qa
                for qa in qa_pairs
            }

            for i, future in enumerate(as_completed(futures)):
                try:
                    result = future.result()
                    qa = futures[future]
                    result['original_index'] = qa.get('index', i + 1)

                    results.append({
                        'index': i + 1,
                        'question': qa.get('question', '')[:200],
                        'answer': qa.get('answer', '')[:500],
                        'result': result
                    })

                    if (i + 1) % 10 == 0 or i == len(qa_pairs) - 1:
                        print(f"✓ 已完成 {i + 1}/{len(qa_pairs)} 个QA对评估")

                except Exception as e:
                    self.logger.error(f"批量评估出错: {e}")

        # 计算统计信息
        valid_results = [r for r in results if 'error' not in r['result']]
        scores = [r['result']['overall_score'] for r in valid_results]
        quality_levels = [r['result']['overall_level'] for r in valid_results]

        statistics = self._calculate_batch_statistics(scores, quality_levels, len(qa_pairs), time.time() - start_time)

        # 保存结果
        if output_file:
            self._save_batch_results(output_file, results, statistics)

        return {
            'statistics': statistics,
            'results': results,
            'invalid_count': len(qa_pairs) - len(valid_results)
        }

    def _calculate_batch_statistics(self, scores: List[float], quality_levels: List[str],
                                   total_pairs: int, processing_time: float) -> Dict[str, Any]:
        """计算批量评估统计信息"""

        if not scores:
            return {'error': '没有有效的评估结果'}

        from collections import Counter
        import numpy as np

        # 基本统计
        quality_distribution = dict(Counter(quality_levels))

        # 分位数统计
        score_percentiles = np.percentile(scores, [25, 50, 75])

        # 维度类别统计
        dimension_stats = self._analyze_dimension_patterns()

        statistics = {
            'total_pairs': total_pairs,
            'valid_results': len(scores),
            'processing_time': round(processing_time, 2),
            'average_score': round(np.mean(scores), 3),
            'median_score': round(np.median(scores), 3),
            'std_deviation': round(np.std(scores), 3),
            'score_range': {
                'min': round(min(scores), 3),
                'max': round(max(scores), 3),
                'percentiles': {
                    '25th': round(score_percentiles[0], 3),
                    '50th': round(score_percentiles[1], 3),
                    '75th': round(score_percentiles[2], 3)
                }
            },
            'quality_distribution': quality_distribution,
            'top_performing_questions': self._get_top_questions(scores[:10]),  # Top 10
            'dimension_insights': dimension_stats,
            'performance_metrics': {
                'throughput': round(len(scores) / processing_time, 2),  # 对/秒
                'evaluation_efficiency': round(processing_time / len(scores), 3)  # 秒/对
            }
        }

        return statistics

    def _get_top_questions(self, top_indices: List[int]) -> List[Dict[str, Any]]:
        """获取表现最好的问题样本"""
        if len(self.results_history) < len(top_indices):
            return []

        # 根据得分排序历史记录
        sorted_history = sorted(
            self.results_history,
            key=lambda x: x['result']['overall_score'],
            reverse=True
        )[:len(top_indices)]

        return [{
            'score': item['result']['overall_score'],
            'question': item['question'],
            'level': item['result']['overall_level']
        } for item in sorted_history]

    def _analyze_dimension_patterns(self) -> Dict[str, Any]:
        """分析维度表现模式"""
        recent_results = self.results_history[-50:]  # 最近50个结果

        if not recent_results:
            return {}

        dimension_scores = {}
        class_scores = {'A': [], 'B': [], 'C': []}

        for record in recent_results:
            if 'result' in record and 'answer_evaluation' in record['result']:
                answer_eval = record['result']['answer_evaluation']

                # 收集维度分数
                if 'dimension_assessments' in answer_eval:
                    for dim in answer_eval['dimension_assessments']:
                        dim_name = dim['dimension']
                        dim_score = dim['score']
                        if dim_name not in dimension_scores:
                            dimension_scores[dim_name] = []
                        dimension_scores[dim_name].append(dim_score)

                # 收集类别分数
                if 'dimension_groups' in answer_eval:
                    for group_name, group_data in answer_eval['dimension_groups'].items():
                        class_name = group_name[0]  # A/B/C
                        if class_name in class_scores:
                            class_scores[class_name].append(group_data['score'])

        # 计算平均分和趋势
        dimension_avg = {name: round(sum(scores) / len(scores), 2)
                        for name, scores in dimension_scores.items() if scores}
        class_avg = {class_name: round(sum(scores) / len(scores), 2)
                    for class_name, scores in class_scores.items() if scores}

        return {
            'dimension_averages': dimension_avg,
            'class_averages': class_avg,
            'strengths': sorted(dimension_avg.items(), key=lambda x: x[1], reverse=True)[:3],
            'weaknesses': sorted(dimension_avg.items(), key=lambda x: x[1])[:3]
        }

    def _save_batch_results(self, output_file: str, results: List[Dict], statistics: Dict):
        """保存批量评估结果"""
        try:
            output_data = {
                'evaluation_summary': {
                    'timestamp': datetime.now().isoformat(),
                    'domain': self.domain_name,
                    'total_questions': len(results)
                },
                'statistics': statistics,
                'results': results
            }

            # 确保输出目录存在
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            print(f"✓ 批量评估结果已保存: {output_file}")

        except Exception as e:
            self.logger.error(f"结果保存失败: {e}")

    def generate_report(self, results_data: Dict[str, Any],
                       report_format: str = 'json',
                       output_dir: str = None) -> str:
        """
        生成评估报告

        Args:
            results_data: 评估结果数据
            report_format: 报告格式 ('json', 'html', 'markdown')
            output_dir: 输出目录

        Returns:
            报告文件路径
        """

        if not output_dir:
            output_dir = self.config.get('output_directory', 'evaluation_results')

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"qa_evaluation_report_{timestamp}"

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        if report_format == 'json':
            report_file = f"{output_dir}/{base_filename}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, ensure_ascii=False, indent=2)

        elif report_format == 'html':
            report_file = f"{output_dir}/{base_filename}.html"
            html_content = self._generate_html_report(results_data)
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

        elif report_format == 'markdown':
            report_file = f"{output_dir}/{base_filename}.md"
            md_content = self._generate_markdown_report(results_data)
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(md_content)

        else:
            raise ValueError(f"不支持的报告格式: {report_format}")

        print(f"✓ 评估报告已生成: {report_file}")
        return report_file

    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """生成HTML报告"""
        statistics = data.get('statistics', {})

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>QA回答质量评估报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f8ff; padding: 20px; border-radius: 8px; }}
        .statistic {{ background: #fff; margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .value {{ font-size: 24px; font-weight: bold; color: #28a745; }}
        .label {{ color: #666; font-size: 14px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; }}
        .dimension-group {{ margin: 20px 0; }}
        .dimension-name {{ font-weight: bold; color: #495057; }}
        .dimension-score {{ color: #28a745; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 QA回答质量评估报告</h1>
        <p>评估领域: {self.domain_name}</p>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="statistic">
        <h2>📊 整体统计</h2>
        <div class="metric">
            <div class="value">{statistics.get('average_score', 'N/A')}</div>
            <div class="label">平均得分</div>
        </div>
        <div class="metric">
            <div class="value">{statistics.get('total_pairs', 'N/A')}</div>
            <div class="label">评估总数</div>
        </div>
        <div class="metric">
            <div class="value">{statistics.get('processing_time', 'N/A')}s</div>
            <div class="label">处理时间</div>
        </div>
        <div class="metric">
            <div class="value">{statistics.get('performance_metrics', {}).get('throughput', 'N/A')}</div>
            <div class="label">处理效率(对/秒)</div>
        </div>
        <div class="metric">
            <div class="value">{', '.join([f'{k}:{v}' for k, v in statistics.get('quality_distribution', {}).items()])}</div>
            <div class="label">质量分布</div>
        </div>
    </div>

    <div class="statistic">
        <h2>🧮 评分算法说明</h2>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h3>整体评分算法</h3>
            <p><strong>综合得分 = (问题得分 × 50% + 回答得分 × 50%)</strong></p>
            <ul>
                <li>问题得分：基于相对质量评判 (0.62 → 62.0分百分制)</li>
                <li>回答得分：基于质量等级评判 (79.41分百分制)</li>
                <li>权重分配：均衡考虑问题与回答的贡献</li>
            </ul>

            <h3>回答质量算法 (十维度)</h3>
            <p><strong>回答得分 = Σ(维度得分 × 权重)</strong></p>
            <ul>
                <li><strong>A类核心质量 (35%)</strong>:
                    <ul>
                        <li>准确性 (25%): 技术参数正确性</li>
                        <li>完整性 (10%): 内容覆盖全面性</li>
                    </ul>
                </li>
                <li><strong>B类匹配质量 (30%)</strong>:
                    <ul>
                        <li>一致性 (9%): 与问题匹配程度</li>
                        <li>实用性 (8%): 实际应用价值</li>
                        <li>结构化 (7%): 内容组织逻辑</li>
                        <li>简洁性 (6%): 表达精炼程度</li>
                    </ul>
                </li>
                <li><strong>C类方案质量 (35%)</strong>:
                    <ul>
                        <li>专业性 (15%): 专业术语规范性</li>
                        <li>先进性 (8%): 技术创新程度</li>
                        <li>实操性 (7%): 实施可行性</li>
                        <li>实验性 (5%): 证据充分性</li>
                    </ul>
                </li>
            </ul>

            <h3>质量等级标准</h3>
            <table style="width: 100%; margin: 10px 0;">
                <tr style="background: #e9ecef;">
                    <th style="padding: 8px; border: 1px solid #ddd;">得分范围</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">质量等级</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">含义</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">90-100分</td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: #28a745;"><strong>优秀</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">顶尖质量，建议推广</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">75-89分</td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: #17a2b8;"><strong>良好</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">高质量，值得借鉴</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">60-74分</td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: #ffc107;"><strong>一般</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">基本合格，有改善空间</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">0-59分</td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: #dc3545;"><strong>较差</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">质量不佳，需要优化</td>
                </tr>
            </table>

            <h3>核心理念</h3>
            <p><em>"问题质量决定回答质量的上限"</em></p>
            <p>系统的核心理念是基于问题-回答的双重视野评估，确保高质量问题的匹配答案获得更好评判，同时避免低质量问题影响到优秀回答的公平评价。</p>
        </div>
    </div>

    <div class="statistic">
        <h2>🏆 质量分布</h2>
        <table>
            <tr>
                <th>质量等级</th>
                <th>数量</th>
                <th>占比</th>
            </tr>
"""

        quality_dist = statistics.get('quality_distribution', {})
        total_count = statistics.get('total_pairs', 1)

        for level, count in quality_dist.items():
            percentage = round(count / total_count * 100, 1)
            html += f"""
            <tr>
                <td>{level}</td>
                <td>{count}</td>
                <td>{percentage}%</td>
            </tr>"""

        html += """
        </table>
    </div>

    <div class="statistic">
        <h2>📋 维度表现详细分值</h2>
        <table>
            <tr>
                <th>维度名称</th>
                <th>得分/10</th>
                <th>权重%</th>
                <th>等级</th>
                <th>说明</th>
            </tr>"""

        # 从results中提取第一个QA对的维度评估数据
        first_result = None
        for result_item in data.get('results', []):
            if 'result' in result_item and 'answer_evaluation' in result_item['result']:
                first_result = result_item['result']['answer_evaluation']
                break

        if first_result and 'dimension_assessments' in first_result:
            dimensions = first_result['dimension_assessments']
            for dim in dimensions:
                name = dim['dimension']
                score = dim['score']
                weight = dim['weight'] * 100

                if score >= 9.0:
                    level = "优秀"
                    color = "#28a745"
                elif score >= 7.5:
                    level = "良好"
                    color = "#17a2b8"
                elif score >= 6.0:
                    level = "一般"
                    color = "#ffc107"
                else:
                    level = "较差"
                    color = "#dc3545"

                # 为每个维度提供简要说明
                descriptions = {
                    "准确性": "信息正确性，技术参数准确度",
                    "完整性": "回答覆盖全面性，无重要遗漏",
                    "一致性": "与问题匹配程度，回答相关性",
                    "实用性": "实际应用价值，指导意义",
                    "结构化": "内容组织逻辑性，层次清晰",
                    "简洁性": "表达精炼度，去除冗余",
                    "专业性": "专业术语规范性，标准符合度",
                    "先进性": "技术前瞻性，创新程度",
                    "实操性": "实施可行性，操作便利性",
                    "实验性": "验证完备度，证据充分性"
                }

                desc = descriptions.get(name, "质量评估指标")

                html += f"""
                <tr>
                    <td><strong>{name}</strong></td>
                    <td><span style="color: {color}; font-weight: bold;">{score:.1f}</span></td>
                    <td>{weight:.1f}%</td>
                    <td><span style="color: {color};">{level}</span></td>
                    <td>{desc}</td>
                </tr>"""

        html += """
        </table>

        <div style="margin-top: 20px;">
            <h3>维度类别汇总</h3>
            <table>
                <tr>
                    <th>类别</th>
                    <th>加权得分</th>
                    <th>权重</th>
                    <th>说明</th>
                </tr>"""

        # 显示维度类别汇总
        if first_result and 'dimension_groups' in first_result:
            groups = first_result['dimension_groups']
            group_descriptions = {
                "A类_核心质量维度": "核心回答质量，准确性和完整性",
                "B类_匹配质量维度": "问题回答匹配程度",
                "C类_方案质量维度": "技术方案质量水平"
            }

            for group_name, group_data in groups.items():
                score = group_data['score']
                weight = group_data['weight'] * 100

                if score >= 8.5:
                    level_color = "#28a745"
                elif score >= 7.0:
                    level_color = "#17a2b8"
                elif score >= 6.0:
                    level_color = "#ffc107"
                else:
                    level_color = "#dc3545"

                # 清理分组名称显示
                display_name = group_name.replace("_", "").replace("类", "类 - ")
                desc = group_descriptions.get(group_name, "质量维度类别")

                html += f"""
                <tr>
                    <td><strong>{display_name}</strong></td>
                    <td><span style="color: {level_color}; font-weight: bold;">{score:.3f}</span></td>
                    <td>{weight:.1f}%</td>
                    <td>{desc}</td>
                </tr>"""

        html += """
            </table>
        </div>

        <div class="dimension-group" style="margin-top: 20px;">
            <h3>评估维度体系说明</h3>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <p><strong>A类核心质量维度 (35%)</strong>: 确保回答的基本质量，包括准确性和完整性</p>
                <p><strong>B类匹配质量维度 (30%)</strong>: 回答与问题的匹配程度和表达效果</p>
                <p><strong>C类方案质量维度 (35%)</strong>: 技术方案的专业水平和实用价值</p>
            </div>
        </div>
    </div>
</body>
</html>"""

        return html

    def _generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """生成Markdown报告"""
        statistics = data.get('statistics', {})

        md = f"""# QA回答质量评估报告

🧠 **评估系统**: QA回答质量评估平台  
🎯 **评估领域**: {self.domain_name}  
⏰ **报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 评估统计

| 指标 | 值 |
|------|-----|
| 平均得分 | {statistics.get('average_score', 'N/A')} |
| 评估总数 | {statistics.get('total_pairs', 'N/A')} |
| 处理时间 | {statistics.get('processing_time', 'N/A')}秒 |
| 处理效率 | {statistics.get('performance_metrics', {}).get('throughput', 'N/A')} 对/秒 |

## 🏆 质量分布

"""

        quality_dist = statistics.get('quality_distribution', {})
        total_count = statistics.get('total_pairs', 1)

        for level, count in quality_dist.items():
            percentage = round(count / total_count * 100, 1)
            md += f"- **{level}**: {count} 个 ({percentage}%)\n"

        md += "\n## 🧮 评分算法说明\n\n"
        md += "### 整体评分算法\n"
        md += "**综合得分 = (问题得分 × 50% + 回答得分 × 50%)**\n\n"
        md += "- **问题得分**: 基于相对质量评判 (原始0-1范围转换为0-100分百分制)\n"
        md += "- **回答得分**: 基于质量等级评判 (十维度加权评分的百分制)\n"
        md += "- **权重分配**: 均衡考虑问题与回答的双重视角贡献\n\n"

        md += "### 回答质量算法 (十维度体系)\n"
        md += "**回答得分 = Σ(维度得分 × 权重)**\n\n"

        md += "#### A类 - 核心质量维度 (35%)\n"
        md += "- **准确性** (25%): 保证答案正确性，技术参数准确度 - 最高权重指标\n"
        md += "- **完整性** (10%): 确保答案覆盖全面性，无重要遗漏\n\n"

        md += "#### B类 - 匹配质量维度 (30%)\n"
        md += "- **一致性** (9%): 回答与问题匹配程度，回答相关性\n"
        md += "- **实用性** (8%): 实际应用价值，指导意义\n"
        md += "- **结构化** (7%): 内容组织逻辑性，层次清晰\n"
        md += "- **简洁性** (6%): 表达精炼度，去除冗余赘述\n\n"

        md += "#### C类 - 方案质量维度 (35%)\n"
        md += "- **专业性** (15%): 专业术语规范性，标准符合度\n"
        md += "- **先进性** (8%): 技术前瞻性，创新程度\n"
        md += "- **实操性** (7%): 实施可行性，操作便利性\n"
        md += "- **实验性** (5%): 验证完备度，证据充分性\n\n"

        md += "### 质量等级标准\n"
        md += "| 得分范围 | 质量等级 | 含义 |\n"
        md += "|---------|---------|------|\n"
        md += "| 90-100分 | **优秀** | 顶尖质量，建议推广 |\n"
        md += "| 75-89分 | **良好** | 高质量，值得借鉴 |\n"
        md += "| 60-74分 | **一般** | 基本合格，有改善空间 |\n"
        md += "| 0-59分 | **较差** | 质量不佳，需要优化 |\n\n"

        md += "### 核心理念\n"
        md += "*\"问题质量决定回答质量的上限\"*\n\n"
        md += "基于问题-回答的双重视角评估，确保高质量问题的匹配答案获得更好评判，同时避免低质量问题影响到优秀回答的公平评价。\n\n"

        md += f"---\n\n报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        return md

    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            'system_name': 'QA Evaluation System',
            'version': '1.0',
            'domain': self.domain_name,
            'model_status': 'loaded',
            'cache_size': len(self.results_history),
            'config': self.config,
            'supported_features': [
                'single_qa_evaluation',
                'batch_evaluation',
                'report_generation',
                'web_interface',
                'api_service'
            ]
        }

    def cleanup(self):
        """清理系统资源"""
        self._save_cache()
        print("✓ 系统资源已清理完毕")


def create_test_qa_data() -> List[Dict[str, Any]]:
    """创建测试QA数据"""
    return [
        {
            'question': '矿热炉温度传感器出现误差，如何处理？',
            'answer': '首先检查传感器连接线是否松动或损坏，然后验证供电电压是否正常，最后更换传感器并重新标定参数。',
            'context': {'difficulty': 'medium'}
        },
        {
            'question': '如何优化PLC控制系统的响应时间？',
            'answer': '采用高速CPU模块，优化程序算法，使用高速通信协议，并实施实时监控优化控制策略。',
            'context': {'difficulty': 'high'}
        },
        {
            'question': '工业机器人出现定位偏差怎么办？',
            'answer': '检查机械传动部件的磨损情况，重新标定机器人坐标系，调整速度加速度参数。',
            'context': {'difficulty': 'medium'}
        },
        {
            'question': '变频器过载保护如何设置？',
            'answer': '根据电机额定功率设置过载保护系数，通常设置为额定电流的1.1-1.5倍，时间特性采用反时限特性。',
            'context': {'difficulty': 'low'}
        },
        {
            'question': 'SCADA系统的数据采集频率如何确定？',
            'answer': '根据过程控制要求和数据分析需求确定，通常慢变过程1秒，快变过程10-100毫秒，考虑网络带宽和存储容量。',
            'context': {'difficulty': 'medium'}
        }
    ]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='QA 回答质量评估系统')
    parser.add_argument('--mode', choices=['single', 'batch', 'web', 'test'],
                       default='test', help='运行模式')
    parser.add_argument('--domain', default='通用工程领域', help='评估领域')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--input', help='输入文件路径 (用于批量评估)')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--question', help='单个问题 (用于单对评估)')
    parser.add_argument('--answer', help='单个回答 (用于单对评估)')
    parser.add_argument('--format', choices=['json', 'html', 'markdown'],
                       default='json', help='报告格式')
    parser.add_argument('--verbose', action='store_true', help='详细输出')

    args = parser.parse_args()

    # 初始化系统
    system = QAEvaluationSystem(domain_name=args.domain, config_file=args.config)

    try:
        if args.mode == 'single':
            if not args.question or not args.answer:
                print("❌ 单对评估需要提供 --question 和 --answer 参数")
                return

            print("🧠 正在评估单个QA对...")
            result = system.evaluate_single_qa(args.question, args.answer)

            if 'error' in result:
                print(f"❌ 评估失败: {result['error']}")
                return

            print("✅ 评估完成!")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.mode == 'batch':
            if not args.input:
                print("❌ 批量评估需要提供 --input 参数 (JSON文件)")
                return

            print(f"📊 正在执行批量评估: {args.input}")
            try:
                with open(args.input, 'r', encoding='utf-8') as f:
                    qa_pairs = json.load(f)
            except Exception as e:
                print(f"❌ 输入文件读取失败: {e}")
                return

            result = system.evaluate_batch_qa(qa_pairs)

            # 生成报告
            report_file = system.generate_report(result, args.format, Path(args.output).parent if args.output else None)

            print("📋 批量评估统计信息:")
            print(json.dumps(result['statistics'], ensure_ascii=False, indent=2))
            print(f"\n📄 详细报告已生成: {report_file}")

        elif args.mode == 'web':
            print("🌐 启动Web界面...")
            start_web_interface(system)

        elif args.mode == 'test':
            print("🧪 运行测试评估...")

            # 创建测试数据
            test_qa_pairs = create_test_qa_data()
            print(f"📝 使用 {len(test_qa_pairs)} 个测试样本")

            # 执行批量评估
            result = system.evaluate_batch_qa(test_qa_pairs)

            # 生成HTML报告用于查看
            report_file = system.generate_report(result, 'html')

            print("🎯 测试评估完成!")
            print("=" * 50)
            print("📊 统计摘要:")
            stats = result['statistics']
            print(f"  • 平均得分: {stats['average_score']}")
            print(f"  • 质量分布: {stats['quality_distribution']}")
            print(f"  • 处理时间: {stats['processing_time']}秒")
            print(f"  • 处理效率: {stats['performance_metrics']['throughput']} 对/秒")
            print("=" * 50)
            print(f"📄 完整报告: {report_file}")
            print("\n💡 提示: 在浏览器中打开HTML报告文件查看详细结果")

    except Exception as e:
        print(f"❌ 系统错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

    finally:
        system.cleanup()


def start_web_interface(system: QAEvaluationSystem):
    """启动Web界面"""
    try:
        from flask import Flask, request, jsonify, render_template_string

        app = Flask(__name__)

        # HTML模板
        TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>QA评估系统</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; }
        button { background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #218838; }
        .result { margin: 20px 0; padding: 15px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; }
        .score { font-size: 24px; font-weight: bold; color: #28a745; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; }
        .metric-label { color: #666; font-size: 14px; }
        .metric-value { font-size: 18px; font-weight: bold; }
        .error { background: #f8d7da; color: #721c24; border-color: #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">🧠 QA 回答质量评估系统</h1>

        <div class="form-group">
            <label for="question">问题 (Question):</label>
            <textarea id="question" rows="3" placeholder="请输入要评估的问题..."></textarea>
        </div>

        <div class="form-group">
            <label for="answer">回答 (Answer):</label>
            <textarea id="answer" rows="6" placeholder="请输入对应的回答..."></textarea>
        </div>

        <button onclick="evaluateQA()">🚀 开始评估</button>

        <div id="result" class="result" style="display: none;">
            <h3>评估结果 (Evaluation Result)</h3>
            <div id="result-content"></div>
        </div>
    </div>

    <script>
        async function evaluateQA() {
            const question = document.getElementById('question').value;
            const answer = document.getElementById('answer').value;

            if (!question.trim() || !answer.trim()) {
                alert('请输入问题和回答！');
                return;
            }

            document.querySelector('button').disabled = true;
            document.querySelector('button').innerHTML = '处理中...';

            try {
                const response = await fetch('/api/evaluate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question, answer })
                });

                const result = await response.json();

                displayResult(result);

            } catch (error) {
                document.getElementById('result-content').innerHTML =
                    '<div class="error">评估出错: ' + error.message + '</div>';
                document.getElementById('result').style.display = 'block';
            } finally {
                document.querySelector('button').disabled = false;
                document.querySelector('button').innerHTML = '🚀 开始评估';
            }
        }

        function displayResult(result) {
            let html = '';

            if (result.error) {
                html = `<div class="error">评估失败: ${result.details}</div>`;
            } else {
                html += '<div class="metric">';
                html += `<div class="metric-value">${result.overall_score}</div>`;
                html += '<div class="metric-label">综合得分</div>';
                html += '</div>';

                html += '<div class="metric">';
                html += `<div class="metric-value">${result.overall_level}</div>`;
                html += '<div class="metric-label">质量等级</div>';
                html += '</div>';

                html += '<div class="metric">';
                html += `<div class="metric-value">${result.qa_quality_satisfaction}</div>`;
                html += '<div class="metric-label">质量满意度</div>';
                html += '</div>';

                html += '<h4>回答质量详情:</h4>';
                html += `<p>回答得分: ${result.answer_evaluation.answer_quality_score}</p>`;
                html += `<p>回答等级: ${result.answer_evaluation.answer_quality_level}</p>`;

                if (result.answer_evaluation.dimension_groups) {
                    html += '<h4>维度分类:</h4>';
                    Object.entries(result.answer_evaluation.dimension_groups).forEach(([groupName, groupData]) => {
                        html += `<p><strong>${groupName}</strong>: ${groupData.score} (权重: ${groupData.weight})</p>`;
                    });
                }
            }

            document.getElementById('result-content').innerHTML = html;
            document.getElementById('result').style.display = 'block';
        }
    </script>
</body>
</html>
"""

        @app.route('/')
        def home():
            return render_template_string(TEMPLATE)

        @app.route('/api/evaluate', methods=['POST'])
        def api_evaluate():
            data = request.get_json()
            question = data.get('question', '')
            answer = data.get('answer', '')

            if not question or not answer:
                return jsonify({'error': '缺少问题或回答'})

            result = system.evaluate_single_qa(question, answer)
            return jsonify(result)

        @app.route('/api/info')
        def api_info():
            return jsonify(system.get_system_info())

        host = system.config.get('web_host', 'localhost')
        port = system.config.get('web_port', 5000)

        print(f"🌐 Web界面启动完成: http://{host}:{port}")
        print("💡 在浏览器中打开上述地址开始使用")
        print("🔄 API接口: /api/evaluate (POST), /api/info (GET)")

        app.run(host=host, port=port, debug=True)

    except ImportError:
        print("❌ Web界面需要 Flask 支持: pip install flask")
        print("💡 或者使用命令行模式: python qa_evaluation_system.py --mode batch")
    except Exception as e:
        print(f"❌ Web界面启动失败: {e}")


if __name__ == "__main__":
    main()
