import tkinter as tk
from lunardate import LunarDate
from datetime import datetime

# 定义时辰映射
hour_to_chinese_time = {
    (23, 1): "子时",
    (1, 3): "丑时",
    (3, 5): "寅时",
    (5, 7): "卯时",
    (7, 9): "辰时",
    (9, 11): "巳时",
    (11, 13): "午时",
    (13, 15): "未时",
    (15, 17): "申时",
    (17, 19): "酉时",
    (19, 21): "戌时",
    (21, 23): "亥时"
}

def get_chinese_time(hour):
    for time_range, chinese_time in hour_to_chinese_time.items():
        if time_range[0] <= hour < time_range[1]:
            return chinese_time
    return ""

def convert_to_lunar():
    date_str = entry.get()
    time_str = time_entry.get()
    try:
        solar_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        lunar = LunarDate.fromSolarDate(solar_datetime.year, solar_datetime.month, solar_datetime.day)
        chinese_time = get_chinese_time(solar_datetime.hour)
        result_label.config(text=f"阴历: {lunar.year} 年 {lunar.month} 月 {lunar.day} 日 {chinese_time}")
    except ValueError:
        result_label.config(text="请输入有效的日期格式 (YYYY-MM-DD) 和时间格式 (HH:MM)")

# 定义关闭窗口的处理函数
def on_closing():
    root.destroy()

# 创建主窗口
root = tk.Tk()
root.title("阳历转阴历")

# 绑定关闭窗口的协议
root.protocol("WM_DELETE_WINDOW", on_closing)

# 创建输入框和标签
label = tk.Label(root, text="输入阳历日期 (YYYY-MM-DD):")
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=5)

time_label = tk.Label(root, text="输入出生时间 (HH:MM):")
time_label.pack(pady=10)

time_entry = tk.Entry(root)
time_entry.pack(pady=5)

# 创建转换按钮
convert_button = tk.Button(root, text="转换", command=convert_to_lunar)
convert_button.pack(pady=20)

# 创建结果标签
result_label = tk.Label(root, text="")
result_label.pack(pady=10)

# 运行主循环
root.mainloop()