import requests
from lxml import etree
from datetime import datetime

url = 'https://www.isa.org.jm/news/'
resp = requests.get(url)
result = resp.text

html = etree.HTML(result)

articles = html.xpath('//article[contains(@id,"post")]')

for article in articles:
    #时间
    date_1 = article.xpath('.//span[@class="post_date"]/text()')[0]
    date_2 = datetime.strptime(date_1, "%d %B %Y")
    date_3 = date_2.strftime("%Y-%m-%d")
    #标题
    title = article.xpath('.//h4[@class="entry-titles default-max-width"]/a/text()')[0]
    #链接
    link = article.xpath('.//h4[@class="entry-titles default-max-width"]/a/@href')[0]

    print(date_3, title, link)
