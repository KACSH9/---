import requests
from lxml import etree
from urllib.parse import urljoin
import html
from datetime import datetime

# 目标页面
url = "https://www.dav.edu.vn/tin-tuc/"
resp = requests.get(url)
resp.encoding = "utf-8"
html_tree = etree.HTML(resp.text)

# 所有新闻块
articles = html_tree.xpath('//article[contains(@class, "story")]')

for article in articles:
    # 获取原始日期（有的格式为：01/06/2025 或带时间）
    raw_date = article.xpath('.//time/text()')
    if not raw_date:
        continue
    try:
        # 截取日期部分并转换格式为 yyyy-mm-dd
        raw_date_str = raw_date[0].strip()[:10]
        date_obj = datetime.strptime(raw_date_str, "%d/%m/%Y")
        date_fmt = date_obj.strftime("%Y-%m-%d")
    except:
        continue  # 如果转换失败，跳过该条

    # 获取标题
    title_nodes = article.xpath('.//h3[@class="story__title"]/a')
    if not title_nodes:
        continue
    title = html.unescape(title_nodes[0].xpath('string(.)').strip())

    # 获取链接
    href = title_nodes[0].xpath('./@href')[0]
    full_url = urljoin(url, href)

    # 输出格式：yyyy-mm-dd  标题  链接
    print(f"{date_fmt}  {title}  {full_url}")
