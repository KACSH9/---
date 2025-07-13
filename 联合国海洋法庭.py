from lxml import etree
from urllib.parse import urljoin
import requests

# 网站地址
base_url = 'https://www.itlos.org'
url = base_url + '/en/main/resources/calendar-of-events/'

# 获取网页内容
resp = requests.get(url)
resp.encoding = 'utf-8'
html = etree.HTML(resp.text)

# 遍历每条新闻
articles = html.xpath('//div[contains(@class, "article") and @itemscope]')

for article in articles:
    # 1. 日期
    date = article.xpath('.//time/@datetime')[0].strip()

    # 2. 标题
    title = article.xpath('.//span[@itemprop="headline"]/text()')[0].strip()

    # 3. 所有链接
    link_tags = article.xpath('.//div[contains(@class, "news-text-wrap")]//a/@href')
    links = [urljoin(base_url, href) for href in link_tags]

    # 4. 输出一行：日期 + 标题 + 所有链接
    line = f"{date} {title} " + " ".join(links)
    print(line)
