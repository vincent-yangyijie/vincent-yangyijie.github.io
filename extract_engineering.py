import pandas as pd
import json
import re

def sanitize_text(text):
    if isinstance(text, str):
        return re.sub(r'[\x00-\x1F\x7F\x80-\x9F]', '', text)
    return text

# 定义要提取的字段
fields = ['uuid', 'question', 'options', 'answer', 'answer_letter', 'discipline', 'field', 'subfield', 'difficulty', 'is_calculation']

try:
    # 直接从文本文件读取并筛选
    with open('SuperGPQA-Engineering.txt', 'r', encoding='utf-8') as file:
        data = []
        for line_num, line in enumerate(file, 1):
            line = line.strip().replace('SuperGPQA-Engineering.txt', '', 1).strip()
            if not line:
                continue
            try:
                json_data = json.loads(line)
                if json_data.get('field') == 'Aeronautical and Astronautical Science and Technology':
                    row = [sanitize_text(json_data.get(f)) for f in fields]
                    data.append(row)
            except json.JSONDecodeError:
                continue

    if data:
        df = pd.DataFrame(data, columns=fields)
        df.to_excel('SuperGPQA-Aeronautical.xlsx', index=False, engine='openpyxl')
        print(f"成功生成筛选文件，共{len(data)}行数据")
    else:
        print("未找到符合条件的数据")
except Exception as e:
    print(f"处理出错: {str(e)}")