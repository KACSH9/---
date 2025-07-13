#!/usr/bin/env python3
# P3.py — 抓取 WTO 时事新闻并统一日期格式为 YYYY-MM-DD（去除时间部分）

import requests
import re

def fetch_wto_news():
    url = "https://www.wto.org/library/news/current_news_e.js"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"[ERROR] 无法下载 WTO JS ({resp.status_code})")
        return

    resp.encoding = "utf-8"
    js_text = resp.text

    # 匹配所有 news_item 块
    blocks = re.findall(r'news_item\[\d+\]\s*=\s*{(.*?)};', js_text, re.DOTALL)
    if not blocks:
        print("[WARN] 未从 WTO JS 中解析到任何 news_item 块")
        return

    # 月份缩写映射
    mon_map = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
        "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }

    for blk in blocks:
        m_date = re.search(r'ni_date\s*:\s*"(.+?)"', blk)
        m_head = re.search(r'ni_head\s*:\s*"(.*?)"',    blk)
        m_url  = re.search(r'nl_url\s*:\s*"(.*?)"',     blk)

        if not (m_date and m_head and m_url):
            continue

        raw = m_date.group(1)  # 可能含日期和时间，如 "07_Jul_2025_17_00_00"、"2025.07.07.17.00.00"
        # 统一所有非字母数字的分隔符为下划线
        norm = re.sub(r'[^0-9A-Za-z]+', '_', raw).strip('_')
        parts = norm.split('_')

        # 只保留前 3 个部分作为日期，丢弃时间
        date_parts = parts[:3]

        # 转成 YYYY-MM-DD
        if len(date_parts) == 3:
            # 如果是 YYYY_MM_DD
            if date_parts[0].isdigit() and date_parts[1].isdigit():
                y, m, d = date_parts
            # 否则当作 DD_MMM_YYYY
            else:
                d, mon_abbr, y = date_parts
                m = mon_map.get(mon_abbr, "01")
            date_str = f"{y.zfill(4)}-{m.zfill(2)}-{d.zfill(2)}"
        else:
            # 回退：仅用下划线替换为中划线
            date_str = "_".join(date_parts).replace('_', '-')

        title = m_head.group(1)
        link  = "https://www.wto.org" + m_url.group(1)

        print(f"{date_str}  {title}  {link}")


if __name__ == "__main__":
    fetch_wto_news()

