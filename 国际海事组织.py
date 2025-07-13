from lxml import etree
import requests
import re
from urllib.parse import urljoin
import csv
from datetime import datetime

# 中文月份映射表
month_map = {
    "一月": "01", "二月": "02", "三月": "03", "四月": "04",
    "五月": "05", "六月": "06", "七月": "07", "八月": "08",
    "九月": "09", "十月": "10", "十一月": "11", "十二月": "12"
}

#print('----------------------------------IMO----------------------------------')

#print('----------------------------------新闻简报----------------------------------')
url = 'https://www.imo.org/zh/mediacentre/pressbriefings/pages/default.aspx'
base = 'https://www.imo.org'
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.imo.org/",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
resp = requests.get(url, headers=headers)
resp.encoding = 'utf-8'
#print(resp.text)

html = etree.HTML(resp.text)

a_list = html.xpath('//div[@class="col-md-6 mb-4 mb-md-6"]')

# 遍历每个卡片，提取时间、标题、链接
for a in a_list:
    # 原始时间格式，例如 "01 七月 2025"
    raw_date = a.xpath('.//span[@class="badge badge-primary badge-sm"]/text()')
    raw_date = raw_date[0].strip() if raw_date else ""

    # 转换时间格式为 yyyy-mm-dd
    date_str = ""
    try:
        parts = raw_date.split()
        if len(parts) == 3:
            day = parts[0].zfill(2)
            month = month_map.get(parts[1], "01")  # 默认1月
            year = parts[2]
            date_obj = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
            date_str = date_obj.strftime("%Y-%m-%d")
    except Exception as e:
        date_str = raw_date  # 转换失败就用原始字符串

    # 标题
    title = a.xpath('.//h3[@class="card-title"]/a/text()')
    title = title[0].strip() if title else ""

    # 相对链接
    rel_url = a.xpath('.//h3[@class="card-title"]/a/@href')
    link = urljoin(base, rel_url[0]) if rel_url else ""

    print(date_str, title, link)


#print('----------------------------------最新消息----------------------------------')
url = 'https://www.imo.org/zh/mediacentre/pages/whatsnew.aspx'
base = 'https://www.imo.org'
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.imo.org/",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
resp = requests.get(url, headers=headers)
resp.encoding = 'utf-8'
#print(resp.text)

html = etree.HTML(resp.text)

a_list = html.xpath('//div[@class="col-md-6 col-xl-4 mb-4 mb-md-6"]')

# 遍历每个卡片，提取时间、标题、链接
for a in a_list:
    # 原始时间格式，例如 "01 七月 2025"
    raw_date = a.xpath('.//span[@class="badge badge-primary badge-sm"]/text()')
    raw_date = raw_date[0].strip() if raw_date else ""

    # 转换时间格式为 yyyy-mm-dd
    date_str = ""
    try:
        parts = raw_date.split()
        if len(parts) == 3:
            day = parts[0].zfill(2)
            month = month_map.get(parts[1], "01")  # 默认1月
            year = parts[2]
            date_obj = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
            date_str = date_obj.strftime("%Y-%m-%d")
    except Exception as e:
        date_str = raw_date  # 转换失败就用原始字符串

    # 标题
    title = a.xpath('.//h3[@class="card-title"]/a/text()')
    title = title[0].strip() if title else ""

    # 相对链接
    rel_url = a.xpath('.//h3[@class="card-title"]/a/@href')
    link = urljoin(base, rel_url[0]) if rel_url else ""

    print(date_str, title, link)


#print('----------------------------------热点活动----------------------------------')

url = 'https://www.imo.org/zh/mediacentre/hottopics/pages/default.aspx'
base = 'https://www.imo.org'
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.imo.org/",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

resp = requests.get(url, headers=headers)
resp.encoding = 'utf-8'
html = etree.HTML(resp.text)

# 适配 <ul class="event-list"> 中的 <li>
a_list = html.xpath('//ul[@class="event-list"]/li')

for a in a_list:
    # 标题文本（有可能包含日期）
    raw_title = a.xpath('.//h3[@class="card-title card-title-lg"]/a/text()')
    raw_title = raw_title[0].strip() if raw_title else ""

    # 提取日期
    date_str = "暂无时间"

    # 清理标题中时间部分
    title_clean = re.sub(r'\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日', '', raw_title).strip(' -：')

    # 获取链接
    rel_url = a.xpath('.//h3[@class="card-title card-title-lg"]/a/@href')
    link = urljoin(base, rel_url[0]) if rel_url else ""

    print(date_str, title_clean, link)





