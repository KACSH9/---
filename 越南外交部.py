import requests
from lxml import etree
from datetime import datetime

def extract_mofa_news(section_name, url, limit=10):
    print(f'----------{section_name}----------')
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
    }

    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    html = etree.HTML(resp.text)

    blocks = html.xpath('//div[@class="block-category-container"]')

    def extract_date(raw):
        try:
            # 原始格式如："12:47 | 07/07/2025"
            date_part = raw.split('|')[-1].strip()
            dt = datetime.strptime(date_part, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except:
            return '未知日期'

    for block in blocks[:limit]:
        title = block.xpath('.//h3[@class="news-title"]/a/text()')
        title = title[0].strip() if title else '无标题'

        link = block.xpath('.//h3[@class="news-title"]/a/@href')
        link = link[0].strip() if link else ''

        date_raw = block.xpath('string(.//div[@class="news-time"])').strip()
        date = extract_date(date_raw)

        print(f"{date} {title} {link}")


extract_mofa_news('高级外部活动', 'https://mofa.gov.vn/hoat-dong-doi-ngoai-cap-cao')
extract_mofa_news('副首相和部长的活动', 'https://mofa.gov.vn/hoat-dong-pho-thu-tuong-bo-truong')
extract_mofa_news('该部领导的活动', 'https://mofa.gov.vn/hoat-dong-lanh-dao-bo')
extract_mofa_news('发言人', 'https://mofa.gov.vn/nguoi-phat-ngon')
extract_mofa_news('新闻发布会', 'https://mofa.gov.vn/hop-bao')
