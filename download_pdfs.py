from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import time
import os

# 设置 Edge 浏览器选项，用于自动下载 PDF 文件
options = webdriver.EdgeOptions()
download_dir = os.path.join(os.getcwd(), 'downloaded_pdfs')
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}
options.add_experimental_option('prefs', prefs)

# 初始化 Edge 浏览器驱动
service = Service()
driver = webdriver.Edge(service=service, options=options)

try:
    # 打开主页面
    driver.get('https://www.pseven.io/company/publications/')
    time.sleep(5)  # 等待页面加载

    # 查找左侧的子网页链接
    side_links = driver.find_elements(By.CSS_SELECTOR, 'a')  # 这里需要根据实际页面结构调整选择器

    # 遍历每个子网页链接
    for link in side_links[:7]:
        link_url = link.get_attribute('href')
        if link_url:
            # 打开子网页
            driver.get(link_url)
            time.sleep(5)  # 等待页面加载

            # 查找带有 "download" 标签的链接
            download_links = driver.find_elements(By.XPATH, '//*[contains(text(), "download")]')
            for download_link in download_links:
                # 检查链接是否指向 PDF 文件
                pdf_url = download_link.get_attribute('href')
                if pdf_url and pdf_url.endswith('.pdf'):
                    # 点击下载链接
                    download_link.click()
                    time.sleep(3)  # 等待下载开始

except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 关闭浏览器
    driver.quit()