# -*- coding: utf-8 -*-
from lxml import etree
import requests
import re
from urllib.parse import urljoin

# 正则匹配：括号中的日期格式（YYYY-MM-DD）
date_pattern = re.compile(r'（(\d{4}-\d{2}-\d{2})）')

# 是否打印一级标题
printed_main_title = False

# ---------------------- 含有明显日期 ----------------------
def extract_simple_section(section_title, url, xpath_expr):
    global printed_main_title
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    html = etree.HTML(resp.text)
    links = html.xpath(xpath_expr)

    if not printed_main_title:
        print('-------------------------------------外交部新闻-------------------------------------')
        printed_main_title = True

    print(f"\n{section_title}")

    for a in links:
        text = a.xpath('string(.)').strip()
        href = a.xpath('./@href')[0]
        full_url = urljoin(url, href)

        date_match = date_pattern.search(text)
        time = date_match.group(1) if date_match else ''
        title = date_pattern.sub('', text).strip()

        print(time, title, full_url)

# ---------------------- 详情页中提取时间 ----------------------
def extract_detail_time_section(section_title, url, xpath_expr):
    global printed_main_title
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    html = etree.HTML(resp.text)
    links = html.xpath(xpath_expr)

    if not printed_main_title:
        print('-------------------------------------外交部新闻-------------------------------------')
        printed_main_title = True

    print(f"\n{section_title}")

    for a in links:
        title = a.xpath('string(.)').strip()
        href = a.xpath('./@href')[0]
        full_url = urljoin(url, href)

        try:
            detail_resp = requests.get(full_url)
            detail_resp.encoding = 'utf-8'
            detail_html = etree.HTML(detail_resp.text)
            time = detail_html.xpath('string(//meta[@name="PubDate"]/@content)').strip()
        except Exception as e:
            time = ''

        print(time, title, full_url)

# ---------------------- 讲话全文 / 声明公报 ----------------------
def extract_rightbox_list(section_title, url):
    global printed_main_title
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    html = etree.HTML(resp.text)
    items = html.xpath('//div[@class="rightbox"]//li')

    if not printed_main_title:
        print('-------------------------------------外交部新闻-------------------------------------')
        printed_main_title = True

    print(f"\n{section_title}")

    for i in items:
        title = i.xpath('string(.//a)').strip()
        href = i.xpath('.//a/@href')
        full_url = urljoin(url, href[0]) if href else ''

        pub_date = ''
        if full_url:
            try:
                detail_resp = requests.get(full_url)
                detail_resp.encoding = 'utf-8'
                detail_tree = etree.HTML(detail_resp.text)
                pub_date = detail_tree.xpath('string(//meta[@name="PubDate"]/@content)').strip()
            except:
                pass

        print(pub_date, title, full_url)

# ---------------------- 开始抓取 ----------------------

# 含有明显日期（括号）者：用 extract_simple_section
extract_simple_section('重要新闻', 'https://www.fmprc.gov.cn/zyxw/', '//ul[@class="list1"][1]/li/a | //ul[@class="list1"][2]/li/a')
extract_simple_section('外交部长活动', 'https://www.fmprc.gov.cn/wjbzhd/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('外交部新闻', 'https://www.fmprc.gov.cn/wjbxw_new/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('领导人活动', 'https://www.fmprc.gov.cn/wjdt_674879/gjldrhd_674881/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('外事日程', 'https://www.fmprc.gov.cn/wjdt_674879/wsrc_674883/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('部领导活动', 'https://www.fmprc.gov.cn/wjdt_674879/wjbxw_674885/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('业务动态', 'https://www.fmprc.gov.cn/wjdt_674879/sjxw_674887/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('吹风会', 'https://www.fmprc.gov.cn/wjdt_674879/cfhsl_674891/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('大使任免', 'https://www.fmprc.gov.cn/wjdt_674879/dsrm_674893/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('驻外报道', 'https://www.fmprc.gov.cn/wjdt_674879/zwbd_674895/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('政策解读', 'https://www.fmprc.gov.cn/wjdt_674879/zcjd/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('外事活动', 'https://www.fmprc.gov.cn/zwbd_673032/wshd_673034/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('公众活动', 'https://www.fmprc.gov.cn/zwbd_673032/gzhd_673042/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('外交之声', 'https://www.fmprc.gov.cn/zwbd_673032/wjzs/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('外交掠影', 'https://www.fmprc.gov.cn/zwbd_673032/ywfc_673029/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('文化交流', 'https://www.fmprc.gov.cn/zwbd_673032/whjl/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('侨务中资机构活动', 'https://www.fmprc.gov.cn/zwbd_673032/jghd_673046/', '//ul[@class="list1"][1]/li/a')

# 需要进详情页取时间者
extract_detail_time_section('发言人表态', 'https://www.fmprc.gov.cn/fyrbt_673021/', '//ul[@class="list1 list1-1"][1]/li[not(@style)]/a | //ul[@class="list1 list1-1"][2]/li[not(@style)]/a')

# 特殊结构：rightbox 列表页
extract_rightbox_list('讲话全文', 'https://www.mfa.gov.cn/web/ziliao_674904/zyjh_674906/')
extract_rightbox_list('声明公报', 'https://www.mfa.gov.cn/web/ziliao_674904/1179_674909/')
