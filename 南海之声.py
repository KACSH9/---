# 南海之声数据爬取
import requests
from time import sleep
from datetime import datetime
import re

# 目标网站
url = 'https://m.weibo.cn/api/container/getIndex?containerid=1076033858832626'

# 请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
    "accept": "application/json, text/plain, */*",
    "referer": "https://m.weibo.cn/u/3858832626",
    "x-requested-with": "XMLHttpRequest"
}

# Cookie信息（登录后从浏览器中获取）
cookies = {
    "SUB": "_2AkMfL9rFf8NxqwFRmvkcxWPmaYl2wgvEieKpcyseJRMxHRl-yT9kqhUCtRB6NK_0Kqsr4wZsn2N_E_F5tcTDyZzhIf-H",
    "SUBP": "0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFNBEyfW18Aqs9jWueGKD-9",
    "XSRF-TOKEN": "Tevhi3ETVUbpzsgEqRryyrjk",
    "WBPSESS": "LKUy5Npwn5zVNZX-hrYAMFVtlGcPOT9go7QWy_otVBwG_j2n5zNfnoivUBS9JnSPAKqo_hwp2D-1aN1x1LFMP_1gkSY6kZ3bziwzTiOYs31MoKM0f7K469MAKvyc5AcFBgw8-97FDQuzgUyWPmnM9hnNmTbF20dstQOxEpm-MEA=",
    "_s_tentry": "-",
    "Apache": "3269131471157.1196.1752390870097",
    "SINAGLOBAL": "3269131471157.1196.1752390870097",
    "ULV": "1752390870180:1:1:1:3269131471157.1196.1752390870097:"
}

# 微博时间格式转化
def convert_weibo_time(weibo_time_str):
    dt = datetime.strptime(weibo_time_str, '%a %b %d %H:%M:%S %z %Y')
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# 微博数据提取与打印
def fetch_weibo_posts(params):
    try:
        response = requests.get(url, headers=headers, cookies=cookies, params=params)
        data = response.json()
        if data.get('ok') == 1 and 'cards' in data.get('data', {}):
            for card in data['data']['cards']:
                if 'mblog' not in card:
                    continue
                mblog = card['mblog']

                # 提取并转换时间
                raw_time = mblog.get('created_at', '')
                standard_time = convert_weibo_time(raw_time)

                # 提取标题
                text = mblog.get('text', '')
                title = text.split('】')[0].split('【')[-1] if '【' in text and '】' in text else text[:20]
                if "<a" in title:
                    title = ''.join(re.findall(r'[\u4e00-\u9fff]+|#|，', title))

                # 提取视频链接（如有）
                video_url = ""
                if 'page_info' in mblog:
                    page_info = mblog['page_info']
                    if 'url_struct' in mblog and len(mblog['url_struct']) > 0:
                        video_url = mblog['url_struct'][0].get('h5_target_url', '')
                    elif 'media_info' in page_info:
                        video_url = page_info['media_info'].get('h5_url', '')
                    if not video_url:
                        video_url = page_info.get('page_url', '')

                # 按要求格式输出
                print(f"{standard_time[:10]} {title} {video_url}")
        else:
            print("未找到微博数据或数据格式不符")
    except Exception as e:
        print(f"无法获得数据与信息: {e}")

# 主函数
max_page = 2
for i in range(1, max_page + 1):
    params = {
        "uid": "3858832626",  # 南海之声微博 UID
        "page": str(i),
        "feature": "0"
    }
    fetch_weibo_posts(params)
    sleep(1)  # 可选：防止请求过快
