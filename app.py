# app.py
import streamlit as st
import sys
import pandas as pd
from pathlib import Path
import run  # 假设 run.py 同一目录下，且定义了 fetch_data()

# 基础路径
BASE_DIR = Path(__file__).parent

st.set_page_config(page_title="舆情信息查询平台", layout="centered")
st.title("📅 海事舆情每日监测平台")

# 日期输入
date = st.date_input("请选择查询日期：")
date_str = date.strftime("%Y-%m-%d")

if st.button("🔍 查询"):
    # 调试目录
    st.write("当前目录文件：", [p.name for p in BASE_DIR.iterdir()])

    # 调用 run.fetch_data
    try:
        data = run.fetch_data(date_str)
    except Exception as e:
        st.error(f"运行爬虫时出错：{e}")
        st.stop()

    if not data:
        st.warning("未获取到任何数据。")
    else:
        df = pd.DataFrame(data)
        st.success(f"查询成功，共 {len(df)} 条记录：")
        st.dataframe(df)
        st.download_button("📥 下载 CSV", df.to_csv(index=False), file_name=f"results_{date_str}.csv")



