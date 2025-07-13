import requests
from lxml import etree
from urllib.parse import urljoin
from datetime import datetime

def convert_date(date_str):
    """
    将 '09 July 2025' 转为 '2025-07-09'
    """
    try:
        dt = datetime.strptime(date_str.strip(), '%d %B %Y')
        return dt.strftime('%Y-%m-%d')
    except:
        return date_str.strip()

url = 'https://forumsec.org/publications'
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
}

resp = requests.get(url, headers=headers)
html = etree.HTML(resp.text)

cards = html.xpath('//div[contains(@class, "card publication")]')[:10]  # 前10条

for card in cards:
    # 提取日期
    date = card.xpath('.//div[@class="card__date"]/text()')
    date_str = convert_date(date[0]) if date else '未知日期'

    # 提取标题
    title = card.xpath('.//a[contains(@class, "card__title")]/text()')
    title_str = title[0].strip() if title else '无标题'

    # 提取链接
    href = card.xpath('.//a[contains(@class, "card__title")]/@href')
    link_str = urljoin(url, href[0]) if href else ''

    print(f"{date_str} {title_str} {link_str}")

