#!/usr/bin/env python3
# 日本外务省每日发布爬虫 -- 支持传入 --date 参数

import argparse
import time
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from lxml import etree
from datetime import datetime

# —————— 1. 接收外部传入的日期参数 ——————
parser = argparse.ArgumentParser(description="抓取日本外务省当天新闻，参数格式 YYYY-MM-DD")
parser.add_argument("--date", "-d", required=True, help="查询日期，格式：YYYY-MM-DD")
args = parser.parse_args()

# 把传入的字符串转成 datetime 对象
query_date = datetime.strptime(args.date, "%Y-%m-%d")

# —————— 2. 构造页面标签 vs. 输出前缀 ——————

# 页面上 <dt> 文本格式例如 "July 7"（英文月份 + 无前导零的日）
try:
    TARGET_DT = query_date.strftime("%B %-d")
except ValueError:
    TARGET_DT = query_date.strftime("%B %d").replace(" 0", " ")
# 输出的前缀日期直接用传入的 YYYY-MM-DD
TODAY_OUT = args.date

# —————— 3. 启动 Selenium，获取渲染后 HTML ——————
PRESS_URL = "https://www.mofa.go.jp/press/release/index.html"
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--headless")  # 云端必须 headless
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

driver.get(PRESS_URL)
time.sleep(3)
html = driver.page_source
driver.quit()

# —————— 4. 解析并提取当天链接 ——————
tree = etree.HTML(html)
# 找到当天 <dt>
dts = tree.xpath(f'//dl[@class="title-list"]/dt[text()="{TARGET_DT}"]')
if not dts:
    # 如果页面结构变了，请检查 TARGET_DT 格式
    print(f"[!] 页面未找到 “{TARGET_DT}” 节点。")
    exit(0)

dd = dts[0].getnext()
links = dd.xpath('.//li/a')

for a in links:
    title = a.xpath("string(.)").strip()
    href  = a.get("href")
    full  = urljoin(PRESS_URL, href)
    # 打印：YYYY-MM-DD  标题  链接
    print(f"{TODAY_OUT}  {title}  {full}")
