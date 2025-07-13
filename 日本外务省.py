#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日本外务省（Selenium 版）：抓取 Press Releases 页面前 10 条新闻，
并输出它们各自的发布日期（来自对应的 <dt>）。
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from lxml import etree
from urllib.parse import urljoin
from datetime import datetime
import time

# 1. 浏览器设置
PRESS_URL = "https://www.mofa.go.jp/press/release/index.html"
opts = Options()
opts.add_argument("--headless")
opts.add_argument("--disable-gpu")
opts.add_argument("--no-sandbox")
opts.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.5790.170 Safari/537.36"
)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=opts)

# 2. 获取页面
driver.get(PRESS_URL)
time.sleep(3)
html = driver.page_source
driver.quit()

# 3. 解析
tree = etree.HTML(html)

results = []
# 4. 遍历每个 dt + dd 组
for dt in tree.xpath('//dl[@class="title-list"]/dt[@class="list-title"]'):
    dt_text = dt.text.strip()  # e.g. "July 13"
    dd = dt.getnext()
    if dd is None:
        continue
    # 遍历这个组里的所有链接
    for a in dd.xpath('.//ul[@class="link-list"]/li/a'):
        title = a.xpath("string(.)").strip()
        href  = a.get("href")
        full  = urljoin(PRESS_URL, href)
        # 记录 (dt_text, title, link)
        results.append((dt_text, title, full))
        if len(results) >= 10:
            break
    if len(results) >= 10:
        break

# 5. 输出前 10 条，拼出 YYYY-MM-DD 格式
current_year = datetime.today().year
for dt_text, title, link in results:
    # 把 "July 13" 转成 2025-07-13
    mon_str, day_str = dt_text.split()
    month = datetime.strptime(mon_str, "%B").month
    day   = int(day_str)
    prefix = f"{current_year}-{month:02d}-{day:02d}"
    print(f"{prefix}  {title}  {link}")
