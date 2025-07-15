# 海事服务网
import requests
import csv
from datetime import datetime

# URL
page_url = "https://www.cnss.com.cn/api/content/list.jspx"  # 镜像网址

# 伪装请求头
headers = {
    'Host': 'www.cnss.com.cn',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.cnss.com.cn/html/currentevents/',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'If-None-Match': 'W/"68125-1752478320112"',
    'If-Modified-Since': 'Mon, 14 Jul 2025 07:32:00 GMT'
}

page_data = {
    "channelIds": 11,  # 目前来看，没啥用
    "first": 1,  # 从第几条数据开始请求
    "count": 50,  # 请求多少条数据
}

def find_page():
    resp = requests.post(page_url, headers=headers, data=page_data)
    resp.raise_for_status()
    return resp.json()  # 返回数据


def get_news(news_list):
    data_list = []  # 用于存储汇总数据
    for item in news_list:
        title = item["title"].strip()
        description = item["description"].strip()
        link = f"https://www.cnss.com.cn{item['url']}"
        date = datetime.strptime(item["releaseDate"][:10], "%Y-%m-%d").strftime("%Y-%m-%d")

        # ✅ 改成你需要的格式输出
        print(f"{date}  {title}  {link}")

        data_list.append({
            "标题": title,
            "内容简介": description,
            "网站URL": link,
            "发布时间": date
        })
    return data_list


def save_csv(data, filename='海事服务网_基础网页.csv'):
    with open(filename, mode="w", newline="", encoding="utf_8_sig") as f:
        writer = csv.DictWriter(f, fieldnames=["标题", "内容简介", "网站URL", "发布时间"])
        writer.writeheader()
        writer.writerows(data)
    print(f"数据已保存到 {filename}")

# 执行函数
data_source = find_page()
news = get_news(data_source)
save_csv(news)
print(f"共获得 {len(news)} 条数据")


