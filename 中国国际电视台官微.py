# 中国国际电视台官微（CGTN）数据爬取
import requests
from time import sleep
from datetime import datetime
import re

# 目标微博用户API地址（第一页起始）
url = 'https://m.weibo.cn/api/container/getIndex?containerid=1076033173633817'

# 请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
    "accept": "application/json, text/plain, */*",
    "referer": "https://m.weibo.cn/u/3173633817",
    "x-requested-with": "XMLHttpRequest"
}

# 登录后获取的 Cookie，保持会话
cookies = {
    "SUB": "_2AkMfL9rFf8NxqwFRmvkcxWPmaYl2wgvEieKpcyseJRMxHRl-yT9kqhUCtRB6NK_0Kqsr4wZsn2N_E_F5tcTDyZzhIf-H",
    "SUBP": "0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFNBEyfW18Aqs9jWueGKD-9",
    "XSRF-TOKEN": "Tevhi3ETVUbpzsgEqRryyrjk",
    "WBPSESS": "LKUy5Npwn5zVNZX-hrYAMFVtlGcPOT9go7QWy_otVBwG_j2n5zNfnoivUBS9JnSPAKqo_hwp2D-1aN1x1LFMP_1gkSY6kZ3bziwzTiOYs31MoKM0f7K469MAKvyc5AcFBgw8-97FDQuzgUyWPmnM9hnNmTbF20dstQOxEpm-MEA="
}

# 时间格式转化
def convert_weibo_time(weibo_time_str):
    dt = datetime.strptime(weibo_time_str, '%a %b %d %H:%M:%S %z %Y')
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# 主体爬取逻辑
def fetch_weibo_posts(params):
    try:
        response = requests.get(url, headers=headers, cookies=cookies, params=params)
        data = response.json()
        if data.get('ok') == 1 and 'cards' in data.get('data', {}):
            for card in data['data']['cards']:
                if 'mblog' not in card:
                    continue
                mblog = card['mblog']
                raw_time = mblog.get('created_at', '')
                standard_time = convert_weibo_time(raw_time)
                text = mblog.get('text', '')
                title = text.split('】')[0].split('【')[-1] if '【' in text and '】' in text else text[:20]
                if "<a" in title:
                    title = ''.join(re.findall(r'[\u4e00-\u9fff]+|#|，', title))

                video_url = ""
                if 'page_info' in mblog:
                    page_info = mblog['page_info']
                    if 'url_struct' in mblog and len(mblog['url_struct']) > 0:
                        video_url = mblog['url_struct'][0].get('h5_target_url', '')
                    elif 'media_info' in page_info:
                        video_url = page_info['media_info'].get('h5_url', '')
                    if not video_url:
                        video_url = page_info.get('page_url', '')

                # 输出格式：xxxx-xx-xx 标题 链接
                print(f"{standard_time[:10]} {title} {video_url}")
        else:
            print("未找到微博数据或数据格式不符")
    except Exception as e:
        print(f"无法获得数据与信息: {e}")

# 执行入口：翻页爬取
max_page = 2  # 微博未登录状态最多2页
for i in range(1, max_page + 1):
    params = {
        "uid": "3173633817",
        "page": str(i),
        "feature": "0"
    }
    fetch_weibo_posts(params)
    sleep(1)  # 可选：控制访问频率