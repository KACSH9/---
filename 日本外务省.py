from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from lxml import etree
from urllib.parse import urljoin
from datetime import datetime
import time

# —————— 配置区 ——————
PRESS_URL = "https://www.mofa.go.jp/press/release/index.html"

# 1. 生成 TARGET_DT，比如 "July 7"（页面里 <dt> 文本正好是这样）
try:
    # Linux / macOS：%-d 去掉前导零
    TARGET_DT = datetime.today().strftime("%B %-d")
except:
    # Windows fallback：%d 会有前导零，去掉它
    TARGET_DT = datetime.today().strftime("%B %d").replace(" 0", " ")

# 2. 生成输出用的日期 "YYYY-MM-DD"
TODAY_OUT = datetime.today().strftime("%Y-%m-%d")

# —————— 启动 Selenium ——————
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
# 如果你想看浏览器界面，就注释掉下面这行
# options.add_argument("--headless")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 打开页面并等待渲染
driver.get(PRESS_URL)
time.sleep(3)

# 获取渲染后 HTML 并退出浏览器
html = driver.page_source
driver.quit()

# —————— 解析并提取 ——————
tree = etree.HTML(html)

# 定位当天的 <dt>，例如 dt.text == "July 7"
dts = tree.xpath(f'//dl[@class="title-list"]/dt[text()="{TARGET_DT}"]')
if not dts:
    print(f"[!] 今日页面未找到 “{TARGET_DT}” 节点。")
    exit()

# 找到对应的 <dd>，提取所有新闻链接
dd = dts[0].getnext()
links = dd.xpath('.//li/a')

for a in links:
    title = a.xpath("string(.)").strip()
    href  = a.get("href")
    full  = urljoin(PRESS_URL, href)
    print(f"{TODAY_OUT}  {title}  {full}")
