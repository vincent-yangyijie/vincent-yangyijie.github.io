import webbrowser
import os

# 定义HTML文件路径
html_files = [
    'index.html',
    'page1.html',
    'page2.html',
    'lithium_sulfur_battery.html'
]

def open_html_files():
    """打开所有HTML文件进行预览"""
    for file in html_files:
        # 获取绝对路径
        abs_path = os.path.abspath(file)
        # 使用默认浏览器打开文件
        webbrowser.open('file://' + abs_path)
        print(f'已打开: {abs_path}')

if __name__ == '__main__':
    print('正在打开HTML文件进行预览...')
    open_html_files()
    print('预览完成！')