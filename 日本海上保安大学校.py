import requests
from lxml import etree
from urllib.parse import urljoin

url = 'https://www.academy.kaiho.mlit.go.jp/index.html'
base = 'https://www.academy.kaiho.mlit.go.jp'

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
}

resp = requests.get(url, headers=headers)
resp.encoding = 'utf-8'

html = etree.HTML(resp.text)
items = html.xpath('//dl[@class="info_list"]/div')

print("---------- 新闻和话题 ----------")
for item in items:
    date = item.xpath('.//time/@datetime')
    title = item.xpath('.//a/text()')
    link = item.xpath('.//a/@href')

    # 提取实际值
    date_str = date[0].strip() if date else ''
    title_str = title[0].strip() if title else ''
    full_link = urljoin(base, link[0].strip()) if link else ''

    # 输出
    if date_str and title_str and full_link:
        print(f"{date_str}  {title_str}  {full_link}")
