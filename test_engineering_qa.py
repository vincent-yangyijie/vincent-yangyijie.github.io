#!/usr/bin/env python3
"""
测试工程技术QA评估 - 使用提供的测试样例
"""

import os
import sys
import json
import time

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from qa_evaluation_system import QAEvaluationSystem
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保QA评估系统文件在当前目录中")
    sys.exit(1)


def create_test_qa_from_docx():
    """从文档内容创建测试QA对"""

    question = """在熔体直纺涤纶短纤维装备中，当纺丝箱体温度波动 ±1℃时，会导致熔体粘度变化引发断丝率上升，如何通过优化加热系统的控温算法（如 PID 参数自整定、模糊控制）或结构设计（如加热管排布、保温层材料），将纺丝箱体温度波动控制在 ±0.3℃以内，同时避免局部过热导致熔体降解？"""

    answer = """附加评价可选

熔体直纺涤纶短纤维装备中纺丝箱体温度精确控制策略

在熔体直纺涤纶短纤维生产过程中，纺丝箱体温度的稳定性是决定产品质量与生产连续性的核心工艺参数。用户提出的问题聚焦于：当箱体温度波动±1℃时，会因熔体粘度变化导致断丝率显著上升2。这一现象的根本原因在于聚酯（PET）熔体具有显著的温度-粘度依赖性，温度波动直接改变其流变性能，进而影响纺丝细流的均匀性与可纺性3。

本问题的核心诉求是将温度波动控制在±0.3℃以内，这要求控温系统具备极高的精度与抗干扰能力29。同时，问题还提出了一个关键的约束条件——避免局部过热导致熔体降解。这表明解决方案不能简单地通过提高整体加热功率来实现，而必须在实现全局精确控温的同时，确保温度场的均匀性28。

因此，该问题可拆解为两个相互关联的子问题：（1）如何通过优化控温算法提升系统的动态响应与稳态精度；（2）如何通过结构设计优化热场分布，消除局部热点28。解决这一问题需要综合运用控制理论与热工设计，结合上下文提供的工艺数据与案例进行系统性分析25。

问题研究

子问题一：控温算法优化以提升动态响应与稳态精度

传统的PID控制虽然应用广泛，但其固定参数难以适应纺丝过程中复杂的非线性、大滞后特性。当系统受到扰动（如环境温度变化、熔体流量波动）时，固定PID参数往往导致超调、振荡或响应迟缓，无法满足±0.3℃的高精度要求8。

上下文中的研究明确指出了PID控制的局限性："PID控制器缺乏鲁棒性8。调优的参数仅适用于特定工况或特定材料，任何变化都可能导致需要重新调优，这不适合工业应用8。" 这一论述直接支持了采用更先进控制算法的必要性29。

一种有效的替代方案是模糊控制。如上下文所述："模糊控制的隶属函数更容易调整，并且可以融入以往的经验15。" 模糊控制不依赖于精确的数学模型，而是基于操作人员的经验规则进行决策，对系统参数变化具有更强的鲁棒性29。例如，可以设计如下规则：当"温度误差为正且误差变化率为负"时，应"减小加热功率"，这种基于语言规则的控制能更灵活地处理非线性过程29。

更进一步，分数阶PID（FOPID）控制被证明在精确温控中具有显著优势。上下文中的实验表明："采用分数阶PID控制，连续温度变化范围可达4-293 K，温度变化3 K仅需不到50秒，并在设定点实现±0.1 K以内的稳定14。" 这一性能远超传统PID，其关键在于分数阶微积分能更精确地描述系统的动态记忆特性，从而实现更优的控制效果14。

此外，自适应PID控制也是可行路径。上下文提到："提出了一种新的PID控制方法，通过为非线性系统建立多个局部线性模型来调整PID参数19。" 这种方法能够在系统工况变化时（如从SYSTEM1切换到SYSTEM2），自动调整PID参数，如图1所示，其参数（Kp, Ki, Kd）随系统状态动态变化，从而维持最优控制性能9。这直接解决了传统PID在工况变化时性能下降的问题8。

子问题二：结构设计优化以实现均匀热场并避免局部过热

即使拥有先进的控制算法，如果加热系统的物理结构设计不合理，仍会产生局部过热，导致熔体热降解。上下文明确指出："过高的纺丝温度会加速聚酯熔体降解，导致黏度下降……可纺性降低1。" 因此，结构设计必须确保热量的均匀传递与分布12。

首先，加热管的排布方式至关重要。不合理的排布会导致热流密度不均，形成热点26。理想的方案是采用多区独立加热与控温。例如，将纺丝箱体沿长度方向划分为多个温控区，每个区配备独立的加热管和温度传感器1。这样，控制系统可以根据各区的实时温度，独立调节加热功率，实现温度场的精细化管理29。上下文提到的"气相热煤炉控制的箱体温度"暗示了热媒循环加热的可能性，通过优化热媒管道的布局和流量分配，可以有效改善温度均匀性28。

其次，保温层材料的选择直接影响热损失与温度稳定性。高效的保温层能减少环境扰动对箱体温度的影响，降低控温系统的调节负担2。应选用导热系数低、耐高温的保温材料（如陶瓷纤维），并确保其厚度均匀、无缝隙，以构建一个稳定的热环境6。

一个关键的结构设计考量是喷丝板表面温度的控制。上下文强调："箱体温度对喷丝板表面温度的影响也较大1。如果板面温度较低，纺出的丝质地较硬，易产生毛丝、飘丝、断头等；如果板面温度过高，容易产生注头丝，出现黏板等现象1。" 这表明，喷丝板区域是温度控制的"最后一公里"，其热设计尤为关键6。可以通过在喷丝板附近设置辅助加热环或优化其与主加热区的热传导路径，来精确调控板面温度，避免因局部温差过大而引发的工艺缺陷6。

综合解决方案探讨

要实现纺丝箱体温度波动控制在±0.3℃以内并避免局部过热，必须将先进的控温算法与优化的结构设计相结合，形成一个协同工作的整体解决方案。

首先，在控制算法层面，应摒弃传统的固定参数PID，采用自适应或智能控制策略。具体而言，可以构建一个基于模糊规则的自整定PID控制器。该控制器以温度误差（e）和误差变化率（ec）为输入，通过模糊推理引擎动态输出PID的三个参数（Kp, Ki, Kd）14。这种设计既保留了PID结构的简洁性，又融入了模糊控制的鲁棒性，能够根据系统实时状态自动"调优"，有效应对±1℃的初始波动，将其抑制在±0.3℃的目标范围内14。

其次，在系统结构层面，必须实施分区加热与多点测温。参考上下文中的工艺实践，例如在生产51 dtex/72 f涤纶POY时，箱体温度被精确控制在292℃左右2。为实现此精度，应在箱体内部沿关键路径（如熔体输送管道、计量泵、纺丝组件）布置多个高精度热电偶（如上下文所述"热电偶焊接在冲头支架和适配器的自由表面"），形成温度监测网络1。同时，将加热系统划分为3-5个独立温控区，每个区由独立的加热管和可控硅（SCR）功率调节器驱动9。

通过综合分析图1、图2和图3所提供的证据，可以明确当前系统的优劣势15。如图1所示，该自适应控制器的PID参数能够根据系统波动（如从SYSTEM1到SYSTEM2）进行动态调整，从而显著改善控制效果，优于固定PID方法19。如图2所示，该系统在三倍过载电流下的瞬态仿真表明，其热管理能力强大，能够在短时间内应对剧烈的热负荷变化16。如图3所示，瞬态过载特性分析进一步验证了系统在极端工况下的稳定性26。这些图表共同证明，一个集成了自适应控制、分区加热和多点测温的系统，具备实现高精度温控的物理与理论基础15。

表1 不同熔体及箱体温度对纺丝状况的影响 和 表2 典型产品的纺丝—牵伸—热定形—卷绕工艺及物理指标 提供了关键的工艺数据支持。表1明确显示，箱体温度高于298℃时，飘丝次数增加；低于293℃时，又会出现硬头丝。这精确地定义了"局部过热"和"温度不足"的工艺边界，为控温系统设定了明确的"禁区"。表2则展示了不同产品规格下的完整工艺窗口，表明控温策略必须具备一定的灵活性，以适应不同产品的生产需求。这进一步论证了采用自适应控制的必要性——它可以根据不同的产品配方（如467 dtex/96 f或555 dtex/144 f）自动调整控制参数，确保在所有工况下都能维持最佳温度。

结论与汇总

综上所述，要解决纺丝箱体温度波动大及局部过热的问题，必须采取系统性的综合策略。单纯优化算法或结构均无法达到理想效果15。

核心解决方案是：构建一个"智能控制+分区加热+多点测温"的闭环系统。在算法上，采用模糊自整定PID或分数阶PID，利用其强鲁棒性和自适应能力，将±1℃的波动抑制到±0.3℃以内14。在结构上，实施多区独立加热和高密度温度监测，确保热量均匀分布，避免局部过热导致的熔体降解12。上下文中的 表1 和 表2 提供了精确的工艺窗口数据，而 图1、图2 和 图3 则从控制性能和热力学特性上验证了该方案的可行性。

最终，通过这种软硬件协同优化的方法，不仅能显著降低断丝率，提高满卷率（如上下文所述"满卷率在98.00%以上"），还能提升纤维的断裂强度和均匀性，实现涤纶短纤维生产的高品质与高稳定性7。







图1 Trajectories of PID parameters corresponding to





图2. Transient simulation with three-times rated current.





图3. Transient overload characteristics.

表1 不同熔体及箱体温度对纺丝状况的影响





表2 典型产品的纺丝—牵伸—热定形—卷绕工艺及物理指标





表2



来源

1.

PDF

反向流动换热器的边界几何控制

2.

PDF

紧凑型热交换器的模型控制，不依赖于传热行为

3.

PDF

Effects of high fractional noncondensable gas on c

4.

PDF

Film boiling heat transfer around a very high temp

5.

PDF

Thermal behavior of a microdevice under transient

6.

PDF

住宅太阳能系统中的微胶囊相变浆料用于热能储存

7.

PDF

基于参考模型的温度控制系统人工神经网络方法

8.

PDF

单螺杆挤出机的能量监测与质量控制

9.

PDF

工业温度调节的稳定自整定模糊逻辑控制系统

10.

PDF

PID controller tuning by frequency loop-shaping: a

11.

PDF

住宅建筑空调系统的模糊逻辑控制

12.

PDF

改进的隐式广义预测控制器的设计

13.

PDF

变速压缩机和电子膨胀阀不同控制器的比较

14.

PDF

熔体直纺51 dtex/72 f涤纶预取向丝生产工艺探讨

15.

PDF

"十"字异形截面纤维工艺探讨

16.

PDF

功能性预取向丝134dtex/72f工艺研究

17.

PDF

52 dtex/72 f吸湿排汗涤纶POY高速纺丝技术探讨

18.

PDF

热处理工艺对含低熔点涤纶短纤维混纺纱性能的影响

19.

PDF

Thermo-energetic modelling of machine tool spindle

20.

PDF

Computational optimization of the internal cooling

21.

PDF

Method for measuring thermal distortion in large m

22.

PDF

多孔板温度评估的低阶建模方法

23.

PDF

The 1963 Viscount Nuffield paper: Electric process

24.

PDF

Comparison of intensity of high temperature surfac

25.

PDF

Microforming of Lightweight Metals in Warm Conditi

26.

PDF

热响应模拟用于调节1016毫米防护热板装置中的PID控制器

27.

PDF

动态电阻温度传感器特性识别与预测

28.

PDF

分段翅片微通道的瞬态传热特性

29.

PDF

永磁和感应电机热电磁综合分析以辅助计算

30.

PDF

火花点火发动机热效率提升的数值模拟研究（第二部分）

31.

PDF

电气机器热寿命预测中神经网络的作用

32.

PDF

芯式变压器绕组瞬态流动动力学的数值研究

33.

PDF

脉冲变压器紧凑热模型考虑非线性热传递

34.

PDF

Sturdy but sensitive to heat: the impact of a wind

35.

PDF

高清红外稳定成像系统设计挑战

36.

PDF

Numerical analysis of the flow and heat transfer i

37.

PDF

保护性服装与皮肤系统热传递研究

38.

PDF

Ice slurry production using supercooling phenomeno

39.

PDF

Design of a multiple linear models-based PID contr

40.

PDF

Application of modern control to a continuous anne

41.

PDF

超导线材和带材在低温-电磁多场下的性能研究设施

42.

PDF

Two-dimensional Temperature Distribution of Strip"""

    return {
        'question': question,
        'answer': answer,
        'domain': 'chemical_engineering',
        'complexity': 'high',
        'context': {
            'technical_field': 'melt_spinning_polyester_fiber_production',
            'key_issues': ['temperature_control', 'PID_algorithm', 'fuzzy_control', 'structural_design', 'thermal_uniformity'],
            'quality_indicators': ['precision_control', 'technical_depth', 'comprehensive_analysis', 'evidenced_reasoning']
        }
    }


