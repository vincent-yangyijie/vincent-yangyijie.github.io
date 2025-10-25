import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 修改为系统中已有的中文字体
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial']  # 优先使用 SimHei

# 以下为原代码
plt.figure(figsize=(12, 8))
plt.title("基于数字孪生的智能研发系统架构（含数据、控制、知识流）", fontsize=14)
plt.axis('off')

nodes = {
    '物理层': (-4, 0),
    '数据采集层': (-4, 1),
    '数字孪生数据库': (-4, 2),
    '数字孪生层': (-4, 3),
    '知识层': (-6, 3),
    'Agentic System': (0, 3),
    '工具集成平台': (0, 4),
    '工具链层': (0, 5),
    '应用层': (-4, 6),
    '工作流引擎': (2, 4),
    '安全层': (2, 3)
}

for label, (x, y) in nodes.items():
    plt.text(x, y, label, bbox=dict(facecolor='lightgray', alpha=0.8, boxstyle='round,pad=0.5'), 
             ha='center', va='center', fontsize=10)

def draw_arrow(start, end, color, label=None, style='-', lw=1.5):
    x1, y1 = nodes[start]
    x2, y2 = nodes[end]
    plt.arrow(x1, y1, x2 - x1, y2 - y1, head_width=0.2, head_length=0.3, fc=color, ec=color, 
              length_includes_head=True, linestyle=style, linewidth=lw)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        plt.text(mid_x, mid_y, label, color=color, ha='center', va='center', fontsize=8)

draw_arrow('物理层', '数据采集层', 'blue', '数据')
draw_arrow('数据采集层', '数字孪生数据库', 'blue')
draw_arrow('数字孪生数据库', '数字孪生层', 'blue')
draw_arrow('数字孪生层', 'Agentic System', 'blue')
draw_arrow('Agentic System', '工具集成平台', 'blue', '数据', style='-.')
draw_arrow('工具集成平台', '工具链层', 'blue')
draw_arrow('工具链层', '数字孪生数据库', 'blue', '结果', style='-.')
draw_arrow('工具链层', 'Agentic System', 'blue', '反馈')

draw_arrow('应用层', 'Agentic System', 'red', '用户事件')
draw_arrow('Agentic System', '工具集成平台', 'red')
draw_arrow('工具集成平台', '工作流引擎', 'red')
draw_arrow('工作流引擎', '工具链层', 'red', '执行')
draw_arrow('工具集成平台', '工具链层', 'red')

draw_arrow('知识层', '数字孪生层', 'green')
draw_arrow('知识层', 'Agentic System', 'green', '知识')
draw_arrow('Agentic System', '应用层', 'green')

draw_arrow('数字孪生层', '安全层', 'black', '安全')
draw_arrow('应用层', '安全层', 'black', '安全', style='-.')

plt.xlim(-7, 3)
plt.ylim(-1, 7)

plt.show()
### 1. 检查系统字体
#要保证系统中安装了 `Noto Sans CJK SC` 字体。若未安装，您可以从 [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Sans+SC) 下载并安装。

### 2. 更换其他中文字体
#若 `Noto Sans CJK SC` 不可用，您可以尝试使用系统里已有的中文字体，例如 `SimHei`（黑体）。以下是修改后的代码：
#```python
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 动态指定字体路径，替换为您实际的字体文件路径
font_path = r'C:\Windows\Fonts\simhei.ttf'
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

# 修改为系统中已有的中文字体
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial']  # 优先使用 SimHei

# 以下为原代码
plt.figure(figsize=(12, 8))
plt.title("基于数字孪生的智能研发系统架构（含数据、控制、知识流）", fontsize=14)
plt.axis('off')

nodes = {
    '物理层': (-4, 0),
    '数据采集层': (-4, 1),
    '数字孪生数据库': (-4, 2),
    '数字孪生层': (-4, 3),
    '知识层': (-6, 3),
    'Agentic System': (0, 3),
    '工具集成平台': (0, 4),
    '工具链层': (0, 5),
    '应用层': (-4, 6),
    '工作流引擎': (2, 4),
    '安全层': (2, 3)
}

for label, (x, y) in nodes.items():
    plt.text(x, y, label, bbox=dict(facecolor='lightgray', alpha=0.8, boxstyle='round,pad=0.5'), 
             ha='center', va='center', fontsize=10)

def draw_arrow(start, end, color, label=None, style='-', lw=1.5):
    x1, y1 = nodes[start]
    x2, y2 = nodes[end]
    plt.arrow(x1, y1, x2 - x1, y2 - y1, head_width=0.2, head_length=0.3, fc=color, ec=color, 
              length_includes_head=True, linestyle=style, linewidth=lw)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        plt.text(mid_x, mid_y, label, color=color, ha='center', va='center', fontsize=8)

draw_arrow('物理层', '数据采集层', 'blue', '数据')
draw_arrow('数据采集层', '数字孪生数据库', 'blue')
draw_arrow('数字孪生数据库', '数字孪生层', 'blue')
draw_arrow('数字孪生层', 'Agentic System', 'blue')
draw_arrow('Agentic System', '工具集成平台', 'blue', '数据', style='-.')
draw_arrow('工具集成平台', '工具链层', 'blue')
draw_arrow('工具链层', '数字孪生数据库', 'blue', '结果', style='-.')
draw_arrow('工具链层', 'Agentic System', 'blue', '反馈')

draw_arrow('应用层', 'Agentic System', 'red', '用户事件')
draw_arrow('Agentic System', '工具集成平台', 'red')
draw_arrow('工具集成平台', '工作流引擎', 'red')
draw_arrow('工作流引擎', '工具链层', 'red', '执行')
draw_arrow('工具集成平台', '工具链层', 'red')

draw_arrow('知识层', '数字孪生层', 'green')
draw_arrow('知识层', 'Agentic System', 'green', '知识')
draw_arrow('Agentic System', '应用层', 'green')

draw_arrow('数字孪生层', '安全层', 'black', '安全')
draw_arrow('应用层', '安全层', 'black', '安全', style='-.')

plt.xlim(-7, 3)
plt.ylim(-1, 7)

plt.show()