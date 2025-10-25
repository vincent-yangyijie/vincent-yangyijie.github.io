import os
import comtypes.client
import time

def pptx_to_pdf(input_file_path, output_file_path):
    try:
        # 确保正确创建 PowerPoint 应用程序对象
        powerpoint = comtypes.client.CreateObject("PowerPoint.Application")
        powerpoint.Visible = 1
        # 增加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                deck = powerpoint.Presentations.Open(input_file_path)
                deck.SaveAs(output_file_path, 32)  # 32 代表 PDF 格式
                deck.Close()
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"尝试打开文件 {input_file_path} 失败，错误信息: {e}，正在进行第 {attempt + 2} 次尝试...")
                    time.sleep(2)
                else:
                    print(f"多次尝试打开文件 {input_file_path} 失败，错误信息: {e}")
        powerpoint.Quit()
    except Exception as e:
        print(f"处理文件 {input_file_path} 时发生错误: {e}")

if __name__ == "__main__":
    folder_path = '.'  # 可修改为实际文件夹路径
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.pptx'):
                input_file_path = os.path.join(root, file)
                output_file_name = os.path.splitext(file)[0] + '.pdf'
                output_file_path = os.path.join(root, output_file_name)
                pptx_to_pdf(input_file_path, output_file_path)