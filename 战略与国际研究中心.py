import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

def get_csis_articles(section_name, referer_url, section_id="3060"):
    """
    获取 CSIS 某一板块第一页文章的标题、日期、链接。
    默认使用 section_id = 3060，可适配多个主题板块。
    """
    url = "https://www.csis.org/views/ajax"
    params = {
        "page": "0",
        "_wrapper_format": "drupal_ajax",
        "view_name": "search_default_index",
        "view_display_id": "block_1",
        "view_args": section_id,
        "view_path": referer_url.replace("https://www.csis.org", ""),
        "_drupal_ajax": "1"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": referer_url,
        "Origin": "https://www.csis.org",
        "X-Requested-With": "XMLHttpRequest"
        # 如仍失败，可以再添加 'Cookie': '复制浏览器中的Cookie值'
    }

    try:
        resp = requests.get(url, headers=headers, params=params)
    except Exception as e:
        print(f"\n❌ [{section_name}] 网络请求失败：{e}")
        return

    if not resp.text.strip().startswith("["):
        print(f"\n❌ [{section_name}] 数据拉取失败：响应不是JSON，可能被封锁或参数无效")
        print(resp.text[:300])  # 打印前 300 字符调试
        return

    try:
        data = json.loads(resp.text)
    except json.JSONDecodeError:
        print(f"\n❌ [{section_name}] JSON解析失败")
        return

    html_block = ""
    for block in data:
        if isinstance(block, dict) and 'data' in block and isinstance(block['data'], str):
            html_block = block['data']
            break

    soup = BeautifulSoup(html_block, 'html.parser')
    articles = soup.select('article')

    print(f"\n------ {section_name} ------")
    for article in articles:
        a_tag = article.select_one('h3.headline-md a, h3.headline-sm a')
        if not a_tag:
            continue
        title = a_tag.get_text(strip=True)
        link = "https://www.csis.org" + a_tag.get('href')

        raw_text = article.get_text(separator=" ", strip=True)
        pub_date = "N/A"
        date_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}", raw_text)
        if date_match:
            try:
                parsed = datetime.strptime(date_match.group(0), "%B %d, %Y")
                pub_date = parsed.strftime("%Y-%m-%d")
            except:
                pass

        if pub_date != "N/A":
            print(f"{pub_date} {title} {link}")



get_csis_articles("海事问题与海洋", "https://www.csis.org/topics/maritime-issues-and-oceans")
get_csis_articles("气候变化", "https://www.csis.org/topics/climate-change")
get_csis_articles("国防和安全", "https://www.csis.org/topics/defense-and-security")
get_csis_articles("能源与可持续性", "https://www.csis.org/topics/energy-and-sustainability")
get_csis_articles("性别与国际安全", "https://www.csis.org/topics/gender-and-international-security")
get_csis_articles("地缘政治与国际安全", "https://www.csis.org/topics/geopolitics-and-international-security")
get_csis_articles("贸易和国际商务", "https://www.csis.org/topics/trade-and-international-business")
get_csis_articles("跨国威胁", "https://www.csis.org/topics/transnational-threats")





