from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from lxml import etree
from urllib.parse import urljoin
from datetime import datetime
import time

# ——————————— 1. 设置 Selenium ———————————
url = "https://www.maritime.dot.gov/newsroom"
base = "https://www.maritime.dot.gov"

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
# 如需静默运行请取消注释
# chrome_options.add_argument("--headless")

# 启动浏览器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get(url)
print("[...] 正在加载页面...")

# 等待页面渲染完成（可调时间）
time.sleep(5)

# 获取完整渲染后的 HTML
html = driver.page_source
driver.quit()

# ——————————— 2. 使用 lxml 提取数据 ———————————
tree = etree.HTML(html)
items = tree.xpath('//div[@class="news-item views-row"]')

print("---------- 海事局新闻稿 ----------")
for item in items:
    # 时间
    raw_date = item.xpath('.//div[@class="views-field views-field-field-effective-date"]/div[@class="field-content"]/text()')
    date = raw_date[0].strip() if raw_date else ""

    # 标题
    title = item.xpath('.//div[@class="views-field views-field-title"]//a/text()')
    title = title[0].strip() if title else ""

    # 链接
    href = item.xpath('.//div[@class="views-field views-field-title"]//a/@href')
    link = urljoin(base, href[0].strip()) if href else ""

    # 日期格式转换
    try:
        formatted_date = datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")
    except:
        formatted_date = date

    print(f"{formatted_date}  {title}  {link}")
