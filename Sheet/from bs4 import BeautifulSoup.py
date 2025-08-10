from bs4 import BeautifulSoup
# requests 库不再需要，可以删除
# import requests

# 本地文件路径
file_path = 'C:/Users/BELLE/Desktop/广西大模型项目需求调研问卷.html'

try:
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    # 假设表单的字段是这样定义的
    name_input = soup.find('input', {'name': 'name'})
    email_input = soup.find('input', {'name': 'email'})

    # 提取输入框的值
    name = name_input.get('value') if name_input else None
    email = email_input.get('value') if email_input else None

    # 输出提取到的数据
    print(f"姓名: {name}")
    print(f"邮箱: {email}")

except FileNotFoundError:
    print(f"未找到文件: {file_path}")
except Exception as e:
    print(f"发生错误: {e}")