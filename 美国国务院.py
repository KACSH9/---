import requests
from lxml import etree
from urllib.parse import urljoin
from datetime import datetime

url = 'https://www.state.gov/'
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
resp = requests.get(url, headers=headers)
resp.encoding = 'utf-8'

html = etree.HTML(resp.text)
items = html.xpath('//li[@class="news-bar__post"]')

print("---------- 头条新闻 ----------")
for item in items:
    # 抓取字段
    raw_date = item.xpath('string(.//div[@class="news-bar__post-date"])').strip()
    title = item.xpath('string(.//p[@class="news-bar__post-title"]/a)').strip()
    link = item.xpath('string(.//p[@class="news-bar__post-title"]/a/@href)').strip()

    # 日期格式转换
    try:
        date_obj = datetime.strptime(raw_date, "%B %d, %Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
    except Exception:
        formatted_date = raw_date  # fallback，保留原始

    print(f"{formatted_date}  {title}  {link}")

print("---------- 其他新闻 ----------")
items = html.xpath('//ul[@class="other-news__list"]/li')

for item in items:
    # 日期
    raw_date_list = item.xpath('.//div[@class="eyebrow other-news__eyebrow"]/text()')
    raw_date = raw_date_list[0].strip() if raw_date_list else ""

    # 标题
    title_list = item.xpath('.//h3[@class="header--four"]/a/text()')
    title = title_list[0].strip() if title_list else ""

    # 链接
    link_list = item.xpath('.//h3[@class="header--four"]/a/@href')
    link = link_list[0].strip() if link_list else ""

    # 日期格式转换
    try:
        formatted_date = datetime.strptime(raw_date, "%B %d, %Y").strftime("%Y-%m-%d")
    except:
        formatted_date = raw_date

    print(f"{formatted_date}  {title}  {link}")

print("---------- 发言人简报 ----------")
briefing_url = 'https://www.state.gov/department-press-briefings'
resp2 = requests.get(briefing_url, headers=headers)
resp2.encoding = 'utf-8'

html2 = etree.HTML(resp2.text)
items = html2.xpath('//li[@class="collection-result"]')

for item in items:
    # 标题
    title_list = item.xpath('.//a[@class="collection-result__link"]/text()')
    title = title_list[0].strip() if title_list else ""

    # 链接
    link_list = item.xpath('.//a[@class="collection-result__link"]/@href')
    link = link_list[0].strip() if link_list else ""

    # 日期（一般在第二个 span）
    date_list = item.xpath('.//div[@class="collection-result-meta"]/span[2]/text()')
    raw_date = date_list[0].strip() if date_list else ""

    # 日期格式转换
    try:
        formatted_date = datetime.strptime(raw_date, "%B %d, %Y").strftime("%Y-%m-%d")
    except:
        formatted_date = raw_date

    print(f"{formatted_date}  {title}  {link}")


print("---------- 中国专页新闻 ----------")
china_url = 'https://www.state.gov/countries-areas/china/'
resp_china = requests.get(china_url, headers=headers)
resp_china.encoding = 'utf-8'
china_html = etree.HTML(resp_china.text)

# 定位到新闻块
china_items = china_html.xpath('//div[contains(@class, "state-content-feed__article")]')

# 去重集合
seen = set()

for item in china_items:
    # 日期
    raw_date_list = item.xpath('.//span[contains(@class, "state-content-feed__article-eyebrow")]/text()')
    raw_date = raw_date_list[0].strip() if raw_date_list else ""

    # 标题
    title_list = item.xpath('.//p[@class="state-content-feed__article-headline"]/a/text()')
    title = title_list[0].strip() if title_list else ""

    # 链接
    link_list = item.xpath('.//p[@class="state-content-feed__article-headline"]/a/@href')
    link = link_list[0].strip() if link_list else ""

    # 去重逻辑
    key = (raw_date, title, link)
    if key in seen:
        continue
    seen.add(key)

    # 日期格式化
    try:
        formatted_date = datetime.strptime(raw_date, "%B %d, %Y").strftime("%Y-%m-%d")
    except:
        formatted_date = raw_date

    print(f"{formatted_date}  {title}  {link}")
