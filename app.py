import streamlit as st
import subprocess
import sys
import pandas as pd
import datetime

st.set_page_config(page_title="海事舆情每日监测平台", page_icon="📅")
st.title("📅 海事舆情每日监测平台")

date_input = st.text_input("请选择查询日期：", value=str(datetime.date.today()))

if st.button("🔍 查询"):
    date_str = date_input.strip()
    command = [sys.executable, "run.py", "--date", date_str]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')

    if result.returncode != 0:
        st.error(f"运行失败：{result.stderr}")
    else:
        lines = [l for l in result.stdout.splitlines() if "▶" in l]
        data = []
        for l in lines:
            script, rest = l.split("▶", 1)
            title, link = rest.strip().rsplit(" ", 1)
            data.append((script.strip(), title.strip(), link.strip()))
        df = pd.DataFrame(data, columns=["script","title","link"])
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 下载 CSV", df.to_csv(index=False).encode(), file_name=f"results_{date_str}.csv")
