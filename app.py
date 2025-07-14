# app.py
import streamlit as st
import subprocess
import sys
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="舆情信息查询平台", layout="centered")
st.title("📅 海事舆情每日监测平台")

# 日期输入
date = st.date_input("请选择查询日期：")
date_str = date.strftime("%Y-%m-%d")

if st.button("🔍 查询"):
    with st.spinner("正在运行爬虫，请稍候..."):
        result = subprocess.run(
            [sys.executable, "run.py", "-d", date_str],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8"
        )
        st.text(result.stdout)

    csv_path = f"results_{date_str}.csv"
    if Path(csv_path).exists():
        df = pd.read_csv(csv_path)
        st.success(f"查询成功，共 {len(df)} 条记录：")
        st.dataframe(df)
        st.download_button("📥 下载 CSV", df.to_csv(index=False), file_name=csv_path)
    else:
        st.warning("未找到结果文件，可能没有该日期的数据。")