def evaluate_engineering_qa():
    """评估工程技术QA的完整测试"""

    print("🔬 工程技术QA质量评估测试")
    print("="*80)

    # 创建领域特定的系统
    system = QAEvaluationSystem(
        domain_name="化工工程领域"
    )

    # 获取测试QA对
    qa_data = create_test_qa_from_docx()

    print(f"📝 测试问题长度: {len(qa_data['question'])} 字符")
    print(f"📝 测试回答长度: {len(qa_data['answer'])} 字符")
    print(f"🏭 评估领域: {qa_data['domain']}")
    print(f"⚙️  问题复杂度: {qa_data['complexity']}")
    print()

    print("问题内容 (前200字符):")
    print("-" * 50)
    print(qa_data['question'][:200] + "...")
    print()

    print("回答内容 (前300字符):")
    print("-" * 50)
    print(qa_data['answer'][:300] + "...")
    print()

    # 执行评估
    print("🧠 开始对该复杂工程QA对进行十维度质量评估...")
    print("-" * 50)

    start_time = time.time()
    result = system.evaluate_single_qa(qa_data['question'], qa_data['answer'])
    processing_time = time.time() - start_time

    if 'error' in result:
        print(f"❌ 评估失败: {result['error']}")
        return

    # 显示评估结果
    print("🎯 评估结果概览:")
    print(f"   📊 综合得分: {result['overall_score']}")
    print(f"   🏆 质量等级: {result['overall_level']}")
    print(f"   📏 满意度: {result['qa_quality_satisfaction']}:.3f")
    print()

    # 详细显示问题评估
    if 'question_evaluation' in result:
        q_eval = result['question_evaluation']
        print("🔍 问题质量评估:")
        print(f"   🎚️  问题得分: {q_eval['overall_score']}")
        print(f"   📋 问题等级: {q_eval['overall_level']}")
        print()

    # 详细显示回答评估
    if 'answer_evaluation' in result:
        a_eval = result['answer_evaluation']
        print("🛠️  回答质量评估:")
        print(f"   📊 回答得分: {a_eval['answer_quality_score']}")
        print(f"   📋 回答等级: {a_eval['answer_quality_level']}")
        print()

        # 显示维度分组结果
        if 'dimension_groups' in a_eval:
            print("📊 十维度分数分布:")
            for group_name, group_data in a_eval['dimension_groups'].items():
                percentage = (group_data['weight'] * 100)
                print(f"{percentage:3.1f}%")
                print(f"权重: {group_data['weight']:.2f}")
                # 显示该组的具体维度
                for dim_name in group_data['contributions'].keys():
                    if dim_name in a_eval.get('dimension_assessments', []):
                        dim_info = next((d for d in a_eval['dimension_assessments'] if d['dimension'] == dim_name), None)
                        if dim_info:
                            dim_score = dim_info['score']
                            dim_weight = dim_info['weight'] * 100
                            print(f"    {dim_name}: {dim_score:.1f}分 (权重: {dim_weight:.1f}%)")
                print()

        # 显示具体维度评估
        if 'dimension_assessments' in a_eval:
            print("📋 各维度详细评估:")
            dimensions = a_eval['dimension_assessments']
            dimension_names = [d['dimension'] for d in dimensions]
            scores = [d['score'] for d in dimensions]

            for i, (name, score) in enumerate(zip(dimension_names, scores)):
                level = "优秀" if score >= 9.0 else "良好" if score >= 7.5 else "一般" if score >= 6.0 else "较差"
                print("<9")
        print()

    # 显示改进建议
    if 'improvement_suggestions' in result and result['improvement_suggestions']:
        print("💡 质量改进建议:")
        for i, suggestion in enumerate(result['improvement_suggestions'], 1):
            print(f"   {i}. [{suggestion['priority']}] {suggestion['aspect']}")
            print(f"      📝 {suggestion['suggestion']}")
        print()

    # 生成评估报告
    print("📄 生成评估报告...")

    # 修改：为单个QA评估结果创建合适的报告数据格式
    single_evaluation_data = {
        'statistics': {
            'total_pairs': 1,
            'valid_results': 1,
            'processing_time': result.get('metadata', {}).get('processing_time', 0),
            'average_score': result['overall_score'],
            'quality_distribution': {result['overall_level']: 1}
        },
        'results': [{
            'index': 1,
            'question': qa_data['question'][:200],
            'answer': qa_data['answer'][:500],
            'result': result
        }]
    }

    try:
        report_file = system.generate_report(single_evaluation_data, 'html')
        print(f"   ✅ HTML报告: {report_file}")

        markdown_report = system.generate_report(single_evaluation_data, 'markdown')
        print(f"   ✅ Markdown报告: {markdown_report}")

        json_report = system.generate_report(result, 'json')  # JSON格式直接使用原始结果
        print(f"   ✅ JSON报告: {json_report}")

    except Exception as e:
        print(f"   ❌ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("🏆 测试总结")
    print("=" * 50)
    print(f"✅ 工程QA评估成功完成!")
    print("🔬 该复杂工程技术QA对展现了以下质量特征:")
    print(f"   • 专业深度: 高水平技术分析与论证")
    print(f"   • 知识广度: 涵盖控制算法、结构设计、材料工艺")
    print(f"   • 实证支撑: 引用文献数据与实验证据")
    print(f"   • 系统思维: 软硬件协同优化解决方案")
    print()

    # 评估系统的表现
    system_quality_score = result['overall_score']
    if system_quality_score >= 8.0:
        assessment = "🌟 优秀 - 该QA对展现了顶尖的技术水准"
    elif system_quality_score >= 7.0:
        assessment = "✅ 良好 - 该QA对具备扎实的专业质量"
    elif system_quality_score >= 6.0:
        assessment = "⚠️  一般 - 该QA对基本满足专业要求"
    else:
        assessment = "❌ 待改进 - 该QA对质量存在明显不足"

    print(f"评估系统判定: {assessment}")

    # 清理系统
    system.cleanup()

    return result


def main():
    """主函数"""
    print("🚀 QA回答质量评估系统 - 工程技术测试")
    print("测试基于提供的复杂工程技术QA样例")
    print()

    try:
        result = evaluate_engineering_qa()

        if result:
            print("\n🎯 测试完成！")
            print("📂 查看生成的HTML报告以获得完整的可视化评估结果")
            print("💡 该系统成功演示了对复杂工程技术QA的全面质量评估")

    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
