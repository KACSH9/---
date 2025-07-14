#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取日本海上保安厅官网三类信息：
1. 海上事故信息（requests）
2. 海上安全信息（Selenium 动态加载）
3. 新闻发布信息（requests）
"""

import requests
from lxml import etree
from urllib.parse import urljoin
import chardet
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ------------------ 日期转换函数 ------------------
def convert_reiwa_date(reiwa_str):
    """将 '令和7年1月17日' → '2025-01-17' """
    match = re.match(r'令和(\d+)年(\d+)月(\d+)日', reiwa_str)
    if match:
        reiwa_year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        year = 2018 + reiwa_year
        return f"{year:04d}-{month:02d}-{day:02d}"
    return reiwa_str

def convert_short_japanese_date(short_date):
    """将 '25/07/10' → '2025-07-10'"""
    try:
        parts = short_date.strip().split('/')
        if len(parts) == 3:
            year = 2000 + int(parts[0])  # 假设 2000年后
            month = int(parts[1])
            day = int(parts[2])
            return f"{year:04d}-{month:02d}-{day:02d}"
    except Exception:
        pass
    return short_date

# ------------------ 1. 海上事故信息 ------------------
print('----------海上事故信息----------')
base_url = 'https://www6.kaiho.mlit.go.jp/info/marinesafety/jikojouhou.html'
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
}

try:
    resp = requests.get(base_url, headers=headers)
    encoding = chardet.detect(resp.content)['encoding']
    resp.encoding = encoding
    html = etree.HTML(resp.text)
    items = html.xpath('//ul[@class="link"]/dt/li')

    for item in items:
        title = item.xpath('.//a/text()')
        link = item.xpath('.//a/@href')

        title_str = title[0].strip() if title else ''
        link_str = urljoin(base_url, link[0].strip()) if link else ''

        try:
            detail_resp = requests.get(link_str, headers=headers, timeout=10)
            detail_encoding = chardet.detect(detail_resp.content)['encoding']
            detail_resp.encoding = detail_encoding
            detail_html = etree.HTML(detail_resp.text)

            desc = detail_html.xpath('//meta[@name="description"]/@content')
            desc_text = desc[0] if desc else ''

            match = re.search(r'令和\d+年\d+月\d+日', desc_text)
            reiwa_date = match.group() if match else '未知'
            pub_date = convert_reiwa_date(reiwa_date)

            print(f"{pub_date} {title_str} {link_str}")
            time.sleep(1)

        except Exception as e:
            print(f"[错误] {link_str} 请求失败：{e}")
except Exception as e:
    print(f"[错误] 主页面解析失败：{e}")

# ------------------ 2. 海上安全信息（动态加载） ------------------
print('----------海上安全信息----------')

class MaritimeSafetyInfoScraper:
    def __init__(self, headless=True):
        self.base_url = "https://www6.kaiho.mlit.go.jp"
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        self.districts = [
            {"name": "第一管区", "url": "/01kanku/kinkyu.html"},
            {"name": "第二管区", "url": "/02kanku/kinkyu.html"},
            {"name": "第三管区", "url": "/03kanku/kinkyu.html"},
            {"name": "第四管区", "url": "/04kanku/kinkyu.html"},
            {"name": "第五管区", "url": "/05kanku/kinkyu.html"},
            {"name": "第六管区", "url": "/06kanku/kinkyu.html"},
            {"name": "第七管区", "url": "/07kanku/kinkyu.html"},
            {"name": "第八管区", "url": "/08kanku/kinkyu.html"},
            {"name": "第九管区", "url": "/09kanku/kinkyu.html"},
            {"name": "第十管区", "url": "/10kanku/kinkyu.html"},
            {"name": "第十一管区", "url": "/11kanku/kinkyu.html"}
        ]
        self.driver = None

    def init_driver(self):
        try:
            # ✅ 使用本地 chromedriver
            service = Service("/usr/local/bin/chromedriver")
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print("[错误] WebDriver 初始化失败：", e)
            return False

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def get_content(self):
        js_script = """
        let results = [];
        document.querySelectorAll('dl').forEach(dl => {
            let dt = dl.querySelector('dt');
            let a = dl.querySelector('dd a');
            if (dt && a) {
                results.push({
                    date: dt.textContent.trim(),
                    title: a.textContent.trim(),
                    href: a.href
                });
            }
        });
        return results;
        """
        return self.driver.execute_script(js_script)

    def scrape_district(self, district):
        url = self.base_url + district['url']
        self.driver.get(url)
        return self.get_content()

    def run(self):
        if not self.init_driver():
            print("WebDriver 初始化失败")
            return
        try:
            for district in self.districts:
                try:
                    data = self.scrape_district(district)
                    for item in data:
                        print(f"{item['date']} {item['title']} {item['href']}")
                except Exception as e:
                    print(f"{district['name']} 获取失败：{e}")
                time.sleep(1)
        finally:
            self.close_driver()

scraper = MaritimeSafetyInfoScraper(headless=True)
scraper.run()

# ------------------ 3. 新闻发布 ------------------
print('----------新闻发布----------')
url_n = 'https://www.kaiho.mlit.go.jp/info/kouhou/'
try:
    resp = requests.get(url_n, headers=headers)
    encoding = chardet.detect(resp.content)['encoding']
    resp.encoding = encoding
    html = etree.HTML(resp.content)
    items = html.xpath('//div[@class="entryList clearfix"]//ul/li')[:10]

    for item in items:
        date_raw = item.xpath('.//h3/text()')
        raw_date = date_raw[0].strip().split('\xa0')[0] if date_raw else ''
        date = convert_short_japanese_date(raw_date)

        a_tag = item.xpath('.//a')[0]
        title = a_tag.xpath('string(.)').strip()
        link = urljoin(url_n, a_tag.get('href'))

        print(f"{date} {title} {link}")
except Exception as e:
    print(f"[错误] 新闻发布抓取失败：{e}")
