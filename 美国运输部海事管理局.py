#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美国运输部海事管理局新闻爬虫，抓取 newsroom 列表中的新闻项。
支持 GitHub Actions 自动化运行。
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  # ✅ 新增
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
chrome_options.add_argument("--headless")  # ✅ 推荐开启 Headless 模式用于 GitHub Actions
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.170 Safari/537.36"
)

# ✅ 使用 webdriver-manager 自动下载 chromedriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

print("[...] 正在加载页面...")
driver.get(url)
time.sleep(5)  # 可根据网络环境适当加长

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


