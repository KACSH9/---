import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://www.msa.gov.cn/page/channelArticles.do?type=xxgk&channelids=A1C5D4CC-DB15-493C-B2FC-A14C490D6331&alone=false&currentPage=1"

headers = {
    "Host": "www.msa.gov.cn",
    "Connection": "keep-alive",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0",
    "Referer": "https://www.msa.gov.cn/page/outter/xinxigongkaimulu.jsp?type=A1C5D4CC-DB15-493C-B2FC-A14C490D6331",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "Cookie": "__jsluid_s=106f8f7787823a8426557e5a6450542f; arialoadData=true; JSESSIONID=F3F221C0BEAC9953BFD538D73651E995; ariauseGraymode=false; ariaappid=3a99fe8c9a6730505625c00f963ea7c0"
}

# 发送请求
resp = requests.get(url, headers=headers)
resp.encoding = 'utf-8'

# 如果是 HTML 内容（而不是 JSON），用 BeautifulSoup 解析
soup = BeautifulSoup(resp.text, 'html.parser')
li_list = soup.find_all('li')

print("---------- 海事要闻 ----------")
for li in li_list:
    a_tag = li.find('a')
    if not a_tag:
        continue

    title_div = a_tag.find('div', class_='name')
    title = title_div.get_text(strip=True) if title_div else ''
    if title_div and title_div.find('span'):
        title = title_div.find('span').get('title') or title

    href = a_tag.get('href', '')
    full_link = urljoin(url, href)

    time_span = a_tag.find('span', class_='time')
    date = time_span.get_text(strip=True) if time_span else ''

    if title and full_link and date:
        print(f"{date}  {title}  {full_link}")
